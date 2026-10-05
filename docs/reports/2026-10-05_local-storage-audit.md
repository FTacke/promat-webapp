# Local Storage Audit — 2026-10-05

Audit of the operator's Windows development machine. Non-normative report; binding rules live in `docs/spec/platform-data-files.md` (new section "Local Storage Roles And Preservation Root"). Sizes are binary units (GB = GiB). No participant-identifying names or IDs are recorded here; no secret values were read.

Labels: **CURRENT PHYSICAL LOCATION — NOT ARCHITECTURAL IDENTITY** marks machine-specific paths that must stay configuration.

> **Reconciliation note (2026-10-05, after the preservation tooling):** this report's migration wording "set the env var" / "root is read from `PROMAT_LOCAL_ARCHIVE_ROOT`" is superseded. The local archive stays the working archive written by intake; the institutional copy is configured separately through `PROMAT_PRESERVATION_ROOT` and created by `scripts/research_data_intake/archive_preservation.py`. Measurements below remain valid as dated facts. See `docs/spec/platform-data-files.md` and `docs/runbooks/archive-preservation.md`.

## Executive summary

- Total local PROMAT footprint: ≈ 26.8 GB before, ≈ 25.1 GB after cleanup (repo tree 19.8 GB + archive 6.9 GB). `C:` had 203.6 GB free before and 205.8 GB after.
- Largest consumers: `scripts/research_data_intake/import/` 12.5 GB (three batches), `exports/` 2.3 GB, local archive 6.9 GB, `data/sessions` 0.96 GB, `.venv` 0.83 GB, intake `.mfa_cache` 0.79 GB.
- Reclaimed in this run: **1.70 GB** (tmp QA captures/Edge profiles + tool caches). One more ≈ 3.1 GB is reclaimable immediately by operator decision (English batch legacy `.mfa_cache`, see Deferred).
- Potentially reclaimable after verified institutional preservation: ≈ 6.3 GB duplicated source WAVs in `import/`, ≈ 3.4 GB `working/` (≈ 1.0 GB of it is regenerable MFA corpus now), ≈ 2.3 GB `exports/`.
- Growth is **not yet controlled**: every completed batch leaves ≈ 2.9× its original audio locally (see Duplication map) and nothing ever cleans it; the only archive is on the same disk.
- Verdict: no waste crisis (≈ 25 GB), but the archive is the only authoritative copy of the originals and is not preserved anywhere else.

## Storage map

| Path (CURRENT PHYSICAL LOCATION) | Size | Role |
|---|---|---|
| `C:\dev\promat\.git` | 0.33 GB | SOURCE |
| `.venv` | 0.83 GB | CACHE (recreatable) |
| `data/sessions/{french,spanish,english}` | 0.96 GB (8,324 MP3 + JSON) | REGENERABLE (importer from archive) |
| `data/db/postgres_dev` | 70 MB | UNKNOWN — Postgres volume, never a cache |
| `data/config/research_player/**` | 0.1 MB | SOURCE/UNIQUE (untracked, see I) |
| `scripts/research_data_intake/import/<3 batches>` | 12.5 GB | SOURCE copy + WORKING (details below) |
| `scripts/research_data_intake/exports/` (7 packages) | 2.3 GB | SPOOL |
| `scripts/research_data_intake/.mfa_cache/shared/{es,fr}` | 0.79 GB | CACHE (no `en` shared cache exists) |
| `C:\dev\promat_data_archive` | 6.9 GB, 9,250 files | SOURCE/UNIQUE (local-only) |
| `tmp/` (after cleanup) | 0.38 GB | WORKING: intake-run notes, 2 MFA test dirs (0.25 GB), one prod-import check dir (0.13 GB, contains WAVs) — kept, REVIEW |
| `logs/`, `secure/`, `public/` | ~0 | empty/placeholder (`secure/` only `.gitkeep`) |
| sibling dirs under `C:\dev` | not scanned | other projects (`corapan*`, `hispanistica*`, …) — out of scope |

