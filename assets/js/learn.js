/* CyberWithMadhav Learn: lesson progress, flashcards, quizzes, steppers, explorers, bit and permission widgets, hub.
 * Progress is kept only in this browser (localStorage key 'cwm-learn'). No cookies, nothing is sent anywhere.
 * Built for a strict CSP: no inline handlers, no eval. Terminal simulator lives in learn-term.js. */
(function () {
  'use strict';
  var KEY = 'cwm-learn';
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var T = function (k, en) { return window.CWMI18N ? window.CWMI18N.t(k, en) : en; };

  function load() { try { var v = JSON.parse(localStorage.getItem(KEY)); return v && typeof v === 'object' && v.l ? v : { v: 1, l: {} }; } catch (e) { return { v: 1, l: {} }; } }
  function save(d) { try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (e) { /* private mode: progress just is not kept */ } }
  function rec(d, slug) { var r = d.l[slug]; if (!r) r = d.l[slug] = { s: [], q: 0, lab: [], done: false, t: 0 }; return r; }
  /* units: one per section, one for the quiz (pass at 70%), one for the lab (all steps ticked) */
  function pct(r, units) {
    if (!r) return 0;
    if (r.done) return 100;
    var u = units || {}, got = 0, tot = (u.s || 0) + (u.q ? 1 : 0) + (u.lab ? 1 : 0);
    if (!tot) return 0;
    got += Math.min(r.s.length, u.s || 0);
    if (u.q && r.q >= 0.7) got += 1;
    if (u.lab) got += Math.min(1, (r.lab.length || 0) / u.lab);
    return Math.round(got / tot * 100);
  }
  window.CWMLearn = { load: load, save: save, pct: pct };

  /* ---------------- lesson page ---------------- */
  function lesson() {
    var art = $('.lx-article'); if (!art) return;
    var slug = document.body.getAttribute('data-lesson');
    var units = { s: +art.getAttribute('data-sections') || 0, q: !!$('.lx-quiz'), lab: $$('.lx-labsteps > li').length };
    var ring = $('.lx-ring');

    function paint() {
      var d = load(), r = d.l[slug], p = pct(r, units);
      if (ring) { ring.style.setProperty('--p', p); $('span b', ring).textContent = p + '%'; }
      $$('.lx-got').forEach(function (b) {
        var on = !!(r && r.s.indexOf(b.getAttribute('data-sec')) > -1);
        b.setAttribute('aria-pressed', String(on));
        $('span', b).textContent = on ? T('lx.got.on', 'Understood') : T('lx.got', 'I understood this section');
        var a = $('.lx-toc a[href="#' + b.getAttribute('data-sec') + '"]'); if (a) a.classList.toggle('done', on);
      });
      $$('.lx-labsteps > li').forEach(function (li, i) {
        var on = !!(r && r.lab.indexOf(i) > -1), cb = $('input', li);
        li.classList.toggle('done', on); if (cb) cb.checked = on;
      });
      var done = $('#lx-done'); if (done) { done.setAttribute('aria-pressed', String(p === 100)); done.textContent = p === 100 ? T('lx.done.on', 'Lesson complete. Nice work.') : T('lx.done', 'Mark the whole lesson complete'); }
    }
    function touch(fn) { var d = load(), r = rec(d, slug); fn(r); r.t = Date.now(); save(d); paint(); }

    $$('.lx-got').forEach(function (b) {
      b.addEventListener('click', function () {
        var id = b.getAttribute('data-sec');
        touch(function (r) { var i = r.s.indexOf(id); if (i > -1) { r.s.splice(i, 1); r.done = false; } else r.s.push(id); });
      });
    });
    $$('.lx-labsteps > li input').forEach(function (cb, i) {
      cb.addEventListener('change', function () {
        touch(function (r) { var k = r.lab.indexOf(i); if (cb.checked && k < 0) r.lab.push(i); if (!cb.checked && k > -1) { r.lab.splice(k, 1); r.done = false; } });
      });
    });
    var done = $('#lx-done');
    if (done) done.addEventListener('click', function () { touch(function (r) { r.done = !r.done; }); });

    /* contents highlight */
    var links = $$('.lx-toc a');
    if ('IntersectionObserver' in window && links.length) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting) return;
          links.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); });
        });
      }, { rootMargin: '-30% 0px -60% 0px' });
      links.forEach(function (a) { var s = document.getElementById(a.getAttribute('href').slice(1)); if (s) io.observe(s); });
    }
    quiz(function (score) { touch(function (r) { if (score > r.q) r.q = score; }); });
    paint();
    document.addEventListener('cwm:lang', paint);
  }

  /* ---------------- quiz ---------------- */
  function quiz(onScore) {
    var box = $('.lx-quiz'); if (!box) return;
    var qs = $$('.lx-q', box), out = $('#lx-score');
    function update(quiet) {
      var answered = $$('.lx-q.answered', box).length, right = $$('.lx-q.correct', box).length;
      if (!out) return;
      $('b', out).textContent = right + ' / ' + qs.length;
      var msg = $('.msg', out);
      if (answered < qs.length) msg.textContent = T('lx.q.left', 'Answer every question to see how you did.') + ' (' + answered + '/' + qs.length + ')';
      else {
        var s = right / qs.length;
        msg.textContent = s >= 0.9 ? T('lx.q.top', 'Excellent. You really know this.') : s >= 0.7 ? T('lx.q.pass', 'Passed. Re-read the ones you missed, then move on.') : T('lx.q.fail', 'Not yet. Go back to the sections behind the wrong answers and try again.');
        if (onScore && quiet !== true) onScore(s);
      }
    }
    qs.forEach(function (q) {
      var ans = +q.getAttribute('data-a'), why = $('.lx-why', q);
      $$('.lx-opts button', q).forEach(function (b, i) {
        b.addEventListener('click', function () {
          if (q.classList.contains('answered')) return;
          q.classList.add('answered'); if (i === ans) q.classList.add('correct');
          $$('.lx-opts button', q).forEach(function (x, j) {
            x.disabled = true; x.setAttribute('aria-disabled', 'true');
            if (j === ans) x.classList.add('right'); else if (j === i) x.classList.add('wrong');
          });
          if (why) { why.hidden = false; why.classList.toggle('no', i !== ans); $('b', why).textContent = i === ans ? T('lx.q.right', 'Correct. ') : T('lx.q.wrong', 'Not quite. '); }
          update();
        });
      });
    });
    var re = $('#lx-retry');
    if (re) re.addEventListener('click', function () {
      qs.forEach(function (q) {
        q.classList.remove('answered', 'correct');
        $$('.lx-opts button', q).forEach(function (x) { x.disabled = false; x.removeAttribute('aria-disabled'); x.classList.remove('right', 'wrong'); });
        var w = $('.lx-why', q); if (w) w.hidden = true;
      });
      update(); var f = $('.lx-opts button', box); if (f) f.focus();
    });
    update();
    document.addEventListener('cwm:lang', function () {
      update(true);
      qs.forEach(function (q) {
        var w = $('.lx-why', q), b = w && $('b', w);
        if (b && !w.hidden) b.textContent = q.classList.contains('correct') ? T('lx.q.right', 'Correct. ') : T('lx.q.wrong', 'Not quite. ');
      });
    });
  }

  /* ---------------- flashcards ---------------- */
  function cards() {
    $$('.lx-card').forEach(function (c) {
      c.addEventListener('click', function () { c.setAttribute('aria-pressed', String(c.getAttribute('aria-pressed') !== 'true')); });
    });
    var all = $('#lx-flipall');
    if (all) all.addEventListener('click', function () {
      var cs = $$('.lx-card'), anyFront = cs.some(function (c) { return c.getAttribute('aria-pressed') !== 'true'; });
      cs.forEach(function (c) { c.setAttribute('aria-pressed', String(anyFront)); });
    });
  }

  /* ---------------- code copy ---------------- */
  function copy() {
    $$('.lx-code').forEach(function (box) {
      var pre = $('pre', box); if (!pre || box.hasAttribute('data-nocopy')) return;
      var b = document.createElement('button'); b.type = 'button'; b.textContent = T('lx.copy', 'Copy');
      b.setAttribute('aria-label', 'Copy commands');
      b.addEventListener('click', function () {
        var text = $$('.cmd', pre).map(function (x) { return x.textContent; }).join('\n') || pre.textContent;
        var ok = function () { b.textContent = T('lx.copied', 'Copied'); b.classList.add('ok'); setTimeout(function () { b.textContent = T('lx.copy', 'Copy'); b.classList.remove('ok'); }, 1500); };
        if (navigator.clipboard) navigator.clipboard.writeText(text).then(ok, function () {}); 
      });
      box.appendChild(b);
    });
  }

  /* ---------------- stepper ---------------- */
  function steppers() {
    $$('.lx-stepper').forEach(function (w) {
      var steps = $$('.lx-step', w), track = $('.lx-steps-track', w), i = 0;
      var prev = $('[data-prev]', w), next = $('[data-next]', w), pos = $('.lx-steps-nav span', w);
      track.innerHTML = steps.map(function (s, k) { return '<li><button type="button" aria-label="Step ' + (k + 1) + ': ' + s.getAttribute('data-t').replace(/"/g, '&quot;') + '">' + (k + 1) + '</button></li>'; }).join('');
      var dots = $$('button', track);
      function go(k) {
        i = Math.max(0, Math.min(steps.length - 1, k));
        steps.forEach(function (s, j) { s.hidden = j !== i; });
        dots.forEach(function (d, j) { d.classList.toggle('on', j === i); d.classList.toggle('past', j < i); d.setAttribute('aria-current', j === i ? 'step' : 'false'); });
        prev.disabled = i === 0; next.disabled = i === steps.length - 1;
        pos.textContent = (i + 1) + ' / ' + steps.length;
      }
      dots.forEach(function (d, j) { d.addEventListener('click', function () { go(j); }); });
      prev.addEventListener('click', function () { go(i - 1); });
      next.addEventListener('click', function () { go(i + 1); });
      w.addEventListener('keydown', function (e) { if (e.target.tagName === 'INPUT') return; if (e.key === 'ArrowRight') go(i + 1); if (e.key === 'ArrowLeft') go(i - 1); });
      go(0);
    });
  }

  /* ---------------- explorer (pick an item, read the panel) ---------------- */
  function explorers() {
    $$('.lx-explorer').forEach(function (w) {
      var btns = $$('[role="tab"]', w), panels = $$('[role="tabpanel"]', w);
      function sel(k) {
        btns.forEach(function (b, j) { var on = j === k; b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; });
        panels.forEach(function (p, j) { p.hidden = j !== k; });
      }
      btns.forEach(function (b, j) {
        b.addEventListener('click', function () { sel(j); });
        b.addEventListener('keydown', function (e) {
          var n = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0;
          if (!n) return; e.preventDefault(); var k = (j + n + btns.length) % btns.length; btns[k].focus(); sel(k);
        });
      });
      sel(0);
    });
  }

  /* ---------------- bits: binary, decimal, hex, ASCII ---------------- */
  function bits() {
    $$('.lx-bitw').forEach(function (w) {
      var bs = $$('.lx-bits button', w), out = {};
      ['dec', 'hex', 'bin', 'chr'].forEach(function (k) { out[k] = $('[data-o="' + k + '"]', w); });
      var inp = $('input', w);
      function val() { return bs.reduce(function (n, b) { return n * 2 + (b.getAttribute('aria-pressed') === 'true' ? 1 : 0); }, 0); }
      function set(n) { bs.forEach(function (b, i) { b.setAttribute('aria-pressed', String(!!(n & (128 >> i)))); }); show(); }
      function show() {
        var n = val();
        bs.forEach(function (b) { var sp = b.querySelector('span'); if (sp) sp.textContent = b.getAttribute('aria-pressed') === 'true' ? '1' : '0'; });
        out.dec.textContent = n;
        out.hex.textContent = '0x' + n.toString(16).toUpperCase().padStart(2, '0');
        out.bin.textContent = n.toString(2).padStart(8, '0').replace(/(\d{4})(\d{4})/, '$1 $2');
        out.chr.textContent = n >= 33 && n <= 126 ? '"' + String.fromCharCode(n) + '"' : n === 32 ? T('lx.bits.space', 'space') : T('lx.bits.np', 'not printable');
        if (inp && document.activeElement !== inp) inp.value = n;
      }
      bs.forEach(function (b) { b.addEventListener('click', function () { b.setAttribute('aria-pressed', String(b.getAttribute('aria-pressed') !== 'true')); show(); }); });
      if (inp) inp.addEventListener('input', function () { var n = parseInt(inp.value, 10); if (n >= 0 && n <= 255) set(n); });
      $$('[data-set]', w).forEach(function (b) { b.addEventListener('click', function () { set(+b.getAttribute('data-set')); }); });
      show();
    });
  }

  /* ---------------- chmod calculator ---------------- */
  function perms() {
    $$('.lx-permw').forEach(function (w) {
      var cbs = $$('input[type="checkbox"]', w), oct = $('input[type="text"]', w), sym = $('[data-o="sym"]', w), cmd = $('[data-o="cmd"]', w), say = $('.lx-permsay', w);
      var who = ['owner', 'group', 'others'];
      function read() { var d = [0, 0, 0]; cbs.forEach(function (c) { if (c.checked) d[+c.getAttribute('data-w')] += +c.getAttribute('data-v'); }); return d; }
      function show(fromText) {
        var d = read(), s = '-' + d.map(function (n) { return (n & 4 ? 'r' : '-') + (n & 2 ? 'w' : '-') + (n & 1 ? 'x' : '-'); }).join('');
        if (!fromText) oct.value = d.join('');
        sym.textContent = s; cmd.textContent = 'chmod ' + d.join('') + ' report.sh';
        say.textContent = d.map(function (n, i) {
          var p = [n & 4 ? 'read' : '', n & 2 ? 'write' : '', n & 1 ? 'run' : ''].filter(Boolean);
          return 'The ' + who[i] + ' can ' + (p.length ? p.join(', ') : 'do nothing');
        }).join('. ') + '.' + (d[2] & 2 ? ' Warning: anyone on the system can change this file.' : '');
      }
      cbs.forEach(function (c) { c.addEventListener('change', function () { show(false); }); });
      oct.addEventListener('input', function () {
        var v = oct.value.trim(); if (!/^[0-7]{3}$/.test(v)) return;
        cbs.forEach(function (c) { c.checked = !!(+v[+c.getAttribute('data-w')] & +c.getAttribute('data-v')); }); show(true);
      });
      $$('[data-set]', w).forEach(function (b) { b.addEventListener('click', function () { oct.value = b.getAttribute('data-set'); oct.dispatchEvent(new Event('input')); }); });
      show(false);
    });
  }

  /* ---------------- hub ---------------- */
  function hub() {
    var root = $('.lh-path'); if (!root) return;
    function paint() {
      var d = load(), all = 0, sum = 0, last = null;
      $$('.lh-stage', root).forEach(function (st) {
        var n = 0, s = 0;
        $$('a.lh-l[data-slug]', st).forEach(function (a) {
          var slug = a.getAttribute('data-slug'), r = d.l[slug];
          var u = { s: +a.getAttribute('data-s'), q: a.getAttribute('data-q') === '1', lab: +a.getAttribute('data-lab') };
          var p = pct(r, u), badge = $('.lh-st', a);
          badge.className = 'lh-st' + (p === 100 ? ' done' : p > 0 ? ' prog' : '');
          badge.textContent = p === 100 ? T('lh.done', 'Done') : p > 0 ? p + '%' : T('lh.new', 'Start');
          n++; s += p; if (r && r.t && (!last || r.t > last.t) && p < 100) last = { t: r.t, href: a.getAttribute('href'), title: $('h3', a).textContent };
        });
        var bar = $('.lh-sbar', st);
        if (bar && n) { $('.lh-bar span', bar).style.width = Math.round(s / n) + '%'; $('em', bar).textContent = Math.round(s / n) + '%'; }
        all += n; sum += s;
      });
      var o = $('#lh-all'); if (o && all) { $('.lh-bar span', o).style.width = Math.round(sum / all) + '%'; $('b', o).textContent = Math.round(sum / all) + '%'; }
      var c = $('#lh-continue');
      if (c) { if (last) { c.href = last.href; $('span', c).textContent = T('lh.cont', 'Continue: ') + last.title; } else { $('span', c).textContent = T('lh.begin', 'Start with lesson 1'); } }
    }
    paint();
    document.addEventListener('cwm:lang', paint);
    var reset = $('#lh-reset');
    if (reset) reset.addEventListener('click', function () {
      if (window.confirm(T('lh.reset.q', 'Clear your lesson progress in this browser?'))) { try { localStorage.removeItem(KEY); } catch (e) {} paint(); }
    });
  }

  function init() { lesson(); cards(); copy(); steppers(); explorers(); bits(); perms(); hub(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
