#!/usr/bin/env python3
"""Build the "best personal site" pages: start-here.html, now.html, uses.html (toolkit) and collaborate.html,
plus humans.txt and .well-known/security.txt. Run from the repo root after build_blog.py and before build_site.py:
    python3 tools/build_extras.py && python3 tools/build_site.py
Uses the shared shell from make_page.py. Hinglish UI strings go into assets/js/i18n-dict.js between the
extras:start and extras:end markers. Facts here must stay true: no follower counts, clients, awards or employer."""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools" / "content"))
import make_page  # noqa: E402
from blog_src import POSTS  # noqa: E402

BASE = make_page.BASE
E = lambda s: html.escape(s, quote=True)
UPDATED = ("2026-11-16", "16 November 2026")
EMAIL = "madhavpandya@zohomail.in"
SOCIALS = [("LinkedIn", "https://www.linkedin.com/in/pandyamadhav/"), ("YouTube", "https://www.youtube.com/@cyberwithmadhav"),
           ("Instagram", "https://www.instagram.com/cyberwithmadhav/"), ("GitHub", "https://github.com/iammadhavpandya-oss")]
HI = {}  # Hinglish strings for data-i18n keys


def post(slug): return next(p for p in POSTS if p["slug"] == slug)


def plink(slug):
    p = post(slug)
    return f'<a href="blog-{slug}.html" data-i18n="blogpost.{slug}.t">{E(p["title"])}</a>'


def t(key, en, hi, tag="p", cls=""):
    HI[key] = hi
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c} data-i18n="{key}">{en}</{tag}>'


def follow_block(prefix):
    btns = "\n".join(f'          <a class="btn btn-ghost small" href="{u}" target="_blank" rel="me noopener">{n}</a>' for n, u in SOCIALS)
    return f"""    <section class="section xp-sec" aria-labelledby="{prefix}-follow-h">
      <div class="wrap">
        <div class="card xp-follow">
          {t(prefix + ".follow.h", "Get the next guide", "Agla guide miss mat karo", "h2", "h3").replace("<h2", f'<h2 id="{prefix}-follow-h"', 1)}
          {t(prefix + ".follow.p", "There is no newsletter yet. Follow on any of these, or add the RSS feed to your reader app. New guides show up there first.", "Abhi newsletter nahi hai. Inme se kahin bhi follow karo, ya RSS feed apne reader app mein add karo. Naye guides wahan sabse pehle aate hain.", "p", "muted")}
          <div class="xp-btns">
{btns}
          <a class="btn btn-ghost small" href="feed.xml">RSS feed</a>
          </div>
        </div>
      </div>
    </section>"""


def hero(prefix, cmd, h1, lead_en, lead_hi, extra=""):
    return f"""    <section class="page-hero xp-hero" aria-labelledby="p-title">
      <div class="wrap">
        <p class="kicker mono"><span class="prompt">$</span> {cmd}</p>
        <h1 id="p-title">{h1}</h1>
        {t(prefix + ".lead", lead_en, lead_hi, "p", "lead")}
{extra}      </div>
    </section>"""


def crumbs(name):
    return f"""        <nav class="xp-crumbs small muted" aria-label="Breadcrumb"><a href="index.html" data-i18n="blog.home">Home</a> <span aria-hidden="true">/</span> <span aria-current="page">{name}</span></nav>
"""


