"""Source for three session landing pages. Built by tools/build_extras.py."""
import html, json
from urllib.parse import quote

import sessions_src

EMAIL = sessions_src.EMAIL
BASE = sessions_src.BASE
E = lambda s: html.escape(s, quote=True)
HI = {}
MAILTO = sessions_src.MAILTO


def t(key, en, hi, tag="p", cls=""):
    HI[key] = hi
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c} data-i18n="{key}">{en}</{tag}>'


def crumbs(name, current):
    return (
        '        <nav class="xp-crumbs small muted" aria-label="Breadcrumb">'
        '<a href="index.html" data-i18n="blog.home">Home</a> <span aria-hidden="true">/</span> '
        '<a href="cybersecurity-awareness-sessions.html">Cybersecurity awareness sessions</a> '
        f'<span aria-hidden="true">/</span> <span aria-current="page">{E(current)}</span></nav>\n'
    )


def book_block(key_prefix):
    return f'''        <div class="xp-btns">
          <a class="btn btn-primary" href="{MAILTO}" data-i18n="sess.cta">Email to book a session</a>
          <a class="btn btn-ghost" href="cybersecurity-awareness-sessions.html" data-i18n="{key_prefix}.all">See all packages and booking details</a>
        </div>
        {t("sess.reply", "I reply personally. No forms, no spam.", "Main personally reply karta hoon. Koi form nahi, koi spam nahi.", "p", "small muted")}
'''


def faq_block(items, prefix):
    parts = []
    for it in items:
        qk, ak = f"{prefix}.faq.q.{it['id']}", f"{prefix}.faq.a.{it['id']}"
        HI[qk] = it["hi_q"]
        HI[ak] = it["hi_a"]
        parts.append(
            f'          <details class="card sess-faq">\n'
            f'            <summary><h3 data-i18n="{qk}">{E(it["q"])}</h3></summary>\n'
            f'            <p data-i18n="{ak}">{E(it["a"])}</p>\n'
            f'          </details>'
        )
    return "\n".join(parts)


def page_ld(file, name, desc, faqs, service_name, service_type):
    url = BASE + file
    person = {
        "@type": "Person",
        "@id": BASE + "about.html#person",
        "name": "Madhav Pandya",
        "url": BASE + "about.html",
        "jobTitle": "Cybersecurity Educator and Founder, CyberWithMadhav",
        "email": "mailto:" + EMAIL,
        "sameAs": [
            "https://www.linkedin.com/in/pandyamadhav/",
            "https://www.instagram.com/cyberwithmadhav/",
            "https://www.youtube.com/@cyberwithmadhav",
            "https://github.com/iammadhavpandya-oss",
        ],
    }
    service = {
        "@type": "Service",
        "@id": url + "#service",
        "name": service_name,
        "serviceType": service_type,
        "description": desc,
        "url": url,
        "provider": person,
        "areaServed": [
            {"@type": "Country", "name": "India"},
            {"@type": "City", "name": "Mumbai", "containedInPlace": {"@type": "State", "name": "Maharashtra"}},
        ],
        "email": EMAIL,
        "isRelatedTo": {"@id": BASE + "cybersecurity-awareness-sessions.html#service"},
    }
    faq = {
        "@type": "FAQPage",
        "@id": url + "#faqpage",
        "url": url,
        "mainEntity": [
            {"@type": "Question", "name": it["q"], "acceptedAnswer": {"@type": "Answer", "text": it["a"]}}
            for it in faqs
        ],
    }
    crumbs_ld = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "Cybersecurity awareness sessions", "item": BASE + "cybersecurity-awareness-sessions.html"},
            {"@type": "ListItem", "position": 3, "name": name, "item": url},
        ],
    }
    graph = {"@context": "https://schema.org", "@graph": [service, faq, crumbs_ld]}
    return "  <script type=\"application/ld+json\">\n  " + json.dumps(graph, ensure_ascii=False) + "\n  </script>"


