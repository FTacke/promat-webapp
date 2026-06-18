from __future__ import annotations

import argparse
from datetime import UTC, date, datetime
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

from sqlalchemy import create_engine, delete, func, inspect, select
from sqlalchemy.orm import Session, sessionmaker


if str(__file__).startswith("<") or not Path(__file__).exists():
    REPO_ROOT = Path.cwd()
else:
    parents = Path(__file__).resolve().parents
    REPO_ROOT = parents[2] if len(parents) > 2 else Path.cwd()
if os.environ.get("PROMAT_APP_SRC"):
    APP_SRC = Path(os.environ["PROMAT_APP_SRC"])
else:
    APP_SRC = REPO_ROOT / "app" / "src"
    if not APP_SRC.exists() and (REPO_ROOT / "src").exists():
        APP_SRC = REPO_ROOT / "src"
SCRIPT_ROOT = Path(__file__).resolve().parent
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from app.research_metadata import ResearchPerson, ResearchSession, ResearchSessionExposure  # noqa: E402

try:
    from language_config import resolve_language_config  # type: ignore[import-not-found] # noqa: E402
except ModuleNotFoundError:

    class _LanguageConfig:
        def __init__(self, code: str, corpus_slug: str) -> None:
            self.code = code
            self.corpus_slug = corpus_slug

    _LANGUAGE_ALIASES = {
        "en": _LanguageConfig("en", "english"),
        "english": _LanguageConfig("en", "english"),
        "fr": _LanguageConfig("fr", "french"),
        "french": _LanguageConfig("fr", "french"),
        "es": _LanguageConfig("es", "spanish"),
        "spanish": _LanguageConfig("es", "spanish"),
        "de": _LanguageConfig("de", "german"),
        "german": _LanguageConfig("de", "german"),
    }

    def resolve_language_config(value: str) -> _LanguageConfig:
        language = _LANGUAGE_ALIASES.get(value.strip().lower())
        if language is None:
            raise ValueError(f"Unsupported intake language {value!r}")
        return language


REQUIRED_TABLES = ("research_people", "research_sessions", "research_session_exposures")
WINDOWS_PATH_RE = re.compile(r"(?i)(?:[a-z]:[\\/]|\\\\)")
SUPPORTED_TASKS = {"wordlist", "text", "interview"}


