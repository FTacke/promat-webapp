from __future__ import annotations

import argparse
from datetime import date
import json
import os
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
APP_SRC = REPO_ROOT / "app" / "src"
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))

os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app.config.data_conventions import (  # noqa: E402
    CONTEXT_VALUES,
    SPEAKER_TYPES,
    STANDARD_VARIETIES,
    parse_person_id,
    parse_session_id,
)
from app.runtime_paths import get_data_root, get_sessions_root  # noqa: E402


LANGUAGE_SLUG = "spanish"
TARGET_LANGUAGE = "es"
TASK_DEFINITIONS = {
    "learner": (
        {
            "task_type": "wordlist",
            "label": "Wortliste",
            "source_audio_name": "wordlist.wav",
            "alignment_name": "wordlist.TextGrid",
        },
        {
            "task_type": "text",
            "label": "Text",
            "source_audio_name": "text.wav",
            "alignment_name": "text.TextGrid",
        },
        {
            "task_type": "interview",
            "label": "Interview zur Aussprache",
            "source_audio_name": "interview.wav",
            "alignment_name": "interview.TextGrid",
        },
    ),
    "native_speaker": (
        {
            "task_type": "wordlist",
            "label": "Wortliste",
            "source_audio_name": "wordlist.wav",
            "alignment_name": "wordlist.TextGrid",
        },
        {
            "task_type": "text",
            "label": "Text",
            "source_audio_name": "text.wav",
            "alignment_name": "text.TextGrid",
        },
    ),
}
MANIFEST_PATH = Path(__file__).with_name("dev_spanish_example_sessions.json")
PLACEHOLDER_SESSION_ID = "ES-L-0901-2024-S01"

PERSON_STABLE_FIELDS: dict[str, tuple[str, ...]] = {
    "learner": (
        "speaker_type",
        "l1",
        "mother_l1",
        "father_l1",
        "additional_languages",
        "gender",
        "birth_year",
        "current_region",
        "childhood_region",
    ),
    "native_speaker": (
        "speaker_type",
        "gender",
        "birth_year",
        "origin_region",
        "origin_country",
        "standard_variety",
    ),
}


