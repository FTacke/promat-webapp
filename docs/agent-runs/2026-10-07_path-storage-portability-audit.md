# Path, Storage and Portability Audit — 2026-10-07

Non-normative audit and migration plan. Binding rules stay in `docs/spec/platform-data-files.md`. This run changed nothing except adding this file: no move, no rename, no config change, no data copy, nothing written to `K:`. CO.RA.PAN (`C:\dev\panhispanic_media_corpora\corapan`) was read only.

Builds on, and does not repeat, `docs/reports/2026-10-05_local-storage-audit.md` (sizes, duplication lifecycle) and the spec sections "Local Archive Filesystem" and "Local Storage Roles And Preservation Root". No participant IDs and no secret values are recorded here.

## A. Executive Result

```text
STATUS = PASS

CURRENT_STATE_AUDITED
TARGET_ARCHITECTURE_DECIDED
MIGRATION_PLAN_READY
PHYSICAL_MOVE_NOT_STARTED
NO_MAJOR_MIGRATION_REQUIRED
```

- The path architecture is already portable. Repo-relative resources resolve from `__file__`, machine roots come from named environment variables, and no long-lived dataset stores an absolute machine path.
- There is exactly one operative hard-coded machine path, and it is dangerous for a move: the fallback `C:\dev\promat_data_archive` in two scripts, in force today because `PROMAT_LOCAL_ARCHIVE_ROOT` is unset. After a move, the next intake would silently create a second archive at the old location.
- The largest real risk is not layout but preservation: all original recordings exist on one local disk only. `K:\Pronunciation_Matters` still does not exist.
- Decision: no new roots, no workspace root, no CO.RA.PAN registry. Four small repairs, then an optional, cheap relocation under one project folder.

Recommended order: repairs (H1–H4) → institutional preservation copy → relocation. The relocation has no functional benefit by itself; it is justified only by one project folder as backup/overview scope, a checkout name that matches the remote (`promat-webapp`), and consistency with CO.RA.PAN. It must not delay preservation.

## B. Current State

### Directory structure and sizes (measured 2026-10-07)

| Location | Files | Size | Content |
|---|---|---|---|
| `C:\dev\promat` (total) | ≈ 80,000 | ≈ 19.2 GB | checkout plus gitignored operative data |
| ├ tracked in Git | 838 | small (largest file 423 KB) | code, templates, static, `content/`, `docs/` |
| ├ `scripts/research_data_intake/import/` | 19,704 | 12.8 GB | 3 intake batches incl. `working/`, legacy `.mfa_cache`, current workbooks |
| ├ `scripts/research_data_intake/exports/` | 22,562 | 2.3 GB | 7 prod upload packages |
| ├ `scripts/research_data_intake/.mfa_cache/` | 2,080 | 0.8 GB | shared MFA models (`es`, `fr`) |
| ├ `tmp/` | 9,249 | 1.36 GB | `ui-qa/` 0.97 GB (incl. a Playwright venv), MFA test dirs, import check, helper scripts |
| ├ `data/sessions/` | 8,547 | 0.96 GB | runtime MP3/JSON (en, fr, es) |
| ├ `data/db/postgres_dev/` | 1,384 | 70 MB | dev PostgreSQL bind mount |
| ├ `data/config/` | 14 | 0.1 MB | untracked research-player catalogs |
| ├ `.venv/` | 22,197 | 0.86 GB | Python 3.12.10 venv |
| └ `secure/`, `logs/` | 1 each | ~0 | placeholders; `public/` does not exist |
| `C:\dev\promat_data_archive` (total) | 9,386 | 7.09 GB | not a Git repo |
| ├ `sessions/{en,es,fr}/` | 9,207 | 7.03 GB | 65 session archives (10 / 24 / 31): 312 WAV 6.05 GB, 8,324 MP3 0.95 GB, 108 TextGrid |
| ├ `batches/` | 30 | 0.2 MB | 6 batch archives (reports, `checksums.sha256`, `import_payload.json`) |
| ├ `fixity/baseline/` | 136 | 0.9 MB | additive SHA-256 baselines |
| ├ `praat_pipeline/` | 8 | 60.7 MB | legacy pipeline incl. `Praat.exe` |
| └ `informanten_intake_20260525/` | 5 | 0.4 MB | first-generation workbooks |

