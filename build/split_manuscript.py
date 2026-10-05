#!/usr/bin/env python3
"""Split the private manuscript into per-chapter Quarto .qmd files.

Single source of truth = the private manuskript-final.md. Only chapters listed
in build/released.txt are generated and wired into _quarto.yml (wave publishing).
Unreleased chapters are never written into this (public) repo.

Usage:  python3 build/split_manuscript.py
"""
import re
import pathlib

PROJ = pathlib.Path(__file__).resolve().parent.parent
MANUSCRIPT = pathlib.Path(
    "/Users/markus/Library/Mobile Documents/com~apple~CloudDocs/"
    "THWS/Projekte/Buch/manuskript-final.md"
)
CHAPTERS = PROJ / "chapters"
RELEASED = PROJ / "build" / "released.txt"
QUARTO = PROJ / "_quarto.yml"

# Buch-spezifische Ueberschriften (ueberschreiben die Manuskript-Headings).
TITLE_OVERRIDES = {
    "einleitung": "Einleitung",
    "kap-01": "Das Versprechen der Moderne",
}


def parse_chapters(text):
    """Return list of {titel, body(list of lines)} by detecting frontmatter
    blocks that actually contain a `titel:` field (ignores body `---` rules)."""
    lines = text.split("\n")
    starts = []
    for i, ln in enumerate(lines):
        if ln.strip() == "---":
            window = lines[i + 1:i + 9]
            has_titel = any(re.match(r"\s*titel\s*:", w) for w in window)
            has_close = any(w.strip() == "---" for w in window)
            if has_titel and has_close:
                starts.append(i)
    chapters = []
    for idx, s in enumerate(starts):
        close = next(j for j in range(s + 1, len(lines)) if lines[j].strip() == "---")
        fm = "\n".join(lines[s + 1:close])
        body_end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        body = lines[close + 1:body_end]
        m = re.search(r'titel\s*:\s*"?(.*?)"?\s*$', fm, re.M)
        titel = m.group(1).strip() if m else f"kapitel-{idx}"
        chapters.append({"titel": titel, "body": body})
    return chapters


def heading_of(body):
    for l in body:
        if l.startswith("# "):
            return l[2:].strip()
    return None


def key_order(heading, titel):
    h = heading or titel
    if re.match(r"Vorwort", h, re.I):
        return ("vorwort", 0)
    if re.match(r"Einleitung", h, re.I):
        return ("einleitung", 1)
    m = re.search(r"Kapitel\s+(\d+)", h)
    if m:
        n = int(m.group(1))
        return (f"kap-{n:02d}", 1 + n)
    slug = re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-")
    return (slug or "kapitel", 99)


def clean_body(body, title_override=None):
    """Drop pre-heading content (e.g. the Vorwort epigraph), set the chapter H1
    (optionally overridden for the book), mark it unnumbered, and remove the
    manual '## Anmerkungen' heading (Quarto renders the footnotes itself)."""
    for i, l in enumerate(body):
        if l.startswith("# "):
            body = body[i:]
            break
    if body and body[0].startswith("# "):
        if title_override:
            body[0] = f"# {title_override} {{.unnumbered}}"
        elif "{" not in body[0]:
            body[0] = body[0].rstrip() + " {.unnumbered}"
    out = [l for l in body if not re.match(r"##\s+Anmerkungen\s*$", l)]
    return "\n".join(out).strip() + "\n"


def main():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    chapters = parse_chapters(text)
    released = []
    if RELEASED.exists():
        released = [x.strip() for x in RELEASED.read_text(encoding="utf-8").splitlines()
                    if x.strip() and not x.lstrip().startswith("#")]

    for ch in chapters:
        ch["heading"] = heading_of(ch["body"])
        ch["key"], ch["order"] = key_order(ch["heading"], ch["titel"])

    CHAPTERS.mkdir(exist_ok=True)
    written = []
    for ch in sorted(chapters, key=lambda c: c["order"]):
        if ch["key"] in released:
            (CHAPTERS / f'{ch["key"]}.qmd').write_text(
                clean_body(ch["body"], TITLE_OVERRIDES.get(ch["key"])), encoding="utf-8")
            written.append(ch)

    chap_lines = ["    - index.qmd"] + [f'    - chapters/{c["key"]}.qmd' for c in written]
    y = QUARTO.read_text(encoding="utf-8")
    begin, end = "    # BEGIN chapters", "    # END chapters"
    pre, _, rest = y.partition(begin)
    _, _, post = rest.partition(end)
    QUARTO.write_text(pre + begin + "\n" + "\n".join(chap_lines) + "\n" + end + post, encoding="utf-8")

    print(f"Kapitel im Manuskript erkannt: {len(chapters)}")
    print(f"Freigegeben & geschrieben: {len(written)}")
    for c in written:
        print(f"  [{c['order']:>2}] {c['key']}.qmd  <-  {c['heading']}")
    missing = [r for r in released if r not in {c['key'] for c in written}]
    if missing:
        print(f"WARNUNG: in released.txt, aber nicht im Manuskript gefunden: {missing}")
    print("\nAlle erkannten Kapitel (Reihenfolge / key):")
    for c in sorted(chapters, key=lambda c: c["order"]):
        mark = "x" if c["key"] in released else " "
        print(f"  [{mark}] {c['key']:<12} {c['heading']}")


if __name__ == "__main__":
    main()
