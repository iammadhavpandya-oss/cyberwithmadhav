#!/usr/bin/env python3
"""Site wide build step. Run after build_pages_data.py and build_legal.py. It runs csp_hash.py itself.

It is idempotent and does five things:
  1. Head tags on every page: og:image (1200x630), twitter:image, web app manifest and apple touch icon.
  2. Shared scripts on every page: assets/js/pwa.js, plus assets/js/search.js on pages other than index.html.
  3. data/search.json: the Ctrl+K search index built from every page and the data files.
  4. sitemap.xml (every public page) and feed.xml (RSS 2.0).
  5. sw.js (offline cache with a content hash version) and 404.html.
"""
import hashlib, html, json, re, subprocess
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BASE = "https://iammadhavpandya-oss.github.io/cyberwithmadhav/"
OG_IMG = BASE + "assets/img/og-image.png"
OG_ALT = "CyberWithMadhav: Cybersecurity in plain English and Hinglish."

# Public pages in nav order. Pages that do not exist yet are skipped.
PAGES = ["index.html", "explore.html", "commands.html", "scams.html", "game.html", "soc.html", "owasp.html", "terminal.html", "daily.html", "progress.html",
         "ctf.html", "prompts.html", "cyberlaw.html", "terms.html", "privacy.html"]
PRIORITY = {"index.html": "1.0", "terms.html": "0.3", "privacy.html": "0.3"}


def pages():
    return [p for p in PAGES if (ROOT / p).exists()]


def read(p): return (ROOT / p).read_text(encoding="utf-8")


def write(p, s):
    path = ROOT / p
    if not path.exists() or path.read_text(encoding="utf-8") != s:
        path.write_text(s, encoding="utf-8")
        print("wrote", p)


def meta(s, attr, name):
    m = re.search(r'<meta %s="%s" content="([^"]*)"' % (attr, re.escape(name)), s)
    return html.unescape(m.group(1)) if m else ""


def title_of(s): return html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1).strip())


def strip_tags(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def git_date(p):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cI", "--", p], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", p], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if out and not dirty: return datetime.fromisoformat(out)
    except Exception:
        pass
    now = datetime.now(timezone.utc).astimezone()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)  # stable within a day for uncommitted files


# ---------- 1 and 2: head tags, nav "More" menu and shared scripts ----------
# The top nav is kept short: Home, Explore (the hub that lists every page), CTF, then search and theme.
NAV = [("index.html", "Home", "nav-home", ""),
       ("explore.html", "Explore", "nav-explore",
        '<svg class="nav-ico" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(-25 12 12)"/></svg>'),
       ("ctf.html", "CTF", "nav-ctf", '<span class="nav-ctf-dot" aria-hidden="true"></span>')]


def nav_links(p):
    hub = p not in [f for f, _, _, _ in NAV] and p != "404.html"  # every other page lives inside Explore
    out = []
    for f, label, cls, ico in NAV:
        if not (ROOT / f).exists(): continue
        attrs = f' class="{cls}{" active" if f == p or (hub and f == "explore.html") else ""}"'
        if f == p: attrs += ' aria-current="page"'
        out.append(f'\n        <a href="{f}"{attrs}>{ico}{label}</a>')
    return "".join(out)


def patch_nav(s, p):
    m = re.search(r'<nav id="nav-links"[^>]*>.*?</nav>', s, re.S)
    if not m: return s
    nav = m.group(0)
    head = re.match(r'<nav id="nav-links"[^>]*>', nav).group(0)
    pal = re.search(r'\n\s*<button class="pal-btn".*?</button>', nav, re.S)
    tt = re.search(r'\n\s*<button class="theme-toggle".*?</button>', nav, re.S)
    nav = head + nav_links(p) + (pal.group(0) if pal else "") + (tt.group(0) if tt else "") + "\n      </nav>"
    return s[:m.start()] + nav + s[m.end():]


