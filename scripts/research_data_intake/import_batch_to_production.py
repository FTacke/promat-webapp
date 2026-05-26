from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Sequence

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session, selectinload, sessionmaker


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_SRC = REPO_ROOT / "app" / "src"
SCRIPT_ROOT = Path(__file__).resolve().parent
ALIGNMENT_EXPORT_ROOT = SCRIPT_ROOT / "alignment_export"
IMPORT_SCRIPT_ROOT = SCRIPT_ROOT / "import"
APP_SCRIPT_ROOT = REPO_ROOT / "app" / "scripts"
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))
if str(ALIGNMENT_EXPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(ALIGNMENT_EXPORT_ROOT))
if str(IMPORT_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPORT_SCRIPT_ROOT))
if str(APP_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_SCRIPT_ROOT))

os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app.config import DEFAULT_DEV_DATABASE_URL  # noqa: E402
from app.research_capabilities import RESEARCH_TASK_KEYS, get_research_task_capability, is_task_available_for_speaker_type  # noqa: E402
from app.research_metadata import ResearchPerson, ResearchSession, ResearchSessionExposure  # noqa: E402
from app.runtime_paths import get_sessions_root  # noqa: E402
from apply_auth_migration import apply_postgres_migration  # noqa: E402
from alignment_export.import_text_mfa_alignment import import_text_mfa_alignment_for_person  # noqa: E402
from alignment_export.prepare_text_mfa_corpus import prepare_text_mfa_for_person  # noqa: E402
from alignment_export.run_text_mfa import check_mfa_available, run_text_mfa_for_person  # noqa: E402
from audio_conversion.ffmpeg_audio import create_full_task_mp3, ensure_media_tools  # noqa: E402
from intake_batch_common import (  # noqa: E402
    build_batch_inventory,
    choose_unique_candidate,
    collect_batch_files,
    files_match,
    is_native_speaker_person_id,
    resolve_batch_dir,
    scan_import_batch,
    working_alignment_path,
    working_intake_state_path,
    working_source_path,
    working_task_root,
)
from intake_storage import validate_runtime_tree, write_batch_archive_reports, write_secure_person_export, write_session_archive  # noqa: E402
from intake_workbook_reader import IntakeExposureRow, IntakePersonRow, IntakeSessionRow, SecurePersonIntakeRow, SessionLinkKey, load_intake_workbook  # noqa: E402
from language_config import resolve_language_config  # noqa: E402
from organize_batch_working_tree import organize_batch_working_tree  # noqa: E402
from produce_text_artifacts import produce_text_artifacts  # noqa: E402
from produce_wordlist_artifacts import produce_wordlist_artifacts  # noqa: E402


class ProductionImportError(RuntimeError):
    """Raised for expected user-facing production import failures."""


@dataclass(frozen=True, slots=True)
class TaskSyncPlan:
    task_key: str
    action: str
    status: str
    reason: str | None
    working_root: Path
    source_wav: Path | None
    alignment_textgrid: Path | None
    working_alignment_json: Path | None


@dataclass(frozen=True, slots=True)
class RawSyncPlan:
    task_key: str
    action: str
    status: str
    reason: str | None
    source_path: Path | None
    target_path: Path
    relative_source: str | None


@dataclass(frozen=True, slots=True)
class SessionImportPlan:
    person: IntakePersonRow
    session: IntakeSessionRow
    exposures: tuple[IntakeExposureRow, ...]
    secure_person: SecurePersonIntakeRow | None
    source_batch: str
    mode_action: str
    reason: str | None
    session_id_change_from: str | None
    existing_db_session_id: str | None
    target_session_dir: Path
    existing_session_dir: Path | None
    target_runtime_exists: bool
    task_plans: tuple[TaskSyncPlan, ...]
    raw_plans: tuple[RawSyncPlan, ...]
    archive_inputs: tuple[Any, ...]
    warnings: tuple[str, ...]
    conflicts: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ImportRunSummary:
    processed_sessions: int
    create_count: int
    update_count: int
    skip_count: int
    conflict_count: int
    task_sync_count: int
    task_available_count: int
    raw_sync_count: int
    raw_keep_count: int
    raw_missing_count: int
    raw_conflict_count: int


@dataclass(slots=True)
class SessionWorkspace:
    target_dir: Path
    seed_dir: Path | None
    backup_dir: Path | None = None
    created_target: bool = False
    copied_from_seed: bool = False
    cleanup_seed_dir: Path | None = None

    def prepare(self) -> None:
        if self.seed_dir is not None and self.seed_dir.exists() and self.seed_dir != self.target_dir:
            if self.target_dir.exists():
                raise ProductionImportError(
                    f"Refusing to copy renamed session into existing target directory: {self.target_dir}"
                )
            shutil.copytree(self.seed_dir, self.target_dir)
            self.created_target = True
            self.copied_from_seed = True
            self.cleanup_seed_dir = self.seed_dir
        elif self.target_dir.exists():
            backup_root = Path(tempfile.mkdtemp(prefix="promat-session-backup-"))
            self.backup_dir = backup_root / self.target_dir.name
            shutil.copytree(self.target_dir, self.backup_dir)
        else:
            self.target_dir.mkdir(parents=True, exist_ok=True)
            self.created_target = True
        for relative_dir in ("alignment", "derived", "items"):
            (self.target_dir / relative_dir).mkdir(parents=True, exist_ok=True)

    def commit(self) -> None:
        if self.backup_dir is not None:
            shutil.rmtree(self.backup_dir.parent, ignore_errors=True)
        if self.cleanup_seed_dir is not None and self.cleanup_seed_dir.exists():
            shutil.rmtree(self.cleanup_seed_dir)

    def rollback(self) -> None:
        if self.created_target and self.target_dir.exists():
            shutil.rmtree(self.target_dir, ignore_errors=True)
        elif self.backup_dir is not None and self.backup_dir.exists():
            if self.target_dir.exists():
                shutil.rmtree(self.target_dir, ignore_errors=True)
            shutil.copytree(self.backup_dir, self.target_dir)
        if self.backup_dir is not None:
            shutil.rmtree(self.backup_dir.parent, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a research intake batch into production runtime sessions and metadata."
    )
    parser.add_argument("--batch-dir", "--batch", dest="batch_dir", required=True, help="Batch directory below scripts/research_data_intake/import/.")
    parser.add_argument("--workbook", help="Optional explicit intake workbook path; defaults to recursive workbook discovery inside the batch.")
    parser.add_argument("--target-language", default="es", help="Target language code or slug. Default: es.")
    parser.add_argument("--person-id", action="append", dest="person_ids", metavar="PERSON_ID", help="Optional person filter; can be repeated for multiple IDs.")
    parser.add_argument("--archive-root", help="Optional explicit local archive root; defaults to PROMAT_LOCAL_ARCHIVE_ROOT.")
    parser.add_argument("--runtime-root", help="Optional explicit PROMAT runtime root that contains data/ and public/.")
    parser.add_argument("--run-working", action="store_true", help="Build or refresh the batch-local working tree for the in-scope people before importing runtime artifacts.")
    parser.add_argument("--run-mfa", action="store_true", help="Prepare text MFA inputs, run MFA, and import working text alignment JSON before runtime sync.")
    parser.add_argument("--cleanup-working-on-success", action="store_true", help="Remove the in-scope batch-local working tree after a successful import run.")
    parser.add_argument("--mfa-executable", default="mfa", help="MFA executable name or absolute path for --run-mfa. Default: mfa.")
    parser.add_argument(
        "--auth-database-url",
        help="Optional AUTH database URL; defaults to AUTH_DATABASE_URL or the active development default.",
    )
    parser.add_argument(
        "--create-missing-only",
        action="store_true",
        help="Create only missing session imports and skip existing DB/runtime sessions entirely.",
    )
    parser.add_argument(
        "--update-metadata",
        action="store_true",
        help="Explicitly update DB rows and metadata.json for existing sessions. This is the default when --create-missing-only is not used.",
    )
    parser.add_argument(
        "--sync-tasks",
        action="store_true",
        help="Delegate task artifact production to wordlist/text when working sources are ready.",
    )
    parser.add_argument(
        "--sync-raw-only",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--allow-session-id-change",
        action="store_true",
        help="Allow a workbook metadata change that derives a new session_id for an existing (person_id, session_ref) slot.",
    )
    parser.add_argument(
        "--validate-wordlist-labels",
        choices=("off", "warn", "fail"),
        default="off",
        help="Forwarded to the reusable wordlist processor when --sync-tasks is enabled.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show creates, updates, skips, and conflicts without writing files or DB rows.")
    return parser.parse_args()


