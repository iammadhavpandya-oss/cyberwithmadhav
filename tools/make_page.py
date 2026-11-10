#!/usr/bin/env python3
"""Generate the feature pages (commands.html, scams.html, ...) from one shared shell.

The head, nav and footer are copied from prompts.html so every page matches; the page's own <main> lives in
tools/pages/<name>.main.html. build_site.py then adds the social tags, the shared scripts and the nav "More" menu,
and csp_hash.py hashes the inline theme script. Run from the repo root: python3 tools/make_page.py
Idempotent; a spec whose main file is missing is skipped. Pass file names to build only those
(scams.html and commands.html were hand tuned after generation, so rebuild them only on purpose)."""
import html, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://iammadhavpandya-oss.github.io/cyberwithmadhav/"

SPECS = [
    {"file": "commands.html", "title": "Command Reference: Blue Team Commands for Linux, Windows and Cisco | CyberWithMadhav",
     "desc": "60 defensive commands for Linux, Windows, Cisco IOS and cross platform triage, with examples, typical output, blue team use, safety notes and official docs.",
     "og": "Command Reference: 60 blue team commands with safety notes",
     "ogdesc": "Filter by OS and category, search instantly and copy examples for ss, Get-WinEvent, show logging, nmap and more. Defensive use on systems you own.",
     "keywords": "blue team commands, linux commands for security, powershell incident response commands, cisco show commands, netstat ss lsof, cyber security commands hindi",
     "body": "cmd-page", "css": ["pages.css", "features.css"], "js": ["commands.js"]},
    {"file": "scams.html", "title": "Scam Encyclopedia India: 25 Cyber Frauds Explained in Hinglish | CyberWithMadhav",
     "desc": "Digital arrest, UPI collect, KYC SMS, APK wedding cards, task jobs and 20 more Indian scams: how each works, red flags, what to do now, the law and the official source.",
     "og": "Scam Encyclopedia India: 25 frauds decoded",
     "ogdesc": "How each scam works in 3 steps, red flags, what to do in the first hour (call 1930), the law that applies and the official advisory.",
     "keywords": "cyber fraud india, digital arrest scam, upi fraud, kyc scam sms, 1930 helpline, cybercrime.gov.in, scam awareness hindi",
     "body": "scam-page", "css": ["pages.css", "features.css"], "js": ["scams.js"]},
    {"file": "game.html", "title": "Scam ya Nahi? Spot the Scam Game in Hinglish | CyberWithMadhav",
     "desc": "30 made up SMS, WhatsApp, call and email messages from Indian scams and real alerts. Tap Scam or Safe, see the red flags, the Hinglish explanation and when to call 1930.",
     "og": "Scam ya Nahi? Spot the scam in 30 messages",
     "ogdesc": "Swipe or tap Scam or Safe on SMS, WhatsApp, call and email examples. Easy, medium and hard levels, red flags explained in Hinglish, best score saved in your browser.",
     "keywords": "scam ya nahi, spot the scam game, cyber fraud quiz india, sms scam test, whatsapp scam quiz, 1930 helpline, scam awareness hinglish",
     "body": "game-page", "css": ["pages.css", "features.css", "game.css"], "js": ["game.js"],
     "foot": "For awareness and learning only. Messages are made up examples."},
    {"file": "about.html", "title": "Madhav Pandya | Cybersecurity Educator, Vasai, India",
     "desc": "Madhav Pandya is an IT Support Engineer and cybersecurity educator in Vasai, Mumbai, explaining scams and cyber law in plain English and Hinglish.",
     "og": "Madhav Pandya | Cybersecurity Educator, Vasai, India",
     "ogdesc": "IT Support Engineer and founder of CyberWithMadhav. Cybersecurity and scam awareness in plain English and Hinglish.",
     "keywords": "Madhav Pandya, Madhav Pandya cybersecurity, CyberWithMadhav, Madhav Pandya Vasai, cybersecurity educator India, scam awareness Hinglish, cyber law India",
     "body": "about-page", "css": ["pages.css"], "js": [], "ogtype": "profile",
     "head": "about.head.html", "foot": "Content is for awareness and education, not legal advice."},
]


