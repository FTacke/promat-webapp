# Bilinguale UI-Abnahme, Abschluss-Run der ersten produktiven Welle

Datum: 2026-04-11

## Ziel

Die bilinguale UI-Grundlage und die erste produktive `de`/`en`-Welle für Shared Shell, `phenomena`, `comparison` und `player` auf der real laufenden App-Instanz in beiden Sprachen browserseitig abnehmen, sichtbare Defekte iterativ beheben, Screenshots erzeugen und die gewonnenen Abnahmeregeln dauerhaft in Governance, Spec und Runbook verankern.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- Root `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- `app/scripts/create_initial_admin.py`
- `app/src/app/routes/public.py`
- `app/src/app/routes/auth.py`
- `app/src/app/routes/research_api.py`

## Geänderte Bereiche

- Live-Abnahme und Defektkorrekturen in `app/src/app/routes/public_content.py`, `app/src/app/research_views.py`, `app/src/app/i18n.py`
- Dauerhafte Governance-Schärfung in `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`, `.github/instructions/repo.instructions.md`
- Aktive UI-Regeln in `docs/spec/platform-data-files.md`
- Wiederholbaren UI-Abnahmeablauf in `docs/runbooks/ui-change-workflow.md`
- Screenshot- und QA-Artefakte unter `tmp/ui-qa/2026-04-11-bilingual-acceptance-90/`

## Wichtige Entscheidungen

- Die UI-Abnahme für fertige bilinguale Oberflächen gilt erst nach realem Browser-Pass auf denselben produktiven Routen in `de` und `en` als abgeschlossen; Tests bleiben unterstützend, aber nicht abnahmetragend.
- Shell-nahe Forschungswurzelseiten zählen zur sichtbaren Abnahmefläche der ersten Welle und mussten im selben Run sprachlich mitgezogen werden, statt den Scope künstlich nur auf engere Workbench-Komponenten zu begrenzen.
- Sichtbare technische Werte wie rohe `set_id`-UUIDs oder interne Handoff-Vokabeln werden auf produktiven Oberflächen nicht nur übersetzt, sondern entfernt oder in nutzerorientierte Sprache überführt.
- Wiederkehrende Abnahmeerkenntnisse wurden nicht im Run-Log belassen, sondern in Governance, aktiver Spec und Runbook normativ verdichtet.

## Abweichungen

- Keine Abweichung bei Routing, Runtime-Grenzen, Datenräumen oder aktiven Plattformregeln.
- Für die Browser-Abnahme wurden ein lokaler Admin und temporäre QA-Sets angelegt; diese dienten nur der Verifikation auf der realen Dev-Instanz.
- Temporäre Hilfsartefakte und Screenshots liegen ausschließlich unter `tmp/ui-qa/2026-04-11-bilingual-acceptance-90/` und bilden keine aktive Dokumentation.

## Verifikation

- Python-Umgebung und Selenium-Verfügbarkeit auf der Workspace-`.venv` geprüft
- Stale Fremdprozess auf Port `8000` entfernt und kanonischen Dev-Stack über `scripts/dev-start.ps1` gestartet
- Health-Check auf `http://127.0.0.1:8000/health` erfolgreich
- Lokalen Admin für die reale Browser-Abnahme angelegt bzw. aktualisiert
- Headless-Edge/Selenium-Abnahme gegen reale Routen in `de` und `en` durchgeführt für:
  - Shared Shell
  - `phenomena` Overview und Editor
  - `comparison`
  - `player`
- Zusätzlich gezielt mitvalidiert:
  - lokalisierte Confirm- und Delete-Dialoge
  - lokalisierter Empty State im Player
  - Bereich mit längeren englischen Labels im Player-Vergleich
- Erste Screenshot-Runde nutzte Defektfindung, danach wurden die gefundenen sichtbaren Mängel behoben und der gesamte Lauf auf dem finalen Code-Stand erneut ausgeführt
- Finaler Screenshot-Satz unter `tmp/ui-qa/2026-04-11-bilingual-acceptance-90/`, unter anderem:
  - `shell_de.png`, `shell_en.png`
  - `phenomena_overview_de_auth.png`, `phenomena_overview_en_auth.png`
  - `phenomena_editor_de.png`, `phenomena_editor_en.png`
  - `phenomena_editor_confirm_de.png`, `phenomena_editor_confirm_en.png`
  - `phenomena_overview_delete_dialog_de.png`, `phenomena_overview_delete_dialog_en.png`
  - `comparison_de_auth.png`, `comparison_en_auth.png`
  - `player_de.png`, `player_en.png`, `player_en_compare.png`
  - `player_empty_de.png`, `player_empty_en.png`
- Übersetzungsschlüssel-Parität per AST-Audit von `app/src/app/i18n.py` geprüft:
  - `de`: 272 Keys
  - `en`: 272 Keys
  - keine fehlenden Keys auf beiden Seiten
- Fokussierter Code-Scan für First-Wave-Flächen auf verbleibende sichtbare Hardcodings in Python, Templates und Page-JS; verbleibende in-scope Label-Helfer wurden in denselben Run in den zentralen Katalog überführt

## Offene Punkte

- Außerhalb der ersten produktiven Welle enthalten weitere Forschungsflächen wie `speakers`, `recordings` und Teile der Profilhilfen weiterhin ältere sichtbare Sprachlogik; sie waren nicht Teil dieser Abschluss-Abnahme.
- Der Screenshot-Run beweist die saubere erste Welle, ersetzt aber keine spätere Erweiterung der bilingualen Produktoberflächen auf die restlichen Forschungsmodule.
- Die temporären QA-Sets bleiben nur Hilfsmittel dieses Abnahmelaufs; spätere Runs sollten bei Bedarf frische QA-Daten anlegen statt diese Artefakte als Produktzustand zu behandeln.

## Nächste sinnvolle Schritte

- Die nächste bilinguale UI-Welle auf `recordings`, `speakers` und Profilflächen ausdehnen und denselben zweisprachigen Browser-Abnahmeprozess anwenden.
- Verbleibende ältere sichtbare `ui_lang`-Verzweigungen in den noch nicht migrierten Forschungsbereichen schrittweise in den zentralen Übersetzungskatalog überführen.
- Den bestehenden Selenium-Abnahmeskriptpfad unter `tmp/ui-qa/` als Vorlage für künftige reale UI-Abschlussläufe wiederverwenden und bei Scope-Erweiterungen mitziehen.