def _discover_workbook_path(batch_dir: Path, explicit_workbook: str | None) -> Path:
    if explicit_workbook:
        workbook_path = Path(explicit_workbook)
        if not workbook_path.is_absolute():
            workbook_path = (batch_dir / explicit_workbook).resolve()
        if not workbook_path.exists() or not workbook_path.is_file():
            raise ProductionImportError(f"Unknown workbook path: {workbook_path}")
        return workbook_path

    scan_report = scan_import_batch(batch_dir)
    workbook_candidates = sorted(candidate.source_path for candidate in scan_report.workbooks)
    if not workbook_candidates:
        raise ProductionImportError(f"No intake workbook (*.xlsx) found in {batch_dir}")
    if len(workbook_candidates) > 1:
        joined = ", ".join(path.name for path in workbook_candidates)
        raise ProductionImportError(
            f"Multiple workbook candidates found in {batch_dir}; use --workbook explicitly. Found: {joined}"
        )
    return workbook_candidates[0]


def _resolve_database_url(explicit_value: str | None) -> str:
    value = (explicit_value or os.getenv("AUTH_DATABASE_URL") or DEFAULT_DEV_DATABASE_URL).strip()
    if not value:
        raise ProductionImportError("AUTH database URL is required.")
    return value


def _resolve_optional_path(value: str | None) -> Path | None:
    if value is None or not value.strip():
        return None
    path = Path(value)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def _apply_runtime_overrides(args: argparse.Namespace) -> None:
    runtime_root = _resolve_optional_path(args.runtime_root)
    archive_root = _resolve_optional_path(args.archive_root)
    if runtime_root is not None:
        os.environ["PROMAT_RUNTIME_ROOT"] = str(runtime_root)
    if archive_root is not None:
        os.environ["PROMAT_LOCAL_ARCHIVE_ROOT"] = str(archive_root)


def _text_task_catalog_path(target_language: str) -> Path:
    language_slug = resolve_language_config(target_language).corpus_slug
    return REPO_ROOT / "data" / "config" / "research_player" / language_slug / "task_catalogs" / "text.json"


def _ensure_db_schema(database_url: str, *, should_write_db: bool, dry_run: bool) -> str | None:
    if not should_write_db or dry_run:
        return None
    if not database_url.startswith("postgresql"):
        return None
    os.environ["AUTH_DATABASE_URL"] = database_url
    apply_postgres_migration(reset=False)
    return "Applied PostgreSQL auth/research metadata migrations before DB upsert."


def _run_working_pipeline(
    *,
    batch_dir: Path,
    person_ids: set[str] | None,
    dry_run: bool,
) -> dict[str, object]:
    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=dry_run,
        replace_existing=True,
        force_tasks=set(),
        person_ids=person_ids or None,
    )
    summary = report_payload.get("summary")
    if isinstance(summary, dict) and int(summary.get("errors") or 0) > 0:
        raise ProductionImportError(
            f"working-tree build reported errors for {batch_dir.name}; see task statuses in the organizer report"
        )
    return report_payload


def _run_text_pipeline(
    *,
    batch_dir: Path,
    person_id: str,
    target_language: str,
    mfa_executable: str,
    dry_run: bool,
) -> list[str]:
    text_catalog_path = _text_task_catalog_path(target_language)
    if not text_catalog_path.exists():
        raise ProductionImportError(f"Missing text task catalog for MFA prep: {text_catalog_path}")
    source_wav = batch_dir / "working" / person_id / "text" / "source" / "text.wav"
    source_textgrid = batch_dir / "working" / person_id / "text" / "alignment" / "text.TextGrid"
    if not source_wav.exists() or source_wav.stat().st_size == 0 or not source_textgrid.exists() or source_textgrid.stat().st_size == 0:
        if dry_run:
            return [
                f"Planned text MFA skip for {person_id}: working text inputs are not present; task would remain missing unless existing runtime artifacts are available."
            ]
        return [
            f"Skipped text MFA for {person_id}: working text inputs are not present; task will remain missing unless existing runtime artifacts are available."
        ]
    prepare_result = prepare_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id=person_id,
        text_source_json=text_catalog_path,
        cli_language=target_language,
        dry_run=dry_run,
        replace_existing=True,
    )
    notes = [f"Prepared text MFA corpus for {person_id}: segments={prepare_result['segments']}"]
    prepare_warnings = prepare_result.get("warnings")
    if isinstance(prepare_warnings, list):
        for warning in prepare_warnings:
            if isinstance(warning, str) and warning.strip():
                notes.append(f"Text MFA prep warning for {person_id}: {warning}")
    if dry_run:
        notes.append(f"Planned MFA for {person_id}: executable={mfa_executable}")
        notes.append(f"Planned working text alignment import for {person_id} after MFA outputs are available.")
        return notes
    mfa_result = run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id=person_id,
        language=target_language,
        mfa_executable=mfa_executable,
        dry_run=dry_run,
    )
    import_result = import_text_mfa_alignment_for_person(
        batch_dir=batch_dir,
        person_id=person_id,
        cli_language=target_language,
        dry_run=dry_run,
        fail_on_missing_output=True,
        replace_existing=True,
    )
    if import_result.skipped_reason is not None:
        raise ProductionImportError(f"text MFA import skipped unexpectedly for {person_id}: {import_result.skipped_reason}")
    notes.append(f"Ran MFA for {person_id}: executable={mfa_result['mfa_executable']} version={mfa_result['mfa_version']}")
    notes.append(f"Imported working text alignment for {person_id}: items={import_result.item_count} tokens={import_result.token_count}")
    return notes


