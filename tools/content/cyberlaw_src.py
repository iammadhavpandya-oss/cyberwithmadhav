# Source of data/cyberlaw.json. Edit here, then: python3 tools/build_pages_data.py
S = {
 "itact": "https://www.indiacode.nic.in/handle/123456789/1999",
 "itact_pdf": "https://www.py.gov.in/sites/default/files/information-technology-act-20003.pdf",
 "itact_updated": "https://www.indiacode.nic.in/indiacode/bitstream/123456789/13116/1/it_act_2000_updated.pdf",
 "sansad": "https://sansad.in/getFile/loksabhaquestions/annex/182/AS226_y8fPvt.pdf",
 "janvishwas": "https://www.meity.gov.in/static/uploads/2024/03/MeitY-JVA-1.pdf",
 "janvishwas_date": "https://www.meity.gov.in/static/uploads/2024/03/249809-Notification-dtd-31-10-2023-Date-of-appointment-for-enforcing-Amendments-to-IT-Act-2000-under-Jan-Vishwas-Act-2023.pdf",
 "shreya": "https://indiankanoon.org/doc/110813550/",
 "pucl": "https://indiankanoon.org/doc/173319912/",
 "puttaswamy": "https://digiscr.sci.gov.in/view_judgment?id=NjEwMg==",
 "anvar": "https://indiankanoon.org/doc/160854826/",
 "arjun": "https://digiscr.sci.gov.in/view_judgment?id=MTA2MjI=",
 "bhasin": "https://digiscr.sci.gov.in/view_judgment?id=OTQwOA%3D%3D",
 "sharat": "https://indiankanoon.org/doc/153597150/",
 "justrights": "https://api.sci.gov.in/supremecourt/2024/8562/8562_2024_1_1501_56073_Judgement_23-Sep-2024.pdf",
 "kamra": "https://www.livelaw.in/high-court/bombay-high-court/it-rules-amendment-2023-unconstitutional-bombay-high-court-third-judge-verdict-kunal-kamra-270177",
 "spdi": "https://upload.indiacode.nic.in/showfile?actid=AC_CEN_45_76_00001_200021_1517807324077&filename=GSR313E_10511%281%29_0.pdf&type=rule",
 "itrules21": "https://mib.gov.in/sites/default/files/IT%28Intermediary%20Guidelines%20and%20Digital%20Media%20Ethics%20Code%29%20Rules%2C%202021%20English.pdf",
 "certin": "https://www.cert-in.org.in/PDF/CERT-In_directions_extension_MSMEs_and_validation_27.06.2022.pdf",
 "dpdp": "https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023.pdf",
 "dpdp_commence": "https://egazette.gov.in/WriteReadData/2025/267647.pdf",
 "dpdp_rules": "https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa",
 "dpdp_pib": "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2190014",
 "newlaws": "https://www.ncrb.mha.gov.in/uploads/SankalanPortal/DownloadPDF/GazetteNotificationOfBNS,BNSS,BSA.pdf",
 "bns_table": "https://www.ncrb.gov.in/uploads/SankalanPortal/SectionTableBNS.html",
 "tdsat": "https://tdsat.gov.in/admin/introduction/uploads/TDSAT%20INTRO.pdf",
 "fin169": "https://indiacode.ecourtsindia.com/finance-act-2017/section/169/",
 "ncrp": "https://cybercrime.gov.in/",
}

hero = {
 "kicker": "IT Act 2000 · Sections 43 and 66",
 "title": "Entering someone's device without permission is illegal in India",
 "sub": "Under Section 43 of the IT Act, accessing a computer, phone, network or data without the owner's permission makes you liable to pay compensation, even with no bad intent: it is a civil wrong. Do the same act dishonestly or fraudulently and it becomes a crime under Section 66, punishable with up to 3 years in jail, a fine of up to ₹5 lakh, or both.",
 "cards": [
  {"k": "Sec 43", "label": "Civil wrong", "text": "Access without permission. Pay damages by way of compensation to the person affected. No intent needed.", "src": S["itact_pdf"]},
  {"k": "Sec 66", "label": "Crime", "text": "Any Sec 43 act done dishonestly or fraudulently. Up to 3 years, or fine up to ₹5 lakh, or both. Cognizable and bailable (Sec 77B).", "src": S["itact_pdf"]}
 ],
 "note": "An honest, unknowing act is not a Section 66 offence. It can still attract Section 43 compensation.",
 "disclaimer": "Educational, not legal advice. Check the current bare act and case law before you rely on anything here."
}

