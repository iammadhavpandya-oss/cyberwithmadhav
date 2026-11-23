"""Stage 3 (CCNA track) lessons 3.5 to 3.7. Original writing for CyberWithMadhav."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from learn_kit import *
from content.learn_ccna_a import PT_NEEDS, PT_GENERIC

def lk(v):  # mission regex helper: a spanning-tree vlan list line containing VLAN v at priority p
    return r"(?:[\d,-]*,)?" + str(v) + r"(?:,[\d,-]*)?"

# ------------------------------------------------------------------ 3.5
LOOP = svg(760, 230, ARROWDEF +
  box(300, 20, 160, 50, "s-p", "SW-A", "root bridge") + box(110, 150, 160, 50, "s-n", "SW-B") + box(490, 150, 160, 50, "s-n", "SW-C") +
  '<line x1="330" y1="72" x2="210" y2="148" class="ln-g" stroke-width="3"/><line x1="430" y1="72" x2="550" y2="148" class="ln-g" stroke-width="3"/>' +
  '<line x1="272" y1="175" x2="488" y2="175" class="ln" stroke-width="2" stroke-dasharray="6 5"/>' +
  '<text x="380" y="168" text-anchor="middle" font-size="12" class="t-m">SW-C port blocks (alternate)</text>' +
  '<text x="190" y="104" text-anchor="end" font-size="11.5" class="t-m">root port on SW-B</text><text x="570" y="104" font-size="11.5" class="t-m">root port on SW-C</text>' +
  '<text x="380" y="222" text-anchor="middle" font-size="12" class="t-m">Without STP, one broadcast would circle this triangle forever</text>',
  "Three switches in a triangle. STP elects SW-A as root and blocks one port on the SW-B to SW-C link to break the loop")

TOPO5 = topo(760, 300, {"d1": (200, 60, "l3switch", "DSW1", "3650"), "d2": (560, 60, "l3switch", "DSW2", "3650"), "a1": (380, 190, "switch", "ASW1", "2960"),
                        "p1": (240, 270, "pc", "PC1", "VLAN 10"), "p2": (520, 270, "pc", "PC2", "VLAN 20")},
  [("d1", "d2", "Gi1/0/1-2", "Gi1/0/1-2", "ln-p"), ("d1", "a1", "Gi1/0/3", "Gi0/1"), ("d2", "a1", "Gi1/0/3", "Gi0/2"), ("a1", "p1", "Fa0/1", ""), ("a1", "p2", "Fa0/11", "")],
  "Lab 3.5 topology: two 3650 distribution switches joined by a two link LACP EtherChannel, each uplinked to access switch ASW1")

GI24 = [f"GigabitEthernet1/0/{i}" for i in range(1, 25)] + ["Vlan1"]
TRUNK = {"mode": "trunk", "native": 99, "allowed": "10,20,99", "nonego": True}

def lesson_ccna_5():
  S = []
  S.append(dict(id="loops", h="Why redundant links can melt a network", hi_h="Loops kyun khatarnak hain",
    body=f'''<p>You add a second link between switches so one cable failure does not take a building offline. Ethernet frames have no hop limit (there is no TTL in the Layer 2 header), so without protection a redundant link creates a loop and three things happen within seconds:</p>
<ul><li><strong>Broadcast storm</strong>: every broadcast is flooded out every port, comes back round the loop, and is flooded again, until links and CPUs are saturated.</li>
<li><strong>MAC table instability</strong>: the same source MAC arrives on different ports, so the switch keeps rewriting its table (MAC flapping).</li>
<li><strong>Duplicate frames</strong>: hosts receive several copies of the same unicast frame.</li></ul>
{fig(LOOP, "Spanning Tree keeps the physical redundancy but logically blocks one port, so there is exactly one active path between any two switches. If an active link fails, the blocked port takes over.", "STP breaks a loop")}
{analogy("<p>A ring road with every junction open lets traffic circle forever. STP is the traffic police putting one barrier on the ring, and moving it the moment a road is closed.</p>")}''',
    hi="Ethernet frame mein TTL nahi hota, isliye redundant links se loop banta hai: broadcast storm, MAC flapping aur duplicate frames, seconds mein network down. STP physical redundancy rakhta hai par ek port logically block karta hai, aur link fail hone pe woh port khul jaata hai."))

  S.append(dict(id="election", h="How STP elects a root and picks ports", hi_h="Root election aur port roles",
    body=f'''<p>Switches exchange <strong>BPDUs</strong> (bridge protocol data units). Each has a <strong>bridge ID</strong>: a priority (default 32768, changeable only in steps of 4096) plus the VLAN number (the system ID extension) plus its MAC address. Then:</p>
<ol><li><strong>Root bridge</strong>: the lowest bridge ID wins. With default priorities that means the lowest MAC, which is often the oldest switch in the building. That is why you always choose the root yourself.</li>
<li><strong>Root port</strong>: every other switch picks its port with the lowest total cost to the root. Ties break on the lowest neighbour bridge ID, then the lowest port ID.</li>
<li><strong>Designated port</strong>: on every link, the side closer to the root forwards. All ports on the root bridge are designated.</li>
<li>Every remaining port is <strong>blocked</strong> (an <em>alternate</em> port in Rapid STP).</li></ol>
{table(["Link speed", "Default STP cost (short method)"], [["10 Mb/s", "100"], ["100 Mb/s", "19"], ["1 Gb/s", "4"], ["10 Gb/s", "2"]], "STP port costs")}
<p>Cisco Catalyst switches run one spanning tree per VLAN: <strong>PVST+</strong> by default (802.1D based) or <strong>Rapid PVST+</strong> (802.1w based). Because each VLAN has its own tree, you can make DSW1 root for VLAN 10 and DSW2 root for VLAN 20 so both uplinks carry traffic.</p>''',
    hi="Bridge ID = priority (default 32768, 4096 ke steps) + VLAN + MAC. Sabse kam bridge ID root banta hai; default pe sabse purana switch (lowest MAC) ban jaata hai, isliye root khud chuno. Har switch ka root port = root tak sabse kam cost. Har link pe root ke paas wala side designated. Baaki ports block. Cisco per-VLAN tree chalata hai, toh VLAN 10 ka root DSW1 aur VLAN 20 ka DSW2 rakh sakte ho."))

  S.append(dict(id="rstp", h="Rapid PVST+: faster convergence", hi_h="Rapid PVST+",
    body=f'''{table(["", "Classic 802.1D (PVST+)", "Rapid 802.1w (Rapid PVST+)"], [
  ["Port states", "Blocking, listening, learning, forwarding, disabled", "Discarding, learning, forwarding"],
  ["Port roles", "Root, designated, blocked", "Root, designated, alternate, backup"],
  ["Recovery after a change", "Timer based: 30 to 50 seconds (forward delay 15 s twice, plus max age 20 s)", "Handshake based: usually within a few seconds on point to point links"],
  ["Configure", "<code>spanning-tree mode pvst</code> (default)", "<code>spanning-tree mode rapid-pvst</code>"]], "802.1D compared with 802.1w")}
<p>An <strong>alternate</strong> port is a pre-computed backup root port: when the root port fails, it moves to forwarding almost immediately. A host plugged into a port should never wait 30 seconds for the network either, which is what PortFast fixes.</p>''',
    hi="Classic STP timers pe chalta hai: 30 se 50 second. Rapid PVST+ handshake se usually kuch seconds mein converge hota hai. States: discarding, learning, forwarding. Alternate port ek ready backup root port hai. spanning-tree mode rapid-pvst se on karo."))

  S.append(dict(id="protection", h="PortFast, BPDU Guard, Root Guard and Loop Guard", hi_h="STP protection features",
    body=f'''{table(["Feature", "Where", "What it does"], [
  ["PortFast", "Access ports to a single host", "Skips listening and learning, so the PC gets connectivity at once."],
  ["BPDU Guard", "Every PortFast port", "If a BPDU arrives, the port goes err-disabled. A switch has no business on a user port."],
  ["Root Guard", "Distribution ports facing access switches", "If a superior BPDU (a would-be better root) arrives, the port goes root-inconsistent and stops forwarding."],
  ["Loop Guard", "Root and alternate ports on switch to switch links", "If BPDUs stop arriving (for example a one way fibre fault), the port is held instead of wrongly moving to forwarding."]], "STP protection features")}
{ios(["ASW1(config)# interface range Fa0/1 - 24", "ASW1(config-if-range)# spanning-tree portfast", "ASW1(config-if-range)# spanning-tree bpduguard enable", "! or globally, for every access port:", "ASW1(config)# spanning-tree portfast default", "ASW1(config)# spanning-tree portfast bpduguard default", "! recover an err-disabled port after removing the cause:", "ASW1(config)# interface Fa0/5", "ASW1(config-if)# shutdown", "ASW1(config-if)# no shutdown"], "PortFast and BPDU Guard")}
{attack("<p>Plug a small switch or a laptop running an attack tool into a user port, send BPDUs with priority 0, and you become the root bridge. Traffic between other switches may now flow through your device (a man in the middle position), and every re-election causes outages. A home router or a cheap unmanaged switch plugged in by an employee can also cause loops or elections by accident.</p>")}
{defend("<p>BPDU Guard on every user port, Root Guard on the ports where the root must never appear, a deliberately chosen root and secondary, and alerting on err-disable and topology change logs. Users get one host per port; anything else is a ticket, not a cable.</p>")}''',
    hi="PortFast host ports ko turant forwarding mein daalta hai. BPDU Guard: user port pe BPDU aaya toh port err-disabled. Root Guard: distribution ports pe, koi better root claim kare toh port block. Loop Guard: BPDUs ruk jaayein toh port forwarding mein nahi jaata. Attacker priority 0 BPDU bhej ke root ban sakta hai aur traffic apne through le sakta hai; BPDU Guard aur Root Guard isko rokte hain."))

  S.append(dict(id="etherchannel", h="EtherChannel: many links, one logical link", hi_h="EtherChannel",
    body=f'''<p>STP blocks redundant parallel links, so two cables between DSW1 and DSW2 would give you the bandwidth of one. <strong>EtherChannel</strong> bundles up to 8 active physical links into one logical <code>Port-channel</code> interface. STP sees one link, nothing is blocked, and losing one member just reduces bandwidth.</p>
{table(["Protocol", "Modes", "Forms a channel when"], [
  ["LACP (IEEE 802.3ad, now 802.1AX)", "active, passive", "active + active, or active + passive. passive + passive never starts."],
  ["PAgP (Cisco only)", "desirable, auto", "desirable + desirable, or desirable + auto. auto + auto never starts."],
  ["Static", "on", "on + on only. No negotiation, so mistakes are not detected. Avoid."]], "EtherChannel modes")}
<ul><li>All members must match: speed, duplex, access or trunk mode, allowed VLANs and native VLAN. A mismatched port is suspended from the bundle.</li>
<li>Traffic is shared per flow using a hash (for example of source and destination IPs), so a single big transfer still uses one member. Two 1 Gb/s links give 2 Gb/s of capacity, not one 2 Gb/s flow.</li>
<li>Configure trunk settings on the Port-channel interface; they apply to the members.</li></ul>''',
    hi="STP parallel links ko block karta hai, EtherChannel unko ek logical Port-channel bana deta hai, toh kuch block nahi hota. LACP (open standard: active/passive), PAgP (Cisco: desirable/auto), on (bina negotiation, avoid). Members ka speed, duplex, mode aur VLANs same hone chahiye. Load per flow share hota hai."))

  S.append(dict(id="practice", h="Practise on DSW1", hi_h="DSW1 pe practice",
    body=f'''<p>DSW1 is a 3650 with VLANs 10, 20 and 99 already created and its uplinks already trunked. Gi1/0/1 and Gi1/0/2 go to DSW2, Gi1/0/3 goes down to ASW1. DSW2 has already been made root primary for VLAN 20, and nobody chose a root for VLANs 10 and 99. This console models DSW2's side of the election for you, so treat the outputs as a guide rather than a real protocol run.</p>
{ios_sim(dict(id="l35", kind="switch", host="DSW1", ifaces=GI24, up=["GigabitEthernet1/0/1", "GigabitEthernet1/0/2", "GigabitEthernet1/0/3"],
  vlans={"10": "STAFF", "20": "GUEST", "99": "NATIVE"},
  init={"GigabitEthernet1/0/1": TRUNK, "GigabitEthernet1/0/2": TRUNK, "GigabitEthernet1/0/3": TRUNK},
  stp=dict(mac="0001.6401.1a01", other=dict(pri=32768, mac="0001.4200.0a01"), otherv={"20": 24576}, rp="GigabitEthernet1/0/1", alt=["GigabitEthernet1/0/2"]),
  intro=["DSW1, a Catalyst 3650 in the lab. Uplinks are trunks. Start in privileged mode with enable."],
  missions=[
    dict(t="Look at spanning tree for VLAN 10. Is DSW1 the root? Type <code>answer yes</code> or <code>answer no</code>.", hint="enable, then show spanning-tree vlan 10", c=dict(type="answer", v="no"), ok="No. DSW2 won because both priorities are 32768 and its MAC is lower. Nobody chose this."),
    dict(t="Which DSW1 port is blocking for VLAN 10? Type <code>answer PORT</code>.", hint="Look for the Altn BLK line", c=dict(type="answer", v=["gi1/0/2", "gigabitethernet1/0/2"]), ok="Gi1/0/2 is the alternate port: a second parallel link STP had to block."),
    dict(t="Switch to Rapid PVST+.", hint="configure terminal, spanning-tree mode rapid-pvst", c=dict(type="run", re=r"^spanning-tree mode rapid-pvst$")),
    dict(t="Make DSW1 root primary for VLANs 10 and 99.", hint="spanning-tree vlan 10,99 root primary", c=dict(type="run", re=r"(?=[\s\S]*^spanning-tree vlan " + lk(10) + r" priority 24576$)[\s\S]*^spanning-tree vlan " + lk(99) + r" priority 24576$")),
    dict(t="Make DSW1 root secondary for VLAN 20.", hint="spanning-tree vlan 20 root secondary", c=dict(type="run", re=r"^spanning-tree vlan " + lk(20) + r" priority 28672$")),
    dict(t="Confirm DSW1 is now root for VLAN 10.", hint="do show spanning-tree vlan 10", c=dict(type="out", re=r"This bridge is the root")),
    dict(t="Bundle Gi1/0/1 and Gi1/0/2 into Port-channel 1 with LACP, starting negotiation from this side.", hint="interface range gi1/0/1 - 2, channel-group 1 mode active", c=dict(type="run", re=r"^interface GigabitEthernet1/0/2\n[^!]*channel-group 1 mode active")),
    dict(t="Check the bundle. Which protocol is it using? Type <code>answer PROTOCOL</code>.", hint="do show etherchannel summary", c=dict(type="answer", v="lacp")),
    dict(t="ASW1 must never become root. Protect Gi1/0/3.", hint="interface gi1/0/3, spanning-tree guard root", c=dict(type="run", re=r"^interface GigabitEthernet1/0/3\n[^!]*spanning-tree guard root")),
    dict(t="For VLAN 20, which interface is DSW1's root port now? Type <code>answer IF</code>.", hint="do show spanning-tree vlan 20", c=dict(type="answer", v=["po1", "port-channel1", "port-channel 1"]), ok="Po1. STP treats the whole bundle as one link, so nothing between the two distribution switches is blocked any more."),
    dict(t="Save.", hint="end, copy running-config startup-config", c=dict(type="saved"))]), "DSW1 STP and EtherChannel")}''',
    hi="Simulator mein DSW1: pehle dekho root kaun hai (DSW2, lowest MAC ki wajah se), kaunsa port block hai, phir rapid-pvst, VLAN 10 aur 99 ka root primary, VLAN 20 ka secondary, Gi1/0/1-2 ka LACP bundle, Gi1/0/3 pe root guard, aur save."))

  return dict(
    slug="learn-ccna-stp-etherchannel", stage=3, n="3.5", minutes=65, level="Intermediate",
    title="Redundant Switch Links: STP, Rapid PVST+, PortFast, BPDU Guard, EtherChannel", short="Loops, root election, Rapid PVST+, STP protection features and LACP EtherChannel.",
    seo_title="STP, Rapid PVST+ and EtherChannel for CCNA: Root Election, BPDU Guard, LACP | CyberWithMadhav",
    desc="Free CCNA lesson: why loops melt networks, how STP elects a root and picks ports, Rapid PVST+, PortFast, BPDU Guard, Root Guard, Loop Guard and LACP EtherChannel, with an IOS simulator and Packet Tracer lab.",
    kw="spanning tree protocol tutorial, stp root bridge election, rapid pvst+ configuration, bpdu guard portfast, root guard loop guard, etherchannel lacp active passive, packet tracer stp etherchannel lab, ccna stp",
    kicker="$ lesson 3.5 --track ccna --domain switching", hi_title="Redundant links: STP aur EtherChannel",
    lead="Redundancy keeps a network up when a cable dies, and the same redundancy can take it down in seconds if loops are not controlled. Learn how spanning tree decides which ports forward, how to choose the root yourself, how to stop rogue switches, and how EtherChannel turns parallel links into one.",
    hi_lead="Redundancy network ko cable failure se bachati hai, aur wahi redundancy loop ban ke seconds mein network gira sakti hai. STP, root choose karna, rogue switch rokna aur EtherChannel seekho.",
    goals=["Explain broadcast storms and why Ethernet needs STP", "Predict the root bridge, root ports, designated ports and blocked ports", "Configure Rapid PVST+ and choose a root and secondary per VLAN", "Apply PortFast, BPDU Guard and Root Guard where they belong", "Build and verify an LACP EtherChannel trunk"],
    sections=S,
    cards=[("Default bridge priority?", "32768, changeable in steps of 4096."), ("Who becomes root?", "Lowest bridge ID: priority, then MAC."), ("STP cost of 1 Gb/s?", "4 (short method)."),
      ("RSTP port states?", "Discarding, learning, forwarding."), ("BPDU Guard action?", "Err-disables the port when a BPDU arrives."), ("Root Guard action?", "Puts the port root-inconsistent if a superior BPDU arrives."),
      ("LACP modes?", "active and passive. passive + passive never forms."), ("Max active links in an EtherChannel?", "8.")],
    quiz=[("All switches use priority 32768. Which becomes root?", ["The newest switch", "The one with the lowest MAC address", "The one with the most ports", "The one with the highest IP"], 1, "Lowest bridge ID; with equal priority the MAC decides."),
      ("Where should BPDU Guard go?", ["Trunks between distribution switches", "Access ports connected to single hosts", "Router ports", "The root bridge's root port"], 1, "User ports should never receive BPDUs."),
      ("Which pair forms an LACP channel?", ["passive + passive", "active + passive", "auto + auto", "on + active"], 1, "At least one side must be active."),
      ("Why use EtherChannel instead of two separate trunks?", ["STP would block one of the two separate links", "It encrypts traffic", "It removes the need for VLANs", "It is required for SSH"], 0, "The bundle is one logical link, so nothing is blocked."),
      ("<code>spanning-tree vlan 10 priority 1000</code> is rejected. Why?", ["VLAN 10 does not exist", "Priority must be a multiple of 4096", "Priority must be above 32768", "Rapid PVST+ is required"], 1, "Valid values are 0, 4096, 8192 and so on up to 61440."),
      ("A single large file copy runs over a two member 1 Gb/s bundle. Roughly how fast can it go?", ["2 Gb/s", "About 1 Gb/s, because one flow hashes to one member", "500 Mb/s", "4 Gb/s"], 1, "Load sharing is per flow, not per packet.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.5: Rapid PVST+, guards and an LACP EtherChannel", time="50 minutes",
      needs=PT_NEEDS + " Devices: 2 x 3650-24PS, 1 x 2960-24TT, 2 x PC-PT. Create VLANs 10, 20 and 99 on all three switches and trunk every inter-switch link (native 99, allowed 10,20,99) as in lesson 3.4.",
      topo=fig(TOPO5, "DSW1 and DSW2 joined by Gi1/0/1 and Gi1/0/2 (Port-channel 1). DSW1 Gi1/0/3 to ASW1 Gi0/1, DSW2 Gi1/0/3 to ASW1 Gi0/2. PC1 on ASW1 Fa0/1 (VLAN 10), PC2 on Fa0/11 (VLAN 20).", "Lab topology"),
      addr=[["PC1", "Fa0", "192.168.10.11/24", "VLAN 10"], ["PC2", "Fa0", "192.168.20.11/24", "VLAN 20"], ["Switches", "", "no IP needed for this lab", "Layer 2 only"]],
      steps=[("Before you change anything", ios(["DSW1# show spanning-tree vlan 10", "DSW1# show spanning-tree vlan 20"], "Default election") + "<p>Write down who is root and which port blocks. Expect the parallel DSW link and one ASW1 uplink to show blocking somewhere.</p>"),
        ("Rapid PVST+ and the roots", ios(["DSW1(config)# spanning-tree mode rapid-pvst", "DSW1(config)# spanning-tree vlan 10,99 root primary", "DSW1(config)# spanning-tree vlan 20 root secondary", "DSW2(config)# spanning-tree mode rapid-pvst", "DSW2(config)# spanning-tree vlan 20 root primary", "DSW2(config)# spanning-tree vlan 10,99 root secondary", "ASW1(config)# spanning-tree mode rapid-pvst"], "Roots")),
        ("Protect the edge (ASW1)", ios(["ASW1(config)# interface range Fa0/1 - 24", "ASW1(config-if-range)# spanning-tree portfast", "ASW1(config-if-range)# spanning-tree bpduguard enable"], "Edge")),
        ("Root Guard toward the access layer (both DSWs)", ios(["DSW1(config)# interface Gi1/0/3", "DSW1(config-if)# spanning-tree guard root"], "Root Guard")),
        ("LACP EtherChannel (both DSWs)", ios(["DSW1(config)# interface range Gi1/0/1 - 2", "DSW1(config-if-range)# channel-group 1 mode active", "Creating a port-channel interface Port-channel 1", "DSW1(config-if-range)# interface Port-channel1", "DSW1(config-if)# switchport mode trunk", "DSW1(config-if)# switchport trunk native vlan 99", "DSW1(config-if)# switchport trunk allowed vlan 10,20,99", "DSW2(config)# interface range Gi1/0/1 - 2", "DSW2(config-if-range)# channel-group 1 mode passive"], "EtherChannel") + "<p>On 3650s you may need <code>switchport trunk encapsulation dot1q</code> before <code>switchport mode trunk</code>, depending on the image.</p>"),
        ("Fail a link", "<p>Start a continuous ping from PC1 to another VLAN 10 host (<code>ping -t</code>), then delete or shut the DSW1 to ASW1 link. Watch the alternate port on ASW1 take over and count the lost pings.</p>"),
        ("Trip BPDU Guard", "<p>Connect a spare 2960 to ASW1 Fa0/5. The port should go err-disabled. Remove the switch, then recover with <code>shutdown</code> and <code>no shutdown</code> on Fa0/5.</p>"),
        ("Verify", ios(["DSW1# show spanning-tree vlan 10", "DSW1# show spanning-tree summary", "DSW1# show etherchannel summary", "DSW1# show interfaces trunk", "ASW1# show interfaces status err-disabled"], "Verify"))],
      verify="DSW1 is root for VLANs 10 and 99 and DSW2 for VLAN 20; show etherchannel summary shows Po1(SU) with both members (P); ASW1 Fa0/5 went err-disabled when a switch was attached.",
      limits=["In some Packet Tracer versions a 3650 starts without a power supply and stays off until you add one in its Physical tab. UNVERIFIED for every version.",
              "Root Guard, Loop Guard and <code>errdisable recovery cause bpduguard</code> are real IOS features; their support on Packet Tracer's switch images is UNVERIFIED. If a command is rejected, note it and read about it instead.",
              "Convergence timing in Packet Tracer is simulated and does not match real hardware; treat lost ping counts as rough.",
              "Layer 3 EtherChannel on the 3650 in Packet Tracer is UNVERIFIED; this lab uses a Layer 2 bundle. Cisco NetAcad publishes official Packet Tracer activities for Rapid PVST+ and EtherChannel if you want more practice.", PT_GENERIC]),
    takeaways=["Loops cause storms; STP blocks just enough ports to prevent them.", "Choose the root yourself, per VLAN, with a secondary.", "Rapid PVST+ recovers in seconds instead of up to 50.",
      "PortFast plus BPDU Guard on user ports; Root Guard where the root must never appear.", "EtherChannel makes parallel links one logical link; use LACP."])

# ------------------------------------------------------------------ 3.6
ROAS = topo(760, 250, {"r1": (380, 40, "router", "R1", "ISR4331"), "sw": (380, 140, "switch", "SW1"),
                       "p1": (140, 220, "pc", "PC-Staff", "192.168.10.11"), "p2": (620, 220, "pc", "PC-Guest", "192.168.20.11")},
  [("r1", "sw", "Gi0/0/0 .10 .20 .99", "Gi0/1 trunk", "ln-p"), ("sw", "p1", "Fa0/1 VLAN 10", ""), ("sw", "p2", "Fa0/11 VLAN 20", "")],
  "Router on a stick: one trunk from SW1 to R1 carries VLANs 10, 20 and 99 to subinterfaces")
HSRPF = svg(760, 220, ARROWDEF +
  box(120, 30, 200, 56, "s-g", "R-A  Active", "real .2, priority 110") + box(440, 30, 200, 56, "s-n", "R-B  Standby", "real .3, priority 100") +
  box(280, 150, 200, 50, "s-p", "Hosts", "gateway 192.168.100.1") +
  '<line x1="220" y1="88" x2="350" y2="148" class="ln-g" stroke-width="3"/><line x1="540" y1="88" x2="410" y2="148" class="ln" stroke-width="2" stroke-dasharray="6 5"/>' +
  '<text x="380" y="60" text-anchor="middle" font-size="12" class="t-m">hellos</text><line x1="322" y1="66" x2="438" y2="66" class="ln" stroke-width="1.5" stroke-dasharray="2 4"/>' +
  '<text x="380" y="122" text-anchor="middle" font-size="12" class="t-m">virtual IP .1 and virtual MAC live on the active router</text>',
  "HSRP: two routers share a virtual gateway IP. The active router answers for it; the standby takes over if hellos stop")

def lesson_ccna_6():
  S = []
  S.append(dict(id="options", h="Three ways to route between VLANs", hi_h="VLANs ke beech routing",
    body=f'''<p>VLANs separate hosts at Layer 2. To let VLAN 10 reach VLAN 20 at all, something must route between their subnets, and every PC needs that device as its default gateway.</p>
{table(["Method", "How", "Good for", "Watch out"], [
  ["Legacy", "One router interface per VLAN", "Teaching only", "Burns router ports and switch ports."],
  ["Router on a stick", "One trunk to a router, one subinterface per VLAN", "Small sites, labs", "All inter-VLAN traffic shares one physical link."],
  ["Layer 3 switch", "<code>ip routing</code> plus an SVI per VLAN", "Most campus networks", "Routing happens in switch hardware at full speed; filter it with ACLs."]], "Inter-VLAN routing methods")}
{defend("<p>The inter-VLAN router is your first internal choke point. It is where you put ACLs (lesson 3.9) so guests reach the internet but not staff, and so a compromised laptop cannot reach management interfaces. A VLAN without filtering at its gateway is only half a boundary.</p>")}''',
    hi="VLAN 10 se VLAN 20 tak jaane ke liye routing chahiye aur har PC ka default gateway woh router hota hai. Teen tareeke: legacy (har VLAN ka alag port), router on a stick (ek trunk, subinterfaces), Layer 3 switch (ip routing + SVI). Gateway pe ACL lagao, warna VLAN aadhi boundary hai."))

  S.append(dict(id="roas", h="Router on a stick", hi_h="Router on a stick",
    body=f'''{fig(ROAS, "SW1's Gi0/1 is an 802.1Q trunk. R1 receives tagged frames on Gi0/0/0 and hands each VLAN to its own subinterface.", "Router on a stick")}
{ios(["R1(config)# interface GigabitEthernet0/0/0", "R1(config-if)# no shutdown", "R1(config-if)# interface GigabitEthernet0/0/0.10", "R1(config-subif)# encapsulation dot1Q 10", "R1(config-subif)# ip address 192.168.10.1 255.255.255.0", "R1(config-subif)# interface GigabitEthernet0/0/0.20", "R1(config-subif)# encapsulation dot1Q 20", "R1(config-subif)# ip address 192.168.20.1 255.255.255.0", "R1(config-subif)# interface GigabitEthernet0/0/0.99", "R1(config-subif)# encapsulation dot1Q 99 native"], "Subinterfaces")}
<ul><li><code>encapsulation dot1Q</code> must come before the IP address on a subinterface.</li><li>The physical interface needs <code>no shutdown</code>; the subinterfaces follow it. The subinterface number does not have to match the VLAN, but matching it saves confusion.</li>
<li>The native VLAN subinterface uses the <code>native</code> keyword so it matches the switch's untagged VLAN 99.</li><li>The switch side is a normal trunk: <code>switchport mode trunk</code>, native 99, allowed 10,20,99.</li></ul>''',
    hi="Router on a stick: switch ka ek trunk router ke ek physical port pe, aur router pe har VLAN ka subinterface (Gi0/0/0.10). Pehle encapsulation dot1Q 10, phir IP. Physical port pe no shutdown. Native VLAN subinterface pe native keyword."))

  S.append(dict(id="l3switch", h="Layer 3 switch SVIs and routed ports", hi_h="Layer 3 switch",
    body=f'''{ios(["DSW1(config)# ip routing", "DSW1(config)# interface vlan 10", "DSW1(config-if)# ip address 192.168.10.1 255.255.255.0", "DSW1(config-if)# no shutdown", "DSW1(config-if)# interface vlan 20", "DSW1(config-if)# ip address 192.168.20.1 255.255.255.0", "DSW1(config-if)# no shutdown", "! a routed uplink to a router, no VLANs involved:", "DSW1(config)# interface GigabitEthernet1/0/24", "DSW1(config-if)# no switchport", "DSW1(config-if)# ip address 10.0.0.1 255.255.255.252"], "SVIs and a routed port")}
<ul><li>Forget <code>ip routing</code> and the SVIs come up but nothing routes between them. It is the most common mistake in this topic.</li>
<li>An SVI is only up/up if its VLAN exists and at least one port in that VLAN (access or trunk) is up and forwarding.</li>
<li><code>no switchport</code> turns a switch port into a router port with its own IP, used for point to point links to routers or other Layer 3 switches.</li></ul>''',
    hi="Layer 3 switch pe ip routing on karo, har VLAN ka SVI (interface vlan 10) IP ke saath. ip routing bhool gaye toh SVIs up honge par routing nahi hogi. SVI up/up tabhi jab VLAN exist kare aur uska koi port up ho. no switchport se port router port ban jaata hai."))

  S.append(dict(id="fhrp", h="First hop redundancy: HSRP", hi_h="HSRP",
    body=f'''<p>Every host has one default gateway address. If that router dies, the hosts are cut off even if a second router is sitting right there. A <strong>first hop redundancy protocol</strong> lets two or more routers share a <em>virtual</em> gateway IP and MAC, so hosts never notice which router is doing the work.</p>
{fig(HSRPF, "Hosts use 192.168.100.1, which belongs to no physical router. The active router answers ARP for it with the HSRP virtual MAC.", "HSRP")}
{table(["", "HSRP version 1", "HSRP version 2"], [["Groups", "0 to 255", "0 to 4095"], ["Hellos to", "224.0.0.2, UDP 1985", "224.0.0.102, UDP 1985"], ["Virtual MAC", "0000.0c07.acXX (XX = group)", "0000.0c9f.fXXX (XXX = group)"], ["IPv6", "No", "Yes"]], "HSRP versions")}
<ul><li>Highest priority becomes active (default 100; a tie goes to the highest interface IP). Hellos every 3 seconds; the standby takes over after the 10 second hold time by default.</li>
<li><strong>Preempt is off by default</strong>. Without <code>standby 1 preempt</code>, a recovered primary router will not take its role back.</li>
<li>Alternatives: <strong>VRRP</strong> (open standard, RFC 5798, master and backup, preempt on by default) and <strong>GLBP</strong> (Cisco, shares the load across several routers at once).</li></ul>
{ios(["R-A(config)# interface GigabitEthernet0/1", "R-A(config-if)# ip address 192.168.100.2 255.255.255.0", "R-A(config-if)# standby version 2", "R-A(config-if)# standby 1 ip 192.168.100.1", "R-A(config-if)# standby 1 priority 110", "R-A(config-if)# standby 1 preempt", "R-A# show standby brief"], "HSRP on the primary")}
{attack("<p>HSRP hellos are multicast on the LAN. A host that sends forged hellos with priority 255 can become the active gateway and receive everyone's outbound traffic: a man in the middle, or a black hole.</p>")}
{defend("<p>Use HSRP authentication with MD5 (<code>standby 1 authentication md5 key-string ...</code>), run HSRP only on interfaces that need it, and alert on unexpected state changes in logs. Packet Tracer support for HSRP MD5 authentication is UNVERIFIED.</p>")}''',
    hi="Host ka ek hi gateway hota hai; woh router gira toh sab cut. HSRP mein do routers ek virtual IP aur MAC share karte hain. Highest priority active (default 100). Preempt default off hai, isliye standby 1 preempt lagao. v2 mein 4096 groups aur IPv6. VRRP open standard, GLBP load share. Attacker priority 255 hellos bhej ke gateway ban sakta hai; MD5 authentication lagao."))

  S.append(dict(id="practice", h="Practise on R1", hi_h="R1 pe practice",
    body=f'''<p>To keep things in one console, R1 here does both jobs: router on a stick on Gi0/0/0, and the primary HSRP router on Gi0/0/1 with a partner at 192.168.100.3 that this console models. In Packet Tracer you build them as separate parts.</p>
{ios_sim(dict(id="l36", kind="router", host="R1", ifaces=["GigabitEthernet0/0/0", "GigabitEthernet0/0/1", "GigabitEthernet0/0/2"], up=["GigabitEthernet0/0/0", "GigabitEthernet0/0/1"], peer="192.168.100.3",
  intro=["R1, an ISR4331. Gi0/0/0 is cabled to SW1's trunk, Gi0/0/1 to the HSRP LAN."],
  missions=[
    dict(t="Bring up the physical interface Gi0/0/0 (no IP on it).", hint="enable, configure terminal, interface g0/0/0, no shutdown", c=dict(type="run", re=r"^interface GigabitEthernet0/0/0\n no ip address\n!")),
    dict(t="Create subinterface Gi0/0/0.10 for VLAN 10 with 192.168.10.1/24.", hint="interface g0/0/0.10, encapsulation dot1Q 10, ip address 192.168.10.1 255.255.255.0", c=dict(type="run", re=r"^interface GigabitEthernet0/0/0\.10\n encapsulation dot1Q 10\n ip address 192\.168\.10\.1 255\.255\.255\.0")),
    dict(t="Same for VLAN 20: Gi0/0/0.20 with 192.168.20.1/24.", hint="interface g0/0/0.20, encapsulation dot1Q 20, ip address 192.168.20.1 255.255.255.0", c=dict(type="run", re=r"^interface GigabitEthernet0/0/0\.20\n encapsulation dot1Q 20\n ip address 192\.168\.20\.1 255\.255\.255\.0")),
    dict(t="Add Gi0/0/0.99 as the native VLAN 99 subinterface.", hint="interface g0/0/0.99, encapsulation dot1Q 99 native", c=dict(type="run", re=r"^interface GigabitEthernet0/0/0\.99\n encapsulation dot1Q 99 native")),
    dict(t="Check the routing table. How many connected (C) routes are there? Type <code>answer N</code>.", hint="do show ip route", c=dict(type="answer", v="2"), ok="Two: 192.168.10.0/24 and 192.168.20.0/24. The native subinterface has no IP address, so it adds no route."),
    dict(t="Now HSRP. Give Gi0/0/1 the address 192.168.100.2/24 and bring it up.", hint="interface g0/0/1, ip address 192.168.100.2 255.255.255.0, no shutdown", c=dict(type="run", re=r"^interface GigabitEthernet0/0/1\n ip address 192\.168\.100\.2 255\.255\.255\.0\n!")),
    dict(t="Use HSRP version 2 and the virtual gateway 192.168.100.1 in group 1.", hint="standby version 2, standby 1 ip 192.168.100.1", c=dict(type="run", re=r"(?=[\s\S]*^ standby version 2$)[\s\S]*^ standby 1 ip 192\.168\.100\.1$")),
    dict(t="Make R1 the preferred router and let it take the role back after a reboot.", hint="standby 1 priority 110, standby 1 preempt", c=dict(type="run", re=r"(?=[\s\S]*^ standby 1 priority 110$)[\s\S]*^ standby 1 preempt$")),
    dict(t="What HSRP state is R1 in? Type <code>answer STATE</code>.", hint="do show standby brief", c=dict(type="answer", v="active"))]), "R1 inter-VLAN and HSRP")}''',
    hi="Simulator mein R1: Gi0/0/0 up, .10 aur .20 subinterfaces IP ke saath, .99 native, routing table check, phir Gi0/0/1 pe HSRP v2: virtual IP .1, priority 110, preempt, aur state check."))

  return dict(
    slug="learn-ccna-inter-vlan-routing-hsrp", stage=3, n="3.6", minutes=60, level="Intermediate",
    title="Inter-VLAN Routing and First Hop Redundancy: Router on a Stick, SVIs, HSRP", short="Router on a stick, Layer 3 switch SVIs and routed ports, and HSRP gateway redundancy.",
    seo_title="Inter-VLAN Routing and HSRP for CCNA: Router on a Stick, SVIs, Preempt | CyberWithMadhav",
    desc="Free CCNA lesson: route between VLANs with router on a stick or Layer 3 switch SVIs, add routed ports, and keep the default gateway alive with HSRP (versions, priority, preempt, attacks), with an IOS simulator and Packet Tracer lab.",
    kw="inter vlan routing, router on a stick configuration, encapsulation dot1q native, layer 3 switch svi ip routing, hsrp configuration priority preempt, hsrp version 2 virtual mac, vrrp vs hsrp vs glbp, packet tracer inter vlan lab",
    kicker="$ lesson 3.6 --track ccna --domain routing", hi_title="Inter-VLAN routing aur HSRP",
    lead="VLANs keep groups apart; routing lets them talk on your terms. Learn the two real ways to route between VLANs, why the default gateway is a single point of failure, and how HSRP fixes it without anyone changing a setting on their laptop.",
    hi_lead="VLANs groups ko alag rakhte hain, routing unhe aapki shart pe baat karne deti hai. Router on a stick, Layer 3 switch aur HSRP seekho.",
    goals=["Compare legacy, router on a stick and Layer 3 switch inter-VLAN routing", "Configure 802.1Q subinterfaces including the native VLAN", "Configure SVIs, ip routing and a routed port on a Layer 3 switch", "Configure HSRP version 2 with priority and preempt, and explain the hijack risk"],
    sections=S,
    cards=[("Subinterface command before the IP?", "encapsulation dot1Q <vlan>"), ("Most common Layer 3 switch mistake?", "Forgetting ip routing."), ("Make a switch port a router port?", "no switchport"),
      ("HSRP default priority?", "100. Highest wins."), ("Is HSRP preempt on by default?", "No."), ("HSRP v2 virtual MAC?", "0000.0c9f.fXXX"), ("Open standard FHRP?", "VRRP."), ("When is an SVI up/up?", "VLAN exists and at least one port in it is up and forwarding.")],
    quiz=[("Router on a stick: what must the switch port facing the router be?", ["Access in VLAN 1", "An 802.1Q trunk", "A routed port", "Shut down"], 1, "It carries several VLANs to the router."),
      ("SVIs are up on a 3650 but VLAN 10 cannot reach VLAN 20. First check?", ["ip routing", "Banner", "CDP", "Duplex"], 0, "Without ip routing the switch does not route."),
      ("The primary HSRP router reboots and comes back, but stays standby. Why?", ["Version 1 is used", "Preempt is not configured", "Its priority is higher", "The VIP is wrong"], 1, "Preempt is off by default."),
      ("What do hosts use as their default gateway with HSRP?", ["The active router's real IP", "The virtual IP", "The standby router's IP", "The switch's IP"], 1, "The virtual IP moves between routers."),
      ("Which protocol is an open standard?", ["HSRP", "GLBP", "VRRP", "PAgP"], 2, "VRRP, RFC 5798."),
      ("Why put ACLs at the inter-VLAN gateway?", ["To speed up routing", "It is the point where traffic between VLANs can be filtered", "HSRP requires it", "To enable trunking"], 1, "That is the internal choke point.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.6: router on a stick, SVIs and HSRP", time="60 minutes",
      needs=PT_NEEDS + " Part A: 1 x ISR4331, 1 x 2960, 2 x PC. Part B: 1 x 3650, 2 x PC. Part C: 2 x 2911, 1 x 2960, 1 x PC. Reuse the VLANs from lesson 3.4.",
      topo=fig(ROAS, "Part A shown: R1 Gi0/0/0 to SW1 Gi0/1 (trunk), PC-Staff on Fa0/1 (VLAN 10), PC-Guest on Fa0/11 (VLAN 20). Part B replaces R1 and SW1 with one 3650. Part C puts two 2911s on one switch in 192.168.100.0/24.", "Lab topology"),
      addr=[["R1 (A)", "Gi0/0/0.10 / .20", "192.168.10.1/24, 192.168.20.1/24", ".99 native, no IP"], ["DSW1 (B)", "VLAN 10 / VLAN 20 SVIs", "192.168.10.1/24, 192.168.20.1/24", "Gi1/0/24 routed 10.0.0.1/30"],
            ["PCs", "Fa0", "192.168.10.11 and 192.168.20.11", "gw .1 of their VLAN"], ["R-A (C)", "G0/1", "192.168.100.2/24", "HSRP active, priority 110"], ["R-B (C)", "G0/1", "192.168.100.3/24", "HSRP standby"], ["PC (C)", "Fa0", "192.168.100.10/24", "gw 192.168.100.1 (virtual)"]],
      steps=[("Part A: switch side", ios(["SW1(config)# interface Gi0/1", "SW1(config-if)# switchport mode trunk", "SW1(config-if)# switchport trunk native vlan 99", "SW1(config-if)# switchport trunk allowed vlan 10,20,99"], "Trunk")),
        ("Part A: router subinterfaces", ios(["R1(config)# interface Gi0/0/0", "R1(config-if)# no shutdown", "R1(config-if)# interface Gi0/0/0.10", "R1(config-subif)# encapsulation dot1Q 10", "R1(config-subif)# ip address 192.168.10.1 255.255.255.0", "R1(config-subif)# interface Gi0/0/0.20", "R1(config-subif)# encapsulation dot1Q 20", "R1(config-subif)# ip address 192.168.20.1 255.255.255.0", "R1(config-subif)# interface Gi0/0/0.99", "R1(config-subif)# encapsulation dot1Q 99 native"], "Subinterfaces") + "<p>Ping PC-Guest from PC-Staff. It should work now, which is exactly why lesson 3.9 adds an ACL.</p>"),
        ("Part B: Layer 3 switch", ios(["DSW1(config)# ip routing", "DSW1(config)# interface vlan 10", "DSW1(config-if)# ip address 192.168.10.1 255.255.255.0", "DSW1(config-if)# no shutdown", "DSW1(config-if)# interface vlan 20", "DSW1(config-if)# ip address 192.168.20.1 255.255.255.0", "DSW1(config-if)# no shutdown", "DSW1(config-if)# interface Gi1/0/24", "DSW1(config-if)# no switchport", "DSW1(config-if)# ip address 10.0.0.1 255.255.255.252"], "SVIs") + "<p>Then remove <code>ip routing</code> and test again, to see the classic failure for yourself. Put it back.</p>"),
        ("Part C: HSRP on R-A", ios(["R-A(config)# interface G0/1", "R-A(config-if)# ip address 192.168.100.2 255.255.255.0", "R-A(config-if)# no shutdown", "R-A(config-if)# standby version 2", "R-A(config-if)# standby 1 ip 192.168.100.1", "R-A(config-if)# standby 1 priority 110", "R-A(config-if)# standby 1 preempt"], "HSRP primary")),
        ("Part C: HSRP on R-B", ios(["R-B(config)# interface G0/1", "R-B(config-if)# ip address 192.168.100.3 255.255.255.0", "R-B(config-if)# no shutdown", "R-B(config-if)# standby version 2", "R-B(config-if)# standby 1 ip 192.168.100.1", "R-B(config-if)# standby 1 preempt"], "HSRP standby")),
        ("Fail over", "<p>From the PC run <code>ping -t 192.168.100.1</code>, then shut R-A's G0/1. Watch R-B become active, then bring R-A back and watch it preempt. Run <code>arp -a</code> on the PC: the gateway's MAC is the HSRP virtual MAC, not a router's own.</p>"),
        ("Verify", ios(["R1# show ip interface brief", "R1# show ip route", "DSW1# show ip route", "DSW1# show interfaces vlan 10", "R-A# show standby brief", "R-A# show standby"], "Verify"))],
      verify="PCs in VLAN 10 and 20 ping each other through R1 and then through DSW1; show standby brief shows R-A Active and R-B Standby, and the roles swap and swap back when R-A's link is shut and restored.",
      limits=["Some Packet Tracer guides use <code>encapsulation dot1Q 99 native</code> on the ISR4331; support on every image is UNVERIFIED. If rejected, leave VLAN 99 off the router.",
              "HSRP on the Packet Tracer 3650 is UNVERIFIED, which is why Part C uses 2911 routers. VRRP and GLBP are UNVERIFIED in Packet Tracer and are theory only here.",
              "Cisco NetAcad publishes official Packet Tracer activities for router on a stick inter-VLAN routing if you want more practice.", PT_GENERIC]),
    takeaways=["Every VLAN needs a gateway that routes and, ideally, filters.", "Router on a stick: dot1Q subinterfaces over one trunk.", "Layer 3 switch: ip routing plus SVIs; no switchport for routed links.",
      "HSRP gives hosts a virtual gateway; configure preempt deliberately.", "Authenticate FHRP hellos where you can."])

# ------------------------------------------------------------------ 3.7
TOPO7 = topo(760, 300, {"p1": (50, 70, "pc", "PC1", "192.168.1.10"), "r1": (230, 70, "router", "R1"), "r2": (530, 70, "router", "R2"), "r3": (380, 230, "router", "R3"),
                        "p3": (710, 40, "pc", "PC3", "192.168.3.10"), "s3": (710, 130, "server", "Server3", "192.168.3.100")},
  [("p1", "r1", "", "Gi0/0/0"), ("r1", "r2", "Gi0/0/1 .1", ".2 Gi0/0/1", "ln-p"), ("r1", "r3", "Gi0/0/2 .1", ".2 Gi0/0/1"), ("r2", "r3", "Gi0/0/2 .1", ".2 Gi0/0/0"), ("r2", "p3", "Gi0/0/0", ""), ("r2", "s3", "", "")],
  "Lab 3.7 topology: R1 reaches LAN3 behind R2 directly or through R3")

RGAME = dict(routes=[
  dict(c="C", src="connected", p="192.168.1.0/24", ad=0, m=0, via="Gi0/0/0"),
  dict(c="S", src="static", p="192.168.3.0/24", ad=1, m=0, via="10.0.12.2"),
  dict(c="S", src="static (floating)", p="192.168.3.0/24", ad=5, m=0, via="10.0.13.2"),
  dict(c="S", src="static", p="192.168.3.100/32", ad=1, m=0, via="10.0.13.2"),
  dict(c="O", src="OSPF", p="10.20.0.0/16", ad=110, m=20, via="10.0.12.2"),
  dict(c="R", src="RIP", p="10.20.30.0/24", ad=120, m=2, via="10.0.13.2"),
  dict(c="D", src="EIGRP", p="10.20.0.0/16", ad=90, m=3072, via="10.0.13.2")],
  dests=["192.168.3.100", "192.168.3.50", "10.20.30.5", "10.20.99.1", "192.168.1.20", "172.16.5.5", "10.21.0.1"])

def lesson_ccna_7():
  S = []
  S.append(dict(id="table", h="Reading a routing table", hi_h="Routing table padhna",
    body=f'''{ios(["R1# show ip route", "Codes: L - local, C - connected, S - static, O - OSPF", "       * - candidate default", "", "Gateway of last resort is not set", "", "C        10.0.12.0/30 is directly connected, GigabitEthernet0/0/1", "L        10.0.12.1/32 is directly connected, GigabitEthernet0/0/1", "S        192.168.3.0/24 [1/0] via 10.0.12.2", "O        10.20.0.0/16 [110/20] via 10.0.12.2, 00:01:12, GigabitEthernet0/0/1"], "A routing table")}
<ul><li><strong>Code</strong>: C connected, L local (the router's own address as a /32), S static, O OSPF, and an asterisk marks a candidate default route.</li>
<li><strong>Prefix and length</strong>: the destination network.</li><li><strong>[AD/metric]</strong>: administrative distance (how much the router trusts the source) and the protocol's metric (how far).</li>
<li><strong>via</strong>: the next hop, then for dynamic routes the age and the exit interface.</li>
<li><strong>Gateway of last resort</strong>: the default route, used when nothing more specific matches.</li></ul>''',
    hi="Routing table mein code (C connected, L local, S static, O OSPF, * default), prefix, [AD/metric], next hop aur exit interface hota hai. Gateway of last resort matlab default route."))

  S.append(dict(id="decision", h="How a router picks a route", hi_h="Router route kaise chunta hai",
    body=f'''<ol><li><strong>Longest prefix match first.</strong> Of all routes that contain the destination, the most specific wins. A /32 beats a /24, which beats a /16, which beats the /0 default. This happens no matter what the AD is.</li>
<li><strong>AD only for identical prefixes.</strong> When two sources offer the same prefix and length, only the lowest AD enters the table.</li>
<li><strong>Metric</strong> breaks ties within one routing protocol.</li></ol>
{table(["Source", "Default AD"], [["Connected", "0"], ["Static", "1"], ["eBGP", "20"], ["EIGRP (internal)", "90"], ["OSPF", "110"], ["RIP", "120"], ["EIGRP (external)", "170"], ["iBGP", "200"], ["Unusable", "255"]], "Administrative distance")}
<p>Practise with the game. This router has no default route, so a packet that matches nothing is dropped.</p>
{route_game(RGAME)}''',
    hi="Pehle longest prefix match: /32 /24 se jeetega, /24 /16 se, chahe AD kuch bhi ho. AD sirf same prefix ke beech decide karta hai: connected 0, static 1, EIGRP 90, OSPF 110, RIP 120. Metric ek protocol ke andar tie todta hai. Game khelo: is router pe default route nahi hai."))

  S.append(dict(id="static", h="Static routes: network, default, host and floating", hi_h="Static route types",
    body=f'''{ios(["! network route via a next hop (recursive: the router then looks up how to reach 10.0.12.2)", "R1(config)# ip route 192.168.3.0 255.255.255.0 10.0.12.2", "! exit interface only: fine on point to point links, avoid on Ethernet", "R1(config)# ip route 192.168.3.0 255.255.255.0 GigabitEthernet0/0/1", "! fully specified: both", "R1(config)# ip route 192.168.3.0 255.255.255.0 GigabitEthernet0/0/1 10.0.12.2", "! default route", "R2(config)# ip route 0.0.0.0 0.0.0.0 10.0.12.1", "! host route", "R1(config)# ip route 192.168.3.100 255.255.255.255 10.0.13.2", "! floating static: AD 5, only used if the AD 1 route disappears", "R1(config)# ip route 192.168.3.0 255.255.255.0 10.0.13.2 5", "! IPv6 equivalents", "R1(config)# ipv6 route 2001:db8:1:3::/64 2001:db8:12::2", "R1(config)# ipv6 route ::/0 2001:db8:12::2"], "Static routes")}
<ul><li>A floating static sits in the running config but stays out of the routing table while the primary route is installed.</li>
<li>A static route via a next hop stays installed as long as the router can still reach that next hop through an up interface. If the far router dies but your local interface stays up, the route usually stays too, and traffic is black holed. That is why real networks pair statics with tracking or use a routing protocol.</li>
<li>For IPv6, if the next hop is a link-local address (fe80::), you must also name the exit interface.</li></ul>''',
    hi="Static route next hop IP se (recursive lookup), exit interface se (sirf point to point pe) ya dono se. Default 0.0.0.0/0, host route /32, floating static higher AD ke saath (jaise 5), jo primary girne pe hi table mein aata hai. Local interface up rahe aur door ka router mar jaaye toh route rehta hai aur traffic black hole hota hai."))

  S.append(dict(id="return-path", h="Troubleshooting: it is always the way back", hi_h="Return path troubleshooting",
    body=f'''<p>A ping needs a route there <em>and</em> a route back. Most static routing tickets are a forgotten return route on the far router. Work hop by hop: <code>show ip route</code> on each router for the destination and for the source, then <code>traceroute</code> (on a PC: <code>tracert</code>) to see where packets stop.</p>
{ios(["R1# show ip route 192.168.3.100", "Routing entry for 192.168.3.100/32", '  Known via "static", distance 1, metric 0', "  Routing Descriptor Blocks:", "  * 10.0.13.2", "      Route metric is 0, traffic share count is 1"], "Which route is used for one destination")}
{attack("<p>Routers are not usually attacked through static routes over the wire, but a compromised admin account can add one quietly: send a subnet's traffic through a capture box, or black hole a monitoring server so alerts never arrive. Asymmetric paths also break stateful firewalls, which see only half of each session and drop it.</p>")}
{defend("<p>Strong AAA and MFA for device logins (lesson 3.12), configuration change logging to syslog (lesson 3.11), regular config backups you can diff, and a review of <code>show ip route</code> after every change. Null routes are a defensive tool too: <code>ip route 198.51.100.0 255.255.255.0 Null0</code> silently drops traffic to a known bad prefix.</p>")}''',
    hi="Ping ko jaane aur wapas aane dono ka route chahiye. Zyada tar problem far router pe return route bhoolna hota hai. Har hop pe show ip route aur traceroute. Compromised admin chupke se route daal ke traffic capture ya monitoring black hole kar sakta hai: AAA, MFA, change logging aur config backups se bachav. Null0 route bad prefix ko drop karta hai."))

  S.append(dict(id="practice", h="Practise on R1", hi_h="R1 pe practice",
    body=f'''{ios_sim(dict(id="l37", kind="router", host="R1", ifaces=["GigabitEthernet0/0/0", "GigabitEthernet0/0/1", "GigabitEthernet0/0/2"], up=["GigabitEthernet0/0/0", "GigabitEthernet0/0/1", "GigabitEthernet0/0/2"],
  init={"GigabitEthernet0/0/0": {"shut": False, "ip": "192.168.1.1", "mask": "255.255.255.0"}, "GigabitEthernet0/0/1": {"shut": False, "ip": "10.0.12.1", "mask": "255.255.255.252"}, "GigabitEthernet0/0/2": {"shut": False, "ip": "10.0.13.1", "mask": "255.255.255.252"}},
  intro=["R1 from the lab, interfaces already addressed. R2 is 10.0.12.2, R3 is 10.0.13.2, LAN3 is 192.168.3.0/24 behind R2."],
  missions=[
    dict(t="Look at the routing table. How many connected (C) networks does R1 have? Type <code>answer N</code>.", hint="enable, show ip route", c=dict(type="answer", v="3")),
    dict(t="Add the primary route to LAN3 via R2.", hint="configure terminal, ip route 192.168.3.0 255.255.255.0 10.0.12.2", c=dict(type="run", re=r"^ip route 192\.168\.3\.0 255\.255\.255\.0 10\.0\.12\.2$")),
    dict(t="Add a floating backup to LAN3 via R3 with AD 5.", hint="ip route 192.168.3.0 255.255.255.0 10.0.13.2 5", c=dict(type="run", re=r"^ip route 192\.168\.3\.0 255\.255\.255\.0 10\.0\.13\.2 5$")),
    dict(t="Is the floating route in the routing table right now? Type <code>answer yes</code> or <code>answer no</code>.", hint="do show ip route", c=dict(type="answer", v="no"), ok="No. Only the AD 1 route is installed; the AD 5 route waits in the running config."),
    dict(t="Send traffic for Server3 (192.168.3.100) via R3 with a host route.", hint="ip route 192.168.3.100 255.255.255.255 10.0.13.2", c=dict(type="run", re=r"^ip route 192\.168\.3\.100 255\.255\.255\.255 10\.0\.13\.2$")),
    dict(t="Ask R1 which route it uses for 192.168.3.100.", hint="do show ip route 192.168.3.100", c=dict(type="out", re=r"Routing entry for 192\.168\.3\.100/32")),
    dict(t="Add the IPv6 route to LAN3 via R2.", hint="ipv6 unicast-routing, then ipv6 route 2001:db8:1:3::/64 2001:db8:12::2", c=dict(type="run", re=r"^ipv6 route 2001:DB8:1:3::/64 2001:DB8:12::2$")),
    dict(t="Simulate losing the R2 link: shut Gi0/0/1, then look at the routing table again.", hint="interface g0/0/1, shutdown, end, show ip route", c=dict(type="out", re=r"S\s+192\.168\.3\.0/24 \[5/0\] via 10\.0\.13\.2"), ok="The floating route took over as [5/0] via R3."),
    dict(t="Restore Gi0/0/1 and save.", hint="interface g0/0/1, no shutdown, end, copy running-config startup-config", c=dict(type="saved"))]), "R1 static routes")}''',
    hi="Simulator mein R1: connected routes gino, primary route R2 se, floating AD 5 R3 se, host route Server3 ke liye, show ip route 192.168.3.100, IPv6 route, Gi0/0/1 shut karke floating route ko kaam karte dekho, phir restore aur save."))

  return dict(
    slug="learn-ccna-static-routing", stage=3, n="3.7", minutes=60, level="Intermediate",
    title="The Routing Table and Static Routing (IPv4 and IPv6)", short="Reading the routing table, longest prefix match, administrative distance, and default, host and floating static routes.",
    seo_title="Routing Table and Static Routes for CCNA: Longest Match, AD, Floating Static | CyberWithMadhav",
    desc="Free CCNA lesson: read a routing table, see why longest prefix match beats administrative distance, and configure IPv4 and IPv6 network, default, host and floating static routes, with a route game, IOS simulator and Packet Tracer lab.",
    kw="ccna static routing, longest prefix match, administrative distance table, floating static route, default route 0.0.0.0, host route /32, ipv6 static route, show ip route explained, packet tracer static routing lab",
    kicker="$ lesson 3.7 --track ccna --domain routing", hi_title="Routing table aur static routing",
    lead="Every packet a router forwards is a lookup in one table. Learn to read that table line by line, predict which route wins, and build static routes, including the backup kind that waits quietly until the primary path fails.",
    hi_lead="Router har packet ke liye ek table dekhta hai. Use padhna, kaunsa route jeetega predict karna aur static routes (backup wale bhi) banana seekho.",
    goals=["Read every field of a routing table entry", "Pick the winning route using longest prefix match, then AD, then metric", "Configure IPv4 and IPv6 network, default, host and floating static routes", "Troubleshoot missing return routes with show ip route and traceroute"],
    sections=S,
    cards=[("What decides first, prefix length or AD?", "Prefix length (longest match)."), ("AD of static?", "1"), ("AD of OSPF?", "110"), ("AD of EIGRP internal?", "90"),
      ("What is a floating static?", "A static with a higher AD that is only used if the primary disappears."), ("Default route?", "ip route 0.0.0.0 0.0.0.0 <next hop>"),
      ("Code L in show ip route?", "The router's own interface address as a /32."), ("IPv6 static via link-local next hop needs?", "The exit interface too.")],
    quiz=[("Routes: OSPF 10.1.0.0/16 and RIP 10.1.1.0/24. Destination 10.1.1.9 uses?", ["OSPF, lower AD", "RIP, longer prefix", "Both, load shared", "Neither"], 1, "Longest prefix match comes before AD."),
      ("Which line adds a floating backup default route?", ["ip route 0.0.0.0 0.0.0.0 203.0.113.1", "ip route 0.0.0.0 0.0.0.0 203.0.113.9 200", "ip default-gateway 203.0.113.9", "ip route 0.0.0.0 255.255.255.255 203.0.113.9"], 1, "A higher AD makes it float."),
      ("Ping from LAN1 to LAN3 fails. R1 has a route to LAN3. What is the next thing to check?", ["R1's banner", "That R2 has a route back to LAN1", "DNS", "VLAN 1"], 1, "Traffic needs a path back."),
      ("Two static routes for 192.168.3.0/24 with AD 1 and AD 5. What is in the routing table?", ["Both", "Only the AD 1 route", "Only the AD 5 route", "Neither"], 1, "Only the best AD for the same prefix is installed."),
      ("Why avoid an exit interface only static on Ethernet?", ["It is not supported", "The router must ARP for every destination on that segment", "It disables CDP", "It changes the AD to 0"], 1, "It relies on proxy ARP and wastes resources."),
      ("What does <code>ip route 198.51.100.0 255.255.255.0 Null0</code> do?", ["Routes to the internet", "Drops traffic to that prefix", "Creates a loop", "Enables NAT"], 1, "A black hole route.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.7: static, host and floating routes", time="50 minutes",
      needs=PT_NEEDS + " Devices: 3 x ISR4331, 2 x 2960, PC1, PC3, Server3. Enable <code>ipv6 unicast-routing</code> on every router.",
      topo=fig(TOPO7, "R1 to R2 on 10.0.12.0/30, R1 to R3 on 10.0.13.0/30, R2 to R3 on 10.0.23.0/30. LAN1 behind R1, LAN3 (PC3 and Server3) behind R2.", "Lab topology"),
      addr=[["R1", "Gi0/0/0", "192.168.1.1/24, 2001:db8:1:1::1/64", "LAN1"], ["R1", "Gi0/0/1", "10.0.12.1/30, 2001:db8:12::1/64", "to R2"], ["R1", "Gi0/0/2", "10.0.13.1/30, 2001:db8:13::1/64", "to R3"],
            ["R2", "Gi0/0/1", "10.0.12.2/30, 2001:db8:12::2/64", "to R1"], ["R2", "Gi0/0/2", "10.0.23.1/30, 2001:db8:23::2/64", "to R3"], ["R2", "Gi0/0/0", "192.168.3.1/24, 2001:db8:1:3::1/64", "LAN3"],
            ["R3", "Gi0/0/1", "10.0.13.2/30, 2001:db8:13::3/64", "to R1"], ["R3", "Gi0/0/0", "10.0.23.2/30, 2001:db8:23::3/64", "to R2"],
            ["PC1", "Fa0", "192.168.1.10/24", "gw 192.168.1.1"], ["PC3", "Fa0", "192.168.3.10/24", "gw 192.168.3.1"], ["Server3", "Fa0", "192.168.3.100/24", "gw 192.168.3.1"]],
      steps=[("Address everything", "<p>Use the table. Check every router with <code>show ip interface brief</code> before adding a single route: half of all routing problems are an interface that is still shut.</p>"),
        ("R1: primary, floating and host routes", ios(["R1(config)# ip route 192.168.3.0 255.255.255.0 10.0.12.2", "R1(config)# ipv6 route 2001:db8:1:3::/64 2001:db8:12::2", "R1(config)# ip route 192.168.3.0 255.255.255.0 10.0.13.2 5", "R1(config)# ipv6 route 2001:db8:1:3::/64 2001:db8:13::3 5", "R1(config)# ip route 192.168.3.100 255.255.255.255 10.0.13.2"], "R1")),
        ("R2: default route back, plus a floating default", ios(["R2(config)# ip route 0.0.0.0 0.0.0.0 10.0.12.1", "R2(config)# ipv6 route ::/0 2001:db8:12::1", "R2(config)# ip route 0.0.0.0 0.0.0.0 10.0.23.2 5"], "R2")),
        ("R3: routes to both LANs", ios(["R3(config)# ip route 192.168.1.0 255.255.255.0 10.0.13.1", "R3(config)# ip route 192.168.3.0 255.255.255.0 10.0.23.1", "R3(config)# ipv6 route 2001:db8:1:1::/64 2001:db8:13::1", "R3(config)# ipv6 route 2001:db8:1:3::/64 2001:db8:23::2"], "R3")),
        ("Compare paths", "<p>From PC1: <code>tracert 192.168.3.10</code> should go R1, R2. <code>tracert 192.168.3.100</code> should go R1, R3, R2, because the /32 host route wins over the /24.</p>"),
        ("Fail the primary", "<p>Shut R1 Gi0/0/1 and run <code>show ip route</code> on R1: the floating route appears as [5/0] via 10.0.13.2. Ping PC3 again. Then bring Gi0/0/1 back.</p>"),
        ("Verify", ios(["R1# show ip route", "R1# show ip route static", "R1# show ip route 192.168.3.100", "R1# show ipv6 route static", "R1# show running-config | include ip route"], "Verify"))],
      verify="R1 shows S 192.168.3.0/24 [1/0] via 10.0.12.2 and S 192.168.3.100/32 [1/0] via 10.0.13.2; the AD 5 route appears only while Gi0/0/1 is shut; tracert to the server goes through R3.",
      limits=["This lab corrects one detail you may see in other guides: on a /30 only .1 and .2 are usable, so R3 uses 10.0.13.2 and R2 uses 10.0.23.1.",
              "As on real IOS, a static route via a next hop usually stays installed when the far router fails but your local interface stays up. That is why this lab shuts the local interface to test failover.", PT_GENERIC]),
    takeaways=["Longest prefix first, then AD, then metric.", "Static routes: network, default, host, floating.", "Floating statics wait in the config until the primary disappears.",
      "Every path needs a return path.", "Log and review route changes like any security relevant change."])
