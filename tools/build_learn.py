#!/usr/bin/env python3
"""Builds the Learn hub (learn.html) and lesson pages (learn-*.html) from tools/content/learn_*.py,
using scams.html as the shell (head, nav, footer), like build_lab.py. Also wires the Learn path into the rest of the site
(idempotent): roadmap links in data/roadmap.json and the privacy storage table.
Then run tools/build_site.py, which owns the nav (Learn link), sitemap, search index, asset versions and sw.js.
   Run: python3 tools/build_learn.py && python3 tools/build_site.py"""
import hashlib, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from learn_kit import e
from content.learn_path import LESSONS, BY_SLUG, STAGES, ROADMAP_LINKS

BASE = "https://www.cyberwithmadhav.com/"
AUTHOR = {"@type": "Person", "name": "Madhav Pandya", "url": BASE + "about.html"}
PUB = {"@type": "Organization", "name": "CyberWithMadhav", "url": BASE}
TODAY = "2026-11-24"
PUBLISHED = {"learn-how-computers-work": "2026-11-23", "learn-operating-system-fundamentals": "2026-11-23", "learn-windows-for-security": "2026-11-23", "learn-networking-basics": "2026-11-23", "learn-linux-fundamentals": "2026-11-23", "learn-linux-hands-on-lab": "2026-11-23"}
FEATS = {}

def ver(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:10]

STAGE_OF = {}
for st in STAGES:
    for it in st["items"]:
        if isinstance(it, str): STAGE_OF[it] = st
ORDER = [s for st in STAGES for s in st["items"] if isinstance(s, str)]

# Hinglish for interface text shared by every Learn page
UI_HI = {
  "lx.c.analogy": "Aise samjho", "lx.c.attack": "Attacker isko kaise abuse karta hai", "lx.c.defend": "Defender ka move",
  "lx.got": "Ye section samajh aa gaya", "lx.got.on": "Samajh aa gaya", "lx.done": "Poora lesson complete mark karo", "lx.done.on": "Lesson complete. Badhiya kaam.",
  "lx.q.left": "Sab sawaal answer karo, phir score dikhega.", "lx.q.top": "Excellent. Aapko ye sach mein aata hai.", "lx.q.pass": "Pass. Jo galat hue unhe dobara padho, phir aage badho.",
  "lx.q.fail": "Abhi nahi. Galat answers wale sections dobara padho aur phir try karo.", "lx.q.right": "Sahi. ", "lx.q.wrong": "Nahi. ",
  "lx.copy": "Copy", "lx.copied": "Copied", "lx.bits.space": "space", "lx.bits.np": "print nahi hota",
  "lx.h.goals": "Is lesson ke baad aap ye kar paoge", "lx.h.cards": "Flashcards: yaad hai?", "lx.h.quiz": "Quick quiz", "lx.h.lab": "Lab: khud karke dekho", "lx.h.take": "Key takeaways",
  "lx.toc": "Is lesson mein", "lx.start": "Lesson shuru karo", "lx.jump": "Seedha lab pe jao", "lx.flipall": "Saare cards palto", "lx.retry": "Quiz dobara karo",
  "lx.cards.p": "Card pe tap karo, answer dekhne ke liye. Pehle khud yaad karne ki koshish karo.", "lx.quiz.p": "Har sawaal pe turant feedback milega. 70% pe lesson ka quiz pass maana jaata hai.",
  "lx.need": "Aapko chahiye:", "lx.verify": "Kaam tab poora jab:", "lx.prev": "Pichla", "lx.next": "Agla", "lx.hub": "Saare lessons",
  "lx.complete.p": "Sab sections, quiz aur lab ho gaye? Lesson complete mark karo. Progress sirf is browser mein save hota hai.",
  "lx.stepdone": "Ho gaya", "lx.legal": "<strong>Sirf apni machines pe.</strong> Ye lab apne VM ya apne computer pe karo. Kisi aur ke system ko bina likhit permission ke scan, test ya access karna IT Act, 2000 (jaise Sections 43 aur 66) ke under offence ho sakta hai.",
  "lx.hint": "Hint", "lx.pt.legal": "<strong>Simulator lab, zero risk.</strong> Ye lab Cisco Packet Tracer ke andar chalta hai, koi real network touch nahi hota. Packet Tracer Cisco Networking Academy (netacad.com) ke free account se free milta hai. Packet Tracer IOS ka ek subset simulate karta hai, isliye jahan kisi feature ka support pakka nahi, wahan humne clearly likha hai.",
  "lx.pt.topo": "Topology aur addressing", "lx.pt.limits": "Packet Tracer limits aur notes", "lx.pt.dl": "Lab checklist download karo (.txt)", "lx.pt.dlp": "Checklist print karo ya Packet Tracer ke saath side mein kholo.",
  "lx.sn.bad": "Address check karo", "lx.sn.badd": "0 se 255 tak ke chaar numbers likho, jaise 192.168.50.130",
  "lx.rt.pick": "Ye use karo", "lx.rt.next": "Agla packet", "lx.rt.again": "Phir se khelo",
  "lx.acl.ip": "Valid source aur destination IPv4 address daalo.", "lx.acl.imp": "kuch match nahi hua, isliye end ka chhupa hua deny ise drop karta hai",
  "lx.t7.bad": "Type 7 string paste karo, jaise 0822455D0A16",
  "lh.done": "Done", "lh.new": "Start", "lh.cont": "Continue: ", "lh.begin": "Lesson 1 se shuru karo", "lh.reset.q": "Is browser se lesson progress clear karein?",
}

