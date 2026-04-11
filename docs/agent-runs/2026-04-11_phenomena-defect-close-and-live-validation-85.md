# Phenomena Defect Close And Live Validation 85

Datum: 2026-04-11

## Ziel

Die noch offenen produktiven `phenomena`-Defekte gezielt im echten lokalen Dev-Flow reproduzieren, beheben und erst nach realer Browser-Validierung gegen `http://127.0.0.1:8000` schließen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `docs/runbooks/ui-change-workflow.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_phenomena_views.py`
- `app/src/app/research_views.py`
- `app/src/app/routes/public.py`
- `app/src/app/__init__.py`
- `app/templates/pages/research_phenomena_overview.html`
- `app/templates/pages/research_phenomena_editor.html`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/static/js/pages/research-phenomena-overview.js`
- `app/static/css/00_tokens.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`
- `app/tests/test_research_phenomena.py`
- `scripts/dev-start.ps1`
- `app/scripts/dev-start.ps1`

## Geänderte Bereiche

- `comparison`-Setquelle im Client für gespeicherte owner-bound Custom-Sets
- Dirty-Navigation im `phenomena`-Editor über den vorhandenen App-Dialog statt über den Browserprompt bei normaler In-App-Navigation
- Badge- und Status-Tokens für `gespeichert` und `ungespeichert`
- aktive `research-access`-Spec für den produktiven Dirty-Navigation-Flow
- finaler Runtime- und Live-QA-Durchlauf inklusive Screenshot-Artefakten unter `tmp/ui-qa/phenomena-defect-close-84-final/`

## Wichtige Entscheidungen

- Saved Custom-Sets in `comparison` werden nicht mehr nur über serverseitig injizierte HTML-Presetdaten abgesichert; der Client lädt sie zusätzlich direkt aus `/api/research/sets?corpus_language=...` nach.
- Für normale In-App-Navigation aus dem dirty `phenomena`-Editor wird der vorhandene App-Confirm-Dialog wiederverwendet; der browsernative `beforeunload`-Prompt bleibt nur als Fallback für Reload, Tab-Close oder vergleichbare Browser-Exits.
- Der sichtbare Statuskontrast `gespeichert` vs. `ungespeichert` wird semantisch getrennt gehalten: `gespeichert` im nativen Türkis, `ungespeichert` im warmen Praxis-Ton.
- Der letzte Live-Blocker war kein weiterer Codefehler, sondern ein falscher lokaler Runtime-Prozess: auf Port 8000 lief zeitweise ein globales Python statt der Repo-`.venv`; erst nach dem expliziten `.venv`-Start war die aktuelle Overview-Terminologie auch real live sichtbar.

## Abweichungen

- Keine produktive Abweichung von der aktiven Spec nach dem Update von `docs/spec/research-access.md`.
- Während der Fehlersuche gab es eine Dev/Live-Abweichung: dieselbe lokale URL wurde zeitweise von einem falschen globalen Python-Prozess bedient und lieferte dadurch alten HTML-Stand aus. Diese Abweichung wurde im selben Run beseitigt und anschließend erneut validiert.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py tests/test_research_phenomena.py`
  - Ergebnis: `15 passed`
- Editor-Errors-Check für die final geänderten CSS-Dateien ohne Restfehler
- direkte Live-HTML-Prüfung nach Server-Neustart:
  - `Set wählen` vorhanden
  - `Phänomenliste wählen` nicht vorhanden
  - `Neues Set` vorhanden
  - neue Intro-Copy vorhanden
  - alte Intro-Copy nicht vorhanden
- vollständiger Headless-Edge-Liveflow gegen `http://127.0.0.1:8000` mit echter Login- und Set-API-Interaktion bestätigt:
  - Overview mit `Phänomene`, neuer Intro-Copy, `1 Set wählen` und `Neues Set`
  - Overview mit curated plus saved custom Sets
  - Comparison-Dropdown mit curated plus gespeichertem Custom-Set
  - Editor-Status `gespeichert` mit türkiser Badge
  - Editor-Status `ungespeichert` mit warmer Badge
  - Materiallisten und Selected-Items visuell stabil
  - Drag-Reorder der ganzen Selected-Items-Zeile
  - App-Dialog `Ungespeicherte Änderungen verwerfen?` bei In-App-Navigation

## Screenshots

- `tmp/ui-qa/phenomena-defect-close-84-final/overview-default.png`
- `tmp/ui-qa/phenomena-defect-close-84-final/overview-with-curated-custom.png`
- `tmp/ui-qa/phenomena-defect-close-84-final/comparison-dropdown-with-custom.png`
- `tmp/ui-qa/phenomena-defect-close-84-final/editor-saved.png`
- `tmp/ui-qa/phenomena-defect-close-84-final/editor-material-lists.png`
- `tmp/ui-qa/phenomena-defect-close-84-final/editor-selected-items.png`
- `tmp/ui-qa/phenomena-defect-close-84-final/editor-drag-state.png`
- `tmp/ui-qa/phenomena-defect-close-84-final/editor-unsaved.png`
- `tmp/ui-qa/phenomena-defect-close-84-final/webapp-unsaved-dialog.png`

## Offene Punkte

- Kein weiterer reproduzierbarer produktiver Defekt im angefragten `phenomena`-Abschlusslauf offen geblieben.
- Die im Test erzeugten Live-Custom-Sets bleiben in der lokalen Dev-Datenbank sichtbar, bis sie dort bewusst gelöscht werden.

## Nächste sinnvolle Schritte

- Falls gewünscht, die lokal angelegten QA-Sets wieder bereinigen.
- Falls ein weiterer Abschlusswunsch bleibt, nur noch einen kurzen manuellen Sichtcheck im nicht-headless Browser auf derselben `.venv`-Instanz ergänzen.