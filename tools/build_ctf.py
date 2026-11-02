#!/usr/bin/env python3
"""Single CTF build: private answer key -> public static data + private server import.

    python3 tools/build_ctf.py            # build
    python3 tools/build_ctf.py --check    # validate only

Input  (private, gitignored): backend/ctf_answers.private.json
Output (public)             : data/ctf.json                 static practice data, hashed answers only
Output (private, gitignored): backend/ctf_import.private.json  read by `python manage.py import`
Output (public)             : backend/ctf_answers.example.json format sample with fake answers

Static answer check (data/ctf.json):
  dk = PBKDF2-HMAC-SHA256(password = normalised answer, salt = challenge salt (utf-8 hex string),
                          iterations = ITER, length = 64 bytes)
  verifier = hex(dk[0:32])  is published; dk[32:64] is the AES-256-GCM key for the explanation.
  So the explanation decrypts only after a correct answer, and nothing in the file is plaintext.
The server never uses these salts: it stores HMAC-SHA256(FLAG_PEPPER, id|answer) instead.
normalise() must match assets/js/ctf.js and backend/ctf.py.
"""
import base64, hashlib, json, os, random, re, sys, unicodedata
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:  # pragma: no cover
    sys.exit("build_ctf.py needs the 'cryptography' package (pip install cryptography)")

ROOT = Path(__file__).resolve().parent.parent
PRIVATE = ROOT / "backend" / "ctf_answers.private.json"
PUBLIC = ROOT / "data" / "ctf.json"
IMPORT = ROOT / "backend" / "ctf_import.private.json"
EXAMPLE = ROOT / "backend" / "ctf_answers.example.json"
ITER = 60000

TRACKS = [
    ("networking", "Networking", "IP, ports, subnets and packets", "\U0001F310"),
    ("linux", "Linux", "Shell, permissions and logs", "\U0001F427"),
    ("basics", "Basic IT Knowledge", "Bits, hardware, safe habits and scam spotting", "\U0001F4BB"),
    ("ccna", "CCNA", "Cisco IOS, routing and switching", "\U0001F5A7"),
    ("cloud", "Cloud Computing", "Shared responsibility, IAM and VPCs", "\u2601\uFE0F"),
    ("pentest", "Pentesting", "Ethical hacking basics, in a lab", "\U0001F5DD\uFE0F"),
    ("blueteam", "Blue Team", "Logs, alerts and incident response", "\U0001F6E1\uFE0F"),
]
LEVELS = [("beginner", "Beginner", 10, 45), ("intermediate", "Intermediate", 20, 75), ("expert", "Expert", 30, 120)]
TYPES = {"mcq", "multi", "order", "text", "flag"}
MAX_ATTEMPTS = {"mcq": 1, "multi": 1, "order": 3, "text": 5, "flag": 5}
SCORING = {
    "points": {l[0]: l[2] for l in LEVELS},
    "softSeconds": {l[0]: l[3] for l in LEVELS},
    "maxAttempts": MAX_ATTEMPTS,
    "wrongPenaltyFromAttempt": 3, "wrongPenalty": 2,       # -2 marks per attempt from the 3rd one on
    "hintCost": [0.25, 0.5],                               # 1 hint = -25%, 2 hints = -50%
    "unlockPercent": 60,
    "timeBonusMax": 0.2, "streakStep": 0.1, "streakCap": 1.5,
    "bands": {"low": [0, 39], "mid": [40, 74], "high": [75, 100]},
    "ranks": [[0, "Recruit"], [150, "Packet Scout"], [500, "Shell Walker"], [1100, "Analyst"],
              [1900, "Operator"], [2700, "Root"]],
}
DYN_ENCODERS = {"hex", "basicauth", "rev", "b64rot13", "rot13", "b64", "jwt", "xor5a", "ps"}


def _n1(s):
    s = unicodedata.normalize("NFKC", str(s)).strip()
    return re.sub(r"\s+", " ", s).lower()

_UNIT_RE = re.compile(r"^([0-9][0-9.]*) ?(?:bits?|hosts?|times|runs|secs?|seconds|s)$")


def _loose(s):
    """Typed answers: drop http(s)://, www. and a trailing slash, and a unit word after a number."""
    s = re.sub(r"^https?://", "", s)
    s = re.sub(r"^www\.", "", s)
    if " " not in s and len(s) > 1:
        s = s.rstrip("/")
    return _UNIT_RE.sub(r"\1", s)


