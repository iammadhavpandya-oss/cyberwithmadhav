"""Source for cybersecurity-awareness-sessions.html. Built by tools/build_extras.py."""
import html, json
from urllib.parse import quote

EMAIL = "madhavpandya@zohomail.in"
BASE = "https://www.cyberwithmadhav.com/"
FILE = "cybersecurity-awareness-sessions.html"
E = lambda s: html.escape(s, quote=True)
HI = {}  # filled by t()


def t(key, en, hi, tag="p", cls=""):
    HI[key] = hi
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c} data-i18n="{key}">{en}</{tag}>'


SUBJECT = "Cyber Awareness Session Request - [Institute Name]"
BODY = """Hello Madhav,

I would like to book a cybersecurity awareness session for our institute.

Institute name:
Type (school, college, coaching or IT institute, company, housing society, NGO, other):
City and area:
Contact person, role and phone:
Audience and age group:
Approx participants:
Preferred topic or package:
Mode (Online / Offline in Mumbai):
Platform or venue address:
Preferred date and time (option 1):
Preferred date and time (option 2):
Duration:
Language (English, Hindi, Hinglish, Marathi):
Facilities (projector, mics, internet, and so on):
Certificates or quiz needed:
Specific concerns:
How did you hear about CyberWithMadhav:

Thank you.
"""
MAILTO = f"mailto:{EMAIL}?subject={quote(SUBJECT, safe='')}&body={quote(BODY, safe='')}"

