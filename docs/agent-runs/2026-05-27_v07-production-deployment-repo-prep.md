# v0.7 Production Deployment Repo Prep

## 1. Scope

Prepared and re-checked the repository-side production deployment wiring for the first controlled PROMAT v0.7 deployment on `vhrz2184`.

This run was repo-only:

- no SSH
- no server runtime changes
- no Docker runtime changes
- no nginx, certbot, systemd, runner, database, mount, permission, or server-file changes
- no data imports
- no real mail delivery
- no production migrations against real data

## 2. Mandatory Context Reviewed

- `docs/spec/platform-data-files.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- no `infra/AGENTS.md` exists
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `infra/docker-compose.prod.yml`
- `app/Dockerfile`
- `/health` and `/ready` implementation in `app/src/app/routes/public.py`
- access-request mail implementation in `app/src/app/services/access_request_notifications.py`
- auth migration script `app/scripts/apply_auth_migration.py`

## 3. Current Deployment Model

| Item | Value |
| --- | --- |
| Checkout | `/srv/webapps/promat/app` |
| Env file | `/srv/webapps/promat/config/passwords.env` |
| Data bind | `/srv/webapps/promat/data:/app/data:ro` |
| Logs bind | `/srv/webapps/promat/logs:/app/logs` |
| Local upstream | `127.0.0.1:8000 -> container:5000` |
| Web container | `promat-web-prod` |
| DB container | `promat-db-prod` |
| Rate-limit container | `promat-rate-limit-prod` |
| Network | `promat-network-prod` |
| DB volume | `promat_postgres_prod` |
| Compose project | external `-p promat-prod` |
| Runner label | `promat-prod` |
| Public domain | `https://pronunciation-matters.de` |

No production `/app/media`, `/srv/webapps/promat/media`, `/srv/webapps_storage/promat/media`, `PROMAT_MEDIA_ROOT`, or `MEDIA_ROOT` dependency was found in productive deployment/runtime code.

## 4. Changes

| File | Change |
| --- | --- |
| `infra/docker-compose.prod.yml` | Removed the static Compose `name:` so the project name is supplied externally via `docker compose -p promat-prod`; kept ProMat-specific containers, network, volumes, loopback port binding, data/logs mounts, DB and web healthchecks, and Gunicorn-based web image. |
| `scripts/deploy_prod.sh` | Added `docker compose ps` based non-secret diagnostics on failures while keeping strict bash, repo-root validation, server env-file validation, Docker Compose v2 requirement, health/readiness checks, and no `down` behavior. |
| `app/passwords.env.template` | Replaced example SMTP/database/mail values with explicit placeholders; removed optional release/admin helper values from the template so it stays a production env-key scaffold rather than an accidental config source. |
| `docs/plans/prep_prod/prep_server.md` | Updated the plan to the 2026-05-27 server state supplied in the task: phases C-E are already complete, data bind is active, no media mount exists, and remaining runtime work starts with runner/checkout/secrets. |

The active spec already contained the v0.7 data-only production rule, so no further `docs/spec/platform-data-files.md` change was needed in this follow-up.

## 5. Production Commands

The deploy workflow operates on the persistent checkout:

```bash
cd /srv/webapps/promat/app
git fetch --prune origin
git checkout --force "$GITHUB_SHA"
git reset --hard "$GITHUB_SHA"
bash scripts/deploy_prod.sh
```

The deploy script uses this Compose command pattern:

```bash
docker compose -p promat-prod --env-file /srv/webapps/promat/config/passwords.env -f infra/docker-compose.prod.yml <subcommand>
```

The production deploy command is:

```bash
docker compose -p promat-prod --env-file /srv/webapps/promat/config/passwords.env -f infra/docker-compose.prod.yml up -d --build --force-recreate
```

The script never calls `docker compose down`, never references a media mount, and only targets ProMat-named services/containers.

## 6. Required Env Keys

`/srv/webapps/promat/config/passwords.env` must provide real values for:

