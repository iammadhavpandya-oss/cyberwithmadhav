// Feature page checks (phases 3 to 8): nav "More" menu, commands.html, and later pages when they exist.
// Run from tools/: node test_features.mjs   Needs the static server on :8000. URL=<live base> tests the live site (no screenshots).
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import http from 'node:http'; import https from 'node:https';
const BASE = (process.env.URL || 'http://127.0.0.1:8000/').replace(/\/?$/, '/');
const LIVE = !!process.env.URL;
const SITE = new globalThis.URL('../', import.meta.url).pathname;
const OUT = SITE + 'docs/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const get = u => new Promise((res, rej) => (u.startsWith('https') ? https : http).get(u, r => {
  const ch = []; r.on('data', c => ch.push(c)); r.on('end', () => res({ status: r.statusCode, text: Buffer.concat(ch).toString('utf8') }));
}).on('error', rej));
const results = [];
const ok = (name, cond, extra = '') => { results.push(`${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '  : ' + extra : ''}`); };
const has = p => fs.existsSync(SITE + p);
const shot = async (p, name, el) => { if (LIVE) return; if (el) { const h = await p.$(el); if (h) await h.screenshot({ path: OUT + name }); } else await p.screenshot({ path: OUT + name }); };
const launch = () => puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'], dumpio: !!process.env.DUMP });
let browser = await launch(); let relaunches = 0;
async function open(path, { scheme = 'dark', width = 1440, height = 900, reduce = false, storage = null } = {}) {
  if (process.env.DUMP) console.error('open', path, width);
  let c; try { c = await browser.createBrowserContext(); } catch (e) { relaunches++; if (process.env.DUMP) console.error('relaunch after', path); try { await browser.close(); } catch (_) {} browser = await launch(); c = await browser.createBrowserContext(); }
  await c.overridePermissions(new globalThis.URL(BASE).origin, ['clipboard-read', 'clipboard-write']);
  const p = await c.newPage(); p.ctx = c; p.errors = [];
  p.on('console', m => { if (m.type() === 'error' && !/favicon|net::ERR_/.test(m.text())) p.errors.push(m.text()); });
  p.on('pageerror', e => p.errors.push('pageerror: ' + e.message));
  await p.evaluateOnNewDocument(s => { try { localStorage.setItem('cwm-consent', JSON.stringify({ v: 2, at: 'test' })); if (s) for (const k in s) localStorage.setItem(k, s[k]); } catch (e) {} }, storage);
  await p.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }, { name: 'prefers-reduced-motion', value: reduce ? 'reduce' : 'no-preference' }]);
  await p.setViewport({ width, height });
  await p.goto(BASE + path, { waitUntil: 'load' }); await sleep(800);
  return p;
}
// WCAG contrast of an element's text against the page background colour (worst case for translucent cards)
const contrastFn = () => (sel) => {
  const lum = c => { const [r, g, b] = c.match(/[\d.]+/g).slice(0, 3).map(Number).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }); return .2126 * r + .7152 * g + .0722 * b; };
  const e = document.querySelector(sel); if (!e) return 0;
  let bgEl = e, bg = 'rgba(0, 0, 0, 0)';
  while (bgEl && /rgba\(.*,\s*0\)|transparent/.test(bg)) { bg = getComputedStyle(bgEl).backgroundColor; bgEl = bgEl.parentElement; }
  if (/rgba\(.*,\s*0\)|transparent/.test(bg)) bg = getComputedStyle(document.body).backgroundColor;
  const a = lum(getComputedStyle(e).color), b = lum(bg); return +((Math.max(a, b) + .05) / (Math.min(a, b) + .05)).toFixed(2);
};

const ALL = ['index.html', 'ctf.html', 'prompts.html', 'cyberlaw.html', 'terms.html', 'privacy.html', 'commands.html', 'scams.html', 'game.html', 'soc.html', 'owasp.html', 'terminal.html', 'daily.html', 'progress.html'].filter(has);
const MORE = ['commands.html', 'scams.html', 'game.html', 'soc.html', 'owasp.html', 'terminal.html', 'daily.html', 'progress.html'].filter(has);

