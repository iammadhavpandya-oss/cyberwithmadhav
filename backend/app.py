"""CyberWithMadhav optional backend: newsletter signup + contact form.

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
        "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500",
    ).split(",")
    if o.strip()
}
RATE_LIMIT = int(os.environ.get("CWM_RATE_LIMIT", "5"))          # requests ...
RATE_WINDOW = int(os.environ.get("CWM_RATE_WINDOW", "600"))      # ... per N seconds, per IP per endpoint
TRUST_PROXY = os.environ.get("CWM_TRUST_PROXY", "0") == "1"      # set to 1 only behind a reverse proxy

EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")
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


def rate_limited(key: str) -> bool:
    now = time.monotonic()
    bucket_key = (request.remote_addr or "unknown", key)
    with _lock:
        q = _hits[bucket_key]
        while q and now - q[0] > RATE_WINDOW:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            return True
        q.append(now)
        return False


# ---------------------------------------------------------------- CORS + headers
@app.after_request
def add_headers(resp):
    origin = (request.headers.get("Origin") or "").rstrip("/")
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Max-Age"] = "600"
        resp.headers["Vary"] = "Origin"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Cache-Control"] = "no-store"
    return resp


def error(msg: str, code: int = 400):
    return jsonify(ok=False, error=msg), code


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
    return 3 <= len(email) <= 254 and bool(EMAIL_RE.match(email))


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
    if rate_limited("subscribe"):
        return error("Too many requests. Please try again later.", 429)
    # Honeypot: humans never see the 'website' field. Pretend success, store nothing.
    if clean(data.get("website"), 200):
        return jsonify(ok=True, message="Thanks for subscribing!"), 200
    email = clean(data.get("email"), 254).lower()
    if not valid_email(email):
        return error("Please enter a valid email address.")
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
    if rate_limited("contact"):
        return error("Too many requests. Please try again later.", 429)
    if clean(data.get("website"), 200):
        return jsonify(ok=True, message="Thanks! Your message has been received."), 200
    name = clean(data.get("name"), 80)
    email = clean(data.get("email"), 254).lower()
    message = clean(data.get("message"), 2000)
    if not (1 <= len(name) <= 80):
        return error("Name is required (max 80 characters).")
    if not valid_email(email):
        return error("Please enter a valid email address.")
    if not (10 <= len(message) <= 2000):
        return error("Message must be 10–2000 characters.")
    db = get_db()
    db.execute("INSERT INTO messages (name, email, message, ip) VALUES (?, ?, ?, ?)",
               (name, email, message, request.remote_addr))
    db.commit()
    return jsonify(ok=True, message="Thanks! Your message has been received."), 201


init_db()

if __name__ == "__main__":
    # Development server only. Use gunicorn (see README) in production.
    app.run(host=os.environ.get("CWM_HOST", "127.0.0.1"), port=int(os.environ.get("CWM_PORT", "5000")), debug=False)
