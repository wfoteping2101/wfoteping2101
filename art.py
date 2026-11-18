#!/usr/bin/env python3
"""Background artwork for the site: an engraved astrolabe and an orbital diagram.

Writes assets/art/astrolabe-{ink,paper}.svg and assets/art/orbits-{ink,paper}.svg.
The drawings are line engravings in one colour; the stylesheet sets their opacity.
Run: python3 art.py
"""
import math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "art")
INK, PAPER, RED = "#1B1A17", "#EFE6D2", "#C8553A"


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def circle(cx, cy, r, w, dash=None, op=1):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op != 1 else ""
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="none" stroke-width="{w}"{d}{o}/>'


def engraved_sphere(cx, cy, R, n, light=(-0.45, -0.55, 0.70)):
    """A sphere shaded with vertical engraved lines whose width follows the light."""
    ln = math.sqrt(sum(c * c for c in light)); L = tuple(c / ln for c in light)
    s = 2 * R / n; out = []
    for i in range(n):
        x = cx - R + s * (i + 0.5); dx = (x - cx) / R
        if abs(dx) >= 1: continue
        h = math.sqrt(1 - dx * dx); y0, y1 = cy - h * R, cy + h * R
        tp = max(0.2 * R * h, 3); steps = max(8, int((y1 - y0) / 2)); run = []
        def flush():
            if len(run) > 1:
                pts = [(x - w, y) for y, w in run] + [(x + w, y) for y, w in reversed(run)]
                out.append('<path d="M' + " L".join(f"{f(a)} {f(b)}" for a, b in pts) + ' Z"/>')
            run.clear()
        for j in range(steps + 1):
            y = y0 + (y1 - y0) * j / steps; dy = (y - cy) / R
            z = max(0.0, 1 - dx * dx - dy * dy) ** 0.5
            lit = max(0.0, dx * L[0] + dy * L[1] + z * L[2])
            w = 0.5 * 0.82 * s * (0.16 + 0.84 * (1 - lit) ** 1.3)
            e = min(y - y0, y1 - y)
            if e < tp: w *= (max(e, 0) / tp) ** 0.7
            if w < 0.05 * s: flush(); continue
            run.append((y, w))
        flush()
    return "".join(out)


