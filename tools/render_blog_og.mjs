// Renders assets/img/madhav-og.jpg (About page share image) and one share image per blog post
// (assets/img/blog/<slug>.png) from tools/og/*.html. Run from tools/ after build_blog.py: node render_blog_og.mjs
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
const root = new globalThis.URL('../', import.meta.url).pathname;
const posts = JSON.parse(fs.readFileSync(root + 'tools/og/blog-og.json', 'utf8'));
const b = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox', '--allow-file-access-from-files'] });
const p = await b.newPage();
await p.setViewport({ width: 1200, height: 630 });
await p.goto('file://' + root + 'tools/og/madhav-og.html', { waitUntil: 'networkidle0' });
await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: root + 'assets/img/madhav-og.jpg', type: 'jpeg', quality: 88 });
fs.mkdirSync(root + 'assets/img/blog', { recursive: true });
for (const x of posts) {
  await p.goto('file://' + root + 'tools/og/blog-og.html?t=' + encodeURIComponent(x.title) + '&c=' + encodeURIComponent(x.category), { waitUntil: 'networkidle0' });
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: root + `assets/img/blog/${x.slug}.png` });
}
await b.close();
console.log('rendered madhav-og.jpg and', posts.length, 'blog share images');
