"""Date-based research session access for PROMAT research pages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from .config.data_conventions import TASK_TYPES
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
    duration_months: int | None
    type: str | None
    exposure_notes: str | None


@dataclass(frozen=True)
class ResearchTaskDefinition:
    key: str
    long_label_de: str
    long_label_en: str
    short_label_de: str
    short_label_en: str
    description_de: str
    description_en: str

    def long_label(self, ui_lang: str) -> str:
        return self.long_label_de if ui_lang == "de" else self.long_label_en

    def short_label(self, ui_lang: str) -> str:
        return self.short_label_de if ui_lang == "de" else self.short_label_en

    def description(self, ui_lang: str) -> str:
        return self.description_de if ui_lang == "de" else self.description_en


RESEARCH_TASKS: tuple[ResearchTaskDefinition, ...] = (
    ResearchTaskDefinition(
        key="isolated_speech",
        long_label_de="Isolierte Aussprache (Wortliste)",
        long_label_en="Isolated Speech",
        short_label_de="Wortliste",
        short_label_en="List",
        description_de="Isolierte Aussprache über das Vorlesen einer Wortliste.",
        description_en="Isolated pronunciation through reading a word list aloud.",
    ),
    ResearchTaskDefinition(
        key="connected_speech",
        long_label_de="Zusammenhängende Aussprache (Text/Sätze)",
        long_label_en="Connected Speech",
        short_label_de="Text",
        short_label_en="Text",
        description_de="Zusammenhängende Aussprache über das Vorlesen eines Textes oder einer Satzliste.",
        description_en="Connected pronunciation through reading a text or sentence list aloud.",
    ),
    ResearchTaskDefinition(
        key="interview",
        long_label_de="Interview zur Aussprache",
        long_label_en="Interview",
        short_label_de="Interview",
        short_label_en="Interview",
        description_de="Reflexion über Aussprache im Interview.",
        description_en="Reflection on pronunciation in an interview setting.",
    ),
)

RESEARCH_TASK_MAP = {task.key: task for task in RESEARCH_TASKS}

NATIVE_SPEAKER_EXCLUDED_TASKS: frozenset[str] = frozenset({"interview"})


@dataclass(frozen=True)
class SessionRecord:
    person_id: str
    session_id: str
    target_language: str | None
    speaker_type: str
    l1: str | None
    mother_l1: str | None
    father_l1: str | None
    additional_languages: tuple[str, ...]
    gender: str | None
    birth_year: int | None
    current_region: str | None
    childhood_region: str | None
    origin_region: str | None
    origin_country: str | None
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
    def level_sort_key(self) -> tuple[int, str, str]:
        return (LEVEL_ORDER.get(self.level_code, 999), self.level_code or "", self.session_id)

    @property
    def session_recency_key(self) -> tuple[date, int, int, str]:
        return (
            self.recording_date or date.min,
            self.recording_year or 0,
            len(self.documented_task_types),
            self.session_id,
        )


@dataclass(frozen=True)
class SpeakerProfile:
    person_id: str
    primary_session: SessionRecord
    sessions: tuple[SessionRecord, ...]

    @property
    def level_sort_key(self) -> tuple[int, str, str]:
        return self.primary_session.level_sort_key


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
                    duration_months=duration_months if isinstance(duration_months, int) else _metadata_int(raw_entry, "duration_months"),
                    type=exposure_type.strip() if isinstance(exposure_type, str) and exposure_type.strip() else None,
                    exposure_notes=exposure_notes.strip() if isinstance(exposure_notes, str) and exposure_notes.strip() else None,
                )
            )
        return tuple(entries)

    country = _metadata_string(metadata, "country")
    duration_months = _metadata_int(metadata, "duration_months")
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
        if isinstance(task_type, str) and task_type in TASK_TYPES and task_type not in resolved:
            resolved.append(task_type)
    return tuple(resolved)


def _read_session_record(metadata_path: Path) -> SessionRecord:
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid session metadata in {metadata_path}")

    return SessionRecord(
        person_id=str(payload.get("person_id") or ""),
        session_id=str(payload.get("session_id") or metadata_path.parent.name),
        target_language=_metadata_string(payload, "target_language"),
        speaker_type=str(payload.get("speaker_type") or "unknown"),
        l1=_metadata_string(payload, "l1"),
        mother_l1=_metadata_string(payload, "mother_l1"),
        father_l1=_metadata_string(payload, "father_l1"),
        additional_languages=_normalize_string_list(payload.get("additional_languages")),
        gender=_metadata_string(payload, "gender"),
        birth_year=payload.get("birth_year") if isinstance(payload.get("birth_year"), int) else None,
        current_region=_metadata_string(payload, "current_region"),
        childhood_region=_metadata_string(payload, "childhood_region"),
        origin_region=_metadata_string(payload, "origin_region"),
        origin_country=_metadata_string(payload, "origin_country"),
        level_code=_metadata_string(payload, "level_code"),
        level_self=_metadata_string(payload, "level_self"),
        standard_variety=_metadata_string(payload, "standard_variety"),
        recording_year=payload.get("recording_year") if isinstance(payload.get("recording_year"), int) else None,
        recording_date=_parse_iso_date(payload.get("recording_date")),
        context=_metadata_string(payload, "context"),
        recorded_by=_metadata_string(payload, "recorded_by"),
        notes=_metadata_string(payload, "notes"),
        documented_task_types=_extract_task_types(payload),
        stays_in_target_country=_resolve_stays_in_target_country(payload),
        exposure_entries=_extract_exposure_entries(payload),
        metadata_path=metadata_path,
        raw_metadata=payload,
    )


def _session_sort_key(session: SessionRecord) -> tuple[int, str, str]:
    return (LEVEL_ORDER.get(session.level_code, 999), session.session_id, session.person_id)


@lru_cache(maxsize=16)
def load_language_sessions(language_slug: str) -> tuple[SessionRecord, ...]:
    sessions_root = get_sessions_root() / language_slug
    if not sessions_root.exists():
        return tuple()

    records = [
        _read_session_record(metadata_path)
        for metadata_path in sorted(sessions_root.glob("*/metadata.json"))
    ]
    records.sort(key=_session_sort_key)
    return tuple(records)


@lru_cache(maxsize=16)
def load_speaker_profiles(language_slug: str) -> tuple[SpeakerProfile, ...]:
    grouped: dict[str, list[SessionRecord]] = {}
    for session in load_language_sessions(language_slug):
        grouped.setdefault(session.person_id, []).append(session)

    profiles: list[SpeakerProfile] = []
    for person_id, sessions in grouped.items():
        sorted_sessions = tuple(sorted(sessions, key=lambda item: item.session_recency_key, reverse=True))
        profiles.append(
            SpeakerProfile(
                person_id=person_id,
                primary_session=sorted_sessions[0],
                sessions=sorted_sessions,
            )
        )

    profiles.sort(key=lambda profile: profile.level_sort_key)
    return tuple(profiles)


def get_session(language_slug: str, session_id: str) -> SessionRecord | None:
    for session in load_language_sessions(language_slug):
        if session.session_id == session_id:
            return session
    return None


def get_speaker_profile(language_slug: str, person_id: str) -> SpeakerProfile | None:
    for profile in load_speaker_profiles(language_slug):
        if profile.person_id == person_id:
            return profile
    return None


def iter_research_tasks() -> Iterable[ResearchTaskDefinition]:
    return RESEARCH_TASKS


def get_research_task(task_key: str) -> ResearchTaskDefinition | None:
    return RESEARCH_TASK_MAP.get(task_key)


def available_task_keys_for_session(session: SessionRecord) -> tuple[str, ...]:
    available_task_keys = set(session.documented_task_types)
    if session.speaker_type == "native_speaker":
        available_task_keys.difference_update(NATIVE_SPEAKER_EXCLUDED_TASKS)
    return tuple(task.key for task in RESEARCH_TASKS if task.key in available_task_keys)


def session_has_task(session: SessionRecord, task_key: str) -> bool:
    return task_key in available_task_keys_for_session(session)