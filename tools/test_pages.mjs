// prompts.html + cyberlaw.html checks and screenshots. Run from tools/: node test_pages.mjs
// Needs the static server on :8000 (python3 -m http.server 8000). Also run at the end of test.mjs.
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
const BASE = (process.env.URL || 'http://127.0.0.1:8000/').replace(/\/?$/, '/');
const OUT = new globalThis.URL('../docs/', import.meta.url).pathname;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const results = [];
const ok = (name, cond, extra = '') => { results.push(`${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '  : ' + extra : ''}`); };
const browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });

// Consent gate: pre-accept for these suites (the gate itself is covered by test_consent.mjs).
{ const _np = browser.newPage.bind(browser); browser.newPage = async (...a) => { const p = await _np(...a); await p.evaluateOnNewDocument(() => { try { localStorage.setItem('cwm-consent', JSON.stringify({ v: 4, at: 'test' })); } catch (e) {} }); return p; }; }
await browser.defaultBrowserContext().overridePermissions(new globalThis.URL(BASE).origin, ['clipboard-read', 'clipboard-write', 'clipboard-sanitized-write']);

async function open(path, { width = 1440, height = 900, scheme = 'dark', mobile = false, reduce = false, wait = 'networkidle0' } = {}) {
  const p = await browser.newPage();
  p.errors = [];
  p.on('console', m => { if (['error', 'warning'].includes(m.type())) p.errors.push(m.type() + ': ' + m.text()); });
  p.on('pageerror', e => p.errors.push('pageerror: ' + e.message));
  const feats = [{ name: 'prefers-color-scheme', value: scheme }];
  if (reduce) feats.push({ name: 'prefers-reduced-motion', value: 'reduce' });
  await p.emulateMediaFeatures(feats);
  await p.setViewport({ width, height, isMobile: mobile, hasTouch: mobile, deviceScaleFactor: mobile ? 2 : 1 });
  p.on('domcontentloaded', () => p.evaluate(() => { document.documentElement.style.scrollBehavior = 'auto'; }).catch(() => {}));
  await p.goto(BASE + path, { waitUntil: wait });
  return p;
}
const textCheck = p => p.evaluate(() => {
  const t = document.body.innerText;
  return { em: (t.match(/\u2014/g) || []).length, overflow: document.documentElement.scrollWidth - window.innerWidth };
});
const slimCheck = p => p.evaluate(() => { const n = [...document.querySelectorAll('.notice-slim')]; const a = n[0] && n[0].querySelector('a'); return { boxes: document.querySelectorAll('.disc-box').length, n: n.length, text: n[0] ? n[0].textContent.trim() : '', href: a ? a.getAttribute('href') : '', h: n[0] ? n[0].getBoundingClientRect().height : 0, dash: n.some(x => /[\u2013\u2014]/.test(x.textContent)), legal: [...document.querySelectorAll('footer .foot-legal a')].map(x => x.getAttribute('href')).join(',') }; });
async function revealAll(p) {
  await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 40)); } window.scrollTo(0, 0); });
  await sleep(400);
}

