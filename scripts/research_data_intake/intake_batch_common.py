from __future__ import annotations

from dataclasses import dataclass
import filecmp
from pathlib import Path
import re
import shutil


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPORT_ROOT = REPO_ROOT / "scripts" / "research_data_intake" / "import"
BATCH_NAME_TOKEN = "batch"
SUPPORTED_TASKS = ("wordlist", "text", "interview")
SUPPORTED_TRANSFER_MODES = ("copy", "move", "symlink")

_BATCH_FILE_PATTERN = re.compile(
    r"^(?P<corpus>[A-Za-z]{2,})[-_](?P<speaker_marker>[A-Za-z])[-_](?P<person_number>\d{4})"
    r"_(?P<task>wordlist|text|interview)_(?P<stage>raw|processed)\.(?P<extension>wav|textgrid)$",
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

    @property
    def canonical_name(self) -> str:
        if self.file_kind == "wav":
            return f"{self.task}.wav"
        return f"{self.task}.TextGrid"


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
    if require_processed and not (path / "processed").is_dir():
        issues.append("missing required processed/ directory")
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
    file_kind = "wav" if extension == "wav" else "textgrid"
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
    )


def collect_batch_files(batch_dir: Path) -> tuple[list[ParsedBatchFile], list[str]]:
    parsed_files: list[ParsedBatchFile] = []
    warnings: list[str] = []
    for source_root in ("processed", "raw"):
        source_dir = batch_dir / source_root
        if not source_dir.exists():
            continue
        for path in sorted(source_dir.iterdir()):
            if not path.is_file():
                continue
            parsed = parse_batch_filename(path=path, source_root=source_root, batch_dir=batch_dir)
            if parsed is None:
                warnings.append(f"unparsed filename under {source_root}: {path.name}")
                continue
            if parsed.stage != source_root:
                warnings.append(
                    f"stage mismatch for {path.name}: filename stage={parsed.stage} folder={source_root}; skipped"
                )
                continue
            parsed_files.append(parsed)
    return parsed_files, warnings


def working_task_root(batch_dir: Path, person_id: str, task: str) -> Path:
    return batch_dir / "working" / person_id / task


def working_source_path(batch_dir: Path, person_id: str, task: str) -> Path:
    return working_task_root(batch_dir, person_id, task) / "source" / f"{task}.wav"


def working_alignment_path(batch_dir: Path, person_id: str, task: str) -> Path:
    return working_task_root(batch_dir, person_id, task) / "alignment" / f"{task}.TextGrid"


def working_text_mfa_corpus_dir(batch_dir: Path, person_id: str) -> Path:
    return working_task_root(batch_dir, person_id, "text") / "mfa_corpus"


def working_text_mfa_output_dir(batch_dir: Path, person_id: str) -> Path:
    return working_task_root(batch_dir, person_id, "text") / "mfa_output"


def working_text_manifest_path(batch_dir: Path, person_id: str) -> Path:
    return working_task_root(batch_dir, person_id, "text") / "mfa_manifest.json"


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
