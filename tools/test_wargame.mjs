// Terminal Wargame tests. Run: node tools/test_wargame.mjs
// Replays every level's intended solution through the browser engine, checks the
// SHA-256 of the password found against the data file, and checks wrong shortcuts fail.
import { createRequire } from 'node:module';
import { readFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const W = require(path.join(ROOT, 'assets/js/wargame.js'));
const DATA = JSON.parse(readFileSync(path.join(ROOT, 'data/terminal_wargame.json'), 'utf8'));
const byId = Object.fromEntries(DATA.levels.map(l => [l.id, l]));
const sha = s => createHash('sha256').update(s).digest('hex');

let pass = 0, fail = 0;
const ok = (cond, msg) => { if (cond) pass++; else { fail++; console.log('  FAIL ' + msg); } };
const tokens = s => (s.match(/[A-Za-z0-9]{32}/g) || []);
const leaks = (out, l) => tokens(out).some(t => sha(t) === l.password_sha256);

const SOLUTIONS = {
  lvl00: ['ls', 'cat readme'],
  lvl01: ['ls', 'cat ./-'],
  lvl02: ['ls', 'cat "spaces in this filename"'],
  lvl03: ['ls -a inhere', 'cat inhere/.hidden_from_you'],
  lvl04: ['file inhere/*', 'cat inhere/-file07'],
  lvl05: ['find inhere -type f -size 1033c ! -executable', 'cat inhere/dir03/.file2'],
  lvl06: ['find / -user cadet07 -group cadet06 -size 33c 2>/dev/null', 'cat /var/lib/misc/.ledger'],
  lvl07: ['grep millionth data.txt'],
  lvl08: ['sort data.txt | uniq -u'],
  lvl09: ['strings data.bin | grep ===='],
  lvl10: ['base64 -d data.txt'],
  lvl11: ['ls -l', 'chmod u+r secret.txt', 'cat secret.txt'],
  lvl12: ['tail -n 3 events.log | head -n 1'],
  lvl13: ['wc -l roster.txt', 'cat vault/slot_137'],
  lvl14: ['history', 'cat /var/backups/.handover_cadet15'],
  lvl15: ['id', 'ls -l /srv/shared', 'cat /srv/shared/auditors_report.txt'],
  lvl16: ['grep -r deploy_key: projects'],
  lvl17: ['cd "old backups"', 'ls -a', 'base64 -d .stash.b64 | base64 -d'],
  lvl18: ['grep -i token notes.txt | grep -v expired | grep -v revoked'],
  lvl19: ['find / -user cadet19 -name "*.b64" 2>/dev/null', 'chmod 400 "/opt/drop zone/.cache/manifest.b64"', 'base64 -d "/opt/drop zone/.cache/manifest.b64" | sort | uniq -u'],
};

console.log('1. Data file');
ok(DATA.levels.length === 20, '20 levels');
for (const l of DATA.levels) {
  ok(/^[0-9a-f]{64}$/.test(l.password_sha256 || ''), `${l.id} has password_sha256`);
  ok(!('password_for_next' in l) && !('solution_cmds' in l), `${l.id} ships no plaintext answers`);
  ok(Array.isArray(l.allowed_cmds) && l.fs && l.fs.user, `${l.id} has allowed_cmds and fs`);
}
const src = '/workspace/cwm-content/terminal_wargame.json';
if (existsSync(src)) {
  const S = JSON.parse(readFileSync(src, 'utf8'));
  for (const l of S.levels) {
    ok(JSON.stringify(l.fs) === JSON.stringify(byId[l.id].fs), `${l.id} fs identical to source`);
    ok(sha(l.password_for_next) === byId[l.id].password_sha256, `${l.id} hash matches source password`);
    ok(JSON.stringify(l.solution_cmds) === JSON.stringify(SOLUTIONS[l.id]), `${l.id} solution list matches source`);
  }
  console.log('   cross checked against source data');
}

console.log('2. Solutions replay');
for (const l of DATA.levels) {
  const sh = new W.Shell(l);
  let last = { out: '', err: '' }, found = false;
  for (const c of SOLUTIONS[l.id]) {
    last = sh.run(c);
    const expected = l.id === 'lvl16' ? /^(grep: \S+: Permission denied\n)*$/ : /^$/;
    ok(expected.test(last.err), `${l.id} "${c}" has no unexpected error: ${last.err.trim()}`);
  }
  found = leaks(last.out, l);
  ok(found, `${l.id} final command prints the password`);
  console.log(`   ${l.id} ${found ? 'ok' : 'MISSING'}  ${l.title}`);
}

console.log('3. Wrong shortcuts must not reveal the password');
const BAD = {
  lvl01: ['cat -'],
  lvl02: ['cat spaces in this filename'],
  lvl03: ['ls inhere', 'cat inhere/*'],
  lvl11: ['cat secret.txt'],
  lvl15: ['cat /srv/shared/netops_report.txt'],
  lvl18: ['grep token notes.txt | grep -v expired | grep -v revoked'],
  lvl19: ['base64 -d "/opt/drop zone/.cache/manifest.b64" | sort | uniq -u'],
};
for (const [id, cmds] of Object.entries(BAD)) {
  for (const c of cmds) {
    const r = new W.Shell(byId[id]).run(c);
    ok(!leaks(r.out, byId[id]), `${id} wrong shortcut "${c}" must not leak`);
  }
}

console.log('4. Engine behaviour');
const L = id => new W.Shell(byId[id]);
const ALL = id => new W.Shell({ ...byId[id], allowed_cmds: W.COMMANDS });
{ const r = L('lvl00').run('grep x readme');
  ok(/not available/i.test(r.err) || /command not found/.test(r.err), 'disallowed command is refused'); }
{ const r = L('lvl00').run('python3 -c 1'); ok(/command not found/.test(r.err), 'unknown command not found'); }
{ const r = L('lvl00').run('ls -z'); ok(/invalid option/.test(r.err), 'unsupported flag refused'); }
{ const r = L('lvl06').run('find / -user cadet07 -group cadet06 -size 33c');
  ok(/Permission denied/.test(r.err), 'find shows permission errors without redirect');
  const r2 = L('lvl06').run('find / -user cadet07 -group cadet06 -size 33c 2>/dev/null');
  ok(r2.err === '' && r2.out.includes('/var/lib/misc/.ledger'), '2>/dev/null hides errors'); }
{ const sh = L('lvl19'); const r = sh.run('chmod 777 /etc');
  ok(/Operation not permitted/.test(r.err), 'chmod on a file you do not own fails'); }
{ const sh = L('lvl11'); const r = sh.run('cat secret.txt');
  ok(/Permission denied/.test(r.err), 'owner without r cannot read'); }
{ const r = L('lvl03').run('ls inhere/*'); ok(!r.out.includes('.hidden'), 'glob skips dotfiles');
  const r2 = L('lvl03').run('ls -a inhere/.*'); ok(r2.out.includes('.hidden_from_you') || r2.err === '', 'dot glob matches dotfiles'); }
{ const r = L('lvl02').run('cat "unterminated'); ok(/unexpected EOF|unterminated|syntax/i.test(r.err), 'unterminated quote errors'); }
{ const r = L('lvl00').run('ls | | cat'); ok(/syntax error/.test(r.err), 'empty pipe segment is a syntax error'); }
{ const r = ALL('lvl00').run("echo 'a  b' c\\ d *"); ok(r.out.startsWith('a  b c d '), 'quotes and escapes'); }
{ const r = ALL('lvl00').run("echo '*'"); ok(r.out === '*\n', 'quoted star is literal'); }
{ const sh = L('lvl15'); const r = sh.run('cat /root/x'); ok(/Permission denied|No such/.test(r.err), 'x needed to traverse /root'); }
{ const sh = L('lvl00'); const c = sh.complete('cat rea'); ok(c.line === 'cat readme ', 'Tab completes file names');
  const c2 = sh.complete('wh'); ok(c2.line === 'whoami ', 'Tab completes command names'); }
{ const sh = L('lvl17'); const c = sh.complete('cd old'); ok(c.line === 'cd old\\ backups/', 'Tab escapes spaces in names'); }
{ const sh = L('lvl12'); ok(sh.run('tail -n 0 events.log').out === '', 'tail -n 0 prints nothing'); }
{ const sh = L('lvl00'); ok(sh.shortCwd() === '~', 'prompt shows ~ at home'); sh.run('cd /'); ok(sh.shortCwd() === '/', 'cd / works'); }

console.log('5. Source hygiene');
const files = ['terminal.html', 'assets/js/wargame.js', 'assets/css/wargame.css', 'data/terminal_wargame.json', 'tools/test_wargame.mjs'];
const DASH = new RegExp('[\\u2013\\u2014]');
for (const f of files) ok(!DASH.test(readFileSync(path.join(ROOT, f), 'utf8')), `${f} has no en or em dash`);
const js = readFileSync(path.join(ROOT, 'assets/js/wargame.js'), 'utf8');
ok(!/\beval\s*\(/.test(js) && !/new\s+Function/.test(js) && !/innerHTML/.test(js), 'engine has no eval, Function or innerHTML');
const html = readFileSync(path.join(ROOT, 'terminal.html'), 'utf8');
ok(!/\sstyle="/.test(html), 'no inline style attributes (CSP)');
const inline = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => 'sha256-' + createHash('sha256').update(m[1]).digest('base64'));
const csp = (html.match(/Content-Security-Policy" content="([^"]+)"/) || [])[1] || '';
ok(inline.length >= 1 && inline.every(h => csp.includes(h)), 'every inline script hash is in the CSP');
for (const id of ['wg-output', 'wg-input', 'wg-prompt', 'wg-levels', 'wg-pass-form', 'wg-toast', 'wg-done', 'wg-hint-btn', 'wg-man'])
  ok(html.includes(`id="${id}"`), `terminal.html has #${id}`);

console.log(`\n${fail ? 'FAILED' : 'PASSED'}: ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
