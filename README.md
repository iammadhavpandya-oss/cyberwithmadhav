# CyberWithMadhav — website

Minimal dark purple + green site for **CyberWithMadhav**, a cybersecurity awareness & learning brand by Madhav Pandya (Vasai, Mumbai).

Static site (vanilla HTML/CSS/JS, no framework) whose content lives in JSON, plus an **optional** Flask backend for newsletter signup and the contact form.

## Sections
| Section | What it has |
|---|---|
| Hero | Intro, CTAs, topic tags |
| Roadmap | Beginner → Intermediate → Advanced tabs: goals, topics, free resources, projects |
| Networking | OSI vs TCP/IP layers, 10 concept cards, common ports, **subnet calculator** (network, broadcast, host range, mask, wildcard, binary; handles /31 and /32) |
| Cheat sheets | 9 sheets (Linux, Nmap, Ports, Wireshark, Git, OWASP Top 10 2021, Incident Response, Windows/AD, Security hygiene) — search with highlight, category filters, copy buttons, print/PDF stylesheet |
| Careers | 7 job paths: what you do, skills, certs, first steps (salaries intentionally omitted) |
| Cyber awareness | **1930** helpline + cybercrime.gov.in, 6 common Indian scams with red flags, 8 safety habits |
| About | Bio, links, timeline, projects (geoimg-osint, homelab-toolkit) |
| Contact | Newsletter + contact form (honeypot, client + server validation) |
| Footer | Ethics / legal note (IT Act 2000, s.43 & s.66) |

Extras: sticky nav with scroll-spy, reading-progress bar, light/dark toggle (saved in `localStorage`), scroll-reveal via IntersectionObserver (disabled under `prefers-reduced-motion`, content visible without JS), SEO + Open Graph + JSON-LD, SVG favicon.

## File tree
```
cwm-site/
├── index.html            # page shell, SEO/OG meta
├── favicon.svg
├── assets/css/style.css  # theme, layout, print CSS
├── assets/js/main.js     # rendering, subnet calc, search, forms
├── data/                 # ← edit content here
│   ├── roadmap.json  networking.json  cheatsheets.json
│   ├── jobs.json     awareness.json   about.json
├── backend/              # optional Flask API
│   ├── app.py  export.py  requirements.txt  .env.example
├── tools/                # headless tests + screenshots (puppeteer-core)
│   ├── test.mjs  package.json
└── docs/                 # screenshots, DEPLOY.md
```

## Run locally
```bash
# 1) static site
cd cwm-site
python3 -m http.server 8000 --bind 127.0.0.1
# open http://127.0.0.1:8000

# 2) optional backend (second terminal)
cd cwm-site/backend
python3 -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # optional; edit values
python app.py           # http://127.0.0.1:5000  (GET /api/health)
```
On `localhost`/`127.0.0.1` the forms talk to `http://127.0.0.1:5000` automatically. Without a backend (e.g. on GitHub Pages) they show an "email me instead" fallback.

Export stored data: `python export.py subscribers > subs.csv` or `python export.py messages > msgs.csv`.

## Editing content
Everything is in `data/*.json` — no build step. Text is HTML-escaped when rendered, so plain text only. Cheat-sheet entries are `{ "cmd": "...", "desc": "..." }` (or `type: "text"` sheets with `items`). Keep facts accurate; don't add unsourced stats or salary numbers.

## Tests
With both servers running:
```bash
cd tools && npm i && node test.mjs
```
Runs 30 checks in headless Chrome (subnet math incl. edge cases, search/filter/copy, roadmap tabs, forms end-to-end, theme toggle, SEO meta, mobile overflow/menu, reduced motion, print CSS, zero console errors) and regenerates `docs/*.png`. Set `CHROME_PATH` if Chrome isn't at `/usr/bin/google-chrome`. Use a fresh DB (`CWM_DB_PATH=/tmp/x.sqlite3`) per run so the rate limiter doesn't trip.

## Backend security
- JSON only (415 otherwise), 16 KB body cap (413), strict email/name/message validation
- Per-IP sliding-window rate limit (5 req / 10 min / endpoint by default) → 429
- Honeypot field `website`: bots get a fake 200, nothing stored
- CORS allow-list from `CWM_ALLOWED_ORIGINS` (defaults to localhost:8000/5500); other origins → 403
- Parameterized SQLite queries, security headers, no secrets in code (all config via env)

## Deploy
See [docs/DEPLOY.md](docs/DEPLOY.md) — GitHub Pages / Netlify / Cloudflare Pages for the static site (free), and optional backend hosting.

## TODO
- [ ] Instagram and YouTube URLs → `data/about.json` (`links`), plus `sameAs` in the JSON-LD in `index.html`
- [ ] Photo → `assets/img/madhav.jpg`, then swap the "MP" placeholder in `index.html`
- [ ] Real domain → `<link rel="canonical">`, `og:url`, JSON-LD `url` (currently `cyberwithmadhav.example`)
- [ ] Social preview image → `assets/img/og-image.png` (1200×630)
- [ ] If the backend is deployed: set `<meta name="cwm-api" content="https://api.your-domain">` and `CWM_ALLOWED_ORIGINS`
- [ ] Rate limiter is in-memory (single process). For multiple workers use Redis or a proxy-level limit.

## Ethics
All offensive-security content is for learning and **authorised** testing only. Unauthorised access is an offence under the IT Act 2000 (India).
