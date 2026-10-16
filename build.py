#!/usr/bin/env python3
"""Builds the static site into dist/. Run: python3 build.py"""
import os, re, shutil, json, html, datetime, hashlib
import content as C
from guides import GUIDES
import fr as FR
import salon as SALON

READING = SALON.available()  # books whose table of contents is present; their text lives in the protected backend
from covers import cover_svg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
E = html.escape

def t(en, fr):
    """Bilingual inline text: English shown, French swapped in by the toggle."""
    return f'<span data-fr="{E(fr, quote=True)}">{E(en)}</span>'

def frp(slug): return FR.PROJECTS.get(slug, {})
def frb(slug): return FR.BOOKS.get(slug, {})
def frs(slug): return FR.SERVICES.get(slug, {})
def frj(slug): return FR.JOURNAL.get(slug, {})
def frg(slug): return FR.GUIDES.get(slug, {})
def tf(en, d, key, i=None, j=None):
    """t() with a French value looked up in dict d[key] (optionally indexed)."""
    v = d.get(key)
    try:
        if v is not None and i is not None: v = v[i]
        if v is not None and j is not None: v = v[j]
    except (IndexError, KeyError, TypeError): v = None
    return t(en, v) if v else E(en)

THREE = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" defer></script><script src="/assets/scenes.js" defer></script>'

def cover_art(seed, color, ink):
    """An original generative motif per cover: concentric arcs, a rose of lines, or a field of dots, seeded by the slug."""
    custom = cover_svg(seed)
    if custom: return custom
    import random
    rnd = random.Random(seed); kind = rnd.choice(["rose", "arcs", "field", "weave"]); out = []
    if kind == "rose":
        n = rnd.choice([8, 12, 16]); out.append(f'<g transform="translate(100 150)" fill="none" stroke="{ink}" stroke-opacity=".55" stroke-width="1.2">' + "".join(f'<ellipse rx="22" ry="{rnd.randint(55,80)}" transform="rotate({360*i/n})"/>' for i in range(n)) + f'<circle r="{rnd.randint(8,14)}" fill="{ink}" fill-opacity=".9" stroke="none"/></g>')
    elif kind == "arcs":
        out.append(f'<g fill="none" stroke="{ink}" stroke-opacity=".5" stroke-width="1.3">' + "".join(f'<path d="M -20 {300 - i*22} Q 100 {120 - i*18} 220 {300 - i*22}"/>' for i in range(9)) + '</g>')
    elif kind == "field":
        out.append(f'<g fill="{ink}" fill-opacity=".55">' + "".join(f'<circle cx="{18 + (i%9)*20.5}" cy="{70 + (i//9)*20}" r="{1.2 + rnd.random()*2.6}"/>' for i in range(81)) + '</g>')
    else:
        out.append(f'<g fill="none" stroke="{ink}" stroke-opacity=".45" stroke-width="1">' + "".join(f'<path d="M 0 {40 + i*26} C 60 {20 + i*26}, 140 {60 + i*26}, 200 {40 + i*26}"/>' for i in range(10)) + "".join(f'<path d="M {20 + i*26} 0 C {0 + i*26} 100, {40 + i*26} 200, {20 + i*26} 300"/>' for i in range(8)) + '</g>')
    return f'<svg class="cover-art" viewBox="0 0 200 300" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><rect width="200" height="300" fill="{color}"/>{"".join(out)}</svg>'

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap">'

NAV = [("/", "Home", "Accueil", "home"), ("/portfolio", "Portfolio", "Portfolio", "portfolio"), ("/books", "Books", "Livres", "books"), ("/gallery", "Gallery", "Galerie", "gallery"), ("/journal", "Journal", "Journal", "journal"), ("/services", "Services", "Services", "services"), ("/contact", "Contact", "Contact", "contact")]

def head(title, desc, path, extra=""):
    full = f"{title} | {C.SITE['name']}" if title else C.SITE["name"]
    url = C.SITE["url"] + path
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(full)}</title><meta name="description" content="{E(desc, quote=True)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{E(full, quote=True)}"><meta property="og:description" content="{E(desc, quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:image" content="{C.SITE['url']}/assets/og.png"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><meta name="theme-color" content="#F6F2EA"><meta name="robots" content="noai, noimageai">
<script src="/assets/guard.js" defer></script><script src="/assets/track.js" defer></script>
{FONTS}<link rel="stylesheet" href="/assets/style.css">{extra}</head><body data-email="{E(C.SITE['email'], quote=True)}"><a class="skip" href="#main">Skip to content</a>"""

def header(active):
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{t(en, fr)}</a>' for h, en, fr, k in NAV)
    return f"""<header class="top"><div class="wrap"><a class="brand" href="/"><i></i>{E(C.SITE['name'])}</a>
<nav class="nav" id="nav" aria-label="Main">{links}</nav>
<div class="tools"><button class="pill lang" data-lang="en" aria-pressed="true">EN</button><button class="pill lang" data-lang="fr" aria-pressed="false">FR</button><button class="pill theme" aria-label="Toggle theme">DARK</button><button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 5h14M2 9h14M2 13h14"/></svg></button></div></div></header><main id="main">"""

def footer():
    y = datetime.date.today().year
    work = "".join(f'<a href="/portfolio/{p["slug"]}">{E(p["title"])}</a>' for p in C.PROJECTS[:6]) + f'<a href="/portfolio">{t("All platforms", "Toutes les plateformes")}</a>'
    return f"""</main><footer><div class="wrap"><div><div class="tag">{E(C.SITE['name'])}</div><p>{t('Network engineering, software platforms, books and video.', 'Réseaux, plateformes logicielles, livres et vidéo.')}</p><p>{t('Maryland, United States. French and English.', 'Maryland, États-Unis. Français et anglais.')}</p><p><a href="mailto:{E(C.SITE['email'])}">{E(C.SITE['email'])}</a></p></div>
<div><h4>Portfolio</h4>{work}</div>
<div><h4>{t('Site', 'Site')}</h4><a href="/books">{t('Books', 'Livres')}</a><a href="/gallery">{t('Gallery', 'Galerie')}</a><a href="/journal">Journal</a><a href="/services">Services</a><a href="/contact">Contact</a><p style="margin-top:14px">&copy; {y} {E(C.SITE['name'])}</p><p class="privacy-note">{t('Anonymous visit statistics. No cookies, no ads.', 'Statistiques de visite anonymes. Pas de cookies, pas de publicité.')}</p></div></div></footer>
<script src="/assets/app.js" defer></script></body></html>"""

def plabel(p):
    return f'<span class="label"><b>N° {E(p["n"])}</b><span>{tf(p["kind"], frp(p["slug"]), "kind")}</span><span>{E(p["year"])}</span></span>'

def stage(p):
    beats = E(json.dumps(p["beats"], ensure_ascii=False), quote=True)
    return f"""<div class="stage" data-beats="{beats}" style="--bk:{p['color']};--bk-ink:{p['ink']}" role="img" aria-label="{E(p['title'], quote=True)}, animated summary"><svg viewBox="0 0 600 340" preserveAspectRatio="xMidYMid meet" aria-hidden="true"><path class="shape" d=""/></svg><span class="meta" data-base="{E(p['title'], quote=True)}">{E(p['title'])}</span><div class="ctl"><button class="play-btn" type="button">PAUSE</button></div><div class="line"></div><div class="bar"></div></div>"""

def visit_link(p, cls="pc-visit"):
    if not p["url"]: return ""
    return f'<a class="{cls}" href="{E(p["url"])}" target="_blank" rel="noopener">{t("Visit", "Visiter")} &#8599;</a>'

