from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Any


SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from intake_batch_common import resolve_batch_dir  # noqa: E402
from language_config import describe_language_config, maybe_resolve_language_config  # noqa: E402
from textgrid_support import (  # noqa: E402
    SILENCE_MARKERS,
    TextGridInterval,
    get_textgrid_tier,
    round_textgrid_seconds,
    seconds_to_ms,
)


EXPECTED_FULL_MP3_PATH = "derived/text.mp3"
MFA_WORD_TIER_NAME = "words"
IGNORED_TOKEN_MARKERS = SILENCE_MARKERS | {"spn", "unk", "<unk>", "noise", "<noise>", "[noise]", "[spn]"}
TIME_TOLERANCE_SECONDS = 0.001


@dataclass(frozen=True, slots=True)
class ManifestItem:
    item_id: str
    item_number: str
    text: str
    source_start_seconds: float
    source_end_seconds: float
    utterance_basename: str

    @property
    def start_ms(self) -> int:
        return seconds_to_ms(self.source_start_seconds)

    @property
    def end_ms(self) -> int:
        return seconds_to_ms(self.source_end_seconds)


@dataclass(frozen=True, slots=True)
class TokenPayload:
    token_id: str
    text: str
    start_ms: int
    end_ms: int

    def to_json(self) -> dict[str, object]:
        return {
            "token_id": self.token_id,
            "text": self.text,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
        }


@dataclass(frozen=True, slots=True)
class ItemPayload:
    item_id: str
    item_number: str
    text: str
    start_ms: int
    end_ms: int
    tokens: list[TokenPayload]

    def to_json(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "item_number": self.item_number,
            "text": self.text,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "tokens": [token.to_json() for token in self.tokens],
        }


@dataclass(slots=True)
class PersonImportResult:
    person_id: str
    batch_name: str
    imported: bool
    skipped_reason: str | None
    warnings: list[str]
    item_count: int
    token_count: int
    output_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import MFA text outputs from batch working trees into final PROMAT-style working alignment/text.json files.",
    )
    parser.add_argument("--batch-dir", required=True, help="Batch directory path or batch name under scripts/research_data_intake/import/.")
    parser.add_argument(
        "--language",
        help="Optional intake language code or corpus slug for shared MFA/text-workflow validation, for example es or spanish.",
    )
    parser.add_argument("--person-id", help="Restrict import to one canonical person_id such as ES-L-0001.")
    parser.add_argument("--dry-run", action="store_true", help="Validate the import plan and MFA outputs without writing alignment/text.json.")
    parser.add_argument(
        "--fail-on-missing-output",
        action="store_true",
        help="Treat missing or unusable MFA per-item output as a hard person-level failure instead of importing with warnings.",
    )
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Replace an existing working text alignment/text.json file instead of skipping that person.",
    )
    return parser.parse_args()


def _print_header(title: str) -> None:
    print(f"\n[{title}]")


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


def _load_manifest_items(manifest_path: Path) -> list[ManifestItem]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    items_payload = payload.get("items")
    if not isinstance(items_payload, list) or not items_payload:
        raise ValueError(f"Manifest must contain a non-empty items list: {manifest_path}")

    items: list[ManifestItem] = []
    seen_basenames: set[str] = set()
    for index, item_payload in enumerate(items_payload, start=1):
        if not isinstance(item_payload, dict):
            raise ValueError(f"Manifest item {index} must be an object: {manifest_path}")
        item = ManifestItem(
            item_id=_require_non_empty_string(item_payload, "item_id", manifest_path, index),
            item_number=_require_non_empty_string(item_payload, "item_number", manifest_path, index),
            text=_require_non_empty_string(item_payload, "text", manifest_path, index),
            source_start_seconds=_require_float(item_payload, "source_start_seconds", manifest_path, index),
            source_end_seconds=_require_float(item_payload, "source_end_seconds", manifest_path, index),
            utterance_basename=_require_non_empty_string(item_payload, "utterance_basename", manifest_path, index),
        )
        if item.utterance_basename in seen_basenames:
            raise ValueError(f"Duplicate utterance_basename in manifest: {item.utterance_basename}")
        if item.source_end_seconds <= item.source_start_seconds:
            raise ValueError(
                f"Manifest item has non-positive duration for {item.item_id}: {item.source_start_seconds} >= {item.source_end_seconds}"
            )
        seen_basenames.add(item.utterance_basename)
        items.append(item)
    return items


