# Finaler Single-Column-Transferblock für which-pronunciation

Datum: 2026-05-13

## Ziel

Den Abschnitt „Impulse für den Unterricht“ auf der DE-Route ein letztes Mal visuell beruhigen (klarere ruhige Abschnittsfläche, einspaltige Karten, zentrierte Desktop-Breite, Nummer+Titel in einer Kopfzeile) und danach dieselbe Komponentenlogik auf EN übertragen, ohne die bestehende Citation-/Icon-Systematik zu brechen.

## Consulted Sources

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`
- Live-Route HTML-Auszug für `didactic_close`

## Geänderte Bereiche

- route-scopte Styling-Regeln für `pm-teaching-page--topic[data-topic-slug="which-pronunciation"]` in `app/static/css/30_components.css`
- keine inhaltliche Änderung an den YAML-Texten der vier Impulskarten
- finaler QA-Scriptlauf unter `tmp/ui-qa/2026-05-13-which-pronunciation-final-single-column/`

## Wichtige Entscheidungen

- Der Umbau blieb im bestehenden `rich_text`-/`didactic_close`-Pfad; Nummer+Titel-Kopfzeile wird über CSS auf der real gerenderten Struktur (`strong + br + Text`) umgesetzt.
- Die Karten wurden auf einspaltige Reihenfolge umgestellt, um die visuelle Unruhe ungleicher Textlängen im 2×2-Grid zu eliminieren.
- Die Desktop-Breite wurde als Anteil der tatsächlichen Rich-Text-Body-Breite umgesetzt (`84%`), nicht als Anteil des gesamten Seitenpanels.
- Die Logik wurde nach DE-Finalisierung auf EN übertragen, ohne deutsche Texte zu übernehmen.

## Abweichungen

- Keine Abweichung von aktiven Regeln. Änderungen bleiben route-scoped auf `which-pronunciation`.

## Verifikation

- `pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation"` -> 2 bestanden
- Integrierter Browser (Live-DOM):
  - DE und EN: Citation-Section bleibt separat, Bottom-Backlink bleibt am Seitenende
  - Copy-State: `done`, transparenter Hintergrund/Rand, keine Badge-Fläche
  - Icongrößen unverändert im Zielbereich (Quote ~22.4px, Copy/Check ~23.2px, Context ~21.6px)
- Headless Playwright Final-QA (Desktop + Mobile) mit Screenshots:
  - Ordner: `tmp/ui-qa/2026-05-13-which-pronunciation-final-single-column/`
  - Dateien: `de_desktop.png`, `de_mobile.png`, `en_desktop.png`, `en_mobile.png`
  - Messwerte:
    - DE Desktop: `columns=1`, `bodyRatio=0.84`, `furtherReadingCount=0`, Backlink korrekt, Copy-State done
    - DE Mobile: `columns=1`, `bodyRatio=1.0`, `furtherReadingCount=0`, Backlink korrekt, Copy-State done
    - EN Desktop: `columns=1`, `bodyRatio=0.84`, `furtherReadingCount=0`, Backlink korrekt, Copy-State done
    - EN Mobile: `columns=1`, `bodyRatio=1.0`, `furtherReadingCount=0`, Backlink korrekt, Copy-State done
    - EN-Guard: keine deutschen UI-Texte erkannt

## Offene Punkte

- Keine offenen Punkte im bearbeiteten Scope.

## Nächste sinnvolle Schritte

- Falls gewünscht, denselben einspaltigen Transferkarten-Standard auf weitere didaktische Abschlussblöcke in Teaching-Topics übertragen.
