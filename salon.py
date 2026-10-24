"""The reading room: free books as rich HTML pages with chapter navigation and calm music.
Sources live in books/*.json. Each book page is written to dist/lire/<slug>.html."""
import os, re, json, html
import richesse
INTROS = {"richesse": richesse.section}
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
    "camera-au-poing": {"title": "Caméra au poing", "subtitle": "Vloguer et filmer comme un pro, avec un téléphone et Bobine", "year": "2026", "color": "#0B0B0D", "ink": "#D4AD6A", "seed": "camera-au-poing",
        "desc_en": "A practical school of vlogging and filmmaking for creators who shoot on a phone: voice and rhythm, telling a day, light, sound, camera movement, scenes, production, documentary, sketch and music video, then editing with Bobine and learning from every post.",
        "desc_fr": "Une école pratique du vlog et du cinéma pour les créateurs qui filment au téléphone : la voix et le rythme, raconter une journée, la lumière, le son, le mouvement, la scène, la production, le documentaire, le sketch et le clip, puis le montage avec Bobine et l'apprentissage de chaque publication.",
        "music": "clair", "buy": [("On Bobine", "Sur Bobine", "https://bobine-tau.vercel.app/livre#camera")]},
    "bobine-la-methode": {"title": "Bobine, la méthode", "subtitle": "Planifier, filmer, monter et vendre avec l'IA", "year": "2026", "color": "#16130F", "ink": "#E9B44C", "seed": "bobine-la-methode",
        "desc_en": "A complete method for creators: an idea bank, one shooting day for a month of content, editing with an AI editor, publishing and selling.",
        "desc_fr": "Une méthode complète pour les créateurs : une banque d'idées, une journée de tournage pour un mois de contenu, le montage avec un monteur IA, la publication et la vente.",
        "music": "clair", "buy": [("Buy the PDF on Bobine", "Acheter le PDF sur Bobine", "https://bobine-tau.vercel.app/livre")]},
    "la-richesse-silencieuse": {"title": "La Richesse Silencieuse", "subtitle": "Le guide d'investissement de la diaspora africaine", "year": "2026", "color": "#0C2A20", "ink": "#E6CB8E", "seed": "richesse-silencieuse",
        "desc_en": "An investing guide for salaried members of the African diaspora. It names the pressure to build back home, shows why many of those emotional investments never pay back, and gives a simple method: save, buy index funds, protect the family, and help relatives within a set limit.",
        "desc_fr": "Un guide d'investissement pour les salariés de la diaspora africaine. Il nomme la pression de construire au pays, montre pourquoi tant de ces investissements affectifs ne rapportent jamais, et propose une méthode simple : épargner, acheter des fonds indiciels, protéger la famille, et aider les proches dans une limite fixée.",
        "music": "clair", "intro": "richesse", "buy": [("Investment simulator", "Simulateur de placements", "/demo/simulateur-placements")]},
    "le-capital-entrave": {"title": "Le capital entravé", "subtitle": "Institutions, investissement et prospérité au Cameroun", "year": "2026", "color": "#3B2414", "ink": "#EDE3CF", "seed": "capital-entrave",
        "desc_en": "Why Cameroon's economy stalls: work and savings cannot become capital when land titles, rules and institutions fail. A few people title and stockpile land to speculate; most families own something they cannot use as collateral. An essay on what must change, and on what the diaspora can do.",
        "desc_fr": "Pourquoi l'économie camerounaise piétine : le travail et l'épargne ne deviennent pas du capital quand les titres fonciers, les règles et les institutions font défaut. Quelques-uns titrent et accumulent les terrains pour spéculer ; la plupart des familles possèdent un bien qu'elles ne peuvent pas mettre en garantie. Un essai sur ce qui doit changer, et sur ce que la diaspora peut faire.",
        "music": "clair", "buy": []},
    "la-monnaie-la-terre-et-le-merite": {"title": "La Monnaie, la Terre et le Mérite", "subtitle": "Trois réformes dures pour un Cameroun qui se construit", "year": "2026", "color": "#06241A", "ink": "#F1CF7A", "seed": "monnaie-terre-merite",
        "desc_en": "A manifesto for Cameroonian decision makers in three books: the money (move the franc CFA from cash to digital, without changing the currency), the land (agriculture, industry under export discipline, finance in their service, as East Asia did) and merit (the value is subjective, a country belongs to no one, tribalism and nepotism are bad economics). Forty-two chapters, a letter to decision makers and the e-XAF interactive demonstrator.",
        "desc_fr": "Un manifeste pour les décideurs camerounais en trois livres : la monnaie (faire passer le franc CFA des espèces au numérique, sans changer de monnaie), la terre (agriculture, industrie sous discipline d'exportation, finance à leur service, comme l'Asie de l'Est) et le mérite (la valeur est subjective, un pays n'appartient à personne, le tribalisme et le népotisme sont de mauvaises théories économiques). Quarante-deux chapitres, une lettre aux décideurs et le démonstrateur interactif e-XAF.",
        "music": "clair", "buy": [("e-XAF demonstrator", "Démonstrateur e-XAF", "/demo/e-xaf")]},
    "les-yeux-ouverts": {"title": "Les Yeux ouverts", "subtitle": "L'intelligence artificielle expliquée à ceux qui ne codent pas", "year": "2026", "color": "#0C1033", "ink": "#F2C66D", "seed": "yeux-ouverts",
        "desc_en": "Artificial intelligence explained to French-speaking Africans who do not code. Part one opens the machine: tokens and the extra cost they put on African languages, the map of meaning, attention, training, why it invents. Part two follows AI agents that act on their own, in business, work and daily life. Part three makes the case: those who say not now are heard and answered, history is recalled, and a programme is laid out so the continent does not look away.",
        "desc_fr": "L'intelligence artificielle expliquée aux Africains francophones qui ne codent pas. La première partie ouvre la machine : les jetons et le surcoût qu'ils imposent aux langues africaines, la carte du sens, l'attention, l'entraînement, pourquoi elle invente. La deuxième suit les agents d'IA qui agissent seuls, dans l'entreprise, le travail et la vie. La troisième porte la thèse : les voix du « pas maintenant » sont entendues et réfutées, l'histoire est rappelée, et un programme est tracé pour que le continent ne détourne plus le regard.",
        "music": "clair", "buy": []},
    "tout-est-code": {"title": "Tout est code", "subtitle": "Apprendre Python pour penser clair, comprendre son époque et tout visualiser", "year": "2026", "color": "#0B1A15", "ink": "#FCD116", "seed": "tout-est-code", "ide": True,
        "desc_en": "Learn Python from zero, in French, written for Africa and its diaspora. Every example runs in the browser: press Run, change a number, run it again. Part one says why code is the language of the age of artificial intelligence. Part two lays the foundations, from variables to objects. Part three puts them to work to think, check misleading figures, draw charts and simulate. Part four builds three complete projects: a mental arithmetic game, a digital tontine, a school report with a market price dashboard.",
        "desc_fr": "Apprendre Python à partir de zéro, en français, pour l'Afrique et sa diaspora. Chaque exemple s'exécute dans le navigateur : on appuie sur Exécuter, on change un nombre, on recommence. La première partie dit pourquoi le code est la langue de l'âge de l'intelligence artificielle. La deuxième pose les fondations, des variables aux objets. La troisième les met au service de la pensée : vérifier les chiffres trompeurs, dessiner des graphiques, simuler. La quatrième construit trois projets complets : un jeu de calcul mental, une tontine numérique, un bulletin scolaire avec un tableau de bord des prix du marché.",
        "music": "clair", "buy": []},
    "le-contrat-du-peuple": {"title": "Le Contrat du Peuple", "subtitle": "Droit social, justice et responsabilité citoyenne pour bâtir une nation libre", "year": "2026", "color": "#1C3FBF", "ink": "#F6F2EA", "seed": "contrat-du-peuple",
        "desc_en": "Essay on the social contract in Cameroon: rights, justice and the responsibilities of citizens. Preface, 20 chapters and an epilogue.",
        "desc_fr": "Essai sur le contrat social au Cameroun : droits, justice et responsabilités du citoyen. Préface, 20 chapitres et un épilogue.",
        "music": "clair", "buy": []},
    "laa": {"title": "La'a", "subtitle": "Chroniques des Clans et des Confréries", "year": "2024", "color": "#5A1F1F", "ink": "#F6F2EA", "seed": "laa",
        "desc_en": "Book one of a planned 20-volume saga. Fote grows up in the village of La'a, joins a brotherhood and lives through a war.",
        "desc_fr": "Premier tome d'une saga prévue en 20 volumes. Fote grandit au village de La'a, entre dans une confrérie et traverse une guerre.",
        "music": "braise", "buy": [("Kindle on Amazon", "Kindle sur Amazon", "https://www.amazon.com/dp/B0CZ8NCM9Z"), ("Paperback on Amazon", "Broché sur Amazon", "https://www.amazon.com/dp/B0D3F4TB9Y")]},
}
ORDER = ["camera-au-poing", "la-richesse-silencieuse", "le-capital-entrave", "la-monnaie-la-terre-et-le-merite", "les-yeux-ouverts", "tout-est-code", "bobine-la-methode", "le-contrat-du-peuple", "laa"]

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
    return f"""<div class="coffee-modal" hidden role="dialog" aria-modal="true" aria-label="Coffee"><div class="cm-card"><button class="cm-x" type="button" aria-label="Close">&times;</button><span class="label"><b>{t('A coffee for the author', 'Un café pour l’auteur')}</b></span><h3>{t('Thank you for reading.', 'Merci de lire.')}</h3><p>{t('All the books on this site are free to read. A contribution of any amount funds the next one. You choose the amount and the payment method.', 'Tous les livres de ce site se lisent gratuitement. Une contribution, quel que soit le montant, finance le suivant. Vous choisissez le montant et le moyen de paiement.')}</p><div class="cta-row cm-ready cm-links"></div><p class="cm-wait muted" hidden>{t('The donation page is not open yet. In the meantime, sharing the book helps.', 'La page de don n’est pas encore ouverte. En attendant, partager le livre aide.')}</p></div></div>"""

