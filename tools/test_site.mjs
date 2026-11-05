// Phase 2 site wide checks: social tags, manifest, service worker, Ctrl+K search, 404, sitemap and feed.
// Run from tools/: node test_site.mjs   Needs the static server on :8000. Serves a GitHub Pages like copy on :8001 for 404.html.
import puppeteer from 'puppeteer-core';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
const BASE = (process.env.URL || 'http://127.0.0.1:8000/').replace(/\/?$/, '/');
const LIVE = !!process.env.URL;
const SITE = new globalThis.URL('../', import.meta.url).pathname;
const OUT = SITE + 'docs/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
// Small GET helper on node:http(s); undici fetch trips over python http.server sockets.
import http from 'node:http'; import https from 'node:https';
const fetch = u => new Promise((res, rej) => (u.startsWith('https') ? https : http).get(u, r => {
  if (r.statusCode >= 300 && r.statusCode < 400 && r.headers.location) { r.resume(); return fetch(new globalThis.URL(r.headers.location, u).href).then(res, rej); }
  const ch = []; r.on('data', c => ch.push(c)); r.on('end', () => { const b = Buffer.concat(ch);
    res({ ok: r.statusCode < 400, status: r.statusCode, text: async () => b.toString('utf8'), json: async () => JSON.parse(b.toString('utf8')), arrayBuffer: async () => b }); });
}).on('error', rej));
const results = [];
const ok = (name, cond, extra = '') => { results.push(`${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '  : ' + extra : ''}`); };
const PAGES = ['index.html', 'explore.html', 'commands.html', 'scams.html', 'game.html', 'terminal.html', 'ctf.html', 'prompts.html', 'cyberlaw.html', 'terms.html', 'privacy.html']
  .concat(['soc.html'].filter(p => fs.existsSync(SITE + p)));
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });
async function open(url, { scheme = 'dark', width = 1440, height = 900 } = {}) {
  const c = await browser.createBrowserContext();
  const p = await c.newPage(); p.ctx = c; p.errors = [];
  p.on('console', m => { if (m.type() === 'error' && !/favicon|net::ERR_/.test(m.text())) p.errors.push(m.text()); });
  p.on('pageerror', e => p.errors.push('pageerror: ' + e.message));
  await p.evaluateOnNewDocument(() => { try { localStorage.setItem('cwm-consent', JSON.stringify({ v: 2, at: 'test' })); } catch (e) {} });
  await p.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }]);
  await p.setViewport({ width, height });
  await p.goto(url, { waitUntil: 'load' }); await sleep(700);
  return p;
}

// 1. head tags on every page
for (const pg of PAGES) {
  const h = await (await fetch(BASE + pg)).text();
  const has = re => re.test(h);
  ok(`${pg}: og:image 1200x630 + twitter:image + manifest + touch icon`,
    has(/property="og:image" content="https:\/\/iammadhavpandya-oss\.github\.io\/cyberwithmadhav\/assets\/img\/og-image\.png"/) && has(/og:image:width" content="1200"/) && has(/og:image:height" content="630"/)
    && has(/name="twitter:card" content="summary_large_image"/) && has(/name="twitter:image" content="https:[^"]+og-image\.png"/) && has(/rel="manifest" href="manifest\.json"/) && has(/rel="apple-touch-icon"/));
  ok(`${pg}: pwa.js${pg === 'index.html' ? '' : ' + search.js'} loaded`, has(/assets\/js\/pwa\.js/) && (pg === 'index.html' || has(/assets\/js\/search\.js/)));
}
{ const r = await fetch(BASE + 'assets/img/og-image.png'); const b = Buffer.from(await r.arrayBuffer());
  ok('og-image.png is a 1200x630 PNG', r.ok && b.readUInt32BE(16) === 1200 && b.readUInt32BE(20) === 630, `${b.readUInt32BE(16)}x${b.readUInt32BE(20)}`); }
{ const m = await (await fetch(BASE + 'manifest.json')).json();
  const icons = await Promise.all(m.icons.map(i => fetch(BASE + i.src).then(r => r.ok)));
  ok('manifest: name, start_url, standalone, icons 192 and 512 resolve', m.name && m.start_url && m.display === 'standalone' && m.icons.some(i => i.sizes === '192x192') && m.icons.some(i => i.sizes === '512x512') && icons.every(Boolean)); }

// 2. sitemap and feed
{ const sm = await (await fetch(BASE + 'sitemap.xml')).text();
  const locs = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]);
  ok('sitemap lists every public page, no 404', PAGES.every(p => locs.some(l => p === 'index.html' ? /cyberwithmadhav\/$/.test(l) : l.endsWith('/' + p))) && !locs.some(l => /404/.test(l)), locs.length + ' urls');
  const fd = await (await fetch(BASE + 'feed.xml')).text();
  ok('feed.xml: RSS 2.0 with one item per page and self link', /<rss version="2.0"/.test(fd) && (fd.match(/<item>/g) || []).length === PAGES.length && /atom:link href="[^"]+feed\.xml" rel="self"/.test(fd));
  const p = await open(BASE + 'feed.xml');
  ok('feed.xml is well formed XML', await p.evaluate(() => !document.querySelector('parsererror')));
  await p.ctx.close(); }
