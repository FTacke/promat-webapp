#!/usr/bin/env bash
# Restore a PROMAT PostgreSQL dump (made by scripts/backup_prod_db.sh) into the database of a running container.
#
# SAFE BY DEFAULT: without --clean, objects that already exist make pg_restore fail (--exit-on-error), so a
# restore into a database that already holds data stops instead of merging into it. Use
# scripts/verify_db_restore.sh to rehearse a restore against a throw-away database first.
#
# DESTRUCTIVE: --clean drops existing objects of the dump before recreating them (data in them is lost). Against the
# production container this additionally requires --allow-production and typing the database name.
#
# Usage:
#   scripts/restore_db_dump.sh --dump FILE --container NAME [--clean] [--allow-production] [--yes]
#
# --yes skips the typed confirmation (for scripted use only; the production guard flags are still required).
# The dump's .sha256 sidecar, if present, is verified before anything is changed.
set -euo pipefail

DUMP=""
CONTAINER=""
CLEAN=0
ALLOW_PRODUCTION=0
ASSUME_YES=0
PRODUCTION_CONTAINER="promat-db-prod"

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
    --container) CONTAINER="${2:?--container needs a value}"; shift 2 ;;
    --clean) CLEAN=1; shift ;;
    --allow-production) ALLOW_PRODUCTION=1; shift ;;
    --yes) ASSUME_YES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) fail "Unknown argument: $1 (see --help)" ;;
  esac
done

[[ -n "${DUMP}" ]] || fail "--dump is required."
[[ -n "${CONTAINER}" ]] || fail "--container is required."
[[ -r "${DUMP}" ]] || fail "Dump not readable: ${DUMP}"
command -v docker >/dev/null 2>&1 || fail "docker is required."
[[ "$(docker inspect -f '{{.State.Running}}' "${CONTAINER}" 2>/dev/null || true)" == "true" ]] \
  || fail "Database container '${CONTAINER}' is not running."

if [[ -f "${DUMP}.sha256" ]]; then
  expected="$(cut -d' ' -f1 "${DUMP}.sha256")"
  actual="$(sha256sum "${DUMP}" | cut -d' ' -f1)"
  [[ "${expected}" == "${actual}" ]] || fail "Checksum mismatch for ${DUMP}; the dump is damaged or was modified."
  echo "Checksum OK."
else
  echo "WARNING: no ${DUMP}.sha256 sidecar found; dump integrity is not verified." >&2
fi

if [[ "${CONTAINER}" == "${PRODUCTION_CONTAINER}" ]]; then
  [[ "${ALLOW_PRODUCTION}" -eq 1 ]] || fail "Refusing to restore into the production container without --allow-production."
  target_db="$(docker exec "${CONTAINER}" sh -c 'printf %s "$POSTGRES_DB"')"
  echo "!!! PRODUCTION RESTORE into container '${CONTAINER}', database '${target_db}'."
  [[ "${CLEAN}" -eq 1 ]] && echo "!!! --clean: existing data in the restored tables WILL BE LOST."
  echo "!!! Stop the web container first (docker stop promat-web-prod) and make a fresh backup."
  if [[ "${ASSUME_YES}" -ne 1 ]]; then
    read -r -p "Type the database name '${target_db}' to continue: " answer
    [[ "${answer}" == "${target_db}" ]] || fail "Confirmation did not match; nothing was changed."
  fi
fi

flags=(--username "\$POSTGRES_USER" --dbname "\$POSTGRES_DB" --no-owner --no-privileges --exit-on-error)
if [[ "${CLEAN}" -eq 1 ]]; then
  flags+=(--clean --if-exists)
fi

echo "Restoring ${DUMP} into container '${CONTAINER}'..."
docker exec -i "${CONTAINER}" sh -c "pg_restore ${flags[*]}" < "${DUMP}"
echo "Restore finished."
