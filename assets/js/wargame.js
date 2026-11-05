/* CyberWithMadhav Terminal Wargame.
   A simulated Linux shell that runs only on an in-memory JSON file tree.
   Nothing here executes real code. Output is written as text nodes only.
   Engine (Shell) works in the browser and in Node (tools/test_wargame.mjs). */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CWMWargame = api;
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => api.boot());
    else api.boot();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* ======================= engine ======================= */

  const COMMANDS = ['ls', 'cd', 'pwd', 'whoami', 'id', 'history', 'echo', 'cat', 'less', 'head', 'tail', 'file',
    'find', 'grep', 'sort', 'uniq', 'wc', 'strings', 'base64', 'chmod'];
  const WS = /[\s\x1c-\x1f\x85]+/;

  function permsStr(p) {
    if (/^\d+$/.test(p)) {
      let out = '';
      for (const ch of p.slice(-3)) {
        const d = Number(ch);
        out += (d & 4 ? 'r' : '-') + (d & 2 ? 'w' : '-') + (d & 1 ? 'x' : '-');
      }
      return out;
    }
    return p;
  }
  function linesOf(t) {
    if (t === '') return [];
    const ls = t.split('\n');
    if (ls[ls.length - 1] === '') ls.pop();
    return ls;
  }
  const joinLines = ls => ls.map(l => l + '\n').join('');
  const cmpStr = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  const pad = (s, n) => { s = String(s); while (s.length < n) s = ' ' + s; return s; };
  const isFlag = t => t.length > 1 && t[0] === '-';

  /* Shell wildcards: only * and ? are special. Everything else is literal. */
  function globRe(pat) {
    let re = '';
    for (const c of pat) {
      if (c === '*') re += '[\\s\\S]*';
      else if (c === '?') re += '[\\s\\S]';
      else re += c.replace(/[.*+?^${}()|[\]\\\/-]/g, '\\$&');
    }
    return new RegExp('^' + re + '$');
  }

  /* Split a line into pipeline segments of {t: text, g: globbable}. */
  function tokenize(line) {
    const segs = []; let cur = [], tok = '', glob = true, has = false, q = null;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (q) {
        if (c === q) q = null;
        else { tok += c; if (c === '*' || c === '?') glob = false; }
      } else if (c === "'" || c === '"') { q = c; has = true; }
      else if (c === '\\' && i + 1 < line.length) {
        i++; tok += line[i]; has = true;
        if (line[i] === '*' || line[i] === '?') glob = false;
      } else if (c === '|') {
        if (has) cur.push({ t: tok, g: glob });
        segs.push(cur); cur = []; tok = ''; glob = true; has = false;
      } else if (/\s/.test(c)) {
        if (has) cur.push({ t: tok, g: glob });
        tok = ''; glob = true; has = false;
      } else { tok += c; has = true; }
    }
    if (q) throw new Error('unterminated quote');
    if (has) cur.push({ t: tok, g: glob });
    segs.push(cur);
    return segs;
  }

  class UsageError extends Error {}

  class Shell {
    constructor(level) {
      const fs = level.fs;
      this.root = JSON.parse(JSON.stringify(fs));
      this.user = fs.user;
      this.uid = fs.uid == null ? 1000 : fs.uid;
      this.groups = fs.groups;
      this.gnames = fs.groups.map(g => g.name);
      this.cwd = fs.cwd;
      this.home = '/home/' + this.user;
      this.history = (fs.history || []).slice();
      this.allowed = new Set((level.allowed_cmds || COMMANDS).map(c => c.split(' ')[0]));
    }

    /* ---------- paths and permissions ---------- */
    abspath(p) {
      if (p === '~' || p.startsWith('~/')) p = this.home + p.slice(1);
      if (!p.startsWith('/')) p = this.cwd.replace(/\/+$/, '') + '/' + p;
      const parts = [];
      for (const seg of p.split('/')) {
        if (seg === '' || seg === '.') continue;
        if (seg === '..') { if (parts.length) parts.pop(); } else parts.push(seg);
      }
      return '/' + parts.join('/');
    }
    /* owner triplet, else group triplet, else other triplet */
    can(node, bit) {
      if (this.user === 'root') return true;
      const p = permsStr(node.perms);
      const t = node.owner === this.user ? p.slice(0, 3) : this.gnames.includes(node.group) ? p.slice(3, 6) : p.slice(6, 9);
      const idx = 'rwx'.indexOf(bit), ch = t[idx];
      return ch !== '-' && (ch === 'rwx'[idx] || ch === 's' || ch === 't');
    }
    /* x is needed on every directory passed through */
    lookup(p) {
      const ap = this.abspath(p);
      let node = this.root;
      if (ap === '/') return { node, err: null };
      for (const seg of ap.replace(/^\/+|\/+$/g, '').split('/')) {
        if (node.type !== 'dir') return { node: null, err: 'ENOTDIR' };
        if (!this.can(node, 'x')) return { node: null, err: 'EACCES' };
        const nxt = node.children.find(c => c.name === seg);
        if (!nxt) return { node: null, err: 'ENOENT' };
        node = nxt;
      }
      return { node, err: null };
    }
    glob(tok) {
      let d, pat, dpath;
      const k = tok.lastIndexOf('/');
      if (k >= 0) { d = tok.slice(0, k); pat = tok.slice(k + 1); dpath = d || '/'; }
      else { d = null; pat = tok; dpath = '.'; }
      const { node, err } = this.lookup(dpath);
      if (err || node.type !== 'dir' || !this.can(node, 'r')) return [tok];
      const re = globRe(pat);
      const names = node.children.map(c => c.name)
        .filter(n => re.test(n) && (pat.startsWith('.') || !n.startsWith('.'))).sort(cmpStr);
      if (!names.length) return [tok];
      return names.map(n => (d !== null ? d + '/' + n : n));
    }
    readFile(cmd, p) {
      const { node, err } = this.lookup(p);
      if (err === 'EACCES') return [null, `${cmd}: ${p}: Permission denied\n`];
      if (err) return [null, `${cmd}: ${p}: No such file or directory\n`];
      if (node.type === 'dir') return [null, `${cmd}: ${p}: Is a directory\n`];
      if (!this.can(node, 'r')) return [null, `${cmd}: ${p}: Permission denied\n`];
      return [node.content, ''];
    }
    inputs(cmd, files, stdin) {
      if (!files.length) return [[[null, stdin]], ''];
      const out = []; let err = '';
      for (const f of files) {
        if (f === '-') { out.push([f, stdin]); continue; }
        const [c, e] = this.readFile(cmd, f);
        err += e;
        if (c !== null) out.push([f, c]);
      }
      return [out, err];
    }
    isAllowed(cmd) { return this.allowed.has(cmd); }
    commandNames() { return COMMANDS.filter(c => this.allowed.has(c)); }

    /* ---------- run one line ---------- */
    run(line, record = true) {
      if (record) this.history.push(line);
      let segs;
      try { segs = tokenize(line); } catch (e) { return { out: '', err: 'syntax error: unterminated quote\n' }; }
      let stdin = '', errAll = '';
      for (const seg of segs) {
        const args = []; let quiet = false;
        for (const { t, g } of seg) {
          if (t === '2>/dev/null') quiet = true;
          else if (g && (t.includes('*') || t.includes('?'))) args.push(...this.glob(t));
          else args.push(t);
        }
        if (!args.length) return { out: '', err: 'syntax error near unexpected token `|\'\n' };
        const cmd = args[0], rest = args.slice(1);
        let out = '', err = '';
        if (!COMMANDS.includes(cmd)) err = `${cmd}: command not found\n`;
        else if (!this.allowed.has(cmd)) err = `${cmd}: not available on this level (type help)\n`;
        else {
          try { [out, err] = this['c_' + cmd](rest, stdin); }
          catch (e) {
            if (e instanceof UsageError) { out = ''; err = `${cmd}: ${e.message}\n`; }
            else throw e;
          }
        }
        if (!quiet) errAll += err;
        stdin = out;
      }
      return { out: stdin, err: errAll };
    }

    /* ---------- commands ---------- */
    c_pwd() { return [this.cwd + '\n', '']; }
    c_whoami() { return [this.user + '\n', '']; }
    c_id() {
      const g0 = this.groups[0];
      const gs = this.groups.map(g => `${g.gid}(${g.name})`).join(',');
      return [`uid=${this.uid}(${this.user}) gid=${g0.gid}(${g0.name}) groups=${gs}\n`, ''];
    }
    c_echo(a) { return [a.join(' ') + '\n', '']; }
    c_history() { return [this.history.map((c, i) => `${pad(i + 1, 5)}  ${c}\n`).join(''), '']; }
    c_cd(a) {
      const target = a.length ? a[0] : '~';
      const { node, err } = this.lookup(target);
      if (err === 'EACCES' || (node && node.type === 'dir' && !this.can(node, 'x'))) return ['', `cd: ${target}: Permission denied\n`];
      if (err || !node) return ['', `cd: ${target}: No such file or directory\n`];
      if (node.type !== 'dir') return ['', `cd: ${target}: Not a directory\n`];
      this.cwd = this.abspath(target);
      return ['', ''];
    }
    c_ls(a) {
      const flags = a.filter(isFlag).map(x => x.slice(1)).join('');
      const bad = flags.replace(/[al]/g, '');
      if (bad) throw new UsageError(`invalid option -- '${bad[0]}' (this game supports -a and -l)`);
      const paths = a.filter(x => !isFlag(x));
      if (!paths.length) paths.push('.');
      const all = flags.includes('a'), long = flags.includes('l');
      let out = '', err = '';
      const fmt = (n, name) => long
        ? `${n.type === 'dir' ? 'd' : '-'}${permsStr(n.perms)} 1 ${n.owner} ${n.group} ${pad(n.size, 6)} ${name}` : name;
      for (const p of paths) {
        const { node, err: e } = this.lookup(p);
        if (e === 'EACCES') { err += `ls: cannot access '${p}': Permission denied\n`; continue; }
        if (e) { err += `ls: cannot access '${p}': No such file or directory\n`; continue; }
        if (node.type === 'file') { out += fmt(node, p) + '\n'; continue; }
        if (!this.can(node, 'r')) { err += `ls: cannot open directory '${p}': Permission denied\n`; continue; }
        if (paths.length > 1) out += `${p}:\n`;
        const items = all ? [[node, '.'], [node, '..']] : [];
        const key = c => c.name.replace(/^\.+/, '').toLowerCase();
        node.children.slice().sort((x, y) => cmpStr(key(x), key(y))).forEach(c => {
          if (c.name.startsWith('.') && !all) return;
          items.push([c, c.name]);
        });
        out += items.map(([n, nm]) => fmt(n, nm) + '\n').join('');
      }
      return [out, err];
    }
    c_cat(a, s) { const [ins, err] = this.inputs('cat', a, s); return [ins.map(x => x[1]).join(''), err]; }
    c_less(a, s) { return this.c_cat(a, s); }
    _n(a) {
      let n = 10; const files = [];
      const num = v => { if (!/^\d+$/.test(v || '')) throw new UsageError(`invalid number of lines: '${v == null ? '' : v}'`); return Number(v); };
      for (let i = 0; i < a.length; i++) {
        if (a[i] === '-n') { n = num(a[i + 1]); i++; continue; }
        if (/^-n\d+$/.test(a[i])) n = Number(a[i].slice(2));
        else if (/^-\d+$/.test(a[i])) n = Number(a[i].slice(1));
        else files.push(a[i]);
      }
      return [n, files];
    }
    c_head(a, s) {
      const [n, files] = this._n(a); const [ins, err] = this.inputs('head', files, s);
      return [ins.map(([, c]) => joinLines(linesOf(c).slice(0, n))).join(''), err];
    }
    c_tail(a, s) {
      const [n, files] = this._n(a); const [ins, err] = this.inputs('tail', files, s);
      return [ins.map(([, c]) => joinLines(n ? linesOf(c).slice(-n) : [])).join(''), err];
    }
    c_file(a) {
      if (!a.length) throw new UsageError('missing file operand');
      let out = '';
      for (const p of a) {
        const { node, err } = this.lookup(p);
        if (err) { out += `${p}: cannot open \`${p}' (No such file or directory)\n`; continue; }
        if (node.type === 'dir') { out += `${p}: directory\n`; continue; }
        if (!this.can(node, 'r')) { out += `${p}: regular file, no read permission\n`; continue; }
        const c = node.content;
        let kind;
        if (c === '') kind = 'empty';
        else if (/^[\x20-\x7e\t\n]*$/.test(c)) kind = 'ASCII text';
        else kind = 'data';
        out += `${p}: ${kind}\n`;
      }
      return [out, ''];
    }
    c_find(a) {
      let i = 0; const starts = [];
      while (i < a.length && !(a[i].startsWith('-') || a[i] === '!')) starts.push(a[i++]);
      if (!starts.length) starts.push('.');
      const preds = []; let neg = false;
      while (i < a.length) {
        const t = a[i];
        if (t === '!') { neg = true; i++; continue; }
        if (['-name', '-type', '-size', '-user', '-group'].includes(t)) {
          const v = a[i + 1];
          if (v == null) return ['', `find: missing argument to \`${t}'\n`];
          if (t === '-type' && v !== 'f' && v !== 'd') return ['', `find: Unknown argument to -type: ${v} (use f or d)\n`];
          if (t === '-size' && !/^[+-]?\d+c$/.test(v)) return ['', `find: invalid argument \`${v}' to \`-size' (use bytes, like 33c)\n`];
          preds.push([neg, t, v]); i += 2;
        } else if (t === '-executable' || t === '-readable') { preds.push([neg, t, null]); i++; }
        else return ['', `find: unknown predicate \`${t}'\n`];
        neg = false;
      }
      const match = n => {
        for (const [ng, t, v] of preds) {
          let r;
          if (t === '-name') r = globRe(v).test(n.name);
          else if (t === '-type') r = v === 'd' ? n.type === 'dir' : n.type === 'file';
          else if (t === '-size') {
            const m = /^([+-]?)(\d+)c$/.exec(v), want = Number(m[2]);
            r = m[1] === '+' ? n.size > want : m[1] === '-' ? n.size < want : n.size === want;
          } else if (t === '-user') r = n.owner === v;
          else if (t === '-group') r = n.group === v;
          else if (t === '-executable') r = this.can(n, 'x');
          else r = this.can(n, 'r');
          if (ng) r = !r;
          if (!r) return false;
        }
        return true;
      };
      const out = []; let err = '';
      const walk = (n, path) => {
        if (match(n)) out.push(path);
        if (n.type === 'dir') {
          if (!(this.can(n, 'r') && this.can(n, 'x'))) { err += `find: '${path}': Permission denied\n`; return; }
          for (const c of n.children) walk(c, path !== '/' ? path.replace(/\/+$/, '') + '/' + c.name : '/' + c.name);
        }
      };
      for (const st of starts) {
        const { node, err: e } = this.lookup(st);
        if (e) { err += `find: '${st}': ${e === 'EACCES' ? 'Permission denied' : 'No such file or directory'}\n`; continue; }
        walk(node, st);
      }
      return [joinLines(out), err];
    }
    c_grep(a, s) {
      let flags = ''; const rest = [];
      for (const t of a) { if (isFlag(t) && !rest.length) flags += t.slice(1); else rest.push(t); }
      const bad = flags.replace(/[ivrn]/g, '');
      if (bad) throw new UsageError(`invalid option -- '${bad[0]}' (this game supports -i -v -r -n)`);
      if (!rest.length) throw new UsageError('usage: grep [-ivrn] PATTERN [FILE]...');
      const pat = rest[0]; let files = rest.slice(1);
      let rx;
      try { rx = new RegExp(pat, flags.includes('i') ? 'i' : ''); }
      catch (e) { throw new UsageError(`invalid pattern '${pat}'`); }
      const inv = flags.includes('v'), rec = flags.includes('r'), num = flags.includes('n');
      if (rec && !files.length) files = ['.'];
      let targets = [], err = '';
      if (rec) {
        const walk = (n, path) => {
          if (n.type === 'file') {
            if (this.can(n, 'r')) targets.push([path, n.content]); else err += `grep: ${path}: Permission denied\n`;
            return;
          }
          if (!(this.can(n, 'r') && this.can(n, 'x'))) { err += `grep: ${path}: Permission denied\n`; return; }
          n.children.slice().sort((x, y) => cmpStr(x.name, y.name)).forEach(c => walk(c, path.replace(/\/+$/, '') + '/' + c.name));
        };
        for (const f of files) {
          const { node, err: e } = this.lookup(f);
          if (e) { err += `grep: ${f}: No such file or directory\n`; continue; }
          walk(node, f);
        }
      } else {
        [targets, err] = this.inputs('grep', files, s);
      }
      const prefix = rec || files.length > 1;
      let out = '';
      for (const [name, c] of targets) {
        linesOf(c).forEach((l, k) => {
          if (rx.test(l) !== inv) out += (prefix && name ? name + ':' : '') + (num ? (k + 1) + ':' : '') + l + '\n';
        });
      }
      return [out, err];
    }
    _flags(a, ok, cmd) {
      const flags = a.filter(isFlag).map(t => t.slice(1)).join('');
      const bad = flags.replace(new RegExp('[' + ok + ']', 'g'), '');
      if (bad) throw new UsageError(`invalid option -- '${bad[0]}'`);
      return [flags, a.filter(t => !isFlag(t))];
    }
    c_sort(a, s) {
      const [flags, files] = this._flags(a, 'rnu');
      const [ins, err] = this.inputs('sort', files, s);
      let ls = [];
      ins.forEach(([, c]) => { ls = ls.concat(linesOf(c)); });
      if (flags.includes('n')) {
        const key = l => { const m = /^\s*(-?\d+)/.exec(l); return m ? Number(m[1]) : 0; };
        ls.sort((x, y) => (key(x) - key(y)) || cmpStr(x, y));
      } else ls.sort(cmpStr);
      if (flags.includes('r')) ls.reverse();
      if (flags.includes('u')) { const seen = new Set(); ls = ls.filter(l => (seen.has(l) ? false : (seen.add(l), true))); }
      return [joinLines(ls), err];
    }
    c_uniq(a, s) {
      const [flags, files] = this._flags(a, 'udc');
      const [ins, err] = this.inputs('uniq', files.slice(0, 1), s);
      let ls = [];
      ins.forEach(([, c]) => { ls = ls.concat(linesOf(c)); });
      let groups = [];
      for (const l of ls) {
        if (groups.length && groups[groups.length - 1][0] === l) groups[groups.length - 1][1]++;
        else groups.push([l, 1]);
      }
      if (flags.includes('u')) groups = groups.filter(g => g[1] === 1);
      if (flags.includes('d')) groups = groups.filter(g => g[1] > 1);
      if (flags.includes('c')) return [groups.map(([l, n]) => `${pad(n, 7)} ${l}\n`).join(''), err];
      return [groups.map(([l]) => l + '\n').join(''), err];
    }
    c_wc(a, s) {
      let [flags, files] = this._flags(a, 'lwc');
      flags = flags || 'lwc';
      const [ins, err] = this.inputs('wc', files, s);
      let out = '';
      for (const [name, c] of ins) {
        const vals = [];
        if (flags.includes('l')) vals.push((c.match(/\n/g) || []).length);
        if (flags.includes('w')) vals.push(c.split(WS).filter(Boolean).length);
        if (flags.includes('c')) vals.push(c.length);
        out += vals.join(' ') + (name ? ' ' + name : '') + '\n';
      }
      return [out, err];
    }
    c_strings(a, s) {
      let n = 4; const files = [];
      for (let i = 0; i < a.length; i++) {
        if (a[i] === '-n') {
          if (!/^\d+$/.test(a[i + 1] || '') || Number(a[i + 1]) < 1) throw new UsageError(`invalid minimum string length '${a[i + 1] || ''}'`);
          n = Number(a[++i]); continue;
        }
        files.push(a[i]);
      }
      const [ins, err] = this.inputs('strings', files, s);
      const re = new RegExp('[\\x20-\\x7e\\t]{' + n + ',}', 'g');
      let out = [];
      ins.forEach(([, c]) => { out = out.concat(c.match(re) || []); });
      return [joinLines(out), err];
    }
    c_base64(a, s) {
      if (!a.includes('-d') && !a.includes('--decode')) return ['', 'base64: only decoding (-d) is supported in this game\n'];
      const files = a.filter(t => t !== '-d' && t !== '--decode');
      const [ins, err0] = this.inputs('base64', files, s);
      let out = '', err = err0;
      for (const [, c] of ins) {
        const d = b64decode(c.split(WS).join(''));
        if (d === null) err += 'base64: invalid input\n'; else out += d;
      }
      return [out, err];
    }
    c_chmod(a) {
      if (!a.length) throw new UsageError('missing operand');
      const mode = a[0], files = a.slice(1);
      if (!files.length) throw new UsageError(`missing operand after '${mode}'`);
      let err = '';
      for (const f of files) {
        const { node, err: e } = this.lookup(f);
        if (e) { err += `chmod: cannot access '${f}': No such file or directory\n`; continue; }
        if (node.owner !== this.user && this.user !== 'root') { err += `chmod: changing permissions of '${f}': Operation not permitted\n`; continue; }
        let p = permsStr(node.perms).split('');
        if (/^[0-7]{3,4}$/.test(mode)) p = permsStr(mode.slice(-3)).split('');
        else {
          for (const clause of mode.split(',')) {
            const m = /^([ugoa]*)([+\-=])([rwx]*)$/.exec(clause);
            if (!m) return ['', `chmod: invalid mode: '${mode}'\n`];
            let who = m[1] || 'a';
            if (who.includes('a')) who = 'ugo';
            for (const w of who) {
              const base = { u: 0, g: 3, o: 6 }[w];
              'rwx'.split('').forEach((b, k) => {
                if (m[2] === '=') p[base + k] = m[3].includes(b) ? b : '-';
                else if (m[3].includes(b)) p[base + k] = m[2] === '+' ? b : '-';
              });
            }
          }
        }
        node.perms = p.join('');
      }
      return ['', err];
    }

    /* ---------- prompt and Tab completion ---------- */
    shortCwd() {
      if (this.cwd === this.home) return '~';
      if (this.cwd.startsWith(this.home + '/')) return '~' + this.cwd.slice(this.home.length);
      return this.cwd;
    }
    /* Returns {line, options}. options lists every match when there is more than one. */
    complete(line, extraCmds) {
      let start = 0, q = null, segStart = 0;
      for (let i = 0; i < line.length; i++) {
        const c = line[i];
        if (q) { if (c === q) q = null; continue; }
        if (c === '\\') { i++; continue; }
        if (c === "'" || c === '"') { q = c; continue; }
        if (/\s/.test(c)) start = i + 1;
        if (c === '|') { start = i + 1; segStart = i + 1; }
      }
      const raw = line.slice(start);
      let quote = null, word = '';
      for (let i = 0; i < raw.length; i++) {
        const c = raw[i];
        if (quote) { if (c === quote) quote = null; else word += c; }
        else if (c === "'" || c === '"') quote = c;
        else if (c === '\\' && i + 1 < raw.length) word += raw[++i];
        else word += c;
      }
      const before = line.slice(segStart, start).trim();
      const head = line.slice(0, start);
      const enc = (txt, done) => {
        if (quote) return quote + txt + (done ? quote + ' ' : '');
        return txt.replace(/([\s'"\\|*?])/g, '\\$1') + (done ? ' ' : '');
      };
      let cands = [];
      if (!before) {
        cands = this.commandNames().concat(extraCmds || []).filter(c => c.startsWith(word)).map(c => ({ v: c, dir: false }));
        cands = cands.filter((c, i, arr) => arr.findIndex(x => x.v === c.v) === i);
      } else {
        const k = word.lastIndexOf('/');
        const dirPart = k >= 0 ? word.slice(0, k + 1) : '';
        const base = k >= 0 ? word.slice(k + 1) : word;
        const { node, err } = this.lookup(dirPart || '.');
        if (!err && node && node.type === 'dir' && this.can(node, 'r')) {
          cands = node.children
            .filter(c => c.name.startsWith(base) && (base.startsWith('.') || !c.name.startsWith('.')))
            .map(c => ({ v: dirPart + c.name, dir: c.type === 'dir', name: c.name + (c.type === 'dir' ? '/' : '') }))
            .sort((x, y) => cmpStr(x.v, y.v));
        }
      }
      if (!cands.length) return { line, options: [] };
      if (cands.length === 1) {
        const c = cands[0];
        return { line: head + (c.dir ? enc(c.v + '/', false) : enc(c.v, true)), options: [] };
      }
      let pre = cands[0].v;
      for (const c of cands) while (!c.v.startsWith(pre)) pre = pre.slice(0, -1);
      const out = pre.length > word.length ? head + enc(pre, false) : line;
      return { line: out, options: cands.map(c => c.name || c.v) };
    }
  }

  function b64decode(str) {
    if (str.length % 4 !== 0 || !/^[A-Za-z0-9+/]*={0,2}$/.test(str)) return null;
    const A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    let out = '';
    for (let i = 0; i < str.length; i += 4) {
      const c = [0, 1, 2, 3].map(k => (str[i + k] === '=' ? -1 : A.indexOf(str[i + k])));
      if (c[0] < 0 || c[1] < 0 || (c[2] < 0 && c[3] >= 0)) return null;
      const n = (c[0] << 18) | (c[1] << 12) | ((c[2] < 0 ? 0 : c[2]) << 6) | (c[3] < 0 ? 0 : c[3]);
      out += String.fromCharCode((n >> 16) & 255);
      if (c[2] >= 0) out += String.fromCharCode((n >> 8) & 255);
      if (c[3] >= 0) out += String.fromCharCode(n & 255);
    }
    return out;
  }

  /* SHA-256 hex of a UTF-8 string. Uses Web Crypto when present, else a small pure JS version. */
  function sha256Sync(msg) {
    const bytes = Array.from(unescape(encodeURIComponent(msg)), c => c.charCodeAt(0));
    const K = [], H = [];
    const isPrime = n => { for (let f = 2; f * f <= n; f++) if (n % f === 0) return false; return true; };
    for (let n = 2, c = 0; c < 64; n++) {
      if (!isPrime(n)) continue;
      if (c < 8) H[c] = (Math.pow(n, 1 / 2) % 1) * 4294967296 | 0;
      K[c++] = (Math.pow(n, 1 / 3) % 1) * 4294967296 | 0;
    }
    const bitLen = bytes.length * 8;
    bytes.push(0x80);
    while (bytes.length % 64 !== 56) bytes.push(0);
    for (let i = 7; i >= 0; i--) bytes.push(i >= 4 ? 0 : (bitLen >>> (i * 8)) & 255);
    const rot = (x, n) => (x >>> n) | (x << (32 - n));
    for (let o = 0; o < bytes.length; o += 64) {
      const w = [];
      for (let i = 0; i < 16; i++) w[i] = (bytes[o + 4 * i] << 24) | (bytes[o + 4 * i + 1] << 16) | (bytes[o + 4 * i + 2] << 8) | bytes[o + 4 * i + 3];
      for (let i = 16; i < 64; i++) {
        const s0 = rot(w[i - 15], 7) ^ rot(w[i - 15], 18) ^ (w[i - 15] >>> 3);
        const s1 = rot(w[i - 2], 17) ^ rot(w[i - 2], 19) ^ (w[i - 2] >>> 10);
        w[i] = (w[i - 16] + s0 + w[i - 7] + s1) | 0;
      }
      let [a, b, c, d, e, f, g, h] = H;
      for (let i = 0; i < 64; i++) {
        const t1 = (h + (rot(e, 6) ^ rot(e, 11) ^ rot(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i]) | 0;
        const t2 = ((rot(a, 2) ^ rot(a, 13) ^ rot(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) | 0;
        h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0;
      }
      H[0] = (H[0] + a) | 0; H[1] = (H[1] + b) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0;
      H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
    }
    return H.map(x => ('00000000' + (x >>> 0).toString(16)).slice(-8)).join('');
  }
  async function sha256(msg) {
    try {
      const c = (typeof crypto !== 'undefined' && crypto.subtle) ? crypto.subtle : null;
      if (c) {
        const buf = await c.digest('SHA-256', new TextEncoder().encode(msg));
        return Array.from(new Uint8Array(buf), b => b.toString(16).padStart(2, '0')).join('');
      }
    } catch (e) { /* fall through */ }
    return sha256Sync(msg);
  }

  /* ======================= UI ======================= */

  const STORE = 'cwm-wargame-v1';
  const HINT_COST = 25, LEVEL_POINTS = 100;
  const HELP = {
    ls: 'list files (-a hidden, -l long)', cd: 'change directory', pwd: 'print working directory',
    whoami: 'print your user name', id: 'print user and groups', history: 'show earlier commands',
    echo: 'print words', cat: 'print files', less: 'print a file (works like cat here)',
    head: 'first lines (-n N)', tail: 'last lines (-n N)', file: 'guess a file type',
    find: 'search files (-name -type -size -user -group -executable -readable !)',
    grep: 'match lines (-i -v -r -n)', sort: 'sort lines (-r -n -u)', uniq: 'collapse repeats (-u -d -c)',
    wc: 'count lines, words, bytes (-l -w -c)', strings: 'printable text in binary data (-n N)',
    base64: 'decode base64 (-d)', chmod: 'change permissions (octal or u+r style)'
  };

  function boot() {
    const app = document.getElementById('wg-app');
    if (!app) return;
    const $ = (s, r) => (r || document).querySelector(s);
    const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };

    const screen = $('#wg-screen'), out = $('#wg-output'), input = $('#wg-input'), promptEl = $('#wg-prompt');
    const list = $('#wg-levels'), form = $('#wg-pass-form'), pass = $('#wg-pass'), passMsg = $('#wg-pass-msg');
    let levels = [], shell = null, cur = 0, hist = [], hpos = 0, draft = '';
    let state = load();

    function load() {
      try { const s = JSON.parse(localStorage.getItem(STORE) || 'null'); if (s && s.v === 1) return s; } catch (e) { /* ignore */ }
      return { v: 1, solved: {}, hints: {}, current: 0, started: null, finished: null };
    }
    function save() { try { localStorage.setItem(STORE, JSON.stringify(state)); } catch (e) { /* private mode */ } }
    const isSolved = i => !!state.solved[levels[i].id];
    const isUnlocked = i => i === 0 || isSolved(i - 1);
    const levelNo = i => String(i).padStart(2, '0');
    const score = () => levels.reduce((t, l) => t + (state.solved[l.id] ? LEVEL_POINTS - (state.solved[l.id].hint ? HINT_COST : 0) : 0), 0);

    const SAFE = s => s.replace(/[\x00-\x08\x0b-\x1f\x7f-\x9f]/g, '\uFFFD');
    function print(text, cls) {
      if (!text) return;
      const n = el('span', cls || null, SAFE(text));
      out.append(n);
      while (out.childNodes.length > 600) out.removeChild(out.firstChild);
      screen.scrollTop = screen.scrollHeight;
    }
    function echoLine(line) {
      const p = el('span', 'wg-line');
      p.append(el('span', 'wg-ps', promptText()), document.createTextNode(' ' + line + '\n'));
      out.append(p);
    }
    function promptText() { return `level${levelNo(cur)}@cwm:${shell ? shell.shortCwd() : '~'}$`; }
    function refreshPrompt() { promptEl.textContent = promptText(); $('#wg-title').textContent = `level${levelNo(cur)}@cwm: ${shell.shortCwd()}`; }

    function renderList() {
      list.textContent = '';
      levels.forEach((l, i) => {
        const li = el('li');
        const b = el('button', 'wg-lvl');
        b.type = 'button';
        const st = isSolved(i) ? 'done' : isUnlocked(i) ? 'open' : 'locked';
        b.dataset.state = st;
        if (i === cur) b.setAttribute('aria-current', 'true');
        b.disabled = st === 'locked';
        b.append(el('span', 'wg-lvl-n mono', levelNo(i)), el('span', 'wg-lvl-t', l.title),
          el('span', 'wg-lvl-s', st === 'done' ? '\u2713' : st === 'locked' ? '\uD83D\uDD12' : '\u203A'));
        b.setAttribute('aria-label', `${levelNo(i)} ${l.title}, ${st === 'done' ? 'solved' : st === 'locked' ? 'locked' : 'open'}`);
        b.addEventListener('click', () => { select(i); if (window.matchMedia('(max-width: 900px)').matches) input.focus({ preventScroll: true }); });
        li.append(b); list.append(li);
      });
      const done = levels.filter((_, i) => isSolved(i)).length;
      $('#wg-progress-n').textContent = `${done}/${levels.length}`;
      $('#wg-progress-bar').style.width = (done / levels.length * 100) + '%';
      $('#wg-score').textContent = String(score());
      $('#wg-results-btn').hidden = done < levels.length;
    }

    function select(i, quiet) {
      if (!isUnlocked(i)) return;
      cur = i; state.current = i; save();
      const l = levels[i];
      shell = new Shell(l);
      $('#wg-lvl-kicker').textContent = `Level ${levelNo(i)} of ${levelNo(levels.length - 1)}`;
      $('#wg-lvl-title').textContent = l.title;
      $('#wg-lvl-goal').textContent = l.goal;
      const hint = $('#wg-hint'), hb = $('#wg-hint-btn');
      hint.textContent = l.hint;
      hint.hidden = !state.hints[l.id];
      hb.textContent = state.hints[l.id] ? 'Hint shown' : `Show hint (costs ${HINT_COST} points)`;
      hb.disabled = !!state.hints[l.id];
      const man = $('#wg-man');
      man.href = l.man_url;
      man.textContent = 'man ' + (l.man_url.match(/man1\/([^.]+)\./) || [, 'page'])[1];
      $('#wg-cmds').textContent = l.allowed_cmds.join(', ');
      $('#wg-pass-label').textContent = i === levels.length - 1 ? 'Final password' : `Password for level ${levelNo(i + 1)}`;
      pass.value = ''; passMsg.textContent = ''; passMsg.className = 'wg-pass-msg small';
      out.textContent = '';
      if (!quiet) {
        print(`CyberWithMadhav training box. Simulated shell: nothing here runs on a real system.\n`, 'wg-dim');
        print(`Level ${levelNo(i)}: ${l.title}\n`, 'wg-hi');
        print(`${l.goal}\n`);
        print(`Type help for the commands on this level. Submit the password in the box below.\n\n`, 'wg-dim');
      }
      refreshPrompt(); renderList();
    }

    function runLine(line) {
      echoLine(line);
      const trimmed = line.trim();
      if (trimmed) { hist.push(line); if (hist.length > 200) hist.shift(); }
      hpos = hist.length; draft = '';
      if (!trimmed) { screen.scrollTop = screen.scrollHeight; return; }
      const word = trimmed.split(/\s+/)[0];
      if (trimmed === 'clear') { shell.history.push(line); out.textContent = ''; return; }
      if (trimmed === 'help') {
        shell.history.push(line);
        print('Commands on this level:\n', 'wg-hi');
        print(shell.commandNames().map(c => `  ${c.padEnd(9)}${HELP[c]}`).join('\n') + '\n');
        print('  clear    clear the screen (or Ctrl+L)\n  help     this list\n', 'wg-dim');
        print('Shell: pipes |, quotes, backslash escapes, * and ? wildcards, 2>/dev/null. Up and down arrows for history, Tab to complete.\n', 'wg-dim');
        return;
      }
      if (word === 'sudo' || word === 'su') { shell.history.push(line); print(`${word}: you are a cadet here, not root. Nice try.\n`, 'wg-err'); return; }
      const r = shell.run(line);
      print(r.err, 'wg-err'); print(r.out);
      refreshPrompt();
    }

    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); const v = input.value; input.value = ''; runLine(v); return; }
      if (e.key === 'ArrowUp') { e.preventDefault(); if (hpos === hist.length) draft = input.value; if (hpos > 0) { hpos--; input.value = hist[hpos]; } moveEnd(); return; }
      if (e.key === 'ArrowDown') { e.preventDefault(); if (hpos < hist.length) { hpos++; input.value = hpos === hist.length ? draft : hist[hpos]; } moveEnd(); return; }
      if (e.key === 'Tab') { e.preventDefault(); tab(); return; }
      if (e.ctrlKey && (e.key === 'l' || e.key === 'L')) { e.preventDefault(); out.textContent = ''; return; }
      if (e.ctrlKey && (e.key === 'c' || e.key === 'C') && !input.value.slice(input.selectionStart, input.selectionEnd)) {
        e.preventDefault(); echoLine(input.value + '^C'); input.value = ''; hpos = hist.length;
      }
    });
    function moveEnd() { requestAnimationFrame(() => { const n = input.value.length; input.setSelectionRange(n, n); }); }
    function tab() {
      const r = shell.complete(input.value, ['help', 'clear']);
      if (r.options.length && r.line === input.value) {
        echoLine(input.value);
        print(r.options.join('   ') + '\n', 'wg-dim');
      }
      input.value = r.line; moveEnd();
    }
    screen.addEventListener('click', () => { if (!window.getSelection().toString()) input.focus({ preventScroll: true }); });

    /* on screen keys for phones */
    document.querySelectorAll('[data-key]').forEach(b => b.addEventListener('click', () => {
      const k = b.dataset.key;
      if (k === 'tab') tab();
      else if (k === 'up' || k === 'down') input.dispatchEvent(new KeyboardEvent('keydown', { key: k === 'up' ? 'ArrowUp' : 'ArrowDown', bubbles: true }));
      else if (k === 'clear') out.textContent = '';
      else if (k === 'enter') { const v = input.value; input.value = ''; runLine(v); }
      else { const s = input.selectionStart ?? input.value.length; input.value = input.value.slice(0, s) + k + input.value.slice(input.selectionEnd ?? s); input.setSelectionRange(s + k.length, s + k.length); }
      input.focus({ preventScroll: true });
    }));

    $('#wg-hint-btn').addEventListener('click', () => {
      const l = levels[cur], hb = $('#wg-hint-btn');
      if (!state.solved[l.id]) state.hints[l.id] = true;
      save();
      $('#wg-hint').hidden = false;
      hb.textContent = 'Hint shown'; hb.disabled = true;
      print(`Hint: ${l.hint}\n`, 'wg-dim');
    });
    $('#wg-reset-level').addEventListener('click', () => { select(cur); input.focus({ preventScroll: true }); });
    $('#wg-day').addEventListener('click', () => { const t = document.querySelector('.theme-toggle'); if (t) t.click(); else { const d = document.documentElement; d.setAttribute('data-theme', d.getAttribute('data-theme') === 'light' ? 'dark' : 'light'); } });

    form.addEventListener('submit', async e => {
      e.preventDefault();
      const v = pass.value.trim();
      if (!v) return;
      const l = levels[cur];
      const ok = (await sha256(v)) === l.password_sha256;
      if (!ok) { passMsg.textContent = 'Not quite. That is not the password for this level.'; passMsg.className = 'wg-pass-msg small bad'; form.classList.remove('shake'); void form.offsetWidth; form.classList.add('shake'); return; }
      const first = !state.solved[l.id];
      if (!state.started) state.started = Date.now();
      if (first) state.solved[l.id] = { at: Date.now(), hint: !!state.hints[l.id] };
      save();
      toast(`Concept learned: ${l.concept_taught}`);
      const all = levels.every((_, i) => isSolved(i));
      if (all && !state.finished) { state.finished = Date.now(); save(); }
      if (cur < levels.length - 1) {
        select(cur + 1);
        print(`Level ${levelNo(cur - 1)} cleared. ${first ? '+' + (LEVEL_POINTS - (state.hints[levels[cur - 1].id] ? HINT_COST : 0)) + ' points.' : ''}\n\n`, 'wg-ok');
        input.focus({ preventScroll: true });
      } else { renderList(); passMsg.textContent = 'Correct. You finished the wargame!'; passMsg.className = 'wg-pass-msg small good'; }
      if (all) showDone();
    });

    let toastT;
    function toast(msg) {
      const t = $('#wg-toast');
      t.textContent = msg; t.hidden = false;
      requestAnimationFrame(() => t.classList.add('show'));
      clearTimeout(toastT);
      toastT = setTimeout(() => { t.classList.remove('show'); setTimeout(() => { t.hidden = true; }, 350); }, 3200);
    }

    function showDone() {
      const d = $('#wg-done');
      const hints = levels.filter(l => state.solved[l.id] && state.solved[l.id].hint).length;
      const max = levels.length * LEVEL_POINTS, sc = score();
      $('#wg-done-score').textContent = `${sc} / ${max}`;
      $('#wg-done-hints').textContent = String(hints);
      let mins = 0;
      const times = levels.map(l => state.solved[l.id] && state.solved[l.id].at).filter(Boolean);
      if (state.started && times.length) mins = Math.max(1, Math.round((Math.max(...times) - Math.min(state.started, ...times)) / 60000));
      $('#wg-done-time').textContent = mins >= 60 ? `${Math.floor(mins / 60)} h ${mins % 60} min` : `${mins} min`;
      const pct = sc / max;
      $('#wg-done-rank').textContent = pct === 1 ? 'Root Whisperer: a perfect run with no hints.' : pct >= 0.85 ? 'Shell Ninja: almost flawless.' : pct >= 0.6 ? 'Terminal Operator: solid work.' : 'Cadet Graduate: every level cleared.';
      const ul = $('#wg-done-concepts'); ul.textContent = '';
      levels.forEach(l => ul.append(el('li', null, l.concept_taught)));
      d.hidden = false;
      $('#wg-done-close').focus();
    }
    $('#wg-done-close').addEventListener('click', () => { $('#wg-done').hidden = true; input.focus({ preventScroll: true }); });
    $('#wg-results-btn').addEventListener('click', showDone);
    $('#wg-reset-all').addEventListener('click', () => {
      if (!confirm('Reset all wargame progress on this device?')) return;
      state = { v: 1, solved: {}, hints: {}, current: 0, started: null, finished: null }; save();
      $('#wg-done').hidden = true; select(0);
    });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$('#wg-done').hidden) $('#wg-done').hidden = true; });

    fetch('data/terminal_wargame.json', { cache: 'no-cache' })
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(d => {
        levels = d.levels;
        let i = Math.min(state.current || 0, levels.length - 1);
        while (i > 0 && !isUnlocked(i)) i--;
        app.classList.add('ready');
        select(i);
      })
      .catch(() => { print('Could not load the level data. Check your connection and reload the page.\n', 'wg-err'); });
  }

  return { Shell, tokenize, permsStr, b64decode, sha256, sha256Sync, COMMANDS, boot };
});
