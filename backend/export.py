"""Export subscribers/messages to CSV:  python export.py subscribers > subs.csv"""
import csv, os, sqlite3, sys
from pathlib import Path
db = Path(os.environ.get("CWM_DB_PATH", Path(__file__).with_name("cwm.sqlite3")))
table = sys.argv[1] if len(sys.argv) > 1 else "subscribers"
if table not in {"subscribers", "messages"}:
    sys.exit("usage: python export.py [subscribers|messages]")
conn = sqlite3.connect(db)
cur = conn.execute(f"SELECT * FROM {table} ORDER BY id")
w = csv.writer(sys.stdout)
w.writerow([d[0] for d in cur.description])
w.writerows(cur)