```text
PROMAT_ENV
PROMAT_PUBLIC_BASE_URL
FLASK_DEBUG
FLASK_SESSION_SECURE
FLASK_SESSION_SAMESITE
PROMAT_RUNTIME_ROOT
PROMAT_PUBLIC_ROOT
PROMAT_TEACHING_CONTENT_ROOT
FLASK_SECRET_KEY
JWT_SECRET_KEY
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
AUTH_DATABASE_URL
RATE_LIMIT_STORAGE_URI
AUTH_HASH_ALGO
AUTH_ACCESS_REQUEST_MAIL_ENABLED
AUTH_ACCESS_REQUEST_EMAIL
AUTH_ACCESS_REQUEST_SUBJECT
AUTH_ACCESS_REQUEST_FROM_EMAIL
AUTH_ACCESS_REQUEST_REPLY_TO_ENABLED
AUTH_ACCESS_REQUEST_SMTP_HOST
AUTH_ACCESS_REQUEST_SMTP_PORT
AUTH_ACCESS_REQUEST_SMTP_USERNAME
AUTH_ACCESS_REQUEST_SMTP_PASSWORD
AUTH_ACCESS_REQUEST_SMTP_USE_TLS
AUTH_ACCESS_REQUEST_SMTP_USE_SSL
AUTH_ACCESS_REQUEST_SMTP_TIMEOUT_SECONDS
AUTH_ACCESS_REQUEST_FORM_MAX_AGE_SECONDS
AUTH_ACCESS_REQUEST_MIN_SUBMIT_SECONDS
```

The repo template contains placeholders only. Secrets and provider-specific values belong only on the server.

## 7. Health, Readiness, And Migration Behavior

- `/health` is liveness-only.
- `/ready` verifies auth DB connectivity, required `users` table presence, data-root readability, logs-dir writability, and production rate-limit backend sanity.
- `/ready` does not check or require `/app/media`.
- Production config fails fast if `RATE_LIMIT_STORAGE_URI` is missing or `memory://`.
- The production image uses Gunicorn bound to `0.0.0.0:5000`.
- The deploy script runs the existing non-destructive auth migration path before web startup:

```bash
python scripts/apply_auth_migration.py --engine postgres
```

If migrations/schema are missing, readiness fails with a non-secret diagnostic instead of silently reporting ready.

## 8. Data Upload / Promotion Alignment

The active spec remains aligned with the data-only model:

- uploads target `/srv/webapps_storage/promat/data/incoming/{upload_id}/`
- promotion is `incoming -> data/releases/{release_id} -> data/current`
- no direct rsync to `current`
- no `rsync --delete`
- no media mount assumption
- forbidden upload contents stay blocked: WAV, TextGrid, XLSX, secure, raw, source, alignment_source, working, `mfa_corpus`, `mfa_output`, PDFs, and temp files

No upload/promotion script was added in this run.

## 9. Validation

| Command | Result |
| --- | --- |
| `.venv\Scripts\python.exe -m ruff check .` | passed |
| `python -m compileall app` | passed |
| YAML parse for `.github/workflows/*.yml` | passed |
| `docker compose --env-file app/passwords.env.template -f infra/docker-compose.prod.yml config` | passed |
| `docker run --rm ... alpine:3.20 ... bash -n scripts/deploy_prod.sh` | passed |
| `.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q` | 70 passed |
| `.venv\Scripts\python.exe -m pytest app/tests -q -k "security_headers or csp or access_request or runtime_config or health or ready"` | 21 passed |
| `node --test app/tests/js/*.test.mjs` | 7 passed |
| `docker build -f app/Dockerfile -t promat-v07-prod-prep-check .` | passed |
| `.venv\Scripts\python.exe -m pytest app/tests -q` | 478 passed |
| `git diff --check` | passed |

The full app test run still reports known test-context Flask-Limiter in-memory warnings. Production remains configured to reject missing or `memory://` rate-limit storage.

## 10. Final Diff Summary

Current run diff:

```text
app/passwords.env.template
docs/plans/prep_prod/prep_server.md
infra/docker-compose.prod.yml
scripts/deploy_prod.sh
docs/agent-runs/2026-05-27_v07-production-deployment-repo-prep.md
```

No `content/`, `content/teaching/`, or `public/teaching/` changes were made.

## 11. Remaining Blockers Before Runner Registration And First Deploy

1. Read-only recheck the server state reported in the task.
2. Register the ProMat self-hosted runner with label `promat-prod`.
3. Populate `/srv/webapps/promat/config/passwords.env` with real secrets and provider values.
4. Create or reset the persistent checkout under `/srv/webapps/promat/app`.
5. Run the first ProMat-only Compose deployment.
6. Verify local `/health` and `/ready` on `127.0.0.1:8000`.
7. Configure nginx/TLS only after explicit runtime approval.
8. Decide whether the first deployment needs an initial data promotion package before public exposure.
