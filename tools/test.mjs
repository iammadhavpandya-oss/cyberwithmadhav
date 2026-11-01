import puppeteer from 'puppeteer-core';
const URL = process.env.URL || 'http://127.0.0.1:8000/';
const OUT = '/workspace/cwm-site/docs';
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });
const results = []; const ok = (name, cond, extra='') => { results.push(`${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '  — ' + extra : ''}`); };
const errors = [];
const page = await browser.newPage();
await browser.defaultBrowserContext().overridePermissions(new globalThis.URL(URL).origin, ['clipboard-read','clipboard-write','clipboard-sanitized-write']);
page.on('console', m => { if (['error','warning'].includes(m.type())) errors.push(`${m.type()}: ${m.text()}`); });
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('requestfailed', r => errors.push('requestfailed: ' + r.url() + ' ' + r.failure()?.errorText));
await page.setViewport({ width: 1440, height: 900 });
await page.goto(URL, { waitUntil: 'networkidle0' });
await page.waitForSelector('.sheet');

// subnet calc
const sc = await page.evaluate(() => {
  const f = window.cwmCalcSubnet; const r = {};
  r.a = f('192.168.1.10/24'); r.b = f('10.20.30.40/13'); r.c = f('172.16.5.4/30'); r.d = f('8.8.8.8/32'); r.e = f('192.168.0.1/31');
  try { f('300.1.1.1/24'); r.err1 = 'no error'; } catch (e) { r.err1 = e.message; }
  try { f('1.2.3.4/33'); r.err2 = 'no error'; } catch (e) { r.err2 = e.message; }
  return r; });
ok('subnet /24 network+broadcast+hosts', sc.a['Network']==='192.168.1.0' && sc.a['Broadcast']==='192.168.1.255' && sc.a['Usable hosts']==='254' && sc.a['Type'].startsWith('Private'));
ok('subnet /13', sc.b['Network']==='10.16.0.0' && sc.b['Broadcast']==='10.23.255.255' && sc.b['Subnet mask']==='255.248.0.0', JSON.stringify([sc.b['Network'],sc.b['Broadcast'],sc.b['Usable hosts']]));
ok('subnet /30', sc.c['First host']==='172.16.5.5' && sc.c['Last host']==='172.16.5.6' && sc.c['Usable hosts']==='2');
ok('subnet /32 public', sc.d['Usable hosts']==='1' && sc.d['Type']==='Public');
ok('subnet /31 (RFC 3021)', sc.e['Usable hosts']==='2');
ok('subnet rejects bad octet', /0–255/.test(sc.err1)); ok('subnet rejects /33', /prefix/i.test(sc.err2));
// UI path
await page.$eval('#subnet-input', el => el.value = '');
await page.type('#subnet-input', '10.0.0.77/26');
await page.click('#subnet-form button');
const ui = await page.$$eval('#subnet-out div', ds => Object.fromEntries(ds.map(d => [d.querySelector('dt').textContent, d.querySelector('dd').textContent])));
ok('subnet UI form 10.0.0.77/26', ui['Network']==='10.0.0.64' && ui['Broadcast']==='10.0.0.127' && ui['Usable hosts']==='62');
await page.$eval('#subnet-input', el => el.value = 'hello');
await page.click('#subnet-form button');
ok('subnet UI shows error', (await page.$eval('#subnet-error', e => e.textContent)).length > 0);
await page.$eval('#subnet-input', el => el.value = '192.168.1.10/24'); await page.click('#subnet-form button');

// search & filter
const totalSheets = await page.$$eval('.sheet', s => s.length);
ok('all 9 cheat sheets render', totalSheets === 9, String(totalSheets));
await page.type('#cs-search', 'nmap -sV'); await new Promise(r => setTimeout(r, 300));
const s1 = await page.evaluate(() => ({ sheets: [...document.querySelectorAll('.sheet')].map(s => s.dataset.id), marks: document.querySelectorAll('#cs-list mark').length, count: document.querySelector('#cs-count').textContent }));
ok('search "nmap -sV" → nmap only, highlighted', s1.sheets.join()==='nmap' && s1.marks > 0, `${s1.count}`);
await page.$eval('#cs-search', el => { el.value = 'zzzqqq'; el.dispatchEvent(new Event('input')); }); await new Promise(r => setTimeout(r, 300));
ok('search no-match shows empty state', !!(await page.$('#cs-list .empty')));
await page.$eval('#cs-search', el => { el.value = 'dns'; el.dispatchEvent(new Event('input')); }); await new Promise(r => setTimeout(r, 300));
const s3 = await page.$$eval('.sheet', s => s.map(x => x.dataset.id));
ok('search "dns" spans multiple sheets', s3.length >= 2, s3.join(','));
await page.$eval('#cs-search', el => { el.value = ''; el.dispatchEvent(new Event('input')); }); await new Promise(r => setTimeout(r, 300));
await page.click('.chip[data-cat="Windows"]');
const s4 = await page.$$eval('.sheet', s => s.map(x => x.dataset.id));
ok('filter chip "Windows"', s4.join()==='windows', s4.join());
await page.click('.chip[data-cat="All"]');

// copy
await page.click('.sheet[data-id="linux"] .copy');
await new Promise(r => setTimeout(r, 200));
const clip = await page.evaluate(() => navigator.clipboard.readText().catch(e => 'ERR ' + e.message));
ok('copy button copies command', clip === 'pwd && ls -la', JSON.stringify(clip));

// roadmap tabs
await page.click('#tab-advanced');
ok('roadmap tab switch', await page.$eval('#panel-advanced', p => !p.hidden) && await page.$eval('#panel-beginner', p => p.hidden));
await page.click('#tab-beginner');

