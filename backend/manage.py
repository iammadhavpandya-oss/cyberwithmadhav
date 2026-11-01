#!/usr/bin/env python3
"""CTF admin CLI.  Run from backend/ with FLAG_PEPPER set (same value as the web app).

  python manage.py import [path]       load/refresh challenges from ctf_import.private.json
  python manage.py hide-user <nick>     hide a player from leaderboards (keeps their data)
  python manage.py unhide-user <nick>
  python manage.py events [n]           show the latest security events (flag_sharing, too_fast)
  python manage.py stats                players, solves and challenges in the database
"""
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("CWM_CTF_AUTO_IMPORT", "0")
import ctf  # noqa: E402

DB = os.environ.get("CWM_DB_PATH", str(HERE / "cwm.sqlite3"))
IST = timezone(timedelta(hours=5, minutes=30))


def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.executescript(ctf.SCHEMA)
    return con


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, args = argv[0], argv[1:]
    con = connect()
    try:
        if cmd == "import":
            if not os.environ.get("FLAG_PEPPER"):
                print("warning: FLAG_PEPPER not set, using the dev pepper file")
            n = ctf.import_challenges(con, Path(args[0]) if args else ctf.IMPORT_PATH)
            print(f"imported {n} challenges")
        elif cmd in ("hide-user", "unhide-user") and args:
            cur = con.execute("UPDATE users SET hidden = ? WHERE nick = ?", (1 if cmd == "hide-user" else 0, args[0]))
            con.commit()
            print(f"{'hid' if cmd == 'hide-user' else 'unhid'} {cur.rowcount} user(s)")
            return 0 if cur.rowcount else 1
        elif cmd == "events":
            n = int(args[0]) if args else 20
            for r in con.execute("SELECT e.*, u.nick FROM security_events e LEFT JOIN users u ON u.id = e.user_id "
                                 "ORDER BY e.id DESC LIMIT ?", (n,)):
                when = datetime.fromtimestamp(r["created_at"], IST).strftime("%Y-%m-%d %H:%M IST")
                print(f"{when}  {r['kind']:<13} {r['nick'] or '-':<20} {r['detail']}")
        elif cmd == "stats":
            q = lambda s: con.execute(s).fetchone()[0]  # noqa: E731
            print(json.dumps({"players": q("SELECT COUNT(*) FROM users"), "hidden": q("SELECT COUNT(*) FROM users WHERE hidden"),
                              "challenges": q("SELECT COUNT(*) FROM challenges"), "solves": q("SELECT COUNT(*) FROM solves"),
                              "submissions": q("SELECT COUNT(*) FROM submissions"),
                              "events": q("SELECT COUNT(*) FROM security_events")}, indent=1))
        else:
            print(__doc__)
            return 2
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
