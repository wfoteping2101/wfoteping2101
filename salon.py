"""The reading room: free books as rich HTML pages with chapter navigation and calm music.
Sources live in books/*.json. Each book page is written to dist/lire/<slug>.html."""
import os, re, json, html
E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))

def md_inline(s):
    s = E(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", s)
    return s

def md_block(body):
    """A small markdown: ##/### headings, paragraphs, dash and numbered lists, > quotes, | tables |, --- rules."""
    out, para, lst, quote, table = [], [], [], [], []
    state = {"ol": False}
    def flush_p():
        if para: out.append(f"<p>{md_inline(' '.join(para))}</p>"); para.clear()
    def flush_l():
        if lst:
            tag = "ol" if state["ol"] else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{md_inline(x)}</li>" for x in lst) + f"</{tag}>"); lst.clear()
    def flush_q():
        if quote:
            paras = "</p><p>".join(md_inline(x) for x in " \n".join(quote).split(" \n \n"))
            out.append(f'<blockquote class="pull"><p>{paras}</p></blockquote>'); quote.clear()
    def flush_t():
        if table:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in table if not re.match(r"^\|?\s*:?-{2,}", r.strip())]
            if rows:
                head, rest = rows[0], rows[1:]
                h = "".join(f"<th>{md_inline(c)}</th>" for c in head)
                bd = "".join("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>" for r in rest)
                out.append(f'<div class="tbl"><table><thead><tr>{h}</tr></thead><tbody>{bd}</tbody></table></div>')
            table.clear()
    def flush_all(): flush_p(); flush_l(); flush_q(); flush_t()
    for line in body.split("\n"):
        line = line.rstrip()
        if not line.strip(): flush_p(); flush_l(); flush_t(); (quote.append("") if quote else None); continue
        if line.lstrip().startswith("|"): flush_p(); flush_l(); flush_q(); table.append(line); continue
        if line.startswith(">"):
            flush_p(); flush_l(); flush_t(); quote.append(line.lstrip(">").strip()); continue
        if quote: flush_q()
        if re.match(r"^(-{3,}|\*{3,})$", line.strip()): flush_all(); out.append('<p class="scene"><span>&middot;</span></p>'); continue
        m = re.match(r"^(#{2,4})\s+(.*)$", line)
        if m:
            flush_all()
            txt = m.group(2).strip(); lvl = len(m.group(1))
            n = re.match(r"^(\d+)\.\s+(.*)$", txt)
            cls = "sec" if lvl == 2 else "sub"
            if n: out.append(f'<h3 class="{cls}"><span class="sn">{n.group(1)}</span>{md_inline(n.group(2))}</h3>')
            else: out.append(f'<h3 class="{cls}">{md_inline(txt)}</h3>' if lvl == 2 else f'<h4 class="{cls}">{md_inline(txt)}</h4>')
            continue
        mo = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if mo and (not lst or state["ol"]):
            flush_p(); state["ol"] = True; lst.append(mo.group(1)); continue
        if re.match(r"^\s*[-•*]\s+", line):
            if lst and state["ol"]: flush_l()
            flush_p(); state["ol"] = False; lst.append(re.sub(r"^\s*[-•*]\s+", "", line)); continue
        if lst and line.startswith("  "): lst[-1] += " " + line.strip(); continue
        flush_l(); para.append(line.strip())
    flush_all()
    return "\n".join(out)

def clean_html(h):
    """Novlr export: p, strong, em, u, br. Keep it, tidy it, mark scene labels."""
    h = h.replace(" ", " ")
    h = re.sub(r"<p>\s*(?:&nbsp;|\s)*</p>", "", h)
    h = re.sub(r"<p>\s*<u>\s*Chapitre\s+\d+\s*</u>\s*</p>", "", h, flags=re.I)
    h = re.sub(r"<p>\s*(?:<[^>]+>\s*)*Sc[èe]ne\s*(\d+)\s*:?\s*(?:</[^>]+>\s*)*</p>", r'<p class="scene"><span>Scène \1</span></p>', h, flags=re.I)
    h = re.sub(r"<p>\s*\*\s*\*\s*\*\s*</p>", '<p class="scene"><span>&middot;</span></p>', h)
    h = re.sub(r"<p>(\s*<br\s*/?>\s*)+</p>", "", h)
    return h