ok('LICENSE is MIT', !LIVE ? /^MIT License/.test(fs.readFileSync(SITE + 'LICENSE', 'utf8')) : true);

// 3. search index and palette
const idx = await (await fetch(BASE + 'data/search.json')).json();
{ const kinds = new Set(idx.map(i => i.k));
  ok('search.json covers pages, sections, sheets, commands, CTF, prompts, law and legal', ['Page', 'Section', 'Sheet', 'Command', 'CTF', 'Prompt', 'Law term', 'Law FAQ', 'Case', 'Legal'].every(k => kinds.has(k)), idx.length + ' entries');
  const pagesOk = await Promise.all([...new Set(idx.map(i => i.u.split(/[?#]/)[0]))].map(u => fetch(BASE + u).then(r => r.ok)));
  ok('every search result points at a page that exists', pagesOk.every(Boolean)); }
for (const pg of ['prompts.html', 'cyberlaw.html', 'terms.html']) {
  const p = await open(BASE + pg, { width: 1000 });
  ok(`${pg}: ⌘K button in nav`, !!(await p.$('#nav-links .pal-btn')));
  await p.keyboard.down('Control'); await p.keyboard.press('k'); await p.keyboard.up('Control'); await sleep(300);
  const st = await p.evaluate(() => ({ open: document.getElementById('palette').open, focus: document.activeElement.id }));
  ok(`${pg}: Ctrl+K opens the site search with focus in the input`, st.open && st.focus === 'pal-input');
  await p.type('#pal-input', 'nmap'); await sleep(200);
  const first = await p.$$eval('#pal-list [role=option]', li => li.map(x => x.textContent));
  ok(`${pg}: typing "nmap" finds cheat sheet commands`, first.length > 0 && first.some(t => /nmap/i.test(t)), first[0]);
  await p.keyboard.press('Escape'); await sleep(200);
  ok(`${pg}: Esc closes`, !(await p.evaluate(() => document.getElementById('palette').open)));
  ok(`${pg}: no console errors`, p.errors.length === 0, p.errors.join(' | '));
  if (pg === 'prompts.html') {
    await p.keyboard.down('Control'); await p.keyboard.press('k'); await p.keyboard.up('Control'); await sleep(200);
    const term = idx.find(i => i.k === 'Law term').t;
    await p.type('#pal-input', term); await sleep(200);
    await p.screenshot({ path: OUT + 'search-palette-dark.png' });
    await Promise.all([p.waitForNavigation({ waitUntil: 'load' }), p.keyboard.press('Enter')]); await sleep(1200);
    ok('Enter on a result navigates (cyber law glossary deep link prefills the search)', /cyberlaw\.html/.test(p.url()) && (await p.$eval('#gl-search', e => e.value)).length > 0, p.url());
  }
  await p.ctx.close();
}
{ const p = await open(BASE + 'index.html');
  await p.keyboard.down('Control'); await p.keyboard.press('k'); await p.keyboard.up('Control'); await sleep(300);
  await p.type('#pal-input', 'Phishing email triage'); await sleep(300);
  const r = await p.$$eval('#pal-list [role=option]', li => li.map(x => x.textContent));
  ok('index palette also finds other pages (prompts)', r.some(t => /Prompt/.test(t)), r.slice(0, 2).join(' / '));
  await p.ctx.close(); }
{ const p = await open(BASE + 'index.html?q=' + encodeURIComponent('Show current directory and list all files with details') + '#cheatsheets'); await sleep(800);
  ok('cheat sheet deep link ?q= filters to the command', (await p.$eval('#cs-search', e => e.value)).startsWith('Show current') && (await p.$$('#cs-list .cmd.copyable')).length >= 1);
  await p.ctx.close(); }
{ const p = await open(BASE + 'prompts.html?q=phishing#library'); await sleep(800);
  ok('prompts deep link ?q= prefills search', (await p.$eval('#p-search', e => e.value)) === 'phishing');
  await p.ctx.close(); }

// 4. service worker
if (!LIVE || BASE.startsWith('https:')) {
  const p = await open(BASE + 'prompts.html');
  const sw = await p.evaluate(async () => { const r = await navigator.serviceWorker.ready; await new Promise(res => setTimeout(res, 1500)); const keys = await caches.keys(); const c = keys.length ? await caches.open(keys[0]) : null; const ks = c ? (await c.keys()).map(r => new URL(r.url).pathname) : []; return { scope: r.scope, keys, n: ks.length, hasCtf: ks.some(k => k.endsWith('/ctf.html')), has404: ks.some(k => k.endsWith('/404.html')) }; });
  ok('service worker registers and precaches core pages', sw.keys.length === 1 && /^cwm-offline-/.test(sw.keys[0]) && sw.hasCtf && sw.has404 && sw.n > 15, JSON.stringify(sw));
  await p.reload({ waitUntil: 'load' }); await sleep(500);
  ok('service worker controls the page after reload', await p.evaluate(() => !!navigator.serviceWorker.controller));
  ok('cached 404.html is the branded page (offline fallback)', await p.evaluate(async () => { const r = await caches.match('404.html'); return !!r && /This page went missing/.test(await r.text()); }));
  await p.ctx.close();
}

// 5. 404 page (served under /cyberwithmadhav/ like GitHub Pages, including a nested path)
let srv = null, NF = null;
if (LIVE) NF = BASE + 'deep/missing/page.html';
else {
  const root = '/tmp/cwm-ghp', mount = root + '/cyberwithmadhav';
  fs.rmSync(root, { recursive: true, force: true }); fs.mkdirSync(mount + '/deep/missing', { recursive: true });
  for (const f of fs.readdirSync(SITE)) if (!['tools', 'backend', '.git'].includes(f)) fs.symlinkSync(SITE + f, mount + '/' + f);
  fs.copyFileSync(SITE + '404.html', mount + '/deep/missing/page.html'); // copy: py3.13 http.server refuses out-of-tree symlinks
  srv = spawn('python3', ['-m', 'http.server', '8001', '--bind', '127.0.0.1'], { cwd: root, stdio: 'ignore' }); await sleep(900);
  NF = 'http://127.0.0.1:8001/cyberwithmadhav/deep/missing/page.html';
}
for (const scheme of ['dark', 'light']) {
  const p = await open(NF, { scheme });
  const r = await p.evaluate(() => {
    const css = [...document.styleSheets].filter(s => s.href && /assets\/css/.test(s.href)).length;
    return { h1: document.querySelector('h1').textContent, css, path: document.getElementById('nf-path').textContent, home: document.querySelector('.nf-actions a').href, star: !!document.querySelector('#starfield'), btn: !!document.querySelector('#nav-links .pal-btn') };
  });
  ok(`404 (${scheme}): branded page with styles, path, home link and search even when nested`, r.h1 === 'This page went missing.' && r.css >= 2 && /deep\/missing\/page\.html/.test(r.path) && /\/cyberwithmadhav\/index\.html$/.test(r.home) && r.btn, JSON.stringify(r));
  ok(`404 (${scheme}): no console errors`, p.errors.length === 0, p.errors.join(' | '));
  if (scheme === 'dark') {
    await p.click('#nf-search'); await sleep(300);
    ok('404: Search the site button opens the palette', await p.evaluate(() => document.getElementById('palette').open));
    await p.keyboard.press('Escape'); await sleep(200);
  }
  await p.screenshot({ path: OUT + `404-${scheme}.png` });
  await p.ctx.close();
}
if (srv) srv.kill();

// 6. about and contact screenshots
{ const p = await open(BASE + 'index.html');
  await p.evaluate(() => document.getElementById('about').scrollIntoView()); await sleep(900);
  const a = await p.$('.about-card'); if (a) await a.screenshot({ path: OUT + 'avatar-dark.png' });
  await p.evaluate(() => document.getElementById('contact').scrollIntoView()); await sleep(900);
  await p.screenshot({ path: OUT + 'contact-follow-dark.png' });
  await p.ctx.close(); }

await browser.close();
console.log(results.join('\n'));
const fail = results.filter(r => r.startsWith('FAIL')).length;
console.log(`\n${results.length - fail}/${results.length} passed`);
process.exit(fail ? 1 : 0);
