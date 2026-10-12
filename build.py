#!/usr/bin/env python3
"""Builds the static site into dist/. Run: python3 build.py"""
import os, shutil, json, html, datetime
import content as C
from guides import GUIDES

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
E = html.escape

def t(en, fr):
    """Bilingual inline text: English shown, French swapped in by the toggle."""
    return f'<span data-fr="{E(fr, quote=True)}">{E(en)}</span>'

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
    return """<div class="glass rv" aria-hidden="true"><svg viewBox="0 0 400 300" fill="none" stroke="currentColor" stroke-width="1.2" style="color:#1C3FBF">
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
<div>{hero_art()}<div class="hero-aside rv"><div class="kv"><span>{t('Trade', 'Métier')}</span><span>{t('Senior network administrator, cloud and infrastructure', 'Administrateur réseau senior, cloud et infrastructure')}</span></div><div class="kv"><span>{t('Ventures', 'Projets')}</span><span>Uplink IT Academy, Bobine, Lemon Network Solutions, Droit Facile</span></div><div class="kv"><span>{t('Writing', 'Écriture')}</span><span>{t('Essays, chronicles, technical books, in French and English', 'Essais, chroniques, livres techniques, en français et en anglais')}</span></div><div class="kv"><span>{t('Certified', 'Certifié')}</span><span>CCNA, Azure Administrator</span></div></div></div></div></section>
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
    return head("", C.SITE["description"], "/") + header("home") + body + footer()

def tome(b):
    where = "".join(f'<a class="btn ghost small" href="{E(u)}" target="_blank" rel="noopener">{E(l)} &rarr;</a>' for l, u in b["where"])
    pages = f'<div><span class="k">Format</span> {E(b["pages"])}</div>' if b["pages"] else ""
    return f"""<article class="tome"><div class="cover" style="--bk:{b['color']};--bk-ink:{b['ink']}"><span class="bn">{E(b['lang'].upper())}</span><span class="bt">{E(b['title'])}</span><span class="bk">{E(b['kind'])}<br>{E(b['year'])}</span></div>
<div class="meta"><h3 style="font-size:22px">{E(b['title'])}</h3><p style="margin:4px 0 6px;font-size:15px;color:var(--encre)">{E(b['line'])}</p>{pages}{('<div class="cta-row" style="margin-top:6px">' + where + '</div>') if where else ''}</div></article>"""

def vcard(v):
    first = v["variants"][0]
    vars_ = "".join(f'<button type="button" data-src="{E(u, quote=True)}" data-ratio="{E(r, quote=True)}" aria-pressed="{"true" if i == 0 else "false"}">{E(l)}</button>' for i, (l, u, r) in enumerate(v["variants"]))
    return f"""<article class="vcard" data-src="{E(first[1], quote=True)}" data-ratio="{E(first[2], quote=True)}" data-poster="{E(v['poster'], quote=True)}"><div class="media"><img src="{E(v['poster'])}" alt="{E(v['title'], quote=True)}, still" loading="lazy"><button class="play" type="button" aria-label="Play {E(v['title'], quote=True)}"><span><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span></button></div>