timeline = [
 {"date": "9 Jun 2000", "title": "Information Technology Act, 2000 (Act 21 of 2000)", "text": "Assent on 9 June 2000; in force from 17 October 2000. Gave legal recognition to electronic records and signatures and created the first cyber contraventions and offences. Based on the UNCITRAL Model Law on Electronic Commerce.", "src": S["itact"]},
 {"date": "27 Oct 2009", "title": "IT (Amendment) Act, 2008 in force (Act 10 of 2009)", "text": "Added Sections 66A to 66F, 67A, 67B, 69A, 72A, 43A and 77A/77B, removed the old compensation cap in Section 43 and moved to the technology-neutral term 'electronic signature'.", "src": S["itact_pdf"]},
 {"date": "11 Apr 2011", "title": "SPDI Rules, 2011", "text": "The Reasonable Security Practices and Sensitive Personal Data or Information Rules (G.S.R. 313(E)) under Section 43A: privacy policy, consent, disclosure limits and reasonable security (IS/ISO/IEC 27001 named as one standard).", "src": S["spdi"]},
 {"date": "24 Mar 2015", "title": "Shreya Singhal v. Union of India", "text": "Supreme Court struck down Section 66A as violating Article 19(1)(a). Upheld Section 69A blocking. Read down Section 79(3)(b): 'actual knowledge' means a court order or government notification.", "src": S["shreya"]},
 {"date": "26 May 2017", "title": "Cyber Appellate Tribunal merged into TDSAT", "text": "Finance Act, 2017 (Section 169) made the Telecom Disputes Settlement and Appellate Tribunal the 'Appellate Tribunal' under the IT Act.", "src": S["fin169"]},
 {"date": "24 Aug 2017", "title": "Justice K.S. Puttaswamy v. Union of India", "text": "Nine-judge bench held that privacy is a fundamental right under Article 21 and Part III. The foundation for India's data protection law.", "src": S["puttaswamy"]},
 {"date": "25 Feb 2021", "title": "IT (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021", "text": "G.S.R. 139(E), replacing the 2011 intermediary rules: due diligence, grievance officers, extra duties for significant social media intermediaries and a code for digital news and OTT publishers.", "src": S["itrules21"]},
 {"date": "28 Apr 2022", "title": "CERT-In Directions under Section 70B(6)", "text": "Report listed cyber incidents to CERT-In within 6 hours, keep ICT logs for a rolling 180 days within India, sync clocks to NIC/NPL NTP. Effective 27 June 2022; extended to 25 September 2022 for MSMEs and some VPN/cloud KYC duties.", "src": S["certin"]},
 {"date": "11 Aug 2023", "title": "Digital Personal Data Protection Act, 2023", "text": "Consent-based processing, Data Principal rights, Data Protection Board of India and penalties of up to ₹250 crore.", "src": S["dpdp"]},
 {"date": "30 Nov 2023", "title": "Jan Vishwas Act changes to the IT Act", "text": "Section 66A formally omitted. Sections 72 and 72A turned from offences into penalties (up to ₹5 lakh and ₹25 lakh).", "src": S["janvishwas_date"]},
 {"date": "1 Jul 2024", "title": "BNS, BNSS and BSA in force", "text": "Bharatiya Nyaya Sanhita, Bharatiya Nagarik Suraksha Sanhita and Bharatiya Sakshya Adhiniyam replaced the IPC, CrPC and Indian Evidence Act.", "src": S["newlaws"]},
 {"date": "1 Jul 2024", "title": "Electronic evidence: Section 65B becomes BSA Section 63", "text": "Certificate requirement continues. Anvar P.V. (2014) made the 65B certificate mandatory for secondary electronic evidence; Arjun Panditrao Khotkar (2020) confirmed it and overruled Shafhi Mohammad. BSA 63 adds a two-part certificate format in its Schedule.", "src": S["arjun"], "verify": "Whether Anvar and Arjun Panditrao apply unchanged to BSA 63 is still being worked out by courts."},
 {"date": "13 Nov 2025", "title": "DPDP Rules, 2025 notified", "text": "G.S.R. 846(E). Board provisions in force at once; consent manager rules after 1 year; most duties of Data Fiduciaries after 18 months (around 13 May 2027). DPDP Act Section 44(2), which omits IT Act Section 43A, also starts at 18 months.", "src": S["dpdp_commence"]}
]

