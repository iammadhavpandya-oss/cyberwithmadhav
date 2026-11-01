/* 404 page: show the missing path and open site search. */
(function () {
  'use strict';
  function init() {
    var p = document.getElementById('nf-path');
    if (p) p.textContent = (location.pathname.replace(/^\/cyberwithmadhav\//, '/') || '/').slice(0, 80);
    var b = document.getElementById('nf-search');
    if (b) b.addEventListener('click', function () { if (window.cwmPalette) window.cwmPalette.open(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
