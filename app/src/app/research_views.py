"""View-model builders for PROMAT research workbench pages."""

from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import urlencode

from flask import url_for

from .content_navigation import build_content_header
from .research_sessions import (
    LEVEL_ORDER,
    PersonRecord,
    SessionRecord,
    get_person_record,
    get_research_task,
    get_session,
    iter_research_tasks,
    load_language_sessions,
    load_person_records,
    matching_sessions_for_person,
    resolve_selected_session,
    session_has_task,
    session_matches_filters,
    sort_sessions_by_recency,
)
from .routes.public_content import get_language, get_language_label, get_research_page_label, get_section_label


SPEAKER_TYPE_LABELS = {
    "learner": {"de": "Lernende", "en": "Learner"},
    "native_speaker": {"de": "Native Speaker", "en": "Native Speaker"},
    "unknown": {"de": "Unbekannt", "en": "Unknown"},
}

GENDER_LABELS = {
    "female": {"de": "weiblich", "en": "female"},
    "male": {"de": "männlich", "en": "male"},
    "diverse": {"de": "divers", "en": "diverse"},
    "unknown": {"de": "unbekannt", "en": "unknown"},
}

TARGET_COUNTRY_STAY_LABELS = {
    True: {"de": "Ja", "en": "Yes"},
    False: {"de": "Nein", "en": "No"},
    None: {"de": "Nicht erfasst", "en": "Not recorded"},
}

SPEAKER_GROUPS = (
    ("all", {"de": "Alle", "en": "All"}),
    ("learner", {"de": "Lernende", "en": "Learners"}),
    ("native_speaker", {"de": "Native Speaker", "en": "Native Speakers"}),
)

RESEARCH_PAGE_INTROS = {
    "recordings": {
        "de": "Session- und taskbasierter Zugang zum spanischen Korpus mit klar sichtbarem Bezug von Person zu Session und Aufzeichnung.",
        "en": "Session- and task-based access to the Spanish corpus with a clear person-to-session-to-recording relation.",
    },
    "speakers": {
        "de": "Personbasierter Zugang zum spanischen Korpus. Eine Person erscheint genau einmal und matched, sobald mindestens eine ihrer Sessions alle aktiven Filter erfüllt.",
        "en": "Person-based access to the Spanish corpus. A person appears exactly once and matches as soon as at least one of their sessions satisfies all active filters.",
    },
}

EXPOSURE_TYPE_LABELS = {
    "erasmus": {"de": "Erasmus", "en": "Erasmus"},
    "study": {"de": "Studium", "en": "Study"},
    "study_abroad": {"de": "Studium", "en": "Study abroad"},
    "work": {"de": "Arbeit", "en": "Work"},
    "travel": {"de": "Reise", "en": "Travel"},
    "family": {"de": "Familie", "en": "Family"},
    "other": {"de": "Sonstiges", "en": "Other"},
}


def _label(mapping: dict[str, dict[str, str]], key: str, ui_lang: str) -> str:
    return mapping.get(key, mapping.get("unknown", {"de": key, "en": key})).get(ui_lang, key)


def _format_level(session: SessionRecord, ui_lang: str) -> str:
    del ui_lang
    return session.level_code or "-"


def _format_standard_variety(session: SessionRecord) -> str:
    if not session.standard_variety:
        return "-"
    return session.standard_variety.upper()


def _format_target_country_stay(stays_in_target_country: bool | None, ui_lang: str) -> str:
    return TARGET_COUNTRY_STAY_LABELS[stays_in_target_country][ui_lang]


def _target_country_stay_label(ui_lang: str) -> str:
    return "Sprachaufenthalte" if ui_lang == "de" else "Stays in target-language country"


def _standard_variety_label(ui_lang: str) -> str:
    return "Standardvarietät" if ui_lang == "de" else "Standard variety"


def _origin_country_label(ui_lang: str) -> str:
    return "Herkunftsland" if ui_lang == "de" else "Origin country"


def _origin_region_label(ui_lang: str) -> str:
    return "Herkunftsregion" if ui_lang == "de" else "Origin region"


def _recorded_by_label(ui_lang: str) -> str:
    return "Explorator:in" if ui_lang == "de" else "Recorded by"


def _mother_l1_label(ui_lang: str) -> str:
    return "L1 der Mutter" if ui_lang == "de" else "Mother L1"


def _father_l1_label(ui_lang: str) -> str:
    return "L1 des Vaters" if ui_lang == "de" else "Father L1"


def _additional_languages_label(ui_lang: str) -> str:
    return "Zusätzliche Sprachen" if ui_lang == "de" else "Additional languages"


def _humanize_value(value: str | None) -> str:
    if not value:
        return "-"
    return value.replace("_", " ").replace("-", " ").strip().title()


def _format_additional_languages(values: tuple[str, ...]) -> str:
    if not values:
        return "-"
    return ", ".join(values)


def _format_duration_months(duration_months: int | None, ui_lang: str) -> str | None:
    if duration_months is None:
        return None
    if ui_lang == "de":
        return f"{duration_months} Monat" if duration_months == 1 else f"{duration_months} Monate"
    return f"{duration_months} month" if duration_months == 1 else f"{duration_months} months"


def _format_exposure_type(exposure_type: str | None, ui_lang: str) -> str | None:
    if not exposure_type:
        return None
    normalized = exposure_type.strip().lower()
    if normalized in EXPOSURE_TYPE_LABELS:
        return EXPOSURE_TYPE_LABELS[normalized][ui_lang]
    return _humanize_value(normalized)


