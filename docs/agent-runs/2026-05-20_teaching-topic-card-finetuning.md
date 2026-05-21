# Teaching Topic-Card Finetuning

Datum: 2026-05-20

## Ziel

Gezielter Finetuning-Run nur für die Topic-Cards auf den Sprachübersichtsseiten unter `/{ui_lang}/teaching/{language}`. Nicht im Scope: H1/Hero/Intro, Sprachkarten der Sprachauswahlseite, Back-Links, Breadcrumbs, Kategorieüberschriften inklusive Underlines sowie die eigentlichen Themenseiten.

## Consulted Sources

- Root- und Scoped-Governance in `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`
- Repo-Anweisungen in `.github/instructions/repo.instructions.md`
- produktive Teaching-Templates und CSS in `app/templates/partials/_teaching_blocks.html`, `app/templates/pages/teaching_page.html`, `app/templates/pages/sample_page.html`, `app/static/css/20_layout.css`, `app/static/css/30_components.css`, `app/static/css/40_cards.css`

## Geänderte Bereiche

- `app/templates/partials/_teaching_blocks.html`
- `app/templates/pages/teaching_page.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`

## Wichtige Entscheidungen

- Die Topic-Tag-Daten wurden nicht aus den zugrunde liegenden Datenstrukturen entfernt. `card.metadata` bleibt bestehen, wird für die Sprachübersichtsseiten aber nicht mehr gerendert.
- Dafür wurde im gemeinsamen Topic-Card-Makro ein kompakter Variant-Pfad eingeführt: `pm-teaching-topic-card--compact`. Dieser Variant wird nur auf Sprachübersichtsseiten und in `sample` verwendet; Topic-Page-Card-Aufrufe in `_teaching_blocks.html` bleiben im bisherigen Pfad.
- Das sichtbare Rendering der Hub-Cards wurde auf Titel, Kurzbeschreibung und Aktion/Status reduziert. Es werden keine leeren Meta-Wrapper oder Pill-Platzhalter mehr ausgegeben.
- Die neue vereinfachte Struktur wird vor allem über diese Klassen getragen:
  - `pm-teaching-topic-card--compact`
  - `pm-teaching-topic-card__body`
  - `pm-teaching-topic-card__action`
  - `pm-teaching-topic-card__status`
  - `pm-teaching-topic-grid`
- Aktive und nicht verfügbare Cards bleiben getrennt:
  - verfügbar: Link-Card mit `pm-card--interactive`, sichtbare Aktion `Öffnen →` bzw. `Open →`, dezenter Hover bleibt aktiv
  - nicht verfügbar: `article[aria-disabled="true"]`, Status `In Vorbereitung` bzw. `In preparation`, `cursor: default`, kein Link und keine Tastatur-Fokussierung als Link

## Abweichungen

- Keine Spezifikationsänderung erforderlich; der Run ist ein lokales UI-Finetuning innerhalb bestehender Teaching-Hub-Oberflächen.

## Verifikation

- Fokussierte Regressionstests:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "test_teaching_language_root_uses_shared_topbar_and_mobile_drawer or test_teaching_english_hub_stays_within_english_edition_topics or test_sample_page_reflects_current_landing_and_corpus_cards or test_teaching_pilot_topic_renders_canonical_two_column_storytelling"` -> `4 passed`
- Live-Server für eindeutige QA separat auf `http://127.0.0.1:8010` gestartet
- Live-DOM-/Layout-Checks auf `http://127.0.0.1:8010/de/teaching/spanish`:
  - `metaCount: 0`
  - `pillCount: 0`
  - verfügbarer Card-Abstand Beschreibung -> Aktion nach finalem Fix ca. `11.2px`
  - Pending-Cards bleiben `article[aria-disabled="true"]` ohne `href`
- Desktop-Screenshots:
  - `tmp/ui-qa/2026-05-20-teaching-topic-card-finetuning/de-desktop-1440x1400.png`
  - `tmp/ui-qa/2026-05-20-teaching-topic-card-finetuning/en-desktop-1440x1400.png`
- Mobile-Screenshots:
  - `tmp/ui-qa/2026-05-20-teaching-topic-card-finetuning/de-mobile-390x844.png`
  - `tmp/ui-qa/2026-05-20-teaching-topic-card-finetuning/en-mobile-390x844.png`

## Offene Punkte

- Die sehr hohen Mobile-Captures per Edge headless liefen in dieser Umgebung nicht stabil weiter; die vorhandenen 390px-Screenshots decken die mobile Route ab, während die kompakte Card-Struktur zusätzlich über Live-DOM-Metriken und die fokussierten Tests abgesichert ist.

## Nächste sinnvolle Schritte

- Falls gewünscht, kann ein weiterer enger Run nur noch die Mobile-QA-Artefakte der Hub-Cards auf tiefere Viewport-Ausschnitte zuschneiden, ohne den produktiven Code noch einmal anzufassen.