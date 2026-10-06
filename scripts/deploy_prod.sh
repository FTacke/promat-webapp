#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/srv/webapps/promat"
ENV_FILE="${APP_ROOT}/config/passwords.env"
COMPOSE_FILE="infra/docker-compose.prod.yml"
PROJECT_NAME="promat-prod"
WEB_CONTAINER="promat-web-prod"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

compose() {
  docker compose -p "${PROJECT_NAME}" --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" "$@"
}

print_diagnostics() {
  echo "Compose service status:"
  compose ps || true
  echo "Container health/status:"
  docker ps --filter "name=promat-" --format 'table {{.Names}}\t{{.Status}}' || true
}

if [[ ! -f "app/Dockerfile" || ! -f "${COMPOSE_FILE}" || ! -d ".git" ]]; then
  fail "scripts/deploy_prod.sh must be run from the PROMAT repository root."
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  fail "Missing production env file: ${ENV_FILE}"
fi

if [[ ! -d "${APP_ROOT}/data" ]]; then
  fail "Missing production data directory: ${APP_ROOT}/data"
fi

if [[ ! -r "${APP_ROOT}/data" ]]; then
  fail "Production data directory is not readable: ${APP_ROOT}/data"
fi

if [[ ! -d "${APP_ROOT}/logs" ]]; then
  fail "Missing production logs directory: ${APP_ROOT}/logs"
fi

if [[ ! -w "${APP_ROOT}/logs" ]]; then
  fail "Production logs directory is not writable: ${APP_ROOT}/logs"
fi

if ! docker compose version >/dev/null 2>&1; then
  fail "Docker Compose v2 is required."
fi

echo "Deploying PROMAT production from $(pwd)"
echo "Compose project: ${PROJECT_NAME}"
echo "Compose file: ${COMPOSE_FILE}"
echo "Env file: ${ENV_FILE}"

echo "Starting database and rate-limit services..."
compose up -d db rate_limit

echo "Waiting for PostgreSQL and rate-limit services..."
for service in promat-db-prod promat-rate-limit-prod; do
  for attempt in $(seq 1 60); do
    status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${service}" 2>/dev/null || true)"
    if [[ "${status}" == "healthy" || "${status}" == "running" ]]; then
      echo "${service}: ${status}"
      break
    fi
    if [[ "${attempt}" == "60" ]]; then
      print_diagnostics
      docker logs --tail 80 "${service}" || true
      fail "${service} did not become healthy."
    fi
    sleep 2
  done
done

echo "Building web image..."
compose build web

# Fail before anything running is touched: load the production configuration exactly as the app does at startup
# (placeholder secrets, missing/invalid PROMAT_PUBLIC_BASE_URL, rate-limit store, ...). The running web container
# keeps serving until this passes, because `compose run --rm` starts a separate throw-away container.
echo "Validating production configuration with the new image..."
compose run --rm --no-deps web python -c 'from flask import Flask; from src.app.config import load_config; load_config(Flask("preflight"))' \
  || fail "Production configuration is invalid; the running services were not changed. See the error above."

# A migration must never run without a fresh, verified backup. backup_prod_db.sh validates the dump with
# pg_restore --list before keeping it and exits non-zero otherwise, which aborts the deploy here, before any
# schema change and before the running web container is touched. A brand-new database (no users table yet) has
# nothing to back up.
echo "Backing up the database before migrations..."
HAS_AUTH_SCHEMA="$(docker exec -i promat-db-prod sh -c 'psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --no-psqlrc --tuples-only --no-align' <<< "SELECT to_regclass('public.users') IS NOT NULL;" | tr -d '[:space:]')"   || fail "Could not inspect the database before the backup; no migration was applied."
if [[ "${HAS_AUTH_SCHEMA}" == "t" ]]; then
  bash scripts/backup_prod_db.sh --container promat-db-prod     || fail "Database backup failed; no migration was applied and the running services were not changed."
else
  echo "Database has no auth schema yet (first deployment); skipping the pre-migration backup."
fi

echo "Applying non-destructive database migrations..."
compose run --rm --no-deps web python scripts/apply_auth_migration.py --engine postgres

# Only the web container is replaced. PostgreSQL and the rate-limit Redis are infrastructure with their own
# lifecycle: restarting them on every application deploy interrupts open connections for no benefit, and a
# database restart is never required to ship application code. `compose up -d db rate_limit` above still
# recreates either one if (and only if) its definition in the compose file changed, which is the intended
# way to roll out a Postgres/Redis change. `--no-deps` keeps Compose from touching them here, and the
# image was already built by `compose build web`.
echo "Starting web service (database and rate-limit services stay running)..."
compose up -d --no-deps --force-recreate web

echo "Waiting for Docker health on ${WEB_CONTAINER}..."
for attempt in $(seq 1 60); do
  status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${WEB_CONTAINER}" 2>/dev/null || true)"
  if [[ "${status}" == "healthy" ]]; then
    echo "${WEB_CONTAINER}: healthy"
    break
  fi
  if [[ "${attempt}" == "60" ]]; then
    print_diagnostics
    echo "Recent web logs:"
    docker logs --tail 120 "${WEB_CONTAINER}" || true
    fail "${WEB_CONTAINER} did not become healthy."
  fi
  sleep 2
done

echo "Checking local health endpoint..."
curl -fsS http://127.0.0.1:8000/health >/dev/null

echo "Checking local readiness endpoint..."
curl -fsS http://127.0.0.1:8000/ready >/dev/null

echo "PROMAT production deploy completed."
