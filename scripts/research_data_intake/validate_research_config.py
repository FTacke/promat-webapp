"""Validate the operator-owned research-player configuration against the app's own loaders.

The canonical task catalogs and player configs live under ``<PROMAT_RUNTIME_ROOT>/data/config/research_player/``
and are intentionally not versioned in this repository (see ``docs/runbooks/test-and-ci.md``). This tool is the
reproducible way to check that a runtime root (a developer machine, a package about to be shipped, or the
server-side data directory) holds a loadable configuration.

Examples:

    python scripts/research_data_intake/validate_research_config.py
    python scripts/research_data_intake/validate_research_config.py --runtime-root C:/dev/promat --language german --require-complete

Exit code 0 means every inspected file loads cleanly; 1 means at least one problem was found.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[1]
APP_SRC = REPO_ROOT / "app" / "src"
for entry in (str(APP_SRC), str(SCRIPT_ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

REQUIRED_CATALOG_TASKS = ("wordlist", "text")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runtime-root", help="Runtime root containing data/config (default: PROMAT_RUNTIME_ROOT or the repo root).")
    parser.add_argument(
        "--language",
        action="append",
        dest="languages",
        help="Corpus slug to validate (spanish, french, english, german). Repeatable. Default: every slug with a config directory.",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Treat a missing wordlist/text catalog or player_config.json as an error for each inspected language.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.runtime_root:
        os.environ["PROMAT_RUNTIME_ROOT"] = str(Path(args.runtime_root).expanduser().resolve())

    from app.config.data_conventions import LANGUAGE_SLUG_TO_TARGET_LANGUAGE
    from app.research_presets import (
        ResearchConfigError,
        clear_research_preset_caches,
        load_player_config,
        load_task_catalog,
    )
    from app.runtime_paths import get_config_root

    config_root = get_config_root() / "research_player"
    print(f"[config-root] {config_root.as_posix()}")
    clear_research_preset_caches()

    known_slugs = list(LANGUAGE_SLUG_TO_TARGET_LANGUAGE)
    if args.languages:
        unknown = [slug for slug in args.languages if slug not in known_slugs]
        if unknown:
            print(f"error: unknown language slug(s): {', '.join(unknown)}; expected one of {', '.join(known_slugs)}", file=sys.stderr)
            return 2
        languages = list(args.languages)
    else:
        languages = [slug for slug in known_slugs if (config_root / slug).is_dir()]

    if not languages:
        print("error: no research-player configuration found; nothing to validate", file=sys.stderr)
        return 1

    problems: list[str] = []
    for slug in languages:
        language_dir = config_root / slug
        if not language_dir.is_dir():
            problems.append(f"{slug}: missing configuration directory {language_dir.as_posix()}")
            continue
        for task in REQUIRED_CATALOG_TASKS:
            catalog_path = language_dir / "task_catalogs" / f"{task}.json"
            if not catalog_path.is_file():
                message = f"{slug}/{task}: catalog not present"
                if args.require_complete:
                    problems.append(message)
                else:
                    print(f"[skip] {message}")
                continue
            try:
                catalog = load_task_catalog(slug, task)
            except ResearchConfigError as exc:
                problems.append(f"{slug}/{task}: {exc}")
                continue
            print(f"[ok] {slug}/{task}: {len(catalog.items_by_id)} items, source_kind={catalog.player_source.source_kind}")
        player_config_path = language_dir / "player_config.json"
        if not player_config_path.is_file():
            message = f"{slug}: player_config.json not present"
            if args.require_complete:
                problems.append(message)
            else:
                print(f"[skip] {message}")
            continue
        try:
            load_player_config(slug)
        except ResearchConfigError as exc:
            problems.append(f"{slug}/player_config: {exc}")
        else:
            print(f"[ok] {slug}/player_config")

    if problems:
        print("[problems]")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("[result] research-player configuration is loadable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
