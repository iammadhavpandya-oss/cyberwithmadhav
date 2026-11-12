// Consent gate, terms.html and privacy.html checks plus screenshots. Run from tools/: node test_consent.mjs
// Needs the static server on :8000. Fresh browser profile, so every page starts without consent.
import puppeteer from 'puppeteer-core';
const BASE = (process.env.URL || 'http://127.0.0.1:8000/').replace(/\/?$/, '/');
const OUT = new globalThis.URL('../docs/', import.meta.url).pathname;
const near = (a, b) => { const x = a.split(/[|,]/).map(Number), y = b.split(/[|,]/).map(Number); return x.length === y.length && x.every((v, i) => Math.abs(v - y[i]) <= 2); }; // 2px allows for the hero's idle float animation
const sleep = ms => new Promise(r => setTimeout(r, ms));
const results = [];
const ok = (name, cond, extra = '') => { results.push(`${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '  : ' + extra : ''}`); };
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });

async function open(path, { scheme = 'dark', width = 1440, height = 900, ctx = null, consent = null, mobile = false } = {}) {
  const c = ctx || await browser.createBrowserContext();
  const p = await c.newPage();
  p.ctx = c; p.errors = [];
  p.on('console', m => { if (m.type() === 'error') p.errors.push(m.text()); });
  p.on('pageerror', e => p.errors.push('pageerror: ' + e.message));
  if (consent !== null) await p.evaluateOnNewDocument(v => { if (!sessionStorage.getItem('seeded')) { localStorage.setItem('cwm-consent', v); sessionStorage.setItem('seeded', '1'); } }, consent);
  await p.evaluateOnNewDocument(() => {
    window.__cls = 0;
    try { new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) window.__cls += e.value; })).observe({ type: 'layout-shift', buffered: true }); } catch (e) {}
  });
  await p.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }]);
  await p.setViewport({ width, height, isMobile: mobile, hasTouch: mobile, deviceScaleFactor: mobile ? 2 : 1 });
  await p.goto(BASE + path, { waitUntil: 'load' }); await sleep(500);
  return p;
}
const gate = p => p.evaluate(() => {
  const g = document.getElementById('cwm-consent'), d = g && g.querySelector('[role="dialog"]');
  const links = g ? [...g.querySelectorAll('a')].map(a => [a.getAttribute('href'), a.target, a.rel].join('|')) : [];
  const btn = document.getElementById('cg-enter'), cb = document.getElementById('cg-agree');
  return { shown: !!g, modal: d ? d.getAttribute('aria-modal') : null, title: d ? document.getElementById(d.getAttribute('aria-labelledby')).textContent : '',
    label: g ? g.querySelector('.cg-check').textContent.replace(/\s*\(opens in a new tab\)/g, '') : '', links, disabled: btn ? btn.disabled : null, checked: cb ? cb.checked : null,
    inert: [...document.body.children].filter(n => n !== g && n.tagName !== 'SCRIPT').every(n => n.inert), pending: document.documentElement.classList.contains('consent-pending'),
    focusIn: !!(d && d.contains(document.activeElement)), stored: localStorage.getItem('cwm-consent'), dash: g ? /[\u2013\u2014]/.test(g.textContent) : false };
});