def normalise(s, type_):
    if type_ == "multi":
        return "|".join(sorted(_n1(p) for p in str(s).split("|") if _n1(p)))
    if type_ == "order":
        return "|".join(_n1(p) for p in str(s).split("|"))
    s = _n1(s)
    if type_ == "flag" and s and not s.startswith("cwm{"):
        s = "cwm{" + s.strip("{}") + "}"
    elif type_ == "text":
        s = _loose(s)
    return s


def derive(salt, norm):
    return hashlib.pbkdf2_hmac("sha256", norm.encode("utf-8"), salt.encode("utf-8"), ITER, 64)


def encrypt(key, text):
    iv = os.urandom(12)
    ct = AESGCM(key).encrypt(iv, text.encode("utf-8"), None)
    return {"iv": base64.b64encode(iv).decode(), "ct": base64.b64encode(ct).decode()}


def validate(data):
    errs, seen = [], set()
    chs = data.get("challenges", [])
    for c in chs:
        cid = c.get("id", "?")
        if cid in seen:
            errs.append(f"{cid}: duplicate id")
        seen.add(cid)
        if not re.fullmatch(r"[a-z]{3}-[bie]\d{1,2}", cid):
            errs.append(f"{cid}: bad id")
        if c.get("track") not in {t[0] for t in TRACKS}:
            errs.append(f"{cid}: unknown track")
        if c.get("level") not in {l[0] for l in LEVELS}:
            errs.append(f"{cid}: unknown level")
        t = c.get("type")
        if t not in TYPES:
            errs.append(f"{cid}: unknown type")
        for k in ("title", "prompt", "explain"):
            if not c.get(k):
                errs.append(f"{cid}: missing {k}")
        ans = c.get("answers") or []
        if not ans:
            errs.append(f"{cid}: no answers")
        opts = c.get("options") or []
        if t in ("mcq", "multi", "order"):
            if len(opts) < 3:
                errs.append(f"{cid}: needs at least 3 options")
            if len({_n1(o) for o in opts}) != len(opts) or any("|" in o for o in opts):
                errs.append(f"{cid}: options collide or contain '|'")
        if t == "mcq" and ans and ans[0] not in opts:
            errs.append(f"{cid}: mcq answer must be an option")
        if t == "multi" and not set(c.get("correct") or []) <= set(opts):
            errs.append(f"{cid}: multi answers must be options")
        if t == "flag" and not re.fullmatch(r"CWM\{[A-Za-z0-9_]+\}", ans[0] if ans else ""):
            errs.append(f"{cid}: flag must look like CWM{{...}}")
        if c.get("dyn") and (c["dyn"].get("enc") not in DYN_ENCODERS or "{x}" not in c["dyn"].get("template", "")):
            errs.append(f"{cid}: bad dyn spec")
        if "\u2014" in json.dumps(c, ensure_ascii=False):
            errs.append(f"{cid}: contains an em dash")
        if t in ("text", "flag"):  # log puzzles legitimately contain the answer in their code block
            vis = " ".join(str(c.get(k) or "") for k in ("title", "prompt")).lower() + " ".join(c.get("hints") or []).lower()
            if any(len(a) > 4 and a.lower() in vis for a in ans):
                errs.append(f"{cid}: answer appears in visible text")
    for tr in TRACKS:
        for l in LEVELS:
            n = sum(1 for c in chs if c.get("track") == tr[0] and c.get("level") == l[0])
            if n < 5:
                errs.append(f"{tr[0]}/{l[0]}: only {n} challenges (need 5)")
    return errs


def shuffled(opts, cid, correct_order=None):
    rnd = random.Random(f"cwm-ctf:{cid}")
    out = list(opts)
    for _ in range(20):
        rnd.shuffle(out)
        if out != list(correct_order or []):
            break
    return out


def public_item(c):
    item = {"id": c["id"], "type": c["type"], "kind": c.get("kind") or c["type"], "title": c["title"],
            "prompt": c["prompt"], "points": SCORING["points"][c["level"]], "maxAttempts": MAX_ATTEMPTS[c["type"]],
            "hintCount": len(c.get("hints") or []) or (1 if c["type"] == "mcq" else 0)}
    if c.get("set"):
        item["set"] = c["set"]
    if c.get("code"):
        item["code"] = c["code"]
    if c.get("options"):
        item["options"] = shuffled(c["options"], c["id"], c["options"] if c["type"] == "order" else None)
    if c.get("dyn"):
        item["dynamic"] = True
    if c.get("placeholder"):
        item["placeholder"] = c["placeholder"]
    return item


