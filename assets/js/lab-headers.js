/* Email Header Forensics. Parses pasted headers in this browser. Nothing is uploaded or stored.
   The optional SPF and DMARC lookup sends only the sender's domain name to Cloudflare DNS, and only after a click. */
(function () {
  'use strict';
  const L = window.CWMLab, { el, finding } = L, $ = s => document.querySelector(s);
  const SAMPLES = {
    phish: `Delivered-To: student@example.com
Received: by 2002:a05:6a10:8f12:b0:5c1:2a3:4b5 with SMTP id x12csp1234567;
        Mon, 23 Nov 2026 05:15:09 -0800 (PST)
Received: from mail.sbi-kyc-update.example (mail.sbi-kyc-update.example. [203.0.113.45])
        by mx.example.com with ESMTPS id a1b2c3d4e5;
        Mon, 23 Nov 2026 05:15:07 -0800 (PST)
Received: from [192.168.1.20] (unknown [198.51.100.7])
        by mail.sbi-kyc-update.example (Postfix) with ESMTPA id 4F2A1;
        Mon, 23 Nov 2026 18:44:58 +0530 (IST)
Authentication-Results: mx.example.com;
       dkim=none;
       spf=softfail (domain of transitioning bounce@mailer-7.example.net does not designate 203.0.113.45 as permitted sender) smtp.mailfrom=bounce@mailer-7.example.net;
       dmarc=fail (p=NONE sp=NONE dis=NONE) header.from=sbi-kyc-update.example
Return-Path: <bounce@mailer-7.example.net>
From: "State Bank of India KYC Team" <alerts@sbi-kyc-update.example>
Reply-To: sbi.kyc.helpdesk@gmail.com
To: student@example.com
Subject: URGENT: Your YONO account will be blocked today, update PAN now
Date: Mon, 23 Nov 2026 18:44:51 +0530
Message-ID: <20261123131451.ABC123@mailer-7.example.net>
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8`,
    clean: `Delivered-To: madhav@example.com
Received: by 2002:a05:6a10:8f12:b0:5c1:2a3:4b5 with SMTP id y45csp7654321;
        Mon, 23 Nov 2026 02:10:04 -0800 (PST)
Received: from mail-sor-f41.example.com (mail-sor-f41.example.com. [192.0.2.41])
        by mx.example.com with SMTPS id k9-20020a05;
        Mon, 23 Nov 2026 02:10:03 -0800 (PST)
Authentication-Results: mx.example.com;
       dkim=pass header.i=@college.example.ac.in header.s=google header.b=Ab12Cd34;
       spf=pass (domain of hod.cs@college.example.ac.in designates 192.0.2.41 as permitted sender) smtp.mailfrom=hod.cs@college.example.ac.in;
       dmarc=pass (p=QUARANTINE sp=QUARANTINE dis=NONE) header.from=college.example.ac.in
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=college.example.ac.in; s=google; h=from:to:subject:date:message-id; bh=abc=; b=xyz=
Return-Path: <hod.cs@college.example.ac.in>
From: "HoD Computer Science" <hod.cs@college.example.ac.in>
To: madhav@example.com
Subject: Cyber awareness session on 5 December
Date: Mon, 23 Nov 2026 15:39:52 +0530
Message-ID: <CAF3x9Q@mail.college.example.ac.in>
MIME-Version: 1.0`
  };
  const PRESSURE = ['urgent', 'immediately', 'blocked', 'block', 'suspend', 'suspended', 'kyc', 'pan', 'verify', 'refund', 'prize', 'lottery', 'winner',
    'arrest', 'court', 'police', 'cbi', 'disconnect', 'disconnection', 'penalty', 'challan', 'expire', 'expired', 'last', 'today', 'otp', 'reward', 'job'];

  function parse(text) {
    const lines = String(text || '').replace(/\r\n?/g, '\n').split('\n');
    const hdrs = []; let started = false;
    for (const line of lines) {
      if (!line.trim()) { if (started) break; else continue; }
      if (/^[ \t]/.test(line) && hdrs.length) { hdrs[hdrs.length - 1].v += ' ' + line.trim(); continue; }
      const m = /^([!-9;-~]+):\s?(.*)$/.exec(line);
      if (m) { hdrs.push({ n: m[1], k: m[1].toLowerCase(), v: m[2].trim() }); started = true; }
    }
    return hdrs;
  }
  const get = (h, k) => h.filter(x => x.k === k).map(x => x.v);
  function addr(v) {
    if (!v) return null;
    const m = /^(.*?)<([^>]+)>/.exec(v);
    let name = m ? m[1].trim().replace(/^"|"$/g, '').trim() : '', a = (m ? m[2] : v).trim().replace(/^<|>$/g, '');
    const am = /[^\s<>"]+@[^\s<>"]+/.exec(a); a = am ? am[0].toLowerCase() : a.toLowerCase();
    const dom = a.includes('@') ? a.split('@').pop().replace(/[>.]+$/, '') : '';
    return { name, addr: a, domain: dom, reg: L.registrable(dom) };
  }
  function parseDate(s) { if (!s) return null; const t = Date.parse(s.replace(/\([^)]*\)/g, '').trim()); return isNaN(t) ? null : new Date(t); }
  function hops(h) {
    return get(h, 'received').map(v => {
      const semi = v.lastIndexOf(';');
      const body = semi >= 0 ? v.slice(0, semi) : v;
      const from = /\bfrom\s+(\S+)/i.exec(body), by = /\bby\s+(\S+)/i.exec(body), wth = /\bwith\s+(\S+)/i.exec(body);
      const IPRE = /\[((?:\d{1,3}\.){3}\d{1,3}|[0-9a-f:]{3,})\]/i;
      const paren = /\bfrom\s+\S+\s+\(([^)]*)\)/i.exec(body);
      const ip = (paren && IPRE.exec(paren[1])) || IPRE.exec(body);
      return { from: from ? from[1] : '', by: by ? by[1] : '', with: wth ? wth[1] : '', ip: ip ? ip[1] : '', date: parseDate(semi >= 0 ? v.slice(semi + 1) : ''), raw: v };
    }).reverse();
  }
  function isPrivate(ip) { return /^(10\.|127\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|169\.254\.)/.test(ip) || /^(::1|fc|fd|fe80)/i.test(ip); }
  function authResults(h) {
    const ar = get(h, 'authentication-results');
    const r = { spf: null, dkim: null, dmarc: null, headerFrom: null, mailFrom: null, dkimD: null, src: ar[0] || null };
    if (ar.length) {
      const v = ar[0];
      ['spf', 'dkim', 'dmarc'].forEach(k => { const m = new RegExp('\\b' + k + '=(\\w+)', 'i').exec(v); if (m) r[k] = m[1].toLowerCase(); });
      const hf = /header\.from=([^\s;]+)/i.exec(v); if (hf) r.headerFrom = hf[1].toLowerCase();
      const mf = /smtp\.mailfrom=([^\s;]+)/i.exec(v); if (mf) r.mailFrom = mf[1].toLowerCase();
      const hd = /header\.(?:d|i)=@?([^\s;]+)/i.exec(v); if (hd) r.dkimD = hd[1].toLowerCase().replace(/^.*@/, '');
    }
    if (!r.spf) { const rs = get(h, 'received-spf')[0]; if (rs) r.spf = rs.split(/\s/)[0].toLowerCase(); }
    if (!r.dkimD) { const ds = get(h, 'dkim-signature')[0]; if (ds) { const m = /\bd=([^;\s]+)/i.exec(ds); if (m) r.dkimD = m[1].toLowerCase(); } }
    return r;
  }

  function analyse(text) {
    const h = parse(text), F = [];
    const add = (sev, t, d) => F.push({ sev, t, d });
    if (!h.length) return null;
    const from = addr(get(h, 'from')[0]), rp = addr(get(h, 'return-path')[0]), rt = addr(get(h, 'reply-to')[0]);
    const subject = get(h, 'subject')[0] || '', mid = (get(h, 'message-id')[0] || '').replace(/[<>]/g, ''), date = parseDate(get(h, 'date')[0]);
    const hp = hops(h), au = authResults(h);

    if (!from) add('med', 'No From header found', 'Paste the full original headers, starting from the top.');
    if (!hp.length) add('info', 'No Received headers', 'The route the message took is missing. Use "Show original" (Gmail) or "View message details" (Outlook) to copy everything.');

    // Authentication
    const dm = au.dmarc, sp = au.spf, dk = au.dkim;
    if (dm === 'pass') add('pass', 'DMARC passed', 'The From domain (' + (au.headerFrom || (from && from.domain)) + ') authorised this message through aligned SPF or DKIM.');
    else if (dm === 'fail') add('high', 'DMARC failed', 'The message failed the From domain\'s own authentication policy. This is the strongest sign of spoofing.');
    else if (dm) add('med', 'DMARC result: ' + dm, 'The receiving server could not confirm the From domain.');
    else add('med', 'No DMARC result in the headers', 'Either the receiver did not check it or the headers are incomplete.');
    if (sp === 'pass') add('pass', 'SPF passed', 'Sent from a server listed by ' + (au.mailFrom ? au.mailFrom.split('@').pop() : 'the envelope sender domain') + '.');
    else if (sp === 'fail') add('high', 'SPF failed', 'The sending server is not allowed to send for the envelope domain.');
    else if (sp === 'softfail') add('med', 'SPF soft fail', 'The sending server is not listed by the envelope domain.');
    else if (sp) add('low', 'SPF result: ' + sp, 'No clear authorisation for the sending server.');
    if (dk === 'pass') add('pass', 'DKIM signature valid' + (au.dkimD ? ' (d=' + au.dkimD + ')' : ''), 'The signed parts were not changed after sending.');
    else if (dk === 'fail') add('high', 'DKIM signature failed', 'The signature does not match. The message may have been altered or forged.');
    else if (dk) add('med', 'DKIM: ' + dk, 'The message was not signed, so its origin cannot be proven cryptographically.');
    if (dk === 'pass' && au.dkimD && from && L.registrable(au.dkimD) !== from.reg) add('low', 'DKIM signed by a different domain', 'Signed by ' + au.dkimD + ' but From is ' + from.domain + '. Common with mailing services, but it does not prove the From address.');

    if (from) {
      // Brand claims
      const claimed = L.brandsIn(from.name + ' ' + from.addr.split('@')[0]);
      const own = L.officialBrand(from.domain);
      const fake = claimed.filter(b => !b.domains.some(d => from.domain === d || from.domain.endsWith('.' + d)));
      const bankIn = /\.bank\.in$/.test(from.domain);
      if (fake.length && !bankIn) add('high', 'Name says ' + fake[0].name + ', but the address is not on their official domains', '"' + (from.name || from.addr) + '" is sent from ' + from.domain + '. Official domains we know: ' + fake[0].domains.join(', ') + '.');
      const like = L.lookalike(from.reg);
      if (like) add('high', 'Lookalike of an official domain', from.reg + ' looks like ' + like.domain + ' (' + like.brand.name + ') by ' + like.how + '.');
      else if (!own && L.brandsIn(from.domain).length && !bankIn) add('high', 'Brand name inside an unofficial domain', from.domain + ' contains "' + L.brandsIn(from.domain)[0].kw.find(k => from.domain.includes(k)) + '" but is not on our list of official domains of ' + L.brandsIn(from.domain)[0].name + '.');
      if (L.FREEMAIL.includes(from.domain) && (claimed.some(b => b.bank || b.gov) || /\b(bank|govt|government|police|court|income tax|customs|officer|ministry|university|college)\b/i.test(from.name)))
        add('high', 'Official-sounding sender on a free email service', 'Banks, government offices and colleges do not send official notices from ' + from.domain + '.');
      const nameMail = /[^\s<>"@]+@[^\s<>"]+\.[a-z]{2,}/i.exec(from.name);
      if (nameMail && nameMail[0].toLowerCase() !== from.addr) add('high', 'Display name shows a different email address', 'The name says ' + nameMail[0] + ' but the real sender is ' + from.addr + '.');
      if (own && dm === 'pass') add('pass', 'Sender domain belongs to ' + own.name, from.domain + ' is an official domain and DMARC passed.');
      if (bankIn && dm === 'pass') add('pass', 'Sender uses a .bank.in domain', 'Only RBI-regulated banks can register .bank.in (through IDRBT). DMARC passed.');
      // Reply-To and Return-Path
      if (rt && rt.reg && rt.reg !== from.reg) add(L.FREEMAIL.includes(rt.domain) && !L.FREEMAIL.includes(from.domain) ? 'high' : 'med', 'Replies go to a different domain',
        'Reply-To is ' + rt.addr + ' while From is ' + from.addr + '. Replies would reach someone else. Classic in invoice and job scams.');
      if (rp && rp.reg && rp.reg !== from.reg) add('low', 'Envelope sender (Return-Path) differs from From', rp.addr + ' vs ' + from.addr + '. Normal for newsletters and mailing services, suspicious when DMARC fails.');
      if (mid && mid.includes('@')) { const md = L.registrable(mid.split('@').pop()); if (md && md !== from.reg && (!rp || md !== rp.reg) && !/google\.com|outlook\.com|prod\.outlook\.com|amazonses\.com|mail\.gmail\.com/.test(mid)) add('low', 'Message-ID domain does not match the sender', mid.split('@').pop() + ' created the message ID, not ' + from.domain + '.'); }
    }
    // Subject
    const words = PRESSURE.filter(w => new RegExp('\\b' + w + '\\b', 'i').test(subject));
    if (words.length >= 2) add('med', 'Pressure words in the subject', '"' + subject + '" uses: ' + words.join(', ') + '. Urgency is the most common phishing lever.');
    else if (words.length === 1) add('low', 'Subject uses a pressure word', '"' + words[0] + '" in "' + subject + '".');
    // Route
    const origin = hp.find(x => x.ip && !isPrivate(x.ip));
    const xoip = (get(h, 'x-originating-ip')[0] || '').replace(/[\[\]]/g, '');
    if (origin) add('info', 'First public IP in the route: ' + origin.ip, 'Seen at the hop from ' + (origin.from || 'unknown') + '. Hops recorded before this one were written on the sender\'s side and can be forged.');
    if (xoip) add('info', 'X-Originating-IP: ' + xoip, 'Some webmail services record the sender\'s IP here.');
    for (let i = 1; i < hp.length; i++) if (hp[i].date && hp[i - 1].date && hp[i].date - hp[i - 1].date < -120000) { add('low', 'Hop timestamps go backwards', 'A server clock is wrong or a Received line was forged (hop ' + i + ' to ' + (i + 1) + ').'); break; }
    const firstT = hp.find(x => x.date), lastT = hp.slice().reverse().find(x => x.date);
    if (firstT && lastT && lastT.date - firstT.date > 3600000) add('low', 'Slow delivery: ' + Math.round((lastT.date - firstT.date) / 60000) + ' minutes in transit', 'Long delays can mean queueing at a bulk or compromised sender.');
    if (date && firstT && Math.abs(firstT.date - date) > 86400000) add('low', 'Date header far from the first Received time', 'The Date line may have been set by hand.');

    const level = F.some(f => f.sev === 'high') ? 'high' : F.some(f => f.sev === 'med') ? 'med' : 'low';
    return { h, from, rp, rt, subject, au, hp, F, level };
  }

  let last = null;
  function render(r) {
    const box = $('#hf-result'); box.replaceChildren(); box.hidden = false;
    if (!r) { box.append(el('p', { class: 'lab-empty', text: 'No headers found. Paste the full original headers (they start with lines like "Received:" or "Delivered-To:").' })); return; }
    const verdict = { high: ['Likely spoofed or phishing', 'v-high'], med: ['Suspicious: verify before acting', 'v-med'], low: ['No strong red flags in the headers', 'v-low'] }[r.level];
    const order = { high: 0, med: 1, low: 2, info: 3, pass: 4 };
    const fmt = d => d ? d.toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'medium' }) : '';
    const rows = r.hp.map((x, i) => {
      const prev = i ? r.hp[i - 1].date : null, delay = prev && x.date ? Math.round((x.date - prev) / 1000) : null;
      return el('tr', {}, [el('td', { text: String(i + 1) }), el('td', {}, [el('code', { text: x.from || '(none)' })]), el('td', {}, [el('code', { text: x.by || '' })]),
        el('td', {}, [el('code', { text: x.ip || '' })]), el('td', { text: x.with }), el('td', { text: fmt(x.date) }), el('td', { text: delay == null ? '' : delay + ' s' })]);
    });
    const kv = (k, v) => [el('dt', { text: k }), el('dd', {}, [el('code', { text: v || '(not present)' })])];
    box.append(
      el('div', { class: 'lab-verdict ' + verdict[1], role: 'status' }, [el('strong', { text: verdict[0] }),
        el('span', { text: ' ' + r.F.filter(f => f.sev === 'high').length + ' high, ' + r.F.filter(f => f.sev === 'med').length + ' medium, ' + r.F.filter(f => f.sev === 'pass').length + ' passed checks.' })]),
      el('div', { class: 'lab-auth' }, ['spf', 'dkim', 'dmarc'].map(k => el('span', { class: 'lab-pill p-' + (r.au[k] === 'pass' ? 'ok' : r.au[k] ? 'bad' : 'na') }, [k.toUpperCase() + ': ', el('b', { text: r.au[k] || 'not found' })]))),
      el('h3', { class: 'lab-sub', text: 'Findings' }),
      el('ul', { class: 'lab-findings' }, r.F.slice().sort((a, b) => order[a.sev] - order[b.sev]).map(f => finding(f.sev, f.t, f.d))),
      el('h3', { class: 'lab-sub', text: 'Key headers' }),
      el('dl', { class: 'lab-kv' }, [].concat(kv('From', r.from && (r.from.name ? '"' + r.from.name + '" ' : '') + (r.from ? r.from.addr : '')), kv('Return-Path', r.rp && r.rp.addr),
        kv('Reply-To', r.rt && r.rt.addr), kv('Subject', r.subject), kv('Authentication-Results', r.au.src))),
      el('h3', { class: 'lab-sub', text: 'Delivery route (oldest hop first)' }),
      r.hp.length ? el('div', { class: 'lab-table-wrap', tabindex: '0', role: 'region', 'aria-label': 'Delivery route table' }, [el('table', { class: 'lab-table' }, [
        el('thead', {}, [el('tr', {}, ['#', 'From', 'By', 'IP', 'With', 'Time (your zone)', 'Delay'].map(t => el('th', { scope: 'col', text: t })))]), el('tbody', {}, rows)])]) : el('p', { class: 'muted', text: 'No Received headers.' })
    );
    const dom = r.from && r.from.domain;
    $('#hf-dns').hidden = !dom; $('#hf-dns-dom').textContent = dom || '';
    $('#hf-dns-out').replaceChildren();
    last = r;
  }
  async function lookup() {
    if (!last || !last.from) return;
    const d = last.from.domain, out = $('#hf-dns-out');
    out.replaceChildren(el('p', { class: 'muted', text: 'Looking up ' + d + '...' }));
    try {
      const [s, m] = await Promise.all([L.spf(d), L.dmarc(d)]);
      const list = [];
      if (s.record) list.push(finding('info', 'SPF for ' + d, s.record + ' (' + s.lookups + ' DNS lookups)'));
      else list.push(finding('warn', 'No SPF record for ' + d, 'This domain does not say which servers may send for it.'));
      if (m.record) list.push(finding((m.tags.p || '') === 'none' ? 'warn' : 'pass', 'DMARC for ' + m.from + ': p=' + (m.tags.p || '?'), m.record));
      else list.push(finding('warn', 'No DMARC record for ' + d, 'Anyone can spoof this domain without receivers being told to reject it.'));
      out.replaceChildren(el('ul', { class: 'lab-findings' }, list), el('p', { class: 'small' }, [el('a', { href: 'dns-security-checker.html?d=' + encodeURIComponent(d), text: 'Run the full DNS security check for ' + d })]));
    } catch (e) { out.replaceChildren(el('p', { class: 'lab-empty', text: 'Could not reach the DNS service.' })); }
  }

  function init() {
    $('#hf-form').addEventListener('submit', e => { e.preventDefault(); render(analyse($('#hf-input').value)); $('#hf-result').scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    document.querySelectorAll('[data-hf-sample]').forEach(b => b.addEventListener('click', () => { $('#hf-input').value = SAMPLES[b.dataset.hfSample]; render(analyse($('#hf-input').value)); }));
    $('#hf-clear').addEventListener('click', () => { $('#hf-input').value = ''; $('#hf-result').hidden = true; $('#hf-dns').hidden = true; last = null; });
    $('#hf-dns-go').addEventListener('click', lookup);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  window.CWMHeaders = { analyse, parse };
})();