def astrolabe(col):
    cx = cy = 600
    g = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1200" width="1200" height="1200"><g fill="none" stroke="{col}" stroke-linecap="round">']
    # limb: rings and degree scale
    for r, w in ((574, 2.2), (560, 1), (532, 1), (516, 2)):
        g.append(circle(cx, cy, r, w))
    for d in range(360):
        a = math.radians(d - 90)
        r0, r1, w = (560, 574, 1.4) if d % 10 == 0 else ((560, 569, 1) if d % 5 == 0 else (560, 565, .6))
        g.append(f'<path d="M{f(cx + r0 * math.cos(a))} {f(cy + r0 * math.sin(a))} L{f(cx + r1 * math.cos(a))} {f(cy + r1 * math.sin(a))}" stroke-width="{w}"/>')
    # stereographic plate: almucantars (circles of equal altitude) and azimuth arcs
    g.append('<defs><clipPath id="plate"><circle cx="600" cy="600" r="516"/></clipPath></defs><g clip-path="url(#plate)">')
    # stereographic projection for latitude 35 degrees, equator radius Re
    phi, Re = math.radians(35), 236
    for k in range(0, 90, 6):
        h = math.radians(k)
        yc = Re * math.cos(phi) / (math.sin(phi) + math.sin(h))
        r = Re * math.cos(h) / (math.sin(phi) + math.sin(h))
        g.append(circle(cx, cy - yc, r, 1.5 if k % 18 == 0 else .8))
    zen = Re * math.cos(phi) / (1 + math.sin(phi))              # zenith point
    for k in range(-8, 9):
        if k == 0: continue
        a = math.radians(k * 11)
        # azimuth circles pass through the zenith and the nadir; centres lie on a horizontal line
        ny = Re * math.cos(phi) / (math.sin(phi) - 1)            # nadir (negative: below centre in this frame)
        mid = (zen + ny) / 2; half = (zen - ny) / 2
        xc = half * math.tan(a); r = half / math.cos(a)
        g.append(circle(cx + xc, cy - mid, abs(r), .7, dash="2 7"))
    g.append(f'<path d="M{cx} 84 L{cx} 1116 M84 {cy} L1116 {cy}" stroke-width="1"/>')
    g.append(circle(cx, cy, 236, 1.2)); g.append(circle(cx, cy, 412, 1.2))
    g.append(circle(cx, cy - 64, 330, 1.6))                     # ecliptic, eccentric
    for d in range(0, 360, 6):                                   # ecliptic graduation
        a = math.radians(d); r0, r1 = 330, 330 + (14 if d % 30 == 0 else 7)
        g.append(f'<path d="M{f(cx + r0 * math.cos(a))} {f(cy - 64 + r0 * math.sin(a))} L{f(cx + r1 * math.cos(a))} {f(cy - 64 + r1 * math.sin(a))}" stroke-width=".8"/>')
    g.append('</g>')
    # rule (alidade) across the face
    a = math.radians(-28)
    g.append(f'<path d="M{f(cx - 540 * math.cos(a))} {f(cy - 540 * math.sin(a))} L{f(cx + 540 * math.cos(a))} {f(cy + 540 * math.sin(a))}" stroke-width="3.2"/>')
    g.append(circle(cx, cy, 14, 2)); g.append(circle(cx, cy, 4, 2))
    # star pointers on the rete
    rnd = random.Random(1486)
    stars = []
    for _ in range(14):
        r = rnd.uniform(150, 480); t = rnd.uniform(0, 2 * math.pi)
        stars.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    for x, y in stars:
        g.append(f'<path d="M{f(x - 7)} {f(y)} L{f(x + 7)} {f(y)} M{f(x)} {f(y - 7)} L{f(x)} {f(y + 7)}" stroke-width="1.1"/>')
    g.append('</g>')
    g.append(f'<g fill="{col}">' + "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="2.6"/>' for x, y in stars) + '</g>')
    # degree numerals on the limb
    g.append(f'<g fill="{col}" font-family="Georgia, \'Times New Roman\', serif" font-size="15" text-anchor="middle">')
    for d in range(0, 360, 30):
        a = math.radians(d - 90); r = 545
        g.append(f'<text x="{f(cx + r * math.cos(a))}" y="{f(cy + r * math.sin(a) + 5)}" transform="rotate({d} {f(cx + r * math.cos(a))} {f(cy + r * math.sin(a))})">{d}</text>')
    g.append('</g></svg>')
    return "".join(g)


def orbits(col):
    cx, cy, R = 470, 470, 150
    g = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 940" width="940" height="940">']
    g.append(f'<g fill="{col}">{engraved_sphere(cx, cy, R, 25)}</g>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="{R + 6}" fill="none" stroke="{col}" stroke-width="1"/>')
    g.append(f'<g fill="none" stroke="{col}" stroke-linecap="round">')
    for rx, ry, rot, w, dash in ((330, 82, -16, 1.6, None), (410, 120, -16, 1, "3 9"), (250, 250, 0, .8, "1 8"), (440, 440, 0, .8, None)):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        g.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" transform="rotate({rot} {cx} {cy})" stroke-width="{w}"{d}/>')
    # construction geometry: inscribed triangle and bisectors, as in a Renaissance drawing sheet
    pts = [(cx + 440 * math.cos(math.radians(a)), cy + 440 * math.sin(math.radians(a))) for a in (-90, 30, 150)]
    g.append('<path d="M' + " L".join(f"{f(x)} {f(y)}" for x, y in pts) + ' Z" stroke-width=".7" stroke-dasharray="6 6"/>')
    for x, y in pts:
        g.append(f'<path d="M{f(x)} {f(y)} L{f(2 * cx - x)} {f(2 * cy - y)}" stroke-width=".5" stroke-dasharray="1 6"/>')
    g.append('</g>')
    # bodies on the orbits: one in red, the others in the line colour
    t = math.radians(-16)
    def on_ellipse(rx, ry, ang):
        x, y = rx * math.cos(ang), ry * math.sin(ang)
        return cx + x * math.cos(t) - y * math.sin(t), cy + x * math.sin(t) + y * math.cos(t)
    x1, y1 = on_ellipse(330, 82, math.radians(-20))
    x2, y2 = on_ellipse(410, 120, math.radians(200))
    g.append(f'<circle cx="{f(x1)}" cy="{f(y1)}" r="13" fill="{RED}"/>')
    g.append(f'<circle cx="{f(x2)}" cy="{f(y2)}" r="9" fill="{col}"/>')
    rnd = random.Random(1543)
    g.append(f'<g fill="{col}">' + "".join(f'<circle cx="{f(rnd.uniform(20, 920))}" cy="{f(rnd.uniform(20, 920))}" r="{f(rnd.uniform(.8, 2.2))}"/>' for _ in range(60)) + '</g>')
    g.append('</svg>')
    return "".join(g)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, col in (("ink", INK), ("paper", PAPER)):
        open(os.path.join(OUT, f"astrolabe-{name}.svg"), "w").write(astrolabe(col))
        open(os.path.join(OUT, f"orbits-{name}.svg"), "w").write(orbits(col))
    print("art written to", OUT)
