/* CyberWithMadhav CTF Arena.
 * Two backends, never mixed:
 *   API mode      Flask (backend/ctf.py) checks answers with HMAC; ranked runs reach the leaderboard.
 *   Practice mode answers checked in the browser with PBKDF2 verifiers from data/ctf.json; the
 *                 explanation is AES-GCM encrypted with a key derived from the right answer.
 *                 Scores stay in localStorage on this device.
 * DOM is built with textContent only (no innerHTML). CSP: script-src 'self'.
 */
(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const root = document.documentElement;
  const body = document.body;

  /* ---------------- storage ---------------- */
  const LS = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } },
    del(k) { try { localStorage.removeItem(k); } catch (e) { /* ignore */ } }
  };
  const K = { prefs: 'cwm-ctf-prefs', prog: 'cwm-ctf-practice-v2', sess: 'cwm-ctf-session', quotes: 'cwm-ctf-quotes', ui: 'cwm-ctf-ui' };
  const mqReduce = window.matchMedia ? matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  const prefs = Object.assign({ sound: false, relaxed: false, free: false, motion: false, lite: false }, LS.get(K.prefs, {}));
  const freshProgress = () => ({ v: 2, levels: {}, solved: {}, xp: 0, streak: { cur: 0, best: 0, last: null, shields: 0 } });
  let P = LS.get(K.prog, null);
  if (!P || P.v !== 2) P = freshProgress();
  const saveP = () => LS.set(K.prog, P);
  let session = LS.get(K.sess, {}) || {};
  const calm = () => prefs.motion || mqReduce.matches;

  /* ---------------- tiny DOM builder (textContent only) ---------------- */
  function el(tag, attrs, ...kids) {
    const n = document.createElement(tag);
    if (attrs) for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k === 'class') n.className = v;
      else if (k === 'text') n.textContent = v;
      else if (k.startsWith('on') && typeof v === 'function') n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? '' : String(v));
    }
    for (const c of kids.flat()) {
      if (c == null || c === false) continue;
      n.append(c.nodeType ? c : document.createTextNode(String(c)));
    }
    return n;
  }
  const SVGNS = 'http://www.w3.org/2000/svg';
  function svg(tag, attrs) {
    const n = document.createElementNS(SVGNS, tag);
    for (const [k, v] of Object.entries(attrs || {})) { if (k === 'text') n.textContent = v; else n.setAttribute(k, String(v)); }
    return n;
  }
  const clear = n => { while (n && n.firstChild) n.removeChild(n.firstChild); return n; };
  const setText = (id, t) => { const n = document.getElementById(id); if (n) n.textContent = t; return n; };
  const show = (n, on) => { if (typeof n === 'string') n = document.getElementById(n); if (n) n.hidden = !on; return n; };
  const fmtTime = s => { s = Math.max(0, Math.round(s)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };
  const fmtWait = s => (s >= 120 ? Math.ceil(s / 60) + ' minutes' : s + ' seconds');
  const plural = (n, one, many) => n + ' ' + (n === 1 ? one : (many || one + 's'));

  /* ---------------- answer normalisation (must match tools/build_ctf.py and backend/ctf.py) ---------------- */
  const n1 = s => String(s).normalize('NFKC').trim().replace(/\s+/g, ' ').toLowerCase();
  /* typed answers: drop http(s)://, www. and a trailing slash, and a unit word after a number */
  function loose(s) {
    s = s.replace(/^https?:\/\//, '').replace(/^www\./, '');
    if (s.indexOf(' ') < 0 && s.length > 1) s = s.replace(/\/+$/, '');
    return s.replace(/^([0-9][0-9.]*) ?(?:bits?|hosts?|times|runs|secs?|seconds|s)$/, '$1');
  }
  function normalise(s, type) {
    if (type === 'multi') return String(s).split('|').map(n1).filter(Boolean).sort().join('|');
    if (type === 'order') return String(s).split('|').map(n1).join('|');
    let t = n1(s);
    if (type === 'flag' && t && !t.startsWith('cwm{')) t = 'cwm{' + t.replace(/^[{}]+|[{}]+$/g, '') + '}';
    else if (type === 'text') t = loose(t);
    return t;
  }

  /* ---------------- practice crypto: PBKDF2 verifier + AES-GCM explanation ---------------- */
  const te = new TextEncoder();
  const hex = b => Array.from(b, x => x.toString(16).padStart(2, '0')).join('');
  const unb64 = s => Uint8Array.from(atob(s), ch => ch.charCodeAt(0));
  let DATA = null, QUOTES = null, S = null;
  async function derive(salt, norm) {
    const key = await crypto.subtle.importKey('raw', te.encode(norm), 'PBKDF2', false, ['deriveBits']);
    const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt: te.encode(salt), iterations: DATA.kdf.iterations }, key, 512);
    return new Uint8Array(bits);
  }
  async function check(c, answer) {
    const norm = normalise(answer, c.type);
    if (!norm) return { ok: false };
    const dk = await derive(c.salt, norm);
    const i = c.verifiers.indexOf(hex(dk.slice(0, 32)));
    return i < 0 ? { ok: false } : { ok: true, i, key: dk.slice(32) };
  }
  async function decryptExp(c, i, keyBytes) {
    try {
      const e = c.exp[i];
      const k = await crypto.subtle.importKey('raw', keyBytes, 'AES-GCM', false, ['decrypt']);
      const pt = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: unb64(e.iv) }, k, unb64(e.ct));
      return new TextDecoder().decode(pt);
    } catch (e) { return null; }
  }
  function perms(a) {
    if (a.length <= 1) return [a.slice()];
    const out = [];
    a.forEach((x, i) => perms(a.slice(0, i).concat(a.slice(i + 1))).forEach(p => out.push([x].concat(p))));
    return out;
  }
  const solveCache = new Map();
  /* Option-based questions can be solved by trying the options; used for 50/50 and to reveal the answer
     after the last attempt. Typed answers and flags cannot be revealed this way, by design. */
  async function solveLocally(c) {
    if (solveCache.has(c.id)) return solveCache.get(c.id);
    const o = c.options || [];
    let cands = [];
    if (c.type === 'mcq') cands = o.map(x => [x]);
    else if (c.type === 'multi') { for (let m = 1; m < (1 << o.length); m++) cands.push(o.filter((_, i) => m & (1 << i))); }
    else if (c.type === 'order' && o.length <= 6) cands = perms(o);
    let found = null;
    for (const cand of cands) {
      const r = await check(c, cand.join('|'));
      if (r.ok) { found = Object.assign({ answer: cand }, r); break; }
    }
    solveCache.set(c.id, found);
    return found;
  }

  /* ---------------- seeded shuffle ---------------- */
  function mulberry32(a) {
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function seedFrom(str) { let h = 2166136261; for (const ch of String(str)) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }
  function shuffle(arr, rnd) { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }

  /* ---------------- scoring (mirrors backend/ctf.py) ---------------- */
  function pyRound(x) { // Python round(): ties to even
    const f = Math.floor(x), d = x - f;
    if (Math.abs(d - 0.5) < 1e-9) return f % 2 === 0 ? f : f + 1;
    return Math.round(x);
  }
  function earned(base, type, attempt, hints) {
    if ((type === 'mcq' || type === 'multi') && attempt > 1) return 0;
    const cost = S.hintCost;
    let p = base * (1 - (hints ? cost[Math.min(hints, cost.length) - 1] : 0));
    p -= S.wrongPenalty * Math.max(0, attempt - S.wrongPenaltyFromAttempt + 1);
    return Math.max(0, pyRound(p));
  }
  const multFor = combo => Math.min(S.streakCap, 1 + S.streakStep * combo);
  const bonusFor = (elapsed, soft, relaxed) => (relaxed ? 0 : S.timeBonusMax * Math.max(0, 1 - elapsed / soft));
  function rankFor(xp) {
    let name = S.ranks[0][1], next = null;
    for (const [at, n] of S.ranks) { if (xp >= at) name = n; else { next = { at, name: n }; break; } }
    return { name, next };
  }
  const bandOf = pct => (pct >= S.bands.high[0] ? 'high' : pct >= S.bands.mid[0] ? 'mid' : 'low');
  const istDay = (ms = Date.now()) => Math.floor((ms / 1000 + 19800) / 86400);

  const trackById = id => DATA.tracks.find(t => t.id === id);
  const levelById = (t, id) => t && t.levels.find(l => l.id === id);
  const LEVEL_IDS = () => DATA.tracks[0].levels.map(l => l.id);

  /* ---------------- progress: server and practice are kept apart ---------------- */
  let MODE = 'checking';            // checking | api | practice
  let API = '';
  let server = null;                // /api/me payload when signed in
  const useServer = () => MODE === 'api' && !!session.token;

  function levelInfo(tid, lid) {
    const t = trackById(tid), l = levelById(t, lid);
    const max = l ? l.maxPoints : 0;
    if (useServer() && server && server.progress) {
      const c = (server.progress[tid] || {})[lid] || {};
      return { score: c.score || 0, max: c.max || max, pct: c.pct || 0, runs: null };
    }
    const c = P.levels[tid + '/' + lid] || {};
    return { score: c.bestScore || 0, max, pct: c.best || 0, runs: c.runs || 0 };
  }
  function trackInfo(tid) {
    const t = trackById(tid);
    let score = 0, max = 0;
    t.levels.forEach(l => { const i = levelInfo(tid, l.id); score += i.score; max += i.max; });
    return { score, max, pct: max ? Math.round(100 * score / max) : 0 };
  }
  function totals() {
    let score = 0;
    DATA.tracks.forEach(t => { score += trackInfo(t.id).score; });
    const max = S.totalPoints;
    if (useServer() && server) {
      return { score: server.score || 0, max, pct: max ? Math.round(100 * (server.score || 0) / max) : 0, xp: server.xp || 0,
        streak: (server.streak || {}).current || 0, bestStreak: (server.streak || {}).best || 0 };
    }
    const st = P.streak || {};
    const alive = st.last != null && istDay() - st.last <= 1 + (st.shields || 0);
    return { score, max, pct: max ? Math.round(100 * score / max) : 0, xp: P.xp || 0, streak: alive ? st.cur || 0 : 0, bestStreak: st.best || 0 };
  }
  function isUnlocked(tid, lid) {
    if (prefs.free) return true;
    const ids = LEVEL_IDS(), i = ids.indexOf(lid);
    return i <= 0 || levelInfo(tid, ids[i - 1]).pct >= S.unlockPercent;
  }
  function bumpStreak() { // same rules as the server: IST days, a shield every 5 days (max 2)
    const st = P.streak = P.streak || { cur: 0, best: 0, last: null, shields: 0 };
    const day = istDay();
    if (st.last === day) return;
    if (st.last != null && day === st.last + 1) st.cur += 1;
    else if (st.last != null && day - st.last - 1 > 0 && day - st.last - 1 <= st.shields) { st.shields -= day - st.last - 1; st.cur += 1; }
    else st.cur = 1;
    if (st.cur % 5 === 0) st.shields = Math.min(2, st.shields + 1);
    st.best = Math.max(st.best || 0, st.cur); st.last = day;
  }

  /* ---------------- sound (WebAudio, muted by default) ---------------- */
  let actx = null;
  function tone(freq, dur, type, when, gain) {
    if (!prefs.sound) return;
    try {
      actx = actx || new (window.AudioContext || window.webkitAudioContext)();
      if (actx.state === 'suspended') actx.resume();
      const t0 = actx.currentTime + (when || 0);
      const o = actx.createOscillator(), g = actx.createGain();
      o.type = type || 'sine'; o.frequency.setValueAtTime(freq, t0);
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(gain || 0.12, t0 + 0.015);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
      o.connect(g).connect(actx.destination); o.start(t0); o.stop(t0 + dur + 0.02);
    } catch (e) { /* audio not available */ }
  }
  const sfx = {
    ok() { tone(660, 0.12, 'triangle'); tone(990, 0.18, 'triangle', 0.09); },
    bad() { tone(180, 0.22, 'sawtooth', 0, 0.06); },
    tick() { tone(1200, 0.05, 'square', 0, 0.03); },
    combo(n) { tone(520 + n * 60, 0.1, 'triangle', 0, 0.08); },
    win() { [523, 659, 784, 1047].forEach((f, i) => tone(f, 0.22, 'triangle', i * 0.11)); },
    low() { tone(330, 0.3, 'sine', 0, 0.08); tone(262, 0.4, 'sine', 0.2, 0.08); }
  };

  /* ---------------- live region, toast ---------------- */
  function announce(msg) { const n = $('#sr-live'); if (!n) return; n.textContent = ''; setTimeout(() => { n.textContent = msg; }, 40); }
  let toastT = 0;
  function toast(msg) {
    const n = $('#toast'); if (!n) return;
    n.textContent = msg; n.hidden = false; n.classList.add('show');
    clearTimeout(toastT); toastT = setTimeout(() => { n.classList.remove('show'); n.hidden = true; }, 2800);
  }

  /* ---------------- effects: confetti, embers, level-up ---------------- */
  const fx = { cv: null, ctx: null, parts: [], raf: 0 };
  function fxBurst(kind, count) {
    if (calm()) return;
    if (prefs.lite) count = Math.round(count / 3);
    fx.cv = fx.cv || $('#fx'); if (!fx.cv) return;
    fx.ctx = fx.ctx || fx.cv.getContext('2d');
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    fx.cv.width = innerWidth * dpr; fx.cv.height = innerHeight * dpr; fx.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const W = innerWidth, H = innerHeight;
    const conf = ['#8B5CF6', '#B79CFF', '#34D399', '#22D3EE', '#FBBF24', '#F472B6'];
    const emb = ['#FB923C', '#F59E0B', '#EF4444', '#FDBA74'];
    for (let i = 0; i < count; i++) {
      if (kind === 'confetti') {
        fx.parts.push({ k: 'c', x: W / 2 + (Math.random() - 0.5) * W * 0.3, y: H * 0.35, vx: (Math.random() - 0.5) * 11, vy: -Math.random() * 12 - 4,
          g: 0.32, s: 5 + Math.random() * 6, r: Math.random() * 6, vr: (Math.random() - 0.5) * 0.3, c: conf[i % conf.length], life: 150 + Math.random() * 60 });
      } else {
        fx.parts.push({ k: 'e', x: Math.random() * W, y: H + Math.random() * 40, vx: (Math.random() - 0.5) * 0.8, vy: -1.2 - Math.random() * 2.2,
          g: -0.004, s: 1.5 + Math.random() * 2.8, r: 0, vr: 0, c: emb[i % emb.length], life: 160 + Math.random() * 120 });
      }
    }
    if (!fx.raf) fx.raf = requestAnimationFrame(fxLoop);
  }
  function fxLoop() {
    const c = fx.ctx, W = innerWidth, H = innerHeight;
    c.clearRect(0, 0, W, H);
    fx.parts = fx.parts.filter(p => p.life > 0 && p.y < H + 60 && p.y > -80);
    for (const p of fx.parts) {
      p.vy += p.g; p.x += p.vx; p.y += p.vy; p.r += p.vr; p.life -= 1; p.vx *= 0.99;
      c.globalAlpha = Math.max(0, Math.min(1, p.life / 60));
      c.fillStyle = p.c;
      if (p.k === 'c') { c.save(); c.translate(p.x, p.y); c.rotate(p.r); c.fillRect(-p.s / 2, -p.s / 4, p.s, p.s / 2); c.restore(); }
      else { c.shadowColor = p.c; c.shadowBlur = 8; c.beginPath(); c.arc(p.x + Math.sin(p.life / 9) * 1.5, p.y, p.s, 0, 6.283); c.fill(); c.shadowBlur = 0; }
    }
    c.globalAlpha = 1;
    fx.raf = fx.parts.length ? requestAnimationFrame(fxLoop) : 0;
    if (!fx.raf) c.clearRect(0, 0, W, H);
  }
  function levelUp(small, big) {
    announce(small + ': ' + big);
    if (calm()) return;
    const n = $('#levelup'); if (!n) return;
    setText('lu-small', small); setText('lu-big', big);
    n.classList.remove('show'); void n.offsetWidth; n.classList.add('show');
    setTimeout(() => n.classList.remove('show'), 1700);
  }
  function shake(n) { if (!n || calm()) return; n.classList.remove('shake'); void n.offsetWidth; n.classList.add('shake'); }

  /* rings use pathLength=100, so the dash is the percentage */
  function setRing(svgEl, pct, band) {
    if (!svgEl) return;
    const fg = svgEl.querySelector('.ring-fg');
    fg.setAttribute('stroke-dasharray', Math.max(0, Math.min(100, pct)) + ' 100');
    fg.classList.remove('low', 'mid', 'high');
    if (band) fg.classList.add(band);
  }
  function segRing(tid) {
    const t = trackById(tid);
    const s = svg('svg', { class: 'seg-ring', viewBox: '0 0 60 60', 'aria-hidden': 'true' });
    t.levels.forEach((l, i) => {
      const pct = levelInfo(tid, l.id).pct, off = -(i * 100 + 3);
      s.append(svg('circle', { class: 's-bg', cx: 30, cy: 30, r: 24, pathLength: 300, 'stroke-dasharray': '94 206', 'stroke-dashoffset': off }));
      if (pct > 0) s.append(svg('circle', { class: 's-fg s' + i, cx: 30, cy: 30, r: 24, pathLength: 300,
        'stroke-dasharray': (94 * pct / 100).toFixed(1) + ' ' + (300 - 94 * pct / 100).toFixed(1), 'stroke-dashoffset': off }));
    });
    return s;
  }

  /* ---------------- API client ---------------- */
  function apiBase() {
    const m = $('meta[name="cwm-api"]');
    const v = ((m && m.content) || '').trim().replace(/\/+$/, '');
    if (v) return v;
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') return 'http://127.0.0.1:5000';
    return '';
  }
  async function api(path, opts) {
    const o = opts || {};
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), o.timeout || 9000);
    const headers = {};
    if (o.body) headers['Content-Type'] = 'application/json';
    if (session.token) headers.Authorization = 'Bearer ' + session.token;
    try {
      const r = await fetch(API + '/api' + path, { method: o.method || 'GET', headers, body: o.body ? JSON.stringify(o.body) : undefined,
        signal: ctl.signal, credentials: 'omit', cache: 'no-store' });
      let j = {};
      try { j = await r.json(); } catch (e) { j = {}; }
      j.status = r.status;
      if (!r.ok) j.ok = false;
      if (r.status === 401 && session.token) { session = {}; LS.del(K.sess); server = null; renderPlayer(); renderHero(); }
      if (r.status === 429) {
        const ra = parseInt(r.headers.get('Retry-After') || '0', 10);
        j.error = (j.error || 'Too many requests.') + (ra ? ' Try again in ' + fmtWait(ra) + '.' : ' Please wait a little.');
      }
      if (!j.ok && !j.error) j.error = 'The server said no (' + r.status + ').';
      return j;
    } catch (e) {
      return { ok: false, status: 0, error: 'Could not reach the scoreboard server.' };
    } finally { clearTimeout(timer); }
  }
  async function healthCheck() {
    API = apiBase();
    if (!API) { setMode('practice', 'none'); return; }
    setMode('checking');
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), 2500);
    let up = false;
    try { const r = await fetch(API + '/api/health', { signal: ctl.signal, credentials: 'omit', cache: 'no-store' }); up = r.ok; }
    catch (e) { up = false; } finally { clearTimeout(timer); }
    if (!up) { setMode('practice', 'down'); return; }
    setMode('api');
    await refreshServer();
  }
  function setMode(mode, why) {
    MODE = mode;
    const b = $('#mode-banner'), t = $('#mode-text');
    b.classList.remove('api', 'practice', 'checking'); b.classList.add(mode);
    const old = $('#mode-retry'); if (old) old.remove();
    if (mode === 'checking') t.textContent = 'Checking the scoreboard server...';
    else if (mode === 'api') t.textContent = 'Scoreboard server online. Join with a nickname and your ranked runs count on the leaderboard.';
    else if (why === 'down') {
      t.textContent = 'Practice mode: the scoreboard server is asleep or unreachable, so scores will not count on the leaderboard. Answers are checked in your browser and your best scores stay on this device.';
      b.append(el('button', { type: 'button', class: 'btn btn-ghost small', id: 'mode-retry', text: 'Try again', onclick: () => healthCheck().then(rerender) }));
    } else t.textContent = 'Practice mode: answers are checked in your browser and your best scores stay on this device.';
    root.setAttribute('data-ctf-mode', mode);
    renderPlayer(); renderBoard(); renderHero();
  }
  async function refreshServer() {
    if (MODE !== 'api') return;
    if (session.token) {
      const me = await api('/me');
      server = me.ok ? me : null;
    } else server = null;
    renderPlayer(); renderBoard(); renderHero();
  }

  /* ---------------- player card ---------------- */
  function renderPlayer() {
    const inApi = MODE === 'api';
    show('player-api', inApi); show('player-local', !inApi);
    const signed = inApi && !!session.token;
    show('join-form', inApi && !signed);
    const rec = $('#recover-form'); if (rec) rec.closest('details').hidden = signed;
    show('player-in', signed);
    if (signed) setText('player-nick', session.nick || 'player');
    const pl = $('#player-local');
    if (pl && !inApi) {
      const p = pl.querySelector('p');
      if (p) p.textContent = MODE === 'checking' ? 'Checking for the scoreboard server...'
        : 'Practice mode keeps your best scores in this browser only. Nothing is sent anywhere.';
    }
  }
  const NICK_RE = /^[A-Za-z0-9._-]{3,20}$/;
  function wirePlayer() {
    $('#join-form').addEventListener('submit', async e => {
      e.preventDefault();
      const inp = $('#nick'), err = $('#nick-error'), nick = inp.value.trim();
      err.textContent = '';
      inp.removeAttribute('aria-invalid');
      if (!NICK_RE.test(nick)) { err.textContent = 'Use 3 to 20 letters, numbers, dot, dash or underscore.'; inp.setAttribute('aria-invalid', 'true'); inp.focus(); return; }
      const btn = e.submitter || $('#join-form button'); btn.disabled = true;
      const r = await api('/auth/guest', { method: 'POST', body: { nick } });
      btn.disabled = false;
      if (!r.ok) { err.textContent = r.error; inp.setAttribute('aria-invalid', 'true'); inp.focus(); return; }
      session = { token: r.token, nick: r.user.nick }; LS.set(K.sess, session);
      setText('recovery-code', r.recovery_code); show('recovery-box', true);
      await refreshServer(); rerender();
      announce('Joined as ' + r.user.nick + '. Save your recovery code.');
      $('#copy-recovery').focus();
    });
    $('#recover-form').addEventListener('submit', async e => {
      e.preventDefault();
      const inp = $('#recover-code'), err = $('#recover-error');
      err.textContent = '';
      const code = inp.value.replace(/[^0-9a-f]/gi, '');
      if (code.length !== 16) { err.textContent = 'A recovery code has 16 letters and numbers, like AB12-CD34-EF56-7890.'; inp.focus(); return; }
      const r = await api('/auth/recover', { method: 'POST', body: { code } });
      if (!r.ok) { err.textContent = r.error; inp.focus(); return; }
      session = { token: r.token, nick: r.user.nick }; LS.set(K.sess, session);
      inp.value = '';
      setText('recovery-code', r.recovery_code); show('recovery-box', true);
      await refreshServer(); rerender();
      announce('Welcome back, ' + r.user.nick + '. Your old recovery code no longer works; save the new one.');
    });
    $('#copy-recovery').addEventListener('click', () => copyText($('#recovery-code').textContent, 'Recovery code copied'));
    $('#sign-out').addEventListener('click', () => {
      if (!window.confirm('Sign out on this device? You will need your recovery code to sign back in.')) return;
      session = {}; LS.del(K.sess); server = null; show('recovery-box', false);
      renderPlayer(); renderBoard(); rerender();
      announce('Signed out.');
    });
  }
  async function copyText(t, msg) {
    try { await navigator.clipboard.writeText(t); toast(msg || 'Copied'); }
    catch (e) { toast('Copy failed. Select the text and copy it manually.'); }
  }

  /* ---------------- leaderboard (API only) / your best (practice) ---------------- */
  let boardScope = 'overall';
  async function renderBoard() {
    const list = $('#board-list'), note = $('#board-note'), tabs = $('#board-tabs');
    if (!list || !DATA) return;
    if (MODE !== 'api') {
      setText('board-title', 'Your best'); tabs.hidden = true; clear(list);
      const rows = [];
      DATA.tracks.forEach(t => t.levels.forEach(l => { const i = levelInfo(t.id, l.id); if (i.runs) rows.push({ t, l, i }); }));
      rows.sort((a, b) => b.i.pct - a.i.pct || b.i.score - a.i.score);
      rows.slice(0, 6).forEach(r => list.append(el('li', null, el('span', null, r.t.name + ' / ' + r.l.name,
        el('span', { class: 'b-sub', text: ' ' + plural(r.i.runs, 'run') })), el('span', { class: 'b-val', text: r.i.pct + '%' }))));
      if (!rows.length) list.append(el('li', { class: 'empty', text: 'Finish a level to see your best scores here.' }));
      note.textContent = MODE === 'checking' ? '' : 'The public leaderboard appears when the scoreboard server is online. Practice scores never mix with server scores.';
      return;
    }
    setText('board-title', 'Leaderboard'); tabs.hidden = false;
    $$('button', tabs).forEach(b => b.setAttribute('aria-selected', String(b.dataset.scope === boardScope)));
    const r = await api('/leaderboard?scope=' + encodeURIComponent(boardScope) + '&limit=10');
    clear(list);
    if (!r.ok) { list.append(el('li', { class: 'empty', text: r.error })); return; }
    r.rows.forEach(row => {
      const me = session.nick && row.nick === session.nick;
      const val = boardScope === 'streak' ? plural(row.streak, 'day') : row.score + ' marks';
      const sub = boardScope === 'streak' ? ' best ' + row.best : boardScope === 'overall' ? ' ' + row.xp + ' XP' : '';
      list.append(el('li', { class: me ? 'me' : null }, el('span', null, row.nick, me ? ' (you)' : '', el('span', { class: 'b-sub', text: sub })),
        el('span', { class: 'b-val', text: val })));
    });
    if (!r.rows.length) list.append(el('li', { class: 'empty', text: 'No scores yet. Be the first on the board.' }));
    note.textContent = boardScope === 'weekly' ? 'Week ' + (r.week || '') + ', India time. First ranked solves only.'
      : boardScope === 'streak' ? 'Days in a row with at least one ranked solve (India time).' : 'First ranked solve of each question counts. Free roam does not.';
  }

  /* ---------------- hero ---------------- */
  function renderHero() {
    if (!DATA) return;
    const T = totals(), rk = rankFor(T.xp);
    setRing($('#ring-overall'), T.pct, T.pct ? bandOf(T.pct) : null);
    setText('ov-pct', T.pct + '%'); setText('ov-rank', useServer() && server ? server.rank : rk.name);
    setText('ov-xp', String(T.xp)); setText('ov-score', T.score + ' / ' + T.max); setText('ov-streak', String(T.streak));
    setText('ov-next-rank', (rk.next ? (rk.next.at - T.xp) + ' XP to ' + rk.next.name + '.' : 'Top rank reached. Keep the streak alive.')
      + (useServer() ? ' Server profile: ' + (session.nick || '') : MODE === 'api' ? ' Practice progress (join to rank).' : ' Practice progress on this device.'));
  }

  /* ---------------- hub / track / briefing ---------------- */
  const KIND = { mcq: 'Multiple choice', multi: 'Select all', order: 'Put in order', text: 'Type the answer', flag: 'Find the flag',
    command: 'Command', log: 'Log analysis', subnet: 'Subnetting', code: 'Read the code' };
  const kindLabel = c => (KIND[c.kind] || KIND[c.type] || c.type) + (c.kind !== c.type && c.type === 'mcq' ? ' quiz' : '');

  function renderHub() {
    const grid = clear($('#track-grid'));
    DATA.tracks.forEach(t => {
      const ti = trackInfo(t.id);
      const done = t.levels.filter(l => levelInfo(t.id, l.id).pct >= S.unlockPercent).length;
      grid.append(el('a', { class: 'card track-card', href: '#/track/' + t.id },
        el('div', { class: 'tc-top' }, el('span', { class: 'tc-emoji', 'aria-hidden': 'true', text: t.icon }), el('h3', { text: t.name })),
        el('p', { text: t.blurb }),
        el('div', { class: 'tc-foot' }, segRing(t.id),
          el('span', { class: 'tc-best' }, ti.pct + '%', el('small', { text: done + ' / 3 levels passed' })),
          t.id === 'pentest' ? el('span', { class: 'flame-tag', text: 'Ethics first' }) : null)));
    });
    renderBoard();
  }
  function renderTrack(t) {
    const ti = DATA.tracks.indexOf(t);
    setText('track-crumb', t.name); setText('track-kicker', '// track ' + (ti + 1) + ' of ' + DATA.tracks.length);
    setText('track-title', t.icon + ' ' + t.name); setText('track-blurb', t.blurb);
    show('ethics', t.id === 'pentest');
    const grid = clear($('#level-grid'));
    const ids = LEVEL_IDS();
    t.levels.forEach((l, i) => {
      const info = levelInfo(t.id, l.id), open = isUnlocked(t.id, l.id);
      const cls = 'card level-card' + (open ? '' : ' locked') + (info.pct >= S.unlockPercent ? ' done' : '');
      const bar = el('div', { class: 'bar', 'aria-hidden': 'true' }, el('span'));
      bar.firstChild.style.width = info.pct + '%';
      const best = info.score || info.runs ? 'Best: ' + info.pct + '% (' + info.score + ' / ' + info.max + ' marks)' : 'Not played yet';
      grid.append(el('div', { class: cls },
        el('h3', null, l.name, open ? null : el('span', { class: 'sr-only', text: ' (locked)' })),
        el('p', { class: 'lv-meta', text: plural(l.challenges.length, 'question') + ' · ' + l.points + ' marks each · ' + l.softSeconds + ' s soft timer' }),
        bar, el('p', { class: 'small muted', text: best }),
        open ? null : el('p', { class: 'lock-note', text: 'Locked. Score ' + S.unlockPercent + '% on ' + levelById(t, ids[i - 1]).name + ' to unlock it, or turn on Free roam.' }),
        open ? el('a', { class: 'btn btn-primary small', href: '#/brief/' + t.id + '/' + l.id, text: info.runs || info.score ? 'Play again' : 'Start' })
          : el('button', { class: 'btn btn-ghost small', type: 'button', disabled: true, text: 'Locked' })));
    });
  }
  function modeLine() {
    if (prefs.free) return 'Free roam: every level is open, and this run does not count toward your rank or the leaderboard.';
    if (useServer()) return 'Ranked: your first correct solve of each question counts on the leaderboard.';
    if (MODE === 'api') return 'Not joined yet: this run is practice and stays on this device. Join with a nickname on the Tracks page to rank.';
    return 'Practice: answers are checked in your browser and your best score is saved on this device only.';
  }
  function renderBrief(t, l) {
    setText('brief-track-link', t.name); $('#brief-track-link').href = '#/track/' + t.id;
    setText('brief-crumb', l.name); setText('brief-title', t.icon + ' ' + t.name + ': ' + l.name);
    $('#brief-back').href = '#/track/' + t.id;
    const types = Array.from(new Set(l.challenges.map(kindLabel)));
    const facts = clear($('#brief-facts'));
    [[String(l.challenges.length), 'questions'], [l.points + ' marks', 'per question, ' + l.maxPoints + ' in total'],
      [prefs.relaxed ? 'Off' : l.softSeconds + ' s', prefs.relaxed ? 'relaxed mode, no timers' : 'soft timer, early answers earn bonus XP'],
      ['1 or 5', 'attempts: 1 for choices, up to 5 typed (-2 marks from the 3rd)'], ['-25%', 'per hint, -50% for a second'],
      [String(types.length), types.join(', ')]]
      .forEach(([b, s]) => facts.append(el('li', null, el('b', { text: b }), el('span', { text: s }))));
    show('brief-ethics', t.id === 'pentest');
    const open = isUnlocked(t.id, l.id);
    setText('brief-mode', open ? modeLine() : 'This level is locked. Score ' + S.unlockPercent + '% on the previous level, or turn on Free roam.');
    const st = $('#brief-start'); st.disabled = !open; st.dataset.track = t.id; st.dataset.level = l.id;
  }

  /* ---------------- runs ---------------- */
  let run = null, lastResult = null, timerT = 0;
  async function startRun(tid, lid) {
    const t = trackById(tid), l = levelById(t, lid);
    if (!t || !l) return;
    if (!isUnlocked(tid, lid)) { toast('That level is locked.'); return; }
    const mode = prefs.free ? 'free' : 'ranked';
    let items;
    let id = 'local-' + Date.now().toString(36);
    const btn = $('#brief-start'); btn.disabled = true;
    if (useServer()) {
      const r = await api('/runs', { method: 'POST', body: { track: tid, level: lid, mode, relaxed: !!prefs.relaxed } });
      btn.disabled = false;
      if (!r.ok) { toast(r.error); setText('brief-mode', r.error); return; }
      id = r.run.id;
      items = r.run.challenges.map(c => ({ c, st: { attempts: 0, hints: c.hintsUsed || 0, hintTexts: [], gone: [], done: false, correct: false, points: 0, xp: 0 } }));
    } else {
      btn.disabled = false;
      const rnd = mulberry32(seedFrom(id));
      items = shuffle(l.challenges, rnd).map(c0 => {
        const c = Object.assign({}, c0);
        if (c.options && c.type !== 'order') c.options = shuffle(c.options, rnd);
        return { c, st: { attempts: 0, hints: 0, hintTexts: [], gone: [], done: false, correct: false, points: 0, xp: 0 } };
      });
    }
    run = { id, server: useServer(), t, l, mode, relaxed: !!prefs.relaxed, soft: l.softSeconds, items, idx: 0, score: 0, xp: 0,
      combo: 0, bestCombo: 0, started: Date.now(), rankBefore: rankFor(totals().xp).name, unlockedBefore: nextLevelOpen(t, l) };
    if (location.hash !== '#/play') location.hash = '#/play'; else route();
  }
  function nextLevelOpen(t, l) {
    const i = t.levels.indexOf(l), n = t.levels[i + 1];
    return n ? isUnlocked(t.id, n.id) : false;
  }

  /* ---------------- play ---------------- */
  function stopTimer() { clearInterval(timerT); timerT = 0; }
  function startTimer() {
    stopTimer();
    const tp = $('#ph-timer');
    tp.hidden = run.relaxed;
    tp.classList.remove('warn', 'over');
    if (run.relaxed) return;
    const said = {};
    const tick = () => {
      const it = run && run.items[run.idx];
      if (!it || it.st.done) { stopTimer(); return; }
      const left = run.soft - (Date.now() - run.qStart) / 1000;
      const s = Math.ceil(left);
      setText('ph-time', left >= 0 ? fmtTime(s) : '+' + fmtTime(-left));
      tp.setAttribute('aria-label', left >= 0 ? 'Time left ' + s + ' seconds' : 'Soft timer over');
      tp.classList.toggle('warn', left < 10 && left >= 0);
      tp.classList.toggle('over', left < 0);
      for (const m of [30, 10, 0]) if (s <= m && !said[m] && run.soft > m) {
        said[m] = true;
        announce(m ? m + ' seconds left.' : 'Soft timer is up. No marks lost, keep going.');
        if (m === 10) sfx.tick();
      }
    };
    tick(); timerT = setInterval(tick, 250);
  }
  function renderHead() {
    const n = run.items.length;
    setText('ph-where', run.t.name + ' / ' + run.l.name + (run.mode === 'free' ? ' · free roam' : run.server ? ' · ranked' : ' · practice'));
    setText('ph-count', 'Q ' + Math.min(run.idx + 1, n) + ' / ' + n);
    setText('ph-score', run.score + ' marks'); setText('ph-xp', run.xp + ' XP');
    const cb = $('#ph-combo');
    cb.hidden = run.combo < 2;
    cb.textContent = 'x' + multFor(run.combo).toFixed(1) + ' combo ' + run.combo;
    $('#ph-bar').style.width = (100 * run.items.filter(i => i.st.done).length / n) + '%';
    const dots = clear($('#ph-dots'));
    run.items.forEach((it, i) => dots.append(el('li', { class: (i === run.idx ? 'cur ' : '') + (it.st.done ? (it.st.correct ? 'ok' : 'bad') : '') })));
  }
  function renderPlay() {
    if (!run) return;
    const it = run.items[run.idx], c = it.c, st = it.st;
    renderHead();
    setText('q-type', kindLabel(c));
    const set = setText('q-set', c.set || ''); set.hidden = !c.set;
    updatePointsTag(it);
    setText('q-title', c.title); setText('q-prompt', c.prompt);
    show('q-code-wrap', !!c.code); setText('q-code', c.code || '');
    renderAnswer(it);
    const fb = $('#q-feedback'); fb.className = 'q-feedback'; fb.textContent = '';
    const ex = clear($('#q-explain')); ex.hidden = true;
    const ht = $('#q-hint-text'); ht.hidden = true; ht.textContent = '';
    show('q-submit', true); $('#q-submit').disabled = false;
    show('q-next', false);
    $('#q-card').classList.remove('flash-ok', 'shake');
    updateHintBtn(it);
    run.qStart = Date.now();
    startTimer();
    const tgt = $('#q-title'); tgt.focus({ preventScroll: true });
    if (!calm()) window.scrollTo({ top: Math.max(0, $('#view-play').getBoundingClientRect().top + scrollY - 70), behavior: 'auto' });
  }
  function updatePointsTag(it) {
    const c = it.c, st = it.st;
    const worth = earned(c.points, c.type, Math.max(1, st.attempts + 1), st.hints);
    setText('q-points', st.hints || st.attempts >= S.wrongPenaltyFromAttempt - 1 ? 'worth ' + worth + ' / ' + c.points + ' marks' : c.points + ' marks');
    const left = c.maxAttempts - st.attempts;
    setText('q-attempts', c.maxAttempts === 1 ? '1 attempt' : plural(left, 'attempt') + ' left');
  }
  function updateHintBtn(it) {
    const b = $('#q-hint'), c = it.c, st = it.st;
    const has = c.hintCount > st.hints && !st.done;
    b.hidden = c.hintCount === 0 || st.done;
    b.disabled = !has;
    const loc = localItem(c.id);
    const isFifty = c.type === 'mcq' && !((loc && loc.hints) || []).length;
    b.textContent = !has ? 'No hints left' : (isFifty ? '50/50' : st.hints ? 'Second hint' : 'Hint') + ' (-' + Math.round(100 * S.hintCost[Math.min(st.hints, 1)]) + '% marks)';
  }

  function renderAnswer(it) {
    const box = clear($('#q-answer')), c = it.c;
    if (c.type === 'mcq' || c.type === 'multi') {
      const multi = c.type === 'multi';
      const fs = el('fieldset', { class: 'opts' }, el('legend', { text: multi ? 'Select all that apply' : 'Choose one answer' }));
      c.options.forEach((o, i) => {
        const inp = el('input', { type: multi ? 'checkbox' : 'radio', name: 'ans', value: o, id: 'opt-' + i });
        fs.append(el('label', { class: 'opt', for: 'opt-' + i, 'data-opt': o }, inp, el('span', { class: 'k', 'aria-hidden': 'true', text: String(i + 1) }), el('span', { text: o })));
      });
      box.append(fs);
    } else if (c.type === 'order') {
      box.append(el('p', { class: 'small muted', id: 'order-help', text: 'Drag the steps, use the arrow buttons, or focus a step, press Space to pick it up, then the arrow keys to move it.' }));
      const ol = el('ol', { class: 'order-list', id: 'order-list', 'aria-describedby': 'order-help' });
      c.options.forEach(o => ol.append(orderItem(o)));
      box.append(ol); renumberOrder();
      wireDrag(ol);
    } else {
      const flag = c.type === 'flag';
      box.append(el('div', { class: 'answer-input' }, el('label', { for: 'ans-text', text: flag ? 'Flag (CWM{...} or just the inside)' : 'Your answer' }),
        el('input', { id: 'ans-text', type: 'text', autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off', maxlength: '200',
          placeholder: c.placeholder ? c.placeholder : flag ? 'CWM{...}' : c.kind === 'subnet' ? 'type a number, address or mask' : c.kind === 'command' ? 'type the command' : 'type here' })));
    }
  }
  function orderItem(text) {
    const li = el('li', { tabindex: '0', draggable: 'true', 'data-val': text },
      el('span', { class: 'n', 'aria-hidden': 'true' }), el('span', { class: 't', text }),
      el('span', { class: 'mv' },
        el('button', { type: 'button', 'aria-label': 'Move up: ' + text, text: '↑', onclick: () => moveItem(li, -1, false) }),
        el('button', { type: 'button', 'aria-label': 'Move down: ' + text, text: '↓', onclick: () => moveItem(li, 1, false) })));
    li.addEventListener('keydown', e => {
      if (e.target !== li) return;
      if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); li.classList.toggle('grab'); announce(li.classList.contains('grab') ? 'Picked up ' + text + '. Use arrow keys, Space to drop.' : 'Dropped ' + text + ' at position ' + posOf(li) + '.'); }
      else if ((e.key === 'ArrowUp' || e.key === 'ArrowDown') && (li.classList.contains('grab') || e.altKey)) { e.preventDefault(); moveItem(li, e.key === 'ArrowUp' ? -1 : 1, true); }
      else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') { e.preventDefault(); const sib = e.key === 'ArrowUp' ? li.previousElementSibling : li.nextElementSibling; if (sib) sib.focus(); }
      else if (e.key === 'Escape' && li.classList.contains('grab')) { li.classList.remove('grab'); announce('Dropped.'); }
    });
    return li;
  }
  const posOf = li => Array.prototype.indexOf.call(li.parentNode.children, li) + 1;
  function moveItem(li, dir, keepFocus) {
    if (li.closest('.order-list').classList.contains('locked')) return;
    const sib = dir < 0 ? li.previousElementSibling : li.nextElementSibling;
    if (!sib) return;
    if (dir < 0) li.parentNode.insertBefore(li, sib); else li.parentNode.insertBefore(sib, li);
    renumberOrder();
    if (keepFocus) li.focus();
    announce(li.dataset.val + ' moved to position ' + posOf(li) + '.');
  }
  function renumberOrder() { $$('#order-list li').forEach((li, i) => { li.querySelector('.n').textContent = (i + 1) + '.'; }); }
  function wireDrag(ol) {
    let dragEl = null;
    ol.addEventListener('dragstart', e => { dragEl = e.target.closest('li'); if (!dragEl) return; dragEl.classList.add('drag'); try { e.dataTransfer.setData('text/plain', dragEl.dataset.val); e.dataTransfer.effectAllowed = 'move'; } catch (x) { /* old browsers */ } });
    ol.addEventListener('dragover', e => {
      if (!dragEl) return; e.preventDefault();
      const over = e.target.closest('li'); if (!over || over === dragEl) return;
      const r = over.getBoundingClientRect();
      ol.insertBefore(dragEl, e.clientY > r.top + r.height / 2 ? over.nextSibling : over);
      renumberOrder();
    });
    ol.addEventListener('drop', e => e.preventDefault());
    ol.addEventListener('dragend', () => { if (dragEl) { dragEl.classList.remove('drag'); announce(dragEl.dataset.val + ' placed at position ' + posOf(dragEl) + '.'); } dragEl = null; });
  }
  function readAnswer(c) {
    if (c.type === 'mcq') { const x = $('#q-answer input:checked'); return x ? x.value : ''; }
    if (c.type === 'multi') return $$('#q-answer input:checked').map(x => x.value);
    if (c.type === 'order') return $$('#order-list li').map(li => li.dataset.val);
    const t = $('#ans-text'); return t ? t.value : '';
  }
  const answerText = a => (Array.isArray(a) ? a.join(' | ') : String(a));
  function localItem(id) {
    for (const t of DATA.tracks) for (const l of t.levels) { const c = l.challenges.find(x => x.id === id); if (c) return c; }
    return null;
  }

  /* ---------------- hints ---------------- */
  async function useHint() {
    if (!run) return;
    const it = run.items[run.idx], c = it.c, st = it.st;
    if (st.done || st.hints >= c.hintCount) return;
    const b = $('#q-hint'); b.disabled = true;
    let text = '', gone = [];
    if (run.server) {
      const r = await api('/challenges/' + encodeURIComponent(c.id) + '/hint', { method: 'POST', body: { run_id: run.id } });
      if (!r.ok) { toast(r.error); updateHintBtn(it); return; }
      st.hints = r.n; text = r.hint || ''; gone = r.eliminate || [];
    } else {
      const loc = localItem(c.id);
      if (loc.hints && loc.hints[st.hints]) text = loc.hints[st.hints];
      else if (c.type === 'mcq') {
        setText('q-feedback', 'Working out the 50/50...');
        const sol = await solveLocally(loc);
        setText('q-feedback', '');
        const wrong = c.options.filter(o => !sol || o !== sol.answer[0]);
        gone = shuffle(wrong, mulberry32(seedFrom(run.id + c.id))).slice(0, 2);
        text = 'Two wrong options removed.';
      }
      st.hints += 1;
    }
    if (text) st.hintTexts.push(text);
    gone.forEach(o => {
      st.gone.push(o);
      const lab = $$('#q-answer .opt').find(x => x.dataset.opt === o);
      if (lab) { lab.classList.add('gone'); const inp = lab.querySelector('input'); inp.disabled = true; inp.checked = false; }
    });
    const ht = $('#q-hint-text'); ht.textContent = 'Hint: ' + st.hintTexts.join('  Next hint: '); ht.hidden = false;
    announce('Hint. ' + text);
    updatePointsTag(it); updateHintBtn(it);
  }

  /* ---------------- submit ---------------- */
  let busy = false;
  async function submit() {
    if (!run || busy) return;
    const it = run.items[run.idx], c = it.c, st = it.st;
    if (st.done) return;
    const ans = readAnswer(c);
    const empty = Array.isArray(ans) ? !ans.length : !String(ans).trim();
    const fb = $('#q-feedback');
    if (empty) {
      fb.className = 'q-feedback bad';
      fb.textContent = c.type === 'mcq' ? 'Pick an option first.' : c.type === 'multi' ? 'Tick at least one option.' : 'Type an answer first.';
      shake($('#q-card')); const f = $('#ans-text') || $('#q-answer input:not(:disabled)'); if (f) f.focus();
      return;
    }
    busy = true; $('#q-submit').disabled = true;
    fb.className = 'q-feedback'; fb.textContent = 'Checking...';
    const elapsed = (Date.now() - run.qStart) / 1000;
    let res;
    try { res = run.server ? await serverSubmit(c, ans) : await practiceSubmit(it, ans, elapsed); }
    finally { busy = false; $('#q-submit').disabled = false; }
    if (!res) return;
    st.given = answerText(ans);
    showOutcome(it, res);
  }
  async function serverSubmit(c, ans) {
    const r = await api('/challenges/' + encodeURIComponent(c.id) + '/submit', { method: 'POST', body: { run_id: run.id, answer: ans } });
    if (!r.ok) {
      const fb = $('#q-feedback'); fb.className = 'q-feedback bad'; fb.textContent = r.error; shake($('#q-card'));
      if (r.status === 409 || r.locked) { const it = run.items[run.idx]; it.st.done = true; it.st.correct = false; return { correct: false, final: true, note: r.error }; }
      return null;
    }
    return { correct: r.correct, final: r.correct || r.attemptsLeft <= 0, attempt: r.attempt, left: r.attemptsLeft, points: r.points || 0,
      xp: r.xp || 0, counted: r.counted, note: r.note, combo: r.combo, explanation: r.explanation || null,
      correctAnswer: r.correctOption ? [r.correctOption] : r.correctOptions || null };
  }
  async function practiceSubmit(it, ans, elapsed) {
    const c = it.c, st = it.st, loc = localItem(c.id);
    const joined = Array.isArray(ans) ? ans.join('|') : ans;
    const chk = await check(loc, joined);
    st.attempts += 1;
    const left = c.maxAttempts - st.attempts;
    const out = { correct: chk.ok, attempt: st.attempts, left: chk.ok ? 0 : left, points: 0, xp: 0, explanation: null, correctAnswer: null };
    if (chk.ok) {
      const pts = earned(c.points, c.type, st.attempts, st.hints);
      const already = !!P.solved[c.id];
      const counted = run.mode === 'ranked' && !already && pts > 0;
      out.points = pts;
      out.xp = counted ? pyRound(pts * (1 + bonusFor(elapsed, run.soft, run.relaxed)) * multFor(run.combo)) : 0;
      out.counted = counted;
      if (!counted) out.note = run.mode === 'free' ? 'Free roam' : already ? 'Already solved' : 'No marks left';
      if (counted) { P.solved[c.id] = pts; P.xp = (P.xp || 0) + out.xp; bumpStreak(); saveP(); }
      out.combo = run.combo + 1;
      out.explanation = await decryptExp(loc, chk.i, chk.key);
    } else {
      out.combo = 0;
      if (left <= 0 && ['mcq', 'multi', 'order'].includes(c.type)) {
        const sol = await solveLocally(loc);
        if (sol) { out.correctAnswer = sol.answer; out.explanation = await decryptExp(loc, sol.i, sol.key); }
      }
    }
    out.final = chk.ok || left <= 0;
    return out;
  }

  function showOutcome(it, res) {
    const c = it.c, st = it.st, fb = $('#q-feedback'), card = $('#q-card');
    if (res.attempt) st.attempts = res.attempt;
    run.combo = res.combo || 0;
    run.bestCombo = Math.max(run.bestCombo, run.combo);
    if (res.correct) {
      st.done = true; st.correct = true; st.points = res.points; st.xp = res.xp;
      run.score += res.points; run.xp += res.xp;
      fb.className = 'q-feedback ok';
      fb.textContent = 'Correct! +' + plural(res.points, 'mark');
      fb.append(el('span', { class: 'gain', text: res.xp ? '+' + res.xp + ' XP' : res.note ? res.note + ', no XP' : '+0 XP' }));
      sfx.ok();
      if (!calm()) { card.classList.remove('flash-ok'); void card.offsetWidth; card.classList.add('flash-ok'); }
      if (run.combo >= 2) {
        const cb = $('#ph-combo'); cb.classList.remove('pop'); void cb.offsetWidth; cb.classList.add('pop'); sfx.combo(run.combo);
        if (run.combo === 3 || run.combo === 5) { toast('Combo x' + run.combo + '! XP multiplier ' + multFor(run.combo).toFixed(1)); fxBurst('confetti', 30); }
      }
      announce('Correct. ' + plural(res.points, 'mark') + (res.xp ? ', ' + res.xp + ' XP.' : '.'));
    } else if (!res.final) {
      fb.className = 'q-feedback bad';
      fb.textContent = 'Not quite. ' + plural(res.left, 'attempt') + ' left' + (st.attempts + 1 >= S.wrongPenaltyFromAttempt ? ', and the next one costs 2 marks.' : '.');
      sfx.bad(); shake(card);
      announce(fb.textContent);
      updatePointsTag(it);
      const f = $('#ans-text'); if (f) { f.select(); f.focus(); }
      renderHead();
      return;
    } else {
      st.done = true; st.correct = false;
      fb.className = 'q-feedback bad';
      fb.textContent = res.note && !res.attempt ? res.note : c.maxAttempts === 1 ? 'Not this time.' : 'Out of attempts.';
      sfx.bad(); shake(card);
      announce(fb.textContent);
    }
    st.correctAnswer = res.correctAnswer;
    st.explanation = res.explanation;
    // lock the inputs and mark options
    $$('#q-answer input').forEach(i => { i.disabled = true; });
    $$('#q-answer .opt').forEach(lab => {
      lab.classList.add('locked');
      const o = lab.dataset.opt, chosen = lab.querySelector('input').checked;
      if (res.correctAnswer && res.correctAnswer.includes(o)) lab.classList.add('ok');
      else if (res.correct && chosen) lab.classList.add('ok');
      else if (chosen) lab.classList.add('bad');
    });
    const ol = $('#order-list'); if (ol) { ol.classList.add('locked'); $$('button, li', ol).forEach(x => { if (x.tagName === 'BUTTON') x.disabled = true; else x.draggable = false; }); }
    const ex = clear($('#q-explain'));
    if (!res.correct && res.correctAnswer && c.type === 'order') ex.append(el('p', { class: 'lbl', text: 'Correct order' }), el('p', { text: res.correctAnswer.join(' → ') }));
    ex.append(el('p', { class: 'lbl', text: 'Why' }),
      el('p', { text: res.explanation || 'The explanation unlocks once you solve this one. Retry the level to have another go.' }));
    ex.hidden = false;
    stopTimer();
    show('q-submit', false); show('q-hint', false);
    const nx = $('#q-next'); nx.hidden = false;
    nx.textContent = run.idx + 1 >= run.items.length ? 'See results' : 'Next question';
    renderHead();
    nx.focus({ preventScroll: true });
  }
  function nextQuestion() {
    if (!run) return;
    if (run.idx + 1 >= run.items.length) { finishRun(); return; }
    run.idx += 1; renderPlay();
  }
  function quitRun() {
    if (!run) return;
    if (run.items.some(i => i.st.done) && !window.confirm('Quit this level? This run will not be saved.')) return;
    const t = run.t; run = null; stopTimer();
    location.hash = '#/track/' + t.id;
  }

  async function finishRun() {
    const R = run; stopTimer();
    const max = R.items.reduce((a, i) => a + i.c.points, 0);
    let out = { score: R.score, max, xp: R.xp, correct: R.items.filter(i => i.st.correct).length, questions: R.items.length,
      bestCombo: R.bestCombo, seconds: Math.round((Date.now() - R.started) / 1000) };
    out.pct = max ? pyRound(100 * out.score / max) : 0;
    let newBest = false;
    if (R.server) {
      const r = await api('/runs/' + encodeURIComponent(R.id) + '/finish', { method: 'POST', body: {} });
      if (r.ok) Object.assign(out, { score: r.run.score, max: r.run.max, pct: r.run.pct, xp: r.run.xp, correct: r.run.correct, bestCombo: r.run.bestCombo, seconds: r.run.seconds });
      else toast(r.error);
      await refreshServer();
    } else if (R.mode !== 'free') {
      const key = R.t.id + '/' + R.l.id, cur = P.levels[key] || { best: 0, bestScore: 0, runs: 0 };
      newBest = out.pct > cur.best;
      P.levels[key] = { best: Math.max(cur.best, out.pct), bestScore: Math.max(cur.bestScore, out.score), runs: cur.runs + 1 };
      saveP();
    }
    lastResult = Object.assign(out, { t: R.t, l: R.l, mode: R.mode, server: R.server, newBest,
      rankBefore: R.rankBefore, rankAfter: rankFor(totals().xp).name, unlockedNow: !R.unlockedBefore && nextLevelOpen(R.t, R.l),
      wrong: R.items.filter(i => !i.st.correct).map(i => ({ c: i.c, given: i.st.given, correctAnswer: i.st.correctAnswer, explanation: i.st.explanation, skipped: !i.st.done })) });
    run = null;
    renderHero();
    location.hash = '#/result';
  }

  /* ---------------- level result ---------------- */
  const TITLES = {
    low: ['Every expert started here', 'Rough round, real learning', 'Reboot and go again'],
    mid: ['Solid progress', 'Getting sharper', 'Halfway to hacker'],
    high: ['Flag captured!', 'Root access granted', 'Outstanding run']
  };
  function countUp(node, to, suffix, ms) {
    if (calm()) { node.textContent = to + suffix; return; }
    const t0 = performance.now();
    const step = now => { const k = Math.min(1, (now - t0) / ms), e = 1 - Math.pow(1 - k, 3); node.textContent = Math.round(to * e) + suffix; if (k < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }
  function renderResult() {
    const R = lastResult, b = bandOf(R.pct);
    const pick = TITLES[b][Math.floor(Math.random() * TITLES[b].length)];
    setText('res-where', '// ' + R.t.name + ' / ' + R.l.name + (R.mode === 'free' ? ' · free roam' : R.server ? ' · ranked' : ' · practice'));
    setText('res-title', pick);
    const sub = b === 'low' ? 'Read the explanations, then retry. Scores climb fast on a second run.'
      : b === 'mid' ? (R.pct >= S.unlockPercent ? 'Next level unlocked. Push for 75% to collect the badge.' : 'Close. ' + S.unlockPercent + '% unlocks the next level.')
        : 'You clearly know this. The next level is waiting.';
    setText('res-sub', R.correct + ' of ' + R.questions + ' correct. ' + sub + (R.mode === 'free' ? ' Free roam runs do not count toward rank.' : ''));
    setRing($('#ring-result'), 0, b);
    requestAnimationFrame(() => setRing($('#ring-result'), R.pct, b));
    countUp($('#res-pct'), R.pct, '%', 1100);
    setText('res-score', R.score + ' / ' + R.max + ' marks');
    show('res-badge', b === 'high'); setText('res-badge-text', R.l.name + ' ' + R.t.name + ' cleared');
    const stats = clear($('#res-stats'));
    [['Marks', R.score + ' / ' + R.max], ['XP', '+' + R.xp], ['Correct', R.correct + ' / ' + R.questions], ['Best combo', String(R.bestCombo)],
      ['Time', fmtTime(R.seconds)], ['Rank', R.rankAfter]].forEach(([k, v]) => stats.append(el('div', null, el('dt', { text: k }), el('dd', { text: v }))));
    // next
    const li = R.t.levels.indexOf(R.l), nl = R.t.levels[li + 1], nb = $('#res-next');
    const ti = DATA.tracks.indexOf(R.t), nt = DATA.tracks[(ti + 1) % DATA.tracks.length];
    if (nl) { const open = isUnlocked(R.t.id, nl.id); nb.disabled = !open; nb.textContent = open ? 'Next level: ' + nl.name : nl.name + ' locked (need ' + S.unlockPercent + '%)'; nb.dataset.go = open ? '#/brief/' + R.t.id + '/' + nl.id : ''; }
    else { nb.disabled = false; nb.textContent = 'Next track: ' + nt.name; nb.dataset.go = '#/track/' + nt.id; }
    // review
    const rv = clear($('#review')); rv.hidden = true;
    const rb = $('#res-review'); rb.setAttribute('aria-expanded', 'false');
    rb.hidden = !R.wrong.length; rb.textContent = 'Review wrong answers (' + R.wrong.length + ')';
    R.wrong.forEach(w => rv.append(el('div', { class: 'rv-item' }, el('h4', { text: w.c.title }), el('p', { text: w.c.prompt }),
      el('p', null, el('span', { class: 'lbl', text: 'Your answer ' }), w.skipped ? 'not answered' : w.given || '(none)'),
      w.correctAnswer ? el('p', null, el('span', { class: 'lbl', text: 'Correct ' }), w.correctAnswer.join(w.c.type === 'order' ? ' → ' : ', ')) : null,
      el('p', null, el('span', { class: 'lbl', text: 'Why ' }), w.explanation || 'Locked until you solve it. Typed answers and flags are never revealed, so retry and crack it.'))));
    // share
    const url = location.origin + location.pathname;
    $('#res-share-wa').href = 'https://wa.me/?text=' + encodeURIComponent('I scored ' + R.pct + '% on ' + R.t.name + ' / ' + R.l.name + ' in the CyberWithMadhav CTF Arena. Can you beat it? ' + url);
    renderQuotes(b);
    // effects
    if (b === 'high') { fxBurst('confetti', 160); sfx.win(); }
    else if (b === 'low') { fxBurst('embers', 70); sfx.low(); }
    else sfx.ok();
    if (R.rankAfter !== R.rankBefore) setTimeout(() => levelUp('New rank', R.rankAfter.toUpperCase()), 500);
    else if (R.unlockedNow && nl) setTimeout(() => levelUp(nl.name + ' unlocked', 'LEVEL UP'), 500);
    announce('Level finished. ' + R.pct + ' percent, ' + R.score + ' of ' + R.max + ' marks. ' + pick + '.');
    $('#res-title').focus({ preventScroll: true });
  }
  function sharePng() {
    const R = lastResult; if (!R) return;
    const W = 1200, H = 630, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
    const c = cv.getContext('2d');
    const g = c.createLinearGradient(0, 0, W, H); g.addColorStop(0, '#0D0B14'); g.addColorStop(1, '#241a3d');
    c.fillStyle = g; c.fillRect(0, 0, W, H);
    for (let i = 0; i < 140; i++) { c.fillStyle = 'rgba(255,255,255,' + (Math.random() * 0.6).toFixed(2) + ')'; c.fillRect(Math.random() * W, Math.random() * H, 2, 2); }
    const b = bandOf(R.pct), col = b === 'high' ? '#34D399' : b === 'mid' ? '#B79CFF' : '#FB923C';
    c.lineWidth = 26; c.strokeStyle = 'rgba(255,255,255,.12)'; c.beginPath(); c.arc(930, 315, 170, 0, 6.283); c.stroke();
    c.strokeStyle = col; c.lineCap = 'round'; c.beginPath(); c.arc(930, 315, 170, -Math.PI / 2, -Math.PI / 2 + 6.283 * R.pct / 100); c.stroke();
    c.fillStyle = '#F3F0FA'; c.textAlign = 'center'; c.font = '700 92px "Space Grotesk", system-ui, sans-serif'; c.fillText(R.pct + '%', 930, 345);
    c.font = '500 26px Inter, system-ui, sans-serif'; c.fillStyle = '#B9B3C9'; c.fillText(R.score + ' / ' + R.max + ' marks', 930, 390);
    c.textAlign = 'left'; c.fillStyle = '#B79CFF'; c.font = '500 26px "JetBrains Mono", monospace'; c.fillText('$ ./ctf --result', 80, 120);
    c.fillStyle = '#F3F0FA'; c.font = '700 70px "Space Grotesk", system-ui, sans-serif'; c.fillText('CTF Arena', 80, 210);
    c.font = '600 40px Inter, system-ui, sans-serif'; c.fillText(R.t.name, 80, 300); c.fillStyle = '#B9B3C9'; c.fillText(R.l.name + ' level', 80, 352);
    c.font = '500 30px Inter, system-ui, sans-serif'; c.fillStyle = col; c.fillText('Rank: ' + R.rankAfter + '   Combo: ' + R.bestCombo, 80, 430);
    c.fillStyle = '#8C86A0'; c.font = '500 24px Inter, system-ui, sans-serif'; c.fillText('CyberWithMadhav · learn, practise, capture the flag', 80, 560);
    cv.toBlob(blob => {
      if (!blob) { toast('Could not make the image.'); return; }
      const u = URL.createObjectURL(blob);
      const a = el('a', { href: u, download: 'cwm-ctf-' + R.t.id + '-' + R.l.id + '.png' }); document.body.append(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(u), 4000);
      toast('Score card saved as a PNG');
    }, 'image/png');
  }

  /* ---------------- quotes: random within the band, never the same one twice in a row ---------------- */
  function pickQuote(list, kind, b) {
    const pool = list.map((q, i) => ({ q, i })).filter(x => x.q.band === b);
    if (!pool.length) return null;
    const mem = LS.get(K.quotes, {}) || {}, last = (mem[kind] || {})[b];
    const choices = pool.length > 1 ? pool.filter(x => x.i !== last) : pool;
    const ch = choices[Math.floor(Math.random() * choices.length)];
    mem[kind] = Object.assign({}, mem[kind], { [b]: ch.i }); LS.set(K.quotes, mem);
    return ch.q;
  }
  function setSrc(id, url) {
    const a = document.getElementById(id), ok = typeof url === 'string' && /^https:\/\//.test(url);
    a.hidden = !ok; if (ok) a.href = url; else a.removeAttribute('href');
    const sep = a.previousSibling; if (sep && sep.nodeType === 3) sep.textContent = ok ? ' · ' : '';
  }
  function renderQuotes(b) {
    if (!QUOTES) { show('q-phil', false); show('q-gita', false); return; }
    const ph = b === 'low' ? pickQuote(QUOTES.philosophers || [], 'phil', b) : null;
    show('q-phil', !!ph);
    if (ph) { setText('phil-text', ph.text); setText('phil-hi', ph.meaning_hi || ''); setText('phil-ref', ph.author_or_ref); setSrc('phil-src', ph.source); }
    const gq = pickQuote(QUOTES.gita || [], 'gita', b);
    show('q-gita', !!gq);
    if (gq) { setText('gita-text', gq.text); setText('gita-en', gq.translation_en || ''); setText('gita-hi', gq.meaning_hi || ''); setText('gita-ref', gq.author_or_ref); setSrc('gita-src', gq.source); }
  }

  /* ---------------- overall: radar + weakest track ---------------- */
  function renderOverall() {
    const T = totals(), rows = DATA.tracks.map(t => ({ t, i: trackInfo(t.id) }));
    setText('ovr-sub', T.pct + '% overall, ' + T.xp + ' XP, rank ' + rankFor(T.xp).name + (useServer() ? ' (server profile).' : ' (practice on this device).'));
    const R = $('#radar'), desc = $('#radar-desc');
    clear(R); R.append(desc);
    const cx = 180, cy = 180, rad = 120, n = rows.length;
    const pt = (k, f) => { const a = -Math.PI / 2 + 2 * Math.PI * k / n; return [cx + Math.cos(a) * rad * f, cy + Math.sin(a) * rad * f]; };
    [0.25, 0.5, 0.75, 1].forEach(f => R.append(svg('polygon', { class: 'grid-ring', points: rows.map((_, k) => pt(k, f).map(v => v.toFixed(1)).join(',')).join(' ') })));
    rows.forEach((r, k) => {
      const [x, y] = pt(k, 1); R.append(svg('line', { class: 'axis', x1: cx, y1: cy, x2: x.toFixed(1), y2: y.toFixed(1) }));
    });
    const vals = rows.map(r => Math.max(0.03, r.i.pct / 100));
    R.append(svg('polygon', { class: 'area', points: vals.map((f, k) => pt(k, f).map(v => v.toFixed(1)).join(',')).join(' ') }));
    rows.forEach((r, k) => {
      const [x, y] = pt(k, vals[k]); R.append(svg('circle', { class: 'pt', cx: x.toFixed(1), cy: y.toFixed(1), r: 4 }));
      const [lx, ly] = pt(k, 1.2);
      const anchor = Math.abs(lx - cx) < 8 ? 'middle' : lx > cx ? 'start' : 'end';
      const t1 = svg('text', { x: lx.toFixed(1), y: ly.toFixed(1), 'text-anchor': anchor }); t1.textContent = r.t.name; R.append(t1);
      const t2 = svg('text', { class: 'v', x: lx.toFixed(1), y: (ly + 14).toFixed(1), 'text-anchor': anchor }); t2.textContent = r.i.pct + '%'; R.append(t2);
    });
    desc.textContent = 'Radar chart of your best score in each track: ' + rows.map(r => r.t.name + ' ' + r.i.pct + '%').join(', ') + '.';
    const body = clear($('#ovr-body'));
    rows.forEach(r => body.append(el('tr', null, el('th', { scope: 'row' }, el('a', { href: '#/track/' + r.t.id, text: r.t.icon + ' ' + r.t.name })),
      ...r.t.levels.map(l => { const i = levelInfo(r.t.id, l.id); return el('td', { text: (i.score || i.runs) ? i.pct + '%' : '-' }); }))));
    const weakest = rows.slice().sort((a, b) => a.i.pct - b.i.pct || DATA.tracks.indexOf(a.t) - DATA.tracks.indexOf(b.t))[0];
    const tried = weakest.t.levels.some(l => { const i = levelInfo(weakest.t.id, l.id); return i.score || i.runs; });
    const sg = clear($('#suggest'));
    const lvl = weakest.t.levels.find(l => isUnlocked(weakest.t.id, l.id) && levelInfo(weakest.t.id, l.id).pct < S.unlockPercent) || weakest.t.levels[0];
    sg.append(el('p', null, el('strong', { text: 'Next best move: ' }), tried ? weakest.t.name + ' is your weakest track at ' + weakest.i.pct + '%.' : 'You have not tried ' + weakest.t.name + ' yet.'),
      el('a', { class: 'btn btn-primary small', href: '#/brief/' + weakest.t.id + '/' + lvl.id, text: 'Play ' + weakest.t.name + ': ' + lvl.name }));
    show('reset-progress', !useServer());
  }

  /* ---------------- routing ---------------- */
  const VIEWS = ['hub', 'track', 'brief', 'play', 'result', 'overall'];
  function showView(v) {
    VIEWS.forEach(x => show('view-' + x, x === v));
    document.body.classList.toggle('in-game', v === 'play' || v === 'result');
  }
  let lastView = null;
  function route() {
    if (!DATA) return;
    const parts = (location.hash || '#/hub').replace(/^#\/?/, '').split('/');
    let v = parts[0] || 'hub';
    if (v === 'main' || v === 'top' || v === 'rules') return; // in-page anchors
    if (v !== 'play') stopTimer();
    if (v === 'play' && !run) { location.replace('#/hub'); return; }
    if (v === 'result' && !lastResult) { location.replace('#/hub'); return; }
    if (v !== 'play' && run && lastView === 'play') { run = null; }
    const t = trackById(parts[1]), l = t && levelById(t, parts[2]);
    if ((v === 'track' && !t) || (v === 'brief' && !l)) { location.replace('#/hub'); return; }
    if (!VIEWS.includes(v)) v = 'hub';
    showView(v);
    if (v === 'hub') renderHub();
    else if (v === 'track') renderTrack(t);
    else if (v === 'brief') renderBrief(t, l);
    else if (v === 'play') renderPlay();
    else if (v === 'result') renderResult();
    else renderOverall();
    renderHero();
    const titles = { hub: 'Tracks', track: t && t.name, brief: l && t.name + ' ' + l.name, play: run && run.t.name + ' ' + run.l.name, result: 'Result', overall: 'Skills radar' };
    document.title = (titles[v] ? titles[v] + ' · ' : '') + 'CTF Arena · CyberWithMadhav';
    if (lastView && lastView !== v) {
      if (v !== 'play' && v !== 'result') { const h = $('#view-' + v + ' h2'); if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); } }
      // land with the mode banner and settings toolbar in view, clear of the fixed nav
      const sec = $('#mode-banner') || $('#view-' + v); if (sec) window.scrollTo({ top: Math.max(0, sec.getBoundingClientRect().top + scrollY - 88), behavior: 'auto' });
    }
    lastView = v;
  }
  function rerender() { if (!run) route(); else { renderHero(); renderPlayer(); } }

  /* ---------------- preferences ---------------- */
  const PREF_IDS = { sound: 'opt-sound', relaxed: 'opt-relaxed', free: 'opt-free', motion: 'opt-motion', lite: 'opt-lite' };
  function applyPrefs() {
    Object.keys(PREF_IDS).forEach(k => { const b = document.getElementById(PREF_IDS[k]); if (b) b.setAttribute('aria-pressed', String(!!prefs[k])); });
    root.classList.toggle('ctf-lite', !!prefs.lite);
    root.classList.toggle('ctf-calm', calm());
    show('free-note', !!prefs.free);
    const st = window.cwmSpace && window.cwmSpace.stars;
    if (st) { if (prefs.lite || calm()) st.stop && st.stop(); else st.start && st.start(); }
  }
  function wirePrefs() {
    Object.keys(PREF_IDS).forEach(k => {
      const b = document.getElementById(PREF_IDS[k]); if (!b) return;
      b.addEventListener('click', () => {
        if (run && (k === 'free' || k === 'relaxed')) { toast('Finish or quit this level to change that.'); return; }
        prefs[k] = !prefs[k]; LS.set(K.prefs, prefs); applyPrefs();
        if (k === 'sound' && prefs.sound) sfx.ok();
        const names = { sound: 'Sound', relaxed: 'Relaxed mode', free: 'Free roam', motion: 'Reduce motion', lite: 'Lite visuals' };
        announce(names[k] + (prefs[k] ? ' on.' : ' off.'));
        if (k === 'free' || k === 'relaxed') rerender();
      });
    });
    if (mqReduce.addEventListener) mqReduce.addEventListener('change', applyPrefs);
  }

  /* ---------------- wiring ---------------- */
  function wire() {
    wirePrefs(); wirePlayer();
    $('#brief-start').addEventListener('click', e => startRun(e.currentTarget.dataset.track, e.currentTarget.dataset.level));
    $('#q-form').addEventListener('submit', e => { e.preventDefault(); submit(); });
    $('#q-hint').addEventListener('click', useHint);
    $('#q-next').addEventListener('click', nextQuestion);
    $('#quit').addEventListener('click', quitRun);
    $('#copy-code').addEventListener('click', () => copyText($('#q-code').textContent, 'Code copied'));
    $('#res-retry').addEventListener('click', () => { if (lastResult) startRun(lastResult.t.id, lastResult.l.id); });
    $('#res-next').addEventListener('click', e => { const g = e.currentTarget.dataset.go; if (g) location.hash = g; });
    $('#res-review').addEventListener('click', e => {
      const rv = $('#review'), open = rv.hidden; rv.hidden = !open; e.currentTarget.setAttribute('aria-expanded', String(open));
      if (open) rv.scrollIntoView({ block: 'nearest', behavior: calm() ? 'auto' : 'smooth' });
    });
    $('#res-share-png').addEventListener('click', sharePng);
    $('#reset-progress').addEventListener('click', () => {
      if (!window.confirm('Reset all practice progress on this device? Server scores are not affected.')) return;
      P = freshProgress(); saveP(); toast('Practice progress reset'); rerender();
    });
    $$('#board-tabs button').forEach(b => b.addEventListener('click', () => { boardScope = b.dataset.scope; renderBoard(); }));
    $('#board-tabs').addEventListener('keydown', e => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      const bs = $$('#board-tabs button'), i = bs.findIndex(b => b.dataset.scope === boardScope);
      const n = bs[(i + (e.key === 'ArrowRight' ? 1 : bs.length - 1)) % bs.length];
      boardScope = n.dataset.scope; n.focus(); renderBoard();
    });
    // nav toggle (space.js only closes the menu)
    const nt = $('.nav-toggle'), nl = $('#nav-links');
    if (nt && nl) nt.addEventListener('click', () => {
      const open = nl.classList.toggle('open');
      nt.setAttribute('aria-expanded', String(open)); nt.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
    // keyboard: 1-9 pick an option, Enter submit / next, Esc closes review or quits
    document.addEventListener('keydown', e => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      const tag = (e.target.tagName || '').toLowerCase();
      if ($('#view-play').hidden || !run) {
        if (e.key === 'Escape' && !$('#review').hidden && !$('#view-result').hidden) { $('#review').hidden = true; $('#res-review').setAttribute('aria-expanded', 'false'); $('#res-review').focus(); }
        return;
      }
      const it = run.items[run.idx];
      if (/^[1-9]$/.test(e.key) && tag !== 'input' && tag !== 'textarea' || (/^[1-9]$/.test(e.key) && e.target.type && e.target.type !== 'text' && tag === 'input')) {
        const inps = $$('#q-answer .opt input');
        const x = inps[Number(e.key) - 1];
        if (x && !x.disabled && !it.st.done) { e.preventDefault(); if (x.type === 'checkbox') x.checked = !x.checked; else x.checked = true; x.focus(); }
      } else if (e.key === 'Enter' && it.st.done && tag !== 'button' && tag !== 'a') { e.preventDefault(); nextQuestion(); }
      else if (e.key === 'Escape' && !$$('#order-list li.grab').length) { e.preventDefault(); quitRun(); }
    });
    window.addEventListener('hashchange', route);
    const y = $('#year'); if (y) y.textContent = String(new Date().getFullYear());
  }

  /* ---------------- boot ---------------- */
  async function boot() {
    applyPrefs();
    try {
      const [d, q] = await Promise.all([
        fetch('data/ctf.json', { cache: 'no-cache' }).then(r => { if (!r.ok) throw new Error('ctf.json ' + r.status); return r.json(); }),
        fetch('data/ctf_quotes.json', { cache: 'no-cache' }).then(r => (r.ok ? r.json() : null)).catch(() => null)
      ]);
      DATA = d; QUOTES = q; S = DATA.scoring;
    } catch (e) {
      const g = $('#track-grid'); if (g) { clear(g); g.append(el('p', { class: 'q-feedback bad', text: 'Could not load the challenges. Please refresh the page.' })); }
      setText('mode-text', 'Could not load the challenges.');
      return;
    }
    if (!window.crypto || !crypto.subtle) setText('mode-text', 'Your browser cannot check answers here (Web Crypto needs HTTPS). Please use a recent browser over HTTPS.');
    wire();
    if (!location.hash || location.hash === '#') history.replaceState(null, '', '#/hub');
    route();
    healthCheck().then(rerender);
  }
  boot();
})();
