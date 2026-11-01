#!/usr/bin/env python3
"""Copy the verified quote bank into data/ctf_quotes.json for the CTF result screen.

Usage: python3 tools/sync_quotes.py [/path/to/ctf_quotes.json]
Default source: /workspace/cwm-content/ctf_quotes.json

The site style rule is "no em dash in visible copy", so this replaces em dashes
with commas (punctuation only; words are untouched). meta.notes is kept in the file
for maintainers but is never shown in the UI.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/cwm-content/ctf_quotes.json")
DST = ROOT / "data" / "ctf_quotes.json"
FIELDS = ("text", "author_or_ref", "band", "translation_en", "meaning_hi", "source")

def tidy(s):
    if not isinstance(s, str):
        return s
    s = re.sub(r"\s*,?\s*\u2014\s*", ", ", s)   # em dash -> comma
    return re.sub(r"\s*\u2013\s*", "-", s)       # en dash -> hyphen

d = json.loads(SRC.read_text(encoding="utf-8"))
out = {"meta": d.get("meta", {}), "philosophers": [], "gita": []}
for key in ("philosophers", "gita"):
    for q in d.get(key, []):
        item = {f: tidy(q.get(f)) for f in FIELDS}
        if item["band"] not in ("low", "mid", "high") or not item["text"] or not item["author_or_ref"]:
            raise SystemExit(f"bad quote in {key}: {q}")
        if item["source"] and not str(item["source"]).startswith("https://"):
            raise SystemExit(f"source must be https: {q}")
        out[key].append(item)
for key in ("philosophers", "gita"):
    for band in ("low", "mid", "high"):
        if not any(q["band"] == band for q in out[key]):
            raise SystemExit(f"{key} has no '{band}' quote")
out["meta"]["synced_from"] = SRC.name
DST.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"wrote {DST} ({len(out['philosophers'])} philosophers, {len(out['gita'])} gita)")
