# Designharmonisierung der Übersichten und Zustand beim UI-Sprachwechsel

Datum: 2026-10-09

## Ziel

Startseite, Unterricht (Sprachauswahl, Themenseiten-Übersicht) und Forschung (Korpusübersicht) in eine Designfamilie bringen, ohne die Seitentypen zu vereinheitlichen; außerdem die Vergleichsauswahl beim DE/EN-Wechsel erhalten.

## Consulted Sources

- `docs/spec/platform-data-files.md`, `docs/spec/research-access.md`, `docs/runbooks/test-and-ci.md`
- `app/static/css/00_tokens.css`, `10_typography.css`, `20_layout.css`, `30_components.css`, `40_cards.css`
- `app/templates/pages/{landing,teaching_page}.html`, `partials/{_corpus_card,_teaching_blocks,_pm_interactions}.html`
- `app/src/app/routes/public_content.py`, `app/src/app/i18n.py`, `app/static/js/pages/research-comparison.js`, `modules/navigation/app-bar.js`

## Geänderte Bereiche

- Gemeinsamer Vertrag `.pm-nav-surface` (Hover, Fokus-Outline, Pfeil, Reduced Motion) plus Tokens `--pm-nav-*`; vier Muster behalten ihre eigene Geometrie.
- Startseite: Panels ca. 12 % flacher (376 → 331 px), Gesamtbreite 58 → 55 rem, Bilder unverändert; Hero unberührt.
- Unterricht, Sprachauswahl: kompakte typografische Zeilen (128 → 90 px), ganze Zeile als Link mit Pfeil, „In Vorbereitung“ ohne Link/Pfeil/`aria-disabled`.
- Unterricht, Themenseiten: Hairline-Kontur, dünne Akzentlinie nur bei verfügbaren Themen, ganze Card als Link mit Pfeil, gleiche Zeilenhöhe im Grid.
- Forschung: Korpuskarten ohne Farbbalken, ganze Karte als Link, `dl` für Verantwortlichkeiten, eine Scope-Zeile mit Zahlen aus den Laufzeitdaten (23 Lernende · 5 Referenzsprecher:innen).
- Entfernt: ca. 370 Zeilen überlagerter Alt-CSS für Sprachzeilen/Themen-Cards/Korpuskarten, `pm-card--lang-*`, Öffnen-/Korpus-öffnen-Strings (`teaching.action.open_*`, `nav.open_corpus`, `research.overview.card.*_recordings.*`).
- Zustandserhaltung: `comparison-lang-handoff.js` (sessionStorage, nur beim Klick auf den Sprachumschalter, 2 min, einmalig, korpusgebunden, gegen den Katalog validiert).

## Wichtige Entscheidungen

- Zustandsprüfung: URL-Zustand (Set, Task, Filter, Player-Query) wurde vom Umschalter bereits erhalten (`app-bar.js`, `_build_ui_lang_switch_url`). Verloren ging nur die Sprecher:innen-Auswahl der Vergleichsseite (nur Speicher, per Design). Option „sessions= in der URL“ verworfen (Smoke-Invariante „kein set_id/keine Serverschreibzugriffe“, pseudonyme IDs in Logs/Referer).
- Bewusst nicht erhalten: Audiowiedergabe, Phänomene-Suchfeld, ungespeicherte Editor-Änderungen (Editor fragt vorher nach), Mittelklick/neuer Tab.

## Abweichungen

- Firefox ist in dieser Umgebung nicht installiert; Prüfung nur in Chromium. Keine Abweichung von der Spezifikation.

## Verifikation

- pytest (komplett), `node --test app/tests/js/*.test.mjs`, `scripts/qa/ci_browser_smoke.py` (263 Checks, darunter neuer Sprachwechsel-Ablauf inkl. Gegenprobe anderes Korpus; Mutation „Handoff aus“ wird rot).
- Playwright-Screenshots Desktop 1280/Mobil 390, DE/EN, Light/Dark, Hover und Fokus, kein Overflow: `tmp/ui-qa/2026-10-09-design-harmonization/`.
