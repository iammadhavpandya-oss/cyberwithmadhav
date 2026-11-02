/* CyberWithMadhav consent gate.
 * Loaded in <head> (not deferred) on every page so the gate class is set before first paint.
 * Stores { v, at } in localStorage under 'cwm-consent'. Bump VERSION when the Terms or Privacy Policy
 * change and every visitor is asked again. terms.html and privacy.html opt out with
 * <meta name="cwm-consent" content="skip">. No innerHTML, no inline styles (CSP safe).
 */
(function () {
  'use strict';
  var VERSION = 2;
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

  function build() {
    if (document.getElementById('cwm-consent')) return;
    var cb = el('input', { type: 'checkbox', id: 'cg-agree', 'aria-describedby': 'cg-hint' });
    var btn = el('button', { type: 'button', class: 'btn btn-primary cg-enter', id: 'cg-enter', disabled: '', 'aria-disabled': 'true' }, ['Enter site']);
    var terms = el('a', { href: 'terms.html', target: '_blank', rel: 'noopener' }, ['Terms and Conditions']);
    var priv = el('a', { href: 'privacy.html', target: '_blank', rel: 'noopener' }, ['Privacy Policy']);
    var newTab = function () { return el('span', { class: 'sr-only', text: ' (opens in a new tab)' }); };
    terms.appendChild(newTab()); priv.appendChild(newTab());

    var box = el('div', { class: 'cg-card', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'cg-title', 'aria-describedby': 'cg-sum' }, [
      el('img', { src: 'favicon.svg', alt: '', width: '40', height: '40', class: 'cg-logo' }),
      el('h2', { id: 'cg-title', text: 'Welcome to CyberWithMadhav' }),
      el('div', { id: 'cg-sum', class: 'cg-sum' }, [
        el('p', { text: 'Free cybersecurity learning, CTF practice, AI prompt sheets and Indian cyber law notes, made for learners in India.' }),
        el('ul', {}, [
          el('li', { text: 'Everything here is for education and awareness. It is not legal or professional advice.' }),
          el('li', { text: 'Practise only on systems you own or are authorised to test. Unauthorised access is a civil wrong under IT Act s.43 and, if done dishonestly or fraudulently, an offence under s.66.' }),
          el('li', { text: 'No trackers or analytics. Your theme, progress and this choice stay in your browser.' })
        ])
      ]),
      el('label', { class: 'cg-check', for: 'cg-agree' }, [cb, el('span', {}, ['I have read and agree to the ', terms, ' and ', priv, '.'])]),
      el('p', { id: 'cg-hint', class: 'cg-hint small muted', 'aria-live': 'polite', text: 'Tick the box to enter the site.' }),
      btn
    ]);
    var wrap = el('div', { id: 'cwm-consent', class: 'cg' }, [box]);

    var others = Array.prototype.filter.call(document.body.children, function (n) { return n !== wrap && n.tagName !== 'SCRIPT'; });
    others.forEach(function (n) { n.setAttribute('inert', ''); n.setAttribute('data-cg-inert', ''); });
    document.body.appendChild(wrap);

    cb.addEventListener('change', function () {
      btn.disabled = !cb.checked; btn.setAttribute('aria-disabled', String(!cb.checked));
      document.getElementById('cg-hint').textContent = cb.checked ? 'Thank you. Select Enter site to continue.' : 'Tick the box to enter the site.';
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
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build); else build();
})();
