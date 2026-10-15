#!/usr/bin/env python3
"""Builds the static site into dist/. Run: python3 build.py"""
import os, shutil, json, html, datetime
import content as C
from guides import GUIDES
import fr as FR
import salon as SALON

if SALON.has_richesse():  # the manuscript has landed: open it in the reading room
    for _b in C.BOOKS:
        if _b["slug"] == "richesse-silencieuse":
            _b.update({"free": "la-richesse-silencieuse", "year": "2026", "pages": "Free, complete, online", "kind": "Investing guide for the diaspora",
                       "line": "A calm, practical investing guide for salaried people of the African diaspora: simple principles, real numbers, and room for family without sacrificing the future. Free to read here, in full.",
                       "where": [("Read it free, online", "/lire/la-richesse-silencieuse")]})
            FR.BOOKS["richesse-silencieuse"] = {"pages": "Gratuit, complet, en ligne", "kind": "Guide d'investissement pour la diaspora",
                       "line": "Un guide d'investissement calme et pratique pour les salariés de la diaspora africaine : des principes simples, de vrais chiffres, et une place pour la famille sans sacrifier l'avenir. À lire ici gratuitement, en entier.",
                       "where": [("Lire gratuitement en ligne", "/lire/la-richesse-silencieuse")]}

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

NAV = [("/", "Home", "Accueil", "home"), ("/work", "Work", "Travaux", "work"), ("/books", "Books", "Livres", "books"), ("/gallery", "Gallery", "Galerie", "gallery"), ("/journal", "Journal", "Journal", "journal"), ("/services", "Services", "Services", "services"), ("/contact", "Contact", "Contact", "contact")]

def head(title, desc, path, extra=""):
    full = f"{title} | {C.SITE['name']}" if title else C.SITE["name"]
    url = C.SITE["url"] + path
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(full)}</title><meta name="description" content="{E(desc, quote=True)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{E(full, quote=True)}"><meta property="og:description" content="{E(desc, quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:image" content="{C.SITE['url']}/assets/og.png"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><meta name="theme-color" content="#F6F2EA">
{FONTS}<link rel="stylesheet" href="/assets/style.css">{extra}</head><body data-email="{E(C.SITE['email'], quote=True)}"><a class="skip" href="#main">Skip to content</a>"""

def header(active):
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{t(en, fr)}</a>' for h, en, fr, k in NAV)
    return f"""<header class="top"><div class="wrap"><a class="brand" href="/"><i></i>{E(C.SITE['name'])}</a>
<nav class="nav" id="nav" aria-label="Main">{links}</nav>
<div class="tools"><button class="pill lang" data-lang="en" aria-pressed="true">EN</button><button class="pill lang" data-lang="fr" aria-pressed="false">FR</button><button class="pill theme" aria-label="Toggle theme">DARK</button><button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav"><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 5h14M2 9h14M2 13h14"/></svg></button></div></div></header><main id="main">"""

def footer():
    y = datetime.date.today().year
    work = "".join(f'<a href="{p["url"] or "/work/" + p["slug"]}"{" target=\"_blank\" rel=\"noopener\"" if p["url"] else ""}>{E(p["title"])}</a>' for p in C.PROJECTS[:6])
    return f"""</main><footer><div class="wrap"><div><div class="tag">{t('Build things that teach, and things that work.', 'Construire ce qui enseigne, et ce qui fonctionne.')}</div><p>{E(C.SITE['location'])}. {t('French and English.', 'Français et anglais.')}</p><p><a href="mailto:{E(C.SITE['email'])}">{E(C.SITE['email'])}</a></p></div>
<div><h4>{t('Work', 'Travaux')}</h4>{work}</div>
<div><h4>{t('Here', 'Ici')}</h4><a href="/books">{t('Books', 'Livres')}</a><a href="/gallery">{t('Gallery', 'Galerie')}</a><a href="/journal">Journal</a><a href="/services">Services</a><a href="/contact">Contact</a><p style="margin-top:14px">&copy; {y} {E(C.SITE['name'])}</p></div></div></footer>
<script src="/assets/app.js" defer></script></body></html>"""

def label(n, kind, year):
    return f'<span class="label"><b>N° {E(n)}</b><span>{E(kind)}</span><span>{E(year)}</span></span>'

def stage(p, meta="Purpose motion"):
    beats = E(json.dumps(p["beats"], ensure_ascii=False), quote=True)
    return f"""<div class="stage" data-beats="{beats}" style="--bk:{p['color']};--bk-ink:{p['ink']}" role="img" aria-label="{E(p['title'], quote=True)}, purpose in motion"><svg viewBox="0 0 600 340" preserveAspectRatio="xMidYMid meet" aria-hidden="true"><path class="shape" d=""/></svg><span class="meta" data-base="{E(meta, quote=True)}">{E(meta)}</span><div class="ctl"><button class="play-btn" type="button">PAUSE</button></div><div class="line"></div><div class="bar"></div></div>"""

def book_btn(p):
    return f"""<button class="book" type="button" aria-pressed="false" style="--bk:{p['color']};--bk-ink:{p['ink']}" data-title="{E(p['title'], quote=True)}" data-kind="{E(p['kind'], quote=True)}" data-year="{E(p['year'], quote=True)}" data-line="{E(p['line'], quote=True)}" data-shot="/assets/shots/{p['shot']}.webp" data-href="/work/{p['slug']}" data-url="{E(p['url'], quote=True)}" data-link-label="{E(p['link_label'], quote=True)}"><span class="bn">N° {E(p['n'])}</span><span class="bt">{E(p['title'])}</span><span class="bk">{E(p['kind'])}<br>{E(p['year'])}</span><span class="bo">Open &rarr;</span></button>"""

def shelf(projects, hint=True):
    books = "".join(book_btn(p) for p in projects)
    return f"""<div class="shelf"><div class="shelf-rail" tabindex="-1">{books}</div><div class="shelf-board" aria-hidden="true"></div>
