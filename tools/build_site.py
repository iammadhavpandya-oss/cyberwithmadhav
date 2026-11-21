#!/usr/bin/env python3
"""Site wide build step. Run after build_pages_data.py and build_legal.py. It runs csp_hash.py itself.

It is idempotent and does five things:
  1. Head tags on every page: og:image (1200x630), twitter:image, web app manifest and apple touch icon.
  2. Shared scripts on every page: assets/js/pwa.js, plus assets/js/search.js on pages other than index.html, plus the GoatCounter visitor-count script.
  3. data/search.json: the Ctrl+K search index built from every page and the data files.
  4. sitemap.xml (every public page) and feed.xml (RSS 2.0).
  5. sw.js (offline cache with a content hash version) and 404.html.
It also writes robots.txt (and keeps /tools/, /backend/ and /docs/ out of search) and adds basic JSON-LD on pages that still have none.
CSP is also patched so GoatCounter can load (https://gc.zgo.at) and send a count (https://cyberwithmadhav.goatcounter.com).
"""
import hashlib, html, json, re, subprocess
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BASE = "https://www.cyberwithmadhav.com/"
OG_IMG = BASE + "assets/img/og-image.png"
OG_ALT = "CyberWithMadhav: Cybersecurity in plain English and Hinglish."

# Public pages in nav order. Pages that do not exist yet are skipped.
PAGES = ["index.html", "explore.html", "commands.html", "scams.html", "game.html", "soc.html", "owasp.html", "terminal.html", "daily.html", "progress.html",
         "ctf.html", "prompts.html", "cyberlaw.html", "blog.html", "faq.html", "start-here.html", "uses.html", "collaborate.html", "shop.html", "now.html",
         "about.html", "terms.html", "privacy.html"]
PRIORITY = {"index.html": "1.0", "faq.html": "0.9", "start-here.html": "0.9", "now.html": "0.5", "terms.html": "0.3", "privacy.html": "0.3"}


def blog_posts():
    f = DATA / "blog.json"  # written by build_blog.py, newest first
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


def pages():
    out = [p for p in PAGES if (ROOT / p).exists()]
    if "blog.html" in out:
        i = out.index("blog.html") + 1
        out[i:i] = [b["file"] for b in blog_posts() if (ROOT / b["file"]).exists()]
    return out


def post_date(p, key="published"):
    s = read(p); m = re.search(r'<meta property="article:%s_time" content="([^"]+)"' % key, s)
    return datetime.fromisoformat(m.group(1)) if m else None


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
       ("blog.html", "Blog", "nav-blog", ""),
       ("faq.html", "FAQ", "nav-faq", ""),
       ("shop.html", "Shop", "nav-shop", ""),
       ("ctf.html", "CTF", "nav-ctf", '<span class="nav-ctf-dot" aria-hidden="true"></span>')]
LANG_BTN = ('<button class="lang-toggle" type="button" aria-pressed="false" aria-label="Language: English. Switch to Hinglish" title="Switch to Hinglish">'
            '<span class="lt-ico" aria-hidden="true">Aa</span><span class="lt-label">English</span></button>')
I18N_TAGS = '<script src="assets/js/i18n-dict.js"></script>\n  <script src="assets/js/i18n.js"></script>\n  '
FOOT_LINKS = [("terms.html", "Terms and Conditions", "foot.terms"), ("privacy.html", "Privacy Policy", "foot.privacy"),
              ("index.html", "Back to home", "foot.home"), ("#top", "Back to top ↑", "foot.top"), ("#top", "Back to top &#8593;", "foot.top")]


def nav_links(p):
    post = p.startswith("blog-")  # blog posts live under Blog
    hub = p not in [f for f, _, _, _ in NAV] and p != "404.html" and not post  # every other page lives inside Explore
    out = []
    for f, label, cls, ico in NAV:
        if not (ROOT / f).exists(): continue
        on = f == p or (hub and f == "explore.html") or (post and f == "blog.html")
        attrs = f' class="{cls}{" active" if on else ""}"'
        if f == p: attrs += ' aria-current="page"'
        key = "nav." + label.lower()
        out.append(f'\n        <a href="{f}"{attrs}>{ico}<span data-i18n="{key}">{label}</span></a>')
    return "".join(out)


