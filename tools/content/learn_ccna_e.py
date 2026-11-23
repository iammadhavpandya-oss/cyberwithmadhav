"""Stage 3 (CCNA track) lessons 3.11 to 3.14. Original writing for CyberWithMadhav."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from learn_kit import *
from content.learn_ccna_a import PT_NEEDS, PT_GENERIC

G3 = ["GigabitEthernet0/0/0", "GigabitEthernet0/0/1", "GigabitEthernet0/0/2"]
SW24 = [f"FastEthernet0/{i}" for i in range(1, 25)] + ["GigabitEthernet0/1", "GigabitEthernet0/2", "Vlan1"]

# ------------------------------------------------------------------ 3.11
TOPO11 = topo(760, 240, {"r1": (130, 70, "router", "R1", "192.168.1.1"), "sw1": (380, 70, "switch", "SW1", "VLAN 1 .2"),
    "srv": (630, 70, "server", "Server-Ops", "192.168.1.100"), "nms": (380, 200, "pc", "NMS-PC", "192.168.1.50")},
  [("r1", "sw1", "Gi0/0/0", ""), ("sw1", "srv", "", "NTP, syslog, TFTP, FTP"), ("sw1", "nms", "", "MIB Browser")],
  "Lab 3.11 topology: R1, SW1, an operations server and an NMS PC on 192.168.1.0/24")

QOSF = svg(760, 190, ARROWDEF +
  box(10, 60, 140, 60, "s-p", "Classify", "what is this?") + box(160, 60, 140, 60, "s-p", "Mark", "DSCP / CoS") + box(310, 60, 140, 60, "s-g", "Queue", "voice first") +
  box(460, 60, 140, 60, "s-n", "Avoid congestion", "WRED drops early") + box(610, 60, 140, 60, "s-n", "Police or shape", "drop or delay") +
  arrow(150, 90, 158, 90) + arrow(300, 90, 308, 90) + arrow(450, 90, 458, 90) + arrow(600, 90, 608, 90) +
  '<text x="380" y="160" text-anchor="middle" font-size="12" class="t-m">Each device applies this per hop; it only matters when a link is congested</text>',
  "QoS tool chain: classify, mark, queue, avoid congestion, then police or shape")

SEVS = [("0", "emergencies", "System unusable"), ("1", "alerts", "Immediate action needed"), ("2", "critical", "Critical condition"), ("3", "errors", "Error condition, for example %LINK-3-UPDOWN"),
        ("4", "warnings", "Warning"), ("5", "notifications", "Normal but significant, for example %SYS-5-CONFIG_I"), ("6", "informational", "Informational"), ("7", "debugging", "Debug output, the least severe")]

def lesson_ccna_11():
  S = []
  S.append(dict(id="ntp", h="NTP: why every device needs the right time", hi_h="NTP aur sahi time",
    body=f'''<p>When something goes wrong at 02:14 on the firewall, you want to line it up with what the core switch logged at 02:14. If one device is seven minutes fast, that timeline is useless. Wrong time also breaks certificate checks (a certificate can look "not yet valid") and some authentication.</p>
<ul><li><strong>NTP</strong> uses UDP port 123 and is organised by <strong>stratum</strong>: stratum 1 servers are directly attached to a reference clock (GPS, atomic), stratum 2 learn from stratum 1, and so on. Stratum 16 means unsynchronised.</li>
<li><code>ntp server 192.168.1.100</code> makes a Cisco device an NTP client of that server. Its own stratum becomes the server's plus one.</li>
<li>A device can also serve time to others; on IOS, <code>ntp master</code> makes a router an authoritative source when nothing better exists.</li>
<li><code>service timestamps log datetime msec</code> puts the date and time, to the millisecond, on every log message.</li></ul>
{ios(["R1(config)# ntp server 192.168.1.100", "R1(config)# service timestamps log datetime msec", "R1# show ntp status", "Clock is synchronized, stratum 2, reference is 192.168.1.100", "R1# show ntp associations", "R1# show clock detail"], "NTP client")}''',
    hi="Sabhi devices ka time same hona chahiye, warna logs ki timeline bekaar aur certificates fail. NTP UDP 123, stratum se chalta hai: stratum 1 reference clock ke paas, 16 matlab unsynchronised. ntp server se device client banta hai, uska stratum server se ek zyada. service timestamps log datetime msec se har log pe exact time."))

  S.append(dict(id="syslog", h="Syslog and severity levels", hi_h="Syslog aur severity",
    body=f'''<p>Cisco messages look like <code>%LINK-3-UPDOWN: Interface GigabitEthernet0/0/1, changed state to down</code>: facility (LINK), severity (3), mnemonic (UPDOWN), then the text. Syslog sends them to a server over UDP port 514.</p>
{table(["Level", "Keyword", "Meaning"], [list(s) for s in SEVS], "Syslog severity levels")}
<p>Choosing a level means "this level and everything more severe". <code>logging trap informational</code> (6) sends levels 0 to 6 and skips debugging. A common trap: thinking 7 is the most serious. It is the least.</p>
{ios(["R1(config)# logging host 192.168.1.100", "R1(config)# logging trap informational", "! older IOS form: logging 192.168.1.100", "R1# show logging"], "Send logs to a server")}
{attack("<p>An intruder who gets onto a router can clear its local log buffer, and with it the evidence of what they did. If time is wrong or logs stay on the box, the investigation has nothing to work with.</p>")}
{defend("<p>Send logs off the device to a syslog server or SIEM the network team cannot quietly edit, keep NTP correct everywhere, and alert on config change messages such as <code>%SYS-5-CONFIG_I</code> outside change windows. Restrict NTP to known servers, using NTP authentication and ACLs where you can.</p>")}''',
    hi="Message format: %FACILITY-SEVERITY-MNEMONIC. Syslog UDP 514. Levels 0 (emergencies) se 7 (debugging); 0 sabse serious, 7 sabse kam. logging trap informational matlab 0 se 6 tak sab. Attacker local logs clear kar sakta hai, isliye logs server ya SIEM pe bhejo aur config change alerts lagao."))

  S.append(dict(id="snmp", h="SNMP: monitoring devices", hi_h="SNMP",
    body=f'''<p>A network management system (<strong>NMS</strong>, the manager) <em>polls</em> <strong>agents</strong> on devices with SNMP over UDP port 161, and agents send <strong>traps</strong> or <strong>informs</strong> (an inform is a trap that expects an acknowledgement) to UDP port 162 when something happens. The data is organised in a <strong>MIB</strong> (management information base); each value, such as sysUpTime or an interface counter, has an <strong>OID</strong> (object identifier).</p>
{table(["Version", "Security", "Use"], [
  ["SNMPv1, v2c", "A community string, sent in cleartext. RO lets you read, RW lets you change settings.", "Labs, or read only behind strict ACLs"],
  ["SNMPv3", "Users with authentication and optional encryption (noAuthNoPriv, authNoPriv, authPriv)", "Production: use authPriv"]], "SNMP versions")}
{ios(["R1(config)# access-list 20 permit host 192.168.1.50", "R1(config)# snmp-server community CwmLabRO ro 20", "! SNMPv3 outline (concept, see lab notes):", "R1(config)# snmp-server group OPS v3 priv", "R1(config)# snmp-server user nms1 OPS v3 auth sha AUTHPASS priv aes 128 PRIVPASS"], "SNMP")}
<p>Communities named <code>public</code> and <code>private</code> are the first thing scanners try. A read-write v2c community is effectively a cleartext admin password. Never configure one on a production device.</p>''',
    hi="NMS agents ko UDP 161 pe poll karta hai, agents events pe UDP 162 pe trap bhejte hain. MIB data model hai, OID ek value. v1/v2c mein community string cleartext jaati hai; RW community matlab cleartext admin password. Production mein SNMPv3 authPriv aur ACL."))

  S.append(dict(id="qos", h="QoS in one picture", hi_h="QoS",
    body=f'''{fig(QOSF, "QoS does not create bandwidth. It decides who waits and who is dropped when a link is full.", "QoS tools")}
<ul><li><strong>Classification and marking</strong>: identify traffic and mark it so later devices do not have to look again. At Layer 3, the <strong>DSCP</strong> field in the IP header (voice is usually EF, value 46). At Layer 2, the 3 bit <strong>CoS</strong> field in the 802.1Q tag.</li>
<li><strong>Trust boundary</strong>: the point where you start believing markings. Usually the access switch port toward an IP phone, never a user PC that could mark its own downloads as voice.</li>
<li><strong>Queuing</strong>: a strict priority queue for voice (small, delay sensitive), weighted queues for the rest.</li>
<li><strong>Congestion avoidance</strong>: WRED drops some TCP packets early, so senders slow down before the queue overflows.</li>
<li><strong>Policing vs shaping</strong>: a policer drops or re-marks traffic above a rate; a shaper buffers and delays it. Service providers police; customers shape to stay under the contract rate.</li></ul>
<p>Voice and video care about <strong>delay</strong>, <strong>jitter</strong> (variation in delay) and <strong>loss</strong>. Commonly quoted targets for voice are one way delay under about 150 ms, jitter under about 30 ms and loss under 1 percent.</p>''',
    hi="QoS bandwidth nahi badhata, congestion mein decide karta hai kaun wait kare. Classify aur mark (DSCP, voice EF 46; CoS 802.1Q tag mein), trust boundary phone wale port pe, voice ke liye priority queue, WRED early drop, policing drop karta hai aur shaping delay. Voice ko delay, jitter aur loss pareshan karte hain."))

  S.append(dict(id="backup", h="Backups: TFTP, FTP and the secure options", hi_h="Config backup",
    body=f'''{table(["Protocol", "Transport", "Authentication", "Encryption"], [["TFTP", "UDP 69", "None", "None"], ["FTP", "TCP 21 control, 20 data (active mode)", "Username and password", "None, credentials in cleartext"], ["SCP, SFTP", "TCP 22 (SSH)", "SSH credentials or keys", "Yes"]], "File transfer options")}
{ios(["R1# copy running-config tftp:", "Address or name of remote host []? 192.168.1.100", "Destination filename [r1-confg]?", "!!", "R1# copy tftp: running-config      ! restore (merges into the running config)"], "Backup to TFTP")}
<p>TFTP is fine on an isolated lab network and nowhere else: anyone on the path can read the file, and anyone who can reach the server can overwrite it. Your configuration contains password hashes, SNMP communities and keys, so treat backups like secrets.</p>''',
    hi="TFTP UDP 69, na authentication na encryption, sirf isolated lab ke liye. FTP mein password cleartext. Production mein SCP ya SFTP. copy running-config tftp: se backup. Config mein hashes, communities aur keys hote hain, backup ko secret ki tarah rakho."))

  S.append(dict(id="practice", h="Practise on R1", hi_h="R1 pe practice",
    body=f'''<p>Server-Ops at 192.168.1.100 provides NTP (as a stratum 1 source in this console), syslog and TFTP. Outputs are modelled.</p>
{ios_sim(dict(id="l311", kind="router", host="R1", ifaces=G3, up=["GigabitEthernet0/0/0"],
  init={"GigabitEthernet0/0/0": dict(shut=False, ip="192.168.1.1", mask="255.255.255.0")}, ntp=dict(ok="192.168.1.100", st=1),
  intro=["R1, an ISR4331 on 192.168.1.0/24. Start with enable."],
  missions=[
    dict(t="Check the time source before changing anything. Is the clock synchronised? Type <code>answer yes</code> or <code>answer no</code>.", hint="enable, show ntp status", c=dict(type="answer", v="no"), ok="Stratum 16: no reference. The leading * in show clock also means the time is not authoritative."),
    dict(t="Make R1 an NTP client of 192.168.1.100.", hint="configure terminal, ntp server 192.168.1.100", c=dict(type="run", re=r"^ntp server 192\.168\.1\.100$")),
    dict(t="Which stratum is R1 now? Type <code>answer N</code>.", hint="do show ntp status", c=dict(type="answer", v="2"), ok="One more than its stratum 1 server."),
    dict(t="Timestamp log messages with date, time and milliseconds.", hint="service timestamps log datetime msec", c=dict(type="run", re=r"^service timestamps log datetime msec$")),
    dict(t="Send logs to the syslog server at 192.168.1.100.", hint="logging host 192.168.1.100", c=dict(type="run", re=r"^logging host 192\.168\.1\.100$")),
    dict(t="Send severities 0 to 6 to the server.", hint="logging trap informational (or logging trap 6)", c=dict(type="cmd", re=r"^logging trap", raw=r"logging trap (informational|6)\s*$"), ok="Informational (6) is the default trap level, so it will not appear in the running config; show logging confirms it."),
    dict(t="What number is the warnings severity? Type <code>answer N</code>.", hint="0 emergencies, 1 alerts, 2 critical, 3 errors...", c=dict(type="answer", v="4")),
    dict(t="Only NMS-PC (192.168.1.50) may poll SNMP. Create standard ACL 20 for it.", hint="access-list 20 permit host 192.168.1.50", c=dict(type="run", re=r"^access-list 20 permit host 192\.168\.1\.50$")),
    dict(t="Create the read only v2c community CwmLabRO, restricted by ACL 20.", hint="snmp-server community CwmLabRO ro 20", c=dict(type="run", re=r"^snmp-server community CwmLabRO RO 20$")),
    dict(t="Back up the configuration to the TFTP server.", hint="end, copy running-config tftp:, then 192.168.1.100 and Enter", c=dict(type="cmd", re=r"^copy running-config tftp:$")),
    dict(t="Save.", hint="copy running-config startup-config", c=dict(type="saved"))]), "R1 operations console")}''',
    hi="Simulator mein R1: pehle NTP status dekho (unsynchronised), ntp server, stratum padho, timestamps, logging host aur trap informational, ACL 20 aur read only community, TFTP backup, save."))

  return dict(
    slug="learn-ccna-network-operations", stage=3, n="3.11", minutes=60, level="Intermediate",
    title="Network Operations: NTP, Syslog, SNMP, QoS and Config Backups", short="Accurate time, log severities, SNMP versions, QoS basics and backing up configs safely.",
    seo_title="NTP, Syslog, SNMP and QoS for CCNA: Severity Levels, SNMPv3, TFTP Backup | CyberWithMadhav",
    desc="Free CCNA lesson on network operations: NTP and stratum, syslog severity levels, SNMP polling, traps and SNMPv3, QoS classification, queuing, policing and shaping, and TFTP, FTP and SCP backups, with an IOS simulator and Packet Tracer lab.",
    kw="ntp server cisco, syslog severity levels, logging trap informational, snmp v2c vs v3, snmp community ro acl, qos dscp ef policing shaping, copy running-config tftp, packet tracer syslog ntp lab, ccna network operations",
    kicker="$ lesson 3.11 --track ccna --domain operations", hi_title="Network operations",
    lead="A network that works is only half the job. You also need to know what it is doing and what it did. Learn how NTP keeps every timestamp honest, how syslog severities work, how SNMP monitors devices and why v2c is risky, what QoS really does, and how to back up configs without leaking them.",
    hi_lead="Network chalana aadha kaam hai; usne kya kiya yeh jaanna bhi zaroori hai. NTP, syslog, SNMP, QoS aur safe backups seekho.",
    goals=["Configure NTP clients and read stratum and sync state", "Send logs to a syslog server at the right severity", "Explain SNMP polling, traps, MIBs and OIDs, and compare v2c with v3", "Describe classification, marking, queuing, policing and shaping", "Back up a configuration and choose a secure transfer protocol"],
    sections=S,
    cards=[("NTP port?", "UDP 123."), ("Stratum 16 means?", "Unsynchronised."), ("Syslog port?", "UDP 514."), ("Most severe syslog level?", "0, emergencies."),
      ("logging trap informational sends?", "Levels 0 to 6."), ("SNMP ports?", "161 polling, 162 traps and informs."), ("Policing vs shaping?", "Policing drops or re-marks; shaping buffers and delays."), ("TFTP port and security?", "UDP 69, no authentication, no encryption.")],
    quiz=[("Which severity is the least serious?", ["0", "3", "5", "7"], 3, "7 is debugging."),
      ("Why does accurate time matter for security?", ["It speeds up routing", "Log correlation and certificate validity depend on it", "It reduces SNMP traffic", "It is required for VLANs"], 1, "Timelines and certificate checks both need correct clocks."),
      ("What protects SNMP traffic with authentication and encryption?", ["SNMPv1", "SNMPv2c", "SNMPv3 authPriv", "A long community string"], 2, "v1 and v2c send communities in cleartext."),
      ("A provider drops traffic above the contracted rate. That is:", ["Shaping", "Policing", "Queuing", "Marking"], 1, "Shaping would buffer it instead."),
      ("Which DSCP value is commonly used for voice?", ["EF (46)", "AF11 (10)", "CS1 (8)", "0"], 0, "Expedited Forwarding."),
      ("Which protocol is the secure choice for copying configs?", ["TFTP", "FTP", "SCP", "Telnet"], 2, "SCP runs over SSH.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.11: time, logs, SNMP and backups", time="45 minutes",
      needs=PT_NEEDS + " Devices: 1 x ISR4331, 1 x 2960, 1 x Server-PT (Server-Ops), 1 x PC-PT (NMS-PC).",
      topo=fig(TOPO11, "R1 Gi0/0/0, Server-Ops and NMS-PC all connect to SW1.", "Lab topology"),
      addr=[["R1", "Gi0/0/0", "192.168.1.1/24", ""], ["SW1", "VLAN 1", "192.168.1.2/24", "default gateway 192.168.1.1"], ["Server-Ops", "Fa0", "192.168.1.100/24", "NTP, syslog, TFTP, FTP"], ["NMS-PC", "Fa0", "192.168.1.50/24", "MIB Browser"]],
      steps=[("Server services", "<p>On Server-Ops, open Services and turn on NTP, Syslog, TFTP and FTP. Add an FTP user with write permission.</p>"),
        ("NTP on R1 and SW1", ios(["ntp server 192.168.1.100", "service timestamps log datetime msec"], "NTP") + "<p>Sync can take a minute or more of simulated time; use the fast forward button.</p>"),
        ("Syslog on R1 and SW1", ios(["logging host 192.168.1.100", "logging trap informational"], "Syslog") + "<p>If <code>logging host</code> is rejected, try the older form <code>logging 192.168.1.100</code>.</p>"),
        ("Make some logs", "<p>Shut and unshut an interface, enter and leave configuration mode, then open Services, Syslog on Server-Ops and find the entries from 192.168.1.1 and 192.168.1.2.</p>"),
        ("SNMP on R1 (v2c, lab only)", ios(["R1(config)# access-list 20 permit host 192.168.1.50", "R1(config)# snmp-server community CwmLabRO ro 20"], "SNMP") + "<p>On NMS-PC open Desktop, MIB Browser: target 192.168.1.1, community CwmLabRO, then GET sysName or sysUpTime.</p>"),
        ("Back up the config", ios(["R1# copy running-config tftp:", "Address or name of remote host []? 192.168.1.100", "Destination filename [r1-confg]?"], "TFTP") + "<p>Check the TFTP file list on Server-Ops. Optionally try <code>ip ftp username</code>, <code>ip ftp password</code> and <code>copy running-config ftp:</code>.</p>"),
        ("Verify", ios(["R1# show ntp status", "R1# show ntp associations", "R1# show clock detail", "R1# show logging"], "Verify"))],
      verify="show ntp status says synchronised with reference 192.168.1.100, show clock detail names NTP as the source, show logging shows trap level informational and host 192.168.1.100, Server-Ops lists syslog entries from both devices, the MIB Browser GET returns a value, and r1-confg appears in the TFTP list.",
      limits=["SNMPv3 commands (<code>snmp-server group</code>, <code>snmp-server user ... auth sha ... priv aes</code>) in Packet Tracer are UNVERIFIED. If rejected, treat SNMPv3 as concept.",
              "<code>ntp master</code> and NTP authentication on Packet Tracer routers are UNVERIFIED. The Server-PT NTP service is the dependable time source.",
              "Whether <code>logging host</code>, <code>logging &lt;ip&gt;</code> or both are accepted depends on the image: UNVERIFIED.",
              "QoS configuration (class-map, policy-map, service-policy) support in Packet Tracer is partial and UNVERIFIED, so QoS stays conceptual here.",
              "FTP copy from IOS in Packet Tracer is UNVERIFIED; TFTP copy works in the outline author's experience. <code>show snmp community</code> is also UNVERIFIED.", PT_GENERIC]),
    takeaways=["Correct time everywhere, from NTP, makes logs and certificates trustworthy.", "Severity 0 is the worst and 7 the least; a trap level includes everything more severe.", "Send logs off the box and alert on config changes.",
      "SNMP v2c communities are cleartext; use v3 authPriv and ACLs.", "QoS manages congestion; it does not add bandwidth.", "Back up configs over SCP or SFTP and protect the files."])

# ------------------------------------------------------------------ 3.12
TOPO12 = topo(760, 320, {"sw1": (300, 80, "switch", "SW1", "2960, VLAN 10 .2"), "r1": (560, 80, "router", "R1", "ISR4331"), "aaa": (700, 210, "server", "Server-AAA", "10.0.0.20"),
    "dhcp": (80, 80, "server", "Server-DHCP", "192.168.10.5"), "p1": (120, 260, "pc", "PC1", "DHCP"), "p2": (240, 260, "pc", "PC2", "DHCP"),
    "rog": (360, 260, "server", "Rogue-Server", "192.168.10.6"), "adm": (480, 260, "pc", "Admin-PC", "192.168.10.50")},
  [("dhcp", "sw1", "", "Fa0/24"), ("sw1", "r1", "Gi0/1", "Gi0/0/0"), ("r1", "aaa", "Gi0/0/1", ""), ("sw1", "p1", "Fa0/1", ""), ("sw1", "p2", "Fa0/2", ""), ("sw1", "rog", "Fa0/3", "", "dash"), ("sw1", "adm", "Fa0/10", "")],
  "Lab 3.12 topology: SW1 with a real DHCP server on Fa0/24, two DHCP clients, a rogue DHCP server on Fa0/3 and an admin PC; R1 reaches an AAA server")

MITM = svg(760, 200, ARROWDEF +
  box(30, 70, 150, 56, "s-g", "PC1", "192.168.10.100") + box(305, 130, 150, 56, "s-a", "Attacker", "fake ARP replies") + box(580, 70, 150, 56, "s-p", "Gateway", "192.168.10.1") +
  '<line x1="182" y1="98" x2="578" y2="98" class="ln" stroke-width="2" stroke-dasharray="6 5"/><text x="380" y="88" text-anchor="middle" font-size="11.5" class="t-m">intended path</text>' +
  arrow(182, 115, 303, 150) + arrow(457, 150, 578, 115) +
  '<text x="380" y="40" text-anchor="middle" font-size="12" class="t-m">"192.168.10.1 is at my MAC": PC1 now sends its traffic through the attacker</text>',
  "ARP spoofing: the attacker claims the gateway's IP so PC1's traffic flows through it. DAI drops ARP replies that do not match the DHCP snooping table")

SNOOP12 = dict(server="FastEthernet0/24", clients=[["0060.2f84.4ab6", "192.168.10.100", 10, "FastEthernet0/1"], ["00d0.ba11.2c01", "192.168.10.101", 10, "FastEthernet0/2"]])
MACS12 = [["10", "0060.2f84.4ab6", "Fa0/1"], ["10", "00d0.ba11.2c01", "Fa0/2"], ["10", "0001.c7a3.9e10", "Fa0/3"], ["10", "0001.c7a3.9e11", "Fa0/3"], ["10", "0002.4a1b.7701", "Fa0/10"], ["10", "000c.85aa.0105", "Fa0/24"], ["10", "0001.6400.0101", "Gi0/1"]]

def acc(v=10):
  return dict(mode="access", av=v, shut=False)

def lesson_ccna_12():
  S = []
  S.append(dict(id="basics", h="Security language and the human layer", hi_h="Security basics",
    body=f'''{table(["Term", "Meaning", "Example"], [
  ["Threat", "Who or what could cause harm", "A scammer, malware, a careless insider"],
  ["Vulnerability", "The weakness", "An open switch port in a meeting room"],
  ["Exploit", "The method that uses the weakness", "Plugging in a rogue DHCP server"],
  ["Mitigation", "The control that reduces the risk", "DHCP snooping, port security"]], "Security terms")}
<p>A security programme is more than device configuration: <strong>user awareness</strong> (recognising phishing and scams, the topic of much of this site), <strong>training</strong> for the people who run systems, and <strong>physical access control</strong> (badges, locked wiring closets, no spare live ports in public areas). Most breaches still start with a stolen password or a convincing message, which is why <strong>MFA</strong> belongs in network security too.</p>
<p>Passwords alone are weak. Alternatives and additions: multi factor authentication (something you know plus something you have or are), certificates (a device or user proves itself with a private key), and biometrics. In password policy, length beats forced complexity, and checking new passwords against known breached lists helps more than frequent forced changes.</p>''',
    hi="Threat = nuksaan kaun kar sakta hai, vulnerability = kamzori, exploit = kamzori use karne ka tareeka, mitigation = control. Security programme mein awareness, training aur physical access control bhi hain. Zyaadatar breaches phishing ya chori ke password se shuru hote hain, isliye MFA, certificates aur lambe passwords."))

  S.append(dict(id="portsec", h="Port security", hi_h="Port security",
    body=f'''<p>A switch learns MAC addresses into a table of limited size. A <strong>CAM (MAC) flooding</strong> attack sends frames from thousands of fake source MACs until the table is full, after which some switches flood unknown unicast traffic out of every port, where the attacker can capture it. Port security limits how many MACs a port may use.</p>
{table(["Setting", "Default", "Notes"], [
  ["<code>switchport port-security maximum N</code>", "1", "MAC addresses allowed on the port"],
  ["<code>switchport port-security violation</code>", "shutdown", "protect: drop silently. restrict: drop, log and count. shutdown: err-disable the port."],
  ["<code>switchport port-security mac-address sticky</code>", "off", "Learned MACs are written into the running config (save to keep them)."]], "Port security options")}
{ios(["SW1(config)# interface range Fa0/1 - 2", "SW1(config-if-range)# switchport mode access", "SW1(config-if-range)# switchport access vlan 10", "SW1(config-if-range)# switchport port-security", "SW1(config-if-range)# switchport port-security maximum 2", "SW1(config-if-range)# switchport port-security mac-address sticky", "SW1(config-if-range)# switchport port-security violation restrict"], "Port security")}
<p>Port security only works on a port that is statically access (or trunk); a dynamic (DTP) port rejects it. An err-disabled port comes back with <code>shutdown</code> then <code>no shutdown</code> once the cause is removed. Port security does not stop someone copying an allowed MAC address. 802.1X, which authenticates the device or user before the port opens, is the stronger control.</p>''',
    hi="CAM flooding mein fake MACs se switch ki table bhar jaati hai aur traffic flood hota hai. Port security MAC limit lagata hai: default maximum 1, violation shutdown (err-disabled). protect chupchaap drop, restrict drop + log + count. sticky learned MACs running config mein likhta hai. Port access mode mein hona chahiye. MAC copy karna phir bhi possible hai; 802.1X zyada strong hai."))

  S.append(dict(id="snoop", h="DHCP snooping and Dynamic ARP Inspection", hi_h="DHCP snooping aur DAI",
    body=f'''<p><strong>DHCP snooping</strong> splits switch ports into trusted (toward the real DHCP server, and uplinks) and untrusted (everything else). Server messages such as Offer and Ack arriving on an untrusted port are dropped, so a rogue server on a user port cannot hand out a fake gateway or DNS. Snooping also builds a <strong>binding table</strong> of MAC, IP, VLAN, port and lease for every client, and can rate limit DHCP on untrusted ports to slow starvation attacks.</p>
{ios(["SW1(config)# ip dhcp snooping", "SW1(config)# ip dhcp snooping vlan 10", "SW1(config)# no ip dhcp snooping information option", "SW1(config)# interface Fa0/24", "SW1(config-if)# ip dhcp snooping trust", "SW1(config)# interface range Fa0/1 - 10", "SW1(config-if-range)# ip dhcp snooping limit rate 10"], "DHCP snooping")}
<p>You need both the global command and the per VLAN command. When snooping is on, the switch inserts DHCP <strong>option 82</strong> by default; a server that is not expecting it may ignore those requests, which is why labs often turn it off.</p>
{fig(MITM, "ARP has no authentication, so any host can claim any IP. Dynamic ARP Inspection checks ARP on untrusted ports against the snooping bindings.", "ARP spoofing")}
<p><strong>Dynamic ARP Inspection</strong> (<code>ip arp inspection vlan 10</code>) inspects ARP packets on untrusted ports and drops any whose IP to MAC pairing is not in the binding table. Trust the uplinks and the server port with <code>ip arp inspection trust</code>. Devices with static addresses have no binding, so on real gear they need trust or an ARP ACL, or their ARP is dropped. Snooping alone does not stop ARP spoofing; it only builds the table DAI uses.</p>''',
    hi="DHCP snooping mein trusted ports (real server, uplinks) aur untrusted ports. Untrusted port pe aaya Offer/Ack drop, toh rogue DHCP server kaam nahi karta. Binding table banti hai (MAC, IP, VLAN, port). Global aur per-VLAN dono commands chahiye. Option 82 labs mein off karte hain. DAI ARP packets ko binding table se match karta hai aur fake ARP drop karta hai; static IP wale devices ko trust ya ARP ACL chahiye."))

  S.append(dict(id="aaa", h="AAA, TACACS+ and RADIUS", hi_h="AAA",
    body=f'''<p>Local usernames on every device do not scale: when an engineer leaves, someone has to remove them from 400 switches. <strong>AAA</strong> moves the decision to a server: <strong>authentication</strong> (who are you), <strong>authorization</strong> (what may you do), <strong>accounting</strong> (what did you do).</p>
{table(["", "TACACS+", "RADIUS"], [["Transport", "TCP 49", "UDP 1812 and 1813 (older 1645 and 1646)"], ["Encryption", "Whole payload", "Only the password"], ["The three A's", "Separate, so per command authorization is possible", "Authentication and authorization combined"], ["Typical use", "Device administration", "Network access: 802.1X, VPN, Wi-Fi"], ["Origin", "Cisco originated, now documented in RFC 8907", "Open standard"]], "TACACS+ compared with RADIUS")}
{ios(["R1(config)# username backup secret <a long local password>", "R1(config)# tacacs-server host 10.0.0.20 key <shared key>", "R1(config)# aaa new-model", "R1(config)# aaa authentication login default group tacacs+ local", "R1(config)# line vty 0 4", "R1(config-line)# login authentication default", "R1(config-line)# transport input ssh"], "AAA with local fallback")}
<p>The method list is tried in order: the TACACS+ server first, and the local database only if the server cannot be reached (not if it says no). Keep one local account for that emergency, with a long secret that is rarely used and closely watched. Run <code>aaa new-model</code> only once you have that account and an open console session, because it changes login behaviour immediately.</p>
<p><strong>VPNs</strong> (concept): an IPsec <strong>site to site</strong> VPN joins two networks across the internet through their gateways; a <strong>remote access</strong> VPN connects one user's device, using client software or a browser based TLS portal. IPsec provides confidentiality, integrity, authentication and anti-replay. A VPN protects traffic in transit; it does nothing about malware already on the laptop.</p>''',
    hi="AAA: authentication, authorization, accounting, ek central server pe. TACACS+ TCP 49, poora payload encrypted, teeno A alag, device admin ke liye. RADIUS UDP 1812/1813, sirf password encrypted, network access (802.1X, VPN, Wi-Fi) ke liye. Method list order mein try hoti hai; local fallback sirf tab jab server reachable na ho. aaa new-model se pehle local account aur console session ready rakho. VPN traffic ko bachata hai, device ke malware ko nahi."))

  S.append(dict(id="practice", h="Practise on SW1", hi_h="SW1 pe practice",
    body=f'''<p>SW1 is a 2960. VLAN 10 exists, Fa0/24 (real DHCP server) and Fa0/10 (Admin-PC) are already access ports in VLAN 10, Gi0/1 is the trunk to R1. Fa0/1 to Fa0/3 have not been touched. Fa0/3 has a small hub with two devices behind it, one of them the rogue server. The DHCP clients are modelled by the console.</p>
{ios_sim(dict(id="l312", kind="switch", host="SW1", ifaces=SW24, up=["FastEthernet0/1", "FastEthernet0/2", "FastEthernet0/3", "FastEthernet0/10", "FastEthernet0/24", "GigabitEthernet0/1"],
  vlans={"10": "USERS"}, macs=MACS12, snoop=SNOOP12,
  init={"FastEthernet0/24": acc(), "FastEthernet0/10": acc(), "GigabitEthernet0/1": dict(mode="trunk", nonego=True, shut=False)},
  intro=["SW1, a Catalyst 2960. Start with enable."],
  missions=[
    dict(t="Turn on DHCP snooping globally and for VLAN 10, and stop the switch inserting option 82.", hint="enable, configure terminal, ip dhcp snooping, ip dhcp snooping vlan 10, no ip dhcp snooping information option", c=dict(type="run", re=r"(?=[\s\S]*^ip dhcp snooping$)(?=[\s\S]*^ip dhcp snooping vlan 10$)[\s\S]*^no ip dhcp snooping information option$")),
    dict(t="Trust only the port to the real DHCP server.", hint="interface fa0/24, ip dhcp snooping trust", c=dict(type="run", re=r"^interface FastEthernet0/24\n[^!]*ip dhcp snooping trust")),
    dict(t="Rate limit DHCP to 10 packets per second on Fa0/1 to Fa0/10.", hint="interface range fa0/1 - 10, ip dhcp snooping limit rate 10", c=dict(type="run", re=r"^interface FastEthernet0/10\n[^!]*ip dhcp snooping limit rate 10")),
    dict(t="How many clients are in the snooping binding table? Type <code>answer N</code>.", hint="do show ip dhcp snooping binding", c=dict(type="answer", v="2"), ok="PC1 and PC2, both leased by the real server through trusted Fa0/24."),
    dict(t="Turn on Dynamic ARP Inspection for VLAN 10 and trust the server port and the uplink.", hint="exit, ip arp inspection vlan 10, interface fa0/24, ip arp inspection trust, interface g0/1, ip arp inspection trust", c=dict(type="run", re=r"(?=[\s\S]*^ip arp inspection vlan 10$)(?=[\s\S]*^interface FastEthernet0/24\n[^!]*ip arp inspection trust)[\s\S]*^interface GigabitEthernet0/1\n[^!]*ip arp inspection trust")),
    dict(t="Try to enable port security on Fa0/1 straight away. Read the message, then make Fa0/1 and Fa0/2 static access ports in VLAN 10.", hint="interface range fa0/1 - 2, switchport port-security, then switchport mode access, switchport access vlan 10", c=dict(type="run", re=r"^interface FastEthernet0/2\n switchport access vlan 10\n switchport mode access")),
    dict(t="On Fa0/1 and Fa0/2: port security, up to 2 MACs, sticky learning, violation restrict.", hint="switchport port-security, switchport port-security maximum 2, switchport port-security mac-address sticky, switchport port-security violation restrict", c=dict(type="run", re=r"^interface FastEthernet0/2\n[^!]*switchport port-security maximum 2\n[^!]*switchport port-security violation restrict\n[^!]*mac-address sticky")),
    dict(t="Now Fa0/3: static access in VLAN 10 with default port security. Watch what happens with two devices behind it.", hint="interface fa0/3, switchport mode access, switchport access vlan 10, switchport port-security", c=dict(type="out", re=r"err-disable")),
    dict(t="What state is Fa0/3 in now? Type <code>answer STATE</code>.", hint="do show interfaces status err-disabled", c=dict(type="answer", v=["err-disabled", "errdisabled", "err-disable"]), ok="Default maximum is 1 and default violation is shutdown. Remove the hub, then shutdown and no shutdown to recover."),
    dict(t="Recover Fa0/3 after removing the hub and rogue server.", hint="shutdown, no shutdown", c=dict(type="cmd", re=r"^no shutdown$")),
    dict(t="Centralise logins: a local fallback user, a TACACS+ server at 10.0.0.20 with key CwmKey, AAA on, and a default login list trying TACACS+ then local.", hint="username backup secret <long password>, tacacs-server host 10.0.0.20 key CwmKey, aaa new-model, aaa authentication login default group tacacs+ local", c=dict(type="run", re=r"(?=[\s\S]*^username backup )(?=[\s\S]*^tacacs-server host 10\.0\.0\.20 key CwmKey$)(?=[\s\S]*^aaa new-model$)[\s\S]*^aaa authentication login default group tacacs\+ local$")),
    dict(t="Save.", hint="end, copy running-config startup-config", c=dict(type="saved"))]), "SW1 access layer console")}''',
    hi="Simulator mein SW1: DHCP snooping on, server port trust, rate limit, binding table dekho, DAI on, phir port security: pehle dynamic port pe reject dekho, access mode karo, maximum 2 sticky restrict, Fa0/3 pe default port security se err-disabled dekho aur recover karo, AAA TACACS+ local fallback ke saath, save."))

  return dict(
    slug="learn-ccna-layer2-security-aaa", stage=3, n="3.12", minutes=75, level="Advanced",
    title="Layer 2 Security and AAA: Port Security, DHCP Snooping, DAI, TACACS+ and RADIUS", short="Threat language, port security, DHCP snooping, ARP inspection, AAA servers and VPN concepts.",
    seo_title="Layer 2 Security for CCNA: Port Security, DHCP Snooping, DAI, AAA TACACS+ vs RADIUS | CyberWithMadhav",
    desc="Free CCNA lesson on access layer security: threats and mitigations, port security violation modes, DHCP snooping, Dynamic ARP Inspection, AAA with TACACS+ and RADIUS, and IPsec VPN concepts, with an IOS simulator and Packet Tracer lab.",
    kw="port security cisco sticky violation, dhcp snooping configuration, dynamic arp inspection, arp spoofing defence, aaa new-model tacacs+, tacacs vs radius, rogue dhcp server, packet tracer port security lab, ccna security fundamentals",
    kicker="$ lesson 3.12 --track ccna --domain security", hi_title="Layer 2 security aur AAA",
    lead="Most attacks on a LAN start at a wall port: a rogue DHCP server, a flood of fake MAC addresses, a laptop pretending to be the gateway. Learn the switch features that stop each one, and how AAA servers replace a password on every box.",
    hi_lead="LAN pe zyaadatar attacks ek wall port se shuru hote hain. Har attack ko rokne wale switch features aur AAA seekho.",
    goals=["Use threat, vulnerability, exploit and mitigation correctly", "Configure port security with limits, sticky learning and violation modes", "Configure DHCP snooping and explain how DAI uses it", "Compare TACACS+ and RADIUS and configure AAA with a local fallback", "Describe site to site and remote access VPNs and password alternatives"],
    sections=S,
    cards=[("Port security default maximum?", "1 MAC."), ("Port security default violation mode?", "shutdown (err-disabled)."), ("restrict vs protect?", "Both drop; restrict also logs and counts."),
      ("DHCP snooping trusted ports?", "Toward the real server and uplinks; everything else untrusted."), ("What does DAI check ARP against?", "The DHCP snooping binding table."), ("TACACS+ transport?", "TCP 49, whole payload encrypted."),
      ("RADIUS ports?", "UDP 1812 and 1813."), ("When is the local fallback used?", "Only when the AAA server cannot be reached.")],
    quiz=[("A rogue DHCP server is on Fa0/3. Which feature stops its offers?", ["Port security", "DHCP snooping with Fa0/3 untrusted", "BPDU Guard", "DAI alone"], 1, "Server messages on untrusted ports are dropped."),
      ("Which violation mode drops, logs and counts but keeps the port up?", ["protect", "restrict", "shutdown", "sticky"], 1, "protect drops silently; shutdown err-disables."),
      ("DHCP snooping is on. Does it stop ARP spoofing by itself?", ["Yes", "No, it only builds the table DAI uses", "Only on trunks", "Only with option 82"], 1, "DAI does the ARP checking."),
      ("Which protocol encrypts the whole AAA payload?", ["RADIUS", "TACACS+", "SNMPv2c", "Telnet"], 1, "RADIUS encrypts only the password."),
      ("With <code>aaa authentication login default group tacacs+ local</code>, the server rejects a password. What happens?", ["The local database is tried", "Login fails", "The router reloads", "RADIUS is tried"], 1, "Fallback only happens when the server is unreachable."),
      ("An attacker sends frames from thousands of random MACs. What is this and what limits it?", ["ARP spoofing, DAI", "CAM flooding, port security", "VLAN hopping, native VLAN change", "DHCP starvation, NTP"], 1, "Port security caps MACs per port.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.12: lock down the access layer and centralise logins", time="60 minutes",
      needs=PT_NEEDS + " Devices: 1 x 2960, 1 x ISR4331, 3 x Server-PT (Server-DHCP, Rogue-Server, Server-AAA), 3 x PC-PT. All SW1 user ports in VLAN 10.",
      topo=fig(TOPO12, "Server-DHCP on SW1 Fa0/24, PC1 Fa0/1, PC2 Fa0/2, Rogue-Server Fa0/3, Admin-PC Fa0/10, SW1 Gi0/1 to R1 Gi0/0/0, R1 Gi0/0/1 to Server-AAA.", "Lab topology"),
      addr=[["R1", "Gi0/0/0 / Gi0/0/1", "192.168.10.1/24 / 10.0.0.1/24", ""], ["SW1", "VLAN 10", "192.168.10.2/24", "gateway 192.168.10.1"], ["Server-DHCP", "Fa0", "192.168.10.5/24", "pool from .100, gateway .1"],
            ["Rogue-Server", "Fa0", "192.168.10.6/24", "pool from .200, gateway .6 (the bad gateway)"], ["Server-AAA", "Fa0", "10.0.0.20/24", "gateway 10.0.0.1, TACACS+ and RADIUS"], ["Admin-PC", "Fa0", "192.168.10.50/24", "static"]],
      steps=[("See the problem", "<p>With no protection, release and renew DHCP on PC1 and PC2 a few times (IP Configuration, switch to Static and back to DHCP). Some leases may come from the rogue server: a .200 address with gateway .6.</p>"),
        ("DHCP snooping", ios(["SW1(config)# ip dhcp snooping", "SW1(config)# ip dhcp snooping vlan 10", "SW1(config)# no ip dhcp snooping information option", "SW1(config)# interface Fa0/24", "SW1(config-if)# ip dhcp snooping trust", "SW1(config)# interface range Fa0/1 - 10", "SW1(config-if-range)# ip dhcp snooping limit rate 10"], "Snooping") + "<p>Renew on the PCs: only the real server's addresses should appear now.</p>"),
        ("Dynamic ARP Inspection", ios(["SW1(config)# ip arp inspection vlan 10", "SW1(config)# interface Fa0/24", "SW1(config-if)# ip arp inspection trust", "SW1(config)# interface Gi0/1", "SW1(config-if)# ip arp inspection trust"], "DAI") + "<p>On real gear, Admin-PC with its static address would also need trust or an ARP ACL.</p>"),
        ("Port security", ios(["SW1(config)# interface range Fa0/1 - 2", "SW1(config-if-range)# switchport mode access", "SW1(config-if-range)# switchport access vlan 10", "SW1(config-if-range)# switchport port-security", "SW1(config-if-range)# switchport port-security maximum 2", "SW1(config-if-range)# switchport port-security mac-address sticky", "SW1(config-if-range)# switchport port-security violation restrict", "SW1(config)# interface Fa0/3", "SW1(config-if)# switchport mode access", "SW1(config-if)# switchport port-security", "SW1(config-if)# switchport port-security violation shutdown"], "Port security") + "<p>Put a hub on Fa0/3 with two devices behind it, or swap the device on the port, and send traffic to trigger the violation.</p>"),
        ("AAA on R1", "<p>On Server-AAA, Services, AAA: add client R1 (10.0.0.1, key of your choice, type TACACS) and a user.</p>" + ios(["R1(config)# username backup secret <a long local password>", "R1(config)# tacacs-server host 10.0.0.20 key <the key>", "R1(config)# aaa new-model", "R1(config)# aaa authentication login default group tacacs+ local", "R1(config)# line vty 0 4", "R1(config-line)# login authentication default", "R1(config-line)# transport input ssh"], "AAA") + "<p>SSH from Admin-PC with the server account. Then turn off the AAA service on the server and confirm the backup account still works. Optional: repeat with <code>radius-server host</code> and <code>group radius local</code>.</p>"),
        ("Verify", ios(["SW1# show ip dhcp snooping", "SW1# show ip dhcp snooping binding", "SW1# show ip arp inspection vlan 10", "SW1# show port-security", "SW1# show port-security interface Fa0/1", "SW1# show interfaces status err-disabled", "SW1# show running-config | include sticky", "R1# show users"], "Verify"))],
      verify="PCs only get .100 and up after snooping; the binding table lists PC1 and PC2; show port-security shows Fa0/1 and Fa0/2 with maximum 2 and Fa0/3 err-disabled after the violation; SSH to R1 works with the server account and, with the server off, with the backup account.",
      limits=["DHCP snooping works on the 2960 in Packet Tracer, but the binding table output can be sporadic, per Wendell Odom's CCNA lab notes for PT 8.0 (certskills.com). The same notes say it could be configured on the 3650 but only worked on 2960s in their testing.",
              "Dynamic ARP Inspection: per the same source, Packet Tracer 8.0 accepts the DAI commands but does not actually filter bad ARP, and may show the VLAN as inactive. Treat DAI as configuration practice, not a working defence demo. Whether newer builds behave better is UNVERIFIED.",
              "Port security works on the 2960 in Packet Tracer in the outline author's experience. AAA with TACACS+ and RADIUS against Server-PT is supported in that experience too; the newer named syntax (<code>tacacs server NAME</code>) is UNVERIFIED, so this lab uses <code>tacacs-server host</code>. <code>show aaa servers</code> is also UNVERIFIED.",
              "IPsec VPN configuration is outside CCNA scope and Packet Tracer's depth of support is UNVERIFIED, so VPNs stay conceptual.", PT_GENERIC]),
    takeaways=["Name the threat, the vulnerability, the exploit and the mitigation.", "Port security caps MACs per port; default is 1 MAC and shutdown.", "DHCP snooping trusts only server-facing ports and builds the binding table.",
      "DAI uses that table to drop spoofed ARP.", "AAA centralises logins; keep a rarely used local fallback.", "MFA and awareness are part of network security."])

# ------------------------------------------------------------------ 3.13
GI24 = [f"GigabitEthernet1/0/{i}" for i in range(1, 25)] + ["Vlan1"]
TOPO13 = topo(760, 320, {"wlc": (380, 40, "wlc", "WLC-2504", "mgmt 192.168.99.10"), "d1": (380, 140, "l3switch", "DSW1", "3650-24PS"),
    "ap1": (160, 220, "ap", "LAP1", "VLAN 99, PoE"), "ap2": (600, 220, "ap", "LAP2", "VLAN 99, PoE"), "srv": (100, 120, "server", "Server-DHCP", "192.168.99.5"),
    "adm": (660, 110, "pc", "Admin-PC", "VLAN 99"), "cl": (380, 290, "phone", "Laptop1, Smartphone1", "wireless, VLAN 50")},
  [("wlc", "d1", "port 1", "Gi1/0/1 trunk", "ln-p"), ("d1", "ap1", "Gi1/0/2", ""), ("d1", "ap2", "Gi1/0/3", ""), ("d1", "srv", "Gi1/0/24", ""), ("d1", "adm", "Gi1/0/10", ""), ("ap1", "cl", "", "", "dash"), ("ap2", "cl", "", "", "dash")],
  "Lab 3.13 topology: a WLC-2504 trunked to DSW1, two lightweight APs on PoE access ports in VLAN 99, wireless clients in VLAN 50")

CH24 = svg(760, 170, "".join(
  f'<path d="M{40 + (c - 1) * 50} 130 Q{40 + (c - 1) * 50 + 55} {30 if c in (1, 6, 11) else 70} {40 + (c - 1) * 50 + 110} 130" class="{"ln-g" if c in (1, 6, 11) else "ln"}" stroke-width="{2.5 if c in (1, 6, 11) else 1}" fill="none"/>'
  f'<text x="{40 + (c - 1) * 50 + 55}" y="152" text-anchor="middle" font-size="11.5" class="{"" if c in (1, 6, 11) else "t-m"}">{c}</text>' for c in range(1, 12)) +
  '<text x="380" y="20" text-anchor="middle" font-size="12" class="t-m">Each 20 MHz channel spreads across about five channel numbers, so only 1, 6 and 11 do not overlap</text>',
  "2.4 GHz channels 1 to 11: channels 1, 6 and 11 are highlighted as the non-overlapping set")

CAPWAP = svg(760, 180, ARROWDEF +
  box(30, 60, 160, 60, "s-n", "Client", "joins SSID") + box(300, 60, 160, 60, "s-g", "Lightweight AP", "local mode") + box(570, 60, 160, 60, "s-p", "WLC", "policy, keys, RF") +
  arrow(192, 90, 298, 90) +
  '<rect x="462" y="70" width="106" height="40" rx="20" class="s-a" stroke-width="1.5"/><text x="515" y="88" text-anchor="middle" font-size="11">CAPWAP</text><text x="515" y="102" text-anchor="middle" font-size="10" class="t-m">UDP 5246, 5247</text>' +
  '<text x="380" y="155" text-anchor="middle" font-size="12" class="t-m">Control (5246) is encrypted with DTLS; client data (5247) is tunnelled to the WLC and can be encrypted</text>',
  "A lightweight AP tunnels control and client traffic to the WLC with CAPWAP")

def lesson_ccna_13():
  S = []
  S.append(dict(id="rf", h="Radio basics: bands, channels and names", hi_h="Wi-Fi basics",
    body=f'''<p>Wi-Fi is half duplex radio: on one channel only one device transmits at a time, and everyone else waits. Good design is mostly about giving each area a clean channel.</p>
{fig(CH24, "In the 2.4 GHz band, 20 MHz channels sit 5 MHz apart, so neighbouring channels overlap. Use 1, 6 and 11 for adjacent APs.", "2.4 GHz channels")}
{table(["Band", "Strengths", "Weaknesses"], [
  ["2.4 GHz", "Longer range, passes walls better", "Only three non-overlapping channels, crowded, interference from Bluetooth and microwave ovens"],
  ["5 GHz", "Many more channels, wider channels possible", "Shorter range"],
  ["6 GHz (Wi-Fi 6E and Wi-Fi 7)", "Lots of clean spectrum", "Shortest range; requires WPA3 or Enhanced Open, WPA2 is not allowed"]], "Wi-Fi bands")}
<ul><li><strong>SSID</strong>: the network name users see. <strong>BSSID</strong>: the MAC address of one AP radio for that SSID. <strong>ESS</strong>: one SSID served by many APs, so clients can roam.</li>
<li>More transmit power is not better: it causes co-channel interference and "sticky" clients that cling to a distant AP.</li></ul>''',
    hi="Wi-Fi half duplex radio hai, ek channel pe ek time pe ek hi device bolta hai. 2.4 GHz mein sirf 1, 6 aur 11 non-overlapping. 5 GHz mein zyaada channels, range kam. 6 GHz mein WPA3 zaroori. SSID naam hai, BSSID AP radio ka MAC, ESS ek SSID kai APs pe. Zyaada power achhi nahi."))

  S.append(dict(id="arch", h="Autonomous, lightweight and cloud managed APs", hi_h="AP architectures",
    body=f'''{table(["Architecture", "How it is managed", "Typical use"], [
  ["Autonomous", "Each AP configured on its own", "A home or very small office"],
  ["Lightweight (split MAC)", "APs join a wireless LAN controller (WLC) with CAPWAP; the WLC holds the configuration, security and RF decisions", "Campuses and enterprises"],
  ["Cloud managed", "APs report to a cloud dashboard (for example Cisco Meraki)", "Many small sites with little local IT"]], "AP architectures")}
{fig(CAPWAP, "CAPWAP tunnels run between each lightweight AP and its WLC.", "CAPWAP")}
{table(["AP mode", "What it does"], [["Local", "Default: serves clients, tunnels their traffic to the WLC"], ["FlexConnect", "Serves clients and can switch their traffic locally, useful for branches over a WAN"], ["Monitor", "Only listens: rogue detection, location, no clients"], ["Sniffer", "Captures frames and sends them to an analyser"], ["Rogue detector", "Watches the wired side to spot rogue APs"], ["Bridge / mesh", "Links APs wirelessly"], ["SE-Connect", "Spectrum analysis for interference"]], "Common AP modes")}
<p>Wiring follows from the mode. A <strong>local mode AP</strong> sits on an <strong>access port</strong>, because client VLANs travel inside the CAPWAP tunnel. A <strong>FlexConnect AP</strong> often needs a <strong>trunk</strong>, because it drops client traffic onto local VLANs. The <strong>WLC</strong> connects with a trunk carrying its management and client VLANs, and several WLC ports can be bundled with <strong>LAG</strong>, which on AireOS controllers is a static bundle with no LACP or PAgP negotiation (<code>channel-group N mode on</code> on the switch).</p>''',
    hi="Autonomous AP alag alag configure hote hain. Lightweight APs CAPWAP (UDP 5246 control DTLS ke saath, 5247 data) se WLC se judte hain, config aur security WLC pe. Cloud managed jaise Meraki dashboard se. Local mode AP access port pe, FlexConnect aksar trunk pe, WLC trunk pe. AireOS WLC ka LAG static hai, switch pe mode on."))

  S.append(dict(id="security", h="WPA, WPA2 and WPA3", hi_h="Wi-Fi security",
    body=f'''{table(["", "WPA", "WPA2", "WPA3"], [
  ["Encryption", "TKIP (deprecated)", "AES-CCMP", "AES (CCMP or GCMP)"],
  ["Personal mode", "Pre-shared key", "Pre-shared key (PSK)", "SAE, which resists offline password guessing"],
  ["Enterprise mode", "802.1X", "802.1X with a RADIUS server", "802.1X, with an optional 192-bit mode"],
  ["Protected management frames", "No", "Optional", "Required"]], "Wi-Fi security generations")}
<p><strong>Personal</strong> means everyone shares one passphrase. <strong>Enterprise</strong> means each user or device authenticates individually through 802.1X to a RADIUS server, so one person can be removed without changing everyone's key. A shared PSK is the wrong choice for a large company. <strong>Wi-Fi Enhanced Open</strong> (OWE), certified alongside WPA3, encrypts open guest networks without a password.</p>
{attack("<p>The evil twin: in a cafe, airport or railway station, an attacker broadcasts the same SSID as the real free Wi-Fi, sometimes with a fake login page asking for a phone number, OTP or card details. Deauthentication frames can knock people off the real network so their devices reconnect to the fake one. Separately, a WPA2 PSK handshake captured over the air can be attacked offline if the passphrase is weak. Inside companies, an employee plugging a cheap AP into a wall port creates a rogue back door.</p>")}
{defend("<p>WPA3 or 802.1X with proper server certificate validation; protected management frames (PMF, 802.11w) to stop forged deauthentication; long passphrases; rogue detection on the WLC plus port security or 802.1X on wall ports; HTTPS only admin access to the WLC from the management VLAN. For users: confirm the network name with staff, never enter OTPs or card details on a Wi-Fi login page, and use mobile data or a trusted VPN for anything sensitive. Hiding the SSID and MAC filtering are not security controls: hidden SSIDs still appear in probe frames, and MACs are easy to copy.</p>")}''',
    hi="WPA TKIP deprecated. WPA2 AES-CCMP, PSK ya 802.1X. WPA3 Personal mein SAE (offline guessing se bachata hai), PMF zaroori. Enterprise mein har user RADIUS se authenticate hota hai. Evil twin: station ya cafe mein same naam ka fake Wi-Fi, login page pe OTP ya card maangta hai. Defence: WPA3/802.1X, PMF, lambe passphrase, rogue detection, aur users kabhi Wi-Fi login page pe OTP na daalein. Hidden SSID aur MAC filtering security nahi hain."))

  S.append(dict(id="gui", h="Building a WLAN in the WLC GUI", hi_h="WLC GUI",
    body=f'''{stepper("WLAN on an AireOS WLC, step by step", "Use Next or the arrow keys. Menu names are from AireOS 8.x; Packet Tracer's WLC may differ.", [
  ("Log in", "<p>Browse to the management address, for example <code>https://192.168.99.10</code>, from a PC in the management VLAN and sign in.</p>"),
  ("Dynamic interface for the clients", "<p><strong>Controller &gt; Interfaces &gt; New</strong>: name it (for example <code>wifi-clients</code>), VLAN 50, IP 192.168.50.10/24, gateway 192.168.50.1, primary DHCP server 192.168.99.5. This is where client traffic leaves the WLC onto the wired network.</p>"),
  ("Create the WLAN", "<p><strong>WLANs &gt; Create New &gt; Go</strong>: type WLAN, profile name and SSID <code>CWM-Staff</code>. On the <strong>General</strong> tab, set Status to Enabled and the interface to <code>wifi-clients</code>.</p>"),
  ("Layer 2 security", "<p><strong>Security &gt; Layer 2</strong>: WPA+WPA2, tick WPA2 Policy with AES encryption, set Authentication Key Management to PSK, and enter an ASCII passphrase of at least 12 characters (the WLC accepts 8 to 63). For Enterprise you would choose 802.1X and point the AAA Servers tab at RADIUS.</p>"),
  ("QoS", "<p><strong>QoS</strong> tab: Platinum for voice, Gold for video, Silver for best effort (the default), Bronze for background traffic.</p>"),
  ("Advanced", "<p><strong>Advanced</strong> tab: session timeout, client exclusion after repeated failures, and the PMF (management frame protection) setting.</p>"),
  ("Apply and check", "<p>Apply, then watch <strong>Wireless &gt; All APs</strong> for joined APs and <strong>Monitor &gt; Clients</strong> for associated clients and their VLAN 50 addresses.</p>")])}''',
    hi="WLC GUI mein: management IP pe login, Controller > Interfaces > New se VLAN 50 ka dynamic interface, WLANs > Create New se SSID, Security > Layer 2 mein WPA2 AES PSK, QoS mein Silver ya voice ke liye Platinum, Advanced mein session timeout aur PMF, phir APs aur clients monitor karo."))

  S.append(dict(id="practice", h="Practise on DSW1", hi_h="DSW1 pe practice",
    body=f'''<p>DSW1 is the 3650 in the lab. Gi1/0/1 goes to the WLC, Gi1/0/2 and Gi1/0/3 to the lightweight APs (powered by PoE), Gi1/0/24 to the DHCP server, which is already an access port in VLAN 99. The WLC GUI part of the lab happens in Packet Tracer.</p>
{ios_sim(dict(id="l313", kind="switch", host="DSW1", ifaces=GI24, up=["GigabitEthernet1/0/1", "GigabitEthernet1/0/2", "GigabitEthernet1/0/3", "GigabitEthernet1/0/24"],
  init={"GigabitEthernet1/0/24": dict(mode="access", av=99, shut=False)}, vlans={"99": "MGMT"},
  poe=[["GigabitEthernet1/0/2", 13.4, "AIR-LAP"], ["GigabitEthernet1/0/3", 13.4, "AIR-LAP"]],
  intro=["DSW1, a Catalyst 3650-24PS. VLAN 99 already exists. Start with enable."],
  missions=[
    dict(t="Create VLAN 50 named WIFI-CLIENTS.", hint="enable, configure terminal, vlan 50, name WIFI-CLIENTS", c=dict(type="vlan", id=50, name="WIFI-CLIENTS")),
    dict(t="Turn on routing on the switch.", hint="exit, ip routing", c=dict(type="run", re=r"^ip routing$")),
    dict(t="Create SVI VLAN 99 with 192.168.99.1/24 and bring it up.", hint="interface vlan 99, ip address 192.168.99.1 255.255.255.0, no shutdown", c=dict(type="run", re=r"^interface Vlan99\n ip address 192\.168\.99\.1 255\.255\.255\.0\n!")),
    dict(t="Create SVI VLAN 50 with 192.168.50.1/24 and relay its DHCP to 192.168.99.5.", hint="interface vlan 50, ip address 192.168.50.1 255.255.255.0, ip helper-address 192.168.99.5, no shutdown", c=dict(type="run", re=r"^interface Vlan50\n ip address 192\.168\.50\.1 255\.255\.255\.0\n ip helper-address 192\.168\.99\.5\n!")),
    dict(t="Local mode APs live on access ports. Make Gi1/0/2 and Gi1/0/3 access ports in VLAN 99 with PortFast.", hint="interface range g1/0/2 - 3, switchport mode access, switchport access vlan 99, spanning-tree portfast", c=dict(type="run", re=r"^interface GigabitEthernet1/0/3\n switchport access vlan 99\n switchport mode access\n spanning-tree portfast")),
    dict(t="Trunk Gi1/0/1 to the WLC, allowing only VLANs 50 and 99.", hint="interface g1/0/1, switchport mode trunk, switchport trunk allowed vlan 50,99", c=dict(type="run", re=r"^interface GigabitEthernet1/0/1\n[^!]*switchport trunk allowed vlan 50,99\n[^!]*switchport mode trunk")),
    dict(t="How many ports are delivering PoE? Type <code>answer N</code>.", hint="do show power inline", c=dict(type="answer", v="2"), ok="Both APs. Without PoE (or a power injector) a lightweight AP simply stays dark."),
    dict(t="Is the SVI for VLAN 50 up? Type <code>answer yes</code> or <code>answer no</code>.", hint="do show ip interface brief", c=dict(type="answer", v="yes"), ok="Yes: VLAN 50 exists and is carried on an up trunk, so the SVI comes up."),
    dict(t="Save.", hint="end, copy running-config startup-config", c=dict(type="saved"))]), "DSW1 console")}''',
    hi="Simulator mein DSW1: VLAN 50, ip routing, VLAN 99 aur 50 ke SVIs, VLAN 50 pe helper-address, AP ports access VLAN 99 portfast ke saath, WLC port trunk 50,99, PoE dekho, save."))

  return dict(
    slug="learn-ccna-wireless-lans", stage=3, n="3.13", minutes=65, level="Intermediate to advanced",
    title="Wireless LANs: RF Basics, WLC and Lightweight APs, WPA2 and WPA3", short="Bands and channels, AP architectures and modes, CAPWAP, WLC GUI WLANs and Wi-Fi security.",
    seo_title="Wireless for CCNA: 2.4 vs 5 GHz, CAPWAP, WLC GUI WLAN, WPA2 vs WPA3, Evil Twin | CyberWithMadhav",
    desc="Free CCNA lesson on wireless LANs: 2.4, 5 and 6 GHz, non-overlapping channels, autonomous, lightweight and cloud APs, AP modes, CAPWAP, switch ports for APs and WLCs, building a WPA2 PSK WLAN in the WLC GUI, and WPA3, with an IOS simulator and Packet Tracer lab.",
    kw="ccna wireless, 2.4 ghz channels 1 6 11, capwap wlc lightweight ap, ap modes flexconnect, wlc gui create wlan, wpa2 vs wpa3 sae, evil twin wifi attack, packet tracer wlc lab, ccna wlan",
    kicker="$ lesson 3.13 --track ccna --domain wireless", hi_title="Wireless LANs",
    lead="Wi-Fi is where most users meet the network, and where many scams meet users. Learn how radio channels work, how controllers run hundreds of access points, how to wire APs and WLCs correctly, how to build a secure WLAN in the controller GUI, and what WPA3 actually fixes.",
    hi_lead="Zyaadatar users network se Wi-Fi pe milte hain, aur kai scams bhi wahin. Channels, WLC, AP wiring, GUI mein WLAN aur WPA3 seekho.",
    goals=["Explain bands, non-overlapping channels, SSID, BSSID and ESS", "Compare autonomous, lightweight and cloud managed APs and common AP modes", "Choose access ports, trunks and LAG correctly for APs and WLCs", "Build a WPA2 PSK WLAN in the WLC GUI", "Compare WPA, WPA2 and WPA3 and defend against evil twins"],
    sections=S,
    cards=[("Non-overlapping 2.4 GHz channels?", "1, 6 and 11."), ("SSID vs BSSID?", "Network name vs one AP radio's MAC for it."), ("CAPWAP ports?", "UDP 5246 control (DTLS) and 5247 data."),
      ("Local mode AP switch port?", "Access port."), ("FlexConnect AP switch port?", "Often a trunk, to switch client VLANs locally."), ("AireOS LAG?", "Static, no LACP or PAgP: mode on."),
      ("WPA3 Personal replaces PSK with?", "SAE."), ("Is PMF required in WPA3?", "Yes.")],
    quiz=[("Three APs cover adjacent areas in 2.4 GHz. Which channels?", ["1, 2, 3", "1, 6, 11", "6, 6, 6", "1, 5, 9"], 1, "The only non-overlapping set in most regions."),
      ("Which protocol connects lightweight APs to a WLC?", ["LWAPP over TCP", "CAPWAP", "SNMP", "STP"], 1, "CAPWAP, UDP 5246 and 5247."),
      ("A local mode AP should be connected to:", ["A trunk", "An access port", "A routed port", "A LAG"], 1, "Client VLANs travel inside the CAPWAP tunnel."),
      ("What does WPA3 Personal use instead of a PSK handshake?", ["TKIP", "SAE", "WEP", "LEAP"], 1, "SAE resists offline guessing."),
      ("Which helps most against an evil twin in a company?", ["Hiding the SSID", "MAC filtering", "802.1X with server certificate validation", "More transmit power"], 2, "Clients verify they are talking to the real network."),
      ("Why is WPA2 PSK a poor choice for a large company?", ["It is unencrypted", "One shared key cannot be revoked per user", "It only works on 2.4 GHz", "It needs a WLC"], 1, "Enterprise mode authenticates each user.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.13: WLC-2504 with lightweight APs and a WPA2 PSK WLAN", time="60 minutes",
      needs=PT_NEEDS + " Devices: 1 x WLC-2504, 1 x 3650-24PS (PoE for the APs; add a power supply in its Physical tab if it stays off), 2 x lightweight APs (model names vary by version, for example LAP-PT or 3702i; UNVERIFIED for your build), 1 x Server-PT, 1 x PC-PT, 1 x Laptop-PT with a wireless module, 1 x Smartphone-PT.",
      topo=fig(TOPO13, "WLC port 1 to DSW1 Gi1/0/1 (trunk). LAP1 Gi1/0/2 and LAP2 Gi1/0/3 (access VLAN 99). Server-DHCP Gi1/0/24 and Admin-PC Gi1/0/10 in VLAN 99.", "Lab topology"),
      addr=[["Management", "VLAN 99", "192.168.99.0/24", "DSW1 SVI .1, WLC .10, DHCP server .5, AP pool from .100"], ["Wireless clients", "VLAN 50", "192.168.50.0/24", "DSW1 SVI .1, WLC dynamic interface .10, client pool"], ["Server-DHCP", "Fa0", "192.168.99.5/24", "pools for VLAN 99 and VLAN 50"]],
      steps=[("DSW1", ios(["DSW1(config)# vlan 50", "DSW1(config-vlan)# name WIFI-CLIENTS", "DSW1(config)# vlan 99", "DSW1(config-vlan)# name MGMT", "DSW1(config)# ip routing", "DSW1(config)# interface Vlan99", "DSW1(config-if)# ip address 192.168.99.1 255.255.255.0", "DSW1(config)# interface Vlan50", "DSW1(config-if)# ip address 192.168.50.1 255.255.255.0", "DSW1(config-if)# ip helper-address 192.168.99.5", "DSW1(config)# interface range Gi1/0/2 - 3", "DSW1(config-if-range)# switchport mode access", "DSW1(config-if-range)# switchport access vlan 99", "DSW1(config-if-range)# spanning-tree portfast", "DSW1(config)# interface Gi1/0/1", "DSW1(config-if)# switchport mode trunk", "DSW1(config-if)# switchport trunk allowed vlan 50,99"], "DSW1")),
        ("DHCP server pools", "<p>On Server-DHCP, Services, DHCP: one pool for 192.168.99.0/24 (gateway .1, start .100) for the APs, and one for 192.168.50.0/24 (gateway .1) for clients.</p>"),
        ("WLC management", "<p>Set the WLC management interface to 192.168.99.10/24, gateway 192.168.99.1, VLAN 99. Whether Packet Tracer expects that VLAN tagged or untagged by default is UNVERIFIED; if the WLC is unreachable, try the other choice to match the switch trunk's native VLAN.</p>"),
        ("WLC GUI", "<p>From Admin-PC, browse to https://192.168.99.10 and log in. Follow the stepper in this lesson: dynamic interface for VLAN 50 (192.168.50.10, gateway .1, DHCP 192.168.99.5), WLAN <code>CWM-Staff</code> on that interface, WPA2 with AES and PSK, a passphrase of at least 12 characters, QoS Silver, enabled.</p>"),
        ("APs and clients", "<p>Wait for both APs to get VLAN 99 addresses and join (Wireless, All APs). On Laptop1 and Smartphone1, connect to <code>CWM-Staff</code> with WPA2-Personal, AES and the passphrase. They should get 192.168.50.x addresses.</p>"),
        ("Discuss", "<p>Without Packet Tracer: what would change for WPA3-Personal (SAE, PMF required) and for WPA3-Enterprise (802.1X against RADIUS)? Where would Platinum QoS be used?</p>"),
        ("Verify", ios(["DSW1# show interfaces trunk", "DSW1# show power inline", "DSW1# show vlan brief", "Laptop1> ipconfig", "Laptop1> ping 192.168.50.1"], "Verify") + "<p>On the WLC: Monitor, Summary for AP and client counts; Monitor, Clients for each client's SSID and address.</p>")],
      verify="Both APs show as registered under Wireless, All APs; Laptop1 and Smartphone1 are associated to CWM-Staff with 192.168.50.x addresses and can ping 192.168.50.1; DSW1 shows PoE on Gi1/0/2 and Gi1/0/3 and a trunk on Gi1/0/1 allowing 50 and 99.",
      limits=["The APs must reach the WLC: here they share its subnet, which avoids needing DHCP option 43 or DNS discovery.",
              "The WLC-2504 GUI exists in Packet Tracer and supports WLAN creation with WPA2 PSK in the outline author's experience, but some menus are greyed out or missing compared with real AireOS. Which ones, per version, is UNVERIFIED.",
              "WPA3 in Packet Tracer is UNVERIFIED and probably unsupported on its end devices and the WLC-2504, so WPA3 is taught as concept here. Rogue detection, PMF settings and LAG on the Packet Tracer WLC are also UNVERIFIED.",
              "Whether Packet Tracer's WLC-2504 offers a CLI for these steps is UNVERIFIED; the GUI is what the exam topics ask for. Some 8.x builds have also offered a WLC-3504 and Meraki devices: UNVERIFIED.", PT_GENERIC]),
    takeaways=["Use channels 1, 6 and 11 in 2.4 GHz, and prefer 5 GHz or 6 GHz where you can.", "Lightweight APs tunnel to a WLC with CAPWAP.", "Local mode AP on an access port; FlexConnect and WLC on trunks; AireOS LAG is static.",
      "Build WLANs in the GUI: interface, SSID, Layer 2 security, QoS, advanced.", "WPA3 brings SAE and mandatory PMF; Enterprise beats a shared key.", "Teach users about evil twins: never type an OTP into a Wi-Fi login page."])

# ------------------------------------------------------------------ 3.14
TOPO14 = topo(760, 250, {"ctl": (130, 60, "server", "Network Controller", "192.168.1.200"), "sw1": (380, 60, "switch", "SW1", "192.168.1.2"), "adm": (130, 190, "pc", "Admin-PC", "192.168.1.50"),
    "r1": (560, 60, "router", "R1", "Gi0/0/0 .1"), "r2": (560, 200, "router", "R2", "Gi0/0/1 10.0.12.2")},
  [("ctl", "sw1", "", ""), ("adm", "sw1", "", ""), ("sw1", "r1", "", "Gi0/0/0"), ("r1", "r2", "Gi0/0/1 .1", "", "ln-p")],
  "Lab 3.14 topology: a Packet Tracer Network Controller, Admin-PC, SW1 and R1 on 192.168.1.0/24, and R2 behind R1 on 10.0.12.0/30")

PLANES = svg(760, 210, ARROWDEF +
  box(40, 20, 680, 50, "s-p", "Management plane", "SSH, SNMP, APIs: how people and tools configure and monitor") +
  box(40, 85, 680, 50, "s-g", "Control plane", "OSPF, STP, ARP: building the tables") +
  box(40, 150, 680, 50, "s-n", "Data plane", "forwarding each packet using those tables"),
  "Three planes inside a network device: management on top, control in the middle, data at the bottom")

SDN = svg(760, 230, ARROWDEF +
  box(230, 10, 300, 46, "s-n", "Apps, scripts, dashboards") + box(230, 92, 300, 50, "s-p", "Controller", "for example Catalyst Center") + box(230, 176, 300, 46, "s-g", "Network devices") +
  arrow(380, 58, 380, 90) + arrow(380, 144, 380, 174) +
  '<text x="400" y="78" font-size="11.5" class="t-m">northbound API (usually REST)</text><text x="400" y="164" font-size="11.5" class="t-m">southbound: NETCONF, RESTCONF, SSH, SNMP, OpenFlow</text>',
  "SDN: applications use the controller's northbound API; the controller talks to devices through southbound interfaces")

JSON14 = '''{
  "response": [
    { "hostname": "R1", "managementIpAddress": "192.168.1.1", "platformId": "ISR4331", "reachable": true, "uptimeDays": 12 },
    { "hostname": "SW1", "managementIpAddress": "192.168.1.2", "platformId": "WS-C2960-24TT-L", "reachable": true, "uptimeDays": 12 },
    { "hostname": "R2", "managementIpAddress": "10.0.12.2", "platformId": "ISR4331", "reachable": false, "uptimeDays": null }
  ],
  "version": "1.0"
}'''
JL14 = dict(json=JSON14, broken=[
  dict(label="Broken 1", json='{\n  "hostname": "R1",\n  "reachable": true,\n}'),
  dict(label="Broken 2", json="{\n  'hostname': 'R1',\n  'reachable': true\n}"),
  dict(label="Broken 3", json='{\n  "hostname": "R1", // the core router\n  "reachable": true\n}'),
  dict(label="Broken 4", json='{\n  hostname: "R1",\n  "reachable": true\n}'),
  dict(label="Broken 5", json='{\n  "hostname": "R1",\n  "reachable": True\n}')],
  qs=[dict(q="The hostname of the second device", v="SW1"), dict(q="R1's management IP address", v="192.168.1.1"), dict(q="Whether R2 is reachable (a boolean)", v=False),
      dict(q="The version string of the reply", v="1.0"), dict(q="R1's uptime in days (a number)", v=12), dict(q="The whole entry for R2 (an object)", v={"hostname": "R2", "managementIpAddress": "10.0.12.2", "platformId": "ISR4331", "reachable": False, "uptimeDays": None})])

def lesson_ccna_14():
  S = []
  S.append(dict(id="why", h="Why automate, and the three planes", hi_h="Automation kyun",
    body=f'''<p>Typing the same NTP server into 300 devices by hand takes a day and produces a few typos. A script or tool does it in minutes, identically, and can report every device whose config has <strong>drifted</strong> from the standard. Automation does not replace network engineers; it removes repetitive work so they can design, review and troubleshoot.</p>
{fig(PLANES, "Separating the planes is what makes controllers possible: the management and some control decisions can move off the box.", "Planes")}
<p><strong>Controller based networking</strong> centralises management (and sometimes control) logic. Examples: Cisco Catalyst Center (formerly DNA Center) for campus, SD-WAN Manager for WAN, and APIC for ACI data centres. Instead of logging into each switch, you describe what you want once and the controller pushes it.</p>''',
    hi="Haath se 300 devices configure karna slow aur galtiyon wala hai; automation same kaam minutes mein, ek jaisa, aur drift bhi pakadta hai. Data plane packets forward karta hai, control plane tables banata hai (OSPF, STP, ARP), management plane se hum configure karte hain (SSH, SNMP, APIs). Controllers jaise Catalyst Center (pehle DNA Center) management ko centralise karte hain."))

  S.append(dict(id="sdn", h="SDN: underlay, overlay, fabric and APIs", hi_h="SDN",
    body=f'''{fig(SDN, "Northbound is where your code talks to the controller. Southbound is how the controller talks to devices.", "SDN layers")}
<ul><li><strong>Underlay</strong>: the physical IP network: links, routing, addresses.</li>
<li><strong>Overlay</strong>: virtual networks built as tunnels on top of the underlay, for example VXLAN.</li>
<li><strong>Fabric</strong>: underlay and overlay managed together as one system.</li></ul>
<p><strong>Virtualisation</strong> runs on the same idea of abstraction. A type 1 hypervisor runs on bare metal (VMware ESXi, Microsoft Hyper-V, KVM); a type 2 runs on top of an operating system (VirtualBox, VMware Workstation). Virtual machines each carry a full operating system; containers share the host's kernel and are lighter. In networking, a <strong>VRF</strong> gives one router several separate routing tables, so different customers or departments can even reuse the same addresses.</p>''',
    hi="Underlay physical IP network hai, overlay uske upar tunnels (jaise VXLAN), fabric dono ek system ki tarah. Northbound API pe apps controller se baat karte hain (usually REST), southbound pe controller devices se (NETCONF, RESTCONF, SSH, SNMP). Type 1 hypervisor bare metal pe, type 2 OS ke upar. Containers host ka kernel share karte hain. VRF ek router mein alag routing tables."))

  S.append(dict(id="rest", h="REST APIs", hi_h="REST APIs",
    body=f'''<p>REST is an architectural style, usually over HTTP: client and server, <strong>stateless</strong> (every request carries everything needed, including authentication), with resources identified by URLs.</p>
{table(["CRUD", "HTTP verb", "Example"], [["Create", "POST", "Add a device to the inventory"], ["Read", "GET", "List devices"], ["Update", "PUT (replace) or PATCH (change part)", "Change a device's location"], ["Delete", "DELETE", "Remove a device"]], "CRUD and HTTP verbs")}
{table(["Code", "Meaning"], [["200 OK", "Success, here is the result"], ["201 Created", "A new resource was made"], ["204 No Content", "Success, nothing to return"], ["400 Bad Request", "Your request is malformed"], ["401 Unauthorized", "Not authenticated (missing or bad credentials or token)"], ["403 Forbidden", "Authenticated, but not allowed"], ["404 Not Found", "No such resource"], ["500 Internal Server Error", "The server failed"]], "HTTP status codes")}
<p>Authentication types: <strong>HTTP Basic</strong> (username and password Base64 encoded, which is encoding not encryption, so HTTPS only), <strong>API keys</strong>, <strong>bearer tokens</strong> (often obtained by first POSTing credentials, then sent in a header on each request), and <strong>OAuth</strong> for delegated access.</p>
{stepper("A typical token flow", "Use Next or the arrow keys. Paths are examples in the style of Cisco's APIC-EM API.", [
  ("1. Ask for a token", "<p><code>POST /api/v1/ticket</code> with a JSON body containing username and password, over HTTPS.</p>"),
  ("2. Receive it", "<p>The reply is <code>200</code> with JSON holding a ticket (token). A wrong password gets a <code>401</code> style error.</p>"),
  ("3. Use it", "<p><code>GET /api/v1/network-device</code> with the token in a header such as <code>X-Auth-Token</code>. No password travels again.</p>"),
  ("4. Read the JSON", "<p>Parse the reply and pick out what you need, for example each device's hostname, as in the reader below.</p>")])}''',
    hi="REST stateless hai, har request mein authentication bhi. Create = POST, Read = GET, Update = PUT ya PATCH, Delete = DELETE. 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 server error. Basic auth sirf Base64 hai, HTTPS zaroori. Token flow: credentials POST karo, token lo, har request header mein token bhejo."))

  S.append(dict(id="json", h="Reading JSON", hi_h="JSON padhna",
    body=f'''<p><strong>JSON</strong> is the most common encoding for API data (XML and YAML are the others you will meet). Its types: an <strong>object</strong> <code>{{ }}</code> of key value pairs, an <strong>array</strong> <code>[ ]</code> of values, a <strong>string</strong> in double quotes, a <strong>number</strong>, <code>true</code> or <code>false</code>, and <code>null</code>. Keys must be strings in double quotes. Standard JSON allows no comments, no single quotes and no trailing commas.</p>
{json_lab(JL14, "JSON reader: an inventory reply")}
<p>The JSON above is illustrative, written for this lesson. A real controller's field names may differ, so read what yours returns.</p>''',
    hi="JSON types: object { }, array [ ], double quotes mein string, number, true/false, null. Keys double quotes mein. Comments, single quotes aur trailing comma allowed nahi. Reader mein broken examples theek karo aur path se values nikaalo."))

  S.append(dict(id="tools", h="Ansible, Terraform and AI", hi_h="Ansible, Terraform aur AI",
    body=f'''{table(["", "Ansible", "Terraform"], [["Style", "Procedural tasks in order, aiming to be idempotent (safe to run twice)", "Declarative: describe the end state"], ["Language", "YAML playbooks", "HCL"], ["How it reaches devices", "Agentless, over SSH or APIs, using modules", "Providers that talk to platform APIs"], ["Dry run", "<code>ansible-playbook --check</code>", "<code>terraform plan</code>, then <code>apply</code>"], ["Remembers", "An inventory of hosts", "A state file of what it created"]], "Ansible compared with Terraform")}
{code(["- name: Set NTP on all routers", "  hosts: routers", "  gather_facts: false", "  tasks:", "    - name: Push the NTP server", "      cisco.ios.ios_config:", "        lines:", "          - ntp server 192.168.1.100"], "Ansible playbook outline (YAML)")}
<p>This uses the <code>ios_config</code> module from the <code>cisco.ios</code> collection; the inventory would put your routers in a <code>routers</code> group with <code>ansible_network_os: cisco.ios.ios</code> and <code>ansible_connection: network_cli</code>. Terraform has providers for Cisco platforms (for example IOS XE); the resource names depend on the provider version, so check its documentation before writing one.</p>
<p><strong>AI and machine learning</strong> in network operations: predictive and ML tools learn a baseline of normal behaviour, flag anomalies and forecast capacity; generative AI drafts configs, summarises logs and answers questions in plain language. It can also be confidently wrong, so everything it produces is reviewed and lab tested like a junior engineer's change.</p>
{attack("<p>A controller GUI or API token is a key to every device at once. Secrets also leak through code: passwords in playbooks, API keys committed to Git, and Terraform state files (which can hold sensitive values) left readable. And automation amplifies mistakes: one bad playbook can break every router in minutes.</p>")}
{defend("<p>HTTPS only, short lived tokens, least privilege roles and MFA on controllers, API access only from admin networks; Ansible Vault or a secrets manager, never secrets in Git, encrypted and access controlled remote state; peer review, <code>--check</code> and <code>plan</code> before every change, staged rollouts, version control and a rollback plan.</p>")}''',
    hi="Ansible agentless hai, SSH pe YAML playbooks, modules aur inventory; idempotent tasks. Terraform declarative HCL, providers, plan phir apply, state file. AI baseline aur anomalies pakadta hai, generative AI config aur log summary draft karta hai, par galat bhi ho sakta hai, review zaroori. Risks: API token chori, Git mein secrets, ek galat playbook sab tod de. Defence: HTTPS, short tokens, MFA, Vault, review aur dry run."))

  return dict(
    slug="learn-ccna-network-automation", stage=3, n="3.14", minutes=60, level="Advanced",
    title="Network Automation and Programmability: Controllers, REST, JSON, Ansible and AI", short="Planes, controllers and SDN, REST verbs and status codes, reading JSON, Ansible, Terraform and AI in operations.",
    seo_title="Network Automation for CCNA: SDN, REST API, JSON, Ansible vs Terraform, AI | CyberWithMadhav",
    desc="Free CCNA lesson on automation and programmability: data, control and management planes, controller based networking and SDN, REST verbs, status codes and authentication, reading JSON, Ansible, Terraform and AI in network operations, with a JSON reader and Packet Tracer controller lab.",
    kw="ccna automation, sdn northbound southbound api, rest api crud http verbs, http status codes 401 403, json data types, ansible vs terraform, catalyst center dna center, packet tracer network controller rest, ccna programmability",
    kicker="$ lesson 3.14 --track ccna --domain automation", hi_title="Network automation",
    lead="The last CCNA topic is the one that changes how you will do all the others. Learn how controllers and APIs replace box by box configuration, read the JSON they return, see where Ansible, Terraform and AI fit, and how to stop automation from becoming the fastest way to break a network.",
    hi_lead="CCNA ka aakhri topic baaki sab karne ka tareeka badal deta hai. Controllers, APIs, JSON, Ansible, Terraform aur AI seekho, safe tareeke se.",
    goals=["Explain why automation helps and name the three planes", "Describe controller based networking and SDN layers and APIs", "Match CRUD to HTTP verbs and read common status codes and auth types", "Read and fix JSON and extract values by path", "Explain what Ansible, Terraform and AI do in network operations, and their risks"],
    sections=S,
    cards=[("Which plane runs OSPF?", "Control plane."), ("Northbound API?", "Apps to controller, usually REST."), ("Southbound examples?", "NETCONF, RESTCONF, SSH, SNMP, OpenFlow."),
      ("Create, read, update, delete verbs?", "POST, GET, PUT or PATCH, DELETE."), ("401 vs 403?", "Not authenticated vs authenticated but not allowed."), ("JSON allows comments?", "No."),
      ("Ansible needs agents?", "No, it is agentless over SSH or APIs."), ("Terraform dry run?", "terraform plan.")],
    quiz=[("Which HTTP verb reads data?", ["POST", "GET", "PUT", "DELETE"], 1, "GET is read."),
      ("A script gets 401 from the controller. Most likely:", ["The URL does not exist", "Missing or invalid credentials or token", "The server crashed", "Success"], 1, "401 means not authenticated."),
      ("Which is valid JSON?", ["{'a': 1}", "{\"a\": 1,}", "{\"a\": true}", "{a: 1}"], 2, "Double quoted keys, lowercase true, no trailing comma."),
      ("Which interface does a controller use to configure devices?", ["Northbound", "Southbound", "Eastbound", "The data plane"], 1, "Southbound faces the devices."),
      ("What makes Ansible different from many tools?", ["It needs an agent on every router", "It is agentless and uses YAML playbooks", "It only works with Terraform", "It replaces routing protocols"], 1, "Agentless over SSH or APIs."),
      ("Generative AI wrote a config for you. What next?", ["Paste it into production", "Review it against vendor docs and test it in a lab first", "Run it twice", "Ask it if it is sure"], 1, "Treat it like an unreviewed change.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.14: talk to the Packet Tracer Network Controller with REST", time="50 minutes",
      needs=PT_NEEDS + " Packet Tracer 8.2 and later include a Network Controller device that, per Cisco's PT FAQ, offers a web GUI and APIs reachable from a browser, Python or Postman. That FAQ page could not be opened directly when this was written (it was read from a search result), so treat the details as UNVERIFIED. Devices: Network Controller, 2 x ISR4331, 1 x 2960, 1 x PC-PT.",
      topo=fig(TOPO14, "Controller, Admin-PC and R1 Gi0/0/0 on SW1. R1 Gi0/0/1 to R2 Gi0/0/1 (10.0.12.0/30).", "Lab topology"),
      addr=[["Controller", "Gi0", "192.168.1.200/24", "gateway 192.168.1.1"], ["R1", "Gi0/0/0 / Gi0/0/1", "192.168.1.1/24 / 10.0.12.1/30", ""], ["R2", "Gi0/0/1", "10.0.12.2/30", "static route to 192.168.1.0/24 via 10.0.12.1"], ["SW1", "VLAN 1", "192.168.1.2/24", "gateway .1"], ["Admin-PC", "Fa0", "192.168.1.50/24", "gateway .1"]],
      steps=[("Prepare the devices", ios(["R1(config)# hostname R1", "R1(config)# ip domain-name cwm.lab", "R1(config)# username admin secret <a long password>", "R1(config)# crypto key generate rsa modulus 2048", "R1(config)# line vty 0 4", "R1(config-line)# login local", "R1(config-line)# transport input ssh", "R2(config)# ip route 192.168.1.0 255.255.255.0 10.0.12.1"], "SSH everywhere (lesson 3.3)") + "<p>Repeat the SSH setup on R2 and SW1.</p>"),
        ("Controller GUI", "<p>From Admin-PC's browser open http://192.168.1.200 (or https, depending on the build), create the admin account, and add R1, R2 and SW1 with their SSH credentials. The section is called something like Provisioning or Discovery; names vary by build and are UNVERIFIED.</p>"),
        ("Compare views", "<p>Read the controller's inventory and topology views and compare them with <code>show cdp neighbors</code> on R1.</p>"),
        ("REST from Admin-PC", "<p>Open Desktop, Programming (Packet Tracer's Python environment). The controller is commonly documented with APIC-EM style endpoints: <code>POST /api/v1/ticket</code> to get a token and <code>GET /api/v1/network-device</code> with an <code>X-Auth-Token</code> header. These paths, the header name and the Python modules available inside Packet Tracer are UNVERIFIED for your build: open the controller's own API documentation page and Packet Tracer's sample programs first, then write the script.</p>"),
        ("Read the reply", "<p>In the JSON you get back, find an object, an array, a string and a number, and write down the path to each device's hostname, as in the JSON reader in this lesson.</p>"),
        ("Paper exercise", "<p>Outside Packet Tracer: write a short Ansible playbook outline that sets the NTP server on all routers (like the one above), then describe the same intent as a Terraform outline. What would <code>--check</code> and <code>terraform plan</code> show you before anything changes?</p>")],
      verify="The controller lists R1, R2 and SW1 as managed and reachable; your script prints a successful (200) reply for the token request and for the device list, and a wrong password gives an authentication error (a 401 style code; the exact code in Packet Tracer is UNVERIFIED).",
      limits=["Ansible, Terraform, NETCONF and RESTCONF do not run inside Packet Tracer. Practise them later on a Linux machine (Stage 2 of this path prepares you).",
              "Packet Tracer's Programming environment supports a subset of Python with its own HTTP helper modules; exact module names are UNVERIFIED, so start from its sample programs.",
              "Field names in a real controller reply may differ from the illustration in this lesson. The AI and machine learning topic has no Packet Tracer lab: as a discussion exercise, take a syslog excerpt and an AI generated root cause, and check whether the logs really support it.", PT_GENERIC]),
    takeaways=["Automation brings speed, consistency and drift detection; engineers still design and review.", "Data, control and management planes; controllers centralise the management side.", "Northbound to the controller, southbound to devices.",
      "REST: POST, GET, PUT or PATCH, DELETE, and know 200, 201, 204, 400, 401, 403, 404, 500.", "JSON: double quotes, no comments, no trailing commas.", "Protect tokens and secrets, dry run every change, and verify anything AI writes."])
