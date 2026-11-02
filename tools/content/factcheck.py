# Mokit's fact-check (cwm-content/cyberlaw_verify.md, checked 1 Nov 2026 IST) wins over every other source.
# Applied by tools/build_pages_data.py to cyberlaw.json, the FAQ, the glossary and Nandi's timeline.
# Codes: C1-C15 = corrections, U1-U6 = uncertain items (shown with a "being verified" tag).
# Markers in strings: "(verify)" = our own open question, "(being verified)" = fact-check item still being confirmed.

V = {  # sources cited in cyberlaw_verify.md
 "itact_updated": "https://www.indiacode.nic.in/bitstream/123456789/13116/1/it_act_2000_updated.pdf",
 "jva": "https://egazette.gov.in/WriteReadData/2023/248047.pdf",
 "jva_commence": "https://egazette.gov.in/WriteReadData/2023/249809.pdf",
 "jva_om": "https://www.meity.gov.in/static/uploads/2024/03/MeitY-JVA-1.pdf",
 "bns": "https://egazette.gov.in/WriteReadData/2023/250883.pdf",
 "bnss": "https://egazette.gov.in/WriteReadData/2023/250884.pdf",
 "bsa": "https://egazette.gov.in/WriteReadData/2023/250882.pdf",
 "dpdp": "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
 "dpdp_rules": "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
 "dpdp_commence": "https://egazette.gov.in/WriteReadData/2025/267647.pdf",
 "itrules_consol": "https://www.meity.gov.in/static/uploads/2026/03/0b576f2071694b52e4cd6bb1b6dfab1e.pdf",
 "itrules_2026": "https://www.meity.gov.in/static/uploads/2026/02/f55fe52418b03f58b0669f6a8bc03b6d.pdf",
 "sgi_faq": "https://www.meity.gov.in/static/uploads/2026/02/49d4c4b42fc2d3dce00e0fdcf7ed1389.pdf",
 "pocso_ic": "https://www.indiacode.nic.in/indiacode/bitstream/123456789/2079/1/AA2012-32.pdf",
 "pocso_2019": "https://www.wcd.gov.in/documents/uploaded/1709101352.pdf",
 "certin": "https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf",
 "certin_ext": "https://www.cert-in.org.in/PDF/CERT-In_directions_extension_MSMEs_and_validation_27.06.2022.pdf",
 "rbios21": "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12192",
 "rbios26_pr": "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=62052",
 "rbios26_faq": "https://rbi.org.in/SCRIPTS/FAQDisplay.aspx?Id=153",
 "rbi2017": "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11040&Mode=0",
 "rbc2025": "https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=13140",
 "cms": "https://cms.rbi.org.in/",
 "anvar": "https://indiankanoon.org/doc/187283766/",
 "kamra_sc": "https://www.livelaw.in/pdf_upload/2026/03/11/6088020242026-03-10-660964.pdf",
}
def S(label, key): return {"label": label, "url": V[key]}

U = {
 "U1": "DPDP 18-month date: 13 or 14 May 2027 depending on the day count (gazette dated 13 Nov 2025, e-signed 14 Nov). A proposed cut to 12 months has not been notified.",
 "U2": "POCSO s.11 wording taken from a non-government mirror (India Code was unreachable); the 2019 amendment's start date (16 Aug 2019) was seen only on the mirror.",
 "U3": "s.77A(2) still cites CrPC ss.265B/265C. The CrPC is repealed; reading it as BNSS Ch. XXIII ss.289-300 (s.290 application, s.291 guidelines) is an interpretation (General Clauses Act s.8). No amending notification found.",
 "U4": "s.77B is silent on offences above 3 years; treating them as non-bailable via BNSS First Schedule Part II is an interpretation.",
 "U5": "RB-IOS 2021 limits (₹20 lakh + ₹1 lakh, 1 year) confirmed only from a non-government copy of the RBI FAQ. Historical: superseded from 1 Jul 2026.",
 "U6": "RBI Responsible Business Conduct Directions 2025: title and date confirmed on RBI's page; clause text read from a non-government mirror because RBI PDFs are bot-blocked.",
 "U4b": "s.77B covers only offences of 3 years and above; treating this below 3 years offence as non-cognizable and bailable under BNSS First Schedule Part II is an interpretation.",
 "ITR26": "2026 IT Rules timelines (G.S.R. 120(E)): fact-check reports them verified against MeitY's text; shown as being verified until a second check.",
 "IOS26": "RB-IOS 2026 figures (₹30 lakh + ₹3 lakh, 90 days): from RBI's press release and FAQ; shown as being verified until a second check.",
}

