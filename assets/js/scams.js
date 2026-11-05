/* scams.html: Scam Encyclopedia India. Data from data/scams.json. No innerHTML from data. */
(function () {
  'use strict';
  const { $, el, getJSON } = window.CWMP;
  const BASE = 'https://iammadhavpandya-oss.github.io/cyberwithmadhav/scams.html';
  const state = { f: 'all', q: '' };
  let data = null, cards = [];
  const norm = s => String(s || '').toLowerCase();
  const ext = (href, text, cls) => el('a', { href, target: '_blank', rel: 'noopener noreferrer', class: cls || null }, [text, el('span', { class: 'sr-only', text: ' (opens in a new tab)' })]);
  const host = u => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return u; } };

  function list(items, cls) { return el('ul', { class: cls }, items.map(t => el('li', { text: t }))); }

  function card(c) {
    const url = BASE + '#s-' + c.id;
    const share = 'https://wa.me/?text=' + encodeURIComponent(`${c.hinglish}: ${c.name}. Red flags and what to do now: ${url}`);
    const pid = 'sp-' + c.id;
    const more = el('button', { type: 'button', class: 'c-more', 'aria-expanded': 'false', 'aria-controls': pid }, [el('span', { text: 'What to do now' }), el('span', { class: 'chev', 'aria-hidden': 'true', text: '▾' })]);
    const panel = el('div', { class: 's-panel', id: pid, hidden: true }, [
      el('a', { class: 's-call small', href: 'tel:1930' }, [el('span', { text: 'Call ' }), el('b', { text: '1930' }), el('span', { text: ' now' })]),
      el('ol', { class: 's-todo' }, c.todo.map(t => el('li', { text: t }))),
      el('p', { class: 's-portal' }, [ext('https://cybercrime.gov.in', 'Report on cybercrime.gov.in ↗')])
    ]);
    more.addEventListener('click', () => toggle(art, more.getAttribute('aria-expanded') !== 'true'));
    const art = el('article', { class: 's-card card', id: 's-' + c.id, 'data-verify': String(c.verify) }, [
      el('div', { class: 's-top' }, [
        el('p', { class: 's-hing', lang: 'hi-Latn', text: c.hinglish }),
        c.verify ? el('span', { class: 'badge verify', title: 'Still being checked against the latest official guidance', text: 'being verified' }) : null
      ]),
      el('h3', { class: 's-name', text: c.name }),
      el('ol', { class: 's-steps', 'aria-label': 'How it works' }, c.steps.map((t, i) => el('li', null, [el('span', { class: 's-n mono', 'aria-hidden': 'true', text: String(i + 1) }), el('span', { text: t })]))),
      el('p', { class: 'c-k mono', text: 'red flags' }),
      list(c.flags, 's-flags'),
      more, panel,
      el('div', { class: 's-foot' }, [
        el('p', { class: 's-law' }, [el('span', { class: 'c-k mono', text: 'law ' }), ...c.law.map(l => el('span', { class: 'badge', text: l }))]),
        el('p', { class: 's-src small' }, [el('span', { class: 'muted', text: 'Source: ' }), ext(c.source, host(c.source) + ' ↗'), c.slow ? el('span', { class: 'muted', text: ' (official site may be slow)' }) : null]),
        el('a', { class: 's-wa small', href: share, target: '_blank', rel: 'noopener noreferrer', 'aria-label': 'Share on WhatsApp: ' + c.name + ' (opens in a new tab)' }, [waIcon(), 'Share on WhatsApp'])
      ])
    ]);
    art._hay = norm([c.name, c.hinglish, c.steps.join(' '), c.flags.join(' '), c.todo.join(' '), c.law.join(' ')].join(' '));
    art._more = more; art._panel = panel;
    return art;
  }

  function waIcon() {
    const ns = 'http://www.w3.org/2000/svg', s = document.createElementNS(ns, 'svg');
    s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('width', '16'); s.setAttribute('height', '16'); s.setAttribute('aria-hidden', 'true');
    const p = document.createElementNS(ns, 'path'); p.setAttribute('fill', 'currentColor');
    p.setAttribute('d', 'M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z');
    s.appendChild(p); return s;
  }

  function toggle(art, open) {
    art._more.setAttribute('aria-expanded', String(open));
    art._more.firstChild.textContent = open ? 'Hide steps' : 'What to do now';
    art._panel.hidden = !open; art.classList.toggle('open', open);
  }

  function apply() {
    const toks = norm(state.q).split(/\s+/).filter(Boolean);
    let n = 0;
    cards.forEach(a => {
      const show = (state.f === 'all' || a.dataset.verify === 'true') && toks.every(t => a._hay.includes(t));
      a.hidden = !show; if (show) n++;
    });
    document.querySelectorAll('#s-filter .chip').forEach(b => b.setAttribute('aria-pressed', String(state.f === b.dataset.id)));
    $('#s-count').textContent = n ? `${n} of ${cards.length} scams` : 'No scam matches. Try another word, or call 1930 if you have lost money.';
    const p = new URLSearchParams(); if (state.q) p.set('q', state.q); if (state.f !== 'all') p.set('f', state.f);
    const qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
  }

  function openHash(ev) {
    const m = /^#s-([a-z0-9-]+)$/.exec(location.hash); if (!m) return;
    const a = document.getElementById('s-' + m[1]); if (!a) return;
    if (a.hidden) { state.f = 'all'; state.q = ''; $('#s-search').value = ''; apply(); }
    a.classList.add('in');
    const go = () => a.scrollIntoView({ block: 'start', behavior: ev && !window.CWMP.reduce ? 'smooth' : 'instant' });
    go(); if (!ev) { requestAnimationFrame(go); if (document.fonts) document.fonts.ready.then(go); }
    a.classList.add('flash'); setTimeout(() => a.classList.remove('flash'), 1600);
    a._more.focus({ preventScroll: true });
  }

  async function init() {
    try { data = await getJSON('data/scams.json'); }
    catch (e) { $('#s-count').textContent = 'Could not load the scams. Refresh, or call 1930 if you need help now.'; return; }
    const p = new URLSearchParams(location.search);
    state.q = (p.get('q') || '').slice(0, 80); $('#s-search').value = state.q;
    if (p.get('f') === 'verify') state.f = 'verify';
    const nv = data.scams.filter(s => s.verify).length;
    const chip = (id, label, n) => el('button', { type: 'button', class: 'chip', 'data-id': id, 'aria-pressed': 'false' }, [label, el('span', { class: 'n', text: String(n) })]);
    $('#s-filter').replaceChildren(chip('all', 'All', data.scams.length), chip('verify', 'Being verified', nv));
    $('#s-filter').addEventListener('click', e => { const b = e.target.closest('.chip'); if (b) { state.f = b.dataset.id; apply(); } });
    cards = data.scams.map(card);
    $('#s-grid').replaceChildren(...cards);
    if ('IntersectionObserver' in window && !window.CWMP.reduce) {
      const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -10% 0px' });
      cards.forEach(c => io.observe(c));
    } else cards.forEach(c => c.classList.add('in'));
    let t; $('#s-search').addEventListener('input', e => { clearTimeout(t); t = setTimeout(() => { state.q = e.target.value.trim(); apply(); }, 60); });
    document.addEventListener('keydown', e => {
      if (e.key === '/' && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) && !e.ctrlKey && !e.metaKey) { e.preventDefault(); $('#s-search').focus(); }
    });
    apply();
    window.addEventListener('hashchange', openHash);
    openHash(null);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