def platform_card(p):
    f = frp(p["slug"]); s = p["slug"]
    return f"""<article class="card pcard rv"><a class="pc-shot" href="/portfolio/{s}" tabindex="-1" aria-hidden="true"><figure class="shot" style="margin:0"><img src="/assets/shots/{p['shot']}.webp" alt="" loading="lazy"></figure></a>{plabel(p)}<h3><a href="/portfolio/{s}">{E(p['title'])}</a></h3><p style="margin:0;color:var(--encre)">{tf(p['line'], f, 'line')}</p><p class="mono muted" style="margin:0;font-size:12px">{tf(p['status'], f, 'status')}</p><p class="pc-links"><a href="/portfolio/{s}">{t('Details', 'Détails')} &rarr;</a><a href="/guides/{s}">{t('How to use', 'Mode d’emploi')} &rarr;</a>{visit_link(p)}</p></article>"""

def hero_art():
    return """<div class="glass rv" aria-hidden="true"><canvas id="hero-canvas"></canvas><svg class="glass-fallback" viewBox="0 0 400 300" fill="none" stroke="currentColor" stroke-width="1.2" style="color:#1C3FBF">
<g opacity=".55"><path d="M40 260 L200 40 L360 260 Z"/><path d="M200 40 V260"/><path d="M120 150 H280"/><path d="M80 205 H320"/></g>
<g opacity=".8" stroke="#B8933F"><circle cx="200" cy="150" r="70"/><circle cx="200" cy="150" r="46"/><path d="M130 150 H270 M200 80 V220"/></g>
<g opacity=".5"><path d="M20 290 H380" /><path d="M60 120 Q200 -20 340 120" /></g></svg></div>"""

# ---------------------------------------------------------------------------
def page_home():
    posts = C.JOURNAL[:3]
    n = len(C.PROJECTS)
    stats = [(str(n), "Platforms", "Plateformes"), (str(len(C.BOOKS)), "Books", "Livres"), (str(len(C.MOTION) + len(C.EDITS)), "Videos", "Vidéos"), (str(len(READING)), "Free to read", "À lire gratuitement")]
    body = f"""<section class="hero wrap"><div class="hero-grid"><div>
<span class="label rv"><b>Portfolio</b><span>{t(C.SITE['location'], 'Maryland, États-Unis')}</span></span>
<h1 class="name rv" style="margin:18px 0 20px">William<br><em>Foteping</em></h1>
<p class="lede rv">{t(C.SITE['tagline_en'], C.SITE['tagline_fr'])}</p>
<p class="cta-row rv"><a class="btn" href="/portfolio">{t('View the portfolio', 'Voir le portfolio')}</a><a class="btn ghost" href="/services">{t('Services and prices', 'Services et tarifs')}</a></p></div>
<div>{hero_art()}<div class="hero-aside rv"><div class="kv"><span>{t('Trade', 'Métier')}</span><span>{t('Senior network administrator, cloud and infrastructure', 'Administrateur réseau senior, cloud et infrastructure')}</span></div><div class="kv"><span>{t('Temperament', 'Tempérament')}</span><span>{t('Serial entrepreneur, hobby entrepreneur, and I love it', 'Entrepreneur en série, entrepreneur par passion, et j’adore ça')}</span></div><div class="kv"><span>{t('Ventures', 'Projets')}</span><span>Uplink IT Academy, Bobine, Lemon Network Solutions, Droit Facile, Peel, Zeste</span></div><div class="kv"><span>{t('Writing', 'Écriture')}</span><span>{t('Essays and a novel in French, technical books in English', 'Essais et roman en français, livres techniques en anglais')}</span></div><div class="kv"><span>{t('Certifications', 'Certifications')}</span><span>Cisco CCNA, Microsoft Azure Administrator (AZ-104)</span></div></div></div></div></section>
<div class="wrap"><div class="stats rv">{"".join(f'<div class="stat"><b>{v}</b><span>{t(en, fr)}</span></div>' for v, en, fr in stats)}</div></div>

<section class="block wrap" id="portfolio"><div class="sec-head"><span class="label rv"><b>01</b><span>Portfolio</span></span><div class="row rv"><h2>{t('Platforms I designed and built.', 'Plateformes que j’ai conçues et construites.')}</h2><a class="btn ghost small" href="/portfolio">{t(f'All {n} platforms', f'Les {n} plateformes')} &rarr;</a></div></div><div class="grid g3">{"".join(platform_card(p) for p in C.PROJECTS[:6])}</div></section>

<section class="block wrap"><div class="sec-head"><span class="label rv"><b>02</b><span>{t('Books', 'Livres')}</span></span><div class="row rv"><h2>{t('Essays, a novel and technical books.', 'Essais, roman et livres techniques.')}</h2><a class="btn ghost small" href="/books">{t('All books', 'Tous les livres')} &rarr;</a></div></div>
<div class="bookcase rv">{"".join(tome(b) for b in C.BOOKS[:3])}</div></section>

<section class="block wrap"><div class="sec-head"><span class="label rv"><b>03</b><span>{t('Gallery', 'Galerie')}</span></span><div class="row rv"><h2>{t('Motion design and video edits.', 'Motion design et montages vidéo.')}</h2><a class="btn ghost small" href="/gallery">{t('Open the gallery', 'Ouvrir la galerie')} &rarr;</a></div></div>
<div class="grid g3 rv">{vcard(C.MOTION[0])}{vcard(C.MOTION[1])}{vcard(C.EDITS[12])}</div></section>

<section class="block wrap"><div class="sec-head"><span class="label rv"><b>04</b><span>Journal</span></span><div class="row rv"><h2>{t('Practical advice drawn from the books.', 'Des conseils pratiques, tirés des livres.')}</h2><a class="btn ghost small" href="/journal">{t('All posts', 'Tous les articles')} &rarr;</a></div></div>
<div class="posts rv">{"".join(post_row(p) for p in posts)}</div></section>

<section class="block wrap"><div class="card rv" style="padding:clamp(24px,4vw,44px);gap:16px"><span class="label"><b>05</b><span>Services</span></span><h2>{t('Work with me.', 'Travailler avec moi.')}</h2><p class="lede">{t('Platforms, networks, books, video and content systems, in French and English. Prices are published; every project starts with a brief and a written quote.', 'Plateformes, réseaux, livres, vidéo et systèmes de contenu, en français et en anglais. Les prix sont affichés ; chaque projet commence par un brief et un devis écrit.')}</p><p class="cta-row"><a class="btn cobalt" href="/services">{t('Services and prices', 'Services et tarifs')}</a><a class="btn ghost" href="/services#brief">{t('Send a brief', 'Envoyer un brief')}</a></p></div></section>"""
    return head("", C.SITE["description"], "/", THREE) + header("home") + body + footer()

def tome(b, is_album=False):
    f = FR.ALBUM if is_album else frb(b["slug"])
    where_en = b["where"]; where_fr = f.get("where", where_en)
    where = "".join(f'<a class="btn {"cobalt" if u.startswith("/lire/") else "ghost"} small" href="{E(u)}"{"" if u.startswith("/") else " target=\"_blank\" rel=\"noopener\""}>{t(l, (where_fr[i][0] if i < len(where_fr) else l))} &rarr;</a>' for i, (l, u) in enumerate(where_en))
    pages = f'<div><span class="k">Format</span> {tf(b["pages"], f, "pages")}</div>' if b.get("pages") else ""
    by = E(b["artist"]) if is_album else E(C.SITE["name"])
    top = E(b["lang"].upper()) if not is_album else "WFOSS"
    year = t(b["year"], "En cours") if b["year"] == "In progress" else E(b["year"])
    return f"""<article class="tome"><div class="cover art" style="--bk:{b['color']};--bk-ink:{b['ink']}">{cover_art(b['slug'], b['color'], b['ink'])}<span class="bn">{top}</span><span class="bt">{E(b['title'])}</span><span class="by">{by}</span><span class="bk">{tf(b['kind'], f, 'kind')}<br>{year}</span></div>
<div class="meta"><h3 style="font-size:22px">{E(b['title'])}</h3><p style="margin:4px 0 6px;font-size:15px;color:var(--encre)">{tf(b['line'], f, 'line')}</p>{pages}{('<div class="cta-row" style="margin-top:6px">' + where + '</div>') if where else ''}</div></article>"""

