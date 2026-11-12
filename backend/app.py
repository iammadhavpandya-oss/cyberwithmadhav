"""CyberWithMadhav optional backend: newsletter signup, contact form and the CTF API.

Stores submissions in SQLite. Features: input validation, per-IP rate limiting,
honeypot spam trap, CORS restricted to an allow-list (localhost by default),
request-size limit and basic security headers. No secrets are hardcoded:
everything is configured through environment variables (see .env.example).
"""
from __future__ import annotations

import os
import re
import sqlite3
import threading
import time
from collections import defaultdict, deque
from pathlib import Path

from flask import Flask, g, jsonify, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("CWM_DB_PATH", BASE_DIR / "cwm.sqlite3"))
ALLOWED_ORIGINS = {
    o.strip().rstrip("/")
    for o in os.environ.get(
        "CWM_ALLOWED_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500,"
        "https://www.cyberwithmadhav.com,https://cyberwithmadhav.com,https://iammadhavpandya-oss.github.io",
    ).split(",")
    if o.strip()
}
RATE_LIMIT = int(os.environ.get("CWM_RATE_LIMIT", "5"))          # requests ...
RATE_WINDOW = int(os.environ.get("CWM_RATE_WINDOW", "600"))      # ... per N seconds, per IP per endpoint
TRUST_PROXY = os.environ.get("CWM_TRUST_PROXY", "0") == "1"      # set to 1 only behind a reverse proxy

EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")
URL_RE = re.compile(r"(?:https?://|www\.)", re.IGNORECASE)
CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024  # 16 KB is plenty for these forms

if TRUST_PROXY:
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)