def build(data):
    tracks, imp = [], []
    for tid, tname, blurb, icon in TRACKS:
        levels = []
        for lid, lname, pts, soft in LEVELS:
            items = []
            for c in [c for c in data["challenges"] if c["track"] == tid and c["level"] == lid]:
                norms = list(dict.fromkeys(normalise(a, c["type"]) for a in c["answers"]))
                salt = os.urandom(16).hex()
                item = public_item(c)
                item["salt"] = salt
                item["verifiers"], item["exp"] = [], []
                for n in norms:
                    dk = derive(salt, n)
                    item["verifiers"].append(dk[:32].hex())
                    item["exp"].append(encrypt(dk[32:], c["explain"]))
                if c.get("hints"):
                    item["hints"] = c["hints"]
                items.append(item)
                imp.append({"id": c["id"], "track": tid, "level": lid, "type": c["type"], "points": pts,
                            "max_attempts": MAX_ATTEMPTS[c["type"]], "public": public_item(c), "answers": norms,
                            "explanation": c["explain"], "hints": c.get("hints") or [],
                            "correct_option": c["answers"][0] if c["type"] == "mcq" else None,
                            "correct_multi": c.get("correct") if c["type"] == "multi" else None,
                            "dyn": c.get("dyn")})
            levels.append({"id": lid, "name": lname, "points": pts, "softSeconds": soft,
                           "maxPoints": pts * len(items), "challenges": items})
        tracks.append({"id": tid, "name": tname, "blurb": blurb, "icon": icon, "levels": levels})
    total = sum(l["maxPoints"] for t in tracks for l in t["levels"])
    pub = {"version": data.get("version", 1), "format": "cwm-ctf-2",
           "kdf": {"name": "PBKDF2", "hash": "SHA-256", "iterations": ITER, "bytes": 64,
                   "verifier": "hex(dk[0:32])", "aesKey": "dk[32:64]", "salt": "utf-8 of the salt string"},
           "scoring": {**SCORING, "totalPoints": total}, "tracks": tracks}
    meta = [{"id": t[0], "name": t[1], "blurb": t[2], "icon": t[3]} for t in TRACKS]
    return pub, {"version": 2, "scoring": SCORING, "tracks": meta, "levels": [list(l) for l in LEVELS], "challenges": imp}


def main():
    if not PRIVATE.exists():
        sys.exit(f"missing {PRIVATE}. It is private and gitignored; ask the maintainer for it.")
    data = json.loads(PRIVATE.read_text(encoding="utf-8"))
    errs = validate(data)
    if errs:
        sys.exit("CTF content errors:\n  " + "\n  ".join(errs))
    if "--check" in sys.argv:
        print(f"ok: {len(data['challenges'])} challenges")
        return
    pub, imp = build(data)
    text = json.dumps(pub, ensure_ascii=False, indent=1)
    low = text.lower()
    for c in data["challenges"]:  # leak checks: no plaintext flag or explanation in the public file
        if c["type"] == "flag" and c["answers"][0].lower() in low:
            sys.exit(f"leak check failed for {c['id']}")
        if c["explain"][:40] in text:
            sys.exit(f"explanation leak for {c['id']}")
    PUBLIC.write_text(text + "\n", encoding="utf-8")
    IMPORT.write_text(json.dumps(imp, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    sample = {"version": 1, "challenges": [
        {"id": "net-b1", "track": "networking", "level": "beginner", "type": "mcq", "kind": "mcq", "set": None,
         "title": "Example MCQ", "prompt": "Question text", "code": None, "options": ["A", "B", "C", "D"],
         "correct": None, "answers": ["B"], "explain": "Shown after a correct answer.", "hints": [], "dyn": None},
        {"id": "net-b5", "track": "networking", "level": "beginner", "type": "flag", "kind": "flag", "set": None,
         "title": "Example flag", "prompt": "Decode the hex.", "code": "43 57 4d 7b ... 7d", "options": None,
         "correct": None, "answers": ["CWM{example_flag}", "CWM{accepted_variant}"],
         "explain": "Shown after a correct answer.", "hints": ["Optional hint, costs 25% of the marks."],
         "dyn": {"enc": "hex", "template": "{x}"}}]}
    EXAMPLE.write_text(json.dumps(sample, indent=1) + "\n", encoding="utf-8")
    n = len(data["challenges"])
    print(f"wrote {PUBLIC.relative_to(ROOT)} and {IMPORT.relative_to(ROOT)}: {n} challenges, {pub['scoring']['totalPoints']} points")


if __name__ == "__main__":
    main()