BOOK_META = {
    "bobine-la-methode": {"title": "Bobine, la méthode", "subtitle": "Planifier, filmer, monter et vendre avec l'IA", "year": "2026", "color": "#16130F", "ink": "#E9B44C", "seed": "bobine-la-methode",
        "desc_en": "The complete creator's method: an idea bank, one shooting day for a month of content, editing with an AI editor, publishing and selling. Written in French for people who sell what they make.",
        "desc_fr": "La méthode complète du créateur : une banque d'idées, une journée de tournage pour un mois de contenu, le montage avec un monteur IA, la publication et la vente. Écrit pour celles et ceux qui vendent ce qu'ils font.",
        "music": "clair", "buy": [("Buy the PDF on Bobine", "Acheter le PDF sur Bobine", "https://bobine-tau.vercel.app/livre")]},
    "la-richesse-silencieuse": {"title": "La Richesse Silencieuse", "subtitle": "Le guide d'investissement de la diaspora africaine", "year": "2026", "color": "#0E3B2E", "ink": "#F2E6C9", "seed": "richesse-silencieuse",
        "desc_en": "A calm, practical investing guide for salaried people of the African diaspora: simple principles, real numbers, and room for family without sacrificing the future.",
        "desc_fr": "Un guide d'investissement calme et pratique pour les salariés de la diaspora africaine : des principes simples, de vrais chiffres, et une place pour la famille sans sacrifier l'avenir.",
        "music": "clair", "buy": []},
    "le-capital-entrave": {"title": "Le capital entravé", "subtitle": "", "year": "2026", "color": "#3B2414", "ink": "#F2E6C9", "seed": "capital-entrave",
        "desc_en": "An essay on capital that cannot move freely, and what it costs the people who live beside it.",
        "desc_fr": "Un essai sur le capital qui ne circule pas librement, et sur ce que cela coûte à ceux qui vivent à côté.",
        "music": "clair", "buy": []},
    "le-contrat-du-peuple": {"title": "Le Contrat du Peuple", "subtitle": "Droit social, justice et responsabilité citoyenne pour bâtir une nation libre", "year": "2026", "color": "#1C3FBF", "ink": "#F6F2EA", "seed": "contrat-du-peuple",
        "desc_en": "A civic essay in twenty chapters and an epilogue, written for Cameroonian readers and readable anywhere.",
        "desc_fr": "Un essai civique en vingt chapitres et un épilogue, écrit pour les lecteurs camerounais et lisible partout.",
        "music": "clair", "buy": []},
    "laa": {"title": "La'a", "subtitle": "Chroniques des Clans et des Confréries", "year": "2024", "color": "#5A1F1F", "ink": "#F6F2EA", "seed": "laa",
        "desc_en": "The first book of a twenty book saga: Fote, a village, a brotherhood, a war, and the loyalties that shape a life.",
        "desc_fr": "Le premier volet d'une saga de vingt livres : Fote, un village, une confrérie, une guerre, et les loyautés qui façonnent une vie.",
        "music": "braise", "buy": [("Kindle on Amazon", "Kindle sur Amazon", "https://www.amazon.com/dp/B0CZ8NCM9Z"), ("Paperback on Amazon", "Broché sur Amazon", "https://www.amazon.com/dp/B0D3F4TB9Y")]},
}
ORDER = ["bobine-la-methode", "la-richesse-silencieuse", "le-capital-entrave", "le-contrat-du-peuple", "laa"]

# The public site only knows each book's table of contents (books/toc/<slug>.json). The text itself lives in the
# protected backend and is fetched one chapter at a time while reading.
SUPABASE = "https://qytpqmgzphiuhlwkybiy.supabase.co"
PUBLISHABLE = "sb_publishable_QgRtb2_rjK2-hMG0s4i2Bw_Y11M05_X"

