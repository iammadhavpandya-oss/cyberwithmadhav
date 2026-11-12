# CyberWithMadhav website

Minimal dark purple + green site for **CyberWithMadhav**, a cybersecurity awareness & learning brand by Madhav Pandya (Mumbai).

Static site (vanilla HTML/CSS/JS, no framework) whose content lives in JSON, plus an **optional** Flask backend for newsletter signup and the contact form.

## Sections
| Section | What it has |
|---|---|
| 1930 banner | "Scammed? Call 1930" bar, dismissible (remembered for the session) |
| Hero | Headline + subhead, `whoami` typing, terminal with an **nmap demo** and a **"scam or not?" quiz**, proof line (counts computed from the data) |
| Roadmap | Beginner → Intermediate → Advanced tabs: goals, topics, free resources, projects |
| Networking | OSI vs TCP/IP layers, concept cards, common ports |
| Cheat sheets | 9 sheets / 110 entries. Sticky search + filter bar, max 8 rows per sheet with "Show all N →", search highlight, **{{VARS}}** you can set once (saved in `localStorage`), tap a row or button to copy ("copied ✓"), flag tooltips, light print stylesheet |
| Tools | All client-side and educational: **subnet calculator**, **password strength** (entropy + pattern penalties + crack-time, never stored), **hash identifier** (with hashcat modes), **link checker** (URL analyzer + manual checklist; the link is never opened) |
| Careers | 7 job paths: what you do, skills, certs, first steps (salaries intentionally omitted) |
| Cyber awareness | **1930** helpline + cybercrime.gov.in, common Indian scams with red flags, safety habits |
| About | Headline, honest timeline ("live" badges), law callout (IT Act, DPDP Act 2023, CERT-In, GRC), projects with "building" notes and GitHub stars (shown only if > 0) |
| Contact | Newsletter + contact form (honeypot, client + server validation) |
| Footer | Ethics / legal note (IT Act 2000, s.43 & s.66) |

Shortcuts: `/` focuses cheat-sheet search, `Ctrl/⌘ + K` opens the command palette (sections, tools, sheets, commands).

Colour roles: purple = actions/links, green = code and live states only, amber = alerts. Muted text is ≥ 7:1 contrast. Mobile: one-column cards, sideways-scrolling filter chips. `prefers-reduced-motion`: no glow, no typing.

Extras: sticky nav with scroll-spy, reading-progress bar, light/dark toggle (saved in `localStorage`), scroll-reveal via IntersectionObserver (content visible without JS), SEO + Open Graph + JSON-LD, SVG favicon.

## CTF Arena (`ctf.html`)
Seven tracks (Networking, Linux, Basic IT Knowledge, CCNA, Cloud Computing, Pentesting, Blue Team), three levels each, 111 self-contained puzzles (MCQ, multi-select, flag, command, log reading, ordering). Beginner 10 marks, Intermediate 20, Expert 30; score 60% to unlock the next level. Results show a Bhagavad Gita verse for the score band, plus a philosopher quote on low scores (`data/ctf_quotes.json`).

- **Static practice mode (default, GitHub Pages):** `data/ctf.json` holds PBKDF2 verifiers only; explanations are AES-GCM encrypted with a key derived from the right answer. Progress lives in `localStorage`. This is honour-system: a determined player can brute-force short answers offline.
- **Server mode (optional):** set `<meta name="cwm-api" content="https://api.your-domain">` in `ctf.html`. The Flask app checks answers with HMAC-SHA256 under a secret `FLAG_PEPPER`, issues per-player flags for some challenges, and runs the leaderboard. If `/api/health` does not answer within 2.5 s the page falls back to practice mode and never mixes the two scores.

Content workflow (the answer key never goes in git):
```bash
# edit backend/ctf_answers.private.json (gitignored; see backend/ctf_answers.example.json for the format)
python3 tools/build_ctf.py --check      # validate
python3 tools/build_ctf.py              # writes data/ctf.json + backend/ctf_import.private.json
cd backend && FLAG_PEPPER=... python manage.py import
python3 tools/csp_hash.py               # only if the inline theme script in ctf.html changes
```
Tests: `cd tools && node test_ctf.mjs` (45 browser checks, also run at the end of `test.mjs`; needs the private key file, set `SKIP_CTF=1` to skip) and `cd backend && python -m unittest test_ctf` (20 API checks).

## CyberPrompts (`prompts.html`) and Cyber Law India (`cyberlaw.html`)

