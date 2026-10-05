"""Read-only local storage inventory for PROMAT.

Reports sizes of repository, intake, runtime, archive and export locations, git worktree state,
preservation-root availability and obvious cleanup candidates. It never modifies or deletes anything.

Usage:
    python scripts/storage_inventory.py
    python scripts/storage_inventory.py --preservation-root K:\\Pronunciation_Matters --measure-preservation
    python scripts/storage_inventory.py --json
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

REPO_ROOT = Path(__file__).resolve().parents[1]
INTAKE_ROOT = REPO_ROOT / "scripts" / "research_data_intake"
DEFAULT_LOCAL_ARCHIVE_ROOT = Path(r"C:\dev\promat_data_archive")
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


def archive_root() -> Path:
    configured = (os.getenv("PROMAT_LOCAL_ARCHIVE_ROOT") or "").strip()
    return Path(configured).expanduser() if configured else DEFAULT_LOCAL_ARCHIVE_ROOT


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
        ("local archive root", archive_root(), "SOURCE / UNIQUE until preserved"),
    ]
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


def gather(args: argparse.Namespace) -> dict[str, object]:
    report: dict[str, object] = {"repo_root": str(REPO_ROOT)}
    rows = []
    for label, path, role in measured_locations():
        size, count = dir_stats(path)
        rows.append({"label": label, "path": str(path), "bytes": size, "files": count, "role": role, "exists": path.exists()})
    report["locations"] = rows
    report["worktrees"] = worktrees()
    report["archive_root"] = {"path": str(archive_root()), "env_configured": bool(os.getenv("PROMAT_LOCAL_ARCHIVE_ROOT"))}
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
    report["cleanup_candidates"] = [{"what": w, "bytes": s, "files": c} for w, s, c in cleanup_candidates()]
    report["repo_volume_free_bytes"] = shutil.disk_usage(REPO_ROOT).free
    return report


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
    print(f"\nArchive root: {arch['path']} ({'PROMAT_LOCAL_ARCHIVE_ROOT' if arch['env_configured'] else 'built-in default'})")
    pres = report["preservation_root"]
    if pres["path"]:
        state = "reachable" if pres["reachable"] else "NOT reachable"
        extra = f", volume free {human(int(pres['volume_free_bytes']))}" if "volume_free_bytes" in pres else ""
        if "bytes" in pres:
            extra += f", content {human(int(pres['bytes']))} in {pres['files']} files"
        print(f"Preservation root {pres['path']}: {state}{extra}")
    else:
        print("Preservation root: not given (--preservation-root)")
    print("\nCleanup candidates (reproducible, never scientific data):")
    for item in report["cleanup_candidates"] or []:
        print(f"  {item['what']}: {human(item['bytes'])} in {item['files']} files")
    if not report["cleanup_candidates"]:
        print("  none")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--preservation-root", help="Institutional preservation root to probe (read-only).")
    parser.add_argument("--measure-preservation", action="store_true", help="Also walk the preservation root for size.")
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