LEGAL = ('<div class="lx-legal" role="note"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3 2 21h20L12 3z"/><path d="M12 10v5M12 18h.01"/></svg>'
         '<p data-i18n="lx.legal"><strong>Only on machines you own.</strong> Do this lab on your own VM or computer. Scanning, testing or accessing anyone else\'s system without written permission can be an offence under the Information Technology Act, 2000 (for example Sections 43 and 66).</p></div>')
PT_NOTE = ('<div class="lx-legal" role="note"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v5h1"/></svg>'
         '<p data-i18n="lx.pt.legal"><strong>Simulator lab, zero risk.</strong> This lab runs inside Cisco Packet Tracer, so it touches no real network. Packet Tracer is free with a Cisco Networking Academy account (netacad.com). It simulates a subset of Cisco IOS, so where support for a feature is uncertain we say so instead of promising it works.</p></div>')

def strip(h):
    return html.unescape(re.sub(r"<[^>]+>", "", h)).strip()

def checklist(L, url):
    lab = L["lab"]; o = []
    o += [f"CyberWithMadhav Learn: lesson {L['n']} lab checklist", strip(lab["title"]), url, ""]
    o += ["Time: " + strip(lab["time"]), "You need: " + strip(lab["needs"]), ""]
    if lab.get("addr"):
        o.append("ADDRESSING")
        for r in lab["addr"]: o.append("  " + " | ".join(strip(c) for c in r))
        o.append("")
    o.append("STEPS (tick each box when done)")
    for k, (h, c) in enumerate(lab["steps"]):
        o.append(f"[ ] {k + 1}. {strip(h)}")
        for pre in re.findall(r"<pre[^>]*>(.*?)</pre>", c, flags=re.S):
            for ln in pre.split("\n"):
                m = re.search(r'<span class="p">(.*?)</span><span class="cmd">(.*?)</span>', ln)
                if m: o.append("      " + strip(m.group(1)) + " " + strip(m.group(2)))
        rest = strip(re.sub(r"<div class=\"lx-code.*?</div>", " ", c, flags=re.S))
        rest = re.sub(r"\s+", " ", rest).strip()
        if rest: o.append("      Note: " + rest)
    o += ["", "DONE WHEN: " + strip(lab["verify"])]
    if lab.get("limits"):
        o += ["", "PACKET TRACER LIMITS AND NOTES"] + ["  - " + strip(x) for x in lab["limits"]]
    if lab.get("kind") == "pt":
        o += ["", "Packet Tracer is free with a Cisco Networking Academy account: https://www.netacad.com/"]
    else:
        o += ["", "Only on machines you own. Testing systems without written permission can be an offence under the IT Act, 2000."]
    txt = "\n".join(o) + "\n"
    txt = txt.replace("\u2014", "-").replace("\u2013", "-").replace("\u2192", "->").replace("\u00a0", " ")
    assert "\u2014" not in txt and "\u2013" not in txt
    d = ROOT / "assets/learn"; d.mkdir(exist_ok=True)
    (d / f"{L['slug']}-lab-checklist.txt").write_text(txt, encoding="utf-8")
    return f"assets/learn/{L['slug']}-lab-checklist.txt"

