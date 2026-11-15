"""Loads the extra blog posts written in the light text format in tools/content/posts/*.txt and
turns them into the same dicts as blog_src.POSTS. Format (one post per block, blocks start with '=== slug'):

=== my-slug
title: Full title
short: Breadcrumb label
desc: Meta description under 160 characters
lead: One or two sentence intro
cat: Category name
order: 3                      (series position, optional)
series: Beginner journey      (optional, links prev and next posts of the same series)
updated: Updated November 2026 (optional note shown under the byline)
tags: a, b, c
kw: keyword one; keyword two
hi: Hinglish title (optional)
related: slug-a, slug-b
hubs: index.html#roadmap|Roadmap on the home page; ctf.html|CTF Arena
src: Source title|https://url
quick: Quick answer text (inline markup allowed)
takeaways:
- point one
- point two
## section-id | Section heading
Paragraphs, '- ' bullet lists, '1. ' numbered lists, ``` code blocks ```, **bold**, `code`, [text](url).
"""
import html, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
E = lambda s: html.escape(s, quote=False)


def inline(s):
    out, pos = [], 0
    for m in re.finditer(r"`([^`]+)`", s):
        out.append(_fmt(s[pos:m.start()])); out.append("<code>" + E(m.group(1)) + "</code>"); pos = m.end()
    out.append(_fmt(s[pos:]))
    return "".join(out)


def _fmt(s):
    s = E(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

    def link(m):
        t, u = m.group(1), m.group(2)
        ext = u.startswith("http")
        return f'<a href="{u}"' + (' target="_blank" rel="noopener"' if ext else "") + f">{t}</a>"
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def block_html(text):
    lines = text.strip("\n").split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        if ln.startswith("```"):
            j = i + 1; buf = []
            while not lines[j].startswith("```"):
                buf.append(lines[j]); j += 1
            out.append('<pre class="bp-code"><code>' + E("\n".join(buf)) + "</code></pre>"); i = j + 1; continue
        if re.match(r"- ", ln):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:]); i += 1
            out.append("<ul>\n" + "\n".join(f"<li>{inline(x)}</li>" for x in items) + "\n</ul>"); continue
        if re.match(r"\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i])); i += 1
            out.append("<ol>\n" + "\n".join(f"<li>{inline(x)}</li>" for x in items) + "\n</ol>"); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"(- |\d+\. |```)", lines[i]):
            buf.append(lines[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n" + "\n".join(out)


def parse(text):
    posts = []
    for chunk in re.split(r"^=== ", text, flags=re.M)[1:]:
        head, _, rest = chunk.partition("\n## ")
        lines = head.split("\n")
        p = {"slug": lines[0].strip(), "src": [], "takeaways": []}
        mode = None
        for ln in lines[1:]:
            if mode == "take" and ln.startswith("- "):
                p["takeaways"].append(inline(ln[2:])); continue
            mode = None
            if not ln.strip():
                continue
            k, _, v = ln.partition(":"); v = v.strip()
            if k == "takeaways":
                mode = "take"
            elif k == "src":
                t, _, u = v.rpartition("|"); p["src"].append((t.strip(), u.strip()))
            else:
                p[k] = v
        secs = []
        for s in ("## " + rest).split("\n## ")[0:]:
            s = s[3:] if s.startswith("## ") else s
            if not s.strip():
                continue
            hl, _, body = s.partition("\n")
            sid, _, h = hl.partition("|")
            secs.append((sid.strip(), h.strip(), block_html(body)))
        p["sections"] = secs
        posts.append(p)
    return posts


def to_post(p, date):
    d = {
        "slug": p["slug"], "date": date, "reviewed": date, "category": p["cat"],
        "tags": [t.strip() for t in p.get("tags", "").split(",") if t.strip()],
        "keywords": [k.strip() for k in p.get("kw", "").split(";") if k.strip()],
        "title": p["title"], "short": p["short"], "desc": p["desc"], "lead": p["lead"],
        "og_alt": "Share card reading " + p["title"],
        "quick": inline(p["quick"]), "sections": p["sections"], "sources": p["src"],
        "related": [s.strip() for s in p.get("related", "").split(",") if s.strip()],
        "hubs": [tuple(x.strip().split("|", 1)) for x in p.get("hubs", "").split(";") if x.strip()],
        "takeaways": p["takeaways"], "hi": {"title": p["hi"]} if p.get("hi") else {},
    }
    if p.get("series"): d["series"] = p["series"]; d["order"] = int(p.get("order", 0))
    if p.get("updated"): d["updated"] = p["updated"]
    if p.get("srch"): d["sources_h"] = p["srch"]
    return d


def parse_add(text):
    """'+++ slug' blocks in posts/*.add append extra '## id | Heading' sections (FAQs) to a post."""
    out = {}
    for chunk in re.split(r"^\+\+\+ ", text, flags=re.M)[1:]:
        slug, _, rest = chunk.partition("\n")
        secs = []
        for s in rest.split("\n## "):
            s = s[3:] if s.startswith("## ") else s
            if not s.strip(): continue
            hl, _, body = s.partition("\n"); sid, _, h = hl.partition("|")
            secs.append((sid.strip(), h.strip(), block_html(body)))
        out.setdefault(slug.strip(), []).extend(secs)
    return out


ADD = {}
for f in sorted(HERE.glob("posts/*.add")):
    for k, v in parse_add(f.read_text(encoding="utf-8")).items(): ADD.setdefault(k, []).extend(v)

MORE_POSTS = []
for f in sorted(HERE.glob("posts/*.txt")):
    for p in parse(f.read_text(encoding="utf-8")):
        p["sections"] += ADD.pop(p["slug"], [])
        MORE_POSTS.append(to_post(p, "2026-11-15"))
assert not ADD, ADD.keys()

# Newest first on the home page and in the offline cache: these go last (all posts share one date, so list order decides)
FEATURED = ["india-cyber-fraud-numbers-2025", "passkeys-2026-explained", "ai-agents-cyber-attacks-cert-in-2026",
            "dpdp-rules-2025-timeline", "sim-binding-whatsapp-india-2027", "ai-voice-cloning-deepfake-scams-2026"]
MORE_POSTS.sort(key=lambda p: FEATURED.index(p["slug"]) if p["slug"] in FEATURED else -1)

MORE_CAT_HI = {"Beginner journey": "Beginner journey", "Cyber trends 2026": "Cyber trends 2026",
               "Everyday safety": "Roz ki online safety", "Tools and labs": "Tools aur labs"}
