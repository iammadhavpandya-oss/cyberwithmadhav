/* CyberWithMadhav Learn: a small Cisco IOS style CLI simulator for practice (switch or router).
 * Modes, abbreviations, ? help, Tab completion, running-config built from state, missions checked against it.
 * It is a teaching aid, not real IOS: only the commands these lessons use are implemented.
 * Config comes from <script type="application/json" class="lx-ios-cfg">. CSP safe (no eval). */
(function () {
  'use strict';
  function $(s, r) { return (r || document).querySelector(s); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function T(k, en) { return window.CWMI18N && window.CWMI18N.t ? window.CWMI18N.t(k, en) : en; }

  /* Cisco type 7 is a reversible XOR with a published key. Real algorithm, shown so learners see why it is weak. */
  var XLAT = 'dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87';
  function type7(pw, seed) {
    var s = seed % 16, out = (s < 10 ? '0' : '') + s;
    for (var i = 0; i < pw.length; i++) { var x = (pw.charCodeAt(i) ^ XLAT.charCodeAt((s + i) % XLAT.length)).toString(16).toUpperCase(); out += x.length < 2 ? '0' + x : x; }
    return out;
  }
  function unType7(h) {
    var s = parseInt(h.slice(0, 2), 10), out = '';
    for (var i = 2; i + 1 < h.length; i += 2) out += String.fromCharCode(parseInt(h.slice(i, i + 2), 16) ^ XLAT.charCodeAt((s + (i - 2) / 2) % XLAT.length));
    return out;
  }
  /* Stand-in for an MD5-crypt (type 5) hash: same shape, not the real digest. */
  function fakeHash(pw) {
    var a = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./', h = 2166136261, o = '';
    for (var k = 0; k < 26; k++) { for (var i = 0; i < pw.length; i++) { h ^= pw.charCodeAt(i) + k * 31; h = Math.imul(h, 16777619) >>> 0; } o += a[h % 64]; }
    return '$1$' + o.slice(0, 4) + '$' + o.slice(4, 26);
  }

  var TYPES = [['GigabitEthernet', ['gigabitethernet', 'gi', 'g']], ['FastEthernet', ['fastethernet', 'fa', 'f']], ['Vlan', ['vlan', 'vl']], ['Loopback', ['loopback', 'lo']], ['Port-channel', ['port-channel', 'po']]];
  function ifName(type, num) {
    var t = type.toLowerCase();
    for (var i = 0; i < TYPES.length; i++) {
      var full = TYPES[i][0].toLowerCase();
      if (TYPES[i][1].indexOf(t) > -1 || (t.length >= 2 && full.indexOf(t) === 0)) return TYPES[i][0] + num;
    }
    return null;
  }
  function shortIf(n) { return n.replace('GigabitEthernet', 'Gi').replace('FastEthernet', 'Fa').replace('Loopback', 'Lo').replace('Port-channel', 'Po'); }
  function ipOk(s) { return /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/.test(s) && s.split('.').every(function (x) { return +x < 256; }); }
  function ip2n(s) { return s.split('.').reduce(function (a, b) { return (a * 256) + (+b); }, 0) >>> 0; }
  function n2ip(n) { return [n >>> 24, (n >>> 16) & 255, (n >>> 8) & 255, n & 255].join('.'); }
  function maskLen(m) { var n = ip2n(m), c = 0; while (n & 0x80000000) { c++; n = (n << 1) >>> 0; } return c; }

  /* Command table. Specs: literal 'a|b', '<w>' word, '<n>' number, '<ip>' IPv4, '<if>' interface, '<rest>' remainder. */
  var C = [];
  function def(modes, spec, fn, help) { C.push({ m: modes.split(' '), s: spec.split(' '), fn: fn, h: help || '' }); }

  function Sim(el, cfg) {
    this.el = el; this.cfg = cfg; this.out = $('.lx-term-out', el); this.input = $('input', el); this.label = $('.lx-term-in label', el);
    this.mlist = $('.lx-missions ol', el); this.hist = []; this.hi = 0; var self = this;
    this.input.addEventListener('keydown', function (e) { self.key(e); });
    this.out.addEventListener('click', function () { if (!window.getSelection().toString()) self.input.focus(); });
    var rb = $('[data-reset]', el); if (rb) rb.addEventListener('click', function () { self.reset(); self.input.focus(); });
    this.reset();
  }
  Sim.prototype.reset = function () {
    var c = this.cfg, sw = c.kind !== 'router', st = { host: c.host || (sw ? 'Switch' : 'Router'), ifs: {}, order: [], vlans: { 1: 'default' }, lines: {}, users: {}, spe: false,
      dl: true, dom: '', gx: {}, keys: 0, sshv: 0, gw: '', banner: '', ens: '', enp: '', cdp: true, lldp: false, routing: !sw, saved: null };
    (c.ifaces || []).forEach(function (n) { st.ifs[n] = { shut: !sw || /^Vlan/.test(n), sp: sw && !/^Vlan/.test(n), mode: 'dynamic auto', av: 1, cdp: true }; st.order.push(n); });
    Object.keys(c.vlans || {}).forEach(function (v) { st.vlans[v] = c.vlans[v]; });
    Object.keys(c.init || {}).forEach(function (n) { if (st.ifs[n]) { var v = JSON.parse(JSON.stringify(c.init[n])); Object.keys(v).forEach(function (k) { st.ifs[n][k] = v[k]; }); } });
    st.lines['con 0'] = { login: '', pw: '', tin: '', to: '' };
    for (var v = 0; v < (sw ? 16 : 5); v++) st.lines['vty ' + v] = { login: v < 5 ? 'login' : 'login', pw: '', tin: '', to: '', ac: '' };
    this.st = st; this.mode = 'user'; this.ctx = null; this.pending = null; this.mi = 0; this.lastOut = ''; this.lastCmd = '';
    this.out.innerHTML = '';
    (c.intro || []).forEach(function (l) { this.print(l, 'dim'); }, this);
    this.print('Simplified IOS simulator: modes, abbreviations (conf t, int g0/1), ? for help and Tab to complete. Type exit or end to step back.', 'dim');
    this.renderMissions(); this.prompt();
  };
  Sim.prototype.print = function (t, cls) { var d = document.createElement('div'); if (cls) d.className = cls; d.textContent = t; this.out.appendChild(d); this.out.scrollTop = this.out.scrollHeight; };
  Sim.prototype.printHTML = function (h) { var d = document.createElement('div'); d.innerHTML = h; this.out.appendChild(d); this.out.scrollTop = this.out.scrollHeight; };
  Sim.prototype.say = function (t) { this.buf.push(t); };
  Sim.prototype.prompt = function () {
    if (this.pending) { this.label.textContent = this.pending.q; this.ps = esc(this.pending.q); return; }
    var m = { user: '>', priv: '#', config: '(config)#', 'if': '(config-if)#', range: '(config-if-range)#', subif: '(config-subif)#', line: '(config-line)#', vlan: '(config-vlan)#' }[this.mode];
    this.label.textContent = this.st.host + m; this.ps = esc(this.st.host + m);
  };
  Sim.prototype.renderMissions = function () {
    var ms = this.cfg.missions || [], self = this; if (!this.mlist) return;
    this.mlist.innerHTML = ms.map(function (m, i) {
      var cls = i < self.mi ? 'done' : i === self.mi ? 'now' : '';
      return '<li class="' + cls + '"><span>' + m.t + '</span>' + (i === self.mi && m.hint ? ' <details><summary>' + esc(T('lx.hint', 'Hint')) + '</summary><code>' + esc(m.hint) + '</code></details>' : '') + '</li>';
    }).join('');
    var cnt = $('.lx-mcount', this.el); if (cnt) cnt.textContent = Math.min(this.mi, ms.length) + '/' + ms.length;
  };

  /* ---------- parsing ---------- */
  function toks(line) { return line.trim().split(/\s+/).filter(Boolean); }
  function matchCmd(cmd, tk, raw) {
    var a = [], lit = [], ti = 0;
    for (var k = 0; k < cmd.s.length; k++) {
      var sp = cmd.s[k], t = tk[ti];
      if (sp === '<rest>') { if (t == null) return { ok: false, at: ti, inc: true }; a.push(restFrom(raw, ti)); ti = tk.length; continue; }
      if (t == null) return { ok: false, at: ti, inc: true };
      if (sp === '<w>') { a.push(t); ti++; continue; }
      if (sp === '<n>') { if (!/^\d+$/.test(t)) return { ok: false, at: ti }; a.push(+t); ti++; continue; }
      if (sp === '<ip>') { if (!ipOk(t)) return { ok: false, at: ti }; a.push(t); ti++; continue; }
      if (sp === '<if>') {
        var m1 = /^([a-z-]+)([\d/.]+)$/i.exec(t), nm = null;
        if (m1) nm = ifName(m1[1], m1[2]);
        else if (/^[a-z-]+$/i.test(t) && tk[ti + 1] && /^\d/.test(tk[ti + 1])) { nm = ifName(t, tk[ti + 1]); if (nm) ti++; }
        if (!nm) return { ok: false, at: ti };
        a.push(nm); ti++; continue;
      }
      var kws = sp.split('|'), lw = t.toLowerCase(), hit = kws.filter(function (w) { return w.indexOf(lw) === 0; });
      if (!hit.length) return { ok: false, at: ti };
      var ex = hit.indexOf(lw) > -1 ? lw : hit[0];
      lit.push({ ti: ti, kw: ex, exact: ex === lw }); if (kws.length > 1) a.push(ex); ti++;
    }
    if (ti < tk.length) return { ok: false, at: ti };
    return { ok: true, a: a, lit: lit };
  }
  function restFrom(raw, ti) { var r = raw.trim(), i = 0; for (var k = 0; k < ti; k++) { r = r.slice(r.search(/\s/)).replace(/^\s+/, ''); i++; } return r; }

  Sim.prototype.find = function (mode, tk, raw) {
    var full = [], far = { at: -1, inc: false };
    C.forEach(function (c) {
      if (c.m.indexOf(mode) < 0) return;
      var r = matchCmd(c, tk, raw);
      if (r.ok) full.push({ c: c, a: r.a, lit: r.lit });
      else if (r.at > far.at || (r.at === far.at && r.inc)) far = { at: r.at, inc: !!r.inc };
    });
    if (full.length > 1) {
      for (var ti = 0; ti < tk.length && full.length > 1; ti++) {
        var at = function (f) { for (var q = 0; q < f.lit.length; q++) if (f.lit[q].ti === ti) return f.lit[q]; return null; };
        var anyEx = full.some(function (f) { var l = at(f); return l && l.exact; });
        if (anyEx) full = full.filter(function (f) { var l = at(f); return !l || l.exact; });
      }
    }
    if (full.length > 1) {
      var ex = full.filter(function (f) { return f.lit.every(function (l) { return l.exact; }); });
      if (ex.length === 1) full = ex;
      else {
        var sig = function (f) { return f.c.s.filter(function (x) { return x[0] !== '<'; }).join(' '); };
        var uniq = {}; full.forEach(function (f) { uniq[sig(f)] = f; });
        var ks = Object.keys(uniq); if (ks.length === 1) full = [uniq[ks[0]]];
      }
    }
    return { full: full, far: far };
  };

  /* ---------- input ---------- */
  Sim.prototype.key = function (e) {
    if (e.key === 'Enter') { var v = this.input.value; this.input.value = ''; this.run(v); }
    else if (e.key === 'ArrowUp') { if (this.hi > 0) { this.hi--; this.input.value = this.hist[this.hi]; } e.preventDefault(); }
    else if (e.key === 'ArrowDown') { if (this.hi < this.hist.length) { this.hi++; this.input.value = this.hist[this.hi] || ''; } e.preventDefault(); }
    else if (e.key === 'Tab') { e.preventDefault(); this.complete(); }
    else if (e.key === '?' && !this.pending && !/^\s*(banner|description|enable|username|password)\b/i.test(this.input.value)) { e.preventDefault(); this.help(this.input.value); }
  };
  Sim.prototype.nextWords = function (line) {
    var tk = toks(line), partial = /\S$/.test(line) ? tk.pop() : '', set = {}, mode = this.mode, modes = [mode];
    if (mode !== 'user' && mode !== 'priv') modes.push('config');
    if (/^do$/i.test(tk[0] || '')) { tk.shift(); modes = ['priv']; }
    C.forEach(function (c) {
      if (!modes.some(function (m) { return c.m.indexOf(m) > -1; })) return;
      var r = matchCmd({ s: c.s.slice(0, tk.length) }, tk, line);
      if (!r.ok || c.s.length <= tk.length) return;
      var sp = c.s[tk.length];
      (sp[0] === '<' ? [sp === '<if>' ? 'WORD (interface)' : sp === '<ip>' ? 'A.B.C.D' : sp === '<n>' ? '<number>' : 'LINE'] : sp.split('|')).forEach(function (w) { if (!partial || w.indexOf(partial.toLowerCase()) === 0) set[w] = c.h; });
    });
    return { words: set, partial: partial };
  };
  Sim.prototype.help = function (line) {
    var nw = this.nextWords(line), ks = Object.keys(nw.words).sort();
    this.printHTML('<span class="pr">' + this.ps + '</span>' + esc(line) + '?');
    if (!ks.length) this.print('% Unrecognized command', 'er');
    else ks.forEach(function (k) { this.print('  ' + (k + '                    ').slice(0, 22) + (nw.words[k] || '')); }, this);
  };
  Sim.prototype.complete = function () {
    var v = this.input.value, nw = this.nextWords(v), ks = Object.keys(nw.words).filter(function (k) { return k[0] !== '<' && !/^[A-Z]/.test(k); });
    if (ks.length === 1 && nw.partial) this.input.value = v.slice(0, v.length - nw.partial.length) + ks[0] + ' ';
  };

  Sim.prototype.run = function (line) {
    this.printHTML('<span class="pr">' + this.ps + '</span>' + esc(this.pending && this.pending.secret ? '' : line));
    this.buf = [];
    if (this.pending) { var p = this.pending; this.pending = null; p.fn.call(this, line.trim()); this.flush(); this.prompt(); this.check(line, p.cmd || ''); return; }
    line = line.slice(0, 300);
    if (!line.trim()) { this.prompt(); return; }
    this.hist.push(line); this.hi = this.hist.length;
    var am = /^\s*answer\s+(.+)$/i.exec(line);
    if (am) {
      var mm = (this.cfg.missions || [])[this.mi];
      if (!mm || mm.c.type !== 'answer') this.print('No question is waiting for an answer right now.', 'dim');
      else if (![].concat(mm.c.v).some(function (v) { return am[1].trim().replace(/\s+/g, ' ').toLowerCase() === String(v).toLowerCase(); })) this.print('Not that one. Look at the output again.', 'er');
      this.lastAns = am[1].trim(); this.prompt(); this.check(line, ''); this.lastAns = null; return;
    }
    var flt = null, pm0 = /^(.*?\S)\s+\|\s+(include|exclude|begin|section|i|e|b|s|inc|incl|excl|beg|sec)\s+(.+)$/i.exec(line);
    if (pm0) { flt = { k: pm0[2].toLowerCase()[0], re: null }; try { flt.re = new RegExp(pm0[3].trim(), 'i'); } catch (e0) { flt.re = new RegExp(pm0[3].trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'); } line = pm0[1]; }
    var tk = toks(line), mode = this.mode, raw = line;
    if (/^do$/i.test(tk[0]) && mode !== 'user' && mode !== 'priv') { tk.shift(); raw = line.replace(/^\s*do\s+/i, ''); mode = 'priv'; this.doing = true; }
    var r = this.find(mode, tk, raw), usedMode = mode;
    if (!r.full.length && mode !== 'user' && mode !== 'priv' && mode !== 'config' && !this.doing) {
      var r2 = this.find('config', tk, raw);
      if (r2.full.length) { r = r2; usedMode = 'config'; }
    }
    if (r.full.length === 1) {
      var f = r.full[0];
      if (usedMode === 'config' && this.mode !== 'config' && !this.doing) { this.mode = 'config'; this.ctx = null; }
      this.lastCmd = f.c.s.map(function (s, i) { return s; }).join(' ');
      f.c.fn.call(this, f.a, raw, tk);
    } else if (r.full.length > 1 || this.ambiguous(usedMode, tk, raw)) this.say('% Ambiguous command:  "' + line.trim() + '"');
    else if (r.far.inc && r.far.at >= tk.length) this.say('% Incomplete command.');
    else {
      var pos = 0, t2 = line.replace(/^\s*do\s+/i, this.doing ? '' : '$&');
      var parts = toks(t2); for (var i = 0; i < Math.max(0, r.far.at); i++) pos = t2.indexOf(parts[i], pos) + parts[i].length;
      pos = t2.indexOf(parts[Math.max(0, r.far.at)] || '', pos);
      this.say(' '.repeat(this.ps.replace(/&[a-z]+;/g, 'x').length + Math.max(0, pos)) + '^');
      this.say("% Invalid input detected at '^' marker.");
    }
    this.doing = false;
    if (flt && this.buf.length) {
      var ls = this.buf.join('\n').split('\n'), res = [], on = false;
      ls.forEach(function (l) {
        if (flt.k === 'i') { if (flt.re.test(l)) res.push(l); }
        else if (flt.k === 'e') { if (!flt.re.test(l)) res.push(l); }
        else if (flt.k === 'b') { if (on || flt.re.test(l)) { on = true; res.push(l); } }
        else { if (/^\S/.test(l)) on = flt.re.test(l); if (on) res.push(l); }
      });
      this.buf = res;
    }
    this.flush(); this.prompt(); this.check(line, this.lastCmd);
  };
  Sim.prototype.flush = function () {
    var txt = this.buf.join('\n'); this.lastOut = txt;
    this.buf.forEach(function (l) { this.print(l, /^%(LINK|LINEPROTO|SYS|SSH)/.test(l) ? 'ok' : (/^% ?\S/.test(l) && !/^% (Access VLAN|Voice VLAN|The key|Generating)/.test(l)) || /^(Command rejected|Please create|\s+\^$)/.test(l) ? 'er' : ''); }, this);
    this.buf = [];
  };
  Sim.prototype.ambiguous = function (mode, tk, raw) {
    for (var p = 0; p < tk.length; p++) {
      var pre = tk.slice(0, p), kws = {}, t = tk[p].toLowerCase();
      C.forEach(function (c) {
        if (c.m.indexOf(mode) < 0 || c.s.length <= p) return;
        if (!matchCmd({ s: c.s.slice(0, p) }, pre, raw).ok) return;
        var sp = c.s[p]; if (sp[0] === '<') return;
        sp.split('|').forEach(function (w) { if (w.indexOf(t) === 0) kws[w] = 1; });
      });
      var ks = Object.keys(kws);
      if (ks.length > 1 && ks.indexOf(t) < 0) return true;
      if (!ks.length) return false;
    }
    return false;
  };
  Sim.prototype.ask = function (q, fn, secret) { this.pending = { q: q, fn: fn, secret: secret }; };

  /* ---------- state helpers ---------- */
  Sim.prototype.cur = function () { return this.ctx || []; };
  Sim.prototype.isSw = function () { return this.cfg.kind !== 'router'; };
  Sim.prototype.vlanHasUp = function (v) {
    var st = this.st, up = this.cfg.up || [];
    return st.order.some(function (n) { var i = st.ifs[n]; return i.sp && !i.shut && up.indexOf(n) > -1 && (i.mode === 'trunk' || i.av === v); });
  };
  Sim.prototype.ifUp = function (n) {
    var i = this.st.ifs[n]; if (!i || i.shut) return false;
    var vm = /^Vlan(\d+)$/.exec(n); if (vm) return !!this.st.vlans[+vm[1]] && this.vlanHasUp(+vm[1]);
    var base = n.split('.')[0]; if (n.indexOf('.') > -1) return this.ifUp(base);
    var pm = /^Port-channel(\d+)$/.exec(n), st = this.st, self = this; if (pm) return st.order.some(function (x) { return st.ifs[x].cg && st.ifs[x].cg.n === +pm[1] && self.ifUp(x); });
    return (this.cfg.up || []).indexOf(n) > -1;
  };
  Sim.prototype.ensureIf = function (n) {
    var st = this.st;
    if (st.ifs[n]) return true;
    var vm = /^Vlan(\d+)$/.exec(n), sub = /^(.+)\.(\d+)$/.exec(n);
    if (vm && this.isSw()) { st.ifs[n] = { shut: true, sp: false }; st.order.push(n); this.say('%LINK-5-CHANGED: Interface ' + n + ', changed state to administratively down'); return true; }
    if (sub && st.ifs[sub[1]] && !this.isSw()) { st.ifs[n] = { shut: false, sp: false, sub: true }; st.order.splice(st.order.indexOf(sub[1]) + 1 + st.order.filter(function (x) { return x.indexOf(sub[1] + '.') === 0; }).length, 0, n); return true; }
    if (/^Port-channel\d+$/.test(n) && this.isSw()) { st.ifs[n] = { shut: false, sp: true, mode: 'dynamic auto', av: 1, cdp: true, po: true }; st.order.push(n); return true; }
    if (/^Loopback\d+$/.test(n)) { st.ifs[n] = { shut: false, sp: false }; st.order.push(n); this.say('%LINK-3-UPDOWN: Interface ' + n + ', changed state to up'); this.say('%LINEPROTO-5-UPDOWN: Line protocol on Interface ' + n + ', changed state to up'); this.cfg.up = (this.cfg.up || []).concat([n]); return true; }
    return false;
  };
  Sim.prototype.each = function (fn) { var self = this; this.cur().forEach(function (n) { fn.call(self, self.st.ifs[n], n); }); };

  /* ---------- running-config ---------- */
  Sim.prototype.running = function () {
    var st = this.st, o = ['Building configuration...', '', 'Current configuration:', '!'];
    o.push(st.spe ? 'service password-encryption' : 'no service password-encryption', '!', 'hostname ' + st.host, '!');
    if (st.ens) o.push('enable secret 5 ' + fakeHash(st.ens));
    if (st.enp) o.push('enable password ' + (st.spe ? '7 ' + type7(st.enp, 7) : st.enp));
    if (st.ens || st.enp) o.push('!');
    if (st.routing && this.isSw()) o.push('ip routing', '!');
    if (!st.dl) o.push('no ip domain-lookup');
    if (st.dom) o.push('ip domain-name ' + st.dom);
    if (!st.dl || st.dom) o.push('!');
    Object.keys(st.users).forEach(function (u) { var x = st.users[u]; o.push('username ' + u + (x.priv ? ' privilege ' + x.priv : '') + (x.s ? ' secret 5 ' + fakeHash(x.s) : ' password ' + (st.spe ? '7 ' + type7(x.p, 4) : x.p))); });
    if (Object.keys(st.users).length) o.push('!');
    if (st.sshv) o.push('ip ssh version ' + st.sshv, '!');
    if (!st.cdp) o.push('no cdp run', '!');
    var gk = Object.keys(st.gx); gk.forEach(function (k) { o.push(st.gx[k]); }); if (gk.length) o.push('!');
    if (st.lldp) o.push('lldp run', '!');
    var sw = this.isSw();
    st.order.forEach(function (n) {
      var i = st.ifs[n]; o.push('interface ' + n);
      if (i.desc) o.push(' description ' + i.desc);
      if (i.enc) o.push(' encapsulation dot1Q ' + i.enc + (i.nat ? ' native' : ''));
      if (i.sp) {
        if (i.av !== 1) o.push(' switchport access vlan ' + i.av);
        if (i.native && i.native !== 1) o.push(' switchport trunk native vlan ' + i.native);
        if (i.allowed) o.push(' switchport trunk allowed vlan ' + i.allowed);
        if (i.mode === 'access' || i.mode === 'trunk') o.push(' switchport mode ' + i.mode);
        else if (i.mode === 'dynamic desirable') o.push(' switchport mode dynamic desirable');
        if (i.nonego) o.push(' switchport nonegotiate');
        if (i.voice) o.push(' switchport voice vlan ' + i.voice);
      } else if (i.ip) o.push(' ip address ' + i.ip + ' ' + i.mask);
      else if (!i.sp) o.push(' no ip address');
      Object.keys(i.x || {}).forEach(function (k) { o.push(' ' + i.x[k]); });
      if (!i.cdp && i.cdp !== undefined) o.push(' no cdp enable');
      if (i.shut) o.push(' shutdown');
      o.push('!');
    });
    if (st.gw) o.push('ip default-gateway ' + st.gw, '!');
    (st.routes || []).forEach(function (r) { o.push('ip route ' + r.txt); });
    (st.v6r || []).forEach(function (r) { o.push('ipv6 route ' + r); });
    if (st.banner) o.push('banner motd ^C' + st.banner + '^C', '!');
    var ln = function (k) { var x = st.lines[k], r = []; if (x.ac) r.push(' access-class ' + x.ac + ' in'); if (x.to) r.push(' exec-timeout ' + x.to); if (x.pw) r.push(' password ' + (st.spe ? '7 ' + type7(x.pw, 9) : x.pw)); if (x.login) r.push(' ' + x.login); if (x.tin) r.push(' transport input ' + x.tin); return r; };
    o.push('line con 0'); o = o.concat(ln('con 0'));
    var vt = Object.keys(st.lines).filter(function (k) { return k.indexOf('vty') === 0; }).map(function (k) { return +k.slice(4); }).sort(function (a, b) { return a - b; });
    var start = 0;
    for (var v = 1; v <= vt.length; v++) {
      if (v === vt.length || v === 5 || JSON.stringify(ln('vty ' + v)) !== JSON.stringify(ln('vty ' + start))) {
        o.push('line vty ' + start + ' ' + (v - 1)); o = o.concat(ln('vty ' + start)); start = v;
      }
    }
    o.push('!', 'end');
    return o.join('\n');
  };

  /* ---------- missions ---------- */
  Sim.prototype.check = function (line, cmd) {
    var ms = this.cfg.missions || [], m = ms[this.mi]; if (!m) return;
    var c = m.c, ok = false, st = this.st;
    switch (c.type) {
      case 'cmd': ok = new RegExp(c.re, 'i').test(this.lastCmd) && (!c.raw || new RegExp(c.raw, 'i').test(line)); break;
      case 'run': ok = new RegExp(c.re, 'm').test(this.running()); break;
      case 'vlan': ok = st.vlans[c.id] && (!c.name || st.vlans[c.id] === c.name); break;
      case 'mode': ok = this.mode === c.m; break;
      case 'saved': ok = !!st.saved && st.saved === this.running(); break;
      case 'out': ok = new RegExp(c.re, 'm').test(this.lastOut); break;
      case 'answer': var la = this.lastAns; ok = la != null && [].concat(c.v).some(function (v) { return la.trim().replace(/\s+/g, ' ').toLowerCase() === String(v).toLowerCase(); }); break;
    }
    if (!ok) return;
    this.print('Mission ' + (this.mi + 1) + ' complete. ' + (m.ok || ''), 'ok');
    this.mi++; this.renderMissions();
    if (this.mi === ms.length) {
      this.print('All ' + ms.length + ' missions done. Now repeat the same steps in Packet Tracer.', 'ok');
      document.dispatchEvent(new CustomEvent('cwm:term-done', { detail: { id: this.cfg.id } }));
    }
  };

  /* ---------- commands ---------- */
  var CFGS = 'config if range subif line vlan';
  def('user', 'enable', function () {
    if (this.st.ens || this.st.enp) this.ask('Password: ', function (v) { if (v === (this.st.ens || this.st.enp)) this.mode = 'priv'; else this.say('% Bad secrets'); }, true);
    else this.mode = 'priv';
  }, 'Turn on privileged commands');
  def('priv', 'disable', function () { this.mode = 'user'; }, 'Turn off privileged commands');
  def('user priv', 'exit|logout', function () { this.mode = 'user'; this.say(''); this.say(this.st.host + ' con0 is now available. Press RETURN to get started.'); }, 'Exit from the EXEC');
  def('priv', 'configure terminal', function () { this.mode = 'config'; this.say('Enter configuration commands, one per line.  End with CNTL/Z.'); }, 'Enter configuration mode');
  def('priv', 'show running-config', function () { this.say(this.running()); }, 'Current operating configuration');
  def('priv', 'show startup-config', function () { this.say(this.st.saved || 'startup-config is not present'); }, 'Contents of startup configuration');
  def('priv', 'copy running-config startup-config', function () { this.ask('Destination filename [startup-config]? ', function () { this.say('Building configuration...'); this.say('[OK]'); this.st.saved = this.running(); }); this.pending.cmd = 'copy running-config startup-config'; }, 'Save the configuration');
  def('priv', 'write memory', function () { this.say('Building configuration...'); this.say('[OK]'); this.st.saved = this.running(); }, 'Write to NV memory');
  def('priv', 'write', function () { this.say('Building configuration...'); this.say('[OK]'); this.st.saved = this.running(); }, 'Write running configuration');
  def('user priv', 'show ip interface brief', function () {
    var self = this, st = this.st, o = ['Interface              IP-Address      OK? Method Status                Protocol'];
    st.order.forEach(function (n) {
      var i = st.ifs[n], up = self.ifUp(n), stat = i.shut ? 'administratively down' : up ? 'up' : 'down';
      o.push((n + '                       ').slice(0, 23) + ((i.ip || 'unassigned') + '                ').slice(0, 16) + 'YES ' + (i.ip ? 'manual ' : 'unset  ') + (stat + '                      ').slice(0, 22) + (up ? 'up' : 'down'));
    });
    this.say(o.join('\n'));
  }, 'Brief summary of IP status');
  def('user priv', 'show vlan brief', function () {
    if (!this.isSw()) { this.say("% Invalid input detected at '^' marker."); return; }
    var st = this.st, o = ['', 'VLAN Name                             Status    Ports', '---- -------------------------------- --------- -------------------------------'];
    Object.keys(st.vlans).map(Number).sort(function (a, b) { return a - b; }).forEach(function (v) {
      var ports = st.order.filter(function (n) { var i = st.ifs[n]; return i.sp && i.mode !== 'trunk' && i.av === v; }).map(shortIf);
      var rows = []; for (var k = 0; k < Math.max(1, ports.length); k += 4) rows.push(ports.slice(k, k + 4).join(', '));
      o.push((v + '    ').slice(0, 5) + (st.vlans[v] + '                                 ').slice(0, 33) + 'active    ' + rows[0]);
      rows.slice(1).forEach(function (r) { o.push('                                                ' + r); });
    });
    o.push('1002 fddi-default                     act/unsup', '1003 token-ring-default               act/unsup', '1004 fddinet-default                  act/unsup', '1005 trnet-default                    act/unsup');
    this.say(o.join('\n'));
  }, 'VLAN summary');
  def('priv', 'show interfaces trunk', function () {
    var st = this.st, self = this, tr = st.order.filter(function (n) { var i = st.ifs[n]; return i.sp && i.mode === 'trunk' && self.ifUp(n); });
    if (!tr.length) return;
    var o = ['', 'Port        Mode             Encapsulation  Status        Native vlan'];
    tr.forEach(function (n) { o.push((shortIf(n) + '            ').slice(0, 12) + 'on               802.1q         trunking      ' + (st.ifs[n].native || 1)); });
    o.push('', 'Port        Vlans allowed on trunk');
    tr.forEach(function (n) { o.push((shortIf(n) + '            ').slice(0, 12) + (st.ifs[n].allowed || '1-4094')); });
    o.push('', 'Port        Vlans allowed and active in management domain');
    tr.forEach(function (n) {
      var al = st.ifs[n].allowed, act = Object.keys(st.vlans).map(Number).filter(function (v) {
        if (!al) return true; return al.split(',').some(function (p) { var r = p.split('-'); return r.length > 1 ? v >= +r[0] && v <= +r[1] : v === +r[0]; });
      });
      o.push((shortIf(n) + '            ').slice(0, 12) + act.join(','));
    });
    this.say(o.join('\n'));
  }, 'Show trunk information');
  def('priv', 'show interfaces <if> switchport', function (a) {
    var i = this.st.ifs[a[0]]; if (!i || !i.sp) { this.say('% Invalid interface'); return; }
    var op = i.mode === 'trunk' ? 'trunk' : i.mode === 'access' ? 'static access' : 'static access';
    this.say(['Name: ' + shortIf(a[0]), 'Switchport: Enabled', 'Administrative Mode: ' + (i.mode === 'access' ? 'static access' : i.mode), 'Operational Mode: ' + (this.ifUp(a[0]) ? op : 'down'),
      'Administrative Trunking Encapsulation: dot1q', 'Negotiation of Trunking: ' + (i.nonego || i.mode === 'access' ? 'Off' : 'On'), 'Access Mode VLAN: ' + i.av + ' (' + (this.st.vlans[i.av] || 'Inactive') + ')',
      'Trunking Native Mode VLAN: ' + (i.native || 1) + ' (' + (this.st.vlans[i.native || 1] || 'Inactive') + ')', 'Voice VLAN: ' + (i.voice ? i.voice + ' (' + (this.st.vlans[i.voice] || 'Inactive') + ')' : 'none')].join('\n'));
  }, 'Show switchport information');
  def('priv', 'show interfaces status', function () {
    if (!this.isSw()) { this.say("% Invalid input detected at '^' marker."); return; }
    var st = this.st, self = this, o = ['', 'Port      Name               Status       Vlan       Duplex  Speed Type'];
    st.order.forEach(function (n) {
      var i = st.ifs[n]; if (!i.sp) return;
      var s = i.shut ? 'disabled' : self.ifUp(n) ? 'connected' : 'notconnect';
      o.push((shortIf(n) + '          ').slice(0, 10) + ((i.desc || '') + '                   ').slice(0, 19) + (s + '             ').slice(0, 13) + ((i.mode === 'trunk' ? 'trunk' : String(i.av)) + '           ').slice(0, 11) + (self.ifUp(n) ? 'a-full  a-100 ' : '  auto   auto ') + (/^Gi/.test(shortIf(n)) ? '10/100/1000BaseTX' : '10/100BaseTX'));
    });
    this.say(o.join('\n'));
  }, 'Show interface line status');
  def('user priv', 'show ip ssh', function () {
    var st = this.st;
    if (!st.keys) this.say('SSH Disabled - version 1.99\n%Please create RSA keys to enable SSH (and of atleast 768 bits for SSH v2).\nAuthentication timeout: 120 secs; Authentication retries: 3');
    else this.say('SSH Enabled - version ' + (st.sshv === 2 ? '2.0' : '1.99') + '\nAuthentication timeout: 120 secs; Authentication retries: 3');
  }, 'Information on SSH');
  Sim.prototype.routeEnts = function () {
    var st = this.st, self = this, ent = [];
    st.order.forEach(function (n) {
      var i = st.ifs[n]; if (!i.ip || !self.ifUp(n)) return;
      var len = maskLen(i.mask), nn = (ip2n(i.ip) & (len ? (0xFFFFFFFF << (32 - len)) >>> 0 : 0)) >>> 0;
      ent.push({ nn: nn, len: len, k: 0, code: 'C', ad: 0, oif: n, line: 'C        ' + n2ip(nn) + '/' + len + ' is directly connected, ' + n }, { nn: ip2n(i.ip), len: 32, k: 1, code: 'L', ad: 0, oif: n, line: 'L        ' + i.ip + '/32 is directly connected, ' + n });
    });
    this.installed().forEach(function (r) { ent.push({ nn: ip2n(r.net), len: maskLen(r.mask), k: 2, code: 'S', ad: r.ad, nh: r.nh, oif: r.oif, line: (r.net === '0.0.0.0' ? 'S*       ' : 'S        ') + r.net + '/' + maskLen(r.mask) + (r.nh ? ' [' + r.ad + '/0] via ' + r.nh + (r.oif ? ', ' + r.oif : '') : ' is directly connected, ' + r.oif) }); });
    return ent.sort(function (a, b) { return a.nn - b.nn || a.len - b.len || a.k - b.k; });
  };
  Sim.prototype.routeHead = function () {
    var df = this.installed().filter(function (r) { return r.net === '0.0.0.0' && r.mask === '0.0.0.0'; })[0];
    return ['Codes: L - local, C - connected, S - static, O - OSPF', '       * - candidate default', '', df ? 'Gateway of last resort is ' + (df.nh || '0.0.0.0') + ' to network 0.0.0.0' : 'Gateway of last resort is not set', ''];
  };
  def('priv', 'show ip route', function () { this.say(this.routeHead().concat(this.routeEnts().map(function (e) { return e.line; })).join('\n')); }, 'IP routing table');
  def('priv', 'show ip route static', function () { this.say(this.routeHead().concat(this.routeEnts().filter(function (e) { return e.code === 'S'; }).map(function (e) { return e.line; })).join('\n')); }, 'Static routes only');
  def('priv', 'show ip route <ip>', function (a) {
    var d = ip2n(a[0]), best = null;
    this.routeEnts().forEach(function (e) { var m = e.len ? (0xFFFFFFFF << (32 - e.len)) >>> 0 : 0; if (((d & m) >>> 0) === e.nn && (!best || e.len > best.len)) best = e; });
    if (!best) { this.say('% Network not in table'); return; }
    var c = best.code !== 'S';
    this.say(['Routing entry for ' + n2ip(best.nn) + '/' + best.len, '  Known via "' + (c ? 'connected' : 'static') + '", distance ' + best.ad + ', metric 0' + (c ? ' (connected, via interface)' : ''), '  Routing Descriptor Blocks:', '  * ' + (best.nh ? best.nh + (best.oif ? ', via ' + best.oif : '') : 'directly connected, via ' + best.oif), '      Route metric is 0, traffic share count is 1'].join('\n'));
  }, 'The route used for one destination (longest match)');
  def('priv', 'show cdp neighbors', function () {
    if (!this.st.cdp) { this.say('% CDP is not enabled'); return; }
    var o = ['Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge', '                  S - Switch, H - Host, I - IGMP, r - Repeater, P - Phone', '', 'Device ID        Local Intrfce   Holdtme    Capability   Platform    Port ID'];
    var st = this.st;
    (this.cfg.cdp || []).forEach(function (r) { var li = st.ifs[r[1]]; if (li && (li.cdp === false || li.shut)) return; o.push((r[0] + '                 ').slice(0, 17) + (shortIf(r[1]) + '                ').slice(0, 16) + '150        ' + (r[2] + '            ').slice(0, 13) + (r[3] + '            ').slice(0, 12) + r[4]); });
    this.say(o.join('\n'));
  }, 'CDP neighbor entries');
  def('priv', 'show history', function () { this.say(this.hist.slice(-10).map(function (h) { return '  ' + h; }).join('\n')); }, 'Command history');
  def('user priv', 'traceroute <ip>', function () { this.say('Type escape sequence to abort.\nSimulator note: traceroute needs a full topology. Run tracert from a PC in Packet Tracer.'); }, 'Trace the path to a destination');
  def('user priv', 'ping <ip>', function (a) { this.say('Type escape sequence to abort.\nSimulator note: pings need a full topology. Test reachability in Packet Tracer.'); }, 'Send echo messages');
  def('priv', 'clear mac address-table dynamic', function () { }, 'Clear dynamic MAC entries');
  def('priv', 'show mac address-table', function () {
    var o = ['          Mac Address Table', '-------------------------------------------', '', 'Vlan    Mac Address       Type        Ports', '----    -----------       --------    -----'];
    (this.cfg.macs || []).forEach(function (r) { o.push(('   ' + r[0] + '    ').slice(0, 8) + r[1] + '    DYNAMIC     ' + r[2]); });
    this.say(o.join('\n'));
  }, 'MAC forwarding table');

  def(CFGS, 'end', function () { this.mode = 'priv'; this.ctx = null; this.say('%SYS-5-CONFIG_I: Configured from console by console'); }, 'Exit to privileged mode');
  def(CFGS, 'exit', function () { if (this.mode === 'config') { this.mode = 'priv'; this.say('%SYS-5-CONFIG_I: Configured from console by console'); } else { this.mode = 'config'; this.ctx = null; } }, 'Exit from this mode');
  def('config', 'hostname <w>', function (a) { this.st.host = a[0].slice(0, 63); }, 'Set the system name');
  def('config', 'enable secret <rest>', function (a) { this.st.ens = a[0].replace(/^0\s+/, ''); }, 'Hashed enable password');
  def('config', 'enable password <rest>', function (a) { if (this.st.ens && this.st.ens === a[0]) { this.say('The enable password you have chosen is the same as your enable secret.'); this.say('This is not recommended.  Re-enter the enable password.'); return; } this.st.enp = a[0]; }, 'Unprotected enable password');
  def('config', 'service password-encryption', function () { this.st.spe = true; }, 'Encrypt plain passwords (type 7)');
  def('config', 'no service password-encryption', function () { this.st.spe = false; }, '');
  def('config', 'no ip domain-lookup', function () { this.st.dl = false; }, 'Stop DNS lookups of typos');
  def('config', 'ip domain-lookup', function () { this.st.dl = true; }, '');
  def('config', 'ip domain-name <w>', function (a) { this.st.dom = a[0]; }, 'Default domain name');
  def('config', 'ip domain name <w>', function (a) { this.st.dom = a[0]; }, 'Default domain name');
  def('config', 'username <w> secret <rest>', function (a) { this.st.users[a[0]] = { s: a[1] }; }, 'Local user with hashed secret');
  def('config', 'username <w> privilege <n> secret <rest>', function (a) { this.st.users[a[0]] = { s: a[2], priv: a[1] }; }, '');
  def('config', 'username <w> password <rest>', function (a) { this.st.users[a[0]] = { p: a[1] }; }, 'Local user with a plain password');
  def('config', 'banner motd <rest>', function (a) {
    var d = a[0][0], t = a[0].slice(1), e2 = t.indexOf(d);
    if (e2 < 0) { this.say('Enter TEXT message.  End with the character \'' + d + '\'.'); this.st.banner = t; return; }
    this.st.banner = t.slice(0, e2);
  }, 'Message of the day banner');
  function keys(bits) {
    var st = this.st;
    if (/^(Switch|Router)$/.test(st.host)) { this.say('% Please define a hostname other than ' + st.host + '.'); return; }
    if (!st.dom) { this.say('% Please define a domain-name first.'); return; }
    var go = function (b, asked) {
      b = +b || 512; if (b < 360 || b > 4096) { this.say('% Invalid modulus size'); return; }
      if (!asked) this.say('The name for the keys will be: ' + st.host + '.' + st.dom); this.say('% The key modulus size is ' + b + ' bits');
      this.say('% Generating ' + b + ' bit RSA keys, keys will be non-exportable...[OK]'); this.say('%SSH-5-ENABLED: SSH 1.99 has been enabled'); st.keys = b;
    };
    if (bits) go.call(this, bits);
    else { this.say('The name for the keys will be: ' + st.host + '.' + st.dom); this.say('Choose the size of the key modulus in the range of 360 to 4096 for your\n  General Purpose Keys. Choosing a key modulus greater than 512 may take\n  a few minutes.'); this.ask('How many bits in the modulus [512]: ', function (v) { go.call(this, v, true); }); this.pending.cmd = 'crypto key generate rsa'; }
  }
  def('config', 'crypto key generate rsa', function () { keys.call(this, 0); }, 'Generate RSA keys');
  def('config', 'crypto key generate rsa modulus <n>', function (a) { keys.call(this, a[0]); }, '');
  def('config', 'crypto key generate rsa general-keys modulus <n>', function (a) { keys.call(this, a[0]); }, '');
  def('config', 'ip ssh version <n>', function (a) {
    if (a[0] !== 1 && a[0] !== 2) { this.say("% Invalid input detected at '^' marker."); return; }
    if (!this.st.keys) { this.say('Please create RSA keys to enable SSH (and of atleast 768 bits for SSH v2).'); return; }
    if (a[0] === 2 && this.st.keys < 768) { this.say('Please create RSA keys (of atleast 768 bits size) to enable SSH v2.'); return; }
    this.st.sshv = a[0];
  }, 'Set the SSH protocol version');
  def('config', 'ip default-gateway <ip>', function (a) { this.st.gw = a[0]; }, 'Gateway for a Layer 2 switch');
  def('config', 'ip route <ip> <ip> <rest>', function (a) {
    var t = a[2].trim().split(/\s+/), r = { net: a[0], mask: a[1], ad: 1 }, k = 0;
    if (ipOk(t[0])) { r.nh = t[0]; k = 1; }
    else { var m1 = /^([a-z-]+)([\d/.]+)$/i.exec(t[0]), nm = m1 ? ifName(m1[1], m1[2]) : null; if (!nm || !this.st.ifs[nm]) { this.say("% Invalid input detected at '^' marker."); return; } r.oif = nm; k = 1; if (ipOk(t[1] || '')) { r.nh = t[1]; k = 2; } }
    if (/^\d+$/.test(t[k] || '')) { r.ad = +t[k]; if (r.ad < 1 || r.ad > 255) { this.say("% Invalid input detected at '^' marker."); return; } k++; }
    if (k < t.length && !/^(name|permanent|tag)$/i.test(t[k])) { this.say("% Invalid input detected at '^' marker."); return; }
    if ((ip2n(a[0]) & ~ip2n(a[1])) >>> 0) { this.say('%Inconsistent address and mask'); return; }
    var txt = a[0] + ' ' + a[1] + ' ' + (r.oif ? r.oif + (r.nh ? ' ' + r.nh : '') : r.nh) + (r.ad !== 1 ? ' ' + r.ad : ''); r.txt = txt;
    this.st.routes = (this.st.routes || []).filter(function (x) { return !(x.net === r.net && x.mask === r.mask && (x.nh || '') === (r.nh || '') && (x.oif || '') === (r.oif || '')); }).concat([r]);
  }, 'Static route: prefix, mask, next hop or exit interface, optional distance');
  def('config', 'no ip route <ip> <ip> <rest>', function (a) { var b = a[2].trim().split(/\s+/)[0]; this.st.routes = (this.st.routes || []).filter(function (x) { return !(x.net === a[0] && x.mask === a[1] && (x.nh === b || shortIf(x.oif || '').toLowerCase() === shortIf(b).toLowerCase() || (x.oif || '').toLowerCase() === b.toLowerCase())); }); }, 'Remove a static route');
  def('config', 'no ip route <ip> <ip>', function (a) { this.st.routes = (this.st.routes || []).filter(function (x) { return !(x.net === a[0] && x.mask === a[1]); }); }, '');
  def('config', 'ip routing', function () { this.st.routing = true; }, 'Enable IP routing');
  def('config', 'no ip routing', function () { this.st.routing = false; }, '');
  def('config', 'cdp run', function () { this.st.cdp = true; }, 'Enable CDP');
  def('config', 'no cdp run', function () { this.st.cdp = false; }, 'Disable CDP');
  def('config', 'lldp run', function () { this.st.lldp = true; }, 'Enable LLDP');
  def('config', 'no lldp run', function () { this.st.lldp = false; }, '');
  def('config', 'vlan <n>', function (a) {
    if (!this.isSw()) { this.say("% Invalid input detected at '^' marker."); return; }
    if (a[0] < 1 || a[0] > 4094) { this.say('% Bad VLAN list'); return; }
    if (!this.st.vlans[a[0]]) this.st.vlans[a[0]] = 'VLAN' + ('000' + a[0]).slice(-4);
    this.mode = 'vlan'; this.ctx = [a[0]];
  }, 'Create or edit a VLAN');
  def('config', 'no vlan <n>', function (a) { if (a[0] === 1) this.say('Default VLAN 1 may not be deleted.'); else delete this.st.vlans[a[0]]; }, 'Delete a VLAN');
  def('vlan', 'name <w>', function (a) { this.st.vlans[this.ctx[0]] = a[0].slice(0, 32); }, 'VLAN name');
  def('config', 'interface <if>', function (a) {
    var n = a[0];
    if (!this.ensureIf(n)) { this.say("% Invalid input detected at '^' marker."); return; }
    this.ctx = [n]; this.mode = n.indexOf('.') > -1 ? 'subif' : 'if';
  }, 'Select an interface');
  def('config', 'interface range <rest>', function (a) {
    var st = this.st, list = [], bad = false;
    a[0].split(',').forEach(function (part) {
      var m = /^\s*([a-z-]+)\s*(\d+\/(?:\d+\/)?)(\d+)\s*(?:-\s*(\d+))?\s*$/i.exec(part);
      if (!m) { bad = true; return; }
      var from = +m[3], to = m[4] ? +m[4] : from;
      for (var k = from; k <= to; k++) { var nm = ifName(m[1], m[2] + k); if (nm && st.ifs[nm]) list.push(nm); else bad = true; }
    });
    if (bad || !list.length) { this.say("% Invalid input detected at '^' marker."); return; }
    this.ctx = list; this.mode = 'range';
  }, 'Select several interfaces');
  var IFM = 'if range subif';
  def(IFM, 'description <rest>', function (a) { this.each(function (i) { i.desc = a[0]; }); }, 'Interface description');
  def(IFM, 'no description', function () { this.each(function (i) { delete i.desc; }); }, '');
  def(IFM, 'shutdown', function () { this.each(function (i, n) { if (!i.shut) { var was = this.ifUp(n); i.shut = true; this.say('%LINK-5-CHANGED: Interface ' + n + ', changed state to administratively down'); if (was) this.say('%LINEPROTO-5-UPDOWN: Line protocol on Interface ' + n + ', changed state to down'); } }); }, 'Shut down the interface');
  def(IFM, 'no shutdown', function () {
    this.each(function (i, n) {
      if (!i.shut) return; i.shut = false;
      if (this.ifUp(n)) { this.say((/^Vlan/.test(n) ? '%LINK-5-CHANGED: Interface ' + n + ', changed state to up' : '%LINK-3-UPDOWN: Interface ' + n + ', changed state to up')); this.say('%LINEPROTO-5-UPDOWN: Line protocol on Interface ' + n + ', changed state to up'); }
      else if (/^Vlan/.test(n)) this.say('%LINK-5-CHANGED: Interface ' + n + ', changed state to up');
    });
  }, 'Bring the interface up');
  def(IFM, 'ip address <ip> <ip>', function (a) {
    var bad = false; this.each(function (i) { if (i.sp) bad = true; });
    if (bad) { this.say("% Invalid input detected at '^' marker.  (A Layer 2 switch port has no IP address. Use interface vlan 1.)"); return; }
    var len = maskLen(a[1]); if (n2ip(len ? (0xFFFFFFFF << (32 - len)) >>> 0 : 0) !== a[1]) { this.say('Bad mask 0x' + ip2n(a[1]).toString(16).toUpperCase() + ' for address ' + a[0]); return; }
    this.each(function (i) { i.ip = a[0]; i.mask = a[1]; });
  }, 'Set the IP address');
  def(IFM, 'no ip address', function () { this.each(function (i) { delete i.ip; delete i.mask; }); }, '');
  def('subif', 'encapsulation dot1q <n>', function (a) { this.each(function (i) { i.enc = a[0]; i.nat = false; }); }, '802.1Q VLAN for this subinterface');
  def('subif', 'encapsulation dot1q <n> native', function (a) { this.each(function (i) { i.enc = a[0]; i.nat = true; }); }, '');
  function spOnly(fn) { return function (a) { var bad = false; this.each(function (i) { if (!i.sp) bad = true; }); if (bad) { this.say("% Invalid input detected at '^' marker."); return; } fn.call(this, a); }; }
  def('if range', 'switchport mode access|trunk|dynamic', spOnly(function (a) {
    var m = a[0] === 'dynamic' ? 'dynamic auto' : a[0];
    this.each(function (i, n) { if (i.mode !== m && i.mode === 'trunk' && this.ifUp(n)) { this.say('%LINEPROTO-5-UPDOWN: Line protocol on Interface ' + n + ', changed state to down'); this.say('%LINEPROTO-5-UPDOWN: Line protocol on Interface ' + n + ', changed state to up'); } i.mode = m; if (m !== 'access' && m !== 'trunk') i.nonego = false; });
  }), 'Set trunking mode');
  def('if range', 'switchport mode dynamic auto|desirable', spOnly(function (a) { this.each(function (i) { i.mode = 'dynamic ' + a[0]; i.nonego = false; }); }), '');
  def('if range', 'switchport access vlan <n>', spOnly(function (a) {
    if (a[0] < 1 || a[0] > 4094) { this.say('% Bad VLAN list'); return; }
    if (!this.st.vlans[a[0]]) { this.say('% Access VLAN does not exist. Creating vlan ' + a[0]); this.st.vlans[a[0]] = 'VLAN' + ('000' + a[0]).slice(-4); }
    this.each(function (i) { i.av = a[0]; });
  }), 'Access mode VLAN');
  def('if range', 'switchport voice vlan <n>', spOnly(function (a) { if (!this.st.vlans[a[0]]) { this.say('% Voice VLAN does not exist. Creating vlan ' + a[0]); this.st.vlans[a[0]] = 'VLAN' + ('000' + a[0]).slice(-4); } this.each(function (i) { i.voice = a[0]; }); }), 'Voice VLAN for an IP phone');
  def('if range', 'switchport trunk native vlan <n>', spOnly(function (a) { this.each(function (i) { i.native = a[0]; }); }), 'Native (untagged) VLAN');
  def('if range', 'switchport trunk allowed vlan <rest>', spOnly(function (a) {
    var v = a[0].replace(/\s+/g, ''); if (!/^(add|remove)?[\d,-]+$/.test(v.replace(/^(add|remove)/, '')) && !/^(add|remove)[\d,-]+$/.test(v)) { if (!/^[\d,-]+$/.test(v)) { this.say('% Bad VLAN list'); return; } }
    this.each(function (i) { i.allowed = v; });
  }), 'VLANs allowed on the trunk');
  def('if range', 'switchport nonegotiate', spOnly(function () {
    var bad = false; this.each(function (i) { if (i.mode !== 'access' && i.mode !== 'trunk') bad = true; });
    if (bad) { this.say("Command rejected: Conflict between 'nonegotiate' and 'dynamic' status."); return; }
    this.each(function (i) { i.nonego = true; });
  }), 'Stop sending DTP frames');
  def(IFM, 'cdp enable', function () { this.each(function (i) { i.cdp = true; }); }, '');
  def(IFM, 'no cdp enable', function () { this.each(function (i) { i.cdp = false; }); }, 'Stop CDP on this port');
  def('config', 'line console <n>', function (a) { if (a[0] !== 0) { this.say("% Invalid input detected at '^' marker."); return; } this.ctx = ['con 0']; this.mode = 'line'; }, 'Console line');
  def('config', 'line vty <n> <n>', function (a) {
    var st = this.st, list = []; for (var v = a[0]; v <= a[1]; v++) { if (!st.lines['vty ' + v]) { this.say('%Invalid line range'); return; } list.push('vty ' + v); }
    this.ctx = list; this.mode = 'line';
  }, 'Virtual terminal lines (SSH and Telnet)');
  function eachLine(fn) { return function (a) { var st = this.st; this.cur().forEach(function (k) { fn(st.lines[k], a); }); }; }
  def('line', 'login', eachLine(function (l) { l.login = 'login'; }), 'Ask for the line password');
  def('line', 'login local', eachLine(function (l) { l.login = 'login local'; }), 'Use local usernames');
  def('line', 'no login', eachLine(function (l) { l.login = 'no login'; }), '');
  def('line', 'password <rest>', eachLine(function (l, a) { l.pw = a[0]; }), 'Line password');
  def('line', 'transport input <rest>', eachLine(function (l, a) { l.tin = a[0].toLowerCase().replace(/\s+/g, ' '); }), 'Allowed protocols: ssh, telnet, all, none');
  def('line', 'exec-timeout <n> <n>', eachLine(function (l, a) { l.to = a[0] + ' ' + a[1]; }), 'Idle logout timer (minutes seconds)');
  def('line', 'logging synchronous', function () { }, 'Stop log messages breaking your typing');
  def('line', 'access-class <w> in', eachLine(function (l, a) { l.ac = a[0]; }), 'Filter who may connect');

  /* ---------- routes: lowest AD per prefix is installed; next hop must be reachable (connected) ---------- */
  Sim.prototype.reach = function (nh) {
    var st = this.st, self = this, n = ip2n(nh);
    return st.order.some(function (x) { var i = st.ifs[x]; if (!i.ip || !self.ifUp(x)) return false; var m = ip2n(i.mask); return ((n & m) >>> 0) === ((ip2n(i.ip) & m) >>> 0); });
  };
  Sim.prototype.installed = function () {
    var self = this, best = {};
    (this.st.routes || []).forEach(function (r) {
      if (r.oif ? !self.ifUp(r.oif) : !self.reach(r.nh)) return;
      var k = r.net + '/' + r.mask; if (!best[k] || r.ad < best[k][0].ad) best[k] = [r]; else if (r.ad === best[k][0].ad) best[k].push(r);
    });
    var out = []; Object.keys(best).forEach(function (k) { out = out.concat(best[k]); });
    return out.sort(function (a, b) { return ip2n(a.net) - ip2n(b.net); });
  };
  /* ---------- extension commands: STP, EtherChannel, HSRP, IPv6, speed and duplex ---------- */
  function ix(key, text) { return function (a) { var t = typeof text === 'function' ? text(a) : text; this.each(function (i) { i.x = i.x || {}; if (t === null) delete i.x[key]; else i.x[key] = t; }); }; }
  function gx(key, text) { return function (a) { var t = typeof text === 'function' ? text(a) : text, k = typeof key === 'function' ? key(a) : key; if (t === null) delete this.st.gx[k]; else this.st.gx[k] = t; }; }
  def('config', 'spanning-tree mode pvst|rapid-pvst|mst', gx('stpm', function (a) { return 'spanning-tree mode ' + a[0]; }), 'STP mode (rapid-pvst is 802.1w per VLAN)');
  def('config', 'spanning-tree vlan <w> priority <n>', function (a) {
    if (a[1] % 4096 || a[1] > 61440) { this.say('% Bridge Priority must be in increments of 4096.'); this.say('% Allowed values are:'); this.say('  0     4096  8192  12288 16384 20480 24576 28672'); this.say('  32768 36864 40960 45056 49152 53248 57344 61440'); return; }
    this.st.gx['stpv' + a[0]] = 'spanning-tree vlan ' + a[0] + ' priority ' + a[1];
  }, 'Bridge priority for these VLANs (multiples of 4096, lower wins)');
  def('config', 'spanning-tree vlan <w> root primary|secondary', function (a) { this.st.gx['stpv' + a[0]] = 'spanning-tree vlan ' + a[0] + ' priority ' + (a[1] === 'primary' ? 24576 : 28672); }, 'Macro that lowers the priority so this switch becomes root');
  def('config', 'spanning-tree portfast default', gx('pfd', 'spanning-tree portfast default'), 'PortFast on every access port');
  def('config', 'spanning-tree portfast bpduguard default', gx('bgd', 'spanning-tree portfast bpduguard default'), 'BPDU Guard on every PortFast port');
  def('if range', 'spanning-tree portfast', spOnly(function () {
    ix('pf', 'spanning-tree portfast').call(this);
    this.say('%Warning: portfast should only be enabled on ports connected to a single'); this.say(' host. Connecting hubs, concentrators, switches, bridges, etc... to this'); this.say(' interface  when portfast is enabled, can cause temporary bridging loops.'); this.say(' Use with CAUTION');
  }), 'Skip listening and learning on a host port');
  def('if range', 'no spanning-tree portfast', ix('pf', null), '');
  def('if range', 'spanning-tree bpduguard enable', spOnly(ix('bg', 'spanning-tree bpduguard enable')), 'Err-disable the port if a BPDU arrives');
  def('if range', 'spanning-tree bpduguard disable', spOnly(ix('bg', 'spanning-tree bpduguard disable')), '');
  def('if range', 'spanning-tree guard root', spOnly(ix('gr', 'spanning-tree guard root')), 'Block the port if it hears a better root');
  def('if range', 'spanning-tree vlan <w> port-priority <n>', spOnly(ix('pp', function (a) { return 'spanning-tree vlan ' + a[0] + ' port-priority ' + a[1]; })), 'Port priority (multiples of 16)');
  def('if range', 'channel-group <n> mode active|passive|on|desirable|auto', spOnly(function (a) {
    var po = 'Port-channel' + a[0], st = this.st;
    if (!st.ifs[po]) { this.say('Creating a port-channel interface Port-channel ' + a[0]); var f0 = null; this.each(function (i) { if (!f0) f0 = i; }); st.ifs[po] = { shut: false, sp: true, mode: f0.mode || 'dynamic auto', av: f0.av || 1, native: f0.native, allowed: f0.allowed, nonego: f0.nonego, cdp: true, po: true }; st.order.push(po); }
    this.each(function (i) { i.x = i.x || {}; i.x.cg = 'channel-group ' + a[0] + ' mode ' + a[1]; i.cg = { n: a[0], m: a[1] }; });
  }), 'Bundle this port into an EtherChannel');
  def('if range', 'no channel-group', function () { this.each(function (i) { if (i.x) delete i.x.cg; delete i.cg; }); }, '');
  def('priv', 'show etherchannel summary', function () {
    var st = this.st, self = this, groups = {};
    st.order.forEach(function (n) { var i = st.ifs[n]; if (i.cg) (groups[i.cg.n] = groups[i.cg.n] || []).push([n, i]); });
    var o = ['Flags:  D - down        P - in port-channel', '        I - stand-alone s - suspended', '        S - Layer2      U - in use', '', 'Number of channel-groups in use: ' + Object.keys(groups).length, 'Number of aggregators:           ' + Object.keys(groups).length, '', 'Group  Port-channel  Protocol    Ports', '------+-------------+-----------+----------------------------------------------'];
    Object.keys(groups).forEach(function (g) {
      var m = groups[g][0][1].cg.m, pr = m === 'active' || m === 'passive' ? 'LACP' : m === 'on' ? '-' : 'PAgP';
      var ports = groups[g].map(function (x) { return shortIf(x[0]) + '(' + (self.ifUp(x[0]) ? 'P' : 'D') + ')'; }).join(' ');
      var any = groups[g].some(function (x) { return self.ifUp(x[0]); });
      o.push((g + '      ').slice(0, 7) + ('Po' + g + '(S' + (any ? 'U' : 'D') + ')            ').slice(0, 14) + (pr + '            ').slice(0, 12) + ports);
    });
    this.say(o.join('\n'));
  }, 'EtherChannel bundles and member ports');
  function vlist(t) { var r = []; String(t).split(',').forEach(function (p) { var m = p.split('-'); for (var v = +m[0]; v <= +(m[1] || m[0]); v++) r.push(v); }); return r; }
  Sim.prototype.stpPri = function (v) { var p = 32768, gx = this.st.gx; Object.keys(gx).forEach(function (k) { if (k.indexOf('stpv') === 0 && vlist(k.slice(4)).indexOf(v) > -1) p = +gx[k].split(' ').pop(); }); return p; };
  Sim.prototype.stpShow = function (v) {
    var st = this.st, self = this, sc = this.cfg.stp || {}, oth = sc.other || { pri: 32768, mac: '0001.4200.0a01' }, mymac = sc.mac || '0001.6401.1a01';
    var ports = st.order.filter(function (n) { var i = st.ifs[n]; if (!i.sp || i.cg || /^Vlan/.test(n) || !self.ifUp(n)) return false; return i.mode === 'trunk' ? (!i.allowed || vlist(i.allowed).indexOf(v) > -1) : (i.av || 1) === v; });
    if (!st.vlans[v] || !ports.length) return null;
    var mine = this.stpPri(v) + v, op = ((sc.otherv || {})[v] || oth.pri) + v, root = mine < op || (mine === op && mymac < oth.mac);
    var cost = function (n) { return /^Port-channel/.test(n) ? 3 : /^Gig/.test(n) ? 4 : 19; };
    var rp = sc.rp && st.ifs[sc.rp] && st.ifs[sc.rp].cg ? 'Port-channel' + st.ifs[sc.rp].cg.n : sc.rp;
    if (rp && ports.indexOf(rp) < 0) rp = null;
    var rapid = (st.gx.stpm || '').indexOf('rapid') > -1, hd = '  Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec';
    var o = ['VLAN' + ('000' + v).slice(-4), '  Spanning tree enabled protocol ' + (rapid ? 'rstp' : 'ieee'), '  Root ID    Priority    ' + (root ? mine : op), '             Address     ' + (root ? mymac : oth.mac)];
    if (root) o.push('             This bridge is the root'); else if (rp) o.push('             Cost        ' + cost(rp), '             Port        ' + (st.order.indexOf(rp) + 1) + ' (' + rp + ')');
    o.push('           ' + hd, '', '  Bridge ID  Priority    ' + mine + '  (priority ' + (mine - v) + ' sys-id-ext ' + v + ')', '             Address     ' + mymac, '           ' + hd, '             Aging Time  300 sec', '', 'Interface           Role Sts Cost      Prio.Nbr Type', '------------------- ---- --- --------- -------- --------------------------------');
    ports.forEach(function (n) {
      var i = st.ifs[n], alt = !root && (sc.alt || []).indexOf(n) > -1, role = !root && n === rp ? 'Root' : alt ? 'Altn' : 'Desg', edge = i.x && i.x.pf || (st.gx.pfd && i.mode === 'access');
      o.push((shortIf(n) + '                    ').slice(0, 20) + role + ' ' + (alt ? 'BLK' : 'FWD') + ' ' + (cost(n) + '          ').slice(0, 10) + ('128.' + (st.order.indexOf(n) + 1) + '         ').slice(0, 9) + 'P2p' + (edge ? ' Edge' : ''));
    });
    return o.join('\n');
  };
  def('priv', 'show spanning-tree', function () { var self = this, out = Object.keys(this.st.vlans).map(Number).sort(function (a, b) { return a - b; }).map(function (v) { return self.stpShow(v); }).filter(Boolean); this.say(out.join('\n\n') || 'No spanning tree instances exist.'); }, 'Spanning tree for every VLAN');
  def('priv', 'show spanning-tree vlan <n>', function (a) { var r = this.stpShow(+a[0]); this.say(r || 'Spanning tree instance(s) for vlan ' + a[0] + ' does not exist.'); }, 'Spanning tree for one VLAN');
  def('if subif', 'standby version 2', ix('sv', 'standby version 2'), 'HSRP version 2');
  def('if subif', 'standby <n> ip <ip>', function (a) { ix('s' + a[0] + 'ip', 'standby ' + a[0] + ' ip ' + a[1]).call(this); this.each(function (i) { i.hsrp = i.hsrp || {}; i.hsrp[a[0]] = Object.assign(i.hsrp[a[0]] || { pri: 100 }, { vip: a[1] }); }); }, 'HSRP virtual IP (the hosts\' gateway)');
  def('if subif', 'standby <n> priority <n>', function (a) { ix('s' + a[0] + 'pri', 'standby ' + a[0] + ' priority ' + a[1]).call(this); this.each(function (i) { i.hsrp = i.hsrp || {}; i.hsrp[a[0]] = Object.assign(i.hsrp[a[0]] || {}, { pri: a[1] }); }); }, 'HSRP priority (higher wins, default 100)');
  def('if subif', 'standby <n> preempt', function (a) { ix('s' + a[0] + 'pre', 'standby ' + a[0] + ' preempt').call(this); this.each(function (i) { i.hsrp = i.hsrp || {}; i.hsrp[a[0]] = Object.assign(i.hsrp[a[0]] || { pri: 100 }, { pre: true }); }); }, 'Take over as active when your priority is higher');
  def('priv', 'show standby brief', function () {
    var st = this.st, self = this, o = ['                     P indicates configured to preempt.', '                     |', 'Interface   Grp  Pri P State   Active          Standby         Virtual IP'];
    st.order.forEach(function (n) { var i = st.ifs[n]; Object.keys(i.hsrp || {}).forEach(function (g) { var h = i.hsrp[g], up = self.ifUp(n) && h.vip; o.push((shortIf(n) + '            ').slice(0, 12) + (g + '    ').slice(0, 5) + (String(h.pri || 100) + '    ').slice(0, 4) + (h.pre ? 'P ' : '  ') + ((up ? 'Active' : 'Init') + '        ').slice(0, 8) + ((up ? 'local' : 'unknown') + '                ').slice(0, 16) + ((up ? (self.cfg.peer || 'unknown') : 'unknown') + '                ').slice(0, 16) + (h.vip || 'unknown')); }); });
    this.say(o.join('\n'));
  }, 'HSRP groups on this device');
  def('config', 'ipv6 unicast-routing', gx('v6r', 'ipv6 unicast-routing'), 'Turn on IPv6 routing');
  def('if subif', 'ipv6 address <rest>', function (a) { var v = a[0].trim(); if (!/^[0-9a-f:]+(\/\d{1,3})?( link-local| eui-64)?$/i.test(v)) { this.say("% Invalid input detected at '^' marker."); return; } ix('v6' + v.split(/\s/)[0], 'ipv6 address ' + v.toUpperCase().replace(' LINK-LOCAL', ' link-local').replace(' EUI-64', ' eui-64')).call(this); }, 'IPv6 address with prefix length');
  def('if subif', 'ipv6 enable', ix('v6en', 'ipv6 enable'), 'Link-local address only');
  def('config', 'ipv6 route <rest>', function (a) { var v = a[0].trim(); if (!/^[0-9a-f:]+\/\d{1,3}\s+\S+/i.test(v)) { this.say("% Invalid input detected at '^' marker."); return; } this.st.v6r = (this.st.v6r || []).filter(function (x) { return x !== v.toUpperCase(); }).concat([v.toUpperCase()]); }, 'IPv6 static route: prefix/len next hop or exit interface');
  def('if', 'speed 10|100|1000|auto', ix('spd', function (a) { return a[0] === 'auto' ? null : 'speed ' + a[0]; }), 'Port speed');
  def('if', 'duplex auto|full|half', ix('dup', function (a) { return a[0] === 'auto' ? null : 'duplex ' + a[0]; }), 'Duplex');
  def('user priv', 'show interfaces <if>', function (a) {
    var n = a[0], i = this.st.ifs[n]; if (!i) { this.say("% Invalid input detected at '^' marker."); return; }
    var up = this.ifUp(n), e = (this.cfg.errs || {})[n] || {}, gi = /^Gig/.test(n), x = i.x || {};
    var dup = x.dup ? x.dup.split(' ')[1] : 'full', spd = x.spd ? x.spd.split(' ')[1] : gi ? '1000' : '100';
    var o = [n + ' is ' + (i.shut ? 'administratively down' : up ? 'up' : 'down') + ', line protocol is ' + (up ? 'up' : 'down') + (up ? ' (connected)' : ' (notconnect)'),
      '  Hardware is ' + (gi ? 'Gigabit Ethernet' : 'Fast Ethernet') + ', address is 0001.64' + ('0' + (this.st.order.indexOf(n) + 16).toString(16)).slice(-2) + '.ab' + ('0' + (this.st.order.indexOf(n) + 1)).slice(-2)];
    if (i.desc) o.push('  Description: ' + i.desc);
    if (i.ip) o.push('  Internet address is ' + i.ip + '/' + maskLen(i.mask));
    o.push('  MTU 1500 bytes, BW ' + (+spd * 1000) + ' Kbit/sec, DLY ' + (gi ? 10 : 100) + ' usec,', '  Encapsulation ARPA, loopback not set', '  ' + (dup === 'half' ? 'Half' : 'Full') + '-duplex, ' + spd + 'Mb/s', '  Last input 00:00:0' + (up ? 1 : 0) + ', output 00:00:01, output hang never',
      '     ' + (e.inp || (up ? 1873 : 0)) + ' packets input, ' + ((e.inp || (up ? 1873 : 0)) * 82) + ' bytes, 0 no buffer', '     ' + (e.crc || 0) + ' input errors, ' + (e.crc || 0) + ' CRC, 0 frame, 0 overrun, 0 ignored, 0 abort',
      '     ' + (e.outp || (up ? 1620 : 0)) + ' packets output, ' + ((e.outp || (up ? 1620 : 0)) * 90) + ' bytes, 0 underruns', '     0 output errors, ' + (e.col || 0) + ' collisions, ' + (e.resets || 1) + ' interface resets', '     ' + (e.late || 0) + ' late collision, 0 deferred');
    this.say(o.join('\n'));
  }, 'Status and counters for one interface');

  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('.lx-ios'), function (t) {
      var c = {}; try { c = JSON.parse(t.querySelector('.lx-ios-cfg').textContent); } catch (e) { c = {}; }
      t.sim = new Sim(t, c);
    });
    Array.prototype.forEach.call(document.querySelectorAll('.lx-t7'), function (w) {
      var inp = w.querySelector('input'), out = w.querySelector('output'), b = w.querySelector('button');
      function go() { var v = inp.value.trim().replace(/^7\s+/, ''); out.textContent = /^\d\d([0-9A-Fa-f]{2})+$/.test(v) ? unType7(v.toUpperCase()) : T('lx.t7.bad', 'Paste a type 7 string such as 0822455D0A16'); }
      b.addEventListener('click', go); inp.addEventListener('keydown', function (e) { if (e.key === 'Enter') go(); });
    });
  }
  window.CWMIos = { type7: type7, unType7: unType7 };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