def shell(file, title, desc, og, ogd, kw, schema, main, body_attrs, extra_js, page_dict_js):
    src = (ROOT / "scams.html").read_text(encoding="utf-8")
    url = BASE + file
    h = re.sub(r"<title>.*?</title>", lambda m: "<title>" + title + "</title>", src)
    h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + e(desc), h)
    h = re.sub(r'(<meta name="keywords" content=")[^"]*', lambda m: m.group(1) + e(kw), h)
    h = h.replace(BASE + "scams.html", url)
    for a in ('property="og:title"', 'name="twitter:title"'):
        h = re.sub(r'(' + a + r' content=")[^"]*', lambda m: m.group(1) + e(og), h)
    for a in ('property="og:description"', 'name="twitter:description"'):
        h = re.sub(r'(' + a + r' content=")[^"]*', lambda m: m.group(1) + e(ogd), h)
    ld = json.dumps(schema, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    h = re.sub(r'(<script type="application/ld\+json">\n).*?(\n  </script>)', lambda m: m.group(1) + ld + m.group(2), h, flags=re.S)
    h = re.sub(r'(<link rel="stylesheet" href="assets/css/features\.css\?v=[0-9a-f]+">)', lambda m: m.group(1) + f'\n  <link rel="stylesheet" href="assets/css/learn.css?v={ver("assets/css/learn.css")}">', h)
    assert "learn.css" in h
    h = re.sub(r'<body class="v3 scam-page">', lambda m: f'<body class="v3 learn-page"{body_attrs}>', h)
    h = h.replace('class="nav-explore active"', 'class="nav-explore"')
    h = re.sub(r'  <main id="main".*?</main>\n', lambda m: '  <main id="main" tabindex="-1">\n' + main + '  </main>\n', h, flags=re.S)
    js = f'  <script src="assets/js/i18n/{page_dict_js}?v={ver("assets/js/i18n/" + page_dict_js)}" defer></script>\n'
    js += "".join(f'  <script src="assets/js/{j}?v={ver("assets/js/" + j)}" defer></script>\n' for j in extra_js)
    h, n = re.subn(r'  <script src="assets/js/scams\.js\?v=[0-9a-f]+" defer></script>\n', lambda m: js, h)
    assert n == 1 and "scams.js" not in h, file
    assert "\u2014" not in h and "\u2013" not in h, f"dash in {file}"
    (ROOT / file).write_text(h, encoding="utf-8")
    print("wrote", file)

def write_dict(name, d, note):
    body = ",\n".join(f" {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}" for k, v in d.items())
    txt = f"/* Hinglish text for {note}. Generated by tools/build_learn.py from tools/content/learn_*.py. */\nwindow.CWM_I18N_PAGE = {{\n{body}\n}};\n"
    assert "\u2014" not in txt and "\u2013" not in txt
    (ROOT / "assets/js/i18n" / name).write_text(txt, encoding="utf-8")

# ---------------------------------------------------------------- lesson page
def lesson_page(L):
    st = STAGE_OF[L["slug"]]
    i = ORDER.index(L["slug"])
    prev = BY_SLUG[ORDER[i - 1]] if i > 0 else None
    nxt = BY_SLUG[ORDER[i + 1]] if i + 1 < len(ORDER) else None
    secs = L["sections"]
    d = dict(UI_HI); d["lx.title"] = L["hi_title"]; d["lx.lead"] = L["hi_lead"]
    toc = []
    for k, s in enumerate(secs):
        d[f"s.{s['id']}.h"] = s["hi_h"]
        toc.append(f'<li><a href="#{s["id"]}"><i></i><span data-i18n="s.{s["id"]}.h">{s["h"]}</span></a></li>')
    toc += ['<li><a href="#flashcards"><i></i><span data-i18n="lx.h.cards">Flashcards</span></a></li>',
            '<li><a href="#quiz"><i></i><span data-i18n="lx.h.quiz">Quick quiz</span></a></li>',
            '<li><a href="#lab"><i></i><span data-i18n="lx.h.lab">Hands-on lab</span></a></li>',
            '<li><a href="#takeaways"><i></i><span data-i18n="lx.h.take">Key takeaways</span></a></li>']
    body = []
    for k, s in enumerate(secs):
        body.append(f'''        <section id="{s["id"]}" aria-labelledby="{s["id"]}-h">
          <span class="lx-num mono">{L["n"]}.{k + 1:02d}</span>
          <h2 id="{s["id"]}-h" data-i18n="s.{s["id"]}.h">{s["h"]}</h2>
          {s["body"]}
          <aside class="lx-call lx-hi" role="note" data-lang-only="hi"><b>Hinglish mein samjho</b><div><p>{s["hi"]}</p></div></aside>
          <button type="button" class="lx-got" data-sec="{s["id"]}" aria-pressed="false"><i aria-hidden="true"></i><span data-i18n="lx.got">I understood this section</span></button>
        </section>''')
    cards = "".join(f'<button type="button" class="lx-card" aria-pressed="false"><span class="in"><span class="f"><small>Card {n + 1}</small><b>{q}</b><small>Tap to reveal</small></span><span class="b"><small>Answer</small><span>{a}</span></span></span></button>' for n, (q, a) in enumerate(L["cards"]))
    quiz = "".join(f'''<div class="card lx-q" data-a="{ans}"><h3><span>Q{n + 1}</span>{q}</h3><ul class="lx-opts">{"".join(f'<li><button type="button"><i>{"ABCD"[j]}</i><span>{o}</span></button></li>' for j, o in enumerate(opts))}</ul><p class="lx-why" hidden aria-live="polite"><b></b>{why}</p></div>''' for n, (q, opts, ans, why) in enumerate(L["quiz"]))
    lab = L["lab"]; pt = lab.get("kind") == "pt"
    ck = checklist(L, BASE + L["slug"] + ".html")
    pre = ""
    if lab.get("topo") or lab.get("addr"):
        from learn_kit import addr_table
        pre = '<div class="lx-pt-pre"><h4 data-i18n="lx.pt.topo">Topology and addressing</h4>' + (lab.get("topo") or "") + (addr_table(lab["addr"]) if lab.get("addr") else "") + '</div>'
    lim = ('<div class="lx-limits" role="note"><h4 data-i18n="lx.pt.limits">Packet Tracer limits and notes</h4><ul>' + "".join(f"<li>{x}</li>" for x in lab["limits"]) + '</ul></div>') if lab.get("limits") else ""
    dl = f'<p class="lx-dl"><a class="btn btn-ghost" href="{ck}" download><span data-i18n="lx.pt.dl">Download the lab checklist (.txt)</span></a> <span class="small muted" data-i18n="lx.pt.dlp">Print it or keep it open beside Packet Tracer.</span></p>' if pt else f'<p class="lx-dl"><a class="btn btn-ghost" href="{ck}" download><span>Download the lab checklist (.txt)</span></a></p>'
    steps = "".join(f'<li><h4>{h}</h4>{c}<label class="lx-check"><input type="checkbox"> <span data-i18n="lx.stepdone">Done</span></label></li>' for h, c in lab["steps"])
    pager = (f'<a href="{prev["slug"]}.html"><small data-i18n="lx.prev">Previous</small>{prev["n"]} {prev["title"]}</a>' if prev else '<a href="learn.html"><small data-i18n="lx.hub">All lessons</small>Learn hub</a>')
    nst = next((x for x in STAGES if x["n"] > st["n"] and any(not isinstance(it, str) for it in x["items"])), None)
    pager += (f'<a class="nx" href="{nxt["slug"]}.html"><small data-i18n="lx.next">Next</small>{nxt["n"]} {nxt["title"]}</a>' if nxt else
              (f'<a class="nx" href="learn.html#{nst["id"]}"><small data-i18n="lx.next">Next</small>Stage {nst["n"]}: {nst["name"]} (coming soon)</a>' if nst else '<a class="nx" href="learn.html"><small data-i18n="lx.hub">All lessons</small>Learn hub</a>'))
    main = f'''    <section class="page-hero" aria-labelledby="p-title">
      <div class="wrap">
        <p class="lx-crumb"><a href="learn.html">Learn</a> / <a href="learn.html#{st["id"]}">Stage {st["n"]}: {st["name"]}</a> / Lesson {L["n"]}</p>
        <div class="lx-hero-grid">
          <div>
            <p class="kicker mono">{e(L["kicker"])}</p>
            <h1 id="p-title" data-i18n="lx.title">{L["title"]}</h1>
            <p class="lead" data-i18n="lx.lead">{L["lead"]}</p>
            <ul class="lx-meta" aria-label="Lesson facts"><li>Stage <b>{st["n"]}</b> {st["name"]}</li><li>Level <b>{L["level"]}</b></li><li><b>{L["minutes"]}</b> min</li><li><b>{len(secs)}</b> sections, quiz, lab</li></ul>
            <p><a class="btn btn-primary" href="#{secs[0]["id"]}" data-i18n="lx.start">Start the lesson</a> <a class="btn btn-ghost" href="#lab" data-i18n="lx.jump">Jump to the lab</a></p>
          </div>
          <div class="lx-ring" aria-hidden="true"><span><b>0%</b><small>complete</small></span></div>
        </div>
      </div>
    </section>
    <section class="section lx-sec" aria-label="Lesson">
      <div class="wrap lx-layout">
        <nav class="card lx-toc" aria-label="In this lesson"><h2 data-i18n="lx.toc">In this lesson</h2><ol>{"".join(toc)}</ol></nav>
        <article class="lx-article" data-sections="{len(secs)}">
        <div class="card lx-goals"><h2 data-i18n="lx.h.goals">By the end of this lesson you can</h2><ul>{"".join(f"<li>{g}</li>" for g in L["goals"])}</ul></div>
{chr(10).join(body)}
        <section id="flashcards" aria-labelledby="fc-h">
          <h2 id="fc-h" data-i18n="lx.h.cards">Flashcards: do you remember?</h2>
          <p class="muted" data-i18n="lx.cards.p">Tap a card to flip it. Try to answer in your head first; recalling is what makes it stick.</p>
          <div class="lx-cards">{cards}</div>
          <p><button type="button" class="lx-wbtn" id="lx-flipall" data-i18n="lx.flipall">Flip all cards</button></p>
        </section>
        <section id="quiz" aria-labelledby="qz-h">
          <h2 id="qz-h" data-i18n="lx.h.quiz">Quick quiz</h2>
          <p class="muted" data-i18n="lx.quiz.p">Instant feedback on every answer. Score 70% or more to pass this lesson's quiz.</p>
          <div class="lx-quiz">{quiz}
            <div class="card lx-score" id="lx-score" aria-live="polite"><b>0 / {len(L["quiz"])}</b><span class="msg"></span><button type="button" class="lx-wbtn" id="lx-retry" data-i18n="lx.retry">Retry the quiz</button></div>
          </div>
        </section>
        <section id="lab" aria-labelledby="lab-h">
          <h2 id="lab-h" data-i18n="lx.h.lab">Hands-on lab</h2>
          <div class="card lx-lab">
            <div class="lx-lab-top"><span class="tag g">{"Cisco Packet Tracer lab" if pt else "lab"}</span><span class="tag">{lab["time"]}</span><span class="tag">{"simulated network" if pt else "your own machines only"}</span></div>
            <h3>{lab["title"]}</h3>
            <p><strong data-i18n="lx.need">You need:</strong> {lab["needs"]}</p>
            {PT_NOTE if pt else LEGAL}
            {pre}
            <ol class="lx-labsteps">{steps}</ol>
            <p class="mt-12"><strong data-i18n="lx.verify">You are done when:</strong> {lab["verify"]}</p>
            {lim}
            {dl}
          </div>
        </section>
        <section id="takeaways" aria-labelledby="tk-h">
          <h2 id="tk-h" data-i18n="lx.h.take">Key takeaways</h2>
          <div class="card lx-take"><ul>{"".join(f"<li>{t}</li>" for t in L["takeaways"])}</ul></div>
          <div class="card lx-complete"><p class="muted" data-i18n="lx.complete.p">Finished the sections, quiz and lab? Mark the lesson complete. Progress is saved only in this browser.</p><button type="button" class="btn btn-primary" id="lx-done" aria-pressed="false">Mark the whole lesson complete</button></div>
          <nav class="lx-pager" aria-label="Lesson navigation">{pager}</nav>
        </section>
        </article>
      </div>
    </section>
'''
    url = BASE + L["slug"] + ".html"
    schema = {"@context": "https://schema.org", "@graph": [
      {"@type": "LearningResource", "@id": url + "#lesson", "name": L["title"], "headline": L["title"], "url": url, "description": L["desc"],
       "learningResourceType": "Lesson", "educationalLevel": L["level"], "timeRequired": f"PT{L['minutes']}M", "inLanguage": "en-IN", "isAccessibleForFree": True,
       "teaches": [re.sub("<[^>]+>", "", g) for g in L["goals"]], "author": AUTHOR, "publisher": PUB, "datePublished": PUBLISHED.get(L["slug"], TODAY), "dateModified": TODAY,
       "isPartOf": {"@type": "Course", "@id": BASE + "learn.html#course", "name": "CyberWithMadhav Learn Path", "url": BASE + "learn.html"}},
      {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": "Learn", "item": BASE + "learn.html"},
        {"@type": "ListItem", "position": 3, "name": L["title"], "item": url}]}]}
    page_js = f"learn-{L['slug'][6:]}.js"
    write_dict(page_js, d, L["slug"] + ".html")
    has_term = 'class="lx-term"' in main
    has_net = any(f'lx-widget {c}"' in main for c in ("lx-subnet", "lx-route", "lx-acl"))
    has_ios = 'class="lx-ios"' in main or 'lx-widget lx-t7"' in main
    f = []
    if has_term: f.append("browser terminal")
    if has_ios: f.append("IOS simulator")
    if 'lx-widget lx-subnet"' in main: f.append("subnet calculator")
    if 'lx-widget lx-route"' in main: f.append("route game")
    if 'lx-widget lx-acl"' in main: f.append("ACL tester")
    if pt: f.append("Packet Tracer")
    FEATS[L["slug"]] = f
    shell(L["slug"] + ".html", L["seo_title"], L["desc"], L["title"] + " | Free lesson", L["short"], L["kw"], schema, main,
          f' data-lesson="{L["slug"]}"', ["learn.js"] + (["learn-term.js"] if has_term else []) + (["learn-net.js"] if has_net else []) + (["learn-ios.js"] if has_ios else []), page_js)