def page(b, t, head, header, footer, cover_art):
    def ambience(rv=True):
        chips = "".join('<button type="button" class="amb" data-amb="%s" aria-pressed="%s">%s</button>' % (k, "true" if k == "calme" else "false", t(en, fr)) for k, en, fr in AMB)
        return '<div class="ambience%s" role="group" aria-label="Ambience">%s</div>' % (" rv" if rv else "", chips)
    def album_panel():
        if b["slug"] == "laa":
            lead = t("The author's album, Chant et poésie de La'a, accompanies this book. You can play it while you read.", "L'album de l'auteur, Chant et poésie de La'a, accompagne ce livre. Vous pouvez l'écouter en lisant.")
        else:
            lead = t("You can also read with the author's album, Chant et poésie de La'a.", "Vous pouvez aussi lire avec l'album de l'auteur, Chant et poésie de La'a.")
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
            f'<h3>{t("This chapter is not available right now.", "Ce chapitre n’est pas disponible pour le moment.")}</h3>'
            f'<p>{t("Free reading of this book is closed for now. The first sections stay open; the full book is available where it is sold.", "La lecture libre de ce livre est fermée pour le moment. Les premières sections restent ouvertes ; le livre complet est disponible là où il est vendu.")}</p>'
            f'<p class="cta-row">{buy}{coffee_button(t, "btn small coffee")}</p></div>')
    music_svg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg>'
    ide = bool(b.get("ide"))
    ide_attr = ' data-ide' if ide else ''
    ide_head = ('<link rel="stylesheet" href="/assets/pyide.css"><script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" defer></script>'
                '<script src="/assets/flag.js" defer></script><script src="/assets/pyide.js" defer></script>') if ide else ''
    ide_flag = '<canvas class="flag3d rv" role="img" aria-label="Drapeau du Cameroun qui flotte au vent"></canvas>' if ide else ''
    intro = INTROS[b["intro"]](t) if b.get("intro") in INTROS else ''
    ide_row = (f'<p class="cta-row rv"><button class="btn cm-green" type="button" data-atelier>{t("Open the Python workshop", "Ouvrir l’atelier Python")}</button>'
               f'<a class="btn ghost" href="/atelier-python">{t("Workshop on a full page", "L’atelier en pleine page")} &rarr;</a></p>'
               f'<p class="rv muted" style="font-size:14px;max-width:58ch">{t("Every Python example in this book runs in your browser: press Run, change the code, run it again. Nothing to install.", "Chaque exemple Python de ce livre s’exécute dans votre navigateur : appuyez sur Exécuter, modifiez le code, relancez. Rien à installer.")}</p>') if ide else ''
    body = f"""<div class="salon guarded" data-book="{E(b['slug'])}"{ide_attr} data-music="{E(b['music'])}" data-sb="{SUPABASE}" data-pk="{PUBLISHABLE}" style="--bk:{b['color']};--bk-ink:{b['ink']}">
<div class="coffee-bar"><div class="wrap cb"><span class="cb-text">{t('This book is free to read. If it helps you, you can buy me a coffee.', 'Ce livre se lit gratuitement. S’il vous est utile, vous pouvez m’offrir un café.')}</span>{coffee_button(t, "btn small cobalt coffee")}</div></div>
<section class="opening wrap"><div class="opening-grid">
<div class="cover art big rv" style="--bk:{b['color']};--bk-ink:{b['ink']}">{cover_art(b['seed'], b['color'], b['ink'])}<span class="bn free-flag">{t('FREE TO READ', 'LECTURE LIBRE')}</span><span class="bt">{E(b['title'])}</span><span class="by">{E(b['author'])}</span><span class="bk">{E(b['subtitle'])}</span></div>
<div class="opening-text">{ide_flag}<span class="label rv"><b>{t('Reading room', 'Salon de lecture')}</b><span class="free-state">{t('Free, complete, online', 'Gratuit, complet, en ligne')}</span></span>
<h1 class="rv" style="margin:14px 0 6px;font-size:clamp(40px,6vw,84px)">{E(b['title'])}</h1><p class="rv sub">{E(b['subtitle'])}</p>
<p class="lede rv">{t(b['desc_en'], b['desc_fr'])}</p>
<p class="rv mono muted" style="margin:0 0 20px">{E(b['author'])} &middot; {n} {t('sections', 'sections')} &middot; {words:,} {t('words', 'mots')} &middot; {t('about', 'environ')} {mins} {t('minutes', 'minutes')}</p>
<p class="cta-row rv"><a class="btn" href="#{b['sections'][0]['id']}" data-start>{t('Start reading', 'Commencer la lecture')}</a>{coffee_button(t, "btn cobalt coffee")}<button class="btn ghost music" type="button" aria-pressed="false">{music_svg}<span class="on">{t('Calm music', 'Musique calme')}</span><span class="off" hidden>{t('Stop the music', 'Couper la musique')}</span></button></p>
{('<p class="cta-row rv buy-row">' + buy + '</p>') if buy else ''}{ide_row}
{ambience()}
<p class="rv muted" style="font-size:14px;max-width:56ch;margin-top:14px">{t('Ambient music generated in your browser. Choose a mood; it plays only when you start it.', 'Une musique d’ambiance générée dans votre navigateur. Choisissez une ambiance ; elle ne démarre que si vous la lancez.')}</p>
{album_panel()}</div></div></section>
{intro}

<div class="reader-bar" role="toolbar" aria-label="Reading tools"><div class="wrap rb"><button class="pill toc-btn" type="button" aria-expanded="false" aria-controls="toc">{t('Contents', 'Sommaire')}</button><span class="now mono"></span><span class="rb-tools">{coffee_button(t, "pill coffee", t('Coffee', 'Café'))}<button class="pill size" data-size="-" type="button" aria-label="Smaller text">A&minus;</button><button class="pill size" data-size="+" type="button" aria-label="Larger text">A+</button><button class="pill paper" type="button" aria-label="Page tone">Paper</button><span class="mwrap"><button class="pill mbtn" type="button" aria-expanded="false" aria-label="Music"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg><i class="eq" aria-hidden="true"><b></b><b></b><b></b></i></button>
<div class="mpanel" hidden><span class="label"><b>{t('Music for reading', 'Musique pour lire')}</b></span><button class="btn small music" type="button" aria-pressed="false"><span class="on">{t('Play', 'Lancer')}</span><span class="off" hidden>{t('Stop', 'Arrêter')}</span></button>{ambience(False)}<label class="vol"><span class="mono">{t('Volume', 'Volume')}</span><input type="range" min="0" max="100" value="70" aria-label="Volume"></label></div></span></span></div><div class="progress"><i></i></div></div>

<div class="wrap reader-grid"><aside class="toc" id="toc"><div class="toc-in"><span class="label"><b>{t('Contents', 'Sommaire')}</b></span><nav aria-label="Contents">{toc}</nav></div></aside>
<div class="book-body">{lock}{chapters}
<section class="colophon"><span class="label"><b>{t('The end', 'Fin')}</b></span><h2 style="margin:12px 0 10px">{t('Thank you for reading.', 'Merci de votre lecture.')}</h2><p class="lede">{t('If this book was useful, you can buy me a coffee or share the link.', 'Si ce livre vous a été utile, vous pouvez m’offrir un café ou partager le lien.')}</p><p class="cta-row">{coffee_button(t, "btn cobalt coffee")}</p>{album_panel()}<p class="cta-row"><a class="btn" href="/books">{t('Other books', 'Autres livres')}</a><a class="btn ghost" href="/contact">{t('Write to me', 'Écrire')}</a></p></section></div></div></div>
{coffee_modal(t)}
<div class="print-block">{t('This book can be read online only. Printing and copying are disabled.', 'Ce livre se lit en ligne uniquement. L’impression et la copie sont désactivées.')}</div>"""
    return head(b["title"], b["desc_en"], f"/lire/{b['slug']}", '<link rel="stylesheet" href="/assets/salon.css"><script>document.documentElement.classList.add("js")</script><script src="/assets/salon.js" defer></script>' + ide_head) + header("books") + body + footer()
