# v0.7 Production Deployment Repo Prep

## 1. Scope

Prepared the repository for the first controlled v0.7 production deployment on `vhrz2184`.

This run changed repository files only. It did not touch the server runtime, did not deploy, did not run data imports, did not run real mails, and did not run migrations against a real production database.

## 2. Target Model

The repo now matches the initial data-only server model:

| Item | Value |
| --- | --- |
| App root | `/srv/webapps/promat` |
| Persistent checkout | `/srv/webapps/promat/app` |
| Env file | `/srv/webapps/promat/config/passwords.env` |
| Data bind | `/srv/webapps/promat/data:/app/data:ro` |
| Logs bind | `/srv/webapps/promat/logs:/app/logs` |
| Local upstream | `127.0.0.1:8000 -> container:5000` |
| Web container | `promat-web-prod` |
| DB container | `promat-db-prod` |
| Rate-limit container | `promat-rate-limit-prod` |
| Network | `promat-network-prod` |
| DB volume | `promat_postgres_prod` |
| Compose project | `promat-prod` |
| Runner label | `promat-prod` |
| Public base URL | `https://pronunciation-matters.de` |

No separate `/srv/webapps/promat/media` bind mount is part of the v0.7 initial deployment. No `/app/media` runtime dependency was found.

## 3. Changed Files

| File | Change |
| --- | --- |
| `infra/docker-compose.prod.yml` | Added canonical production Compose file with ProMat-specific service/container/network/volume names, loopback-only port binding, data/logs mounts, Redis-backed limiter service, and web healthcheck. |
| `app/infra/docker-compose.prod.yml` | Removed the old production Compose location so production deployment uses the repo-root `infra/` path. |
| `scripts/deploy_prod.sh` | Added strict production deploy script for the persistent server checkout; validates env/data/log paths, uses Compose v2, runs safe auth migrations, waits for health, and checks `/health` plus `/ready`. |
| `.github/workflows/deploy.yml` | Added self-hosted deploy workflow using runner label `promat-prod` and persistent checkout `/srv/webapps/promat/app`. |
| `.github/workflows/ci.yml`, `.github/workflows/full-test.yml`, `.github/workflows/release-candidate-check.yml` | Updated Compose config validation to the new `infra/docker-compose.prod.yml` path. |
| `app/passwords.env.template` | Updated required production env-key template for the v0.7 server model and access-request mail transport. |
| `app/src/app/config/__init__.py` | Made `PROMAT_ENV` the leading environment selector and exposed `PROMAT_PUBLIC_BASE_URL`. |
| `app/src/app/runtime_paths.py` | Made dev-environment detection honor `PROMAT_ENV`. |
| `app/src/app/routes/public.py` | Changed `/health` to liveness-only and added `/ready` with DB, data-root, logs-dir, and production rate-limit sanity checks. |
| `app/src/app/__init__.py`, `app/src/app/analytics.py`, `app/src/app/extensions/__init__.py` | Excluded `/ready` from auth-context gating, analytics, and rate limiting like `/health`. |
| `app/tests/test_auth_phase1.py`, `app/tests/test_runtime_config.py` | Added readiness and `PROMAT_ENV` regression coverage. |
| `AGENTS.md`, `.github/copilot-instructions.md`, `README.md` | Updated active runtime wiring references to the new production Compose path. |
| `docs/spec/platform-data-files.md` | Clarified the initial v0.7 data-only production model and upload target path. |
| `docs/plans/prep_prod/prep_server.md` | Aligned the server-prep plan with the data-only model and removed the initial media-mount assumption. |

## 4. Production Commands

The deploy workflow runs on the server checkout:

```bash
cd /srv/webapps/promat/app
git fetch --prune origin
git checkout --force "$GITHUB_SHA"
git reset --hard "$GITHUB_SHA"
bash scripts/deploy_prod.sh
```

The deploy script uses this Compose pattern:

```bash
docker compose -p promat-prod --env-file /srv/webapps/promat/config/passwords.env -f infra/docker-compose.prod.yml <subcommand>
```

The web deployment step is:

