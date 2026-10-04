# Production Safety Foundation

Datum: 2026-10-04

Branch: `claude/production-safety-foundation` (from `claude/wizardly-mayer-jaa7z2` at `d936801`, the re-entry audit). Nothing was merged, deployed, or changed in production.

## Ziel

Establish a trustworthy production-development baseline before German data and content work: a green, reproducible full test suite; CI as the real release gate with production deployment only after it; legal pages that work in the production image; a backup/restore foundation; fail-fast secret and URL configuration; and the confirmed security, privacy and regression findings of `docs/audits/promat_reentry_audit_2026-10-04.md`.

## Consulted Sources

- `docs/audits/promat_reentry_audit_2026-10-04.md`
- `docs/spec/platform-data-files.md`, `research-access.md`, `intake-workbook.md`, `research-capabilities.md`
- `AGENTS.md` and the scoped `AGENTS.md` files, `docs/runbooks/*`, run logs `2026-04-21_*`, `2026-05-25_*`, `2026-06-19_french-theatre-live-production-fix.md`
- `.github/workflows/*`, `infra/docker-compose.prod.yml`, `scripts/deploy_prod.sh`, `app/Dockerfile`

## Baseline (audit state)

| Check | Result |
|---|---|
| `pytest` | 681 passed, **20 failed**, **3 modules not collectable** |
| `pip-audit -r app/requirements.txt` | 49 advisory entries in 10 packages (the audit reported "11") |
| CI | smoke subset only; deploy ran in parallel to CI |

## Result

| Check | After |
|---|---|
| `pytest` (fresh clone, no operator data) | **836 passed, 7 deselected** (`data` marker), 0 failed, 0 collection errors |
| ruff / compileall / governance / teaching validation / shellcheck / actionlint | all pass |
| JavaScript tests | 11/11 |
| Production image build (+ in-image runtime assets, config preflight) | succeeds |
| Backup → verified restore against real migrations in disposable Postgres 15 | `RESTORE VERIFIED`, 13 tables |
| `pip-audit -r app/requirements.txt` | no known vulnerabilities |
| `pip-audit -r app/requirements-dev.txt` | 1 package: pytest 8.4.2 (fix needs pytest 9, deferred) |

## Changes

### Tests and reproducibility

- `scripts/research_data_intake/organize_batch_working_tree.py` is now versioned next to the importer. **It is a reconstruction**: the original was never committed (absent from all 212 commits) and exists only on the operator's machine. It was rebuilt from the 37 tests that pin its behaviour, the runbook, the run logs and the scanner helpers in `intake_batch_common.py`. Statuses the tests do not pin (`missing_*`, `conflict_multiple_{processed,raw}_wav/textgrid`, `conflict_existing_working_tree`, `planned_rebuild`, `error_interview_transform`) follow the same naming scheme. The importer no longer puts the gitignored `import/` directory on `sys.path`, so a stale local copy cannot shadow the tracked one. **The operator must diff the local original against it once** (runbook `research-intake-working-pipeline.md`).
- Operator-owned research-player catalogs are not in git and are not committed here (the real files were not available to this run and are operator content). Reproducibility model: tracked minimal synthetic fixtures (`app/tests/fixtures/runtime`, `fixture_runtime_root` in `app/tests/conftest.py`); `scripts/research_data_intake/validate_research_config.py` to check a real runtime root with the app loaders; intake tooling resolves catalogs from `PROMAT_RUNTIME_ROOT/data/config` like the app (identical default behaviour); canonical home for German: `data/config/research_player/german/`. Whether and where to version the real catalogs is left to the German-readiness run.
- Seven tests that assert the *content of the real catalogs* (item counts, `wl_014 = théâtre`, …) carry the existing `data` marker; they run with `pytest -m data` against real configuration and are the only reclassified tests. Structural equivalents (connected-text semantics, spoken-title item, canonical `théâtre` through the loader) run on fixtures in the canonical suite.

### CI and deployment

