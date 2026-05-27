from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from typing import Any, Iterable, Sequence

from intake_batch_common import ParsedBatchFile


DEFAULT_LOCAL_ARCHIVE_ROOT = Path(r"C:\dev\promat_data_archive")
ARCHIVE_SESSION_SUBDIRS = (
    "secure",
    "raw",
    "source",
    "alignment_source",
    "runtime",
    "metadata",
    "reports",
)
FORBIDDEN_RUNTIME_SUFFIXES = {".wav", ".textgrid", ".xlsx", ".xlsm", ".xls", ".pdf"}
FORBIDDEN_RUNTIME_PARTS = {"secure", "raw", "origin", "source", "alignment_source", "working", "mfa_corpus", "mfa_output"}
ALLOWED_RUNTIME_PATTERNS = (
    re.compile(r"^metadata\.json$"),
    re.compile(r"^alignment/[^/]+\.json$"),
    re.compile(r"^derived/[^/]+\.mp3$"),
    re.compile(r"^items/[^/]+/[^/]+\.mp3$"),
)
ALLOWED_PROD_PACKAGE_PATTERNS = (
    re.compile(r"^sessions/[a-z]{2}/[^/]+/metadata\.json$"),
    re.compile(r"^sessions/[a-z]{2}/[^/]+/alignment/[^/]+\.json$"),
    re.compile(r"^sessions/[a-z]{2}/[^/]+/derived/[^/]+\.mp3$"),
    re.compile(r"^sessions/[a-z]{2}/[^/]+/items/[^/]+/[^/]+\.mp3$"),
    re.compile(r"^db/import_payload\.json$"),
    re.compile(r"^config/research_player/.+\.json$"),
    re.compile(r"^manifest\.json$"),
    re.compile(r"^checksums\.sha256$"),
    re.compile(r"^reports/[^/]+\.(md|txt|json)$"),
)


class IntakeStorageError(RuntimeError):
    """Raised for user-facing archive/runtime/package contract errors."""


@dataclass(frozen=True, slots=True)
class ArchiveWriteResult:
    archive_session_dir: Path
    manifest_path: Path
    report_path: Path
    runtime_files: tuple[str, ...]
    input_files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProdPackageBuildResult:
    output_dir: Path
    manifest_path: Path
    checksums_path: Path
    report_path: Path
    relative_files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BatchArchiveReportResult:
    batch_dir: Path
    import_payload_path: Path
    report_paths: tuple[Path, ...]
    checksums_path: Path


def get_local_archive_root() -> Path:
    configured = (os.getenv("PROMAT_LOCAL_ARCHIVE_ROOT") or "").strip()
    return Path(configured).expanduser() if configured else DEFAULT_LOCAL_ARCHIVE_ROOT


def archive_sessions_root(archive_root: Path | None = None) -> Path:
    return (archive_root or get_local_archive_root()) / "sessions"


def archive_batches_root(archive_root: Path | None = None) -> Path:
    return (archive_root or get_local_archive_root()) / "batches"


def archive_session_dir(language_code: str, session_id: str, archive_root: Path | None = None) -> Path:
    return archive_sessions_root(archive_root) / language_code.lower() / session_id


def relative_posix_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sorted_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file())


def _matches_any(relative_path: str, patterns: Sequence[re.Pattern[str]]) -> bool:
    return any(pattern.match(relative_path) for pattern in patterns)


def _has_forbidden_path_part(relative_path: str) -> str | None:
    for part in Path(relative_path).parts:
        if part in FORBIDDEN_RUNTIME_PARTS:
            return part
    return None


def validate_runtime_tree(session_dir: Path, *, required_tasks: Sequence[str] | None = None) -> list[str]:
    errors: list[str] = []
    if not session_dir.exists():
        return [f"missing runtime session directory: {session_dir}"]

    observed_task_artifacts: dict[str, set[str]] = {}
    for file_path in _sorted_files(session_dir):
        relative_path = relative_posix_path(file_path, session_dir)
        suffix = file_path.suffix.lower()
        forbidden_part = _has_forbidden_path_part(relative_path)
        has_error = False
        if forbidden_part is not None:
            errors.append(f"forbidden runtime path part '{forbidden_part}': {relative_path}")
            has_error = True
        if suffix in FORBIDDEN_RUNTIME_SUFFIXES:
            errors.append(f"forbidden runtime file type {suffix}: {relative_path}")
            has_error = True
        if has_error:
            continue
        if not _matches_any(relative_path, ALLOWED_RUNTIME_PATTERNS):
            errors.append(f"unsupported runtime file path: {relative_path}")
            continue

        parts = Path(relative_path).parts
        if len(parts) >= 2 and parts[0] in {"alignment", "derived"}:
            observed_task_artifacts.setdefault(Path(parts[1]).stem, set()).add(parts[0])

    if required_tasks:
        for task_key in required_tasks:
            artifact_groups = observed_task_artifacts.get(task_key, set())
            if "alignment" not in artifact_groups:
                errors.append(f"missing runtime alignment JSON for task {task_key}")
            if "derived" not in artifact_groups:
                errors.append(f"missing runtime derived MP3 for task {task_key}")
    return errors