<div class="shelf-hint"><span>{t('Select a book to present it, select again to open it. Arrow keys move along the shelf, Escape puts it back.', 'Sélectionnez un livre pour le présenter, puis une seconde fois pour l’ouvrir. Les flèches parcourent l’étagère, Échap le range.')}</span><span class="shelf-arrows"><button type="button" data-dir="prev" aria-label="Previous">&larr;</button><button type="button" data-dir="next" aria-label="Next">&rarr;</button></span></div>
<div class="present" aria-live="polite"><img class="p-img" alt="" src=""><div><span class="label"><b class="p-kind"></b></span><h3 class="p-title" style="margin:10px 0 8px"></h3><p class="p-line lede" style="font-size:17px"></p><p class="cta-row"><a class="btn p-open" href="#">{t('Read the book', 'Lire le livre')}</a><a class="btn ghost p-guide" href="#">{t('How to use', 'Mode d’emploi')}</a><a class="btn ghost p-link" href="#" target="_blank" rel="noopener"></a></p></div></div></div>"""

def hero_art():
    return """<div class="glass rv" aria-hidden="true"><canvas id="hero-canvas"></canvas><svg class="glass-fallback" viewBox="0 0 400 300" fill="none" stroke="currentColor" stroke-width="1.2" style="color:#1C3FBF">
<g opacity=".55"><path d="M40 260 L200 40 L360 260 Z"/><path d="M200 40 V260"/><path d="M120 150 H280"/><path d="M80 205 H320"/></g>
<g opacity=".8" stroke="#B8933F"><circle cx="200" cy="150" r="70"/><circle cx="200" cy="150" r="46"/><path d="M130 150 H270 M200 80 V220"/></g>
<g opacity=".5"><path d="M20 290 H380" /><path d="M60 120 Q200 -20 340 120" /></g></svg></div>"""

# ---------------------------------------------------------------------------
def page_home():
    featured = C.PROJECTS[0]
    posts = C.JOURNAL[:3]
    stats = [("9", "Platforms", "Plateformes"), ("6", "Books", "Livres"), ("14", "Motion and edits", "Motion et montages"), ("2", "Languages", "Langues")]
    body = f"""<section class="hero wrap"><div class="hero-grid"><div>
<span class="label rv"><b>{t('Portfolio', 'Portfolio')}</b><span>{E(C.SITE['location'])}</span></span>
<h1 class="name rv" style="margin:18px 0 20px">William<br><em>Foteping</em></h1>
<p class="lede rv">{t(C.SITE['tagline_en'], C.SITE['tagline_fr'])}</p>
<p class="cta-row rv"><a class="btn" href="/work">{t('Open the library', 'Ouvrir la bibliothèque')}</a><a class="btn ghost" href="/services">{t('Work with me', 'Travailler avec moi')}</a></p></div>
<div>{hero_art()}<div class="hero-aside rv"><div class="kv"><span>{t('Trade', 'Métier')}</span><span>{t('Senior network administrator, cloud and infrastructure', 'Administrateur réseau senior, cloud et infrastructure')}</span></div><div class="kv"><span>{t('Temperament', 'Tempérament')}</span><span>{t('Serial entrepreneur, hobby entrepreneur, and I love it', 'Entrepreneur en série, entrepreneur par passion, et j’aime ça')}</span></div><div class="kv"><span>{t('Ventures', 'Projets')}</span><span>Uplink IT Academy, Bobine, Lemon Network Solutions, Droit Facile</span></div><div class="kv"><span>{t('Writing', 'Écriture')}</span><span>{t('Essays, chronicles, technical books, in French and English', 'Essais, chroniques, livres techniques, en français et en anglais')}</span></div><div class="kv"><span>{t('Certified', 'Certifié')}</span><span>CCNA, Azure Administrator</span></div></div></div></div></section>
<div class="wrap"><div class="stats rv">{"".join(f'<div class="stat"><b>{n}</b><span>{t(en, fr)}</span></div>' for n, en, fr in stats)}</div></div>

<section class="block wrap" id="library"><div class="sec-head"><span class="label rv"><b>01</b><span>{t('The library', 'La bibliothèque')}</span></span><div class="row rv"><h2>{t('Every project is a book.', 'Chaque projet est un livre.')}</h2><a class="btn ghost small" href="/work">{t('All the shelves', 'Toutes les étagères')} &rarr;</a></div><p class="lede rv">{t('Take one down. Each book has the purpose, the problem, what I built, how it works, and a short motion that says why it exists.', 'Prenez-en un. Chaque livre raconte le but, le problème, ce que j’ai construit, comment ça marche, et une courte animation qui dit pourquoi il existe.')}</p></div>{shelf(C.PROJECTS)}</section>

<section class="block wrap"><div class="sec-head"><span class="label rv"><b>02</b><span>{t('Purpose in motion', 'Le but en mouvement')}</span></span><div class="row rv"><h2>{E(featured['title'])}: {t('why it exists', 'pourquoi il existe')}</h2><a class="btn ghost small" href="/work/{featured['slug']}">{t('Read the book', 'Lire le livre')} &rarr;</a></div></div><div class="rv">{stage(featured, featured['title'])}</div></section>

<section class="block wrap"><div class="sec-head"><span class="label rv"><b>03</b><span>{t('Books', 'Livres')}</span></span><div class="row rv"><h2>{t('Written, edited, produced.', 'Écrits, édités, produits.')}</h2><a class="btn ghost small" href="/books">{t('The bookcase', 'La bibliothèque')} &rarr;</a></div></div>
<div class="bookcase rv">{"".join(tome(b) for b in C.BOOKS[:3])}</div></section>

<section class="block wrap"><div class="sec-head"><span class="label rv"><b>04</b><span>{t('Gallery', 'Galerie')}</span></span><div class="row rv"><h2>{t('Moving images.', 'Images qui bougent.')}</h2><a class="btn ghost small" href="/gallery">{t('Watch', 'Regarder')} &rarr;</a></div></div>
<div class="grid g3 rv">{vcard(C.MOTION[0])}{vcard(C.EDITS[0])}{vcard(C.EDITS[12])}</div></section>

<section class="block wrap"><div class="sec-head"><span class="label rv"><b>05</b><span>Journal</span></span><div class="row rv"><h2>{t('Life, process, regards.', 'La vie, le processus, des regards.')}</h2><a class="btn ghost small" href="/journal">{t('Read the journal', 'Lire le journal')} &rarr;</a></div></div>
<div class="posts rv">{"".join(post_row(p) for p in posts)}</div></section>