def load_books():
    books = []
    for slug in ORDER:
        p = os.path.join(HERE, "books", "toc", slug + ".json")
        if not os.path.exists(p): continue
        t = json.load(open(p, encoding="utf-8"))
        secs = [{"id": s["cid"], "label": s["label"], "title": s["title"], "kind": s["kind"], "part": s.get("part", ""), "words": s.get("words", 0)} for s in t["sections"]]
        books.append(dict(BOOK_META[slug], slug=slug, author="William Foteping", sections=secs))
    return books

def available():
    return [b["slug"] for b in load_books()]

AMB = [("calme", "Calm", "Calme"), ("pluie", "Soft rain", "Pluie douce"), ("foret", "Morning forest", "Forêt au matin"), ("mer", "Distant sea", "Mer au loin"), ("nuit", "Night", "Nuit")]
ALBUM_EMBED = "https://open.spotify.com/embed/album/5Ddoawb4wW8x2xMxW64RZN?utm_source=generator&theme=0"
ALBUM_URL = "https://open.spotify.com/album/5Ddoawb4wW8x2xMxW64RZN"

ROMAN = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI","XXII"]

COFFEE_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 8h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5V8z"/><path d="M17 9h1.5a2.5 2.5 0 0 1 0 5H17"/><path d="M8 2.5c-.6.8-.6 1.7 0 2.5M12 2.5c-.6.8-.6 1.7 0 2.5"/></svg>'

def coffee_button(t, cls="btn coffee", label=None):
    lab = label or t("Buy me a coffee", "Offrez-moi un café")
    return f'<button class="{cls}" type="button" data-coffee>{COFFEE_SVG}<span>{lab}</span></button>'

def coffee_modal(t):
    return f"""<div class="coffee-modal" hidden role="dialog" aria-modal="true" aria-label="Coffee"><div class="cm-card"><button class="cm-x" type="button" aria-label="Close">&times;</button><span class="label"><b>{t('A coffee for the author', 'Un café pour l’auteur')}</b></span><h3>{t('Thank you for reading.', 'Merci de lire.')}</h3><p>{t('Every book here is free to read. A coffee, a few dollars or more, pays for the time it takes to write the next one. You choose the amount on a secure Stripe page.', 'Chaque livre ici se lit gratuitement. Un café, quelques dollars ou plus, finance le temps d’écrire le suivant. Vous choisissez le montant sur une page Stripe sécurisée.')}</p><p class="cta-row cm-ready"><a class="btn cobalt cm-go" href="#" target="_blank" rel="noopener">{t('Give on Stripe', 'Donner sur Stripe')} &rarr;</a></p><p class="cm-wait muted" hidden>{t('The donation page opens in a few days. Meanwhile, sharing the book is the best gift.', 'La page de don ouvre dans quelques jours. En attendant, partager le livre est le plus beau cadeau.')}</p></div></div>"""

