#!/usr/bin/env python3
"""Build the blog from tools/content/blog_src.py. Run from the repo root after make_page.py:
    python3 tools/build_blog.py && python3 tools/build_legal.py && python3 tools/build_site.py
(build_site.py adds the shared head tags, nav, search index, sitemap, feed and service worker, and hashes the CSP.)
Share images: node tools/render_blog_og.mjs (reads tools/og/blog-og.json written here).

URL scheme: flat files in the site root (blog.html, blog-<slug>.html) with relative links, so the same files work on
the github.io project URL (/cyberwithmadhav/) and on a domain root (Hostinger). When the site moves to its own
domain, keep these names (or add redirects) so links in search results and shares keep working.
It writes:
  blog.html, blog-<slug>.html, assets/js/i18n/post-<slug>.js (Hinglish text for each post),
  the "Latest from the blog" block in index.html, the Related guides block in scams.html and cyberlaw.html,
  the post titles inside assets/js/i18n-dict.js, data/blog.json and tools/og/blog-og.json."""
import html, json, math, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools" / "content"))
import make_page  # noqa: E402
from blog_src import POSTS, CAT_HI  # noqa: E402

BASE = make_page.BASE
E = lambda s: html.escape(s, quote=True)
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def nice(d):
    y, m, dd = map(int, d.split("-")); return f"{dd} {MONTHS[m - 1]} {y}"


def iso_ts(d): return d + "T09:00:00+05:30"


def words(h): return len(re.sub(r"<[^>]+>", " ", h).split())


def minutes(p): return max(1, math.ceil((words(p["quick"]) + sum(words(b) for _, _, b in p["sections"])) / 200))


def cat_key(c): return "cat." + re.sub(r"[^a-z]+", "-", c.lower()).strip("-")


def fname(p): return f"blog-{p['slug']}.html"


def by_slug(s): return next(p for p in POSTS if p["slug"] == s)


POSTS_SORTED = sorted(POSTS, key=lambda p: (p["date"], p["slug"]), reverse=True)


def card(p, level="h3"):
    return f"""        <article class="bp-card" data-cat="{E(p['category'])}">
          <p class="bp-cat mono" data-i18n="{cat_key(p['category'])}">{E(p['category'])}</p>
          <{level} class="bp-card-t"><a href="{fname(p)}" data-i18n="blogpost.{p['slug']}.t">{E(p['title'])}</a></{level}>
          <p class="muted small" data-i18n="blogpost.{p['slug']}.d">{E(p['lead'])}</p>
          <p class="bp-meta small muted"><time datetime="{p['date']}">{nice(p['date'])}</time> · {minutes(p)} <span data-i18n="blog.min">min read</span></p>
        </article>"""


AUTHOR_IMG = '<img src="assets/img/madhav-square.jpg" width="{s}" height="{s}" alt="Madhav Pandya, cybersecurity educator from Mumbai" loading="lazy" decoding="async">'


