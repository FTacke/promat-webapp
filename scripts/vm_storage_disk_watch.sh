#!/usr/bin/env bash
# Lightweight disk watch for the production VM root filesystem.
# Installed on the VM as /usr/local/sbin/disk-watch, run hourly by disk-watch.timer
# (see docs/runbooks/vm-storage-maintenance.md).
#
# Writes to the system journal only; it never deletes anything and does not replace the
# existing mail alert (disk-check.sh in root's crontab):
#   usage >= DISK_WATCH_CRIT_PCT (85)  -> priority crit    "CRITICAL ..."
#   usage >= DISK_WATCH_WARN_PCT (75)  -> priority warning "WARNING ..."
#   growth over 7 days > DISK_WATCH_GROWTH_GIB (3) -> priority warning, with an estimate of
#   the days left; this shows when usage keeps rising despite the cleanup jobs.
#   (DISK_WATCH_GROWTH_GIB must be a whole number)
#   a maintenance unit (vscode-server-cleanup, docker-safe-maintenance) failed, or its timer
#   did not trigger for more than MAINT_OVERDUE_DAYS (9) -> priority warning.
#
# Read it with:  journalctl -t disk-watch -p warning     (SyslogIdentifier=disk-watch)
set -euo pipefail

MOUNT="${DISK_WATCH_MOUNT:-/}"
WARN="${DISK_WATCH_WARN_PCT:-75}"
CRIT="${DISK_WATCH_CRIT_PCT:-85}"
GROWTH_GIB="${DISK_WATCH_GROWTH_GIB:-3}"
OVERDUE_DAYS="${MAINT_OVERDUE_DAYS:-9}"
STATE_DIR="${DISK_WATCH_STATE_DIR:-/var/lib/disk-watch}"
HISTORY="$STATE_DIR/usage.tsv"
MAINT_UNITS="${DISK_WATCH_MAINT_UNITS:-vscode-server-cleanup docker-safe-maintenance}"
MAX_HISTORY_LINES=120

if [ -n "${JOURNAL_STREAM:-}" ]; then P_CRIT="<2>"; P_WARN="<4>"; P_INFO="<6>"; else P_CRIT=""; P_WARN=""; P_INFO=""; fi

read -r PCT USED AVAIL < <(df --output=pcent,used,avail -B1 "$MOUNT" | awk 'NR==2{gsub("%","",$1); print $1, $2, $3}')
[ -n "${PCT:-}" ] || { echo "disk-watch: cannot read usage of $MOUNT" >&2; exit 2; }
GIB() { awk -v b="$1" 'BEGIN{printf "%.1f", b/1073741824}'; }

if [ "$PCT" -ge "$CRIT" ]; then
  echo "${P_CRIT}CRITICAL: $MOUNT is ${PCT}% full ($(GIB "$USED") GiB used, $(GIB "$AVAIL") GiB free; critical threshold ${CRIT}%)"
elif [ "$PCT" -ge "$WARN" ]; then
  echo "${P_WARN}WARNING: $MOUNT is ${PCT}% full ($(GIB "$USED") GiB used, $(GIB "$AVAIL") GiB free; warning threshold ${WARN}%)"
else
  echo "${P_INFO}ok: $MOUNT is ${PCT}% full ($(GIB "$USED") GiB used, $(GIB "$AVAIL") GiB free)"
fi

# --- daily history + 7-day growth ------------------------------------------------
mkdir -p "$STATE_DIR"
TODAY="$(date +%F)"
if [ ! -s "$HISTORY" ] || [ "$(tail -n 1 "$HISTORY" | cut -f1)" != "$TODAY" ]; then
  printf '%s\t%s\t%s\n' "$TODAY" "$USED" "$PCT" >> "$HISTORY"
  tail -n "$MAX_HISTORY_LINES" "$HISTORY" > "$HISTORY.tmp" && mv "$HISTORY.tmp" "$HISTORY"
fi
CUTOFF="$(date -d '7 days ago' +%F)"
# newest sample that is at least 7 days old
read -r THEN_DATE THEN_USED < <(awk -F'\t' -v c="$CUTOFF" '$1<=c {d=$1; u=$2} END{if (d!="") print d, u}' "$HISTORY") || true
if [ -n "${THEN_DATE:-}" ]; then
  DAYS=$(( ( $(date -d "$TODAY" +%s) - $(date -d "$THEN_DATE" +%s) ) / 86400 ))
  GROWTH=$(( USED - THEN_USED ))
  LIMIT=$(( GROWTH_GIB * 1073741824 ))
  if [ "$DAYS" -gt 0 ] && [ "$GROWTH" -gt "$LIMIT" ]; then
    LEFT=$(awk -v a="$AVAIL" -v g="$GROWTH" -v d="$DAYS" 'BEGIN{printf "%.0f", a/(g/d)}')
    echo "${P_WARN}WARNING: $MOUNT grew by $(GIB "$GROWTH") GiB in ${DAYS} days (limit ${GROWTH_GIB} GiB/week); at this rate it is full in about ${LEFT} days"
  else
    echo "${P_INFO}growth: $(GIB "$GROWTH") GiB over ${DAYS} days (limit ${GROWTH_GIB} GiB/week)"
  fi
else
  echo "${P_INFO}growth: not enough history yet (needs a sample at least 7 days old)"
fi

# --- maintenance units must have run and succeeded --------------------------------
NOW_S="$(date +%s)"
for unit in $MAINT_UNITS; do
  systemctl cat "$unit.timer" >/dev/null 2>&1 || continue       # not installed on this VM
  if systemctl is-failed --quiet "$unit.service"; then
    echo "${P_WARN}WARNING: $unit.service is in failed state - see: journalctl -u $unit.service -p warning"
  fi
  # Persistent timers keep a stamp of their last trigger; without one, fall back to the unit file's age.
  stamp="/var/lib/systemd/timers/stamp-$unit.timer"
  [ -e "$stamp" ] || stamp="$(systemctl show -p FragmentPath --value "$unit.timer")"
  if [ -n "$stamp" ] && [ -e "$stamp" ]; then
    age_days=$(( (NOW_S - $(stat -c %Y "$stamp")) / 86400 ))
    if [ "$age_days" -gt "$OVERDUE_DAYS" ]; then
      echo "${P_WARN}WARNING: $unit.timer did not trigger for ${age_days} days (expected weekly) - check: systemctl list-timers $unit.timer"
    fi
  fi
done
