"""Stage 3 (CCNA track) lessons 3.3 and 3.4. Original writing for CyberWithMadhav."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from learn_kit import *
from content.learn_ccna_a import PT_NEEDS, PT_GENERIC

SW24 = [f"FastEthernet0/{i}" for i in range(1, 25)] + ["GigabitEthernet0/1", "GigabitEthernet0/2", "Vlan1"]

MACT = svg(760, 250, ARROWDEF +
  box(300, 90, 160, 56, "s-g", "SW1", "MAC table") +
  "".join(box(x, y, 120, 44, "s-n", n, m, 8) for x, y, n, m in [(20, 20, "PC1 on Fa0/1", "aaaa.0001"), (20, 180, "PC2 on Fa0/2", "aaaa.0002"), (620, 20, "PC3 on Fa0/3", "aaaa.0003"), (620, 180, "PC4 on Fa0/4", "aaaa.0004")]) +
  arrow(142, 46, 298, 104, "ln-p", True) + arrow(462, 104, 618, 46, "ln-g") + '<line x1="462" y1="130" x2="618" y2="196" class="ln" stroke-width="2" stroke-dasharray="3 6"/><line x1="298" y1="130" x2="142" y2="196" class="ln" stroke-width="2" stroke-dasharray="3 6"/>' +
  '<text x="380" y="176" text-anchor="middle" font-size="11.5" class="t-m">1. learns aaaa.0001 is on Fa0/1 (source MAC)</text>' +
  '<text x="380" y="194" text-anchor="middle" font-size="11.5" class="t-m">2. knows the destination: forwards only to Fa0/3</text>' +
  '<text x="380" y="212" text-anchor="middle" font-size="11.5" class="t-m">3. unknown destination or broadcast: floods (dotted)</text>',
  "A switch learns source MACs, forwards known destinations out one port, and floods unknown or broadcast frames to every other port in the VLAN")

TOPO3 = topo(760, 270, {"pc1": (60, 50, "pc", "PC1", ".11"), "pc2": (60, 140, "pc", "PC2", ".12"), "adm": (60, 230, "pc", "Admin-PC", ".50"),
                        "sw1": (270, 140, "switch", "SW1", "VLAN 1 .2"), "sw2": (520, 140, "switch", "SW2", "VLAN 1 .3"),
                        "pc3": (700, 80, "pc", "PC3", ".13"), "pc4": (700, 200, "pc", "PC4", ".14"), "r1": (270, 34, "router", "R1", ".1")},
  [("pc1", "sw1", "", "Fa0/1"), ("pc2", "sw1", "", "Fa0/2"), ("adm", "sw1", "", "Fa0/3"), ("sw1", "sw2", "Gi0/1", "Gi0/1"), ("sw2", "pc3", "Fa0/1", ""), ("sw2", "pc4", "Fa0/2", ""), ("sw1", "r1", "Fa0/24", "Gi0/0/0")],
  "Lab 3.3 topology: SW1 and SW2 joined on Gi0/1, R1 on SW1 Fa0/24, all in 192.168.1.0/24")

def lesson_ccna_3():
  S = []
  S.append(dict(id="mac-learning", h="How a switch learns, forwards, floods and filters", hi_h="Switch kaise seekhta aur forward karta hai",
    body=f'''{fig(MACT, "Every frame teaches the switch where its <em>source</em> lives. The <em>destination</em> decides where it goes: one port if known, every other port in the VLAN if unknown or broadcast.", "MAC learning")}
<ul><li><strong>Learn</strong>: the switch records the source MAC of every incoming frame against the port it arrived on.</li>
<li><strong>Forward</strong>: a known destination MAC goes out only its port. <strong>Filter</strong>: if the destination is on the same port it came in on, the frame is dropped.</li>
<li><strong>Flood</strong>: unknown unicast, broadcast (ff:ff:ff:ff:ff:ff, for example ARP requests) and, by default, multicast go out every port in the VLAN except the one they came in on.</li>
<li><strong>Age</strong>: entries that are not refreshed expire, after 300 seconds by default on Catalyst switches. Many MACs can sit behind one port, for example everything learned through an uplink to another switch.</li></ul>
{attack("<p><strong>MAC flooding</strong> (CAM table overflow): a tool sends thousands of frames with random fake source MACs until the table is full. The switch can no longer learn real addresses, floods traffic like a hub, and the attacker's port now sees other people's frames.</p>")}
{defend("<p>Port security limits how many MACs a port may learn and shuts or restricts the port when the limit is hit (lesson 3.12). Watch logs for MAC flapping, where the same MAC jumps between ports.</p>")}''',
    hi="Switch source MAC se seekhta hai (kaunsa MAC kis port pe), destination MAC se forward karta hai. Unknown ya broadcast frame sab ports pe flood hota hai. Entries 300 second baad expire. MAC flooding attack table bhar deta hai aur switch hub jaisa flood karne lagta hai; port security isko rokta hai."))

  S.append(dict(id="management", h="Managing a switch: SVI, gateway and access methods", hi_h="Switch management",
    body=f'''<p>A Layer 2 switch does not need an IP address to switch frames. It needs one only so <em>you</em> can manage it remotely. That address lives on a virtual interface, the <strong>SVI</strong> (switch virtual interface), such as <code>interface vlan 1</code> or better, a dedicated management VLAN. Because a pure Layer 2 switch does not route, it also needs <code>ip default-gateway</code> to answer admins on other subnets.</p>
{ios(["SW1(config)# interface vlan 1", "SW1(config-if)# ip address 192.168.1.2 255.255.255.0", "SW1(config-if)# no shutdown", "SW1(config-if)# exit", "SW1(config)# ip default-gateway 192.168.1.1"], "Management SVI")}
{table(["Method", "Encrypted?", "Use"], [
  ["Console cable", "local only", "First setup and recovery. Protect it with a login."], ["Telnet (TCP 23)", "No", "Never on production networks."], ["SSH (TCP 22)", "Yes", "The normal way to manage devices."],
  ["HTTP / HTTPS web UI", "only HTTPS", "If you do not use it, turn it off: <code>no ip http server</code> and <code>no ip http secure-server</code>."],
  ["TACACS+ / RADIUS (AAA)", "varies", "Central logins and logging for many devices (lesson 3.12)."], ["Cloud managed", "Yes (TLS)", "Devices managed from a vendor dashboard."]], "Management access options")}
{defend("<p>Keep management on its own VLAN and subnet, reachable only from admin machines, and restrict the VTY lines with an access list (<code>access-class</code>, lesson 3.9). Many attacks on network gear start with a management interface that was reachable from everywhere.</p>")}''',
    hi="Switch ko frames switch karne ke liye IP nahi chahiye; IP sirf management ke liye SVI (interface vlan) pe lagta hai, saath mein ip default-gateway. Telnet cleartext hai, SSH use karo. Web UI use nahi karte toh band karo. Management alag VLAN pe rakho aur access-class se VTY restrict karo."))

  S.append(dict(id="passwords", h="Passwords on Cisco devices: what each type really means", hi_h="Cisco password types",
    body=f'''{table(["In the config", "What it is", "Verdict"], [
  ["<code>enable password cisco</code> (type 0)", "Plain text", "Never use"], ["<code>password 7 0822455D0A16</code> (type 7)", "Scrambled with a public algorithm, made by <code>service password-encryption</code>", "Reversible in a second: hides from shoulder surfers only"],
  ["<code>secret 5 $1$...</code> (type 5)", "MD5 based hash", "Better, but old and fast to crack"], ["<code>secret 8</code> / <code>secret 9</code>", "PBKDF2-SHA256 / scrypt hashes on newer IOS", "Best where your IOS supports them"]], "Cisco password types")}
<p>So: always use <code>enable secret</code> (never <code>enable password</code>), create users with <code>username NAME secret PASSWORD</code>, and still turn on <code>service password-encryption</code> so any remaining line passwords are at least not readable over someone's shoulder. On real IOS 15.3 and later you can choose the strongest hash with <code>enable algorithm-type scrypt secret ...</code>; Packet Tracer support for that is UNVERIFIED.</p>
{type7_decoder()}
{attack("<p>Config files get shared in tickets, emailed to vendors and posted on forums for help. Any type 7 password in them can be decoded instantly, as the widget shows, and weak type 5 hashes can be cracked offline.</p>")}
{defend("<p>Treat a config file as a secret. Strip passwords before sharing, prefer AAA with central accounts and MFA (lesson 3.12), and choose long passphrases over short complex ones: length beats complexity rules, never reuse, and use MFA, certificates or biometrics where possible.</p>")}''',
    hi="enable password ya type 0 plain text hai. Type 7 (service password-encryption) public algorithm hai, ek second mein decode ho jaata hai, widget mein dekho. Type 5 MD5 hash, type 8/9 behtar. Hamesha enable secret aur username ... secret use karo. Config file ko secret samjho, share karne se pehle passwords hatao."))

  S.append(dict(id="ssh", h="SSH only: the full recipe", hi_h="Sirf SSH: poori recipe",
    body=f'''<p>Typing <code>ip ssh version 2</code> alone does nothing useful. SSH needs all of these, in this order:</p>
<ol><li>A hostname that is not the default (<code>hostname SW1</code>) and a domain name (<code>ip domain-name cyberwithmadhav.lab</code>), because the RSA key is named after both.</li>
<li>An RSA key pair: <code>crypto key generate rsa</code>, then answer the modulus question. Version 2 needs at least 768 bits; 2048 is a sensible modern choice.</li>
<li><code>ip ssh version 2</code>.</li><li>A local user: <code>username netadmin secret ...</code>.</li>
<li>VTY lines that use it and refuse Telnet: <code>line vty 0 15</code>, <code>login local</code>, <code>transport input ssh</code>.</li></ol>
<p>Do the whole baseline in the simulator. Passwords here are lab examples; never reuse them anywhere real.</p>
{ios_sim(dict(id="l33", kind="switch", host="Switch", ifaces=SW24, up=["FastEthernet0/1", "FastEthernet0/2", "FastEthernet0/3", "FastEthernet0/24", "GigabitEthernet0/1"],
  cdp=[["SW2", "GigabitEthernet0/1", "S I", "2960", "Gig 0/1"], ["R1", "FastEthernet0/24", "R B S I", "ISR4331", "Gig 0/0/0"]],
  macs=[["1", "0001.6401.0011", "Fa0/1"], ["1", "0001.6401.0012", "Fa0/2"], ["1", "0001.6401.0050", "Fa0/3"], ["1", "0001.6401.0013", "Gi0/1"], ["1", "0001.6401.0014", "Gi0/1"], ["1", "0001.6401.0001", "Fa0/24"]],
  intro=["Switch SW1 from the lab, factory defaults. PCs on Fa0/1 to Fa0/3, SW2 on Gi0/1, R1 on Fa0/24."],
  missions=[
    dict(t="Look at the MAC address table. How many MACs did it learn through Gi0/1? Type <code>answer N</code>.", hint="enable, then show mac address-table", c=dict(type="answer", v="2"), ok="Two: PC3 and PC4 sit behind SW2, so both appear on Gi0/1."),
    dict(t="In global config, name the switch SW1 and stop it treating typos as hostnames.", hint="configure terminal, hostname SW1, no ip domain-lookup", c=dict(type="run", re=r"^no ip domain-lookup$")),
    dict(t="Set a hashed enable password.", hint="enable secret Cwm#Enable2026", c=dict(type="run", re=r"^enable secret 5 ")),
    dict(t="Create the local admin user netadmin with a secret.", hint="username netadmin secret Cwm#Admin2026", c=dict(type="run", re=r"^username netadmin secret 5 ")),
    dict(t="Add a login banner.", hint="banner motd # Authorised access only. Activity is logged. #", c=dict(type="run", re=r"^banner motd ")),
    dict(t="Set the domain name and generate a 2048 bit RSA key.", hint="ip domain-name cyberwithmadhav.lab, then crypto key generate rsa and answer 2048", c=dict(type="cmd", re=r"^crypto key generate rsa")),
    dict(t="Turn on SSH version 2.", hint="ip ssh version 2", c=dict(type="run", re=r"^ip ssh version 2$")),
    dict(t="Make every VTY line use local users and accept SSH only.", hint="line vty 0 15, login local, transport input ssh", c=dict(type="run", re=r"^line vty 5 15\n login local\n transport input ssh")),
    dict(t="Give the switch its management address 192.168.1.2/24 on VLAN 1 and the gateway 192.168.1.1.", hint="interface vlan 1, ip address 192.168.1.2 255.255.255.0, no shutdown, exit, ip default-gateway 192.168.1.1", c=dict(type="run", re=r"^ip default-gateway 192\.168\.1\.1$")),
    dict(t="Shut every unused port, Fa0/4 to Fa0/23.", hint="interface range fa0/4 - 23, shutdown", c=dict(type="run", re=r"^interface FastEthernet0/23\n shutdown")),
    dict(t="Check SSH, then save the configuration.", hint="end, show ip ssh, copy running-config startup-config", c=dict(type="saved"))]), "SW1 baseline")}''',
    hi="SSH ke liye: non-default hostname, domain name, RSA key (2048), ip ssh version 2, local user, aur VTY pe login local + transport input ssh. Simulator mein poora baseline karo: MAC table padho, enable secret, user, banner, SSH, management IP, unused ports shut, aur save."))

  S.append(dict(id="cdp-lldp", h="CDP and LLDP: useful maps, useful to attackers too", hi_h="CDP aur LLDP",
    body=f'''<p><strong>CDP</strong> (Cisco Discovery Protocol) is Cisco proprietary and on by default on Cisco gear. Every 60 seconds each device tells its neighbours its name, model, IOS version, port and management address. <strong>LLDP</strong> (IEEE 802.1AB) does the same across vendors and is usually off on Cisco IOS until you type <code>lldp run</code>.</p>
{ios(["SW1# show cdp neighbors", "Device ID        Local Intrfce   Holdtme    Capability   Platform    Port ID", "SW2              Gig 0/1         150        S I          2960        Gig 0/1", "R1               Fas 0/24        140        R B S I      ISR4331     Gig 0/0/0", "SW1# show cdp neighbors detail", "SW1(config)# lldp run", "SW1# show lldp neighbors"], "Neighbour discovery")}
{attack("<p>Anyone plugged into a user port receives these advertisements: the switch model, its exact IOS version (handy for finding known vulnerabilities), management IPs and VLAN details. Reconnaissance for free.</p>")}
{defend("<p>Keep CDP or LLDP on infrastructure links where they help you, and turn them off on user facing ports: <code>no cdp enable</code> per interface (or <code>no cdp run</code> globally) and <code>no lldp transmit</code> plus <code>no lldp receive</code>.</p>")}''',
    hi="CDP (Cisco, default on) aur LLDP (multi-vendor, Cisco pe default off) neighbours ko naam, model, IOS version, port aur IP batate hain. Admin ke liye map, attacker ke liye free recon. User ports pe band karo (no cdp enable, no lldp transmit/receive), infrastructure links pe rakho."))

  return dict(
    slug="learn-ccna-switching-secure-access", stage=3, n="3.3", minutes=60, level="Beginner to intermediate",
    title="Switching Fundamentals and Secure Device Access", short="MAC learning and flooding, management SVIs, Cisco password types, SSH only access and CDP/LLDP.",
    seo_title="Cisco Switching Basics and SSH Hardening: MAC Table, Passwords, CDP | CyberWithMadhav",
    desc="Free CCNA lesson: how switches learn, forward and flood, management SVIs, Cisco password types (and why type 7 is not encryption), SSH version 2 only, CDP and LLDP, with an IOS simulator and Packet Tracer lab.",
    kw="how a switch learns mac addresses, mac flooding attack, cisco enable secret vs password, type 7 password decode, configure ssh cisco switch, transport input ssh, cdp lldp security, ccna packet tracer ssh lab",
    kicker="$ lesson 3.3 --track ccna --domain access", hi_title="Switching aur secure device access",
    lead="A switch quietly decides where every frame goes, and the way you log in to it decides whether an attacker can too. Learn how MAC tables really work, why most Cisco passwords in old configs are not secret at all, and how to lock management down to SSH only.",
    hi_lead="Switch chupchap decide karta hai har frame kahan jaayega, aur aap usme kaise login karte ho woh decide karta hai attacker bhi kar sakta hai ya nahi. MAC table, Cisco password types aur SSH-only management seekho.",
    goals=["Explain learning, forwarding, filtering, flooding and aging in a MAC table", "Give a switch a management SVI and default gateway", "Choose secure password types and explain why type 7 is reversible", "Configure SSH version 2 only access with local users", "Decide where CDP and LLDP should run"],
    sections=S,
    cards=[("A switch learns from which MAC?", "The source MAC of incoming frames."), ("Default MAC aging on Catalyst?", "300 seconds."), ("Why does a Layer 2 switch need ip default-gateway?", "To reply to admins on other subnets; it does not route."),
      ("Is type 7 encryption?", "No. It is reversible with a public algorithm."), ("Five things SSH needs?", "Hostname, domain name, RSA keys, local user, VTY with login local and transport input ssh."),
      ("Minimum RSA key size for SSH v2?", "768 bits; use 2048."), ("CDP default on Cisco?", "On. LLDP is usually off until lldp run."), ("Stop a typo becoming a DNS lookup?", "no ip domain-lookup")],
    quiz=[("A switch receives a frame for a MAC it has never seen. What does it do?", ["Drops it", "Floods it out every other port in the VLAN", "Sends it to the router", "Asks DHCP"], 1, "Unknown unicast is flooded."),
      ("Which line is safest?", ["enable password Cisco123", "enable secret Cwm#Long-Passphrase-2026", "password 7 0822455D0A16", "no enable"], 1, "enable secret stores a hash; type 7 and plain passwords are reversible."),
      ("You typed <code>ip ssh version 2</code> and SSH still fails. Most likely missing?", ["A banner", "RSA keys or transport input ssh on the VTYs", "An IPv6 address", "VLAN 99"], 1, "Without keys nothing listens; without transport input ssh the VTYs may not accept it."),
      ("Why add <code>no cdp enable</code> on user ports?", ["It speeds up the port", "CDP leaks model, IOS version and addresses to whoever is connected", "It is required for SSH", "It enables PoE"], 1, "Reconnaissance risk."),
      ("An attacker fills the MAC table with fake addresses. Which feature stops it?", ["Port security", "CDP", "Banner motd", "Duplex auto"], 0, "Port security limits learned MACs per port."),
      ("What does <code>service password-encryption</code> really protect against?", ["Offline cracking", "Someone reading the config over your shoulder", "Network sniffing", "Brute force over SSH"], 1, "Type 7 only hides passwords from casual viewing.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.3: baseline hardening and a MAC table study", time="40 minutes",
      needs=PT_NEEDS + " Devices: 2 x 2960-24TT, 1 x ISR4331, 5 x PC-PT. Everything stays in VLAN 1 for now; VLANs arrive in lesson 3.4.",
      topo=fig(TOPO3, "PC1, PC2 and Admin-PC on SW1; PC3 and PC4 on SW2; SW1 Gi0/1 to SW2 Gi0/1; R1 Gi0/0/0 to SW1 Fa0/24.", "Lab topology"),
      addr=[["R1", "Gi0/0/0", "192.168.1.1/24", ""], ["SW1", "VLAN 1", "192.168.1.2/24", "gw 192.168.1.1"], ["SW2", "VLAN 1", "192.168.1.3/24", "gw 192.168.1.1"],
            ["PC1 to PC4", "Fa0", "192.168.1.11 to .14/24", "gw 192.168.1.1"], ["Admin-PC", "Fa0", "192.168.1.50/24", "gw 192.168.1.1"]],
      steps=[("Watch the MAC table fill", ios(["SW1# clear mac address-table dynamic", "SW1# show mac address-table", "! ping PC3 from PC1, then look again", "SW1# show mac address-table"], "MAC table") + "<p>PC3 and PC4 appear against Gi0/1: many MACs behind one port.</p>"),
        ("Baseline SW1 (repeat on SW2 and R1 with their own names and addresses)", ios(["SW1(config)# hostname SW1", "SW1(config)# no ip domain-lookup", "SW1(config)# enable secret Cwm#Enable2026", "SW1(config)# service password-encryption", "SW1(config)# banner motd # Authorised access only. Activity is logged. #", "SW1(config)# username netadmin secret Cwm#Admin2026", "SW1(config)# line console 0", "SW1(config-line)# login local", "SW1(config-line)# exec-timeout 5 0", "SW1(config-line)# exit", "SW1(config)# interface vlan 1", "SW1(config-if)# ip address 192.168.1.2 255.255.255.0", "SW1(config-if)# no shutdown", "SW1(config-if)# exit", "SW1(config)# ip default-gateway 192.168.1.1"], "Baseline")),
        ("SSH only", ios(["SW1(config)# ip domain-name cyberwithmadhav.lab", "SW1(config)# crypto key generate rsa", "How many bits in the modulus [512]: 2048", "SW1(config)# ip ssh version 2", "SW1(config)# line vty 0 15", "SW1(config-line)# login local", "SW1(config-line)# transport input ssh"], "SSH")),
        ("Test from Admin-PC", "<p>In Admin-PC's Command Prompt: <code>ssh -l netadmin 192.168.1.2</code> should log in. Then <code>telnet 192.168.1.2</code> should be refused or closed.</p>"),
        ("Neighbours and unused ports", ios(["SW1# show cdp neighbors", "SW1(config)# lldp run", "SW1# show lldp neighbors", "SW1(config)# interface range Fa0/1 - 3", "SW1(config-if-range)# no cdp enable", "SW1(config-if-range)# interface range Fa0/4 - 23", "SW1(config-if-range)# shutdown"], "CDP and ports")),
        ("Verify and save", ios(["SW1# show ip ssh", "SW1# show ssh", "SW1# show running-config | section line vty", "SW1# show interfaces status", "SW1# copy running-config startup-config"], "Verify"))],
      verify="SSH from Admin-PC works and Telnet fails, show ip ssh reports version 2.0, unused ports show disabled, and the MAC table shows PC3 and PC4 behind Gi0/1.",
      limits=["Some Packet Tracer images accept only <code>line vty 0 15</code> on switches and <code>line vty 0 4</code> on some routers. Use what the device accepts. UNVERIFIED for every model.",
              "An RSA modulus of 2048 is accepted by recent Packet Tracer versions in common lab guides, but this is UNVERIFIED for every image. If rejected, use the largest value offered (at least 1024).",
              "LLDP on Packet Tracer's 2960 and ISR models: UNVERIFIED for every build. <code>login block-for</code> exists in IOS; Packet Tracer support UNVERIFIED.",
              "<code>enable algorithm-type scrypt secret</code> (type 9) is real IOS; Packet Tracer support UNVERIFIED."]),
    takeaways=["Switches learn from source MACs and flood the unknown.", "Management needs an SVI and, on a Layer 2 switch, a default gateway.", "enable secret and username secret; type 7 is not encryption.",
      "SSH needs hostname, domain, keys, a user and transport input ssh.", "CDP and LLDP belong on infrastructure links, not user ports."])

# ------------------------------------------------------------------ 3.4
TAG = svg(760, 190,
  "".join(f'<rect x="{x}" y="40" width="{w}" height="52" rx="6" class="{c}" stroke-width="1.5"/><text x="{x + w / 2}" y="63" text-anchor="middle" font-size="12.5" font-weight="600">{n}</text><text x="{x + w / 2}" y="80" text-anchor="middle" font-size="10.5" class="t-m">{s}</text>'
          for x, w, c, n, s in [(14, 100, "s-n", "Dest MAC", "6 bytes"), (118, 100, "s-n", "Src MAC", "6 bytes"), (222, 150, "s-p", "802.1Q tag", "4 bytes"), (376, 90, "s-n", "EtherType", "2 bytes"), (470, 170, "s-n", "Payload", "46 to 1500 bytes"), (644, 100, "s-n", "FCS", "4 bytes")]) +
  '<path d="M222 96 L120 130 M372 96 L620 130" class="ln-p" stroke-width="1.5" fill="none"/>' +
  "".join(f'<rect x="{x}" y="130" width="{w}" height="42" rx="5" class="s-p" stroke-width="1.2"/><text x="{x + w / 2}" y="150" text-anchor="middle" font-size="11.5" font-weight="600">{n}</text><text x="{x + w / 2}" y="165" text-anchor="middle" font-size="10" class="t-m">{s}</text>'
          for x, w, n, s in [(120, 170, "TPID 0x8100", "16 bits: this frame is tagged"), (294, 90, "PCP", "3 bits: priority"), (388, 60, "DEI", "1 bit"), (452, 168, "VLAN ID", "12 bits: 1 to 4094")]),
  "An Ethernet frame with an 802.1Q tag inserted after the source MAC. The tag carries a 12 bit VLAN ID")

TOPO4 = topo(760, 250, {"s1": (60, 50, "pc", "PC-Staff1", "VLAN 10"), "ph": (60, 130, "phone", "IP-Phone1", "voice 30"), "g1": (60, 210, "pc", "PC-Guest1", "VLAN 20"),
                        "sw1": (260, 130, "switch", "SW1"), "sw2": (500, 130, "switch", "SW2"),
                        "s2": (700, 70, "pc", "PC-Staff2", "VLAN 10"), "g2": (700, 190, "pc", "PC-Guest2", "VLAN 20")},
  [("s1", "sw1", "", "Fa0/2"), ("ph", "sw1", "", "Fa0/3"), ("g1", "sw1", "", "Fa0/12"), ("sw1", "sw2", "Gi0/1", "Gi0/1", "ln-p"), ("sw2", "s2", "Fa0/2", ""), ("sw2", "g2", "Fa0/12", "")],
  "Lab 3.4 topology: staff, voice and guest ports on two switches joined by an 802.1Q trunk")

def lesson_ccna_4():
  S = []
  S.append(dict(id="why-vlans", h="VLANs: separate networks on shared switches", hi_h="VLANs kya hain",
    body=f'''<p>A <strong>VLAN</strong> is a separate broadcast domain carved out of shared switches. Ports in VLAN 10 and ports in VLAN 20 behave as if they were on different switches: broadcasts stay inside their VLAN, and traffic between VLANs must go through a router or Layer 3 switch (lesson 3.6), which is exactly where you can filter it.</p>
<ul><li><strong>Normal range</strong>: 1 to 1005. VLANs 1002 to 1005 are reserved for old FDDI and Token Ring uses. <strong>Extended range</strong>: 1006 to 4094.</li>
<li><strong>VLAN 1</strong> is the default; every port starts there and it cannot be deleted. Good practice is to keep users and management out of it.</li>
<li>Each VLAN normally gets its own IP subnet, so your VLSM plan from lesson 3.2 maps straight onto VLANs.</li></ul>
{table(["VLAN", "Name", "Subnet", "Ports on each switch"], [["10", "STAFF", "192.168.10.0/24", "Fa0/1 to Fa0/10"], ["20", "GUEST", "192.168.20.0/24", "Fa0/11 to Fa0/20"], ["30", "VOICE", "192.168.30.0/24", "voice on Fa0/3"], ["99", "NATIVE", "no hosts", "trunk native VLAN only"], ["999", "PARKING", "no hosts", "Fa0/21 to Fa0/24, shut"]], "The lab's VLAN plan")}
{analogy("<p>VLANs are separate WhatsApp groups on the same phone network. Everyone uses the same towers, but a message to the family group never reaches the office group, and forwarding between groups needs someone (the router) to do it deliberately.</p>")}''',
    hi="VLAN shared switches pe alag broadcast domain hai. VLAN 10 aur 20 ke ports aise behave karte hain jaise alag switches pe hon. Beech ka traffic router se jaata hai, wahi filter karne ka mauka hai. Normal range 1 se 1005, extended 1006 se 4094. VLAN 1 default hai, users ko usse bahar rakho."))

  S.append(dict(id="access-voice", h="Access ports and voice VLANs", hi_h="Access ports aur voice VLAN",
    body=f'''<p>An <strong>access port</strong> belongs to one data VLAN and sends untagged frames, so the PC never knows VLANs exist. It can also carry one <strong>voice VLAN</strong>, so an IP phone and the PC plugged into the phone share one cable: the phone tags its own traffic with the voice VLAN (CDP or LLDP tells it which one), and the PC's traffic stays untagged in the data VLAN.</p>
{ios(["SW1(config)# vlan 10", "SW1(config-vlan)# name STAFF", "SW1(config-vlan)# exit", "SW1(config)# interface range Fa0/1 - 10", "SW1(config-if-range)# switchport mode access", "SW1(config-if-range)# switchport access vlan 10", "SW1(config-if-range)# switchport nonegotiate", "SW1(config-if-range)# interface Fa0/3", "SW1(config-if)# switchport voice vlan 30"], "Access and voice ports")}
<p>If you assign a port to a VLAN that does not exist yet, IOS creates it for you with a message such as <code>% Access VLAN does not exist. Creating vlan 10</code>, named VLAN0010. Name your VLANs anyway; names make <code>show vlan brief</code> readable at 2 a.m.</p>''',
    hi="Access port ek data VLAN ka hota hai aur untagged frames bhejta hai. Voice VLAN se IP phone aur uske peeche ka PC ek hi cable share karte hain: phone apna traffic voice VLAN se tag karta hai. VLAN exist nahi karta toh IOS khud bana deta hai, phir bhi naam do."))

  S.append(dict(id="trunks", h="802.1Q trunks, the native VLAN and allowed lists", hi_h="802.1Q trunks aur native VLAN",
    body=f'''<p>A <strong>trunk</strong> carries many VLANs over one link, usually between switches or to a router. It marks each frame's VLAN by inserting a 4 byte <strong>802.1Q tag</strong>.</p>
{fig(TAG, "The 802.1Q tag sits between the source MAC and the EtherType. Its 12 bit VLAN ID allows VLANs 1 to 4094 (0 and 4095 are reserved).", "802.1Q tag")}
<ul><li>The <strong>native VLAN</strong> is the one VLAN sent <em>untagged</em> on a trunk (VLAN 1 unless you change it). Both ends must agree. A mismatch makes frames leak between VLANs, and CDP reports it with a message like <code>%CDP-4-NATIVE_VLAN_MISMATCH</code>.</li>
<li>The <strong>allowed list</strong> (<code>switchport trunk allowed vlan 10,20,30,99</code>) limits which VLANs cross the trunk. By default, all of them do.</li>
<li>On 2960 class switches only 802.1Q exists, so <code>switchport trunk encapsulation dot1q</code> is not needed (and may be rejected). On 3560 and 3650 class switches you may need it before <code>switchport mode trunk</code>.</li></ul>
{ios(["SW1(config)# interface GigabitEthernet0/1", "SW1(config-if)# switchport mode trunk", "SW1(config-if)# switchport trunk native vlan 99", "SW1(config-if)# switchport trunk allowed vlan 10,20,30,99", "SW1(config-if)# switchport nonegotiate", "SW1# show interfaces trunk"], "Trunk")}''',
    hi="Trunk ek link pe bahut saare VLANs le jaata hai, har frame mein 4 byte ka 802.1Q tag (12 bit VLAN ID) daal ke. Native VLAN untagged jaata hai, dono side same hona chahiye, warna CDP NATIVE_VLAN_MISMATCH bolega. Allowed list se sirf zaroori VLANs bhejo."))

  S.append(dict(id="dtp", h="DTP: when two switches negotiate a trunk", hi_h="DTP negotiation",
    body=f'''<p>Cisco switches can negotiate whether a link becomes a trunk using <strong>DTP</strong> (Dynamic Trunking Protocol). The result depends on the mode at each end:</p>
{table(["", "dynamic auto", "dynamic desirable", "trunk", "access"], [
  ["<b>dynamic auto</b>", "access", "trunk", "trunk", "access"], ["<b>dynamic desirable</b>", "trunk", "trunk", "trunk", "access"],
  ["<b>trunk</b>", "trunk", "trunk", "trunk", "limited connectivity"], ["<b>access</b>", "access", "access", "limited connectivity", "access"]], "DTP results")}
<p>The default on many current Catalyst switches, including the 2960, is <code>dynamic auto</code>, and auto plus auto gives an <em>access</em> link. That surprises people: two new switches cabled together do not trunk until you configure one side. Professionals do not rely on negotiation at all; they hard code every port as access or trunk and turn DTP off with <code>switchport nonegotiate</code>.</p>''',
    hi="DTP se Cisco switches trunk negotiate karte hain. auto + auto = access (isliye do naye switches khud trunk nahi bante), desirable + auto = trunk. Professionals negotiation pe bharosa nahi karte: har port hard code (access ya trunk) aur switchport nonegotiate se DTP band."))

  S.append(dict(id="vlan-hopping", h="VLAN hopping and how to stop it", hi_h="VLAN hopping",
    body=f'''{attack("<p><strong>Switch spoofing</strong>: a laptop that speaks DTP talks a user port left in <code>dynamic</code> mode into becoming a trunk, and suddenly receives every VLAN. <strong>Double tagging</strong>: an attacker in the trunk's native VLAN sends a frame with two tags; the first switch strips the outer (native) tag and forwards the frame, and the next switch reads the inner tag and delivers it into another VLAN. Double tagging only works from the native VLAN and only one way, but that is enough to send attack traffic into a protected VLAN.</p>")}
{defend("<p>The standard defences, all of which you configure in this lesson's lab:</p><ul><li>User ports: <code>switchport mode access</code> plus <code>switchport nonegotiate</code>.</li><li>Trunks: <code>switchport mode trunk</code> plus <code>switchport nonegotiate</code>, and only the needed VLANs allowed.</li><li>Native VLAN set to an unused VLAN that no host uses (VLAN 99 here), and no users in VLAN 1.</li><li>Unused ports moved to a parking VLAN and shut.</li><li>Where the platform supports it, tag the native VLAN too (<code>vlan dot1q tag native</code>); Packet Tracer support for that is UNVERIFIED and likely missing on the 2960 image.</li></ul>")}
<p>Practise the whole SW1 configuration in the simulator, then build both switches in Packet Tracer.</p>
{ios_sim(dict(id="l34", kind="switch", host="SW1", ifaces=SW24, up=["FastEthernet0/2", "FastEthernet0/3", "FastEthernet0/12", "GigabitEthernet0/1"],
  cdp=[["SW2", "GigabitEthernet0/1", "S I", "2960", "Gig 0/1"]],
  intro=["SW1 from the lab: a 2960 with factory VLAN settings. Staff PC on Fa0/2, phone on Fa0/3, guest PC on Fa0/12, SW2 on Gi0/1."],
  missions=[
    dict(t="Create VLAN 10 named STAFF.", hint="enable, configure terminal, vlan 10, name STAFF", c=dict(type="vlan", id=10, name="STAFF")),
    dict(t="Create VLAN 20 GUEST, 30 VOICE, 99 NATIVE and 999 PARKING.", hint="vlan 20, name GUEST, and so on", c=dict(type="vlan", id=999, name="PARKING")),
    dict(t="Make Fa0/1 to Fa0/10 static access ports in VLAN 10 with DTP off.", hint="interface range fa0/1 - 10, switchport mode access, switchport access vlan 10, switchport nonegotiate", c=dict(type="run", re=r"^interface FastEthernet0/10\n switchport access vlan 10\n switchport mode access\n switchport nonegotiate")),
    dict(t="Add voice VLAN 30 on Fa0/3.", hint="interface fa0/3, switchport voice vlan 30", c=dict(type="run", re=r"^interface FastEthernet0/3\n[^!]*switchport voice vlan 30")),
    dict(t="Guest ports Fa0/11 to Fa0/20: access VLAN 20, DTP off.", hint="interface range fa0/11 - 20 ...", c=dict(type="run", re=r"^interface FastEthernet0/20\n switchport access vlan 20\n switchport mode access\n switchport nonegotiate")),
    dict(t="Park and shut Fa0/21 to Fa0/24 in VLAN 999.", hint="interface range fa0/21 - 24, switchport mode access, switchport access vlan 999, shutdown", c=dict(type="run", re=r"^interface FastEthernet0/24\n switchport access vlan 999\n switchport mode access\n shutdown")),
    dict(t="Before touching Gi0/1, check what DTP negotiated. What is its Operational Mode? Type <code>answer MODE</code> (one word).", hint="do show interfaces g0/1 switchport", c=dict(type="answer", v=["access", "static access"]), ok="dynamic auto on both ends gives an access link, not a trunk."),
    dict(t="Hard code Gi0/1 as a trunk: native VLAN 99, allowed 10,20,30,99, DTP off.", hint="interface g0/1, switchport mode trunk, switchport trunk native vlan 99, switchport trunk allowed vlan 10,20,30,99, switchport nonegotiate", c=dict(type="run", re=r"^interface GigabitEthernet0/1\n switchport trunk native vlan 99\n switchport trunk allowed vlan 10,20,30,99\n switchport mode trunk\n switchport nonegotiate")),
    dict(t="Verify the trunk.", hint="do show interfaces trunk", c=dict(type="cmd", re="^show interfaces trunk$"))]), "SW1 VLANs and trunk")}''',
    hi="Switch spoofing: DTP wala laptop dynamic port ko trunk bana deta hai aur saare VLANs dekh leta hai. Double tagging: native VLAN se do tags wala frame doosre VLAN mein pahunch jaata hai. Bachav: user ports access + nonegotiate, trunks trunk + nonegotiate + allowed list, native VLAN unused (99), VLAN 1 mein users nahi, unused ports parking VLAN mein shut."))

  return dict(
    slug="learn-ccna-vlans-trunks", stage=3, n="3.4", minutes=60, level="Intermediate",
    title="VLANs and Trunks: 802.1Q, Native VLAN, DTP, Voice VLAN", short="VLAN design, access and voice ports, 802.1Q trunks, DTP results and VLAN hopping defences.",
    seo_title="VLANs and Trunks for CCNA: 802.1Q, Native VLAN, DTP, VLAN Hopping | CyberWithMadhav",
    desc="Free CCNA lesson: create VLANs, access and voice ports, 802.1Q trunks with a safe native VLAN and allowed list, the DTP result table, and switch spoofing and double tagging defences, with an IOS simulator and Packet Tracer lab.",
    kw="vlan tutorial ccna, 802.1q trunk native vlan, dtp dynamic auto desirable table, switchport nonegotiate, voice vlan configuration, vlan hopping double tagging defence, packet tracer vlan trunk lab",
    kicker="$ lesson 3.4 --track ccna --domain access", hi_title="VLANs aur trunks",
    lead="VLANs are the first real security boundary inside a network: guests on one side, staff on another, phones in their own lane. Build them, join switches with trunks that cannot be talked into leaking, and understand the two classic VLAN hopping tricks well enough to shut them down.",
    hi_lead="VLANs network ke andar pehli asli security boundary hain: guests ek taraf, staff doosri, phones apni lane mein. Unhe banao, switches ko safe trunks se jodo, aur VLAN hopping ke dono tricks samajh ke band karo.",
    goals=["Create normal range VLANs and assign data and voice access ports", "Build 802.1Q trunks with a non default native VLAN and an allowed list", "Predict the result of each DTP mode pair and switch DTP off", "Explain switch spoofing and double tagging and apply the standard defences"],
    sections=S,
    cards=[("Normal VLAN range?", "1 to 1005 (1002 to 1005 reserved). Extended: 1006 to 4094."), ("Size of the 802.1Q tag?", "4 bytes, with a 12 bit VLAN ID."),
      ("What is the native VLAN?", "The VLAN sent untagged on a trunk. Both ends must match."), ("auto plus auto gives?", "An access link."),
      ("Turn DTP off?", "switchport nonegotiate"), ("Defence against double tagging?", "Native VLAN unused by any host, no users in VLAN 1, tag native where supported."),
      ("Voice VLAN command?", "switchport voice vlan 30"), ("Where do trunk ports appear in show vlan brief?", "They do not. Use show interfaces trunk.")],
    quiz=[("Two new 2960s with default settings are cabled together. What forms?", ["A trunk", "An access link", "An EtherChannel", "Nothing"], 1, "dynamic auto on both ends never starts negotiation."),
      ("What does the native VLAN carry?", ["Tagged voice traffic", "Untagged frames on a trunk", "Only management traffic", "Nothing"], 1, "Frames in the native VLAN cross the trunk untagged."),
      ("Which pair of commands hardens a user port?", ["switchport mode trunk + nonegotiate", "switchport mode access + switchport nonegotiate", "switchport mode dynamic desirable", "no shutdown + cdp enable"], 1, "Static access and no DTP stops switch spoofing."),
      ("Double tagging works only when the attacker is in which VLAN?", ["Voice VLAN", "The trunk's native VLAN", "VLAN 4094", "Any VLAN"], 1, "The outer tag must match the native VLAN to be stripped."),
      ("PCs in VLAN 10 on SW1 and SW2 cannot talk. The trunk is up. First thing to check?", ["The banner", "That VLAN 10 is in the trunk's allowed list and exists on both switches", "DNS", "The router's NAT"], 1, "A VLAN must exist and be allowed on the trunk."),
      ("Why move unused ports to a parking VLAN and shut them?", ["To save power only", "So a device plugged in lands nowhere useful and the port stays off", "It is required by DTP", "To enable PoE"], 1, "Defence in depth for physical access.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.4: two switch VLANs with a hardened trunk", time="40 minutes",
      needs=PT_NEEDS + " Devices: 2 x 2960-24TT, 4 x PC-PT, and optionally 1 x IP Phone (7960).",
      topo=fig(TOPO4, "Staff, phone and guest ports on SW1, staff and guest ports on SW2, and an 802.1Q trunk between their Gi0/1 ports.", "Lab topology"),
      addr=[["PC-Staff1", "Fa0", "192.168.10.11/24", "VLAN 10, no gateway yet"], ["PC-Staff2", "Fa0", "192.168.10.12/24", "VLAN 10"], ["PC-Guest1", "Fa0", "192.168.20.11/24", "VLAN 20"], ["PC-Guest2", "Fa0", "192.168.20.12/24", "VLAN 20"]],
      steps=[("Create the VLANs on both switches", ios(["SW1(config)# vlan 10", "SW1(config-vlan)# name STAFF", "SW1(config-vlan)# vlan 20", "SW1(config-vlan)# name GUEST", "SW1(config-vlan)# vlan 30", "SW1(config-vlan)# name VOICE", "SW1(config-vlan)# vlan 99", "SW1(config-vlan)# name NATIVE", "SW1(config-vlan)# vlan 999", "SW1(config-vlan)# name PARKING"], "VLANs")),
        ("Access, voice and parking ports", ios(["SW1(config)# interface range Fa0/1 - 10", "SW1(config-if-range)# switchport mode access", "SW1(config-if-range)# switchport access vlan 10", "SW1(config-if-range)# switchport nonegotiate", "SW1(config-if-range)# interface Fa0/3", "SW1(config-if)# switchport voice vlan 30", "SW1(config-if)# interface range Fa0/11 - 20", "SW1(config-if-range)# switchport mode access", "SW1(config-if-range)# switchport access vlan 20", "SW1(config-if-range)# switchport nonegotiate", "SW1(config-if-range)# interface range Fa0/21 - 24", "SW1(config-if-range)# switchport mode access", "SW1(config-if-range)# switchport access vlan 999", "SW1(config-if-range)# shutdown"], "Ports")),
        ("See what DTP did by default", ios(["SW1# show interfaces Gi0/1 switchport"], "DTP") + "<p>Read Administrative Mode and Operational Mode before you change anything.</p>"),
        ("Harden the trunk (both switches)", ios(["SW1(config)# interface Gi0/1", "SW1(config-if)# switchport mode trunk", "SW1(config-if)# switchport trunk native vlan 99", "SW1(config-if)# switchport trunk allowed vlan 10,20,30,99", "SW1(config-if)# switchport nonegotiate"], "Trunk")),
        ("Test", "<p>PC-Staff1 pings PC-Staff2: it works. PC-Staff1 pings PC-Guest2: it fails, because they are in different VLANs and subnets and there is no router yet (lesson 3.6).</p>"),
        ("Break it on purpose", "<p>On SW2 only, set <code>switchport trunk native vlan 1</code>. Watch the console for the native VLAN mismatch message, then set it back to 99.</p>"),
        ("Verify", ios(["SW1# show vlan brief", "SW1# show interfaces trunk", "SW1# show interfaces Gi0/1 switchport", "SW1# show interfaces Fa0/3 switchport"], "Verify"))],
      verify="show interfaces trunk shows Gi0/1 in mode on, 802.1q, native VLAN 99 and allowed 10,20,30,99; staff PCs reach each other across the trunk; guests cannot reach staff.",
      limits=["Packet Tracer does not let you craft double tagged frames or DTP attacks, so the hopping attacks stay theory here. That is fine for a defence first course.",
              "<code>vlan dot1q tag native</code> (tagging the native VLAN) is UNVERIFIED in Packet Tracer and likely not supported on the 2960 image.",
              "The exact text of the CDP native VLAN mismatch message in Packet Tracer is UNVERIFIED; on real IOS it reads like <code>%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on ...</code>.", PT_GENERIC]),
    takeaways=["A VLAN is a broadcast domain, usually one subnet.", "Access ports are untagged; trunks tag with 802.1Q except the native VLAN.", "auto plus auto is an access link; hard code ports and use nonegotiate.",
      "Native VLAN unused, users out of VLAN 1, trunks carry only what they need.", "Park and shut unused ports."])