def _build_exposure_row(session: SessionRecord, ui_lang: str) -> dict[str, Any]:
    label = _target_country_stay_label(ui_lang)
    if session.exposure_entries:
        entries = []
        for entry in session.exposure_entries:
            parts = []
            if entry.country:
                parts.append(_humanize_value(entry.country))
            duration = _format_duration_months(entry.duration_months, ui_lang)
            if duration:
                parts.append(duration)
            exposure_type = _format_exposure_type(entry.type, ui_lang)
            if exposure_type:
                parts.append(exposure_type)
            entries.append(
                {
                    "text": " · ".join(parts) if parts else ("Sprachaufenthalt" if ui_lang == "de" else "Language stay"),
                    "note": entry.exposure_notes or "",
                }
            )
        return {"label": label, "kind": "exposure", "entries": entries}

    if session.stays_in_target_country is False:
        return {
            "label": label,
            "kind": "exposure",
            "value": "Keine erfassten Sprachaufenthalte" if ui_lang == "de" else "No recorded stays in the target-language country",
        }

    if session.stays_in_target_country is True:
        return {
            "label": label,
            "kind": "exposure",
            "value": "Erfasst, ohne Detailangaben" if ui_lang == "de" else "Recorded without detailed stay information",
        }

    return {"label": label, "kind": "exposure", "value": "Nicht erfasst" if ui_lang == "de" else "Not recorded"}


def _uses_native_filters(selected_group: str) -> bool:
    return selected_group == "native_speaker"


def _sorted_distinct(values: list[str | None]) -> list[str]:
    return sorted({value for value in values if value})


def _flatten_person_sessions(persons: list[PersonRecord]) -> list[SessionRecord]:
    sessions: list[SessionRecord] = []
    for person in persons:
        sessions.extend(person.sessions)
    return sessions


def _normalize_text(value: str | None) -> str | None:
    normalized = (value or "").strip()
    return normalized or None


def _normalize_recordings_filters(query_args: Mapping[str, str]) -> dict[str, str]:
    active_task = _normalize_text(query_args.get("task")) or "wordlist"
    if get_research_task(active_task) is None:
        active_task = "wordlist"
    return {
        "task": active_task,
        "level": _normalize_text(query_args.get("level")) or "",
        "l1": (_normalize_text(query_args.get("l1")) or "").upper(),
        "speaker_type": _normalize_text(query_args.get("speaker_type")) or "",
        "gender": _normalize_text(query_args.get("gender")) or "",
        "target_country_stay": _normalize_text(query_args.get("target_country_stay")) or "",
        "standard_variety": _normalize_text(query_args.get("standard_variety")) or "",
        "origin_country": _normalize_text(query_args.get("origin_country")) or "",
    }


def _normalize_speakers_filters(query_args: Mapping[str, str]) -> dict[str, str]:
    speaker_group = _normalize_text(query_args.get("speaker_group")) or "all"
    if speaker_group not in {key for key, _ in SPEAKER_GROUPS}:
        speaker_group = "all"
    return {
        "speaker_group": speaker_group,
        "level": _normalize_text(query_args.get("level")) or "",
        "l1": (_normalize_text(query_args.get("l1")) or "").upper(),
        "gender": _normalize_text(query_args.get("gender")) or "",
        "target_country_stay": _normalize_text(query_args.get("target_country_stay")) or "",
        "standard_variety": _normalize_text(query_args.get("standard_variety")) or "",
        "origin_country": _normalize_text(query_args.get("origin_country")) or "",
    }


def _recordings_section_label(ui_lang: str) -> str:
    return "Aufzeichnungen" if ui_lang == "de" else "Recordings"


def _recording_links_aria_label(ui_lang: str) -> str:
    return "Direktlinks zu Aufzeichnungen" if ui_lang == "de" else "Direct links to recordings"


def _unavailable_label(ui_lang: str) -> str:
    return "Nicht verfügbar" if ui_lang == "de" else "Not available"


def _url_with_query(endpoint: str, *, query: Mapping[str, str] | None = None, **values: Any) -> str:
    base_url = url_for(endpoint, **values)
    if not query:
        return base_url

    cleaned = [(key, value) for key, value in query.items() if value not in (None, "")]
    if not cleaned:
        return base_url
    return f"{base_url}?{urlencode(cleaned)}"


def _language_context(ui_lang: str, language_slug: str) -> tuple[dict[str, Any], str]:
    language = get_language(language_slug)
    if language is None:
        raise LookupError(f"Unsupported language slug: {language_slug}")
    language_label = get_language_label(language, ui_lang)
    return language, language_label


def _filter_chip(label: str, endpoint: str, *, query: Mapping[str, str], drop_key: str, **values: Any) -> dict[str, str]:
    next_query = dict(query)
    next_query.pop(drop_key, None)
    return {"label": label, "href": _url_with_query(endpoint, query=next_query, **values)}


def _session_accent_modifier(session: SessionRecord) -> str:
    if session.is_native or not session.level_code:
        return "native"
    return session.level_code.lower()


def _format_recording_date(session: SessionRecord) -> str:
    return session.recording_date.isoformat() if session.recording_date else "-"


def _format_recording_year(session: SessionRecord) -> str:
    return str(session.recording_year_value) if session.recording_year_value else "-"


def _recording_year_span(person: PersonRecord) -> str:
    if not person.recording_years:
        return "-"
    if len(person.recording_years) == 1:
        return str(person.recording_years[0])
    return f"{person.recording_years[0]}–{person.recording_years[-1]}"


