/* CyberWithMadhav — vanilla JS. Content lives in /data/*.json */
(function () {
  'use strict';
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Backend base URL: <meta name="cwm-api" content="https://api.example.com"> overrides.
  const apiMeta = document.querySelector('meta[name="cwm-api"]');
  const LOCAL = ['localhost', '127.0.0.1'].includes(location.hostname);
  const API = apiMeta ? apiMeta.content.replace(/\/$/, '') : (LOCAL ? 'http://127.0.0.1:5000' : '');

  /* ---------- reveal ---------- */
  let io = null;
  if (!reduced && 'IntersectionObserver' in window) {
    io = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  }
  function observe(root = document) {
    $$('.reveal:not(.in)', root).forEach(el => io ? io.observe(el) : el.classList.add('in'));
  }

  /* ---------- toast + copy ---------- */
  const toast = $('#toast');
  let toastT;
  function showToast(msg) {
    toast.textContent = msg; toast.classList.add('show');
    clearTimeout(toastT); toastT = setTimeout(() => toast.classList.remove('show'), 1800);
  }
  async function copyText(text) {
    try { await navigator.clipboard.writeText(text); return true; }
    catch (_) {
      const ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      let ok = false; try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      ta.remove(); return ok;
    }
  }

  /* ---------- nav, progress, theme ---------- */
  const navBtn = $('.nav-toggle'), navLinks = $('#nav-links');
  navBtn.addEventListener('click', () => {
    const open = navLinks.classList.toggle('open');
    navBtn.setAttribute('aria-expanded', String(open));
    navBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
  $$('#nav-links a').forEach(a => a.addEventListener('click', () => {
    navLinks.classList.remove('open'); navBtn.setAttribute('aria-expanded', 'false');
  }));

  const bar = $('#progress-bar');
  let ticking = false;
  function onScroll() {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
    ticking = false;
  }
  window.addEventListener('scroll', () => { if (!ticking) { requestAnimationFrame(onScroll); ticking = true; } }, { passive: true });
  onScroll();

  if ('IntersectionObserver' in window) {
    const links = new Map($$('#nav-links a[href^="#"]').map(a => [a.getAttribute('href').slice(1), a]));
    const spy = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting && links.has(e.target.id)) {
          links.forEach(a => a.classList.remove('active'));
          links.get(e.target.id).classList.add('active');
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    links.forEach((_, id) => { const s = document.getElementById(id); if (s) spy.observe(s); });
  }

  $('.theme-toggle').addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', cur);
    try { localStorage.setItem('cwm-theme', cur); } catch (e) {}
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = cur === 'light' ? '#FAF9FD' : '#0D0B14';
  });
  $('#year').textContent = new Date().getFullYear();

  /* ---------- data loading ---------- */
  const load = (name) => fetch(`data/${name}.json`, { cache: 'no-cache' }).then(r => {
    if (!r.ok) throw new Error(`${name}.json: HTTP ${r.status}`); return r.json();
  });

  /* ---------- roadmap ---------- */
  function renderRoadmap(d) {
    const tabs = $('.stage-tabs'), panels = $('#roadmap-panels');
    tabs.innerHTML = d.stages.map((s, i) =>
      `<button role="tab" id="tab-${esc(s.id)}" aria-controls="panel-${esc(s.id)}" aria-selected="${i === 0}" tabindex="${i === 0 ? 0 : -1}"><span class="n">0${i + 1}</span>${esc(s.name)}</button>`).join('');
    panels.innerHTML = d.stages.map((s, i) => `
      <div class="stage" role="tabpanel" id="panel-${esc(s.id)}" aria-labelledby="tab-${esc(s.id)}" ${i ? 'hidden' : ''}>
        <p class="goal">${esc(s.goal)}</p>
        <article class="card reveal"><h3><span class="tag p">learn</span> Topics</h3>
          <ul class="dash">${s.topics.map(t => `<li>${esc(t)}</li>`).join('')}</ul></article>
        <article class="card reveal"><h3><span class="tag g">free</span> Resources</h3>
          <ul class="clean res">${s.resources.map(r => `<li><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.name)} ↗</a><small>${esc(r.note)}</small></li>`).join('')}</ul></article>
        <article class="card reveal"><h3><span class="tag">build</span> Project ideas</h3>
          <ul class="dash">${s.projects.map(t => `<li>${esc(t)}</li>`).join('')}</ul></article>
      </div>`).join('');
    const btns = $$('button', tabs);
    function select(btn) {
      btns.forEach(b => { const on = b === btn; b.setAttribute('aria-selected', on); b.tabIndex = on ? 0 : -1;
        $('#' + b.getAttribute('aria-controls')).hidden = !on; });
      observe(panels);
    }
    btns.forEach((b, i) => {
      b.addEventListener('click', () => select(b));
      b.addEventListener('keydown', e => {
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
          const n = btns[(i + (e.key === 'ArrowRight' ? 1 : btns.length - 1)) % btns.length];
          n.focus(); select(n);
        }
      });
    });
    observe(panels);
  }

  /* ---------- networking ---------- */
  function renderNetworking(d) {
    $('#layers').innerHTML = `
      <div class="layer-col"><h3>OSI model <span class="muted small">(7 layers, conceptual)</span></h3>
        ${d.osi.map(l => `<div class="layer"><b><span class="num">L${l.n}</span>${esc(l.name)}</b><span>${esc(l.ex)}</span></div>`).join('')}</div>
      <div class="layer-col tcp"><h3>TCP/IP model <span class="muted small">(4 layers, practical)</span></h3>
        ${d.tcpip.map(l => `<div class="layer"><b>${esc(l.name)}</b><span>${esc(l.ex)}</span></div>`).join('')}
        <p class="muted small" style="margin-top:12px">${esc(d.note)}</p></div>`;
    $('#net-cards').innerHTML = d.cards.map(c => `
      <article class="card net-card reveal"><h3>${esc(c.title)} <span class="tag g">${esc(c.tag)}</span></h3>
        <p>${esc(c.body)}</p><p class="ex">${esc(c.ex)}</p></article>`).join('') + `
      <article class="card net-card reveal"><h3>Common ports <span class="tag p">ref</span></h3>
        <table class="ports"><caption class="sr-only">Common ports and services</caption><tbody>
        ${d.ports.map(p => `<tr><td>${esc(p[0])}</td><td>${esc(p[1])}</td></tr>`).join('')}</tbody></table></article>`;
    observe($('#networking'));
  }

  /* ---------- subnet calculator ---------- */
  const ipToInt = (o) => ((o[0] << 24) | (o[1] << 16) | (o[2] << 8) | o[3]) >>> 0;
  const intToIp = (n) => [24, 16, 8, 0].map(s => (n >>> s) & 255).join('.');
  function parseCidr(str) {
    const m = String(str).trim().match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?:\/(\d{1,2}))?$/);
    if (!m) throw new Error('Use the format a.b.c.d/prefix, e.g. 10.0.0.5/16');
    const oct = m.slice(1, 5).map(Number);
    if (oct.some(o => o > 255) || m.slice(1, 5).some(o => o.length > 1 && o[0] === '0'))
      throw new Error('Each octet must be 0–255 without leading zeros.');
    const prefix = m[5] === undefined ? 32 : Number(m[5]);
    if (prefix > 32) throw new Error('Prefix must be between /0 and /32.');
    return { ip: ipToInt(oct), prefix, first: oct[0] };
  }
  function calcSubnet(str) {
    const { ip, prefix, first } = parseCidr(str);
    const mask = prefix === 0 ? 0 : (0xFFFFFFFF << (32 - prefix)) >>> 0;
    const network = (ip & mask) >>> 0;
    const broadcast = (network | (~mask >>> 0)) >>> 0;
    const total = 2 ** (32 - prefix);
    let usable, firstHost, lastHost;
    if (prefix === 32) { usable = 1; firstHost = lastHost = network; }
    else if (prefix === 31) { usable = 2; firstHost = network; lastHost = broadcast; }
    else { usable = total - 2; firstHost = network + 1; lastHost = broadcast - 1; }
    const cls = first < 128 ? 'A' : first < 192 ? 'B' : first < 224 ? 'C' : first < 240 ? 'D (multicast)' : 'E (reserved)';
    const inR = (base, bits) => ((ip & ((0xFFFFFFFF << (32 - bits)) >>> 0)) >>> 0) === ipToInt(base);
    const type = inR([10,0,0,0],8) || inR([172,16,0,0],12) || inR([192,168,0,0],16) ? 'Private (RFC 1918)'
      : inR([127,0,0,0],8) ? 'Loopback' : inR([169,254,0,0],16) ? 'Link-local (APIPA)'
      : inR([100,64,0,0],10) ? 'Shared / CGNAT (RFC 6598)' : first >= 224 ? 'Multicast / reserved' : 'Public';
    const bin = intToIp(mask).split('.').map(o => Number(o).toString(2).padStart(8, '0')).join('.');
    return {
      'Address': intToIp(ip), 'CIDR': `${intToIp(network)}/${prefix}`, 'Subnet mask': intToIp(mask),
      'Wildcard mask': intToIp(~mask >>> 0), 'Network': intToIp(network), 'Broadcast': prefix >= 31 ? 'n/a' : intToIp(broadcast),
      'First host': intToIp(firstHost), 'Last host': intToIp(lastHost),
      'Total addresses': total.toLocaleString('en-IN'), 'Usable hosts': usable.toLocaleString('en-IN'),
      'Class (legacy)': cls, 'Type': type, 'Mask (binary)': bin
    };
  }
  window.cwmCalcSubnet = calcSubnet; // exposed for testing
  function runSubnet(e) {
    if (e) e.preventDefault();
    const err = $('#subnet-error'), out = $('#subnet-out'), input = $('#subnet-input');
    try {
      const r = calcSubnet(input.value);
      err.textContent = ''; input.removeAttribute('aria-invalid');
      out.innerHTML = Object.entries(r).map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('');
    } catch (ex) {
      err.textContent = ex.message; input.setAttribute('aria-invalid', 'true'); out.innerHTML = '';
    }
  }
  $('#subnet-form').addEventListener('submit', runSubnet);
  runSubnet();

  /* ---------- cheat sheets ---------- */
  let sheets = [], activeCat = 'All';
  const openSheets = new Set();
  function hl(text, q) {
    const t = esc(text);
    if (!q) return t;
    const re = new RegExp('(' + esc(q).replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    return t.replace(re, '<mark>$1</mark>');
  }
  function renderSheets() {
    const q = $('#cs-search').value.trim();
    const ql = q.toLowerCase();
    let shown = 0, cmds = 0;
    const html = sheets.filter(s => activeCat === 'All' || s.category === activeCat).map(s => {
      const titleHit = !ql || s.title.toLowerCase().includes(ql) || s.category.toLowerCase().includes(ql);
      const items = s.items.filter(it => titleHit || (it.cmd + ' ' + it.what).toLowerCase().includes(ql));
      if (!items.length) return '';
      shown++; cmds += items.length;
      const text = s.type === 'text';
      const open = q || window.matchMedia('(min-width: 821px)').matches || openSheets.has(s.id);
      return `<details class="card sheet" data-id="${esc(s.id)}"${open ? ' open' : ''}>
        <summary><h3>${hl(s.title, q)} <span class="tag ${text ? 'p' : 'g'}">${esc(s.category)}</span></h3></summary>
        <p class="desc">${esc(s.desc)}</p>
        ${items.map(it => `<div class="cmd${text ? ' text' : ''}">
          <code>${hl(it.cmd, q)}</code><span class="what">${hl(it.what, q)}</span>
          ${text ? '' : `<button class="copy" type="button" data-copy="${esc(it.cmd)}" aria-label="Copy command: ${esc(it.cmd)}">copy</button>`}
        </div>`).join('')}
      </details>`;
    }).join('');
    $('#cs-list').innerHTML = html || `<div class="empty card">No matches for “${esc(q)}”. Try another keyword.</div>`;
    $('#cs-count').textContent = `${shown} sheet${shown === 1 ? '' : 's'} · ${cmds} entr${cmds === 1 ? 'y' : 'ies'}`;
  }
  function renderCheatsheets(d) {
    sheets = d.sheets;
    const cats = ['All', ...new Set(sheets.map(s => s.category))];
    $('#cs-filters').innerHTML = cats.map(c => `<button type="button" class="chip" aria-pressed="${c === 'All'}" data-cat="${esc(c)}">${esc(c)}</button>`).join('');
    $('#cs-filters').addEventListener('click', e => {
      const b = e.target.closest('.chip'); if (!b) return;
      activeCat = b.dataset.cat;
      $$('.chip').forEach(c => c.setAttribute('aria-pressed', c === b));
      renderSheets();
    });
    let t; $('#cs-search').addEventListener('input', () => { clearTimeout(t); t = setTimeout(renderSheets, 80); });
    $('#cs-list').addEventListener('click', async e => {
      const b = e.target.closest('.copy'); if (!b) return;
      const ok = await copyText(b.dataset.copy);
      b.textContent = ok ? 'copied' : 'failed'; b.classList.toggle('ok', ok);
      showToast(ok ? 'Copied to clipboard' : 'Copy failed — select and copy manually');
      setTimeout(() => { b.textContent = 'copy'; b.classList.remove('ok'); }, 1500);
    });
    $('#cs-list').addEventListener('toggle', e => {
      const d = e.target; if (!d.matches || !d.matches('details.sheet')) return;
      d.open ? openSheets.add(d.dataset.id) : openSheets.delete(d.dataset.id);
    }, true);
    window.addEventListener('beforeprint', () => $$('#cs-list details').forEach(d => d.open = true));
    $('#cs-print').addEventListener('click', () => window.print());
    renderSheets();
  }

  /* ---------- jobs ---------- */
  function renderJobs(d) {
    $('#jobs').innerHTML = d.jobs.map(j => `
      <article class="card job reveal">
        <span class="tag p">${esc(j.team)}</span>
        <h3 style="margin-top:10px">${esc(j.title)}</h3>
        <p class="sum">${esc(j.summary)}</p>
        <h4>Key skills</h4><div class="tags">${j.skills.map(s => `<span class="tag">${esc(s)}</span>`).join('')}</div>
        <h4>Certs to consider</h4><div class="tags">${j.entry.map(s => `<span class="tag g">${esc(s)}</span>`).join('')}</div>
        <h4>First steps</h4><ol>${j.first.map(s => `<li>${esc(s)}</li>`).join('')}</ol>
      </article>`).join('');
    $('#jobs-note').textContent = d.note;
    observe($('#careers'));
  }

  /* ---------- awareness ---------- */
  function renderAwareness(d) {
    $('#scams').innerHTML = d.scams.map(s => `
      <article class="card scam reveal">
        <h3><span aria-hidden="true" class="mono" style="color:var(--green-2)">${esc(s.icon)}</span> ${esc(s.title)}</h3>
        <p class="how">${esc(s.how)}</p>
        <h4 class="flag">Red flags</h4><ul class="dash">${s.flags.map(f => `<li>${esc(f)}</li>`).join('')}</ul>
        <h4 class="do">What to do</h4><ul class="dash">${s.do.map(f => `<li>${esc(f)}</li>`).join('')}</ul>
      </article>`).join('');
    $('#habits').innerHTML = `<h3>8 habits that stop most attacks</h3><ul class="dash">${d.habits.map(h => `<li>${esc(h)}</li>`).join('')}</ul>`;
    observe($('#awareness'));
  }

  /* ---------- about ---------- */
  function renderAbout(d) {
    $('#about-bio').textContent = d.bio;
    $('#about-links').innerHTML = d.links.map(l => l.url
      ? `<li><a href="${esc(l.url)}" ${l.url.startsWith('http') ? 'target="_blank" rel="noopener"' : ''}><span>${esc(l.label)}</span><span class="muted small">${esc(l.display || '↗')}</span></a></li>`
      : `<li><a class="todo" aria-disabled="true"><span>${esc(l.label)}</span><span class="small mono">${esc(l.todo || 'TODO')}</span></a></li>`).join('');
    $('#timeline').innerHTML = d.timeline.map(t => `
      <li class="reveal${t.now ? ' now' : ''}"><span class="when">${esc(t.when)}</span><h3>${esc(t.title)}</h3><p>${esc(t.body)}</p></li>`).join('');
    $('#projects').innerHTML = d.projects.map(p => `
      <article class="card project reveal"><h3>${p.url ? `<a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.name)} ↗</a>` : esc(p.name)}</h3>
        <p>${esc(p.body)}</p><div class="tags" style="display:flex;gap:6px;flex-wrap:wrap">${p.tags.map(t => `<span class="tag">${esc(t)}</span>`).join('')}</div>
        ${p.todo ? `<p class="small mono muted" style="margin-top:10px">${esc(p.todo)}</p>` : ''}</article>`).join('');
    observe($('#about'));
  }

  /* ---------- forms ---------- */
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  function wireForm(form, path, collect, validate) {
    const status = $('.form-status', form);
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const data = collect(form);
      const problem = validate(data);
      status.className = 'form-status small';
      if (problem) { status.textContent = problem; status.classList.add('err'); return; }
      if (!API) { status.textContent = 'Signup backend is not connected yet — please email madhavpandya@zoho.in.'; status.classList.add('err'); return; }
      const btn = $('button[type="submit"]', form); btn.disabled = true;
      try {
        const r = await fetch(API + path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        const j = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(j.error || `Request failed (${r.status})`);
        status.textContent = j.message || 'Done!'; status.classList.add('ok'); form.reset();
      } catch (ex) {
        status.textContent = ex.message === 'Failed to fetch' ? 'Could not reach the server. Please try again later or email madhavpandya@zoho.in.' : ex.message;
        status.classList.add('err');
      } finally { btn.disabled = false; }
    });
  }
  wireForm($('#newsletter-form'), '/api/subscribe',
    f => ({ email: f.email.value.trim(), website: f.website.value }),
    d => EMAIL_RE.test(d.email) ? '' : 'Please enter a valid email address.');
  wireForm($('#contact-form'), '/api/contact',
    f => ({ name: f.name.value.trim(), email: f.email.value.trim(), message: f.message.value.trim(), website: f.website.value }),
    d => !d.name ? 'Please enter your name.' : !EMAIL_RE.test(d.email) ? 'Please enter a valid email address.'
      : d.message.length < 10 ? 'Message should be at least 10 characters.' : '');

  /* ---------- boot ---------- */
  observe();
  const jobs = [
    ['roadmap', renderRoadmap], ['networking', renderNetworking], ['cheatsheets', renderCheatsheets],
    ['jobs', renderJobs], ['awareness', renderAwareness], ['about', renderAbout]
  ];
  Promise.allSettled(jobs.map(([n, fn]) => load(n).then(fn))).then(res => {
    res.forEach((r, i) => { if (r.status === 'rejected') console.warn('[cwm] failed to load', jobs[i][0], r.reason); });
    document.documentElement.classList.add('ready');
  });
})();
