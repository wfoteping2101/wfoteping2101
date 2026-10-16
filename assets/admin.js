/* The owner's private room: who visits and reads, the free switch of each book, the donation link,
   and the gallery of moments (upload photos and footage, write their story). Guarded by a private key
   that only the owner has; every action is checked again by the backend. */
(function () {
  const root = document.querySelector('.admin'); if (!root) return;
  const SB = 'https://qytpqmgzphiuhlwkybiy.supabase.co', PK = 'sb_publishable_QgRtb2_rjK2-hMG0s4i2Bw_Y11M05_X';
  const $ = (s, r) => (r || root).querySelector(s), $$ = (s, r) => Array.from((r || root).querySelectorAll(s));
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }, del(k) { try { localStorage.removeItem(k); } catch (e) {} } };
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const nf = n => (n == null ? 0 : n).toLocaleString('fr-FR');
  let KEY = '';
  let BOOKS = [];

  async function admin(action, p) {
    const r = await fetch(SB + '/rest/v1/rpc/pf_admin', { method: 'POST', headers: { apikey: PK, 'Content-Type': 'application/json' }, body: JSON.stringify({ p_key: KEY, p_action: action, p: p || {} }) });
    if (!r.ok) throw new Error('Erreur ' + r.status);
    const d = await r.json();
    if (d && d.error === 'denied') { logout(); throw new Error('Clé refusée'); }
    if (d && d.error) throw new Error(d.error);
    return d;
  }
  function toast(m, bad) { const t = $('.a-toast'); t.textContent = m; t.classList.toggle('bad', !!bad); t.classList.add('on'); clearTimeout(t._t); t._t = setTimeout(() => t.classList.remove('on'), 2600); }

  /* ---------- sign in ---------- */
  async function login(k) {
    KEY = k.trim();
    try { await admin('check'); } catch (e) { KEY = ''; $('.a-login .err').textContent = 'Cette clé ne passe pas. Réessayez.'; return; }
    store.set('pf-admin-key', KEY);
    if (store.get('pf-me') === null) store.set('pf-me', '1');
    $('.a-login').hidden = true; $('.a-app').hidden = false;
    $('#me-toggle').checked = store.get('pf-me') === '1';
    show(store.get('pf-admin-tab') || 'stats');
  }
  function logout() { KEY = ''; store.del('pf-admin-key'); $('.a-app').hidden = true; $('.a-login').hidden = false; }
  $('.a-login form').addEventListener('submit', e => { e.preventDefault(); login($('.a-login input').value); });
  $('#logout').addEventListener('click', logout);

  /* ---------- tabs ---------- */
  function show(tab) {
    $$('.a-tabs button').forEach(b => b.setAttribute('aria-selected', b.dataset.tab === tab ? 'true' : 'false'));
    $$('.a-pane').forEach(p => p.hidden = p.dataset.pane !== tab);
    store.set('pf-admin-tab', tab);
    if (tab === 'stats') loadStats();
    if (tab === 'books') loadBooks();
    if (tab === 'gallery') loadGallery();
    if (tab === 'settings') loadSettings();
  }
  $$('.a-tabs button').forEach(b => b.addEventListener('click', () => show(b.dataset.tab)));

  /* ---------- visits and readers ---------- */
  const countryName = (() => { try { const d = new Intl.DisplayNames(['fr'], { type: 'region' }); return c => { try { return c && c !== '?' ? d.of(c) : 'Inconnu'; } catch (e) { return c; } }; } catch (e) { return c => c; } })();
  const bookTitle = s => (BOOKS.find(b => b.slug === s) || {}).title || s || '';
  const KIND = { view: 'a ouvert', chapter: 'a lu', read: 'lecture', donate: 'a cliqué Café', donate_go: 'est allé sur Stripe', outbound: 'est parti vers', play: 'a lancé' };
  function bars(rows, key, label, max) {
    max = max || Math.max(1, ...rows.map(r => r[key] || 0));
    return '<div class="a-bars">' + rows.map(r => `<div class="a-bar"><span class="l">${esc(label(r))}</span><span class="t"><i style="width:${Math.max(2, (r[key] || 0) / max * 100)}%"></i></span><span class="v">${nf(r[key])}</span></div>`).join('') + '</div>';
  }
  function chart(daily, days) {
    const map = new Map(daily.map(d => [d.day, d]));
    const out = []; const now = new Date();
    for (let i = days - 1; i >= 0; i--) { const d = new Date(now); d.setDate(now.getDate() - i); const k = d.toISOString().slice(0, 10); out.push(Object.assign({ day: k, views: 0, visitors: 0, chapters: 0 }, map.get(k) || {})); }
    const max = Math.max(1, ...out.map(d => Math.max(d.views, d.chapters)));
    const W = 720, H = 180, bw = W / out.length;
    const rects = out.map((d, i) => {
      const hv = d.views / max * (H - 24), hc = d.chapters / max * (H - 24);
      return `<g><title>${d.day} : ${d.visitors} visiteurs, ${d.views} pages, ${d.chapters} chapitres</title><rect x="${i * bw + bw * .12}" y="${H - 18 - hv}" width="${bw * .38}" height="${hv}" rx="2" class="cv"/><rect x="${i * bw + bw * .52}" y="${H - 18 - hc}" width="${bw * .38}" height="${hc}" rx="2" class="cc"/></g>`;
    }).join('');
    const ticks = out.map((d, i) => (out.length <= 14 || i % Math.ceil(out.length / 10) === 0) ? `<text x="${i * bw + bw / 2}" y="${H - 4}" text-anchor="middle">${d.day.slice(8)}/${d.day.slice(5, 7)}</text>` : '').join('');
    return `<svg viewBox="0 0 ${W} ${H}" class="a-chart" role="img" aria-label="Pages vues et chapitres lus par jour">${rects}${ticks}</svg><p class="a-legend"><i class="cv"></i> Pages vues <i class="cc"></i> Chapitres lus</p>`;
  }
  let statsTimer;
  async function loadStats() {
    const days = parseInt($('#range').value, 10);
    const box = $('.a-stats'); box.classList.add('busy');
    try {
      if (!BOOKS.length) BOOKS = await admin('books');
      const s = await admin('stats', { days });
      const tiles = [['En ce moment', s.live, 'visiteurs sur le site'], ['Visiteurs', s.visitors, 'personnes différentes'], ['Pages vues', s.views, ''], ['Lecteurs', s.readers, 'ont ouvert un chapitre'],
        ['Chapitres lus', s.chapters, ''], ['Minutes de lecture', s.reading_minutes, ''], ['Clics Café', s.donate_clicks, '']];
      $('.a-tiles').innerHTML = tiles.map(t => `<div class="a-tile"><span>${t[0]}</span><b>${nf(t[1])}</b><small>${t[2]}</small></div>`).join('');
      $('.a-daily').innerHTML = chart(s.daily || [], days);
      const books = s.books || [];
      $('.a-books-read').innerHTML = books.length ? `<table><thead><tr><th>Livre</th><th>Lecteurs</th><th>Chapitres lus</th><th>Le plus loin</th><th>Ont fini</th><th>Minutes</th></tr></thead><tbody>${books.map(b => {
        const total = (BOOKS.find(x => x.slug === b.book) || {}).sections || 0;
        return `<tr><td>${esc(bookTitle(b.book))}</td><td>${nf(b.readers)}</td><td>${nf(b.chapters)}</td><td>${b.deepest != null ? (b.deepest + 1) + ' / ' + total : ''}</td><td>${nf(b.finished)}</td><td>${nf(b.minutes)}</td></tr>`; }).join('')}</tbody></table>` : '<p class="muted">Personne n’a encore ouvert de chapitre sur cette période.</p>';
      const cb = s.chapters_by_book || [];
      const byBook = {}; cb.forEach(r => { (byBook[r.book] = byBook[r.book] || []).push(r); });
      $('.a-funnel').innerHTML = Object.keys(byBook).map(k => `<h4>${esc(bookTitle(k))}</h4>` + bars(byBook[k], 'readers', r => 'Section ' + (r.chapter + 1))).join('') || '<p class="muted">Rien encore.</p>';
      $('.a-countries').innerHTML = bars((s.countries || []).slice(0, 15), 'visitors', r => countryName(r.country));
      $('.a-cities').innerHTML = bars((s.cities || []).slice(0, 15), 'visitors', r => (r.city === '?' ? 'Ville inconnue' : r.city) + ', ' + countryName(r.country));
      $('.a-pages').innerHTML = bars((s.pages || []).slice(0, 15), 'visitors', r => r.path);
      $('.a-refs').innerHTML = bars((s.referrers || []).slice(0, 12), 'visits', r => r.referrer === 'direct' ? 'Accès direct ou application' : r.referrer);
      $('.a-devices').innerHTML = bars(s.devices || [], 'visitors', r => ({ mobile: 'Téléphone', desktop: 'Ordinateur', tablet: 'Tablette' }[r.device] || r.device));
      $('.a-recent tbody').innerHTML = (s.recent || []).map(e => {
        const t = new Date(e.at);
        const what = e.kind === 'chapter' ? `${esc(bookTitle(e.book))}, section ${e.chapter + 1}` : e.kind === 'read' ? `${esc(bookTitle(e.book))}, ${Math.round((e.seconds || 0) / 60)} min` : e.kind === 'outbound' ? esc(e.book || '') : esc(e.path || bookTitle(e.book) || '');
        const where = [e.city, e.country ? countryName(e.country) : ''].filter(Boolean).join(', ');
        return `<tr><td class="mono">${t.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })} ${t.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</td><td class="mono">${esc(e.visitor || '')}</td><td>${KIND[e.kind] || e.kind}</td><td>${what}</td><td>${esc(where)}</td><td>${esc([e.device, e.browser].filter(Boolean).join(', '))}</td><td>${esc(e.referrer || '')}</td></tr>`;
      }).join('') || '<tr><td colspan="7" class="muted">Aucune activité.</td></tr>';
      $('.a-updated').textContent = 'Mis à jour à ' + new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    } catch (e) { toast(e.message, true); }
    box.classList.remove('busy');
    clearTimeout(statsTimer); statsTimer = setTimeout(() => { if (!$('[data-pane="stats"]').hidden) loadStats(); }, 60000);
  }
  $('#range').addEventListener('change', loadStats);
  $('#refresh').addEventListener('click', loadStats);

  /* ---------- books: free or paused ---------- */
  const toLocalInput = iso => { if (!iso) return ''; const d = new Date(iso); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10); };
  async function loadBooks() {
    try { BOOKS = await admin('books'); } catch (e) { return toast(e.message, true); }
    $('.a-booklist').innerHTML = BOOKS.map(b => `<article class="a-book" data-slug="${esc(b.slug)}">
      <div class="h"><h3>${esc(b.title)}</h3><span class="state ${b.free_now ? 'on' : 'off'}">${b.free_now ? 'Gratuit maintenant' : 'En pause : extrait seulement'}</span></div>
      <p class="muted">${b.sections} sections. <a href="/lire/${esc(b.slug)}" target="_blank" rel="noopener">Voir la page</a></p>
      <label class="sw"><input type="checkbox" name="free" ${b.free ? 'checked' : ''}><span>Lecture libre activée</span></label>
      <div class="a-row"><label>Gratuit jusqu’au (vide = sans fin)<input type="date" name="until" value="${toLocalInput(b.free_until)}"></label>
      <label>Sections lisibles quand c’est en pause<input type="number" min="0" max="10" name="preview" value="${b.preview}"></label></div>
      <label>Lien d’achat affiché quand c’est en pause<input type="url" name="buy" value="${esc(b.buy_url || '')}" placeholder="https://"></label>
      <div class="a-actions"><button class="a-btn" data-save>Enregistrer</button><button class="a-btn ghost" data-month>Gratuit 30 jours à partir d’aujourd’hui</button><button class="a-btn ghost" data-close>Fermer maintenant</button></div></article>`).join('');
    $$('.a-book').forEach(card => {
      const slug = card.dataset.slug;
      const save = async (over) => {
        const until = card.querySelector('[name=until]').value;
        const p = Object.assign({ slug, free: card.querySelector('[name=free]').checked, free_until: until ? new Date(until + 'T23:59:00').toISOString() : '',
          preview: parseInt(card.querySelector('[name=preview]').value || '1', 10), buy_url: card.querySelector('[name=buy]').value.trim() }, over || {});
        try { await admin('set_book', p); toast('Enregistré'); loadBooks(); } catch (e) { toast(e.message, true); }
      };
      card.querySelector('[data-save]').addEventListener('click', () => save());
      card.querySelector('[data-month]').addEventListener('click', () => { const d = new Date(); d.setDate(d.getDate() + 30); d.setHours(23, 59, 0, 0); save({ free: true, free_until: d.toISOString() }); });
      card.querySelector('[data-close]').addEventListener('click', () => save({ free: false }));
    });
  }
  $('#all-month').addEventListener('click', async () => { const d = new Date(); d.setDate(d.getDate() + 30); d.setHours(23, 59, 0, 0); try { await admin('set_all', { free: true, free_until: d.toISOString() }); toast('Tous les livres sont gratuits 30 jours'); loadBooks(); } catch (e) { toast(e.message, true); } });
  $('#all-open').addEventListener('click', async () => { try { await admin('set_all', { free: true, free_until: '' }); toast('Tous les livres sont gratuits, sans date de fin'); loadBooks(); } catch (e) { toast(e.message, true); } });
  $('#all-close').addEventListener('click', async () => { try { await admin('set_all', { free: false }); toast('Lecture libre fermée pour tous les livres'); loadBooks(); } catch (e) { toast(e.message, true); } });

  /* ---------- gallery of moments ---------- */
  let GALLERY = [];
  async function loadGallery() {
    try { GALLERY = await admin('gallery'); } catch (e) { return toast(e.message, true); }
    $('.a-glist').innerHTML = GALLERY.length ? GALLERY.map(itemForm).join('') : '<p class="muted">Aucun moment pour l’instant. Ajoutez une photo ou une vidéo ci-dessus.</p>';
    $$('.a-gitem').forEach(wire);
  }
  function itemForm(g) {
    const media = g.kind === 'video' ? `<video src="${esc(g.url)}" ${g.poster ? `poster="${esc(g.poster)}"` : ''} muted playsinline controls preload="metadata"></video>` : `<img src="${esc(g.url)}" alt="" loading="lazy">`;
    return `<article class="a-gitem" data-id="${esc(g.id || '')}" data-kind="${esc(g.kind)}" data-url="${esc(g.url)}" data-poster="${esc(g.poster || '')}">
      <div class="m">${media}</div><div class="f">
      <div class="a-row"><label>Titre<input name="title" value="${esc(g.title || '')}" placeholder="La lumière du soir à Kribi"></label><label>Titre en français<input name="title_fr" value="${esc(g.title_fr || '')}"></label></div>
      <label>L’histoire (anglais)<textarea name="story" rows="4" placeholder="Ce que l’on voit, pourquoi cela compte, ce que cela vous a appris.">${esc(g.story || '')}</textarea></label>
      <label>L’histoire (français)<textarea name="story_fr" rows="4">${esc(g.story_fr || '')}</textarea></label>
      <div class="a-row"><label>Lieu<input name="place" value="${esc(g.place || '')}" placeholder="Reims, France"></label><label>Date<input type="date" name="taken" value="${esc(g.taken || '')}"></label><label>Ordre (plus grand = en premier)<input type="number" name="sort" value="${g.sort || 0}"></label></div>
      <label class="sw"><input type="checkbox" name="published" ${g.published === false ? '' : 'checked'}><span>Visible dans la galerie</span></label>
      <div class="a-actions"><button class="a-btn" data-save>Enregistrer</button>${g.id ? '<button class="a-btn ghost danger" data-del>Retirer</button>' : ''}</div></div></article>`;
  }
  function wire(card) {
    card.querySelector('[data-save]').addEventListener('click', async () => {
      const v = n => card.querySelector(`[name=${n}]`);
      const p = { id: card.dataset.id || '', kind: card.dataset.kind, url: card.dataset.url, poster: card.dataset.poster || '', title: v('title').value.trim(), title_fr: v('title_fr').value.trim(),
        story: v('story').value.trim(), story_fr: v('story_fr').value.trim(), place: v('place').value.trim(), taken: v('taken').value, sort: parseInt(v('sort').value || '0', 10), published: v('published').checked };
      try { const r = await admin('gallery_save', p); card.dataset.id = r.id || p.id; toast('Moment enregistré'); loadGallery(); } catch (e) { toast(e.message, true); }
    });
    const del = card.querySelector('[data-del]');
    if (del) del.addEventListener('click', async () => {
      if (del.dataset.armed !== '1') { del.dataset.armed = '1'; del.textContent = 'Confirmer le retrait'; setTimeout(() => { del.dataset.armed = ''; del.textContent = 'Retirer'; }, 4000); return; }
      try { await admin('gallery_delete', { id: card.dataset.id }); toast('Retiré de la galerie'); loadGallery(); } catch (e) { toast(e.message, true); }
    });
  }
  async function signed(file) {
    const r = await fetch(SB + '/functions/v1/pf-upload', { method: 'POST', headers: { apikey: PK, 'Content-Type': 'application/json' }, body: JSON.stringify({ key: KEY, type: file.type, name: file.name || 'media' }) });
    const d = await r.json(); if (!r.ok || d.error) throw new Error(d.error === 'type' ? 'Format non accepté' : 'Envoi refusé');
    const up = await fetch(d.signedUrl, { method: 'PUT', headers: { 'Content-Type': file.type, 'x-upsert': 'false' }, body: file });
    if (!up.ok) throw new Error('Envoi interrompu (' + up.status + ')');
    return d.publicUrl;
  }
  function posterOf(file) {
    return new Promise(resolve => {
      try {
        const v = document.createElement('video'); v.muted = true; v.playsInline = true; v.preload = 'auto'; v.src = URL.createObjectURL(file);
        v.addEventListener('loadeddata', () => { v.currentTime = Math.min(1.5, (v.duration || 2) / 3); });
        v.addEventListener('seeked', () => {
          const c = document.createElement('canvas'); const s = Math.min(1, 1280 / Math.max(v.videoWidth, v.videoHeight)); c.width = v.videoWidth * s; c.height = v.videoHeight * s;
          c.getContext('2d').drawImage(v, 0, 0, c.width, c.height); c.toBlob(b => resolve(b ? new File([b], 'poster.jpg', { type: 'image/jpeg' }) : null), 'image/jpeg', .86);
        });
        v.addEventListener('error', () => resolve(null)); setTimeout(() => resolve(null), 12000);
      } catch (e) { resolve(null); }
    });
  }
  async function shrink(file) {
    if (!/^image\/(jpeg|png|webp)$/.test(file.type) || file.size < 1.5e6) return file;
    try {
      const bmp = await createImageBitmap(file); const s = Math.min(1, 2400 / Math.max(bmp.width, bmp.height));
      const c = document.createElement('canvas'); c.width = Math.round(bmp.width * s); c.height = Math.round(bmp.height * s); c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
      const b = await new Promise(r => c.toBlob(r, 'image/jpeg', .88)); return b ? new File([b], file.name.replace(/\.\w+$/, '') + '.jpg', { type: 'image/jpeg' }) : file;
    } catch (e) { return file; }
  }
  $('#files').addEventListener('change', async e => {
    const files = Array.from(e.target.files || []); e.target.value = '';
    for (const f0 of files) {
      const status = $('.a-upload .st');
      if (f0.size > 50 * 1024 * 1024) { toast(f0.name + ' dépasse 50 Mo. Raccourcissez la vidéo ou exportez-la en 1080p.', true); continue; }
      try {
        status.textContent = 'Envoi de ' + f0.name + '…';
        const f = await shrink(f0);
        const kind = f.type.startsWith('video') ? 'video' : 'image';
        let poster = '';
        if (kind === 'video') { const p = await posterOf(f); if (p) poster = await signed(p); }
        const url = await signed(f);
        const card = document.createElement('div'); card.innerHTML = itemForm({ kind, url, poster, published: true, sort: 0 });
        const el = card.firstElementChild; $('.a-glist').prepend(el); wire(el);
        const p = $('.a-glist > p.muted'); if (p) p.remove();
        status.textContent = f0.name + ' est en ligne. Écrivez son histoire, puis Enregistrer.';
      } catch (err) { status.textContent = ''; toast(err.message, true); }
    }
  });

  /* ---------- settings ---------- */
  async function loadSettings() {
    try { const r = await fetch(SB + '/rest/v1/rpc/pf_public', { method: 'POST', headers: { apikey: PK, 'Content-Type': 'application/json' }, body: '{}' }); const d = await r.json(); const links = (d.donations && d.donations.length) ? d.donations : (d.donation_url ? [{ label: '', url: d.donation_url }] : []); document.querySelectorAll('.a-don').forEach((row, i) => { const l = links[i] || {}; row.querySelector('.dl').value = l.label || ''; row.querySelector('.du').value = l.url || ''; }); } catch (e) {}
  }
  $('#save-donation').addEventListener('click', async () => { const links = [...document.querySelectorAll('.a-don')].map(r => ({ label: r.querySelector('.dl').value.trim(), url: r.querySelector('.du').value.trim() })).filter(x => x.url); try { await admin('set_donations', { links }); toast(links.length ? 'Liens de don enregistrés' : 'Liens de don retirés'); } catch (e) { toast(e.message === 'link not allowed' ? 'Lien refusé. Utilisez un lien https de Stripe, Ko-fi, PayPal, Flutterwave, CinetPay, Buy Me a Coffee ou Patreon.' : e.message, true); } });
  $('#me-toggle').addEventListener('change', e => { store.set('pf-me', e.target.checked ? '1' : '0'); toast(e.target.checked ? 'Vos visites ne sont plus comptées sur cet appareil' : 'Vos visites sont comptées'); });
  $('#change-key').addEventListener('click', async () => {
    const a = $('#new-key').value.trim(), b = $('#new-key2').value.trim();
    if (a.length < 12) return toast('Au moins 12 caractères', true);
    if (a !== b) return toast('Les deux clés ne sont pas identiques', true);
    try { await admin('change_key', { new_key: a }); KEY = a; store.set('pf-admin-key', a); $('#new-key').value = $('#new-key2').value = ''; toast('Nouvelle clé enregistrée'); } catch (e) { toast(e.message, true); }
  });

  /* ---------- start ---------- */
  const q = new URLSearchParams(location.search).get('k');
  if (q) { history.replaceState(null, '', location.pathname); login(q); }
  else if (store.get('pf-admin-key')) login(store.get('pf-admin-key'));
})();
