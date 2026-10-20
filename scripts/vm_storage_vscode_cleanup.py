#!/usr/bin/env python3
"""Safe cleanup of stale VS Code Server installations on the production VM.

Scans ~/.vscode-server/cli/servers/ and removes only entries that are provably
superseded and unused.  Dry-run is the default; pass --apply to delete.
Installed on the VM as /usr/local/sbin/vscode-server-cleanup (see
docs/runbooks/vm-storage-maintenance.md).

Why this exists: the VS Code "agent host" downloads every new server version
into "<channel>-<commit>.staging" and renames it to "<channel>-<commit>".  When
several agent hosts run in parallel they race on the same staging directory,
the losers fail with "error renaming downloaded server: Directory not empty"
and leave the staging directory behind.  Every update then costs ~0.7 GB that
nothing ever reclaims.

Decision rules (evaluated on every run, nothing is hardcoded to a version):

  * An entry referenced by ANY process (exe, cwd, root, open fd, mapped file,
    command line, environment) is kept - its sibling (final <-> .staging) too.
  * An entry with a file changed in the last --active-grace-minutes is kept
    (install/update may be writing to it).
  * The --keep-complete newest complete installations per channel are kept
    (ordered by the version in server/package.json).
  * An installation newer than the newest complete one is kept (it may be the
    next active version).
  * Installations younger than --max-age-days are kept.
  * ".staging" entries younger than --staging-age-days are kept.
  * "Complete" means: all marker files present AND at least 70 % of the median
    file count of the comparable entries in the channel (catches installs that
    were only partially populated by the update race).
  * If no complete installation exists in a channel (layout change?), no final
    installation is deleted at all.
  * If the process table cannot be scanned completely, nothing is deleted.
  * Names that do not match "<Channel>-<40 hex>[.staging]" are never touched.

Exit codes: 0 ok, 1 deletion errors or unexpected failure, 2 refused (unsafe
setup), 3 process scan incomplete (nothing deleted), 75 another run holds the
lock.  Under systemd (JOURNAL_STREAM set) every line carries a syslog priority
prefix, so problems show up with `journalctl -p warning`.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shutil
import stat
import sys
import time
import traceback
from dataclasses import dataclass, field

DEFAULT_SERVERS_DIR = "/root/.vscode-server/cli/servers"
DEFAULT_LOCK_FILE = "/run/lock/vscode-server-cleanup.lock"

ENTRY_RE = re.compile(r"^(?P<channel>[A-Za-z]+)-(?P<commit>[0-9a-f]{40})(?P<staging>\.staging)?$")
REF_RE = re.compile(r"servers/(?P<channel>[A-Za-z]+)-(?P<commit>[0-9a-f]{40})")
VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")

REQUIRED_FILES = (
    "server/node",
    "server/bin/code-server",
    "server/out/server-main.js",
    "server/package.json",
    "server/product.json",
)
REQUIRED_DIRS = ("server/node_modules", "server/extensions")
MIN_FILE_RATIO = 0.7

# Skips after the plan was made that are expected races, not problems.
BENIGN_SKIPS = ("already-gone", "became-in-use", "became-active")

EXIT_OK, EXIT_ERRORS, EXIT_REFUSED, EXIT_SCAN_INCOMPLETE, EXIT_LOCKED = 0, 1, 2, 3, 75
SYSLOG_PRIORITY = {"error": 3, "warn": 4, "info": 6}


@dataclass
class Entry:
    name: str
    path: str
    channel: str
    commit: str
    staging: bool
    size: int = 0
    age_s: float = 0.0
    newest_ctime: float = 0.0
    complete: bool = False
    marker_complete: bool = False
    file_count: int = 0
    version: tuple | None = None
    version_str: str | None = None
    active: bool = False
    inspect_error: str | None = None
    action: str = "keep"
    reasons: list = field(default_factory=list)


@dataclass
class Config:
    servers_dir: str
    apply: bool
    keep_complete: int
    max_age_s: float
    staging_age_s: float
    active_grace_s: float
    now: float


class Logger:
    def __init__(self, fmt: str):
        self.fmt = fmt
        self.journal = bool(os.environ.get("JOURNAL_STREAM"))

    def emit(self, event: str, level: str = "info", **fields):
        record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "level": level, "event": event, **fields}
        if self.fmt == "json":
            line = json.dumps(record, ensure_ascii=False, default=str)
        else:
            rest = " ".join(f"{k}={v}" for k, v in fields.items())
            line = f"{record['ts']} {level.upper():5} {event} {rest}".rstrip()
        prefix = f"<{SYSLOG_PRIORITY.get(level, 6)}>" if self.journal else ""
        print(prefix + line, flush=True)


# --------------------------------------------------------------------------- inspection


def walk_stats(path: str) -> tuple[int, float, int]:
    """Return (allocated bytes, newest ctime, entry count) of a tree without following symlinks."""
    total = 0
    count = 0
    newest = 0.0
    for root, dirs, files in os.walk(path, followlinks=False):
        for name in dirs + files:
            try:
                st = os.lstat(os.path.join(root, name))
            except FileNotFoundError:
                continue
            total += st.st_blocks * 512
            count += 1
            newest = max(newest, st.st_ctime)
    st = os.lstat(path)
    return total + st.st_blocks * 512, max(newest, st.st_ctime), count


def read_version(entry_path: str) -> tuple[tuple | None, str | None]:
    try:
        with open(os.path.join(entry_path, "server", "package.json"), encoding="utf-8") as fh:
            raw = json.load(fh).get("version")
    except (OSError, ValueError, AttributeError):
        return None, None
    m = VERSION_RE.match(raw) if isinstance(raw, str) else None
    return (tuple(int(g) for g in m.groups()), raw) if m else (None, None)


def is_complete(entry_path: str) -> bool:
    for rel in REQUIRED_FILES:
        p = os.path.join(entry_path, rel)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            return False
    return all(os.path.isdir(os.path.join(entry_path, rel)) for rel in REQUIRED_DIRS)


def inspect_entry(servers_dir: str, name: str, m: re.Match, cfg: Config) -> Entry:
    path = os.path.join(servers_dir, name)
    e = Entry(name, path, m["channel"], m["commit"], bool(m["staging"]))
    try:
        st = os.lstat(path)
        server_dir = os.path.join(path, "server")
        try:
            srv_mtime = os.lstat(server_dir).st_mtime
        except OSError:
            srv_mtime = st.st_mtime
        e.age_s = cfg.now - max(st.st_mtime, srv_mtime)
        e.size, e.newest_ctime, e.file_count = walk_stats(path)
        e.active = (cfg.now - e.newest_ctime) < cfg.active_grace_s
        e.version, e.version_str = read_version(path)
        e.marker_complete = is_complete(path)
        e.complete = e.marker_complete  # refined by apply_plausibility()
    except OSError as exc:
        e.inspect_error = f"{type(exc).__name__}: {exc}"
    return e


def apply_plausibility(entries: list) -> None:
    """Downgrade marker-complete entries that hold far fewer files than their peers."""
    counts_by_channel: dict = {}
    for e in entries:
        if e.marker_complete and not e.inspect_error:
            counts_by_channel.setdefault(e.channel, []).append(e.file_count)
    for e in entries:
        counts = sorted(counts_by_channel.get(e.channel, []))
        if e.marker_complete and counts:
            median = counts[len(counts) // 2]
            e.complete = e.file_count >= MIN_FILE_RATIO * median


# --------------------------------------------------------------------------- process scan


def scan_processes() -> tuple[dict, list]:
    """Map (channel, commit) -> ["pid:how", ...]; also return unreadable pids."""
    refs: dict[tuple, list] = {}
    unreadable: list = []
    me = os.getpid()

    def note(text: str, pid: str, how: str):
        for m in REF_RE.finditer(text):
            refs.setdefault((m["channel"], m["commit"]), []).append(f"{pid}:{how}")

    for pid in os.listdir("/proc"):
        if not pid.isdigit() or int(pid) == me:
            continue
        base = f"/proc/{pid}"
        try:
            for link in ("exe", "cwd", "root"):
                try:
                    note(os.readlink(f"{base}/{link}"), pid, link)
                except FileNotFoundError:
                    if not os.path.exists(base):
                        raise
            try:
                for fd in os.listdir(f"{base}/fd"):
                    try:
                        note(os.readlink(f"{base}/fd/{fd}"), pid, "fd")
                    except FileNotFoundError:
                        continue
            except FileNotFoundError:
                if not os.path.exists(base):
                    raise
            for fname, how in (("cmdline", "cmdline"), ("environ", "environ"), ("maps", "maps")):
                try:
                    with open(f"{base}/{fname}", "rb") as fh:
                        data = fh.read().replace(b"\0", b" ").decode("utf-8", "replace")
                except FileNotFoundError:
                    if not os.path.exists(base):
                        raise
                    continue
                note(data, pid, how)
        except (FileNotFoundError, ProcessLookupError):
            continue  # process exited while scanning
        except PermissionError:
            unreadable.append(pid)
    return refs, unreadable


# --------------------------------------------------------------------------- decision


def decide(entries: list, refs: dict, scan_complete: bool, cfg: Config) -> None:
    channels: dict = {}
    for e in entries:
        channels.setdefault(e.channel, {}).setdefault(e.commit, {})["staging" if e.staging else "final"] = e

    for channel, keys in channels.items():
        complete = []
        for commit, pair in keys.items():
            f = pair.get("final")
            if f and f.complete and f.version and not f.inspect_error:
                complete.append((f.version, commit))
        complete.sort(reverse=True)
        keep_commits = {c for _, c in complete[: cfg.keep_complete]}
        newest_version = complete[0][0] if complete else None

        for commit, pair in keys.items():
            key_version = next((x.version for x in (pair.get("final"), pair.get("staging")) if x and x.version), None)
            used_by = refs.get((channel, commit))
            for e in pair.values():
                reasons = []
                if e.inspect_error:
                    reasons.append(f"inspect-error({e.inspect_error})")
                if not scan_complete:
                    reasons.append("process-scan-incomplete")
                if used_by:
                    reasons.append("in-use(" + ",".join(sorted(set(used_by))[:6]) + ")")
                if e.active:
                    reasons.append("recent-writes")
                if e.staging:
                    if e.age_s < cfg.staging_age_s:
                        reasons.append(f"staging-younger-than-{cfg.staging_age_s / 86400:g}d")
                else:
                    if commit in keep_commits:
                        reasons.append(f"newest-{cfg.keep_complete}-complete")
                    if e.age_s < cfg.max_age_s:
                        reasons.append(f"younger-than-{cfg.max_age_s / 86400:g}d")
                    if newest_version is None:
                        reasons.append("no-complete-install-in-channel")
                    elif key_version is None:
                        reasons.append("version-unknown")
                    elif key_version > newest_version:
                        reasons.append("newer-than-newest-complete")
                if reasons:
                    e.action, e.reasons = "keep", reasons
                else:
                    e.action = "delete"
                    e.reasons = [
                        "orphaned-staging" if e.staging
                        else ("outdated-unused-install" if e.complete else "incomplete-outdated-unused")
                    ]


# --------------------------------------------------------------------------- deletion


def delete_entry(e: Entry, cfg: Config, servers_dir: str, servers_dev: int) -> tuple[bool, str]:
    """Delete one entry after re-validating path and usage right before removal."""
    path = e.path
    if os.path.dirname(path) != servers_dir or not ENTRY_RE.match(os.path.basename(path)):
        return False, "path-outside-servers-dir"
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return False, "already-gone"
    if not stat.S_ISDIR(st.st_mode) or stat.S_ISLNK(st.st_mode):
        return False, "not-a-plain-directory"
    if os.path.realpath(path) != path:
        return False, "path-resolves-elsewhere"
    if st.st_dev != servers_dev:
        return False, "different-filesystem"
    refs, unreadable = scan_processes()
    if unreadable:
        return False, "process-scan-incomplete"
    if (e.channel, e.commit) in refs:
        return False, "became-in-use"
    if (cfg.now - walk_stats(path)[1]) < cfg.active_grace_s:
        return False, "became-active"
    errors = []
    shutil.rmtree(path, onerror=lambda fn, p, exc: errors.append(f"{p}: {exc[1]}"))
    if errors:
        return False, "rmtree-errors: " + "; ".join(errors[:3])
    return True, "deleted"


# --------------------------------------------------------------------------- main


def validate_servers_dir(raw: str) -> str:
    path = os.path.abspath(raw)
    if os.path.islink(path) or os.path.realpath(path) != path:
        raise ValueError(f"servers dir must not be or contain a symlink: {raw}")
    parts = path.split(os.sep)
    if len(parts) < 4 or parts[-1] != "servers" or parts[-2] != "cli" or not parts[-3].startswith(".vscode-server"):
        raise ValueError(f"refusing to operate on {path}: expected <...>/.vscode-server/cli/servers")
    if not os.path.isdir(path):
        raise ValueError(f"not a directory: {path}")
    return path


def parse_args(argv):
    ap = argparse.ArgumentParser(description="Safely remove stale VS Code Server installations.")
    ap.add_argument("--servers-dir", default=DEFAULT_SERVERS_DIR)
    ap.add_argument("--apply", action="store_true", help="actually delete (default: dry-run)")
    ap.add_argument("--keep-complete", type=int, default=2, help="newest complete installs kept per channel")
    ap.add_argument("--max-age-days", type=float, default=14, help="min age of an unused install before removal")
    ap.add_argument("--staging-age-days", type=float, default=7, help="min age of an orphaned .staging before removal")
    ap.add_argument("--active-grace-minutes", type=float, default=60, help="keep entries changed within this window")
    ap.add_argument("--format", choices=("auto", "json", "text"), default="auto")
    ap.add_argument("--lock-file", default=DEFAULT_LOCK_FILE)
    ap.add_argument("--now", type=float, default=None, help=argparse.SUPPRESS)  # tests only
    return ap.parse_args(argv)


def run(args, log: Logger) -> int:
    mode = "apply" if args.apply else "dry-run"

    try:
        servers_dir = validate_servers_dir(args.servers_dir)
    except ValueError as exc:
        log.emit("refused", "error", reason=str(exc))
        return EXIT_REFUSED
    if args.keep_complete < 1:
        log.emit("refused", "error", reason="--keep-complete must be >= 1")
        return EXIT_REFUSED

    lock_fh = open(args.lock_file, "a+")  # noqa: SIM115 - held for the whole run
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log.emit("locked", "warn", detail="another cleanup run is in progress; exiting", lock=args.lock_file)
        return EXIT_LOCKED

    cfg = Config(
        servers_dir=servers_dir,
        apply=args.apply,
        keep_complete=args.keep_complete,
        max_age_s=args.max_age_days * 86400,
        staging_age_s=args.staging_age_days * 86400,
        active_grace_s=args.active_grace_minutes * 60,
        now=args.now if args.now is not None else time.time(),
    )
    servers_dev = os.lstat(servers_dir).st_dev
    before = shutil.disk_usage(servers_dir)
    log.emit("start", mode=mode, servers_dir=servers_dir, keep_complete=cfg.keep_complete,
             max_age_days=args.max_age_days, staging_age_days=args.staging_age_days)

    entries, ignored = [], []
    for name in sorted(os.listdir(servers_dir)):
        m = ENTRY_RE.match(name)
        full = os.path.join(servers_dir, name)
        if not m or os.path.islink(full) or not os.path.isdir(full):
            ignored.append(name)
            continue
        entries.append(inspect_entry(servers_dir, name, m, cfg))
    if ignored:
        log.emit("ignored", names=",".join(ignored))

    refs, unreadable = scan_processes()
    scan_complete = not unreadable
    if not scan_complete:
        log.emit("process-scan-incomplete", "error", unreadable_pids=",".join(unreadable[:20]),
                 detail="no entry will be deleted; run as root")
    log.emit("process-scan", referenced_entries=len(refs), unreadable_pids=len(unreadable))

    apply_plausibility(entries)
    decide(entries, refs, scan_complete, cfg)
    for e in sorted(entries, key=lambda x: (x.channel, x.version or (), x.name), reverse=True):
        log.emit("decision", action=e.action, entry=e.name, version=e.version_str or "?",
                 kind="staging" if e.staging else ("install" if e.complete else "install-incomplete"),
                 age_days=round(e.age_s / 86400, 1), size_mb=round(e.size / 1048576, 1),
                 reasons="+".join(e.reasons))

    to_delete = [e for e in entries if e.action == "delete"]
    freed = deleted = failed = 0
    if args.apply:
        for e in to_delete:
            ok, why = delete_entry(e, cfg, servers_dir, servers_dev)
            if ok:
                deleted += 1
                freed += e.size
                log.emit("deleted", entry=e.name, size_mb=round(e.size / 1048576, 1))
            elif why in BENIGN_SKIPS:
                log.emit("delete-skipped", "warn", entry=e.name, reason=why)
            else:
                failed += 1
                log.emit("delete-failed", "error", entry=e.name, reason=why)
    after = shutil.disk_usage(servers_dir)
    result = "scan-incomplete" if not scan_complete else ("errors" if failed else "ok")
    log.emit("summary", "error" if result != "ok" else "info", result=result, mode=mode,
             entries=len(entries), kept=len(entries) - len(to_delete),
             candidates=len(to_delete), candidates_mb=round(sum(e.size for e in to_delete) / 1048576, 1),
             deleted=deleted, freed_mb=round(freed / 1048576, 1), errors=failed,
             fs_used_before_pct=round(100 * before.used / before.total, 1),
             fs_used_after_pct=round(100 * after.used / after.total, 1))
    if not scan_complete:
        return EXIT_SCAN_INCOMPLETE
    return EXIT_ERRORS if failed else EXIT_OK


def main(argv=None) -> int:
    args = parse_args(argv)
    fmt = args.format
    if fmt == "auto":
        fmt = "text" if sys.stdout.isatty() else "json"
    log = Logger(fmt)
    try:
        return run(args, log)
    except Exception as exc:  # noqa: BLE001 - report every unexpected failure as an error event
        log.emit("unexpected-error", "error", error=f"{type(exc).__name__}: {exc}",
                 trace=traceback.format_exc().replace("\n", " | "))
        return EXIT_ERRORS


if __name__ == "__main__":
    sys.exit(main())