# ---------------------------------------------------------------- database
SCHEMA = """
CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    ip TEXT
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    ip TEXT
);
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)


# ---------------------------------------------------------------- rate limiting (in-memory, single process)
_hits: dict[tuple[str, str], deque] = defaultdict(deque)
_lock = threading.Lock()
_last_sweep = 0.0
MAX_BUCKETS = 10_000  # hard cap so a flood of spoofed IPs cannot grow memory without bound
MAX_WINDOW = max(RATE_WINDOW, 3600)  # longest window any caller uses (the CTF uses up to 1 hour)


def _sweep(now: float) -> None:
    """Drop buckets whose newest hit is outside the window (called under _lock)."""
    global _last_sweep
    if now - _last_sweep < 60 and len(_hits) < MAX_BUCKETS:
        return
    _last_sweep = now
    for k in [k for k, q in _hits.items() if not q or now - q[-1] > MAX_WINDOW]:
        del _hits[k]
    if len(_hits) >= MAX_BUCKETS:  # still full: drop the oldest half
        for k in sorted(_hits, key=lambda k: _hits[k][-1])[: len(_hits) // 2]:
            del _hits[k]


def rate_limited(key: str, limit: int | None = None, window: int | None = None, who: str | None = None) -> int:
    """Return 0 if allowed, else the number of seconds until the next request is allowed.

    Buckets are per (who, key); `who` defaults to the client IP. `limit`/`window`
    default to CWM_RATE_LIMIT / CWM_RATE_WINDOW.
    """
    limit = RATE_LIMIT if limit is None else limit
    window = min(RATE_WINDOW if window is None else window, MAX_WINDOW)
    now = time.monotonic()
    bucket_key = (who or request.remote_addr or "unknown", key)
    with _lock:
        _sweep(now)
        q = _hits[bucket_key]
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= limit:
            return max(1, int(window - (now - q[0])) + 1)
        q.append(now)
        return 0


# ---------------------------------------------------------------- CORS + headers
@app.after_request
def add_headers(resp):
    origin = (request.headers.get("Origin") or "").rstrip("/")
    allowed = CTF_ORIGINS if request.blueprint == "ctf" else ALLOWED_ORIGINS
    if origin in allowed:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp.headers["Access-Control-Max-Age"] = "600"
        resp.headers["Access-Control-Expose-Headers"] = "Retry-After"
        resp.headers["Vary"] = "Origin"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    resp.headers["Permissions-Policy"] = "interest-cohort=()"
    resp.headers["Cross-Origin-Resource-Policy"] = "same-site"
    return resp


def error(msg: str, code: int = 400, field: str | None = None):
    body = {"ok": False, "error": msg}
    if field:
        body["field"] = field  # lets the frontend highlight the right input
    return jsonify(body), code


def too_many(retry_after: int):
    resp = jsonify(ok=False, error="Too many requests. Please try again later.")
    resp.status_code = 429
    resp.headers["Retry-After"] = str(retry_after)
    return resp


@app.errorhandler(413)
def too_large(_e):
    return error("Request too large.", 413)


@app.errorhandler(404)
def not_found(_e):
    return error("Not found.", 404)


@app.errorhandler(405)
def bad_method(_e):
    return error("Method not allowed.", 405)


def read_json():
    origin = (request.headers.get("Origin") or "").rstrip("/")
    if origin and origin not in ALLOWED_ORIGINS:
        return None, error("Origin not allowed.", 403)
    if not request.is_json:
        return None, error("Content-Type must be application/json.", 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, error("Invalid JSON body.")
    return data, None


def clean(value, max_len: int) -> str:
    if not isinstance(value, str):
        return ""
    return CTRL_RE.sub("", value).strip()[:max_len + 1]


def valid_email(email: str) -> bool:
    if not (3 <= len(email) <= 254) or not EMAIL_RE.match(email):
        return False
    local = email.rsplit("@", 1)[0]
    return len(local) <= 64 and ".." not in email and not local.startswith(".") and not local.endswith(".")


# ---------------------------------------------------------------- routes
@app.get("/api/health")
def health():
    return jsonify(ok=True)


@app.route("/api/subscribe", methods=["POST", "OPTIONS"])
def subscribe():
    if request.method == "OPTIONS":
        return ("", 204)
    data, err = read_json()
    if err:
        return err
    wait = rate_limited("subscribe")
    if wait:
        return too_many(wait)
    # Honeypot: humans never see the 'website' field. Pretend success, store nothing.
    if clean(data.get("website"), 200):
        return jsonify(ok=True, message="Thanks for subscribing!"), 200
    email = clean(data.get("email"), 254).lower()
    if not valid_email(email):
        return error("Please enter a valid email address.", field="email")
    db = get_db()
    try:
        db.execute("INSERT INTO subscribers (email, ip) VALUES (?, ?)", (email, request.remote_addr))
        db.commit()
    except sqlite3.IntegrityError:
        # Don't reveal whether an email is already subscribed.
        pass
    return jsonify(ok=True, message="Thanks for subscribing!"), 201


@app.route("/api/contact", methods=["POST", "OPTIONS"])
def contact():
    if request.method == "OPTIONS":
        return ("", 204)
    data, err = read_json()
    if err:
        return err
    wait = rate_limited("contact")
    if wait:
        return too_many(wait)
    if clean(data.get("website"), 200):
        return jsonify(ok=True, message="Thanks! Your message has been received."), 200
    name = clean(data.get("name"), 80)
    email = clean(data.get("email"), 254).lower()
    message = clean(data.get("message"), 2000)
    if not (1 <= len(name) <= 80):
        return error("Name is required (max 80 characters).", field="name")
    if URL_RE.search(name):
        return error("Please enter just your name, without links.", field="name")
    if not valid_email(email):
        return error("Please enter a valid email address.", field="email")
    if not (10 <= len(message) <= 2000):
        return error("Message must be 10 to 2000 characters.", field="message")
    if len(URL_RE.findall(message)) > 3:
        return error("Please include at most 3 links.", field="message")
    db = get_db()
    db.execute("INSERT INTO messages (name, email, message, ip) VALUES (?, ?, ?, ?)",
               (name, email, message, request.remote_addr))
    db.commit()
    return jsonify(ok=True, message="Thanks! Your message has been received."), 201


init_db()

# CTF API (backend/ctf.py). It shares the database, rate limiter and helpers above.
try:
    from ctf import CTF_ORIGINS, init_ctf  # noqa: E402  (run from backend/)
except ImportError:  # imported as backend.app
    from .ctf import CTF_ORIGINS, init_ctf  # noqa: E402

init_ctf(app, get_db=get_db, rate_limited=rate_limited, error=error, too_many=too_many,
         read_json=read_json, clean=clean, db_path=DB_PATH)

if __name__ == "__main__":
    # Development server only. Use gunicorn (see README) in production.
    app.run(host=os.environ.get("CWM_HOST", "127.0.0.1"), port=int(os.environ.get("CWM_PORT", "5000")), debug=False)
