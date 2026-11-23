"""The Learn path: stages, live lessons and coming soon outlines.
Stage 3 follows the CCNA-aligned outline (Cisco CCNA 200-301 v1.1 exam topics), 14 lessons with Packet Tracer labs."""
from content.learn_s1a import lesson_computer, lesson_os
from content.learn_s1b import lesson_windows, lesson_network
from content.learn_s2 import lesson_linux_theory, lesson_linux_lab
from content.learn_s2b import lesson_bash, lesson_logging
from content.learn_ccna_a import lesson_ccna_1, lesson_ccna_2
from content.learn_ccna_b import lesson_ccna_3, lesson_ccna_4
from content.learn_ccna_c import lesson_ccna_5, lesson_ccna_6, lesson_ccna_7
from content.learn_ccna_d import lesson_ccna_8, lesson_ccna_9, lesson_ccna_10
from content.learn_ccna_e import lesson_ccna_11, lesson_ccna_12, lesson_ccna_13, lesson_ccna_14

LESSONS = [lesson_computer(), lesson_os(), lesson_windows(), lesson_network(), lesson_linux_theory(), lesson_linux_lab(), lesson_bash(), lesson_logging(),
           lesson_ccna_1(), lesson_ccna_2(), lesson_ccna_3(), lesson_ccna_4(), lesson_ccna_5(), lesson_ccna_6(), lesson_ccna_7(),
           lesson_ccna_8(), lesson_ccna_9(), lesson_ccna_10(), lesson_ccna_11(), lesson_ccna_12(), lesson_ccna_13(), lesson_ccna_14()]
BY_SLUG = {l["slug"]: l for l in LESSONS}

def soon(n, title, goals, tags=()):
    return dict(soon=True, n=n, title=title, goals=goals, tags=list(tags))

