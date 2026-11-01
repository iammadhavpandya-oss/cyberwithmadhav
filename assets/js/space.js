/* CyberWithMadhav v3: theme switch, starfield, warp jumps, parallax, glass nav, back-to-top.
   Vanilla JS, no dependencies. Heavy motion is off for prefers-reduced-motion. */
(function () {
  'use strict';
  const root = document.documentElement;
  const $ = (s, el = document) => el.querySelector(s);
  const mqReduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const mqLight = window.matchMedia('(prefers-color-scheme: light)');
  const mqSmall = window.matchMedia('(max-width: 700px), (pointer: coarse)');
  let reduced = mqReduce.matches;
  const theme = () => (root.getAttribute('data-theme') === 'light' ? 'light' : 'dark');

  /* ---------------- theme (day / night) ---------------- */
  const btn = $('.theme-toggle');
  const meta = $('meta[name="theme-color"]');
  function syncThemeUI() {
    const t = theme();
    if (btn) {
      btn.setAttribute('aria-label', t === 'light' ? 'Switch to dark theme' : 'Switch to light theme');
      btn.setAttribute('title', t === 'light' ? 'Night mode' : 'Day mode');
    }
    if (meta) meta.content = t === 'light' ? '#F6F4FB' : '#0D0B14';
  }
  function setTheme(t, origin) {
    const apply = () => { root.setAttribute('data-theme', t); syncThemeUI(); stars.retint(); };
    if (!reduced && origin && document.startViewTransition) {
      const r = origin.getBoundingClientRect();
      const x = r.left + r.width / 2, y = r.top + r.height / 2;
      const end = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
      const vt = document.startViewTransition(apply);
      vt.ready.then(() => {
        root.animate({ clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${end}px at ${x}px ${y}px)`] },
          { duration: 600, easing: 'cubic-bezier(.4,0,.2,1)', pseudoElement: '::view-transition-new(root)' });
      }).catch(() => {});
    } else {
      root.classList.add('theme-anim'); apply();
      setTimeout(() => root.classList.remove('theme-anim'), 450);
    }
  }
  if (btn) btn.addEventListener('click', () => {
    const next = theme() === 'light' ? 'dark' : 'light';
    try { localStorage.setItem('cwm-theme', next); } catch (e) {}
    setTheme(next, btn);
  });
  // Follow the system until the visitor picks a theme themselves.
  const onSystem = (e) => {
    let saved = null; try { saved = localStorage.getItem('cwm-theme'); } catch (_) {}
    if (!saved) setTheme(e.matches ? 'light' : 'dark');
  };
  mqLight.addEventListener ? mqLight.addEventListener('change', onSystem) : mqLight.addListener(onSystem);

  /* ---------------- starfield canvas ---------------- */
  const stars = (function () {
    const cv = $('#starfield');
    const api = { retint() {}, boost() {}, start() {}, stop() {} };
    if (!cv || !cv.getContext) return api;
    const ctx = cv.getContext('2d', { alpha: true });
    let W = 0, H = 0, dpr = 1, list = [], raf = 0, last = 0, t0 = performance.now();
    let warpV = 0, warpShift = 0, px = 0, py = 0, tx = 0, ty = 0, lastScroll = 0, shoot = null, nextShoot = 4000;
    const PAL = {
      dark: [['233,230,242', .82], ['183,156,255', .13], ['74,222,128', .05]],
      light: [['109,40,217', .6], ['124,58,237', .25], ['21,128,61', .15]]
    };
    function pick(p) { let r = Math.random(); for (const [c, w] of p) { if ((r -= w) <= 0) return c; } return p[0][0]; }
    function build() {
      const small = mqSmall.matches;
      const n = Math.round(Math.min(small ? 90 : 240, (W * H) / (small ? 9000 : 5600)));
      const p = PAL[theme()];
      list = Array.from({ length: n }, () => {
        const z = 0.15 + Math.pow(Math.random(), 2.2) * 0.85;
        return { x: Math.random() * W, y: Math.random() * H, z, r: 0.35 + z * 1.25, tw: Math.random() * 6.283, sp: 0.4 + Math.random() * 1.4, c: pick(p) };
      });
    }
    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, mqSmall.matches ? 1.5 : 2);
      W = innerWidth; H = innerHeight;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      cv.style.width = W + 'px'; cv.style.height = H + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      build(); draw(performance.now(), 16);
    }
    function draw(now, dt) {
      const light = theme() === 'light';
      ctx.clearRect(0, 0, W, H);
      const sy = window.scrollY || 0;
      px += (tx - px) * 0.05; py += (ty - py) * 0.05;
      warpShift += warpV * dt * 1.6; warpV *= Math.pow(0.93, dt / 16);
      if (Math.abs(warpV) < 0.01) warpV = 0;
      const t = (now - t0) * 0.001, base = light ? 0.38 : 0.9;
      for (const s of list) {
        if (!reduced) s.x += 0.006 * s.z * dt;
        let x = (s.x + px * s.z * 18) % W; if (x < 0) x += W;
        let y = (s.y - (sy * 0.12 + warpShift) * s.z + py * s.z * 12) % H; if (y < 0) y += H;
        const tw = reduced ? 1 : 0.62 + 0.38 * Math.sin(t * s.sp + s.tw);
        const a = base * tw * (0.35 + s.z * 0.65);
        const streak = Math.abs(warpV) * s.z * 70;
        if (streak > 1.5) {
          ctx.strokeStyle = `rgba(${s.c},${a})`; ctx.lineWidth = s.r; ctx.lineCap = 'round';
          ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y + Math.sign(warpV) * streak); ctx.stroke();
        } else {
          ctx.fillStyle = `rgba(${s.c},${a})`;
          ctx.beginPath(); ctx.arc(x, y, s.r, 0, 6.283); ctx.fill();
          if (s.z > 0.82 && !light) { ctx.fillStyle = `rgba(${s.c},${a * 0.12})`; ctx.beginPath(); ctx.arc(x, y, s.r * 3.4, 0, 6.283); ctx.fill(); }
        }
      }
      // An occasional shooting star, night mode on larger screens only.
      if (!reduced && !light && !mqSmall.matches) {
        nextShoot -= dt;
        if (!shoot && nextShoot <= 0) { shoot = { x: Math.random() * W * 0.7 + W * 0.2, y: Math.random() * H * 0.35, life: 0 }; nextShoot = 7000 + Math.random() * 7000; }
        if (shoot) {
          shoot.life += dt; const k = shoot.life / 900;
          const hx = shoot.x - k * 340, hy = shoot.y + k * 150;
          const g = ctx.createLinearGradient(hx, hy, hx + 90, hy - 40);
          g.addColorStop(0, `rgba(233,230,242,${0.75 * (1 - k)})`); g.addColorStop(1, 'rgba(183,156,255,0)');
          ctx.strokeStyle = g; ctx.lineWidth = 1.4; ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(hx + 90, hy - 40); ctx.stroke();
          if (k >= 1) shoot = null;
        }
      }
    }
    function loop(now) {
      raf = requestAnimationFrame(loop);
      const dt = Math.min(now - last, 64);
      const busy = warpV !== 0 || now - lastScroll < 400 || Math.abs(tx - px) > 0.002;
      if (!busy && dt < 32) return; // ~30 fps when idle, full rate while moving
      last = now; draw(now, dt);
    }
    api.start = () => { if (!reduced && !raf && !document.hidden) { last = performance.now(); raf = requestAnimationFrame(loop); } };
    api.stop = () => { cancelAnimationFrame(raf); raf = 0; };
    api.retint = () => { const p = PAL[theme()]; list.forEach(s => (s.c = pick(p))); if (!raf) draw(performance.now(), 16); };
    api.boost = (dir) => { if (!reduced) { warpV = dir * 1.1; lastScroll = performance.now(); api.start(); } };
    api.scrolled = () => { lastScroll = performance.now(); if (reduced) draw(performance.now(), 16); };
    let rz; addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(resize, 150); }, { passive: true });
    if (!mqSmall.matches) addEventListener('pointermove', e => { tx = e.clientX / W - 0.5; ty = e.clientY / H - 0.5; }, { passive: true });
    document.addEventListener('visibilitychange', () => (document.hidden ? api.stop() : api.start()));
    resize(); api.start();
    return api;
  })();

  mqReduce.addEventListener && mqReduce.addEventListener('change', e => { reduced = e.matches; reduced ? stars.stop() : stars.start(); });

  /* ---------------- warp jump to sections ---------------- */
  function warp(target) {
    if (!target) return;
    const dir = target.getBoundingClientRect().top >= 0 ? 1 : -1;
    stars.boost(dir);
    if (reduced) return;
    const sec = target.closest('section, footer') || target;
    sec.classList.remove('arrive'); void sec.offsetWidth; sec.classList.add('arrive');
    setTimeout(() => sec.classList.remove('arrive'), 1100);
  }
  document.addEventListener('click', e => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a || a.classList.contains('skip')) return;
    const id = a.getAttribute('href').slice(1);
    const el = id ? document.getElementById(id) : null;
    if (!el) return;
    e.preventDefault();
    warp(el);
    const top = id === 'top' ? 0 : el.getBoundingClientRect().top + scrollY - 70;
    scrollTo({ top: Math.max(0, top), behavior: reduced ? 'auto' : 'smooth' });
    if (history.pushState) history.pushState(null, '', id === 'top' ? location.pathname + location.search : '#' + id);
    // Move keyboard focus to the section for screen reader and keyboard users.
    const focusEl = el.matches('section, header, footer') ? el : el.closest('section') || el;
    if (!focusEl.hasAttribute('tabindex')) focusEl.setAttribute('tabindex', '-1');
    focusEl.focus({ preventScroll: true });
  });

  /* ---------------- scroll effects: glass nav, parallax, back-to-top ---------------- */
  const nav = $('.nav'), toTop = $('#to-top'), ring = toTop && toTop.querySelector('.p');
  const nebula = $('.nebula'), hero = $('.hero');
  let ticking = false;
  function onScroll() {
    ticking = false;
    const y = scrollY, max = root.scrollHeight - root.clientHeight;
    if (nav) nav.classList.toggle('scrolled', y > 8);
    if (toTop) {
      const show = y > 700;
      if (show && toTop.hidden) { toTop.hidden = false; requestAnimationFrame(() => toTop.classList.add('show')); }
      else if (!show && !toTop.hidden && toTop.classList.contains('show')) { toTop.classList.remove('show'); setTimeout(() => { if (!toTop.classList.contains('show')) toTop.hidden = true; }, 250); }
      if (ring) ring.style.strokeDashoffset = String(100 - (max > 0 ? (y / max) * 100 : 0));
    }
    if (!reduced) {
      if (nebula) nebula.style.transform = `translate3d(0,${(-y * 0.04).toFixed(1)}px,0)`;
      if (hero && y < innerHeight * 1.2) hero.style.setProperty('--py', (y * 0.25).toFixed(1) + 'px');
    }
    stars.scrolled && stars.scrolled();
  }
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  if (toTop) toTop.addEventListener('click', () => {
    stars.boost(-1);
    scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
    const brand = $('.brand'); if (brand) brand.focus({ preventScroll: true });
  });

  /* ---------------- mobile menu: Esc + outside tap close it ---------------- */
  const navBtn = $('.nav-toggle'), links = $('#nav-links');
  function closeMenu(focusBtn) {
    if (!links || !links.classList.contains('open')) return;
    links.classList.remove('open'); navBtn.setAttribute('aria-expanded', 'false'); navBtn.setAttribute('aria-label', 'Open menu');
    if (focusBtn) navBtn.focus();
  }
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(true); });
  document.addEventListener('click', e => { if (links && links.classList.contains('open') && !e.target.closest('.nav')) closeMenu(false); });

  syncThemeUI(); onScroll();
  window.cwmSpace = { warp, setTheme, stars };
})();
