# 2026-06-19 French Theatre Item Canonicalization

## Scope

- Inventoried the French wordlist item across tracked files, ignored import/runtime/export trees, filenames, MFA dictionaries, and XLSX XML contents.
- Added one French-only canonical item normalization before wordlist label validation and artifact generation.
- Added visible `canonical_item_correction` intake-plan warnings and a production-package rejection gate for stale French JSON.
- Added an idempotent DB/runtime migration with separate `--dry-run` and `--apply` modes.
- Production data was not changed in this repository run.

## Inventory

- Current French task catalog, current runtime sessions, French batch inputs, TextGrids, and XLSX workbooks already used canonical `théâtre`.
- Four ignored historical export packages contained 32 stale JSON values, all at `items[13].text`; the local file migration corrected them and their checksum files were regenerated.
- Unaccented `theatre` occurs only in external MFA dictionaries and English dictionary contexts and was intentionally left unchanged.
- No filename, MP3 path, asset key, storage key, or generated URL required migration.

## Migration Dry-runs

- Local files plus import/exports: 1,101 JSON files scanned, 32 affected files/occurrences before apply, zero asset/path changes.
- Repeated local file scan after apply: 1,101 JSON files scanned, zero affected files or occurrences.
- Local development PostgreSQL: seven `research_*` tables scanned, zero affected tables, rows, cells, or occurrences.
- Live production Dry-run remains pending until this code is deployed. The exact read-only and reviewed DB-apply commands are in `docs/runbooks/research-prod-upload-and-publish.md`.

## Validation

- Importer, working pipeline, storage/package, preset, package-gate, and migration tests passed: 116 tests.
- Existing `french_batch_20260618_runtime` production package validation passed.
- `python -m ruff check .` passed after removing one pre-existing unused import from `app/src/app/research_views.py`.
- Final tracked search found the legacy spelling only in the explicit correction rule and regression-test inputs/assertions.