def vcard(v):
    first = v["variants"][0]
    ti, li = v["fr"] if v.get("fr") else (None, None)
    kind = t(v["kind"], "Montage de démonstration, une minute") if v["kind"].startswith("Demo edit") else E(v["kind"])
    vars_ = "".join(f'<button type="button" data-src="{E(u, quote=True)}" data-ratio="{E(r, quote=True)}" aria-pressed="{"true" if i == 0 else "false"}">{E(l)}</button>' for i, (l, u, r) in enumerate(v["variants"]))
    return f"""<article class="vcard" data-src="{E(first[1], quote=True)}" data-ratio="{E(first[2], quote=True)}" data-poster="{E(v['poster'], quote=True)}"><div class="media"><img src="{E(v['poster'])}" alt="{E(v['title'], quote=True)}" loading="lazy"><button class="play" type="button" aria-label="Play {E(v['title'], quote=True)}"><span><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span></button></div>
<div class="body"><span class="label"><b>{kind}</b><span>{E(v['year'])}</span></span><h3 style="font-size:22px">{t(v['title'], ti) if ti else E(v['title'])}</h3><p style="margin:0;font-size:14px;color:var(--encre)">{t(v['line'], li) if li else E(v['line'])}</p><div class="vars">{vars_}</div></div></article>"""

MONTHS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
def date_t(iso, long=False):
    d = datetime.date.fromisoformat(iso)
    en = d.strftime("%d %B %Y" if long else "%d %b %Y")
    fr = f"{d.day} {MONTHS_FR[d.month - 1]} {d.year}"
    return t(en, fr)

def asset_v(rel):
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel)
    return hashlib.sha1(open(f, "rb").read()).hexdigest()[:8] if os.path.exists(f) else "0"

def art_src(p): return "/" + p["thumb"] + "?v=" + asset_v(p["thumb"])

def post_row(p):
    return f"""<article class="post" lang="fr"><a class="th" href="/journal/{p['slug']}" tabindex="-1" aria-hidden="true"><img src="{art_src(p)}" alt="" loading="lazy" width="900" height="675"></a><div><span class="cat"><i style="background:{p['color']}"></i>{FE(p['cat'])}</span> <span class="date">{date_t(p['date'])}</span><h3><a href="/journal/{p['slug']}">{FE(p['title'])}</a></h3><p class="lede">{FE(p['lede'])}</p><a class="btn ghost small" href="/journal/{p['slug']}">Lire &rarr;</a></div></article>"""

def typo(x):
    """French typography: curly apostrophes, thin no-break spaces before high punctuation and inside guillemets."""
    x = x.replace("'", "\u2019")
    for a, b in ((" :", "\u00a0:"), (" ;", "\u202f;"), (" ?", "\u202f?"), (" !", "\u202f!"), ("« ", "«\u202f"), (" »", "\u202f»")): x = x.replace(a, b)
    return x

def FE(x): return E(typo(x))

def inline(x):
    x = FE(x)
    x = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", x)
    return re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", x)

def prose(blocks):
    out = []
    for b in blocks:
        if b.startswith("## "): out.append(f"<h2>{inline(b[3:])}</h2>")
        elif b.startswith("> "): out.append(f"<blockquote><p>{inline(b[2:])}</p></blockquote>")
        elif b.startswith("- "): out.append("<ul>" + "".join(f"<li>{inline(l[2:])}</li>" for l in b.split("\n")) + "</ul>")
        else: out.append(f"<p>{inline(b)}</p>")
    return "".join(out)

# ---------------------------------------------------------------------------
def page_portfolio():
    live = [p for p in C.PROJECTS if p["url"]]; private = [p for p in C.PROJECTS if not p["url"]]
    n = len(C.PROJECTS)
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>Portfolio</b><span>{t(f'{n} platforms', f'{n} plateformes')}</span></span><h1 class="rv" style="margin:16px 0 14px">Portfolio.</h1><p class="lede rv">{t('Software platforms I designed and built, in IT training, video, networking, law, publishing, real estate and security. Each page covers the problem, the features and the technology, with a guided tour of the real screens.', 'Des plateformes logicielles que j’ai conçues et construites : formation IT, vidéo, réseaux, droit, édition, immobilier et sécurité. Chaque page présente le problème, les fonctions et la technique, avec une visite guidée des vrais écrans.')}</p></section>
<section class="block wrap" style="padding-top:10px"><div class="sec-head"><span class="label rv"><b>{t('Live', 'En ligne')}</b><span>{len(live)}</span></span></div><div class="grid g3">{"".join(platform_card(p) for p in live)}</div></section>
<section class="block wrap" style="padding-top:0"><div class="sec-head"><span class="label rv"><b>{t('Private', 'Privé')}</b><span>{len(private)}</span></span><p class="muted rv" style="margin:0">{t('Not public. Walkthrough on request.', 'Non publiques. Démonstration sur demande.')}</p></div><div class="grid g3">{"".join(platform_card(p) for p in private)}</div></section>"""
    return head("Portfolio", "Software platforms designed and built by William Foteping.", "/portfolio") + header("portfolio") + body + footer()

def page_project(p, prev, nxt):
    f = frp(p["slug"])
    secs = "".join(f'<div class="chapter rv"><span class="ch">{str(i + 1).zfill(2)}</span><div><h3>{tf(h, f, "sections", i, 0)}</h3><p>{tf(x, f, "sections", i, 1)}</p></div></div>' for i, (h, x) in enumerate(p["sections"]))
    facts = "".join(f'<div><span>{tf(k, f, "facts", i, 0)}</span><span>{tf(v, f, "facts", i, 1)}</span></div>' for i, (k, v) in enumerate(p["facts"]))
    visit = f'<a class="btn" href="{E(p["url"])}" target="_blank" rel="noopener">{t("Visit the site", "Voir le site")} &#8599;</a>' if p["url"] else f'<span class="notice">{t("Private. Walkthrough on request at", "Privé. Démonstration sur demande à")} {E(C.SITE["email"])}.</span>'
    m = len(p["sections"]) + 1
    body = f"""<section class="block wrap"><div class="open">
