#!/usr/bin/env python3
"""Recompute the sha256 of each inline <script> in the pages with a CSP meta (ctf, prompts, cyberlaw) and update it.
Run after editing the theme pre-paint script:  python3 tools/csp_hash.py"""
import base64, hashlib, re
from pathlib import Path

for name in ("ctf.html", "prompts.html", "cyberlaw.html", "terms.html", "privacy.html"):
  p = Path(__file__).resolve().parent.parent / name
  html = p.read_text(encoding="utf-8")
  hashes = ["'sha256-%s'" % base64.b64encode(hashlib.sha256(m.encode()).digest()).decode()
          for m in re.findall(r"<script>(.*?)</script>", html, re.S)]
  html, n = re.subn(r"script-src 'self'( 'sha256-[^']+')*", "script-src 'self' " + " ".join(hashes), html)
  p.write_text(html, encoding="utf-8")
  print(f"{name}: updated {n} CSP meta with {len(hashes)} hash(es)")