def patch_page(p):
    s = read(p)
    s = patch_nav(s, p)
    # social image tags: drop old ones, then add one consistent block after og:locale (or og:url)
    s = re.sub(r'\n\s*<meta (?:property="og:image(?::[a-z]+)?"|name="twitter:image(?::alt)?") content="[^"]*">', "", s)
    title, desc = meta(s, "property", "og:title") or title_of(s), meta(s, "property", "og:description") or meta(s, "name", "description")
    social = (f'\n  <meta property="og:image" content="{OG_IMG}">'
              '\n  <meta property="og:image:width" content="1200">\n  <meta property="og:image:height" content="630">'
              f'\n  <meta property="og:image:alt" content="{html.escape(OG_ALT)}">')
    anchor = re.search(r'\n\s*<meta property="og:locale"[^>]*>', s) or re.search(r'\n\s*<meta property="og:url"[^>]*>', s)
    s = s[:anchor.end()] + social + s[anchor.end():]
    if 'name="twitter:card"' not in s:
        tw = (f'\n  <meta name="twitter:card" content="summary_large_image">'
              f'\n  <meta name="twitter:title" content="{html.escape(title)}">'
              f'\n  <meta name="twitter:description" content="{html.escape(desc)}">')
        a = s.index(social) + len(social); s = s[:a] + tw + s[a:]
    m = re.search(r'\n\s*<meta name="twitter:description"[^>]*>', s)
    s = s[:m.end()] + f'\n  <meta name="twitter:image" content="{OG_IMG}">\n  <meta name="twitter:image:alt" content="{html.escape(OG_ALT)}">' + s[m.end():]
    # manifest and touch icon after the favicon
    s = re.sub(r'\n\s*<link rel="(?:manifest|apple-touch-icon)"[^>]*>', "", s)
    s = s.replace('<link rel="icon" type="image/svg+xml" href="favicon.svg">',
                  '<link rel="icon" type="image/svg+xml" href="favicon.svg">\n  <link rel="manifest" href="manifest.json">\n  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">', 1)
    # shared scripts before </body>
    s = re.sub(r'\n\s*<script src="assets/js/(?:pwa|search|nav)\.js" defer></script>', "", s)
    tags = ['<script src="assets/js/nav.js" defer></script>'] + ([] if p == "index.html" else ['<script src="assets/js/search.js" defer></script>']) + ['<script src="assets/js/pwa.js" defer></script>']
    s = s.replace("\n</body>", "".join("\n  " + t for t in tags) + "\n</body>", 1)
    write(p, s)


# ---------- 3: search index ----------
def short_title(t): return re.split(r"\s+\|\s+|:\s", t)[0].strip()


