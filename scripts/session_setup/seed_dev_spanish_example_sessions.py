from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_SRC = REPO_ROOT / "app" / "src"
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))

os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app.config.data_conventions import CONTEXT_VALUES, SPEAKER_TYPES, STANDARD_VARIETIES  # noqa: E402
from app.runtime_paths import get_data_root, get_sessions_root  # noqa: E402


LANGUAGE_SLUG = "spanish"
TARGET_LANGUAGE = "es"
TASK_TYPE = "isolated_speech"
TASK_LABEL = "Isolierte Aussprache (Wortliste)"
SOURCE_AUDIO_NAME = "isolated_speech.wav"
ALIGNMENT_NAME = "isolated_speech.TextGrid"
MANIFEST_PATH = Path(__file__).with_name("dev_spanish_example_sessions.json")


def _load_manifest(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        entries = json.load(handle)
    if not isinstance(entries, list):
        raise ValueError("Manifest root must be a list.")
    if len(entries) != 11:
        raise ValueError("Manifest must define exactly 11 example sessions.")
    return entries


def _validate_entry(entry: dict[str, object]) -> None:
    speaker_type = entry.get("speaker_type")
    if speaker_type not in SPEAKER_TYPES:
        raise ValueError(f"Unsupported speaker_type: {speaker_type}")

    context = entry.get("context")
    if context not in CONTEXT_VALUES:
        raise ValueError(f"Unsupported context: {context}")

    if entry.get("recording_year") != 2026:
        raise ValueError(f"recording_year must be 2026: {entry.get('session_id')}")

    session_id = str(entry.get("session_id"))
    if not session_id.startswith("ES-"):
        raise ValueError(f"session_id must use ES prefix: {session_id}")

    if entry.get("speaker_type") == "native_speaker":
        standard_variety = entry.get("standard_variety")
        if standard_variety not in STANDARD_VARIETIES[TARGET_LANGUAGE]:
            raise ValueError(f"Unsupported standard_variety: {standard_variety}")
        if entry.get("level_code") is not None or entry.get("level_self") is not None:
            raise ValueError(f"native_speaker entries must not define levels: {session_id}")
    else:
        if not entry.get("level_code") or not entry.get("level_self"):
            raise ValueError(f"learner entries must define level_code and level_self: {session_id}")


def _build_metadata(entry: dict[str, object]) -> dict[str, object]:
    speaker_type = str(entry["speaker_type"])
    note_suffix = (
        " Processed example WAV stored as source audio; no raw master is currently available for this dev seed."
    )
    metadata: dict[str, object] = {
        "person_id": entry["person_id"],
        "session_id": entry["session_id"],
        "target_language": TARGET_LANGUAGE,
        "speaker_type": speaker_type,
        "l1": entry["l1"],
        "gender": entry["gender"],
        "birth_year": entry["birth_year"],
        "current_region": entry["current_region"],
        "childhood_region": entry["childhood_region"],
        "level_code": entry.get("level_code"),
        "level_self": entry.get("level_self"),
        "standard_variety": entry.get("standard_variety"),
        "recording_year": entry["recording_year"],
        "recording_date": entry["recording_date"],
        "context": entry["context"],
        "notes": f"{entry['notes']}{note_suffix}",
        "tasks": [
            {
                "task_type": TASK_TYPE,
                "label": TASK_LABEL,
                "source_file": f"source/{SOURCE_AUDIO_NAME}",
                "alignment_file": f"alignment/{ALIGNMENT_NAME}",
            }
        ],
        "files": [
            {
                "path": "metadata.json",
                "file_role": "metadata",
                "format": "json",
            },
            {
                "path": f"source/{SOURCE_AUDIO_NAME}",
                "file_role": "audio_source",
                "format": "wav",
            },
            {
                "path": f"alignment/{ALIGNMENT_NAME}",
                "file_role": "textgrid",
                "format": "textgrid",
            },
        ],
    }
    if speaker_type != "native_speaker":
        metadata["standard_variety"] = None
    return metadata


def _remove_misplaced_raw_file(session_dir: Path, dry_run: bool) -> None:
    misplaced_raw = session_dir / "raw" / SOURCE_AUDIO_NAME
    if misplaced_raw.exists() and not dry_run:
        misplaced_raw.unlink()


def _copy_fixture(source_dir: Path, session_dir: Path, fixture_name: str, dry_run: bool) -> None:
    source_audio = source_dir / f"{fixture_name}.wav"
    source_alignment = source_dir / f"{fixture_name}.TextGrid"
    if not source_audio.exists():
        raise FileNotFoundError(f"Missing source audio fixture: {source_audio}")
    if not source_alignment.exists():
        raise FileNotFoundError(f"Missing source alignment fixture: {source_alignment}")

    source_dir_target = session_dir / "source"
    alignment_dir = session_dir / "alignment"
    if not dry_run:
        shutil.copy2(source_audio, source_dir_target / SOURCE_AUDIO_NAME)
        shutil.copy2(source_alignment, alignment_dir / ALIGNMENT_NAME)


def seed_sessions(manifest_path: Path, dry_run: bool) -> list[tuple[str, str, str]]:
    entries = _load_manifest(manifest_path)
    for entry in entries:
        _validate_entry(entry)

    data_root = get_data_root()
    example_data_root = data_root / "example_data"
    sessions_root = get_sessions_root() / LANGUAGE_SLUG
    mappings: list[tuple[str, str, str]] = []

    for entry in entries:
        fixture_name = str(entry["source_fixture"])
        person_id = str(entry["person_id"])
        session_id = str(entry["session_id"])
        session_dir = sessions_root / session_id
        metadata = _build_metadata(entry)
        mappings.append((fixture_name, person_id, session_id))

        if not dry_run:
            for folder_name in ("raw", "source", "alignment", "derived", "items"):
                (session_dir / folder_name).mkdir(parents=True, exist_ok=True)

        _copy_fixture(example_data_root, session_dir, fixture_name, dry_run=dry_run)
        _remove_misplaced_raw_file(session_dir, dry_run=dry_run)

        if not dry_run:
            metadata_path = session_dir / "metadata.json"
            metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    return mappings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed the local PROMAT Spanish dev example dataset from data/example_data."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_PATH,
        help="Path to the dev example session manifest JSON.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the manifest and fixture mapping without writing files.",
    )
    args = parser.parse_args()

    mappings = seed_sessions(args.manifest.resolve(), dry_run=args.dry_run)
    action = "Validated" if args.dry_run else "Seeded"
    print(f"{action} {len(mappings)} Spanish dev example sessions.")
    for fixture_name, person_id, session_id in mappings:
        print(f"- {fixture_name} -> {person_id} / {session_id}")
    print("Note: the tracked placeholder session ES-L-DE-B2-24-001 is left untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())