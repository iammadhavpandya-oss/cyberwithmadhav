/* CyberWithMadhav Email and Link Security Lab: shared helpers.
   Pure functions run offline in this browser. Only dns() makes a network call, to Cloudflare DNS over HTTPS,
   and only when a tool page asks for it (the DNS checker, or the opt-in lookup in the header analyser). */
(function () {
  'use strict';

  /* Official domains of brands often impersonated in India. Every entry is the brand's own public domain.
     Banks also moved to the restricted .bank.in zone (RBI circular of 22 April 2025), handled by a rule below. */
  const BRANDS = [
    { name: 'State Bank of India (SBI)', kw: ['sbi', 'onlinesbi', 'yonosbi', 'statebank'], domains: ['sbi.co.in', 'onlinesbi.sbi', 'sbi.bank.in', 'sbicard.com'], bank: true },
    { name: 'HDFC Bank', kw: ['hdfc', 'hdfcbank'], domains: ['hdfcbank.com', 'hdfc.bank.in'], bank: true },
    { name: 'ICICI Bank', kw: ['icici', 'icicibank'], domains: ['icicibank.com', 'icici.bank.in'], bank: true },
    { name: 'Axis Bank', kw: ['axisbank'], domains: ['axisbank.com', 'axis.bank.in'], bank: true },
    { name: 'Kotak Mahindra Bank', kw: ['kotak'], domains: ['kotak.com', 'kotak.bank.in'], bank: true },
    { name: 'Punjab National Bank', kw: ['pnb', 'pnbindia'], domains: ['pnbindia.in', 'pnb.bank.in'], bank: true },
    { name: 'Bank of Baroda', kw: ['bankofbaroda'], domains: ['bankofbaroda.in', 'bankofbaroda.bank.in'], bank: true },
    { name: 'Canara Bank', kw: ['canarabank', 'canara'], domains: ['canarabank.com', 'canarabank.bank.in'], bank: true },
    { name: 'Union Bank of India', kw: ['unionbank', 'unionbankofindia'], domains: ['unionbankofindia.co.in', 'unionbankofindia.bank.in'], bank: true },
    { name: 'NPCI and UPI', kw: ['npci', 'upi', 'bhim', 'bhimupi'], domains: ['npci.org.in', 'bhimupi.org.in'] },
    { name: 'Reserve Bank of India', kw: ['rbi', 'reservebank'], domains: ['rbi.org.in'] },
    { name: 'Paytm', kw: ['paytm'], domains: ['paytm.com'] },
    { name: 'PhonePe', kw: ['phonepe'], domains: ['phonepe.com'] },
    { name: 'Google Pay', kw: ['googlepay', 'gpay'], domains: ['pay.google.com'] },
    { name: 'Income Tax Department', kw: ['incometax', 'incometaxindia'], domains: ['incometax.gov.in', 'incometaxindia.gov.in'], gov: true },
    { name: 'UIDAI (Aadhaar)', kw: ['uidai', 'aadhaar', 'aadhar'], domains: ['uidai.gov.in', 'myaadhaar.uidai.gov.in'], gov: true },
    { name: 'EPFO', kw: ['epfo', 'epfindia'], domains: ['epfindia.gov.in'], gov: true },
    { name: 'India Post', kw: ['indiapost', 'indiaposts'], domains: ['indiapost.gov.in'], gov: true },
    { name: 'Parivahan and e-Challan', kw: ['parivahan', 'echallan', 'challan', 'mparivahan'], domains: ['parivahan.gov.in'], gov: true },
    { name: 'National Cyber Crime Reporting Portal', kw: ['cybercrime'], domains: ['cybercrime.gov.in'], gov: true },
    { name: 'Sanchar Saathi', kw: ['sancharsaathi'], domains: ['sancharsaathi.gov.in'], gov: true },
    { name: 'DigiLocker', kw: ['digilocker'], domains: ['digilocker.gov.in'], gov: true },
    { name: 'IRCTC', kw: ['irctc'], domains: ['irctc.co.in'] },
    { name: 'LIC of India', kw: ['licindia'], domains: ['licindia.in'] },
    { name: 'MSEDCL (Mahavitaran)', kw: ['mahadiscom', 'mahavitaran', 'msedcl'], domains: ['mahadiscom.in'] },
    { name: 'Adani Electricity Mumbai', kw: ['adanielectricity'], domains: ['adanielectricity.com'] },
    { name: 'Airtel', kw: ['airtel'], domains: ['airtel.in'] },
    { name: 'Jio', kw: ['jio', 'reliancejio'], domains: ['jio.com'] },
    { name: 'Amazon India', kw: ['amazon'], domains: ['amazon.in', 'amazon.com'] },
    { name: 'Flipkart', kw: ['flipkart'], domains: ['flipkart.com'] },
    { name: 'Blue Dart', kw: ['bluedart'], domains: ['bluedart.com'] },
    { name: 'Delhivery', kw: ['delhivery'], domains: ['delhivery.com'] },
    { name: 'WhatsApp', kw: ['whatsapp'], domains: ['whatsapp.com', 'wa.me'] },
    { name: 'Microsoft', kw: ['microsoft', 'office365', 'outlook', 'microsoftonline'], domains: ['microsoft.com', 'office.com', 'outlook.com', 'live.com', 'microsoftonline.com'] },
    { name: 'Google', kw: ['google', 'gmail'], domains: ['google.com', 'gmail.com', 'google.co.in'] },
    { name: 'Apple', kw: ['apple', 'icloud'], domains: ['apple.com', 'icloud.com'] }
  ];
  const FREEMAIL = ['gmail.com', 'googlemail.com', 'yahoo.com', 'yahoo.co.in', 'outlook.com', 'hotmail.com', 'live.com', 'rediffmail.com',
    'zohomail.in', 'zohomail.com', 'proton.me', 'protonmail.com', 'icloud.com', 'aol.com', 'yandex.com', 'mail.com', 'gmx.com'];
  /* Multi-label public suffixes we care about. Not the full Public Suffix List, so registrable domains are a close approximation. */
  const SUFFIX2 = ['co.in', 'net.in', 'org.in', 'gov.in', 'nic.in', 'ac.in', 'edu.in', 'res.in', 'firm.in', 'gen.in', 'ind.in', 'bank.in', 'fin.in',
    'co.uk', 'org.uk', 'ac.uk', 'gov.uk', 'com.au', 'net.au', 'org.au', 'co.jp', 'com.br', 'co.za', 'com.sg', 'com.cn', 'com.pk', 'com.bd', 'co.nz'];

  function registrable(host) {
    host = String(host || '').toLowerCase().replace(/\.$/, '');
    const p = host.split('.');
    if (p.length <= 2) return host;
    const last2 = p.slice(-2).join('.');
    return SUFFIX2.includes(last2) ? p.slice(-3).join('.') : last2;
  }
  function suffixOf(host) { const r = registrable(host); return r.split('.').slice(1).join('.'); }
  function officialBrand(host) {
    host = String(host || '').toLowerCase();
    let best = null, len = 0;
    for (const b of BRANDS) for (const d of b.domains) if ((host === d || host.endsWith('.' + d)) && d.length > len) { best = b; len = d.length; }
    return best;
  }
  function tokens(s) { return String(s || '').toLowerCase().split(/[^a-z0-9]+|(?<=[a-z])(?=[0-9])|(?<=[0-9])(?=[a-z])/).filter(Boolean); }
  /* Brand named in free text, such as a display name or a hostname. Short keywords must be a whole token. */
  function brandsIn(text) {
    const t = String(text || '').toLowerCase(), tk = tokens(t), joined = tk.join('');
    const out = [];
    BRANDS.forEach(b => {
      const hit = b.kw.some(k => k.length <= 4 ? tk.includes(k) : (tk.includes(k) || joined.includes(k)));
      if (hit) out.push(b);
    });
    return out;
  }
  function dl(a, b) { /* Damerau-Levenshtein (optimal string alignment) */
    const m = a.length, n = b.length, d = [];
    for (let i = 0; i <= m; i++) { d[i] = [i]; }
    for (let j = 0; j <= n; j++) d[0][j] = j;
    for (let i = 1; i <= m; i++) for (let j = 1; j <= n; j++) {
      const c = a[i - 1] === b[j - 1] ? 0 : 1;
      d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + c);
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
    }
    return d[m][n];
  }
  const HOMO = { '\u0430': 'a', '\u0435': 'e', '\u043e': 'o', '\u0440': 'p', '\u0441': 'c', '\u0443': 'y', '\u0445': 'x', '\u0456': 'i', '\u0458': 'j', '\u0455': 's',
    '\u0501': 'd', '\u04bb': 'h', '\u04cf': 'l', '\u051b': 'q', '\u051d': 'w', '\u03b1': 'a', '\u03bf': 'o', '\u03c1': 'p', '\u03bd': 'v', '\u03c4': 't', '\u03b9': 'i',
    '\u03ba': 'k', '\u0131': 'i', '\u0142': 'l', '\u00e0': 'a', '\u00e1': 'a', '\u00e9': 'e', '\u00ed': 'i', '\u00f3': 'o', '\u00fa': 'u', '\u00f6': 'o', '\u00fc': 'u' };
  function skeleton(s) {
    let t = Array.from(String(s || '').toLowerCase()).map(c => HOMO[c] || c).join('');
    return t.replace(/0/g, 'o').replace(/1/g, 'l').replace(/rn/g, 'm').replace(/vv/g, 'w');
  }
  const L2 = d => d.split('.').slice(1).join('.');
  /* Closest official domain to a registrable domain that is not itself official. */
  function lookalike(reg) {
    reg = String(reg || '').toLowerCase();
    if (!reg || officialBrand(reg)) return null;
    const label = reg.split('.')[0], sk = skeleton(label);
    let best = null;
    BRANDS.forEach(b => b.domains.forEach(d => {
      if (d.split('.').length > 2 && !d.endsWith('.bank.in') && !d.endsWith('.co.in') && !d.endsWith('.gov.in') && !d.endsWith('.org.in')) return;
      const ol = d.split('.')[0];
      if (ol.length < 4) { if (sk === ol && label !== ol && (!best || L2(d) === L2(reg))) best = { brand: b, domain: d, dist: 0, how: 'lookalike characters' }; return; }
      const dist = Math.min(dl(label, ol), dl(sk, ol));
      const lim = ol.length >= 8 ? 2 : 1;
      if (dist > 0 && dist <= lim && (!best || dist < best.dist || (dist === best.dist && L2(d) === L2(reg)))) best = { brand: b, domain: d, dist, how: sk === ol ? 'lookalike characters' : 'spelling' };
      if (dist === 0 && label !== ol && (!best || best.dist > 0)) best = { brand: b, domain: d, dist: 0, how: 'lookalike characters' };
      if (dist === 0 && label === ol && reg !== d && !(best && best.dist === 0)) best = { brand: b, domain: d, dist: 0, how: 'same name, different ending' };
    }));
    return best;
  }

  /* Punycode (RFC 3492) decoder, so xn-- labels can be shown as the characters a victim would see. */
  function punyDecode(input) {
    const base = 36, tMin = 1, tMax = 26, skew = 38, damp = 700, initialBias = 72, initialN = 128;
    let output = [], i = 0, n = initialN, bias = initialBias;
    let b = input.lastIndexOf('-'); if (b < 0) b = 0;
    for (let j = 0; j < b; j++) output.push(input.charCodeAt(j));
    const adapt = (delta, numPoints, first) => { let k = 0; delta = first ? Math.floor(delta / damp) : delta >> 1; delta += Math.floor(delta / numPoints);
      for (; delta > ((base - tMin) * tMax) >> 1; k += base) delta = Math.floor(delta / (base - tMin)); return Math.floor(k + (base - tMin + 1) * delta / (delta + skew)); };
    for (let idx = b > 0 ? b + 1 : 0; idx < input.length;) {
      const oldi = i;
      for (let w = 1, k = base; ; k += base) {
        if (idx >= input.length) throw new Error('bad punycode');
        const c = input.charCodeAt(idx++);
        const digit = c - 48 < 10 ? c - 22 : c - 65 < 26 ? c - 65 : c - 97 < 26 ? c - 97 : base;
        if (digit >= base) throw new Error('bad punycode');
        i += digit * w;
        const t = k <= bias ? tMin : k >= bias + tMax ? tMax : k - bias;
        if (digit < t) break;
        w *= base - t;
      }
      bias = adapt(i - oldi, output.length + 1, oldi === 0);
      n += Math.floor(i / (output.length + 1)); i %= output.length + 1;
      output.splice(i++, 0, n);
    }
    return String.fromCodePoint(...output);
  }
  function toUnicode(host) { return String(host || '').split('.').map(l => { if (!/^xn--/i.test(l)) return l; try { return punyDecode(l.slice(4)); } catch (e) { return l; } }).join('.'); }

  /* Cloudflare DNS over HTTPS (JSON). Only the name and record type leave the browser. */
  const cache = new Map();
  async function dns(name, type) {
    const key = type + ' ' + name;
    if (cache.has(key)) return cache.get(key);
    const p = (async () => {
      const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 8000);
      try {
        const r = await fetch('https://cloudflare-dns.com/dns-query?name=' + encodeURIComponent(name) + '&type=' + encodeURIComponent(type),
          { headers: { accept: 'application/dns-json' }, signal: ctl.signal, credentials: 'omit', referrerPolicy: 'no-referrer' });
        if (!r.ok) throw new Error('DNS service answered ' + r.status);
        const j = await r.json();
        const typeNum = { A: 1, NS: 2, CNAME: 5, MX: 15, TXT: 16, AAAA: 28, DS: 43, DNSKEY: 48, CAA: 257 }[type];
        const ans = (j.Answer || []).filter(a => !typeNum || a.type === typeNum).map(a => a.data);
        return { ok: true, status: j.Status, ad: !!j.AD, answers: ans, nx: j.Status === 3 };
      } finally { clearTimeout(t); }
    })();
    cache.set(key, p);
    p.catch(() => cache.delete(key));
    return p;
  }
  function txtJoin(data) { /* "part one" "part two" -> part onepart two */
    const parts = String(data).match(/"((?:[^"\\]|\\.)*)"/g);
    return parts ? parts.map(s => s.slice(1, -1).replace(/\\(.)/g, '$1')).join('') : String(data);
  }
  async function txt(name) { const r = await dns(name, 'TXT'); return Object.assign({}, r, { answers: r.answers.map(txtJoin) }); }

  /* SPF: find records, walk includes and redirects, count DNS lookups (RFC 7208 limit is 10). */
  async function spf(domain) {
    const res = { records: [], record: null, lookups: 0, all: null, includes: [], errors: [], warnings: [], ptr: false, tree: [] };
    const top = await txt(domain);
    res.records = top.answers.filter(t => /^v=spf1(\s|$)/i.test(t));
    if (!res.records.length) return res;
    res.record = res.records[0];
    const seen = new Set();
    async function walk(rec, dom, depth) {
      if (depth > 10) { res.errors.push('Includes nest too deep at ' + dom); return; }
      const terms = rec.split(/\s+/).slice(1);
      for (const raw of terms) {
        const term = raw.replace(/^[+\-~?]/, ''), q = raw[0].match(/[+\-~?]/) ? raw[0] : '+';
        const mech = term.split(/[:=/]/)[0].toLowerCase();
        if (['include', 'a', 'mx', 'ptr', 'exists', 'redirect'].includes(mech)) res.lookups++;
        if (mech === 'ptr') res.ptr = true;
        if (mech === 'all' && depth === 0) res.all = q;
        if ((mech === 'include' || mech === 'redirect') && term.includes(mech === 'include' ? ':' : '=')) {
          const target = term.slice(term.indexOf(mech === 'include' ? ':' : '=') + 1);
          if (depth === 0) res.includes.push(target);
          if (target.includes('%{')) { res.warnings.push('Macro in ' + target + ' was not expanded'); continue; }
          if (seen.has(target)) continue; seen.add(target);
          try {
            const r = await txt(target);
            const s = r.answers.filter(t => /^v=spf1(\s|$)/i.test(t));
            if (!s.length) res.errors.push(mech + ' target ' + target + ' has no SPF record');
            else { res.tree.push({ depth: depth + 1, name: target, record: s[0] }); await walk(s[0], target, depth + 1); }
          } catch (e) { res.errors.push('Could not look up ' + target); }
        }
      }
    }
    await walk(res.record, domain, 0);
    if (!res.all) { const red = /\bredirect=/i.test(res.record); if (!red) res.all = 'none'; else res.all = 'redirect'; }
    return res;
  }
  function parseTags(rec) { const o = {}; String(rec).split(';').forEach(p => { const i = p.indexOf('='); if (i > 0) o[p.slice(0, i).trim().toLowerCase()] = p.slice(i + 1).trim(); }); return o; }
  async function dmarc(domain) {
    let r = await txt('_dmarc.' + domain);
    let recs = r.answers.filter(t => /^v=DMARC1/i.test(t)), from = domain;
    const org = registrable(domain);
    if (!recs.length && org !== domain) { r = await txt('_dmarc.' + org); recs = r.answers.filter(t => /^v=DMARC1/i.test(t)); from = org; }
    return { records: recs, record: recs[0] || null, tags: recs[0] ? parseTags(recs[0]) : {}, from };
  }

  function normDomain(input) {
    let s = String(input || '').trim().toLowerCase();
    if (!s) return '';
    if (s.includes('@') && !s.includes('/')) s = s.split('@').pop();
    try { s = new URL(/^[a-z][a-z0-9+.-]*:\/\//.test(s) ? s : 'http://' + s).hostname; } catch (e) { return ''; }
    s = s.replace(/^www\./, '').replace(/\.$/, '');
    return /^(?=.{1,253}$)([a-z0-9_](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{2,63}$/.test(s) ? s : '';
  }
  function esc(s) { return String(s == null ? '' : s); }
  function el(tag, attrs, kids) {
    const n = document.createElement(tag);
    if (attrs) for (const k in attrs) { const v = attrs[k]; if (v == null || v === false) continue;
      if (k === 'class') n.className = v; else if (k === 'text') n.textContent = v; else n.setAttribute(k, v === true ? '' : v); }
    (kids || []).forEach(c => { if (c != null && c !== false) n.append(c.nodeType ? c : document.createTextNode(esc(c))); });
    return n;
  }
  function toast(msg) {
    const t = document.getElementById('toast'); if (!t) return; t.textContent = msg; t.hidden = false;
    requestAnimationFrame(() => t.classList.add('show'));
    clearTimeout(toast.t); toast.t = setTimeout(() => { t.classList.remove('show'); setTimeout(() => { t.hidden = true; }, 300); }, 2200);
  }
  async function copy(text) {
    try { await navigator.clipboard.writeText(text); toast('Copied to clipboard'); }
    catch (e) { toast('Copy failed. Select the text and copy it.'); }
  }
  /* Severity badge + finding row used by all three tools */
  function finding(sev, title, detail, fix) {
    const label = { high: 'High', med: 'Medium', low: 'Low', info: 'Info', pass: 'Pass', fail: 'Fail', warn: 'Warn' }[sev] || sev;
    return el('li', { class: 'lab-f lab-' + sev }, [
      el('span', { class: 'lab-badge', text: label }),
      el('div', { class: 'lab-f-body' }, [el('p', { class: 'lab-f-t', text: title }), detail ? el('p', { class: 'lab-f-d', text: detail }) : null,
        fix ? el('p', { class: 'lab-f-fix' }, [el('b', { text: 'Fix: ' }), el('code', { text: fix })]) : null])
    ]);
  }

  window.CWMLab = { BRANDS, FREEMAIL, registrable, suffixOf, officialBrand, brandsIn, lookalike, skeleton, toUnicode, dl,
    dns, txt, spf, dmarc, parseTags, normDomain, el, toast, copy, finding };
})();