def search_index():
    out, seen = [], set()

    def add(k, t, s, u, x=""):
        key = (k, t, u)
        if key in seen: return
        seen.add(key); item = {"k": k, "t": t, "s": s[:110], "u": u}
        if x: item["x"] = x[:300]
        out.append(item)

    for p in pages():
        s = read(p)
        name = "Home" if p == "index.html" else short_title(title_of(s))
        add("Page", name, meta(s, "name", "description"), p)
        for m in re.finditer(r'<section[^>]*\bid="([a-z0-9-]+)"[^>]*>(.*?)</h2>', s, re.S):
            sid, body = m.group(1), m.group(2)
            h = re.search(r"<h2[^>]*>(.*)$", body, re.S)
            if not h or sid in ("hero", "top"): continue
            add("Section", strip_tags(h.group(1)), name, f"{p}#{sid}")
    cs = json.loads((DATA / "cheatsheets.json").read_text())
    for sh in cs["sheets"]:
        add("Sheet", sh["title"], sh["category"] + " cheat sheet", f"index.html#sheet-{sh['id']}", sh.get("desc", ""))
        if sh.get("type") == "text": continue
        for it in sh["items"]:
            cmd = re.sub(r"\{\{(\w+)\}\}", lambda m: next((v["default"] for v in cs["variables"] if v["key"] == m.group(1)), m.group(0)), it["cmd"])
            add("Command", cmd, it["what"], "index.html?q=" + _q(it["what"]) + "#cheatsheets", sh["title"])
    ctf = json.loads((DATA / "ctf.json").read_text())
    for t in ctf["tracks"]:
        add("CTF", t["name"] + " track", t.get("blurb", ""), f"ctf.html#/track/{t['id']}")
    pr = json.loads((DATA / "prompts.json").read_text())
    cats = {c["id"]: c["name"] for c in pr["categories"]}
    for c in pr["categories"]:
        add("Prompts", c["name"], "prompt category", f"prompts.html?cat={c['id']}#library", c.get("desc", ""))
    for q in pr["prompts"]:
        add("Prompt", q["title"], cats.get(q["cat"], ""), "prompts.html?q=" + _q(q["title"]) + "#library", q.get("use", ""))
    for g in json.loads((DATA / "cyberlaw_glossary.json").read_text()):
        add("Law term", g["term"], g.get("ref", "") or "glossary", "cyberlaw.html?q=" + _q(g["term"]) + "#glossary", g.get("meaning_en", ""))
    for f in json.loads((DATA / "cyberlaw_faq.json").read_text()):
        add("Law FAQ", f["q"], "Cyber Law FAQ", "cyberlaw.html#faq", " ".join(f.get("refs", [])))
    for c in json.loads((DATA / "cyberlaw_cases.json").read_text()):
        add("Case", c["name"], f'{c.get("court", "")} {c.get("year", "")}'.strip(), "cyberlaw.html#cases", c.get("why_it_matters", ""))
    for extra in ("commands_index.json", "scams_index.json", "game_index.json", "soc_index.json", "owasp_index.json", "terminal_index.json", "daily_index.json"):
        f = DATA / extra  # optional per page indexes written by later build steps
        if f.exists():
            for it in json.loads(f.read_text()): add(it["k"], it["t"], it.get("s", ""), it["u"], it.get("x", ""))
    for p in ("terms.html", "privacy.html"):
        if not (ROOT / p).exists(): continue
        for m in re.finditer(r'<section class="legal-sec[^"]*" id="([a-z0-9-]+)"[^>]*>\s*<h2[^>]*>(.*?)</h2>', read(p), re.S):
            add("Legal", strip_tags(m.group(2)), "Terms" if p == "terms.html" else "Privacy", f"{p}#{m.group(1)}")
    write("data/search.json", json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n")
    print("search.json:", len(out), "entries")


def _q(s):
    from urllib.parse import quote
    return quote(s, safe="")


# ---------- 4: sitemap and feed ----------
def sitemap_and_feed():
    ps = pages()
    rows = []
    for p in ps:
        loc = BASE if p == "index.html" else BASE + p
        rows.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{git_date(p).date().isoformat()}</lastmod>\n    <priority>{PRIORITY.get(p, '0.8')}</priority>\n  </url>")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n")
    items = []
    for p in sorted(ps, key=lambda p: git_date(p), reverse=True):
        s = read(p); loc = BASE if p == "index.html" else BASE + p
        items.append("    <item>\n"
                     f"      <title>{html.escape(meta(s, 'property', 'og:title') or title_of(s))}</title>\n"
                     f"      <link>{loc}</link>\n      <guid isPermaLink=\"true\">{loc}</guid>\n"
                     f"      <pubDate>{format_datetime(git_date(p))}</pubDate>\n"
                     f"      <description>{html.escape(meta(s, 'name', 'description'))}</description>\n    </item>")
    latest = max(git_date(p) for p in ps)
    write("feed.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n  <channel>\n'
          "    <title>CyberWithMadhav</title>\n"
          f"    <link>{BASE}</link>\n"
          f'    <atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>\n'
          "    <description>Cybersecurity in plain English and Hinglish: roadmap, cheat sheets, CTF practice, prompts, cyber law and scam alerts for India.</description>\n"
          "    <language>en-in</language>\n"
          f"    <lastBuildDate>{format_datetime(latest)}</lastBuildDate>\n" + "\n".join(items) + "\n  </channel>\n</rss>\n")


# ---------- 5: service worker and 404 ----------
def service_worker():
    ps = pages() + ["404.html"]
    assets = sorted({m for p in pages() for m in re.findall(r'(?:src|href)="((?:assets/(?:css|js|fonts)/)[^"?#]+)"', read(p))})
    fonts_css = ROOT / "assets/css/fonts.css"
    if fonts_css.exists():
        for name in re.findall(r'url\(\.\./fonts/([^)]+)\)', fonts_css.read_text(encoding="utf-8")):
            assets.append("assets/fonts/" + name)
        assets = sorted(set(assets))
    core = ["./"] + ps + assets + ["manifest.json", "favicon.svg", "assets/img/icon-192.png", "assets/img/apple-touch-icon.png", "data/search.json"]
    h = hashlib.sha256()
    for f in sorted(set(ps + assets + ["manifest.json", "data/search.json"])):
        fp = ROOT / f
        if fp.exists(): h.update(f.encode()); h.update(fp.read_bytes())
    version = h.hexdigest()[:12]
    js = """/* Offline cache for CyberWithMadhav. Generated by tools/build_site.py; edit that file, not this one.
   Pages: network first, falling back to the cache, then to 404.html.
   Styles, scripts, data and images from this site: stale while revalidate.
   Other origins (fonts, APIs) are never touched. */
const VERSION = 'cwm-offline-%s';
const CORE = %s;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('cwm-offline-') && k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); }
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || caches.match('404.html'))));
    return;
  }
  e.respondWith(caches.match(req).then(hit => {
    const net = fetch(req).then(res => {
      if (res.ok && res.type === 'basic') { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); }
      return res;
    });
    return hit ? (net.catch(() => hit), hit) : net;
  }));
});
""" % (version, json.dumps(core, indent=0).replace("\n", " "))
    write("sw.js", js)


