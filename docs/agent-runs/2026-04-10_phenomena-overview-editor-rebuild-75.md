# Phänomene Overview/Editor Rebuild

Datum: 2026-04-10

## Ziel

Die bestehende einteilige `phenomena`-Seite in eine ruhige Übersichtsseite plus separate Bearbeitungs-Unterseiten aufteilen und den owner-bound Set-Workflow dafür anpassen.

## Consulted Sources

- `docs/plans/phenomena_plan.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- `app/src/app/research_sets.py`
- `app/src/app/routes/research_api.py`
- `app/src/app/routes/public.py`
- `app/src/app/research_phenomena_views.py`
- `app/templates/pages/research_phenomena_overview.html`
- `app/templates/pages/research_phenomena_editor.html`
- `app/static/js/pages/research-phenomena-overview.js`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/migrations/0004_extend_research_sets_for_phenomena_editor.sql`
- `app/tests/test_research_sets.py`
- `app/tests/test_research_phenomena.py`
- `docs/spec/research-access.md`
- `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- `phenomena` ist produktiv nicht mehr ein kombiniertes Preset-/Workspace-Surface, sondern getrennt in Overview und Editor.
- Für kuratierte Listen gibt es eine öffentliche Editor-Ansicht auf Preset-Basis; owner-bound Persistenz entsteht erst beim Speichern oder beim expliziten Modifizieren.
- Für gespeicherte oder verworfene Arbeitsstände bleibt das bestehende `research_sets`-Modell die einzige Persistenzbasis; es wurde erweitert statt ersetzt.
- Set-Titel werden für neue und preset-abgeleitete Drafts lesbar automatisch vergeben (`Neues Set n`, `Titel (modifiziert)`).
- Die produktive Editor-Oberfläche verwendet einen einzigen sichtbaren Speichern-Flow über `POST`/`PATCH`/`PUT` in der bestehenden `/api/research/sets`-Familie; sichtbares `Speichern als` entfällt.

## Abweichungen

- Keine bekannte Abweichung von der aktiven Spezifikation nach Aktualisierung der Specs in diesem Run.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sets.py app/tests/test_research_phenomena.py`
- statische Fehlerprüfung der geänderten Python-, JS-, CSS- und Template-Dateien via Editor-Problems-Check

## Offene Punkte

- Es gibt noch keine Browser-End-to-End-Validierung für die neuen Editor-Interaktionen wie Rename/Delete-Dialoge, Dirty-State-Warnung und Drag-and-drop-Reihenfolge.
- Der alte `research-phenomena.js`-Bestand ist aktuell ungenutzt; funktional ist er abgelöst, aber noch nicht entfernt.

## Nächste sinnvolle Schritte

- Den neuen `phenomena`-Flow einmal manuell im laufenden Dev-Server durchspielen: neue Liste, curated öffnen, curated modifizieren, speichern, umbenennen, löschen.
- Falls stabil, den ungenutzten Altbestand der früheren einteiligen `phenomena`-Implementierung bereinigen.