- `ci.yml`: ruff, compileall, governance, teaching validation, shellcheck, **whole** pytest suite; JS tests; compose config + production image build + in-image asset check; backup/restore rehearsal; `release-gate` job depends on all. `full-test.yml` removed (superseded); `release-candidate-check.yml` reuses `ci.yml`.
- `deploy.yml`: `workflow_run` on completed CI for a push to `main` (or manual dispatch for rollback). Deploys `workflow_run.head_sha` (not `github.sha`, which would be the branch tip), verifies a successful CI run for that exact SHA via the API, skips when `main` has moved on, serializes runs. Runner steps and `deploy_prod.sh` call are otherwise unchanged. `test_ci_workflows.py` pins this.
- `deploy_prod.sh`: replaces only `web` (`up -d --no-deps --force-recreate web`; compose dry-run showed the old command also recreated `promat-db-prod` and `promat-rate-limit-prod`), and validates the production configuration with the new image before migrations. Evidence for not restarting the DB: nothing in the deploy needs it; compose still recreates a service whose definition changed.

### Legal pages

- `docs/plans/impressum_datenschutz.md` → `content/legal/impressum_datenschutz.md` (the image copies `content/`, not `docs/`); tests render the legal pages from an image-shaped layout without `docs/` (verified to fail on the old path); `scripts/ci_image_smoke.py` checks the built image.

### Backup and restore

- `scripts/backup_prod_db.sh`, `restore_db_dump.sh`, `verify_db_restore.sh`, `ci_backup_restore_smoke.sh`; runbook `backup-and-restore.md` with scope table, schedule example, destructive-restore steps and what is deferred. Verified locally with real migrations: backup, checksum failure, count-drift (exit 3), refusal to restore into the production container without `--allow-production`, safe default (no `--clean`), pruning, failure when the container is missing.

### Security

- Reset/invite links use `PROMAT_PUBLIC_BASE_URL` only (validated at startup; https required in production; dev default `http://127.0.0.1:8000`); test forges `Host`, `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-Prefix` behind `ProxyFix` (fails on the old code).
- Production rejects empty or `__NAME__` placeholder `JWT_SECRET_KEY` (and the same for `FLASK_SECRET_KEY`); no values logged; no length rule (PyJWT 2.15 now warns below 32 bytes; see operator checks).
- `(x_html or x) | safe` → `x_html | safe if x_html else x` in 50 template places; set-label HTML injection regression test (fails on the old template), Unicode/IPA preserved.
- Config preflight in `deploy_prod.sh` so a bad secret/URL stops the deploy before the running container is replaced.

### Privacy

- Speaker profile no longer renders `research_consent_signed`, `teaching_consent_signed`, `consent_date`, `consent_file`, `questionnaire_file`, `secure_notes` (all columns of the `Secure_Person_Intake` sheet). Database, importer and runtime `metadata.json` are untouched. Evidence weighed: the spec's profile semantics enumerate the shown fields and omit these; the sheet is the secure sheet; the older run log (`2026-05-25-intake-consent-exposure-alignment`) and UI copy show they were added deliberately "for research-only contexts", but no normative text requires showing them. **`person_notes` stays** (documented as an internal research note). Also fixed: `origin_region` was shown twice for native speakers. Spec `research-access.md` now states the boundary; the old test that asserted the exposure now asserts its absence in the builder and in the rendered route (de/en).

### Dependencies

- Patch/minor pins only: anyio 4.11.0→4.14.2, click 8.3.0→8.3.3, flask 3.1.2→3.1.3, idna 3.10→3.15, pygments 2.19.2→2.20.0, pyjwt 2.10.1→2.15.1, python-dotenv 1.1.1→1.2.2, requests 2.32.5→2.33.0, urllib3 2.5.0→2.8.0, werkzeug 3.1.3→3.1.6.

## Test-failure resolution

