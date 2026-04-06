from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_SRC = REPO_ROOT / "app" / "src"
SCRIPT_ROOT = Path(__file__).resolve().parent
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app.runtime_paths import get_sessions_root  # noqa: E402
from alignment_export.wordlist_alignment import (  # noqa: E402
    EXPECTED_WORDLIST_COUNT,
    build_alignment_payload,
    build_timed_items,
    load_wordlist_catalog,
    parse_textgrid_intervals,
    write_alignment_json,
)
from audio_conversion.ffmpeg_audio import (  # noqa: E402
    TARGET_BITRATE,
    TARGET_BITRATE_BPS,
    TARGET_CHANNELS,
    create_full_wordlist_mp3,
    ensure_media_tools,
    probe_audio_profile,
    probe_duration_seconds,
)
from item_split.wordlist_splits import build_split_boundaries, create_wordlist_splits  # noqa: E402


LANGUAGE_SLUG = "spanish"
TASK_KEY = "wordlist"
CATALOG_PATH = REPO_ROOT / "data" / "config" / "research_player" / LANGUAGE_SLUG / "task_catalogs" / "wordlist.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Produce wordlist player artifacts from Spanish dev sessions.")
    selection_group = parser.add_mutually_exclusive_group(required=True)
    selection_group.add_argument("--session-id", help="Process one concrete session_id.")
    selection_group.add_argument(
        "--all-suitable-sessions",
        action="store_true",
        help="Process all current Spanish sessions with non-empty source/wordlist.wav and alignment/wordlist.TextGrid.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and plan outputs without writing files.")
    parser.add_argument(
        "--validate-labels",
        choices=("off", "warn", "fail"),
        default="off",
        help="Compare TextGrid labels against the task catalog without ever normalizing them.",
    )
    return parser.parse_args()


def _load_metadata(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"metadata.json must contain an object: {path}")
    return payload


def _task_definition(metadata: dict[str, Any]) -> dict[str, Any] | None:
    tasks = metadata.get("tasks")
    if not isinstance(tasks, list):
        return None
    for task in tasks:
        if isinstance(task, dict) and task.get("task_type") == TASK_KEY:
            return task
    return None


def _suitable_session_targets() -> tuple[list[Path], list[str]]:
    sessions_root = get_sessions_root() / LANGUAGE_SLUG
    targets: list[Path] = []
    skipped: list[str] = []
    for metadata_path in sorted(sessions_root.glob("*/metadata.json")):
        try:
            metadata = _load_metadata(metadata_path)
        except Exception as exc:
            skipped.append(f"{metadata_path.parent.name}: invalid metadata ({exc})")
            continue
        task_definition = _task_definition(metadata)
        if task_definition is None:
            skipped.append(f"{metadata_path.parent.name}: no documented wordlist task")
            continue
        source_file = task_definition.get("source_file") or "source/wordlist.wav"
        alignment_file = task_definition.get("alignment_file") or "alignment/wordlist.TextGrid"
        source_path = metadata_path.parent / str(source_file)
        alignment_path = metadata_path.parent / str(alignment_file)
        if not source_path.exists() or source_path.stat().st_size == 0:
            skipped.append(f"{metadata_path.parent.name}: missing or empty {source_file}")
            continue
        if not alignment_path.exists() or alignment_path.stat().st_size == 0:
            skipped.append(f"{metadata_path.parent.name}: missing or empty {alignment_file}")
            continue
        targets.append(metadata_path.parent)
    return targets, skipped


def _resolve_session_dir(args: argparse.Namespace) -> tuple[list[Path], list[str]]:
    if args.session_id:
        session_dir = get_sessions_root() / LANGUAGE_SLUG / args.session_id
        if not session_dir.exists():
            raise FileNotFoundError(f"Unknown session_id: {args.session_id}")
        return [session_dir], []
    return _suitable_session_targets()


