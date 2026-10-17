/* Python in the page. Every Python example of a book becomes a small editor that runs in the browser
   (Pyodide, loaded on the first run only), and a free workshop opens from any [data-atelier] button or
   mounts inline in [data-atelier-inline]. Each example runs on its own; a program stops by itself after
   ten seconds; input() opens a small dialog; matplotlib figures appear under the code. French interface. */
(function () {
  const BASE = window.PYIDE_BASE || 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };

  /* ---------- the Python runtime, loaded once on demand ---------- */
  const PRELUDE = `
import sys, time, traceback, builtins, os, io, base64
os.environ['MPLBACKEND'] = 'Agg'
from js import window
def _entree(invite=''):
    invite = str(invite)
    sys.stdout.write(invite)
    r = window.prompt(invite if invite.strip() else 'Votre saisie :')
    r = '' if r is None else str(r)
    sys.stdout.write(r + '\\n')
    return r
builtins.input = _entree
_LIMITE = 10.0
def _executer(code):
    g = {'__name__': '__main__', '__builtins__': builtins}
    debut = time.time()
    n = [0]
    def trace(frame, event, arg):
        n[0] += 1
        if n[0] & 1023 == 0 and time.time() - debut > _LIMITE:
            raise TimeoutError("arrêt automatique au bout de 10 secondes (boucle infinie ?)")
        return trace
    plt = None
    if 'matplotlib' in code:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.close('all')
        plt.show = lambda *a, **k: None
    sys.settrace(trace)
    try:
        exec(compile(code, '<programme>', 'exec'), g)
    except SystemExit:
        pass
    except BaseException:
        t, e, tb = sys.exc_info()
        sys.settrace(None)
        te = traceback.TracebackException(t, e, tb.tb_next if tb else None)
        te.stack = traceback.StackSummary.from_list([f for f in te.stack if f.filename != '<exec>'])
        sys.stderr.write(''.join(te.format()))
    finally:
        sys.settrace(None)
        sys.stdout.flush()
        sys.stderr.flush()
    images = []
    if plt is not None:
        for num in plt.get_fignums():
            f = plt.figure(num)
            b = io.BytesIO()
            f.savefig(b, format='png', dpi=110, bbox_inches='tight')
            images.append(base64.b64encode(b.getvalue()).decode())
        plt.close('all')
    return images
`;
  let pyP = null, ready = false;
  function loadPy() {
    if (pyP) return pyP;
    pyP = new Promise((resolve, reject) => {
      const go = async () => {
        try { const py = await window.loadPyodide({ indexURL: BASE }); await py.runPythonAsync(PRELUDE); ready = true; resolve(py); }
        catch (e) { reject(e); }
      };
      if (window.loadPyodide) return go();
      const s = document.createElement('script'); s.src = BASE + 'pyodide.js'; s.onload = go; s.onerror = () => reject(new Error('load'));
      document.head.appendChild(s);
    });
    pyP.catch(() => { pyP = null; });
    return pyP;
  }

  const HINTS = [
    ['TimeoutError', 'Le programme a été arrêté au bout de dix secondes. Vérifiez la condition de votre boucle : devient-elle fausse un jour ?'],
    ['IndentationError', 'Le décalage des lignes (l’indentation) n’est pas cohérent. Les lignes d’un même bloc doivent commencer au même endroit.'],
    ['SyntaxError', 'La phrase Python est mal formée : une parenthèse, un guillemet ou un deux-points manque peut-être. Regardez la ligne indiquée et celle d’avant.'],
    ['NameError', 'Un nom est utilisé avant d’avoir été défini, ou il est mal orthographié (majuscules comprises).'],
    ['ZeroDivisionError', 'Une division par zéro a été demandée.'],
    ['TypeError', 'Une opération mélange des types incompatibles, par exemple un texte et un nombre. Une conversion avec int(), float() ou str() manque peut-être.'],
    ['ValueError', 'La valeur n’a pas la forme attendue, par exemple int("abc").'],
    ['IndexError', 'L’indice demandé n’existe pas : une liste de 3 éléments a les indices 0, 1 et 2.'],
    ['KeyError', 'Cette clé n’existe pas dans le dictionnaire. Vérifiez l’orthographe, ou utilisez .get().'],
    ['AttributeError', 'Cet objet n’a pas cet attribut ou cette méthode. Vérifiez le nom et le type de l’objet.'],
    ['FileNotFoundError', 'Le fichier n’existe pas encore ici : un programme doit d’abord l’écrire avant de le lire.'],
    ['ModuleNotFoundError', 'Ce module n’est pas disponible dans l’atelier du navigateur.'],
  ];

  async function run(code, ui) {
    const out = ui.out, plots = ui.plots, hint = ui.hint;
    ui.box.hidden = false; out.textContent = ''; plots.innerHTML = ''; hint.hidden = true; hint.textContent = '';
    const write = (s, cls) => { const sp = el('span', cls || '', s); out.appendChild(sp); };
    ui.btn.disabled = true; ui.btn.classList.add('busy');
    try {
      if (!ready) write('Chargement de Python dans votre navigateur (la première fois seulement)…\n', 'muted');
      let py;
      try { py = await loadPy(); } catch (e) { out.textContent = ''; write('Python n’a pas pu être chargé. Vérifiez votre connexion Internet, puis réessayez.\n', 'err'); return; }
      if (/\b(import|from)\s+matplotlib/.test(code)) write('Préparation des graphiques (matplotlib), quelques secondes la première fois…\n', 'muted');
      try { await py.loadPackagesFromImports(code, { messageCallback: () => {}, errorCallback: () => {} }); } catch (e) {}
      out.textContent = '';
      await new Promise(r => setTimeout(r, 20));
      py.setStdout({ batched: s => write(s + '\n') });
      py.setStderr({ batched: s => write(s + '\n', 'err') });
      const fn = py.globals.get('_executer');
      let imgs = [];
      try { const r = fn(code); imgs = r.toJs(); r.destroy(); }
      catch (e) { write(String(e && e.message || e) + '\n', 'err'); }
      finally { fn.destroy(); }
      imgs.forEach(b64 => { const im = new Image(); im.src = 'data:image/png;base64,' + b64; im.alt = 'Graphique produit par le programme'; plots.appendChild(im); });
      if (!out.textContent && !imgs.length) write('(Le programme s’est exécuté sans rien afficher.)\n', 'muted');
      const errs = [...out.querySelectorAll('.err')].map(n => n.textContent).join('');
      const h = HINTS.find(([k]) => errs.includes(k));
      if (h) { hint.hidden = false; hint.innerHTML = ''; hint.append(el('b', '', 'Indice : '), document.createTextNode(h[1])); }
    } finally { ui.btn.disabled = false; ui.btn.classList.remove('busy'); }
  }

  /* ---------- a light editor: a textarea over a highlighted copy of the code ---------- */
  const TOK = /([rbfuRBFU]{0,2}"""[\s\S]*?(?:"""|$)|[rbfuRBFU]{0,2}'''[\s\S]*?(?:'''|$)|[rbfuRBFU]{0,2}"(?:\\.|[^"\\\n])*"?|[rbfuRBFU]{0,2}'(?:\\.|[^'\\\n])*'?)|(#[^\n]*)|\b(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\b|\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b|\b(print|input|len|range|int|float|str|list|dict|tuple|set|sum|min|max|abs|round|sorted|enumerate|zip|type|open|isinstance|super|map|filter|any|all|bool|reversed|format)(?=\s*\()|([A-Za-z_À-ſ][\wÀ-ſ]*)/g;
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  function highlight(src) {
    let html = '', last = 0, prev = '', m;
    TOK.lastIndex = 0;
    while ((m = TOK.exec(src))) {
      html += esc(src.slice(last, m.index));
      const [tok, s, c, n, k, b, id] = m;
      if (s) html += '<i class="s">' + esc(tok) + '</i>';
      else if (c) html += '<i class="c">' + esc(tok) + '</i>';
      else if (n) html += '<i class="n">' + tok + '</i>';
      else if (k) html += '<i class="k">' + tok + '</i>';
      else if (b) html += '<i class="b">' + tok + '</i>';
      else html += (prev === 'def' || prev === 'class') ? '<i class="f">' + esc(tok) + '</i>' : esc(tok);
      prev = k || '';
      last = m.index + tok.length;
      if (tok.length === 0) TOK.lastIndex++;
    }
    return html + esc(src.slice(last));
  }

  function editor(initial, onRun, big) {
    const wrap = el('div', 'pyed' + (big ? ' big' : ''));
    const pre = el('pre', 'hl'); pre.setAttribute('aria-hidden', 'true'); const code = el('code'); pre.appendChild(code);
    const ta = el('textarea', 'ta');
    ta.spellcheck = false; ta.setAttribute('autocapitalize', 'off'); ta.setAttribute('autocomplete', 'off'); ta.setAttribute('autocorrect', 'off');
    ta.setAttribute('aria-label', 'Code Python modifiable'); ta.value = initial;
    wrap.append(pre, ta);
    const sync = () => {
      code.innerHTML = highlight(ta.value) + '\n';
      if (!big) { ta.style.height = 'auto'; ta.style.height = Math.max(ta.scrollHeight, 44) + 'px'; }
    };
    const insert = (txt) => {
      ta.focus();
      if (!document.execCommand || !document.execCommand('insertText', false, txt)) {
        const a = ta.selectionStart, b = ta.selectionEnd; ta.setRangeText(txt, a, b, 'end');
      }
      sync();
    };
    ta.addEventListener('input', sync);
    ta.addEventListener('scroll', () => { pre.scrollTop = ta.scrollTop; pre.scrollLeft = ta.scrollLeft; });
    ta.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); onRun(); return; }
      if (e.key === 'Tab' && !e.shiftKey) { e.preventDefault(); insert('    '); return; }
      if (e.key === 'Tab' && e.shiftKey) {
        e.preventDefault(); const v = ta.value, a = ta.selectionStart, ls = v.lastIndexOf('\n', a - 1) + 1, line = v.slice(ls);
        const k = Math.min(4, (line.match(/^ */) || [''])[0].length); if (k) { ta.setRangeText('', ls, ls + k, 'end'); sync(); } return;
      }
      if (e.key === 'Enter' && !e.shiftKey) {
        const v = ta.value, a = ta.selectionStart, ls = v.lastIndexOf('\n', a - 1) + 1, line = v.slice(ls, a);
        let ind = (line.match(/^ */) || [''])[0];
        if (/:\s*(#.*)?$/.test(line)) ind += '    ';
        e.preventDefault(); insert('\n' + ind);
      }
    });
    requestAnimationFrame(sync);
    return { wrap, ta, get: () => ta.value, set: (v) => { ta.value = v; sync(); }, sync };
  }

  function outputBox() {
    const box = el('div', 'pyout'); box.hidden = true;
    const out = el('pre', 'pyout-text'); const plots = el('div', 'pyout-plots'); const hint = el('p', 'pyout-hint'); hint.hidden = true;
    box.append(el('span', 'pyout-label', 'Sortie'), out, plots, hint);
    return { box, out, plots, hint };
  }

  /* ---------- the free workshop ---------- */
  const EXAMPLES = [
    ['Bonjour', 'nom = "Aïcha"\nville = "Douala"\nprint(f"Bonjour {nom}, bienvenue à l\'atelier depuis {ville} !")\n'],
    ['Euros en francs CFA', '# 1 euro = 655,957 francs CFA (parité fixe)\nTAUX = 655.957\nfor euros in [10, 50, 100, 250]:\n    fcfa = round(euros * TAUX)\n    print(f"{euros:>4} € = {fcfa:,} FCFA".replace(",", " "))\n'],
    ['Moyenne avec coefficients', 'notes = {"Maths": (14, 4), "Français": (11, 3), "Histoire": (13, 2), "Anglais": (16, 2)}\ntotal = sum(n * c for n, c in notes.values())\ncoefs = sum(c for _, c in notes.values())\nmoyenne = total / coefs\nprint(f"Moyenne : {moyenne:.2f} / 20")\n'],
    ['Graphique', 'import matplotlib.pyplot as plt\n\nmois = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"]\npluie = [5, 12, 48, 110, 160, 210]  # données imaginées\nplt.bar(mois, pluie, color="#007A5E")\nplt.title("Pluie par mois (mm), données fictives")\nplt.ylabel("millimètres")\nplt.show()\n'],
    ['Devine le nombre', 'import random\n\nsecret = random.randint(1, 20)\nfor essai in range(1, 6):\n    proposition = int(input("Votre nombre entre 1 et 20 : "))\n    if proposition == secret:\n        print(f"Bravo, trouvé en {essai} essai(s) !")\n        break\n    print("Plus grand" if proposition < secret else "Plus petit")\nelse:\n    print(f"Perdu, c\'était {secret}.")\n'],
  ];
  let atelier = null;
  function buildAtelier(inline) {
    const root = el('section', 'atelier' + (inline ? ' inline' : ''));
    root.setAttribute('aria-label', 'Atelier Python');
    if (!inline) { root.hidden = true; root.setAttribute('role', 'dialog'); root.setAttribute('aria-modal', 'true'); }
    const bar = el('div', 'at-bar');
    const title = el('div', 'at-title'); title.append(el('b', '', 'Atelier Python'), el('span', 'muted', 'Écrivez, exécutez, recommencez. Ctrl + Entrée pour exécuter.'));
    const sel = el('select', 'at-ex'); sel.setAttribute('aria-label', 'Exemples');
    sel.append(new Option('Exemples…', ''));
    EXAMPLES.forEach(([n], i) => sel.append(new Option(n, String(i))));
    const runB = el('button', 'btn small at-run', 'Exécuter'); runB.type = 'button';
    const clrB = el('button', 'btn ghost small', 'Effacer'); clrB.type = 'button';
    const dlB = el('button', 'btn ghost small', 'Télécharger .py'); dlB.type = 'button';
    const musB = el('button', 'btn ghost small at-music', 'Musique calme'); musB.type = 'button'; musB.setAttribute('aria-pressed', 'false');
    const tools = el('div', 'at-tools'); tools.append(sel, runB, clrB, dlB, musB);
    if (!inline) { const x = el('button', 'at-x', '×'); x.type = 'button'; x.setAttribute('aria-label', 'Fermer l’atelier'); x.onclick = () => close(); tools.append(x); }
    bar.append(title, tools);
    const saved = store.get('atelier-code');
    const ed = editor(saved || EXAMPLES[0][1], () => go(), true);
    const ui = outputBox(); ui.btn = runB; ui.box.hidden = false; ui.out.append(el('span', 'muted', 'Le résultat de votre programme apparaîtra ici.'));
    const body = el('div', 'at-body'); body.append(ed.wrap, ui.box);
    root.append(bar, body);
    const go = () => { store.set('atelier-code', ed.get()); run(ed.get(), ui); };
    runB.onclick = go;
    clrB.onclick = () => { ed.set(''); ui.out.textContent = ''; ui.plots.innerHTML = ''; ui.hint.hidden = true; ed.ta.focus(); };
    sel.onchange = () => { if (sel.value !== '') { ed.set(EXAMPLES[+sel.value][1]); sel.value = ''; } };
    dlB.onclick = () => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([ed.get()], { type: 'text/x-python' })); a.download = 'mon_programme.py'; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500); };
    musB.onclick = () => { const on = Music.toggle(); musB.setAttribute('aria-pressed', String(on)); musB.textContent = on ? 'Couper la musique' : 'Musique calme'; };
    ed.ta.addEventListener('input', () => store.set('atelier-code', ed.get()));
    function open(code) { if (code != null) ed.set(code); root.hidden = false; document.documentElement.classList.add('atelier-open'); setTimeout(() => ed.ta.focus(), 30); }
    function close() { root.hidden = true; document.documentElement.classList.remove('atelier-open'); }
    root.addEventListener('keydown', e => { if (e.key === 'Escape' && !inline) close(); });
    return { root, open, close, ed };
  }

  /* ---------- calm music for the workshop page (the reading room has its own) ---------- */
  const Music = (() => {
    let ctx, out, on = false, timer = 0, step = 0;
    const scale = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21], root = 220;
    const salonBtn = () => document.querySelector('.salon .opening button.music');
    function pluck(f, t, v) {
      const o = ctx.createOscillator(), o2 = ctx.createOscillator(), g = ctx.createGain(), g2 = ctx.createGain();
      o.type = 'sine'; o.frequency.value = f; o2.type = 'sine'; o2.frequency.value = f * 2.01;
      g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(v, t + .012); g.gain.exponentialRampToValueAtTime(.0005, t + 2.6);
      g2.gain.setValueAtTime(0, t); g2.gain.linearRampToValueAtTime(v * .22, t + .008); g2.gain.exponentialRampToValueAtTime(.0004, t + .7);
      o.connect(g); o2.connect(g2); g.connect(out); g2.connect(out); o.start(t); o2.start(t); o.stop(t + 2.8); o2.stop(t + 1);
    }
    function pad(f, t, d) {
      const o = ctx.createOscillator(), g = ctx.createGain(), lp = ctx.createBiquadFilter(); o.type = 'triangle'; o.frequency.value = f; lp.type = 'lowpass'; lp.frequency.value = 700;
      g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(.035, t + d * .4); g.gain.linearRampToValueAtTime(0, t + d);
      o.connect(lp); lp.connect(g); g.connect(out); o.start(t); o.stop(t + d + .1);
    }
    function tick() {
      if (!on) return; const t = ctx.currentTime + .05;
      if (step % 8 === 0) [0, 7, 16].forEach(s => pad(root / 2 * Math.pow(2, s / 12), t, 9));
      if (Math.random() < .72) pluck(root * Math.pow(2, scale[Math.floor(Math.random() * scale.length)] / 12), t, .07 + Math.random() * .05);
      step++; timer = setTimeout(tick, 1100 + Math.random() * 500);
    }
    function toggle() {
      const sb = salonBtn(); if (sb) { const was = sb.getAttribute('aria-pressed') === 'true'; sb.click(); return !was; }
      if (!ctx) { ctx = new (window.AudioContext || window.webkitAudioContext)(); out = ctx.createGain(); out.gain.value = .9; const d = ctx.createDelay(1), fb = ctx.createGain(); d.delayTime.value = .42; fb.gain.value = .3; out.connect(ctx.destination); out.connect(d); d.connect(fb); fb.connect(d); d.connect(ctx.destination); }
      on = !on; if (on) { ctx.resume(); tick(); } else clearTimeout(timer);
      return on;
    }
    return { toggle };
  })();

  /* ---------- turn the book's Python examples into runnable cells ---------- */
  function enhance(scope) {
    scope.querySelectorAll('pre.python:not([data-cell])').forEach(pre => {
      pre.setAttribute('data-cell', '1');
      const src = (pre.textContent || '').replace(/\n+$/, '') + '\n';
      const cell = el('div', 'pycell');
      const bar = el('div', 'pyc-bar'); const acts = el('span', 'pyc-act');
      const runB = el('button', 'btn small pyc-run', 'Exécuter'); runB.type = 'button';
      const resetB = el('button', 'btn ghost small pyc-reset', 'Réinitialiser'); resetB.type = 'button'; resetB.hidden = true;
      const openB = el('button', 'btn ghost small pyc-open', 'Dans l’atelier'); openB.type = 'button';
      acts.append(runB, resetB, openB); bar.append(el('span', 'pyc-tag', 'Python'), acts);
      const ui = outputBox(); ui.btn = runB;
      const ed = editor(src, () => run(ed.get(), ui), false);
      ed.ta.addEventListener('input', () => { resetB.hidden = ed.get() === src; });
      runB.onclick = () => run(ed.get(), ui);
      resetB.onclick = () => { ed.set(src); resetB.hidden = true; };
      openB.onclick = () => { if (!atelier) { atelier = buildAtelier(false); document.body.appendChild(atelier.root); } atelier.open(ed.get()); };
      cell.append(bar, ed.wrap, ui.box);
      pre.replaceWith(cell);
    });
    scope.querySelectorAll('pre.text:not([data-expected])').forEach(p => {
      p.setAttribute('data-expected', '1');
      const prev = p.previousElementSibling;
      if (prev && /^\s*(Résultat|Exemple de session|Sortie)/i.test(prev.textContent || '')) p.classList.add('expected');
    });
  }

  function init() {
    const inline = document.querySelector('[data-atelier-inline]');
    if (inline) { const a = buildAtelier(true); inline.appendChild(a.root); atelier = a; }
    document.addEventListener('click', e => {
      const b = e.target.closest && e.target.closest('[data-atelier]'); if (!b) return;
      e.preventDefault(); if (!atelier) { atelier = buildAtelier(false); document.body.appendChild(atelier.root); } atelier.open();
    });
    const scope = document.querySelector('.salon[data-ide]');
    if (scope) {
      enhance(scope);
      let queued = false;
      new MutationObserver(() => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; enhance(scope); }); }).observe(scope, { childList: true, subtree: true });
      const fab = el('button', 'atelier-fab', 'Atelier Python'); fab.type = 'button'; fab.setAttribute('data-atelier', ''); document.body.appendChild(fab);
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
