# Applies Nandi's SEO pack (cwm-content/seo_pack.json) to prompts.html, cyberlaw.html and ctf.html.
# Idempotent: rewrites title/description/og/twitter/keywords tags and the JSON-LD block between seo markers.
# Counts and categories are taken from the data the pages actually render, so the meta never drifts.
import html, json, re
BASE = "https://www.cyberwithmadhav.com/"

def _attr(s): return html.escape(s, quote=True)

def _set_meta(doc, key, val, attr="name", after='<meta property="og:locale"'):
    tag = f'<meta {attr}="{key}" content="{_attr(val)}">'
    pat = re.compile(rf'<meta {attr}="{re.escape(key)}" content="[^"]*">')
    if pat.search(doc): return pat.sub(lambda m: tag, doc, count=1)
    i = doc.index(after); j = doc.index("\n", i)
    return doc[:j + 1] + "  " + tag + "\n" + doc[j + 1:]

def _prompts_overrides(root, p):
    d = json.loads((root / "data" / "prompts.json").read_text())
    cats, prompts = d["categories"], d["prompts"]
    n = {c["id"]: sum(1 for x in prompts if x["cat"] in c.get("group", [c["id"]])) for c in cats}
    uc = root / "data" / "cyberprompts_usecases.json"
    nuc = len(json.loads(uc.read_text())) if uc.exists() else 0
    p["meta_description"] = (f"{len(prompts)} free defensive AI prompts in {len(cats)} categories, including Defensive Analysis, SOC, victim help, "
                             f"compliance and cyber law, plus {nuc} scenario cards. India focused.")
    ld = p["json_ld"]
    ld["numberOfItems"] = len(cats)
    author = ld["author"]
    ld["itemListElement"] = [{"@type": "ListItem", "position": i + 1, "item": {"@type": "CreativeWork", "name": f"{c['name']} prompts",
        "description": (f"{n[c['id']]} defensive AI prompts in the {c['name']} category" + (", grouping the analysis categories." if c.get("group") else ".")),
        "url": BASE + "prompts.html", "author": author}} for i, c in enumerate(cats)]
    return p

def _cyberlaw_overrides(root, p):
    faq = root / "data" / "cyberlaw_faq.json"
    if faq.exists():
        f = json.loads(faq.read_text())
        p["json_ld"]["mainEntity"] = [{"@type": "Question", "name": x["q"], "acceptedAnswer": {"@type": "Answer", "text": x["a_en"]}} for x in f]
    p["meta_description"] = re.sub(r"\s*(punishments, bail and compounding|DPDP Act penalties)[,;]?", "", p["meta_description"])
    return p

def apply(root, pack_path):
    if not pack_path.exists():
        print("missing seo_pack.json (SEO left as is)"); return
    pack = json.loads(pack_path.read_text())
    for page, p in pack.items():
        if page == "prompts.html": p = _prompts_overrides(root, p)
        if page == "cyberlaw.html": p = _cyberlaw_overrides(root, p)
        url = BASE + page
        assert p["canonical_url"] == url and p["json_ld"]["url"] == url, page
        f = root / page; doc = f.read_text()
        doc = re.sub(r"<title>[^<]*</title>", lambda m: f"<title>{html.escape(p['title'], quote=False)}</title>", doc, count=1)
        doc = _set_meta(doc, "description", p["meta_description"])
        doc = _set_meta(doc, "keywords", ", ".join(p["keywords"]), after='<meta name="description"')
        doc = _set_meta(doc, "og:title", p["og_title"], "property")
        doc = _set_meta(doc, "og:description", p["og_description"], "property")
        doc = _set_meta(doc, "og:url", url, "property")
        doc = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', doc, count=1)
        doc = _set_meta(doc, "twitter:title", p["og_title"], after='<meta name="twitter:card"')
        doc = _set_meta(doc, "twitter:description", p["og_description"], after='<meta name="twitter:title"')
        ld = json.dumps(p["json_ld"], ensure_ascii=False, indent=1).replace("</", "<\\/")
        block = f'  <!-- seo:start (generated from seo_pack.json by tools/build_pages_data.py) -->\n  <script type="application/ld+json">\n{ld}\n  </script>\n  <!-- seo:end -->\n'
        doc = re.sub(r"  <!-- seo:start.*?<!-- seo:end -->\n", "", doc, flags=re.S)
        doc = doc.replace("</head>", block + "</head>", 1)
        f.write_text(doc)
        print(f"seo applied: {page} ({len(p['meta_description'])} char description)")