| # | Test(s) | Cause class | Resolution |
|---|---|---|---|
| 1–9 | `test_auth_phase1`: `test_login_from_corpus_root_redirects_to_speakers`, `test_corpus_root_login_href_points_to_speakers[de/en × spanish/french/german/english]` | confirmed application regression (`bc5ffd2` reverted `1705434`) | `public_content.py`: corpus-root login `next` is `/speakers` again for every corpus. Nine `test_research_sessions` assertions that only passed because of the regression were updated |
| 10 | `test_french_item_migration::test_runtime_french_item_catalog_and_exports_use_canonical_value` | missing external data (reads real catalog and exports) | `data` marker |
| 11 | `test_research_comparison::…english_labels_for_migrated_workspace` | outdated expectation (intro string cleared deliberately in `eff0add`) | asserts the empty intro |
| 12–17 | `test_research_presets`: six `*_from_repo` / `*_repo_catalogs_*` tests | missing external data (assert real catalog content) | `data` marker + fixture-based structural tests |
| 18–19 | `test_research_sessions::…spanish_design_page…closing_shared_citation[de,en]` | outdated expectation (heading changed in `06a4817`) | updated headings |
| 20 | `test_teaching_content::…parses_teaching_impulses` | incorrect expectation (input has a `section_heading`; the sibling test expects it) | expects `section_heading, text, teaching_impulses` |
| C1–C3 | `test_research_production_importer`, `test_research_raw_sync_importer`, `test_research_working_tree_intake` (collection errors) | missing repository artifact (`organize_batch_working_tree.py`) | organizer versioned; 81 previously uncollectable tests now run. 18 of them then needed catalog items → fixtures |

## Validation (exact)

Fresh `git clone` of the branch, Python 3.12.3 venv from the pinned requirements, CI environment variables:

- `python -m ruff check .` · `python -m compileall -q app scripts` · `python scripts/ci_governance_checks.py` · `python scripts/validate_teaching_content.py` · `shellcheck scripts/*.sh` · `actionlint -ignore 'label "promat-prod" is unknown'` (the label is the self-hosted runner)
- `cd app && python -m pytest tests -q` → 836 passed, 7 deselected
- `node --test app/tests/js/*.test.mjs` → 11 passed
- `docker compose --env-file app/passwords.env.template -f infra/docker-compose.prod.yml config`; `docker build -f app/Dockerfile`; `docker run -i … python - < scripts/ci_image_smoke.py`; config preflight with valid, placeholder-JWT and placeholder-URL environments in the image. The sandbox's TLS-intercepting proxy breaks `pip` inside an unmodified `docker build`, so the build used a wrapper Dockerfile that only adds the proxy CA before the same layers; `app/Dockerfile` itself is unchanged.
- `PYTHON=… scripts/ci_backup_restore_smoke.sh` → backup/restore smoke OK
- `pip-audit -r app/requirements.txt` / `-r app/requirements-dev.txt`
- GitHub Actions: CI dispatched once on the working branch (never on `main`; the deploy workflow is not reachable from a non-`main` run) - see the final response for its conclusion.

Not exercised: the new `deploy.yml` end to end (it only runs from `main`), the self-hosted runner, and anything against production (the environment cannot reach it).

## Abweichungen

- Spec text (`platform-data-files.md`, interview raw fallback) and the intake runbook contradicted the tests and the 2026-05-25 run log; the spec and runbook were corrected to the tested behaviour.
- The organizer is a reconstruction (see above); preserving the original "exactly" was impossible because it is not in the repository.

## Remaining operator checks (production access required)

See `docs/runbooks/deploy-and-rollback.md` (full checklist): legal routes return 200; deployed `JWT_SECRET_KEY` is not a placeholder and ≥ 32 characters; `PROMAT_PUBLIC_BASE_URL` is the canonical https origin and a real reset mail carries it; first CI-gated deploy deploys the tested commit; `promat-db-prod` start time unchanged across a deploy; `backup_prod_db.sh` + `verify_db_restore.sh` against the real database, cron and off-server copy; branch protection requiring `release-gate`; flat `config/research_player` vs `current/config` drift; diff of the local organizer copy; a profile with consent data shows no consent rows.

## Deferred

- Storage & Preservation run: retention/off-host policy, fixity checks, original/canonical/derived separation, versioning of research catalogs, restore drills.
- German readiness run: where real catalogs are versioned, making the publish step deliver `config/` to the flat tree (currently manual), German quote normalisation in the text MFA prep, mandatory `--target-language`, German dry-run.
- DOI/publication work: unchanged by this run.
- Not done on purpose: stop shipping consent fields in runtime `metadata.json` (needs an intake-contract decision); `person_notes` visibility (one-line change if the owner decides otherwise); pytest 9 (dev only); passlib replacement before Python 3.13; token revocation, login timing, `/ready` hardening, GoatCounter scope, access-request retention (audit register items C).
