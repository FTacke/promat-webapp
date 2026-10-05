"""Operator CLI: fixity baseline, verified institutional copy, verification, state and cleanup-eligibility report.

Dry-run is the default for every writing command; pass --execute to write. The tool never deletes, renames or
rewrites anything in the local archive and has no K:-specific (or any drive-specific) knowledge: the preservation
root comes from --preservation-root or PROMAT_PRESERVATION_ROOT.

    python archive_preservation.py baseline        [--execute]
    python archive_preservation.py copy            [--execute] [--exclude-secure]
    python archive_preservation.py verify          (full SHA-256 verification of the destination)
    python archive_preservation.py status
    python archive_preservation.py cleanup-report  [--candidate-dir DIR ...]
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import fnmatch
import json
from pathlib import Path
import sys
from typing import Any, Sequence

import preservation as pres
import provenance as provenance_helpers
from intake_storage import get_local_archive_root

EXIT_OK = 0
EXIT_PROBLEMS = 1
EXIT_CONFIG = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("baseline", "copy", "verify", "status", "cleanup-report"))
    parser.add_argument("--archive-root", help="Local archive root (default: PROMAT_LOCAL_ARCHIVE_ROOT).")
    parser.add_argument("--preservation-root", help=f"Institutional root (default: ${pres.PRESERVATION_ROOT_ENV}; never defaulted).")
    parser.add_argument("--unit", action="append", default=[], help="Limit to units matching this glob, e.g. 'sessions/es/*'. Repeatable.")
    parser.add_argument("--execute", action="store_true", help="Actually write (baseline, copy). Without it: dry-run.")
    parser.add_argument("--exclude-secure", action="store_true", help="Copy without secure/ content. Such units never count as PRESERVED.")
    parser.add_argument("--candidate-dir", action="append", default=[], type=Path, help="cleanup-report: local tree to match against preserved content.")
    parser.add_argument("--report-dir", type=Path, help="Write <command>-<timestamp>.json/.md here (dry-runs write reports only when given).")
    return parser


def _select_units(archive_root: Path, patterns: Sequence[str]) -> list[str]:
    units = pres.discover_units(archive_root)
    if not patterns:
        return units
    return [u for u in units if any(fnmatch.fnmatch(u, pattern) for pattern in patterns)]


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# Archive preservation report: {report['command']}", ""]
    lines.append(f"- Generated: {report['generated_at']}")
    lines.append(f"- Mode: {'execute' if report['execute'] else 'dry-run'}")
    lines.append(f"- Git revision: {report['git_revision']}")
    lines.append(f"- Preservation root id: {report.get('preservation_root_id') or 'none'}")
    lines.append(f"- Result: **{report['result']}**")
    lines.append("")
    lines.append("## Summary")
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Units needing attention")
    flagged = [u for u in report["units"] if u.get("problems") or u.get("reasons")]
    if not flagged:
        lines.append("- none")
    for unit in flagged[:200]:
        detail = "; ".join(unit.get("problems") or unit.get("reasons") or [])
        lines.append(f"- `{unit['unit']}` ({unit.get('state') or unit.get('status')}): {detail}")
    lines.append("")
    return "\n".join(lines)


def _emit(report: dict[str, Any], report_dir: Path | None) -> None:
    print(f"[{report['command']}] result={report['result']} " + " ".join(f"{k}={v}" for k, v in report["summary"].items()))
    for unit in report["units"]:
        if unit.get("problems") or unit.get("reasons"):
            print(f"  - {unit['unit']}: " + "; ".join(unit.get("problems") or unit.get("reasons")))
    if report_dir is not None:
        report_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        stem = f"{report['command']}-{stamp}"
        (report_dir / f"{stem}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (report_dir / f"{stem}.md").write_text(_render_markdown(report), encoding="utf-8")
        print(f"reports: {report_dir / (stem + '.json')} and .md")


def _base_report(command: str, execute: bool, root: pres.PreservationRoot | None) -> dict[str, Any]:
    return {
        "command": command,
        "generated_at": provenance_helpers.utc_timestamp(),
        "execute": execute,
        "git_revision": provenance_helpers.current_git_revision(),
        "preservation_root_id": root.root_id if root else None,
        "units": [],
        "summary": {},
        "result": "ok",
    }


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    archive_root = Path(args.archive_root).expanduser() if args.archive_root else get_local_archive_root()
    if not archive_root.is_dir():
        print(f"ERROR: local archive root does not exist: {archive_root}")
        return EXIT_CONFIG
    units = _select_units(archive_root, args.unit)
    command = args.command

    root: pres.PreservationRoot | None = None
    if command != "baseline":
        try:
            root_path = pres.resolve_preservation_root_path(args.preservation_root)
            migrated_from = archive_root.parent if archive_root.name == pres.DEST_ARCHIVE_DIR else None
            root = pres.open_preservation_root(
                root_path,
                archive_root=archive_root,
                initialize=(command == "copy" and args.execute),
                migrated_from=migrated_from,
            )
        except pres.PreservationConfigError as exc:
            if command in {"status", "cleanup-report"} and "No preservation root configured" in str(exc):
                root = None  # states can still be reported (nothing can be PRESERVED)
            else:
                print(f"ERROR: {exc}")
                return EXIT_CONFIG
        if command in {"copy", "verify"} and root is not None and root.root_id is None and (not args.execute or command == "verify"):
            if command == "verify":
                print("ERROR: the preservation root is not initialised (no marker); nothing to verify.")
                return EXIT_CONFIG

    report = _base_report(command, args.execute, root)
    problems = 0

    if command == "baseline":
        results = [pres.baseline_unit(archive_root, unit, execute=args.execute) for unit in units]
        for r in results:
            r["problems"] = [] if r["status"] in {"baseline_written", "would_write_baseline", "baseline_present", "covered_by_unit_manifest"} else [r["status"]]
        problems = sum(1 for r in results if r["problems"])
        counts: dict[str, int] = {}
        for r in results:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        report["units"] = results
        report["summary"] = {"units": len(results), "files": sum(r["files"] for r in results), **counts}

    elif command == "copy":
        results = [pres.copy_unit(archive_root, unit, root, execute=args.execute, exclude_secure=args.exclude_secure) for unit in units]
        report["units"] = [
            {"unit": r.unit, "status": r.status, "scope": r.scope, "problems": r.problems, "receipt": r.receipt_path,
             "files": len(r.files)}
            for r in results
        ]
        problems = sum(1 for r in results if r.status == "failed")
        counts = {}
        for r in results:
            counts[r.status] = counts.get(r.status, 0) + 1
        report["summary"] = {"units": len(results), **counts}

    elif command in {"verify", "status"}:
        states = [pres.derive_state(archive_root, unit, root, full_verify=(command == "verify")) for unit in units]
        report["units"] = [{**s, "problems": []} for s in states]
        counts = {state: sum(1 for s in states if s["state"] == state) for state in pres.STATES}
        report["summary"] = {"units": len(states), **counts}
        if command == "verify":
            problems = sum(1 for s in states if s["state"] in {pres.STATE_PENDING} and any("verification failed" in r for r in s["reasons"]))

    else:  # cleanup-report
        cleanup = pres.cleanup_eligibility_report(archive_root, root, candidate_dirs=args.candidate_dir)
        report["units"] = [{**u, "problems": []} for u in cleanup["units"]]
        report["cleanup"] = {k: v for k, v in cleanup.items() if k != "units"}
        report["summary"] = {"units": len(cleanup["units"]), **cleanup["counts"], "deletes_anything": False}

    if problems:
        report["result"] = "problems"
    _emit(report, args.report_dir)
    return EXIT_PROBLEMS if problems else EXIT_OK


if __name__ == "__main__":
    sys.exit(run())
