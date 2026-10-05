# Archive Provenance & Institutional Preservation Foundation

Datum: 2026-10-05

Branch: `claude/archive-provenance-preservation` (from `claude/storage-preservation-architecture`). Nothing was merged, deployed, or changed in production; no `K:` access, no SSH, no existing archive content touched.

## Baseline

- Branch base: Production Safety Foundation + architecture plan. Canonical suite before the run: 836 passed, 7 `data`-marked deselected.
- Missing inputs named in the task do not exist on any branch of this repository: `docs/reports/2026-10-05_local-storage-audit.md`, `docs/runbooks/local-storage-hygiene.md`, `scripts/storage_inventory.py`, `docs/agent-runs/2026-10-05_local-storage-audit.md`. Facts from the task text were used instead; the cleanup report is a documented JSON schema those tools can consume later.

## Implementation

| File | Change |
|---|---|
| `scripts/research_data_intake/fixity.py` | new: `checksums.sha256` read/write/verify (existing sha256sum format) |
| `scripts/research_data_intake/provenance.py` | new: git revision (fallback `unknown`), tool versions, workbook/catalog records |
| `scripts/research_data_intake/preservation.py` | new: root abstraction, verified copy, receipts, state model, cleanup report |
| `scripts/research_data_intake/archive_preservation.py` | new: operator CLI (`baseline`, `copy`, `verify`, `status`, `cleanup-report`) |
| `scripts/research_data_intake/intake_storage.py` | additive: per-file provenance, `provenance` block, `metadata/checksums.sha256`, batch workbook + `batch_provenance.json` |
| `scripts/research_data_intake/import_batch_to_production.py` | minimal wiring: real `importer_version`, run provenance, workbook path |
| `app/tests/test_archive_preservation.py` | 46 new tests (temp dirs only) |
| `docs/spec/platform-data-files.md`, `docs/runbooks/archive-preservation.md`, `backup-and-restore.md`, plan status note | docs |

## Compatibility

Intake behaviour is unchanged: source formats, filename conventions, import order, staging, SSH publication, atomic publication, IDs, server paths and the DB integration are not touched. Manifests only gained fields; `validate_archive_tree` still accepts the layout (the new fixity file lives in `metadata/`). `test_research_intake_storage.py` and `test_research_working_tree_intake.py` pass unmodified. Neither organizer was touched; the English `.mfa_cache` is not referenced.

## Provenance model

Per input file: original filename, normalized relative source, canonical name, task, role, size, sha256, batch id, session id, intake timestamp. Per runtime file: `derived_from`. Block: git revision, ffmpeg/MFA versions, workbook and catalog records. The workbook is copied to `batches/{batch}/secure/workbook/` (secure class) and recorded in `batch_provenance.json`. See the spec section "Archive provenance and fixity".

## Fixity model

One format (`checksums.sha256`, relative POSIX paths). Session archives: `metadata/checksums.sha256` (refreshed after the secure export, which is written later). Batches: `checksums.sha256`. Existing archives: additive baseline under `fixity/baseline/`; no manifest or archived file is rewritten; unreadable files prevent a baseline instead of producing a partial one.

## Institutional-copy tooling

Root from `PROMAT_PRESERVATION_ROOT` / `--preservation-root`, never defaulted, no drive letters in code (tested). Marker `PRESERVATION_ROOT.json` with `root_id`. Copy: verify source → `*.partial` → read-back → atomic rename; conflicts never overwritten; resumable; dry-run default; JSON + Markdown reports; extended-length path helper for Windows (pure-function tested only).

## Preservation states

`ACTIVE_LOCAL` → `PRESERVATION_PENDING` → `PRESERVED` → `LOCAL_CLEANUP_ELIGIBLE`, each with evidence and reasons. Receipts bind a unit to root id and manifest hash; a changed unit or a changed root returns it to pending; `--exclude-secure` copies never reach PRESERVED; cleanup eligibility needs a fresh full destination verification.

## Cleanup eligibility

`cleanup-report` (`promat.cleanup_eligibility.v1`, `deletes_anything: false`) lists eligible units and, for given local directories, files whose SHA-256 duplicates fully verified preserved content. A test asserts no archive, working, or destination file changes and that the modules contain no deletion calls beyond their own `.partial`/probe files.

## Existing archive strategy

Baseline only; no migration, renaming, or regeneration. Baselines describe today's content, not historical correctness.

## Validation

- New tests: 46 passed. Canonical suite: 882 passed, 7 deselected. `ruff check .` clean; `scripts/ci_governance_checks.py` passes.
- Not tested: Windows, `K:`, real MFA/ffmpeg version output, an end-to-end `import_batch_to_production.py` run (needs MFA, ffmpeg and Postgres); the wiring is covered through the storage functions it calls.

## Operator procedure

`docs/runbooks/archive-preservation.md` (11 steps, PowerShell, to be run locally).

## Deferred items

German catalogs; German source-data intake; organizer behavioural equivalence; DOI/publication exporter; consent-withdrawal implementation; catalog governance beyond provenance; Windows runtime verification of the long-path handling; integration into `storage_inventory.py` once it exists in this repository.