# bail/compound columns: per Sec 77A/77B and BNSS First Schedule Part II; Lok Sabha answer used as cross-check
itact = [
 {"sec": "43", "title": "Unauthorised access, download, virus, damage, disruption and more", "kind": "civil", "punishment": "Damages by way of compensation to the person affected (no upper cap in the section). Adjudicating Officer up to ₹5 crore claims, civil court above.", "bail": "Not an offence", "compound": "Contravention can be compounded under Sec 63", "src": S["itact_pdf"]},
 {"sec": "43A", "title": "Body corporate negligent in protecting sensitive personal data", "kind": "civil", "punishment": "Damages by way of compensation. To be omitted when DPDP Act Sec 44(2) commences (18 months from 13 Nov 2025).", "bail": "Not an offence", "compound": "Sec 63", "src": S["dpdp_commence"]},
 {"sec": "65", "title": "Tampering with computer source documents", "kind": "offence", "punishment": "Up to 3 years, or fine up to ₹2 lakh, or both", "bail": "Bailable, cognizable", "compound": "Yes (Sec 77A)", "src": S["itact_pdf"]},
 {"sec": "66", "title": "Computer related offences (Sec 43 acts done dishonestly or fraudulently)", "kind": "offence", "punishment": "Up to 3 years, or fine up to ₹5 lakh, or both", "bail": "Bailable, cognizable", "compound": "Yes (Sec 77A)", "src": S["itact_pdf"]},
 {"sec": "66A", "title": "Offensive messages", "kind": "struck", "punishment": "Struck down in Shreya Singhal (2015); omitted by Jan Vishwas Act from 30 Nov 2023. No one can be prosecuted (PUCL, 2022).", "bail": "n/a", "compound": "n/a", "src": S["pucl"]},
 {"sec": "66B", "title": "Dishonestly receiving stolen computer resource or device", "kind": "offence", "punishment": "Up to 3 years, or fine up to ₹1 lakh, or both", "bail": "Bailable, cognizable", "compound": "Yes (Sec 77A)", "src": S["itact_pdf"]},
 {"sec": "66C", "title": "Identity theft (password, e-signature, unique ID)", "kind": "offence", "punishment": "Up to 3 years and fine up to ₹1 lakh", "bail": "Bailable, cognizable", "compound": "Yes, unless against a woman or child (Sec 77A)", "src": S["itact_pdf"]},
 {"sec": "66D", "title": "Cheating by personation using a computer resource", "kind": "offence", "punishment": "Up to 3 years and fine up to ₹1 lakh", "bail": "Bailable, cognizable", "compound": "Yes, unless against a woman or child (Sec 77A)", "src": S["itact_pdf"]},
 {"sec": "66E", "title": "Violation of privacy (images of private area without consent)", "kind": "offence", "punishment": "Up to 3 years, or fine up to ₹2 lakh, or both", "bail": "Bailable, cognizable", "compound": "Usually no: most victims are women, and 77A bars compounding then", "src": S["itact_pdf"], "verify": "Compoundability depends on the victim; check 77A proviso on the facts."},
 {"sec": "66F", "title": "Cyber terrorism", "kind": "offence", "punishment": "Imprisonment which may extend to life", "bail": "Non-bailable, cognizable", "compound": "No", "src": S["itact_pdf"]},
 {"sec": "67", "title": "Publishing or transmitting obscene material electronically", "kind": "offence", "punishment": "First: up to 3 years and fine up to ₹5 lakh. Repeat: up to 5 years and fine up to ₹10 lakh", "bail": "First: bailable. Repeat: non-bailable. Cognizable", "compound": "First conviction only, and not if against a woman or child", "src": S["itact_pdf"]},
 {"sec": "67A", "title": "Sexually explicit material", "kind": "offence", "punishment": "First: up to 5 years and fine up to ₹10 lakh. Repeat: up to 7 years and fine up to ₹10 lakh", "bail": "Non-bailable, cognizable", "compound": "No (over 3 years)", "src": S["itact_pdf"]},
 {"sec": "67B", "title": "Child sexual exploitation and abuse material (CSEAM)", "kind": "offence", "punishment": "First: up to 5 years and fine up to ₹10 lakh. Repeat: up to 7 years and fine up to ₹10 lakh. Covers browsing, downloading and storing too (Just Rights for Children Alliance, 2024)", "bail": "Non-bailable, cognizable", "compound": "No", "src": S["justrights"]},
 {"sec": "69", "title": "Failing to assist lawful interception, monitoring or decryption", "kind": "offence", "punishment": "Up to 7 years and fine", "bail": "Non-bailable, cognizable", "compound": "No", "src": S["itact_pdf"]},
 {"sec": "69A", "title": "Intermediary not complying with a blocking direction", "kind": "offence", "punishment": "Up to 7 years and fine", "bail": "Non-bailable, cognizable", "compound": "No", "src": S["itact_pdf"]},
 {"sec": "70", "title": "Unauthorised access to a notified protected system", "kind": "offence", "punishment": "Up to 10 years and fine", "bail": "Non-bailable, cognizable", "compound": "No", "src": S["itact_pdf"]},
 {"sec": "72", "title": "Breach of confidentiality by a person acting under powers of the Act", "kind": "civil", "punishment": "Penalty up to ₹5 lakh (was up to 2 years jail before 30 Nov 2023)", "bail": "Not an offence since Jan Vishwas", "compound": "n/a", "src": S["janvishwas"]},
 {"sec": "72A", "title": "Disclosure of personal information in breach of lawful contract", "kind": "civil", "punishment": "Penalty up to ₹25 lakh (was up to 3 years jail or ₹5 lakh fine before 30 Nov 2023)", "bail": "Not an offence since Jan Vishwas", "compound": "n/a", "src": S["janvishwas"]},
 {"sec": "77A", "title": "Compounding of offences", "kind": "rule", "punishment": "A court may compound offences other than those punishable with life or over 3 years. Not where enhanced punishment applies for a prior conviction, or the offence affects socio-economic conditions, or is against a child under 18 or a woman.", "bail": "n/a", "compound": "n/a", "src": S["itact_pdf"], "verify": "77A(2) still refers to CrPC 265B/265C (plea bargaining); read with the matching BNSS provisions."},
 {"sec": "77B", "title": "Cognizable and bailable", "kind": "rule", "punishment": "Offences punishable with 3 years and above are cognizable; offences punishable with 3 years are bailable. Others follow the BNSS First Schedule Part II (3 to 7 years: non-bailable).", "bail": "n/a", "compound": "n/a", "src": S["sansad"]},
 {"sec": "79", "title": "Safe harbour for intermediaries", "kind": "rule", "punishment": "No liability for third-party content if the intermediary only provides access, does not initiate, select the receiver or modify, observes due diligence (IT Rules 2021), and acts on actual knowledge (court order or government notice, per Shreya Singhal).", "bail": "n/a", "compound": "n/a", "src": S["shreya"]},
 {"sec": "84B", "title": "Abetment", "kind": "offence", "punishment": "Same punishment as the offence abetted, if committed in consequence and no express provision exists", "bail": "Follows the main offence", "compound": "Follows the main offence", "src": S["itact_pdf"]},
 {"sec": "84C", "title": "Attempt", "kind": "offence", "punishment": "Up to half of the longest term for the offence, or the fine for it, or both", "bail": "Follows the term", "compound": "Follows the term", "src": S["itact_pdf"]}
]

