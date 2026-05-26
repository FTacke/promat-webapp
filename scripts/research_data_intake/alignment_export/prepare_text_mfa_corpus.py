from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
import wave


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from intake_batch_common import (  # noqa: E402
    ensure_directory,
    resolve_batch_dir,
    working_text_manifest_path,
    working_text_mfa_corpus_dir,
    working_text_mfa_output_dir,
)
from language_config import describe_language_config, maybe_resolve_language_config  # noqa: E402
from textgrid_support import parse_textgrid_intervals, round_textgrid_seconds, spoken_intervals  # noqa: E402


@dataclass(frozen=True, slots=True)
class TextSourceItem:
    item_id: str
    item_number: str
    text: str


@dataclass(frozen=True, slots=True)
class ManifestItem:
    item_id: str
    item_number: str
    text: str
    source_start_seconds: float
    source_end_seconds: float
    utterance_basename: str


@dataclass(slots=True)
class Summary:
    processed_people: int = 0
    planned_segments: int = 0
    written_segments: int = 0
    warnings: int = 0
    errors: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a per-person MFA intermediate corpus from working/<person_id>/text inputs.",
    )
    parser.add_argument("--batch-dir", required=True, help="Batch directory path or batch name under scripts/research_data_intake/import/.")
    parser.add_argument("--text-source-json", required=True, help="JSON file that provides canonical text items for the text task.")
    parser.add_argument(
        "--language",
        help="Optional intake language code or corpus slug for shared MFA/text-workflow validation, for example es or spanish.",
    )
    parser.add_argument("--person-id", help="Restrict processing to one canonical person_id such as ES-L-0001.")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and planned MFA outputs without writing files.")
    parser.add_argument("--replace-existing", action="store_true", help="Replace existing utterance files and the manifest for the target person(s).")
    return parser.parse_args()


def _print_header(title: str) -> None:
    print(f"\n[{title}]")


def _load_text_source_items(path: Path) -> tuple[list[TextSourceItem], str | None]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    declared_language: str | None = None
    if isinstance(payload, dict):
        task_value = payload.get("task")
        if task_value not in (None, "text"):
            raise ValueError(f"Text source task must be 'text' when declared: {path}")
        language_value = payload.get("language")
        if isinstance(language_value, str) and language_value.strip():
            declared_language = language_value.strip()
        items_payload = payload.get("items")
    else:
        items_payload = payload

    if not isinstance(items_payload, list) or not items_payload:
        raise ValueError(f"Text source must provide a non-empty items list: {path}")

    items: list[TextSourceItem] = []
    for index, item_payload in enumerate(items_payload, start=1):
        if not isinstance(item_payload, dict):
            raise ValueError(f"Text source item {index} must be an object: {path}")
        item_id = item_payload.get("item_id")
        item_number = item_payload.get("item_number")
        text = item_payload.get("text")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError(f"Text source item_id must be a non-empty string at index {index}: {path}")
        if not isinstance(item_number, str) or not item_number.strip():
            raise ValueError(f"Text source item_number must be a non-empty string at index {index}: {path}")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Text source text must be a non-empty string at index {index}: {path}")
        items.append(TextSourceItem(item_id=item_id, item_number=item_number, text=text))
    return items, declared_language


def _normalize_person_id(person_id: str) -> str:
    return person_id.strip().upper()


def _resolve_people(batch_dir: Path, requested_person_id: str | None) -> list[str]:
    working_root = batch_dir / "working"
    if not working_root.exists() or not working_root.is_dir():
        raise FileNotFoundError(f"Batch working/ directory does not exist: {working_root}")
    if requested_person_id:
        person_id = _normalize_person_id(requested_person_id)
        if not (working_root / person_id).exists():
            raise FileNotFoundError(f"Unknown person_id in batch working tree: {person_id}")
        return [person_id]
    return sorted(path.name for path in working_root.iterdir() if path.is_dir())


def _resolve_language(cli_value: str | None, source_value: str | None, source_path: Path) -> str | None:
    cli_config = maybe_resolve_language_config(cli_value)
    source_config = maybe_resolve_language_config(source_value)
    if cli_config is not None and source_config is not None and cli_config.code != source_config.code:
        raise ValueError(
            f"Conflicting text workflow language values for {source_path}: cli={cli_config.code} text_source={source_config.code}"
        )
    resolved = cli_config or source_config
    if resolved is None:
        return None
    return resolved.code


def _source_paths(batch_dir: Path, person_id: str) -> tuple[Path, Path]:
    task_root = batch_dir / "working" / person_id / "text"
    return task_root / "source" / "text.wav", task_root / "alignment" / "text.TextGrid"


def _utterance_basename(index: int, item: TextSourceItem) -> str:
    return f"text_{index:03d}_{item.item_id}"