/* ---------- prompts.html ---------- */
let p = await open('prompts.html');
await p.waitForFunction(() => document.documentElement.dataset.promptsReady === '1');
let r = await p.evaluate(() => ({
  banner: document.querySelector('#ethics').textContent.trim(),
  chips: document.querySelectorAll('#p-cats .chip').length,
  cards: document.querySelectorAll('.p-card').length,
  da: document.querySelector('#p-cats .chip[data-cat="defensive-analysis"]')?.textContent || '',
  everyCard: [...document.querySelectorAll('.p-card')].every(c => c.querySelector('h3') && c.querySelector('.p-use') && c.querySelector('pre code') && c.querySelector('.copy') && c.querySelector('.p-tip') && c.querySelector('.p-model')),
  placeholders: document.querySelectorAll('.p-card .ph').length,
  navActive: document.querySelector('#nav-links a[aria-current="page"]')?.textContent, navHub: document.querySelector('#nav-links a.active')?.getAttribute('href'),
  navLinks: [...document.querySelectorAll('#nav-links a')].map(a => a.textContent.trim()).join('|'),
  uc: document.querySelectorAll('.uc').length, lv: document.querySelectorAll('.uc .lvl').length,
  chipNames: [...document.querySelectorAll('#p-cats .chip')].map(c => c.dataset.cat).filter(c => c !== 'all'),
  ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent),
  desc: document.querySelector('meta[name="description"]').content, kw: document.querySelector('meta[name="keywords"]')?.content || '',
  canon: document.querySelector('link[rel=canonical]').href, ogUrl: document.querySelector('meta[property="og:url"]').content
}));
{ let ld = null; try { ld = JSON.parse(r.ld[0]); } catch (e) { /* bad */ }
  const cats = await p.evaluate(() => fetch('data/prompts.json').then(x => x.json()).then(d => d.categories.map(c => c.name + ' prompts')));
  const names = ld ? ld.itemListElement.map(x => x.item.name) : [];
  ok('prompts SEO: ItemList JSON-LD lists exactly the 19 rendered categories incl. Defensive Analysis', ld && ld.numberOfItems === 19 && names.length === r.chipNames.length && JSON.stringify(names) === JSON.stringify(cats) && names.includes('Defensive Analysis prompts'), names.length + '');
  ok('prompts SEO: meta says 90 prompts / 19 categories, keywords, real canonical + og:url', /^90 free defensive AI prompts in 19 categories/.test(r.desc) && /Defensive Analysis/.test(r.desc) && r.kw.length > 20
    && r.canon === 'https://www.cyberwithmadhav.com/prompts.html' && r.ogUrl === r.canon, r.desc); }
{ const sc = await slimCheck(p);
  ok('prompts: big disclaimer boxes gone, one slim notice links to Terms, footer legal links', sc.boxes === 0 && sc.n === 1 && /Authorised and defensive use only/.test(sc.text) && /^terms\.html/.test(sc.href) && sc.h < 60 && !sc.dash && sc.legal === 'terms.html,privacy.html', JSON.stringify(sc)); }
ok('prompts: ethics banner', r.banner === 'Use only on systems and data you own or are authorised to test.', r.banner);
ok('prompts: 90 cards, each with title/use/template/copy/tip/model', r.cards === 90 && r.everyCard, String(r.cards));
ok('prompts: 19 categories + All chip, incl. Defensive Analysis', r.chips === 20 && /Defensive Analysis/.test(r.da), r.chips + ' ' + r.da);
ok('prompts: [placeholders] highlighted', r.placeholders > 90, String(r.placeholders));
ok('prompts: short nav (Home, Explore, Blog, CTF) with Explore highlighted', r.navLinks === 'Home|Explore|Blog|CTF' && r.navHub === 'explore.html' && !r.navActive, r.navLinks + ' ' + r.navHub);
ok('prompts: 12 use-case cards with level badges', r.uc === 12 && r.lv === 12);
await p.type('#p-search', 'nmap'); await sleep(300);
const nm = await p.$$eval('.p-card', cs => cs.length);
ok('prompts: search filters', nm > 0 && nm < 90, String(nm));
await p.click('#p-search', { clickCount: 3 }); await p.keyboard.press('Backspace'); await sleep(300);
await p.click('#p-cats .chip[data-cat="defensive-analysis"]'); await sleep(100);
const da = await p.evaluate(() => ({ n: document.querySelectorAll('.p-card').length, cats: [...new Set([...document.querySelectorAll('.p-card')].map(c => c.dataset.cat))] }));
ok('prompts: Defensive Analysis filter groups analysis categories', da.n === 40 && !da.cats.includes('career'), JSON.stringify(da));
await p.click('#p-cats .chip[data-cat="soc"]'); await sleep(100);
ok('prompts: category filter', (await p.$$eval('.p-card', cs => cs.every(c => c.dataset.cat === 'soc') && cs.length)) === 8);
const firstId = await p.$eval('.p-card', c => c.dataset.id);
await p.click('.p-card .fav'); await sleep(100);
await p.click('.p-card .copy'); await sleep(200);
const clip = await p.evaluate(() => navigator.clipboard.readText());
const want = await p.evaluate(id => fetch('data/prompts.json').then(r => r.json()).then(d => d.prompts.find(x => x.id === id).prompt), firstId);
ok('prompts: copy button copies the template', clip === want);
await p.reload({ waitUntil: 'networkidle0' });
await p.waitForFunction(() => document.documentElement.dataset.promptsReady === '1');
await p.click('#p-favs'); await sleep(100);
const fav = await p.evaluate(() => ({ ids: [...document.querySelectorAll('.p-card')].map(c => c.dataset.id), n: document.querySelector('#fav-n').textContent }));
ok('prompts: favourites persist in localStorage', fav.ids.length === 1 && fav.ids[0] === firstId && fav.n === '1', JSON.stringify(fav));
await p.click('#p-favs');
await p.click('#uc-levels .chip[data-level="expert"]'); await sleep(50);
ok('prompts: use-case level filter', (await p.$$eval('.uc:not([hidden])', cs => cs.length)) === 4);
await p.click('#uc-levels .chip[data-level="all"]');
await p.evaluate(() => document.querySelector('.uc .btn').click()); await sleep(300);
ok('prompts: use-case button opens matching category', (await p.$eval('#p-cats .chip[aria-pressed="true"]', c => c.dataset.cat)) === 'defensive-analysis');
await p.evaluate(() => window.scrollTo(0, 0)); await sleep(500);
await p.click('#p-cats .chip[data-cat="all"]'); await sleep(200);
let tc = await textCheck(p);
ok('prompts: no em dash, no horizontal overflow', tc.em === 0 && tc.overflow <= 0, JSON.stringify(tc));
await p.screenshot({ path: OUT + 'prompts-dark.png' });
ok('prompts: no console errors', p.errors.length === 0, p.errors.join(' | '));
await p.close();

