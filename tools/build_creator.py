#!/usr/bin/env python3
"""Writes the creator / media kit page source for cybersecurity-content-creator-india.html.

Outputs:
  tools/pages/cybersecurity-content-creator-india.main.html   the <main> block
  tools/pages/cybersecurity-content-creator-india.head.html   JSON-LD (WebPage about the Person, FAQPage, breadcrumbs)
  assets/js/i18n-dict.js                                      Hinglish strings between /* creator:start */ and /* creator:end */
Then run: python3 tools/make_page.py cybersecurity-content-creator-india.html && python3 tools/build_site.py
Facts only. No follower counts, awards, press or reviews. No em or en dashes. No current employer. BCA shown without the institute."""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.cyberwithmadhav.com/"
FILE = "cybersecurity-content-creator-india.html"
URL = BASE + FILE
E = lambda s: html.escape(s, quote=False)

MAIL = "mailto:contact@cyberwithmadhav.com?subject=Collaboration%20with%20CyberWithMadhav&body=Hello%20Madhav%2C%0A%0AOrganisation%20or%20channel%3A%0AWhat%20we%20have%20in%20mind%20(session%2C%20interview%2C%20guest%20post%2C%20collab)%3A%0APreferred%20date%3A%0ALanguage%20(English%2C%20Hindi%2C%20Hinglish)%3A%0A%0AThank%20you."

