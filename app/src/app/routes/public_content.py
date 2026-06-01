"""Structured content, labels, and route metadata for PROMAT public pages."""

from __future__ import annotations

from typing import Any

from ..i18n import DEFAULT_UI_LANGUAGE, SUPPORTED_UI_LANGUAGES, translate
from ..research_capabilities import get_research_page_capability, get_research_page_order
from ..research_sessions import load_language_sessions
from ..teaching_content import (
    build_teaching_hub_page,
    build_teaching_topic_page,
    count_teaching_topics,
    list_teaching_languages,
    resolve_teaching_edition_ui_lang,
)
from .public_page_content_data import (
    PROJECT_PAGES_CONTENT,
    SPANISH_DESIGN_PAGE_CONTENT,
)


LANGUAGES: tuple[dict[str, Any], ...] = (
    {
        "slug": "spanish",
        "lang_code": "es",
        "labels": {"de": "Spanisch", "en": "Spanish"},
        "root_subtitle": {
            "de": "Forschungsbereich zur spanischen Lernendenaussprache.",
            "en": "Research area for Spanish learner pronunciation.",
        },
        "project_lead": "Prof. Dr. Felix Tacke",
        "conducted_by": "Marlon Merte",
        "material_conception": ("Felix Tacke", "Ana Goás Pérez"),
        "summary": {
            "de": "Referenzkorpus für plurizentrisches Spanisch zwischen methodischer Dokumentation, Vergleich und didaktischer Weitergabe.",
            "en": "Reference corpus for pluricentric Spanish across method documentation, comparison, and teaching transfer.",
        },
        "research_focus": {
            "de": "Variation zwischen standardnaher Moderation, argumentativer Studiensprache und Lernendenaussprache.",
            "en": "Variation across standard-oriented moderation, academic speech, and learner pronunciation.",
        },
        "teaching_focus": {
            "de": "Aussprachebewusstsein für plurizentrisches Spanisch im Unterricht.",
            "en": "Pronunciation awareness for pluricentric Spanish in teaching.",
        },
    },
    {
        "slug": "french",
        "lang_code": "fr",
        "labels": {"de": "Französisch", "en": "French"},
        "root_subtitle": {
            "de": "Forschungsbereich zur französischen Lernendenaussprache.",
            "en": "Research area for French learner pronunciation.",
        },
        "project_lead": "Prof. Dr. Janina Reinhardt",
        "conducted_by": "Amelie Spieß",
        "material_conception": ("Janina Reinhardt",),
        "summary": {
            "de": "Vorbereiteter Korpusbereich für Rhythmus, Vokalqualität und frankophone Variationslagen.",
            "en": "Prepared corpus area for rhythm, vowel quality, and francophone variation.",
        },
        "research_focus": {
            "de": "Rhythmus, Vokalqualität und Registerwechsel in institutionellen Settings.",
            "en": "Rhythm, vowel quality, and register shifts in institutional settings.",
        },
        "teaching_focus": {
            "de": "Unterrichtsmaterial für Hörverstehen, Prosodie und Variationssensibilität.",
            "en": "Teaching materials for listening, prosody, and variation awareness.",
        },
    },
    {
        "slug": "german",
        "lang_code": "de",
        "labels": {"de": "Deutsch", "en": "German"},
        "root_subtitle": {
            "de": "Forschungsbereich zur deutschen Lernendenaussprache.",
            "en": "Research area for German learner pronunciation.",
        },
        "project_lead": "Prof. Dr. Kathrin Siebold",
        "conducted_by": "Theresa Fischer",
        "material_conception": ("Kathrin Siebold, Theresa Fischer",),
        "summary": {
            "de": "Vorbereiteter Korpusbereich für deutsche Ausspracheprofile in Lern- und Vergleichskontexten.",
            "en": "Prepared corpus area for German pronunciation profiles in learning and comparison contexts.",
        },
        "research_focus": {
            "de": "Lernersprache, Normorientierung und didaktisch relevante Abweichungen.",
            "en": "Learner speech, norm orientation, and teaching-relevant deviations.",
        },
        "teaching_focus": {
            "de": "Praxisnahe Materialien zu Wahrnehmung, Produktion und Rückmeldung.",
            "en": "Practical materials for perception, production, and feedback.",
        },
    },
    {
        "slug": "english",
        "lang_code": "en",
        "labels": {"de": "Englisch", "en": "English"},
        "root_subtitle": {
            "de": "Forschungsbereich zur englischen Lernendenaussprache.",
            "en": "Research area for English learner pronunciation.",
        },
        "project_lead": "Prof. Dr. Rolf Kreyer",
        "conducted_by": "Marlon Merte",
        "material_conception": ("Rolf Kreyer",),
        "summary": {
            "de": "Vorbereiteter Korpusbereich für Akzentprofil, Intonation und intelligibility-orientierte Vergleichsachsen.",
            "en": "Prepared corpus area for accent profile, intonation, and intelligibility-oriented comparison.",
        },
        "research_focus": {
            "de": "Akzentprofil, Intonation und Varietätssensibilität in öffentlichen Sprechsituationen.",
            "en": "Accent profile, intonation, and variety awareness in public speaking situations.",
        },
        "teaching_focus": {
            "de": "Aufgaben für Akzentwahrnehmung, Intonation und verständlichkeitsorientierten Englischunterricht.",
            "en": "Tasks for accent perception, intonation, and intelligibility-oriented English teaching.",
        },
    },
)


