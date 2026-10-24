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


# ---------------------------------------------------------------------------
# La Monnaie, la Terre et le Mérite: three gold emblems on deep green, one per book.
def monnaie():
    u = _uid()
    BG, BG2, G, GL, PA, MUTE = "#06241A", "#0B3D2E", "#B8862B", "#F1CF7A", "#F6F1E3", "#CFE3D8"
    o = []
    o.append(f'<defs>{_grain("g" + u)}<linearGradient id="b{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
             f'<linearGradient id="au{u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GL}"/><stop offset="1" stop-color="{G}"/></linearGradient>'
             f'<pattern id="q{u}" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="4.5" height="4.5" fill="{GL}" fill-opacity=".9"/><rect x="6" y="1.5" width="3" height="3" fill="{GL}" fill-opacity=".5"/><rect x="1.5" y="6.5" width="3" height="3" fill="{GL}" fill-opacity=".6"/><rect x="6.5" y="6.5" width="3.5" height="3.5" fill="{GL}" fill-opacity=".35"/></pattern>'
             f'<clipPath id="c1{u}"><circle cx="120" cy="486" r="60"/></clipPath><clipPath id="c2{u}"><circle cx="300" cy="486" r="60"/></clipPath><clipPath id="c3{u}"><circle cx="480" cy="486" r="60"/></clipPath></defs>')
    o.append(f'<rect width="600" height="900" fill="url(#b{u})"/>')
    o.append(f'<rect x="26" y="26" width="548" height="848" fill="none" stroke="{GL}" stroke-opacity=".35" stroke-width="1.2"/>')
    o.append(f'<text x="300" y="88" text-anchor="middle" font-family="{SANS}" font-size="9.5" letter-spacing="3.6" fill="{MUTE}">UN MANIFESTE POUR LES DÉCIDEURS CAMEROUNAIS</text>')
    o.append(f'<text x="300" y="175" text-anchor="middle" font-family="{SERIF}" font-size="50" font-weight="600" letter-spacing="-.5" fill="{PA}">La Monnaie,</text>')
    o.append(f'<text x="300" y="232" text-anchor="middle" font-family="{SERIF}" font-size="50" font-weight="600" letter-spacing="-.5" fill="{PA}">la Terre</text>')
    o.append(f'<text x="300" y="289" text-anchor="middle" font-family="{SERIF}" font-size="50" font-weight="600" letter-spacing="-.5" fill="{PA}">et le Mérite</text>')
    o.append(f'<rect x="240" y="310" width="120" height="2.5" fill="url(#au{u})"/>')
    o.append(f'<text x="300" y="344" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="16.5" fill="#E7D9AD">Trois réformes dures pour un Cameroun qui se construit</text>')
    # 1. money: a coin whose right half becomes a QR code
    o.append(f'<circle cx="120" cy="486" r="64" fill="none" stroke="{GL}" stroke-width="3.5"/>')
    o.append(f'<g clip-path="url(#c1{u})"><rect x="60" y="426" width="60" height="120" fill="{GL}" fill-opacity=".12"/><text x="90" y="502" text-anchor="middle" font-family="{SERIF}" font-size="46" font-weight="700" fill="{GL}">F</text><rect x="120" y="426" width="60" height="120" fill="url(#q{u})"/></g>')
    o.append(f'<line x1="120" y1="422" x2="120" y2="550" stroke="{BG}" stroke-width="3.5"/>')
    # 2. land: furrows under a small factory and an export arrow
    o.append(f'<circle cx="300" cy="486" r="64" fill="none" stroke="{GL}" stroke-width="3.5"/>')
    o.append(f'<g clip-path="url(#c2{u})"><rect x="240" y="494" width="120" height="52" fill="{GL}" fill-opacity=".12"/>'
             f'<path d="M240,508 Q270,497 300,508 T360,508" fill="none" stroke="{GL}" stroke-width="3"/><path d="M240,523 Q270,512 300,523 T360,523" fill="none" stroke="{GL}" stroke-width="3"/><path d="M240,538 Q270,527 300,538 T360,538" fill="none" stroke="{GL}" stroke-width="3"/>'
             f'<rect x="259" y="460" width="22" height="34" fill="{GL}"/><rect x="285" y="445" width="22" height="49" fill="{GL}"/><rect x="311" y="471" width="22" height="23" fill="{GL}"/><path d="M263,460 L274,445 L285,460" fill="{GL}"/>'
             f'<path d="M337,478 L359,456 M359,456 L345,456 M359,456 L359,470" fill="none" stroke="{GL}" stroke-width="3.5" stroke-linecap="round"/></g>')
    # 3. merit: a balanced scale over equal figures
    o.append(f'<circle cx="480" cy="486" r="64" fill="none" stroke="{GL}" stroke-width="3.5"/>')
    o.append(f'<g clip-path="url(#c3{u})"><line x1="480" y1="440" x2="480" y2="498" stroke="{GL}" stroke-width="3.5"/><line x1="440" y1="454" x2="520" y2="454" stroke="{GL}" stroke-width="3.5"/>'
             f'<path d="M428,480 L452,480 L440,454 Z" fill="none" stroke="{GL}" stroke-width="3"/><path d="M508,480 L532,480 L520,454 Z" fill="none" stroke="{GL}" stroke-width="3"/><line x1="458" y1="498" x2="502" y2="498" stroke="{GL}" stroke-width="3.5"/>')
    for i in range(5):
        x = 440 + i * 20
        o.append(f'<circle cx="{x}" cy="514" r="5" fill="{GL}"/><rect x="{x - 5}" y="521" width="10" height="18" rx="2.5" fill="{GL}"/>')
    o.append('</g>')
    for x, a, b in ((120, "LA MONNAIE", "le même franc, un autre support"), (300, "LA TERRE", "cultiver, fabriquer, exporter"), (480, "LE MÉRITE", "un pays n'appartient à personne")):
        o.append(f'<text x="{x}" y="582" text-anchor="middle" font-family="{SERIF}" font-size="15.5" fill="{PA}">{a}</text><text x="{x}" y="601" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="10" fill="{MUTE}">{b}</text>')
    o.append(f'<text x="300" y="668" text-anchor="middle" font-family="{SERIF}" font-size="12.5" fill="#E7D9AD">LIVRE I · Le Cameroun sans espèces</text>')
    o.append(f'<text x="300" y="690" text-anchor="middle" font-family="{SERIF}" font-size="12.5" fill="#E7D9AD">LIVRE II · Ce qui fait fonctionner l’Asie</text>')
    o.append(f'<text x="300" y="712" text-anchor="middle" font-family="{SERIF}" font-size="12.5" fill="#E7D9AD">LIVRE III · Un pays n’appartient à personne</text>')
    o.append(f'<path d="M 110 752 H 490" stroke="{GL}" stroke-opacity=".5" stroke-width="1"/>')
    o.append(f'<text font-family="{SERIF}" font-style="italic" font-size="14.5" fill="{PA}" text-anchor="middle"><tspan x="300" y="784">« Le cash ne cause pas la pauvreté ;</tspan><tspan x="300" y="806">il la rend invisible, lente et coûteuse. »</tspan></text>')
    o.append(f'<text x="300" y="856" text-anchor="middle" font-family="{SANS}" font-size="8.5" letter-spacing="3" fill="{MUTE}">AVEC LE DÉMONSTRATEUR INTERACTIF e-XAF</text>')
    o.append(f'<rect width="600" height="900" filter="url(#g{u})"/>')
    return "".join(o)

