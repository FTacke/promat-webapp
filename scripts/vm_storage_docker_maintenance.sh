#!/usr/bin/env bash
# Conservative Docker maintenance for the production VM.
# Installed on the VM as /usr/local/sbin/docker-safe-maintenance
# (see docs/runbooks/vm-storage-maintenance.md).
#
# What it DOES:
#   1. Removes build cache older than BUILD_CACHE_MAX_AGE (default 168h = 7 days).
#   2. Keeps /etc/logrotate.d/docker-unbounded-container-logs in sync: it lists
#      only containers that still have NO json-file size limit (created before
#      /etc/docker/daemon.json set one) and removes the file as soon as there
#      are none, so a recreated container is never rotated twice.
#   3. Reports (read-only) what it deliberately leaves alone.
#
# What it NEVER does: remove images (tagged, untagged or dangling), containers,
# networks or volumes. Rollback images stay untouched; protect them with a tag
# in the rollback/ namespace (see runbook).
#
# Usage: docker-safe-maintenance [--dry-run]
set -euo pipefail

AGE="${BUILD_CACHE_MAX_AGE:-168h}"
LOGROTATE_FILE="${LOGROTATE_FILE:-/etc/logrotate.d/docker-unbounded-container-logs}"
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

# Under systemd, a "<N>" prefix sets the journal priority (3 err, 4 warning, 6 info).
if [ -n "${JOURNAL_STREAM:-}" ]; then P_ERR="<3>"; P_WARN="<4>"; P_INFO="<6>"; else P_ERR=""; P_WARN=""; P_INFO=""; fi
info() { echo "${P_INFO}docker-safe-maintenance: $*"; }
warn() { echo "${P_WARN}docker-safe-maintenance: WARNING: $*"; }
err()  { echo "${P_ERR}docker-safe-maintenance: ERROR: $*" >&2; }

command -v docker >/dev/null 2>&1 || { err "docker not found"; exit 2; }
docker info >/dev/null 2>&1 || { err "docker daemon not reachable"; exit 2; }

# --- 1. build cache ---------------------------------------------------------
cache_size() { docker system df --format '{{.Type}}|{{.Size}}' | awk -F'|' '$1=="Build Cache"{print $2}'; }
info "build cache before: $(cache_size)"
if [ "$DRY_RUN" = 1 ]; then
  info "dry-run: would run: docker builder prune --force --filter until=${AGE}"
else
  docker builder prune --force --filter "until=${AGE}" | tail -n 1 | sed 's/^/docker-safe-maintenance: /'
  info "build cache after: $(cache_size)"
fi

# --- 2. keep the stopgap logrotate rule in sync ------------------------------
# Containers created before the daemon-wide json-file limits have an empty option map.
unbounded=""
while read -r id; do
  [ -n "$id" ] || continue
  driver="$(docker inspect -f '{{.HostConfig.LogConfig.Type}}' "$id")"
  opts="$(docker inspect -f '{{len .HostConfig.LogConfig.Config}}' "$id")"
  path="$(docker inspect -f '{{.LogPath}}' "$id")"
  if [ "$driver" = "json-file" ] && [ "$opts" = "0" ] && [ -n "$path" ]; then
    unbounded="${unbounded}${path}"$'\n'
  fi
done < <(docker ps -aq --no-trunc)

if [ -z "$unbounded" ]; then
  if [ -e "$LOGROTATE_FILE" ]; then
    if [ "$DRY_RUN" = 1 ]; then info "dry-run: would remove $LOGROTATE_FILE (no container without log limit left)";
    else rm -f "$LOGROTATE_FILE"; info "removed $LOGROTATE_FILE: every container now uses the native docker log rotation"; fi
  else
    info "all containers use the native docker log rotation; no stopgap rule needed"
  fi
else
  tmp="$(mktemp)"
  {
    echo "# Managed by docker-safe-maintenance - do not edit. Stopgap for containers created before"
    echo "# /etc/docker/daemon.json set json-file limits. The file disappears once none are left."
    printf '%s' "$unbounded" | sort
    echo "{"
    echo "    size 50M"
    echo "    rotate 3"
    echo "    compress"
    echo "    missingok"
    echo "    notifempty"
    echo "    copytruncate"
    echo "}"
  } > "$tmp"
  if logrotate -d "$tmp" >/dev/null 2>&1; then
    if [ "$DRY_RUN" = 1 ]; then info "dry-run: would write $LOGROTATE_FILE for: $(printf '%s' "$unbounded" | wc -l) container log(s)";
    else install -m 644 "$tmp" "$LOGROTATE_FILE"; info "logrotate stopgap covers $(printf '%s' "$unbounded" | wc -l) container log(s) without native limit"; fi
  else
    warn "generated logrotate rule failed validation; left $LOGROTATE_FILE unchanged"
  fi
  rm -f "$tmp"
fi

# --- 3. read-only report of what is intentionally NOT cleaned -------------------
info "not touched: dangling images=$(docker images -f dangling=true -q | wc -l)" \
     "stopped containers=$(docker ps -aq -f status=exited -f status=created | wc -l)" \
     "unused volumes=$(docker volume ls -qf dangling=true | wc -l)"
info "protected rollback tags: $(docker images --format '{{.Repository}}:{{.Tag}}' | grep -c '^rollback/' || true)"
