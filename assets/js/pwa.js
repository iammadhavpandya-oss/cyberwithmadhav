/* Registers the offline service worker (sw.js). Skipped on file:// and when the browser has no support. */
(function () {
  'use strict';
  if (!('serviceWorker' in navigator) || location.protocol === 'file:') return;
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('sw.js', { scope: './' }).catch(function () {});
  });
})();