No symlinks or junctions in either root. Free space: `C:` 185 GB, `K:` 196 GB.

### Git

- Remote `origin` = `https://github.com/FTacke/promat-webapp.git`; branch `feature/run4-publication-metadata`, HEAD `8f328f8`, identical to `origin/main`; working tree clean.
- No stashes, one worktree, no submodules, no hooks, no unpushed commits on any local branch. Local `main` is 28 commits behind `origin/main` (ref only).
- No data that does not belong in Git is tracked: under `data/`, `secure/` only `.gitkeep` files. The research data inside the checkout is all gitignored.

### Active dependencies and external processes

- No running process, Windows service or scheduled task references either path. Nothing listens on 8000 or 54321.
- Docker engine was not running, so the state of container `promat_auth_db` and the dev database content could not be inspected.
- `PROMAT_*` variables are unset at process, user and machine level. `PROMAT_RUNTIME_ROOT` / `PROMAT_PUBLIC_ROOT` are derived per start by `app/scripts/dev-start.ps1` from the script location.
- No code loads a `.env` file (no `dotenv` use anywhere). `app/.env.example` is documentation only; its `PROMAT_LOCAL_ARCHIVE_ROOT` line has no effect.
- Path-keyed tool state outside the repo: VS Code workspace storage (`file:///c%3A/dev/promat`) and the Claude Code project directory `~\.claude\projects\c--dev-promat` (holds the persistent memory).
- `K:` is reachable; `K:\Pronunciation_Matters` does not exist (creation was denied on 2026-10-05). No `preservation/receipts` exist in the archive: every unit is at best `PRESERVATION_PENDING`.

## C. Path Findings

Classes: A = scientific / identity-critical, B = active operative, C = configuration / migration / tooling, D = historical / documentation.

### A — none

Checked and clean (relative POSIX paths or bare filenames only):

- archive `metadata/archive_manifest.json` (`raw/interview.wav`, `source/…`, `alignment_source/…`), `checksums.sha256`, batch reports and `import_payload.json`;
- runtime `data/sessions/**/metadata.json` and `alignment/*.json` (`derived/wordlist.mp3`, …);
- upload-package `manifest.json` and payloads;
- `fixity/baseline/*`;
- database columns `research_people.consent_file` / `questionnaire_file` (bare filenames in the secure intake JSON; the live dev DB itself was not queried, see gate G6).

Identity is carried by `person_id`, `session_id`, `item_id`, batch name and SHA-256, never by a path. Nothing persisted needs migrating, so no legacy resolver is needed.

### B — active operative (2 lines, 1 finding)

| Location | Finding |
|---|---|
| `scripts/research_data_intake/intake_storage.py:21` | `DEFAULT_LOCAL_ARCHIVE_ROOT = Path(r"C:\dev\promat_data_archive")`, used by `get_local_archive_root()` (line 82) whenever the variable is unset — the current state of this machine |
| `scripts/storage_inventory.py:29` | same literal, same fallback |

Effect after moving the archive: the importer recreates `C:\dev\promat_data_archive` and writes new sessions there. That is exactly the competing second data world this audit must prevent.

### C — configuration and tooling

