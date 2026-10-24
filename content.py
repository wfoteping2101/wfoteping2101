# Site content in English. French lives in fr.py; the platforms (EN and FR) live in platforms.py.
# House rules: no em dashes, no en dashes, no emojis, no phone numbers,
# never name the day job employer, coworkers or clients.

SITE = {
    "name": "William Foteping",
    "tagline_en": "Senior network administrator in cloud and infrastructure. I also build software platforms, write books in French and English, and make the videos that present them.",
    "tagline_fr": "Administrateur réseau senior, cloud et infrastructure. Je construis aussi des plateformes logicielles, j'écris des livres en français et en anglais, et je réalise les vidéos qui les présentent.",
    "location": "Maryland, United States",
    "email": "support@lemonshops.app",
    "url": "https://william-foteping.vercel.app",
    "description": "William Foteping: network engineer, software platforms, books, motion design and services.",
    "consult_price": 150,
    "consult_credit_days": 30,
    "amazon_laa": "https://www.amazon.com/s?k=LAA+Chroniques+des+Clans+et+Confr%C3%A9ries",
    "spotify": "https://open.spotify.com/search/Wfoss%20Chant%20et%20po%C3%A9sie%20de%20La%27a",
}

CDN = "https://d2ol7oe51mr4n9.cloudfront.net/user_38X5q6AW6UAWxSufMc8KKw4LN7Q/"

from platforms import PROJECTS  # the 13 platforms, written in platforms.py

ALBUM = {"slug": "wfoss", "title": "Chant et poésie de La'a", "artist": "Wfoss", "kind": "Album", "year": "2026", "color": "#0E1B4D", "ink": "#F2E6C9",
    "line": "Synth album composed for film and video, released under the name Wfoss.",
    "where": [("Listen on Spotify", "https://open.spotify.com/search/Wfoss%20Chant%20et%20po%C3%A9sie%20de%20La%27a")]}

