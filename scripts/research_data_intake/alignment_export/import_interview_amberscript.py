from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from intake_batch_common import (  # noqa: E402
    person_id_language_slug,
    read_json_file,
    resolve_batch_dir,
    resolve_catalog_item,
    working_alignment_json_path,
)
from textgrid_support import seconds_to_ms  # noqa: E402


EXPECTED_FULL_MP3_PATH = "derived/interview.mp3"
SPEAKER_CODE_MAP = {
    "spk1": "interviewer",
    "spk2": "participant",
}
SPEAKER_NAME_CODE_MAP = {
    "speaker 1": "interviewer",
    "speaker 2": "participant",
}
ANNOTATION_TASK_PREFIXES = (
    ("wl_", "wordlist"),
    ("d_", "text"),
    ("qy_", "text"),
    ("qw_", "text"),
    ("t_", "text"),
)
MATERIAL_REF_PATTERN = re.compile(r"\[(?P<item_id>(?:wl_|d_|qy_|qw_|t_)\d+)\]")


class InterviewImportError(ValueError):
    def __init__(self, status_code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transform one Amberscript interview export into the batch-local PROMAT working alignment/interview.json format.",
    )
    parser.add_argument("--source-json", required=True, help="Path to the Amberscript export JSON.")
    parser.add_argument("--person-id", required=True, help="Canonical person_id such as ES-L-0001.")
    parser.add_argument(
        "--batch-dir",
        help="Optional batch directory path or batch name under scripts/research_data_intake/import/ to resolve the default working output path.",
    )
    parser.add_argument("--output-json", help="Optional explicit output path. Defaults to working/{person_id}/interview/alignment/interview.json when --batch-dir is set.")
    parser.add_argument("--session-id", help="Optional resolved session_id. Defaults to null in the working-tree output.")
    parser.add_argument("--dry-run", action="store_true", help="Validate the Amberscript export without writing the output JSON.")
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Replace an existing output JSON instead of failing when the file already exists.",
    )
    return parser.parse_args()


def _print_header(title: str) -> None:
    print(f"\n[{title}]")


def _normalize_person_id(person_id: str) -> str:
    normalized = person_id.strip().upper()
    if not normalized:
        raise ValueError("person_id must not be empty")
    return normalized


def _require_segments(payload: dict[str, Any], source_json_path: Path) -> list[dict[str, Any]]:
    segments_payload = payload.get("segments")
    if not isinstance(segments_payload, list) or not segments_payload:
        raise ValueError(f"Amberscript export must contain a non-empty segments list: {source_json_path}")
    normalized_segments: list[dict[str, Any]] = []
    for index, segment_payload in enumerate(segments_payload, start=1):
        if not isinstance(segment_payload, dict):
            raise ValueError(f"Segment {index} must be an object: {source_json_path}")
        normalized_segments.append(segment_payload)
    return normalized_segments


def _require_words(segment_payload: dict[str, Any], source_json_path: Path, segment_number: int) -> list[dict[str, Any]]:
    words_payload = segment_payload.get("words")
    if not isinstance(words_payload, list) or not words_payload:
        raise ValueError(f"Segment {segment_number} must contain a non-empty words list: {source_json_path}")
    normalized_words: list[dict[str, Any]] = []
    for word_index, word_payload in enumerate(words_payload, start=1):
        if not isinstance(word_payload, dict):
            raise ValueError(f"Segment {segment_number} word {word_index} must be an object: {source_json_path}")
        normalized_words.append(word_payload)
    return normalized_words


def _require_word_timing(word_payload: dict[str, Any], key: str, source_json_path: Path, segment_number: int, word_index: int) -> int:
    value = word_payload.get(key)
    if not isinstance(value, (int, float)):
        raise ValueError(
            f"Segment {segment_number} word {word_index} field {key!r} must be numeric in {source_json_path}"
        )
    return seconds_to_ms(float(value))


def _require_word_text(word_payload: dict[str, Any], source_json_path: Path, segment_number: int, word_index: int) -> str:
    value = word_payload.get("text")
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Segment {segment_number} word {word_index} must have non-empty text in {source_json_path}")
    return value.strip()


