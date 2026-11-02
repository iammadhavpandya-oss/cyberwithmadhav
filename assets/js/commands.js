/* commands.html: Command Reference. Data from data/commands.json. No innerHTML from data. */
(function () {
  'use strict';
  const { $, el, copyText, getJSON } = window.CWMP;
  const state = { os: 'all', cat: 'all', q: '' };
  let data = null, cards = [];

  const norm = s => String(s || '').toLowerCase();

  function chip(group, id, label, n) {
    return el('button', { type: 'button', class: 'chip', 'data-group': group, 'data-id': id, 'aria-pressed': String(state[group] === id) },
      [label, el('span', { class: 'n', text: String(n) })]);
  }

  function chips() {
    const cnt = (k, v) => data.commands.filter(c => c[k] === v).length;
    $('#c-os').replaceChildren(chip('os', 'all', 'All', data.commands.length), ...data.os.map(o => chip('os', o.id, o.name, cnt('os', o.id))));
    $('#c-cat').replaceChildren(chip('cat', 'all', 'All', data.commands.length), ...data.categories.map(o => chip('cat', o.id, o.name, cnt('cat', o.id))));
  }

  function field(label, text, cls) {
    return el('div', { class: 'c-field ' + (cls || '') }, [el('p', { class: 'c-k mono', text: label }), el('p', { class: 'c-v', text })]);
  }

  function card(c) {
    const osName = data.os.find(o => o.id === c.os).name, catName = data.categories.find(o => o.id === c.cat).name;
    const pid = 'cp-' + c.id;
    const copy = el('button', { type: 'button', class: 'copy', 'aria-label': 'Copy example: ' + c.example, text: 'Copy' });
    copy.addEventListener('click', () => copyText(c.example, copy));
    const more = el('button', { type: 'button', class: 'c-more', 'aria-expanded': 'false', 'aria-controls': pid }, [el('span', { text: 'Details' }), el('span', { class: 'chev', 'aria-hidden': 'true', text: '▾' })]);
    const safety = el('div', { class: 'c-safety' + (c.prominent ? ' warn' : ''), role: c.prominent ? 'note' : null }, [
      el('p', { class: 'c-k mono', text: c.prominent ? '⚠ safety: read first' : 'safety note' }), el('p', { class: 'c-v', text: c.safety })]);
    const panel = el('div', { class: 'c-panel', id: pid, hidden: true }, [
      field('typical output', c.output, 'c-out'),
      field('blue team use', c.blue),
      c.prominent ? null : safety,
      el('p', { class: 'c-doc' }, [el('a', { href: c.doc, target: '_blank', rel: 'noopener noreferrer', text: 'Official docs ↗' }), el('span', { class: 'sr-only', text: ' (opens in a new tab)' })])
    ]);
    more.addEventListener('click', () => toggle(art, more.getAttribute('aria-expanded') !== 'true'));
    const art = el('article', { class: 'c-card card', id: 'c-' + c.id, 'data-os': c.os, 'data-cat': c.cat }, [
      el('div', { class: 'c-top' }, [
        el('h3', { class: 'c-name mono', text: c.cmd }),
        el('span', { class: 'c-badges' }, [el('span', { class: 'badge os-' + c.os, text: osName }), el('span', { class: 'badge', text: catName })])
      ]),
      el('p', { class: 'c-what', text: c.what }),
      el('div', { class: 'c-ex' }, [el('code', { class: 'mono', text: c.example }), copy]),
      c.prominent ? safety : null,
      more, panel
    ]);
    art._hay = norm([c.cmd, c.what, c.example, c.output, c.blue, c.safety, osName, catName].join(' '));
    art._more = more; art._panel = panel;
    return art;
  }

  function toggle(art, open) {
    art._more.setAttribute('aria-expanded', String(open));
    art._more.firstChild.textContent = open ? 'Hide details' : 'Details';
    art._panel.hidden = !open; art.classList.toggle('open', open);
  }

  function apply() {
    const toks = norm(state.q).split(/\s+/).filter(Boolean);
    let n = 0;
    cards.forEach(a => {
      const show = (state.os === 'all' || a.dataset.os === state.os) && (state.cat === 'all' || a.dataset.cat === state.cat) && toks.every(t => a._hay.includes(t));
      a.hidden = !show; if (show) n++;
    });
    document.querySelectorAll('#c-os .chip, #c-cat .chip').forEach(b => b.setAttribute('aria-pressed', String(state[b.dataset.group] === b.dataset.id)));
    $('#c-count').textContent = n ? `${n} of ${cards.length} commands` : 'No command matches. Try another word or clear the filters.';
    const p = new URLSearchParams();
    if (state.os !== 'all') p.set('os', state.os);
    if (state.cat !== 'all') p.set('cat', state.cat);
    if (state.q) p.set('q', state.q);
    const qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
  }

  function openHash(ev) {
    const m = /^#c-([a-z0-9-]+)$/.exec(location.hash); if (!m) return;
    const a = document.getElementById('c-' + m[1]); if (!a) return;
    if (a.hidden) { state.os = 'all'; state.cat = 'all'; state.q = ''; $('#c-search').value = ''; apply(); }
    toggle(a, true);
    const go = () => a.scrollIntoView({ block: 'center', behavior: ev && !window.CWMP.reduce ? 'smooth' : 'instant' });
    go(); if (!ev) { requestAnimationFrame(go); if (document.fonts) document.fonts.ready.then(go); }
    a.classList.add('flash'); setTimeout(() => a.classList.remove('flash'), 1600);
    a._more.focus({ preventScroll: true });
  }

  async function init() {
    try { data = await getJSON('data/commands.json'); }
    catch (e) { $('#c-count').textContent = 'Could not load the commands. Refresh to try again.'; return; }
    const p = new URLSearchParams(location.search);
    if (data.os.some(o => o.id === p.get('os'))) state.os = p.get('os');
    if (data.categories.some(o => o.id === p.get('cat'))) state.cat = p.get('cat');
    state.q = (p.get('q') || '').slice(0, 80); $('#c-search').value = state.q;
    chips();
    cards = data.commands.map(card);
    $('#c-grid').replaceChildren(...cards);
    const m = data.meta;
    $('#c-meta').textContent = [m.notes.split('. ').slice(2).join('. '), m.docs_checked ? 'Doc links checked on ' + m.docs_checked + '.' : ''].filter(Boolean).join(' ');
    document.addEventListener('click', e => {
      const b = e.target.closest('#c-os .chip, #c-cat .chip'); if (!b) return;
      state[b.dataset.group] = b.dataset.id; apply();
    });
    let t; $('#c-search').addEventListener('input', e => { clearTimeout(t); t = setTimeout(() => { state.q = e.target.value.trim(); apply(); }, 60); });
    $('#c-reset').addEventListener('click', () => { state.os = 'all'; state.cat = 'all'; state.q = ''; $('#c-search').value = ''; apply(); $('#c-search').focus(); });
    document.addEventListener('keydown', e => {
      if (e.key === '/' && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) && !e.ctrlKey && !e.metaKey) { e.preventDefault(); $('#c-search').focus(); }
    });
    apply();
    window.addEventListener('hashchange', openHash);
    openHash(null);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
