# 2026-05-27 English and Spanish prod upload, publish, and validation

## Scope

- Work on main only.
- Promote already integrated English and Spanish runtime data plus current `data/config/research_player/` with the hardened flow.
- Keep publish contract: incoming -> releases/<release_id> -> current.
- No direct writes to live paths, no delete-based sync, no new import/MFA reruns.
- Document DB import decision explicitly.

## Inputs and package

- upload id: `promat_upload_20260527T175242Z_english_spanish_runtime`
- local package: `scripts/research_data_intake/exports/promat_upload_20260527T175242Z_english_spanish_runtime`
- package file count: `4415`
- uploaded incoming path: `/srv/webapps_storage/promat/data/incoming/promat_upload_20260527T175242Z_english_spanish_runtime/`

## Local gates already completed before publish

- runtime/session audit completed for English and Spanish runtime trees.
- config integrity checks completed for `data/config/research_player/` references.
- payload parse and sensitive-key-name checks completed.
- package validator passed:
  - `python scripts/research_data_intake/validate_research_intake.py prod-package ...`
- focused tests passed:
  - `app/tests/test_research_presets.py` -> `15 passed`
  - `app/tests/test_research_intake_storage.py` -> `13 passed`
  - `app/tests/test_upload_prod_package.py` -> `6 passed`

## Server incoming gates (Part H)

Checked on server against `/srv/webapps_storage/promat/data/incoming/promat_upload_20260527T175242Z_english_spanish_runtime`:

1. allowlist/structure gate passed
   - root entries: `checksums.sha256`, `config`, `manifest.json`, `reports`, `sessions`
2. forbidden scan passed
   - no `secure/raw/source` tree fragments
   - no forbidden payload extensions (`*.wav`, `*.TextGrid`, `*.xlsx`, `*.pdf`)
3. JSON parse gate passed
   - `JSON_PARSE_OK 143`
4. checksum gate passed
   - `sha256sum -c checksums.sha256` returned success on Linux
5. sessions path contract passed
   - no code dirs (`sessions/en`, `sessions/es`, `sessions/fr`, `sessions/de`)

## Stage, promote, and current switch

- previous current:
  - `/srv/webapps_storage/promat/data/releases/release_20260527T172020Z_french_batch_20260527_initial_fix01`
- staged release:
  - `/srv/webapps_storage/promat/data/releases/release_20260527T175805Z_promat_upload_20260527T175242Z_english_spanish_runtime`
- method:
  - `rsync -a current/ -> stage/`
  - `rsync -a incoming/ -> stage/`
  - no `--delete`
- atomic switch:
  - `ln -sfn <stage> /srv/webapps_storage/promat/data/current`
- current now points to:
  - `/srv/webapps_storage/promat/data/releases/release_20260527T175805Z_promat_upload_20260527T175242Z_english_spanish_runtime`

## DB payload and upsert decision

- release contains `db/import_payload.json`.
- DB upsert/import was intentionally skipped in this run.
- reason: no approved production DB importer entrypoint was available in-scope for this hardened publish run; keeping runtime publish and DB upsert decoupled was required.

## Post-promote validation

- host-local (from production host):
  - `http://127.0.0.1:8000/health` -> `200`
  - `http://127.0.0.1:8000/ready` -> `200`
- public:
  - `https://pronunciation-matters.de/health` -> `200`
  - `https://pronunciation-matters.de/ready` -> `200`
- smoke routes:
  - `https://pronunciation-matters.de/de/research/english` -> `200`
  - `https://pronunciation-matters.de/de/research/english/design` -> `200`
  - `https://pronunciation-matters.de/de/research/spanish` -> `200`
  - `https://pronunciation-matters.de/de/research/spanish/design` -> `200`

Note:

- local workstation requests to `http://127.0.0.1:8000/{health,ready}` timed out (expected from non-host context), so host-local checks were executed over SSH on the production server.

## Cleanup

- incoming directory removed after successful promote and checks:
  - `/srv/webapps_storage/promat/data/incoming/promat_upload_20260527T175242Z_english_spanish_runtime`

## Server publish log artifact

- written to:
  - `/srv/webapps_storage/promat/data/publish_logs/promat_publish_promat_upload_20260527T175242Z_english_spanish_runtime_20260527T180041Z.md`
