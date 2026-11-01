"""CyberWithMadhav CTF API (Flask blueprint, SQLite).

Plugged into app.py through init_ctf(). Routes:
  GET  /api/tracks                         track/level catalogue (+ your progress with a token)
  POST /api/auth/guest      {nick}          -> bearer token + one-time recovery code
  POST /api/auth/recover    {code}          -> new token + new recovery code
  GET  /api/me                              your score, XP, rank, streak, level progress
  POST /api/runs            {track, level, mode: ranked|free, relaxed}
  POST /api/challenges/<id>/hint   {run_id}
  POST /api/challenges/<id>/submit {run_id, answer}
  POST /api/runs/<id>/finish
  GET  /api/leaderboard?scope=overall|track|weekly|streak[&track=<id>]

Security notes
  * Answers are stored only as HMAC-SHA256(FLAG_PEPPER, "<cid>|<normalised answer>").
    Normalisation = NFKC, trim, collapse whitespace, lowercase (see normalise()).
  * Bearer tokens and recovery codes are random; only their SHA-256 is stored.
  * Artifact challenges get a per-user flag cwm{u<uidhex>_<hmac16>}; someone else's valid
    flag is logged as a flag_sharing security event (no auto-ban).
  * Elapsed time always comes from the server clock. Very fast correct answers are logged
    as too_fast events (no auto-ban).
  * 5 wrong answers on one challenge within 10 minutes lock it for the rest of that window
    (429 + Retry-After). Unknown run/challenge ids all return the same 404 body.
  * Request bodies over 4 KB are rejected. CORS is limited to CWM_CTF_ORIGINS
    (default: https://iammadhavpandya-oss.github.io).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import random
import re
import secrets
import sqlite3
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, g, jsonify, request

bp = Blueprint("ctf", __name__, url_prefix="/api")
H: dict = {}  # helpers injected by init_ctf (get_db, rate_limited, error, too_many, clean)

HERE = Path(__file__).resolve().parent
IMPORT_PATH = Path(os.environ.get("CWM_CTF_IMPORT", HERE / "ctf_import.private.json"))
CTF_ORIGINS = {
    o.strip().rstrip("/")
    for o in os.environ.get("CWM_CTF_ORIGINS", "https://iammadhavpandya-oss.github.io").split(",")
    if o.strip()
}
LOCK_AFTER = int(os.environ.get("CWM_CTF_LOCK_AFTER", "5"))
LOCK_SECONDS = int(os.environ.get("CWM_CTF_LOCK_SECONDS", "600"))
MAX_BODY = 4096
IST = 19800  # seconds east of UTC
NOT_FOUND = "Not found."

RESERVED = {"admin", "administrator", "root", "system", "sysadmin", "moderator", "mod", "staff", "support",
            "madhav", "madhavpandya", "cyberwithmadhav", "cwm", "official", "null", "undefined", "anonymous",
            "guest", "owner", "security", "help", "api"}
IMPERSONATE = ("admin", "madhav", "moderator", "official", "root", "staff")
PROFANITY = ("fuck", "shit", "bitch", "cunt", "dick", "pussy", "slut", "whore", "nigg", "fag", "rape",
             "chutiya", "madarchod", "behenchod", "bhenchod", "bhosd", "randi", "gaand", "lund", "harami")
NICK_RE = re.compile(r"[A-Za-z0-9_.-]{3,20}")
FLAG_RE = re.compile(r"cwm\{u([0-9a-f]{1,12})_([0-9a-f]{16})\}")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, nick TEXT NOT NULL UNIQUE COLLATE NOCASE,
  recovery_hash TEXT, hidden INTEGER NOT NULL DEFAULT 0, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL,
  created_at REAL NOT NULL, last_seen REAL NOT NULL);
CREATE TABLE IF NOT EXISTS challenges (id TEXT PRIMARY KEY, track TEXT NOT NULL, level TEXT NOT NULL,
  type TEXT NOT NULL, points INTEGER NOT NULL, max_attempts INTEGER NOT NULL, sort INTEGER NOT NULL,
  public_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS challenge_answers (challenge_id TEXT NOT NULL, digest TEXT NOT NULL,
  PRIMARY KEY (challenge_id, digest));
CREATE TABLE IF NOT EXISTS challenge_private (challenge_id TEXT PRIMARY KEY, explanation TEXT NOT NULL,
  hints_json TEXT NOT NULL, correct_option TEXT, correct_multi_json TEXT, dyn_json TEXT);
CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, track TEXT NOT NULL,
  level TEXT NOT NULL, mode TEXT NOT NULL, relaxed INTEGER NOT NULL, order_json TEXT NOT NULL,
  started_at REAL NOT NULL, last_event_at REAL NOT NULL, finished_at REAL, combo INTEGER NOT NULL DEFAULT 0,
  best_combo INTEGER NOT NULL DEFAULT 0, score INTEGER NOT NULL DEFAULT 0, xp INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS submissions (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL,
  challenge_id TEXT NOT NULL, run_id TEXT NOT NULL, digest TEXT NOT NULL, correct INTEGER NOT NULL,
  ip_hash TEXT, created_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS sub_user_ch ON submissions (user_id, challenge_id, created_at);
CREATE TABLE IF NOT EXISTS hints_used (user_id INTEGER NOT NULL, challenge_id TEXT NOT NULL, n INTEGER NOT NULL,
  created_at REAL NOT NULL, PRIMARY KEY (user_id, challenge_id, n));
CREATE TABLE IF NOT EXISTS solves (user_id INTEGER NOT NULL, challenge_id TEXT NOT NULL, points INTEGER NOT NULL,
  xp INTEGER NOT NULL, run_id TEXT NOT NULL, created_at REAL NOT NULL, PRIMARY KEY (user_id, challenge_id));
CREATE TABLE IF NOT EXISTS user_scores (user_id INTEGER PRIMARY KEY, score INTEGER NOT NULL DEFAULT 0,
  xp INTEGER NOT NULL DEFAULT 0, solves INTEGER NOT NULL DEFAULT 0, updated_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS track_scores (user_id INTEGER NOT NULL, track TEXT NOT NULL,
  score INTEGER NOT NULL DEFAULT 0, updated_at REAL NOT NULL, PRIMARY KEY (user_id, track));
CREATE TABLE IF NOT EXISTS weekly_scores (user_id INTEGER NOT NULL, week TEXT NOT NULL,
  score INTEGER NOT NULL DEFAULT 0, updated_at REAL NOT NULL, PRIMARY KEY (user_id, week));
CREATE TABLE IF NOT EXISTS user_streaks (user_id INTEGER PRIMARY KEY, current INTEGER NOT NULL DEFAULT 0,
  best INTEGER NOT NULL DEFAULT 0, last_day INTEGER, shields INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS security_events (id INTEGER PRIMARY KEY, user_id INTEGER, kind TEXT NOT NULL,
  detail TEXT, ip_hash TEXT, created_at REAL NOT NULL);
"""


