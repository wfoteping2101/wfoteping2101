"""Academic records for the portfolio: platform pages and book catalogue entries.

The descriptive text lives in acad_a.py, acad_b.py, acad_c.py (platforms, by number)
and acad_books.py (books). Each value is an (English, French) pair. This module
overlays those records on the data in platforms.py, content.py and fr.py, and
applies French typographic spacing to the French side.
"""
import re
from acad_a import A
from acad_b import B
from acad_c import C
from acad_thales import T
from acad_etali import E as ETALI_RECORD
from acad_books import BOOKS as BOOK_RECORDS

PLATFORM_RECORDS = {**T, **A, **B, **C, **ETALI_RECORD}

NNBSP, NBSP = " ", " "


def fr_typo(s):
    """French spacing: thin no-break space before ; ? ! and digit groups, no-break space before : and inside guillemets."""
    s = s.replace(" ;", NNBSP + ";").replace(" ?", NNBSP + "?").replace(" !", NNBSP + "!")
    s = s.replace(" :", NBSP + ":").replace("« ", "«" + NBSP).replace(" »", NBSP + "»").replace(" $", NBSP + "$")
    s = re.sub(r"(\d) (\d{3})\b", lambda m: m.group(1) + NNBSP + m.group(2), s)
    return s


def _pair(p):
    return (p[0], fr_typo(p[1]))


def apply_platforms(platforms):
    for P in platforms:
        r = PLATFORM_RECORDS.get(P["slug"])
        if not r:
            continue
        P["kind"] = _pair(r["kind"])
        P["line"] = _pair(r["line"])
        P["facts"] = [(_pair(k), _pair(v)) for k, v in r["facts"]]
        P["sections"] = [(_pair(h), _pair(x)) for h, x in r["sections"]]


def apply_books_en(books):
    for b in books:
        r = BOOK_RECORDS.get(b["slug"])
        if r:
            for key in ("kind", "pages", "line"):
                b[key] = r[key][0]


def apply_books_fr(fr_books):
    for slug, r in BOOK_RECORDS.items():
        d = fr_books.setdefault(slug, {})
        for key in ("kind", "pages", "line"):
            d[key] = fr_typo(r[key][1])
