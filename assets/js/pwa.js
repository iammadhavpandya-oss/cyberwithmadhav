/* Registers the offline service worker (sw.js), skipped on file:// and when the browser has no support.
   Also loads the easter eggs (assets/js/eggs.js) only after the page has fully loaded and the browser is idle,
   so they never compete with first paint. tools/build_site.py keeps the ?v= hash below up to date. */
(function () {
  'use strict';
  window.addEventListener('load', function () {
    if ('serviceWorker' in navigator && location.protocol !== 'file:') {
      navigator.serviceWorker.register('sw.js', { scope: './' }).catch(function () {});
    }
    var go = function () {
      var s = document.createElement('script'); s.src = 'assets/js/eggs.js?v=b17c9b0c51'; s.async = true; document.body.appendChild(s);
    };
    if (window.requestIdleCallback) window.requestIdleCallback(go, { timeout: 3000 }); else setTimeout(go, 800);
  });
})();