# ---------- colleges ----------
COL_FAQS = [
    {
        "id": "cover",
        "q": "What does a cyber security workshop for college students cover?",
        "hi_q": "College students ke cyber security workshop mein kya cover hota hai?",
        "a": "The usual starting point is UPI fraud, fake job or internship offers, phishing, account takeover, public or campus Wi-Fi, two-factor authentication, and digital arrest awareness. Tell me what your students are worried about and I will shape the session around that.",
        "hi_a": "Usual starting point hai UPI fraud, fake job ya internship offers, phishing, account takeover, public ya campus Wi-Fi, two-factor authentication, aur digital arrest awareness. Batao aapke students kis cheez se worried hain, main session usi ke around shape karunga.",
    },
    {
        "id": "guest",
        "q": "Can you give a guest lecture on cyber security at our college?",
        "hi_q": "Kya aap hamare college mein cyber security pe guest lecture de sakte ho?",
        "a": "Yes. Faculty, student councils and NSS units can email to book a guest lecture or a longer workshop. Online sessions are open to colleges anywhere in India. In-person sessions are for Mumbai campuses only. Please write at least 2 weeks ahead where possible.",
        "hi_a": "Haan. Faculty, student councils aur NSS units email karke guest lecture ya lambe workshop book kar sakte hain. Online sessions India ke kisi bhi college se ho sakte hain. In-person sessions sirf Mumbai campuses ke liye hain. Jahan ho sake, kam se kam 2 hafte pehle likho.",
    },
    {
        "id": "length",
        "q": "How long is a typical college session, and what does it cost?",
        "hi_q": "Typical college session kitni der ki hoti hai, aur fees kya hai?",
        "a": "Most college sessions run 60 to 90 minutes. An extended workshop can go longer if you want a quiz or a hands-on demo on my own test devices. The fee is shared on request, based on audience size and format. I reply with a clear fee before anything is booked.",
        "hi_a": "Zyadatar college sessions 60 se 90 minutes ki hoti hain. Extended workshop lambi ho sakti hai agar aap quiz ya meri test devices pe hands-on demo chahte ho. Fee request pe share ki jaati hai, audience size aur format ke hisaab se. Book hone se pehle main clear fee ke saath reply karta hoon.",
    },
    {
        "id": "not",
        "q": "Is this a placement workshop or legal advice?",
        "hi_q": "Kya ye placement workshop ya legal advice hai?",
        "a": "No. This is an awareness and education session only. It is not a placement or employability workshop, and it is not legal advice. If someone has lost money, they should call 1930 or report at cybercrime.gov.in.",
        "hi_a": "Nahi. Ye sirf awareness aur education session hai. Ye placement ya employability workshop nahi hai, aur legal advice bhi nahi. Agar kisi ka paisa gaya ho, to 1930 pe call karein ya cybercrime.gov.in pe report karein.",
    },
]