NOT_FOUND_TITLE = "Page not found | CyberWithMadhav"


def not_found():
    t = read("terms.html")
    head = t[:t.index("<body")]
    head = re.sub(r"<title>.*?</title>", f"<title>{NOT_FOUND_TITLE}</title>", head)
    head = re.sub(r'\n\s*<(?:meta property="og:[^"]*"|meta name="twitter:[^"]*"|link rel="canonical")[^>]*>', "", head)
    head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="This page does not exist on CyberWithMadhav.">\n  <meta name="robots" content="noindex">', head)
    head = head.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n  <base href="/cyberwithmadhav/">', 1)
    head = head.replace("base-uri 'none'", "base-uri 'self'")
    head = re.sub(r'\n\s*<link rel="stylesheet" href="assets/css/legal.css">', "", head)
    nav = re.search(r'<header class="nav" id="top">.*?</header>', t, re.S).group(0)
    nav = nav.replace(' active" aria-current="page"', '"')
    nav = patch_nav(nav, "404.html")
    foot = re.search(r'<footer.*?</footer>', t, re.S).group(0)
    body = f"""<body class="v3 nf-page">
  <div class="space" aria-hidden="true">
    <div class="nebula"><i class="n1"></i><i class="n2"></i><i class="n3"></i></div>
    <canvas id="starfield"></canvas>
  </div>
  <a class="skip" href="#main">Skip to content</a>

  {nav}

  <main id="main">
    <section class="nf wrap" aria-labelledby="nf-title">
      <p class="kicker mono">error 404 · not found</p>
      <div class="nf-term card mono" aria-hidden="true">
        <p><span class="g">$</span> curl -I <span id="nf-path">this-page</span></p>
        <p>HTTP/1.1 <span class="r">404 Not Found</span></p>
        <p class="muted">no flag here either</p>
      </div>
      <h1 id="nf-title">This page went missing.</h1>
      <p class="lead muted">The link may be old or mistyped. Ye page exist nahi karta, but everything else is one click away.</p>
      <div class="nf-actions">
        <a class="btn btn-primary" href="index.html">Go to home</a>
        <a class="btn" href="explore.html">Open mission control</a>
        <button class="btn" type="button" id="nf-search">Search the site <span class="mono small" aria-hidden="true">Ctrl+K</span></button>
      </div>
      <ul class="nf-links clean">
        <li><a href="explore.html">Explore all pages</a></li>
        <li><a href="index.html#cheatsheets">Cheat sheets</a></li>
        <li><a href="ctf.html">CTF Arena</a></li>
        <li><a href="prompts.html">Prompts</a></li>
        <li><a href="cyberlaw.html">Cyber Law</a></li>
      </ul>
      <p class="small muted">Lost money to a scam? Call <a href="tel:1930">1930</a> or report at <a href="https://cybercrime.gov.in" target="_blank" rel="noopener">cybercrime.gov.in</a>.</p>
    </section>
  </main>

  {foot}

  <script src="assets/js/space.js" defer></script>
  <script src="assets/js/pages.js" defer></script>
  <script src="assets/js/notfound.js" defer></script>
  <script src="assets/js/nav.js" defer></script>
  <script src="assets/js/search.js" defer></script>
  <script src="assets/js/pwa.js" defer></script>
</body>
</html>
"""
    write("404.html", head + body)


def main():
    for p in pages(): patch_page(p)
    not_found()
    search_index()
    sitemap_and_feed()
    subprocess.run(["python3", str(ROOT / "tools" / "csp_hash.py")], check=True)  # hashes first, so the sw version covers the final pages
    service_worker()


if __name__ == "__main__":
    main()
