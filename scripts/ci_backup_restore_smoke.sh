#!/usr/bin/env bash
# End-to-end rehearsal of the PostgreSQL backup/restore tooling against a throw-away database.
#
# Starts a disposable PostgreSQL container, applies the real migrations, seeds a few rows, takes a backup with
# scripts/backup_prod_db.sh, and verifies a restore into a second disposable container with
# scripts/verify_db_restore.sh. Used by CI and runnable locally (needs docker, and the Python dependencies of
# app/requirements.txt for the migration runner). Touches no production system.
#
# Usage: PYTHON=/path/to/python scripts/ci_backup_restore_smoke.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PYTHON:-python3}"
NAME="promat-backup-smoke-$$"
PORT="${PROMAT_SMOKE_DB_PORT:-55433}"
PASSWORD="$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 24)"
WORKDIR="$(mktemp -d)"

cleanup() {
  docker rm -f "${NAME}" >/dev/null 2>&1 || true
  rm -rf "${WORKDIR}"
}
trap cleanup EXIT

docker run -d --name "${NAME}" \
  -e POSTGRES_USER=promat_smoke \
  -e POSTGRES_PASSWORD="${PASSWORD}" \
  -e POSTGRES_DB=promat_smoke \
  -p "127.0.0.1:${PORT}:5432" \
  postgres:15 >/dev/null

for attempt in $(seq 1 60); do
  if docker exec "${NAME}" pg_isready --username promat_smoke --dbname promat_smoke >/dev/null 2>&1; then
    sleep 2
    docker exec "${NAME}" pg_isready --username promat_smoke --dbname promat_smoke >/dev/null 2>&1 && break
  fi
  [[ "${attempt}" -lt 60 ]] || { echo "ERROR: database did not become ready" >&2; exit 1; }
  sleep 1
done

(
  cd "${REPO_ROOT}/app"
  AUTH_DATABASE_URL="postgresql+psycopg2://promat_smoke:${PASSWORD}@127.0.0.1:${PORT}/promat_smoke" \
  PROMAT_RUNTIME_ROOT="${WORKDIR}" PROMAT_PUBLIC_ROOT="${WORKDIR}/public" \
    "${PYTHON}" scripts/apply_auth_migration.py --engine postgres >/dev/null
)

docker exec "${NAME}" psql --username promat_smoke --dbname promat_smoke -v ON_ERROR_STOP=1 --quiet --command \
  "INSERT INTO users (user_id, username, email, password_hash, role) VALUES
     ('smoke-1', 'alice', 'alice@example.test', 'not-a-real-hash', 'user'),
     ('smoke-2', 'bob', 'bob@example.test', 'not-a-real-hash', 'admin');"

"${SCRIPT_DIR}/backup_prod_db.sh" --container "${NAME}" --output-dir "${WORKDIR}/backups" --keep 3
DUMP="$(find "${WORKDIR}/backups" -name 'promat_db_*.dump' | head -n 1)"
"${SCRIPT_DIR}/verify_db_restore.sh" --dump "${DUMP}"
grep -q "^users	2$" "${DUMP}.counts.tsv" || { echo "ERROR: users row count missing from sidecar" >&2; exit 1; }
echo "backup/restore smoke OK"
