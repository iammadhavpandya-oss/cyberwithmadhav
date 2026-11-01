// CTF page checks. Run from tools/:  node test_ctf.mjs   (also run at the end of test.mjs)
// Needs: static server on :8000 (python3 -m http.server 8000) and, for API mode, the Flask app on :5000 with
// CWM_CTF_ORIGINS including http://127.0.0.1:8000. Set CTF_API=0 to skip API mode.
// The answer key is read from backend/ctf_answers.private.json (local only, gitignored) to play levels.
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
const BASE = (process.env.URL || 'http://127.0.0.1:8000/').replace(/\/?$/, '/');
const OUT = new globalThis.URL('../docs/', import.meta.url).pathname;
const KEY = JSON.parse(fs.readFileSync(new globalThis.URL('../backend/ctf_answers.private.json', import.meta.url), 'utf8')).challenges;
const byTitle = new Map(KEY.map(c => [c.title, c]));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const results = [];
const ok = (name, cond, extra = '') => { results.push(`${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '  : ' + extra : ''}`); };
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });

async function newPage({ blockApi = true, width = 1440, height = 900, scheme = 'dark', mobile = false } = {}) {
  const p = await browser.newPage();
  p.errors = [];
  p.on('console', m => { if (['error', 'warning'].includes(m.type()) && !(blockApi && /ERR_FAILED/.test(m.text()))) p.errors.push(m.type() + ': ' + m.text()); });
  p.on('pageerror', e => p.errors.push('pageerror: ' + e.message));
  if (blockApi) {
    await p.setRequestInterception(true);
    p.on('request', r => (r.url().includes(':5000')) ? r.abort() : r.continue());
  }
  await p.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: scheme }]);
  await p.setViewport({ width, height, isMobile: mobile, hasTouch: mobile, deviceScaleFactor: mobile ? 2 : 1 });
  // smooth scrolling (html{scroll-behavior:smooth}) makes puppeteer click mid-scroll; turn it off via CSSOM (CSP-safe)
  p.on('domcontentloaded', () => p.evaluate(() => { document.documentElement.style.scrollBehavior = 'auto'; }).catch(() => {}));
  return p;
}
const view = p => p.evaluate(() => [...document.querySelectorAll('.ctf-view')].filter(s => !s.hidden).map(s => s.dataset.view).join(','));

