from __future__ import annotations

from dataclasses import dataclass
import filecmp
from functools import lru_cache
import json
from pathlib import Path
import re
import shutil

from language_config import resolve_language_config


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPORT_ROOT = REPO_ROOT / "scripts" / "research_data_intake" / "import"
BATCH_NAME_TOKEN = "batch"
SUPPORTED_TASKS = ("wordlist", "text", "interview")
SUPPORTED_TRANSFER_MODES = ("copy", "move", "symlink")

IGNORED_BATCH_DIR_NAMES = {"working", "reports", "exports", "__pycache__", ".mfa_cache"}
WORKBOOK_EXTENSIONS = {".xlsx"}
ROLE_ALIASES = {
    "raw": "raw",
    "origin": "origin",
    "processed": "source",
    "source": "source",
    "amberscript": "alignment_source",
    "alignment": "alignment_source",
}
ROLE_PRIORITY = ("source", "raw", "origin", "alignment_source")

_PERSON_ID_PATTERN = re.compile(
    r"(?P<corpus>[A-Za-z]{2,})[-_](?P<speaker_marker>[A-Za-z])[-_](?P<person_number>\d{4})",
    re.IGNORECASE,
)
_TOKEN_SPLIT_PATTERN = re.compile(r"[^A-Za-z0-9]+")

