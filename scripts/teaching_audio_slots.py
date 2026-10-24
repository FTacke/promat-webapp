"""Curated corpus recordings of the Spanish Teaching topic pages: export from the local runtime and consistency check.

The recordings used on the Teaching topic pages are declared in one place, ``content/teaching/spanish/audio-slots.yaml``:
per comparison (topic page, phenomenon, item, target word sequence, listening question) the recordings with their
speaker category, session, corpus item and the media file under the topic's ``media/audio/corpus/``. The topic YAML only
names those media files, so a recording is replaced by changing the session or item of one entry here and running

    python scripts/teaching_audio_slots.py --export

(texts and layout stay untouched). ``--check`` needs no corpus data: it verifies the declaration against the committed
media (files present, SHA-256, every file referenced by the topic sources, listening questions quoted on the page) and,
when a local runtime is available, the release conditions of every source session.

Release gate (``docs/spec/intake-workbook.md``: ``teaching_consent_signed`` is an eligibility flag for manual selection,
never an automatic switch; research access never replaces it): before anything is exported or accepted, every source
session must carry ``teaching_consent_signed: yes`` and ``needs_review: false``, a reference recording must come from a
native speaker and a learner recording from a learner session, the item must exist in the session's alignment (and contain
the comparison's ``target_tokens`` in sequence), and no session of ``EXCLUDED_SESSIONS`` may be used. ``--release-report``
prints this check as a table (session, item, consent, review flag, speaker type, item text, result).

Source: final item MP3s of ``data/sessions/{corpus}/{session_id}/items/{task}/{item_id}.mp3``; nothing else is read.

A recording is exported either unchanged (copy) or, when it carries a ``crop`` entry, as a **cut-out** of the item MP3: the
corpus recording stays untouched, a derivative with the target word sequence is rendered with ffmpeg from the stored cut
points (``start_ms``/``end_ms`` on the item MP3 timeline, chosen by looking at spectrogram and energy envelope of the actual
realisation, not at the forced-alignment word times), short edge fades and an optional ``lead_silence_ms`` before the first
sound; nothing is inserted between the words and speed and signal are unchanged. ``source_sha256`` ties the derivative to the
exact source file, ``sha256`` to the committed media. Needs ``ffmpeg`` on the PATH for ``--export`` of cropped entries only.

A recording may also be a **montage** of several single-word items of one session: instead of ``item``/``crop`` it carries ``parts``
(each with its own ``item``, ``crop`` cut points, optional ``target_tokens`` and ``source_sha256``) and ``join`` (``pause_ms`` of silence
between the parts). The derivative is rendered with the same ffmpeg chain per part, parts in the declared order, nothing else inserted
(used for the two-word cards of the vowel page); it is not an utterance of the speaker and the page must say so.
A montage of the predecessor corpus MAR.ELE carries ``origin`` (corpus) and ``parts`` with ``source_file`` (relative to the MAR.ELE
webapp backup, ``items/inf-NNN_NNN_word.mp3``) instead of ``item``: ``--export --marele-root PATH`` (or ``PROMAT_MARELE_ROOT``) renders it
from that backup and refreshes the source hashes; without the backup it is only verified (file, hash, page reference).

Recordings from the predecessor corpus MAR.ELE are not part of the research runtime: they carry an ``origin`` entry
(corpus, source file, transcription) instead of ``session_id`` and ``item``, are copied once into the topic
media by hand (the source repository stays untouched) and are only verified here (file present, SHA-256, referenced).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any
import unicodedata

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
# Sessions that must never be used on a Teaching page, with the reason. A session leaves this list only by a
# deliberate edit after a new, verifiable Teaching consent (the metadata flag alone is not enough).
EXCLUDED_SESSIONS = {
    "ES-L-0014-2026-S01": "teaching_consent_signed: no (no new Teaching release documented)",
    "ES-N-0003-2026-S01": "teaching_consent_signed: no",
    "ES-L-0023-2026-S01": "first language Portuguese (not a German-L1 learner comparison)",
}
CROP_KEYS = ("start_ms", "end_ms")
FFMPEG_AUDIO = ["-c:a", "libmp3lame", "-b:a", "160k", "-ar", "48000", "-ac", "1"]
HEADER = """# Curated corpus recordings of the Spanish Teaching topic pages (declaration; see scripts/teaching_audio_slots.py).
#
# Edit a recording (session / item) here, then run `python scripts/teaching_audio_slots.py --export` and commit the changed
# media file and its `sha256`. The topic pages name only the media file, never a session, so replacing a recording
# needs no change to the page texts. All recordings come from sessions with `teaching_consent_signed: yes` (checked by
# `--release-report`). The `selection` of the first release was made automatically; the combinations of
# `soft-spanish-hard-german` were chosen in a manual phonetic curation (Ana Goás Pérez); the `r` page was curated by acoustic screening
# (intensity contour and spectrogram of the r realisations) and is provisional until listened to. Recordings with an `origin`
# entry come from the predecessor corpus MAR.ELE (not from the research runtime); they are not touched by --export.
# A `crop` entry renders the target word sequence out of the item MP3 (cut points fixed here, see the script docstring).
# `reserves` document curatorial alternatives that are NOT integrated (no media, no audio box).
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


