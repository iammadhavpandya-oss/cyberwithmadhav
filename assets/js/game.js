/* game.html: Scam ya Nahi? Data from data/game.json. Vanilla JS, no innerHTML from data, nothing leaves the browser.
   Logic helpers are exposed as window.CWMGame for tools/test_features.mjs. */
(function () {
  'use strict';
  const { $, el, getJSON, store, save } = window.CWMP;
  const reduce = window.CWMP.reduce;
  const PAGE = 'https://www.cyberwithmadhav.com/game.html';
  const BEST_KEY = 'cwm-scamgame-best';
  const LEVELS = ['all', 'easy', 'medium', 'hard'];
  const SPEAKER = /(Caller|IVR|Agent|Aap|You):\s*/g;

  /* ---------- pure logic ---------- */
  const L = {
    filter(items, level) { return level === 'all' ? items.slice() : items.filter(i => i.level === level); },
    shuffle(arr, rnd) { const a = arr.slice(), r = rnd || Math.random; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; },
    isRight(item, saidScam) { return item.scam === !!saidScam; },
    /* split a call script into speaker turns; other channels stay one bubble. Text itself is never changed. */
    turns(item) {
      if (item.channel !== 'call_script') return [{ who: '', text: item.text }];
      const out = []; let m, last = null, lastEnd = 0; SPEAKER.lastIndex = 0;
      while ((m = SPEAKER.exec(item.text))) {
        if (last) out.push({ who: last, text: item.text.slice(lastEnd, m.index).trim() });
        else if (m.index > 0) out.push({ who: '', text: item.text.slice(0, m.index).trim() });
        last = m[1]; lastEnd = SPEAKER.lastIndex;
      }
      if (last) out.push({ who: last, text: item.text.slice(lastEnd).trim() }); else out.push({ who: '', text: item.text });
      return out.filter(t => t.text);
    },
    /* best per level: higher score wins; on a tie the bigger round wins */
    better(old, s, t) { return !old || s > old.s || (s === old.s && t > old.t); },
    verdict(s, t) {
      const r = t ? s / t : 0;
      if (r === 1) return 'Full marks! Scammers ka kaam aapke saamne nahi chalega. Ab family group mein bhi share karo.';
      if (r >= 0.8) return 'Bahut badhiya. Bas ek do tricks aur seekh lo, phir koi aapko fasa nahi payega.';
      if (r >= 0.5) return 'Theek thaak. Red flags dobara padho: urgency, link, OTP, paisa pehle. Practice se aur pakka hoga.';
      return 'Abhi thoda risk hai. Scam Encyclopedia padho aur ek baar phir khelo. Shak ho to pehle official number se confirm karo.';
    },
    shareText(s, t, level) {
      const lv = level === 'all' ? '' : ' (' + level + ' level)';
      return 'Maine CyberWithMadhav ka "Scam ya Nahi?" game khela' + lv + ' aur ' + s + '/' + t + ' sahi pehchane. Aap kitne pakad paoge? ' + PAGE;
    },
    shareUrl(s, t, level) { return 'https://wa.me/?text=' + encodeURIComponent(L.shareText(s, t, level)); }
  };
  window.CWMGame = L;

  /* ---------- state ---------- */
  let data = null;
  const st = { level: 'all', shuffle: true, deck: [], i: 0, points: 0, answered: false, missed: [] };
  const CH_ICON = {
    sms: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z',
    whatsapp: 'M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3z',
    call_script: 'M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z',
    email: 'M3 5h18v14H3zM3 6l9 7 9-7'
  };
  function icon(d) {
    const ns = 'http://www.w3.org/2000/svg', s = document.createElementNS(ns, 'svg');
    s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('width', '20'); s.setAttribute('height', '20'); s.setAttribute('fill', 'none');
    s.setAttribute('stroke', 'currentColor'); s.setAttribute('stroke-width', '2'); s.setAttribute('stroke-linecap', 'round'); s.setAttribute('stroke-linejoin', 'round');
    const p = document.createElementNS(ns, 'path'); p.setAttribute('d', d); s.appendChild(p); return s;
  }
  const ext = (href, text) => el('a', { href, target: '_blank', rel: 'noopener noreferrer' }, [text, el('span', { class: 'sr-only', text: ' (opens in a new tab)' })]);
  const bestAll = () => store(BEST_KEY, {}) || {};
  const card = () => st.deck[st.i];

  function showBest() {
    const b = bestAll()[st.level];
    $('#g-best').textContent = b ? b.s + ' / ' + b.t : 'none yet';
  }

  function updateScore() {
    $('#g-points').textContent = String(st.points);
    $('#g-total').textContent = String(st.i + (st.answered ? 1 : 0));
    $('#g-pos').textContent = String(Math.min(st.i + 1, st.deck.length));
    $('#g-count').textContent = String(st.deck.length);
    $('#g-fill').style.width = (st.deck.length ? ((st.i + (st.answered ? 1 : 0)) / st.deck.length) * 100 : 0) + '%';
  }

  function chips() {
    const n = { all: data.items.length, ...data.meta.levels };
    const label = { all: 'All', easy: 'Easy', medium: 'Medium', hard: 'Hard' };
    $('#g-level').replaceChildren(...LEVELS.map(k => el('button', { type: 'button', class: 'chip', 'data-id': k, 'aria-pressed': String(st.level === k) }, [label[k], el('span', { class: 'n', text: String(n[k] || 0) })])));
  }

  function newGame(focus) {
    const pool = L.filter(data.items, st.level);
    st.deck = st.shuffle ? L.shuffle(pool) : pool;
    st.i = 0; st.points = 0; st.answered = false; st.missed = [];
    document.querySelectorAll('#g-level .chip').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.id === st.level)));
    $('#g-shuffle').setAttribute('aria-pressed', String(st.shuffle));
    const p = new URLSearchParams(location.search);
    if (st.level === 'all') p.delete('level'); else p.set('level', st.level);
    const qs = p.toString(); history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
    $('#g-end').hidden = true; $('#g-play').hidden = false;
    showBest(); render(focus);
  }

  function render(focus) {
    const c = card(); const ph = $('#g-card');
    ph.classList.remove('right', 'wrong', 'out-l', 'out-r', 'dragging'); ph.style.transform = '';
    ph.dataset.channel = c.channel;
    $('#g-ico').replaceChildren(icon(CH_ICON[c.channel] || CH_ICON.sms));
    $('#g-chan').textContent = data.meta.channels[c.channel] || c.channel;
    $('#g-sender').textContent = c.sender;
    $('#g-lvl').textContent = c.level;
    const isCall = c.channel === 'call_script';
    $('#g-body').replaceChildren(...L.turns(c).map(t => el('div', { class: 'g-bubble' + (t.who === 'Aap' || t.who === 'You' ? ' me' : ''), lang: 'hi-Latn' }, [
      t.who ? el('span', { class: 'g-speaker mono', text: t.who }) : null,
      el('p', { text: t.text })
    ])).concat(isCall ? [el('p', { class: 'g-note small muted', text: 'Call transcript' })] : []));
    $('#g-result').replaceChildren(); $('#g-next-row').hidden = true;
    $('#g-btn-scam').disabled = false; $('#g-btn-safe').disabled = false;
    st.answered = false; updateScore();
    if (!reduce) { ph.classList.remove('enter'); void ph.offsetWidth; ph.classList.add('enter'); }
    if (focus) ph.focus({ preventScroll: false });
  }

  function answer(saidScam) {
    if (st.answered || !card()) return;
    const c = card(), right = L.isRight(c, saidScam);
    st.answered = true; if (right) st.points++; else st.missed.push(c);
    $('#g-btn-scam').disabled = true; $('#g-btn-safe').disabled = true;
    const ph = $('#g-card'); ph.classList.remove('dragging'); ph.style.transform = '';
    ph.classList.add(right ? 'right' : 'wrong');
    const truth = c.scam ? 'Ye scam tha.' : 'Ye safe tha.';
    const kids = [
      el('p', { class: 'g-verdict ' + (right ? 'ok' : 'no') }, [el('b', { text: right ? 'Sahi jawab! ' : 'Galat. ' }), el('span', { text: truth + (right ? '' : ' Aapne ' + (saidScam ? 'Scam' : 'Safe') + ' chuna.') })]),
      el('p', { class: 'c-k mono', text: c.scam ? 'red flags' : 'why it looks safe' }),
      el('ul', { class: 'g-tells', lang: 'hi-Latn' }, c.tells.map(t => el('li', { text: t }))),
      el('p', { class: 'g-why', lang: 'hi-Latn', text: c.why })
    ];
    if (c.report) kids.push(el('p', { class: 'g-report' }, [el('span', { class: 'c-k mono', text: 'report: ' }), el('a', { href: 'tel:1930', text: '1930' }), el('span', { text: ' / ' }), ext('https://cybercrime.gov.in', 'cybercrime.gov.in')]));
    if (c.link) kids.push(el('p', { class: 'g-link small' }, [el('span', { class: 'muted', text: 'Full scam card: ' }), el('a', { href: c.link.href, text: c.link.name })]));
    $('#g-result').replaceChildren(...kids);
    updateScore();
    const last = st.i >= st.deck.length - 1;
    $('#g-next').textContent = last ? 'See my score' : 'Next card';
    $('#g-next-row').hidden = false;
    $('#g-next').focus({ preventScroll: true });
    const r = $('#g-result').getBoundingClientRect();
    if (r.bottom > innerHeight) $('#g-result').scrollIntoView({ block: 'nearest', behavior: reduce ? 'instant' : 'smooth' });
  }

  function next() {
    if (!st.answered) return;
    if (st.i >= st.deck.length - 1) return end();
    st.i++; render(true);
  }

  function end() {
    const s = st.points, t = st.deck.length;
    const all = bestAll(), old = all[st.level], nb = L.better(old, s, t);
    if (nb) { all[st.level] = { s, t, at: new Date().toISOString().slice(0, 10) }; save(BEST_KEY, all); }
    $('#g-play').hidden = true; const e = $('#g-end'); e.hidden = false;
    $('#g-end-points').textContent = String(s); $('#g-end-total').textContent = String(t);
    $('#g-end-msg').textContent = L.verdict(s, t);
    $('#g-end-best').textContent = nb ? (old ? 'New best score for this level! Old best was ' + old.s + ' / ' + old.t + '.' : 'First score saved as your best for this level.') : 'Your best for this level: ' + old.s + ' / ' + old.t + '.';
    $('#g-share').href = L.shareUrl(s, t, st.level);
    const m = st.missed;
    $('#g-missed').replaceChildren(...(m.length ? [
      el('p', { class: 'c-k mono', text: 'cards you missed' }),
      el('ul', { class: 'g-miss' }, m.map(c => el('li', null, [el('b', { text: (c.scam ? 'Scam: ' : 'Safe: ') }), el('span', { text: c.sender }), c.link ? el('span', null, [' ', el('a', { href: c.link.href, text: 'read more' })]) : null])))
    ] : []));
    showBest(); updateScore();
    e.focus();
  }

  /* ---------- swipe on touch (left = Scam, right = Safe) ---------- */
  function swipe() {
    const ph = $('#g-card'); let x0 = null, y0 = 0, id = null, dx = 0;
    ph.addEventListener('pointerdown', e => {
      if (e.pointerType === 'mouse' || st.answered) return;
      x0 = e.clientX; y0 = e.clientY; id = e.pointerId; dx = 0;
    });
    ph.addEventListener('pointermove', e => {
      if (x0 == null || e.pointerId !== id) return;
      dx = e.clientX - x0; const dy = e.clientY - y0;
      if (Math.abs(dy) > Math.abs(dx) && Math.abs(dx) < 12) return;
      ph.classList.add('dragging');
      ph.classList.toggle('lean-l', dx < -30); ph.classList.toggle('lean-r', dx > 30);
      if (!reduce) ph.style.transform = 'translateX(' + dx + 'px) rotate(' + (dx / 25) + 'deg)';
    });
    const up = e => {
      if (x0 == null || e.pointerId !== id) return;
      x0 = null; ph.classList.remove('dragging', 'lean-l', 'lean-r'); ph.style.transform = '';
      if (Math.abs(dx) > 70) answer(dx < 0);
    };
    ph.addEventListener('pointerup', up); ph.addEventListener('pointercancel', e => { dx = 0; up(e); });
  }

  function keys() {
    document.addEventListener('keydown', e => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      const a = document.activeElement;
      if (a && /^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)) return;
      const pal = document.getElementById('palette'); if (pal && pal.open) return;
      if ($('#g-play').hidden) return;
      if (!st.answered && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) { e.preventDefault(); answer(e.key === 'ArrowLeft'); }
      else if (st.answered && e.key === 'Enter' && a && a.id !== 'g-next' && a.tagName !== 'A' && a.tagName !== 'BUTTON') { e.preventDefault(); next(); }
    });
  }

  async function init() {
    try { data = await getJSON('data/game.json'); }
    catch (e) { $('#g-sender').textContent = 'Could not load the game'; $('#g-chan').textContent = 'Error'; $('#g-body').replaceChildren(el('p', { text: 'Refresh the page. If you lost money to a scam, call 1930 now.' })); return; }
    const lv = new URLSearchParams(location.search).get('level');
    if (LEVELS.includes(lv)) st.level = lv;
    chips();
    $('#g-level').addEventListener('click', e => { const b = e.target.closest('.chip'); if (b) { st.level = b.dataset.id; newGame(false); } });
    $('#g-shuffle').addEventListener('click', () => { st.shuffle = !st.shuffle; newGame(false); });
    $('#g-restart').addEventListener('click', () => newGame(true));
    $('#g-again').addEventListener('click', () => newGame(true));
    $('#g-btn-scam').addEventListener('click', () => answer(true));
    $('#g-btn-safe').addEventListener('click', () => answer(false));
    $('#g-next').addEventListener('click', next);
    swipe(); keys();
    newGame(false);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
