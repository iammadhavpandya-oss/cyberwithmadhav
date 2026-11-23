/* CyberWithMadhav Learn: networking widgets for the CCNA track.
 * Subnet calculator with practice questions, "which route wins" game and an ACL rule tester.
 * Config per widget in <script type="application/json">. CSP safe (no eval, no inline handlers). */
(function () {
  'use strict';
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function T(k, en) { return window.CWMI18N && window.CWMI18N.t ? window.CWMI18N.t(k, en) : en; }
  function cfgOf(w, cls) { try { return JSON.parse($('.' + cls, w).textContent); } catch (e) { return {}; } }
  function ipOk(s) { return /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/.test(s) && s.split('.').every(function (x) { return +x < 256 && String(+x) === x; }); }
  function ip2n(s) { return s.split('.').reduce(function (a, b) { return a * 256 + (+b); }, 0) >>> 0; }
  function n2ip(n) { return [n >>> 24, (n >>> 16) & 255, (n >>> 8) & 255, n & 255].join('.'); }
  function maskN(len) { return len ? (0xFFFFFFFF << (32 - len)) >>> 0 : 0; }
  function inNet(ip, net, len) { var m = maskN(len); return ((ip & m) >>> 0) === ((net & m) >>> 0); }
  function kind(n) {
    var R = [['10.0.0.0', 8, 'Private (RFC 1918)'], ['172.16.0.0', 12, 'Private (RFC 1918)'], ['192.168.0.0', 16, 'Private (RFC 1918)'], ['127.0.0.0', 8, 'Loopback'],
      ['169.254.0.0', 16, 'Link-local (APIPA: no DHCP answer)'], ['100.64.0.0', 10, 'Shared address space (carrier-grade NAT, RFC 6598)'], ['192.0.2.0', 24, 'Documentation (RFC 5737)'],
      ['198.51.100.0', 24, 'Documentation (RFC 5737)'], ['203.0.113.0', 24, 'Documentation (RFC 5737)'], ['224.0.0.0', 4, 'Multicast'], ['240.0.0.0', 4, 'Reserved'], ['0.0.0.0', 8, 'This network (special)']];
    for (var i = 0; i < R.length; i++) if (inNet(n, ip2n(R[i][0]), R[i][1])) return R[i][2];
    return 'Public';
  }
  function calc(ip, len) {
    var n = ip2n(ip), m = maskN(len), net = (n & m) >>> 0, bc = (net | (~m >>> 0)) >>> 0, size = Math.pow(2, 32 - len);
    var r = { net: n2ip(net), mask: n2ip(m), wc: n2ip((~m) >>> 0), bc: n2ip(bc), total: size, kind: kind(n) };
    if (len === 32) { r.first = r.last = n2ip(n); r.hosts = 1; r.note = '/32: a single host route'; }
    else if (len === 31) { r.first = n2ip(net); r.last = n2ip(bc); r.hosts = 2; r.note = '/31: two addresses, both usable on point-to-point links (RFC 3021)'; }
    else { r.first = n2ip(net + 1); r.last = n2ip(bc - 1); r.hosts = size - 2; }
    var oct = Math.min(3, Math.floor(len / 8)); if (len % 8 === 0 && len > 0) oct = len / 8 - 1;
    r.oct = oct + 1; r.block = 256 - ((m >>> (24 - oct * 8)) & 255); if (len % 8 === 0) r.block = len === 0 ? 256 : 1;
    if (len % 8 === 0 && len) { r.oct = len / 8; r.block = 1; }
    return r;
  }

  /* ---------- subnet calculator ---------- */
  function subnet(w) {
    var ip = $('[data-i="ip"]', w), pf = $('[data-i="pfx"]', w), sl = $('[data-i="slide"]', w), bits = $('.lx-snbits', w), out = $('.lx-snout', w);
    function draw() {
      var v = ip.value.trim(), len = Math.max(0, Math.min(32, parseInt(pf.value, 10) || 0));
      if (!ipOk(v)) { out.innerHTML = '<div><dt>' + esc(T('lx.sn.bad', 'Check the address')) + '</dt><dd>' + esc(T('lx.sn.badd', 'Type four numbers from 0 to 255, like 192.168.50.130')) + '</dd></div>'; bits.innerHTML = ''; return; }
      sl.value = len; var r = calc(v, len), b = ('00000000000000000000000000000000' + ip2n(v).toString(2)).slice(-32), h = '';
      for (var i = 0; i < 32; i++) { h += '<span class="' + (i < len ? 'n' : 'h') + '">' + b[i] + '</span>'; if (i % 8 === 7 && i < 31) h += '<i>.</i>'; }
      bits.innerHTML = h + '<small><b class="n">network bits: ' + len + '</b> <b class="h">host bits: ' + (32 - len) + '</b></small>';
      var rows = [['Network address', r.net + '/' + len], ['Subnet mask', r.mask], ['Wildcard mask', r.wc], ['Broadcast address', len >= 31 ? 'none (' + r.bc + ' is a host here)' : r.bc],
        ['Usable host range', r.first + ' to ' + r.last], ['Usable hosts', r.hosts.toLocaleString('en-IN') + (r.note ? ' (' + r.note + ')' : ' (2^' + (32 - len) + ' minus 2)')],
        ['Block size', len % 8 === 0 ? 'falls on an octet boundary' : r.block + ' in octet ' + r.oct + ' (256 minus ' + (256 - r.block) + ')'], ['Address type', r.kind]];
      out.innerHTML = rows.map(function (x) { return '<div><dt>' + esc(x[0]) + '</dt><dd>' + esc(x[1]) + '</dd></div>'; }).join('');
    }
    ip.addEventListener('input', draw); pf.addEventListener('input', draw);
    sl.addEventListener('input', function () { pf.value = sl.value; draw(); });
    draw();
    var qb = $('[data-q]', w), qp = $('.lx-snq .q', w), row = $('.lx-snq .row', w), ans = $('[data-i="ans"]', w), fb = $('.lx-snq .fb', w), chk = $('[data-check]', w), cur = null, score = [0, 0];
    if (!qb) return;
    function rnd(a, b) { return a + Math.floor(Math.random() * (b - a + 1)); }
    qb.addEventListener('click', function () {
      var bases = [[10, rnd(0, 255), rnd(0, 255), rnd(1, 254)], [172, rnd(16, 31), rnd(0, 255), rnd(1, 254)], [192, 168, rnd(0, 255), rnd(1, 254)]];
      var a = bases[rnd(0, 2)].join('.'), len = rnd(18, 30), r = calc(a, len), kinds = [
        ['network address', r.net], ['broadcast address', r.bc], ['number of usable hosts', String(r.hosts)], ['last usable host', r.last], ['first usable host', r.first], ['subnet mask', r.mask]];
      var k = kinds[rnd(0, kinds.length - 1)]; cur = { a: k[1], r: r, ip: a, len: len, what: k[0] };
      qp.innerHTML = 'Host <code>' + a + '/' + len + '</code>: what is the <b>' + esc(k[0]) + '</b>?';
      row.hidden = false; ans.value = ''; fb.textContent = ''; fb.className = 'fb'; ans.focus();
    });
    function check() {
      if (!cur) return; var v = ans.value.trim().replace(/\/\d+$/, '').replace(/,/g, '');
      var ok = v === cur.a; score[1]++; if (ok) score[0]++;
      fb.className = 'fb ' + (ok ? 'ok' : 'no');
      fb.textContent = (ok ? T('lx.q.right', 'Correct. ') : T('lx.q.wrong', 'Not quite. ') + 'The answer is ' + cur.a + '. ') + 'Network ' + cur.r.net + ', broadcast ' + cur.r.bc + ', block size ' + cur.r.block + '. Score ' + score[0] + '/' + score[1] + '.';
      ip.value = cur.ip; pf.value = cur.len; draw();
    }
    chk.addEventListener('click', check); ans.addEventListener('keydown', function (e) { if (e.key === 'Enter') check(); });
  }

  /* ---------- which route wins ---------- */
  function route(w) {
    var c = cfgOf(w, 'lx-route-cfg'), routes = (c.routes || []).map(function (r, i) { var p = r.p.split('/'); return { i: i, c: r.c, src: r.src, p: r.p, net: ip2n(p[0]), len: +p[1], ad: r.ad, m: r.m, via: r.via }; });
    var tb = $('tbody', w), q = $('.lx-rq', w), fb = $('.lx-rfb', w), nx = $('[data-next]', w), drop = $('[data-drop]', w), sc = $('.lx-rscore', w), k = 0, score = 0, done = false;
    tb.innerHTML = routes.map(function (r) { return '<tr><td><code>' + esc(r.c) + '</code> ' + esc(r.src) + '</td><td><code>' + esc(r.p) + '</code></td><td>' + r.ad + '</td><td>' + r.m + '</td><td>' + esc(r.via) + '</td><td><button type="button" class="lx-wbtn" data-r="' + r.i + '">' + esc(T('lx.rt.pick', 'Use this')) + '</button></td></tr>'; }).join('');
    function solve(d) {
      var ip = ip2n(d), m = routes.filter(function (r) { return inNet(ip, r.net, r.len); }), best = {}, inst = [];
      m.forEach(function (r) { var key = r.p; if (!best[key] || r.ad < best[key].ad || (r.ad === best[key].ad && r.m < best[key].m)) best[key] = r; });
      Object.keys(best).forEach(function (k2) { inst.push(best[k2]); });
      inst.sort(function (a, b) { return b.len - a.len; });
      return { matches: m, installed: inst, win: inst[0] || null };
    }
    function show() {
      var d = c.dests[k]; done = false; fb.textContent = ''; fb.className = 'lx-rfb'; nx.hidden = true;
      $$('button[data-r]', w).forEach(function (b) { b.disabled = false; b.closest('tr').className = ''; }); drop.disabled = false;
      q.innerHTML = 'Packet ' + (k + 1) + ' of ' + c.dests.length + ': destination <code>' + esc(d) + '</code>. Which route forwards it?';
      sc.textContent = 'Score ' + score + '/' + k;
    }
    function answer(i) {
      if (done) return; done = true;
      var s = solve(c.dests[k]), right = s.win ? s.win.i === i : i === -1;
      if (right) score++;
      $$('button[data-r]', w).forEach(function (b) { b.disabled = true; var r = routes[+b.getAttribute('data-r')]; var tr = b.closest('tr');
        if (s.win && r.i === s.win.i) tr.className = 'win'; else if (s.matches.indexOf(r) > -1) tr.className = 'match'; if (r.i === i && !right) tr.className = 'wrong'; });
      drop.disabled = true;
      var why = [];
      if (!s.matches.length) why.push('No route matches, and there is no default route, so the router drops the packet (and may send an ICMP unreachable back).');
      else {
        why.push('Matching routes: ' + s.matches.map(function (r) { return r.p + ' (' + r.src + ', AD ' + r.ad + ')'; }).join(', ') + '.');
        var same = {}; s.matches.forEach(function (r) { (same[r.p] = same[r.p] || []).push(r); });
        Object.keys(same).forEach(function (p) { if (same[p].length > 1) { var w2 = same[p].slice().sort(function (a, b) { return a.ad - b.ad || a.m - b.m; })[0]; why.push('For ' + p + ' several sources offer a route: only the lowest AD (' + w2.src + ', AD ' + w2.ad + ') goes into the routing table. AD only breaks ties for the same prefix.'); } });
        why.push('Longest prefix wins: /' + s.win.len + ' via ' + s.win.via + '.');
      }
      fb.className = 'lx-rfb ' + (right ? 'ok' : 'no');
      fb.innerHTML = '<b>' + esc(right ? T('lx.q.right', 'Correct. ') : T('lx.q.wrong', 'Not quite. ')) + '</b>' + esc(why.join(' '));
      k++; sc.textContent = 'Score ' + score + '/' + k;
      if (k < c.dests.length) nx.hidden = false; else { nx.hidden = false; nx.textContent = T('lx.rt.again', 'Play again'); k = -1; }
    }
    tb.addEventListener('click', function (e) { var b = e.target.closest('button[data-r]'); if (b) answer(+b.getAttribute('data-r')); });
    drop.addEventListener('click', function () { answer(-1); });
    nx.addEventListener('click', function () { if (k === -1) { k = 0; score = 0; nx.textContent = T('lx.rt.next', 'Next packet'); } show(); });
    show();
  }

  /* ---------- ACL tester ---------- */
  var PORTS = { www: 80, http: 80, domain: 53, ftp: 21, 'ftp-data': 20, telnet: 23, smtp: 25, pop3: 110, ntp: 123, snmp: 161, snmptrap: 162, tftp: 69, bootps: 67, bootpc: 68, syslog: 514, tacacs: 49, isakmp: 500 };
  var PROTOS = ['ip', 'tcp', 'udp', 'icmp'];
  function parseAddr(t, i, std) {
    var a = t[i];
    if (a === 'any') return { a: 0, w: 0xFFFFFFFF, n: 1, s: 'any' };
    if (a === 'host' && ipOk(t[i + 1] || '')) return { a: ip2n(t[i + 1]), w: 0, n: 2, s: 'host ' + t[i + 1] };
    if (ipOk(a || '')) {
      if (ipOk(t[i + 1] || '')) return { a: ip2n(a), w: ip2n(t[i + 1]), n: 2, s: a + ' ' + t[i + 1] };
      if (std) return { a: ip2n(a), w: 0, n: 1, s: a };
    }
    return null;
  }
  function parsePort(t, i) {
    var op = t[i]; if (['eq', 'neq', 'gt', 'lt', 'range'].indexOf(op) < 0) return { n: 0 };
    var pv = function (x) { return /^\d+$/.test(x || '') ? +x : PORTS[x]; };
    var p1 = pv(t[i + 1]); if (p1 == null) return { err: 'unknown port "' + (t[i + 1] || '') + '"' };
    if (op === 'range') { var p2 = pv(t[i + 2]); if (p2 == null) return { err: 'range needs two ports' }; return { n: 3, op: op, p: [p1, p2] }; }
    return { n: 2, op: op, p: [p1] };
  }
  function portOk(pp, v) { if (!pp || !pp.op) return true; var p = pp.p; return pp.op === 'eq' ? v === p[0] : pp.op === 'neq' ? v !== p[0] : pp.op === 'gt' ? v > p[0] : pp.op === 'lt' ? v < p[0] : v >= p[0] && v <= p[1]; }
  function parseAcl(text) {
    var type = null, out = [];
    text.split('\n').forEach(function (raw, li) {
      var line = raw.trim(); if (!line || line[0] === '!') return;
      var t = line.toLowerCase().split(/\s+/), r = { raw: line, li: li + 1 };
      if (t[0] === 'ip' && t[1] === 'access-list') { type = t[2]; r.head = true; out.push(r); return; }
      if (t[0] === 'access-list' && /^\d+$/.test(t[1])) { var num = +t[1]; type = (num < 100 || (num >= 1300 && num < 2000)) ? 'standard' : 'extended'; t = t.slice(2); }
      if (t[0] === 'remark' || (/^\d+$/.test(t[0]) && t[1] === 'remark')) { r.remark = true; out.push(r); return; }
      if (/^\d+$/.test(t[0])) { r.seq = +t[0]; t = t.slice(1); }
      if (t[0] !== 'permit' && t[0] !== 'deny') { r.err = 'not an ACL entry (starts with "' + t[0] + '")'; out.push(r); return; }
      r.act = t[0]; var i = 1, ty = type || (PROTOS.indexOf(t[1]) > -1 ? 'extended' : 'standard');
      r.type = ty;
      if (ty === 'standard') {
        var s0 = parseAddr(t, i, true); if (!s0) { r.err = 'could not read the source address'; out.push(r); return; }
        r.src = s0; i += s0.n;
      } else {
        r.proto = t[i]; if (PROTOS.indexOf(r.proto) < 0) { r.err = 'unknown protocol "' + (t[i] || '') + '" (use ip, tcp, udp or icmp)'; out.push(r); return; } i++;
        var s1 = parseAddr(t, i, false); if (!s1) { r.err = 'could not read the source (use any, host A.B.C.D or address plus wildcard)'; out.push(r); return; } r.src = s1; i += s1.n;
        var sp = parsePort(t, i); if (sp.err) { r.err = sp.err; out.push(r); return; } if (sp.n) { if (r.proto === 'ip' || r.proto === 'icmp') { r.err = 'ports only make sense with tcp or udp'; out.push(r); return; } r.sport = sp; i += sp.n; }
        var d1 = parseAddr(t, i, false); if (!d1) { r.err = 'could not read the destination'; out.push(r); return; } r.dst = d1; i += d1.n;
        var dp = parsePort(t, i); if (dp.err) { r.err = dp.err; out.push(r); return; } if (dp.n) { if (r.proto === 'ip' || r.proto === 'icmp') { r.err = 'ports only make sense with tcp or udp'; out.push(r); return; } r.dport = dp; i += dp.n; }
        if (r.proto === 'icmp' && ['echo', 'echo-reply', 'unreachable', 'time-exceeded'].indexOf(t[i]) > -1) { r.icmp = t[i]; i++; }
        if (t[i] === 'established') { if (r.proto !== 'tcp') { r.err = 'established only works with tcp'; out.push(r); return; } r.est = true; i++; }
      }
      if (t[i] === 'log') { r.log = true; i++; }
      if (i < t.length) { r.err = 'did not understand "' + t.slice(i).join(' ') + '"'; }
      out.push(r);
    });
    return out;
  }
  function evalAcl(rules, pk) {
    var res = null, trace = [];
    rules.forEach(function (r) {
      if (r.head || r.remark) return;
      if (r.err) { trace.push({ r: r, st: 'err', why: r.err }); return; }
      if (res) { trace.push({ r: r, st: 'skip', why: 'not checked: an earlier line already matched' }); return; }
      var why = null;
      if (r.type === 'extended' && r.proto !== 'ip' && r.proto !== pk.proto) why = 'protocol is ' + pk.proto + ', line wants ' + r.proto;
      else if (((pk.src & ~r.src.w) >>> 0) !== ((r.src.a & ~r.src.w) >>> 0)) why = 'source ' + n2ip(pk.src) + ' is not ' + r.src.s;
      else if (r.type === 'extended' && ((pk.dst & ~r.dst.w) >>> 0) !== ((r.dst.a & ~r.dst.w) >>> 0)) why = 'destination ' + n2ip(pk.dst) + ' is not ' + r.dst.s;
      else if (r.sport && !portOk(r.sport, pk.sport)) why = 'source port ' + pk.sport + ' does not match';
      else if (r.dport && !portOk(r.dport, pk.dport)) why = 'destination port ' + pk.dport + ' does not match ' + r.dport.op + ' ' + r.dport.p.join(' to ');
      else if (r.icmp && r.icmp !== pk.icmp) why = 'ICMP type is ' + pk.icmp + ', line wants ' + r.icmp;
      else if (r.est && !pk.ack) why = 'established needs ACK or RST set (a reply), this is a new connection';
      if (why) trace.push({ r: r, st: 'no', why: why });
      else { res = r; trace.push({ r: r, st: 'hit', why: 'match: ' + r.act.toUpperCase() + (r.log ? ' and log it' : '') }); }
    });
    return { res: res, trace: trace };
  }
  function acl(w) {
    var c = cfgOf(w, 'lx-acl-cfg'), ta = $('[data-i="acl"]', w), f = function (k) { return $('[data-i="' + k + '"]', w); };
    var tr = $('.lx-acl-trace', w), out = $('.lx-acl-res', w), pre = $('.lx-acl-pre', w);
    if (c.acl && !ta.value) ta.value = c.acl;
    function set(p) { f('proto').value = p.proto; f('src').value = p.src; f('dst').value = p.dst; f('dport').value = p.dport || ''; f('ack').checked = !!p.ack; if (p.icmp) f('icmp').value = p.icmp; sync(); test(); }
    (c.presets || []).forEach(function (p) { var b = document.createElement('button'); b.type = 'button'; b.className = 'lx-wbtn'; b.textContent = p.label; b.addEventListener('click', function () { set(p); }); pre.appendChild(b); });
    function sync() { var pr = f('proto').value; w.setAttribute('data-proto', pr); }
    function test() {
      var s = f('src').value.trim(), d = f('dst').value.trim();
      if (!ipOk(s) || !ipOk(d)) { out.className = 'lx-acl-res'; out.textContent = T('lx.acl.ip', 'Enter a valid source and destination IPv4 address.'); tr.innerHTML = ''; return; }
      var pk = { proto: f('proto').value, src: ip2n(s), dst: ip2n(d), dport: parseInt(f('dport').value, 10) || 0, sport: parseInt(f('sport').value, 10) || 50123, ack: f('ack').checked, icmp: f('icmp').value };
      var rules = parseAcl(ta.value), r = evalAcl(rules, pk);
      tr.innerHTML = r.trace.map(function (x) { return '<li class="' + x.st + '"><code>' + esc(x.r.raw) + '</code><span>' + esc(x.why) + '</span></li>'; }).join('') +
        (r.res ? '' : '<li class="hit imp"><code>deny any (implicit, invisible)</code><span>' + esc(T('lx.acl.imp', 'nothing matched, so the hidden deny at the end drops it')) + '</span></li>');
      var permit = r.res && r.res.act === 'permit';
      out.className = 'lx-acl-res ' + (permit ? 'ok' : 'no');
      out.innerHTML = '<b>' + (permit ? 'PERMITTED' : 'DENIED') + '</b> ' + esc(r.res ? 'by line ' + (r.res.seq != null ? 'sequence ' + r.res.seq : r.res.li) + ': ' + r.res.raw : 'by the implicit deny any at the end of every ACL');
    }
    ['input', 'change'].forEach(function (ev) { w.addEventListener(ev, function (e) { if (e.target.matches('input,select,textarea')) { sync(); test(); } }); });
    $('[data-test]', w).addEventListener('click', test);
    if (c.presets && c.presets[0]) set(c.presets[0]); else { sync(); test(); }
  }

  /* JSON reader: validate with friendly hints, then read values by path (no eval) */
  function jsonHint(t) {
    var bare = t.replace(/"(?:[^"\\]|\\.)*"/g, '""');
    if (/\/\/|\/\*/.test(t.replace(/"(?:[^"\\]|\\.)*"/g, '""'))) return 'Standard JSON has no comments. Remove the // or /* */ text.';
    if (/'[^']*'\s*:/.test(t) || /:\s*'/.test(t)) return 'Strings and keys need double quotes. Single quotes are not allowed in JSON.';
    if (/,\s*[}\]]/.test(bare)) return 'There is a comma right before a closing } or ]. JSON does not allow a trailing comma.';
    if (/[{,]\s*[A-Za-z_][\w-]*\s*:/.test(bare)) return 'Every key must be a string in double quotes, for example "hostname".';
    if (/\b(True|False|None|NULL|TRUE|FALSE)\b/.test(t.replace(/"(?:[^"\\]|\\.)*"/g, '""'))) return 'JSON literals are lowercase: true, false and null.';
    return '';
  }
  function jtype(v) { return v === null ? 'null' : Array.isArray(v) ? 'array' : typeof v === 'object' ? 'object' : typeof v; }
  function jpath(obj, p) {
    var re = /^(?:\.?([A-Za-z_$][\w$-]*)|\[(\d+)\]|\["([^"]+)"\])/, cur = obj, rest = p.trim(), steps = 0;
    if (!rest) return { err: 'Type a path first.' };
    while (rest.length) {
      var m = re.exec(rest); if (!m) return { err: 'Could not read the path near "' + rest + '". Use .key, [0] or ["key"].' };
      var k = m[1] != null ? m[1] : m[2] != null ? +m[2] : m[3];
      if (cur === null || typeof cur !== 'object') return { err: 'Cannot go inside a ' + jtype(cur) + '.' };
      if (typeof k === 'number' && !Array.isArray(cur)) return { err: '[' + k + '] needs an array, but this is an ' + jtype(cur) + '.' };
      if (typeof k === 'string' && Array.isArray(cur)) return { err: '"' + k + '" is a key, but this is an array. Use [0], [1] and so on.' };
      if (!Object.prototype.hasOwnProperty.call(cur, k)) return { err: 'No ' + (typeof k === 'number' ? 'item [' + k + ']' : 'key "' + k + '"') + ' here.' };
      cur = cur[k]; rest = rest.slice(m[0].length); steps++;
    }
    return { v: cur };
  }
  function jsonLab(w) {
    var c = cfgOf(w, 'lx-json-cfg'), ta = $('[data-i="json"]', w), pin = $('[data-i="path"]', w), res = $('.lx-json-res', w), val = $('.lx-json-val', w), qs = $('.lx-json-qs', w), pre = $('.lx-json-pre', w);
    ta.value = c.json || '';
    var mk = function (label, fn) { var b = document.createElement('button'); b.type = 'button'; b.className = 'lx-wbtn'; b.textContent = label; b.addEventListener('click', fn); pre.appendChild(b); };
    mk(T('lx.json.good', 'Valid example'), function () { ta.value = c.json || ''; check(); });
    (c.broken || []).forEach(function (x) { mk(x.label, function () { ta.value = x.json; check(); }); });
    var done = {};
    (c.qs || []).forEach(function (q, i) { var li = document.createElement('li'); li.innerHTML = esc(q.q); li.setAttribute('data-q', i); qs.appendChild(li); });
    function parse() { try { return { ok: true, v: JSON.parse(ta.value) }; } catch (e) { return { ok: false, e: e }; } }
    function check() {
      var r = parse();
      if (r.ok) {
        var cnt = {}; (function walk(v) { var t = jtype(v); cnt[t] = (cnt[t] || 0) + 1; if (t === 'array') v.forEach(walk); else if (t === 'object') Object.keys(v).forEach(function (k) { walk(v[k]); }); })(r.v);
        res.className = 'lx-json-res ok'; res.textContent = T('lx.json.ok', 'Valid JSON.') + ' ' + Object.keys(cnt).map(function (k) { return cnt[k] + ' ' + k + (cnt[k] > 1 ? 's' : ''); }).join(', ') + '.';
      } else { res.className = 'lx-json-res no'; res.textContent = T('lx.json.bad', 'Not valid JSON.') + ' ' + (jsonHint(ta.value) || String(r.e.message || r.e)); }
      return r;
    }
    function read() {
      var r = parse(); if (!r.ok) { check(); val.className = 'lx-json-val no'; val.textContent = T('lx.json.fix', 'Fix the JSON first.'); return; }
      var o = jpath(r.v, pin.value);
      if (o.err) { val.className = 'lx-json-val no'; val.textContent = o.err; return; }
      val.className = 'lx-json-val ok'; val.textContent = jtype(o.v) + ': ' + JSON.stringify(o.v);
      (c.qs || []).forEach(function (q, i) { if (!done[i] && JSON.stringify(q.v) === JSON.stringify(o.v)) { done[i] = 1; var li = $('[data-q="' + i + '"]', qs); li.className = 'ok'; li.appendChild(document.createTextNode(' ' + T('lx.json.got', 'Found:') + ' ' + pin.value.trim())); } });
    }
    $('[data-check]', w).addEventListener('click', check); $('[data-read]', w).addEventListener('click', read);
    pin.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); read(); } });
    check();
  }

  function init() {
    $$('.lx-subnet').forEach(subnet); $$('.lx-route').forEach(route); $$('.lx-acl').forEach(acl); $$('.lx-json').forEach(jsonLab);
  }
  window.CWMNet = { calc: calc, parseAcl: parseAcl, evalAcl: evalAcl, ip2n: ip2n };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
