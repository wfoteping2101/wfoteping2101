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
    /* ---------- art for the journal: one piece per article ---------- */
    plotter(scene, group, cam) { // the machine traces, I recognize: a pen draws the unfinished house, the transfers, the land plan, the stamp
      scene.background = new THREE.Color(0x0b1226); scene.fog = new THREE.Fog(0x0b1226, 7, 14);
      cam.position.set(0, 3.1, 4.4); cam.lookAt(0, -0.6, 0.1);
      const paper = new THREE.Mesh(new THREE.PlaneGeometry(5.2, 3.4), new THREE.MeshStandardMaterial({ color: new THREE.Color(0xb3a079).convertSRGBToLinear(), roughness: 1, envMapIntensity: 0.1 }));
      paper.rotation.x = -Math.PI / 2; paper.position.y = -0.6; group.add(paper);
      const shadow = new THREE.Mesh(new THREE.PlaneGeometry(5.4, 3.6), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35 }));
      shadow.rotation.x = -Math.PI / 2; shadow.position.set(0.08, -0.62, 0.1); group.add(shadow);
      const seg = [], col = []; let ink = [0.11, 0.25, 0.75]; const P = (x, z) => [x, -0.59, z];
      const line = (a, b) => { seg.push(...P(a[0], a[1]), ...P(b[0], b[1])); col.push(...ink, ...ink); };
      const rect = (x, z, w, h) => { line([x, z], [x + w, z]); line([x + w, z], [x + w, z + h]); line([x + w, z + h], [x, z + h]); line([x, z + h], [x, z]); };
      // the house, seen from the front, drawn flat on the paper (z grows toward the viewer)
      line([-2.3, 1.2], [-0.3, 1.2]);                    // ground
      rect(-2.15, 1.12, 1.7, 0.06);                      // ground slab
      [-2.05, -1.35, -0.62].forEach(x => { rect(x, 0.2, 0.08, 0.92); rect(x, -0.62, 0.08, 0.74); });
      rect(-2.15, 0.12, 1.7, 0.08);                      // first floor slab
      rect(-2.05, -0.68, 0.78, 0.06);                    // the one beam
      [-2.05, -1.35, -0.62].forEach(x => { for (let k = 0; k < 4; k++) line([x + 0.01 + k * 0.022, -0.62], [x - 0.03 + k * 0.035, -0.86 - (k % 2) * 0.05]); });
      for (let r = 0; r < 6; r++) for (let c = 0; c < 4; c++) if (r < 4 || (c + r) % 2) rect(-1.96 + c * 0.15 + (r % 2) * 0.07, 1.04 - r * 0.08, 0.13, 0.07);
      for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) if (r < 2 || c % 2) rect(-1.26 + c * 0.155, 1.04 - r * 0.08, 0.14, 0.07);
      ink = [0.72, 0.55, 0.22];
      // transfers arriving from the right edge into the empty upper room
      for (let k = 0; k < 3; k++) for (let d = 0; d < 14; d++) { const x0 = 0.25 - d * 0.1, z0 = -1.25 + k * 0.12 + d * 0.06; line([x0, z0], [x0 - 0.05, z0 + 0.03]); }
      ink = [0.16, 0.12, 0.09];
      // the land plan
      const gx = 0.45, gz = -1.3, cw = 0.42, ch = 0.36;
      for (let r = 0; r <= 7; r++) line([gx, gz + r * ch], [gx + 4 * cw, gz + r * ch]);
      for (let c = 0; c <= 4; c++) line([gx + c * cw, gz], [gx + c * cw, gz + 7 * ch]);
      for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) { const x = gx + (2 + j) * cw, z = gz + i * ch; line([x + 0.04, z + 0.04], [x + cw - 0.04, z + ch - 0.04]); line([x + cw - 0.04, z + 0.04], [x + 0.04, z + ch - 0.04]); }
      ink = [0.66, 0.26, 0.16];
      // the stamp
      const sc = [gx + 1.0, gz + 1.85], sr = 0.42; for (let a = 0; a < 48; a++) { const a0 = a / 48 * Math.PI * 2, a1 = (a + 1) / 48 * Math.PI * 2; line([sc[0] + Math.cos(a0) * sr, sc[1] + Math.sin(a0) * sr], [sc[0] + Math.cos(a1) * sr, sc[1] + Math.sin(a1) * sr]); line([sc[0] + Math.cos(a0) * sr * 0.8, sc[1] + Math.sin(a0) * sr * 0.8], [sc[0] + Math.cos(a1) * sr * 0.8, sc[1] + Math.sin(a1) * sr * 0.8]); }
      const n = seg.length / 6;
      const mat = new THREE.MeshBasicMaterial({ transparent: true, opacity: 1, toneMapped: false });
      const inkM = new THREE.InstancedMesh(new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2), mat, n);
      { const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3(), ps = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0), cc = new THREE.Color();
        for (let k = 0; k < n; k++) { const x0 = seg[k * 6], z0 = seg[k * 6 + 2], x1 = seg[k * 6 + 3], z1 = seg[k * 6 + 5], dx = x1 - x0, dz = z1 - z0;
          ps.set((x0 + x1) / 2, -0.588, (z0 + z1) / 2); q.setFromAxisAngle(up, -Math.atan2(dz, dx)); sc.set(Math.hypot(dx, dz) + 0.014, 1, 0.016);
          inkM.setMatrixAt(k, m4.compose(ps, q, sc)); inkM.setColorAt(k, cc.setRGB(col[k * 6], col[k * 6 + 1], col[k * 6 + 2]).convertSRGBToLinear()); } }
      group.add(inkM);
      const g = { setDrawRange: (a, b) => { inkM.count = b / 2; } };
      const pen = new THREE.Group(); const gold = new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.25 });
      const tip = new THREE.Mesh(new THREE.ConeGeometry(0.035, 0.16, 16), gold); tip.rotation.x = Math.PI; tip.position.y = 0.08; pen.add(tip);
      const body = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.9, 16), new THREE.MeshStandardMaterial({ color: 0x1b1a17, roughness: 0.4, metalness: 0.3 })); body.position.y = 0.6; pen.add(body);
      pen.rotation.z = -0.25; group.add(pen);
      group.rotation.y = -0.08;
      return t => {
        const cycle = n / 26 + 3, u = t % cycle, shown = Math.min(n, Math.floor(u * 26));
        g.setDrawRange(0, shown * 2); mat.opacity = u > cycle - 1.2 ? Math.max(0, (cycle - u) / 1.2) : 1;
        const i = Math.max(0, shown - 1) * 6; pen.position.set(seg[i + 3] || 0, -0.59 + (shown >= n ? 0.25 : 0.0), seg[i + 5] || 0);
      };
    },
    altitude(scene, group, cam) { // a gold thread climbs through four planes of glass above a field of lights
      scene.background = new THREE.Color(0x0e1220); scene.fog = new THREE.Fog(0x0e1220, 6, 15);
      cam.position.set(0, 0.6, 7.2);
      const pts = []; for (let i = 0; i < 2600; i++) { const a = Math.random() * Math.PI * 2, r = Math.sqrt(Math.random()) * 5; pts.push(Math.cos(a) * r, -1.9, Math.sin(a) * r); }
      const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
      group.add(new THREE.Points(pg, new THREE.PointsMaterial({ color: 0xe6c88a, size: 0.025, transparent: true, opacity: 0.8 })));
      const levels = [[-1.1, 1.0, 0x3b5fe0], [-0.2, 1.25, 0x1c3fbf], [0.7, 0.95, 0x2a4fd6], [1.6, 1.7, 0x6f86e8]];
      const discs = levels.map(([y, r, c]) => { const m = new THREE.Mesh(new THREE.CircleGeometry(r, 64), new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false }));
        m.rotation.x = -Math.PI / 2; m.position.y = y; group.add(m);
        const ring = new THREE.Mesh(new THREE.TorusGeometry(r, 0.008, 8, 96), new THREE.MeshBasicMaterial({ color: 0xe6c88a, transparent: true, opacity: 0.7 })); ring.rotation.x = Math.PI / 2; ring.position.y = y; group.add(ring); return m; });
      const hp = []; for (let i = 0; i <= 200; i++) { const s = i / 200, a = s * Math.PI * 7; hp.push(new THREE.Vector3(Math.cos(a) * (0.25 + s * 0.35), -1.9 + s * 4.0, Math.sin(a) * (0.25 + s * 0.35))); }
      const curve = new THREE.CatmullRomCurve3(hp);
      group.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 400, 0.012, 8, false), new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.3, emissive: 0x3a2a08 })));
      const bead = new THREE.Mesh(new THREE.SphereGeometry(0.07, 24, 24), new THREE.MeshStandardMaterial({ color: 0xffe2a0, emissive: 0xc9a45c, emissiveIntensity: 1.2 })); group.add(bead);
      const glow = new THREE.PointLight(0xffd58a, 1.4, 3); group.add(glow);
      return t => { group.rotation.y = t * 0.08; const s = (t * 0.06) % 1; const p = curve.getPointAt(s); bead.position.copy(p); glow.position.copy(p);
        cam.position.y = 0.4 + s * 0.8; cam.lookAt(0, 0.1 + p.y * 0.2, 0); discs.forEach((d, i) => { d.material.opacity = 0.14 + (Math.abs(p.y - levels[i][0]) < 0.3 ? 0.22 : 0); }); };
    },
    crack(scene, group, cam) { // a monument to prestige that cracks open, and the light that was behind it
      scene.background = new THREE.Color(0x0f0b08); scene.fog = new THREE.Fog(0x0f0b08, 8, 16);
      cam.position.set(0, 0.1, 8.6);
      const W = 1.3, H = 3.2, D = 0.7, cols = 4, rows = 9, P = [];
      for (let r = 0; r <= rows; r++) { P.push([]); for (let c = 0; c <= cols; c++) { const edge = r === 0 || r === rows || c === 0 || c === cols; P[r].push([-W / 2 + c * W / cols + (edge ? 0 : (Math.random() - 0.5) * 0.18), -H / 2 + r * H / rows + (edge ? 0 : (Math.random() - 0.5) * 0.2)]); } }
      const marble = new THREE.MeshStandardMaterial({ color: 0xd6cdbd, roughness: 0.7, metalness: 0.02, flatShading: true, envMapIntensity: 0.22 });
      const shards = [];
      const tri = (a, b, c) => { const sh = new THREE.Shape(); sh.moveTo(...a); sh.lineTo(...b); sh.lineTo(...c); sh.lineTo(...a);
        const geo = new THREE.ExtrudeGeometry(sh, { depth: D, bevelEnabled: false }); geo.translate(0, 0, -D / 2);
        const cx = (a[0] + b[0] + c[0]) / 3, cy = (a[1] + b[1] + c[1]) / 3; geo.translate(-cx, -cy, 0);
        const m = new THREE.Mesh(geo, marble); m.position.set(cx, cy, 0); m.userData = { home: new THREE.Vector3(cx, cy, 0), dir: new THREE.Vector3(cx * 1.6 + (Math.random() - 0.5) * 0.6, cy * 0.35 + (Math.random() - 0.5) * 0.4, (Math.random() - 0.2) * 1.2).normalize(), spin: new THREE.Vector3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5), k: 0.6 + Math.random() * 0.8 };
        group.add(m); shards.push(m); };
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) { const a = P[r][c], b = P[r][c + 1], cc = P[r + 1][c + 1], d = P[r + 1][c]; if ((r + c) % 2) { tri(a, b, cc); tri(a, cc, d); } else { tri(a, b, d); tri(b, cc, d); } }
      const plaque = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.16, 0.04), new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.25 })); plaque.position.set(0, 0.9, D / 2 + 0.03); group.add(plaque);
      const core = new THREE.Mesh(new THREE.BoxGeometry(W * 0.92, H * 0.95, D * 0.6), new THREE.MeshBasicMaterial({ color: 0xffa83a, toneMapped: false })); group.add(core);
      const gc = document.createElement('canvas'); gc.width = gc.height = 128; const gx = gc.getContext('2d'); const gr = gx.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,190,90,1)'); gr.addColorStop(0.35, 'rgba(255,150,50,.45)'); gr.addColorStop(1, 'rgba(255,120,30,0)'); gx.fillStyle = gr; gx.fillRect(0, 0, 128, 128);
      const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(gc), blending: THREE.AdditiveBlending, transparent: true, depthWrite: false, toneMapped: false })); halo.position.z = -0.5; group.add(halo);
      const rim = new THREE.DirectionalLight(0xffcf8a, 0.6); rim.position.set(-3, 2, -3); scene.add(rim);
      const light = new THREE.PointLight(0xffb84a, 0, 9); light.position.set(0, 0, 0.8); group.add(light);
      const base = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.18, 1.2), new THREE.MeshStandardMaterial({ color: 0x2a221a, roughness: 0.8 })); base.position.y = -H / 2 - 0.1; group.add(base);
      const ease = x => x < 0 ? 0 : x > 1 ? 1 : x * x * (3 - 2 * x);
      return t => { const u = t % 7; // 0-2 still, 2-2.6 tremor, 2.6-4.2 burst, 4.2-6.2 drift back, 6.2-7 rest
        const burst = u < 2.6 ? 0 : u < 4.2 ? ease((u - 2.6) / 1.6) : u < 6.2 ? 1 - ease((u - 4.2) / 2) : 0;
        const trem = u > 2 && u < 2.6 ? 0.012 : 0;
        shards.forEach(m => { const d = m.userData; m.position.copy(d.home).addScaledVector(d.dir, burst * 0.9 * d.k); m.position.x += (Math.random() - 0.5) * trem; m.rotation.set(d.spin.x * burst * 1.2, d.spin.y * burst * 1.2, d.spin.z * burst); });
        plaque.position.y = 0.9 - burst * 2.4; plaque.rotation.z = burst * 0.9; plaque.position.z = D / 2 + 0.03 + burst * 0.6;
        light.intensity = 0.4 + burst * 4.5 + (trem ? 1.2 : 0); core.scale.setScalar(0.9 + burst * 0.1); halo.scale.setScalar(1.2 + burst * 6.5 + (trem ? 0.8 : 0)); halo.material.opacity = 0.25 + burst * 0.75;
        group.rotation.y = Math.sin(t * 0.25) * 0.35; };
    },
    queue(scene, group, cam) { // the ticket queue: one ticket waits in red, and turns green when it is solved
      scene.background = new THREE.Color(0x0c1a14); scene.fog = new THREE.Fog(0x0c1a14, 5, 12);
      cam.position.set(1.6, 0.6, 8.6); cam.lookAt(0, 0, 0);
      const card = new THREE.MeshStandardMaterial({ color: 0xe6dfd1, roughness: 0.8, envMapIntensity: 0.3 }); const ink = new THREE.MeshBasicMaterial({ color: 0x1f4d3a });
      const cards = [];
      for (let i = 0; i < 11; i++) { const c = new THREE.Group(); const b = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.38, 0.04), card); c.add(b);
        for (let k = 0; k < 3; k++) { const l = new THREE.Mesh(new THREE.BoxGeometry(k ? 0.9 - k * 0.25 : 1.3, 0.035, 0.01), ink); l.position.set(-0.3 - (k ? 0.2 : 0), 0.1 - k * 0.09, 0.026); c.add(l); }
        const dot = new THREE.Mesh(new THREE.SphereGeometry(0.06, 20, 20), new THREE.MeshStandardMaterial({ color: 0x9aa59f, emissive: 0x000000, toneMapped: false })); dot.position.set(0.9, 0, 0.04); c.add(dot); c.userData.dot = dot;
        group.add(c); cards.push(c); }
      const N = 70, pos = []; for (let i = 0; i < N; i++) pos.push(new THREE.Vector3((Math.random() - 0.5) * 9, (Math.random() - 0.5) * 6, -3 - Math.random() * 3));
      const lp = []; for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) if (pos[i].distanceTo(pos[j]) < 1.4) lp.push(pos[i].x, pos[i].y, pos[i].z, pos[j].x, pos[j].y, pos[j].z);
      const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(lp, 3)); group.add(new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0x2e6b52, transparent: true, opacity: 0.45 })));
      const red = new THREE.Color(0xd2412c), green = new THREE.Color(0x2fbf71), grey = new THREE.Color(0x9aa59f);
      return t => { const sp = 0.32, gap = 0.46;
        cards.forEach((c, i) => { const y = 2.4 - (((i * gap) + t * sp) % (cards.length * gap)); c.position.set(Math.sin(y * 0.6) * 0.25, y, -Math.abs(y) * 0.35); c.rotation.y = -0.25 + y * 0.04;
          const hot = (Math.floor((i * gap + t * sp) / (cards.length * gap)) + i) % 4 === 0; const d = c.userData.dot.material;
          if (hot) { const c2 = y > -0.6 ? red : green; d.color.copy(c2); d.emissive.copy(c2).multiplyScalar(0.9); } else { d.color.copy(grey); d.emissive.setRGB(0, 0, 0); }
          c.children[0].material = card; });
        group.rotation.y = Math.sin(t * 0.2) * 0.15; };
    },
    pages(scene, group, cam) { // ten pages fan open: the quote that became a book
      scene.background = new THREE.Color(0x15181d); scene.fog = new THREE.Fog(0x15181d, 6, 13);
      cam.position.set(0.4, 1.6, 5.4); cam.lookAt(0, 0, 0);
      function tex(i) { const c = document.createElement('canvas'); c.width = 280; c.height = 380; const x = c.getContext('2d');
        x.fillStyle = '#f4efe3'; x.fillRect(0, 0, 280, 380); x.strokeStyle = 'rgba(28,63,191,.75)'; x.lineWidth = 2; x.fillStyle = 'rgba(28,63,191,.75)';
        x.fillRect(22, 24, 120, 8); x.fillRect(22, 40, 70, 5);
        if (i % 3 === 0) { x.strokeRect(22, 70, 236, 180); x.beginPath(); x.moveTo(120, 70); x.lineTo(120, 250); x.moveTo(22, 160); x.lineTo(258, 160); x.stroke(); [[70, 115], [190, 115], [70, 205], [190, 205]].forEach(([a, b]) => { x.beginPath(); x.arc(a, b, 34, 0, 7); x.globalAlpha = .35; x.stroke(); x.globalAlpha = 1; x.beginPath(); x.arc(a, b, 4, 0, 7); x.fill(); }); }
        else if (i % 3 === 1) { for (let r = 0; r < 9; r++) { x.fillRect(22, 74 + r * 22, 150, 4); x.fillRect(210, 74 + r * 22, 48, 4); } x.strokeRect(22, 290, 236, 60); }
        else { for (let u = 0; u < 7; u++) { x.strokeRect(60, 70 + u * 30, 160, 24); x.fillRect(70, 79 + u * 30, 20 + (u * 37) % 90, 6); } }
        x.strokeStyle = 'rgba(184,147,63,.9)'; x.beginPath(); x.moveTo(22, 362); x.lineTo(258, 362); x.stroke();
        const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding; t.anisotropy = 4; return t; }
      const pages = [];
      for (let i = 0; i < 10; i++) { const piv = new THREE.Group(); const m = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 2.04), new THREE.MeshStandardMaterial({ map: tex(i), roughness: 0.95, side: THREE.DoubleSide, envMapIntensity: 0.3 })); m.position.x = 0.75; piv.add(m); piv.position.z = i * 0.004; group.add(piv); pages.push(piv); }
      const cover = new THREE.Mesh(new THREE.BoxGeometry(1.56, 2.1, 0.03), new THREE.MeshStandardMaterial({ color: 0xf2c200, roughness: 0.5 })); cover.position.set(0.78, 0, -0.03); group.add(cover);
      group.rotation.x = -0.9; group.position.y = -0.2;
      return t => { const open = 0.5 - 0.5 * Math.cos(t * 0.45); pages.forEach((p, i) => { const k = (i + 1) / pages.length; p.rotation.y = -Math.PI * 0.94 * k * open * (0.6 + 0.4 * k); });
        group.rotation.z = Math.sin(t * 0.2) * 0.08; group.position.x = -0.6 + open * 0.6; };
    },
    braid(scene, group, cam) { // two languages braided into one thread
      scene.background = new THREE.Color(0x1c0f0a); scene.fog = new THREE.Fog(0x1c0f0a, 6, 13);
      cam.position.set(0, 0, 7.8);
      const mk = (phase, col, emi) => { const pts = []; for (let i = 0; i <= 260; i++) { const s = i / 260, y = -2.2 + s * 4.4, r = 0.55 * Math.sin(Math.PI * Math.min(1, s * 1.15)) + 0.02, a = s * Math.PI * 6 + phase; pts.push(new THREE.Vector3(Math.cos(a) * r, y, Math.sin(a) * r)); }
        return new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 520, 0.05, 14, false), new THREE.MeshStandardMaterial({ color: col, metalness: 0.35, roughness: 0.32, emissive: emi, envMapIntensity: 0.55 })); };
      group.add(mk(0, 0x2347d6, 0x0b1a6e), mk(Math.PI, 0xc9a45c, 0x3a2a08));
      const motes = []; for (let i = 0; i < 160; i++) motes.push((Math.random() - 0.5) * 6, (Math.random() - 0.5) * 5, (Math.random() - 0.5) * 3);
      const mg = new THREE.BufferGeometry(); mg.setAttribute('position', new THREE.Float32BufferAttribute(motes, 3));
      const pts = new THREE.Points(mg, new THREE.PointsMaterial({ color: 0xf1e7d3, size: 0.03, transparent: true, opacity: 0.6 })); scene.add(pts);
      group.rotation.z = 0.35;
      return t => { group.rotation.y = t * 0.35; pts.rotation.y = -t * 0.03; };
    },
    formats(scene, group, cam) { // one reel at the centre, fifteen formats around it, each fed by the same source
      scene.background = new THREE.Color(0x121210); scene.fog = new THREE.Fog(0x121210, 8, 15);
      cam.position.set(0, 1.5, 8.2); cam.lookAt(0, -0.1, 0);
      const R = [['1:1', 1, 1], ['4:5', 4, 5], ['9:16', 9, 16], ['16:9', 16, 9], ['1.91:1', 1.91, 1], ['2:3', 2, 3], ['3:1', 3, 1], ['1:1', 1, 1], ['4:5', 4, 5], ['9:16', 9, 16], ['16:9', 16, 9], ['4:3', 4, 3], ['2:1', 2, 1], ['3:4', 3, 4], ['5:4', 5, 4]];
      const pal = [['#EFE8DA', '#1C3FBF'], ['#1C3FBF', '#EFE8DA'], ['#C9A45C', '#121210'], ['#EFE8DA', '#8A3A1F'], ['#26261F', '#C9A45C']];
      const card = (i, w, h) => { const c = document.createElement('canvas'); c.width = w >= h ? 512 : Math.round(512 * w / h); c.height = h >= w ? 512 : Math.round(512 * h / w); const x = c.getContext('2d'), [bg, fg] = pal[i % pal.length], W = c.width, H = c.height;
        x.fillStyle = bg; x.fillRect(0, 0, W, H); x.fillStyle = fg; x.globalAlpha = 0.9; x.fillRect(W * 0.08, H * 0.08, W * 0.84, H * 0.5); x.globalAlpha = 1;
        x.fillStyle = bg; x.beginPath(); x.moveTo(W * 0.46, H * 0.25); x.lineTo(W * 0.46, H * 0.41); x.lineTo(W * 0.58, H * 0.33); x.fill();
        x.fillStyle = fg; x.globalAlpha = 0.75; x.fillRect(W * 0.08, H * 0.66, W * 0.62, Math.max(6, H * 0.04)); x.fillRect(W * 0.08, H * 0.74, W * 0.44, Math.max(6, H * 0.04)); x.globalAlpha = 1;
        x.font = `500 ${Math.round(Math.min(W, H) * 0.11)}px ui-monospace, Menlo, monospace`; x.fillText(R[i][0], W * 0.08, H * 0.92); const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding; return t; };
      const reel = new THREE.Group(); const gold = new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.28 });
      reel.add(new THREE.Mesh(new THREE.TorusGeometry(0.5, 0.05, 16, 64), gold)); reel.add(new THREE.Mesh(new THREE.CircleGeometry(0.12, 32), gold));
      for (let k = 0; k < 5; k++) { const a = k / 5 * Math.PI * 2, sp = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.05, 0.03), gold); sp.position.set(Math.cos(a) * 0.29, Math.sin(a) * 0.29, 0); sp.rotation.z = a; reel.add(sp); }
      group.add(reel);
      const dots = [], ends = []; const lp = [];
      R.forEach(([lab, w, h], i) => { const a = i / R.length * Math.PI * 2, sz = 0.92, cw = sz * Math.sqrt(w / h), ch = sz * Math.sqrt(h / w);
        const m = new THREE.Mesh(new THREE.PlaneGeometry(cw, ch), new THREE.MeshBasicMaterial({ map: card(i, w, h), side: THREE.DoubleSide, toneMapped: false }));
        m.position.set(Math.cos(a) * 3, Math.sin(i * 1.7) * 0.55, Math.sin(a) * 3); m.lookAt(0, m.position.y, 0); m.rotateY(Math.PI); group.add(m); ends.push(m.position.clone());
        lp.push(0, 0, 0, m.position.x, m.position.y, m.position.z);
        const d = new THREE.Mesh(new THREE.SphereGeometry(0.035, 12, 12), new THREE.MeshBasicMaterial({ color: 0xe6cb8e, toneMapped: false })); group.add(d); dots.push(d); });
      const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(lp, 3));
      group.add(new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: GOLD, transparent: true, opacity: 0.22 })));
      return t => { group.rotation.y = t * 0.11; reel.rotation.z = -t * 0.8; reel.lookAt(cam.position.x * 0, 0, 100); reel.rotation.z = -t * 0.8;
        dots.forEach((d, i) => { const u = (t * 0.35 + i / R.length) % 1; d.position.copy(ends[i]).multiplyScalar(u); d.scale.setScalar(u < 0.9 ? 1 : (1 - u) * 10); }); };
    },
    glass(scene, group, cam) { // a rose window: chalk stone, lead, glass that brightens as the light crosses it
      scene.background = new THREE.Color(0x070b1f); scene.fog = new THREE.Fog(0x070b1f, 9, 16);
      cam.position.set(0, 0, 8.6); cam.lookAt(0, 0, 0);
      const cols = [0x1c3fbf, 0x2f5be6, 0xc9a45c, 0x8a1f2a, 0x1c3fbf, 0x1f5a3a, 0x2f5be6, 0xe6cb8e];
      const panes = []; const lead = new THREE.LineBasicMaterial({ color: 0x0a0a0c });
      const pane = (shape, c, a, r) => { const g = new THREE.ShapeGeometry(shape, 24); const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: 0.94, toneMapped: false })); m.userData = { base: new THREE.Color(c).convertSRGBToLinear(), a, r }; group.add(m); panes.push(m);
        const e = new THREE.LineSegments(new THREE.EdgesGeometry(g), lead); e.position.z = 0.002; group.add(e); };
      const sector = (r0, r1, a0, a1) => { const s = new THREE.Shape(); s.moveTo(Math.cos(a0) * r0, Math.sin(a0) * r0); s.absarc(0, 0, r1, a0, a1, false); s.absarc(0, 0, r0, a1, a0, true); return s; };
      { const s = new THREE.Shape(); s.absarc(0, 0, 0.42, 0, Math.PI * 2, false); pane(s, 0xc9a45c, 0, 0); }
      [[0.5, 1.15, 8, 0.05], [1.22, 1.86, 16, 0.035], [1.93, 2.42, 24, 0.025]].forEach(([r0, r1, n, gap], ring) => { for (let k = 0; k < n; k++) { const a0 = k / n * Math.PI * 2 + gap, a1 = (k + 1) / n * Math.PI * 2 - gap; pane(sector(r0, r1, a0, a1), cols[(k + ring * 3) % cols.length], (a0 + a1) / 2, (r0 + r1) / 2); } });
      for (let k = 0; k < 8; k++) { const a = (k + 0.5) / 8 * Math.PI * 2, s = new THREE.Shape(); s.absarc(Math.cos(a) * 1.54, Math.sin(a) * 1.54, 0.17, 0, Math.PI * 2, false); pane(s, 0xe6cb8e, a, 1.54); panes[panes.length - 1].position.z = 0.004; }
      const stone = new THREE.MeshStandardMaterial({ color: 0xd9d2c3, roughness: 0.95 });
      group.add(new THREE.Mesh(new THREE.TorusGeometry(2.52, 0.11, 20, 160), stone)); group.add(new THREE.Mesh(new THREE.TorusGeometry(1.19, 0.035, 12, 120), stone)); group.add(new THREE.Mesh(new THREE.TorusGeometry(1.9, 0.03, 12, 140), stone));
      const gc = document.createElement('canvas'); gc.width = gc.height = 128; const gx = gc.getContext('2d'), gr = gx.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(120,150,255,.55)'); gr.addColorStop(0.5, 'rgba(60,90,220,.18)'); gr.addColorStop(1, 'rgba(20,30,90,0)'); gx.fillStyle = gr; gx.fillRect(0, 0, 128, 128);
      const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(gc), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, toneMapped: false })); halo.scale.setScalar(8.5); halo.position.z = -0.6; scene.add(halo);
      const N = 260, dp = new Float32Array(N * 3); for (let i = 0; i < N; i++) { dp[i * 3] = (Math.random() - 0.5) * 6; dp[i * 3 + 1] = (Math.random() - 0.5) * 6; dp[i * 3 + 2] = 0.4 + Math.random() * 2.2; }
      const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.BufferAttribute(dp, 3));
      const dust = new THREE.Points(dg, new THREE.PointsMaterial({ color: 0xf1e7d3, size: 0.025, transparent: true, opacity: 0.6, depthWrite: false })); scene.add(dust);
      return t => { const L = t * 0.32; group.rotation.y = Math.sin(t * 0.2) * 0.16; group.rotation.x = Math.sin(t * 0.13) * 0.06;
        panes.forEach(m => { const d = Math.max(0, Math.cos(m.userData.a - L)); const k = 0.55 + 1.1 * Math.pow(d, 3) * (0.6 + m.userData.r * 0.2); m.material.color.copy(m.userData.base).multiplyScalar(k); });
        for (let i = 0; i < N; i++) { dp[i * 3 + 1] += 0.0016 + (i % 5) * 0.0004; if (dp[i * 3 + 1] > 3) dp[i * 3 + 1] = -3; } dg.attributes.position.needsUpdate = true; };
    },
  };

  function journalScene(canvas, kind) {
    const r = makeRenderer(canvas), scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(36, 1, 0.1, 50);
    cam.position.set(0, 0.3, 6); scene.environment = envMap(r);
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8899cc, 0.6)); const key = new THREE.DirectionalLight(0xffffff, 1); key.position.set(3, 5, 4); scene.add(key);
    const group = new THREE.Group(); scene.add(group);
    const tick = (scenes[kind] || scenes.glass)(scene, group, cam);
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