# ---------------------------------------------------------------- hub
def units(L):
    return len(L["sections"]), 1, len(L["lab"]["steps"])

def hub():
    d = dict(UI_HI)
    d.update({"lh.title": "Cybersecurity seekho, zero se, step by step", "lh.lead": "Sirf list nahi, poore lessons. Har topic pe click karo aur wahi depth pao jo paid courses mein milti hai: theory, diagrams, attacker aur defender ka view, flashcards, quiz aur apne VM pe lab. Bilkul free.",
              "lh.how": "Har lesson kaise kaam karta hai", "lh.path": "Learning path", "lh.prog": "Aapka progress", "lh.reset": "Progress reset karo",
              "lh.h1": "Theory jo samajh aaye", "lh.p1": "Simple English, diagrams aur roz ki zindagi wale examples. Hinglish mode mein har section ka short recap.",
              "lh.h2": "Attacker aur defender dono", "lh.p2": "Har concept ke saath: attacker isko kaise abuse karta hai aur defender kya karta hai.",
              "lh.h3": "Interactive practice", "lh.p3": "Flashcards, turant feedback wale quiz, widgets aur browser mein chalne wala practice terminal.",
              "lh.h4": "Apne VM pe asli lab", "lh.p4": "VirtualBox lab steps, snapshots ke saath. Sirf apni machines pe, legal aur safe.",
              "lh.note": "Progress sirf aapke browser mein save hota hai (local storage). Koi account nahi, koi cookie nahi."})
    out = []
    for st in STAGES:
        d[f"st.{st['n']}.name"] = st["hi_name"]; d[f"st.{st['n']}.desc"] = st["hi_desc"]
        live = [x for x in st["items"] if isinstance(x, str)]
        cards = []
        for it in st["items"]:
            if isinstance(it, str):
                L = BY_SLUG[it]; s, q, lab = units(L)
                cards.append(f'''<li><a class="lh-l" href="{it}.html" data-slug="{it}" data-s="{s}" data-q="1" data-lab="{lab}"><span class="top"><span class="n mono">{L["n"]}</span><span class="lh-st">Start</span></span><h3>{L["title"]}</h3><p>{L["short"]}</p><span class="foot"><span>{L["minutes"]} min</span><span>{s} sections</span><span>quiz</span><span>lab</span>{"".join(f"<span>{x}</span>" for x in FEATS.get(it, []))}</span></a></li>''')
            else:
                gl = "".join(f"<li>{g}</li>" for g in it["goals"])
                tg = "".join(f"<span>{t}</span>" for t in it["tags"])
                cards.append(f'''<li><div class="lh-l soon"><span class="top"><span class="n mono">{it["n"]}</span><span class="lh-soon">Coming soon</span></span><h3>{it["title"]}</h3><details><summary>What you will learn</summary><ul>{gl}</ul></details>{f'<span class="foot">{tg}</span>' if tg else ''}</div></li>''')
        bar = f'<p class="lh-sbar"><span class="lh-bar" aria-hidden="true"><span></span></span><em>0%</em> of this stage</p>' if live else ''
        out.append(f'''        <section class="lh-stage{'' if live else ' soon'}" id="{st["id"]}" aria-labelledby="{st["id"]}-h">
          <span class="lh-badge" aria-hidden="true">{st["n"]}</span>
          <div class="lh-stage-h"><h2 id="{st["id"]}-h"><span class="sr-only">Stage {st["n"]}: </span><span data-i18n="st.{st["n"]}.name">{st["name"]}</span></h2><span class="tag {'g' if live else ''}">{st["tag"]}</span><span class="tag">{len(live)} of {len(st["items"])} lessons live</span></div>
          <p data-i18n="st.{st["n"]}.desc">{st["desc"]}</p>
          {bar}
          <ul class="lh-lessons">{"".join(cards)}</ul>
        </section>''')
    total = sum(len(st["items"]) for st in STAGES)
    s3 = next(x for x in STAGES if x["n"] == 3); s3live = sum(1 for x in s3["items"] if isinstance(x, str))
    ccna_txt = ("The CCNA track has all 14 lessons live, each with a Cisco Packet Tracer lab." if s3live == len(s3["items"]) else
                f"The 14 lesson CCNA track has {s3live} lessons live, each with a Cisco Packet Tracer lab." if s3live else "That includes a 14 lesson CCNA track with Packet Tracer labs.")
    main = f'''    <section class="page-hero" aria-labelledby="p-title">
      <div class="wrap">
        <p class="kicker mono"><span class="prompt">$</span> ./learn --from zero --to job-ready</p>
        <h1 id="p-title" data-i18n="lh.title">Learn cybersecurity from zero, one clear step at a time</h1>
        <p class="lead" data-i18n="lh.lead">Not a list of topics to Google. Full lessons, with the depth of a paid course: theory you can follow, diagrams, how attackers abuse each idea and how defenders respond, flashcards, quizzes and labs on your own VM. Free.</p>
        <div class="lh-overall" id="lh-all"><span class="small muted" data-i18n="lh.prog">Your progress</span><span class="lh-bar" aria-hidden="true"><span></span></span><b>0%</b>
          <a class="btn btn-primary" id="lh-continue" href="learn-how-computers-work.html"><span>Start with lesson 1</span></a></div>
        <p class="small muted mt-12">{len(ORDER)} lessons live now and {total - len(ORDER)} more mapped out below. {ccna_txt}</p>
      </div>
    </section>
    <section class="section" aria-labelledby="how-h" id="how">
      <div class="wrap">
        <h2 id="how-h" class="sr-only" data-i18n="lh.how">How every lesson works</h2>
        <div class="lh-how">
          <div class="card"><span class="ico" aria-hidden="true">01</span><h3 data-i18n="lh.h1">Theory that makes sense</h3><p data-i18n="lh.p1">Plain English, diagrams and everyday analogies. Switch to Hinglish for a short recap of every section.</p></div>
          <div class="card"><span class="ico" aria-hidden="true">02</span><h3 data-i18n="lh.h2">Attacker and defender views</h3><p data-i18n="lh.p2">Every concept comes with how attackers abuse it and what defenders do about it.</p></div>
          <div class="card"><span class="ico" aria-hidden="true">03</span><h3 data-i18n="lh.h3">Interactive practice</h3><p data-i18n="lh.p3">Flashcards, quizzes with instant feedback, widgets and a practice terminal that runs in your browser.</p></div>
          <div class="card"><span class="ico" aria-hidden="true">04</span><h3 data-i18n="lh.h4">Real labs on your own VM</h3><p data-i18n="lh.p4">Step by step VirtualBox labs with snapshots. Only on machines you own: legal and safe.</p></div>
        </div>
        <h2 class="sr-only" data-i18n="lh.path">Learning path</h2>
        <div class="lh-path">
{chr(10).join(out)}
        </div>
        <p class="small muted mt-12"><span data-i18n="lh.note">Your progress is saved only in this browser (local storage). No account, no cookies.</span> <button type="button" class="lx-wbtn" id="lh-reset" data-i18n="lh.reset">Reset progress</button></p>
        <p class="small muted">Prefer a one page overview? See the <a href="index.html#roadmap">roadmap</a>, practise in the <a href="terminal.html">terminal wargame</a> and the <a href="ctf.html">CTF arena</a>, and keep the <a href="commands.html">command library</a> open while you work.</p>
      </div>
    </section>
'''
    url = BASE + "learn.html"
    schema = {"@context": "https://schema.org", "@graph": [
      {"@type": "Course", "@id": url + "#course", "name": "CyberWithMadhav Learn Path: Cybersecurity from Zero", "url": url,
       "description": "A free, structured cybersecurity learning path: computer and OS fundamentals, Windows, networking, Linux with labs, then CCNA, security fundamentals and specialisations.",
       "provider": PUB, "author": AUTHOR, "inLanguage": "en-IN", "isAccessibleForFree": True, "educationalLevel": "Beginner",
       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR", "category": "Free"},
       "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Online", "courseWorkload": f"PT{max(1, round(sum(BY_SLUG[x]['minutes'] for x in ORDER) / 60))}H"},
       "hasPart": [{"@type": "LearningResource", "name": BY_SLUG[s]["title"], "url": BASE + s + ".html"} for s in ORDER]},
      {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE}, {"@type": "ListItem", "position": 2, "name": "Learn", "item": url}]}]}
    write_dict("learn-hub.js", d, "learn.html")
    shell("learn.html", "Learn Cybersecurity Free: Step by Step Path with Labs | CyberWithMadhav",
          "Free cybersecurity lessons from zero: how computers and operating systems work, Windows, networking, Linux with hands-on labs, then a CCNA track with Packet Tracer labs.",
          "Learn cybersecurity from zero: free lessons with labs", "Computer and OS fundamentals, Windows, networking, Linux with labs, and a CCNA track with Cisco Packet Tracer labs.",
          "learn cybersecurity free, cybersecurity course for beginners india, linux lab, ccna packet tracer labs, windows security basics, networking basics",
          schema, main, "", ["learn.js"], "learn-hub.js")