<section class="block wrap"><div class="card rv" style="padding:clamp(24px,4vw,44px);gap:16px"><span class="label"><b>06</b><span>Services</span></span><h2>{t('I can do this for you.', 'Je peux faire ça pour vous.')}</h2><p class="lede">{t('Platforms, networks, books, motion and content systems, in French and English. A clear brief, a booked meeting on Zoom, Teams or Google Meet, a price in writing.', 'Plateformes, réseaux, livres, motion et systèmes de contenu, en français et en anglais. Un brief clair, un rendez-vous sur Zoom, Teams ou Google Meet, un prix par écrit.')}</p><p class="cta-row"><a class="btn cobalt" href="/services">{t('See services and prices', 'Voir les services et les prix')}</a><a class="btn ghost" href="/services#brief">{t('Send a brief', 'Envoyer un brief')}</a></p></div></section>"""
    return head("", C.SITE["description"], "/", THREE) + header("home") + body + footer()

def tome(b, is_album=False):
    f = FR.ALBUM if is_album else frb(b["slug"])
    where_en = b["where"]; where_fr = f.get("where", where_en)
    where = "".join(f'<a class="btn {"cobalt" if u.startswith("/lire/") else "ghost"} small" href="{E(u)}"{"" if u.startswith("/") else " target=\"_blank\" rel=\"noopener\""}>{t(l, (where_fr[i][0] if i < len(where_fr) else l))} &rarr;</a>' for i, (l, u) in enumerate(where_en))
    pages = f'<div><span class="k">Format</span> {tf(b["pages"], f, "pages")}</div>' if b.get("pages") else ""
    by = E(b["artist"]) if is_album else E(C.SITE["name"])
    top = E(b["lang"].upper()) if not is_album else "WFOSS"
    return f"""<article class="tome"><div class="cover art" style="--bk:{b['color']};--bk-ink:{b['ink']}">{cover_art(b['slug'], b['color'], b['ink'])}<span class="bn">{top}</span><span class="bt">{E(b['title'])}</span><span class="by">{by}</span><span class="bk">{tf(b['kind'], f, 'kind')}<br>{E(b['year'])}</span></div>
<div class="meta"><h3 style="font-size:22px">{E(b['title'])}</h3><p style="margin:4px 0 6px;font-size:15px;color:var(--encre)">{tf(b['line'], f, 'line')}</p>{pages}{('<div class="cta-row" style="margin-top:6px">' + where + '</div>') if where else ''}</div></article>"""

def vcard(v):
    first = v["variants"][0]
    vars_ = "".join(f'<button type="button" data-src="{E(u, quote=True)}" data-ratio="{E(r, quote=True)}" aria-pressed="{"true" if i == 0 else "false"}">{E(l)}</button>' for i, (l, u, r) in enumerate(v["variants"]))
    return f"""<article class="vcard" data-src="{E(first[1], quote=True)}" data-ratio="{E(first[2], quote=True)}" data-poster="{E(v['poster'], quote=True)}"><div class="media"><img src="{E(v['poster'])}" alt="{E(v['title'], quote=True)}, still" loading="lazy"><button class="play" type="button" aria-label="Play {E(v['title'], quote=True)}"><span><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span></button></div>
<div class="body"><span class="label"><b>{E(v['kind'])}</b><span>{E(v['year'])}</span></span><h3 style="font-size:22px">{E(v['title'])}</h3><p style="margin:0;font-size:14px;color:var(--encre)">{E(v['line'])}</p><div class="vars">{vars_}</div></div></article>"""

def post_row(p):
    d = datetime.date.fromisoformat(p["date"]).strftime("%d %b %Y")
    return f"""<article class="post"><a class="th" href="/journal/{p['slug']}"><img src="{E(p['thumb']) if p['thumb'].startswith('http') else '/' + E(p['thumb'])}" alt="" loading="lazy"></a><div><span class="cat"><i style="color:{p['color']}"></i>{tf(p['cat'], frj(p['slug']), 'cat')}</span> <span class="date">{d}</span><h3><a href="/journal/{p['slug']}">{tf(p['title'], frj(p['slug']), 'title')}</a></h3><p class="lede" style="font-size:17px">{tf(p['lede'], frj(p['slug']), 'lede')}</p><a class="btn ghost small" href="/journal/{p['slug']}">{t('Read', 'Lire')} &rarr;</a></div></article>"""

# ---------------------------------------------------------------------------
def page_work():
    cards = "".join(f"""<a class="card rv" href="/work/{p['slug']}" style="gap:10px"><figure class="shot" style="margin:0 0 6px"><img src="/assets/shots/{p['shot']}.webp" alt="{E(p['title'], quote=True)}, screenshot" loading="lazy"></figure>{label(p['n'], p['kind'], p['year'])}<h3>{E(p['title'])}</h3><p style="margin:0;color:var(--encre)">{E(p['line'])}</p><span class="mono muted">{E(p['status'])}</span><span class="mono" style="color:var(--cobalt)">{t('Book', 'Livre')} &rarr; &nbsp; <a href="/guides/{p['slug']}" style="text-decoration:underline">{t('How to use', 'Mode d’emploi')}</a></span></a>""" for p in C.PROJECTS)
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>{t('Work', 'Travaux')}</b><span>{len(C.PROJECTS)} {t('books on the shelf', 'livres sur l’étagère')}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('The library.', 'La bibliothèque.')}</h1><p class="lede rv">{t('Platforms, tools and sites I designed and built, presented as books: take one down, read the purpose, the problem, what I built and how it works, and watch a short motion that says why it exists.', 'Plateformes, outils et sites que j’ai conçus et construits, présentés comme des livres : prenez-en un, lisez le but, le problème, ce que j’ai construit et comment ça marche, et regardez une courte animation qui dit pourquoi il existe.')}</p></section>
<section class="wrap">{shelf(C.PROJECTS)}</section>
<section class="block wrap"><div class="sec-head"><span class="label rv"><b>{t('Index', 'Index')}</b><span>{t('All works', 'Toutes les œuvres')}</span></span></div><div class="grid g3">{cards}</div></section>"""
    return head("Work", "Platforms, tools and sites by William Foteping, presented as books.", "/work") + header("work") + body + footer()

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
def page_project(p, prev, nxt):
    f = frp(p["slug"])
    chapters = "".join(f'<div class="chapter rv"><span class="ch">{ROMAN[i]}</span><div><h3>{tf(h, f, "chapters", i, 0)}</h3><p>{tf(txt, f, "chapters", i, 1)}</p></div></div>' for i, (h, txt) in enumerate(p["chapters"]))
    facts = "".join(f'<div><span>{E(k)}</span><span>{E(v)}</span></div>' for k, v in p["facts"])
    hl = "".join(f"<li>{tf(h, f, 'highlights', i)}</li>" for i, h in enumerate(p["highlights"]))
    visit = f'<a class="btn" href="{E(p["url"])}" target="_blank" rel="noopener">{t("Visit", "Visiter")} {E(p["link_label"])} &rarr;</a>' if p["url"] else f'<span class="notice">{t("This one is a private build for now. Ask me for a walkthrough.", "Celui-ci est une version privée pour le moment. Demandez-moi une visite.")}</span>'
    body = f"""<section class="block wrap"><div class="open">
<aside><div class="cover" style="--bk:{p['color']};--bk-ink:{p['ink']}"><span class="bn">N° {E(p['n'])}</span><span class="bt">{E(p['title'])}</span><span class="bk">{tf(p['kind'], f, 'kind')}<br>{E(p['year'])}<br>{tf(p['status'], f, 'status')}</span></div>
<div class="facts">{facts}<div><span>Stack</span><span>{E(p['stack'])}</span></div></div></aside>
<div><span class="label rv"><b>N° {E(p['n'])}</b><span>{E(p['kind'])}</span><span>{E(p['year'])}</span></span><h1 class="rv" style="margin:14px 0 12px;font-size:clamp(36px,5.5vw,72px)">{E(p['title'])}</h1><p class="lede rv">{tf(p['line'], f, 'line')}</p><p class="cta-row rv" style="margin:18px 0 34px">{visit}<a class="btn cobalt" href="/guides/{p['slug']}">{t('How to use it', 'Mode d’emploi')}</a><a class="btn ghost" href="#motion">{t('Watch the purpose', 'Voir le but en mouvement')}</a></p>
<figure class="shot rv"><img src="/assets/shots/{p['shot']}.webp" alt="{E(p['title'], quote=True)}, screenshot"><figcaption>{E(p['title'])}, {t('screenshot', 'capture d’écran')}</figcaption></figure>
<div class="chapters" style="margin-top:40px">{chapters}
<div class="chapter rv" id="motion"><span class="ch">{ROMAN[len(p['chapters'])]}</span><div><h3>{t('The purpose, in motion', 'Le but, en mouvement')}</h3><p style="margin-bottom:14px">{t('A short motion design made for this book: four beats, one drawn shape each, the reason the project exists. Tap it to step through.', 'Un court motion design fait pour ce livre : quatre temps, une forme dessinée à chaque fois, la raison d’être du projet. Touchez pour avancer.')}</p>{stage(p, p['title'])}</div></div>
<div class="chapter rv"><span class="ch">{ROMAN[len(p['chapters']) + 1]}</span><div><h3>{t('In short', 'En bref')}</h3><ul class="ticks">{hl}</ul><p class="cta-row" style="margin-top:18px">{visit}</p></div></div></div>
<nav class="cta-row" style="margin-top:48px;justify-content:space-between" aria-label="Books"><a class="btn ghost small" href="/work/{prev['slug']}">&larr; {E(prev['title'])}</a><a class="btn ghost small" href="/work/{nxt['slug']}">{E(nxt['title'])} &rarr;</a></nav></div></div></section>"""
    return head(p["title"], p["line"], f"/work/{p['slug']}") + header("work") + body + footer()