| Location | Finding |
|---|---|
| `.vscode/tasks.json:7,20,35` | `c:/dev/promat/.venv/Scripts/python.exe` |
| `app/.vscode/tasks.json:7,9` | same, plus a `tmp/ui-qa/2026-04-13-…` script path |
| `.claude/settings.json:5,7,8` | allowlist entries with `/c/dev/promat/public` and `C:\dev\promat_data_archive` |
| `scripts/qa/capture_qa.ps1:20` | `$outputDir = "C:\dev\promat\tmp\ui-qa\…"` |
| `app/.env.example:14` | `PROMAT_LOCAL_ARCHIVE_ROOT=C:\dev\promat_data_archive` (example value) |
| `scripts/qa/responsive_smoke.py:180` | `Path("tmp/ui-qa")` depends on the working directory |
| `.venv/pyvenv.cfg` and `.venv/Scripts/*` | absolute paths baked in; a venv does not survive a move |
| `docker-compose.dev-postgres.yml:12` | bind mount `./data/db/postgres_dev`; an existing container keeps the old absolute mount, and the compose project name derives from the directory name |
| `import/*/working/**/mfa_state.json`, `mfa_manifest.json` (54 + 54 files, 369 values), `.intake_state.json` (3) | absolute paths in batch-local working state; regenerable. Whether MFA reuse survives a move is unverified (gate G5) |
| `tmp/*.cmd`, `tmp/run_es_en_runtime_audit.ps1` | one-off helpers with `C:\dev\promat\…` |

Working-directory audit of active code: all repo roots derive from `Path(__file__).resolve().parents[n]` (`runtime_paths.py:30`, `config/__init__.py:134`, `__init__.py:201`, every `REPO_ROOT` in `scripts/`). `public_content.py:31` uses a relative `content/legal/…` but resolves it by walking parents (line 724). `Path.cwd()` in the intake CLIs only anchors relative command-line arguments. No finding.

### D — historical / documentation

- `scripts/research_data_intake/README.md` (lines 16, 181–249) and `validate_research_config.py:11`: example commands with `c:/dev/promat/…`.
- `docs/**` (spec line 618 "Default local example", runbooks, reports, about 400 run logs).
- Archive `praat_pipeline/praat_scripts/label_wortliste_from_sounding.praat:4-5`: `C:/dev/promat-data/…`, a location that predates even the current archive. Historical evidence; leave untouched.

## D. Data and Storage Classification

| Data | Location today | Class | Written by / read by | Regenerable | Git | Second copy | Stable identity | Role |
|---|---|---|---|---|---|---|---|---|
| Original and processed WAV, TextGrid, Amberscript JSON | archive `sessions/*/*/{raw,source,alignment_source}` | SOURCE / AUTHORITATIVE | importer / derivation tooling | no | no | only byte-identical drop-ins on the same disk | `session_id` + SHA-256 | authoritative, **not preserved** |
| Secure person intake, consent references | archive `sessions/*/*/secure` | SOURCE (personal data) | importer / operator | no | no | none | `person_id` | authoritative, not preserved |
| Archive manifests, batch reports, fixity baselines | archive `metadata/`, `batches/`, `fixity/` | SOURCE (provenance) | importer, `archive_preservation.py` | no | no | none | unit name | authoritative |
| Current intake workbooks (3) | `import/<batch>/*.xlsx` **inside the checkout** | SOURCE / UNIQUE | operator / importer | no | no (ignored) | none | batch name | authoritative, at risk |
| First-generation workbooks, Praat pipeline | archive `informanten_intake_20260525/`, `praat_pipeline/` | HISTORICAL | – | no | no | none | – | historical; not covered by preservation tooling |
| Research-player catalogs | `data/config/research_player/**` | SOURCE / UNIQUE | operator / app + intake | no | no (ignored) | copies in upload packages | item IDs | authoritative, at risk |
| Runtime sessions (MP3, JSON) | `data/sessions/**`; mirrored in archive `runtime/` | DERIVED / REGENERABLE | importer / app | yes | no | archive, packages, prod | `session_id` | operative working copy |
| Drop-in WAVs and `working/` | `import/<batch>/` | working copy of SOURCE + DERIVED | organizer, MFA / importer | mostly | no | archive | – | working copy, cleanup-eligible only after preservation |
| Upload packages | `exports/*` | EXPORT / SPOOL | package builder / upload | yes | no | prod | upload id | spool |
| Dev PostgreSQL | `data/db/postgres_dev` | DATABASE (dev) | Docker / app | no (accounts, sets), low value | no | none | – | operative, never cache |
| Prod PostgreSQL | server | DATABASE | app | no | no | server backups per runbook | – | authoritative for accounts and sets; out of scope here |
| Teaching content and media | `content/teaching/**` | SOURCE (editorial) | editors / app | no | **yes** | GitHub | `resource_id` | authoritative in Git |
| Templates, static, fixtures, docs | `app/**`, `docs/**` | SOURCE (code) | – | – | yes | GitHub | – | Git |
| MFA model cache, `.venv`, tool caches | `.mfa_cache/`, `.venv/` | CACHE | tools | yes | no | – | – | cache |
| `tmp/` | `tmp/` | RUNTIME / temporary | QA runs | yes | no | – | – | temporary |

