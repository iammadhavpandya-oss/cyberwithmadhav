/* CyberWithMadhav language toggle: English (default, indexed) or Hinglish (Roman script).
 * Loaded in <head>, not deferred, after i18n-dict.js and before consent.js, so <html lang> is set before first paint.
 * Choice is kept in localStorage 'cwm-lang' ('en' or 'hi'). No cookies, nothing sent anywhere.
 * Elements opt in with data-i18n="key" (innerHTML is swapped from window.CWM_I18N.hi, plus window.CWM_I18N_PAGE
 * on pages that ship their own dictionary, e.g. blog posts). data-lang-only="hi|en" shows a block in one language only.
 * The English text is read from the page itself, so the dictionary only needs the Hinglish side. CSP safe. */
(function () {
  'use strict';
  var KEY = 'cwm-lang', root = document.documentElement, orig = new Map();
  var lang = 'en';
  try { lang = localStorage.getItem(KEY) === 'hi' ? 'hi' : 'en'; } catch (e) {}
  function setLangAttr() { root.setAttribute('lang', lang === 'hi' ? 'hi-Latn' : 'en-IN'); root.setAttribute('data-lang', lang); }
  setLangAttr();

  function dict() {
    var d = {}, a = (window.CWM_I18N && window.CWM_I18N.hi) || {}, b = window.CWM_I18N_PAGE || {}, k;
    for (k in a) d[k] = a[k];
    for (k in b) d[k] = b[k];
    return d;
  }
  function t(key, en) { if (lang !== 'hi') return en; var v = dict()[key]; return v == null ? en : v; }

  function apply() {
    var d = dict();
    Array.prototype.forEach.call(document.querySelectorAll('[data-i18n]'), function (el) {
      var k = el.getAttribute('data-i18n');
      if (!orig.has(el)) orig.set(el, el.innerHTML);
      var v = lang === 'hi' ? d[k] : null;
      var next = v == null ? orig.get(el) : v;
      if (el.innerHTML !== next) el.innerHTML = next;
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-i18n-attr]'), function (el) {
      el.getAttribute('data-i18n-attr').split(';').forEach(function (pair) {
        var p = pair.split(':'), attr = p[0], k = p[1], store = 'data-i18n-en-' + attr;
        if (!attr || !k) return;
        if (!el.hasAttribute(store)) el.setAttribute(store, el.getAttribute(attr) || '');
        var v = lang === 'hi' ? d[k] : null;
        el.setAttribute(attr, v == null ? el.getAttribute(store) : v);
      });
    });
    Array.prototype.forEach.call(document.querySelectorAll('.lang-toggle'), function (b) {
      var hi = lang === 'hi';
      b.setAttribute('aria-pressed', String(hi));
      b.setAttribute('aria-label', hi ? 'Language: Hinglish. Switch to English' : 'Language: English. Switch to Hinglish');
      b.setAttribute('title', hi ? 'Switch to English' : 'Switch to Hinglish');
      var l = b.querySelector('.lt-label'); if (l) l.textContent = hi ? 'Hinglish' : 'English';
    });
  }
  function set(next) {
    lang = next === 'hi' ? 'hi' : 'en';
    try { localStorage.setItem(KEY, lang); } catch (e) {}
    setLangAttr(); apply();
    document.dispatchEvent(new CustomEvent('cwm:lang', { detail: { lang: lang } }));
  }
  window.CWMI18N = { get lang() { return lang; }, t: t, set: set, apply: apply, key: KEY };

  function init() {
    apply();
    document.addEventListener('click', function (e) {
      var b = e.target.closest && e.target.closest('.lang-toggle');
      if (b) { e.preventDefault(); set(lang === 'hi' ? 'en' : 'hi'); }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
