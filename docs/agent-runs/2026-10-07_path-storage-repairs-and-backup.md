# Path/Storage Repairs and Physical Backup — 2026-10-07

Non-normative run report. Binding rules: `docs/spec/platform-data-files.md`, section "Storage Roots" (added in this run). Follows the audit `docs/agent-runs/2026-10-07_path-storage-portability-audit.md`, which is left unchanged as dated evidence.

No physical relocation was done: `C:\dev\promat` and `C:\dev\promat_data_archive` are where they were, and no junction exists. Work is on branch `repair/path-storage-roots`, uncommitted.

```text
PATH_REPAIRS_COMPLETE
STORAGE_ROOTS_EXPLICIT
HARDCODED_PATH_RATCHET_ACTIVE
RELOCATION_CANARY_GREEN
DOCKER_G6_RESOLVED
BACKUP_ARCHITECTURE_READY
D_BACKUP_VERIFIED
K_PRESERVATION_BLOCKED            (PRESERVATION_BLOCKED_BY_STORAGE_ACCESS)
PHYSICAL_RELOCATION_NOT_STARTED
```

## A. Repairs

```text
H1    = PASS
H2    = PASS
H3    = PASS
H4    = PASS
H5-H7 = PASS
```

- **H1 archive root fails closed.** Both `DEFAULT_LOCAL_ARCHIVE_ROOT` literals are gone (`intake_storage.py`, `storage_inventory.py`). `get_local_archive_root()` raises `IntakeStorageError` naming the variable; nothing is created. `import_batch_to_production.py` checks the root before any working, runtime or database write of a non-dry run; `archive_preservation.py` exits with code 2; the read-only inventory reports "NOT CONFIGURED" instead of assuming a location.
- **H2 local `.env`.** New `scripts/research_data_intake/storage_roots.py` (stdlib, about 90 lines): reads the repository-root `.env` for exactly three names, never overrides the process environment, never writes, refuses relative values, has no defaults and no host detection. `python-dotenv` was not used: it is only a pinned requirement with no caller, and a general loader would have pulled unrelated keys into the environment. Versioned `.env.example` added; `.env` was already git-ignored.
- **H3 ratchet.** `scripts/ci_governance_checks.py` gained the guard "machine-dependent absolute paths in active code or configuration" (drive paths, UNC shares, home directories, the archive directory name). Python files are checked by string literal, so docstrings and comments are not hits; other files line by line without comment lines; escape marker `path-literal: <reason>`. Baseline: **0 findings**, no baseline file.
- **H4 relocation test.** `app/tests/test_relocation.py`, everything under `tmp_path / "Pronunciation Matters ñ"` with an unrelated working directory: composed app on a relocated synthetic runtime (public page, teaching page, legal page, static asset, design page, `/ready`, protected player page and audio byte-identical after login), archive unit written through the configured root, archive moved and repointed with identical manifest, checksums and fixity, and the fail-closed case with nothing created.
- **H5–H7.** `.vscode/tasks.json` uses `${workspaceFolder}`; the stale `app/.vscode/tasks.json` (its `tmp` script no longer exists) is removed; `scripts/qa/capture_qa.ps1` derives from `$PSScriptRoot`; `scripts/qa/responsive_smoke.py` derives from the repository root; examples in `scripts/research_data_intake/README.md`, `validate_research_config.py`, `app/.env.example` and two lines of `docs/runbooks/research-intake-working-pipeline.md` are portable. Other runbooks and run logs that mention `c:/dev/promat` were deliberately not rewritten.

## B. Docker

```text
G6 = PASS
```