<div class="body"><span class="label"><b>{E(v['kind'])}</b><span>{E(v['year'])}</span></span><h3 style="font-size:22px">{E(v['title'])}</h3><p style="margin:0;font-size:14px;color:var(--encre)">{E(v['line'])}</p><div class="vars">{vars_}</div></div></article>"""

def post_row(p):
    d = datetime.date.fromisoformat(p["date"]).strftime("%d %b %Y")
    return f"""<article class="post"><a class="th" href="/journal/{p['slug']}"><img src="{E(p['thumb']) if p['thumb'].startswith('http') else '/' + E(p['thumb'])}" alt="" loading="lazy"></a><div><span class="cat"><i style="color:{p['color']}"></i>{E(p['cat'])}</span> <span class="date">{d}</span><h3><a href="/journal/{p['slug']}">{E(p['title'])}</a></h3><p class="lede" style="font-size:17px">{E(p['lede'])}</p><a class="btn ghost small" href="/journal/{p['slug']}">{t('Read', 'Lire')} &rarr;</a></div></article>"""

# ---------------------------------------------------------------------------
def page_work():
    cards = "".join(f"""<a class="card rv" href="/work/{p['slug']}" style="gap:10px"><figure class="shot" style="margin:0 0 6px"><img src="/assets/shots/{p['shot']}.webp" alt="{E(p['title'], quote=True)}, screenshot" loading="lazy"></figure>{label(p['n'], p['kind'], p['year'])}<h3>{E(p['title'])}</h3><p style="margin:0;color:var(--encre)">{E(p['line'])}</p><span class="mono muted">{E(p['status'])}</span><span class="mono" style="color:var(--cobalt)">{t('Book', 'Livre')} &rarr; &nbsp; <a href="/guides/{p['slug']}" style="text-decoration:underline">{t('How to use', 'Mode d’emploi')}</a></span></a>""" for p in C.PROJECTS)
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>{t('Work', 'Travaux')}</b><span>{len(C.PROJECTS)} {t('books on the shelf', 'livres sur l’étagère')}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('The library.', 'La bibliothèque.')}</h1><p class="lede rv">{t('Platforms, tools and sites I designed and built, presented as books: take one down, read the purpose, the problem, what I built and how it works, and watch a short motion that says why it exists.', 'Plateformes, outils et sites que j’ai conçus et construits, présentés comme des livres : prenez-en un, lisez le but, le problème, ce que j’ai construit et comment ça marche, et regardez une courte animation qui dit pourquoi il existe.')}</p></section>
<section class="wrap">{shelf(C.PROJECTS)}</section>
<section class="block wrap"><div class="sec-head"><span class="label rv"><b>{t('Index', 'Index')}</b><span>{t('All works', 'Toutes les œuvres')}</span></span></div><div class="grid g3">{cards}</div></section>"""
    return head("Work", "Platforms, tools and sites by William Foteping, presented as books.", "/work") + header("work") + body + footer()

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
def page_project(p, prev, nxt):
    chapters = "".join(f'<div class="chapter rv"><span class="ch">{ROMAN[i]}</span><div><h3>{E(h)}</h3><p>{E(txt)}</p></div></div>' for i, (h, txt) in enumerate(p["chapters"]))
    facts = "".join(f'<div><span>{E(k)}</span><span>{E(v)}</span></div>' for k, v in p["facts"])
    hl = "".join(f"<li>{E(h)}</li>" for h in p["highlights"])
    visit = f'<a class="btn" href="{E(p["url"])}" target="_blank" rel="noopener">{t("Visit", "Visiter")} {E(p["link_label"])} &rarr;</a>' if p["url"] else f'<span class="notice">{t("This one is a private build for now. Ask me for a walkthrough.", "Celui-ci est une version privée pour le moment. Demandez-moi une visite.")}</span>'
    body = f"""<section class="block wrap"><div class="open">
<aside><div class="cover" style="--bk:{p['color']};--bk-ink:{p['ink']}"><span class="bn">N° {E(p['n'])}</span><span class="bt">{E(p['title'])}</span><span class="bk">{E(p['kind'])}<br>{E(p['year'])}<br>{E(p['status'])}</span></div>
<div class="facts">{facts}<div><span>Stack</span><span>{E(p['stack'])}</span></div></div></aside>
<div><span class="label rv"><b>N° {E(p['n'])}</b><span>{E(p['kind'])}</span><span>{E(p['year'])}</span></span><h1 class="rv" style="margin:14px 0 12px;font-size:clamp(36px,5.5vw,72px)">{E(p['title'])}</h1><p class="lede rv">{E(p['line'])}</p><p class="cta-row rv" style="margin:18px 0 34px">{visit}<a class="btn cobalt" href="/guides/{p['slug']}">{t('How to use it', 'Mode d’emploi')}</a><a class="btn ghost" href="#motion">{t('Watch the purpose', 'Voir le but en mouvement')}</a></p>
<figure class="shot rv"><img src="/assets/shots/{p['shot']}.webp" alt="{E(p['title'], quote=True)}, screenshot"><figcaption>{E(p['title'])}, {t('screenshot', 'capture d’écran')}</figcaption></figure>
<div class="chapters" style="margin-top:40px">{chapters}
<div class="chapter rv" id="motion"><span class="ch">{ROMAN[len(p['chapters'])]}</span><div><h3>{t('The purpose, in motion', 'Le but, en mouvement')}</h3><p style="margin-bottom:14px">{t('A short motion design made for this book: four beats, one drawn shape each, the reason the project exists. Tap it to step through.', 'Un court motion design fait pour ce livre : quatre temps, une forme dessinée à chaque fois, la raison d’être du projet. Touchez pour avancer.')}</p>{stage(p, p['title'])}</div></div>
<div class="chapter rv"><span class="ch">{ROMAN[len(p['chapters']) + 1]}</span><div><h3>{t('In short', 'En bref')}</h3><ul class="ticks">{hl}</ul><p class="cta-row" style="margin-top:18px">{visit}</p></div></div></div>
<nav class="cta-row" style="margin-top:48px;justify-content:space-between" aria-label="Books"><a class="btn ghost small" href="/work/{prev['slug']}">&larr; {E(prev['title'])}</a><a class="btn ghost small" href="/work/{nxt['slug']}">{E(nxt['title'])} &rarr;</a></nav></div></div></section>"""
    return head(p["title"], p["line"], f"/work/{p['slug']}") + header("work") + body + footer()