# ---------------------------------------------------------------------------
# Les Yeux ouverts: an open eye at dawn; the iris is a neural network, and under it
# five greetings are split into tokens the way a language model splits them.
def yeux():
    import math
    u = _uid()
    CX, CY, EW, EH = 300, 395, 230, 118
    GOLD, GOLD2, CREAM, MIST = "#F2C66D", "#C8902E", "#F7F1E3", "#C9CFEA"
    rnd = random.Random(7)
    o = []
    lid = f"M{CX-EW},{CY} Q{CX},{CY-2*EH} {CX+EW},{CY} Q{CX},{CY+2*EH} {CX-EW},{CY} Z"
    o.append(f'<defs>{_grain("g" + u, ".06")}'
             f'<linearGradient id="b{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#151A47"/><stop offset=".55" stop-color="#0C1033"/><stop offset="1" stop-color="#070920"/></linearGradient>'
             f'<linearGradient id="au{u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD2}"/></linearGradient>'
             f'<radialGradient id="d{u}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{GOLD}" stop-opacity=".30"/><stop offset=".6" stop-color="{GOLD}" stop-opacity=".06"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="i{u}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#2A2F6B"/><stop offset="1" stop-color="#11143A"/></radialGradient>'
             f'<clipPath id="e{u}"><path d="{lid}"/></clipPath><clipPath id="f{u}"><rect x="25" y="25" width="550" height="850"/></clipPath></defs>')
    o.append(f'<rect width="600" height="900" fill="url(#b{u})"/>')
    for row in range(5):
        for col in range(16):
            x = 22 + col * 37 + (18 if row % 2 else 0)
            y = 742 + row * 26
            if x > 580: continue
            o.append(f'<path d="M{x},{y-6} L{x+7},{y} L{x},{y+6} L{x-7},{y} Z" fill="none" stroke="{MIST}" stroke-opacity=".07" stroke-width="1"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="300" fill="url(#d{u})"/><g clip-path="url(#f{u})">')
    for i in range(48):
        a = math.pi * i / 47
        r1, r2 = 228, 228 + (26 if i % 2 else 48)
        o.append(f'<line x1="{CX + r1*math.cos(a):.1f}" y1="{CY - r1*math.sin(a):.1f}" x2="{CX + r2*math.cos(a):.1f}" y2="{CY - r2*math.sin(a):.1f}" stroke="{GOLD}" stroke-opacity=".22" stroke-width="1"/>')
    o.append('</g>')
    o.append(f'<path d="{lid}" fill="#E9E4F2" fill-opacity=".06"/><g clip-path="url(#e{u})">')
    R = 102
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#i{u})"/>')
    nodes = []
    for rad, n in ((34, 8), (58, 14), (82, 20)):
        off = rnd.random() * math.pi
        nodes.append([(CX + rad * math.cos(off + 2*math.pi*k/n), CY + rad * math.sin(off + 2*math.pi*k/n)) for k in range(n)])
    for r in range(2):
        for (x1, y1) in nodes[r]:
            for (x2, y2) in sorted(nodes[r + 1], key=lambda p: (p[0]-x1)**2 + (p[1]-y1)**2)[:3]:
                o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{GOLD}" stroke-opacity=".55" stroke-width=".9"/>')
    for (x, y) in nodes[2]:
        o.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{CX + R*(x-CX)/82:.1f}" y2="{CY + R*(y-CY)/82:.1f}" stroke="{GOLD}" stroke-opacity=".35" stroke-width=".8"/>')
    for ri, ring in enumerate(nodes):
        for (x, y) in ring:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2.6 + ri*0.4:.1f}" fill="{GOLD}"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="url(#au{u})" stroke-width="3"/>'
             f'<circle cx="{CX}" cy="{CY}" r="21" fill="#05061A"/><circle cx="{CX-7}" cy="{CY-8}" r="5.5" fill="{CREAM}" fill-opacity=".9"/></g>')
    o.append(f'<path d="{lid}" fill="none" stroke="url(#au{u})" stroke-width="4.5" stroke-linejoin="round"/>'
             f'<path d="M{CX-EW-14},{CY} Q{CX},{CY-2*EH-34} {CX+EW+14},{CY}" fill="none" stroke="{GOLD}" stroke-opacity=".45" stroke-width="1.6"/>')
    chips = (("Mbo", "te"), ("Jë", "rë", "jëf"), ("Bon", "jour"), ("I", "ni", "ce"), ("A", "kwa", "ba"))
    labels = ("lingala", "wolof", "français", "bambara", "baoulé")
    widths = [sum(12 + 8.2 * len(p) for p in ch) + 3 * (len(ch) - 1) for ch in chips]
    x, y0 = CX - (sum(widths) + 14 * 4) / 2, CY + 148
    for ch, w, lab in zip(chips, widths, labels):
        xx = x
        for p in ch:
            pw = 12 + 8.2 * len(p)
            o.append(f'<rect x="{xx:.1f}" y="{y0-13}" width="{pw:.1f}" height="22" rx="5" fill="{GOLD}" fill-opacity=".10" stroke="{GOLD}" stroke-opacity=".7" stroke-width="1"/>'
                     f'<text x="{xx+pw/2:.1f}" y="{y0+3}" text-anchor="middle" font-family="{SANS}" font-size="12.5" font-weight="500" fill="{CREAM}">{p}</text>')
            xx += pw + 3
        o.append(f'<text x="{x+w/2:.1f}" y="{y0+25}" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="9.5" fill="{MIST}" fill-opacity=".8">{lab}</text>')
        x += w + 14
    o.append(f'<rect x="24" y="24" width="552" height="852" fill="none" stroke="{GOLD}" stroke-opacity=".32" stroke-width="1.1"/>')
    o.append(f'<text x="300" y="80" text-anchor="middle" font-family="{SANS}" font-size="9.6" font-weight="500" letter-spacing="3.4" fill="{MIST}">L’INTELLIGENCE ARTIFICIELLE EXPLIQUÉE</text>'
             f'<text x="300" y="97" text-anchor="middle" font-family="{SANS}" font-size="9.6" font-weight="500" letter-spacing="3.4" fill="{MIST}">À CEUX QUI NE CODENT PAS</text>')
    o.append(f'<text x="300" y="648" text-anchor="middle" font-family="{SANS}" font-size="64" font-weight="800" letter-spacing="-1.5" fill="{CREAM}">Les Yeux</text>'
             f'<text x="300" y="712" text-anchor="middle" font-family="{SANS}" font-size="64" font-weight="800" letter-spacing="-1.5" fill="url(#au{u})">ouverts</text>'
             f'<rect x="245" y="732" width="110" height="2.5" fill="url(#au{u})"/>')
    o.append(f'<text x="300" y="762" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="16.5" fill="#E9DDB8">Pourquoi l’Afrique ne peut plus</text>'
             f'<text x="300" y="783" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="16.5" fill="#E9DDB8">détourner le regard</text>')
    o.append(f'<text x="300" y="842" text-anchor="middle" font-family="{SANS}" font-size="8.4" font-weight="500" letter-spacing="2.2" fill="{MIST}">OUVRIR LA MACHINE  ·  LES MACHINES QUI AGISSENT  ·  L’AFRIQUE DEVANT LA MACHINE</text>')
    o.append(f'<rect width="600" height="900" filter="url(#g{u})"/>')
    return "".join(o)

