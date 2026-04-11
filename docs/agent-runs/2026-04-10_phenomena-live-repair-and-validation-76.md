# Phänomene Live Repair And Validation

Datum: 2026-04-10

## Ziel

Den bereits umgebauten split `phenomena`-Flow gegen die echte lokale Dev-PostgreSQL-Instanz reparieren, globale Form-Control-Regressions im Live-UI bereinigen und den vollständigen Browserflow mit Screenshots verifizieren.

## Consulted Sources

- `docs/plans/phenomena_plan.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `app/scripts/dev-start.ps1`
- `app/scripts/dev-setup.ps1`
- `app/scripts/apply_auth_migration.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`

## Geänderte Bereiche

- `app/scripts/apply_auth_migration.py`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/static/js/pages/research-phenomena-overview.js`
- `app/tests/test_research_sets.py`

## Root Causes

- Die lokale Dev-Bootstrap-Kette führte `0004_extend_research_sets_for_phenomena_editor.sql` nicht aus, weil `app/scripts/apply_auth_migration.py` nur die fest verdrahteten Dateien `0001` bis `0003` anwandte.
- Dadurch fehlte live in PostgreSQL die Spalte `research_sets.note`; der owner-bound Set-Create/Patch-Pfad lief damit gegen Schema-Drift.
- Die neuen Phänomene-Form-Controls verwendeten effektiv eine 4px-Radius-/transparente Darstellung und ließen Vergleichs-Filter und Editor-Felder deutlich eckiger wirken als die bestehende UI-Sprache.
- Der Editor initialisierte den Dirty-State-Baseline-Snapshot zu früh; bereits gespeicherte Sets landeten deshalb visuell sofort in `ungespeichert`.
- Rename/Delete im Overview waren clientseitig defekt, weil die Dialoge im Template außerhalb von `data-phenomena-overview-root` liegen, das JS aber per `root.querySelector(...)` suchte und dadurch `null`-Referenzen band.

## Umsetzung

- Den Postgres-Migrationsrunner auf eine geordnete Discovery aller nummerierten PostgreSQL-SQL-Dateien unter `app/migrations/` umgestellt; `_sqlite.sql` wird explizit ausgeschlossen.
- Die aktualisierte Migrationskette direkt gegen die echte lokale Dev-DB ausgeführt; `research_sets.note` wurde live nachgezogen.
- Den realen DB-Schreibpfad mit derselben lokalen Dev-DB geprüft: Draft anlegen, Items schreiben, speichern, laden, löschen.
- Die Phänomene-/Comparison-Formfelder visuell auf die weichere, hinterlegte Systemform zurückgeführt und Focus-States ergänzt.
- Den Editor-Dirty-State auf nachgelagerten Baseline-Aufbau korrigiert und doppelte kuratierte Hinweis-Texte bereinigt.
- Rename/Delete im Overview repariert, indem Dialog- und Formularreferenzen dokumentweit statt root-lokal gebunden werden.
- Einen Regressionstest ergänzt, der die vollständige PostgreSQL-Migrationskette inklusive `0004` absichert.

## Live-Verifikation

- Reale lokale PostgreSQL-Inspektion vor dem Fix: `research_sets.note` fehlte.
- Reale lokale PostgreSQL-Inspektion nach dem Fix: `research_sets.note` vorhanden.
- Service-Livecheck gegen die echte Dev-DB erfolgreich:
  - Draft create
  - Item replace
  - Metadata patch mit `note` und `state=saved`
  - Load
  - Delete
- Browser-Livecheck per headless Selenium gegen `http://127.0.0.1:8000` erfolgreich für:
  - anonyme `phenomena`-Overview
  - anonymer Preset-Editor
  - `comparison`-Filteroberfläche
  - Owner-Login
  - neue Liste anlegen
  - Item auswählen
  - speichern
  - Overview-Overflow öffnen
  - Umbenennen-Dialog
  - Rename abschließen
  - Löschdialog
  - Delete abschließen

## Screenshots

- `tmp/ui-qa/phenomena-repair-76/overview-anon-after-fix.png`
- `tmp/ui-qa/phenomena-repair-76/comparison-after-fix.png`
- `tmp/ui-qa/phenomena-repair-76/editor-preset-public-after-fix.png`
- `tmp/ui-qa/phenomena-repair-76/editor-new-empty.png`
- `tmp/ui-qa/phenomena-repair-76/editor-new-selected-unsaved.png`
- `tmp/ui-qa/phenomena-repair-76/editor-new-selected-saved.png`
- `tmp/ui-qa/phenomena-repair-76/overview-custom-overflow.png`
- `tmp/ui-qa/phenomena-repair-76/overview-rename-dialog.png`
- `tmp/ui-qa/phenomena-repair-76/overview-delete-dialog.png`
- `tmp/ui-qa/phenomena-repair-76/overview-after-delete.png`

## Tests

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sets.py tests/test_research_phenomena.py`
- Ergebnis: `25 passed`

## Offene Punkte

- Kein weiterer produktiver Backend- oder Browser-Blocker im reparierten `phenomena`-Flow gefunden.
- Die Screenshot-Artefakte liegen bewusst unter `tmp/ui-qa/` und sind keine normative Dokumentation.