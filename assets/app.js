/* Chalk and cobalt: site behaviour. No frameworks. */
(function () {
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };

  /* ---------- language (EN / FR) ---------- */
  const LANG_KEY = 'wf-lang';
  function applyLang(l) {
    document.documentElement.lang = l;
    $$('[data-fr]').forEach(el => {
      if (!el.dataset.en) el.dataset.en = el.innerHTML;
      el.innerHTML = l === 'fr' ? el.dataset.fr : el.dataset.en;
    });
    $$('[data-fr-ph]').forEach(el => { if (!el.dataset.enPh) el.dataset.enPh = el.placeholder; el.placeholder = l === 'fr' ? el.dataset.frPh : el.dataset.enPh; });
    $$('.lang').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === l ? 'true' : 'false'));
    store.set(LANG_KEY, l);
    dispatchEvent(new CustomEvent('wf-lang', { detail: l }));
  }
  $$('.lang').forEach(b => b.addEventListener('click', () => applyLang(b.dataset.lang)));
  applyLang(store.get(LANG_KEY) || 'en');

  /* ---------- theme ---------- */
  const THEME_KEY = 'wf-theme';
  function applyTheme(t) { if (t === 'system') document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme', t); store.set(THEME_KEY, t); const b = $('.theme'); if (b) b.textContent = t === 'dark' ? 'LIGHT' : t === 'light' ? 'AUTO' : 'DARK'; }
  const tb = $('.theme');
  if (tb) tb.addEventListener('click', () => { const cur = store.get(THEME_KEY) || 'system'; applyTheme(cur === 'system' ? 'dark' : cur === 'dark' ? 'light' : 'system'); });
  applyTheme(store.get(THEME_KEY) || 'system');

  /* ---------- nav ---------- */
  const burger = $('.burger'), nav = $('.nav');
  if (burger && nav) burger.addEventListener('click', () => { const o = nav.classList.toggle('open'); burger.setAttribute('aria-expanded', o ? 'true' : 'false'); });

  /* ---------- reveal ---------- */
  const rvs = $$('.rv');
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '20% 0px 10% 0px' });
    rvs.forEach(el => io.observe(el));
    let tick = false;
    const sweep = () => { tick = false; const lim = window.scrollY + window.innerHeight + 120; rvs.forEach(el => { if (!el.classList.contains('in') && el.getBoundingClientRect().top + window.scrollY < lim) el.classList.add('in'); }); };
    addEventListener('scroll', () => { if (!tick) { tick = true; requestAnimationFrame(sweep); } }, { passive: true });
    setTimeout(sweep, 300);
  } else rvs.forEach(el => el.classList.add('in'));

  /* ---------- the shelf: select a book to present it, select again to open ---------- */
  $$('.shelf').forEach(shelf => {
    const books = $$('.book', shelf), present = $('.present', shelf), rail = $('.shelf-rail', shelf);
    let cur = -1;
    function put(i) {
      books.forEach((b, j) => b.setAttribute('aria-pressed', i === j ? 'true' : 'false'));
      cur = i;
      if (!present) return;
      if (i < 0) { present.classList.remove('on'); return; }
      const b = books[i];
      $('.p-title', present).textContent = b.dataset.title;
      $('.p-kind', present).textContent = b.dataset.kind + ' · ' + b.dataset.year;
      $('.p-line', present).textContent = b.dataset.line;
      const img = $('.p-img', present); img.src = b.dataset.shot; img.alt = b.dataset.title + ', screenshot';
      const a = $('.p-open', present); a.href = b.dataset.href; const gd = $('.p-guide', present); if (gd) gd.href = b.dataset.href.replace('/work/', '/guides/');
      const l = $('.p-link', present); if (b.dataset.url) { l.href = b.dataset.url; l.textContent = b.dataset.linkLabel; l.hidden = false; } else { l.hidden = true; }
      present.classList.add('on');
      b.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'nearest', inline: 'center' });
    }
    books.forEach((b, i) => {
      b.addEventListener('click', () => { if (cur === i) location.href = b.dataset.href; else put(i); });
      b.addEventListener('keydown', e => { if (e.key === 'ArrowRight') { e.preventDefault(); put(Math.min(books.length - 1, i + 1)); books[Math.min(books.length - 1, i + 1)].focus(); } if (e.key === 'ArrowLeft') { e.preventDefault(); put(Math.max(0, i - 1)); books[Math.max(0, i - 1)].focus(); } if (e.key === 'Escape') put(-1); });
    });
    $$('.shelf-arrows button', shelf).forEach(btn => btn.addEventListener('click', () => { const d = btn.dataset.dir === 'next' ? 1 : -1; if (cur < 0) put(d > 0 ? 0 : books.length - 1); else put(Math.max(0, Math.min(books.length - 1, cur + d))); }));
    if (rail) rail.addEventListener('keydown', e => { if (e.key === 'Escape') put(-1); });
  });

  /* ---------- purpose motion ---------- */
  const SHAPES = {
    ring: 'M 300 170 m -110 0 a 110 110 0 1 0 220 0 a 110 110 0 1 0 -220 0',
    arc: 'M 120 280 Q 300 40 480 280',
    line: 'M 80 170 L 520 170',
    wave: 'M 60 180 C 140 90, 220 270, 300 180 S 460 90, 540 180',
    frame: 'M 150 70 H 450 V 270 H 150 Z',
    grid: 'M 150 70 H 450 M 150 170 H 450 M 150 270 H 450 M 150 70 V 270 M 300 70 V 270 M 450 70 V 270',
    dots: 'M 160 170 a 10 10 0 1 0 0.1 0 M 230 170 a 10 10 0 1 0 0.1 0 M 300 170 a 10 10 0 1 0 0.1 0 M 370 170 a 10 10 0 1 0 0.1 0 M 440 170 a 10 10 0 1 0 0.1 0',
    stack: 'M 180 100 H 420 M 180 140 H 420 M 180 180 H 420 M 180 220 H 420 M 180 260 H 420'
  };
  $$('.stage').forEach(stage => {
    let beats = [];
    try { beats = JSON.parse(stage.dataset.beats || '[]'); } catch (e) {}
    if (!beats.length) return;
    const svg = $('svg', stage), path = $('path', svg), line = $('.line', stage), bar = $('.bar', stage), play = $('.play-btn', stage);
    let i = -1, timer = null, running = !reduce, len = 0;
    function show(k) {
      i = k; const b = beats[k];
      path.setAttribute('d', SHAPES[b.s] || SHAPES.ring);
      len = path.getTotalLength();
      path.style.transition = 'none'; path.style.strokeDasharray = len; path.style.strokeDashoffset = len;
      line.classList.remove('on'); line.textContent = b.t;
      requestAnimationFrame(() => requestAnimationFrame(() => { path.style.transition = 'stroke-dashoffset 1.4s cubic-bezier(.2,.7,.2,1)'; path.style.strokeDashoffset = 0; line.classList.add('on'); }));
      bar.style.width = ((k + 1) / beats.length * 100) + '%';
      const m = $('.meta', stage); if (m) m.textContent = m.dataset.base + ' · ' + String(k + 1).padStart(2, '0') + ' / ' + String(beats.length).padStart(2, '0');
    }
    function step() { show((i + 1) % beats.length); if (running) timer = setTimeout(step, 3000); }
    if (play) play.addEventListener('click', () => { running = !running; play.textContent = running ? 'PAUSE' : 'PLAY'; if (running) step(); else clearTimeout(timer); });
    if (running) step(); else { show(0); if (play) play.textContent = 'PLAY'; }
    stage.addEventListener('click', e => { if (e.target.closest('.ctl')) return; clearTimeout(timer); show((i + 1) % beats.length); if (running) timer = setTimeout(step, 3000); });
  });

  /* ---------- walkthrough tour: real screens, camera moves, highlights ---------- */
  $$('.tour').forEach(tour => {
    let scenes = [];
    try { scenes = JSON.parse(tour.dataset.scenes || '[]'); } catch (e) {}
    if (!scenes.length) return;
    const img = $('.tour-img', tour), rect = $('.tour-hl rect', tour), k = $('.k', tour), tt = $('.t', tour), c = $('.c', tour), n = $('.tour-n', tour), dots = $('.dots', tour), play = $('.t-play', tour), cap = $('.tour-cap', tour);
    let i = -1, timer = null, running = !reduce;
    scenes.forEach((s, j) => { const d = document.createElement('button'); d.type = 'button'; d.setAttribute('role', 'tab'); d.setAttribute('aria-label', 'Scene ' + (j + 1)); d.addEventListener('click', () => { go(j); restart(); }); dots.appendChild(d); });
    function go(j) {
      i = j; const s0 = scenes[j]; const s = (document.documentElement.lang === 'fr' && s0.fr) ? Object.assign({}, s0, s0.fr) : s0; const [x, y, w, h] = s.f;
      const scale = Math.min(2.2, Math.max(1, Math.min(100 / w, 100 / h) * 0.92));
      const lim = (scale - 1) * 50 / scale; const cx = x + w / 2, cy = y + h / 2; const tx = Math.max(-lim, Math.min(lim, 50 - cx)), ty = Math.max(-lim, Math.min(lim, 50 - cy));
      if (img.getAttribute('src') !== s.img) { img.style.transition = 'none'; img.style.opacity = 0; img.src = s.img; requestAnimationFrame(() => { img.style.transition = reduce ? 'none' : 'opacity .5s, transform 5s cubic-bezier(.2,.7,.2,1)'; img.style.opacity = 1; img.style.transform = `scale(${scale}) translate(${tx}%, ${ty}%)`; }); }
      else { img.style.transition = reduce ? 'none' : 'transform 5s cubic-bezier(.2,.7,.2,1)'; img.style.transform = `scale(${scale}) translate(${tx}%, ${ty}%)`; }
      rect.setAttribute('x', x); rect.setAttribute('y', y); rect.setAttribute('width', w); rect.setAttribute('height', h);
      rect.style.transition = 'none'; rect.style.strokeDasharray = '400'; rect.style.strokeDashoffset = '400'; rect.style.opacity = (w >= 95 && h >= 95) ? 0 : 1;
      requestAnimationFrame(() => requestAnimationFrame(() => { rect.style.transition = reduce ? 'none' : 'stroke-dashoffset 1.6s ease'; rect.style.strokeDashoffset = '0'; }));
      cap.classList.remove('on'); k.textContent = s.k; tt.textContent = s.t; c.textContent = s.c; requestAnimationFrame(() => requestAnimationFrame(() => cap.classList.add('on')));
      n.textContent = String(j + 1).padStart(2, '0') + ' / ' + String(scenes.length).padStart(2, '0');
      $$('button', dots).forEach((d, q) => d.setAttribute('aria-selected', q === j ? 'true' : 'false'));
    }
    function step() { go((i + 1) % scenes.length); if (running) timer = setTimeout(step, 5200); }
    function restart() { clearTimeout(timer); if (running) timer = setTimeout(step, 5200); }
    $('.t-prev', tour).addEventListener('click', () => { go((i - 1 + scenes.length) % scenes.length); restart(); });
    $('.t-next', tour).addEventListener('click', () => { go((i + 1) % scenes.length); restart(); });
    play.addEventListener('click', () => { running = !running; play.textContent = running ? 'PAUSE' : 'PLAY'; if (running) restart(); else clearTimeout(timer); });
    tour.addEventListener('keydown', e => { if (e.key === 'ArrowRight') { go((i + 1) % scenes.length); restart(); } if (e.key === 'ArrowLeft') { go((i - 1 + scenes.length) % scenes.length); restart(); } if (e.key === ' ') { e.preventDefault(); play.click(); } });
    if ('IntersectionObserver' in window) { const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting && i < 0) { step(); io.disconnect(); } })); io.observe(tour); } else step();
    if (!running) { go(0); play.textContent = 'PLAY'; }
    addEventListener('wf-lang', () => { if (i >= 0) { const keep = i; i = -1; go(keep); } });
  });

  /* ---------- gallery players ---------- */
  $$('.vcard').forEach(card => {
    const media = $('.media', card), playBtn = $('.play', card), vars = $$('.vars button', card);
    let src = card.dataset.src, ratio = card.dataset.ratio || '16:9', video = null;
    function setRatio(r) { media.classList.toggle('tall', r === '9:16'); }
    function start() {
      if (!video) { video = document.createElement('video'); video.controls = true; video.playsInline = true; video.setAttribute('controlslist', 'nodownload'); video.disablePictureInPicture = true; video.oncontextmenu = e => e.preventDefault(); video.preload = 'metadata'; video.poster = card.dataset.poster || ''; media.innerHTML = ''; media.appendChild(video); }
      video.src = src; setRatio(ratio); video.play().catch(() => {});
    }
    setRatio(ratio);
    if (playBtn) playBtn.addEventListener('click', start);
    vars.forEach(b => b.addEventListener('click', () => { vars.forEach(x => x.setAttribute('aria-pressed', 'false')); b.setAttribute('aria-pressed', 'true'); src = b.dataset.src; ratio = b.dataset.ratio; if (video) start(); else setRatio(ratio); }));
  });

  /* ---------- services: reserve and pay ---------- */
  const CONTACT = document.body.dataset.email || '';
  async function checkout(item, email, ref, btn) {
    const old = btn.textContent; btn.disabled = true; btn.textContent = 'One moment';
    try {
      const r = await fetch('/api/checkout', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ item, email, ref }) });
      const j = await r.json().catch(() => ({}));
      if (r.ok && j.url) { location.href = j.url; return; }
      if (r.status === 503) { fallback(item, email, ref, 'Card payment is being switched on. Your request has been prepared as an email instead; send it and I will reply with a payment link.'); }
      else fallback(item, email, ref, 'The payment page could not be opened. Your request has been prepared as an email instead.');
    } catch (e) { fallback(item, email, ref, 'The payment page could not be reached. Your request has been prepared as an email instead.'); }
    btn.disabled = false; btn.textContent = old;
  }
  function fallback(item, email, ref, msg) {
    const n = $('#pay-notice'); if (n) { n.textContent = msg; n.hidden = false; }
    const subject = encodeURIComponent('Reservation: ' + item + (ref ? ' (' + ref + ')' : ''));
    const body = encodeURIComponent('Hello William,\n\nI would like to reserve: ' + item + '\nReference: ' + (ref || 'none') + '\nMy email: ' + (email || '') + '\n\nPlease send me the payment link.\n');
    location.href = 'mailto:' + CONTACT + '?subject=' + subject + '&body=' + body;
  }
  $$('[data-pay]').forEach(btn => btn.addEventListener('click', () => {
    const email = ($('#b-email') || {}).value || '';
    const ref = store.get('wf-brief-ref') || '';
    checkout(btn.dataset.pay, email, ref, btn);
  }));

  /* ---------- brief and booking form ---------- */
  const form = $('form.brief');
  if (form) {
    const out = $('.summary', form);
    function val(n) { const el = form.elements[n]; if (!el) return ''; if (el.length && el[0] && el[0].type === 'radio') { const c = Array.from(el).find(x => x.checked); return c ? c.value : ''; } return (el.value || '').trim(); }
    function build() {
      const ref = 'WF-' + new Date().toISOString().slice(2, 10).replace(/-/g, '') + '-' + Math.random().toString(36).slice(2, 6).toUpperCase();
      store.set('wf-brief-ref', ref);
      const lines = [
        'BRIEF ' + ref,
        'Name: ' + val('name'), 'Email: ' + val('email'), 'Company: ' + val('company'),
        'Service: ' + val('service'), 'Language: ' + val('lang'),
        '', 'What you want:', val('want'), '', 'Goal:', val('goal'), '', 'Audience:', val('audience'), '', 'What exists today:', val('existing'), '', 'References:', val('refs'),
        '', 'Budget range: ' + val('budget'), 'Deadline: ' + val('deadline'),
        '', 'MEETING', 'Platform: ' + val('platform'), 'Timezone: ' + val('tz'),
        'Slot 1: ' + val('slot1'), 'Slot 2: ' + val('slot2'), 'Slot 3: ' + val('slot3'),
      ];
      return { ref, text: lines.join('\n') };
    }
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const { ref, text } = build();
      out.textContent = text; out.classList.add('on');
      const bEmail = $('#b-email'); if (bEmail) bEmail.value = val('email');
      const subject = encodeURIComponent('Brief ' + ref + ', ' + val('service') + ', ' + val('name'));
      window.open('mailto:' + CONTACT + '?subject=' + subject + '&body=' + encodeURIComponent(text), '_self');
      const n = $('#brief-notice'); if (n) { n.hidden = false; }
      $('#after-brief').hidden = false;
      $('#after-brief').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    });
    const copy = $('#copy-brief');
    if (copy) copy.addEventListener('click', async () => { try { await navigator.clipboard.writeText(out.textContent); copy.textContent = 'Copied'; } catch (e) { const r = document.createRange(); r.selectNodeContents(out); const s = getSelection(); s.removeAllRanges(); s.addRange(r); copy.textContent = 'Selected, press copy'; } });
  }

  /* ---------- thanks page: show session id ---------- */
  const sid = new URLSearchParams(location.search).get('session_id');
  const sEl = $('#session'); if (sEl && sid) { sEl.textContent = sid; sEl.parentElement.hidden = false; }
})();
