/* Site wide Ctrl+K search for every page except index.html (main.js runs the palette there).
   Results come from data/search.json, written at build time by tools/build_site.py. */
(function () {
  'use strict';
  if (document.getElementById('palette')) return;
  var items = null, res = [], idx = 0, loading = null;
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    (kids || []).forEach(function (c) { n.append(c); });
    return n;
  }
  var input = el('input', { id: 'pal-input', type: 'text', placeholder: 'Search the whole site: commands, CTF, prompts, law, scams', autocomplete: 'off', spellcheck: 'false', role: 'combobox', 'aria-expanded': 'true', 'aria-controls': 'pal-list', 'aria-autocomplete': 'list' });
  var list = el('ul', { id: 'pal-list', role: 'listbox', 'aria-label': 'Results' });
  var pal = el('dialog', { class: 'palette', id: 'palette', 'aria-label': 'Site search' }, [
    el('div', { class: 'pal-head' }, [el('label', { for: 'pal-input', class: 'sr-only' }, ['Search the whole site']), input]),
    list,
    el('p', { class: 'pal-foot mono' }, ['\u2191\u2193 move \u00b7 Enter open \u00b7 Esc close'])
  ]);
  function load() {
    if (!loading) loading = fetch('data/search.json').then(function (r) { return r.ok ? r.json() : []; }).catch(function () { return []; }).then(function (l) { items = l; return l; });
    return loading;
  }
  function search() {
    var q = input.value.trim().toLowerCase(), words = q.split(/\s+/).filter(Boolean), here = location.pathname.split('/').pop() || 'index.html';
    if (!items) { list.replaceChildren(el('li', { class: 'none' }, ['Loading\u2026'])); return; }
    var scored = [];
    items.forEach(function (it) {
      var hay = (it.t + ' ' + (it.s || '') + ' ' + it.k + ' ' + (it.x || '')).toLowerCase();
      if (!words.every(function (w) { return hay.indexOf(w) !== -1; })) return;
      var t = it.t.toLowerCase(), page = it.u.split(/[?#]/)[0];
      var score = !q ? (it.k === 'Page' ? 0 : 5) : t.indexOf(q) === 0 ? 0 : t.indexOf(q) !== -1 ? 1 : 2;
      if (q && page === here) score -= 0.5;
      scored.push([it, score]);
    });
    scored.sort(function (a, b) { return a[1] - b[1]; });
    res = scored.slice(0, 40).map(function (x) { return x[0]; }); idx = 0;
    if (!res.length) { list.replaceChildren(el('li', { class: 'none' }, ['No results'])); input.setAttribute('aria-activedescendant', ''); return; }
    list.replaceChildren.apply(list, res.map(function (it, i) {
      return el('li', { role: 'option', id: 'pal-' + i, 'aria-selected': String(i === 0), 'data-i': String(i) }, [
        el('span', { class: 'k mono' }, [it.k]), el('span', { class: 'l' + (it.k === 'Command' ? ' mono' : '') }, [it.t]), el('span', { class: 's' }, [it.s || ''])]);
    }));
    input.setAttribute('aria-activedescendant', 'pal-0');
  }
  function move(d) {
    if (!res.length) return;
    idx = (idx + d + res.length) % res.length;
    list.querySelectorAll('[role="option"]').forEach(function (li, i) { li.setAttribute('aria-selected', String(i === idx)); });
    var li = document.getElementById('pal-' + idx); li.scrollIntoView({ block: 'nearest' }); input.setAttribute('aria-activedescendant', li.id);
  }
  function go(i) {
    var it = res[i]; if (!it) return;
    close();
    var u = new URL(it.u, location.href);
    if (u.pathname === location.pathname && u.search === location.search && u.hash) { location.hash = u.hash; var t = document.getElementById(decodeURIComponent(u.hash.slice(1))); if (t) t.scrollIntoView({ block: 'start' }); }
    else location.href = it.u;
  }
  function open() {
    if (pal.open) return;
    input.value = ''; search();
    if (pal.showModal) pal.showModal(); else pal.setAttribute('open', '');
    input.focus();
    load().then(function () { if (pal.open) search(); });
  }
  function close() { if (pal.close) pal.close(); else pal.removeAttribute('open'); }
  window.cwmPalette = { open: open, close: close };
  input.addEventListener('input', search);
  input.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
    else if (e.key === 'Enter') { e.preventDefault(); go(idx); }
  });
  list.addEventListener('click', function (e) { var li = e.target.closest('[data-i]'); if (li) go(Number(li.dataset.i)); });
  pal.addEventListener('click', function (e) { if (e.target === pal) close(); });
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && !e.altKey && e.key.toLowerCase() === 'k') { e.preventDefault(); pal.open ? close() : open(); }
  });
  function mount() {
    document.body.append(pal);
    var nav = document.getElementById('nav-links'), tt = nav && nav.querySelector('.theme-toggle');
    if (nav && !nav.querySelector('.pal-btn')) {
      var b = el('button', { class: 'pal-btn', type: 'button', id: 'palette-open', title: 'Search the whole site (Ctrl+K)' }, [el('span', { 'aria-hidden': 'true' }, ['\u2318K']), el('span', { class: 'sr-only' }, ['Search the whole site (Ctrl+K)'])]);
      b.addEventListener('click', open);
      nav.insertBefore(b, tt || null);
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();