def colleges_main():
    HI.update({
        "colp.h1": "Colleges aur universities ke liye cyber security workshop",
        "colp.all": "Saari packages aur booking details dekho",
        "colp.more.sch": "School ke liye cyber safety seminar",
        "colp.more.mum": "Mumbai mein cyber awareness speaker",
    })
    extra = crumbs("colleges", "Workshop for colleges") + book_block("colp")
    return f'''  <main id="main" tabindex="-1">
    <section class="page-hero xp-hero" aria-labelledby="p-title">
      <div class="wrap">
        <p class="kicker mono"><span class="prompt">$</span> ./book --college-workshop</p>
        <h1 id="p-title" data-i18n="colp.h1">Cyber security workshop for colleges and universities</h1>
        {t("colp.lead", "A guest lecture or workshop for students who use UPI, job portals and campus Wi-Fi every day. Online across India. In person at Mumbai campuses.", "Un students ke liye guest lecture ya workshop jo har din UPI, job portals aur campus Wi-Fi use karte hain. Online poore India mein. Mumbai campuses pe in person.", "p", "lead")}
{extra}      </div>
    </section>

    <section class="section xp-sec" id="who" aria-labelledby="colp-who-h">
      <div class="wrap xp-narrow">
        {t("colp.who.h", "Who this workshop is for", "Ye workshop kiske liye hai", "h2").replace("<h2", '<h2 id="colp-who-h"', 1)}
        {t("colp.who.p", "This page is for college faculty, student councils, NSS units and department heads who want a cyber security awareness session their students will actually sit through. It is also useful for coaching batches that want the same topics before internships or a first job.", "Ye page college faculty, student councils, NSS units aur department heads ke liye hai, jo aisi cyber security awareness session chahte hain jisme students sach mein baithen. Coaching batches ke liye bhi useful hai, jo internships ya pehli job se pehle yahi topics chahte hain.", "p")}
      </div>
    </section>

    <section class="section xp-sec" id="topics" aria-labelledby="colp-top-h">
      <div class="wrap xp-narrow">
        {t("colp.top.h", "What a typical college session covers", "Typical college session mein kya aata hai", "h2").replace("<h2", '<h2 id="colp-top-h"', 1)}
        {t("colp.top.p", "I start from scams that college students in India actually face, not generic slides copied from somewhere else. A usual 60 to 90 minute session includes:", "Main un scams se shuru karta hoon jo India mein college students actually face karte hain, kahin se copy ki hui generic slides se nahi. Usual 60 se 90 minute session mein ye aata hai:", "p")}
        <ul class="xp-list">
          <li>{t("colp.t1", "UPI fraud: collect requests, fake refunds and QR codes that should not be trusted blindly.", "UPI fraud: collect requests, fake refunds, aur QR codes jin par andha bharosa nahi karna chahiye.", "span")}</li>
          <li>{t("colp.t2", "Fake job and internship offers, including roles that ask for a registration fee or your OTP.", "Fake job aur internship offers, un roles ke saath jo registration fee ya OTP maange.", "span")}</li>
          <li>{t("colp.t3", "Phishing on email, SMS and WhatsApp, and how account takeover usually starts.", "Email, SMS aur WhatsApp pe phishing, aur account takeover aksar kaise shuru hota hai.", "span")}</li>
          <li>{t("colp.t4", "Campus and public Wi-Fi habits, two-factor authentication, and stronger passwords.", "Campus aur public Wi-Fi ke habits, two-factor authentication, aur strong passwords.", "span")}</li>
          <li>{t("colp.t5", "Digital arrest awareness, and a clear first-hour plan: when to call 1930 and how to report at cybercrime.gov.in.", "Digital arrest awareness, aur clear first-hour plan: 1930 kab call karein, aur cybercrime.gov.in pe report kaise karein.", "span")}</li>
        </ul>
        {t("colp.top.p2", "If your department wants a longer workshop, we can add a live quiz and a hands-on demo that runs only on my own test devices. There is no hacking of real accounts or real people.", "Agar aapka department lamba workshop chahe, to live quiz aur hands-on demo add ho sakta hai, jo sirf meri apni test devices pe chalta hai. Asli accounts ya asli logon ki hacking nahi hoti.", "p")}
      </div>
    </section>

    <section class="section xp-sec" id="format" aria-labelledby="colp-fmt-h">
      <div class="wrap xp-narrow">
        {t("colp.fmt.h", "Online for any college in India, offline in Mumbai", "India ke kisi bhi college ke liye online, Mumbai mein offline", "h2").replace("<h2", '<h2 id="colp-fmt-h"', 1)}
        {t("colp.fmt.p", "If your campus is outside Mumbai, book an online session. We agree the platform over email, for example Google Meet or Zoom. You need a stable internet link and a way for the group to see and hear the session. If your campus is in Mumbai, I can come to the venue. Please share the room setup and facilities such as a projector, a microphone and internet.", "Agar aapka campus Mumbai ke bahar hai, to online session book karo. Platform email pe agree karte hain, jaise Google Meet ya Zoom. Stable internet chahiye, aur group ke liye session dekhne-sunne ka tareeka. Agar campus Mumbai mein hai, to main venue pe aa sakta hoon. Room setup aur projector, microphone aur internet jaise facilities bata dena.", "p")}
      </div>
    </section>

    <section class="section xp-sec" id="book-college" aria-labelledby="colp-book-h">
      <div class="wrap xp-narrow">
        {t("colp.book.h", "How a college can book this guest lecture", "College ye guest lecture kaise book kare", "h2").replace("<h2", '<h2 id="colp-book-h"', 1)}
        {t("colp.book.p", "Email contact@cyberwithmadhav.com with the college name, department or club, city, audience size, preferred dates, language (English, Hindi, Hinglish or Marathi), and whether you want the session online or in person in Mumbai. I reply personally with a plan and a clear fee. No booking form and no mailing list.", "contact@cyberwithmadhav.com pe email karo: college ka naam, department ya club, city, audience size, preferred dates, language (English, Hindi, Hinglish ya Marathi), aur session online chahiye ya Mumbai mein in person. Main personally plan aur clear fee ke saath reply karta hoon. Koi booking form nahi, koi mailing list nahi.", "p")}
        <div class="xp-btns">
          <a class="btn btn-primary" href="{MAILTO}" data-i18n="sess.cta">Email to book a session</a>
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="faq" aria-labelledby="colp-faq-h">
      <div class="wrap xp-narrow">
        {t("colp.faq.h", "Questions colleges usually ask", "Colleges aksar ye poochte hain", "h2").replace("<h2", '<h2 id="colp-faq-h"', 1)}
        <div class="sess-faqs">
{faq_block(COL_FAQS, "colp")}
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="related" aria-labelledby="colp-rel-h">
      <div class="wrap xp-narrow">
        {t("colp.rel.h", "Related session pages", "Related session pages", "h2").replace("<h2", '<h2 id="colp-rel-h"', 1)}
        <p class="small"><a href="cybersecurity-awareness-sessions.html" data-i18n="colp.all">See all packages and booking details</a> · <a href="cyber-awareness-session-for-schools.html" data-i18n="colp.more.sch">Cyber safety seminar for schools</a> · <a href="cyber-awareness-speaker-mumbai.html" data-i18n="colp.more.mum">Cyber awareness speaker in Mumbai</a></p>
      </div>
    </section>
  </main>'''