_BATCH_FILE_PATTERN = re.compile(
    r"^(?P<corpus>[A-Za-z]{2,})[-_](?P<speaker_marker>[A-Za-z])[-_](?P<person_number>\d{4})"
    r"_(?P<task>wordlist|text|interview)_(?P<stage>raw|processed)\.(?P<extension>wav|textgrid|json)$",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ParsedBatchFile:
    source_path: Path
    source_root: str
    relative_source: str
    person_id: str
    task: str
    stage: str
    file_kind: str
    file_role: str

    @property
    def canonical_name(self) -> str:
        if self.file_kind == "wav":
            return f"{self.task}.wav"
        if self.file_kind == "json":
            return f"{self.task}.json"
        return f"{self.task}.TextGrid"


@dataclass(frozen=True, slots=True)
class BatchWorkbookCandidate:
    source_path: Path
    source_root: str
    relative_source: str


@dataclass(frozen=True, slots=True)
class BatchScanReport:
    workbooks: tuple[BatchWorkbookCandidate, ...]
    parsed_files: tuple[ParsedBatchFile, ...]
    warnings: tuple[str, ...]


@dataclass(slots=True)
class BatchTaskCandidates:
    processed_wav: list[ParsedBatchFile]
    raw_wav: list[ParsedBatchFile]
    processed_textgrid: list[ParsedBatchFile]
    raw_textgrid: list[ParsedBatchFile]
    processed_json: list[ParsedBatchFile]
    raw_json: list[ParsedBatchFile]
    source_wav: list[ParsedBatchFile]
    origin_wav: list[ParsedBatchFile]
    alignment_textgrid: list[ParsedBatchFile]
    alignment_json: list[ParsedBatchFile]
    interview_alignment_json: list[ParsedBatchFile]


@dataclass(frozen=True, slots=True)
class CatalogItemLookup:
    item_id: str
    item_number: str
    canonical_text: str
    label: str


def is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
    except ValueError:
        return False
    return True


def is_batch_directory_name(name: str) -> bool:
    return BATCH_NAME_TOKEN in name.strip().lower()


def batch_validation_issues(path: Path, require_processed: bool = True) -> list[str]:
    issues: list[str] = []
    if not is_batch_directory_name(path.name):
        issues.append(f"batch directory name must contain '{BATCH_NAME_TOKEN}'")
    return issues


def list_available_batch_dirs(require_processed: bool = True) -> list[Path]:
    if not IMPORT_ROOT.exists() or not IMPORT_ROOT.is_dir():
        return []

    available: list[Path] = []
    for candidate in sorted(IMPORT_ROOT.iterdir()):
        if not candidate.is_dir():
            continue
        if batch_validation_issues(candidate, require_processed=require_processed):
            continue
        available.append(candidate.resolve())
    return available


def _available_batch_hint(require_processed: bool) -> str:
    available_batches = list_available_batch_dirs(require_processed=require_processed)
    if not available_batches:
        return f"No processable batch directories are currently available below {IMPORT_ROOT}."
    joined = ", ".join(batch.name for batch in available_batches)
    return f"Available batch directories below {IMPORT_ROOT}: {joined}"


def resolve_batch_dir(batch_dir_arg: str, require_processed: bool = True) -> Path:
    raw_path = Path(batch_dir_arg)
    candidates: list[Path] = []
    if raw_path.is_absolute():
        candidates.append(raw_path)
    else:
        candidates.append(IMPORT_ROOT / batch_dir_arg)
        candidates.append(REPO_ROOT / batch_dir_arg)
        candidates.append(Path.cwd() / batch_dir_arg)

    seen: set[Path] = set()
    invalid_messages: list[str] = []
    import_root = IMPORT_ROOT.resolve()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if not resolved.exists() or not resolved.is_dir():
            continue
        if not is_relative_to(resolved, import_root):
            invalid_messages.append(f"Batch directory must stay under {IMPORT_ROOT}: {resolved}")
            continue
        issues = batch_validation_issues(resolved, require_processed=require_processed)
        if issues:
            invalid_messages.append(f"{resolved}: {'; '.join(issues)}")
            continue
        return resolved

    hint = _available_batch_hint(require_processed=require_processed)
    if invalid_messages:
        raise ValueError(f"Unusable batch directory {batch_dir_arg!r}. {' | '.join(invalid_messages)}. {hint}")
    raise FileNotFoundError(f"Unknown batch directory: {batch_dir_arg}. {hint}")


def canonical_person_id(corpus: str, speaker_marker: str, person_number: str) -> str:
    return f"{corpus.upper()}-{speaker_marker.upper()}-{person_number}"


def parse_batch_filename(path: Path, source_root: str, batch_dir: Path) -> ParsedBatchFile | None:
    match = _BATCH_FILE_PATTERN.match(path.name)
    if match is None:
        return None

    extension = str(match.group("extension") or "").lower()
    if extension == "wav":
        file_kind = "wav"
    elif extension == "json":
        file_kind = "json"
    else:
        file_kind = "textgrid"
    relative_source = str(path.relative_to(batch_dir)).replace("\\", "/")
    return ParsedBatchFile(
        source_path=path,
        source_root=source_root,
        relative_source=relative_source,
        person_id=canonical_person_id(
            corpus=str(match.group("corpus") or ""),
            speaker_marker=str(match.group("speaker_marker") or ""),
            person_number=str(match.group("person_number") or ""),
        ),
        task=str(match.group("task") or "").lower(),
        stage=str(match.group("stage") or "").lower(),
        file_kind=file_kind,
        file_role="source" if str(match.group("stage") or "").lower() == "processed" else "raw",
    )


def _relative_source_root(path: Path, batch_dir: Path) -> str:
    relative_parts = path.relative_to(batch_dir).parts
    if len(relative_parts) <= 1:
        return "batch_root"
    return relative_parts[0]


def _path_tokens(path: Path) -> list[str]:
    return [token for token in _TOKEN_SPLIT_PATTERN.split(path.stem.lower()) if token]


def _detect_person_id(path: Path) -> str | None:
    match = _PERSON_ID_PATTERN.search(path.stem)
    if match is None:
        return None
    return canonical_person_id(
        corpus=str(match.group("corpus") or ""),
        speaker_marker=str(match.group("speaker_marker") or ""),
        person_number=str(match.group("person_number") or ""),
    )


def _detect_task(tokens: list[str]) -> str | None:
    matches = [task for task in SUPPORTED_TASKS if task in tokens]
    if len(matches) != 1:
        return None
    return matches[0]


def _detect_role(tokens: list[str], *, extension: str) -> str | None:
    matched_roles = {ROLE_ALIASES[token] for token in tokens if token in ROLE_ALIASES}
    if extension == ".textgrid":
        return "alignment_source" if not matched_roles or matched_roles <= {"alignment_source", "source", "raw"} else None
    if extension == ".json":
        if not matched_roles:
            return "alignment_source"
        if matched_roles <= {"alignment_source", "source", "raw"}:
            return "alignment_source"
        return None
    if len(matched_roles) != 1:
        return None
    return next(iter(matched_roles))


def _stage_for_role(role: str) -> str:
    if role == "raw":
        return "raw"
    return "processed"


def _parse_drop_in_file(path: Path, batch_dir: Path) -> tuple[ParsedBatchFile | BatchWorkbookCandidate | None, str | None]:
    extension = path.suffix.lower()
    relative_source = str(path.relative_to(batch_dir)).replace("\\", "/")
    source_root = _relative_source_root(path, batch_dir)

    if path.name.startswith("~$"):
        return None, None
    if extension in WORKBOOK_EXTENSIONS:
        return BatchWorkbookCandidate(source_path=path, source_root=source_root, relative_source=relative_source), None
    if extension not in {".wav", ".json", ".textgrid"}:
        return None, f"unsupported intake file type skipped: {relative_source}"

    tokens = _path_tokens(path)
    person_id = _detect_person_id(path)
    if person_id is None:
        return None, f"unrecognized intake filename without person_id: {relative_source}"
    task = _detect_task(tokens)
    if task is None:
        return None, f"unrecognized intake filename without unique task token: {relative_source}"
    role = _detect_role(tokens, extension=extension)
    if role is None:
        return None, f"ambiguous or unsupported intake role in filename: {relative_source}"

    if extension == ".wav":
        file_kind = "wav"
        if role == "alignment_source":
            return None, f"invalid WAV alignment role in filename: {relative_source}"
    elif extension == ".json":
        if task == "wordlist":
            return None, f"unexpected JSON intake source for wordlist task: {relative_source}"
        file_kind = "json"
    else:
        if task == "interview":
            return None, f"unexpected TextGrid intake source for interview task: {relative_source}"
        file_kind = "textgrid"

    return (
        ParsedBatchFile(
            source_path=path,
            source_root=source_root,
            relative_source=relative_source,
            person_id=person_id,
            task=task,
            stage=_stage_for_role(role),
            file_kind=file_kind,
            file_role=role,
        ),
        None,
    )


def _iter_batch_files(batch_dir: Path) -> list[Path]:
    files: list[Path] = []
    _collect_batch_files(batch_dir, batch_dir, files)
    return sorted(files)


def _collect_batch_files(current: Path, batch_dir: Path, result: list[Path]) -> None:
    try:
        children = list(current.iterdir())
    except OSError:
        return
    for child in sorted(children):
        if child.is_dir():
            rel_parts = child.relative_to(batch_dir).parts
            if any(part in IGNORED_BATCH_DIR_NAMES for part in rel_parts):
                continue
            _collect_batch_files(child, batch_dir, result)
        else:
            try:
                if child.is_file():
                    result.append(child)
            except OSError:
                pass


def scan_import_batch(batch_dir: Path) -> BatchScanReport:
    parsed_files: list[ParsedBatchFile] = []
    workbook_candidates: list[BatchWorkbookCandidate] = []
    warnings: list[str] = []
    for path in _iter_batch_files(batch_dir):
        parsed, warning = _parse_drop_in_file(path, batch_dir)
        if warning is not None:
            warnings.append(warning)
            continue
        if parsed is None:
            continue
        if isinstance(parsed, BatchWorkbookCandidate):
            workbook_candidates.append(parsed)
        else:
            parsed_files.append(parsed)
    return BatchScanReport(
        workbooks=tuple(workbook_candidates),
        parsed_files=tuple(parsed_files),
        warnings=tuple(warnings),
    )


def collect_batch_files(batch_dir: Path) -> tuple[list[ParsedBatchFile], list[str]]:
    scan_report = scan_import_batch(batch_dir)
    return list(scan_report.parsed_files), list(scan_report.warnings)


def empty_batch_task_candidates() -> BatchTaskCandidates:
    return BatchTaskCandidates(
        processed_wav=[],
        raw_wav=[],
        processed_textgrid=[],
        raw_textgrid=[],
        processed_json=[],
        raw_json=[],
        source_wav=[],
        origin_wav=[],
        alignment_textgrid=[],
        alignment_json=[],
        interview_alignment_json=[],
    )


def build_batch_inventory(parsed_files: list[ParsedBatchFile]) -> dict[str, dict[str, BatchTaskCandidates]]:
    inventory: dict[str, dict[str, BatchTaskCandidates]] = {}
    for entry in parsed_files:
        person_inventory = inventory.setdefault(entry.person_id, {})
        task_bucket = person_inventory.setdefault(entry.task, empty_batch_task_candidates())
        if entry.file_kind == "wav":
            if entry.file_role == "raw":
                task_bucket.raw_wav.append(entry)
            elif entry.file_role == "origin":
                task_bucket.origin_wav.append(entry)
            elif entry.file_role == "source":
                task_bucket.source_wav.append(entry)
                task_bucket.processed_wav.append(entry)
        elif entry.file_kind == "textgrid":
            task_bucket.alignment_textgrid.append(entry)
            task_bucket.processed_textgrid.append(entry)
            if entry.file_role == "raw":
                task_bucket.raw_textgrid.append(entry)
        elif entry.file_kind == "json":
            task_bucket.alignment_json.append(entry)
            task_bucket.processed_json.append(entry)
            if entry.file_role == "raw":
                task_bucket.raw_json.append(entry)
            if entry.task == "interview":
                task_bucket.interview_alignment_json.append(entry)
    return inventory


def collect_batch_inventory(batch_dir: Path) -> tuple[dict[str, dict[str, BatchTaskCandidates]], list[str]]:
    parsed_files, warnings = collect_batch_files(batch_dir)
    return build_batch_inventory(parsed_files), warnings


def choose_unique_candidate(
    candidates: list[ParsedBatchFile],
    *,
    source_label: str,
    selection_label: str,
) -> tuple[ParsedBatchFile | None, str | None]:
    if not candidates:
        return None, None
    if len(candidates) > 1:
        joined = ", ".join(candidate.relative_source for candidate in candidates)
        return None, f"ambiguous {selection_label} candidates in {source_label}: {joined}"
    return candidates[0], None


def working_task_root(batch_dir: Path, person_id: str, task: str) -> Path:
    return batch_dir / "working" / person_id / task


def working_source_path(batch_dir: Path, person_id: str, task: str) -> Path:
    return working_task_root(batch_dir, person_id, task) / "source" / f"{task}.wav"


def working_alignment_path(batch_dir: Path, person_id: str, task: str) -> Path:
    return working_task_root(batch_dir, person_id, task) / "alignment" / f"{task}.TextGrid"


def working_alignment_json_path(batch_dir: Path, person_id: str, task: str) -> Path:
    return working_task_root(batch_dir, person_id, task) / "alignment" / f"{task}.json"


def working_text_mfa_corpus_dir(batch_dir: Path, person_id: str) -> Path:
    return working_task_root(batch_dir, person_id, "text") / "mfa_corpus"


def working_text_mfa_output_dir(batch_dir: Path, person_id: str) -> Path:
    return working_task_root(batch_dir, person_id, "text") / "mfa_output"


def working_text_manifest_path(batch_dir: Path, person_id: str) -> Path:
    return working_task_root(batch_dir, person_id, "text") / "mfa_manifest.json"


def working_text_mfa_state_path(batch_dir: Path, person_id: str) -> Path:
    return working_task_root(batch_dir, person_id, "text") / "mfa_state.json"


def working_intake_state_path(batch_dir: Path) -> Path:
    return batch_dir / "working" / ".intake_state.json"


def relative_posix_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def file_snapshot(path: Path, root: Path) -> dict[str, object]:
    stat_result = path.stat()
    return {
        "path": relative_posix_path(path, root),
        "size": stat_result.st_size,
        "mtime_ns": stat_result.st_mtime_ns,
        "hash": None,
    }


def read_json_file(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def person_id_language_slug(person_id: str) -> str:
    parts = person_id.strip().split("-")
    if not parts or not parts[0].strip():
        raise ValueError(f"Invalid person_id without language prefix: {person_id!r}")
    return resolve_language_config(parts[0].strip().lower()).corpus_slug


def person_id_speaker_marker(person_id: str) -> str | None:
    parts = person_id.strip().split("-")
    if len(parts) < 2 or not parts[1].strip():
        return None
    return parts[1].strip().upper()


def is_native_speaker_person_id(person_id: str) -> bool:
    return person_id_speaker_marker(person_id) == "N"


def task_catalog_path(language_slug: str, task_key: str) -> Path:
    return REPO_ROOT / "data" / "config" / "research_player" / language_slug / "task_catalogs" / f"{task_key}.json"


@lru_cache(maxsize=None)
def load_task_catalog_item_index(language_slug: str, task_key: str) -> dict[str, CatalogItemLookup]:
    catalog_path = task_catalog_path(language_slug, task_key)
    payload = read_json_file(catalog_path)
    items_payload = payload.get("items")
    if not isinstance(items_payload, list) or not items_payload:
        raise ValueError(f"Task catalog must contain a non-empty items list: {catalog_path}")

    catalog_index: dict[str, CatalogItemLookup] = {}
    for index, item_payload in enumerate(items_payload, start=1):
        if not isinstance(item_payload, dict):
            raise ValueError(f"Task catalog item {index} must be an object: {catalog_path}")
        item_id = item_payload.get("item_id")
        item_number = item_payload.get("item_number")
        text_value = item_payload.get("text")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError(f"Task catalog item_id must be a non-empty string at index {index}: {catalog_path}")
        if not isinstance(item_number, str) or not item_number.strip():
            raise ValueError(f"Task catalog item_number must be a non-empty string at index {index}: {catalog_path}")
        if not isinstance(text_value, str) or not text_value.strip():
            raise ValueError(f"Task catalog text must be a non-empty string at index {index}: {catalog_path}")
        label_value = item_payload.get("label")
        if not isinstance(label_value, str) or not label_value.strip():
            label_value = text_value
        normalized_item_id = item_id.strip()
        if normalized_item_id in catalog_index:
            raise ValueError(f"Duplicate task catalog item_id {normalized_item_id!r}: {catalog_path}")
        catalog_index[normalized_item_id] = CatalogItemLookup(
            item_id=normalized_item_id,
            item_number=item_number.strip(),
            canonical_text=text_value.strip(),
            label=label_value.strip(),
        )
    return catalog_index


def resolve_catalog_item(language_slug: str, task_key: str, item_id: str) -> CatalogItemLookup | None:
    return load_task_catalog_item_index(language_slug, task_key).get(item_id.strip())


def ensure_directory(path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    path.mkdir(parents=True, exist_ok=True)


def files_match(source: Path, target: Path) -> bool:
    if not target.exists() and not target.is_symlink():
        return False
    try:
        if target.is_symlink() and target.resolve() == source.resolve():
            return True
    except OSError:
        return False
    try:
        return filecmp.cmp(source, target, shallow=False)
    except OSError:
        return False


def replace_existing_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.exists():
        raise IsADirectoryError(f"Refusing to replace directory with file target: {path}")


def transfer_file(source: Path, target: Path, mode: str, dry_run: bool) -> None:
    if mode not in SUPPORTED_TRANSFER_MODES:
        raise ValueError(f"Unsupported transfer mode: {mode}")
    if dry_run:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if mode == "copy":
        shutil.copy2(source, target)
        return
    if mode == "move":
        shutil.move(str(source), str(target))
        return
    target.symlink_to(source.resolve())
