# French versions of the site content. The toggle swaps them in; any missing field falls back to English.
# The platforms and their guides are written in platforms.py, in both languages.

from platforms import PROJECTS_FR as PROJECTS, GUIDES_FR as GUIDES

BOOKS = {
"camera-au-poing": {"pages": "Préface, introduction, 23 chapitres, 4 annexes", "kind": "Vlog, cinéma, montage",
    "line": "Vloguer et filmer avec un téléphone : trouver sa voix, raconter une journée, la lumière, le son, la scène, le documentaire, le sketch et le clip, puis monter avec Bobine et apprendre de chaque publication.",
    "where": [("Lire en ligne, gratuitement",), ("Sur Bobine",)]},
"contrat-du-peuple": {"pages": "Préface, 20 chapitres, épilogue", "kind": "Essai civique",
    "line": "Essai sur le contrat social au Cameroun : droits, justice et responsabilités du citoyen.",
    "where": [("Lire en ligne, gratuitement",)]},
"laa": {"pages": "13 chapitres, présentation, glossaire", "kind": "Roman",
    "line": "Premier tome d'une saga prévue en 20 volumes. Fote grandit au village de La'a, entre dans une confrérie et traverse une guerre.",
    "where": [("Lire en ligne, gratuitement",), ("Kindle",), ("Broché",)]},
"richesse-silencieuse": {"pages": "Introduction, 28 chapitres, conclusion, annexes", "kind": "Guide d'investissement",
    "line": "Un guide d'investissement pour les salariés de la diaspora africaine. Il nomme la pression de construire au pays, montre pourquoi tant de ces investissements affectifs ne rapportent jamais, et propose une méthode simple : épargner, acheter des fonds indiciels, protéger la famille, et aider les proches dans une limite fixée.",
    "where": [("Lire en ligne, gratuitement",)]},
"capital-entrave": {"pages": "Prologue, 50 chapitres en 7 parties, carnet de décision, sources", "kind": "Essai, économie",
    "line": "Pourquoi l'économie camerounaise piétine : le travail et l'épargne ne deviennent pas du capital quand les titres fonciers, les règles et les institutions font défaut. Quelques-uns titrent et accumulent les terrains pour spéculer ; la plupart des familles possèdent un bien qu'elles ne peuvent pas mettre en garantie.",
    "where": [("Lire en ligne, gratuitement",)]},
"monnaie-terre-merite": {"pages": "Introduction, 42 chapitres en 3 livres, lettre aux décideurs, 5 annexes", "kind": "Essai, politique publique",
    "line": "Trois réformes dures pour le Cameroun, écrites pour ceux qui décident : faire passer le franc CFA des espèces au numérique sans changer de monnaie ; reconstruire la terre, l'industrie et la finance comme l'Asie de l'Est l'a fait ; traiter l'économie comme un échange entre individus libres, pas comme une rente partagée entre clans. Avec le démonstrateur interactif e-XAF.",
    "where": [("Lire en ligne, gratuitement",), ("Démonstrateur e-XAF",)]},
"bobine-la-methode": {"pages": "265 pages", "kind": "Méthode de production vidéo",
    "line": "Planifier, filmer, monter avec l'IA et vendre du contenu vidéo, avec une journée de tournage pour un mois de publications. Le PDF est vendu sur Bobine.",
    "where": [("Lire en ligne, gratuitement",), ("PDF sur Bobine",)]},
"unifi-ground-up": {"pages": "241 pages, 59 figures", "kind": "Réseaux",
    "line": "Concevoir et exploiter un réseau d'entreprise avec UniFi : passerelles, commutation, WiFi, caméras, contrôle d'accès, baies et exploitation. Chapitres d'essai gratuits.",
    "where": [("Chapitres d'essai",)]},
"msp-30-days": {"pages": "214 pages, 11 figures", "kind": "Entreprise IT",
    "line": "Un plan jour par jour pour lancer seul une société de services informatiques : offre, tarifs, contrat, outils de supervision, premiers clients.",
    "where": [("Chapitres d'essai",)]},
"project-book": {"pages": "10 pages, US Letter", "kind": "Format de document",
    "line": "Le document de 10 pages remis à chaque client de Lemon Network Solutions : conception, cartes de couverture, baie et câblage, nomenclature, calendrier et réception.",
    "where": [("Voir l'exemple",)]},
}

ALBUM = {"kind": "Album", "line": "Album de synthétiseurs composé pour le film et la vidéo, publié sous le nom de Wfoss.",
         "where": [("Écouter sur Spotify",)]}

