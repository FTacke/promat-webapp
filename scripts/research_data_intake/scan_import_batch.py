from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from intake_batch_common import resolve_batch_dir, scan_import_batch  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan one drop-in intake batch and report recognized workbooks, source files, warnings, and conflicts."
    )
    parser.add_argument("--batch-dir", required=True, help="Batch directory path or batch name under scripts/research_data_intake/import/.")
    parser.add_argument("--json", action="store_true", help="Emit the scan report as JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    batch_dir = resolve_batch_dir(args.batch_dir, require_processed=False)
    report = scan_import_batch(batch_dir)
    payload = {
        "batch_dir": batch_dir.as_posix(),
        "workbooks": [candidate.relative_source for candidate in report.workbooks],
        "recognized_files": [
            {
                "path": entry.relative_source,
                "person_id": entry.person_id,
                "task": entry.task,
                "file_kind": entry.file_kind,
                "file_role": entry.file_role,
            }
            for entry in report.parsed_files
        ],
        "warnings": list(report.warnings),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"[batch] {payload['batch_dir']}")
    print(f"[workbooks] {', '.join(payload['workbooks']) or 'none'}")
    print("[recognized-files]")
    for entry in payload["recognized_files"]:
        print(f"- {entry['path']}: {entry['person_id']} {entry['task']} {entry['file_role']} {entry['file_kind']}")
    print("[warnings]")
    for warning in payload["warnings"] or ["none"]:
        print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())