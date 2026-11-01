"""Flask test-client checks for the CTF API.  Run:  cd backend && .venv/bin/python -m unittest test_ctf -v

Needs backend/ctf_import.private.json (built by tools/build_ctf.py from the private answer key).
Uses a throwaway database and a test pepper.
"""
import json
import os
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

TMP = tempfile.mkdtemp()
os.environ["CWM_DB_PATH"] = str(Path(TMP) / "test.sqlite3")
os.environ["FLAG_PEPPER"] = "test-pepper-not-secret"
os.environ["CWM_CTF_ORIGINS"] = "https://iammadhavpandya-oss.github.io,http://localhost:8000"

import app as core  # noqa: E402
import ctf  # noqa: E402

IMP = json.loads(ctf.IMPORT_PATH.read_text(encoding="utf-8"))
KEY = {c["id"]: c for c in IMP["challenges"]}
ORIGIN = {"Origin": "http://localhost:8000"}
PRIVATE = json.loads((Path(__file__).parent / "ctf_answers.private.json").read_text(encoding="utf-8"))["challenges"]


def plain(cid):
    return next(c for c in PRIVATE if c["id"] == cid)


class Base(unittest.TestCase):
    n = 0

    def setUp(self):
        core._hits.clear()
        self.c = core.app.test_client()

    def db(self):
        con = sqlite3.connect(os.environ["CWM_DB_PATH"])
        self.addCleanup(con.close)
        return con

    def guest(self, nick=None):
        Base.n += 1
        r = self.c.post("/api/auth/guest", json={"nick": nick or f"tester{Base.n}"}, headers=ORIGIN)
        self.assertEqual(r.status_code, 201, r.json)
        core._hits.clear()
        return r.json

    def h(self, tok):
        return {**ORIGIN, "Authorization": f"Bearer {tok}"}

    def start(self, tok, track="networking", level="beginner", mode="ranked", relaxed=False):
        r = self.c.post("/api/runs", json={"track": track, "level": level, "mode": mode, "relaxed": relaxed},
                        headers=self.h(tok))
        return r

    def sub(self, tok, run_id, cid, ans):
        return self.c.post(f"/api/challenges/{cid}/submit", json={"run_id": run_id, "answer": ans}, headers=self.h(tok))

    def right(self, run_item):
        """Correct raw answer for a run item (uses the plaintext key; dyn flags come from the artifact)."""
        c = plain(run_item["id"])
        if c.get("dyn"):
            return None
        if c["type"] == "multi":
            return c["correct"]
        if c["type"] == "order":
            return c["options"]
        return c["answers"][0]


class Catalogue(Base):
    def test_health_and_tracks(self):
        self.assertEqual(self.c.get("/api/health").status_code, 200)
        r = self.c.get("/api/tracks")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json["tracks"]), 7)
        lv = r.json["tracks"][0]["levels"]
        self.assertEqual([x["unlocked"] for x in lv], [True, False, False])
        total = sum(x["max"] for t in r.json["tracks"] for x in t["levels"])
        self.assertEqual(total, 2220)

    def test_no_plaintext_in_db(self):
        con = self.db()
        dump = "\n".join(con.iterdump()).lower()
        for c in PRIVATE:
            if c["type"] == "flag":
                self.assertNotIn(c["answers"][0].lower(), dump, c["id"])
        row = con.execute("SELECT digest FROM challenge_answers LIMIT 1").fetchone()
        self.assertEqual(len(row[0]), 64)

    def test_hmac_uses_pepper(self):
        d = ctf.digest("net-b1", "network")
        os.environ["FLAG_PEPPER"] = "other"
        self.assertNotEqual(d, ctf.digest("net-b1", "network"))
        os.environ["FLAG_PEPPER"] = "test-pepper-not-secret"

    def test_normalise(self):
        self.assertEqual(ctf.normalise("  ＣＷＭ{Ping   Pong} ", "flag"), "cwm{ping pong}")
        self.assertEqual(ctf.normalise("ping_pong", "flag"), "cwm{ping_pong}")
        self.assertEqual(ctf.normalise("B|a| c", "multi"), "a|b|c")
        self.assertEqual(ctf.normalise("B|a", "order"), "b|a")


