# Local Project Relocation — 2026-10-07

Non-normative run report. Follows `2026-10-07_path-storage-portability-audit.md`, `2026-10-07_path-storage-repairs-and-backup.md` and `2026-10-07_storage-integration-and-cold-backup-verify.md`. No rule changed in this run.

```text
LOCAL_RELOCATION_COMPLETE

REPO_ROOT          = C:\dev\pronunciation_matters\promat_webapp
LOCAL_ARCHIVE_ROOT = C:\dev\pronunciation_matters\promat_data_archive

D_BACKUP_OPERATOR_APPROVED
D_BACKUP_VALID
OLD_ROOTS_ABSENT
DOCKER_REBOUND
DATABASE_INTACT
FULL_VALIDATION_PASS
NO_JUNCTIONS
INSTITUTIONAL_PRESERVATION_PENDING
```

## A. Before

```text
OLD_REPO_ROOT    = C:\dev\promat
OLD_ARCHIVE_ROOT = C:\dev\promat_data_archive
```

**G1 (remote CI of `80bc1f0`).** Not green and not re-run: every job passed (Python lint, governance and full suite; JavaScript; production image; backup/restore rehearsal) except "Browser smoke", which was cancelled by its 15-minute timeout while still in "Install dependencies", before any project code ran. The release gate is therefore red and the deployment was skipped. Assessment: independent of the storage and path change, whose jobs are green; the relocation was not made to wait for it. A re-run through the GitHub web UI is still owed (no authenticated client on this machine).

**G8 = PASS.** Git clean on `80bc1f0` = `origin/main`, nothing unpushed, no stash, one worktree; no intake, MFA or dev-server process; `promat_auth_db` removed with `docker compose down`; nothing written to the backup volume.

**G9 (snapshot directly before the renames).**

| | Files | Bytes |
|---|---|---|
| Checkout | 88,668 | 20,168,858,699 (33 MFA cache files unreadable, as before) |
| Archive | 9,463 | 7,438,630,395 |

Archive content: 65 sessions + 6 batches = 71 units; 68 fixity baselines; 71 backup receipts; 6 supplemental receipts; 0 preservation receipts. States: `PRESERVATION_PENDING=71`, `BACKED_UP=71`, fixity without drift.

## B. Move

```text
C:\dev\promat_data_archive -> C:\dev\pronunciation_matters\promat_data_archive   OK
C:\dev\promat              -> C:\dev\pronunciation_matters\promat_webapp         OK
```

- `C:\dev\pronunciation_matters` was created as a plain folder; it is not a Git repository and holds exactly the two directories.
- Both moves are single same-volume renames. Nothing was copied, nothing inside either tree was reorganised, no manifest or report was rewritten, no junction or symlink exists.
- The archive was renamed first and verified at its new place before the checkout was touched.
- The checkout could not be renamed from inside the editor session that had it open. A one-off helper outside the checkout waited until the folder was free and then performed the one rename; the operator closed the editor for this. The helper folder is deleted; its script and log are kept under `tmp/relocation-2026-10-07/`.

## C. After

```text
NEW_REPO_ROOT    = C:\dev\pronunciation_matters\promat_webapp
NEW_ARCHIVE_ROOT = C:\dev\pronunciation_matters\promat_data_archive
```

- `.env`: `PROMAT_LOCAL_ARCHIVE_ROOT` points at the new archive root; `PROMAT_BACKUP_ROOT` unchanged; `PROMAT_PRESERVATION_ROOT` unset.
- `.venv` deleted and recreated in place: project requirements (`app/requirements.txt`, `app/requirements-dev.txt`), then the remaining packages of the previous environment at their recorded versions (48 packages, among them playwright, praatio and the MFA package). The interpreter and the VS Code tasks resolve inside the new checkout.
- Claude Code project state copied to the new project key; the old directory is kept.

## D. Docker

- Container `promat_auth_db` recreated from the new checkout: compose project `promat_webapp`, bind mount `…\promat_webapp\data\db\postgres_dev -> /var/lib/postgresql/data`, healthy.
- Network binding: `127.0.0.1:54321` only. The earlier `0.0.0.0:54321` binding is gone.
- Database intact, row counts identical to the dump taken before the move: 29 accounts (4 admin, 25 user), 177 research sets with 20,572 items, 65 research people, 65 research sessions, 33 analytics rows. Correction to the two earlier reports: they gave 8 sets and 995 items, taken from table statistics that were out of date; the dump shows the figures above were already true then.
- Login through the running app with the dev admin succeeded (303, access cookie set); `/ready` reported the database, data root, logs directory and rate-limit backend as ok.

## E. Validation