No user uploads exist: the app writes only database rows and logs. The webapp never reads the archive; only intake tooling does.

Functionally, `promat_data_archive` is the **local working archive and currently the only authoritative copy** of the research sources. It is neither a backup nor preservation. The name is accurate enough and is bound into the spec, the variable name and the runbooks; renaming it would be cosmetic. Keep it.

## E. Target Architecture

```text
C:\dev\pronunciation_matters\        plain folder, never a Git repository
├─ promat_webapp\                    Git checkout (remote promat-webapp); also PROMAT_RUNTIME_ROOT in dev
│  ├─ app\ content\ docs\ infra\ scripts\      versioned
│  ├─ data\{config,sessions,db}\               gitignored runtime, unchanged
│  ├─ scripts\research_data_intake\{import,exports,.mfa_cache}\   gitignored, unchanged
│  └─ tmp\ logs\ secure\ .venv\
└─ promat_data_archive\              PROMAT_LOCAL_ARCHIVE_ROOT, layout unchanged

K:\Pronunciation_Matters\            PROMAT_PRESERVATION_ROOT (later the dedicated HRZ share)
```

Decisions:

- **Umbrella folder:** yes, as the last and optional step. Name `pronunciation_matters`.
- **Checkout name:** `promat_webapp`, matching the remote.
- **Archive:** moves under the umbrella with its name and internal layout unchanged.
- **`promat_workspace`: rejected.** The app needs no third root. `PROMAT_RUNTIME_ROOT` already separates runtime data logically; in dev it points at the checkout, in prod at `/app`. A separate workspace would require moving the spec-bound batch root `scripts/research_data_intake/import/` and would only relocate regenerable data. The one real hazard of data in the checkout — unique workbooks and catalogs in gitignored folders, which a `git clean -fdx` would destroy — is solved by preserving those files (section M), not by a new root.
- **Not adopted from CO.RA.PAN:** root registry, `root_id + rel` references (one data root; plain relative paths already in use), legacy resolver (nothing to resolve), outage spool, retention classes, storage-target layer, relocation script.
- **Adopted from CO.RA.PAN:** fail closed on an unset required root; a small hard-coded-path ratchet; one relocation test with spaces and `ñ`; measure path length before nesting; guards test facts, not directory names.

## F. Root Contract

No new roots. One contract change (archive root becomes required for intake).

| Root | Purpose and content | Configured by | Access | Authoritative | Preservation |
|---|---|---|---|---|---|
| repo (derived) | code, templates, static, `content/`, fixtures | `Path(__file__)`; never configured | read; Git writes | yes, via Git | GitHub |
| `PROMAT_RUNTIME_ROOT` | `data/{config,sessions}`, `logs/` | env; dev default from `dev-start.ps1` (checkout), prod `/app`; unset = startup error | app reads `data/` and writes `logs/`; intake writes `data/sessions` | catalogs yes; sessions no (derived) | catalogs yes, sessions no |
| `PROMAT_PUBLIC_ROOT` | released public media (currently empty) | env; same defaults; unset = startup error | app reads | no | no |
| `PROMAT_TEACHING_CONTENT_ROOT` | optional override of `content/teaching` | env, optional | app reads | no (Git is) | – |
| `PROMAT_LOCAL_ARCHIVE_ROOT` | session and batch archives, fixity | env or `--archive-root`; **to become required, no built-in default** | intake tooling only; never the webapp | yes, until a unit is `PRESERVED` | source of the preservation copy |
| `PROMAT_PRESERVATION_ROOT` | verified institutional copy, identified by `PRESERVATION_ROOT.json` | env or `--preservation-root`; no default (already the rule) | `archive_preservation.py`, `storage_inventory.py` only | yes, once verified | yes |