BOOKS = [
    {"slug": "camera-au-poing", "title": "Caméra au poing", "lang": "Français", "kind": "Vlog, film, editing", "year": "2026", "pages": "Preface, introduction, 23 chapters, 4 appendices",
     "color": "#0B0B0D", "ink": "#D4AD6A", "free": "camera-au-poing",
     "line": "Vlogging and filmmaking with a phone: finding a voice, telling a day, light, sound, scenes, documentary, sketch and music video, then editing with Bobine and learning from every post.",
     "where": [("Read online, free", "/lire/camera-au-poing"), ("On Bobine", "https://bobine-tau.vercel.app/livre#camera")]},
    {"slug": "richesse-silencieuse", "title": "La Richesse Silencieuse", "lang": "Français", "kind": "Investing guide", "year": "2026", "pages": "Introduction, 28 chapters, conclusion, appendices",
     "color": "#0C2A20", "ink": "#E6CB8E", "free": "la-richesse-silencieuse",
     "line": "Investing guide for salaried members of the African diaspora. It names the pressure to build back home, shows why many of those emotional investments never pay back, and gives a simple method: save, buy index funds, protect the family, and help relatives within a set limit. Comes with an interactive investment simulator.",
     "where": [("Read online, free", "/lire/la-richesse-silencieuse"), ("Investment simulator", "/demo/simulateur-placements")]},
    {"slug": "capital-entrave", "title": "Le capital entravé", "lang": "Français", "kind": "Essay, economy", "year": "2026", "pages": "Prologue, 50 chapters in 7 parts, decision notebook, sources",
     "color": "#EDE3CF", "ink": "#A8432A", "free": "le-capital-entrave",
     "line": "Why Cameroon's economy stalls: work and savings cannot become capital when land titles, rules and institutions fail. A few people title and stockpile land to speculate; most families own something they cannot use as collateral.",
     "where": [("Read online, free", "/lire/le-capital-entrave")]},
    {"slug": "monnaie-terre-merite", "title": "La Monnaie, la Terre et le Mérite", "lang": "Français", "kind": "Essay, public policy", "year": "2026", "pages": "Introduction, 42 chapters in 3 books, letter to decision makers, 5 appendices",
     "color": "#06241A", "ink": "#F1CF7A", "free": "la-monnaie-la-terre-et-le-merite",
     "line": "Three hard reforms for Cameroon, written for the people who decide: move the franc CFA from cash to digital without changing the currency; rebuild land, industry and finance the way East Asia did; and treat the economy as exchange between free individuals, not a rent shared between clans. Comes with the e-XAF interactive demonstrator.",
     "where": [("Read online, free", "/lire/la-monnaie-la-terre-et-le-merite"), ("e-XAF demonstrator", "/demo/e-xaf")]},
    {"slug": "yeux-ouverts", "title": "Les Yeux ouverts", "lang": "Français", "kind": "Essay, artificial intelligence", "year": "2026", "pages": "Introduction, 26 chapters in 3 parts, conclusion, 4 appendices",
     "color": "#0C1033", "ink": "#F2C66D", "free": "les-yeux-ouverts",
     "line": "Artificial intelligence explained to French-speaking Africans who do not code: how a language model works, piece by piece (tokens, attention, training, why it invents), what changes when AI agents act on their own, and why a continent that looks away from this technology will pay for it.",
     "where": [("Read online, free", "/lire/les-yeux-ouverts")]},
    {"slug": "tout-est-code", "title": "Tout est code", "lang": "Français", "kind": "Python course, interactive", "year": "2026", "pages": "Introduction, 28 chapters in 4 parts, conclusion, 4 appendices",
     "color": "#0B1A15", "ink": "#FCD116", "free": "tout-est-code",
     "line": "Learn Python from zero, in French, for Africa and its diaspora: think in steps, catch up, check misleading figures and draw any problem as a chart. Every example runs in the browser, and a free Python workshop sits next to the book.",
     "where": [("Read online, free", "/lire/tout-est-code"), ("Python workshop", "/atelier-python")]},
    {"slug": "contrat-du-peuple", "title": "Le Contrat du Peuple", "lang": "Français", "kind": "Civic essay", "year": "2026", "pages": "Preface, 20 chapters, epilogue",
     "color": "#1C3FBF", "ink": "#F6F2EA", "free": "le-contrat-du-peuple",
     "line": "Essay on the social contract in Cameroon: rights, justice and the responsibilities of citizens.",
     "where": [("Read online, free", "/lire/le-contrat-du-peuple")]},
    {"slug": "laa", "title": "La'a : Chroniques des Clans et des Confréries", "lang": "Français", "kind": "Novel", "year": "2024", "pages": "13 chapters, presentation, glossary",
     "color": "#5A1F1F", "ink": "#F6F2EA", "free": "laa",
     "line": "Book one of a planned 20-volume saga. Fote grows up in the village of La'a, joins a brotherhood and lives through a war.",
     "where": [("Read online, free", "/lire/laa"), ("Kindle", "https://www.amazon.com/dp/B0CZ8NCM9Z"), ("Paperback", "https://www.amazon.com/dp/B0D3F4TB9Y")]},
    {"slug": "bobine-la-methode", "title": "Bobine, la méthode", "lang": "Français", "kind": "Video production method", "year": "2026", "pages": "265 pages",
     "color": "#16130F", "ink": "#E9B44C", "free": "bobine-la-methode",
     "line": "How to plan, film, edit with AI and sell video content, with one shooting day for a month of posts. The PDF is sold on Bobine.",
     "where": [("Read online, free", "/lire/bobine-la-methode"), ("PDF on Bobine", "https://bobine-tau.vercel.app/livre")]},
    {"slug": "unifi-ground-up", "title": "UniFi from the Ground Up", "lang": "English", "kind": "Networking", "year": "2026", "pages": "241 pages, 59 figures",
     "color": "#15181D", "ink": "#F2C200",
     "line": "Designing and running a business network with UniFi: gateways, switching, WiFi, cameras, door access, racks and operations. Sample chapters are free.",
     "where": [("Sample chapters", "https://v0-lemon-network-solutions.vercel.app/books")]},
    {"slug": "msp-30-days", "title": "The 30-Day Managed Services Launch", "lang": "English", "kind": "IT business", "year": "2026", "pages": "214 pages, 11 figures",
     "color": "#F2C200", "ink": "#15181D",
     "line": "A day-by-day plan to launch a one-person IT services company: offer, pricing, contract, monitoring tools, first clients.",
     "where": [("Sample chapters", "https://v0-lemon-network-solutions.vercel.app/books")]},
    {"slug": "project-book", "title": "The Project Book", "lang": "English", "kind": "Document format", "year": "2026", "pages": "10 pages, US Letter",
     "color": "#E9E2D3", "ink": "#15181D",
     "line": "The 10-page document each Lemon Network Solutions client receives: design, coverage maps, rack and cabling, bill of materials, timeline and acceptance.",
     "where": [("See the sample", "https://v0-lemon-network-solutions.vercel.app/plan")]},
]

