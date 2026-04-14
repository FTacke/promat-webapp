# Dummy Data Cleanup And L1 Additional 122

Datum: 2026-04-14

## Ziel

Die bestehende Dummy-/Dev-Forschungsbasis im Repo und im lokalen PostgreSQL-Workbench-Zustand entfernen und gleichzeitig `l1_additional` als reales, produktives Personenfeld in Spec, Modell und Webapp einführen.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- `app/src/app/config/data_conventions.py`
- `app/src/app/research_sessions.py`
- `app/src/app/research_views.py`
- `app/src/app/i18n.py`
- `app/templates/pages/sample_page.html`
- `app/tests/test_research_sessions.py`
- `app/tests/test_research_comparison.py`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `.gitignore`
- `data/sessions/spanish/`
- `data/example_data/`
- `data/research.db`
- lokale PostgreSQL-Tabellen `research_sets`, `research_set_items`, `research_set_workbench_state`, `research_set_workbench_sessions`

## Wichtige Entscheidungen

- `l1_additional` bleibt ein eigenes Personenfeld und wird nicht in `additional_languages` überführt.
- Für `l1`, `l1_additional`, `mother_l1` und `father_l1` gilt nun dieselbe zentrale Uppercase-Normalisierung gegen die kanonische `l1_code`-Werteliste.
- Mehrfachwerte in `l1_additional` werden produktiv als semikolon-separierte Codes oder als Liste eingelesen und im Modell dedupliziert als geordnete Tupel geführt.
- Die Vergleichs-Workbench bekommt `l1_additional` zusätzlich im Session-Katalog-JSON, damit strukturierte Client-Payloads nicht hinter der Profilansicht zurückbleiben.
- Repo-getrackte Dummy-Sessions, Example-Fixtures und der alte lokale `data/research.db`-Platzhalter wurden vollständig entfernt; die nächste produktive Befüllung von `data/sessions/` ist dem zentralen orchestrierenden Import vorbehalten.
- Der lokale PostgreSQL-Workbench-Zustand wurde vollständig geleert, weil die vorhandenen Sets und Session-Selektionen auf den Dummy-Korpuszustand verwiesen.

## Abweichungen

- Keine Abweichung von den aktiven Specs.
- Die alte manuelle Dev-Seed-Strecke für spanische Beispiel-Sessions wurde zusammen mit ihrer Runbook-Dokumentation entfernt, um ein erneutes Einschleusen von Dummy-Forschungsdaten zu vermeiden.

## Verifikation

- Sprachserver-Fehlerprüfung auf allen geänderten Python-Test- und Anwendungsdateien ohne Befund.
- Repo-Datenbereinigung verifiziert: unter `data/sessions/spanish/` bleibt nur `.gitkeep`, `data/example_data/` ist entfernt, `data/research.db` ist entfernt.
- Lokale PostgreSQL-Bereinigung verifiziert:
  - vorher `research_set_workbench_sessions=79`, `research_set_items=13731`, `research_set_workbench_state=149`, `research_sets=149`
  - nachher alle vier Tabellen `=0`

## Offene Punkte

- Der zentrale orchestrierende Produktionsimport für reale Forschungsdaten ist weiterhin der nächste separate Arbeitsschritt.
- Historische QA-Artefakte unter `tmp/` können weiterhin alte Dummy-Referenzen enthalten; sie sind keine aktive Laufzeitquelle, wurden in diesem Run aber nicht global bereinigt.

## Nächste sinnvolle Schritte

1. Den zentralen orchestrierenden Produktionsimport auf Basis der nun bereinigten Runtime-Struktur entwerfen und implementieren.
2. Dabei `l1_additional` direkt in den Importpfad aus Workbook/Intake in `metadata.json` übernehmen.
3. Nach dem ersten Realdaten-Import die betroffenen Research-Seiten und die Comparison-Workbench mit echten Sessions erneut browserseitig prüfen.