# ---------- schools ----------
SCH_FAQS = [
    {
        "id": "present",
        "q": "Does a teacher need to be present for a school cyber safety seminar?",
        "hi_q": "School ke cyber safety seminar mein teacher ka present hona zaroori hai?",
        "a": "Yes. Sessions for school children happen only with a teacher or school staff member present throughout. I do not collect personal data from students, and any hands-on demo is only on my own test devices.",
        "hi_a": "Haan. School children ke sessions sirf tab hote hain jab poori session ke dauran ek teacher ya school staff present ho. Main students ka personal data nahi leta, aur koi bhi hands-on demo sirf meri apni test devices pe hota hai.",
    },
    {
        "id": "age",
        "q": "What age groups can the school session be for?",
        "hi_q": "School session kaunse age group ke liye ho sakti hai?",
        "a": "Tell me the class or age group in your email so I can keep the examples age-appropriate. A session for younger students stays with passwords, what not to share, and when to tell a teacher or parent. Older school students can also hear about phishing SMS and fake study or game apps, still in plain language.",
        "hi_a": "Email mein class ya age group bata dena taaki examples age-appropriate rahen. Chhote students ke liye session passwords, kya share nahi karna, aur teacher ya parent ko kab batana hai, yahi rehti hai. Bade school students ko phishing SMS aur fake study ya game apps ke baare mein bhi bata sakta hoon, phir bhi simple language mein.",
    },
    {
        "id": "cost",
        "q": "How much does a cyber safety seminar for a school cost?",
        "hi_q": "School ke cyber safety seminar ki fees kitni hai?",
        "a": "The fee is shared on request, based on audience size, length and whether the session is online or in person in Mumbai. Email the details and I will reply with a clear fee before anything is booked.",
        "hi_a": "Fee request pe share ki jaati hai, audience size, duration, aur session online hai ya Mumbai mein in person, iske hisaab se. Details email karo, book hone se pehle main clear fee ke saath reply karunga.",
    },
    {
        "id": "addons",
        "q": "Can teachers get a briefing or a handout after the session?",
        "hi_q": "Session ke baad teachers ko briefing ya handout mil sakta hai?",
        "a": "Yes, if you ask for it. Add-ons include a short teacher or admin briefing, a one-page handout with 1930 and cybercrime.gov.in, a live quiz, participation certificates, and a follow-up recap PDF. Language can be English, Hindi, Hinglish or Marathi.",
        "hi_a": "Haan, agar aap maange. Add-ons mein chhoti teacher ya admin briefing, 1930 aur cybercrime.gov.in wala ek page ka handout, live quiz, participation certificates, aur follow-up recap PDF shamil ho sakte hain. Language English, Hindi, Hinglish ya Marathi ho sakti hai.",
    },
]


