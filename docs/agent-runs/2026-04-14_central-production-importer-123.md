# Run Log: Central Production Importer

## Summary

- implemented the central orchestrating production importer in `scripts/research_data_intake/import_batch_to_production.py`
- added workbook parsing and validation in `scripts/research_data_intake/intake_workbook_reader.py`
- wired workbook-driven PostgreSQL upserts for `research_people`, `research_sessions`, and `research_session_exposures`
- projected runtime `metadata.json` plus `wordlist` and `text` production artifacts into `data/sessions/{language}/{session_id}/`
- updated active specs and the intake runbook to describe the new production import contract

## Key Decisions

- production import is scope-aware by `target_language`; off-scope workbook rows do not block an in-scope corpus run
- `session_id` is always derived from `person_id + recording_year + session_ref`; populated workbook `session_id` cells are ignored with a warning
- a changed derived `session_id` for an existing `(person_id, session_ref)` slot is a hard conflict unless `--allow-session-id-change` is set
- `wordlist` and `text` sync are delegated to reusable task processors; `interview` stays explicitly unimplemented

## Validation

- applied the local PostgreSQL migration chain through `0007_create_research_metadata_tables.sql`
- ran full ES dry-run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanisch_batch --target-language es --sync-tasks --dry-run`
- ran one real smoke-test import for `ES-L-0001` with task sync, verified runtime outputs and DB rows, then cleaned the smoke-test session directory and DB rows again
- ran metadata-only reimport for `ES-L-0001`
- ran `--create-missing-only` dry-run for `ES-L-0001` and confirmed exact skip behavior

## Notes

- real workbook practice currently uses uppercase `target_language` and `standard_variety` values; the importer normalizes them to canonical lowercase runtime values
- off-scope workbook rows may still be incomplete for later corpus runs and are therefore ignored by the current scope-limited validation pass
