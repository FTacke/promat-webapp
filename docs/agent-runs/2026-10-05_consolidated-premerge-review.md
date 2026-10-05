# Consolidated pre-merge review

Datum: 2026-10-05

## Reviewed state

- Review target: `origin/local/preservation-activation` at `3c0bb8c` (it contains `origin/claude/storage-preservation-consolidated` `ce3340c` and every earlier Claude branch; nothing is unique to the other branches). `origin/main` is `5512451` (the local-storage audit commit) and is an ancestor of the target; there is nothing on `main` that the target lacks.
- Branch topology (commits ahead of `origin/main`): 14 = Production Safety Foundation + re-entry audit + architecture plan + archive provenance/preservation tooling + local-storage reconciliation merge + the local activation run (`3c0bb8c`: cleanup-report Windows fix, run report) + this review commit.
- Local-run evidence (`2026-10-05_preservation-activation-organizer-equivalence.md`, audit report) was kept unchanged and is treated as authoritative.
- Not merged to `main`, not deployed, no production, SSH, `K:` or institutional-storage access; no scientific data touched.

## Diff scope against `origin/main`

74 files, +6280/−372: CI/deploy workflows, backup/restore scripts, runtime config checks, auth/mail link, research profile and label escaping, templates, dependencies, legal content move, intake/archive code (additive provenance/fixity), preservation CLI, storage inventory, reconstructed organizer, tests and docs. Application behaviour that can change in production is limited to the items in "Production-safety result".

## Findings

| Severity | Finding | Disposition |
|---|---|---|
| Critical | none | – |
| High (operator gate, not a code defect) | Production now refuses to start when `JWT_SECRET_KEY`/`FLASK_SECRET_KEY` are empty or `__…__` placeholders, or `PROMAT_PUBLIC_BASE_URL` is missing, placeholder or not `https://`. If the real server `passwords.env` still has a template value the first deploy fails. | Mitigated: `deploy_prod.sh` validates the configuration with the new image in a throw-away container *before* touching running services, so a bad value aborts the deploy with the old site still serving. Operator must still check the three values before merging (runbook `deploy-and-rollback.md`). |
| Medium | Explicitly requested unknown `--person-id` succeeded in the reconstructed organizer (historical organizer failed). | **Fixed** (see below). |
| Medium (known limitation, fail-safe) | Re-importing an already preserved session changes its archive files; the unit returns to `PRESERVATION_PENDING` and `copy` reports `conflict_destination_mismatch` instead of overwriting. Updating a preserved unit in the root is an explicit operator decision (no tool does it). | Documented here; no change (never overwriting is the required behaviour). |
| Medium (operator-only) | Content outside archive units (`praat_pipeline/`, first-generation workbooks, current batch workbooks, task catalogs, historical organizer, dev DB) is not covered by the unit copy. | Already reported by the tool (`archive_root_entries_not_covered_by_unit_copy`, `not_covered`) and listed in the activation report; stays an operator gate. |
| Low | `actionlint` warns about the custom runner label `promat-prod`; identical label exists on `origin/main`. | Pre-existing, unchanged. |
| Low | Quick (size-only) status can show `PRESERVED` after same-size corruption; only a full `verify` can grant `LOCAL_CLEANUP_ELIGIBLE`. | By design, tested. |

No regression of working intake behaviour was found: `intake_storage.py` and `import_batch_to_production.py` changes are additive (extra manifest fields, extra files, `importer_version` string); the intake/storage tests pass unmodified.

## Fixes made

`scripts/research_data_intake/organize_batch_working_tree.py`: when `--person-id` values were requested and a requested ID has no file in the batch, the report gets one entry `status: error_unknown_person` (`summary.errors` ≥ 1, CLI exit 1); no state and no working directory is created for it. Unfiltered runs and known IDs are unaffected (request matching stays case-insensitive). Nothing else in the organizer, no CLI/label harmonisation, and the historical organizer is neither used nor required. The importer is unaffected: it passes only its own `--person-id` filter and merely records the error count in run notes. Tests: `test_organize_batch_working_tree_fails_clearly_for_explicitly_requested_unknown_person`, `…known_person_request_is_unchanged_by_unknown_person_check`, `…unfiltered_run_never_reports_unknown_person`. Spec organizer note updated.

## Storage-root invariant

`PROMAT_LOCAL_ARCHIVE_ROOT` (or the built-in fallback) is the only archive root intake reads (`intake_storage.get_local_archive_root`). `PROMAT_PRESERVATION_ROOT` appears only in `preservation.py`, `archive_preservation.py` and `storage_inventory.py`. `test_intake_never_reads_the_preservation_root` scans every other intake module for the name and for `import preservation`, and asserts that setting the variable does not change `get_local_archive_root()`. Result: holds, test passes.

## Organizer edge-case result

Fixed and tested (above). All 37 pre-existing pinned organizer tests still pass; the real-batch byte-identical success-path evidence from the local run is unaffected because the change only fires for an explicit ID absent from the inventory.

## Preservation review (code)

Reviewed against the list in the task; no concrete defect found beyond the already-fixed `.ark`/WinError 1920 case (`_candidate_files`, regression test present):