def schools_main():
    HI.update({
        "schp.h1": "India ke schools ke liye cyber safety seminar",
        "schp.all": "Saari packages aur booking details dekho",
        "schp.more.col": "College ke liye cyber security workshop",
        "schp.more.mum": "Mumbai mein cyber awareness speaker",
    })
    extra = crumbs("schools", "Seminar for schools") + book_block("schp")
    return f'''  <main id="main" tabindex="-1">
    <section class="page-hero xp-hero" aria-labelledby="p-title">
      <div class="wrap">
        <p class="kicker mono"><span class="prompt">$</span> ./book --school-seminar</p>
        <h1 id="p-title" data-i18n="schp.h1">Cyber safety seminar for schools in India</h1>
        {t("schp.lead", "Age-appropriate sessions so students pause before they click, share or install. A teacher must be present. Online across India. In person at schools in Mumbai.", "Age-appropriate sessions, taaki students click, share ya install se pehle sochen. Teacher ka present hona zaroori hai. Online poore India mein. Mumbai ke schools mein in person.", "p", "lead")}
{extra}      </div>
    </section>

    <section class="section xp-sec" id="who" aria-labelledby="schp-who-h">
      <div class="wrap xp-narrow">
        {t("schp.who.h", "Who this seminar is for", "Ye seminar kiske liye hai", "h2").replace("<h2", '<h2 id="schp-who-h"', 1)}
        {t("schp.who.p", "This page is for school principals, teachers and coordinators who want a cyber safety seminar for their students. The aim is simple: help children and teenagers pause before they click a link, share a photo, or install an app they do not recognise.", "Ye page school principals, teachers aur coordinators ke liye hai, jo apne students ke liye cyber safety seminar chahte hain. Maqsad simple hai: bachchon aur teenagers ko is baat ki aadat dena ki wo link click, photo share, ya anjaan app install karne se pehle sochen.", "p")}
      </div>
    </section>

    <section class="section xp-sec" id="topics" aria-labelledby="schp-top-h">
      <div class="wrap xp-narrow">
        {t("schp.top.h", "What a school cyber safety seminar covers", "School cyber safety seminar mein kya aata hai", "h2").replace("<h2", '<h2 id="schp-top-h"', 1)}
        {t("schp.top.p", "A typical school session is 45 to 60 minutes and stays age-appropriate. I adjust the examples once you tell me the class or age group. Core topics usually include:", "Typical school session 45 se 60 minutes ki hoti hai aur age-appropriate rehti hai. Jab aap class ya age group bata doge, main examples uske hisaab se adjust karta hoon. Core topics aksar ye hote hain:", "p")}
        <ul class="xp-list">
          <li>{t("schp.t1", "Passwords and PINs, and why they should not be shared with friends or with a message that looks official.", "Passwords aur PINs, aur unhe doston ya official dikhne wale message ke saath share kyun nahi karna chahiye.", "span")}</li>
          <li>{t("schp.t2", "What not to share on chat or social apps: photos, home address, school name, OTP or payment details.", "Chat ya social apps pe kya share nahi karna: photos, ghar ka address, school ka naam, OTP ya payment details.", "span")}</li>
          <li>{t("schp.t3", "Fake game or study apps, and why an install from outside the official store is risky.", "Fake game ya study apps, aur official store ke bahar se install kyun risky hai.", "span")}</li>
          <li>{t("schp.t4", "Phishing SMS and messages that pretend to be a school, a courier or a prize.", "Phishing SMS aur messages jo school, courier ya prize ban kar aate hain.", "span")}</li>
          <li>{t("schp.t5", "When to tell a teacher or parent, and how a family can call 1930 or report at cybercrime.gov.in if something goes wrong.", "Teacher ya parent ko kab batana hai, aur agar kuch galat ho to family 1930 kaise call kare ya cybercrime.gov.in pe report kaise kare.", "span")}</li>
        </ul>
      </div>
    </section>

    <section class="section xp-sec" id="standards" aria-labelledby="schp-std-h">
      <div class="wrap xp-narrow">
        {t("schp.std.h", "How I run a session with school children", "School children ke saath session kaise chalti hai", "h2").replace("<h2", '<h2 id="schp-std-h"', 1)}
        <ul class="xp-list">
          <li>{t("schp.s1", "A teacher or school staff member is present throughout.", "Poori session ke dauran ek teacher ya school staff present hota hai.", "span")}</li>
          <li>{t("schp.s2", "I do not collect students' personal data.", "Main students ka personal data nahi leta.", "span")}</li>
          <li>{t("schp.s3", "There is no hacking of real accounts or real people. Any demo is only on my own test devices.", "Asli accounts ya asli logon ki hacking nahi hoti. Koi bhi demo sirf meri apni test devices pe hota hai.", "span")}</li>
          <li>{t("schp.s4", "The session is educational only. It is not legal advice.", "Session sirf educational hai. Ye legal advice nahi hai.", "span")}</li>
        </ul>
        {t("schp.std.p", "Online sessions are open to schools anywhere in India. In-person sessions are only at school venues in Mumbai.", "Online sessions India ke kisi bhi school se book ho sakte hain. In-person sessions sirf Mumbai ke school venues pe hote hain.", "p")}
      </div>
    </section>

    <section class="section xp-sec" id="book-school" aria-labelledby="schp-book-h">
      <div class="wrap xp-narrow">
        {t("schp.book.h", "How a school can book this seminar", "School ye seminar kaise book kare", "h2").replace("<h2", '<h2 id="schp-book-h"', 1)}
        {t("schp.book.p", "Email contact@cyberwithmadhav.com with the school name, city, class or age group, about how many students will attend, preferred dates, language, and whether you want the session online or in person in Mumbai. Mention if you also want a teacher briefing or a handout. I reply personally with a plan and a clear fee.", "contact@cyberwithmadhav.com pe email karo: school ka naam, city, class ya age group, lagbhag kitne students aayenge, preferred dates, language, aur session online chahiye ya Mumbai mein in person. Agar teacher briefing ya handout bhi chahiye to likh dena. Main personally plan aur clear fee ke saath reply karta hoon.", "p")}
        <div class="xp-btns">
          <a class="btn btn-primary" href="{MAILTO}" data-i18n="sess.cta">Email to book a session</a>
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="faq" aria-labelledby="schp-faq-h">
      <div class="wrap xp-narrow">
        {t("schp.faq.h", "Questions schools usually ask", "Schools aksar ye poochte hain", "h2").replace("<h2", '<h2 id="schp-faq-h"', 1)}
        <div class="sess-faqs">
{faq_block(SCH_FAQS, "schp")}
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="related" aria-labelledby="schp-rel-h">
      <div class="wrap xp-narrow">
        {t("schp.rel.h", "Related session pages", "Related session pages", "h2").replace("<h2", '<h2 id="schp-rel-h"', 1)}
        <p class="small"><a href="cybersecurity-awareness-sessions.html" data-i18n="schp.all">See all packages and booking details</a> · <a href="cyber-security-workshop-for-colleges.html" data-i18n="schp.more.col">Cyber security workshop for colleges</a> · <a href="cyber-awareness-speaker-mumbai.html" data-i18n="schp.more.mum">Cyber awareness speaker in Mumbai</a></p>
      </div>
    </section>
  </main>'''