def patch_nav(s, p):
    m = re.search(r'<nav id="nav-links"[^>]*>.*?</nav>', s, re.S)
    if not m: return s
    nav = m.group(0)
    head = re.match(r'<nav id="nav-links"[^>]*>', nav).group(0)
    pal = re.search(r'\n\s*<button class="pal-btn".*?</button>', nav, re.S)
    tt = re.search(r'\n\s*<button class="theme-toggle".*?</button>', nav, re.S)
    nav = head + nav_links(p) + (pal.group(0) if pal else "") + "\n        " + LANG_BTN + (tt.group(0) if tt else "") + "\n      </nav>"
    return s[:m.start()] + nav + s[m.end():]


def patch_footer(s):
    m = re.search(r'<footer class="footer">.*?</footer>', s, re.S)
    if not m: return s
    f = m.group(0)
    f = re.sub(r'<a href="about\.html"(?: data-i18n="foot\.about")?>About Madhav Pandya</a>(?: · <a href="blog\.html" data-i18n="foot\.blog">Blog</a>)?(?: · <a href="faq\.html" data-i18n="foot\.faq">FAQ</a>)?(?: · <a href="start-here\.html" data-i18n="foot\.start">Start here</a>)?(?: · <a href="collaborate\.html" data-i18n="foot\.collab">Collaborate</a>)?(?: · <a href="shop\.html" data-i18n="foot\.shop">Shop</a>)?',
               '<a href="about.html" data-i18n="foot.about">About Madhav Pandya</a> · <a href="blog.html" data-i18n="foot.blog">Blog</a> · <a href="faq.html" data-i18n="foot.faq">FAQ</a>'
               ' · <a href="start-here.html" data-i18n="foot.start">Start here</a> · <a href="collaborate.html" data-i18n="foot.collab">Collaborate</a> · <a href="shop.html" data-i18n="foot.shop">Shop</a>', f)
    for href, text, key in FOOT_LINKS:
        f = re.sub(r'<a href="%s"(?: data-i18n="[^"]*")?>%s</a>' % (re.escape(href), re.escape(text)), f'<a href="{href}" data-i18n="{key}">{text}</a>', f)
    return s[:m.start()] + f + s[m.end():]


def patch_head(s):
    s = re.sub(r'<html lang="[^"]*"', '<html lang="en-IN"', s, count=1)
    s = re.sub(r'<script src="assets/js/i18n-dict\.js"></script>\s*<script src="assets/js/i18n\.js"></script>\s*', "", s)
    return s.replace('<script src="assets/js/consent.js"></script>', I18N_TAGS + '<script src="assets/js/consent.js"></script>', 1)