def _session_count_label(ui_lang: str) -> str:
    return "Zugeordnete Sessions" if ui_lang == "de" else "Associated sessions"


def _build_task_item(session: SessionRecord, task_key: str, ui_lang: str, language_slug: str, source: str) -> dict[str, Any]:
    task = get_research_task(task_key)
    if task is None:
        raise LookupError(f"Unsupported task: {task_key}")

    is_available = session_has_task(session, task.key)
    return {
        "key": task.key,
        "label": task.short_label(ui_lang),
        "description": task.description(ui_lang),
        "href": _url_with_query(
            "public.research_player_stub",
            ui_lang=ui_lang,
            language_slug=language_slug,
            session_id=session.session_id,
            task=task.key,
            query={"source": source},
        ) if is_available else None,
        "is_disabled": not is_available,
        "state_label": _unavailable_label(ui_lang) if not is_available else None,
    }


def _level_summary_label(level_codes: tuple[str, ...], ui_lang: str) -> str:
    if ui_lang == "de":
        return "Niveau" if len(level_codes) == 1 else "Niveaus"
    return "Level" if len(level_codes) == 1 else "Levels"


def _format_level_summary(level_codes: tuple[str, ...]) -> str:
    if not level_codes:
        return "-"
    return ", ".join(level_codes)


def _summarize_target_country_stays(person: PersonRecord, ui_lang: str) -> str:
    values = {session.stays_in_target_country for session in person.sessions if session.stays_in_target_country is not None}
    if not values:
        return TARGET_COUNTRY_STAY_LABELS[None][ui_lang]
    if values == {True}:
        return TARGET_COUNTRY_STAY_LABELS[True][ui_lang]
    if values == {False}:
        return TARGET_COUNTRY_STAY_LABELS[False][ui_lang]
    return "Teilweise" if ui_lang == "de" else "Mixed"


def _recordings_filter_form(ui_lang: str, language_slug: str, filters: Mapping[str, str], sessions: list[SessionRecord]) -> dict[str, Any]:
    levels = sorted({session.level_code for session in sessions if session.level_code}, key=lambda value: LEVEL_ORDER.get(value, 999))
    l1_values = _sorted_distinct([session.l1 for session in sessions])
    speaker_types = _sorted_distinct([session.speaker_type for session in sessions])
    genders = _sorted_distinct([session.gender for session in sessions])
    standard_varieties = _sorted_distinct([session.standard_variety for session in sessions])
    origin_countries = _sorted_distinct([session.origin_country for session in sessions])
    fields = [
        {
            "name": "speaker_type",
            "label": "Sprechergruppe" if ui_lang == "de" else "Speaker type",
            "value": filters["speaker_type"],
            "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                {"value": value, "label": _label(SPEAKER_TYPE_LABELS, value, ui_lang)} for value in speaker_types
            ],
        },
    ]

    if _uses_native_filters(filters["speaker_type"]):
        fields.extend(
            [
                {
                    "name": "standard_variety",
                    "label": _standard_variety_label(ui_lang),
                    "value": filters["standard_variety"],
                    "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                        {"value": value, "label": value.upper()} for value in standard_varieties
                    ],
                },
                {
                    "name": "origin_country",
                    "label": _origin_country_label(ui_lang),
                    "value": filters["origin_country"],
                    "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                        {"value": value, "label": value} for value in origin_countries
                    ],
                },
            ]
        )
    else:
        fields.extend(
            [
                {
                    "name": "level",
                    "label": "Niveau" if ui_lang == "de" else "Level",
                    "value": filters["level"],
                    "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                        {"value": level, "label": level} for level in levels
                    ],
                },
                {
                    "name": "l1",
                    "label": "L1",
                    "value": filters["l1"],
                    "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                        {"value": value, "label": value} for value in l1_values
                    ],
                },
                {
                    "name": "target_country_stay",
                    "label": _target_country_stay_label(ui_lang),
                    "value": filters["target_country_stay"],
                    "options": [
                        {"value": "", "label": "Alle" if ui_lang == "de" else "All"},
                        {"value": "yes", "label": "Ja" if ui_lang == "de" else "Yes"},
                        {"value": "no", "label": "Nein" if ui_lang == "de" else "No"},
                    ],
                },
            ]
        )

    fields.append(
        {
            "name": "gender",
            "label": "Geschlecht" if ui_lang == "de" else "Gender",
            "value": filters["gender"],
            "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                {"value": value, "label": _label(GENDER_LABELS, value, ui_lang)} for value in genders
            ],
        }
    )

    return {
        "action": url_for("public.research_language_page", ui_lang=ui_lang, language_slug=language_slug, page_slug="recordings"),
        "hidden_fields": [{"name": "task", "value": filters["task"]}],
        "fields": fields,
        "submit_label": "Filter anwenden" if ui_lang == "de" else "Apply filters",
        "reset_label": "Filter zurücksetzen" if ui_lang == "de" else "Reset filters",
        "reset_href": _url_with_query(
            "public.research_language_page",
            ui_lang=ui_lang,
            language_slug=language_slug,
            page_slug="recordings",
            query={"task": filters["task"]},
        ),
        "title": "Filter" if ui_lang == "de" else "Filters",
        "summary": "Filter einblenden" if ui_lang == "de" else "Show filters",
    }


