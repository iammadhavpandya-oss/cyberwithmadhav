/* CyberWithMadhav consent gate.
 * Loaded in <head> (not deferred) on every page so the gate class is set before first paint.
 * Stores { v, at } in localStorage under 'cwm-consent'. Bump VERSION when the Terms or Privacy Policy
 * change and every visitor is asked again. terms.html and privacy.html opt out with
 * <meta name="cwm-consent" content="skip">. No innerHTML, no inline styles (CSP safe).
 * Text follows the language toggle (i18n.js): T(key, English) returns the Hinglish string when Hinglish is on.
 */
(function () {
  'use strict';
  var VERSION = 3;
  var KEY = 'cwm-consent';
  var root = document.documentElement;

  function read() {
    try { var v = JSON.parse(localStorage.getItem(KEY)); return v && v.v === VERSION ? v : null; } catch (e) { return null; }
  }
  function write() {
    try { localStorage.setItem(KEY, JSON.stringify({ v: VERSION, at: new Date().toISOString() })); return true; } catch (e) { return false; }
  }
  window.CWMConsent = { version: VERSION, key: KEY, has: function () { return !!read(); },
    reset: function () { try { localStorage.removeItem(KEY); } catch (e) {} } };

  var skip = document.querySelector('meta[name="cwm-consent"][content="skip"]');
  if (skip || read()) return;
  root.classList.add('consent-pending');

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    for (var k in attrs || {}) {
      if (k === 'text') n.textContent = attrs[k]; else if (k === 'class') n.className = attrs[k]; else n.setAttribute(k, attrs[k]);
    }
    (kids || []).forEach(function (c) { n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }

  function T(k, en) { return window.CWMI18N ? window.CWMI18N.t('consent.' + k, en) : en; }

  function build() {
    if (document.getElementById('cwm-consent')) return;
    var cb = el('input', { type: 'checkbox', id: 'cg-agree', 'aria-describedby': 'cg-hint' });
    var btn = el('button', { type: 'button', class: 'btn btn-primary cg-enter', id: 'cg-enter', disabled: '', 'aria-disabled': 'true' }, [T('enter', 'Enter site')]);
    var terms = el('a', { href: 'terms.html', target: '_blank', rel: 'noopener' }, [T('terms', 'Terms and Conditions')]);
    var priv = el('a', { href: 'privacy.html', target: '_blank', rel: 'noopener' }, [T('privacy', 'Privacy Policy')]);
    var newTab = function () { return el('span', { class: 'sr-only', text: T('newtab', ' (opens in a new tab)') }); };
    terms.appendChild(newTab()); priv.appendChild(newTab());
    var hi = window.CWMI18N && window.CWMI18N.lang === 'hi';
    var langBtn = el('button', { type: 'button', class: 'cg-lang lang-toggle', 'aria-pressed': String(!!hi), 'aria-label': hi ? 'Language: Hinglish. Switch to English' : 'Language: English. Switch to Hinglish' },
      [el('span', { class: 'lt-ico', 'aria-hidden': 'true', text: 'Aa' }), el('span', { class: 'lt-label', text: hi ? 'Hinglish' : 'English' })]);

    var box = el('div', { class: 'cg-card', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'cg-title', 'aria-describedby': 'cg-sum' }, [
      el('div', { class: 'cg-top' }, [el('img', { src: 'favicon.svg', alt: '', width: '40', height: '40', class: 'cg-logo' }), langBtn]),
      el('h2', { id: 'cg-title', text: T('title', 'Welcome to CyberWithMadhav') }),
      el('div', { id: 'cg-sum', class: 'cg-sum' }, [
        el('p', { text: T('intro', 'Free cybersecurity learning, CTF practice, AI prompt sheets and Indian cyber law notes, made for learners in India.') }),
        el('ul', {}, [
          el('li', { text: T('li1', 'Education and awareness only. Nothing here is legal, security or professional advice. Check official sources before you rely on anything.') }),
          el('li', { text: T('li2', 'Test only systems, networks and accounts you own or have written permission to test. Unauthorised access is a civil wrong under IT Act s.43 and, if done dishonestly or fraudulently, an offence under s.66. Other laws, including the BNS, can also apply.') }),
          el('li', { text: T('li3', 'You are responsible for how you use what you learn. Everything is provided as is, with no warranty.') }),
          el('li', { text: T('li4', 'No trackers or analytics. Your theme, language, progress and this choice stay in your browser.') })
        ])
      ]),
      el('label', { class: 'cg-check', for: 'cg-agree' }, [cb, el('span', {}, [T('agree1', 'I am 18 or older, or I have a parent or guardian\'s permission. I have read and agree to the '), terms, T('agree2', ' and '), priv, T('agree3', ', and I will use this site only for lawful, authorised learning.')])]),
      el('p', { id: 'cg-hint', class: 'cg-hint small muted', 'aria-live': 'polite', text: T('hint', 'Tick the box to enter the site.') }),
      btn
    ]);
    var wrap = el('div', { id: 'cwm-consent', class: 'cg' }, [box]);

    var others = Array.prototype.filter.call(document.body.children, function (n) { return n !== wrap && n.tagName !== 'SCRIPT'; });
    others.forEach(function (n) { n.setAttribute('inert', ''); n.setAttribute('data-cg-inert', ''); });
    document.body.appendChild(wrap);

    cb.addEventListener('change', function () {
      btn.disabled = !cb.checked; btn.setAttribute('aria-disabled', String(!cb.checked));
      document.getElementById('cg-hint').textContent = cb.checked ? T('thanks', 'Thank you. Select Enter site to continue.') : T('hint', 'Tick the box to enter the site.');
    });
    btn.addEventListener('click', function () {
      if (!cb.checked) return;
      write();
      Array.prototype.forEach.call(document.querySelectorAll('[data-cg-inert]'), function (n) { n.removeAttribute('inert'); n.removeAttribute('data-cg-inert'); });
      root.classList.remove('consent-pending');
      wrap.remove();
      var m = document.getElementById('main'); if (m) m.focus({ preventScroll: true });
      document.dispatchEvent(new CustomEvent('cwm:consent', { detail: { version: VERSION } }));
    });
    /* Focus trap. Esc does not dismiss: agreeing is the only way in. */
    wrap.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); return; }
      if (e.key !== 'Tab') return;
      var f = Array.prototype.filter.call(box.querySelectorAll('a[href],input,button:not([disabled])'), function (n) { return n.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      else if (!box.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
    }, true);
    /* keep site shortcuts (Ctrl+K palette, CTF keys) from firing behind the gate */
    wrap.addEventListener('keydown', function (e) { e.stopPropagation(); });
    document.addEventListener('keydown', function (e) {
      if (!document.getElementById('cwm-consent')) return;
      if (e.key === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); }
    }, true);
    document.addEventListener('focusin', function (e) {
      if (document.getElementById('cwm-consent') && !box.contains(e.target)) cb.focus();
    });
    cb.focus();
  }
  /* language switched while the gate is open: rebuild it in the new language, keep focus on the switch */
  document.addEventListener('cwm:lang', function () {
    var w = document.getElementById('cwm-consent'); if (!w) return;
    var was = document.getElementById('cg-agree').checked;
    w.remove(); build();
    if (was) { var c = document.getElementById('cg-agree'); c.checked = true; c.dispatchEvent(new Event('change')); }
    var lb = document.querySelector('#cwm-consent .cg-lang'); if (lb) lb.focus();
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build); else build();
})();
