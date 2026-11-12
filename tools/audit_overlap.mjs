// Layout audit: text overlaps, horizontal overflow, header covering anchors, More menu, consent modal.
// Run from tools/: URL=http://127.0.0.1:8000/ OUT=/tmp/audit node audit_overlap.mjs [page ...]
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
const BASE = (process.env.URL || 'https://www.cyberwithmadhav.com/').replace(/\/?$/, '/');
const OUT = (process.env.OUT || '/tmp/audit').replace(/\/?$/, '/');
const SHOTS = process.env.SHOTS !== '0';
fs.mkdirSync(OUT, { recursive: true });
const ALL = ['index.html', 'explore.html', 'commands.html', 'scams.html', 'terminal.html', 'ctf.html', 'prompts.html', 'cyberlaw.html', 'terms.html', 'privacy.html', '404.html', 'game.html', 'soc.html', 'owasp.html', 'daily.html', 'progress.html', 'paths.html'];
const PAGES = process.argv.slice(2).length ? process.argv.slice(2) : ALL;
const SIZES = [[360, 740], [390, 844], [768, 1024], [1280, 800], [1440, 900]];
const THEMES = ['dark', 'light'];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'], protocolTimeout: 300000 });

function probe() {
  const vw = document.documentElement.clientWidth;
  const out = { overflowX: document.documentElement.scrollWidth - vw, wide: [], overlaps: [], spill: [], anchors: [], more: null };
  const vc = new Map();
  const vis0 = e => { for (let n = e; n && n.nodeType === 1; n = n.parentElement) { const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0) return false; if (n.tagName === 'DETAILS' && !n.open && n !== e && !e.closest('summary')) { if (!n.querySelector('summary').contains(e)) return false; } } return true; };
  const vis = e => { if (!vc.has(e)) vc.set(e, vis0(e)); return vc.get(e); };
  const clipRect = e => { let r = { l: -1e9, t: -1e9, r: 1e9, b: 1e9 }; for (let n = e; n && n !== document.documentElement; n = n.parentElement) { const s = getComputedStyle(n); if (s.overflowX !== 'visible' || s.overflowY !== 'visible' || s.clipPath !== 'none') { const b = n.getBoundingClientRect(); r = { l: Math.max(r.l, b.left), t: Math.max(r.t, b.top), r: Math.min(r.r, b.right), b: Math.min(r.b, b.bottom) }; } if (s.position === 'fixed') break; } return r; };
  const desc = e => { let s = e.tagName.toLowerCase(); if (e.id) s += '#' + e.id; if (e.className && typeof e.className === 'string') s += '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.'); const p = e.parentElement; return (p ? (p.id ? '#' + p.id : p.className && typeof p.className === 'string' ? '.' + p.className.trim().split(/\s+/)[0] : p.tagName.toLowerCase()) + ' > ' : '') + s; };
  const boxes = [];
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, { acceptNode: t => t.nodeValue.trim() ? 1 : 2 });
  for (let t; (t = tw.nextNode());) {
    const e = t.parentElement; if (!e || /^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|OPTION)$/.test(e.tagName)) continue;
    if (e.closest('[aria-hidden="true"], .sr-only, .visually-hidden, svg, canvas')) continue;
    if (!vis(e)) continue;
    const cs = getComputedStyle(e);
    const c = clipRect(e); const rg = document.createRange(); rg.selectNodeContents(t);
    const fixed = (() => { for (let n = e; n; n = n.parentElement) { const p = getComputedStyle(n).position; if (p === 'fixed' || p === 'sticky') return true; } return false; })();
    const inModal = !!e.closest('#cwm-consent');
    for (const r of rg.getClientRects()) {
      if (r.width < 2 || r.height < 2) continue;
      const v = { l: Math.max(r.left, c.l), t: Math.max(r.top, c.t), r: Math.min(r.right, c.r), b: Math.min(r.bottom, c.b) };
      if (v.r - v.l < 2 || v.b - v.t < 2) continue;
      boxes.push({ e, ...v, fixed, inModal, txt: t.nodeValue.trim().slice(0, 40) });
      // text spilling out of the viewport horizontally
      if (r.right > vw + 1 && c.r > vw) out.wide.push(desc(e) + ' "' + t.nodeValue.trim().slice(0, 30) + '" right=' + Math.round(r.right));
    }
    // block that its own text spills out of (long words)
    if (/block|flex-item|list-item|table-cell/.test(cs.display) && cs.overflowX === 'visible' && e.scrollWidth > e.clientWidth + 2 && e.clientWidth > 0 && !e.closest('pre,code,.term,.terminal')) out.spill.push(desc(e) + ' sw=' + e.scrollWidth + ' cw=' + e.clientWidth);
  }
  const modalOpen = !!document.getElementById('cwm-consent');
  boxes.sort((a, b) => a.t - b.t);
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length && boxes[j].t < boxes[i].b; j++) {
    const a = boxes[i], b = boxes[j];
    if (a.e === b.e || a.e.contains(b.e) || b.e.contains(a.e)) continue;
    if (modalOpen && !(a.inModal && b.inModal)) continue;
    const w = Math.min(a.r, b.r) - Math.max(a.l, b.l), h = Math.min(a.b, b.b) - Math.max(a.t, b.t);
    if (w > 3 && h > 3) out.overlaps.push(`${desc(a.e)} "${a.txt}" X ${desc(b.e)} "${b.txt}" (${Math.round(w)}x${Math.round(h)} at ${Math.round(Math.max(a.l, b.l))},${Math.round(Math.max(a.t, b.t) + scrollY)})${a.fixed || b.fixed ? ' [fixed]' : ''}`);
  }
  return out;
}