<aside><div class="facts" style="border-top:6px solid {p['color']};padding-top:6px;margin-top:0">{facts}<div><span>Stack</span><span>{E(p['stack'])}</span></div><div><span>{t('Status', 'Statut')}</span><span>{tf(p['status'], f, 'status')}</span></div>{f'<div><span>{t("Link", "Lien")}</span><span><a href="{E(p["url"])}" target="_blank" rel="noopener">{tf(p["link_label"], f, "link_label")}</a></span></div>' if p["url"] else ''}</div></aside>
<div>{plabel(p)}<h1 class="rv" style="margin:14px 0 12px;font-size:clamp(36px,5.5vw,72px)">{E(p['title'])}</h1><p class="lede rv">{tf(p['line'], f, 'line')}</p><p class="cta-row rv" style="margin:18px 0 34px">{visit}<a class="btn cobalt" href="/guides/{p['slug']}">{t('How to use', 'Mode d’emploi')}</a><a class="btn ghost" href="#motion">{t('In motion', 'En mouvement')}</a></p>
<figure class="shot rv"><img src="/assets/shots/{p['shot']}.webp" alt="{E(p['title'], quote=True)}, screenshot"><figcaption>{E(p['title'])}, {t('screenshot', 'capture d’écran')}</figcaption></figure>
<div class="chapters" style="margin-top:40px">{secs}
<div class="chapter rv" id="motion"><span class="ch">{str(m).zfill(2)}</span><div><h3>{t('In motion', 'En mouvement')}</h3><p style="margin-bottom:14px">{t('Four frames that summarize the platform. Click to advance.', 'Quatre plans qui résument la plateforme. Cliquez pour avancer.')}</p>{stage(p)}</div></div></div>
<nav class="cta-row" style="margin-top:48px;justify-content:space-between" aria-label="Platforms"><a class="btn ghost small" href="/portfolio/{prev['slug']}">&larr; {E(prev['title'])}</a><a class="btn ghost small" href="/portfolio/{nxt['slug']}">{E(nxt['title'])} &rarr;</a></nav></div></div></section>"""
    return head(p["title"], p["line"], f"/portfolio/{p['slug']}") + header("portfolio") + body + footer()

def salon_card(b):
    f = frb(b["slug"])
    if b["free"]:
        cta = f'<a class="btn cobalt small" href="/lire/{b["free"]}">{t("Read online", "Lire en ligne")} &rarr;</a>'
    else:
        cta = f'<span class="notice">{t("In progress. Free to read here when published.", "En cours d’écriture. Lisible gratuitement ici à sa parution.")}</span>'
    return f"""<article class="card salon-card" style="--bk:{b['color']};--bk-ink:{b['ink']}"><div class="cover art mini" style="--bk:{b['color']};--bk-ink:{b['ink']}">{cover_art(b['slug'], b['color'], b['ink'])}<span class="bt">{E(b['title'])}</span><span class="by">{E(C.SITE['name'])}</span></div><div><span class="label"><b data-free-slug="{E(b['free'])}">{t('Free', 'Gratuit')}</b><span>{tf(b['kind'], f, 'kind')}</span></span><h3 style="font-size:22px;margin:8px 0">{E(b['title'])}</h3><p style="margin:0 0 12px;font-size:15px;color:var(--encre)">{tf(b['line'], f, 'line')}</p>{cta}</div></article>"""

def page_books():
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>{t('Books', 'Livres')}</b><span>{len(C.BOOKS)} {t('titles', 'titres')}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('Books.', 'Livres.')}</h1><p class="lede rv">{t('Essays and a novel in French, technical books in English, and a document format I use with clients.', 'Essais et roman en français, livres techniques en anglais, et un format de document utilisé avec mes clients.')}</p></section>
<section class="block wrap" style="padding-top:10px" id="salon"><div class="sec-head"><span class="label rv"><b>{t('Read online', 'Lecture en ligne')}</b><span>{t('Free', 'Gratuit')}</span></span><div class="row rv"><h2>{t('Free to read online.', 'À lire gratuitement en ligne.')}</h2></div><p class="lede rv">{t('Each book is free for a set period: the full text, chapter by chapter, with optional background music generated in your browser. Reading is online only; download and printing are disabled.', 'Chaque livre est gratuit pendant une période donnée : le texte intégral, chapitre par chapitre, avec une musique de fond facultative générée dans le navigateur. La lecture se fait en ligne uniquement ; téléchargement et impression sont désactivés.')}</p></div>
<div class="grid g3 rv">{"".join(salon_card(b) for b in C.BOOKS if b.get("free"))}</div></section>
<section class="block wrap" style="padding-top:10px"><div class="sec-head"><span class="label rv"><b>{t('All titles', 'Tous les titres')}</b></span></div><div class="bookcase">{"".join(tome(b) for b in C.BOOKS)}</div></section>
<section class="block wrap" style="padding-top:0"><div class="sec-head"><span class="label rv"><b>{t('Music', 'Musique')}</b></span><h2 class="rv">{t('Music for film.', 'Musique pour l’image.')}</h2></div><div class="bookcase">{tome(C.ALBUM, True)}</div></section>
<section class="block wrap"><div class="card rv" style="padding:clamp(24px,4vw,40px)"><h2 style="font-size:clamp(26px,3vw,38px)">{t('Book production', 'Production de livres')}</h2><p class="lede">{t('Editing, layout, figures, cover, print-ready PDF and ebook, in French or English.', 'Édition, mise en page, figures, couverture, PDF prêt à imprimer et livre numérique, en français ou en anglais.')}</p><p class="cta-row"><a class="btn" href="/services#books">{t('See the service', 'Voir le service')} &rarr;</a></p></div></section>"""
    return head("Books", "Books by William Foteping, several free to read online.", "/books", '<script src="/assets/live.js" defer></script>') + header("books") + body + footer()

def page_gallery():
    motion = "".join(vcard(v) for v in C.MOTION)
    edits = "".join(vcard(v) for v in C.EDITS)
    films = '<div class="grid g2" style="margin-top:18px">' + "".join(f'<a class="card film-card" href="{E(u)}" target="_blank" rel="noopener"><figure class="shot" style="margin:0 0 8px"><img src="/assets/shots/{sh}.webp" alt="" loading="lazy"></figure><span class="label"><b>{t(k, kf)}</b><span>2026</span></span><h3 style="font-size:22px">{t(ti, tif)}</h3><p style="margin:0;font-size:14px;color:var(--encre)">{t(li, lif)}</p><span class="mono" style="color:var(--cobalt)">{t("Open the page", "Ouvrir la page")} &#8599;</span></a>' for u, sh, k, kf, ti, tif, li, lif in FILMS) + '</div>'
    tours = "".join(f'<a class="card" href="/guides/{p["slug"]}#tour" style="gap:8px"><figure class="shot" style="margin:0 0 4px"><img src="/assets/shots/{p["shot"]}.webp" alt="" loading="lazy"></figure>{plabel(p)}<h3 style="font-size:20px">{E(p["title"])}</h3></a>' for p in C.PROJECTS)
    motions = "".join(f'<a class="card" href="/portfolio/{p["slug"]}#motion" style="gap:8px">{plabel(p)}<h3 style="font-size:20px">{E(p["title"])}</h3><p style="margin:0;font-size:14px;color:var(--encre)">{t(p["beats"][0]["t"], p["beats"][0]["fr"])}</p></a>' for p in C.PROJECTS)
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>{t('Gallery', 'Galerie')}</b><span>{t('Video', 'Vidéo')}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('Gallery.', 'Galerie.')}</h1><p class="lede rv">{t('Motion design, demo edits and guided tours of each platform, in 16:9 and 9:16, in French and English where available.', 'Motion design, montages de démonstration et visites guidées de chaque plateforme, en 16:9 et 9:16, en français et en anglais quand ils existent.')}</p></section>
<section class="block wrap regards" style="padding-top:10px" hidden><div class="sec-head"><span class="label rv"><b>{t('Photos', 'Photos')}</b><span>{t('With their stories', 'Avec leur histoire')}</span></span></div><div class="moments" data-regards></div></section>
<section class="block wrap" style="padding-top:10px"><div class="sec-head"><span class="label rv"><b>01</b><span>{t('Motion design', 'Motion design')}</span></span></div><div class="grid g2">{motion}</div>{films}</section>
<section class="block wrap"><div class="sec-head"><span class="label rv"><b>02</b><span>{t('Demo edits', 'Montages de démonstration')}</span><span>{len(C.EDITS)}</span></span><p class="muted" style="margin:0">{t('Edited with Bobine from licensed stock footage. These are demonstrations, not client work.', 'Montés avec Bobine à partir d’images sous licence. Ce sont des démonstrations, pas des travaux clients.')}</p></div><div class="grid g3">{edits}</div></section>
<section class="block wrap"><div class="sec-head"><span class="label rv"><b>03</b><span>{t('Guided tours', 'Visites guidées')}</span></span><p class="muted" style="margin:0">{t('A guided tour of the real screens of each platform.', 'Une visite guidée des vrais écrans de chaque plateforme.')}</p></div><div class="grid g3">{tours}</div></section>
<section class="block wrap"><div class="sec-head"><span class="label rv"><b>04</b><span>{t('Platform animations', 'Animations des plateformes')}</span></span><p class="muted" style="margin:0">{t('Four frames per platform, drawn in the browser.', 'Quatre plans par plateforme, dessinés dans le navigateur.')}</p></div><div class="grid g3">{motions}</div></section>"""
    return head("Gallery", "Motion design, video edits and photos by William Foteping.", "/gallery", '<script src="/assets/live.js" defer></script>') + header("gallery") + body + footer()

def page_journal():
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>Journal</b><span>{len(C.JOURNAL)} {t('posts', 'articles')}</span></span><h1 class="rv" style="margin:16px 0 14px">Journal.</h1><p class="lede rv">{t('Practical advice on the subjects of the books: civic life, land, money, family, video and inheritance. Written in French; each article comes with its own animated piece.', 'Des conseils pratiques sur les sujets des livres : la vie citoyenne, la terre, l’argent, la famille, la vidéo et la transmission. Chaque article a sa propre œuvre animée.')}</p></section>
<section class="block wrap" style="padding-top:10px"><div class="posts">{"".join(post_row(p) for p in C.JOURNAL)}</div></section>"""
    return head("Journal", "Practical advice in French on civic life, land, money, family, video and inheritance.", "/journal") + header("journal") + body + footer()

