"""Stage 1 lessons, part A: How a computer works, OS fundamentals. Original writing for CyberWithMadhav."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from learn_kit import *

# ---------------------------------------------------------------- diagrams
ARCH = svg(720, 330, ARROWDEF +
  box(250, 20, 220, 150, "s-p", "", None, 16) +
  '<text x="360" y="44" text-anchor="middle" font-size="14" font-weight="700">CPU</text>' +
  box(266, 58, 90, 46, "s-n", "Control", "unit", 8) + box(364, 58, 90, 46, "s-n", "ALU", "maths, logic", 8) +
  box(266, 112, 188, 44, "s-n", "Registers + cache", "tiny, fastest", 8) +
  box(20, 60, 170, 70, "s-g", "RAM", "working memory, volatile") +
  box(530, 60, 170, 70, "s-a", "Storage", "SSD or HDD, keeps data") +
  box(70, 240, 180, 64, "s-n", "Input", "keyboard, network, mic") +
  box(470, 240, 180, 64, "s-n", "Output", "screen, network, speaker") +
  '<rect x="20" y="196" width="680" height="22" rx="11" class="s-p" stroke-width="1"/>' +
  '<text x="360" y="211" text-anchor="middle" font-size="11">system bus: address, data and control lines (in modern PCs, PCIe links and memory channels)</text>' +
  arrow(190, 95, 248, 95, "ln-g", True) + arrow(470, 95, 528, 95, "ln", True) +
  arrow(360, 170, 360, 194, "ln-p") + arrow(160, 238, 160, 220, "ln") + arrow(560, 220, 560, 238, "ln") +
  arrow(105, 130, 105, 194, "ln") + arrow(615, 130, 615, 194, "ln"),
  "Block diagram of a computer: the CPU with control unit, ALU and registers, connected to RAM, storage, input and output over buses")

PYR = svg(720, 300,
  '<polygon points="360,18 420,78 300,78" class="s-r" stroke-width="1.5"/><text x="360" y="66" text-anchor="middle" font-size="12" font-weight="700">Registers</text>' +
  '<polygon points="300,84 420,84 470,134 250,134" class="s-a" stroke-width="1.5"/><text x="360" y="115" text-anchor="middle" font-size="12" font-weight="700">CPU cache L1 L2 L3</text>' +
  '<polygon points="250,140 470,140 530,196 190,196" class="s-g" stroke-width="1.5"/><text x="360" y="173" text-anchor="middle" font-size="13" font-weight="700">RAM</text>' +
  '<polygon points="190,202 530,202 600,270 120,270" class="s-p" stroke-width="1.5"/><text x="360" y="241" text-anchor="middle" font-size="13" font-weight="700">SSD and hard disk</text>' +
  '<text x="640" y="40" font-size="11" class="t-m">faster</text><text x="640" y="56" font-size="11" class="t-m">smaller</text><text x="640" y="72" font-size="11" class="t-m">costlier per GB</text>' +
  '<text x="30" y="236" font-size="11" class="t-m">slower</text><text x="30" y="252" font-size="11" class="t-m">bigger</text><text x="30" y="268" font-size="11" class="t-m">keeps data at power off</text>' +
  '<line x1="660" y1="84" x2="660" y2="270" class="ln" stroke-width="1.5" stroke-dasharray="4 4"/><line x1="60" y1="20" x2="60" y2="210" class="ln" stroke-width="1.5" stroke-dasharray="4 4"/>',
  "Memory hierarchy pyramid: registers at the top, then CPU cache, RAM, and SSD or hard disk at the bottom")

RINGS = svg(720, 300, ARROWDEF +
  box(20, 20, 680, 90, "s-g", "", None, 14) + '<text x="40" y="44" font-size="12" font-weight="700">USER MODE (ring 3): limited, crashes stay inside one process</text>' +
  box(40, 54, 140, 44, "s-n", "Browser", None, 8) + box(200, 54, 140, 44, "s-n", "WhatsApp", None, 8) + box(360, 54, 140, 44, "s-n", "Terminal", None, 8) + box(520, 54, 160, 44, "s-n", "Malware?", "same rules apply", 8) +
  '<rect x="20" y="124" width="680" height="34" rx="10" class="s-a" stroke-width="1.5"/><text x="360" y="146" text-anchor="middle" font-size="12" font-weight="600">system call interface: open, read, write, execve, CreateFile ... the only door down</text>' +
  box(20, 172, 680, 76, "s-p", "", None, 14) + '<text x="40" y="194" font-size="12" font-weight="700">KERNEL MODE (ring 0): full control of the hardware</text>' +
  box(40, 204, 150, 36, "s-n", "Scheduler", None, 8) + box(205, 204, 150, 36, "s-n", "Memory manager", None, 8) + box(370, 204, 150, 36, "s-n", "File systems", None, 8) + box(535, 204, 145, 36, "s-n", "Drivers", None, 8) +
  box(20, 258, 680, 34, "s-n", "Hardware: CPU, RAM, disk, network card", None, 10) +
  arrow(110, 100, 110, 122, "ln", True) + arrow(270, 100, 270, 122, "ln", True) + arrow(430, 100, 430, 122, "ln", True),
  "User mode applications reach the kernel only through the system call interface; the kernel controls the hardware")

LAYOUT = svg(720, 330, ARROWDEF +
  box(220, 14, 280, 40, "s-r", "Kernel space", "not readable from user mode", 8) +
  box(220, 62, 280, 52, "s-a", "Stack", "local variables, return addresses", 8) +
  '<text x="360" y="134" text-anchor="middle" font-size="12" class="t-m">grows down  &#8595;     free space     &#8593;  grows up</text>' +
  box(220, 146, 280, 52, "s-g", "Heap", "malloc, new: dynamic data", 8) +
  box(220, 206, 280, 40, "s-n", "Data and BSS", "global variables", 8) +
  box(220, 254, 280, 40, "s-p", "Text (code)", "read only, executable", 8) +
  '<text x="520" y="30" font-size="11" class="t-m">high addresses</text><text x="520" y="290" font-size="11" class="t-m">low addresses</text>' +
  '<text x="40" y="90" font-size="11" class="t-m">overflow a stack buffer</text><text x="40" y="106" font-size="11" class="t-m">and you can overwrite</text><text x="40" y="122" font-size="11" class="t-m">the saved return address</text>' +
  arrow(170, 104, 216, 90, "ln-p"),
  "Typical layout of a process's virtual memory: kernel space, stack, free space, heap, data and text segments")

def lesson_computer():
  S = []
  S.append(dict(id="big-picture", h="The big picture: five parts, one idea", hi_h="Big picture: paanch hisse, ek idea",
    body=f'''<p>Every computer you will ever defend, from a ₹8,000 phone to a rack server in a Mumbai data centre, follows the same pattern. Something <strong>takes input</strong>, something <strong>processes</strong> it, something <strong>remembers</strong> it for now, something <strong>stores</strong> it for later, and something <strong>sends output</strong>.</p>
<p>The design most machines still use comes from the <strong>stored program</strong> idea described by John von Neumann and colleagues in 1945: program instructions and data live in the same memory, and the processor fetches both from there. That single decision is why a bug can make a computer treat attacker supplied <em>data</em> as <em>instructions</em>. Keep that thought; half of exploitation grows from it.</p>
{fig(ARCH, "The CPU does the work, RAM holds what is being worked on, storage keeps things after power off, and buses connect them.", "Computer block diagram")}
{analogy("<p>A restaurant kitchen. The <strong>chef</strong> is the CPU. The <strong>counter</strong> in front of the chef is RAM: small, right there, wiped clean at closing time. The <strong>store room</strong> is the SSD: big, slower to reach, keeps everything overnight. Orders come in from waiters (input) and plates go out (output).</p>")}
<p>Why should a security learner care about hardware at all? Because every attack eventually lands somewhere physical: a value in a CPU register, a password sitting in RAM, a deleted file still on a disk, or malicious code hiding in firmware that runs before Windows even starts. Defenders who understand the machine know where to look.</p>''',
    hi="Computer ke 5 kaam: input lena, process karna (CPU), abhi ke liye yaad rakhna (RAM), hamesha ke liye store karna (SSD), aur output dena. Von Neumann design mein code aur data ek hi memory mein rehte hain, isliye bug hone par attacker ka data code ban sakta hai."))

  S.append(dict(id="cpu", h="The CPU: fetch, decode, execute, billions of times a second", hi_h="CPU: fetch, decode, execute",
    body=f'''<p>The CPU (central processing unit) only ever does one simple loop. It <strong>fetches</strong> the next instruction from memory, <strong>decodes</strong> what it means, <strong>executes</strong> it, and moves on. A 3 GHz core has a clock that ticks three billion times per second, and modern cores finish several instructions per tick by working on many at once in a pipeline.</p>
<h3>Parts worth knowing</h3>
<ul>
<li><strong>Control unit</strong>: reads instructions and directs everything else.</li>
<li><strong>ALU</strong> (arithmetic logic unit): adds, compares, does AND, OR, XOR. Encryption and hashing are mostly huge numbers of these simple operations.</li>
<li><strong>Registers</strong>: a handful of tiny storage slots inside the CPU. Two matter a lot in security: the <strong>instruction pointer</strong> (RIP on 64-bit x86) holds the address of the next instruction, and the <strong>stack pointer</strong> (RSP) tracks the top of the stack.</li>
<li><strong>Cores and threads</strong>: a 6 core CPU is six processors on one chip. Simultaneous multithreading (Intel calls it Hyper-Threading) lets one core run two instruction streams.</li>
<li><strong>Instruction set</strong>: the vocabulary a CPU understands. Laptops and servers mostly speak <strong>x86-64</strong>; phones, Apple M series Macs and many cloud servers speak <strong>ARM</strong>. Malware compiled for one will not run on the other without translation.</li>
</ul>
{stepper("Watch one instruction go through the CPU", "Click Next, or use the arrow keys.", [
  ("1. Fetch", "<p>The control unit reads the address in the instruction pointer, say <code>0x401000</code>, and pulls the bytes stored there from cache or RAM.</p><p>Bytes fetched: <code>48 01 D8</code></p>"),
  ("2. Decode", "<p>The decoder works out that <code>48 01 D8</code> means <code>add rax, rbx</code>: add the value in register RBX to register RAX.</p>"),
  ("3. Execute", "<p>The ALU adds the two numbers. If RAX held 40 and RBX held 2, RAX now holds 42. Flags are updated too, for example whether the result was zero.</p>"),
  ("4. Write back and advance", "<p>The result is stored, and the instruction pointer moves to the next instruction, <code>0x401003</code>. Then the loop repeats.</p>"),
  ("5. Where attacks hit", "<p>If an attacker can change the value in the instruction pointer, the CPU will happily fetch <em>their</em> bytes next. Classic buffer overflow exploits do exactly this by overwriting a saved return address on the stack. The CPU has no idea anything is wrong.</p>")])}
{attack("<p><strong>Control of the instruction pointer is the goal of most memory corruption exploits.</strong> In 2018 researchers also showed <strong>Spectre and Meltdown</strong>: CPUs that guess ahead (speculative execution) leave traces in the cache that a malicious program can measure to read memory it should never see. These were hardware design flaws, fixed partly by microcode updates and operating system patches.</p>")}
{defend("<p>Keep firmware, microcode and the OS updated, because CPU flaws are patched there. In malware analysis you will read CPU instructions (assembly) in tools like Ghidra, so a little x86 now pays off later.</p>")}''',
    hi="CPU ek hi loop chalata hai: instruction fetch karo, samjho (decode), chalao (execute), aage badho. Instruction pointer register batata hai agla kaam kahan hai. Attacker agar ye pointer control kar le, to CPU uska code chala dega. Isi ko memory corruption exploit kehte hain."))

  S.append(dict(id="memory", h="Memory: why RAM forgets and why that matters", hi_h="Memory: RAM bhoolti kyun hai",
    body=f'''<p>Storage is arranged as a hierarchy. The closer to the CPU, the faster and smaller it is.</p>
{fig(PYR, "Data moves up the pyramid when it is needed and down when it is not.", "Memory hierarchy")}
{table(["Level", "Typical size", "Rough access time", "Keeps data at power off?"], [
  ["Registers", "a few hundred bytes", "under 1 ns", "No"],
  ["L1 / L2 / L3 cache", "KB to tens of MB", "about 1 to 40 ns", "No"],
  ["RAM (DDR4, DDR5)", "8 to 64 GB on a PC", "about 50 to 100 ns", "No"],
  ["NVMe SSD", "256 GB to several TB", "tens of microseconds", "Yes"],
  ["Hard disk (HDD)", "1 TB and up", "several milliseconds", "Yes"]],
  "Memory hierarchy sizes and speeds")}
<p class="small muted">Numbers are typical orders of magnitude, not exact specs. The jump from RAM to a hard disk is roughly a hundred thousand times slower.</p>
<p><strong>RAM is volatile</strong>: it needs power to hold data. Everything a running program uses lives there: the document you are typing, decrypted files, session tokens and, very often, passwords in plain form for a short time.</p>
{analogy("<p>RAM is a whiteboard, storage is a notebook. You work on the whiteboard because it is fast, but it gets wiped when the lights go off. If you want to keep something you copy it into the notebook.</p>")}
{attack("<ul><li><strong>Credential theft from memory</strong>: tools like Mimikatz read the memory of the Windows LSASS process to pull password hashes and sometimes cleartext secrets.</li><li><strong>Cold boot attacks</strong>: RAM fades over seconds, not instantly. Researchers in 2008 showed that cooling memory chips keeps data readable long enough to dump encryption keys.</li><li><strong>Swap and hibernation files</strong> copy RAM to disk, so secrets can end up stored where you did not expect.</li></ul>")}
{defend("<p>Memory is evidence. Incident responders capture RAM <em>before</em> shutting a machine down, then analyse it with tools such as Volatility to find running malware, network connections and injected code that never touched the disk. Windows Credential Guard isolates LSASS secrets to make the Mimikatz style of theft much harder.</p>")}''',
    hi="RAM fast hai par power jaate hi sab bhool jaati hai. Running programs ke passwords aur keys RAM mein hote hain, isliye attacker memory padhne ki koshish karte hain. Defender ke liye RAM evidence hai: machine band karne se pehle memory dump lo."))

  S.append(dict(id="storage", h="Storage: disks, partitions and the myth of delete", hi_h="Storage: disk, partition aur delete ka sach",
    body=f'''<p>A <strong>hard disk</strong> stores bits magnetically on spinning platters. An <strong>SSD</strong> stores them as charge in flash memory cells, with no moving parts, which is why it is so much faster. Both present themselves to the OS as a long row of numbered blocks.</p>
<h3>Partitions and partition tables</h3>
<p>A disk is split into partitions, and a small table at the start records where each begins and ends.</p>
{table(["", "MBR (older)", "GPT (modern)"], [
  ["Introduced", "1983 with PC DOS 2.0", "with UEFI, in the 2000s"],
  ["Max disk size", "about 2 TiB with 512 byte sectors", "about 9.4 ZB, effectively unlimited"],
  ["Partitions", "4 primary (more via an extended partition)", "128 by default on Windows"],
  ["Firmware", "legacy BIOS", "UEFI"],
  ["Resilience", "single copy at the start", "backup header at the end of the disk, plus checksums"]],
  "MBR versus GPT")}
<p>Each partition is then formatted with a <strong>file system</strong> such as NTFS or ext4, which keeps an index of file names and where their blocks are. You will meet those in the next lesson.</p>
<h3>Delete does not mean gone</h3>
<p>When you delete a file, the file system usually just marks its blocks as free and removes the index entry. The bytes stay on the disk until something overwrites them. That is how forensic tools recover deleted photos and chats. SSDs complicate this: the <strong>TRIM</strong> command tells the drive which blocks are unused, and the drive may erase them in the background, so recovery from SSDs is much less reliable.</p>
{attack("<p>Sold or discarded laptops and pen drives regularly leak data because owners only deleted or quick formatted them. Attackers also hide data in places casual users never look, such as unallocated space or slack space at the end of a file's last block.</p>")}
{defend("<p>Turn on <strong>full disk encryption</strong> (BitLocker on Windows, FileVault on macOS, LUKS on Linux). Then a stolen or discarded disk is just noise without the key. Before giving away a device, use the built in reset that wipes encryption keys, or a proper secure erase tool for the drive type.</p>")}''',
    hi="Disk ko partitions mein baanta jaata hai (MBR purana, GPT naya). File delete karne se data turant nahi mitta, sirf jagah free mark hoti hai. Isliye purane phone ya pen drive se data recover ho sakta hai. Bachav: full disk encryption (BitLocker, LUKS)."))

  S.append(dict(id="binary-hex", h="Binary and hex: the language under everything", hi_h="Binary aur hex",
    body=f'''<p>A computer only stores two states, on and off, written as 1 and 0. One of these is a <strong>bit</strong>. Eight bits make a <strong>byte</strong>, which can hold 2<sup>8</sup> = 256 different values, from 0 to 255.</p>
<p>Each bit position is worth double the one to its right: 128, 64, 32, 16, 8, 4, 2, 1. To read <code>0100 0001</code>, add the positions that are on: 64 + 1 = 65.</p>
{bits()}
<h3>Why hexadecimal?</h3>
<p>Long binary strings are hard to read, so we use base 16. Hex digits go 0 to 9 and then A to F (A = 10, F = 15). The trick is that <strong>one hex digit is exactly four bits</strong>, so a byte is always two hex digits: <code>0100 0001</code> becomes <code>0x41</code>. Memory addresses, MAC addresses, colours on the web, hashes and file contents in a hex editor are all written this way.</p>
{table(["Decimal", "Binary", "Hex", "Where you see it"], [
  ["65", "0100 0001", "0x41", "ASCII letter A"],
  ["127", "0111 1111", "0x7F", "first byte of every Linux ELF program"],
  ["255", "1111 1111", "0xFF", "255.255.255.0 subnet masks, maximum byte"],
  ["77 and 90", "0100 1101 0101 1010", "4D 5A", "MZ, the first two bytes of every Windows .exe and .dll"]],
  "Number conversions")}
<p><strong>ASCII</strong> maps numbers to characters (65 is A, 97 is a, 48 is the digit 0). <strong>Unicode</strong> (usually stored as UTF-8) extends this to every script, including Devanagari, which matters for phishing because some letters from different scripts look identical.</p>
<h3>File signatures: the extension can lie, the bytes rarely do</h3>
{table(["File type", "First bytes (hex)", "As text"], [
  ["Windows program (.exe, .dll)", "4D 5A", "MZ"],
  ["Linux program (ELF)", "7F 45 4C 46", ".ELF"],
  ["PDF", "25 50 44 46", "%PDF"],
  ["ZIP, and anything built on ZIP (.docx, .xlsx, .apk, .jar)", "50 4B 03 04", "PK.."],
  ["PNG image", "89 50 4E 47", ".PNG"]],
  "Common magic bytes")}
{attack("<p>Scammers send <code>invoice.pdf.exe</code> and rely on Windows hiding known extensions, or rename an Android APK to look like a PDF. The magic bytes still say MZ or PK. In India, fake e-challan and wedding invite APKs spread exactly this way on WhatsApp.</p>")}
{defend("<p>Check what a file really is: on Linux run <code>file suspicious.pdf</code> or <code>head -c 8 suspicious.pdf | xxd</code>. On Windows, turn on <em>File name extensions</em> in File Explorer's View menu so double extensions stand out.</p>")}''',
    hi="Bit = 0 ya 1. Byte = 8 bits = 0 se 255. Hex mein ek digit 4 bits ke barabar hai, isliye ek byte = do hex digits (jaise 0x41 = A). File ki extension jhooth bol sakti hai, par shuru ke bytes (magic bytes) sach batate hain: MZ matlab Windows program, PK matlab ZIP ya APK."))

  S.append(dict(id="boot", h="Boot process: from power button to login screen", hi_h="Boot process: power button se login tak",
    body=f'''<p>Booting is a relay race. Each runner checks the next one and hands over control. Security depends on every hand-off being trustworthy, because whatever runs first can control everything after it.</p>
{stepper("Follow a modern UEFI boot", "Use Next or the arrow keys.", [
  ("1. Power on", "<p>The power supply stabilises and the CPU starts executing at a fixed address that points into firmware stored on a flash chip on the motherboard.</p>"),
  ("2. Firmware and POST", "<p>The firmware (UEFI on almost all PCs since about 2012, legacy BIOS before that) runs the <strong>Power-On Self Test</strong>: checks RAM, CPU and basic devices. Beep codes or an error screen here usually mean a hardware fault.</p>"),
  ("3. Secure Boot check", "<p>UEFI reads its boot order and finds the boot loader file on the EFI System Partition, for example <code>\\EFI\\Microsoft\\Boot\\bootmgfw.efi</code>. With <strong>Secure Boot</strong> on, it verifies the file's digital signature against trusted keys stored in firmware before running it.</p>"),
  ("4. Boot loader", "<p>Windows Boot Manager or GRUB (on Linux) loads the operating system kernel into RAM. GRUB is also where you can pick between two installed systems.</p>"),
  ("5. Kernel", "<p>The kernel (<code>ntoskrnl.exe</code> on Windows, <code>vmlinuz</code> on Linux) takes over the hardware, loads drivers and mounts the main file system.</p>"),
  ("6. First process", "<p>On Linux the kernel starts PID 1, usually <strong>systemd</strong>, which starts every service. On Windows the session manager <code>smss.exe</code> starts <code>wininit.exe</code> and <code>winlogon.exe</code>, which start services and the login screen.</p>"),
  ("7. Login", "<p>You sign in, your user session and desktop start, and startup programs run. This last step is a favourite place for malware to add itself.</p>")])}
{table(["", "Legacy BIOS", "UEFI"], [
  ["Era", "1980s to about 2012", "standard on PCs since Windows 8"],
  ["Mode", "16-bit, tiny code size", "32 or 64-bit, much richer"],
  ["Disk", "MBR", "GPT (MBR supported only through legacy compatibility mode, CSM)"],
  ["Signature checks", "none", "Secure Boot"],
  ["Windows 11", "not supported", "required, with TPM 2.0"]],
  "BIOS versus UEFI")}
{attack("<p><strong>Bootkits</strong> infect the early stages so they load before the OS and its antivirus. ESET documented <strong>LoJax</strong> in 2018, the first UEFI rootkit seen in the wild, written to the firmware flash chip so it survived even a disk replacement. In 2023 <strong>BlackLotus</strong> became the first public UEFI bootkit able to bypass Secure Boot on fully updated Windows 11, abusing an older signed boot component (CVE-2022-21894).</p>")}
{defend("<ul><li>Keep <strong>Secure Boot</strong> on and install firmware updates from the laptop or motherboard maker.</li><li>Set a firmware (BIOS/UEFI) admin password so nobody can change boot order and boot from a USB stick.</li><li>The <strong>TPM</strong> chip can measure each boot stage; BitLocker uses this so that a tampered boot chain asks for the recovery key.</li></ul>")}''',
    hi="Boot ek relay race hai: firmware (UEFI) se boot loader, phir kernel, phir pehla process (systemd ya wininit), phir login. Jo pehle chalta hai wo sab control karta hai, isliye bootkits isi chain ko target karte hain. Secure Boot har step ka signature check karta hai, use on rakho."))

  return dict(
    slug="learn-how-computers-work", stage=1, n="1.1", minutes=45, level="Beginner",
    title="How a Computer Works", short="CPU, RAM, storage, binary and hex, and the boot process, through a security lens.",
    seo_title="How a Computer Works for Cybersecurity: CPU, RAM, Boot, Binary | CyberWithMadhav",
    desc="Free lesson: how the CPU, RAM, storage, binary, hex and the BIOS/UEFI boot process work, and how attackers abuse each one. With quiz, flashcards and a VM lab.",
    kw="how a computer works, cpu ram storage, bios vs uefi, boot process, binary to hex, magic bytes, computer fundamentals for cybersecurity",
    kicker="$ lesson 1.1 --stage foundations", hi_title="Computer kaise kaam karta hai",
    lead="Before you can secure a machine you need to know what is inside it. This lesson walks through the CPU, memory, storage, binary and the boot process, and at every step shows where attackers strike and how defenders respond.",
    hi_lead="Machine secure karne se pehle samjho uske andar kya hai. CPU, memory, storage, binary aur boot process, aur har step pe attacker kahan hit karta hai aur defender kya karta hai.",
    goals=["Explain what the CPU, RAM and storage each do, and why RAM is volatile", "Follow the fetch, decode, execute cycle and say why the instruction pointer matters", "Convert between binary, decimal and hex, and identify a file by its magic bytes", "Describe the UEFI boot chain, Secure Boot and how bootkits attack it"],
    sections=S,
    cards=[("What does the instruction pointer hold?", "The memory address of the next instruction the CPU will run. Hijacking it is the aim of most memory corruption exploits."),
      ("Why is RAM called volatile?", "It needs power to hold data. Contents fade within seconds to minutes once power is cut."),
      ("How many bits is one hex digit?", "Four. So one byte is always exactly two hex digits, 00 to FF."),
      ("What are the first two bytes of a Windows .exe?", "4D 5A, which is MZ in ASCII."),
      ("What does Secure Boot check?", "The digital signature of each boot component, starting with the boot loader, against keys trusted by the firmware."),
      ("Why can deleted files be recovered?", "Deleting usually just marks blocks as free. The bytes stay until overwritten (less true on SSDs because of TRIM)."),
      ("MBR or GPT for a 4 TB disk?", "GPT. MBR tops out at about 2 TiB with 512 byte sectors."),
      ("What is 0xFF in decimal?", "255, all eight bits set.")],
    quiz=[("Which component holds the data of programs that are running right now?", ["SSD", "RAM", "GPU", "Firmware chip"], 1, "Running programs live in RAM. Storage keeps files when the power is off."),
      ("An attachment is named <code>marksheet.pdf</code> but its first bytes are <code>4D 5A</code>. What is it really?", ["A normal PDF", "A ZIP archive", "A Windows executable", "A PNG image"], 2, "4D 5A (MZ) is the signature of Windows executables. A real PDF starts with %PDF."),
      ("Binary <code>1100 1000</code> is which decimal number?", ["200", "196", "136", "100"], 0, "128 + 64 + 8 = 200."),
      ("Why do incident responders capture RAM before switching a suspicious machine off?", ["RAM is encrypted at shutdown", "Running malware, keys and connections are only in memory and vanish at power off", "Windows deletes logs at shutdown", "It makes the disk image smaller"], 1, "Memory is volatile. Fileless malware and live network connections exist only there."),
      ("What did the BlackLotus bootkit (2023) show?", ["Secure Boot can be bypassed by abusing old, still trusted signed components", "BIOS is safer than UEFI", "SSDs cannot be infected", "TPM chips store malware"], 0, "BlackLotus abused a vulnerable but still signed Windows boot component (CVE-2022-21894) to get past Secure Boot."),
      ("Which statement about deleting a file on a hard disk is true?", ["The bytes are overwritten with zeros immediately", "The file system marks the space as free, and the data stays until overwritten", "The file moves to the BIOS", "It is encrypted automatically"], 1, "That is why forensic recovery works, and why full disk encryption matters for discarded drives.")],
    lab=dict(title="Lab: look inside your own machine", time="30 to 45 minutes",
      needs="A laptop or PC with VirtualBox installed, and an Ubuntu 24.04 LTS ISO (free from ubuntu.com). Windows steps use your own Windows PC.",
      steps=[("Create a VM and choose the firmware type", "<p>In VirtualBox click <strong>New</strong>, pick the Ubuntu ISO, and give it 2 CPUs, 4 GB RAM and a 25 GB disk. Before the first boot open <strong>Settings, System, Motherboard</strong> (switch to Expert mode if you do not see it) and note whether <strong>Enable EFI</strong> is ticked. Install Ubuntu.</p>"),
        ("Take a snapshot", "<p>With the VM powered off, open the VM's Snapshots view and click <strong>Take</strong>. Name it <code>clean-install</code>. You can now break anything and roll back in seconds.</p>"),
        ("Check BIOS or UEFI from inside Linux", code(["$ [ -d /sys/firmware/efi ] && echo UEFI || echo 'Legacy BIOS'", "$ sudo mokutil --sb-state"], "Firmware check") + "<p><code>mokutil</code> reports whether Secure Boot is on (install it with <code>sudo apt install mokutil</code> if missing). Now power off, flip the EFI setting, and try booting again. A system installed in UEFI mode will not boot in legacy mode: you just saw why the firmware type matters.</p><p>Flip it back before continuing.</p>"),
        ("Inspect CPU, RAM and disks", code(["$ lscpu | head -20", "$ free -h", "$ lsblk -f", "$ sudo fdisk -l /dev/sda | head"], "Hardware inspection") + "<p>Find the architecture (x86_64), number of CPUs, total RAM, and whether the disk label type is <code>gpt</code> or <code>dos</code> (MBR).</p>"),
        ("Read magic bytes", code(["$ head -c 4 /bin/ls | xxd", "$ cp /bin/ls ~/holiday.pdf", "$ file ~/holiday.pdf", "$ head -c 4 ~/holiday.pdf | xxd"], "Magic bytes") + "<p>The copy is named like a PDF but <code>file</code> and the bytes <code>7f45 4c46</code> say ELF program. Delete it after: <code>rm ~/holiday.pdf</code>.</p>"),
        ("Check your real Windows PC", "<p>On your own Windows machine press <kbd>Win</kbd> + <kbd>R</kbd>, run <code>msinfo32</code>, and read <strong>BIOS Mode</strong> (UEFI or Legacy) and <strong>Secure Boot State</strong>. Turn on <em>File name extensions</em> in File Explorer if it is off.</p>")],
      verify="You can say your VM's firmware type, Secure Boot state, CPU architecture and partition table type, and you identified a file by its bytes instead of its name."),
    takeaways=["The CPU only fetches, decodes and executes. Whoever controls the instruction pointer controls the machine.",
      "RAM holds live secrets and live evidence; it disappears at power off.",
      "Deleted is not erased. Full disk encryption protects discarded and stolen drives.",
      "Hex is binary made readable: one hex digit per four bits. Trust magic bytes over file extensions.",
      "The boot chain is only as strong as its first link. Keep Secure Boot on and firmware updated."])


def lesson_os():
  S = []
  S.append(dict(id="what-os-does", h="What an operating system actually does", hi_h="Operating system asal mein kya karta hai",
    body=f'''<p>An operating system has two jobs. It is a <strong>referee</strong> that shares the CPU, memory, disk and network fairly between dozens of programs, and it is a <strong>translator</strong> that gives programs simple commands like "open this file" instead of making each one talk to disk controllers directly.</p>
<p>The core of the OS is the <strong>kernel</strong>. It runs in a privileged CPU mode (kernel mode, often called ring 0 on x86) where it can touch any memory and any device. Everything else, including your browser, terminal and antivirus user interface, runs in <strong>user mode</strong> (ring 3) with restricted rights.</p>
{fig(RINGS, "A crash in user mode kills one app. A bug in kernel mode can take down or take over the whole machine.", "User mode and kernel mode")}
{table(["Kernel design", "Idea", "Examples"], [
  ["Monolithic", "most OS services (drivers, file systems, networking) run inside the kernel for speed", "Linux"],
  ["Hybrid", "a monolithic style kernel with some microkernel ideas and parts moved out", "Windows NT family, macOS (XNU)"],
  ["Microkernel", "only the bare minimum in the kernel; drivers and services run as separate user processes", "QNX, seL4, MINIX 3"]],
  "Kernel designs")}
{analogy("<p>A bank branch. Customers (programs) cannot walk into the vault (hardware). They fill a slip at the counter (a system call), and the staff (kernel) checks the slip and fetches what is allowed. A customer who forges slips is a malware author; a staff member who can be bribed is a kernel vulnerability.</p>")}
{attack("<p>The prize for an attacker is code running in kernel mode, because from there security software can be blinded. That is why malicious or vulnerable drivers are so dangerous. In <strong>BYOVD</strong> (bring your own vulnerable driver) attacks, ransomware groups load a legitimately signed but buggy driver and use it to switch off endpoint protection.</p>")}''',
    hi="OS do kaam karta hai: resources baantna (referee) aur programs ko simple commands dena (translator). Kernel sabse powerful hissa hai jo kernel mode mein chalta hai. Apps user mode mein chalti hain. Attacker ka sapna hai kernel mode mein code chalana."))

  S.append(dict(id="syscalls", h="System calls: the only door into the kernel", hi_h="System calls: kernel ka darwaza",
    body=f'''<p>When a program wants something only the kernel can do, it makes a <strong>system call</strong>: it puts a call number and arguments in registers and executes a special instruction (<code>syscall</code> on x86-64) that switches the CPU into kernel mode at a fixed entry point. The kernel checks permissions, does the work and returns.</p>
{table(["Task", "Linux system call", "Windows (documented API, then native call)"], [
  ["Open a file", "<code>openat</code>", "<code>CreateFileW</code> then <code>NtCreateFile</code>"],
  ["Read data", "<code>read</code>", "<code>ReadFile</code> then <code>NtReadFile</code>"],
  ["Start a program", "<code>fork</code> / <code>clone</code> then <code>execve</code>", "<code>CreateProcessW</code> then <code>NtCreateUserProcess</code>"],
  ["Network connection", "<code>socket</code>, <code>connect</code>", "Winsock <code>connect</code>, handled by the AFD driver"],
  ["Allocate memory", "<code>mmap</code>, <code>brk</code>", "<code>VirtualAlloc</code> then <code>NtAllocateVirtualMemory</code>"]],
  "System calls")}
<p>You can watch system calls happen. On Linux, <code>strace</code> prints every call a program makes:</p>
{code(["$ strace -e trace=openat,execve cat /etc/hostname", 'execve("/usr/bin/cat", ["cat", "/etc/hostname"], ...) = 0', 'openat(AT_FDCWD, "/etc/hostname", O_RDONLY) = 3', "cwm-lab"], "strace example", copy=False)}
{attack("<p>Many security products watch Windows API calls by placing hooks in <code>ntdll.dll</code> inside each process. Malware answers with <strong>direct or indirect system calls</strong>, invoking the kernel itself so the hooks never see the request.</p>")}
{defend("<p>Watch from where malware cannot easily hide: the kernel. Windows offers <strong>ETW</strong> (Event Tracing for Windows) and kernel callbacks used by modern EDR tools; Linux offers <strong>eBPF</strong>, which tools such as Falco and Tetragon use to observe system calls with low overhead.</p>")}''',
    hi="Program jab file kholna, network use karna ya naya program chalana chahta hai, to system call karta hai. Linux pe strace se ye calls dekh sakte ho. Malware hooks se bachne ke liye seedha syscall karta hai, isliye defenders kernel level telemetry (ETW, eBPF) use karte hain."))

  S.append(dict(id="processes", h="Processes and threads: programs come alive", hi_h="Processes aur threads",
    body=f'''<p>A <strong>program</strong> is a file on disk. A <strong>process</strong> is that program loaded into memory and running, with its own private memory, open files, a security identity and at least one <strong>thread</strong> (a single line of execution the scheduler can run). Threads in the same process share its memory.</p>
<p>Every process gets a <strong>PID</strong> (process ID) and remembers its parent's PID (<strong>PPID</strong>). Together they form a tree, and that tree is one of the best tools a defender has.</p>
{stepper("What happens when you type ls and press Enter", "Linux shown; Windows does the same in one CreateProcess call.", [
  ("1. The shell reads your command", "<p>Bash (PID 1201) parses <code>ls -l</code> and searches each folder in <code>$PATH</code> until it finds <code>/usr/bin/ls</code>.</p>"),
  ("2. fork", "<p>Bash calls <code>fork()</code> (in practice <code>clone()</code>). The kernel creates a near copy of bash, PID 1388, with PPID 1201.</p>"),
  ("3. execve", "<p>The child calls <code>execve(\"/usr/bin/ls\", ...)</code>. The kernel throws away the copied bash memory and loads the ls program, its libraries and a fresh stack. Same PID, new program.</p>"),
  ("4. Scheduling", "<p>The process is placed in the <strong>ready</strong> queue. The scheduler gives it CPU time slices, switching between processes many times per second (a <strong>context switch</strong> saves and restores registers).</p>"),
  ("5. Waiting", "<p>When ls asks for the directory contents it may wait for the disk. It moves to <strong>waiting</strong> (blocked) so other processes can use the CPU.</p>"),
  ("6. Exit", "<p>ls prints its output and calls <code>exit</code>. It becomes a <strong>zombie</strong> for a moment until bash collects its exit code with <code>wait()</code>, and then it is gone.</p>")])}
{code(["$ ps -ef --forest | tail -5", "student   1201   1190  0 09:30 pts/0  00:00:00 -bash", "student   1388   1201  0 09:41 pts/0  00:00:00  \\_ ps -ef --forest"], "Process tree", copy=False)}
{attack("<ul><li><strong>Suspicious parents</strong>: Word or Excel starting <code>powershell.exe</code> or <code>cmd.exe</code> is a classic sign of a malicious macro.</li><li><strong>Masquerading</strong>: malware named <code>svch0st.exe</code> or a real name like <code>svchost.exe</code> running from the wrong folder.</li><li><strong>Process injection</strong>: writing code into another, trusted process so the malicious work appears to come from it.</li></ul>")}
{defend("<p>Always ask three questions about a process: <em>who is its parent</em>, <em>where is its file on disk</em>, and <em>which user is it running as</em>. On Windows, Sysinternals <strong>Process Explorer</strong> and <strong>Sysmon</strong> event ID 1 (process creation with command line and parent) answer all three.</p>")}''',
    hi="Program disk pe file hai, process wahi program jab RAM mein chal raha ho. Har process ka PID aur parent ka PPID hota hai. Defender ke teen sawaal: parent kaun hai, file kahan hai, kaunsa user chala raha hai. Word se PowerShell khulna red flag hai."))

  S.append(dict(id="virtual-memory", h="Memory management: every process lives in its own illusion", hi_h="Virtual memory",
    body=f'''<p>Each process believes it has a huge, private address space starting near zero. That is <strong>virtual memory</strong>. The CPU's memory management unit (MMU) translates every virtual address into a real physical RAM address using <strong>page tables</strong> the kernel maintains. Memory is handled in <strong>pages</strong>, usually 4 KiB each.</p>
<ul>
<li><strong>Isolation</strong>: process A simply has no mapping for process B's pages, so it cannot read them. That is a security boundary built into hardware.</li>
<li><strong>Swapping</strong>: rarely used pages can be moved to disk (a swap partition on Linux, <code>pagefile.sys</code> on Windows) and brought back when touched.</li>
<li><strong>Permissions per page</strong>: each page can be readable, writable and executable, or not.</li>
</ul>
{fig(LAYOUT, "Simplified layout. Real systems randomise where each region starts.", "Process memory layout")}
<h3>Built in defences against memory attacks</h3>
{table(["Defence", "What it does", "What it stops"], [
  ["DEP / NX bit", "marks stack and heap pages as non-executable", "running shellcode placed in a data buffer"],
  ["ASLR", "randomises where the stack, heap, libraries and program load", "hard coded addresses in exploits"],
  ["Stack canaries", "a secret value before the return address, checked before returning", "simple stack buffer overflows"],
  ["CFG, CET shadow stack", "check that indirect calls and returns go to valid places", "return oriented programming"]],
  "Memory protections")}
{attack("<p>Attackers chain bugs: an <strong>information leak</strong> reveals an address to defeat ASLR, then a <strong>buffer overflow</strong> or <strong>use-after-free</strong> corrupts memory, and <strong>return oriented programming</strong> reuses small pieces of existing code to get around DEP. Browser and phone exploits sold for large sums usually chain several such bugs.</p>")}
{defend("<p>Check that ASLR is on in Linux: <code>cat /proc/sys/kernel/randomize_va_space</code> should print <code>2</code>. On Windows, <em>Exploit protection</em> in Windows Security shows DEP, ASLR and CFG settings. Writing software in memory safe languages such as Rust removes whole classes of these bugs.</p>")}''',
    hi="Har process ko lagta hai uske paas apni private memory hai (virtual memory). MMU aur page tables isse asli RAM se jodte hain, isliye ek process doosre ki memory nahi padh sakta. ASLR, DEP aur stack canaries jaise defences memory attacks ko mushkil banate hain."))

  S.append(dict(id="file-systems", h="File systems: how names become bytes", hi_h="File systems",
    body=f'''<p>A file system turns a raw partition into folders and files. It stores the <strong>data</strong>, and separately the <strong>metadata</strong>: name, size, owner, permissions, timestamps and the list of blocks holding the content.</p>
<ul>
<li>Linux <strong>ext4</strong> keeps metadata in an <strong>inode</strong> per file. The file name lives in the directory entry that points to the inode, which is why one file can have several names (hard links). See inode numbers with <code>ls -i</code>.</li>
<li>Windows <strong>NTFS</strong> keeps a record for every file in the <strong>Master File Table</strong> (<code>$MFT</code>), a goldmine for forensic investigators.</li>
</ul>
{table(["File system", "Used by", "Notes for security"], [
  ["NTFS", "Windows system drives", "permissions (ACLs), journaling, encryption via BitLocker or EFS, alternate data streams"],
  ["ext4", "most Linux distributions", "Unix permissions, journaling, inodes"],
  ["XFS, Btrfs", "RHEL family servers, Fedora, some NAS boxes", "Btrfs has snapshots useful for ransomware recovery"],
  ["APFS", "macOS, iOS", "built in encryption and snapshots"],
  ["FAT32", "old pen drives, EFI System Partition", "no permissions at all, 4 GiB maximum file size"],
  ["exFAT", "SD cards, large pen drives", "no permissions, no journal"]],
  "Common file systems")}
<h3>Timestamps tell stories</h3>
<p>File systems record when a file was modified, accessed, had its metadata changed, and (on NTFS and newer ext4) created. Investigators build <strong>timelines</strong> from these to reconstruct an attack minute by minute.</p>
{attack("<ul><li><strong>Timestomping</strong>: malware resets its own timestamps to match old system files so it blends in.</li><li><strong>Alternate data streams</strong>: NTFS lets a file carry hidden extra streams, like <code>notes.txt:payload.exe</code>, that do not appear in normal listings.</li><li>Copying files to FAT32 or exFAT pen drives silently strips all permissions.</li></ul>")}
{defend("<p>That hidden stream feature is also used for good. When you download a file, Windows adds a <code>Zone.Identifier</code> stream, the <strong>Mark of the Web</strong>, which triggers SmartScreen and Office's Protected View. View it with <code>Get-Item file.docx -Stream *</code> in PowerShell.</p>")}''',
    hi="File system naam ko asli bytes se jodta hai aur metadata rakhta hai: owner, permissions, timestamps. Linux pe inode, Windows NTFS pe MFT. Investigators timestamps se timeline banate hain. Attacker timestamps badal sakta hai (timestomping) ya NTFS streams mein cheezein chhupa sakta hai."))

  S.append(dict(id="users-permissions", h="Users, permissions and privilege", hi_h="Users, permissions aur privilege",
    body=f'''<p>Every process runs <strong>as some user</strong>, and the OS checks that identity on every file open and system call. That is what stops one user from reading another's files.</p>
{table(["", "Linux and macOS", "Windows"], [
  ["Most powerful account", "<code>root</code>, user ID 0", "<code>NT AUTHORITY\\SYSTEM</code> for the OS, plus members of Administrators"],
  ["Identity number", "UID and GID", "SID, for example S-1-5-18 is SYSTEM"],
  ["Who may do what", "owner, group, others with read, write, execute bits", "access control lists (ACLs) on each object"],
  ["Temporary elevation", "<code>sudo</code>", "User Account Control (UAC) prompt"],
  ["Extra mandatory controls", "SELinux, AppArmor", "integrity levels, AppLocker, WDAC"]],
  "Accounts and permissions")}
<p>Most permission systems you meet are <strong>discretionary access control</strong> (DAC): the owner of a file decides who else can use it. <strong>Mandatory access control</strong> (MAC) adds rules set by the administrator that even owners cannot override, which is why a compromised web server process under SELinux still cannot read home folders.</p>
<h3>Privilege escalation</h3>
<p>Attackers usually land as a low privileged user, for example through a phishing document or a web bug, and then try to climb. <strong>Vertical</strong> escalation means becoming admin or root. <strong>Horizontal</strong> means becoming another user at the same level, perhaps one with access to payroll files.</p>
{analogy("<p>An office building. Your ID card opens your floor (user). Facilities staff have master keys (root or SYSTEM). A visitor badge (a web server account) should open only the lobby. Privilege escalation is finding a master key left in a drawer.</p>")}
{attack("<p>Common climbs: misconfigured <code>sudo</code> rules, programs with the Linux SUID bit, Windows services whose files any user can overwrite, saved passwords in scripts, and unpatched kernel bugs. Lists such as GTFOBins and LOLBAS catalogue built in programs that can be abused this way.</p>")}
{defend("<p><strong>Least privilege</strong>: give each person and service only what it needs. Use a normal account day to day and a separate admin account only when needed. Remove old accounts. Patch quickly, because many escalations rely on public bugs.</p>")}''',
    hi="Har process kisi user ke naam se chalta hai aur OS har kaam pe permission check karta hai. Linux mein root (UID 0), Windows mein SYSTEM aur Administrators sabse powerful hain. Attacker chhote user se shuru karke upar chadhta hai (privilege escalation). Bachav: least privilege, roz normal account use karo."))

  return dict(
    slug="learn-operating-system-fundamentals", stage=1, n="1.2", minutes=50, level="Beginner",
    title="Operating System Fundamentals", short="Kernel, system calls, processes, virtual memory, file systems and permissions.",
    seo_title="Operating System Fundamentals for Cybersecurity: Kernel, Processes, Memory | CyberWithMadhav",
    desc="Free lesson on how operating systems work: kernel and user mode, system calls, processes, virtual memory, ASLR, file systems, users and privilege escalation.",
    kw="operating system fundamentals, kernel vs user mode, system calls, process tree, virtual memory aslr, file systems ntfs ext4, privilege escalation basics",
    kicker="$ lesson 1.2 --stage foundations", hi_title="Operating system ke fundamentals",
    lead="Windows, Linux, Android and macOS look different, but underneath they solve the same problems in similar ways. Learn the kernel, processes, memory, file systems and permissions once, and every OS starts to make sense, including how attackers move through it.",
    hi_lead="Windows, Linux, Android, macOS alag dikhte hain par andar se same problems solve karte hain. Kernel, processes, memory, file systems aur permissions ek baar samjho, phir har OS samajh aayega.",
    goals=["Explain kernel mode, user mode and why system calls exist", "Trace how a process is created and read a process tree like an analyst", "Describe virtual memory and the protections ASLR, DEP and stack canaries", "Compare file systems and explain inodes, the MFT and timestamps", "Explain users, permissions, least privilege and privilege escalation"],
    sections=S,
    cards=[("Kernel mode vs user mode?", "Kernel mode can access all memory and hardware. User mode is restricted; programs must ask the kernel through system calls."),
      ("What is a PPID?", "The parent process ID: which process started this one. Unusual parents are a strong attack signal."),
      ("What does ASLR do?", "Randomises where code, libraries, stack and heap are loaded so exploits cannot rely on fixed addresses."),
      ("Where does NTFS keep file records?", "In the Master File Table, $MFT."),
      ("What is a zombie process?", "A process that has exited but whose exit status has not yet been collected by its parent."),
      ("UID of root?", "0. Any account with UID 0 has root powers, whatever its name."),
      ("What is BYOVD?", "Bring your own vulnerable driver: loading a signed but buggy driver to get kernel access and disable security tools."),
      ("Mark of the Web?", "A Zone.Identifier alternate data stream Windows adds to downloaded files, used by SmartScreen and Office Protected View.")],
    quiz=[("A program wants to read a file. What must it do?", ["Read the disk sectors directly", "Make a system call so the kernel checks permission and reads it", "Ask the BIOS", "Nothing, all memory is shared"], 1, "User mode code cannot touch hardware. The kernel mediates every file access."),
      ("Which process tree is the strongest sign of a malicious document?", ["explorer.exe starting chrome.exe", "services.exe starting svchost.exe", "winword.exe starting powershell.exe", "bash starting ls"], 2, "Office apps rarely need to start PowerShell. It is a common macro malware pattern."),
      ("<code>cat /proc/sys/kernel/randomize_va_space</code> prints 0. What does that mean?", ["ASLR is fully on", "ASLR is off", "The kernel is 32-bit", "Swap is disabled"], 1, "0 means no randomisation. 2 is the normal full setting."),
      ("Why can malware avoid user mode API hooks?", ["By making system calls directly", "By running on FAT32", "By using a longer file name", "By lowering its priority"], 0, "Direct or indirect syscalls skip hooked functions in ntdll.dll."),
      ("A web server process is compromised, but SELinux prevents it reading users' home folders. That is an example of:", ["Discretionary access control", "Mandatory access control", "ASLR", "Timestomping"], 1, "MAC policies are set by the administrator and apply even if file permissions would allow access."),
      ("An attacker logged in as a normal user becomes root. This is:", ["Horizontal privilege escalation", "Vertical privilege escalation", "Lateral movement", "Persistence"], 1, "Vertical means moving to a higher privilege level.")],
    lab=dict(title="Lab: watch the OS at work", time="40 minutes",
      needs="Your Ubuntu VM from lesson 1.1 (restore the clean-install snapshot if you broke it). Optional: your own Windows PC.",
      steps=[("See the process tree", code(["$ ps -ef --forest | less", "$ pstree -p | head -30", "$ echo $$"], "Process tree") + "<p><code>$$</code> is your shell's PID. Find it in the tree and follow the parents up to PID 1. What is PID 1 called?</p>"),
        ("Trace system calls", code(["$ sudo apt install -y strace", "$ strace -c ls /etc > /dev/null", "$ strace -e trace=openat cat /etc/hostname"], "strace") + "<p>The <code>-c</code> summary shows how many calls of each type a tiny command makes. Note how many files <code>cat</code> opens before it reaches the one you asked for (libraries and locale files).</p>"),
        ("Look at a process's memory map", code(["$ cat /proc/self/maps | head -20", "$ cat /proc/sys/kernel/randomize_va_space", "$ cat /proc/self/maps | grep stack; cat /proc/self/maps | grep stack"], "Memory maps") + "<p>Run the last line twice: the stack address changes each run. That is ASLR working. Find the pages marked <code>r-xp</code> (code) and <code>rw-p</code> (data).</p>"),
        ("Inodes, links and timestamps", code(["$ cd ~ && echo hello > a.txt", "$ ln a.txt b.txt && ls -li a.txt b.txt", "$ stat a.txt", "$ touch -d '2020-01-01 10:00' a.txt && stat a.txt"], "Inodes and timestamps") + "<p>Both names share one inode number. The <code>touch -d</code> line is a harmless timestomp on your own file: notice which timestamp changed and which one (Change) still shows the real time. Investigators use exactly that mismatch.</p>"),
        ("Users and permissions", code(["$ id", "$ sudo useradd -m labuser", "$ sudo -u labuser cat /home/student/a.txt", "$ chmod 600 ~/a.txt && sudo -u labuser cat /home/student/a.txt", "$ sudo userdel -r labuser"], "Users") + "<p>Notice the second read fails with Permission denied (if your home folder is not readable by others the first may fail too, which is also a lesson). Replace <code>student</code> with your own user name.</p>"),
        ("Windows: the same ideas", "<p>On your own Windows PC open Task Manager, Details tab, right click a column header, <strong>Select columns</strong>, and add <em>Command line</em> and <em>Elevated</em>. Then download <strong>Process Explorer</strong> from Microsoft Sysinternals (learn.microsoft.com/sysinternals) and view the process tree. Find <code>lsass.exe</code> and check its parent.</p>")],
      verify="You can name PID 1, show ASLR changing addresses, explain why two file names had one inode, and point to a process's parent on both Linux and Windows."),
    takeaways=["The kernel is the referee; system calls are the only legitimate way in.",
      "Read processes as a family tree: parent, path and user tell you if something is wrong.",
      "Virtual memory isolates processes. ASLR, DEP and canaries make memory bugs harder, not impossible.",
      "Metadata and timestamps are evidence, and attackers try to fake them.",
      "Least privilege limits how far one compromised account can go."])