def _amberscript_speaker_code_map(payload: dict[str, Any], source_json_path: Path) -> dict[str, str]:
    speakers_payload = payload.get("speakers")
    if speakers_payload is None:
        return {}
    if not isinstance(speakers_payload, list):
        raise ValueError(f"Amberscript export speakers must be a list when present: {source_json_path}")

    mapped: dict[str, str] = {}
    for index, speaker_payload in enumerate(speakers_payload, start=1):
        if not isinstance(speaker_payload, dict):
            raise ValueError(f"Amberscript speaker {index} must be an object: {source_json_path}")
        raw_spkid = speaker_payload.get("spkid")
        raw_name = speaker_payload.get("name")
        if not isinstance(raw_spkid, str) or not raw_spkid.strip():
            continue
        if not isinstance(raw_name, str) or not raw_name.strip():
            continue

        normalized_spkid = raw_spkid.strip().lower()
        normalized_name = raw_name.strip().lower()
        resolved_code = SPEAKER_NAME_CODE_MAP.get(normalized_name)
        if resolved_code is None:
            continue
        existing_code = mapped.get(normalized_spkid)
        if existing_code is not None and existing_code != resolved_code:
            raise ValueError(
                f"Amberscript speaker id {raw_spkid!r} maps to multiple speaker roles in {source_json_path}"
            )
        mapped[normalized_spkid] = resolved_code
    return mapped


def _speaker_code(raw_value: Any, source_json_path: Path, segment_number: int, speaker_id_map: dict[str, str]) -> str:
    if not isinstance(raw_value, str) or not raw_value.strip():
        raise ValueError(f"Segment {segment_number} must declare a speaker code in {source_json_path}")
    normalized = raw_value.strip().lower()
    if normalized not in SPEAKER_CODE_MAP:
        mapped_code = speaker_id_map.get(normalized)
        if mapped_code is not None:
            return mapped_code
        raise ValueError(f"Unsupported Amberscript speaker code {raw_value!r} in segment {segment_number}: {source_json_path}")
    return SPEAKER_CODE_MAP[normalized]


def _annotation_task(item_id: str) -> str | None:
    normalized = item_id.strip().lower()
    for prefix, task_name in ANNOTATION_TASK_PREFIXES:
        if normalized.startswith(prefix):
            return task_name
    return None


def _zero_padded_item_id(item_id: str) -> str:
    match = re.fullmatch(r"(?P<prefix>wl_|d_|qy_|qw_|t_)(?P<number>\d+)", item_id.strip().lower())
    if match is None:
        return item_id
    width = 3 if match.group("prefix") == "wl_" else 2
    return f"{match.group('prefix')}{int(match.group('number')):0{width}d}"


def _resolve_annotation_catalog_entry(*, language_slug: str, item_id: str, source_json_path: Path) -> tuple[str, str, dict[str, object]]:
    task_name = _annotation_task(item_id)
    if task_name is None:
        raise InterviewImportError(
            "error_invalid_material_ref_marker",
            f"Unsupported material reference prefix in {item_id!r}: {source_json_path}",
        )
    resolved_item_id = item_id
    catalog_entry = resolve_catalog_item(language_slug, task_name, resolved_item_id)
    if catalog_entry is None:
        normalized_item_id = _zero_padded_item_id(item_id)
        if normalized_item_id != item_id:
            normalized_catalog_entry = resolve_catalog_item(language_slug, task_name, normalized_item_id)
            if normalized_catalog_entry is not None:
                resolved_item_id = normalized_item_id
                catalog_entry = normalized_catalog_entry
    if catalog_entry is None:
        raise InterviewImportError(
            "error_unknown_material_ref_item_id",
            f"Unknown material reference item_id {item_id!r} for {language_slug}/{task_name}: {source_json_path}",
        )
    return task_name, resolved_item_id, {
        "label": catalog_entry.label,
        "item_number": catalog_entry.item_number,
        "canonical_text": catalog_entry.canonical_text,
    }


def _split_material_ref_token(*, raw_text: str, source_json_path: Path) -> tuple[str, str, str]:
    if raw_text.count("[") != 1 or raw_text.count("]") != 1:
        raise InterviewImportError(
            "error_invalid_material_ref_marker",
            f"Invalid material reference marker {raw_text!r}: {source_json_path}",
        )
    match = MATERIAL_REF_PATTERN.search(raw_text)
    if match is None:
        raise InterviewImportError(
            "error_invalid_material_ref_marker",
            f"Invalid material reference marker {raw_text!r}: {source_json_path}",
        )

    prefix = raw_text[: match.start()]
    suffix = raw_text[match.end() :]
    if "[" in prefix or "]" in prefix or "[" in suffix or "]" in suffix:
        raise InterviewImportError(
            "error_invalid_material_ref_marker",
            f"Nested material reference marker {raw_text!r}: {source_json_path}",
        )

    normalized_suffix = suffix.strip()
    if normalized_suffix and not re.fullmatch(r"[.,!?;:\-]+", normalized_suffix):
        raise InterviewImportError(
            "error_invalid_material_ref_marker",
            f"Material reference marker must only carry trailing punctuation, got {raw_text!r}: {source_json_path}",
        )

    return prefix.rstrip(), normalized_suffix, match.group("item_id")


