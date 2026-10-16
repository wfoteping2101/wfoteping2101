# Hand-drawn vector covers for three books. Pure SVG, drawn in code: no generated images.
# cover_svg(seed) returns an <svg class="cover-art cover-custom"> for the seeds below, or None.
import random

_n = [0]
def _uid():
    _n[0] += 1
    return f"c{_n[0]}"

SERIF = "Fraunces, Georgia, 'Times New Roman', serif"
MONO = "'JetBrains Mono', ui-monospace, Menlo, monospace"
SANS = "Inter, system-ui, sans-serif"

def _grain(fid, alpha=".07"):
    return (f'<filter id="{fid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>'
            f'<feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 {alpha}"/></feComponentTransfer></filter>')

# ---------------------------------------------------------------------------
# La Richesse Silencieuse: the unfinished house, paid for month after month from abroad.
def richesse():
    u = _uid()
    G, GL, CR, BG = "#C9A45C", "#E6CB8E", "#F1E7D3", "#0C2A20"
    rnd = random.Random(7)
    o = []
    o.append(f'<defs>{_grain("g" + u)}<radialGradient id="r{u}" cx="50%" cy="66%" r="60%"><stop offset="0" stop-color="#14392C"/><stop offset="1" stop-color="{BG}"/></radialGradient>'
             f'<linearGradient id="t{u}" x1="1" y1="0" x2="0" y2="0" gradientUnits="userSpaceOnUse" gradientTransform="scale(600 1)"><stop offset="0" stop-color="{GL}" stop-opacity=".95"/><stop offset=".55" stop-color="{G}" stop-opacity=".55"/><stop offset="1" stop-color="{G}" stop-opacity=".08"/></linearGradient>'
             f'<path id="p1{u}" d="M 330 560 C 352 470, 420 410, 640 388"/><path id="p2{u}" d="M 352 572 C 376 488, 444 432, 640 418"/><path id="p3{u}" d="M 376 584 C 398 508, 466 456, 640 448"/></defs>')
    o.append(f'<rect width="600" height="900" fill="url(#r{u})"/>')
    # a quiet sun behind the house
    o.append(f'<circle cx="300" cy="620" r="150" fill="{G}" fill-opacity=".03"/><circle cx="300" cy="620" r="150" fill="none" stroke="{G}" stroke-opacity=".1" stroke-width="1"/>')
    # transfers flowing in from abroad: amounts written along the line, fading as they reach the house
    amounts = ["200 €", "350 $", "150 000 FCFA", "100 €", "500 $", "75 000 FCFA", "250 €", "300 $", "50 000 FCFA", "400 €"]
    o.append(f'<clipPath id="k{u}"><rect x="23" y="23" width="554" height="854"/></clipPath><g clip-path="url(#k{u})">')
    for k, pid in enumerate(("p1", "p2", "p3")):
        seq = amounts[k * 3:] + amounts[:k * 3]
        line = "  ·  ".join(seq + seq) + "  ·  "
        o.append(f'<text font-family="{MONO}" font-size="{11 - k}" letter-spacing="1" fill="url(#t{u})"><textPath href="#{pid}{u}" startOffset="{2 + k * 3}%">{line}</textPath></text>')
    o.append('</g>')
    # ground
    o.append(f'<path d="M 64 782 H 536" stroke="{G}" stroke-width="1.2"/>')
    for x in range(78, 530, 22):
        o.append(f'<path d="M {x} 790 l -8 10" stroke="{G}" stroke-opacity=".35" stroke-width=".8"/>')
    # cinder blocks: the walls stopped where the money stopped
    def blocks(x0, x1, y_bottom, rows_full, ragged, fill_op=".07"):
        bw, bh = 28, 14
        for r in range(rows_full + ragged):
            y = y_bottom - (r + 1) * bh
            off = 0 if r % 2 == 0 else bw / 2
            x = x0 - off
            while x < x1:
                a, b = max(x, x0), min(x + bw, x1)
                keep = r < rows_full or rnd.random() < (0.75 if r == rows_full else 0.35)
                if keep and b - a > 4:
                    o.append(f'<rect x="{a + .6:.1f}" y="{y + .6:.1f}" width="{b - a - 1.2:.1f}" height="{bh - 1.2}" fill="{CR}" fill-opacity="{fill_op}" stroke="{CR}" stroke-opacity=".32" stroke-width=".7"/>')
                x += bw
    blocks(174, 300, 776, 6, 2)
    blocks(314, 426, 776, 3, 2)
    blocks(314, 426, 606, 2, 1, ".05")
    # concrete frame: slabs and columns
    def rect(x, y, w, h, op=".9", fill=".05"):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{G}" fill-opacity="{fill}" stroke="{G}" stroke-opacity="{op}" stroke-width="1.1"/>')
    rect(140, 776, 320, 8, fill=".2")
    for cx in (160, 300, 426):
        rect(cx, 620, 14, 156)
        rect(cx, 474, 14, 132)
    rect(140, 606, 320, 14, fill=".14")
    rect(160, 466, 154, 10, fill=".1")   # one beam, never continued
    # rebar waiting at the top of every column
    for cx in (160, 300, 426):
        for i, dx in enumerate((2, 6, 9, 12)):
            lean = (i - 1.5) * 2.2 + rnd.uniform(-1, 1)
            top = 474 if cx != 160 and cx != 300 else 466
            o.append(f'<path d="M {cx + dx} {top} q {lean * .4:.1f} -22 {lean:.1f} -{38 + rnd.randint(0, 14)}" fill="none" stroke="{GL}" stroke-opacity=".8" stroke-width=".9"/>')
    # weeds at the foot of the columns: time passing
    for cx in (156, 296, 422, 452):
        for j in range(5):
            h = rnd.randint(7, 16)
            o.append(f'<path d="M {cx + j * 3} 776 q {rnd.uniform(-4, 4):.1f} -{h / 2:.0f} {rnd.uniform(-6, 6):.1f} -{h}" fill="none" stroke="{G}" stroke-opacity=".5" stroke-width=".8"/>')
    # frame, type
    o.append(f'<rect x="22" y="22" width="556" height="856" fill="none" stroke="{G}" stroke-opacity=".45" stroke-width=".8"/>')
    o.append(f'<text x="300" y="84" text-anchor="middle" font-family="{MONO}" font-size="13" letter-spacing="6" fill="{G}">WILLIAM FOTEPING</text>')
    o.append(f'<text x="300" y="190" text-anchor="middle" font-family="{SERIF}" font-size="74" font-weight="400" fill="{CR}">La Richesse</text>')
    o.append(f'<text x="300" y="272" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="82" font-weight="300" fill="{GL}">Silencieuse</text>')
    o.append(f'<path d="M 270 308 H 330" stroke="{G}" stroke-width="1"/>')
    o.append(f'<text x="300" y="342" text-anchor="middle" font-family="{SANS}" font-size="15" letter-spacing=".6" fill="{CR}" fill-opacity=".78">Le guide d’investissement</text>')
    o.append(f'<text x="300" y="364" text-anchor="middle" font-family="{SANS}" font-size="15" letter-spacing=".6" fill="{CR}" fill-opacity=".78">de la diaspora africaine</text>')
    o.append(f'<text x="300" y="846" text-anchor="middle" font-family="{MONO}" font-size="10" letter-spacing="3" fill="{G}" fill-opacity=".7">GUIDE</text>')
    o.append(f'<rect width="600" height="900" filter="url(#g{u})"/>')
    return "".join(o)

