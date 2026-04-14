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
from typing import Any

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session, selectinload, sessionmaker


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_SRC = REPO_ROOT / "app" / "src"
SCRIPT_ROOT = Path(__file__).resolve().parent
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app.config import DEFAULT_DEV_DATABASE_URL  # noqa: E402
from app.research_capabilities import RESEARCH_TASK_KEYS, get_research_task_capability  # noqa: E402
from app.research_metadata import ResearchPerson, ResearchSession, ResearchSessionExposure  # noqa: E402
from app.runtime_paths import get_sessions_root  # noqa: E402
from audio_conversion.ffmpeg_audio import ensure_media_tools  # noqa: E402
from intake_batch_common import resolve_batch_dir, working_alignment_path, working_source_path, working_task_root  # noqa: E402
from intake_workbook_reader import IntakeExposureRow, IntakePersonRow, IntakeSessionRow, SessionLinkKey, load_intake_workbook  # noqa: E402
from language_config import resolve_language_config  # noqa: E402
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
class SessionImportPlan:
    person: IntakePersonRow
    session: IntakeSessionRow
    exposures: tuple[IntakeExposureRow, ...]
    mode_action: str
    reason: str | None
    session_id_change_from: str | None
    existing_db_session_id: str | None
    target_session_dir: Path
    existing_session_dir: Path | None
    target_runtime_exists: bool
    task_plans: tuple[TaskSyncPlan, ...]
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
        for relative_dir in ("raw", "source", "alignment", "derived", "items"):
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
    parser.add_argument("--batch-dir", required=True, help="Batch directory below scripts/research_data_intake/import/.")
    parser.add_argument("--workbook", help="Optional explicit intake workbook path; defaults to intake_data/*.xlsx.")
    parser.add_argument("--target-language", default="es", help="Target language code or slug. Default: es.")
    parser.add_argument("--person-id", help="Optional single person filter, for smoke tests or controlled imports.")
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

    intake_data_dir = batch_dir / "intake_data"
    if not intake_data_dir.exists():
        raise ProductionImportError(f"Batch has no intake_data directory: {intake_data_dir}")
    workbook_candidates = sorted(path for path in intake_data_dir.glob("*.xlsx") if not path.name.startswith("~$"))
    if not workbook_candidates:
        raise ProductionImportError(f"No intake workbook (*.xlsx) found in {intake_data_dir}")
    if len(workbook_candidates) > 1:
        joined = ", ".join(path.name for path in workbook_candidates)
        raise ProductionImportError(
            f"Multiple workbook candidates found in {intake_data_dir}; use --workbook explicitly. Found: {joined}"
        )
    return workbook_candidates[0]


def _resolve_database_url(explicit_value: str | None) -> str:
    value = (explicit_value or os.getenv("AUTH_DATABASE_URL") or DEFAULT_DEV_DATABASE_URL).strip()
    if not value:
        raise ProductionImportError("AUTH database URL is required.")
    return value


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
    source_path = session_dir / "source" / f"{task_key}.wav"
    alignment_path = session_dir / "alignment" / f"{task_key}.TextGrid"
    alignment_json_path = session_dir / "alignment" / f"{task_key}.json"
    derived_mp3_path = session_dir / "derived" / f"{task_key}.mp3"
    return source_path.exists() or alignment_path.exists() or alignment_json_path.exists() or derived_mp3_path.exists()


def _documented_tasks_from_session_dir(session_dir: Path) -> tuple[str, ...]:
    documented: list[str] = []
    for task_key in RESEARCH_TASK_KEYS:
        if _task_status_from_session_dir(session_dir, task_key):
            documented.append(task_key)
    return tuple(documented)