def _read_wave_params(path: Path) -> tuple[wave._wave_params, int, int]:
    with wave.open(str(path), "rb") as handle:
        params = handle.getparams()
        total_frames = handle.getnframes()
        sample_rate = handle.getframerate()
    return params, total_frames, sample_rate


def _frame_bounds(start_seconds: float, end_seconds: float, sample_rate: int, total_frames: int) -> tuple[int, int]:
    start_frame = max(0, int(round(start_seconds * sample_rate)))
    end_frame = int(round(end_seconds * sample_rate))
    if end_frame > total_frames:
        raise ValueError(
            f"TextGrid boundary exceeds source audio duration: end_seconds={end_seconds:.4f} total_frames={total_frames}"
        )
    if end_frame <= start_frame:
        raise ValueError(
            f"Non-positive segment after frame conversion: start={start_seconds:.4f} end={end_seconds:.4f}"
        )
    return start_frame, end_frame


def _clear_existing_outputs(mfa_corpus_dir: Path, manifest_path: Path) -> None:
    if mfa_corpus_dir.exists():
        for path in mfa_corpus_dir.iterdir():
            if path.is_file() and path.suffix.lower() in {".wav", ".lab"}:
                path.unlink()
    if manifest_path.exists() and manifest_path.is_file():
        manifest_path.unlink()


def _write_segment_wav(source_wav: Path, target_wav: Path, start_frame: int, end_frame: int) -> None:
    with wave.open(str(source_wav), "rb") as source_handle:
        params = source_handle.getparams()
        source_handle.setpos(start_frame)
        frames = source_handle.readframes(end_frame - start_frame)

    with wave.open(str(target_wav), "wb") as target_handle:
        target_handle.setparams(params)
        target_handle.writeframes(frames)


def _build_manifest_items(text_items: list[TextSourceItem], intervals: list[object]) -> list[ManifestItem]:
    manifest_items: list[ManifestItem] = []
    for index, (text_item, interval) in enumerate(zip(text_items, intervals, strict=True), start=1):
        start_seconds = round_textgrid_seconds(interval.start_seconds)
        end_seconds = round_textgrid_seconds(interval.end_seconds)
        if end_seconds <= start_seconds:
            raise ValueError(f"Non-positive timing interval for {text_item.item_id}: {start_seconds} >= {end_seconds}")
        manifest_items.append(
            ManifestItem(
                item_id=text_item.item_id,
                item_number=text_item.item_number,
                text=text_item.text,
                source_start_seconds=start_seconds,
                source_end_seconds=end_seconds,
                utterance_basename=_utterance_basename(index, text_item),
            )
        )
    return manifest_items


def _process_person(
    *,
    batch_dir: Path,
    person_id: str,
    text_items: list[TextSourceItem],
    language_code: str | None,
    language_slug: str | None,
    dry_run: bool,
    replace_existing: bool,
) -> tuple[int, dict[str, object]]:
    source_wav, source_textgrid = _source_paths(batch_dir, person_id)
    if not source_wav.exists() or source_wav.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty text source wav for {person_id}: {source_wav}")
    if not source_textgrid.exists() or source_textgrid.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty text TextGrid for {person_id}: {source_textgrid}")

    intervals = spoken_intervals(parse_textgrid_intervals(source_textgrid))
    if len(intervals) != len(text_items):
        raise ValueError(
            f"Text source item count ({len(text_items)}) does not match spoken TextGrid interval count ({len(intervals)}) for {person_id}"
        )

    manifest_items = _build_manifest_items(text_items, intervals)
    params, total_frames, sample_rate = _read_wave_params(source_wav)
    if params.nchannels <= 0 or params.sampwidth <= 0 or sample_rate <= 0:
        raise ValueError(f"Unsupported WAV parameters for {person_id}: {source_wav}")
    frame_bounds = [
        _frame_bounds(item.source_start_seconds, item.source_end_seconds, sample_rate, total_frames)
        for item in manifest_items
    ]

    mfa_corpus_dir = working_text_mfa_corpus_dir(batch_dir, person_id)
    mfa_output_dir = working_text_mfa_output_dir(batch_dir, person_id)
    manifest_path = working_text_manifest_path(batch_dir, person_id)

    planned_output_paths: list[Path] = []
    for item in manifest_items:
        planned_output_paths.append(mfa_corpus_dir / f"{item.utterance_basename}.wav")
        planned_output_paths.append(mfa_corpus_dir / f"{item.utterance_basename}.lab")
    planned_output_paths.append(manifest_path)

    conflicts = [path for path in planned_output_paths if path.exists() or path.is_symlink()]
    if conflicts and not replace_existing:
        joined = ", ".join(str(path.relative_to(batch_dir)).replace("\\", "/") for path in conflicts[:5])
        raise FileExistsError(f"Existing MFA prep outputs found for {person_id}; rerun with --replace-existing: {joined}")

    if dry_run:
        return len(manifest_items), {
            "person_id": person_id,
            "segments": len(manifest_items),
            "source_wav": str(source_wav.relative_to(batch_dir)).replace("\\", "/"),
            "source_textgrid": str(source_textgrid.relative_to(batch_dir)).replace("\\", "/"),
        }

    ensure_directory(mfa_corpus_dir, dry_run=False)
    ensure_directory(mfa_output_dir, dry_run=False)
    if replace_existing:
        _clear_existing_outputs(mfa_corpus_dir, manifest_path)

    for item, (start_frame, end_frame) in zip(manifest_items, frame_bounds, strict=True):
        _write_segment_wav(
            source_wav=source_wav,
            target_wav=mfa_corpus_dir / f"{item.utterance_basename}.wav",
            start_frame=start_frame,
            end_frame=end_frame,
        )
        (mfa_corpus_dir / f"{item.utterance_basename}.lab").write_text(item.text + "\n", encoding="utf-8")

    manifest_payload = {
        "person_id": person_id,
        "task": "text",
        "language_code": language_code,
        "language": language_slug,
        "source_wav": str(source_wav.relative_to(batch_dir)).replace("\\", "/"),
        "source_textgrid": str(source_textgrid.relative_to(batch_dir)).replace("\\", "/"),
        "items": [asdict(item) for item in manifest_items],
    }
    manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(manifest_items), {
        "person_id": person_id,
        "segments": len(manifest_items),
        "source_wav": manifest_payload["source_wav"],
        "source_textgrid": manifest_payload["source_textgrid"],
    }


