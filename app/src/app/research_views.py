"""View-model builders for PROMAT research workbench pages."""

from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import urlencode

from flask import url_for

from .research_sessions import (
    LEVEL_ORDER,
    SpeakerProfile,
    SessionRecord,
    get_research_task,
    get_session,
    get_speaker_profile,
    iter_research_tasks,
    load_language_sessions,
    load_speaker_profiles,
    session_has_task,
)
from .routes.public_content import get_language, get_language_label, get_research_page_label, get_section_label


SPEAKER_TYPE_LABELS = {
    "learner": {"de": "Lernende", "en": "Learner"},
    "native_speaker": {"de": "Native Speaker", "en": "Native Speaker"},
    "heritage_speaker": {"de": "Heritage Speaker", "en": "Heritage Speaker"},
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
        "de": "Aufgabenorientierter Zugang zum spanischen Korpus mit klar getrennten Task-Panels, kompakten Filtern und direktem Übergang in die vorbereitete Player-Route.",
        "en": "Task-first access to the Spanish corpus with clearly separated task panels, compact filters, and direct links into the prepared player route.",
    },
    "speakers": {
        "de": "Personenorientierter Zugang zum spanischen Korpus mit ruhigen Profilkarten, reduzierten Metadaten und einem klar getrennten Profilzugang.",
        "en": "Person-first access to the Spanish corpus with calm profile cards, reduced metadata, and a clearly separated profile view.",
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
    if session.level_code:
        return session.level_code
    return "-"


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


def _format_additional_languages(session: SessionRecord) -> str:
    if not session.additional_languages:
        return "-"
    return ", ".join(session.additional_languages)


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
        return {"label": label, "entries": entries}

    if session.stays_in_target_country is False:
        return {
            "label": label,
            "value": "Keine erfassten Sprachaufenthalte" if ui_lang == "de" else "No recorded stays in the target-language country",
        }

    if session.stays_in_target_country is True:
        return {
            "label": label,
            "value": "Erfasst, ohne Detailangaben" if ui_lang == "de" else "Recorded without detailed stay information",
        }

    return {"label": label, "value": "Nicht erfasst" if ui_lang == "de" else "Not recorded"}


def _uses_native_filters(selected_group: str) -> bool:
    return selected_group == "native_speaker"


def _sorted_distinct(values: list[str | None]) -> list[str]:
    return sorted({value for value in values if value})


def _normalize_text(value: str | None) -> str | None:
    normalized = (value or "").strip()
    return normalized or None


def _normalize_recordings_filters(query_args: Mapping[str, str]) -> dict[str, str]:
    active_task = _normalize_text(query_args.get("task")) or "isolated_speech"
    if get_research_task(active_task) is None:
        active_task = "isolated_speech"
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


def _research_breadcrumbs(ui_lang: str, language_slug: str, current_label: str | None = None) -> list[dict[str, Any]]:
    _, language_label = _language_context(ui_lang, language_slug)
    breadcrumbs = [
        {"label": get_section_label("research", ui_lang), "href": url_for("public.research_home", ui_lang=ui_lang), "current": False},
        {"label": language_label, "href": url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug), "current": current_label is None},
    ]
    if current_label:
        breadcrumbs.append({"label": current_label, "href": None, "current": True})
    return breadcrumbs


def _session_matches_recordings_filters(session: SessionRecord, filters: Mapping[str, str]) -> bool:
    if filters["level"] and session.level_code != filters["level"]:
        return False
    if filters["l1"] and (session.l1 or "").upper() != filters["l1"]:
        return False
    if filters["speaker_type"] and session.speaker_type != filters["speaker_type"]:
        return False
    if filters["gender"] and session.gender != filters["gender"]:
        return False
    if filters["target_country_stay"] == "yes" and session.stays_in_target_country is not True:
        return False
    if filters["target_country_stay"] == "no" and session.stays_in_target_country is not False:
        return False
    if filters["standard_variety"] and session.standard_variety != filters["standard_variety"]:
        return False
    if filters["origin_country"] and session.origin_country != filters["origin_country"]:
        return False
    return True


def _profile_matches_speaker_filters(profile: SpeakerProfile, filters: Mapping[str, str]) -> bool:
    session = profile.primary_session
    if filters["speaker_group"] != "all" and session.speaker_type != filters["speaker_group"]:
        return False
    if filters["level"] and session.level_code != filters["level"]:
        return False
    if filters["l1"] and (session.l1 or "").upper() != filters["l1"]:
        return False
    if filters["gender"] and session.gender != filters["gender"]:
        return False
    if filters["target_country_stay"] == "yes" and session.stays_in_target_country is not True:
        return False
    if filters["target_country_stay"] == "no" and session.stays_in_target_country is not False:
        return False
    if filters["standard_variety"] and session.standard_variety != filters["standard_variety"]:
        return False
    if filters["origin_country"] and session.origin_country != filters["origin_country"]:
        return False
    return True


