from __future__ import annotations

import argparse
from datetime import UTC, datetime
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_SRC = REPO_ROOT / "app" / "src"
SCRIPT_ROOT = Path(__file__).resolve().parent
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from app.runtime_paths import get_sessions_root  # noqa: E402
from intake_storage import IntakeStorageError, build_prod_upload_package  # noqa: E402
from language_config import maybe_resolve_language_config, resolve_language_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an explicit allowlist-based PROMAT prod upload package from validated runtime artifacts."
    )
    parser.add_argument("--language", help="Corpus language slug or code for the runtime session lookup, for example spanish or es.")
    parser.add_argument("--session-id", action="append", help="Session to include. Repeat for multiple sessions.")
    parser.add_argument(
        "--all-runtime-sessions",
        action="store_true",
        help="Include every existing data/sessions/{language}/{session_id}/ runtime session with a metadata.json file.",
    )
    parser.add_argument("--db-payload", help="Optional path to a prebuilt import_payload.json.")
    parser.add_argument(
        "--include-research-player-config",
        action="store_true",
        help="Include data/config/research_player JSON files in the package.",
    )
    parser.add_argument("--upload-id", help="Optional explicit upload id. Defaults to promat_upload_<UTC timestamp>.")
    parser.add_argument("--output-dir", help="Optional explicit package output directory.")
    return parser.parse_args()


_TASK_KEYS = ("wordlist", "text", "interview")


def _session_dir_has_task_artifacts(session_dir: Path) -> bool:
    for task_key in _TASK_KEYS:
        if (session_dir / "alignment" / f"{task_key}.json").exists():
            return True
        if (session_dir / "derived" / f"{task_key}.mp3").exists():
            return True
    return False


def _discover_all_runtime_sessions() -> list[tuple[str, Path]]:
    sessions_root = get_sessions_root()
    session_roots: list[tuple[str, Path]] = []
    for language_dir in sorted(path for path in sessions_root.iterdir() if path.is_dir()):
        language = maybe_resolve_language_config(language_dir.name)
        session_dirs = sorted(path for path in language_dir.iterdir() if path.is_dir())
        if language is None:
            if session_dirs:
                raise IntakeStorageError(f"unsupported runtime language directory with sessions: {language_dir}")
            continue
        for session_dir in session_dirs:
            if not (session_dir / "metadata.json").exists():
                continue
            if not _session_dir_has_task_artifacts(session_dir):
                continue
            session_roots.append((language.code, session_dir))
    return session_roots


def main() -> int:
    args = parse_args()
    if args.all_runtime_sessions:
        if args.language or args.session_id:
            print("ERROR: --all-runtime-sessions cannot be combined with --language or --session-id")
            return 1
        session_roots = _discover_all_runtime_sessions()
        if not session_roots:
            print(f"ERROR: no runtime sessions found under {get_sessions_root()}")
            return 1
    else:
        if not args.language or not args.session_id:
            print("ERROR: --language and at least one --session-id are required unless --all-runtime-sessions is used")
            return 1
        language = resolve_language_config(args.language)
        session_roots = []
        for session_id in args.session_id:
            session_dir = get_sessions_root() / language.corpus_slug / session_id
            if not session_dir.exists():
                print(f"ERROR: unknown runtime session directory: {session_dir}")
                return 1
            session_roots.append((language.code, session_dir))

    upload_id = args.upload_id or f"promat_upload_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    output_dir = Path(args.output_dir) if args.output_dir else (SCRIPT_ROOT / "exports" / upload_id)

    db_payload = None
    if args.db_payload:
        db_payload = __import__("json").loads(Path(args.db_payload).read_text(encoding="utf-8"))

    config_roots = []
    if args.include_research_player_config:
        config_roots.append(REPO_ROOT / "data" / "config" / "research_player")

    try:
        result = build_prod_upload_package(
            output_dir=output_dir,
            session_roots=session_roots,
            db_payload=db_payload,
            config_roots=config_roots,
            upload_id=upload_id,
        )
    except IntakeStorageError as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"[upload-id] {upload_id}")
    print(f"[output-dir] {result.output_dir}")
    print(f"[manifest] {result.manifest_path}")
    print(f"[checksums] {result.checksums_path}")
    print(f"[files] {len(result.relative_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
