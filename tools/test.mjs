import puppeteer from 'puppeteer-core';
const URL = process.env.URL || 'http://127.0.0.1:8000/';
const OUT = '/workspace/cwm-site/docs';
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });

// Consent gate: pre-accept for these suites (the gate itself is covered by test_consent.mjs).
{ const _np = browser.newPage.bind(browser); browser.newPage = async (...a) => { const p = await _np(...a); await p.evaluateOnNewDocument(() => { try { localStorage.setItem('cwm-consent', JSON.stringify({ v: 2, at: 'test' })); } catch (e) {} }); return p; }; }
const results = []; const ok = (name, cond, extra='') => { results.push(`${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '  | ' + extra : ''}`); };
const errors = [];
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
async function stubGitHub(p) {
  await p.setRequestInterception(true);
  p.on('request', r => {
    const u = r.url();
    if (u.startsWith('https://api.github.com/repos/')) return r.respond({ status: 200, contentType: 'application/json', headers: { 'Access-Control-Allow-Origin': '*' }, body: JSON.stringify({ stargazers_count: u.includes('geoimg') ? 3 : 0 }) });
    r.continue();
  });
}
const page = await browser.newPage();
await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'dark' }]);
await stubGitHub(page);
await browser.defaultBrowserContext().overridePermissions(new globalThis.URL(URL).origin, ['clipboard-read','clipboard-write','clipboard-sanitized-write']);
page.on('console', m => { if (['error','warning'].includes(m.type())) errors.push(`${m.type()}: ${m.text()}`); });
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('requestfailed', r => errors.push('requestfailed: ' + r.url() + ' ' + r.failure()?.errorText));
await page.setViewport({ width: 1440, height: 900 });
await page.goto(URL, { waitUntil: 'networkidle0' });
await page.waitForSelector('.sheet');

// hero + global
const hero = await page.evaluate(() => ({ h1: document.querySelector('#hero-title').textContent.trim(), lead: document.querySelector('.hero .lead').textContent.trim(),
  toastHidden: document.querySelector('#toast').hidden && getComputedStyle(document.querySelector('#toast')).display === 'none',
  proof: document.querySelector('#proof').textContent.replace(/\s+/g, ' ').trim(), tags: !!document.querySelector('.hero-tags'),
  banner: getComputedStyle(document.querySelector('#alert-bar')).display !== 'none' && document.querySelector('#alert-bar').textContent.includes('1930') }));