STAGES = [
  dict(n=1, id="stage-1", name="Foundations", hi_name="Neev (Foundations)", tag="start here",
       desc="How computers, operating systems, Windows and networks really work. Every later skill stands on this.",
       hi_desc="Computer, operating system, Windows aur network asal mein kaise kaam karte hain. Aage ki har skill isi pe khadi hai.",
       items=["learn-how-computers-work", "learn-operating-system-fundamentals", "learn-windows-for-security", "learn-networking-basics"]),
  dict(n=2, id="stage-2", name="Linux", hi_name="Linux", tag="theory, then labs",
       desc="Theory first, then the terminal. Understand the system, then drill it in a browser shell and on your own VM.",
       hi_desc="Pehle theory, phir terminal. System samjho, phir browser shell aur apne VM pe practice karo.",
       items=["learn-linux-fundamentals", "learn-linux-hands-on-lab",
              "learn-bash-scripting-for-security",
              "learn-linux-logging-auditing-hardening"]),
  dict(n=3, id="stage-3", name="Networking and CCNA", hi_name="Networking aur CCNA", tag="Packet Tracer labs",
       desc="Fourteen lessons mapped to the Cisco CCNA 200-301 v1.1 exam topics, each with a Cisco Packet Tracer lab and a defensive security angle.",
       hi_desc="Cisco CCNA 200-301 v1.1 ke topics pe 14 lessons, har ek mein Packet Tracer lab aur security angle.",
       items=[
         "learn-ccna-network-building-blocks",
         "learn-ccna-ip-addressing-subnetting",
         "learn-ccna-switching-secure-access",
         "learn-ccna-vlans-trunks",
         "learn-ccna-stp-etherchannel",
         "learn-ccna-inter-vlan-routing-hsrp",
         "learn-ccna-static-routing",
         "learn-ccna-ospf",
         "learn-ccna-access-control-lists",
         "learn-ccna-dhcp-dns-nat",
         "learn-ccna-network-operations",
         "learn-ccna-layer2-security-aaa",
         "learn-ccna-wireless-lans",
         "learn-ccna-network-automation"]),
  dict(n=4, id="stage-4", name="Security Fundamentals", hi_name="Security fundamentals", tag="core concepts",
       desc="The ideas every security role shares: risk, cryptography, identity and a little code.",
       hi_desc="Wo ideas jo har security role mein kaam aate hain: risk, cryptography, identity aur thoda code.",
       items=[soon("4.1", "CIA Triad, Threats, Vulnerabilities and Risk", ["Use the CIA triad to describe impact", "Tell threat, vulnerability, exploit and risk apart", "Do a simple risk assessment for a small office"]),
              soon("4.2", "Cryptography in Practice: Hashing, Encryption, TLS and PKI", ["Choose hashing, symmetric or asymmetric crypto for a job", "Read a certificate chain", "Explain what TLS protects and what it does not"], ["lab"]),
              soon("4.3", "Authentication, MFA and Passkeys", ["Compare passwords, OTPs, authenticator apps and passkeys", "Explain why SMS OTP is the weakest second factor", "Design a sensible login policy"]),
              soon("4.4", "Python for Security", ["Write scripts that parse logs and call APIs", "Build a small port checker for your own lab", "Handle files and errors safely"], ["lab"])]),
  dict(n=5, id="stage-5", name="Attack and Defence", hi_name="Attack aur defence", tag="home lab",
       desc="How real attacks work and how defenders catch them, practised only in your own lab and on legal training platforms.",
       hi_desc="Asli attacks kaise hote hain aur defenders kaise pakadte hain, sirf apne lab aur legal platforms pe.",
       items=[soon("5.1", "Web Security: HTTP in Depth, OWASP Top 10, Burp Suite", ["Explain the OWASP Top 10 categories with examples", "Intercept and modify requests in Burp in a legal lab", "Write a clear finding with impact and fix"], ["lab"]),
              soon("5.2", "Network Security: Nmap, Wireshark, Firewalls, IDS", ["Scan your own lab responsibly with Nmap", "Investigate traffic in Wireshark", "Write and test firewall rules"], ["lab"]),
              soon("5.3", "Blue Team: Logs, SIEM and Alert Triage", ["Collect Windows and Linux logs into a SIEM such as Wazuh", "Triage an alert end to end", "Write a short incident report"], ["lab"]),
              soon("5.4", "Active Directory Fundamentals", ["Explain domains, Kerberos and Group Policy", "Build a small AD lab", "Spot the common misconfigurations"], ["lab"]),
              soon("5.5", "Cloud Security Basics", ["Explain the shared responsibility model", "Find IAM and storage misconfigurations", "Turn on logging that catches them"])]),
  dict(n=6, id="stage-6", name="Specialise", hi_name="Specialise karo", tag="advanced",
       desc="Go deep in one direction: offence, detection, forensics or malware.",
       hi_desc="Ek direction mein gehraai: offence, detection, forensics ya malware.",
       items=[soon("6.1", "Penetration Testing Method and Reporting", ["Follow a scoped, authorised test from start to report", "Rate findings by risk", "Write a report a manager can act on"]),
              soon("6.2", "Active Directory Attacks and Defences", ["Explain Kerberoasting, delegation abuse and tiering", "Detect each technique in logs", "Harden a lab domain"], ["lab"]),
              soon("6.3", "Detection Engineering: Sigma, YARA, MITRE ATT&amp;CK", ["Map behaviour to ATT&amp;CK techniques", "Write and test Sigma and YARA rules", "Measure detection coverage"], ["lab"]),
              soon("6.4", "Digital Forensics and Incident Response", ["Capture and analyse memory and disk images", "Build a timeline", "Run an incident from detection to lessons learned"], ["lab"]),
              soon("6.5", "Malware Analysis Fundamentals", ["Set up an isolated analysis VM", "Do basic static and dynamic analysis", "Extract indicators of compromise safely"], ["lab"])]),
]

# Home page roadmap topics mapped to lessons. Keys are the exact topic strings in data/roadmap.json.
ROADMAP_LINKS = {
  "How computers work: CPU, RAM, storage, OS, processes": [("learn-how-computers-work.html", "Lesson 1.1"), ("learn-operating-system-fundamentals.html", "Lesson 1.2")],
  "Networking basics: OSI & TCP/IP, IP addressing, subnetting, DNS, DHCP, common ports": [("learn-networking-basics.html", "Lesson 1.4"), ("learn-ccna-ip-addressing-subnetting.html", "Lesson 3.2"), ("learn-ccna-dhcp-dns-nat.html", "Lesson 3.10"), ("learn.html#stage-3", "CCNA path")],
  "Linux command line: files, permissions, users, processes, package managers": [("learn-linux-fundamentals.html", "Lesson 2.1"), ("learn-linux-hands-on-lab.html", "Lab 2.2")],
  "Basic scripting: Bash and Python (variables, loops, files)": [("learn-bash-scripting-for-security.html", "Lesson 2.3")],
  "Network security: Nmap, Wireshark, firewalls, VPNs, IDS/IPS concepts": [("learn-ccna-access-control-lists.html", "Lesson 3.9"), ("learn-ccna-layer2-security-aaa.html", "Lesson 3.12")],
  "Blue team: logs, SIEM basics (Splunk / Elastic / Wazuh), alert triage": [("learn-linux-logging-auditing-hardening.html", "Lesson 2.4"), ("learn-ccna-network-operations.html", "Lesson 3.11")],
  "Windows basics: PowerShell, users & groups, services, Event Viewer": [("learn-windows-for-security.html", "Lesson 1.3")],
}