def _detect_working_task(batch_dir: Path, person_id: str, task_key: str, sync_tasks: bool) -> TaskSyncPlan:
    task_root = working_task_root(batch_dir, person_id, task_key)
    source_wav = working_source_path(batch_dir, person_id, task_key)
    alignment_textgrid = working_alignment_path(batch_dir, person_id, task_key)
    working_alignment_json = task_root / "alignment" / f"{task_key}.json"

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
    interview_alignment = alignment_textgrid.exists() or working_alignment_json.exists()
    if interview_source or interview_alignment:
        return TaskSyncPlan(
            task_key=task_key,
            action="skip",
            status="not_implemented",
            reason="interview import pipeline is not implemented yet",
            working_root=task_root,
            source_wav=source_wav if interview_source else None,
            alignment_textgrid=alignment_textgrid if alignment_textgrid.exists() else None,
            working_alignment_json=working_alignment_json if working_alignment_json.exists() else None,
        )
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
    allow_session_id_change: bool,
    db_session: Session,
) -> tuple[list[SessionImportPlan], list[str]]:
    sessions = db_session.scalars(
        select(ResearchSession).options(selectinload(ResearchSession.exposures)).where(
            ResearchSession.target_language == workbook_data.target_language
        )
    ).all()
    by_slot = {(row.person_id, row.session_ref): row for row in sessions}
    by_session_id = {row.session_id: row for row in sessions}
    runtime_dirs = _existing_runtime_dirs(workbook_data.sessions[0].corpus_language) if workbook_data.sessions else {}
    plan_warnings: list[str] = []
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

        if create_missing_only and (existing_slot is not None or existing_by_id is not None or target_runtime_exists):
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
            _detect_working_task(batch_dir=batch_dir, person_id=workbook_session.person_id, task_key=task_key, sync_tasks=sync_tasks)
            for task_key in RESEARCH_TASK_KEYS
        )
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

        plans.append(
            SessionImportPlan(
                person=person,
                session=workbook_session,
                exposures=exposures,
                mode_action=mode_action,
                reason=reason,
                session_id_change_from=session_id_change_from,
                existing_db_session_id=existing_slot.session_id if existing_slot is not None else None,
                target_session_dir=target_session_dir,
                existing_session_dir=existing_runtime_dir,
                target_runtime_exists=target_runtime_exists,
                task_plans=task_plans,
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
        for task_plan in plan.task_plans:
            if task_plan.action == "sync":
                task_sync_count += 1
            elif task_plan.action == "available":
                task_available_count += 1
            suffix = f"/{task_plan.status}"
            if task_plan.reason is not None and task_plan.status != "ready":
                suffix = f"/{task_plan.status}:{task_plan.reason}"
            task_summary_parts.append(f"{task_plan.task_key}={task_plan.action}{suffix}")

        details = [
            f"{plan.mode_action:8}",
            plan.session.session_id,
            f"({plan.person.person_id}/{plan.session.session_ref})",
            f"tasks[{', '.join(task_summary_parts)}]",
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
            ]
        )
    )
    return summary