# (key, english, hinglish) for text blocks
T = {
 "h1": ("cybersecurity content creator in India", "India ka cybersecurity content creator"),
 "lead": ("I make cybersecurity awareness content from Mumbai: short posts and videos on Instagram and YouTube, plus guides, scam alerts and free lessons on this website, in plain English and Hinglish. I am an early stage creator and I would rather be useful than loud.",
          "Main Mumbai se cybersecurity awareness content banata hoon: Instagram aur YouTube pe short posts aur videos, aur is website pe guides, scam alerts aur free lessons, simple English aur Hinglish mein. Main abhi shuruaati stage ka creator hoon, aur shor se zyada kaam ka banna chahta hoon."),
 "who.h": ("Who is Madhav Pandya?", "Madhav Pandya kaun hai?"),
 "who.p1": ("Madhav Pandya is a cybersecurity content creator based in Mumbai, India, and the founder of CyberWithMadhav. He explains online safety, scams and Indian cyber law to beginners and families, in plain English and Hinglish, without jargon and without fear tactics.",
            "Madhav Pandya Mumbai (India) mein rehne wale cybersecurity content creator hain aur CyberWithMadhav ke founder. Wo online safety, scams aur Indian cyber law beginners aur families ko simple English aur Hinglish mein samjhate hain, bina jargon aur bina darr ke."),
 "who.p2": ("He is studying for a BA LLB at KES Shri J.P. Law College and a BCA with a specialisation in Cloud Computing and Cyber Security. He also runs cyber awareness sessions for colleges and other groups. You can read the long version on the <a href=\"about.html\">About page</a>.",
            "Wo KES Shri J.P. Law College se BA LLB aur Cloud Computing aur Cyber Security specialisation ke saath BCA kar rahe hain. Wo colleges aur doosre groups ke liye cyber awareness sessions bhi lete hain. Poori kahani <a href=\"about.html\">About page</a> pe hai."),
 "make.h": ("What I create", "Main kya banata hoon"),
 "make.p": ("Everything is made for people in India and keeps to official sources, with links, so you can check it yourself.",
            "Sab kuch India ke logon ke liye hai aur official sources ke saath, links ke saath, taaki aap khud check kar sakein."),
 "plat.h": ("Where to find the content", "Content kahan milega"),
 "plat.p": ("The same topics appear on each platform in a different format. I do not share follower numbers here because they change, so please look at the profiles yourself.",
            "Wahi topics har platform pe alag format mein aate hain. Follower numbers yahan nahi likhta kyunki wo badalte rehte hain, profiles khud dekh lijiye."),
 "sess.h": ("Cyber awareness sessions for colleges", "Colleges ke liye cyber awareness sessions"),
 "sess.p": ("I run cyber awareness sessions and guest lectures for colleges, schools, clubs and community groups. They are online across India and in person in Mumbai, usually 60 to 90 minutes for college students, with time for questions. They are awareness sessions, not legal advice.",
            "Main colleges, schools, clubs aur community groups ke liye cyber awareness sessions aur guest lectures leta hoon. Ye poore India mein online aur Mumbai mein in person hote hain, college students ke liye aam taur pe 60 se 90 minute, sawaalon ke time ke saath. Ye awareness sessions hain, legal advice nahi."),
 "bg.h": ("Background", "Background"),
 "bg.p": ("Education: BA LLB at KES Shri J.P. Law College (in progress). BCA with a specialisation in Cloud Computing and Cyber Security (in progress). Diploma in Cloud Computing (completed).",
          "Education: KES Shri J.P. Law College se BA LLB (chal raha hai). Cloud Computing aur Cyber Security specialisation ke saath BCA (chal raha hai). Diploma in Cloud Computing (complete)."),
 "bg.c": ("Certifications and courses: Cisco Introduction to Cybersecurity, a cybersecurity and penetration testing professional certification, Oracle Cloud Infrastructure AI Associate, Oracle Virtualization, Agile Project Management (HP LIFE) and Prompt Engineering (Infosys Springboard).",
          "Certifications aur courses: Cisco Introduction to Cybersecurity, ek cybersecurity aur penetration testing professional certification, Oracle Cloud Infrastructure AI Associate, Oracle Virtualization, Agile Project Management (HP LIFE) aur Prompt Engineering (Infosys Springboard)."),
 "bg.b": ("A cybersecurity book for beginners is in progress. There is no title or date yet. Follow on Instagram or YouTube for updates.",
          "Beginners ke liye ek cybersecurity book likhi ja rahi hai. Abhi title ya date nahi hai. Updates ke liye Instagram ya YouTube follow karein."),
 "col.h": ("Collaborate or contact", "Collaborate ya contact"),
 "col.p": ("I am open to awareness sessions, interviews, podcast or video collaborations, guest articles, and corrections or topic ideas. Email with the date, the audience and the language you prefer (English, Hindi or Hinglish). I reply personally, usually by email.",
           "Main awareness sessions, interviews, podcast ya video collabs, guest articles, aur corrections ya topic ideas ke liye available hoon. Date, audience aur pasand ki language (English, Hindi ya Hinglish) ke saath email karein. Main khud reply karta hoon, aam taur pe email pe."),
 "col.btn": ("Email to collaborate", "Collaborate ke liye email karo"),
 "col.kit": ("Short bio, photo and logo are on the <a href=\"collaborate.html\">collaborate and media kit page</a>. To book a session, see <a href=\"cybersecurity-awareness-sessions.html\">cyber security awareness sessions</a>.",
             "Short bio, photo aur logo <a href=\"collaborate.html\">collaborate aur media kit page</a> pe hain. Session book karne ke liye <a href=\"cybersecurity-awareness-sessions.html\">cyber security awareness sessions</a> dekho."),
 "faq.h": ("Frequently asked questions", "Aksar pooche jaane wale sawaal"),
 "rel.h": ("More from CyberWithMadhav", "CyberWithMadhav se aur"),
}

