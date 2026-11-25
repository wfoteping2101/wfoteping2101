# Engineering records for the project pages: role, size, architecture diagram, stack by layer,
# key decisions and notes. Each text is (English, French). Records live in eng_a/b/c.py, keyed by slug.
# House rules: no em or en dashes, no emojis, no phone numbers, never name the day job employer.
from academic import fr_typo

LAYERS = {
    "front": ("Interface", "Interface"),
    "server": ("Server and API", "Serveur et API"),
    "data": ("Data and storage", "Données et stockage"),
    "auth": ("Identity and access", "Identité et accès"),
    "ai": ("AI", "IA"),
    "pay": ("Payments", "Paiements"),
    "maps": ("Maps and geodata", "Cartes et géodonnées"),
    "media": ("Media", "Médias"),
    "chain": ("Blockchain", "Blockchain"),
    "offline": ("Offline", "Hors ligne"),
    "engine": ("Engine", "Moteur"),
    "content": ("Content pipeline", "Chaîne de contenu"),
    "infra": ("Hosting and CI", "Hébergement et CI"),
    "test": ("Testing", "Tests"),
}

COLS = {
    "client": ("Client", "Client"),
    "device": ("Device", "Appareil"),
    "edge": ("Edge and routing", "Périphérie et routage"),
    "server": ("Server", "Serveur"),
    "worker": ("Background work", "Tâches de fond"),
    "data": ("Data", "Données"),
    "ext": ("External services", "Services externes"),
    "build": ("Build time", "Construction"),
    "chain": ("Chain", "Chaîne"),
    "state": ("State", "État"),
    "logic": ("Domain logic", "Logique métier"),
}

NOTE = {
    "data": ("Data model", "Modèle de données"),
    "sec": ("Security", "Sécurité"),
    "test": ("Testing", "Tests"),
    "next": ("Limits and next steps", "Limites et suite"),
    "perf": ("Performance", "Performance"),
}

from eng_a import EA
from eng_b import EB
from eng_c import EC
from eng_etali import EE
from eng_paradoxe import EP


def _fr(x):
    """Apply French typography to the French half of every (en, fr) pair, recursively."""
    if isinstance(x, tuple) and len(x) == 2 and all(isinstance(v, str) for v in x):
        return (x[0], fr_typo(x[1]))
    if isinstance(x, (list, tuple)):
        return type(x)(_fr(v) for v in x)
    if isinstance(x, dict):
        return {k: _fr(v) for k, v in x.items()}
    return x


ENG = {k: _fr(v) for k, v in {**EA, **EB, **EC, **EE, **EP}.items()}

# Sanity checks run at build time.
for _s, _e in ENG.items():
    assert len(_e.get("links", [])) == len(_e["arch"]) - 1, _s + ": one link label per arrow"
    for _k, _ in _e["layers"]:
        assert _k in LAYERS, _s + ": unknown layer " + _k
    for _k, _ in _e["arch"]:
        assert _k in COLS, _s + ": unknown column " + _k
    for _k, _ in _e.get("notes", []):
        assert _k in NOTE, _s + ": unknown note " + _k
