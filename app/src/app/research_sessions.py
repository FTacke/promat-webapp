"""Date-based person and session access for PROMAT research pages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping

from .config.data_conventions import (
    PersonIdParts,
    SessionIdParts,
    get_corpus_code_for_language_slug,
    get_corpus_code_for_target_language,
    normalize_l1_code,
    normalize_l1_code_list,
    parse_person_id,
    parse_session_id,
)
from .research_capabilities import (
    RESEARCH_TASK_KEYS,
    ResearchTaskCapability,
    available_task_keys_for_session as resolve_available_task_keys_for_session,
    get_research_task_capability,
    iter_research_task_capabilities,
)
from .runtime_paths import get_sessions_root


LEVEL_ORDER = {
    "A1": 10,
    "A2": 20,
    "B1": 30,
    "B2": 40,
    "C1": 50,
    "C2": 60,
}

TARGET_COUNTRY_STAY_FIELD_CANDIDATES: tuple[str, ...] = (
    "stays_in_target_country",
)

LEGACY_EXPOSURE_FIELD_CANDIDATES: tuple[str, ...] = (
    "previous_exposure",
    "has_previous_exposure",
    "prior_exposure",
    "prior_exposure_flag",
    "exposure_flag",
)

LEGACY_EXPOSURE_COLLECTION_CANDIDATES: tuple[str, ...] = (
    "exposure",
    "exposures",
    "exposure_history",
    "exposure_entries",
)


@dataclass(frozen=True)
class ExposureEntry:
    country: str | None
    duration_months: float | None
    type: str | None
    exposure_notes: str | None


ResearchTaskDefinition = ResearchTaskCapability

RESEARCH_TASKS: tuple[ResearchTaskDefinition, ...] = tuple(iter_research_task_capabilities())
RESEARCH_TASK_MAP = {task.key: task for task in RESEARCH_TASKS}


@dataclass(frozen=True)
class SessionRecord:
    person_id: str
    person_id_parts: PersonIdParts
    session_id: str
    session_id_parts: SessionIdParts
    target_language: str | None
    speaker_type: str
    l1: str | None
    l1_additional: tuple[str, ...]
    mother_l1: str | None
    father_l1: str | None
    additional_languages: tuple[str, ...]
    gender: str | None
    birth_year: int | None
    current_region: str | None
    childhood_region: str | None
    origin_region: str | None
    origin_country: str | None
    person_notes: str | None
    research_consent_signed: str | None
    teaching_consent_signed: str | None
    consent_date: date | None
    consent_file: str | None
    questionnaire_file: str | None
    secure_notes: str | None
    level_code: str | None
    level_self: str | None
    standard_variety: str | None
    recording_year: int | None
    recording_date: date | None
    context: str | None
    recorded_by: str | None
    notes: str | None
    documented_task_types: tuple[str, ...]
    stays_in_target_country: bool | None
    exposure_entries: tuple[ExposureEntry, ...]
    metadata_path: Path
    raw_metadata: dict[str, Any]

    @property
    def is_native(self) -> bool:
        return self.speaker_type == "native_speaker"

    @property
    def session_number(self) -> int:
        return self.session_id_parts.session_number

    @property
    def recording_year_value(self) -> int:
        return self.recording_year or self.session_id_parts.recording_year

    @property
    def level_sort_key(self) -> tuple[int, int, int, str]:
        return (
            LEVEL_ORDER.get(self.level_code, 999),
            self.recording_year_value,
            self.session_number,
            self.session_id,
        )

    @property
    def session_recency_key(self) -> tuple[date, int, int, int, str]:
        return (
            self.recording_date or date.min,
            self.recording_year_value,
            self.session_number,
            len(self.documented_task_types),
            self.session_id,
        )


@dataclass(frozen=True)
class PersonRecord:
    person_id: str
    person_id_parts: PersonIdParts
    speaker_type: str
    target_language: str | None
    l1: str | None
    l1_additional: tuple[str, ...]
    mother_l1: str | None
    father_l1: str | None
    additional_languages: tuple[str, ...]
    gender: str | None
    birth_year: int | None
    current_region: str | None
    childhood_region: str | None
    origin_region: str | None
    origin_country: str | None
    standard_variety: str | None
    person_notes: str | None
    research_consent_signed: str | None
    teaching_consent_signed: str | None
    consent_date: date | None
    consent_file: str | None
    questionnaire_file: str | None
    secure_notes: str | None
    sessions: tuple[SessionRecord, ...]

    @property
    def is_native(self) -> bool:
        return self.speaker_type == "native_speaker"

    @property
    def latest_session(self) -> SessionRecord:
        return self.sessions[0]

    @property
    def session_count(self) -> int:
        return len(self.sessions)

    @property
    def level_codes(self) -> tuple[str, ...]:
        values = {session.level_code for session in self.sessions if session.level_code}
        return tuple(sorted(values, key=lambda value: LEVEL_ORDER.get(value, 999)))

    @property
    def recording_years(self) -> tuple[int, ...]:
        values = {session.recording_year_value for session in self.sessions}
        return tuple(sorted(values))

    @property
    def available_task_keys(self) -> tuple[str, ...]:
        available: set[str] = set()
        for session in self.sessions:
            available.update(available_task_keys_for_session(session))
        return tuple(task.key for task in RESEARCH_TASKS if task.key in available)


SpeakerProfile = PersonRecord


def _parse_iso_date(value: Any) -> date | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _normalize_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value in (0, 1):
            return bool(value)
        return None
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "ja"}:
            return True
        if normalized in {"0", "false", "no", "nein"}:
            return False
    return None


def _metadata_string(metadata: dict[str, Any], field_name: str) -> str | None:
    value = metadata.get(field_name)
    return value if isinstance(value, str) else None


def _metadata_int(metadata: dict[str, Any], field_name: str) -> int | None:
    value = metadata.get(field_name)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.isdigit():
            return int(normalized)
    return None


def _metadata_float(metadata: dict[str, Any], field_name: str) -> float | None:
    value = metadata.get(field_name)
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        normalized = value.strip().replace(",", ".")
        if not normalized:
            return None
        try:
            return float(Decimal(normalized))
        except (InvalidOperation, ValueError):
            return None
    return None


def _normalize_string_list(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(str(item).strip() for item in value if isinstance(item, str) and item.strip())
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(";")]
        return tuple(part for part in parts if part)
    return tuple()


def _extract_exposure_entries(metadata: dict[str, Any]) -> tuple[ExposureEntry, ...]:
    raw_entries = metadata.get("exposure_entries")
    if isinstance(raw_entries, list):
        entries: list[ExposureEntry] = []
        for raw_entry in raw_entries:
            if not isinstance(raw_entry, dict):
                continue
            country = raw_entry.get("country")
            duration_months = raw_entry.get("duration_months")
            exposure_type = raw_entry.get("type")
            exposure_notes = raw_entry.get("exposure_notes")
            if not any((country, duration_months, exposure_type, exposure_notes)):
                continue
            entries.append(
                ExposureEntry(
                    country=country.strip() if isinstance(country, str) and country.strip() else None,
                    duration_months=(
                        float(duration_months)
                        if isinstance(duration_months, (int, float)) and not isinstance(duration_months, bool)
                        else _metadata_float(raw_entry, "duration_months")
                    ),
                    type=exposure_type.strip() if isinstance(exposure_type, str) and exposure_type.strip() else None,
                    exposure_notes=exposure_notes.strip() if isinstance(exposure_notes, str) and exposure_notes.strip() else None,
                )
            )
        return tuple(entries)

    country = _metadata_string(metadata, "country")
    duration_months = _metadata_float(metadata, "duration_months")
    exposure_type = _metadata_string(metadata, "type")
    exposure_notes = _metadata_string(metadata, "exposure_notes")
    if any((country, duration_months, exposure_type, exposure_notes)):
        return (
            ExposureEntry(
                country=country,
                duration_months=duration_months,
                type=exposure_type,
                exposure_notes=exposure_notes,
            ),
        )

    return tuple()


def _resolve_stays_in_target_country(metadata: dict[str, Any]) -> bool | None:
    for field_name in TARGET_COUNTRY_STAY_FIELD_CANDIDATES:
        if field_name in metadata:
            normalized = _normalize_bool(metadata.get(field_name))
            if normalized is not None:
                return normalized

    if _extract_exposure_entries(metadata):
        return True

    for field_name in LEGACY_EXPOSURE_FIELD_CANDIDATES:
        if field_name in metadata:
            normalized = _normalize_bool(metadata.get(field_name))
            if normalized is not None:
                return normalized

    for field_name in LEGACY_EXPOSURE_COLLECTION_CANDIDATES:
        if field_name not in metadata:
            continue
        value = metadata.get(field_name)
        if isinstance(value, list):
            return True if value else False
        normalized = _normalize_bool(value)
        if normalized is not None:
            return normalized

    exposure_notes = metadata.get("exposure_notes")
    if isinstance(exposure_notes, str) and exposure_notes.strip():
        return True

    return None


def _extract_task_types(metadata: dict[str, Any]) -> tuple[str, ...]:
    tasks = metadata.get("tasks")
    if not isinstance(tasks, list):
        return tuple()

    resolved: list[str] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        task_type = task.get("task_type")
        if isinstance(task_type, str) and task_type in RESEARCH_TASK_KEYS and task_type not in resolved:
            resolved.append(task_type)
    return tuple(resolved)


def _require_person_id_parts(person_id: str, metadata_path: Path) -> PersonIdParts:
    person_id_parts = parse_person_id(person_id)
    if person_id_parts is None:
        raise ValueError(f"Invalid person_id in {metadata_path}: {person_id}")
    return person_id_parts


def _require_session_id_parts(session_id: str, metadata_path: Path) -> SessionIdParts:
    session_id_parts = parse_session_id(session_id)
    if session_id_parts is None:
        raise ValueError(f"Invalid session_id in {metadata_path}: {session_id}")
    return session_id_parts


def _validate_session_identity(
    metadata_path: Path,
    person_id: str,
    person_id_parts: PersonIdParts,
    session_id: str,
    session_id_parts: SessionIdParts,
    speaker_type: str,
    target_language: str | None,
    recording_year: int | None,
) -> None:
    if metadata_path.parent.name != session_id:
        raise ValueError(f"Session directory and session_id differ in {metadata_path}: {metadata_path.parent.name} != {session_id}")
    if session_id_parts.person_id != person_id:
        raise ValueError(f"session_id does not embed person_id in {metadata_path}: {session_id}")
    if person_id_parts.speaker_type != speaker_type:
        raise ValueError(f"person_id speaker marker does not match speaker_type in {metadata_path}: {person_id}")
    if recording_year is not None and session_id_parts.recording_year != recording_year:
        raise ValueError(f"session_id recording year does not match metadata in {metadata_path}: {session_id}")
    expected_corpus_code = get_corpus_code_for_target_language(target_language or "")
    if expected_corpus_code is not None and person_id_parts.corpus_code != expected_corpus_code:
        raise ValueError(f"person_id corpus code does not match target_language in {metadata_path}: {person_id}")


def _read_session_record(metadata_path: Path) -> SessionRecord:
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid session metadata in {metadata_path}")

    person_id = str(payload.get("person_id") or "").strip()
    session_id = str(payload.get("session_id") or "").strip()
    if not person_id or not session_id:
        raise ValueError(f"person_id and session_id are required in {metadata_path}")

    speaker_type = str(payload.get("speaker_type") or "").strip()
    if not speaker_type:
        raise ValueError(f"speaker_type is required in {metadata_path}")

    target_language = _metadata_string(payload, "target_language")
    recording_year = _metadata_int(payload, "recording_year")
    person_id_parts = _require_person_id_parts(person_id, metadata_path)
    session_id_parts = _require_session_id_parts(session_id, metadata_path)

    _validate_session_identity(
        metadata_path,
        person_id,
        person_id_parts,
        session_id,
        session_id_parts,
        speaker_type,
        target_language,
        recording_year,
    )

    return SessionRecord(
        person_id=person_id,
        person_id_parts=person_id_parts,
        session_id=session_id,
        session_id_parts=session_id_parts,
        target_language=target_language,
        speaker_type=speaker_type,
        l1=normalize_l1_code(payload.get("l1")),
        l1_additional=normalize_l1_code_list(payload.get("l1_additional")),
        mother_l1=normalize_l1_code(payload.get("mother_l1")),
        father_l1=normalize_l1_code(payload.get("father_l1")),
        additional_languages=_normalize_string_list(payload.get("additional_languages")),
        gender=_metadata_string(payload, "gender"),
        birth_year=_metadata_int(payload, "birth_year"),
        current_region=_metadata_string(payload, "current_region"),
        childhood_region=_metadata_string(payload, "childhood_region"),
        origin_region=_metadata_string(payload, "origin_region"),
        origin_country=_metadata_string(payload, "origin_country"),
        person_notes=_metadata_string(payload, "person_notes"),
        research_consent_signed=_metadata_string(payload, "research_consent_signed"),
        teaching_consent_signed=_metadata_string(payload, "teaching_consent_signed"),
        consent_date=_parse_iso_date(payload.get("consent_date")),
        consent_file=_metadata_string(payload, "consent_file"),
        questionnaire_file=_metadata_string(payload, "questionnaire_file"),
        secure_notes=_metadata_string(payload, "secure_notes"),
        level_code=_metadata_string(payload, "level_code"),
        level_self=_metadata_string(payload, "level_self"),
        standard_variety=_metadata_string(payload, "standard_variety"),
        recording_year=recording_year,
        recording_date=_parse_iso_date(payload.get("recording_date")),
        context=_metadata_string(payload, "context"),
        recorded_by=_metadata_string(payload, "recorded_by"),
        notes=_metadata_string(payload, "session_notes") or _metadata_string(payload, "notes"),
        documented_task_types=_extract_task_types(payload),
        stays_in_target_country=_resolve_stays_in_target_country(payload),
        exposure_entries=_extract_exposure_entries(payload),
        metadata_path=metadata_path,
        raw_metadata=payload,
    )


def sort_sessions_by_recency(sessions: Iterable[SessionRecord]) -> tuple[SessionRecord, ...]:
    return tuple(sorted(sessions, key=lambda item: item.session_recency_key, reverse=True))


def _session_display_sort_key(session: SessionRecord) -> tuple[int, int, int, int, str]:
    parsed_session = parse_session_id(session.session_id)
    if parsed_session is None:
        return (2, 0, 0, 0, session.session_id)
    parsed_person = parse_person_id(parsed_session.person_id)
    if parsed_person is None:
        return (2, 0, 0, 0, session.session_id)
    # L→0 (learner first), N→1 (native second), unknown→2 (fallback to end)
    marker_order = {"L": 0, "N": 1}
    speaker_type_order = marker_order.get(parsed_person.speaker_marker, 2)
    return (speaker_type_order, parsed_person.sequence, parsed_session.recording_year, parsed_session.session_number, session.session_id)


def sort_sessions_for_display(sessions: Iterable[SessionRecord]) -> tuple[SessionRecord, ...]:
    """Sort for dropdown display: learners (L) first then natives (N), each group numerically."""
    return tuple(sorted(sessions, key=_session_display_sort_key))


def _latest_non_empty_value(sessions: Iterable[SessionRecord], field_name: str) -> Any:
    for session in sort_sessions_by_recency(sessions):
        value = getattr(session, field_name)
        if isinstance(value, tuple):
            if value:
                return value
            continue
        if value not in (None, ""):
            return value
    return tuple() if field_name in {"l1_additional", "additional_languages"} else None


def _validate_language_scope(language_slug: str, session: SessionRecord) -> None:
    expected_corpus_code = get_corpus_code_for_language_slug(language_slug)
    if expected_corpus_code is None:
        raise ValueError(f"Unsupported language slug: {language_slug}")
    if session.person_id_parts.corpus_code != expected_corpus_code:
        raise ValueError(
            f"person_id corpus code does not match language folder for {session.metadata_path}: {session.person_id}"
        )


def _aggregate_person_record(person_id: str, sessions: Iterable[SessionRecord]) -> PersonRecord:
    sorted_sessions = sort_sessions_by_recency(sessions)
    if not sorted_sessions:
        raise ValueError(f"Cannot aggregate person without sessions: {person_id}")

    speaker_types = {session.speaker_type for session in sorted_sessions}
    if len(speaker_types) != 1:
        raise ValueError(f"person_id mixes speaker types: {person_id}")

    speaker_type = sorted_sessions[0].speaker_type
    if speaker_type == "native_speaker" and len(sorted_sessions) != 1:
        raise ValueError(f"native_speaker person_id must map to exactly one session: {person_id}")

    return PersonRecord(
        person_id=person_id,
        person_id_parts=sorted_sessions[0].person_id_parts,
        speaker_type=speaker_type,
        target_language=_latest_non_empty_value(sorted_sessions, "target_language"),
        l1=_latest_non_empty_value(sorted_sessions, "l1"),
        l1_additional=_latest_non_empty_value(sorted_sessions, "l1_additional"),
        mother_l1=_latest_non_empty_value(sorted_sessions, "mother_l1"),
        father_l1=_latest_non_empty_value(sorted_sessions, "father_l1"),
        additional_languages=_latest_non_empty_value(sorted_sessions, "additional_languages"),
        gender=_latest_non_empty_value(sorted_sessions, "gender"),
        birth_year=_latest_non_empty_value(sorted_sessions, "birth_year"),
        current_region=_latest_non_empty_value(sorted_sessions, "current_region"),
        childhood_region=_latest_non_empty_value(sorted_sessions, "childhood_region"),
        origin_region=_latest_non_empty_value(sorted_sessions, "origin_region"),
        origin_country=_latest_non_empty_value(sorted_sessions, "origin_country"),
        standard_variety=_latest_non_empty_value(sorted_sessions, "standard_variety"),
        person_notes=_latest_non_empty_value(sorted_sessions, "person_notes"),
        research_consent_signed=_latest_non_empty_value(sorted_sessions, "research_consent_signed"),
        teaching_consent_signed=_latest_non_empty_value(sorted_sessions, "teaching_consent_signed"),
        consent_date=_latest_non_empty_value(sorted_sessions, "consent_date"),
        consent_file=_latest_non_empty_value(sorted_sessions, "consent_file"),
        questionnaire_file=_latest_non_empty_value(sorted_sessions, "questionnaire_file"),
        secure_notes=_latest_non_empty_value(sorted_sessions, "secure_notes"),
        sessions=sorted_sessions,
    )


@lru_cache(maxsize=16)
def load_language_sessions(language_slug: str) -> tuple[SessionRecord, ...]:
    sessions_root = get_sessions_root() / language_slug
    if not sessions_root.exists():
        return tuple()

    records: list[SessionRecord] = []
    for metadata_path in sorted(sessions_root.glob("*/metadata.json")):
        session = _read_session_record(metadata_path)
        _validate_language_scope(language_slug, session)
        records.append(session)

    return tuple(records)


@lru_cache(maxsize=16)
def load_person_records(language_slug: str) -> tuple[PersonRecord, ...]:
    grouped: dict[str, list[SessionRecord]] = {}
    for session in load_language_sessions(language_slug):
        grouped.setdefault(session.person_id, []).append(session)

    records = [_aggregate_person_record(person_id, sessions) for person_id, sessions in grouped.items()]
    records.sort(key=lambda record: record.person_id)
    return tuple(records)


def load_speaker_profiles(language_slug: str) -> tuple[SpeakerProfile, ...]:
    return load_person_records(language_slug)


def get_session(language_slug: str, session_id: str) -> SessionRecord | None:
    for session in load_language_sessions(language_slug):
        if session.session_id == session_id:
            return session
    return None


def get_person_record(language_slug: str, person_id: str) -> PersonRecord | None:
    for person in load_person_records(language_slug):
        if person.person_id == person_id:
            return person
    return None


def get_speaker_profile(language_slug: str, person_id: str) -> SpeakerProfile | None:
    return get_person_record(language_slug, person_id)


def resolve_selected_session(
    person: PersonRecord,
    requested_session_id: str | None = None,
    preferred_session_ids: Iterable[str] | None = None,
) -> SessionRecord:
    if requested_session_id:
        for session in person.sessions:
            if session.session_id == requested_session_id:
                return session

    if preferred_session_ids is not None:
        preferred_ids = {session_id for session_id in preferred_session_ids if session_id}
        for session in person.sessions:
            if session.session_id in preferred_ids:
                return session

    return person.latest_session


def session_matches_filters(session: SessionRecord, filters: Mapping[str, str]) -> bool:
    speaker_group = (filters.get("speaker_group") or filters.get("speaker_type") or "").strip()
    if speaker_group and speaker_group != "all" and session.speaker_type != speaker_group:
        return False
    if filters.get("level") and session.level_code != filters.get("level"):
        return False
    if filters.get("l1") and (session.l1 or "").upper() != (filters.get("l1") or "").upper():
        return False
    if filters.get("gender") and session.gender != filters.get("gender"):
        return False
    if filters.get("target_country_stay") == "yes" and session.stays_in_target_country is not True:
        return False
    if filters.get("target_country_stay") == "no" and session.stays_in_target_country is not False:
        return False
    if filters.get("standard_variety") and session.standard_variety != filters.get("standard_variety"):
        return False
    if filters.get("origin_country") and session.origin_country != filters.get("origin_country"):
        return False
    return True


def matching_sessions_for_person(person: PersonRecord, filters: Mapping[str, str]) -> tuple[SessionRecord, ...]:
    matched = [session for session in person.sessions if session_matches_filters(session, filters)]
    return sort_sessions_by_recency(matched)


def iter_research_tasks() -> Iterable[ResearchTaskDefinition]:
    return RESEARCH_TASKS


def get_research_task(task_key: str) -> ResearchTaskDefinition | None:
    return get_research_task_capability(task_key)


def available_task_keys_for_session(session: SessionRecord) -> tuple[str, ...]:
    return resolve_available_task_keys_for_session(session.documented_task_types, session.speaker_type)


def session_has_task(session: SessionRecord, task_key: str) -> bool:
    return task_key in available_task_keys_for_session(session)