# Gallery. "fr" holds the French title and line.
MOTION = [
    {"slug": "uplink-promo", "title": "Uplink in 44 seconds", "kind": "Motion design", "year": "2026",
     "line": "Vertical promo for TikTok and Reels: exam practice, the ticket simulator, the lab and pricing.",
     "fr": ("Uplink en 44 secondes", "Promo verticale pour TikTok et Reels : examens, simulateur de tickets, lab et tarifs."),
     "poster": "/assets/motion/uplink-promo.webp",
     "variants": [("9:16", "/assets/motion/uplink-promo-9x16.mp4", "9:16")]},
    {"slug": "bobine-50", "title": "Bobine in 50 seconds", "kind": "Motion design", "year": "2026",
     "line": "Explainer in French and English: the formats, the three steps and on-device editing. Original synthesized music.",
     "fr": ("Bobine en 50 secondes", "Vidéo explicative en français et en anglais : les formats, les trois étapes et le montage sur l'appareil. Musique originale de synthèse."),
     "poster": "https://bobine-tau.vercel.app/showcase/v2/showcase-clean.webp",
     "variants": [("FR 16:9", CDN + "9a061b90-4085-4d01-b5f3-a28f02622f95.mp4", "16:9"), ("EN 16:9", CDN + "fa4e5ccd-491d-4fe2-b3eb-b99d5f3630ef.mp4", "16:9"),
                  ("FR 9:16", CDN + "f524675c-f597-41a0-a0d5-09eb2174a1c2.mp4", "9:16"), ("EN 9:16", CDN + "728f9080-6e0b-46fe-bb38-3b5476b89825.mp4", "9:16")]},
]