def salon_card(b):
    f = frb(b["slug"])
    if b["free"]:
        cta = f'<a class="btn cobalt small" href="/lire/{b["free"]}">{t("Read now", "Lire maintenant")} &rarr;</a>'
    else:
        cta = f'<span class="notice">{t("In writing. Free here when the first chapters land.", "En cours d’écriture. Gratuit ici dès les premiers chapitres.")}</span>'
    return f"""<article class="card salon-card" style="--bk:{b['color']};--bk-ink:{b['ink']}"><div class="cover art mini" style="--bk:{b['color']};--bk-ink:{b['ink']}">{cover_art(b['slug'], b['color'], b['ink'])}<span class="bt">{E(b['title'])}</span><span class="by">{E(C.SITE['name'])}</span></div><div><span class="label"><b>{t('Free', 'Gratuit')}</b><span>{tf(b['kind'], f, 'kind')}</span></span><h3 style="font-size:22px;margin:8px 0">{E(b['title'])}</h3><p style="margin:0 0 12px;font-size:15px;color:var(--encre)">{tf(b['line'], f, 'line')}</p>{cta}</div></article>"""

def page_books():
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>{t('Books', 'Livres')}</b><span>{len(C.BOOKS)} {t('titles', 'titres')}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('The bookcase.', 'La bibliothèque.')}</h1><p class="lede rv">{t('Books I wrote, and books I produce for others: essays and chronicles in French, technical books in English, and the project book format. New titles join this shelf as they are finished.', 'Les livres que j’ai écrits, et ceux que je produis pour d’autres : essais et chroniques en français, livres techniques en anglais, et le format du livre de projet. Les nouveaux titres rejoignent cette étagère quand ils sont terminés.')}</p></section>
<section class="block wrap" style="padding-top:10px" id="salon"><div class="sec-head"><span class="label rv"><b>{t('Reading room', 'Salon de lecture')}</b><span>{t('Free, complete, online', 'Gratuit, complet, en ligne')}</span></span><div class="row rv"><h2>{t('Read them here, for free.', 'Lisez-les ici, gratuitement.')}</h2></div><p class="lede rv">{t('Three books open to everyone: the full text, chapter by chapter, with a calm piece of music generated in your browser if you want company. Nothing to buy, nothing to sign up for.', 'Trois livres ouverts à tous : le texte intégral, chapitre par chapitre, avec une musique calme générée dans votre navigateur si vous voulez de la compagnie. Rien à acheter, rien à créer.')}</p></div>
<div class="grid g3 rv">{"".join(salon_card(b) for b in C.BOOKS if "free" in b)}</div></section>
<section class="block wrap" style="padding-top:10px"><div class="sec-head"><span class="label rv"><b>{t('All titles', 'Tous les titres')}</b></span></div><div class="bookcase">{"".join(tome(b) for b in C.BOOKS)}</div></section>
<section class="block wrap" style="padding-top:0"><div class="sec-head"><span class="label rv"><b>{t('Music', 'Musique')}</b><span>{t('For images', 'Pour les images')}</span></span><h2 class="rv">{t('An album for the screen.', 'Un album pour l’écran.')}</h2></div><div class="bookcase">{tome(C.ALBUM, True)}</div></section>
<section class="block wrap"><div class="card rv" style="padding:clamp(24px,4vw,40px)"><h2 style="font-size:clamp(26px,3vw,38px)">{t('Your book, produced.', 'Votre livre, produit.')}</h2><p class="lede">{t('From a manuscript or a pile of notes to a print ready PDF and an ebook, with figures, running heads and a cover.', 'D’un manuscrit ou d’une pile de notes à un PDF prêt à imprimer et un ebook, avec figures, titres courants et couverture.')}</p><p class="cta-row"><a class="btn" href="/services#books">{t('Book production service', 'Service de production de livres')} &rarr;</a></p></div></section>"""
    return head("Books", "Books written and produced by William Foteping.", "/books") + header("books") + body + footer()

def page_gallery():
    motion = "".join(vcard(v) for v in C.MOTION)
    edits = "".join(vcard(v) for v in C.EDITS)
    purposes = "".join(f'<a class="card" href="/work/{p["slug"]}#motion" style="gap:8px">{label(p["n"], p["kind"], p["year"])}<h3 style="font-size:20px">{E(p["title"])}</h3><p style="margin:0;font-size:14px;color:var(--encre)">{E(p["beats"][0]["t"])} {E(p["beats"][-1]["t"])}</p></a>' for p in C.PROJECTS)
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>{t('Gallery', 'Galerie')}</b><span>{t('Motion and edits', 'Motion et montages')}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('Moving images.', 'Images qui bougent.')}</h1><p class="lede rv">{t('Motion designs and one minute edits made for my platforms, in both aspect ratios and both languages where they exist. Everything I make with Bobine and for the Bobine landing page lands here.', 'Motion designs et montages d’une minute faits pour mes plateformes, dans les deux formats et les deux langues quand elles existent. Tout ce que je fais avec Bobine et pour la page d’accueil de Bobine arrive ici.')}</p></section>
<section class="block wrap" style="padding-top:10px"><div class="sec-head"><span class="label rv"><b>01</b><span>{t('Motion design', 'Motion design')}</span></span></div><div class="grid g2">{motion}</div></section>
<section class="block wrap"><div class="sec-head"><span class="label rv"><b>02</b><span>{t('Showcase edits', 'Montages de démonstration')}</span><span>{len(C.EDITS)}</span></span><p class="muted" style="margin:0">{t('Real stock footage, edited by Bobine, labelled as examples and never as customer work.', 'Vraies images de banque, montées par Bobine, présentées comme des exemples et jamais comme du travail client.')}</p></div><div class="grid g3">{edits}</div></section>
<section class="block wrap"><div class="sec-head"><span class="label rv"><b>03</b><span>{t('Walkthroughs', 'Visites guidées')}</span></span><p class="muted" style="margin:0">{t('One motion design per platform, built from its real screens: what it is, how to use it, where to write.', 'Un motion design par plateforme, fait de ses vrais écrans : ce que c’est, comment s’en servir, où écrire.')}</p></div><div class="grid g3">{"".join(f'<a class="card" href="/guides/{p["slug"]}#tour" style="gap:8px"><figure class="shot" style="margin:0 0 4px"><img src="/assets/shots/{p["shot"]}.webp" alt="" loading="lazy"></figure>{label(p["n"], p["kind"], p["year"])}<h3 style="font-size:20px">{t("How to use", "Mode d’emploi")} {E(p["title"])}</h3></a>' for p in C.PROJECTS)}</div></section>
<section class="block wrap"><div class="sec-head"><span class="label rv"><b>04</b><span>{t('Purpose motions', 'Les buts en mouvement')}</span></span><p class="muted" style="margin:0">{t('One short motion per project book, drawn in the browser.', 'Un court motion par livre de projet, dessiné dans le navigateur.')}</p></div><div class="grid g3">{purposes}</div></section>"""
    return head("Gallery", "Motion designs and video edits by William Foteping.", "/gallery") + header("gallery") + body + footer()