def post_main(p):
    secs = p["sections"]
    toc = "\n".join(f'            <li><a href="#{sid}" data-i18n="post.s.{sid}.h">{E(h)}</a></li>' for sid, h, _ in secs)
    body = "\n".join(f"""      <section class="bp-sec" id="{sid}" aria-labelledby="{sid}-h">
        <h2 id="{sid}-h" data-i18n="post.s.{sid}.h">{E(h)}</h2>
        <div data-i18n="post.s.{sid}.b">{b.strip()}</div>
      </section>""" for sid, h, b in secs)
    src = "\n".join(f'          <li><a href="{E(u)}"{"" if u.startswith("tel:") else " target=\"_blank\" rel=\"noopener\""}>{E(t)}</a></li>' for t, u in p["sources"])
    rel = "\n".join(card(by_slug(s), "h3") for s in p["related"])
    hubs = " · ".join(f'<a href="{h}">{E(t)}</a>' for h, t in p["hubs"])
    tags = "".join(f'<span class="tag">{E(t)}</span>' for t in p["tags"])
    return f"""  <main id="main" tabindex="-1">
    <article class="bp-post wrap" aria-labelledby="p-title">
      <nav class="bp-crumbs small muted" aria-label="Breadcrumb">
        <a href="index.html" data-i18n="blog.home">Home</a> <span aria-hidden="true">/</span> <a href="blog.html">Blog</a> <span aria-hidden="true">/</span> <span aria-current="page" data-i18n="blogpost.{p['slug']}.s">{E(p['short'])}</span>
      </nav>
      <p class="bp-cat mono" data-i18n="{cat_key(p['category'])}">{E(p['category'])}</p>
      <h1 id="p-title" data-i18n="post.title">{E(p['title'])}</h1>
      <p class="lead" data-i18n="post.lead">{E(p['lead'])}</p>
      <div class="bp-byline small muted">
        {AUTHOR_IMG.format(s=40).replace('loading="lazy"', 'loading="eager"')}
        <p><span data-i18n="blog.by">By</span> <a href="about.html">Madhav Pandya</a> · <span data-i18n="blog.published">Published</span> <time datetime="{p['date']}">{nice(p['date'])}</time> · <span data-i18n="blog.reviewed">Last reviewed</span> <time datetime="{p['reviewed']}">{nice(p['reviewed'])}</time> · {minutes(p)} <span data-i18n="blog.min">min read</span></p>
      </div>
      <div class="tags tags-row bp-tags">{tags}</div>

      <aside class="bp-glass bp-quick" aria-labelledby="quick-h">
        <h2 id="quick-h" data-i18n="blog.quick">Quick answer</h2>
        <p data-i18n="post.quick">{p['quick']}</p>
      </aside>

      <nav class="bp-glass bp-toc" aria-labelledby="toc-h">
        <h2 id="toc-h" data-i18n="blog.contents">Contents</h2>
        <ol>
{toc}
        </ol>
      </nav>

{body}

      <aside class="bp-glass bp-sources" aria-labelledby="src-h">
        <h2 id="src-h" data-i18n="blog.sources">Official sources</h2>
        <ul>
{src}
        </ul>
        <p class="small muted" data-i18n="blog.sources.note">Links open the official sites. Procedures and rules can change, so check them before you rely on this post.</p>
      </aside>

      <aside class="bp-glass bp-author" aria-label="About the author">
        {AUTHOR_IMG.format(s=96)}
        <p data-i18n="blog.author"><strong>Madhav Pandya</strong> explains cybersecurity and scam awareness in plain English and Hinglish. He is the founder of CyberWithMadhav and is studying law and cloud security. <a href="about.html">About Madhav Pandya</a></p>
      </aside>

      <section class="bp-related" aria-labelledby="rel-h">
        <h2 id="rel-h" data-i18n="blog.related">Related guides</h2>
        <div class="bp-grid">
{rel}
        </div>
        <p class="small bp-hubs"><span data-i18n="blog.more">More on this site:</span> {hubs}</p>
      </section>

      <p class="small muted bp-disclaimer" data-i18n="blog.disclaimer">Educational content, not legal advice. Check official sources before you rely on it. If you have lost money, call <a href="tel:1930">1930</a> now. <a href="terms.html">Terms</a></p>
    </article>
  </main>"""


def post_head(p):
    url = BASE + fname(p); img = BASE + f"assets/img/blog/{p['slug']}.png"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BlogPosting", "@id": url + "#post", "mainEntityOfPage": url, "headline": p["title"], "description": p["desc"],
         "image": img, "datePublished": iso_ts(p["date"]), "dateModified": iso_ts(p["reviewed"]), "inLanguage": "en-IN",
         "articleSection": p["category"], "keywords": p["keywords"],
         "author": {"@type": "Person", "@id": BASE + "about.html#person", "name": "Madhav Pandya", "url": BASE + "about.html"},
         "publisher": {"@type": "Organization", "@id": BASE + "#org", "name": "CyberWithMadhav", "logo": {"@type": "ImageObject", "url": BASE + "assets/img/apple-touch-icon.png"}},
         "isPartOf": {"@id": BASE + "blog.html#blog"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": BASE + "blog.html"},
            {"@type": "ListItem", "position": 3, "name": p["title"]}]}]}
    return (f'  <link rel="alternate" type="application/rss+xml" title="CyberWithMadhav" href="feed.xml">\n'
            f'  <meta property="article:published_time" content="{iso_ts(p["date"])}">\n'
            f'  <meta property="article:modified_time" content="{iso_ts(p["reviewed"])}">\n'
            f'  <meta property="article:author" content="{BASE}about.html">\n'
            f'  <meta property="article:section" content="{E(p["category"])}">\n'
            f'  <script type="application/ld+json">\n  {json.dumps(ld, ensure_ascii=False)}\n  </script>')


