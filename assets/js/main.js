/* CyberWithMadhav: vanilla JS. Content lives in /data/*.json */
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
      // v3: stagger items that enter together so grids cascade in.
      let n = 0;
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        e.target.style.setProperty('--rd', Math.min(n++, 6) * 70 + 'ms');
        e.target.classList.add('in'); io.unobserve(e.target);
        const t = e.target; setTimeout(() => t.style.removeProperty('--rd'), 1300);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  }
  function observe(root = document) {
    $$('.reveal:not(.in)', root).forEach(el => io ? io.observe(el) : el.classList.add('in'));
  }

  /* ---------- toast + copy ---------- */
  // Toast is hidden (display:none via [hidden]) on load and only shown on demand.
  const toast = $('#toast');
  let toastT;
  function showToast(msg) {
    toast.textContent = msg; toast.hidden = false;
    requestAnimationFrame(() => toast.classList.add('show'));
    clearTimeout(toastT);
    toastT = setTimeout(() => { toast.classList.remove('show'); setTimeout(() => { if (!toast.classList.contains('show')) { toast.hidden = true; toast.textContent = ''; } }, 300); }, 2200);
  }
  const live = $('#sr-live');
  function announce(msg) { live.textContent = ''; setTimeout(() => live.textContent = msg, 30); }
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

  // Theme toggle, starfield, warp jumps and back-to-top live in space.js (v3).
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
      throw new Error('Each octet must be 0 to 255 without leading zeros.');
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

  let csResolve; const csReady = new Promise(r => { csResolve = r; setTimeout(r, 4000); });
  /* ---------- variables (editable placeholders) ---------- */
  let varDefs = [], vars = {};
  const VAR_KEY = 'cwm-vars';
  function loadVars() {
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem(VAR_KEY) || '{}') || {}; } catch (e) { saved = {}; }
    vars = {};
    varDefs.forEach(v => { const s = typeof saved[v.key] === 'string' ? saved[v.key].trim().slice(0, 80) : ''; vars[v.key] = s || v.default; });
  }
  function saveVars() {
    const out = {};
    varDefs.forEach(v => { if (vars[v.key] !== v.default) out[v.key] = vars[v.key]; });
    try { Object.keys(out).length ? localStorage.setItem(VAR_KEY, JSON.stringify(out)) : localStorage.removeItem(VAR_KEY); } catch (e) {}
  }
  const subst = (tpl) => String(tpl).replace(/\{\{([A-Z_]+)\}\}/g, (m, k) => (k in vars ? vars[k] : m));
  window.cwmSubst = subst;
  const varListeners = [];
  function renderVarFields() {
    $('#vars-fields').innerHTML = varDefs.map(v => `
      <label class="var-field"><span>${esc(v.label)} <small class="muted">${esc(v.hint || '')}</small></span>
        <input class="mono" type="text" name="${esc(v.key)}" data-var="${esc(v.key)}" value="${esc(vars[v.key])}" placeholder="${esc(v.default)}" maxlength="80" spellcheck="false" autocomplete="off"></label>`).join('');
  }
  function onVarsChanged() { saveVars(); varListeners.forEach(fn => fn()); }

  /* ---------- cheat sheets ---------- */
  const LIMIT = 8;
  let sheets = [], flagGloss = {}, activeCat = 'All';
  const openSheets = new Set(), expanded = new Set();
  const reEsc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  function hl(text, terms) {
    text = String(text);
    if (!terms || !terms.length) return esc(text);
    const re = new RegExp('(' + terms.map(reEsc).join('|') + ')', 'gi');
    return text.split(re).map((p, i) => i % 2 ? `<mark>${esc(p)}</mark>` : esc(p)).join('');
  }
  function renderCmd(tpl, sheetId, terms) {
    const gl = flagGloss[sheetId] || {};
    return String(tpl).split(/(\{\{[A-Z_]+\}\})/).map(part => {
      const m = part.match(/^\{\{([A-Z_]+)\}\}$/);
      if (m) return `<span class="var" title="Your value. Edit it in “Your values”">${hl(vars[m[1]] ?? part, terms)}</span>`;
      return part.split(/(\s+)/).map(tok => gl[tok]
        ? `<button type="button" class="flag" aria-expanded="false">${hl(tok, terms)}<span class="tip" role="tooltip">${esc(gl[tok])}</span></button>`
        : hl(tok, terms)).join('');
    }).join('');
  }
  function renderSheets() {
    const q = $('#cs-search').value.trim();
    const ql = q.toLowerCase();
    const terms = q ? q.split(/\s+/).filter(Boolean) : [];
    let shown = 0, cmds = 0;
    const wide = window.matchMedia('(min-width: 821px)').matches;
    const html = sheets.filter(s => activeCat === 'All' || s.category === activeCat).map(s => {
      const titleHit = !ql || s.title.toLowerCase().includes(ql) || s.category.toLowerCase().includes(ql);
      const items = s.items.filter(it => titleHit || (subst(it.cmd) + ' ' + it.what).toLowerCase().includes(ql));
      if (!items.length) return '';
      shown++; cmds += items.length;
      const text = s.type === 'text';
      const open = q || wide || openSheets.has(s.id);
      const capped = !q && !expanded.has(s.id) && items.length > LIMIT + 1;
      const vis = capped ? items.slice(0, LIMIT) : items;
      const more = !q && items.length > LIMIT + 1
        ? `<button type="button" class="more" data-sheet="${esc(s.id)}" aria-expanded="${!capped}">${capped ? `Show all ${items.length} →` : 'Show fewer ↑'}</button>` : '';
      return `<details class="card sheet" data-id="${esc(s.id)}" id="sheet-${esc(s.id)}"${open ? ' open' : ''}>
        <summary><h3>${hl(s.title, terms)} <span class="tag">${esc(s.category)}</span></h3></summary>
        <p class="desc">${esc(s.desc)}</p>
        ${vis.map(it => `<div class="cmd${text ? ' text' : ' copyable'}"${text ? '' : ` data-tpl="${esc(it.cmd)}"`}>
          <code>${text ? hl(it.cmd, terms) : renderCmd(it.cmd, s.id, terms)}</code><span class="what">${hl(it.what, terms)}</span>
          ${text ? '' : `<button class="copy" type="button" aria-label="Copy command: ${esc(subst(it.cmd))}">copy</button>`}
        </div>`).join('')}
        ${more}
      </details>`;
    }).join('');
    $('#cs-list').innerHTML = html || `<div class="empty card">No matches for “${esc(q)}”. Try another keyword.</div>`;
    $('#cs-count').textContent = `${shown} sheet${shown === 1 ? '' : 's'} · ${cmds} entr${cmds === 1 ? 'y' : 'ies'}`;
  }
  async function copyRow(row) {
    const b = $('.copy', row); if (!b) return;
    const ok = await copyText(subst(row.dataset.tpl));
    b.textContent = ok ? 'copied ✓' : 'failed'; b.classList.toggle('ok', ok); row.classList.toggle('copied', ok);
    if (ok) announce('Copied to clipboard'); else showToast('Copy failed. Select the text and copy it manually.');
    clearTimeout(b._t); b._t = setTimeout(() => { b.textContent = 'copy'; b.classList.remove('ok'); row.classList.remove('copied'); }, 1500);
  }
  function closeTips(except) { $$('.flag[aria-expanded="true"]').forEach(f => { if (f !== except) f.setAttribute('aria-expanded', 'false'); }); }
  function setCat(cat) {
    activeCat = cat;
    $$('#cs-filters .chip').forEach(c => c.setAttribute('aria-pressed', c.dataset.cat === cat));
    renderSheets();
  }
  function renderCheatsheets(d) {
    sheets = d.sheets; flagGloss = d.flags || {}; varDefs = d.variables || [];
    loadVars(); renderVarFields();
    const cats = ['All', ...new Set(sheets.map(s => s.category))];
    $('#cs-filters').innerHTML = cats.map(c => `<button type="button" class="chip" aria-pressed="${c === 'All'}" data-cat="${esc(c)}">${esc(c)}</button>`).join('');
    $('#cs-filters').addEventListener('click', e => { const b = e.target.closest('.chip'); if (b) setCat(b.dataset.cat); });
    let t; $('#cs-search').addEventListener('input', () => { clearTimeout(t); t = setTimeout(renderSheets, 80); });
    $('#cs-list').addEventListener('click', e => {
      const flag = e.target.closest('.flag');
      if (flag) { e.preventDefault(); e.stopPropagation(); const open = flag.getAttribute('aria-expanded') !== 'true'; closeTips(flag); flag.setAttribute('aria-expanded', String(open)); return; }
      closeTips();
      const more = e.target.closest('.more');
      if (more) { const id = more.dataset.sheet; expanded.has(id) ? expanded.delete(id) : expanded.add(id); renderSheets(); const nb = $(`.more[data-sheet="${id}"]`); if (nb) nb.focus(); return; }
      const row = e.target.closest('.cmd.copyable'); if (!row) return;
      if (!e.target.closest('.copy') && String(window.getSelection && window.getSelection()).length) return;
      copyRow(row);
    });
    document.addEventListener('click', e => { if (!e.target.closest('.flag')) closeTips(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeTips(); });
    $('#cs-list').addEventListener('toggle', e => {
      const d = e.target; if (!d.matches || !d.matches('details.sheet')) return;
      d.open ? openSheets.add(d.dataset.id) : openSheets.delete(d.dataset.id);
    }, true);
    $('#vars-toggle').addEventListener('click', () => {
      const p = $('#vars-panel'); p.hidden = !p.hidden; $('#vars-toggle').setAttribute('aria-expanded', String(!p.hidden));
      if (!p.hidden) $('input', p).focus();
    });
    $('#vars-fields').addEventListener('input', e => {
      const i = e.target.closest('input[data-var]'); if (!i) return;
      const def = varDefs.find(v => v.key === i.dataset.var);
      vars[i.dataset.var] = i.value.trim().slice(0, 80) || def.default;
      clearTimeout(t); t = setTimeout(onVarsChanged, 120);
    });
    $('#vars-panel').addEventListener('submit', e => e.preventDefault());
    $('#vars-reset').addEventListener('click', () => { varDefs.forEach(v => vars[v.key] = v.default); renderVarFields(); onVarsChanged(); });
    varListeners.push(renderSheets);
    { const q0 = new URLSearchParams(location.search).get('q'); if (q0) setTimeout(() => jumpToCommand(q0.slice(0, 120)), 0); } // deep link from site search: index.html?q=cmd#cheatsheets
    window.addEventListener('beforeprint', () => { document.body.classList.add('printing'); $$('#cs-list details').forEach(d => d.open = true); sheets.forEach(s => expanded.add(s.id)); renderSheets(); $$('#cs-list details').forEach(d => d.open = true); });
    window.addEventListener('afterprint', () => { document.body.classList.remove('printing'); expanded.clear(); renderSheets(); });
    $('#cs-print').addEventListener('click', () => window.print());
    renderSheets();
    const entries = sheets.reduce((n, s) => n + s.items.length, 0);
    setCount('entries', entries); setCount('sheets', sheets.length);
    addPalette(sheets.map(s => ({ kind: 'Sheet', label: s.title, sub: s.category, run: () => openSheet(s.id) })));
    csResolve();
    addPalette(sheets.flatMap(s => s.type === 'text' ? [] : s.items.map(it => ({ kind: 'Command', label: () => subst(it.cmd), sub: it.what, run: () => jumpToCommand(subst(it.cmd)) }))));
  }
  function setCount(k, n) { $$(`[data-count="${k}"]`).forEach(el => el.textContent = n.toLocaleString('en-IN')); }
  function openSheet(id) {
    $('#cs-search').value = ''; setCat('All');
    const d = $(`#sheet-${id}`); if (!d) return;
    d.open = true; openSheets.add(id);
    d.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
    $('summary', d).focus({ preventScroll: true });
  }
  function jumpToCommand(cmd) {
    setCat('All'); $('#cs-search').value = cmd; renderSheets();
    $('#cheatsheets').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
    const row = $('#cs-list .cmd.copyable'); if (row) { row.classList.add('flash'); const b = $('.copy', row); if (b) b.focus({ preventScroll: true }); }
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
    renderQuiz(d.quiz);
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
    if (d.headline) $('#about-title').textContent = d.headline;
    $('#about-bio').textContent = d.bio;
    // Links without a URL (e.g. Instagram/YouTube not set yet) are simply not shown.
    const fl = $('#follow-links');
    if (fl) fl.innerHTML = d.links.filter(l => /^(Instagram|YouTube)$/.test(l.label)).map(l => /^https:\/\//.test(l.url)
      ? `<li><a href="${esc(l.url)}" target="_blank" rel="noopener"><span>Follow on ${esc(l.label)}</span><span class="muted small">↗</span></a></li>`
      : `<li><span class="soon"><span>${esc(l.label)}</span><span class="muted small">coming soon</span></span></li>`).join('');
    $('#about-links').innerHTML = d.links.filter(l => l.url).map(l =>
      `<li><a href="${esc(l.url)}" ${l.url.startsWith('http') ? 'target="_blank" rel="noopener"' : ''}><span>${esc(l.label)}</span><span class="muted small">${esc(l.display || '↗')}</span></a></li>`).join('');
    $('#timeline').innerHTML = d.timeline.map(t => `
      <li class="reveal${t.now ? ' now' : ''}${t.law ? ' law-item' : ''}"><span class="when">${esc(t.when)}${t.now ? ' <span class="live">live</span>' : ''}</span>
        <h3>${esc(t.title)}${t.law ? ' <a class="tag law-tag" href="#law">cyber law · GRC ↓</a>' : ''}</h3><p>${esc(t.body)}</p>
        ${t.metric ? `<p class="metric mono">${esc(t.metric)}</p>` : ''}</li>`).join('');
    const lc = d.lawCallout;
    if (lc) $('#law').innerHTML = `<p class="kicker mono">⚖ the law angle</p><h3 id="law-title">${esc(lc.title)}</h3><p>${esc(lc.body)}</p>
      <ul class="dash">${lc.points.map(p => `<li>${esc(p)}</li>`).join('')}</ul>`;
    else $('#law').remove();
    $('#projects').innerHTML = d.projects.map(p => `
      <article class="card project reveal" data-repo="${esc(p.repo || '')}"><h3>${p.url ? `<a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.name)} ↗</a>` : esc(p.name)} <span class="stars mono" hidden></span></h3>
        <p>${esc(p.body)}</p>
        ${p.building ? `<p class="building"><span class="live">building</span> ${esc(p.building.replace(/^Now building:\s*/i, ''))}</p>` : ''}
        <div class="tags" style="display:flex;gap:6px;flex-wrap:wrap">${p.tags.map(t => `<span class="tag">${esc(t)}</span>`).join('')}</div></article>`).join('');
    observe($('#about'));
    lazyStars();
  }
  // GitHub star counts: fetched only when About is near the viewport, cached for 6h, shown only if > 0, fails silently.
  function lazyStars() {
    const cards = $$('.project[data-repo]').filter(c => c.dataset.repo);
    if (!cards.length) return;
    const run = () => cards.forEach(async c => {
      const repo = c.dataset.repo, key = 'cwm-stars:' + repo;
      let n = null;
      try { const c0 = JSON.parse(sessionStorage.getItem(key) || 'null'); if (c0 && Date.now() - c0.t < 216e5) n = c0.n; } catch (e) {}
      if (n === null) {
        try {
          const r = await fetch(`https://api.github.com/repos/${repo}`, { headers: { Accept: 'application/vnd.github+json' } });
          if (!r.ok) return;
          n = (await r.json()).stargazers_count;
          try { sessionStorage.setItem(key, JSON.stringify({ n, t: Date.now() })); } catch (e) {}
        } catch (e) { return; }
      }
      if (typeof n === 'number' && n > 0) { const s = $('.stars', c); s.textContent = `★ ${n.toLocaleString('en-IN')}`; s.title = `${n} GitHub stars`; s.hidden = false; }
    });
    if (!('IntersectionObserver' in window)) return run();
    const o = new IntersectionObserver(es => { if (es.some(x => x.isIntersecting)) { o.disconnect(); run(); } }, { rootMargin: '600px 0px' });
    o.observe($('#projects'));
  }

  /* ---------- banner ---------- */
  $('.alert-close').addEventListener('click', () => {
    document.documentElement.classList.add('no-banner');
    try { sessionStorage.setItem('cwm-banner', 'hidden'); } catch (e) {}
    $('.brand').focus();
  });

  /* ---------- hero: whoami typing ---------- */
  (function whoami() {
    const out = $('#who-out'), h1 = $('#hero-title'), full = out.textContent;
    if (reduced) { h1.classList.add('in'); return; }
    out.textContent = ''; h1.classList.add('pre');
    let i = 0;
    const step = () => {
      out.textContent = full.slice(0, ++i);
      if (i < full.length) setTimeout(step, 38);
      else setTimeout(() => { h1.classList.add('in'); h1.classList.remove('pre'); $('#whoami').classList.add('done'); }, 180);
    };
    setTimeout(step, 250);
  })();

  /* ---------- hero: terminal card ---------- */
  let termDemo = null, termTyped = false;
  function termHTML(upto) {
    const lines = [`<span class="t-prompt">$</span> ${esc(subst(termDemo.cmd))}`,
      ...termDemo.lines.map(l => esc(subst(l)).replace(/\bopen\b/g, '<span class="t-open">open</span>'))];
    return lines.slice(0, upto).join('\n');
  }
  function renderTerm(animate) {
    const pre = $('#term-out'); if (!termDemo) return;
    const total = termDemo.lines.length + 1;
    if (!animate || reduced) { pre.innerHTML = termHTML(total); return; }
    let n = 0;
    const tick = () => { pre.innerHTML = termHTML(++n) + (n < total ? '\n<span class="cursor">▌</span>' : ''); if (n < total) setTimeout(tick, n === 1 ? 700 : 260); };
    tick();
  }
  function renderTools(d) {
    termDemo = d.terminalDemo;
    renderTerm(!termTyped); termTyped = true;
    varListeners.push(() => renderTerm(false));
    if (d.note) $('#tools-note').textContent = d.note;
    if (d.hashNote) $('#hash-note').textContent = 'Paste a hash to guess its type. ' + d.hashNote;
    toolData = d;
    $('#link-checklist').innerHTML = d.checklist.map((c, i) => `<label class="chk"><input type="checkbox" value="${i}"> <span>${esc(c)}</span></label>`).join('');
    $('#link-checklist').addEventListener('change', () => {
      const n = $$('#link-checklist input:checked').length, o = $('#checklist-out');
      o.className = 'small ' + (n >= 3 ? 'bad' : n ? 'warn' : '');
      o.innerHTML = n === 0 ? 'Nothing ticked. If you\'re still unsure, open the official app or website yourself instead of the link.'
        : n < 3 ? `<b>${n} red flag${n > 1 ? 's' : ''}.</b> Be careful: verify through the official app, website or helpline before you do anything.`
        : `<b>${n} red flags. Treat it as a scam.</b> Don't click, pay or share OTPs. Report it at <a href="https://cybercrime.gov.in" target="_blank" rel="noopener">cybercrime.gov.in</a> or call <a href="tel:1930">1930</a>, and report fraud messages on <a href="https://sancharsaathi.gov.in" target="_blank" rel="noopener">Sanchar Saathi (Chakshu)</a>.`;
    });
    setCount('tools', $$('#tools .tool').length);
    runLink(); runHash();
  }
  (function termTabs() {
    const tabs = $$('#term [role="tab"]');
    const sel = (t) => { tabs.forEach(b => { const on = b === t; b.setAttribute('aria-selected', on); b.tabIndex = on ? 0 : -1; $('#' + b.getAttribute('aria-controls')).hidden = !on; }); };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => sel(t));
      t.addEventListener('keydown', e => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { const n = tabs[(i + 1) % tabs.length]; n.focus(); sel(n); } });
    });
  })();

  /* ---------- hero: scam or not? ---------- */
  let quiz = [], qi = 0, qRight = 0, qDone = 0;
  function showQuiz() {
    const q = quiz[qi % quiz.length];
    $('#quiz-n').textContent = `message ${qi % quiz.length + 1}/${quiz.length}${qDone ? ` · score ${qRight}/${qDone}` : ''}`;
    $('#quiz-msg').textContent = q.msg;
    $('#quiz-why').textContent = ''; $('#quiz-why').className = 'quiz-why';
    $$('.quiz-btns button').forEach(b => b.disabled = false);
    $('#quiz-next').hidden = true;
  }
  function renderQuiz(list) {
    quiz = list || []; if (!quiz.length) { $('#tt-quiz').remove(); return; }
    showQuiz();
    $('.quiz-btns').addEventListener('click', e => {
      const b = e.target.closest('button[data-answer]'); if (!b) return;
      const q = quiz[qi % quiz.length], right = (b.dataset.answer === 'scam') === q.scam;
      qDone++; if (right) qRight++;
      $$('.quiz-btns button').forEach(x => x.disabled = true);
      const w = $('#quiz-why'); w.className = 'quiz-why ' + (right ? 'ok' : 'bad');
      w.textContent = `${right ? '✓ Right' : '✗ Not quite'}: ${q.scam ? 'scam' : 'looks legit'}. ${q.why}`;
      $('#quiz-n').textContent = `message ${qi % quiz.length + 1}/${quiz.length} · score ${qRight}/${qDone}`;
      $('#quiz-next').hidden = false; $('#quiz-next').focus();
    });
    $('#quiz-next').addEventListener('click', () => { qi++; showQuiz(); $('.quiz-btns button').focus(); });
  }

  /* ---------- tool: password strength (client-side only, never stored) ---------- */
  let toolData = { commonPasswords: [], keyboardRows: [], link: { shorteners: [], riskyTlds: [], brands: {}, lureWords: [] } };
  function fmtTime(sec) {
    if (sec < 1) return 'instantly';
    const u = [['century', 3.156e9], ['year', 3.156e7], ['month', 2.63e6], ['day', 86400], ['hour', 3600], ['minute', 60], ['second', 1]];
    if (sec >= 3.156e11) return 'centuries+';
    for (const [n, s] of u) if (sec >= s) { const v = Math.round(sec / s); return `${v} ${n === 'century' ? (v > 1 ? 'centuries' : 'century') : n + (v > 1 ? 's' : '')}`; }
    return 'instantly';
  }
  function pwStrength(pw) {
    if (!pw) return null;
    const chars = [...pw], len = chars.length;
    let pool = 0;
    if (/[a-z]/.test(pw)) pool += 26; if (/[A-Z]/.test(pw)) pool += 26; if (/\d/.test(pw)) pool += 10;
    if (/[^a-zA-Z0-9]/.test(pw) && /[\x20-\x7e]/.test(pw.replace(/[a-zA-Z0-9]/g, ''))) pool += 33;
    if (/[^\x00-\x7f]/.test(pw)) pool += 100;
    const bpc = Math.log2(Math.max(pool, 2));
    let bits = len * bpc;
    const warn = [], lower = pw.toLowerCase();
    const deleet = lower.replace(/0/g, 'o').replace(/[4@]/g, 'a').replace(/3/g, 'e').replace(/[1!|]/g, 'i').replace(/[5$]/g, 's').replace(/7/g, 't');
    const common = (toolData.commonPasswords || []).map(s => s.toLowerCase());
    const core = lower.replace(/[^a-z0-9@]+$/, '').replace(/\d+$/, '');
    if (common.includes(lower) || common.includes(deleet) || (core.length >= 4 && common.includes(core))) { bits = Math.min(bits, 6); warn.push('This is one of the most common passwords. Attackers try these first.'); }
    else {
      common.filter(w => w.length >= 5).forEach(w => { if (lower.includes(w) || deleet.includes(w) || deleet.replace(/i/g, 'l').includes(w)) { bits -= (w.length - 1) * bpc - 10; warn.push(`Contains a very common password (“${w}”).`); } });
      (lower.match(/(.)\1{2,}/g) || []).forEach(r => { bits -= (r.length - 1) * bpc; warn.push('Repeated characters (like “aaa”) add almost nothing.'); });
      let run = 1;
      for (let i = 1; i <= chars.length; i++) {
        const d = i < chars.length ? chars[i].charCodeAt(0) - chars[i - 1].charCodeAt(0) : 99;
        const prev = i > 1 ? chars[i - 1].charCodeAt(0) - chars[i - 2].charCodeAt(0) : 0;
        if (Math.abs(d) === 1 && (run === 1 || d === prev)) run++;
        else { if (run >= 3) { bits -= (run - 1) * bpc; warn.push('Sequences like “abc” or “123” are guessed early.'); } run = 1; if (Math.abs(d) === 1) run = 2; }
      }
      (toolData.keyboardRows || []).forEach(row => {
        for (let k = 4; k <= row.length; k++) for (let s = 0; s + k <= row.length; s++) {
          const sub = row.slice(s, s + k);
          if (k === row.length || !lower.includes(row.slice(s, s + k + 1))) if (lower.includes(sub) || lower.includes([...sub].reverse().join(''))) { if (k >= 4 && !warn.includes('Keyboard patterns like “qwerty” are in every wordlist.')) { bits -= (k - 1) * bpc; warn.push('Keyboard patterns like “qwerty” are in every wordlist.'); } }
        }
      });
      if (/(19|20)\d{2}/.test(pw)) { bits -= 4 * bpc - 7; warn.push('Years and dates (birthdays!) are easy to guess.'); }
      if (/^\d+$/.test(pw) && len <= 12) warn.push('Only digits: phone numbers and dates are tried quickly.');
    }
    bits = Math.max(0, Math.round(bits));
    if (len < 8) warn.push('Too short. Aim for at least 12 characters, or 4+ random words.');
    const guesses = Math.pow(2, Math.max(bits - 1, 0));
    const score = bits < 28 ? 0 : bits < 36 ? 1 : bits < 60 ? 2 : bits < 80 ? 3 : 4;
    return { bits, score, label: ['Very weak', 'Weak', 'Fair', 'Strong', 'Very strong'][score],
      online: fmtTime(guesses / 10), offline: fmtTime(guesses / 1e10), warnings: [...new Set(warn)] };
  }
  window.cwmPassword = pwStrength;
  function runPw() {
    const r = pwStrength($('#pw-input').value), out = $('#pw-out'), bar = $('#pw-bar');
    if (!r) { out.innerHTML = ''; bar.style.width = '0'; bar.dataset.score = ''; return; }
    bar.style.width = Math.min(100, Math.max(6, r.bits)) + '%'; bar.dataset.score = r.score;
    out.innerHTML = `<p class="pw-label s${r.score}"><b>${r.label}</b> <span class="muted">· about ${r.bits} bits of entropy</span></p>
      <dl class="kv"><div><dt>Online attack (10 guesses/s)</dt><dd>${esc(r.online)}</dd></div><div><dt>Offline, fast hash (10 billion/s)</dt><dd>${esc(r.offline)}</dd></div></dl>
      ${r.warnings.length ? `<ul class="dash small">${r.warnings.map(w => `<li>${esc(w)}</li>`).join('')}</ul>` : '<p class="small muted">No obvious patterns found. Use a password manager so it stays unique.</p>'}`;
  }
  $('#pw-input').addEventListener('input', runPw);
  $('#pw-show').addEventListener('click', () => {
    const i = $('#pw-input'), show = i.type === 'password';
    i.type = show ? 'text' : 'password'; $('#pw-show').textContent = show ? 'Hide' : 'Show'; $('#pw-show').setAttribute('aria-pressed', String(show));
  });
  window.addEventListener('pagehide', () => { $('#pw-input').value = ''; });

  /* ---------- tool: hash identifier ---------- */
  function hashId(input) {
    const s = String(input || '').trim();
    if (!s) return null;
    const C = (name, mode, note) => ({ name, mode, note });
    const rules = [
      [/^\$2[abxy]\$\d{2}\$[./A-Za-z0-9]{53}$/, [C('bcrypt', 3200, 'Slow, salted. Common in web apps.')]],
      [/^\$2[abxy]\$/, [C('bcrypt (unusual length)', 3200)]],
      [/^\$argon2(id|i|d)\$/, [C('Argon2', null, 'Modern, memory-hard password hash.')]],
      [/^\$y\$/, [C('yescrypt', null, 'Default in /etc/shadow on recent Debian, Ubuntu and Kali.')]],
      [/^\$6\$/, [C('SHA-512 crypt', 1800, 'Linux /etc/shadow.')]],
      [/^\$5\$/, [C('SHA-256 crypt', 7400, 'Linux /etc/shadow.')]],
      [/^\$apr1\$/, [C('Apache APR1-MD5', 1600, '.htpasswd files.')]],
      [/^\$1\$/, [C('MD5 crypt', 500, 'Old Linux / Cisco.')]],
      [/^\$[PH]\$/, [C('phpass', 400, 'WordPress, phpBB.')]],
      [/^pbkdf2_sha256\$/, [C('Django PBKDF2-SHA256', 10000)]],
      [/^\{SSHA\}/i, [C('LDAP salted SHA-1 (SSHA)', 111)]],
      [/^\{SHA\}/i, [C('LDAP SHA-1', 101)]],
      [/^\*[0-9A-F]{40}$/i, [C('MySQL 4.1+', 300)]],
      [/^eyJ[\w-]*\.[\w-]*\.[\w-]*$/, [C('JWT (JSON Web Token)', null, 'Not a hash: a signed token. Its first two parts are just Base64 you can decode.')]],
      [/^[0-9a-f]{32}:[0-9a-f]{32}$/i, [C('LM:NTLM pair (pwdump format)', 1000, 'The right half is the NTLM hash.')]]
    ];
    for (const [re, c] of rules) if (re.test(s)) return { input: s, length: s.length, charset: 'prefix', candidates: c };
    if (/^[0-9a-f]+$/i.test(s)) {
      const byLen = {
        8: [C('CRC32', 11500), C('Adler-32')],
        16: [C('MySQL 3.x (OLD_PASSWORD)', 200), C('Half of an LM hash')],
        32: [C('MD5', 0), C('NTLM', 1000, 'Windows. Same length as MD5, so context decides (e.g. from a SAM/NTDS dump = NTLM).'), C('MD4', 900), C('LM', 3000)],
        40: [C('SHA-1', 100), C('RIPEMD-160', 6000)],
        56: [C('SHA-224', 1300), C('SHA3-224')],
        64: [C('SHA-256', 1400), C('SHA3-256', 17400), C('BLAKE2s-256')],
        96: [C('SHA-384', 10800), C('SHA3-384')],
        128: [C('SHA-512', 1700), C('SHA3-512', 17600), C('BLAKE2b-512', 600), C('Whirlpool', 6100)]
      }[s.length];
      return { input: s, length: s.length, charset: 'hex', candidates: byLen || [] };
    }
    if (/^[A-Za-z0-9+/]+={0,2}$/.test(s) && s.length % 4 === 0) {
      const bytes = s.length / 4 * 3 - (s.match(/=*$/)[0].length);
      const m = { 16: 'MD5 / NTLM', 20: 'SHA-1', 32: 'SHA-256', 64: 'SHA-512' }[bytes];
      return { input: s, length: s.length, charset: 'base64', candidates: m ? [C(`Base64-encoded ${bytes}-byte digest (${m}?)`)] : [] };
    }
    return { input: s, length: s.length, charset: 'mixed', candidates: [] };
  }
  window.cwmHashId = hashId;
  function runHash() {
    const r = hashId($('#hash-input').value), out = $('#hash-out');
    if (!r) { out.innerHTML = ''; return; }
    out.innerHTML = `<p class="small muted">${r.length} characters · ${esc(r.charset)}</p>` + (r.candidates.length
      ? `<ol class="cands">${r.candidates.map((c, i) => `<li><b>${esc(c.name)}</b>${i === 0 && r.candidates.length > 1 ? ' <span class="muted small">(most likely)</span>' : ''}${c.mode != null ? ` <code>hashcat -m ${c.mode}</code>` : ''}${c.note ? `<br><span class="small muted">${esc(c.note)}</span>` : ''}</li>`).join('')}</ol>`
      : '<p class="small">No match. Check for extra spaces, or a salt glued on with “:”.</p>');
  }
  $('#hash-input').addEventListener('input', runHash);

  /* ---------- tool: link analyzer (never opens the link) ---------- */
  function linkCheck(raw) {
    let s = String(raw || '').trim();
    if (!s) return null;
    const f = [], add = (level, text) => f.push({ level, text });
    const hasScheme = /^[a-z][a-z0-9+.-]*:/i.test(s);
    let u;
    try { u = new URL(hasScheme ? s : 'http://' + s); } catch (e) { return { error: 'That doesn\'t look like a link.', findings: [], verdict: 'unknown' }; }
    const L = toolData.link || {};
    if (!/^https?:$/.test(u.protocol)) add('high', `Uses “${u.protocol}” instead of a normal web link.`);
    else if (hasScheme && u.protocol === 'http:') add('med', 'Not HTTPS: anything you type can be read in transit.');
    const host = u.hostname.toLowerCase().replace(/\.$/, '');
    const authority = s.replace(/^[a-z][a-z0-9+.-]*:\/\//i, '').split(/[/?#]/)[0];
    if (u.username || u.password || authority.includes('@')) add('high', `Contains “@”: everything before it is ignored. The real site is ${host}.`);
    const authHost = authority.split('@').pop().replace(/:\d+$/, '');
    if (/^\[.*\]$/.test(host) || /^\d{1,3}(\.\d{1,3}){3}$/.test(host)) add('high', /^\d+$/.test(authHost) || /^0x/i.test(authHost) ? `Disguised IP address (decodes to ${host}) instead of a domain name.` : 'Uses a raw IP address instead of a domain name.');
    const labels = host.split('.');
    if (labels.some(l => l.startsWith('xn--'))) add('high', 'Internationalised (punycode “xn--”) domain: letters may imitate a real site, e.g. Cyrillic “а” for Latin “a”.');
    if (labels.length >= 5) add('med', `Many subdomain levels (${labels.length}): real brand names can hide at the front.`);
    const tld = labels[labels.length - 1];
    if ((L.riskyTlds || []).includes(tld)) add('med', `“.${tld}” is a cheap domain ending that's often abused.`);
    const onDomain = (d) => host === d || host.endsWith('.' + d);
    if ((L.shorteners || []).some(onDomain)) add('med', 'Link shortener: the real destination is hidden.');
    const norm = host.replace(/0/g, 'o').replace(/1/g, 'l').replace(/3/g, 'e').replace(/5/g, 's').replace(/\$/g, 's');
    const toks = norm.split(/[.-]/);
    Object.entries(L.brands || {}).forEach(([b, official]) => {
      const hit = toks.includes(b) || (b.length >= 5 && norm.includes(b));
      if (hit && !official.some(onDomain)) add('high', `Mentions “${b}” but isn't an official ${b} domain (${official.filter(o => o.includes('.') && o !== 'bank.in').join(', ')}).`);
    });
    if ((toks.includes('gov') || toks.includes('nic')) && !/\.(gov\.in|nic\.in|gov)$/.test(host)) add('high', 'Looks like a government site but isn\'t on .gov.in / .nic.in.');
    if ((host.match(/-/g) || []).length >= 3) add('med', 'Lots of hyphens in the domain, a common lookalike trick.');
    const lures = (L.lureWords || []).filter(w => (host + u.pathname + u.search).toLowerCase().includes(w));
    if (lures.length) add(lures.length >= 2 ? 'med' : 'info', `Bait words: ${lures.slice(0, 5).join(', ')}.`);
    if (/\.apk($|[?#])/i.test(u.pathname)) add('high', 'Downloads an Android app (.apk) from outside the Play Store.');
    if (u.port) add('med', `Unusual port :${u.port}.`);
    if (s.length > 120) add('info', 'Very long link: the important part may be hidden.');
    const high = f.filter(x => x.level === 'high').length, med = f.filter(x => x.level === 'med').length;
    return { host, findings: f, verdict: high ? 'risky' : med ? 'careful' : 'clean' };
  }
  window.cwmLinkCheck = linkCheck;
  function runLink() {
    const r = linkCheck($('#link-input').value), out = $('#link-out');
    if (!r) { out.innerHTML = ''; return; }
    if (r.error) { out.innerHTML = `<p class="error">${esc(r.error)}</p>`; return; }
    const v = { risky: ['bad', 'Looks risky. Don\'t open it.'], careful: ['warn', 'Be careful. Verify before you open it.'], clean: ['ok', 'No obvious red flags. That isn\'t a guarantee, so still use the checklist.'] }[r.verdict];
    out.innerHTML = `<p class="verdict ${v[0]}"><b>${esc(v[1])}</b> <span class="muted small">host: <code>${esc(r.host)}</code></span></p>` +
      (r.findings.length ? `<ul class="findings">${r.findings.map(x => `<li class="${x.level}"><span class="lvl mono">${x.level === 'high' ? 'high' : x.level === 'med' ? 'warn' : 'info'}</span> ${esc(x.text)}</li>`).join('')}</ul>` : '');
  }
  let lt; $('#link-input').addEventListener('input', () => { clearTimeout(lt); lt = setTimeout(runLink, 120); });

  /* ---------- command palette (Ctrl/Cmd+K) ---------- */
  const palItems = [];
  function addPalette(list) { palItems.push(...list); }
  const pal = $('#palette'), palInput = $('#pal-input'), palList = $('#pal-list');
  let palRes = [], palIdx = 0;
  const scrollTo = (sel, focusSel) => () => {
    const el = $(sel); if (!el) return;
    el.dispatchEvent(new CustomEvent('cwm:show', { bubbles: true })); // tool tabs and folds open the target first
    if (window.cwmSpace) window.cwmSpace.warp(el);
    el.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
    if (focusSel) setTimeout(() => { const f = $(focusSel); if (f) f.focus({ preventScroll: true }); }, reduced ? 0 : 400);
  };
  // home sections (the top nav is short now, so list them from the page itself)
  $$('main > section[id]').forEach(sec => { const h = sec.querySelector('h2'); if (h) addPalette([{ kind: 'Section', label: h.textContent.trim(), sub: '#' + sec.id, run: scrollTo('#' + sec.id) }]); });
  addPalette([
    { kind: 'Tool', label: 'Subnet calculator', sub: 'IPv4 / CIDR', run: scrollTo('#subnet', '#subnet-input') },
    { kind: 'Tool', label: 'Password strength checker', sub: 'offline entropy estimate', run: scrollTo('#pw-tool', '#pw-input') },
    { kind: 'Tool', label: 'Hash identifier', sub: 'MD5, NTLM, SHA, bcrypt…', run: scrollTo('#hash-tool', '#hash-input') },
    { kind: 'Tool', label: 'Is this link suspicious?', sub: 'URL red flags + checklist', run: scrollTo('#link-tool', '#link-input') },
    { kind: 'Tool', label: 'Scam or not? quiz', sub: 'hero terminal', run: () => { $('#tt-quiz') && $('#tt-quiz').click(); scrollTo('.hero')(); } },
    { kind: 'Action', label: 'Set your values (IP, subnet, interface, domain)', sub: 'cheat sheets', run: () => { const p = $('#vars-panel'); if (p.hidden) $('#vars-toggle').click(); scrollTo('#cheatsheets', '#vars-fields input')(); } },
    { kind: 'Action', label: 'Scammed? Call 1930 / report online', sub: 'stay safe', run: scrollTo('#awareness') },
    { kind: 'Action', label: 'Toggle light / dark theme', sub: 'appearance', run: () => $('.theme-toggle').click() }
  ]);
  const labelOf = (it) => typeof it.label === 'function' ? it.label() : it.label;
  function palSearch() {
    const q = palInput.value.trim().toLowerCase(), words = q.split(/\s+/).filter(Boolean);
    const scored = [];
    palItems.forEach(it => {
      const lab = labelOf(it), hay = (lab + ' ' + (it.sub || '') + ' ' + it.kind + ' ' + (it.x || '')).toLowerCase();
      if (words.every(w => hay.includes(w))) {
        const ll = lab.toLowerCase();
        scored.push([it, lab, !q ? (it.kind === 'Command' ? 9 : 0) : ll.startsWith(q) ? 0 : ll.includes(q) ? 1 : 2]);
      }
    });
    scored.sort((a, b) => a[2] - b[2]);
    palRes = scored.slice(0, 40); palIdx = 0;
    palList.innerHTML = palRes.length ? palRes.map(([it, lab], i) => `<li role="option" id="pal-${i}" aria-selected="${i === 0}" data-i="${i}"><span class="k mono">${esc(it.kind)}</span><span class="l${it.kind === 'Command' ? ' mono' : ''}">${esc(lab)}</span><span class="s">${esc(it.sub || '')}</span></li>`).join('')
      : '<li class="none">No results</li>';
    palInput.setAttribute('aria-activedescendant', palRes.length ? 'pal-0' : '');
  }
  function palMove(d) {
    if (!palRes.length) return;
    palIdx = (palIdx + d + palRes.length) % palRes.length;
    $$('#pal-list [role="option"]').forEach((li, i) => li.setAttribute('aria-selected', i === palIdx));
    const li = $('#pal-' + palIdx); li.scrollIntoView({ block: 'nearest' }); palInput.setAttribute('aria-activedescendant', li.id);
  }
  function palRun(i) { const r = palRes[i]; if (!r) return; closePalette(); r[0].run(); }
  function openPalette() {
    if (pal.open) return;
    palInput.value = ''; palSearch();
    if (pal.showModal) pal.showModal(); else pal.setAttribute('open', '');
    palInput.focus();
  }
  function closePalette() { if (pal.close) pal.close(); else pal.removeAttribute('open'); }
  window.cwmPalette = { open: openPalette, close: closePalette };
  palInput.addEventListener('input', palSearch);
  palInput.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { e.preventDefault(); palMove(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); palMove(-1); }
    else if (e.key === 'Enter') { e.preventDefault(); palRun(palIdx); }
  });
  palList.addEventListener('click', e => { const li = e.target.closest('[data-i]'); if (li) palRun(Number(li.dataset.i)); });
  pal.addEventListener('click', e => { if (e.target === pal) closePalette(); });
  $('#palette-open').addEventListener('click', openPalette);
  // Site wide results (CTF, prompts, cyber law, commands, scams, legal) from the build time index data/search.json.
  fetch('data/search.json').then(r => r.ok ? r.json() : []).then(list => {
    addPalette(list.filter(it => !/^index\.html/.test(it.u)).map(it => ({ kind: it.k, label: it.t, sub: it.s, x: it.x, run: () => { location.href = it.u; } })));
    if (pal.open) palSearch();
  }).catch(() => {});

  /* ---------- keyboard shortcuts ---------- */
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && !e.altKey && e.key.toLowerCase() === 'k') { e.preventDefault(); pal.open ? closePalette() : openPalette(); return; }
    if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      const t = e.target, typing = t.closest && t.closest('input, textarea, select, [contenteditable="true"], dialog');
      if (typing) return;
      e.preventDefault();
      const s = $('#cs-search');
      s.scrollIntoView({ behavior: 'auto', block: 'center' }); s.focus({ preventScroll: true }); s.select();
    }
  });

  /* ---------- forms ---------- */
  // Contact: no backend on GitHub Pages, so compose a mailto: link the visitor sends from their own email app.
  (function wireMailto(form) {
    if (!form) return;
    const status = $('.form-status', form);
    form.addEventListener('submit', e => {
      e.preventDefault();
      status.className = 'form-status small'; status.textContent = '';
      $$('[aria-invalid]', form).forEach(x => x.removeAttribute('aria-invalid'));
      const name = form.name.value.trim(), subject = form.subject.value.trim(), msg = form.message.value.trim();
      const bad = !name ? ['name', 'Please enter your name.'] : msg.length < 10 ? ['message', 'Message should be at least 10 characters.'] : null;
      if (bad) { status.textContent = bad[1]; status.classList.add('err'); const f = form.elements[bad[0]]; f.setAttribute('aria-invalid', 'true'); f.focus(); return; }
      const href = 'mailto:madhavpandya@zoho.in?subject=' + encodeURIComponent(subject || 'Hello from CyberWithMadhav') + '&body=' + encodeURIComponent(msg + '\n\n' + name);
      form.dataset.mailto = href;
      status.textContent = 'Opening your email app. If nothing opens, email madhavpandya@zoho.in directly.'; status.classList.add('ok');
      if (!navigator.webdriver) location.href = href;
    });
  })($('#contact-form'));
  /* ---------- boot ---------- */
  observe();
  const jobs = [
    ['roadmap', renderRoadmap], ['networking', renderNetworking], ['cheatsheets', renderCheatsheets],
    ['jobs', renderJobs], ['awareness', renderAwareness], ['about', renderAbout], ['tools', d => csReady.then(() => renderTools(d))]
  ];
  Promise.allSettled(jobs.map(([n, fn]) => load(n).then(fn))).then(res => {
    res.forEach((r, i) => { if (r.status === 'rejected') console.warn('[cwm] failed to load', jobs[i][0], r.reason); });
    document.documentElement.classList.add('ready');
  });
})();