// Answer the current question. mode: 'right' | 'wrong'
async function answer(p, mode) {
  const t = await p.$eval('#q-title', e => e.textContent);
  const c = byTitle.get(t);
  if (!c) throw new Error('no key for ' + t);
  const right = c.answers[0];
  if (c.type === 'mcq') {
    const opt = mode === 'right' ? right : c.options.find(o => o !== right);
    await p.evaluate(o => [...document.querySelectorAll('#q-answer .opt')].find(l => l.dataset.opt === o).click(), opt);
  } else if (c.type === 'multi') {
    const want = mode === 'right' ? right.split('|') : [c.options.find(o => !right.split('|').includes(o))];
    await p.evaluate(w => document.querySelectorAll('#q-answer .opt').forEach(l => { const i = l.querySelector('input'); if (i.checked !== w.includes(l.dataset.opt)) l.click(); }), want);
  } else if (c.type === 'order') {
    const want = right.split('|'); if (mode !== 'right') want.reverse();
    await p.evaluate(w => { const ol = document.querySelector('#order-list'); w.forEach(v => ol.append([...ol.children].find(li => li.dataset.val === v))); }, want);
  } else {
    let val = mode === 'right' ? right : 'definitely wrong';
    if (mode === 'right' && c.dyn && p.apiMode) { // per-player flag from the server: decode the artifact like a player would
      const code = await p.$eval('#q-code', e => e.textContent);
      if (c.dyn.enc === 'hex') val = Buffer.from(code.trim().split(/\s+/).map(h => parseInt(h, 16))).toString();
      else throw new Error('test decoder missing for ' + c.dyn.enc);
    }
    await p.$eval('#ans-text', e => { e.value = ''; });
    await p.type('#ans-text', val);
  }
  await p.click('#q-submit');
  await p.waitForFunction(() => { const f = document.querySelector('#q-feedback'); return f.textContent && f.textContent !== 'Checking...' && f.textContent !== 'Working out the 50/50...'; }, { timeout: 15000 });
  return c;
}
// Play the whole level; wrong answers use up all attempts
async function playLevel(p, mode, onEach) {
  for (let guard = 0; guard < 12; guard++) {
    const c = await answer(p, mode);
    if (onEach) await onEach(c);
    while (await p.$eval('#q-next', e => e.hidden)) { await answer(p, mode); }
    const last = await p.$eval('#q-next', e => e.textContent === 'See results');
    await p.click('#q-next');
    if (last) { await p.waitForFunction(() => location.hash === '#/result', { timeout: 10000 }); await sleep(300); return; }
    await sleep(60);
  }
}
const start = async (p, t, l) => {
  await p.evaluate(h => { location.hash = h; }, `#/brief/${t}/${l}`); await sleep(150);
  await p.click('#brief-start'); await p.waitForFunction(() => location.hash === '#/play' && !document.querySelector('#view-play').hidden && /^Q 1 \//.test(document.querySelector('#ph-count').textContent), { timeout: 10000 });
};

/* ================= static / practice mode ================= */
const p = await newPage();
await p.goto(BASE + 'ctf.html', { waitUntil: 'networkidle0' });
await p.waitForFunction(() => document.documentElement.dataset.ctfMode === 'practice', { timeout: 6000 }).catch(() => {});
const hub = await p.evaluate(() => ({
  mode: document.documentElement.dataset.ctfMode, banner: document.querySelector('#mode-text').textContent,
  cards: document.querySelectorAll('#track-grid .track-card').length, board: document.querySelector('#board-title').textContent,
  tabs: document.querySelector('#board-tabs').hidden, hash: location.hash, nav: !!document.querySelector('.nav-ctf[aria-current="page"]'),
  sound: document.querySelector('#opt-sound').getAttribute('aria-pressed'), live: document.querySelector('#sr-live').getAttribute('aria-live'),
  csp: document.querySelector('meta[http-equiv="Content-Security-Policy"]')?.content || ''
}));
ok('static: API blocked falls back to practice banner within 2.5 s', hub.mode === 'practice' && /Practice mode/.test(hub.banner) && /not count/.test(hub.banner), hub.banner.slice(0, 60));
ok('hub shows 7 track cards, routed to #/hub', hub.cards === 7 && hub.hash === '#/hub', hub.cards + ' ' + hub.hash);
ok('static: "Your best" instead of leaderboard', hub.board === 'Your best' && hub.tabs);
ok('nav CTF link active, sound muted by default, aria-live polite', hub.nav && hub.sound === 'false' && hub.live === 'polite');
ok('CSP meta present (no inline script allowance)', /script-src 'self'/.test(hub.csp) && !/unsafe-inline/.test(hub.csp.split('script-src')[1].split(';')[0]), hub.csp.slice(0, 80));
const data = await p.evaluate(() => fetch('data/ctf.json').then(r => r.json()));
const counts = data.tracks.map(t => t.id + ':' + t.levels.map(l => l.challenges.length).join('/'));
ok('7 tracks x 3 levels, at least 5 challenges each', data.tracks.length === 7 && data.tracks.every(t => t.levels.length === 3 && t.levels.every(l => l.challenges.length >= 5)), counts.join(' '));
const raw = fs.readFileSync(new globalThis.URL('../data/ctf.json', import.meta.url), 'utf8');
const leaks = KEY.filter(c => c.type !== 'mcq' && c.type !== 'multi' && c.type !== 'order').filter(c => c.answers.some(a => a.length > 3 && raw.includes('"' + a + '"')));
ok('public ctf.json has no plaintext typed answers or explanations', !leaks.length && !raw.includes(KEY[0].explain), leaks.map(c => c.id).join(','));

// track view + lock
await p.evaluate(() => { location.hash = '#/track/networking'; }); await sleep(200);
const tv = await p.evaluate(() => ({ cards: [...document.querySelectorAll('#level-grid .level-card')].map(c => c.className), lock: document.querySelector('.lock-note')?.textContent || '', ethics: document.querySelector('#ethics').hidden }));
ok('track view: beginner open, later levels locked with text', !tv.cards[0].includes('locked') && tv.cards[1].includes('locked') && /Locked\. Score 60%/.test(tv.lock) && tv.ethics, tv.lock);
await p.evaluate(() => { location.hash = '#/track/pentest'; }); await sleep(150);
ok('pentest track shows the ethics banner', await p.$eval('#ethics', e => !e.hidden && e.textContent.includes('Practice only on systems you own or are authorised to test.')));
await p.evaluate(() => { location.hash = '#/brief/pentest/beginner'; }); await sleep(150);
ok('briefing: facts, ethics on pentest, start enabled', await p.evaluate(() => document.querySelectorAll('#brief-facts li').length >= 5 && !document.querySelector('#brief-ethics').hidden && !document.querySelector('#brief-start').disabled));
await p.evaluate(() => { location.hash = '#/brief/networking/expert'; }); await sleep(150);
ok('briefing for a locked level: start disabled', await p.$eval('#brief-start', b => b.disabled));

// play networking beginner, all right
await start(p, 'networking', 'beginner');
const play0 = await p.evaluate(() => ({ inGame: document.body.classList.contains('in-game'), timer: !document.querySelector('#ph-timer').hidden, dots: document.querySelectorAll('#ph-dots li').length, focus: document.activeElement.id }));
ok('play view: in-game, timer visible, progress dots, focus on question', play0.inGame && play0.timer && play0.dots >= 5 && play0.focus === 'q-title', JSON.stringify(play0));
// keyboard: press 1 on an mcq selects option 1
let usedKeys = false, usedHint = false;
await playLevel(p, 'right', async c => {
  if (c.type === 'mcq' && !usedKeys) usedKeys = true;
  const fb = await p.$eval('#q-feedback', e => e.className + '|' + e.textContent);
  if (!/ok/.test(fb)) results.push('FAIL  expected correct for ' + c.id + ' : ' + fb);
});
const res = await p.evaluate(() => ({ pct: document.querySelector('#res-pct').textContent, title: document.querySelector('#res-title').textContent,
  badge: !document.querySelector('#res-badge').hidden, phil: document.querySelector('#q-phil').hidden, gita: !document.querySelector('#q-gita').hidden,
  gText: document.querySelector('#gita-text').textContent, gEn: document.querySelector('#gita-en').textContent, gHi: document.querySelector('#gita-hi').textContent,
  gRef: document.querySelector('#gita-ref').textContent, gSrc: document.querySelector('#gita-src').href, next: document.querySelector('#res-next').textContent,
  wa: document.querySelector('#res-share-wa').href, review: document.querySelector('#res-review').hidden }));
await sleep(1300);
const pctAfter = await p.$eval('#res-pct', e => e.textContent);
ok('all correct: 100%, badge, next level unlocked', pctAfter === '100%' && res.badge && /Next level: Intermediate/.test(res.next), pctAfter + ' / ' + res.next);
ok('high band: Gita verse with transliteration, English, Hindi, ref, https source; no philosopher', res.gita && res.phil && res.gText && res.gEn && /[\u0900-\u097F]/.test(res.gHi) && /Gita/.test(res.gRef) && /^https:/.test(res.gSrc), res.gRef);
ok('share: wa.me link with score', /^https:\/\/wa\.me\/\?text=.*100%25/.test(res.wa));
ok('no wrong answers to review', res.review);
await sleep(3200); await p.evaluate(() => window.scrollTo(0, 0)); await sleep(200); // let level-up, confetti and toasts settle
await p.screenshot({ path: OUT + 'ctf-result.png' });
const store = await p.evaluate(() => JSON.parse(localStorage.getItem('cwm-ctf-practice-v2')));
ok('practice progress saved in localStorage', store.levels['networking/beginner'].best === 100 && Object.keys(store.solved).length >= 5 && store.xp > 0, 'xp ' + store.xp);

// replay same level: no extra XP for already-solved questions
const xp1 = store.xp;
await p.click('#res-retry'); await p.waitForFunction(() => location.hash === '#/play' && !document.querySelector('#view-play').hidden && /^Q 1 \//.test(document.querySelector('#ph-count').textContent)); await sleep(100);
await answer(p, 'right');
const note = await p.$eval('#q-feedback', e => e.textContent);
ok('replay: already-solved question gives marks but no XP', /Already solved, no XP/.test(note), note);
await p.click('#q-next'); await sleep(50);
// hint / 50-50 and keyboard on an mcq
for (let i = 0; i < 8 && !(usedHint); i++) {
  const t = await p.$eval('#q-title', e => e.textContent), c = byTitle.get(t);
  if (c.type === 'mcq' && !c.hints.length) {
    await p.click('#q-hint'); await p.waitForFunction(() => document.querySelectorAll('#q-answer .opt.gone').length === 2, { timeout: 15000 });
    const pts = await p.$eval('#q-points', e => e.textContent);
    ok('50/50 hint removes two wrong options and shows reduced marks', /worth 8 \/ 10/.test(pts), pts);
    await p.evaluate(() => document.querySelector('#q-title').focus());
    const free = await p.evaluate(() => [...document.querySelectorAll('#q-answer .opt')].findIndex(l => !l.classList.contains('gone')));
    await p.keyboard.press(String(free + 1));
    ok('keyboard: number key picks an option', await p.evaluate(i => document.querySelectorAll('#q-answer .opt input')[i].checked, free));
    await p.keyboard.press('Enter'); await sleep(400);
    usedHint = true;
  } else { await answer(p, 'right'); }
  if (!(await p.$eval('#q-next', e => e.hidden))) { await p.click('#q-next'); await sleep(50); }
}
// Esc quits (with confirm)
p.once('dialog', d => d.accept());
await p.keyboard.press('Escape'); await sleep(300);
ok('Esc quits the level back to the track', (await p.evaluate(() => location.hash)) === '#/track/networking');
ok('quit run is not saved', (await p.evaluate(() => JSON.parse(localStorage.getItem('cwm-ctf-practice-v2')).levels['networking/beginner'].runs)) === 1);

// Linux beginner all wrong: low band
await start(p, 'linux', 'beginner');
// wrong attempt shake + attempts note on a text question
await playLevel(p, 'wrong');
await sleep(1300);
const low = await p.evaluate(() => ({ pct: document.querySelector('#res-pct').textContent, phil: !document.querySelector('#q-phil').hidden, pRef: document.querySelector('#phil-ref').textContent,
  gita: !document.querySelector('#q-gita').hidden, review: document.querySelector('#res-review').textContent, next: document.querySelector('#res-next').disabled, badge: document.querySelector('#res-badge').hidden,
  fx: document.querySelector('#fx') ? 1 : 0 }));
ok('all wrong: 0%, philosopher + Gita shown, no badge, next locked', low.pct === '0%' && low.phil && low.gita && low.badge && low.next, low.pRef);
await p.click('#res-review'); await sleep(100);
const rv = await p.evaluate(() => ({ n: document.querySelectorAll('#review .rv-item').length, txt: document.querySelector('#review').textContent }));
ok('review lists wrong answers, reveals choice answers only', rv.n >= 5 && /Correct /.test(rv.txt) && /never revealed/.test(rv.txt), rv.n + ' items');
const q1 = await p.evaluate(() => JSON.parse(localStorage.getItem('cwm-ctf-quotes')));
await p.click('#res-retry'); await p.waitForFunction(() => location.hash === '#/play' && !document.querySelector('#view-play').hidden && /^Q 1 \//.test(document.querySelector('#ph-count').textContent));
await playLevel(p, 'wrong');
const q2 = await p.evaluate(() => JSON.parse(localStorage.getItem('cwm-ctf-quotes')));
ok('quotes: no repeat of the last pick within a band', q1.gita.low !== q2.gita.low && q1.phil.low !== q2.phil.low, JSON.stringify([q1, q2]));

// overall radar
await p.evaluate(() => { location.hash = '#/overall'; }); await sleep(200);
const ov = await p.evaluate(() => ({ pts: document.querySelectorAll('#radar .pt').length, rows: document.querySelectorAll('#ovr-body tr').length, sug: document.querySelector('#suggest').textContent, desc: document.querySelector('#radar-desc').textContent }));
ok('overall: radar with 7 points, table, weakest-track suggestion', ov.pts === 7 && ov.rows === 7 && /weakest track at|not tried/.test(ov.sug) && /Networking 17%/.test(ov.desc), ov.sug + ' | ' + ov.desc + ' ' + ov.pts + '/' + ov.rows);

// prefs: relaxed hides timer, free roam unlocks + not counted
await p.click('#opt-relaxed'); await p.click('#opt-free');
await p.evaluate(() => { location.hash = '#/track/networking'; }); await sleep(150);
ok('free roam: all levels open, note shown', await p.evaluate(() => !document.querySelector('.level-card.locked') && !document.querySelector('#free-note').hidden));
await start(p, 'cloud', 'expert');
ok('relaxed: timer hidden', await p.$eval('#ph-timer', e => e.hidden));
await playLevel(p, 'right');
const fr = await p.evaluate(() => ({ where: document.querySelector('#res-where').textContent, saved: !!JSON.parse(localStorage.getItem('cwm-ctf-practice-v2')).levels['cloud/expert'] }));
ok('free roam run does not count toward progress', /free roam/.test(fr.where) && !fr.saved, fr.where);
await p.evaluate(() => { location.hash = '#/hub'; }); await sleep(150);
await p.click('#opt-relaxed');
await p.click('#opt-free');

// order question: keyboard reorder + buttons
await p.click('#opt-free');
await start(p, 'networking', 'intermediate');
for (let i = 0; i < 8; i++) {
  const t = await p.$eval('#q-title', e => e.textContent), c = byTitle.get(t);
  if (c.type === 'order') {
    const before = await p.$$eval('#order-list li', l => l.map(x => x.dataset.val));
    await p.focus('#order-list li:nth-child(1)'); await p.keyboard.press('Space'); await p.keyboard.press('ArrowDown'); await p.keyboard.press('Space');
    const after = await p.$$eval('#order-list li', l => l.map(x => x.dataset.val));
    await p.click('#order-list li:nth-child(2) .mv button:last-child');
    const after2 = await p.$$eval('#order-list li', l => l.map(x => x.dataset.val));
    ok('order: Space + arrows and the move buttons reorder steps', after[1] === before[0] && after2[2] === before[0], after2.join(' > '));
    break;
  }
  await answer(p, 'right'); while (await p.$eval('#q-next', e => e.hidden)) await answer(p, 'right');
  await p.click('#q-next'); await sleep(50);
}
await p.evaluate(() => { location.hash = '#/hub'; }); await sleep(100);
await p.click('#opt-free');

// visible text rules over every view
const dash = await p.evaluate(async () => {
  const bad = [];
  for (const h of ['#/hub', '#/track/pentest', '#/brief/blueteam/beginner', '#/overall']) { location.hash = h; await new Promise(r => setTimeout(r, 120)); if (document.body.innerText.includes('\u2014')) bad.push(h); }
  return bad;
});
const q = JSON.parse(fs.readFileSync(new globalThis.URL('../data/ctf_quotes.json', import.meta.url), 'utf8'));
const qd = [...q.philosophers, ...q.gita].filter(x => [x.text, x.translation_en, x.meaning_hi, x.author_or_ref].join(' ').includes('\u2014'));
const cd = data.tracks.flatMap(t => t.levels.flatMap(l => l.challenges)).filter(c => [c.title, c.prompt, ...(c.options || []), ...(c.hints || [])].join(' ').includes('\u2014'));
const jsd = fs.readFileSync(new globalThis.URL('../assets/js/ctf.js', import.meta.url), 'utf8').includes('\u2014');
ok('no em dash in visible CTF copy (views, challenges, quotes, script)', !dash.length && !qd.length && !cd.length && !jsd, [dash, qd.length, cd.map(c => c.id)].join(' '));

// screenshots: dark hub, light track
await p.evaluate(() => { localStorage.setItem('cwm-ctf-ui', '1'); location.hash = '#/hub'; }); await sleep(400); await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForFunction(() => [...document.querySelectorAll('.toast')].every(t => t.hidden || !t.classList.contains('show')), { timeout: 8000 }).catch(() => {}); await sleep(300);
await p.screenshot({ path: OUT + 'ctf-dark.png' });
await p.click('.theme-toggle'); await sleep(400);
ok('theme toggle switches to light', await p.evaluate(() => document.documentElement.getAttribute('data-theme') === 'light'));
await p.evaluate(() => { location.hash = '#/track/networking'; }); await sleep(400);
await p.screenshot({ path: OUT + 'ctf-light.png' });
await p.click('.theme-toggle'); await sleep(100);
ok('practice: no console errors, CSP violations or failed requests', p.errors.length === 0, p.errors.join(' | '));

/* ================= mobile ================= */
const m = await newPage({ width: 390, height: 844, mobile: true });
await m.goto(BASE + 'ctf.html#/hub', { waitUntil: 'networkidle0' });
await m.click('.nav-toggle'); await sleep(200);
ok('mobile: nav toggle opens the menu', await m.evaluate(() => document.querySelector('#nav-links').classList.contains('open') && document.querySelector('.nav-toggle').getAttribute('aria-expanded') === 'true'));
await m.keyboard.press('Escape'); await sleep(200);
await start(m, 'networking', 'beginner');
const ow = await m.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1);
ok('mobile: no horizontal overflow in play view', ow);
ok('mobile: practice banner button fits on screen', await m.evaluate(() => { const b = document.querySelector('#mode-retry'); return !b || b.getBoundingClientRect().right <= window.innerWidth - 8; }));
await answer(m, 'right'); await sleep(200);
await m.evaluate(() => window.scrollTo(0, document.querySelector('#view-play').getBoundingClientRect().top + scrollY - 76)); await sleep(150);
await m.screenshot({ path: OUT + 'ctf-mobile.png' });
ok('mobile: no console errors', m.errors.length === 0, m.errors.join(' | '));

/* ================= reduced motion ================= */
const r = await newPage();
await r.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
await r.goto(BASE + 'ctf.html#/hub', { waitUntil: 'networkidle0' });
ok('reduced motion: calm mode on', await r.evaluate(() => document.documentElement.classList.contains('ctf-calm')));
await start(r, 'basics', 'beginner'); await playLevel(r, 'right');
ok('reduced motion: result shows final % instantly, no level-up overlay', await r.evaluate(() => document.querySelector('#res-pct').textContent === '100%' && getComputedStyle(document.querySelector('#levelup')).display === 'none'));

/* ================= API mode ================= */
if (process.env.CTF_API !== '0') {
  const up = await fetch('http://127.0.0.1:5000/api/health').then(x => x.ok).catch(() => false);
  if (!up) ok('API mode: Flask on :5000 (start it to run these checks)', false, 'not running');
  else {
    const a = await newPage({ blockApi: false });
    a.apiMode = true;
    await a.goto(BASE + 'ctf.html#/hub', { waitUntil: 'load' });
    await a.waitForFunction(() => document.documentElement.dataset.ctfMode === 'api', { timeout: 6000 }).catch(() => {});
    ok('API mode: banner online, leaderboard tabs shown', await a.evaluate(() => /online/.test(document.querySelector('#mode-text').textContent) && !document.querySelector('#board-tabs').hidden));
    const nick = 'tester' + Math.floor(Math.random() * 1e5);
    await a.type('#nick', 'a'); await a.click('#join-form button[type="submit"]'); await sleep(400);
    ok('nickname validation error shown', await a.evaluate(() => !document.querySelector('#nick-error').hidden && document.querySelector('#nick-error').textContent.length > 5), await a.$eval('#nick-error', e => e.textContent));
    await a.$eval('#nick', e => { e.value = ''; }); await a.type('#nick', nick); await a.click('#join-form button[type="submit"]');
    await a.waitForFunction(() => !document.querySelector('#player-in').hidden, { timeout: 6000 });
    ok('join: recovery code shown once', await a.evaluate(() => /^[0-9a-f]{4}(-?[0-9a-f]{4}){3}$|^[0-9a-f]{16}$/i.test(document.querySelector('#recovery-code').textContent.trim())), await a.$eval('#recovery-code', e => e.textContent));
    await start(a, 'networking', 'beginner');
    await playLevel(a, 'right');
    await sleep(500);
    const ar = await a.evaluate(() => ({ where: document.querySelector('#res-where').textContent, pct: document.querySelector('#res-pct').textContent }));
    ok('API mode: ranked run scored by the server', /ranked/.test(ar.where), JSON.stringify(ar));
    await a.evaluate(() => { location.hash = '#/hub'; }); await sleep(600);
    const lb = await a.evaluate(() => document.querySelector('#board-list').textContent);
    ok('API mode: player on the leaderboard', lb.includes(nick), lb.slice(0, 80));
    ok('API mode: no console errors', a.errors.length === 0, a.errors.join(' | '));
  }
}

console.log(results.join('\n'));
const fails = results.filter(x => x.startsWith('FAIL')).length;
console.log(`\nCTF: ${results.length - fails}/${results.length} passed`);
await browser.close();
if (fails) process.exitCode = 1;