def _speakers_filter_form(ui_lang: str, language_slug: str, filters: Mapping[str, str], persons: list[PersonRecord]) -> dict[str, Any]:
    sessions = _flatten_person_sessions(persons)
    levels = sorted({session.level_code for session in sessions if session.level_code}, key=lambda value: LEVEL_ORDER.get(value, 999))
    l1_values = _sorted_distinct([session.l1 for session in sessions])
    genders = _sorted_distinct([person.gender for person in persons])
    standard_varieties = _sorted_distinct([person.standard_variety for person in persons])
    origin_countries = _sorted_distinct([person.origin_country for person in persons])
    fields: list[dict[str, Any]] = []

    if _uses_native_filters(filters["speaker_group"]):
        fields.extend(
            [
                {
                    "name": "standard_variety",
                    "label": _standard_variety_label(ui_lang),
                    "value": filters["standard_variety"],
                    "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                        {"value": value, "label": value.upper()} for value in standard_varieties
                    ],
                },
                {
                    "name": "origin_country",
                    "label": _origin_country_label(ui_lang),
                    "value": filters["origin_country"],
                    "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                        {"value": value, "label": value} for value in origin_countries
                    ],
                },
            ]
        )
    else:
        fields.extend(
            [
                {
                    "name": "level",
                    "label": "Niveau" if ui_lang == "de" else "Level",
                    "value": filters["level"],
                    "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                        {"value": level, "label": level} for level in levels
                    ],
                },
                {
                    "name": "l1",
                    "label": "L1",
                    "value": filters["l1"],
                    "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                        {"value": value, "label": value} for value in l1_values
                    ],
                },
                {
                    "name": "target_country_stay",
                    "label": _target_country_stay_label(ui_lang),
                    "value": filters["target_country_stay"],
                    "options": [
                        {"value": "", "label": "Alle" if ui_lang == "de" else "All"},
                        {"value": "yes", "label": "Ja" if ui_lang == "de" else "Yes"},
                        {"value": "no", "label": "Nein" if ui_lang == "de" else "No"},
                    ],
                },
            ]
        )

    fields.append(
        {
            "name": "gender",
            "label": "Geschlecht" if ui_lang == "de" else "Gender",
            "value": filters["gender"],
            "options": [{"value": "", "label": "Alle" if ui_lang == "de" else "All"}] + [
                {"value": value, "label": _label(GENDER_LABELS, value, ui_lang)} for value in genders
            ],
        }
    )

    return {
        "action": url_for("public.research_language_page", ui_lang=ui_lang, language_slug=language_slug, page_slug="speakers"),
        "hidden_fields": [{"name": "speaker_group", "value": filters["speaker_group"]}],
        "fields": fields,
        "submit_label": "Filter anwenden" if ui_lang == "de" else "Apply filters",
        "reset_label": "Filter zurücksetzen" if ui_lang == "de" else "Reset filters",
        "reset_href": _url_with_query(
            "public.research_language_page",
            ui_lang=ui_lang,
            language_slug=language_slug,
            page_slug="speakers",
            query={"speaker_group": filters["speaker_group"]} if filters["speaker_group"] != "all" else {},
        ),
        "title": "Weitere Filter" if ui_lang == "de" else "More filters",
        "summary": "Filter einblenden" if ui_lang == "de" else "Show filters",
    }