# ---------------------------------------------------------------- site wiring (idempotent)
NAV_LINK = '<a href="learn.html" class="nav-learn"><span data-i18n="nav.learn">Learn</span></a>'
def add_nav(h, active=False):
    h = re.sub(r'\s*<a href="learn\.html" class="nav-learn[^"]*"(?: aria-current="page")?><span data-i18n="nav\.learn">Learn</span></a>', "", h)
    link = NAV_LINK.replace('class="nav-learn"', 'class="nav-learn active" aria-current="page"') if active else NAV_LINK
    m = re.search(r'(\n(\s*)<a href="index\.html" class="nav-home[^"]*"[^>]*>.*?</a>)', h)
    if not m: return h
    return h[:m.end()] + "\n" + m.group(2) + link + h[m.end():]

def wire():
    # roadmap topics
    rp = ROOT / "data/roadmap.json"; rd = json.loads(rp.read_text(encoding="utf-8"))
    for stg in rd["stages"]:
        new = []
        for t in stg["topics"]:
            text = t["t"] if isinstance(t, dict) else t
            links = ROADMAP_LINKS.get(text)
            new.append({"t": text, "learn": [{"href": h, "label": l} for h, l in links]} if links else {"t": text, "soon": True})
        stg["topics"] = new
    rp.write_text(json.dumps(rd, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # home page roadmap: a call to action into the Learn path, plus its Hinglish text in the shared dictionary
    ip = ROOT / "index.html"; ih = ip.read_text(encoding="utf-8")
    ih = re.sub(r'\n\s*<div class="rm-cta[^"]*">.*?</div><!-- /rm-cta -->', "", ih, flags=re.S)
    cta = ('\n        <div class="rm-cta reveal"><p data-i18n="home.learn.p"><strong>New: Beginner topics now open full lessons.</strong> Theory, diagrams, quizzes and VM labs, right here on the site. No more Googling each topic.</p>'
           '<a class="btn btn-primary" href="learn.html" data-i18n="home.learn.cta">Open the Learn path &rarr;</a></div><!-- /rm-cta -->')
    anchor = '<p class="muted" data-i18n="home.roadmap.p">'
    k = ih.index(anchor); k = ih.index("</header>", k) + len("</header>")
    ih = ih[:k] + cta + ih[k:]
    ip.write_text(ih, encoding="utf-8")
    dp = ROOT / "assets/js/i18n-dict.js"; dt = dp.read_text(encoding="utf-8")
    dt = re.sub(r"\n/\* learn:start \*/.*?/\* learn:end \*/", "", dt, flags=re.S)
    dt = dt.rstrip("\n") + "\n" + ('/* learn:start */\nObject.assign(window.CWM_I18N.hi, {\n'
          ' "home.learn.p": "<strong>Naya: Beginner topics ab poore lessons kholte hain.</strong> Theory, diagrams, quiz aur VM labs, isi site pe. Ab har topic Google karne ki zaroorat nahi.",\n'
          ' "home.learn.cta": "Learn path kholo &rarr;"\n});\n/* learn:end */\n')
    dp.write_text(dt, encoding="utf-8")
    # privacy storage table (and the generator that owns it)
    row_txt = "Which lesson sections, quizzes and lab steps you finished on the Learn pages, so your progress shows when you come back."
    bl = ROOT / "tools/build_legal.py"; b = bl.read_text(encoding="utf-8")
    if '"cwm-learn"' not in b:
        b = b.replace(' ("cwm-prompt-favs", "Local storage",', f' ("cwm-learn", "Local storage", "{row_txt}"),\n ("cwm-prompt-favs", "Local storage",', 1)
        bl.write_text(b, encoding="utf-8")
    pp = ROOT / "privacy.html"; ph = pp.read_text(encoding="utf-8")
    if "<code>cwm-learn</code>" not in ph:
        row = f'<tr><th scope="row"><code>cwm-learn</code></th><td>Local storage</td><td>{row_txt}</td></tr>'
        ph2 = ph.replace('<tr><th scope="row"><code>cwm-prompt-favs</code></th>', row + '<tr><th scope="row"><code>cwm-prompt-favs</code></th>', 1)
        assert ph2 != ph, "privacy storage row anchor not found"
        pp.write_text(ph2, encoding="utf-8")
    print("wired roadmap and privacy storage table. Now run: python3 tools/build_site.py")

if __name__ == "__main__":
    for L in LESSONS: lesson_page(L)
    hub()
    wire()