def _update_metadata(session_dir: Path, payload: dict[str, Any], split_paths: list[str]) -> None:
    metadata_path = session_dir / "metadata.json"
    metadata = _load_metadata(metadata_path)
    tasks = metadata.get("tasks")
    if isinstance(tasks, list):
        for task in tasks:
            if isinstance(task, dict) and task.get("task_type") == TASK_KEY:
                task["derived_file"] = "derived/wordlist.mp3"

    files = metadata.get("files")
    retained_files: list[dict[str, Any]] = []
    if isinstance(files, list):
        for entry in files:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path")
            if not isinstance(path, str):
                retained_files.append(entry)
                continue
            if path == "derived/wordlist.mp3" or path == "alignment/wordlist.json" or path.startswith("items/wordlist/"):
                continue
            retained_files.append(entry)

    retained_files.append({"path": "alignment/wordlist.json", "file_role": "alignment_json", "format": "json", "status": "processed"})
    retained_files.append({"path": "derived/wordlist.mp3", "file_role": "audio_mp3", "format": "mp3", "status": "processed"})
    retained_files.extend(
        {"path": split_path, "file_role": "items_audio", "format": "mp3", "status": "processed"}
        for split_path in split_paths
    )

    metadata["files"] = retained_files
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _cleanup_wordlist_outputs(session_dir: Path) -> None:
    derived_mp3 = session_dir / "derived" / "wordlist.mp3"
    alignment_json_path = session_dir / "alignment" / "wordlist.json"
    items_dir = session_dir / "items" / "wordlist"

    if derived_mp3.exists():
        derived_mp3.unlink()
    if alignment_json_path.exists():
        alignment_json_path.unlink()
    if items_dir.exists():
        for split_mp3 in items_dir.glob("*.mp3"):
            split_mp3.unlink()


def _validate_generated_outputs(session_dir: Path, expected_ids: list[str]) -> dict[str, object]:
    derived_mp3 = session_dir / "derived" / "wordlist.mp3"
    alignment_json_path = session_dir / "alignment" / "wordlist.json"
    items_dir = session_dir / "items" / "wordlist"

    if not derived_mp3.exists() or derived_mp3.stat().st_size == 0:
        raise RuntimeError(f"Missing derived MP3: {derived_mp3}")
    if not alignment_json_path.exists() or alignment_json_path.stat().st_size == 0:
        raise RuntimeError(f"Missing alignment JSON: {alignment_json_path}")

    payload = json.loads(alignment_json_path.read_text(encoding="utf-8"))
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != EXPECTED_WORDLIST_COUNT:
        raise RuntimeError(f"alignment/wordlist.json must contain exactly {EXPECTED_WORDLIST_COUNT} items: {alignment_json_path}")

    observed_ids = [item.get("item_id") for item in items if isinstance(item, dict)]
    if observed_ids != expected_ids:
        raise RuntimeError(f"alignment/wordlist.json item_id sequence mismatch: {alignment_json_path}")

    item_paths = sorted(items_dir.glob("*.mp3"))
    if len(item_paths) != EXPECTED_WORDLIST_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_WORDLIST_COUNT} split MP3s in {items_dir}, found {len(item_paths)}")

    expected_split_paths = {f"items/wordlist/{item_id}.mp3" for item_id in expected_ids}
    payload_split_paths = {
        item.get("split_mp3")
        for item in items
        if isinstance(item, dict) and isinstance(item.get("split_mp3"), str)
    }
    if payload_split_paths != expected_split_paths:
        raise RuntimeError(f"Split path mismatch in alignment JSON for {session_dir.name}")

    for relative_path in expected_split_paths:
        if not (session_dir / relative_path).exists():
            raise RuntimeError(f"Missing split MP3 referenced by JSON: {relative_path}")

    derived_profile = probe_audio_profile(derived_mp3)
    sample_profiles = {"derived": derived_profile}
    for sample_name in (expected_ids[0], expected_ids[-1]):
        sample_profiles[sample_name] = probe_audio_profile(session_dir / f"items/wordlist/{sample_name}.mp3")

    for profile_name, profile in sample_profiles.items():
        if profile.get("channels") != TARGET_CHANNELS:
            raise RuntimeError(f"Expected mono output for {profile_name} in {session_dir.name}")
        if profile.get("bit_rate") != TARGET_BITRATE_BPS:
            raise RuntimeError(
                f"Expected {TARGET_BITRATE_BPS} bps output for {profile_name} in {session_dir.name}, got {profile.get('bit_rate')}"
            )

    return {
        "derived_profile": derived_profile,
        "sample_split_profiles": sample_profiles,
        "item_count": len(item_paths),
    }


def _print_header(title: str) -> None:
    print(f"\n[{title}]")