Import batches: `english_batch_20260618` 4.3 GB (of which 3.1 GB legacy `.mfa_cache`, 0.45 GB `working/`), `french_batch_20260618` 4.6 GB (1.7 GB `working/`), `spanish_batch_20260619` 3.6 GB (1.3 GB `working/`).

## Worktree audit

`git worktree list --porcelain`: exactly one entry — `C:/dev/promat` → `refs/heads/main` → `28c63d1` (== `origin/main` after fetch; at audit start clean; the only post-audit changes are the files added by this run). No sibling worktrees, nothing to prune or remove. Local branches `feature/direct-mail-sendmail`, `fix/design-responsive-ui-polish`, `fix/responsive-layout-polish-round-2` are merged into `main` (branch refs only, not worktrees; not deleted — operator decision). No intake files were found inside any worktree. The repo directory is `C:\dev\promat` (not `promat_webapp`).

## Intake duplication map (measured)

Per language, all sizes measured on disk:

| Stage | Spanish | French | English | Audio? |
|---|---|---|---|---|
| Original WAV/TextGrid in drop-in `import/<batch>/` | 2.4 GB | 3.1 GB | 0.8 GB | lossless; unique until archived |
| `working/` (copy of sources + `mfa_corpus` slices) | 1.3 GB | 1.7 GB | 0.45 GB | lossless copies + derived slices |
| legacy `.mfa_cache` in batch | – | – | 3.1 GB | tool cache |
| runtime `data/sessions/<lang>` | 0.37 GB | 0.46 GB | 0.13 GB | derived MP3 |
| archive `sessions/<lang>` (raw + source + alignment + runtime MP3) | 2.7 GB | 3.4 GB | 0.9 GB | lossless + derived |
| export package | 0.38 GB | 0.46 GB | 0.13 GB | derived MP3 |
| Local total for the batch | ≈ 7.1 GB | ≈ 9.1 GB | ≈ 5.6 GB (2.5 w/o legacy cache) | |
| Multiple of original audio | ≈ 2.9× | ≈ 2.9× | ≈ 3.1× (6.8× incl. cache) | |

Evidence: SHA-256 comparison showed **all** original WAV/TextGrid files in the three batch drop-ins (420 files, 6.35 GB) are byte-identical to files in the archive; all `working/` WAVs are archive-identical except 3,110 `text/mfa_corpus` slices (≈ 1.0 GB, regenerable). The three current intake workbooks are **not** archive-identical (see J). Inside the archive, `raw/` and `source/` WAVs are byte-identical for only 20 of 156 pairs (0.39 GB), so they are mostly distinct (original vs processed), not wasteful duplication. Production holds a further copy server-side (not inspected).

What blocks cleanup today: (1) the archive itself is on `C:` and not preserved institutionally, so deleting the drop-in leaves a single copy; (2) prod-publish confirmation for packages is not recorded locally; (3) re-import tooling expects `working/` and the batch workbook.

Smallest growth-prevention changes (not implemented): record a lifecycle marker (`PRESERVED` + checksum manifest) per batch; make `exports/` retention follow the existing release-retention idea; stop creating batch-local `.mfa_cache` (the shared cache already replaced it, code still migrates the legacy one).

## Preservation status

Everything below exists **only on this machine** (no institutional copy verified):

- all original recordings and annotations (in archive; drop-in copies are duplicates),
- the three current intake workbooks (only in `import/<batch>/`),
- `data/config/research_player/**` task catalogs (copies also inside every upload package),
- the historical `organize_batch_working_tree.py` (only in gitignored `import/`),
- the dev Postgres volume.

`K:\Pronunciation_Matters` does not exist yet.

## Safe cleanup performed

