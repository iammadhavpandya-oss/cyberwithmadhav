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
    var m = { user: '>', priv: '#', config: '(config)#', 'if': '(config-if)#', range: '(config-if-range)#', subif: '(config-subif)#', line: '(config-line)#', vlan: '(config-vlan)#', router: '(config-router)#', sacl: '(config-std-nacl)#', eacl: '(config-ext-nacl)#', dhcp: '(dhcp-config)#' }[this.mode];
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
      if (this.st.ospf && this.ospfTick) this.ospfTick();
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
    this.buf.forEach(function (l) { this.print(l, /^%(LINK|LINEPROTO|SYS|SSH)/.test(l) || (/^%OSPF/.test(l) && !/to DOWN/.test(l)) ? 'ok' : (/^% ?\S/.test(l) && !/^% (Access VLAN|Voice VLAN|The key|Generating)/.test(l)) || /^(Command rejected|Please create|\s+\^$)/.test(l) ? 'er' : ''); }, this);
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
    var i = this.st.ifs[n]; if (!i || i.shut || i.errd) return false;
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
    o = o.concat(this.runHook(0));
    var me = this;
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
      } else if (i.dhcp) o.push(' ip address dhcp');
      else if (i.ip) o.push(' ip address ' + i.ip + ' ' + i.mask);
      else if (!i.sp) o.push(' no ip address');
      Object.keys(i.x || {}).forEach(function (k) { o.push(' ' + i.x[k]); });
      if (!i.cdp && i.cdp !== undefined) o.push(' no cdp enable');
      if (i.ps && i.ps.sticky && !i.errd) me.psMacs(n).slice(0, i.ps.max || 1).forEach(function (m) { o.push(' switchport port-security mac-address sticky ' + m[1]); });
      if (i.shut) o.push(' shutdown');
      o.push('!');
    });
    o = o.concat(this.runHook(1));
    if (st.gw) o.push('ip default-gateway ' + st.gw, '!');
    (st.routes || []).forEach(function (r) { o.push('ip route ' + r.txt); });
    (st.v6r || []).forEach(function (r) { o.push('ipv6 route ' + r); });
    o = o.concat(this.runHook(2));
    if (st.banner) o.push('banner motd ^C' + st.banner + '^C', '!');
    var ln = function (k) { var x = st.lines[k], r = []; if (x.ac) r.push(' access-class ' + x.ac + ' in'); if (x.to) r.push(' exec-timeout ' + x.to); if (x.pw) r.push(' password ' + (st.spe ? '7 ' + type7(x.pw, 9) : x.pw)); if (x.la) r.push(' login authentication ' + x.la); if (x.login) r.push(' ' + x.login); if (x.tin) r.push(' transport input ' + x.tin); return r; };
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
  var CFGS = 'config if range subif line vlan router sacl eacl dhcp';
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
      var s = i.errd ? 'err-disabled' : i.shut ? 'disabled' : self.ifUp(n) ? 'connected' : 'notconnect';
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
      ent.push({ nn: nn, len: len, k: 0, code: 'C', ad: 0, oif: n, line: 'C        ' + n2ip(nn) + '/' + len + ' is directly connected, ' + n }); if (len < 32) ent.push({ nn: ip2n(i.ip), len: 32, k: 1, code: 'L', ad: 0, oif: n, line: 'L        ' + i.ip + '/32 is directly connected, ' + n });
    });
    if (this.ospfEnts) ent = ent.concat(this.ospfEnts());
    this.installed().forEach(function (r) { ent.push({ nn: ip2n(r.net), len: maskLen(r.mask), k: 2, code: 'S', ad: r.ad, nh: r.nh, oif: r.oif, line: (r.net === '0.0.0.0' ? 'S*       ' : 'S        ') + r.net + '/' + maskLen(r.mask) + (r.nh ? ' [' + r.ad + '/0] via ' + r.nh + (r.oif ? ', ' + r.oif : '') : ' is directly connected, ' + r.oif) }); });
    return ent.sort(function (a, b) { return a.nn - b.nn || a.len - b.len || a.k - b.k; });
  };
  Sim.prototype.routeHead = function () {
    var df = this.installed().filter(function (r) { return r.net === '0.0.0.0' && r.mask === '0.0.0.0'; })[0];
    var od = !df && this.ospfEnts ? this.ospfEnts().filter(function (e) { return e.dflt; })[0] : null; if (od) df = { nh: od.nh };
    return ['Codes: L - local, C - connected, S - static, O - OSPF', '       E2 - OSPF external type 2, * - candidate default', '', df ? 'Gateway of last resort is ' + (df.nh || '0.0.0.0') + ' to network 0.0.0.0' : 'Gateway of last resort is not set', ''];
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
      if (!i.shut) return; i.shut = false; i.errd = false;
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

  /* ---------- batch 2: OSPF, ACLs, DHCP, NAT, NTP, syslog, SNMP, port security, snooping, AAA, PoE ---------- */
  var BLK = 'router sacl eacl dhcp';
  function gp(slot, key, text) { return function (a) { var t = typeof text === 'function' ? text(a) : text, k = typeof key === 'function' ? key(a) : key, st = this.st; st[slot] = st[slot] || {}; if (t === null) delete st[slot][k]; else st[slot][k] = t; }; }
  function os(i) { i.os = i.os || {}; return i.os; }
  function fmtDate(d) { var M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], h = d.getHours(), ap = h < 12 ? 'AM' : 'PM'; h = h % 12 || 12; return M[d.getMonth()] + ' ' + ('0' + d.getDate()).slice(-2) + ' ' + d.getFullYear() + ' ' + ('0' + h).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2) + ' ' + ap; }
  function pad(s, n) { s = String(s); while (s.length < n) s += ' '; return s; }

  /* ACL text parsing (normalised the way IOS stores it) */
  function aclAddr(t, i) {
    if (t[i] === 'any') return { n: 1, s: 'any' };
    if (t[i] === 'host' && ipOk(t[i + 1] || '')) return { n: 2, s: 'host ' + t[i + 1] };
    if (ipOk(t[i] || '') && ipOk(t[i + 1] || '')) { var w = ip2n(t[i + 1]), a = n2ip((ip2n(t[i]) & ~w) >>> 0); return { n: 2, s: w === 0 ? 'host ' + a : a + ' ' + t[i + 1] }; }
    return null;
  }
  function aclPort(t, i) {
    if (['eq', 'neq', 'gt', 'lt', 'range'].indexOf(t[i]) < 0) return 0;
    var ok = function (x) { return (/^\d+$/.test(x || '') && +x < 65536) || /^(www|domain|ftp|ftp-data|telnet|smtp|pop3|ntp|snmp|snmptrap|tftp|bootps|bootpc|syslog|tacacs|isakmp|22|443)$/.test(x || ''); };
    if (!ok(t[i + 1])) return -1; if (t[i] === 'range') return ok(t[i + 2]) ? 3 : -1; return 2;
  }
  function aclParse(type, rest) {
    var t = rest.toLowerCase().trim().split(/\s+/), act = t[0], i = 1, out = [act];
    if (act !== 'permit' && act !== 'deny') return null;
    if (type === 'standard') {
      var a = ipOk(t[1] || '') && !ipOk(t[2] || '') ? { n: 1, s: 'host ' + t[1] } : aclAddr(t, 1);
      if (!a) return null; out.push(a.s); i += a.n;
    } else {
      var pr = t[1]; if (!/^(ip|tcp|udp|icmp|ospf|esp|gre)$/.test(pr || '')) return null; out.push(pr); i = 2;
      var s = aclAddr(t, i); if (!s) return null; out.push(s.s); i += s.n;
      var sp = aclPort(t, i); if (sp < 0 || (sp && !/^(tcp|udp)$/.test(pr))) return null; if (sp) { out = out.concat(t.slice(i, i + sp)); i += sp; }
      var d = aclAddr(t, i); if (!d) return null; out.push(d.s); i += d.n;
      var dp = aclPort(t, i); if (dp < 0 || (dp && !/^(tcp|udp)$/.test(pr))) return null; if (dp) { out = out.concat(t.slice(i, i + dp)); i += dp; }
      if (pr === 'icmp' && /^(echo|echo-reply|unreachable|time-exceeded|ttl-exceeded)$/.test(t[i] || '')) { out.push(t[i]); i++; }
      if (t[i] === 'established' && pr === 'tcp') { out.push(t[i]); i++; }
    }
    if (t[i] === 'log') { out.push('log'); i++; }
    return i === t.length ? out.join(' ') : null;
  }
  Sim.prototype.aclGet = function (name, type, named) {
    var st = this.st; st.acls = st.acls || {}; st.aclOrder = st.aclOrder || [];
    if (!st.acls[name]) { st.acls[name] = { type: type, named: named, ents: [] }; st.aclOrder.push(name); }
    return st.acls[name];
  };
  Sim.prototype.aclAdd = function (A, seq, raw) {
    var txt = /^remark /.test(raw) ? raw : aclParse(A.type, raw);
    if (!txt) { this.say("% Invalid input detected at '^' marker."); return; }
    if (seq == null) seq = (A.ents.length ? A.ents[A.ents.length - 1].seq : 0) + 10;
    if (A.ents.some(function (e) { return e.seq === seq; })) { this.say('% Duplicate sequence number'); return; }
    A.ents.push({ seq: seq, txt: txt }); A.ents.sort(function (x, y) { return x.seq - y.seq; });
  };
  function numType(n) { return (n >= 1 && n <= 99) || (n >= 1300 && n <= 1999) ? 'standard' : (n >= 100 && n <= 199) || (n >= 2000 && n <= 2699) ? 'extended' : null; }
  def('config', 'access-list <n> permit|deny <rest>', function (a) { var ty = numType(a[0]); if (!ty) { this.say("% Invalid input detected at '^' marker."); return; } this.aclAdd(this.aclGet(String(a[0]), ty, false), null, a[1] + ' ' + a[2]); }, 'Numbered ACL entry (1-99 standard, 100-199 extended)');
  def('config', 'access-list <n> remark <rest>', function (a) { var ty = numType(a[0]); if (ty) this.aclAdd(this.aclGet(String(a[0]), ty, false), null, 'remark ' + a[1]); }, 'ACL comment');
  def('config', 'no access-list <n>', function (a) { var st = this.st, k = String(a[0]); if (st.acls && st.acls[k]) { delete st.acls[k]; st.aclOrder.splice(st.aclOrder.indexOf(k), 1); } }, '');
  def('config', 'ip access-list standard|extended <w>', function (a) { var A = this.aclGet(a[1], a[0], true); if (A.type !== a[0]) { this.say('% A ' + A.type + ' access list with this name already exists'); return; } this.mode = a[0] === 'standard' ? 'sacl' : 'eacl'; this.ctx = [a[1]]; }, 'Named access list');
  def('config', 'no ip access-list standard|extended <w>', function (a) { var st = this.st; if (st.acls && st.acls[a[1]]) { delete st.acls[a[1]]; st.aclOrder.splice(st.aclOrder.indexOf(a[1]), 1); } }, '');
  def('sacl eacl', 'permit|deny <rest>', function (a) { this.aclAdd(this.st.acls[this.ctx[0]], null, a[0] + ' ' + a[1]); }, 'Add an entry at the end');
  def('sacl eacl', '<n> permit|deny <rest>', function (a) { this.aclAdd(this.st.acls[this.ctx[0]], a[0], a[1] + ' ' + a[2]); }, 'Add an entry with this sequence number');
  def('sacl eacl', 'remark <rest>', function (a) { this.aclAdd(this.st.acls[this.ctx[0]], null, 'remark ' + a[0]); }, 'Comment');
  def('sacl eacl', 'no <n>', function (a) { var A = this.st.acls[this.ctx[0]]; A.ents = A.ents.filter(function (e) { return e.seq !== a[0]; }); }, 'Delete one entry by sequence number');
  def(IFM, 'ip access-group <w> in|out', function (a) { ix('acg' + a[1], 'ip access-group ' + a[0] + ' ' + a[1]).call(this); this.each(function (i) { i.acg = i.acg || {}; i.acg[a[1]] = a[0]; }); }, 'Filter traffic on this interface');
  def(IFM, 'no ip access-group <w> in|out', function (a) { ix('acg' + a[1], null).call(this); this.each(function (i) { if (i.acg) delete i.acg[a[1]]; }); }, '');
  def('priv', 'show access-lists', function () { this.showAcl(null); }, 'All access lists with match counters');
  def('priv', 'show access-lists <w>', function (a) { this.showAcl(a[0]); }, 'One access list');
  def('priv', 'show ip access-lists', function () { this.showAcl(null); }, 'IPv4 access lists');
  Sim.prototype.showAcl = function (only) {
    var st = this.st, hits = this.cfg.hits || {}, o = [];
    (st.aclOrder || []).forEach(function (k) {
      if (only && only !== k) return; var A = st.acls[k];
      o.push((A.type === 'standard' ? 'Standard' : 'Extended') + ' IP access list ' + k);
      A.ents.forEach(function (e) { if (/^remark /.test(e.txt)) return; var h = (hits[k] || {})[e.seq]; o.push('    ' + e.seq + ' ' + e.txt + (h ? ' (' + h + ' match' + (h > 1 ? 'es' : '') + ')' : '')); });
    });
    this.say(o.join('\n'));
  };
  def('priv', 'show ip interface <if>', function (a) {
    var n = a[0], i = this.st.ifs[n]; if (!i) { this.say("% Invalid input detected at '^' marker."); return; }
    var up = this.ifUp(n), g = i.acg || {};
    this.say([n + ' is ' + (i.shut ? 'administratively down' : up ? 'up' : 'down') + ', line protocol is ' + (up ? 'up' : 'down'), i.ip ? '  Internet address is ' + i.ip + '/' + maskLen(i.mask) : '  Internet protocol processing disabled', '  Broadcast address is 255.255.255.255', '  MTU is 1500 bytes',
      (i.x && i.x.helper ? '  Helper address is ' + i.x.helper.split(' ').pop() : '  Helper address is not set'), '  Outgoing access list is ' + (g.out || 'not set'), '  Inbound  access list is ' + (g['in'] || 'not set'), '  Proxy ARP is enabled'].join('\n'));
  }, 'IP settings of one interface, including ACLs');

  /* OSPF */
  def('config', 'router ospf <n>', function (a) { var st = this.st; if (st.ospf && st.ospf.pid !== a[0]) { this.say('% This simulator runs one OSPF process; use router ospf ' + st.ospf.pid); return; } st.ospf = st.ospf || { pid: a[0], nets: [], pas: {}, npas: {}, ref: 0, dio: false, rid: '', ridAct: '' }; this.mode = 'router'; this.ctx = []; }, 'OSPF routing process (the number is local only)');
  def('config', 'no router ospf <n>', function () { this.st.ospf = null; }, '');
  def('router', 'router-id <ip>', function (a) { var o = this.st.ospf; o.rid = a[0]; if (this.ospfNbrs().length && o.ridAct !== a[0]) this.say('% OSPF: Reload or use "clear ip ospf process" command, for this to take effect'); else o.ridAct = a[0]; }, 'Fixed router ID');
  def('router', 'network <ip> <ip> area <n>', function (a) { var o = this.st.ospf; if (!o.nets.some(function (x) { return x.ip === a[0] && x.w === a[1]; })) o.nets.push({ ip: n2ip((ip2n(a[0]) & ~ip2n(a[1])) >>> 0), w: a[1], area: a[2] }); }, 'Run OSPF on interfaces in this range (wildcard mask)');
  def('router', 'no network <ip> <ip> area <n>', function (a) { var o = this.st.ospf; o.nets = o.nets.filter(function (x) { return !(x.ip === n2ip((ip2n(a[0]) & ~ip2n(a[1])) >>> 0) && x.w === a[1]); }); }, '');
  def('router', 'passive-interface <if>', function (a) { if (!this.st.ifs[a[0]]) { this.say("% Invalid input detected at '^' marker."); return; } this.st.ospf.pas[a[0]] = true; delete this.st.ospf.npas[a[0]]; }, 'Advertise the subnet but send no hellos');
  def('router', 'no passive-interface <if>', function (a) { delete this.st.ospf.pas[a[0]]; this.st.ospf.npas[a[0]] = true; }, '');
  def('router', 'passive-interface default', function () { this.st.ospf.pasDef = true; this.st.ospf.npas = {}; }, 'Make every interface passive');
  def('router', 'auto-cost reference-bandwidth <n>', function (a) { this.st.ospf.ref = a[0] === 100 ? 0 : a[0]; this.say('% OSPF: Reference bandwidth is changed.'); this.say('        Please ensure reference bandwidth is consistent across all routers.'); }, 'Reference bandwidth in Mb/s (default 100)');
  def('router', 'default-information originate', function () { this.st.ospf.dio = true; }, 'Advertise this router\'s default route');
  def('router', 'no default-information originate', function () { this.st.ospf.dio = false; }, '');
  def(IFM, 'ip ospf priority <n>', function (a) { if (a[0] > 255) { this.say("% Invalid input detected at '^' marker."); return; } ix('opri', 'ip ospf priority ' + a[0]).call(this); this.each(function (i) { os(i).pri = a[0]; }); }, 'DR election priority (0 to 255, default 1)');
  def(IFM, 'ip ospf cost <n>', function (a) { ix('ocost', 'ip ospf cost ' + a[0]).call(this); this.each(function (i) { os(i).cost = a[0]; }); }, 'Fixed OSPF cost');
  def(IFM, 'ip ospf hello-interval <n>', function (a) { ix('ohel', 'ip ospf hello-interval ' + a[0]).call(this); this.each(function (i) { os(i).hello = a[0]; }); }, 'Seconds between hellos (default 10)');
  def(IFM, 'no ip ospf priority', function () { ix('opri', null).call(this); this.each(function (i) { delete os(i).pri; }); }, '');
  def(IFM, 'no ip ospf cost', function () { ix('ocost', null).call(this); this.each(function (i) { delete os(i).cost; }); }, '');
  def(IFM, 'no ip ospf hello-interval', function () { ix('ohel', null).call(this); this.each(function (i) { delete os(i).hello; }); }, '');
  def(IFM, 'ip ospf dead-interval <n>', function (a) { ix('odead', 'ip ospf dead-interval ' + a[0]).call(this); this.each(function (i) { os(i).dead = a[0]; }); }, 'Seconds before a silent neighbour is dead');
  def(IFM, 'no ip ospf dead-interval', function () { ix('odead', null).call(this); this.each(function (i) { delete os(i).dead; }); }, '');
  def(IFM, 'ip ospf network point-to-point|broadcast', function (a) { ix('onet', a[0] === 'broadcast' ? null : 'ip ospf network point-to-point').call(this); this.each(function (i) { os(i).p2p = a[0] !== 'broadcast'; }); }, 'OSPF network type');
  def(IFM, 'no ip ospf network', function () { ix('onet', null).call(this); this.each(function (i) { os(i).p2p = false; }); }, '');
  def(IFM, 'ip ospf <n> area <n>', function (a) { ix('oarea', 'ip ospf ' + a[0] + ' area ' + a[1]).call(this); this.each(function (i) { os(i).area = a[1]; }); }, 'Enable OSPF on this interface directly');
  def('priv', 'clear ip ospf process', function () { this.ask('Reset ALL OSPF processes? [no]: ', function (v) { var o = this.st.ospf; if (/^y/i.test(v) && o) { o.ridAct = o.rid || ''; this.st.odr = {}; this.st.oprev = {}; this.ospfTick(true); } }); this.pending.cmd = 'clear ip ospf process'; }, 'Restart OSPF (applies a new router ID, reruns DR election)');
  Sim.prototype.ospfArea = function (n) {
    var o = this.st.ospf, i = this.st.ifs[n]; if (!o || !i || !i.ip || !this.ifUp(n)) return null;
    if (i.os && i.os.area != null) return i.os.area;
    var ip = ip2n(i.ip), hit = null;
    o.nets.forEach(function (nt) { var w = ip2n(nt.w); if (hit == null && ((ip & ~w) >>> 0) === ((ip2n(nt.ip) & ~w) >>> 0)) hit = nt.area; });
    return hit;
  };
  Sim.prototype.ospfPassive = function (n) { var o = this.st.ospf; return o.pasDef ? !o.npas[n] : !!o.pas[n]; };
  Sim.prototype.ospfRid = function () {
    var o = this.st.ospf, st = this.st, self = this; if (o.ridAct) return o.ridAct;
    var best = function (re) { var b = null; st.order.forEach(function (n) { var i = st.ifs[n]; if (re.test(n) && i.ip && self.ifUp(n) && (!b || ip2n(i.ip) > ip2n(b))) b = i.ip; }); return b; };
    return best(/^Loopback/) || best(/^(?!Loopback)/) || '0.0.0.0';
  };
  Sim.prototype.ospfCost = function (n) { var i = this.st.ifs[n], c = i.os && i.os.cost; if (c) return c; var ref = this.st.ospf.ref || 100, bw = /^Gig/.test(n) ? 1000 : /^Loop/.test(n) ? 8000000 : 100; return Math.max(1, Math.floor(ref / bw)); };
  Sim.prototype.ospfNbrs = function () {
    var self = this, o = this.st.ospf, out = []; if (!o) return out;
    ((this.cfg.ospf || {}).nbrs || []).forEach(function (nb) {
      var n = nb.iface, i = self.st.ifs[n], ar = self.ospfArea(n); if (ar == null || ar !== (nb.area || 0) || self.ospfPassive(n)) return;
      var h = (i.os && i.os.hello) || 10, d = (i.os && i.os.dead) || h * 4, nh = nb.hello || 10;
      if (h !== nh || d !== (nb.dead || nh * 4)) return;
      out.push(nb);
    });
    return out;
  };
  Sim.prototype.ospfRoles = function (n) {
    var i = this.st.ifs[n]; if (i.os && i.os.p2p) return null;
    var me = { rid: this.ospfRid(), pri: i.os && i.os.pri != null ? i.os.pri : 1, me: true };
    var all = [me].concat(this.ospfNbrs().filter(function (x) { return x.iface === n; }).map(function (x) { return { rid: x.rid, pri: x.pri == null ? 1 : x.pri }; }));
    var el = all.filter(function (x) { return x.pri > 0; }).sort(function (a, b) { return b.pri - a.pri || ip2n(b.rid) - ip2n(a.rid); });
    var ids = all.map(function (x) { return x.rid; }), st = this.st; st.odr = st.odr || {};
    var c = st.odr[n], has = function (r) { return r !== '0.0.0.0' && ids.indexOf(r) > -1; };
    /* DR election is not preemptive: keep the elected DR and BDR while they are still present */
    if (!c || c.alone && all.length > 1 || !has(c.dr)) c = { dr: el[0] ? el[0].rid : '0.0.0.0', bdr: el[1] ? el[1].rid : '0.0.0.0', alone: all.length === 1 };
    else if (!has(c.bdr)) { var rest = el.filter(function (x) { return x.rid !== c.dr; }); c = { dr: c.dr, bdr: rest[0] ? rest[0].rid : '0.0.0.0', alone: all.length === 1 }; }
    st.odr[n] = c;
    return { dr: c.dr, bdr: c.bdr, me: me };
  };
  Sim.prototype.nbrState = function (nb) {
    var r = this.ospfRoles(nb.iface); if (!r) return 'FULL/  -';
    if (nb.rid === r.dr) return 'FULL/DR'; if (nb.rid === r.bdr) return 'FULL/BDR';
    return r.me.rid === r.dr || r.me.rid === r.bdr ? 'FULL/DROTHER' : '2WAY/DROTHER';
  };
  Sim.prototype.ospfTick = function (restart) {
    var o = this.st.ospf; if (!o) return;
    var now = {}, prev = this.st.oprev || {}, self = this;
    this.ospfNbrs().forEach(function (nb) { now[nb.rid + '@' + nb.iface] = nb; });
    Object.keys(prev).forEach(function (k) { if (!now[k]) { var nb = prev[k]; self.say('%OSPF-5-ADJCHG: Process ' + o.pid + ', Nbr ' + nb.rid + ' on ' + nb.iface + ' from FULL to DOWN, Neighbor Down: ' + (self.ifUp(nb.iface) && self.ospfArea(nb.iface) != null && !self.ospfPassive(nb.iface) ? 'Dead timer expired' : 'Interface down or detached')); } });
    Object.keys(now).forEach(function (k) { if (!prev[k]) { var nb = now[k]; if (self.nbrState(nb).indexOf('FULL') === 0) self.say('%OSPF-5-ADJCHG: Process ' + o.pid + ', Nbr ' + nb.rid + ' on ' + nb.iface + ' from LOADING to FULL, Loading Done'); } });
    this.st.oprev = now;
  };
  Sim.prototype.ospfEnts = function () {
    var o = this.st.ospf, self = this, ent = [], by = {}; if (!o) return ent;
    var up = {}; this.ospfNbrs().forEach(function (nb) { up[nb.ip] = nb; });
    var lc = Math.max(1, Math.floor((o.ref || 100) / 1000));
    ((this.cfg.ospf || {}).routes || []).forEach(function (r) {
      var nb = up[r.via]; if (!nb) return;
      var p = r.p.split('/'), cost = r.e2 ? 1 : self.ospfCost(nb.iface) + (r.rc != null ? r.rc : (r.links || 1) * lc);
      var k = r.p; if (!by[k] || cost < by[k].cost) by[k] = { cost: cost, p: p, e2: r.e2, hops: [[r.via, nb.iface]] }; else if (cost === by[k].cost) by[k].hops.push([r.via, nb.iface]);
    });
    Object.keys(by).forEach(function (k) {
      var b = by[k], code = b.e2 ? (b.p[0] === '0.0.0.0' ? 'O*E2     ' : 'O E2     ') : 'O        ', head = code + b.p[0] + '/' + b.p[1] + ' ', ln = [];
      b.hops.forEach(function (h, j) { var t = '[110/' + b.cost + '] via ' + h[0] + ', 00:00:12, ' + h[1]; ln.push(j ? new Array(head.length + 1).join(' ') + t : head + t); });
      ent.push({ nn: ip2n(b.p[0]), len: +b.p[1], k: 3, code: 'O', ad: 110, nh: b.hops[0][0], oif: b.hops[0][1], line: ln.join('\n'), dflt: b.p[0] === '0.0.0.0' });
    });
    return ent;
  };
  def('priv', 'show ip ospf neighbor', function () {
    var self = this, o = ['', 'Neighbor ID     Pri   State           Dead Time   Address         Interface'];
    this.ospfNbrs().forEach(function (nb) { var r = self.ospfRoles(nb.iface); o.push(pad(nb.rid, 16) + pad(String(r ? (nb.pri == null ? 1 : nb.pri) : 0), 6) + pad(self.nbrState(nb), 16) + pad('00:00:3' + (nb.rid.length % 9), 12) + pad(nb.ip, 16) + nb.iface); });
    this.say(o.join('\n'));
  }, 'OSPF neighbours and their state');
  def('priv', 'show ip ospf interface brief', function () {
    var st = this.st, self = this, o = ['Interface    PID   Area            IP Address/Mask    Cost  State Nbrs F/C']; if (!st.ospf) { this.say(''); return; }
    st.order.forEach(function (n) {
      var ar = self.ospfArea(n), i = st.ifs[n]; if (ar == null) return;
      var nbs = self.ospfNbrs().filter(function (x) { return x.iface === n; }), r = self.ospfRoles(n), full = nbs.filter(function (x) { return self.nbrState(x).indexOf('FULL') === 0; }).length;
      var stt = r ? (r.me.rid === r.dr ? 'DR' : r.me.rid === r.bdr ? 'BDR' : 'DROTH') : 'P2P';
      if (/^Loopback/.test(n)) stt = 'LOOP';
      o.push(pad(shortIf(n), 13) + pad(st.ospf.pid, 6) + pad(ar, 16) + pad(i.ip + '/' + maskLen(i.mask), 19) + pad(self.ospfCost(n), 6) + pad(stt, 6) + full + '/' + nbs.length);
    });
    this.say(o.join('\n'));
  }, 'OSPF interfaces, cost and DR role');
  def('priv', 'show ip protocols', function () {
    var o = this.st.ospf, self = this; if (!o) { this.say(''); return; }
    var L = ['*** IP Routing is NSF aware ***', '', 'Routing Protocol is "ospf ' + o.pid + '"', '  Outgoing update filter list for all interfaces is not set', '  Incoming update filter list for all interfaces is not set', '  Router ID ' + this.ospfRid(), '  Number of areas in this router is 1. 1 normal 0 stub 0 nssa', '  Maximum path: 4', '  Routing for Networks:'];
    o.nets.forEach(function (x) { L.push('    ' + x.ip + ' ' + x.w + ' area ' + x.area); });
    var pv = this.st.order.filter(function (n) { return self.ospfPassive(n) && self.st.ifs[n].ip; });
    if (pv.length) { L.push('  Passive Interface(s):'); pv.forEach(function (n) { L.push('    ' + n); }); }
    L.push('  Routing Information Sources:', '    Gateway         Distance      Last Update');
    var seen = {}; this.ospfNbrs().forEach(function (nb) { if (!seen[nb.rid]) { seen[nb.rid] = 1; L.push('    ' + pad(nb.rid, 16) + pad('     110', 14) + '00:00:12'); } });
    L.push('  Distance: (default is 110)'); this.say(L.join('\n'));
  }, 'Routing protocol summary');
  def('priv', 'show ip route ospf', function () { this.say(this.routeHead().concat(this.routeEnts().filter(function (e) { return e.code === 'O'; }).map(function (e) { return e.line; })).join('\n')); }, 'OSPF routes only');

  /* DHCP */
  def('config', 'ip dhcp excluded-address <ip>', gx(function (a) { return 'dx' + a[0]; }, function (a) { return 'ip dhcp excluded-address ' + a[0]; }), 'Addresses the DHCP server must not hand out');
  def('config', 'ip dhcp excluded-address <ip> <ip>', gx(function (a) { return 'dx' + a[0]; }, function (a) { return 'ip dhcp excluded-address ' + a[0] + ' ' + a[1]; }), '');
  def('config', 'ip dhcp pool <w>', function (a) { var st = this.st; st.pools = st.pools || {}; st.pools[a[0]] = st.pools[a[0]] || {}; this.mode = 'dhcp'; this.ctx = [a[0]]; }, 'Create or edit a DHCP pool');
  def('config', 'no ip dhcp pool <w>', function (a) { if (this.st.pools) delete this.st.pools[a[0]]; }, '');
  def('dhcp', 'network <ip> <ip>', function (a) { var len = maskLen(a[1]); if (n2ip(len ? (0xFFFFFFFF << (32 - len)) >>> 0 : 0) !== a[1]) { this.say('% Invalid mask'); return; } this.st.pools[this.ctx[0]].net = a[0] + ' ' + a[1]; }, 'Subnet this pool serves');
  def('dhcp', 'default-router <ip>', function (a) { this.st.pools[this.ctx[0]].gw = a[0]; }, 'Gateway handed to clients');
  def('dhcp', 'dns-server <rest>', function (a) { this.st.pools[this.ctx[0]].dns = a[0]; }, 'DNS servers handed to clients');
  def('dhcp', 'domain-name <w>', function (a) { this.st.pools[this.ctx[0]].dom = a[0]; }, 'DNS domain for clients');
  def('dhcp', 'lease <rest>', function (a) { this.st.pools[this.ctx[0]].lease = a[0]; }, 'Lease time: days [hours] [minutes]');
  def(IFM, 'ip helper-address <ip>', ix('helper', function (a) { return 'ip helper-address ' + a[0]; }), 'Relay DHCP broadcasts to this server');
  def(IFM, 'no ip helper-address <ip>', ix('helper', null), '');
  def(IFM, 'ip address dhcp', function () { this.each(function (i) { i.dhcp = true; delete i.ip; delete i.mask; }); }, 'Get this interface address from DHCP');
  Sim.prototype.leases = function () {
    var st = this.st, out = [], cl = ((this.cfg.dhcp || {}).clients || []), self = this;
    var ex = Object.keys(st.gx).filter(function (k) { return k.indexOf('dx') === 0; }).map(function (k) { var p = st.gx[k].split(' ').slice(3); return [ip2n(p[0]), ip2n(p[1] || p[0])]; });
    Object.keys(st.pools || {}).forEach(function (pn) {
      var P = st.pools[pn]; if (!P.net) return; var nw = P.net.split(' '), base = ip2n(nw[0]), len = maskLen(nw[1]), size = Math.pow(2, 32 - len), mine = st.order.some(function (n) { var i = st.ifs[n]; return i.ip && self.ifUp(n) && maskLen(i.mask) === len && ((ip2n(i.ip) >>> (32 - len)) === (base >>> (32 - len))); });
      if (!mine) return; var ip = base + 1;
      cl.forEach(function (c) { while (ip < base + size - 1 && ex.some(function (r) { return ip >= r[0] && ip <= r[1]; })) ip++; if (ip < base + size - 1) { out.push({ ip: n2ip(ip), mac: c, pool: pn }); ip++; } });
    });
    return out;
  };
  def('priv', 'show ip dhcp binding', function () {
    var o = ['Bindings from all pools not associated with VRF:', 'IP address          Client-ID/              Lease expiration        Type', '                    Hardware address/', '                    User name'], exp = fmtDate(new Date(Date.now() + 864e5));
    this.leases().forEach(function (l) { o.push(pad(l.ip, 20) + pad(('01' + l.mac.replace(/\./g, '')).replace(/(.{4})(?=.)/g, '$1.'), 24) + pad(exp, 24) + 'Automatic'); });
    this.say(o.join('\n'));
  }, 'Leases this router has handed out');
  def('priv', 'show ip dhcp pool', function () {
    var st = this.st, L = this.leases(), o = [];
    Object.keys(st.pools || {}).forEach(function (pn) { var P = st.pools[pn], n = L.filter(function (l) { return l.pool === pn; }).length; o.push('', 'Pool ' + pn + ' :', ' Utilization mark (high/low)    : 100 / 0', ' Subnet size (first/next)       : 0 / 0', ' Total addresses                : ' + (P.net ? Math.pow(2, 32 - maskLen(P.net.split(' ')[1])) - 2 : 0), ' Leased addresses               : ' + n, ' Pending event                  : none'); });
    this.say(o.join('\n'));
  }, 'DHCP pools and how full they are');

  /* NAT */
  function natOn(i) { return i.x && i.x.nat ? i.x.nat.split(' ')[2] : null; }
  def(IFM, 'ip nat inside|outside', ix('nat', function (a) { return 'ip nat ' + a[0]; }), 'Mark the inside or outside of NAT');
  def(IFM, 'no ip nat inside|outside', ix('nat', null), '');
  def('config', 'ip nat inside source list <w> interface <if> overload', function (a) { this.st.natsrc = { list: a[0], oif: a[1], ovl: true }; }, 'PAT: share the outside interface address');
  def('config', 'ip nat inside source list <w> pool <w>', function (a) { this.st.natsrc = { list: a[0], pool: a[1], ovl: false }; }, 'Dynamic NAT from a pool');
  def('config', 'ip nat inside source list <w> pool <w> overload', function (a) { this.st.natsrc = { list: a[0], pool: a[1], ovl: true }; }, 'PAT over a pool');
  def('config', 'no ip nat inside source list <rest>', function () { this.st.natsrc = null; }, '');
  def('config', 'ip nat inside source static <ip> <ip>', function (a) { var st = this.st; st.natst = st.natst || {}; st.natst[a[0]] = a[1]; }, 'Static one to one NAT');
  def('config', 'no ip nat inside source static <ip> <ip>', function (a) { if (this.st.natst) delete this.st.natst[a[0]]; }, '');
  def('config', 'ip nat pool <w> <ip> <ip> netmask <ip>', function (a) { var st = this.st; st.natpool = st.natpool || {}; st.natpool[a[0]] = [a[1], a[2], a[3]]; }, 'Range of public addresses');
  def('config', 'no ip nat pool <w>', function (a) { if (this.st.natpool) delete this.st.natpool[a[0]]; }, '');
  def('priv', 'clear ip nat translation *', function () { this.st.natclr = true; }, 'Drop dynamic translations (breaks live sessions)');
  Sim.prototype.natRows = function () {
    var st = this.st, self = this, rows = [], ins = st.order.filter(function (n) { return natOn(st.ifs[n]) === 'inside'; }), outs = st.order.filter(function (n) { return natOn(st.ifs[n]) === 'outside'; });
    Object.keys(st.natst || {}).forEach(function (k) { rows.push(['---', st.natst[k], k, '---', '---']); });
    var s = st.natsrc, A = s && st.acls && st.acls[s.list];
    var clr = st.natclr; st.natclr = false;
    if (s && A && ins.length && outs.length && !clr) {
      var permits = function (ip) { var hit = null; A.ents.forEach(function (e) { if (hit || /^remark/.test(e.txt)) return; var t = e.txt.split(' '), ad = aclAddr(t, 1) || { s: t[1] }; var src = t[1] === 'any' ? true : t[1] === 'host' ? t[2] === ip : (function () { var w = ip2n(t[2] || '0.0.0.0'); return ((ip2n(ip) & ~w) >>> 0) === ip2n(t[1]); })(); if (src) hit = t[0]; }); return hit === 'permit'; };
      var pool = s.pool && st.natpool && st.natpool[s.pool], pAddr = [], used = {};
      if (pool) for (var x = ip2n(pool[0]); x <= ip2n(pool[1]); x++) pAddr.push(n2ip(x));
      var gip = s.oif ? (st.ifs[s.oif] || {}).ip : null;
      ((this.cfg.nat || {}).flows || []).forEach(function (f) {
        if (!permits(f.il)) return;
        var g = gip; if (pool) { if (!s.ovl) { if (used[f.il] == null) { if (Object.keys(used).length >= pAddr.length) return; used[f.il] = pAddr[Object.keys(used).length]; } g = used[f.il]; } else g = pAddr[0]; }
        if (!g) return;
        rows.push([f.pro, g + ':' + f.ip, f.il + ':' + f.ip, f.og + ':' + f.op, f.og + ':' + f.op]);
      });
    }
    return { rows: rows, ins: ins, outs: outs };
  };
  def('priv', 'show ip nat translations', function () {
    var R = this.natRows(), o = ['Pro  Inside global         Inside local          Outside local         Outside global'];
    R.rows.forEach(function (r) { o.push(pad(r[0], 5) + pad(r[1], 22) + pad(r[2], 22) + pad(r[3], 22) + r[4]); });
    this.say(o.join('\n'));
  }, 'Current NAT translations');
  def('priv', 'show ip nat statistics', function () {
    var R = this.natRows(), st = R.rows.filter(function (r) { return r[0] === '---'; }).length, dy = R.rows.length - st;
    this.say(['Total active translations: ' + R.rows.length + ' (' + st + ' static, ' + dy + ' dynamic; ' + dy + ' extended)', 'Outside interfaces:', '  ' + (R.outs.join(', ') || 'none'), 'Inside interfaces:', '  ' + (R.ins.join(', ') || 'none'), 'Hits: ' + dy * 12 + '  Misses: ' + dy].join('\n'));
  }, 'NAT counters and interfaces');

  /* NTP, syslog, SNMP, backups */
  var SEV = ['emergencies', 'alerts', 'critical', 'errors', 'warnings', 'notifications', 'informational', 'debugging'];
  def('config', 'ntp server <ip>', gp('gp2', function (a) { return 'ntp' + a[0]; }, function (a) { return 'ntp server ' + a[0]; }), 'Get time from this NTP server');
  def('config', 'no ntp server <ip>', gp('gp2', function (a) { return 'ntp' + a[0]; }, null), '');
  def('config', 'service timestamps <rest>', gx(function (a) { return 'sts' + a[0].split(' ')[0]; }, function (a) { return 'service timestamps ' + a[0]; }), 'Timestamp format for log or debug messages');
  def('config', 'logging host <ip>', gp('gp2', function (a) { return 'lgh' + a[0]; }, function (a) { return 'logging host ' + a[0]; }), 'Send logs to this syslog server');
  def('config', 'logging <ip>', gp('gp2', function (a) { return 'lgh' + a[0]; }, function (a) { return 'logging host ' + a[0]; }), 'Send logs to this syslog server (older form)');
  def('config', 'no logging host <ip>', gp('gp2', function (a) { return 'lgh' + a[0]; }, null), '');
  def('config', 'logging trap <w>', function (a) { var v = a[0].toLowerCase(), k = /^\d$/.test(v) ? +v : SEV.indexOf(v); if (!(k >= 0 && k <= 7)) { this.say("% Invalid input detected at '^' marker."); return; } this.st.gp2 = this.st.gp2 || {}; if (k === 6) delete this.st.gp2.lgt; else this.st.gp2.lgt = 'logging trap ' + SEV[k]; this.st.trap = k; /* informational is the default, so IOS does not show it */ }, 'Most detailed severity sent to syslog (0 to 7)');
  def('config', 'logging buffered <rest>', gx('lgb', function (a) { return 'logging buffered ' + a[0]; }), 'Keep logs in RAM');
  def('config', 'snmp-server community <w> ro|rw', gp('gp2', function (a) { return 'snc' + a[0]; }, function (a) { return 'snmp-server community ' + a[0] + ' ' + a[1].toUpperCase(); }), 'SNMPv1/v2c community (cleartext)');
  def('config', 'snmp-server community <w> ro|rw <w>', gp('gp2', function (a) { return 'snc' + a[0]; }, function (a) { return 'snmp-server community ' + a[0] + ' ' + a[1].toUpperCase() + ' ' + a[2]; }), '');
  def('config', 'no snmp-server community <w>', gp('gp2', function (a) { return 'snc' + a[0]; }, null), '');
  def('config', 'snmp-server location|contact <rest>', gp('gp2', function (a) { return 'sn' + a[0]; }, function (a) { return 'snmp-server ' + a[0] + ' ' + a[1]; }), 'SNMP system information');
  def('config', 'snmp-server group|user|host <rest>', gp('gp2', function (a) { return 'sn' + a[0] + a[1].split(' ')[0]; }, function (a) { return 'snmp-server ' + a[0] + ' ' + a[1]; }), 'SNMPv3 groups and users, or trap receivers');
  def('config', 'snmp-server enable traps', gp('gp2', 'snt', 'snmp-server enable traps'), 'Send SNMP traps');
  def('priv', 'show ntp status', function () {
    var st = this.st, srv = Object.keys(st.gp2 || {}).filter(function (k) { return k.indexOf('ntp') === 0; }).map(function (k) { return k.slice(3); })[0], ok = srv && (this.cfg.ntp || {}).ok === srv;
    this.say(ok ? 'Clock is synchronized, stratum ' + ((this.cfg.ntp.st || 1) + 1) + ', reference is ' + srv + '\nnominal freq is 250.0000 Hz, actual freq is 250.0000 Hz, precision is 2**24\nreference time is (simulated)\nclock offset is 0.0000 msec, root delay is 0.00  msec' : 'Clock is unsynchronized, stratum 16, no reference clock\nnominal freq is 250.0000 Hz, actual freq is 250.0000 Hz, precision is 2**24');
  }, 'NTP synchronisation state');
  def('priv', 'show ntp associations', function () {
    var st = this.st, o = ['', '  address         ref clock       st   when   poll reach  delay  offset   disp'], ok = (this.cfg.ntp || {}).ok;
    Object.keys(st.gp2 || {}).filter(function (k) { return k.indexOf('ntp') === 0; }).forEach(function (k) { var ip = k.slice(3), y = ok === ip; o.push((y ? '*~' : ' ~') + pad(ip, 16) + pad(y ? '.LOCL.' : '.INIT.', 16) + pad(y ? ' 1' : '16', 5) + pad(y ? '   12' : '    -', 7) + pad('   64', 7) + pad(y ? '377' : '  0', 6) + ' 0.000   0.000  ' + (y ? '0.191' : '16000.')); });
    o.push(' * sys.peer, # selected, + candidate, - outlyer, x falseticker, ~ configured'); this.say(o.join('\n'));
  }, 'NTP servers and which one is used');
  def('user priv', 'show clock', function () { var d = new Date(), ok = (this.cfg.ntp || {}).ok && Object.keys(this.st.gp2 || {}).some(function (k) { return k.indexOf('ntp') === 0; }); this.say((ok ? '' : '*') + d.toTimeString().slice(0, 8) + '.' + ('00' + d.getMilliseconds()).slice(-3) + ' IST ' + d.toDateString()); }, 'Current time');
  def('user priv', 'show clock detail', function () { var d = new Date(), ok = (this.cfg.ntp || {}).ok && Object.keys(this.st.gp2 || {}).some(function (k) { return k.indexOf('ntp') === 0; }); this.say((ok ? '' : '*') + d.toTimeString().slice(0, 8) + '.' + ('00' + d.getMilliseconds()).slice(-3) + ' IST ' + d.toDateString() + '\n' + (ok ? 'Time source is NTP' : 'No time source')); }, 'Current time and its source');
  def('priv', 'show logging', function () {
    var st = this.st, hosts = Object.keys(st.gp2 || {}).filter(function (k) { return k.indexOf('lgh') === 0; }).map(function (k) { return k.slice(3); }), t = st.trap == null ? 6 : st.trap;
    var o = ['Syslog logging: enabled (0 messages dropped, 0 flushes, 0 overruns)', '    Console logging: level debugging, 42 messages logged', '    Monitor logging: level debugging, 0 messages logged', '    Buffer logging:  ' + (st.gx.lgb ? 'level debugging, 42 messages logged' : 'disabled'), '    Trap logging: level ' + SEV[t] + ', 46 message lines logged'];
    hosts.forEach(function (h) { o.push('        Logging to ' + h + '  (udp port 514, audit disabled,', '              link up),', '              12 message lines logged'); });
    this.say(o.join('\n'));
  }, 'Logging settings and syslog servers');
  def('priv', 'copy running-config tftp:', function () {
    this.ask('Address or name of remote host []? ', function (h) {
      if (!ipOk(h)) { this.say('%Error parsing tftp://' + h); return; }
      var fn = this.st.host.toLowerCase() + '-confg';
      this.ask('Destination filename [' + fn + ']? ', function (f) { var len = this.running().length; this.say('Writing ' + (f || fn) + '...!!'); this.say('[OK - ' + len + ' bytes]'); this.say(''); this.say(len + ' bytes copied in 0.' + (len % 900 + 100) + ' secs'); this.st.tftp = h; });
      this.pending.cmd = 'copy running-config tftp:';
    });
  }, 'Back up the configuration to a TFTP server');

  /* Port security, DHCP snooping, DAI */
  Sim.prototype.psMacs = function (n) { var sh = shortIf(n), st = this.st; return (this.cfg.macs || []).filter(function (r) { return r[2] === sh && !(st.psGone || {})[n + r[1]]; }); };
  Sim.prototype.psEval = function () {
    this.each(function (i, n) {
      var p = i.ps; if (!p || !p.on || i.errd || i.shut) return;
      var macs = this.psMacs(n), max = p.max || 1; if (macs.length <= max) return;
      var bad = macs[max]; p.viol = (p.viol || 0) + macs.length - max;
      if ((p.act || 'shutdown') === 'shutdown') {
        this.say('%PM-4-ERR_DISABLE: psecure-violation error detected on ' + shortIf(n) + ', putting ' + shortIf(n) + ' in err-disable state');
        this.say('%PORT_SECURITY-2-PSECURE_VIOLATION: Security violation occurred, caused by MAC address ' + bad[1] + ' on port ' + n + '.');
        this.say('%LINEPROTO-5-UPDOWN: Line protocol on Interface ' + n + ', changed state to down'); this.say('%LINK-3-UPDOWN: Interface ' + n + ', changed state to down');
        i.errd = true; this.st.psGone = this.st.psGone || {}; var st = this.st; macs.slice(max).forEach(function (m) { st.psGone[n + m[1]] = true; });
      }
    });
  };
  function psCmd(fn) { return spOnly(function (a) { var bad = null; this.each(function (i, n) { if (i.mode !== 'access' && !bad) bad = n; }); if (bad) { this.say('Command rejected: ' + bad + ' is a dynamic port.'); return; } fn.call(this, a); this.psEval(); }); }
  def('if range', 'switchport port-security', psCmd(function () { ix('ps', 'switchport port-security').call(this); this.each(function (i) { i.ps = i.ps || {}; i.ps.on = true; }); }), 'Turn on port security (default: 1 MAC, violation shutdown)');
  def('if range', 'switchport port-security maximum <n>', psCmd(function (a) { ix('psm', 'switchport port-security maximum ' + a[0]).call(this); this.each(function (i) { i.ps = i.ps || {}; i.ps.max = a[0]; }); }), 'How many MAC addresses this port may learn');
  def('if range', 'switchport port-security mac-address sticky', psCmd(function () { ix('pss', 'switchport port-security mac-address sticky').call(this); this.each(function (i) { i.ps = i.ps || {}; i.ps.sticky = true; }); }), 'Save learned MACs into the running config');
  def('if range', 'switchport port-security violation protect|restrict|shutdown', psCmd(function (a) { ix('psv', a[0] === 'shutdown' ? null : 'switchport port-security violation ' + a[0]).call(this); this.each(function (i) { i.ps = i.ps || {}; i.ps.act = a[0]; }); }), 'What happens on a violation');
  def('priv', 'show port-security', function () {
    var st = this.st, self = this, o = ['Secure Port  MaxSecureAddr  CurrentAddr  SecurityViolation  Security Action', '                (Count)       (Count)          (Count)', '---------------------------------------------------------------------------'];
    st.order.forEach(function (n) { var i = st.ifs[n], p = i.ps; if (!p || !p.on) return; var cur = Math.min(self.psMacs(n).length, p.max || 1); if (i.errd) cur = 0; o.push(pad('      ' + shortIf(n), 19) + pad(String(p.max || 1), 13) + pad(String(cur), 19) + pad(String(p.viol || 0), 11) + ((p.act || 'shutdown').charAt(0).toUpperCase() + (p.act || 'shutdown').slice(1))); });
    o.push('---------------------------------------------------------------------------', 'Total Addresses in System (excluding one mac per port)     : 0', 'Max Addresses limit in System (excluding one mac per port) : 4096');
    this.say(o.join('\n'));
  }, 'Port security summary');
  def('priv', 'show port-security interface <if>', function (a) {
    var n = a[0], i = this.st.ifs[n] || {}, p = i.ps || {}, macs = this.psMacs(n), cur = i.errd ? 0 : Math.min(macs.length, p.max || 1);
    this.say(['Port Security              : ' + (p.on ? 'Enabled' : 'Disabled'), 'Port Status                : ' + (!p.on ? 'Secure-down' : i.errd ? 'Secure-shutdown' : this.ifUp(n) ? 'Secure-up' : 'Secure-down'), 'Violation Mode             : ' + ((p.act || 'shutdown').charAt(0).toUpperCase() + (p.act || 'shutdown').slice(1)), 'Aging Time                 : 0 mins', 'Aging Type                 : Absolute', 'SecureStatic Address Aging : Disabled', 'Maximum MAC Addresses      : ' + (p.max || 1), 'Total MAC Addresses        : ' + cur, 'Configured MAC Addresses   : 0', 'Sticky MAC Addresses       : ' + (p.sticky ? cur : 0), 'Last Source Address:Vlan   : ' + (macs[0] ? macs[macs.length - 1][1] + ':' + (i.av || 1) : '0000.0000.0000:0'), 'Security Violation Count   : ' + (p.viol || 0)].join('\n'));
  }, 'Port security on one interface');
  def('priv', 'show interfaces status err-disabled', function () {
    var st = this.st, o = ['', 'Port      Name               Status       Reason               Err-disabled Vlans'];
    st.order.forEach(function (n) { if (st.ifs[n].errd) o.push(pad(shortIf(n), 29) + pad('err-disabled', 13) + 'psecure-violation'); });
    this.say(o.join('\n'));
  }, 'Ports shut down by a protection feature');
  def('config', 'ip dhcp snooping', gx('dsn', 'ip dhcp snooping'), 'Turn on DHCP snooping (also needs a VLAN)');
  def('config', 'no ip dhcp snooping', gx('dsn', null), '');
  def('config', 'ip dhcp snooping vlan <w>', gx('dsnv', function (a) { return 'ip dhcp snooping vlan ' + a[0]; }), 'VLANs where snooping runs');
  def('config', 'no ip dhcp snooping information option', gx('dsno', 'no ip dhcp snooping information option'), 'Do not insert option 82');
  def(IFM, 'ip dhcp snooping trust', ix('dst', 'ip dhcp snooping trust'), 'Allow DHCP server replies on this port');
  def(IFM, 'no ip dhcp snooping trust', ix('dst', null), '');
  def(IFM, 'ip dhcp snooping limit rate <n>', ix('dsr', function (a) { return 'ip dhcp snooping limit rate ' + a[0]; }), 'Max DHCP packets per second');
  def('config', 'ip arp inspection vlan <w>', gx('dai', function (a) { return 'ip arp inspection vlan ' + a[0]; }), 'Dynamic ARP Inspection on these VLANs');
  def(IFM, 'ip arp inspection trust', ix('dait', 'ip arp inspection trust'), 'Do not check ARP on this port');
  Sim.prototype.snoopVlans = function () { var v = this.st.gx.dsnv; return v ? vlist(v.split(' ').pop()) : []; };
  def('priv', 'show ip dhcp snooping', function () {
    var st = this.st, on = !!st.gx.dsn, vl = this.snoopVlans(), o = ['Switch DHCP snooping is ' + (on ? 'enabled' : 'disabled'), 'Switch DHCP gleaning is disabled', 'DHCP snooping is configured on following VLANs:', vl.join(',') || 'none', 'DHCP snooping is operational on following VLANs:', on ? (vl.join(',') || 'none') : 'none', 'DHCP snooping is configured on the following L3 Interfaces:', '', 'Insertion of option 82 is ' + (st.gx.dsno ? 'disabled' : 'enabled'), 'Verification of hwaddr field is enabled', '', 'Interface                  Trusted    Allow option    Rate limit (pps)', '-----------------------    -------    ------------    ----------------'];
    st.order.forEach(function (n) { var x = st.ifs[n].x || {}; if (x.dst || x.dsr) o.push(pad(n, 27) + pad(x.dst ? 'yes' : 'no', 11) + pad(x.dst ? 'yes' : 'no', 16) + (x.dsr ? x.dsr.split(' ').pop() : 'unlimited')); });
    this.say(o.join('\n'));
  }, 'DHCP snooping settings and trusted ports');
  def('priv', 'show ip dhcp snooping binding', function () {
    var st = this.st, c = this.cfg.snoop || {}, o = ['MacAddress          IpAddress        Lease(sec)  Type           VLAN  Interface', '------------------  ---------------  ----------  -------------  ----  --------------------'], n = 0, srv = c.server && st.ifs[c.server];
    if (st.gx.dsn && srv && srv.x && srv.x.dst) (c.clients || []).forEach(function (b) { if (this.snoopVlans().indexOf(b[2]) < 0) return; n++; o.push(pad(b[0].replace(/\./g, '').replace(/(..)(?=.)/g, '$1:').toUpperCase(), 20) + pad(b[1], 17) + pad('86400', 12) + pad('dhcp-snooping', 15) + pad(String(b[2]), 6) + b[3]); }, this);
    o.push('Total number of bindings: ' + n); this.say(o.join('\n'));
  }, 'Who got which address, as seen by snooping');
  def('priv', 'show ip arp inspection vlan <n>', function (a) {
    var on = this.st.gx.dai && vlist(this.st.gx.dai.split(' ').pop()).indexOf(a[0]) > -1;
    this.say(['', 'Source Mac Validation      : Disabled', 'Destination Mac Validation : Disabled', 'IP Address Validation      : Disabled', '', ' Vlan     Configuration    Operation   ACL Match          Static ACL', ' ----     -------------    ---------   ---------          ----------', pad('   ' + a[0], 10) + pad(on ? 'Enabled' : 'Disabled', 17) + pad(on && this.st.vlans[a[0]] ? 'Active' : 'Inactive', 12)].join('\n'));
  }, 'DAI state for one VLAN');

  /* AAA */
  def('config', 'aaa new-model', gx('aaa', 'aaa new-model'), 'Turn on AAA');
  def('config', 'aaa authentication login <w> <rest>', gx(function (a) { return 'aaal' + a[0]; }, function (a) { return 'aaa authentication login ' + a[0] + ' ' + a[1]; }), 'Login method list, tried in order');
  def('config', 'tacacs-server host <ip> key <w>', gp('gp2', function (a) { return 'tac' + a[0]; }, function (a) { return 'tacacs-server host ' + a[0] + ' key ' + a[1]; }), 'TACACS+ server (TCP 49)');
  def('config', 'radius-server host <ip> key <w>', gp('gp2', function (a) { return 'rad' + a[0]; }, function (a) { return 'radius-server host ' + a[0] + ' key ' + a[1]; }), 'RADIUS server (UDP 1812/1813)');
  def('line', 'login authentication <w>', function (a) { var st = this.st; this.cur().forEach(function (k) { st.lines[k].la = a[0]; }); }, 'Use this AAA method list on these lines');
  def('config', 'aaa authorization exec <w> <rest>', gx(function (a) { return 'aaae' + a[0]; }, function (a) { return 'aaa authorization exec ' + a[0] + ' ' + a[1]; }), 'Authorise EXEC sessions');
  def('config', 'aaa accounting exec <w> <rest>', gx(function (a) { return 'aaac' + a[0]; }, function (a) { return 'aaa accounting exec ' + a[0] + ' ' + a[1]; }), 'Record EXEC sessions');

  /* PoE */
  def('priv', 'show power inline', function () {
    var self = this, rows = (this.cfg.poe || []).filter(function (p) { return self.ifUp(p[0]); }), used = rows.reduce(function (s, p) { return s + p[1]; }, 0);
    var o = ['Module   Available     Used     Remaining', '          (Watts)     (Watts)    (Watts)', '------   ---------   --------   ---------', '1           390.0' + pad('', 7) + used.toFixed(1) + pad('', 7) + (390 - used).toFixed(1), 'Interface Admin  Oper       Power   Device              Class Max', '                            (Watts)', '--------- ------ ---------- ------- ------------------- ----- ----'];
    rows.forEach(function (p) { o.push(pad(shortIf(p[0]), 10) + pad('auto', 7) + pad('on', 11) + pad(p[1].toFixed(1), 8) + pad(p[2], 20) + pad('4', 6) + '30.0'); });
    this.say(o.join('\n'));
  }, 'Power over Ethernet per port');

  /* running-config hooks */
  Sim.prototype.runHook = function (k) {
    var st = this.st, o = [], self = this;
    if (k === 0) Object.keys(st.pools || {}).forEach(function (pn) { var P = st.pools[pn]; o.push('ip dhcp pool ' + pn); if (P.net) o.push(' network ' + P.net); if (P.gw) o.push(' default-router ' + P.gw); if (P.dns) o.push(' dns-server ' + P.dns); if (P.dom) o.push(' domain-name ' + P.dom); if (P.lease) o.push(' lease ' + P.lease); o.push('!'); });
    if (k === 1) {
      var os_ = st.ospf; if (os_) { o.push('router ospf ' + os_.pid); if (os_.rid) o.push(' router-id ' + os_.rid); if (os_.ref) o.push(' auto-cost reference-bandwidth ' + os_.ref); if (os_.pasDef) o.push(' passive-interface default'); st.order.forEach(function (n) { if (os_.pasDef ? os_.npas[n] : os_.pas[n]) o.push((os_.pasDef ? ' no' : '') + ' passive-interface ' + n); }); os_.nets.forEach(function (x) { o.push(' network ' + x.ip + ' ' + x.w + ' area ' + x.area); }); if (os_.dio) o.push(' default-information originate'); o.push('!'); }
      Object.keys(st.natpool || {}).forEach(function (p) { var v = st.natpool[p]; o.push('ip nat pool ' + p + ' ' + v[0] + ' ' + v[1] + ' netmask ' + v[2]); });
      if (st.natsrc) o.push('ip nat inside source list ' + st.natsrc.list + (st.natsrc.oif ? ' interface ' + st.natsrc.oif : ' pool ' + st.natsrc.pool) + (st.natsrc.ovl ? ' overload' : ''));
      Object.keys(st.natst || {}).forEach(function (k2) { o.push('ip nat inside source static ' + k2 + ' ' + st.natst[k2]); });
    }
    if (k === 2) {
      (st.aclOrder || []).forEach(function (nm) { var A = st.acls[nm]; if (A.named) { o.push('ip access-list ' + A.type + ' ' + nm); A.ents.forEach(function (e) { o.push(' ' + e.txt); }); } });
      (st.aclOrder || []).forEach(function (nm) { var A = st.acls[nm]; if (!A.named) A.ents.forEach(function (e) { o.push('access-list ' + nm + ' ' + e.txt); }); });
      var g = st.gp2 || {}; Object.keys(g).sort(function (a, b) { var r = function (x) { return /^lg/.test(x) ? 0 : /^sn/.test(x) ? 1 : /^(tac|rad)/.test(x) ? 2 : 3; }; return r(a) - r(b); }).forEach(function (k2) { o.push(g[k2]); });
    }
    if (o.length && o[o.length - 1] !== '!') o.push('!');
    return o;
  };

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