def page_journal():
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>Journal</b><span>{t('Life, process, regards', 'Vie, processus, regards')}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('A journal of making.', 'Un journal de fabrication.')}</h1><p class="lede rv">{t('How things get built, what the days look like, and galleries of the small things and landscapes around me that make me want to make more.', 'Comment les choses se construisent, à quoi ressemblent les journées, et des galeries des petites choses et des paysages autour de moi qui me donnent envie de faire plus.')}</p></section>
<section class="block wrap" style="padding-top:10px"><div class="posts">{"".join(post_row(p) for p in C.JOURNAL)}</div></section>"""
    return head("Journal", "Journal of William Foteping: process, life and galleries.", "/journal") + header("journal") + body + footer()

def page_post(p, prev, nxt):
    f = frj(p["slug"])
    d = datetime.date.fromisoformat(p["date"]).strftime("%d %B %Y")
    paras = "".join(f"<p>{tf(x, f, 'body', i)}</p>" for i, x in enumerate(p["body"]))
    gal = ""
    if p["images"]:
        gal = '<div class="gallery centered">' + "".join(f'<figure><img src="{E(sr) if sr.startswith("http") else "/" + E(sr)}" alt="{E(c, quote=True)}" loading="lazy"><figcaption>{tf(c, f, "captions", i)}</figcaption></figure>' for i, (sr, c) in enumerate(p["images"])) + "</div>"
    sound = f'<button class="btn ghost small sound" type="button" data-sound="{E(p["sound"])}" aria-pressed="false" data-on="{E(p["sound_label"], quote=True)}" data-off="{t("Sound off", "Couper le son")}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 10v4h4l5 4V6L8 10H4z"/><path d="M16 9a4 4 0 0 1 0 6"/></svg><span>{tf(p["sound_label"], f, "sound_label")}</span></button>'
    body = f"""<article class="block wrap"><div class="post-head"><span class="cat rv"><i style="color:{p['color']}"></i>{tf(p['cat'], f, 'cat')}</span> <span class="date">{d}</span><h1 class="rv" style="margin:14px 0 16px;font-size:clamp(34px,5vw,64px);max-width:22ch">{tf(p['title'], f, 'title')}</h1><p class="lede rv">{tf(p['lede'], f, 'lede')}</p><p class="cta-row rv" style="margin-top:10px">{sound}</p></div>