async function run(page, w, h, theme, consent) {
  const p = await browser.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.evaluateOnNewDocument((theme, consent) => { try { localStorage.setItem('cwm-theme', theme); if (consent) localStorage.setItem('cwm-consent', JSON.stringify({ v: 2, at: 'audit' })); else localStorage.removeItem('cwm-consent'); } catch (e) {} }, theme, consent);
  await p.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }, { name: 'prefers-color-scheme', value: theme }]);
  await p.setViewport({ width: w, height: h });
  const res = await p.goto(BASE + page, { waitUntil: "networkidle2", timeout: 45000 }).catch(e => (console.error("goto", page, e.message), null));
  if (!res || res.status() >= 400 && page !== '404.html') { await p.close(); return null; }
  await sleep(700);
  // force reveal animations to their end state
  await p.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in', 'is-visible', 'visible', 'shown')));
  await sleep(300);
  const tag = `${page.replace('.html', '')}_${w}_${theme}${consent ? '' : '_consent'}`;
  const r = await p.evaluate(probe);
  if (consent) {
    // header vs anchors: jump to each section id and check it clears the fixed header
    r.anchors = await p.evaluate(async () => {
      const hdr = document.querySelector('header.nav, .nav'); if (!hdr) return [];
      const bad = [];
      const ids = [...document.querySelectorAll('main section[id], main [id].section')].map(s => s.id).filter(Boolean);
      for (const id of ids) { const s = document.getElementById(id); if (!s || !s.offsetHeight) continue; s.scrollIntoView({ block: 'start', behavior: 'instant' }); await new Promise(r => setTimeout(r, 30));
        const hb = hdr.getBoundingClientRect().bottom; const first = s.querySelector('h1,h2,h3,.kicker,p') || s; const ft = first.getBoundingClientRect().top;
        if (ft < hb - 1 && getComputedStyle(hdr).position !== 'static') bad.push(`#${id} first text top=${Math.round(ft)} < header bottom=${Math.round(hb)}`); }
      window.scrollTo(0, 0); return bad;
    });
    // More menu
    r.more = await p.evaluate(async () => {
      const t = document.querySelector('.nav-toggle'); const d = document.querySelector('details.nav-more'); if (!d) return null;
      if (t && getComputedStyle(t).display !== 'none') { t.click(); await new Promise(r => setTimeout(r, 400)); }
      d.open = true; await new Promise(r => setTimeout(r, 400));
      const m = d.querySelector('.nav-more-menu').getBoundingClientRect(); const vw = document.documentElement.clientWidth, vh = innerHeight;
      const issues = []; if (m.left < -1 || m.right > vw + 1) issues.push(`menu x ${Math.round(m.left)}..${Math.round(m.right)} outside 0..${vw}`);
      if (m.bottom > vh + 1 && getComputedStyle(d.querySelector('.nav-more-menu')).position === 'fixed') issues.push(`menu bottom ${Math.round(m.bottom)} > ${vh}`);
      return issues;
    });
    const mo = await p.evaluate(probe); // overlaps with menu open: only those involving the menu matter
    r.moreOverlaps = mo.overlaps.filter(x => /nav-more|nav-links/.test(x) && !/\[fixed\]$/.test('') ).filter(x => (x.match(/nav-more/g) || []).length === 2 || /nav-more.*X.*nav-more/.test(x));
    if (SHOTS && (w === 360 || w === 1280)) await p.screenshot({ path: OUT + tag + '_more.png' });
    await p.evaluate(() => { const d = document.querySelector('details.nav-more'); if (d) d.open = false; const t = document.querySelector('.nav-toggle[aria-expanded="true"]'); if (t) t.click(); });
  }
  if (SHOTS) await p.screenshot({ path: OUT + tag + '.png', fullPage: consent });
  r.errs = errs;
  await p.close();
  return { tag, ...r };
}

const report = []; let bad = 0;
const jobs = [];
for (const page of PAGES) for (const [w, h] of SIZES) for (const theme of THEMES) for (const consent of [true, false]) jobs.push([page, w, h, theme, consent]);
const skip = new Set();
async function worker() { while (jobs.length) { const j = jobs.shift(); if (skip.has(j[0])) continue; let r; for (let k = 0; k < 3; k++) { r = await run(...j).catch(e => ({ tag: j.join('_'), fail: e.message })); if (!(r && r.fail)) break; } if (r === null) { skip.add(j[0]); continue; } report.push(r); } }
await Promise.all([1, 2, 3, 4].map(worker));
await browser.close();
report.sort((a, b) => a.tag.localeCompare(b.tag));
for (const r of report) {
  const n = (r.overlaps || []).length + (r.overflowX > 0 ? 1 : 0) + (r.wide || []).length + (r.spill || []).length + (r.anchors || []).length + (r.more || []).length + (r.moreOverlaps || []).length + (r.fail ? 1 : 0);
  if (!n) continue; bad++;
  console.log(`\n== ${r.tag}${r.fail ? ' FAIL ' + r.fail : ''}${r.overflowX > 0 ? ' overflowX=' + r.overflowX : ''}`);
  for (const k of ['overlaps', 'wide', 'spill', 'anchors', 'more', 'moreOverlaps']) for (const x of (r[k] || []).slice(0, 12)) console.log(`  ${k}: ${x}`);
}
console.log(`\n${report.length} runs, ${bad} with issues, pages: ${[...new Set(report.map(r => r.tag.split('_')[0]))].join(' ')}`);
fs.writeFileSync(OUT + 'report.json', JSON.stringify(report, null, 1));