- Baselines additive: written only under `fixity/baseline/`; existing baselines and manifests are never rewritten, drift is reported; unreadable files prevent a partial baseline.
- Source immutability: copy and verify only read the local archive; writes go to the destination, `preservation/receipts/` and `fixity/`.
- Secure data: complete scope includes `secure/` (the dry-run on the real archive reported scope `complete`); `--exclude-secure` yields scope `excluded_secure`, which never counts as preserved.
- Partial/atomic copy, resume, conflicts: `*.partial` + read-back + `os.replace`, interrupted partials replaced, mismatching destination files never overwritten, sources failing expected fixity not copied.
- Full-hash verification and eligibility: `LOCAL_CLEANUP_ELIGIBLE` needs a fresh full destination hash, local files matching fixity and a destination separate from the archive.
- Root identity and transitions: `root_id` marker, receipt bound to root and manifest hash; a changed unit or root returns the unit to pending.
- Windows paths: `fs_path`/extended-length handling, proven on `C:` by the local run; `K:` behaviour (network share, permissions, throughput) is **not** verified.

Cloud tests do not establish institutional preservation. No unit is `PRESERVED` or cleanup-eligible, and none was claimed.

## Production-safety result

Each property below has a passing test (workflow, packaging, deploy-script, runtime-config, auth and research test modules; 617 tests in those modules plus the full suite):

- Deploy waits for a successful CI/release gate and deploys `workflow_run.head_sha` (tested commit); manual rollback requires a green CI run for that SHA; stale runs skip when `main` moved on.
- `deploy_prod.sh` recreates only `web` (`--no-deps`); database and Redis are not restarted.
- Reset/invitation links use `PROMAT_PUBLIC_BASE_URL`, never `Host`/`X-Forwarded-*`.
- Placeholder or empty JWT/Flask secrets are rejected outside dev/test.
- Hostile research-set labels are escaped (`| safe` only for explicit `*_html` fields).
- Ordinary research profiles no longer expose consent or secure intake fields.
- Corpus-root login returns to `/speakers`; a specific restricted page returns to the requested target.
- `content/legal/impressum_datenschutz.md` is under `content/`, which the production image copies (`COPY content/ ./content/`); the existing legal text was moved, none was written or changed.
- Dependency check: `pip-audit -r app/requirements.txt` → no known vulnerabilities.

## Validation (exact, Python 3.12.3 in Cloud)

| Check | Result |
|---|---|
| `pytest tests` (canonical, from `app/`) | **896 passed**, 7 deselected (`data`-marked, operator catalogs), 0 failed |
| Focused modules (CI/workflows, packaging, deploy/backup scripts, runtime config, auth, sessions, phenomena, archive preservation, storage inventory, intake storage, working-tree intake, config fixtures) | 617 passed |
| `node --test app/tests/js/*.test.mjs` | 11 pass, 0 fail |
| `ruff check .` | all checks passed |
| `scripts/ci_governance_checks.py` | passed |
| `compileall -q app scripts` | ok |
| `shellcheck --severity=warning scripts/*.sh` | clean |
| `actionlint` | only the pre-existing `promat-prod` custom-label warning |
| `pip-audit -r app/requirements.txt` | no known vulnerabilities |
| Not run here | production image build/smoke and backup/restore rehearsal (verified by the earlier green GitHub CI run; they run again in CI on the PR), real importer run (needs Postgres, Docker, MFA), anything on Windows/`K:` |

Failure attribution: none. Earlier-run notes: base 836 → 882 → 892 → 896 passed (new tests only).

## German readiness (evidence only)

Organizer: ready (canonical, equivalence with documented differences, unknown-person follow-up done). Preservation root: not ready (HRZ storage unavailable; not a blocker for the German intake itself). German task catalogs: none exist, none created. German source data: not present locally. German single-speaker dry-run: blocked (catalog, source data, workbook; plus Docker/Postgres for the importer dry-run). German intake is a separate piece of work.

## Remaining operator-only gates

1. Verify `JWT_SECRET_KEY`, `FLASK_SECRET_KEY`, `PROMAT_PUBLIC_BASE_URL` (https) in the server `passwords.env` before the first deploy.
2. HRZ storage: obtain the preservation folder, complete the real copy and full SHA-256 verify.
3. Separate backup of classes the unit copy does not cover (historical workbooks, catalogs, `praat_pipeline/`, historical organizer, dev DB).
4. Real-importer run with Postgres, German content/catalog supply.

## Merge-readiness classification

**MERGE_READY_PENDING_REAL_PRESERVATION**

Code, review and tests are ready. Institutional preservation is not GREEN: no unit is `PRESERVED`, and the operator should wait for the HRZ storage and the real copy plus full verify before merging to `main`.

## Next step once HRZ storage is available

On the operator machine with the target folder available: set `PROMAT_PRESERVATION_ROOT`, then follow `docs/runbooks/archive-preservation.md` steps 3–10: `copy` dry-run, `copy --execute`, `verify` (exit 0, `LOCAL_CLEANUP_ELIGIBLE` = 71 for the current archive), `status`, `storage_inventory.py`; record the reports, then open the PR from this branch.
