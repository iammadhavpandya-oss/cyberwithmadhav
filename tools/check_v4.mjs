// One-off check for the v4 update: console errors, CSP violations, horizontal overflow, JSON-LD parse,
// dashes, i18n toggle, and the review screenshots. Run from tools/ with the static server on :8000.
import puppeteer from 'puppeteer-core';
const BASE = 'http://127.0.0.1:8000/';
const OUT = '/workspace/cwm-about-review/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const res = [];
async function open(path, { w = 1440, h = 900, scheme = 'dark', mobile = false, consent = true, lang = 'en' } = {}) {
  const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });
  const p = await b.newPage(); p.ctx = b; p.errs = [];
  p.on('console', m => { if (['error', 'warning'].includes(m.type())) p.errs.push(m.text()); });
  p.on('pageerror', e => p.errs.push('pageerror ' + e.message));
  p.on('requestfailed', r => p.errs.push('failed ' + r.url()));
  await p.evaluateOnNewDocument((consent, lang) => { try { if (consent) localStorage.setItem('cwm-consent', JSON.stringify({ v: 4, at: 'x' })); localStorage.setItem('cwm-lang', lang); } catch (e) {} }, consent, lang);
  await p.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }]);
  await p.setViewport({ width: w, height: h, isMobile: mobile, hasTouch: mobile, deviceScaleFactor: mobile ? 2 : 1 });
  await p.goto(BASE + path, { waitUntil: 'networkidle0' }); await sleep(600);
  return p;
}
const pages = ['index.html', 'about.html', 'blog.html', 'blog-report-cyber-fraud-india.html', 'blog-digital-arrest-scam-india.html', 'blog-upi-scams-india.html', 'terms.html', 'privacy.html', 'scams.html', 'cyberlaw.html', 'explore.html', 'prompts.html', 'commands.html', 'game.html', 'terminal.html', 'ctf.html', '404.html'];
for (const pg of pages) for (const [lang, mobile] of [['en', false], ['hi', false], ['en', true]]) {
  const p = await open(pg, mobile ? { w: 390, h: 844, mobile: true, lang } : { lang });
  const r = await p.evaluate(() => {
    const ld = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { JSON.parse(s.textContent); return 'ok'; } catch (e) { return 'BAD ' + e.message; } });
    const t = document.body.innerText;
    return { ow: document.documentElement.scrollWidth - window.innerWidth, ld, dash: /[\u2013\u2014]/.test(t + document.title), lang: document.documentElement.lang,
      h1: document.querySelectorAll('h1').length, btn: !!document.querySelector('.lang-toggle'), pressed: document.querySelector('.lang-toggle')?.getAttribute('aria-pressed') };
  });
  const errs = p.errs.filter(e => !/ERR_CONNECTION_REFUSED|127\.0\.0\.1:5000/.test(e));
  const good = r.ow <= 0 && !r.ld.some(x => x !== 'ok') && !r.dash && errs.length === 0 && r.btn && r.lang === (lang === 'hi' ? 'hi-Latn' : 'en-IN') && r.pressed === String(lang === 'hi');
  console.error(pg, lang, mobile); res.push(`${good ? 'PASS' : 'FAIL'} ${pg} ${lang}${mobile ? ' mobile' : ''} ${JSON.stringify(r)} ${errs.join(' | ')}`);
  await p.ctx.close();
}
// toggling live
{ const p = await open('blog-upi-scams-india.html');
  const before = await p.$eval('h1', e => e.textContent);
  await p.click('.lang-toggle'); await sleep(200);
  const after = await p.evaluate(() => ({ h1: document.querySelector('h1').textContent, lang: document.documentElement.lang, store: localStorage.getItem('cwm-lang') }));
  await p.click('.lang-toggle'); await sleep(200);
  const back = await p.$eval('h1', e => e.textContent);
  res.push(`${before !== after.h1 && after.lang === 'hi-Latn' && after.store === 'hi' && back === before ? 'PASS' : 'FAIL'} toggle en>hi>en on post ${JSON.stringify(after)}`);
  await p.ctx.close(); }
// filter chips
{ const p = await open('blog.html'); const n = await p.$$eval('.bp-chips .chip', c => c.length);
  await p.click('.bp-chips .chip:nth-child(2)'); await sleep(100);
  const vis = await p.$$eval('#bp-grid .bp-card', c => c.filter(x => !x.hidden).length);
  res.push(`${n >= 2 && vis === 3 ? 'PASS' : 'FAIL'} blog chips ${n}, visible ${vis}`); await p.ctx.close(); }
// screenshots
{ const p = await open('blog.html'); await p.screenshot({ path: OUT + 'blog-listing-night.png', fullPage: true }); await p.ctx.close(); }
{ const p = await open('blog-digital-arrest-scam-india.html'); await p.screenshot({ path: OUT + 'blog-post-night-desktop.png', fullPage: true }); await p.ctx.close(); }
{ const p = await open('blog-report-cyber-fraud-india.html', { w: 390, h: 844, mobile: true, scheme: 'light' }); await p.screenshot({ path: OUT + 'blog-post-day-mobile.png', fullPage: true }); await p.ctx.close(); }
{ const p = await open('index.html'); await p.evaluate(() => { document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')); }); await sleep(300);
  await p.screenshot({ path: OUT + 'home-v4-night.png' });
  const el = await p.$('#next-level'); await el.scrollIntoView(); await sleep(400);
  await el.screenshot({ path: OUT + 'next-level-neon.png' });
  const bl = await p.$('#blog-latest'); await bl.scrollIntoView(); await sleep(400); await bl.screenshot({ path: OUT + 'home-v4-blog-block-night.png' });
  await p.ctx.close(); }
{ const p = await open('index.html', { scheme: 'light' }); await p.evaluate(() => { document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')); });
  const el = await p.$('#next-level'); await el.scrollIntoView(); await sleep(400); await el.screenshot({ path: OUT + 'next-level-neon-day.png' }); await p.ctx.close(); }
{ const p = await open('index.html', { consent: false }); await sleep(400); await p.screenshot({ path: OUT + 'consent-v3.png' });
  await p.click('#cwm-consent .cg-lang'); await sleep(300);
  const t = await p.$eval('#cg-title', e => e.textContent); res.push(`${/swagat/.test(t) ? 'PASS' : 'FAIL'} consent switches to Hinglish: ${t}`);
  await p.screenshot({ path: OUT + 'consent-v3-hinglish.png' });
  await p.click('#cg-agree'); await p.click('#cg-enter'); await sleep(200);
  const st = await p.evaluate(() => JSON.parse(localStorage.getItem('cwm-consent')).v); res.push(`${st === 4 ? 'PASS' : 'FAIL'} consent stored v${st}`);
  await p.ctx.close(); }
{ const p = await open('index.html', { lang: 'hi' }); await sleep(300); await p.screenshot({ path: OUT + 'lang-toggle-hinglish.png' }); await p.ctx.close(); }
{ const p = await open('index.html', { lang: 'hi', w: 390, h: 844, mobile: true }); await p.click('.nav-toggle'); await sleep(500); await p.screenshot({ path: OUT + 'lang-toggle-hinglish-mobile-menu.png' }); await p.ctx.close(); }
console.log(res.join('\n'));
console.log(res.filter(r => r.startsWith('FAIL')).length + ' fails of ' + res.length);
