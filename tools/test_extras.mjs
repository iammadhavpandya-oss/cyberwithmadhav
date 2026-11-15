// New pages (Start here, Toolkit, Collaborate, Now), easter eggs, humans.txt, security.txt, robots.txt and 404 theme.
// Run from tools/: node test_extras.mjs   Needs the static server on :8000 (or URL=...).
import puppeteer from 'puppeteer-core';
const BASE = (process.env.URL || 'http://127.0.0.1:8000/').replace(/\/?$/, '/');
const results = []; const ok = (n, c, x = '') => results.push(`${c ? 'PASS' : 'FAIL'}  ${n}${x ? '  | ' + x : ''}`);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });
async function open(path, { scheme = 'dark', width = 1280, height = 900, reduce = false, lang } = {}) {
  const p = await browser.newPage(); p.ctx = { close: () => p.close() }; p.errors = [];
  p.on('console', m => { if (m.type() === 'error' && !/favicon|ERR_CONNECTION_REFUSED/.test(m.text())) p.errors.push(m.text()); });
  p.on('pageerror', e => p.errors.push('pageerror: ' + e.message));
  await p.evaluateOnNewDocument((lang) => { try { localStorage.setItem('cwm-consent', JSON.stringify({ v: 4, at: 'test' })); localStorage.setItem('cwm-lang', lang || 'en'); } catch (e) {} }, lang);
  await p.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }, { name: 'prefers-reduced-motion', value: reduce ? 'reduce' : 'no-preference' }]);
  await p.setViewport({ width, height });
  const r = await p.goto(BASE + path, { waitUntil: 'networkidle0' }); p.status = r.status(); await sleep(1500);
  return p;
}
const NEW = ['start-here.html', 'uses.html', 'collaborate.html', 'now.html'];
for (const pg of NEW) for (const scheme of ['dark', 'light']) {
  const p = await open(pg, { scheme });
  const r = await p.evaluate(() => ({
    h1: document.querySelector('h1')?.textContent, dash: /[\u2013\u2014]/.test(document.documentElement.outerHTML),
    ld: [...document.querySelectorAll('script[type="application/ld+json"]')].every(s => { try { JSON.parse(s.textContent); return true; } catch (e) { return false; } }),
    canon: document.querySelector('link[rel=canonical]')?.href, foot: !!document.querySelector('footer a[href="start-here.html"]'),
    overflow: document.documentElement.scrollWidth - innerWidth, hs: !!document.querySelector('.egg-hs') }));
  ok(`${pg} ${scheme}: 200, h1, valid JSON-LD, canonical, footer links, no dashes, no errors, handshake line`, p.status === 200 && r.h1 && r.ld && r.canon === 'https://www.cyberwithmadhav.com/' + pg && r.foot && !r.dash && r.overflow <= 0 && r.hs && p.errors.length === 0, JSON.stringify(r) + ' ' + p.errors.join(' | '));
  if (scheme === 'dark' && pg === 'start-here.html') await p.screenshot({ path: '/workspace/cwm-upgrade-start-here.png', fullPage: false });
  if (scheme === 'light' && pg === 'collaborate.html') await p.screenshot({ path: '/workspace/cwm-upgrade-collaborate.png', fullPage: false });
  await p.ctx.close();
}
{ // Hinglish
  const p = await open('start-here.html', { lang: 'hi' });
  const t = await p.evaluate(() => document.querySelector('[data-i18n="sh.safe.h"]').textContent);
  ok('start-here: Hinglish strings apply', /Mujhe bas online safe/.test(t), t); await p.ctx.close();
}
{ // mobile no overflow
  for (const pg of NEW) { const p = await open(pg, { width: 360, height: 760 }); const o = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); ok(`${pg}: no horizontal scroll at 360px`, o <= 0, String(o)); await p.ctx.close(); }
}
{ // eggs on the blog page
  const p = await open('blog-vpn-myths.html');
  await p.click('h1'); // focus somewhere neutral
  for (const k of ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a']) await p.keyboard.press(k);
  await sleep(500);
  const opened = await p.evaluate(() => { const s = document.querySelector('.egg-shell'); return !!s && !s.hidden && document.activeElement.id === 'egg-in'; });
  ok('Konami code opens the root shell and focuses its input', opened);
  await p.keyboard.type('sudo make me a coffee'); await p.keyboard.press('Enter'); await sleep(300);
  const out = await p.evaluate(() => document.querySelector('.egg-out').textContent);
  const toast = await p.evaluate(() => document.getElementById('toast')?.textContent || '');
  ok('shell: sudo make me a coffee answers 418 and shows the teapot toast', /418 I'm a teapot/.test(out) && /418/.test(toast), JSON.stringify({ out: out.slice(-200), toast }));
  await p.keyboard.type('cat flag.txt'); await p.keyboard.press('Enter'); await sleep(200);
  ok('shell: cat flag.txt prints the flag and points to the CTF', /CWM\{/.test(await p.evaluate(() => document.querySelector('.egg-out').textContent)));
  await p.keyboard.type('matrix'); await p.keyboard.press('Enter'); await sleep(400);
  ok('shell: matrix shows the packet rain', await p.evaluate(() => !document.querySelector('.egg-rain').hidden));
  await p.keyboard.press('Escape'); await sleep(100); await p.keyboard.press('Escape'); await sleep(200);
  ok('Esc stops the rain, then closes the shell', await p.evaluate(() => document.querySelector('.egg-shell').hidden));
  await p.evaluate(() => document.querySelector('a.brand').focus());
  await p.keyboard.type('sudo'); await sleep(400);
  ok('typing sudo opens the shell; Esc returns focus', await p.evaluate(() => !document.querySelector('.egg-shell').hidden));
  await p.keyboard.press('Escape'); await sleep(200);
  ok('focus returns to where it was', await p.evaluate(() => document.activeElement.classList.contains('brand')));
  await p.click('h1'); await p.keyboard.type('coffee'); await sleep(300);
  ok('typing coffee shows HTTP 418', /418/.test(await p.evaluate(() => document.getElementById('toast').textContent)));
  const hv = await p.evaluate(() => matchMedia('(hover: hover)').matches);
  const hex = await p.evaluate(() => document.querySelector('main h2.egg-hex')?.getAttribute('data-hex'));
  ok('headings carry a hex label for hover (mouse devices only)', hv ? /^0x[0-9a-f]+/.test(hex || '') : !hex, hv + ' ' + hex);
  const src = await (await fetch(BASE + 'blog-vpn-myths.html')).text();
  ok('page source carries the hidden flag comment', /<!-- CWM\{v13w_s0urc3_l1k3_a_d3f3nd3r\}/.test(src));
  ok('no console errors with the eggs', p.errors.length === 0, p.errors.join(' | '));
  await p.ctx.close();
}
{ // inputs never trigger, reduced motion skips rain
  const p = await open('index.html', { reduce: true });
  await p.focus('#c-name'); await p.keyboard.type('sudo coffee');
  ok('typing in a form field never triggers an egg', await p.evaluate(() => !document.querySelector('.egg-shell') || document.querySelector('.egg-shell').hidden));
  await p.click('h2'); for (const k of ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a']) await p.keyboard.press(k); await sleep(400);
  await p.keyboard.type('matrix'); await p.keyboard.press('Enter'); await sleep(300);
  const rm = await p.evaluate(() => ({ open: !!document.querySelector('.egg-shell') && !document.querySelector('.egg-shell').hidden, rain: document.querySelector('.egg-rain')?.hidden, out: document.querySelector('.egg-out')?.textContent.slice(-160), act: document.activeElement.id }));
  ok('reduced motion: matrix is skipped', rm.open && rm.rain && /reduced motion/.test(rm.out), JSON.stringify(rm));
  for (let i = 0; i < 5; i++) { await p.click('a.brand'); await sleep(80); }
  await sleep(200);
  ok('home: 5 logo clicks brew a teapot', /418/.test(await p.evaluate(() => document.getElementById('toast')?.textContent || '')));
  ok('home: no console errors', p.errors.length === 0, p.errors.join(' | '));
  await p.ctx.close();
}
{ // text files and 404
  const h = await fetch(BASE + 'humans.txt'), s = await fetch(BASE + '.well-known/security.txt'), r = await (await fetch(BASE + 'robots.txt')).text();
  const st = await s.text();
  ok('humans.txt served', h.ok && /Madhav Pandya/.test(await h.text()));
  ok('security.txt has Contact, Expires in the future, Canonical', s.ok && /^Contact: mailto:madhavpandya@zohomail\.in$/m.test(st) && new Date(st.match(/^Expires: (.+)$/m)[1]) > new Date() && /^Canonical: https:\/\/www\.cyberwithmadhav\.com\/\.well-known\/security\.txt$/m.test(st));
  ok('robots.txt still allows everything and lists the sitemap', /^User-agent: \*$/m.test(r) && /^Allow: \/$/m.test(r) && !/^Disallow/m.test(r) && /^Sitemap: https:\/\/www\.cyberwithmadhav\.com\/sitemap\.xml$/m.test(r));
  const nf = await (await fetch(BASE + '404.html')).text();
  ok('404 is themed as packet lost with traceroute', /packet lost/.test(nf) && /TTL expired in transit/.test(nf) && /traceroute home/.test(nf));
}
await browser.close();
console.log(results.join('\n'));
const f = results.filter(r => r.startsWith('FAIL')).length;
console.log(`\n${results.length - f} passed, ${f} failed`); process.exit(f ? 1 : 0);