def _copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _build_task_entries(session_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tasks: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    for task_key in RESEARCH_TASK_KEYS:
        if not _task_status_from_session_dir(session_dir, task_key):
            continue
        source_rel = f"source/{task_key}.wav"
        alignment_rel = f"alignment/{task_key}.TextGrid"
        derived_rel = f"derived/{task_key}.mp3"
        alignment_json_rel = f"alignment/{task_key}.json"
        source_path = session_dir / source_rel
        alignment_path = session_dir / alignment_rel
        derived_path = session_dir / derived_rel
        alignment_json_path = session_dir / alignment_json_rel
        task_entry: dict[str, Any] = {
            "task_type": task_key,
            "label": _task_label(task_key),
            "source_file": source_rel,
            "alignment_file": alignment_rel,
        }
        if derived_path.exists():
            task_entry["derived_file"] = derived_rel
        tasks.append(task_entry)

        if source_path.exists():
            files.append({"path": source_rel, "file_role": "audio_source", "format": "wav", "status": "source"})
        if alignment_path.exists():
            files.append({"path": alignment_rel, "file_role": "textgrid", "format": "textgrid", "status": "processed"})
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
    documented_tasks = _documented_tasks_from_session_dir(session_dir)
    tasks, files = _build_task_entries(session_dir)
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
        "standard_variety": plan.session.standard_variety,
        "level_code": plan.session.level_code,
        "level_self": plan.session.level_self,
        "recording_year": plan.session.recording_year,
        "recording_date": plan.session.recording_date.isoformat() if plan.session.recording_date else None,
        "context": plan.session.context,
        "recorded_by": plan.session.recorded_by,
        "needs_review": plan.person.needs_review or plan.session.needs_review,
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
                "notes": exposure.exposure_notes,
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
    source_target = session_dir / "source" / "wordlist.wav"
    alignment_target = session_dir / "alignment" / "wordlist.TextGrid"
    _copy_file(task_plan.source_wav, source_target)
    _copy_file(task_plan.alignment_textgrid, alignment_target)
    return produce_wordlist_artifacts(
        session_dir=session_dir,
        session_id=plan.session.session_id,
        person_id=plan.person.person_id,
        source_wav=source_target,
        alignment_textgrid=alignment_target,
        dry_run=False,
        validate_labels=validate_wordlist_labels,
        update_metadata=False,
    )


def _sync_text_task(plan: SessionImportPlan, task_plan: TaskSyncPlan) -> dict[str, Any]:
    assert task_plan.source_wav is not None
    assert task_plan.working_alignment_json is not None
    session_dir = plan.target_session_dir
    source_target = session_dir / "source" / "text.wav"
    _copy_file(task_plan.source_wav, source_target)
    if task_plan.alignment_textgrid is not None:
        _copy_file(task_plan.alignment_textgrid, session_dir / "alignment" / "text.TextGrid")
    return produce_text_artifacts(
        session_dir=session_dir,
        session_id=plan.session.session_id,
        person_id=plan.person.person_id,
        source_wav=source_target,
        working_alignment_json=task_plan.working_alignment_json,
        dry_run=False,
    )


def _apply_plan(
    db_session: Session,
    plan: SessionImportPlan,
    *,
    validate_wordlist_labels: str,
) -> None:
    workspace = SessionWorkspace(target_dir=plan.target_session_dir, seed_dir=plan.existing_session_dir)
    workspace.prepare()
    try:
        for task_plan in plan.task_plans:
            if task_plan.action != "sync":
                continue
            if task_plan.task_key == "wordlist":
                _sync_wordlist_task(plan, task_plan, validate_wordlist_labels=validate_wordlist_labels)
            elif task_plan.task_key == "text":
                _sync_text_task(plan, task_plan)

        metadata_payload, documented_tasks = _build_metadata_payload(plan, plan.target_session_dir)
        _write_metadata_json(plan.target_session_dir, metadata_payload)
        now = datetime.now(UTC)
        _upsert_person_row(db_session, plan.person, now=now)
        _upsert_session_row(db_session, plan, documented_tasks=documented_tasks, now=now)
        db_session.commit()
        workspace.commit()
    except Exception:
        db_session.rollback()
        workspace.rollback()
        raise


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
        batch_dir = resolve_batch_dir(args.batch_dir, require_processed=False)
        workbook_path = _discover_workbook_path(batch_dir, args.workbook)
        target_language = resolve_language_config(args.target_language).code
        workbook_data = load_intake_workbook(
            workbook_path,
            target_language=target_language,
            person_id_filter=args.person_id,
        )
        if workbook_data.errors:
            print("[workbook-errors]")
            for error in workbook_data.errors:
                print(f"- {error}")
            return 1
        if not workbook_data.sessions:
            raise ProductionImportError("No matching workbook sessions found for the requested target language/person filter.")

        database_url = _resolve_database_url(args.auth_database_url)
        engine = create_engine(database_url, future=True)
        _assert_schema_ready(engine)
        session_factory = sessionmaker(bind=engine, future=True)

        with session_factory() as db_session:
            plans, plan_warnings = _build_import_plans(
                batch_dir=batch_dir,
                workbook_data=workbook_data,
                create_missing_only=args.create_missing_only,
                sync_tasks=args.sync_tasks,
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
            for plan in plans:
                if plan.mode_action not in {"create", "update"}:
                    continue
                _apply_plan(
                    db_session,
                    plan,
                    validate_wordlist_labels=args.validate_wordlist_labels,
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