_S = [
    ("riviera", ("Riviera vlog", "Vlog Riviera"), ("One-minute travel vlog cut to music.", "Vlog de voyage d'une minute, monté sur la musique."), [("16:9", "775c134d-e61d-4180-aada-12744e029a73"), ("9:16", "b3a9cad5-b386-40fb-a7a3-47ec6a4c8dbc")]),
    ("launch", ("Sneaker launch", "Lancement de baskets"), ("60-second product launch, cuts on the beat.", "Lancement produit en 60 secondes, coupes sur le temps."), [("16:9", "9f9558d8-d9f6-43ce-9dc2-960446636331"), ("9:16", "4e792f56-83dd-40f7-aa6d-bbbc7a6d5afe")]),
    ("ugc", ("Skincare UGC", "UGC soin de la peau"), ("Creator on camera, product shots, captions for sound-off viewing.", "Créatrice face caméra, plans produit, sous-titres pour une lecture sans son."), [("16:9 EN", "32deeb4f-b58e-4626-8b2c-13a28ca61964"), ("16:9 FR", "04634902-c79f-4821-a021-4365cf144465"), ("9:16 EN", "036aa637-ae32-43c9-98f6-59c405315f72"), ("9:16 FR", "15d1f9c5-26a5-48bc-827c-8359c71b954c")]),
    ("ugc-ad", ("Fashion UGC ad", "Publicité UGC mode"), ("Ad structure: hook, proof, call to action.", "Structure publicitaire : accroche, preuve, appel à l'action."), [("16:9 EN", "f9699b3d-bb51-4607-b12a-76f6720a0327"), ("16:9 FR", "6e0c7c99-a912-437a-8bab-e3caa9b81a53"), ("9:16 EN", "5b6d2082-52cd-47b7-a60e-1fff8fa92bee"), ("9:16 FR", "3efd35e4-274c-4088-a72f-e21577c9c672")]),
    ("explainer", ("Espresso explainer", "Explication espresso"), ("How an espresso machine works, in three parts, with voice-over.", "Le fonctionnement d'une machine à espresso, en trois parties, avec voix off."), [("16:9 EN", "2daa9607-f55f-477e-ae62-2609f96f7a68"), ("16:9 FR", "a482a2f7-239e-4d4a-9a8a-ebe8fab44893"), ("9:16 EN", "91f9277a-42f3-4fc9-8230-7324e40061ed"), ("9:16 FR", "83ca2ea2-c20a-4f5a-9ce2-d1b3284e4f5d")]),
    ("montage", ("Première, a montage", "Première, un montage"), ("Music-led montage, no dialogue.", "Montage guidé par la musique, sans dialogue."), [("16:9", "f0300aef-48e2-4431-a4d7-1077019baaeb"), ("9:16", "37fea3b3-0df5-417c-9628-b52e35a5a1d0")]),
    ("demo", ("Ceramics demo", "Démonstration céramique"), ("Product demo filmed on the hands at work.", "Démonstration produit filmée sur les mains au travail."), [("16:9 EN", "3fae7c27-9753-4190-a60f-8c7b860e6ecd"), ("16:9 FR", "45714d9c-2029-48e3-a8ce-add6aff55604"), ("9:16 EN", "06323d6d-bf94-470a-81ef-9d3f9e9837ef"), ("9:16 FR", "1c49a9e9-584e-462c-b2a9-d1d143d384ab")]),
    ("podcast", ("Podcast clip", "Extrait de podcast"), ("One idea from a long interview, captioned.", "Une idée tirée d'un long entretien, sous-titrée."), [("16:9 EN", "b8fef201-5d47-4974-a460-469a2159383f"), ("16:9 FR", "e3a3330b-d03d-40ad-887d-5a23f20eeebd"), ("9:16 EN", "721ded78-a319-42a0-ac1a-d8654c1532c6"), ("9:16 FR", "d030c6d6-5711-4969-b155-99c65dd418ab")]),
    ("talking", ("Coach, talking head", "Coach face caméra"), ("A coach speaking to camera, minimal edit.", "Un coach face caméra, montage minimal."), [("16:9 EN", "5bc7b521-f56d-4413-bf07-655561ff6cf4"), ("16:9 FR", "d8aeb330-60dc-4042-8b4e-705c09e053eb"), ("9:16 EN", "498aaa71-77df-4996-bb04-f6a081860393"), ("9:16 FR", "b710fafa-fd72-4971-aced-20bdb28f9592")]),
    ("collage", ("Paper collage", "Collage papier"), ("Paper cut-out style with stop-motion timing.", "Style papier découpé, rythme image par image."), [("16:9", "8a570a8c-c581-46e5-a18e-21a36c957f7a"), ("9:16", "f960f218-21fc-48f7-9cd3-58b6b1c7dac7")]),
    ("showcase", ("Perfume showcase", "Vitrine parfum"), ("Luxury product, slow camera moves.", "Produit de luxe, mouvements de caméra lents."), [("16:9", "4d5d741d-4ec5-4a5e-a526-8794a358e71e"), ("9:16", "22f1e3c8-3d07-4e2c-b29b-4b4577c3bdff")]),
    ("viral", ("Five looks, a trend", "Cinq tenues, une tendance"), ("Trend format: five outfits on one beat.", "Format tendance : cinq tenues sur un même rythme."), [("16:9", "0afe151a-ba8a-4719-9a98-a4468cf7434d"), ("9:16", "b8be7f15-68f0-4de8-a0ce-c6a1b74d3b57")]),
    ("art", ("Mouvement, an art film", "Mouvement, film d'art"), ("Dance film with film grain and long dissolves.", "Film de danse, grain argentique et longs fondus."), [("16:9", "df6bb459-c667-4212-a129-53c7bf708b98"), ("9:16", "9a28e751-bed2-459b-b5c1-ff9a042e0e0a")]),
]
EDITS = [{"slug": k, "title": t[0], "kind": "Demo edit, one minute", "year": "2026", "line": l[0], "fr": (t[1], l[1]),
          "poster": f"https://bobine-tau.vercel.app/showcase/v2/{k}-clean.webp",
          "variants": [(lab, CDN + mid + ".mp4", lab.split()[0]) for lab, mid in v]} for k, t, l, v in _S]

# Journal. Images: list of (src, caption).
# The journal is written in French, in journal.py.
from journal import JOURNAL