# ---------------- cyberlaw.json (built-in data) ----------------
def apply_law(d):
    it = {r["sec"]: r for r in d["itact"]}
    # C1, C2: ss.72 and 72A are civil penalties since 30 Nov 2023 (JVA Sch. entry 32(J), 32(K))
    it["72"].update(punishment="Penalty up to ₹5 lakh (Jan Vishwas Act 2023, entry 32(J), from 30 Nov 2023). Before that: up to 2 years, or fine up to ₹1 lakh, or both.",
                    bail="Not an offence since 30 Nov 2023", src=V["jva"], src_label="Jan Vishwas Act", src2=V["jva_commence"], src2_label="In force 30 Nov 2023")
    it["72A"].update(title="Penalty for disclosure of information in breach of lawful contract",
                     punishment="Penalty up to ₹25 lakh (Jan Vishwas Act 2023, entry 32(K), from 30 Nov 2023). Before that: up to 3 years, or fine up to ₹5 lakh, or both.",
                     bail="Not an offence since 30 Nov 2023", src=V["jva"], src_label="Jan Vishwas Act", src2=V["jva_commence"], src2_label="In force 30 Nov 2023")
    # C3: 66A struck down and formally omitted
    it["66A"].update(punishment="Struck down in Shreya Singhal (24 Mar 2015) and formally omitted by the Jan Vishwas Act 2023 (entry 32(E)) from 30 Nov 2023. No one can be prosecuted (PUCL, 2022).",
                     src2=V["jva"], src2_label="Jan Vishwas Act")
    # C9: s.43A still in force until DPDP s.44(2) commences
    it["43A"].update(punishment="Damages by way of compensation. Still in force: DPDP Act s.44(2), which omits it, starts 18 months after 13 Nov 2025 (around 13 May 2027). Until then the SPDI Rules 2011 also apply.",
                     pending=U["U1"], src=V["itact_updated"], src2=V["dpdp_commence"], src2_label="DPDP commencement")
    # U3, U4
    it["77A"].pop("verify", None); it["77A"]["pending"] = U["U3"]
    it["77B"]["pending"] = U["U4"]; it["77B"]["src2"] = V["itact_updated"]; it["77B"]["src2_label"] = "Bare act"
    for r in d["itact"]:
        if r["bail"].startswith("Non-bailable") or "Repeat: non-bailable" in r["bail"]:
            r["bail_pending"] = U["U4"]
    # 66E: Mokit: compoundable unless the victim is a woman or child (77A proviso) - interpretation
    it["66E"].update(compound="Yes, unless the offence is against a woman or a child (Sec 77A)", verify="Compoundability under 77A is an interpretation; check the victim and facts.")
    # C4: other Jan Vishwas changes (w.e.f. 30 Nov 2023)
    jva = dict(src=V["jva"], src_label="Jan Vishwas Act", src2=V["jva_commence"], src2_label="In force 30 Nov 2023")
    new = [
     {"sec": "33(2), 44, 45", "title": "Surrendering a licence, failing to furnish information, residuary penalty", "kind": "civil",
      "punishment": "Sec 33(2): penalty up to ₹5 lakh (was 6 months or ₹10,000). Sec 44: ₹15 lakh / ₹50,000 / ₹1 lakh (was ₹1.5 lakh / ₹5,000 / ₹10,000). Sec 45: penalty up to ₹1 lakh plus compensation up to ₹10 lakh (intermediary, company or body corporate) or ₹1 lakh (any other person); now also covers directions or orders.",
      "bail": "Not an offence", "compound": "n/a", **jva},
     {"sec": "67C(2)", "title": "Intermediary failing to preserve and retain information", "kind": "civil",
      "punishment": "Penalty up to ₹25 lakh (was up to 3 years and fine). Jan Vishwas entry 32(F).", "bail": "Not an offence since 30 Nov 2023", "compound": "n/a", **jva},
     {"sec": "68(2)", "title": "Not complying with an order of the Controller", "kind": "civil",
      "punishment": "Penalty up to ₹25 lakh (was up to 2 years, or ₹1 lakh, or both). Jan Vishwas entry 32(G).", "bail": "Not an offence since 30 Nov 2023", "compound": "n/a", **jva},
     {"sec": "69B(4)", "title": "Failing to assist traffic-data monitoring", "kind": "offence",
      "punishment": "Up to 1 year, or fine up to ₹1 crore, or both (was up to 3 years and fine). Jan Vishwas entry 32(H).", "bail": "Non-cognizable, bailable (below 3 years; BNSS First Schedule Part II)",
      "compound": "Yes (Sec 77A)", "pending": U["U4b"], **jva},
     {"sec": "70B(7)", "title": "Not complying with CERT-In directions", "kind": "offence",
      "punishment": "Up to 1 year, or fine up to ₹1 crore (was ₹1 lakh), or both. Jan Vishwas entry 32(I).", "bail": "Non-cognizable, bailable (below 3 years; BNSS First Schedule Part II)",
      "compound": "Yes (Sec 77A)", "pending": U["U4b"], **jva},
    ]
    order = ["43", "43A", "33(2), 44, 45", "65", "66", "66A", "66B", "66C", "66D", "66E", "66F", "67", "67A", "67B", "67C(2)", "68(2)", "69", "69A", "69B(4)",
             "70", "70B(7)", "72", "72A", "77A", "77B", "79", "84B", "84C"]
    rows = {r["sec"]: r for r in d["itact"] + new}
    d["itact"] = [rows[k] for k in order if k in rows]

    # C13: BNS punishments (higher than IPC)
    pun = {
     "Cheating (online fraud, UPI and investment scams)": "318(2): up to 3 years (IPC 417: 1 year). 318(3): up to 5 years. 318(4): up to 7 years and fine (as IPC 420)",
     "Cheating by personation (fake profiles, fake officials)": "319(2): up to 5 years (IPC 419: 3 years)",
     "Extortion (sextortion, 'digital arrest' demands)": "308(2): up to 7 years (IPC 384: 3 years)",
     "Defamation": "356(2): up to 2 years, or fine, or both, or community service (new)",
     "Criminal intimidation, incl. anonymous communication": "351(2): up to 2 years. 351(3): up to 7 years. 351(4): up to 2 years in addition (as IPC 507)",
     "Stalking (includes monitoring a woman's internet or email use)": "Up to 3 years (first), up to 5 years (repeat)",
    }
    for r in d["bns"]:
        if r["topic"] in pun: r["punishment"] = pun[r["topic"]]; r["src2"] = V["bns"]
    d["bns"].insert(2, {"topic": "Personating a public servant (fake police, 'digital arrest' calls)", "bns": "204", "ipc": "170",
                        "punishment": "6 months to 3 years and fine", "src": d["bns"][0]["src"], "src2": V["bns"]})
    d["bns_note"] = ("BNS punishments are often higher than the old IPC ones: simple cheating 3 years (was 1), personation 5 (was 3), extortion 7 (was 3), and defamation adds community service. "
                     + d["bns_note"])

    # C9 + U1: DPDP phases
    d["dpdp"]["status"] = ("Phased commencement (G.S.R. 843(E), 13 Nov 2025): the Board provisions are in force; consent managers from about 13 Nov 2026; "
                           "duties of Data Fiduciaries, grievance and complaints (ss.13, 27), appeals (s.29), these penalties (s.33 and Schedule) and the omission of IT Act s.43A (s.44(2)) "
                           "only from 18 months, around 13 May 2027 (being verified). Until then IT Act s.43A and the SPDI Rules 2011 still apply.")
    d["dpdp"]["src"] = V["dpdp"]; d["dpdp"]["src2"] = V["dpdp_commence"]

    # procedure: s.46 limit verified; TDSAT then HC verified (sec 5); add takedown step with 2026 timelines (C5-C8)
    p = {s["step"]: s for s in d["procedure"]}
    p["3"]["text"] = p["3"]["text"].replace("above that, the competent civil court.", "above that, the competent court (Sec 46(1A)).")
    p["2"]["text"] = ("For cognizable offences (3 years and above under Sec 77B), the police must register an FIR under BNSS Section 173, which allows e-FIRs. "
                      "For offences punishable with 3 years or more but less than 7 years, the officer may, with prior permission of an officer not below the rank of DSP, "
                      "first hold a preliminary enquiry within 14 days (BNSS 173(3)). IT Act offences are investigated by an officer not below the rank of Inspector (Sec 78).")
    p["2"]["src"] = V["bnss"]; p["2"]["more"] = [S("IT Act s.77B and s.78 (India Code)", "itact_updated")]
    p["5"].pop("verify", None)  # Mokit s.5: TDSAT (s.57), then the High Court (s.62) verified
    p["6"]["text"] = ("Organisations must report listed incidents to CERT-In within 6 hours (2022 Directions). Under the DPDP Act, personal data breaches must also be notified to the Board "
                      "and affected people, but that duty starts only around 13 May 2027 (being verified).")
    p["6"]["text"] = p["6"]["text"].replace(" (being verified)", ""); p["6"]["pending"] = U["U1"]
    d["procedure"].append({"step": "7", "title": "Get content taken down: platform timelines (IT Rules 2026)",
        "text": ("Complain to the platform's grievance officer: it must acknowledge within 24 hours and resolve within 7 days. Intimate or morphed images must be removed within 2 hours "
                 "of a complaint. On a court order or a reasoned notice from a Joint Secretary-rank officer (DIG for police), content must go within 3 hours. Other removal requests: 36 hours. "
                 "If the platform does not act, appeal to the Grievance Appellate Committee or go to court."),
        "pending": U["ITR26"], "src": V["itrules_2026"],
        "more": [S("IT Rules consolidated (MeitY)", "itrules_consol"), S("SGI FAQ (MeitY)", "sgi_faq")]})

    # built-in timeline fallback: same corrections
    for t in d["timeline"]:
        if t["date"] == "11 Apr 2011":
            t["text"] += " Still in force until DPDP Act s.44(2) commences (around 13 May 2027)."
        if t["date"] == "13 Nov 2025":
            t["pending"] = U["U1"]
        if t["date"] == "30 Nov 2023":
            t["text"] = ("Section 66A formally omitted. Sections 72 and 72A turned from offences into penalties (up to ₹5 lakh and ₹25 lakh). "
                         "Penalties under ss.33(2), 44, 45, 67C, 68, 69B and 70B revised.")
    d["timeline"] += TL_ADD_BUILTIN
    d["meta"]["factcheck"] = "Facts checked against primary texts on 1 Nov 2026 (IST). Items tagged 'being verified' are still being confirmed."
    return d

