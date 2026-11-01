/* terms.html and privacy.html: highlight the current section in the contents sidebar. */
(function () {
  'use strict';
  var links = Array.prototype.slice.call(document.querySelectorAll('.legal-toc a[href^="#"]'));
  if (!links.length || !('IntersectionObserver' in window)) return;
  var map = {};
  links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
  function set(id) {
    links.forEach(function (a) { a.classList.remove('on'); a.removeAttribute('aria-current'); });
    if (map[id]) { map[id].classList.add('on'); map[id].setAttribute('aria-current', 'location'); }
  }
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) set(e.target.id); });
  }, { rootMargin: '-20% 0px -70% 0px', threshold: 0 });
  Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) io.observe(s); });
  set(links[0].getAttribute('href').slice(1));
})();