PROJECT_PAGE_ORDER: tuple[tuple[str, str], ...] = (
    ("about", "project.about"),
    ("structure", "project.structure"),
    ("data-methods", "project.data-methods"),
    ("team", "project.team"),
)

RESEARCH_PAGE_ORDER: tuple[tuple[str, str], ...] = get_research_page_order()

TEACHING_PAGE_ORDER: tuple[tuple[str, str], ...] = (
    ("phenomena", "teaching.phenomena"),
    ("materials", "teaching.materials"),
)


def _localized(value: Any, ui_lang: str) -> Any:
    if isinstance(value, dict):
        return value.get(ui_lang) or value.get(DEFAULT_UI_LANGUAGE) or next(iter(value.values()))
    return value


def _deep_localize(value: Any, ui_lang: str) -> Any:
    if isinstance(value, dict):
        if value and set(value.keys()).issubset(set(SUPPORTED_UI_LANGUAGES)):
            return _localized(value, ui_lang)
        return {key: _deep_localize(item, ui_lang) for key, item in value.items()}
    if isinstance(value, list):
        return [_deep_localize(item, ui_lang) for item in value]
    return value


def get_supported_ui_language(ui_lang: str) -> str | None:
    if ui_lang in SUPPORTED_UI_LANGUAGES:
        return ui_lang
    return None


def get_text(ui_lang: str, key: str, **kwargs: object) -> str:
    return translate(ui_lang, key, **kwargs)


def get_section_label(section_key: str, ui_lang: str) -> str:
    return get_text(ui_lang, f"section.{section_key}")


def get_top_navigation(ui_lang: str) -> list[dict[str, str]]:
    return [
        {"key": "project", "label": get_section_label("project", ui_lang), "href_key": "project_root"},
        {"key": "research", "label": get_section_label("research", ui_lang), "href_key": "research_root"},
        {"key": "teaching", "label": get_section_label("teaching", ui_lang), "href_key": "teaching_root"},
    ]


def get_language(slug: str) -> dict[str, Any] | None:
    for language in LANGUAGES:
        if language["slug"] == slug:
            return language
    return None


def get_canonical_language_slug(slug: str) -> str | None:
    if get_language(slug) is not None:
        return slug
    return None


def get_canonical_project_page_slug(slug: str) -> str | None:
    page_slugs = {page_slug for page_slug, _ in PROJECT_PAGE_ORDER}
    if slug in page_slugs:
        return slug
    return None


def get_canonical_research_page_slug(slug: str) -> str | None:
    page_slugs = {page_slug for page_slug, _ in RESEARCH_PAGE_ORDER}
    if slug in page_slugs:
        return slug
    return None