# ------------------------------------------------------------------ crypto helpers
def _pepper() -> bytes:
    env = os.environ.get("FLAG_PEPPER")
    if env:
        return env.encode()
    # Dev fallback: a random pepper kept in a gitignored file next to this module.
    f = HERE / ".flag_pepper"
    if not f.exists():
        f.write_text(secrets.token_hex(32))
        print("WARNING: FLAG_PEPPER is not set; created backend/.flag_pepper for local development.")
    return f.read_text().strip().encode()


def _n1(s) -> str:
    s = unicodedata.normalize("NFKC", str(s)).strip()
    return re.sub(r"\s+", " ", s).lower()


def normalise(s, type_: str) -> str:
    """Must match tools/build_ctf.py and assets/js/ctf.js."""
    if type_ == "multi":
        return "|".join(sorted(_n1(p) for p in str(s).split("|") if _n1(p)))
    if type_ == "order":
        return "|".join(_n1(p) for p in str(s).split("|"))
    s = _n1(s)
    if type_ == "flag" and s and not s.startswith("cwm{"):
        s = "cwm{" + s.strip("{}") + "}"
    return s


def digest(cid: str, norm: str) -> str:
    return hmac.new(_pepper(), f"{cid}|{norm}".encode(), hashlib.sha256).hexdigest()


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def ip_hash() -> str:
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0].strip()
    return hmac.new(_pepper(), f"ip|{ip}".encode(), hashlib.sha256).hexdigest()[:32]


def user_flag(uid: int, cid: str) -> str:
    mac = hmac.new(_pepper(), f"flag|{uid}|{cid}".encode(), hashlib.sha256).hexdigest()[:16]
    return f"CWM{{u{uid:x}_{mac}}}"


def _b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def _rot13(s: str) -> str:
    return s.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                     "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"))