def validate_archive_tree(session_archive_dir: Path) -> list[str]:
    errors: list[str] = []
    if not session_archive_dir.exists():
        return [f"missing archive session directory: {session_archive_dir}"]

    expected_top_level = set(ARCHIVE_SESSION_SUBDIRS)
    for child in session_archive_dir.iterdir():
        if child.name not in expected_top_level:
            errors.append(f"unexpected archive top-level path: {child.name}")

    manifest_path = session_archive_dir / "metadata" / "archive_manifest.json"
    if not manifest_path.exists():
        errors.append(f"missing archive manifest: {manifest_path}")

    runtime_dir = session_archive_dir / "runtime"
    errors.extend(f"archive runtime: {message}" for message in validate_runtime_tree(runtime_dir))
    return errors


def validate_prod_package(package_dir: Path) -> list[str]:
    errors: list[str] = []
    if not package_dir.exists():
        return [f"missing prod package directory: {package_dir}"]

    for file_path in _sorted_files(package_dir):
        relative_path = relative_posix_path(file_path, package_dir)
        suffix = file_path.suffix.lower()
        forbidden_part = _has_forbidden_path_part(relative_path)
        has_error = False
        if forbidden_part is not None:
            errors.append(f"forbidden prod package path part '{forbidden_part}': {relative_path}")
            has_error = True
        if suffix in FORBIDDEN_RUNTIME_SUFFIXES:
            errors.append(f"forbidden prod package file type {suffix}: {relative_path}")
            has_error = True
        if has_error:
            continue
        if not _matches_any(relative_path, ALLOWED_PROD_PACKAGE_PATTERNS):
            errors.append(f"unsupported prod package file path: {relative_path}")
    return errors


def _copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _runtime_output_files(session_dir: Path) -> list[Path]:
    files: list[Path] = []
    for file_path in _sorted_files(session_dir):
        relative_path = relative_posix_path(file_path, session_dir)
        if _matches_any(relative_path, ALLOWED_RUNTIME_PATTERNS):
            files.append(file_path)
    return files


def _file_manifest_entry(file_path: Path, *, relative_to: Path, role: str) -> dict[str, Any]:
    return {
        "path": relative_posix_path(file_path, relative_to),
        "role": role,
        "sha256": sha256_file(file_path),
        "size": file_path.stat().st_size,
    }


def _archive_target_relative(entry: ParsedBatchFile) -> str:
    extension = ".wav" if entry.file_kind == "wav" else ".json" if entry.file_kind == "json" else ".TextGrid"
    return f"{entry.file_role}/{entry.task}{extension}"


