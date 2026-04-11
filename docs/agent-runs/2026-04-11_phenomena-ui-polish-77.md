# Phänomene UI Polish

Datum: 2026-04-11

## Ziel

Die neue split `phenomena`-Overview und den Editor deutlich ruhiger, dichter und systemnäher ausarbeiten, ohne die neue Overview/Editor-Architektur wieder zu verändern.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/templates/pages/research_comparison.html`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-comparison.js`
- `data/config/research_player/spanish/phenomena_presets.json`

## Geänderte Bereiche

- `app/templates/pages/research_phenomena_overview.html`
- `app/templates/pages/research_phenomena_editor.html`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_phenomena.py`

## Wichtige Entscheidungen

- Die visuelle Nachschärfung bleibt strikt innerhalb der bestehenden Split-Architektur; Overview bleibt Listen-Einstieg, Editor bleibt fokussierte Kurationsfläche.
- Statt neuer Phänomene-spezifischer UI-Sprache wurden vorhandene Muster aus `comparison`, `player` und den shared Controls bewusst wiederverwendet.
- Die Overview wurde von schweren Karten auf ruhigere horizontale Listenzeilen verschoben.
- Der Editor übernimmt stärker die Listen- und Badge-Logik aus `player` und `comparison`, insbesondere für Status, Source-Rows und Selected-Items.

## Abweichungen

- Keine Abweichung von der aktiven Spezifikation.
- Für die Live-Screenshot-Validierung musste statt des älteren Fixture-Ids `starter_preset` ein tatsächlich vorhandenes lokales Preset wie `question_prosody_paths` verwendet werden.

## Verifikation

- Editor-Problems-Check für die geänderten CSS-Dateien, zuletzt ohne Fehler.
- Headless-Browser-Validierung mit aktualisierten Screenshots unter `tmp/ui-qa/phenomena-ui-polish-77/`.
- Manuelle Sichtprüfung der zentralen Screenshots für Overview, Editor-Head, Note-Field, muted Source-Rows und Selected-Items.
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sets.py tests/test_research_phenomena.py`
  - Ergebnis: `25 passed`

## Offene Punkte

- Keine neue fachliche Lücke gefunden; offen war am Ende nur die letzte Test-Anpassung an die neue gerenderte Overview-Überschrift.
- Der lokale Dev-Server lief für die Browser-QA weiter und kann nach Bedarf beendet werden.

## Nächste sinnvolle Schritte

- Falls noch gewünscht, eine letzte gemeinsame Sichtprüfung direkt gegen die laufende Dev-Instanz.
- Danach den laufenden Dev-Server wieder beenden.