| Check | Result |
|---|---|
| Archive files / bytes | 9,463 / 7,438,630,395 — identical to G9 |
| Checkout files / bytes | 88,673 / 20,168,868,528 — G9 plus the five hand-over files written after the snapshot and the 22-byte `.env` edit; every other top-level entry identical |
| `git status`, `git fsck`, `git remote -v` | clean, no errors, remote unchanged |
| `storage_inventory.py` | archive root = new path (from `.env`); backup root = existing backup; preservation not configured |
| Archive units / batches | 71 / 6; `PRESERVATION_PENDING=71`; fixity `baseline_present=68`, `covered_by_unit_manifest=3`, no drift |
| Importer `--dry-run` on an existing batch | exit 0; 28 sessions planned, 0 conflicts; archive path resolved at the new root |
| `trace_runtime_paths.py` | every path under the new checkout; no reference to an old root |
| App (canonical `dev-start.ps1`) | public pages (landing, project, teaching, legal, research, design) and a static asset 200; protected speakers page and player pages 200 after login |
| Player audio | one session each for Spanish, French and English: 200, `audio/mpeg`, byte length equal to the file on disk |

One expected consequence, as decided under G5: in the dry-run the `text` task of the batch reports "needs preparation" (MFA working state no longer matches). That state holds absolute paths and is regenerable; it only matters if this batch is imported again, which would re-run MFA. Whether it was already stale before the move was not compared.

### Tests

| Gate | Result |
|---|---|
| Full `pytest` | 1272 passed, 1 failed, 2 skipped, 9 deselected |
| The one failure | `test_runtime_packaging.py::test_legal_pages_render_in_image_layout_with_distinct_german_and_english_text` — the documented Windows locale issue; 3 passed with `PYTHONUTF8=1`; green in Linux CI |
| Governance checks incl. path ratchet | passed, 0 findings |
| Teaching validation | passed |
| JavaScript tests | 64 passed |
| `ruff check` on all tracked Python files, `compileall` | passed |

## F. Backup

```text
D_BACKUP_OPERATOR_APPROVED
D_BACKUP_STATUS = VALID
```

Nothing was copied to the backup. After the move: `backup-status` `BACKED_UP=71`; `backup-verify --unbuffered` `BACKED_UP=71`, `supplemental_ok=6`, `supplemental_failed=0`, 9,403 files, 7,438,974,103 bytes. No receipt or manifest contains a local absolute path, so no identity depended on the old location.

## G. Preservation

```text
INSTITUTIONAL_PRESERVATION_PENDING
PROMAT_PRESERVATION_ROOT = unset
PRESERVATION_PENDING = 71
```

Nothing was written to `K:`. When the institutional file service is available: set `PROMAT_PRESERVATION_ROOT` to the project folder on it, then `copy` (dry-run), `copy --execute`, `verify --unbuffered`, and `supplemental --execute` with the workbook and catalog extras from `docs/runbooks/archive-preservation.md`. Target: `PRESERVED=71`.

## H. Old Paths

```text
C:\dev\promat                 DOES_NOT_EXIST
C:\dev\promat_data_archive    DOES_NOT_EXIST
```

Checked again after the full test suite, the importer dry-run, the app start and the backup verification: neither path was recreated. The only tracked non-documentation mention of the old checkout path is a fixture string in `app/tests/test_machine_path_guard.py`.

## Left for the operator

- Re-run the failed job of the CI run for `80bc1f0` (or rely on the run triggered by this report's commit).
- Delete the old Claude Code project directory `c--dev-promat` once the new one is confirmed in use.
- `tmp/relocation-2026-10-07/` (snapshots, helper script and log, package list) can be deleted after one release cycle.

## Post-Run Update (2026-10-07, after the push of this report)

```text
G1 = PASS
CI = PASS
BROWSER_SMOKE = PASS
PRODUCTION_DEPLOYMENT = PASS
```

- Commit `4c73c4a` (this report, on top of the storage commit `80bc1f0`) is on `main`. Its CI run was green in every job, including the browser smoke that had been cancelled in the earlier run, and the production deployment that followed succeeded. The cancelled run for `80bc1f0` does not need to be re-run. The statements above that describe G1 as open were correct when written.
- `DEV_DB`: 177 research sets, 20,572 items. The lower figures in the two earlier reports came from out-of-date table statistics; the dump taken before the move already held these numbers, so nothing was lost in the relocation.
- `MFA_WORKING_STATE = REGENERABLE`. The Spanish batch may need a new preparation and MFA run if it is ever imported again. No repair is required.
- Cleanup: the local and remote work branch `repair/path-storage-roots` is removed (fully contained in `main`); the old path-keyed Claude Code project directory is removed after its content was confirmed in the new one; of `tmp/relocation-2026-10-07/` only the pre-move snapshot, the rename log, the package list of the previous environment and the last backup verification report remain.

```text
LOCAL_RELOCATION_FINALIZED
INSTITUTIONAL_PRESERVATION_PENDING
```