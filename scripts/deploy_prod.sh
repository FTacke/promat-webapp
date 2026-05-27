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
      echo "Container status before failure:"
      docker ps --filter "name=promat-" --format 'table {{.Names}}\t{{.Status}}'
      docker logs --tail 80 "${service}" || true
      fail "${service} did not become healthy."
    fi
    sleep 2
  done
done

echo "Building web image..."
compose build web

echo "Applying non-destructive database migrations..."
compose run --rm --no-deps web python scripts/apply_auth_migration.py --engine postgres

echo "Starting web service..."
compose up -d --build --force-recreate

echo "Waiting for Docker health on ${WEB_CONTAINER}..."
for attempt in $(seq 1 60); do
  status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${WEB_CONTAINER}" 2>/dev/null || true)"
  if [[ "${status}" == "healthy" ]]; then
    echo "${WEB_CONTAINER}: healthy"
    break
  fi
  if [[ "${attempt}" == "60" ]]; then
    echo "Container status before failure:"
    docker ps --filter "name=promat-" --format 'table {{.Names}}\t{{.Status}}'
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