def _process_session(session_dir: Path, catalog_path: Path, dry_run: bool, validate_labels: str) -> dict[str, Any]:
    metadata = _load_metadata(session_dir / "metadata.json")
    session_id = str(metadata.get("session_id") or session_dir.name)
    person_id = str(metadata.get("person_id") or "")
    task_definition = _task_definition(metadata)
    if task_definition is None:
        raise ValueError(f"No wordlist task documented for {session_id}")

    source_wav = session_dir / str(task_definition.get("source_file") or "source/wordlist.wav")
    alignment_textgrid = session_dir / str(task_definition.get("alignment_file") or "alignment/wordlist.TextGrid")
    derived_mp3 = session_dir / "derived" / "wordlist.mp3"
    alignment_json_path = session_dir / "alignment" / "wordlist.json"

    if not source_wav.exists() or source_wav.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty wordlist source WAV for {session_id}: {source_wav}")
    if not alignment_textgrid.exists() or alignment_textgrid.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty wordlist TextGrid for {session_id}: {alignment_textgrid}")

    catalog_items = load_wordlist_catalog(catalog_path)
    intervals = parse_textgrid_intervals(alignment_textgrid)
    timed_items, label_warnings = build_timed_items(catalog_items, intervals, validate_labels)
    split_paths = [item.split_mp3 for item in timed_items]
    source_profile = probe_audio_profile(source_wav)
    source_duration = float(source_profile.get("duration") or 0.0)
    if source_duration <= 0:
        raise ValueError(f"Source audio has no readable duration for {session_id}: {source_wav}")
    last_item = timed_items[-1]
    if last_item.end_seconds > source_duration:
        raise ValueError(
            f"Canonical wordlist boundaries exceed source audio duration for {session_id}: "
            f"last_end={last_item.end_seconds:.4f}s duration={source_duration:.4f}s"
        )

    if dry_run:
        return {
            "session_id": session_id,
            "person_id": person_id,
            "warnings": label_warnings,
            "source_profile": source_profile,
            "item_count": len(timed_items),
            "mode": "dry-run",
        }

    create_full_wordlist_mp3(source_wav, derived_mp3)
    derived_duration_seconds = probe_duration_seconds(derived_mp3)
    split_boundaries = build_split_boundaries(session_dir, timed_items, derived_duration_seconds)
    create_wordlist_splits(derived_mp3, split_boundaries)
    alignment_payload = build_alignment_payload(session_id=session_id, person_id=person_id, items=timed_items)
    write_alignment_json(alignment_json_path, alignment_payload)
    _update_metadata(session_dir, alignment_payload, split_paths)
    verification = _validate_generated_outputs(session_dir, [item.item_id for item in timed_items])

    return {
        "session_id": session_id,
        "person_id": person_id,
        "warnings": label_warnings,
        "verification": verification,
        "item_count": len(timed_items),
        "mode": "write",
    }


def main() -> int:
    args = parse_args()
    ensure_media_tools()
    targets, skipped = _resolve_session_dir(args)
    if not targets:
        raise RuntimeError("No suitable Spanish sessions found for wordlist processing.")

    results: list[dict[str, Any]] = []
    for session_dir in targets:
        try:
            result = _process_session(
                session_dir=session_dir,
                catalog_path=CATALOG_PATH,
                dry_run=args.dry_run,
                validate_labels=args.validate_labels,
            )
        except Exception as exc:
            if args.session_id:
                raise
            _cleanup_wordlist_outputs(session_dir)
            skipped.append(f"{session_dir.name}: {exc}")
            continue
        results.append(result)

    _print_header("wordlist-production-summary")
    print(f"catalog={CATALOG_PATH}")
    print(f"mode={'dry-run' if args.dry_run else 'write'} validate_labels={args.validate_labels}")
    print(f"target_bitrate={TARGET_BITRATE} mono={TARGET_CHANNELS} cbr=true")
    for result in results:
        print(f"processed {result['session_id']} ({result['person_id']}) items={result['item_count']}")
        for warning in result.get("warnings", []):
            print(f"warning: {warning}")
        verification = result.get("verification")
        if isinstance(verification, dict):
            derived_profile = verification.get("derived_profile")
            if isinstance(derived_profile, dict):
                print(
                    "verified "
                    f"channels={derived_profile.get('channels')} bit_rate={derived_profile.get('bit_rate')} "
                    f"duration={derived_profile.get('duration')}"
                )
    for reason in skipped:
        print(f"skipped {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())