def _cleanup_working_people(batch_dir: Path, person_ids: Sequence[str]) -> str:
    working_root = batch_dir / "working"
    removed_people: list[str] = []
    for person_id in person_ids:
        person_root = working_root / person_id
        if person_root.exists():
            shutil.rmtree(person_root)
            removed_people.append(person_id)

    state_path = working_intake_state_path(batch_dir)
    if state_path.exists():
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        persons_payload = payload.get("persons")
        if isinstance(persons_payload, dict):
            for person_id in person_ids:
                persons_payload.pop(person_id, None)
            if persons_payload:
                state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            else:
                state_path.unlink()

    if working_root.exists() and not any(working_root.iterdir()):
        shutil.rmtree(working_root)
        return "Removed person-scoped working trees and deleted the now-empty batch working/ root."
    if removed_people:
        return "Removed person-scoped working trees: " + ", ".join(sorted(removed_people))
    return "No working tree cleanup was necessary."


def _normalize_text_list(values: tuple[str, ...]) -> str | None:
    if not values:
        return None
    return "; ".join(values)


def _task_label(task_key: str) -> str:
    capability = get_research_task_capability(task_key)
    if capability is None:
        return task_key
    return capability.long_label("de")


def _task_status_from_session_dir(session_dir: Path, task_key: str) -> bool:
    alignment_json_path = session_dir / "alignment" / f"{task_key}.json"
    derived_mp3_path = session_dir / "derived" / f"{task_key}.mp3"
    return alignment_json_path.exists() or derived_mp3_path.exists()


def _archive_inputs_for_person(parsed_batch_files: list[Any], person_id: str) -> tuple[tuple[Any, ...], tuple[str, ...]]:
    selected = [entry for entry in parsed_batch_files if entry.person_id == person_id]
    seen_keys: dict[tuple[str, str, str], Any] = {}
    conflicts: list[str] = []
    for entry in selected:
        key = (entry.task, entry.file_role, entry.file_kind)
        if key in seen_keys:
            conflicts.append(
                f"multiple archive inputs for {person_id} {entry.task}/{entry.file_role}/{entry.file_kind}: "
                f"{seen_keys[key].relative_source}, {entry.relative_source}"
            )
            continue
        seen_keys[key] = entry
    return tuple(sorted(seen_keys.values(), key=lambda item: (item.task, item.file_role, item.file_kind))), tuple(conflicts)


def _task_not_expected_status(task_key: str, person_id: str, speaker_type: str | None) -> tuple[str, str] | None:
    normalized_speaker_type = (speaker_type or "").strip()
    if normalized_speaker_type:
        if is_task_available_for_speaker_type(task_key, normalized_speaker_type):
            return None
        if task_key == "interview" and normalized_speaker_type == "native_speaker":
            return ("not_expected_for_native_speaker", "interview is not expected for native_speaker")
        return None
    if task_key == "interview" and is_native_speaker_person_id(person_id):
        return ("not_expected_for_native_speaker", "interview is not expected for native_speaker")
    return None


def _documented_tasks_from_session_dir(
    session_dir: Path,
    *,
    person_id: str | None = None,
    speaker_type: str | None = None,
) -> tuple[str, ...]:
    documented: list[str] = []
    for task_key in RESEARCH_TASK_KEYS:
        if person_id is not None and _task_not_expected_status(task_key, person_id, speaker_type) is not None:
            continue
        if _task_status_from_session_dir(session_dir, task_key):
            documented.append(task_key)
    return tuple(documented)


def _detect_working_task(
    batch_dir: Path,
    person_id: str,
    task_key: str,
    sync_tasks: bool,
    speaker_type: str | None,
) -> TaskSyncPlan:
    task_root = working_task_root(batch_dir, person_id, task_key)
    source_wav = working_source_path(batch_dir, person_id, task_key)
    alignment_textgrid = working_alignment_path(batch_dir, person_id, task_key)
    working_alignment_json = task_root / "alignment" / f"{task_key}.json"

    not_expected = _task_not_expected_status(task_key, person_id, speaker_type)
    if not_expected is not None:
        status, reason = not_expected
        return TaskSyncPlan(
            task_key=task_key,
            action="skip",
            status=status,
            reason=reason,
            working_root=task_root,
            source_wav=None,
            alignment_textgrid=None,
            working_alignment_json=None,
        )

    if not task_root.exists():
        return TaskSyncPlan(
            task_key=task_key,
            action="skip",
            status="missing",
            reason="working task directory missing",
            working_root=task_root,
            source_wav=None,
            alignment_textgrid=None,
            working_alignment_json=None,
        )

    if task_key == "wordlist":
        if not source_wav.exists() or not alignment_textgrid.exists():
            return TaskSyncPlan(
                task_key=task_key,
                action="skip",
                status="incomplete",
                reason="wordlist source/alignment missing",
                working_root=task_root,
                source_wav=source_wav if source_wav.exists() else None,
                alignment_textgrid=alignment_textgrid if alignment_textgrid.exists() else None,
                working_alignment_json=None,
            )
        return TaskSyncPlan(
            task_key=task_key,
            action="sync" if sync_tasks else "available",
            status="ready",
            reason=None,
            working_root=task_root,
            source_wav=source_wav,
            alignment_textgrid=alignment_textgrid,
            working_alignment_json=None,
        )

    if task_key == "text":
        if not source_wav.exists() or not working_alignment_json.exists():
            return TaskSyncPlan(
                task_key=task_key,
                action="skip",
                status="incomplete",
                reason="text source/alignment JSON missing",
                working_root=task_root,
                source_wav=source_wav if source_wav.exists() else None,
                alignment_textgrid=alignment_textgrid if alignment_textgrid.exists() else None,
                working_alignment_json=working_alignment_json if working_alignment_json.exists() else None,
            )
        return TaskSyncPlan(
            task_key=task_key,
            action="sync" if sync_tasks else "available",
            status="ready",
            reason=None,
            working_root=task_root,
            source_wav=source_wav,
            alignment_textgrid=alignment_textgrid if alignment_textgrid.exists() else None,
            working_alignment_json=working_alignment_json,
        )

    interview_source = source_wav.exists()
    interview_alignment_json = working_alignment_json.exists()
    if not interview_source and not interview_alignment_json:
        return TaskSyncPlan(
            task_key=task_key,
            action="skip",
            status="missing",
            reason="no interview working inputs",
            working_root=task_root,
            source_wav=None,
            alignment_textgrid=None,
            working_alignment_json=None,
        )
    if not interview_source or not interview_alignment_json:
        return TaskSyncPlan(
            task_key=task_key,
            action="skip",
            status="incomplete",
            reason="interview source/alignment JSON missing",
            working_root=task_root,
            source_wav=source_wav if interview_source else None,
            alignment_textgrid=None,
            working_alignment_json=working_alignment_json if interview_alignment_json else None,
        )
    return TaskSyncPlan(
        task_key=task_key,
        action="sync" if sync_tasks else "available",
        status="ready",
        reason=None,
        working_root=task_root,
        source_wav=source_wav,
        alignment_textgrid=None,
        working_alignment_json=working_alignment_json,
    )