def build_recordings_page(ui_lang: str, language_slug: str, query_args: Mapping[str, str]) -> dict[str, Any]:
    filters = _normalize_recordings_filters(query_args)
    sessions = list(load_language_sessions(language_slug))
    scoped_sessions = [session for session in sessions if session_matches_filters(session, filters)]

    active_filters: list[dict[str, str]] = []
    if filters["speaker_type"]:
        active_filters.append(
            _filter_chip(
                f"{'Sprechergruppe' if ui_lang == 'de' else 'Speaker type'}: {_label(SPEAKER_TYPE_LABELS, filters['speaker_type'], ui_lang)}",
                "public.research_language_page",
                query=filters,
                drop_key="speaker_type",
                ui_lang=ui_lang,
                language_slug=language_slug,
                page_slug="recordings",
            )
        )
    if _uses_native_filters(filters["speaker_type"]):
        if filters["standard_variety"]:
            active_filters.append(
                _filter_chip(
                    f"{_standard_variety_label(ui_lang)}: {filters['standard_variety'].upper()}",
                    "public.research_language_page",
                    query=filters,
                    drop_key="standard_variety",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="recordings",
                )
            )
        if filters["origin_country"]:
            active_filters.append(
                _filter_chip(
                    f"{_origin_country_label(ui_lang)}: {filters['origin_country']}",
                    "public.research_language_page",
                    query=filters,
                    drop_key="origin_country",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="recordings",
                )
            )
    else:
        if filters["level"]:
            active_filters.append(
                _filter_chip(
                    f"{'Niveau' if ui_lang == 'de' else 'Level'}: {filters['level']}",
                    "public.research_language_page",
                    query=filters,
                    drop_key="level",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="recordings",
                )
            )
        if filters["l1"]:
            active_filters.append(
                _filter_chip(
                    f"L1: {filters['l1']}",
                    "public.research_language_page",
                    query=filters,
                    drop_key="l1",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="recordings",
                )
            )
        if filters["target_country_stay"]:
            stay_label = "Ja" if filters["target_country_stay"] == "yes" else "Nein"
            if ui_lang == "en":
                stay_label = "Yes" if filters["target_country_stay"] == "yes" else "No"
            active_filters.append(
                _filter_chip(
                    f"{_target_country_stay_label(ui_lang)}: {stay_label}",
                    "public.research_language_page",
                    query=filters,
                    drop_key="target_country_stay",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="recordings",
                )
            )
    if filters["gender"]:
        active_filters.append(
            _filter_chip(
                f"{'Geschlecht' if ui_lang == 'de' else 'Gender'}: {_label(GENDER_LABELS, filters['gender'], ui_lang)}",
                "public.research_language_page",
                query=filters,
                drop_key="gender",
                ui_lang=ui_lang,
                language_slug=language_slug,
                page_slug="recordings",
            )
        )

    task_counts: dict[str, int] = {
        task.key: sum(1 for session in scoped_sessions if session_has_task(session, task.key))
        for task in iter_research_tasks()
    }
    available_tasks = [task for task in iter_research_tasks() if task_counts[task.key] > 0]
    active_task_key = filters["task"]
    if available_tasks and task_counts.get(active_task_key, 0) == 0:
        active_task_key = available_tasks[0].key

    active_task = get_research_task(active_task_key)
    if active_task is None:
        raise LookupError(f"Unsupported task: {active_task_key}")

    task_panels = []
    for task in iter_research_tasks():
        task_count = task_counts[task.key]
        task_query = dict(filters)
        task_query["task"] = task.key
        task_panels.append(
            {
                "key": task.key,
                "label": task.short_label(ui_lang),
                "description": task.description(ui_lang),
                "count": task_count,
                "count_label": "Aufzeichnungen" if ui_lang == "de" else "recordings",
                "href": _url_with_query(
                    "public.research_language_page",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="recordings",
                    query=task_query,
                ) if task_count > 0 else None,
                "current": task.key == active_task_key,
                "is_disabled": task_count == 0,
                "state_label": _unavailable_label(ui_lang) if task_count == 0 else None,
            }
        )

    filtered_sessions = sort_sessions_by_recency(
        session for session in scoped_sessions if session_has_task(session, active_task_key)
    )

    results = [
        {
            "person_id": session.person_id,
            "person_href": _url_with_query(
                "public.research_speaker_profile",
                ui_lang=ui_lang,
                language_slug=language_slug,
                person_id=session.person_id,
                query={"session": session.session_id},
            ),
            "session_id": session.session_id,
            "speaker_type": _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
            "context_value": "" if session.is_native else _format_level(session, ui_lang),
            "detail_value": "" if session.is_native else (session.l1 or "-"),
            "gender": _label(GENDER_LABELS, session.gender or "unknown", ui_lang),
            "target_country_stay": "-" if session.is_native else _format_target_country_stay(session.stays_in_target_country, ui_lang),
            "action_label": active_task.short_label(ui_lang),
            "player_href": _url_with_query(
                "public.research_player_stub",
                ui_lang=ui_lang,
                language_slug=language_slug,
                session_id=session.session_id,
                task=active_task_key,
                query={"source": "recordings"},
            ),
        }
        for session in filtered_sessions
    ]

    return {
        "title": get_research_page_label("recordings", ui_lang),
        "template": "pages/research_recordings.html",
        "page_kind": "workbench",
        "access": "protected",
        "content_header": build_content_header(
            page_name="research",
            title=get_research_page_label("recordings", ui_lang),
            intro=RESEARCH_PAGE_INTROS["recordings"][ui_lang],
            section_label=get_section_label("research", ui_lang),
            section_href=url_for("public.research_home", ui_lang=ui_lang),
            context_mode="language",
            context_title=_language_context(ui_lang, language_slug)[1],
            context_root_href=url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug),
        ),
        "task_panels": task_panels,
        "active_task": {
            "key": active_task.key,
            "label": active_task.long_label(ui_lang),
            "description": active_task.description(ui_lang),
            "count": len(filtered_sessions),
            "count_label": "Aufzeichnungen" if ui_lang == "de" else "recordings",
        },
        "filter_form": _recordings_filter_form(ui_lang, language_slug, {**filters, "task": active_task_key}, sessions),
        "status": {
            "result_count": len(filtered_sessions),
            "active_filter_count": len(active_filters),
            "result_label": "Sessions" if ui_lang == "de" else "sessions",
            "filter_label": "aktive Filter" if ui_lang == "de" else "active filters",
        },
        "active_filters": active_filters,
        "columns": {
            "recording": "Aufzeichnung (Sprecher:in)" if ui_lang == "de" else "Recording (speaker)",
            "speaker_type": "Sprechergruppe" if ui_lang == "de" else "Speaker type",
            "context": "Niveau" if ui_lang == "de" else "Level",
            "detail": "L1",
            "gender": "Geschlecht" if ui_lang == "de" else "Gender",
            "stay": _target_country_stay_label(ui_lang),
            "action": "Aktion" if ui_lang == "de" else "Action",
        },
        "results": results,
        "empty_state": {
            "message": "Keine passenden Sessions gefunden." if ui_lang == "de" else "No matching sessions found.",
            "reset_href": _recordings_filter_form(ui_lang, language_slug, {**filters, "task": active_task_key}, sessions)["reset_href"],
            "reset_label": "Filter zurücksetzen" if ui_lang == "de" else "Reset filters",
        },
    }