# ---------------------------------------------------------------------------
# Tout est code: a code window on deep green, the flag's three colours, and four verbs printed by Python.
def code():
    u = _uid()
    BG, BG2, G, R, Y, CR, MU = "#0B1A15", "#12291F", "#007A5E", "#CE1126", "#FCD116", "#F4EFE3", "#A9C2B6"
    o = []
    o.append(f'<defs>{_grain("g" + u, ".06")}<linearGradient id="b{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
             f'<pattern id="d{u}" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="{MU}" fill-opacity=".14"/></pattern></defs>')
    o.append(f'<rect width="600" height="900" fill="url(#b{u})"/><rect width="600" height="900" fill="url(#d{u})"/>')
    # the flag as three bands across the top, the star in the middle band
    o.append(f'<rect x="0" y="0" width="200" height="14" fill="{G}"/><rect x="200" y="0" width="200" height="14" fill="{R}"/><rect x="400" y="0" width="200" height="14" fill="{Y}"/>')
    o.append(f'<text x="300" y="74" text-anchor="middle" font-family="{SANS}" font-size="10" font-weight="600" letter-spacing="3.6" fill="{MU}">APPRENDRE PYTHON, POUR L’AFRIQUE ET SA DIASPORA</text>')
    # the code window
    x0, y0, w, h = 62, 116, 476, 342
    o.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="16" fill="#06110D" stroke="{G}" stroke-opacity=".55" stroke-width="1.4"/>')
    o.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="38" rx="16" fill="#0F2219"/><rect x="{x0}" y="{y0 + 22}" width="{w}" height="16" fill="#0F2219"/>')
    for i, c in enumerate((G, R, Y)):
        o.append(f'<circle cx="{x0 + 24 + i * 20}" cy="{y0 + 19}" r="6" fill="{c}"/>')
    o.append(f'<text x="{x0 + w - 18}" y="{y0 + 24}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MU}">atelier.py</text>')
    K, S, B, C, N = "#FF8FA0", "#FCE08A", "#7FE0C3", "#8FA39C", "#E9F2EE"
    lines = [
        [(C, "# le code est une langue, elle est à vous")],
        [(N, "verbes = ["), (S, '"penser"'), (N, ", "), (S, '"rattraper"'), (N, ",")],
        [(N, "          "), (S, '"critiquer"'), (N, ", "), (S, '"visualiser"'), (N, "]")],
        [],
        [(K, "for"), (N, " verbe "), (K, "in"), (N, " verbes:")],
        [(N, "    "), (B, "print"), (N, "(verbe.upper())")],
    ]
    yy = y0 + 72
    for ln in lines:
        x = x0 + 22
        spans = "".join(f'<tspan fill="{c}">{s.replace("&", "&amp;").replace("<", "&lt;")}</tspan>' for c, s in ln)
        o.append(f'<text x="{x}" y="{yy}" font-family="{MONO}" font-size="15" xml:space="preserve">{spans}</text>')
        yy += 26
    o.append(f'<line x1="{x0 + 18}" y1="{yy - 6}" x2="{x0 + w - 18}" y2="{yy - 6}" stroke="{MU}" stroke-opacity=".25" stroke-dasharray="3 5"/>')
    yy += 18
    for i, v in enumerate(("PENSER", "RATTRAPER", "CRITIQUER", "VISUALISER")):
        o.append(f'<text x="{x0 + 22}" y="{yy + i * 24}" font-family="{MONO}" font-size="15" font-weight="600" fill="{("#3CC79A" if i == 0 else "#FF5A6E" if i == 1 else Y if i == 2 else CR)}" fill-opacity="{1 if i else .95}">{v}</text>')
    o.append(f'<rect x="{x0 + 22 + 10 * 9.2}" y="{yy + 3 * 24 - 13}" width="9" height="16" fill="{Y}"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>')
    # the title
    o.append(f'<text x="300" y="604" text-anchor="middle" font-family="{SANS}" font-size="68" font-weight="800" letter-spacing="-2" fill="{CR}">Tout est</text>')
    o.append(f'<text x="300" y="684" text-anchor="middle" font-family="{MONO}" font-size="74" font-weight="600" letter-spacing="-1" fill="{Y}">code<tspan fill="{G}">()</tspan></text>')
    o.append(f'<rect x="230" y="708" width="46" height="3" fill="{G}"/><rect x="277" y="708" width="46" height="3" fill="{R}"/><rect x="324" y="708" width="46" height="3" fill="{Y}"/>')
    o.append(f'<text x="300" y="742" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="16.5" fill="#E7E0C8">Apprendre Python pour penser clair,</text>')
    o.append(f'<text x="300" y="764" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="16.5" fill="#E7E0C8">comprendre son époque et tout visualiser</text>')
    o.append(f'<text x="300" y="838" text-anchor="middle" font-family="{SANS}" font-size="8.6" font-weight="600" letter-spacing="2.4" fill="{MU}">CHAQUE EXEMPLE S’EXÉCUTE DANS LE NAVIGATEUR</text>')
    o.append(f'<rect x="24" y="24" width="552" height="852" fill="none" stroke="{Y}" stroke-opacity=".22" stroke-width="1"/>')
    o.append(f'<rect width="600" height="900" filter="url(#g{u})"/>')
    return "".join(o)