def ld_page(file, name, desc, typ="WebPage", extra=None):
    url = BASE + file
    page = {"@type": typ, "@id": url + "#page", "url": url, "name": name, "description": desc, "inLanguage": "en-IN",
            "isPartOf": {"@id": BASE + "#website"}, "author": {"@id": BASE + "about.html#person"}, "dateModified": UPDATED[0] + "T09:00:00+05:30"}
    if extra: page.update(extra)
    graph = [page, {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": name.split(":")[0].split(" | ")[0], "item": url}]}]
    return '  <script type="application/ld+json">\n  ' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "\n  </script>"


# ---------------- Start here ----------------
SAFE = ["first-hour-after-cyber-fraud", "upi-scams-india", "safe-upi-habits", "otp-scams-india", "spot-phishing-sms-india",
        "digital-arrest-scam-india", "whatsapp-account-takeover", "secure-parents-phone", "two-factor-authentication-guide", "strong-passwords-password-managers"]
LAW = ["cyber-law-india-intro", "report-cyber-fraud-india", "dpdp-rules-2025-timeline", "loan-app-harassment-help"]


def start_main():
    journey = sorted((p for p in POSTS if p.get("series") == "Beginner journey"), key=lambda p: p["order"])
    jl = "\n".join(f'            <li>{plink(p["slug"])}</li>' for p in journey)
    sl = "\n".join(f'            <li>{plink(s)}</li>' for s in SAFE)
    ll = "\n".join(f'            <li>{plink(s)}</li>' for s in LAW)
    sos = f"""        <div class="xp-sos" role="note">
          {t("sh.sos", '<strong>Lost money just now?</strong> Call <a href="tel:1930">1930</a> and report at <a href="https://cybercrime.gov.in" target="_blank" rel="noopener">cybercrime.gov.in</a> first. Then read <a href="blog-first-hour-after-cyber-fraud.html">what to do in the first hour</a>.', '<strong>Abhi paise gaye?</strong> Pehle <a href="tel:1930">1930</a> call karo aur <a href="https://cybercrime.gov.in" target="_blank" rel="noopener">cybercrime.gov.in</a> pe report karo. Phir padho <a href="blog-first-hour-after-cyber-fraud.html">pehle ghante mein kya karna hai</a>.', "p")}
        </div>
"""
    return f"""  <main id="main" tabindex="-1">
{hero("sh", "cd ~/start-here", "Start here", "New to CyberWithMadhav? Pick the path that fits you. Every guide is free, in plain English, with a Hinglish switch at the top.", "CyberWithMadhav pe naye ho? Apna path chuno. Har guide free hai, simple English mein, aur upar Hinglish ka switch hai.", crumbs("Start here") + sos)}

    <section class="section xp-sec" aria-label="Choose your path">
      <div class="wrap xp-paths">
        <article class="card xp-path t-amber" id="stay-safe" aria-labelledby="sh-safe-h">
          <p class="kicker mono">path 01</p>
          {t("sh.safe.h", "I just want to stay safe online", "Mujhe bas online safe rehna hai", "h2", "h3").replace("<h2", '<h2 id="sh-safe-h"', 1)}
          {t("sh.safe.p", "For you, your parents and your family. No jargon. Read these in any order.", "Aapke, aapke parents aur family ke liye. Koi jargon nahi. Kisi bhi order mein padho.", "p", "muted")}
          <ol class="xp-list">
{sl}
          </ol>
          <p class="xp-more small"><a href="game.html" data-i18n="sh.safe.game">Practice: play Scam ya Nahi?</a> · <a href="scams.html" data-i18n="sh.safe.enc">Scam encyclopedia</a> · <a href="faq.html#scams" data-i18n="sh.safe.faq">Quick answers</a></p>
        </article>

        <article class="card xp-path t-violet" id="learn" aria-labelledby="sh-learn-h">
          <p class="kicker mono">path 02</p>
          {t("sh.learn.h", "I want to learn cybersecurity", "Mujhe cybersecurity seekhni hai", "h2", "h3").replace("<h2", '<h2 id="sh-learn-h"', 1)}
          {t("sh.learn.p", "The Beginner Journey is a 15 part series, from zero to a 90 day study plan. Read it in order.", "Beginner Journey 15 parts ki series hai, zero se 90 din ke study plan tak. Order mein padho.", "p", "muted")}
          <ol class="xp-list">
{jl}
          </ol>
          <p class="xp-more small"><a href="ctf.html" data-i18n="sh.learn.ctf">Then practice in the CTF Arena</a> · <a href="commands.html" data-i18n="sh.learn.cmd">Command reference</a> · <a href="uses.html" data-i18n="sh.learn.kit">Free toolkit</a></p>
        </article>

        <article class="card xp-path t-pink" id="law" aria-labelledby="sh-law-h">
          <p class="kicker mono">path 03</p>
          {t("sh.law.h", "I am curious about cyber law in India", "Mujhe India ke cyber law samajhne hain", "h2", "h3").replace("<h2", '<h2 id="sh-law-h"', 1)}
          {t("sh.law.p", "The IT Act, BNS and the DPDP Act in plain words, plus where to file a complaint. Educational, not legal advice.", "IT Act, BNS aur DPDP Act simple shabdon mein, aur complaint kahan file karein. Educational hai, legal advice nahi.", "p", "muted")}
          <ol class="xp-list">
            <li><a href="cyberlaw.html" data-i18n="sh.law.page">Cyber Law India: the full guide</a></li>
{ll}
          </ol>
          <p class="xp-more small"><a href="faq.html#law" data-i18n="sh.law.faq">Cyber law quick answers</a></p>
        </article>
      </div>
    </section>

{follow_block("sh")}
  </main>"""


# ---------------- Now ----------------
def now_main():
    items = [
        ("now.study", "<strong>Studying.</strong> A BCA in Cloud Computing and Cyber Security, and a BA LLB at KES Shri J.P. Law College. The law side is why this site explains the IT Act and the DPDP Act so often.",
         "<strong>Padhai.</strong> BCA (Cloud Computing and Cyber Security) aur KES Shri J.P. Law College se BA LLB. Isi law side ki wajah se yahan IT Act aur DPDP Act baar baar samjhaye jaate hain."),
        ("now.write", f'<strong>Writing.</strong> Guides on this site, {len(POSTS)} so far, each with its official sources. The <a href="start-here.html#learn">Beginner Journey</a> series is complete.',
         f'<strong>Likhna.</strong> Is site pe guides, abhi tak {len(POSTS)}, har ek official sources ke saath. <a href="start-here.html#learn">Beginner Journey</a> series poori ho gayi hai.'),
        ("now.book", "<strong>A cybersecurity book.</strong> Coming soon. More here when it is ready.",
         "<strong>Ek cybersecurity book.</strong> Jaldi aa rahi hai. Ready hone pe yahan update milega."),
        ("now.share", '<strong>Sharing.</strong> Short posts on <a href="https://www.linkedin.com/in/pandyamadhav/" target="_blank" rel="me noopener">LinkedIn</a> about cyber awareness, networking, careers and cyber law in India.',
         '<strong>Share karna.</strong> <a href="https://www.linkedin.com/in/pandyamadhav/" target="_blank" rel="me noopener">LinkedIn</a> pe chhote posts: cyber awareness, networking, careers aur India ka cyber law.'),
        ("now.build", '<strong>Building.</strong> Free practice on this site: the <a href="ctf.html">CTF Arena</a>, the <a href="game.html">Scam ya Nahi?</a> game and the <a href="faq.html">FAQ</a>.',
         '<strong>Banana.</strong> Is site pe free practice: <a href="ctf.html">CTF Arena</a>, <a href="game.html">Scam ya Nahi?</a> game aur <a href="faq.html">FAQ</a>.'),
    ]
    li = "\n".join(f'          <li>{t(k, en, hi, "p")}</li>' for k, en, hi in items)
    return f"""  <main id="main" tabindex="-1">
{hero("now", "cat ~/now.txt", "What I am doing now", "A short, honest snapshot of what I am focused on this month. If you knew me in person, this is what I would tell you.", "Is mahine main kis pe focus kar raha hoon, ek chhota aur honest snapshot. Agar aap mujhe personally jaante, toh yahi bataata.", crumbs("Now"))}

    <section class="section xp-sec" aria-labelledby="now-h">
      <div class="wrap xp-narrow">
        <h2 id="now-h" class="sr-only">Now</h2>
        <ul class="xp-now">
{li}
        </ul>
        <p class="small muted mono">Updated <time datetime="{UPDATED[0]}">{UPDATED[1]}</time> · Mumbai, India</p>
        {t("now.what", 'This is a <a href="https://nownownow.com/about" target="_blank" rel="noopener">now page</a>, an idea from Derek Sivers: a page that says what you are focused on at this point in your life.', 'Yeh ek <a href="https://nownownow.com/about" target="_blank" rel="noopener">now page</a> hai, Derek Sivers ka idea: ek page jo batata hai ki aap life ke is point pe kis cheez pe focus kar rahe ho.', "p", "small muted")}
      </div>
    </section>

{follow_block("now")}
  </main>"""


# ---------------- Toolkit (uses) ----------------
KIT = [
    ("kit.lab", "Lab setup", "Lab setup", [
        ("VirtualBox", "https://www.virtualbox.org/", "Run practice machines safely inside your own computer.", "safe-home-lab-setup"),
        ("Ubuntu and Kali Linux", "https://ubuntu.com/download", "Linux for learning the command line, logs and security tools.", "linux-basics-for-cybersecurity"),
        ("GitHub", "https://github.com/", "A free place to show your notes, write ups and small projects.", "cybersecurity-portfolio-github")]),
    ("kit.net", "Network", "Network", [
        ("Nmap", "https://nmap.org/", "See which devices and ports are open, on your own lab only.", "nmap-own-lab-guide"),
        ("Wireshark", "https://www.wireshark.org/", "Watch real packets and understand what the network is doing.", "wireshark-basics")]),
    ("kit.web", "Web security", "Web security", [
        ("Browser DevTools", "https://developer.chrome.com/docs/devtools", "Already in your browser. Inspect requests, cookies and headers.", "browser-devtools-for-security"),
        ("Burp Suite Community", "https://portswigger.net/burp/communitydownload", "Free proxy for learning web testing on practice labs.", "burp-suite-intro-practice")]),
    ("kit.safe", "Everyday safety", "Everyday safety", [
        ("A password manager", None, "One strong, unique password for every account, without remembering them all.", "strong-passwords-password-managers"),
        ("An authenticator app or passkeys", None, "A second step that a stolen password alone cannot pass.", "two-factor-authentication-guide"),
        ("SHA-256 checksums", None, "Check that a download is the real file: sha256sum on Linux, Get-FileHash on Windows.", "verify-downloads-sha256"),
        ("Sanchar Saathi", "https://sancharsaathi.gov.in/", "Government portal to report fraud calls and check mobile connections in your name.", "sanchar-saathi-guide")]),
    ("kit.practice", "Practice", "Practice", [
        ("picoCTF and OverTheWire", "https://picoctf.org/", "Free, legal beginner challenges.", "ctf-for-beginners"),
        ("CTF Arena on this site", "ctf.html", "111 puzzles across 7 tracks, scored in your browser.", None)]),
]


def kit_main():
    groups = []
    for key, en, hi, items in KIT:
        HI[key] = hi
        cards = []
        for name, url, what, slug in items:
            ext = url and url.startswith("http")
            nm = f'<a href="{url}"{" target=\"_blank\" rel=\"noopener\"" if ext else ""}>{E(name)}</a>' if url else E(name)
            guide = f'<p class="small xp-guide"><span data-i18n="kit.guide">Guide:</span> {plink(slug)}</p>' if slug else ""
            cards.append(f"""          <article class="card xp-tool">
            <h3 class="h4">{nm}</h3>
            <p class="muted small">{E(what)}</p>
            {guide}
          </article>""")
        groups.append(f"""    <section class="section xp-sec xp-kit" aria-labelledby="{key}-h">
      <div class="wrap">
        <h2 id="{key}-h" data-i18n="{key}">{en}</h2>
        <div class="xp-grid">
{chr(10).join(cards)}
        </div>
      </div>
    </section>""")
    HI["kit.guide"] = "Guide:"
    note = t("kit.note", 'Only scan, test or capture traffic on systems you own or have written permission to test. Unauthorised access is an offence under the IT Act 2000 (sections 43 and 66). See the <a href="terms.html">terms</a>.',
             'Sirf apne systems pe ya likhit permission ke saath hi scan, test ya traffic capture karo. Bina permission access IT Act 2000 (section 43 aur 66) ke under offence hai. <a href="terms.html">Terms</a> dekho.', "p", "small muted xp-note")
    return f"""  <main id="main" tabindex="-1">
{hero("kit", "ls ~/toolkit", "Free cybersecurity toolkit", "The free tools the guides on this site teach, grouped by what you want to do. Each one links to its official site and to a step by step guide here.", "Is site ke guides jo free tools sikhate hain, kaam ke hisaab se group kiye hue. Har tool ki official site aur yahan ka step by step guide linked hai.", crumbs("Toolkit") + "        " + note + "\n")}

{chr(10).join(groups)}
  </main>"""


# ---------------- Collaborate / media kit ----------------
def collab_main():
    topics = [("col.t1", "Scam awareness for families and senior citizens", "Families aur senior citizens ke liye scam awareness"),
              ("col.t2", "Online safety for school and college students", "School aur college students ke liye online safety"),
              ("col.t3", "Starting a cybersecurity career in India", "India mein cybersecurity career kaise shuru karein"),
              ("col.t4", "Cyber law basics: the IT Act, BNS and the DPDP Act", "Cyber law basics: IT Act, BNS aur DPDP Act"),
              ("col.t5", "Home labs and CTF practice for beginners", "Beginners ke liye home lab aur CTF practice")]
    tl = "\n".join(f'            <li>{t(k, en, hi, "span")}</li>' for k, en, hi in topics)
    ways = [("col.w1", "Awareness sessions for schools, colleges, housing societies and teams", "Schools, colleges, housing societies aur teams ke liye awareness sessions"),
            ("col.w2", "Guest articles, interviews and podcast or video collaborations", "Guest articles, interviews aur podcast ya video collaborations"),
            ("col.w3", "Corrections and topic ideas for the guides on this site", "Is site ke guides ke liye corrections aur topic ideas")]
    wl = "\n".join(f'            <li>{t(k, en, hi, "span")}</li>' for k, en, hi in ways)
    soc = "\n".join(f'            <li><a href="{u}" target="_blank" rel="me noopener">{n}</a> <span class="muted small mono">{E(u.split("//")[1].rstrip("/"))}</span></li>' for n, u in SOCIALS)
    sw = "".join(f'<li><span class="xp-sw xp-sw-{n}" aria-hidden="true"></span><span class="mono small">{c}</span> <span class="muted small">{lbl}</span></li>'
                 for n, c, lbl in [("bg", "#0D0B14", "background"), ("p", "#8B5CF6", "purple"), ("g", "#22C55E", "green")])
    bio = ("Madhav Pandya is a cybersecurity educator from Mumbai and the founder of CyberWithMadhav. He explains cybersecurity, "
           "scam awareness and Indian cyber law in plain English and Hinglish. He is studying for a BCA in Cloud Computing and "
           "Cyber Security and a BA LLB at KES Shri J.P. Law College.")
    return f"""  <main id="main" tabindex="-1">
{hero("col", "./collaborate --hello", "Collaborate with CyberWithMadhav", "Want a cyber awareness session, an interview or a collab? Here is what I talk about, a short bio you can use, and how to reach me.", "Cyber awareness session, interview ya collab chahiye? Yahan hai main kin topics pe baat karta hoon, ek short bio jo aap use kar sakte ho, aur contact kaise karein.", crumbs("Collaborate") + f'        <div class="xp-btns"><a class="btn btn-primary" href="mailto:{EMAIL}?subject=Collaboration%20with%20CyberWithMadhav">Email {EMAIL}</a><a class="btn btn-ghost" href="https://www.linkedin.com/in/pandyamadhav/" target="_blank" rel="me noopener">Message on LinkedIn</a></div>\n')}

    <section class="section xp-sec" aria-label="Topics and ways to collaborate">
      <div class="wrap xp-grid2">
        <article class="card">
          {t("col.topics.h", "Topics I talk about", "Main in topics pe baat karta hoon", "h2", "h3")}
          <ul class="xp-list">
{tl}
          </ul>
        </article>
        <article class="card">
          {t("col.ways.h", "Ways to work together", "Saath kaam karne ke tareeke", "h2", "h3")}
          <ul class="xp-list">
{wl}
          </ul>
          {t("col.ways.p", "Send the date, the audience and the language you prefer (English, Hindi or Hinglish). I reply by email.", "Date, audience aur language (English, Hindi ya Hinglish) bhejo. Main email pe reply karta hoon.", "p", "small muted")}
        </article>
      </div>
    </section>

    <section class="section xp-sec" id="media-kit" aria-labelledby="col-kit-h">
      <div class="wrap">
        {t("col.kit.h", "Media kit", "Media kit", "h2").replace("<h2", '<h2 id="col-kit-h"', 1)}
        <div class="xp-grid2">
          <article class="card">
            <h3 class="h4" data-i18n="col.bio.h">Short bio</h3>
            <p class="xp-bio">{E(bio)}</p>
            <p class="small muted"><span data-i18n="col.bio.note">Free to use with a link to</span> <a href="https://www.cyberwithmadhav.com/">cyberwithmadhav.com</a>.</p>
          </article>
          <article class="card">
            <h3 class="h4" data-i18n="col.brand.h">Brand and photo</h3>
            <ul class="xp-swatches clean">{sw}</ul>
            <p class="small muted">Fonts: Space Grotesk (headings) and Inter (text).</p>
            <p class="small"><a href="assets/img/madhav.jpg" data-i18n="col.photo">Profile photo (JPG)</a> · <a href="favicon.svg" data-i18n="col.logo">Logo mark (SVG)</a> · <a href="assets/img/icon-512.png">Icon (PNG, 512 px)</a></p>
          </article>
          <article class="card">
            <h3 class="h4" data-i18n="col.where.h">Where to find me</h3>
            <ul class="xp-list clean">
{soc}
              <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
            </ul>
          </article>
        </div>
      </div>
    </section>
  </main>"""


def i18n_block():
    HI.update({"foot.start": "Yahan se shuru karo", "foot.now": "Abhi", "foot.kit": "Toolkit", "foot.collab": "Collaborate",
               "col.bio.h": "Short bio", "col.bio.note": "Free use karo, bas link dena", "col.brand.h": "Brand aur photo",
               "col.photo": "Profile photo (JPG)", "col.logo": "Logo mark (SVG)", "col.where.h": "Main kahan milunga",
               "sh.safe.game": "Practice: Scam ya Nahi? khelo", "sh.safe.enc": "Scam encyclopedia", "sh.safe.faq": "Quick answers",
               "sh.learn.ctf": "Phir CTF Arena mein practice", "sh.learn.cmd": "Command reference", "sh.learn.kit": "Free toolkit",
               "sh.law.page": "Cyber Law India: poora guide", "sh.law.faq": "Cyber law quick answers",
               "home.start.btn": "Naye ho? Yahan se shuru karo", "home.collab": "Awareness session ya collab chahiye? <a href=\"collaborate.html\">Collaborate</a> dekho."})
    # site wide strings (footer, home) go in the shared dictionary; strings for the four pages go in their own
    # deferred file, so the render blocking i18n-dict.js stays small on every other page
    shared = {k: v for k, v in HI.items() if k.startswith(("foot.", "home."))}
    page = {k: v for k, v in HI.items() if k not in shared}
    pf = ROOT / "assets/js/i18n/page-extras.js"
    pjs = ("/* Hinglish strings for start-here, uses, collaborate and now. Generated by tools/build_extras.py. */\n"
           "window.CWM_I18N_PAGE = Object.assign(window.CWM_I18N_PAGE || {}, %s);\n" % json.dumps(page, ensure_ascii=False, indent=1))
    if not pf.exists() or pf.read_text(encoding="utf-8") != pjs:
        pf.write_text(pjs, encoding="utf-8"); print("wrote assets/js/i18n/page-extras.js")
    path = ROOT / "assets/js/i18n-dict.js"
    d = path.read_text(encoding="utf-8")
    blk = ("/* extras:start (generated by tools/build_extras.py) */\nObject.assign(window.CWM_I18N.hi, %s);\n/* extras:end */"
           % json.dumps(shared, ensure_ascii=False, indent=1))
    if "/* extras:start" in d:
        d2 = re.sub(r"/\* extras:start.*?/\* extras:end \*/", lambda m: blk, d, flags=re.S)
    else:
        d2 = d.replace("/* faq:start", blk + "\n/* faq:start", 1) if "/* faq:start" in d else d.rstrip() + "\n" + blk + "\n"
    if d2 != d:
        path.write_text(d2, encoding="utf-8"); print("wrote assets/js/i18n-dict.js (extras strings)")


def text_files():
    humans = f"""/* TEAM */
  Founder, writer and builder: Madhav Pandya
  Contact: {EMAIL}
  From: Mumbai, India
  LinkedIn: https://www.linkedin.com/in/pandyamadhav/
  YouTube: https://www.youtube.com/@cyberwithmadhav
  Instagram: https://www.instagram.com/cyberwithmadhav/

/* THANKS */
  Everyone who reports a scam at 1930 and cybercrime.gov.in. You protect the next person.

/* SITE */
  Last update: {UPDATED[0].replace("-", "/")}
  Language: English, Hinglish
  Standards: HTML5, CSS3, RSS 2.0, schema.org
  Components: plain HTML, CSS and JavaScript, no framework, no trackers
  Fonts: Space Grotesk, Inter, JetBrains Mono (self hosted)
  Hosting: Hostinger

/* SIDE QUEST */
  You read humans.txt, so you are curious. Good.
  There is a flag in every page source and a shell behind the Konami code.
  Real challenges: https://www.cyberwithmadhav.com/ctf.html
"""
    (ROOT / "humans.txt").write_text(humans, encoding="utf-8")
    wk = ROOT / ".well-known"; wk.mkdir(exist_ok=True)
    sec = f"""# Security contact for www.cyberwithmadhav.com (RFC 9116).
# This is a static educational website. There is no bug bounty, but every good faith report is read and credited if you want.
# Please do not run automated scanners against the live site; describe the issue and how to reproduce it.
Contact: mailto:{EMAIL}
Expires: 2027-11-16T00:00:00+05:30
Preferred-Languages: en, hi
Canonical: https://www.cyberwithmadhav.com/.well-known/security.txt
"""
    (wk / "security.txt").write_text(sec, encoding="utf-8")
    print("wrote humans.txt, .well-known/security.txt")


SPECS = [
    {"file": "start-here.html", "title": "Start Here: Cybersecurity and Scam Safety Guides for Beginners | CyberWithMadhav",
     "desc": "New to CyberWithMadhav? Three simple paths: stay safe from scams, learn cybersecurity from zero with the 15 part Beginner Journey, or understand cyber law in India.",
     "og": "Start here: pick your cybersecurity path", "ogdesc": "Stay safe from scams, learn cybersecurity from zero, or understand cyber law in India. Free guides in English and Hinglish.",
     "keywords": "", "body": "xp-page", "css": ["pages.css", "extras.css"], "js": ["i18n/page-extras.js"], "main_fn": start_main, "ldtype": "CollectionPage", "ldname": "Start here"},
    {"file": "now.html", "title": "Now: What Madhav Pandya Is Focused On | CyberWithMadhav",
     "desc": "What Madhav Pandya is working on right now: studying law and cloud security, writing cybersecurity guides, a book coming soon, and free practice tools.",
     "og": "What I am doing now | Madhav Pandya", "ogdesc": "A short, honest snapshot of what Madhav Pandya is focused on this month.",
     "keywords": "", "body": "xp-page", "css": ["pages.css", "extras.css"], "js": ["i18n/page-extras.js"], "main_fn": now_main, "ldtype": "AboutPage", "ldname": "Now"},
    {"file": "uses.html", "title": "Free Cybersecurity Toolkit for Beginners: Nmap, Wireshark, Burp and More | CyberWithMadhav",
     "desc": "Free tools for learning cybersecurity and staying safe: VirtualBox, Linux, Nmap, Wireshark, Burp Suite Community, DevTools, password managers and Sanchar Saathi, each with a guide.",
     "og": "Free cybersecurity toolkit for beginners", "ogdesc": "The free tools the CyberWithMadhav guides teach, with official links and step by step guides.",
     "keywords": "", "body": "xp-page", "css": ["pages.css", "extras.css"], "js": ["i18n/page-extras.js"], "main_fn": kit_main, "ldtype": "CollectionPage", "ldname": "Toolkit"},
    {"file": "collaborate.html", "title": "Collaborate and Media Kit: Cyber Awareness Sessions | CyberWithMadhav",
     "desc": "Invite Madhav Pandya for cyber awareness sessions, interviews or collaborations. Topics, a short bio, brand colours, photo and contact details.",
     "og": "Collaborate with CyberWithMadhav", "ogdesc": "Cyber awareness sessions, interviews and collabs. Topics, short bio, media kit and contact.",
     "keywords": "", "body": "xp-page", "css": ["pages.css", "extras.css"], "js": ["i18n/page-extras.js"], "main_fn": collab_main, "ldtype": "ContactPage", "ldname": "Collaborate"},
]


def main():
    parts = make_page.shell()
    for spec in SPECS:
        s = dict(spec)
        s["main"] = s.pop("main_fn")()
        s["head_html"] = ld_page(s["file"], s["ldname"], s["desc"], s["ldtype"])
        make_page.build(s, *parts)
    i18n_block()
    text_files()
    for f in [s["file"] for s in SPECS] + ["humans.txt", ".well-known/security.txt", "assets/js/i18n-dict.js", "assets/js/i18n/page-extras.js"]:
        txt = (ROOT / f).read_text(encoding="utf-8")
        assert "\u2014" not in txt and "\u2013" not in txt, f


if __name__ == "__main__":
    main()