// ---------- nav "More" menu on every page ----------
for (const pg of ALL) {
  for (const w of [1000, 1280]) {
    const p = await open(pg, { width: w, height: 800 });
    const n = await p.evaluate(() => {
      const nav = document.getElementById('nav-links'); const kids = [...nav.children].filter(k => getComputedStyle(k).display !== 'none');
      const mids = kids.map(k => { const r = k.getBoundingClientRect(); return r.top + r.height / 2; }); const tops = { size: Math.max(...mids) - Math.min(...mids) > 8 ? 2 : 1 };
      const inner = document.querySelector('.nav-inner').getBoundingClientRect();
      return { rows: tops.size, over: Math.round(nav.getBoundingClientRect().right - inner.right), more: [...document.querySelectorAll('.nav-more-menu > a')].map(a => a.getAttribute('href')) };
    });
    ok(`${pg} @${w}: nav one row with More menu listing ${MORE.length} pages`, n.rows === 1 && n.over <= 0 && JSON.stringify(n.more) === JSON.stringify(MORE), JSON.stringify(n));
    if (w === 1000) {
      await p.focus('.nav-more summary'); await p.keyboard.press('Enter'); await sleep(150);
      const o = await p.evaluate(() => ({ open: document.querySelector('.nav-more').open, exp: document.querySelector('.nav-more summary').getAttribute('aria-expanded'), vis: document.querySelector('.nav-more-menu a').getBoundingClientRect().height > 0 }));
      if (pg === 'commands.html') await shot(p, 'nav-more-dark.png');
      await p.keyboard.press('Escape'); await sleep(100);
      const c = await p.evaluate(() => ({ open: document.querySelector('.nav-more').open, f: document.activeElement.tagName }));
      await p.mouse.click(5, 400);
      ok(`${pg}: More opens with Enter (aria-expanded), Esc closes and returns focus`, o.open && o.exp === 'true' && o.vis && !c.open && c.f === 'SUMMARY', JSON.stringify({ o, c }));
      ok(`${pg}: no console errors`, p.errors.length === 0, p.errors.join(' | '));
    }
    await p.ctx.close();
  }
}
{ const p = await open('index.html', { width: 390, height: 800 });
  await p.click('.nav-toggle'); await sleep(400);
  await p.click('.nav-more summary'); await sleep(200);
  const r = await p.evaluate(() => { const a = document.querySelector('.nav-more-menu a'); const b = a.getBoundingClientRect(); return { h: b.height, inView: b.right <= innerWidth && b.left >= 0 }; });
  ok('mobile 390px: More expands inside the menu sheet', r.h > 30 && r.inView, JSON.stringify(r));
  await p.ctx.close(); }