def page_post(p, prev, nxt):
    sound = f'<button class="btn ghost small sound" type="button" data-sound="{E(p["sound"])}" aria-pressed="false" data-on="{E(p["sound_label"], quote=True)}" data-off="Couper le son"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 10v4h4l5 4V6L8 10H4z"/><path d="M16 9a4 4 0 0 1 0 6"/></svg><span>{E(p["sound_label"])}</span></button>'
    words = sum(len(b.split()) for b in p["body"]); mins = max(1, round(words / 220))
    body = f"""<article class="block wrap post-page" lang="fr"><div class="post-head"><span class="cat rv"><i style="background:{p['color']}"></i>{FE(p['cat'])}</span> <span class="date">{date_t(p['date'], True)} &middot; {mins} min</span><h1 class="rv">{FE(p['title'])}</h1><p class="lede rv">{FE(p['lede'])}</p><p class="cta-row rv" style="margin-top:10px">{sound}<span class="infr" lang="en">{t('Written in French', 'Écrit en français')}</span></p></div>
<div class="scene rv" style="background-image:url({art_src(p)})"><canvas data-scene="{E(p['scene'])}" aria-label="{E(p['title'], quote=True)}, œuvre animée"></canvas></div>
<div class="prose rv centered">{prose(p['body'])}</div>
<nav class="post-nav" aria-label="Articles"><a href="/journal/{prev['slug']}"><span>&larr; Précédent</span><b>{FE(prev['title'])}</b></a><a href="/journal/{nxt['slug']}"><span>Suivant &rarr;</span><b>{FE(nxt['title'])}</b></a></nav></article>"""
    return head(p["title"], p["lede"], f"/journal/{p['slug']}", THREE) + header("journal") + body + footer()

def page_services():
    cards = "".join(f"""<article class="card rv" id="{s['slug']}"><span class="label"><b>{str(i + 1).zfill(2)}</b><span>Service</span></span><h3>{tf(s['name'], frs(s['slug']), 'name')}</h3><p style="margin:0;color:var(--encre)">{tf(s['line'], frs(s['slug']), 'line')}</p><p class="mono muted" style="margin:0"><b style="color:var(--fusain)">{t('Example', 'Exemple')}:</b> {tf(s['example'], frs(s['slug']), 'example')}</p><ul class="ticks">{"".join(f"<li>{tf(d, frs(s['slug']), 'deliverables', k)}</li>" for k, d in enumerate(s['deliverables']))}</ul><div class="foot"><div class="price">{t('from', 'dès')} ${s['from']:,}<small>{tf(s['unit'], frs(s['slug']), 'unit')}</small></div><button class="btn small" type="button" data-pay="{s['slug']}">{t('Pay the deposit', 'Payer l’acompte')} ${s['deposit']:,}</button></div></article>""" for i, s in enumerate(C.SERVICES))
    steps = "".join(f'<div class="step rv"><span class="n">{i + 1}</span><div><h3>{t(h, FR.STEPS[i][0])}</h3><p>{t(d, FR.STEPS[i][1])}</p></div></div>' for i, (h, d) in enumerate(C.STEPS))
    opts = "".join(f'<option>{E(s["name"])}</option>' for s in C.SERVICES) + "<option>Something else</option>"
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>Services</b><span>{t('Prices in US dollars', 'Prix en dollars américains')}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('Services and prices.', 'Services et tarifs.')}</h1><p class="lede rv">{t('Nine services, each with an example, a starting price and a deposit. Every project starts with a brief, a meeting and a written quote.', 'Neuf services, chacun avec un exemple, un prix de départ et un acompte. Chaque projet commence par un brief, un rendez-vous et un devis écrit.')}</p></section>
<section class="block wrap" style="padding-top:10px"><div class="grid g3">{cards}</div><p id="pay-notice" class="notice" hidden style="margin-top:16px"></p></section>

<section class="block wrap" id="how"><div class="sec-head"><span class="label rv"><b>{t('How it works', 'Déroulement')}</b><span>{t('Five steps', 'Cinq étapes')}</span></span><h2 class="rv">{t('From brief to delivery.', 'Du brief à la livraison.')}</h2></div><div class="steps">{steps}</div>
<div class="card rv" style="margin-top:28px;padding:clamp(22px,3vw,34px)"><div class="foot"><div><h3 style="font-size:24px">{t('Consultation, 45 minutes', 'Consultation, 45 minutes')}</h3><p style="margin:6px 0 0;color:var(--encre)">{t('Zoom, Microsoft Teams or Google Meet. Credited to your project if it starts within 30 days.', 'Zoom, Microsoft Teams ou Google Meet. Déduite du projet s’il démarre dans les 30 jours.')}</p></div><div class="cta-row"><span class="price">${C.SITE['consult_price']}</span><button class="btn cobalt" type="button" data-pay="consultation">{t('Reserve and pay', 'Réserver et payer')}</button></div></div></div></section>