# ---------- mumbai speaker ----------
MUM_FAQS = [
    {
        "id": "where",
        "q": "Which parts of Mumbai do you come to for an offline session?",
        "hi_q": "Offline session ke liye Mumbai ke kaunse areas mein aate ho?",
        "a": "I come to your venue within Mumbai. There is no separate office address to visit. Please share the full venue address, the room setup, and facilities such as a projector, a microphone and internet. If your venue is outside Mumbai, book an online session instead.",
        "hi_a": "Main aapke Mumbai ke andar wale venue pe aata hoon. Koi alag office address visit karne ke liye nahi hai. Poora venue address, room setup, aur projector, microphone aur internet jaise facilities bata dena. Agar venue Mumbai ke bahar hai, to online session book karo.",
    },
    {
        "id": "who",
        "q": "Can Rotary, Lions, a company or a housing society book you as a speaker?",
        "hi_q": "Kya Rotary, Lions, company ya housing society aapko speaker ke roop mein book kar sakti hai?",
        "a": "Yes. Rotary and Lions chapters, companies, housing societies, NGOs, women groups and other community groups can email to book. Tell me who will be in the room and roughly how many people will attend. Online bookings are also open if an in-person date in Mumbai does not work.",
        "hi_a": "Haan. Rotary aur Lions chapters, companies, housing societies, NGOs, women groups aur doosre community groups email karke book kar sakte hain. Bata dena room mein kaun hoga aur lagbhag kitne log aayenge. Agar Mumbai mein in-person date nahi ho pati, to online bhi book ho sakta hai.",
    },
    {
        "id": "lang",
        "q": "Which languages can a Mumbai session be in?",
        "hi_q": "Mumbai session kaunsi language mein ho sakti hai?",
        "a": "English, Hindi, Hinglish or Marathi. Pick the language your audience is most comfortable with, or a mix if that helps.",
        "hi_a": "English, Hindi, Hinglish ya Marathi. Jo language aapki audience ko sabse comfortable ho, wahi choose karo, ya mix bhi chalega.",
    },
    {
        "id": "book",
        "q": "How do we invite you as a cyber awareness speaker in Mumbai?",
        "hi_q": "Mumbai mein cyber awareness speaker ke roop mein aapko kaise invite karein?",
        "a": "Email contact@cyberwithmadhav.com with the organisation name, venue area in Mumbai, audience, preferred dates and the length you have. I reply personally with a plan and a clear fee before anything is booked. Please write at least 2 weeks ahead where possible.",
        "hi_a": "contact@cyberwithmadhav.com pe email karo: organisation ka naam, Mumbai mein venue area, audience, preferred dates aur kitni der ka slot hai. Main personally plan aur clear fee ke saath reply karta hoon, book hone se pehle. Jahan ho sake, kam se kam 2 hafte pehle likho.",
    },
]


