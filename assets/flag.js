/* The flag of Cameroon floating in the wind, drawn with three.js r128 (global THREE) on every canvas.flag3d.
   Green, red and yellow bands with the yellow star; the cloth ripples from the pole. Still when motion is reduced. */
(function () {
  function texture() {
    const c = document.createElement('canvas'); c.width = 768; c.height = 512; const g = c.getContext('2d');
    g.fillStyle = '#007A5E'; g.fillRect(0, 0, 256, 512);
    g.fillStyle = '#CE1126'; g.fillRect(256, 0, 256, 512);
    g.fillStyle = '#FCD116'; g.fillRect(512, 0, 256, 512);
    g.beginPath();
    for (let i = 0; i < 10; i++) {
      const r = i % 2 ? 34 : 88, a = -Math.PI / 2 + i * Math.PI / 5;
      g.lineTo(384 + r * Math.cos(a), 256 + r * Math.sin(a));
    }
    g.closePath(); g.fillStyle = '#FCD116'; g.fill();
    const t = new THREE.CanvasTexture(c); t.anisotropy = 4; return t;
  }
  function start(cv) {
    let R;
    try { R = new THREE.WebGLRenderer({ canvas: cv, alpha: true, antialias: true }); } catch (e) { return; }
    R.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    const scene = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(30, 1.5, .1, 50); cam.position.set(0.15, 0.05, 6.4);
    const W = 3, H = 2, geo = new THREE.PlaneGeometry(W, H, 48, 32);
    const mat = new THREE.MeshLambertMaterial({ map: texture(), side: THREE.DoubleSide });
    const flag = new THREE.Mesh(geo, mat);
    const group = new THREE.Group(); group.add(flag);
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 3.3, 16), new THREE.MeshLambertMaterial({ color: 0xd8d2c4 }));
    pole.position.set(-W / 2 - 0.04, -0.6, 0); group.add(pole);
    const knob = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), new THREE.MeshLambertMaterial({ color: 0xFCD116 }));
    knob.position.set(-W / 2 - 0.04, 1.08, 0); group.add(knob);
    group.rotation.y = -0.32; group.position.x = 0.15; scene.add(group);
    scene.add(new THREE.AmbientLight(0xffffff, 0.72));
    const sun = new THREE.DirectionalLight(0xffffff, 0.7); sun.position.set(2, 3, 4); scene.add(sun);
    const pos = geo.attributes.position, base = Float32Array.from(pos.array);
    const still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let visible = true, t0 = performance.now();
    function wave(time) {
      for (let i = 0; i < pos.count; i++) {
        const x = base[i * 3], y = base[i * 3 + 1], u = (x + W / 2) / W;
        const z = (Math.sin(x * 2.1 - time * 2.3 + y * 0.5) * 0.17 + Math.sin(x * 4.3 - time * 3.4) * 0.045) * u;
        pos.array[i * 3 + 1] = y - u * u * 0.05 + Math.sin(time * 1.3 + x) * 0.012 * u;
        pos.array[i * 3 + 2] = z;
      }
      pos.needsUpdate = true; geo.computeVertexNormals();
    }
    function size() {
      const w = cv.clientWidth || 300, h = cv.clientHeight || 190;
      R.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix();
    }
    size();
    if (window.ResizeObserver) new ResizeObserver(size).observe(cv);
    if (window.IntersectionObserver) new IntersectionObserver(es => { visible = es[0].isIntersecting; }).observe(cv);
    function frame(now) {
      if (visible) { wave(still ? 0.6 : (now - t0) / 1000); R.render(scene, cam); }
      if (!still) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  function init() { if (!window.THREE) return; document.querySelectorAll('canvas.flag3d').forEach(start); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