ok('hero headline + subhead', hero.h1 === 'Cybersecurity in plain English and Hinglish.' && hero.lead === 'Free roadmap, cheat sheets and scam alerts, made for India.', hero.h1);
ok('toast hidden on load', hero.toastHidden);
ok('proof line computed from data (no hashtags)', /^110 commands & refs · 9 sheets · 4 tools · free forever$/.test(hero.proof) && !hero.tags, hero.proof);
ok('1930 banner visible', hero.banner);
await sleep(1600);
const who = await page.evaluate(() => ({ w: document.querySelector('#who-out').textContent, h: getComputedStyle(document.querySelector('#hero-title')).opacity }));
ok('whoami types out, headline fades in', who.w === 'madhav@cyberwithmadhav' && who.h === '1', JSON.stringify(who));
await sleep(2200);
const term = await page.$eval('#term-out', e => e.textContent);
ok('terminal nmap demo typed with target var', term.includes('$ nmap -sV 192.168.1.10') && term.includes('3306/tcp open'), term.split('\n')[0]);
await page.click('#tt-quiz');
ok('quiz tab shows a message', await page.$eval('#tp-quiz', p => !p.hidden) && (await page.$eval('#quiz-msg', e => e.textContent)).length > 20);
await page.click('[data-answer="scam"]');
const q1 = await page.evaluate(() => ({ why: document.querySelector('#quiz-why').textContent, next: !document.querySelector('#quiz-next').hidden, n: document.querySelector('#quiz-n').textContent }));
ok('quiz answer → explanation + score', q1.why.length > 20 && q1.next && /score 1\/1|score 0\/1/.test(q1.n), q1.n);
await page.click('#quiz-next'); await page.click('#tt-nmap');
const contrast = await page.evaluate(() => {
  const rgb = (c) => c.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number);
  const L = (c) => { const v = rgb(c).map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
  const cr = (a, b) => { const [x, y] = [L(a), L(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const muted = getComputedStyle(document.querySelector('.lead')).color;
  return Math.min(cr(muted, 'rgb(13,11,20)'), cr(muted, 'rgb(22,18,31)'));
});
ok('muted text contrast >= 7:1 on bg and surface', contrast >= 7, contrast.toFixed(2));
const roles = await page.evaluate(() => ({ kicker: getComputedStyle(document.querySelector('.kicker')).color, chip: getComputedStyle(document.querySelector('.chip[aria-pressed="true"]')).borderColor, code: getComputedStyle(document.querySelector('.cmd code')).color }));
ok('colour roles: kicker neutral, chip purple, code green', roles.kicker === 'rgb(189, 182, 207)' && roles.chip === 'rgb(139, 92, 246)' && roles.code === 'rgb(74, 222, 128)', JSON.stringify(roles));

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
ok('subnet rejects bad octet', /0 to 255/.test(sc.err1)); ok('subnet rejects /33', /prefix/i.test(sc.err2));
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
await page.$eval('#cs-search', el => { el.value = 'nmap'; el.dispatchEvent(new Event('input')); }); await sleep(300);
ok('search lifts the 8-row cap', !(await page.$('.more')) && (await page.$$eval('.sheet[data-id="nmap"] .cmd', r => r.length)) === 13);
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

// cap + show all
const cap = await page.evaluate(() => ({ rows: document.querySelectorAll('.sheet[data-id="linux"] .cmd').length, btn: document.querySelector('.more[data-sheet="linux"]')?.textContent }));
ok('sheets capped at 8 rows with "Show all N →"', cap.rows === 8 && cap.btn === 'Show all 16 →', JSON.stringify(cap));
await page.click('.more[data-sheet="linux"]');
ok('"Show all" expands the sheet', (await page.$$eval('.sheet[data-id="linux"] .cmd', r => r.length)) === 16 && (await page.$eval('.more[data-sheet="linux"]', b => b.textContent)) === 'Show fewer ↑');
await page.click('.more[data-sheet="linux"]');

// copy
await page.click('.sheet[data-id="linux"] .copy');
await sleep(200);
const clip = await page.evaluate(() => navigator.clipboard.readText().catch(e => 'ERR ' + e.message));
const copiedTxt = await page.$eval('.sheet[data-id="linux"] .copy', b => b.textContent);
ok('copy button copies command, shows "copied ✓" in place', clip === 'pwd && ls -la' && copiedTxt === 'copied ✓', JSON.stringify([clip, copiedTxt]));
ok('toast stays hidden on successful copy', await page.$eval('#toast', t => t.hidden));
await page.evaluate(() => navigator.clipboard.writeText('x'));
await page.click('.sheet[data-id="linux"] .cmd:nth-of-type(2) .what');
await sleep(200);
const rowClip = await page.evaluate(() => navigator.clipboard.readText());
const row2 = await page.$eval('.sheet[data-id="linux"] .cmd:nth-of-type(2)', r => r.dataset.tpl);
ok('clicking anywhere on the row copies', rowClip === row2 && rowClip.length > 1, rowClip);

// flag glossary
const flagN = await page.$$eval('.sheet[data-id="nmap"] .flag', f => f.length);
await page.hover('.sheet[data-id="nmap"] .flag');
const tipVis = await page.$eval('.sheet[data-id="nmap"] .flag .tip', t => getComputedStyle(t).visibility);
await page.evaluate(() => navigator.clipboard.writeText('x'));
await page.click('.sheet[data-id="nmap"] .flag');
const flagExp = await page.$eval('.sheet[data-id="nmap"] .flag', f => f.getAttribute('aria-expanded'));
const afterFlag = await page.evaluate(() => navigator.clipboard.readText());
ok('flag tips on hover + tap (tap does not copy)', flagN > 5 && tipVis === 'visible' && flagExp === 'true' && afterFlag === 'x', JSON.stringify({ flagN, tipVis, flagExp, afterFlag }));
await page.mouse.click(5, 300);

// variables
await page.click('#vars-toggle');
ok('"Your values" panel opens with 4 fields', await page.$eval('#vars-panel', p => !p.hidden) && (await page.$$eval('#vars-fields input', i => i.length)) === 4);
await page.$eval('#vars-fields input[data-var="TARGET_IP"]', el => el.value = '');
await page.type('#vars-fields input[data-var="TARGET_IP"]', '10.10.11.5');
await sleep(400);
const varTxt = await page.$eval('.sheet[data-id="nmap"]', s => { const c = s.cloneNode(true); c.querySelectorAll('.tip').forEach(t => t.remove()); return c.textContent; });
const stored = await page.evaluate(() => localStorage.getItem('cwm-vars'));
ok('variables substitute into commands and persist to localStorage', varTxt.includes('nmap -sV 10.10.11.5') && !varTxt.includes('{{') && JSON.parse(stored).TARGET_IP === '10.10.11.5', stored);
const nmapRow = await page.$$eval('.sheet[data-id="nmap"] .cmd', rs => rs.findIndex(r => r.dataset.tpl === 'nmap -sV {{TARGET_IP}}'));
await page.click(`.sheet[data-id="nmap"] .cmd:nth-of-type(${nmapRow + 1}) .copy`); await sleep(200);
ok('copy uses your value', (await page.evaluate(() => navigator.clipboard.readText())) === 'nmap -sV 10.10.11.5');
ok('terminal demo follows your target IP', (await page.$eval('#term-out', e => e.textContent)).includes('nmap -sV 10.10.11.5'));
await page.reload({ waitUntil: 'networkidle0' }); await page.waitForSelector('.sheet');
ok('variables survive reload', (await page.$eval('.sheet[data-id="nmap"]', s => s.textContent)).includes('10.10.11.5'));
await page.click('#vars-toggle'); await page.click('#vars-reset'); await sleep(300);
ok('reset restores defaults', (await page.evaluate(() => localStorage.getItem('cwm-vars'))) === null && (await page.$eval('.sheet[data-id="nmap"]', s => s.textContent)).includes('192.168.1.10'));
await page.click('#vars-toggle');

// sticky controls + "/" + palette
await page.evaluate(() => { document.documentElement.style.scrollBehavior = 'auto'; document.querySelector('#sheet-windows').scrollIntoView(); window.scrollBy(0, 200); });
await sleep(200);
const sticky = await page.$eval('#cs-controls', e => ({ pos: getComputedStyle(e).position, top: Math.round(e.getBoundingClientRect().top) }));
ok('filter bar is sticky under the nav', sticky.pos === 'sticky' && sticky.top >= 55 && sticky.top <= 65, JSON.stringify(sticky));
await page.evaluate(() => window.scrollTo(0, 0)); await page.click('body', { offset: { x: 5, y: 500 } }).catch(() => {});
await page.keyboard.press('/');
ok('"/" focuses cheat-sheet search', await page.evaluate(() => document.activeElement.id) === 'cs-search');
await page.keyboard.type('/'); // typing "/" inside the field must not be swallowed
ok('"/" still types inside inputs', (await page.$eval('#cs-search', e => e.value)) === '/');
await page.$eval('#cs-search', el => { el.value = ''; el.dispatchEvent(new Event('input')); el.blur(); }); await sleep(200);
await page.keyboard.down('Control'); await page.keyboard.press('k'); await page.keyboard.up('Control');
ok('Ctrl+K opens command palette', await page.$eval('#palette', d => d.open) && await page.evaluate(() => document.activeElement.id) === 'pal-input');
await page.keyboard.type('hash');
const palFirst = await page.$eval('#pal-list [aria-selected="true"] .l', e => e.textContent);
await page.keyboard.press('Enter'); await sleep(700);
ok('palette search → jumps to tool', palFirst === 'Hash identifier' && !(await page.$eval('#palette', d => d.open)) && await page.evaluate(() => document.activeElement.id) === 'hash-input', palFirst);
await page.keyboard.down('Control'); await page.keyboard.press('k'); await page.keyboard.up('Control');
await page.keyboard.type('tcpdump'); await page.keyboard.press('Enter'); await sleep(600);
ok('palette command → filters cheat sheets to it', (await page.$eval('#cs-search', e => e.value)).startsWith('sudo tcpdump') && (await page.$$eval('#cs-list .cmd', r => r.length)) >= 1);
await page.keyboard.down('Control'); await page.keyboard.press('k'); await page.keyboard.up('Control'); await page.keyboard.press('Escape');
ok('Esc closes palette', !(await page.$eval('#palette', d => d.open)));
await page.$eval('#cs-search', el => { el.value = ''; el.dispatchEvent(new Event('input')); }); await sleep(200);

// tools
const pw = await page.evaluate(() => ({ a: cwmPassword('123456'), b: cwmPassword('password'), c: cwmPassword('asdfgh@1998'), d: cwmPassword('Correct-Horse-Battery-Staple-91'), e: cwmPassword('') }));
ok('password: common → very weak', pw.a.score === 0 && pw.b.score === 0 && pw.a.warnings.some(w => /common/.test(w)), JSON.stringify([pw.a.bits, pw.b.bits]));
ok('password: keyboard+year flagged', pw.c.score <= 1 && pw.c.warnings.some(w => /Keyboard/.test(w)) && pw.c.warnings.some(w => /Years/.test(w)), JSON.stringify(pw.c));
ok('password: long passphrase strong', pw.d.score >= 3 && pw.e === null, String(pw.d.bits));
await page.type('#pw-input', 'Tr0ub4dor&3');
const pwUi = await page.evaluate(() => ({ out: document.querySelector('#pw-out').textContent, type: document.querySelector('#pw-input').type, ls: JSON.stringify(localStorage), ss: JSON.stringify(sessionStorage) }));
ok('password UI: shows estimate, masked, nothing stored', /bits of entropy/.test(pwUi.out) && pwUi.type === 'password' && !pwUi.ls.includes('Tr0ub') && !pwUi.ss.includes('Tr0ub'));
await page.click('#pw-show'); ok('password show/hide toggle', await page.$eval('#pw-input', i => i.type) === 'text'); await page.click('#pw-show');
const hs = await page.evaluate(() => {
  const f = (h) => (cwmHashId(h)?.candidates[0] || {}).name;
  return { bcrypt: f('$2b$12$KIXQJ3jNv0zjG9i3pZ0b0eQ0X0n0hQ8lCwWzv6vEcU3oXy2Kk3mJW'), sha512c: f('$6$rounds=5000$salt$abc'), md5: cwmHashId('5f4dcc3b5aa765d61d8327deb882cf99').candidates.map(c => c.name),
    sha1: f('5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8'), sha256: f('5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'), jwt: f('eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.abc'), yes: f('$y$j9T$abc$def'), none: cwmHashId('hello world').candidates.length };
});
ok('hash identifier: bcrypt/$6$/MD5+NTLM/SHA1/SHA256/JWT/yescrypt', hs.bcrypt === 'bcrypt' && hs.sha512c === 'SHA-512 crypt' && hs.md5.includes('MD5') && hs.md5.includes('NTLM') && hs.sha1 === 'SHA-1' && hs.sha256 === 'SHA-256' && /JWT/.test(hs.jwt) && hs.yes === 'yescrypt' && hs.none === 0, JSON.stringify(hs));
await page.type('#hash-input', '5f4dcc3b5aa765d61d8327deb882cf99');
ok('hash UI shows hashcat mode', (await page.$eval('#hash-out', e => e.textContent)).includes('hashcat -m 0'));
const lk = await page.evaluate(() => {
  const v = (u) => cwmLinkCheck(u); const has = (u, re) => v(u).findings.some(f => re.test(f.text));
  return { clean: v('https://www.sbi.co.in/web/personal-banking').verdict, kyc: v('http://sbi-kyc-update.top/verify').verdict, http: has('http://example.com', /HTTPS/),
    puny: has('https://xn--pple-43d.com', /punycode/), ip: has('http://192.168.1.1/login', /IP address/), dec: has('http://3232235777/', /Disguised/), at: has('https://www.google.com@evil.example/', /@/),
    short: has('https://bit.ly/3abc', /shortener/i), subs: has('https://login.secure.account.verify.example.com', /subdomain/), tld: has('https://example.xyz', /\.xyz/), gov: has('https://incometax-gov-refund.in', /government/), apk: has('https://x.example/app.apk', /apk/), bad: v('not a url ::').error ? 'err' : v('not a url ::').verdict };
});
ok('link analyzer: official bank clean, scam risky', lk.clean === 'clean' && lk.kyc === 'risky', JSON.stringify([lk.clean, lk.kyc]));
ok('link analyzer: http/punycode/IP/decimal IP/@/shortener/subdomains/TLD/gov/apk', lk.http && lk.puny && lk.ip && lk.dec && lk.at && lk.short && lk.subs && lk.tld && lk.gov && lk.apk, JSON.stringify(lk));
await page.type('#link-input', 'http://sbi-kyc-update.top/verify'); await sleep(300);
ok('link UI verdict', (await page.$eval('#link-out .verdict', e => e.className)).includes('bad'));
const boxes = await page.$$('#link-checklist input');
for (const b of boxes.slice(0, 3)) await b.click();
ok('checklist: 3 ticks → treat as scam', boxes.length === 8 && (await page.$eval('#checklist-out', e => e.textContent)).includes('Treat it as a scam'));
ok('tools labelled educational + client-side', /Educational/.test(await page.$eval('#tools-note', e => e.textContent)));

// roadmap tabs
await page.click('#tab-advanced');
ok('roadmap tab switch', await page.$eval('#panel-advanced', p => !p.hidden) && await page.$eval('#panel-beginner', p => p.hidden));
await page.click('#tab-beginner');

// counts
const counts = await page.evaluate(() => ({ jobs: document.querySelectorAll('.job').length, scams: document.querySelectorAll('.scam').length, net: document.querySelectorAll('.net-card').length, tl: document.querySelectorAll('#timeline li').length, proj: document.querySelectorAll('.project').length }));
ok('jobs=7, scams>=5, net cards, timeline, projects', counts.jobs===7 && counts.scams>=5 && counts.net>=10 && counts.tl===7 && counts.proj===2, JSON.stringify(counts));

// about
await page.evaluate(() => document.querySelector('#projects').scrollIntoView()); await sleep(800);
const ab = await page.evaluate(() => ({ h2: document.querySelector('#about-title').textContent, law: document.querySelector('#law').textContent, links: [...document.querySelectorAll('#about-links a')].map(a => a.textContent),
  building: document.querySelectorAll('.project .building').length, stars: [...document.querySelectorAll('.project .stars')].map(s => s.hidden ? '-' : s.textContent) }));
ok('about headline', ab.h2 === 'Madhav Pandya: cybersecurity educator studying BCA and law, explaining cybersecurity in Hinglish.');
ok('law callout: IT Act, DPDP 2023, GRC', /IT Act/.test(ab.law) && /DPDP\)? Act,? 2023/.test(ab.law) && /GRC/.test(ab.law), ab.law.slice(0, 80));
ok('Instagram/YouTube hidden until URL set', !ab.links.some(t => /Instagram|YouTube/.test(t)) && ab.links.some(t => /GitHub/.test(t)), ab.links.join(','));
ok('projects: building notes + stars only when > 0', ab.building === 2 && ab.stars[0] === '★ 3' && ab.stars[1] === '-', JSON.stringify(ab.stars));

// contact form composes a mailto: link (no backend on GitHub Pages); no newsletter form
ok('no newsletter form', !(await page.$('#newsletter-form')));
await page.click('#contact-form button[type=submit]');
ok('contact form client validation', (await page.$eval('#contact-form .form-status', e => e.className + ' ' + e.textContent)).includes('err'));
await page.type('#c-name', 'Test User'); await page.type('#c-subject', 'Hi'); await page.type('#c-msg', 'Hello from the headless test!');
await page.click('#contact-form button[type=submit]');
{ const m = await page.$eval('#contact-form', f => f.dataset.mailto || '');
  ok('contact form → mailto with subject and body', m.startsWith('mailto:madhavpandya@zoho.in?subject=Hi&body=') && m.includes('Test%20User'), m.slice(0, 80)); }
ok('follow card: Instagram and YouTube coming soon, no fake URLs', await page.$$eval('#follow-links li', li => li.length === 2 && li.every(x => /coming soon/.test(x.textContent) && !x.querySelector('a'))));
ok('initials avatar, no TODO', await page.evaluate(() => !!document.querySelector('.photo.avatar .av-initials') && !/TODO/.test(document.body.innerHTML)));
await page.$$eval('.form-status', s => s.forEach(x => { x.textContent=''; x.className='form-status small'; }));

// theme toggle
await page.click('.theme-toggle'); await sleep(800);
ok('theme toggle → light', await page.evaluate(() => document.documentElement.dataset.theme) === 'light');
const lightC = await page.evaluate(() => {
  const rgb = (c) => c.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number);
  const L = (c) => { const v = rgb(c).map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
  const cr = (a, b) => { const [x, y] = [L(a), L(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const bg = getComputedStyle(document.documentElement).backgroundColor;
  const pick = s => getComputedStyle(document.querySelector(s)).color;
  return Object.fromEntries(['.lead', '.kicker', '.cmd code', '.tag', '#nav-links a', '.job .sum', '.more', '#vars-reset'].map(s => [s, +cr(pick(s), bg).toFixed(2)]));
});
ok('v3 light theme: text passes WCAG AA (>= 4.5:1)', Object.values(lightC).every(v => v >= 4.5), JSON.stringify(lightC));
ok('v3 theme saved to localStorage', await page.evaluate(() => localStorage.getItem('cwm-theme')) === 'light');
await page.reload({ waitUntil: 'networkidle0' }); await page.waitForSelector('.sheet');
ok('v3 saved theme survives reload (no flash: set before CSS paints)', await page.evaluate(() => document.documentElement.dataset.theme) === 'light');
await page.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')));
await sleep(600); await page.evaluate(() => { document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0, 0); }); await sleep(900);
await page.evaluate(() => window.scrollTo(0, 0)); await sleep(400);
await page.screenshot({ path: `${OUT}/v3-light.png` });
await page.click('.theme-toggle'); await sleep(800);
ok('theme toggle → back to dark', await page.evaluate(() => document.documentElement.dataset.theme) === 'dark');
// v3 space + glass checks
const v3 = await page.evaluate(() => ({ canvas: !!document.querySelector('#starfield') && document.querySelector('#starfield').width > 0,
  glass: getComputedStyle(document.querySelector('.card')).backdropFilter, navGlass: getComputedStyle(document.querySelector('.nav')).backdropFilter,
  marker: document.querySelector('meta[name="cwm-version"]').content }));
ok('v3 starfield canvas + frosted glass cards/nav', v3.canvas && /blur/.test(v3.glass) && /blur/.test(v3.navGlass) && v3.marker === '3', JSON.stringify(v3));
await page.evaluate(() => { window.scrollTo(0, 3000); }); await sleep(500);
ok('v3 back-to-top appears after scrolling + glass nav state', await page.evaluate(() => !document.querySelector('#to-top').hidden && document.querySelector('.nav').classList.contains('scrolled')));
await page.click('#to-top'); await sleep(1500);
ok('v3 back-to-top returns to top', await page.evaluate(() => window.scrollY) < 5);
await page.click('#nav-links a[href="#careers"]'); await sleep(1500);
const warp = await page.evaluate(() => ({ y: document.querySelector('#careers').getBoundingClientRect().top, hash: location.hash, active: document.querySelector('#nav-links a.active')?.getAttribute('href') }));
ok('v3 nav warp jump lands on section, updates hash + active link', Math.abs(warp.y) < 90 && warp.hash === '#careers' && warp.active === '#careers', JSON.stringify(warp));
await page.evaluate(() => { history.replaceState(null, '', location.pathname); window.scrollTo(0, 0); });

// meta
const meta = await page.evaluate(() => ({ og: !!document.querySelector('meta[property="og:title"]'), desc: !!document.querySelector('meta[name="description"]'), h1: document.querySelectorAll('h1').length, icon: document.querySelector('link[rel=icon]').href, lang: document.documentElement.lang }));
ok('SEO/OG meta, single h1, favicon, lang', meta.og && meta.desc && meta.h1 === 1 && meta.lang === 'en', JSON.stringify(meta));

ok('password: leetspeak of a common password caught', (await page.evaluate(() => cwmPassword('P@ssw0rd!').score)) <= 1);
// screenshots: hide stubbed star counts so docs never show fake numbers
await page.evaluate(() => document.querySelectorAll('.project .stars').forEach(s => s.hidden = true));
// screenshots: reveal everything first
await page.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')));
await page.evaluate(() => { document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0, 0); }); await new Promise(r => setTimeout(r, 700));
await page.screenshot({ path: `${OUT}/desktop.png`, fullPage: true });
await page.screenshot({ path: `${OUT}/v3-dark.png` });
async function crop(sel, file, maxH = 1400) {
  const el = await page.$(sel); const b = await el.boundingBox();
  const y = b.y + (await page.evaluate(() => window.scrollY));
  await page.screenshot({ path: `${OUT}/${file}`, clip: { x: 0, y, width: 1440, height: Math.min(b.height, maxH) }, captureBeyondViewport: true });
}
await crop('.hero', 'hero.png'); await crop('#cheatsheets', 'cheatsheets.png', 1500); await crop('#about', 'about.png', 1500);
await crop('#tools', 'tools.png', 1500);

const m = await browser.newPage();
await m.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'dark' }]);
await stubGitHub(m);
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
const chipsM = await m.$eval('#cs-filters', c => ({ wrap: getComputedStyle(c).flexWrap, ox: getComputedStyle(c).overflowX, scroll: c.scrollWidth > c.clientWidth }));
ok('mobile: filter chips scroll sideways', chipsM.wrap === 'nowrap' && chipsM.ox === 'auto' && chipsM.scroll, JSON.stringify(chipsM));
const cols = await m.evaluate(() => ['.cards', '.projects', '.tools-grid', '.cs-list'].map(s => getComputedStyle(document.querySelector(s)).gridTemplateColumns.split(' ').length));
ok('mobile: cards collapse to one column', cols.every(n => n === 1), cols.join(','));
ok('mobile: hero stacks (terminal below copy)', await m.evaluate(() => document.querySelector('#term').getBoundingClientRect().top > document.querySelector('.hero .cta').getBoundingClientRect().bottom));
await m.click('.nav-toggle'); ok('mobile menu opens', await m.$eval('#nav-links', n => n.classList.contains('open'))); await m.click('.nav-toggle');
await m.click('.alert-close');
ok('banner dismisses for this visit', await m.$eval('#alert-bar', b => getComputedStyle(b).display === 'none'));
await m.reload({ waitUntil: 'networkidle0' });
ok('banner stays hidden after reload in same session', await m.$eval('#alert-bar', b => getComputedStyle(b).display === 'none'));
const ms = await browser.newPage();
await ms.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'dark' }]);
await stubGitHub(ms);
await ms.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
await ms.goto(URL, { waitUntil: 'networkidle0' }); await ms.waitForSelector('.sheet');
await ms.evaluate(() => document.querySelectorAll('.reveal').forEach(e => e.classList.add('in')));
await new Promise(r => setTimeout(r, 800));
await ms.screenshot({ path: `${OUT}/mobile-hero.png` });
await ms.screenshot({ path: `${OUT}/mobile.png`, fullPage: true });
await ms.screenshot({ path: `${OUT}/v3-mobile.png` });
await ms.click('.nav-toggle'); await sleep(500);
await ms.screenshot({ path: `${OUT}/v3-mobile-menu.png` });
ok('v3 mobile: Esc closes menu', await (async () => { await ms.keyboard.press('Escape'); await sleep(300); return !(await ms.$eval('#nav-links', n => n.classList.contains('open'))); })());
ok('mobile: no console errors', mErr.length === 0, mErr.join(' | '));

