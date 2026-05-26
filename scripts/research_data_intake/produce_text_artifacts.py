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
from audio_conversion.ffmpeg_audio import (  # noqa: E402
    TARGET_BITRATE,
    TARGET_BITRATE_BPS,
    TARGET_CHANNELS,
    create_full_task_mp3,
    create_split_mp3,
    ensure_media_tools,
    probe_audio_profile,
    probe_duration_seconds,
)
from language_config import resolve_language_config  # noqa: E402


DEFAULT_LANGUAGE_SLUG = "spanish"
TASK_KEY = "text"
SPLIT_PADDING_SECONDS = 0.25


def _resolve_language_slug(value: str | None) -> str:
    return resolve_language_config(value or DEFAULT_LANGUAGE_SLUG).corpus_slug


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Produce text player artifacts from runtime sessions.")
    selection_group = parser.add_mutually_exclusive_group(required=True)
    selection_group.add_argument("--session-id", help="Process one concrete session_id.")
    selection_group.add_argument(
        "--all-suitable-sessions",
        action="store_true",
        help="Process all suitable sessions for the selected corpus language with non-empty source/text.wav and alignment/text.json.",
    )
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE_SLUG,
        help="Target intake language code or corpus slug for runtime session selection. Default: spanish.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and plan outputs without writing files.")
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


def _resolve_session_dir(args: argparse.Namespace, language_slug: str) -> tuple[list[Path], list[str]]:
    if args.session_id:
        session_dir = get_sessions_root() / language_slug / args.session_id
        if not session_dir.exists():
            raise FileNotFoundError(f"Unknown session_id: {args.session_id}")
        return [session_dir], []

    sessions_root = get_sessions_root() / language_slug
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
            skipped.append(f"{metadata_path.parent.name}: no documented text task")
            continue
        source_file = task_definition.get("source_file") or "source/text.wav"
        source_path = metadata_path.parent / str(source_file)
        alignment_json_path = metadata_path.parent / "alignment" / "text.json"
        if not source_path.exists() or source_path.stat().st_size == 0:
            skipped.append(f"{metadata_path.parent.name}: missing or empty {source_file}")
            continue
        if not alignment_json_path.exists() or alignment_json_path.stat().st_size == 0:
            skipped.append(f"{metadata_path.parent.name}: missing or empty alignment/text.json")
            continue
        targets.append(metadata_path.parent)
    return targets, skipped


def _cleanup_text_outputs(session_dir: Path) -> None:
    derived_mp3 = session_dir / "derived" / "text.mp3"
    alignment_json_path = session_dir / "alignment" / "text.json"
    items_dir = session_dir / "items" / "text"
    if derived_mp3.exists():
        derived_mp3.unlink()
    if alignment_json_path.exists():
        alignment_json_path.unlink()
    if items_dir.exists():
        for split_mp3 in items_dir.glob("*.mp3"):
            split_mp3.unlink()


def _load_alignment_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"alignment/text.json must contain an object: {path}")
    return payload


def _normalized_item_payloads(payload: dict[str, Any], session_id: str, person_id: str) -> list[dict[str, Any]]:
    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("alignment/text.json must contain a non-empty items list")

    items: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, dict):
            raise ValueError(f"text item {index} must be an object")
        item_id = raw_item.get("item_id")
        item_number = raw_item.get("item_number")
        text_value = raw_item.get("text")
        start_ms = raw_item.get("start_ms")
        end_ms = raw_item.get("end_ms")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError(f"text item {index} is missing item_id")
        if not isinstance(item_number, str) or not item_number.strip():
            raise ValueError(f"text item {index} is missing item_number")
        if not isinstance(text_value, str) or not text_value.strip():
            raise ValueError(f"text item {index} is missing text")
        if not isinstance(start_ms, int) or not isinstance(end_ms, int) or end_ms <= start_ms:
            raise ValueError(f"text item {item_id} has invalid timing")
        item_payload = dict(raw_item)
        item_payload["item_id"] = item_id
        item_payload["item_number"] = item_number
        item_payload["text"] = text_value
        item_payload["start_ms"] = start_ms
        item_payload["end_ms"] = end_ms
        item_payload["split_mp3"] = f"items/text/{item_id}.mp3"
        items.append(item_payload)

    payload["session_id"] = session_id
    payload["person_id"] = person_id
    payload["task"] = TASK_KEY
    payload["audio"] = {"full_mp3": "derived/text.mp3"}
    payload["items"] = items
    return items


def _normalized_omitted_item_payloads(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_items = payload.get("omitted_items")
    if raw_items is None:
        return []
    if not isinstance(raw_items, list):
        raise ValueError("alignment/text.json omitted_items must be a list when present")
    omitted_items: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, dict):
            raise ValueError(f"omitted text item {index} must be an object")
        item_id = raw_item.get("item_id")
        item_number = raw_item.get("item_number")
        text_value = raw_item.get("text")
        omit_reason = raw_item.get("omit_reason")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError(f"omitted text item {index} is missing item_id")
        if not isinstance(item_number, str) or not item_number.strip():
            raise ValueError(f"omitted text item {item_id} is missing item_number")
        if not isinstance(text_value, str) or not text_value.strip():
            raise ValueError(f"omitted text item {item_id} is missing text")
        if raw_item.get("omitted") is not True:
            raise ValueError(f"omitted text item {item_id} must set omitted=true")
        if not isinstance(omit_reason, str) or not omit_reason.strip():
            raise ValueError(f"omitted text item {item_id} is missing omit_reason")
        for forbidden_key in ("start_ms", "end_ms", "split_mp3"):
            if forbidden_key in raw_item:
                raise ValueError(f"omitted text item {item_id} must not include {forbidden_key}")
        omitted_items.append(
            {
                "item_id": item_id,
                "item_number": item_number,
                "text": text_value,
                "omitted": True,
                "omit_reason": omit_reason,
            }
        )
    payload["omitted_items"] = omitted_items
    return omitted_items