def write_sha256_checksums(root: Path, relative_paths: Iterable[str], *, output_path: Path) -> None:
    lines: list[str] = []
    for relative_path in sorted(relative_paths):
        file_path = root / relative_path.replace("/", os.sep)
        lines.append(f"{sha256_file(file_path)}  {relative_path}")
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_session_archive(
    *,
    session_dir: Path,
    language_code: str,
    session_id: str,
    person_id: str,
    source_batch: str,
    input_files: Sequence[ParsedBatchFile],
    warnings: Sequence[str],
    skipped_or_missing_artifacts: Sequence[dict[str, Any] | str] = (),
    importer_version: str,
    archive_root: Path | None = None,
    report_payload: dict[str, Any] | None = None,
) -> ArchiveWriteResult:
    archive_dir = archive_session_dir(language_code, session_id, archive_root)
    for subdir in ARCHIVE_SESSION_SUBDIRS:
        (archive_dir / subdir).mkdir(parents=True, exist_ok=True)

    # A raw WAV is used as the derivation source when no processed WAV exists for that task.
    # This matches the organizer's priority rule: processed WAV first, raw WAV as fallback.
    processed_wav_tasks: set[str] = {
        entry.task for entry in input_files if entry.file_kind == "wav" and entry.file_role == "source"
    }
    raw_wav_derivation_paths: set[Path] = {
        entry.source_path
        for entry in input_files
        if entry.file_kind == "wav" and entry.file_role == "raw" and entry.task not in processed_wav_tasks
    }

    # Build per-task audio role index for manifest documentation.
    task_wav_entries: dict[str, dict[str, Any]] = {}
    for entry in input_files:
        if entry.file_kind != "wav":
            continue
        role_info = task_wav_entries.setdefault(entry.task, {"raw_available": False, "processed_available": False})
        if entry.file_role == "raw":
            role_info["raw_available"] = True
            role_info["raw_file_path"] = f"raw/{entry.task}.wav"
        elif entry.file_role == "source":
            role_info["processed_available"] = True
            role_info["processed_file_path"] = f"source/{entry.task}.wav"
    for task, role_info in task_wav_entries.items():
        if task in processed_wav_tasks:
            role_info["source_audio_role"] = "processed"
            role_info["source_file_path"] = role_info.get("processed_file_path", f"source/{task}.wav")
        elif role_info["raw_available"]:
            role_info["source_audio_role"] = "raw"
            role_info["source_file_path"] = f"raw/{task}.wav"

    copied_input_paths: list[str] = []
    input_manifest_entries: list[dict[str, Any]] = []
    for entry in input_files:
        relative_target = _archive_target_relative(entry)
        target_path = archive_dir / relative_target.replace("/", os.sep)
        _copy_file(entry.source_path, target_path)
        copied_input_paths.append(relative_target)
        manifest_entry = _file_manifest_entry(target_path, relative_to=archive_dir, role=entry.file_role)
        if entry.source_path in raw_wav_derivation_paths:
            manifest_entry["source_file_role"] = "raw"
            manifest_entry["source_file_used_for_derivation"] = True
            # Also copy to source/ so derivation tooling always finds the WAV under source/.
            source_copy_relative = f"source/{entry.task}.wav"
            source_copy_path = archive_dir / source_copy_relative.replace("/", os.sep)
            _copy_file(entry.source_path, source_copy_path)
            copied_input_paths.append(source_copy_relative)
        input_manifest_entries.append(manifest_entry)

    runtime_manifest_entries: list[dict[str, Any]] = []
    copied_runtime_paths: list[str] = []
    for runtime_file in _runtime_output_files(session_dir):
        runtime_relative = relative_posix_path(runtime_file, session_dir)
        archive_relative = f"runtime/{runtime_relative}"
        target_path = archive_dir / archive_relative.replace("/", os.sep)
        _copy_file(runtime_file, target_path)
        copied_runtime_paths.append(archive_relative)
        runtime_manifest_entries.append(_file_manifest_entry(target_path, relative_to=archive_dir, role="runtime_output"))

    manifest = {
        "session_id": session_id,
        "person_id": person_id,
        "target_language": language_code.lower(),
        "source_batch": source_batch,
        "archived_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "importer_version": importer_version,
        "task_audio_roles": task_wav_entries,
        "input_files": input_manifest_entries,
        "generated_runtime_files": runtime_manifest_entries,
        "warnings": list(warnings),
        "skipped_or_missing_artifacts": list(skipped_or_missing_artifacts),
    }
    manifest_path = archive_dir / "metadata" / "archive_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "session_id": session_id,
        "source_batch": source_batch,
        "input_file_count": len(input_manifest_entries),
        "runtime_file_count": len(runtime_manifest_entries),
        "warnings": list(warnings),
        "skipped_or_missing_artifacts": list(skipped_or_missing_artifacts),
        "report_payload": report_payload or {},
    }
    report_path = archive_dir / "reports" / "import_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    archive_errors = validate_archive_tree(archive_dir)
    if archive_errors:
        raise IntakeStorageError("archive tree validation failed: " + "; ".join(archive_errors))

    return ArchiveWriteResult(
        archive_session_dir=archive_dir,
        manifest_path=manifest_path,
        report_path=report_path,
        runtime_files=tuple(sorted(copied_runtime_paths)),
        input_files=tuple(sorted(copied_input_paths)),
    )


