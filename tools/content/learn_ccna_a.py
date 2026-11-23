"""Stage 3 (CCNA track) lessons 3.1 and 3.2. Original writing for CyberWithMadhav.
Mapped to Cisco CCNA 200-301 v1.1 exam topics. Packet Tracer notes follow tools' rule: no PT support claim unless verified."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from learn_kit import *

PT_NEEDS = 'Cisco Packet Tracer (free with a Cisco Networking Academy account; version 9.0.1 was the current download on the NetAcad Resource Hub when this lesson was written).'
PT_GENERIC = "Packet Tracer simulates a subset of IOS. If a command here is rejected in your version, note it, skip that step and carry on; the concept still applies to real Cisco gear."

def pt_steps(*steps):
    return list(steps)

# ------------------------------------------------------------------ 3.1
OSI = svg(760, 330, ARROWDEF + "".join(
  box(30, 18 + i * 42, 220, 36, c, f"{7 - i}  {n}", None, 8) for i, (n, c) in enumerate(
    [("Application", "s-p"), ("Presentation", "s-p"), ("Session", "s-p"), ("Transport", "s-g"), ("Network", "s-a"), ("Data link", "s-n"), ("Physical", "s-n")])) +
  box(300, 18, 200, 120, "s-p", "Application", "HTTP, DNS, SSH, DHCP") + box(300, 144, 200, 36, "s-g", "Transport", "TCP, UDP") +
  box(300, 186, 200, 36, "s-a", "Internet", "IPv4, IPv6, ICMP") + box(300, 228, 200, 78, "s-n", "Link (network access)", "Ethernet, Wi-Fi") +
  "".join(f'<text x="560" y="{y}" font-size="13" font-weight="600">{t}</text><text x="560" y="{y + 15}" font-size="11" class="t-m">{s}</text>' for y, t, s in
          [(70, "data", "what the app sends"), (160, "segment / datagram", "TCP / UDP header added"), (202, "packet", "IP header added"), (262, "frame, then bits", "MAC header and trailer, then signal")]) +
  '<text x="140" y="322" text-anchor="middle" font-size="11" class="t-m">OSI: 7 layer teaching model</text><text x="400" y="322" text-anchor="middle" font-size="11" class="t-m">TCP/IP: what actually runs</text>',
  "OSI's seven layers beside the TCP/IP model, with the name of the unit of data at each layer")

HANDSHAKE = svg(700, 230, ARROWDEF +
  box(30, 20, 150, 40, "s-n", "Client", None, 8) + box(520, 20, 150, 40, "s-n", "Server :443", None, 8) +
  '<line x1="105" y1="60" x2="105" y2="220" class="ln" stroke-dasharray="4 4"/><line x1="595" y1="60" x2="595" y2="220" class="ln" stroke-dasharray="4 4"/>' +
  arrow(108, 90, 590, 110, "ln-p") + '<text x="350" y="92" text-anchor="middle" font-size="12" font-weight="600">1. SYN, seq=x</text>' +
  arrow(592, 140, 110, 160, "ln-g") + '<text x="350" y="142" text-anchor="middle" font-size="12" font-weight="600">2. SYN-ACK, seq=y, ack=x+1</text>' +
  arrow(108, 190, 590, 210, "ln-p") + '<text x="350" y="192" text-anchor="middle" font-size="12" font-weight="600">3. ACK, ack=y+1, then data</text>',
  "The TCP three way handshake: SYN, SYN-ACK, ACK, after which data can flow")

TOPO1 = topo(600, 240, {"pc1": (70, 60, "pc", "PC1", "192.168.10.11"), "pc2": (70, 175, "pc", "PC2", "192.168.10.12"),
                        "sw1": (290, 118, "switch", "SW1", "2960-24TT"), "r1": (500, 118, "router", "R1", "ISR4331")},
  [("pc1", "sw1", "Fa0", "Fa0/1"), ("pc2", "sw1", "Fa0", "Fa0/2"), ("sw1", "r1", "Gi0/1", "Gi0/0/0")], "Lab 3.1 topology: two PCs on switch SW1, which connects to router R1")

def lesson_ccna_1():
  S = []
  S.append(dict(id="layers", h="Layers and encapsulation: how data gets wrapped", hi_h="Layers aur encapsulation",
    body=f'''<p>Lesson 1.4 introduced the layers. The CCNA expects you to use them as a tool: when something breaks, you work out which layer is failing and test that layer. Two models describe the same idea.</p>
{fig(OSI, "The seven OSI layers are a teaching and troubleshooting vocabulary. The TCP/IP model (often drawn with four layers, sometimes five with physical split out) describes the protocols that actually run.", "OSI and TCP/IP models")}
<p>As data goes down the stack, each layer adds its own header: the application's data gets a TCP or UDP header (now a <strong>segment</strong> or <strong>datagram</strong>), then an IP header (a <strong>packet</strong>), then an Ethernet header and trailer (a <strong>frame</strong>), and finally the physical layer turns it into electrical, light or radio signals (<strong>bits</strong>). The receiver strips the headers in reverse. That is <strong>encapsulation</strong> and <strong>de-encapsulation</strong>.</p>
<ul><li>A switch normally reads up to Layer 2 (MAC addresses in the frame).</li><li>A router reads up to Layer 3 (IP addresses in the packet), and rebuilds a new Layer 2 frame for every hop.</li><li>Firewalls read Layers 3 and 4 (addresses and ports), and next generation firewalls look into Layer 7 (which application, which URL).</li></ul>
{analogy("<p>A letter goes in an envelope with the flat number (port), the envelope goes in a courier bag with the city address (IP), and the bag rides on whatever truck covers the next stretch of road (the frame). Each depot opens only the outer layer it needs and puts the bag on a new truck.</p>")}
{defend("<p>Name the layer before you pick a control: ARP spoofing is a Layer 2 problem (fixed with Dynamic ARP Inspection, lesson 3.12), IP spoofing is Layer 3 (ACLs, lesson 3.9), session hijacking lives in the upper layers (fixed with TLS). The wrong layer means the wrong fix.</p>")}''',
    hi="Data neeche jaate hue har layer apna header lagati hai: segment (TCP), packet (IP), frame (Ethernet), phir bits. Receiver ulta khole. Switch Layer 2 (MAC), router Layer 3 (IP), firewall 3-4 aur NGFW Layer 7 tak dekhta hai. Problem kis layer pe hai, wahi decide karta hai fix kya hoga."))

  S.append(dict(id="devices", h="What each device does", hi_h="Har device ka kaam",
    body=f'''{table(["Device", "Works at", "Job"], [
  ["Layer 2 switch", "L2", "Forwards frames by MAC address inside one network (one VLAN). Learns which MAC lives on which port."],
  ["Router", "L3", "Forwards packets by IP address between networks. Chooses the path using its routing table."],
  ["Layer 3 (multilayer) switch", "L2 and L3", "Switches and routes in hardware. Common as the core or distribution layer inside a campus."],
  ["Access point (AP)", "L1 and L2", "Bridges Wi-Fi clients onto the wired network."],
  ["Wireless LAN controller (WLC)", "management", "Configures and manages many lightweight APs centrally (lesson 3.13)."],
  ["Firewall / NGFW and IPS", "L3 to L7", "Stateful filtering; next generation firewalls add application awareness and intrusion prevention, which blocks known attack patterns inline."],
  ["Endpoints and servers", "all layers", "Laptops, phones, cameras and printers; servers provide services like DNS, DHCP, web and file sharing."],
  ["PoE switch", "L1 and L2", "Power over Ethernet: powers phones, cameras and APs over the data cable."]], "Network device roles")}
<p>You will also meet the classic designs. A <strong>two tier</strong> (collapsed core) campus has access switches connected to a pair of core and distribution switches. A <strong>three tier</strong> campus separates access, distribution and core. Data centres use <strong>spine and leaf</strong>, where every leaf switch connects to every spine, so any two servers are the same number of hops apart. A <strong>SOHO</strong> (small office, home office) network often has one box that is router, switch, AP and firewall at once, and the WAN connects sites to each other and to the cloud.</p>
{attack("<p>Attackers love physical access. A live, unused wall port, or a cheap unmanaged switch someone put under a desk, lets a rogue laptop or a tiny implant join the internal network with no password at all.</p>")}
{defend("<p>Shut unused switch ports and put them in an unused VLAN, lock wiring closets, label everything, and use port security or 802.1X so only known devices get access (lessons 3.4 and 3.12).</p>")}''',
    hi="Switch frames ko MAC se ek network ke andar bhejta hai, router packets ko IP se networks ke beech. L3 switch dono karta hai. AP Wi-Fi ko wired se jodta hai, WLC bahut saare APs manage karta hai, NGFW aur IPS application dekh ke attacks rokte hain. Khula unused port attacker ka entry point hai: band karo."))

  S.append(dict(id="cabling", h="Cabling, duplex and the physical layer", hi_h="Cabling aur duplex",
    body=f'''{table(["Medium", "Typical reach", "Use it for"], [
  ["Copper UTP (Cat5e, Cat6, Cat6A)", "Up to 100 m per run for common Ethernet", "Desks, phones, APs, PoE devices"],
  ["Multimode fibre (MMF)", "Hundreds of metres, depending on speed and fibre grade", "Inside a building, between floors and racks"],
  ["Single-mode fibre (SMF)", "Kilometres", "Between buildings, campuses and service providers"]], "Cable types")}
<p>Fibre does not make a single link magically faster; its advantages are distance and immunity to electrical noise. Old Ethernet needed crossover cables between similar devices, but modern ports use <strong>Auto-MDIX</strong> and work with either cable. In Packet Tracer you still pick the cable type, so the copper straight-through cable is the normal choice between a PC and a switch.</p>
<h3>Half and full duplex</h3>
<p>Hubs created one shared medium where only one device could talk at a time (<strong>half duplex</strong>), and collisions were normal. Switch ports are point to point, so both sides talk at once (<strong>full duplex</strong>) and you should see <strong>zero collisions</strong>. When one side is set to full and the other falls back to half, you get a <strong>duplex mismatch</strong>: the link works but is slow, the half duplex side counts collisions and <em>late collisions</em>, and the full duplex side counts CRC and input errors. The fix is to leave both ends on auto, or set both ends the same.</p>
{analogy("<p>Full duplex is a phone call: both talk and listen at once. Half duplex is a walkie talkie: one talks, the other waits. A mismatch is one person on a phone call and the other holding a walkie talkie, constantly cutting each other off.</p>")}''',
    hi="Copper UTP 100 m tak, multimode fibre building ke andar, single-mode kilometres tak. Fibre ka fayda distance aur noise se bachav hai. Switch ports full duplex hote hain, collisions zero hone chahiye. Duplex mismatch: ek side full, doosri half: link slow, late collisions aur CRC errors. Dono side auto ya same rakho."))

  S.append(dict(id="tcp-udp", h="TCP, UDP and the ports you must know", hi_h="TCP, UDP aur ports",
    body=f'''<p><strong>TCP</strong> is connection oriented. It sets up a session with a three way handshake, numbers every byte, acknowledges what arrived, resends what was lost and uses a window to control speed. <strong>UDP</strong> just sends: no handshake, no recovery, very little overhead. That makes UDP right for voice, video, DNS queries and anything where a late packet is useless anyway.</p>
{fig(HANDSHAKE, "Every TCP connection starts like this. A port that answers SYN with SYN-ACK is open; that is exactly what a port scanner looks for.", "TCP handshake")}
{table(["Port", "Protocol", "Transport", "Note"], [
  ["20, 21", "FTP", "TCP", "Cleartext; prefer SFTP"], ["22", "SSH", "TCP", "Encrypted remote admin"], ["23", "Telnet", "TCP", "Cleartext passwords: disable it"],
  ["25", "SMTP", "TCP", "Mail between servers"], ["53", "DNS", "UDP and TCP", "TCP for large answers and zone transfers"], ["67, 68", "DHCP", "UDP", "Server 67, client 68"],
  ["69", "TFTP", "UDP", "No authentication, used for config and image copies"], ["80, 443", "HTTP, HTTPS", "TCP (HTTP/3 uses UDP 443)", "Web"],
  ["123", "NTP", "UDP", "Time sync, vital for log correlation"], ["161, 162", "SNMP", "UDP", "Monitoring; traps on 162"], ["514", "Syslog", "UDP", "Log messages"]], "Well known ports")}
{attack("<p>An open Telnet port sends usernames and passwords in cleartext, so anyone who can capture traffic on the path can read them. And because a SYN gets a SYN-ACK from any open TCP port, scanners map every listening service on a network in minutes.</p>")}
{defend("<p>Turn off what you do not need, replace cleartext protocols (Telnet, FTP, HTTP management) with SSH, SFTP and HTTPS, and filter management ports so only admin subnets reach them (lessons 3.3 and 3.9).</p>")}''',
    hi="TCP: handshake (SYN, SYN-ACK, ACK), sequence numbers, acknowledgement aur resend. UDP: bas bhej do, fast aur halka: voice, video, DNS. Ports yaad karo: SSH 22, Telnet 23 (cleartext, band karo), DNS 53, DHCP 67/68, TFTP 69, HTTPS 443, NTP 123, SNMP 161/162, syslog 514."))

  S.append(dict(id="interfaces", h="Reading interfaces like an engineer", hi_h="Interfaces padhna",
    body=f'''<p>Two commands answer most physical layer questions. <code>show ip interface brief</code> gives one line per interface with its IP and two status words: <strong>Status</strong> is Layer 1 (is there a working link?) and <strong>Protocol</strong> is Layer 2 (is the data link working?). <code>show interfaces</code> adds duplex, speed and the error counters.</p>
{table(["Status / Protocol", "Means", "Check"], [
  ["up / up", "Working", "Nothing to fix at L1 and L2"], ["administratively down / down", "Someone typed shutdown", "no shutdown"],
  ["down / down", "No physical link", "Cable, the other end, wrong port"], ["up / down", "Link is there but L2 fails", "Encapsulation or keepalive mismatch, a problem at the far end"]], "Interface status")}
<p>In the counters, <strong>CRC</strong> and <strong>input errors</strong> rising usually means a bad cable, interference or a duplex mismatch; <strong>late collisions</strong> on a switched link almost always mean a duplex mismatch. Practise reading them on R1 below. One of its interfaces has a problem.</p>
{ios_sim(dict(id="l31", kind="router", host="Router", ifaces=["GigabitEthernet0/0/0", "GigabitEthernet0/0/1", "GigabitEthernet0/0/2"], up=["GigabitEthernet0/0/0", "GigabitEthernet0/0/1"], init={"GigabitEthernet0/0/1": {"shut": False, "ip": "10.1.1.1", "mask": "255.255.255.252", "x": {"dup": "duplex half", "spd": "speed 100"}}},
  errs={"GigabitEthernet0/0/1": {"crc": 412, "late": 37, "col": 52, "inp": 2210}},
  intro=["Router R1 (ISR4331 style). Gi0/0/0 goes to SW1. Gi0/0/1 goes to a second switch that was configured by hand last week."],
  missions=[
    dict(t="Enter privileged EXEC mode.", hint="enable", c=dict(type="mode", m="priv")),
    dict(t="Enter global configuration mode.", hint="configure terminal (or conf t)", c=dict(type="mode", m="config")),
    dict(t="Name the router R1.", hint="hostname R1", c=dict(type="run", re="^hostname R1$")),
    dict(t="Give Gi0/0/0 the address 192.168.10.1/24.", hint="interface g0/0/0, then ip address 192.168.10.1 255.255.255.0", c=dict(type="run", re=r"^interface GigabitEthernet0/0/0\n ip address 192\.168\.10\.1 255\.255\.255\.0")),
    dict(t="Bring Gi0/0/0 up.", hint="no shutdown", c=dict(type="run", re=r"^interface GigabitEthernet0/0/0\n ip address [^\n]+\n!")),
    dict(t="Back in privileged mode, list every interface with its status.", hint="end, then show ip interface brief", c=dict(type="cmd", re="^show ip interface brief$")),
    dict(t="Read the counters on Gi0/0/1.", hint="show interfaces g0/0/1", c=dict(type="cmd", re=r"^show interfaces <if>$")),
    dict(t="Late collisions plus CRC errors: what is the most likely cause? Type <code>answer duplex</code>, <code>answer cable</code> or <code>answer shutdown</code>.", hint="Late collisions on a switched link point to one specific setting.", c=dict(type="answer", v="duplex"), ok="Duplex mismatch. Set both ends to auto (or both to the same fixed value).")]), "R1 interfaces")}''',
    hi="show ip interface brief: Status = Layer 1, Protocol = Layer 2. administratively down matlab shutdown command, down/down matlab cable ya doosri side. show interfaces mein CRC aur input errors: kharab cable ya duplex mismatch; late collisions: lagbhag hamesha duplex mismatch. Simulator mein R1 configure karo aur problem dhoondho."))

  return dict(
    slug="learn-ccna-network-building-blocks", stage=3, n="3.1", minutes=55, level="Beginner",
    title="Network Building Blocks: OSI, TCP/IP, Devices, Cabling, Interfaces", short="Layers and encapsulation, device roles, topologies, cabling, TCP vs UDP and reading interface counters.",
    seo_title="CCNA Network Fundamentals: OSI vs TCP/IP, Devices, Cabling, TCP UDP | CyberWithMadhav",
    desc="Free CCNA 200-301 lesson: OSI and TCP/IP layers, encapsulation, routers, switches, APs, WLCs and firewalls, copper and fibre, duplex, TCP vs UDP, ports, and show interfaces, with a Packet Tracer lab.",
    kw="ccna network fundamentals, osi vs tcp ip model, encapsulation pdu, router vs switch, duplex mismatch late collisions, tcp vs udp ports, show interfaces crc, packet tracer lab beginner",
    kicker="$ lesson 3.1 --track ccna --domain fundamentals", hi_title="Network building blocks",
    lead="Before VLANs, routing and security, you need a clear picture of what a network is made of: the layers every packet passes through, the job of each box, the cables between them, and how to read an interface when something feels slow.",
    hi_lead="VLANs, routing aur security se pehle saaf picture chahiye: har packet kin layers se guzarta hai, har device ka kaam, unke beech ke cables, aur kuch slow lage toh interface kaise padhein.",
    goals=["Map the OSI layers to the TCP/IP model and name the unit of data at each", "Explain the job of routers, switches, Layer 3 switches, APs, WLCs, firewalls and IPS", "Choose copper, multimode or single-mode fibre for a run", "Compare TCP and UDP and recall the well known ports", "Diagnose duplex and cabling problems from show interfaces"],
    sections=S,
    cards=[("Unit of data at Layer 3?", "Packet. Layer 4 is segment (TCP) or datagram (UDP), Layer 2 is frame."), ("Switch forwards by?", "Destination MAC address, inside one network or VLAN."),
      ("Router forwards by?", "Destination IP address, between networks."), ("Max length of a common copper Ethernet run?", "100 metres."),
      ("Late collisions usually mean?", "A duplex mismatch."), ("TCP handshake?", "SYN, SYN-ACK, ACK."), ("DNS uses?", "Port 53, UDP and TCP."), ("up / down in show ip int brief?", "Layer 1 is fine, Layer 2 is failing.")],
    quiz=[("Which device forwards traffic between different IP networks?", ["Layer 2 switch", "Router", "Access point", "Hub"], 1, "Routers (and Layer 3 switches) route between networks."),
      ("A PC's data gets an IP header. What is it called now?", ["Frame", "Segment", "Packet", "Bit"], 2, "IP adds the Layer 3 header, making a packet."),
      ("Which link should you choose between two buildings 3 km apart?", ["Cat6 copper", "Multimode fibre", "Single-mode fibre", "Wi-Fi"], 2, "Single-mode fibre covers kilometres."),
      ("Which application is best suited to UDP?", ["File download", "Voice call", "Email delivery", "SSH"], 1, "Late voice packets are useless, so retransmission does not help."),
      ("An interface shows <code>administratively down</code>. Fix?", ["Replace the cable", "no shutdown", "Reload the router", "Change the IP"], 1, "Administratively down means it was shut down in the config."),
      ("You see rising CRC errors on one side and late collisions on the other. Most likely cause?", ["Wrong VLAN", "Duplex mismatch", "Wrong IP address", "DNS failure"], 1, "Classic duplex mismatch symptoms.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.1: build, cable and read interfaces", time="30 minutes",
      needs=PT_NEEDS + " Devices: 1 x 2960-24TT switch, 1 x ISR4331 router, 2 x PC-PT, copper straight-through cables.",
      topo=fig(TOPO1, "PC1 and PC2 connect to SW1 on Fa0/1 and Fa0/2; SW1 Gi0/1 connects to R1 Gi0/0/0.", "Lab topology"),
      addr=[["R1", "Gi0/0/0", "192.168.10.1/24", "n/a"], ["PC1", "Fa0", "192.168.10.11/24", "192.168.10.1"], ["PC2", "Fa0", "192.168.10.12/24", "192.168.10.1"]],
      steps=[("Place and cable", "<p>Add the devices and cable them as in the diagram. Watch the link lights: switch ports often show orange for a short time before turning green, because they pass through spanning tree states first (lesson 3.5).</p>"),
        ("Configure R1", ios(["Router> enable", "Router# configure terminal", "Router(config)# hostname R1", "R1(config)# interface GigabitEthernet0/0/0", "R1(config-if)# ip address 192.168.10.1 255.255.255.0", "R1(config-if)# no shutdown", "R1(config-if)# end"], "R1")),
        ("Address the PCs", "<p>On each PC open Desktop, then IP Configuration, and enter the address, mask and gateway from the table.</p>"),
        ("Test and watch the layers", "<p>From PC1's Command Prompt run <code>ping 192.168.10.1</code> and <code>ping 192.168.10.12</code>. Then switch to Simulation mode, filter for ICMP and ARP, and step through one ping. Open a PDU and match each part to a layer: Ethernet header (L2), IP header (L3), ICMP (the payload).</p>"),
        ("Verify", ios(["R1# show ip interface brief", "R1# show interfaces GigabitEthernet0/0/0", "SW1# show interfaces status"], "Verify") + "<p>On PC1: <code>ipconfig</code> and <code>arp -a</code>. The first ping may lose one reply while ARP finds R1's MAC address; that is normal.</p>"),
        ("Force a mismatch and look", ios(["SW1(config)# interface FastEthernet0/1", "SW1(config-if)# duplex half", "SW1(config-if)# speed 10", "SW1(config-if)# end", "SW1# show interfaces FastEthernet0/1"], "Mismatch") + "<p>Read the duplex and speed lines, then set the port back with <code>duplex auto</code> and <code>speed auto</code>.</p>")],
      verify="R1 Gi0/0/0 is up/up with 192.168.10.1, both PCs ping R1 and each other, and you can point to the L2, L3 and ICMP parts of a PDU in Simulation mode.",
      limits=["Packet Tracer does not reliably produce realistic CRC errors or late collisions from a duplex mismatch, so treat step 6 as a where to look exercise, not proof of real error behaviour. UNVERIFIED how the counters react in your version.",
              "Fibre cables exist in Packet Tracer, but the device needs a fibre capable port or module, and module names vary by model. UNVERIFIED per device.", PT_GENERIC]),
    takeaways=["Each layer adds a header; switches read L2, routers L3, NGFWs up to L7.", "Copper to 100 m, multimode in buildings, single-mode for kilometres.",
      "Switched links are full duplex with zero collisions; late collisions mean a duplex mismatch.", "TCP is reliable and ordered, UDP is fast and light.", "show ip interface brief first, show interfaces for the details."])

# ------------------------------------------------------------------ 3.2
VLSM = svg(760, 170,
  '<rect x="20" y="40" width="720" height="56" rx="8" class="s-n" stroke-width="1.5"/>' +
  "".join(f'<rect x="{20 + a * 720 / 256:.1f}" y="40" width="{(b - a) * 720 / 256:.1f}" height="56" rx="6" class="{c}" stroke-width="1.5"/>'
          f'<text x="{20 + (a + b) / 2 * 720 / 256:.1f}" y="64" text-anchor="middle" font-size="12.5" font-weight="600">{n}</text>'
          f'<text x="{20 + (a + b) / 2 * 720 / 256:.1f}" y="82" text-anchor="middle" font-size="10.5" class="t-m">{s}</text>'
          for a, b, c, n, s in [(0, 128, "s-p", "LAN-A /25", ".0 to .127"), (128, 192, "s-g", "LAN-B /26", ".128 to .191"), (192, 224, "s-a", "LAN-C /27", ".192 to .223")]) +
  f'<text x="{20 + 226 * 720 / 256:.1f}" y="118" text-anchor="middle" font-size="10.5" class="t-m">/30 link .224 to .227</text>' +
  f'<rect x="{20 + 224 * 720 / 256:.1f}" y="40" width="{4 * 720 / 256:.1f}" height="56" class="s-r" stroke-width="1"/>' +
  f'<text x="{20 + 242 * 720 / 256:.1f}" y="146" text-anchor="middle" font-size="10.5" class="t-m">free: .228 to .255</text>' +
  '<text x="20" y="28" font-size="12" class="t-m">192.168.50.0/24, biggest subnet first, each starting on its own block boundary</text>',
  "VLSM plan for 192.168.50.0/24: a /25, a /26, a /27 and a /30, placed largest first with no overlap")

TOPO2 = topo(760, 270, {"pca": (60, 70, "pc", "PC-A", ".10/25"), "swa": (190, 70, "switch", "SW-A"), "r1": (360, 120, "router", "R1"),
                        "pcb": (60, 215, "pc", "PC-B", ".140/26"), "swb": (190, 215, "switch", "SW-B"),
                        "r2": (560, 120, "router", "R2"), "swc": (680, 70, "switch", "SW-C"), "pcc": (690, 215, "pc", "PC-C", ".200/27")},
  [("pca", "swa", "", ""), ("swa", "r1", "", "Gi0/0/0"), ("pcb", "swb", "", ""), ("swb", "r1", "", "Gi0/0/2"), ("r1", "r2", "Gi0/0/1", "Gi0/0/1"), ("r2", "swc", "Gi0/0/0", ""), ("swc", "pcc", "", "")],
  "Lab 3.2 topology: R1 serves LAN-A and LAN-B, R2 serves LAN-C, and R1 and R2 share a /30 link")

def lesson_ccna_2():
  S = []
  S.append(dict(id="ipv4", h="IPv4 addresses, masks and prefixes", hi_h="IPv4 address, mask aur prefix",
    body=f'''<p>An IPv4 address is 32 bits, written as four decimal numbers (octets) from 0 to 255. The <strong>mask</strong> says how many of those bits name the network; the rest name the host. <code>255.255.255.0</code> and <code>/24</code> say the same thing: 24 network bits, 8 host bits.</p>
<ul><li><strong>Network address</strong>: all host bits 0. It names the subnet and cannot be given to a host.</li>
<li><strong>Broadcast address</strong>: all host bits 1. A packet to it reaches every host in the subnet.</li>
<li><strong>Usable hosts</strong>: 2<sup>host bits</sup> minus 2. A /24 gives 254, a /30 gives 2 (ideal for router to router links). A /31 gives two usable addresses on point to point links (RFC 3021), and a /32 is a single host.</li>
<li>The <strong>wildcard mask</strong> is the mask inverted (0.0.0.255 for a /24). ACLs and OSPF use it (lessons 3.8 and 3.9).</li></ul>
{subnet_calc("192.168.50.130", 26)}
<p>Classful thinking (Class A, B, C) is history. Any prefix length can be used on any range, which is what <strong>CIDR</strong> (classless inter-domain routing) means.</p>''',
    hi="IPv4 32 bits ka hai. Mask batata hai kitne bits network ke hain: /24 = 255.255.255.0. Sab host bits 0 = network address, sab 1 = broadcast. Usable hosts = 2^host bits minus 2. /30 mein 2 hosts (router links), /31 point-to-point pe 2 (RFC 3021). Calculator mein slider chala ke bits dekho."))

  S.append(dict(id="subnetting", h="Subnetting by hand: the block size method", hi_h="Haath se subnetting: block size method",
    body=f'''<p>You do not need a calculator, and in the exam you will not have one. Use the <strong>interesting octet</strong>, the one where the mask is not 255 or 0.</p>
<ol><li>Find the interesting octet of the mask. For /26 the mask is 255.255.255.<strong>192</strong>.</li>
<li>Block size = 256 minus that value: 256 minus 192 = <strong>64</strong>. Subnets start at 0, 64, 128, 192 in that octet.</li>
<li>Find the block that contains your address. 192.168.50.130 sits in the block starting at <strong>128</strong>.</li>
<li>Network = 192.168.50.128. Broadcast = one less than the next block: 192.168.50.191. Hosts = .129 to .190, which is 62 hosts.</li></ol>
{table(["Prefix", "Mask", "Block size", "Usable hosts"], [["/24", "255.255.255.0", "256 (whole octet)", "254"], ["/25", "255.255.255.128", "128", "126"], ["/26", "255.255.255.192", "64", "62"], ["/27", "255.255.255.224", "32", "30"],
  ["/28", "255.255.255.240", "16", "14"], ["/29", "255.255.255.248", "8", "6"], ["/30", "255.255.255.252", "4", "2"], ["/20", "255.255.240.0", "16 in the third octet", "4094"]], "Prefix cheat sheet")}
<p>Practise with the question button in the calculator above until you can do one in under 30 seconds. When the mask's interesting octet is the third one (for example /20), the same method applies to the third octet and the fourth octet runs from 0 to 255 inside each block.</p>
{analogy("<p>Block size is like seat rows in a cinema of 256 seats. With rows of 64, the rows start at seat 0, 64, 128 and 192. Seat 130 is in the row starting at 128, and that row ends at 191.</p>")}''',
    hi="Interesting octet lo (jo 255 ya 0 nahi). Block size = 256 minus woh value. /26 = 192 to block 64: subnets 0, 64, 128, 192. 192.168.50.130 block 128 mein: network .128, broadcast .191, hosts .129 se .190. Exam mein calculator nahi milta, isliye roz 5 sawaal practice karo."))

  S.append(dict(id="vlsm", h="VLSM: fitting different sized subnets into one block", hi_h="VLSM",
    body=f'''<p>Real networks need subnets of different sizes. <strong>Variable length subnet masking</strong> gives each one only the space it needs. The rule that keeps plans clean: <strong>allocate the biggest subnet first, and start every subnet on a multiple of its own block size.</strong></p>
<p>The lab scenario: you are given 192.168.50.0/24 and need LAN-A with 100 hosts, LAN-B with 50, LAN-C with 20 and one router to router link.</p>
{table(["Subnet", "Needs", "Smallest fit", "Network", "Usable range", "Broadcast"], [
  ["LAN-A", "100", "/25 (126 hosts)", "192.168.50.0", ".1 to .126", ".127"], ["LAN-B", "50", "/26 (62)", "192.168.50.128", ".129 to .190", ".191"],
  ["LAN-C", "20", "/27 (30)", "192.168.50.192", ".193 to .222", ".223"], ["R1 to R2", "2", "/30 (2)", "192.168.50.224", ".225 to .226", ".227"]], "VLSM plan")}
{fig(VLSM, "The same plan drawn as a line of 256 addresses. Going largest first guarantees every block lands on a boundary, and .228 to .255 stay free for growth.", "VLSM line")}
{attack("<p>One flat network where cameras, guest Wi-Fi, staff laptops and servers share a subnet is a gift to an attacker: compromise one cheap camera and you can reach everything directly.</p>")}
{defend("<p>Good subnetting is the foundation of <strong>segmentation</strong>. Separate subnets for guests, IoT, servers, staff and management let ACLs and firewalls limit how far an attacker can move after the first device falls (lessons 3.4 and 3.9).</p>")}''',
    hi="VLSM: har subnet ko utna hi space do jitna chahiye. Rule: sabse bada subnet pehle, aur har subnet apne block size ke multiple pe shuru. 192.168.50.0/24 se: /25 (100 hosts), /26 (50), /27 (20), /30 (link). Alag subnets = segmentation, attacker ek camera hack karke sab tak nahi pahunch sakta."))

  S.append(dict(id="special", h="Private, special and public addresses", hi_h="Private aur special addresses",
    body=f'''{table(["Range", "What it is"], [
  ["10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16", "Private (RFC 1918). Not routed on the internet; reaching the internet needs NAT (lesson 3.10)."],
  ["127.0.0.0/8", "Loopback: the device itself."], ["169.254.0.0/16", "Link-local (APIPA): a client that asked for DHCP and got no answer gives itself one of these."],
  ["100.64.0.0/10", "Shared address space for carrier-grade NAT (RFC 6598). Many Indian mobile and broadband users sit behind it."],
  ["192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24", "Documentation (RFC 5737). Safe for examples, never used on real networks."],
  ["224.0.0.0/4", "Multicast, for example OSPF uses 224.0.0.5 and 224.0.0.6."]], "Special IPv4 ranges")}
<p>Private does not mean secure. It only means internet routers will not carry those addresses; inside your network, a private address is just as reachable as any other. Security comes from filtering and segmentation, not from the address range.</p>
{defend("<p>An APIPA address (169.254.x.x) on a client is a useful clue during an incident: DHCP was unreachable, blocked, or exhausted by a starvation attack (lesson 3.12). Check the DHCP server and the switch path before blaming the client.</p>")}''',
    hi="Private ranges (RFC 1918): 10/8, 172.16/12, 192.168/16, internet pe route nahi hote, NAT chahiye. 169.254 = DHCP nahi mila (APIPA). 100.64/10 = carrier NAT. 192.0.2, 198.51.100, 203.0.113 sirf documentation ke liye. Private ka matlab secure nahi; security filtering aur segmentation se aati hai."))

  S.append(dict(id="ipv6", h="IPv6: writing, shortening and address types", hi_h="IPv6 basics",
    body=f'''<p>IPv6 addresses are 128 bits, written as eight groups of four hex digits. Two rules shorten them: drop the <strong>leading zeros</strong> in any group, and replace <strong>one</strong> run of all-zero groups with <code>::</code>. Using <code>::</code> twice would be ambiguous, so it is allowed only once.</p>
{code(["# full form", "2001:0db8:0000:0000:0000:ff00:0042:8329", "# leading zeros dropped", "2001:db8:0:0:0:ff00:42:8329", "# longest zero run replaced", "2001:db8::ff00:42:8329"], "Shortening an IPv6 address", False)}
{table(["Type", "Prefix", "Notes"], [
  ["Global unicast", "2000::/3", "Routable on the internet, like a public IPv4 address."], ["Unique local", "fc00::/7 (used as fd00::/8)", "Private use inside an organisation."],
  ["Link-local", "fe80::/10", "Every IPv6 interface has one; never routed. Routers use them as next hops and gateways."],
  ["Multicast", "ff00::/8", "One to many. ff02::1 is all nodes, ff02::2 all routers on the link."], ["Anycast", "from the unicast space", "Same address on many devices; the nearest one answers."]], "IPv6 address types")}
<p>There is no broadcast in IPv6. Hosts get addresses statically, by <strong>SLAAC</strong> (the router advertises the /64 prefix and the host builds its own interface ID), by stateless DHCPv6 (SLAAC plus DHCPv6 for options like DNS) or by stateful DHCPv6. With <strong>modified EUI-64</strong>, the interface ID comes from the MAC: split the 48 bit MAC in half, insert <code>FFFE</code> in the middle and flip the seventh bit of the first byte.</p>
{code(["# MAC 0050.56ab.cdef", "0050:56 | ab:cdef  ->  0050:56ff:feab:cdef", "# flip bit 7 of the first byte: 00 becomes 02", "interface ID 0250:56ff:feab:cdef  (written 250:56ff:feab:cdef)"], "EUI-64 worked example", False)}
{attack("<p>Many networks run IPv6 on every laptop without anyone watching it. A rogue device that sends fake Router Advertisements can make clients use it as their default gateway, putting it in the middle of their traffic.</p>")}
{defend("<p>Monitor and filter IPv6 exactly like IPv4, and on switches that support it use RA Guard so only real router ports may send Router Advertisements. RA Guard is beyond the CCNA's depth and is not expected to work in Packet Tracer (UNVERIFIED).</p>")}''',
    hi="IPv6 128 bits, 8 groups hex mein. Leading zeros hatao, aur ek baar :: se zero groups chhota karo. Types: global unicast 2000::/3, unique local fd00::/8, link-local fe80::/10 (har interface pe), multicast ff00::/8. Broadcast nahi hota. SLAAC mein host khud address banata hai; EUI-64 MAC ke beech FFFE daal ke 7th bit flip karta hai. Fake Router Advertisement se attacker gateway ban sakta hai."))

  S.append(dict(id="configure", h="Configure the plan on a router, then check clients", hi_h="Router pe plan configure karo",
    body=f'''<p>Put the VLSM plan onto R1's three interfaces in the simulator, then add IPv6. On real devices and in Packet Tracer the commands are the same.</p>
{ios_sim(dict(id="l32", kind="router", host="R1", ifaces=["GigabitEthernet0/0/0", "GigabitEthernet0/0/1", "GigabitEthernet0/0/2"], up=["GigabitEthernet0/0/0", "GigabitEthernet0/0/1", "GigabitEthernet0/0/2"],
  intro=["R1 from the lab. Gi0/0/0 is LAN-A, Gi0/0/2 is LAN-B and Gi0/0/1 is the /30 link to R2."],
  missions=[
    dict(t="LAN-A: give Gi0/0/0 the first usable address of 192.168.50.0/25 and bring it up.", hint="interface g0/0/0, ip address 192.168.50.1 255.255.255.128, no shutdown", c=dict(type="run", re=r"^interface GigabitEthernet0/0/0\n ip address 192\.168\.50\.1 255\.255\.255\.128\n!")),
    dict(t="LAN-B: Gi0/0/2 gets the first usable address of 192.168.50.128/26.", hint="ip address 192.168.50.129 255.255.255.192", c=dict(type="run", re=r"^interface GigabitEthernet0/0/2\n ip address 192\.168\.50\.129 255\.255\.255\.192$")),
    dict(t="The /30 link: Gi0/0/1 gets 192.168.50.225/30.", hint="ip address 192.168.50.225 255.255.255.252", c=dict(type="run", re=r"^interface GigabitEthernet0/0/1\n ip address 192\.168\.50\.225 255\.255\.255\.252$")),
    dict(t="Turn on IPv6 routing.", hint="ipv6 unicast-routing (global config)", c=dict(type="run", re="^ipv6 unicast-routing$")),
    dict(t="Give Gi0/0/0 the IPv6 address 2001:db8:acad:a::1/64.", hint="interface g0/0/0, ipv6 address 2001:db8:acad:a::1/64", c=dict(type="run", re=r"^ ipv6 address 2001:DB8:ACAD:A::1/64$")),
    dict(t="Check your work: show the connected and local routes.", hint="end, then show ip route", c=dict(type="cmd", re="^show ip route$"))]), "R1 addressing")}
<p>On clients, check what they actually got. Windows: <code>ipconfig /all</code>. Linux: <code>ip addr</code> and <code>ip route</code>. macOS: <code>ifconfig</code>, or <code>networksetup -getinfo Wi-Fi</code> where the service name matches your adapter (it differs between Macs).</p>''',
    hi="Simulator mein R1 ke teeno interfaces pe VLSM plan lagao: /25, /26 aur /30, phir ipv6 unicast-routing aur IPv6 address. show ip route mein C (connected) aur L (local) routes dikhengi. Clients pe ipconfig /all (Windows) ya ip addr (Linux) se check karo."))

  return dict(
    slug="learn-ccna-ip-addressing-subnetting", stage=3, n="3.2", minutes=70, level="Beginner to intermediate",
    title="IP Addressing: IPv4 Subnetting, VLSM, Private Ranges, IPv6 Basics", short="Masks and prefixes, the block size method, VLSM plans, special ranges and IPv6 with a live subnet calculator.",
    seo_title="IPv4 Subnetting, VLSM and IPv6 for CCNA: Calculator and Practice | CyberWithMadhav",
    desc="Free CCNA lesson: IPv4 masks, prefixes and the block size subnetting method, VLSM design, RFC 1918 and special ranges, IPv6 shortening, types and EUI-64, with a subnet calculator and Packet Tracer lab.",
    kw="ipv4 subnetting made easy, block size method subnetting, vlsm example 192.168, subnet calculator practice, rfc 1918 private ip, ipv6 address types shortening, eui-64 example, ccna ip addressing",
    kicker="$ lesson 3.2 --track ccna --domain addressing", hi_title="IP addressing aur subnetting",
    lead="Subnetting scares people because it is usually taught as magic. It is just counting in blocks. Learn the block size method, design a VLSM plan without overlaps, know which ranges are special, and get comfortable with IPv6, with a calculator that shows every bit.",
    hi_lead="Subnetting isliye darata hai kyunki use jaadu ki tarah padhaya jaata hai. Ye bas blocks mein ginti hai. Block size method seekho, bina overlap VLSM plan banao, special ranges jaano, aur IPv6 se comfortable ho jao.",
    goals=["Find the network, broadcast, host range and host count for any IPv4 prefix by hand", "Design a VLSM plan that fits several subnets into one block without overlap", "Name the private and special IPv4 ranges and what each means in an investigation", "Write, shorten and classify IPv6 addresses, and build an EUI-64 interface ID", "Configure and verify dual stack addressing on a router"],
    sections=S,
    cards=[("Usable hosts in a /27?", "30 (32 minus 2)."), ("Block size for /28?", "16 (256 minus 240)."), ("Network address of 10.1.1.77/26?", "10.1.1.64 (blocks of 64)."),
      ("The three RFC 1918 ranges?", "10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16."), ("169.254.x.x on a client means?", "It asked for DHCP and got no answer (APIPA)."),
      ("How many times can :: appear?", "Once."), ("IPv6 link-local prefix?", "fe80::/10"), ("VLSM golden rule?", "Biggest subnet first, each on its own block boundary.")],
    quiz=[("What is the broadcast address of 192.168.50.130/26?", ["192.168.50.127", "192.168.50.191", "192.168.50.255", "192.168.50.192"], 1, "Blocks of 64: 128 to 191."),
      ("Which prefix gives exactly 2 usable hosts in the classic calculation?", ["/29", "/30", "/31", "/32"], 1, "4 addresses minus network and broadcast. /31 also gives 2 on point-to-point links under RFC 3021."),
      ("You need 50 hosts. Smallest subnet?", ["/27", "/26", "/25", "/28"], 1, "/26 gives 62; /27 gives only 30."),
      ("Which address is private?", ["172.32.1.1", "172.20.1.1", "11.0.0.1", "192.169.1.1"], 1, "172.16.0.0/12 runs from 172.16 to 172.31."),
      ("What is the recommended way (RFC 5952) to write 2001:0db8:0000:0000:0001:0000:0000:0001?", ["2001:db8::1::1", "2001:db8::1:0:0:1", "2001:db8:0:0:1::1", "2001:db8:0::1:0::1"], 1, "B and C are both valid addresses, but when two zero runs are equal, RFC 5952 compresses the first one. A and D use :: twice, which is never allowed."),
      ("Which IPv6 type does every IPv6 interface have automatically?", ["Global unicast", "Link-local", "Unique local", "Anycast"], 1, "fe80::/10 link-local addresses exist on every IPv6 enabled interface.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.2: VLSM plan plus a dual stack link", time="45 minutes",
      needs=PT_NEEDS + " Devices: 2 x ISR4331, 3 x 2960, 3 x PC-PT. Work out the VLSM table yourself before you read the answer in section 3.",
      topo=fig(TOPO2, "R1 serves LAN-A on Gi0/0/0 and LAN-B on Gi0/0/2, and links to R2 on Gi0/0/1. R2 serves LAN-C on Gi0/0/0.", "Lab topology"),
      addr=[["R1", "Gi0/0/0", "192.168.50.1/25, 2001:db8:acad:a::1/64, fe80::1", "LAN-A gateway"], ["R1", "Gi0/0/2", "192.168.50.129/26, 2001:db8:acad:b::1/64, fe80::1", "LAN-B gateway"],
            ["R1", "Gi0/0/1", "192.168.50.225/30, 2001:db8:acad:12::1/64", "link to R2"], ["R2", "Gi0/0/1", "192.168.50.226/30, 2001:db8:acad:12::2/64", "link to R1"],
            ["R2", "Gi0/0/0", "192.168.50.193/27, 2001:db8:acad:c::1/64, fe80::2", "LAN-C gateway"], ["PC-A", "Fa0", "192.168.50.10/25", "gw .1, IPv6 by SLAAC"],
            ["PC-B", "Fa0", "192.168.50.140/26", "gw .129, IPv6 by SLAAC"], ["PC-C", "Fa0", "192.168.50.200/27", "gw .193, IPv6 by SLAAC"]],
      steps=[("IPv4 on every router interface", ios(["R1(config)# interface GigabitEthernet0/0/0", "R1(config-if)# ip address 192.168.50.1 255.255.255.128", "R1(config-if)# no shutdown", "! repeat for Gi0/0/2 and Gi0/0/1, then R2's interfaces"], "IPv4")),
        ("IPv6 routing and addresses", ios(["R1(config)# ipv6 unicast-routing", "R1(config)# interface GigabitEthernet0/0/0", "R1(config-if)# ipv6 address 2001:db8:acad:a::1/64", "R1(config-if)# ipv6 address fe80::1 link-local", "! same pattern on the other interfaces and on R2"], "IPv6")),
        ("See EUI-64 for yourself", ios(["R1(config)# interface loopback 0", "R1(config-if)# ipv6 address 2001:db8:acad:99::/64 eui-64", "R1(config-if)# end", "R1# show ipv6 interface brief"], "EUI-64") + "<p>Find <code>FF:FE</code> in the middle of the host part.</p>"),
        ("Clients", "<p>Set each PC's IPv4 statically and IPv6 to Automatic (SLAAC) in IP Configuration.</p>"),
        ("Routes so the LANs meet (a preview of lesson 3.7)", ios(["R1(config)# ip route 192.168.50.192 255.255.255.224 192.168.50.226", "R1(config)# ipv6 route 2001:db8:acad:c::/64 2001:db8:acad:12::2", "R2(config)# ip route 192.168.50.0 255.255.255.128 192.168.50.225", "R2(config)# ip route 192.168.50.128 255.255.255.192 192.168.50.225", "R2(config)# ipv6 route 2001:db8:acad:a::/64 2001:db8:acad:12::1", "R2(config)# ipv6 route 2001:db8:acad:b::/64 2001:db8:acad:12::1"], "Static routes")),
        ("Verify", ios(["R1# show ip interface brief", "R1# show ipv6 interface brief", "R1# show ipv6 interface GigabitEthernet0/0/0", "R1# show ip route", "R1# show ipv6 route"], "Verify") + "<p>Then ping PC-C from PC-A over IPv4 and IPv6, and run <code>ipconfig</code> on PC-A: its IPv6 gateway should be R1's link-local fe80::1.</p>")],
      verify="All three LANs reach each other over IPv4 and IPv6, your own VLSM table matches the one in section 3, and you found the FFFE in the EUI-64 address.",
      limits=["Whether Packet Tracer PCs build their SLAAC interface ID with EUI-64 or a random value can vary by version. UNVERIFIED.", "<code>ipconfig /all</code> on Packet Tracer PCs shows less detail than real Windows.", PT_GENERIC]),
    takeaways=["Block size = 256 minus the interesting mask octet.", "VLSM: biggest first, on block boundaries, no overlap.", "Private ranges need NAT to reach the internet, and are not a security control.",
      "IPv6: drop leading zeros, one :: only, link-local everywhere, no broadcast.", "Segmentation starts with a good addressing plan."])