bns = [
 {"topic": "Cheating (online fraud, UPI and investment scams)", "bns": "318 (318(4) for inducing delivery of property)", "ipc": "415, 417, 418, 420", "src": S["bns_table"]},
 {"topic": "Cheating by personation (fake profiles, fake officials)", "bns": "319", "ipc": "416, 419", "src": S["bns_table"]},
 {"topic": "Extortion (sextortion, 'digital arrest' demands)", "bns": "308", "ipc": "383 to 389", "src": S["bns_table"]},
 {"topic": "Defamation", "bns": "356", "ipc": "499 to 502", "src": S["bns_table"]},
 {"topic": "Organised crime (definition expressly covers cyber-crimes)", "bns": "111", "ipc": "New, no IPC equivalent", "src": S["bns_table"]},
 {"topic": "Petty organised crime", "bns": "112", "ipc": "New", "src": S["bns_table"]},
 {"topic": "Forgery, including for cheating or harming reputation", "bns": "336 (336(3), 336(4))", "ipc": "463, 465, 468, 469", "src": S["bns_table"]},
 {"topic": "Making a false document (includes electronic records)", "bns": "335", "ipc": "464", "src": S["bns_table"]},
 {"topic": "Criminal intimidation, incl. anonymous communication", "bns": "351 (351(4))", "ipc": "503, 506, 507", "src": S["bns_table"]},
 {"topic": "Stalking (includes monitoring a woman's internet or email use)", "bns": "78", "ipc": "354D", "src": S["bns_table"]},
 {"topic": "Voyeurism", "bns": "77", "ipc": "354C", "src": S["bns_table"]},
 {"topic": "Sexual harassment", "bns": "75", "ipc": "354A", "src": S["bns_table"]},
 {"topic": "Statements conducing to public mischief (fake news)", "bns": "353", "ipc": "505", "src": S["bns_table"]},
 {"topic": "Criminal breach of trust", "bns": "316", "ipc": "405 to 409", "src": S["bns_table"]},
 {"topic": "Theft (devices, data carriers)", "bns": "303", "ipc": "378, 379", "src": S["bns_table"]},
 {"topic": "Criminal conspiracy", "bns": "61", "ipc": "120A, 120B", "src": S["bns_table"]}
]
bns_note = "Where the act is about an electronic record and the IT Act covers it, the Supreme Court treats the IT Act as the special law (Sharat Babu Digumarti, 2016). Check overlap case by case."

