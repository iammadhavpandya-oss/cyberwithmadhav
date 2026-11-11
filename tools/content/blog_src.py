"""Blog posts for CyberWithMadhav. English is the indexed, authoritative text; the "hi" fields are the
Hinglish (Roman script) versions shown when a visitor switches the language toggle.
Rules: no invented statistics, official sources only, a Last reviewed date on every post, never backdate.
Build: python3 tools/build_blog.py (then build_site.py)."""

CATEGORIES = ["Scam awareness", "Cyber law India", "Learn cybersecurity", "Tools and labs"]
CAT_HI = {"Scam awareness": "Scam awareness", "Cyber law India": "Cyber law India",
          "Learn cybersecurity": "Cybersecurity seekho", "Tools and labs": "Tools aur labs"}

S_1930 = ("1930: National Cyber Crime Helpline", "tel:1930")
S_NCRP = ("cybercrime.gov.in: National Cyber Crime Reporting Portal", "https://cybercrime.gov.in/")
S_I4C = ("I4C, Ministry of Home Affairs: advisories", "https://i4c.mha.gov.in/advisories.aspx")
S_DA = ("I4C advisory on the digital arrest scam (TAU/ADV/003, 6 March 2025, PDF)", "https://cybercrime.gov.in/pdf/Advisories/ADVISORYTAU-ADV-003DigitalArrest06.03.2025.pdf")
S_RBI = ("RBI circular on limiting customer liability in unauthorised electronic banking transactions (6 July 2017, PDF)", "https://www.rbi.org.in/commonman/Upload/English/Notification/PDFs/NOTI1506072017.PDF")
S_CHAKSHU = ("Sanchar Saathi (DoT): Chakshu, report suspected fraud calls and messages", "https://sancharsaathi.gov.in/")
S_CERTIN = ("CERT-In: Indian Computer Emergency Response Team", "https://www.cert-in.org.in/")
S_ITACT = ("Information Technology Act, 2000 on India Code", "https://www.indiacode.nic.in/handle/123456789/1999")
S_NPCI = ("NPCI: UPI", "https://www.npci.org.in/")

