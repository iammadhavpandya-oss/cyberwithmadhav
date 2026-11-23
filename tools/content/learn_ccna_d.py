"""Stage 3 (CCNA track) lessons 3.8 to 3.10. Original writing for CyberWithMadhav."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from learn_kit import *
from content.learn_ccna_a import PT_NEEDS, PT_GENERIC

G3 = ["GigabitEthernet0/0/0", "GigabitEthernet0/0/1", "GigabitEthernet0/0/2"]

# ------------------------------------------------------------------ 3.8
TOPO8 = topo(760, 330, {"sw": (380, 50, "switch", "SW0", "shared LAN"),
    "r1": (140, 160, "router", "R1", "RID 1.1.1.1"), "r2": (380, 160, "router", "R2", "RID 2.2.2.2"), "r3": (620, 160, "router", "R3", "RID 3.3.3.3"),
    "l1": (140, 290, "pc", "LAN1", "192.168.1.0/24"), "l2": (380, 290, "pc", "LAN2", "192.168.2.0/24"), "l3": (620, 290, "pc", "LAN3", "192.168.3.0/24")},
  [("sw", "r1", "", "Gi0/0/0 .1"), ("sw", "r2", "", "Gi0/0/0 .2"), ("sw", "r3", "", "Gi0/0/0 .3"),
   ("r1", "l1", "Gi0/0/1 .1", ""), ("r2", "l2", "Gi0/0/1 .1", ""), ("r3", "l3", "Gi0/0/1 .1", ""), ("r1", "r3", "Gi0/0/2 .1", "Gi0/0/2 .2", "ln-p")],
  "Lab 3.8 topology: R1, R2 and R3 share 172.16.100.0/24 through SW0, each has its own LAN, and R1 and R3 also have a point to point link 10.0.13.0/30")

STATES = svg(760, 170, ARROWDEF +
  "".join(box(10 + k * 107, 50, 96, 46, "s-g" if k == 6 else "s-p" if k == 2 else "s-n", s) for k, s in enumerate(["Down", "Init", "2-Way", "ExStart", "Exchange", "Loading", "Full"])) +
  "".join(arrow(106 + k * 107, 73, 117 + k * 107, 73) for k in range(6)) +
  '<text x="58" y="122" text-anchor="middle" font-size="11" class="t-m">no hello yet</text><text x="165" y="122" text-anchor="middle" font-size="11" class="t-m">heard a hello</text>' +
  '<text x="272" y="122" text-anchor="middle" font-size="11" class="t-m">saw my RID in theirs</text><text x="272" y="138" text-anchor="middle" font-size="11" class="t-m">DR/BDR elected here</text>' +
  '<text x="433" y="122" text-anchor="middle" font-size="11" class="t-m">swap database summaries</text><text x="591" y="122" text-anchor="middle" font-size="11" class="t-m">request missing LSAs</text>' +
  '<text x="708" y="122" text-anchor="middle" font-size="11" class="t-m">databases match</text>',
  "OSPF neighbour states from Down to Full")

OSPF8 = dict(nbrs=[dict(rid="2.2.2.2", ip="172.16.100.2", iface="GigabitEthernet0/0/0", pri=200),
                   dict(rid="3.3.3.3", ip="172.16.100.3", iface="GigabitEthernet0/0/0", pri=1),
                   dict(rid="3.3.3.3", ip="10.0.13.2", iface="GigabitEthernet0/0/2", pri=1)],
  routes=[dict(p="192.168.2.0/24", via="172.16.100.2", links=1), dict(p="2.2.2.2/32", via="172.16.100.2", rc=1),
          dict(p="192.168.3.0/24", via="172.16.100.3", links=1), dict(p="192.168.3.0/24", via="10.0.13.2", links=1),
          dict(p="3.3.3.3/32", via="172.16.100.3", rc=1), dict(p="3.3.3.3/32", via="10.0.13.2", rc=1)])

def lesson_ccna_8():
  S = []
  S.append(dict(id="linkstate", h="Link state routing in plain words", hi_h="Link state routing kya hai",
    body=f'''<p>Static routes from lesson 3.7 work until a link fails and nobody updates them. A <strong>dynamic routing protocol</strong> lets routers tell each other what they can reach and recalculate when something changes. <strong>OSPF</strong> (Open Shortest Path First) is the open standard one you will meet everywhere, and OSPFv2 carries IPv4.</p>
<ol><li>Each router finds <strong>neighbours</strong> by sending hello packets out of its OSPF interfaces (to multicast 224.0.0.5).</li>
<li>Neighbours exchange <strong>LSAs</strong> (link state advertisements): descriptions of each router's links, subnets and costs.</li>
<li>Every router in an <strong>area</strong> ends up with an identical <strong>link state database</strong> (LSDB), a map of the area.</li>
<li>Each router runs the <strong>SPF</strong> (Dijkstra) algorithm on that map, with itself as the root, and installs the lowest cost paths in its routing table as <code>O</code> routes with administrative distance 110.</li></ol>
{analogy("<p>Distance vector protocols work like asking for directions: each neighbour only tells you how far a place is. OSPF gives every router the same complete city map, and each one plans its own shortest route on it.</p>")}
<p>This lesson covers <strong>single area</strong> OSPF: everything is in area 0, the backbone. Multi area design exists for large networks and is beyond CCNA depth.</p>''',
    hi="Static routes link fail hone pe khud update nahi hote. OSPF mein routers hello bhej ke neighbours dhoondhte hain, LSAs exchange karte hain, sabke paas area ka same map (LSDB) hota hai, aur har router Dijkstra (SPF) chala ke apna shortest path nikaalta hai. Routing table mein yeh O routes hain, AD 110."))

  S.append(dict(id="neighbours", h="Becoming neighbours: states, timers and the must-match list", hi_h="Neighbour kaise bante hain",
    body=f'''{fig(STATES, "Two routers move through these states. Full means their databases are synchronised. On a shared LAN, two routers that are neither DR nor BDR stop at 2-Way with each other, and that is normal.", "Neighbour states")}
<p>Hellos go out every <strong>10 seconds</strong> on Ethernet, and a neighbour is declared dead after <strong>40 seconds</strong> of silence (the dead interval). Two routers only become neighbours when these match:</p>
{table(["Must match", "What happens if it does not"], [
  ["Area ID", "No adjacency. The hello is ignored."],
  ["Subnet and mask on the link", "No adjacency on broadcast links."],
  ["Hello and dead intervals", "No adjacency. Changing one side drops an existing neighbour when the dead timer runs out."],
  ["Authentication settings", "No adjacency."],
  ["Stub area flag", "No adjacency (not used in this lesson)."],
  ["MTU", "Neighbours get stuck in ExStart or Exchange."]], "OSPF neighbour requirements")}
<p>What does <em>not</em> need to match: the <strong>process ID</strong> in <code>router ospf 1</code>. It is local to the router. Router IDs must be unique.</p>
<p><strong>Router ID</strong> (a 32 bit name written like an IPv4 address) is chosen in this order: the <code>router-id</code> command; else the highest IP on a loopback interface that is up; else the highest IP on an active physical interface. A router ID only changes when the process restarts, so after changing it you run <code>clear ip ospf process</code>.</p>''',
    hi="Hello har 10 second, dead interval 40 second. Neighbour banne ke liye area, subnet, hello/dead timers, authentication aur stub flag match hone chahiye; MTU mismatch pe ExStart/Exchange mein atak jaate hain. Process ID local hai, match nahi karna. Router ID: router-id command, warna highest loopback IP, warna highest active interface IP. Change ke baad clear ip ospf process."))

  S.append(dict(id="dr", h="DR and BDR on shared LANs, and why point to point skips it", hi_h="DR aur BDR election",
    body=f'''<p>If ten routers share one Ethernet segment and every pair formed a full adjacency, that would be 45 adjacencies flooding the same updates. OSPF instead elects a <strong>designated router (DR)</strong> and a <strong>backup (BDR)</strong>. Everyone forms a Full adjacency with the DR and BDR; the others (<strong>DROTHERs</strong>) stay at 2-Way with each other.</p>
<ul><li>Highest <strong>OSPF interface priority</strong> wins (default 1, range 0 to 255). Priority 0 means "never be DR or BDR".</li>
<li>On a tie, the highest <strong>router ID</strong> wins.</li>
<li>The election is <strong>not preemptive</strong>. A router that joins later with a higher priority does not take over. The DR changes only if it fails (then the BDR is promoted) or the OSPF processes are restarted.</li></ul>
<p>A link with only two routers (a /30 between R1 and R3, say) gains nothing from an election. <code>ip ospf network point-to-point</code> on both ends removes the DR/BDR step and the wait that comes with it, so the adjacency forms faster. Both ends must use the same network type.</p>
{table(["Command", "Where", "Effect"], [
  ["<code>ip ospf priority 200</code>", "Interface", "Makes this router the likely DR on that segment (at the next election)."],
  ["<code>ip ospf priority 0</code>", "Interface", "Never DR or BDR on that segment."],
  ["<code>ip ospf network point-to-point</code>", "Interface, both ends", "No DR/BDR election; neighbour shows FULL/ -."]], "DR related commands")}''',
    hi="Shared LAN pe har pair ka adjacency banana waste hai, isliye DR aur BDR elect hote hain. Highest priority (default 1, 0 matlab kabhi nahi), tie pe highest router ID. Election preemptive nahi hai: baad mein aaya better router DR nahi chheenta, jab tak DR fail na ho ya process clear na karo. Do router wale link pe ip ospf network point-to-point lagao, election skip."))

  S.append(dict(id="config", h="Configuring single area OSPF", hi_h="OSPF configure karna",
    body=f'''{ios(["R1(config)# interface Loopback0", "R1(config-if)# ip address 1.1.1.1 255.255.255.255", "R1(config-if)# exit", "R1(config)# router ospf 1", "R1(config-router)# router-id 1.1.1.1", "R1(config-router)# network 172.16.100.0 0.0.0.255 area 0", "R1(config-router)# network 10.0.13.0 0.0.0.3 area 0", "R1(config-router)# network 192.168.1.0 0.0.0.255 area 0", "R1(config-router)# network 1.1.1.1 0.0.0.0 area 0", "R1(config-router)# passive-interface GigabitEthernet0/0/1", "R1(config-router)# auto-cost reference-bandwidth 10000", "! alternative to network statements, per interface:", "R1(config)# interface GigabitEthernet0/0/1", "R1(config-if)# ip ospf 1 area 0"], "Single area OSPFv2 on R1")}
<ul><li>A <code>network</code> statement does not advertise a prefix by itself. It says "run OSPF on every interface whose IP falls in this range", and those interfaces' subnets get advertised. It uses a <strong>wildcard</strong> mask: 0.0.0.255 for a /24, 0.0.0.3 for a /30, 0.0.0.0 for exactly one address.</li>
<li><code>passive-interface</code> stops hellos on a LAN port but still advertises its subnet. Every user facing interface should be passive. <code>passive-interface default</code> followed by <code>no passive-interface</code> on router links is the safer habit.</li>
<li><code>default-information originate</code> shares this router's default route with the rest of the area. Others see it as <code>O*E2 0.0.0.0/0</code>.</li></ul>''',
    hi="network command wildcard mask ke saath batata hai ki kin interfaces pe OSPF chalana hai: /24 ke liye 0.0.0.255, /30 ke liye 0.0.0.3. Ya interface pe ip ospf 1 area 0. LAN ports passive karo: hello band, subnet phir bhi advertise. default-information originate se default route baaki routers ko milta hai (O*E2)."))

  S.append(dict(id="cost", h="Cost: how OSPF picks the best path", hi_h="OSPF cost",
    body=f'''<p>OSPF's metric is <strong>cost</strong>, added up along the path. Interface cost = reference bandwidth / interface bandwidth, with a minimum of 1. The default reference is 100 Mb/s, which means FastEthernet, Gigabit and 10 Gigabit links all cost 1 and OSPF cannot tell them apart.</p>
{table(["Link", "Cost, reference 100 (default)", "Cost, reference 10000"], [["100 Mb/s", "1", "100"], ["1 Gb/s", "1", "10"], ["10 Gb/s", "1", "1"]], "Interface cost by reference bandwidth")}
<p>Fix it with <code>auto-cost reference-bandwidth 10000</code> (in Mb/s) on <strong>every</strong> router, or set a link's cost directly with <code>ip ospf cost N</code>. In the routing table, <code>[110/20]</code> means AD 110 and total cost 20. If two paths have the same cost, OSPF installs both (up to 4 by default on IOS) and shares the load.</p>
{attack("<p>A laptop on a user VLAN running routing software can speak OSPF. If that VLAN's router interface is not passive, the laptop can form an adjacency and advertise fake routes (even a better default route), pulling traffic through itself for interception or into a black hole.</p>")}
{defend("<p>Passive interfaces everywhere users live; OSPF authentication between routers (MD5 or HMAC-SHA where your platform supports it); ACLs that drop OSPF (IP protocol 89) arriving from user ports; and watching the <code>%OSPF-5-ADJCHG</code> log messages, because an unexpected new neighbour is an incident.</p>")}''',
    hi="Cost = reference bandwidth / interface bandwidth, minimum 1. Default reference 100 Mb/s hai, toh 100M, 1G aur 10G sab cost 1. Har router pe auto-cost reference-bandwidth 10000 lagao. [110/20] matlab AD 110 aur total cost 20. Equal cost paths dono install hote hain. Attacker user VLAN pe OSPF bol ke fake routes inject kar sakta hai; passive interfaces aur authentication se roko."))

  S.append(dict(id="practice", h="Practise on R1", hi_h="R1 pe practice",
    body=f'''<p>R1's interfaces are already addressed. R2 and R3 are modelled by this console: R2 has already been given OSPF priority 200 on the shared LAN by a colleague, and R3's end of the point to point link is configured to match whatever you do. All three routers use the same reference bandwidth. Treat outputs as a close guide, not a real protocol run.</p>
{ios_sim(dict(id="l38", kind="router", host="R1", ifaces=G3, up=G3,
  init={"GigabitEthernet0/0/0": dict(shut=False, ip="172.16.100.1", mask="255.255.255.0"), "GigabitEthernet0/0/1": dict(shut=False, ip="192.168.1.1", mask="255.255.255.0"), "GigabitEthernet0/0/2": dict(shut=False, ip="10.0.13.1", mask="255.255.255.252")},
  ospf=OSPF8, intro=["R1, an ISR4331. Interfaces are addressed and up. Start with enable."],
  missions=[
    dict(t="Create Loopback0 with 1.1.1.1/32.", hint="enable, configure terminal, interface loopback 0, ip address 1.1.1.1 255.255.255.255", c=dict(type="run", re=r"^interface Loopback0\n ip address 1\.1\.1\.1 255\.255\.255\.255")),
    dict(t="Start OSPF process 1 and fix the router ID at 1.1.1.1.", hint="exit, router ospf 1, router-id 1.1.1.1", c=dict(type="run", re=r"^router ospf 1\n(?:[^!]*\n)? router-id 1\.1\.1\.1$")),
    dict(t="Enable OSPF on the shared LAN 172.16.100.0/24 in area 0, and watch the neighbours come up.", hint="network 172.16.100.0 0.0.0.255 area 0", c=dict(type="run", re=r"^ network 172\.16\.100\.0 0\.0\.0\.255 area 0$"), ok="Two neighbours went to FULL on Gi0/0/0."),
    dict(t="Also run OSPF on the R1 to R3 link (10.0.13.0/30) and on LAN1 (192.168.1.0/24).", hint="network 10.0.13.0 0.0.0.3 area 0, network 192.168.1.0 0.0.0.255 area 0", c=dict(type="run", re=r"(?=[\s\S]*^ network 10\.0\.13\.0 0\.0\.0\.3 area 0$)[\s\S]*^ network 192\.168\.1\.0 0\.0\.0\.255 area 0$")),
    dict(t="LAN1 has only PCs. Stop sending hellos there but keep advertising it.", hint="passive-interface g0/0/1", c=dict(type="run", re=r"^ passive-interface GigabitEthernet0/0/1$")),
    dict(t="Who is the DR on the shared LAN? Type <code>answer RID</code>.", hint="do show ip ospf neighbor", c=dict(type="answer", v="2.2.2.2"), ok="R2, because a colleague gave it priority 200. R1 and R3 both have priority 1."),
    dict(t="And the BDR? Type <code>answer RID</code>.", hint="Same output, the FULL/BDR line", c=dict(type="answer", v="3.3.3.3"), ok="R3: priorities tie at 1, and 3.3.3.3 is a higher router ID than 1.1.1.1."),
    dict(t="Make 1 Gb/s links cost 10 instead of 1.", hint="auto-cost reference-bandwidth 10000", c=dict(type="run", re=r"^ auto-cost reference-bandwidth 10000$")),
    dict(t="The R1 to R3 link has only two routers. Remove the DR/BDR election on R1's end.", hint="interface g0/0/2, ip ospf network point-to-point", c=dict(type="run", re=r"^interface GigabitEthernet0/0/2\n[^!]*ip ospf network point-to-point")),
    dict(t="Look at the OSPF routes. What is the cost to 192.168.2.0/24? Type <code>answer N</code>.", hint="do show ip route ospf, then read [110/N]", c=dict(type="answer", v="20"), ok="10 for R1's Gi0/0/0 plus 10 for R2's LAN interface."),
    dict(t="How many equal cost paths does R1 have to 192.168.3.0/24? Type <code>answer N</code>.", hint="Count the via lines under that prefix", c=dict(type="answer", v="2"), ok="Two: through the shared LAN and through the point to point link, both cost 20. OSPF load shares across them."),
    dict(t="Give R1's Gi0/0/0 priority 255, then check the neighbours again. Who is DR now? Type <code>answer RID</code>.", hint="interface g0/0/0, ip ospf priority 255, do show ip ospf neighbor", c=dict(type="answer", v="2.2.2.2"), ok="Still R2. The election is not preemptive; R1 would only take over after clear ip ospf process or a DR failure. Remove it again with no ip ospf priority."),
    dict(t="Break it: set the hello interval on Gi0/0/0 to 5 seconds and watch what happens.", hint="interface g0/0/0, ip ospf hello-interval 5", c=dict(type="out", re=r"from FULL to DOWN"), ok="Hello and dead timers must match, so R2 and R3 stopped accepting R1's hellos on that LAN. R3 stays reachable over the point to point link."),
    dict(t="Fix it.", hint="no ip ospf hello-interval", c=dict(type="out", re=r"from LOADING to FULL")),
    dict(t="Share a default route. Create Loopback1 with 203.0.113.1/32 as a stand in internet, point a default route at it, and originate it into OSPF.", hint="interface loopback 1, ip address 203.0.113.1 255.255.255.255, exit, ip route 0.0.0.0 0.0.0.0 Loopback1, router ospf 1, default-information originate", c=dict(type="run", re=r"(?=[\s\S]*^ip route 0\.0\.0\.0 0\.0\.0\.0 Loopback1$)[\s\S]*^ default-information originate$")),
    dict(t="Save.", hint="end, copy running-config startup-config", c=dict(type="saved"))]), "R1 OSPF console")}''',
    hi="Simulator mein R1: Loopback0, router ospf 1 aur router-id, shared LAN, p2p link aur LAN1 pe network commands, LAN1 passive, DR aur BDR pehchano, reference bandwidth 10000, p2p network type, cost padho, priority 255 se dekho ki election preemptive nahi, hello timer tod ke theek karo, default route share karo, save."))

  return dict(
    slug="learn-ccna-ospf", stage=3, n="3.8", minutes=70, level="Intermediate to advanced",
    title="Single Area OSPFv2: Neighbours, DR/BDR, Cost and Troubleshooting", short="Link state routing, neighbour rules, DR and BDR, cost, passive interfaces and a default route.",
    seo_title="OSPF for CCNA: Single Area OSPFv2, DR BDR Election, Cost, Passive Interface | CyberWithMadhav",
    desc="Free CCNA lesson on single area OSPFv2: link state basics, neighbour states and must-match rules, router ID, DR and BDR election, point to point links, cost and reference bandwidth, with an IOS simulator and Packet Tracer lab.",
    kw="ospf tutorial, single area ospfv2, ospf dr bdr election, ospf neighbor states, ospf cost reference bandwidth, passive-interface ospf, default-information originate, packet tracer ospf lab, ccna ospf",
    kicker="$ lesson 3.8 --track ccna --domain routing", hi_title="Single area OSPF",
    lead="Static routes do not notice when a link dies. OSPF does. Learn how routers discover each other, agree on one map of the network, elect a DR on shared LANs, choose paths by cost, and how a single mismatched timer can quietly break it all.",
    hi_lead="Static routes ko link failure ka pata nahi chalta, OSPF ko chalta hai. Neighbours, LSDB, DR election, cost aur troubleshooting seekho.",
    goals=["Explain how OSPF neighbours form and build a shared LSDB", "Configure single area OSPFv2 with a fixed router ID and passive interfaces", "Predict DR and BDR election results and use point to point links", "Read OSPF costs and equal cost paths in the routing table", "Troubleshoot neighbours that will not reach FULL"],
    sections=S,
    cards=[("OSPF administrative distance?", "110."), ("Default hello and dead on Ethernet?", "10 s and 40 s."), ("Router ID order?", "router-id command, highest up loopback IP, highest active interface IP."),
      ("Must the process ID match?", "No, it is local. The area must match."), ("DR election tie breaker?", "Highest priority, then highest router ID."), ("Priority 0 means?", "Never DR or BDR."),
      ("Default reference bandwidth?", "100 Mb/s, so every link 100 Mb/s or faster costs 1."), ("What does passive-interface do?", "Stops hellos but still advertises the subnet.")],
    quiz=[("Two routers on the same link show no OSPF neighbour. Which mismatch causes this?", ["Different process IDs", "Different hello intervals", "Different hostnames", "Different router ID formats"], 1, "Hello and dead timers must match. Process IDs are local."),
      ("A router with priority 255 joins a LAN that already has a DR with priority 1. What happens?", ["It becomes DR immediately", "Nothing changes until the DR fails or OSPF is restarted", "Both become DR", "The old DR goes to priority 0"], 1, "DR election is not preemptive."),
      ("Two DROTHERs on a shared LAN show 2WAY/DROTHER with each other. This is:", ["A broken adjacency", "Normal", "An MTU mismatch", "An authentication failure"], 1, "DROTHERs only go Full with the DR and BDR."),
      ("With the default reference bandwidth, what is the cost of a 10 Gb/s link?", ["1", "10", "100", "0.01"], 0, "100 / 10000 is below 1, and the minimum cost is 1."),
      ("Which wildcard matches the 10.0.13.0/30 subnet in a network statement?", ["255.255.255.252", "0.0.0.3", "0.0.0.4", "0.0.3.255"], 1, "A /30 has 4 addresses, so the wildcard is 0.0.0.3."),
      ("Why make LAN interfaces passive?", ["To save power", "So nobody on the LAN can form an OSPF adjacency, while the subnet is still advertised", "To stop the LAN subnet being advertised", "To make the router the DR"], 1, "It blocks rogue OSPF speakers and wasted hellos.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.8: OSPF with DR election and a point to point link", time="55 minutes",
      needs=PT_NEEDS + " Devices: 3 x ISR4331, 4 x 2960 (SW0 for the shared LAN plus one per LAN), 3 x PC-PT.",
      topo=fig(TOPO8, "R1, R2 and R3 Gi0/0/0 on SW0 (172.16.100.0/24). Each Gi0/0/1 to its own LAN switch. R1 Gi0/0/2 to R3 Gi0/0/2 (10.0.13.0/30).", "Lab topology"),
      addr=[["R1", "Gi0/0/0 / Gi0/0/1 / Gi0/0/2", "172.16.100.1/24 / 192.168.1.1/24 / 10.0.13.1/30", "Lo0 1.1.1.1/32"], ["R2", "Gi0/0/0 / Gi0/0/1", "172.16.100.2/24 / 192.168.2.1/24", "Lo0 2.2.2.2/32"],
            ["R3", "Gi0/0/0 / Gi0/0/1 / Gi0/0/2", "172.16.100.3/24 / 192.168.3.1/24 / 10.0.13.2/30", "Lo0 3.3.3.3/32"], ["PC1 / PC2 / PC3", "Fa0", "192.168.1.10 / 192.168.2.10 / 192.168.3.10 (/24)", "gateway .1 in each LAN"]],
      steps=[("Address everything, including loopbacks", "<p>Use the table. Bring every router interface up with <code>no shutdown</code> and ping across each link before touching OSPF.</p>"),
        ("OSPF on R1 (adapt the networks for R2 and R3)", ios(["R1(config)# router ospf 1", "R1(config-router)# router-id 1.1.1.1", "R1(config-router)# network 172.16.100.0 0.0.0.255 area 0", "R1(config-router)# network 10.0.13.0 0.0.0.3 area 0", "R1(config-router)# network 192.168.1.0 0.0.0.255 area 0", "R1(config-router)# network 1.1.1.1 0.0.0.0 area 0", "R1(config-router)# passive-interface GigabitEthernet0/0/1", "R1(config-router)# auto-cost reference-bandwidth 10000", "R1(config)# interface GigabitEthernet0/0/2", "R1(config-if)# ip ospf network point-to-point"], "R1") + "<p>Use the same reference bandwidth on all three routers and set point to point on R3's Gi0/0/2 too.</p>"),
        ("Make R2 the DR", ios(["R2(config)# interface GigabitEthernet0/0/0", "R2(config-if)# ip ospf priority 200", "R1# clear ip ospf process", "Reset ALL OSPF processes? [no]: yes"], "Priority") + "<p>Run <code>clear ip ospf process</code> on all three routers, because the election is not preemptive.</p>"),
        ("Share a default route from R1", ios(["R1(config)# interface Loopback1", "R1(config-if)# ip address 203.0.113.1 255.255.255.255", "R1(config-if)# exit", "R1(config)# ip route 0.0.0.0 0.0.0.0 Loopback1", "R1(config)# router ospf 1", "R1(config-router)# default-information originate"], "Default route")),
        ("Break and fix", ios(["R3(config)# interface GigabitEthernet0/0/0", "R3(config-if)# ip ospf hello-interval 5", "! wait for the dead timer, watch the ADJCHG messages, then:", "R3(config-if)# no ip ospf hello-interval"], "Timer mismatch")),
        ("Verify", ios(["R1# show ip ospf neighbor", "R1# show ip ospf interface brief", "R1# show ip protocols", "R2# show ip route ospf", "R1# show ip ospf database"], "Verify"))],
      verify="On R1, show ip ospf neighbor lists R2 as FULL/DR and R3 as FULL/BDR on Gi0/0/0, and R3 again as FULL/ - on Gi0/0/2. R2 and R3 show O routes to the other LANs and an O*E2 default route. PC1 pings PC2 and PC3.",
      limits=["You will not see 2WAY/DROTHER with only three routers. Add a fourth router to SW0 if you want to see two DROTHERs at 2-Way with each other.",
              "<code>show ip ospf interface brief</code> is reported by a third party site as added in Packet Tracer 8.2. UNVERIFIED against Cisco release notes; use <code>show ip ospf interface</code> if it is missing.",
              "<code>ip ospf network point-to-point</code> on Packet Tracer Ethernet interfaces is UNVERIFIED. If it is rejected, leave that link as broadcast: the two routers will elect a DR and BDR, and everything else still works.",
              "The interface form <code>ip ospf 1 area 0</code> is UNVERIFIED on every Packet Tracer image. The network statements above are the reliable way.",
              "OSPF authentication in Packet Tracer is UNVERIFIED and outside this lesson's depth.", PT_GENERIC]),
    takeaways=["OSPF routers share one map per area and each runs SPF on it.", "Area, subnet, timers and authentication must match; the process ID does not.", "DR and BDR: highest priority then router ID, and the election is not preemptive.",
      "Raise the reference bandwidth on every router so fast links get different costs.", "Make user facing interfaces passive, and treat an unexpected new neighbour as an incident."])

# ------------------------------------------------------------------ 3.9
TOPO9 = topo(760, 300, {"r1": (380, 50, "router", "R1", "ISR4331"), "sw1": (200, 150, "switch", "SW1", "2960, SVI .99.2"), "sw2": (600, 150, "switch", "SW2"),
    "ps": (70, 260, "pc", "PC-Staff", "192.168.10.10"), "pg": (200, 260, "pc", "PC-Guest", "192.168.20.10"), "pa": (330, 260, "pc", "Admin-PC", "192.168.99.10"),
    "srv": (600, 255, "server", "Server-Web", "10.10.10.10")},
  [("r1", "sw1", "Gi0/0/0 .10 .20 .99", "Gi0/1 trunk", "ln-p"), ("r1", "sw2", "Gi0/0/1 10.10.10.1", ""), ("sw1", "ps", "", "VLAN 10"), ("sw1", "pg", "", "VLAN 20"), ("sw1", "pa", "", "VLAN 99"), ("sw2", "srv", "", "")],
  "Lab 3.9 topology: router on a stick for VLANs 10, 20 and 99, with a web and DNS server behind R1 Gi0/0/1")

GUEST_ACL = """ip access-list extended GUEST-IN
 10 permit udp 192.168.20.0 0.0.0.255 host 10.10.10.10 eq domain
 15 permit icmp 192.168.20.0 0.0.0.255 host 10.10.10.10 echo
 20 permit tcp 192.168.20.0 0.0.0.255 host 10.10.10.10 eq www
 30 deny ip 192.168.20.0 0.0.0.255 192.168.0.0 0.0.255.255 log
 35 deny ip 192.168.20.0 0.0.0.255 10.0.0.0 0.255.255.255 log
 40 permit ip 192.168.20.0 0.0.0.255 any"""
ACLT9 = dict(acl=GUEST_ACL, presets=[
  dict(label="Guest looks up a name", proto="udp", src="192.168.20.10", dst="10.10.10.10", dport=53),
  dict(label="Guest opens the web server", proto="tcp", src="192.168.20.10", dst="10.10.10.10", dport=80),
  dict(label="Guest pings a staff PC", proto="icmp", src="192.168.20.10", dst="192.168.10.10", icmp="echo"),
  dict(label="Guest tries SSH to R1", proto="tcp", src="192.168.20.10", dst="192.168.99.1", dport=22),
  dict(label="Guest HTTPS to the internet", proto="tcp", src="192.168.20.10", dst="93.184.216.34", dport=443),
  dict(label="Guest HTTPS to the server", proto="tcp", src="192.168.20.10", dst="10.10.10.10", dport=443),
  dict(label="Staff packet hits this ACL", proto="tcp", src="192.168.10.10", dst="10.10.10.10", dport=80)])

def sub(v, ip):
  return dict(sub=True, shut=False, sp=False, enc=v, ip=ip, mask="255.255.255.0")
IF9 = ["GigabitEthernet0/0/0", "GigabitEthernet0/0/0.10", "GigabitEthernet0/0/0.20", "GigabitEthernet0/0/0.99", "GigabitEthernet0/0/1", "GigabitEthernet0/0/2"]

def lesson_ccna_9():
  S = []
  S.append(dict(id="how", h="How an ACL decides", hi_h="ACL kaise decide karta hai",
    body=f'''<p>An <strong>access control list</strong> is an ordered list of permit and deny lines. When a packet is checked against it, the router:</p>
<ol><li>Compares the packet with the first line, then the next, top to bottom.</li>
<li>Stops at the <strong>first line that matches</strong> and does what it says. Later lines are never read for that packet.</li>
<li>If no line matches, drops the packet. Every ACL ends with an invisible <code>deny any</code>.</li></ol>
<p>That last rule causes the classic outage: an ACL with only <code>deny host 192.168.10.10</code> does block that host, and it also blocks everyone else, because nothing is permitted. If you mean "everyone except this host", add <code>permit any</code> at the end.</p>
{table(["Type", "Numbers", "Matches on", "Place it"], [
  ["Standard", "1 to 99, 1300 to 1999", "Source IP only", "Close to the destination, so it does not block the source from everywhere else."],
  ["Extended", "100 to 199, 2000 to 2699", "Protocol, source, destination, ports, some flags", "Close to the source, so unwanted traffic is dropped before it crosses the network."]], "Standard and extended ACLs")}
<p>On an interface you get <strong>one ACL per direction per protocol</strong>: one IPv4 ACL in, one out. "In" means packets arriving on that interface, before routing. "Out" means packets leaving it, after routing. Outbound ACLs do not filter packets the router itself generates, such as its own pings or routing updates.</p>''',
    hi="ACL upar se neeche check hota hai, pehli matching line decide karti hai, aur end mein invisible deny any hota hai. Sirf deny wali ACL sabko block kar deti hai, isliye permit any lagana padta hai. Standard (1-99, 1300-1999) sirf source dekhta hai, destination ke paas lagao. Extended (100-199, 2000-2699) protocol, source, destination aur ports dekhta hai, source ke paas lagao. Interface pe ek direction mein ek hi IPv4 ACL."))

  S.append(dict(id="wildcard", h="Wildcard masks", hi_h="Wildcard masks",
    body=f'''<p>ACLs (and OSPF network statements) use <strong>wildcard masks</strong>: a 0 bit means "this bit must match", a 1 bit means "ignore this bit". For a normal subnet the wildcard is the subnet mask inverted, which you can get by subtracting each octet from 255.</p>
{table(["To match", "Address and wildcard", "Shortcut"], [
  ["One host", "192.168.10.10 0.0.0.0", "<code>host 192.168.10.10</code>"],
  ["A /24", "192.168.20.0 0.0.0.255", ""],
  ["A /26 (64 addresses)", "192.168.20.64 0.0.0.63", ""],
  ["A /30", "10.0.13.0 0.0.0.3", ""],
  ["All of 192.168.0.0 to 192.168.255.255", "192.168.0.0 0.0.255.255", ""],
  ["Everything", "0.0.0.0 255.255.255.255", "<code>any</code>"]], "Wildcard examples")}
<p>Wildcards can also match patterns a subnet mask cannot. <code>192.168.1.0 0.0.254.255</code> matches every odd third octet (192.168.1.x, 192.168.3.x and so on). You will rarely write one, but you should recognise that a wildcard is not always a contiguous block.</p>''',
    hi="Wildcard mein 0 matlab match karna zaroori, 1 matlab ignore. Normal subnet ke liye 255 mein se mask ka har octet ghatao: /24 ka 0.0.0.255, /26 ka 0.0.0.63, /30 ka 0.0.0.3. host = 0.0.0.0, any = 255.255.255.255."))

  S.append(dict(id="syntax", h="Numbered, named and extended syntax", hi_h="ACL syntax",
    body=f'''{ios(["! numbered standard", "R1(config)# access-list 10 deny host 192.168.10.10", "R1(config)# access-list 10 permit any", "! named extended, with sequence numbers", "R1(config)# ip access-list extended GUEST-IN", "R1(config-ext-nacl)# 10 permit udp 192.168.20.0 0.0.0.255 host 10.10.10.10 eq domain", "R1(config-ext-nacl)# 20 permit tcp 192.168.20.0 0.0.0.255 host 10.10.10.10 eq www", "R1(config-ext-nacl)# 30 deny ip 192.168.20.0 0.0.0.255 192.168.0.0 0.0.255.255 log", "R1(config-ext-nacl)# 40 permit ip 192.168.20.0 0.0.0.255 any", "! insert or delete one line later", "R1(config-ext-nacl)# 15 permit icmp 192.168.20.0 0.0.0.255 host 10.10.10.10 echo", "R1(config-ext-nacl)# no 30", "! apply", "R1(config)# interface GigabitEthernet0/0/0.20", "R1(config-subif)# ip access-group GUEST-IN in"], "ACL syntax")}
<ul><li>Extended line order: <code>action protocol source [source port] destination [destination port] [options]</code>. Ports need <code>tcp</code> or <code>udp</code>.</li>
<li>Port operators: <code>eq</code>, <code>neq</code>, <code>gt</code>, <code>lt</code>, <code>range</code>. Names like <code>www</code> (80) and <code>domain</code> (53) are accepted.</li>
<li><code>established</code> matches TCP packets with ACK or RST set, which is a cheap way to allow replies. It is a flag check, not session tracking, so it is not a stateful firewall.</li>
<li><strong>Named</strong> ACLs give each line a sequence number, so you can insert line 15 between 10 and 20 or delete one line, instead of deleting and retyping a numbered list.</li></ul>''',
    hi="Extended order: action, protocol, source, source port, destination, destination port. Ports ke liye tcp ya udp chahiye. eq, neq, gt, lt, range. established sirf ACK/RST flag check hai, stateful firewall nahi. Named ACL mein sequence numbers se beech mein line daal sakte ho ya ek line hata sakte ho."))

  S.append(dict(id="tester", h="Try it: walk a packet through GUEST-IN", hi_h="ACL tester",
    body=f'''<p>This is the guest VLAN policy from the lab. Pick an example packet, or edit the ACL and type your own, then read the trace to see exactly which line decided.</p>
{acl_tester(ACLT9)}
<p>Notice the last example. GUEST-IN only matches guest sources, so a staff packet falls through to the implicit deny. That is fine, because the ACL is applied only on the guest subinterface, but it shows why applying an ACL to the wrong interface breaks things.</p>''',
    hi="Example packets chuno ya ACL edit karo, aur trace mein dekho kaunsi line ne decide kiya. Staff packet implicit deny pe girta hai: ACL galat interface pe lagao toh yahi outage hota hai."))

  S.append(dict(id="mgmt", h="Protecting the router itself", hi_h="Management access lock karna",
    body=f'''<p>An ACL on a data interface does not protect SSH to the router from every direction. For the VTY lines use <code>access-class</code>, which filters who may open a remote session, whichever interface they arrive on.</p>
{ios(["R1(config)# ip access-list standard MGMT-ONLY", "R1(config-std-nacl)# permit 192.168.99.0 0.0.0.255", "R1(config-std-nacl)# deny any log", "R1(config)# line vty 0 4", "R1(config-line)# access-class MGMT-ONLY in"], "VTY access")}
{attack("<p>Once one guest laptop is compromised, a flat network lets the attacker scan and reach everything: staff PCs, printers, and the SSH prompt of every router and switch, where password guessing starts. The same goes for spoofed traffic arriving from the internet claiming to come from your own private ranges.</p>")}
{defend("<p>Extended ACLs between VLANs so guests reach only what they need, <code>access-class</code> on every device's VTY lines so only the admin subnet can even try to log in, <code>log</code> on the important deny lines (sent to syslog in lesson 3.11), and edge filters that drop inbound packets with RFC 1918 or your own internal source addresses (the idea behind BCP 38).</p>")}''',
    hi="Router ke SSH ko bachane ke liye line vty pe access-class lagao, sirf admin subnet allowed. Attack: ek guest laptop compromise hua toh flat network mein sab reachable. Defence: VLANs ke beech extended ACLs, VTY pe access-class, deny lines pe log, aur internet se aane wale private source addresses drop karo."))

  S.append(dict(id="practice", h="Practise on R1", hi_h="R1 pe practice",
    body=f'''<p>R1 already routes for VLANs 10, 20 and 99 (router on a stick, as in lesson 3.6) and reaches the server LAN on Gi0/0/1. Match counters in this console are sample numbers, standing in for real traffic.</p>
{ios_sim(dict(id="l39", kind="router", host="R1", ifaces=IF9, up=IF9,
  init={"GigabitEthernet0/0/0": dict(shut=False), "GigabitEthernet0/0/0.10": sub(10, "192.168.10.1"), "GigabitEthernet0/0/0.20": sub(20, "192.168.20.1"), "GigabitEthernet0/0/0.99": sub(99, "192.168.99.1"), "GigabitEthernet0/0/1": dict(shut=False, ip="10.10.10.1", mask="255.255.255.0")},
  hits={"GUEST-IN": {"10": 14, "15": 4, "20": 31, "30": 6, "35": 2, "40": 52}, "MGMT-ONLY": {"10": 3, "20": 2}, "10": {"10": 5, "20": 40}},
  intro=["R1, an ISR4331 doing router on a stick. Start with enable."],
  missions=[
    dict(t="Create the named extended ACL GUEST-IN with two lines: 10 allows guests DNS to 10.10.10.10, 20 allows guests HTTP to it.", hint="enable, configure terminal, ip access-list extended GUEST-IN, 10 permit udp 192.168.20.0 0.0.0.255 host 10.10.10.10 eq domain, 20 permit tcp 192.168.20.0 0.0.0.255 host 10.10.10.10 eq www", c=dict(type="run", re=r"^ip access-list extended GUEST-IN\n permit udp 192\.168\.20\.0 0\.0\.0\.255 host 10\.10\.10\.10 eq domain\n permit tcp 192\.168\.20\.0 0\.0\.0\.255 host 10\.10\.10\.10 eq www")),
    dict(t="Line 30: deny guests to all of 192.168.0.0/16 and log it. Line 35: the same for 10.0.0.0/8.", hint="30 deny ip 192.168.20.0 0.0.0.255 192.168.0.0 0.0.255.255 log, 35 deny ip 192.168.20.0 0.0.0.255 10.0.0.0 0.255.255.255 log", c=dict(type="run", re=r"deny ip 192\.168\.20\.0 0\.0\.0\.255 192\.168\.0\.0 0\.0\.255\.255 log\n deny ip 192\.168\.20\.0 0\.0\.0\.255 10\.0\.0\.0 0\.255\.255\.255 log")),
    dict(t="Line 40: let guests reach everything else (the internet).", hint="40 permit ip 192.168.20.0 0.0.0.255 any", c=dict(type="run", re=r"log\n permit ip 192\.168\.20\.0 0\.0\.0\.255 any")),
    dict(t="Apply GUEST-IN inbound on the guest subinterface.", hint="exit, interface g0/0/0.20, ip access-group GUEST-IN in", c=dict(type="run", re=r"^interface GigabitEthernet0/0/0\.20\n[^!]*ip access-group GUEST-IN in")),
    dict(t="Without retyping anything, insert line 15 letting guests ping the server.", hint="ip access-list extended GUEST-IN, 15 permit icmp 192.168.20.0 0.0.0.255 host 10.10.10.10 echo", c=dict(type="run", re=r"eq domain\n permit icmp 192\.168\.20\.0 0\.0\.0\.255 host 10\.10\.10\.10 echo\n permit tcp")),
    dict(t="Check the counters. Which sequence number has been dropping guest traffic to the 192.168 ranges? Type <code>answer N</code>.", hint="do show access-lists", c=dict(type="answer", v="30"), ok="Line 30, with 6 matches. Counters are how you prove which line acted."),
    dict(t="Lock remote logins to the admin subnet: a standard named ACL MGMT-ONLY permitting 192.168.99.0/24 and denying everything else with logging.", hint="ip access-list standard MGMT-ONLY, permit 192.168.99.0 0.0.0.255, deny any log", c=dict(type="run", re=r"^ip access-list standard MGMT-ONLY\n permit 192\.168\.99\.0 0\.0\.0\.255\n deny any log")),
    dict(t="Apply it to VTY lines 0 to 4.", hint="line vty 0 4, access-class MGMT-ONLY in", c=dict(type="run", re=r"^line vty 0 4\n access-class MGMT-ONLY in")),
    dict(t="Standard ACL practice: numbered ACL 10 blocking only PC-Staff (192.168.10.10) and allowing everyone else.", hint="access-list 10 deny host 192.168.10.10, access-list 10 permit any", c=dict(type="run", re=r"^access-list 10 deny host 192\.168\.10\.10\naccess-list 10 permit any")),
    dict(t="A standard ACL goes close to the destination. Apply ACL 10 outbound on the server LAN interface.", hint="interface g0/0/1, ip access-group 10 out", c=dict(type="run", re=r"^interface GigabitEthernet0/0/1\n[^!]*ip access-group 10 out")),
    dict(t="What wildcard would match a /26? Type <code>answer W.X.Y.Z</code>.", hint="255.255.255.192 inverted", c=dict(type="answer", v="0.0.0.63")),
    dict(t="Save.", hint="end, copy running-config startup-config", c=dict(type="saved"))]), "R1 ACL console")}''',
    hi="Simulator mein R1: GUEST-IN banao (DNS, HTTP allow, internal ranges deny with log, baaki permit), guest subinterface pe in direction lagao, line 15 insert karo, counters padho, MGMT-ONLY se VTY lock karo, numbered ACL 10 se sirf PC-Staff ko server se roko, save."))

  return dict(
    slug="learn-ccna-access-control-lists", stage=3, n="3.9", minutes=65, level="Intermediate to advanced",
    title="Access Control Lists: Standard, Extended, Named and VTY Protection", short="Top down matching, the implicit deny, wildcards, placement, named ACL editing and locking down SSH.",
    seo_title="Cisco ACLs for CCNA: Standard vs Extended, Wildcard Masks, Named ACLs, access-class | CyberWithMadhav",
    desc="Free CCNA lesson on IPv4 access control lists: first match and the implicit deny, wildcard masks, standard and extended syntax, placement, named ACL sequence numbers and VTY access-class, with an ACL rule tester, IOS simulator and Packet Tracer lab.",
    kw="cisco acl tutorial, standard vs extended acl, wildcard mask calculator, named acl sequence numbers, ip access-group in out, access-class vty, acl implicit deny, packet tracer acl lab, ccna acl",
    kicker="$ lesson 3.9 --track ccna --domain security", hi_title="Access control lists",
    lead="ACLs are the simplest traffic policy a router can enforce, and the easiest way to cause an outage. Learn how a packet walks the list, how wildcards work, where to put each type, how to edit a live ACL safely, and how to make sure only admins can even reach the login prompt.",
    hi_lead="ACL router ki sabse simple policy hai, aur outage ka sabse aasan tareeka bhi. Matching, wildcards, placement, editing aur VTY protection seekho.",
    goals=["Predict which line of an ACL matches a packet, including the implicit deny", "Write wildcard masks for hosts, subnets and ranges", "Configure numbered and named standard and extended ACLs", "Choose the right interface and direction for each ACL", "Restrict VTY access with access-class and read match counters"],
    sections=S,
    cards=[("ACL processing order?", "Top down, first match wins, implicit deny any at the end."), ("Standard ACL number ranges?", "1 to 99 and 1300 to 1999."), ("Extended ACL number ranges?", "100 to 199 and 2000 to 2699."),
      ("Where does a standard ACL go?", "Close to the destination."), ("Where does an extended ACL go?", "Close to the source."), ("Wildcard for a /26?", "0.0.0.63."),
      ("Filter SSH to the router?", "access-class NAME in on the VTY lines."), ("Why named ACLs?", "Sequence numbers let you insert or delete single lines.")],
    quiz=[("An ACL contains only <code>access-list 5 deny host 10.1.1.5</code> and is applied. What happens to traffic from 10.1.1.6?", ["Permitted", "Denied by the implicit deny", "Logged and permitted", "Depends on the direction"], 1, "Nothing permits it, so the invisible deny any drops it."),
      ("Which wildcard matches 172.16.8.0/22?", ["0.0.3.255", "0.0.7.255", "255.255.252.0", "0.0.4.255"], 0, "A /22 has 1024 addresses: 4 in the third octet, so 0.0.3.255."),
      ("Where should an extended ACL that blocks guests from staff be placed?", ["Outbound on the staff subinterface", "Inbound on the guest subinterface", "On the VTY lines", "On the ISP router"], 1, "Close to the source, so the traffic is dropped as early as possible."),
      ("How do you stop non-admins reaching SSH on a router?", ["ip access-group on every interface", "access-class on the VTY lines", "A standard ACL outbound on the WAN", "transport input none"], 1, "access-class filters sessions to the VTYs whatever interface they arrive on."),
      ("<code>permit tcp any host 10.1.1.1 eq 22 established</code> matches:", ["New SSH connections", "TCP packets to port 22 with ACK or RST set", "All SSH traffic in both directions", "UDP port 22"], 1, "established is a flag check for replies, not session tracking."),
      ("How many IPv4 ACLs can be applied inbound on one interface?", ["One", "Two", "Unlimited", "One per VLAN"], 0, "One per interface, per direction, per protocol.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.9: segment guests and lock down management", time="50 minutes",
      needs=PT_NEEDS + " Start from your lesson 3.6 router on a stick file, or build it: 1 x ISR4331, 2 x 2960, 3 x PC-PT, 1 x Server-PT. SSH from lesson 3.3 should already work on R1 and SW1.",
      topo=fig(TOPO9, "R1 Gi0/0/0 trunks to SW1 with subinterfaces .10, .20 and .99. R1 Gi0/0/1 to SW2 and Server-Web.", "Lab topology"),
      addr=[["R1", "Gi0/0/0.10 / .20 / .99", "192.168.10.1 / 192.168.20.1 / 192.168.99.1 (/24)", "gateways for each VLAN"], ["R1", "Gi0/0/1", "10.10.10.1/24", "server LAN"], ["SW1", "VLAN 99", "192.168.99.2/24", "gateway 192.168.99.1"],
            ["PC-Staff / PC-Guest / Admin-PC", "Fa0", "192.168.10.10 / 192.168.20.10 / 192.168.99.10", "gateway .1"], ["Server-Web", "Fa0", "10.10.10.10/24", "gateway 10.10.10.1, HTTP and DNS on"]],
      steps=[("Guest policy, close to the source", ios(GUEST_ACL.replace(" 15 permit icmp 192.168.20.0 0.0.0.255 host 10.10.10.10 echo\n", "").split("\n") + ["interface GigabitEthernet0/0/0.20", " ip access-group GUEST-IN in"], "GUEST-IN on R1")),
        ("Management lockdown (R1 and SW1)", ios(["ip access-list standard MGMT-ONLY", " permit 192.168.99.0 0.0.0.255", " deny any log", "line vty 0 4", " access-class MGMT-ONLY in"], "MGMT-ONLY") + "<p>On SW1 apply it to <code>line vty 0 15</code> if that range exists in your model.</p>"),
        ("Insert a line without retyping", ios(["R1(config)# ip access-list extended GUEST-IN", "R1(config-ext-nacl)# 15 permit icmp 192.168.20.0 0.0.0.255 host 10.10.10.10 echo"], "Sequence 15")),
        ("Standard ACL near the destination", ios(["R1(config)# access-list 10 deny host 192.168.10.10", "R1(config)# access-list 10 permit any", "R1(config)# interface GigabitEthernet0/0/1", "R1(config-if)# ip access-group 10 out"], "ACL 10")),
        ("Test from each PC", "<p>From PC-Guest: browse <code>http://10.10.10.10</code> (works), ping 10.10.10.10 (works after step 3), ping 192.168.10.10 (fails), SSH to 192.168.99.1 (fails). From PC-Staff: browse the server (fails after step 4). From Admin-PC: SSH to R1 (works).</p>"),
        ("Verify", ios(["R1# show access-lists", "R1# show ip interface GigabitEthernet0/0/0.20", "R1# show running-config | section vty"], "Verify"))],
      verify="show access-lists shows every line with a sequence number and match counters that rise only on the lines your tests hit. show ip interface for Gi0/0/0.20 reports GUEST-IN as the inbound list. The VTY section shows access-class MGMT-ONLY in. PC-Staff cannot reach the server but PC-Guest can, because ACL 10 filters by source only.",
      limits=["Numbered and named standard and extended ACLs, sequence numbers and <code>access-class</code> work in Packet Tracer in the outline author's experience, but test in your own build.",
              "The <code>log</code> keyword is accepted, but whether Packet Tracer actually generates log messages for ACL hits is UNVERIFIED. Rely on the match counters.",
              "IPv6 ACLs (<code>ipv6 access-list</code> with <code>ipv6 traffic-filter</code>) follow the same ideas but are not part of this lab.", PT_GENERIC]),
    takeaways=["First match wins, and every ACL ends with an invisible deny any.", "Standard near the destination, extended near the source.", "Wildcard = 255 minus each mask octet for normal subnets.",
      "Use named ACLs so you can insert and delete single lines.", "Protect the management plane with access-class, and log the denies that matter."])

# ------------------------------------------------------------------ 3.10
TOPO10 = topo(760, 320, {"sw1": (120, 60, "switch", "SW1"), "pcs": (120, 170, "pc", "PC1, PC2", "DHCP clients"), "r1": (380, 60, "router", "R1", "ISR4331"),
    "sws": (640, 60, "switch", "SW-S"), "srv": (640, 175, "server", "Server-DHCP-DNS", "10.0.0.10"), "isp": (380, 190, "router", "ISP", "ISR4331"), "web": (380, 300, "server", "Web-Internet", "198.51.100.10")},
  [("pcs", "sw1", "", ""), ("sw1", "r1", "", "Gi0/0/0 .1"), ("r1", "sws", "Gi0/0/1 10.0.0.1", ""), ("sws", "srv", "", ""), ("r1", "isp", "Gi0/0/2 .2", "Gi0/0/0 .1", "ln-p"), ("isp", "web", "Gi0/0/1 .1", "")],
  "Lab 3.10 topology: PCs on 192.168.10.0/24 get addresses from a central server through R1, and reach a fake internet through PAT on R1 Gi0/0/2 (203.0.113.2/29)")

NATT = svg(760, 200, ARROWDEF +
  box(20, 60, 170, 70, "s-g", "PC1", "inside local 192.168.10.100") + box(295, 60, 170, 70, "s-p", "R1 (PAT)", "inside global 203.0.113.2") + box(570, 60, 170, 70, "s-n", "Web server", "outside global 198.51.100.10") +
  arrow(192, 85, 293, 85) + arrow(467, 85, 568, 85) + arrow(568, 112, 467, 112) + arrow(293, 112, 192, 112) +
  '<text x="242" y="78" text-anchor="middle" font-size="10.5" class="t-m">src .10.100:49152</text><text x="517" y="78" text-anchor="middle" font-size="10.5" class="t-m">src 203.0.113.2:49152</text>' +
  '<text x="380" y="168" text-anchor="middle" font-size="12" class="t-m">R1 rewrites the source on the way out and remembers the mapping so it can reverse it for the reply</text>',
  "PAT: PC1's private source address and port are swapped for R1's public address on the way out, and swapped back for the reply")

def lesson_ccna_10():
  S = []
  S.append(dict(id="dhcp", h="DHCP: how a PC gets its address", hi_h="DHCP DORA",
    body=f'''<p>Typing addresses into every PC does not scale and invites mistakes. <strong>DHCP</strong> hands out the address, mask, default gateway, DNS servers and a lease time. The client uses UDP port 68 and the server UDP port 67.</p>
{stepper("The DORA exchange", "Use Next or the arrow keys.", [
  ("Discover", "<p>The PC has no address yet, so it broadcasts: source 0.0.0.0, destination 255.255.255.255. \"Is there a DHCP server out there?\"</p>"),
  ("Offer", "<p>A server replies with an offer: \"you can have 192.168.10.100/24, gateway 192.168.10.1, DNS 10.0.0.10, for one day\".</p>"),
  ("Request", "<p>The PC broadcasts that it accepts this server's offer. It is a broadcast so any other servers that made offers know they were not picked.</p>"),
  ("Acknowledge", "<p>The server confirms. The PC configures itself and renews part way through the lease (by default at half the lease time) instead of repeating the whole process.</p>")])}
<p>Broadcasts do not cross routers, so a server in the data centre never hears a Discover from a branch LAN. The fix is a <strong>relay agent</strong>: <code>ip helper-address 10.0.0.10</code> on the router interface facing the clients turns the broadcast into a unicast to the server, and includes the interface address (192.168.10.1) so the server knows which pool to use. A router can also be a DHCP server itself, or a DHCP <em>client</em> with <code>ip address dhcp</code>, which is common on an internet facing interface.</p>''',
    hi="DHCP address, mask, gateway, DNS aur lease deta hai. Client UDP 68, server UDP 67. DORA: Discover (broadcast), Offer, Request, Acknowledge. Broadcast router cross nahi karta, isliye client wale interface pe ip helper-address lagao, router request ko server tak unicast karta hai. Router khud DHCP server bhi ban sakta hai, ya ip address dhcp se client."))

  S.append(dict(id="dns", h="DNS: names to addresses", hi_h="DNS",
    body=f'''<p>People type names; packets need addresses. <strong>DNS</strong> resolves one to the other. Your PC asks its configured resolver, which finds the answer (asking other servers if needed) and caches it.</p>
{table(["Record", "Holds"], [["A", "An IPv4 address for a name"], ["AAAA", "An IPv6 address for a name"], ["CNAME", "An alias pointing to another name"], ["MX", "The mail server for a domain"], ["PTR", "Reverse lookup: address to name"], ["NS", "Which servers are authoritative for a zone"]], "Common DNS records")}
<p>DNS mostly uses UDP port 53, and TCP port 53 for large answers and zone transfers, so "DNS is only UDP" is wrong. On a router, <code>ip name-server</code> sets the resolver it uses itself, and <code>no ip domain-lookup</code> (lesson 3.3) stops it trying to resolve every mistyped command.</p>
{attack("<p>If an attacker controls which DNS server your users ask, or poisons the answers, a correct looking address bar can take someone to a fake bank login. A rogue DHCP server on the LAN can do this quietly by handing out the attacker's DNS server and gateway. A DHCP starvation attack, requesting leases from thousands of fake MACs, empties the pool so real users get nothing, which also makes it easier for a rogue server to answer them instead.</p>")}
{defend("<p>Only trusted resolvers handed out by DHCP; DHCP snooping and port security on access switches (lesson 3.12); DNSSEC where your resolver supports it; and the habit this site keeps repeating: read the actual domain in the address bar before typing a password.</p>")}''',
    hi="DNS naam ko address mein badalta hai. A (IPv4), AAAA (IPv6), CNAME (alias), MX (mail), PTR (reverse). Mostly UDP 53, bade answers aur zone transfer ke liye TCP 53. Rogue DHCP server attacker ka DNS de sakta hai aur fake bank site khul jaati hai; starvation attack pool khaali kar deta hai. Defence: DHCP snooping, port security, trusted resolvers, aur URL dhyaan se padho."))

  S.append(dict(id="nat", h="NAT and PAT", hi_h="NAT aur PAT",
    body=f'''<p>Private ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) are not routed on the internet. <strong>NAT</strong> on the edge router rewrites them to public addresses on the way out and back again for the replies.</p>
{fig(NATT, "With PAT, many inside hosts share one public address and are told apart by port numbers in the translation table.", "PAT")}
{table(["Term", "Meaning", "In the lab"], [
  ["Inside local", "The real, usually private, address of the inside host", "192.168.10.100"],
  ["Inside global", "The public address that represents the inside host", "203.0.113.2"],
  ["Outside global", "The real address of the remote host", "198.51.100.10"],
  ["Outside local", "How the remote host appears from inside; usually the same as outside global", "198.51.100.10"]], "NAT address terms")}
{table(["Type", "Mapping", "Use"], [
  ["Static NAT", "One inside address to one public address, permanently", "Publishing a server"],
  ["Dynamic NAT", "Inside hosts borrow addresses from a pool, one to one while in use", "Rare today; runs out when the pool is used up"],
  ["PAT (overload)", "Many inside hosts share one public address, told apart by port", "Almost every home and office"]], "NAT types")}
{ios(["R1(config)# access-list 1 permit 192.168.10.0 0.0.0.255", "R1(config)# ip nat inside source list 1 interface GigabitEthernet0/0/2 overload", "R1(config)# interface GigabitEthernet0/0/0", "R1(config-if)# ip nat inside", "R1(config)# interface GigabitEthernet0/0/2", "R1(config-if)# ip nat outside", "R1(config)# ip nat inside source static 10.0.0.10 203.0.113.3"], "PAT and one static mapping")}
<p>NAT hides internal addresses, but it is not a security policy: a static mapping publishes the server to the whole internet. Use an ACL or firewall to allow only the ports you mean to publish, and keep that server patched and separated. Also note that <code>clear ip nat translation *</code> drops every active session through the router.</p>''',
    hi="Private addresses internet pe route nahi hote, NAT unhe public address mein badalta hai. Inside local = host ka asli private IP, inside global = usko represent karne wala public IP, outside global = remote host ka asli IP. Static NAT server publish karne ke liye, dynamic pool se, PAT (overload) mein bahut saare hosts ek public IP share karte hain ports se. NAT firewall nahi hai."))

  S.append(dict(id="practice", h="Practise on R1", hi_h="R1 pe practice",
    body=f'''<p>R1's interfaces are addressed. The DHCP clients and the internet traffic in this console are modelled for you so the show commands have something to display.</p>
{ios_sim(dict(id="l310", kind="router", host="R1", ifaces=G3, up=G3,
  init={"GigabitEthernet0/0/0": dict(shut=False, ip="192.168.10.1", mask="255.255.255.0"), "GigabitEthernet0/0/1": dict(shut=False, ip="10.0.0.1", mask="255.255.255.0"), "GigabitEthernet0/0/2": dict(shut=False, ip="203.0.113.2", mask="255.255.255.248")},
  dhcp=dict(clients=["0060.2f84.4ab6", "00d0.ba11.2c01", "0001.c7a3.9e10"]),
  nat=dict(flows=[dict(pro="tcp", il="192.168.10.100", ip=49152, og="198.51.100.10", op=80), dict(pro="tcp", il="192.168.10.101", ip=49153, og="198.51.100.10", op=80), dict(pro="icmp", il="192.168.10.102", ip=1, og="198.51.100.10", op=1)]),
  intro=["R1, an ISR4331. Gi0/0/0 is the PC LAN, Gi0/0/1 the server LAN, Gi0/0/2 faces the ISP. Start with enable."],
  missions=[
    dict(t="First try R1 as the DHCP server. Exclude 192.168.10.1 to 192.168.10.99 from leasing.", hint="enable, configure terminal, ip dhcp excluded-address 192.168.10.1 192.168.10.99", c=dict(type="run", re=r"^ip dhcp excluded-address 192\.168\.10\.1 192\.168\.10\.99$")),
    dict(t="Create pool LAN10 for 192.168.10.0/24 with gateway 192.168.10.1 and DNS 10.0.0.10.", hint="ip dhcp pool LAN10, network 192.168.10.0 255.255.255.0, default-router 192.168.10.1, dns-server 10.0.0.10", c=dict(type="run", re=r"^ip dhcp pool LAN10\n network 192\.168\.10\.0 255\.255\.255\.0\n default-router 192\.168\.10\.1\n dns-server 10\.0\.0\.10")),
    dict(t="Which address did the first client get? Type <code>answer IP</code>.", hint="do show ip dhcp binding", c=dict(type="answer", v="192.168.10.100"), ok="The first address after the excluded range."),
    dict(t="The team wants one central server instead. Remove the pool and relay requests to 10.0.0.10 from the PC LAN.", hint="exit, no ip dhcp pool LAN10, interface g0/0/0, ip helper-address 10.0.0.10", c=dict(type="run", re=r"^(?![\s\S]*ip dhcp pool)[\s\S]*^interface GigabitEthernet0/0/0\n[^!]*ip helper-address 10\.0\.0\.10")),
    dict(t="Define who may be translated: standard ACL 1 permitting 192.168.10.0/24.", hint="exit, access-list 1 permit 192.168.10.0 0.0.0.255", c=dict(type="run", re=r"^access-list 1 permit 192\.168\.10\.0 0\.0\.0\.255$")),
    dict(t="Turn on PAT using Gi0/0/2's address.", hint="ip nat inside source list 1 interface g0/0/2 overload", c=dict(type="run", re=r"^ip nat inside source list 1 interface GigabitEthernet0/0/2 overload$")),
    dict(t="Mark Gi0/0/0 and Gi0/0/1 as NAT inside and Gi0/0/2 as outside.", hint="interface g0/0/0, ip nat inside, interface g0/0/1, ip nat inside, interface g0/0/2, ip nat outside", c=dict(type="run", re=r"(?=[\s\S]*^interface GigabitEthernet0/0/0\n[^!]*ip nat inside)(?=[\s\S]*^interface GigabitEthernet0/0/1\n[^!]*ip nat inside)[\s\S]*^interface GigabitEthernet0/0/2\n[^!]*ip nat outside")),
    dict(t="Add a default route to the ISP at 203.0.113.1.", hint="exit, ip route 0.0.0.0 0.0.0.0 203.0.113.1", c=dict(type="run", re=r"^ip route 0\.0\.0\.0 0\.0\.0\.0 203\.0\.113\.1$")),
    dict(t="Look at the translations. Which inside global address do all the PCs share? Type <code>answer IP</code>.", hint="do show ip nat translations", c=dict(type="answer", v="203.0.113.2"), ok="Every PC appears as 203.0.113.2, told apart by port number. That is PAT."),
    dict(t="Publish the internal DNS server 10.0.0.10 on the spare public address 203.0.113.3.", hint="ip nat inside source static 10.0.0.10 203.0.113.3", c=dict(type="run", re=r"^ip nat inside source static 10\.0\.0\.10 203\.0\.113\.3$")),
    dict(t="How many static translations are there now? Type <code>answer N</code>.", hint="do show ip nat statistics", c=dict(type="answer", v="1")),
    dict(t="Save.", hint="end, copy running-config startup-config", c=dict(type="saved"))]), "R1 DHCP and NAT console")}''',
    hi="Simulator mein R1: pehle router ko DHCP server banao (excluded range, pool), binding dekho, phir pool hata ke helper-address se central server use karo, ACL 1, PAT overload, inside/outside interfaces, default route, translations padho, DNS server ko static NAT se publish karo, save."))

  return dict(
    slug="learn-ccna-dhcp-dns-nat", stage=3, n="3.10", minutes=65, level="Intermediate",
    title="DHCP, DNS and NAT/PAT: Addresses, Names and the Internet Edge", short="DORA, DHCP relay, DNS records, NAT terms, static NAT and PAT overload.",
    seo_title="DHCP, DNS and NAT for CCNA: DORA, ip helper-address, PAT Overload, Static NAT | CyberWithMadhav",
    desc="Free CCNA lesson: how DHCP's DORA exchange works, DHCP relay with ip helper-address, DNS records and ports, NAT address terms, static NAT, dynamic NAT and PAT overload, with an IOS simulator and Packet Tracer lab.",
    kw="dhcp dora explained, ip helper-address dhcp relay, cisco router dhcp server, dns record types, nat inside local inside global, pat overload configuration, static nat cisco, packet tracer nat lab, ccna dhcp nat",
    kicker="$ lesson 3.10 --track ccna --domain ip-services", hi_title="DHCP, DNS aur NAT",
    lead="Three services every network quietly depends on. DHCP gives devices their addresses, DNS turns names into addresses, and NAT lets a whole office share one public IP. Learn how each works, how to configure them on a Cisco router, and how attackers abuse DHCP and DNS.",
    hi_lead="DHCP address deta hai, DNS naam ko address banata hai, NAT poore office ko ek public IP share karwata hai. Teeno ka kaam, config aur attacks seekho.",
    goals=["Describe the DHCP DORA exchange and why relay is needed", "Configure a router as DHCP server, relay agent and client", "Explain DNS record types and why DNS uses both UDP and TCP", "Use the four NAT address terms correctly", "Configure and verify static NAT and PAT"],
    sections=S,
    cards=[("DHCP ports?", "Client UDP 68, server UDP 67."), ("DORA?", "Discover, Offer, Request, Acknowledge."), ("DHCP relay command?", "ip helper-address <server> on the client facing interface."),
      ("DNS ports?", "UDP 53, and TCP 53 for large answers and zone transfers."), ("Inside local?", "The real private address of the inside host."), ("Inside global?", "The public address representing the inside host."),
      ("PAT keyword?", "overload."), ("What publishes one server?", "Static NAT: ip nat inside source static.")],
    quiz=[("Why does a PC in another subnet not reach a central DHCP server by default?", ["DHCP uses TCP", "The Discover is a broadcast and routers do not forward broadcasts", "DHCP only works on VLAN 1", "The server needs NAT"], 1, "ip helper-address relays it."),
      ("Which address is the inside global?", ["The PC's private address", "The public address that represents the PC", "The web server's address", "The ISP router's address"], 1, "Inside global is how the inside host appears outside."),
      ("Many hosts share one public IP. Which NAT type?", ["Static NAT", "Dynamic NAT", "PAT (overload)", "NAT64"], 2, "Port numbers keep the sessions apart."),
      ("Which record maps a name to an IPv6 address?", ["A", "AAAA", "PTR", "MX"], 1, "AAAA is the IPv6 equivalent of A."),
      ("What does a DHCP starvation attack do?", ["Encrypts DHCP traffic", "Exhausts the address pool with fake requests", "Changes the DNS server", "Disables NAT"], 1, "Real clients then get no lease, and a rogue server can step in."),
      ("A static NAT mapping publishes an internal server. What should accompany it?", ["Nothing, NAT is a firewall", "An ACL or firewall rule allowing only the needed ports", "A second static mapping", "Disabling DNS"], 1, "NAT changes addresses; it does not enforce policy.")],
    lab=dict(kind="pt", title="Packet Tracer lab 3.10: central DHCP with relay, DNS, and PAT to the internet", time="55 minutes",
      needs=PT_NEEDS + " Devices: 2 x ISR4331 (R1 and ISP), 2 x 2960, 2 x PC-PT, 2 x Server-PT. 203.0.113.0/24 and 198.51.100.0/24 are documentation ranges (RFC 5737) standing in for public space.",
      topo=fig(TOPO10, "PCs on SW1 to R1 Gi0/0/0. R1 Gi0/0/1 to SW-S and Server-DHCP-DNS. R1 Gi0/0/2 to ISP Gi0/0/0; ISP Gi0/0/1 to Web-Internet.", "Lab topology"),
      addr=[["R1", "Gi0/0/0", "192.168.10.1/24", "ip nat inside, ip helper-address 10.0.0.10"], ["R1", "Gi0/0/1", "10.0.0.1/24", "ip nat inside"], ["R1", "Gi0/0/2", "203.0.113.2/29", "ip nat outside"],
            ["ISP", "Gi0/0/0 / Gi0/0/1", "203.0.113.1/29 / 198.51.100.1/24", "no route to 192.168.10.0 needed"], ["Server-DHCP-DNS", "Fa0", "10.0.0.10/24", "gateway 10.0.0.1"], ["Web-Internet", "Fa0", "198.51.100.10/24", "gateway 198.51.100.1, HTTP on"]],
      steps=[("Server services", "<p>On Server-DHCP-DNS, open Services, DHCP: create a pool for 192.168.10.0/24 starting at 192.168.10.100 with default gateway 192.168.10.1 and DNS server 10.0.0.10, and turn the service on. Then Services, DNS: turn it on and add an A record <code>web.cwm.lab</code> pointing to 198.51.100.10.</p>"),
        ("Relay", ios(["R1(config)# interface GigabitEthernet0/0/0", "R1(config-if)# ip helper-address 10.0.0.10"], "DHCP relay") + "<p>Set both PCs to DHCP in their IP Configuration and confirm they receive .100 and up.</p>"),
        ("Optional: router as the DHCP server instead", ios(["R1(config)# ip dhcp excluded-address 192.168.10.1 192.168.10.99", "R1(config)# ip dhcp pool LAN10", "R1(dhcp-config)# network 192.168.10.0 255.255.255.0", "R1(dhcp-config)# default-router 192.168.10.1", "R1(dhcp-config)# dns-server 10.0.0.10"], "Router DHCP") + "<p>Remove the helper address if you try this, or you will have two servers answering.</p>"),
        ("PAT for the LAN", ios(["R1(config)# access-list 1 permit 192.168.10.0 0.0.0.255", "R1(config)# ip nat inside source list 1 interface GigabitEthernet0/0/2 overload", "R1(config)# interface GigabitEthernet0/0/0", "R1(config-if)# ip nat inside", "R1(config)# interface GigabitEthernet0/0/1", "R1(config-if)# ip nat inside", "R1(config)# interface GigabitEthernet0/0/2", "R1(config-if)# ip nat outside", "R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1"], "PAT") + "<p>The ISP has no route back to 192.168.10.0/24, and needs none. That is the point of NAT.</p>"),
        ("Static NAT for the DNS server (demo only)", ios(["R1(config)# ip nat inside source static 10.0.0.10 203.0.113.3"], "Static NAT") + "<p>From Web-Internet, ping 203.0.113.3 or run <code>nslookup web.cwm.lab 203.0.113.3</code>. In real life publish only the ports you need and filter with an ACL.</p>"),
        ("Dynamic NAT with a pool (in a copy of the file)", ios(["R1(config)# no ip nat inside source list 1 interface GigabitEthernet0/0/2 overload", "R1(config)# ip nat pool PUBLIC 203.0.113.4 203.0.113.6 netmask 255.255.255.248", "R1(config)# ip nat inside source list 1 pool PUBLIC"], "Dynamic NAT") + "<p>With three pool addresses, a fourth inside host cannot get out until a translation times out. Adding <code>overload</code> to the pool line turns it into PAT over the pool.</p>"),
        ("Test and verify", ios(["PC1> ipconfig /all", "R1# show ip nat translations", "R1# show ip nat statistics", "R1# show ip dhcp binding", "R1# show ip dhcp pool"], "Verify") + "<p>From PC1, browse <code>http://web.cwm.lab</code>. Briefly try <code>debug ip nat</code>, then turn it off with <code>undebug all</code>.</p>")],
      verify="PC1 ipconfig /all shows an address from .100 up, gateway 192.168.10.1 and DNS 10.0.0.10. show ip nat translations lists entries with inside global 203.0.113.2 and different ports for different inside locals, plus the static entry for 10.0.0.10. PC1 opens http://web.cwm.lab.",
      limits=["Server-PT DHCP and DNS services work for simple pools and A records. How Packet Tracer matches a Server-PT pool to the relay address in every version is UNVERIFIED; if a PC gets no lease, check that the pool's gateway sits in the PC's subnet.",
              "Packet Tracer's <code>show ip nat statistics</code> output is shorter than real IOS.", "Which DNS record types beyond A and CNAME Packet Tracer's DNS server supports is UNVERIFIED for every version.", PT_GENERIC]),
    takeaways=["DHCP is DORA over UDP 67 and 68; relay it across routers with ip helper-address.", "DNS uses UDP 53 and TCP 53; whoever controls your DNS controls where names go.", "Know the four NAT terms: inside local, inside global, outside local, outside global.",
      "PAT (overload) lets a whole site share one public address.", "NAT is not a firewall; filter what you publish."])
