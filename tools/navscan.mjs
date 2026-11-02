// Sweep viewport widths and check the header fits: brand, links and buttons must not overlap or overflow.
import puppeteer from 'puppeteer-core';
const BASE = (process.env.URL || 'http://127.0.0.1:8000/').replace(/\/?$/, '/');
const PAGES = process.argv.slice(2).length ? process.argv.slice(2) : ['index.html', 'commands.html', 'scams.html', 'terminal.html', 'ctf.html', 'prompts.html', 'cyberlaw.html', 'terms.html', 'privacy.html', '404.html'];
const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'], protocolTimeout: 120000 });
let bad = 0;
for (const pg of PAGES) {
  const p = await b.newPage();
  await p.evaluateOnNewDocument(() => localStorage.setItem('cwm-consent', JSON.stringify({ v: 2, at: 'scan' })));
  await p.setViewport({ width: 1600, height: 800 });
  const r = await p.goto(BASE + pg, { waitUntil: 'load', timeout: 30000 }).catch(() => null);
  if (!r) { console.log(pg, 'load fail'); continue; }
  const fails = [];
  for (let w = 320; w <= 1600; w += 10) {
    await p.setViewport({ width: w, height: 800 });
    const f = await p.evaluate(() => {
      const inner = document.querySelector('.nav-inner'); if (!inner) return null;
      const ir = inner.getBoundingClientRect();
      const kids = [...inner.querySelectorAll('.brand, .brand > *, #nav-links > a, #nav-links > details > summary, #nav-links > button, .nav-inner > button, .nav-inner > a')].filter(e => e.offsetWidth && getComputedStyle(e).visibility !== 'hidden' && !e.closest('#nav-links:not(.open)') || (e.closest('#nav-links') && getComputedStyle(document.getElementById('nav-links')).position !== 'absolute' && e.offsetWidth));
      const rs = kids.map(e => [e, e.getBoundingClientRect()]).filter(([e, r]) => r.width > 1);
      const out = [];
      for (const [e, r] of rs) if (r.left < ir.left - 1 || r.right > ir.right + 1) out.push('out:' + (e.className || e.tagName));
      for (let i = 0; i < rs.length; i++) for (let j = i + 1; j < rs.length; j++) { const [a, ra] = rs[i], [c, rc] = rs[j]; if (a.contains(c) || c.contains(a)) continue; if (Math.min(ra.right, rc.right) - Math.max(ra.left, rc.left) > 1 && Math.min(ra.bottom, rc.bottom) - Math.max(ra.top, rc.top) > 1) out.push((a.textContent.trim().slice(0, 12) || a.className) + ' X ' + (c.textContent.trim().slice(0, 12) || c.className)); }
      if (document.documentElement.scrollWidth > innerWidth) out.push('overflowX');
      return out.length ? out.join(', ') : null;
    });
    if (f) fails.push(w + ': ' + f);
  }
  if (fails.length) { bad++; console.log('== ' + pg); fails.slice(0, 40).forEach(x => console.log('  ' + x)); }
  await p.close();
}
await b.close();
console.log(bad ? `${bad} pages with header issues` : 'header fits at every width 320..1600');
