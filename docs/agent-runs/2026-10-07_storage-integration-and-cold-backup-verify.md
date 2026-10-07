# Storage Integration, Cold Backup Verification and Supplemental Backup — 2026-10-07

Non-normative run report. Binding rules: `docs/spec/platform-data-files.md`, section "Storage Roots". Earlier evidence, unchanged: `2026-10-07_path-storage-portability-audit.md`, `2026-10-07_path-storage-repairs-and-backup.md`.

No physical relocation, no junction, nothing written to `K:`.

```text
PATH_STORAGE_REPAIRS_INTEGRATED
G1_LOCAL = PASS / G1_REMOTE_CI = PENDING (at the time of writing; see the commit history for the CI result)
D_BACKUP_COLD_VERIFIED
SUPPLEMENTAL_DATA_BACKED_UP
D_BACKUP_DATA_PROTECTION_ASSESSED (result reported to the operator, not recorded here)
G4_PART2_COMPLETE
G5_RESOLVED
K_PRESERVATION_DEFERRED_TO_FINAL_FILESERVICE
PHYSICAL_RELOCATION_NOT_STARTED
```

## A. Git / Integration

- Fresh inspection confirmed the working tree matched the repair report: fail-closed archive root, `.env` reader, `PROMAT_BACKUP_ROOT`, role guards, path ratchet, relocation test, portable VS Code and QA paths. Nothing was re-implemented. `HEAD` was `8f328f8`, identical to `origin/main`, so the branch fast-forwards.
- One commit on `repair/path-storage-roots` carries the repairs of the previous run, the two additions of this run (cold verification, supplemental sets) and the run reports.
- Integration path: this repository integrates by fast-forward push to `main` (no pull requests in the history, no `gh` CLI on the machine). CI runs on that push and is the release gate; a green run deploys the commit to production automatically. The change set does not touch `app/src`, templates or static files.

```text
G1_LOCAL     = PASS
G1_REMOTE_CI = PENDING   (run not finished when this file was committed)
```

```text
STORAGE_RUN_REGRESSION = none
PREEXISTING_PLATFORM_DEPENDENT_TEST =
  test_runtime_packaging.py::test_legal_pages_render_in_image_layout_with_distinct_german_and_english_text
```

Fresh evidence for that test: it fails in this checkout and identically in a clean worktree, passes in both with `PYTHONUTF8=1`, and in the earlier run failed on an untouched `HEAD`. It decodes a subprocess's output with the Windows locale encoding. CI runs on Linux. Not changed.

## B. Cold Verify

- **Physical reconnect: no.** It was not needed. `backup-verify --unbuffered` (new) opens every file with `FILE_FLAG_NO_BUFFERING`, so each byte is read from the device and the operating system's file cache cannot answer. That is exactly the property the reconnect was meant to guarantee, and it is repeatable without an operator. What it does not exercise is a power cycle of the drive; the copy flushes every file to the device before renaming it (`fsync`), so nothing depends on that.
- **Device identity:** Kingston XS2000, USB (serial compared with the previous run, recorded locally), volume label `RESEARCH_BACKUP`, NTFS, 3,584 GB free; `BACKUP_ROOT.json` `role: backup`, `root_id 981086a8-7841-4bc5-96f8-d4cfb12cfe9e`. `PROMAT_BACKUP_ROOT` points at `D:\projects\pronunciation_matters\promat\backup`. Only `panhispanic_media_corpora` exists beside it under `D:\projects`; it was not touched.
- **Result** (19 s, about 390 MB/s):

```text
units=71  BACKED_UP=71  BACKUP_PENDING=0  ACTIVE_LOCAL=0
supplemental_ok=6  supplemental_failed=0
read_mode=unbuffered  verified_files=9403  verified_bytes=7438974103
conflicts=0  missing=0  mismatched=0  unreadable=0
```

  9,237 unit files (6.87 GB) plus 166 supplemental files (65.4 MB). No file was re-copied for the verification.

## C. Supplemental Backup

The earlier list was re-checked. A SHA-256 comparison of every top-level drop-in file of the three import batches against the archive found 468 of 471 byte-identical in the archive (WAV, TextGrid, JSON); only the three workbooks are not. One item was added to the list: the historical batch organizer, which exists only in a git-ignored folder.

| Set | Class | Regenerable | Personal data | Files / bytes | Status |
|---|---|---|---|---|---|
| `intake_workbooks` (3 current workbooks) | authoritative source | no | yes | 3 / 305,534 | BACKED_UP |
| `research_player_config` (`data/config/research_player`) | authoritative source | no | no | 13 / 53,977 | BACKED_UP |
| `praat_pipeline` | historical | no | no | 8 / 63,674,503 | BACKED_UP |
| `informanten_intake_20260525` (first-generation workbooks) | historical | no | yes | 5 / 436,407 | BACKED_UP |
| `fixity` (baselines) | provenance | only as of today | no | 136 / 925,022 | BACKED_UP |
| `historical_organizer` | provenance | no | no | 1 / 30,248 | BACKED_UP |