SERVICES = {
"platforms": {"name": "Plateformes et applications web", "unit": "par plateforme ; pages d'accueil dès 1 500 $",
    "line": "Plateformes de formation, portails clients, places de marché et pages d'accueil, avec base de données, comptes, paiements et une seconde langue si besoin.",
    "example": "Uplink IT Academy : sept modules, séries d'examens, simulateur de tickets et labs, avec paiements Stripe.",
    "deliverables": ["Périmètre et arborescence par écrit", "Système de design et écrans pensés pour mobile", "Base de données, connexion et paiements", "Mise en ligne sur votre domaine, avec documentation"]},
"ai-building": {"name": "Construire avec l'IA, accompagné", "unit": "de l'heure ; atelier d'une demi-journée 600 $",
    "line": "Un accompagnement concret pour les fondateurs et les équipes qui veulent concevoir, construire et déployer des produits avec des assistants IA.",
    "example": "La méthode utilisée pour chaque plateforme de ce portfolio, appliquée à votre projet.",
    "deliverables": ["Votre projet monté et déployé pendant les séances", "Un guide écrit de la méthode", "Prompts et listes de contrôle", "Une semaine de suivi par courriel"]},
"network-design": {"name": "Conception, installation et documentation réseau", "unit": "par site ; conception et documentation seules dès 500 $",
    "line": "Des réseaux de site complets : couverture WiFi, commutation, caméras, contrôle d'accès, baie et câblage, dessinés sur vos plans, installés et documentés.",
    "example": "Des déploiements de bureaux et de salles, chacun livré avec un dossier de projet de 10 pages.",
    "deliverables": ["Visite du site et revue des plans", "Plans de conception et cartes de couverture", "Nomenclature avec prix catalogue", "Installation, configuration et remise", "Dossier de projet en PDF"]},
"training-content": {"name": "Contenu de formation, labs et préparation aux examens", "unit": "par module",
    "line": "Questions de mise en situation avec explications, labs auto-corrigés, scénarios de tickets et cours pour l'informatique, la sécurité et l'éducation civique.",
    "example": "Séries de 200 questions, labs Cisco et Linux scénarisés, et un simulateur de tickets.",
    "deliverables": ["Plan aligné sur les objectifs de l'examen", "Questions, labs ou leçons originaux", "Correction automatique pour chaque lab", "Livré sur votre plateforme ou la mienne"]},
"books": {"name": "Édition et production de livres", "unit": "édition ; production complète dès 1 500 $",
    "line": "D'un manuscrit ou de notes à un livre fini : structure, édition, mise en page, figures, PDF prêt à imprimer et livre numérique, en français ou en anglais.",
    "example": "Deux livres techniques illustrés de plus de 200 pages, et un livre de méthode de 265 pages.",
    "deliverables": ["Édition structurelle et révision du texte", "Mise en page intérieure avec figures", "Couverture", "PDF prêt à imprimer et fichiers numériques"]},
"motion": {"name": "Motion design et montage vidéo", "unit": "par animation ; montage d'une minute dès 150 $ ; 10 montages 1 200 $",
    "line": "Animations explicatives, motion produit et montages d'une minute pour les réseaux en 16:9 et 9:16, sous-titrés, en français et en anglais.",
    "example": "Bobine en 50 secondes et les 13 montages de démonstration de la galerie.",
    "deliverables": ["Script et storyboard", "Versions 16:9 et 9:16", "Sous-titres et carton final", "Fichiers sources sur demande"]},
"content-systems": {"name": "Systèmes de contenu pour les réseaux sociaux", "unit": "par mois",
    "line": "Un système de publication pour votre marque : carrousels, scripts, calendrier, file de relecture sur téléphone et guide de méthode.",
    "example": "Le système que j'utilise pour publier chaque jour pour Uplink.",
    "deliverables": ["Calendrier éditorial mensuel", "20 carrousels et 5 vidéos par mois", "File de relecture sur votre téléphone", "Guide mis à jour chaque mois"]},
"receptionist": {"name": "Réceptionniste téléphonique IA", "unit": "installation ; puis dès 149 $ par mois",
    "line": "Une réceptionniste bilingue qui répond à chaque appel, prend les rendez-vous, prépare les devis et relance par SMS. Installée et gérée pour vous.",
    "example": "Riva, conçue pour les entreprises qui ne peuvent pas décrocher en travaillant.",
    "deliverables": ["Parcours d'appel et scripts en deux langues", "Reliée à votre numéro actuel", "Validation du patron d'un geste", "Réglage et rapport mensuels"]},
"localization": {"name": "Localisation français et anglais", "unit": "par projet ; 0,12 $ le mot",
    "line": "Interfaces, livres, scripts et sites traduits et adaptés par un locuteur natif des deux langues.",
    "example": "Chaque plateforme bilingue de ce portfolio.",
    "deliverables": ["Traduction et adaptation", "Fichiers de textes pour votre application", "Glossaire terminologique", "Relecture en contexte"]},
}

STEPS = [
    ("Envoyez un brief", "Objectif, public, existant, références, budget et échéance. Le formulaire ci-dessous prépare le courriel."),
    ("Choisissez un créneau", "Proposez trois créneaux et une plateforme : Zoom, Microsoft Teams ou Google Meet. Je confirme sous un jour ouvré."),
    ("Réservez la consultation", "45 minutes, 150 $ par carte, déduits du projet s'il démarre dans les 30 jours."),
    ("Rencontrons-nous", "Nous passons le brief en revue. Vous recevez le périmètre, le prix et le calendrier par écrit."),
    ("Acompte, réalisation, livraison", "L'acompte lance le travail. Vous validez chaque étape. La livraison comprend deux séries de corrections et la documentation."),
]

JOURNAL = {}  # the journal is written in French (journal.py)
