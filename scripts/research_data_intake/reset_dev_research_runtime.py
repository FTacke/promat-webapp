from __future__ import annotations

import argparse
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_SRC = REPO_ROOT / "app" / "src"
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))

from app.runtime_paths import get_sessions_root  # noqa: E402


PROTECTED_FILENAMES = {".gitkeep", "README.md"}
DEFAULT_LANGUAGE_DIRS = ("de", "en", "es", "fr")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Explicitly reset local dev research runtime files under data/sessions without touching content, Teaching, prod paths, or the local archive."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required confirmation flag. Without it the command only prints what it would remove.",
    )
    return parser.parse_args()


def _remove_runtime_children(path: Path) -> None:
    for child in path.iterdir():
        if child.is_file() and child.name in PROTECTED_FILENAMES:
            continue
        if child.is_dir():
            import shutil

            shutil.rmtree(child)
        elif child.is_file():
            child.unlink()


def main() -> int:
    args = parse_args()
    sessions_root = get_sessions_root()
    if not sessions_root.exists():
        print(f"[skip] sessions root missing: {sessions_root}")
        return 0

    if not args.yes:
        print(f"[dry-run] would clean: {sessions_root}")
        print("[note] content/, Teaching/public, prod paths, and PROMAT_LOCAL_ARCHIVE_ROOT stay untouched")
        return 0

    _remove_runtime_children(sessions_root)
    for language_dir in DEFAULT_LANGUAGE_DIRS:
        (sessions_root / language_dir).mkdir(parents=True, exist_ok=True)
    print(f"[done] cleaned runtime session directories under {sessions_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())