dpdp = {
 "intro": "Penalties are imposed by the Data Protection Board after an inquiry, under Section 33 and the Schedule. They are maximum amounts, not fixed fines.",
 "rows": [
  {"breach": "Failing to take reasonable security safeguards to prevent a personal data breach (Sec 8(5))", "max": "₹250 crore"},
  {"breach": "Failing to notify the Board or affected Data Principals of a breach (Sec 8(6))", "max": "₹200 crore"},
  {"breach": "Additional obligations for children (Sec 9)", "max": "₹200 crore"},
  {"breach": "Additional obligations of a Significant Data Fiduciary (Sec 10)", "max": "₹150 crore"},
  {"breach": "Duties of a Data Principal (Sec 15)", "max": "₹10,000"},
  {"breach": "Breach of a voluntary undertaking (Sec 32)", "max": "Up to the amount for the original breach"},
  {"breach": "Any other provision of the Act or Rules", "max": "₹50 crore"}
 ],
 "status": "Commencement: Board provisions from 13 Nov 2025; most obligations and the penalty provisions (Sec 27, 33) from 18 months later.",
 "src": S["dpdp"], "src2": S["dpdp_commence"]
}

procedure = [
 {"step": "1", "title": "Report fast: 1930 and cybercrime.gov.in", "text": "Call the National Cyber Crime Helpline 1930 as soon as money is lost, so the transaction can be flagged and frozen. File a complaint on the National Cyber Crime Reporting Portal (cybercrime.gov.in), which routes it to the state police.", "src": S["ncrp"]},
 {"step": "2", "title": "FIR and investigation", "text": "For cognizable offences (3 years and above under Sec 77B), the police must register an FIR under BNSS Section 173, which allows e-FIRs. IT Act offences are investigated by an officer not below the rank of Inspector (Sec 78).", "src": S["itact_pdf"]},
 {"step": "3", "title": "Compensation: Adjudicating Officer (Sec 46)", "text": "For Sec 43, 43A and other contraventions, file before the Adjudicating Officer: an officer not below Director rank in the Government of India, or equivalent in the state (usually the state IT Secretary). Claims up to ₹5 crore; above that, the competent civil court.", "src": S["itact_pdf"], "verify": "Check your state's notification for who the Adjudicating Officer is and the current filing format."},
 {"step": "4", "title": "Appeal: TDSAT (Sec 57)", "text": "Appeal from the Adjudicating Officer or Controller lies to the Appellate Tribunal within 45 days. Since 26 May 2017 that is TDSAT, after the Cyber Appellate Tribunal was merged into it by the Finance Act, 2017.", "src": S["tdsat"]},
 {"step": "5", "title": "High Court (Sec 62)", "text": "Appeal from TDSAT to the High Court within 60 days, on any question of fact or law. The High Court can allow a further 60 days for sufficient cause.", "src": S["itact_pdf"], "verify": "Confirm the appeal forum and limitation on the current text after the Finance Act, 2017 changes."},
 {"step": "6", "title": "Data breaches: CERT-In and the DPDP Board", "text": "Organisations must report listed incidents to CERT-In within 6 hours (2022 Directions). Under the DPDP regime, personal data breaches are also notified to the Board and affected people once those duties commence.", "src": S["certin"]}
]