def get_canonical_teaching_page_slug(slug: str) -> str | None:
    page_slugs = {page_slug for page_slug, _ in TEACHING_PAGE_ORDER}
    if slug in page_slugs:
        return slug
    return None


def get_language_label(language: dict[str, Any], ui_lang: str) -> str:
    return _localized(language["labels"], ui_lang)


def get_research_corpus_title(language: dict[str, Any], ui_lang: str) -> str:
    return _research_corpus_card_title(language, ui_lang)


def get_project_page_label(page_slug: str, ui_lang: str) -> str:
    label_key = dict(PROJECT_PAGE_ORDER)[page_slug]
    return get_text(ui_lang, label_key)


def get_research_page_label(page_slug: str, ui_lang: str) -> str:
    capability = get_research_page_capability(page_slug)
    if capability is None:
        raise KeyError(page_slug)
    label_key = capability.label_key
    return get_text(ui_lang, label_key)


def get_teaching_page_label(page_slug: str, ui_lang: str) -> str:
    label_key = dict(TEACHING_PAGE_ORDER)[page_slug]
    return get_text(ui_lang, label_key)


def _research_corpus_card_title(language: dict[str, Any], ui_lang: str) -> str:
    label = get_language_label(language, ui_lang)
    if ui_lang == "de":
        return f"{label}-Korpus"
    return f"{label} corpus"


def _research_learner_recording_count(language_slug: str) -> int:
    learner_person_ids = {
        session.person_id
        for session in load_language_sessions(language_slug)
        if session.speaker_type == "learner"
    }
    return len(learner_person_ids)


def _research_reference_speaker_count(language_slug: str) -> int:
    native_speaker_ids = {
        session.person_id
        for session in load_language_sessions(language_slug)
        if session.speaker_type == "native_speaker"
    }
    return len(native_speaker_ids)


def _research_learner_recording_copy(count: int, ui_lang: str) -> str:
    if count == 1:
        return get_text(ui_lang, "research.overview.card.learner_recordings.one", count=count)
    return get_text(ui_lang, "research.overview.card.learner_recordings.other", count=count)


def _research_reference_recording_copy(count: int, ui_lang: str) -> str:
    if count == 1:
        return get_text(ui_lang, "research.overview.card.reference_recordings.one", count=count)
    return get_text(ui_lang, "research.overview.card.reference_recordings.other", count=count)


