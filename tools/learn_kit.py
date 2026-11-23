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