def listing_main():
    used = [c for c in dict.fromkeys(p["category"] for p in POSTS_SORTED)]
    chips = ['<button type="button" class="chip" data-cat="all" aria-pressed="true"><span data-i18n="blog.all">All</span> <span class="n">%d</span></button>' % len(POSTS)]
    chips += [f'<button type="button" class="chip" data-cat="{E(c)}" aria-pressed="false"><span data-i18n="{cat_key(c)}">{E(c)}</span> <span class="n">{sum(p["category"] == c for p in POSTS)}</span></button>' for c in used]
    cards = "\n".join(card(p, "h2") for p in POSTS_SORTED)
    return f"""  <main id="main" tabindex="-1">
    <section class="page-hero bp-hero" aria-labelledby="p-title">
      <div class="wrap">
        <p class="kicker mono"><span class="prompt">$</span> ls ~/blog</p>
        <h1 id="p-title">Blog</h1>
        <p class="lead" data-i18n="blog.sub">Scams, cyber law and beginner cybersecurity, in plain English and Hinglish.</p>
        <p class="small muted" data-i18n="blog.subnote">Every post links to the official source and shows when it was last reviewed. Lost money right now? Call <a href="tel:1930">1930</a>.</p>
      </div>
    </section>
    <section class="section bp-list" aria-label="Posts">
      <div class="wrap">
        <div class="chips bp-chips" role="group" aria-label="Filter posts by category" data-i18n-attr="aria-label:blog.filter">
          {"".join(chips)}
        </div>
        <p class="sr-only" id="bp-count" aria-live="polite"></p>
        <div class="bp-grid" id="bp-grid">
{cards}
        </div>
        <p class="small muted bp-rss"><span data-i18n="blog.rss">Prefer a reader app? Subscribe to the</span> <a href="feed.xml">RSS feed</a>.</p>
      </div>
    </section>
  </main>"""


def listing_head():
    ld = {"@context": "https://schema.org", "@type": "Blog", "@id": BASE + "blog.html#blog", "name": "CyberWithMadhav Blog", "url": BASE + "blog.html",
          "inLanguage": "en-IN", "publisher": {"@id": BASE + "#org"},
          "blogPost": [{"@type": "BlogPosting", "@id": BASE + fname(p) + "#post", "headline": p["title"], "url": BASE + fname(p), "datePublished": iso_ts(p["date"])} for p in POSTS_SORTED]}
    return ('  <link rel="alternate" type="application/rss+xml" title="CyberWithMadhav" href="feed.xml">\n'
            f'  <script type="application/ld+json">\n  {json.dumps(ld, ensure_ascii=False)}\n  </script>')


def page_dict(p):
    d = {"post.title": p["hi"]["title"], "post.lead": p["hi"]["lead"], "post.quick": p["hi"]["quick"]}
    for (sid, _, _), (h, b) in zip(p["sections"], p["hi"]["sections"]):
        d[f"post.s.{sid}.h"] = h; d[f"post.s.{sid}.b"] = b.strip()
    return d


def post_titles_dict():
    d = {}
    for p in POSTS:
        d[f"blogpost.{p['slug']}.t"] = p["hi"]["title"]; d[f"blogpost.{p['slug']}.d"] = p["hi"]["lead"]
        d[f"blogpost.{p['slug']}.s"] = p["hi"].get("short", p["short"])
    for c, h in CAT_HI.items(): d[cat_key(c)] = h
    return d


def write(path, s):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != s:
        path.write_text(s, encoding="utf-8"); print("wrote", path.relative_to(ROOT))


def splice(path, start, end, block, anchor=None):
    s = (ROOT / path).read_text(encoding="utf-8")
    if start in s:
        a = s.index(start); b = s.index(end) + len(end)
        s2 = s[:a] + start + "\n" + block + "\n    " + end + s[b:]
    elif anchor and anchor in s:
        s2 = s.replace(anchor, "    " + start + "\n" + block + "\n    " + end + "\n" + anchor, 1)
    else:
        print("skip splice", path); return
    write(path, s2)


