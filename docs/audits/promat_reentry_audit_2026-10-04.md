# PROMAT Re-entry Audit (2026-10-04)

Status: non-normative audit report. Active rules remain in `docs/spec/`. This document records findings and recommendations only; nothing in it changes current specs.

Scope: repository `FTacke/promat-webapp` at `main` = `28c63d1` (2026-08-17, last production deploy run #110 succeeded the same minute). Branch for this report: `claude/wizardly-mayer-jaa7z2`.

File naming: the request named `docs/audits/2026-10-04-pronunciation-matters-reentry-audit.md`. `docs/audits/` already uses the convention `promat_<topic>_<YYYY-MM-DD>.md` (e.g. `promat_webapp_local_audit_2026-05-30.md`), so this report follows that convention.

Method and limits:

- Full source/config read of the repository, git history (shallow clone, 50 commits back to 2026-06-01 after the history reset documented in `docs/agent-runs/2026-03-31_git-history-reset-04.md`), GitHub Actions run list (read-only).
- Local test suite, lint, governance checks, `pip-audit`, and a local Docker build were run in an isolated cloud container (details in §10).
- **The production website could not be inspected.** The cloud environment's egress policy blocks `pronunciation-matters.de` (HTTP 403 at the proxy). Every statement about live behaviour is therefore derived from code and marked UNKNOWN where it matters (§17).
- No SSH, no credentials, no deployment, no change to application code or configuration.

---

## 1. Executive assessment

- **Overall health: good core, weak safety net.** The application is a coherent, well-governed Flask monolith (≈21k lines Python, 39 templates, 701 tests) with an unusually explicit spec layer (`docs/spec/`) and a careful, checksum-verified intake/publish chain.
- **Strengths:** clean runtime boundaries (`data/` mounted read-only into the container, secrets outside git, `secure/` never served); consistent route-level research gating; argon2 hashing, CSRF-protected JWT cookies, CSP/HSTS; teaching content already declarative (YAML) with structured citation and DOI field; intake is filename-driven with explicit refusal on ambiguity, manifests and SHA-256 checksums.
- **Main risk 1 – `main` deploys without any gate.** `.github/workflows/deploy.yml` runs on every push to `main` in parallel with CI, not after it. Run #110 finished deploying before CI finished. CI itself only runs a smoke subset; the full suite is manual-only.
- **Main risk 2 – the full test suite on `main` is red and nobody sees it.** 20 failing tests + 3 modules that cannot be imported on a clean checkout. Among them is a **real regression**: the corpus-root login link no longer returns users to `/speakers` (commit `bc5ffd2` silently reverted `1705434`).
- **Main risk 3 – essential intake code and canonical scientific config are not in git.** `scripts/research_data_intake/import/organize_batch_working_tree.py` (imported by the production importer at module load) and all task catalogs / player configs under `data/config/research_player/**` exist only on the operator's machine and the server. A fresh checkout cannot run the intake, and the canonical item texts are not versioned.
- **Main risk 4 – probable broken legal pages in the production image.** `/impressum` and `/privacy` read `docs/plans/impressum_datenschutz.md`, which `app/Dockerfile` does not copy. Verified in a locally built image: `LegalContentError`. Whether production is affected must be checked immediately (UNKNOWN, §17).
- **Main risk 5 – no backup/restore story in the repo.** No database dump, no data backup, no restore runbook; the Postgres and Redis volumes plus `/srv/webapps_storage/promat/data` are the only copies on the server side.
- **Security:** no critical exploitable flaw found from source, but two confirmed issues worth fixing soon: password-reset links built from the request host (Host-header poisoning, depends on nginx config) and an unescaped `|safe` rendering of user-chosen set labels (HTML injection, blocked from script execution by CSP). Consent/internal person metadata is shown on speaker profiles to every authenticated user and a test locks that in.
- **Dependencies:** pinned and reasonably current (Python 3.12, Flask 3.1, SQLAlchemy 2.0), but the lockfile has not been refreshed since 2025: `pip-audit` reports 49 advisories in 11 packages (werkzeug, urllib3, pyjwt, requests, flask, idna, …). Patch-level refresh only; no framework migration needed.
- **German expansion:** German is already registered everywhere (corpus registry, standard varieties, MFA language config, empty teaching hub). It is **not** blocked architecturally, but it is the first corpus that will go through the pipeline without ever having been tested; it needs the German task catalogs, a Spanish-only branch removed from the design-page routing, and the versioned intake code first.
- **Ready for renewed development?** Yes, after a short safety-foundation run (§15 A): gate deployment on CI, make the full suite green and reproducible, check the legal page, and put a backup in place. None of this requires redesign.
- **Can German data/content expansion begin immediately?** German *teaching* content: yes (fully declarative, no code change). German *research data*: only after the intake code and catalogs are versioned and a German dry-run has passed (§15 B). German *design page*: needs a small, bounded routing generalisation.

---

## 2. Current architecture

### 2.1 Application

```mermaid
flowchart LR
  subgraph Browser
    UI[Jinja HTML + vanilla ES modules\napp/static/js, app/static/css]
  end
  subgraph Server[Host: vhrz2184]
    NGINX[nginx TLS\n(not in repo)] --> GUNI
    subgraph Docker[compose project promat-prod]
      GUNI[promat-web-prod\nGunicorn 2 workers\nFlask app src.app.main:app]
      PG[(promat-db-prod\nPostgres 15\nvolume promat_postgres_prod)]
      RD[(promat-rate-limit-prod\nRedis 7 AOF\nvolume promat_redis_prod)]
    end
    DATA[/srv/webapps/promat/data\n(bind of /srv/webapps_storage/promat/data)\nmounted :ro at /app/data/]
    LOGS[/srv/webapps/promat/logs/]
  end
  UI --> NGINX
  GUNI --> PG
  GUNI --> RD
  GUNI -->|read-only| DATA
  GUNI --> LOGS
  UI -.-> GC[GoatCounter (3rd party)]
```

- Framework: Flask 3.1 app factory `app/src/app/__init__.py:create_app`; blueprints `routes/public.py`, `routes/auth.py`, `routes/admin.py`, `routes/research_api.py`.
- No frontend build step: hand-written ES modules and CSS (≈750 KB JS+CSS, 6.4 MB self-hosted variable fonts). There is no npm/Vite pipeline despite `VITE_*` env names.
- Persistence: PostgreSQL (`AUTH_DATABASE_URL`) for users, access requests, research sets, research metadata (`research_people`, `research_sessions`, `research_session_exposures`), analytics aggregates; Redis only for rate limiting; files under `PROMAT_RUNTIME_ROOT/data` for session JSON/MP3 and research-player config; teaching content baked into the image from `content/teaching`.
- Migrations: plain SQL in `app/migrations/`, applied idempotently by `app/scripts/apply_auth_migration.py` on every deploy. Note duplicate number prefixes (`0006_finalize_protected_area.sql` and `0006_unify_research_sets…sql`; engine-split `0008`/`0009`) — works today, but ordering relies on filename sort.
- Auth: Flask-JWT-Extended access token in HttpOnly cookie, double-submit CSRF, argon2; roles from token claims; group accounts (`account_kind`). Research access gate `_require_research_route_access` (`routes/public.py:348`) per route; only `design` is public (`research_capabilities.py`).
- i18n: one Python dict `TRANSLATIONS` (`i18n.py`, 916 keys each in `de`/`en`, key sets identical), routes `/{ui_lang}/…`.
- Logging: Gunicorn access/error logs to stdout (docker logs), app `RotatingFileHandler` under `/app/logs`. No error aggregation or uptime monitoring in repo.

### 2.2 Deployment flow

```mermaid
sequenceDiagram
  participant Dev as Developer push
  participant GH as GitHub main
  participant CI as CI workflow (ubuntu-latest)
  participant R as Self-hosted runner [promat-prod]
  participant S as /srv/webapps/promat/app
  Dev->>GH: push to main
  par independent
    GH->>CI: ruff, compileall, governance, compose config, ~12 smoke tests, 11 JS tests
  and
    GH->>R: deploy.yml
    R->>S: git fetch; checkout --force SHA; reset --hard
    R->>S: scripts/deploy_prod.sh
    S->>S: compose up db, rate_limit; wait healthy
    S->>S: compose build web (on server)
    S->>S: compose run web apply_auth_migration.py --engine postgres
    S->>S: compose up -d --build --force-recreate (all services)
    S->>S: wait for container health; curl /health, /ready
  end
```

### 2.3 Research data intake flow

```mermaid
flowchart TD
  A[Drop-in batch\nscripts/research_data_intake/import/<x_batch>/\nWAV, TextGrid, Amberscript JSON, intake XLSX] --> B[scan_import_batch.py\nfilename classification]
  B --> C[import/organize_batch_working_tree.py\n**not in git**]
  C --> D[import_batch_to_production.py\nworkbook read, MFA text alignment (Docker mfa),\nwordlist splits, ffmpeg MP3 160k loudnorm]
  D --> E[(dev Postgres upsert)]
  D --> F[Local archive PROMAT_LOCAL_ARCHIVE_ROOT\nraw/source/secure/alignment/runtime + manifests]
  D --> G[repo data/sessions/<slug>/ runtime JSON+MP3]
  G --> H[build_prod_upload_package.py\nallowlist, manifest.json, checksums.sha256]
  H --> I[validate_research_intake.py prod-package]
  I --> J[upload_prod_package.py\nrsync/tar over SSH -> /srv/webapps_storage/promat/data/incoming/<id>]
  J --> K[publish_prod_release.py via ssh bash -s\nsha256 -c, stage releases/release_ts, DB payload apply in container,\nswitch current symlink, rm -rf + rsync sessions/<slug>, docker restart, health]
  K --> L[App reads data/sessions + Postgres metadata]
```

### 2.4 Storage/persistence model (summary; details in §6)

| Class | Where | In git? | Backup in repo? |
|---|---|---|---|
| A Source (WAV, TextGrid, XLSX, consent) | operator machine `C:\dev\promat_data_archive` (`intake_storage.py:18`) + batch `import/` | no (correct) | none documented |
| B Canonical (task catalogs, player config, normalized metadata) | `data/config/research_player/**` (local + server), archive `metadata/` | **no** | none |
| C Derived (session JSON/MP3, packages, reports) | `data/sessions/**`, server `releases/`, archive `runtime/` | no | one previous release, 7 days (publish retention) |
| D Application state | Postgres volume, Redis volume | no | none in repo |
| E Publication artifacts | none yet; tag `v0.7` (code only) | — | — |

### 2.5 Content architecture

- Teaching: `content/teaching/<language>/teaching.yaml`, `hubs/{de,en}.yaml`, `<topic>/{de,en}.yaml`, media beside topics; loader `teaching_content.py`; block vocabulary of ~20 types; served at `/teaching-media/...` from the content tree (there is no `public/teaching`, contrary to the wording in `AGENTS.md`).
- Research corpus landing, design page, project pages: Python dicts with embedded HTML (`routes/public_content.py:LANGUAGES`, `routes/public_page_content_data.py:PROJECT_PAGES_CONTENT`, `SPANISH_DESIGN_PAGE_CONTENT`) rendered by the generic `templates/pages/promat_page.html`.
- Legal pages: parsed at runtime from `docs/plans/impressum_datenschutz.md`.

---

## 3. What is already working well (do not rewrite without reason)

1. **Spec-driven governance** (`docs/spec/*`, scoped `AGENTS.md`, `scripts/ci_governance_checks.py`). It is the reason the system is reconstructable after months away.
2. **Runtime boundary model**: code checkout `/srv/webapps/promat/app` vs data `/srv/webapps_storage/promat/data` bound to `/srv/webapps/promat/data`, mounted `:ro`. A code deploy cannot overwrite research data.
3. **Intake classification discipline**: filename-driven, refuses ambiguity (`intake_batch_common.choose_unique_candidate`), multiple workbooks are a hard error, workbook vocabularies validated.
4. **Prod package + publish chain**: allowlist export, `manifest.json` + `checksums.sha256` verified locally and remotely, staged release directory, atomic `current` symlink switch, forbidden-file scan, DB payload validated against the release before apply, single DB transaction (`apply_prod_db_payload.py`). This is better than most projects of this size; extend, don't replace.
5. **Language config registry for intake** (`scripts/research_data_intake/language_config.py`) already contains `de` with MFA `german_mfa`.
6. **Research access gating** per route before lookup, with tests (`test_research_detail_routes_require_auth_before_lookup` etc.).
7. **Auth core**: argon2, hashed single-use reset tokens, CSRF on JWT cookies, production refuses `memory://` rate-limit store, mail header sanitisation, honeypot + signed timing token on the access request.
8. **Teaching content model**: YAML, bilingual, markdown with `html=False`, structured `metadata` and `citation` (with `doi`), validation script.
9. **Deploy script hygiene**: `set -euo pipefail`, preflight checks, health waits, `/health` + `/ready` probes after deploy.
10. **Dependabot** for pip, Docker and Actions is configured (PRs are not being merged, see §12).

---

## 4. Production/deployment findings

- **D1 – Deploy is not gated on CI.** `deploy.yml` triggers on `push: [main]` independently of `ci.yml`. GitHub run list for `28c63d1`: CI run 216 and Deploy run 110 both started 2026-08-17T12:35:41Z; deploy finished at 12:36:55, CI at 12:36:58. A push that fails CI is deployed anyway.
- **D2 – CI checks too little for a production-deploying branch.** `ci.yml` runs ~12 named smoke tests; `full-test.yml` (full suite) is `workflow_dispatch` only (scheduled run disabled 2026-05-31, `docs/audits/promat_disable_scheduled_full_test_2026-05-31.md`); `release-candidate-check.yml` (incl. Docker build) is manual. Consequence: the regressions in §10 have been on `main` since June unnoticed.
- **D3 – Build happens on the production host**, during the deploy, from the checked-out tree (`compose build web`). No image registry, no image tag per SHA. Rollback = re-run the workflow for an older SHA (`workflow_dispatch` deploys whatever ref is chosen) and rebuild; there is no rollback automation or documented procedure.
- **D4 – `compose up -d --build --force-recreate` recreates all services**, including Postgres and Redis, on every deploy (`scripts/deploy_prod.sh`). Data survives (named volumes), but every code push restarts the database. Low risk, unnecessary downtime and an avoidable failure mode; scoping to `web` would suffice.
- **D5 – Migrations run before the new container starts, without a backup step.** `apply_auth_migration.py` is described as non-destructive; there is no pre-migration `pg_dump`. Failure mid-migration leaves the old container running against a partially migrated schema (SQL files are not wrapped in an explicit transaction per file — UNKNOWN whether the runner does this; see `app/scripts/apply_auth_migration.py`).
- **D6 – Server checkout is force-reset** (`git checkout --force` + `reset --hard`). Correct for a deploy-only checkout; any manual hotfix on the server is silently lost. Keep, but document.
- **D7 – Post-deploy smoke covers only `/health` and `/ready`.** A page-level 500 (e.g. legal pages, §11) would not fail the deploy.
- **D8 – Branch protection / required checks:** not visible from the repo; `CODEOWNERS` is comment-only by design. UNKNOWN (§17).
- **D9 – Release tags exist (`v0.7`) but are decorative.** `deploy.yml` reads the latest GitHub release only for the footer label; deployment is per commit.

Assessment of candidate gates (only what the evidence supports):

| Gate | Recommendation |
|---|---|
| Deploy only after CI succeeds (`workflow_run` or job `needs` in one workflow) | **Yes, required** (D1). Cheap, no workflow change for the operator. |
| Full pytest suite + Docker build in CI on PR/push | **Yes** once the suite is green and self-contained (D2, §10). Runtime is ~2 min. |
| Branch protection with required CI on `main` | **Yes**, lightweight: require CI, allow admin bypass. |
| Post-deploy smoke of a handful of public pages | **Yes**, extend `deploy_prod.sh` with 4–5 `curl -f` checks. |
| Image tagging per SHA + documented rollback | Recommended (C), proportionate: tag `promat-web:<sha>` and keep the previous image. |
| Staging/preview deployment | **Not justified now.** Single maintainer, small traffic; CI gate + smoke + rollback give most of the value. |
| Explicit production promotion via tags | Not now; revisit when scientific releases start (§7). |

---

## 5. Intake findings

Pipeline reconstruction: §2.3. Detailed run instructions live in `scripts/research_data_intake/README.md` and `docs/runbooks/research-intake-working-pipeline.md`, `research-prod-upload-and-publish.md`, `research-prod-db-payload-upsert.md`.

Confirmed problems:

- **I1 – Production importer depends on an unversioned file.** `import_batch_to_production.py:64` imports `organize_batch_working_tree` from `scripts/research_data_intake/import/`, which `.gitignore` excludes (`scripts/research_data_intake/import/*`). The file is absent from git history and from the clean checkout; three test modules fail at collection. The whole intake is therefore reproducible only on the operator's machine. This is the most important intake finding and the first thing to fix before German intake.
- **I2 – Canonical task catalogs and player configs are unversioned.** `data/config/research_player/<slug>/{player_config.json,task_catalogs/*.json}` are declared canonical in `docs/spec/platform-data-files.md` (§`data/config/`), but `data/config/*` is gitignored. Eight tests that read them fail on a clean checkout. German catalogs do not exist anywhere visible.
- **I3 – Publish does not deliver config updates to the path the app reads.** `publish_prod_release.py` syncs only `sessions/` from the new release into `DATA_ROOT/sessions/`; `config/research_player/**` from a package lands in `releases/…`/`current/` but the app reads `data/config/research_player/<slug>` (`research_presets._research_player_language_dir`). UNKNOWN whether the server has a symlink making this work (§17). Relevant for German, whose catalogs must be shipped for the first time.
- **I4 – Publish ordering can leave DB ahead of files.** DB payload is committed before the `current` switch and before the `rm -rf sessions/<slug>` + `rsync` (`publish_prod_release.py:~217–231`). A failure between those steps leaves DB rows pointing at sessions not yet served; the `rm -rf` + `rsync` also has a window where the corpus directory is absent. Rare for a single-operator workflow; mitigate by syncing to a temp dir and `mv`.
- **I5 – Failure reporting:** with `set -euo pipefail`, a failed publish exits before the publish log is written, although the runbook expects a report on every run.
- **I6 – Local importer is per-session atomic, not per-batch.** `SessionWorkspace` rollback per session; the archive write is not rolled back; batch `import_payload.json` is not written after a mid-batch failure, and a `--person-id` re-run overwrites it with a subset. Re-runs are safe (become updates). Acceptable; document the "re-run whole batch before packaging" rule.
- **I7 – Item clips are cut from the encoded MP3** (`audio_conversion/ffmpeg_audio.py`), i.e. a second lossy generation. Audible impact is probably negligible at 160 kbit/s; note for preservation (canonical audio must be the WAV in the archive, not the web MP3).
- **I8 – `upload_prod_package._verify_remote_root` requires a `config` entry** — a package built without `--include-research-player-config` will fail post-upload verification; untested.
- **I9 – Runbook drift:** the French `théâtre` migration runbook calls `/app/scripts/research_data_intake/migrate_french_theatre_item.py`, but the Dockerfile copies only `apply_prod_db_payload.py`.

German-specific assessment:

- Registered: `language_config.py` (`de`→`german`, MFA `german_mfa`), `config/data_conventions.py` (`TARGET_LANGUAGES`, `STANDARD_VARIETIES["de"]`), DB check constraint allows `de`, workbook alias `CH_DE_STD`.
- Defaults that are Spanish: `--target-language` default `es`, `produce_wordlist_artifacts.py:44`, `produce_text_artifacts.py:37`. Harmless if the flag is always passed; worth making mandatory.
- French-only normalisation (`item_text_normalization.py`) is correctly scoped and will not affect German.
- `prepare_text_mfa_corpus._comparison_text` normalises quotes but not German „ “ ‚ ‘ — catalog/TextGrid quote differences would produce mismatches in the text task.
- `reset_dev_research_runtime.py:17` creates code-named folders (`de,en,es,fr`) while runtime uses slugs — dev-only inconsistency.
- No German batch has ever been run; no DE fixtures in tests.
- Verdict: **the machinery is generic enough; no redesign needed.** Required before German: I1, I2, German catalogs, quote normalisation check, and one dry-run end-to-end on a single German speaker.

---

## 6. Storage and preservation findings

| Class | Current location | Source of truth | Mutability | Recoverability / backup visible | Regenerable | Versioning / integrity |
|---|---|---|---|---|---|---|
| A Source recordings, TextGrids, XLSX, consent, secure person data | Operator archive `PROMAT_LOCAL_ARCHIVE_ROOT/sessions/<code>/<session>/{raw,source,alignment_source,secure}` (`intake_storage.py`); never on server | Archive | Append, overwrite in place on re-import | **No backup documented** — single laptop copy is the critical risk | No | `archive_manifest.json` with SHA-256 per file; no fixity re-check |
| B Canonical: task catalogs, player config | `data/config/research_player/**` locally + server | Ambiguous (local copy) | Edited by hand | Not in git, no backup documented | No (intellectual content) | None |
| B Canonical: normalized person/session metadata | Workbook → dev DB → prod DB via payload; archive `metadata/` | Workbook + archive | Upsert | Prod DB: no backup in repo | Yes, from archive + workbook | Payload checksummed |
| C Derived: session JSON/MP3 | Server `data/sessions/<slug>`, `releases/`, `current/`; archive `runtime/` | Archive runtime copy | Replaced per release | 1 previous release, ≤7 days | Yes (from A+B via intake, requires MFA/ffmpeg) | `checksums.sha256` per package |
| C Derived: teaching media | `content/teaching/**/media` in git | git | Commit | git | — | git |
| D App state: users, access requests, research sets, analytics | Postgres volume `promat_postgres_prod` | DB | Live | **None in repo** | No (user-created sets, accounts) | None |
| D Rate limit | Redis volume | — | Ephemeral | Not needed | Yes | — |
| E Publication artifacts | None | — | — | — | — | Git tag `v0.7` only |

Principles proposed for a future *PROMAT Storage & Preservation Policy* (to live in `docs/spec/platform-data-files.md`, not implemented here):

1. **Three-tier separation stays as is:** A (source, offline/secure), B (canonical, versioned), C (derived, disposable). The existing directory model already supports this.
2. **Canonical config belongs in version control.** Task catalogs and player configs are scholarly content: version them (in this repo under a non-ignored path, or in a dedicated small data repo) and ship them to production through the package mechanism.
3. **Rule of 3-2-1 for class A and D only.** Source recordings: archive copy + university storage (e.g. HRZ network drive/Uni-Cloud) + one offline copy. Postgres: nightly `pg_dump` to `/srv/webapps_storage/promat/backups` with rotation and an off-host copy. Class C needs no backup beyond the release retention because it is regenerable.
4. **Fixity:** keep SHA-256 manifests (already present); add a periodic verify for the archive and a manifest for each scientific release.
5. **Restore is part of backup:** one runbook and one tested restore (DB into a scratch container; one corpus re-generated from archive).
6. **Retention:** derived releases short (as now); source and canonical indefinitely; access-request personal data with an explicit retention period (see S6).
7. **Proportionality:** no object storage, no data lake, no second database. Plain files + checksums + `pg_dump` are sufficient at this size.

---

## 7. DOI/publication-readiness findings

Target lifecycle: living app → versioned snapshot → export package → university repository → DOI.

- **Teaching pages are closest to ready.** YAML per topic with `metadata.authors`, `created`, `updated`, `status`, `credits` (roles, affiliations) and `citation.{text,copy_text,doi,url}` (`teaching_content.py:_citation_payload`). Missing: `version`, `license`, `published`/`release_date`, stable topic identifier independent of slug, `language` (implicit in path), `related_identifiers`.
- **Research-design pages are not ready.** The Spanish design page is ≈460 lines of HTML strings inside Python (`public_page_content_data.py:667–1129`), with the citation hard-coded as HTML and copy text. No structured author/version/date/licence fields, and content changes require code changes and redeploys. Migrating design pages to the same YAML model as teaching (with a `research_design` block vocabulary) is the single most useful step for DOI readiness and for German design pages.
- **Corpus releases are not represented.** The intake produces checksummed packages and batch reports, which is a good basis, but there is no notion of a corpus version, release manifest with metadata, or exported dataset structure. Session data are also partly access-restricted, so a DOI release will need a decision on what is published (metadata only vs. audio) — not decidable from the repo.
- **Licences:** only `app/LICENSE` (MIT, code). No licence for content or data (e.g. CC BY 4.0 for texts, a separate licence/access statement for recordings). No `CITATION.cff`.
- **Citation hierarchy:** the platform has an app-level version (`APP_RELEASE_TAG`, footer), per-corpus people in `LANGUAGES` (lead, conducted by, material conception), per-topic authors in teaching YAML. The hierarchy platform → language resource → page is therefore already implicit; it lacks an explicit "part of / is version of" relation and a resource-level citation for the language corpus and for each language's teaching resource.
- **Export tooling:** none (no static snapshot, no Frozen-Flask, no export script). Because teaching and (after migration) design pages are file-based, a snapshot exporter can render each page to standalone HTML + YAML source + media + `metadata.json` without touching the live app.

Metadata the application should be able to represent/export (repository-specific rules are not documented in the repo and must be confirmed with the university repository): title (de/en), creators with ORCID and role, contributors (editor/platform), publisher/platform relation (`isPartOf`), language(s), version, publication date, licence, recommended citation, related identifiers (previous version, platform DOI, corpus DOI), repository identifier, DOI.

---

## 8. Security findings

Confirmed vulnerabilities (fix soon; neither is critical):

- **S1 – Password-reset link poisoning (conditional).** `services/auth_mail_messages.py:build_password_link` uses `url_for(..., _external=True)`; `__init__.py:185` applies `ProxyFix(x_host=1, x_prefix=1)`; no `SERVER_NAME`/`TRUSTED_HOSTS`; `PROMAT_PUBLIC_BASE_URL` is required by compose but **unused in code**. An unauthenticated `POST /auth/password/forgot` with a forged `X-Forwarded-Host` could produce a mail with a link to an attacker host carrying a valid 14-day token — unless nginx overwrites `Host`/`X-Forwarded-Host` (UNKNOWN, §17). Fix: build links from `PROMAT_PUBLIC_BASE_URL`; set `TRUSTED_HOSTS`.
- **S2 – Stored HTML injection via research-set labels.** `templates/partials/_content_header.html:35` renders `(content_header.title_html or content_header.title) | safe`; editor pages pass the user-supplied set label as `title` (`research_phenomena_views.py:518,549`), labels are only stripped (`research_sets.py:337`). Affects other members of a group account and every viewer of admin-labelled curated sets. CSP `script-src 'self'` prevents script execution; HTML/CSS injection (fake links/forms) remains. Fix: never pipe the plain field through `|safe`. The same `(x_html or x) | safe` pattern recurs in teaching partials (repo-controlled input today).

Credible risks:

- **S3 – `JWT_SECRET_KEY` strength not validated.** Only `FLASK_SECRET_KEY == "__CHANGE_ME__"` is rejected (`config/__init__.py:~207`); the template ships `JWT_SECRET_KEY=__CHANGE_ME__`. Roles are trusted from token claims, so a weak/default JWT secret = admin token forgery. Verify production value (§17) and add a startup check.
- **S4 – No token revocation.** No blocklist/user loader; logout only clears the cookie; deactivating or demoting a user takes effect only after token expiry (default 3600 s). Acceptable for now if expiry stays short; add a per-request user-status check later.
- **S5 – Reset tokens in access logs.** Gunicorn `--access-logfile -` logs `GET /auth/password/reset?token=…`; tokens valid 14 days.
- **S6 – Personal data retention.** Access requests store name, email, institution, user agent and the raw `X-Forwarded-For` (client-spoofable) with no retention/cleanup.
- **S7 – Consent/internal person metadata visible on speaker profiles.** `research_views.py:1054–1067` renders person notes, consent flags, consent date, consent file, questionnaire file and `secure_notes` when present; the production importer writes the first four into runtime `metadata.json` (`import_batch_to_production.py:1157–1160`). Visible to every authenticated research user including group accounts. `test_profile_page_uses_profile_wording_and_structured_exposure` asserts these rows. This conflicts with the historical requirement and with data-minimisation; also `origin_region` is rendered twice for natives.
- **S8 – Login enumeration/lockout abuse.** Missing users skip argon2 (timing), lockout after 5 failures is per account and can be triggered by anyone knowing the address; forgot-password sends mail synchronously.
- **S9 – `/ready` is unauthenticated, unthrottled, and returns exception text** (`routes/public.py:822–863`), opening a DB connection per call.
- **S10 – GoatCounter on protected pages** (`templates/base.html:39`, no SRI) sends paths with person/session IDs to a third party; first-party analytics cookie set without consent. Privacy/legal question rather than a technical vulnerability.

Hardening opportunities (no current exploit): GET logout without CSRF; explicit `next` path check instead of relying on Werkzeug encoding; validate `teaching_lang`/`topic_slug` in the media route; `?_profile=1` profiling hook reachable before auth; `Cache-Control: private` on protected HTML/audio; `MAX_CONTENT_LENGTH`; container runs as root; no `.dockerignore` (tests, `.vscode`, caches copied into the image); deprecated `X-XSS-Protection` header.

Fine as is: SQL via ORM only; Jinja autoescape; markdown `html=False`; JS `innerHTML` with `escapeHtml`; media from `data/` resolved by lookup, not path; debug off in production; CSP/HSTS/XFO/nosniff/Referrer-Policy; production refuses in-memory rate limiting.

---

## 9. Performance/efficiency findings

No material problem found; the player cold-load work of spring 2026 is documented in `docs/performance-*.md`.

- **P1 – Static assets have no long-lived caching or fingerprinting.** Production uses Flask's default `SEND_FILE_MAX_AGE_DEFAULT` (no max-age) and no versioned asset URLs; 6.4 MB fonts and 4.2 MB images are revalidated on each visit unless nginx overrides (UNKNOWN). Fix (C): serve `/static` from nginx with long cache + cache-busting query.
- **P2 – Audio** served via `send_file(conditional=True)` (Range support) through Gunicorn workers; fine at current traffic. With 2 sync workers, many concurrent audio streams can occupy workers; consider nginx `X-Accel-Redirect` only if usage grows.
- **P3 – `Flask-Caching` `SimpleCache`** is per-process; acceptable with 2 workers.
- **P4 – Item clip MP3s** are many small files; fine.
- **P5 – `/ready` performs a schema inspection and file write per call** (see S9).
- Frontend: no bundler, ≈750 KB JS+CSS unminified; the largest CSS file is 257 KB (`30_components.css`). Acceptable; not worth a build pipeline now.

---

## 10. Test/regression findings

### 10.1 Validation run (this audit)

Environment: Python 3.12.3 venv, `app/requirements.txt` + `requirements-dev.txt`, CI-equivalent env vars, runtime root in a scratch directory.

| Check | Result |
|---|---|
| `ruff check .` | pass |
| `python -m compileall app` | pass |
| `scripts/ci_governance_checks.py` | pass |
| `node --test app/tests/js/*.test.mjs` | 11/11 pass |
| `pytest tests` (full) | **3 collection errors** (`test_research_production_importer.py`, `test_research_raw_sync_importer.py`, `test_research_working_tree_intake.py`) |
| `pytest tests` minus those 3 modules | **681 passed, 20 failed** (≈112 s) |
| Docker build `app/Dockerfile` | builds (with the cloud proxy CA injected via a scratch Dockerfile wrapper; application layers identical) |
| Legal-content lookup inside the built image | **fails**: `LegalContentError: docs/plans/impressum_datenschutz.md not found` |
| `pip-audit -r app/requirements.txt` | 49 advisories in 11 packages |
| Production HTTP checks | not possible (egress blocked) |

All failures are pre-existing on `main`; this run changed no code.

Failure classification:

| Group | Tests | Cause | Kind |
|---|---|---|---|
| Login return target | `test_login_from_corpus_root_redirects_to_speakers`, `test_corpus_root_login_href_points_to_speakers[×8]` | `routes/public_content.py:529` uses `login_next:research:{slug}`; commit `bc5ffd2` (2026-06-22) removed the `:speakers` suffix that `1705434` had added the same day | **Real regression** |
| Design-page citation | `test_spanish_design_page_uses_dedicated_title_and_closing_shared_citation[de,en]` | Heading changed to "Diesen Aufsatz zitieren" (`06a4817`), test not updated | Test drift after intentional content change (confirm wording) |
| Teaching impulses | `test_build_teaching_topic_page_parses_teaching_impulses` | `section_heading` block now kept in output; test expects it dropped | Test drift (confirm intended) |
| Repo data dependency | 6 in `test_research_presets.py`, `test_french_item_migration.py::test_runtime_french_item_catalog…`, `test_research_comparison.py::test_build_comparison_page_exposes_english_labels…` | read gitignored `data/config/research_player/**` | Non-reproducible tests (I2) |
| Missing module | 3 modules | `import/organize_batch_working_tree.py` not in git | Non-reproducible tests (I1) |

CI stays green only because `ci.yml` selects ~12 tests that avoid all of these.

### 10.2 Coverage map (critical behaviour)

| Behaviour | Coverage |
|---|---|
| Public/restricted routes, research gate | good (auth + sessions tests) |
| Login, return targets | good, but currently failing (regression) |
| Access request success/500, confirmation UI | good |
| Speaker pages, players, comparison | good (Python); JS state partially |
| Default set "All Items" | partial (URL helper only) |
| Whole-row playback stop | none |
| Speaker ordering | good |
| Standard-variety labels | unit only |
| Profile metadata visibility | test asserts the *unwanted* behaviour |
| Language switching / multilingual routes | good |
| Teaching / theme pages | good |
| Dark mode | none (Datawrapper flag only) |
| Intake | good in principle, but 3 modules unrunnable on clean checkout |
| Production build | none in CI (manual RC workflow only); legal-page breakage would not be caught |

### 10.3 Historical issues (current implementation)

| # | Issue | Status | Evidence |
|---|---|---|---|
| 1 | Login return target | **STILL PRESENT (regressed)** | Generic `next` handling is correct and tested (`_safe_next`, `test_protected_research_route_click_preserves_exact_target` pass), but corpus-root login link returns to corpus root instead of `/speakers`; 9 tests fail |
| 2 | Access request success vs 500 | FIXED / protected | `access_request_notifications.py:145–174`; `test_access_request_submit_does_not_500_when_status_update_fails` |
| 3 | Access-request confirmation UI | FIXED / protected | `_render_access_request_thanks` (`public.py:319`); `test_access_request_thanks_*` |
| 4 | Unreadable dark-mode teaching boxes | FIXED / not protected | Admonition backgrounds derive from dark-redefined tokens (`00_tokens.css:144,156,911–975`); no dark-mode test; browser check needed |
| 5 | Player switching away from "All Items" | FIXED / partly protected (comparison); residual risk | `research-comparison.js:573–610`, `comparison-url-state.js:38–59`; `buildPlayerHref` always passes `set_id` of a saved draft, and no test asserts "Alle Items" is current in the player |
| 6 | No stop for whole-row playback | FIXED / not protected | `research-comparison.js:375–415,1614` |
| 7 | Unresolved standard-variety codes | FIXED / protected (unit) | `STANDARD_VARIETY_LABEL_KEYS` (`research_views.py:134–166`) covers all codes; `test_format_standard_variety_value_*` |
| 8 | Learner/native ordering | FIXED / protected | `sort_sessions_for_display` (`research_sessions.py:478`); `test_sort_sessions_for_display_*` |
| 9 | Consent/internal metadata on profiles | **STILL PRESENT** (and locked in by test) | `research_views.py:1054–1067`; S7 |
| 10 | French `théatre` → `théâtre` | FIXED in code / protected, data side UNKNOWN | `item_text_normalization.py`, `migrate_french_theatre_item.py`, `intake_storage.py:217`; runtime catalog test cannot run without `data/config` |

---

## 11. Content/multilingual findings

- **C1 – Legal pages depend on a planning document that is not in the image.** `routes/public_content.py:_legal_source_path` searches parent dirs for `docs/plans/impressum_datenschutz.md`; `app/Dockerfile` copies only `app/` and `content/`. In the locally built image the lookup raises `LegalContentError`, which no route handler catches → 500 on `/impressum`, `/<ui_lang>/impressum`, `/<ui_lang>/privacy`. The local test passes only because the repo checkout contains `docs/`. Also contradicts the docs rule that `docs/plans/` are planning inputs only. Highest-priority content item; production status UNKNOWN.
- **C2 – Corpus registry is scattered.** Corpora are listed in `routes/public_content.py:LANGUAGES` (effective registry), `research_capabilities.py:ACTIVE_RESEARCH_CORPORA` (unused), `config/data_conventions.py`, DB check constraint (`research_metadata.py:62`), `analytics.py:TRACKED_CORPORA`, `routes/admin.py:573`, teaching sort order. Adding a *fifth* language needs ~6 edits + migration. For German (already present everywhere) no change is needed.
- **C3 – Design pages are Spanish-only by code branch.** `routes/public_content.py:550` (`if language_slug != "spanish"` → placeholder) and `:573` (`design` → `SPANISH_DESIGN_PAGE_CONTENT`). A German design page currently needs another hard-coded dict + branch. Recommended: per-language design content files (YAML, same block model as teaching) looked up by slug.
- **C4 – Project pages duplicated.** `PROJECT_PAGES_CONTENT` (Python) is a hand copy of `docs/plans/project_pages/…md`; drift risk.
- **C5 – UI languages hard-coded to de/en** in a few places (`__init__.py:45,294–295`, `*_de/*_en` dataclass fields in `research_capabilities.py`). Fine for the declared de/en scope; would need work only if a third UI language is planned.
- **C6 – Teaching is fully declarative.** German and English teaching hubs exist with `groups: []`; adding German topics = adding YAML + media, validated by `scripts/validate_teaching_content.py` (which checks structure, not block schema).
- **C7 – `AGENTS.md` mentions `public/teaching/...`**, but teaching media are served from `content/teaching/**/media` via `/teaching-media/`. Documentation drift, no runtime effect.
- Intentional language-specific behaviour to keep: per-language standard varieties, task-capability matrix, Spanish productive-surface override (documented in `docs/spec/research-capabilities.md`), per-corpus people, French item normalisation.

---

## 12. Dependency/modernization findings

Runtime: Python 3.12 (`python:3.12-slim`, supported until 2028-10) — no change needed. Postgres 15 (supported until 2027-11), Redis 7 — fine.

| Package | Present | Target | Reason | Benefit | Risk | Before German? |
|---|---|---|---|---|---|---|
| werkzeug (via Flask) | 3.1.3 | ≥3.1.6 | 3 advisories | security | low (patch) | yes, in the refresh run |
| flask | 3.1.2 | 3.1.3 | advisory | security | low | yes |
| urllib3 | 2.5.0 | ≥2.8.0 | 7 advisories | security | low | yes |
| pyjwt | 2.10.1 | ≥2.15 | several advisories | security of auth tokens | low–medium (verify Flask-JWT-Extended compat, run auth tests) | yes |
| requests, idna, python-dotenv, pygments, anyio, click | various | patch | advisories | security | low | yes |
| gunicorn | 23.0.0 | latest 2x/26.x | currency | minor | medium (major); 23 has no listed advisory | no |
| SQLAlchemy | 2.0.43 | 2.0.x latest | patch | — | low; **do not** jump to 2.1 now | no |
| passlib | 1.7.4 | (unmaintained) | uses deprecated `crypt`, removed in Python 3.13 | future runtime upgrade | medium (replace with `argon2-cffi` direct + verify legacy hashes) | no, before Python 3.13 |
| redis client | 5.2.1 | 6.x+ | currency | — | low | no |
| psycopg2-binary | 2.9.10 | 2.9.13 | patch | — | low | no |

Other observations: `requirements.in` header still says "CO.RA.PAN web app"; `pydub` appears unused by intake (`ffmpeg_audio.py` uses subprocess) — verify and drop later; Dependabot opens PRs but none appear merged (lockfile from 2025) — decide a cadence (e.g. monthly patch refresh) rather than auto-merge. No frontend toolchain to modernise. Do **not** "upgrade everything".

---

## 13. Documentation findings

| Question | Answerable from repo? | Where / gap |
|---|---|---|
| Set up the project | Yes, Windows-centric | `docs/runbooks/local-dev-start.md`, `scripts/dev-*.ps1`; no Linux/macOS path; `README.md` minimal |
| Run tests | Partly | CI files show it; no runbook; tests depend on local data (I1/I2) |
| How deployment works | Partly | `deploy.yml`, `deploy_prod.sh`; server prep in `docs/plans/prep_prod/prep_server.md` (a *plan*, contains now-outdated "not yet present" statements) — no deployment runbook |
| Add a language | No | scattered registry (C2) — needs a checklist in spec/runbook |
| Add research data | Yes | intake runbooks + `scripts/research_data_intake/README.md` (depends on unversioned script) |
| Add a research-design page | No | code-only today |
| Add a teaching/theme page | Partly | `content/teaching_import/README.md`, validator; no authoring runbook |
| Back up | **No** | none |
| Restore | **No** | none |
| Create a scientific release | **No** | none |
| Roll back a bad deployment | **No** | only a `rollback_hint` for data publish in `publish_prod_release.py:202` |

Additional drift: `docs/performance-*.md` sit at `docs/` root outside the documented buckets; `.github/CODEOWNERS` placeholder by design.

---

## 14. Risk register

| ID | Finding | Evidence | Impact | Likelihood | Priority | Recommended action |
|---|---|---|---|---|---|---|
| R01 | Deploy runs regardless of CI result | `.github/workflows/deploy.yml` (on push main, no dependency); runs 216/110 started same second | High: broken code reaches prod | Medium | **A** | Make deploy depend on successful CI (`workflow_run` on CI success, or single workflow with `needs`) |
| R02 | CI runs only a smoke subset; full suite red since June | `ci.yml` named tests; §10.1 | High: regressions invisible | Certain (already happened) | **A** | Fix/realign failing tests, then run full suite + Docker build in CI |
| R03 | Legal pages likely 500 in prod image | `public_content.py:643–651`, `app/Dockerfile`; image check | High (legal obligation: Impressum) | High | **A** (verify today) | Move legal source into `content/legal/` (copied into image) and add post-deploy page smoke |
| R04 | Intake importer imports unversioned module | `import_batch_to_production.py:64`, `.gitignore` `scripts/research_data_intake/import/*` | High: intake irreproducible, single-machine dependency | High | **A** | Commit `organize_batch_working_tree.py` to a tracked path; keep only batch data ignored |
| R05 | Canonical task catalogs/player configs not versioned | `.gitignore` `data/config/*`; spec `data/config/` section; 8 failing tests | High: loss of scholarly content, untestable | Medium | **A/B** | Version catalogs (tracked path or data repo) and point tests at fixtures |
| R06 | No DB or source-data backup/restore documented | no `pg_dump`/backup in repo; runbook references "existing backup path" | Very high if disk/laptop lost | Low–Medium | **A** | Nightly `pg_dump` + off-host copy; source archive second copy; restore test |
| R07 | Corpus-root login return target regressed | `public_content.py:529`, commits `1705434`→`bc5ffd2` | Medium UX | Certain | **B** | Restore `:speakers` target (tests already exist) |
| R08 | Consent/internal metadata shown on profiles | `research_views.py:1054–1067`; importer writes fields | Medium (data protection) | Certain where fields set | **B** | Remove internal rows from profile; stop writing consent fields into runtime metadata; invert test |
| R09 | Reset-link host poisoning | `auth_mail_messages.py:39`, `__init__.py:185`, unused `PROMAT_PUBLIC_BASE_URL` | High (account takeover) | Low–Medium (depends on nginx) | **B** | Build links from `PROMAT_PUBLIC_BASE_URL`; `TRUSTED_HOSTS` |
| R10 | `JWT_SECRET_KEY` not validated | `config/__init__.py:~207`, template default | Critical if default used | Low (verify) | **A (verify) / B (fix)** | Operator confirms value; startup check for length/default |
| R11 | Set-label HTML injection | `_content_header.html:35`, `research_phenomena_views.py:518,549` | Medium | Low | B | Remove `|safe` fallback |
| R12 | Publish config gap (`config/` not synced to `data/config`) | `publish_prod_release.py` sync block; `research_presets.py:105` | Medium: German catalogs might not reach app | Unknown | **B** | Verify server layout; sync config like sessions |
| R13 | Publish: DB committed before files switched; rm-rf window | `publish_prod_release.py:~217–231` | Medium, transient inconsistency | Low | C | Sync to temp + rename; DB step after file switch or document recovery |
| R14 | Deploy recreates DB/Redis each time; migrations without pre-backup | `deploy_prod.sh` | Medium | Low | B | Recreate `web` only; `pg_dump` before migrations |
| R15 | 49 dependency advisories | `pip-audit` | Medium | Medium | B | Patch-level lock refresh, run full suite |
| R16 | Design pages hard-coded to Spanish in Python | `public_content.py:550,573`; `public_page_content_data.py` | Blocks German design page cleanly; DOI export | Certain | B | File-based design content model |
| R17 | No rollback procedure / image tags | `deploy.yml`, `deploy_prod.sh` | Medium | Low | C | Tag images per SHA; rollback runbook |
| R18 | Reset tokens in access logs; no access-request retention | Dockerfile CMD; migration 0008 | Low–Medium (privacy) | Medium | C | Token in POST/fragment or log filter; retention job |
| R19 | GoatCounter on protected routes with IDs | `base.html:39`, `__init__.py:279–288` | Low–Medium (privacy) | Certain | C | Exclude `/research/*/speakers|player` paths or strip IDs |
| R20 | `/ready` leaks exception text, unthrottled | `public.py:822–863` | Low | Low | C | Generic message externally; restrict to localhost |
| R21 | No content/data licence, no release model | only `app/LICENSE` | Blocks DOI | Certain | C (before first DOI) | Decide licences; add release metadata |
| R22 | passlib uses removed-in-3.13 `crypt` | DeprecationWarning in test run | Blocks Python 3.13 | Later | C | Replace passlib when upgrading Python |

---

## 15. Prioritized work

### A. Required before further substantial development

1. Gate production deployment on a successful CI run (R01) and add branch protection requiring CI.
2. Make the full test suite green and self-contained on a clean checkout: version `organize_batch_working_tree.py` (R04), provide catalog fixtures or versioned catalogs for tests (R05), update the two drifted tests after confirming intent, then run the full suite + Docker build in CI (R02).
3. Verify `/impressum` and `/privacy` in production today; move the legal source into the image (`content/`), add a post-deploy smoke for 4–5 public pages (R03, D7).
4. Establish and test a minimal backup: nightly `pg_dump`, off-host copy, second copy of the local source archive, one restore test (R06). Operator verifies `JWT_SECRET_KEY` (R10).

### B. Recommended before German data/content expansion

1. Version canonical task catalogs/player configs and fix/verify the publish path for config (R05, R12); create German catalogs under that model.
2. German intake dry-run on one speaker end-to-end (local), including MFA `german_mfa`, quote normalisation, package validation; make `--target-language` mandatory.
3. Fix the corpus-root login regression (R07) and remove consent/internal metadata from speaker profiles (R08).
4. Security patch set: reset links from `PROMAT_PUBLIC_BASE_URL` + trusted hosts (R09), JWT secret startup check (R10), remove `|safe` fallback (R11), patch-level dependency refresh (R15).
5. File-based research-design content model, migrate Spanish design page, so the German design page is content, not code (R16).
6. Deploy hygiene: recreate only `web`, dump before migrations (R14).

### C. Valuable later

- Image tag per SHA + rollback runbook (R17).
- Publish atomicity for sessions sync; write publish log on failure (R13, I5).
- Privacy: access-request retention, GoatCounter scope, reset token logging (R18, R19).
- Single corpus registry (C2); project pages from one source (C4).
- Static asset caching via nginx (P1).
- DOI/release model: licences, `CITATION.cff`, snapshot exporter for teaching/design pages, corpus release manifest (§7, R21).
- Token revocation / user-status check (S4); login timing equalisation (S8); `/ready` hardening (R20).
- Replace passlib before Python 3.13 (R22); `.dockerignore`, non-root container user.
- Tests for row-stop playback, "All Items" default in player, dark-mode teaching boxes (browser check).

### D. Do not change / no current action

- The intake classification model, archive layout, package/manifest/checksum mechanism and staged-release publish — extend, don't replace.
- SSH-based upload/publish workflow — appropriate for one operator; no need for a data API or object store.
- Flask + Jinja + vanilla JS stack; no SPA/bundler migration.
- `data/` read-only mount and code/data separation on the server.
- Teaching YAML content model (extend with version/licence only).
- Spec-driven governance and the `docs/` bucket rules.
- No staging environment for now.
- Python 3.12, Postgres 15, SQLAlchemy 2.0 — no major upgrades now.
- Intentional per-language methodology (standard varieties, task matrix, French normalisation).

---

## 16. Proposed next agent runs

### Run 1 – Production safety gates and reproducible test suite
- **Objective:** `main` deploys only green, fully tested code; the suite runs on a clean checkout.
- **Why:** R01, R02, R04, part of R05; the regression in R07 went unnoticed because of this.
- **Scope:** make `deploy.yml` depend on CI success; extend `ci.yml` with full `pytest tests` and `docker build`; track `organize_batch_working_tree.py` (move out of the ignored `import/` dir or un-ignore that single file, adjust import path); add minimal catalog fixtures under `app/tests/fixtures/` and point data-dependent tests at them (or skip with explicit `data` marker); update the two drifted tests after confirming the wording with the operator; add post-deploy `curl -f` checks for `/de`, `/en`, `/de/research/spanish/design`, `/de/teaching`, `/impressum`. Do not fix product bugs here except as needed to make tests meaningful (the R07 regression test stays red until Run 3, or fix it here if the operator confirms — it is a one-line change).
- **Files:** `.github/workflows/{ci,deploy}.yml`, `scripts/deploy_prod.sh`, `.gitignore`, `scripts/research_data_intake/import*/`, `app/tests/**`, `docs/runbooks/` (new deploy runbook), `docs/spec/platform-data-files.md` if paths change.
- **Acceptance:** clean clone → `pytest tests` all pass or are explicitly marked; CI runs full suite + Docker build; a deliberately failing CI run does not deploy (verify on a branch with `workflow_dispatch` dry-run logic, not on `main`); deploy runbook exists.
- **Dependencies:** none.
- **Production risk:** medium (changes the deploy workflow) — merge during a quiet window, watch the first deploy.
- **Model:** Sonnet 5.5 Medium.

### Run 2 – Legal-page fix, backup/restore foundation, deploy hygiene
- **Objective:** legal pages guaranteed in the image; documented, tested backup and restore.
- **Why:** R03, R06, R14, R10 check.
- **Scope:** move `impressum_datenschutz.md` content to `content/legal/` (copied by Dockerfile) and update `_legal_source_path`; add a test that runs against the image layout; add `scripts/backup_prod_db.sh` (pg_dump via `docker exec`, rotation) and a cron/systemd snippet in a runbook (operator installs it); `deploy_prod.sh`: dump before migrations, recreate only `web`; runbooks `backup-and-restore.md` and `deploy-rollback.md`; startup check rejecting default/short `JWT_SECRET_KEY`.
- **Files:** `app/src/app/routes/public_content.py`, `app/Dockerfile`, `content/legal/`, `scripts/deploy_prod.sh`, `scripts/`, `docs/runbooks/`, `docs/spec/platform-data-files.md`, `app/src/app/config/__init__.py`.
- **Acceptance:** image-level legal test passes; restore of a dump into a scratch Postgres documented and executed once by the operator; deploy no longer restarts DB.
- **Dependencies:** Run 1 (so changes are CI-gated).
- **Production risk:** medium (deploy script, startup check could refuse start if the prod JWT secret is weak — operator must verify first).
- **Model:** Sonnet 5.5 Medium.

### Run 3 – Security and privacy patch set
- **Objective:** close the confirmed security/privacy issues.
- **Why:** R07, R08, R09, R11, R15.
- **Scope:** reset/invite links from `PROMAT_PUBLIC_BASE_URL`, `TRUSTED_HOSTS`; remove `|safe` fallback for plain fields in `_content_header.html` (and audit `_teaching_blocks.html`/`_admonition.html` pattern); remove internal/consent rows from speaker profile, fix duplicate `origin_region`, invert the profile test, stop writing consent fields into runtime `metadata.json` in the importer; restore corpus-root login `:speakers`; patch-level lock refresh (`uv pip compile` with upgrades for the advisory packages only), full suite.
- **Files:** `app/src/app/services/auth_mail_messages.py`, `app/src/app/__init__.py`, `app/templates/partials/_content_header.html`, `app/src/app/research_views.py`, `app/src/app/routes/public_content.py`, `scripts/research_data_intake/import_batch_to_production.py`, `app/requirements.txt`, tests, `docs/spec/research-access.md` / `auth-accounts.md` as needed.
- **Acceptance:** tests for each fix; `pip-audit` clean or remaining items justified; bilingual browser check of profile and login pages per UI rules.
- **Dependencies:** Run 1.
- **Production risk:** low–medium.
- **Model:** Sonnet 5.5 Medium.

### Run 4 – German readiness: canonical config versioning and intake dry-run
- **Objective:** German research data can be imported with the existing pipeline.
- **Why:** R05, R12, §5 German assessment.
- **Scope:** decide and implement the versioned home of `research_player/**` catalogs/configs (tracked repo path vs. small data repo) and how they reach `data/config` on the server (package + publish sync); verify/fix the publish config sync; German quote normalisation in `_comparison_text`; make `--target-language` mandatory; add a synthetic German fixture batch test (filename classification, workbook, package validation); operator-run dry-run on one real German speaker following the runbook; update `docs/spec/platform-data-files.md`, `intake-workbook.md`, intake runbooks.
- **Files:** `scripts/research_data_intake/**`, `.gitignore`, `data/config` layout, `app/tests/test_research_*`, specs/runbooks.
- **Acceptance:** fixture test green in CI; one German speaker processed locally to a validated prod package; publish path for config verified against server layout (by operator).
- **Dependencies:** Run 1; ideally Run 2 (backup before first German publish).
- **Production risk:** low (local work); the eventual publish is operator-controlled.
- **Model:** Opus 5.5 Medium (open storage decision + pipeline diagnosis), or Sonnet 5.5 High if the operator decides the catalog location beforehand.

### Run 5 – File-based research-design content model (+ publication metadata fields)
- **Objective:** design pages become content files with structured metadata, enabling German design pages and later DOI snapshots.
- **Why:** R16, §7.
- **Scope:** define a YAML model for research-design pages reusing teaching block types and metadata (authors with roles/ORCID, created/updated, version, licence, citation, doi); loader + per-language lookup replacing `public_content.py:550,573` branches; migrate `SPANISH_DESIGN_PAGE_CONTENT` 1:1 (byte-equivalent rendered output as acceptance); add `version`/`license` to teaching metadata; spec update in `docs/spec/platform-data-files.md` / `research-capabilities.md`.
- **Files:** `app/src/app/routes/public_content.py`, `public_page_content_data.py`, `teaching_content.py` (shared parts), `content/research/<lang>/design/{de,en}.yaml`, templates, tests, validator.
- **Acceptance:** Spanish design page renders identically (diff of HTML), German design route renders from a placeholder YAML, bilingual browser screenshots, tests updated.
- **Dependencies:** Run 1.
- **Production risk:** medium (visible public page) — mitigated by render-diff test.
- **Model:** Sonnet 5.5 High.

(No separate DOI/export run is proposed yet: it should follow once licences and the university repository's metadata requirements are known; Run 5 lays the necessary groundwork.)

---

## 17. Unknowns requiring operator/server verification

| # | Unknown | Why it matters | How to answer (later, by operator) |
|---|---|---|---|
| U1 | Does `/impressum` / `/de/privacy` return 200 in production? | Legal obligation; code analysis predicts 500 | Open `https://pronunciation-matters.de/impressum` and `/de/privacy`; or on server `docker exec promat-web-prod ls /app/docs` and `docker logs promat-web-prod | grep LegalContentError` |
| U2 | Is the production `JWT_SECRET_KEY` strong and not `__CHANGE_ME__`? | Default → admin token forgery | On server: `grep -c '^JWT_SECRET_KEY=__CHANGE_ME__' /srv/webapps/promat/config/passwords.env` and check length (do not print the value) |
| U3 | nginx `Host`/`X-Forwarded-Host` handling | Decides exploitability of reset-link poisoning (S1) | `nginx -T | grep -A20 pronunciation-matters` — look for `proxy_set_header Host $host;` and whether `X-Forwarded-Host` is set/overwritten; also `server_name` default server behaviour |
| U4 | Is any backup of Postgres volume / `/srv/webapps_storage` in place (HRZ-level snapshots, cron)? | R06 priority | `crontab -l; ls /etc/cron.d; systemctl list-timers`; ask HRZ about VM snapshot policy |
| U5 | Second copy of `C:\dev\promat_data_archive` (source recordings, consent) | Only copy of irreplaceable data | Operator checks where the archive is mirrored (university storage, external disk) |
| U6 | Branch protection / required status checks on `main` | R01 | GitHub → Settings → Branches (or `gh api repos/FTacke/promat-webapp/branches/main/protection`) |
| U7 | How does the app read `config/research_player` on the server (symlink to `current/config`?) | R12, German catalogs | `ls -la /srv/webapps_storage/promat/data/ /srv/webapps_storage/promat/data/config` |
| U8 | Is `organize_batch_working_tree.py` on the operator machine the latest version and under any backup? | R04 | Operator: `git status --ignored scripts/research_data_intake/import/` locally |
| U9 | Current French runtime catalog contains `théâtre` (historical correction applied in prod) | Historical item 10 | `grep -c 'théatre' /srv/webapps/promat/data/config/research_player/french/task_catalogs/wordlist.json` and DB check per `migrate_french_theatre_item.py` docs |
| U10 | Static asset caching / compression at nginx | P1 | `curl -sI https://pronunciation-matters.de/static/fonts/Inter-Variable.woff2` (Cache-Control, Content-Encoding) |
| U11 | Server user and permissions of the self-hosted runner (docker group = root-equivalent) | Least privilege | `ps -o user= -C Runner.Listener`; `id <runner-user>` |
| U12 | Does `apply_auth_migration.py` wrap each SQL file in a transaction on Postgres? | Partial-migration risk (D5) | Read `app/scripts/apply_auth_migration.py` with a dry run against a scratch Postgres |
| U13 | Live security headers and cookie flags as actually served | Confirm §8 assumptions | `curl -sI https://pronunciation-matters.de/de` from a normal network |
| U14 | Whether the corpus-root login regression is visible live | R07 | Logged out, open `/de/research/spanish` and inspect the login link `next` value |

(The cloud environment used for this audit blocks outbound access to `pronunciation-matters.de`; U1, U10, U13 and U14 are simple read-only checks from any normal network.)