TL_ADD_BUILTIN = [
 {"date": "22 Oct 2025", "title": "IT Rules: who can send takedown notices", "text": "G.S.R. 775(E), in force 15 Nov 2025: 'actual knowledge' under rule 3(1)(d) arises only from a court order or a reasoned intimation from a Joint Secretary-rank officer (DIG for police).", "src": V["itrules_consol"]},
 {"date": "10 Feb 2026", "title": "IT Rules amendment on synthetic media", "text": "G.S.R. 120(E), in force 20 Feb 2026: defines synthetically generated information, adds labelling duties and cuts timelines: 2 hours for intimate or morphed images, 3 hours on orders, 36 hours for other removal requests, 7 days for grievances.", "src": V["itrules_2026"], "pending": U["ITR26"]},
 {"date": "1 Jul 2026", "title": "RBI Integrated Ombudsman Scheme, 2026", "text": "Replaces the 2021 scheme. Complain within 90 days at cms.rbi.org.in; awards up to ₹30 lakh + ₹3 lakh. Complaints received before 1 Jul 2026 stay under the 2021 scheme.", "src": V["rbios26_pr"], "pending": U["IOS26"]},
]

# ---------------- Nandi's history timeline (cyberlaw_timeline.json) ----------------
def apply_timeline(tl):
    for t in tl:
        t.setdefault("corrections", [])
        title = t["title"]
        def fix(field, new, code):
            t[field] = new; t["corrections"].append(code)
        if title.startswith("IT (Amendment) Act 2008"):
            fix("what_changed", t["what_changed"].replace("data protection duties in section 43A and the intermediary safe harbour in section 79.",
                "data protection duties in section 43A, and substituted section 79 with the present intermediary safe harbour."), "s.79 substituted, not added")
            t["more"] = [{"label": "IT Act 2000 as first enacted, with the original s.79 (MeitY)", "url": "https://www.meity.gov.in/static/uploads/2024/03/ITbill_2000.pdf"}]
        if title.startswith("SPDI Rules 2011"):
            fix("why_it_matters_for_advocates", "They remain the data protection yardstick for Section 43A compensation claims until DPDP Act s.44(2) omits Section 43A, around 13 May 2027.", "C9")
            t["pending"] = U["U1"]
        if title.startswith("Shreya Singhal"):
            fix("what_changed", t["what_changed"] + " The Jan Vishwas Act 2023 later omitted section 66A from the statute book with effect from 30 November 2023.", "C3")
        if title.startswith("CERT-In Directions"):
            fix("what_changed", t["what_changed"].replace(" (check the current text for exact timelines)", "")
                + " They took effect after 60 days (27 June 2022), and the MSME and validation parts were extended to 25 September 2022.", "key dates")
            t["more"] = [S("Extension notice", "certin_ext")]
        if title.startswith("IT Rules 2021 notified"):
            fix("why_it_matters_for_advocates", "These rules, as amended in 2022, 2023, 2025 and 2026, are the current baseline for takedown requests, grievance escalation and platform compliance work.", "C5-C8")
            t["more"] = [S("Consolidated text (MeitY, as on 10 Feb 2026)", "itrules_consol")]
        if title.startswith("DPDP Act 2023"):
            fix("what_changed", t["what_changed"].replace("once the relevant provisions are in force", "once s.44(2) commences, 18 months after 13 November 2025 (around 13 May 2027)")
                + " Until then IT Act section 43A and the SPDI Rules 2011 stay in force.", "C9")
            t["source_url"] = V["dpdp"]; t["pending"] = U["U1"]
        if title.startswith("Kunal Kamra"):
            fix("what_changed", t["what_changed"].replace("The Union's appeal is reported to be pending before the Supreme Court, so check its current status.",
                "The Union of India's appeal is pending in the Supreme Court: notice was issued on 10 March 2026 with no interim stay."), "SC order 10 Mar 2026")
            t["verify"] = False; t["more"] = [{"label": "SC record of proceedings, 10 Mar 2026", "url": V["kamra_sc"]}]
        if title.startswith("DPDP Rules 2025"):
            fix("what_changed", "The Digital Personal Data Protection Rules, 2025 were notified as G.S.R. 846(E) dated 13 November 2025, with the Act's commencement notification G.S.R. 843(E). "
                "Rules 1, 2 and 17 to 21 applied at once; rule 4 (consent managers) after one year (around 13 November 2026); rules 3, 5 to 16, 22 and 23 "
                "after 18 months (around 13 May 2027).", "C9")
            t["pending"] = U["U1"]; t["more"] = [S("Commencement notification", "dpdp_commence")]
        if title.startswith("IT Rules amendment 2026"):
            fix("what_changed", "The IT Rules amendment notified as G.S.R. 120(E) on 10 February 2026, in force from 20 February 2026, defines synthetically generated information such as deepfakes "
                "and adds labelling, metadata and provenance duties for intermediaries. It also cuts timelines: intimate or morphed images within 2 hours, court or government orders within "
                "3 hours, other removal requests within 36 hours, and grievances resolved within 7 days (acknowledgement still 24 hours).", "C5-C8")
            t["pending"] = U["ITR26"]; t["more"] = [S("SGI FAQ (MeitY)", "sgi_faq")]
        if not t["corrections"]: del t["corrections"]
    add = [
     {"year": 2014, "date": "2014-09-18", "title": "Anvar P V v P K Basheer decided", "what_changed": "The Supreme Court held that a section 65B certificate is mandatory for secondary electronic evidence.",
      "why_it_matters_for_advocates": "It is the starting point for every objection to an uncertified electronic record, now under BSA section 63.", "source_url": V["anvar"], "verify": False, "added_by": "fact-check"},
     {"year": 2023, "date": "2023-11-30", "title": "Jan Vishwas Act changes to the IT Act take effect", "what_changed": "The Jan Vishwas (Amendment of Provisions) Act, 2023 (published 11 August 2023) came into force for the IT Act on 30 November 2023 (S.O. 4745(E)). Sections 72 and 72A became civil penalties (up to ₹5 lakh and ₹25 lakh), section 66A was formally omitted, and penalties under sections 33(2), 44, 45, 67C, 68, 69B and 70B were revised.",
      "why_it_matters_for_advocates": "A breach of confidentiality under section 72 or 72A after 30 November 2023 is a penalty matter, not a criminal charge.", "source_url": V["jva_commence"], "verify": False, "added_by": "fact-check",
      "more": [S("Jan Vishwas Act (Gazette)", "jva")]},
     {"year": 2024, "date": "2024-02-23", "title": "Commencement notifications for BNS, BNSS and BSA", "what_changed": "Notifications S.O. 850(E), 848(E) and 849(E) dated 23 February 2024 brought the three codes into force from 1 July 2024, except BNS section 106(2).",
      "why_it_matters_for_advocates": "Cite the commencement notification when the date of offence decides IPC or BNS.", "source_url": "https://egazette.gov.in/WriteReadData/2024/252353.pdf", "verify": False, "added_by": "fact-check"},
     {"year": 2025, "date": "2025-10-22", "title": "IT Rules amendment on takedown notices", "what_changed": "G.S.R. 775(E), in force 15 November 2025, says an intermediary gets 'actual knowledge' under rule 3(1)(d) only through a court order or a reasoned intimation from an officer of Joint Secretary rank, or DIG rank for police.",
      "why_it_matters_for_advocates": "A takedown demand from a junior officer may not trigger the platform's duty; check who signed it.", "source_url": V["itrules_consol"], "verify": False, "added_by": "fact-check"},
     {"year": 2025, "date": "2025-11-28", "title": "RBI Responsible Business Conduct Directions replace the 2017 liability circular", "what_changed": "The RBI (Commercial Banks - Responsible Business Conduct) Directions, 2025 (RBI/DOR/2025-26/170) carried the July 2017 customer liability rules into Ch. IV, Section D, paras 67 to 72, and the 2017 circular was withdrawn. The substance is unchanged: zero liability if reported within 3 working days, capped liability for 4 to 7 days, shadow credit within 10 working days.",
      "why_it_matters_for_advocates": "Cite the 2025 Directions, not the withdrawn 2017 circular, in bank fraud notices.", "source_url": V["rbc2025"], "verify": False, "added_by": "fact-check", "pending": U["U6"]},
     {"year": 2026, "date": "2026-07-01", "title": "RBI Integrated Ombudsman Scheme, 2026 in force", "what_changed": "RB-IOS 2026, announced on 16 January 2026, replaced the 2021 scheme from 1 July 2026. Complaints must be filed within 90 days, and awards can go up to ₹30 lakh + ₹3 lakh (the 2021 limits were ₹20 lakh + ₹1 lakh with one year to file). Complaints received before 1 July 2026 stay under the 2021 scheme.",
      "why_it_matters_for_advocates": "The filing window for bank and payment complaints is now 90 days, so escalate quickly.", "source_url": V["rbios26_pr"], "verify": False, "added_by": "fact-check",
      "pending": U["IOS26"] + " " + U["U5"], "more": [S("RB-IOS 2026 FAQ", "rbios26_faq")]},
    ]
    tl = tl + add
    tl.sort(key=lambda t: t["date"])
    return tl