def _require_non_empty_string(payload: dict[str, Any], key: str, path: Path, index: int) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Manifest field {key!r} must be a non-empty string at item {index}: {path}")
    return value


def _require_float(payload: dict[str, Any], key: str, path: Path, index: int) -> float:
    value = payload.get(key)
    if not isinstance(value, (int, float)):
        raise ValueError(f"Manifest field {key!r} must be numeric at item {index}: {path}")
    return float(value)


def _load_manifest_payload(manifest_path: Path) -> dict[str, Any]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Manifest root must be an object: {manifest_path}")
    return payload


def _session_id_from_manifest(manifest_payload: dict[str, Any]) -> str | None:
    session_id = manifest_payload.get("session_id")
    if isinstance(session_id, str) and session_id.strip():
        return session_id
    return None


def _resolve_language_config(manifest_payload: dict[str, Any], cli_value: str | None) -> object | None:
    cli_config = maybe_resolve_language_config(cli_value)
    manifest_config = maybe_resolve_language_config(
        manifest_payload.get("language_code") if isinstance(manifest_payload.get("language_code"), str) else None
    )
    if manifest_config is None:
        manifest_config = maybe_resolve_language_config(
            manifest_payload.get("language") if isinstance(manifest_payload.get("language"), str) else None
        )
    if cli_config is not None and manifest_config is not None and cli_config.code != manifest_config.code:
        raise ValueError(f"Conflicting language settings: cli={cli_config.code} manifest={manifest_config.code}")
    return cli_config or manifest_config


def _person_paths(batch_dir: Path, person_id: str) -> dict[str, Path]:
    text_root = batch_dir / "working" / person_id / "text"
    return {
        "text_root": text_root,
        "source_wav": text_root / "source" / "text.wav",
        "source_textgrid": text_root / "alignment" / "text.TextGrid",
        "manifest": text_root / "mfa_manifest.json",
        "mfa_corpus": text_root / "mfa_corpus",
        "mfa_output": text_root / "mfa_output",
        "alignment_json": text_root / "alignment" / "text.json",
    }


def _list_mfa_output_textgrids(mfa_output_dir: Path) -> dict[str, Path]:
    matches: dict[str, Path] = {}
    for path in sorted(mfa_output_dir.glob("*.TextGrid")):
        matches[path.stem] = path
    return matches


def _is_ignored_token(text: str) -> bool:
    normalized = text.strip().lower()
    return normalized in IGNORED_TOKEN_MARKERS


def _globalize_interval(interval: TextGridInterval, item: ManifestItem) -> tuple[float, float]:
    global_start = round_textgrid_seconds(item.source_start_seconds + interval.start_seconds)
    global_end = round_textgrid_seconds(item.source_start_seconds + interval.end_seconds)
    if global_start < item.source_start_seconds - TIME_TOLERANCE_SECONDS:
        raise ValueError(f"Token starts before segment window for {item.utterance_basename}")
    if global_end > item.source_end_seconds + TIME_TOLERANCE_SECONDS:
        raise ValueError(f"Token ends after segment window for {item.utterance_basename}")
    if global_end <= global_start:
        raise ValueError(f"Token interval is non-positive for {item.utterance_basename}")
    return global_start, global_end


def _build_tokens(item: ManifestItem, mfa_textgrid_path: Path) -> list[TokenPayload]:
    word_tier = get_textgrid_tier(mfa_textgrid_path, MFA_WORD_TIER_NAME)
    tokens: list[TokenPayload] = []
    previous_end_ms = -1
    for token_index, interval in enumerate(word_tier.intervals, start=1):
        if _is_ignored_token(interval.text):
            continue
        global_start_seconds, global_end_seconds = _globalize_interval(interval, item)
        start_ms = seconds_to_ms(global_start_seconds)
        end_ms = seconds_to_ms(global_end_seconds)
        if start_ms < 0 or end_ms < 0:
            raise ValueError(f"Negative token timing produced for {item.utterance_basename}")
        if end_ms <= start_ms:
            raise ValueError(f"Non-positive token ms interval produced for {item.utterance_basename}")
        if previous_end_ms > start_ms:
            raise ValueError(f"Non-monotone token timing in {item.utterance_basename}")
        tokens.append(
            TokenPayload(
                token_id=f"{item.item_id}_tok_{token_index:02d}",
                text=interval.text,
                start_ms=start_ms,
                end_ms=end_ms,
            )
        )
        previous_end_ms = end_ms
    return tokens


