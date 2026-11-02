/* Nav "More" menu (a native <details>): close on outside click, on Escape (focus back to the toggle) and after a link is chosen. */
(function () {
  'use strict';
  const d = document.querySelector('.nav-more'); if (!d) return;
  const s = d.querySelector('summary');
  s.setAttribute('aria-haspopup', 'true');
  const sync = () => s.setAttribute('aria-expanded', String(d.open));
  sync(); d.addEventListener('toggle', sync);
  document.addEventListener('click', e => { if (d.open && !d.contains(e.target)) d.open = false; });
  d.addEventListener('keydown', e => { if (e.key === 'Escape' && d.open) { e.stopPropagation(); d.open = false; s.focus(); } });
  d.addEventListener('focusout', e => { if (d.open && e.relatedTarget && !d.contains(e.relatedTarget) && window.matchMedia('(min-width:821px)').matches) d.open = false; });
})();
