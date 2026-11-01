/* Cyber Law India: renders data/cyberlaw*.json. textContent only. */
(function () {
  'use strict';
  const P = window.CWMP; if (!P) return;
  const { $, el, extLink } = P;
  const LKEY = 'cwm-law-lang';
  let lang = P.store(LKEY, 'en') === 'hi' ? 'hi' : 'en';
  let faq = [], gloss = [];

  const VRE = /\s*\(?\bverify\b\)?\.?/i;
  const hasVerify = s => typeof s === 'string' && /\bverify\b/i.test(s);
  function vtag(title) { return el('span', { class: 'verify', title: title || 'Needs a fresh check before use in court', tabindex: '0' }, ['verify']); }
  /* "being verified": a fact-check item (Mokit's U1 to U6, 2026 IT Rules, RB-IOS 2026) still under confirmation */
  function ptag(title) { return el('span', { class: 'verify pending', title: title || 'Fact-check in progress: confirm against the linked primary source', tabindex: '0' }, ['being verified']); }
  /* turns "text (verify)" / "text (being verified)" into text with inline tags */
  const MRE = /\s*\((verify|being verified)\)/gi;
  function withVerify(text) {
    text = String(text == null ? '' : text);
    if (!MRE.test(text)) { MRE.lastIndex = 0; return [text]; }
    MRE.lastIndex = 0;
    const out = []; let last = 0, m;
    while ((m = MRE.exec(text))) {
      if (m.index > last) out.push(text.slice(last, m.index));
      out.push(' ', m[1].toLowerCase() === 'verify' ? vtag() : ptag());
      last = MRE.lastIndex;
    }
    if (last < text.length) out.push(text.slice(last));
    return out;
  }
  /* structured items: verify = our open question, pending = fact-check item being verified */
  function flags(o) {
    return [o.verify ? vtag(o.verify) : null, o.pending ? ptag(o.pending) : null];
  }
  function notes(o) {
    return [o.verify ? el('span', { class: 'vnote', text: 'Verify: ' + o.verify }) : null,
            o.pending ? el('span', { class: 'vnote', text: 'Being verified: ' + o.pending }) : null];
  }
  function srcList(list) {
    if (!list || !list.length) return null;
    const box = el('p', { class: 'src-list' }, [el('span', { class: 'muted', text: 'Sources: ' })]);
    list.forEach((x, i) => { if (i) box.append(' · '); box.append(extLink(x.url, x.label)); });
    return box;
  }
  function urlOf(s) { const m = String(s || '').match(/https?:\/\/\S+/); return m ? m[0] : ''; }

  function hero(h) {
    const box = $('#hero-cards'); box.textContent = '';
    (h.cards || []).forEach((c, i) => box.append(el('div', { class: 'card ' + (i === 0 ? 'civil' : 'crime') }, [
      el('span', { class: 'lbl', text: c.label }), el('span', { class: 'k', text: c.k }), el('p', { text: c.text }), c.src ? extLink(c.src, 'Bare act') : null
    ])));
    if (h.note) $('#hero-note').textContent = h.note;
  }

  function timeline(list) {
    const ol = $('#tl'); ol.textContent = '';
    list.forEach(t => ol.append(el('li', { class: 'reveal' }, [el('div', { class: 'card' }, [
      el('time', { text: t.date }), el('h3', null, [t.title].concat(flags(t))), el('p', { text: t.text }),
      ...notes(t), extLink(t.src), srcList(t.more)
    ])])));
  }

  /* Nandi's "History of Indian Cyber Law" (data/cyberlaw_timeline.json), patched by the fact-check at build time */
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function fmtDate(iso) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || ''); if (!m) return iso || '';
    return (+m[3]) + ' ' + MON[+m[2] - 1] + ' ' + m[1];
  }
  function history(list) {
    const ol = $('#tl'); ol.textContent = ''; ol.classList.add('tl-hist', 'reveal'); ol.dataset.source = 'file';
    list.forEach((t, i) => {
      const fc = t.added_by ? 'Added from the fact-check of 1 Nov 2026.'
        : (t.corrections && t.corrections.length ? 'Updated by the fact-check of 1 Nov 2026 (' + t.corrections.join(', ') + ').' : '');
      ol.append(el('li', { class: 'reveal ' + (i % 2 ? 'r' : 'l') }, [
        el('span', { class: 'tl-year', 'aria-hidden': 'true', text: String(t.year || '') }),
        el('div', { class: 'card' }, [
          el('time', { datetime: t.date, text: fmtDate(t.date) }),
          el('h3', null, [t.title, t.verify ? vtag('Flagged for a fresh check against the source') : null, t.pending ? ptag(t.pending) : null]),
          el('p', null, withVerify(t.what_changed)),
          t.why_it_matters_for_advocates ? el('p', { class: 'why' }, [el('strong', { text: 'Why it matters for advocates: ' }), t.why_it_matters_for_advocates]) : null,
          t.pending ? el('span', { class: 'vnote', text: 'Being verified: ' + t.pending }) : null,
          fc ? el('span', { class: 'vnote fc', text: fc }) : null,
          el('p', { class: 'src-list' }, [extLink(t.source_url, 'Source')].concat(...(t.more || []).map(x => [' · ', extLink(x.url, x.label)])))
        ])
      ]));
    });
  }

  /* Where to File: Mokit's reporting guide (data/cyberlaw_reporting.json), expandable cards */
  function forums(list) {
    const box = $('#file-list'); box.textContent = '';
    list.forEach((f, i) => {
      const dd = (label, kids) => [el('dt', { text: label }), el('dd', null, kids)];
      box.append(el('details', { class: 'card file-card reveal' + (i < 2 ? ' first' : '') }, [
        el('summary', null, [
          el('span', { class: 'fn', 'aria-hidden': 'true', text: String(i + 1).padStart(2, '0') }),
          el('span', { class: 'ft' }, [f.forum]),
          i < 2 ? el('span', { class: 'start', text: 'Start here' }) : null,
          f.verify ? vtag('Flagged in the reporting guide: confirm against the official site before relying on it') : null
        ]),
        el('div', { class: 'file-body' }, [
          el('dl', null, [
            ...dd('Who can file', [f.who_can_file]),
            ...dd('When to use', [f.when_to_use]),
            ...dd('Time limit', [f.time_limit]),
            ...dd('Documents needed', [el('ul', null, (f.documents_needed || []).map(x => el('li', { text: x })))])
          ]),
          el('p', { class: 'src-list' }, [extLink(f.official_url, 'Official site')])
        ])
      ]));
    });
  }

  const KIND = { offence: 'Offence', civil: 'Civil', struck: 'Struck down', rule: 'Rule' };
  function itact(rows) {
    const tb = $('#it-table tbody'); tb.textContent = '';
    rows.forEach(r => tb.append(el('tr', { class: r.kind === 'struck' ? 'struck' : null, 'data-kind': r.kind }, [
      el('td', { class: 'sec' }, [r.sec]),
      el('td', null, [r.title]),
      el('td', null, [el('span', { class: 'kind ' + r.kind, text: KIND[r.kind] || r.kind })]),
      el('td', null, [r.punishment]),
      el('td', null, [r.bail, r.bail_pending ? ptag(r.bail_pending) : null]),
      el('td', null, [r.compound].concat(flags(r), notes(r))),
      el('td', null, [extLink(r.src, r.src_label || 'Bare act'), r.src2 ? el('br') : null, r.src2 ? extLink(r.src2, r.src2_label || 'Amendment') : null])
    ])));
    $('#it-filter').addEventListener('click', e => {
      const b = e.target.closest('.chip'); if (!b) return;
      $('#it-filter').querySelectorAll('.chip').forEach(c => c.setAttribute('aria-pressed', String(c === b)));
      const k = b.dataset.k;
      tb.querySelectorAll('tr').forEach(tr => { const d = tr.dataset.kind; tr.hidden = !(k === 'all' || d === k || (k === 'rule' && d === 'struck')); });
    });
  }

  function bns(rows, note) {
    const tb = $('#bns-table tbody'); tb.textContent = '';
    rows.forEach(r => tb.append(el('tr', null, [el('td', null, [r.topic]), el('td', { class: 'sec' }, [r.bns]), el('td', null, [r.ipc]),
      el('td', null, [r.punishment || 'See BNS text']),
      el('td', null, [extLink(r.src, 'NCRB table'), r.src2 ? el('br') : null, r.src2 ? extLink(r.src2, 'BNS gazette') : null])])));
    if (note) $('#bns-note').textContent = note;
  }

  function dpdp(d) {
    const g = $('#dp-grid'); g.textContent = '';
    if (d.intro) g.before(el('p', { class: 'dp-intro muted', text: d.intro }));
    d.rows.forEach(r => g.append(el('div', { class: 'card reveal' }, [el('span', { class: 'amt', text: r.max }), el('p', { text: r.breach })])));
    const st = $('#dp-status'); st.textContent = '';
    st.append(...withVerify(d.status || ''), ' ');
    if (d.src) st.append(extLink(d.src, 'DPDP Act'));
    if (d.src2) { st.append(' · '); st.append(extLink(d.src2, 'Commencement notification')); }
  }

  function steps(list) {
    const g = $('#steps'); g.textContent = '';
    list.forEach(s => g.append(el('div', { class: 'card reveal' }, [
      el('h3', null, [el('span', { class: 'n', 'aria-hidden': 'true', text: s.step }), el('span', { class: 'sr-only', text: 'Step ' + s.step + ': ' }), s.title].concat(flags(s))),
      el('p', { text: s.text }), ...notes(s), extLink(s.src), srcList(s.more)
    ])));
  }

  /* Case files. Prefer Nandi's data/cyberlaw_cases.json; fall back to the built-in list. */
  function citation(raw) {
    if (!hasVerify(raw)) return { text: raw, pending: false };
    const parts = raw.split(';').map(s => s.trim()).filter(Boolean);
    const keep = parts.filter(p => !(hasVerify(p) && /\b(SCC|DLT|AIR|SCR)\b/.test(p))).map(p => p.replace(VRE, '').trim());
    return { text: keep.join('; '), pending: true };
  }
  function normCase(c) {
    if (c.citation !== undefined) return c;
    return { name: c.name, citation: c.cite + (c.verify ? ' (verify)' : ''), year: c.year, court: c.court, facts: '', held: c.held, why_it_matters: '', source: c.src, note: c.verify };
  }
  function cases(list) {
    const g = $('#case-grid'); g.textContent = '';
    list.map(normCase).forEach(c => {
      const ci = citation(c.citation || '');
      const src = urlOf(c.source);
      const secondary = hasVerify(c.source) || /secondary/i.test(c.source || '');
      const kids = [
        el('span', { class: 'stamp', 'aria-hidden': 'true', text: 'HELD' }),
        el('h3', { text: c.name }),
        el('p', { class: 'cite' }, [ci.text, ci.pending ? el('span', { class: 'verify', title: 'Report citation not yet confirmed against the official reporter' }, ['citation being verified']) : null]),
        c.court ? el('p', { class: 'muted court-name', text: c.court }) : null,
        c.facts ? el('p', null, [el('span', { class: 'lbl', text: 'Facts' }), c.facts]) : null,
        el('p', null, [el('span', { class: 'lbl', text: 'Held' })].concat(withVerify(c.held))),
        c.why_it_matters ? el('p', null, [el('span', { class: 'lbl', text: 'Why it matters' }), c.why_it_matters]) : null,
        c.note ? el('span', { class: 'vnote', text: 'Verify: ' + c.note }) : null,
        el('p', { class: 'case-links' }, [
          src ? extLink(src, secondary ? 'Secondary source' : 'Read judgment') : null,
          secondary ? vtag('Secondary source; no official text online') : null,
          c.status_src ? ' · ' : null, c.status_src ? extLink(c.status_src, 'SC appeal status') : null
        ])
      ];
      g.append(el('article', { class: 'card case reveal', 'data-year': c.year, 'aria-label': c.name + ', ' + c.year }, kids));
    });
  }

  function refsNode(refs) {
    return el('div', { class: 'refs', 'aria-label': 'References' }, (refs || []).map(r => el('span', { class: 'tag' }, withVerify(r))));
  }
  function renderFaq() {
    const box = $('#faq-list'); box.textContent = '';
    faq.forEach((f, i) => {
      const a = lang === 'hi' ? (f.a_hinglish || f.a_en) : f.a_en;
      box.append(el('details', { class: 'card', id: 'faq-' + (i + 1) }, [
        el('summary', { text: f.q }),
        el('div', { class: 'ans', lang: lang === 'hi' ? 'hi-Latn' : 'en' }, [el('p', null, withVerify(a)), refsNode(f.refs), srcList(f.sources)])
      ]));
    });
  }
  function renderGloss() {
    const q = ($('#gl-search').value || '').trim().toLowerCase();
    const list = $('#gl-list'); list.textContent = '';
    let n = 0;
    gloss.forEach(g => {
      const m = lang === 'hi' ? (g.meaning_hinglish || g.meaning_en) : g.meaning_en;
      if (q && !(g.term + ' ' + g.meaning_en + ' ' + (g.meaning_hinglish || '')).toLowerCase().includes(q)) return;
      n++;
      list.append(el('div', { class: 'card gl-item' }, [el('dt', { text: g.term }), el('dd', { lang: lang === 'hi' ? 'hi-Latn' : 'en' }, withVerify(m)), g.ref ? el('dd', null, [el('span', { class: 'tag' }, withVerify(g.ref))]) : null, g.sources ? el('dd', null, [srcList(g.sources)]) : null]));
    });
    $('#gl-count').textContent = n + ' of ' + gloss.length + ' terms';
  }
  function setLang(l) {
    lang = l; P.save(LKEY, l);
    document.querySelectorAll('.lang .chip').forEach(c => c.setAttribute('aria-pressed', String(c.dataset.lang === l)));
    const open = Array.from(document.querySelectorAll('#faq-list details[open]')).map(d => d.id);
    renderFaq(); open.forEach(id => { const d = document.getElementById(id); if (d) d.open = true; });
    renderGloss();
  }

  async function downloads(list) {
    const g = $('#dl-grid'); g.textContent = '';
    for (const d of list) {
      const card = el('div', { class: 'card' }, [el('h3', { text: d.title }), el('p', { text: d.desc })]);
      g.append(card);
      const ok = d.available === false ? false : await P.exists(d.file);
      card.append(ok ? el('a', { class: 'btn btn-primary small', href: d.file, download: '' }, ['Download PDF'])
        : el('span', { class: 'soon', 'data-file': d.file }, ['PDF coming soon']));
    }
  }

  async function init() {
    const page = $('.law-page') || document.body;
    requestAnimationFrame(() => page.classList.add('go'));
    let d;
    try { d = await P.getJSON('data/cyberlaw.json'); } catch (e) { $('#tl').append(el('li', { text: 'Could not load data/cyberlaw.json.' })); return; }
    hero(d.hero);
    let hist = null;
    try { hist = await P.getJSON('data/cyberlaw_timeline.json'); } catch (e) { hist = null; }
    if (Array.isArray(hist) && hist.length) history(hist); else timeline(d.timeline);
    itact(d.itact); bns(d.bns, d.bns_note); dpdp(d.dpdp); steps(d.procedure);
    let cl = d.cases, fromFile = false;
    try { const x = await P.getJSON('data/cyberlaw_cases.json'); if (Array.isArray(x) && x.length) { cl = x; fromFile = true; } } catch (e) { /* fallback */ }
    let fl = [];
    try { fl = await P.getJSON('data/cyberlaw_reporting.json'); } catch (e) { fl = []; }
    if (Array.isArray(fl) && fl.length) forums(fl); else $('#where-to-file').hidden = true;
    cases(cl); $('#case-grid').dataset.source = fromFile ? 'file' : 'builtin';
    try { faq = await P.getJSON('data/cyberlaw_faq.json'); } catch (e) { faq = []; }
    if (!faq.length) $('#faq').hidden = true;
    try { gloss = await P.getJSON('data/cyberlaw_glossary.json'); } catch (e) { gloss = []; }
    if (!gloss.length) $('#glossary').hidden = true;
    gloss.sort((a, b) => a.term.localeCompare(b.term));
    document.querySelectorAll('.lang .chip').forEach(c => c.addEventListener('click', () => setLang(c.dataset.lang)));
    $('#gl-search').addEventListener('input', renderGloss);
    setLang(lang);
    P.reveal();
    await downloads(d.downloads || []);
    document.documentElement.dataset.lawReady = '1';
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
