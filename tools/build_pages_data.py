#!/usr/bin/env python3
"""Build data/prompts.json, data/cyberlaw.json and copy bot content for prompts.html / cyberlaw.html.
Idempotent. Run from repo root: python3 tools/build_pages_data.py [--content /workspace/cwm-content]"""
import json, re, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "content"))
import prompts_src, cyberlaw_src, factcheck, seo  # noqa: E402

CONTENT = Path(sys.argv[sys.argv.index("--content") + 1]) if "--content" in sys.argv else Path("/workspace/cwm-content")
DATA = ROOT / "data"
EM = "\u2014"

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def clean(o):
    if isinstance(o, str): return o.replace(EM, ", ").replace("\u2013", "-") if (EM in o or "\u2013" in o) else o
    if isinstance(o, list): return [clean(x) for x in o]
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    return o

def build_prompts():
    cats, prompts, seen = [], [], set()
    for cid, name, desc, items in prompts_src.CATS:
        cats.append({"id": cid, "name": name, "desc": desc})
        for t, use, prompt, tip, model in items:
            pid = f"{cid}-{slug(t)}"
            seen.add(t.lower()); prompts.append({"id": pid, "cat": cid, "title": t, "use": use, "prompt": prompt, "tip": tip, "model": model})
    extra = CONTENT / "prompts_extra.json"
    merged = 0
    if extra.exists():
        alias = {"career": "career", "soc basics": "soc"}
        descs = {"Content Creation": "Create clear, accurate cyber awareness content.", "Victim Help": "Help victims of online fraud and abuse take the right next steps.",
                 "Cyber Law Explainers": "Explain Indian cyber law in plain words. Not legal advice.", "Compliance": "Prepare for privacy and security compliance work.",
                 "Training": "Plan and run security awareness and team training."}
        for x in json.loads(extra.read_text()):
            if x["title"].lower() in seen: continue
            cname = x["category"].strip(); cid = alias.get(cname.lower(), slug(cname))
            if not any(c["id"] == cid for c in cats):
                cats.append({"id": cid, "name": cname, "desc": descs.get(cname, "")})
            seen.add(x["title"].lower()); merged += 1
            prompts.append({"id": f"{cid}-{slug(x['title'])}", "cat": cid, "title": x["title"], "use": x.get("use_case", ""),
                            "prompt": x["prompt"], "tip": x.get("pro_tip", ""), "model": x.get("best_model") or prompts_src.M_GEN, "source": "community"})
    # "Defensive Analysis" (used by Nandi's use-case cards) is an umbrella filter over the analysis categories.
    group = ["osint", "recon", "ir", "threatintel", "malware", "phishing", "cloud", "code"]
    cats.insert(0, {"id": "defensive-analysis", "name": "Defensive Analysis", "group": group,
                    "desc": "All defensive analysis prompts: OSINT on yourself or with consent, authorised scans, incident response, threat intel, malware, phishing, cloud and code review."})
    out = clean({"meta": {"updated": "2026-11-01", "banner": "Use only on systems and data you own or are authorised to test."}, "categories": cats, "prompts": prompts})
    (DATA / "prompts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    return len(cats), len(prompts), merged

KAMRA_SC = ("The Union of India's appeal (SLP (C) Diary No. 60880/2024) is pending in the Supreme Court: "
            "notice was issued on 10 March 2026 and no interim stay was granted.")
KAMRA_SC_SRC = "https://www.livelaw.in/pdf_upload/2026/03/11/6088020242026-03-10-660964.pdf"

def patch_cases(cases):
    """Parent steering: the Kamra card must say the SC appeal is pending (SC record of proceedings, 10 Mar 2026)."""
    for c in cases:
        if c.get("name", "").startswith("Kunal Kamra"):
            held = c.get("held", "")
            i = held.find("Supreme Court records show")
            if i != -1:
                held = held[:i].rstrip()
            c["held"] = (held + " " + KAMRA_SC).strip()
            c["status_src"] = KAMRA_SC_SRC
    return cases

def copy_usecases():
    src = CONTENT / "cyberprompts_usecases.json"
    if not src.exists():
        print("missing cyberprompts_usecases.json"); return
    cats = {c["name"].lower(): c["id"] for c in json.loads((DATA / "prompts.json").read_text())["categories"]}
    alias = {"soc basics": "soc", "career": "career"}
    d = clean(json.loads(src.read_text()))
    for u in d:
        n = u.get("which_prompt_category", "").strip().lower()
        u["cat_id"] = alias.get(n) or cats.get(n) or slug(n)
    (DATA / "cyberprompts_usecases.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    print(f"copied cyberprompts_usecases.json: {len(d)} items")

def copy_reporting():
    """Mokit's reporting guide: only the forums array, NCRP and the 1930 helpline first."""
    src = CONTENT / "cyberlaw_reporting_guide.json"
    if not src.exists():
        print("missing cyberlaw_reporting_guide.json (Where to File section hidden)")
        return
    forums = clean(json.loads(src.read_text())["forums"])
    keys = ("forum", "who_can_file", "when_to_use", "time_limit", "documents_needed", "official_url", "verify")
    for f in forums:
        assert all(k in f for k in keys), f.get("forum")
        assert f["official_url"].startswith("https://"), f["official_url"]
    rank = lambda f: 0 if "NCRP" in f["forum"] else 1 if "1930" in f["forum"] else 2
    forums.sort(key=rank)  # stable: the rest keep the guide's order
    (DATA / "cyberlaw_reporting.json").write_text(json.dumps(forums, ensure_ascii=False, indent=1) + "\n")
    print(f"copied cyberlaw_reporting.json: {len(forums)} forums ({sum(f['verify'] for f in forums)} flagged verify)")


def main():
    DATA.mkdir(exist_ok=True)
    print("prompts: categories=%d prompts=%d merged_extra=%d" % build_prompts())
    law = clean(factcheck.apply_law(json.loads(json.dumps(cyberlaw_src.DATA))))  # Mokit's fact-check wins
    for d in law["downloads"]:  # page shows "coming soon" for missing PDFs without a 404 request
        d["available"] = (ROOT / d["file"]).is_file()
        if d.get("claude"):  # PDF 2: Claude edition, Light plus an optional Dark file
            c = d["claude"]
            c["available"] = (ROOT / c["file"]).is_file()
            c["dark_available"] = bool(c.get("dark")) and (ROOT / c["dark"]).is_file()
    (DATA / "cyberlaw.json").write_text(json.dumps(law, ensure_ascii=False, indent=1) + "\n")
    print("cyberlaw.json written")
    copy_usecases()
    patch = {"cyberlaw_faq.json": factcheck.apply_faq, "cyberlaw_glossary.json": factcheck.apply_glossary,
             "cyberlaw_cases.json": patch_cases, "cyberlaw_timeline.json": factcheck.apply_timeline}
    copy_reporting()
    for name in ("cyberlaw_faq.json", "cyberlaw_glossary.json", "cyberlaw_cases.json", "cyberlaw_timeline.json"):
        src = CONTENT / name
        if src.exists():
            d = clean(json.loads(src.read_text()))
            d = clean(patch[name](d))
            (DATA / name).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
            print(f"copied {name}: {len(d)} items")
        else:
            print(f"missing {name} (page shows built-in fallback)")
    seo.apply(ROOT, CONTENT / "seo_pack.json")

if __name__ == "__main__": main()