def _material_ref_annotation(
    *,
    item_id: str,
    insert_after_token_id: str,
    language_slug: str,
    source_json_path: Path,
) -> dict[str, object]:
    task_name, resolved_item_id, catalog_payload = _resolve_annotation_catalog_entry(
        language_slug=language_slug,
        item_id=item_id,
        source_json_path=source_json_path,
    )
    return {
        "kind": "material_ref",
        "item_id": resolved_item_id,
        "task": task_name,
        "insert_after_token_id": insert_after_token_id,
        **catalog_payload,
    }


def _append_token(
    tokens: list[dict[str, object]],
    *,
    segment_id: str,
    text: str,
    start_ms: int,
    end_ms: int,
    suffix: str = "",
) -> str:
    token_id = f"{segment_id}_tok_{len(tokens) + 1:03d}"
    token_payload: dict[str, object] = {
        "token_id": token_id,
        "text": text,
        "start_ms": start_ms,
        "end_ms": end_ms,
    }
    if suffix:
        token_payload["suffix"] = suffix
    tokens.append(token_payload)
    return token_id


def _token_text_for_segment_text(token: dict[str, object]) -> str:
    suffix = token.get("suffix")
    if isinstance(suffix, str) and suffix:
        return f"{token['text']}{suffix}"
    return str(token["text"])


def _is_intraword_bracket_literal(raw_text: str) -> bool:
    match = re.search(r"\[[^\]]*\]", raw_text)
    if match is None:
        return False
    label = match.group(0).strip("[]")
    if re.fullmatch(r"[A-Za-z]+_\d+", label):
        return False
    has_left_anchor = match.start() > 0 and raw_text[match.start() - 1].isalnum()
    has_right_anchor = match.end() < len(raw_text) and raw_text[match.end()].isalnum()
    has_right_boundary = match.end() == len(raw_text) or not raw_text[match.end()].isalnum()
    return has_left_anchor and (has_right_anchor or has_right_boundary)


def _is_non_material_bracket_literal(raw_text: str) -> bool:
    if _is_intraword_bracket_literal(raw_text):
        return True
    stripped = raw_text.strip().strip('"')
    match = re.search(r"\[(?P<label>[^\[\]]*)\]", stripped)
    if match is None:
        unmatched = re.search(r"\[(?P<label>[^\[\]\s]+)$", stripped)
        if unmatched is None:
            unmatched_closing = re.search(r"(?P<label>[^\[\]\s]+)\]", stripped)
            if unmatched_closing is None:
                return False
            label = unmatched_closing.group("label").strip()
            return bool(label) and not re.fullmatch(r"[A-Za-z]+_\d+", label)
        label = unmatched.group("label").strip()
        return bool(label) and not re.fullmatch(r"[A-Za-z]+_\d+", label)
    label = match.group("label").strip()
    if re.fullmatch(r"[A-Za-z]+_\d+", label):
        return False
    return True


def _append_suffix_to_previous_token(tokens: list[dict[str, object]], suffix: str) -> None:
    if not suffix:
        return
    if not tokens:
        raise InterviewImportError(
            "error_invalid_material_ref_marker",
            "Material reference marker lost its spoken anchor before any token was emitted.",
        )
    previous_suffix = tokens[-1].get("suffix")
    if isinstance(previous_suffix, str) and previous_suffix:
        tokens[-1]["suffix"] = f"{previous_suffix}{suffix}"
    else:
        tokens[-1]["suffix"] = suffix