class Auth(Base):
    def test_nick_rules(self):
        for bad in ["ab", "a" * 21, "has space", "<script>", "admin", "SuperAdmin", "r00t", "Madhav_fan", "fuck_it"]:
            core._hits.clear()
            r = self.c.post("/api/auth/guest", json={"nick": bad}, headers=ORIGIN)
            self.assertEqual(r.status_code, 400, bad)
        self.guest("Neo_01")
        r = self.c.post("/api/auth/guest", json={"nick": "neo_01"}, headers=ORIGIN)
        self.assertEqual(r.status_code, 409)

    def test_token_and_recovery_hashed(self):
        g = self.guest()
        con = self.db()
        dump = "\n".join(con.iterdump())
        self.assertNotIn(g["token"], dump)
        self.assertNotIn(g["recovery_code"], dump)
        self.assertEqual(self.c.get("/api/me", headers=self.h(g["token"])).status_code, 200)
        self.assertEqual(self.c.get("/api/me", headers=self.h("nope")).status_code, 401)

    def test_recover_is_one_time(self):
        g = self.guest()
        r = self.c.post("/api/auth/recover", json={"code": g["recovery_code"]}, headers=ORIGIN)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json["user"]["nick"], g["user"]["nick"])
        self.assertEqual(self.c.get("/api/me", headers=self.h(g["token"])).status_code, 401)  # old session gone
        self.assertEqual(self.c.post("/api/auth/recover", json={"code": g["recovery_code"]},
                                     headers=ORIGIN).status_code, 400)

    def test_guest_rate_limit(self):
        codes = [self.c.post("/api/auth/guest", json={"nick": f"burst{i}"}, headers=ORIGIN).status_code for i in range(7)]
        self.assertIn(429, codes)