def shell():
    s = (ROOT / "prompts.html").read_text(encoding="utf-8")
    head = s[:s.index("<!-- seo:start")].rstrip() + "\n</head>\n"
    nav = re.search(r'  <header class="nav" id="top">.*?</header>\n', s, re.S).group(0)
    nav = nav.replace(' class="active" aria-current="page"', "")
    nav = re.sub(r"\s*<!-- more:start -->.*?<!-- more:end -->", "", nav, flags=re.S)
    foot = re.search(r'  <footer class="footer">.*?</footer>\n', s, re.S).group(0)
    tail = re.search(r'  <button type="button" class="to-top".*?<div class="toast"[^>]*></div>\n', s, re.S).group(0)
    return head, nav, foot, tail


def build(spec, head, nav, foot, tail):
    main = ROOT / "tools" / "pages" / spec["file"].replace(".html", ".main.html")
    if not main.exists():
        print("skip", spec["file"], "(no", main.name + ")"); return
    url = BASE + spec["file"]
    h = head
    h = re.sub(r"<title>.*?</title>", "<title>" + html.escape(spec["title"], quote=False) + "</title>", h)
    h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + html.escape(spec["desc"]), h)
    h = re.sub(r'(<meta name="keywords" content=")[^"]*', lambda m: m.group(1) + html.escape(spec["keywords"]), h)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, h)
    for k in ("og:title", "twitter:title"):
        h = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*' % k, lambda m: m.group(1) + html.escape(spec["og"]), h)
    for k in ("og:description", "twitter:description"):
        h = re.sub(r'(<meta (?:property|name)="%s" content=")[^"]*' % k, lambda m: m.group(1) + html.escape(spec["ogdesc"]), h)
    if spec.get("ogtype"):
        h = re.sub(r'(<meta property="og:type" content=")[^"]*', lambda m: m.group(1) + spec["ogtype"], h)
    if spec.get("head"):  # extra head tags (profile meta, JSON-LD) from tools/pages/<head file>
        h = h.replace("\n</head>\n", "\n" + (ROOT / "tools" / "pages" / spec["head"]).read_text(encoding="utf-8").rstrip() + "\n</head>\n", 1)
    h = h.replace('  <link rel="stylesheet" href="assets/css/pages.css">\n',
                  "".join(f'  <link rel="stylesheet" href="assets/css/{c}">\n' for c in spec["css"]))
    n = nav.replace(f'<a href="{spec["file"]}">', f'<a href="{spec["file"]}" class="active" aria-current="page">')
    f = foot.replace("Prompts are for learning and defensive or authorised work only. Check every AI answer yourself.",
                     spec.get("foot", "For learning and defensive or authorised work only."))
    scripts = "".join(f'  <script src="assets/js/{j}" defer></script>\n' for j in ["space.js", "pages.js"] + spec["js"])
    page = (h + f'<body class="v3 {spec["body"]}">\n  <div class="space" aria-hidden="true">\n'
            '    <div class="nebula"><i class="n1"></i><i class="n2"></i><i class="n3"></i></div>\n'
            '    <canvas id="starfield"></canvas>\n  </div>\n  <a class="skip" href="#main">Skip to content</a>\n\n'
            + n + "\n" + main.read_text(encoding="utf-8").rstrip() + "\n\n" + f + "\n" + tail + scripts + "</body>\n</html>\n")
    out = ROOT / spec["file"]
    old = out.read_text(encoding="utf-8") if out.exists() else ""
    # keep what build_site.py and csp_hash.py add later, so re-running this does not churn the file
    if old and _norm(old) == _norm(page): return
    out.write_text(page, encoding="utf-8"); print("wrote", spec["file"])


def _norm(s):
    s = re.sub(r"\n\s*<(?:meta (?:property|name)=\"(?:og:image[^\"]*|twitter:[^\"]*)\"|link rel=\"(?:manifest|apple-touch-icon)\")[^>]*>", "", s)
    s = re.sub(r"\n\s*<script src=\"assets/js/(?:pwa|search|nav)\.js\" defer></script>", "", s)
    s = re.sub(r"\s*<!-- more:start -->.*?<!-- more:end -->", "", s, flags=re.S)
    s = re.sub(r"'sha256-[^']+'", "", s)
    return s


def main():
    import sys
    only = [a for a in sys.argv[1:] if a.endswith(".html")]  # e.g. python3 tools/make_page.py game.html
    parts = shell()
    for spec in SPECS:
        if not only or spec["file"] in only: build(spec, *parts)


if __name__ == "__main__":
    main()
