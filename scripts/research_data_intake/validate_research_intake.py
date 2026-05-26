from __future__ import annotations

import argparse
from pathlib import Path
import sys


SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from intake_storage import validate_archive_tree, validate_prod_package, validate_runtime_tree  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate PROMAT runtime, archive, or prod upload package trees.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    runtime_parser = subparsers.add_parser("runtime-tree", help="Validate one runtime session tree.")
    runtime_parser.add_argument("--session-dir", required=True, help="Path to data/sessions/{language}/{session_id}/")

    archive_parser = subparsers.add_parser("archive-tree", help="Validate one archive session tree.")
    archive_parser.add_argument("--archive-session-dir", required=True, help="Path to archive sessions/{lang}/{session_id}/")

    package_parser = subparsers.add_parser("prod-package", help="Validate one built prod upload package.")
    package_parser.add_argument("--package-dir", required=True, help="Path to one upload package directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "runtime-tree":
        errors = validate_runtime_tree(Path(args.session_dir))
    elif args.command == "archive-tree":
        errors = validate_archive_tree(Path(args.archive_session_dir))
    else:
        errors = validate_prod_package(Path(args.package_dir))
    if errors:
        print("[errors]")
        for error in errors:
            print(f"- {error}")
        return 1
    print("[ok] validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())