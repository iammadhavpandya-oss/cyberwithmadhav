/* CyberPrompts: search, category filter, favourites (localStorage), copy. */
(function () {
  'use strict';
  const P = window.CWMP; if (!P) return;
  const { $, el } = P;
  const FKEY = 'cwm-prompt-favs';
  const STAR = '<path d="M12 3.5l2.6 5.3 5.9.9-4.25 4.1 1 5.8L12 16.9l-5.25 2.7 1-5.8L3.5 9.7l5.9-.9z"/>';
  let data = null, cat = 'all', favOnly = false, q = '';
  let favs = new Set(P.store(FKEY, []));

  function starSvg() {
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('width', '18'); s.setAttribute('height', '18');
    s.setAttribute('fill', 'none'); s.setAttribute('stroke', 'currentColor'); s.setAttribute('stroke-width', '1.8');
    s.setAttribute('stroke-linejoin', 'round'); s.setAttribute('aria-hidden', 'true');
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    p.setAttribute('d', STAR.match(/d="([^"]+)"/)[1]); s.append(p);
    return s;
  }

  function codeNodes(text) {
    const out = []; let last = 0; const re = /\[[^\]\n]{1,60}\]/g; let m;
    while ((m = re.exec(text))) {
      if (m.index > last) out.push(document.createTextNode(text.slice(last, m.index)));
      out.push(el('span', { class: 'ph', text: m[0] }));
      last = m.index + m[0].length;
    }
    if (last < text.length) out.push(document.createTextNode(text.slice(last)));
    return out;
  }

  function card(p, catName) {
    const fav = el('button', { type: 'button', class: 'fav', 'aria-pressed': String(favs.has(p.id)), 'aria-label': 'Favourite: ' + p.title, title: 'Save to favourites' }, [starSvg()]);
    fav.addEventListener('click', () => {
      if (favs.has(p.id)) favs.delete(p.id); else favs.add(p.id);
      P.save(FKEY, Array.from(favs));
      fav.setAttribute('aria-pressed', String(favs.has(p.id)));
      P.toast(favs.has(p.id) ? 'Saved to favourites' : 'Removed from favourites');
      updateFavCount();
      if (favOnly) render();
    });
    const pre = el('pre', { tabindex: '0', 'aria-label': 'Prompt template: ' + p.title }, [el('code', null, codeNodes(p.prompt))]);
    const copy = el('button', { type: 'button', class: 'copy', 'aria-label': 'Copy prompt: ' + p.title }, ['Copy']);
    copy.addEventListener('click', () => P.copyText(p.prompt, copy));
    return el('article', { class: 'card p-card', 'data-id': p.id, 'data-cat': p.cat }, [
      el('div', { class: 'p-top' }, [
        el('div', null, [el('span', { class: 'tag p', text: catName }), el('h3', { text: p.title })]),
        fav
      ]),
      el('p', { class: 'p-use' }, [el('b', { text: 'Use case: ' }), p.use]),
      el('div', { class: 'code-box' }, [copy, pre]),
      el('p', { class: 'p-tip' }, [el('b', { text: 'Pro tip: ' }), p.tip]),
      el('p', { class: 'p-model' }, [el('b', { text: 'Best model: ' }), p.model])
    ]);
  }

  function updateFavCount() {
    $('#fav-n').textContent = String(data ? data.prompts.filter(p => favs.has(p.id)).length : favs.size);
  }

  function inCat(p, id) {
    if (id === 'all') return true;
    const c = data.categories.find(x => x.id === id);
    return c && c.group ? c.group.includes(p.cat) : p.cat === id;
  }

  function matches(p) {
    if (!inCat(p, cat)) return false;
    if (favOnly && !favs.has(p.id)) return false;
    if (!q) return true;
    const hay = (p.title + ' ' + p.use + ' ' + p.prompt + ' ' + p.tip + ' ' + p.cat).toLowerCase();
    return q.split(/\s+/).every(w => hay.includes(w));
  }

  function render() {
    const grid = $('#p-grid'); grid.textContent = '';
    const names = Object.fromEntries(data.categories.map(c => [c.id, c.name]));
    const list = data.prompts.filter(matches);
    list.forEach(p => grid.append(card(p, names[p.cat] || p.cat)));
    if (!list.length) grid.append(el('p', { class: 'empty', text: favOnly && !favs.size ? 'No favourites yet. Tap the star on any prompt to save it here.' : 'No prompts match. Try another word or category.' }));
    const cname = cat === 'all' ? 'all categories' : names[cat];
    $('#p-count').textContent = 'Showing ' + list.length + ' of ' + data.prompts.length + ' prompts in ' + cname + (favOnly ? ' (favourites only)' : '') + '.';
  }

  function setCat(id) {
    cat = id;
    $('#p-cats').querySelectorAll('.chip').forEach(c => c.setAttribute('aria-pressed', String(c.dataset.cat === id)));
    render();
  }

  const LV = { beginner: 'Beginner', mid: 'Mid', expert: 'Expert' };
  function usecases(list) {
    const grid = $('#uc-grid'); grid.textContent = '';
    const names = Object.fromEntries(data.categories.map(c => [c.id, c.name]));
    list.forEach(u => {
      const known = !!names[u.cat_id];
      const open = known ? el('button', { type: 'button', class: 'btn btn-ghost small', 'aria-label': 'Show ' + names[u.cat_id] + ' prompts for: ' + u.title }, ['Show ' + names[u.cat_id] + ' prompts']) : null;
      if (open) open.addEventListener('click', () => {
        q = ''; $('#p-search').value = ''; favOnly = false; $('#p-favs').setAttribute('aria-pressed', 'false');
        setCat(u.cat_id);
        const lib = $('#library'); lib.scrollIntoView({ behavior: P.reduce ? 'auto' : 'smooth', block: 'start' });
        $('#p-search').focus({ preventScroll: true });
      });
      const lvl = (u.level || '').toLowerCase();
      grid.append(el('article', { class: 'card uc reveal', 'data-level': lvl }, [
        el('div', { class: 'meta' }, [el('span', { class: 'lvl ' + lvl, text: LV[lvl] || u.level }), el('span', { class: 'tag p', text: u.which_prompt_category })]),
        el('h3', { text: u.title }),
        el('p', { text: u.scenario }),
        el('ol', null, (u.steps || []).map(t => el('li', { text: t }))),
        el('p', { class: 'safe' }, [el('b', { text: 'Safety:' }), el('span', { text: u.safety_note })]),
        open
      ]));
    });
    P.reveal(Array.from(grid.children));
    const lb = $('#uc-levels');
    lb.addEventListener('click', e => {
      const b = e.target.closest('.chip'); if (!b) return;
      lb.querySelectorAll('.chip').forEach(c => c.setAttribute('aria-pressed', String(c === b)));
      grid.querySelectorAll('.uc').forEach(c => { c.hidden = !(b.dataset.level === 'all' || c.dataset.level === b.dataset.level); });
    });
  }

  function chips() {
    const box = $('#p-cats'); box.textContent = '';
    const counts = {}; data.categories.forEach(c => { counts[c.id] = data.prompts.filter(p => inCat(p, c.id)).length; });
    const mk = (id, name, n, desc) => {
      const b = el('button', { type: 'button', class: 'chip', 'data-cat': id, 'aria-pressed': String(cat === id), title: desc || null }, [name, el('span', { class: 'n', 'aria-hidden': 'true', text: String(n) })]);
      b.addEventListener('click', () => setCat(id));
      return b;
    };
    box.append(mk('all', 'All', data.prompts.length));
    data.categories.filter(c => counts[c.id]).forEach(c => box.append(mk(c.id, c.name, counts[c.id], c.desc)));
  }

  async function init() {
    try { data = await P.getJSON('data/prompts.json'); }
    catch (e) { $('#p-count').textContent = 'Could not load prompts. Open data/prompts.json directly.'; return; }
    if (data.meta && data.meta.banner) $('#ethics span').textContent = data.meta.banner;
    const params = new URLSearchParams(location.search);
    if (params.get('cat') && data.categories.some(c => c.id === params.get('cat'))) cat = params.get('cat');
    if (params.get('q')) { q = params.get('q').slice(0, 120).trim().toLowerCase(); $('#p-search').value = params.get('q').slice(0, 120); }
    chips(); updateFavCount(); render();
    let t; $('#p-search').addEventListener('input', e => { clearTimeout(t); t = setTimeout(() => { q = e.target.value.trim().toLowerCase(); render(); }, 120); });
    const fb = $('#p-favs');
    fb.addEventListener('click', () => { favOnly = !favOnly; fb.setAttribute('aria-pressed', String(favOnly)); render(); });
    try { usecases(await P.getJSON('data/cyberprompts_usecases.json')); }
    catch (e) { $('#howto').hidden = true; }
    document.documentElement.dataset.promptsReady = '1';
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