def main():
    head, nav, foot, tail = make_page.shell()
    for p in POSTS:
        spec = {"file": fname(p), "title": p["title"] + " | CyberWithMadhav", "desc": p["desc"], "og": p["title"], "ogdesc": p["desc"],
                "keywords": "", "body": "blog-page bp-post-page", "css": ["pages.css", "blog.css"], "js": ["blog.js", f"i18n/post-{p['slug']}.js"],
                "ogtype": "article", "foot": "Educational content, not legal advice. Check official sources.",
                "main": post_main(p), "head_html": post_head(p)}
        make_page.build(spec, head, nav, foot, tail)
        write(f"assets/js/i18n/post-{p['slug']}.js", "/* Hinglish text for %s. Generated by tools/build_blog.py from tools/content/blog_src.py. */\nwindow.CWM_I18N_PAGE = %s;\n"
              % (fname(p), json.dumps(page_dict(p), ensure_ascii=False, indent=1)))
    spec = {"file": "blog.html", "title": "Cybersecurity Blog in Hinglish | CyberWithMadhav",
            "desc": "Scam alerts, Indian cyber law explained and beginner cybersecurity guides in plain English and Hinglish, by Madhav Pandya.",
            "og": "CyberWithMadhav Blog: scams, cyber law and cybersecurity in Hinglish",
            "ogdesc": "Step by step guides on reporting cyber fraud, the digital arrest scam and UPI scams, with official sources.",
            "keywords": "", "body": "blog-page bp-list-page", "css": ["pages.css", "blog.css"], "js": ["blog.js"],
            "foot": "Educational content, not legal advice. Check official sources.", "main": listing_main(), "head_html": listing_head()}
    make_page.build(spec, head, nav, foot, tail)

    # home: Latest from the blog (3 newest)
    latest = "\n".join(card(p) for p in POSTS_SORTED[:3])
    block = f"""    <section id="blog-latest" class="section" aria-labelledby="blog-latest-title">
      <div class="wrap">
        <header class="section-head reveal">
          <p class="kicker mono">latest / blog</p>
          <h2 id="blog-latest-title" data-i18n="home.blog.h">Latest from the blog</h2>
          <p class="muted" data-i18n="home.blog.p">Step by step guides on scams and cyber law, with official sources, in plain English and Hinglish.</p>
        </header>
        <div class="bp-grid">
{latest}
        </div>
        <p class="bp-all"><a class="btn btn-ghost small" href="blog.html" data-i18n="home.blog.all">All blog posts →</a></p>
      </div>
    </section>"""
    splice("index.html", "<!-- blog:start -->", "<!-- blog:end -->", block)
    s = (ROOT / "index.html").read_text(encoding="utf-8")
    if 'href="assets/css/blog.css"' not in s:
        write("index.html", s.replace('<link rel="stylesheet" href="assets/css/explore.css">', '<link rel="stylesheet" href="assets/css/explore.css">\n  <link rel="stylesheet" href="assets/css/blog.css">', 1))

    # hubs link down to their posts
    rel = "\n".join(f'          <li><a href="{fname(p)}" data-i18n="blogpost.{p["slug"]}.t">{E(p["title"])}</a></li>' for p in POSTS_SORTED)
    hub = f"""    <section class="section bp-hub" aria-labelledby="hub-rel-h">
      <div class="wrap">
        <h2 id="hub-rel-h" class="h3" data-i18n="blog.related">Related guides</h2>
        <ul class="bp-hub-list">
{rel}
        </ul>
        <p class="small"><a href="blog.html" data-i18n="home.blog.all">All blog posts →</a></p>
      </div>
    </section>"""
    for page in ("scams.html", "cyberlaw.html"):
        splice(page, "<!-- blog-related:start -->", "<!-- blog-related:end -->", hub, anchor="  </main>")

    # post titles for the Hinglish dictionary
    dpath = ROOT / "assets/js/i18n-dict.js"
    d = dpath.read_text(encoding="utf-8")
    blk = "/* blog:start (generated by tools/build_blog.py) */\nObject.assign(window.CWM_I18N.hi, %s);\n/* blog:end */" % json.dumps(post_titles_dict(), ensure_ascii=False, indent=1)
    d2 = re.sub(r"/\* blog:start.*?/\* blog:end \*/", lambda m: blk, d, flags=re.S) if "/* blog:start" in d else d.rstrip() + "\n" + blk + "\n"
    write("assets/js/i18n-dict.js", d2)

    write("data/blog.json", json.dumps([{"slug": p["slug"], "file": fname(p), "title": p["title"], "desc": p["desc"], "category": p["category"],
                                         "date": p["date"], "reviewed": p["reviewed"], "og_alt": p["og_alt"], "minutes": minutes(p)} for p in POSTS_SORTED],
                                       ensure_ascii=False, indent=1) + "\n")
    write("tools/og/blog-og.json", json.dumps([{"slug": p["slug"], "title": p["title"], "category": p["category"]} for p in POSTS], ensure_ascii=False, indent=1) + "\n")
    for f in ["blog.html"] + [fname(p) for p in POSTS] + ["assets/js/i18n-dict.js"]:
        t = (ROOT / f).read_text(encoding="utf-8")
        assert "\u2014" not in t and "\u2013" not in t, f


if __name__ == "__main__":
    main()