class Play(Base):
    def test_full_level_ranked_and_unlock(self):
        g = self.guest()
        tok = g["token"]
        self.assertEqual(self.start(tok, level="intermediate").status_code, 403)  # locked
        self.assertEqual(self.start(tok, level="intermediate", mode="free").status_code, 201)  # free roam ok
        r = self.start(tok)
        run = r.json["run"]
        self.assertEqual(run["softSeconds"], 45)
        total = 0
        for item in run["challenges"]:
            self.assertNotIn("salt", item)
            self.assertNotIn("verifiers", item)
            ans = self.right(item)
            if ans is None:  # dynamic flag: decode own artifact (hex)
                ans = bytes.fromhex(item["code"].replace(" ", "")).decode()
                self.assertTrue(ans.startswith(f"CWM{{u{g['user']['id']:x}_"))
            res = self.sub(tok, run["id"], item["id"], ans)
            self.assertTrue(res.json["correct"], item["id"])
            self.assertIn("explanation", res.json)
            self.assertTrue(res.json["counted"])
            total += res.json["scored"]
        self.assertEqual(total, sum(KEY[i["id"]]["points"] for i in run["challenges"]))
        fin = self.c.post(f"/api/runs/{run['id']}/finish", json={}, headers=self.h(tok)).json
        self.assertEqual(fin["run"]["pct"], 100)
        self.assertTrue(fin["nextUnlocked"])
        self.assertEqual(self.start(tok, level="intermediate").status_code, 201)
        me = self.c.get("/api/me", headers=self.h(tok)).json
        self.assertEqual(me["score"], total)
        self.assertGreaterEqual(me["xp"], total)
        self.assertEqual(me["streak"]["current"], 1)
        lb = self.c.get("/api/leaderboard?scope=overall").json["rows"]
        self.assertIn(g["user"]["nick"], [x["nick"] for x in lb])
        for scope in ("weekly", "streak"):
            self.assertEqual(self.c.get(f"/api/leaderboard?scope={scope}").status_code, 200)
        self.assertEqual(self.c.get("/api/leaderboard?scope=track&track=networking").json["rows"][0]["score"], total)
        # second run: already solved gives no extra marks
        run2 = self.start(tok).json["run"]
        it = next(i for i in run2["challenges"] if not KEY[i["id"]]["dyn"])
        again = self.sub(tok, run2["id"], it["id"], self.right(it)).json
        self.assertFalse(again["counted"])
        self.assertGreater(again["points"], 0)  # still shows run performance
        self.assertEqual(again["note"], "Already solved")
        self.assertEqual(self.c.get("/api/me", headers=self.h(tok)).json["score"], total)

    def test_free_roam_scores_nothing(self):
        tok = self.guest()["token"]
        run = self.start(tok, mode="free").json["run"]
        it = next(i for i in run["challenges"] if i["type"] == "mcq")
        r = self.sub(tok, run["id"], it["id"], self.right(it)).json
        self.assertTrue(r["correct"])
        self.assertFalse(r["counted"])
        self.assertEqual(r["xp"], 0)
        self.assertEqual(self.c.get("/api/me", headers=self.h(tok)).json["score"], 0)

    def test_mcq_one_attempt_reveals(self):
        tok = self.guest()["token"]
        run = self.start(tok).json["run"]
        it = next(i for i in run["challenges"] if i["type"] == "mcq")
        wrong = next(o for o in it["options"] if o != KEY[it["id"]]["correct_option"])
        r = self.sub(tok, run["id"], it["id"], wrong).json
        self.assertFalse(r["correct"])
        self.assertEqual(r["correctOption"], KEY[it["id"]]["correct_option"])
        self.assertEqual(self.sub(tok, run["id"], it["id"], wrong).status_code, 409)

    def test_flag_penalty_and_hint_cost(self):
        tok = self.guest()["token"]
        run = self.start(tok, "linux", "beginner").json["run"]
        it = next(i for i in run["challenges"] if i["id"] == "lin-b4")  # text, 10 marks, 5 attempts
        for _ in range(3):
            self.assertFalse(self.sub(tok, run["id"], it["id"], "nope").json["correct"])
        r = self.sub(tok, run["id"], it["id"], self.right(it)).json  # 4th attempt: -2 -2
        self.assertEqual(r["scored"], 6)
        self.assertEqual(ctf.earned_points(20, "flag", 1, 1, IMP["scoring"]), 15)
        self.assertEqual(ctf.earned_points(20, "flag", 3, 0, IMP["scoring"]), 18)
        self.assertEqual(ctf.earned_points(20, "flag", 1, 2, IMP["scoring"]), 10)
        self.assertEqual(ctf.earned_points(10, "mcq", 2, 0, IMP["scoring"]), 0)

    def test_hint_flow(self):
        tok = self.guest()["token"]
        run = self.start(tok).json["run"]
        mcq = next(i for i in run["challenges"] if i["type"] == "mcq")
        h = self.c.post(f"/api/challenges/{mcq['id']}/hint", json={"run_id": run["id"]}, headers=self.h(tok)).json
        self.assertEqual(len(h["eliminate"]), 2)
        self.assertNotIn(KEY[mcq["id"]]["correct_option"], h["eliminate"])
        again = self.c.post(f"/api/challenges/{mcq['id']}/hint", json={"run_id": run["id"]}, headers=self.h(tok))
        self.assertEqual(again.status_code, 409)
        r = self.sub(tok, run["id"], mcq["id"], self.right(mcq)).json
        self.assertEqual(r["scored"], round(KEY[mcq["id"]]["points"] * 0.75))

    def test_lockout_after_five_wrong(self):
        tok = self.guest()["token"]
        cid = "lin-b4"
        for _ in range(2):  # 3 + 2 wrong across two runs = 5
            run = self.start(tok, "linux").json["run"]
            for _ in range(3):
                self.sub(tok, run["id"], cid, "nope")
                core._hits.clear()
        run = self.start(tok, "linux").json["run"]
        r = self.sub(tok, run["id"], cid, "tail -n 20")
        self.assertEqual(r.status_code, 429)
        self.assertTrue(r.json["locked"])
        self.assertIn("Retry-After", r.headers)

    def test_dynamic_flag_sharing_logged(self):
        a, b = self.guest(), self.guest()
        ra = self.start(a["token"]).json["run"]
        rb = self.start(b["token"]).json["run"]
        ia = next(i for i in ra["challenges"] if i["id"] == "net-b5")
        ib = next(i for i in rb["challenges"] if i["id"] == "net-b5")
        self.assertNotEqual(ia["code"], ib["code"])
        flag_a = bytes.fromhex(ia["code"].replace(" ", "")).decode()
        self.assertFalse(self.sub(b["token"], rb["id"], "net-b5", flag_a).json["correct"])
        self.assertFalse(self.sub(b["token"], rb["id"], "net-b5", plain("net-b5")["answers"][0]).json["correct"])
        con = self.db()
        kinds = [r[0] for r in con.execute("SELECT kind FROM security_events WHERE user_id = ?", (b["user"]["id"],))]
        self.assertIn("flag_sharing", kinds)

    def test_all_encoders_round_trip(self):
        import base64
        f = ctf.user_flag(26, "x")
        self.assertRegex(f, r"^CWM\{u1a_[0-9a-f]{16}\}$")
        dec = {"hex": lambda s: bytes.fromhex(s.replace(" ", "")).decode(),
               "basicauth": lambda s: base64.b64decode(s).decode().split(":", 1)[1],
               "rev": lambda s: s[::-1], "rot13": ctf._rot13,
               "b64rot13": lambda s: base64.b64decode(ctf._rot13(s)).decode(),
               "b64": lambda s: base64.b64decode(s).decode(),
               "jwt": lambda s: json.loads(base64.urlsafe_b64decode(s.split(".")[1] + "=="))["flag"],
               "xor5a": lambda s: bytes(b ^ 0x5A for b in bytes.fromhex(s)).decode(),
               "ps": lambda s: base64.b64decode(s).decode("utf-16-le").split("'")[1]}
        for enc, fn in dec.items():
            self.assertEqual(fn(ctf.encode_artifact(enc, f)), f, enc)

    def test_identical_404s(self):
        tok = self.guest()["token"]
        run = self.start(tok).json["run"]
        a = self.sub(tok, "bogus", "net-b1", "x")
        b = self.sub(tok, run["id"], "zzz-b9", "x")
        c = self.sub(tok, run["id"], "lin-b1", "x")  # real id, not in this run
        d = self.c.post("/api/runs/bogus/finish", json={}, headers=self.h(tok))
        self.assertEqual({a.status_code, b.status_code, c.status_code, d.status_code}, {404})
        self.assertEqual(len({a.data, b.data, c.data, d.data}), 1)

    def test_streak_shields(self):
        con = self.db()
        con.row_factory = sqlite3.Row
        day = 86400
        t0 = 1_800_000_000
        for i in range(5):
            ctf.bump_streak(con, 999, t0 + i * day)
        row = con.execute("SELECT * FROM user_streaks WHERE user_id = 999").fetchone()
        self.assertEqual((row["current"], row["shields"]), (5, 1))
        ctf.bump_streak(con, 999, t0 + 6 * day)  # skipped one day, shield covers it
        row = con.execute("SELECT * FROM user_streaks WHERE user_id = 999").fetchone()
        self.assertEqual((row["current"], row["shields"]), (6, 0))
        ctf.bump_streak(con, 999, t0 + 9 * day)  # two missed days, no shield
        self.assertEqual(con.execute("SELECT current FROM user_streaks WHERE user_id = 999").fetchone()[0], 1)
        self.assertEqual(ctf.ist_day(18000), 0)       # 05:00 IST on 1 Jan 1970
        self.assertEqual(ctf.ist_day(86400 - 19800), 1)  # IST midnight