def mumbai_main():
    HI.update({
        "mump.all": "Saari packages aur booking details dekho",
        "mump.more.col": "College ke liye cyber security workshop",
        "mump.more.sch": "School ke liye cyber safety seminar",
        "mump.h1": "Mumbai mein cyber awareness speaker",
    })
    extra = crumbs("mumbai", "Speaker in Mumbai") + book_block("mump")
    return f'''  <main id="main" tabindex="-1">
    <section class="page-hero xp-hero" aria-labelledby="p-title">
      <div class="wrap">
        <p class="kicker mono"><span class="prompt">$</span> ./book --mumbai-speaker</p>
        <h1 id="p-title" data-i18n="mump.h1">Cyber awareness speaker in Mumbai</h1>
        {t("mump.lead", "Invite Madhav Pandya for an in-person cyber awareness session at your Mumbai venue, or book the same session online if you are elsewhere in India.", "Apne Mumbai venue pe in-person cyber awareness session ke liye Madhav Pandya ko invite karo, ya agar aap India mein kahin aur ho to wahi session online book karo.", "p", "lead")}
{extra}      </div>
    </section>

    <section class="section xp-sec" id="who" aria-labelledby="mump-who-h">
      <div class="wrap xp-narrow">
        {t("mump.who.h", "Who books an in-person session in Mumbai", "Mumbai mein in-person session kaun book karta hai", "h2").replace("<h2", '<h2 id="mump-who-h"', 1)}
        {t("mump.who.p", "This page is for people in Mumbai who want a speaker on site: colleges and schools, coaching institutes, company offices, housing societies, NGOs, and clubs such as Rotary, Lions, NSS or a student club. I come to your venue. There is no separate office address to visit.", "Ye page Mumbai ke un logon ke liye hai jo speaker ko site pe chahte hain: colleges aur schools, coaching institutes, company offices, housing societies, NGOs, aur Rotary, Lions, NSS ya student club jaise clubs. Main aapke venue pe aata hoon. Visit karne ke liye koi alag office address nahi hai.", "p")}
      </div>
    </section>

    <section class="section xp-sec" id="topics" aria-labelledby="mump-top-h">
      <div class="wrap xp-narrow">
        {t("mump.top.h", "What an offline Mumbai session can cover", "Offline Mumbai session mein kya cover ho sakta hai", "h2").replace("<h2", '<h2 id="mump-top-h"', 1)}
        {t("mump.top.p", "The topics follow the audience in the room. A college or corporate group often needs UPI fraud, phishing, fake job offers or work email caution. A housing society, Rotary or Lions meeting often needs a family-friendly briefing: OTP scams, QR codes at shops and gates, WhatsApp safety, and where to report. A women group can also cover account safety, harassment reporting and loan app caution. I confirm the outline with you before the date.", "Topics room ki audience ke hisaab se hote hain. College ya corporate group ko aksar UPI fraud, phishing, fake job offers ya work email ki caution chahiye. Housing society, Rotary ya Lions meeting ko aksar family-friendly briefing chahiye: OTP scams, shops aur gates pe QR codes, WhatsApp safety, aur report kahan karein. Women group ke saath account safety, harassment reporting aur loan app ki caution bhi cover ho sakti hai. Date se pehle main outline aapke saath confirm karta hoon.", "p")}
      </div>
    </section>

    <section class="section xp-sec" id="venue" aria-labelledby="mump-ven-h">
      <div class="wrap xp-narrow">
        {t("mump.ven.h", "What to arrange at the venue", "Venue pe kya arrange karna hai", "h2").replace("<h2", '<h2 id="mump-ven-h"', 1)}
        {t("mump.ven.p", "Please share the full Mumbai address, a contact person on the day, and the room setup. A projector or screen, a microphone if the room is large, and a stable internet link help the session run smoothly. If a facility is missing, tell me in the email and we will adapt. Sessions can be in English, Hindi, Hinglish or Marathi.", "Poora Mumbai address, us din ka contact person, aur room setup bata dena. Projector ya screen, bade room mein microphone, aur stable internet se session smooth chalti hai. Agar koi facility nahi hai to email mein likh dena, hum adjust kar lenge. Sessions English, Hindi, Hinglish ya Marathi mein ho sakti hain.", "p")}
        {t("mump.ven.p2", "If you are not in Mumbai, you can still book. Online sessions are open to institutes, clubs and companies anywhere in India, and abroad if the time works.", "Agar aap Mumbai mein nahi ho, tab bhi book kar sakte ho. Online sessions India ke kisi bhi sheher ke institutes, clubs aur companies ke liye khule hain, aur bahar se bhi agar time match kare.", "p")}
      </div>
    </section>

    <section class="section xp-sec" id="speaker" aria-labelledby="mump-spk-h">
      <div class="wrap xp-narrow">
        {t("mump.spk.h", "About the speaker", "Speaker ke baare mein", "h2").replace("<h2", '<h2 id="mump-spk-h"', 1)}
        {t("mump.spk.p", "Madhav Pandya is a cybersecurity educator from Mumbai and the founder of CyberWithMadhav. He explains cybersecurity, scam awareness and Indian cyber law in plain English and Hinglish. He is studying for a BCA in Cloud Computing and Cyber Security, and a BA LLB at KES Shri J.P. Law College.", "Madhav Pandya Mumbai se cybersecurity educator hain aur CyberWithMadhav ke founder hain. Wo cybersecurity, scam awareness aur Indian cyber law simple English aur Hinglish mein samjhate hain. Wo Cloud Computing and Cyber Security mein BCA kar rahe hain, aur KES Shri J.P. Law College se BA LLB.", "p")}
        <p class="small"><a href="about.html">More on the About page</a> · <a href="collaborate.html">Media kit and other collaborations</a></p>
      </div>
    </section>

    <section class="section xp-sec" id="book-mumbai" aria-labelledby="mump-book-h">
      <div class="wrap xp-narrow">
        {t("mump.book.h", "How to invite a cyber awareness speaker in Mumbai", "Mumbai mein cyber awareness speaker ko kaise invite karein", "h2").replace("<h2", '<h2 id="mump-book-h"', 1)}
        {t("mump.book.p", "Email contact@cyberwithmadhav.com with the organisation name, venue area, audience, preferred dates and the length you have. I reply personally with a plan and a clear fee before anything is booked. Please write at least 2 weeks ahead where possible.", "contact@cyberwithmadhav.com pe email karo: organisation ka naam, venue area, audience, preferred dates aur kitni der ka slot hai. Main personally plan aur clear fee ke saath reply karta hoon, book hone se pehle. Jahan ho sake, kam se kam 2 hafte pehle likho.", "p")}
        <div class="xp-btns">
          <a class="btn btn-primary" href="{MAILTO}" data-i18n="sess.cta">Email to book a session</a>
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="faq" aria-labelledby="mump-faq-h">
      <div class="wrap xp-narrow">
        {t("mump.faq.h", "Questions organisers in Mumbai usually ask", "Mumbai ke organisers aksar ye poochte hain", "h2").replace("<h2", '<h2 id="mump-faq-h"', 1)}
        <div class="sess-faqs">
{faq_block(MUM_FAQS, "mump")}
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="related" aria-labelledby="mump-rel-h">
      <div class="wrap xp-narrow">
        {t("mump.rel.h", "Related session pages", "Related session pages", "h2").replace("<h2", '<h2 id="mump-rel-h"', 1)}
        <p class="small"><a href="cybersecurity-awareness-sessions.html" data-i18n="mump.all">See all packages and booking details</a> · <a href="cyber-security-workshop-for-colleges.html" data-i18n="mump.more.col">Cyber security workshop for colleges</a> · <a href="cyber-awareness-session-for-schools.html" data-i18n="mump.more.sch">Cyber safety seminar for schools</a></p>
      </div>
    </section>
  </main>'''


