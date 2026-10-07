"""Read-only local storage inventory for PROMAT.

Reports sizes of repository, intake, runtime, archive and export locations, git worktree state,
preservation-root availability and obvious cleanup candidates. It never modifies or deletes anything.

Usage:
    python scripts/storage_inventory.py
    python scripts/storage_inventory.py --preservation-root <preservation root> --measure-preservation
    python scripts/storage_inventory.py --json
    (roots come from PROMAT_LOCAL_ARCHIVE_ROOT, PROMAT_PRESERVATION_ROOT and PROMAT_BACKUP_ROOT, in the environment
    or the repository-root .env; states/cleanup model: scripts/research_data_intake/archive_preservation.py)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# The preservation model (states, receipts, cleanup schema) lives in the intake scripts; the inventory only reads it.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research_data_intake"))

import storage_roots  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
INTAKE_ROOT = REPO_ROOT / "scripts" / "research_data_intake"
QA_DEBRIS_PATTERN = re.compile(
    r"^(ui-qa|mobile-audit-|edge-qa-|phenomena-followup-|promat-phenomena-|promat-ui-qa-|shell-|topbar-|drawer-)"
)
CACHE_DIRS = (".mypy_cache", ".ruff_cache", ".pytest_cache")


def dir_stats(path: Path) -> tuple[int, int]:
    """Return (bytes, file_count) for a directory tree; (0, 0) when missing."""
    total = count = 0
    if not path.exists():
        return 0, 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
                count += 1
            except OSError:
                continue
    return total, count


def human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:,.1f} {unit}"
        value /= 1024
    return f"{size} B"


def archive_root() -> Path | None:
    """The configured local archive root, or ``None``. The inventory reports an unset root; it never assumes one."""
    try:
        return storage_roots.configured_root(storage_roots.LOCAL_ARCHIVE_ROOT_ENV)
    except storage_roots.StorageRootNotConfigured:
        return None


def worktrees() -> list[dict[str, object]]:
    try:
        out = subprocess.run(
            ["git", "worktree", "list", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    entries: list[dict[str, object]] = []
    for block in out.strip().split("\n\n"):
        item: dict[str, object] = {}
        for line in block.splitlines():
            key, _, value = line.partition(" ")
            item[key] = value or True
        if "worktree" in item:
            path = Path(str(item["worktree"]))
            item["exists"] = path.exists()
            if path.exists():
                status = subprocess.run(
                    ["git", "status", "--porcelain"], cwd=path, capture_output=True, text=True
                ).stdout
                item["dirty_files"] = len([line for line in status.splitlines() if line.strip()])
            entries.append(item)
    return entries


def measured_locations() -> list[tuple[str, Path, str]]:
    """(label, path, role) tuples; roles follow docs/runbooks/local-storage-hygiene.md."""
    locations: list[tuple[str, Path, str]] = [
        ("git objects", REPO_ROOT / ".git", "SOURCE (repository history)"),
        ("python venv", REPO_ROOT / ".venv", "CACHE (recreatable)"),
        ("runtime sessions", REPO_ROOT / "data" / "sessions", "REGENERABLE (from archive + importer)"),
        ("dev postgres data", REPO_ROOT / "data" / "db", "UNKNOWN (database volume, never a cache)"),
        ("tmp", REPO_ROOT / "tmp", "WORKING/REGENERABLE (QA debris + intake run notes)"),
        ("intake .mfa_cache", INTAKE_ROOT / ".mfa_cache", "CACHE (MFA models)"),
        ("intake exports", INTAKE_ROOT / "exports", "SPOOL (upload packages)"),
    ]
    local_archive = archive_root()
    if local_archive is not None:
        locations.append(("local archive root", local_archive, "SOURCE / UNIQUE until preserved"))
    import_root = INTAKE_ROOT / "import"
    if import_root.is_dir():
        for batch in sorted(p for p in import_root.iterdir() if p.is_dir() and not p.name.startswith("__")):
            locations.append((f"intake batch {batch.name}", batch, "SOURCE copy + WORKING"))
            if (batch / "working").is_dir():
                locations.append((f"  working/ of {batch.name}", batch / "working", "WORKING (MFA corpus regenerable)"))
    return locations


def cleanup_candidates() -> list[tuple[str, int, int]]:
    candidates: list[tuple[str, int, int]] = []
    for name in CACHE_DIRS:
        size, count = dir_stats(REPO_ROOT / name)
        if count:
            candidates.append((name, size, count))
    tmp_root = REPO_ROOT / "tmp"
    if tmp_root.is_dir():
        size = count = 0
        for child in tmp_root.iterdir():
            if child.is_dir() and QA_DEBRIS_PATTERN.match(child.name):
                child_size, child_count = dir_stats(child)
                size += child_size
                count += child_count
            elif child.is_file() and child.suffix in {".png", ".html"}:
                size += child.stat().st_size
                count += 1
        if count:
            candidates.append(("tmp/ QA captures and browser profiles", size, count))
    return candidates


def preservation_section(args: argparse.Namespace) -> dict[str, object]:
    """Read-only preservation status: root probe, quick per-unit states and the optional cleanup JSON.

    Logic is not duplicated: states come from preservation.derive_state (quick mode: existence and size, no
    hashing, so at most PRESERVED). LOCAL_CLEANUP_ELIGIBLE appears only through a cleanup-report JSON produced by
    ``archive_preservation.py cleanup-report`` (a snapshot; regenerate it before acting on it).
    """
    import preservation as pres  # local import keeps the inventory usable without the intake scripts

    local_archive = archive_root()
    configured = args.preservation_root or storage_roots.configured_value(pres.PRESERVATION_ROOT_ENV)
    section: dict[str, object] = {
        "configured": bool(configured),
        "source": "argument" if args.preservation_root else ("PROMAT_PRESERVATION_ROOT" if configured else None),
        "path": configured,
        "reachable": False,
        "root_id": None,
        "unit_states": None,
        "cleanup_report": None,
        "archive_root_entries_not_covered_by_unit_copy": pres.uncovered_top_level(local_archive) if local_archive else [],
    }
    root = None
    if configured:
        root_path = Path(configured)
        section["reachable"] = root_path.exists()
        if local_archive is not None:
            try:
                root = pres.open_preservation_root(root_path, archive_root=local_archive, initialize=False)
                section["root_id"] = root.root_id
            except pres.PreservationConfigError as exc:
                section["error"] = str(exc)
    if local_archive is not None and local_archive.is_dir():
        states = [pres.derive_state(local_archive, unit, root, full_verify=False) for unit in pres.discover_units(local_archive)]
        section["unit_states"] = {state: sum(1 for s in states if s["state"] == state) for state in pres.STATES}
        section["unit_states"]["note"] = "quick check (no hashing); eligibility needs archive_preservation.py cleanup-report"
    if args.cleanup_report:
        try:
            payload = json.loads(Path(args.cleanup_report).read_text(encoding="utf-8"))
            cleanup = payload.get("cleanup", payload)
            if cleanup.get("schema") != pres.CLEANUP_SCHEMA or cleanup.get("deletes_anything") is not False:
                raise ValueError(f"not a {pres.CLEANUP_SCHEMA} report")
            section["cleanup_report"] = {
                "generated_at": cleanup.get("generated_at"),
                "counts": cleanup.get("counts"),
                "duplicate_bytes": sum(
                    d["size"] for c in cleanup.get("candidate_directories", []) for d in c.get("duplicates", [])
                ),
                "snapshot_warning": "snapshot only; regenerate before any operator action",
            }
        except (OSError, ValueError) as exc:
            section["cleanup_report"] = {"error": str(exc)}
    return section


def backup_section() -> dict[str, object]:
    """Read-only state of the physical backup. An offline backup volume is a normal, reported state."""
    import preservation as pres

    local_archive = archive_root()
    configured = storage_roots.configured_value(pres.BACKUP_ROOT_ENV)
    section: dict[str, object] = {"configured": bool(configured), "path": configured, "reachable": False, "root_id": None, "unit_states": None}
    if not configured:
        return section
    root_path = Path(configured)
    section["reachable"] = root_path.exists()
    if local_archive is None or not local_archive.is_dir():
        return section
    root = None
    try:
        root = pres.open_preservation_root(root_path, archive_root=local_archive, initialize=False, role=pres.BACKUP)
        section["root_id"] = root.root_id
    except pres.PreservationConfigError as exc:
        section["error"] = str(exc)
    if section["reachable"] and root is not None:
        states = [pres.derive_state(local_archive, unit, root, full_verify=False) for unit in pres.discover_units(local_archive)]
        section["unit_states"] = {state: sum(1 for s in states if s["state"] == state) for state in pres.BACKUP.states}
    return section


def gather(args: argparse.Namespace) -> dict[str, object]:
    report: dict[str, object] = {"repo_root": str(REPO_ROOT)}
    rows = []
    for label, path, role in measured_locations():
        size, count = dir_stats(path)
        rows.append({"label": label, "path": str(path), "bytes": size, "files": count, "role": role, "exists": path.exists()})
    report["locations"] = rows
    report["worktrees"] = worktrees()
    local_archive = archive_root()
    report["archive_root"] = {
        "path": str(local_archive) if local_archive else None,
        "source": storage_roots.configured_source(storage_roots.LOCAL_ARCHIVE_ROOT_ENV),
    }
    preservation: dict[str, object] = {"path": args.preservation_root, "reachable": False}
    if args.preservation_root:
        root = Path(args.preservation_root)
        preservation["reachable"] = root.exists()
        anchor = root.anchor or str(root)
        if Path(anchor).exists():
            preservation["volume_free_bytes"] = shutil.disk_usage(anchor).free
        if root.exists() and args.measure_preservation:
            preservation["bytes"], preservation["files"] = dir_stats(root)
    report["preservation_root"] = preservation
    report["preservation"] = preservation_section(args)
    report["backup"] = backup_section()
    report["cleanup_candidates"] = [{"what": w, "bytes": s, "files": c} for w, s, c in cleanup_candidates()]
    report["repo_volume_free_bytes"] = shutil.disk_usage(REPO_ROOT).free
    return report


def print_preservation(section: dict[str, object]) -> None:
    print("\nPreservation status (read-only; local archive remains the working archive, the root is a second verified copy):")
    if section["unit_states"]:
        print("  unit states: " + ", ".join(f"{k}={v}" for k, v in section["unit_states"].items() if k != "note"))
    if section.get("archive_root_entries_not_covered_by_unit_copy"):
        print("  not covered by the unit copy: " + ", ".join(section["archive_root_entries_not_covered_by_unit_copy"]))
    if section.get("error"):
        print(f"  preservation root error: {section['error']}")
    if section["root_id"]:
        print(f"  preservation root id: {section['root_id']}")
    cleanup = section["cleanup_report"]
    if cleanup and "error" in cleanup:
        print(f"  cleanup report unreadable: {cleanup['error']}")
    elif cleanup:
        counts = cleanup.get("counts") or {}
        print(f"  cleanup report ({cleanup['generated_at']}): " + ", ".join(f"{k}={v}" for k, v in counts.items())
              + f"; duplicate local bytes {human(int(cleanup['duplicate_bytes']))} ({cleanup['snapshot_warning']})")


def print_report(report: dict[str, object]) -> None:
    print(f"PROMAT storage inventory (read-only) - repo {report['repo_root']}")
    print(f"Repo volume free: {human(int(report['repo_volume_free_bytes']))}\n")
    print(f"{'location':44} {'size':>12} {'files':>8}  role")
    for row in report["locations"]:
        if not row["exists"]:
            print(f"{row['label']:44} {'missing':>12} {'':>8}  {row['role']}")
            continue
        print(f"{row['label']:44} {human(row['bytes']):>12} {row['files']:>8}  {row['role']}")
    print("\nWorktrees:")
    for wt in report["worktrees"]:
        flags = []
        if not wt.get("exists"):
            flags.append("MISSING (prunable)")
        if wt.get("prunable"):
            flags.append("prunable")
        if wt.get("dirty_files"):
            flags.append(f"{wt['dirty_files']} modified/untracked")
        print(f"  {wt['worktree']} [{wt.get('branch', 'detached')}] {' '.join(flags) or 'clean'}")
    arch = report["archive_root"]
    if arch["path"]:
        print(f"\nArchive root: {arch['path']} (PROMAT_LOCAL_ARCHIVE_ROOT from {arch['source']})")
    else:
        print("\nArchive root: NOT CONFIGURED (set PROMAT_LOCAL_ARCHIVE_ROOT; there is no default location)")
    pres = report["preservation_root"]
    if not pres["path"] and report["preservation"]["configured"]:
        pres = {**pres, "path": report["preservation"]["path"], "reachable": report["preservation"]["reachable"]}
    if pres["path"]:
        state = "reachable" if pres["reachable"] else "NOT reachable"
        extra = f", volume free {human(int(pres['volume_free_bytes']))}" if "volume_free_bytes" in pres else ""
        if "bytes" in pres:
            extra += f", content {human(int(pres['bytes']))} in {pres['files']} files"
        print(f"Preservation root {pres['path']}: {state}{extra}")
    else:
        print("Preservation root: not configured (--preservation-root or PROMAT_PRESERVATION_ROOT)")
    print_preservation(report["preservation"])
    backup = report["backup"]
    if not backup["configured"]:
        print("\nBackup root: not configured (PROMAT_BACKUP_ROOT)")
    elif not backup["reachable"]:
        print(f"\nBackup root {backup['path']}: OFFLINE or missing (a backup volume may be disconnected; nothing else depends on it)")
    else:
        states = backup["unit_states"] or {}
        print(f"\nBackup root {backup['path']}: reachable, id {backup['root_id'] or 'not initialised'}"
              + ("; " + ", ".join(f"{k}={v}" for k, v in states.items()) if states else ""))
    if backup.get("error"):
        print(f"  backup root error: {backup['error']}")
    print("\nCleanup candidates (reproducible, never scientific data):")
    for item in report["cleanup_candidates"] or []:
        print(f"  {item['what']}: {human(item['bytes'])} in {item['files']} files")
    if not report["cleanup_candidates"]:
        print("  none")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--preservation-root", help="Institutional preservation root to probe (read-only).")
    parser.add_argument("--measure-preservation", action="store_true", help="Also walk the preservation root for size.")
    parser.add_argument("--cleanup-report", help="JSON from archive_preservation.py cleanup-report (read only).")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args(argv)
    report = gather(args)
    if args.json:
        json.dump(report, sys.stdout, indent=2, default=str)
        print()
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