Configuration mechanism for the two intake roots: one gitignored `.env` at the repo root, read by one small loader in the intake tooling that never overrides the process environment; names and placeholders in the versioned `.env.example`. No host detection, no default.

## G. Migration Mapping

```text
C:\dev\promat               → C:\dev\pronunciation_matters\promat_webapp
C:\dev\promat_data_archive  → C:\dev\pronunciation_matters\promat_data_archive
```

Both are same-volume renames (atomic, no copy, no re-hash needed beyond the fixity check). Nothing inside either tree moves. Nothing in persisted data changes.

## H. Dependencies to Update

Repairs before any move (each is small; H1 needs a spec edit in the same run):

1. **H1 archive root fails closed.** Remove both `DEFAULT_LOCAL_ARCHIVE_ROOT` literals (`intake_storage.py:21`, `storage_inventory.py:29`); unset means a named error. Update `docs/spec/platform-data-files.md` line 664 (which currently states the fallback is kept) and line 618, plus `docs/runbooks/archive-preservation.md`.
2. **H2 `.env` loading for intake roots** as in section F; move `PROMAT_LOCAL_ARCHIVE_ROOT` in `.env.example` to a placeholder value.
3. **H3 hard-coded-path ratchet** (section "Ratchet" below) in `scripts/ci_governance_checks.py`.
4. **H4 relocation test** (section J, part 1) in `app/tests/`.
5. `.vscode/tasks.json`, `app/.vscode/tasks.json`: use `${workspaceFolder}`; drop the stale `tmp` task.
6. `scripts/qa/capture_qa.ps1:20`: derive from `$PSScriptRoot`. `scripts/qa/responsive_smoke.py:180`: derive from the repo root.
7. `scripts/research_data_intake/README.md`, `validate_research_config.py:11`: relative example commands.

At move time (operator, local):