def build_speakers_page(ui_lang: str, language_slug: str, query_args: Mapping[str, str]) -> dict[str, Any]:
    filters = _normalize_speakers_filters(query_args)
    persons = list(load_person_records(language_slug))
    matched_people = [(person, matching_sessions_for_person(person, filters)) for person in persons]
    filtered_people = [(person, matching_sessions) for person, matching_sessions in matched_people if matching_sessions]

    active_filters: list[dict[str, str]] = []
    if filters["speaker_group"] != "all":
        group_label = dict(SPEAKER_GROUPS)[filters["speaker_group"]][ui_lang]
        active_filters.append(
            _filter_chip(
                f"{'Gruppe' if ui_lang == 'de' else 'Group'}: {group_label}",
                "public.research_language_page",
                query=filters,
                drop_key="speaker_group",
                ui_lang=ui_lang,
                language_slug=language_slug,
                page_slug="speakers",
            )
        )
    if _uses_native_filters(filters["speaker_group"]):
        if filters["standard_variety"]:
            active_filters.append(
                _filter_chip(
                    f"{_standard_variety_label(ui_lang)}: {filters['standard_variety'].upper()}",
                    "public.research_language_page",
                    query=filters,
                    drop_key="standard_variety",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="speakers",
                )
            )
        if filters["origin_country"]:
            active_filters.append(
                _filter_chip(
                    f"{_origin_country_label(ui_lang)}: {filters['origin_country']}",
                    "public.research_language_page",
                    query=filters,
                    drop_key="origin_country",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="speakers",
                )
            )
    else:
        if filters["level"]:
            active_filters.append(
                _filter_chip(
                    f"{'Niveau' if ui_lang == 'de' else 'Level'}: {filters['level']}",
                    "public.research_language_page",
                    query=filters,
                    drop_key="level",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="speakers",
                )
            )
        if filters["l1"]:
            active_filters.append(
                _filter_chip(
                    f"L1: {filters['l1']}",
                    "public.research_language_page",
                    query=filters,
                    drop_key="l1",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="speakers",
                )
            )
        if filters["target_country_stay"]:
            stay_label = "Ja" if filters["target_country_stay"] == "yes" else "Nein"
            if ui_lang == "en":
                stay_label = "Yes" if filters["target_country_stay"] == "yes" else "No"
            active_filters.append(
                _filter_chip(
                    f"{_target_country_stay_label(ui_lang)}: {stay_label}",
                    "public.research_language_page",
                    query=filters,
                    drop_key="target_country_stay",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="speakers",
                )
            )
    if filters["gender"]:
        active_filters.append(
            _filter_chip(
                f"{'Geschlecht' if ui_lang == 'de' else 'Gender'}: {_label(GENDER_LABELS, filters['gender'], ui_lang)}",
                "public.research_language_page",
                query=filters,
                drop_key="gender",
                ui_lang=ui_lang,
                language_slug=language_slug,
                page_slug="speakers",
            )
        )

    quick_filters = []
    for group_key, labels in SPEAKER_GROUPS:
        query = {**filters, "speaker_group": "" if group_key == "all" else group_key}
        if group_key == "native_speaker":
            query.pop("level", None)
            query.pop("l1", None)
            query.pop("target_country_stay", None)
        else:
            query.pop("standard_variety", None)
            query.pop("origin_country", None)
        if group_key == "all":
            query.pop("speaker_group", None)
        quick_filters.append(
            {
                "label": labels[ui_lang],
                "href": _url_with_query(
                    "public.research_language_page",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="speakers",
                    query=query,
                ),
                "current": filters["speaker_group"] == group_key,
            }
        )

    cards = []
    for person, matching_sessions in filtered_people:
        selected_session = resolve_selected_session(person, preferred_session_ids=[session.session_id for session in matching_sessions])
        if person.is_native:
            meta_rows = [
                {"label": _standard_variety_label(ui_lang), "value": person.standard_variety.upper() if person.standard_variety else "-"},
                {"label": _origin_country_label(ui_lang), "value": person.origin_country or "-"},
                {"label": _origin_region_label(ui_lang), "value": person.origin_region or "-"},
                {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": _label(GENDER_LABELS, person.gender or "unknown", ui_lang)},
                {"label": "Aufnahmejahr" if ui_lang == "de" else "Recording year", "value": _format_recording_year(selected_session)},
            ]
        else:
            meta_rows = [
                {"label": "Sessions" if ui_lang == "de" else "Sessions", "value": str(person.session_count)},
                {"label": _level_summary_label(person.level_codes, ui_lang), "value": _format_level_summary(person.level_codes)},
                {"label": "L1", "value": person.l1 or "-"},
                {"label": _target_country_stay_label(ui_lang), "value": _summarize_target_country_stays(person, ui_lang)},
                {"label": "Aufnahmejahre" if ui_lang == "de" else "Recording years", "value": _recording_year_span(person)},
            ]
        cards.append(
            {
                "person_id": person.person_id,
                "eyebrow": _label(SPEAKER_TYPE_LABELS, person.speaker_type, ui_lang),
                "selected_session_label": "Ausgewählte Session" if ui_lang == "de" else "Selected session",
                "selected_session_id": selected_session.session_id,
                "meta_rows": meta_rows,
                "profile_href": _url_with_query(
                    "public.research_speaker_profile",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    person_id=person.person_id,
                    query={"session": selected_session.session_id},
                ),
                "profile_label": "Profil öffnen" if ui_lang == "de" else "Open profile",
                "recordings_label": _recordings_section_label(ui_lang),
                "recording_links_aria_label": _recording_links_aria_label(ui_lang),
                "task_links": [
                    {
                        "label": task.short_label(ui_lang),
                        "href": _url_with_query(
                            "public.research_player_stub",
                            ui_lang=ui_lang,
                            language_slug=language_slug,
                            session_id=selected_session.session_id,
                            task=task.key,
                            query={"source": "speakers"},
                        ),
                    }
                    for task in iter_research_tasks()
                    if session_has_task(selected_session, task.key)
                ],
                "accent_modifier": _session_accent_modifier(selected_session),
            }
        )

    return {
        "title": get_research_page_label("speakers", ui_lang),
        "template": "pages/research_speakers.html",
        "page_kind": "workbench",
        "access": "protected",
        "content_header": build_content_header(
            page_name="research",
            title=get_research_page_label("speakers", ui_lang),
            intro=RESEARCH_PAGE_INTROS["speakers"][ui_lang],
            section_label=get_section_label("research", ui_lang),
            section_href=url_for("public.research_home", ui_lang=ui_lang),
            context_mode="language",
            context_title=_language_context(ui_lang, language_slug)[1],
            context_root_href=url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug),
        ),
        "quick_filters": quick_filters,
        "filter_form": _speakers_filter_form(ui_lang, language_slug, filters, persons),
        "status": {
            "result_count": len(filtered_people),
            "active_filter_count": len(active_filters),
            "result_label": "Personen" if ui_lang == "de" else "people",
            "filter_label": "aktive Filter" if ui_lang == "de" else "active filters",
        },
        "active_filters": active_filters,
        "cards": cards,
        "empty_state": {
            "message": "Keine passenden Personen gefunden." if ui_lang == "de" else "No matching people found.",
            "reset_href": _speakers_filter_form(ui_lang, language_slug, filters, persons)["reset_href"],
            "reset_label": "Filter zurücksetzen" if ui_lang == "de" else "Reset filters",
        },
    }