# ---------------- FAQ ----------------
def apply_faq(f):
    def q(n): return f[n - 1]
    # FAQ2 (C12, U6)
    x = q(2)
    x["a_en"] = x["a_en"].replace("Under the RBI's July 2017 customer liability circular, how quickly you report can affect how much of the loss you bear; the reporting windows in that circular should be checked against the current RBI text (verify).",
        "Under the RBI's customer liability rules (first issued in July 2017 and now in the RBI Responsible Business Conduct Directions, 2025, paras 67 to 72), you bear zero loss for a third-party fraud reported within 3 working days; reporting within 4 to 7 working days caps your loss at ₹5,000, ₹10,000 or ₹25,000 depending on the account; after that the bank's Board-approved policy applies (being verified).")
    x["a_hinglish"] += " RBI rules ke hisaab se 3 working days ke andar report kiya toh third-party fraud mein aapki liability zero ho sakti hai."
    x["refs"] = ["RBI (Commercial Banks - Responsible Business Conduct) Directions 2025, paras 67-72 (carries over the July 2017 circular) (being verified)", "IT Act s.66D", "BNS s.318 (old IPC 420)"]
    x["sources"] = [S("RBI master direction page", "rbc2025"), S("2017 circular (withdrawn)", "rbi2017")]
    # FAQ3: s.61 verified
    x = q(3); x["refs"] = ["BSA 2023 s.63 (old Evidence Act s.65B)", "BSA 2023 s.61", "BSA 2023 Schedule (certificate)"]; x["sources"] = [S("BSA (Gazette)", "bsa")]
    # FAQ4: s.46 verified
    x = q(4)
    x["a_en"] = x["a_en"].replace("Claims under Section 43 are usually decided by an adjudicating officer (verify), so check the process with a lawyer.",
        "Claims under Section 43 of up to ₹5 crore are decided by the adjudicating officer under Section 46; larger claims go to the competent court. Check the process with a lawyer.")
    x["refs"] = ["IT Act s.43", "IT Act s.66", "IT Act s.46"]; x["sources"] = [S("IT Act (India Code)", "itact_updated")]
    # FAQ5: 66A also omitted
    x = q(5)
    x["a_en"] = x["a_en"].replace("was struck down by the Supreme Court in Shreya Singhal (2015) and should not be applied.",
        "was struck down by the Supreme Court in Shreya Singhal (2015) and formally omitted by the Jan Vishwas Act from 30 November 2023, so it cannot be applied.")
    x["refs"] = [r if not r.startswith("IT Act s.66A") else "IT Act s.66A (struck down 2015; omitted 30 Nov 2023)" for r in x["refs"]]
    x["sources"] = [S("BNSS (Gazette)", "bnss"), S("Jan Vishwas Act", "jva")]
    # FAQ6 (C9, C10, U1)
    x = q(6)
    x["a_en"] = ("Under the Digital Personal Data Protection Act 2023, you must first use the grievance redressal mechanism of the company (Data Fiduciary) or Consent Manager, which must reply "
                 "within a reasonable period not exceeding 90 days (DPDP Rules r.14(3)). Only then can you complain to the Data Protection Board of India, and the Board's orders can be appealed "
                 "to the Appellate Tribunal (TDSAT) within 60 days (s.29(2)). But these grievance, complaint, appeal and penalty provisions take effect only 18 months after 13 November 2025, "
                 "around 13 May 2027 (being verified). Until then, claim compensation under IT Act Section 43A before the adjudicating officer (Section 46) or in a civil court; the SPDI Rules "
                 "2011 still apply. For financial loss or a crime, also report to 1930 and cybercrime.gov.in.")
    x["a_hinglish"] = ("DPDP Act mein pehle company ke grievance officer ko complaint karni hoti hai (jawab 90 din ke andar), phir Data Protection Board, aur Board ke order ke khilaaf 60 din mein "
                       "TDSAT appeal. Lekin yeh provisions lagbhag 13 May 2027 se lagu honge. Tab tak IT Act Section 43A aur Section 46 (adjudicating officer) ya civil court ka raasta hai. "
                       "Fraud ya paisa gaya hai toh 1930 aur cybercrime.gov.in pe bhi report karo.")
    x["refs"] = ["DPDP Act 2023 s.13(3)", "DPDP Act 2023 s.27", "DPDP Act 2023 s.29(2)", "DPDP Rules 2025 r.14(3)", "IT Act s.43A, s.46", "DPDP commencement, G.S.R. 843(E) (being verified)"]
    x["sources"] = [S("DPDP Act", "dpdp"), S("DPDP Rules 2025", "dpdp_rules"), S("Commencement notification", "dpdp_commence")]
    # FAQ9 (C15 + 2026 timelines)
    x = q(9)
    x["a_en"] += (" Under the IT Rules as amended in 2026, the platform must acknowledge your complaint within 24 hours and resolve it within 7 days, and intimate or morphed images "
                  "must be taken down within 2 hours (being verified).")
    x["a_hinglish"] += " IT Rules 2026 ke hisaab se platform ko complaint 24 ghante mein acknowledge karke 7 din mein resolve karni hoti hai, aur intimate ya morphed photos 2 ghante mein hatani hoti hain."
    x["refs"] = ["BNS s.356 (old IPC 499/500)", "IT Rules 2021 r.3, as amended by G.S.R. 120(E), 2026 (being verified)"]
    x["sources"] = [S("G.S.R. 120(E), 2026", "itrules_2026"), S("IT Rules consolidated", "itrules_consol")]
    # FAQ10 (U2)
    x = q(10)
    x["refs"] = ["BNS s.78 (old IPC 354D)", "BNS s.351 (old IPC 503/506)", "IT Act s.67B", "POCSO Act 2012 s.11 (being verified)", "POCSO Act 2012 s.15 (as substituted in 2019)"]
    x["sources"] = [S("POCSO (India Code)", "pocso_ic"), S("POCSO Amendment 2019 (WCD)", "pocso_2019")]
    # FAQ11: three days verified
    x = q(11)
    x["a_en"] = x["a_en"].replace("Complaints received electronically may need to be signed by the complainant within a set period to be taken on record as an FIR (verify).",
        "Information given electronically must be signed by the complainant within three days to be taken on record as an FIR (BNSS s.173(1)(ii)).")
    x["sources"] = [S("BNSS (Gazette)", "bnss")]
    # FAQ12 (C14)
    x = q(12)
    x["a_en"] = x["a_en"].replace("For some offences in the middle punishment range, police may first conduct a preliminary enquiry with senior approval (verify).",
        "For offences punishable with 3 years or more but less than 7 years, police may first hold a preliminary enquiry, within 14 days, with permission from an officer of DSP rank.")
    x["a_en"] = x["a_en"].replace("Superintendent of Police or DCP", "Superintendent of Police")
    x["a_hinglish"] = x["a_hinglish"].replace("SP ya DCP", "Superintendent of Police (SP)")
    x["sources"] = [S("BNSS (Gazette)", "bnss")]
    # FAQ13 (C11, C12, U5, U6)
    x = q(13)
    x["a_en"] = ("Under the RBI's customer liability rules, first issued in the July 2017 circular and now carried into the RBI (Commercial Banks - Responsible Business Conduct) Directions, 2025 "
                 "(paras 67 to 72), you have zero liability where the bank was negligent, or where a third-party breach occurred and you reported it within 3 working days. Reporting within "
                 "4 to 7 working days caps your liability at ₹5,000, ₹10,000 or ₹25,000 depending on the account, and beyond 7 working days the bank's Board-approved policy applies (being verified). "
                 "If the loss happened because you shared credentials such as OTP or PIN, you may bear the loss until you report it. The bank must credit the amount to your account (shadow credit) "
                 "within 10 working days of your report and resolve the complaint within 90 days. If the bank does not reply within 30 days or you are not satisfied, complain at cms.rbi.org.in "
                 "under the Reserve Bank - Integrated Ombudsman Scheme, 2026 (in force 1 July 2026): file within 90 days; the Ombudsman can award up to ₹30 lakh + ₹3 lakh, and an appeal lies "
                 "within 30 days (being verified). Complaints received before 1 July 2026 stay under the 2021 scheme. A lawyer or consumer forum advisor can help.")
    x["a_hinglish"] = ("RBI rules (pehle 2017 circular, ab RBI Responsible Business Conduct Directions 2025) ke hisaab se, galti bank ki ho ya third-party fraud ho aur aapne 3 working days mein "
                       "report kiya, toh liability zero. 4 se 7 working days mein report kiya toh loss ₹5,000 se ₹25,000 tak capped. OTP ya PIN khud share kiya toh loss aapka ho sakta hai jab tak "
                       "report na karo. Bank ko 10 working days mein shadow credit dena hota hai. Bank 30 din mein jawab na de toh 90 din ke andar cms.rbi.org.in pe RBI Ombudsman (RB-IOS 2026) ko complaint karo.")
    x["refs"] = ["RBI (Commercial Banks - Responsible Business Conduct) Directions 2025, paras 67-72 (being verified)", "Reserve Bank - Integrated Ombudsman Scheme 2026, in force 1 Jul 2026 (being verified)",
                 "RB-IOS 2021 limits, historical (being verified)"]
    x["sources"] = [S("RBC Directions (RBI)", "rbc2025"), S("RB-IOS 2026 press release", "rbios26_pr"), S("RB-IOS 2026 FAQ", "rbios26_faq"), S("RBI complaint portal", "cms"),
                    S("RB-IOS 2021 scheme (RBI)", "rbios21")]
    # FAQ14: 2026 amendment cite
    x = q(14)
    x["refs"] = [r if not r.startswith("IT (Intermediary") else "IT Rules Amendment 2026, G.S.R. 120(E), in force 20 Feb 2026" for r in x["refs"]]
    x["sources"] = [S("G.S.R. 120(E), 2026", "itrules_2026"), S("SGI FAQ (MeitY)", "sgi_faq")]
    x = q(1); x["sources"] = [S("IT Act (India Code)", "itact_updated"), S("BNS (Gazette)", "bns")]
    x = q(15); x["sources"] = [S("BNS (Gazette)", "bns")]
    return f

