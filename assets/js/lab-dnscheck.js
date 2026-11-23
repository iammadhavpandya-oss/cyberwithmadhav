/* Domain Email and DNS Security Posture Checker. Uses CWMLab.dns (Cloudflare DNS over HTTPS). Only the domain name leaves the browser. */
(function () {
  'use strict';
  const L = window.CWMLab, { el, finding } = L, $ = s => document.querySelector(s);
  const SELECTORS = ['google', 'selector1', 'selector2', 'default', 'dkim', 'mail', 'k1', 'k2', 's1', 's2', 'zmail', 'hostingermail-a', 'hostingermail-b', 'mxvault', 'smtp', 'everlytickey1'];
  let report = '';

  async function check(domain) {
    const out = { domain, checks: [], raw: [] };
    const add = (id, sev, pts, max, title, detail, fix) => out.checks.push({ id, sev, pts, max, title, detail, fix });
    const [a, aaaa, ns, mx, caa, soa] = await Promise.all([L.dns(domain, 'A'), L.dns(domain, 'AAAA'), L.dns(domain, 'NS'), L.dns(domain, 'MX'), L.dns(domain, 'CAA'), L.dns(domain, 'DNSKEY')]);
    if (ns.nx) { out.nx = true; return out; }
    out.raw.push(['NS', ns.answers], ['MX', mx.answers], ['A', a.answers], ['AAAA', aaaa.answers], ['CAA', caa.answers]);
    const nullMx = mx.answers.length === 1 && /^0\s+\.$/.test(mx.answers[0].trim());
    out.sendsMail = mx.answers.length > 0 && !nullMx;

    // MX
    if (nullMx) add('mx', 'pass', 0, 0, 'Null MX: this domain says it receives no email', 'RFC 7505 null MX record "0 ." is set.');
    else if (mx.answers.length) add('mx', 'info', 0, 0, 'Mail servers (MX) found: ' + mx.answers.length, mx.answers.map(m => m.replace(/\.$/, '')).join(', '));
    else add('mx', 'info', 0, 0, 'No MX record', 'The domain does not receive email directly. It can still be spoofed in the From line unless SPF and DMARC say "no mail".', 'v=spf1 -all  (and a DMARC p=reject record) for domains that never send mail');

    // SPF
    const s = await L.spf(domain);
    out.raw.push(['SPF (TXT)', s.records]);
    if (!s.records.length) add('spf', 'fail', 0, 35, 'No SPF record', 'Receivers cannot tell which servers may send mail for this domain, which makes spoofing easier.',
      out.sendsMail ? 'TXT @  "v=spf1 include:<your mail provider> ~all"  e.g. include:_spf.google.com (Google Workspace), include:spf.protection.outlook.com (Microsoft 365), include:_spf.mail.hostinger.com (Hostinger)' : 'TXT @  "v=spf1 -all"');
    else {
      let pts = 15;
      if (s.records.length > 1) add('spf1', 'fail', 0, 0, 'More than one SPF record (' + s.records.length + ')', 'RFC 7208 treats this as a permanent error, so SPF fails for every message.', 'Merge them into one v=spf1 record');
      else { pts += 5; }
      if (s.lookups > 10) add('spfl', 'fail', 0, 0, 'SPF needs ' + s.lookups + ' DNS lookups (limit is 10)', 'Above 10 lookups SPF returns a permanent error at many receivers.', 'Remove unused include: entries or flatten some of them');
      else pts += 5;
      const all = s.all;
      const allMsg = { '-': ['pass', 10, 'SPF ends in -all (hard fail)', 'Unlisted servers are rejected. Strongest setting.'],
        '~': ['pass', 10, 'SPF ends in ~all (soft fail)', 'Unlisted servers are marked suspicious. Fine when DMARC is enforced.'],
        '?': ['warn', 3, 'SPF ends in ?all (neutral)', 'This says nothing about unlisted servers, so it gives almost no protection.'],
        '+': ['fail', 0, 'SPF ends in +all', 'This allows every server on the internet to send as this domain.'],
        'none': ['warn', 3, 'SPF has no all mechanism', 'Without an all at the end, unlisted servers get a neutral result.'],
        'redirect': ['pass', 10, 'SPF uses redirect=', 'The policy comes from the redirect target.'] }[all] || ['warn', 3, 'SPF all qualifier unclear', ''];
      add('spf', all === '+' ? 'fail' : 'pass', pts, 25, 'SPF record found', s.record + '  (' + s.lookups + ' of 10 DNS lookups used)');
      add('spfall', allMsg[0], allMsg[1], 10, allMsg[2], allMsg[3], allMsg[0] === 'pass' ? null : 'End the record with ~all or -all');
      if (s.ptr) add('spfptr', 'warn', 0, 0, 'SPF uses the ptr mechanism', 'RFC 7208 says ptr should not be used: it is slow and unreliable.', 'Replace ptr with ip4:/ip6: or include:');
      s.errors.forEach(e => add('spfe', 'warn', 0, 0, 'SPF include problem', e));
    }

    // DMARC
    const d = await L.dmarc(domain);
    out.raw.push(['DMARC (_dmarc TXT)', d.records]);
    if (!d.record) add('dmarc', 'fail', 0, 35, 'No DMARC record', 'Without DMARC, receivers have no instruction for mail that fails SPF and DKIM, and you get no reports about spoofing.',
      'TXT _dmarc  "v=DMARC1; p=none; rua=mailto:dmarc-reports@' + domain + '"  then move to p=quarantine and p=reject after reading reports');
    else {
      const t = d.tags, p = (t.p || '').toLowerCase(), pct = t.pct ? parseInt(t.pct, 10) : 100;
      if (d.records.length > 1) add('dmarc2', 'fail', 0, 0, 'More than one DMARC record', 'Receivers ignore DMARC when there are several records.', 'Keep exactly one v=DMARC1 record');
      add('dmarc', 'pass', 15, 15, 'DMARC record found' + (d.from !== domain ? ' (inherited from ' + d.from + ')' : ''), d.record);
      const pol = { reject: ['pass', 15, 'DMARC policy is reject', 'Spoofed mail that fails checks is refused. Strongest setting.'],
        quarantine: ['pass', 11, 'DMARC policy is quarantine', 'Failing mail goes to spam. Consider p=reject once reports are clean.'],
        none: ['warn', 3, 'DMARC policy is none (monitor only)', 'Spoofed mail is still delivered. p=none is meant as a short first step.'] }[p] || ['fail', 0, 'DMARC policy tag p= is missing or invalid', ''];
      add('dmarcp', pol[0], pol[1], 15, pol[2], pol[3], p === 'reject' ? null : 'Move to p=quarantine, then p=reject');
      if (p !== 'none' && pct < 100) add('dmarcpct', 'warn', 0, 0, 'DMARC applies to only ' + pct + '% of failing mail', 'The rest gets the next weaker policy (' + (p === 'reject' ? 'quarantine' : 'none') + '), as RFC 7489 describes.', 'Remove pct= or set pct=100');
      if (t.rua) add('rua', 'pass', 5, 5, 'DMARC aggregate reports are sent', 'rua=' + t.rua);
      else add('rua', 'warn', 0, 5, 'No DMARC reporting address (rua)', 'You will not see who is sending mail as your domain.', 'Add rua=mailto:dmarc-reports@' + domain);
      if (t.sp && t.sp.toLowerCase() === 'none' && p !== 'none') add('sp', 'warn', 0, 0, 'Subdomain policy sp=none', 'Subdomains can still be spoofed.', 'Set sp=quarantine or sp=reject');
    }

    // DKIM selector probe
    const found = [];
    await Promise.all(SELECTORS.map(async sel => { try { const r = await L.txt(sel + '._domainkey.' + domain); if (r.answers.some(x => /k=|p=/.test(x))) found.push(sel); } catch (e) { } }));
    out.raw.push(['DKIM selectors found', found.map(x => x + '._domainkey')]);
    if (found.length) add('dkim', 'pass', 10, 10, 'DKIM key found (selector: ' + found.join(', ') + ')', 'Messages can be signed so receivers can check they were not altered.');
    else add('dkim', out.sendsMail ? 'warn' : 'info', 0, out.sendsMail ? 10 : 0, 'No DKIM key at ' + SELECTORS.length + ' common selectors', 'DKIM selectors cannot be listed from DNS, so a key may exist under another name. Check a real email from this domain: the DKIM-Signature header shows s=selector.', 'Turn on DKIM signing in your mail provider and publish its key');

    // DNSSEC
    const dnssec = a.ad || ns.ad || mx.ad;
    out.raw.push(['DNSKEY', soa.answers.length ? [soa.answers.length + ' key(s)'] : []]);
    if (dnssec) add('dnssec', 'pass', 5, 5, 'DNSSEC is on and validates', 'Cloudflare\'s resolver marked the answers as authenticated (AD flag).');
    else add('dnssec', 'warn', 0, 5, 'DNSSEC not validated', 'DNS answers for this domain are not signed (or the chain is broken), so they could be forged in transit.', 'Turn on DNSSEC at your DNS host and add the DS record at your registrar');

    // CAA
    if (caa.answers.length) add('caa', 'pass', 5, 5, 'CAA record limits who can issue TLS certificates', caa.answers.join(' | '));
    else add('caa', 'warn', 0, 5, 'No CAA record', 'Any certificate authority may issue certificates for this domain.', 'CAA @  0 issue "letsencrypt.org"  (use your actual certificate authority)');

    // MTA-STS, TLS-RPT, BIMI
    const [sts, rpt, bimi] = await Promise.all([L.txt('_mta-sts.' + domain), L.txt('_smtp._tls.' + domain), L.txt('default._bimi.' + domain)]);
    const stsRec = sts.answers.find(x => /^v=STSv1/i.test(x)), rptRec = rpt.answers.find(x => /^v=TLSRPTv1/i.test(x)), bimiRec = bimi.answers.find(x => /^v=BIMI1/i.test(x));
    out.raw.push(['MTA-STS', stsRec ? [stsRec] : []], ['TLS-RPT', rptRec ? [rptRec] : []], ['BIMI', bimiRec ? [bimiRec] : []]);
    const mailOnly = out.sendsMail ? 1 : 0;
    if (stsRec) add('sts', 'pass', 3, 3, 'MTA-STS is published', stsRec + '. The policy file itself (https://mta-sts.' + domain + '/.well-known/mta-sts.txt) is not fetched from the browser.');
    else add('sts', mailOnly ? 'warn' : 'info', 0, 3 * mailOnly, 'No MTA-STS', 'Senders cannot be told to require encrypted (TLS) delivery to your mail servers.', mailOnly ? 'TXT _mta-sts  "v=STSv1; id=20261123"  plus a policy file at https://mta-sts.' + domain + '/.well-known/mta-sts.txt' : null);
    if (rptRec) add('rpt', 'pass', 2, 2, 'TLS reporting (TLS-RPT) is on', rptRec);
    else add('rpt', mailOnly ? 'warn' : 'info', 0, 2 * mailOnly, 'No TLS-RPT', 'You get no reports when other servers fail to deliver to you securely.', mailOnly ? 'TXT _smtp._tls  "v=TLSRPTv1; rua=mailto:tls-reports@' + domain + '"' : null);
    add('bimi', 'info', 0, 0, bimiRec ? 'BIMI logo record found' : 'No BIMI record (optional)', bimiRec || 'BIMI shows a verified brand logo in some inboxes. It needs DMARC enforcement first.');

    const max = out.checks.reduce((n, c) => n + c.max, 0), got = out.checks.reduce((n, c) => n + c.pts, 0);
    out.score = max ? Math.round(got * 100 / max) : 0;
    out.grade = out.score >= 90 ? 'A' : out.score >= 75 ? 'B' : out.score >= 60 ? 'C' : out.score >= 40 ? 'D' : 'F';
    return out;
  }

  function render(r) {
    const box = $('#dc-result'); box.replaceChildren(); box.hidden = false;
    if (r.nx) { box.append(el('p', { class: 'lab-empty', text: r.domain + ' does not exist in DNS (NXDOMAIN). Check the spelling.' })); return; }
    const order = { fail: 0, warn: 1, pass: 2, info: 3 };
    const sorted = r.checks.slice().sort((a, b) => order[a.sev] - order[b.sev]);
    const nFail = r.checks.filter(c => c.sev === 'fail').length, nWarn = r.checks.filter(c => c.sev === 'warn').length;
    box.append(
      el('div', { class: 'lab-summary' }, [
        el('div', { class: 'lab-grade g-' + r.grade, 'aria-label': 'Grade ' + r.grade }, [el('span', { text: r.grade }), el('small', { text: r.score + '/100' })]),
        el('div', {}, [el('h2', { class: 'lab-h', text: r.domain }),
          el('p', { class: 'muted', text: nFail + ' failed, ' + nWarn + ' warnings, ' + r.checks.filter(c => c.sev === 'pass').length + ' passed. ' + (r.sendsMail ? 'This domain receives email.' : 'This domain does not receive email (no MX), so it should declare that it sends none.') }),
          el('p', { class: 'small muted', text: 'Checked ' + new Date().toLocaleString('en-IN') + ' through Cloudflare DNS over HTTPS.' })])
      ]),
      el('h3', { class: 'lab-sub', text: 'Findings and fixes' }),
      el('ul', { class: 'lab-findings' }, sorted.map(c => finding(c.sev, c.title, c.detail, c.fix))),
      el('details', { class: 'lab-raw' }, [el('summary', { text: 'Raw DNS records' }),
        el('dl', {}, r.raw.flatMap(([k, v]) => [el('dt', { text: k }), el('dd', {}, [el('code', { text: v && v.length ? v.join('\n') : '(none)' })])]))])
    );
    report = ['CyberWithMadhav DNS and email security check', 'Domain: ' + r.domain, 'Grade: ' + r.grade + ' (' + r.score + '/100)', '']
      .concat(sorted.map(c => '[' + c.sev.toUpperCase() + '] ' + c.title + (c.detail ? '\n  ' + c.detail : '') + (c.fix ? '\n  Fix: ' + c.fix : '')))
      .concat(['', 'Checked with https://www.cyberwithmadhav.com/dns-security-checker.html']).join('\n');
    $('#dc-copy').hidden = false;
  }

  async function run(e) {
    if (e) e.preventDefault();
    const d = L.normDomain($('#dc-domain').value);
    const st = $('#dc-status');
    if (!d) { st.textContent = 'Enter a domain like example.com or an email address.'; return; }
    $('#dc-domain').value = d; st.textContent = 'Checking ' + d + '...'; $('#dc-go').disabled = true; $('#dc-copy').hidden = true;
    try { const r = await check(d); render(r); st.textContent = r.nx ? 'Domain not found.' : 'Done. Grade ' + r.grade + '.';
      history.replaceState(null, '', location.pathname + '?d=' + encodeURIComponent(d)); }
    catch (err) { st.textContent = 'Could not reach the DNS service. Check your connection and try again.'; }
    finally { $('#dc-go').disabled = false; }
  }

  function init() {
    $('#dc-form').addEventListener('submit', run);
    $('#dc-copy').addEventListener('click', () => L.copy(report));
    document.querySelectorAll('[data-dc-try]').forEach(b => b.addEventListener('click', () => { $('#dc-domain').value = b.dataset.dcTry; run(); }));
    const q = new URLSearchParams(location.search).get('d');
    if (q) { $('#dc-domain').value = q.slice(0, 253); run(); }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  window.CWMDnsCheck = { check };
})();
