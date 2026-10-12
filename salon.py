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
    """A small markdown: ## headings, paragraphs, dash lists, blank line separation."""
    out, para, lst = [], [], []
    def flush_p():
        if para: out.append(f"<p>{md_inline(' '.join(para))}</p>"); para.clear()
    def flush_l():
        if lst: out.append("<ul>" + "".join(f"<li>{md_inline(x)}</li>" for x in lst) + "</ul>"); lst.clear()
    for line in body.split("\n"):
        line = line.rstrip()
        if not line.strip(): flush_p(); flush_l(); continue
        m = re.match(r"^(#{2,4})\s+(.*)$", line)
        if m:
            flush_p(); flush_l()
            txt = m.group(2).strip()
            n = re.match(r"^(\d+)\.\s+(.*)$", txt)
            if n: out.append(f'<h3 class="sec"><span class="sn">{n.group(1)}</span>{md_inline(n.group(2))}</h3>')
            else: out.append(f"<h3 class=\"sec\">{md_inline(txt)}</h3>")
            continue
        if re.match(r"^[-•]\s+", line): flush_p(); lst.append(re.sub(r"^[-•]\s+", "", line)); continue
        para.append(line.strip())
    flush_p(); flush_l()
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

def load_books():
    books = []
    c = json.load(open(os.path.join(HERE, "books", "contrat.json"), encoding="utf-8"))
    secs = []
    for s in c["sections"]:
        num = s["num"]; kind = s["kind"].lower()
        label = num if kind != "chapter" else num
        secs.append({"id": re.sub(r"[^a-z0-9]+", "-", num.lower().replace("é", "e").replace("è", "e")).strip("-"), "label": label, "title": s["title"].split(" : ", 1)[-1] if kind != "chapter" else s["title"], "html": md_block(s["body"]), "kind": kind})
    books.append({"slug": "le-contrat-du-peuple", "title": "Le Contrat du Peuple", "subtitle": "Droit social, justice et responsabilité citoyenne pour bâtir une nation libre", "author": "William Foteping", "year": "2026", "color": "#1C3FBF", "ink": "#F6F2EA", "seed": "contrat-du-peuple",
        "desc_en": "A civic essay in twenty chapters and an epilogue, written for Cameroonian readers and readable anywhere.", "desc_fr": "Un essai civique en vingt chapitres et un épilogue, écrit pour les lecteurs camerounais et lisible partout.",
        "music": "clair", "sections": secs})
    l = json.load(open(os.path.join(HERE, "books", "laa-raw.json"), encoding="utf-8"))
    secs = []
    for d in l:
        t = d["title"].strip(); m = re.match(r"^(\d+)\.\s*(.*)$", t)
        if m: secs.append({"id": f"chapitre-{m.group(1)}", "label": f"Chapitre {m.group(1)}", "title": m.group(2).strip(), "html": clean_html(d["html"]), "kind": "chapter"})
        else: secs.append({"id": re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-"), "label": t, "title": t, "html": clean_html(d["html"]), "kind": "front"})
    books.append({"slug": "laa", "title": "La'a", "subtitle": "Chroniques des Clans et des Confréries", "author": "William Foteping", "year": "2024", "color": "#5A1F1F", "ink": "#F6F2EA", "seed": "laa",
        "desc_en": "The first book of a twenty book saga: Fote, a village, a brotherhood, a war, and the loyalties that shape a life.", "desc_fr": "Le premier volet d'une saga de vingt livres : Fote, un village, une confrérie, une guerre, et les loyautés qui façonnent une vie.",
        "music": "braise", "sections": secs})
    return books

ROMAN = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI","XXII"]

def page(b, t, head, header, footer, cover_art):
    def short(s): return s["label"].replace("Chapitre ", "") if s["kind"] == "chapter" else s["label"][:1]
    toc = "".join(f'<a href="#{s["id"]}" data-i="{i}"><span class="n">{E(short(s))}</span><span>{E(s["title"])}</span></a>' for i, s in enumerate(b["sections"]))
    chapters = ""
    for i, s in enumerate(b["sections"]):
        kicker = E(s["label"]) if s["kind"] == "chapter" else E(s["label"])
        chapters += f'''<section class="chap" id="{s["id"]}" data-i="{i}"><header class="chap-head"><span class="kicker mono">{kicker}</span><h2>{E(s["title"])}</h2></header><div class="text">{s["html"]}</div>
<nav class="chap-nav" aria-label="Chapitres"><a class="btn ghost small prev" href="#">&larr; <span></span></a><a class="btn small next" href="#"><span></span> &rarr;</a></nav></section>'''
    words = sum(len(re.sub(r"<[^>]+>", " ", s["html"]).split()) for s in b["sections"])
    mins = max(1, round(words / 220))
    n = len(b["sections"])
    body = f"""<div class="salon" data-book="{E(b['slug'])}" data-music="{E(b['music'])}" style="--bk:{b['color']};--bk-ink:{b['ink']}">
<section class="opening wrap"><div class="opening-grid">
<div class="cover art big rv" style="--bk:{b['color']};--bk-ink:{b['ink']}">{cover_art(b['seed'], b['color'], b['ink'])}<span class="bn">{t('FREE TO READ', 'LECTURE LIBRE')}</span><span class="bt">{E(b['title'])}</span><span class="by">{E(b['author'])}</span><span class="bk">{E(b['subtitle'])}</span></div>
<div class="opening-text"><span class="label rv"><b>{t('Reading room', 'Salon de lecture')}</b><span>{t('Free, complete, online', 'Gratuit, complet, en ligne')}</span></span>
<h1 class="rv" style="margin:14px 0 6px;font-size:clamp(40px,6vw,84px)">{E(b['title'])}</h1><p class="rv sub">{E(b['subtitle'])}</p>
<p class="lede rv">{t(b['desc_en'], b['desc_fr'])}</p>
<p class="rv mono muted" style="margin:0 0 20px">{E(b['author'])} &middot; {n} {t('sections', 'sections')} &middot; {words:,} {t('words', 'mots')} &middot; {t('about', 'environ')} {mins} {t('minutes', 'minutes')}</p>
<p class="cta-row rv"><a class="btn" href="#{b['sections'][0]['id']}" data-start>{t('Start reading', 'Commencer la lecture')}</a><button class="btn ghost music" type="button" aria-pressed="false"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg><span class="on">{t('Calm music', 'Musique calme')}</span><span class="off" hidden>{t('Stop the music', 'Couper la musique')}</span></button><a class="btn ghost" href="/books">{t('All the books', 'Tous les livres')}</a></p>
<p class="rv muted" style="font-size:14px;max-width:52ch">{t('A soft piece, generated in your browser, to keep you company while you read. It starts only when you ask.', 'Un morceau doux, généré dans votre navigateur, pour vous tenir compagnie pendant la lecture. Il ne démarre que si vous le demandez.')}</p></div></div></section>

<div class="reader-bar" role="toolbar" aria-label="Reading tools"><div class="wrap rb"><button class="pill toc-btn" type="button" aria-expanded="false" aria-controls="toc">{t('Contents', 'Sommaire')}</button><span class="now mono"></span><span class="rb-tools"><button class="pill size" data-size="-" type="button" aria-label="Smaller text">A&minus;</button><button class="pill size" data-size="+" type="button" aria-label="Larger text">A+</button><button class="pill music" type="button" aria-pressed="false" aria-label="Calm music"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg></button></span></div><div class="progress"><i></i></div></div>

<div class="wrap reader-grid"><aside class="toc" id="toc"><div class="toc-in"><span class="label"><b>{t('Contents', 'Sommaire')}</b></span><nav aria-label="Contents">{toc}</nav></div></aside>
<div class="book-body">{chapters}
<section class="colophon"><span class="label"><b>{t('The end', 'Fin')}</b></span><h2 style="margin:12px 0 10px">{t('Thank you for reading.', 'Merci de votre lecture.')}</h2><p class="lede">{t('This book is free to read here, in full. If it was worth something to you, share the link, or write to me.', 'Ce livre se lit ici gratuitement, en entier. S’il a compté pour vous, partagez le lien, ou écrivez-moi.')}</p><p class="cta-row"><a class="btn" href="/books">{t('Other books', 'Autres livres')}</a><a class="btn ghost" href="/contact">{t('Write to me', 'Écrire')}</a></p></section></div></div></div>"""
    return head(b["title"], b["desc_en"], f"/lire/{b['slug']}", '<link rel="stylesheet" href="/assets/salon.css"><script>document.documentElement.classList.add("js")</script><script src="/assets/salon.js" defer></script>') + header("books") + body + footer()