```bash
docker compose -p promat-prod --env-file /srv/webapps/promat/config/passwords.env -f infra/docker-compose.prod.yml up -d --build --force-recreate
```

The script never calls `docker compose down` and only addresses ProMat-specific containers and services.

## 5. Required Env Keys

`/srv/webapps/promat/config/passwords.env` must provide these keys before first deployment:

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
APP_REPOSITORY_URL
APP_RELEASE_TAG
APP_RELEASE_URL
GUNICORN_WORKERS
GUNICORN_TIMEOUT
```

The template contains placeholders only. The operator must set real secrets and ensure `AUTH_DATABASE_URL` matches the production PostgreSQL credentials.

## 6. Health, Readiness, And Migrations

`/health` is now liveness-only and returns a small non-secret payload when the process responds.

`/ready` returns 200 only when:

- the auth DB can be reached,
- the required `users` table exists,
- `/app/data` is present and readable,
- `/app/logs` is present and writable,
- `RATE_LIMIT_STORAGE_URI` is configured and is not `memory://` in production.

`/ready` does not check `/app/media`.

The production image already uses Gunicorn:

```text
gunicorn --bind 0.0.0.0:5000 ... src.app.main:app
```

The deploy script applies non-destructive auth migrations before starting the recreated web service:

```bash
python scripts/apply_auth_migration.py --engine postgres
```

If migrations are missing or the schema is absent, `/ready` fails with a non-secret diagnostic instead of reporting readiness.

## 7. Data Upload And Media Model

The active production data contract now states:

- prod upload packages target `/srv/webapps_storage/promat/data/incoming/{upload_id}/`,
- server-side promotion goes `incoming -> releases -> current`,
- no direct write to `current`,
- no `rsync --delete`,
- no separate media mount in the initial v0.7 deployment,
- forbidden upload contents remain blocked: WAV, TextGrid, XLSX, secure, raw, source, alignment_source, working, MFA directories, PDFs, and temp files.

No upload/promotion implementation was added in this run. That remains a follow-up unless first deployment requires production data promotion before app startup.

## 8. Validation

| Command | Result |
| --- | --- |
| `python -m compileall app` | passed |
| `.venv\Scripts\python.exe -m ruff check .` | passed |
| YAML parse for `.github/workflows/*.yml` | passed |
| `docker compose --env-file app/passwords.env.template -f infra/docker-compose.prod.yml config` | passed |
| `docker run --rm ... alpine:3.20 ... bash -n scripts/deploy_prod.sh` | passed |
| `.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q` | 70 passed |
| `node --test app/tests/js/*.test.mjs` | 7 passed |
| `.venv\Scripts\python.exe -m pytest app/tests -q` | 478 passed |
| `docker build -f app/Dockerfile -t promat-v07-prod-prep-check .` | passed |
| `git diff --check` | passed |

The full app test run reported the existing Flask-Limiter in-memory warnings in testing contexts only. Production config still fails fast for missing or `memory://` rate-limit storage.

## 9. Not Done

- No server runtime changes.
- No deployment.
- No GitHub runner registration.
- No Nginx, Certbot, or TLS changes.
- No data imports.
- No real production migrations.
- No real mail delivery.
- No content or Teaching data changes.
- No `/app/media` or `/srv/webapps/promat/media` mount.

## 10. Remaining Blockers Before First Deploy

1. Create and permission `/srv/webapps/promat/{app,config,runner,data,logs}` on the server.
2. Normalize the prepared storage path to `/srv/webapps_storage/promat` only after explicit server-side approval.
3. Bind `/srv/webapps_storage/promat/data` to `/srv/webapps/promat/data`.
4. Populate `/srv/webapps/promat/config/passwords.env` with real secrets and matching PostgreSQL/SMTP values.
5. Register the self-hosted GitHub runner with label `promat-prod`.
6. Prepare Nginx and TLS for `pronunciation-matters.de` and optionally `www.pronunciation-matters.de`.
7. Define the first production data promotion step if the initial app launch should include research runtime data.
8. Run the first controlled deployment and post-deploy smoke checks on the server.
