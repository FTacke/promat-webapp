#!/usr/bin/env bash
# Self-test for vm_storage_docker_maintenance.sh using a stub "docker" that records every call.
# Proves: only read-only calls plus "builder prune --filter until=..." are ever issued, and the
# logrotate stopgap lists exactly the containers without native json-file limits (and vanishes
# when there are none, so nothing is rotated twice).
#
# Usage: vm_storage_docker_maintenance_selftest.sh [path-to-docker-maintenance-script]
set -uo pipefail

SCRIPT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/vm_storage_docker_maintenance.sh}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/bin"
CALLS="$TMP/calls.log"

cat > "$TMP/bin/docker" <<'STUB'
#!/usr/bin/env bash
echo "$*" >> "$STUB_CALLS"
case "$1" in
  info) exit 0 ;;
  system) echo "Build Cache|0B" ;;
  builder) echo "Total reclaimed space: 0B" ;;
  ps) case "$*" in *--no-trunc*) printf '%s\n' $STUB_IDS ;; esac ;;
  inspect)
    id="${@: -1}"
    case "$*" in
      *LogConfig.Type*) echo "json-file" ;;
      *len*)            if grep -qx "$id" "$STUB_LIMITED" 2>/dev/null; then echo 2; else echo 0; fi ;;
      *LogPath*)        echo "/var/lib/docker/containers/$id/$id-json.log" ;;
    esac ;;
  images|volume) ;;
  *) echo "unexpected docker call: $*" >&2; exit 99 ;;
esac
STUB
chmod +x "$TMP/bin/docker"

pass=0; fail=0
ok()  { pass=$((pass + 1)); echo "PASS  $1"; }
bad() { fail=$((fail + 1)); echo "FAIL  $1   [$2]"; }
run() { env PATH="$TMP/bin:$PATH" STUB_CALLS="$CALLS" STUB_LIMITED="$TMP/limited" LOGROTATE_FILE="$TMP/logrotate.conf" "$@" bash "$SCRIPT" 2>&1; }

: > "$CALLS"; : > "$TMP/limited"
out="$(run STUB_IDS="aaa bbb ccc")"
[ "$(grep -c '^/var/lib/docker/containers/' "$TMP/logrotate.conf")" = 3 ] && ok "three unbounded containers -> three paths in the stopgap" || bad "three unbounded containers" "$(cat "$TMP/logrotate.conf" 2>&1)"

printf 'aaa\nccc\n' > "$TMP/limited"
out="$(run STUB_IDS="aaa bbb ccc")"
if [ "$(grep -c '^/var/lib/docker/containers/' "$TMP/logrotate.conf")" = 1 ] && grep -q '/bbb/bbb-json.log' "$TMP/logrotate.conf"; then
  ok "containers with native limits are dropped from the stopgap (no double rotation)"
else bad "native-limit containers dropped" "$(cat "$TMP/logrotate.conf")"; fi

printf 'aaa\nbbb\nccc\n' > "$TMP/limited"
out="$(run STUB_IDS="aaa bbb ccc")"
[ ! -e "$TMP/logrotate.conf" ] && ok "all containers native -> stopgap file removed" || bad "stopgap removed" "$(cat "$TMP/logrotate.conf")"

# --dry-run must not touch the stopgap file even when it would be removed
: > "$TMP/limited"; run STUB_IDS="aaa" >/dev/null          # creates the file
before="$(cat "$TMP/logrotate.conf")"
printf 'aaa\n' > "$TMP/limited"                             # now the container is native -> real run would delete it
out="$(env PATH="$TMP/bin:$PATH" STUB_CALLS="$TMP/dry.log" STUB_LIMITED="$TMP/limited" STUB_IDS="aaa" LOGROTATE_FILE="$TMP/logrotate.conf" bash "$SCRIPT" --dry-run 2>&1)"; cat "$TMP/dry.log" >> "$CALLS"
[ "$(cat "$TMP/logrotate.conf" 2>/dev/null)" = "$before" ] && grep -q "dry-run: would remove" <<<"$out" && ok "--dry-run changes nothing" || bad "--dry-run changes nothing" "$out"
if grep -q "dry-run: would run: docker builder prune" <<<"$out" && ! grep -q "^builder" "$TMP/dry.log"; then ok "--dry-run does not call builder prune"; else bad "--dry-run does not call builder prune" "$(cat "$TMP/dry.log")"; fi

# Every docker call ever made must be on the allow-list.
bad_calls="$(grep -vE '^(info|system df |builder prune --force --filter until=[0-9a-z]+$|ps -aq --no-trunc$|ps -aq -f status=exited -f status=created$|inspect -f \{\{\.(HostConfig\.LogConfig\.Type|HostConfig\.LogConfig\.Config|LogPath)|inspect -f \{\{len \.HostConfig\.LogConfig\.Config\}\}|images |volume ls )' "$CALLS" | sort -u)"
[ -z "$bad_calls" ] && ok "only allow-listed docker calls were issued" || bad "docker call allow-list" "$bad_calls"
grep -qE 'prune' <(grep -v '^builder prune --force --filter until=' "$CALLS") && bad "only builder prune is used" "$(grep prune "$CALLS" | sort -u)" || ok "the only prune ever issued is: builder prune --filter until=..."

echo; echo "$pass passed, $fail failed"
[ "$fail" = 0 ]
