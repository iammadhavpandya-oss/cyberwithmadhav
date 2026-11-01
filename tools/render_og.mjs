// Renders the share image and app icons. Run from tools/: node render_og.mjs
import puppeteer from 'puppeteer-core';
const root = new globalThis.URL('../', import.meta.url).pathname;
const b = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox', '--allow-file-access-from-files'] });
const p = await b.newPage();
await p.setViewport({ width: 1200, height: 630 });
await p.goto('file://' + root + 'tools/og/og.html', { waitUntil: 'networkidle0' });
await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: root + 'assets/img/og-image.png' });
await p.goto('file://' + root + 'tools/og/icon.html', { waitUntil: 'networkidle0' });
for (const s of [512, 192, 180]) {
  await p.setViewport({ width: 512, height: 512, deviceScaleFactor: s / 512 });
  await p.screenshot({ path: root + `assets/img/${s === 180 ? 'apple-touch-icon' : 'icon-' + s}.png` });
}
await b.close();
console.log('rendered og-image.png and icons');