- Location: `D:\…\backup\supplemental\2026-10-07\<set>\`, with `_manifests\<set>.sha256` and `.json`. The existing `archive\` and `_backup\` trees were not reorganised.
- Tooling: `backup-supplemental` in the existing CLI, using the existing verified copy. Additive; a label is a snapshot; a changed source under an existing label is reported as `conflict_manifest_differs` and nothing is replaced. Sets are verified against their own manifests, without the source, and are included in every `backup-verify`.
- NOT_REQUIRED: runtime sessions, upload packages, MFA working state and caches (regenerable); code and Teaching content (Git).
- Not backed up, by decision: the dev database. It is test state (accounts, sets created during development); the production database is the authority and has its own backup runbook. A local dump from the previous run exists under `tmp/`.

## D. Data Protection on D:

```text
D_BACKUP_DATA_PROTECTION = ASSESSED — operator decision required
```

The backup volume was inspected read-only (encryption state, access control, content classes, documented project requirements). Nothing was changed and the backup was kept. This repository is public, so the classification, its evidence and the required decision are recorded in a local, git-ignored note (`tmp/storage-repairs-2026-10-07/d-backup-data-protection.md`) and were reported to the operator directly.

## E. Preservation

```text
K_PRESERVATION_DEFERRED
```

Pronunciation Matters has no writable namespace of its own on `K:`; the CO.RA.PAN area was deliberately not used. The final institutional file service is expected next week and becomes the preservation target directly. No code change is needed for it: `PROMAT_PRESERVATION_ROOT=<share folder>`, then `copy` (dry-run), `copy --execute`, `verify --unbuffered`, and `supplemental --execute` with the same `--extra` arguments as the backup. Archive fixity is ready (71 units, no drift). Preservation state today: `PRESERVATION_PENDING=71`.

## F. Relocation Readiness

| Gate | State |
|---|---|
| G1 repairs on `main`, CI green | local PASS; remote CI pending at the time of writing |
| G2 full suite at the old location | PASS (1 pre-existing platform-dependent failure, see A) |
| G3 path ratchet at zero | PASS |
| G4 relocation canary | **PASS** — part 1 permanent test; part 2 clean worktree at `C:\temp\Pronunciation Matters ñ\promat_webapp` (the committed state of this change, no operator data): full suite identical to the main checkout, governance and teaching validation green from a working directory outside the checkout, `trace_runtime_paths.py` without any reference to the old checkout. Worktree and folder removed. The existing interpreter environment was reused; it holds no link into the source tree |
| G5 no batch in progress, MFA decision | **PASS** — no intake or MFA process or container; all three batches were last touched in June and are archived. `MFA_WORKING_STATE = REGENERABLE`: a re-run of MFA after the move is acceptable, no legacy-path compatibility is built |
| G6 dev database | PASS (previous run) |
| G7 archive fixity, copies | fixity PASS; physical backup cold-verified; institutional preservation deferred |
| G8 clean Git, handles closed, container removed | move-time |
| G9 file count and bytes of both trees | move-time |

## G. Tests

| Gate | Result |
|---|---|
| Full `pytest`, main checkout | 1272 passed, 1 failed (pre-existing), 2 skipped, 9 deselected |
| Full `pytest`, clean worktree under `Pronunciation Matters ñ` | 1272 passed, 1 failed (the same), 2 skipped, 9 deselected |
| `test_runtime_packaging.py` with `PYTHONUTF8=1` | 3 passed in both locations |
| Storage tests (`test_storage_roots`, `test_archive_preservation`, `test_storage_inventory`) | 83 passed; `test_storage_roots.py` now 26 tests (6 new: unbuffered hashing, supplemental sets) |
| `ruff check` on changed files, `compileall` | passed |
| `scripts/ci_governance_checks.py` | all guards passed |
| `scripts/validate_teaching_content.py` | passed |
| JavaScript tests | 64 passed |

Not run locally (CI only): `shellcheck`, production image build and in-image smoke, backup/restore rehearsal, Chromium browser smoke.

## Answers

1. **Data that exists only once locally:** no non-regenerable research material. Everything has a copy on `C:` and on `D:`. Both copies are in one place and under one custody, and none is institutional yet. The dev database is single-copy by decision.
2. **D: complete and cold-verified:** yes — 71 units and 6 supplemental sets, 9,403 files, read from the device.
3. **Data protection:** assessed; the result and the required decision are in the local note.
4. **Open before the move:** remote CI for G1; G8 and G9 at move time. Institutional preservation should come first.
5. **When the file service is available:** create the project folder, set `PROMAT_PRESERVATION_ROOT`, run `copy` dry-run, `copy --execute`, `verify --unbuffered`, then `supplemental --execute` with the workbook and catalog extras. After `PRESERVED=71`, do the relocation.