def _existing_runtime_dirs(corpus_language: str) -> dict[str, Path]:
    runtime_root = get_sessions_root() / corpus_language
    if not runtime_root.exists():
        return {}
    return {path.name: path for path in runtime_root.iterdir() if path.is_dir()}


def _build_import_plans(
    *,
    batch_dir: Path,
    workbook_data,
    create_missing_only: bool,
    sync_tasks: bool,
    sync_raw_only: bool,
    allow_session_id_change: bool,
    db_session: Session,
) -> tuple[list[SessionImportPlan], list[str]]:
    parsed_batch_files, batch_warnings = collect_batch_files(batch_dir)
    batch_inventory = build_batch_inventory(parsed_batch_files)
    sessions = db_session.scalars(
        select(ResearchSession).options(selectinload(ResearchSession.exposures)).where(
            ResearchSession.target_language == workbook_data.target_language
        )
    ).all()
    by_slot = {(row.person_id, row.session_ref): row for row in sessions}
    by_session_id = {row.session_id: row for row in sessions}
    runtime_dirs = _existing_runtime_dirs(workbook_data.sessions[0].corpus_language) if workbook_data.sessions else {}
    plan_warnings: list[str] = list(batch_warnings)
    plans: list[SessionImportPlan] = []

    for workbook_session in workbook_data.sessions:
        person = workbook_data.persons[workbook_session.person_id]
        exposures = workbook_data.exposures_by_key.get(
            SessionLinkKey(person_id=workbook_session.person_id, session_ref=workbook_session.session_ref),
            tuple(),
        )
        slot_key = (workbook_session.person_id, workbook_session.session_ref)
        existing_slot = by_slot.get(slot_key)
        existing_by_id = by_session_id.get(workbook_session.session_id)
        session_id_change_from: str | None = None
        conflicts: list[str] = []
        warnings: list[str] = []

        if existing_slot is not None and existing_slot.session_id != workbook_session.session_id:
            if not allow_session_id_change:
                conflicts.append(
                    f"session_id would change from {existing_slot.session_id} to {workbook_session.session_id}"
                )
            elif existing_by_id is not None and existing_by_id.session_id != existing_slot.session_id:
                conflicts.append(
                    f"derived session_id {workbook_session.session_id} already belongs to another imported session"
                )
            else:
                session_id_change_from = existing_slot.session_id
                warnings.append(
                    f"session_id change allowed for {workbook_session.person_id}/{workbook_session.session_ref}: {existing_slot.session_id} -> {workbook_session.session_id}"
                )

        if existing_by_id is not None and (existing_by_id.person_id, existing_by_id.session_ref) != slot_key:
            conflicts.append(
                f"derived session_id {workbook_session.session_id} already exists for {existing_by_id.person_id}/{existing_by_id.session_ref}"
            )

        existing_runtime_dir = None
        if session_id_change_from is not None:
            existing_runtime_dir = runtime_dirs.get(session_id_change_from)
        elif existing_slot is not None:
            existing_runtime_dir = runtime_dirs.get(existing_slot.session_id)
        elif existing_by_id is not None:
            existing_runtime_dir = runtime_dirs.get(existing_by_id.session_id)

        target_session_dir = (get_sessions_root() / workbook_session.corpus_language / workbook_session.session_id).resolve()
        target_runtime_exists = target_session_dir.exists()

        if sync_raw_only and not target_runtime_exists:
            mode_action = "skip"
            reason = "raw-only mode requires an existing runtime session directory"
        elif create_missing_only and (existing_slot is not None or existing_by_id is not None or target_runtime_exists):
            mode_action = "skip"
            reason = "existing session already present; create-missing-only requested"
        elif conflicts:
            mode_action = "conflict"
            reason = "; ".join(conflicts)
        elif existing_slot is None and existing_by_id is None and not target_runtime_exists:
            mode_action = "create"
            reason = None
        else:
            mode_action = "update"
            reason = None
            if target_runtime_exists and existing_slot is None and existing_by_id is None:
                warnings.append("runtime session directory exists without research_sessions row; importer will attach DB metadata")
                plan_warnings.append(
                    f"{workbook_session.session_id}: runtime directory exists without DB metadata; treated as update"
                )

        task_plans = tuple(
            _detect_working_task(
                batch_dir=batch_dir,
                person_id=workbook_session.person_id,
                task_key=task_key,
                sync_tasks=sync_tasks,
                speaker_type=person.speaker_type,
            )
            for task_key in RESEARCH_TASK_KEYS
        )
        archive_inputs, archive_conflicts = _archive_inputs_for_person(parsed_batch_files, workbook_session.person_id)
        conflicts.extend(archive_conflicts)
        raw_plans = tuple()
        if mode_action not in {"skip", "conflict"} and conflicts:
            mode_action = "conflict"
            reason = "; ".join(conflicts)
        if mode_action in {"skip", "conflict"}:
            task_plans = tuple(
                TaskSyncPlan(
                    task_key=task_plan.task_key,
                    action="skip",
                    status=task_plan.status,
                    reason=task_plan.reason if task_plan.reason is not None else f"session {mode_action}",
                    working_root=task_plan.working_root,
                    source_wav=task_plan.source_wav,
                    alignment_textgrid=task_plan.alignment_textgrid,
                    working_alignment_json=task_plan.working_alignment_json,
                )
                for task_plan in task_plans
            )
            raw_plans = tuple(
                RawSyncPlan(
                    task_key=raw_plan.task_key,
                    action="keep" if raw_plan.action == "keep" else "skip",
                    status=raw_plan.status,
                    reason=raw_plan.reason if raw_plan.reason is not None else f"session {mode_action}",
                    source_path=raw_plan.source_path,
                    target_path=raw_plan.target_path,
                    relative_source=raw_plan.relative_source,
                )
                for raw_plan in raw_plans
            )

        plans.append(
            SessionImportPlan(
                person=person,
                session=workbook_session,
                exposures=exposures,
                secure_person=workbook_data.secure_persons.get(workbook_session.person_id),
                source_batch=batch_dir.name,
                mode_action=mode_action,
                reason=reason,
                session_id_change_from=session_id_change_from,
                existing_db_session_id=existing_slot.session_id if existing_slot is not None else None,
                target_session_dir=target_session_dir,
                existing_session_dir=existing_runtime_dir,
                target_runtime_exists=target_runtime_exists,
                task_plans=task_plans,
                raw_plans=raw_plans,
                archive_inputs=archive_inputs,
                warnings=tuple(warnings),
                conflicts=tuple(conflicts),
            )
        )

    return plans, plan_warnings


