#!/usr/bin/env python3
"""Checks every internal href/src in the root HTML pages: the file must exist and any #fragment must match an id in it.
Fragments starting with / are client side routes (ctf.html) and are skipped.
Run from the repo root: python3 tools/check_links.py"""
import re, sys
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
ids = {}


def ids_of(f):
    if f not in ids:
        ids[f] = set(re.findall(r'\sid="([^"]+)"', (ROOT / f).read_text(encoding="utf-8")))
    return ids[f]


bad, n = [], 0
for page in sorted(ROOT.glob("*.html")):
    s = page.read_text(encoding="utf-8")
    for m in re.finditer(r'\s(?:href|src)="([^"]+)"', s):
        u = m.group(1)
        if re.match(r"^(https?:|mailto:|tel:|data:|javascript:|//)", u):
            continue
        n += 1
        pu = urlparse(u)
        target = unquote(pu.path) or page.name
        if not (ROOT / target).exists():
            bad.append(f"{page.name}: missing file {u}"); continue
        if pu.fragment and not pu.fragment.startswith("/") and target.endswith(".html") and pu.fragment not in ids_of(target):
            bad.append(f"{page.name}: missing anchor {u}")
print(f"checked {n} internal links in {len(list(ROOT.glob('*.html')))} pages, {len(bad)} broken")
print("\n".join(bad))
sys.exit(1 if bad else 0)