<div class="scene rv" style="--bk:{p['color']}"><canvas data-scene="{E(p['scene'])}" aria-label="{E(p['title'], quote=True)}, animated scene"></canvas></div>
<div class="prose rv centered">{paras}</div>{gal}
<nav class="cta-row" style="margin-top:48px;justify-content:space-between" aria-label="Posts"><a class="btn ghost small" href="/journal/{prev['slug']}">&larr; {E(prev['title'][:36])}</a><a class="btn ghost small" href="/journal/{nxt['slug']}">{E(nxt['title'][:36])} &rarr;</a></nav></article>"""
    return head(p["title"], p["lede"], f"/journal/{p['slug']}", THREE) + header("journal") + body + footer()

def page_services():
    cards = "".join(f"""<article class="card rv" id="{s['slug']}"><span class="label"><b>{str(i + 1).zfill(2)}</b><span>Service</span></span><h3>{tf(s['name'], frs(s['slug']), 'name')}</h3><p style="margin:0;color:var(--encre)">{tf(s['line'], frs(s['slug']), 'line')}</p><p class="mono muted" style="margin:0"><b style="color:var(--fusain)">{t('Example', 'Exemple')}:</b> {tf(s['example'], frs(s['slug']), 'example')}</p><ul class="ticks">{"".join(f"<li>{tf(d, frs(s['slug']), 'deliverables', k)}</li>" for k, d in enumerate(s['deliverables']))}</ul><div class="foot"><div class="price">{t('from', 'à partir de')} ${s['from']:,}<small>{tf(s['unit'], frs(s['slug']), 'unit')}</small></div><button class="btn small" type="button" data-pay="{s['slug']}">{t('Pay the deposit', 'Payer l’acompte')} ${s['deposit']:,}</button></div></article>""" for i, s in enumerate(C.SERVICES))
    steps = "".join(f'<div class="step rv"><span class="n">{i + 1}</span><div><h3>{t(h, FR.STEPS[i][0])}</h3><p>{t(d, FR.STEPS[i][1])}</p></div></div>' for i, (h, d) in enumerate(C.STEPS))
    opts = "".join(f'<option>{E(s["name"])}</option>' for s in C.SERVICES) + "<option>Something else</option>"
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>Services</b><span>{t('Prices in US dollars', 'Prix en dollars américains')}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('What I can do for you.', 'Ce que je peux faire pour vous.')}</h1><p class="lede rv">{t('Nine things I do well, with a real example of each, a starting price and the deposit that starts the work. Every engagement begins the same way: a brief, a booked meeting, a price in writing.', 'Neuf choses que je fais bien, avec un vrai exemple de chacune, un prix de départ et l’acompte qui lance le travail. Chaque mission commence de la même façon : un brief, un rendez-vous, un prix par écrit.')}</p></section>
<section class="block wrap" style="padding-top:10px"><div class="grid g3">{cards}</div><p id="pay-notice" class="notice" hidden style="margin-top:16px"></p></section>

<section class="block wrap" id="how"><div class="sec-head"><span class="label rv"><b>{t('How it works', 'Comment ça marche')}</b><span>{t('Five steps', 'Cinq étapes')}</span></span><h2 class="rv">{t('Brief. Book. Reserve. Meet. Build.', 'Brief. Réserver. Rencontrer. Construire.')}</h2></div><div class="steps">{steps}</div>
<div class="card rv" style="margin-top:28px;padding:clamp(22px,3vw,34px)"><div class="foot"><div><h3 style="font-size:24px">{t('Consultation, 45 minutes', 'Consultation, 45 minutes')}</h3><p style="margin:6px 0 0;color:var(--encre)">{t('On Zoom, Microsoft Teams or Google Meet. Credited to your project if you book within thirty days.', 'Sur Zoom, Microsoft Teams ou Google Meet. Créditée sur votre projet si vous réservez dans les trente jours.')}</p></div><div class="cta-row"><span class="price">${C.SITE['consult_price']}</span><button class="btn cobalt" type="button" data-pay="consultation">{t('Reserve and pay', 'Réserver et payer')}</button></div></div></div></section>

<section class="block wrap" id="brief"><div class="sec-head"><span class="label rv"><b>{t('The brief', 'Le brief')}</b><span>{t('Step one and two', 'Étapes un et deux')}</span></span><h2 class="rv">{t('Tell me exactly what you want.', 'Dites-moi exactement ce que vous voulez.')}</h2><p class="lede rv">{t('Sending the brief opens your email app with everything filled in. Then reserve the consultation, and I confirm a slot within a day.', 'Envoyer le brief ouvre votre application mail avec tout rempli. Réservez ensuite la consultation, et je confirme un créneau sous un jour.')}</p></div>
<form class="brief rv" novalidate>
<div class="f2"><div class="fr"><label for="name">{t('Your name', 'Votre nom')}</label><input id="name" name="name" required autocomplete="name"></div><div class="fr"><label for="email">Email</label><input id="email" name="email" type="email" required autocomplete="email"></div></div>
<div class="f2"><div class="fr"><label for="company">{t('Company or project', 'Entreprise ou projet')}</label><input id="company" name="company"></div><div class="fr"><label for="service">Service</label><select id="service" name="service">{opts}</select></div></div>
<div class="fr"><label>{t('Working language', 'Langue de travail')}</label><div class="choices"><label><input type="radio" name="lang" value="English" checked> English</label><label><input type="radio" name="lang" value="Français"> Français</label><label><input type="radio" name="lang" value="Both"> {t('Both', 'Les deux')}</label></div></div>
<div class="fr"><label for="want">{t('What do you want, concretely?', 'Que voulez-vous, concrètement ?')}</label><textarea id="want" name="want" required placeholder="A learning platform with paid courses and a free sample in each, in French and English."></textarea></div>
<div class="f2"><div class="fr"><label for="goal">{t('The goal it serves', 'Le but visé')}</label><textarea id="goal" name="goal" placeholder="Sell 100 seats in the first quarter."></textarea></div><div class="fr"><label for="audience">{t('Who it is for', 'Pour qui')}</label><textarea id="audience" name="audience" placeholder="Beginners in IT, mostly on phones."></textarea></div></div>
<div class="f2"><div class="fr"><label for="existing">{t('What exists today', 'Ce qui existe aujourd’hui')}</label><textarea id="existing" name="existing" placeholder="A logo, twenty videos, a mailing list."></textarea></div><div class="fr"><label for="refs">{t('References you like, links', 'Références que vous aimez, liens')}</label><textarea id="refs" name="refs" placeholder="Two or three sites, books or videos."></textarea></div></div>
<div class="f2"><div class="fr"><label for="budget">{t('Budget range', 'Fourchette de budget')}</label><select id="budget" name="budget"><option>Under 1,000</option><option>1,000 to 3,000</option><option>3,000 to 8,000</option><option>8,000 to 20,000</option><option>Above 20,000</option><option>Not sure yet</option></select></div><div class="fr"><label for="deadline">{t('Deadline', 'Échéance')}</label><input id="deadline" name="deadline" placeholder="End of November"></div></div>
<hr class="rule"><div class="fr"><label>{t('Meeting platform', 'Plateforme de réunion')}</label><div class="choices"><label><input type="radio" name="platform" value="Zoom" checked> Zoom</label><label><input type="radio" name="platform" value="Microsoft Teams"> Microsoft Teams</label><label><input type="radio" name="platform" value="Google Meet"> Google Meet</label></div></div>
<div class="f2"><div class="fr"><label for="tz">{t('Your timezone', 'Votre fuseau horaire')}</label><input id="tz" name="tz" placeholder="New York, Paris, Douala"></div><div class="fr"><label for="slot1">{t('Preferred slot 1', 'Créneau préféré 1')}</label><input id="slot1" name="slot1" required placeholder="Tue 21 Oct, 6 to 7 pm"></div></div>
<div class="f2"><div class="fr"><label for="slot2">{t('Preferred slot 2', 'Créneau préféré 2')}</label><input id="slot2" name="slot2" placeholder="Wed 22 Oct, 12 to 1 pm"></div><div class="fr"><label for="slot3">{t('Preferred slot 3', 'Créneau préféré 3')}</label><input id="slot3" name="slot3" placeholder="Sat 25 Oct, morning"></div></div>
<div class="cta-row"><button class="btn" type="submit">{t('Send the brief by email', 'Envoyer le brief par email')}</button></div>
<p id="brief-notice" class="notice" hidden>{t('Your email app should have opened with the brief. If it did not, copy the brief below and send it to', 'Votre application mail devrait s’être ouverte avec le brief. Sinon, copiez le brief ci-dessous et envoyez-le à')} {E(C.SITE['email'])}.</p>
<pre class="summary" aria-live="polite"></pre>
<div id="after-brief" hidden class="cta-row"><button class="btn ghost small" type="button" id="copy-brief">{t('Copy the brief', 'Copier le brief')}</button><input type="hidden" id="b-email"><button class="btn cobalt" type="button" data-pay="consultation">{t('Step three: reserve the consultation', 'Étape trois : réserver la consultation')} ${C.SITE['consult_price']}</button></div>
</form></section>"""
    return head("Services", "Services and prices: platforms, networks, books, motion, content systems, localisation.", "/services") + header("services") + body + footer()


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
        fh = f["rooms"][i][2] if i < len(f.get("rooms", [])) else []
        how = "".join(f"<li>{t(h, fh[k] if k < len(fh) else None)}</li>" for k, h in enumerate(r["how"]))
        rt = f["rooms"][i][0] if i < len(f.get("rooms", [])) else None; rx = f["rooms"][i][1] if i < len(f.get("rooms", [])) else None
        rooms += f"""<article class="room rv"><figure class="shot"><img src="{shot_path(r.get('shot'), p)}" alt="{E(r['title'], quote=True)}, screenshot" loading="lazy"><figcaption>{E(p['title'])}, {t(r['title'], rt)}</figcaption></figure><div><span class="label"><b>{str(i + 1).zfill(2)}</b><span>{t(r['title'], rt)}</span></span><h3 style="margin:10px 0 8px">{t(r['title'], rt)}</h3><p style="font-size:17px;line-height:1.65;color:var(--encre)">{t(r['text'], rx)}</p><h4 class="mono muted" style="margin:14px 0 6px;letter-spacing:.14em">{t('HOW TO USE IT', 'MODE D’EMPLOI')}</h4><ol class="how">{how}</ol></div></article>"""
    tips = "".join(f"<li>{tf(x, f, 'tips', i)}</li>" for i, x in enumerate(g["tips"]))
    faq = "".join(f'<details class="faq"><summary>{tf(q, f, "faq", i, 0)}</summary><p>{tf(a, f, "faq", i, 1)}</p></details>' for i, (q, a) in enumerate(g["faq"]))
    contact = "".join(f'<a class="card" href="{E(h)}"{" target=\"_blank\" rel=\"noopener\"" if h.startswith("http") else ""}><span class="label"><b>Contact</b></span><h3 style="font-size:20px">{tf(l, f, "contact", i)}</h3></a>' for i, (l, h) in enumerate(g["contact"]))
    visit = f'<a class="btn" href="{E(p["url"])}" target="_blank" rel="noopener">{t("Open", "Ouvrir")} {E(p["title"])} &rarr;</a>' if p["url"] else ""
    body = f"""<section class="block wrap" style="padding-bottom:24px"><span class="label rv"><b>N° {E(p['n'])}</b><span>{t('How to use', 'Mode d’emploi')}</span><span>{tf(p['kind'], fp, 'kind')}</span></span><h1 class="rv" style="margin:14px 0 12px;font-size:clamp(34px,5.5vw,70px)">{t('How to use', 'Comment utiliser')} {E(p['title'])}</h1><p class="lede rv">{tf(g['audience'], f, 'audience')}</p><p class="cta-row rv" style="margin-top:16px">{visit}<a class="btn ghost" href="/work/{p['slug']}">{t('Read the book', 'Lire le livre')}</a><a class="btn ghost" href="#contact">Contact</a></p></section>
<section class="wrap rv"><div class="sec-head" style="margin-bottom:14px"><span class="label"><b>{t('Walkthrough', 'Visite guidée')}</b><span>{t('Motion design, real screens', 'Motion design, vrais écrans')}</span></span></div>{tour(p, g, f)}<p class="muted" style="font-size:13px;margin-top:10px">{t('It plays by itself. Tap a dot or the arrows to move, Pause to stop.', 'Elle se joue toute seule. Touchez un point ou les flèches pour avancer, Pause pour arrêter.')}</p></section>
<section class="block wrap"><div class="sec-head"><span class="label rv"><b>01</b><span>{t('Get started', 'Pour commencer')}</span></span><h2 class="rv">{t('Five steps, five minutes.', 'Cinq étapes, cinq minutes.')}</h2></div><div class="steps">{start}</div></section>
<section class="block wrap" style="padding-top:0"><div class="sec-head"><span class="label rv"><b>02</b><span>{t('Room by room', 'Pièce par pièce')}</span></span><h2 class="rv">{t('What is inside, and how to use it.', 'Ce qu’il y a dedans, et comment s’en servir.')}</h2></div><div class="rooms">{rooms}</div></section>
<section class="block wrap" style="padding-top:0"><div class="grid g2"><div class="card rv"><span class="label"><b>03</b><span>{t('Tips', 'Conseils')}</span></span><ul class="ticks" style="font-size:16px">{tips}</ul></div><div class="card rv"><span class="label"><b>04</b><span>FAQ</span></span><div>{faq}</div></div></div></section>
<section class="block wrap" id="contact" style="padding-top:0"><div class="sec-head"><span class="label rv"><b>05</b><span>Contact</span></span><h2 class="rv">{t('Contact about', 'Contact à propos de')} {E(p['title'])}</h2></div><div class="grid g3 rv">{contact}<a class="card" href="/services#brief"><span class="label"><b>{t('Project', 'Projet')}</b></span><h3 style="font-size:20px">{t('Want something like this built for you?', 'Vous voulez la même chose pour vous ?')}</h3><span class="mono muted">{t('Send a brief', 'Envoyer un brief')} &rarr;</span></a></div></section>"""
    return head("How to use " + p["title"], f"How to use {p['title']}: walkthrough, getting started, room by room, tips, FAQ and contact.", f"/guides/{p['slug']}") + header("work") + body + footer()