def build_interview_alignment_payload(
    *,
    source_json_path: Path,
    person_id: str,
    session_id: str | None = None,
) -> dict[str, object]:
    payload = read_json_file(source_json_path)
    segments_payload = _require_segments(payload, source_json_path)
    normalized_person_id = _normalize_person_id(person_id)
    language_slug = person_id_language_slug(normalized_person_id)
    speaker_id_map = _amberscript_speaker_code_map(payload, source_json_path)

    warnings: list[str] = []
    segments: list[dict[str, object]] = []
    for segment_index, segment_payload in enumerate(segments_payload, start=1):
        words_payload = _require_words(segment_payload, source_json_path, segment_index)
        segment_id = f"seg_{segment_index:03d}"
        speaker_code = _speaker_code(segment_payload.get("speaker"), source_json_path, segment_index, speaker_id_map)
        first_start_ms = _require_word_timing(words_payload[0], "start", source_json_path, segment_index, 1)
        last_end_ms = _require_word_timing(
            words_payload[-1],
            "end",
            source_json_path,
            segment_index,
            len(words_payload),
        )
        if last_end_ms <= first_start_ms:
            warnings.append(f"segment {segment_index} has zero duration; clamped to 1ms")
            last_end_ms = first_start_ms + 1

        tokens: list[dict[str, object]] = []
        annotations: list[dict[str, object]] = []
        previous_token_id: str | None = None

        for word_index, word_payload in enumerate(words_payload, start=1):
            text = _require_word_text(word_payload, source_json_path, segment_index, word_index)
            start_ms = _require_word_timing(word_payload, "start", source_json_path, segment_index, word_index)
            end_ms = _require_word_timing(word_payload, "end", source_json_path, segment_index, word_index)
            if end_ms <= start_ms:
                warnings.append(
                    f"segment {segment_index} word {word_index} ({text!r}) has zero duration; clamped to 1ms"
                )
                end_ms = start_ms + 1

            material_ref_match = MATERIAL_REF_PATTERN.search(text)
            if material_ref_match is not None:
                cleaned_text, token_suffix, item_id = _split_material_ref_token(raw_text=text, source_json_path=source_json_path)
                if cleaned_text:
                    previous_token_id = _append_token(
                        tokens,
                        segment_id=segment_id,
                        text=cleaned_text,
                        start_ms=start_ms,
                        end_ms=end_ms,
                        suffix=token_suffix,
                    )
                else:
                    if previous_token_id is None:
                        raise InterviewImportError(
                            "error_invalid_material_ref_marker",
                            f"Material reference marker lost its spoken anchor in {text!r}: {source_json_path}",
                        )
                    _append_suffix_to_previous_token(tokens, token_suffix)
                annotations.append(
                    _material_ref_annotation(
                        item_id=item_id,
                        insert_after_token_id=previous_token_id,
                        language_slug=language_slug,
                        source_json_path=source_json_path,
                    )
                )
            else:
                previous_token_id = _append_token(
                    tokens,
                    segment_id=segment_id,
                    text=text,
                    start_ms=start_ms,
                    end_ms=end_ms,
                )
            if material_ref_match is None and ("[" in text or "]" in text) and not _is_non_material_bracket_literal(text):
                raise InterviewImportError(
                    "error_invalid_material_ref_marker",
                    f"Invalid material reference marker {text!r}: {source_json_path}",
                )

        segment_payload_json: dict[str, object] = {
            "segment_id": segment_id,
            "segment_number": str(segment_index),
            "speaker_code": speaker_code,
            "start_ms": first_start_ms,
            "end_ms": last_end_ms,
            "text": " ".join(_token_text_for_segment_text(token) for token in tokens),
        }
        if tokens:
            segment_payload_json["tokens"] = tokens
        if annotations:
            segment_payload_json["annotations"] = annotations
        segments.append(segment_payload_json)

    if not segments:
        raise ValueError(f"No usable interview segments were derived from {source_json_path}")

    result: dict[str, object] = {
        "session_id": session_id,
        "person_id": normalized_person_id,
        "task": "interview",
        "audio": {
            "full_mp3": EXPECTED_FULL_MP3_PATH,
        },
        "segments": segments,
    }
    if warnings:
        result["_import_warnings"] = warnings
    return result


def write_interview_alignment_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _resolve_output_json_path(output_json: str | None, batch_dir: Path | None, person_id: str) -> Path:
    if output_json:
        output_path = Path(output_json)
        if not output_path.is_absolute():
            output_path = (Path.cwd() / output_path).resolve()
        return output_path
    if batch_dir is None:
        raise ValueError("Either --output-json or --batch-dir must be provided")
    return working_alignment_json_path(batch_dir, person_id, "interview")


def _run() -> int:
    args = parse_args()
    source_json_path = Path(args.source_json)
    if not source_json_path.is_absolute():
        source_json_path = (Path.cwd() / source_json_path).resolve()

    batch_dir = resolve_batch_dir(args.batch_dir) if args.batch_dir else None
    person_id = _normalize_person_id(args.person_id)
    output_json_path = _resolve_output_json_path(args.output_json, batch_dir, person_id)
    if output_json_path.exists() and not args.replace_existing:
        raise FileExistsError(f"Interview alignment JSON already exists: {output_json_path}")

    payload = build_interview_alignment_payload(
        source_json_path=source_json_path,
        person_id=person_id,
        session_id=args.session_id,
    )
    if not args.dry_run:
        write_interview_alignment_json(output_json_path, payload)

    token_count = sum(len(segment.get("tokens", [])) for segment in payload["segments"])
    annotation_count = sum(len(segment.get("annotations", [])) for segment in payload["segments"])
    _print_header("interview-amberscript-import-summary")
    print(f"source_json={source_json_path.as_posix()}")
    print(f"output_json={output_json_path.as_posix()}")
    if batch_dir is not None:
        print(f"batch={batch_dir.as_posix()}")
    print(f"mode={'dry-run' if args.dry_run else 'write'} replace_existing={args.replace_existing}")
    print(
        f"summary person_id={person_id} segments={len(payload['segments'])} tokens={token_count} annotations={annotation_count}"
    )
    return 0


def main() -> int:
    try:
        return _run()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