<section class="block wrap" id="brief"><div class="sec-head"><span class="label rv"><b>Brief</b><span>{t('Steps 1 and 2', 'Étapes 1 et 2')}</span></span><h2 class="rv">{t('Your brief.', 'Votre brief.')}</h2><p class="lede rv">{t('The form opens your email app with your answers filled in. Then reserve the consultation; I confirm the time within one business day.', 'Le formulaire ouvre votre messagerie avec vos réponses. Réservez ensuite la consultation ; je confirme l’horaire sous un jour ouvré.')}</p></div>
<form class="brief rv" novalidate>
<div class="f2"><div class="fr"><label for="name">{t('Your name', 'Votre nom')}</label><input id="name" name="name" required autocomplete="name"></div><div class="fr"><label for="email">Email</label><input id="email" name="email" type="email" required autocomplete="email"></div></div>
<div class="f2"><div class="fr"><label for="company">{t('Company or project', 'Entreprise ou projet')}</label><input id="company" name="company"></div><div class="fr"><label for="service">Service</label><select id="service" name="service">{opts}</select></div></div>
<div class="fr"><label>{t('Working language', 'Langue de travail')}</label><div class="choices"><label><input type="radio" name="lang" value="English" checked> English</label><label><input type="radio" name="lang" value="Français"> Français</label><label><input type="radio" name="lang" value="Both"> {t('Both', 'Les deux')}</label></div></div>
<div class="fr"><label for="want">{t('What do you need?', 'De quoi avez-vous besoin ?')}</label><textarea id="want" name="want" required placeholder="A learning platform with paid courses and a free sample in each, in French and English."></textarea></div>
<div class="f2"><div class="fr"><label for="goal">{t('Goal', 'Objectif')}</label><textarea id="goal" name="goal" placeholder="Sell 100 seats in the first quarter."></textarea></div><div class="fr"><label for="audience">{t('Audience', 'Public')}</label><textarea id="audience" name="audience" placeholder="Beginners in IT, mostly on phones."></textarea></div></div>
<div class="f2"><div class="fr"><label for="existing">{t('What exists today', 'Ce qui existe déjà')}</label><textarea id="existing" name="existing" placeholder="A logo, twenty videos, a mailing list."></textarea></div><div class="fr"><label for="refs">{t('References (links)', 'Références (liens)')}</label><textarea id="refs" name="refs" placeholder="Two or three sites, books or videos."></textarea></div></div>
<div class="f2"><div class="fr"><label for="budget">{t('Budget range', 'Fourchette de budget')}</label><select id="budget" name="budget"><option>Under 1,000</option><option>1,000 to 3,000</option><option>3,000 to 8,000</option><option>8,000 to 20,000</option><option>Above 20,000</option><option>Not sure yet</option></select></div><div class="fr"><label for="deadline">{t('Deadline', 'Échéance')}</label><input id="deadline" name="deadline" placeholder="End of November"></div></div>
<hr class="rule"><div class="fr"><label>{t('Meeting platform', 'Plateforme de réunion')}</label><div class="choices"><label><input type="radio" name="platform" value="Zoom" checked> Zoom</label><label><input type="radio" name="platform" value="Microsoft Teams"> Microsoft Teams</label><label><input type="radio" name="platform" value="Google Meet"> Google Meet</label></div></div>
<div class="f2"><div class="fr"><label for="tz">{t('Time zone', 'Fuseau horaire')}</label><input id="tz" name="tz" placeholder="New York, Paris, Douala"></div><div class="fr"><label for="slot1">{t('Time slot 1', 'Créneau 1')}</label><input id="slot1" name="slot1" required placeholder="Tue 21 Oct, 6 to 7 pm"></div></div>
<div class="f2"><div class="fr"><label for="slot2">{t('Time slot 2', 'Créneau 2')}</label><input id="slot2" name="slot2" placeholder="Wed 22 Oct, 12 to 1 pm"></div><div class="fr"><label for="slot3">{t('Time slot 3', 'Créneau 3')}</label><input id="slot3" name="slot3" placeholder="Sat 25 Oct, morning"></div></div>
<div class="cta-row"><button class="btn" type="submit">{t('Send the brief by email', 'Envoyer le brief par courriel')}</button></div>
<p id="brief-notice" class="notice" hidden>{t('Your email app should have opened. If not, copy the brief below and send it to', 'Votre messagerie devrait s’être ouverte. Sinon, copiez le brief ci-dessous et envoyez-le à')} {E(C.SITE['email'])}.</p>
<pre class="summary" aria-live="polite"></pre>
<div id="after-brief" hidden class="cta-row"><button class="btn ghost small" type="button" id="copy-brief">{t('Copy the brief', 'Copier le brief')}</button><input type="hidden" id="b-email"><button class="btn cobalt" type="button" data-pay="consultation">{t('Step 3: reserve the consultation', 'Étape 3 : réserver la consultation')} ${C.SITE['consult_price']}</button></div>
</form></section>"""
    return head("Services", "Services and prices: platforms, networks, books, motion design, content systems, localization.", "/services") + header("services") + body + footer()


def shot_path(name, p):
    here = os.path.dirname(os.path.abspath(__file__))
    if name and os.path.exists(os.path.join(here, "assets", "shots", name + ".webp")): return f"/assets/shots/{name}.webp"
    return f"/assets/shots/{p['shot']}.webp"

def tour(p, g, f=None):
    f = f or {}
    scenes = []
    for i, sc in enumerate(g["scenes"]):
        fs = f.get("scenes", [])
        d = {"k": sc["k"], "t": sc["t"], "c": sc["c"], "img": shot_path(sc.get("shot"), p), "f": sc["f"]}
        if i < len(fs): d["fr"] = {"k": fs[i][0], "t": fs[i][1], "c": fs[i][2]}
        scenes.append(d)
    data = E(json.dumps(scenes, ensure_ascii=False), quote=True)
    return f"""<div class="tour" id="tour" data-scenes="{data}" style="--bk:{p['color']};--bk-ink:{p['ink']}" tabindex="0" aria-label="{E(p['title'], quote=True)} walkthrough">
<div class="tour-stage"><img class="tour-img" alt="" src="{scenes[0]['img']}"><svg class="tour-hl" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><rect x="0" y="0" width="100" height="100" rx="1.2"/></svg><div class="tour-n mono"></div></div>
<div class="tour-cap"><span class="k mono"></span><h3 class="t"></h3><p class="c"></p></div>
<div class="tour-ctl"><button type="button" class="t-prev" aria-label="Previous">&larr;</button><div class="dots" role="tablist"></div><button type="button" class="t-play">PAUSE</button><button type="button" class="t-next" aria-label="Next">&rarr;</button></div></div>"""

def page_guide(p):
    g = GUIDES[p["slug"]]; f = frg(p["slug"]); fp = frp(p["slug"])
    start = "".join(f'<div class="step rv"><span class="n">{i + 1}</span><div><p style="font-size:17px">{tf(x, f, "start", i)}</p></div></div>' for i, x in enumerate(g["start"]))
    rooms = ""
    for i, r in enumerate(g["rooms"]):
        fr_r = f["rooms"][i] if i < len(f.get("rooms", [])) else (None, None, [])
        how = "".join(f"<li>{t(h, fr_r[2][k] if k < len(fr_r[2]) else None)}</li>" for k, h in enumerate(r["how"]))
        rooms += f"""<article class="room rv"><figure class="shot"><img src="{shot_path(r.get('shot'), p)}" alt="{E(p['title'], quote=True)}, {E(r['title'], quote=True)}" loading="lazy"><figcaption>{E(p['title'])}, {t(r['title'], fr_r[0])}</figcaption></figure><div><span class="label"><b>{str(i + 1).zfill(2)}</b></span><h3 style="margin:10px 0 8px">{t(r['title'], fr_r[0])}</h3><p style="font-size:17px;line-height:1.65;color:var(--encre)">{t(r['text'], fr_r[1])}</p><h4 class="mono muted" style="margin:14px 0 6px;letter-spacing:.14em">{t('STEPS', 'ÉTAPES')}</h4><ol class="how">{how}</ol></div></article>"""
    tips = "".join(f"<li>{tf(x, f, 'tips', i)}</li>" for i, x in enumerate(g["tips"]))
    faq = "".join(f'<details class="faq"><summary>{tf(q, f, "faq", i, 0)}</summary><p>{tf(a, f, "faq", i, 1)}</p></details>' for i, (q, a) in enumerate(g["faq"]))
    contact = "".join(f'<a class="card" href="{E(h)}"{" target=\"_blank\" rel=\"noopener\"" if h.startswith("http") else ""}><span class="label"><b>Contact</b></span><h3 style="font-size:20px">{tf(l, f, "contact", i)}</h3></a>' for i, (l, h) in enumerate(g["contact"]))
    visit = f'<a class="btn" href="{E(p["url"])}" target="_blank" rel="noopener">{t("Open", "Ouvrir")} {E(p["title"])} &#8599;</a>' if p["url"] else ""
    body = f"""<section class="block wrap" style="padding-bottom:24px">{plabel(p)}<h1 class="rv" style="margin:14px 0 12px;font-size:clamp(34px,5.5vw,70px)">{t('How to use', 'Utiliser')} {E(p['title'])}</h1><p class="lede rv">{tf(g['audience'], f, 'audience')}</p><p class="cta-row rv" style="margin-top:16px">{visit}<a class="btn ghost" href="/portfolio/{p['slug']}">{t('Platform details', 'Fiche de la plateforme')}</a><a class="btn ghost" href="#contact">Contact</a></p></section>
