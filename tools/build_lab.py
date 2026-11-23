#!/usr/bin/env python3
"""Builds the Email and Link Security Lab pages from scams.html (shared head, nav and footer).
Run: python3 tools/build_lab.py   Then tools/csp_hash.py is not needed: the inline theme script is copied unchanged."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.cyberwithmadhav.com/"
LOCK = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="10.5" width="16" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/></svg>'
AUTHOR = {"@type": "Person", "name": "Madhav Pandya", "url": BASE + "about.html"}
PUB = {"@type": "Organization", "name": "CyberWithMadhav", "url": BASE}

def crumb(name):
    return f'<p class="lab-crumb"><a href="security-lab.html">Security Lab</a> / {name}</p>'

def privacy(text):
    return f'<p class="lab-privacy" role="note">{LOCK}<span>{text}</span></p>'

CTA = '''        <div class="card lab-cta">
          <h2>Email security and phishing workshop for your institute</h2>
          <p class="muted">For colleges, schools and IT teams: how spoofed mail gets through, how to read headers and links like an analyst, and a live check of your own domain's SPF, DKIM and DMARC. Online across India, in person in Mumbai.</p>
          <p><a class="btn btn-primary" href="cybersecurity-awareness-sessions.html" data-goatcounter-click="lab-book-session">Book a session for your institute</a> <a class="btn btn-ghost" href="security-lab.html">All lab tools</a></p>
        </div>
        <div class="s-help" role="note" aria-label="Emergency help">
          <a class="s-call" href="tel:1930"><span>Lost money? Call <b>1930</b></span></a>
          <p>National Cyber Crime Helpline. Then report on <a href="https://cybercrime.gov.in" target="_blank" rel="noopener noreferrer">cybercrime.gov.in</a><span class="sr-only"> (opens in a new tab)</span>. Report fraud calls and SMS on Chakshu at <a href="https://sancharsaathi.gov.in" target="_blank" rel="noopener noreferrer">sancharsaathi.gov.in</a><span class="sr-only"> (opens in a new tab)</span>.</p>
        </div>'''

def other(cur):
    items = [("dns-security-checker.html", "DNS and Email Security Checker"), ("email-header-analyzer.html", "Email Header Forensics"), ("url-forensics.html", "Phishing URL Forensics")]
    return '<p class="lab-more">' + " ".join(f'<a class="btn btn-ghost small" href="{f}">{n}</a>' for f, n in items if f != cur) + '</p>'

PAGES = [
  dict(file="security-lab.html",
    title="Email and Link Security Lab: Free DNS, Header and URL Analysis Tools | CyberWithMadhav",
    desc="Free analyst tools that run in your browser: grade a domain's SPF, DKIM, DMARC and DNSSEC, analyse email headers for spoofing, and dissect phishing links.",
    og="Email and Link Security Lab: DNS posture, header forensics, URL forensics",
    ogd="Three free, privacy-first security tools by CyberWithMadhav. Built for students, IT teams and anyone checking a suspicious email or link.",
    kw="email security tools, spf dkim dmarc checker, email header analyzer, phishing url checker, dns security, security lab india",
    js=[], dns=False,
    schema=lambda u: {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Email and Link Security Lab", "url": u, "inLanguage": "en-IN", "isAccessibleForFree": True,
      "description": "Three browser-based security tools: DNS and email security posture checker, email header forensics and phishing URL forensics.", "author": AUTHOR, "publisher": PUB,
      "hasPart": [{"@type": "WebApplication", "name": n, "url": BASE + f, "applicationCategory": "SecurityApplication", "operatingSystem": "Any"} for f, n in
                  [("dns-security-checker.html", "DNS and Email Security Checker"), ("email-header-analyzer.html", "Email Header Forensics"), ("url-forensics.html", "Phishing URL Forensics")]]},
    main=f'''    <section class="page-hero" aria-labelledby="p-title">
      <div class="wrap">
        <p class="kicker mono"><span class="prompt">$</span> ./lab --dns --headers --links</p>
        <h1 id="p-title">Email and Link Security Lab</h1>
        <p class="lead">Three analyst tools for the way most attacks in India start: an email or a link. Grade any domain's email security, take apart the headers of a suspicious email, and dissect a phishing URL without ever opening it.</p>
        {privacy("<strong>Privacy first.</strong> Header and URL analysis run fully offline in your browser. The DNS checker sends only the domain name you type to Cloudflare's public DNS resolver. No accounts, no cookies, nothing stored on our side.")}
      </div>
    </section>
    <section class="section lab-sec" aria-label="Tools">
      <div class="wrap">
        <div class="lab-cards">
          <article class="card lab-card">
            <span class="lab-tag">DNS over HTTPS</span>
            <h2><a href="dns-security-checker.html" data-goatcounter-click="lab-hub-dns">DNS and Email Security Checker</a></h2>
            <p class="muted">An A to F grade for any domain, with the exact record to fix each problem.</p>
            <ul><li>SPF with recursive lookup count (limit 10)</li><li>DMARC policy, pct and reporting</li><li>DKIM at common selectors</li><li>DNSSEC, CAA, MTA-STS, TLS-RPT, BIMI</li></ul>
          </article>
          <article class="card lab-card">
            <span class="lab-tag">Fully offline</span>
            <h2><a href="email-header-analyzer.html" data-goatcounter-click="lab-hub-headers">Email Header Forensics</a></h2>
            <p class="muted">Paste raw headers and see who really sent the message and how it travelled.</p>
            <ul><li>SPF, DKIM and DMARC verdicts</li><li>Hop by hop route with delays</li><li>Reply-To and Return-Path mismatches</li><li>Indian bank and government impersonation</li></ul>
          </article>
          <article class="card lab-card">
            <span class="lab-tag">Fully offline</span>
            <h2><a href="url-forensics.html" data-goatcounter-click="lab-hub-url">Phishing URL Forensics</a></h2>
            <p class="muted">Peel a suspicious link layer by layer. It is never opened or expanded.</p>
            <ul><li>Punycode and homoglyph detection</li><li>Typosquats of Indian banks, UPI and gov.in</li><li>Redirect wrappers and hidden destinations</li><li>@ tricks, IP hosts, APK downloads</li></ul>
          </article>
        </div>
      </div>
    </section>
    <section class="section lab-method" aria-labelledby="m-h">
      <div class="wrap">
        <h2 id="m-h">Who it is for</h2>
        <p><strong>Students and freshers</strong> learning blue team and SOC skills: these are the same checks an analyst runs during phishing triage. <strong>IT teams at colleges and schools</strong>: see in one minute whether anyone can send email as your principal or your exam cell. <strong>Everyone else</strong>: get a second opinion on a scary email or link before you click.</p>
        <h3>Method and honest limits</h3>
        <ul>
          <li>Results come from public DNS data and from the text you paste. The tools do not open links, log in anywhere or scan servers.</li>
          <li>A browser cannot read another website's HTTP security headers (CORS blocks it), so there is no header grade here. Use a server-side scanner for that.</li>
          <li>Official domain lists cover common Indian banks, payment apps, government portals and big brands. A domain missing from the list is not automatically fake.</li>
          <li>No tool can prove a message is safe. When money or passwords are involved, contact the organisation through its official app or a number you already have.</li>
        </ul>
{CTA}
      </div>
    </section>
'''),
  dict(file="dns-security-checker.html",
    title="DNS and Email Security Checker: SPF, DKIM, DMARC, DNSSEC Grade | CyberWithMadhav",
    desc="Free A to F grade for any domain's email and DNS security: SPF lookups, DMARC policy, DKIM, DNSSEC, CAA, MTA-STS and TLS-RPT, with exact fixes.",
    og="DNS and Email Security Checker: grade SPF, DKIM, DMARC and DNSSEC",
    ogd="Type a domain and get an A to F grade with the exact DNS records to fix. Only the domain name is sent, to Cloudflare DNS.",
    kw="spf checker, dmarc checker, dkim lookup, dnssec check, email security grade, mta-sts check, college domain email security",
    js=["lab-core.js", "lab-dnscheck.js"], dns=True,
    schema=lambda u: {"@context": "https://schema.org", "@type": "WebApplication", "name": "DNS and Email Security Checker", "url": u, "applicationCategory": "SecurityApplication",
      "operatingSystem": "Any", "browserRequirements": "Requires JavaScript", "inLanguage": "en-IN", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
      "description": "Grades a domain's SPF, DMARC, DKIM, DNSSEC, CAA, MTA-STS and TLS-RPT records using DNS over HTTPS, with fixes.", "author": AUTHOR, "publisher": PUB},
    main=f'''    <section class="page-hero" aria-labelledby="p-title">
      <div class="wrap">
        {crumb("DNS and Email Security Checker")}
        <p class="kicker mono"><span class="prompt">$</span> dig +dnssec TXT _dmarc.yourdomain</p>
        <h1 id="p-title">DNS and Email Security Checker</h1>
        <p class="lead">Can someone send email pretending to be your college, company or bank? Type a domain and get an A to F grade for its email and DNS security, with the exact record to add for every problem.</p>
        {privacy("<strong>What leaves your browser:</strong> only the domain name, sent to Cloudflare's public DNS resolver (cloudflare-dns.com) to read public DNS records. Nothing is sent to CyberWithMadhav and nothing is stored.")}
      </div>
    </section>
    <section class="section lab-sec" aria-label="Checker">
      <div class="wrap">
        <div class="card lab-tool">
          <form id="dc-form" class="lab-row" novalidate>
            <label class="sr-only" for="dc-domain">Domain or email address</label>
            <input id="dc-domain" class="lab-input" type="text" inputmode="url" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="example.com or name@example.com" maxlength="253" required>
            <button id="dc-go" class="btn btn-primary" type="submit" data-goatcounter-click="lab-dns-check">Check domain</button>
          </form>
          <div class="lab-try"><span>Try:</span><button type="button" data-dc-try="cyberwithmadhav.com">cyberwithmadhav.com</button><button type="button" data-dc-try="gmail.com">gmail.com</button><button type="button" data-dc-try="vjti.ac.in">vjti.ac.in</button><button type="button" data-dc-try="rbi.org.in">rbi.org.in</button></div>
          <p class="lab-status" id="dc-status" aria-live="polite"></p>
          <div class="lab-result" id="dc-result" hidden aria-live="polite"></div>
          <p><button type="button" class="btn btn-ghost small" id="dc-copy" hidden data-goatcounter-click="lab-dns-copy-report">Copy report</button></p>
          <noscript><p class="lab-empty">This checker needs JavaScript.</p></noscript>
        </div>
      </div>
    </section>
    <section class="section lab-method" aria-labelledby="m-h">
      <div class="wrap">
        <h2 id="m-h">What is checked and how it is graded</h2>
        <p>Each record earns points; the grade is the share of points earned. Email checks weigh the most because spoofed email is the most common way attacks start.</p>
        <ul>
          <li><strong>SPF (35 points):</strong> one valid v=spf1 record, no more than 10 DNS lookups across all includes (RFC 7208), and an ending of ~all or -all.</li>
          <li><strong>DMARC (35 points):</strong> a v=DMARC1 record, policy quarantine or reject, and a rua reporting address.</li>
          <li><strong>DKIM (10 points):</strong> a public key at one of 16 common selectors. Selectors cannot be listed from DNS, so "not found" can mean "not guessed".</li>
          <li><strong>DNSSEC (5), CAA (5), MTA-STS (3) and TLS-RPT (2).</strong> BIMI is shown for information only.</li>
          <li>Domains with no MX record are graded on whether they clearly say they send no email (v=spf1 -all and DMARC reject), which stops spoofing of unused domains.</li>
        </ul>
        <h3>Limits</h3>
        <ul>
          <li>HTTP security headers (CSP, HSTS and others) are not graded: browsers block reading another site's headers (CORS), and this site has no server to do it.</li>
          <li>Results reflect what Cloudflare's resolver sees at that moment. DNS changes can take time to appear.</li>
          <li>A good grade means spoofing your domain is hard. It does not mean your mailboxes or website are secure.</li>
        </ul>
        {other("dns-security-checker.html")}
{CTA}
      </div>
    </section>
'''),
  dict(file="email-header-analyzer.html",
    title="Email Header Analyzer: Spot Spoofed and Phishing Emails Offline | CyberWithMadhav",
    desc="Paste raw email headers to see SPF, DKIM and DMARC results, the hop by hop route, Reply-To tricks and Indian bank or government impersonation. Runs offline.",
    og="Email Header Forensics: who really sent that email?",
    ogd="SPF, DKIM, DMARC, delivery route and impersonation checks for Indian banks and government. Your headers never leave your browser.",
    kw="email header analyzer, check email headers, spoofed email check, phishing email analysis, spf dkim dmarc fail meaning, received headers",
    js=["lab-core.js", "lab-headers.js"], dns=True,
    schema=lambda u: {"@context": "https://schema.org", "@type": "WebApplication", "name": "Email Header Forensics", "url": u, "applicationCategory": "SecurityApplication",
      "operatingSystem": "Any", "browserRequirements": "Requires JavaScript", "inLanguage": "en-IN", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
      "description": "Analyses raw email headers in the browser for authentication results, delivery route and impersonation of Indian banks and government bodies.", "author": AUTHOR, "publisher": PUB},
    main=f'''    <section class="page-hero" aria-labelledby="p-title">
      <div class="wrap">
        {crumb("Email Header Forensics")}
        <p class="kicker mono"><span class="prompt">$</span> grep -i "^received\\|^authentication-results" mail.eml</p>
        <h1 id="p-title">Email Header Forensics</h1>
        <p class="lead">Got an email from "your bank", "the Income Tax Department" or "your HoD" that feels off? Paste its full headers to see whether it passed SPF, DKIM and DMARC, where it really came from, and whether the sender is pretending to be someone else.</p>
        {privacy("<strong>Fully offline.</strong> Headers contain email addresses and IPs, so they are analysed only inside your browser. Nothing is uploaded or saved. The optional DNS lookup below sends just the sender's domain name to Cloudflare DNS, and only if you click it.")}
      </div>
    </section>
    <section class="section lab-sec" aria-label="Analyser">
      <div class="wrap">
        <div class="card lab-tool">
          <h2>Paste the full headers</h2>
          <p class="lab-note">Gmail: open the email, tap the three dots, then <b>Show original</b>. Outlook on the web: open the email, then the three dots, <b>View</b>, <b>View message details</b>. Copy everything from the top.</p>
          <form id="hf-form" novalidate>
            <label class="sr-only" for="hf-input">Raw email headers</label>
            <textarea id="hf-input" class="lab-input" rows="12" spellcheck="false" autocomplete="off" placeholder="Delivered-To: ...&#10;Received: from ...&#10;Authentication-Results: ...&#10;From: ..."></textarea>
            <p class="lab-row lab-actions"><button class="btn btn-primary" type="submit" data-goatcounter-click="lab-headers-analyse">Analyse headers</button><button class="btn btn-ghost" type="button" id="hf-clear">Clear</button></p>
          </form>
          <div class="lab-try"><span>Samples (fictional):</span><button type="button" data-hf-sample="phish" data-goatcounter-click="lab-headers-sample-phish">Fake SBI KYC mail</button><button type="button" data-hf-sample="clean">Genuine college mail</button></div>
          <div class="lab-result" id="hf-result" hidden aria-live="polite"></div>
          <div class="lab-dns" id="hf-dns" hidden>
            <p class="lab-note">Optional: read the public SPF and DMARC records of <code id="hf-dns-dom"></code>. This sends only that domain name to Cloudflare DNS.</p>
            <p><button type="button" class="btn btn-ghost small" id="hf-dns-go" data-goatcounter-click="lab-headers-dns-lookup">Look up SPF and DMARC</button></p>
            <div id="hf-dns-out" aria-live="polite"></div>
          </div>
          <noscript><p class="lab-empty">This analyser needs JavaScript.</p></noscript>
        </div>
      </div>
    </section>
    <section class="section lab-method" aria-labelledby="m-h">
      <div class="wrap">
        <h2 id="m-h">How to read the result</h2>
        <ul>
          <li><strong>DMARC fail</strong> is the strongest spoofing signal: the domain in the From line did not authorise the message.</li>
          <li><strong>Reply-To on another domain</strong>, especially Gmail or another free service, means your reply goes to someone else. Common in fee, invoice and job scams.</li>
          <li><strong>Display name tricks:</strong> "State Bank of India" or "Income Tax Department" as the name, with an address that is not on an official domain such as sbi.co.in, a .bank.in address or incometax.gov.in.</li>
          <li><strong>The route:</strong> read Received lines from the bottom up. Only hops added by your own mail provider can be trusted; earlier ones can be forged.</li>
        </ul>
        <h3>Limits</h3>
        <ul>
          <li>The tool trusts the Authentication-Results line written by your mail provider. If you edit headers before pasting, the result changes.</li>
          <li>A clean result means the headers look consistent. A real, hacked mailbox can still send a scam.</li>
        </ul>
        {other("email-header-analyzer.html")}
{CTA}
      </div>
    </section>
'''),
  dict(file="url-forensics.html",
    title="Phishing URL Checker: Offline Link Forensics for Indian Scams | CyberWithMadhav",
    desc="Dissect a suspicious link without opening it: punycode and lookalike domains, fake bank and gov.in names, redirect wrappers, @ tricks, IP hosts and APK files.",
    og="Phishing URL Forensics: dissect a link without opening it",
    ogd="Lookalike domains of Indian banks, UPI apps and gov.in, hidden redirects and APK traps, checked offline in your browser.",
    kw="phishing url checker, check suspicious link, fake bank website check india, punycode domain, homoglyph attack, typosquatting check, apk link",
    js=["lab-core.js", "lab-url.js"], dns=False,
    schema=lambda u: {"@context": "https://schema.org", "@type": "WebApplication", "name": "Phishing URL Forensics", "url": u, "applicationCategory": "SecurityApplication",
      "operatingSystem": "Any", "browserRequirements": "Requires JavaScript", "inLanguage": "en-IN", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
      "description": "Offline analysis of a URL's structure for phishing signs, including lookalike domains of Indian banks and government portals, without opening it.", "author": AUTHOR, "publisher": PUB},
    main=f'''    <section class="page-hero" aria-labelledby="p-title">
      <div class="wrap">
        {crumb("Phishing URL Forensics")}
        <p class="kicker mono"><span class="prompt">$</span> echo "$URL" | ./dissect --no-follow</p>
        <h1 id="p-title">Phishing URL Forensics</h1>
        <p class="lead">Paste a link, or the whole SMS or WhatsApp message that contains it. See who really owns the domain, whether it imitates an Indian bank, UPI app or government portal, and what is hidden inside redirects and encoding.</p>
        {privacy("<strong>Fully offline. The link is never opened.</strong> Nothing is fetched, previewed or expanded, and nothing leaves your browser. That is why short links like bit.ly stay hidden here: expanding them would mean contacting the shortener.")}
      </div>
    </section>
    <section class="section lab-sec" aria-label="Analyser">
      <div class="wrap">
        <div class="card lab-tool">
          <form id="uf-form" novalidate>
            <label class="lab-h" for="uf-input">Link or message</label>
            <textarea id="uf-input" class="lab-input" rows="4" spellcheck="false" autocomplete="off" placeholder="https://... or paste the whole message" data-short></textarea>
            <p class="lab-row lab-actions"><button class="btn btn-primary" type="submit" data-goatcounter-click="lab-url-analyse">Dissect link</button></p>
          </form>
          <div class="lab-try"><span>Samples:</span>
            <button type="button" data-uf-try="https://hdfcbank.com.secure-login.example/netbanking">brand as subdomain</button>
            <button type="button" data-uf-try="https://www.icicibank.com@203.0.113.9/login">@ trick</button>
            <button type="button" data-uf-try="https://www.google.com/url?q=https%3A%2F%2Fparivahan-echallan.example%2Fpay.apk">hidden APK</button>
            <button type="button" data-uf-try="https://paytn.com/kyc/update">typosquat</button>
            <button type="button" data-uf-try="https://xn--bi-doc.co.in/">homoglyph</button>
            <button type="button" data-uf-try="https://www.onlinesbi.sbi/">real SBI</button>
          </div>
          <div class="lab-result" id="uf-result" hidden aria-live="polite"></div>
          <noscript><p class="lab-empty">This analyser needs JavaScript.</p></noscript>
        </div>
      </div>
    </section>
    <section class="section lab-method" aria-labelledby="m-h">
      <div class="wrap">
        <h2 id="m-h">Read a link like an analyst</h2>
        <ul>
          <li><strong>Find the registrable domain</strong>: read the host from right to left. In hdfcbank.com.secure-login.example the owner is secure-login.example, not HDFC Bank.</li>
          <li><strong>Banks now use .bank.in</strong>, which only RBI-regulated banks can register through IDRBT (RBI circular of 22 April 2025). Government portals end in .gov.in or .nic.in. Read more in <a href="blog-bank-in-domain-india.html">the .bank.in guide</a>.</li>
          <li><strong>Lookalike characters</strong>: Cyrillic "а" and Latin "a" look the same. Browsers show such domains as punycode (xn--) in many cases, which this tool decodes.</li>
          <li><strong>APK links</strong> install apps outside the Play Store. Fake e-challan, KYC and wedding invite APKs are used to steal OTPs.</li>
        </ul>
        <h3>Limits</h3>
        <ul>
          <li>The tool judges the text of the link only. It cannot see the page, and a clean result does not mean a site is safe.</li>
          <li>Lookalike detection compares against a list of official domains of common Indian banks, payment apps, government portals and big brands. Unlisted brands are not covered.</li>
        </ul>
        {other("url-forensics.html")}
{CTA}
      </div>
    </section>
'''),
]

def build():
    src = (ROOT / "scams.html").read_text(encoding="utf-8")
    for p in PAGES:
        url = BASE + p["file"]
        h = src
        h = re.sub(r"<title>.*?</title>", "<title>" + p["title"] + "</title>", h)
        sub = lambda pat, val: re.sub(pat, lambda m: m.group(1) + val, h)
        h = sub(r'(<meta name="description" content=")[^"]*', p["desc"])
        h = re.sub(r'(<meta name="keywords" content=")[^"]*', lambda m: m.group(1) + p["kw"], h)
        h = h.replace(BASE + "scams.html", url)
        for a in ('property="og:title"', 'name="twitter:title"'):
            h = re.sub(r'(' + a + r' content=")[^"]*', lambda m: m.group(1) + p["og"], h)
        for a in ('property="og:description"', 'name="twitter:description"'):
            h = re.sub(r'(' + a + r' content=")[^"]*', lambda m: m.group(1) + p["ogd"], h)
        ld = json.dumps(p["schema"](url), ensure_ascii=False, separators=(",", ":"))
        h = re.sub(r'(<script type="application/ld\+json">\n).*?(\n  </script>)', lambda m: m.group(1) + ld + m.group(2), h, flags=re.S)
        h = h.replace('<link rel="stylesheet" href="assets/css/features.css?v=e695d1ea11">',
                      '<link rel="stylesheet" href="assets/css/features.css?v=e695d1ea11">\n  <link rel="stylesheet" href="assets/css/lab.css?v=2">')
        if p["dns"]:
            h = h.replace("connect-src 'self' https://cyberwithmadhav.goatcounter.com;", "connect-src 'self' https://cyberwithmadhav.goatcounter.com https://cloudflare-dns.com;")
            assert "https://cloudflare-dns.com" in h
        h = h.replace('<body class="v3 scam-page">', '<body class="v3 lab-page">')
        h = h.replace('class="nav-explore active"', 'class="nav-explore"')
        h = re.sub(r'  <main id="main".*?</main>\n', lambda m: '  <main id="main" tabindex="-1">\n' + p["main"] + '  </main>\n', h, flags=re.S)
        js = "".join(f'  <script src="assets/js/{j}?v=2" defer></script>\n' for j in p["js"])
        h = h.replace('  <script src="assets/js/scams.js?v=20b204b82c" defer></script>\n', js)
        assert "scams.js" not in h and "\u2014" not in h and "\u2013" not in h, p["file"]
        (ROOT / p["file"]).write_text(h, encoding="utf-8")
        print("wrote", p["file"])

if __name__ == "__main__":
    build()
