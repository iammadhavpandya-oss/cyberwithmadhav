#!/usr/bin/env python3
"""Build terms.html and privacy.html from the text below (same header, nav and footer as the other pages).
Run: python3 tools/build_legal.py && python3 tools/csp_hash.py
When you change the meaning of the Terms or the Privacy Policy, also bump VERSION in assets/js/consent.js
so every visitor is asked to agree again, and update UPDATED below."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://iammadhavpandya-oss.github.io/cyberwithmadhav/"
UPDATED = "1 November 2026"
UPDATED_ISO = "2026-11-01"
EMAIL = "madhavpandya@zoho.in"

THEME_JS = """
    /* v3: theme before first paint. Saved choice wins, else follow the system. */
    (function(){var d=document.documentElement;d.classList.add('js');try{var t=localStorage.getItem('cwm-theme');if(t!=='light'&&t!=='dark'){t=window.matchMedia&&window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';}d.setAttribute('data-theme',t);var m=document.querySelector('meta[name="theme-color"]');if(m)m.content=t==='light'?'#F6F4FB':'#0D0B14';if(sessionStorage.getItem('cwm-banner')==='hidden')d.classList.add('no-banner');}catch(e){}})();
  """

NAV = """<a href="index.html">Home</a>
        <a href="index.html#roadmap">Roadmap</a>
        <a href="index.html#cheatsheets">Cheat sheets</a>
        <a href="index.html#tools">Tools</a>
        <a href="ctf.html" class="nav-ctf"><span class="nav-ctf-dot" aria-hidden="true"></span>CTF</a>
        <a href="prompts.html">Prompts</a>
        <a href="cyberlaw.html">Cyber Law</a>
        <a href="terms.html" class="nav-legal">Terms</a>
        <a href="privacy.html" class="nav-legal">Privacy</a>"""

THEME_BTN = """<button class="theme-toggle" type="button" aria-label="Switch to light theme" title="Switch theme">
          <span class="tt-track" aria-hidden="true">
            <span class="tt-knob">
              <svg class="tt-sun" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M4.6 4.6l1.6 1.6M17.8 17.8l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.6 19.4l1.6-1.6M17.8 6.2l1.6-1.6"/></svg>
              <svg class="tt-moon" viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M20.5 14.6A8.6 8.6 0 0 1 9.4 3.5a8.6 8.6 0 1 0 11.1 11.1z"/></svg>
            </span>
          </span>
          <span class="tt-label">Theme</span>
        </button>"""

# ---------------------------------------------------------------- Terms
TERMS = [
 ("acceptance", "Acceptance of these terms", [
  "These Terms and Conditions govern your use of the CyberWithMadhav website at iammadhavpandya-oss.github.io/cyberwithmadhav, including every page, the CTF Arena, the CyberPrompts library, the Cyber Law India pages and the downloadable PDFs (together, the \"site\").",
  "By ticking the box on the welcome screen, or by otherwise using the site, you confirm that you have read, understood and agree to these Terms and to our <a href=\"privacy.html\">Privacy Policy</a>. If you do not agree, please do not use the site.",
  "In these Terms, \"we\", \"us\" and \"our\" mean Madhav Pandya, who runs CyberWithMadhav, and \"you\" means any person who visits or uses the site."]),
 ("educational", "Educational purpose only", [
  "The site is a free learning resource on cybersecurity, digital safety and Indian cyber law. All content is provided for general education and awareness.",
  "Nothing on the site is legal advice, professional security advice, financial advice or a substitute for advice from a qualified advocate or security professional. Reading the site does not create a lawyer and client relationship or any other professional relationship with us.",
  "If you have a legal problem, consult a qualified advocate. If you are a victim of cybercrime, report it at <a href=\"https://cybercrime.gov.in/\" target=\"_blank\" rel=\"noopener\">cybercrime.gov.in</a> or call the 1930 helpline."]),
 ("accuracy", "No guarantee of accuracy", [
  "We try to keep the content correct and up to date, and we mark points we are still checking as \"being verified\". However, we do not guarantee that any content is complete, accurate, current or suitable for your purpose.",
  "Laws, rules, notifications, court judgments and official procedures change, sometimes without much notice. Section numbers, penalties, time limits and the status of provisions may have changed since a page was written.",
  "Always check the official source, such as the bare act on indiacode.nic.in, the Gazette of India, the relevant regulator or the court judgment itself, before you rely on anything you read here. If you find an error, please tell us using the contact details below."]),
 ("authorised-use", "Authorised and ethical use only", [
  "Security techniques, commands, tools and prompts on the site are shared so that you can learn, defend systems and carry out testing that you are permitted to do. You may use them only on systems, networks, devices, accounts and data that you own, or for which you have clear written permission from the owner.",
  "In India, accessing a computer, computer system or network, or downloading or damaging data, without the permission of the owner can make you liable to pay compensation under Section 43 of the Information Technology Act, 2000. Doing so dishonestly or fraudulently is a criminal offence under Section 66 of the same Act. Related conduct such as cheating, extortion, criminal intimidation, defamation and stalking can also be offences under the Bharatiya Nyaya Sanhita, 2023 (BNS).",
  "You are solely responsible for making sure that your use of anything you learn here is lawful where you are, and that you have the permissions you need."]),
 ("prohibited", "Prohibited uses", [
  "You must not use the site, or anything you learn or download from it, to:",
  ["attack, scan, probe, exploit or disrupt any system, network or service that you do not own or are not authorised to test;",
   "harass, stalk, threaten, intimidate, impersonate, defame or spy on any person;",
   "commit or help anyone commit fraud, phishing, identity theft, extortion or any other crime;",
   "access, collect or share personal data, passwords or confidential information without a lawful basis;",
   "spread malware, or interfere with the site itself, its hosting or other visitors, for example by overloading it, scraping it at scale or trying to bypass its security; or",
   "break any law that applies to you."],
  "We may report suspected unlawful use to the appropriate authorities."]),
 ("ctf", "CTF rules and fair play", [
  "The CTF Arena puzzles are self contained exercises. They do not involve any live targets, and you must not treat them as permission to test any real system.",
  ["Play fairly. Do not share flags, answers or full solutions publicly, so that other learners can enjoy the challenges.",
   "Do not brute force answers, automate submissions, or scrape challenge data, hints or answers.",
   "Do not attack, probe or try to bypass the scoring, the rate limits or any backend used for the leaderboard.",
   "Use a nickname that is not offensive and does not impersonate anyone. You do not need to use your real name.",
   "We may reset scores, hide nicknames or remove entries that break these rules, at our discretion."],
  "Your practice progress is stored in your own browser, as described in the <a href=\"privacy.html\">Privacy Policy</a>."]),
 ("ai-prompts", "AI prompt usage and data safety", [
  "The CyberPrompts library contains prompts for defensive, educational and authorised security work. When you use a prompt with any AI tool, you are bound by that tool's own terms and by your organisation's policies.",
  ["Never paste OTPs, passwords, PINs, API keys, private keys, session tokens or other secrets into an AI tool.",
   "Never paste client data, personal data, confidential documents or anything you do not have permission to share. Remove or mask identifying details first.",
   "Use only the AI tools your organisation has approved for the type of data involved.",
   "AI output can be wrong, incomplete or invented. Check every answer yourself before you act on it, and never run commands or code you do not understand."],
  "We are not responsible for the output of any AI tool or for what you share with it."]),
 ("pdfs", "Downloadable PDFs", [
  "The cheat sheets and other PDFs on the site are provided for your personal and educational use. You may download, print and share them for non commercial learning, as long as you keep them unchanged.",
  ["Keep the attribution to CyberWithMadhav and Madhav Pandya and any watermark intact.",
   "Do not sell, resell, rent or bundle the PDFs, or include them in paid courses or products, without our written permission.",
   "Do not remove or change the notices, or present the PDFs as your own work."],
  "The PDFs carry the same educational purpose and accuracy limits as the rest of the site."]),
 ("ip", "Intellectual property", [
  "Unless stated otherwise, the text, explanations, cheat sheets, puzzles, prompt sheets, illustrations, page design, layout and code of the site are created by Madhav Pandya for CyberWithMadhav, and all rights in them are reserved.",
  "You may quote short extracts with a clear credit and a link back to the site. Any other copying, reproduction or reuse needs our written permission.",
  "Names, logos and trademarks of other organisations, tools and platforms mentioned on the site belong to their owners. Mentioning them does not mean they endorse us or that we endorse them. Laws, judgments and official documents we refer to remain the works of their respective authorities."]),
 ("third-party", "Third party links", [
  "The site links to other websites, such as government portals, courts, learning platforms and tool vendors, because they are useful sources. We do not control those sites and are not responsible for their content, availability, security or privacy practices.",
  "A link does not mean we endorse the site or its owner. Your use of any linked site is governed by that site's own terms."]),
 ("privacy", "Privacy", [
  "We do not use analytics, advertising or tracking scripts, and the site does not set cookies.",
  "Your browser's local storage keeps a few settings on your own device: your light or dark theme choice, your CTF practice progress and preferences, prompt favourites, cheat sheet lab values, and a record that you accepted these Terms (with the version number). You can clear them at any time through your browser's site data settings.",
  "Full details, including the services the site relies on, are in our <a href=\"privacy.html\">Privacy Policy</a>."]),
 ("liability", "Limitation of liability and indemnity", [
  "The site and all content, tools and downloads are provided free of charge, \"as is\" and \"as available\", without warranties of any kind, whether express or implied, including warranties of accuracy, fitness for a particular purpose or uninterrupted availability.",
  "To the fullest extent permitted by law, CyberWithMadhav and Madhav Pandya are not liable for any loss or damage, whether direct, indirect, incidental or consequential, arising from your use of the site, your reliance on any content, any action you take based on it, or your misuse of any technique, tool or prompt described here.",
  "You agree to indemnify and hold harmless CyberWithMadhav and Madhav Pandya against any claims, losses, liabilities and expenses, including reasonable legal fees, arising from your breach of these Terms or your unlawful or unauthorised use of anything on the site.",
  "Nothing in these Terms limits any liability that cannot be limited under applicable Indian law."]),
 ("law", "Governing law and jurisdiction", [
  "These Terms are governed by the laws of India.",
  "Subject to applicable law, the competent courts at Mumbai, and at Vasai in Palghar district, Maharashtra, shall have exclusive jurisdiction over any dispute arising out of or in connection with these Terms or the site."]),
 ("changes", "Changes to these terms", [
  "We may update these Terms from time to time, for example when the law changes or when we add new features. The date at the top of this page shows when they were last updated.",
  "When we make a significant change, we will ask you to read and accept the updated Terms the next time you visit. Continuing to use the site after that means you accept the updated Terms."]),
 ("contact", "Contact", [
  "Questions about these Terms, requests for permission, or reports of an error or misuse can be sent to Madhav Pandya at <a href=\"mailto:%s\">%s</a>." % (EMAIL, EMAIL),
  "You can also use the contact form on the <a href=\"index.html#contact\">home page</a> when it is available."]),
]

# ---------------------------------------------------------------- Privacy
STORAGE = [
 ("cwm-consent", "Local storage", "That you accepted the Terms and Privacy Policy, the version you accepted and when."),
 ("cwm-theme", "Local storage", "Your light or dark theme choice."),
 ("cwm-ctf-practice-v2, cwm-ctf-prefs, cwm-ctf-ui, cwm-ctf-quotes", "Local storage", "Your CTF practice progress and best scores, your CTF settings (such as sound and motion), and which quotes you have already seen."),
 ("cwm-ctf-session", "Local storage", "Only if a CTF leaderboard backend is connected and you create a nickname: your nickname and sign in token."),
 ("cwm-prompt-favs", "Local storage", "The prompts you marked as favourites."),
 ("cwm-vars", "Local storage", "Lab values you type into the cheat sheets, such as a target IP for your own lab."),
 ("cwm-banner, cwm-stars:*", "Session storage", "Whether you closed the alert banner, and a short cache of public GitHub star counts. Cleared when you close the tab."),
]
PRIVACY = [
 ("summary", "Summary", [
  "CyberWithMadhav is a static website. We do not run analytics, advertising or tracking scripts, we do not set cookies, and you do not need an account to use the site.",
  "A few settings are kept in your own browser so the site remembers your choices. They never leave your device unless you use an optional feature described below."]),
 ("who", "Who we are", [
  "The site is run by Madhav Pandya under the name CyberWithMadhav. You can reach us at <a href=\"mailto:%s\">%s</a>." % (EMAIL, EMAIL)]),
 ("browser", "What is stored in your browser", [
  "The site uses your browser's local storage and session storage. This data stays on your device and is not sent to us.",
  "TABLE",
  "You can remove all of it at any time by clearing site data for this site in your browser settings. If you clear the consent record, you will see the welcome screen again."]),
 ("services", "Services the site relies on", [
  ["<strong>GitHub Pages</strong> hosts the site. Like any web host, GitHub receives technical information such as your IP address when your browser requests a page. See the <a href=\"https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement\" target=\"_blank\" rel=\"noopener\">GitHub General Privacy Statement</a>.",
   "<strong>Google Fonts</strong> serves the fonts used on the pages, so your browser requests font files from Google's servers. See the <a href=\"https://developers.google.com/fonts/faq/privacy\" target=\"_blank\" rel=\"noopener\">Google Fonts privacy FAQ</a>.",
   "<strong>GitHub API</strong>: on the home page, when you scroll near the About section, your browser may fetch public star counts for the listed projects from api.github.com."],
  "We do not receive any personal information from these services."]),
 ("optional", "Optional forms and leaderboard", [
  "The newsletter form, the contact form and the CTF leaderboard work only when an optional backend is connected. At the time of writing, no backend is connected on the live site, so these forms show an email fallback and CTF progress stays in your browser.",
  "If a backend is connected in future, it will store only what you submit: your email address for the newsletter, your name, email and message for the contact form, or your chosen nickname and scores for the leaderboard, along with basic technical data such as an IP address or a hashed IP address used to prevent abuse. It will be used only to reply to you, send the newsletter you asked for, or run the leaderboard, and never sold. We will update this policy before that happens."]),
 ("rights", "Your choices and rights", [
  "You can use the site without giving us any personal information. You can clear browser storage at any time. If you have sent us information by email or a form, you can ask us to access, correct or delete it by writing to <a href=\"mailto:%s\">%s</a>." % (EMAIL, EMAIL)]),
 ("children", "Children", [
  "The site is an educational resource for a general audience. We do not knowingly collect personal information from children. Parents and teachers are welcome to use the awareness content with children."]),
 ("changes", "Changes to this policy", [
  "If we change this policy in a meaningful way, we will update the date above and ask you to accept the updated version on your next visit. This policy forms part of our <a href=\"terms.html\">Terms and Conditions</a>."]),
]


def render_blocks(blocks):
  out = []
  for b in blocks:
    if isinstance(b, list):
      out.append("<ul>" + "".join("<li>%s</li>" % x for x in b) + "</ul>")
    elif b == "TABLE":
      rows = "".join("<tr><th scope=\"row\"><code>%s</code></th><td>%s</td><td>%s</td></tr>" % (escape(k), w, escape(d)) for k, w, d in STORAGE)
      out.append('<div class="tbl-wrap" tabindex="0" role="region" aria-label="Browser storage used by the site"><table class="law legal-tbl"><caption>Browser storage used by the site</caption>'
                 '<thead><tr><th scope="col">Key</th><th scope="col">Where</th><th scope="col">What it holds</th></tr></thead><tbody>' + rows + "</tbody></table></div>")
    else:
      out.append("<p>%s</p>" % b)
  return "\n          ".join(out)


def page(fname, title, h1, kicker, desc, lead, sections, other):
  toc = "\n            ".join('<li><a href="#%s">%s</a></li>' % (sid, escape(t)) for sid, t, _ in sections)
  body = "\n".join(
    """        <section class="legal-sec" id="%s" aria-labelledby="%s-h">
          <h2 id="%s-h"><span class="legal-n mono" aria-hidden="true">%02d</span>%s</h2>
          %s
        </section>""" % (sid, sid, sid, i + 1, escape(t), render_blocks(bl)) for i, (sid, t, bl) in enumerate(sections))
  active = 'class="nav-legal active" aria-current="page"'
  nav = NAV.replace('href="%s" class="nav-legal"' % fname, 'href="%s" %s' % (fname, active))
  html = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} | CyberWithMadhav</title>
  <meta name="description" content="{escape(desc)}">
  <meta name="author" content="Madhav Pandya">
  <meta name="theme-color" content="#0D0B14">
  <meta name="cwm-consent" content="skip">
  <link rel="canonical" href="{BASE}{fname}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="CyberWithMadhav">
  <meta property="og:title" content="{escape(title)} | CyberWithMadhav">
  <meta property="og:description" content="{escape(desc)}">
  <meta property="og:url" content="{BASE}{fname}">
  <meta property="og:locale" content="en_IN">
  <meta name="color-scheme" content="dark light">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'">
  <script>{THEME_JS}</script>
  <script src="assets/js/consent.js"></script>
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
  <link rel="stylesheet" href="assets/css/style.css">
  <link rel="stylesheet" href="assets/css/pages.css">
  <link rel="stylesheet" href="assets/css/legal.css">
</head>
<body class="v3 legal-page">
  <div class="space" aria-hidden="true">
    <div class="nebula"><i class="n1"></i><i class="n2"></i><i class="n3"></i></div>
    <canvas id="starfield"></canvas>
  </div>
  <a class="skip" href="#main">Skip to content</a>

  <header class="nav" id="top">
    <div class="wrap nav-inner">
      <a class="brand" href="index.html" aria-label="CyberWithMadhav home">
        <img src="favicon.svg" alt="" width="28" height="28">
        <span>Cyber<b>With</b>Madhav</span>
      </a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="nav-links" aria-label="Open menu">
        <span></span><span></span>
      </button>
      <nav id="nav-links" aria-label="Primary">
        {nav}
        {THEME_BTN}
      </nav>
    </div>
  </header>

  <main id="main" tabindex="-1">
    <section class="page-hero legal-hero" aria-labelledby="legal-title">
      <div class="wrap">
        <p class="kicker mono">{kicker}</p>
        <h1 id="legal-title">{escape(h1)}</h1>
        <p class="lead">{lead}</p>
        <p class="legal-meta small muted">Last updated: <time datetime="{UPDATED_ISO}">{UPDATED}</time> · Version 1 · <a href="{other[0]}">{other[1]}</a></p>
      </div>
    </section>

    <div class="wrap legal-grid">
      <nav class="legal-toc" aria-label="Contents">
        <p class="legal-toc-h mono">Contents</p>
        <ol>
            {toc}
        </ol>
      </nav>
      <article class="legal-body" id="legal-body">
{body}
      </article>
    </div>
  </main>

  <footer class="footer">
    <div class="wrap">
      <nav class="foot-legal" aria-label="Legal"><a href="terms.html">Terms and Conditions</a><a href="privacy.html">Privacy Policy</a></nav>
      <div class="foot-row">
        <p class="small muted">© <span id="year">2026</span> CyberWithMadhav · Madhav Pandya. Educational content, provided as is.</p>
        <p class="small"><a href="index.html">Back to home</a> · <a href="#top">Back to top ↑</a></p>
      </div>
    </div>
  </footer>

  <button type="button" class="to-top" id="to-top" aria-label="Back to top" hidden>
    <svg class="to-top-ring" viewBox="0 0 44 44" aria-hidden="true"><circle cx="22" cy="22" r="20"/><circle class="p" cx="22" cy="22" r="20" pathLength="100"/></svg>
    <svg class="to-top-arrow" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5.5 11.5 12 5l6.5 6.5"/></svg>
  </button>
  <div class="toast" id="toast" role="status" aria-live="polite" hidden></div>
  <script src="assets/js/space.js" defer></script>
  <script src="assets/js/pages.js" defer></script>
  <script src="assets/js/legal.js" defer></script>
</body>
</html>
"""
  assert "\u2014" not in html and "\u2013" not in html, fname
  (ROOT / fname).write_text(html, encoding="utf-8")
  print("wrote", fname, len(sections), "sections")


page("terms.html", "Terms and Conditions", "Terms and Conditions", "<span class=\"prompt\">$</span> cat terms.md",
     "Terms and Conditions for CyberWithMadhav: educational use only, authorised and ethical use under the IT Act and BNS, CTF fair play, AI prompt safety, PDFs, liability and governing law.",
     "Please read these terms before using CyberWithMadhav. They explain what the site is for, how you may use its content, and the limits of our responsibility.",
     TERMS, ("privacy.html", "Read the Privacy Policy"))
page("privacy.html", "Privacy Policy", "Privacy Policy", "<span class=\"prompt\">$</span> cat privacy.md",
     "Privacy Policy for CyberWithMadhav: no trackers, no analytics, no cookies. What the site keeps in your browser and which services it relies on.",
     "Short version: no trackers, no analytics, no cookies and no account. Here is exactly what stays in your browser and which services the site relies on.",
     PRIVACY, ("terms.html", "Read the Terms and Conditions"))