def _print_plan(plans: list[SessionImportPlan], workbook_warnings: tuple[str, ...], plan_warnings: list[str]) -> ImportRunSummary:
    if workbook_warnings:
        print("[workbook-warnings]")
        for warning in workbook_warnings:
            print(f"- {warning}")
        print()

    if plan_warnings:
        print("[plan-warnings]")
        for warning in plan_warnings:
            print(f"- {warning}")
        print()

    print("[import-plan]")
    create_count = 0
    update_count = 0
    skip_count = 0
    conflict_count = 0
    task_sync_count = 0
    task_available_count = 0
    raw_sync_count = 0
    raw_keep_count = 0
    raw_missing_count = 0
    raw_conflict_count = 0
    for plan in plans:
        if plan.mode_action == "create":
            create_count += 1
        elif plan.mode_action == "update":
            update_count += 1
        elif plan.mode_action == "skip":
            skip_count += 1
        elif plan.mode_action == "conflict":
            conflict_count += 1

        task_summary_parts: list[str] = []
        raw_summary_parts: list[str] = []
        for task_plan in plan.task_plans:
            if task_plan.action == "sync":
                task_sync_count += 1
            elif task_plan.action == "available":
                task_available_count += 1
            suffix = f"/{task_plan.status}"
            if task_plan.reason is not None and task_plan.status != "ready":
                suffix = f"/{task_plan.status}:{task_plan.reason}"
            task_summary_parts.append(f"{task_plan.task_key}={task_plan.action}{suffix}")

        for raw_plan in plan.raw_plans:
            if raw_plan.action == "sync":
                raw_sync_count += 1
            elif raw_plan.action == "keep":
                raw_keep_count += 1
            elif raw_plan.action == "missing":
                raw_missing_count += 1
            elif raw_plan.action == "conflict":
                raw_conflict_count += 1
            suffix = f"/{raw_plan.status}"
            if raw_plan.reason is not None and raw_plan.action != "keep":
                suffix = f"/{raw_plan.status}:{raw_plan.reason}"
            raw_summary_parts.append(f"{raw_plan.task_key}={raw_plan.action}{suffix}")

        details = [
            f"{plan.mode_action:8}",
            plan.session.session_id,
            f"({plan.person.person_id}/{plan.session.session_ref})",
            f"tasks[{', '.join(task_summary_parts)}]",
            f"archive_inputs={len(plan.archive_inputs)}",
        ]
        if plan.reason:
            details.append(f"reason={plan.reason}")
        if plan.session_id_change_from is not None:
            details.append(f"rename-from={plan.session_id_change_from}")
        print(" ".join(details))
        for warning in plan.warnings:
            print(f"  warning: {warning}")

    summary = ImportRunSummary(
        processed_sessions=len(plans),
        create_count=create_count,
        update_count=update_count,
        skip_count=skip_count,
        conflict_count=conflict_count,
        task_sync_count=task_sync_count,
        task_available_count=task_available_count,
        raw_sync_count=raw_sync_count,
        raw_keep_count=raw_keep_count,
        raw_missing_count=raw_missing_count,
        raw_conflict_count=raw_conflict_count,
    )
    print()
    print("[summary]")
    print(
        " ".join(
            [
                f"sessions={summary.processed_sessions}",
                f"create={summary.create_count}",
                f"update={summary.update_count}",
                f"skip={summary.skip_count}",
                f"conflict={summary.conflict_count}",
                f"task_sync={summary.task_sync_count}",
                f"task_available={summary.task_available_count}",
                f"raw_sync={summary.raw_sync_count}",
                f"raw_keep={summary.raw_keep_count}",
                f"raw_missing={summary.raw_missing_count}",
                f"raw_conflict={summary.raw_conflict_count}",
            ]
        )
    )
    return summary