def recording_parts(recording: dict[str, Any]) -> list[dict[str, Any]]:
    """The source parts of a recording: the ``parts`` of a montage, otherwise one part made of ``item``/``crop``/``source_sha256``."""
    if recording.get("parts"):
        return list(recording["parts"])
    return [{"item": recording.get("item") or {}, "crop": recording.get("crop"), "source_sha256": recording.get("source_sha256"), "target_tokens": recording.get("target_tokens")}]


def is_montage(recording: dict[str, Any]) -> bool:
    return bool(recording.get("parts"))


def external_montage_problems(recording: dict[str, Any]) -> list[str]:
    """Declaration rules of a montage made from MAR.ELE items (no session, no corpus item)."""
    problems = []
    if not str((recording.get("origin") or {}).get("corpus") or "").strip():
        problems.append("external montage needs origin.corpus")
    join = recording.get("join") or {}
    if len(recording.get("parts") or []) < 2 or not isinstance(join.get("pause_ms"), int) or join["pause_ms"] < 0 or recording.get("session_id") or recording.get("item"):
        problems.append("a montage needs at least two parts, join.pause_ms and no session/item of its own")
    for part in recording.get("parts") or []:
        crop = part.get("crop") or {}
        if not str(part.get("source_file") or "").strip():
            problems.append("every part of an external montage needs a source_file")
        if not all(isinstance(crop.get(key), int) for key in CROP_KEYS) or crop.get("end_ms", 0) <= crop.get("start_ms", 0):
            problems.append("every part of a montage needs a crop with integer start_ms < end_ms")
        if not re.fullmatch(r"[0-9a-f]{64}", str(part.get("source_sha256") or "")):
            problems.append("every part needs the source_sha256 of its source file")
    return problems


def source_path(sessions_root: Path, recording: dict[str, Any], item: dict[str, Any] | None = None) -> Path:
    item = item or recording["item"]
    return sessions_root / CORPUS / recording["session_id"] / "items" / item["task"] / f"{item['id']}.mp3"


def iter_recordings(data: dict[str, Any]):
    for comparison in data.get("comparisons") or []:
        for recording in comparison.get("recordings") or []:
            yield comparison, recording


def is_external(recording: dict[str, Any]) -> bool:
    """True for a recording of another corpus (MAR.ELE) that has no source session in the research runtime."""
    return bool(recording.get("origin"))