def patch_page(p):
    s = read(p)
    s = patch_head(s)
    s = patch_nav(s, p)
    s = patch_footer(s)
    # social image tags: drop old ones, then add one consistent block after og:locale (or og:url)
    s = re.sub(r'\n\s*<meta (?:property="og:image(?::[a-z]+)?"|name="twitter:image(?::alt)?") content="[^"]*">', "", s)
    title, desc = meta(s, "property", "og:title") or title_of(s), meta(s, "property", "og:description") or meta(s, "name", "description")
    post = next((b for b in blog_posts() if b["file"] == p), None)
    if p == "about.html":
        og_img, og_w, og_h, og_alt = BASE + "assets/img/madhav-og.jpg", "1200", "630", "Madhav Pandya, cybersecurity educator from Mumbai"
    elif post and (ROOT / f"assets/img/blog/{post['slug']}.jpg").exists():
        og_img, og_w, og_h, og_alt = BASE + f"assets/img/blog/{post['slug']}.jpg", "1200", "630", post["og_alt"]
    elif post and (ROOT / f"assets/img/blog/{post['slug']}.png").exists():
        og_img, og_w, og_h, og_alt = BASE + f"assets/img/blog/{post['slug']}.png", "1200", "630", post["og_alt"]
    else:
        og_img, og_w, og_h, og_alt = (BASE + "assets/img/og-image.jpg" if (ROOT / "assets/img/og-image.jpg").exists() else OG_IMG), "1200", "630", OG_ALT
    social = (f'\n  <meta property="og:image" content="{og_img}">'
              f'\n  <meta property="og:image:width" content="{og_w}">\n  <meta property="og:image:height" content="{og_h}">'
              f'\n  <meta property="og:image:alt" content="{html.escape(og_alt)}">')
    anchor = re.search(r'\n\s*<meta property="og:locale"[^>]*>', s) or re.search(r'\n\s*<meta property="og:url"[^>]*>', s)
    s = s[:anchor.end()] + social + s[anchor.end():]
    if 'name="twitter:card"' not in s:
        tw = (f'\n  <meta name="twitter:card" content="summary_large_image">'
              f'\n  <meta name="twitter:title" content="{html.escape(title)}">'
              f'\n  <meta name="twitter:description" content="{html.escape(desc)}">')
        a = s.index(social) + len(social); s = s[:a] + tw + s[a:]
    m = re.search(r'\n\s*<meta name="twitter:description"[^>]*>', s)
    s = s[:m.end()] + f'\n  <meta name="twitter:image" content="{og_img}">\n  <meta name="twitter:image:alt" content="{html.escape(og_alt)}">' + s[m.end():]
    # manifest and touch icon after the favicon
    s = re.sub(r'\n\s*<link rel="(?:manifest|apple-touch-icon)"[^>]*>', "", s)
    s = s.replace('<link rel="icon" type="image/svg+xml" href="favicon.svg">',
                  '<link rel="icon" type="image/svg+xml" href="favicon.svg">\n  <link rel="manifest" href="manifest.json">\n  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">', 1)
    # shared scripts before </body>
    s = re.sub(r'\n\s*<script src="assets/js/(?:pwa|search|nav|eggs)\.js(?:\?v=[0-9a-f]+)?" defer></script>', "", s)
    s = re.sub(r'\n\s*<script data-goatcounter="[^"]+"[^>]*></script>', "", s)
    tags = ['<script src="assets/js/nav.js" defer></script>'] + ([] if p == "index.html" else ['<script src="assets/js/search.js" defer></script>']) + ['<script src="assets/js/pwa.js" defer></script>']  # pwa.js loads eggs.js after the load event
    s = s.replace("\n</body>", "".join("\n  " + t for t in tags) + "\n</body>", 1)
    s = re.sub(r"\n\s*<!-- CWM\{.*?-->", "", s)
    s = s.replace("\n</body>", "\n  " + FLAG + "\n  " + GOAT + "\n</body>", 1)
    s = patch_csp(s)
    write(p, version_assets(s))


FLAG = "<!-- CWM{v13w_s0urc3_l1k3_a_d3f3nd3r} You read the source. Nice. Real challenges: https://www.cyberwithmadhav.com/ctf.html -->"
# Cookieless visitor counter. async, after the page's own scripts. count.js already skips localhost and private IPs.
GC_SCRIPT = "https://gc.zgo.at"
GC_COUNT = "https://cyberwithmadhav.goatcounter.com"
GOAT = '<script data-goatcounter="%s/count" async src="%s/count.js"></script>' % (GC_COUNT, GC_SCRIPT)