def _runtime_warnings(payload: dict[str, Any]) -> list[str]:
    raw_warnings = payload.get("_import_warnings")
    if not isinstance(raw_warnings, list):
        return []
    return [
        str(warning)
        for warning in raw_warnings
        if isinstance(warning, str) and not warning.startswith("session_id remains unresolved in the working tree")
    ]


def _split_item_boundaries(items: list[dict[str, Any]], duration_seconds: float) -> list[tuple[str, float, float]]:
    boundaries: list[tuple[str, float, float]] = []
    for item in items:
        start_seconds = max(0.0, (int(item["start_ms"]) / 1000.0) - SPLIT_PADDING_SECONDS)
        end_seconds = min(duration_seconds, (int(item["end_ms"]) / 1000.0) + SPLIT_PADDING_SECONDS)
        if end_seconds <= start_seconds:
            raise ValueError(f"Invalid split boundaries for {item['item_id']}")
        boundaries.append((str(item["item_id"]), start_seconds, end_seconds))
    return boundaries


def produce_text_artifacts(
    session_dir: Path,
    *,
    session_id: str,
    person_id: str,
    source_wav: Path,
    working_alignment_json: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    if not source_wav.exists() or source_wav.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty text source WAV for {session_id}: {source_wav}")
    if not working_alignment_json.exists() or working_alignment_json.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty working text alignment JSON for {session_id}: {working_alignment_json}")

    payload = _load_alignment_payload(working_alignment_json)
    items = _normalized_item_payloads(payload, session_id=session_id, person_id=person_id)
    omitted_items = _normalized_omitted_item_payloads(payload)
    warnings = _runtime_warnings(payload)
    if warnings:
        payload["_import_warnings"] = warnings
    else:
        payload.pop("_import_warnings", None)
    source_profile = probe_audio_profile(source_wav)
    source_duration = float(source_profile.get("duration") or 0.0)
    if source_duration <= 0:
        raise ValueError(f"Source audio has no readable duration for {session_id}: {source_wav}")

    if dry_run:
        return {
            "session_id": session_id,
            "person_id": person_id,
            "item_count": len(items),
            "omitted_item_count": len(omitted_items),
            "warnings": warnings,
            "source_profile": source_profile,
            "mode": "dry-run",
        }

    derived_mp3 = session_dir / "derived" / "text.mp3"
    alignment_json_path = session_dir / "alignment" / "text.json"
    items_dir = session_dir / "items" / "text"
    items_dir.mkdir(parents=True, exist_ok=True)
    for existing_split in items_dir.glob("*.mp3"):
        existing_split.unlink()

    create_full_task_mp3(source_wav, derived_mp3)
    derived_duration_seconds = probe_duration_seconds(derived_mp3)
    for item_id, start_seconds, end_seconds in _split_item_boundaries(items, derived_duration_seconds):
        create_split_mp3(derived_mp3, items_dir / f"{item_id}.mp3", start_seconds, end_seconds)

    alignment_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    derived_profile = probe_audio_profile(derived_mp3)
    if derived_profile.get("channels") != TARGET_CHANNELS:
        raise RuntimeError(f"Expected mono output for {session_id}")
    if derived_profile.get("bit_rate") != TARGET_BITRATE_BPS:
        raise RuntimeError(
            f"Expected {TARGET_BITRATE_BPS} bps output for {session_id}, got {derived_profile.get('bit_rate')}"
        )

    return {
        "session_id": session_id,
        "person_id": person_id,
        "item_count": len(items),
        "omitted_item_count": len(omitted_items),
        "warnings": warnings,
        "verification": {"derived_profile": derived_profile},
        "mode": "write",
    }


def _process_session(session_dir: Path, dry_run: bool) -> dict[str, Any]:
    metadata = _load_metadata(session_dir / "metadata.json")
    session_id = str(metadata.get("session_id") or session_dir.name)
    person_id = str(metadata.get("person_id") or "")
    task_definition = _task_definition(metadata)
    if task_definition is None:
        raise ValueError(f"No text task documented for {session_id}")
    source_wav = session_dir / str(task_definition.get("source_file") or "source/text.wav")
    alignment_json = session_dir / "alignment" / "text.json"
    return produce_text_artifacts(
        session_dir,
        session_id=session_id,
        person_id=person_id,
        source_wav=source_wav,
        working_alignment_json=alignment_json,
        dry_run=dry_run,
    )


def _print_header(title: str) -> None:
    print(f"\n[{title}]")


def main() -> int:
    args = parse_args()
    language_slug = _resolve_language_slug(args.language)
    ensure_media_tools()
    targets, skipped = _resolve_session_dir(args, language_slug)
    if not targets:
        raise RuntimeError(f"No suitable {language_slug} sessions found for text processing.")

    results: list[dict[str, Any]] = []
    for session_dir in targets:
        try:
            result = _process_session(session_dir=session_dir, dry_run=args.dry_run)
        except Exception as exc:
            if args.session_id:
                raise
            _cleanup_text_outputs(session_dir)
            skipped.append(f"{session_dir.name}: {exc}")
            continue
        results.append(result)

    _print_header("text-production-summary")
    print(f"language={language_slug}")
    print(f"mode={'dry-run' if args.dry_run else 'write'} target_bitrate={TARGET_BITRATE} mono={TARGET_CHANNELS} cbr=true")
    for result in results:
        print(f"processed {result['session_id']} ({result['person_id']}) items={result['item_count']}")
    for reason in skipped:
        print(f"skipped {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