<section class="wrap rv"><div class="sec-head" style="margin-bottom:14px"><span class="label"><b>{t('Guided tour', 'Visite guidée')}</b><span>{t('Real screens', 'Vrais écrans')}</span></span></div>{tour(p, g, f)}<p class="muted" style="font-size:13px;margin-top:10px">{t('Plays automatically. Use the dots or arrows to move, Pause to stop.', 'Lecture automatique. Points ou flèches pour naviguer, Pause pour arrêter.')}</p></section>
<section class="block wrap"><div class="sec-head"><span class="label rv"><b>01</b></span><h2 class="rv">{t('Getting started', 'Pour commencer')}</h2></div><div class="steps">{start}</div></section>
<section class="block wrap" style="padding-top:0"><div class="sec-head"><span class="label rv"><b>02</b></span><h2 class="rv">{t('Features', 'Fonctions')}</h2></div><div class="rooms">{rooms}</div></section>
<section class="block wrap" style="padding-top:0"><div class="grid g2"><div class="card rv"><span class="label"><b>03</b><span>{t('Tips', 'Conseils')}</span></span><ul class="ticks" style="font-size:16px">{tips}</ul></div><div class="card rv"><span class="label"><b>04</b><span>FAQ</span></span><div>{faq}</div></div></div></section>
<section class="block wrap" id="contact" style="padding-top:0"><div class="sec-head"><span class="label rv"><b>05</b></span><h2 class="rv">Contact</h2></div><div class="grid g3 rv">{contact}<a class="card" href="/services#brief"><span class="label"><b>{t('Project', 'Projet')}</b></span><h3 style="font-size:20px">{t('Need a similar platform?', 'Besoin d’une plateforme similaire ?')}</h3><span class="mono muted">{t('Send a brief', 'Envoyer un brief')} &rarr;</span></a></div></section>"""
    return head("How to use " + p["title"], f"How to use {p['title']}: guided tour, first steps, features, tips, FAQ and contact.", f"/guides/{p['slug']}") + header("portfolio") + body + footer()

def page_contact():
    body = f"""<section class="block wrap"><span class="label rv"><b>Contact</b><span>{t(C.SITE['location'], 'Maryland, États-Unis')}</span></span><h1 class="rv" style="margin:16px 0 14px">Contact.</h1><p class="lede rv">{t('For a project, start with the brief on the services page. For anything else, email me. I reply within one business day, in French or English.', 'Pour un projet, commencez par le brief de la page services. Pour le reste, écrivez-moi. Je réponds sous un jour ouvré, en français ou en anglais.')}</p>
<div class="grid g2 rv" style="margin-top:28px"><div class="card"><span class="label"><b>Email</b></span><h3><a href="mailto:{E(C.SITE['email'])}">{E(C.SITE['email'])}</a></h3><p style="margin:0;color:var(--encre)">{t('Projects, books, speaking, questions.', 'Projets, livres, interventions, questions.')}</p></div><div class="card"><span class="label"><b>{t('Meetings', 'Rendez-vous')}</b></span><h3>Zoom, Microsoft Teams, Google Meet</h3><p style="margin:0;color:var(--encre)">{t('Booked through the brief and confirmed by email.', 'Réservés via le brief et confirmés par courriel.')}</p><p class="cta-row" style="margin-top:10px"><a class="btn small" href="/services#brief">{t('Open the brief', 'Ouvrir le brief')}</a></p></div></div>
<div class="sec-head" style="margin-top:36px"><span class="label rv"><b>{t('Platforms', 'Plateformes')}</b><span>{t('Contact each one directly', 'Contacter chacune directement')}</span></span></div>
<div class="grid g3 rv">{"".join(f'<a class="card" href="/guides/{p["slug"]}#contact" style="gap:6px">{plabel(p)}<h3 style="font-size:20px">{E(p["title"])}</h3></a>' for p in C.PROJECTS)}</div></section>"""
    return head("Contact", "Contact William Foteping.", "/contact") + header("contact") + body + footer()

def page_thanks():
    body = f"""<section class="block wrap"><span class="label rv"><b>{t('Reserved', 'Réservé')}</b></span><h1 class="rv" style="margin:16px 0 14px">{t('Payment received.', 'Paiement reçu.')}</h1><p class="lede rv">{t('I will confirm your time slot by email within one business day and send a calendar invitation for the platform you chose.', 'Je confirme votre créneau par courriel sous un jour ouvré et j’envoie une invitation pour la plateforme choisie.')}</p><p class="mono muted" hidden>{t('Reference', 'Référence')}: <span id="session"></span></p><p class="cta-row"><a class="btn" href="/">{t('Home', 'Accueil')}</a></p></section>"""
    return head("Thank you", "Reservation confirmed.", "/thanks") + header("services") + body + footer()

FILMS = [
    ("https://claude.ai/artifact/V1u1HfuXv56xoGZ5MQczYh", "zeste-film", "Paper animation", "Animation papier", "Zeste explainer", "Le film de Zeste",
     "90 seconds of torn-paper animation with kalimba: you speak, Claude prepares, you approve. On the Zeste page, in French and English.",
     "90 secondes d'animation en papier déchiré, au son du kalimba : vous parlez, Claude prépare, vous validez. Sur la page Zeste, en français et en anglais."),
    ("https://claude.ai/artifact/VJodoes5amcSFqaWrmcpGo", "peel", "Interactive", "Interactif", "Peel exposure check", "Le test d'exposition de Peel",
     "Five questions, a live score and the likely risks, computed in the browser.",
     "Cinq questions, un score en direct et les risques probables, calculés dans le navigateur."),
]

def page_admin():
    body = f"""<section class="admin wrap">
<div class="a-login"><span class="label"><b>Privé</b><span>Propriétaire</span></span><h1 style="font-size:34px;margin:4px 0">La salle des machines</h1><p class="muted" style="margin:0">Entrez votre clé privée. Elle reste sur cet appareil.</p>
<form><input type="password" autocomplete="current-password" placeholder="Clé privée" aria-label="Clé privée" required><button class="a-btn" type="submit">Entrer</button><p class="err"></p></form></div>
<div class="a-app" hidden>
<div class="a-top"><div><span class="label"><b>Privé</b><span>william-foteping.vercel.app</span></span><h1>Qui lit, qui visite.</h1></div><button class="a-btn ghost" id="logout" type="button">Se déconnecter</button></div>
<div class="a-tabs" role="tablist"><button type="button" data-tab="stats">Visites et lecteurs</button><button type="button" data-tab="books">Livres gratuits</button><button type="button" data-tab="gallery">Galerie</button><button type="button" data-tab="settings">Réglages</button></div>

<div class="a-pane a-stats" data-pane="stats">
<div class="a-top" style="align-items:center"><label style="max-width:240px">Période<select id="range"><option value="1">Aujourd’hui</option><option value="7">7 jours</option><option value="30" selected>30 jours</option><option value="90">90 jours</option><option value="365">12 mois</option></select></label><div class="a-actions"><span class="muted a-updated" style="font-size:13px"></span><button class="a-btn ghost" id="refresh" type="button">Actualiser</button></div></div>
<div class="a-tiles"></div>
<div class="a-card" style="margin-bottom:14px"><h3>Jour après jour</h3><div class="a-daily"></div></div>
<div class="a-card" style="margin-bottom:14px"><h3>Livres lus</h3><div class="a-table a-books-read"></div><h4>Jusqu’où ils lisent</h4><div class="a-funnel"></div></div>
<div class="a-grid" style="margin-bottom:14px"><div class="a-card"><h3>Pays</h3><div class="a-countries"></div></div><div class="a-card"><h3>Villes</h3><div class="a-cities"></div></div>
<div class="a-card"><h3>Pages</h3><div class="a-pages"></div></div><div class="a-card"><h3>D’où ils viennent</h3><div class="a-refs"></div><h4>Appareils</h4><div class="a-devices"></div></div></div>
<div class="a-card"><h3>Activité récente</h3><p class="muted" style="margin:-6px 0 10px;font-size:13px">Chaque visiteur est un identifiant anonyme : mêmes lettres, même personne. Aucun nom, aucune adresse IP n’est gardé.</p><div class="a-table a-recent"><table><thead><tr><th>Quand</th><th>Visiteur</th><th>Action</th><th>Quoi</th><th>Où</th><th>Appareil</th><th>Venu de</th></tr></thead><tbody></tbody></table></div></div>
</div>

