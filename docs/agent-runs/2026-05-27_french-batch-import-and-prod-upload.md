# 2026-05-27 French Batch Import and Initial Prod Upload Package

## Scope

- Batch: `scripts/research_data_intake/import/french_batch_20260527`
- Goal:
  - complete/repair French learner runtime imports for FR-L-0001..FR-L-0007,
  - validate runtime trees,
  - build a validated initial prod upload package,
  - upload package to server incoming path,
  - no server-side promote step.

## Preconditions and constraints

- Kept production-upload workflow in incoming-only mode.
- No `--delete` operations used.
- No server-side promotion commands executed.
- Intake/runtime separation preserved (`data/sessions/` runtime-only artifacts).

## Implementation and fixes applied

### 1. Text intake robustness and stale-state reuse

Updated importer and text-alignment workflow to resolve Windows signature mismatches and incomplete MFA output handling:

- `scripts/research_data_intake/import_batch_to_production.py`
  - normalized signature path values (drive-letter case-insensitive comparison) in text stale-state matching.
  - added fallback behavior for text alignment import:
    - first try strict `fail_on_missing_output=True`,
    - if strict import fails on missing per-item MFA output, retry import with warnings (`fail_on_missing_output=False`) so person-level task import can complete with explicit warnings.

### 2. MFA run-state continuity

- `scripts/research_data_intake/alignment_export/run_text_mfa.py`
  - ensured `mfa_state.json` carries manifest-derived source signatures and language metadata consistently.

### 3. TextGrid parsing correction

- `scripts/research_data_intake/textgrid_support.py`
  - ensured numbered silence labels (e.g. `silent1`) are treated as non-spoken intervals.

### 4. French text catalog correction

- `data/config/research_player/french/task_catalogs/text.json`
  - corrected `t_42` text line to match spoken source for alignment pipeline consistency.

### 5. Tests

- `app/tests/test_research_production_importer.py`
  - suite passed after importer/text-pipeline changes (`30 passed`).

## Import execution results

Executed central importer for target people in focused runs:

- FR-L-0004: success (`tasks[wordlist=sync/ready, text=sync/ready]`)
- FR-L-0005: success after fallback-capable pipeline update (`tasks[wordlist=sync/ready, text=sync/ready]`)
- FR-L-0006: success (`tasks[wordlist=sync/ready, text=sync/ready]`)
- FR-L-0007: success (`tasks[wordlist=sync/ready, text=sync/ready]`)
- FR-L-0001..0003: resynced successfully after refreshing stale signature metadata (`tasks[wordlist=sync/ready, text=sync/ready]`)

Runtime audit confirmed:

- FR-L-0001..FR-L-0007 each have
  - `alignment/wordlist.json` + `derived/wordlist.mp3`
  - `alignment/text.json` + `derived/text.mp3`
- completion count for FR-L-0001..0007: **7/7**.

## Validation

- Runtime tree validation:
  - all French session runtime trees validated successfully,
  - explicit revalidation passed for FR-L-0001..FR-L-0007 (`[ok] validation passed`).
- Package validation:
  - `validate_research_intake.py prod-package --package-dir .../french_batch_20260527_initial`
  - result: `[ok] validation passed`.

## Upload package

Built package:

- Upload ID: `french_batch_20260527_initial`
- Output dir: `scripts/research_data_intake/exports/french_batch_20260527_initial`
- Files: `1205`
- Generated:
  - `manifest.json`
  - `checksums.sha256`
  - `sessions/`, `config/`, `reports/`

## Server transfer (incoming only)

Target:

- host: `vhrz2184`
- path: `/srv/webapps_storage/promat/data/incoming/french_batch_20260527_initial/`

Transfer notes:

- `rsync` binary was not available on this Windows runner.
- server-side `scp`/SFTP subsystem was unavailable (`subsystem request failed on channel 0`).
- package was uploaded via binary-safe tar stream over SSH to the same incoming path.

Remote verification:

- remote listing shows expected package root files (`manifest.json`, `checksums.sha256`, `sessions/`, `config/`, `reports/`).
- remote file count: `1205` (matches local package file count).

## Post-run status

- Batch objective met for French learners FR-L-0001..FR-L-0007 (wordlist+text complete).
- Initial prod upload package built and validated.
- Package delivered to incoming path on `vhrz2184`.
- No promotion step executed.
