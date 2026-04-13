"""View-model builders for PROMAT research workbench pages."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlencode

from flask import g, url_for

from .content_navigation import build_content_header
from .i18n import translate, translate_many
from .research_capabilities import (
    PLAYER_RENDER_MODES,
    comparison_default_view_task,
    comparison_view_task_keys,
    get_research_task_label,
    phenomena_task_keys,
    set_filter_task_keys,
    task_supports_player_compare,
)
from .research_player_runtime import (
    NormalizedPlayerSource,
    build_player_compare_rows as _build_player_compare_rows,
    build_player_items as _build_player_items,
    build_player_set_notice as _build_player_set_notice,
    build_running_text_blocks as _build_running_text_blocks,
    is_playable_audio_artifact as _is_playable_audio_artifact,
    load_task_bundle as _load_task_bundle,
    load_task_ready_sessions as _load_task_ready_sessions,
    normalized_render_mode_query as _normalized_render_mode_query,
    normalize_compare_mode as _normalize_compare_mode,
    resolve_player_audio_artifact as _resolve_player_audio_artifact_runtime,
    resolve_player_item_download as _resolve_player_item_download_runtime,
    resolve_player_runtime_state,
    resolve_player_set_context,
)
from .research_presets import load_phenomena_presets, load_task_catalogs
from .research_sets import (
    list_selectable_owned_sets,
    load_owned_set,
)
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

PHENOMENA_ITEM_TASKS: tuple[str, ...] = set_filter_task_keys()
COMPARISON_VIEW_TASKS: tuple[str, ...] = comparison_view_task_keys()


def _label(mapping: dict[str, dict[str, str]], key: str, ui_lang: str) -> str:
    return mapping.get(key, mapping.get("unknown", {"de": key, "en": key})).get(ui_lang, key)


def _t(ui_lang: str, key: str, **kwargs: object) -> str:
    return translate(ui_lang, key, **kwargs)


def _format_level(session: SessionRecord, ui_lang: str) -> str:
    del ui_lang
    return session.level_code or "-"


STANDARD_VARIETY_LABELS = {
    "castellano": {"de": "Kastilisches Spanisch", "en": "Castilian Spanish"},
    "es_std": {"de": "Spanien", "en": "Spain"},
    "mx_std": {"de": "Mexiko", "en": "Mexico"},
    "rioplatense": {"de": "Río-de-la-Plata-Spanisch", "en": "Rioplatense Spanish"},
    "andino": {"de": "Andines Spanisch", "en": "Andean Spanish"},
    "caribeno": {"de": "Karibisches Spanisch", "en": "Caribbean Spanish"},
    "caribeno_estandar": {"de": "Karibisches Spanisch", "en": "Caribbean Spanish"},
    "mexicano": {"de": "Mexikanisches Spanisch", "en": "Mexican Spanish"},
    "mexicano_estandar": {"de": "Mexikanisches Spanisch", "en": "Mexican Spanish"},
}


def _format_standard_variety_value(value: str | None, ui_lang: str) -> str:
    if not value:
        return "-"
    normalized = value.strip().lower()
    mapped = STANDARD_VARIETY_LABELS.get(normalized)
    if mapped:
        return mapped.get(ui_lang, mapped.get("en", _humanize_value(value)))
    return _humanize_value(value)


def _format_standard_variety(session: SessionRecord, ui_lang: str) -> str:
    return _format_standard_variety_value(session.standard_variety, ui_lang)


def _format_target_country_stay(stays_in_target_country: bool | None, ui_lang: str) -> str:
    return TARGET_COUNTRY_STAY_LABELS[stays_in_target_country][ui_lang]


def _target_country_stay_label(ui_lang: str) -> str:
    return _t(ui_lang, "common.labels.target_country_stays")


def _standard_variety_label(ui_lang: str) -> str:
    return _t(ui_lang, "common.labels.standard_variety")


def _origin_country_label(ui_lang: str) -> str:
    return _t(ui_lang, "common.labels.origin_country")


def _origin_region_label(ui_lang: str) -> str:
    return _t(ui_lang, "common.labels.origin_region")


def _recorded_by_label(ui_lang: str) -> str:
    return _t(ui_lang, "common.labels.recorded_by")


def _mother_l1_label(ui_lang: str) -> str:
    return _t(ui_lang, "common.labels.mother_l1")


def _father_l1_label(ui_lang: str) -> str:
    return _t(ui_lang, "common.labels.father_l1")


def _additional_languages_label(ui_lang: str) -> str:
    return _t(ui_lang, "common.labels.additional_languages")


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
                    "text": " · ".join(parts) if parts else _t(ui_lang, "research.exposure.language_stay"),
                    "note": entry.exposure_notes or "",
                }
            )
        return {"label": label, "kind": "exposure", "entries": entries}

    if session.stays_in_target_country is False:
        return {
            "label": label,
            "kind": "exposure",
            "value": _t(ui_lang, "research.exposure.none"),
        }

    if session.stays_in_target_country is True:
        return {
            "label": label,
            "kind": "exposure",
            "value": _t(ui_lang, "research.exposure.recorded_without_details"),
        }

    return {"label": label, "kind": "exposure", "value": _t(ui_lang, "research.exposure.not_recorded")}


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
            "public.research_player",
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
                "public.research_player",
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
                            "public.research_player",
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


def _phenomena_intro(ui_lang: str) -> str:
    return _t(ui_lang, "research.phenomena.intro")


def _phenomena_status_title(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.material_title")


def _phenomena_empty_title(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.empty_title")


def _phenomena_empty_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.phenomena.empty_text")


def _phenomena_login_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.phenomena.login_text")


def _phenomena_pending_preset_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.phenomena.pending_preset_text")


def _phenomena_pending_set_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.pending_set_text")


def _phenomena_open_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.edit_items_label")


def _phenomena_login_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.login_label")


def _phenomena_add_label(ui_lang: str) -> str:
    return _t(ui_lang, "common.actions.add")


def _phenomena_remove_label(ui_lang: str) -> str:
    return _t(ui_lang, "common.actions.remove")


def _phenomena_open_player_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.open_player")


def _phenomena_open_comparison_label(ui_lang: str) -> str:
    return get_research_page_label("comparison", ui_lang)


def _phenomena_catalog_heading(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.material_title")


def _phenomena_page_href(
    ui_lang: str,
    language_slug: str,
    *,
    preset_id: str | None = None,
    set_id: str | None = None,
    task: str | None = None,
) -> str:
    return _url_with_query(
        "public.research_language_page",
        ui_lang=ui_lang,
        language_slug=language_slug,
        page_slug="phenomena",
        query={"preset_id": preset_id, "set_id": set_id, "task": task},
    )


def _phenomena_login_href(
    ui_lang: str,
    language_slug: str,
    *,
    preset_id: str | None = None,
    set_id: str | None = None,
    task: str | None = None,
) -> str:
    return url_for(
        "public.login",
        next=_phenomena_page_href(ui_lang, language_slug, preset_id=preset_id, set_id=set_id, task=task),
    )


def _phenomena_task_labels(language_slug: str, ui_lang: str) -> dict[str, str]:
    return {
        task_key: get_research_task_label(task_key, ui_lang, variant="material", language_slug=language_slug)
        for task_key in PHENOMENA_ITEM_TASKS
    }


def _phenomena_preferred_task(task_counts: Mapping[str, int]) -> str:
    ranked = sorted(
        ((task_key, task_counts.get(task_key, 0)) for task_key in PHENOMENA_ITEM_TASKS),
        key=lambda entry: (-entry[1], PHENOMENA_ITEM_TASKS.index(entry[0])),
    )
    return ranked[0][0]


def _phenomena_task_summary(task_counts: Mapping[str, int], task_labels: Mapping[str, str]) -> str:
    parts = [
        f"{task_counts[task_key]} {task_labels[task_key]}"
        for task_key in PHENOMENA_ITEM_TASKS
        if task_counts.get(task_key, 0) > 0 and task_key in task_labels
    ]
    return " · ".join(parts)


def _phenomena_catalog_payload(language_slug: str, ui_lang: str) -> dict[str, list[dict[str, str | None]]]:
    catalogs = load_task_catalogs(language_slug)
    task_labels = _phenomena_task_labels(language_slug, ui_lang)
    payload: dict[str, list[dict[str, str | None]]] = {}
    for task_key in PHENOMENA_ITEM_TASKS:
        catalog = catalogs.get(task_key)
        if catalog is None:
            payload[task_key] = []
            continue
        payload[task_key] = [
            {
                "task": task_key,
                "task_label": task_labels.get(task_key, task_key),
                "item_id": item.item_id,
                "item_number": item.item_number,
                "text": item.text,
                "group_id": item.group_id,
            }
            for item in catalog.items_by_id.values()
        ]
    return payload


def _phenomena_preset_cards(language_slug: str, ui_lang: str) -> list[dict[str, Any]]:
    catalogs = _phenomena_catalog_payload(language_slug, ui_lang)
    item_lookup = {
        (task_key, item["item_id"]): item
        for task_key, items in catalogs.items()
        for item in items
    }
    task_labels = _phenomena_task_labels(language_slug, ui_lang)
    cards: list[dict[str, Any]] = []
    for preset in load_phenomena_presets(language_slug):
        task_counts = {task_key: 0 for task_key in PHENOMENA_ITEM_TASKS}
        preview_labels: list[str] = []
        for reference in preset.items:
            if reference.task not in task_counts:
                continue
            task_counts[reference.task] += 1
            item = item_lookup.get((reference.task, reference.item_id))
            if item is not None and len(preview_labels) < 4:
                preview_labels.append(f"{item['item_number']} {item['text']}")
        preferred_task = _phenomena_preferred_task(task_counts)
        cards.append(
            {
                "preset_id": preset.preset_id,
                "label": preset.label,
                "description": preset.description,
                "item_count": len(preset.items),
                "task_counts": task_counts,
                "task_summary": _phenomena_task_summary(task_counts, task_labels),
                "preview_labels": preview_labels,
                "preferred_task": preferred_task,
                "login_href": _phenomena_login_href(ui_lang, language_slug, preset_id=preset.preset_id, task=preferred_task),
            }
        )
    return cards


def _comparison_material_presets(language_slug: str, ui_lang: str) -> list[dict[str, object]]:
    task_labels = _phenomena_task_labels(language_slug, ui_lang)
    presets: list[dict[str, object]] = []
    for preset in load_phenomena_presets(language_slug):
        task_counts = {task_key: 0 for task_key in PHENOMENA_ITEM_TASKS}
        for reference in preset.items:
            if reference.task in task_counts:
                task_counts[reference.task] += 1
        presets.append(
            {
                "presetId": preset.preset_id,
                "kind": "curated",
                "optionLabel": f"{preset.label} · curated",
                "label": preset.label,
                "preferredTask": _phenomena_preferred_task(task_counts),
                "taskSummary": _phenomena_task_summary(task_counts, task_labels),
                "items": [
                    {
                        "task": reference.task,
                        "item_id": reference.item_id,
                    }
                    for reference in preset.items
                ],
            }
        )

    owner_user_id = _current_owner_user_id()
    if owner_user_id is None:
        return presets

    try:
        saved_sets = list_selectable_owned_sets(owner_user_id=owner_user_id, corpus_language=language_slug)
    except (ResearchSetStorageUnavailableError, ResearchSetValidationError, RuntimeError):
        return presets

    for stored_set in saved_sets:
        task_counts = {task_key: 0 for task_key in PHENOMENA_ITEM_TASKS}
        for reference in stored_set.items:
            if reference.task in task_counts:
                task_counts[reference.task] += 1
        presets.append(
            {
                "presetId": f"saved:{stored_set.set_id}",
                "kind": "custom",
                "setId": stored_set.set_id,
                "optionLabel": f"{stored_set.label or _t(ui_lang, 'common.untitled')} · {_t(ui_lang, 'common.status.custom')}",
                "label": stored_set.label or _t(ui_lang, "common.untitled"),
                "preferredTask": stored_set.workbench_state.comparison_view_task or _phenomena_preferred_task(task_counts),
                "taskSummary": _phenomena_task_summary(task_counts, task_labels),
                "items": [
                    {
                        "task": reference.task,
                        "item_id": reference.item_id,
                    }
                    for reference in stored_set.items
                ],
            }
        )
    return presets


def _phenomena_session_options(language_slug: str) -> dict[str, list[dict[str, str]]]:
    sessions_by_task: dict[str, list[dict[str, str]]] = {task_key: [] for task_key in PHENOMENA_ITEM_TASKS}
    for session in sort_sessions_by_recency(load_language_sessions(language_slug)):
        for task_key in PHENOMENA_ITEM_TASKS:
            if not session_has_task(session, task_key):
                continue
            sessions_by_task[task_key].append(
                {
                    "session_id": session.session_id,
                    "label": f"{session.session_id} · {session.person_id}",
                }
            )
    return sessions_by_task


def _comparison_intro(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.intro")


def _comparison_status_title(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.status_title")


def _comparison_empty_title(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.empty_title")


def _comparison_empty_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.empty_text")


def _comparison_login_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.login_text")


def _comparison_pending_set_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.pending_set_text")


def _comparison_create_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.create_label")


def _comparison_login_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.login_label")


def _comparison_edit_items_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.phenomena_choose_label")


def _comparison_open_player_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.open_player")


def _comparison_download_clip_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.download_clip")


def _comparison_add_session_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.add_session")


def _comparison_remove_session_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.remove_session")


def _comparison_play_row_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.play_row")


def _comparison_play_clip_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.play_clip")


def _comparison_stop_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.comparison.stop")


def _comparison_view_task_label(view_task: str, task_labels: Mapping[str, str], ui_lang: str) -> str:
    if view_task == "all":
        return _t(ui_lang, "research.comparison.default_set_label")
    return task_labels.get(view_task, view_task)


def _comparison_page_href(
    ui_lang: str,
    language_slug: str,
    *,
    set_id: str | None = None,
    task: str | None = None,
) -> str:
    return _url_with_query(
        "public.research_language_page",
        ui_lang=ui_lang,
        language_slug=language_slug,
        page_slug="comparison",
        query={"set_id": set_id, "task": task},
    )


def _comparison_login_href(
    ui_lang: str,
    language_slug: str,
    *,
    set_id: str | None = None,
    task: str | None = None,
) -> str:
    return url_for(
        "public.login",
        next=_comparison_page_href(ui_lang, language_slug, set_id=set_id, task=task),
    )


def _comparison_session_task_summary(clip_counts: list[dict[str, Any]]) -> str:
    parts = []
    for entry in clip_counts:
        if not entry["documented"]:
            continue
        if entry["clip_count"] > 0:
            parts.append(f"{entry['clip_count']} {entry['label']}")
        else:
            parts.append(f"0 {entry['label']}")
    return " · ".join(parts)


def _comparison_session_catalog(language_slug: str, ui_lang: str) -> list[dict[str, Any]]:
    task_labels = _phenomena_task_labels(language_slug, ui_lang)
    catalog: list[dict[str, Any]] = []
    for session in sort_sessions_by_recency(load_language_sessions(language_slug)):
        documented_tasks = [task_key for task_key in PHENOMENA_ITEM_TASKS if session_has_task(session, task_key)]
        available_item_ids_by_task: dict[str, list[str]] = {task_key: [] for task_key in PHENOMENA_ITEM_TASKS}
        clip_counts: list[dict[str, Any]] = []
        for task_key in PHENOMENA_ITEM_TASKS:
            bundle = _load_task_bundle(session, task_key) if task_key in documented_tasks else None
            item_ids = [item["item_id"] for item in bundle["items"] if item["split_audio_path"] is not None] if bundle else []
            available_item_ids_by_task[task_key] = item_ids
            clip_counts.append(
                {
                    "task": task_key,
                    "label": task_labels.get(task_key, task_key),
                    "documented": task_key in documented_tasks,
                    "clip_count": len(item_ids),
                }
            )

        context_label = _t(ui_lang, "research.comparison.variety_label") if session.is_native else _t(ui_lang, "research.comparison.level_label")
        context_value = _format_standard_variety_value(session.standard_variety, ui_lang) if session.is_native else _format_level(session, ui_lang)
        detail_label = _origin_country_label(ui_lang) if session.is_native else _t(ui_lang, "common.labels.l1_short")
        detail_value = (session.origin_country or "-") if session.is_native else (session.l1 or "-")
        level_value = "-" if session.is_native else (_format_level(session, ui_lang) or "-")
        l1_value = "-" if session.is_native else (session.l1 or "-")
        gender_key = (session.gender or "unknown").strip().lower() if isinstance(session.gender, str) else "unknown"
        if session.is_native:
            target_country_stay_key = "unknown"
        elif session.stays_in_target_country is True:
            target_country_stay_key = "yes"
        elif session.stays_in_target_country is False:
            target_country_stay_key = "no"
        else:
            target_country_stay_key = "unknown"
        catalog.append(
            {
                "sessionId": session.session_id,
                "label": session.person_id,
                "personId": session.person_id,
                "speakerTypeKey": session.speaker_type,
                "speakerTypeLabel": _t(ui_lang, "research.comparison.native_short") if session.is_native else _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
                "accentModifier": _session_accent_modifier(session),
                "isNative": session.is_native,
                "contextLabel": context_label,
                "contextValue": context_value,
                "detailLabel": detail_label,
                "detailValue": detail_value,
                "levelValue": level_value,
                "l1Value": l1_value,
                "l1BadgeLabel": f"L1: {session.l1}" if session.l1 and not session.is_native else "",
                "standardVarietyLabel": _standard_variety_label(ui_lang),
                "standardVarietyValue": _format_standard_variety_value(session.standard_variety, ui_lang) if session.is_native else "",
                "recordingDate": _format_recording_date(session),
                "genderKey": gender_key,
                "genderLabel": _label(GENDER_LABELS, gender_key, ui_lang),
                "targetCountryStayKey": target_country_stay_key,
                "targetCountryStayLabel": "-" if session.is_native else _format_target_country_stay(session.stays_in_target_country, ui_lang),
                "availableTasks": documented_tasks,
                "availableItemIdsByTask": available_item_ids_by_task,
                "taskSummary": _comparison_session_task_summary(clip_counts),
                "clipCounts": clip_counts,
            }
        )
    return catalog


def build_comparison_page(ui_lang: str, language_slug: str, query_args: Mapping[str, str]) -> dict[str, Any] | None:
    language = get_language(language_slug)
    if language is None:
        return None

    owner_user_id = _current_owner_user_id()
    is_authenticated = owner_user_id is not None
    task_labels = _phenomena_task_labels(language_slug, ui_lang)
    requested_set_id = _normalize_text(query_args.get("set_id"))
    raw_view_task = _normalize_text(query_args.get("task")) or ""
    requested_view_task = raw_view_task if raw_view_task in COMPARISON_VIEW_TASKS else ""
    if raw_view_task and not requested_view_task:
        page_notice = _t(ui_lang, "research.comparison.unknown_task_filter")
    else:
        page_notice = None

    default_view_task = requested_view_task or comparison_default_view_task()
    workspace_mode = "empty"
    workspace_text = _comparison_empty_text(ui_lang) if is_authenticated else _comparison_login_text(ui_lang)
    if requested_set_id:
        workspace_mode = "load-set"
        workspace_text = _comparison_pending_set_text(ui_lang) if is_authenticated else _comparison_login_text(ui_lang)

    phenomena_base_href = url_for(
        "public.research_language_page",
        ui_lang=ui_lang,
        language_slug=language_slug,
        page_slug="phenomena",
    )
    player_href_template = url_for(
        "public.research_player",
        ui_lang=ui_lang,
        language_slug=language_slug,
        session_id="__SESSION__",
        task="__TASK__",
    )

    return {
        "title": get_research_page_label("comparison", ui_lang),
        "template": "pages/research_comparison.html",
        "page_kind": "workbench",
        "access": "protected",
        "content_header": build_content_header(
            page_name="research",
            title=get_research_page_label("comparison", ui_lang),
            intro=_comparison_intro(ui_lang),
            section_label=get_section_label("research", ui_lang),
            section_href=url_for("public.research_home", ui_lang=ui_lang),
            context_mode="language",
            context_title=_language_context(ui_lang, language_slug)[1],
            context_root_href=url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug),
        ),
        "page_notice": page_notice,
        "is_authenticated": is_authenticated,
        "workspace": {
            "title": _comparison_status_title(ui_lang),
            "mode": workspace_mode,
            "empty_title": _comparison_empty_title(ui_lang),
            "text": workspace_text,
            "login_href": _comparison_login_href(ui_lang, language_slug, set_id=requested_set_id, task=default_view_task),
            "login_label": _comparison_login_label(ui_lang),
            "create_label": _comparison_create_label(ui_lang),
            "edit_items_label": _comparison_edit_items_label(ui_lang),
        },
        "client_state": {
            "uiLang": ui_lang,
            "languageSlug": language_slug,
            "isAuthenticated": is_authenticated,
            "requestedSetId": requested_set_id,
            "defaultViewTask": default_view_task,
            "comparisonPageHref": _comparison_page_href(ui_lang, language_slug),
            "loginHref": _comparison_login_href(ui_lang, language_slug),
            "phenomenaBaseHref": phenomena_base_href,
            "playerHrefTemplate": player_href_template,
            "createSetHref": "/api/research/sets",
            "setApiBaseHref": "/api/research/sets",
            "taskLabels": task_labels,
            "materialPresets": _comparison_material_presets(language_slug, ui_lang),
            "viewTasks": [
                {"task": view_task, "label": _comparison_view_task_label(view_task, task_labels, ui_lang)}
                for view_task in COMPARISON_VIEW_TASKS
            ],
            "catalogsByTask": _phenomena_catalog_payload(language_slug, ui_lang),
            "sessionCatalog": _comparison_session_catalog(language_slug, ui_lang),
            "labels": {
                **translate_many(
                    ui_lang,
                    {
                        "statusTitle": "research.comparison.status_title",
                        "emptyTitle": "research.comparison.empty_title",
                        "emptyText": "research.comparison.empty_text",
                        "loginText": "research.comparison.login_text",
                        "loginLabel": "research.comparison.login_label",
                        "loadingSet": "research.comparison.pending_set_text",
                        "createLabel": "research.comparison.create_label",
                        "editItemsLabel": "research.comparison.edit_items_label",
                        "openPlayer": "research.comparison.open_player",
                        "addSessionLabel": "research.comparison.add_session",
                        "removeSessionLabel": "research.comparison.remove_session",
                        "playRowLabel": "research.comparison.play_row",
                        "playClipLabel": "research.comparison.play_clip",
                        "stopLabel": "research.comparison.stop",
                        "materialTitle": "research.comparison.material_title",
                        "materialText": "research.comparison.material_text",
                        "materialPrompt": "research.comparison.material_prompt",
                        "materialLoadingTitle": "research.comparison.material_loading_title",
                        "materialLoadingText": "research.comparison.material_loading_text",
                        "setSelectLabel": "research.comparison.set_select_label",
                        "setSelectInfoLabel": "research.comparison.set_select_info_label",
                        "setSelectInfoText": "research.comparison.set_select_info_text",
                        "sessionPanelTitle": "research.comparison.session_panel_title",
                        "allSessionsTitle": "research.comparison.all_sessions_title",
                        "selectedSessionsTitle": "research.comparison.selected_sessions_title",
                        "itemsTitle": "research.comparison.items_title",
                        "matrixTitle": "research.comparison.matrix_title",
                        "controlsTitle": "research.comparison.controls_title",
                        "volumeLabel": "research.player.volume",
                        "speedLabel": "research.player.speed",
                        "workspaceReady": "research.comparison.workspace_ready",
                        "workspaceItems": "research.comparison.workspace_items",
                        "workspaceSpeakers": "research.comparison.workspace_speakers",
                        "workspaceSetId": "research.comparison.workspace_set_id",
                        "workspacePreset": "research.comparison.workspace_preset",
                        "defaultSetLabel": "research.comparison.default_set_label",
                        "fullListLabel": "research.comparison.full_list_label",
                        "fullTextLabel": "research.comparison.full_text_label",
                        "customSetLabel": "research.comparison.custom_set_label",
                        "curatedMaterialLabel": "research.comparison.curated_material_label",
                        "phenomenaChooseLabel": "research.comparison.phenomena_choose_label",
                        "speakerGroupLabel": "research.comparison.speaker_group_label",
                        "levelLabel": "research.comparison.level_label",
                        "l1ShortLabel": "research.comparison.l1_short_label",
                        "speakerIdLabel": "research.comparison.speaker_id_label",
                        "searchPlaceholder": "research.comparison.search_placeholder",
                        "moreFiltersLabel": "research.comparison.more_filters_label",
                        "l1FilterLabel": "research.comparison.l1_filter_label",
                        "genderFilterLabel": "research.comparison.gender_filter_label",
                        "exposureFilterLabel": "research.comparison.exposure_filter_label",
                        "filterAllLabel": "research.comparison.filter_all_label",
                        "exposureYesLabel": "research.comparison.exposure_yes_label",
                        "exposureNoLabel": "research.comparison.exposure_no_label",
                        "clearFiltersLabel": "research.comparison.clear_filters_label",
                        "speakerSingularLabel": "research.comparison.speaker_singular",
                        "speakerPluralLabel": "research.comparison.speaker_plural",
                        "availableEmptyFiltered": "research.comparison.available_empty_filtered",
                        "selectedEmpty": "research.comparison.selected_empty",
                        "stateDraft": "research.comparison.state_draft",
                        "stateSaved": "research.comparison.state_saved",
                        "stateCurated": "research.comparison.state_curated",
                        "stateCustom": "research.comparison.state_custom",
                        "downloadClip": "research.comparison.download_clip",
                        "workspaceEmptyItems": "research.comparison.workspace_empty_items",
                        "workspaceEmptySessions": "research.comparison.workspace_empty_sessions",
                        "workspaceNoRows": "research.comparison.workspace_no_rows",
                        "workspaceNoMatches": "research.comparison.workspace_no_matches",
                        "clipUnavailable": "research.comparison.clip_unavailable",
                        "taskLabel": "research.comparison.task_label",
                        "sessionLabel": "research.comparison.session_label",
                        "requestFailed": "common.errors.request_failed",
                        "saveHint": "research.comparison.save_hint",
                        "saveValidationError": "research.comparison.save_validation_error",
                        "saveSuccessPrefix": "research.comparison.save_success_prefix",
                        "saveBackendError": "research.comparison.save_backend_error",
                        "saveErrorFallback": "research.comparison.save_error_fallback",
                        "playbackIdle": "research.comparison.playback_idle",
                        "playbackLoading": "research.comparison.playback_loading",
                        "playbackRowPrefix": "research.comparison.playback_row_prefix",
                        "playbackSpeakerPrefix": "research.comparison.playback_speaker_prefix",
                        "clipMissing": "research.comparison.clip_missing",
                    },
                ),
                "sessionPanelText": "",
                "allSessionsText": "",
                "selectedSessionsText": "",
                "learnersTitle": _t(ui_lang, "research.comparison.learners_title"),
                "nativeTitle": _t(ui_lang, "research.comparison.native_title"),
                "nativeShort": _t(ui_lang, "research.comparison.native_short"),
                "selectedTitle": _t(ui_lang, "research.comparison.selected_title"),
                "noscript": _t(ui_lang, "research.comparison.noscript"),
                "untitled": _t(ui_lang, "common.untitled"),
            },
        },
    }


def _recording_date_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.recording_date")


def _task_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.task_switch")


def _player_available_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.available")


def _player_current_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.current_task")


def _player_not_ready_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.not_ready")


def _player_artifacts_missing_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.artifacts_missing")


def _player_play_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.play")


def _player_pause_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.pause")


def _player_sequence_toggle_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.play_both")


def _player_session_switch_title(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.sessions_and_comparison")


def _player_session_switch_hint(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.sessions_and_comparison_hint")


def _player_primary_session_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.primary_session")


def _player_compare_session_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.compare_session")


def _player_compare_disabled_option(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.no_comparison")


def _player_compare_add_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.add_comparison")


def _player_compare_remove_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.remove_comparison")


def _player_compare_close_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.close_comparison")


def _player_compare_picker_title(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.choose_comparison_session")


def _player_session_switcher_label(ui_lang: str, role_key: str) -> str:
    if role_key == "secondary":
        return _t(ui_lang, "research.player.change_compare_session")
    return _t(ui_lang, "research.player.change_primary_session")


def _player_compare_placeholder_badge(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.pending")


def _player_compare_placeholder_rows(ui_lang: str) -> list[dict[str, str]]:
    return [
        {
            "label": _t(ui_lang, "research.player.placeholder_status"),
            "value": _t(ui_lang, "research.player.no_comparison_selected"),
        },
        {
            "label": _t(ui_lang, "research.player.next_step"),
            "value": _player_compare_picker_title(ui_lang),
        },
    ]


def _player_compare_invalid_notice(language_slug: str, task_key: str, ui_lang: str) -> str:
    task_label = _player_task_display_label(language_slug, task_key, ui_lang)
    return _t(ui_lang, "research.player.compare_invalid_notice", task_label=task_label)


def _player_compare_partial_notice(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.compare_partial_notice")


def _player_controls_status_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.controls_status")


def _player_volume_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.volume")


def _player_speed_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.speed")


def _player_speaker_activate_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.activate")


def _player_mode_hint(ui_lang: str, mode_key: str) -> str:
    if mode_key == "manual":
        return _t(ui_lang, "research.player.mode_hint.manual")
    if mode_key == "sequence":
        return _t(ui_lang, "research.player.mode_hint.sequence")
    return _t(ui_lang, "research.player.mode_hint.single")


def _wordlist_items_label(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.wordlist")


def _player_missing_message(task_key: str, ui_lang: str) -> str:
    if task_key == "wordlist":
        return _t(ui_lang, "research.player.missing_message.wordlist")
    return _t(ui_lang, "research.player.missing_message.generic")


def _player_missing_hint(task_key: str, ui_lang: str) -> str | None:
    if task_key == "wordlist":
        return _t(ui_lang, "research.player.missing_hint.wordlist")
    return _t(ui_lang, "research.player.missing_hint.generic")


def _player_set_banner_title(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.set_banner.active_title")


def _player_set_requires_auth_title(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.set_banner.requires_auth_title")


def _player_set_unavailable_title(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.set_banner.unavailable_title")


def _player_set_requires_auth_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.set_banner.requires_auth_text")


def _player_set_unavailable_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.set_banner.unavailable_text")


def _player_set_storage_unavailable_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.set_banner.storage_unavailable_text")


def _player_set_empty_message(task_label: str, ui_lang: str) -> str:
    return _t(ui_lang, "research.player.set_banner.empty_message", task_label=task_label)


def _player_set_empty_hint(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.set_banner.empty_hint")


def _player_set_interview_hint(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.set_banner.interview_hint")


def _player_set_focus_missed_text(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.set_banner.focus_missed")


def _player_text_compare_unavailable_notice(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.text_compare_unavailable")


def _player_text_running_mode_notice(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.text_running_mode_notice")


def _player_source_handoff_note(source: str | None, ui_lang: str) -> str | None:
    if source == "comparison":
        return _t(ui_lang, "research.player.source_handoff.comparison")
    if source == "phenomena":
        return _t(ui_lang, "research.player.source_handoff.phenomena")
    return None


def _current_owner_user_id() -> str | None:
    candidate = getattr(g, "user_id", None)
    if isinstance(candidate, str) and candidate.strip():
        return candidate.strip()
    return None


def _player_task_display_label(language_slug: str, task_key: str, ui_lang: str) -> str:
    return get_research_task_label(task_key, ui_lang, variant="material", language_slug=language_slug)


def _load_player_set_context(
    ui_lang: str,
    language_slug: str,
    task_key: str,
    requested_set_id: str | None,
    requested_preset_id: str | None,
    requested_focus_item: str | None,
) -> dict[str, Any] | None:
    del ui_lang
    return resolve_player_set_context(
        language_slug,
        task_key,
        requested_set_id,
        requested_preset_id,
        requested_focus_item,
        owner_user_id=_current_owner_user_id(),
        load_owned_set_fn=load_owned_set,
    )


def _build_player_set_notice(
    ui_lang: str,
    language_slug: str,
    task_key: str,
    set_context: dict[str, Any] | None,
    resolved_focus_item_id: str | None,
) -> dict[str, Any] | None:
    if set_context is None:
        return None

    status = set_context["status"]
    if status == "requires-auth":
        return {
            "status": status,
            "text": _player_set_requires_auth_text(ui_lang),
        }
    if status == "storage-unavailable":
        return {
            "status": status,
            "text": _player_set_storage_unavailable_text(ui_lang),
        }
    if status != "loaded":
        return {
            "status": status,
            "text": _player_set_unavailable_text(ui_lang),
        }

    if task_key in PHENOMENA_ITEM_TASKS and set_context.get("requested_focus_item") and not resolved_focus_item_id:
        return {
            "status": "focus-missed",
            "text": _player_set_focus_missed_text(ui_lang),
        }

    return None


def _format_player_clock(milliseconds: int) -> str:
    total_seconds = max(0, milliseconds // 1000)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _player_intro(ui_lang: str) -> str:
    return _t(ui_lang, "research.player.intro")


def _build_player_query(
    source: str | None,
    compare_session_id: str | None = None,
    compare_mode: str | None = None,
    set_id: str | None = None,
    preset_id: str | None = None,
    focus_item: str | None = None,
    render_mode: str | None = None,
) -> dict[str, str] | None:
    query: dict[str, str] = {}
    if source:
        query["source"] = source
    if compare_session_id:
        query["compare_session"] = compare_session_id
    if compare_mode == "manual":
        query["compare_mode"] = compare_mode
    if set_id:
        query["set_id"] = set_id
    if preset_id:
        query["preset_id"] = preset_id
    if focus_item:
        query["focus_item"] = focus_item
    if render_mode in PLAYER_RENDER_MODES:
        query["render_mode"] = render_mode
    return query or None


def _player_page_href(
    ui_lang: str,
    language_slug: str,
    session_id: str,
    task_key: str,
    source: str | None,
    *,
    compare_session_id: str | None = None,
    compare_mode: str | None = None,
    set_id: str | None = None,
    preset_id: str | None = None,
    focus_item: str | None = None,
    render_mode: str | None = None,
) -> str:
    return _url_with_query(
        "public.research_player",
        ui_lang=ui_lang,
        language_slug=language_slug,
        session_id=session_id,
        task=task_key,
        query=_build_player_query(source, compare_session_id, compare_mode, set_id, preset_id, focus_item, render_mode),
    )


def _player_session_option_label(session: SessionRecord, ui_lang: str) -> str:
    return session.session_id


def _build_player_summary_card(
    session: SessionRecord,
    ui_lang: str,
    language_slug: str,
    role_key: str,
    session_options: list[dict[str, Any]],
) -> dict[str, Any]:
    context_label = _t(ui_lang, "research.comparison.variety_label") if session.is_native else _t(ui_lang, "research.comparison.level_label")
    context_value = _format_standard_variety(session, ui_lang) if session.is_native else _format_level(session, ui_lang)
    detail_label = _origin_country_label(ui_lang) if session.is_native else _t(ui_lang, "common.labels.l1_short")
    detail_value = (session.origin_country or "-") if session.is_native else (session.l1 or "-")
    return {
        "speaker_key": role_key,
        "session_id": session.session_id,
        "accent_modifier": _session_accent_modifier(session),
        "role_label": _t(ui_lang, "research.player.role.primary") if role_key == "primary" else _t(ui_lang, "research.player.role.compare"),
        "profile_href": _url_with_query(
            "public.research_speaker_profile",
            ui_lang=ui_lang,
            language_slug=language_slug,
            person_id=session.person_id,
            query={"session": session.session_id},
        ),
        "profile_label": _t(ui_lang, "research.player.profile"),
        "session_switch": {
            "label": _player_session_switcher_label(ui_lang, role_key),
            "current_label": session.session_id,
            "options": session_options,
        },
        "badges": [
            _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
            context_value if context_value != "-" else None,
        ],
        "rows": [
            {"label": "Person-ID", "value": session.person_id},
            {"label": _recording_date_label(ui_lang), "value": _format_recording_date(session)},
            {"label": context_label, "value": context_value},
            {"label": detail_label, "value": detail_value},
        ],
        "is_placeholder": False,
        "is_visible": True,
        "card_actions": [],
        "activate_label": _player_speaker_activate_label(ui_lang),
    }


def _build_text_player_items(
    ui_lang: str,
    language_slug: str,
    session: SessionRecord,
    task_key: str,
    bundle: Mapping[str, Any],
    item_filter: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    bundle_items = {item["item_id"]: item for item in bundle["items"]}
    visible_items = item_filter or [
        {
            "item_id": item["item_id"],
            "item_number": item["item_number"],
            "text": item["text"],
            "group_id": None,
            "segment_id": None,
            "note": None,
        }
        for item in bundle["items"]
    ]

    rows: list[dict[str, Any]] = []
    for visible_item in visible_items:
        bundle_item = bundle_items.get(visible_item["item_id"])
        if bundle_item is None:
            rows.append(
                {
                    "item_id": visible_item["item_id"],
                    "item_number": visible_item["item_number"],
                    "text": visible_item["text"],
                    "group_id": visible_item.get("group_id"),
                    "segment_id": visible_item.get("segment_id"),
                    "note": visible_item.get("note"),
                    "start_label": "",
                    "end_label": "",
                    "download_href": None,
                    "start_ms": None,
                    "end_ms": None,
                    "is_available": False,
                    "missing_label": _t(ui_lang, "research.player.no_clip_in_session"),
                }
            )
            continue

        rows.append(
            {
                "item_id": bundle_item["item_id"],
                "item_number": visible_item["item_number"],
                "text": visible_item["text"],
                "group_id": visible_item.get("group_id"),
                "segment_id": visible_item.get("segment_id"),
                "note": visible_item.get("note"),
                "start_label": _format_player_clock(bundle_item["start_ms"]),
                "end_label": _format_player_clock(bundle_item["end_ms"]),
                "download_href": url_for(
                    "public.research_player_item_download",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    session_id=session.session_id,
                    task=task_key,
                    item_id=bundle_item["item_id"],
                ) if bundle_item["split_audio_path"] else None,
                "start_ms": bundle_item["start_ms"],
                "end_ms": bundle_item["end_ms"],
                "is_available": True,
                "missing_label": None,
            }
        )
    return rows


def _build_player_compare_placeholder_card(ui_lang: str, session_options: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "speaker_key": "secondary",
        "session_id": "",
        "accent_modifier": "native",
        "role_label": _t(ui_lang, "research.player.role.compare"),
        "profile_href": None,
        "profile_label": _t(ui_lang, "research.player.profile"),
        "session_switch": {
            "label": _player_session_switcher_label(ui_lang, "secondary"),
            "current_label": _player_compare_picker_title(ui_lang),
            "options": session_options,
        },
        "badges": [_player_compare_placeholder_badge(ui_lang)],
        "rows": _player_compare_placeholder_rows(ui_lang),
        "is_placeholder": True,
        "is_visible": False,
        "card_actions": [],
    }


def _build_wordlist_player_items(
    ui_lang: str,
    language_slug: str,
    session: SessionRecord,
    task_key: str,
    bundle: Mapping[str, Any],
    item_filter: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    bundle_items = {item["item_id"]: item for item in bundle["items"]}
    visible_items = item_filter or [
        {
            "item_id": item["item_id"],
            "item_number": item["item_number"],
            "text": item["text"],
        }
        for item in bundle["items"]
    ]

    rows: list[dict[str, Any]] = []
    for visible_item in visible_items:
        bundle_item = bundle_items.get(visible_item["item_id"])
        if bundle_item is None:
            rows.append(
                {
                    "item_id": visible_item["item_id"],
                    "item_number": visible_item["item_number"],
                    "text": visible_item["text"],
                    "start_label": "",
                    "end_label": "",
                    "download_href": None,
                    "start_ms": None,
                    "end_ms": None,
                    "is_available": False,
                    "missing_label": _t(ui_lang, "research.player.no_clip_in_session"),
                }
            )
            continue

        rows.append(
            {
                "item_id": bundle_item["item_id"],
                "item_number": visible_item["item_number"],
                "text": visible_item["text"],
                "start_label": _format_player_clock(bundle_item["start_ms"]),
                "end_label": _format_player_clock(bundle_item["end_ms"]),
                "download_href": url_for(
                    "public.research_player_item_download",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    session_id=session.session_id,
                    task=task_key,
                    item_id=bundle_item["item_id"],
                ) if bundle_item["split_audio_path"] else None,
                "start_ms": bundle_item["start_ms"],
                "end_ms": bundle_item["end_ms"],
                "is_available": True,
                "missing_label": None,
            }
        )
    return rows


def _build_player_switchers(
    ui_lang: str,
    language_slug: str,
    primary_session: SessionRecord,
    task_key: str,
    source: str | None,
    ready_sessions: list[SessionRecord],
    compare_session: SessionRecord | None,
    compare_mode: str,
    set_id: str | None = None,
    preset_id: str | None = None,
    focus_item: str | None = None,
    render_mode: str | None = None,
) -> dict[str, Any]:
    compare_session_id = compare_session.session_id if compare_session else None
    primary_options = [
        {
            "label": _player_session_option_label(candidate, ui_lang),
            "href": _player_page_href(
                ui_lang,
                language_slug,
                candidate.session_id,
                task_key,
                source,
                compare_session_id=compare_session_id if compare_session_id != candidate.session_id else None,
                compare_mode=compare_mode,
                set_id=set_id,
                preset_id=preset_id,
                focus_item=focus_item,
                render_mode=render_mode if task_key == "text" else None,
            ),
            "current": candidate.session_id == primary_session.session_id,
        }
        for candidate in ready_sessions
    ]

    compare_options = [
        {
            "label": _player_compare_disabled_option(ui_lang),
            "href": _player_page_href(
                ui_lang,
                language_slug,
                primary_session.session_id,
                task_key,
                source,
                set_id=set_id,
                preset_id=preset_id,
                focus_item=focus_item,
                render_mode=render_mode if task_key == "text" else None,
            ),
            "current": compare_session is None,
        }
    ]
    for candidate in ready_sessions:
        if candidate.session_id == primary_session.session_id:
            continue
        compare_options.append(
            {
                "label": _player_session_option_label(candidate, ui_lang),
                "href": _player_page_href(
                    ui_lang,
                    language_slug,
                    primary_session.session_id,
                    task_key,
                    source,
                    compare_session_id=candidate.session_id,
                    compare_mode=compare_mode,
                    set_id=set_id,
                    preset_id=preset_id,
                    focus_item=focus_item,
                    render_mode=render_mode if task_key == "text" else None,
                ),
                "current": compare_session is not None and candidate.session_id == compare_session.session_id,
            }
        )

    return {
        "title": _player_session_switch_title(ui_lang),
        "hint": _player_session_switch_hint(ui_lang),
        "primary": {"label": _player_primary_session_label(ui_lang), "options": primary_options},
        "compare": {"label": _player_compare_session_label(ui_lang), "options": compare_options},
    }


def _player_origin_context(
    ui_lang: str,
    language_slug: str,
    session: SessionRecord,
    task_key: str,
    source: str | None,
    profile_href: str,
    set_id: str | None = None,
    preset_id: str | None = None,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    speakers_href = url_for("public.research_language_page", ui_lang=ui_lang, language_slug=language_slug, page_slug="speakers")
    recordings_href = _url_with_query(
        "public.research_language_page",
        ui_lang=ui_lang,
        language_slug=language_slug,
        page_slug="recordings",
        query={"task": task_key},
    )
    speakers_label = get_research_page_label("speakers", ui_lang)
    recordings_label = get_research_page_label("recordings", ui_lang)
    comparison_label = get_research_page_label("comparison", ui_lang)
    phenomena_label = get_research_page_label("phenomena", ui_lang)
    profile_label = _t(ui_lang, "research.player.profile")

    if source == "recordings":
        return (
            {"label": _t(ui_lang, "research.player.back_recordings"), "href": recordings_href},
            [{"label": recordings_label, "href": recordings_href}],
        )
    if source == "profile":
        return (
            {"label": _t(ui_lang, "research.player.back_profile"), "href": profile_href},
            [
                {"label": speakers_label, "href": speakers_href},
                {"label": profile_label, "href": profile_href},
            ],
        )
    if source == "comparison":
        comparison_href = _comparison_page_href(
            ui_lang,
            language_slug,
            set_id=set_id,
            task=task_key if task_key in PHENOMENA_ITEM_TASKS else None,
        )
        return (
            {"label": _t(ui_lang, "research.player.back_comparison"), "href": comparison_href},
            [{"label": comparison_label, "href": comparison_href}],
        )
    if source == "phenomena":
        phenomena_href = _phenomena_page_href(
            ui_lang,
            language_slug,
            preset_id=preset_id,
            set_id=set_id,
            task=task_key if task_key in PHENOMENA_ITEM_TASKS else None,
        )
        return (
            {"label": _t(ui_lang, "research.player.back_phenomena"), "href": phenomena_href},
            [{"label": phenomena_label, "href": phenomena_href}],
        )
    return (
        {"label": _t(ui_lang, "research.player.back_speakers"), "href": speakers_href},
        [{"label": speakers_label, "href": speakers_href}],
    )


def _build_player_task_panels(
    ui_lang: str,
    language_slug: str,
    session: SessionRecord,
    requested_task_key: str,
    source: str | None,
    wordlist_ready: bool,
    text_ready: bool,
    compare_session_id: str | None = None,
    compare_mode: str | None = None,
    set_id: str | None = None,
    preset_id: str | None = None,
    focus_item: str | None = None,
    render_mode: str | None = None,
) -> list[dict[str, Any]]:
    panels: list[dict[str, Any]] = []
    for task in iter_research_tasks():
        is_available = session_has_task(session, task.key)
        is_current = task.key == requested_task_key
        href: str | None = None
        state_label: str

        if not is_available:
            state_label = _unavailable_label(ui_lang)
        elif task.key in {"wordlist", "text"}:
            task_ready = wordlist_ready if task.key == "wordlist" else text_ready
            if task_ready:
                href = None if is_current else _player_page_href(
                    ui_lang,
                    language_slug,
                    session.session_id,
                    task.key,
                    source,
                    compare_session_id=compare_session_id,
                    compare_mode=compare_mode,
                    set_id=set_id,
                    preset_id=preset_id,
                    focus_item=focus_item,
                    render_mode=render_mode if task.key == "text" else None,
                )
                state_label = _player_current_label(ui_lang) if is_current else _player_available_label(ui_lang)
            else:
                state_label = _player_artifacts_missing_label(ui_lang)
        else:
            state_label = _player_not_ready_label(ui_lang)

        panels.append(
            {
                "key": task.key,
                "label": task.short_label(ui_lang),
                "description": task.description(ui_lang),
                "href": href,
                "current": is_current,
                "is_disabled": href is None,
                "state_label": state_label,
            }
        )
    return panels


def _player_render_mode_label(ui_lang: str, render_mode: str) -> str:
    if render_mode == "running_text":
        return _t(ui_lang, "research.player.view_text")
    return _t(ui_lang, "research.player.view_list")


def _build_player_render_mode_switch(
    ui_lang: str,
    language_slug: str,
    session_id: str,
    task_key: str,
    source: str | None,
    *,
    compare_session_id: str | None,
    compare_mode: str | None,
    set_id: str | None,
    preset_id: str | None,
    focus_item: str | None,
    player_source: NormalizedPlayerSource,
) -> dict[str, Any] | None:
    if player_source.task_key != "text" or len(player_source.allowed_render_modes) <= 1:
        return None

    options = []
    for render_mode in player_source.allowed_render_modes:
        options.append(
            {
                "key": render_mode,
                "label": _player_render_mode_label(ui_lang, render_mode),
                "current": render_mode == player_source.render_mode,
                "href": _player_page_href(
                    ui_lang,
                    language_slug,
                    session_id,
                    task_key,
                    source,
                    compare_session_id=compare_session_id,
                    compare_mode=compare_mode,
                    set_id=set_id,
                    preset_id=preset_id,
                    focus_item=focus_item,
                    render_mode=render_mode if render_mode != player_source.default_render_mode else None,
                ),
            }
        )

    return {
        "label": _t(ui_lang, "research.player.view_mode"),
        "current": player_source.render_mode,
        "options": options,
    }


def _build_player_set_select(
    ui_lang: str,
    language_slug: str,
    session_id: str,
    task_key: str,
    source: str | None,
    *,
    compare_session_id: str | None,
    compare_mode: str | None,
    active_set_id: str | None,
    active_preset_id: str | None,
    render_mode: str | None,
) -> dict[str, Any] | None:
    if task_key not in PHENOMENA_ITEM_TASKS:
        return None

    options = [
        {
            "label": _t(ui_lang, "research.player.all_items"),
            "href": _player_page_href(
                ui_lang,
                language_slug,
                session_id,
                task_key,
                source,
                compare_session_id=compare_session_id,
                compare_mode=compare_mode,
                render_mode=render_mode if task_key == "text" else None,
            ),
            "current": active_set_id is None and active_preset_id is None,
        }
    ]

    for preset in load_phenomena_presets(language_slug):
        options.append(
            {
                "label": preset.label,
                "href": _player_page_href(
                    ui_lang,
                    language_slug,
                    session_id,
                    task_key,
                    source,
                    compare_session_id=compare_session_id,
                    compare_mode=compare_mode,
                    preset_id=preset.preset_id,
                    render_mode=render_mode if task_key == "text" else None,
                ),
                "current": active_set_id is None and preset.preset_id == active_preset_id,
            }
        )

    owner_user_id = _current_owner_user_id()
    if owner_user_id is not None:
        try:
            stored_sets = list_selectable_owned_sets(
                owner_user_id=owner_user_id,
                corpus_language=language_slug,
                current_set_id=active_set_id,
            )
        except (ResearchSetStorageUnavailableError, ResearchSetValidationError, RuntimeError):
            stored_sets = []

        for stored_set in stored_sets:
            options.append(
                {
                    "label": stored_set.label or _t(ui_lang, "common.untitled"),
                    "href": _player_page_href(
                        ui_lang,
                        language_slug,
                        session_id,
                        task_key,
                        source,
                        compare_session_id=compare_session_id,
                        compare_mode=compare_mode,
                        set_id=stored_set.set_id,
                        render_mode=render_mode if task_key == "text" else None,
                    ),
                    "current": stored_set.set_id == active_set_id,
                }
            )

    return {
        "label": _t(ui_lang, "research.player.set_select_label"),
        "info_label": _t(ui_lang, "research.player.set_select_info_label"),
        "info_text": _t(ui_lang, "research.player.set_select_info_text"),
        "disabled": len(options) <= 1,
        "options": options,
    }


def build_player_page(
    ui_lang: str,
    language_slug: str,
    session_id: str,
    task_key: str,
    source: str | None,
    compare_session_id: str | None = None,
    compare_mode: str | None = None,
    set_id: str | None = None,
    preset_id: str | None = None,
    focus_item: str | None = None,
    render_mode: str | None = None,
) -> dict[str, Any] | None:
    session = get_session(language_slug, session_id)
    task = get_research_task(task_key)
    if session is None or task is None or not session_has_task(session, task_key):
        return None

    runtime_state = resolve_player_runtime_state(
        ui_lang,
        language_slug,
        session,
        task_key,
        owner_user_id=_current_owner_user_id(),
        compare_session_id=compare_session_id,
        compare_mode=compare_mode,
        set_id=set_id,
        preset_id=preset_id,
        focus_item=focus_item,
        render_mode=render_mode,
        load_owned_set_fn=load_owned_set,
    )
    set_context = runtime_state.set_context
    effective_set_id = runtime_state.effective_set_id
    effective_preset_id = runtime_state.effective_preset_id
    active_selector_preset_id = runtime_state.active_selector_preset_id

    profile_href = _url_with_query(
        "public.research_speaker_profile",
        ui_lang=ui_lang,
        language_slug=language_slug,
        person_id=session.person_id,
        query={"session": session.session_id},
    )

    origin_link, ancestors = _player_origin_context(
        ui_lang,
        language_slug,
        session,
        task_key,
        source,
        profile_href,
        effective_set_id,
        effective_preset_id,
    )

    context_value = _format_standard_variety(session, ui_lang) if session.is_native else _format_level(session, ui_lang)
    detail_value = (session.origin_country or "-") if session.is_native else (session.l1 or "-")
    text_bundle = _load_task_bundle(session, "text") if session_has_task(session, "text") else None
    text_ready = text_bundle is not None
    wordlist_bundle = _load_task_bundle(session, "wordlist") if session_has_task(session, "wordlist") else None
    wordlist_ready = wordlist_bundle is not None
    task_bundle = runtime_state.task_bundle
    ready_sessions = runtime_state.ready_sessions
    compare_session = runtime_state.compare_session
    compare_bundle = runtime_state.compare_bundle
    compare_notice = _player_compare_invalid_notice(language_slug, task_key, ui_lang) if runtime_state.compare_requested_unavailable else None
    effective_compare_mode = runtime_state.effective_compare_mode
    player_source = runtime_state.player_source
    active_render_mode_query = runtime_state.active_render_mode_query
    task_panels = _build_player_task_panels(
        ui_lang,
        language_slug,
        session,
        task_key,
        source,
        wordlist_ready,
        text_ready,
        compare_session.session_id if compare_session else None,
        effective_compare_mode,
        set_id,
        preset_id,
        focus_item,
        active_render_mode_query,
    )
    summary_cards: list[dict[str, Any]] = []

    player_view: dict[str, Any]
    filtered_task_empty = runtime_state.filtered_task_empty

    if task_key in PHENOMENA_ITEM_TASKS and task_bundle is not None and player_source is not None:
        player_switchers = _build_player_switchers(
            ui_lang,
            language_slug,
            session,
            task_key,
            source,
            ready_sessions,
            compare_session,
            effective_compare_mode,
            effective_set_id,
            effective_preset_id,
            focus_item,
            active_render_mode_query,
        ) if ready_sessions else None
        primary_session_options = player_switchers["primary"]["options"] if player_switchers else [
            {
                "label": session.session_id,
                "href": _player_page_href(
                    ui_lang,
                    language_slug,
                    session.session_id,
                    task_key,
                    source,
                    set_id=effective_set_id,
                    preset_id=effective_preset_id,
                    focus_item=focus_item,
                    render_mode=active_render_mode_query if task_key == "text" else None,
                ),
                "current": True,
            }
        ]
        compare_session_options = player_switchers["compare"]["options"][1:] if player_switchers else []
        compare_is_ready = compare_session is not None and compare_bundle is not None
        can_compare = bool(compare_session_options)
        primary_items = runtime_state.primary_items
        secondary_items = runtime_state.secondary_items
        compare_rows = runtime_state.compare_rows if compare_is_ready else []
        visible_focus_item = runtime_state.visible_focus_item_id
        manual_compare_href = _player_page_href(
            ui_lang,
            language_slug,
            session.session_id,
            task_key,
            source,
            compare_session_id=compare_session.session_id if compare_session else None,
            compare_mode="manual",
            set_id=effective_set_id,
            preset_id=effective_preset_id,
            focus_item=visible_focus_item or focus_item,
            render_mode=active_render_mode_query if task_key == "text" else None,
        ) if compare_session else None
        sequence_compare_href = _player_page_href(
            ui_lang,
            language_slug,
            session.session_id,
            task_key,
            source,
            compare_session_id=compare_session.session_id if compare_session else None,
            set_id=effective_set_id,
            preset_id=effective_preset_id,
            focus_item=visible_focus_item or focus_item,
            render_mode=active_render_mode_query if task_key == "text" else None,
        ) if compare_session else None
        primary_summary = _build_player_summary_card(session, ui_lang, language_slug, "primary", primary_session_options)
        primary_summary["card_actions"].append(
            {
                "kind": "link",
                "action": "profile",
                "label": primary_summary["profile_label"],
                "href": primary_summary["profile_href"],
            }
        )
        if can_compare and not compare_is_ready:
            primary_summary["card_actions"].append(
                {"kind": "button", "action": "compare-add", "label": _player_compare_add_label(ui_lang)}
            )
        summary_cards.append(primary_summary)

        if compare_is_ready:
            secondary_summary = _build_player_summary_card(
                compare_session,
                ui_lang,
                language_slug,
                "secondary",
                compare_session_options,
            )
            secondary_summary["card_actions"].append(
                {
                    "kind": "link",
                    "action": "profile",
                    "label": secondary_summary["profile_label"],
                    "href": secondary_summary["profile_href"],
                }
            )
            secondary_summary["card_actions"].append(
                {
                    "kind": "link",
                    "action": "compare-remove",
                    "label": _player_compare_remove_label(ui_lang),
                    "href": _player_page_href(
                        ui_lang,
                        language_slug,
                        session.session_id,
                        task_key,
                        source,
                        set_id=effective_set_id,
                        preset_id=effective_preset_id,
                        focus_item=visible_focus_item or focus_item,
                        render_mode=active_render_mode_query if task_key == "text" else None,
                    ),
                }
            )
            summary_cards.append(secondary_summary)
        elif can_compare:
            secondary_placeholder = _build_player_compare_placeholder_card(ui_lang, compare_session_options)
            secondary_placeholder["card_actions"].append(
                {"kind": "button", "action": "compare-remove", "label": _player_compare_remove_label(ui_lang)}
            )
            summary_cards.append(secondary_placeholder)

        controls_hint = compare_notice
        if controls_hint is None and compare_is_ready and any(not row["secondary"]["is_available"] for row in compare_rows):
            controls_hint = _player_compare_partial_notice(ui_lang)
        render_mode_switch = _build_player_render_mode_switch(
            ui_lang,
            language_slug,
            session.session_id,
            task_key,
            source,
            compare_session_id=compare_session.session_id if compare_session else None,
            compare_mode=effective_compare_mode if compare_session else None,
            set_id=effective_set_id,
            preset_id=effective_preset_id,
            focus_item=visible_focus_item or focus_item,
            player_source=player_source,
        )
        set_select = _build_player_set_select(
            ui_lang,
            language_slug,
            session.session_id,
            task_key,
            source,
            compare_session_id=compare_session.session_id if compare_session else None,
            compare_mode=effective_compare_mode if compare_session else None,
            active_set_id=effective_set_id,
            active_preset_id=active_selector_preset_id,
            render_mode=active_render_mode_query,
        )
        player_view = {
            "mode": task_key,
            "source_kind": player_source.source_kind,
            "render_mode": player_source.render_mode,
            "render_modes": render_mode_switch,
            "set_select": set_select,
            "primary_audio_mode": player_source.primary_audio_mode,
            "supports_full_audio": player_source.supports_full_audio,
            "audio_href": url_for(
                "public.research_player_audio",
                ui_lang=ui_lang,
                language_slug=language_slug,
                session_id=session.session_id,
                task=task_key,
            ),
            "controls_title": _t(ui_lang, "research.player.controls_title") if task_key == "wordlist" else player_source.items_title,
            "controls_status_label": _player_controls_status_label(ui_lang),
            "controls_status_value": session.session_id,
            "controls_hint": controls_hint,
            "items_title": player_source.items_title,
            "items_count": len(primary_items),
            "set_notice": _build_player_set_notice(
                ui_lang,
                language_slug,
                task_key,
                set_context,
                visible_focus_item,
            ),
            "download_label": _t(ui_lang, "research.player.download_mp3"),
            "toggle_play_label": _player_play_label(ui_lang),
            "toggle_pause_label": _player_pause_label(ui_lang),
            "volume_label": _player_volume_label(ui_lang),
            "speed_label": _player_speed_label(ui_lang),
            "primary": {
                "speaker_key": "primary",
                "session_id": session.session_id,
                "label": session.session_id,
                "role_label": _t(ui_lang, "research.player.role.primary"),
                "audio_href": url_for(
                    "public.research_player_audio",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    session_id=session.session_id,
                    task=task_key,
                ),
                "items": primary_items,
            },
            "secondary": {
                "speaker_key": "secondary",
                "session_id": compare_session.session_id,
                "label": compare_session.session_id,
                "role_label": _t(ui_lang, "research.player.role.compare"),
                "audio_href": url_for(
                    "public.research_player_audio",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    session_id=compare_session.session_id,
                    task=task_key,
                ),
                "items": secondary_items,
            } if compare_session and compare_bundle else None,
            "compare": {
                "is_ready": compare_is_ready,
                "mode": effective_compare_mode,
                "has_candidates": can_compare,
                "sequence_toggle": {
                    "label": _player_sequence_toggle_label(ui_lang),
                    "enabled": effective_compare_mode == "sequence",
                    "off_href": manual_compare_href,
                    "on_href": sequence_compare_href,
                } if compare_is_ready else None,
                "switchers": player_switchers,
                "rows": compare_rows,
            },
            "text_blocks": _build_running_text_blocks(primary_items) if task_key == "text" and player_source.render_mode == "running_text" and not compare_is_ready else [],
            "client_state": {
                "requestedMode": effective_compare_mode,
                "compareOpen": compare_is_ready,
                "canCompare": can_compare,
                "mobileMinWidth": 900,
                "rateOptions": [0.5, 0.75, 1.0, 1.25, 1.5],
                "defaultRate": 1.0,
                "defaultRateIndex": 2,
                "defaultVolume": 1.0,
                "singleViewHref": _player_page_href(
                    ui_lang,
                    language_slug,
                    session.session_id,
                    task_key,
                    source,
                    set_id=effective_set_id,
                    preset_id=effective_preset_id,
                    focus_item=visible_focus_item or focus_item,
                    render_mode=active_render_mode_query if task_key == "text" else None,
                ),
                "modeHrefs": {
                    "manual": manual_compare_href,
                    "sequence": sequence_compare_href,
                },
                "speakers": [
                    {
                        "key": "primary",
                        "sessionId": session.session_id,
                        "label": session.session_id,
                        "items": [
                            {
                                "itemId": item["item_id"],
                                "startMs": item["start_ms"],
                                "endMs": item["end_ms"],
                            }
                            for item in primary_items
                            if item["is_available"] and item["start_ms"] is not None and item["end_ms"] is not None
                        ],
                    }
                ] + ([
                    {
                        "key": "secondary",
                        "sessionId": compare_session.session_id,
                        "label": compare_session.session_id,
                        "items": [
                            {
                                "itemId": item["item_id"],
                                "startMs": item["start_ms"],
                                "endMs": item["end_ms"],
                            }
                            for item in secondary_items
                            if item["is_available"] and item["start_ms"] is not None and item["end_ms"] is not None
                        ],
                    }
                ] if compare_session and compare_bundle else []),
                "compareReady": compare_is_ready,
                "focusedItemId": visible_focus_item,
                "statusLabel": _player_controls_status_label(ui_lang),
                "togglePlay": _player_play_label(ui_lang),
                "togglePause": _player_pause_label(ui_lang),
                "items": [
                    {
                        "itemId": item["item_id"],
                        "startMs": item["start_ms"],
                        "endMs": item["end_ms"],
                    }
                    for item in primary_items
                    if item["is_available"] and item["start_ms"] is not None and item["end_ms"] is not None
                ],
            },
            "items": primary_items,
        }
        if filtered_task_empty:
            player_view["empty_state"] = {
                "title": player_source.items_title,
                "message": _player_set_empty_message(_player_task_display_label(language_slug, task_key, ui_lang), ui_lang),
                "hint": _player_set_empty_hint(ui_lang),
            }
    else:
        fallback_href = None
        fallback_wordlist_available = wordlist_ready and (
            set_context is None
            or set_context["status"] != "loaded"
            or set_context["task_counts"].get("wordlist", 0) > 0
        )
        if task_key != "wordlist" and fallback_wordlist_available:
            fallback_href = _player_page_href(
                ui_lang,
                language_slug,
                session.session_id,
                "wordlist",
                source,
                set_id=effective_set_id,
                preset_id=effective_preset_id,
                focus_item=focus_item,
            )
        player_message = _player_missing_message(task_key, ui_lang)
        player_hint = _player_missing_hint(task_key, ui_lang)
        if filtered_task_empty:
            player_message = _player_set_empty_message(_player_task_display_label(language_slug, task_key, ui_lang), ui_lang)
            player_hint = _player_set_empty_hint(ui_lang)
        elif set_context is not None and set_context["status"] == "loaded" and task_key == "interview":
            player_hint = _player_set_interview_hint(ui_lang)
        player_view = {
            "mode": "unavailable",
            "title": _t(ui_lang, "research.player.status_title"),
            "message": player_message,
            "hint": player_hint,
            "set_select": _build_player_set_select(
                ui_lang,
                language_slug,
                session.session_id,
                task_key,
                source,
                compare_session_id=compare_session.session_id if compare_session else None,
                compare_mode=effective_compare_mode if compare_session else None,
                active_set_id=effective_set_id,
                active_preset_id=active_selector_preset_id,
                render_mode=active_render_mode_query,
            ) if task_key in PHENOMENA_ITEM_TASKS else None,
            "set_notice": _build_player_set_notice(
                ui_lang,
                language_slug,
                task_key,
                set_context,
                None,
            ),
            "fallback_link": {
                "href": fallback_href,
                "label": _t(ui_lang, "research.player.open_wordlist"),
            } if fallback_href else None,
        }

    page_title = _t(ui_lang, "research.player.page_title")

    return {
        "title": page_title,
        "template": "pages/research_player.html",
        "page_kind": "workbench",
        "access": "protected",
        "content_header": build_content_header(
            page_name="research",
            title=page_title,
            intro=_player_intro(ui_lang),
            section_label=get_section_label("research", ui_lang),
            section_href=url_for("public.research_home", ui_lang=ui_lang),
            context_mode="language",
            context_title=_language_context(ui_lang, language_slug)[1],
            context_root_href=url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug),
            ancestors=ancestors,
        ),
        "origin_link": origin_link,
        "speakers_href": url_for("public.research_language_page", ui_lang=ui_lang, language_slug=language_slug, page_slug="speakers"),
        "recordings_href": _url_with_query(
            "public.research_language_page",
            ui_lang=ui_lang,
            language_slug=language_slug,
            page_slug="recordings",
            query={"task": task_key},
        ),
        "task_panels": task_panels,
        "summary_cards": summary_cards,
        "summary": {
            "session_id": session.session_id,
            "person_id": session.person_id,
            "recording_date": _format_recording_date(session),
            "speaker_type": _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
            "context_label": _t(ui_lang, "research.comparison.variety_label") if session.is_native else _t(ui_lang, "research.comparison.level_label"),
            "context_value": context_value,
            "detail_label": _origin_country_label(ui_lang) if session.is_native else _t(ui_lang, "common.labels.l1_short"),
            "detail_value": detail_value,
            "task_label": _task_label(ui_lang),
            "task_value": player_source.items_title if task_key == "text" and player_source is not None else task.long_label(ui_lang),
            "recorded_by_label": _recorded_by_label(ui_lang),
            "recorded_by_value": session.recorded_by or "-",
            "recording_date_label": _recording_date_label(ui_lang),
            "accent_modifier": _session_accent_modifier(session),
            "selected_label": player_source.items_title if task_key == "text" and player_source is not None else task.short_label(ui_lang),
            "badges": [
                _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
                context_value if context_value != "-" else None,
            ],
        },
        "player": player_view,
    }


def resolve_player_audio_artifact(language_slug: str, session_id: str, task_key: str) -> Path | None:
    return _resolve_player_audio_artifact_runtime(language_slug, session_id, task_key)


def resolve_player_item_download(language_slug: str, session_id: str, task_key: str, item_id: str) -> dict[str, Any] | None:
    return _resolve_player_item_download_runtime(language_slug, session_id, task_key, item_id)