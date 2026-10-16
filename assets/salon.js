/* The reading room: one chapter at a time, a remembered place, page tones, and a calm piece of music
   composed live in the browser (no audio files), with a choice of weather. Sound starts only on a tap. */
(function () {
  const root = document.querySelector('.salon'); if (!root) return;
  const chaps = [...root.querySelectorAll('.chap')], toc = root.querySelector('.toc'), tocLinks = [...root.querySelectorAll('.toc nav a')];
  const now = root.querySelector('.now'), bar = root.querySelector('.progress i'), colophon = root.querySelector('.colophon');
  const rbar = root.querySelector('.reader-bar'), header = document.querySelector('header.top');
  const book = root.dataset.book, KEY = 'salon-' + book;
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  let cur = -1;

  /* ---------- the text lives in the protected backend; one chapter is fetched at a time ---------- */
  const SB = root.dataset.sb + '/rest/v1/rpc/', PK = root.dataset.pk;
  const vid = (window.pfVisitor && window.pfVisitor()) || '', sid = (window.pfSession && window.pfSession()) || '';
  const lockBox = root.querySelector('.lock');
  const isFrUI = () => document.documentElement.getAttribute('lang') === 'fr';
  async function rpc(fn, body) {
    const r = await fetch(SB + fn, { method: 'POST', headers: { apikey: PK, 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
    if (!r.ok) throw new Error('rpc ' + r.status);
    return r.json();
  }
  const loaded = new Map();
  function msg(c, fr, en) { c.querySelector('.text').innerHTML = '<p class="note">' + (isFrUI() ? fr : en) + '</p>'; }
  async function load(i) {
    const c = chaps[i]; if (!c || loaded.get(i) === 'ok' || loaded.get(i) === 'busy') return;
    loaded.set(i, 'busy');
    try {
      const d = await rpc('pf_chapter', { p_book: book, p_idx: i, p_visitor: vid, p_session: sid });
      if (d && d.html) {
        const t = c.querySelector('.text'); t.removeAttribute('data-pending'); t.innerHTML = d.html;
        t.querySelectorAll('a[href^="http"]').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });
        loaded.set(i, 'ok'); lockBox.hidden = true; c.classList.remove('locked');
        if ((i + 1) % 3 === 0 || i === chaps.length - 1) t.appendChild(supportCard());
      } else if (d && d.locked) {
        loaded.set(i, 'locked'); c.classList.add('locked'); c.querySelector('.text').innerHTML = ''; lockBox.hidden = false;
        c.querySelector('.text').appendChild(lockBox);
      } else if (d && d.slow) {
        loaded.delete(i); msg(c, 'Vous tournez les pages très vite. Patientez une minute, puis rechargez ce chapitre.', 'You are turning pages very fast. Wait a minute, then reload this chapter.');
      } else { loaded.delete(i); msg(c, 'Ce chapitre ne s’est pas chargé. Vérifiez la connexion et réessayez.', 'This chapter did not load. Check the connection and try again.'); }
    } catch (e) {
      loaded.delete(i); msg(c, 'Ce chapitre ne s’est pas chargé. Vérifiez la connexion et réessayez.', 'This chapter did not load. Check the connection and try again.');
    }
    progress();
  }

  /* a support card every third chapter: the book is free, the author asks for a donation */
  let freeUntil = null;
  function bi(en, fr) { const s = document.createElement('span'); s.dataset.en = en; s.dataset.fr = fr; s.textContent = isFrUI() ? fr : en; return s; }
  function supportCard() {
    const a = document.createElement('aside'); a.className = 'support-card';
    const d = freeUntil ? freeUntil : null;
    const dEn = d ? d.toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' }) : '', dFr = d ? d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) : '';
    const k = document.createElement('p'); k.className = 'sc-k'; k.appendChild(bi('Support the author', 'Soutenir l’auteur'));
    const p = document.createElement('p'); p.appendChild(bi(
      (d ? 'This book is free to read until ' + dEn + '. ' : 'This book is free to read. ') + 'Writing it took months of work. If this chapter was useful to you, a donation of any amount pays for the next book.',
      (d ? 'Ce livre se lit gratuitement jusqu’au ' + dFr + '. ' : 'Ce livre se lit gratuitement. ') + 'L’écrire a demandé des mois de travail. Si ce chapitre vous a été utile, un don, quel que soit le montant, finance le prochain livre.'));
    const row = document.createElement('p'); row.className = 'sc-row';
    const b = document.createElement('button'); b.type = 'button'; b.className = 'sc-btn'; b.setAttribute('data-coffee', 'chapter'); b.appendChild(bi('Make a donation', 'Faire un don'));
    const sh = document.createElement('button'); sh.type = 'button'; sh.className = 'sc-share'; sh.appendChild(bi('Copy the link to share', 'Copier le lien pour partager'));
    sh.addEventListener('click', () => { const u = location.origin + location.pathname; (navigator.clipboard ? navigator.clipboard.writeText(u) : Promise.reject()).then(() => { sh.textContent = isFrUI() ? 'Lien copié' : 'Link copied'; }).catch(() => { sh.textContent = u; }); });
    row.append(b, sh); a.append(k, p, row);
    return a;
  }

  /* free or paused, and the donation link, set from the private admin page */
  let donations = [];
  function donLabel(d) {
    if (d.label) return d.label;
    const h = (d.url.match(/^https:\/\/([^/]+)/) || [])[1] || '';
    if (/stripe/.test(h)) return isFrUI() ? 'Carte bancaire' : 'Card';
    if (/flutterwave|cinetpay/.test(h)) return 'Mobile Money';
    if (/ko-fi/.test(h)) return 'Ko-fi'; if (/paypal/.test(h)) return 'PayPal'; if (/buymeacoffee/.test(h)) return 'Buy Me a Coffee'; if (/patreon/.test(h)) return 'Patreon';
    return isFrUI() ? 'Faire un don' : 'Donate';
  }
  rpc('pf_public', {}).then(p => {
    donations = (p.donations && p.donations.length) ? p.donations : (p.donation_url ? [{ label: '', url: p.donation_url }] : []);
    const me = (p.books || []).find(x => x.slug === book); if (!me) return;
    const st = root.querySelector('.free-state'), flag = root.querySelector('.free-flag');
    const until = me.free_until ? new Date(me.free_until) : null; freeUntil = me.free ? until : null;
    const fmt = d => d.toLocaleDateString(isFrUI() ? 'fr-FR' : 'en-US', { day: 'numeric', month: 'long', year: 'numeric' });
    if (me.free) {
      st.textContent = until ? (isFrUI() ? 'Gratuit jusqu’au ' + fmt(until) : 'Free until ' + fmt(until)) : (isFrUI() ? 'Gratuit, complet, en ligne' : 'Free, complete, online');
    } else {
      st.textContent = isFrUI() ? 'Extrait gratuit, lecture complète en pause' : 'Free excerpt, full reading paused';
      if (flag) flag.textContent = isFrUI() ? 'EXTRAIT' : 'EXCERPT';
    }
  }).catch(() => {});

  /* reading time, sent once a minute while the page is visible and a chapter is open */
  let readSec = 0;
  setInterval(() => { if (document.visibilityState === 'visible' && cur >= 0 && loaded.get(cur) === 'ok') readSec += 10;
    if (readSec >= 60 && window.pfTrack) { window.pfTrack('read', { book, chapter: cur, seconds: readSec }); readSec = 0; } }, 10000);
  addEventListener('pagehide', () => { if (readSec > 0 && window.pfTrack) window.pfTrack('read', { book, chapter: cur, seconds: readSec }, true); });

  /* coffee */
  const modal = document.querySelector('.coffee-modal');
  document.addEventListener('click', e => { const b = e.target.closest('[data-coffee]'); if (!b || !modal) return;
    if (window.pfTrack) window.pfTrack('donate', { book, from: b.getAttribute('data-coffee') || '' });
    const wait = modal.querySelector('.cm-wait'), ready = modal.querySelector('.cm-ready');
    ready.innerHTML = '';
    donations.forEach((d, k) => { const a = document.createElement('a'); a.className = 'btn ' + (k === 0 ? 'cobalt' : 'ghost') + ' cm-go'; a.href = d.url; a.target = '_blank'; a.rel = 'noopener'; a.textContent = donLabel(d) + ' \u2192'; ready.appendChild(a); });
    if (donations.length) { ready.hidden = false; wait.hidden = true; } else { ready.hidden = true; wait.hidden = false; }
    modal.hidden = false; modal.querySelector('.cm-x').focus();
  });
  if (modal) { modal.addEventListener('click', e => { if (e.target === modal || e.target.closest('.cm-x')) modal.hidden = true; });
    modal.addEventListener('click', e => { const a = e.target.closest('.cm-go'); if (a && window.pfTrack) window.pfTrack('donate_go', { book, to: (a.href.match(/^https:\/\/([^/]+)/) || [])[1] || '' }); }); }

  /* ---------- layout: the reader bar sits under the site header ---------- */
  function measure() {
    const h = header ? header.getBoundingClientRect().height : 0;
    root.style.setProperty('--hdr', h + 'px');
    root.style.setProperty('--rb-h', (rbar ? rbar.getBoundingClientRect().height : 48) + 'px');
  }
  measure(); addEventListener('resize', measure, { passive: true });
  const offset = () => (header ? header.getBoundingClientRect().height : 0) + (rbar ? rbar.getBoundingClientRect().height : 0) + 18;

  /* ---------- chapters ---------- */
  function show(i, scroll) {
    i = Math.max(0, Math.min(chaps.length - 1, i)); if (i === cur && !scroll) return;
    chaps.forEach((c, k) => c.classList.toggle('on', k === i));
    tocLinks.forEach((a, k) => a.setAttribute('aria-current', k === i ? 'true' : 'false'));
    const c = chaps[i]; cur = i; load(i);
    const title = c.querySelector('h2').textContent.trim(), kick = c.querySelector('.kicker').textContent.trim();
    now.textContent = kick && kick !== title ? kick + ' · ' + title : title;
    const prev = c.querySelector('.prev'), next = c.querySelector('.next');
    if (i > 0) { prev.hidden = false; prev.querySelector('span').textContent = chaps[i - 1].querySelector('h2').textContent; prev.href = '#' + chaps[i - 1].id; } else prev.hidden = true;
    if (i < chaps.length - 1) { next.hidden = false; next.querySelector('span').textContent = chaps[i + 1].querySelector('h2').textContent; next.href = '#' + chaps[i + 1].id; } else next.hidden = true;
    colophon.classList.toggle('on', i === chaps.length - 1);
    toc.classList.remove('open'); root.querySelector('.toc-btn').setAttribute('aria-expanded', 'false');
    store.set(KEY, String(i));
    if (scroll) { const top = c.getBoundingClientRect().top + scrollY - offset(); scrollTo({ top: Math.max(top, 0), behavior: 'smooth' }); }
    progress();
  }
  function fromHash() { const id = decodeURIComponent(location.hash.slice(1)); return chaps.findIndex(c => c.id === id); }
  function progress() { const c = chaps[cur]; if (!c) return; const r = c.getBoundingClientRect(); const seen = Math.min(1, Math.max(0, (innerHeight - r.top) / r.height)); bar.style.width = (((cur + seen) / chaps.length) * 100).toFixed(1) + '%'; }
  addEventListener('scroll', progress, { passive: true });
  addEventListener('hashchange', () => { const k = fromHash(); if (k >= 0) show(k, true); });
  root.querySelectorAll('.chap-nav a, .toc nav a, [data-start]').forEach(a => a.addEventListener('click', e => {
    const id = (a.getAttribute('href') || '').slice(1); const k = chaps.findIndex(c => c.id === id); if (k < 0) return;
    e.preventDefault(); history.replaceState(null, '', '#' + id); show(k, true);
  }));
  root.querySelector('.toc-btn').addEventListener('click', e => { const open = !toc.classList.contains('open'); toc.classList.toggle('open', open); e.currentTarget.setAttribute('aria-expanded', open ? 'true' : 'false'); });

  /* ---------- text size and page tone ---------- */
  root.querySelectorAll('.size').forEach(b => b.addEventListener('click', () => { const s = parseFloat(getComputedStyle(root).getPropertyValue('--size')) || 19; const n = Math.max(15, Math.min(26, s + (b.dataset.size === '+' ? 1 : -1))); root.style.setProperty('--size', n + 'px'); store.set('salon-size', n); }));
  const sz = store.get('salon-size'); if (sz) root.style.setProperty('--size', sz + 'px');
  const TONES = [['paper', 'Paper', 'Papier'], ['sepia', 'Sepia', 'Sépia'], ['night', 'Night', 'Nuit']];
  const paperBtn = root.querySelector('.paper');
  const isFr = () => document.documentElement.getAttribute('lang') === 'fr';
  function tone(k) { const i = Math.max(0, TONES.findIndex(x => x[0] === k)); root.dataset.tone = TONES[i][0]; if (TONES[i][0] === 'paper') delete document.documentElement.dataset.tone; else document.documentElement.dataset.tone = TONES[i][0]; if (paperBtn) paperBtn.textContent = isFr() ? TONES[i][2] : TONES[i][1]; store.set('salon-tone', TONES[i][0]); }
  tone(store.get('salon-tone') || 'paper');
  if (paperBtn) paperBtn.addEventListener('click', () => { const i = TONES.findIndex(x => x[0] === root.dataset.tone); tone(TONES[(i + 1) % TONES.length][0]); });
  new MutationObserver(() => tone(root.dataset.tone)).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });

  addEventListener('keydown', e => { if (e.target.closest('input,textarea,select')) return; if (e.key === 'ArrowRight') show(cur + 1, true); if (e.key === 'ArrowLeft') show(cur - 1, true); if (e.key === 'Escape') { closePanel(); if (modal) modal.hidden = true; } });

  let start = fromHash();
  if (start < 0) { const s = store.get(KEY); if (s !== null) start = parseInt(s, 10); }
  show(start >= 0 ? start : 0, false);
  if (location.hash) setTimeout(() => show(cur, true), 80);

  /* ---------- the music ---------- */
  const Music = (() => {
    let ctx, out, master, bed, timer, on = false, nodes = [], layer = null, amb = store.get('salon-amb') || 'calme', vol = parseFloat(store.get('salon-vol') || '0.7');
    const mood = root.dataset.music || 'clair';
    // Chords as semitone offsets from a root, a slow cycle. "clair": lydian warmth; "braise": dorian embers. "nuit" goes lower and slower.
    const BASE = mood === 'braise'
      ? { root: 110, chords: [[0, 3, 7, 10, 14], [-2, 2, 5, 9, 12], [3, 7, 10, 14, 17], [-4, 0, 3, 7, 10]], scale: [0, 2, 3, 5, 7, 10, 12, 14, 15, 17, 19], tempo: 11 }
      : { root: 146.83, chords: [[0, 4, 7, 11, 14], [5, 9, 12, 16, 19], [-3, 0, 4, 7, 11], [2, 5, 9, 12, 16]], scale: [0, 2, 4, 7, 9, 11, 12, 14, 16, 19, 21], tempo: 10 };
    const prog = () => amb === 'nuit' ? Object.assign({}, BASE, { root: BASE.root * 0.75, tempo: BASE.tempo + 4 }) : BASE;
    const f = (semi) => prog().root * Math.pow(2, semi / 12);
    function build() {
      ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
      out = ctx.createGain(); out.gain.value = 0; out.connect(ctx.destination);
      master = ctx.createGain(); master.gain.value = 1;
      const comp = ctx.createDynamicsCompressor(); comp.threshold.value = -24; comp.ratio.value = 3;
      const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 2600; lp.Q.value = .4;
      const d1 = ctx.createDelay(2), d2 = ctx.createDelay(2), g1 = ctx.createGain(), g2 = ctx.createGain(), wet = ctx.createGain();
      d1.delayTime.value = .37; d2.delayTime.value = .61; g1.gain.value = .34; g2.gain.value = .28; wet.gain.value = .45;
      master.connect(lp); lp.connect(comp); comp.connect(out);
      lp.connect(d1); d1.connect(g1); g1.connect(d1); g1.connect(wet);
      lp.connect(d2); d2.connect(g2); g2.connect(d2); g2.connect(wet);
      wet.connect(comp);
      bed = ctx.createGain(); bed.gain.value = 1; bed.connect(out);
      nodes = [comp, lp, d1, d2, g1, g2, wet, master, bed];
    }
    function noiseBuf(kind) {
      const len = ctx.sampleRate * 6, b = ctx.createBuffer(2, len, ctx.sampleRate);
      for (let ch = 0; ch < 2; ch++) { const d = b.getChannelData(ch); let last = 0, b0 = 0, b1 = 0, b2 = 0;
        for (let i = 0; i < len; i++) { const w = Math.random() * 2 - 1;
          if (kind === 'brown') { last = (last + 0.02 * w) / 1.02; d[i] = last * 3.2; }
          else { b0 = 0.99765 * b0 + w * 0.0990460; b1 = 0.96300 * b1 + w * 0.2965164; b2 = 0.57000 * b2 + w * 1.0526913; d[i] = (b0 + b1 + b2 + w * 0.1848) * 0.11; } } }
      return b;
    }
    function loop(kind) { const s = ctx.createBufferSource(); s.buffer = noiseBuf(kind); s.loop = true; return s; }
    function stopLayer() { if (!layer) return; const L = layer; layer = null; clearTimeout(L.timer); try { L.g.gain.cancelScheduledValues(ctx.currentTime); L.g.gain.setValueAtTime(L.g.gain.value, ctx.currentTime); L.g.gain.linearRampToValueAtTime(0, ctx.currentTime + 1.5); } catch (e) {} setTimeout(() => { L.src.forEach(s => { try { s.stop(); } catch (e) {} }); try { L.g.disconnect(); } catch (e) {} }, 1700); }
    function startLayer() {
      stopLayer(); if (!ctx || !on || amb === 'calme') return;
      const g = ctx.createGain(); g.gain.value = 0; g.connect(bed); const L = { g, src: [], timer: 0 }; layer = L; const t = ctx.currentTime;
      if (amb === 'pluie') { // soft rain on leaves, with the odd heavier drop
        const n = loop('pink'), hp = ctx.createBiquadFilter(), lp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 500; lp.type = 'lowpass'; lp.frequency.value = 7000;
        n.connect(hp); hp.connect(lp); lp.connect(g); n.start(); L.src.push(n); g.gain.linearRampToValueAtTime(.42, t + 3);
        const drop = () => { if (layer !== L) return; const o = ctx.createBufferSource(); o.buffer = noiseBuf('pink'); const bp = ctx.createBiquadFilter(), dg = ctx.createGain(); bp.type = 'bandpass'; bp.frequency.value = 1800 + Math.random() * 2600; bp.Q.value = 8; const s0 = ctx.currentTime; dg.gain.setValueAtTime(0, s0); dg.gain.linearRampToValueAtTime(.5, s0 + .004); dg.gain.exponentialRampToValueAtTime(.001, s0 + .09); o.connect(bp); bp.connect(dg); dg.connect(g); o.start(s0); o.stop(s0 + .12); L.timer = setTimeout(drop, 120 + Math.random() * 700); };
        drop();
      } else if (amb === 'mer') { // a slow swell, breathing every eight or nine seconds
        const n = loop('brown'), lp = ctx.createBiquadFilter(), sw = ctx.createGain(); lp.type = 'lowpass'; lp.frequency.value = 700;
        const lfo = ctx.createOscillator(), lg = ctx.createGain(); lfo.frequency.value = 0.115; lg.gain.value = .32; lfo.connect(lg); lg.connect(sw.gain); sw.gain.value = .42;
        const lfo2 = ctx.createOscillator(), lg2 = ctx.createGain(); lfo2.frequency.value = 0.115; lg2.gain.value = 380; lfo2.connect(lg2); lg2.connect(lp.frequency);
        n.connect(lp); lp.connect(sw); sw.connect(g); n.start(); lfo.start(); lfo2.start(); L.src.push(n, lfo, lfo2); g.gain.linearRampToValueAtTime(.9, t + 4);
      } else if (amb === 'foret') { // morning birds over a little wind
        const n = loop('brown'), lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 500; n.connect(lp); lp.connect(g); n.start(); L.src.push(n); g.gain.linearRampToValueAtTime(.35, t + 3);
        const bird = () => { if (layer !== L) return; const s0 = ctx.currentTime, k = 2 + Math.floor(Math.random() * 4), base = 2200 + Math.random() * 2200;
          for (let j = 0; j < k; j++) { const o = ctx.createOscillator(), bg = ctx.createGain(), a = s0 + j * (0.13 + Math.random() * 0.08); o.type = 'sine'; o.frequency.setValueAtTime(base, a); o.frequency.exponentialRampToValueAtTime(base * (1.15 + Math.random() * 0.4), a + 0.06); o.frequency.exponentialRampToValueAtTime(base * 0.92, a + 0.12);
            bg.gain.setValueAtTime(0, a); bg.gain.linearRampToValueAtTime(.05, a + 0.015); bg.gain.exponentialRampToValueAtTime(.0005, a + 0.13); o.connect(bg); bg.connect(bed); o.start(a); o.stop(a + 0.16); }
          L.timer = setTimeout(bird, 1800 + Math.random() * 5200); };
        L.timer = setTimeout(bird, 900);
      } else if (amb === 'nuit') { // crickets far away and a very low wind
        const n = loop('brown'), lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 320; n.connect(lp); lp.connect(g); n.start(); L.src.push(n); g.gain.linearRampToValueAtTime(.3, t + 3);
        const cricket = () => { if (layer !== L) return; const s0 = ctx.currentTime, fq = 4300 + Math.random() * 500;
          for (let j = 0; j < 3; j++) { const o = ctx.createOscillator(), cg = ctx.createGain(), a = s0 + j * 0.09; o.type = 'triangle'; o.frequency.value = fq; cg.gain.setValueAtTime(0, a); cg.gain.linearRampToValueAtTime(.018, a + 0.01); cg.gain.linearRampToValueAtTime(0, a + 0.05); o.connect(cg); cg.connect(bed); o.start(a); o.stop(a + 0.06); }
          L.timer = setTimeout(cricket, 600 + Math.random() * 1600); };
        cricket();
      }
    }
    function pad(freq, t0, dur, v) {
      const o1 = ctx.createOscillator(), o2 = ctx.createOscillator(), o3 = ctx.createOscillator(), g = ctx.createGain(), fl = ctx.createBiquadFilter();
      o1.type = 'sine'; o2.type = 'triangle'; o3.type = 'sine';
      o1.frequency.value = freq; o2.frequency.value = freq * 1.003; o3.frequency.value = freq * 0.5;
      fl.type = 'lowpass'; fl.frequency.value = amb === 'nuit' ? 650 : 900; fl.Q.value = .3;
      const lfo = ctx.createOscillator(), lg = ctx.createGain(); lfo.frequency.value = .07 + Math.random() * .05; lg.gain.value = 180; lfo.connect(lg); lg.connect(fl.frequency);
      g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(v, t0 + dur * .35); g.gain.setValueAtTime(v, t0 + dur * .7); g.gain.linearRampToValueAtTime(0, t0 + dur);
      o1.connect(fl); o2.connect(fl); o3.connect(fl); fl.connect(g); g.connect(master);
      [o1, o2, o3, lfo].forEach(o => { o.start(t0); o.stop(t0 + dur + .1); });
    }
    function pluck(freq, t0, v) { // kalimba-like: a sine with a fast decay and a soft partial
      const o = ctx.createOscillator(), o2 = ctx.createOscillator(), g = ctx.createGain(), g2 = ctx.createGain();
      o.type = 'sine'; o.frequency.value = freq; o2.type = 'sine'; o2.frequency.value = freq * 2.01;
      g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(v, t0 + .012); g.gain.exponentialRampToValueAtTime(.0005, t0 + 2.4);
      g2.gain.setValueAtTime(0, t0); g2.gain.linearRampToValueAtTime(v * .25, t0 + .008); g2.gain.exponentialRampToValueAtTime(.0004, t0 + .7);
      o.connect(g); o2.connect(g2); g.connect(master); g2.connect(master);
      o.start(t0); o2.start(t0); o.stop(t0 + 2.6); o2.stop(t0 + .9);
    }
    let barN = 0, nextAt = 0;
    function schedule() {
      if (!on) return;
      const t = ctx.currentTime; if (nextAt === 0) nextAt = t + .1;
      const P = prog(), soft = amb === 'calme' ? 1 : .8;
      while (nextAt < t + 1.5) {
        const chord = P.chords[barN % P.chords.length], dur = P.tempo;
        chord.forEach((semi, k) => pad(f(semi) * (k === 0 ? .5 : 1), nextAt + k * .25, dur + 3, (k === 0 ? .055 : .035) * soft));
        let m = nextAt + 1.2 + Math.random();
        while (m < nextAt + dur - 1) {
          if (Math.random() < (amb === 'nuit' ? .55 : .8)) { const s = P.scale[Math.floor(Math.random() * P.scale.length)]; pluck(f(s) * 2, m, (.07 + Math.random() * .05) * soft); }
          m += 1.1 + Math.random() * 2.6;
        }
        nextAt += dur; barN++;
      }
      timer = setTimeout(schedule, 700);
    }
    function ramp(to, s) { if (!out) return; out.gain.cancelScheduledValues(ctx.currentTime); out.gain.setValueAtTime(out.gain.value, ctx.currentTime); out.gain.linearRampToValueAtTime(to, ctx.currentTime + s); }
    function start() {
      if (!ctx || nodes.length === 0) build();
      if (ctx.state === 'suspended') ctx.resume();
      on = true; barN = 0; nextAt = 0; ramp(vol * 1.1, 3); schedule(); startLayer();
    }
    function stop() {
      on = false; clearTimeout(timer); stopLayer(); if (!out) return; ramp(0, 2.5);
      const o = out, ns = nodes; setTimeout(() => { try { o.disconnect(); ns.forEach(n => n.disconnect()); } catch (e) {} }, 2800); out = null; master = null; bed = null; nodes = [];
    }
    return {
      toggle() { on ? stop() : start(); return on; }, get on() { return on; },
      get amb() { return amb; }, setAmb(k) { amb = k; store.set('salon-amb', k); if (on) { nextAt = 0; startLayer(); } },
      get vol() { return vol; }, setVol(v) { vol = v; store.set('salon-vol', String(v)); if (on) ramp(v * 1.1, .4); }
    };
  })();

  const btns = [...root.querySelectorAll('.music')], mbtn = root.querySelector('.mbtn'), panel = root.querySelector('.mpanel');
  function paint(on) {
    btns.forEach(b => { b.setAttribute('aria-pressed', on ? 'true' : 'false'); const a = b.querySelector('.on'), z = b.querySelector('.off'); if (a) { a.hidden = on; z.hidden = !on; } });
    if (mbtn) mbtn.classList.toggle('playing', on);
  }
  function play() { let on; try { on = Music.toggle(); } catch (e) { return; } paint(on); }
  btns.forEach(b => b.addEventListener('click', play));
  root.querySelectorAll('.amb').forEach(b => { b.setAttribute('aria-pressed', b.dataset.amb === Music.amb ? 'true' : 'false'); b.addEventListener('click', () => {
    Music.setAmb(b.dataset.amb); root.querySelectorAll('.amb').forEach(x => x.setAttribute('aria-pressed', x.dataset.amb === Music.amb ? 'true' : 'false'));
    if (!Music.on) play();
  }); });
  const range = root.querySelector('.vol input'); if (range) { range.value = Math.round(Music.vol * 100); range.addEventListener('input', () => Music.setVol(range.value / 100)); }
  function closePanel() { if (!panel || panel.hidden) return; panel.hidden = true; mbtn.setAttribute('aria-expanded', 'false'); }
  if (mbtn && panel) {
    mbtn.addEventListener('click', e => { e.stopPropagation(); panel.hidden = !panel.hidden; mbtn.setAttribute('aria-expanded', panel.hidden ? 'false' : 'true'); });
    document.addEventListener('click', e => { if (!e.target.closest('.mwrap')) closePanel(); });
  }

  /* ---------- the author's album, loaded only when asked ---------- */
  root.querySelectorAll('.album-open').forEach(b => b.addEventListener('click', () => {
    const box = b.closest('.album').querySelector('.album-frame'); if (!box) return;
    if (!box.firstChild) { const f = document.createElement('iframe'); f.src = b.dataset.src; f.title = "Chant et poésie de La'a"; f.loading = 'lazy'; f.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture'; f.style.cssText = 'width:100%;height:352px;border:0;border-radius:14px'; box.appendChild(f); }
    box.hidden = !box.hidden;
    if (!box.hidden && Music.on) play(); // one music at a time
  }));
})();