def _normalise(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def session_problems(sessions_root: Path, recording: dict[str, Any]) -> list[str]:
    """Release conditions of the source session of one recording."""
    session_id = recording["session_id"]
    if session_id in EXCLUDED_SESSIONS:
        return [f"{session_id}: excluded from Teaching use ({EXCLUDED_SESSIONS[session_id]})"]
    metadata_file = sessions_root / CORPUS / session_id / "metadata.json"
    if not metadata_file.is_file():
        return [f"{session_id}: metadata.json missing in {sessions_root / CORPUS}"]
    metadata = _load_json(metadata_file)
    problems = []
    if metadata.get("teaching_consent_signed") != "yes":
        problems.append(f"{session_id}: teaching_consent_signed is {metadata.get('teaching_consent_signed')!r}, not 'yes'")
    if metadata.get("needs_review"):
        problems.append(f"{session_id}: needs_review is set")
    if metadata.get("speaker_type") != SPEAKER_TYPE[recording["category"]]:
        problems.append(f"{session_id}: speaker_type {metadata.get('speaker_type')!r} does not match category {recording['category']!r}")
    return problems


def alignment_item(sessions_root: Path, recording: dict[str, Any], item: dict[str, Any] | None = None) -> dict[str, Any] | None:
    item = item or recording["item"]
    alignment = sessions_root / CORPUS / recording["session_id"] / "alignment" / f"{item['task']}.json"
    if not alignment.is_file():
        return None
    return next((entry for entry in _load_json(alignment).get("items") or [] if entry.get("item_id") == item["id"]), None)


def token_window(entry: dict[str, Any], target_tokens: list[str]) -> list[dict[str, Any]] | None:
    """The alignment tokens of ``entry`` that spell ``target_tokens`` in sequence (``None`` when they do not)."""
    tokens = entry.get("tokens") or [{"text": word} for word in re.findall(r"\w+", str(entry.get("text", "")))]  # word-list items carry no tokens
    wanted = [_normalise(word) for word in target_tokens]
    spelled = [_normalise(str(token.get("text", ""))) for token in tokens]
    for index in range(len(spelled) - len(wanted) + 1):
        if spelled[index:index + len(wanted)] == wanted:
            return tokens[index:index + len(wanted)]
    return None


def item_problems(sessions_root: Path, comparison: dict[str, Any], recording: dict[str, Any]) -> list[str]:
    """Every source item of the recording exists and belongs to the wanted item (and word sequence)."""
    problems = []
    for part in recording_parts(recording):
        item = part["item"]
        where = f"{recording['session_id']}/{item.get('id')}"
        if not source_path(sessions_root, recording, item).is_file():
            problems.append(f"{where}: item recording missing: {source_path(sessions_root, recording, item)}")
        entry = alignment_item(sessions_root, recording, item)
        tokens = part.get("target_tokens") or comparison.get("target_tokens")
        if entry is None:
            problems.append(f"{where}: item not found in the session alignment")
        elif tokens and token_window(entry, tokens) is None:
            problems.append(f"{where}: item text {entry.get('text')!r} does not contain {' '.join(tokens)!r} in sequence")
    return problems


def release_rows(data: dict[str, Any], sessions_root: Path) -> list[dict[str, str]]:
    """One row per distinct (session, item) used by a recording or named by a reserve: the Teaching release check."""
    rows: dict[tuple[str, str], dict[str, str]] = {}
    pairs: list[tuple[dict[str, Any], dict[str, Any], str]] = []
    for c, r in iter_recordings(data):
        if is_external(r):
            continue
        for part in recording_parts(r):
            # one pseudo recording per source item, so a montage is checked item by item
            pairs.append((c, {"session_id": r["session_id"], "category": r["category"], "item": part["item"], "target_tokens": part.get("target_tokens")}, "integrated"))
    for reserve in data.get("reserves") or []:
        for category in CATEGORIES:
            pairs.append((reserve, {"session_id": reserve[category], "category": category, "item": reserve["item"]}, "reserve (not integrated)"))
    for comparison, recording, status in pairs:
        key = (recording["session_id"], f"{recording['item']['task']}/{recording['item']['id']}")
        if key in rows:
            continue
        metadata_file = sessions_root / CORPUS / recording["session_id"] / "metadata.json"
        metadata = _load_json(metadata_file) if metadata_file.is_file() else {}
        entry = alignment_item(sessions_root, recording)
        problems = session_problems(sessions_root, recording) + item_problems(sessions_root, comparison, recording)
        rows[key] = {
            "session": recording["session_id"],
            "item": recording["item"]["id"],
            "role": recording["category"],
            "use": f"{comparison.get('id')} · {status}",
            "consent": str(metadata.get("teaching_consent_signed")),
            "review": str(metadata.get("needs_review")),
            "speaker_type": str(metadata.get("speaker_type")),
            "item_text": str((entry or {}).get("text", "-")),
            "result": "OK" if not problems else "BLOCKED: " + "; ".join(problems),
        }
    return list(rows.values())


def render_release_report(rows: list[dict[str, str]]) -> str:
    columns = ["session", "item", "role", "use", "consent", "review", "speaker_type", "item_text", "result"]
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    lines += ["| " + " | ".join(row[column] for column in columns) + " |" for row in rows]
    return "\n".join(lines)


def check(data: dict[str, Any], sessions_root: Path | None = None, marele_root: Path | None = None) -> list[str]:
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
        external = is_external(recording)
        if external and is_montage(recording):
            problems.extend(f"{where}: {problem}" for problem in external_montage_problems(recording))
            if marele_root is not None:
                for part in recording["parts"]:
                    source = marele_root / str(part.get("source_file") or "")
                    if not source.is_file():
                        problems.append(f"{where}: MAR.ELE source missing: {source}")
                    elif sha256_of(source) != part.get("source_sha256"):
                        problems.append(f"{where}: the MAR.ELE source {part['source_file']} changed since the cut was made")
        elif external:
            origin = recording["origin"]
            missing = [key for key in ("corpus", "source_file") if not str(origin.get(key) or "").strip()]
            if missing or recording.get("session_id") or item:
                problems.append(f"{where}: external recording needs origin corpus/source_file and no session or item ({missing})")
        else:
            if not str(recording.get("session_id", "")).startswith(SESSION_PREFIX[category]):
                problems.append(f"{where}: session {recording.get('session_id')!r} does not fit category {category!r}")
            if recording.get("session_id") in EXCLUDED_SESSIONS:
                problems.append(f"{where}: session {recording['session_id']} is excluded from Teaching use ({EXCLUDED_SESSIONS[recording['session_id']]})")
            montage = is_montage(recording)
            if montage:
                join = recording.get("join") or {}
                if len(recording["parts"]) < 2 or not isinstance(join.get("pause_ms"), int) or join["pause_ms"] < 0 or recording.get("item") or recording.get("crop"):
                    problems.append(f"{where}: a montage needs at least two parts, join.pause_ms and no item/crop of its own")
            for part in recording_parts(recording):
                part_item = part.get("item") or {}
                pattern = ITEM_ID.get(part_item.get("task", ""))
                if pattern is None or not pattern.match(str(part_item.get("id", ""))):
                    problems.append(f"{where}: invalid corpus item {part_item!r}")
                part_crop = part.get("crop")
                if montage and part_crop is None:
                    problems.append(f"{where}: every part of a montage needs a crop")
                if part_crop is not None:
                    if not all(isinstance(part_crop.get(key), int) for key in CROP_KEYS) or part_crop["end_ms"] <= part_crop["start_ms"]:
                        problems.append(f"{where}: crop needs integer start_ms < end_ms on a corpus recording")
                    if not (part.get("target_tokens") or comparison.get("target_tokens")):
                        problems.append(f"{where}: a cropped comparison must declare target_tokens")
                    if not str(part.get("source_sha256") or ""):
                        problems.append(f"{where}: cropped recording needs the source_sha256 of the item MP3")
        crop = recording.get("crop")
        if crop is not None and external:
            problems.append(f"{where}: crop needs integer start_ms < end_ms on a corpus recording")
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
        if sessions_root is not None and not external:
            problems.extend(f"{where}: {problem}" for problem in session_problems(sessions_root, recording))
            problems.extend(f"{where}: {problem}" for problem in item_problems(sessions_root, comparison, recording))
            for part in recording_parts(recording):
                origin_file = source_path(sessions_root, recording, part["item"])
                if not origin_file.is_file():
                    problems.append(f"{where}: source recording missing: {origin_file}")
                elif part.get("crop") is not None:
                    if sha256_of(origin_file) != part.get("source_sha256"):
                        problems.append(f"{where}: the source item MP3 changed since the cut was made (re-check the cut points, then --export)")
                elif target.is_file() and sha256_of(origin_file) != sha256_of(target):
                    problems.append(f"{where}: media file differs from its source recording (re-export to refresh)")
    for reserve in data.get("reserves") or []:
        for category in CATEGORIES:
            session_id = str(reserve.get(category) or "")
            if session_id in EXCLUDED_SESSIONS or not session_id.startswith(SESSION_PREFIX[category]):
                problems.append(f"reserve {reserve.get('id')}: {category} session {session_id!r} is excluded or does not fit its category")
        if any(c.get("id") == reserve.get("id") for c in data.get("comparisons") or []):
            problems.append(f"reserve {reserve.get('id')}: a reserve is not an integrated comparison")
    for comparison in data.get("comparisons") or []:
        question = str(comparison.get("question") or "")
        if question and question not in sources.get(comparison["topic"], ""):
            problems.append(f"{comparison.get('id')}: listening question is not quoted in the topic source: {question!r}")
    if sessions_root is not None:
        problems.extend(f"release gate: {row['session']} {row['item']}: {row['result']}" for row in release_rows(data, sessions_root) if row["result"] != "OK")
    return problems


def ffmpeg_version() -> str:
    out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    return out.split(" Copyright")[0].replace("ffmpeg version ", "")


def derive_crop(source: Path, target: Path, crop: dict[str, Any]) -> None:
    """Render the cut-out: trim, edge fades, optional leading silence; metadata stripped, bit-exact muxing."""
    start, end = crop["start_ms"] / 1000, crop["end_ms"] / 1000
    fade_in, fade_out = crop.get("fade_in_ms", 10) / 1000, crop.get("fade_out_ms", 15) / 1000
    chain = f"atrim=start={start}:end={end},asetpts=PTS-STARTPTS,afade=t=in:st=0:d={fade_in},afade=t=out:st={end - start - fade_out:.3f}:d={fade_out}"
    if crop.get("lead_silence_ms"):
        chain += f",adelay={int(crop['lead_silence_ms'])}:all=1"
    command = ["ffmpeg", "-loglevel", "error", "-y", "-i", str(source), "-af", chain, "-map_metadata", "-1",
               "-fflags", "+bitexact", "-flags:a", "+bitexact", *FFMPEG_AUDIO, str(target)]
    subprocess.run(command, check=True)


def derive_montage(sources: list[Path], target: Path, parts: list[dict[str, Any]], join: dict[str, Any]) -> None:
    """Render a montage: each part trimmed and faded like a single cut-out, then joined with ``pause_ms`` of silence between the parts."""
    pause = join["pause_ms"] / 1000
    chains = []
    for index, part in enumerate(parts):
        crop = part["crop"]
        start, end = crop["start_ms"] / 1000, crop["end_ms"] / 1000
        fade_in, fade_out = crop.get("fade_in_ms", 10) / 1000, crop.get("fade_out_ms", 15) / 1000
        chain = f"[{index}:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,afade=t=in:st=0:d={fade_in},afade=t=out:st={end - start - fade_out:.3f}:d={fade_out}"
        if index < len(parts) - 1:
            chain += f",apad=pad_dur={pause}"
        chains.append(chain + f"[p{index}]")
    labels = "".join(f"[p{index}]" for index in range(len(parts)))
    graph = ";".join(chains) + f";{labels}concat=n={len(parts)}:v=0:a=1[out]"
    command = ["ffmpeg", "-loglevel", "error", "-y"]
    for source in sources:
        command += ["-i", str(source)]
    command += ["-filter_complex", graph, "-map", "[out]", "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:a", "+bitexact", *FFMPEG_AUDIO, str(target)]
    subprocess.run(command, check=True)


def export(data: dict[str, Any], sessions_root: Path, marele_root: Path | None = None) -> list[str]:
    """Copy (or cut) the declared recordings from the local runtime into the topic media and refresh their hashes."""
    problems: list[str] = []
    for comparison, recording in iter_recordings(data):
        if is_external(recording):
            if is_montage(recording) and marele_root is not None:
                problems.extend(f"{comparison['id']}/{recording['slot']}: MAR.ELE source missing: {marele_root / part['source_file']}"
                                for part in recording["parts"] if not (marele_root / part["source_file"]).is_file())
            continue
        where = f"{comparison['id']}/{recording['slot']}"
        problems.extend(f"{where}: {problem}" for problem in session_problems(sessions_root, recording))
        problems.extend(f"{where}: {problem}" for problem in item_problems(sessions_root, comparison, recording))
    if problems:
        return problems
    for comparison, recording in iter_recordings(data):
        if is_external(recording):
            if is_montage(recording) and marele_root is not None:
                target = media_path(comparison["topic"], recording["file"])
                target.parent.mkdir(parents=True, exist_ok=True)
                origins = [marele_root / part["source_file"] for part in recording["parts"]]
                derive_montage(origins, target, recording["parts"], recording["join"])
                for part, origin in zip(recording["parts"], origins):
                    part["source_sha256"] = sha256_of(origin)
                recording["join"]["tool"] = f"ffmpeg {ffmpeg_version()}"
                recording["sha256"] = sha256_of(target)
            continue
        target = media_path(comparison["topic"], recording["file"])
        target.parent.mkdir(parents=True, exist_ok=True)
        if is_montage(recording):
            origins = [source_path(sessions_root, recording, part["item"]) for part in recording["parts"]]
            derive_montage(origins, target, recording["parts"], recording["join"])
            for part, origin in zip(recording["parts"], origins):
                part["source_sha256"] = sha256_of(origin)
            recording["join"]["tool"] = f"ffmpeg {ffmpeg_version()}"
            recording["sha256"] = sha256_of(target)
            continue
        origin_file = source_path(sessions_root, recording)
        if recording.get("crop"):
            derive_crop(origin_file, target, recording["crop"])
            recording["source_sha256"] = sha256_of(origin_file)
            recording["crop"]["tool"] = f"ffmpeg {ffmpeg_version()}"
        else:
            shutil.copyfile(origin_file, target)
            recording.pop("source_sha256", None)
        recording["sha256"] = sha256_of(target)
    dump_slots(data)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--export", action="store_true", help="copy or cut the declared recordings from the local runtime")
    parser.add_argument("--check", action="store_true", help="verify the declaration (default)")
    parser.add_argument("--release-report", action="store_true", help="print the Teaching release check (session, item, consent) as a table")
    parser.add_argument("--sessions-root", type=Path, default=DEFAULT_SESSIONS_ROOT, help="runtime sessions root (default: data/sessions)")
    parser.add_argument("--marele-root", type=Path, default=os.environ.get("PROMAT_MARELE_ROOT"), help="root of the MAR.ELE webapp backup (only for MAR.ELE montages)")
    args = parser.parse_args()
    data = load_slots()
    sessions_root = args.sessions_root if runtime_available(args.sessions_root) else None
    if args.release_report:
        if sessions_root is None:
            print(f"No runtime sessions under {args.sessions_root}", file=sys.stderr)
            return 1
        rows = release_rows(data, sessions_root)
        print(render_release_report(rows))
        return 0 if all(row["result"] == "OK" for row in rows) else 1
    if args.export:
        if sessions_root is None:
            print(f"No runtime sessions under {args.sessions_root}", file=sys.stderr)
            return 1
        problems = export(data, sessions_root, args.marele_root)
        print("exported" if not problems else "export refused")
    else:
        problems = check(data, sessions_root, args.marele_root)
        print("slots OK" if not problems else "slots FAILED")
    for problem in problems:
        print(" -", problem)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