FAQS = [
    {
        "id": "who-can-book",
        "q": "Who can book a session?",
        "hi_q": "Session kaun book kar sakta hai?",
        "a": "Schools, colleges, coaching and IT institutes, companies, housing societies, NGOs, women groups and other community groups can email to book. Tell me who the audience is, the age group and about how many people will attend.",
        "hi_a": "Schools, colleges, coaching aur IT institutes, companies, housing societies, NGOs, women groups aur doosre community groups email karke book kar sakte hain. Audience kaun hai, age group kya hai aur lagbhag kitne log aayenge, ye bata dena.",
    },
    {
        "id": "online-offline",
        "q": "Can we book online if we are not in Mumbai?",
        "hi_q": "Agar hum Mumbai mein nahi hain to online book kar sakte hain?",
        "a": "Yes. Online sessions are open to institutes anywhere in India, and abroad if the time works. In-person sessions are only within Mumbai. We agree the video platform over email, for example Google Meet or Zoom.",
        "hi_a": "Haan. Online sessions India ke kisi bhi sheher se book ho sakte hain, aur bahar se bhi agar time match kare. In-person sessions sirf Mumbai ke andar hote hain. Video platform email pe decide karte hain, jaise Google Meet ya Zoom.",
    },
    {
        "id": "fees",
        "q": "How much does a session cost?",
        "hi_q": "Session ki fees kitni hai?",
        "a": "Shared on request, based on audience size and format. Email the details below and I will reply with a clear fee before anything is booked.",
        "hi_a": "Request pe share ki jaati hai, audience size aur format ke hisaab se. Neeche wale details email karo, book hone se pehle main clear fee ke saath reply karunga.",
    },
    {
        "id": "notice",
        "q": "How much notice should we give?",
        "hi_q": "Kitne din pehle email karna chahiye?",
        "a": "Please email at least 2 weeks ahead where possible. If a date is urgent, still write in: I will say quickly whether it can work.",
        "hi_a": "Jahan ho sake, kam se kam 2 hafte pehle email karo. Agar date urgent hai to bhi likh dena: main jaldi bataunga ki ho sakta hai ya nahi.",
    },
    {
        "id": "language",
        "q": "Which languages can the session be in?",
        "hi_q": "Session kaunsi language mein ho sakta hai?",
        "a": "English, Hindi, Hinglish or Marathi. Pick the language your audience is most comfortable with, or a mix if that helps.",
        "hi_a": "English, Hindi, Hinglish ya Marathi. Jo language aapki audience ko sabse comfortable ho, wahi choose karo, ya mix bhi chalega.",
    },
    {
        "id": "legal",
        "q": "Is this legal advice?",
        "hi_q": "Kya ye legal advice hai?",
        "a": "No. The session is for awareness and education only, not legal advice. If someone has lost money or needs to report an incident, they should call 1930 or report at cybercrime.gov.in.",
        "hi_a": "Nahi. Session sirf awareness aur education ke liye hai, legal advice nahi. Agar kisi ka paisa gaya ho ya incident report karna ho, to 1930 pe call karein ya cybercrime.gov.in pe report karein.",
    },
    {
        "id": "minors",
        "q": "Can you run a session for school children?",
        "hi_q": "School children ke liye session ho sakta hai?",
        "a": "Yes, with a teacher or school staff member present throughout. I do not collect personal data from participants, and any hands-on demo is only on my own test devices.",
        "hi_a": "Haan, poori session ke dauran ek teacher ya school staff ke saath. Main participants ka personal data nahi leta, aur koi bhi hands-on demo sirf meri apni test devices pe hota hai.",
    },
    {
        "id": "recording",
        "q": "Will the session be recorded?",
        "hi_q": "Kya session record hogi?",
        "a": "Only if the institute asks, and only after attendees are informed. There is no default recording.",
        "hi_a": "Sirf tab, jab institute maange, aur attendees ko pehle bata diya jaye. Default mein recording nahi hoti.",
    },
    {
        "id": "how-to-book",
        "q": "How do we book a cyber security workshop or guest lecture?",
        "hi_q": "Cyber security workshop ya guest lecture kaise book karein?",
        "a": "Email madhavpandya@zohomail.in with the institute name, audience, city, preferred dates and whether you want an online session or an in-person session in Mumbai. I reply personally with a plan and a clear fee before anything is booked. Please write at least 2 weeks ahead where possible.",
        "hi_a": "madhavpandya@zohomail.in pe email karo: institute ka naam, audience, city, preferred dates, aur online chahiye ya Mumbai mein in-person. Main personally plan aur clear fee ke saath reply karta hoon, book hone se pehle. Jahan ho sake, kam se kam 2 hafte pehle likho.",
    },
    {
        "id": "college-topics",
        "q": "What topics do you cover in a cyber security workshop for students?",
        "hi_q": "Students ke cyber security workshop mein kaunse topics aate hain?",
        "a": "For college and coaching students the usual starting point is UPI fraud, fake job offers, phishing, account takeover, public or campus Wi-Fi, two-factor authentication, and digital arrest awareness. For school students the session stays age-appropriate: passwords and PINs, what not to share, fake game or study apps, phishing SMS, and when to tell a teacher or parent. Tell me what your group is worried about and I will shape the session around that.",
        "hi_a": "College aur coaching students ke liye usual starting point hai UPI fraud, fake job offers, phishing, account takeover, public ya campus Wi-Fi, two-factor authentication, aur digital arrest awareness. School students ke liye session age-appropriate rehti hai: passwords aur PINs, kya share nahi karna, fake game ya study apps, phishing SMS, aur teacher ya parent ko kab batana hai. Batao aapka group kis cheez se worried hai, main session usi ke around shape karunga.",
    },
    {
        "id": "online-vs-offline",
        "q": "What is the difference between an online session and an offline session in Mumbai?",
        "hi_q": "Online session aur Mumbai ki offline session mein kya fark hai?",
        "a": "Online sessions are open to institutes anywhere in India, and abroad if the time works. We agree the video platform over email, for example Google Meet or Zoom. Offline, in-person sessions are only within Mumbai. I come to your venue. Please share the address, the room setup, and facilities such as a projector, a microphone and internet.",
        "hi_a": "Online sessions India ke kisi bhi sheher se book ho sakte hain, aur bahar se bhi agar time match kare. Video platform email pe decide karte hain, jaise Google Meet ya Zoom. Offline, in-person sessions sirf Mumbai ke andar hote hain. Main aapke venue pe aata hoon. Address, room setup, aur projector, microphone aur internet jaise facilities bata dena.",
    },
    {
        "id": "clubs",
        "q": "Can a Rotary, Lions or student club book a cyber awareness session?",
        "hi_q": "Kya Rotary, Lions ya student club cyber awareness session book kar sakta hai?",
        "a": "Yes. Rotary and Lions chapters, NSS units, student clubs, housing societies, NGOs and other community groups can email to book. Online across India, or in person if your venue is in Mumbai. Tell me who will be in the room and roughly how many people will attend.",
        "hi_a": "Haan. Rotary aur Lions chapters, NSS units, student clubs, housing societies, NGOs aur doosre community groups email karke book kar sakte hain. Online poore India mein, ya in person agar venue Mumbai mein hai. Bata dena room mein kaun hoga aur lagbhag kitne log aayenge.",
    },
    {
        "id": "school-cost",
        "q": "How much does a cyber safety seminar for a school cost?",
        "hi_q": "School ke cyber safety seminar ki fees kitni hai?",
        "a": "The fee is shared on request, based on audience size, length and whether the session is online or in person in Mumbai. Email the details and I will reply with a clear fee before anything is booked. There is no published rate card on this site.",
        "hi_a": "Fee request pe share ki jaati hai, audience size, duration, aur session online hai ya Mumbai mein in person, iske hisaab se. Details email karo, book hone se pehle main clear fee ke saath reply karunga. Is site pe koi published rate card nahi hai.",
    },
]


CHECKLIST = [
    ("Institute name", "Institute ka naam"),
    ("Type (school, college, coaching or IT institute, company, housing society, NGO, other)", "Type (school, college, coaching ya IT institute, company, housing society, NGO, other)"),
    ("City and area", "City aur area"),
    ("Contact person, role and phone", "Contact person, role aur phone"),
    ("Audience and age group", "Audience aur age group"),
    ("Approx participants", "Lagbhag kitne participants"),
    ("Preferred topic or package", "Preferred topic ya package"),
    ("Mode (Online / Offline in Mumbai)", "Mode (Online / Mumbai mein Offline)"),
    ("Platform or venue address", "Platform ya venue address"),
    ("Preferred date and time (2 options)", "Preferred date aur time (2 options)"),
    ("Duration", "Duration"),
    ("Language", "Language"),
    ("Facilities", "Facilities"),
    ("Certificates or quiz needed", "Certificates ya quiz chahiye"),
    ("Specific concerns", "Koi specific concerns"),
    ("How did you hear about CyberWithMadhav", "CyberWithMadhav ke baare mein kaise pata chala"),
]


