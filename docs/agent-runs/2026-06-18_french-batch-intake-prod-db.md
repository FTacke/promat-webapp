# 2026-06-18 French batch intake, prod publish, DB upsert

## Scope

- Batch: `scripts/research_data_intake/import/french_batch_20260618`
- Runtime upload id: `french_batch_20260618_runtime`
- Production release: `/srv/webapps_storage/promat/data/releases/release_20260618T143628Z_french_batch_20260618_runtime`
- Current after promote: `/srv/webapps_storage/promat/data/releases/release_20260618T143628Z_french_batch_20260618_runtime`

## Intake notes

- Corrected workbook typo in ignored intake source data: `FR-L0025` to `FR-L-0025`.
- Added `_bearbeitet` as filename role alias for processed/source files.
- Accepted non-material French interview bracket literals while keeping material-reference-like unknowns as errors.
- Clamped zero-duration Amberscript words or segments to 1 ms with warnings.
- Zero-padded known material references such as `t_8` to `t_08`.
- Treated dashed silence labels such as `silent-` as silence in wordlist TextGrid import.

## Results

- Imported 31 French workbook sessions into runtime metadata.
- Produced or reused task artifacts for 21 delivered people: `FR-L-0001` through `FR-L-0007`, `FR-L-0009` through `FR-L-0021`, and `FR-N-0001`.
- Runtime package contained 3,573 files and passed local prod-package validation plus remote checksum gates.
- Production DB upsert status: applied through `/app/scripts/research_data_intake/apply_prod_db_payload.py` inside `promat-web-prod`.
- Post-apply dry-run showed the French payload as unchanged: 31 `research_people`, 31 `research_sessions`, and 14 `research_session_exposures`.
- Existing English DB payload was also applied before the French publish: 10 people, 10 sessions, and 1 exposure inserted.

## Checks

- Smoke checks after promote returned 200 for `/health`, `/ready`, `/de/research/french`, `/de/research/french/design`, `/en/research/french`, `/de/research/english`, `/de/research/spanish`, `/en/research/english`, and `/en/research/spanish`.
- No zero-byte file, WAV, TextGrid, XLSX, or Windows path was found in the promoted current release.
- Publish logging was fixed after the run to avoid Bash command substitution in Markdown JSON fences.