def page(b, t, head, header, footer, cover_art):
    def ambience(rv=True):
        chips = "".join('<button type="button" class="amb" data-amb="%s" aria-pressed="%s">%s</button>' % (k, "true" if k == "calme" else "false", t(en, fr)) for k, en, fr in AMB)
        return '<div class="ambience%s" role="group" aria-label="Ambience">%s</div>' % (" rv" if rv else "", chips)
    def album_panel():
        if b["slug"] == "laa":
            lead = t("This book has its own music: Chant et poésie de La'a, the author's synth album. Open the player and read with it.", "Ce livre a sa propre musique : Chant et poésie de La'a, l'album de l'auteur. Ouvrez le lecteur et lisez avec lui.")
        else:
            lead = t("Or read with the author's album, Chant et poésie de La'a, slow synths written for images.", "Ou lisez avec l'album de l'auteur, Chant et poésie de La'a, des synthés lents écrits pour l'image.")
        return f'<div class="album rv"><p>{lead}</p><div class="cta-row"><button class="btn ghost small album-open" type="button" data-src="{E(ALBUM_EMBED)}">{t("Open the album player", "Ouvrir le lecteur de l’album")}</button><a class="btn ghost small" href="{ALBUM_URL}" target="_blank" rel="noopener">Spotify &rarr;</a></div><div class="album-frame" hidden></div></div>'
    def short(s):
        if s["kind"] == "chapter": return re.sub(r"^\D+", "", s["label"]) or s["label"][:2]
        if s["kind"] == "annex": return re.sub(r"^Annexe\s*", "", s["label"])[:2]
        return s["label"][:1]
    toc = "".join(f'<a href="#{s["id"]}" data-i="{i}"><span class="n">{E(short(s))}</span><span>{E(s["title"])}</span></a>' for i, s in enumerate(b["sections"]))
    chapters = ""
    for i, s in enumerate(b["sections"]):
        kicker = (E(s["part"]) + " &middot; " if s.get("part") else "") + E(s["label"])
        chapters += (f'<section class="chap" id="{s["id"]}" data-i="{i}"><header class="chap-head"><span class="kicker mono">{kicker}</span><h2>{E(s["title"])}</h2></header>'
                     f'<div class="text" data-pending><p class="loading"><span></span><span></span><span></span></p></div>'
                     f'<nav class="chap-nav" aria-label="Chapitres"><a class="btn ghost small prev" href="#">&larr; <span></span></a><a class="btn small next" href="#"><span></span> &rarr;</a></nav></section>\n')
    words = sum(s.get("words", 0) for s in b["sections"])
    mins = max(1, round(words / 220))
    n = len(b["sections"])
    buy = "".join(f'<a class="btn ghost small" href="{E(u)}" target="_blank" rel="noopener">{t(en, fr)} &rarr;</a>' for en, fr, u in b.get("buy", []))
    lock = (f'<div class="lock" hidden><span class="label"><b>{t("Free reading is paused", "La lecture libre est en pause")}</b></span>'
            f'<h3>{t("This chapter opens again soon.", "Ce chapitre rouvrira bientôt.")}</h3>'
            f'<p>{t("The author opens his books for free for a period of time. This one is closed for now: the first pages stay open, and you can follow the book where it is sold.", "L’auteur ouvre ses livres gratuitement pendant une période. Celui-ci est fermé pour le moment : les premières pages restent ouvertes, et vous pouvez suivre le livre là où il est vendu.")}</p>'
            f'<p class="cta-row">{buy}{coffee_button(t, "btn small coffee")}</p></div>')
    music_svg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg>'
    body = f"""<div class="salon guarded" data-book="{E(b['slug'])}" data-music="{E(b['music'])}" data-sb="{SUPABASE}" data-pk="{PUBLISHABLE}" style="--bk:{b['color']};--bk-ink:{b['ink']}">
<div class="coffee-bar"><div class="wrap cb"><span class="cb-text">{t('These pages are free. If they help you, a coffee keeps them coming.', 'Ces pages sont gratuites. Si elles vous aident, un café les fait vivre.')}</span>{coffee_button(t, "btn small cobalt coffee")}</div></div>
<section class="opening wrap"><div class="opening-grid">
<div class="cover art big rv" style="--bk:{b['color']};--bk-ink:{b['ink']}">{cover_art(b['seed'], b['color'], b['ink'])}<span class="bn free-flag">{t('FREE TO READ', 'LECTURE LIBRE')}</span><span class="bt">{E(b['title'])}</span><span class="by">{E(b['author'])}</span><span class="bk">{E(b['subtitle'])}</span></div>
<div class="opening-text"><span class="label rv"><b>{t('Reading room', 'Salon de lecture')}</b><span class="free-state">{t('Free, complete, online', 'Gratuit, complet, en ligne')}</span></span>
<h1 class="rv" style="margin:14px 0 6px;font-size:clamp(40px,6vw,84px)">{E(b['title'])}</h1><p class="rv sub">{E(b['subtitle'])}</p>
<p class="lede rv">{t(b['desc_en'], b['desc_fr'])}</p>
<p class="rv mono muted" style="margin:0 0 20px">{E(b['author'])} &middot; {n} {t('sections', 'sections')} &middot; {words:,} {t('words', 'mots')} &middot; {t('about', 'environ')} {mins} {t('minutes', 'minutes')}</p>
<p class="cta-row rv"><a class="btn" href="#{b['sections'][0]['id']}" data-start>{t('Start reading', 'Commencer la lecture')}</a>{coffee_button(t, "btn cobalt coffee")}<button class="btn ghost music" type="button" aria-pressed="false">{music_svg}<span class="on">{t('Calm music', 'Musique calme')}</span><span class="off" hidden>{t('Stop the music', 'Couper la musique')}</span></button></p>
{('<p class="cta-row rv buy-row">' + buy + '</p>') if buy else ''}
{ambience()}
<p class="rv muted" style="font-size:14px;max-width:56ch;margin-top:14px">{t('A slow piece, composed live in your browser while you read, never twice the same. Choose its weather. It starts only when you ask.', 'Un morceau lent, composé en direct dans votre navigateur pendant que vous lisez, jamais deux fois le même. Choisissez son climat. Il ne démarre que si vous le demandez.')}</p>
{album_panel()}</div></div></section>

<div class="reader-bar" role="toolbar" aria-label="Reading tools"><div class="wrap rb"><button class="pill toc-btn" type="button" aria-expanded="false" aria-controls="toc">{t('Contents', 'Sommaire')}</button><span class="now mono"></span><span class="rb-tools">{coffee_button(t, "pill coffee", t('Coffee', 'Café'))}<button class="pill size" data-size="-" type="button" aria-label="Smaller text">A&minus;</button><button class="pill size" data-size="+" type="button" aria-label="Larger text">A+</button><button class="pill paper" type="button" aria-label="Page tone">Paper</button><span class="mwrap"><button class="pill mbtn" type="button" aria-expanded="false" aria-label="Music"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg><i class="eq" aria-hidden="true"><b></b><b></b><b></b></i></button>
<div class="mpanel" hidden><span class="label"><b>{t('Music for reading', 'Musique pour lire')}</b></span><button class="btn small music" type="button" aria-pressed="false"><span class="on">{t('Play', 'Lancer')}</span><span class="off" hidden>{t('Stop', 'Arrêter')}</span></button>{ambience(False)}<label class="vol"><span class="mono">{t('Volume', 'Volume')}</span><input type="range" min="0" max="100" value="70" aria-label="Volume"></label></div></span></span></div><div class="progress"><i></i></div></div>

<div class="wrap reader-grid"><aside class="toc" id="toc"><div class="toc-in"><span class="label"><b>{t('Contents', 'Sommaire')}</b></span><nav aria-label="Contents">{toc}</nav></div></aside>
<div class="book-body">{lock}{chapters}
<section class="colophon"><span class="label"><b>{t('The end', 'Fin')}</b></span><h2 style="margin:12px 0 10px">{t('Thank you for reading.', 'Merci de votre lecture.')}</h2><p class="lede">{t('This book is free to read here. If it gave you something, offer a coffee: it pays for the next book. Or share the link.', 'Ce livre se lit ici gratuitement. S’il vous a apporté quelque chose, offrez un café : il finance le prochain livre. Ou partagez le lien.')}</p><p class="cta-row">{coffee_button(t, "btn cobalt coffee")}</p>{album_panel()}<p class="cta-row"><a class="btn" href="/books">{t('Other books', 'Autres livres')}</a><a class="btn ghost" href="/contact">{t('Write to me', 'Écrire')}</a></p></section></div></div></div>
{coffee_modal(t)}
<div class="print-block">{t('This book is read online only. Printing and copying are turned off.', 'Ce livre se lit en ligne uniquement. L’impression et la copie sont désactivées.')}</div>"""
    return head(b["title"], b["desc_en"], f"/lire/{b['slug']}", '<link rel="stylesheet" href="/assets/salon.css"><script>document.documentElement.classList.add("js")</script><script src="/assets/salon.js" defer></script>') + header("books") + body + footer()