cases = [
 {"name": "Shreya Singhal v. Union of India", "year": "2015", "court": "Supreme Court", "cite": "(2015) 5 SCC 1", "held": "Section 66A unconstitutional; 69A blocking upheld; Section 79 read down to court or government notice.", "src": S["shreya"]},
 {"name": "PUCL v. Union of India", "year": "2022", "court": "Supreme Court", "cite": "Order of 12 Oct 2022", "held": "No prosecution under struck-down Section 66A; police told not to register 66A cases; pending 66A charges deleted.", "src": S["pucl"]},
 {"name": "Justice K.S. Puttaswamy v. Union of India", "year": "2017", "court": "Supreme Court (9 judges)", "cite": "2017 INSC 801", "held": "Privacy is a fundamental right; restrictions need legality, legitimate aim and proportionality.", "src": S["puttaswamy"]},
 {"name": "Anvar P.V. v. P.K. Basheer", "year": "2014", "court": "Supreme Court", "cite": "(2014) 10 SCC 473", "held": "Secondary electronic evidence needs a Section 65B certificate; oral evidence cannot replace it.", "src": S["anvar"]},
 {"name": "Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal", "year": "2020", "court": "Supreme Court (3 judges)", "cite": "2020 INSC 453", "held": "65B(4) certificate is a condition precedent unless the original device is produced; Shafhi Mohammad overruled.", "src": S["arjun"]},
 {"name": "Anuradha Bhasin v. Union of India", "year": "2020", "court": "Supreme Court", "cite": "2020 INSC 31", "held": "Speech and trade over the internet are protected under Article 19; shutdown orders must be published, proportionate and reviewed.", "src": S["bhasin"]},
 {"name": "Sharat Babu Digumarti v. Govt of NCT of Delhi", "year": "2016", "court": "Supreme Court", "cite": "Judgment of 14 Dec 2016", "held": "For electronic records the IT Act is a special law that overrides IPC 292 on obscenity.", "src": S["sharat"]},
 {"name": "Just Rights for Children Alliance v. S. Harish", "year": "2024", "court": "Supreme Court", "cite": "2024 INSC 716", "held": "Viewing, storing or possessing child sexual abuse material is punishable under POCSO Sec 15 and IT Act 67B; use the term CSEAM.", "src": S["justrights"]},
 {"name": "Kunal Kamra v. Union of India", "year": "2024", "court": "Bombay High Court", "cite": "WP (L) No. 9792 of 2023, decided 26 Sep 2024", "held": "2023 amendment to IT Rules 3(1)(b)(v) creating a government Fact Check Unit struck down as violating Articles 14, 19(1)(a) and 19(1)(g). The Union of India's appeal is pending in the Supreme Court (notice issued 10 Mar 2026).", "src": S["kamra"]}
]

downloads = [
 {"title": "Cyber Law PG Diploma cheat sheet", "desc": "IT Act sections, BNS map, DPDP penalties, procedure and leading cases on a few printable pages.", "file": "assets/pdf/cyberlaw-pg-cheatsheet.pdf",
  "claude": {"file": "assets/pdf/cyberlaw-pg-cheatsheet-claude.pdf", "dark": "assets/pdf/cyberlaw-pg-cheatsheet-claude-dark.pdf"}},
 {"title": "CyberPrompts sheet", "desc": "The best prompts from the CyberPrompts page, formatted for print.", "file": "assets/pdf/cyberprompts-sheet.pdf",
  "claude": {"file": "assets/pdf/cyberprompts-sheet-claude.pdf", "dark": "assets/pdf/cyberprompts-sheet-claude-dark.pdf"}}
]

DATA = {"meta": {"updated": "2026-11-01", "disclaimer": hero["disclaimer"], "note": "Each item links to its source. Items tagged 'verify' need a fresh check before use in court."},
        "hero": hero, "timeline": timeline, "itact": itact, "bns": bns, "bns_note": bns_note, "dpdp": dpdp,
        "procedure": procedure, "cases": cases, "downloads": downloads}