def _filter_chip(label: str, endpoint: str, *, query: Mapping[str, str], drop_key: str, **values: Any) -> dict[str, str]:
    next_query = dict(query)
    next_query.pop(drop_key, None)
    return {"label": label, "href": _url_with_query(endpoint, query=next_query, **values)}


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
                    "label": "Level" if ui_lang == "de" else "Level",
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


def _speakers_filter_form(ui_lang: str, language_slug: str, filters: Mapping[str, str], profiles: list[SpeakerProfile]) -> dict[str, Any]:
    sessions = [profile.primary_session for profile in profiles]
    levels = sorted({session.level_code for session in sessions if session.level_code}, key=lambda value: LEVEL_ORDER.get(value, 999))
    l1_values = _sorted_distinct([session.l1 for session in sessions])
    genders = _sorted_distinct([session.gender for session in sessions])
    standard_varieties = _sorted_distinct([session.standard_variety for session in sessions])
    origin_countries = _sorted_distinct([session.origin_country for session in sessions])
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
                    "label": "Level" if ui_lang == "de" else "Level",
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
    scoped_sessions = [session for session in sessions if _session_matches_recordings_filters(session, filters)]

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
                    f"Level: {filters['level']}",
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
        if task_count == 0:
            continue
        task_query = dict(filters)
        task_query["task"] = task.key
        task_panels.append(
            {
                "key": task.key,
                "label": task.short_label(ui_lang),
                "description": task.description(ui_lang),
                "count": task_count,
                "count_label": "Aufnahmen" if ui_lang == "de" else "recordings",
                "href": _url_with_query(
                    "public.research_language_page",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug="recordings",
                    query=task_query,
                ),
                "current": task.key == active_task_key,
            }
        )

    filtered_sessions = [session for session in scoped_sessions if session_has_task(session, active_task_key)]

    results = [
        {
            "session_id": session.session_id,
            "person_id": session.person_id,
            "speaker_type": _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
            "level": _format_level(session, ui_lang),
            "l1": session.l1 or "-",
            "gender": _label(GENDER_LABELS, session.gender or "unknown", ui_lang),
            "target_country_stay": _format_target_country_stay(session.stays_in_target_country, ui_lang),
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
        "content_header": {
            "breadcrumbs": _research_breadcrumbs(ui_lang, language_slug),
            "title": get_research_page_label("recordings", ui_lang),
            "intro": RESEARCH_PAGE_INTROS["recordings"][ui_lang],
            "title_id": "promat-page-title",
        },
        "task_panels": task_panels,
        "active_task": {
            "key": active_task.key,
            "label": active_task.long_label(ui_lang),
            "description": active_task.description(ui_lang),
            "count": len(filtered_sessions),
            "count_label": "Aufnahmen" if ui_lang == "de" else "recordings",
        },
        "filter_form": _recordings_filter_form(
            ui_lang,
            language_slug,
            {**filters, "task": active_task_key},
            sessions,
        ),
        "status": {
            "result_count": len(filtered_sessions),
            "active_filter_count": len(active_filters),
            "result_label": "Aufnahmen" if ui_lang == "de" else "Recordings",
            "filter_label": "aktive Filter" if ui_lang == "de" else "active filters",
        },
        "active_filters": active_filters,
        "columns": {"stay": _target_country_stay_label(ui_lang)},
        "results": results,
        "empty_state": {
            "message": "Keine passenden Aufnahmen gefunden." if ui_lang == "de" else "No matching recordings found.",
            "reset_href": _recordings_filter_form(
                ui_lang,
                language_slug,
                {**filters, "task": active_task_key},
                sessions,
            )["reset_href"],
            "reset_label": "Filter zurücksetzen" if ui_lang == "de" else "Reset filters",
        },
    }


def build_speakers_page(ui_lang: str, language_slug: str, query_args: Mapping[str, str]) -> dict[str, Any]:
    filters = _normalize_speakers_filters(query_args)
    profiles = list(load_speaker_profiles(language_slug))
    filtered_profiles = [profile for profile in profiles if _profile_matches_speaker_filters(profile, filters)]

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
                    f"Level: {filters['level']}",
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
    for profile in filtered_profiles:
        session = profile.primary_session
        if session.speaker_type == "native_speaker":
            meta_rows = [
                {"label": _standard_variety_label(ui_lang), "value": _format_standard_variety(session)},
                {"label": _origin_country_label(ui_lang), "value": session.origin_country or "-"},
                {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": _label(GENDER_LABELS, session.gender or "unknown", ui_lang)},
                {"label": _origin_region_label(ui_lang), "value": session.origin_region or "-"},
            ]
        else:
            meta_rows = [
                {"label": "Level", "value": _format_level(session, ui_lang)},
                {"label": "L1", "value": session.l1 or "-"},
                {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": _label(GENDER_LABELS, session.gender or "unknown", ui_lang)},
                {"label": _target_country_stay_label(ui_lang), "value": _format_target_country_stay(session.stays_in_target_country, ui_lang)},
            ]
        cards.append(
            {
                "person_id": profile.person_id,
                "session_id": session.session_id,
                "eyebrow": _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
                "speaker_type": _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
                "meta_rows": meta_rows,
                "profile_href": url_for(
                    "public.research_speaker_profile",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    person_id=profile.person_id,
                ),
                "recordings_label": _recordings_section_label(ui_lang),
                "recording_links_aria_label": _recording_links_aria_label(ui_lang),
                "task_links": [
                    {
                        "label": task.short_label(ui_lang),
                        "href": _url_with_query(
                            "public.research_player_stub",
                            ui_lang=ui_lang,
                            language_slug=language_slug,
                            session_id=session.session_id,
                            task=task.key,
                            query={"source": "speakers"},
                        ),
                    }
                    for task in iter_research_tasks()
                    if session_has_task(session, task.key)
                ],
                "accent_modifier": session.level_code.lower() if session.level_code else "native",
            }
        )

    return {
        "title": get_research_page_label("speakers", ui_lang),
        "template": "pages/research_speakers.html",
        "page_kind": "workbench",
        "access": "protected",
        "content_header": {
            "breadcrumbs": _research_breadcrumbs(ui_lang, language_slug),
            "title": get_research_page_label("speakers", ui_lang),
            "intro": RESEARCH_PAGE_INTROS["speakers"][ui_lang],
            "title_id": "promat-page-title",
        },
        "quick_filters": quick_filters,
        "filter_form": _speakers_filter_form(ui_lang, language_slug, filters, profiles),
        "status": {
            "result_count": len(filtered_profiles),
            "active_filter_count": len(active_filters),
            "result_label": "Sprecher:innen" if ui_lang == "de" else "Speakers",
            "filter_label": "aktive Filter" if ui_lang == "de" else "active filters",
        },
        "active_filters": active_filters,
        "cards": cards,
        "empty_state": {
            "message": "Keine passenden Sprecher:innen gefunden." if ui_lang == "de" else "No matching speakers found.",
            "reset_href": _speakers_filter_form(ui_lang, language_slug, filters, profiles)["reset_href"],
            "reset_label": "Filter zurücksetzen" if ui_lang == "de" else "Reset filters",
        },
    }


def build_speaker_profile_page(ui_lang: str, language_slug: str, person_id: str) -> dict[str, Any] | None:
    profile = get_speaker_profile(language_slug, person_id)
    if profile is None:
        return None

    session = profile.primary_session
    is_native = session.speaker_type == "native_speaker"
    identity_rows = [
        {"label": "Person-ID" if ui_lang == "de" else "Person ID", "value": profile.person_id},
        {"label": "Ausgewählte Session" if ui_lang == "de" else "Selected session", "value": session.session_id},
        {"label": "Aufnahmejahr" if ui_lang == "de" else "Recording year", "value": str(session.recording_year) if session.recording_year else "-"},
        {"label": "Aufnahmedatum" if ui_lang == "de" else "Recording date", "value": session.recording_date.isoformat() if session.recording_date else "-"},
        {"label": _recorded_by_label(ui_lang), "value": session.recorded_by or "-"},
    ]

    if is_native:
        biography_title = "Herkunft und Varietät" if ui_lang == "de" else "Origin and variety"
        biography_rows = [
            {"label": _standard_variety_label(ui_lang), "value": _format_standard_variety(session)},
            {"label": _origin_country_label(ui_lang), "value": session.origin_country or "-"},
            {"label": _origin_region_label(ui_lang), "value": session.origin_region or "-"},
            {"label": "L1", "value": session.l1 or "-"},
            {"label": _mother_l1_label(ui_lang), "value": session.mother_l1 or "-"},
            {"label": _father_l1_label(ui_lang), "value": session.father_l1 or "-"},
            {"label": _additional_languages_label(ui_lang), "value": _format_additional_languages(session)},
            {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": _label(GENDER_LABELS, session.gender or "unknown", ui_lang)},
            {"label": "Geburtsjahr" if ui_lang == "de" else "Birth year", "value": str(session.birth_year) if session.birth_year else "-"},
        ]
    else:
        biography_title = "Sprachbiographie" if ui_lang == "de" else "Language biography"
        biography_rows = [
            {"label": "Level (Selbsteinschätzung)" if ui_lang == "de" else "Level (self rating)", "value": session.level_self or _format_level(session, ui_lang)},
            {"label": "L1", "value": session.l1 or "-"},
            {"label": _mother_l1_label(ui_lang), "value": session.mother_l1 or "-"},
            {"label": _father_l1_label(ui_lang), "value": session.father_l1 or "-"},
            {"label": _additional_languages_label(ui_lang), "value": _format_additional_languages(session)},
            {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": _label(GENDER_LABELS, session.gender or "unknown", ui_lang)},
            {"label": "Geburtsjahr" if ui_lang == "de" else "Birth year", "value": str(session.birth_year) if session.birth_year else "-"},
            {"label": "Aktuelle Region" if ui_lang == "de" else "Current region", "value": session.current_region or "-"},
            {"label": "Region Kindheit" if ui_lang == "de" else "Childhood region", "value": session.childhood_region or "-"},
            _build_exposure_row(session, ui_lang),
        ]

    related_sessions = [
        {
            "session_id": related.session_id,
            "label": f"{related.session_id} · {related.recording_year or '-'} · {(_format_standard_variety(related) if related.speaker_type == 'native_speaker' else _format_level(related, ui_lang))}",
        }
        for related in profile.sessions[1:]
    ]

    return {
        "title": "Profil" if ui_lang == "de" else "Profile",
        "template": "pages/research_speaker_profile.html",
        "page_kind": "workbench",
        "access": "protected",
        "content_header": {
            "breadcrumbs": _research_breadcrumbs(ui_lang, language_slug, "Profil" if ui_lang == "de" else "Profile"),
            "title": "Profil" if ui_lang == "de" else "Profile",
            "intro": "Sprecher:innenprofil mit kompaktem Personen-, Herkunfts- und Aufzeichnungskontext." if ui_lang == "de" else "Speaker profile with concise identity, origin, and recording context.",
            "title_id": "promat-page-title",
        },
        "profile_header": {
            "person_id": profile.person_id,
            "session_id": session.session_id,
            "speaker_type": _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
            "badges": [
                _label(SPEAKER_TYPE_LABELS, session.speaker_type, ui_lang),
                _format_standard_variety(session) if is_native else _format_level(session, ui_lang),
            ],
        },
        "identity_section": {"title": "Aufnahmekontext" if ui_lang == "de" else "Recording context", "rows": identity_rows},
        "biography_section": {"title": biography_title, "rows": biography_rows},
        "notes": session.notes,
        "related_sessions": related_sessions,
        "recordings_label": _recordings_section_label(ui_lang),
        "tasks": [
            {
                "label": task.short_label(ui_lang),
                "description": task.description(ui_lang),
                "href": _url_with_query(
                    "public.research_player_stub",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    session_id=session.session_id,
                    task=task.key,
                    query={"source": "profile"},
                ),
            }
            for task in iter_research_tasks()
            if session_has_task(session, task.key)
        ],
        "speakers_href": url_for("public.research_language_page", ui_lang=ui_lang, language_slug=language_slug, page_slug="speakers"),
    }


def build_player_stub_page(ui_lang: str, language_slug: str, session_id: str, task_key: str, source: str | None) -> dict[str, Any] | None:
    session = get_session(language_slug, session_id)
    task = get_research_task(task_key)
    if session is None or task is None or not session_has_task(session, task_key):
        return None

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
        origin_label = "Zurück zu Aufnahmen" if ui_lang == "de" else "Back to recordings"

    profile = get_speaker_profile(language_slug, session.person_id)
    profile_href = None
    if profile is not None:
        profile_href = url_for(
            "public.research_speaker_profile",
            ui_lang=ui_lang,
            language_slug=language_slug,
            person_id=profile.person_id,
        )

    return {
        "title": task.long_label(ui_lang),
        "template": "pages/research_player_stub.html",
        "page_kind": "workbench",
        "access": "protected",
        "content_header": {
            "breadcrumbs": _research_breadcrumbs(ui_lang, language_slug, task.long_label(ui_lang)),
            "title": task.long_label(ui_lang),
            "intro": "Die Player-Ansicht ist strukturell vorbereitet, wird in diesem Run aber bewusst noch nicht fachlich ausgebaut." if ui_lang == "de" else "The player view is structurally prepared but intentionally not implemented in this run.",
            "title_id": "promat-page-title",
        },
        "origin_link": {"label": origin_label, "href": origin_href},
        "profile_link": {"label": "Zum Profil" if ui_lang == "de" else "Open profile", "href": profile_href} if profile_href else None,
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
            "level": _format_level(session, ui_lang),
            "l1": session.l1 or "-",
            "task": task.long_label(ui_lang),
            "task_description": task.description(ui_lang),
        },
    }