def prepare_text_mfa_for_person(
    *,
    batch_dir: Path,
    person_id: str,
    text_source_json: Path,
    cli_language: str | None,
    dry_run: bool = False,
    replace_existing: bool = False,
) -> dict[str, object]:
    text_items, declared_language = _load_text_source_items(text_source_json)
    language_code = _resolve_language(cli_language, declared_language, text_source_json)
    language_config = maybe_resolve_language_config(language_code)
    segment_count, result = _process_person(
        batch_dir=batch_dir,
        person_id=_normalize_person_id(person_id),
        text_items=text_items,
        language_code=None if language_config is None else language_config.code,
        language_slug=None if language_config is None else language_config.corpus_slug,
        dry_run=dry_run,
        replace_existing=replace_existing,
    )
    return {
        **result,
        "segments": segment_count,
        "language_code": None if language_config is None else language_config.code,
        "language_slug": None if language_config is None else language_config.corpus_slug,
        "mode": "dry-run" if dry_run else "write",
    }


def _run() -> int:
    args = parse_args()
    batch_dir = resolve_batch_dir(args.batch_dir)
    text_source_path = Path(args.text_source_json)
    if not text_source_path.is_absolute():
        text_source_path = (Path.cwd() / text_source_path).resolve()
    text_items, declared_language = _load_text_source_items(text_source_path)
    language_code = _resolve_language(args.language, declared_language, text_source_path)
    language_config = maybe_resolve_language_config(language_code)
    people = _resolve_people(batch_dir, args.person_id)
    summary = Summary()
    warnings: list[str] = []

    for person_id in people:
        try:
            segment_count, result = _process_person(
                batch_dir=batch_dir,
                person_id=person_id,
                text_items=text_items,
                language_code=None if language_config is None else language_config.code,
                language_slug=None if language_config is None else language_config.corpus_slug,
                dry_run=args.dry_run,
                replace_existing=args.replace_existing,
            )
        except Exception as exc:
            summary.errors += 1
            if args.person_id:
                raise
            warnings.append(f"skipped {person_id}: {exc}")
            continue

        summary.processed_people += 1
        summary.planned_segments += segment_count
        if not args.dry_run:
            summary.written_segments += segment_count
        print(
            f"prepared {result['person_id']} segments={result['segments']} "
            f"source={result['source_wav']} textgrid={result['source_textgrid']}"
        )

    summary.warnings = len(warnings)
    _print_header("text-mfa-corpus-summary")
    print(f"batch={str(batch_dir).replace('\\', '/')}")
    print(f"mode={'dry-run' if args.dry_run else 'write'} replace_existing={args.replace_existing}")
    print(f"text_source_json={str(text_source_path).replace('\\', '/')}")
    if language_config is not None:
        print(f"language={describe_language_config(language_config)}")
    print(
        "summary "
        f"processed_people={summary.processed_people} planned_segments={summary.planned_segments} "
        f"written_segments={summary.written_segments} warnings={summary.warnings} errors={summary.errors}"
    )
    for warning in warnings:
        print(f"warning: {warning}")
    return 1 if summary.errors else 0


def main() -> int:
    try:
        return _run()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())