def build_prod_upload_package(
    *,
    output_dir: Path,
    session_roots: Sequence[tuple[str, Path]],
    db_payload: dict[str, Any] | None = None,
    config_roots: Sequence[Path] = (),
    upload_id: str,
) -> ProdPackageBuildResult:
    if output_dir.exists():
        raise IntakeStorageError(f"refusing to overwrite existing prod package directory: {output_dir}")

    relative_files: list[str] = []
    for language_code, session_dir in session_roots:
        runtime_errors = validate_runtime_tree(session_dir)
        if runtime_errors:
            raise IntakeStorageError(
                f"cannot package invalid runtime session {session_dir.name}: " + "; ".join(runtime_errors)
            )
        for runtime_file in _runtime_output_files(session_dir):
            runtime_relative = relative_posix_path(runtime_file, session_dir)
            package_relative = f"sessions/{language_code.lower()}/{session_dir.name}/{runtime_relative}"
            _copy_file(runtime_file, output_dir / package_relative.replace("/", os.sep))
            relative_files.append(package_relative)

    if db_payload is not None:
        db_payload_path = output_dir / "db" / "import_payload.json"
        db_payload_path.parent.mkdir(parents=True, exist_ok=True)
        db_payload_path.write_text(json.dumps(db_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        relative_files.append("db/import_payload.json")

    for config_root in config_roots:
        for config_file in sorted(path for path in config_root.rglob("*.json") if path.is_file()):
            package_relative = f"config/research_player/{relative_posix_path(config_file, config_root)}"
            _copy_file(config_file, output_dir / package_relative.replace("/", os.sep))
            relative_files.append(package_relative)

    report_path = output_dir / "reports" / "upload_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "\n".join(
            [
                f"# PROMAT Upload Package {upload_id}",
                "",
                f"Sessions: {', '.join(session_dir.name for _, session_dir in session_roots) or 'none'}",
                f"Files: {len(relative_files)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    relative_files.append("reports/upload_report.md")

    manifest_path = output_dir / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    final_package_files = sorted([*relative_files, "manifest.json", "checksums.sha256"])
    manifest_payload = {
        "upload_id": upload_id,
        "built_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "sessions": [session_dir.name for _, session_dir in session_roots],
        "files": final_package_files,
    }
    manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    relative_files.append("manifest.json")

    checksums_path = output_dir / "checksums.sha256"
    write_sha256_checksums(output_dir, sorted(relative_files), output_path=checksums_path)
    relative_files.append("checksums.sha256")

    package_errors = validate_prod_package(output_dir)
    if package_errors:
        raise IntakeStorageError("prod package validation failed: " + "; ".join(package_errors))

    return ProdPackageBuildResult(
        output_dir=output_dir,
        manifest_path=manifest_path,
        checksums_path=checksums_path,
        report_path=report_path,
        relative_files=tuple(sorted(relative_files)),
    )


def write_secure_person_export(
    *,
    archive_session_dir: Path,
    person_id: str,
    secure_data: dict[str, Any],
    consent_pdf_source: Path | None = None,
    questionnaire_pdf_source: Path | None = None,
) -> None:
    """Write secure person intake data to the local archive. Never call for runtime or prod packages."""
    secure_dir = archive_session_dir / "secure"
    secure_dir.mkdir(parents=True, exist_ok=True)
    export_payload = {"person_id": person_id, **secure_data}
    secure_json_path = secure_dir / "secure_person_intake.json"
    secure_json_path.write_text(json.dumps(export_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if consent_pdf_source is not None and consent_pdf_source.exists():
        _copy_file(consent_pdf_source, secure_dir / "consent" / consent_pdf_source.name)
    if questionnaire_pdf_source is not None and questionnaire_pdf_source.exists():
        _copy_file(questionnaire_pdf_source, secure_dir / "questionnaire" / questionnaire_pdf_source.name)


def write_batch_archive_reports(
    *,
    batch_name: str,
    import_payload: dict[str, Any],
    intake_report_markdown: str,
    validation_report_markdown: str,
    archive_report_markdown: str,
    run_notes: Sequence[str] = (),
    archive_root: Path | None = None,
) -> BatchArchiveReportResult:
    batch_dir = archive_batches_root(archive_root) / batch_name
    batch_dir.mkdir(parents=True, exist_ok=True)

    if run_notes:
        import_payload = dict(import_payload)
        import_payload["run_notes"] = list(run_notes)

    import_payload_path = batch_dir / "import_payload.json"
    import_payload_path.write_text(json.dumps(import_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    intake_report_path = batch_dir / "intake_report.md"
    intake_report_path.write_text(intake_report_markdown, encoding="utf-8")

    validation_report_path = batch_dir / "validation_report.md"
    validation_report_path.write_text(validation_report_markdown, encoding="utf-8")

    archive_report_path = batch_dir / "archive_report.md"
    archive_report_path.write_text(archive_report_markdown, encoding="utf-8")

    checksums_path = batch_dir / "checksums.sha256"
    relative_paths = (
        "import_payload.json",
        "intake_report.md",
        "validation_report.md",
        "archive_report.md",
    )
    write_sha256_checksums(batch_dir, relative_paths, output_path=checksums_path)

    return BatchArchiveReportResult(
        batch_dir=batch_dir,
        import_payload_path=import_payload_path,
        report_paths=(intake_report_path, validation_report_path, archive_report_path),
        checksums_path=checksums_path,
    )