def _research_corpus_card_metadata_rows(language: dict[str, Any], ui_lang: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = [
        {
            "label": get_text(ui_lang, "research.overview.card.project_lead"),
            "value": language["project_lead"],
        },
        {
            "label": get_text(ui_lang, "research.overview.card.material_conception"),
            "value": ", ".join(language["material_conception"]),
        },
        {
            "label": get_text(ui_lang, "research.overview.card.conducted_by"),
            "value": language["conducted_by"],
        },
    ]

    learner_recording_count = _research_learner_recording_count(language["slug"])
    if learner_recording_count > 0:
        rows.append(
            {
                "text": _research_learner_recording_copy(learner_recording_count, ui_lang)
            }
        )
    else:
        rows.append({"text": get_text(ui_lang, "research.overview.card.in_progress")})

    reference_speaker_count = _research_reference_speaker_count(language["slug"])
    if reference_speaker_count > 0:
        rows.append(
            {
                "text": _research_reference_recording_copy(reference_speaker_count, ui_lang)
            }
        )

    return rows


def _research_feature_cards(language_slug: str, ui_lang: str) -> list[dict[str, str]]:
    labels = {
        "design": "Methodische Anlage und Auswahlprinzipien des Korpus.",
        "speakers": "Zugang über Personen mit reduzierten Metadaten, Filtern und späteren Player-Aktionen.",
        "comparison": "Kontrastive Oberfläche für Items über mehrere Sprecher:innen hinweg.",
        "phenomena": "Linguistisch motivierter Zugang über Kategorien und Aussprachephänomene.",
    }
    return [
        {
            "title": get_research_page_label(page_slug, ui_lang),
            "text": labels[page_slug],
            "href_key": f"research:{language_slug}:{page_slug}",
            "link_label": get_text(ui_lang, "nav.open_page"),
            "variant": "selection",
        }
        for page_slug, _ in RESEARCH_PAGE_ORDER
    ]


def _teaching_feature_cards(language_slug: str, ui_lang: str) -> list[dict[str, str]]:
    labels = {
        "phenomena": "Reduzierter Einstieg in didaktisch relevante Aussprachephänomene.",
        "materials": "Vorbereitete Sammlung für Materialien, Arbeitsformate und öffentliche Medienverweise.",
    }
    return [
        {
            "title": get_teaching_page_label(page_slug, ui_lang),
            "text": labels[page_slug],
            "href_key": f"teaching:{language_slug}:{page_slug}",
            "link_label": get_text(ui_lang, "nav.open_page"),
            "variant": "selection",
        }
        for page_slug, _ in TEACHING_PAGE_ORDER
    ]


def build_start_page(ui_lang: str) -> dict[str, Any]:
    return {
        "title": "Pronunciation Matters",
        "layout": "landing",
        "intro": get_text(ui_lang, "landing.intro"),
        "page_kind": "landing",
        "more_link": {"label": get_text(ui_lang, "nav.more"), "href_key": "project_root"},
        "landing_cards": [
            {
                "entry_kind": "research",
                "title": get_text(ui_lang, "landing.research.title"),
                "text": get_text(ui_lang, "landing.research.text"),
                "href_key": "research_root",
                "link_label": get_text(ui_lang, "landing.research.link"),
                "image_asset": "img/cards/research_title_image.jpg",
                "image_alt": get_text(ui_lang, "landing.research.image_alt"),
            },
            {
                "entry_kind": "teaching",
                "title": get_text(ui_lang, "landing.teaching.title"),
                "text": get_text(ui_lang, "landing.teaching.text"),
                "href_key": "teaching_root",
                "link_label": get_text(ui_lang, "landing.teaching.link"),
                "image_asset": "img/cards/unterricht_01.png",
                "image_alt": get_text(ui_lang, "landing.teaching.image_alt"),
            },
        ],
        "sections": [],
    }


def build_corpus_cards_research(ui_lang: str) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for language in LANGUAGES:
        cards.append(
            {
                "title": _research_corpus_card_title(language, ui_lang),
                "modifier": f"pm-card--corpus-research pm-card--lang-{language['lang_code']} pm-corpus-overview-card--shared-accent",
                "metadata_rows": _research_corpus_card_metadata_rows(language, ui_lang),
                "action_label": get_text(ui_lang, "nav.open_corpus"),
                "href_key": f"research:{language['slug']}",
            }
        )
    return cards


def build_corpus_cards_teaching(ui_lang: str) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    teaching_languages = set(list_teaching_languages())
    teaching_language_order = {
        "spanish": 0,
        "english": 1,
        "french": 2,
        "german": 3,
    }
    available_languages: list[tuple[int, str, dict[str, Any], str]] = []
    for language in LANGUAGES:
        if language["slug"] not in teaching_languages:
            continue
        effective_ui_lang = resolve_teaching_edition_ui_lang(language["slug"], ui_lang)
        if effective_ui_lang is None:
            continue
        available_languages.append(
            (
                teaching_language_order.get(language["slug"], len(teaching_language_order)),
                get_language_label(language, ui_lang),
                language,
                effective_ui_lang,
            )
        )

    available_languages.sort(key=lambda item: (item[0], item[1]))

    for _, title, language, effective_ui_lang in available_languages:
        topic_count = count_teaching_topics(language["slug"], effective_ui_lang)
        is_available = topic_count > 0
        if topic_count == 1:
            status = get_text(ui_lang, "teaching.overview.status.one", count=topic_count)
        elif topic_count > 1:
            status = get_text(ui_lang, "teaching.overview.status.other", count=topic_count)
        else:
            status = get_text(ui_lang, "teaching.topic.pending")
        cards.append(
            {
                "title": title,
                "presentation": "teaching-selection-row",
                "modifier": "",
                "is_available": is_available,
                "metadata_rows": [{"text": status}],
                "action_label": get_text(ui_lang, "teaching.action.open_language") if is_available else "",
                **({"href_key": f"teaching:{language['slug']}"} if is_available else {}),
            }
        )
    return cards


def build_research_select_page(ui_lang: str) -> dict[str, Any]:
    return {
        "title": get_section_label("research", ui_lang),
        "eyebrow": get_section_label("research", ui_lang),
        "page_kind": "workbench",
        "corpus_cards": build_corpus_cards_research(ui_lang),
        "sections": [],
        "is_section_root": True,
    }


def build_teaching_select_page(ui_lang: str) -> dict[str, Any]:
    return {
        "title": get_text(ui_lang, "teaching.overview.prompt"),
        "eyebrow": get_section_label("teaching", ui_lang),
        "intro": "",
        "overview_intro": get_text(ui_lang, "teaching.overview.orientation"),
        "selection_prompt": "",
        "page_kind": "material",
        "layout": "teaching",
        "template": "pages/teaching_page.html",
        "corpus_cards": build_corpus_cards_teaching(ui_lang),
        "sections": [],
        "is_section_root": True,
    }


PROJECT_PAGES: dict[str, dict[str, Any]] = PROJECT_PAGES_CONTENT


def build_project_page(ui_lang: str, page_slug: str) -> dict[str, Any] | None:
    page = PROJECT_PAGES.get(page_slug)
    if page is None:
        return None

    localized_page = _deep_localize(page, ui_lang)
    localized_page.setdefault("eyebrow", get_section_label("project", ui_lang))
    return localized_page


def build_research_language_root_page(
    ui_lang: str,
    language_slug: str,
    *,
    is_authenticated: bool,
) -> dict[str, Any] | None:
    language = get_language(language_slug)
    if language is None:
        return None

    title = _research_corpus_card_title(language, ui_lang)
    return {
        "title": title,
        "eyebrow": get_section_label("research", ui_lang),
        "template": "pages/research_language_root.html",
        "intro": _localized(language["root_subtitle"], ui_lang),
        "body_paragraphs": [
            get_text(ui_lang, "research.root.body", corpus_title=title),
            get_text(ui_lang, "research.root.access_text"),
        ],
        "mobile_intro": get_text(ui_lang, "research.root.mobile_intro", corpus_title=title),
        "action_links": []
        if is_authenticated
        else [
            {
                "label": get_text(ui_lang, "research.root.action.access_request"),
                "href_key": "access_request",
            },
            {
                "label": get_text(ui_lang, "research.root.action.login"),
                "href_key": "login",
            },
        ],
        "page_kind": "reading",
        "access": "public",
        "sections": [],
        "is_language_root": True,
    }


def build_research_page(ui_lang: str, language_slug: str, page_slug: str) -> dict[str, Any] | None:
    language = get_language(language_slug)
    capability = get_research_page_capability(page_slug)
    if language is None:
        return None
    if capability is None:
        return None

    title = get_language_label(language, ui_lang)
    page_title = get_research_page_label(page_slug, ui_lang)

    if language_slug != "spanish":
        return {
            "title": page_title,
            "eyebrow": f"{get_section_label('research', ui_lang)} · {title}",
            "intro": get_text(
                ui_lang,
                "research.placeholder.intro",
                page_title=page_title,
                language_title=title,
            ),
            "page_kind": capability.page_kind,
            "access": capability.access,
            "sections": [
                {
                    "heading": get_text(ui_lang, "research.placeholder.heading"),
                    "paragraphs": [
                        get_text(ui_lang, "research.placeholder.route_ready"),
                        get_text(ui_lang, "research.placeholder.future_content"),
                    ],
                }
            ],
        }

    if page_slug == "design":
        return _deep_localize(SPANISH_DESIGN_PAGE_CONTENT, ui_lang)

    pages: dict[str, dict[str, Any]] = {
        "speakers": {
            "title": get_research_page_label("speakers", ui_lang),
            "eyebrow": f"{get_section_label('research', ui_lang)} · {title}",
            "intro": get_text(ui_lang, "research.speakers.intro"),
            "page_kind": "workbench",
            "access": "protected",
            "sections": [
                {
                    "heading": get_research_page_label("speakers", ui_lang),
                    "paragraphs": [get_text(ui_lang, "research.speakers.no_data_message")],
                },
            ],
        },
        "comparison": {
            "title": get_research_page_label("comparison", ui_lang),
            "eyebrow": f"{get_section_label('research', ui_lang)} · {title}",
            "intro": get_text(ui_lang, "research.comparison.intro"),
            "page_kind": "workbench",
            "access": "protected",
            "sections": [
                {
                    "heading": get_research_page_label("comparison", ui_lang),
                    "paragraphs": [get_text(ui_lang, "research.comparison.no_data_message")],
                },
            ],
        },
        "phenomena": {
            "title": get_research_page_label("phenomena", ui_lang),
            "eyebrow": f"{get_section_label('research', ui_lang)} · {title}",
            "intro": get_text(ui_lang, "research.phenomena.intro"),
            "page_kind": "workbench",
            "access": "protected",
            "sections": [
                {
                    "heading": get_research_page_label("phenomena", ui_lang),
                    "paragraphs": [get_text(ui_lang, "research.phenomena.overview.no_data_title")],
                },
            ],
        },
    }

    return pages.get(page_slug)


def build_teaching_language_root_page(ui_lang: str, language_slug: str) -> dict[str, Any] | None:
    return build_teaching_hub_page(ui_lang, language_slug)


def build_teaching_page(ui_lang: str, language_slug: str, page_slug: str) -> dict[str, Any] | None:
    return build_teaching_topic_page(ui_lang, language_slug, page_slug)


LEGAL_PAGES: dict[str, dict[str, Any]] = {
    "impressum": {
        "title": "Impressum",
        "eyebrow": "Rechtliches",
        "intro": "Vorläufige Platzhalterseite für Anbieterkennzeichnung und Projektverantwortung.",
        "page_kind": "reading",
        "sections": [
            {
                "heading": "Projektkontext",
                "paragraphs": [
                    "PROMAT wird als Forschungs- und Lehrplattform an der Philipps-Universität Marburg entwickelt. Endgültige Anbieterangaben werden in der produktiven Fassung ergänzt.",
                ],
            },
        ],
    },
    "privacy": {
        "title": "Datenschutz",
        "eyebrow": "Rechtliches",
        "intro": "Vorläufige Platzhalterseite für Datenschutz- und Zugriffshinweise.",
        "page_kind": "reading",
        "sections": [
            {
                "heading": "Aktueller Stand",
                "paragraphs": [
                    "Die Plattform ist strukturell auf getrennte Datenzonen vorbereitet. Finale Restricted-Logik und öffentliche Freigabeprozesse werden später sauber ergänzt.",
                ],
            },
            {
                "heading": "Cookieless Webanalyse mit GoatCounter",
                "paragraphs": [
                    "Zur aggregierten Nutzungsstatistik der öffentlichen Website kann PROMAT GoatCounter einsetzen. Die Einbindung erfolgt über die Instanz pronunciation-matters.goatcounter.com und wird nur in der produktiven Umgebung geladen.",
                    "GoatCounter arbeitet ohne Tracking-Cookies. Erfasst werden technische Abrufdaten wie aufgerufene Seite, Referrer, Bildschirmbreite und Zeitpunkt, damit die Nutzung der öffentlichen Seiten statistisch ausgewertet und die Website verbessert werden kann.",
                    "Die Analyse dient nicht dazu, einzelne Nutzerinnen oder Nutzer über mehrere Dienste hinweg wiederzuerkennen oder personenbezogene Profile für Werbung zu erstellen.",
                ],
            },
        ],
    },
}
