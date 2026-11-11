// Feature page checks (phases 3 to 8): short top nav, explore hub, commands.html, and later pages when they exist.
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
  await p.evaluateOnNewDocument(s => { try { localStorage.setItem('cwm-consent', JSON.stringify({ v: 3, at: 'test' })); if (s) for (const k in s) localStorage.setItem(k, s[k]); } catch (e) {} }, storage);
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

const ALL = ['index.html', 'explore.html', 'ctf.html', 'prompts.html', 'cyberlaw.html', 'terms.html', 'privacy.html', 'commands.html', 'scams.html', 'game.html', 'soc.html', 'owasp.html', 'terminal.html', 'daily.html', 'progress.html'].filter(has);
// ---------- short top nav on every page: Home, Explore, CTF, search, theme ----------
const NAV = 'index.html,explore.html,blog.html,ctf.html';
for (const pg of ALL) {
  for (const w of [1000, 1280]) {
    const p = await open(pg, { width: w, height: 800 });
    const n = await p.evaluate(() => {
      const nav = document.getElementById('nav-links'); const kids = [...nav.children].filter(k => getComputedStyle(k).display !== 'none');
      const mids = kids.map(k => { const r = k.getBoundingClientRect(); return r.top + r.height / 2; }); const tops = { size: Math.max(...mids) - Math.min(...mids) > 8 ? 2 : 1 };
      const inner = document.querySelector('.nav-inner').getBoundingClientRect();
      return { rows: tops.size, over: Math.round(nav.getBoundingClientRect().right - inner.right), links: [...nav.querySelectorAll('a')].map(a => a.getAttribute('href')).join(','),
        pal: !!nav.querySelector('.pal-btn'), theme: !!nav.querySelector('.theme-toggle'), more: !!document.querySelector('.nav-more'),
        cur: (nav.querySelector('[aria-current="page"]') || {}).textContent || '' };
    });
    const wantCur = { 'index.html': 'Home', 'explore.html': 'Explore', 'ctf.html': 'CTF' }[pg] || '';
    ok(`${pg} @${w}: short nav in one row (Home, Explore, Blog, CTF, search, language, theme)`, n.rows === 1 && n.over <= 0 && n.links === NAV && n.pal && n.theme && !n.more && n.cur.trim() === wantCur, JSON.stringify(n));
    if (w === 1000) ok(`${pg}: no console errors`, p.errors.length === 0, p.errors.join(' | '));
    await p.ctx.close();
  }
}
{ const p = await open('index.html', { width: 390, height: 800 });
  await p.click('.nav-toggle'); await sleep(400);
  const r = await p.evaluate(() => { const a = document.querySelector('#nav-links a[href="explore.html"]'); const b = a.getBoundingClientRect(); return { h: b.height, inView: b.right <= innerWidth && b.left >= 0 }; });
  ok('mobile 390px: menu sheet shows Explore', r.h > 30 && r.inView, JSON.stringify(r));
  await p.ctx.close(); }

// ---------- explore.html hub ----------
if (has('explore.html')) {
  const p = await open('explore.html');
  const r = await p.evaluate(() => {
    const cards = [...document.querySelectorAll('.mc-card')];
    return { zones: [...document.querySelectorAll('.mc-zone[id] h2')].map(h => h.textContent.trim()).join(','), n: cards.length,
      named: cards.every(c => c.querySelector('.mc-title a') && c.querySelector('.mc-tag').textContent.trim().length > 10),
      hrefs: cards.map(c => c.querySelector('.mc-title a').getAttribute('href')),
      dash: /[\u2013\u2014]/.test(document.documentElement.outerHTML), overflow: document.documentElement.scrollWidth - innerWidth };
  });
  const need = ['cyberlaw.html', 'commands.html', 'ctf.html', 'terminal.html', 'scams.html', 'game.html', 'prompts.html', 'terms.html', 'privacy.html', 'index.html#networking', 'index.html#tools'];
  ok('explore: zones Learn, Practice, Stay Safe, AI, Legal with a card for every page', r.zones === 'Learn,Practice,Stay Safe,AI,Legal' && need.every(h => r.hrefs.includes(h)) && r.named && !r.dash && r.overflow <= 0, JSON.stringify(r));
  const brk = []; for (const h of r.hrefs) { const f = h.split('#')[0]; if (!has(f)) brk.push(h); }
  ok('explore: every card links to a page that exists', brk.length === 0, brk.join());
  await shot(p, 'explore-dark.png');
  ok('explore: no console errors', p.errors.length === 0, p.errors.join(' | '));
  await p.ctx.close();
}

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