def patch_csp(s):
    """Allow the GoatCounter script and its count beacon (sendBeacon or image). Idempotent."""
    def add(m):
        csp = m.group(1)
        def script_src(sm):
            cur = sm.group(0)
            return cur if GC_SCRIPT in cur else cur + " " + GC_SCRIPT
        csp = re.sub(r"script-src [^;]+", script_src, csp, count=1)
        def connect_src(sm):
            cur = sm.group(0)
            if GC_COUNT in cur:
                return cur
            return re.sub(r"connect-src 'self'", "connect-src 'self' " + GC_COUNT, cur, count=1)
        csp = re.sub(r"connect-src [^;]+", connect_src, csp, count=1)
        def img_src(sm):
            cur = sm.group(0)
            return cur if GC_COUNT in cur else cur + " " + GC_COUNT
        csp = re.sub(r"img-src [^;]+", img_src, csp, count=1)
        return '<meta http-equiv="Content-Security-Policy" content="%s">' % csp
    return re.sub(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', add, s, count=1)


def asset_hash(rel):
    f = ROOT / rel
    return hashlib.sha256(f.read_bytes()).hexdigest()[:10] if f.exists() else None


def version_assets(s):
    """Add ?v=<content hash> to local CSS and JS so the 1 year browser cache never serves an old file after a deploy."""
    def sub(m):
        h = asset_hash(m.group(2))
        return f'{m.group(1)}="{m.group(2)}' + (f'?v={h}"' if h else '"')
    return re.sub(r'\b(href|src)="(assets/(?:css|js)/[^"?#]+\.(?:css|js))(?:\?v=[0-9a-f]+)?"', sub, s)


def version_eggs():
    """eggs.js loads eggs.css itself; pin that URL to the CSS content hash too."""
    p = ROOT / "assets/js/eggs.js"
    if not p.exists(): return
    s = p.read_text(encoding="utf-8")
    s2 = re.sub(r"assets/css/eggs\.css(?:\?v=[0-9a-f]+)?'", f"assets/css/eggs.css?v={asset_hash('assets/css/eggs.css')}'", s)
    if s2 != s: p.write_text(s2, encoding="utf-8"); print("wrote assets/js/eggs.js (css version)")
    q = ROOT / "assets/js/pwa.js"  # pwa.js injects eggs.js after load; pin that URL to the eggs.js content hash
    t = q.read_text(encoding="utf-8")
    t2 = re.sub(r"assets/js/eggs\.js(?:\?v=[0-9a-f]+)?'", f"assets/js/eggs.js?v={asset_hash('assets/js/eggs.js')}'", t)
    if t2 != t: q.write_text(t2, encoding="utf-8"); print("wrote assets/js/pwa.js (eggs version)")


# ---------- 3: search index ----------
def short_title(t): return re.split(r"\s+\|\s+|:\s", t)[0].strip()


def clip(s, n):
    """Shorten a visible search snippet at a word boundary and mark the cut with an ellipsis."""
    s = s.strip()
    if len(s) <= n: return s
    cut = s[:n - 1].rsplit(" ", 1)[0].rstrip(" ,;:.(")
    return cut + "\u2026"


def search_index():
    out, seen = [], set()

    def add(k, t, s, u, x=""):
        key = (k, t, u)
        if key in seen: return
        seen.add(key); item = {"k": k, "t": t, "s": clip(s, 110), "u": u}
        if x: item["x"] = x[:300]
        out.append(item)

    for p in pages():
        s = read(p)
        name = "Home" if p == "index.html" else short_title(title_of(s))
        add("Blog" if p.startswith("blog-") else "Page", title_of(s).split(" | ")[0] if p.startswith("blog-") else name, meta(s, "name", "description"), p)
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
    for extra in ("commands_index.json", "scams_index.json", "game_index.json", "soc_index.json", "owasp_index.json", "terminal_index.json", "daily_index.json", "faq_index.json"):
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
        lm = post_date(p, "modified") or git_date(p)
        rows.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lm.date().isoformat()}</lastmod>\n    <priority>{PRIORITY.get(p, '0.8')}</priority>\n  </url>")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n")
    items = []
    when = {p: post_date(p) or git_date(p) for p in ps}  # posts use their real publish date
    for p in sorted(ps, key=lambda p: when[p], reverse=True):
        s = read(p); loc = BASE if p == "index.html" else BASE + p
        items.append("    <item>\n"
                     f"      <title>{html.escape(meta(s, 'property', 'og:title') or title_of(s))}</title>\n"
                     f"      <link>{loc}</link>\n      <guid isPermaLink=\"true\">{loc}</guid>\n"
                     f"      <pubDate>{format_datetime(when[p])}</pubDate>\n"
                     f"      <description>{html.escape(meta(s, 'name', 'description'))}</description>\n    </item>")
    latest = max(when.values())
    write("feed.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n  <channel>\n'
          "    <title>CyberWithMadhav</title>\n"
          f"    <link>{BASE}</link>\n"
          f'    <atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>\n'
          "    <description>Cybersecurity in plain English and Hinglish: roadmap, cheat sheets, CTF practice, prompts, cyber law and scam alerts for India.</description>\n"
          "    <language>en-in</language>\n"
          f"    <lastBuildDate>{format_datetime(latest)}</lastBuildDate>\n" + "\n".join(items) + "\n  </channel>\n</rss>\n")



