"""Stage 1 lessons, part B: Windows for security, networking primer. Original writing for CyberWithMadhav."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from learn_kit import *

PTREE = svg(720, 300, ARROWDEF +
  box(290, 12, 140, 40, "s-p", "System", "PID 4", 8) +
  box(290, 76, 140, 40, "s-n", "smss.exe", "session manager", 8) +
  box(40, 150, 150, 40, "s-n", "csrss.exe", "one per session", 8) + box(220, 150, 150, 40, "s-n", "wininit.exe", "session 0", 8) + box(520, 150, 160, 40, "s-n", "winlogon.exe", "logon session", 8) +
  box(130, 226, 150, 40, "s-g", "services.exe", "service control", 8) + box(300, 226, 140, 40, "s-r", "lsass.exe", "logins, secrets", 8) + box(520, 226, 160, 40, "s-n", "userinit.exe", "then explorer.exe", 8) +
  box(20, 256, 100, 36, "s-n", "svchost.exe", None, 8) +
  arrow(360, 52, 360, 74) + arrow(330, 116, 120, 148) + arrow(360, 116, 300, 148) + arrow(400, 116, 590, 148) +
  arrow(280, 190, 210, 224) + arrow(310, 190, 360, 224) + arrow(600, 190, 600, 224) + arrow(160, 266, 122, 272),
  "Normal Windows startup process tree: System, smss.exe, then csrss.exe, wininit.exe and winlogon.exe; wininit starts services.exe and lsass.exe; services.exe starts svchost.exe")

def lesson_windows():
  S = []
  S.append(dict(id="architecture", h="Know normal: the Windows process family", hi_h="Normal pehchano: Windows ke core processes",
    body=f'''<p>Most Indian offices, colleges and government departments run Windows, so most incidents you investigate will touch it. The first skill is not a fancy tool; it is knowing what a <strong>healthy</strong> Windows machine looks like, so the odd thing jumps out.</p>
{fig(PTREE, "smss.exe creates per session copies of itself that exit, so csrss.exe, wininit.exe and winlogon.exe normally show no living parent.", "Windows process tree")}
{table(["Process", "Normal location", "Normal parent", "How many", "Notes"], [
  ["System", "kernel, no file", "none", "1", "always PID 4"],
  ["smss.exe", "C:\\Windows\\System32", "System", "1 lasting copy", "first user mode process"],
  ["csrss.exe", "C:\\Windows\\System32", "smss.exe (exited)", "2 or more", "one per session"],
  ["wininit.exe", "C:\\Windows\\System32", "smss.exe (exited)", "1", "starts services.exe and lsass.exe"],
  ["services.exe", "C:\\Windows\\System32", "wininit.exe", "1", "Service Control Manager"],
  ["lsass.exe", "C:\\Windows\\System32", "wininit.exe", "1", "checks passwords, holds credentials; never more than one"],
  ["svchost.exe", "C:\\Windows\\System32", "services.exe", "many", "hosts services; launched with <code>-k</code> group arguments"],
  ["explorer.exe", "C:\\Windows", "userinit.exe (exited)", "one per logged in user", "the desktop and taskbar"]],
  "Normal Windows processes")}
{attack("<p>Malware hides in plain sight: a second <code>lsass.exe</code>, an <code>svchost.exe</code> whose parent is not services.exe, <code>scvhost.exe</code> with letters swapped, or a correct name running from <code>C:\\Users\\Public</code> or <code>AppData</code>. Credential stealers also open handles to the real lsass.exe to read its memory.</p>")}
{defend("<p>Compare against this table. Microsoft's <strong>Credential Guard</strong> and running LSASS as a protected process (<em>LSA protection</em>) block most memory reading attacks against lsass.exe.</p>")}''',
    hi="Pehle normal Windows ko pehchano, tabhi gadbad dikhegi. lsass.exe sirf ek hota hai aur System32 mein hota hai. svchost.exe ka parent services.exe hona chahiye. Galat folder ya galat parent wala process suspicious hai."))

  S.append(dict(id="file-system", h="The Windows file system and where malware likes to live", hi_h="Windows folders aur malware ke thikane",
    body=f'''<p>Windows uses NTFS with drive letters (<code>C:</code>, <code>D:</code>). A few folders matter far more than others:</p>
{table(["Folder", "What it holds", "Who can write"], [
  ["<code>C:\\Windows\\System32</code>", "the core 64-bit system files and tools", "administrators and the system only"],
  ["<code>C:\\Windows\\SysWOW64</code>", "32-bit versions of system files on 64-bit Windows (yes, the names look backwards)", "administrators"],
  ["<code>C:\\Program Files</code> and <code>Program Files (x86)</code>", "installed software", "administrators"],
  ["<code>C:\\ProgramData</code>", "shared app data, hidden by default", "often any user can create files"],
  ["<code>C:\\Users\\&lt;name&gt;\\AppData\\Roaming</code>, <code>Local</code>, <code>LocalLow</code>", "per user app settings and caches", "that user"],
  ["<code>%TEMP%</code> (usually <code>AppData\\Local\\Temp</code>)", "temporary files", "that user"],
  ["<code>C:\\Users\\Public</code>", "files shared with every user", "every user"]],
  "Important Windows folders")}
<p>Permissions on NTFS are <strong>access control lists</strong>: a list of entries like "Users: Read and Execute" or "Administrators: Full control". View them in a file's Properties, Security tab, or with <code>icacls</code>.</p>
{code(["C:\\> icacls C:\\ProgramData", "C:\\> icacls \"C:\\Program Files\""], "icacls")}
{attack("<p>Malware and phishing payloads run from places a normal user can write without admin rights: <code>AppData</code>, <code>%TEMP%</code>, <code>ProgramData</code>, <code>Users\\Public</code> and Downloads. They often persist through the per user <strong>Startup folder</strong> (<code>shell:startup</code>, which is <code>%AppData%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup</code>).</p>")}
{defend("<p>Application control (AppLocker or Windows Defender Application Control) can block programs from running in user writable folders. For investigation, start your search for a suspicious executable in exactly those folders.</p>")}''',
    hi="System32 aur Program Files mein sirf admin likh sakta hai. AppData, Temp, ProgramData aur Users\\Public mein normal user bhi likh sakta hai, isliye malware wahin rehta hai. Startup folder persistence ki common jagah hai."))

  S.append(dict(id="registry", h="The registry: Windows' giant settings database", hi_h="Registry: Windows ka settings database",
    body=f'''<p>The registry is a tree database holding almost every setting: installed software, services, drivers, user preferences and security policy. Its building blocks are <strong>keys</strong> (like folders) and <strong>values</strong> (name, type, data). Common types are <code>REG_SZ</code> (text), <code>REG_DWORD</code> (32-bit number) and <code>REG_BINARY</code>.</p>
{table(["Root key", "Short", "What it holds"], [
  ["HKEY_LOCAL_MACHINE", "HKLM", "machine wide settings: software, services, drivers, security"],
  ["HKEY_CURRENT_USER", "HKCU", "settings for the logged in user (loaded from their NTUSER.DAT)"],
  ["HKEY_USERS", "HKU", "every loaded user profile"],
  ["HKEY_CLASSES_ROOT", "HKCR", "file associations and COM objects (a merged view of HKLM and HKCU)"],
  ["HKEY_CURRENT_CONFIG", "HKCC", "current hardware profile"]],
  "Registry root keys")}
<p>On disk, the main hives are files in <code>C:\\Windows\\System32\\config</code>: <code>SAM</code> (local accounts and password hashes), <code>SECURITY</code>, <code>SOFTWARE</code> and <code>SYSTEM</code>. Each user's HKCU is <code>C:\\Users\\&lt;name&gt;\\NTUSER.DAT</code>.</p>
{code(["C:\\> reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "C:\\> reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "PS> Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'"], "Run keys")}
{attack("<p>The <strong>Run</strong> and <strong>RunOnce</strong> keys start a program at every login, so they are one of the most common persistence spots (MITRE ATT&amp;CK technique T1547.001). Attackers who get admin also try to copy the SAM and SYSTEM hives to extract local password hashes offline.</p>")}
{defend("<p>Sysinternals <strong>Autoruns</strong> lists every auto start location in one view (Run keys, services, scheduled tasks, drivers and more) and can hide entries signed by Microsoft so the unusual ones stand out. Sysmon event IDs 12 to 14 record registry changes.</p>")}''',
    hi="Registry Windows ka settings database hai: keys aur values. HKLM poori machine ke liye, HKCU current user ke liye. Run keys har login pe program chalati hain, isliye malware wahan apna entry daalta hai. Autoruns tool sab auto start jagah ek saath dikhata hai."))

  S.append(dict(id="users-uac", h="Accounts, SIDs, tokens and UAC", hi_h="Accounts, SID, tokens aur UAC",
    body=f'''<p>Windows identifies every user and group by a <strong>security identifier (SID)</strong>, not by name. A few are worth memorising:</p>
{table(["SID or ending", "Means"], [
  ["S-1-5-18", "Local System (NT AUTHORITY\\SYSTEM), the most powerful local account"],
  ["S-1-5-19 / S-1-5-20", "Local Service / Network Service, lower privilege service accounts"],
  ["...-500", "the built in Administrator account (relative ID 500), disabled by default on modern Windows"],
  ["...-501", "the built in Guest account"],
  ["S-1-5-32-544", "the local Administrators group"],
  ["...-1001 and up", "ordinary user accounts you create"]],
  "Well known SIDs")}
<p>When you log in, Windows builds an <strong>access token</strong> listing your SID, groups and privileges. Every process you start carries a copy, and the kernel checks it against each object's ACL.</p>
<h3>User Account Control</h3>
<p>If you are an administrator, Windows actually gives you <strong>two tokens</strong>: a filtered standard user token used for normal work and a full admin token. UAC is the prompt that switches a program to the full token. Processes also get an <strong>integrity level</strong> (Low, Medium, High, System); a browser sandbox runs at Low so it cannot write to most of your files.</p>
{analogy("<p>A hotel key card. Your card (token) lists which doors you may open. UAC is the front desk asking \"are you sure?\" before upgrading your card to the master key for one task.</p>")}
{attack("<p>Microsoft states that UAC is <strong>not a security boundary</strong>, and many UAC bypass techniques exist that let malware already running as an admin user get the full token without a prompt. Attackers also love <code>SeDebugPrivilege</code> and <code>SeImpersonatePrivilege</code>, which lead to SYSTEM.</p>")}
{defend("<p>Work daily as a <strong>standard user</strong> and type admin credentials only when needed. Keep UAC on its default or higher. On networks, Microsoft <strong>LAPS</strong> gives each machine a unique, rotating local administrator password so one stolen password does not unlock every PC.</p>")}
{code(["C:\\> whoami /user", "C:\\> whoami /groups", "C:\\> whoami /priv", "C:\\> net localgroup administrators"], "Who am I")}''',
    hi="Windows har user ko SID se pehchanta hai (S-1-5-18 = SYSTEM, -500 = built in Administrator). Login pe access token banta hai jo har process ke saath chalta hai. Admin user ke paas do tokens hote hain aur UAC prompt full token deta hai. UAC security boundary nahi hai, isliye roz standard user use karo."))

  S.append(dict(id="services-tasks", h="Services and scheduled tasks", hi_h="Services aur scheduled tasks",
    body=f'''<p>A <strong>service</strong> is a background program managed by the Service Control Manager (services.exe). It can start at boot before anyone logs in and usually runs as LocalSystem, LocalService, NetworkService or a dedicated account. A <strong>scheduled task</strong> runs a program at a time or on a trigger such as logon or idle.</p>
{code(["PS> Get-Service | Where-Object Status -eq 'Running'", "C:\\> sc qc Spooler", "C:\\> schtasks /query /fo LIST /v | more", "PS> Get-ScheduledTask | Where-Object State -ne 'Disabled'"], "Services and tasks")}
{table(["Startup type", "Meaning"], [
  ["Automatic", "starts at boot"], ["Automatic (Delayed Start)", "starts shortly after boot to speed up login"],
  ["Manual", "starts when something asks for it"], ["Disabled", "cannot start"]], "Service startup types")}
{attack("<p>Creating a service or task is a favourite way to keep access and to run as SYSTEM. Tools like PsExec create a temporary service on the target to run commands remotely. Weak permissions on a service's executable or registry key let a normal user replace it and wait for a reboot.</p>")}
{defend("<p>New services are logged as <strong>event 7045</strong> in the System log; new scheduled tasks as <strong>4698</strong> in the Security log when object access auditing for tasks is enabled. Turn off services you do not need, such as the Print Spooler on servers that never print (it was abused in the 2021 PrintNightmare flaws).</p>")}''',
    hi="Services background programs hain jo boot pe hi chal jaate hain, aksar SYSTEM ke roop mein. Scheduled tasks time ya trigger pe chalte hain. Attacker dono ko persistence ke liye use karta hai. Naya service event 7045 mein dikhta hai."))

  ev = [("4624", "Successful logon", "<p>Check the <strong>Logon Type</strong>: 2 interactive at the keyboard, 3 network (file shares), 5 service, 7 unlock, 10 remote desktop (RDP), 11 cached credentials. An admin account logging on with type 10 from an unknown IP at 3 AM deserves attention.</p>"),
    ("4625", "Failed logon", "<p>Many 4625s for one account means password guessing; one failure for many accounts means password spraying. The <em>Status</em> and <em>Sub Status</em> codes say why it failed, for example <code>0xC000006A</code> wrong password and <code>0xC0000064</code> user does not exist.</p>"),
    ("4672", "Special privileges assigned", "<p>Logged right after 4624 when an account with admin level privileges logs on. Useful to spot admin logons quickly.</p>"),
    ("4688", "New process created", "<p>Only recorded if <em>Audit Process Creation</em> is enabled, and the command line is included only if you also enable <em>Include command line in process creation events</em>. Sysmon event 1 gives richer detail.</p>"),
    ("4720", "User account created", "<p>Attackers create backdoor accounts. Any account created outside normal IT work should be checked.</p>"),
    ("4732", "Member added to a local group", "<p>Look especially for additions to Administrators or Remote Desktop Users.</p>"),
    ("4740", "Account locked out", "<p>Often the visible result of brute force. Logged on the domain controller for domain accounts.</p>"),
    ("1102", "Security log cleared", "<p>Recorded in the Security log itself when someone clears it. Attackers clear logs to hide; legitimate admins rarely need to.</p>"),
    ("7045", "Service installed", "<p>In the <strong>System</strong> log. Remote execution tools and some malware install services, so random names or paths in Temp are a red flag.</p>"),
    ("4104", "PowerShell script block", "<p>In <em>Microsoft-Windows-PowerShell/Operational</em> when script block logging is on. It records the actual decoded script, which defeats much obfuscation.</p>")]
  S.append(dict(id="event-logs", h="Event Viewer: the machine's diary", hi_h="Event Viewer: machine ki diary",
    body=f'''<p>Open <code>eventvwr.msc</code>. Under <strong>Windows Logs</strong> you find Application, Security, Setup, System and Forwarded Events, and under <strong>Applications and Services Logs</strong> hundreds of detailed channels such as PowerShell and Windows Defender. Each record has a time, source, <strong>event ID</strong>, level and details. Learn the IDs and you can read the story of an attack.</p>
{explorer("Event IDs every Windows defender should know", "Pick an event ID. All except 7045 and 4104 are in the Security log.", [(f"{i} <small>{t}</small>", f"<h4>{i}: {t}</h4>{d}") for i, t, d in ev])}
{code(["PS> Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 10", "PS> Get-WinEvent -FilterHashtable @{LogName='System'; Id=7045} | Format-List TimeCreated, Message"], "Query logs with PowerShell")}
{attack("<p>Attackers clear logs (event 1102 betrays them) or simply rely on the fact that useful auditing is off by default on many machines. Default Security log size is also small, so old evidence rolls off quickly.</p>")}
{defend("<p>Enable process creation auditing with command lines, PowerShell script block logging, raise the Security log size, install <strong>Sysmon</strong> with a good community configuration, and forward logs to a central place (a SIEM) so a cleared local log does not erase the evidence.</p>")}''',
    hi="Event Viewer machine ki diary hai. 4624 login hua, 4625 login fail, 4720 naya user bana, 4732 group mein add hua, 1102 log clear hua, 7045 naya service. Logs ko central SIEM pe bhejo taaki attacker local log clear kare to bhi saboot bacha rahe."))

  S.append(dict(id="command-line", h="cmd and PowerShell for defenders", hi_h="cmd aur PowerShell",
    body=f'''<p><strong>cmd.exe</strong> is the old command prompt, still everywhere. <strong>PowerShell</strong> is far more powerful: commands (cmdlets) follow a <code>Verb-Noun</code> pattern and pass <em>objects</em> through the pipeline, not just text, so you can filter and sort on real properties.</p>
{table(["Question", "cmd", "PowerShell"], [
  ["Who am I, what privileges?", "<code>whoami /all</code>", "<code>[Security.Principal.WindowsIdentity]::GetCurrent()</code>"],
  ["Local users", "<code>net user</code>", "<code>Get-LocalUser</code>"],
  ["Who is admin?", "<code>net localgroup administrators</code>", "<code>Get-LocalGroupMember Administrators</code>"],
  ["Running processes", "<code>tasklist /svc</code>", "<code>Get-Process | Sort-Object CPU -Descending</code>"],
  ["Network connections", "<code>netstat -ano</code>", "<code>Get-NetTCPConnection -State Established</code>"],
  ["IP configuration", "<code>ipconfig /all</code>", "<code>Get-NetIPConfiguration</code>"],
  ["File hash", "<code>certutil -hashfile file SHA256</code>", "<code>Get-FileHash file -Algorithm SHA256</code>"],
  ["Hidden files too", "<code>dir /a</code>", "<code>Get-ChildItem -Force</code>"],
  ["System details and patches", "<code>systeminfo</code>", "<code>Get-HotFix</code>"]],
  "Equivalent commands")}
{code(["PS> Get-NetTCPConnection -State Established | Select-Object LocalPort, RemoteAddress, RemotePort, OwningProcess", "PS> Get-Process -Id (Get-NetTCPConnection -State Established).OwningProcess | Select-Object Id, ProcessName, Path"], "Which program is talking to the internet?")}
{attack("<p>PowerShell is a built in tool, so attackers use it to download and run code in memory (\"living off the land\"). Look for <code>-EncodedCommand</code> or <code>-enc</code> with long base64 text, <code>-WindowStyle Hidden</code>, <code>IEX</code> (Invoke-Expression) and <code>DownloadString</code>. Note that the <strong>execution policy is not a security boundary</strong>; <code>-ExecutionPolicy Bypass</code> skips it.</p>")}
{defend("<p>Turn on script block logging (event 4104), keep Windows PowerShell 5.1 or PowerShell 7 with <strong>AMSI</strong> (lets antivirus scan scripts at run time), remove the old PowerShell 2.0 feature where it exists because it lacks these protections, and alert on encoded or hidden PowerShell started by Office or browsers.</p>")}''',
    hi="cmd purana hai, PowerShell powerful hai (Verb-Noun commands, objects ka pipeline). Defenders ke liye: whoami /all, Get-LocalGroupMember Administrators, Get-NetTCPConnection, Get-FileHash. Attacker PowerShell -enc aur hidden window se malware chalata hai. Script block logging (4104) on rakho."))

  return dict(
    slug="learn-windows-for-security", stage=1, n="1.3", minutes=60, level="Beginner",
    title="Windows Essentials for Security", short="Core processes, folders, registry, SIDs and UAC, services, Event IDs, cmd and PowerShell.",
    seo_title="Windows for Cybersecurity: Registry, Event IDs, UAC, PowerShell Basics | CyberWithMadhav",
    desc="Free Windows security lesson: normal processes, risky folders, registry Run keys, SIDs, tokens and UAC, services, Event IDs 4624 4625 4720 1102 7045, cmd and PowerShell.",
    kw="windows for cybersecurity, windows event ids 4624 4625, registry run keys, uac explained, powershell for security, windows processes lsass svchost, sysinternals",
    kicker="$ lesson 1.3 --stage foundations", hi_title="Security ke liye Windows essentials",
    lead="Windows runs most office and college desktops in India, and attackers know it inside out. This lesson teaches you what normal looks like, where Windows keeps its secrets, and how to read the evidence an attacker leaves behind.",
    hi_lead="India ke zyada tar office aur college computers Windows pe chalte hain. Is lesson mein seekho normal kaisa dikhta hai, Windows apne secrets kahan rakhta hai, aur attacker ke chhode saboot kaise padhein.",
    goals=["Recognise the normal Windows process tree and spot impostors", "Know which folders and registry keys malware uses to hide and persist", "Explain SIDs, access tokens, integrity levels and what UAC really does", "Read key Security and System event IDs and query them with PowerShell", "Use cmd and PowerShell to answer basic incident response questions"],
    sections=S,
    cards=[("How many lsass.exe processes are normal?", "Exactly one, in C:\\Windows\\System32, started by wininit.exe."),
      ("Event 4625?", "A failed logon. Many in a row suggest password guessing."),
      ("Logon type 10?", "RemoteInteractive, meaning Remote Desktop (RDP)."),
      ("SID S-1-5-18?", "NT AUTHORITY\\SYSTEM, the Local System account."),
      ("Where do Run keys live?", "HKCU and HKLM under Software\\Microsoft\\Windows\\CurrentVersion\\Run."),
      ("Event 7045 is in which log?", "The System log. It records a new service being installed."),
      ("Is UAC a security boundary?", "No. Microsoft says it is not, and bypasses exist. It is a convenience and safety layer."),
      ("Which event shows decoded PowerShell scripts?", "4104, script block logging, in Microsoft-Windows-PowerShell/Operational.")],
    quiz=[("You find <code>svchost.exe</code> running from <code>C:\\Users\\Public\\svchost.exe</code>. What do you conclude?", ["Normal, svchost runs from many folders", "Suspicious: the real one runs from System32 and is started by services.exe", "It is a Windows update", "It is the Print Spooler"], 1, "Correct name, wrong place. Classic masquerading."),
      ("Which registry location makes a program start each time the current user logs in?", ["HKLM\\SYSTEM\\CurrentControlSet\\Enum", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "HKCR\\.txt", "HKCC\\Software"], 1, "The Run key (and RunOnce) under HKCU applies at that user's logon."),
      ("200 events with ID 4625 for the account <code>admin</code> in 10 minutes most likely means:", ["A successful login", "Password brute force against admin", "A new service", "The log was cleared"], 1, "4625 is a failed logon; many against one account is brute force."),
      ("Which event suggests someone tried to hide their tracks?", ["4624", "1102", "4672", "4688"], 1, "1102 is logged when the Security log is cleared."),
      ("A Word document launches <code>powershell.exe -w hidden -enc SQBFAFgA...</code>. Best description?", ["Normal update check", "Likely malicious macro running encoded PowerShell", "UAC prompt", "Windows Defender scan"], 1, "Office spawning hidden, encoded PowerShell is a textbook malware pattern."),
      ("What is the safest daily setup for a home PC?", ["Use the built in Administrator account", "Turn UAC off", "Work as a standard user and elevate only when needed", "Disable event logs to save space"], 2, "Least privilege limits what malware gets if you click something bad.")],
    lab=dict(title="Lab: create evidence on your own Windows VM, then find it", time="45 to 60 minutes",
      needs="A Windows VM in VirtualBox. Microsoft offers free time limited evaluation copies of Windows 11 Enterprise and Windows Server at microsoft.com/evalcenter. Use a VM, not your main PC, because you will create accounts and settings.",
      steps=[("Snapshot first", "<p>Install Windows in the VM, then take a snapshot called <code>clean</code>. Everything below can be undone by restoring it.</p>"),
        ("Turn on the useful logging", code(["C:\\> auditpol /set /subcategory:\"Process Creation\" /success:enable", "C:\\> reg add HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\Audit /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f", "C:\\> auditpol /get /category:\"Logon/Logoff\""], "Enable auditing") + "<p>Run these in an <strong>administrator</strong> Command Prompt. The second line adds command lines to event 4688.</p>"),
        ("Make some events", code(["PS> $p = Read-Host -AsSecureString 'Password for labuser'", "PS> New-LocalUser -Name labuser -Password $p", "PS> Add-LocalGroupMember -Group Administrators -Member labuser", "C:\\> runas /user:labuser cmd"], "Create events") + "<p>Use an administrator PowerShell. At the <code>runas</code> prompt type a <strong>wrong</strong> password twice. You just created events 4720, 4732 and 4625.</p>"),
        ("Find them in Event Viewer and PowerShell", code(["PS> Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4720,4732,4625} -MaxEvents 20 | Format-Table TimeCreated, Id, Message -Wrap"], "Find events") + "<p>Open <code>eventvwr.msc</code>, Windows Logs, Security, and use <em>Filter Current Log</em> with <code>4720,4732,4625</code>. Read who did what and when.</p>"),
        ("Plant and hunt a harmless persistence entry", code(["C:\\> reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v LabNotepad /t REG_SZ /d notepad.exe /f", "C:\\> reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"], "Run key") + "<p>Sign out and in: Notepad opens. Now download <strong>Autoruns</strong> from Microsoft Sysinternals and find <code>LabNotepad</code> in the Logon tab. Delete it there or with <code>reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v LabNotepad /f</code>.</p>"),
        ("Clean up", code(["PS> Remove-LocalUser -Name labuser"], "Cleanup") + "<p>Or simply restore the <code>clean</code> snapshot.</p>")],
      verify="You created a user, an admin group change, failed logons and a Run key, and found every one of them in the logs or in Autoruns."),
    takeaways=["Learn normal first: right name, right path, right parent, right count.",
      "User writable folders (AppData, Temp, ProgramData, Public) are where payloads run from.",
      "Run keys, services and scheduled tasks are the big three persistence spots; Autoruns shows them all.",
      "4624, 4625, 4672, 4688, 4720, 4732, 1102 and 7045 tell most attack stories.",
      "PowerShell is a gift to admins and attackers alike. Log it."])


HOMENET = svg(720, 250, ARROWDEF +
  box(20, 20, 130, 44, "s-n", "Laptop", "192.168.1.10", 8) + box(20, 80, 130, 44, "s-n", "Phone", "192.168.1.11", 8) + box(20, 140, 130, 44, "s-n", "Smart TV", "192.168.1.12", 8) +
  box(220, 64, 180, 76, "s-p", "Home router", "switch + Wi-Fi + NAT", 12) +
  '<text x="310" y="158" text-anchor="middle" font-size="11" class="t-m">LAN side 192.168.1.1</text><text x="310" y="174" text-anchor="middle" font-size="11" class="t-m">WAN side: one ISP address</text>' +
  box(460, 74, 110, 56, "s-a", "ISP", "Jio, Airtel, BSNL", 10) +
  box(610, 54, 96, 96, "s-g", "Internet", "servers", 48) +
  arrow(150, 42, 218, 88, "ln", True) + arrow(150, 102, 218, 102, "ln", True) + arrow(150, 162, 218, 118, "ln", True) +
  arrow(400, 102, 458, 102, "ln-p", True) + arrow(570, 102, 608, 102, "ln-p", True) +
  '<text x="20" y="222" font-size="11" class="t-m">Private addresses inside. The router translates them (NAT) to the one public address your ISP gives you, or shares an ISP address with other customers (CGNAT).</text>',
  "A home network: devices with private addresses connect to a router that does NAT, then to the ISP and the internet")

ENCAP = svg(720, 230,
  '<rect x="430" y="18" width="200" height="34" rx="6" class="s-g" stroke-width="1.5"/><text x="530" y="40" text-anchor="middle" font-size="12">HTTP data: GET /index.html</text><text x="20" y="40" font-size="12" font-weight="700">Application</text>' +
  '<rect x="350" y="66" width="80" height="34" rx="6" class="s-a" stroke-width="1.5"/><text x="390" y="88" text-anchor="middle" font-size="11">TCP 443</text><rect x="430" y="66" width="200" height="34" rx="6" class="s-g" stroke-width="1.5"/><text x="530" y="88" text-anchor="middle" font-size="11">data</text><text x="20" y="88" font-size="12" font-weight="700">Transport: segment</text>' +
  '<rect x="250" y="114" width="100" height="34" rx="6" class="s-p" stroke-width="1.5"/><text x="300" y="136" text-anchor="middle" font-size="11">IP src, dst</text><rect x="350" y="114" width="280" height="34" rx="6" class="s-n" stroke-width="1.5"/><text x="490" y="136" text-anchor="middle" font-size="11">TCP header + data</text><text x="20" y="136" font-size="12" font-weight="700">Internet: packet</text>' +
  '<rect x="150" y="162" width="100" height="34" rx="6" class="s-r" stroke-width="1.5"/><text x="200" y="184" text-anchor="middle" font-size="11">MAC header</text><rect x="250" y="162" width="380" height="34" rx="6" class="s-n" stroke-width="1.5"/><text x="440" y="184" text-anchor="middle" font-size="11">IP packet</text><rect x="630" y="162" width="60" height="34" rx="6" class="s-r" stroke-width="1.5"/><text x="660" y="184" text-anchor="middle" font-size="11">FCS</text><text x="20" y="184" font-size="12" font-weight="700">Link: frame</text>' +
  '<text x="20" y="220" font-size="11" class="t-m">Each layer wraps the one above in its own header. The receiver unwraps in reverse order.</text>',
  "Encapsulation: application data gets a TCP header, then an IP header, then an Ethernet header and trailer")

HANDSHAKE = svg(720, 250, ARROWDEF +
  box(20, 14, 160, 40, "s-p", "Your laptop", "client", 8) + box(540, 14, 160, 40, "s-g", "Web server", "port 443", 8) +
  '<line x1="100" y1="54" x2="100" y2="240" class="ln" stroke-width="1.5" stroke-dasharray="4 4"/><line x1="620" y1="54" x2="620" y2="240" class="ln" stroke-width="1.5" stroke-dasharray="4 4"/>' +
  arrow(102, 84, 616, 112, "ln-p") + '<text x="360" y="88" text-anchor="middle" font-size="12">SYN  seq=1000</text>' +
  arrow(618, 140, 104, 168, "ln-g") + '<text x="360" y="144" text-anchor="middle" font-size="12">SYN-ACK  seq=5000 ack=1001</text>' +
  arrow(102, 196, 616, 222, "ln-p") + '<text x="360" y="200" text-anchor="middle" font-size="12">ACK  ack=5001: connection open</text>',
  "TCP three way handshake: SYN from client, SYN-ACK from server, ACK from client")

DNSFLOW = svg(720, 260, ARROWDEF +
  box(20, 100, 120, 50, "s-p", "Your device", "stub resolver", 8) +
  box(200, 100, 150, 50, "s-a", "Recursive resolver", "ISP, 1.1.1.1, 8.8.8.8", 8) +
  box(470, 10, 230, 44, "s-n", "Root servers  .", None, 8) + box(470, 104, 230, 44, "s-n", "TLD servers  .in", None, 8) + box(470, 198, 230, 44, "s-g", "Authoritative: example.in", None, 8) +
  arrow(140, 118, 198, 118, "ln-p") + '<text x="170" y="110" text-anchor="middle" font-size="10">1</text>' +
  arrow(350, 110, 468, 36, "ln") + '<text x="400" y="62" font-size="10" class="t-m">2 ask root, told: try .in</text>' +
  arrow(350, 125, 468, 126, "ln") + '<text x="372" y="140" font-size="10" class="t-m">3 ask .in</text>' +
  arrow(350, 140, 468, 214, "ln") + '<text x="360" y="200" font-size="10" class="t-m">4 get the A record</text>' +
  arrow(198, 136, 142, 136, "ln-g") + '<text x="170" y="162" text-anchor="middle" font-size="10">5 answer, cached for TTL</text>',
  "DNS resolution: device asks a recursive resolver, which asks the root, the TLD and the authoritative server, then returns and caches the answer")

def lesson_network():
  S = []
  S.append(dict(id="what-is-network", h="What a network is, from your Wi-Fi to the internet", hi_h="Network kya hai",
    body=f'''<p>A network is two or more devices that can exchange data. Each device has a <strong>network interface</strong> (Wi-Fi or Ethernet) with a hardware address, the <strong>MAC address</strong>: 48 bits written as six hex pairs like <code>3C:52:82:1A:9F:04</code>. The first half usually identifies the manufacturer.</p>
<ul>
<li>A <strong>switch</strong> connects devices on the same local network (LAN) and forwards frames by MAC address.</li>
<li>A <strong>router</strong> connects different networks and forwards packets by IP address. Your home "router" is really a router, switch, Wi-Fi access point and firewall in one box.</li>
<li>The <strong>internet</strong> is a network of networks: thousands of ISPs and companies whose routers exchange routes with each other.</li>
</ul>
{fig(HOMENET, "Most Indian homes look like this. Many mobile and some broadband connections add carrier grade NAT, so even the router's outside address is shared.", "Home network diagram")}
{analogy("<p>The MAC address is your flat number inside one building; the IP address is your full postal address that works across the city. The building's security guard (switch) knows flat numbers; the postal system (routers) only cares about postal addresses.</p>")}
{attack("<p>On a shared network such as public Wi-Fi, attackers can try <strong>ARP spoofing</strong>, falsely claiming the router's IP address belongs to their MAC, so your traffic flows through them. That is a big reason to always use HTTPS and to be careful on open Wi-Fi.</p>")}''',
    hi="Network matlab devices jo data share karte hain. MAC address ek network ke andar kaam aata hai (flat number), IP address network ke paar (postal address). Switch MAC se, router IP se forward karta hai. Public Wi-Fi pe ARP spoofing ho sakta hai, isliye HTTPS zaroori hai."))

  S.append(dict(id="layers", h="Layers and encapsulation", hi_h="Layers aur encapsulation",
    body=f'''<p>Networking is split into layers so each part can change without breaking the others. The practical model is <strong>TCP/IP</strong> with four layers; the <strong>OSI</strong> model has seven and is used to talk about problems ("it is a layer 2 issue").</p>
{table(["TCP/IP layer", "OSI layers", "Unit", "Examples"], [
  ["Application", "7 Application, 6 Presentation, 5 Session", "data", "HTTP, DNS, SMTP, SSH, TLS (commonly placed here)"],
  ["Transport", "4 Transport", "segment (TCP) or datagram (UDP)", "TCP, UDP, port numbers"],
  ["Internet", "3 Network", "packet", "IPv4, IPv6, ICMP"],
  ["Link", "2 Data link, 1 Physical", "frame, bits", "Ethernet, Wi-Fi, MAC addresses, cables, radio"]],
  "TCP/IP and OSI layers")}
{fig(ENCAP, "Wireshark shows exactly these nested headers for every packet you capture.", "Encapsulation")}
<p>For a deeper walk through both models see the guide <a href="blog-osi-tcp-ip-model-explained.html">OSI and TCP/IP explained</a>.</p>
{defend("<p>Layers map neatly to defences: Wi-Fi encryption at the link layer, firewalls filtering IP addresses and ports at layers 3 and 4, and web application firewalls inspecting HTTP at layer 7. Defence in depth means having something at several layers.</p>")}''',
    hi="TCP/IP model ke 4 layers: Application (HTTP, DNS), Transport (TCP, UDP, ports), Internet (IP), Link (Ethernet, Wi-Fi). Har layer upar wale data ko apne header mein lapet deti hai, isse encapsulation kehte hain. Har layer pe alag defence hota hai."))

  S.append(dict(id="ip-addressing", h="IP addresses, subnets and private ranges", hi_h="IP address aur subnet",
    body=f'''<p>An <strong>IPv4 address</strong> is 32 bits, written as four bytes in decimal: <code>192.168.1.10</code>. Part of it identifies the <strong>network</strong> and the rest the <strong>host</strong>. The split is set by the <strong>subnet mask</strong>, usually written in <strong>CIDR</strong> form as a slash and the number of network bits.</p>
{table(["CIDR", "Mask", "Addresses", "Usable hosts", "Typical use"], [
  ["/24", "255.255.255.0", "256", "254", "home or small office LAN"],
  ["/16", "255.255.0.0", "65,536", "65,534", "large campus"],
  ["/30", "255.255.255.252", "4", "2", "link between two routers"],
  ["/32", "255.255.255.255", "1", "1 (one host)", "a single address in a firewall rule"]],
  "Common subnet sizes")}
<p>In a /24 like <code>192.168.1.0/24</code>, the first address (<code>.0</code>) names the network and the last (<code>.255</code>) is the broadcast address, leaving .1 to .254 for devices. Your <strong>default gateway</strong>, usually the router, is where packets for other networks go.</p>
<h3>Special ranges to recognise on sight</h3>
{table(["Range", "Meaning"], [
  ["10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16", "private (RFC 1918), not routed on the internet"],
  ["100.64.0.0/10", "shared address space for carrier grade NAT at ISPs"],
  ["127.0.0.0/8", "loopback, the machine itself (127.0.0.1 is localhost)"],
  ["169.254.0.0/16", "link local: the device gave itself an address because DHCP failed"],
  ["192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24", "reserved for documentation and examples"]],
  "Special IPv4 ranges")}
<p><strong>IPv6</strong> uses 128-bit addresses like <code>2001:db8::1</code>, so there are enough for every device without NAT. Indian mobile networks such as Jio rolled out IPv6 widely, so your phone very likely has one now.</p>
<p>Practise subnetting with the <a href="index.html#tools">subnet calculator</a> on the home page.</p>
{attack("<p>Attackers scan address ranges to find live hosts, then probe their ports. Inside a company, flat networks where every PC can reach every server let ransomware spread fast.</p>")}
{defend("<p><strong>Segmentation</strong>: put servers, staff PCs, CCTV and guest Wi-Fi in separate subnets or VLANs with firewall rules between them. You will build this in the CCNA stage.</p>")}''',
    hi="IPv4 address 32 bits ka hota hai. /24 matlab pehle 24 bits network ke, baaki host ke (254 devices). 10.x, 172.16 se 172.31, aur 192.168.x private ranges hain. 169.254 dikhe to DHCP fail hua. Network ko segments mein baanto taaki ransomware poore office mein na faile."))

  ports = [["20, 21", "TCP", "FTP", "file transfer, sends passwords in clear text"], ["22", "TCP", "SSH", "secure remote shell; brute forced constantly on the internet"], ["23", "TCP", "Telnet", "old remote shell with no encryption; should be off"],
    ["25", "TCP", "SMTP", "mail between servers"], ["53", "UDP and TCP", "DNS", "name lookups"], ["67, 68", "UDP", "DHCP", "automatic IP addresses"], ["80", "TCP", "HTTP", "web without encryption"],
    ["110, 143", "TCP", "POP3, IMAP", "reading mail (secure versions on 995, 993)"], ["123", "UDP", "NTP", "time sync, critical for logs"], ["443", "TCP (and UDP for HTTP/3)", "HTTPS", "web with TLS"],
    ["445", "TCP", "SMB", "Windows file sharing; never expose to the internet"], ["3306", "TCP", "MySQL", "database"], ["3389", "TCP", "RDP", "Windows remote desktop; a top ransomware entry point when exposed"]]
  S.append(dict(id="ports-tcp-udp", h="Ports, TCP and UDP", hi_h="Ports, TCP aur UDP",
    body=f'''<p>An IP address gets a packet to the right machine. A <strong>port number</strong> (0 to 65535) gets it to the right program on that machine. Ports 0 to 1023 are the <strong>well known</strong> ports for standard services. Your side of a connection uses a random high <strong>ephemeral</strong> port.</p>
<p>Two transport protocols carry almost everything:</p>
<ul><li><strong>TCP</strong> is connection based and reliable: it numbers bytes, resends lost data and delivers in order. Web, email, SSH.</li>
<li><strong>UDP</strong> just sends datagrams with no setup and no guarantee. Faster and simpler: DNS queries, video calls, online games, and QUIC (HTTP/3).</li></ul>
{fig(HANDSHAKE, "Every TCP connection starts with these three packets. Sequence numbers are random in real life.", "TCP handshake")}
{table(["Port", "Protocol", "Service", "Security note"], ports, "Common ports")}
{attack("<p>Port scanners like Nmap send SYN packets to many ports; a SYN-ACK reply means open. Exposed SMB on port 445 let the <strong>WannaCry</strong> ransomware spread worldwide in May 2017 through the EternalBlue exploit, and exposed RDP on 3389 remains one of the most common ransomware entry points.</p>")}
{defend("<p>Close what you do not need, and never expose SMB, RDP or databases directly to the internet; put them behind a VPN. Check what your own Linux machine listens on with <code>ss -tuln</code>, or on Windows with <code>netstat -ano</code>. Only scan systems you own or have written permission to test.</p>")}''',
    hi="IP address machine tak le jaata hai, port number sahi program tak. TCP reliable hai (3 way handshake: SYN, SYN-ACK, ACK), UDP fast hai par guarantee nahi. 22 SSH, 53 DNS, 80 HTTP, 443 HTTPS, 445 SMB, 3389 RDP. SMB aur RDP ko kabhi internet pe open mat chhodo."))

  S.append(dict(id="dns", h="DNS: the internet's phone book", hi_h="DNS: internet ki phone book",
    body=f'''<p>People remember names, computers need IP addresses. <strong>DNS</strong> (Domain Name System) translates one into the other, and it does it through a hierarchy of servers.</p>
{fig(DNSFLOW, "Answers are cached for the record's TTL (time to live), so most lookups never go beyond the resolver.", "DNS resolution")}
{table(["Record", "Holds", "Example"], [
  ["A", "IPv4 address", "example.in to 203.0.113.20"], ["AAAA", "IPv6 address", "example.in to 2001:db8::20"],
  ["CNAME", "an alias pointing to another name", "www to example.in"], ["MX", "mail servers for the domain", "10 mx1.example.in"],
  ["TXT", "free text, used for SPF, DKIM, DMARC and domain verification", "v=spf1 include:... -all"], ["NS", "which servers are authoritative for the domain", "ns1.dns-host.example"]],
  "DNS record types")}
{code(["$ nslookup cyberwithmadhav.com", "$ dig +short A cyberwithmadhav.com", "$ dig +short MX gmail.com", "$ dig +trace example.com"], "DNS lookups")}
<p>You can check a real domain's email related DNS records with the <a href="dns-security-checker.html">DNS and Email Security Checker</a> in the Security Lab.</p>
{attack("<ul><li><strong>Lookalike domains</strong> (sbi-kyc-update.example) only need a cheap DNS registration.</li><li><strong>DNS spoofing or cache poisoning</strong> returns a fake IP for a real name.</li><li><strong>DNS tunnelling</strong> hides stolen data or malware commands inside DNS queries, because DNS is allowed out of almost every network.</li></ul>")}
{defend("<p>Use a trustworthy resolver, and consider encrypted DNS (DNS over HTTPS or DNS over TLS). In companies, log DNS queries: unusually long or random looking subdomains are a classic tunnelling signal. Domain owners protect their names with DNSSEC and email records like SPF, DKIM and DMARC.</p>")}''',
    hi="DNS naam ko IP address mein badalta hai: device resolver se poochta hai, resolver root, phir .in jaise TLD, phir domain ke authoritative server se. A record IPv4, MX mail, TXT mein SPF aur DMARC. Attacker lookalike domains, DNS spoofing aur DNS tunnelling use karta hai."))

  S.append(dict(id="http-https", h="HTTP and HTTPS: what really happens when you open a website", hi_h="HTTP aur HTTPS",
    body=f'''<p>HTTP is a simple text conversation: the browser sends a <strong>request</strong> with a method, path and headers, and the server sends a <strong>response</strong> with a status code, headers and a body.</p>
{code(["$ curl -sI https://example.com", "HTTP/2 200", "content-type: text/html", "cache-control: max-age=3600"], "HTTP response headers", copy=False)}
{table(["Status", "Meaning"], [["200", "OK"], ["301 / 302", "moved, go to the Location header"], ["401 / 403", "not logged in / not allowed"], ["404", "not found"], ["500", "server error"]], "HTTP status codes")}
<p>Methods you will meet: <code>GET</code> reads, <code>POST</code> submits data, <code>PUT</code> and <code>DELETE</code> change resources in APIs. <strong>Cookies</strong> are headers the server asks the browser to send back, which is how logins are remembered, and why stealing a session cookie can be as good as stealing the password.</p>
<p><strong>HTTPS</strong> is HTTP inside <strong>TLS</strong>. TLS encrypts the conversation, protects it from tampering and proves the server owns the certificate for that domain.</p>
{stepper("You type https://www.example.in and press Enter", "Seven things happen in well under a second.", [
  ("1. Do I already know?", "<p>The browser checks its own DNS cache, then the OS cache and hosts file.</p>"),
  ("2. DNS lookup", "<p>If not cached, the OS asks the configured resolver for the A or AAAA record and gets back an IP address such as 203.0.113.20.</p>"),
  ("3. Route", "<p>The destination is not on your subnet, so the packet goes to the default gateway (your router), then through the ISP and other networks to the server.</p>"),
  ("4. TCP handshake", "<p>SYN, SYN-ACK, ACK on port 443 opens a connection. (HTTP/3 uses QUIC over UDP instead and combines this with the next step.)</p>"),
  ("5. TLS handshake", "<p>Browser and server agree on keys. The server sends its certificate; the browser checks it is valid, not expired, issued by a trusted authority and matches <code>www.example.in</code>.</p>"),
  ("6. HTTP request and response", "<p>Encrypted inside TLS, the browser sends <code>GET / HTTP/2</code> with headers and cookies. The server answers <code>200 OK</code> with HTML.</p>"),
  ("7. Render, and repeat", "<p>The browser reads the HTML, then requests CSS, scripts and images, often from other domains, repeating steps 1 to 6 for each new host.</p>")])}
{attack("<p>The padlock proves the connection is encrypted to <em>that domain</em>, not that the domain is honest. Phishing sites get free certificates in minutes. Attackers also steal session cookies with malware or through cross site scripting, bypassing passwords and OTPs entirely.</p>")}
{defend("<p>Read the domain, not the padlock. Sites should use HTTPS everywhere with HSTS and mark cookies <code>Secure</code>, <code>HttpOnly</code> and <code>SameSite</code>. You can inspect any site's headers and cookies with browser DevTools; see <a href=\"blog-browser-devtools-for-security.html\">DevTools for security</a>.</p>")}''',
    hi="HTTP request aur response ki baat hai: GET, POST, status codes 200, 404, 500. HTTPS = HTTP + TLS, jo encrypt karta hai aur certificate se domain prove karta hai. Padlock sirf ye batata hai ki connection encrypted hai, ye nahi ki site imaandaar hai. Domain padho, padlock nahi."))

  return dict(
    slug="learn-networking-basics", stage=1, n="1.4", minutes=55, level="Beginner",
    title="Networking Basics: IP, Ports, DNS and HTTP", short="MAC and IP, layers, subnets, TCP and UDP ports, DNS and HTTPS. The bridge to CCNA.",
    seo_title="Networking Basics for Cybersecurity: IP, Subnets, Ports, DNS, HTTP | CyberWithMadhav",
    desc="Free networking primer for security beginners: MAC vs IP, TCP/IP layers, subnets and private ranges, TCP and UDP ports, the 3 way handshake, DNS records, HTTP and HTTPS.",
    kw="networking basics for cybersecurity, ip address subnet cidr, tcp vs udp, common ports list, how dns works, http vs https, tcp three way handshake",
    kicker="$ lesson 1.4 --stage foundations", hi_title="Networking basics: IP, ports, DNS aur HTTP",
    lead="Almost every attack crosses a network, and almost every investigation reads network evidence. This primer gives you the working mental model: addresses, layers, ports, DNS and HTTPS, ready for the CCNA stage.",
    hi_lead="Lagbhag har attack network se guzarta hai. Ye primer aapko kaam ka mental model deta hai: addresses, layers, ports, DNS aur HTTPS, CCNA stage ke liye taiyaar.",
    goals=["Tell MAC addresses, IP addresses, switches and routers apart", "Explain the TCP/IP layers and encapsulation", "Read CIDR notation and recognise private and special IPv4 ranges", "Explain TCP versus UDP, the handshake and the security meaning of common ports", "Trace a DNS lookup and an HTTPS page load end to end"],
    sections=S,
    cards=[("Switch vs router?", "A switch forwards frames by MAC address inside a LAN. A router forwards packets by IP address between networks."),
      ("Usable hosts in a /24?", "254. 256 addresses minus the network and broadcast addresses."),
      ("The three RFC 1918 private ranges?", "10.0.0.0/8, 172.16.0.0/12 and 192.168.0.0/16."),
      ("TCP handshake order?", "SYN, SYN-ACK, ACK."),
      ("Port 3389?", "RDP, Windows Remote Desktop. Never expose it straight to the internet."),
      ("What does an MX record hold?", "The mail servers that accept email for a domain."),
      ("A 169.254.x.x address means?", "The device could not get an address from DHCP and assigned itself a link local one."),
      ("Does the padlock mean a site is safe?", "No. It means the connection is encrypted to that domain. Phishing sites have padlocks too.")],
    quiz=[("Which device forwards traffic between your home network and your ISP?", ["Switch", "Router", "Repeater", "Network card"], 1, "Routers connect different networks. The home box includes a router."),
      ("Which address is NOT private?", ["10.20.30.40", "172.20.1.1", "192.168.0.5", "8.8.8.8"], 3, "8.8.8.8 is a public address (Google Public DNS)."),
      ("A DNS query for a short name is most often sent using:", ["TCP port 80", "UDP port 53", "TCP port 443", "UDP port 123"], 1, "DNS normally uses UDP 53, falling back to TCP 53 for large answers."),
      ("You see SYN packets from one IP to ports 1 to 1024 on a server, one after another. What is likely happening?", ["A software update", "A port scan", "A DNS lookup", "TLS renewal"], 1, "Probing many ports in order is a port scan."),
      ("Which statement about HTTPS is true?", ["It proves the website owner is trustworthy", "It encrypts traffic between browser and the server named in the certificate", "It hides which domain you visit from everyone", "It blocks malware downloads"], 1, "TLS gives confidentiality and integrity to the named server, nothing more."),
      ("In <code>192.168.10.0/24</code>, what is the broadcast address?", ["192.168.10.0", "192.168.10.1", "192.168.10.254", "192.168.10.255"], 3, "The last address of the block is the broadcast address.")],
    lab=dict(title="Lab: see your own network", time="40 minutes",
      needs="Your Ubuntu VM (NAT adapter is fine), and Wireshark (free, wireshark.org) on the VM or your own PC. Capture only on networks and devices you own.",
      steps=[("Find your addresses", code(["$ ip -br addr", "$ ip route", "$ resolvectl status | grep -A2 'DNS Servers'"], "Addresses") + "<p>Write down your IP, prefix length, default gateway and DNS server. On Windows the same information is in <code>ipconfig /all</code>. In VirtualBox NAT mode you will usually see 10.0.2.15/24 with gateway 10.0.2.2.</p>"),
        ("Test the path", code(["$ ping -c 3 10.0.2.2", "$ ping -c 3 1.1.1.1", "$ tracepath -n 1.1.1.1"], "Path") + "<p>If the gateway answers but 1.1.1.1 does not, the problem is beyond your machine. If 1.1.1.1 answers but names fail, it is DNS. That split is the start of all network troubleshooting.</p>"),
        ("Query DNS by hand", code(["$ sudo apt install -y dnsutils", "$ dig cyberwithmadhav.com A", "$ dig cyberwithmadhav.com MX", "$ dig cyberwithmadhav.com TXT", "$ dig +trace cyberwithmadhav.com"], "dig") + "<p>Find the TTL of the A record and the SPF entry in the TXT records. In the trace, spot the root, the .com servers and the authoritative servers.</p>"),
        ("Read HTTP headers", code(["$ curl -sI http://example.com", "$ curl -sI https://example.com", "$ curl -v https://example.com -o /dev/null 2>&1 | grep -E 'Connected|SSL|subject|issuer'"], "curl") + "<p>Note the status code and the certificate subject and issuer.</p>"),
        ("Capture a handshake in Wireshark", "<p>Start a capture on your own interface, then run <code>curl https://example.com</code>. Stop and apply the display filter <code>dns || tcp.flags.syn==1</code>. Find the DNS query and response, then the SYN, SYN-ACK and ACK. Next filter <code>tls.handshake</code> and find the Client Hello and the server name (SNI) it carries.</p>"),
        ("List your listening ports", code(["$ ss -tuln", "$ sudo ss -tulnp"], "Listening ports") + "<p>For each listening port, name the service. Anything you cannot explain is worth investigating, on your own machine.</p>")],
      verify="You can name your IP, gateway and DNS server, explain a ping or DNS failure, and point to a DNS exchange and a TCP handshake in your own capture."),
    takeaways=["MAC addresses work inside a LAN; IP addresses work across networks.",
      "Layers wrap each other: frame, packet, segment, data.",
      "Know the private ranges and what /24, /30 and /32 mean on sight.",
      "Ports identify services. Exposed SMB and RDP are invitations to attackers.",
      "DNS and HTTPS are where phishing lives. Read the domain, not the padlock."])