| What | Result |
|---|---|
| `tmp/` Edge QA profiles and screenshot dirs (`edge-qa-*`, `mobile-audit-*`, `ui-qa`, `phenomena-*`, `promat-*-qa`, `shell-*`, `topbar-*`, `drawer-*`) — 51 dirs, no research data inside | removed |
| `tmp/` root `*.png`, `*.html`, `30_components.live*.css` captures | removed |
| `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `__pycache__` under `app/`, `scripts/`, `tmp/` | removed |
| Space reclaimed (free-space delta on `C:`) | 1,822,412,800 bytes (1.70 GB) |
| Worktrees before/after | 1 / 1 |
| Git status after | clean except files added by this run |

Intentionally retained despite size: `.venv`, `import/*`, `exports/*`, archive, `data/sessions`, `data/db`, `.mfa_cache/shared`, remaining `tmp/` intake notes and MFA test dirs. No research data, workbook, catalog or database was deleted.

## Deferred cleanup

- `import/english_batch_20260618/.mfa_cache` (3.1 GB): regenerable, but `run_text_mfa.py` migrates it into the not-yet-existing `shared/en`; deleting forces an MFA model download. Operator decision.
- `working/**/text/mfa_corpus` + `mfa_output`: after archive verified.
- `exports/` packages: after prod publish confirmed; catalogs in them are currently a second copy of the local catalogs (back up catalogs first).
- Drop-in source WAVs, `working/`, local archive: only after verified institutional preservation.
- `tmp/production-import-check-*`, `tmp/mfa-english-*`: April test artifacts, REVIEW.

## Proposed cleanup policy

Implemented as `docs/runbooks/local-storage-hygiene.md` and the spec section: always-safe caches/QA debris; operator-confirmed regenerable intermediates; preservation-gated sources; never-delete class. Lifecycle by evidence, not state machinery: `ACTIVE → INTAKE_COMPLETE (archive manifest + import report) → PRESERVATION_PENDING → PRESERVED (checksummed copy verified) → LOCAL_CLEANUP_ELIGIBLE`. No retention periods were invented.

## Proposed storage inventory tooling

`scripts/storage_inventory.py` (added, read-only, lint-clean): sizes per location/batch/`working/`, worktree state (missing/dirty), archive root and its source (env vs default), preservation-root reachability and optional size, cleanup candidates, `--json`. Verified on this machine.

## Risks / operator decisions

1. Archive is single-copy on `C:`; highest risk. Next step is the verification-first copy to the preservation root (below).
2. `data/config/research_player/**` is untracked (`.gitignore: data/config/*`); only other copies are in upload packages. Back up before cleaning exports.
3. Historical organizer exists only in a gitignored dir; the committed reconstruction is **not proven equivalent** and is not on `main` (H).
4. MFA image is unpinned (`mmcauliffe/montreal-forced-aligner:latest`); local venv `mfa` CLI is broken (`_kalpy` import error), so alignment depends on Docker.
5. `intake_storage.py` hardcodes the fallback `C:\dev\promat_data_archive` (`DEFAULT_LOCAL_ARCHIVE_ROOT`); `PROMAT_LOCAL_ARCHIVE_ROOT` is unset on this machine, so the default is in force.

`K:\Pronunciation_Matters` as preservation root: **yes, cleanly**, because archive layout is root-relative (`sessions/{lang}/{session_id}/…`) and the root is read from `PROMAT_LOCAL_ARCHIVE_ROOT`. Migration = verified copy + set the env var. Smallest optional change: make the code fallback fail loudly instead of defaulting to a drive path (not implemented).

---

# Cloud handoff: verified local environment facts

## A. Git topology

- Canonical checkout (CURRENT PHYSICAL LOCATION): `C:\dev\promat`; branch `main`; HEAD `28c63d1853d727aab8beee7a6b930f343f4e3f6e`; identical to `origin/main` (fetched 2026-10-05).
- Worktrees: only `C:/dev/promat` → `main` → `28c63d1`. Canonical for development. No obsolete worktrees existed; none removed. No scientific/intake files in any worktree except the main checkout's gitignored `import/`, `data/`, `exports/` (by design).
- Canonical git state = `main`/`origin/main`. Local-only operational state = everything gitignored (`import/`, `exports/`, `data/*`, `tmp/`, `secure/*`, `.venv`, `.mfa_cache`) plus `C:\dev\promat_data_archive`. Stale copies: none. Unmerged remote Claude branches exist: `claude/storage-preservation-architecture` (adds the storage plan and the reconstructed organizer), `claude/production-safety-foundation` (same organizer), `claude/wizardly-mayer-jaa7z2`; none is merged into `main`.

## B. Physical paths (all CURRENT PHYSICAL LOCATION — NOT ARCHITECTURAL IDENTITY)

| Path | Purpose | In git? | Data class | Configurable via |
|---|---|---|---|---|
| `C:\dev\promat` | repo | yes | source | – |
| `scripts/research_data_intake/import/<batch>/` | intake drop-in | no (ignored) | source copies + workbook | batch-dir CLI arg |
| `…/import/<batch>/working/` | per-batch person/task tree | no | derived + source copies | fixed relative to batch |
| `data/sessions/{lang}/` | runtime tree | no | derived MP3/JSON | `PROMAT_RUNTIME_ROOT` |
| `C:\dev\promat_data_archive` | archive root | outside repo | source/unique | `PROMAT_LOCAL_ARCHIVE_ROOT` (unset; code default) |
| `…/exports/<package>/` | prod upload packages | no | derived | build script args |
| `tmp/` | scratch | no | temporary | – |
| `…/.mfa_cache/shared/{lang}` | MFA model cache | no | cache | fixed under intake root |
| `data/db/postgres_dev` | dev Postgres bind mount | no | DB state | `docker-compose.dev-postgres.yml` (`PROMAT_DEV_DB_PORT`) |
| `logs/` | logs | no | – | – |
| `C:\dev\promat_data_archive\{batches,praat_pipeline,informanten_intake_20260525}` | per-batch reports/checksums; legacy Praat pipeline incl. Praat.exe and plain-text catalogs; first-generation workbooks | outside repo | source/unique | under archive root |

No database dumps found. Other `C:\dev\*` projects are unrelated and were not scanned.

## C. Configuration map (values not recorded for secrets; none inspected)

| Name | Controls | Configured via | Required | Machine path? |
|---|---|---|---|---|
| `PROMAT_LOCAL_ARCHIVE_ROOT` | archive root | shell env (unset locally) | local intake | yes |
| `PROMAT_RUNTIME_ROOT` | runtime data root (`data/`) | env / code default | local, CI tests, prod | yes |
| `PROMAT_PUBLIC_ROOT` | public asset root | env / default | local, prod | yes |
| `PROMAT_TEACHING_CONTENT_ROOT` | teaching content | env / default | optional | yes |
| `PROMAT_ENV` | dev/prod mode | env | all | no |
| `PROMAT_PUBLIC_BASE_URL` | public URL | prod env | prod | no |
| `PROMAT_REQUIRE_RUNTIME_CONFIG` | fail if config missing | env | optional | no |
| `PROMAT_APP_SRC` | app path for payload script | env | local script | yes |
| `PROMAT_MFA_DOCKER_IMAGE` | MFA image override | env | local intake | no |
| `PROMAT_DEV_DB_PORT` | dev Postgres host port | env | local | no |
| `AUTH_DATABASE_URL` | auth/research DB | env (dev default points to local Postgres `:54321`) | local, prod | dev default only |
| `POSTGRES_USER/PASSWORD/DB` | dev DB container | compose file | local | no (dev creds are in tracked compose) |
| `JWT_SECRET_KEY` (alias `JWT_SECRET`) | auth signing | prod env — value inspected: NO | prod, CI | no |
| `FLASK_SECRET_KEY`, `SMTP_*`, `MAIL_ENABLED` | sessions / mail | prod env — values inspected: NO | prod | no |
| `PROMAT_QA_EMAIL/PASSWORD` | QA login for smoke script | shell — NO | optional | no |

Publishing uses CLI args (`--host`, `--ssh-user`, `--upload-id`, `--remote-app-root`), not env vars. No backup/restore env vars found in code (backup/restore is documented in runbooks only). None of the sensitive names were set in this shell.

## D. Archive root and preservation status

- `PROMAT_LOCAL_ARCHIVE_ROOT` unset → code default `C:\dev\promat_data_archive` (local `C:` disk, outside repo). 6.9 GB, 9,250 files: 65 sessions (en 10, es 24, fr 31), each with `archive_manifest.json` (65/65); 6 batch folders with `checksums.sha256`, intake/validation/archive reports; 312 WAV (5.9 GB), 8,324 MP3.
- Contains original recordings **not available elsewhere** (drop-in copies are duplicates on the same disk). Session-internal checksums: none beyond manifest + per-batch `checksums.sha256`. Nothing is on institutional storage.
- Intended role: **institutional preservation root**; current physical target `K:\Pronunciation_Matters` — a current physical target, not a permanent identifier. It must stay configurable; a later move to a dedicated university volume = verified migration + configuration change, with no change to intake semantics or archive IDs.

## E. K: facts

- `K:` is mounted and reachable: NTFS network share (DFS, university HRZ), 948 GB used / 178.3 GB free at audit time.
- `K:\Pronunciation_Matters` does **not** exist. Writability: UNKNOWN (deliberately not tested; nothing was created on `K:`).
- `K:\Corapan` exists (existence check only; contents not inspected). `K:\Corapan` and `K:\Pronunciation_Matters` are separate project roots; never intermix.
- Suitability: free space (178 GB) is ≈ 25× the 6.9 GB archive; NTFS handles normal copy/hash. Throughput over DFS not measured.

## F. Original scientific data

| Class | Where | Size/count | Other copy? | Preservation |
|---|---|---|---|---|
| Original WAV (raw + processed) | archive `sessions/*/*/{raw,source}`; also drop-in `import/` | 312 WAV in archive (5.9 GB); 3,578 WAV in `import/` incl. slices | drop-in == archive (byte-identical, same disk) | local-only |
| TextGrids / Amberscript-derived JSON | archive `alignment_source/`; drop-in | 108 TextGrid in archive | yes, same disk | local-only |
| Master workbooks | `import/<batch>/promat_intake_<lang>.xlsx` (current, June); archive `informanten_intake_20260525/` (May, different content) | 3 current + 4 early | no | local-only |
| Secure person metadata | archive `sessions/*/secure/secure_person_intake.json` | one per session | no | local-only; never in git |
| Task catalogs | `data/config/research_player/**` | 3 languages × 2 tasks | identical copies in all 7 upload packages; older plain-text versions in archive `praat_pipeline/catalogs` | local + packages |

`secure/` in the repo is empty by design.

## G. Actual duplicate-copy lifecycle

See "Intake duplication map". Chain: source/drop-in (lossless, unique until archived) → `working/` (lossless copies + derived MFA slices, regenerable partly) → runtime MP3 (derived, regenerable from archive) → archive (lossless + derived, canonical) → export package (derived MP3, regenerable) → production copy (not inspected). Cleanup-eligible: drop-in/`working` after preservation; runtime and export when prod/runtime reproducibility from archive is confirmed.

## H. Organizer equivalence evidence

- Historical copy: `C:\dev\promat\scripts\research_data_intake\import\organize_batch_working_tree.py` (gitignored; 746 lines; mtime 2026-05-26), SHA-256 `539973a1b575b8268cd7abdcc63758d3e8c0cb2900c86318c39d279055446fc0`.
- Reconstructed copy: **not on `main`** (introduced in commit `54a5f2c`, present on `origin/claude/production-safety-foundation` and `origin/claude/storage-preservation-architecture`; 587 lines), SHA-256 `2274ba44b80d59ba0df165a5e39fd315e41fef58379a4e2bfca280661b9f4582`. Both unmerged branches carry the identical file.
- **Not byte-identical.** Neither file was modified.
- Evidence: in a throwaway worktree (since removed) the pinned suite `app/tests/test_research_working_tree_intake.py` passes 37/37 with the reconstructed file **and** 37/37 with the historical file swapped in. Both pass the same pinned behaviour.
- Differences (classification):
  - Structure: historical uses dataclasses `Summary/TaskSelection/TaskReport`, helpers `collect_batch_files`, `file_snapshot`, `ensure_directory`, `relative_posix_path`; reconstruction uses `scan_import_batch`, `choose_unique_candidate`, `SUPPORTED_TRANSFER_MODES` — **equivalent implementation (uncertain)**.
  - CLI: historical `--copy/--move/--symlink` and `--report-json`; reconstruction `--transfer-mode` and `--json`; common `--batch-dir --person-id --dry-run --replace-existing --force-task` — **behavioural difference (interface)**.
  - Status vocabulary: historical emits `missing_json`, `missing_textgrid`, `missing_wav_and_json`, `missing_wav_and_textgrid`, `conflict_multiple_*_candidates`, `conflict_existing_task_without_state`, `error_build_failed`; reconstruction emits `planned_rebuild`, `conflict_existing_working_tree`, `error_interview_transform` and generic prefixes — **behavioural difference (report surface)**; the reconstruction's own docstring admits unpinned names follow a naming scheme.
  - Docstring/provenance header (reconstruction only) — non-functional.
- **Behavioural equivalence is NOT established.** Core tested behaviour matches; CLI flags and status names differ, and no real-batch dry-run comparison was run (the historical script's `--dry-run` was not run on live batches to avoid touching real data). Do not treat the reconstruction as canonical for German intake until a representative dry-run comparison or a deliberate interface decision is made. The historical file is the only copy of the original behaviour — keep it.

## I. Task catalogs

- Local (all three, untracked): `data/config/research_player/{english,french,spanish}/{player_config.json, phenomena_presets.json (deprecated), task_catalogs/{text,wordlist}.json}` + `README.md`.
- Git: **none tracked** (`git ls-files data/config/research_player` = 0; ignored by `data/config/*`). Test fixtures in `app/tests/fixtures/runtime/data/config/research_player/{en,fr,es}` are tracked and are fixtures, not necessarily the operator catalogs.
- Recoverable: byte-identical copies in all 7 `exports/*` packages (SHA-256 verified for all 6 catalogs against 3 current packages); older plain-text catalogs in archive `praat_pipeline/catalogs`. Not in git, not in production verified, not on institutional storage.
- German: **no German research catalogs exist** in any scanned location (German appears only as Teaching content under `content/teaching/german/**`). German catalog content must be supplied from outside Cloud.

## J. Intake workbook(s)

- Current: `import/english_batch_20260618/promat_intake_english.xlsx`, `…french…`, `…spanish_batch_20260619/promat_intake_spanish.xlsx` (one per batch, retained in the batch dir). First-generation versions plus `promat_intake_template_alt.xlsx` in archive `informanten_intake_20260525/` (hashes differ from current).
- Not versioned in git (by design). The archive keeps normalized extracts (`secure_person_intake.json`, manifest `input_files`) and not the workbook itself for the June batches. To prove which workbook generated a batch: record the workbook SHA-256 in `archive_report.md`/manifest at import (not currently recorded) — input for the archive-provenance run.

## K. Toolchain (relevant only)

| Tool | Local version | Repo/provenance records |
|---|---|---|
| Python | 3.12.10 (system and `.venv`) | `app/pyproject.toml` (not re-checked) |
| ffmpeg | 8.1-full_build (gyan.dev) | **not recorded** in manifests |
| MFA | Docker image `mmcauliffe/montreal-forced-aligner:latest` (unpinned); `montreal_forced_aligner 3.3.9` in `.venv` but `mfa` CLI broken (`_kalpy` missing) | `mfa_version` is recorded per run (`run_text_mfa.py`); image tag/digest is not |
| Docker | 29.2.1; engine **not running** at audit time | – |
| Git | 2.53.0.windows.1 | – |
| Praat | `Praat.exe` (61 MB) in archive `praat_pipeline/` | version not recorded |
| praatio | 6.2.2 | pinned deps |

Flag: ffmpeg version and MFA image digest are absent from provenance.

## L. SSH/publishing interface (structure only; no connection made)

Scripts: `build_prod_upload_package.py` (builds package locally under `exports/`), `upload_prod_package.py` (rsync, falling back to tar-over-SSH; `--method auto|rsync|tar-ssh`; remote `checksums.sha256` verify), `publish_prod_release.py` (remote script over `ssh <user>@<host> bash -s`, optional DB payload upsert via `apply_prod_db_payload.py`), `scripts/deploy_prod.sh`. Defaults in repo: user `root`, remote data root `/srv/webapps_storage/promat/data` (uploads land in `…/incoming/<upload-id>`), remote app root `/srv/webapps/promat/app`. `--host` is a required argument (not stored in git); SSH keys/config are operator-local and were not inspected.

## M. Local database

A dev Postgres 15 container (`promat_auth_db`, bind mount `data/db/postgres_dev`, 70 MB) backs the auth/research-set model. It is **not required for intake** (importer writes files and a payload JSON; DB upsert is a separate prod step). Contents are not reproducible from intake inputs (accounts, owner-bound sets). Docker engine was not running so container/volume state could not be listed. Never treat it as cache.

## N. Docker and package-manager storage

Not measurable: Docker engine down (`docker system df` unreachable), so images/build cache/volumes are UNKNOWN. `.venv` 0.83 GB (active dev dependency). No `node_modules` found within depth 3. MFA model caches 0.79 GB (shared) + 3.1 GB (English legacy) are the only project-related tool caches.

## O. Local-vs-repository truth table

| Artifact | Git | Local | University | Production | Regenerable? | Intended source of truth |
|---|---|---|---|---|---|---|
| Application source | yes | yes | – | deployed | n/a | git `main` |
| Task catalogs | **no** | yes (+ packages) | no | yes (via packages) | no (content) | git (to be decided) / preservation root |
| Original recordings | no | archive (+drop-in dup) | **no** | no | no | preservation root |
| Source annotations (TextGrid/JSON) | no | archive (+drop-in dup) | no | no | partly (MFA) | preservation root |
| Intake workbook | no | `import/<batch>` | no | no | no | preservation root |
| Canonical session archive | no | `C:\dev\promat_data_archive` | no | no | no | preservation root |
| Derived web MP3 | no | `data/sessions`, archive `runtime/`, packages | no | yes | yes | archive/preservation |
| Runtime metadata | no | `data/sessions` | no | yes | yes (importer) | archive |
| PostgreSQL state | no | dev volume | no | prod DB | no | prod DB + backup |
| Upload packages | no | `exports/` | no | staged/promoted | yes | rebuilt from archive |
| Scholarly publication packages | none exist | none | no | no | n/a | not yet defined |

## P. Verified local prerequisites for next German intake

- Historical organizer equivalence: **NOT READY** (not established; see H)
- German task catalogs: **NOT READY** (none exist)
- German source-data location: **UNKNOWN** (nothing found locally)
- Intake workbook readiness: **UNKNOWN** (no German workbook; `template_alt.xlsx` exists in archive)
- Local disk space: **READY** (205.8 GB free on `C:`)
- Institutional preservation-root readiness: **NOT READY** (folder missing; not a German-intake blocker)
- Isolated dry-run location: **READY** (`tmp/`, gitignored; or a fresh `import/<batch>/`)
- Operator-only prerequisites: German recordings/workbook/catalogs, Docker engine running, MFA image availability for German, decision on organizer interface.

## Q. Cloud continuation package

Cloud now knows from this report: local storage topology and sizes; preservation-root plan and that `K:\Pronunciation_Matters` is absent; archive location/status (single copy, 65 sessions, manifests present); the measured duplication lifecycle; organizer comparison (hashes, test result, interface differences); catalog availability (untracked, recoverable from packages); workbook provenance gap; toolchain versions and the two missing provenance items; cleanup policy and runbook; German-readiness facts.

Still requires operator/local execution: creating/copying to `K:\Pronunciation_Matters` and checksum verification; testing `K:` writability/throughput; production SSH operations and confirming prod publish state; Docker/DB volume inspection; real German source-data intake; real-batch dry-run comparison of the two organizers; setting `PROMAT_LOCAL_ARCHIVE_ROOT`; deleting any preserved local originals; deleting the English legacy `.mfa_cache`.