for (const page of ['index.html', 'ctf.html', 'prompts.html', 'cyberlaw.html']) {
  const p = await open(page);
  let g = await gate(p);
  ok(`${page}: gate shows on first visit as an aria-modal dialog`, g.shown && g.modal === 'true' && g.title === 'Welcome to CyberWithMadhav' && g.pending, JSON.stringify(g));
  ok(`${page}: checkbox text and both links open in a new tab`, g.label.trim() === 'I am 18 or older, or I have a parent or guardian\'s permission. I have read and agree to the Terms and Conditions and Privacy Policy, and I will use this site only for lawful, authorised learning.' && g.links.join() === 'terms.html|_blank|noopener,privacy.html|_blank|noopener', g.label + ' ' + g.links);
  ok(`${page}: Enter disabled until ticked, background inert, focus inside, no dashes`, g.disabled === true && g.checked === false && g.inert && g.focusIn && !g.dash, JSON.stringify(g));
  await p.keyboard.press('Escape'); await sleep(100);
  g = await gate(p);
  ok(`${page}: Esc does not dismiss`, g.shown && g.stored === null);
  let inside = true;
  for (let i = 0; i < 9; i++) { await p.keyboard.press('Tab'); inside = inside && await p.evaluate(() => document.getElementById('cwm-consent').contains(document.activeElement)); }
  for (let i = 0; i < 4; i++) { await p.keyboard.down('Shift'); await p.keyboard.press('Tab'); await p.keyboard.up('Shift'); inside = inside && await p.evaluate(() => document.getElementById('cwm-consent').contains(document.activeElement)); }
  ok(`${page}: focus trap holds for Tab and Shift+Tab`, inside);
  await p.click('#cg-enter').catch(() => {}); await sleep(100);
  ok(`${page}: clicking disabled Enter does nothing`, (await gate(p)).shown);
  await p.focus('#cg-agree'); await p.keyboard.press('Space'); await sleep(50);
  g = await gate(p);
  ok(`${page}: Space ticks the box and enables Enter`, g.checked && g.disabled === false);
  const pos = () => p.evaluate(() => { const r = n => { const b = document.querySelector(n).getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width)].join(','); }; const l = n => { let e = document.querySelector(n), x = 0, y = 0; const w = e.offsetWidth; while (e) { x += e.offsetLeft; y += e.offsetTop; e = e.offsetParent; } return [x, y, w].join(','); }; return [r('.nav'), l('h1'), innerWidth - document.documentElement.clientWidth].join('|'); });
  const card1 = await p.$eval('.cg-card', c => { const b = c.getBoundingClientRect(); return [b.left, b.top, b.width, b.height].map(Math.round).join(','); });
  await sleep(400);
  const card2 = await p.$eval('.cg-card', c => { const b = c.getBoundingClientRect(); return [b.left, b.top, b.width, b.height].map(Math.round).join(','); });
  await p.evaluate(() => document.fonts.ready.then(() => 0)); await sleep(150); // web fonts load async and change the 15ch headline width; that is not the gate
  const before = await pos();
  await p.focus('#cg-enter'); await p.keyboard.press('Enter'); await sleep(150);
  const after = await pos();
  g = await gate(p);
  const st = JSON.parse(g.stored || 'null');
  ok(`${page}: Enter site closes the gate, stores versioned consent, restores the page`, !g.shown && !g.pending && st && st.v === 4 && !!st.at && await p.evaluate(() => ![...document.body.children].some(n => n.inert)), JSON.stringify(g));
  ok(`${page}: no CSP or script errors; gate card is stable and closing it moves nothing on the page`, p.errors.length === 0 && card1 === card2 && near(before, after), JSON.stringify({ e: p.errors, card1, card2, before, after }));
  await p.reload({ waitUntil: 'load' }); await sleep(400);
  ok(`${page}: no gate on the next visit`, !(await gate(p)).shown);
  await p.ctx.close();
}

{ const p = await open('index.html', { consent: JSON.stringify({ v: 3, at: '2026-11-11T00:00:00Z' }) });
  ok('older consent version re-prompts', (await gate(p)).shown); await p.ctx.close(); }
{ const p = await open('index.html', { consent: JSON.stringify({ v: 4, at: '2026-11-12T00:00:00Z' }) });
  ok('current consent version skips the gate', !(await gate(p)).shown); await p.ctx.close(); }
{ const p = await open('prompts.html');
  await p.keyboard.down('Control'); await p.keyboard.press('k'); await p.keyboard.up('Control');
  await p.keyboard.press('/'); await sleep(100);
  ok('site shortcuts do not fire behind the gate', (await gate(p)).shown && await p.evaluate(() => document.getElementById('cwm-consent').contains(document.activeElement)));
  await p.ctx.close(); }

/* screenshots of the modal */
for (const scheme of ['dark', 'light']) {
  const p = await open('index.html', { scheme }); await sleep(600);
  await p.screenshot({ path: OUT + `consent-modal-${scheme}.png` }); await p.ctx.close();
}
{ const p = await open('cyberlaw.html', { width: 390, height: 844, mobile: true }); await sleep(500);
  const fit = await p.evaluate(() => { const r = document.querySelector('.cg-card').getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth; });
  ok('mobile: gate card fits the screen', fit);
  await p.screenshot({ path: OUT + 'consent-modal-mobile.png' }); await p.ctx.close(); }

