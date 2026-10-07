"""Operator CLI: fixity baseline, verified institutional copy, verification, state and cleanup-eligibility report.

Dry-run is the default for every writing command; pass --execute to write. The tool never deletes, renames or
rewrites anything in the local archive and has no K:-specific (or any drive-specific) knowledge: the preservation
root comes from --preservation-root or PROMAT_PRESERVATION_ROOT.

    python archive_preservation.py baseline        [--execute]
    python archive_preservation.py copy            [--execute] [--exclude-secure]
    python archive_preservation.py verify          (full SHA-256 verification of the destination)
    python archive_preservation.py status
    python archive_preservation.py cleanup-report  [--candidate-dir DIR ...]

The backup-* commands run the same verified copy against the physically separate backup root (--backup-root or
PROMAT_BACKUP_ROOT). A backup is a different role: it has its own marker, receipts and states (BACKUP_PENDING,
BACKED_UP), never makes a unit PRESERVED or cleanup-eligible, and is never read by intake or the app.

    python archive_preservation.py backup-copy          [--execute]
    python archive_preservation.py backup-verify        [--unbuffered]   (full SHA-256 verification of the backup)
    python archive_preservation.py backup-status
    python archive_preservation.py backup-supplemental  [--execute] [--label NAME] [--extra NAME=PATH ...]

supplemental / backup-supplemental copy what the unit copy does not cover: the other archive-root entries, the
fixity baselines and any --extra source (a directory, a file or a glob), into supplemental/<label>/<set>/ with a
manifest of their own. verify --unbuffered reads every file from the device instead of the file cache.
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
from intake_storage import IntakeStorageError, get_local_archive_root

EXIT_OK = 0
EXIT_PROBLEMS = 1
EXIT_CONFIG = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "command",
        choices=(
            "baseline", "copy", "verify", "status", "cleanup-report", "supplemental",
            "backup-copy", "backup-verify", "backup-status", "backup-supplemental",
        ),
    )
    parser.add_argument("--archive-root", help="Local archive root (default: PROMAT_LOCAL_ARCHIVE_ROOT).")
    parser.add_argument("--preservation-root", help=f"Institutional root (default: ${pres.PRESERVATION_ROOT_ENV}; never defaulted).")
    parser.add_argument("--backup-root", help=f"Backup root for the backup-* commands (default: ${pres.BACKUP_ROOT_ENV}; never defaulted).")
    parser.add_argument("--unit", action="append", default=[], help="Limit to units matching this glob, e.g. 'sessions/es/*'. Repeatable.")
    parser.add_argument("--execute", action="store_true", help="Actually write (baseline, copy). Without it: dry-run.")
    parser.add_argument("--exclude-secure", action="store_true", help="Copy without secure/ content. Such units never count as PRESERVED.")
    parser.add_argument("--unbuffered", action="store_true", help="verify: read from the device, bypassing the OS file cache (cold verification).")
    parser.add_argument("--label", help="supplemental: snapshot label (default: today's UTC date).")
    parser.add_argument("--extra", action="append", default=[], metavar="NAME=PATH", help="supplemental: additional set from a directory, file or glob. Repeatable.")
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
    lines.append(f"- Role: {report['role']}")
    lines.append(f"- Root id: {report.get('root_id') or 'none'}")
    lines.append(f"- Result: **{report['result']}**")
    lines.append("")
    lines.append("## Summary")
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    not_covered = report.get("archive_root_entries_not_covered_by_unit_copy") or []
    lines.append("")
    lines.append("## Archive-root entries not covered by the unit copy")
    lines.extend([f"- `{name}`" for name in not_covered] or ["- none"])
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
    if report.get("archive_root_entries_not_covered_by_unit_copy"):
        print("NOTE not covered by the unit copy (preserve separately): " + ", ".join(report["archive_root_entries_not_covered_by_unit_copy"]))
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


def _base_report(command: str, execute: bool, root: pres.PreservationRoot | None, role: pres.RootRole) -> dict[str, Any]:
    return {
        "command": command,
        "role": role.name,
        "generated_at": provenance_helpers.utc_timestamp(),
        "execute": execute,
        "git_revision": provenance_helpers.current_git_revision(),
        "root_id": root.root_id if root else None,
        "preservation_root_id": root.root_id if root and role is pres.PRESERVATION else None,
        "units": [],
        "summary": {},
        "result": "ok",
    }


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        archive_root = Path(args.archive_root).expanduser() if args.archive_root else get_local_archive_root()
    except IntakeStorageError as exc:
        print(f"ERROR: {exc}")
        return EXIT_CONFIG
    if not archive_root.is_dir():
        print(f"ERROR: local archive root does not exist: {archive_root}")
        return EXIT_CONFIG
    units = _select_units(archive_root, args.unit)
    # A backup command is the same operation against the other role's root; the role decides marker, receipts and states.
    role = pres.BACKUP if args.command.startswith("backup-") else pres.PRESERVATION
    command = args.command.removeprefix("backup-")
    if args.preservation_root if role is pres.BACKUP else args.backup_root:
        print(f"ERROR: {args.command} works on the {role.name} root; pass {role.cli_option}, not the other role's option.")
        return EXIT_CONFIG
    if role is pres.BACKUP and args.exclude_secure:
        print("ERROR: a backup is always complete; --exclude-secure is not available for backup-copy.")
        return EXIT_CONFIG

    root: pres.PreservationRoot | None = None
    if command != "baseline":
        try:
            root_path = pres.resolve_preservation_root_path(args.backup_root if role is pres.BACKUP else args.preservation_root, role)
            migrated_from = archive_root.parent if role is pres.PRESERVATION and archive_root.name == pres.DEST_ARCHIVE_DIR else None
            root = pres.open_preservation_root(
                root_path,
                archive_root=archive_root,
                initialize=(command in {"copy", "supplemental"} and args.execute),
                migrated_from=migrated_from,
                role=role,
            )
        except pres.PreservationConfigError as exc:
            if command in {"status", "cleanup-report"} and f"No {role.name} root configured" in str(exc):
                root = None  # states can still be reported (nothing can be PRESERVED)
            else:
                print(f"ERROR: {exc}")
                return EXIT_CONFIG
        if command in {"copy", "verify"} and root is not None and root.root_id is None and (not args.execute or command == "verify"):
            if command == "verify":
                print(f"ERROR: the {role.name} root is not initialised (no marker); nothing to verify.")
                return EXIT_CONFIG

    report = _base_report(args.command, args.execute, root, role)
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

    elif command == "supplemental":
        label = args.label or datetime.now(UTC).strftime("%Y-%m-%d")
        sources: dict[str, Path | str] = dict(pres.archive_supplemental_sources(archive_root))
        for item in args.extra:
            name, separator, source = item.partition("=")
            if not separator or not name or not source or name in sources:
                print(f"ERROR: --extra needs a unique NAME=PATH, got {item!r}")
                return EXIT_CONFIG
            sources[name] = source
        results = [
            pres.copy_supplemental_set(archive_root, root, label, name, pres.collect_source_files(source), execute=args.execute)
            for name, source in sorted(sources.items())
        ]
        report["units"] = results
        problems = sum(1 for r in results if r["problems"])
        counts = {}
        for r in results:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        report["summary"] = {"label": label, "sets": len(results), "files": sum(r["files"] for r in results), "bytes": sum(r["bytes"] for r in results), **counts}

    elif command in {"verify", "status"}:
        full = command == "verify"
        states = [pres.derive_state(archive_root, unit, root, full_verify=full, role=role, unbuffered=args.unbuffered) for unit in units]
        report["units"] = [{**s, "problems": []} for s in states]
        counts = {state: sum(1 for s in states if s["state"] == state) for state in role.states}
        report["summary"] = {"units": len(states), **counts}
        if full:
            problems = sum(1 for s in states if s["state"] == role.pending_state and any("verification failed" in r for r in s["reasons"]))
            supplemental = pres.verify_supplemental(root, unbuffered=args.unbuffered) if root is not None and not args.unit else []
            failed = [s for s in supplemental if not s["ok"]]
            problems += len(failed)
            report["supplemental"] = supplemental
            report["units"].extend({**s, "problems": ["supplemental set failed verification"]} for s in failed)
            verified = [s["evidence"] for s in states if s["state"] != role.pending_state and "destination_files" in s["evidence"]]
            report["summary"].update({
                "read_mode": "unbuffered" if args.unbuffered else "buffered",
                "verified_files": sum(e["destination_files"] for e in verified) + sum(s["files"] for s in supplemental if s["ok"]),
                "verified_bytes": sum(e["destination_bytes"] for e in verified) + sum(s["bytes"] for s in supplemental if s["ok"]),
                "supplemental_ok": len(supplemental) - len(failed),
                "supplemental_failed": len(failed),
            })

    else:  # cleanup-report
        cleanup = pres.cleanup_eligibility_report(archive_root, root, candidate_dirs=args.candidate_dir)
        report["units"] = [{**u, "problems": []} for u in cleanup["units"]]
        report["cleanup"] = {k: v for k, v in cleanup.items() if k != "units"}
        report["summary"] = {"units": len(cleanup["units"]), **cleanup["counts"], "deletes_anything": False}

    report["archive_root_entries_not_covered_by_unit_copy"] = pres.uncovered_top_level(archive_root)
    if problems:
        report["result"] = "problems"
    _emit(report, args.report_dir)
    return EXIT_PROBLEMS if problems else EXIT_OK


if __name__ == "__main__":
    sys.exit(run())
