# Research Intake Target Model Implementation

Datum: 2026-05-25

## Ziel

Das neue PROMAT-Research-Intake-Zielmodell systematisch umsetzen und absichern: Drop-in-Batches ohne manuelle `processed/`-, `raw/`- oder `intake_data/`-Pflicht, Runtime-only `data/sessions/`, externes session-zentriertes Archiv unter `PROMAT_LOCAL_ARCHIVE_ROOT`, explizite allowlist-basierte Prod-Upload-Pakete sowie konsistente Doku-, Runbook- und Governance-Regeln.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/intake-workbook.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `docs/runbooks/research-wordlist-production.md`
- `scripts/research_data_intake/README.md`
- `AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `.github/copilot-instructions.md`
- `app/.env.example`

## Geaenderte Bereiche

- `docs/spec/platform-data-files.md`
- `scripts/research_data_intake/README.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `docs/runbooks/research-wordlist-production.md`
- `app/.env.example`
- `AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `.github/copilot-instructions.md`
- `scripts/research_data_intake/import_batch_to_production.py`
- `app/tests/test_research_raw_sync_importer.py`

## Wichtige Entscheidungen

- `data/sessions/` bleibt strikt Runtime-only und enthaelt nur `metadata.json`, `alignment/*.json`, `derived/*.mp3` und `items/**/*.mp3`.
- WAV-, TextGrid-, XLSX-, `secure/`-, `raw/`, `origin/`, `source/`- und MFA-Artefakte gehoeren nicht in Runtime und nicht in Prod-Upload-Pakete.
- Das lokale Langzeitarchiv ist extern unter `PROMAT_LOCAL_ARCHIVE_ROOT` und session-zentriert unter `sessions/{lang}/{session_id}/...`.
- Prod-Uploads sind explizite allowlist-basierte Exporte aus validierten Runtime-Artefakten plus optionalem `db/import_payload.json`; Auslassung im Paket loescht nie implizit Prod-Daten.
- Research-Intake-Runs greifen nicht in `content/`, `content/teaching/` oder `public/teaching/` ein.
- Das Import-CLI behaelt den obsoleten `--sync-raw-only`-Fehlerpfad intern, zeigt die Option aber nicht mehr als aktive Help-Oberflaeche an.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_working_tree_intake.py app/tests/test_research_intake_storage.py app/tests/test_research_production_importer.py app/tests/test_research_raw_sync_importer.py -q`
  - Ergebnis: `41 passed in 1.46s`
- Help-Checks erfolgreich fuer:
  - `scripts/research_data_intake/scan_import_batch.py --help`
  - `scripts/research_data_intake/validate_research_intake.py --help`
  - `scripts/research_data_intake/import_batch_to_production.py --help`
  - `scripts/research_data_intake/build_prod_upload_package.py --help`
  - `scripts/research_data_intake/reset_dev_research_runtime.py --help`
- Fuer die env-abhaengigen CLIs wurden `PROMAT_RUNTIME_ROOT`, `PROMAT_PUBLIC_ROOT` und `PROMAT_LOCAL_ARCHIVE_ROOT` lokal gesetzt, damit die Help-Ausgabe die reale Dev-Laufzeit spiegelt.

## Offene Punkte

- Es wurde kein realer Batch gegen ein echtes lokales Archiv oder eine echte Dev-DB importiert; dieser Run blieb absichtlich bei Code-, Doku- und fokussierter Testvalidierung.
- Historische Agent-Run-Logs und Planungsdokumente koennen weiterhin alte Aussagen enthalten, bleiben aber nicht normativ.

## Naechste sinnvolle Schritte

- Mit einem echten ES- oder EN-Batch einen End-to-End-Dry-Run gegen das externe Archiv durchfuehren.
- Danach ein explizites Upload-Paket erzeugen und gegen die spaetere Server-Incoming-Struktur pruefen.