SERVICES = [
    {"slug": "platforms", "name": "Web platforms and apps", "from": 4500, "unit": "per platform; landing pages from $1,500", "deposit": 900,
     "line": "Learning platforms, client portals, marketplaces and landing pages, with database, accounts, payments and an optional second language.",
     "example": "Uplink IT Academy: seven modules, exam sets, a ticket simulator and labs, with Stripe payments.",
     "deliverables": ["Written scope and sitemap", "Design system and mobile-first screens", "Database, sign-in and payments", "Launch on your domain, with documentation"]},
    {"slug": "ai-building", "name": "Building with AI, coached", "from": 120, "unit": "per hour; half-day workshop $600", "deposit": 120,
     "line": "Hands-on coaching for founders and teams who want to design, build and deploy products with AI assistants.",
     "example": "The method used for every platform in this portfolio, applied to your project.",
     "deliverables": ["Your project set up and deployed during the sessions", "A written playbook of the method", "Prompts and checklists", "One week of email follow-up"]},
    {"slug": "network-design", "name": "Network design, installation and documentation", "from": 5000, "unit": "per site; design and documentation only from $500", "deposit": 1500,
     "line": "Complete site networks: WiFi coverage, switching, cameras, door access, rack and cabling, drawn on your floor plans, installed and documented.",
     "example": "Office and venue deployments, each delivered with a 10-page project book.",
     "deliverables": ["Site survey and floor plan review", "Design drawings and coverage maps", "Bill of materials with list prices", "Installation, configuration and handover", "Project book in PDF"]},
    {"slug": "training-content", "name": "Training content, labs and exam practice", "from": 900, "unit": "per module", "deposit": 300,
     "line": "Scenario questions with explanations, self-grading labs, ticket scenarios and courses for IT, security and civic education.",
     "example": "200-question practice sets, scripted Cisco and Linux labs, and a ticket simulator.",
     "deliverables": ["Outline mapped to the exam objectives", "Original questions, labs or lessons", "Automatic grading for every lab", "Delivered in your platform or mine"]},
    {"slug": "books", "name": "Book editing and production", "from": 600, "unit": "editing; full production from $1,500", "deposit": 300,
     "line": "From manuscript or notes to a finished book: structure, editing, layout, figures, print-ready PDF and ebook, in French or English.",
     "example": "Two illustrated technical books of more than 200 pages, and a 265-page method book.",
     "deliverables": ["Structural and line editing", "Interior layout with figures", "Cover design", "Print-ready PDF and ebook files"]},
    {"slug": "motion", "name": "Motion design and video editing", "from": 350, "unit": "per motion piece; one-minute edit from $150; 10 edits $1,200", "deposit": 150,
     "line": "Explainer animations, product motion and one-minute social edits in 16:9 and 9:16, captioned, in French and English.",
     "example": "Bobine in 50 seconds and the 13 demo edits in the gallery.",
     "deliverables": ["Script and storyboard", "16:9 and 9:16 versions", "Captions and end card", "Source files on request"]},
    {"slug": "content-systems", "name": "Content systems for social media", "from": 800, "unit": "per month", "deposit": 400,
     "line": "A publishing system for your brand: carousels, scripts, a calendar, a review queue on your phone, and a playbook.",
     "example": "The system I use to publish for Uplink every day.",
     "deliverables": ["Monthly content calendar", "20 carousels and 5 videos per month", "Review queue on your phone", "Playbook updated every month"]},
    {"slug": "receptionist", "name": "AI phone receptionist", "from": 900, "unit": "setup; then from $149 per month", "deposit": 300,
     "line": "A bilingual receptionist that answers every call, books appointments, drafts quotes and follows up by text. Set up and managed for you.",
     "example": "Riva, built for businesses that cannot answer the phone while they work.",
     "deliverables": ["Call flow and scripts in two languages", "Connected to your existing number", "One-tap approval for the owner", "Monthly tuning and report"]},
    {"slug": "localization", "name": "French and English localization", "from": 300, "unit": "per project; $0.12 per word", "deposit": 150,
     "line": "Interfaces, books, scripts and websites translated and adapted by a native speaker of both languages.",
     "example": "Every bilingual platform in this portfolio.",
     "deliverables": ["Translation and adaptation", "String files for your app", "Terminology glossary", "Proofreading in context"]},
]

STEPS = [
    ("Send a brief", "Goal, audience, what exists today, references, budget and deadline. The form below prepares the email."),
    ("Choose a time", "Propose three time slots and a platform: Zoom, Microsoft Teams or Google Meet. I confirm one within one business day."),
    ("Reserve the consultation", "45 minutes, $150 by card, credited to the project if you go ahead within 30 days."),
    ("Meet", "We review the brief. You receive the scope, price and timeline in writing."),
    ("Deposit, build, deliver", "The deposit starts the work. You review at each milestone. Delivery includes two rounds of revisions and documentation."),
]