TOPICS = [
 ("Scam awareness for families and senior citizens: UPI, OTP, digital arrest, fake KYC and more.", "Families aur senior citizens ke liye scam awareness: UPI, OTP, digital arrest, fake KYC aur bahut kuch."),
 ("Online safety for school and college students.", "School aur college students ke liye online safety."),
 ("Starting a cybersecurity career in India, with a free step by step learning path.", "India mein cybersecurity career shuru karna, free step by step learning path ke saath."),
 ("Cyber law basics in India: the IT Act, BNS and the DPDP Act.", "India mein cyber law basics: IT Act, BNS aur DPDP Act."),
 ("Home labs and CTF practice for beginners, on systems you own.", "Beginners ke liye home labs aur CTF practice, sirf apne systems pe."),
]
PLATFORMS = [
 ("Instagram", "https://www.instagram.com/cyberwithmadhav/", "@cyberwithmadhav: short scam alerts and safety tips"),
 ("YouTube", "https://www.youtube.com/@cyberwithmadhav", "@cyberwithmadhav: videos on cybersecurity and scam awareness"),
 ("Website", "/", "cyberwithmadhav.com: blog, free lessons, scam encyclopedia, cheat sheets and CTF practice"),
 ("LinkedIn", "https://www.linkedin.com/in/pandyamadhav/", "Professional profile of Madhav Pandya"),
 ("GitHub", "https://github.com/iammadhavpandya-oss", "Small defensive Python and OSINT projects"),
]
FAQS = [
 ("who", "Who is Madhav Pandya?",
  "Madhav Pandya is a cybersecurity content creator from Mumbai, India, and the founder of CyberWithMadhav. He creates scam awareness, cyber law and online safety content in plain English and Hinglish on Instagram, YouTube and cyberwithmadhav.com, and he runs cyber awareness sessions for colleges and community groups. He is studying for a BA LLB and a BCA in Cloud Computing and Cyber Security.",
  "Madhav Pandya Mumbai, India ke cybersecurity content creator hain aur CyberWithMadhav ke founder. Wo Instagram, YouTube aur cyberwithmadhav.com pe scam awareness, cyber law aur online safety content simple English aur Hinglish mein banate hain, aur colleges aur community groups ke liye cyber awareness sessions lete hain. Wo BA LLB aur Cloud Computing aur Cyber Security mein BCA kar rahe hain."),
 ("what", "What is CyberWithMadhav?",
  "CyberWithMadhav is a cybersecurity awareness project started by Madhav Pandya. It includes Instagram and YouTube content and this website, which has a blog, free lessons, a scam encyclopedia, cyber law guides, cheat sheets and CTF practice, all in plain English and Hinglish.",
  "CyberWithMadhav Madhav Pandya ka shuru kiya hua cybersecurity awareness project hai. Isme Instagram aur YouTube content aur ye website hai, jisme blog, free lessons, scam encyclopedia, cyber law guides, cheat sheets aur CTF practice hain, sab simple English aur Hinglish mein."),
 ("creator", "Who is a cybersecurity content creator in India?",
  "A cybersecurity content creator in India is someone who explains online safety, scams and security topics to the public through posts, videos and guides. There are many such creators across India. Madhav Pandya is one of them: an emerging creator based in Mumbai who focuses on scam awareness, Indian cyber law and beginner learning in English and Hinglish.",
  "India mein cybersecurity content creator wo hota hai jo posts, videos aur guides ke zariye online safety, scams aur security topics aam logon ko samjhata hai. India mein aise kai creators hain. Madhav Pandya unme se ek hain: Mumbai ke ek ubharte hue creator jo scam awareness, Indian cyber law aur beginners ke learning pe English aur Hinglish mein kaam karte hain."),
 ("influencer", "Is Madhav Pandya a cybersecurity influencer?",
  "He is an early stage, growing cybersecurity content creator, not a celebrity influencer. He does not sell fear or hype. The focus is practical, checkable guidance for Indian audiences, with links to official sources.",
  "Wo shuruaati stage ke, badhte hue cybersecurity content creator hain, celebrity influencer nahi. Wo darr ya hype nahi bechte. Focus India ke audience ke liye practical, check karne layak guidance pe hai, official sources ke links ke saath."),
 ("topics", "What topics does he cover?",
  "Scam awareness for families and senior citizens, online safety for students, starting a cybersecurity career in India, cyber law basics (the IT Act, BNS and the DPDP Act), and home labs and CTF practice for beginners.",
  "Families aur senior citizens ke liye scam awareness, students ke liye online safety, India mein cybersecurity career shuru karna, cyber law basics (IT Act, BNS aur DPDP Act), aur beginners ke liye home labs aur CTF practice."),
 ("sessions", "Does he run cyber awareness sessions for colleges?",
  "Yes. He runs awareness sessions and guest lectures for colleges, schools, clubs and community groups, online across India and in person in Mumbai. See the cyber security awareness sessions page for packages and how to book.",
  "Haan. Wo colleges, schools, clubs aur community groups ke liye awareness sessions aur guest lectures lete hain, poore India mein online aur Mumbai mein in person. Packages aur booking ke liye cyber security awareness sessions page dekho."),
 ("where", "Where is Madhav Pandya based?",
  "He is based in Mumbai, Maharashtra, India. Online sessions and collaborations are open across India.",
  "Wo Mumbai, Maharashtra, India mein rehte hain. Online sessions aur collaborations poore India ke liye khule hain."),
 ("contact", "How can I contact Madhav Pandya or collaborate?",
  "Email contact@cyberwithmadhav.com with the date, the audience and the language you prefer. You can also message him on LinkedIn or Instagram. He replies personally.",
  "contact@cyberwithmadhav.com pe date, audience aur pasand ki language ke saath email karein. LinkedIn ya Instagram pe bhi message kar sakte hain. Wo khud reply karte hain."),
]
RELATED = [("about.html", "About Madhav Pandya"), ("blog.html", "Cybersecurity blog"), ("scams.html", "Scam encyclopedia"),
           ("learn.html", "Free cybersecurity lessons"), ("cyberlaw.html", "Cyber law India"), ("cybersecurity-awareness-sessions.html", "Awareness sessions"),
           ("cyber-awareness-speaker-mumbai.html", "Cyber awareness speaker in Mumbai"), ("collaborate.html", "Collaborate and media kit")]

