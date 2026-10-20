#!/usr/bin/env bash
# Self-test for vm_storage_disk_watch.sh. Uses a throw-away state dir; the unit-state checks
# (failed / overdue) additionally need root and systemd and create a transient unit pair under
# /run/systemd/system that is removed again.
#
# Usage: vm_storage_disk_watch_selftest.sh [path-to-disk-watch-script]
set -uo pipefail

SCRIPT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/vm_storage_disk_watch.sh}"
TMP="$(mktemp -d)"
UNIT="dw-selftest"
cleanup() {
  systemctl stop "$UNIT.timer" "$UNIT.service" >/dev/null 2>&1 || true
  rm -f "/run/systemd/system/$UNIT.timer" "/run/systemd/system/$UNIT.service"
  systemctl daemon-reload >/dev/null 2>&1 || true
  systemctl reset-failed "$UNIT.service" >/dev/null 2>&1 || true
  rm -rf "$TMP"
}
trap cleanup EXIT

pass=0; fail=0
ok()   { pass=$((pass + 1)); echo "PASS  $1"; }
bad()  { fail=$((fail + 1)); echo "FAIL  $1   [$2]"; }
# run <env assignments...> -> output of the script with an isolated state dir and no unit checks
run()  { env DISK_WATCH_STATE_DIR="$TMP/state" DISK_WATCH_MAINT_UNITS="${UNITS:-}" "$@" bash "$SCRIPT" 2>&1; }
expect() { # expect <name> <regex> <output>
  if grep -qE "$2" <<<"$3"; then ok "$1"; else bad "$1" "$3"; fi
}
reject() { # reject <name> <regex> <output>
  if grep -qE "$2" <<<"$3"; then bad "$1" "$3"; else ok "$1"; fi
}

out="$(run DISK_WATCH_WARN_PCT=101 DISK_WATCH_CRIT_PCT=101)"
expect "below thresholds: plain ok line" '^ok: / is [0-9]+% full' "$out"
reject "below thresholds: no warning" 'WARNING|CRITICAL' "$out"

out="$(run DISK_WATCH_WARN_PCT=1 DISK_WATCH_CRIT_PCT=101)"
expect "warn threshold: WARNING line" '^WARNING: / is [0-9]+% full' "$out"
reject "warn threshold: not critical" 'CRITICAL' "$out"

out="$(run DISK_WATCH_WARN_PCT=1 DISK_WATCH_CRIT_PCT=1)"
expect "crit threshold: CRITICAL line" '^CRITICAL: / is [0-9]+% full' "$out"

out="$(run JOURNAL_STREAM=1:1 DISK_WATCH_WARN_PCT=1 DISK_WATCH_CRIT_PCT=1)"
expect "journal priority: crit is <2>" '^<2>CRITICAL' "$out"
out="$(run JOURNAL_STREAM=1:1 DISK_WATCH_WARN_PCT=1 DISK_WATCH_CRIT_PCT=101)"
expect "journal priority: warning is <4>" '^<4>WARNING' "$out"

# history: one sample per day, no growth info yet
rm -rf "$TMP/state"
out="$(run DISK_WATCH_WARN_PCT=101 DISK_WATCH_CRIT_PCT=101)"
expect "no history: says so" 'not enough history' "$out"
run DISK_WATCH_WARN_PCT=101 DISK_WATCH_CRIT_PCT=101 >/dev/null
[ "$(wc -l < "$TMP/state/usage.tsv")" = 1 ] && ok "history: one sample per day" || bad "history: one sample per day" "$(cat "$TMP/state/usage.tsv")"

# growth: an 8-day-old sample far below the current usage must raise a warning with an estimate
printf '%s\t%s\t%s\n' "$(date -d '8 days ago' +%F)" 1000 1 | cat - "$TMP/state/usage.tsv" > "$TMP/state/h" && mv "$TMP/state/h" "$TMP/state/usage.tsv"
out="$(run DISK_WATCH_WARN_PCT=101 DISK_WATCH_CRIT_PCT=101)"
expect "growth above limit: WARNING with days-left estimate" '^WARNING: / grew by .* GiB in 8 days.*full in about [0-9]+ days' "$out"
out="$(run DISK_WATCH_WARN_PCT=101 DISK_WATCH_CRIT_PCT=101 DISK_WATCH_GROWTH_GIB=100000)"
reject "growth below limit: no warning" 'WARNING' "$out"
expect "growth below limit: info line" '^growth: ' "$out"

# a stable history (same usage 8 days ago) is not growth
used="$(df --output=used -B1 / | tail -n 1 | tr -d ' ')"
printf '%s\t%s\t%s\n' "$(date -d '9 days ago' +%F)" "$used" 1 > "$TMP/state/usage.tsv"
out="$(run DISK_WATCH_WARN_PCT=101 DISK_WATCH_CRIT_PCT=101)"
reject "stable usage: no growth warning" 'WARNING' "$out"

# maintenance units: unknown unit names are skipped silently
out="$(UNITS="no-such-unit-xyz" run DISK_WATCH_WARN_PCT=101 DISK_WATCH_CRIT_PCT=101)"
reject "unknown maintenance unit is skipped" 'WARNING' "$out"

if [ "$(id -u)" = 0 ] && command -v systemctl >/dev/null 2>&1 && [ -d /run/systemd/system ]; then
  printf '[Unit]\nDescription=disk-watch selftest\n[Service]\nType=oneshot\nExecStart=/bin/false\n' > "/run/systemd/system/$UNIT.service"
  printf '[Unit]\nDescription=disk-watch selftest\n[Timer]\nOnCalendar=2999-01-01\n[Install]\nWantedBy=timers.target\n' > "/run/systemd/system/$UNIT.timer"
  systemctl daemon-reload
  systemctl start "$UNIT.service" >/dev/null 2>&1 || true   # fails on purpose
  out="$(UNITS="$UNIT" run DISK_WATCH_WARN_PCT=101 DISK_WATCH_CRIT_PCT=101)"
  expect "failed maintenance unit is reported" "WARNING: $UNIT.service is in failed state" "$out"
  reject "fresh timer is not reported overdue" "did not trigger" "$out"
  touch -d '20 days ago' "/run/systemd/system/$UNIT.timer"
  out="$(UNITS="$UNIT" run DISK_WATCH_WARN_PCT=101 DISK_WATCH_CRIT_PCT=101)"
  expect "timer that never triggered for 20 days is reported overdue" "WARNING: $UNIT.timer did not trigger for 20 days" "$out"
else
  echo "SKIP  unit-state tests (need root + systemd)"
fi

echo; echo "$pass passed, $fail failed"
[ "$fail" = 0 ]
