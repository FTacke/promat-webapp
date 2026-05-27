# 2026-05-27 French prod package fix and upload

## Scope

- Work on `main` only.
- Fix failed server publish gates for upload `french_batch_20260527_initial`.
- Build corrected package with new upload id.
- Validate locally and against Linux checksum gate.
- Upload corrected package to server incoming under new id.
- Do not run promote blindly; provide a server follow-up prompt when no publish entrypoint is discoverable.

## Root causes from failed server run

From `/srv/webapps_storage/promat/data/publish_logs/promat_publish_french_batch_20260527_initial_20260527T154312Z.md`:

1. `checksums.sha256` failed raw `sha256sum -c` on Linux because CRLF introduced `\r` into filenames.
2. Package used `sessions/fr/...` while expected runtime-style contract is `sessions/french/...`.
3. Package had no `db/import_payload.json`, so DB import step did not run.

## Code fixes

### Builder and validator

Updated `scripts/research_data_intake/intake_storage.py`:

- `write_sha256_checksums(...)`
  - explicit `encoding="utf-8"`
  - explicit `newline="\n"`
- package outputs now written with LF semantics:
  - `manifest.json`
  - `checksums.sha256`
  - `reports/upload_report.md`
  - `db/import_payload.json` (if included)
- package session path uses corpus slug via language config mapping:
  - `fr -> french`
  - `en -> english`
  - `es -> spanish`
  - `de -> german`
- validator hardened:
  - rejects code-based package session dirs like `sessions/fr/...`
  - requires corpus slug form `sessions/<corpus_slug>/...`
  - verifies `manifest.json` file list against actual package files
  - verifies `checksums.sha256` UTF-8, LF-only, strict line format (`<sha256><two spaces><relative/path>`)
  - verifies checksum hashes against package file contents

### Tests

Updated `app/tests/test_research_intake_storage.py`:

- package build assertions switched to `sessions/spanish/...` for `es`.
- added regression tests for:
  - rejecting `sessions/fr/...`
  - LF-only checksum output and Linux-compatible checksum line format
  - detecting CRLF in `checksums.sha256`

Test run:

- `python -m pytest app/tests/test_research_intake_storage.py -q`
- result: `13 passed`.

## Contract and docs updates

- `docs/spec/platform-data-files.md`
  - made package path contract explicit: `sessions/{corpus_slug}/{session_id}/...`.
- `docs/runbooks/research-intake-working-pipeline.md`
  - added explicit rule that package paths use corpus slug (e.g. `sessions/french/...`).
- `scripts/research_data_intake/README.md`
  - documented the same corpus-slug package path contract.

## DB payload check

Checked realistic paths:

- found: `C:/dev/promat_data_archive/batches/french_batch_20260527/import_payload.json`
- not found:
  - `C:/dev/promat/scripts/research_data_intake/import/french_batch_20260527/import_payload.json`
  - `C:/dev/promat/scripts/research_data_intake/import/french_batch_20260527/reports/import_payload.json`

Payload sanity check:

- top-level keys: `batch_name`, `generated_at`, `persons`, `sessions`, `exposures`, `run_notes`
- no obvious secure-person fields (`email`, `first_name`, `last_name`, `secure`, consent/questionnaire file pointers).

## Corrected package build

- New upload id: `french_batch_20260527_initial_fix01`
- Build command:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/build_prod_upload_package.py --all-runtime-sessions --include-research-player-config --db-payload C:/dev/promat_data_archive/batches/french_batch_20260527/import_payload.json --upload-id french_batch_20260527_initial_fix01`

Build result:

- output dir: `scripts/research_data_intake/exports/french_batch_20260527_initial_fix01`
- files: `4416`

## Local validation

- validator command:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/validate_research_intake.py prod-package --package-dir C:/dev/promat/scripts/research_data_intake/exports/french_batch_20260527_initial_fix01`

- result: `[ok] validation passed`

Additional explicit checks (Python):

- `checksums.sha256` has no `\r`
- all checksum lines LF-terminated
- strict checksum line format passes
- all checksum hashes match files
- manifest file list matches actual package files
- no backslash/absolute package paths
- `sessions/french/...` present
- `sessions/fr/...` absent
- required French sessions `FR-L-0001..0007` present under `sessions/french/...`
- required presets present:
  - `config/research_player/english/phenomena_presets.json`
  - `config/research_player/french/phenomena_presets.json`
- `db/import_payload.json` present

WSL Linux check attempt:

- attempted `wsl ... sha256sum -c`
- not usable in this environment (`/mnt/c/...` path unavailable).

## Upload to server incoming (new id only)

- old failed incoming kept untouched:
  - `/srv/webapps_storage/promat/data/incoming/french_batch_20260527_initial/`
- new upload target:
  - `/srv/webapps_storage/promat/data/incoming/french_batch_20260527_initial_fix01/`

Transport notes:

- `rsync` unavailable on this Windows host.
- server-side `scp`/SFTP subsystem unavailable.
- used binary-safe tar-over-SSH from Python stream into remote `tar -xf -`.

Remote checks:

- root contains: `manifest.json`, `checksums.sha256`, `sessions/`, `config/`, `db/`, `reports/`
- remote file count: `4416`
- server Linux checksum gate:

`sha256sum -c checksums.sha256` -> `rc:0`

- session language dirs in uploaded package: `english`, `french`, `spanish`
- `db/import_payload.json` present on server package.

## Server publish rerun status

- No reliable, repository-tracked publish entrypoint script was discoverable in the deployed tree for direct re-run from this session.
- Therefore no blind promote command was executed.
- Provided follow-up prompt below for controlled server execution using the corrected upload id.

## Ready server follow-up prompt

Use this prompt for the server-side publish operator run:

"""
Bitte führe den serverseitigen Publish-Run für Upload-ID `french_batch_20260527_initial_fix01` aus.

Pfad:
`/srv/webapps_storage/promat/data/incoming/french_batch_20260527_initial_fix01/`

Pflicht-Gates in Reihenfolge:
1) Allowlist + Forbidden-Scan
2) JSON-Parse-Gate
3) `sha256sum -c checksums.sha256` (roh, ohne Normalisierung)
4) Sessions-Pfadvertrag: nur `sessions/<corpus_slug>/...` (insb. `sessions/french/...`, kein `sessions/fr/...`)
5) Stage nach `data/releases/{release_id}`
6) DB-Import nur wenn `db/import_payload.json` vorhanden und Importpfad/Tool verfügbar
7) atomic `data/current`-Switch
8) health/ready
9) French smoke (`/de/research/french`, `/de/research/french/design`)
10) incoming cleanup nur nach erfolgreichem Promote

Zusatzregeln:
- Kein `--delete`.
- Kein direkter Write in Live-Pfade außerhalb des Stage/Current-Vertrags.
- Altes failed incoming (`french_batch_20260527_initial`) erst nach erfolgreichem neuem Promote bewusst bereinigen oder nach Quarantine verschieben, mit Doku.
- Neues incoming (`french_batch_20260527_initial_fix01`) erst nach erfolgreichem Promote löschen.

Bitte liefere anschließend einen Publish-Report unter:
`/srv/webapps_storage/promat/data/publish_logs/promat_publish_french_batch_20260527_initial_fix01_<timestamp>.md`
"""
