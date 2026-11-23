/* Phishing URL Forensics. Pure text analysis in this browser. The link is never opened, fetched, previewed or expanded. */
(function () {
  'use strict';
  const L = window.CWMLab, { el, finding } = L, $ = s => document.querySelector(s);
  const SHORTENERS = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'is.gd', 'cutt.ly', 'rb.gy', 'shorturl.at', 'ow.ly', 'buff.ly', 'rebrand.ly', 'tiny.cc',
    's.id', 't.ly', 'v.gd', 'bitly.com', 'shorte.st', 'adf.ly', 'qrco.de', 'amzn.to', 'lnkd.in', 'surl.li', 'tinu.be'];
  /* TLDs that show up often in phishing and abuse reports. Not proof of anything on their own. */
  const RISKY_TLD = ['top', 'xyz', 'icu', 'cyou', 'buzz', 'sbs', 'click', 'rest', 'cfd', 'monster', 'tk', 'ml', 'ga', 'cf', 'gq', 'zip', 'mov', 'lol', 'quest', 'bond', 'live', 'shop', 'online', 'site', 'support', 'help'];
  const RISKY_EXT = { apk: 'high', exe: 'high', scr: 'high', msi: 'high', bat: 'high', cmd: 'high', js: 'med', vbs: 'high', jar: 'high', zip: 'med', rar: 'med', '7z': 'med', iso: 'med', html: 'low', htm: 'low', svg: 'low' };
  const BAIT = ['login', 'signin', 'verify', 'verification', 'kyc', 'update', 'secure', 'account', 'otp', 'refund', 'reward', 'prize', 'lottery', 'unlock', 'suspend',
    'blocked', 'pan', 'aadhaar', 'challan', 'electricity', 'bill', 'claim', 'gift', 'bonus', 'wallet', 'password', 'netbanking', 'yono', 'apk', 'download'];
  /* Known redirect wrappers and the query parameter that holds the real destination. */
  const REDIRECTORS = [
    { host: /(^|\.)google\.[a-z.]+$/, path: /^\/url$/, param: ['q', 'url'], name: 'Google redirect' },
    { host: /(^|\.)safelinks\.protection\.outlook\.com$/, param: ['url'], name: 'Microsoft Safe Links' },
    { host: /^l\.facebook\.com$|^lm\.facebook\.com$/, param: ['u'], name: 'Facebook link shim' },
    { host: /^l\.instagram\.com$/, param: ['u'], name: 'Instagram link shim' },
    { host: /(^|\.)youtube\.com$/, path: /^\/redirect$/, param: ['q'], name: 'YouTube redirect' },
    { host: /(^|\.)linkedin\.com$/, path: /^\/redir/, param: ['url'], name: 'LinkedIn redirect' },
    { host: /.*/, param: ['url', 'redirect', 'redirect_uri', 'redirect_url', 'next', 'target', 'dest', 'destination', 'continue', 'return', 'returnurl', 'goto', 'u', 'r', 'link'], name: 'Open redirect parameter', generic: true }
  ];

  function extract(text) {
    const t = String(text || '').trim();
    const m = /\b((?:https?|hxxps?|ftp|data|javascript):[^\s<>"']+|(?:www\.)[^\s<>"']+|[a-z0-9.-]+\.[a-z]{2,}(?:\/[^\s<>"']*)?)/i.exec(t.replace(/\[\.\]|\(\.\)|\{\.\}/g, '.'));
    if (!m) return '';
    return m[1].replace(/^hxxp/i, 'http').replace(/[).,;!?]+$/, '');
  }
  function pctDecode(s) { let cur = s, n = 0; for (; n < 5; n++) { let nx; try { nx = decodeURIComponent(cur); } catch (e) { break; } if (nx === cur) break; cur = nx; } return { text: cur, layers: n }; }
  function b64(s) {
    if (!/^[A-Za-z0-9+/_-]{16,}={0,2}$/.test(s)) return null;
    try { const t = atob(s.replace(/-/g, '+').replace(/_/g, '/')); return /^[\x20-\x7e]+$/.test(t) && /https?:\/\/|www\.|@|\.[a-z]{2,}\//i.test(t) ? t : null; } catch (e) { return null; }
  }
  function ipForm(rawHost) {
    if (/^\d+$/.test(rawHost)) return 'decimal number';
    if (/^0x[0-9a-f]+$/i.test(rawHost) || /(^|\.)0x[0-9a-f]+/i.test(rawHost)) return 'hexadecimal';
    if (/^(0\d+\.)|\.0\d+/.test(rawHost) && /^[\d.]+$/.test(rawHost)) return 'octal';
    if (/^(\d{1,3}\.){3}\d{1,3}$/.test(rawHost)) return 'dotted IPv4';
    if (/^\[[0-9a-f:]+\]$/i.test(rawHost)) return 'IPv6';
    return null;
  }

  function analyse(input, depth) {
    depth = depth || 0;
    const F = [], add = (sev, t, d) => F.push({ sev, t, d });
    let raw = String(input || '').trim();
    if (!raw) return null;
    const scheme = (/^([a-z][a-z0-9+.-]*):/i.exec(raw) || [])[1];
    if (scheme && /^(javascript|data|vbscript)$/i.test(scheme)) {
      add('high', scheme + ': link', 'This is not a web address. It runs code or embeds content directly. Do not open it.');
      return { raw, F, level: 'high', parts: null, chain: [] };
    }
    const withScheme = scheme && /^[a-z]+:\/\//i.test(raw) ? raw : 'http://' + raw.replace(/^\/\//, '');
    const rawAuth = (/^[a-z][a-z0-9+.-]*:\/\/([^/?#]*)/i.exec(withScheme) || [])[1] || '';
    const rawHost = rawAuth.replace(/^.*@/, '').replace(/:\d+$/, '');
    let u; try { u = new URL(withScheme); } catch (e) { add('high', 'Malformed address', 'The link could not be parsed as a URL. Malformed links are sometimes used to confuse filters.'); return { raw, F, level: 'high', parts: null, chain: [] }; }
    const host = u.hostname.toLowerCase(), uni = L.toUnicode(host), reg = L.registrable(host), tld = host.split('.').pop();
    const parts = { scheme: u.protocol.replace(':', ''), user: u.username ? decodeURIComponent(u.username) + (u.password ? ':***' : '') : '', host, uni, reg, port: u.port, path: u.pathname, query: [...u.searchParams.entries()], hash: u.hash };

    if (!scheme) add('info', 'No scheme given', 'Analysed as http://. Real links in messages usually start with https://.');
    else if (u.protocol === 'http:') add('med', 'Not encrypted (http)', 'Anything typed on this page travels without encryption. Banks and government portals use https.');
    if (u.username || u.password) add('high', 'Text before @ in the address', 'Browsers ignore "' + parts.user + '@" and go to ' + host + '. Attackers put a trusted name before the @ to fool readers.');
    const ipf = ipForm(rawHost);
    if (ipf) add('high', 'Host is an IP address (' + ipf + ')', 'Real organisations use domain names. ' + (ipf !== 'dotted IPv4' && ipf !== 'IPv6' ? 'The browser reads ' + rawHost + ' as ' + host + '.' : ''));
    if (host.includes('xn--') || /[^\x00-\x7f]/.test(rawHost)) {
      const scripts = new Set(Array.from(uni.replace(/[.\-0-9]/g, '')).map(c => /[a-z]/i.test(c) ? 'Latin' : /[\u0400-\u04ff]/.test(c) ? 'Cyrillic' : /[\u0370-\u03ff]/.test(c) ? 'Greek' : /[\u0900-\u097f]/.test(c) ? 'Devanagari' : 'Other'));
      add(scripts.size > 1 ? 'high' : 'med', 'Internationalised domain (punycode)', 'Shown to people as ' + uni + ' but registered as ' + host + '. Scripts used: ' + [...scripts].join(', ') + '.' + (scripts.size > 1 ? ' Mixing scripts is a classic homoglyph trick.' : ''));
    }
    const own = L.officialBrand(host);
    const bankIn = /\.bank\.in$/.test(host);
    if (own) add('pass', 'Official domain of ' + own.name, reg + ' is on our list of official domains. A real domain can still host a redirect, so check the rest of the findings.');
    if (bankIn && !own) add('pass', 'Uses the .bank.in zone', 'Only RBI-regulated banks can register .bank.in, through IDRBT. Still read the full name carefully.');
    if (/\.gov\.in$|\.nic\.in$/.test(host)) add('pass', 'Government of India domain (' + L.suffixOf(host) + ')', 'gov.in and nic.in are restricted to government bodies.');
    if (!own && !bankIn) {
      const like = L.lookalike(L.registrable(L.toUnicode(host).normalize('NFKC'))) || L.lookalike(reg);
      if (like) add('high', 'Lookalike of ' + like.domain, reg + ' resembles the official ' + like.domain + ' (' + like.brand.name + ') by ' + like.how + '.');
      const inHost = L.brandsIn(host.replace(reg, ' ' + reg.split('.')[0]));
      const inSub = L.brandsIn(host.slice(0, Math.max(0, host.length - reg.length)));
      if (inSub.length) add('high', 'Brand name used as a subdomain', '"' + host.slice(0, host.length - reg.length - 1) + '" sits in front of ' + reg + ', which is the real owner. ' + reg + ' is not on our list of ' + inSub[0].name + ' domains.');
      else if (inHost.length && !like) add('high', 'Brand name inside an unofficial domain', reg + ' mentions ' + inHost[0].name + ' but is not on our list of its official domains (' + inHost[0].domains.join(', ') + ').');
      const govWords = /(incometax|aadhaar|aadhar|uidai|epfo|parivahan|echallan|challan|pmkisan|govt|government|police|cybercrime)/i.exec(host);
      if (govWords && !/\.gov\.in$|\.nic\.in$/.test(host)) add('high', 'Government-sounding name outside gov.in', '"' + govWords[1] + '" appears in a domain that does not end in .gov.in or .nic.in.');
    }
    if (RISKY_TLD.includes(tld)) add('med', 'Ending often seen in phishing (.' + tld + ')', 'Cheap or abused domain endings show up a lot in phishing reports. Not proof on its own.');
    if (SHORTENERS.includes(host)) add('med', 'Link shortener (' + host + ')', 'The real destination is hidden. This tool does not expand it, because expanding means contacting the shortener. Ask the sender for the full link or open the brand\'s app yourself.');
    const labels = host.split('.');
    if (labels.length >= 5) add('low', 'Many subdomains (' + labels.length + ' labels)', 'Long chains push the real domain out of view on small screens.');
    if ((host.replace(/xn--/g, '').match(/-/g) || []).length >= 3) add('low', 'Many hyphens in the host', 'Patterns like secure-login-update-bank are common in phishing domains.');
    if (host.length > 50) add('low', 'Very long host name (' + host.length + ' characters)', 'The real domain may be hidden off screen.');
    if (u.port && !['80', '443'].includes(u.port)) add('low', 'Unusual port :' + u.port, 'Normal websites do not need a port number.');
    const ext = (/\.([a-z0-9]{1,4})$/i.exec(u.pathname) || [])[1];
    if (ext && RISKY_EXT[ext.toLowerCase()]) add(RISKY_EXT[ext.toLowerCase()], 'Downloads a .' + ext.toLowerCase() + ' file', ext.toLowerCase() === 'apk' ? 'APK files install Android apps outside the Play Store. Fake e-challan, KYC and wedding-card APKs steal OTPs and SMS.' : 'Opening downloaded files from links can install malware.');
    const pathAll = (u.pathname + ' ' + u.search).toLowerCase();
    const bait = BAIT.filter(w => new RegExp('(^|[^a-z])' + w + '([^a-z]|$)').test(pathAll) || host.split(/[.-]/).includes(w));
    if (bait.length >= 2) add('med', 'Bait words in the link', bait.slice(0, 6).join(', ') + '. Phishing links copy the words of the action they want from you.');
    else if (bait.length === 1) add('low', 'Bait word in the link', bait[0]);
    if (/@/.test(u.pathname)) add('low', '@ inside the path', 'Harmless for the browser, but often used to make a link look like an email address or another site.');
    const dec = pctDecode(u.href);
    if (dec.layers >= 2) add('med', 'Encoded ' + dec.layers + ' times', 'Repeated percent-encoding hides the real text from filters and readers.');

    // Redirect chain (never followed: we only read the destination written inside the link)
    const chain = [];
    if (depth < 5) for (const r of REDIRECTORS) {
      if (!r.host.test(host) || (r.path && !r.path.test(u.pathname))) continue;
      const key = r.param.find(p => u.searchParams.get(p));
      if (!key) continue;
      let val = u.searchParams.get(key);
      const b = b64(val); if (b) val = b;
      val = pctDecode(val).text;
      if (!/^(https?:)?\/\/|^www\./i.test(val)) continue;
      add(r.generic ? 'med' : 'info', (r.generic ? 'Redirect parameter "' + key + '"' : r.name) + ' wraps another link', 'The real destination written inside is ' + val.slice(0, 200) + (b ? ' (it was hidden with base64).' : '.'));
      const inner = analyse(val, depth + 1);
      if (inner) chain.push({ via: r.name, url: val, res: inner });
      break;
    }
    u.searchParams.forEach((v, k) => { const b = b64(v); if (b && !chain.length) add('med', 'Hidden link in parameter "' + k + '"', 'Base64 decodes to: ' + b.slice(0, 160)); });

    const worst = [F, ...chain.map(c => c.res.F)].flat();
    const level = worst.some(f => f.sev === 'high') ? 'high' : worst.filter(f => f.sev === 'med').length >= 1 ? 'med' : 'low';
    return { raw, F, level, parts, chain };
  }
  const defang = s => String(s).replace(/^http/i, 'hxxp').replace(/\./g, '[.]');

  function block(r, title) {
    const order = { high: 0, med: 1, low: 2, info: 3, pass: 4 };
    const p = r.parts, kv = (k, v) => v ? [el('dt', { text: k }), el('dd', {}, [el('code', { text: v })])] : [];
    return el('div', { class: 'lab-block' }, [
      title ? el('h3', { class: 'lab-sub', text: title }) : null,
      el('ul', { class: 'lab-findings' }, r.F.length ? r.F.slice().sort((a, b) => order[a.sev] - order[b.sev]).map(f => finding(f.sev, f.t, f.d)) : [finding('info', 'No red flags found in the text of this link', 'That does not make it safe. Open the organisation\'s app or type its address yourself.')]),
      p ? el('details', { class: 'lab-raw', open: true }, [el('summary', { text: 'Anatomy of the link' }), el('dl', { class: 'lab-kv' }, [].concat(
        kv('Scheme', p.scheme), kv('Text before @', p.user), kv('Host (as registered)', p.host), kv('Host (as people see it)', p.uni !== p.host ? p.uni : ''),
        kv('Registrable domain (the real owner)', p.reg), kv('Port', p.port), kv('Path', p.path), kv('Query', p.query.map(([k, v]) => k + ' = ' + v).join('\n')), kv('Fragment', p.hash)))]) : null
    ]);
  }
  function render(r) {
    const box = $('#uf-result'); box.replaceChildren(); box.hidden = false;
    if (!r) { box.append(el('p', { class: 'lab-empty', text: 'No link found. Paste a URL or a message that contains one.' })); return; }
    const verdict = { high: ['High risk: do not open', 'v-high'], med: ['Suspicious: verify another way', 'v-med'], low: ['No strong red flags in the link text', 'v-low'] }[r.level];
    box.append(el('div', { class: 'lab-verdict ' + verdict[1], role: 'status' }, [el('strong', { text: verdict[0] }), el('span', { text: ' This tool only reads the text of the link. It never opens it.' })]),
      el('p', { class: 'lab-defang' }, [el('span', { class: 'muted small', text: 'Safe to share (defanged): ' }), el('code', { id: 'uf-def', text: defang(r.raw) }),
        el('button', { type: 'button', class: 'btn btn-ghost small', id: 'uf-copy', 'data-goatcounter-click': 'lab-url-copy-defanged', text: 'Copy' })]),
      block(r, 'Findings'));
    let c = r.chain;
    while (c && c.length) { box.append(block(c[0].res, 'Hidden destination via ' + c[0].via + ': ' + defang(c[0].url).slice(0, 120))); c = c[0].res.chain; }
    $('#uf-copy').addEventListener('click', () => L.copy($('#uf-def').textContent));
  }
  function run(e) {
    if (e) e.preventDefault();
    const link = extract($('#uf-input').value);
    render(link ? analyse(link) : null);
  }
  function init() {
    $('#uf-form').addEventListener('submit', run);
    document.querySelectorAll('[data-uf-try]').forEach(b => b.addEventListener('click', () => { $('#uf-input').value = b.dataset.ufTry; run(); }));
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  window.CWMUrl = { analyse, extract, defang };
})();