// counts
const counts = await page.evaluate(() => ({ jobs: document.querySelectorAll('.job').length, scams: document.querySelectorAll('.scam').length, net: document.querySelectorAll('.net-card').length, tl: document.querySelectorAll('#timeline li').length, proj: document.querySelectorAll('.project').length }));
ok('jobs=7, scams>=5, net cards, timeline, projects', counts.jobs===7 && counts.scams>=5 && counts.net>=10 && counts.tl===4 && counts.proj===2, JSON.stringify(counts));

// forms against local backend
await page.type('#nl-email', 'reader@example.com'); await page.click('#newsletter-form button[type=submit]');
await page.waitForFunction(() => document.querySelector('#newsletter-form .form-status').textContent.length > 0, { timeout: 5000 });
ok('newsletter form → backend', (await page.$eval('#newsletter-form .form-status', e => e.className + ' ' + e.textContent)).includes('ok'), await page.$eval('#newsletter-form .form-status', e => e.textContent));
await page.type('#c-name', 'Test User'); await page.type('#c-email', 'test@example.com'); await page.type('#c-msg', 'Hello from the headless test!');
await page.click('#contact-form button[type=submit]');
await page.waitForFunction(() => document.querySelector('#contact-form .form-status').textContent.length > 0, { timeout: 5000 });
ok('contact form → backend', (await page.$eval('#contact-form .form-status', e => e.className)).includes('ok'), await page.$eval('#contact-form .form-status', e => e.textContent));
await page.$eval('#nl-email', el => el.value = 'bad'); await page.click('#newsletter-form button[type=submit]');
ok('newsletter client validation', (await page.$eval('#newsletter-form .form-status', e => e.textContent)).includes('valid'));
await page.$eval('#nl-email', el => el.value = ''); await page.$$eval('.form-status', s => s.forEach(x => { x.textContent=''; x.className='form-status small'; }));

// theme toggle
await page.click('.theme-toggle');
ok('theme toggle → light', await page.evaluate(() => document.documentElement.dataset.theme) === 'light');
await page.click('.theme-toggle');

// meta
const meta = await page.evaluate(() => ({ og: !!document.querySelector('meta[property="og:title"]'), desc: !!document.querySelector('meta[name="description"]'), h1: document.querySelectorAll('h1').length, icon: document.querySelector('link[rel=icon]').href, lang: document.documentElement.lang }));
ok('SEO/OG meta, single h1, favicon, lang', meta.og && meta.desc && meta.h1 === 1 && meta.lang === 'en', JSON.stringify(meta));

// screenshots: reveal everything first
await page.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')));
await page.evaluate(() => { document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0, 0); }); await new Promise(r => setTimeout(r, 700));
await page.screenshot({ path: `${OUT}/desktop.png`, fullPage: true });
async function crop(sel, file, maxH = 1400) {
  const el = await page.$(sel); const b = await el.boundingBox();
  const y = b.y + (await page.evaluate(() => window.scrollY));
  await page.screenshot({ path: `${OUT}/${file}`, clip: { x: 0, y, width: 1440, height: Math.min(b.height, maxH) }, captureBeyondViewport: true });
}
await crop('.hero', 'hero.png'); await crop('#cheatsheets', 'cheatsheets.png', 1500); await crop('#about', 'about.png', 1500);
await crop('#networking', 'networking.png', 1500);

const m = await browser.newPage();
const mErr = [];
m.on('console', x => { if (['error','warning'].includes(x.type())) mErr.push(x.text()); }); m.on('pageerror', e => mErr.push(e.message));
await m.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
await m.goto(URL, { waitUntil: 'networkidle0' }); await m.waitForSelector('.sheet');
const overflow = await m.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
ok('mobile: no horizontal overflow', overflow <= 0, `overflow=${overflow}px`);
const closed = await m.$$eval('details.sheet', d => d.filter(x => !x.open).length);
ok('mobile: cheat sheets collapsed by default', closed === 9, String(closed));
await m.click('details.sheet[data-id="nmap"] summary');
ok('mobile: tap expands a sheet', await m.$eval('details.sheet[data-id="nmap"]', d => d.open));
await m.click('details.sheet[data-id="nmap"] summary');
await m.click('.nav-toggle'); ok('mobile menu opens', await m.$eval('#nav-links', n => n.classList.contains('open'))); await m.click('.nav-toggle');
const ms = await browser.newPage();
await ms.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
await ms.goto(URL, { waitUntil: 'networkidle0' }); await ms.waitForSelector('.sheet');
await ms.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')));
await new Promise(r => setTimeout(r, 800));
await ms.screenshot({ path: `${OUT}/mobile-hero.png` });
await ms.screenshot({ path: `${OUT}/mobile.png`, fullPage: true });
ok('mobile: no console errors', mErr.length === 0, mErr.join(' | '));

// reduced motion
const rm = await browser.newPage();
await rm.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
await rm.goto(URL, { waitUntil: 'networkidle0' }); await rm.waitForSelector('.sheet');
ok('reduced motion: content visible without animation', await rm.$eval('#jobs .job', e => getComputedStyle(e).opacity === '1'));

// print css
await page.emulateMediaType('print');
ok('print CSS hides nav/hero, keeps cheat sheets', await page.evaluate(() => getComputedStyle(document.querySelector('.nav')).display === 'none' && getComputedStyle(document.querySelector('.hero')).display === 'none' && getComputedStyle(document.querySelector('#cheatsheets')).display !== 'none'));
await page.pdf({ path: '/tmp/cwm-cheatsheets-print.pdf', format: 'A4' });
await page.emulateMediaType('screen');

ok('desktop: no console errors/warnings/failed requests', errors.length === 0, errors.join(' | '));
console.log(results.join('\n'));
await browser.close();