def _load_manifest(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        entries = json.load(handle)
    if not isinstance(entries, list):
        raise ValueError("Manifest root must be a list.")
    if len(entries) != 11:
        raise ValueError("Manifest must define exactly 11 example sessions.")
    return entries


def _normalize_field_value(value: object) -> object:
    if isinstance(value, list):
        return tuple(value)
    return value


def _validate_recording_date(recording_date: object, recording_year: int, session_id: str) -> None:
    if not isinstance(recording_date, str) or not recording_date.strip():
        raise ValueError(f"recording_date must be a non-empty ISO date string: {session_id}")
    try:
        resolved = date.fromisoformat(recording_date)
    except ValueError as exc:
        raise ValueError(f"recording_date must be ISO formatted: {session_id}") from exc
    if resolved.year != recording_year:
        raise ValueError(f"recording_date year must match recording_year: {session_id}")


def _validate_entry(entry: dict[str, object]) -> None:
    person_id = str(entry.get("person_id") or "")
    session_id = str(entry.get("session_id") or "")
    speaker_type = entry.get("speaker_type")
    if speaker_type not in SPEAKER_TYPES:
        raise ValueError(f"Unsupported speaker_type: {speaker_type}")

    person_id_parts = parse_person_id(person_id)
    if person_id_parts is None:
        raise ValueError(f"person_id must use canonical format: {person_id}")

    session_id_parts = parse_session_id(session_id)
    if session_id_parts is None:
        raise ValueError(f"session_id must use canonical format: {session_id}")
    if session_id_parts.person_id != person_id:
        raise ValueError(f"session_id must embed person_id: {session_id}")
    if person_id_parts.corpus_code != "ES":
        raise ValueError(f"person_id must use ES corpus code for Spanish seeds: {person_id}")
    if person_id_parts.speaker_type != speaker_type:
        raise ValueError(f"person_id marker does not match speaker_type: {person_id}")

    context = entry.get("context")
    if context not in CONTEXT_VALUES:
        raise ValueError(f"Unsupported context: {context}")

    recorded_by = entry.get("recorded_by")
    if not isinstance(recorded_by, str) or not recorded_by.strip():
        raise ValueError(f"recorded_by must be a non-empty string: {session_id}")

    recording_year = entry.get("recording_year")
    if not isinstance(recording_year, int):
        raise ValueError(f"recording_year must be an integer: {session_id}")
    if session_id_parts.recording_year != recording_year:
        raise ValueError(f"session_id recording year must match recording_year: {session_id}")
    _validate_recording_date(entry.get("recording_date"), recording_year, session_id)

    source_fixture = entry.get("source_fixture")
    if not isinstance(source_fixture, str) or not source_fixture.strip():
        raise ValueError(f"source_fixture must be a non-empty string: {session_id}")

    notes = entry.get("notes")
    if not isinstance(notes, str) or not notes.strip():
        raise ValueError(f"notes must be a non-empty string: {session_id}")

    if entry.get("speaker_type") == "native_speaker":
        standard_variety = entry.get("standard_variety")
        if standard_variety not in STANDARD_VARIETIES[TARGET_LANGUAGE]:
            raise ValueError(f"Unsupported standard_variety: {standard_variety}")
        if not entry.get("origin_country") or not entry.get("origin_region"):
            raise ValueError(f"native_speaker entries must define origin_country and origin_region: {session_id}")
        if entry.get("level_code") is not None or entry.get("level_self") is not None:
            raise ValueError(f"native_speaker entries must not define levels: {session_id}")
    else:
        l1 = entry.get("l1")
        mother_l1 = entry.get("mother_l1")
        father_l1 = entry.get("father_l1")
        additional_languages = entry.get("additional_languages")
        if not isinstance(l1, str) or not l1.strip():
            raise ValueError(f"learner entries must define l1: {session_id}")
        if not isinstance(mother_l1, str) or not mother_l1.strip():
            raise ValueError(f"mother_l1 must be a non-empty string: {session_id}")
        if not isinstance(father_l1, str) or not father_l1.strip():
            raise ValueError(f"father_l1 must be a non-empty string: {session_id}")
        if not isinstance(additional_languages, list) or not all(isinstance(item, str) and item.strip() for item in additional_languages):
            raise ValueError(f"additional_languages must be a list of non-empty strings: {session_id}")
        if not entry.get("level_code") or not entry.get("level_self"):
            raise ValueError(f"learner entries must define level_code and level_self: {session_id}")
        if not entry.get("current_region") or not entry.get("childhood_region"):
            raise ValueError(f"learner entries must define current_region and childhood_region: {session_id}")
        if entry.get("stays_in_target_country") not in (True, False, None):
            raise ValueError(f"learner entries must define stays_in_target_country as true, false, or null: {session_id}")
        exposure_entries = entry.get("exposure_entries")
        if not isinstance(exposure_entries, list):
            raise ValueError(f"learner entries must define exposure_entries as a list: {session_id}")
        for exposure_entry in exposure_entries:
            if not isinstance(exposure_entry, dict):
                raise ValueError(f"exposure_entries items must be objects: {session_id}")
            duration_months = exposure_entry.get("duration_months")
            if duration_months is not None and not isinstance(duration_months, int):
                raise ValueError(f"duration_months must be an integer or null: {session_id}")


def _validate_manifest(entries: list[dict[str, object]]) -> None:
    seen_session_ids: set[str] = set()
    grouped_entries: dict[str, list[dict[str, object]]] = {}

    for entry in entries:
        _validate_entry(entry)
        session_id = str(entry["session_id"])
        if session_id in seen_session_ids:
            raise ValueError(f"Duplicate session_id in manifest: {session_id}")
        seen_session_ids.add(session_id)
        grouped_entries.setdefault(str(entry["person_id"]), []).append(entry)

    for person_id, person_entries in grouped_entries.items():
        speaker_type = str(person_entries[0]["speaker_type"])
        session_numbers: set[int] = set()
        stable_fields = PERSON_STABLE_FIELDS.get(speaker_type, ("speaker_type", "gender", "birth_year"))

        if speaker_type == "native_speaker" and len(person_entries) != 1:
            raise ValueError(f"native_speaker person_id must map to exactly one session in manifest: {person_id}")

        baseline_entry = person_entries[0]
        for entry in person_entries:
            session_id_parts = parse_session_id(str(entry["session_id"]))
            if session_id_parts is None:
                raise ValueError(f"Invalid session_id in manifest: {entry['session_id']}")
            if session_id_parts.session_number in session_numbers:
                raise ValueError(f"Duplicate session number for person_id in manifest: {entry['session_id']}")
            session_numbers.add(session_id_parts.session_number)

            for field_name in stable_fields:
                if _normalize_field_value(entry.get(field_name)) != _normalize_field_value(baseline_entry.get(field_name)):
                    raise ValueError(
                        f"Stable person field '{field_name}' differs across sessions for {person_id}: {entry['session_id']}"
                    )


def _build_metadata(entry: dict[str, object]) -> dict[str, object]:
    speaker_type = str(entry["speaker_type"])
    task_definitions = TASK_DEFINITIONS[speaker_type]
    note_suffix = (
        " Processed example WAV stored as source audio; no raw master is currently available for this dev seed."
    )
    metadata: dict[str, object] = {
        "person_id": entry["person_id"],
        "session_id": entry["session_id"],
        "target_language": TARGET_LANGUAGE,
        "speaker_type": speaker_type,
        "gender": entry["gender"],
        "birth_year": entry["birth_year"],
        "recording_year": entry["recording_year"],
        "recording_date": entry["recording_date"],
        "context": entry["context"],
        "recorded_by": entry["recorded_by"],
        "notes": f"{entry['notes']}{note_suffix}",
        "tasks": [
            {
                "task_type": task_definition["task_type"],
                "label": task_definition["label"],
                "source_file": f"source/{task_definition['source_audio_name']}",
                "alignment_file": f"alignment/{task_definition['alignment_name']}",
            }
            for task_definition in task_definitions
        ],
        "files": [
            {
                "path": "metadata.json",
                "file_role": "metadata",
                "format": "json",
            },
            *[
                {
                    "path": f"source/{task_definition['source_audio_name']}",
                    "file_role": "audio_source",
                    "format": "wav",
                }
                for task_definition in task_definitions
            ],
            *[
                {
                    "path": f"alignment/{task_definition['alignment_name']}",
                    "file_role": "textgrid",
                    "format": "textgrid",
                }
                for task_definition in task_definitions
            ],
        ],
    }

    if speaker_type == "native_speaker":
        metadata["standard_variety"] = entry.get("standard_variety")
        metadata["origin_country"] = entry.get("origin_country")
        metadata["origin_region"] = entry.get("origin_region")
        metadata["level_code"] = None
        metadata["level_self"] = None
    else:
        metadata["l1"] = entry["l1"]
        metadata["mother_l1"] = entry["mother_l1"]
        metadata["father_l1"] = entry["father_l1"]
        metadata["additional_languages"] = entry["additional_languages"]
        metadata["current_region"] = entry["current_region"]
        metadata["childhood_region"] = entry["childhood_region"]
        metadata["level_code"] = entry.get("level_code")
        metadata["level_self"] = entry.get("level_self")
        metadata["stays_in_target_country"] = entry.get("stays_in_target_country")
        metadata["exposure_entries"] = entry.get("exposure_entries")
        metadata["standard_variety"] = None

    return metadata


def _cleanup_stale_seed_session_dirs(sessions_root: Path, active_session_ids: set[str], dry_run: bool) -> None:
    if not sessions_root.exists():
        return

    for metadata_path in sessions_root.glob("*/metadata.json"):
        try:
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        notes = payload.get("notes")
        if not isinstance(notes, str):
            continue
        if "Fully fictional local dev seed mapped from data/example_data/test_person_" not in notes:
            continue
        session_dir = metadata_path.parent
        if session_dir.name in active_session_ids:
            continue
        if not dry_run:
            shutil.rmtree(session_dir)


def _remove_misplaced_raw_files(session_dir: Path, speaker_type: str, dry_run: bool) -> None:
    for task_definition in TASK_DEFINITIONS[speaker_type]:
        misplaced_raw = session_dir / "raw" / str(task_definition["source_audio_name"])
        if misplaced_raw.exists() and not dry_run:
            misplaced_raw.unlink()


def _copy_fixtures(source_dir: Path, session_dir: Path, fixture_name: str, speaker_type: str, dry_run: bool) -> None:
    source_audio = source_dir / f"{fixture_name}.wav"
    source_alignment = source_dir / f"{fixture_name}.TextGrid"
    if not source_audio.exists():
        raise FileNotFoundError(f"Missing source audio fixture: {source_audio}")
    if not source_alignment.exists():
        raise FileNotFoundError(f"Missing source alignment fixture: {source_alignment}")

    source_dir_target = session_dir / "source"
    alignment_dir = session_dir / "alignment"
    for task_definition in TASK_DEFINITIONS[speaker_type]:
        if not dry_run:
            shutil.copy2(source_audio, source_dir_target / str(task_definition["source_audio_name"]))
            shutil.copy2(source_alignment, alignment_dir / str(task_definition["alignment_name"]))


def seed_sessions(manifest_path: Path, dry_run: bool) -> list[tuple[str, str, str]]:
    entries = _load_manifest(manifest_path)
    _validate_manifest(entries)

    data_root = get_data_root()
    example_data_root = data_root / "example_data"
    sessions_root = get_sessions_root() / LANGUAGE_SLUG
    mappings: list[tuple[str, str, str]] = []
    active_session_ids = {str(entry["session_id"]) for entry in entries}

    _cleanup_stale_seed_session_dirs(sessions_root, active_session_ids, dry_run=dry_run)

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

        _copy_fixtures(example_data_root, session_dir, fixture_name, str(entry["speaker_type"]), dry_run=dry_run)
        _remove_misplaced_raw_files(session_dir, str(entry["speaker_type"]), dry_run=dry_run)

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
    print(f"Note: the tracked placeholder session {PLACEHOLDER_SESSION_ID} is left untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())