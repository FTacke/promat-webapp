# Phänomene-Set-Editor: JS-Stabilisierung und Item-Auswahl

Datum: 2026-05-28

## Ziel

Die akute Regression im Phänomene-Set-Editor beheben: Items aus Wortliste/Text sollten wieder auswählbar sein,
die Editor-JS-Datei sollte strukturell konsistent ausführbar sein, und die Button-Matrix für User/Admin/Custom/Curated
sollte weiter gelten.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `docs/agent-runs/AGENTS.md`
- `docs/agent-runs/_template.md`
- `docs/agent-runs/2026-05-28_phenomena-editor-button-matrix-fix.md`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/templates/pages/research_phenomena_editor.html`
- `app/tests/test_research_phenomena.py`

## Geänderte Bereiche

- `app/static/js/pages/research-phenomena-editor.js`
  - auf die letzte intakte Struktur zurückgeführt und die Button-Matrix sauber neu eingetragen
  - `parseState()` bereinigt: nur State-Parsing, keine Event-Fragmente
  - `requestJson()` wieder als eigene Top-Level-Funktion hergestellt
  - `syncStatus()` genau einmal vorhanden
  - `discardOrDelete()` vollständig durch `discardOrNavigate()` plus `performDeleteCustom()` ersetzt
  - `renderSourceList()`, `toggleSelection()`, Root-Click-Delegation und Drag/Reorder wieder vollständig im `init()`-Kontext
- `app/tests/test_research_phenomena.py`
  - statische Regressionstests für die JS-Struktur ergänzt
  - Template-Test gegen verschachtelte Buttons und altes Curated-Toggle-Datenattribut ergänzt
- `tmp/ui-qa/2026-05-28-phenomena-editor-stability/`
  - nicht-normative Browser-QA-Artefakte und temporärer lokaler Server-Helper

## Wichtige Entscheidungen

- Die kaputt gemergte Datei wurde nicht weiter lokal geflickt, sondern aus der letzten intakten JS-Struktur
  rekonstruiert und nur mit der gewünschten Button-Matrix ergänzt.
- Custom-Löschen ist ein eigener `[data-phenomena-delete-action]`-Flow; der Discard-Button verwirft/navigiert nur.
- Die Admin-Buttons bleiben im Template vorhanden, werden aber clientseitig gemäß Rolle und Set-Zustand verborgen;
  Server-seitige Admin-Endpunkte bleiben die eigentliche Sicherheitsgrenze.

## Ursache

Der letzte Commit hatte Merge-Fragmente mitten in die JS-Datei geschrieben:

- Event-Listener standen nach `return` in `parseState()`.
- Der Kopf von `requestJson()` fehlte, während der Funktionskörper stehen blieb.
- `syncStatus()` existierte doppelt.
- `renderSourceList()` war teilweise durch ein zweites `syncStatus()` ersetzt.
- `discardOrNavigate()` und `performDeleteCustom()` lagen verschachtelt im `noteInput`-/Dragstart-Bereich.
- Dadurch wurden die Source-Item-Buttons zwar gerendert, aber die Click-Delegation und Teile der Renderlogik waren nicht mehr zuverlässig ausführbar.

## Button-Matrix

- User: keine Admin-Curated-Aktionen sichtbar, kein Curated-Löschen, kein Save-as-curated, kein Curated-Update.
- Admin + Custom/Draft: Save-as-curated sichtbar, Curated-Löschen verborgen, Custom-Speichern/Löschen zustandsabhängig.
- Admin + Curated: Curated-Löschen und Curated-Update sichtbar, Save-as-curated und Custom-Löschen verborgen,
  Discard-Label als Änderungen-verwerfen-Variante.
- Custom-Kopie aus Curated: bleibt Custom; Curated-Löschen verborgen; Admin sieht Save-as-curated, User nicht.

## Verifikation

- `node --check app/static/js/pages/research-phenomena-editor.js`
- `.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q`
- `.venv/Scripts/python.exe -m pytest app/tests/test_research_sets.py -q`
- `.venv/Scripts/python.exe -m ruff check .`
- aus `app/`: `../.venv/Scripts/python.exe -m ruff check .`
- `.venv/Scripts/python.exe scripts/ci_governance_checks.py`
- `.venv/Scripts/python.exe -m compileall -q app/src app/tests`

## Browser-QA

Headless Chromium gegen einen separaten lokalen Server auf `http://127.0.0.1:8015` mit lokaler Dev-Postgres-DB:

- Normaler QA-User: neues Set geöffnet, Item ausgewählt, Marker/Selected-Liste/Save-Button geprüft, Item entfernt,
  Bulk-Auswahl und Drag/Reorder geprüft.
- Normaler QA-User: kuratiertes Set geöffnet; Admin-Aktionen verborgen.
- Admin: neues Custom-Set geöffnet; Save-as-curated sichtbar, Curated-Löschen verborgen; Item-Auswahl, Bulk und Drag/Reorder geprüft.
- Admin: kuratiertes Set geöffnet; Curated-Löschen und Curated-Update sichtbar, Save-as-curated und Custom-Löschen verborgen;
  Item-Abwahl geprüft.
- Admin: Custom-Kopie aus Curated geöffnet; bleibt Custom, Curated-Löschen verborgen, Save-as-curated sichtbar; Item-Abwahl geprüft.
- Console-Errors: keine.

## Abweichungen

Keine Abweichung von aktiven Specs oder Dev/Prod-Parität. Keine Server- oder DB-Migration erforderlich.
Für die Browser-QA wurde nur ein lokaler QA-User in der Dev-Datenbank angelegt und der Dev-Admin idempotent zurückgesetzt.

## Offene Punkte

Keine bekannten offenen Punkte für diese Regression.

## Nächste sinnvolle Schritte

- Nach Push CI beobachten und bei Abweichungen gezielt nacharbeiten.
