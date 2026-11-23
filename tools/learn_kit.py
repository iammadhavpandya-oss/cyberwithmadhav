"""HTML building blocks for Learn lessons (used by tools/content/learn_src.py and tools/build_learn.py).
Everything returns plain HTML strings. Interactive parts are wired up by assets/js/learn.js and learn-term.js."""
import html, json, re

def e(s):
    return html.escape(s, quote=True)

def call(kind, label, body, hi_key=None):
    k = f' data-i18n="{hi_key}"' if hi_key else ''
    return f'<aside class="lx-call lx-{kind}" role="note"><b{k}>{label}</b><div>{body}</div></aside>'

def analogy(body):  return call("analogy", "Think of it like this", body, "lx.c.analogy")
def attack(body):   return call("attack", "How attackers abuse this", body, "lx.c.attack")
def defend(body):   return call("defend", "Defender move", body, "lx.c.defend")
def hi(body):       return f'<aside class="lx-call lx-hi" role="note" data-lang-only="hi"><b>Hinglish mein samjho</b><div><p>{body}</p></div></aside>'

def fig(svg, caption, label):
    return f'<figure class="lx-fig" role="group" aria-label="{e(label)}">{svg}<figcaption>{caption}</figcaption></figure>'

def code(lines, title=None, copy=True):
    """lines: list of strings. '$ cmd' = command, '# text' = comment, anything else = output."""
    out = []
    for ln in lines:
        if ln.startswith("$ "):   out.append(f'<span class="p">$ </span><span class="cmd">{e(ln[2:])}</span>')
        elif ln.startswith("PS> "): out.append(f'<span class="p">PS&gt; </span><span class="cmd">{e(ln[4:])}</span>')
        elif ln.startswith("C:\\> "): out.append(f'<span class="p">C:\\&gt; </span><span class="cmd">{e(ln[5:])}</span>')
        elif ln.startswith("# "): out.append(f'<span class="c">{e(ln)}</span>')
        else: out.append(f'<span class="o">{e(ln)}</span>')
    lab = f' aria-label="{e(title)}"' if title else ''
    return f'<div class="lx-code"{"" if copy else " data-nocopy"}><pre tabindex="0"{lab}><code>' + "\n".join(out) + '</code></pre></div>'