def encode_artifact(enc: str, flag: str) -> str:
    raw = flag.encode()
    if enc == "hex":
        return " ".join(f"{b:02x}" for b in raw)
    if enc == "basicauth":
        return _b64(b"cwm:" + raw)
    if enc == "rev":
        return flag[::-1]
    if enc == "b64rot13":
        return _rot13(_b64(raw))
    if enc == "rot13":
        return _rot13(flag)
    if enc == "b64":
        return _b64(raw)
    if enc == "jwt":
        u = lambda b: base64.urlsafe_b64encode(b).decode().rstrip("=")  # noqa: E731
        head = u(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
        body = u(json.dumps({"user": "guest", "role": "user", "flag": flag}, separators=(",", ":")).encode())
        return f"{head}.{body}.{u(b'this-is-a-lab-signature')}"
    if enc == "xor5a":
        return bytes(b ^ 0x5A for b in raw).hex()
    if enc == "ps":
        return _b64(f"Write-Output '{flag}'".encode("utf-16-le"))
    raise ValueError(enc)


# ------------------------------------------------------------------ setup / import
def init_ctf(app, **helpers):
    H.update(helpers)
    db_path = helpers["db_path"]
    con = sqlite3.connect(db_path)
    try:
        con.executescript(SCHEMA)
        con.commit()
        empty = con.execute("SELECT COUNT(*) FROM challenges").fetchone()[0] == 0
        if empty and IMPORT_PATH.exists() and os.environ.get("CWM_CTF_AUTO_IMPORT", "1") != "0":
            import_challenges(con, IMPORT_PATH)
    finally:
        con.close()
    app.register_blueprint(bp)


def import_challenges(con: sqlite3.Connection, path: Path) -> int:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    meta = {"scoring": data["scoring"], "tracks": data["tracks"], "levels": data["levels"]}
    con.execute("CREATE TABLE IF NOT EXISTS ctf_meta (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
    con.execute("INSERT OR REPLACE INTO ctf_meta VALUES ('meta', ?)", (json.dumps(meta),))
    ids = []
    for i, c in enumerate(data["challenges"]):
        ids.append(c["id"])
        con.execute("INSERT OR REPLACE INTO challenges VALUES (?,?,?,?,?,?,?,?)",
                    (c["id"], c["track"], c["level"], c["type"], c["points"], c["max_attempts"], i,
                     json.dumps(c["public"], ensure_ascii=False)))
        con.execute("DELETE FROM challenge_answers WHERE challenge_id = ?", (c["id"],))
        for a in c["answers"]:
            con.execute("INSERT OR IGNORE INTO challenge_answers VALUES (?,?)", (c["id"], digest(c["id"], a)))
        con.execute("INSERT OR REPLACE INTO challenge_private VALUES (?,?,?,?,?,?)",
                    (c["id"], c["explanation"], json.dumps(c["hints"], ensure_ascii=False), c.get("correct_option"),
                     json.dumps(c.get("correct_multi")) if c.get("correct_multi") else None,
                     json.dumps(c["dyn"]) if c.get("dyn") else None))
    if ids:
        q = ",".join("?" * len(ids))
        for t in ("challenge_answers", "challenge_private"):
            con.execute(f"DELETE FROM {t} WHERE challenge_id NOT IN ({q})", ids)
        con.execute(f"DELETE FROM challenges WHERE id NOT IN ({q})", ids)
    con.commit()
    return len(ids)


def _meta(db) -> dict:
    if "ctf_meta" not in g:
        row = db.execute("SELECT v FROM ctf_meta WHERE k = 'meta'").fetchone()
        g.ctf_meta = json.loads(row[0]) if row else {"scoring": {}, "tracks": [], "levels": []}
    return g.ctf_meta


# ------------------------------------------------------------------ request plumbing
def nf():
    return H["error"](NOT_FOUND, 404)


@bp.before_request
def _guard():
    if request.method == "OPTIONS":
        return ("", 204)
    if (request.content_length or 0) > MAX_BODY:
        return H["error"]("Request too large.", 413)
    origin = (request.headers.get("Origin") or "").rstrip("/")
    if origin and origin not in CTF_ORIGINS:
        return H["error"]("Origin not allowed.", 403)
    if request.method == "POST":
        if not request.is_json:
            return H["error"]("Content-Type must be application/json.", 415)
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return H["error"]("Invalid JSON body.")
        g.body = body
    retry = H["rate_limited"](f"ctf-ip:{request.remote_addr}", limit=120, window=60)
    if retry:
        return H["too_many"](retry)
    return None


def body() -> dict:
    return getattr(g, "body", {}) or {}


def current_user(db):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or len(auth) > 200:
        return None
    row = db.execute("SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ?",
                     (sha(auth[7:].strip()),)).fetchone()
    if row:
        db.execute("UPDATE sessions SET last_seen = ? WHERE token_hash = ?", (time.time(), sha(auth[7:].strip())))
    return row


def need_user(db):
    u = current_user(db)
    if not u:
        return None, H["error"]("Sign in first.", 401)
    return u, None


def event(db, uid, kind, detail):
    db.execute("INSERT INTO security_events (user_id, kind, detail, ip_hash, created_at) VALUES (?,?,?,?,?)",
               (uid, kind, json.dumps(detail)[:500], ip_hash(), time.time()))


def nick_problem(nick: str) -> str | None:
    if not NICK_RE.fullmatch(nick):
        return "Use 3 to 20 letters, numbers, dot, dash or underscore."
    low = nick.lower()
    squashed = re.sub(r"[^a-z]", "", low.replace("0", "o").replace("1", "i").replace("3", "e").replace("4", "a")
                      .replace("5", "s").replace("7", "t").replace("@", "a"))
    if low.strip("._-") in RESERVED or squashed in RESERVED or any(w in squashed for w in IMPERSONATE):
        return "That nickname is reserved."
    if any(p in squashed or p in low for p in PROFANITY):
        return "Please choose a friendlier nickname."
    return None


def rank_for(xp: int, scoring: dict) -> str:
    name = "Recruit"
    for need, title in scoring.get("ranks", [[0, "Recruit"]]):
        if xp >= need:
            name = title
    return name


def ist_day(ts: float) -> int:
    return int((ts + IST) // 86400)


def ist_week(ts: float) -> str:
    y, w, _ = datetime.fromtimestamp(ts + IST, tz=timezone.utc).isocalendar()
    return f"{y}-W{w:02d}"


def level_progress(db, uid: int) -> dict:
    """{track: {level: {"score": n, "max": m, "pct": p}}} from first solves."""
    out: dict = {}
    for r in db.execute("SELECT track, level, SUM(points) mx, COUNT(*) n FROM challenges GROUP BY track, level"):
        out.setdefault(r["track"], {})[r["level"]] = {"score": 0, "max": r["mx"], "count": r["n"], "pct": 0}
    if uid:
        for r in db.execute("SELECT c.track, c.level, SUM(s.points) sc FROM solves s JOIN challenges c "
                            "ON c.id = s.challenge_id WHERE s.user_id = ? GROUP BY c.track, c.level", (uid,)):
            cell = out[r["track"]][r["level"]]
            cell["score"] = r["sc"] or 0
            cell["pct"] = round(100 * cell["score"] / cell["max"]) if cell["max"] else 0
    return out


def unlocked(progress: dict, levels: list, track: str, level: str, scoring: dict) -> bool:
    order = [lv[0] for lv in levels]
    i = order.index(level)
    return i == 0 or progress.get(track, {}).get(order[i - 1], {}).get("pct", 0) >= scoring.get("unlockPercent", 60)


# ------------------------------------------------------------------ routes
@bp.get("/tracks")
def tracks():
    db = H["get_db"]()
    meta = _meta(db)
    u = current_user(db)
    prog = level_progress(db, u["id"] if u else 0)
    out = []
    for t in meta["tracks"]:
        lv = []
        for lid, lname, pts, soft in meta["levels"]:
            cell = prog.get(t["id"], {}).get(lid, {"score": 0, "max": 0, "count": 0, "pct": 0})
            lv.append({"id": lid, "name": lname, "points": pts, "softSeconds": soft, **cell,
                       "unlocked": unlocked(prog, meta["levels"], t["id"], lid, meta["scoring"])})
        out.append({**t, "levels": lv})
    db.commit()
    return jsonify(ok=True, scoring=meta["scoring"], tracks=out)


@bp.post("/auth/guest")
def guest():
    retry = H["rate_limited"](f"ctf-guest:{request.remote_addr}", limit=5, window=3600)
    if retry:
        return H["too_many"](retry)
    nick = str(body().get("nick", "")).strip()
    problem = nick_problem(nick)
    if problem:
        return H["error"](problem, 400, "nick")
    db = H["get_db"]()
    code = "-".join(secrets.token_hex(2).upper() for _ in range(4))
    try:
        cur = db.execute("INSERT INTO users (nick, recovery_hash, created_at) VALUES (?,?,?)",
                         (nick, sha(code.replace("-", "").lower()), time.time()))
    except sqlite3.IntegrityError:
        return H["error"]("That nickname is taken.", 409, "nick")
    token = secrets.token_urlsafe(32)
    db.execute("INSERT INTO sessions VALUES (?,?,?,?)", (sha(token), cur.lastrowid, time.time(), time.time()))
    db.commit()
    return jsonify(ok=True, token=token, recovery_code=code, user={"id": cur.lastrowid, "nick": nick}), 201


@bp.post("/auth/recover")
def recover():
    retry = H["rate_limited"](f"ctf-recover:{request.remote_addr}", limit=10, window=3600)
    if retry:
        return H["too_many"](retry)
    code = re.sub(r"[^0-9a-f]", "", str(body().get("code", "")).lower())[:32]
    db = H["get_db"]()
    row = db.execute("SELECT * FROM users WHERE recovery_hash = ?", (sha(code),)).fetchone() if len(code) == 16 else None
    if not row:
        return H["error"]("That recovery code is not valid.", 400, "code")
    new_code = "-".join(secrets.token_hex(2).upper() for _ in range(4))
    token = secrets.token_urlsafe(32)
    db.execute("UPDATE users SET recovery_hash = ? WHERE id = ?", (sha(new_code.replace("-", "").lower()), row["id"]))
    db.execute("DELETE FROM sessions WHERE user_id = ?", (row["id"],))
    db.execute("INSERT INTO sessions VALUES (?,?,?,?)", (sha(token), row["id"], time.time(), time.time()))
    db.commit()
    return jsonify(ok=True, token=token, recovery_code=new_code, user={"id": row["id"], "nick": row["nick"]})


@bp.get("/me")
def me():
    db = H["get_db"]()
    u, err = need_user(db)
    if err:
        return err
    meta = _meta(db)
    sc = db.execute("SELECT score, xp, solves FROM user_scores WHERE user_id = ?", (u["id"],)).fetchone()
    st = db.execute("SELECT current, best, shields FROM user_streaks WHERE user_id = ?", (u["id"],)).fetchone()
    xp = sc["xp"] if sc else 0
    db.commit()
    return jsonify(ok=True, user={"id": u["id"], "nick": u["nick"]}, score=sc["score"] if sc else 0, xp=xp,
                   solves=sc["solves"] if sc else 0, rank=rank_for(xp, meta["scoring"]),
                   streak=dict(st) if st else {"current": 0, "best": 0, "shields": 0},
                   progress=level_progress(db, u["id"]))


@bp.post("/runs")
def start_run():
    db = H["get_db"]()
    u, err = need_user(db)
    if err:
        return err
    retry = H["rate_limited"](f"ctf-runs:{u['id']}", limit=60, window=3600)
    if retry:
        return H["too_many"](retry)
    b = body()
    track, level = str(b.get("track", ""))[:20], str(b.get("level", ""))[:20]
    mode = "free" if b.get("mode") == "free" else "ranked"
    meta = _meta(db)
    rows = db.execute("SELECT * FROM challenges WHERE track = ? AND level = ? ORDER BY sort", (track, level)).fetchall()
    if not rows:
        return nf()
    if mode == "ranked" and not unlocked(level_progress(db, u["id"]), meta["levels"], track, level, meta["scoring"]):
        return H["error"](f"Locked. Score {meta['scoring'].get('unlockPercent', 60)}% on the previous level first, "
                          "or use Free roam.", 403)
    run_id = secrets.token_hex(12)
    rnd = random.Random(run_id)
    order = [r["id"] for r in rows]
    rnd.shuffle(order)
    by_id = {r["id"]: r for r in rows}
    items = []
    for cid in order:
        pub = json.loads(by_id[cid]["public_json"])
        if pub.get("options") and pub["type"] != "order":
            rnd.shuffle(pub["options"])
        if pub.get("dynamic"):
            dyn = json.loads(db.execute("SELECT dyn_json FROM challenge_private WHERE challenge_id = ?",
                                        (cid,)).fetchone()[0])
            pub["code"] = dyn["template"].replace("{x}", encode_artifact(dyn["enc"], user_flag(u["id"], cid)))
        pub["hintsUsed"] = db.execute("SELECT COUNT(*) FROM hints_used WHERE user_id = ? AND challenge_id = ?",
                                      (u["id"], cid)).fetchone()[0]
        pub["solved"] = bool(db.execute("SELECT 1 FROM solves WHERE user_id = ? AND challenge_id = ?",
                                        (u["id"], cid)).fetchone())
        items.append(pub)
    now = time.time()
    db.execute("INSERT INTO runs (id, user_id, track, level, mode, relaxed, order_json, started_at, last_event_at) "
               "VALUES (?,?,?,?,?,?,?,?,?)", (run_id, u["id"], track, level, mode, 1 if b.get("relaxed") else 0,
                                              json.dumps(order), now, now))
    db.commit()
    soft = next((lv[3] for lv in meta["levels"] if lv[0] == level), 60)
    return jsonify(ok=True, run={"id": run_id, "track": track, "level": level, "mode": mode,
                                 "relaxed": bool(b.get("relaxed")), "softSeconds": soft, "challenges": items}), 201


def _run_for(db, uid, run_id, cid=None):
    run = db.execute("SELECT * FROM runs WHERE id = ? AND user_id = ?", (str(run_id)[:40], uid)).fetchone()
    if not run or run["finished_at"]:
        return None, None
    if cid is not None and cid not in json.loads(run["order_json"]):
        return None, None
    ch = db.execute("SELECT * FROM challenges WHERE id = ?", (cid,)).fetchone() if cid else None
    return run, ch


@bp.post("/challenges/<cid>/hint")
def hint(cid):
    db = H["get_db"]()
    u, err = need_user(db)
    if err:
        return err
    run, ch = _run_for(db, u["id"], body().get("run_id", ""), cid[:20])
    if not ch:
        return nf()
    priv = db.execute("SELECT * FROM challenge_private WHERE challenge_id = ?", (cid,)).fetchone()
    hints = json.loads(priv["hints_json"])
    used = db.execute("SELECT COUNT(*) FROM hints_used WHERE user_id = ? AND challenge_id = ?", (u["id"], cid)).fetchone()[0]
    total = len(hints) or (1 if ch["type"] == "mcq" else 0)
    if used >= total:
        return H["error"]("No more hints for this one.", 409)
    db.execute("INSERT INTO hints_used VALUES (?,?,?,?)", (u["id"], cid, used + 1, time.time()))
    db.commit()
    out = {"ok": True, "n": used + 1, "of": total, "cost": [0.25, 0.5][min(used, 1)]}
    if hints:
        out["hint"] = hints[used]
    else:  # MCQ 50/50: remove two wrong options, chosen by the run seed
        pub = json.loads(ch["public_json"])
        wrong = [o for o in pub["options"] if o != priv["correct_option"]]
        random.Random(run["id"] + cid).shuffle(wrong)
        out["eliminate"] = wrong[:2]
        out["hint"] = "Two wrong options removed."
    return jsonify(out)


@bp.post("/challenges/<cid>/submit")
def submit(cid):
    db = H["get_db"]()
    u, err = need_user(db)
    if err:
        return err
    for key, limit in ((f"ctf-sub-ip:{request.remote_addr}", 30), (f"ctf-sub-u:{u['id']}", 20)):
        retry = H["rate_limited"](key, limit=limit, window=60)
        if retry:
            return H["too_many"](retry)
    b = body()
    run, ch = _run_for(db, u["id"], b.get("run_id", ""), cid[:20])
    if not ch:
        return nf()
    raw = b.get("answer", "")
    if isinstance(raw, list):
        raw = "|".join(str(x)[:200] for x in raw[:8])
    raw = str(raw)
    if not raw.strip() or len(raw) > 600:
        return H["error"]("Type an answer (up to 200 characters).", 400, "answer")
    now = time.time()
    since = now - LOCK_SECONDS
    recent_wrong = db.execute("SELECT created_at FROM submissions WHERE user_id = ? AND challenge_id = ? AND correct = 0 "
                              "AND created_at > ? ORDER BY created_at", (u["id"], cid, since)).fetchall()
    if len(recent_wrong) >= LOCK_AFTER:
        resp = H["too_many"](max(1, int(recent_wrong[-LOCK_AFTER]["created_at"] + LOCK_SECONDS - now)))
        resp.set_data(json.dumps({"ok": False, "error": "Too many wrong answers. This challenge is locked for a while.",
                                  "locked": True}))
        return resp
    in_run = db.execute("SELECT COUNT(*) n, SUM(correct) c FROM submissions WHERE run_id = ? AND challenge_id = ?",
                        (run["id"], cid)).fetchone()
    if in_run["c"]:
        return H["error"]("Already answered in this run.", 409)
    if in_run["n"] >= ch["max_attempts"]:
        return H["error"]("No attempts left for this question.", 409)

    norm = normalise(raw, ch["type"])
    d = digest(cid, norm)
    priv = db.execute("SELECT * FROM challenge_private WHERE challenge_id = ?", (cid,)).fetchone()
    if priv["dyn_json"]:
        correct = hmac.compare_digest(norm, normalise(user_flag(u["id"], cid), "flag"))
        m = FLAG_RE.fullmatch(norm)
        if not correct and m and int(m.group(1), 16) != u["id"]:
            other = int(m.group(1), 16)
            if hmac.compare_digest(norm, normalise(user_flag(other, cid), "flag")):
                event(db, u["id"], "flag_sharing", {"challenge": cid, "owner": other})
    else:
        correct = any(hmac.compare_digest(d, r[0]) for r in
                      db.execute("SELECT digest FROM challenge_answers WHERE challenge_id = ?", (cid,)))
    db.execute("INSERT INTO submissions (user_id, challenge_id, run_id, digest, correct, ip_hash, created_at) "
               "VALUES (?,?,?,?,?,?,?)", (u["id"], cid, run["id"], d, 1 if correct else 0, ip_hash(), now))
    attempt = in_run["n"] + 1
    left = ch["max_attempts"] - attempt
    meta = _meta(db)
    sc = meta["scoring"]
    out = {"ok": True, "correct": correct, "attempt": attempt, "attemptsLeft": 0 if correct else left,
           "points": 0, "xp": 0}
    elapsed = now - run["last_event_at"]
    if correct:
        if elapsed < (1.0 if ch["type"] == "mcq" else 2.0):
            event(db, u["id"], "too_fast", {"challenge": cid, "seconds": round(elapsed, 2)})
        hints = db.execute("SELECT COUNT(*) FROM hints_used WHERE user_id = ? AND challenge_id = ?",
                           (u["id"], cid)).fetchone()[0]
        wrong_ever = db.execute("SELECT COUNT(*) FROM submissions WHERE user_id = ? AND challenge_id = ? AND correct = 0",
                                (u["id"], cid)).fetchone()[0]
        points = earned_points(ch["points"], ch["type"], wrong_ever + 1, hints, sc)
        combo = run["combo"]
        soft = next((lv[3] for lv in meta["levels"] if lv[0] == ch["level"]), 60)
        bonus = 0 if run["relaxed"] else sc.get("timeBonusMax", 0.2) * max(0.0, 1 - elapsed / soft)
        mult = min(sc.get("streakCap", 1.5), 1 + sc.get("streakStep", 0.1) * combo)
        already = db.execute("SELECT 1 FROM solves WHERE user_id = ? AND challenge_id = ?", (u["id"], cid)).fetchone()
        run_pts = earned_points(ch["points"], ch["type"], attempt, hints, sc)  # this run's performance
        xp = round(run_pts * (1 + bonus) * mult)
        counted = run["mode"] == "ranked" and not already and points > 0
        if counted:  # leaderboard: first ranked solve only, lifetime attempts
            record_solve(db, u["id"], ch, points, xp, run["id"], now)
        else:
            xp = 0
            out["note"] = "Free roam" if run["mode"] == "free" else ("Already solved" if already else "No marks left")
        out.update(points=run_pts, xp=xp, counted=counted, scored=points if counted else 0)
        db.execute("UPDATE runs SET score = score + ?, xp = xp + ? WHERE id = ?", (run_pts, xp, run["id"]))
        db.execute("UPDATE runs SET combo = combo + 1, best_combo = MAX(best_combo, combo + 1), last_event_at = ? "
                   "WHERE id = ?", (now, run["id"]))
        out["combo"] = combo + 1
        out["timeBonus"] = round(bonus, 3)
        out["multiplier"] = round(mult, 2)
    else:
        db.execute("UPDATE runs SET combo = 0 WHERE id = ?", (run["id"],))
        out["combo"] = 0
        if left <= 0:
            db.execute("UPDATE runs SET last_event_at = ? WHERE id = ?", (now, run["id"]))
    if correct or left <= 0:
        out["explanation"] = priv["explanation"]
        if ch["type"] == "mcq":
            out["correctOption"] = priv["correct_option"]
        if ch["type"] == "multi" and priv["correct_multi_json"]:
            out["correctOptions"] = json.loads(priv["correct_multi_json"])
    db.commit()
    return jsonify(out)


def earned_points(base: int, type_: str, attempt: int, hints: int, sc: dict) -> int:
    """Marks for a correct answer on the given (lifetime) attempt number."""
    if type_ in ("mcq", "multi") and attempt > 1:
        return 0
    cost = sc.get("hintCost", [0.25, 0.5])
    p = base * (1 - (cost[min(hints, len(cost)) - 1] if hints else 0))
    start = sc.get("wrongPenaltyFromAttempt", 3)
    p -= sc.get("wrongPenalty", 2) * max(0, attempt - start + 1)
    return max(0, round(p))


def record_solve(db, uid, ch, points, xp, run_id, now):
    db.execute("INSERT INTO solves VALUES (?,?,?,?,?,?)", (uid, ch["id"], points, xp, run_id, now))
    db.execute("INSERT INTO user_scores (user_id, score, xp, solves, updated_at) VALUES (?,?,?,1,?) "
               "ON CONFLICT(user_id) DO UPDATE SET score = score + excluded.score, xp = xp + excluded.xp, "
               "solves = solves + 1, updated_at = excluded.updated_at", (uid, points, xp, now))
    db.execute("INSERT INTO track_scores VALUES (?,?,?,?) ON CONFLICT(user_id, track) DO UPDATE SET "
               "score = score + excluded.score, updated_at = excluded.updated_at", (uid, ch["track"], points, now))
    db.execute("INSERT INTO weekly_scores VALUES (?,?,?,?) ON CONFLICT(user_id, week) DO UPDATE SET "
               "score = score + excluded.score, updated_at = excluded.updated_at", (uid, ist_week(now), points, now))
    bump_streak(db, uid, now)


def bump_streak(db, uid, now):
    """IST-day streak. A shield is earned every 5 days (max 2) and covers one missed day."""
    day = ist_day(now)
    row = db.execute("SELECT * FROM user_streaks WHERE user_id = ?", (uid,)).fetchone()
    cur, best, last, shields = (row["current"], row["best"], row["last_day"], row["shields"]) if row else (0, 0, None, 0)
    if last == day:
        return
    if last is not None and day == last + 1:
        cur += 1
    elif last is not None and 0 < day - last - 1 <= shields:
        shields -= day - last - 1
        cur += 1
    else:
        cur = 1
    if cur % 5 == 0:
        shields = min(2, shields + 1)
    db.execute("INSERT OR REPLACE INTO user_streaks VALUES (?,?,?,?,?)", (uid, cur, max(best, cur), day, shields))


@bp.post("/runs/<run_id>/finish")
def finish(run_id):
    db = H["get_db"]()
    u, err = need_user(db)
    if err:
        return err
    run, _ = _run_for(db, u["id"], run_id)
    if not run:
        return nf()
    now = time.time()
    db.execute("UPDATE runs SET finished_at = ? WHERE id = ?", (now, run["id"]))
    order = json.loads(run["order_json"])
    q = ",".join("?" * len(order))
    max_pts = db.execute(f"SELECT SUM(points) FROM challenges WHERE id IN ({q})", order).fetchone()[0] or 0
    right = db.execute(f"SELECT COUNT(DISTINCT challenge_id) FROM submissions WHERE run_id = ? AND correct = 1",
                       (run["id"],)).fetchone()[0]
    meta = _meta(db)
    prog = level_progress(db, u["id"])
    lv_ids = [lv[0] for lv in meta["levels"]]
    i = lv_ids.index(run["level"])
    nxt = lv_ids[i + 1] if i + 1 < len(lv_ids) else None
    sc = db.execute("SELECT xp FROM user_scores WHERE user_id = ?", (u["id"],)).fetchone()
    db.commit()
    return jsonify(ok=True, run={"id": run["id"], "mode": run["mode"], "score": run["score"], "max": max_pts,
                                 "pct": round(100 * run["score"] / max_pts) if max_pts else 0, "xp": run["xp"],
                                 "correct": right, "questions": len(order), "bestCombo": run["best_combo"],
                                 "seconds": round(now - run["started_at"])},
                   level=prog[run["track"]][run["level"]],
                   nextUnlocked=bool(nxt) and unlocked(prog, meta["levels"], run["track"], nxt, meta["scoring"]),
                   rank=rank_for(sc["xp"] if sc else 0, meta["scoring"]))


@bp.get("/leaderboard")
def leaderboard():
    db = H["get_db"]()
    scope = request.args.get("scope", "overall")
    track = request.args.get("track", "")[:20]
    try:
        limit = max(1, min(50, int(request.args.get("limit", 20))))
    except ValueError:
        limit = 20
    if scope == "overall":
        sql, args = ("SELECT u.nick, s.score, s.xp, s.solves FROM user_scores s JOIN users u ON u.id = s.user_id "
                     "WHERE u.hidden = 0 AND s.score > 0 ORDER BY s.score DESC, s.updated_at ASC LIMIT ?", (limit,))
    elif scope == "track":
        if not db.execute("SELECT 1 FROM challenges WHERE track = ?", (track,)).fetchone():
            return nf()
        sql, args = ("SELECT u.nick, t.score FROM track_scores t JOIN users u ON u.id = t.user_id WHERE u.hidden = 0 "
                     "AND t.track = ? AND t.score > 0 ORDER BY t.score DESC, t.updated_at ASC LIMIT ?", (track, limit))
    elif scope == "weekly":
        sql, args = ("SELECT u.nick, w.score FROM weekly_scores w JOIN users u ON u.id = w.user_id WHERE u.hidden = 0 "
                     "AND w.week = ? AND w.score > 0 ORDER BY w.score DESC, w.updated_at ASC LIMIT ?",
                     (ist_week(time.time()), limit))
    elif scope == "streak":
        today = ist_day(time.time())
        sql, args = ("SELECT u.nick, s.current AS streak, s.best FROM user_streaks s JOIN users u ON u.id = s.user_id "
                     "WHERE u.hidden = 0 AND s.current > 0 AND s.last_day >= ? - 1 - s.shields "
                     "ORDER BY s.current DESC, s.best DESC LIMIT ?", (today, limit))
    else:
        return H["error"]("scope must be overall, track, weekly or streak.")
    rows = [dict(r) for r in db.execute(sql, args)]
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return jsonify(ok=True, scope=scope, week=ist_week(time.time()) if scope == "weekly" else None, rows=rows)