// ---------- commands.html ----------
if (has('commands.html')) {
  const p = await open('commands.html');
  const cnt = async () => p.evaluate(() => [...document.querySelectorAll('.c-card')].filter(c => !c.hidden).length);
  const st = await p.evaluate(() => ({ cards: document.querySelectorAll('.c-card').length, os: document.querySelectorAll('#c-os .chip').length, cat: document.querySelectorAll('#c-cat .chip').length, count: document.getElementById('c-count').textContent, notice: !!document.querySelector('.notice-slim a[href="terms.html#authorised-use"]') }));
  ok('commands: 60 cards, OS chips All+4, task chips All+7, count line', st.cards === 60 && st.os === 5 && st.cat === 8 && /60 of 60/.test(st.count), JSON.stringify(st));
  ok('commands: slim Terms notice', st.notice);
  await shot(p, 'commands-dark.png');
  await p.click('#c-os .chip[data-id="windows"]'); await sleep(100);
  const win = await cnt();
  await p.click('#c-cat .chip[data-id="processes"]'); await sleep(100);
  const wp = await cnt(); const qs = await p.evaluate(() => location.search);
  ok('commands: OS chip Windows = 21, plus task Processes narrows further, state in URL', win === 21 && wp > 0 && wp < 21 && /os=windows/.test(qs) && /cat=processes/.test(qs), JSON.stringify({ win, wp, qs }));
  await p.click('#c-reset'); await sleep(100);
  await p.type('#c-search', 'hash'); await sleep(250);
  const hs = await p.evaluate(() => [...document.querySelectorAll('.c-card')].filter(c => !c.hidden).map(c => c.querySelector('.c-name').textContent));
  ok('commands: instant search "hash" finds sha256sum and Get-FileHash', hs.includes('sha256sum') && hs.includes('Get-FileHash'), JSON.stringify(hs));
  await p.evaluate(() => { const i = document.getElementById('c-search'); i.value = ''; i.dispatchEvent(new Event('input')); }); await p.type('#c-search', 'zzqqxx'); await sleep(250);
  ok('commands: no-match message', /No command matches/.test(await p.evaluate(() => document.getElementById('c-count').textContent)) && (await cnt()) === 0);
  await p.click('#c-reset'); await sleep(100);
  const ss = await p.$('#c-linux-ss');
  await (await ss.$('.copy')).click(); await sleep(200);
  const cp = await p.evaluate(async () => ({ clip: await navigator.clipboard.readText().catch(() => ''), btn: document.querySelector('#c-linux-ss .copy').textContent }));
  ok('commands: copy button copies the example', cp.clip === 'sudo ss -tulpn' && cp.btn === 'Copied', JSON.stringify(cp));
  const before = await p.evaluate(() => document.getElementById('cp-linux-ss').hidden);
  await (await ss.$('.c-more')).click(); await sleep(150);
  const ex = await p.evaluate(() => { const c = document.getElementById('c-linux-ss'); return { exp: c.querySelector('.c-more').getAttribute('aria-expanded'), hidden: document.getElementById('cp-linux-ss').hidden, text: document.getElementById('cp-linux-ss').textContent }; });
  ok('commands: card expands with typical output, blue team use, safety note and doc link', before && ex.exp === 'true' && !ex.hidden && /typical output/.test(ex.text) && /blue team use/.test(ex.text) && /safety note/.test(ex.text) && /Official docs/.test(ex.text), JSON.stringify(ex).slice(0, 200));
  await shot(p, 'commands-card-open-dark.png', '#c-linux-ss');
  const warn = await p.evaluate(() => ['#c-cross-platform-nmap', '#c-cross-platform-arp-a'].map(s => { const w = document.querySelector(s + ' .c-safety.warn'); return w && w.getBoundingClientRect().height > 0 && !w.closest('[hidden]') ? w.textContent : ''; }));
  ok('commands: nmap and arp show the safety note prominently without expanding', /written permission/.test(warn[0]) && /Read only/.test(warn[1]), JSON.stringify(warn));
  const others = await p.evaluate(() => document.querySelectorAll('.c-safety.warn').length);
  ok('commands: only those two cards use the prominent note', others === 2, String(others));
  const cr = await p.evaluate(contrastFn(), '.c-what'); const ck = await p.evaluate(contrastFn(), '.c-k');
  ok('commands: AA contrast dark (card text, labels)', cr >= 4.5 && ck >= 4.5, JSON.stringify({ cr, ck }));
  ok('commands: no console errors', p.errors.length === 0, p.errors.join(' | '));
  await p.ctx.close();
  const d = await open('commands.html#c-cross-platform-nmap');
  const dl = await d.evaluate(() => ({ exp: document.querySelector('#c-cross-platform-nmap .c-more').getAttribute('aria-expanded'), top: Math.round(document.getElementById('c-cross-platform-nmap').getBoundingClientRect().top), h: innerHeight }));
  ok('commands: #c-<id> deep link opens and scrolls to the card', dl.exp === 'true' && dl.top > 0 && dl.top < dl.h, JSON.stringify(dl));
  await d.ctx.close();
  const q = await open('commands.html?os=cisco_ios&q=vlan');
  const qc = await q.evaluate(() => [...document.querySelectorAll('.c-card')].filter(c => !c.hidden).map(c => c.querySelector('.c-name').textContent));
  ok('commands: ?os=&q= prefill', qc.length >= 1 && qc.every(n => n.startsWith('show')), JSON.stringify(qc));
  await q.ctx.close();
  const l = await open('commands.html', { scheme: 'light' });
  const lr = await l.evaluate(contrastFn(), '.c-what'), lk = await l.evaluate(contrastFn(), '.c-k'), ln = await l.evaluate(contrastFn(), '.c-name');
  ok('commands: AA contrast light', lr >= 4.5 && lk >= 4.5 && ln >= 4.5, JSON.stringify({ lr, lk, ln }));
  await shot(l, 'commands-light.png'); await l.ctx.close();
  const m = await open('commands.html', { width: 390, height: 844 });
  const mo = await m.evaluate(() => document.documentElement.scrollWidth <= innerWidth);
  ok('commands: no horizontal scroll at 390px', mo);
  await shot(m, 'commands-mobile.png'); await m.ctx.close();
  const k = await open('commands.html');
  await k.keyboard.press('/'); await sleep(100);
  ok('commands: "/" focuses search', await k.evaluate(() => document.activeElement.id === 'c-search'));
  await k.keyboard.press('Escape');
  await k.keyboard.down('Control'); await k.keyboard.press('k'); await k.keyboard.up('Control'); await sleep(400);
  await k.type('#pal-input', 'Get-FileHash'); await sleep(300);
  const hit = await k.evaluate(() => [...document.querySelectorAll('#pal-list a, #pal-list [data-u], #pal-list li')].map(a => a.getAttribute('href') || a.dataset.u || a.textContent).join(' '));
  ok('commands: site search finds Command ref entries', /commands\.html#c-windows-get-filehash|Command ref/.test(hit), hit.slice(0, 200));
  await k.ctx.close();
  const sm = await get(BASE + 'sitemap.xml'), si = await get(BASE + 'data/search.json');
  ok('commands: in sitemap and search.json', /commands\.html/.test(sm.text) && /"u":"commands\.html#c-/.test(si.text));
  const html = (await get(BASE + 'commands.html')).text, data = (await get(BASE + 'data/commands.json')).text;
  ok('commands: no em or en dash in page or data', !/[\u2013\u2014]/.test(html + data));
}

await browser.close();
console.log(results.join('\n'));
const fail = results.filter(r => r.startsWith('FAIL')).length;
console.log(`\n${results.length - fail}/${results.length} passed`);
process.exit(fail ? 1 : 0);