def robots():
    write("robots.txt", "# Hello, curious human. Robots read this file, and so do future defenders.\n"
          "# Nothing is hidden here. The flags live in the CTF Arena: /ctf.html\n"
          "# Found a security issue? /.well-known/security.txt\n"
          "User-agent: *\nAllow: /\n"
          "Disallow: /tools/\nDisallow: /backend/\nDisallow: /docs/\n"
          "Sitemap: %ssitemap.xml\n" % BASE)


# ---------- 5: service worker and 404 ----------
def service_worker():
    ps = pages() + ["404.html"]
    # precache the main pages and only the 6 newest blog posts; other posts are cached when visited (network first)
    newest = [b["file"] for b in blog_posts()][:6]
    pre = [p for p in ps if not p.startswith("blog-") or p in newest]
    # precache the exact versioned URLs the pages request (?v=hash), so offline pages find their CSS and JS
    assets = sorted({m for p in pre if p != "404.html" for m in re.findall(r'(?:src|href)="((?:assets/(?:css|js|fonts)/)[^"?#]+(?:\?v=[0-9a-f]+)?)"', read(p))})
    fonts_css = ROOT / "assets/css/fonts.css"
    if fonts_css.exists():
        for name in re.findall(r'url\(\.\./fonts/([^)]+)\)', fonts_css.read_text(encoding="utf-8")):
            assets.append("assets/fonts/" + name)
        assets = sorted(set(assets))
    imgs = ["assets/img/icon-192.png", "assets/img/apple-touch-icon.png"]
    for extra in ("assets/img/madhav.jpg", "assets/img/madhav-square.jpg", "assets/img/madhav.webp", "assets/img/madhav-square.webp"):
        if (ROOT / extra).exists():
            imgs.append(extra)
    core = ["./"] + pre + assets + ["manifest.json", "favicon.svg"] + imgs + ["data/search.json"]
    h = hashlib.sha256()
    for f in sorted(set(ps + [a.split("?")[0] for a in assets] + ["manifest.json", "data/search.json"])):
        fp = ROOT / f
        if fp.exists(): h.update(f.encode()); h.update(fp.read_bytes())
    version = h.hexdigest()[:12]
    js = """/* Offline cache for CyberWithMadhav. Generated by tools/build_site.py; edit that file, not this one.
   Pages: network first, falling back to the cache, then to 404.html.
   Styles, scripts, data and images from this site: stale while revalidate.
   Other origins (fonts, APIs, GoatCounter) are never intercepted or cached. */
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
  if (req.method !== 'GET' || url.origin !== self.location.origin) return; // pass through cross-origin requests, including GoatCounter count calls
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(res => {
      if (res.status === 200) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); }
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || caches.match('404.html'))));
    return;
  }
  e.respondWith(caches.match(req).then(hit => {
    const net = fetch(req).then(res => {
      if (res.status === 200 && res.type === 'basic') { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); }
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
    head = re.sub(r'\n\s*<script type="application/ld\+json">.*?</script>', "", head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="This page does not exist on CyberWithMadhav.">\n  <meta name="robots" content="noindex">', head)
    head = head.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n  <base href="/">', 1)
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
      <p class="kicker mono">error 404 · packet lost</p>
      <div class="nf-term card mono" aria-hidden="true">
        <p><span class="g">$</span> ping <span id="nf-path">this-page</span></p>
        <p>Request timed out. <span class="r">TTL expired in transit.</span></p>
        <p class="muted">4 packets sent, 0 received, 100% packet loss</p>
        <p><span class="g">$</span> traceroute home</p>
        <p class="muted">1 you · 2 * * * · 3 * * * · 4 index.html <span class="g">found a route</span></p>
        <p class="muted">no flag here either. try view source.</p>
      </div>
      <h1 id="nf-title">This page went missing.</h1>
      <p class="lead muted">The link may be old or mistyped. Ye page exist nahi karta, but everything else is one click away.</p>
      <div class="nf-actions">
        <a class="btn btn-primary" href="index.html">Go to home</a>
        <a class="btn" href="explore.html">Open mission control</a>
        <button class="btn" type="button" id="nf-search">Search the site <span class="mono small" aria-hidden="true">Ctrl+K</span></button>
      </div>
      <ul class="nf-links clean">
        <li><a href="start-here.html">Start here</a></li>
        <li><a href="explore.html">Explore all pages</a></li>
        <li><a href="faq.html">FAQ</a></li>
        <li><a href="blog.html">Blog</a></li>
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
  {FLAG}
  {GOAT}
</body>
</html>
"""
    write("404.html", version_assets(patch_csp(head + body)))