# Footer and byline strings used sitewide by build_site.py
SITEWIDE_HI = {
 "foot.creator": "Madhav Pandya Mumbai se ek <a href=\"cybersecurity-content-creator-india.html\">cybersecurity content creator (India)</a> hain.",
 "blog.bycreator": "Madhav Pandya, Mumbai (India) se cybersecurity content creator",
 "about.lead": "Main Madhav Pandya hoon, India ka cybersecurity content creator, Mumbai se, aur CyberWithMadhav ka founder. Main Instagram, YouTube aur is website pe cybersecurity aur scam awareness simple English aur Hinglish mein samjhata hoon.",
 "about.h1role": "cybersecurity content creator, India",
 "about.kit": "Collaboration, interview ya college session ke liye mera <a href=\"cybersecurity-content-creator-india.html\">creator page</a> dekho.",
}


def main_html():
    def t(k): return f'data-i18n="crt.{k}"'
    topics = "\n".join(f'          <li data-i18n="crt.topic{i}">{E(en)}</li>' for i, (en, _) in enumerate(TOPICS))
    plats = "\n".join(
        f'          <li><a href="{u}"{"" if u == "/" else " target=\"_blank\" rel=\"me noopener\""}><strong>{E(n)}</strong></a>: {E(d)}</li>' for n, u, d in PLATFORMS)
    faqs = "\n".join(
        f'''          <details class="card sess-faq">
            <summary><h3 data-i18n="crt.faq.q.{k}">{E(q)}</h3></summary>
            <p data-i18n="crt.faq.a.{k}">{E(a)}</p>
          </details>''' for k, q, a, _ in FAQS)
    rel = " · ".join(f'<a href="{h}">{E(x)}</a>' for h, x in RELATED)
    return f'''  <main id="main" tabindex="-1">
    <section class="page-hero xp-hero" aria-labelledby="p-title">
      <div class="wrap">
        <p class="kicker mono"><span class="prompt">$</span> ./creator --india</p>
        <h1 id="p-title">Madhav Pandya, <span {t("h1")}>{E(T["h1"][0])}</span></h1>
        <p class="lead" {t("lead")}>{E(T["lead"][0])}</p>
        <nav class="xp-crumbs small muted" aria-label="Breadcrumb"><a href="/" data-i18n="blog.home">Home</a> <span aria-hidden="true">/</span> <a href="about.html">About</a> <span aria-hidden="true">/</span> <span aria-current="page">Creator page</span></nav>
        <div class="xp-btns">
          <a class="btn btn-primary" href="{MAIL}" {t("col.btn")}>{E(T["col.btn"][0])}</a>
          <a class="btn btn-ghost" href="https://www.instagram.com/cyberwithmadhav/" target="_blank" rel="me noopener">Instagram</a>
          <a class="btn btn-ghost" href="https://www.youtube.com/@cyberwithmadhav" target="_blank" rel="me noopener">YouTube</a>
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="who" aria-labelledby="crt-who-h">
      <div class="wrap xp-narrow">
        <h2 id="crt-who-h" {t("who.h")}>{E(T["who.h"][0])}</h2>
        <p {t("who.p1")}>{E(T["who.p1"][0])}</p>
        <p {t("who.p2")}>{T["who.p2"][0]}</p>
      </div>
    </section>

    <section class="section xp-sec" id="topics" aria-labelledby="crt-make-h">
      <div class="wrap xp-narrow">
        <h2 id="crt-make-h" {t("make.h")}>{E(T["make.h"][0])}</h2>
        <p {t("make.p")}>{E(T["make.p"][0])}</p>
        <ul class="xp-list">
{topics}
        </ul>
        <p class="small xp-more"><a href="scams.html">Scam encyclopedia</a> · <a href="blog.html">Blog</a> · <a href="learn.html">Learn path</a> · <a href="cyberlaw.html">Cyber law India</a> · <a href="ctf.html">CTF practice</a></p>
      </div>
    </section>

    <section class="section xp-sec" id="platforms" aria-labelledby="crt-plat-h">
      <div class="wrap xp-narrow">
        <h2 id="crt-plat-h" {t("plat.h")}>{E(T["plat.h"][0])}</h2>
        <p {t("plat.p")}>{E(T["plat.p"][0])}</p>
        <ul class="xp-list">
{plats}
        </ul>
      </div>
    </section>

    <section class="section xp-sec" id="sessions" aria-labelledby="crt-sess-h">
      <div class="wrap xp-narrow">
        <h2 id="crt-sess-h" {t("sess.h")}>{E(T["sess.h"][0])}</h2>
        <p {t("sess.p")}>{E(T["sess.p"][0])}</p>
        <p class="small"><a href="cybersecurity-awareness-sessions.html">Cyber security awareness sessions</a> · <a href="cyber-security-workshop-for-colleges.html">College workshop</a> · <a href="cyber-awareness-speaker-mumbai.html">Speaker in Mumbai</a></p>
      </div>
    </section>

    <section class="section xp-sec" id="background" aria-labelledby="crt-bg-h">
      <div class="wrap xp-narrow">
        <h2 id="crt-bg-h" {t("bg.h")}>{E(T["bg.h"][0])}</h2>
        <p {t("bg.p")}>{E(T["bg.p"][0])}</p>
        <p {t("bg.c")}>{E(T["bg.c"][0])}</p>
        <p {t("bg.b")}>{E(T["bg.b"][0])}</p>
      </div>
    </section>

    <section class="section xp-sec" id="collaborate" aria-labelledby="crt-col-h">
      <div class="wrap xp-narrow">
        <h2 id="crt-col-h" {t("col.h")}>{E(T["col.h"][0])}</h2>
        <p {t("col.p")}>{E(T["col.p"][0])}</p>
        <div class="xp-btns">
          <a class="btn btn-primary" href="{MAIL}" {t("col.btn")}>{E(T["col.btn"][0])}</a>
        </div>
        <p class="small" {t("col.kit")}>{T["col.kit"][0]}</p>
        <p class="small muted">contact@cyberwithmadhav.com</p>
      </div>
    </section>

    <section class="section xp-sec" id="faq" aria-labelledby="crt-faq-h">
      <div class="wrap xp-narrow">
        <h2 id="crt-faq-h" {t("faq.h")}>{E(T["faq.h"][0])}</h2>
        <div class="sess-faqs">
{faqs}
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="related" aria-labelledby="crt-rel-h">
      <div class="wrap xp-narrow">
        <h2 id="crt-rel-h" {t("rel.h")}>{E(T["rel.h"][0])}</h2>
        <p class="small">{rel}</p>
      </div>
    </section>
  </main>'''