SPECS = [
    {
        "file": "cyber-security-workshop-for-colleges.html",
        "title": "Cyber Security Workshop for Colleges | CyberWithMadhav",
        "desc": "Book a cyber security workshop or guest lecture for college students. UPI fraud, fake jobs and campus Wi-Fi. Online across India, offline in Mumbai.",
        "og": "Cyber Security Workshop for Colleges | CyberWithMadhav",
        "ogdesc": "Book a cyber security workshop or guest lecture for college students. Online across India, offline in Mumbai.",
        "body": "xp-page sess-page",
        "css": ["pages.css", "extras.css"],
        "js": ["i18n/page-extras.js"],
        "main_fn": colleges_main,
        "ldname": "Cyber security workshop for colleges",
        "foot": "Content is for awareness and education, not legal advice.",
        "ld_fn": lambda s: page_ld(s["file"], s["ldname"], s["desc"], COL_FAQS, "Cyber security workshop for colleges", "Cyber security workshop"),
        "og_alt": "CyberWithMadhav: cyber security workshop and guest lecture for college students in India and Mumbai.",
    },
    {
        "file": "cyber-awareness-session-for-schools.html",
        "title": "Cyber Safety Seminar for Schools | CyberWithMadhav",
        "desc": "Book a cyber safety seminar for school students in India. Age-appropriate sessions with a teacher present. Online across India, in person in Mumbai.",
        "og": "Cyber Safety Seminar for Schools | CyberWithMadhav",
        "ogdesc": "Book a cyber safety seminar for school students. Age-appropriate, with a teacher present. Online across India, in person in Mumbai.",
        "body": "xp-page sess-page",
        "css": ["pages.css", "extras.css"],
        "js": ["i18n/page-extras.js"],
        "main_fn": schools_main,
        "ldname": "Cyber safety seminar for schools",
        "foot": "Content is for awareness and education, not legal advice.",
        "ld_fn": lambda s: page_ld(s["file"], s["ldname"], s["desc"], SCH_FAQS, "Cyber safety seminar for schools", "Cyber safety seminar"),
        "og_alt": "CyberWithMadhav: cyber safety seminar for school students in India, online or in person in Mumbai.",
    },
    {
        "file": "cyber-awareness-speaker-mumbai.html",
        "title": "Cyber Awareness Speaker in Mumbai | CyberWithMadhav",
        "desc": "Invite Madhav Pandya, a cyber awareness speaker in Mumbai, for clubs, corporates and institutes. Offline in Mumbai, online across India.",
        "og": "Cyber Awareness Speaker in Mumbai | CyberWithMadhav",
        "ogdesc": "Invite Madhav Pandya for an in-person cyber awareness session in Mumbai, or book online from anywhere in India.",
        "body": "xp-page sess-page",
        "css": ["pages.css", "extras.css"],
        "js": ["i18n/page-extras.js"],
        "main_fn": mumbai_main,
        "ldname": "Cyber awareness speaker in Mumbai",
        "foot": "Content is for awareness and education, not legal advice.",
        "ld_fn": lambda s: page_ld(s["file"], s["ldname"], s["desc"], MUM_FAQS, "Cyber awareness speaker in Mumbai", "Cyber awareness speaking"),
        "og_alt": "Madhav Pandya, cyber awareness speaker in Mumbai, for clubs, corporates and institutes.",
    },
]