// ---------- game.html: Scam ya Nahi? ----------
if (has('game.html')) {
  const data = JSON.parse((await get(BASE + 'data/game.json')).text);
  const p = await open('game.html?level=hard', { width: 390, height: 844 });
  // pure logic (window.CWMGame)
  const lg = await p.evaluate(items => {
    const L = window.CWMGame, ids = items.map(i => i.id).sort().join();
    const sh = L.shuffle(items, () => 0.3);
    const call = items.find(i => i.channel === 'call_script');
    return { all: L.filter(items, 'all').length, easy: L.filter(items, 'easy').length, med: L.filter(items, 'medium').length, hard: L.filter(items, 'hard').length,
      shuffleSame: sh.map(i => i.id).sort().join() === ids && sh.length === items.length,
      turns: L.turns(call).length >= 1 && L.turns(call).every(t => call.text.includes(t.text)),
      right: L.isRight({ scam: true }, true) && !L.isRight({ scam: false }, true),
      better: L.better(null, 0, 5) && L.better({ s: 3, t: 8 }, 4, 8) && !L.better({ s: 5, t: 8 }, 4, 8),
      share: L.shareUrl(3, 8, 'hard'), shareTxt: L.shareText(3, 8, 'hard') };
  }, data.items);
  const lv = data.items.reduce((a, i) => (a[i.level] = (a[i.level] || 0) + 1, a), {});
  ok('game logic: level filter, shuffle keeps every card, call turns, scoring, best rule', lg.all === data.items.length && lg.easy === lv.easy && lg.med === lv.medium && lg.hard === lv.hard && lg.shuffleSame && lg.turns && lg.right && lg.better, JSON.stringify(lg).slice(0, 200));
  ok('game logic: WhatsApp share is a wa.me/?text= link with score and page URL', lg.share.startsWith('https://wa.me/?text=') && decodeURIComponent(lg.share.slice(20)) === lg.shareTxt && /3\/8/.test(lg.shareTxt) && /game\.html/.test(lg.shareTxt), lg.share.slice(0, 80));
  ok('game: 30 cards, 18 scam, every linked card points at a scams.html anchor', data.items.length === 30 && data.items.filter(i => i.scam).length === 18 && data.items.filter(i => i.link).every(i => /^scams\.html#s-[a-z0-9-]+$/.test(i.link.href)));
  const scams = JSON.parse((await get(BASE + 'data/scams.json')).text).scams.map(s => 's-' + s.id);
  ok('game: linked anchors exist on scams.html', data.items.filter(i => i.link).every(i => scams.includes(i.link.href.split('#')[1])));
  const st0 = await p.evaluate(() => ({ chips: [...document.querySelectorAll('#g-level .chip')].map(c => c.textContent + ':' + c.getAttribute('aria-pressed')).join(','), count: document.getElementById('g-count').textContent,
    btns: ['g-btn-scam', 'g-btn-safe'].map(id => document.getElementById(id).textContent.trim()).join(','), live: document.getElementById('g-result').getAttribute('aria-live'),
    sender: document.getElementById('g-sender').textContent, over: document.documentElement.scrollWidth - innerWidth }));
  ok('game: ?level=hard preselects Hard (8 cards), Scam and Safe buttons with visible text, aria-live result', /Hard8:true/.test(st0.chips) && st0.count === String(lv.hard) && st0.btns === 'Scam,Safe' && st0.live === 'polite' && st0.sender.length > 2, JSON.stringify(st0));
  ok('game: no horizontal scroll at 390px', st0.over <= 0, String(st0.over));
  await shot(p, 'game-mobile-dark.png');
  // turn shuffle off so the order is the data order, then play the hard round
  await p.click('#g-shuffle'); await sleep(100);
  const hard = data.items.filter(i => i.level === 'hard');
  const s1 = await p.evaluate(() => ({ sh: document.getElementById('g-shuffle').getAttribute('aria-pressed'), sender: document.getElementById('g-sender').textContent }));
  ok('game: shuffle toggle off gives the data order', s1.sh === 'false' && s1.sender === hard[0].sender, JSON.stringify(s1));
  await p.click(hard[0].scam ? '#g-btn-scam' : '#g-btn-safe'); await sleep(200);
  const a1 = await p.evaluate(() => ({ pts: document.getElementById('g-points').textContent, tot: document.getElementById('g-total').textContent, res: document.getElementById('g-result').textContent,
    focus: document.activeElement.id, dis: document.getElementById('g-btn-scam').disabled, tells: document.querySelectorAll('#g-result .g-tells li').length }));
  ok('game: right answer scores 1/1 and reveals Sahi jawab, tells and the Hinglish explanation, focus moves to Next', a1.pts === '1' && a1.tot === '1' && /Sahi jawab/.test(a1.res) && a1.res.includes(hard[0].why) && a1.tells === hard[0].tells.length && a1.focus === 'g-next' && a1.dis, JSON.stringify(a1).slice(0, 200));
  await p.keyboard.press('Enter'); await sleep(250);
  const a2 = await p.evaluate(() => ({ pos: document.getElementById('g-pos').textContent, focus: document.activeElement.id, res: document.getElementById('g-result').textContent }));
  ok('game: Enter goes to the next card and focus lands on the message card', a2.pos === '2' && a2.focus === 'g-card' && a2.res === '', JSON.stringify(a2));
  await p.keyboard.press(hard[1].scam ? 'ArrowRight' : 'ArrowLeft'); await sleep(200);
  const a3 = await p.evaluate(() => ({ pts: document.getElementById('g-points').textContent, tot: document.getElementById('g-total').textContent, res: document.getElementById('g-result').textContent }));
  ok('game: arrow key answers (wrong on purpose shows Galat with the truth)', a3.pts === '1' && a3.tot === '2' && /Galat/.test(a3.res), JSON.stringify(a3).slice(0, 160));
  await p.keyboard.press('Enter'); await sleep(200);
  // swipe on touch: left = Scam
  const sw = await p.evaluate(() => {
    const c = document.getElementById('g-card'), r = c.getBoundingClientRect(), y = r.top + 40, x = r.left + r.width / 2;
    const ev = (t, dx) => c.dispatchEvent(new PointerEvent(t, { pointerId: 7, pointerType: 'touch', clientX: x + dx, clientY: y, bubbles: true }));
    ev('pointerdown', 0); ev('pointermove', -60); ev('pointermove', -140); ev('pointerup', -140);
    return { tot: document.getElementById('g-total').textContent, res: document.getElementById('g-result').textContent };
  });
  ok('game: swipe left on touch answers Scam', sw.tot === '3' && (hard[2].scam ? /Sahi jawab/ : /Galat/).test(sw.res), JSON.stringify(sw).slice(0, 120));
  for (let i = 3; i < hard.length; i++) { await p.click('#g-next'); await sleep(80); await p.click(hard[i].scam ? '#g-btn-scam' : '#g-btn-safe'); await sleep(80); }
  const nx = await p.evaluate(() => document.getElementById('g-next').textContent);
  await p.click('#g-next'); await sleep(250);
  const end = await p.evaluate(() => ({ end: !document.getElementById('g-end').hidden, play: document.getElementById('g-play').hidden, pts: document.getElementById('g-end-points').textContent, tot: document.getElementById('g-end-total').textContent,
    share: document.getElementById('g-share').href, target: document.getElementById('g-share').target, focus: document.activeElement.id, best: JSON.parse(localStorage.getItem('cwm-scamgame-best') || '{}'), missed: document.querySelectorAll('.g-miss li').length }));
  const want = hard.length - 1;
  ok('game: last card says See my score, end screen shows score/total and focus', nx === 'See my score' && end.end && end.play && end.pts === String(want) && end.tot === String(hard.length) && end.focus === 'g-end' && end.missed === 1, JSON.stringify(end).slice(0, 200));
  ok('game: end screen WhatsApp share link (user initiated, new tab)', end.share.startsWith('https://wa.me/?text=') && /game\.html/.test(decodeURIComponent(end.share)) && end.target === '_blank');
  ok('game: best score saved in localStorage per level', end.best.hard && end.best.hard.s === want && end.best.hard.t === hard.length, JSON.stringify(end.best));
  await shot(p, 'game-end-mobile-dark.png');
  ok('game: no console errors', p.errors.length === 0, p.errors.join(' | '));
  await p.ctx.close();
  // best is shown on the next visit; report line where the data says so; reduced motion
  const rep = data.items.find(i => i.report);
  const q = await open('game.html?level=' + rep.level, { reduce: true, storage: { 'cwm-scamgame-best': JSON.stringify({ [rep.level]: { s: 2, t: 9 } }) } });
  await q.click('#g-shuffle'); await sleep(100);
  const pool = data.items.filter(i => i.level === rep.level); const k = pool.indexOf(rep);
  for (let i = 0; i < k; i++) { await q.click('#g-btn-safe'); await sleep(60); await q.click('#g-next'); await sleep(60); }
  await q.click('#g-btn-scam'); await sleep(150);
  const r = await q.evaluate(() => ({ best: document.getElementById('g-best').textContent, rep: (document.querySelector('#g-result .g-report') || {}).textContent || '', tel: !!document.querySelector('#g-result .g-report a[href="tel:1930"]'),
    portal: !!document.querySelector('#g-result .g-report a[href="https://cybercrime.gov.in"]'), link: (document.querySelector('#g-result .g-link a') || {}).getAttribute?.('href') || '', anim: document.getElementById('g-card').classList.contains('enter'),
    trans: getComputedStyle(document.getElementById('g-card')).transitionDuration }));
  ok('game: report line "1930 / cybercrime.gov.in" where the explanation says so, plus the scams.html card link', /1930 \/ cybercrime\.gov\.in/.test(r.rep) && r.tel && r.portal && r.link === (rep.link ? rep.link.href : ''), JSON.stringify(r));
  ok('game: saved best shows on load; reduced motion turns off the card animation', r.best === '2 / 9' && !r.anim && /^0s/.test(r.trans), JSON.stringify(r));
  const safeOne = data.items.find(i => !i.report);
  ok('game: data has cards without a report line (shown only where the data says so)', !!safeOne);
  await q.ctx.close();
  const l = await open('game.html', { scheme: 'light', width: 1280 });
  const lc = await l.evaluate(contrastFn(), '.g-bubble p'), ls = await l.evaluate(contrastFn(), '.g-sender');
  ok('game: AA contrast light (bubble text, sender)', lc >= 4.5 && ls >= 4.5, JSON.stringify({ lc, ls }));
  await shot(l, 'game-light.png'); await l.ctx.close();
  const d = await open('game.html', { width: 1280 });
  const dc = await d.evaluate(contrastFn(), '.g-bubble p'), ds = await d.evaluate(contrastFn(), '.g-sender');
  ok('game: AA contrast dark (bubble text, sender)', dc >= 4.5 && ds >= 4.5, JSON.stringify({ dc, ds }));
  await shot(d, 'game-dark.png'); await d.ctx.close();
  const m = await open('game.html', { width: 360, height: 740 });
  ok('game: no horizontal scroll at 360px', await m.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await m.ctx.close();
  const sm = await get(BASE + 'sitemap.xml'), si = await get(BASE + 'data/search.json'), swj = await get(BASE + 'sw.js'), ex = await get(BASE + 'explore.html');
  ok('game: in sitemap, search.json, sw.js precache and the Explore hub', /game\.html/.test(sm.text) && /"u":"game\.html\?level=easy"/.test(si.text) && /"game\.html"/.test(swj.text) && /"assets\/js\/game\.js"/.test(swj.text) && /href="game\.html"/.test(ex.text));
  const gh = (await get(BASE + 'game.html')).text, gj = (await get(BASE + 'assets/js/game.js')).text, gc = (await get(BASE + 'assets/css/game.css')).text, gd = (await get(BASE + 'data/game.json')).text;
  ok('game: no em or en dash in page, script, styles or data', !/[\u2013\u2014]/.test(gh + gj + gc + gd));
  ok('game: no external scripts or styles', !/<script[^>]+src="https?:|<link[^>]+href="https?:[^"]+\.css/.test(gh));
}

await browser.close();
console.log(results.join('\n'));
const fail = results.filter(r => r.startsWith('FAIL')).length;
console.log(`\n${results.length - fail}/${results.length} passed`);
process.exit(fail ? 1 : 0);