def crumbs():
    return """        <nav class="xp-crumbs small muted" aria-label="Breadcrumb"><a href="index.html" data-i18n="blog.home">Home</a> <span aria-hidden="true">/</span> <span aria-current="page">Cybersecurity awareness sessions</span></nav>
"""


def sessions_main():
    who = [
        ("sess.w1", "Schools", "Schools", "Teachers who want students to pause before they click, share or install."),
        ("sess.w2", "Colleges", "Colleges", "Students who use UPI, job portals and campus Wi-Fi every day."),
        ("sess.w3", "Coaching and IT institutes", "Coaching aur IT institutes", "Batches preparing for jobs, internships or a first role in tech."),
        ("sess.w4", "Companies", "Companies", "Staff who handle email, payments, customer data or vendor links."),
        ("sess.w5", "Housing societies", "Housing societies", "Residents and committee members who want a clear briefing for the building."),
        ("sess.w6", "NGOs and community groups", "NGOs aur community groups", "Groups that work with families, women, seniors or first-time smartphone users."),
        ("sess.w7", "Clubs and societies", "Clubs aur societies", "Rotary, Lions, NSS, student clubs and other groups that want a practical cyber awareness talk."),
    ]
    who_html = "\n".join(
        f'          <article class="card sess-card">\n'
        f'            {t(k + ".h", en, hi, "h3")}\n'
        f'            {t(k + ".p", p, {"sess.w1": "Teachers jo chahte hain students click, share ya install se pehle sochen.", "sess.w2": "Students jo har din UPI, job portals aur campus Wi-Fi use karte hain.", "sess.w3": "Batches jo jobs, internships ya tech ki pehli role ke liye prepare ho rahe hain.", "sess.w4": "Staff jo email, payments, customer data ya vendor links handle karte hain.", "sess.w5": "Residents aur committee members jo building ke liye clear briefing chahte hain.", "sess.w6": "Groups jo families, women, seniors ya pehli baar smartphone use karne walon ke saath kaam karte hain.", "sess.w7": "Rotary, Lions, NSS, student clubs aur doosre groups jo practical cyber awareness talk chahte hain."}[k], "p", "muted")}\n'
        f'          </article>'
        for k, en, hi, p in who
    )

    gets = [
        ("sess.g1", "Practical examples from scams people in India actually face, not generic slides.", "Practical examples un scams se jo India mein log actually face karte hain, generic slides nahi."),
        ("sess.g2", "Jargon-free language, with time for questions.", "Bina jargon ke language, aur sawaal ke liye time."),
        ("sess.g3", "A clear first-hour plan: when to call 1930 and how to report at cybercrime.gov.in.", "Clear first-hour plan: 1930 kab call karein, aur cybercrime.gov.in pe report kaise karein."),
        ("sess.g4", "A session shaped to your audience, age group and the time you have.", "Session aapki audience, age group aur available time ke hisaab se."),
        ("sess.g5", "A personal reply to your email. No booking form and no mailing list.", "Aapke email ka personal reply. Koi booking form nahi, koi mailing list nahi."),
    ]
    get_html = "\n".join(f'            <li>{t(k, en, hi, "span")}</li>' for k, en, hi in gets)

    packs = [
        ("sess.p1", "School kids", "School kids", "45-60 min",
         "Passwords and PINs, what not to share, fake game or study apps, phishing SMS, and when to tell a teacher or parent."),
        ("sess.p2", "College students", "College students", "60-90 min",
         "UPI fraud, fake job offers, phishing, account takeover, public Wi-Fi, 2FA, and digital arrest awareness."),
        ("sess.p3", "Coaching and IT institutes", "Coaching aur IT institutes", "90-120 min",
         "The college topics, plus checking an app before you install it, internships that ask for fees, password managers, and safe habits for a first tech job."),
        ("sess.p4", "Seniors and parents", "Seniors aur parents", "45-60 min",
         "UPI and OTP scams, digital arrest, fake KYC calls, WhatsApp takeover, deepfake family video calls, and how to verify before you pay."),
        ("sess.p5", "Corporate staff", "Corporate staff", "60-90 min",
         "Work email phishing, passwords and 2FA, QR and UPI risks, vendor and attachment caution, how to report, and a short, plain DPDP awareness note. Not legal advice."),
        ("sess.p6", "Women groups", "Women groups", "60-90 min",
         "Account safety, reporting harassment, UPI and OTP scams, deepfakes, loan app caution, and where to get help including 1930."),
        ("sess.p7", "Housing societies and NGOs", "Housing societies aur NGOs", "45-60 min",
         "Common Indian scams, tips families can forward, QR codes at shops and gates, WhatsApp group safety, and where to report."),
    ]
    pack_hi = {
        "sess.p1": "Passwords aur PINs, kya share nahi karna, fake game ya study apps, phishing SMS, aur teacher ya parent ko kab batana hai.",
        "sess.p2": "UPI fraud, fake job offers, phishing, account takeover, public Wi-Fi, 2FA, aur digital arrest awareness.",
        "sess.p3": "College wale topics, plus app install karne se pehle check karna, internships jo fees maange, password managers, aur pehli tech job ke safe habits.",
        "sess.p4": "UPI aur OTP scams, digital arrest, fake KYC calls, WhatsApp takeover, deepfake family video calls, aur pay karne se pehle verify kaise karein.",
        "sess.p5": "Work email phishing, passwords aur 2FA, QR aur UPI ke risks, vendor aur attachment ki caution, report kaise karein, aur ek chhota, simple DPDP awareness note. Legal advice nahi.",
        "sess.p6": "Account safety, harassment report karna, UPI aur OTP scams, deepfakes, loan app ki caution, aur help kahan se lein, 1930 ke saath.",
        "sess.p7": "Common Indian scams, tips jo family aage bhej sake, shops aur gates pe QR codes, WhatsApp group safety, aur report kahan karein.",
    }
    pack_html = "\n".join(
        f'          <article class="card sess-card">\n'
        f'            <p class="kicker mono">{dur}</p>\n'
        f'            {t(k + ".h", title, title_hi, "h3")}\n'
        f'            {t(k + ".p", topics, pack_hi[k], "p", "muted")}\n'
        f'          </article>'
        for k, title, title_hi, dur, topics in packs
    )

    tiers = [
        ("sess.t1", "Basic", "Basic", "45-60 min",
         "A focused briefing on the topics your audience needs most, plus time for questions."),
        ("sess.t2", "Standard", "Standard", "90 min, with a quiz",
         "A fuller session with a live quiz so people can check what they picked up, plus Q&A."),
        ("sess.t3", "Extended", "Extended", "Half day, with a hands-on demo",
         "A longer workshop with a hands-on demo on my own test devices, plus quiz and Q&A."),
    ]
    tier_hi = {
        "sess.t1": "Aapki audience ko jin topics ki sabse zyada zaroorat hai, unpe focused briefing, plus sawaal ke liye time.",
        "sess.t2": "Thodi lambi session, live quiz ke saath taaki log check kar saken ki kya samajh aaya, plus Q&A.",
        "sess.t3": "Lamba workshop, hands-on demo meri apni test devices pe, plus quiz aur Q&A.",
    }
    tier_html = "\n".join(
        f'          <article class="card sess-card sess-tier">\n'
        f'            <p class="kicker mono">{meta}</p>\n'
        f'            {t(k + ".h", name, name_hi, "h3")}\n'
        f'            {t(k + ".p", desc, tier_hi[k], "p", "muted")}\n'
        f'          </article>'
        for k, name, name_hi, meta, desc in tiers
    )

    addons = [
        ("sess.a1", "Participation certificates", "Participation certificates"),
        ("sess.a2", "A live quiz", "Live quiz"),
        ("sess.a3", "A one-page handout with 1930 and cybercrime.gov.in", "Ek page ka handout, 1930 aur cybercrime.gov.in ke saath"),
        ("sess.a4", "Anonymous Q&A slips, so quieter people can ask too", "Anonymous Q&A slips, taaki jo log kam bolte hain wo bhi pooch saken"),
        ("sess.a5", "Language: English, Hindi, Hinglish or Marathi", "Language: English, Hindi, Hinglish ya Marathi"),
        ("sess.a6", "A follow-up recap PDF after the session", "Session ke baad follow-up recap PDF"),
        ("sess.a7", "A short teacher or admin briefing for schools", "Schools ke liye chhoti teacher ya admin briefing"),
        ("sess.a8", "Reusable posters or slides the institute can keep", "Reusable posters ya slides jo institute rakh sake"),
        ("sess.a9", "A recording only if the institute asks and attendees are informed", "Recording sirf tab, jab institute maange aur attendees ko bata diya jaye"),
    ]
    addon_html = "\n".join(f'            <li>{t(k, en, hi, "span")}</li>' for k, en, hi in addons)

    steps = [
        ("sess.s1", "01", "Email me", "Mujhe email karo",
         "Use the button below, or write to the address yourself. Include the checklist so I can reply with a clear plan."),
        ("sess.s2", "02", "I reply personally", "Main personally reply karta hoon",
         "We agree the date, the format, the language, any add-ons and the fee before anything is booked."),
        ("sess.s3", "03", "The session happens", "Session hoti hai",
         "Online or in Mumbai, as agreed. If you asked for a recap PDF or certificates, those follow after."),
    ]
    step_hi = {
        "sess.s1": "Neeche wala button use karo, ya khud address pe likho. Checklist bhej dena taaki main clear plan ke saath reply kar sakun.",
        "sess.s2": "Date, format, language, koi add-ons aur fee, book hone se pehle agree kar lete hain.",
        "sess.s3": "Online ya Mumbai mein, jaise agree hua. Agar aapne recap PDF ya certificates maange hon, wo baad mein milenge.",
    }
    step_html = "\n".join(
        f'          <article class="card sess-card">\n'
        f'            <p class="kicker mono">{num}</p>\n'
        f'            {t(k + ".h", en_h, hi_h, "h3")}\n'
        f'            {t(k + ".p", en_p, step_hi[k], "p", "muted")}\n'
        f'          </article>'
        for k, num, en_h, hi_h, en_p in steps
    )

    faq_html = []
    for it in FAQS:
        HI[f"sess.faq.q.{it['id']}"] = it["hi_q"]
        HI[f"sess.faq.a.{it['id']}"] = it["hi_a"]
        faq_html.append(
            f'          <details class="card sess-faq">\n'
            f'            <summary><h3 data-i18n="sess.faq.q.{it["id"]}">{E(it["q"])}</h3></summary>\n'
            f'            <p data-i18n="sess.faq.a.{it["id"]}">{E(it["a"])}</p>\n'
            f'          </details>'
        )
    faq_block = "\n".join(faq_html)

    check_html = []
    for i, (en, hi) in enumerate(CHECKLIST, 1):
        key = f"sess.chk.{i}"
        HI[key] = hi
        check_html.append(f'            <li data-i18n="{key}">{E(en)}</li>')
    check_block = "\n".join(check_html)

    extra = crumbs() + f"""        <div class="xp-btns">
          <a class="btn btn-primary" href="{MAILTO}" data-i18n="sess.cta">Email to book a session</a>
        </div>
        {t("sess.reply", "I reply personally. No forms, no spam.", "Main personally reply karta hoon. Koi form nahi, koi spam nahi.", "p", "small muted")}
"""

    HI.update({
        "sess.h1": "Colleges, schools aur clubs ke liye cyber security awareness sessions",
        "sess.cta": "Session book karne ke liye email karo",
        "sess.spk.about": "About page pe aur padho",
        "sess.spk.collab": "Media kit aur doosre collaborations",
        "sess.more.col": "College workshop page",
        "sess.more.sch": "School seminar page",
        "sess.more.mum": "Mumbai speaker page",
        "sess.aud.more": "In pages pe audience ke hisaab se aur padho",
    })
    return f"""  <main id="main" tabindex="-1">
    <section class="page-hero xp-hero" aria-labelledby="p-title">
      <div class="wrap">
        <p class="kicker mono"><span class="prompt">$</span> ./book --session</p>
        <h1 id="p-title" data-i18n="sess.h1">Cyber security awareness sessions for colleges, schools and clubs</h1>
        {t("sess.lead", "Guest lectures and workshops on UPI fraud, phishing, fake apps and account safety. Online across India. In person in Mumbai. By Madhav Pandya.", "College, school aur clubs ke liye guest lecture aur workshop: UPI fraud, phishing, fake apps aur account safety. Online poore India mein. In person Mumbai mein. Madhav Pandya ke saath.", "p", "lead")}
{extra}      </div>
    </section>

    <section class="section xp-sec" id="who" aria-labelledby="sess-who-h">
      <div class="wrap">
        {t("sess.who.h", "Who it is for", "Ye kis ke liye hai", "h2").replace("<h2", '<h2 id="sess-who-h"', 1)}
        {t("sess.who.p", "If you look after students, staff, residents or a community group, and you want them to spot a scam before they lose money, this is for you.", "Agar aap students, staff, residents ya kisi community group ko handle karte ho, aur chahte ho ki wo paisa gawane se pehle scam pehchaan lein, to ye unke liye hai.", "p", "muted")}
        <div class="xp-grid sess-grid">
{who_html}
        </div>
      </div>
    </section>


    <section class="section xp-sec" id="colleges" aria-labelledby="sess-col-h">
      <div class="wrap xp-narrow">
        {t("sess.col.h", "For colleges and universities", "Colleges aur universities ke liye", "h2").replace("<h2", '<h2 id="sess-col-h"', 1)}
        {t("sess.col.p1", "A guest lecture or cyber security workshop for college students works best when it talks about the scams they actually see: UPI collect requests, fake internship or job offers, phishing on campus Wi-Fi, account takeover and digital arrest calls. I keep the language plain, and I leave time for questions.", "College students ke liye guest lecture ya cyber security workshop tab best chalti hai jab un scams ki baat ho jo wo actually dekhte hain: UPI collect requests, fake internship ya job offers, campus Wi-Fi pe phishing, account takeover aur digital arrest calls. Language simple rakhata hoon, aur sawaal ke liye time chhodta hoon.", "p")}
        {t("sess.col.p2", "The usual length is 60 to 90 minutes. Online sessions are open to colleges anywhere in India. In-person sessions are for Mumbai campuses only. Student councils, NSS units and faculty can email to book. This is an awareness session, not a placement workshop and not legal advice.", "Usual duration 60 se 90 minutes hai. Online sessions India ke kisi bhi college se book ho sakte hain. In-person sessions sirf Mumbai campuses ke liye hain. Student councils, NSS units aur faculty email karke book kar sakte hain. Ye awareness session hai, placement workshop nahi, legal advice bhi nahi.", "p")}
        <p class="small"><a href="cyber-security-workshop-for-colleges.html" data-i18n="sess.more.col">College workshop page</a></p>
      </div>
    </section>

    <section class="section xp-sec" id="schools" aria-labelledby="sess-sch-h">
      <div class="wrap xp-narrow">
        {t("sess.sch.h", "For schools", "Schools ke liye", "h2").replace("<h2", '<h2 id="sess-sch-h"', 1)}
        {t("sess.sch.p1", "A cyber safety seminar for school students stays age-appropriate. Typical topics are passwords and PINs, what not to share, fake game or study apps, phishing SMS, and when to tell a teacher or parent. A teacher or school staff member must be present throughout.", "School students ke cyber safety seminar age-appropriate rehti hai. Typical topics hain passwords aur PINs, kya share nahi karna, fake game ya study apps, phishing SMS, aur teacher ya parent ko kab batana hai. Poori session ke dauran ek teacher ya school staff present hona zaroori hai.", "p")}
        {t("sess.sch.p2", "I do not collect personal data from students. Any hands-on demo runs only on my own test devices. You can also ask for a short teacher or admin briefing, and a one-page handout with 1930 and cybercrime.gov.in. Online across India, or in person at schools in Mumbai.", "Main students ka personal data nahi leta. Koi bhi hands-on demo sirf meri apni test devices pe hota hai. Aap chhoti teacher ya admin briefing bhi maang sakte ho, aur ek page ka handout 1930 aur cybercrime.gov.in ke saath. Online poore India mein, ya Mumbai ke schools mein in person.", "p")}
        <p class="small"><a href="cyber-awareness-session-for-schools.html" data-i18n="sess.more.sch">School seminar page</a></p>
      </div>
    </section>

    <section class="section xp-sec" id="clubs" aria-labelledby="sess-club-h">
      <div class="wrap xp-narrow">
        {t("sess.club.h", "For clubs and NGOs", "Clubs aur NGOs ke liye", "h2").replace("<h2", '<h2 id="sess-club-h"', 1)}
        {t("sess.club.p1", "Rotary and Lions chapters, NSS units, student clubs, housing societies and NGOs often want a practical talk that families can take home. I cover common Indian scams, QR codes at shops and gates, WhatsApp group safety, and where to report, including 1930 and cybercrime.gov.in.", "Rotary aur Lions chapters, NSS units, student clubs, housing societies aur NGOs aksar aisi practical baat chahte hain jo family ghar le ja sake. Main common Indian scams, shops aur gates pe QR codes, WhatsApp group safety, aur report kahan karein, 1930 aur cybercrime.gov.in ke saath, cover karta hoon.", "p")}
        {t("sess.club.p2", "Sessions can be in English, Hindi, Hinglish or Marathi. Online for clubs anywhere in India, or in person if your venue is in Mumbai. Tell me who will be in the room: students, residents, seniors, a women group, or a mixed audience.", "Sessions English, Hindi, Hinglish ya Marathi mein ho sakti hain. India ke kisi bhi club ke liye online, ya in person agar venue Mumbai mein hai. Bata dena room mein kaun hoga: students, residents, seniors, women group, ya mixed audience.", "p")}
        <p class="small"><a href="cyber-awareness-speaker-mumbai.html" data-i18n="sess.more.mum">Mumbai speaker page</a></p>
      </div>
    </section>

    <section class="section xp-sec" id="institutes" aria-labelledby="sess-inst-h">
      <div class="wrap xp-narrow">
        {t("sess.inst.h", "For coaching institutes and corporates", "Coaching institutes aur corporates ke liye", "h2").replace("<h2", '<h2 id="sess-inst-h"', 1)}
        {t("sess.inst.p1", "Coaching and IT institutes can book a longer session for batches preparing for jobs or a first role in tech. Along with the college topics, we can cover checking an app before you install it, internships that ask for fees, password managers, and safe habits for a first tech job.", "Coaching aur IT institutes un batches ke liye lambi session book kar sakte hain jo jobs ya tech ki pehli role ke liye prepare ho rahe hain. College wale topics ke saath, app install karne se pehle check karna, internships jo fees maange, password managers, aur pehli tech job ke safe habits bhi cover ho sakte hain.", "p")}
        {t("sess.inst.p2", "For company staff the usual focus is work email phishing, passwords and 2FA, QR and UPI risks, vendor and attachment caution, how to report, and a short, plain note on the DPDP Act. This is awareness only, not legal advice and not a full compliance audit. Online across India, or in person at Mumbai offices.", "Company staff ke liye usual focus hai work email phishing, passwords aur 2FA, QR aur UPI ke risks, vendor aur attachment ki caution, report kaise karein, aur DPDP Act pe ek chhota, simple note. Ye sirf awareness hai, legal advice nahi, aur poora compliance audit bhi nahi. Online poore India mein, ya Mumbai ke offices mein in person.", "p")}
      </div>
    </section>

    <section class="section xp-sec" id="get" aria-labelledby="sess-get-h">
      <div class="wrap xp-narrow">
        {t("sess.get.h", "What you get", "Aapko kya milta hai", "h2").replace("<h2", '<h2 id="sess-get-h"', 1)}
        <ul class="xp-list">
{get_html}
        </ul>
      </div>
    </section>

    <section class="section xp-sec" id="packages" aria-labelledby="sess-pack-h">
      <div class="wrap">
        {t("sess.pack.h", "Packages by audience", "Audience ke hisaab se packages", "h2").replace("<h2", '<h2 id="sess-pack-h"', 1)}
        {t("sess.pack.p", "Core topics are a starting point. Tell me what your group is worried about and I will shape the session around that.", "Yeh core topics ek starting point hain. Batao aapka group kis cheez se worried hai, main session usi ke around shape karunga.", "p", "muted")}
        <div class="xp-grid sess-grid">
{pack_html}
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="tiers" aria-labelledby="sess-tier-h">
      <div class="wrap">
        {t("sess.tier.h", "Choose a length", "Duration chuno", "h2").replace("<h2", '<h2 id="sess-tier-h"', 1)}
        <div class="xp-grid2">
{tier_html}
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="format" aria-labelledby="sess-mode-h">
      <div class="wrap">
        {t("sess.mode.h", "Online or in person", "Online ya in person", "h2").replace("<h2", '<h2 id="sess-mode-h"', 1)}
        <div class="xp-grid2">
          <article class="card sess-card">
            <p class="kicker mono">online</p>
            {t("sess.online.h", "Online, across India", "Online, poore India mein", "h3")}
            {t("sess.online.p", "For institutes anywhere in India, and abroad if the time works. We agree the platform over email. You need a stable internet link, and a way for the group to see and hear the session.", "India ke kisi bhi sheher ke institutes ke liye, aur bahar se bhi agar time match kare. Platform email pe agree karte hain. Stable internet chahiye, aur group ke liye session dekhne-sunne ka tareeka.", "p", "muted")}
          </article>
          <article class="card sess-card">
            <p class="kicker mono">offline</p>
            {t("sess.offline.h", "In person, Mumbai only", "In person, sirf Mumbai", "h3")}
            {t("sess.offline.p", "I come to your venue in Mumbai. Please share the address, the room setup, and facilities such as a projector, a microphone and internet.", "Main aapke Mumbai venue pe aata hoon. Address, room setup, aur projector, microphone aur internet jaise facilities bata dena.", "p", "muted")}
          </article>
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="addons" aria-labelledby="sess-add-h">
      <div class="wrap xp-narrow">
        {t("sess.add.h", "Add-ons you can request", "Add-ons jo aap maang sakte ho", "h2").replace("<h2", '<h2 id="sess-add-h"', 1)}
        <ul class="xp-list">
{addon_html}
        </ul>
      </div>
    </section>

    <section class="section xp-sec" id="booking" aria-labelledby="sess-book-h">
      <div class="wrap">
        {t("sess.how.h", "How booking works", "Booking kaise hoti hai", "h2").replace("<h2", '<h2 id="sess-book-h"', 1)}
        <div class="xp-grid2">
{step_html}
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="speaker" aria-labelledby="sess-spk-h">
      <div class="wrap xp-narrow">
        {t("sess.spk.h", "About the speaker", "Speaker ke baare mein", "h2").replace("<h2", '<h2 id="sess-spk-h"', 1)}
        {t("sess.spk.p1", "Madhav Pandya is a cybersecurity educator from Mumbai and the founder of CyberWithMadhav. He explains cybersecurity, scam awareness and Indian cyber law in plain English and Hinglish.", "Madhav Pandya Mumbai se cybersecurity educator hain aur CyberWithMadhav ke founder hain. Wo cybersecurity, scam awareness aur Indian cyber law simple English aur Hinglish mein samjhate hain.", "p")}
        {t("sess.spk.p2", "He is studying for a BCA in Cloud Computing and Cyber Security, and a BA LLB at KES Shri J.P. Law College. He also holds a Diploma in Cloud Computing, Oracle Cloud Infrastructure AI Associate, Agile Project Management from HP LIFE, and Prompt Engineering from Infosys Springboard.", "Wo Cloud Computing and Cyber Security mein BCA kar rahe hain, aur KES Shri J.P. Law College se BA LLB. Unke paas Diploma in Cloud Computing, Oracle Cloud Infrastructure AI Associate, HP LIFE se Agile Project Management, aur Infosys Springboard se Prompt Engineering bhi hai.", "p")}
        <p class="small"><a href="about.html" data-i18n="sess.spk.about">More on the About page</a> · <a href="collaborate.html" data-i18n="sess.spk.collab">Media kit and other collaborations</a></p>
      </div>
    </section>

    <section class="section xp-sec" id="standards" aria-labelledby="sess-std-h">
      <div class="wrap">
        <div class="card sess-std" role="note">
          {t("sess.std.h", "Session standards", "Session ke standards", "h2", "h3").replace("<h2", '<h2 id="sess-std-h"', 1)}
          <ul class="xp-list">
            <li>{t("sess.std.1", "The session is educational only. It is not legal advice.", "Session sirf educational hai. Ye legal advice nahi hai.", "span")}</li>
            <li>{t("sess.std.2", "There is no hacking of real accounts or real people.", "Asli accounts ya asli logon ki hacking nahi hoti.", "span")}</li>
            <li>{t("sess.std.3", "Any demo runs only on my own test devices.", "Koi bhi demo sirf meri apni test devices pe hota hai.", "span")}</li>
            <li>{t("sess.std.4", "I do not collect participants' personal data.", "Main participants ka personal data nahi leta.", "span")}</li>
            <li>{t("sess.std.5", "Sessions for minors happen only with a teacher or staff member present.", "Minors ke sessions sirf tab, jab teacher ya staff member present ho.", "span")}</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="faq" aria-labelledby="sess-faq-h">
      <div class="wrap xp-narrow">
        {t("sess.faq.h", "Questions institutes usually ask", "Institutes aksar ye poochte hain", "h2").replace("<h2", '<h2 id="sess-faq-h"', 1)}
        <div class="sess-faqs">
{faq_block}
        </div>
      </div>
    </section>

    <section class="section xp-sec" id="book" aria-labelledby="sess-cta-h">
      <div class="wrap">
        <div class="card sess-cta">
          {t("sess.end.h", "Ready to book a session?", "Session book karne ke liye ready ho?", "h2").replace("<h2", '<h2 id="sess-cta-h"', 1)}
          {t("sess.end.p", "Write to me at the address below. I read every email myself.", "Neeche wale address pe likho. Har email main khud padhta hoon.", "p", "muted")}
          <div class="xp-btns">
            <a class="btn btn-primary" href="{MAILTO}" data-i18n="sess.cta">Email to book a session</a>
          </div>
          <p class="mono small sess-email"><a href="mailto:{EMAIL}">{EMAIL}</a></p>
          {t("sess.chk.h", "What to include in your email", "Email mein kya likhein", "h3")}
          <ul class="xp-list sess-check">
{check_block}
          </ul>
        </div>
      </div>
    </section>
  </main>"""


