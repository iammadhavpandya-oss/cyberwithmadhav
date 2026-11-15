/* Blog listing: category filter chips (no URL change). Posts stay fully visible without JS. CSP safe.
   Cards sit in one group per category (.bp-group); a group hides when none of its cards match. */
(function () {
  'use strict';
  var chips = document.querySelectorAll('.bp-chips .chip'), root = document.getElementById('bp-grid'), out = document.getElementById('bp-count');
  if (!chips.length || !root) return;
  var cards = root.querySelectorAll('.bp-card'), groups = root.querySelectorAll('.bp-group');
  if (!cards.length) return;
  function show(cat) {
    var n = 0;
    Array.prototype.forEach.call(chips, function (c) { c.setAttribute('aria-pressed', String(c.getAttribute('data-cat') === cat)); });
    Array.prototype.forEach.call(cards, function (c) { var on = cat === 'all' || c.getAttribute('data-cat') === cat; c.hidden = !on; if (on) n++; });
    Array.prototype.forEach.call(groups, function (g) { g.hidden = !(cat === 'all' || g.getAttribute('data-cat') === cat); });
    if (out) out.textContent = window.CWMI18N ? window.CWMI18N.t('blog.shown', '{n} posts shown').replace('{n}', n) : n + ' posts shown';
  }
  Array.prototype.forEach.call(chips, function (c) { c.addEventListener('click', function () { show(c.getAttribute('data-cat')); }); });
})();