def _build_item_payloads(
    manifest_items: list[ManifestItem],
    mfa_output_textgrids: dict[str, Path],
    fail_on_missing_output: bool,
) -> tuple[list[ItemPayload], list[str], int]:
    warnings: list[str] = []
    item_payloads: list[ItemPayload] = []
    token_count = 0
    for item in manifest_items:
        mfa_textgrid_path = mfa_output_textgrids.get(item.utterance_basename)
        tokens: list[TokenPayload] = []
        if mfa_textgrid_path is None:
            message = f"missing MFA TextGrid for {item.utterance_basename}"
            if fail_on_missing_output:
                raise ValueError(message)
            warnings.append(message)
        else:
            tokens = _build_tokens(item, mfa_textgrid_path)
            if not tokens:
                message = f"empty token list for {item.utterance_basename}"
                if fail_on_missing_output:
                    raise ValueError(message)
                warnings.append(message)

        item_payloads.append(
            ItemPayload(
                item_id=item.item_id,
                item_number=item.item_number,
                text=item.text,
                start_ms=item.start_ms,
                end_ms=item.end_ms,
                tokens=tokens,
            )
        )
        token_count += len(tokens)
    return item_payloads, warnings, token_count


def _build_alignment_payload(session_id: str | None, person_id: str, items: list[ItemPayload]) -> dict[str, object]:
    return {
        "session_id": session_id,
        "person_id": person_id,
        "task": "text",
        "audio": {
            "full_mp3": EXPECTED_FULL_MP3_PATH,
        },
        "items": [item.to_json() for item in items],
    }


def _manifest_omitted_items(manifest_payload: dict[str, Any], manifest_path: Path) -> list[dict[str, object]]:
    omitted_payload = manifest_payload.get("omitted_items")
    if omitted_payload is None:
        return []
    if not isinstance(omitted_payload, list):
        raise ValueError(f"Manifest omitted_items must be a list when present: {manifest_path}")
    omitted_items: list[dict[str, object]] = []
    for index, item_payload in enumerate(omitted_payload, start=1):
        if not isinstance(item_payload, dict):
            raise ValueError(f"Manifest omitted item {index} must be an object: {manifest_path}")
        item_id = _require_non_empty_string(item_payload, "item_id", manifest_path, index)
        item_number = _require_non_empty_string(item_payload, "item_number", manifest_path, index)
        text = _require_non_empty_string(item_payload, "text", manifest_path, index)
        omit_reason = _require_non_empty_string(item_payload, "omit_reason", manifest_path, index)
        if item_payload.get("omitted") is not True:
            raise ValueError(f"Manifest omitted item {item_id} must set omitted=true: {manifest_path}")
        omitted_items.append(
            {
                "item_id": item_id,
                "item_number": item_number,
                "text": text,
                "omitted": True,
                "omit_reason": omit_reason,
            }
        )
    return omitted_items