def share_jpegs():
    """Compressed JPEG copies of the 1200x630 PNG share images (WhatsApp skips previews over about 300 KB)."""
    try:
        from PIL import Image
    except ImportError:
        print("PIL missing: share images stay PNG"); return
    for png in sorted((ROOT / "assets/img/blog").glob("*.png")) + [ROOT / "assets/img/og-image.png"]:
        jpg = png.with_suffix(".jpg")
        if png.exists() and (not jpg.exists() or jpg.stat().st_mtime < png.stat().st_mtime):
            Image.open(png).convert("RGB").save(jpg, "JPEG", quality=84, optimize=True, progressive=True); print("wrote", jpg.relative_to(ROOT))



def ensure_basic_schema():
    """Add WebPage or CollectionPage plus breadcrumbs on public pages that still have no JSON-LD."""
    types = {"explore.html": "CollectionPage", "game.html": "LearningResource",
             "shop.html": "CollectionPage"}
    for p in pages():
        s = read(p)
        if "application/ld+json" in s:
            continue
        url = BASE if p == "index.html" else BASE + p
        title = title_of(s)
        name = title.split(" | ")[0].strip() or title
        desc = meta(s, "name", "description") or name
        typ = types.get(p, "WebPage")
        graph = [{"@type": typ, "@id": url + "#page", "url": url, "name": name,
                  "description": desc, "inLanguage": "en-IN",
                  "isPartOf": {"@id": BASE + "#website"}},
                 {"@type": "BreadcrumbList", "itemListElement": [
                     {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
                     {"@type": "ListItem", "position": 2, "name": name, "item": url}]}]
        block = '  <script type="application/ld+json">\n  ' + json.dumps(
            {"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "\n  </script>\n"
        if "</head>" not in s:
            raise SystemExit("no </head> in " + p)
        write(p, s.replace("</head>", block + "</head>", 1))
        print("schema added:", p)


def main():
    share_jpegs()
    version_eggs()
    ensure_basic_schema()
    for p in pages(): patch_page(p)
    not_found()
    search_index()
    sitemap_and_feed()
    robots()
    subprocess.run(["python3", str(ROOT / "tools" / "csp_hash.py")], check=True)  # hashes first, so the sw version covers the final pages
    service_worker()


if __name__ == "__main__":
    main()
