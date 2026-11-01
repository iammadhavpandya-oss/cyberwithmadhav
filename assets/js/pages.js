/* Shared helpers for prompts.html and cyberlaw.html. No innerHTML from data. */
(function () {
  'use strict';
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function el(tag, attrs, kids) {
    const n = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      const v = attrs[k];
      if (v == null || v === false) continue;
      if (k === 'class') n.className = v;
      else if (k === 'text') n.textContent = v;
      else n.setAttribute(k, v === true ? '' : v);
    }
    (kids || []).forEach(c => { if (c != null) n.append(c.nodeType ? c : document.createTextNode(String(c))); });
    return n;
  }

  let toastT;
  function toast(msg) {
    const t = $('#toast'); if (!t) return;
    t.textContent = msg; t.hidden = false;
    requestAnimationFrame(() => t.classList.add('show'));
    clearTimeout(toastT);
    toastT = setTimeout(() => { t.classList.remove('show'); setTimeout(() => { t.hidden = true; }, 300); }, 1800);
  }

  async function copyText(text, btn) {
    let ok = false;
    try { await navigator.clipboard.writeText(text); ok = true; }
    catch (e) {
      const ta = el('textarea', { class: 'sr-only', 'aria-hidden': 'true' }); ta.value = text;
      document.body.append(ta); ta.select();
      try { ok = document.execCommand('copy'); } catch (e2) { ok = false; }
      ta.remove();
    }
    if (btn) {
      const old = btn.dataset.label || btn.textContent;
      btn.dataset.label = old;
      btn.classList.toggle('ok', ok); btn.textContent = ok ? 'Copied' : 'Copy failed';
      setTimeout(() => { btn.classList.remove('ok'); btn.textContent = old; }, 1500);
    }
    toast(ok ? 'Copied to clipboard' : 'Could not copy. Select the text and copy it manually.');
    return ok;
  }

  let io = null;
  function reveal(nodes) {
    nodes = nodes || $$('.reveal:not(.in)');
    if (reduce || !('IntersectionObserver' in window)) { nodes.forEach(n => n.classList.add('in')); return; }
    if (!io) io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    nodes.forEach(n => io.observe(n));
  }

  async function getJSON(url) {
    const r = await fetch(url, { cache: 'no-cache' });
    if (!r.ok) throw new Error(url + ' ' + r.status);
    return r.json();
  }

  async function exists(url) {
    try {
      const r = await fetch(url, { method: 'HEAD', cache: 'no-cache' });
      return r.ok;
    } catch (e) { return false; }
  }

  function store(key, fallback) {
    try { const v = JSON.parse(localStorage.getItem(key)); return v == null ? fallback : v; } catch (e) { return fallback; }
  }
  function save(key, v) { try { localStorage.setItem(key, JSON.stringify(v)); } catch (e) { /* private mode */ } }

  function extLink(href, text, cls) {
    return el('a', { href, class: cls || 'src', target: '_blank', rel: 'noopener noreferrer' }, [text || 'Source']);
  }

  /* nav toggle (same behaviour as ctf.js) */
  function nav() {
    const nt = $('.nav-toggle'), nl = $('#nav-links');
    if (!nt || !nl) return;
    nt.addEventListener('click', () => {
      const open = nl.classList.toggle('open');
      nt.setAttribute('aria-expanded', String(open));
      nt.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
    $$('a', nl).forEach(a => a.addEventListener('click', () => {
      nl.classList.remove('open'); nt.setAttribute('aria-expanded', 'false'); nt.setAttribute('aria-label', 'Open menu');
    }));
  }

  function init() {
    nav();
    const y = $('#year'); if (y) y.textContent = String(new Date().getFullYear());
    reveal();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();

  window.CWMP = { $, $$, el, toast, copyText, reveal, getJSON, exists, store, save, extLink, reduce };
})();
