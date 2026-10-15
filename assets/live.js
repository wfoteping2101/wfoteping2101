/* Live parts of static pages: which books are free right now, and the gallery of moments (photos and footage
   with their stories) that the owner adds from his private admin page. */
(function () {
  const SB = 'https://qytpqmgzphiuhlwkybiy.supabase.co/rest/v1/rpc/', PK = 'sb_publishable_QgRtb2_rjK2-hMG0s4i2Bw_Y11M05_X';
  const fr = () => document.documentElement.getAttribute('lang') === 'fr';
  const rpc = (fn, body) => fetch(SB + fn, { method: 'POST', headers: { apikey: PK, 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) }).then(r => r.ok ? r.json() : Promise.reject(r.status));
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };

  /* free state on book cards */
  const tags = document.querySelectorAll('[data-free-slug]');
  let pub = null;
  function paintFree() {
    if (!pub) return;
    tags.forEach(t => {
      const b = (pub.books || []).find(x => x.slug === t.dataset.freeSlug); if (!b) return;
      const until = b.free_until ? new Date(b.free_until) : null;
      const d = until ? until.toLocaleDateString(fr() ? 'fr-FR' : 'en-US', { day: 'numeric', month: 'long' }) : '';
      t.textContent = b.free ? (until ? (fr() ? 'Gratuit jusqu’au ' + d : 'Free until ' + d) : (fr() ? 'Gratuit' : 'Free'))
        : (fr() ? 'Extrait gratuit' : 'Free excerpt');
      t.classList.toggle('paused', !b.free);
    });
  }
  if (tags.length) rpc('pf_public').then(p => { pub = p; paintFree(); }).catch(() => {});

  /* moments: photos and footage with their story */
  const box = document.querySelector('[data-regards]');
  let items = [];
  function render() {
    if (!box) return;
    box.innerHTML = '';
    if (!items.length) { box.closest('section').hidden = true; return; }
    box.closest('section').hidden = false;
    items.forEach((it, i) => {
      const fig = el('figure', 'moment rv in' + (i % 2 ? ' alt' : ''));
      const frame = el('div', 'm-media');
      if (it.kind === 'video') {
        const v = el('video'); v.src = it.url; if (it.poster) v.poster = it.poster; v.muted = true; v.loop = true; v.playsInline = true; v.preload = 'metadata'; v.controls = true;
        v.setAttribute('controlslist', 'nodownload noplaybackrate'); v.disablePictureInPicture = true;
        frame.appendChild(v);
      } else {
        const img = el('img'); img.src = it.url; img.alt = (fr() ? it.title_fr : it.title) || it.title || ''; img.loading = 'lazy'; img.decoding = 'async';
        frame.appendChild(img);
      }
      const cap = el('figcaption', 'm-story');
      const meta = [it.place, it.taken ? new Date(it.taken + 'T12:00:00').toLocaleDateString(fr() ? 'fr-FR' : 'en-US', { month: 'long', year: 'numeric' }) : ''].filter(Boolean).join(' · ');
      if (meta) cap.appendChild(el('span', 'm-meta mono', meta));
      const title = (fr() ? it.title_fr || it.title : it.title || it.title_fr) || '';
      if (title) cap.appendChild(el('h3', 'm-title', title));
      const story = (fr() ? it.story_fr || it.story : it.story || it.story_fr) || '';
      story.split(/\n{2,}/).forEach(p => { if (p.trim()) cap.appendChild(el('p', '', p.trim())); });
      fig.appendChild(frame); fig.appendChild(cap); box.appendChild(fig);
    });
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(es => es.forEach(e => { const v = e.target.querySelector('video'); if (v) { e.isIntersecting ? v.play().catch(() => {}) : v.pause(); } }), { threshold: .5 });
      box.querySelectorAll('.moment').forEach(m => io.observe(m));
    }
  }
  if (box) rpc('pf_gallery').then(g => { items = Array.isArray(g) ? g : []; render(); }).catch(() => { box.closest('section').hidden = true; });
  addEventListener('wf-lang', () => { paintFree(); if (items.length) render(); });
})();