def _person_section_rows(person: PersonRecord, ui_lang: str) -> list[dict[str, str]]:
    rows = [
        {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": _label(GENDER_LABELS, person.gender or "unknown", ui_lang)},
        {"label": "Geburtsjahr" if ui_lang == "de" else "Birth year", "value": str(person.birth_year) if person.birth_year else "-"},
    ]
    if person.is_native:
        rows.extend(
            [
                {"label": _origin_country_label(ui_lang), "value": person.origin_country or "-"},
                {"label": _origin_region_label(ui_lang), "value": person.origin_region or "-"},
                {"label": _standard_variety_label(ui_lang), "value": person.standard_variety.upper() if person.standard_variety else "-"},
            ]
        )
        return rows

    rows.extend(
        [
            {"label": "L1", "value": person.l1 or "-"},
            {"label": _mother_l1_label(ui_lang), "value": person.mother_l1 or "-"},
            {"label": _father_l1_label(ui_lang), "value": person.father_l1 or "-"},
            {"label": _additional_languages_label(ui_lang), "value": _format_additional_languages(person.additional_languages)},
            {"label": "Aktuelle Region" if ui_lang == "de" else "Current region", "value": person.current_region or "-"},
            {"label": "Region Kindheit" if ui_lang == "de" else "Childhood region", "value": person.childhood_region or "-"},
        ]
    )
    return rows


def _session_card_rows(session: SessionRecord, ui_lang: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {"label": "Aufnahmedatum" if ui_lang == "de" else "Recording date", "value": _format_recording_date(session)},
        {"label": "Aufnahmejahr" if ui_lang == "de" else "Recording year", "value": _format_recording_year(session)},
        {"label": _recorded_by_label(ui_lang), "value": session.recorded_by or "-"},
    ]
    if not session.is_native:
        rows.extend(
            [
                {"label": "Niveau zum Aufnahmezeitpunkt" if ui_lang == "de" else "Level at recording", "value": session.level_self or _format_level(session, ui_lang)},
                _build_exposure_row(session, ui_lang),
            ]
        )
    return rows


def _session_cards(person: PersonRecord, selected_session: SessionRecord, ui_lang: str, language_slug: str) -> list[dict[str, Any]]:
    cards = []
    for session in person.sessions:
        cards.append(
            {
                "session_id": session.session_id,
                "is_selected": session.session_id == selected_session.session_id,
                "selected_label": "Ausgewählt" if ui_lang == "de" else "Selected",
                "accent_modifier": _session_accent_modifier(session),
                "rows": _session_card_rows(session, ui_lang),
                "notes": session.notes,
                "recordings_label": _recordings_section_label(ui_lang),
                "tasks": [_build_task_item(session, task.key, ui_lang, language_slug, "profile") for task in iter_research_tasks()],
            }
        )
    return cards


def build_speaker_profile_page(
    ui_lang: str,
    language_slug: str,
    person_id: str,
    requested_session_id: str | None = None,
) -> dict[str, Any] | None:
    person = get_person_record(language_slug, person_id)
    if person is None:
        return None

    selected_session = resolve_selected_session(person, requested_session_id=requested_session_id)
    person_section_rows = _person_section_rows(person, ui_lang)
    session_cards = _session_cards(person, selected_session, ui_lang, language_slug)

    if person.is_native:
        intro = "Reduziertes Vergleichsprofil mit genau einer Session und den zugehörigen Aufzeichnungen." if ui_lang == "de" else "Reduced comparison profile with exactly one session and its recordings."
        header_badges = [_label(SPEAKER_TYPE_LABELS, person.speaker_type, ui_lang), person.standard_variety.upper() if person.standard_variety else None]
    else:
        intro = "Profil mit Personendaten und allen zugehörigen Sessions und Aufzeichnungen." if ui_lang == "de" else "Profile with person data and all associated sessions and recordings."
        header_badges = [_label(SPEAKER_TYPE_LABELS, person.speaker_type, ui_lang), _recording_year_span(person)]

    return {
        "title": "Profil" if ui_lang == "de" else "Profile",
        "template": "pages/research_speaker_profile.html",
        "page_kind": "workbench",
        "access": "protected",
        "content_header": build_content_header(
            page_name="research",
            title="Profil" if ui_lang == "de" else "Profile",
            intro=intro,
            section_label=get_section_label("research", ui_lang),
            section_href=url_for("public.research_home", ui_lang=ui_lang),
            context_mode="language",
            context_title=_language_context(ui_lang, language_slug)[1],
            context_root_href=url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug),
            ancestors=[
                {
                    "label": get_research_page_label("speakers", ui_lang),
                    "href": url_for("public.research_language_page", ui_lang=ui_lang, language_slug=language_slug, page_slug="speakers"),
                }
            ],
        ),
        "profile_header": {
            "person_id": person.person_id,
            "speaker_type": _label(SPEAKER_TYPE_LABELS, person.speaker_type, ui_lang),
            "session_count_label": _session_count_label(ui_lang),
            "session_count_value": person.session_count,
            "badges": [badge for badge in header_badges if badge and badge != "-"],
        },
        "person_section": {"title": "Profildaten" if ui_lang == "de" else "Profile data", "rows": person_section_rows},
        "sessions_section": {
            "title": "Session und Aufzeichnungen" if ui_lang == "de" and (person.is_native or person.session_count == 1) else "Sessions und Aufzeichnungen" if ui_lang == "de" else "Session and recordings" if person.is_native or person.session_count == 1 else "Sessions and recordings",
            "cards": session_cards,
        },
        "speakers_href": url_for("public.research_language_page", ui_lang=ui_lang, language_slug=language_slug, page_slug="speakers"),
    }


