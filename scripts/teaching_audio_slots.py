"""Curated corpus recordings of the Spanish Teaching topic pages: export from the local runtime and consistency check.

The recordings used on the Teaching topic pages are declared in one place, ``content/teaching/spanish/audio-slots.yaml``:
per comparison (topic page, phenomenon, item, target word sequence, listening question) the recordings with their
speaker category, session, corpus item and the media file under the topic's ``media/audio/corpus/``. The topic YAML only
names those media files, so a recording is replaced by changing the session or item of one entry here and running

    python scripts/teaching_audio_slots.py --export

(texts and layout stay untouched). ``--check`` needs no corpus data: it verifies the declaration against the committed
media (files present, SHA-256, every file referenced by the topic sources, listening questions quoted on the page) and,
when a local runtime is available, the release conditions of every source session.

Release conditions (``docs/spec/intake-workbook.md``: ``teaching_consent_signed`` is an eligibility flag for manual
selection, never an automatic switch): the session must carry ``teaching_consent_signed: yes`` and ``needs_review:
false``, a reference recording must come from a native speaker and a learner recording from a learner session. Source:
final item MP3s of ``data/sessions/{corpus}/{session_id}/items/{task}/{item_id}.mp3``; nothing else is read or copied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "content" / "teaching"
DEFAULT_SESSIONS_ROOT = REPO_ROOT / "data" / "sessions"
SLOTS_FILE = CONTENT_ROOT / "spanish" / "audio-slots.yaml"
CORPUS = "spanish"
CATEGORIES = ("reference", "learner")
SESSION_PREFIX = {"reference": "ES-N-", "learner": "ES-L-"}
SPEAKER_TYPE = {"reference": "native_speaker", "learner": "learner"}
ITEM_ID = {"wordlist": re.compile(r"^wl_\d{3}$"), "text": re.compile(r"^(d|qy|qw)_\d{2}$")}
HEADER = """# Curated corpus recordings of the Spanish Teaching topic pages (declaration; see scripts/teaching_audio_slots.py).
#
# Edit a recording (session / item) here, then run `python scripts/teaching_audio_slots.py --export` and commit the changed
# media file and its `sha256`. The topic pages name only the media file, never a session, so replacing a recording
# needs no change to the page texts. All recordings come from sessions with `teaching_consent_signed: yes`; the
# `selection` of the first release was made automatically (typical duration, no outliers) and is NOT phonetically
# verified: it is a neutral comparison, not a claim about a specific learner realisation.
"""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_available(sessions_root: Path) -> bool:
    """True when ``sessions_root`` holds Spanish corpus sessions (the folder alone may exist as an empty placeholder)."""
    return any((sessions_root / CORPUS).glob("ES-*/metadata.json"))


def load_slots(path: Path = SLOTS_FILE) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def dump_slots(data: dict[str, Any], path: Path = SLOTS_FILE) -> None:
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120)
    path.write_text(HEADER + "\n" + body, encoding="utf-8", newline="\n")


def media_path(topic: str, file: str) -> Path:
    return CONTENT_ROOT / CORPUS / topic / "media" / "audio" / file


def source_path(sessions_root: Path, recording: dict[str, Any]) -> Path:
    item = recording["item"]
    return sessions_root / CORPUS / recording["session_id"] / "items" / item["task"] / f"{item['id']}.mp3"


def iter_recordings(data: dict[str, Any]):
    for comparison in data.get("comparisons") or []:
        for recording in comparison.get("recordings") or []:
            yield comparison, recording


def session_problems(sessions_root: Path, recording: dict[str, Any]) -> list[str]:
    """Release conditions of the source session of one recording."""
    session_id = recording["session_id"]
    metadata_file = sessions_root / CORPUS / session_id / "metadata.json"
    if not metadata_file.is_file():
        return [f"{session_id}: metadata.json missing in {sessions_root / CORPUS}"]
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    problems = []
    if metadata.get("teaching_consent_signed") != "yes":
        problems.append(f"{session_id}: teaching_consent_signed is {metadata.get('teaching_consent_signed')!r}, not 'yes'")
    if metadata.get("needs_review"):
        problems.append(f"{session_id}: needs_review is set")
    if metadata.get("speaker_type") != SPEAKER_TYPE[recording["category"]]:
        problems.append(f"{session_id}: speaker_type {metadata.get('speaker_type')!r} does not match category {recording['category']!r}")
    return problems


def check(data: dict[str, Any], sessions_root: Path | None = None) -> list[str]:
    """Consistency problems of the declaration; the session conditions are checked when ``sessions_root`` is given."""
    problems: list[str] = []
    seen_files: set[tuple[str, str]] = set()
    sources: dict[str, str] = {}
    for comparison, recording in iter_recordings(data):
        where = f"{comparison.get('id')}/{recording.get('slot')}"
        topic = comparison["topic"]
        if topic not in sources:
            sources[topic] = "\n".join(
                path.read_text(encoding="utf-8") for path in sorted((CONTENT_ROOT / CORPUS / topic).glob("*.yaml"))
            )
        category = recording.get("category")
        item = recording.get("item") or {}
        if category not in CATEGORIES:
            problems.append(f"{where}: category must be one of {CATEGORIES}")
            continue
        if not str(recording.get("session_id", "")).startswith(SESSION_PREFIX[category]):
            problems.append(f"{where}: session {recording.get('session_id')!r} does not fit category {category!r}")
        pattern = ITEM_ID.get(item.get("task", ""))
        if pattern is None or not pattern.match(str(item.get("id", ""))):
            problems.append(f"{where}: invalid corpus item {item!r}")
        key = (topic, recording["file"])
        if key in seen_files:
            problems.append(f"{where}: media file {recording['file']} declared twice")
        seen_files.add(key)
        target = media_path(topic, recording["file"])
        if not target.is_file():
            problems.append(f"{where}: media file missing: {target.relative_to(REPO_ROOT)}")
        elif recording.get("sha256") != sha256_of(target):
            problems.append(f"{where}: sha256 differs from {target.relative_to(REPO_ROOT)} (run --export or update the entry)")
        if recording["file"] not in sources[topic]:
            problems.append(f"{where}: {recording['file']} is not referenced by the topic sources of {topic}")
        if sessions_root is not None:
            problems.extend(f"{where}: {problem}" for problem in session_problems(sessions_root, recording))
            origin = source_path(sessions_root, recording)
            if not origin.is_file():
                problems.append(f"{where}: source recording missing: {origin}")
            elif target.is_file() and sha256_of(origin) != sha256_of(target):
                problems.append(f"{where}: media file differs from its source recording (re-export to refresh)")
    for comparison in data.get("comparisons") or []:
        question = str(comparison.get("question") or "")
        if question and question not in sources.get(comparison["topic"], ""):
            problems.append(f"{comparison.get('id')}: listening question is not quoted in the topic source: {question!r}")
    return problems


def export(data: dict[str, Any], sessions_root: Path) -> list[str]:
    """Copy the declared recordings from the local runtime into the topic media and refresh their hashes."""
    problems: list[str] = []
    for comparison, recording in iter_recordings(data):
        where = f"{comparison['id']}/{recording['slot']}"
        problems.extend(f"{where}: {problem}" for problem in session_problems(sessions_root, recording))
        origin = source_path(sessions_root, recording)
        if not origin.is_file():
            problems.append(f"{where}: source recording missing: {origin}")
    if problems:
        return problems
    for _comparison, recording in iter_recordings(data):
        target = media_path(_comparison["topic"], recording["file"])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path(sessions_root, recording), target)
        recording["sha256"] = sha256_of(target)
    dump_slots(data)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--export", action="store_true", help="copy the declared recordings from the local runtime")
    parser.add_argument("--check", action="store_true", help="verify the declaration (default)")
    parser.add_argument("--sessions-root", type=Path, default=DEFAULT_SESSIONS_ROOT, help="runtime sessions root (default: data/sessions)")
    args = parser.parse_args()
    data = load_slots()
    sessions_root = args.sessions_root if runtime_available(args.sessions_root) else None
    if args.export:
        if sessions_root is None:
            print(f"No runtime sessions under {args.sessions_root}", file=sys.stderr)
            return 1
        problems = export(data, sessions_root)
        print("exported" if not problems else "export refused")
    else:
        problems = check(data, sessions_root)
        print("slots OK" if not problems else "slots FAILED")
    for problem in problems:
        print(" -", problem)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