8. `docker compose -f docker-compose.dev-postgres.yml down` before; `dev-start.ps1` recreates the container afterwards from the new location (database files travel with the checkout).
9. Recreate `.venv` (delete, `python -m venv`, reinstall). The Playwright venv under `tmp/ui-qa/…/pwenv` is disposable.
10. `.claude/settings.json` allowlist entries (operator decision; stale entries are harmless).
11. Copy `~\.claude\projects\c--dev-promat\memory\` to the new project key so the persistent memory survives; reopen the folder in VS Code (workspace state starts fresh).
12. Set `PROMAT_LOCAL_ARCHIVE_ROOT` (and later `PROMAT_PRESERVATION_ROOT`) in the new `.env`.

Not to be changed: historical docs and run logs, the Praat script in the archive, existing manifests, `tmp/` helpers (delete rather than fix).

### Hardcoded-Path Ratchet (design for H3)

One more guard in the existing `scripts/ci_governance_checks.py` (already in CI), no new tool:

- **Scope (strict):** tracked files under `app/src`, `app/scripts`, `scripts`, `infra`, `.github/workflows`, `.vscode`, plus `docker-compose.dev-postgres.yml` and `app/.env.example`.
- **Exempt:** `docs/`, `app/tests/`, `content/`, `*.md`.
- **Python files:** inspect string tokens only (`tokenize`), skipping comments and docstrings, so usage examples do not trip it.
- **Patterns:** Windows drive plus `dev|Users|temp`, `K:\`, `\\server\share`, `/home/<name>/`, and the literal `promat_data_archive` as a path component. Not hits: `${VAR}`, `$PSScriptRoot`, URLs, and the container and server paths that are the deployment contract (`/app/…`, `/srv/webapps…`, `/usr/sbin/sendmail`), held in a short explicit allowlist.
- **Escape:** an inline `path-literal: <reason>` marker on the same line.
- **Baseline:** empty after H1 and H5–H7. No baseline file, no shrink logic.

## I. Migration Gates

All must be green before the physical move:

- **G1** H1–H7 merged to `main`; CI release gate green.
- **G2** Full `pytest` green in the old location on that commit (baseline for comparison).
- **G3** Ratchet reports zero findings.
- **G4** Relocation canary (section J) passes.
- **G5** No intake batch in progress. Decision recorded on whether MFA working state must survive (if yes, test MFA reuse on one person in the canary copy; if no, accept a possible MFA rerun).
- **G6** Docker engine started once: `promat_auth_db` state known, dev database confirmed disposable or dumped; `rg` over a `pg_dump` shows no `C:\` values.
- **G7** `archive_preservation.py status` and a fixity verification of the archive against baselines/manifests are clean, with the report kept. Strongly preferred: preservation copy to `K:` verified first (section M). If `K:` is still blocked, the move may proceed only as an atomic rename, never as copy-and-delete.
- **G8** Git clean, no unpushed commits, no stash, no running dev server, VS Code and other handles on both folders closed.
- **G9** File count and total bytes of both trees recorded.

## J. Relocation Canary

**Part 1 — permanent test (H4), deterministic, runs in CI.** In `tmp_path / "Pronunciation Matters ñ"`:

1. copy the tracked fixture runtime `app/tests/fixtures/runtime` to `<base>/runtime ñ/`, create an empty `<base>/public`, set `PROMAT_RUNTIME_ROOT` / `PROMAT_PUBLIC_ROOT`, change the working directory to an unrelated folder;
2. build the app with the existing `real_app_factory` (SQLite); assert a public page, a `/static/` asset, a research design page, and one player audio response for a fixture session all return 200;
3. write a small synthetic archive unit to `<base>/archive a/` through `intake_storage`, move it to `<base>/archive b ñ/`, repoint `PROMAT_LOCAL_ARCHIVE_ROOT`, and assert manifest, `checksums.sha256` and fixity verification are unchanged;
4. assert that with `PROMAT_LOCAL_ARCHIVE_ROOT` unset the archive getter raises and no directory is created.

**Part 2 — one-off operator canary before the move.** `git worktree add "C:\temp\Pronunciation Matters ñ\promat_webapp" <commit>` (a clean checkout without operator data), fresh venv there, then: full `pytest`; `scripts/ci_governance_checks.py`; `scripts/validate_teaching_content.py`; `app/scripts/trace_runtime_paths.py` with output containing no `C:\dev\promat`; start the app against the fixture runtime and load one page. Remove the worktree afterwards. No production data is copied.

## K. Rollback

Because both steps are same-volume renames and no persisted data changes:

1. stop the dev server, `docker compose down`;
2. rename both folders back to `C:\dev\promat` and `C:\dev\promat_data_archive`;
3. restore the previous `.env` (or unset the variables) and recreate `.venv`;
4. `dev-start.ps1`, then compare file count and bytes with G9.

The code repairs H1–H7 are location-independent and stay. If a rename fails halfway (locked handle), nothing is partially copied; close the handle and retry or rename back. No junction is left behind in either direction.

## L. Post-Move Validation

1. File count and bytes of both trees equal G9.
2. `git status` clean, `git fsck` passes, `git remote -v` unchanged.
3. Full `pytest` green; governance checks (with ratchet) green.
4. `dev-start.ps1` brings up Postgres and the app; log line "Resolved runtime paths" shows only new paths; login works; one player audio plays for one session per language.
5. `scripts/storage_inventory.py` reports the archive root from `PROMAT_LOCAL_ARCHIVE_ROOT` with 65 sessions and 6 batches.
6. `archive_preservation.py status` gives the same result as in G7.
7. `import_batch_to_production.py … --dry-run` on one existing batch resolves the new archive path.
8. `C:\dev\promat` and `C:\dev\promat_data_archive` do not exist, and still do not exist after step 7.

## M. Storage and Preservation Plan

| Data | Stays local | Institutional storage | Status there |
|---|---|---|---|
| Archive units `sessions/`, `batches/` (WAV, annotations, secure, manifests, fixity) | yes, as working archive | yes | **authoritative and preserved** once verified by full SHA-256 |
| Current intake workbooks | in the batch | yes, inside the batch unit (`secure/workbook/`) | preserved; three June batches predate this and need an additive preservation step |
| Research-player catalogs | `data/config` | yes | preserved; open decision whether Git becomes their home instead |
| `informanten_intake_20260525/`, `praat_pipeline/` | yes | yes, as a one-time historical deposit | historical; today outside the tooling scope |
| Runtime sessions, upload packages, MFA corpus/output, caches, `.venv`, `tmp/` | yes | no | regenerable |
| Dev database | yes | no | disposable |
| Prod database | server | no (server backup runbook) | backup, separate process |
| Code, Teaching content | yes | no | Git / GitHub |

Rules that prevent double authority (all already in the spec; restated as the decision):

- Flow is one-directional: intake → local archive → verified preservation copy. Intake never writes to the preservation root, and `PROMAT_LOCAL_ARCHIVE_ROOT` is never pointed at it.
- A unit is authoritative locally until it is `PRESERVED`; from then on the preservation copy is the authority and the local unit is a working copy that may be removed only when `LOCAL_CLEANUP_ELIGIBLE`.
- The preservation root is identified by `PRESERVATION_ROOT.json` (`root_id`), not by `K:`. Moving from `K:\Pronunciation_Matters` to the planned dedicated share (CephFS/SMB, 2 TB, tape, offline second copy) is a verified copy plus one configuration change.
- Preservation is not backup. Tape and the offline second copy of the institutional share are the backup of the preserved data; a second folder on `C:` or in a sync client is neither.
- Drop-in copies under `import/` are working copies and never a reason to skip preservation.

Next concrete step, independent of the relocation: obtain write access to `K:\Pronunciation_Matters` (blocked since 2026-10-05), then run the existing `archive_preservation.py copy` → verify. Until then about 6 GB of unrepeatable recordings exist on one disk.

## N. Cleanup After Successful Migration

- **Delete:** nothing needs deleting, since renames leave no old tree. If the old folder names reappear, treat it as a defect (H1 regression), not as debris.
- **Delete (hygiene, operator decision, unrelated to the move):** `tmp/ui-qa/**` (0.97 GB), `tmp/mfa-english-*`, `tmp/production-import-check-*`, `tmp/*.cmd` and other helpers with old paths, the old `.venv` (recreated anyway), the old Claude project directory after its memory was copied.
- **Keep deliberately:** the G7/G9 reports for one release cycle under `tmp/preservation-reports/`; `import/`, `exports/` and the local archive until units are `LOCAL_CLEANUP_ELIGIBLE`.
- **Never rewritten:** docs and run logs that mention `C:\dev\promat`, the Praat script, existing manifests.

## Windows Portability

| Tree | Longest path today | After move | Over 240 |
|---|---|---|---|
| tracked files | 121 | 150 (+29) | 0 |
| `import/` | 174 | 203 | 0 |
| `tmp/` | 175 | 204 | 0 |
| `exports/` | 167 | 196 | 0 |
| archive | 92 | 113 (+21) | 0 |

No path exceeds 240 before or after. `LongPathsEnabled` is already 1 (read only, not changed); Git `core.longpaths` is unset and not needed. File names: no non-ASCII names in any data tree; two tracked docs contain spaces. The canary covers spaces and `ñ` in the root, which the real target does not use.

## Not Verified

- Docker engine was down: container state and dev database content (G6).
- Whether MFA reuse survives changed absolute paths in `mfa_state.json` (G5).
- The test suite was not run in this audit; G2 establishes the baseline.
- `fixity/baseline` holds 136 files (68 units) against 71 archive units; whether the remaining three are covered by complete unit manifests was not checked (G7 answers it).
- Production server paths were not inspected. The spec names `/srv/webapps_storage/promat/data` for uploads while `infra/docker-compose.prod.yml` mounts `/srv/webapps/promat/data`; whether these are the same location is an operator fact outside this audit.
- CO.RA.PAN findings come from reading its repository; none of its tests or canaries were run.