# ---------------------------------------------------------------------------
# Inside Your House: the book's own cover (a cutaway of a modern house with every system labeled),
# kept as the SVG drawn for the book in books/covers/, with its ids made unique on the page.
def house():
    import re
    from pathlib import Path
    u = _uid()
    src = (Path(__file__).resolve().parent / "books" / "covers" / "inside-your-house.svg").read_text(encoding="utf-8")
    src = re.sub(r"<title>.*?</title>", "", src, flags=re.S)
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    body = re.sub(r"^.*?<svg[^>]*>", "", src, count=1, flags=re.S).rsplit("</svg>", 1)[0]
    for i in sorted(set(re.findall(r'id="([^"]+)"', body)), key=len, reverse=True):
        body = body.replace(f'id="{i}"', f'id="{u}{i}"').replace(f"url(#{i})", f"url(#{u}{i})")
    return f'<svg x="0" y="0" width="600" height="900" viewBox="{vb}" preserveAspectRatio="xMidYMid slice">{body}</svg>'

COVERS = {"richesse-silencieuse": richesse, "la-richesse-silencieuse": richesse, "capital-entrave": capital, "le-capital-entrave": capital, "camera-au-poing": camera, "monnaie-terre-merite": monnaie, "la-monnaie-la-terre-et-le-merite": monnaie, "yeux-ouverts": yeux, "les-yeux-ouverts": yeux, "tout-est-code": code, "inside-your-house": house}

def cover_svg(seed):
    fn = COVERS.get(seed)
    if not fn: return None
    return f'<svg class="cover-art cover-custom" viewBox="0 0 600 900" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Couverture">{fn()}</svg>'