<div class="a-pane" data-pane="books" hidden>
<div class="a-card" style="margin-bottom:14px"><h3>Tous les livres d’un coup</h3><p class="muted" style="margin-top:-4px">Quand la lecture libre est fermée, les visiteurs lisent seulement les premières sections, puis voient vos liens d’achat et le bouton café.</p><div class="a-actions"><button class="a-btn" id="all-month" type="button">Tout gratuit 30 jours</button><button class="a-btn ghost" id="all-open" type="button">Tout gratuit sans date de fin</button><button class="a-btn ghost danger" id="all-close" type="button">Tout fermer maintenant</button></div></div>
<div class="a-booklist"></div></div>

<div class="a-pane" data-pane="gallery" hidden>
<div class="a-upload"><h3 style="font:400 24px var(--serif);margin:0">Ajouter des photos ou des vidéos</h3><p class="muted" style="margin:0">Photos JPG, PNG ou WebP, vidéos MP4 ou MOV jusqu’à 50 Mo. Les grandes photos sont réduites avant l’envoi. Après l’envoi, écrivez l’histoire de chaque moment, puis Enregistrer.</p><input type="file" id="files" accept="image/jpeg,image/png,image/webp,image/gif,video/mp4,video/quicktime,video/webm" multiple><p class="st"></p></div>
<div class="a-glist"></div></div>

<div class="a-pane" data-pane="settings" hidden><div class="a-grid">
<div class="a-card"><h3>Liens de don</h3><p class="muted" style="margin-top:-4px">Jusqu’à trois liens, proposés dans cet ordre quand un lecteur touche « Faire un don ». Sites acceptés : Stripe, Ko-fi, PayPal, Flutterwave, CinetPay, Buy Me a Coffee, Patreon. Laissez une ligne vide pour ne pas l’afficher.</p><div class="a-row a-don"><label>Libellé<input class="dl" type="text" maxlength="40" placeholder="Carte bancaire"></label><label>Lien<input class="du" type="url" placeholder="https://buy.stripe.com/..."></label></div><div class="a-row a-don"><label>Libellé<input class="dl" type="text" maxlength="40" placeholder="PayPal"></label><label>Lien<input class="du" type="url" placeholder="https://ko-fi.com/... ou https://www.paypal.com/donate/..."></label></div><div class="a-row a-don"><label>Libellé<input class="dl" type="text" maxlength="40" placeholder="Mobile Money"></label><label>Lien<input class="du" type="url" placeholder="https://flutterwave.com/pay/..."></label></div><div class="a-actions"><button class="a-btn" id="save-donation" type="button">Enregistrer</button></div></div>
<div class="a-card"><h3>Mes propres visites</h3><label class="sw"><input type="checkbox" id="me-toggle"><span>Ne pas compter mes visites sur cet appareil</span></label></div>
<div class="a-card"><h3>Changer la clé privée</h3><label>Nouvelle clé (au moins 12 caractères)<input id="new-key" type="password" autocomplete="new-password"></label><label>La même, encore une fois<input id="new-key2" type="password" autocomplete="new-password"></label><div class="a-actions"><button class="a-btn" id="change-key" type="button">Changer la clé</button></div></div>
</div></div>
</div><div class="a-toast" role="status"></div></section>"""
    extra = '<meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="/assets/admin.css"><script src="/assets/admin.js" defer></script>'
    return head("Private", "Private.", "/admin", extra) + header("") + body + footer()

def page_404():
    body = f"""<section class="block wrap"><span class="label rv"><b>404</b></span><h1 class="rv" style="margin:16px 0 14px">{t('Page not found.', 'Page introuvable.')}</h1><p class="cta-row"><a class="btn" href="/">{t('Home', 'Accueil')}</a><a class="btn ghost" href="/portfolio">Portfolio</a></p></section>"""
    return head("Not found", "Page not found.", "/404") + header("") + body + footer()

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#F6F2EA"/><circle cx="32" cy="32" r="13" fill="#1C3FBF"/><path d="M12 52 L32 10 L52 52" fill="none" stroke="#1B1A17" stroke-width="3" stroke-linejoin="round"/></svg>"""

import hashlib
def asset_version():
    here = os.path.dirname(os.path.abspath(__file__)); h = hashlib.sha1()
    for n in ("style.css", "app.js", "scenes.js", "salon.css", "salon.js", "guard.js", "track.js", "live.js", "admin.js", "admin.css"):
        p = os.path.join(here, "assets", n)
        if os.path.exists(p): h.update(open(p, "rb").read())
    return h.hexdigest()[:8]
V = asset_version()

def write(path, s, strict=True):
    for bad, name in (("—", "em dash"), ("–", "en dash")):
        assert not strict or bad not in s, f"{name} found in {path}"
    import re as _re
    s = _re.sub(r'(/assets/(?:style|salon|admin)\.css|/assets/(?:app|scenes|salon|guard|track|live|admin)\.js)(?=["\'])', lambda m: m.group(1) + "?v=" + V, s)
    s = _re.sub(r'(/assets/(?:shots|motion)/[\w.-]+\.(?:webp|png|jpg|mp4))(?=["\'&])', lambda m: m.group(1) + "?v=" + V, s)
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(s)

def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    here = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(os.path.join(here, "assets"), os.path.join(OUT, "assets"), ignore=shutil.ignore_patterns("posters"))
    with open(os.path.join(OUT, "assets", "favicon.svg"), "w") as f: f.write(FAVICON)
    write("index.html", page_home())
    write("portfolio/index.html", page_portfolio())
    n = len(C.PROJECTS)
    for i, p in enumerate(C.PROJECTS): write(f"portfolio/{p['slug']}.html", page_project(p, C.PROJECTS[i - 1], C.PROJECTS[(i + 1) % n]))
    for p in C.PROJECTS: write(f"guides/{p['slug']}.html", page_guide(p))
    write("books.html", page_books())
    for b in SALON.load_books(): write(f"lire/{b['slug']}.html", SALON.page(b, t, head, header, footer, cover_art), strict=False)
    write("gallery.html", page_gallery())
    write("demo/e-xaf.html", open(os.path.join(here, "demo", "e-xaf.html"), encoding="utf-8").read(), strict=False)
    write("journal/index.html", page_journal())
    m = len(C.JOURNAL)
    for i, p in enumerate(C.JOURNAL): write(f"journal/{p['slug']}.html", page_post(p, C.JOURNAL[i - 1], C.JOURNAL[(i + 1) % m]))
    write("services.html", page_services())
    write("contact.html", page_contact())
    write("thanks.html", page_thanks())
    write("404.html", page_404())
    write("admin.html", page_admin())
    pages = ["/", "/portfolio"] + [f"/portfolio/{p['slug']}" for p in C.PROJECTS] + [f"/guides/{p['slug']}" for p in C.PROJECTS] + ["/books"] + [f"/lire/{b['slug']}" for b in SALON.load_books()] + ["/gallery", "/demo/e-xaf", "/journal"] + [f"/journal/{p['slug']}" for p in C.JOURNAL] + ["/services", "/contact"]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{C.SITE['url']}{u}</loc></url>" for u in pages) + "</urlset>")
    ai = ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "CCBot", "anthropic-ai", "ClaudeBot", "Claude-Web", "Google-Extended", "PerplexityBot", "Bytespider", "Amazonbot", "Applebot-Extended", "meta-externalagent", "FacebookBot", "Diffbot", "ImagesiftBot", "Omgilibot", "cohere-ai", "YouBot", "Timpibot"]
    write("robots.txt", "".join(f"User-agent: {b}\nDisallow: /\n\n" for b in ai) + f"User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /api/\nSitemap: {C.SITE['url']}/sitemap.xml\n")
    print("built", len(pages), "pages into", OUT)

if __name__ == "__main__":
    main()