POSTS = [
# ------------------------------------------------------------------ 1
{
 "slug": "report-cyber-fraud-india",
 "date": "2026-11-11", "reviewed": "2026-11-11",
 "category": "Scam awareness",
 "tags": ["1930", "cybercrime.gov.in", "UPI", "beginners"],
 "keywords": ["how to report cyber fraud India", "cyber crime complaint kaise kare", "1930 helpline", "cybercrime.gov.in complaint"],
 "title": "How to Report Cyber Fraud in India: 1930 and cybercrime.gov.in, Step by Step",
 "short": "How to report cyber fraud",
 "desc": "Lost money to an online fraud in India? Call 1930, then complete your complaint on cybercrime.gov.in. A step by step guide in plain English and Hinglish.",
 "lead": "If money has left your account because of a scam, the order of steps matters. Here is what to do, in order, with the official links.",
 "og_alt": "Share card reading How to report cyber fraud in India, with 1930 and cybercrime.gov.in",
 "quick": "Call <a href=\"tel:1930\">1930</a> as soon as you notice the fraud. You will get an acknowledgement number by SMS. Then log in at <a href=\"https://cybercrime.gov.in/\" target=\"_blank\" rel=\"noopener\">cybercrime.gov.in</a> and complete the full complaint with that number, and tell your bank through its official helpline. The faster you report, the better the chance that the money can be put on hold.",
 "sections": [
  ("first-hour", "What to do in the first hour", """
<p>Panic is normal. Ghabrao mat, but move fast, because money in a fraud usually moves quickly from one account to another. Do these things in this order:</p>
<ol>
<li><strong>Stop paying.</strong> Do not send any more money, even if the caller says it will "reverse" or "unlock" the first payment.</li>
<li><strong>Call 1930.</strong> This is the National Cyber Crime Helpline. It is run by the police of your state or union territory.</li>
<li><strong>Call your bank or card issuer</strong> on the number printed on your card or shown on the bank's official website or app. Ask them to block the card, UPI or net banking if it is at risk.</li>
<li><strong>Save the evidence</strong> before you do anything else with your phone (see the list below).</li>
<li><strong>Complete the complaint online</strong> at cybercrime.gov.in with the acknowledgement number you get from 1930.</li>
</ol>"""),
  ("call-1930", "Step 1: Call 1930", """
<p>When you call 1930, a police operator notes your details and the transaction details and raises a ticket on the Citizen Financial Cyber Fraud Reporting and Management System (CFCFRMS). This system connects the police with banks, wallets and payment companies, so that a reported amount can be traced and, if it is still in the system, put on hold.</p>
<p>Keep this ready before you call:</p>
<ul>
<li>your name, mobile number and address</li>
<li>the bank or app the money went from</li>
<li>the date, time and amount of each payment</li>
<li>the transaction ID or UTR number of each payment</li>
<li>the UPI ID, account number, phone number or link the money went to</li>
</ul>
<p>After the call you get an SMS with an acknowledgement number. The official CFCFRMS guidance asks you to then file the formal complaint on cybercrime.gov.in within 24 hours using that number. Don't skip this part.</p>"""),
  ("portal", "Step 2: Complete the complaint on cybercrime.gov.in", """
<p>The National Cyber Crime Reporting Portal is <a href="https://cybercrime.gov.in/" target="_blank" rel="noopener">cybercrime.gov.in</a>. Type the address yourself. Do not use a link from a search ad or a message.</p>
<ol>
<li>Choose the option to file a complaint. Financial frauds, hacking, fake profiles and most other online crimes go under the "Report Other Cybercrimes" route, which lets you track your complaint later.</li>
<li>Register with your name and a valid Indian mobile number and enter the OTP you receive.</li>
<li>Pick the category and sub category that matches what happened, for example online financial fraud, and enter the acknowledgement number from your 1930 call if you have one.</li>
<li>Describe what happened in simple words, in time order. Add every transaction and upload screenshots.</li>
<li>Submit and note the acknowledgement number. You can check progress with the track option on the portal.</li>
</ol>
<p>Crimes related to women and children, such as child sexual abuse material, have a separate option on the portal that also allows anonymous reporting. Anonymous reports cannot be tracked.</p>"""),
  ("evidence", "Evidence to keep", """
<p>Police and banks act on details. Before you delete anything or block anyone, save:</p>
<ul>
<li>screenshots of the chat, SMS, email, profile or ad that started it</li>
<li>bank or UPI app screenshots showing each debit, with the UTR or transaction ID</li>
<li>the scammer's phone numbers, UPI IDs, account numbers, website links and app names</li>
<li>call logs with dates and times</li>
<li>any receipt, "certificate" or document they sent you</li>
</ul>
<p>Sab kuch ek folder mein rakho. Don't edit or crop away the date and time.</p>"""),
  ("bank", "Tell your bank in writing too", """
<p>Your bank needs its own complaint, separate from the police complaint. Use the bank's official helpline, app or website, and keep the complaint or reference number.</p>
<p>The Reserve Bank of India has rules on how much of an unauthorised electronic banking loss a customer has to bear. Under the RBI's 2017 circular on limiting customer liability, how quickly you tell the bank affects your liability, and in some cases reporting within three working days can mean zero liability. If you shared your OTP or PIN yourself, the rules treat it differently. Check the RBI circular linked below, and ask your bank which rule it is applying to your case.</p>"""),
  ("no-loss", "No money lost? Still report it", """
<p>If you only received a fraud call, SMS or WhatsApp message and did not lose money, you can report the number on <strong>Chakshu</strong>, a facility on the Department of Telecommunications' Sanchar Saathi portal. If money is lost, use 1930 and cybercrime.gov.in instead.</p>
<p>For non financial cybercrimes such as a hacked account, a fake profile using your photos or online harassment, file on cybercrime.gov.in and also use the reporting tools of the app involved.</p>"""),
  ("recovery-scams", "Beware of fake recovery agents", """
<p>After a fraud, many people search online for help and land on "recovery experts", fake helplines or fake lawyers who ask for a fee to get the money back. This is a second scam. The 1930 helpline and cybercrime.gov.in are free. Dial 1930 directly and type cybercrime.gov.in yourself.</p>
<p>Ek baar jo dhokha hua, uske baad doosra mat hone do.</p>"""),
 ],
 "sources": [S_1930, S_NCRP, S_I4C, S_RBI, S_CHAKSHU],
 "related": ["digital-arrest-scam-india", "upi-scams-india"],
 "hubs": [("scams.html", "Scam Encyclopedia: 25 Indian scams explained"), ("index.html#awareness", "Scam awareness for every family"), ("cyberlaw.html", "Cyber Law India: IT Act, BNS and DPDP explained")],
 "hi": {
  "title": "India mein cyber fraud kaise report karein: 1930 aur cybercrime.gov.in, step by step",
  "lead": "Agar scam ki wajah se account se paise nikal gaye hain, to steps ka order bahut matter karta hai. Yahan sab kuch order mein hai, official links ke saath.",
  "quick": "Fraud pata chalte hi <a href=\"tel:1930\">1930</a> pe call karo. SMS pe ek acknowledgement number aayega. Fir <a href=\"https://cybercrime.gov.in/\" target=\"_blank\" rel=\"noopener\">cybercrime.gov.in</a> pe login karke us number ke saath poori complaint fill karo, aur apne bank ko uski official helpline pe batao. Jitna jaldi report karoge, utna better chance hai ki paisa hold pe lag jaye.",
  "sections": [
   ("Pehle ghante mein kya karein", """
<p>Ghabrana normal hai, par jaldi action lo, kyunki fraud ka paisa ek account se doosre account mein bahut jaldi move hota hai. Ye steps isi order mein karo:</p>
<ol>
<li><strong>Payment band karo.</strong> Aur paisa mat bhejo, chahe caller bole ki isse pehla payment "reverse" ya "unlock" ho jayega.</li>
<li><strong>1930 pe call karo.</strong> Ye National Cyber Crime Helpline hai, jo aapke state ya UT ki police chalati hai.</li>
<li><strong>Bank ya card company ko call karo</strong>, card ke peeche likhe number pe ya bank ki official website ya app wale number pe. Risk ho to card, UPI ya net banking block karwao.</li>
<li><strong>Evidence save karo</strong>, phone mein kuch bhi delete karne se pehle (list neeche hai).</li>
<li><strong>Online complaint poori karo</strong> cybercrime.gov.in pe, 1930 se mile acknowledgement number ke saath.</li>
</ol>"""),
   ("Step 1: 1930 pe call karo", """
<p>1930 pe call karne par police operator aapki details aur transaction details note karke Citizen Financial Cyber Fraud Reporting and Management System (CFCFRMS) pe ticket banata hai. Ye system police ko banks, wallets aur payment companies se jodta hai, taaki report hua amount trace ho sake aur agar system mein hai to hold pe lag sake.</p>
<p>Call se pehle ye ready rakho:</p>
<ul>
<li>apna naam, mobile number aur address</li>
<li>kis bank ya app se paisa gaya</li>
<li>har payment ki date, time aur amount</li>
<li>har payment ka transaction ID ya UTR number</li>
<li>jis UPI ID, account number, phone number ya link pe paisa gaya</li>
</ul>
<p>Call ke baad SMS pe acknowledgement number aata hai. Official CFCFRMS guidance kehti hai ki us number ke saath 24 ghante ke andar cybercrime.gov.in pe formal complaint file karo. Ye step skip mat karna.</p>"""),
   ("Step 2: cybercrime.gov.in pe complaint poori karo", """
<p>National Cyber Crime Reporting Portal hai <a href="https://cybercrime.gov.in/" target="_blank" rel="noopener">cybercrime.gov.in</a>. Address khud type karo. Search ad ya message wale link se mat kholo.</p>
<ol>
<li>Complaint file karne ka option chuno. Financial fraud, hacking, fake profile aur zyada tar online crimes "Report Other Cybercrimes" mein aate hain, jisme baad mein complaint track kar sakte ho.</li>
<li>Apne naam aur valid Indian mobile number se register karo aur OTP daalo.</li>
<li>Jo hua uske hisaab se category aur sub category chuno, jaise online financial fraud, aur 1930 wala acknowledgement number ho to daalo.</li>
<li>Kya hua, simple words mein, time ke order mein likho. Har transaction add karo aur screenshots upload karo.</li>
<li>Submit karke acknowledgement number note karo. Portal ke track option se progress dekh sakte ho.</li>
</ol>
<p>Women aur children se jude crimes, jaise child sexual abuse material, ke liye portal pe alag option hai jisme anonymous report bhi kar sakte ho. Anonymous report track nahi hoti.</p>"""),
   ("Kaunsa evidence rakhna hai", """
<p>Police aur bank details pe kaam karte hain. Kuch delete ya block karne se pehle save karo:</p>
<ul>
<li>jis chat, SMS, email, profile ya ad se shuru hua uske screenshots</li>
<li>bank ya UPI app ke screenshots jisme har debit aur UTR ya transaction ID dikhe</li>
<li>scammer ke phone numbers, UPI IDs, account numbers, website links aur app names</li>
<li>date aur time ke saath call logs</li>
<li>unka bheja koi bhi receipt, "certificate" ya document</li>
</ul>
<p>Sab kuch ek folder mein rakho. Date aur time crop mat karna.</p>"""),
   ("Bank ko bhi likh ke batao", """
<p>Police complaint ke alawa bank ko alag complaint chahiye. Bank ki official helpline, app ya website use karo aur complaint ya reference number sambhal ke rakho.</p>
<p>Reserve Bank of India ke rules hain ki unauthorised electronic banking loss ka kitna hissa customer ko bharna padega. RBI ke 2017 wale circular ke hisaab se, aap bank ko kitni jaldi batate ho isse aapki liability badalti hai, aur kuch cases mein teen working days ke andar report karne par liability zero ho sakti hai. Agar OTP ya PIN aapne khud share kiya tha, to rule alag lagta hai. Neeche diya RBI circular dekho, aur bank se poocho ki aapke case mein kaunsa rule laga rahe hain.</p>"""),
   ("Paisa nahi gaya? Fir bhi report karo", """
<p>Agar sirf fraud call, SMS ya WhatsApp message aaya aur paisa nahi gaya, to number ko <strong>Chakshu</strong> pe report kar sakte ho. Ye Department of Telecommunications ke Sanchar Saathi portal ki facility hai. Paisa gaya hai to 1930 aur cybercrime.gov.in hi use karo.</p>
<p>Non financial cybercrime, jaise hacked account, aapki photos wali fake profile ya online harassment, ke liye cybercrime.gov.in pe file karo aur us app ke reporting tools bhi use karo.</p>"""),
   ("Fake recovery agents se bacho", """
<p>Fraud ke baad bahut log online help dhoondhte hain aur "recovery experts", fake helplines ya fake lawyers tak pahunch jaate hain jo paisa wapas dilane ke liye fee maangte hain. Ye doosra scam hai. 1930 helpline aur cybercrime.gov.in free hain. 1930 seedha dial karo aur cybercrime.gov.in khud type karo.</p>
<p>Ek baar jo dhokha hua, uske baad doosra mat hone do.</p>"""),
  ],
 },
},
# ------------------------------------------------------------------ 2
{
 "slug": "digital-arrest-scam-india",
 "date": "2026-11-11", "reviewed": "2026-11-11",
 "category": "Scam awareness",
 "tags": ["digital arrest", "impersonation", "1930", "Hinglish"],
 "keywords": ["digital arrest scam India", "digital arrest kya hota hai", "fake CBI call", "1930 helpline"],
 "title": "Digital Arrest Scam: What It Is and What To Do",
 "short": "Digital arrest scam",
 "desc": "Digital arrest scam explained in plain English and Hinglish: how the call works, red flags, and what to do. Call 1930 and report at cybercrime.gov.in.",
 "lead": "There is no such thing as a digital arrest in Indian law. Here is how the scam works, how to spot it, and what to do if you or a family member gets the call.",
 "og_alt": "Share card reading Digital arrest scam: what it is and what to do",
 "quick": "\"Digital arrest\" is a scam, not a legal procedure. The Indian Cyber Crime Coordination Centre (I4C) says there is no concept of digital arrest under any Indian law, and real police, CBI, ED or RBI officials do not arrest anyone on a video call or ask for money to settle a case. Hang up, tell a family member, verify with your nearest police station on a number you look up yourself, and if you have paid, call <a href=\"tel:1930\">1930</a> at once.",
 "sections": [
  ("how", "How the scam works", """
<p>The I4C advisory on this scam describes a pattern that repeats with small changes:</p>
<ol>
<li><strong>The call.</strong> An automated (IVR) call or a person claims to be from a courier company, the telecom department, Mumbai Police, Delhi Police, the CBI, the narcotics department, the RBI or the Enforcement Directorate. The number shown can be spoofed.</li>
<li><strong>The accusation.</strong> You are told a parcel in your name has drugs or fake passports, or that your Aadhaar or mobile number was used for money laundering or other crimes. Sometimes they say a family member has been caught.</li>
<li><strong>The confinement.</strong> You are moved to a video call, often on WhatsApp or Skype, with people in uniform and a set that looks like a police station. You are told to keep the camera on, stay in the room and tell no one. This is the "digital arrest".</li>
<li><strong>The money.</strong> To "clear your name", "verify your funds" or "settle the case", you are told to transfer money to an account they give you. It never comes back.</li>
</ol>"""),
  ("red-flags", "Red flags", """
<ul>
<li>Anyone saying you are under "digital arrest" or "digital custody". This does not exist in law.</li>
<li>Being told to stay on a video call for hours and not tell your family.</li>
<li>Arrest warrants, court orders or ID cards sent as WhatsApp images or PDFs.</li>
<li>Any request to move money to a "safe", "RBI" or "verification" account.</li>
<li>Pressure, threats and a deadline measured in minutes.</li>
</ul>
<p>Asli police aise kaam nahi karti. Notice aata hai, proper process hota hai, video call pe arrest nahi hota.</p>"""),
  ("ruko-socho", "Ruko, Socho, Action lo", """
<p>In his Mann Ki Baat address on 27 October 2024, the Prime Minister spoke about this scam and gave a three step rule:</p>
<ul>
<li><strong>Ruko (stop):</strong> don't panic, and don't share any personal or bank details.</li>
<li><strong>Socho (think):</strong> no genuine agency questions you like this on a phone or video call or asks you for money.</li>
<li><strong>Action lo (act):</strong> call 1930, report on cybercrime.gov.in, tell your family and keep a record.</li>
</ul>"""),
  ("on-call", "If the call is happening right now", """
<ol>
<li>Disconnect. There is no penalty for hanging up on a stranger, whatever they claim to be.</li>
<li>Do not call back on any number they gave you, and do not install any app or open any link they send.</li>
<li>Tell someone at home or call a family member. The scam depends on keeping you alone.</li>
<li>If you are worried that a real case exists, call or visit your nearest police station using a number you find yourself.</li>
<li>Report the number on Chakshu on the Sanchar Saathi portal, even if you did not lose money.</li>
</ol>"""),
  ("paid", "If you have already paid", """
<p>Call <a href="tel:1930">1930</a> immediately, then complete the complaint on cybercrime.gov.in and inform your bank. Keep the call logs, numbers, video call IDs, screenshots and every transaction ID. Our step by step guide on <a href="blog-report-cyber-fraud-india.html">how to report cyber fraud in India</a> covers exactly what to keep and what to type.</p>
<p>It is not your fault. These are organised criminal groups that use fear very skilfully. Sharam mat karo, report karo.</p>"""),
  ("family", "Talk to your parents and grandparents", """
<p>Senior citizens are a common target. Tell them one simple line: "Koi bhi officer video call pe arrest nahi karta, aur case khatam karne ke liye paise nahi maangta." Save 1930 in their phone, and agree that they will call you before they send money to anyone who is threatening them.</p>"""),
  ("law", "Which laws apply", """
<p>Impersonating officials, threatening people and taking money this way can be offences under the Bharatiya Nyaya Sanhita, 2023, and cheating by personation using a computer resource is an offence under Section 66D of the Information Technology Act, 2000. The police decide which sections apply in a case. For the basics, see <a href="cyberlaw.html">Cyber Law India</a> on this site.</p>"""),
 ],
 "sources": [S_DA, S_I4C, S_NCRP, S_1930, S_CHAKSHU, S_ITACT],
 "related": ["report-cyber-fraud-india", "upi-scams-india"],
 "hubs": [("scams.html", "Scam Encyclopedia: digital arrest and 24 more scams"), ("game.html", "Scam ya Nahi? Practise spotting scam messages"), ("cyberlaw.html", "IT Act and BNS explained")],
 "hi": {
  "title": "Digital arrest scam: ye kya hai aur kya karein",
  "lead": "Indian law mein digital arrest naam ki koi cheez nahi hai. Yahan samjho scam kaise chalta hai, kaise pehchano, aur agar aapko ya family mein kisi ko call aaye to kya karna hai.",
  "quick": "\"Digital arrest\" ek scam hai, koi legal procedure nahi. Indian Cyber Crime Coordination Centre (I4C) kehta hai ki kisi bhi Indian law mein digital arrest ka concept hi nahi hai, aur asli police, CBI, ED ya RBI wale video call pe arrest nahi karte, na hi case settle karne ke liye paise maangte hain. Call kaato, family ko batao, nearest police station se khud dhoondhe number pe confirm karo, aur paise de diye ho to turant <a href=\"tel:1930\">1930</a> pe call karo.",
  "sections": [
   ("Scam kaise kaam karta hai", """
<p>I4C ki advisory ek pattern batati hai jo thode badlav ke saath baar baar repeat hota hai:</p>
<ol>
<li><strong>Call.</strong> Ek automated (IVR) call ya koi insaan khud ko courier company, telecom department, Mumbai Police, Delhi Police, CBI, narcotics department, RBI ya Enforcement Directorate se batata hai. Screen pe dikhne wala number spoof ho sakta hai.</li>
<li><strong>Ilzaam.</strong> Bola jata hai ki aapke naam ke parcel mein drugs ya fake passports hain, ya aapka Aadhaar ya mobile number money laundering jaise crime mein use hua. Kabhi kehte hain ki family ka koi member pakda gaya hai.</li>
<li><strong>Kaid.</strong> Aapko video call pe le jaate hain, aksar WhatsApp ya Skype pe, jahan uniform wale log aur police station jaisa set dikhta hai. Camera on rakhne, room mein rehne aur kisi ko na batane ko kehte hain. Yahi "digital arrest" hai.</li>
<li><strong>Paisa.</strong> "Naam clear karne", "funds verify karne" ya "case settle karne" ke liye unke diye account mein paise bhejne ko kehte hain. Wo kabhi wapas nahi aate.</li>
</ol>"""),
   ("Red flags", """
<ul>
<li>Koi bole ki aap "digital arrest" ya "digital custody" mein ho. Law mein aisa kuch nahi hai.</li>
<li>Ghanton video call pe rehne aur family ko na batane ko kaha jaye.</li>
<li>Arrest warrant, court order ya ID card WhatsApp image ya PDF mein bheje jaayein.</li>
<li>Paise kisi "safe", "RBI" ya "verification" account mein bhejne ki koi bhi request.</li>
<li>Pressure, dhamki aur minutes ki deadline.</li>
</ul>
<p>Asli police aise kaam nahi karti. Notice aata hai, proper process hota hai, video call pe arrest nahi hota.</p>"""),
   ("Ruko, Socho, Action lo", """
<p>27 October 2024 ke Mann Ki Baat mein Prime Minister ne is scam ke baare mein baat ki aur teen step ka rule diya:</p>
<ul>
<li><strong>Ruko:</strong> ghabrao mat, aur koi personal ya bank detail share mat karo.</li>
<li><strong>Socho:</strong> koi bhi asli agency phone ya video call pe aise poochtaach nahi karti, na paise maangti hai.</li>
<li><strong>Action lo:</strong> 1930 pe call karo, cybercrime.gov.in pe report karo, family ko batao aur record rakho.</li>
</ul>"""),
   ("Agar call abhi chal rahi hai", """
<ol>
<li>Call kaat do. Kisi anjaan ka call kaatne pe koi penalty nahi hai, wo khud ko kuch bhi bataye.</li>
<li>Unke diye number pe call back mat karo, aur unka bheja koi app ya link mat kholo.</li>
<li>Ghar pe kisi ko batao ya family member ko call karo. Scam tabhi chalta hai jab aap akele ho.</li>
<li>Agar dar hai ki sach mein koi case hai, to nearest police station ko khud dhoondhe number pe call karo ya wahan jao.</li>
<li>Number ko Sanchar Saathi portal ke Chakshu pe report karo, chahe paisa na gaya ho.</li>
</ol>"""),
   ("Agar paise de diye hain", """
<p>Turant <a href="tel:1930">1930</a> pe call karo, fir cybercrime.gov.in pe complaint poori karo aur bank ko batao. Call logs, numbers, video call IDs, screenshots aur har transaction ID sambhal ke rakho. Hamari step by step guide <a href="blog-report-cyber-fraud-india.html">India mein cyber fraud kaise report karein</a> mein sab detail hai ki kya rakhna hai aur kya likhna hai.</p>
<p>Isme aapki galti nahi hai. Ye organised criminal groups hain jo dar ka bahut chalaki se use karte hain. Sharam mat karo, report karo.</p>"""),
   ("Mummy papa aur dada dadi se baat karo", """
<p>Senior citizens aksar target hote hain. Unhe ek simple line yaad karwao: "Koi bhi officer video call pe arrest nahi karta, aur case khatam karne ke liye paise nahi maangta." Unke phone mein 1930 save karo, aur tay karo ki dhamki dene wale ko paise bhejne se pehle wo aapko call karenge.</p>"""),
   ("Kaunse laws lagte hain", """
<p>Officials ki nakal karna, logon ko dhamkana aur is tarah paise lena Bharatiya Nyaya Sanhita, 2023 ke under offence ho sakta hai, aur computer resource se personation karke cheating Information Technology Act, 2000 ke Section 66D ke under offence hai. Kis case mein kaunse sections lagenge, ye police decide karti hai. Basics ke liye is site ka <a href="cyberlaw.html">Cyber Law India</a> dekho.</p>"""),
  ],
 },
},
# ------------------------------------------------------------------ 3
{
 "slug": "upi-scams-india",
 "date": "2026-11-11", "reviewed": "2026-11-11",
 "category": "Scam awareness",
 "tags": ["UPI", "QR code", "refund scam", "1930"],
 "keywords": ["UPI fraud what to do", "UPI scam se kaise bache", "fake QR code scam", "UPI collect request scam"],
 "title": "UPI Scams Explained: Collect Requests, Fake QR Codes and Refund Tricks",
 "short": "UPI scams explained",
 "desc": "UPI scams explained in plain English and Hinglish: collect requests, fake QR codes, sent by mistake and refund tricks, and what to do if you lose money.",
 "lead": "Almost every UPI scam relies on one confusion: thinking you need to scan, approve or enter your PIN to receive money. You never do.",
 "og_alt": "Share card reading UPI scams explained: collect requests, fake QR codes and refund tricks",
 "quick": "You only enter your UPI PIN to send money, never to receive it, and you never need to scan a QR code to get paid. If any screen asks for your PIN, money is about to leave your account. If you have lost money, call <a href=\"tel:1930\">1930</a>, report on <a href=\"https://cybercrime.gov.in/\" target=\"_blank\" rel=\"noopener\">cybercrime.gov.in</a> and raise a complaint with your bank and in your UPI app.",
 "sections": [
  ("pin-rule", "The one rule: PIN means money out", """
<p>UPI has two directions. In a <em>push</em> payment you start it, by scanning a QR code or entering a UPI ID, and you confirm with your PIN. In a <em>pull</em> payment, also called a collect request, someone else asks for money and you approve it with your PIN.</p>
<p>In both cases, your PIN moves money out of your account. Receiving money needs nothing from you. PIN daala matlab paisa gaya. Bas itna yaad rakho.</p>"""),
  ("collect", "Collect request scams", """
<p>In this trick, a "buyer", "customer care agent" or "lottery office" sends a request to your UPI app and tells you to approve it to receive a payment or a refund. Approving with your PIN actually pays them.</p>
<p>The National Payments Corporation of India (NPCI), which runs UPI, told banks and UPI apps to stop person to person (P2P) collect requests from 1 October 2025 (circular NPCI/UPI/OC/220/2025-26 dated 29 July 2025). Collect requests from merchants, such as a shopping or ticket booking app, still exist. So if a payment request pops up that you did not start yourself, decline it.</p>"""),
  ("qr", "Fake QR code scams", """
<p>A QR code is a way to pay, not to get paid. Common versions:</p>
<ul>
<li>A "buyer" on a selling site sends a QR code and says "scan this to receive the advance". Scanning and entering your PIN sends your money to them.</li>
<li>A sticker pasted over a shop's real QR code, so your payment goes to someone else. Before you enter the PIN, check that the name shown in your app is the shop's name.</li>
<li>QR codes in emails, posters or messages that open a fake payment or login page.</li>
</ul>
<p>Paise lene ke liye scan nahi karna padta. Jo bole "scan karo, paise aayenge", wahi scammer hai.</p>"""),
  ("refund", "Refund and \"sent by mistake\" tricks", """
<ul>
<li><strong>Fake credit SMS.</strong> You get an SMS that looks like a bank alert saying money was credited, then a call: "I sent it by mistake, please send it back." The SMS is fake. Open your bank or UPI app and check your actual balance and history, not the SMS.</li>
<li><strong>Real mistaken credit.</strong> If money really arrived and someone asks for it back, do not send it to a new number or UPI ID they give you. Ask them to contact their own bank, which can handle a wrong transfer through official channels.</li>
<li><strong>Fake customer care.</strong> Numbers from search results, comments or social media posts that claim to be a bank, app or courier helpline. They ask you to approve a "refund" request or install a screen sharing app, then take control. Get support numbers only from the official app or website.</li>
</ul>"""),
  ("habits", "Simple safety habits", """
<ul>
<li>Read the payee name on the confirmation screen before you enter your PIN.</li>
<li>Never share your UPI PIN, OTP or card details with anyone, including someone who says they are from your bank.</li>
<li>Do not install screen sharing or remote access apps because a caller asked you to.</li>
<li>Keep your phone and UPI apps updated, and lock the apps with a screen lock.</li>
<li>Turn on SMS and email alerts from your bank so you see every debit.</li>
</ul>"""),
  ("lost-money", "If you lost money through UPI", """
<ol>
<li>Call <a href="tel:1930">1930</a> right away and keep the acknowledgement number.</li>
<li>Complete the complaint on cybercrime.gov.in with every UTR or transaction ID.</li>
<li>Report it to your bank and raise a complaint inside your UPI app.</li>
<li>Save screenshots of the chats, the request or QR code and the payment screens.</li>
</ol>
<p>The full steps are in <a href="blog-report-cyber-fraud-india.html">how to report cyber fraud in India</a>. To check a suspicious link someone sent you without opening it, try the <a href="index.html#link-tool">link checker</a> on the home page.</p>"""),
 ],
 "sources": [S_1930, S_NCRP, S_NPCI, S_RBI, S_I4C, S_CERTIN],
 "related": ["report-cyber-fraud-india", "digital-arrest-scam-india"],
 "hubs": [("index.html#link-tool", "Is this link suspicious? Free link checker"), ("scams.html", "Scam Encyclopedia: UPI and 24 more scams"), ("game.html", "Scam ya Nahi? Spot the scam game")],
 "hi": {
  "title": "UPI scams samjho: collect requests, fake QR codes aur refund tricks",
  "lead": "Lagbhag har UPI scam ek hi confusion pe chalta hai: ye sochna ki paise lene ke liye scan, approve ya PIN daalna padta hai. Kabhi nahi padta.",
  "quick": "UPI PIN sirf paise bhejne ke liye daalte hain, lene ke liye kabhi nahi, aur payment lene ke liye QR code scan karne ki zaroorat nahi hoti. Agar koi screen PIN maange, to paisa aapke account se jaane wala hai. Paise chale gaye hain to <a href=\"tel:1930\">1930</a> pe call karo, <a href=\"https://cybercrime.gov.in/\" target=\"_blank\" rel=\"noopener\">cybercrime.gov.in</a> pe report karo, aur bank aur UPI app mein complaint daalo.",
  "sections": [
   ("Ek rule: PIN matlab paisa bahar", """
<p>UPI ki do directions hain. <em>Push</em> payment aap khud shuru karte ho, QR scan karke ya UPI ID daal ke, aur PIN se confirm karte ho. <em>Pull</em> payment, yaani collect request, mein koi aur paise maangta hai aur aap PIN se approve karte ho.</p>
<p>Dono cases mein PIN se paisa aapke account se bahar jaata hai. Paise lene ke liye aapko kuch nahi karna padta. PIN daala matlab paisa gaya. Bas itna yaad rakho.</p>"""),
   ("Collect request scams", """
<p>Is trick mein koi "buyer", "customer care agent" ya "lottery office" aapke UPI app pe request bhejta hai aur kehta hai ki payment ya refund lene ke liye approve karo. PIN se approve karte hi aap unhe pay kar dete ho.</p>
<p>UPI chalane wali National Payments Corporation of India (NPCI) ne banks aur UPI apps ko 1 October 2025 se person to person (P2P) collect requests band karne ko kaha (circular NPCI/UPI/OC/220/2025-26, dated 29 July 2025). Merchants, jaise shopping ya ticket booking apps, ki collect requests abhi bhi hoti hain. Isliye jo payment request aapne khud shuru nahi ki, use decline karo.</p>"""),
   ("Fake QR code scams", """
<p>QR code pay karne ke liye hota hai, paise lene ke liye nahi. Common tareeke:</p>
<ul>
<li>Selling site pe koi "buyer" QR bhejta hai aur kehta hai "advance lene ke liye scan karo". Scan karke PIN daalte hi aapka paisa unke paas.</li>
<li>Dukaan ke asli QR ke upar chipka sticker, taaki payment kisi aur ko jaye. PIN daalne se pehle check karo ki app mein dukaan ka hi naam dikh raha hai.</li>
<li>Emails, posters ya messages ke QR codes jo fake payment ya login page kholte hain.</li>
</ul>
<p>Paise lene ke liye scan nahi karna padta. Jo bole "scan karo, paise aayenge", wahi scammer hai.</p>"""),
   ("Refund aur \"galti se bhej diya\" tricks", """
<ul>
<li><strong>Fake credit SMS.</strong> Bank alert jaisa SMS aata hai ki paise credit hue, fir call: "Galti se bhej diya, please wapas bhej do." SMS fake hota hai. Bank ya UPI app kholke asli balance aur history dekho, SMS nahi.</li>
<li><strong>Sach mein galti se aaya paisa.</strong> Agar paisa sach mein aaya aur koi wapas maange, to unke diye naye number ya UPI ID pe mat bhejo. Unhe apne bank se contact karne ko bolo, jo galat transfer official tareeke se handle karta hai.</li>
<li><strong>Fake customer care.</strong> Search results, comments ya social media posts mein bank, app ya courier helpline ke naam pe numbers. Wo "refund" request approve karwate hain ya screen sharing app install karwa ke control le lete hain. Support number sirf official app ya website se lo.</li>
</ul>"""),
   ("Simple safety habits", """
<ul>
<li>PIN daalne se pehle confirmation screen pe payee ka naam padho.</li>
<li>UPI PIN, OTP ya card details kisi ko mat do, us insaan ko bhi nahi jo khud ko bank wala bataye.</li>
<li>Caller ke kehne pe screen sharing ya remote access app install mat karo.</li>
<li>Phone aur UPI apps updated rakho, aur apps pe screen lock lagao.</li>
<li>Bank ke SMS aur email alerts on rakho taaki har debit dikhe.</li>
</ul>"""),
   ("Agar UPI se paise chale gaye", """
<ol>
<li>Turant <a href="tel:1930">1930</a> pe call karo aur acknowledgement number sambhalo.</li>
<li>Har UTR ya transaction ID ke saath cybercrime.gov.in pe complaint poori karo.</li>
<li>Bank ko report karo aur UPI app ke andar bhi complaint daalo.</li>
<li>Chats, request ya QR code aur payment screens ke screenshots save karo.</li>
</ol>
<p>Poore steps <a href="blog-report-cyber-fraud-india.html">India mein cyber fraud kaise report karein</a> mein hain. Kisi ka bheja shady link bina khole check karna ho, to home page pe <a href="index.html#link-tool">link checker</a> try karo.</p>"""),
  ],
 },
},
]