- `prompts.html`: 90 defensive / authorised-use prompts in 19 categories (incl. the Defensive Analysis group), search, category filter, favourites in localStorage, 12 "How to use safely" scenario cards. Data: `data/prompts.json`, `data/cyberprompts_usecases.json`.
- `cyberlaw.html`: hero (Sec 43 civil vs Sec 66 crime), History of Indian Cyber Law timeline (`data/cyberlaw_timeline.json`, 26 entries), IT Act table (28 rows), BNS to IPC map (17 rows), DPDP penalties, procedure (7 steps), Where to File (`data/cyberlaw_reporting.json`, 9 forums, NCRP and 1930 first), 12 case files, FAQ in English and Hinglish (15), glossary (40), PDF downloads (`assets/pdf/`). Educational, not legal advice.
- Tags: `verify` (solid) = open question; `being verified` (dashed) = fact-check item still being confirmed against the linked primary source.

Build order (content lives in `/workspace/cwm-content`, outside the repo):

```bash
python3 tools/build_pages_data.py   # writes data/*.json, applies tools/content/factcheck.py (fact-check corrections override raw content), copies the reporting guide forums, then tools/content/seo.py (titles, meta, og, keywords, JSON-LD for prompts, cyberlaw, ctf)
python3 tools/csp_hash.py           # only if an inline script changed
```

Tests: `cd tools && node test_pages.mjs` (prompts + cyberlaw + SEO, screenshots in `docs/`), or `node test.mjs` for everything (`SKIP_CTF=1` / `SKIP_PAGES=1` to skip parts). `sitemap.xml` and `robots.txt` list the real URLs.

## File tree
```
cwm-site/
├── index.html            # page shell, SEO/OG meta
├── favicon.svg
├── assets/css/style.css  # theme, layout, print CSS
├── assets/js/main.js     # rendering, subnet calc, search, forms
├── data/                 # ← edit content here
│   ├── roadmap.json  networking.json  cheatsheets.json
│   ├── jobs.json     awareness.json   about.json   tools.json
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
Everything is in `data/*.json`, with no build step. Text is HTML-escaped when rendered, so plain text only. Cheat-sheet entries are `{ "cmd": "...", "desc": "..." }` (or `type: "text"` sheets with `items`). Keep facts accurate; don't add unsourced stats or salary numbers.

## Tests
With both servers running:
```bash
cd tools && npm i && node test.mjs
```
Runs 83 checks in headless Chrome (hero, quiz, contrast + colour roles, cheat-sheet cap/search/copy/vars/flags/palette/shortcuts, subnet/password/hash/link tools, about, forms end-to-end, theme toggle, SEO meta, mobile layout, reduced motion, print CSS, zero console errors; GitHub API is stubbed) and regenerates `docs/*.png`. Set `CHROME_PATH` if Chrome isn't at `/usr/bin/google-chrome`. Use a fresh DB (`CWM_DB_PATH=/tmp/x.sqlite3`) per run so the rate limiter doesn't trip.

## Backend security
- JSON only (415 otherwise), 16 KB body cap (413), strict email/name/message validation
- Per-IP sliding-window rate limit (5 req / 10 min / endpoint by default) → 429
- Honeypot field `website`: bots get a fake 200, nothing stored
- CORS allow-list from `CWM_ALLOWED_ORIGINS` (defaults to localhost:8000/5500); other origins → 403
- Parameterized SQLite queries, security headers, no secrets in code (all config via env)

## Deploy
See [docs/DEPLOY.md](docs/DEPLOY.md): GitHub Pages / Netlify / Cloudflare Pages for the static site (free), and optional backend hosting.

## TODO
- [ ] Instagram and YouTube URLs → `data/about.json` (`links[].url`; rows stay hidden while empty), plus `sameAs` in the JSON-LD in `index.html`
- [ ] Real numbers only if available → `data/about.json` `timeline[].metric` (empty = hidden)
- [ ] Photo → `assets/img/madhav.jpg`, then swap the "MP" placeholder in `index.html`
- [x] Real domain: `<link rel="canonical">`, `og:url`, `og:image` and `sitemap.xml` point to https://www.cyberwithmadhav.com/
- [ ] Social preview image → `assets/img/og-image.png` (1200×630)
- [ ] CTF API is not deployed yet: see the CTF section of docs/DEPLOY.md, then set `cwm-api` in `ctf.html`
- [ ] If the backend is deployed: set `<meta name="cwm-api" content="https://api.your-domain">` and `CWM_ALLOWED_ORIGINS`
- [ ] Rate limiter is in-memory (single process). For multiple workers use Redis or a proxy-level limit.

## Ethics
All offensive-security content is for learning and **authorised** testing only. Unauthorised access is an offence under the IT Act 2000 (India).