def page_books():
    body = f"""<section class="block wrap" style="padding-bottom:20px"><span class="label rv"><b>{t('Books', 'Livres')}</b><span>{len(C.BOOKS)} {t('titles', 'titres')}</span></span><h1 class="rv" style="margin:16px 0 14px">{t('The bookcase.', 'La bibliothèque.')}</h1><p class="lede rv">{t('Books I wrote, and books I produce for others: essays and chronicles in French, technical books in English, and the project book format. New titles join this shelf as they are finished.', 'Les livres que j’ai écrits, et ceux que je produis pour d’autres : essais et chroniques en français, livres techniques en anglais, et le format du livre de projet. Les nouveaux titres rejoignent cette étagère quand ils sont terminés.')}</p></section>
<section class="block wrap" style="padding-top:10px"><div class="bookcase">{"".join(tome(b) for b in C.BOOKS)}</div></section>
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
    d = datetime.date.fromisoformat(p["date"]).strftime("%d %B %Y")
    paras = "".join(f"<p>{E(x)}</p>" for x in p["body"])
    gal = ""
    if p["images"]:
        gal = '<div class="gallery">' + "".join(f'<figure><img src="{E(s) if s.startswith('http') else '/' + E(s)}" alt="{E(c, quote=True)}" loading="lazy"><figcaption>{E(c)}</figcaption></figure>' for s, c in p["images"]) + "</div>"
    body = f"""<article class="block wrap"><span class="cat rv"><i style="color:{p['color']}"></i>{E(p['cat'])}</span> <span class="date">{d}</span><h1 class="rv" style="margin:14px 0 16px;font-size:clamp(34px,5vw,64px);max-width:20ch">{E(p['title'])}</h1><p class="lede rv">{E(p['lede'])}</p>
<figure class="shot rv" style="margin:28px 0"><img src="{E(p['thumb']) if p['thumb'].startswith('http') else '/' + E(p['thumb'])}" alt=""></figure>
<div class="prose rv">{paras}</div>{gal}
<nav class="cta-row" style="margin-top:48px;justify-content:space-between" aria-label="Posts"><a class="btn ghost small" href="/journal/{prev['slug']}">&larr; {E(prev['title'][:36])}</a><a class="btn ghost small" href="/journal/{nxt['slug']}">{E(nxt['title'][:36])} &rarr;</a></nav></article>"""
    return head(p["title"], p["lede"], f"/journal/{p['slug']}") + header("journal") + body + footer()

def page_services():
    cards = "".join(f"""<article class="card rv" id="{s['slug']}"><span class="label"><b>{str(i + 1).zfill(2)}</b><span>Service</span></span><h3>{E(s['name'])}</h3><p style="margin:0;color:var(--encre)">{E(s['line'])}</p><p class="mono muted" style="margin:0"><b style="color:var(--fusain)">{t('Example', 'Exemple')}:</b> {E(s['example'])}</p><ul class="ticks">{"".join(f"<li>{E(d)}</li>" for d in s['deliverables'])}</ul><div class="foot"><div class="price">{t('from', 'à partir de')} ${s['from']:,}<small>{E(s['unit'])}</small></div><button class="btn small" type="button" data-pay="{s['slug']}">{t('Pay the deposit', 'Payer l’acompte')} ${s['deposit']:,}</button></div></article>""" for i, s in enumerate(C.SERVICES))
    steps = "".join(f'<div class="step rv"><span class="n">{i + 1}</span><div><h3>{E(h)}</h3><p>{E(d)}</p></div></div>' for i, (h, d) in enumerate(C.STEPS))
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

def tour(p, g):
    scenes = [{"k": sc["k"], "t": sc["t"], "c": sc["c"], "img": shot_path(sc.get("shot"), p), "f": sc["f"]} for sc in g["scenes"]]
    data = E(json.dumps(scenes, ensure_ascii=False), quote=True)
    return f"""<div class="tour" id="tour" data-scenes="{data}" style="--bk:{p['color']};--bk-ink:{p['ink']}" tabindex="0" aria-label="{E(p['title'], quote=True)} walkthrough">
