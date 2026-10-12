/* Three.js pieces for the portfolio: the hero symbol and one scene per journal article.
   Also a small procedural nature sound engine (no audio files). Requires three r128 (global THREE). */
(function () {
  if (!window.THREE) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const dark = () => document.documentElement.getAttribute('data-theme') === 'dark' || (!document.documentElement.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
  const COBALT = 0x1c3fbf, GOLD = 0xb8933f, CHALK = 0xf6f2ea, INK = 0x1b1a17;

  function envMap(renderer) {
    // A small lit room rendered to a PMREM texture, so glass and gold have something to reflect.
    const scene = new THREE.Scene();
    const geo = new THREE.BoxGeometry(1, 1, 1);
    const add = (color, s, p, intensity) => { const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color })); m.scale.set(...s); m.position.set(...p); scene.add(m); };
    add(0xf7f2e8, [40, 40, 40], [0, 0, 0]); // the room, seen from inside thanks to BackSide below
    scene.children[0].material.side = THREE.BackSide;
    add(0xffffff, [6, 0.2, 6], [0, 14, 0]);
    add(0xdfe6ff, [0.2, 10, 10], [-16, 2, 0]);
    add(0xffe7b8, [0.2, 8, 8], [16, -2, 4]);
    add(0xffffff, [10, 0.2, 4], [0, -14, -6]);
    const pmrem = new THREE.PMREMGenerator(renderer); pmrem.compileEquirectangularShader();
    const tex = pmrem.fromScene(scene, 0.04).texture; pmrem.dispose(); return tex;
  }

  function makeRenderer(canvas) {
    const r = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
    r.setPixelRatio(Math.min(2, devicePixelRatio || 1)); r.outputEncoding = THREE.sRGBEncoding; r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.05;
    return r;
  }
  function fit(r, cam, el) { const w = el.clientWidth, h = el.clientHeight; if (!w || !h) return; r.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); }

  /* ---------- the symbol: a rose window of cobalt glass, a gold ring, a chalk heart ---------- */
  function hero(canvas) {
    const r = makeRenderer(canvas), scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
    cam.position.set(0, 0.4, 7.2); scene.environment = envMap(r);
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8899cc, 0.55));
    const key = new THREE.DirectionalLight(0xffffff, 1.1); key.position.set(4, 6, 5); scene.add(key);
    const warm = new THREE.PointLight(0xffd9a0, 1.2, 20); warm.position.set(-4, -2, 4); scene.add(warm);
    const group = new THREE.Group(); scene.add(group);
    const glass = new THREE.MeshPhysicalMaterial({ color: COBALT, metalness: 0, roughness: 0.12, transmission: 0.82, thickness: 0.6, ior: 1.45, transparent: true, opacity: 0.95, envMapIntensity: 1.4, side: THREE.DoubleSide, clearcoat: 0.6, clearcoatRoughness: 0.2 });
    const glass2 = glass.clone(); glass2.color = new THREE.Color(0x3b5fe0); glass2.transmission = 0.9;
    const gold = new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.22, envMapIntensity: 1.6 });
    const chalk = new THREE.MeshStandardMaterial({ color: CHALK, metalness: 0, roughness: 0.9 });
    // petal
    const shape = new THREE.Shape(); shape.moveTo(0, 0); shape.bezierCurveTo(0.42, 0.5, 0.42, 1.5, 0, 2.3); shape.bezierCurveTo(-0.42, 1.5, -0.42, 0.5, 0, 0);
    const petal = new THREE.ExtrudeGeometry(shape, { depth: 0.06, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 2, curveSegments: 24 });
    petal.translate(0, 0, -0.03);
    for (let ring = 0; ring < 2; ring++) {
      const n = ring === 0 ? 12 : 16, rad = ring === 0 ? 0.55 : 1.55, len = ring === 0 ? 1 : 0.78;
      for (let i = 0; i < n; i++) {
        const m = new THREE.Mesh(petal, ring === 0 ? glass : glass2); const a = (i / n) * Math.PI * 2 + (ring ? Math.PI / n : 0);
        m.scale.set(len, len, 1); m.position.set(Math.cos(a) * rad, Math.sin(a) * rad, ring ? -0.18 : 0); m.rotation.z = a - Math.PI / 2; m.rotation.x = ring ? 0.18 : -0.12;
        group.add(m);
      }
    }
    const ringGeo = new THREE.TorusGeometry(2.95, 0.045, 24, 160); group.add(new THREE.Mesh(ringGeo, gold));
    const ring2 = new THREE.Mesh(new THREE.TorusGeometry(1.52, 0.02, 16, 120), gold); ring2.position.z = -0.14; group.add(ring2);
    // the heart: chalk sphere with a gold point
    const heart = new THREE.Mesh(new THREE.SphereGeometry(0.34, 48, 48), chalk); group.add(heart);
    const dot = new THREE.Mesh(new THREE.SphereGeometry(0.1, 24, 24), gold); dot.position.z = 0.34; group.add(dot);
    // gold particles, slow
    const pts = new THREE.BufferGeometry(); const N = 180, arr = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) { const a = Math.random() * Math.PI * 2, rr = 3.3 + Math.random() * 1.6; arr[i * 3] = Math.cos(a) * rr; arr[i * 3 + 1] = Math.sin(a) * rr * 0.9; arr[i * 3 + 2] = (Math.random() - 0.5) * 2; }
    pts.setAttribute('position', new THREE.BufferAttribute(arr, 3));
    const dust = new THREE.Points(pts, new THREE.PointsMaterial({ color: GOLD, size: 0.035, transparent: true, opacity: 0.8 })); scene.add(dust);
    let px = 0, py = 0, tx = 0, ty = 0;
    addEventListener('pointermove', e => { tx = (e.clientX / innerWidth - 0.5); ty = (e.clientY / innerHeight - 0.5); }, { passive: true });
    const clock = new THREE.Clock();
    function frame() {
      const t = clock.getElapsedTime();
      px += (tx - px) * 0.04; py += (ty - py) * 0.04;
      group.rotation.z = reduce ? 0 : t * 0.06; group.rotation.y = px * 0.6; group.rotation.x = py * 0.4 - 0.05;
      group.scale.setScalar(1 + Math.sin(t * 0.7) * 0.012);
      dust.rotation.z = -t * 0.02;
      warm.position.x = Math.cos(t * 0.3) * 4; warm.position.y = Math.sin(t * 0.2) * 2;
      fit(r, cam, canvas); r.render(scene, cam);
      if (!reduce || t < 1) requestAnimationFrame(frame);
    }
    frame();
  }

  /* ---------- journal scenes ---------- */
  const scenes = {
    network(scene, group) { // constellation of nodes and links
      const N = 70, pos = []; const mat = new THREE.MeshStandardMaterial({ color: 0x1f4d3a, roughness: 0.5, metalness: 0.1 }); const gm = new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.3 });
      const geo = new THREE.SphereGeometry(0.06, 16, 16);
      for (let i = 0; i < N; i++) { const v = new THREE.Vector3().randomDirection().multiplyScalar(1.4 + Math.random() * 1.2); pos.push(v); const m = new THREE.Mesh(geo, i % 9 === 0 ? gm : mat); m.position.copy(v); m.scale.setScalar(i % 9 === 0 ? 1.8 : 1); group.add(m); }
      const lines = []; for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) if (pos[i].distanceTo(pos[j]) < 1.05) lines.push(pos[i].x, pos[i].y, pos[i].z, pos[j].x, pos[j].y, pos[j].z);
      const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(lines, 3)); group.add(new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: COBALT, transparent: true, opacity: 0.45 })));
      return t => { group.rotation.y = t * 0.12; group.rotation.x = Math.sin(t * 0.2) * 0.15; };
    },
    frames(scene, group) { // film frames drifting in a slow helix
      const gm = new THREE.MeshStandardMaterial({ color: 0x15181d, roughness: 0.35, metalness: 0.4 }); const em = new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.3 });
      const frames = [];
      for (let i = 0; i < 18; i++) { const f = new THREE.Group(); const a = i * 0.55; f.position.set(Math.cos(a) * 1.7, (i - 9) * 0.22, Math.sin(a) * 1.7); f.lookAt(0, f.position.y, 0);
        const b = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.56, 0.03), gm); f.add(b); const e = new THREE.Mesh(new THREE.BoxGeometry(0.82, 0.48, 0.035), new THREE.MeshStandardMaterial({ color: new THREE.Color().setHSL(0.08 + (i % 5) * 0.05, 0.4, 0.45), roughness: 0.7 })); f.add(e);
        for (let k = -3; k <= 3; k++) { const h = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.04, 0.04), em); h.position.set(k * 0.13, 0.26, 0.02); f.add(h); }
        group.add(f); frames.push(f); }
      return t => { group.rotation.y = -t * 0.1; frames.forEach((f, i) => { f.position.y = (i - 9) * 0.22 + Math.sin(t * 0.8 + i) * 0.04; }); };
    },
    blueprint(scene, group) { // a wireframe building and wifi rings
      const wm = new THREE.LineBasicMaterial({ color: COBALT, transparent: true, opacity: 0.7 });
      for (let fl = 0; fl < 3; fl++) { const g = new THREE.EdgesGeometry(new THREE.BoxGeometry(2.6, 0.7, 1.8)); const l = new THREE.LineSegments(g, wm); l.position.y = fl * 0.72 - 0.7; group.add(l); }
      const gm = new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.3 }); const rings = [];
      for (let i = 0; i < 4; i++) { const p = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 12), gm); p.position.set((i % 2 ? 0.8 : -0.8), (i < 2 ? 0 : 0.72) - 0.35, i % 3 ? 0.4 : -0.4); group.add(p);
        const rg = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.008, 8, 48), new THREE.MeshBasicMaterial({ color: GOLD, transparent: true, opacity: 0.6 })); rg.rotation.x = Math.PI / 2; rg.position.copy(p.position); group.add(rg); rings.push(rg); }
      return t => { group.rotation.y = 0.6 + Math.sin(t * 0.25) * 0.35; group.rotation.x = 0.35; rings.forEach((rg, i) => { const s = 1 + ((t * 0.6 + i * 0.4) % 1.6); rg.scale.setScalar(s); rg.material.opacity = Math.max(0, 0.7 - (s - 1) * 0.45); }); };
    },
    path(scene, group) { // a staircase of chalk steps rising, with a gold thread
      const cm = new THREE.MeshStandardMaterial({ color: CHALK, roughness: 0.95 }); const gm = new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.35 });
      const pts = [];
      for (let i = 0; i < 14; i++) { const a = i * 0.42; const s = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.08, 0.36), cm); s.position.set(Math.cos(a) * 1.5, i * 0.16 - 1.1, Math.sin(a) * 1.5); s.rotation.y = -a; group.add(s); pts.push(s.position.clone().add(new THREE.Vector3(0, 0.08, 0))); }
      const curve = new THREE.CatmullRomCurve3(pts); group.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 120, 0.012, 8, false), gm));
      const bead = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 16), gm); group.add(bead);
      return t => { group.rotation.y = -t * 0.15; const p = curve.getPointAt((t * 0.08) % 1); bead.position.copy(p); };
    },
    glass(scene, group) { // shards of cathedral glass in cobalt, gold and chalk
      const cols = [COBALT, 0x3b5fe0, GOLD, CHALK, 0x8a3a1f]; const shards = [];
      for (let i = 0; i < 42; i++) { const sh = new THREE.Shape(); const n = 3 + (i % 3); for (let k = 0; k < n; k++) { const a = (k / n) * Math.PI * 2, rr = 0.25 + Math.random() * 0.3; k ? sh.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : sh.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); }
        const m = new THREE.Mesh(new THREE.ShapeGeometry(sh), new THREE.MeshPhysicalMaterial({ color: cols[i % cols.length], transmission: 0.7, roughness: 0.2, thickness: 0.3, transparent: true, opacity: 0.9, side: THREE.DoubleSide }));
        const a = Math.random() * Math.PI * 2, rr = 0.5 + Math.random() * 1.9; m.position.set(Math.cos(a) * rr, Math.sin(a) * rr, (Math.random() - 0.5) * 0.8); m.rotation.z = Math.random() * 6; m.userData.s = 0.3 + Math.random(); group.add(m); shards.push(m); }
      group.add(new THREE.Mesh(new THREE.TorusGeometry(2.5, 0.03, 16, 120), new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.3 })));
      return t => { group.rotation.z = t * 0.05; group.rotation.y = Math.sin(t * 0.3) * 0.3; shards.forEach(m => { m.rotation.z += 0.002 * m.userData.s; }); };
    },
  };

  function journalScene(canvas, kind) {
    const r = makeRenderer(canvas), scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(36, 1, 0.1, 50);
    cam.position.set(0, 0.3, 6); scene.environment = envMap(r);
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8899cc, 0.6)); const key = new THREE.DirectionalLight(0xffffff, 1); key.position.set(3, 5, 4); scene.add(key);
    const group = new THREE.Group(); scene.add(group);
    const tick = (scenes[kind] || scenes.glass)(scene, group);
    let tx = 0, ty = 0, px = 0, py = 0; canvas.addEventListener('pointermove', e => { const b = canvas.getBoundingClientRect(); tx = (e.clientX - b.left) / b.width - 0.5; ty = (e.clientY - b.top) / b.height - 0.5; }, { passive: true });
    const clock = new THREE.Clock(); let visible = true;
    if ('IntersectionObserver' in window) new IntersectionObserver(es => es.forEach(e => visible = e.isIntersecting)).observe(canvas);
    function frame() { if (visible) { const t = clock.getElapsedTime(); px += (tx - px) * 0.05; py += (ty - py) * 0.05; tick(reduce ? 0 : t); scene.rotation.y = px * 0.5; scene.rotation.x = py * 0.3; fit(r, cam, canvas); r.render(scene, cam); } if (!reduce) requestAnimationFrame(frame); }
    frame();
  }

  /* ---------- nature sounds, synthesised ---------- */
  const Sound = (() => {
    let ctx, master, nodes = [], on = false, kind = 'forest';
    function noise(ctx) { const b = ctx.createBuffer(1, ctx.sampleRate * 4, ctx.sampleRate); const d = b.getChannelData(0); let last = 0; for (let i = 0; i < d.length; i++) { const w = Math.random() * 2 - 1; last = (last + 0.02 * w) / 1.02; d[i] = last * 3.5; } const s = ctx.createBufferSource(); s.buffer = b; s.loop = true; return s; }
    function build() {
      ctx = ctx || new (window.AudioContext || window.webkitAudioContext)(); master = ctx.createGain(); master.gain.value = 0; master.connect(ctx.destination); nodes = [];
      const t = ctx.currentTime;
      if (kind === 'rain' || kind === 'forest' || kind === 'wind') {
        const n = noise(ctx), f = ctx.createBiquadFilter(); f.type = kind === 'wind' ? 'lowpass' : 'bandpass'; f.frequency.value = kind === 'rain' ? 1800 : kind === 'wind' ? 420 : 900; f.Q.value = kind === 'rain' ? 0.5 : 0.8;
        const g = ctx.createGain(); g.gain.value = kind === 'rain' ? 0.5 : 0.35; n.connect(f); f.connect(g); g.connect(master); n.start(); nodes.push(n);
        const lfo = ctx.createOscillator(), lg = ctx.createGain(); lfo.frequency.value = kind === 'wind' ? 0.07 : 0.11; lg.gain.value = kind === 'wind' ? 0.22 : 0.08; lfo.connect(lg); lg.connect(g.gain); lfo.start(); nodes.push(lfo);
      }
      if (kind === 'ocean') {
        const n = noise(ctx), f = ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 600; const g = ctx.createGain(); g.gain.value = 0.25; n.connect(f); f.connect(g); g.connect(master); n.start(); nodes.push(n);
        const lfo = ctx.createOscillator(), lg = ctx.createGain(); lfo.frequency.value = 0.085; lg.gain.value = 0.2; lfo.connect(lg); lg.connect(g.gain); lfo.start(); nodes.push(lfo);
        const lfo2 = ctx.createOscillator(), lg2 = ctx.createGain(); lfo2.frequency.value = 0.21; lg2.gain.value = 300; lfo2.connect(lg2); lg2.connect(f.frequency); lfo2.start(); nodes.push(lfo2);
      }
      if (kind === 'forest') { // birds: short chirps at random moments
        const chirp = () => { if (!on) return; const o = ctx.createOscillator(), g = ctx.createGain(); const f0 = 1800 + Math.random() * 1800; o.frequency.setValueAtTime(f0, ctx.currentTime); o.frequency.exponentialRampToValueAtTime(f0 * (1.2 + Math.random() * 0.5), ctx.currentTime + 0.12); o.frequency.exponentialRampToValueAtTime(f0 * 0.9, ctx.currentTime + 0.25);
          g.gain.setValueAtTime(0, ctx.currentTime); g.gain.linearRampToValueAtTime(0.045, ctx.currentTime + 0.03); g.gain.exponentialRampToValueAtTime(0.0005, ctx.currentTime + 0.3); o.connect(g); g.connect(master); o.start(); o.stop(ctx.currentTime + 0.32); setTimeout(chirp, 600 + Math.random() * 2600); };
        setTimeout(chirp, 800);
      }
      master.gain.linearRampToValueAtTime(0.9, t + 2.5);
    }
    function stop() { if (!master) return; master.gain.cancelScheduledValues(ctx.currentTime); master.gain.linearRampToValueAtTime(0, ctx.currentTime + 1.2); const m = master, ns = nodes; setTimeout(() => { ns.forEach(n => { try { n.stop(); } catch (e) {} }); m.disconnect(); }, 1400); nodes = []; }
    return { toggle(k) { kind = k || kind; if (on) { stop(); on = false; return false; } on = true; build(); if (ctx.state === 'suspended') ctx.resume(); return true; }, isOn: () => on };
  })();

  /* ---------- wire up ---------- */
  const h = document.getElementById('hero-canvas'); if (h) try { hero(h); } catch (e) { h.hidden = true; }
  document.querySelectorAll('canvas[data-scene]').forEach(c => { try { journalScene(c, c.dataset.scene); } catch (e) { c.hidden = true; } });
  document.querySelectorAll('[data-sound]').forEach(b => b.addEventListener('click', () => { const on = Sound.toggle(b.dataset.sound); b.setAttribute('aria-pressed', on ? 'true' : 'false'); b.querySelector('span').textContent = on ? b.dataset.off : b.dataset.on; }));
})();
