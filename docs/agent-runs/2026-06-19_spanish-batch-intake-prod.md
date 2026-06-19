# 2026-06-19 Spanish batch intake and production publish

## Scope

- Batch: `scripts/research_data_intake/import/spanish_batch_20260619`
- Target language: `es`
- Runtime corpus slug: `spanish`
- Upload ID: `spanish_batch_20260619_runtime`

## Intake findings

- Scanner recognized the batch workbook and all delivered WAV, TextGrid, and JSON files without filename-classification warnings.
- Workbook scope contains 28 Spanish sessions.
- 24 sessions have delivered task data and are publishable.
- 4 sessions are metadata-only and are skipped with `reason=no_delivered_task_data`: `ES-L-0020-2026-S01` through `ES-L-0023-2026-S01`.
- Native speakers `ES-N-0001` through `ES-N-0005` correctly have `wordlist` and `text`; `interview` is `not_expected_for_native_speaker`.

## Code and spec adjustments

- `[]` inside interview tokens is now accepted as a non-material phonetic omission marker and stays literal token text.
- Wordlist TextGrid parsing now uses the shared TextGrid reader so UTF-16 and UTF-8 exports are both accepted.
- The production importer no longer aborts an entire batch solely because the working organizer reports an isolated task-level error; publishability is still determined from actual delivered task data.
- `docs/spec/platform-data-files.md` was updated for the `[]` marker and TextGrid encoding tolerance.

## Local validation

- Working tree prepared 24 people and 72 tasks with zero warnings/errors after the marker fix.
- Text MFA used the shared cache at `scripts/research_data_intake/.mfa_cache/shared/es/`; after the first Docker-backed ensure step, later runs reused the cache.
- Runtime validation found 24 `data/sessions/spanish/{session_id}` directories, no forbidden WAV/TextGrid/XLSX/working/MFA artifacts in session trees, no zero-byte session files, and no local Windows paths in Runtime JSON.
- Archive payload: `persons=24`, `sessions=24`, `exposures=6`; no empty `documented_tasks`; no metadata-only sessions.
- Prod package validation passed for `scripts/research_data_intake/exports/spanish_batch_20260619_runtime`.

## Tests

- `python -m pytest app/tests/test_research_production_importer.py app/tests/test_research_prod_db_payload.py app/tests/test_research_prod_publish.py app/tests/test_research_working_tree_intake.py`
- `python -m ruff check .`

## Status

- Local intake and package build are complete.
- Upload, publish with DB upsert, production smoke checks, DB count checks, and release retention checks are performed after this log entry.
