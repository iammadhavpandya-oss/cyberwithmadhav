"""The Learn path: stages, live lessons and coming soon outlines.
Stage 3 follows the CCNA-aligned outline (Cisco CCNA 200-301 v1.1 exam topics), 14 lessons with Packet Tracer labs."""
from content.learn_s1a import lesson_computer, lesson_os
from content.learn_s1b import lesson_windows, lesson_network
from content.learn_s2 import lesson_linux_theory, lesson_linux_lab

LESSONS = [lesson_computer(), lesson_os(), lesson_windows(), lesson_network(), lesson_linux_theory(), lesson_linux_lab()]
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
              soon("2.3", "Bash Scripting for Security", ["Write scripts with variables, loops, conditions and functions", "Automate log triage and backups safely", "Read and audit other people's scripts before running them"], ["lab"]),
              soon("2.4", "Linux Logging, Auditing and Hardening", ["Use journald, rsyslog and auditd to record what matters", "Apply CIS style hardening and check it", "Detect common persistence with a repeatable checklist"], ["lab"])]),
  dict(n=3, id="stage-3", name="Networking and CCNA", hi_name="Networking aur CCNA", tag="Packet Tracer labs",
       desc="Fourteen lessons mapped to the Cisco CCNA 200-301 v1.1 exam topics, each with a Cisco Packet Tracer lab and a defensive security angle.",
       hi_desc="Cisco CCNA 200-301 v1.1 ke topics pe 14 lessons, har ek mein Packet Tracer lab aur security angle.",
       items=[
         soon("3.1", "Network Building Blocks: OSI, TCP/IP, Devices, Cabling, Interfaces", ["Map OSI layers to the TCP/IP model", "Name the job of routers, switches, APs, WLCs, firewalls and servers", "Spot duplex, speed and CRC problems in show interfaces"], ["PT lab"]),
         soon("3.2", "IP Addressing: IPv4 Subnetting, VLSM, Private Ranges, IPv6 Basics", ["Work out network, broadcast and host range for any prefix", "Design a VLSM plan without overlap", "Write, shorten and classify IPv6 addresses"], ["PT lab"]),
         soon("3.3", "Switching Fundamentals and Secure Device Access", ["Explain MAC learning, flooding and aging", "Do a secure baseline: enable secret, banners, local users", "Configure SSH version 2 and block Telnet"], ["PT lab"]),
         soon("3.4", "VLANs and Trunks: 802.1Q, Native VLAN, DTP, Voice VLAN", ["Create VLANs and assign data and voice ports", "Build 802.1Q trunks and change the native VLAN", "Explain VLAN hopping and apply the standard defences"], ["PT lab"]),
         soon("3.5", "Redundant Switch Links: STP, Rapid PVST+, PortFast, BPDU Guard, EtherChannel", ["Explain loops and broadcast storms and how STP stops them", "Predict root bridge and port roles", "Bundle uplinks with LACP EtherChannel"], ["PT lab"]),
         soon("3.6", "Inter-VLAN Routing and First Hop Redundancy", ["Configure router-on-a-stick and SVIs", "Compare HSRP, VRRP and GLBP", "Configure and verify basic HSRP"], ["PT lab"]),
         soon("3.7", "The Routing Table and Static Routing (IPv4 and IPv6)", ["Read every part of a routing table entry", "Explain longest prefix match, AD and metric", "Configure default, host and floating static routes"], ["PT lab"]),
         soon("3.8", "Single-Area OSPFv2", ["Explain neighbours, adjacencies and the LSDB", "Configure OSPF with router IDs and passive interfaces", "Troubleshoot neighbours stuck below FULL"], ["PT lab"]),
         soon("3.9", "Access Control Lists: Standard, Extended, Named", ["Write wildcard masks", "Configure standard and extended ACLs in the right place and direction", "Lock VTY access to an admin subnet"], ["PT lab"]),
         soon("3.10", "DHCP, DNS and NAT/PAT", ["Describe DHCP DORA and DNS resolution", "Configure DHCP server, relay and client on a router", "Configure static NAT, dynamic NAT and PAT"], ["PT lab"]),
         soon("3.11", "Network Operations: NTP, SNMP, Syslog, QoS, TFTP/FTP", ["Set up NTP and explain why time matters for logs", "Compare SNMPv2c and SNMPv3", "Send logs to syslog and back up configs with TFTP"], ["PT lab"]),
         soon("3.12", "Layer 2 Security, AAA and Security Fundamentals", ["Configure port security and DHCP snooping", "Explain Dynamic ARP Inspection", "Compare TACACS+ and RADIUS and configure AAA with local fallback"], ["PT lab"]),
         soon("3.13", "Wireless LANs: Architectures, WLC GUI, WPA2 and WPA3", ["Explain RF bands, channels, SSIDs and BSSIDs", "Compare autonomous, lightweight and cloud APs", "Create a WPA2 PSK WLAN on a controller and compare WPA3"], ["PT lab"]),
         soon("3.14", "Network Automation and Programmability", ["Compare traditional and controller based networking", "Describe SDN planes and APIs", "Read JSON and use a REST API"], ["PT lab"])]),
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
  "Networking basics: OSI & TCP/IP, IP addressing, subnetting, DNS, DHCP, common ports": [("learn-networking-basics.html", "Lesson 1.4"), ("learn.html#stage-3", "CCNA path")],
  "Linux command line: files, permissions, users, processes, package managers": [("learn-linux-fundamentals.html", "Lesson 2.1"), ("learn-linux-hands-on-lab.html", "Lab 2.2")],
  "Windows basics: PowerShell, users & groups, services, Event Viewer": [("learn-windows-for-security.html", "Lesson 1.3")],
}