# ---------------------------------------------------------------------------
# Le capital entravé: a land registry plan. A few titled parcels in one hand; everyone else lives on land that
# cannot serve as capital, with a stamp that never comes.
def capital():
    u = _uid()
    PA, INK, RED, OCH, MUTE = "#EDE3CF", "#24170F", "#A8432A", "#C69A4B", "#6B5A48"
    rnd = random.Random(11)
    o = []
    X0, Y0, X1, Y1 = 46, 392, 554, 838
    cols, rows = 9, 8
    cw, ch = (X1 - X0) / cols, (Y1 - Y0) / rows
    # shared jittered vertices so the parcels tile like a real plan
    V = [[(X0 + c * cw + (rnd.uniform(-9, 9) if 0 < c < cols else 0), Y0 + r * ch + (rnd.uniform(-8, 8) if 0 < r < rows else 0)) for c in range(cols + 1)] for r in range(rows + 1)]
    titled = {(0, 6), (0, 7), (0, 8), (1, 6), (1, 7), (1, 8), (2, 7), (2, 8), (3, 8), (2, 6)}
    o.append(f'<defs>{_grain("g" + u, ".09")}<clipPath id="m{u}"><rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}"/></clipPath>'
             f'<path id="s{u}" d="M 190 718 m -58 0 a 58 58 0 1 1 116 0 a 58 58 0 1 1 -116 0"/></defs>')
    o.append(f'<rect width="600" height="900" fill="{PA}"/>')
    o.append(f'<g clip-path="url(#m{u})">')
    for r in range(rows):
        for c in range(cols):
            a, b, cc, d = V[r][c], V[r][c + 1], V[r + 1][c + 1], V[r + 1][c]
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (a, b, cc, d))
            mx, my = sum(p[0] for p in (a, b, cc, d)) / 4, sum(p[1] for p in (a, b, cc, d)) / 4
            if (r, c) in titled:
                o.append(f'<polygon points="{pts}" fill="{RED}" fill-opacity=".9" stroke="{PA}" stroke-width="1.4"/>')
                o.append(f'<text x="{mx:.1f}" y="{my + 3:.1f}" text-anchor="middle" font-family="{MONO}" font-size="8" fill="{PA}" fill-opacity=".9">TF {rnd.randint(10, 99)}</text>')
            else:
                o.append(f'<polygon points="{pts}" fill="{OCH}" fill-opacity="{rnd.choice(("0", "0", ".05", ".09"))}" stroke="{INK}" stroke-opacity=".5" stroke-width=".8" stroke-dasharray="3 3"/>')
                if rnd.random() < .55:   # a home that exists, on land that cannot be used as capital
                    s = rnd.uniform(7, 10)
                    hx, hy = mx + rnd.uniform(-8, 8), my + rnd.uniform(-5, 7)
                    o.append(f'<path d="M {hx - s:.1f} {hy:.1f} v {s * .9:.1f} h {2 * s:.1f} v -{s * .9:.1f} M {hx - s - 2:.1f} {hy + 1:.1f} L {hx:.1f} {hy - s * .8:.1f} L {hx + s + 2:.1f} {hy + 1:.1f}" fill="none" stroke="{INK}" stroke-opacity=".62" stroke-width=".9" stroke-linejoin="round"/>')
                    if rnd.random() < .5:
                        for k in range(3):
                            o.append(f'<circle cx="{hx + s + 6 + k * 4:.1f}" cy="{hy + s * .9 - 1:.1f}" r="1.1" fill="{INK}" fill-opacity=".45"/>')
    # one bold line around the parcels held by a single owner
    edge = [V[0][6], V[1][6], V[2][6], V[3][6], V[3][7], V[3][8], V[4][8], V[4][9]]
    o.append('<path d="M ' + " L ".join(f"{x:.1f} {y:.1f}" for x, y in edge) + f'" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
    # the road the plan never finished
    road = "M 30 650 C 160 610, 250 690, 360 640 S 520 560, 580 590"
    o.append(f'<path d="{road}" fill="none" stroke="{PA}" stroke-width="22"/>')
    o.append(f'<path d="{road}" fill="none" stroke="{INK}" stroke-opacity=".55" stroke-width="1" transform="translate(0 -11)"/><path d="{road}" fill="none" stroke="{INK}" stroke-opacity=".55" stroke-width="1" transform="translate(0 11)" stroke-dasharray="40 14"/>')
    o.append('</g>')
    o.append(f'<rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    # north arrow and scale bar
    o.append(f'<g transform="translate(540 362)" fill="none" stroke="{INK}" stroke-width=".9"><path d="M 0 14 L 0 -12 M -5 -4 L 0 -12 L 5 -4"/></g><text x="526" y="372" text-anchor="middle" font-family="{MONO}" font-size="9" fill="{INK}">N</text>')
    o.append(f'<g transform="translate(46 862)"><rect width="40" height="5" fill="{INK}"/><rect x="40" width="40" height="5" fill="{PA}" stroke="{INK}" stroke-width=".8"/><text y="-5" font-family="{MONO}" font-size="8" fill="{INK}">0</text><text x="40" y="-5" text-anchor="middle" font-family="{MONO}" font-size="8" fill="{INK}">50</text><text x="80" y="-5" text-anchor="middle" font-family="{MONO}" font-size="8" fill="{INK}">100 m</text></g>')
    # the stamp that never comes
    o.append(f'<g transform="rotate(-14 190 718)" opacity=".86"><circle cx="190" cy="718" r="74" fill="{PA}" fill-opacity=".55" stroke="{RED}" stroke-width="2.4"/><circle cx="190" cy="718" r="66" fill="none" stroke="{RED}" stroke-width=".9"/><circle cx="190" cy="718" r="40" fill="none" stroke="{RED}" stroke-width=".9"/>'
             f'<text font-family="{MONO}" font-size="10.5" letter-spacing="2.2" fill="{RED}"><textPath href="#s{u}" textLength="352" lengthAdjust="spacing">TITRE FONCIER · DEMANDE EN ATTENTE ·</textPath></text>'
             f'<text x="190" y="714" text-anchor="middle" font-family="{SERIF}" font-size="15" font-weight="600" fill="{RED}">ORD.</text><text x="190" y="732" text-anchor="middle" font-family="{SERIF}" font-size="15" font-weight="600" fill="{RED}">74-1</text></g>')
    # type
    o.append(f'<text x="300" y="84" text-anchor="middle" font-family="{MONO}" font-size="13" letter-spacing="6" fill="{INK}" fill-opacity=".85">WILLIAM FOTEPING</text>')
    o.append(f'<text x="300" y="186" text-anchor="middle" font-family="{SERIF}" font-size="76" font-weight="600" fill="{INK}">Le capital</text>')
    o.append(f'<text x="300" y="268" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="86" font-weight="400" fill="{RED}">entravé</text>')
    o.append(f'<text x="300" y="320" text-anchor="middle" font-family="{SANS}" font-size="15" letter-spacing=".6" fill="{INK}" fill-opacity=".78">Institutions, investissement</text>')
    o.append(f'<text x="300" y="342" text-anchor="middle" font-family="{SANS}" font-size="15" letter-spacing=".6" fill="{INK}" fill-opacity=".78">et prospérité au Cameroun</text>')
    o.append(f'<text x="554" y="868" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="3" fill="{INK}" fill-opacity=".7">ESSAI</text>')
    o.append(f'<rect width="600" height="900" filter="url(#g{u})"/>')
    return "".join(o)

# ---------------------------------------------------------------------------
# Caméra au poing: a phone viewfinder, mid-recording, with the focus box on a third.
def camera():
    u = _uid()
    PA, AM, RED = "#ECE5D8", "#D4AD6A", "#E5484D"
    X0, Y0, X1, Y1 = 42, 42, 558, 858
    o = []
    o.append(f'<defs>{_grain("g" + u, ".09")}'
             f'<linearGradient id="b{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121215"/><stop offset=".6" stop-color="#0B0B0D"/><stop offset="1" stop-color="#08080A"/></linearGradient>'
             f'<radialGradient id="a{u}" cx="444" cy="198" r="360" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{AM}" stop-opacity=".34"/><stop offset=".7" stop-color="{AM}" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="r{u}" cx="72" cy="828" r="400" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#8B3A2A" stop-opacity=".42"/><stop offset=".72" stop-color="#8B3A2A" stop-opacity="0"/></radialGradient>'
             f'<filter id="f{u}" x="-1" y="-1" width="3" height="3"><feGaussianBlur stdDeviation="5"/></filter></defs>')
    o.append(f'<rect width="600" height="900" fill="url(#b{u})"/><rect width="600" height="900" fill="url(#a{u})"/><rect width="600" height="900" fill="url(#r{u})"/>')
    # rule of thirds inside the frame
    w, h = X1 - X0, Y1 - Y0
    for k in (1, 2):
        x, y = X0 + w * k / 3, Y0 + h * k / 3
        o.append(f'<path d="M {x:.1f} {Y0} V {Y1} M {X0} {y:.1f} H {X1}" stroke="{PA}" stroke-opacity=".11" stroke-width="1"/>')
    # frame corners
    L, sw = 54, 2.6
    for cx, cy, dx, dy in ((X0, Y0, 1, 1), (X1, Y0, -1, 1), (X0, Y1, 1, -1), (X1, Y1, -1, -1)):
        o.append(f'<path d="M {cx} {cy + dy * L} V {cy} H {cx + dx * L}" fill="none" stroke="{PA}" stroke-opacity=".88" stroke-width="{sw}"/>')
    # HUD: REC, resolution, timecode
    hud = f'font-family="{SANS}" font-size="13.5" letter-spacing="2.4" fill="{PA}" fill-opacity=".82"'
    o.append(f'<circle cx="75" cy="80" r="11" fill="{RED}" fill-opacity=".55" filter="url(#f{u})"/><circle cx="75" cy="80" r="6.6" fill="{RED}"/>')
    o.append(f'<text x="91" y="85" {hud}>REC</text><text x="532" y="85" text-anchor="end" {hud}>4K</text>')
    o.append(f'<text x="532" y="826" text-anchor="end" {hud} style="font-variant-numeric:tabular-nums">00:00:01:12</text>')
    # focus box on the upper-right third
    fx, fy, s, t = X0 + w * 2 / 3, Y0 + h / 3, 39, 19
    for cx, cy, dx, dy in ((fx - s, fy - s, 1, 1), (fx + s, fy - s, -1, 1), (fx - s, fy + s, 1, -1), (fx + s, fy + s, -1, -1)):
        o.append(f'<path d="M {cx:.1f} {cy + dy * t:.1f} V {cy:.1f} H {cx + dx * t:.1f}" fill="none" stroke="{AM}" stroke-width="2"/>')
    o.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="3.3" fill="{AM}"/>')
    # type
    o.append(f'<text x="75" y="436" font-family="{SANS}" font-size="13" letter-spacing="4.4" fill="{AM}">VLOG · CINÉMA · MONTAGE</text>')
    o.append(f'<text x="72" y="540" font-family="{SERIF}" font-size="104" font-weight="500" letter-spacing="-1" fill="{PA}">Caméra</text>')
    o.append(f'<text x="104" y="638" font-family="{SERIF}" font-style="italic" font-size="104" font-weight="400" letter-spacing="-1" fill="{AM}">au poing</text>')
    o.append(f'<text font-family="{SERIF}" font-style="italic" font-size="23" fill="{PA}" fill-opacity=".82"><tspan x="75" y="700">Vloguer et filmer comme un pro,</tspan><tspan x="75" y="731">avec un téléphone et Bobine</tspan></text>')
    o.append(f'<text x="75" y="826" font-family="{SANS}" font-size="12.5" letter-spacing="5.2" fill="{PA}" fill-opacity=".72">ÉDITIONS BOBINE</text>')
    o.append(f'<rect width="600" height="900" filter="url(#g{u})"/>')
    return "".join(o)

COVERS = {"richesse-silencieuse": richesse, "la-richesse-silencieuse": richesse, "capital-entrave": capital, "le-capital-entrave": capital, "camera-au-poing": camera}

def cover_svg(seed):
    fn = COVERS.get(seed)
    if not fn: return None
    return f'<svg class="cover-art cover-custom" viewBox="0 0 600 900" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Couverture">{fn()}</svg>'