# ---------------- Glossary ----------------
def apply_glossary(g):
    by = {x["term"]: x for x in g}
    def has(t): return t in by
    if has("e-FIR and Zero FIR"):
        x = by["e-FIR and Zero FIR"]
        x["meaning_en"] = x["meaning_en"].replace("once signed by the informant within the prescribed time (verify).", "once signed by the informant within three days.")
        x["sources"] = [S("BNSS (Gazette)", "bnss")]
    if has("Grievance officer"):
        x = by["Grievance officer"]
        x["meaning_en"] = x["meaning_en"].replace("within the timelines set in the rules.",
            "within the timelines set in the rules: for intermediaries, acknowledgement within 24 hours and resolution within 7 days under the 2026 amendment (being verified).")
        x["sources"] = [S("G.S.R. 120(E), 2026", "itrules_2026")]
    if has("Deepfake"):
        x = by["Deepfake"]; x["ref"] = "IT Rules Amendment 2026, G.S.R. 120(E), r.2(1)(wa) and r.3(3) (being verified)"
        x["sources"] = [S("G.S.R. 120(E), 2026", "itrules_2026"), S("SGI FAQ (MeitY)", "sgi_faq")]
    if has("Reasonable security practices"):
        x = by["Reasonable security practices"]
        x["meaning_en"] = x["meaning_en"].replace("is set to be omitted by the DPDP Act once that amendment takes effect.",
            "stays in force until DPDP Act s.44(2) omits it, around 13 May 2027 (being verified).")
        x["sources"] = [S("DPDP commencement", "dpdp_commence")]
    if has("Sensitive personal data or information"):
        x = by["Sensitive personal data or information"]
        x["meaning_en"] += " These rules still apply until DPDP Act s.44(2) commences (around 13 May 2027)."
    if has("Data Protection Board of India"):
        x = by["Data Protection Board of India"]
        x["meaning_en"] += " The Board was set up from 13 November 2025, but its complaint and penalty powers apply only from around 13 May 2027 (being verified)."
        x["sources"] = [S("DPDP commencement", "dpdp_commence")]
    if has("Personal data breach"):
        x = by["Personal data breach"]
        x["meaning_en"] = x["meaning_en"].replace("data fiduciaries must intimate such breaches to the Board and affected persons.",
            "data fiduciaries must intimate such breaches to the Board and affected persons once that duty starts, around 13 May 2027.")
    if has("Compoundable offence"):
        x = by["Compoundable offence"]
        x["meaning_en"] += " IT Act s.77A(2) still refers to old CrPC plea-bargaining sections; reading them as BNSS ss.289-300 is an interpretation (being verified)."
    if has("Cognizable offence"):
        x = by["Cognizable offence"]
        x["meaning_en"] += " Offences of exactly three years are also bailable; for offences above three years s.77B is silent on bail (being verified)."
    if has("IP address and log retention"):
        x = by["IP address and log retention"]
        x["meaning_en"] = x["meaning_en"].replace("CERT-In directions require covered entities to maintain ICT system logs for a set period (verify).",
            "CERT-In directions require covered entities to maintain logs of all ICT systems for a rolling 180 days, within India.")
        x["sources"] = [S("CERT-In Directions, 28 Apr 2022", "certin")]
    if has("Blocking order"):
        x = by["Blocking order"]; x["ref"] = x["ref"].replace(" Rules 2009 (verify)", " Rules 2009")
    if has("Deepfake"):
        by["Deepfake"]["ref"] = "IT Rules Amendment 2026, G.S.R. 120(E), r.2(1)(wa) and r.3(3)"
    return g