def page_contact():
    body = f"""<section class="block wrap"><span class="label rv"><b>Contact</b><span>{E(C.SITE['location'])}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('Write to me.', 'Écrivez-moi.')}</h1><p class="lede rv">{t('For a project, start with the brief on the services page; it saves us a meeting. For everything else, an email is best. I answer within a day, in French or English.', 'Pour un projet, commencez par le brief sur la page services ; cela nous épargne une réunion. Pour tout le reste, un email est le mieux. Je réponds sous un jour, en français ou en anglais.')}</p>
<div class="grid g2 rv" style="margin-top:28px"><div class="card"><span class="label"><b>Email</b></span><h3><a href="mailto:{E(C.SITE['email'])}">{E(C.SITE['email'])}</a></h3><p style="margin:0;color:var(--encre)">{t('Projects, books, talks, questions.', 'Projets, livres, conférences, questions.')}</p></div><div class="card"><span class="label"><b>{t('Meetings', 'Réunions')}</b></span><h3>Zoom, Microsoft Teams, Google Meet</h3><p style="margin:0;color:var(--encre)">{t('Booked through the brief, confirmed by email.', 'Réservées via le brief, confirmées par email.')}</p><p class="cta-row" style="margin-top:10px"><a class="btn small" href="/services#brief">{t('Open the brief', 'Ouvrir le brief')}</a></p></div></div>
<div class="grid g3 rv" style="margin-top:18px">{"".join(f'<a class="card" href="{E(p["url"])}" target="_blank" rel="noopener" style="gap:6px"><span class="label"><b>N° {E(p["n"])}</b></span><h3 style="font-size:20px">{E(p["title"])}</h3><span class="mono muted">{E(p["link_label"])}</span></a>' for p in C.PROJECTS if p["url"])}</div></section>"""
    return head("Contact", "Contact William Foteping.", "/contact") + header("contact") + body + footer()