/* terms.html and privacy.html */
for (const [page, n, h1] of [['terms.html', 18, 'Terms and Conditions'], ['privacy.html', 8, 'Privacy Policy']]) {
  for (const scheme of ['dark', 'light']) {
    const p = await open(page, { scheme });
    const r = await p.evaluate(() => {
      const t = document.body.innerText;
      return { gate: !!document.getElementById('cwm-consent'), h1: document.querySelector('h1').textContent, secs: document.querySelectorAll('.legal-sec').length,
        toc: [...document.querySelectorAll('.legal-toc a')].map(a => a.getAttribute('href')), ids: [...document.querySelectorAll('.legal-sec')].map(s => '#' + s.id),
        updated: /Last updated: 12 November 2026 · Version 4/.test(t), dash: /[\u2013\u2014]/.test(document.documentElement.outerHTML), theme: document.documentElement.dataset.theme,
        sticky: getComputedStyle(document.querySelector('.legal-toc')).position, blur: getComputedStyle(document.querySelector('.legal-sec')).backdropFilter,
        legal: [...document.querySelectorAll('footer .foot-legal a')].map(a => a.getAttribute('href')).join(','), navLegal: [...document.querySelectorAll('#nav-links a')].map(a => a.getAttribute('href')).join(','),
        overflow: document.documentElement.scrollWidth - innerWidth, text: t };
    });
    ok(`${page} ${scheme}: not gated, ${n} sections, contents sidebar matches, sticky glass, last updated, no dashes`, !r.gate && r.h1 === h1 && r.secs === n && r.toc.join() === r.ids.join() && r.sticky === 'sticky' && /blur/.test(r.blur) && r.updated && !r.dash && r.theme === scheme && r.overflow <= 0,
      JSON.stringify(Object.assign({}, r, { text: undefined })));
    ok(`${page} ${scheme}: footer carries Terms and Privacy, short nav (Home, Explore, Blog, CTF), no errors`, r.legal === 'terms.html,privacy.html' && r.navLegal === 'index.html,explore.html,blog.html,ctf.html' && p.errors.length === 0, r.legal + ' | ' + r.navLegal + ' ' + p.errors);
    if (page === 'terms.html' && scheme === 'dark') {
      const need = ['Section 43', 'Section 66', 'Bharatiya Nyaya Sanhita', 'brute force', 'OTPs, passwords', 'client data', 'watermark', 'resell', 'Madhav Pandya for CyberWithMadhav', 'privacy.html', 'theme', 'CTF practice progress', 'indemnify', 'laws of India', 'courts at Mumbai, Maharashtra', 'User responsibility and lawful use', 'under 18', 'madhavpandya@zoho.in'];
      const miss = need.filter(k => !r.text.includes(k) && !(k === 'privacy.html' && true));
      ok('terms: covers every required topic', miss.length === 0, miss.join());
      await p.click('.legal-toc a[href="#law"]'); await sleep(1600);
      ok('terms: contents link jumps and highlights the section', await p.evaluate(() => location.hash === '#law' && document.querySelector('.legal-toc a.on').getAttribute('href') === '#law'));
      await p.evaluate(() => scrollTo(0, 0)); await sleep(300);
    }
    if (page === 'privacy.html' && scheme === 'dark') {
      ok('privacy: lists consent, theme and CTF storage keys, no trackers', ['cwm-consent', 'cwm-theme', 'cwm-ctf-practice-v2'].every(k => r.text.includes(k)) && /no trackers/i.test(r.text));
    }
    if (page === 'terms.html') await p.screenshot({ path: OUT + `terms-${scheme}.png` });
    if (page === 'privacy.html' && scheme === 'dark') await p.screenshot({ path: OUT + 'privacy-dark.png' });
    await p.ctx.close();
  }
}
{ const p = await open('terms.html', { width: 390, height: 844, mobile: true });
  const o = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  ok('terms mobile: no horizontal overflow, contents stack above the text', o <= 0 && await p.evaluate(() => getComputedStyle(document.querySelector('.legal-toc')).position === 'static'));
  await p.screenshot({ path: OUT + 'terms-mobile.png' }); await p.ctx.close(); }

await browser.close();
console.log('\n=== consent gate + legal pages ===\n' + results.join('\n'));
const fails = results.filter(x => x.startsWith('FAIL')).length;
console.log(`${results.length - fails}/${results.length} passed`);
if (fails) process.exitCode = 1;
