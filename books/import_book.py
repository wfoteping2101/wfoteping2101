#!/usr/bin/env python3
"""Turn a finished manuscript (.docx, .md or a folder of chapter .md files) into books/richesse.json for the reading room.

Usage:  python3 books/import_book.py <manuscript.docx | manuscript.md | chapters_folder> [--subtitle "..."]
Every top level heading (# ...) starts a section. "Chapitre N : Titre" (or with a dash) becomes chapter N.
"Partie ..." headings with little text are folded into the next chapter's label. Needs pandoc for .docx.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def to_markdown(src):
    if os.path.isdir(src):
        files = sorted(f for f in os.listdir(src) if f.endswith(".md"))
        def key(f):
            m = re.search(r"(\d+)", f); base = f.lower()
            if "avant" in base or "intro" in base or base.startswith("00"): return (0, f)
            if "conclusion" in base: return (2, f)
            if "annexe" in base: return (3, f)
            return (1, int(m.group(1)) if m else 999)
        return "\n\n".join(open(os.path.join(src, f), encoding="utf-8").read() for f in sorted(files, key=key))
    if src.lower().endswith(".docx"):
        return subprocess.run(["pandoc", src, "-t", "gfm", "--wrap=none"], check=True, capture_output=True, text=True).stdout
    return open(src, encoding="utf-8").read()

def slug(s):
    s = s.lower()
    for a, b in (("é", "e"), ("è", "e"), ("ê", "e"), ("à", "a"), ("â", "a"), ("ç", "c"), ("ô", "o"), ("î", "i"), ("û", "u"), ("ù", "u")): s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]

def split(md):
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)  # yaml front matter
    md = re.sub(r"\{#[^}]*\}", "", md)                      # pandoc heading ids
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    parts, cur = [], None
    for line in md.split("\n"):
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            cur = {"head": m.group(1).strip().strip("*"), "body": []}; parts.append(cur); continue
        if cur is None: continue
        cur["body"].append(line)
    out, pending_part, seen = [], "", set()
    for p in parts:
        head, body = p["head"], "\n".join(p["body"]).strip()
        if re.match(r"^(Partie|Part)\b", head, re.I) and len(body.split()) < 120:
            pending_part = head; continue
        m = re.match(r"^Chapitre\s+(\d+)\s*(?:[:.—–-]+)\s*(.+)$", head, re.I)
        if m:
            n, title = m.group(1), m.group(2).strip()
            sec = {"id": f"chapitre-{n}", "label": f"Chapitre {n}", "title": title, "kind": "chapter"}
        else:
            t2 = re.split(r"\s+[—–-]\s+|\s*:\s+", head, maxsplit=1)
            label = t2[0].strip(); title = t2[1].strip() if len(t2) > 1 else label
            sec = {"id": slug(label) or "section", "label": label, "title": title, "kind": "front" if not out or label.lower().startswith(("avant", "préface", "preface", "introduction")) else "back"}
        if pending_part: sec["part"] = pending_part; pending_part = ""
        while sec["id"] in seen: sec["id"] += "-b"
        seen.add(sec["id"])
        sec["body"] = re.sub(r"\n{3,}", "\n\n", body)
        out.append(sec)
    return out

def main():
    args = sys.argv[1:]
    if not args: print(__doc__); sys.exit(1)
    sub = None
    if "--subtitle" in args: i = args.index("--subtitle"); sub = args[i + 1]; del args[i:i + 2]
    secs = split(to_markdown(args[0]))
    data = {"title": "La Richesse Silencieuse", "sections": secs}
    if sub: data["subtitle"] = sub
    dst = os.path.join(HERE, "richesse.json")
    json.dump(data, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    words = sum(len(s["body"].split()) for s in secs)
    print(f"{len(secs)} sections, {words:,} words -> {dst}")
    for s in secs: print(" ", s["id"], "|", s["label"], "|", s["title"][:60], "|", len(s["body"].split()))

if __name__ == "__main__":
    main()