def _copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _build_task_entries(
    session_dir: Path,
    *,
    person_id: str | None = None,
    speaker_type: str | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tasks: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    for task_key in RESEARCH_TASK_KEYS:
        if person_id is not None and _task_not_expected_status(task_key, person_id, speaker_type) is not None:
            continue
        if not _task_status_from_session_dir(session_dir, task_key):
            continue
        derived_rel = f"derived/{task_key}.mp3"
        alignment_json_rel = f"alignment/{task_key}.json"
        derived_path = session_dir / derived_rel
        alignment_json_path = session_dir / alignment_json_rel
        task_entry: dict[str, Any] = {
            "task_type": task_key,
            "label": _task_label(task_key),
        }
        if alignment_json_path.exists():
            task_entry["alignment_file"] = alignment_json_rel
        if derived_path.exists():
            task_entry["derived_file"] = derived_rel
        tasks.append(task_entry)

        if alignment_json_path.exists():
            files.append({"path": alignment_json_rel, "file_role": "alignment_json", "format": "json", "status": "processed"})
        if derived_path.exists():
            files.append({"path": derived_rel, "file_role": "audio_mp3", "format": "mp3", "status": "processed"})

        items_dir = session_dir / "items" / task_key
        if items_dir.exists():
            for item_path in sorted(items_dir.glob("*.mp3")):
                files.append(
                    {
                        "path": str(item_path.relative_to(session_dir)).replace("\\", "/"),
                        "file_role": "items_audio",
                        "format": "mp3",
                        "status": "processed",
                    }
                )

    files.insert(0, {"path": "metadata.json", "file_role": "metadata", "format": "json", "status": "processed"})
    return tasks, files


def _build_metadata_payload(plan: SessionImportPlan, session_dir: Path) -> tuple[dict[str, Any], tuple[str, ...]]:
    documented_tasks = _documented_tasks_from_session_dir(
        session_dir,
        person_id=plan.person.person_id,
        speaker_type=plan.person.speaker_type,
    )
    tasks, files = _build_task_entries(
        session_dir,
        person_id=plan.person.person_id,
        speaker_type=plan.person.speaker_type,
    )
    payload: dict[str, Any] = {
        "person_id": plan.person.person_id,
        "session_id": plan.session.session_id,
        "target_language": plan.session.target_language,
        "speaker_type": plan.person.speaker_type,
        "l1": plan.person.l1,
        "l1_additional": list(plan.person.l1_additional),
        "mother_l1": plan.person.mother_l1,
        "father_l1": plan.person.father_l1,
        "additional_languages": list(plan.person.additional_languages),
        "gender": plan.person.gender,
        "birth_year": plan.person.birth_year,
        "current_region": plan.person.current_region,
        "childhood_region": plan.person.childhood_region,
        "origin_country": plan.person.origin_country,
        "origin_region": plan.person.origin_region,
        "person_notes": plan.person.person_notes,
        "research_consent_signed": plan.person.research_consent_signed,
        "teaching_consent_signed": plan.person.teaching_consent_signed,
        "consent_date": plan.person.consent_date.isoformat() if plan.person.consent_date else None,
        "standard_variety": plan.session.standard_variety,
        "level_code": plan.session.level_code,
        "level_self": plan.session.level_self,
        "recording_year": plan.session.recording_year,
        "recording_date": plan.session.recording_date.isoformat() if plan.session.recording_date else None,
        "context": plan.session.context,
        "recorded_by": plan.session.recorded_by,
        "needs_review": plan.person.needs_review or plan.session.needs_review,
        "session_notes": plan.session.session_notes,
        "notes": plan.session.session_notes,
        "tasks": tasks,
        "files": files,
    }
    if plan.person.speaker_type == "learner":
        payload["stays_in_target_country"] = bool(plan.exposures)
        payload["exposure_entries"] = [
            {
                "country": exposure.country,
                "duration_months": exposure.duration_months,
                "type": exposure.exposure_type,
                "exposure_notes": exposure.exposure_notes,
                "needs_review": exposure.needs_review,
            }
            for exposure in plan.exposures
        ]
    return payload, documented_tasks


def _write_metadata_json(target_dir: Path, metadata_payload: dict[str, Any]) -> None:
    metadata_path = target_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _upsert_person_row(db_session: Session, person: IntakePersonRow, now: datetime) -> ResearchPerson:
    row = db_session.get(ResearchPerson, person.person_id)
    if row is None:
        row = ResearchPerson(person_id=person.person_id, created_at=now, updated_at=now)
        db_session.add(row)
    row.speaker_type = person.speaker_type
    row.l1 = person.l1
    row.l1_additional = _normalize_text_list(person.l1_additional)
    row.mother_l1 = person.mother_l1
    row.father_l1 = person.father_l1
    row.additional_languages = _normalize_text_list(person.additional_languages)
    row.gender = person.gender
    row.birth_year = person.birth_year
    row.current_region = person.current_region
    row.childhood_region = person.childhood_region
    row.origin_country = person.origin_country
    row.origin_region = person.origin_region
    row.needs_review = person.needs_review
    row.person_notes = person.person_notes
    row.research_consent_signed = person.research_consent_signed
    row.teaching_consent_signed = person.teaching_consent_signed
    row.consent_date = person.consent_date
    row.consent_file = person.consent_file
    row.questionnaire_file = person.questionnaire_file
    row.secure_notes = person.secure_notes
    row.updated_at = now
    return row


def _upsert_session_row(
    db_session: Session,
    plan: SessionImportPlan,
    *,
    documented_tasks: tuple[str, ...],
    now: datetime,
) -> ResearchSession:
    row = db_session.get(ResearchSession, plan.session.session_id)
    if row is None and plan.session_id_change_from is not None:
        row = db_session.get(ResearchSession, plan.session_id_change_from)
        if row is not None:
            row.session_id = plan.session.session_id
    if row is None:
        row = ResearchSession(session_id=plan.session.session_id, created_at=now, updated_at=now)
        db_session.add(row)

    row.person_id = plan.person.person_id
    row.session_ref = plan.session.session_ref
    row.corpus_language = plan.session.corpus_language
    row.target_language = plan.session.target_language
    row.standard_variety = plan.session.standard_variety
    row.level_self = plan.session.level_self
    row.level_code = plan.session.level_code
    row.recording_year = plan.session.recording_year
    row.recording_date = plan.session.recording_date
    row.recorded_by = plan.session.recorded_by
    row.context = plan.session.context
    row.stays_in_target_country = bool(plan.exposures) if plan.person.speaker_type == "learner" else None
    row.needs_review = plan.session.needs_review
    row.session_notes = plan.session.session_notes
    row.documented_tasks = _normalize_text_list(documented_tasks)
    row.updated_at = now

    existing_exposures = sorted(row.exposures, key=lambda exposure: exposure.sort_order)
    for exposure_row in existing_exposures:
        db_session.delete(exposure_row)
    db_session.flush()
    for index, exposure in enumerate(plan.exposures, start=1):
        db_session.add(
            ResearchSessionExposure(
                session_id=plan.session.session_id,
                sort_order=index,
                country=exposure.country,
                duration_months=exposure.duration_months,
                exposure_type=exposure.exposure_type,
                exposure_notes=exposure.exposure_notes,
                needs_review=exposure.needs_review,
                created_at=now,
                updated_at=now,
            )
        )
    return row


def _sync_wordlist_task(plan: SessionImportPlan, task_plan: TaskSyncPlan, validate_wordlist_labels: str) -> dict[str, Any]:
    assert task_plan.source_wav is not None
    assert task_plan.alignment_textgrid is not None
    session_dir = plan.target_session_dir
    language_slug = resolve_language_config(plan.session.target_language).corpus_slug
    return produce_wordlist_artifacts(
        session_dir=session_dir,
        session_id=plan.session.session_id,
        person_id=plan.person.person_id,
        source_wav=task_plan.source_wav,
        alignment_textgrid=task_plan.alignment_textgrid,
        language_slug=language_slug,
        dry_run=False,
        validate_labels=validate_wordlist_labels,
        update_metadata=False,
    )


def _sync_text_task(plan: SessionImportPlan, task_plan: TaskSyncPlan) -> dict[str, Any]:
    assert task_plan.source_wav is not None
    assert task_plan.working_alignment_json is not None
    session_dir = plan.target_session_dir
    return produce_text_artifacts(
        session_dir=session_dir,
        session_id=plan.session.session_id,
        person_id=plan.person.person_id,
        source_wav=task_plan.source_wav,
        working_alignment_json=task_plan.working_alignment_json,
        dry_run=False,
    )


def _sync_interview_task(plan: SessionImportPlan, task_plan: TaskSyncPlan) -> dict[str, Any]:
    assert task_plan.source_wav is not None
    assert task_plan.working_alignment_json is not None
    session_dir = plan.target_session_dir
    alignment_target = session_dir / "alignment" / "interview.json"
    derived_target = session_dir / "derived" / "interview.mp3"

    payload = json.loads(task_plan.working_alignment_json.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ProductionImportError(
            f"Working interview alignment JSON must contain an object: {task_plan.working_alignment_json}"
        )
    payload["session_id"] = plan.session.session_id
    payload["person_id"] = plan.person.person_id
    payload["task"] = "interview"
    payload["audio"] = {"full_mp3": "derived/interview.mp3"}
    alignment_target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    create_full_task_mp3(task_plan.source_wav, derived_target)

    return {
        "session_id": plan.session.session_id,
        "person_id": plan.person.person_id,
        "mode": "write",
        "segment_count": len(payload.get("segments", [])) if isinstance(payload.get("segments"), list) else 0,
    }


def _sync_raw_files(raw_plans: tuple[RawSyncPlan, ...]) -> None:
    for raw_plan in raw_plans:
        if raw_plan.action != "sync":
            continue
        if raw_plan.source_path is None:
            raise ProductionImportError(f"Raw sync planned without source path for {raw_plan.task_key}")
        _copy_file(raw_plan.source_path, raw_plan.target_path)


def _remove_runtime_task_artifacts(session_dir: Path, task_key: str) -> None:
    artifact_paths = [
        session_dir / "alignment" / f"{task_key}.json",
        session_dir / "derived" / f"{task_key}.mp3",
    ]
    for artifact_path in artifact_paths:
        if artifact_path.exists() or artifact_path.is_symlink():
            artifact_path.unlink()
    items_dir = session_dir / "items" / task_key
    if items_dir.exists():
        shutil.rmtree(items_dir)


def _apply_plan(
    db_session: Session,
    plan: SessionImportPlan,
    *,
    validate_wordlist_labels: str,
    write_archive: bool = True,
    write_db: bool = True,
    archive_root: Path | None = None,
) -> None:
    workspace = SessionWorkspace(target_dir=plan.target_session_dir, seed_dir=plan.existing_session_dir)
    workspace.prepare()
    try:
        skipped_or_missing_artifacts = [
            {
                "task": task_plan.task_key,
                "action": task_plan.action,
                "status": task_plan.status,
                "reason": task_plan.reason,
            }
            for task_plan in plan.task_plans
            if task_plan.action != "sync"
        ]
        for task_plan in plan.task_plans:
            if task_plan.action != "sync":
                continue
            if task_plan.task_key == "wordlist":
                _sync_wordlist_task(plan, task_plan, validate_wordlist_labels=validate_wordlist_labels)
            elif task_plan.task_key == "text":
                _sync_text_task(plan, task_plan)
            elif task_plan.task_key == "interview":
                _sync_interview_task(plan, task_plan)

        for task_key in RESEARCH_TASK_KEYS:
            if _task_not_expected_status(task_key, plan.person.person_id, plan.person.speaker_type) is not None:
                _remove_runtime_task_artifacts(plan.target_session_dir, task_key)

        metadata_payload, documented_tasks = _build_metadata_payload(plan, plan.target_session_dir)
        _write_metadata_json(plan.target_session_dir, metadata_payload)
        runtime_errors = validate_runtime_tree(plan.target_session_dir, required_tasks=documented_tasks)
        if runtime_errors:
            raise ProductionImportError(
                f"runtime validation failed for {plan.session.session_id}: " + "; ".join(runtime_errors)
            )
        if write_archive:
            archive_result = write_session_archive(
                session_dir=plan.target_session_dir,
                language_code=plan.session.target_language,
                session_id=plan.session.session_id,
                person_id=plan.person.person_id,
                source_batch=plan.source_batch,
                input_files=plan.archive_inputs,
                warnings=plan.warnings,
                skipped_or_missing_artifacts=skipped_or_missing_artifacts,
                importer_version="import_batch_to_production",
                archive_root=archive_root,
                report_payload={"documented_tasks": list(documented_tasks)},
            )
            if plan.secure_person is not None:
                sp = plan.secure_person
                secure_data = {
                    "last_name": sp.last_name,
                    "first_name": sp.first_name,
                    "email": sp.email,
                    "research_consent_signed": sp.research_consent_signed,
                    "teaching_consent_signed": sp.teaching_consent_signed,
                    "consent_date": sp.consent_date.isoformat() if sp.consent_date else None,
                    "consent_file": sp.consent_file,
                    "questionnaire_file": sp.questionnaire_file,
                    "paper_original_location": sp.paper_original_location,
                    "intake_date": sp.intake_date.isoformat() if sp.intake_date else None,
                    "intake_by": sp.intake_by,
                    "needs_review": sp.needs_review,
                    "verified_by": sp.verified_by,
                    "verified_date": sp.verified_date.isoformat() if sp.verified_date else None,
                    "secure_notes": sp.secure_notes,
                }
                write_secure_person_export(
                    archive_session_dir=archive_result.archive_session_dir,
                    person_id=plan.person.person_id,
                    secure_data=secure_data,
                )
        if write_db:
            now = datetime.now(UTC)
            _upsert_person_row(db_session, plan.person, now=now)
            _upsert_session_row(db_session, plan, documented_tasks=documented_tasks, now=now)
            db_session.commit()
        workspace.commit()
        return {
            "person": {
                "person_id": plan.person.person_id,
                "speaker_type": plan.person.speaker_type,
                "l1": plan.person.l1,
                "l1_additional": list(plan.person.l1_additional),
                "mother_l1": plan.person.mother_l1,
                "father_l1": plan.person.father_l1,
                "additional_languages": list(plan.person.additional_languages),
                "gender": plan.person.gender,
                "birth_year": plan.person.birth_year,
                "current_region": plan.person.current_region,
                "childhood_region": plan.person.childhood_region,
                "origin_country": plan.person.origin_country,
                "origin_region": plan.person.origin_region,
                "research_consent_signed": plan.person.research_consent_signed,
                "teaching_consent_signed": plan.person.teaching_consent_signed,
            },
            "session": {
                "session_id": plan.session.session_id,
                "person_id": plan.person.person_id,
                "session_ref": plan.session.session_ref,
                "corpus_language": plan.session.corpus_language,
                "target_language": plan.session.target_language,
                "standard_variety": plan.session.standard_variety,
                "level_self": plan.session.level_self,
                "level_code": plan.session.level_code,
                "recording_year": plan.session.recording_year,
                "recording_date": plan.session.recording_date.isoformat() if plan.session.recording_date else None,
                "recorded_by": plan.session.recorded_by,
                "context": plan.session.context,
                "documented_tasks": list(documented_tasks),
            },
            "exposures": [
                {
                    "session_id": plan.session.session_id,
                    "country": exposure.country,
                    "duration_months": exposure.duration_months,
                    "type": exposure.exposure_type,
                    "exposure_notes": exposure.exposure_notes,
                }
                for exposure in plan.exposures
            ],
            "warnings": list(plan.warnings),
            "archive_input_count": len(plan.archive_inputs),
            "db_update": "applied" if write_db else "skipped_by_flag",
        }
    except Exception:
        if write_db:
            db_session.rollback()
        workspace.rollback()
        raise


def _apply_raw_only_backfill(plan: SessionImportPlan) -> None:
    target_dir = plan.target_session_dir
    if not target_dir.exists():
        raise ProductionImportError(f"Raw-only mode requires an existing runtime session directory: {target_dir}")
    metadata_path = target_dir / "metadata.json"
    if not metadata_path.exists():
        raise ProductionImportError(f"Raw-only mode requires metadata.json in the existing session directory: {metadata_path}")

    original_metadata = metadata_path.read_text(encoding="utf-8")
    created_raw_paths: list[Path] = []
    try:
        for raw_plan in plan.raw_plans:
            if raw_plan.action != "sync":
                continue
            if raw_plan.source_path is None:
                raise ProductionImportError(f"Raw sync planned without source path for {plan.session.session_id}/{raw_plan.task_key}")
            _copy_file(raw_plan.source_path, raw_plan.target_path)
            created_raw_paths.append(raw_plan.target_path)
        metadata_payload, _ = _build_metadata_payload(plan, target_dir)
        _write_metadata_json(target_dir, metadata_payload)
    except Exception:
        metadata_path.write_text(original_metadata, encoding="utf-8")
        for created_path in reversed(created_raw_paths):
            if created_path.exists():
                created_path.unlink()
        raise


def _render_markdown_list(items: Sequence[str]) -> str:
    if not items:
        return "- none\n"
    return "".join(f"- {item}\n" for item in items)


def _write_batch_reports(
    *,
    batch_name: str,
    workbook_warnings: Sequence[str],
    plan_warnings: Sequence[str],
    applied_results: Sequence[dict[str, Any]],
    run_notes: Sequence[str] = (),
    archive_root: Path | None = None,
) -> None:
    import_payload = {
        "batch_name": batch_name,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "persons": [result["person"] for result in applied_results],
        "sessions": [result["session"] for result in applied_results],
        "exposures": [entry for result in applied_results for entry in result["exposures"]],
    }
    intake_report = "".join(
        [
            f"# Intake Report {batch_name}\n\n",
            "## Workbook Warnings\n",
            _render_markdown_list(list(workbook_warnings)),
            "\n## Plan Warnings\n",
            _render_markdown_list(list(plan_warnings)),
            "\n## Run Notes\n",
            _render_markdown_list(list(run_notes)),
        ]
    )
    validation_report = "".join(
        [
            f"# Validation Report {batch_name}\n\n",
            f"Imported sessions: {len(applied_results)}\n\n",
            "## Session Warnings\n",
            _render_markdown_list(
                [
                    f"{result['session']['session_id']}: {warning}"
                    for result in applied_results
                    for warning in result["warnings"]
                ]
            ),
            "\n## Run Notes\n",
            _render_markdown_list(list(run_notes)),
        ]
    )
    archive_report = "".join(
        [
            f"# Archive Report {batch_name}\n\n",
            "## Archived Session Inputs\n",
            _render_markdown_list(
                [
                    f"{result['session']['session_id']}: archive_inputs={result['archive_input_count']}"
                    for result in applied_results
                ]
            ),
            "\n## Run Notes\n",
            _render_markdown_list(list(run_notes)),
        ]
    )
    write_batch_archive_reports(
        batch_name=batch_name,
        import_payload=import_payload,
        intake_report_markdown=intake_report,
        validation_report_markdown=validation_report,
        archive_report_markdown=archive_report,
        run_notes=run_notes,
        archive_root=archive_root,
    )


def _assert_schema_ready(engine) -> None:
    inspector = inspect(engine)
    required_tables = ("research_people", "research_sessions", "research_session_exposures")
    missing = [table_name for table_name in required_tables if not inspector.has_table(table_name)]
    if missing:
        raise ProductionImportError(
            "Research metadata tables are missing. Run the migration chain first. Missing: " + ", ".join(missing)
        )


def main() -> int:
    args = parse_args()
    try:
        _apply_runtime_overrides(args)
        if args.sync_raw_only and args.sync_tasks:
            raise ProductionImportError("--sync-raw-only cannot be combined with --sync-tasks")
        if args.sync_raw_only and args.create_missing_only:
            raise ProductionImportError("--sync-raw-only cannot be combined with --create-missing-only")
        if args.sync_raw_only:
            raise ProductionImportError("--sync-raw-only is obsolete under the runtime-only session model.")
        batch_dir = resolve_batch_dir(args.batch_dir, require_processed=False)
        workbook_path = _discover_workbook_path(batch_dir, args.workbook)
        target_language = resolve_language_config(args.target_language).code
        person_id_filter: set[str] | None = set(args.person_ids) if args.person_ids else None
        workbook_data = load_intake_workbook(
            workbook_path,
            target_language=target_language,
            person_id_filter=person_id_filter,
        )
        if workbook_data.errors:
            print("[workbook-errors]")
            for error in workbook_data.errors:
                print(f"- {error}")
            return 1
        if not workbook_data.sessions:
            raise ProductionImportError("No matching workbook sessions found for the requested target language/person filter.")

        run_notes: list[str] = []
        in_scope_people = sorted(workbook_data.persons)
        if args.run_working:
            working_report = _run_working_pipeline(
                batch_dir=batch_dir,
                person_ids=person_id_filter,
                dry_run=args.dry_run,
            )
            run_notes.append(
                f"Working-tree orchestration completed for {', '.join(working_report.get('person_ids', [])) or 'all in-scope people'}."
            )
        if args.run_mfa:
            mfa_version = check_mfa_available(args.mfa_executable)
            run_notes.append(f"Verified MFA executable {args.mfa_executable}: {mfa_version}")
            for person_id in in_scope_people:
                run_notes.extend(
                    _run_text_pipeline(
                        batch_dir=batch_dir,
                        person_id=person_id,
                        target_language=target_language,
                        mfa_executable=args.mfa_executable,
                        dry_run=args.dry_run,
                    )
                )

        database_url = _resolve_database_url(args.auth_database_url)
        schema_note = _ensure_db_schema(database_url, should_write_db=True, dry_run=args.dry_run)
        if schema_note is not None:
            run_notes.append(schema_note)
        engine = create_engine(database_url, future=True)
        _assert_schema_ready(engine)
        session_factory = sessionmaker(bind=engine, future=True)

        with session_factory() as db_session:
            plans, plan_warnings = _build_import_plans(
                batch_dir=batch_dir,
                workbook_data=workbook_data,
                create_missing_only=args.create_missing_only,
                sync_tasks=args.sync_tasks,
                sync_raw_only=args.sync_raw_only,
                allow_session_id_change=args.allow_session_id_change,
                db_session=db_session,
            )
            summary = _print_plan(plans, workbook_data.warnings, plan_warnings)
            if summary.conflict_count:
                return 1
            if args.dry_run:
                return 0
            if args.sync_tasks and summary.task_sync_count:
                ensure_media_tools()
            applied_results: list[dict[str, Any]] = []
            archive_root = _resolve_optional_path(args.archive_root)
            for plan in plans:
                if plan.mode_action not in {"create", "update"}:
                    continue
                if args.sync_raw_only:
                    _apply_raw_only_backfill(plan)
                else:
                    applied_results.append(
                        _apply_plan(
                            db_session,
                            plan,
                            validate_wordlist_labels=args.validate_wordlist_labels,
                            write_archive=True,
                            write_db=True,
                            archive_root=archive_root,
                        )
                    )
            if args.cleanup_working_on_success and args.run_working and not args.dry_run:
                run_notes.append(_cleanup_working_people(batch_dir, in_scope_people))
            if applied_results:
                _write_batch_reports(
                    batch_name=batch_dir.name,
                    workbook_warnings=workbook_data.warnings,
                    plan_warnings=plan_warnings,
                    applied_results=applied_results,
                    run_notes=run_notes,
                    archive_root=archive_root,
                )
        return 0
    except ProductionImportError as exc:
        print(f"ERROR: {exc}")
        return 1
    except Exception as exc:
        print(f"ERROR: unexpected import failure: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())