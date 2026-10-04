#!/usr/bin/env bash
# Create a verified logical backup of the PROMAT PostgreSQL database.
#
# Runs on the production host (or any host that runs the compose stack). It uses `pg_dump` *inside* the database
# container, so it needs no database password and reads no secrets file: the container already has
# POSTGRES_USER / POSTGRES_DB in its environment and accepts local socket connections.
#
# What it produces, in --output-dir:
#   promat_db_<UTC timestamp>.dump              pg_dump custom format (compressed, restorable with pg_restore)
#   promat_db_<UTC timestamp>.dump.sha256       checksum of the dump
#   promat_db_<UTC timestamp>.dump.counts.tsv   exact row count per table right after the dump (used by
#                                               scripts/verify_db_restore.sh to check a restore)
#
# The dump is written to a ".partial" file, validated with `pg_restore --list`, and only then renamed. Any failure
# exits non-zero (cron/systemd will surface it) and leaves no half-written file under the final name.
#
# The backup contains personal data (accounts, password hashes, access requests). Files are created with mode 600
# in a 700 directory. Copy them off-host only to storage that is allowed to hold such data.
#
# Usage:
#   scripts/backup_prod_db.sh [--output-dir DIR] [--container NAME] [--keep N]
#
# Defaults: DIR=${PROMAT_BACKUP_DIR:-/srv/webapps_storage/promat/backups/postgres}, NAME=promat-db-prod, N=14.
# --keep N prunes older promat_db_*.dump sets (dump + sidecars) beyond the N newest in DIR; 0 disables pruning.
set -euo pipefail
umask 077

OUTPUT_DIR="${PROMAT_BACKUP_DIR:-/srv/webapps_storage/promat/backups/postgres}"
CONTAINER="promat-db-prod"
KEEP=14

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

usage() {
  sed -n '2,/^set -euo/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir) OUTPUT_DIR="${2:?--output-dir needs a value}"; shift 2 ;;
    --container) CONTAINER="${2:?--container needs a value}"; shift 2 ;;
    --keep) KEEP="${2:?--keep needs a value}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) fail "Unknown argument: $1 (see --help)" ;;
  esac
done

[[ "${KEEP}" =~ ^[0-9]+$ ]] || fail "--keep must be a non-negative integer."
command -v docker >/dev/null 2>&1 || fail "docker is required."
[[ "$(docker inspect -f '{{.State.Running}}' "${CONTAINER}" 2>/dev/null || true)" == "true" ]] \
  || fail "Database container '${CONTAINER}' is not running."

mkdir -p "${OUTPUT_DIR}"
chmod 700 "${OUTPUT_DIR}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BASENAME="promat_db_${STAMP}.dump"
FINAL="${OUTPUT_DIR}/${BASENAME}"
PARTIAL="${FINAL}.partial"
COUNTS_PARTIAL="${FINAL}.counts.tsv.partial"
[[ ! -e "${FINAL}" ]] || fail "Refusing to overwrite existing backup ${FINAL}."

# shellcheck disable=SC2317,SC2329  # invoked through the EXIT trap
cleanup() {
  rm -f "${PARTIAL}" "${COUNTS_PARTIAL}"
}
trap cleanup EXIT

echo "Backing up database from container '${CONTAINER}' to ${FINAL}"

# --no-owner/--no-privileges: restore into any role without depending on the original role names.
docker exec "${CONTAINER}" sh -c 'pg_dump --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --format=custom --no-owner --no-privileges' \
  > "${PARTIAL}"

[[ -s "${PARTIAL}" ]] || fail "pg_dump produced an empty file."

# The archive must be readable by pg_restore and contain table data.
docker exec -i "${CONTAINER}" pg_restore --list < "${PARTIAL}" > "${PARTIAL}.list" \
  || { rm -f "${PARTIAL}.list"; fail "pg_restore cannot read the new dump; it is not a valid archive."; }
if ! grep -q "TABLE DATA" "${PARTIAL}.list"; then
  rm -f "${PARTIAL}.list"
  fail "The dump contains no table data; refusing to keep it."
fi
rm -f "${PARTIAL}.list"

# Exact row count per table right after the dump; lets a restore be verified against the live database.
# `\gexec` runs one generated `SELECT count(*)` per public table; output is `table<TAB>count`.
COUNT_SQL="SELECT format('SELECT %L, count(*) FROM %I.%I', c.relname, n.nspname, c.relname) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind = 'r' AND n.nspname = 'public' ORDER BY c.relname \\gexec"
docker exec -i "${CONTAINER}" sh -c 'psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --no-psqlrc --quiet -v ON_ERROR_STOP=1 --tuples-only --no-align --field-separator "$(printf "\t")"' \
  <<< "${COUNT_SQL}" > "${COUNTS_PARTIAL}" \
  || fail "Could not compute row counts."
[[ -s "${COUNTS_PARTIAL}" ]] || fail "Row-count sidecar is empty; the database has no tables in schema public."

mv "${PARTIAL}" "${FINAL}"
mv "${COUNTS_PARTIAL}" "${FINAL}.counts.tsv"
(cd "${OUTPUT_DIR}" && sha256sum "${BASENAME}" > "${BASENAME}.sha256")
trap - EXIT

SIZE="$(wc -c < "${FINAL}" | tr -d ' ')"
TABLES="$(wc -l < "${FINAL}.counts.tsv" | tr -d ' ')"
echo "Backup written: ${FINAL} (${SIZE} bytes, ${TABLES} tables)"
echo "Checksum:       ${FINAL}.sha256"

if [[ "${KEEP}" -gt 0 ]]; then
  mapfile -t OLD < <(find "${OUTPUT_DIR}" -maxdepth 1 -name 'promat_db_*.dump' -printf '%f\n' | sort -r | tail -n +"$((KEEP + 1))")
  for old in "${OLD[@]:-}"; do
    [[ -n "${old}" ]] || continue
    echo "Pruning old backup ${old}"
    rm -f "${OUTPUT_DIR}/${old}" "${OUTPUT_DIR}/${old}.sha256" "${OUTPUT_DIR}/${old}.counts.tsv"
  done
fi

echo "OK"