def head_html():
    page = {"@type": "WebPage", "@id": URL + "#webpage", "url": URL, "name": "Cybersecurity content creator in India: Madhav Pandya",
            "description": "Creator page for Madhav Pandya, a cybersecurity content creator in India based in Mumbai: topics, platforms, college sessions and collaboration.",
            "inLanguage": "en-IN", "isPartOf": {"@id": BASE + "#website"}, "about": {"@id": BASE + "#person"},
            "primaryImageOfPage": {"@type": "ImageObject", "url": BASE + "assets/img/madhav.jpg"}}
    faq = {"@type": "FAQPage", "@id": URL + "#faqpage", "url": URL, "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for _, q, a, _ in FAQS]}
    crumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": "About", "item": BASE + "about.html"},
        {"@type": "ListItem", "position": 3, "name": "Cybersecurity content creator in India", "item": URL}]}
    ld = {"@context": "https://schema.org", "@graph": [page, faq, crumbs]}
    return '  <script type="application/ld+json">\n  ' + json.dumps(ld, ensure_ascii=False) + "\n  </script>\n"


def i18n_block():
    d = dict(SITEWIDE_HI)
    for k, (_, hi) in T.items(): d["crt." + k] = hi
    for i, (_, hi) in enumerate(TOPICS): d[f"crt.topic{i}"] = hi
    for k, _, _, hi in FAQS:
        d[f"crt.faq.q.{k}"] = {"who": "Madhav Pandya kaun hai?", "what": "CyberWithMadhav kya hai?", "creator": "India mein cybersecurity content creator kaun hota hai?",
                               "influencer": "Kya Madhav Pandya cybersecurity influencer hain?", "topics": "Wo kin topics pe kaam karte hain?",
                               "sessions": "Kya wo colleges ke liye cyber awareness sessions lete hain?", "where": "Madhav Pandya kahan rehte hain?",
                               "contact": "Madhav Pandya se contact ya collaborate kaise karein?"}[k]
        d[f"crt.faq.a.{k}"] = hi
    return "/* creator:start (generated by tools/build_creator.py) */\nObject.assign(window.CWM_I18N.hi, %s);\n/* creator:end */" % json.dumps(d, ensure_ascii=False, indent=1)


def main():
    pages = ROOT / "tools" / "pages"
    (pages / FILE.replace(".html", ".main.html")).write_text(main_html() + "\n", encoding="utf-8")
    (pages / FILE.replace(".html", ".head.html")).write_text(head_html(), encoding="utf-8")
    p = ROOT / "assets/js/i18n-dict.js"
    d = p.read_text(encoding="utf-8"); blk = i18n_block()
    d2 = re.sub(r"/\* creator:start.*?/\* creator:end \*/", lambda m: blk, d, flags=re.S) if "/* creator:start" in d else d.rstrip() + "\n" + blk + "\n"
    if d2 != d: p.write_text(d2, encoding="utf-8"); print("wrote assets/js/i18n-dict.js (creator strings)")
    print("wrote creator page sources")


if __name__ == "__main__":
    main()
