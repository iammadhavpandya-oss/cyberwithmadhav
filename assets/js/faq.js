/* FAQ search filter and deep links. No network, nothing stored. */
(function () {
  'use strict';
  var input = document.getElementById('faq-q');
  var count = document.getElementById('faq-count');
  if (!input) return;

  function textOf(el) {
    return (el.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
  }

  function shownLabel(n) {
    var d = (window.CWM_I18N && window.CWM_I18N.hi) || {};
    var lang = document.documentElement.getAttribute('data-lang') || 'en';
    var tmpl = lang === 'hi' && d['faq.shown'] ? d['faq.shown'] : '{n} questions shown';
    return tmpl.replace('{n}', String(n));
  }

  function emptyLabel() {
    var d = (window.CWM_I18N && window.CWM_I18N.hi) || {};
    var lang = document.documentElement.getAttribute('data-lang') || 'en';
    return lang === 'hi' && d['faq.empty'] ? d['faq.empty'] : 'No questions match this search. Try different words, or clear the search to see every question.';
  }

  function filter() {
    var q = input.value.trim().toLowerCase();
    var items = document.querySelectorAll('.faq-page .faq details');
    var n = 0;
    items.forEach(function (d) {
      var hit = !q || textOf(d).indexOf(q) !== -1;
      d.classList.toggle('is-hidden', !hit);
      if (hit) n += 1;
    });
    document.querySelectorAll('.faq-sec').forEach(function (sec) {
      var visible = sec.querySelectorAll('details:not(.is-hidden)').length;
      sec.classList.toggle('is-empty', visible === 0);
    });
    if (count) {
      count.textContent = q ? shownLabel(n) : '';
    }
    var empty = document.getElementById('faq-empty');
    if (n === 0) {
      if (!empty) {
        empty = document.createElement('p');
        empty.id = 'faq-empty';
        empty.className = 'muted faq-empty';
        input.parentNode.appendChild(empty);
      }
      empty.hidden = false;
      empty.textContent = emptyLabel();
    } else if (empty) {
      empty.hidden = true;
    }
  }

  function openHash() {
    var id = (location.hash || '').replace(/^#/, '');
    if (!id) return;
    var el = document.getElementById(id);
    if (!el) return;
    if (el.tagName === 'DETAILS') {
      el.open = true;
      el.classList.remove('is-hidden');
    } else {
      var first = el.querySelector('details');
      if (first) first.open = true;
    }
  }

  input.addEventListener('input', filter);
  window.addEventListener('hashchange', openHash);
  openHash();
})();