class PayloadUpsertError(RuntimeError):
    """Raised when a production DB payload cannot be validated or applied."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and optionally upsert a staged PROMAT db/import_payload.json into the auth DB."
    )
    parser.add_argument("--release-dir", required=True, help="Staged release directory that contains runtime files.")
    parser.add_argument(
        "--payload",
        help="Path to import_payload.json. Defaults to <release-dir>/db/import_payload.json.",
    )
    parser.add_argument(
        "--auth-database-url",
        help="Target DB URL. Defaults to AUTH_DATABASE_URL; no dev fallback is used for this prod tool.",
    )
    parser.add_argument("--apply", action="store_true", help="Apply the transactional DB upsert. Default is dry-run.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report planned DB changes without writing.")
    parser.add_argument(
        "--cleanup-metadata-only",
        action="store_true",
        help=(
            "Find and optionally remove DB rows for sessions of --target-language that have no runtime task artifacts "
            "in the release dir. Requires --target-language. Default is dry-run; use --apply-cleanup to apply."
        ),
    )
    parser.add_argument(
        "--target-language",
        help="Target language code or slug for --cleanup-metadata-only (e.g. fr or french).",
    )
    parser.add_argument(
        "--apply-cleanup",
        action="store_true",
        help="Apply the metadata-only cleanup transactionally. Only valid with --cleanup-metadata-only.",
    )
    return parser.parse_args()


def load_payload(payload_path: Path) -> dict[str, Any]:
    if not payload_path.exists():
        raise PayloadUpsertError(f"db import payload is missing: {payload_path}")
    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PayloadUpsertError(f"db import payload is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise PayloadUpsertError("db import payload must be a JSON object")
    return payload


def _require_list(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise PayloadUpsertError(f"db import payload key {key!r} must be a list")
    if any(not isinstance(entry, dict) for entry in value):
        raise PayloadUpsertError(f"db import payload key {key!r} must contain objects only")
    return value


def _has_windows_path(value: Any) -> bool:
    if isinstance(value, str):
        return bool(WINDOWS_PATH_RE.search(value))
    if isinstance(value, dict):
        return any(_has_windows_path(nested) for nested in value.values())
    if isinstance(value, list):
        return any(_has_windows_path(nested) for nested in value)
    return False


def _require_text(row: dict[str, Any], key: str, row_label: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PayloadUpsertError(f"{row_label} requires non-empty {key!r}")
    return value.strip()


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return str(value)


def _normalize_text_list(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, (list, tuple)):
        values = [str(item).strip() for item in value if str(item).strip()]
        return "; ".join(values) if values else None
    return str(value)


def _normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "ja", "y"}
    return bool(value)


def _normalize_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _normalize_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value.strip())
    raise PayloadUpsertError(f"date value must be ISO text, got {value!r}")


def _metadata_documented_tasks(metadata_path: Path) -> set[str]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    tasks = metadata.get("tasks")
    if not isinstance(tasks, list):
        raise PayloadUpsertError(f"runtime metadata tasks must be a list: {metadata_path}")
    documented: set[str] = set()
    for task in tasks:
        if isinstance(task, dict) and isinstance(task.get("task_type"), str):
            documented.add(task["task_type"])
    return documented


def validate_payload_against_release(payload: dict[str, Any], release_dir: Path) -> dict[str, Any]:
    if not release_dir.exists() or not release_dir.is_dir():
        raise PayloadUpsertError(f"release directory does not exist: {release_dir}")
    if _has_windows_path(payload):
        raise PayloadUpsertError("db import payload contains a local Windows path")

    batch_name = payload.get("batch_name")
    if not isinstance(batch_name, str) or "batch" not in batch_name.lower():
        raise PayloadUpsertError("db import payload requires a batch_name containing 'batch'")

    persons = _require_list(payload, "persons")
    sessions = _require_list(payload, "sessions")
    exposures = _require_list(payload, "exposures") if "exposures" in payload else []
    if not persons or not sessions:
        raise PayloadUpsertError("db import payload must contain at least one person and one session")

    person_ids = {_require_text(person, "person_id", "person") for person in persons}
    if len(person_ids) != len(persons):
        raise PayloadUpsertError("db import payload contains duplicate person_id values")

    session_ids: set[str] = set()
    languages: set[str] = set()
    language_slugs: set[str] = set()
    documented_task_count = 0
    for session_row in sessions:
        session_id = _require_text(session_row, "session_id", "session")
        if session_id in session_ids:
            raise PayloadUpsertError(f"db import payload contains duplicate session_id {session_id}")
        session_ids.add(session_id)

        person_id = _require_text(session_row, "person_id", f"session {session_id}")
        if person_id not in person_ids:
            raise PayloadUpsertError(f"session {session_id} references unknown person_id {person_id}")

        language = resolve_language_config(_require_text(session_row, "target_language", f"session {session_id}"))
        languages.add(language.code)
        language_slugs.add(language.corpus_slug)
        corpus_language = session_row.get("corpus_language")
        if corpus_language is not None and str(corpus_language).strip() != language.corpus_slug:
            raise PayloadUpsertError(
                f"session {session_id} corpus_language {corpus_language!r} does not match target_language {language.code!r}"
            )

        session_dir = release_dir / "sessions" / language.corpus_slug / session_id
        metadata_path = session_dir / "metadata.json"
        if not metadata_path.exists():
            raise PayloadUpsertError(f"session {session_id} metadata is missing in staged release: {metadata_path}")
        metadata_tasks = _metadata_documented_tasks(metadata_path)
        raw_tasks = session_row.get("documented_tasks") or []
        if isinstance(raw_tasks, str):
            documented_tasks = [task.strip() for task in raw_tasks.split(";") if task.strip()]
        elif isinstance(raw_tasks, list):
            documented_tasks = [str(task).strip() for task in raw_tasks if str(task).strip()]
        else:
            raise PayloadUpsertError(f"session {session_id} documented_tasks must be a list or text")
        if not documented_tasks:
            raise PayloadUpsertError(
                f"session {session_id} has no documented_tasks; metadata-only sessions must not be in db/import_payload.json"
            )
        for task in documented_tasks:
            if task not in SUPPORTED_TASKS:
                raise PayloadUpsertError(f"session {session_id} has unsupported task {task!r}")
            if task not in metadata_tasks:
                raise PayloadUpsertError(f"session {session_id} task {task!r} is not documented in metadata.json")
            alignment_path = session_dir / "alignment" / f"{task}.json"
            derived_path = session_dir / "derived" / f"{task}.mp3"
            if not alignment_path.exists():
                raise PayloadUpsertError(f"session {session_id} task {task} alignment is missing: {alignment_path}")
            if not derived_path.exists():
                raise PayloadUpsertError(f"session {session_id} task {task} mp3 is missing: {derived_path}")
            documented_task_count += 1

    for index, exposure in enumerate(exposures, start=1):
        session_id = _require_text(exposure, "session_id", f"exposure {index}")
        if session_id not in session_ids:
            raise PayloadUpsertError(f"exposure {index} references unknown session_id {session_id}")

    return {
        "batch_name": batch_name,
        "languages": sorted(languages),
        "language_slugs": sorted(language_slugs),
        "person_count": len(persons),
        "session_count": len(sessions),
        "exposure_count": len(exposures),
        "documented_task_count": documented_task_count,
    }


def _assert_schema_ready(engine) -> None:
    inspector = inspect(engine)
    missing = [table_name for table_name in REQUIRED_TABLES if not inspector.has_table(table_name)]
    if missing:
        raise PayloadUpsertError("research metadata tables are missing: " + ", ".join(missing))


def _count_rows(db_session: Session, model: type[Any]) -> int:
    return int(db_session.scalar(select(func.count()).select_from(model)) or 0)


def _empty_table_counts() -> dict[str, dict[str, int]]:
    return {table: {"insert": 0, "update": 0, "unchanged": 0, "delete": 0} for table in REQUIRED_TABLES}


def _status_for_existing(row: Any, desired: dict[str, Any]) -> str:
    for key, value in desired.items():
        if getattr(row, key) != value:
            return "update"
    return "unchanged"


def _set_values(row: Any, desired: dict[str, Any], now: datetime) -> None:
    for key, value in desired.items():
        setattr(row, key, value)
    row.updated_at = now


def _person_values(row: dict[str, Any], *, inserting: bool) -> dict[str, Any]:
    field_map = {
        "speaker_type": _normalize_text,
        "l1": _normalize_text,
        "l1_additional": _normalize_text_list,
        "mother_l1": _normalize_text,
        "father_l1": _normalize_text,
        "additional_languages": _normalize_text_list,
        "gender": _normalize_text,
        "birth_year": _normalize_int,
        "current_region": _normalize_text,
        "childhood_region": _normalize_text,
        "origin_country": _normalize_text,
        "origin_region": _normalize_text,
        "needs_review": _normalize_bool,
        "person_notes": _normalize_text,
        "research_consent_signed": _normalize_text,
        "teaching_consent_signed": _normalize_text,
        "consent_date": _normalize_date,
        "consent_file": _normalize_text,
        "questionnaire_file": _normalize_text,
        "secure_notes": _normalize_text,
    }
    values = {key: normalizer(row[key]) for key, normalizer in field_map.items() if key in row}
    if inserting and "needs_review" not in values:
        values["needs_review"] = False
    return values


def _session_values(
    row: dict[str, Any],
    *,
    person_speaker_type: str | None,
    has_exposures: bool,
    inserting: bool,
) -> dict[str, Any]:
    language = resolve_language_config(_require_text(row, "target_language", f"session {row.get('session_id', '?')}"))
    values: dict[str, Any] = {
        "person_id": _require_text(row, "person_id", f"session {row.get('session_id', '?')}"),
        "session_ref": _require_text(row, "session_ref", f"session {row.get('session_id', '?')}"),
        "corpus_language": row.get("corpus_language") or language.corpus_slug,
        "target_language": language.code,
        "standard_variety": _normalize_text(row.get("standard_variety")),
        "level_self": _normalize_text(row.get("level_self")),
        "level_code": _normalize_text(row.get("level_code")),
        "recording_year": _normalize_int(row.get("recording_year")),
        "recording_date": _normalize_date(row.get("recording_date")),
        "recorded_by": _normalize_text(row.get("recorded_by")),
        "context": _normalize_text(row.get("context")),
        "stays_in_target_country": bool(has_exposures) if person_speaker_type == "learner" else None,
        "documented_tasks": _normalize_text_list(row.get("documented_tasks")),
    }
    if "needs_review" in row or inserting:
        values["needs_review"] = _normalize_bool(row.get("needs_review"))
    if "session_notes" in row or inserting:
        values["session_notes"] = _normalize_text(row.get("session_notes"))
    return values


def _exposure_values(row: dict[str, Any], sort_order: int) -> dict[str, Any]:
    return {
        "sort_order": sort_order,
        "country": _normalize_text(row.get("country")),
        "duration_months": _normalize_int(row.get("duration_months")),
        "exposure_type": _normalize_text(row.get("type", row.get("exposure_type"))),
        "exposure_notes": _normalize_text(row.get("exposure_notes")),
        "needs_review": _normalize_bool(row.get("needs_review")),
    }


def _plan_and_optionally_apply(
    db_session: Session,
    payload: dict[str, Any],
    *,
    apply_changes: bool,
    now: datetime,
) -> dict[str, Any]:
    counters = _empty_table_counts()
    persons = _require_list(payload, "persons")
    sessions = _require_list(payload, "sessions")
    exposures = _require_list(payload, "exposures") if "exposures" in payload else []
    person_by_id = {person["person_id"]: person for person in persons}
    exposures_by_session: dict[str, list[dict[str, Any]]] = {}
    for exposure in exposures:
        exposures_by_session.setdefault(exposure["session_id"], []).append(exposure)

    for person in persons:
        person_id = _require_text(person, "person_id", "person")
        row = db_session.get(ResearchPerson, person_id)
        desired = _person_values(person, inserting=row is None)
        if row is None:
            counters["research_people"]["insert"] += 1
            if apply_changes:
                row = ResearchPerson(person_id=person_id, created_at=now, updated_at=now)
                _set_values(row, desired, now)
                db_session.add(row)
        else:
            status = _status_for_existing(row, desired)
            counters["research_people"][status] += 1
            if apply_changes and status == "update":
                _set_values(row, desired, now)

    if apply_changes:
        db_session.flush()

    for session_row in sessions:
        session_id = _require_text(session_row, "session_id", "session")
        row = db_session.get(ResearchSession, session_id)
        person_id = _require_text(session_row, "person_id", f"session {session_id}")
        person_speaker_type = _normalize_text(person_by_id[person_id].get("speaker_type"))
        desired = _session_values(
            session_row,
            person_speaker_type=person_speaker_type,
            has_exposures=bool(exposures_by_session.get(session_id)),
            inserting=row is None,
        )
        if row is None:
            counters["research_sessions"]["insert"] += 1
            if apply_changes:
                row = ResearchSession(session_id=session_id, created_at=now, updated_at=now)
                _set_values(row, desired, now)
                db_session.add(row)
        else:
            status = _status_for_existing(row, desired)
            counters["research_sessions"][status] += 1
            if apply_changes and status == "update":
                _set_values(row, desired, now)

    if apply_changes:
        db_session.flush()

    for session_row in sessions:
        session_id = _require_text(session_row, "session_id", "session")
        desired_exposures = exposures_by_session.get(session_id, [])
        existing_rows = db_session.scalars(
            select(ResearchSessionExposure)
            .where(ResearchSessionExposure.session_id == session_id)
            .order_by(ResearchSessionExposure.sort_order)
        ).all()
        existing_by_order = {row.sort_order: row for row in existing_rows}
        for sort_order, exposure in enumerate(desired_exposures, start=1):
            row = existing_by_order.get(sort_order)
            desired = _exposure_values(exposure, sort_order)
            if row is None:
                counters["research_session_exposures"]["insert"] += 1
                if apply_changes:
                    db_session.add(
                        ResearchSessionExposure(
                            session_id=session_id,
                            created_at=now,
                            updated_at=now,
                            **desired,
                        )
                    )
            else:
                status = _status_for_existing(row, desired)
                counters["research_session_exposures"][status] += 1
                if apply_changes and status == "update":
                    _set_values(row, desired, now)

        desired_orders = set(range(1, len(desired_exposures) + 1))
        for row in existing_rows:
            if row.sort_order in desired_orders:
                continue
            counters["research_session_exposures"]["delete"] += 1
            if apply_changes:
                db_session.delete(row)

    return {"tables": counters}


def run_payload_upsert(
    *,
    release_dir: Path,
    payload_path: Path,
    database_url: str,
    apply_changes: bool,
) -> dict[str, Any]:
    payload = load_payload(payload_path)
    validation = validate_payload_against_release(payload, release_dir)
    engine = create_engine(database_url, future=True)
    _assert_schema_ready(engine)
    session_factory = sessionmaker(bind=engine, future=True)
    now = datetime.now(UTC)

    with session_factory() as db_session:
        before_counts = {
            "research_people": _count_rows(db_session, ResearchPerson),
            "research_sessions": _count_rows(db_session, ResearchSession),
            "research_session_exposures": _count_rows(db_session, ResearchSessionExposure),
        }

    if apply_changes:
        with session_factory.begin() as db_session:
            changes = _plan_and_optionally_apply(db_session, payload, apply_changes=True, now=now)
        with session_factory() as db_session:
            post_validation = _post_upsert_validation(db_session, payload)
    else:
        with session_factory() as db_session:
            changes = _plan_and_optionally_apply(db_session, payload, apply_changes=False, now=now)
        post_validation = {"status": "not_run", "reason": "dry_run"}

    return {
        "mode": "apply" if apply_changes else "dry_run",
        "batch_name": validation["batch_name"],
        "languages": validation["languages"],
        "language_slugs": validation["language_slugs"],
        "payload": {
            "path": str(payload_path),
            "person_count": validation["person_count"],
            "session_count": validation["session_count"],
            "exposure_count": validation["exposure_count"],
            "documented_task_count": validation["documented_task_count"],
        },
        "tables": changes["tables"],
        "pre_upsert_counts": before_counts,
        "post_upsert_validation": post_validation,
        "rollback": (
            "The DB write runs in one SQLAlchemy transaction. On failure it is rolled back automatically; "
            "for manual rollback use the production DB backup/snapshot or restore the affected keys listed in this report."
        ),
        "generated_at": now.isoformat(timespec="seconds"),
    }


def _session_dir_has_task_artifacts(session_dir: Path) -> bool:
    for task_key in SUPPORTED_TASKS:
        if (session_dir / "alignment" / f"{task_key}.json").exists():
            return True
        if (session_dir / "derived" / f"{task_key}.mp3").exists():
            return True
    return False


def run_cleanup_metadata_only(
    *,
    release_dir: Path,
    database_url: str,
    target_language: str,
    apply_cleanup: bool,
) -> dict[str, Any]:
    language = resolve_language_config(target_language)
    sessions_dir = release_dir / "sessions" / language.corpus_slug

    engine = create_engine(database_url, future=True)
    _assert_schema_ready(engine)
    session_factory = sessionmaker(bind=engine, future=True)

    metadata_only_session_ids: list[str] = []
    person_session_ids: dict[str, list[str]] = {}
    exposure_count_to_delete = 0

    with session_factory() as db_session:
        all_db_sessions = db_session.scalars(
            select(ResearchSession).where(ResearchSession.target_language == language.code)
        ).all()

        for db_row in all_db_sessions:
            person_session_ids.setdefault(db_row.person_id, []).append(db_row.session_id)
            session_dir = sessions_dir / db_row.session_id
            if not _session_dir_has_task_artifacts(session_dir):
                metadata_only_session_ids.append(db_row.session_id)
                exp_count = int(
                    db_session.scalar(
                        select(func.count())
                        .select_from(ResearchSessionExposure)
                        .where(ResearchSessionExposure.session_id == db_row.session_id)
                    )
                    or 0
                )
                exposure_count_to_delete += exp_count

        metadata_only_set = set(metadata_only_session_ids)
        persons_to_delete = sorted(
            person_id
            for person_id, session_ids in person_session_ids.items()
            if all(sid in metadata_only_set for sid in session_ids)
        )

    result: dict[str, Any] = {
        "mode": "apply_cleanup" if apply_cleanup else "dry_run",
        "target_language": language.code,
        "corpus": language.corpus_slug,
        "sessions_checked": len(all_db_sessions),
        "sessions_to_delete": sorted(metadata_only_session_ids),
        "persons_to_delete": persons_to_delete,
        "exposures_to_delete": exposure_count_to_delete,
    }

    if apply_cleanup:
        with session_factory.begin() as db_session:
            for session_id in metadata_only_session_ids:
                db_session.execute(
                    delete(ResearchSessionExposure).where(ResearchSessionExposure.session_id == session_id)
                )
                session_row = db_session.get(ResearchSession, session_id)
                if session_row is not None:
                    db_session.delete(session_row)
            for person_id in persons_to_delete:
                person_row = db_session.get(ResearchPerson, person_id)
                if person_row is not None:
                    db_session.delete(person_row)
        result["applied"] = True

    return result


def _post_upsert_validation(db_session: Session, payload: dict[str, Any]) -> dict[str, Any]:
    persons = _require_list(payload, "persons")
    sessions = _require_list(payload, "sessions")
    exposures = _require_list(payload, "exposures") if "exposures" in payload else []
    person_ids = {person["person_id"] for person in persons}
    session_ids = {session["session_id"] for session in sessions}
    missing_people = [person_id for person_id in sorted(person_ids) if db_session.get(ResearchPerson, person_id) is None]
    missing_sessions = [
        session_id for session_id in sorted(session_ids) if db_session.get(ResearchSession, session_id) is None
    ]
    expected_exposure_count = len(exposures)
    actual_exposure_count = int(
        db_session.scalar(
            select(func.count())
            .select_from(ResearchSessionExposure)
            .where(ResearchSessionExposure.session_id.in_(session_ids))
        )
        or 0
    )
    status = "ok" if not missing_people and not missing_sessions and actual_exposure_count == expected_exposure_count else "failed"
    return {
        "status": status,
        "missing_people": missing_people,
        "missing_sessions": missing_sessions,
        "expected_exposure_count": expected_exposure_count,
        "actual_exposure_count": actual_exposure_count,
    }


def _resolve_database_url(explicit_value: str | None) -> str:
    value = (explicit_value or os.getenv("AUTH_DATABASE_URL") or "").strip()
    if not value:
        raise PayloadUpsertError("AUTH_DATABASE_URL or --auth-database-url is required for DB payload upsert")
    return value


def main() -> int:
    args = parse_args()
    try:
        if args.cleanup_metadata_only:
            if args.apply_cleanup and args.dry_run:
                raise PayloadUpsertError("--apply-cleanup and --dry-run cannot be combined")
            if not args.target_language:
                raise PayloadUpsertError("--cleanup-metadata-only requires --target-language")
            if args.apply and not args.cleanup_metadata_only:
                raise PayloadUpsertError("--apply cannot be combined with --cleanup-metadata-only; use --apply-cleanup")
            release_dir = Path(args.release_dir).resolve()
            report = run_cleanup_metadata_only(
                release_dir=release_dir,
                database_url=_resolve_database_url(args.auth_database_url),
                target_language=args.target_language,
                apply_cleanup=args.apply_cleanup,
            )
        else:
            if args.apply and args.dry_run:
                raise PayloadUpsertError("--apply and --dry-run cannot be combined")
            release_dir = Path(args.release_dir).resolve()
            payload_path = Path(args.payload).resolve() if args.payload else release_dir / "db" / "import_payload.json"
            report = run_payload_upsert(
                release_dir=release_dir,
                payload_path=payload_path,
                database_url=_resolve_database_url(args.auth_database_url),
                apply_changes=args.apply,
            )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