def _write_alignment_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _import_person(
    batch_dir: Path,
    person_id: str,
    cli_language: str | None,
    dry_run: bool,
    fail_on_missing_output: bool,
    replace_existing: bool,
) -> PersonImportResult:
    paths = _person_paths(batch_dir, person_id)
    warnings: list[str] = []

    for required_key in ("source_wav", "manifest", "mfa_corpus", "mfa_output"):
        required_path = paths[required_key]
        if not required_path.exists():
            return PersonImportResult(
                person_id=person_id,
                batch_name=batch_dir.name,
                imported=False,
                skipped_reason=f"missing {required_key}: {required_path}",
                warnings=warnings,
                item_count=0,
                token_count=0,
                output_path=paths["alignment_json"],
            )

    if paths["alignment_json"].exists() and not replace_existing:
        return PersonImportResult(
            person_id=person_id,
            batch_name=batch_dir.name,
            imported=False,
            skipped_reason=f"existing alignment JSON: {paths['alignment_json']}",
            warnings=warnings,
            item_count=0,
            token_count=0,
            output_path=paths["alignment_json"],
        )

    manifest_payload = _load_manifest_payload(paths["manifest"])
    _resolve_language_config(manifest_payload, cli_language)
    manifest_items = _load_manifest_items(paths["manifest"])
    source_textgrid_value = manifest_payload.get("source_textgrid")
    if isinstance(source_textgrid_value, str) and source_textgrid_value:
        source_textgrid_path = batch_dir / source_textgrid_value.replace("/", "\\")
        if not source_textgrid_path.exists():
            warnings.append(f"manifest source_textgrid not found: {source_textgrid_value}")
    elif not paths["source_textgrid"].exists():
        warnings.append(f"source TextGrid not found: {paths['source_textgrid']}")

    mfa_output_textgrids = _list_mfa_output_textgrids(paths["mfa_output"])
    if not mfa_output_textgrids:
        return PersonImportResult(
            person_id=person_id,
            batch_name=batch_dir.name,
            imported=False,
            skipped_reason=f"no MFA TextGrids in {paths['mfa_output']}",
            warnings=warnings,
            item_count=0,
            token_count=0,
            output_path=paths["alignment_json"],
        )

    manifest_basenames = {item.utterance_basename for item in manifest_items}
    unmatched_outputs = sorted(set(mfa_output_textgrids) - manifest_basenames)
    if unmatched_outputs:
        warnings.append(f"unmatched MFA outputs: {', '.join(unmatched_outputs[:5])}")

    item_payloads, item_warnings, token_count = _build_item_payloads(
        manifest_items=manifest_items,
        mfa_output_textgrids=mfa_output_textgrids,
        fail_on_missing_output=fail_on_missing_output,
    )
    warnings.extend(item_warnings)

    payload = _build_alignment_payload(
        session_id=_session_id_from_manifest(manifest_payload),
        person_id=person_id,
        items=item_payloads,
    )
    omitted_items = _manifest_omitted_items(manifest_payload, paths["manifest"])
    if omitted_items:
        payload["omitted_items"] = omitted_items

    if payload.get("session_id") is None:
        warnings.append("session_id remains unresolved in the working tree and was serialized as null")

    if not dry_run:
        _write_alignment_json(paths["alignment_json"], payload)

    return PersonImportResult(
        person_id=person_id,
        batch_name=batch_dir.name,
        imported=True,
        skipped_reason=None,
        warnings=warnings,
        item_count=len(item_payloads),
        token_count=token_count,
        output_path=paths["alignment_json"],
    )


def import_text_mfa_alignment_for_person(
    *,
    batch_dir: Path,
    person_id: str,
    cli_language: str | None,
    dry_run: bool = False,
    fail_on_missing_output: bool = False,
    replace_existing: bool = False,
) -> PersonImportResult:
    return _import_person(
        batch_dir=batch_dir,
        person_id=_normalize_person_id(person_id),
        cli_language=cli_language,
        dry_run=dry_run,
        fail_on_missing_output=fail_on_missing_output,
        replace_existing=replace_existing,
    )


def _run() -> int:
    args = parse_args()
    batch_dir = resolve_batch_dir(args.batch_dir)
    people = _resolve_people(batch_dir, args.person_id)

    imported_results: list[PersonImportResult] = []
    skipped_results: list[PersonImportResult] = []
    error_messages: list[str] = []

    for person_id in people:
        try:
            result = _import_person(
                batch_dir=batch_dir,
                person_id=person_id,
                cli_language=args.language,
                dry_run=args.dry_run,
                fail_on_missing_output=args.fail_on_missing_output,
                replace_existing=args.replace_existing,
            )
        except Exception as exc:
            message = f"{person_id}: {exc}"
            error_messages.append(message)
            if args.person_id:
                raise
            print(f"error {message}")
            continue

        if result.imported:
            imported_results.append(result)
            print(
                f"imported {result.person_id} items={result.item_count} tokens={result.token_count} "
                f"output={result.output_path.relative_to(batch_dir).as_posix()}"
            )
            for warning in result.warnings:
                print(f"warning {result.person_id}: {warning}")
        else:
            skipped_results.append(result)
            print(f"skipped {result.person_id}: {result.skipped_reason}")
            for warning in result.warnings:
                print(f"warning {result.person_id}: {warning}")

    _print_header("text-mfa-import-summary")
    print(f"batch={batch_dir.as_posix()}")
    print(
        f"mode={'dry-run' if args.dry_run else 'write'} fail_on_missing_output={args.fail_on_missing_output} "
        f"replace_existing={args.replace_existing}"
    )
    if args.language:
        print(f"language={describe_language_config(maybe_resolve_language_config(args.language))}")
    print(
        f"summary found={len(people)} imported={len(imported_results)} skipped={len(skipped_results)} "
        f"warnings={sum(len(result.warnings) for result in imported_results + skipped_results)} errors={len(error_messages)}"
    )
    return 1 if error_messages else 0


def main() -> int:
    try:
        return _run()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
