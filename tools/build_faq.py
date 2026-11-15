#!/usr/bin/env python3
"""Build faq.html, the FAQ search-index entries and Hinglish strings.

Run from the repo root after (or before) build_blog.py:
    python3 tools/build_faq.py && python3 tools/build_site.py
Idempotent. Validates that every guide file exists, JSON-LD parses, the question
count matches, titles and descriptions stay within SEO limits, and there are no
em or en dashes.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "content"))
import make_page  # noqa: E402
from faq_src import G, SECTIONS  # noqa: E402

BASE = make_page.BASE
E = lambda s: html.escape(s, quote=True)
EM = "\u2014"
EN = "\u2013"
TITLE = "FAQ: Scams, Safety and Cyber Careers in India | CyberWithMadhav"
DESC = "Plain answers on UPI fraud, 1930, passwords, cybersecurity careers and Indian cyber law. Each answer links to a full guide on CyberWithMadhav."
OG = "FAQ: Scams, Safety and Cyber Careers in India"
OGDESC = "Short, plain answers on UPI fraud, 1930, passwords, cybersecurity careers and Indian cyber law. Each one leads to a full guide."
KEYWORDS = "cybersecurity faq india, upi fraud 1930, cybercrime.gov.in, digital arrest scam, otp scam, password manager, 2FA, cybersecurity career india, IT Act 2000, DPDP Rules, deepfake scam"


def plain(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def dash_ok(s, where):
    if EM in s or EN in s:
        raise SystemExit(f"em or en dash in {where}")


def blog(slug):
    return f"blog-{slug}.html"


def items():
    for sec in SECTIONS:
        for it in sec["items"]:
            yield sec, it


def validate():
    n = 0
    seen = set()
    for sec, it in items():
        n += 1
        if it["id"] in seen:
            raise SystemExit("duplicate id " + it["id"])
        seen.add(it["id"])
        for key in ("q", "a", "hi_q", "hi_a", "h", "hi"):
            val = it[key] if key in it else sec[key if key != "hi" else "hi"]
            dash_ok(val, f"{it['id']}.{key}")
        guide = it["guide"]
        if guide not in G:
            raise SystemExit("missing guide title " + guide)
        path = ROOT / blog(guide)
        if not path.exists():
            raise SystemExit("missing guide file " + blog(guide))
        for rel in it["related"]:
            if rel not in G:
                raise SystemExit("missing related title " + rel)
            if not (ROOT / blog(rel)).exists():
                raise SystemExit("missing related file " + blog(rel))
        for href, _t in it.get("extra") or []:
            if not href.startswith(("https:", "mailto:", "tel:")) and not (ROOT / href.split("#")[0]).exists():
                raise SystemExit("missing extra link " + href)
        aq, aa = plain(it["q"]), plain(it["a"])
        if not (2 <= len(aa.split(".")) or True):
            pass
        words = len(aa.split())
        if words < 20 or words > 140:
            print("warn: answer length", it["id"], words, "words")
    if n < 30 or n > 40:
        raise SystemExit(f"need 30 to 40 questions, got {n}")
    if len(TITLE) > 70:
        raise SystemExit("title too long: %d" % len(TITLE))
    left = TITLE.split(" | ")[0]
    if len(left) > 60:
        raise SystemExit("title left part too long: %d" % len(left))
    if len(DESC) > 160:
        raise SystemExit("meta description too long: %d" % len(DESC))
    return n


def guide_link(slug, cls="faq-guide"):
    title = G[slug]
    return (f'<p class="{cls}"><a href="{blog(slug)}">'
            f'<span data-i18n="faq.read">Read the full guide</span>: '
            f'<span data-i18n="blogpost.{slug}.t">{E(title)}</span></a></p>')


def related_html(it):
    links = []
    for slug in it["related"]:
        links.append(f'<a href="{blog(slug)}" data-i18n="blogpost.{slug}.t">{E(G[slug])}</a>')
    for href, label in it.get("extra") or []:
        links.append(f'<a href="{E(href)}">{E(label)}</a>')
    if not links:
        return ""
    return ('<p class="small muted faq-more"><span data-i18n="faq.more">Related guides:</span> '
            + " · ".join(links) + "</p>")


def details_html(it):
    return f"""          <details class="card" id="q-{E(it['id'])}">
            <summary>
              <h3 data-i18n="faq.q.{it['id']}">{E(it['q'])}</h3>
            </summary>
            <div class="ans">
              <p data-i18n="faq.a.{it['id']}">{it['a']}</p>
              {guide_link(it['guide'])}
              {related_html(it)}
            </div>
          </details>"""


def main_html():
    jumps = []
    secs = []
    for sec in SECTIONS:
        jumps.append(f'<a class="chip" href="#{sec["id"]}" data-i18n="faq.sec.{sec["id"]}">{E(sec["h"])}</a>')
        body = "\n".join(details_html(it) for it in sec["items"])
        secs.append(f"""    <section class="section faq-sec" id="{sec["id"]}" aria-labelledby="{sec["id"]}-h">
      <div class="wrap faq-wrap">
        <h2 id="{sec["id"]}-h" data-i18n="faq.sec.{sec["id"]}">{E(sec["h"])}</h2>
        <div class="faq" data-sec="{sec["id"]}">
{body}
        </div>
      </div>
    </section>""")
    return f"""  <main id="main" tabindex="-1">
    <section class="page-hero faq-hero" aria-labelledby="p-title">
      <div class="wrap">
        <nav class="bp-crumbs small muted" aria-label="Breadcrumb">
          <a href="index.html" data-i18n="blog.home">Home</a> <span aria-hidden="true">/</span> <span aria-current="page" data-i18n="nav.faq">FAQ</span>
        </nav>
        <p class="kicker mono"><span class="prompt">$</span> man faq</p>
        <h1 id="p-title" data-i18n="faq.h1">Questions people actually ask</h1>
        <p class="lead" data-i18n="faq.lead">Short, plain answers on scams, online safety, cybersecurity careers and Indian cyber law. Each one leads you to a full guide.</p>
        <p class="small muted" data-i18n="faq.sub">Lost money right now? Call <a href="tel:1930">1930</a> or report at <a href="https://cybercrime.gov.in" target="_blank" rel="noopener">cybercrime.gov.in</a>.</p>
        <div class="faq-tools">
          <label class="sr-only" for="faq-q" data-i18n="faq.search.lbl">Search questions</label>
          <input id="faq-q" type="search" placeholder="Search questions..." autocomplete="off" data-i18n-attr="placeholder:faq.search.ph">
          <p class="small muted" id="faq-count" aria-live="polite"></p>
        </div>
        <nav class="faq-jump chips" aria-label="FAQ sections">
          {"".join(jumps)}
        </nav>
      </div>
    </section>
{chr(10).join(secs)}
    <section class="section faq-end" aria-label="More on this site">
      <div class="wrap faq-wrap">
        <p class="small muted" data-i18n="faq.browse">Want a longer read? Browse the <a href="blog.html">blog</a> or <a href="explore.html">explore every page</a>.</p>
      </div>
    </section>
  </main>"""


def jsonld():
    questions = []
    for _sec, it in items():
        questions.append({
            "@type": "Question",
            "@id": BASE + "faq.html#q-" + it["id"],
            "name": it["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": plain(it["a"]),
            },
        })
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": BASE + "faq.html#faq",
        "url": BASE + "faq.html",
        "name": OG,
        "description": DESC,
        "inLanguage": "en-IN",
        "isPartOf": {"@id": BASE + "#website"},
        "mainEntity": questions,
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "FAQ", "item": BASE + "faq.html"},
        ],
    }
    return (f'  <script type="application/ld+json">\n  {json.dumps(faq, ensure_ascii=False, indent=2)}\n  </script>\n'
            f'  <script type="application/ld+json">\n  {json.dumps(crumbs, ensure_ascii=False, indent=2)}\n  </script>')


def i18n_dict():
    d = {
        "faq.h1": "Aapke sawaal, seedhe jawaab",
        "faq.lead": "Scams, online safety, cybersecurity careers aur Indian cyber law pe chhote, simple jawaab. Har jawaab aapko ek poori guide tak le jaata hai.",
        "faq.sub": "Abhi paisa gaya hai? <a href=\"tel:1930\">1930</a> pe call karo ya <a href=\"https://cybercrime.gov.in\" target=\"_blank\" rel=\"noopener\">cybercrime.gov.in</a> pe report karo.",
        "faq.search.lbl": "Sawaal dhoondho",
        "faq.search.ph": "Sawaal dhoondho...",
        "faq.read": "Poori guide padho",
        "faq.more": "Related guides:",
        "faq.browse": "Lamba padhna hai? <a href=\"blog.html\">Blog</a> dekho ya <a href=\"explore.html\">har page explore karo</a>.",
        "faq.empty": "Is search se koi sawaal nahi mila. Alag words try karo, ya saare sawaal dekhne ke liye search saaf karo.",
        "faq.shown": "{n} sawaal dikh rahe hain",
    }
    for sec in SECTIONS:
        d[f"faq.sec.{sec['id']}"] = sec["hi"]
        for it in sec["items"]:
            d[f"faq.q.{it['id']}"] = it["hi_q"]
            d[f"faq.a.{it['id']}"] = it["hi_a"]
    return d


def splice_i18n():
    path = ROOT / "assets/js/i18n-dict.js"
    d = path.read_text(encoding="utf-8")
    blk = ("/* faq:start (generated by tools/build_faq.py) */\n"
           "Object.assign(window.CWM_I18N.hi, %s);\n"
           "/* faq:end */" % json.dumps(i18n_dict(), ensure_ascii=False, indent=1))
    if "/* faq:start" in d:
        d2 = re.sub(r"/\* faq:start.*?/\* faq:end \*/", lambda m: blk, d, flags=re.S)
    else:
        # keep it before the generated blog block so rebuilds do not collide
        if "/* blog:start" in d:
            d2 = d.replace("/* blog:start", blk + "\n/* blog:start", 1)
        else:
            d2 = d.rstrip() + "\n" + blk + "\n"
    if d2 != d:
        path.write_text(d2, encoding="utf-8")
        print("wrote assets/js/i18n-dict.js (faq strings)")


def search_index():
    out = []
    for sec, it in items():
        out.append({
            "k": "FAQ",
            "t": it["q"],
            "s": "FAQ · " + sec["h"],
            "u": "faq.html#q-" + it["id"],
            "x": plain(it["a"])[:300],
        })
    path = ROOT / "data" / "faq_index.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("wrote data/faq_index.json:", len(out), "entries")


def check_output(n):
    page = (ROOT / "faq.html").read_text(encoding="utf-8")
    dash_ok(page, "faq.html")
    details = re.findall(r'<details class="card" id="q-([^"]+)">', page)
    h3 = re.findall(r"<h3 data-i18n=\"faq\.q\.[^\"]+\">(.*?)</h3>", page)
    if len(details) != n or len(h3) != n:
        raise SystemExit(f"visible Q count mismatch: details={len(details)} h3={len(h3)} expected={n}")
    blocks = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', page, re.S)
    types = []
    faq_n = 0
    for raw in blocks:
        data = json.loads(raw)
        types.append(data.get("@type"))
        if data.get("@type") == "FAQPage":
            ents = data["mainEntity"]
            faq_n = len(ents)
            for i, ent in enumerate(ents):
                q = h3[i]
                # visible answer is the first <p data-i18n="faq.a...."> inside that details
                vis_a = re.search(rf'id="q-{re.escape(details[i])}".*?<p data-i18n="faq\.a\.[^"]+">(.*?)</p>', page, re.S)
                if not vis_a:
                    raise SystemExit("missing visible answer for " + details[i])
                if ent["name"] != plain(q):
                    raise SystemExit(f"JSON-LD question mismatch for {details[i]}: {ent['name']!r} vs {plain(q)!r}")
                if ent["acceptedAnswer"]["text"] != plain(vis_a.group(1)):
                    raise SystemExit(f"JSON-LD answer mismatch for {details[i]}")
    if "FAQPage" not in types or "BreadcrumbList" not in types:
        raise SystemExit("missing JSON-LD types: " + ", ".join(types))
    if faq_n != n:
        raise SystemExit(f"JSON-LD Q count {faq_n} != {n}")
    if 'rel="canonical" href="https://www.cyberwithmadhav.com/faq.html"' not in page:
        raise SystemExit("bad canonical")
    if "<h1" in page and page.count("<h1") != 1:
        raise SystemExit("expected exactly one H1")
    # every blog link in the page must exist
    for href in re.findall(r'href="(blog-[^"#]+)"', page):
        if not (ROOT / href).exists():
            raise SystemExit("broken blog link in faq.html: " + href)
    print("validated faq.html:", n, "questions, JSON-LD matches visible Q&A")


def main():
    n = validate()
    head = jsonld()
    spec = {
        "file": "faq.html",
        "title": TITLE,
        "desc": DESC,
        "og": OG,
        "ogdesc": OGDESC,
        "keywords": KEYWORDS,
        "body": "faq-page",
        "css": ["pages.css", "blog.css", "faq.css"],
        "js": ["faq.js"],
        "foot": "Content is for awareness and education, not legal advice.",
        "main": main_html(),
        "head_html": head,
    }
    make_page.build(spec, *make_page.shell())
    splice_i18n()
    search_index()
    check_output(n)
    print("faq: %d questions in %d sections" % (n, len(SECTIONS)))


if __name__ == "__main__":
    main()