class Hardening(Base):
    def test_big_body_and_bad_origin_and_cors(self):
        tok = self.guest()["token"]
        r = self.c.post("/api/runs", data=json.dumps({"x": "a" * 5000}), content_type="application/json",
                        headers=self.h(tok))
        self.assertEqual(r.status_code, 413)
        r = self.c.post("/api/auth/guest", json={"nick": "evilorigin"}, headers={"Origin": "https://evil.example"})
        self.assertEqual(r.status_code, 403)
        r = self.c.options("/api/auth/guest", headers={"Origin": "https://iammadhavpandya-oss.github.io",
                                                       "Access-Control-Request-Method": "POST"})
        self.assertEqual(r.headers.get("Access-Control-Allow-Origin"), "https://iammadhavpandya-oss.github.io")
        self.assertIn("Authorization", r.headers.get("Access-Control-Allow-Headers"))
        self.assertIn("Retry-After", r.headers.get("Access-Control-Expose-Headers", ""))  # so the page can show the wait
        r = self.c.options("/api/auth/guest", headers={"Origin": "http://localhost:5500"})
        self.assertIsNone(r.headers.get("Access-Control-Allow-Origin"))  # main-site dev origin is not CTF-allowed
        self.assertEqual(self.c.get("/api/tracks").headers["X-Content-Type-Options"], "nosniff")

    def test_existing_endpoints_still_work(self):
        r = self.c.post("/api/subscribe", json={"email": "a@example.com"}, headers=ORIGIN)
        self.assertIn(r.status_code, (200, 201))


if __name__ == "__main__":
    unittest.main()