def table(head, rows, caption):
    th = "".join(f'<th scope="col">{h}</th>' for h in head)
    tr = "".join("<tr>" + "".join((f'<th scope="row">{c}</th>' if i == 0 else f'<td>{c}</td>') for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="lx-tbl" tabindex="0" role="region" aria-label="{e(caption)}"><table><caption class="sr-only">{e(caption)}</caption><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'

def stepper(title, hint, steps):
    """steps: list of (title, html)."""
    body = "".join(f'<div class="lx-step" data-t="{e(t)}" aria-live="polite"><h4>{t}</h4>{h}</div>' for t, h in steps)
    return (f'<div class="card lx-widget lx-stepper"><h3>{title}</h3><p class="hint">{hint}</p><ol class="lx-steps-track" aria-label="Steps"></ol>{body}'
            f'<div class="lx-steps-nav"><button type="button" class="lx-wbtn" data-prev>&larr; Back</button><span></span><button type="button" class="lx-wbtn" data-next>Next &rarr;</button></div></div>')

_ex = [0]
def explorer(title, hint, items):
    """items: list of (button label, html). A tab list."""
    _ex[0] += 1; n = _ex[0]
    tabs = "".join(f'<button type="button" role="tab" id="ex{n}-t{i}" aria-controls="ex{n}-p{i}" aria-selected="false">{lab}</button>' for i, (lab, _) in enumerate(items))
    pans = "".join(f'<div role="tabpanel" id="ex{n}-p{i}" aria-labelledby="ex{n}-t{i}" class="lx-expanel" tabindex="0">{h}</div>' for i, (_, h) in enumerate(items))
    return f'<div class="card lx-widget lx-explorer"><h3>{title}</h3><p class="hint">{hint}</p><div class="lx-extabs" role="tablist" aria-label="{e(re.sub("<[^>]+>", "", title))}">{tabs}</div>{pans}</div>'

def bits():
    btn = "".join(f'<button type="button" aria-pressed="false" aria-label="Bit worth {1 << (7 - i)}"><span>0</span><small>{1 << (7 - i)}</small></button>' for i in range(8))
    return ('<div class="card lx-widget lx-bitw"><h3>Byte builder: flip the bits</h3>'
            '<p class="hint">Each switch is one bit. Turn them on and watch the same byte as decimal, hex and a text character. Or type a number from 0 to 255.</p>'
            f'<div class="lx-bits" role="group" aria-label="Eight bits, most significant first">{btn}</div>'
            '<div class="lx-bitout" aria-live="polite"><div><b>Decimal</b><span data-o="dec"></span></div><div><b>Hex</b><span data-o="hex"></span></div><div><b>Binary</b><span data-o="bin"></span></div><div><b>ASCII</b><span data-o="chr"></span></div></div>'
            '<p class="lx-permout"><label class="small muted" for="bits-n">Type a number</label><input id="bits-n" type="number" min="0" max="255" inputmode="numeric"> '
            '<button type="button" class="lx-wbtn" data-set="65">65</button><button type="button" class="lx-wbtn" data-set="127">127</button><button type="button" class="lx-wbtn" data-set="255">255</button><button type="button" class="lx-wbtn" data-set="0">0</button></p></div>')

def perm_calc():
    def fs(w, name):
        return (f'<fieldset><legend>{name}</legend>' + "".join(f'<label><input type="checkbox" data-w="{w}" data-v="{v}"{" checked" if (w, v) in DEF else ""}> {lab}</label>' for v, lab in ((4, "read (r)"), (2, "write (w)"), (1, "execute (x)"))) + '</fieldset>')
    global DEF
    DEF = {(0, 4), (0, 2), (0, 1), (1, 4), (1, 1)}
    return ('<div class="card lx-widget lx-permw"><h3>chmod calculator</h3><p class="hint">Tick what each class of user may do, or type three octal digits. The symbolic form is what <code>ls -l</code> shows you.</p>'
            f'<div class="lx-perm">{fs(0, "Owner (u)")}{fs(1, "Group (g)")}{fs(2, "Others (o)")}</div>'
            '<div class="lx-permout" aria-live="polite"><label class="small muted" for="perm-oct">Octal</label><input id="perm-oct" type="text" inputmode="numeric" maxlength="3" autocomplete="off"><code data-o="sym"></code><code data-o="cmd"></code></div>'
            '<p class="lx-permsay" aria-live="polite"></p>'
            '<p class="lx-permout"><span class="small muted">Common:</span><button type="button" class="lx-wbtn" data-set="644">644</button><button type="button" class="lx-wbtn" data-set="600">600</button><button type="button" class="lx-wbtn" data-set="755">755</button><button type="button" class="lx-wbtn" data-set="700">700</button><button type="button" class="lx-wbtn" data-set="777">777</button></p></div>')

def terminal(cfg, title="Practice shell"):
    data = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    n = len(cfg.get("missions", []))
    return (f'<div class="lx-term" role="region" aria-label="{e(title)}">'
            f'<div class="lx-term-bar"><i></i><i></i><i></i>student@cwm-lab: {e(title)}</div>'
            '<div class="lx-term-grid"><div><div class="lx-term-out" role="log" aria-live="polite" tabindex="0"></div>'
            '<div class="lx-term-in"><label for="ti-' + e(cfg["id"]) + '"></label><input id="ti-' + e(cfg["id"]) + '" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Type a command and press Enter"></div></div>'
            f'<div class="lx-missions"><h4>Missions <span class="lx-mcount">0/{n}</span></h4><ol></ol></div></div>'
            '<div class="lx-term-foot"><span>Simulated in your browser. Nothing runs on a real machine.</span><button type="button" data-reset>Reset shell</button></div>'
            f'<script type="application/json" class="lx-term-cfg">{data}</script></div>')

def svg(w, h, inner, title):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(title)}" xmlns="http://www.w3.org/2000/svg"><title>{e(title)}</title>{inner}</svg>'

def box(x, y, w, h, cls, label, sub=None, rx=10):
    t = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}" stroke-width="1.5"/>'
    cy = y + h / 2 + (-4 if sub else 5)
    t += f'<text x="{x + w / 2}" y="{cy}" text-anchor="middle" font-size="14" font-weight="600">{label}</text>'
    if sub: t += f'<text x="{x + w / 2}" y="{cy + 18}" text-anchor="middle" font-size="11" class="t-m">{sub}</text>'
    return t

