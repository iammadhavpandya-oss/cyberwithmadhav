/* Progressive disclosure: tool tabs on the homepage, and on cyber law a sticky section bar plus long lists
   that show the first few entries with a "Show all" button. Without JS everything stays fully visible. */
(function () {
  'use strict';
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- homepage: one tool at a time ---------- */
  const tabs = $('.tool-tabs'), grid = $('.tools-grid');
  if (tabs && grid) {
    const btns = $$('[role="tab"]', tabs);
    const panels = btns.map(b => document.getElementById(b.getAttribute('aria-controls')));
    panels.forEach((p, i) => { p.setAttribute('role', 'tabpanel'); p.setAttribute('aria-labelledby', btns[i].id); });
    const show = (id, focus) => {
      const i = Math.max(0, btns.findIndex(b => b.getAttribute('aria-controls') === id));
      btns.forEach((b, j) => { b.setAttribute('aria-selected', String(i === j)); b.tabIndex = i === j ? 0 : -1; });
      panels.forEach((p, j) => { p.classList.toggle('tab-off', i !== j); if (i === j) p.classList.add('in'); });
      if (focus) btns[i].focus();
    };
    tabs.hidden = false; grid.classList.add('tabs-on');
    btns.forEach((b, i) => {
      b.addEventListener('click', () => show(b.getAttribute('aria-controls')));
      b.addEventListener('keydown', e => {
        const k = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
        if (k) { e.preventDefault(); show(btns[(i + k + btns.length) % btns.length].getAttribute('aria-controls'), true); }
        else if (e.key === 'Home' || e.key === 'End') { e.preventDefault(); show(btns[e.key === 'Home' ? 0 : btns.length - 1].getAttribute('aria-controls'), true); }
      });
    });
    const fromHash = () => { const id = location.hash.slice(1); if (panels.some(p => p.id === id)) show(id); };
    panels.forEach(p => p.addEventListener('cwm:show', () => show(p.id)));
    window.addEventListener('hashchange', fromHash);
    show(panels[0].id); fromHash();
  }

  /* ---------- cyber law ---------- */
  const toc = $('#law-toc');
  if (!toc) return;

  // sticky bar: highlight the section in view and keep its chip visible
  const links = $$('a[href^="#"]', toc), scroller = $('.law-toc-scroll', toc);
  const byId = new Map(links.map(a => [a.getAttribute('href').slice(1), a]));
  const mark = id => {
    const a = byId.get(id); if (!a) return;
    links.forEach(l => { l.classList.toggle('on', l === a); if (l === a) l.setAttribute('aria-current', 'true'); else l.removeAttribute('aria-current'); });
    const x = a.offsetLeft - (scroller.clientWidth - a.offsetWidth) / 2;
    scroller.scrollTo({ left: Math.max(0, x), behavior: reduce ? 'auto' : 'smooth' });
  };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) mark(e.target.id); }), { rootMargin: '-35% 0px -60% 0px' });
    byId.forEach((_, id) => { const s = document.getElementById(id); if (s) io.observe(s); });
  }
  const stuck = () => toc.classList.toggle('stuck', toc.getBoundingClientRect().top <= 61);
  window.addEventListener('scroll', stuck, { passive: true }); stuck();

  // folding long lists
  const FOLDS = [
    { list: '#tl', items: '#tl > li', cap: 6, noun: 'timeline entries' },
    { list: '#it-table', items: '#it-table tbody tr', cap: 8, noun: 'IT Act sections', host: '#it-table', open: '#it-filter .chip' },
    { list: '#bns-table', items: '#bns-table tbody tr', cap: 8, noun: 'BNS rows', host: '#bns-table' },
    { list: '#case-grid', items: '#case-grid > .case', cap: 6, noun: 'case files' },
    { list: '#faq-list', items: '#faq-list > details', cap: 6, noun: 'questions' },
    { list: '#gl-list', items: '#gl-list > .gl-item', cap: 12, noun: 'terms', search: '#gl-search' }
  ];
  const all = [];
  function setup() {
    FOLDS.forEach(f => {
      const list = $(f.list); if (!list) return;
      const host = f.host ? list.closest('.tbl-wrap') || list : list;
      const btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'btn btn-ghost fold-btn';
      btn.setAttribute('aria-controls', list.id);
      host.after(btn);
      const st = { f, list, host, btn, folded: true };
      const apply = () => {
        const items = $$(f.items);
        const fold = st.folded && items.length > f.cap;
        items.forEach((el, i) => el.classList.toggle('fold-x', fold && i >= f.cap));
        host.classList.toggle('folded', fold);
        btn.hidden = items.length <= f.cap;
        btn.setAttribute('aria-expanded', String(!fold));
        btn.textContent = fold ? `Show all ${items.length} ${f.noun}` : 'Show fewer';
      };
      st.apply = apply;
      st.open = () => { if (st.folded) { st.folded = false; apply(); } };
      btn.addEventListener('click', () => {
        st.folded = !st.folded; apply();
        if (st.folded) { const sec = list.closest('section'); if (sec && sec.getBoundingClientRect().top < 0) sec.scrollIntoView({ block: 'start', behavior: reduce ? 'auto' : 'smooth' }); }
      });
      if (f.open) $$(f.open).forEach(c => c.addEventListener('click', st.open));
      if (f.search) { const s = $(f.search); if (s) { if (s.value.trim()) st.folded = false; s.addEventListener('input', st.open); } }
      // data re-renders (language switch, filters) replace children: fold them again
      new MutationObserver(() => apply()).observe(f.host ? list.querySelector('tbody') || list : list, { childList: true });
      apply(); all.push(st);
    });
    openForHash();
  }
  // a deep link or search result pointing inside a folded list opens it first
  function openForHash() {
    let t; try { t = location.hash && document.querySelector(decodeURIComponent(location.hash)); } catch (e) { t = null; }
    if (!t) return;
    const st = all.find(s => s.list.contains(t) && t.closest('.fold-x'));
    if (st) { st.open(); t.scrollIntoView({ block: 'start' }); }
  }
  window.addEventListener('hashchange', openForHash);
  document.addEventListener('cwm:show', e => { const st = all.find(s => s.list.contains(e.target)); if (st) st.open(); });

  const ready = () => document.documentElement.dataset.lawReady === '1';
  if (ready()) setup();
  else {
    const mo = new MutationObserver(() => { if (ready()) { mo.disconnect(); setup(); } });
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-law-ready'] });
  }
})();