def page_thanks():
    body = f"""<section class="block wrap"><span class="label rv"><b>{t('Reserved', 'Réservé')}</b></span><h1 class="rv" style="margin:16px 0 14px">{t('Thank you.', 'Merci.')}</h1><p class="lede rv">{t('Your payment went through. I will confirm your slot by email within a day and send a calendar invitation for Zoom, Microsoft Teams or Google Meet, as you chose.', 'Votre paiement est passé. Je confirme votre créneau par email sous un jour et j’envoie une invitation pour Zoom, Microsoft Teams ou Google Meet, selon votre choix.')}</p><p class="mono muted" hidden>{t('Reference', 'Référence')}: <span id="session"></span></p><p class="cta-row"><a class="btn" href="/">{t('Back to the start', 'Retour au début')}</a></p></section>"""
    return head("Thank you", "Reservation confirmed.", "/thanks") + header("services") + body + footer()

def page_404():
    body = f"""<section class="block wrap"><span class="label rv"><b>404</b></span><h1 class="rv" style="margin:16px 0 14px">{t('That shelf is empty.', 'Cette étagère est vide.')}</h1><p class="cta-row"><a class="btn" href="/">{t('Back to the library', 'Retour à la bibliothèque')}</a></p></section>"""
    return head("Not found", "Page not found.", "/404") + header("") + body + footer()

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#F6F2EA"/><circle cx="32" cy="32" r="13" fill="#1C3FBF"/><path d="M12 52 L32 10 L52 52" fill="none" stroke="#1B1A17" stroke-width="3" stroke-linejoin="round"/></svg>"""

import hashlib
def asset_version():
    here = os.path.dirname(os.path.abspath(__file__)); h = hashlib.sha1()
    for n in ("style.css", "app.js", "scenes.js", "salon.css", "salon.js"):
        p = os.path.join(here, "assets", n)
        if os.path.exists(p): h.update(open(p, "rb").read())
    return h.hexdigest()[:8]
V = asset_version()

def write(path, s, strict=True):
    for bad, name in (("—", "em dash"), ("–", "en dash")):
        assert not strict or bad not in s, f"{name} found in {path}"
    import re as _re
    s = _re.sub(r'(/assets/(?:style|salon)\.css|/assets/(?:app|scenes|salon)\.js)(?=["\'])', lambda m: m.group(1) + "?v=" + V, s)
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
    write("work/index.html", page_work())
    n = len(C.PROJECTS)
    for i, p in enumerate(C.PROJECTS): write(f"work/{p['slug']}.html", page_project(p, C.PROJECTS[i - 1], C.PROJECTS[(i + 1) % n]))
    for p in C.PROJECTS: write(f"guides/{p['slug']}.html", page_guide(p))
    write("books.html", page_books())
    for b in SALON.load_books(): write(f"lire/{b['slug']}.html", SALON.page(b, t, head, header, footer, cover_art), strict=False)
    write("gallery.html", page_gallery())
    write("journal/index.html", page_journal())
    m = len(C.JOURNAL)
    for i, p in enumerate(C.JOURNAL): write(f"journal/{p['slug']}.html", page_post(p, C.JOURNAL[i - 1], C.JOURNAL[(i + 1) % m]))
    write("services.html", page_services())
    write("contact.html", page_contact())
    write("thanks.html", page_thanks())
    write("404.html", page_404())
    pages = ["/", "/work"] + [f"/work/{p['slug']}" for p in C.PROJECTS] + [f"/guides/{p['slug']}" for p in C.PROJECTS] + ["/books"] + [f"/lire/{b['slug']}" for b in SALON.load_books()] + ["/gallery", "/journal"] + [f"/journal/{p['slug']}" for p in C.JOURNAL] + ["/services", "/contact"]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{C.SITE['url']}{u}</loc></url>" for u in pages) + "</urlset>")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {C.SITE['url']}/sitemap.xml\n")
    print("built", len(pages), "pages into", OUT)

if __name__ == "__main__":
    main()