// reduced motion
const rm = await browser.newPage();
await rm.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }, { name: 'prefers-color-scheme', value: 'dark' }]);
await stubGitHub(rm);
await rm.goto(URL, { waitUntil: 'networkidle0' }); await rm.waitForSelector('.sheet');
ok('reduced motion: content visible without animation', await rm.$eval('#jobs .job', e => getComputedStyle(e).opacity === '1'));
const rmS = await rm.evaluate(() => ({ who: document.querySelector('#who-out').textContent, h1: getComputedStyle(document.querySelector('#hero-title')).opacity, glow: getComputedStyle(document.querySelector('.hero'), '::before').display, term: document.querySelector('#term-out').textContent.includes('Nmap done') }));
ok('reduced motion: no typing (final text instantly), no glow', rmS.who === 'madhav@cyberwithmadhav' && rmS.h1 === '1' && rmS.glow === 'none' && rmS.term, JSON.stringify(rmS));

// print css
await page.emulateMediaType('print');
ok('print CSS hides nav/hero, keeps cheat sheets', await page.evaluate(() => getComputedStyle(document.querySelector('.nav')).display === 'none' && getComputedStyle(document.querySelector('.hero')).display === 'none' && getComputedStyle(document.querySelector('#cheatsheets')).display !== 'none'));
const pr = await page.evaluate(() => ({ bg: getComputedStyle(document.body).backgroundColor, card: getComputedStyle(document.querySelector('.sheet')).backgroundColor, code: getComputedStyle(document.querySelector('.cmd code')).color }));
ok('print uses light background + dark text', pr.bg === 'rgb(255, 255, 255)' && pr.card === 'rgb(255, 255, 255)' && pr.code === 'rgb(0, 0, 0)', JSON.stringify(pr));
await page.pdf({ path: '/tmp/cwm-cheatsheets-print.pdf', format: 'A4' });
await page.emulateMediaType('screen');

ok('desktop: no console errors/warnings/failed requests', errors.length === 0, errors.join(' | '));
console.log(results.join('\n'));
await browser.close();

// CTF page checks (needs the answer key in backend/ctf_answers.private.json; set SKIP_CTF=1 to skip)
if (!process.env.SKIP_CTF) await import('./test_ctf.mjs');
// prompts.html + cyberlaw.html checks and screenshots (set SKIP_PAGES=1 to skip)
if (!process.env.SKIP_PAGES) await import('./test_pages.mjs');
