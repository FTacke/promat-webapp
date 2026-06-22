# Darkmode-Kontrast-Fix: „Vertiefung"-Kasten (Teaching)

**Datum:** 2026-06-22

## Aufgabe

Darkmode-Kontrastfehler beim `further_reading`-Block auf Teaching-Themenseiten beheben. Im Darkmode erschien der „Vertiefung"-Kasten fast weiß, während Text, Links und Icons korrekt in hellen Farben gerendert wurden → nicht lesbar.

## Ursache

`--pm-admonition-weiterlesen-bg` ist im `:root`-Block definiert als:

```css
color-mix(in srgb, var(--book-paper) 82%, var(--pm-surface-paper) 18%)
```

`--book-paper: #fbfaf8` ist ein statischer, globaler Token **ohne Dark-Mode-Override**. Im Darkmode löst der Hintergrund daher zu ~`#fbfaf8` auf (fast weiß), während Textfarben (`--book-fg`) korrekt auf hellgrau angepasst werden → helle Schrift auf hellem Hintergrund.

Dieselbe Ursache betraf auch `--pm-admonition-weiterlesen-border` und `--pm-admonition-weiterlesen-accent`, die ebenfalls `--book-paper`-abhängig sind.

## Lösung

Drei Dark-Mode-Overrides im `html[data-theme="dark"], html[data-theme="auto"][data-system-dark="true"]`-Block in `app/static/css/00_tokens.css` hinzugefügt:

```css
--pm-admonition-weiterlesen-bg: color-mix(in srgb, var(--book-surface-2) 86%, var(--book-bg) 14%);
--pm-admonition-weiterlesen-border: color-mix(in srgb, var(--book-border) 94%, transparent);
--pm-admonition-weiterlesen-accent: color-mix(in srgb, var(--book-adm-weiterlesen) 48%, var(--book-surface-2) 52%);
```

Folgt dem Pattern der anderen Dark-Mode-Admonition-Overrides (z. B. `--pm-admonition-citation-bg`).

## Geänderte Dateien

- `app/static/css/00_tokens.css` — 3 Zeilen im Dark-Mode-Block ergänzt

## Checks

- `ruff check .` → All checks passed
- `compileall -q app scripts` → sauber
- `validate_teaching_content.py` → Teaching content validation passed for 4 teaching languages
- Teaching-Tests: 11 vorbestehende Fehler (in `test_research_sessions.py`, `test_teaching_content.py`), kein neuer Fehler durch diese Änderung

## Lightmode

Unverändert — alle drei neuen Regeln sind ausschließlich im Dark-Mode-Selektor. Lightmode nutzt weiterhin die Basis-`:root`-Definitionen.