/* ---------- cyberlaw.html (dark) ---------- */
p = await open('cyberlaw.html');
await p.waitForFunction(() => document.documentElement.dataset.lawReady === '1');
await sleep(2800);
r = await p.evaluate(() => ({
  h1: document.querySelector('#law-title').textContent.trim(),
  h1o: getComputedStyle(document.querySelector('#law-title')).opacity,
  sub: document.querySelector('#hero-sub').textContent,
  disc: document.body.innerText.includes('Educational, not legal advice'),
  tl: document.querySelectorAll('#tl > li').length, it: document.querySelectorAll('#it-table tbody tr').length,
  bns: document.querySelectorAll('#bns-table tbody tr').length, dp: document.querySelectorAll('#dp-grid .card').length,
  st: document.querySelectorAll('#steps .card').length, cases: document.querySelectorAll('.case').length,
  caseSrc: document.querySelector('#case-grid').dataset.source,
  pending: document.querySelectorAll('.case .cite .verify').length,
  rawVerifyInCite: [...document.querySelectorAll('.case .cite')].some(c => /\(verify\)/i.test(c.firstChild?.textContent || '')),
  sccInPending: [...document.querySelectorAll('.case .cite')].filter(c => c.querySelector('.verify')).some(c => /SCC|DLT/.test(c.firstChild?.textContent || '') && !/Aneeta/.test(c.textContent)),
  kamra: [...document.querySelectorAll('.case')].find(c => /Kamra/.test(c.textContent))?.textContent || '',
  faq: document.querySelectorAll('#faq-list details').length, gl: document.querySelectorAll('#gl-list .gl-item').length,
  soon: document.querySelectorAll('#dl-grid .soon').length, pdfLinks: document.querySelectorAll('#dl-grid a[href$=".pdf"]').length,
  verifyTags: document.querySelectorAll('.verify').length,
  badLinks: [...document.querySelectorAll('main a[target="_blank"]')].filter(a => !/^https:\/\//.test(a.getAttribute('href'))).map(a => a.href),
  extNoRel: [...document.querySelectorAll('main a[target="_blank"]')].filter(a => !/noopener/.test(a.rel)).length,
  itRowsSrc: [...document.querySelectorAll('#it-table tbody tr')].every(tr => tr.querySelector('a.src')),
  tlSrc: [...document.querySelectorAll('#tl li')].every(li => li.querySelector('a.src')),
  tlHist: document.querySelector('#tl').dataset.source === 'file' && document.querySelector('#tl').classList.contains('tl-hist'),
  tlHead: document.querySelector('#timeline-h').textContent.trim(),
  tlWhy: document.querySelectorAll('#tl .why').length,
  pendingTags: document.querySelectorAll('.verify.pending').length,
  pendIn: ['#it-table', '#dp-status', '#steps', '#faq-list', '#gl-list', '#tl'].filter(q => document.querySelector(q + ' .verify.pending')),
  bnsPun: [...document.querySelectorAll('#bns-table tbody tr')].find(tr => /Cheating \(online/.test(tr.textContent))?.children[3]?.textContent || '',
  it72: [...document.querySelectorAll('#it-table tbody tr')].find(tr => tr.children[0].textContent === '72')?.textContent || '',
  it43A: [...document.querySelectorAll('#it-table tbody tr')].find(tr => tr.children[0].textContent === '43A')?.textContent || '',
  faqAll: [...document.querySelectorAll('#faq-list details')].map(d => d.textContent),
  ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent),
  desc: document.querySelector('meta[name="description"]').content, canon: document.querySelector('link[rel=canonical]').href,
  court: !!document.querySelector('.court svg .gavel') && !!document.querySelector('.court .beam') && !!document.querySelector('.ink path'),
  serif: getComputedStyle(document.querySelector('#law-title')).fontFamily
}));
ok('law: hero headline', r.h1 === "Entering someone's device without permission is illegal in India" && r.h1o === '1', r.h1);
ok('law: subline Sec 43 civil, Sec 66 dishonest/fraudulent, 3 yrs / 5 lakh', /Section 43/.test(r.sub) && /civil/.test(r.sub) && /dishonestly or fraudulently/.test(r.sub) && /3 years/.test(r.sub) && /5 lakh/.test(r.sub));
ok('law: disclaimer', r.disc);
{ const sc = await slimCheck(p);
  ok('law: big disclaimer boxes gone, one slim notice links to Terms, footer legal links', sc.boxes === 0 && sc.n === 1 && sc.text === 'Educational only, not legal advice. See Terms.' && sc.href === 'terms.html' && sc.h < 60 && !sc.dash && sc.legal === 'terms.html,privacy.html', JSON.stringify(sc)); }
ok('law: counts timeline 26, IT Act 28, BNS 17, DPDP 7, steps 7', r.tl === 26 && r.it === 28 && r.bns === 17 && r.dp === 7 && r.st === 7, [r.tl, r.it, r.bns, r.dp, r.st].join(','));
ok('law: "History of Indian Cyber Law" timeline from data/cyberlaw_timeline.json, why-it-matters on each entry', r.tlHist && r.tlHead === 'History of Indian Cyber Law' && r.tlWhy === 26, r.tlHead + ' ' + r.tlWhy);
ok('law: fact-check "being verified" tags in IT table, DPDP, steps, FAQ, glossary and timeline', r.pendIn.length === 6 && r.pendingTags >= 15, r.pendingTags + ' ' + r.pendIn.join(','));
ok('law: BNS punishment column (318(2) 3 years vs IPC 417 1 year)', /318\(2\): up to 3 years \(IPC 417: 1 year\)/.test(r.bnsPun), r.bnsPun);
ok('law: s.72 is a civil penalty (Jan Vishwas), s.43A still in force until ~May 2027', /Penalty up to ₹5 lakh/.test(r.it72) && /Civil/.test(r.it72) && /Still in force/.test(r.it43A) && /13 May 2027/.test(r.it43A));
ok('law: FAQ12 says Superintendent of Police (no DCP), FAQ6 phased DPDP, FAQ9 2026 timelines, FAQ13 RB-IOS 2026',
  /Superintendent of Police/.test(r.faqAll[11]) && !/DCP/.test(r.faqAll[11]) && /13 May 2027/.test(r.faqAll[5]) && /43A/.test(r.faqAll[5]) && /2 hours/.test(r.faqAll[8]) && /7 days/.test(r.faqAll[8]) && /Integrated Ombudsman Scheme, 2026/.test(r.faqAll[12]) && /₹30 lakh/.test(r.faqAll[12]));
{ let ld = null; try { ld = JSON.parse(r.ld[0]); } catch (e) { /* bad */ }
  ok('law SEO: FAQPage JSON-LD with 15 answers matching the page, real canonical, meta without dropped wording', r.ld.length === 1 && ld && ld['@type'] === 'FAQPage' && ld.mainEntity.length === 15 && /Superintendent of Police/.test(ld.mainEntity[11].acceptedAnswer.text)
    && r.canon === 'https://www.cyberwithmadhav.com/cyberlaw.html' && !/punishments, bail and compounding|DPDP Act penalties/.test(r.desc), r.desc); }
ok('law: 12 case files loaded from data/cyberlaw_cases.json', r.cases === 12 && r.caseSrc === 'file', r.cases + ' ' + r.caseSrc);
ok('law: unconfirmed citations show "citation being verified" not the SCC/DLT cite', r.pending === 6 && !r.rawVerifyInCite && !r.sccInPending, String(r.pending));
{ const want = JSON.parse(fs.readFileSync(new globalThis.URL('../data/cyberlaw_reporting.json', import.meta.url)));
  const fr = await p.evaluate(() => [...document.querySelectorAll('#file-list details.file-card')].map(d => ({ t: d.querySelector('.ft').textContent, v: !!d.querySelector('summary .verify'), href: d.querySelector('.file-body a.src')?.getAttribute('href'), docs: d.querySelectorAll('.file-body li').length, dt: [...d.querySelectorAll('dt')].map(x => x.textContent).join('|') })));
  ok('law: Where to File has 9 expandable forum cards, NCRP then 1930 first', fr.length === 9 && /NCRP/.test(fr[0].t) && /1930/.test(fr[1].t) && Array.isArray(want) && want.length === 9, fr.map(x => x.t.slice(0, 18)).join(' / '));
  ok('law: each forum card shows who/when/time limit/documents, verify badge as flagged, official_url link', fr.every((x, i) => x.dt === 'Who can file|When to use|Time limit|Documents needed' && x.v === want[i].verify && x.href === want[i].official_url && x.docs === want[i].documents_needed.length), String(fr.filter(x => x.v).length) + ' verify');
  await p.focus('#file-list summary'); await p.keyboard.press('Enter'); await sleep(100);
  ok('law: forum card expands from the keyboard', await p.$eval('#file-list details', d => d.open));
  await p.evaluate(() => document.querySelector('#where-to-file').scrollIntoView()); await sleep(900);
  await p.screenshot({ path: OUT + 'cyberlaw-where-to-file-dark.png' });
  await p.keyboard.press('Enter'); }
ok('law: Kamra card says SC appeal pending', /appeal.*is pending in the Supreme Court/.test(r.kamra));
ok('law: FAQ 15, glossary 40', r.faq === 15 && r.gl === 40, r.faq + ' ' + r.gl);
{ const dl = JSON.parse(fs.readFileSync(new globalThis.URL('../data/cyberlaw.json', import.meta.url))).downloads;
  const have = dl.filter(d => d.available).length;
  const links = have + dl.reduce((n, d) => n + (d.claude && d.claude.available ? 1 + (d.claude.dark_available ? 1 : 0) : 0), 0);
  ok('law: PDF 1 and PDF 2 (Claude, Light + Dark) are links if the files exist, else "coming soon"', r.pdfLinks === links && r.soon === dl.length - have, r.pdfLinks + ' links ' + r.soon + ' soon'); }
for (const f of ['cyberlaw-pg-cheatsheet.pdf', 'cyberprompts-sheet.pdf', 'cyberlaw-pg-cheatsheet-claude.pdf', 'cyberlaw-pg-cheatsheet-claude-dark.pdf', 'cyberprompts-sheet-claude.pdf', 'cyberprompts-sheet-claude-dark.pdf']) {
  const res = await fetch(BASE + 'assets/pdf/' + f).catch(() => null);
  const exists = fs.existsSync(new globalThis.URL('../assets/pdf/' + f, import.meta.url));
  if (exists) ok('pdf served 200: ' + f, res && res.status === 200 && (res.headers.get('content-type') || '').includes('pdf'), res && res.status);
}
ok('law: every row and event has a citation link; external links https + noopener', r.itRowsSrc && r.tlSrc && r.badLinks.length === 0 && r.extNoRel === 0, r.badLinks.join(' '));
ok('law: verify tags shown', r.verifyTags >= 10, String(r.verifyTags));
ok('law: courtroom SVG (gavel, scales, pen ink) + serif heading', r.court && /Libre Baskerville/.test(r.serif), r.serif);
// FAQ language toggle
await p.evaluate(() => document.querySelector('#faq-list details').open = true);
const en = await p.$eval('#faq-list .ans p', e => e.textContent);
await p.click('.lang .chip[data-lang="hi"]'); await sleep(100);
const hi = await p.evaluate(() => ({ t: document.querySelector('#faq-list .ans p').textContent, open: document.querySelector('#faq-list details').open, l: localStorage.getItem('cwm-law-lang') }));
ok('law: EN/Hinglish toggle swaps answers, keeps open item, remembers choice', hi.t !== en && hi.open && hi.l === '"hi"', hi.t.slice(0, 50));
await p.click('.lang .chip[data-lang="en"]');
await p.type('#gl-search', 'intermediary'); await sleep(100);
const gn = await p.$$eval('#gl-list .gl-item', cs => cs.length);
ok('law: glossary search', gn > 0 && gn < 40, String(gn));
await p.click('#gl-search', { clickCount: 3 }); await p.keyboard.press('Backspace');
await p.click('#it-filter .chip[data-k="civil"]'); await sleep(50);
ok('law: IT Act filter', (await p.$$eval('#it-table tbody tr:not([hidden])', t => t.every(x => x.dataset.kind === 'civil') && t.length)) > 0);
await p.click('#it-filter .chip[data-k="all"]');
// keyboard: FAQ summary reachable and toggles with Enter
await p.focus('#faq-list summary'); await p.keyboard.press('Enter');
ok('law: FAQ accordion works from the keyboard', await p.$eval('#faq-list details:nth-child(2)', d => true) && await p.$eval('#faq-list details', d => d.open === false));
await revealAll(p);
tc = await textCheck(p);
ok('law: no em dash, no horizontal overflow (desktop)', tc.em === 0 && tc.overflow <= 0, JSON.stringify(tc));
await p.screenshot({ path: OUT + 'cyberlaw-dark.png' });
await p.evaluate(() => document.querySelector('#cases').scrollIntoView()); await sleep(900);
await p.screenshot({ path: OUT + 'cyberlaw-cases-dark.png' });
ok('law: no console errors', p.errors.length === 0, p.errors.join(' | '));
await p.close();

/* light */
p = await open('cyberlaw.html', { scheme: 'light' });
await p.waitForFunction(() => document.documentElement.dataset.lawReady === '1');
await sleep(2800);
const lt = await p.evaluate(() => ({ theme: document.documentElement.dataset.theme, bg: getComputedStyle(document.querySelector('.law-cards .card')).backgroundImage }));
await p.evaluate(() => document.querySelector('#timeline').scrollIntoView()); await sleep(1800);
const tlBg = await p.evaluate(() => getComputedStyle(document.querySelector('#tl .card')).backgroundImage);
ok('law light: timeline entries are parchment', /radial-gradient/.test(tlBg) && /255, 249, 232/.test(tlBg), tlBg.slice(0, 80));
await p.screenshot({ path: OUT + 'cyberlaw-timeline-light.png' });
await p.evaluate(() => window.scrollTo(0, 0)); await sleep(400);
ok('law light: parchment / legal-pad cards', lt.theme === 'light' && /radial-gradient/.test(lt.bg) && /repeating-linear-gradient/.test(lt.bg));
await p.screenshot({ path: OUT + 'cyberlaw-light.png' });
await p.evaluate(() => document.querySelector('#faq').scrollIntoView()); await sleep(900);
await p.screenshot({ path: OUT + 'cyberlaw-faq-light.png' });
ok('law light: no console errors', p.errors.length === 0, p.errors.join(' | '));
await p.close();

/* mobile + reduced motion */
p = await open('cyberlaw.html', { width: 390, height: 844, mobile: true, reduce: true });
await p.waitForFunction(() => document.documentElement.dataset.lawReady === '1');
const rm = await p.evaluate(() => ({ o: getComputedStyle(document.querySelector('#law-title')).opacity, a: getComputedStyle(document.querySelector('.court .beam')).animationName, ink: getComputedStyle(document.querySelector('.ink path')).strokeDashoffset }));
ok('law mobile: reduced motion shows final state, no animation', rm.o === '1' && rm.a === 'none' && /^0/.test(rm.ink), JSON.stringify(rm));
const tlr = await p.evaluate(() => { const li = document.querySelector('#tl li'); return { o: getComputedStyle(li).opacity, t: getComputedStyle(li).transform, line: getComputedStyle(document.querySelector('#tl'), '::before').transform }; });
ok('law mobile: reduced motion timeline is static (no slide, line drawn)', tlr.o === '1' && tlr.t === 'none' && /^(none|matrix\(1, 0, 0, 1, 0, 0\))$/.test(tlr.line), JSON.stringify(tlr));
await p.click('.nav-toggle'); await sleep(150);
const nav = await p.evaluate(() => ({ open: document.querySelector('#nav-links').classList.contains('open'), hub: [...document.querySelectorAll('#nav-links a')].some(a => a.getAttribute('href') === 'explore.html' && a.textContent.trim() === 'Explore') }));
ok('law mobile: menu opens and lists Explore (the hub that links Cyber Law)', nav.open && nav.hub);
await p.click('.nav-toggle');
await revealAll(p);
tc = await textCheck(p);
ok('law mobile: no horizontal overflow', tc.overflow <= 0, JSON.stringify(tc));
await p.screenshot({ path: OUT + 'cyberlaw-mobile.png' });
await p.close();

/* index + ctf nav: the short nav (Home, Explore, CTF) fits on one line */
for (const page of ['index.html', 'ctf.html']) {
  const q = await open(page, { width: 1000, height: 800, wait: 'load' }); await sleep(800);
  const n = await q.evaluate(() => { const nl = document.querySelector('#nav-links'); const links = [...nl.querySelectorAll('a')].map(a => a.getAttribute('href')); const tops = new Set([...nl.children].filter(c => c.getClientRects().length).map(c => Math.round(c.getBoundingClientRect().top + c.getBoundingClientRect().height / 2))); return { links, rows: tops.size, over: document.documentElement.scrollWidth - innerWidth }; });
  if (page === 'ctf.html') { const m = await q.evaluate(async () => ({ t: (await (await fetch(location.href)).text()).match(/<title>([^<]*)/)[1], ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { return JSON.parse(s.textContent)['@type']; } catch (e) { return 'bad'; } }), c: document.querySelector('link[rel=canonical]').href }));
    ok('ctf SEO: title, LearningResource JSON-LD, real canonical', m.t === 'CTF Arena: Free Cyber Security Practice | CyberWithMadhav' && m.ld.join() === 'LearningResource' && m.c === 'https://www.cyberwithmadhav.com/ctf.html', JSON.stringify(m)); }
  ok(`${page}: nav is Home, Explore, Blog, CTF in one row at 1000px`, n.links.join() === 'index.html,explore.html,blog.html,ctf.html' && n.rows === 1 && n.over <= 0, JSON.stringify({ rows: n.rows, over: n.over }));
  await q.close();
}

await browser.close();
console.log('\n=== prompts + cyberlaw ===\n' + results.join('\n'));
const fails = results.filter(x => x.startsWith('FAIL')).length;
console.log(`${results.length - fails}/${results.length} passed`);
if (fails) process.exitCode = 1;
