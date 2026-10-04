#!/usr/bin/env bash
# Rehearse and verify a restore of a PROMAT PostgreSQL dump in a disposable PostgreSQL container.
#
# Nothing here touches production: it starts a throw-away container (no published ports, random password, data in
# tmpfs), restores the dump with scripts/restore_db_dump.sh, compares the restored per-table row counts with the
# <dump>.counts.tsv sidecar written by scripts/backup_prod_db.sh, and removes the container again.
#
# Usage:
#   scripts/verify_db_restore.sh --dump FILE [--image postgres:15] [--keep-container]
#
# Exit codes: 0 restore verified; 3 restore worked but row counts differ from the sidecar (rows may have been written
# between dump and count - re-run a backup and verify again before concluding anything); 1 any other failure.
set -euo pipefail

DUMP=""
IMAGE="postgres:15"
KEEP=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

usage() {
  sed -n '2,/^set -euo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dump) DUMP="${2:?--dump needs a value}"; shift 2 ;;
    --image) IMAGE="${2:?--image needs a value}"; shift 2 ;;
    --keep-container) KEEP=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) fail "Unknown argument: $1 (see --help)" ;;
  esac
done

[[ -n "${DUMP}" ]] || fail "--dump is required."
[[ -r "${DUMP}" ]] || fail "Dump not readable: ${DUMP}"
command -v docker >/dev/null 2>&1 || fail "docker is required."

NAME="promat-restore-verify-$$"
PASSWORD="$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 24)"

# shellcheck disable=SC2317,SC2329  # invoked through the EXIT trap
cleanup() {
  if [[ "${KEEP}" -eq 1 ]]; then
    echo "Leaving container '${NAME}' running (remove with: docker rm -f ${NAME})."
  else
    docker rm -f "${NAME}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

echo "Starting disposable ${IMAGE} container '${NAME}'..."
docker run -d --name "${NAME}" \
  -e POSTGRES_USER=promat_restore_test \
  -e POSTGRES_PASSWORD="${PASSWORD}" \
  -e POSTGRES_DB=promat_restore_test \
  --tmpfs /var/lib/postgresql/data \
  "${IMAGE}" >/dev/null

for attempt in $(seq 1 60); do
  if docker exec "${NAME}" sh -c 'pg_isready --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"' >/dev/null 2>&1; then
    # The image restarts once during init; wait until two consecutive probes succeed.
    sleep 2
    docker exec "${NAME}" sh -c 'pg_isready --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"' >/dev/null 2>&1 && break
  fi
  [[ "${attempt}" -lt 60 ]] || fail "Disposable database did not become ready."
  sleep 1
done

"${SCRIPT_DIR}/restore_db_dump.sh" --dump "${DUMP}" --container "${NAME}"

COUNT_SQL="SELECT format('SELECT %L, count(*) FROM %I.%I', c.relname, n.nspname, c.relname) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind = 'r' AND n.nspname = 'public' ORDER BY c.relname \\gexec"
RESTORED="$(mktemp)"
trap 'rm -f "${RESTORED}"; cleanup' EXIT
docker exec -i "${NAME}" sh -c 'psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --no-psqlrc --quiet -v ON_ERROR_STOP=1 --tuples-only --no-align --field-separator "$(printf "\t")"' \
  <<< "${COUNT_SQL}" | sort > "${RESTORED}"

[[ -s "${RESTORED}" ]] || fail "The restored database has no tables in schema public."
echo "Restored tables (name<TAB>rows):"
cat "${RESTORED}"

SIDECAR="${DUMP}.counts.tsv"
if [[ ! -f "${SIDECAR}" ]]; then
  echo "WARNING: no ${SIDECAR}; only checked that the dump restores and contains tables." >&2
  echo "RESTORE OK (counts not compared)"
  exit 0
fi

if diff <(sort "${SIDECAR}") "${RESTORED}" >/dev/null; then
  echo "RESTORE VERIFIED: row counts of all $(wc -l < "${RESTORED}" | tr -d ' ') tables match the sidecar."
  exit 0
fi
echo "Row counts differ from ${SIDECAR} (< expected at backup time, > restored):" >&2
diff <(sort "${SIDECAR}") "${RESTORED}" >&2 || true
exit 3
