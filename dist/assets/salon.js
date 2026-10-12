/* The reading room: one chapter at a time, a remembered place, and a calm piece of music
   generated in the browser (no audio files). Starts only on a tap. */
(function () {
  const root = document.querySelector('.salon'); if (!root) return;
  const chaps = [...root.querySelectorAll('.chap')], toc = root.querySelector('.toc'), tocLinks = [...root.querySelectorAll('.toc nav a')];
  const now = root.querySelector('.now'), bar = root.querySelector('.progress i'), colophon = root.querySelector('.colophon');
  const book = root.dataset.book, KEY = 'salon-' + book;
  const fr = () => document.documentElement.getAttribute('lang') === 'fr' || document.documentElement.dataset.lang === 'fr';
  let cur = -1;

  function show(i, scroll) {
    i = Math.max(0, Math.min(chaps.length - 1, i)); if (i === cur && !scroll) return;
    chaps.forEach((c, k) => c.classList.toggle('on', k === i));
    tocLinks.forEach((a, k) => a.setAttribute('aria-current', k === i ? 'true' : 'false'));
    const c = chaps[i]; cur = i;
    const title = c.querySelector('h2').textContent, kick = c.querySelector('.kicker').textContent;
    now.textContent = kick + ' · ' + title;
    const prev = c.querySelector('.prev'), next = c.querySelector('.next');
    if (i > 0) { prev.hidden = false; prev.querySelector('span').textContent = chaps[i - 1].querySelector('h2').textContent; prev.href = '#' + chaps[i - 1].id; } else prev.hidden = true;
    if (i < chaps.length - 1) { next.hidden = false; next.querySelector('span').textContent = chaps[i + 1].querySelector('h2').textContent; next.href = '#' + chaps[i + 1].id; } else { next.hidden = true; }
    colophon.classList.toggle('on', i === chaps.length - 1);
    toc.classList.remove('open'); root.querySelector('.toc-btn').setAttribute('aria-expanded', 'false');
    try { localStorage.setItem(KEY, String(i)); } catch (e) {}
    if (scroll) { const y = root.querySelector('.reader-bar').getBoundingClientRect().bottom + scrollY - 8; const top = c.getBoundingClientRect().top + scrollY; scrollTo({ top: Math.max(top - 70, 0), behavior: 'smooth' }); }
    progress();
  }
  function fromHash() { const id = location.hash.slice(1); const k = chaps.findIndex(c => c.id === id); return k; }
  function progress() { const c = chaps[cur]; if (!c) return; const r = c.getBoundingClientRect(); const seen = Math.min(1, Math.max(0, (innerHeight - r.top) / r.height)); const total = (cur + seen) / chaps.length; bar.style.width = (total * 100).toFixed(1) + '%'; }
  addEventListener('scroll', progress, { passive: true });
  addEventListener('hashchange', () => { const k = fromHash(); if (k >= 0) show(k, true); });
  root.querySelector('.toc-btn').addEventListener('click', e => { const open = !toc.classList.contains('open'); toc.classList.toggle('open', open); e.currentTarget.setAttribute('aria-expanded', open ? 'true' : 'false'); });
  root.querySelectorAll('.size').forEach(b => b.addEventListener('click', () => { const s = parseFloat(getComputedStyle(root).getPropertyValue('--size')) || 19; const n = Math.max(15, Math.min(26, s + (b.dataset.size === '+' ? 1 : -1))); root.style.setProperty('--size', n + 'px'); try { localStorage.setItem('salon-size', n); } catch (e) {} }));
  try { const s = localStorage.getItem('salon-size'); if (s) root.style.setProperty('--size', s + 'px'); } catch (e) {}
  addEventListener('keydown', e => { if (e.target.closest('input,textarea')) return; if (e.key === 'ArrowRight') show(cur + 1, true); if (e.key === 'ArrowLeft') show(cur - 1, true); });

  let start = fromHash();
  if (start < 0) { try { const s = localStorage.getItem(KEY); if (s !== null) start = parseInt(s, 10); } catch (e) {} }
  show(start >= 0 ? start : 0, false);
  if (location.hash) setTimeout(() => show(cur, true), 60);

  /* ---------- the music: a slow piece for reading ---------- */
  const Music = (() => {
    let ctx, master, timer, on = false, nodes = [];
    const mood = root.dataset.music || 'clair';
    // Chords as semitone offsets from a root; a gentle cycle. "clair": lydian warmth; "braise": dorian embers.
    const PROG = mood === 'braise'
      ? { root: 110, chords: [[0, 3, 7, 10, 14], [-2, 2, 5, 9, 12], [3, 7, 10, 14, 17], [-4, 0, 3, 7, 10]], scale: [0, 2, 3, 5, 7, 10, 12, 14, 15, 17, 19], tempo: 11 }
      : { root: 146.83, chords: [[0, 4, 7, 11, 14], [5, 9, 12, 16, 19], [-3, 0, 4, 7, 11], [2, 5, 9, 12, 16]], scale: [0, 2, 4, 7, 9, 11, 12, 14, 16, 19, 21], tempo: 10 };
    const f = (semi) => PROG.root * Math.pow(2, semi / 12);
    function build() {
      ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
      master = ctx.createGain(); master.gain.value = 0;
      const comp = ctx.createDynamicsCompressor(); comp.threshold.value = -24; comp.ratio.value = 3;
      const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 2600; lp.Q.value = .4;
      // a simple space: two feedback delays
      const d1 = ctx.createDelay(2), d2 = ctx.createDelay(2), g1 = ctx.createGain(), g2 = ctx.createGain(), wet = ctx.createGain();
      d1.delayTime.value = .37; d2.delayTime.value = .61; g1.gain.value = .34; g2.gain.value = .28; wet.gain.value = .45;
      master.connect(lp); lp.connect(comp); comp.connect(ctx.destination);
      lp.connect(d1); d1.connect(g1); g1.connect(d1); g1.connect(wet);
      lp.connect(d2); d2.connect(g2); g2.connect(d2); g2.connect(wet);
      wet.connect(comp);
      nodes = [comp, lp, d1, d2, g1, g2, wet];
    }
    function pad(freq, t0, dur, vol) {
      const o1 = ctx.createOscillator(), o2 = ctx.createOscillator(), o3 = ctx.createOscillator(), g = ctx.createGain(), fl = ctx.createBiquadFilter();
      o1.type = 'sine'; o2.type = 'triangle'; o3.type = 'sine';
      o1.frequency.value = freq; o2.frequency.value = freq * 1.003; o3.frequency.value = freq * 0.5;
      fl.type = 'lowpass'; fl.frequency.value = 900; fl.Q.value = .3;
      const lfo = ctx.createOscillator(), lg = ctx.createGain(); lfo.frequency.value = .07 + Math.random() * .05; lg.gain.value = 180; lfo.connect(lg); lg.connect(fl.frequency);
      g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(vol, t0 + dur * .35); g.gain.setValueAtTime(vol, t0 + dur * .7); g.gain.linearRampToValueAtTime(0, t0 + dur);
      o1.connect(fl); o2.connect(fl); o3.connect(fl); fl.connect(g); g.connect(master);
      [o1, o2, o3, lfo].forEach(o => { o.start(t0); o.stop(t0 + dur + .1); });
    }
    function pluck(freq, t0, vol) { // kalimba-like: sine with a fast decay and a soft partial
      const o = ctx.createOscillator(), o2 = ctx.createOscillator(), g = ctx.createGain(), g2 = ctx.createGain();
      o.type = 'sine'; o.frequency.value = freq; o2.type = 'sine'; o2.frequency.value = freq * 2.01;
      g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(vol, t0 + .012); g.gain.exponentialRampToValueAtTime(.0005, t0 + 2.4);
      g2.gain.setValueAtTime(0, t0); g2.gain.linearRampToValueAtTime(vol * .25, t0 + .008); g2.gain.exponentialRampToValueAtTime(.0004, t0 + .7);
      o.connect(g); o2.connect(g2); g.connect(master); g2.connect(master);
      o.start(t0); o2.start(t0); o.stop(t0 + 2.6); o2.stop(t0 + .9);
    }
    let bar = 0, nextAt = 0;
    function schedule() {
      if (!on) return;
      const t = ctx.currentTime; if (nextAt === 0) nextAt = t + .1;
      while (nextAt < t + 1.5) {
        const chord = PROG.chords[bar % PROG.chords.length], dur = PROG.tempo;
        chord.forEach((semi, k) => pad(f(semi) * (k === 0 ? .5 : 1), nextAt + k * .25, dur + 3, k === 0 ? .055 : .035));
        // sparse melody over the chord
        let m = nextAt + 1.2 + Math.random();
        while (m < nextAt + dur - 1) {
          if (Math.random() < .8) { const s = PROG.scale[Math.floor(Math.random() * PROG.scale.length)]; pluck(f(s) * 2, m, .07 + Math.random() * .05); }
          m += 1.1 + Math.random() * 2.6;
        }
        nextAt += dur; bar++;
      }
      timer = setTimeout(schedule, 700);
    }
    function start() {
      if (!ctx) build(); else if (!master || nodes.length === 0) build();
      if (ctx.state === 'suspended') ctx.resume();
      on = true; bar = 0; nextAt = 0; master.gain.cancelScheduledValues(ctx.currentTime); master.gain.setValueAtTime(0, ctx.currentTime); master.gain.linearRampToValueAtTime(.9, ctx.currentTime + 3);
      schedule();
    }
    function stop() {
      on = false; clearTimeout(timer); if (!master) return; const m = master, ns = nodes; master.gain.cancelScheduledValues(ctx.currentTime); master.gain.setValueAtTime(master.gain.value, ctx.currentTime); master.gain.linearRampToValueAtTime(0, ctx.currentTime + 2.5);
      setTimeout(() => { try { m.disconnect(); ns.forEach(n => n.disconnect()); } catch (e) {} }, 2800); master = null; nodes = [];
    }
    return { toggle() { on ? stop() : start(); return on; }, get on() { return on; } };
  })();
  const btns = [...root.querySelectorAll('.music')];
  function paint(on) { btns.forEach(b => { b.setAttribute('aria-pressed', on ? 'true' : 'false'); const a = b.querySelector('.on'), z = b.querySelector('.off'); if (a) { a.hidden = on; z.hidden = !on; } }); }
  btns.forEach(b => b.addEventListener('click', () => { let on; try { on = Music.toggle(); } catch (e) { return; } paint(on); }));
  document.addEventListener('visibilitychange', () => { /* keep playing; the reader may switch tabs to take a note */ });
})();
