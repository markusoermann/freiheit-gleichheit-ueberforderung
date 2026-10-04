# Freiheit, Gleichheit, Überforderung. — Public Beta

Öffentliche Beta-Ausgabe des Buches, **kuratiert von Markus Oermann**. Erscheint
wellenweise, Kapitel für Kapitel, als Quarto-Website (HTML), später zusätzlich als PDF
und vollständiges EPUB.

## Design-Entscheidungen (Spec)

- **Quarto-Book-Projekt** als Single Source: aus einer Quelle entstehen HTML-Site (ein
  Kapitel = eine verlinkte Seite), PDF und EPUB.
- **Single Source of Truth = das private Manuskript** `manuskript-final.md`. Dieses Repo
  enthält nur die daraus erzeugten, bereits **freigegebenen** Kapitel.
- **Design:** kühl-minimalistisch, serifenlos (Inter), ein Stahlblau-Akzent (`#2f6690`).
  Kein THWS-Logo, kein THWS-Farbschema. (`custom.scss`)
- **Kurator-Framing durchgehend:** „kuratiert von Markus Oermann" statt Autorenzeile.
- **Lizenz:** © 2026 Markus Oermann. Alle Rechte vorbehalten — frei lesbar und verlinkbar.
- **Wellen-Publishing:** `build/released.txt` steuert, welche Kapitel überhaupt erzeugt und
  in `_quarto.yml` verlinkt werden. Nicht freigegebene Kapitel landen nie im öffentlichen Repo.

## Eine neue Welle veröffentlichen

1. Kapitel-Key(s) in `build/released.txt` ergänzen (z. B. `kap-02`).
2. `python3 build/split_manuscript.py` — erzeugt die `.qmd` und aktualisiert die
   Kapitelliste in `_quarto.yml`.
3. `quarto preview` (lokal prüfen) bzw. `quarto render`.
4. `git add -A && git commit && git push` — GitHub Actions rendert und veröffentlicht auf
   GitHub Pages.

## Lokal bauen

```bash
python3 build/split_manuscript.py   # Kapitel aus dem Manuskript erzeugen
quarto preview                      # lokale Vorschau
quarto render                       # Build nach _site/
```

## Noch offen (spätere Wellen)

- PDF (Typst) und vollständiges **EPUB**.
- **Personenregister** und **Schlagwortverzeichnis** (am Ende der Wellen).
- Social-Media-Posts je Welle (Kapitel-Zusammenfassungen).