def build_player_stub_page(ui_lang: str, language_slug: str, session_id: str, task_key: str, source: str | None) -> dict[str, Any] | None:
    session = get_session(language_slug, session_id)
    task = get_research_task(task_key)
    if session is None or task is None or not session_has_task(session, task_key):
        return None

    profile_href = _url_with_query(
        "public.research_speaker_profile",
        ui_lang=ui_lang,
        language_slug=language_slug,
        person_id=session.person_id,
        query={"session": session.session_id},
    )

    origin_href = url_for("public.research_language_page", ui_lang=ui_lang, language_slug=language_slug, page_slug="speakers")
    origin_label = "Zurück zu Sprecher:innen" if ui_lang == "de" else "Back to speakers"
    if source == "recordings":
        origin_href = _url_with_query(
            "public.research_language_page",
            ui_lang=ui_lang,
            language_slug=language_slug,
            page_slug="recordings",
            query={"task": task_key},
        )
        origin_label = "Zurück zu Aufzeichnungen" if ui_lang == "de" else "Back to recordings"
    elif source == "profile":
        origin_href = profile_href
        origin_label = "Zurück zum Profil" if ui_lang == "de" else "Back to profile"

    context_value = _format_standard_variety(session) if session.is_native else _format_level(session, ui_lang)
    detail_value = (session.origin_country or "-") if session.is_native else (session.l1 or "-")

    return {
        "title": task.long_label(ui_lang),
        "template": "pages/research_player_stub.html",
        "page_kind": "workbench",
        "access": "protected",
        "content_header": build_content_header(
            page_name="research",
            title=task.long_label(ui_lang),
            intro="Die Player-Ansicht ist strukturell vorbereitet, wird in diesem Run aber bewusst noch nicht fachlich ausgebaut." if ui_lang == "de" else "The player view is structurally prepared but intentionally not implemented in this run.",
            section_label=get_section_label("research", ui_lang),
            section_href=url_for("public.research_home", ui_lang=ui_lang),
            context_mode="language",
            context_title=_language_context(ui_lang, language_slug)[1],
            context_root_href=url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug),
            ancestors=[
                {
                    "label": get_research_page_label("recordings", ui_lang) if source == "recordings" else get_research_page_label("speakers", ui_lang),
                    "href": _url_with_query(
                        "public.research_language_page",
                        ui_lang=ui_lang,
                        language_slug=language_slug,
                        page_slug="recordings" if source == "recordings" else "speakers",
                        query={"task": task_key} if source == "recordings" else None,
                    ),
                }
            ],
        ),
        "origin_link": {"label": origin_label, "href": origin_href},
        "profile_link": {"label": "Zum Profil" if ui_lang == "de" else "Open profile", "href": profile_href},
        "speakers_href": url_for("public.research_language_page", ui_lang=ui_lang, language_slug=language_slug, page_slug="speakers"),
        "recordings_href": _url_with_query(
            "public.research_language_page",
            ui_lang=ui_lang,
            language_slug=language_slug,
            page_slug="recordings",
            query={"task": task_key},
        ),
        "session": {
            "session_id": session.session_id,
            "person_id": session.person_id,
            "speaker_type": _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
            "context_label": "Varietät" if session.is_native and ui_lang == "de" else "Niveau" if ui_lang == "de" else "Variety" if session.is_native else "Level",
            "context_value": context_value,
            "detail_label": _origin_country_label(ui_lang) if session.is_native else "L1",
            "detail_value": detail_value,
            "task": task.long_label(ui_lang),
            "task_description": task.description(ui_lang),
        },
    }