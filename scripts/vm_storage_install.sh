#!/usr/bin/env bash
# Install (or refresh) the VM storage maintenance from this checkout; also the restore
# procedure for a fresh VM. Idempotent. See docs/runbooks/vm-storage-maintenance.md.
#
#   sudo bash scripts/vm_storage_install.sh            install files, units and timers
#   bash scripts/vm_storage_install.sh --check         static checks + self-tests, installs nothing
#
# Installed files:
#   /usr/local/sbin/vscode-server-cleanup            <- scripts/vm_storage_vscode_cleanup.py
#   /usr/local/sbin/docker-safe-maintenance          <- scripts/vm_storage_docker_maintenance.sh
#   /usr/local/sbin/disk-watch                       <- scripts/vm_storage_disk_watch.sh
#   /usr/local/share/vm-storage-maintenance/*selftest*  <- the self-tests
#   /etc/systemd/system/{vscode-server-cleanup,docker-safe-maintenance,disk-watch}.{service,timer}
# It does not touch crontabs, Docker containers/images/volumes, or any application data.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$REPO/scripts"
UNITS_SRC="$REPO/infra/host-maintenance"
SBIN="${SBIN:-/usr/local/sbin}"
SHARE="${SHARE:-/usr/local/share/vm-storage-maintenance}"
SYSTEMD_DIR="${SYSTEMD_DIR:-/etc/systemd/system}"

say()  { echo "vm-storage-install: $*"; }
die()  { echo "vm-storage-install: ERROR: $*" >&2; exit 1; }

check() {
  say "static checks"
  for f in vm_storage_docker_maintenance.sh vm_storage_disk_watch.sh vm_storage_disk_watch_selftest.sh vm_storage_docker_maintenance_selftest.sh vm_storage_install.sh; do
    bash -n "$SCRIPTS/$f" || die "syntax error in $f"
  done
  python3 -c "import ast,sys; [ast.parse(open(p).read(), p) for p in sys.argv[1:]]" \
    "$SCRIPTS/vm_storage_vscode_cleanup.py" "$SCRIPTS/vm_storage_vscode_cleanup_selftest.py" || die "python syntax error"

  # The Docker job may only remove old build cache. Guard against anyone adding destructive commands.
  local forbidden='docker +(system|image|container|volume|network) +(prune|rm)|docker +(rmi|rm|kill|stop|restart)\b|--volumes'
  if grep -vE '^[[:space:]]*#' "$SCRIPTS/vm_storage_docker_maintenance.sh" | grep -nE "$forbidden"; then
    die "vm_storage_docker_maintenance.sh contains a forbidden destructive Docker command (see above)"
  fi
  say "docker maintenance script contains no destructive commands beyond 'builder prune'"

  local out
  say "vscode cleanup self-test"
  out="$(python3 "$SCRIPTS/vm_storage_vscode_cleanup_selftest.py" "$SCRIPTS/vm_storage_vscode_cleanup.py" 2>&1)" \
    || { echo "$out"; die "vscode cleanup self-test failed"; }
  echo "$out" | tail -n 1
  say "disk-watch self-test"
  out="$(bash "$SCRIPTS/vm_storage_disk_watch_selftest.sh" "$SCRIPTS/vm_storage_disk_watch.sh" 2>&1)" \
    || { echo "$out"; die "disk-watch self-test failed"; }
  echo "$out" | tail -n 1
  say "docker maintenance self-test (stub docker)"
  out="$(bash "$SCRIPTS/vm_storage_docker_maintenance_selftest.sh" "$SCRIPTS/vm_storage_docker_maintenance.sh" 2>&1)" \
    || { echo "$out"; die "docker maintenance self-test failed"; }
  echo "$out" | tail -n 1
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    say "docker maintenance dry-run"
    bash "$SCRIPTS/vm_storage_docker_maintenance.sh" --dry-run
  fi
  say "all checks passed"
}

install_all() {
  [ "$(id -u)" = 0 ] || die "run as root"
  check
  install -d -m 755 "$SBIN" "$SHARE"
  install -m 755 "$SCRIPTS/vm_storage_vscode_cleanup.py"        "$SBIN/vscode-server-cleanup"
  install -m 755 "$SCRIPTS/vm_storage_docker_maintenance.sh"    "$SBIN/docker-safe-maintenance"
  install -m 755 "$SCRIPTS/vm_storage_disk_watch.sh"            "$SBIN/disk-watch"
  install -m 755 "$SCRIPTS/vm_storage_vscode_cleanup_selftest.py" "$SHARE/vscode-cleanup-selftest.py"
  install -m 755 "$SCRIPTS/vm_storage_disk_watch_selftest.sh"   "$SHARE/disk-watch-selftest.sh"
  install -m 755 "$SCRIPTS/vm_storage_docker_maintenance_selftest.sh" "$SHARE/docker-maintenance-selftest.sh"
  for u in vscode-server-cleanup docker-safe-maintenance disk-watch; do
    install -m 644 "$UNITS_SRC/$u.service" "$UNITS_SRC/$u.timer" "$SYSTEMD_DIR/"
  done
  systemctl daemon-reload

  systemctl enable --now disk-watch.timer
  if [ -d /root/.vscode-server/cli/servers ]; then systemctl enable --now vscode-server-cleanup.timer
  else say "no /root/.vscode-server yet: vscode-server-cleanup.timer installed but NOT enabled (enable it after the first VS Code connection)"; fi
  if command -v docker >/dev/null 2>&1; then systemctl enable --now docker-safe-maintenance.timer
  else say "docker not installed: docker-safe-maintenance.timer installed but NOT enabled"; fi

  # Warn about the dangerous legacy job; never edit crontabs automatically.
  if crontab -l 2>/dev/null | grep -vE '^[[:space:]]*#' | grep -E 'docker +(system|image|container|volume) +prune'; then
    say "WARNING: root's crontab still contains a Docker prune job (see above). Remove it - see the runbook."
  fi
  systemctl list-timers --no-pager 'vscode-server-cleanup.timer' 'docker-safe-maintenance.timer' 'disk-watch.timer' || true
  say "installed"
}

case "${1:-}" in
  --check) check ;;
  "")      install_all ;;
  *)       die "usage: $0 [--check]" ;;
esac