def arrow(x1, y1, x2, y2, cls="ln", flow=False):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}{" flow" if flow else ""}" stroke-width="2" marker-end="url(#ah)"/>'

ARROWDEF = '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="currentColor" class="t-m"/></marker></defs>'

# ---------------------------------------------------------------- CCNA track helpers
_IOS_P = re.compile(r'^([A-Za-z][\w-]*(?:\((?:config[\w-]*)\))?[#>])\s?(.*)$')
def ios(lines, title=None):
    """IOS transcript. 'R1(config)# cmd' = prompt + command, '! text' = comment, anything else = output."""
    out = []
    for ln in lines:
        m = _IOS_P.match(ln)
        if ln.startswith("!"): out.append(f'<span class="c">{e(ln)}</span>')
        elif m and m.group(2) is not None and not ln.startswith(" "): out.append(f'<span class="p">{e(m.group(1))}</span><span class="cmd">{e(m.group(2))}</span>')
        else: out.append(f'<span class="o">{e(ln)}</span>')
    lab = f' aria-label="{e(title)}"' if title else ''
    return '<div class="lx-code lx-ioscode"><pre tabindex="0"' + lab + '><code>' + "\n".join(out) + '</code></pre></div>'

def ios_sim(cfg, title="IOS practice console"):
    data = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    n = len(cfg.get("missions", []))
    host = cfg.get("host") or ("Router" if cfg.get("kind") == "router" else "Switch")
    return (f'<div class="lx-ios" role="region" aria-label="{e(title)}">'
            f'<div class="lx-term-bar"><i></i><i></i><i></i>console: {e(host)} ({e(title)})</div>'
            '<div class="lx-term-grid"><div><div class="lx-term-out" role="log" aria-live="polite" tabindex="0"></div>'
            f'<div class="lx-term-in"><label for="io-{e(cfg["id"])}"></label><input id="io-{e(cfg["id"])}" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Type an IOS command and press Enter"></div></div>'
            f'<div class="lx-missions"><h4>Missions <span class="lx-mcount">0/{n}</span></h4><ol></ol></div></div>'
            '<div class="lx-term-foot"><span>Simplified IOS simulator in your browser. It teaches the commands; Packet Tracer and real gear have many more.</span><button type="button" data-reset>Reset device</button></div>'
            f'<script type="application/json" class="lx-ios-cfg">{data}</script></div>')

def subnet_calc(ip="192.168.50.130", pfx=26):
    return ('<div class="card lx-widget lx-subnet"><h3>Subnet calculator</h3>'
            '<p class="hint">Type any IPv4 address and prefix, or drag the slider. Purple bits are the network part, green bits are the host part.</p>'
            '<div class="lx-snin"><label>IPv4 address <input data-i="ip" type="text" inputmode="decimal" autocomplete="off" spellcheck="false" value="' + e(ip) + '"></label>'
            f'<label>Prefix length / <input data-i="pfx" type="number" min="0" max="32" value="{pfx}"></label></div>'
            f'<label class="lx-snsl"><span class="sr-only">Prefix length slider</span><input data-i="slide" type="range" min="0" max="32" value="{pfx}"></label>'
            '<div class="lx-snbits mono" aria-hidden="true"></div><dl class="lx-snout" aria-live="polite"></dl>'
            '<div class="lx-snq"><p><button type="button" class="lx-wbtn" data-q>Give me a practice question</button></p><p class="q" aria-live="polite"></p>'
            '<p class="row" hidden><label><span class="sr-only">Your answer</span><input data-i="ans" type="text" autocomplete="off" spellcheck="false" placeholder="your answer"></label> <button type="button" class="lx-wbtn" data-check>Check</button></p>'
            '<p class="fb" aria-live="polite"></p></div></div>')

def route_game(cfg, title="Which route wins?"):
    data = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    return (f'<div class="card lx-widget lx-route"><h3>{title}</h3>'
            '<p class="hint">These are all the routes this router learned, from every source. Only the best source for each prefix goes into the routing table, then the longest matching prefix forwards the packet. Pick the route that forwards each packet, or drop it.</p>'
            '<p class="lx-rq" aria-live="polite"></p>'
            '<div class="lx-tbl" tabindex="0" role="region" aria-label="Candidate routes"><table><caption class="sr-only">Candidate routes</caption><thead><tr><th scope="col">Source</th><th scope="col">Prefix</th><th scope="col">AD</th><th scope="col">Metric</th><th scope="col">Next hop</th><th scope="col"><span class="sr-only">Choose</span></th></tr></thead><tbody></tbody></table></div>'
            '<p><button type="button" class="lx-wbtn" data-drop>Drop it: no route matches</button> <button type="button" class="lx-wbtn" data-next hidden>Next packet</button> <span class="lx-rscore small muted"></span></p>'
            '<p class="lx-rfb" aria-live="polite"></p>'
            f'<script type="application/json" class="lx-route-cfg">{data}</script></div>')

def acl_tester(cfg, title="ACL rule tester"):
    data = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    return (f'<div class="card lx-widget lx-acl"><h3>{title}</h3>'
            '<p class="hint">Edit the ACL, describe a packet, and watch it walk the list top to bottom. The first matching line decides. If nothing matches, the invisible deny at the end drops it.</p>'
            '<div class="lx-aclgrid"><label class="lx-acl-ta">ACL lines<textarea data-i="acl" rows="8" spellcheck="false" autocomplete="off"></textarea></label>'
            '<div class="lx-acl-pk"><fieldset><legend>Packet</legend>'
            '<label>Protocol <select data-i="proto"><option value="tcp">tcp</option><option value="udp">udp</option><option value="icmp">icmp</option></select></label>'
            '<label>Source IP <input data-i="src" type="text" inputmode="decimal" autocomplete="off" spellcheck="false"></label>'
            '<label>Destination IP <input data-i="dst" type="text" inputmode="decimal" autocomplete="off" spellcheck="false"></label>'
            '<label class="pt">Destination port <input data-i="dport" type="number" min="0" max="65535"></label>'
            '<label class="pt">Source port <input data-i="sport" type="number" min="0" max="65535" value="50123"></label>'
            '<label class="pt tcp"><input data-i="ack" type="checkbox"> ACK set (a reply in an existing connection)</label>'
            '<label class="ic">ICMP type <select data-i="icmp"><option value="echo">echo (ping request)</option><option value="echo-reply">echo-reply</option><option value="unreachable">unreachable</option><option value="time-exceeded">time-exceeded</option></select></label>'
            '</fieldset><p class="lx-acl-pre" aria-label="Example packets"></p><p><button type="button" class="lx-wbtn" data-test>Test this packet</button></p></div></div>'
            '<p class="lx-acl-res" aria-live="polite"></p><ol class="lx-acl-trace" aria-label="How the packet was checked"></ol>'
            f'<script type="application/json" class="lx-acl-cfg">{data}</script></div>')

def type7_decoder():
    return ('<div class="card lx-widget lx-t7"><h3>Type 7 decoder: see why it is not encryption</h3>'
            '<p class="hint">Paste a type 7 string from a config (the part after <code>password 7</code>). The algorithm and its key are public, so anyone can reverse it. Only paste lab strings, never a real device\'s.</p>'
            '<p class="lx-permout"><label class="small muted" for="t7-in">Type 7 string</label><input id="t7-in" type="text" autocomplete="off" spellcheck="false" value="0822455D0A16"> <button type="button" class="lx-wbtn">Decode</button></p>'
            '<p>Plain text: <output class="mono" for="t7-in" aria-live="polite"></output></p></div>')

# topology drawing: nodes {id: (x, y, kind, label, sub)}, links [(a, b, label_a, label_b, style)]
_ICON = {
  "router": lambda x, y: f'<circle cx="{x}" cy="{y}" r="22" class="s-p" stroke-width="1.6"/><path d="M{x-11} {y-4}h22M{x+5} {y-9}l6 5-6 5M{x-11} {y+5}h22M{x-5} {y}l-6 5 6 5" class="ln-p" stroke-width="1.6" fill="none"/>',
  "switch": lambda x, y: f'<rect x="{x-28}" y="{y-15}" width="56" height="30" rx="6" class="s-g" stroke-width="1.6"/><path d="M{x-16} {y-5}h32M{x+10} {y-9}l6 4-6 4M{x+16} {y+5}h-32M{x-10} {y+1}l-6 4 6 4" class="ln-g" stroke-width="1.5" fill="none"/>',
  "l3switch": lambda x, y: f'<rect x="{x-28}" y="{y-15}" width="56" height="30" rx="6" class="s-a" stroke-width="1.6"/><path d="M{x-16} {y-5}h32M{x+10} {y-9}l6 4-6 4M{x+16} {y+5}h-32M{x-10} {y+1}l-6 4 6 4" class="ln" stroke-width="1.5" fill="none"/><text x="{x+22}" y="{y-18}" font-size="10" class="t-m">L3</text>',
  "pc": lambda x, y: f'<rect x="{x-17}" y="{y-14}" width="34" height="23" rx="3" class="s-n" stroke-width="1.5"/><path d="M{x-6} {y+15}h12M{x} {y+9}v6" class="ln" stroke-width="1.5"/>',
  "server": lambda x, y: f'<rect x="{x-14}" y="{y-20}" width="28" height="40" rx="3" class="s-n" stroke-width="1.5"/><path d="M{x-8} {y-10}h16M{x-8} {y-2}h16M{x-8} {y+6}h16" class="ln" stroke-width="1.3"/>',
  "ap": lambda x, y: f'<rect x="{x-18}" y="{y-6}" width="36" height="14" rx="7" class="s-n" stroke-width="1.5"/><path d="M{x-9} {y-12}q9-9 18 0M{x-14} {y-17}q14-13 28 0" class="ln-p" stroke-width="1.5" fill="none"/>',
  "wlc": lambda x, y: f'<rect x="{x-26}" y="{y-14}" width="52" height="28" rx="4" class="s-a" stroke-width="1.5"/><text x="{x}" y="{y+4}" font-size="10" text-anchor="middle">WLC</text>',
  "cloud": lambda x, y: f'<path d="M{x-26} {y+12}h50a12 12 0 0 0 0-24a16 16 0 0 0-30-6a12 12 0 0 0-20 12a9 9 0 0 0 0 18z" class="s-n" stroke-width="1.5"/>',
  "phone": lambda x, y: f'<rect x="{x-12}" y="{y-12}" width="24" height="22" rx="4" class="s-n" stroke-width="1.5"/><path d="M{x-6} {y-6}h12M{x-6} {y}h12" class="ln" stroke-width="1.3"/>',
}
def topo(w, h, nodes, links, title):
    g = []
    for a, b, la, lb, *st in links:
        x1, y1 = nodes[a][0], nodes[a][1]; x2, y2 = nodes[b][0], nodes[b][1]
        cls = (st[0] if st else "ln")
        dash = ' stroke-dasharray="6 5"' if cls == "dash" else ''
        g.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{"ln" if cls == "dash" else cls}" stroke-width="{3 if cls == "ln-p" else 2}"{dash}/>')
        for lab, t in ((la, 0.27), (lb, 0.73)):
            if lab:
                lx, ly = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                g.append(f'<text x="{lx:.0f}" y="{ly - 6:.0f}" font-size="10.5" text-anchor="middle" class="t-m lx-tl">{e(lab)}</text>')
    for k, (x, y, kind, label, *sub) in nodes.items():
        g.append(_ICON[kind](x, y))
        dy = 24 if kind in ("pc", "phone") else 36 if kind in ("router", "server") else 30
        g.append(f'<text x="{x}" y="{y + dy}" font-size="12.5" font-weight="600" text-anchor="middle">{e(label)}</text>')
        if sub and sub[0]: g.append(f'<text x="{x}" y="{y + dy + 14}" font-size="10.5" text-anchor="middle" class="t-m">{e(sub[0])}</text>')
    return svg(w, h, "".join(g), title)

def addr_table(rows, caption="Addressing table"):
    return table(["Device", "Interface", "IPv4 address / prefix", "Default gateway or note"], rows, caption)
