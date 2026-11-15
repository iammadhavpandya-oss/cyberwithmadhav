/* CyberWithMadhav easter eggs. Small, deferred, no network calls, nothing stored.
 * Triggers (see README "Easter eggs"):
 *   Konami code (up up down down left right left right b a), or type "sudo" anywhere: opens the root shell panel.
 *   Tap the footer handshake line 3 times (touch friendly): opens the root shell panel.
 *   Type "coffee" anywhere, or click the logo 5 times on the home page: HTTP 418 I'm a teapot.
 *   Hover a section heading (mouse only): its first letters in hex.
 *   Open DevTools console: ASCII banner and a note for curious devs.
 * Rules: keyboard only triggers ignore inputs, Esc closes the panel and returns focus, no modal overlay,
 * prefers-reduced-motion skips every animation. CSP safe: no inline styles, CSS is a 'self' stylesheet loaded when idle. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function hi() { return (window.CWMI18N && window.CWMI18N.lang === 'hi') || root.getAttribute('data-lang') === 'hi'; }
  function L(en, hin) { return hi() ? hin : en; }

  /* 1. DevTools banner */
  try {
    var art = [
      '   ______        __  __        __  __           ',
      '  / ____/      _/ / / /  __   / / / /           ',
      ' / /   | | /| / / /_/ /  \\ \\ / /_/ /            ',
      '/ /___ | |/ |/ / __  /    \\ / __  /             ',
      '\\____/ |__/|__/_/ /_/     /_/ /_/  CyberWithMadhav'
    ].join('\n');
    console.log('%c' + art, 'color:#8B5CF6;font-family:monospace;font-weight:bold');
    console.log('%cHey, you opened DevTools. You already think like a defender.', 'color:#22C55E;font-weight:bold');
    console.log('Side quest: there is a flag hidden in this page source, a note in /robots.txt and the team in /humans.txt.\n' +
      'Then test yourself for real at https://www.cyberwithmadhav.com/ctf.html\n' +
      'Found a security issue? Please report it: https://www.cyberwithmadhav.com/.well-known/security.txt\n' +
      'Not hiring, always learning. Say hi: madhavpandya@zohomail.in');
  } catch (e) {}

  /* lazy stylesheet, loaded when the browser is idle so it never blocks first paint */
  var cssReady = null;
  function css() {
    if (cssReady) return cssReady;
    cssReady = new Promise(function (res) {
      var l = d.createElement('link'); l.rel = 'stylesheet'; l.href = 'assets/css/eggs.css?v=f72f71331f';
      l.onload = res; l.onerror = res; d.head.appendChild(l);
    });
    return cssReady;
  }
  var idle = window.requestIdleCallback || function (f) { return setTimeout(f, 1200); };

  /* toast: reuse the page toast if present */
  var tT;
  function toast(msg) {
    var t = d.getElementById('toast');
    if (!t) { t = d.createElement('div'); t.id = 'toast'; t.className = 'toast'; t.setAttribute('role', 'status'); t.setAttribute('aria-live', 'polite'); d.body.appendChild(t); }
    t.textContent = msg; t.hidden = false;
    requestAnimationFrame(function () { t.classList.add('show'); });
    clearTimeout(tT);
    tT = setTimeout(function () { t.classList.remove('show'); setTimeout(function () { t.hidden = true; }, 300); }, 3200);
  }

  function teapot() { toast(L('HTTP 418 I\'m a teapot. Brewing chai instead of coffee... done. Stay hydrated, stay patched.', 'HTTP 418 I\'m a teapot. Coffee nahi, chai ban rahi hai... ready. Hydrated raho, patched raho.')); }

  /* 2. root shell panel */
  var panel = null, out, inp, lastFocus = null, rain = null;
  var flag = 'CWM{y0u_f0und_th3_r00t_sh3ll}';
  function cmds(c) {
    c = c.trim().replace(/\s+/g, ' ');
    var lc = c.toLowerCase();
    if (!c) return '';
    if (lc === 'help') return L('commands: whoami, ls, cat flag.txt, ping cyberwithmadhav.com, traceroute 1930, nmap localhost, sudo make me a coffee, matrix, handshake, clear, exit',
                                 'commands: whoami, ls, cat flag.txt, ping cyberwithmadhav.com, traceroute 1930, nmap localhost, sudo make me a coffee, matrix, handshake, clear, exit');
    if (lc === 'whoami') return L('guest. Curious, careful and allowed to be here. That is the right kind of hacker.', 'guest. Curious, careful aur allowed. Yahi sahi wala hacker hai.');
    if (lc === 'ls' || lc === 'ls -la') return 'flag.txt  blog/  ctf/  faq/  start-here/  .secrets (permission denied, as it should be)';
    if (lc === 'cat flag.txt') return flag + '\n' + L('Nice. Real challenges with scores live in the CTF Arena: ctf.html', 'Badhiya. Asli challenges CTF Arena mein hain: ctf.html');
    if (lc.indexOf('cat') === 0) return 'cat: ' + c.slice(4) + ': No such file. Try: cat flag.txt';
    if (lc.indexOf('ping') === 0) return 'PING cyberwithmadhav.com: 64 bytes, icmp_seq=1 ttl=64 time=0.42 ms\n' + L('Server is up. You are reading it right now.', 'Server up hai. Aap abhi padh rahe ho.');
    if (lc.indexOf('traceroute') === 0) return ' 1  you (127.0.0.1)\n 2  your bank: call them and block the card\n 3  1930: National Cyber Crime Helpline\n 4  cybercrime.gov.in: file the complaint\n' + L('Route to help found in 4 hops. Save the complaint number.', 'Help tak 4 hops mein pahunch gaye. Complaint number sambhal ke rakho.');
    if (lc.indexOf('nmap') === 0) return L('Scanning only what you own is the rule. localhost is yours: 80/tcp open http, 443/tcp open https.\nLearn the safe way: blog-nmap-own-lab-guide.html',
                                            'Rule simple hai: sirf apna system scan karo. localhost aapka hai: 80/tcp open http, 443/tcp open https.\nSafe tareeka: blog-nmap-own-lab-guide.html');
    if (lc === 'sudo make me a coffee' || lc === 'make me a coffee' || lc === 'coffee') { teapot(); return 'HTTP/1.1 418 I\'m a teapot'; }
    if (lc.indexOf('sudo') === 0) return L('guest is not in the sudoers file. This incident will be reported (to nobody, relax).', 'guest sudoers file mein nahi hai. Incident report hoga (kisi ko nahi, relax).');
    if (lc === 'handshake') return 'SYN  >\n     < SYN-ACK\nACK  >\n' + L('connection established', 'connection ban gaya');
    if (lc === 'matrix') { matrix(); return reduce ? L('Animation skipped because your device prefers reduced motion.', 'Reduced motion on hai, isliye animation skip.') : L('Packets incoming. Press Esc to stop.', 'Packets aa rahe hain. Rokne ke liye Esc.'); }
    if (lc === 'clear') { out.textContent = ''; return ''; }
    if (lc === 'exit' || lc === 'logout') { close(); return ''; }
    if (lc === 'rm -rf /' || lc === 'rm -rf /*') return L('Nice try. Backups exist for a reason.', 'Nice try. Backup isi liye hota hai.');
    return c.split(' ')[0] + ': command not found. Type help';
  }
  function print(s) { if (!s) return; out.textContent += s + '\n'; out.scrollTop = out.scrollHeight; }
  function build() {
    panel = d.createElement('section');
    panel.className = 'egg-shell';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'false');
    panel.setAttribute('aria-label', 'Root shell easter egg');
    panel.innerHTML = '<div class="egg-bar"><span class="egg-dots" aria-hidden="true"><i></i><i></i><i></i></span><span class="egg-title">guest@cyberwithmadhav:~#</span>' +
      '<button type="button" class="egg-x" aria-label="Close the shell">esc</button></div>' +
      '<pre class="egg-out" aria-live="polite"></pre><canvas class="egg-rain" aria-hidden="true" hidden></canvas>' +
      '<form class="egg-form"><label class="egg-ps" for="egg-in">$</label><input id="egg-in" class="egg-in" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="send"></form>';
    d.body.appendChild(panel);
    out = panel.querySelector('.egg-out'); inp = panel.querySelector('.egg-in');
    panel.querySelector('.egg-x').addEventListener('click', close);
    panel.querySelector('.egg-form').addEventListener('submit', function (e) {
      e.preventDefault(); var v = inp.value; inp.value = ''; print('$ ' + v); print(cmds(v));
    });
    panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') { e.stopPropagation(); if (rain) stopRain(); else close(); } });
  }
  function open() {
    css().then(function () {
      if (!panel) build();
      if (!panel.hidden && panel.classList.contains('on')) { inp.focus(); return; }
      lastFocus = d.activeElement;
      panel.hidden = false; panel.classList.add('on');
      if (!out.textContent) print(L('Access granted. Welcome to the root shell, guest.\nType help to see commands. Esc closes.', 'Access granted. Root shell mein swagat hai, guest.\nCommands ke liye help likho. Esc se band.'));
      inp.focus();
    });
  }
  function close() {
    if (!panel) return; stopRain();
    panel.classList.remove('on'); panel.hidden = true;
    if (lastFocus && lastFocus.focus) try { lastFocus.focus(); } catch (e) {}
  }
  function matrix() {
    if (reduce || !panel) return;
    var cv = panel.querySelector('.egg-rain'); cv.hidden = false;
    var ctx = cv.getContext('2d'), w = cv.width = panel.clientWidth, h = cv.height = 140, cols = Math.floor(w / 14), y = [];
    for (var i = 0; i < cols; i++) y[i] = Math.random() * -20;
    var bits = ['0', '1', 'SYN', 'ACK', 'TTL', '0x1f', '443', 'FIN'], t0 = Date.now();
    function step() {
      ctx.fillStyle = 'rgba(13,11,20,.25)'; ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = '#4ADE80'; ctx.font = '12px monospace';
      for (var i = 0; i < cols; i++) {
        ctx.fillText(bits[(Math.random() * bits.length) | 0], i * 14, y[i] * 14);
        y[i] = y[i] * 14 > h && Math.random() > 0.9 ? 0 : y[i] + 1;
      }
      rain = Date.now() - t0 < 5000 ? requestAnimationFrame(step) : (stopRain(), null);
    }
    rain = requestAnimationFrame(step);
  }
  function stopRain() { if (rain) cancelAnimationFrame(rain); rain = null; if (panel) panel.querySelector('.egg-rain').hidden = true; }

  /* keyboard triggers */
  var K = ['arrowup', 'arrowup', 'arrowdown', 'arrowdown', 'arrowleft', 'arrowright', 'arrowleft', 'arrowright', 'b', 'a'], ki = 0, typed = '';
  d.addEventListener('keydown', function (e) {
    var t = e.target, tag = t && t.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (t && t.isContentEditable) || e.ctrlKey || e.metaKey || e.altKey) return;
    var k = (e.key || '').toLowerCase();
    ki = k === K[ki] ? ki + 1 : (k === K[0] ? 1 : 0);
    if (ki === K.length) { ki = 0; e.preventDefault(); open(); return; } // preventDefault: the final key must not land in the shell input
    if (k.length === 1) {
      typed = (typed + k).slice(-12);
      if (/sudo$/.test(typed)) { typed = ''; e.preventDefault(); open(); }
      else if (/coffee$/.test(typed)) { typed = ''; teapot(); }
    }
  });

  /* logo x5 on the home page (the logo links to #top there, so clicks do not leave the page) */
  var clicks = 0, cT;
  d.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('a.brand');
    if (!b || b.getAttribute('href') !== '#top') return;
    clicks++; clearTimeout(cT); cT = setTimeout(function () { clicks = 0; }, 1500);
    if (clicks >= 5) { clicks = 0; teapot(); }
  });

  /* 3. footer handshake line, hex headings: added when idle */
  function pktId() {
    var s = location.pathname || '/', h = 0;
    for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
    return '10.' + ((h >> 16) & 255) + '.' + ((h >> 8) & 255) + '.' + (h & 255);
  }
  function hsText() { return 'SYN \u2192 SYN-ACK \u2192 ACK \u00b7 ' + L('connection established', 'connection ban gaya') + ' \u00b7 page id ' + pktId(); }
  idle(function () {
    css().then(function () {
      var f = d.querySelector('footer.footer .wrap');
      if (f && !f.querySelector('.egg-hs')) {
        var p = d.createElement('p'); p.className = 'egg-hs mono small'; p.setAttribute('aria-hidden', 'true'); p.textContent = hsText();
        var taps = 0, tt;
        p.addEventListener('click', function () { taps++; clearTimeout(tt); tt = setTimeout(function () { taps = 0; }, 1200); if (taps >= 3) { taps = 0; open(); } });
        f.appendChild(p);
        d.addEventListener('cwm:lang', function () { p.textContent = hsText(); });
      }
      if (window.matchMedia && window.matchMedia('(hover: hover)').matches) {
        Array.prototype.forEach.call(d.querySelectorAll('main h2'), function (h) {
          var s = (h.textContent || '').trim().slice(0, 4); if (!s) return;
          var hex = Array.prototype.map.call(s, function (ch) { return '0x' + ch.charCodeAt(0).toString(16); }).join(' ');
          h.setAttribute('data-hex', hex); h.classList.add('egg-hex');
        });
      }
    });
  });
})();
