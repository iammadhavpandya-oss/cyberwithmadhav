#!/usr/bin/env python3
"""Copy the feature page content from /workspace/cwm-content into data/ and write per page search indexes.
Run from the repo root after build_pages_data.py and before build_site.py:
  python3 tools/build_features.py [--content /workspace/cwm-content]
Idempotent. Missing source files are skipped with a message, so a page keeps its last committed data."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CONTENT = Path(sys.argv[sys.argv.index("--content") + 1]) if "--content" in sys.argv else Path("/workspace/cwm-content")


def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def clean(o):
    """No em or en dashes in anything the site shows."""
    if isinstance(o, str): return o.replace(" \u2014 ", ", ").replace("\u2014", ", ").replace("\u2013", "-")
    if isinstance(o, list): return [clean(x) for x in o]
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    return o


def write(name, obj, compact=False):
    p = DATA / name
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) if compact else json.dumps(obj, ensure_ascii=False, indent=1)
    s += "\n"
    if not p.exists() or p.read_text(encoding="utf-8") != s:
        p.write_text(s, encoding="utf-8"); print("wrote data/" + name)


def load(name):
    p = CONTENT / name
    if not p.exists():
        print("missing", name, "(kept the committed data)"); return None
    return clean(json.loads(p.read_text(encoding="utf-8")))


# ---------- Phase 3: Command Reference ----------
OS_LABEL = {"linux": "Linux", "windows": "Windows", "cisco_ios": "Cisco IOS", "cross_platform": "Cross platform"}
CAT_LABEL = {"network": "Network", "processes": "Processes", "files_perms": "Files and permissions", "users": "Users",
             "logs": "Logs", "cisco": "Cisco", "recon_own_network": "Recon (own network)"}
# Commands whose safety note must be shown prominently (steering: nmap and arp).
PROMINENT = {"nmap", "arp -a"}


def commands():
    d = load("cmdref.json")
    if d is None: return
    out, seen = [], set()
    for c in d["commands"]:
        cid = slug(c["os"] + "-" + c["cmd"])
        assert cid not in seen, cid; seen.add(cid)
        assert c["doc_url"].startswith("https://"), c["doc_url"]
        out.append({"id": cid, "cmd": c["cmd"], "os": c["os"], "cat": c["category"], "what": c["what_it_does"],
                    "example": c["example"], "output": c["example_output_hint"], "blue": c["blue_team_use"],
                    "safety": c["safety_note"], "doc": c["doc_url"], "prominent": c["cmd"] in PROMINENT})
    oses = [k for k in OS_LABEL if any(c["os"] == k for c in out)]
    cats = [k for k in CAT_LABEL if any(c["cat"] == k for c in out)]
    checked = sorted({u.get("checked", "") for u in d["meta"].get("url_checks", [])})
    write("commands.json", {"meta": {"updated": d["meta"].get("created", ""), "notes": d["meta"].get("notes", ""),
                                     "docs_checked": checked[-1] if checked else ""},
                            "os": [{"id": k, "name": OS_LABEL[k]} for k in oses],
                            "categories": [{"id": k, "name": CAT_LABEL[k]} for k in cats], "commands": out})
    idx = [{"k": "Command ref", "t": c["cmd"], "s": OS_LABEL[c["os"]] + " · " + CAT_LABEL[c["cat"]],
            "u": "commands.html#c-" + c["id"], "x": c["what"] + " " + c["example"]} for c in out]
    write("commands_index.json", idx, compact=True)
    print(f"commands: {len(out)} ({len(oses)} OS, {len(cats)} categories)")


def terminal():
    """Search entries for the Terminal Wargame (built by the wargame worker; read only here)."""
    p = DATA / "terminal_wargame.json"
    if not p.exists(): return
    d = json.loads(p.read_text(encoding="utf-8"))
    idx = [{"k": "Terminal", "t": f"Level {i}: {l['title']}", "s": "Terminal Wargame", "u": "terminal.html",
            "x": clean(f"{l.get('concept_taught', '')}. {' '.join(l.get('allowed_cmds', []))}")} for i, l in enumerate(d["levels"])]
    write("terminal_index.json", idx, compact=True)


def slow_urls():
    """URLs that failed at least once in the link recheck (/tmp/urlcheck.txt) but answered 200 on retry."""
    p = Path("/tmp/urlcheck.txt"); keep = DATA / "slow_urls.json"
    if p.exists():
        out = []
        for line in p.read_text().splitlines():
            try: r = json.loads(line)
            except ValueError: continue
            if any(c != "200" for c in r.get("codes", [])): out.append(r["url"])
        keep.write_text(json.dumps(sorted(out), indent=0) + "\n") if not keep.exists() or json.loads(keep.read_text()) != sorted(out) else None
    return set(json.loads(keep.read_text())) if keep.exists() else set()


def scams():
    src = load("scam_encyclopedia.json")
    if src is None: return
    slugs = {v: k for k, v in load("scam_slug_map.json").items()}
    slow = slow_urls()
    out = []
    for x in src:
        key = slugs.get(x["name"]) or slug(x["name"]).replace("-", "_")
        out.append({"id": key.replace("_", "-"), "slug": key, "name": x["name"], "hinglish": x["hinglish_name"],
                    "steps": x["how_it_works"], "flags": x["red_flags"], "todo": x["what_to_do_now"],
                    "law": x["applicable_law"], "source": x["source_url"], "verify": bool(x.get("verify")),
                    "slow": x["source_url"] in slow})
    write("scams.json", {"meta": {"count": len(out), "helpline": "1930", "portal": "https://cybercrime.gov.in"}, "scams": clean(out)})
    idx = [{"k": "Scam", "t": c["name"], "s": c["hinglish"], "u": f"scams.html#s-{c['id']}",
            "x": clean(" ".join(c["steps"] + c["flags"][:2]))} for c in out]
    write("scams_index.json", idx, compact=True)
    print(f"scams: {len(out)} ({sum(c['verify'] for c in out)} being verified, {sum(c['slow'] for c in out)} slow sources)")


def main():
    DATA.mkdir(exist_ok=True)
    commands()
    terminal()
    scams()


if __name__ == "__main__":
    main()