<div class="tour-stage"><img class="tour-img" alt="" src="{scenes[0]['img']}"><svg class="tour-hl" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><rect x="0" y="0" width="100" height="100" rx="1.2"/></svg><div class="tour-n mono"></div></div>
<div class="tour-cap"><span class="k mono"></span><h3 class="t"></h3><p class="c"></p></div>
<div class="tour-ctl"><button type="button" class="t-prev" aria-label="Previous">&larr;</button><div class="dots" role="tablist"></div><button type="button" class="t-play">PAUSE</button><button type="button" class="t-next" aria-label="Next">&rarr;</button></div></div>"""

def page_guide(p):
    g = GUIDES[p["slug"]]
    start = "".join(f'<div class="step rv"><span class="n">{i + 1}</span><div><p style="font-size:17px">{E(x)}</p></div></div>' for i, x in enumerate(g["start"]))
    rooms = ""
    for i, r in enumerate(g["rooms"]):
        how = "".join(f"<li>{E(h)}</li>" for h in r["how"])
        rooms += f"""<article class="room rv"><figure class="shot"><img src="{shot_path(r.get('shot'), p)}" alt="{E(r['title'], quote=True)}, screenshot" loading="lazy"><figcaption>{E(p['title'])}, {E(r['title'])}</figcaption></figure><div><span class="label"><b>{str(i + 1).zfill(2)}</b><span>{E(r['title'])}</span></span><h3 style="margin:10px 0 8px">{E(r['title'])}</h3><p style="font-size:17px;line-height:1.65;color:var(--encre)">{E(r['text'])}</p><h4 class="mono muted" style="margin:14px 0 6px;letter-spacing:.14em">HOW TO USE IT</h4><ol class="how">{how}</ol></div></article>"""
    tips = "".join(f"<li>{E(x)}</li>" for x in g["tips"])
    faq = "".join(f'<details class="faq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in g["faq"])
    contact = "".join(f'<a class="card" href="{E(h)}"{" target=\"_blank\" rel=\"noopener\"" if h.startswith("http") else ""}><span class="label"><b>Contact</b></span><h3 style="font-size:20px">{E(l)}</h3></a>' for l, h in g["contact"])
    visit = f'<a class="btn" href="{E(p["url"])}" target="_blank" rel="noopener">{t("Open", "Ouvrir")} {E(p["title"])} &rarr;</a>' if p["url"] else ""
    body = f"""<section class="block wrap" style="padding-bottom:24px"><span class="label rv"><b>N° {E(p['n'])}</b><span>{t('How to use', 'Mode d’emploi')}</span><span>{E(p['kind'])}</span></span><h1 class="rv" style="margin:14px 0 12px;font-size:clamp(34px,5.5vw,70px)">{t('How to use', 'Comment utiliser')} {E(p['title'])}</h1><p class="lede rv">{E(g['audience'])}</p><p class="cta-row rv" style="margin-top:16px">{visit}<a class="btn ghost" href="/work/{p['slug']}">{t('Read the book', 'Lire le livre')}</a><a class="btn ghost" href="#contact">Contact</a></p></section>
<section class="wrap rv"><div class="sec-head" style="margin-bottom:14px"><span class="label"><b>{t('Walkthrough', 'Visite guidée')}</b><span>{t('Motion design, real screens', 'Motion design, vrais écrans')}</span></span></div>{tour(p, g)}<p class="muted" style="font-size:13px;margin-top:10px">{t('It plays by itself. Tap a dot or the arrows to move, Pause to stop.', 'Elle se joue toute seule. Touchez un point ou les flèches pour avancer, Pause pour arrêter.')}</p></section>
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

def write(path, s):
    for bad, name in (("—", "em dash"), ("–", "en dash")):
        assert bad not in s, f"{name} found in {path}"
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
    write("gallery.html", page_gallery())
    write("journal/index.html", page_journal())
    m = len(C.JOURNAL)
    for i, p in enumerate(C.JOURNAL): write(f"journal/{p['slug']}.html", page_post(p, C.JOURNAL[i - 1], C.JOURNAL[(i + 1) % m]))
    write("services.html", page_services())
    write("contact.html", page_contact())
    write("thanks.html", page_thanks())
    write("404.html", page_404())
    pages = ["/", "/work"] + [f"/work/{p['slug']}" for p in C.PROJECTS] + [f"/guides/{p['slug']}" for p in C.PROJECTS] + ["/books", "/gallery", "/journal"] + [f"/journal/{p['slug']}" for p in C.JOURNAL] + ["/services", "/contact"]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{C.SITE['url']}{u}</loc></url>" for u in pages) + "</urlset>")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {C.SITE['url']}/sitemap.xml\n")
    print("built", len(pages), "pages into", OUT)

if __name__ == "__main__":
    main()