def sessions_ld(desc):
    url = BASE + FILE
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
        "name": "Cybersecurity Awareness Sessions",
        "serviceType": "Cybersecurity awareness training",
        "description": desc,
        "url": url,
        "provider": person,
        "areaServed": [
            {"@type": "Country", "name": "India"},
            {"@type": "City", "name": "Mumbai", "containedInPlace": {"@type": "State", "name": "Maharashtra"}},
        ],
        "audience": [
            {"@type": "EducationalAudience", "educationalRole": "student", "audienceType": "College students, school students and coaching institute batches"},
            {"@type": "BusinessAudience", "audienceType": "Corporate staff, clubs, NGOs and housing societies"},
        ],
        "availableChannel": [
            {"@type": "ServiceChannel", "name": "Online session", "serviceLocation": {"@type": "Country", "name": "India"}},
            {"@type": "ServiceChannel", "name": "In-person session", "serviceLocation": {"@type": "City", "name": "Mumbai"}},
        ],
        "email": EMAIL,
        "isPartOf": {"@id": BASE + "#website"},
    }
    faq = {
        "@type": "FAQPage",
        "@id": url + "#faqpage",
        "url": url,
        "mainEntity": [
            {
                "@type": "Question",
                "name": it["q"],
                "acceptedAnswer": {"@type": "Answer", "text": it["a"]},
            }
            for it in FAQS
        ],
    }
    crumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "Cybersecurity awareness sessions", "item": url},
        ],
    }
    graph = {"@context": "https://schema.org", "@graph": [service, faq, crumbs]}
    return "  <script type=\"application/ld+json\">\n  " + json.dumps(graph, ensure_ascii=False) + "\n  </script>"


SPEC = {
    "file": FILE,
    "title": "Cyber Security Awareness Session Mumbai | CyberWithMadhav",
    "desc": "Book a cyber security awareness session or workshop for colleges, schools, clubs and corporates. Online across India, offline in Mumbai. By Madhav Pandya.",
    "og": "Cyber Security Awareness Session Mumbai | CyberWithMadhav",
    "ogdesc": "Book a cyber security awareness session or workshop for colleges, schools, clubs and corporates. Online across India, offline in Mumbai.",
    "keywords": "",
    "body": "xp-page sess-page",
    "css": ["pages.css", "extras.css"],
    "js": ["i18n/page-extras.js"],
    "foot": "Content is for awareness and education, not legal advice.",
}