- `promat_auth_db` exists and runs (`postgres:15`, healthy, created 2026-05-03), compose project `promat`, working dir and config file under `C:\dev\promat`, bind mount `C:\dev\promat\data\db\postgres_dev -> /var/lib/postgresql/data`.
- The dev database is **not disposable without thought**: 29 accounts (4 admin, 25 user), 8 research sets with 995 items, 65 research people rows, analytics rows. A full `pg_dump` (1.4 MB) is kept at `tmp/storage-repairs-2026-10-07/promat_dev_db_2026-10-07.sql` (git-ignored; contains password hashes and e-mail addresses, so it must stay local).
- The dump contains **0** absolute machine paths (`C:\`, `C:/dev`, the archive directory name, `/home/`). `research_people.consent_file` / `questionnaire_file`: 64 values, none with a path separator.
- Because the mount is a bind mount inside the checkout, the data travels with a rename. The container itself keeps the old absolute mount and must be removed before the move and recreated after it (`docker compose down`, then `dev-start.ps1`).
- Side observation: the running container publishes `0.0.0.0:54321`, while the compose file says `127.0.0.1`. The container predates that setting; recreating it at move time corrects this.

## C. Roots

| Root | Contract now in force |
|---|---|
| `PROMAT_LOCAL_ARCHIVE_ROOT` | Local working archive; the only intake target. Required for every intake and archive operation; unset is an error before any write. Authoritative for a unit until that unit is `PRESERVED`. This machine: set in `.env` (the existing archive). |
| `PROMAT_PRESERVATION_ROOT` | Verified institutional copy; written only by `archive_preservation.py copy`; marker `PRESERVATION_ROOT.json` (`role: preservation`). Optional; unset means every unit stays `PRESERVATION_PENDING`. This machine: unset. |
| `PROMAT_BACKUP_ROOT` | Physically separate backup; written only by `archive_preservation.py backup-copy`; marker `BACKUP_ROOT.json` (`role: backup`). Optional and may be offline. Never authoritative, never an intake target, never a data source, never grounds for cleanup. This machine: set in `.env`. |

All three: process environment first, then the repository-root `.env`; no default. A directory carrying the other role's marker, or equal to or nested in another root, is refused before anything is written. The web application reads none of them (enforced by a test).

## D. D: Backup

- **Volume:** `D:` = Kingston XS2000, USB, NTFS, label `RESEARCH_BACKUP`, 3,815 GB, 3,591 GB free, healthy.
- **Existing structure:** `D:\projects\panhispanic_media_corpora\corapan\{archive,snapshots}`. No Pronunciation Matters content existed. Convention read from it: `D:\projects\<umbrella>\<project>\<kind>`.
- **Chosen target:** `D:\projects\pronunciation_matters\promat\backup` (parent created by hand, the root itself by the tool). Nothing of CO.RA.PAN was touched.
- **Procedure:** the existing verified copy of `preservation.py`, parameterised by a role, instead of a second tool. New commands `backup-copy`, `backup-verify`, `backup-status`. Additive only: no delete, no overwrite (a differing file is a reported conflict), no mirror or sync, dry-run by default, `--exclude-secure` refused.
- **Data copied: yes.** All conditions held (unambiguous empty target, ample space, tooling built and tested for it, clean dry-run). Dry-run: 71 `would_back_up`. Execute: 71 `backed_up` in 121 s. Result on `D:`: 9,237 files, 6.87 GB, identical in count and size to the local `sessions/` and `batches/`; 71 receipts on both sides; no `*.partial` left.
- **Verification:** every file was hashed at the source, read back from the destination and compared before the rename; `backup-verify` then re-hashed everything: `BACKED_UP=71`, `BACKUP_PENDING=0`. Caveat: that pass took 9 s, so it was almost certainly served from the operating system's file cache. A cold `backup-verify` after disconnecting and reconnecting the disk is still owed and is now a runbook step.
- **Not in the backup** (same scope as preservation, listed by the tool): archive-root folders `praat_pipeline/` and `informanten_intake_20260525/`, the fixity baselines, the three current intake workbooks under `import/<batch>/`, and the catalogs under `data/config/research_player/`.
- Side effect in the local archive: the tool-owned folder `backup/receipts/` (71 small JSON files). No existing archive file was changed.
- Preservation state after the backup is unchanged: `PRESERVATION_PENDING=71`.

## E. K: Preservation

```text
BLOCKED
```

`K:` is reachable (196 GB free); `K:\Pronunciation_Matters` does not exist. No write or create attempt was made in this run and no permission was changed. The archive's fixity is ready for the copy: `baseline` dry-run over 71 units and 9,237 files reported 68 `baseline_present`, 3 `covered_by_unit_manifest`, no drift.

## F. Tests and Gates

| Gate | Result |
|---|---|
| Full `pytest` (`app/`, `python -m pytest tests -q`) | **1266 passed, 1 failed, 2 skipped, 9 deselected** |
| New tests | 29: `test_storage_roots.py` 20, `test_machine_path_guard.py` 6, `test_relocation.py` 3, plus updated `test_storage_inventory.py`; an autouse fixture hides every operator root from the suite |
| `ruff check` on all changed and new Python files | passed |
| `compileall` on changed trees | passed |
| `scripts/ci_governance_checks.py` | all 8 guards passed, including the new one |
| `scripts/validate_teaching_content.py` | passed |
| JavaScript tests (`node --test`) | 64 passed |

The one failure is `test_runtime_packaging.py::test_legal_pages_render_in_image_layout_with_distinct_german_and_english_text`. It is not caused by this run: it fails identically on an untouched checkout of `HEAD` (temporary worktree, since removed) and passes with `PYTHONUTF8=1`. The test decodes a subprocess's output with the Windows locale encoding; on Linux CI it is not expected to fail. Not changed here.

Not run locally: `shellcheck`, the production image build and in-image smoke, the backup/restore rehearsal and the Chromium browser smoke. They run in CI. The image copies only `apply_prod_db_payload.py` from the intake scripts, which does not import the changed modules.

## G. Remaining Migration Gates

| Gate | State |
|---|---|
| G1 repairs on `main`, CI green | **open** — changes are uncommitted on `repair/path-storage-roots` |
| G2 full suite baseline at the old location | done locally (see F); CI confirms |
| G3 ratchet at zero | **pass** |
| G4 relocation canary | part 1 (permanent test) **pass**; part 2 (clean worktree under `C:\temp\Pronunciation Matters ñ`, full suite there) **open** |
| G5 no batch in progress; decision on MFA working state | **open** — operator decision |
| G6 dev database | **pass** |
| G7 archive fixity clean, preservation state known | fixity **pass**; preservation **blocked** on `K:`; a verified physical backup now exists |
| G8 clean Git, no handles, dev server stopped, container removed | **open** — at move time |
| G9 file count and bytes of both trees recorded | **open** — at move time (the archive now has 71 more files than in the audit: the backup receipts) |

At move time, additionally: update `PROMAT_LOCAL_ARCHIVE_ROOT` in `.env`, recreate `.venv`, copy the Claude Code project memory to the new project key.

## H. Recommendation

Order: **1. preservation on K:, 2. keep the D: backup current, 3. local relocation.**

The next run should be exactly this: commit and merge the repairs (G1), then a cold `backup-verify` after reconnecting `D:`, and a small additive step that also secures what neither copy covers today — the three current intake workbooks, the research-player catalogs, `praat_pipeline/`, `informanten_intake_20260525/` and the fixity baselines. Those are the remaining single-copy items, and they are tiny.

Preservation on `K:` needs one thing from outside the repository: the folder `K:\Pronunciation_Matters` created with write permission by the file service. Once it exists, the run is the existing runbook (`copy` dry-run, `copy --execute`, `verify`), with no code change. The physical relocation stays last; it is a rename and is no longer blocked by anything technical except G4 part 2 and the move-time gates.
