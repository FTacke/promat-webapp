"""Structured content, labels, and route metadata for PROMAT public pages."""

from __future__ import annotations

from typing import Any


DEFAULT_UI_LANGUAGE = "de"
SUPPORTED_UI_LANGUAGES: tuple[str, ...] = ("de",)


TEXTS: dict[str, dict[str, str]] = {
    "de": {
        "section.project": "Projekt",
        "section.research": "Forschung",
        "section.teaching": "Unterricht",
        "section.sample": "Sample",
        "section.legal": "Rechtliches",
        "nav.choose_language": "Sprache wählen",
        "nav.more": "Mehr erfahren →",
        "nav.open_section": "Bereich öffnen",
        "nav.open_corpus": "Korpus öffnen →",
        "nav.open_materials": "Materialien öffnen →",
        "nav.open_page": "Seite öffnen →",
        "project.about": "Worum es geht",
        "project.research-design": "Forschungsdesign",
        "project.data-methods": "Daten & Methodik",
        "project.team": "Team",
        "research.design": "Design",
        "research.speakers": "Sprecher:innen",
        "research.recordings": "Aufnahmen",
        "research.comparison": "Vergleich",
        "research.phenomena": "Phänomene",
        "teaching.phenomena": "Phänomene",
        "teaching.materials": "Materialien",
    },
    "en": {
        "section.project": "Project",
        "section.research": "Research",
        "section.teaching": "Teaching",
        "section.sample": "Sample",
        "section.legal": "Legal",
        "nav.choose_language": "Choose language",
        "nav.more": "Learn more →",
        "nav.open_section": "Open area",
        "nav.open_corpus": "Open corpus →",
        "nav.open_materials": "Open materials →",
        "nav.open_page": "Open page →",
        "project.about": "About",
        "project.research-design": "Research Design",
        "project.data-methods": "Data & Methods",
        "project.team": "Team",
        "research.design": "Design",
        "research.speakers": "Speakers",
        "research.recordings": "Recordings",
        "research.comparison": "Comparison",
        "research.phenomena": "Phenomena",
        "teaching.phenomena": "Phenomena",
        "teaching.materials": "Materials",
    },
}


LANGUAGES: tuple[dict[str, Any], ...] = (
    {
        "slug": "spanish",
        "lang_code": "es",
        "labels": {"de": "Spanisch", "en": "Spanish"},
        "corpus_lead": "Prof. Marín",
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
        "corpus_lead": "Prof. Delorme",
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
        "corpus_lead": "Dr. Hamid",
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
        "corpus_lead": "Prof. Reeves",
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
    ("research-design", "project.research-design"),
    ("data-methods", "project.data-methods"),
    ("team", "project.team"),
)

RESEARCH_PAGE_ORDER: tuple[tuple[str, str], ...] = (
    ("design", "research.design"),
    ("speakers", "research.speakers"),
    ("recordings", "research.recordings"),
    ("comparison", "research.comparison"),
    ("phenomena", "research.phenomena"),
)

TEACHING_PAGE_ORDER: tuple[tuple[str, str], ...] = (
    ("phenomena", "teaching.phenomena"),
    ("materials", "teaching.materials"),
)


def _localized(value: Any, ui_lang: str) -> Any:
    if isinstance(value, dict):
        return value.get(ui_lang) or value.get(DEFAULT_UI_LANGUAGE) or next(iter(value.values()))
    return value


def get_supported_ui_language(ui_lang: str) -> str | None:
    if ui_lang in SUPPORTED_UI_LANGUAGES:
        return ui_lang
    return None


def get_text(ui_lang: str, key: str) -> str:
    language_texts = TEXTS.get(ui_lang) or TEXTS[DEFAULT_UI_LANGUAGE]
    if key in language_texts:
        return language_texts[key]
    return TEXTS[DEFAULT_UI_LANGUAGE][key]


def get_section_label(section_key: str, ui_lang: str) -> str:
    return get_text(ui_lang, f"section.{section_key}")


def get_top_navigation(ui_lang: str) -> list[dict[str, str]]:
    return [
        {"key": "project", "label": get_section_label("project", ui_lang), "href_key": "project_root"},
        {"key": "research", "label": get_section_label("research", ui_lang), "href_key": "research_root"},
        {"key": "teaching", "label": get_section_label("teaching", ui_lang), "href_key": "teaching_root"},
        {"key": "sample", "label": get_section_label("sample", ui_lang), "href_key": "sample_root"},
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


def get_project_page_label(page_slug: str, ui_lang: str) -> str:
    label_key = dict(PROJECT_PAGE_ORDER)[page_slug]
    return get_text(ui_lang, label_key)


def get_research_page_label(page_slug: str, ui_lang: str) -> str:
    label_key = dict(RESEARCH_PAGE_ORDER)[page_slug]
    return get_text(ui_lang, label_key)


def get_teaching_page_label(page_slug: str, ui_lang: str) -> str:
    label_key = dict(TEACHING_PAGE_ORDER)[page_slug]
    return get_text(ui_lang, label_key)


def _research_feature_cards(language_slug: str, ui_lang: str) -> list[dict[str, str]]:
    labels = {
        "design": "Methodische Anlage und Auswahlprinzipien des Korpus.",
        "speakers": "Zugang über Personen mit reduzierten Metadaten, Filtern und späteren Player-Aktionen.",
        "recordings": "Zugang über Aufgabentypen wie isolierte Aussprache, zusammenhängende Aussprache und Interview.",
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
        "intro": (
            "Lernendenaussprache erforschen, Unterricht gestalten – in Englisch, Französisch, "
            "Spanisch und Deutsch."
        ),
        "page_kind": "landing",
        "more_link": {"label": get_text(ui_lang, "nav.more"), "href_key": "project_root"},
        "landing_cards": [
            {
                "entry_kind": "research",
                "title": "Aussprache erforschen",
                "text": "Korpora mit authentischen Sprachdaten und klar getrennten Forschungszugängen.",
                "href_key": "research_root",
                "link_label": "Zur Forschung →",
                "image_asset": "img/cards/forschung_01.png",
                "image_alt": "Forschungssituation mit Besprechung und Audioanalyse auf einem Laptop",
            },
            {
                "entry_kind": "teaching",
                "title": "Aussprache unterrichten",
                "text": "Anschauliche Materialien mit frei zugänglichen Medien und vorbereiteten Unterrichtspfaden.",
                "href_key": "teaching_root",
                "link_label": "Zum Unterricht →",
                "image_asset": "img/cards/unterricht_01.png",
                "image_alt": "Unterrichtssituation im Klassenraum als Motiv für Materialien und Hörbeispiele",
            },
        ],
        "sections": [],
    }


def build_corpus_cards_research(ui_lang: str) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for language in LANGUAGES:
        cards.append(
            {
                "title": get_language_label(language, ui_lang),
                "modifier": "pm-card--corpus-research",
                "meta": f"Projekt-Leitung: {language['corpus_lead']}",
                "text": _localized(language["summary"], ui_lang),
                "action_label": get_text(ui_lang, "nav.open_corpus"),
                "href_key": f"research:{language['slug']}",
            }
        )
    return cards


def build_corpus_cards_teaching(ui_lang: str) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for language in LANGUAGES:
        cards.append(
            {
                "title": get_language_label(language, ui_lang),
                "modifier": f"pm-card--lang-{language['lang_code']}",
                "meta": "",
                "text": _localized(language["teaching_focus"], ui_lang),
                "action_label": get_text(ui_lang, "nav.open_materials"),
                "href_key": f"teaching:{language['slug']}",
            }
        )
    return cards


def build_research_select_page(ui_lang: str) -> dict[str, Any]:
    return {
        "title": get_section_label("research", ui_lang),
        "eyebrow": get_section_label("research", ui_lang),
        "intro": (
            "Vier Sprachkorpora zur Lernendenaussprache mit einheitlicher Route-Struktur, "
            "vorbereiteter Zugriffslogik und deutschsprachiger UI."
        ),
        "page_kind": "workbench",
        "corpus_cards": build_corpus_cards_research(ui_lang),
        "sections": [],
        "is_section_root": True,
    }


def build_teaching_select_page(ui_lang: str) -> dict[str, Any]:
    return {
        "title": get_section_label("teaching", ui_lang),
        "eyebrow": get_section_label("teaching", ui_lang),
        "intro": (
            "Unterrichtsbereiche mit klarer Trennung zwischen öffentlichem Materialraum und "
            "geschütztem Forschungsdatenraum."
        ),
        "page_kind": "material",
        "corpus_cards": build_corpus_cards_teaching(ui_lang),
        "sections": [],
        "is_section_root": True,
    }


PROJECT_PAGES: dict[str, dict[str, Any]] = {
    "about": {
        "title": "Worum es geht",
        "eyebrow": "Projekt",
        "intro": "Pronunciation Matters verbindet Projektkommunikation, Forschung und Unterricht über eine gemeinsame, zukunftsfeste Plattformstruktur.",
        "page_kind": "reading",
        "sections": [
            {
                "heading": "Ausgangspunkt",
                "paragraphs": [
                    "PROMAT trennt bewusst zwischen UI-Sprache, technischer Routing-Struktur, Datenarchitektur und Dateisystem. Dadurch kann die Plattform später ohne Grundumbau um Englisch, Auth-Absicherung und weitere Korpora erweitert werden.",
                    "Der aktuelle Umbau bereitet diese Struktur vor, ohne bereits eine finale Restricted- oder Player-Architektur produktiv zu setzen.",
                ],
            },
            {
                "heading": "Strukturelle Leitlinien",
                "bullets": [
                    "Technische Slugs, Feldnamen und Controlled Vocabularies bleiben konsequent englisch.",
                    "Sichtbare UI-Beschriftungen bleiben zunächst deutsch und sind von den technischen Slugs entkoppelt.",
                    "Öffentliche Medien liegen strukturell unter /public, geschützte Forschungsdaten unter /data, Klardaten außerhalb der Webapp unter /secure.",
                ],
            },
        ],
    },
    "research-design": {
        "title": "Forschungsdesign",
        "eyebrow": "Projekt",
        "intro": "Das Projekt wird entlang stabiler Seitentypen, Sprachbereiche und klarer Datenzonen organisiert.",
        "page_kind": "reading",
        "sections": [
            {
                "heading": "Routing und Seitenlogik",
                "paragraphs": [
                    "Die Plattform nutzt ein ui-lang-prefixed Routing-Schema und trennt zwischen Projekt-, Forschungs-, Unterrichts- und Sample-Bereich. Innerhalb der Forschung folgen alle Sprachbereiche denselben englischen Seitenschlüsseln: design, speakers, recordings, comparison und phenomena.",
                    "Unterricht bleibt bewusst schlanker und führt pro Sprache zunächst nur über eine Landingpage zu phenomena und materials.",
                ],
            },
            {
                "heading": "Vorbereitete Erweiterbarkeit",
                "bullets": [
                    "Weitere UI-Sprachen können über dieselben Slugs ergänzt werden.",
                    "Weitere Korpussprachen können ohne Routenumbau aktiviert werden.",
                    "Restricted-Logik kann später auf vorbereitete research-Seiten aufsetzen, statt gegen provisorische Altstrukturen zu arbeiten.",
                ],
            },
        ],
    },
    "data-methods": {
        "title": "Daten & Methodik",
        "eyebrow": "Projekt",
        "intro": "Der Umbau trennt technische Datenzonen und benennt Metadaten, Tasks und Dateitypen konsistent auf Englisch.",
        "page_kind": "reading",
        "sections": [
            {
                "heading": "Datenzonen",
                "bullets": [
                    "/secure bleibt außerhalb der Webapp und wird nicht angebunden.",
                    "/data ist der vorbereitete Bereich für geschützte Forschungsdaten und Sessions.",
                    "/public ist der vorbereitete Bereich für frei zugängliche Unterrichts- und Sample-Medien.",
                ],
            },
            {
                "heading": "Metadatenkonventionen",
                "paragraphs": [
                    "Begriffe wie speaker_type, target_language, context, file_role und task_type werden nur noch in der englischen technischen Form verwendet. Sichtbare deutsche Labels sind davon getrennt organisiert.",
                ],
            },
        ],
    },
    "team": {
        "title": "Team",
        "eyebrow": "Projekt",
        "intro": "Die Teamseite markiert Arbeitsfelder und Verantwortungsbereiche, nicht bereits eine finale Personenmodellierung.",
        "page_kind": "reading",
        "sections": [
            {
                "heading": "Arbeitsfelder",
                "bullets": [
                    "Sprachspezifische Korpuskuratierung",
                    "Datenmodellierung, Session-Struktur und Exportpfade",
                    "UI- und Routing-Systematik für Forschung und Unterricht",
                ],
            },
        ],
    },
}


def build_research_language_root_page(ui_lang: str, language_slug: str) -> dict[str, Any] | None:
    language = get_language(language_slug)
    if language is None:
        return None

    title = get_language_label(language, ui_lang)
    if language_slug == "spanish":
        return {
            "title": title,
            "eyebrow": get_section_label("research", ui_lang),
            "intro": (
                "Das spanische Korpus dient als Referenzimplementierung für die neue PROMAT-Struktur mit "
                "sprachneutralen Slugs, vorbereiteten Zugangsseiten und klar getrennter Datenarchitektur."
            ),
            "page_kind": "reading",
            "access": "public",
            "feature_cards": _research_feature_cards(language_slug, ui_lang),
            "sections": [
                {
                    "heading": "Zugänge zum Korpus",
                    "paragraphs": [
                        "Das Korpus ist über mehrere gleichwertige Zugänge erschlossen: über Personen, Aufgabentypen, itembasierten Vergleich und Phänomene.",
                        "Die methodische Anlage bleibt öffentlich unter Design dokumentiert; datennahe Oberflächen sind strukturell vorbereitet, aber noch nicht final abgesichert.",
                    ],
                },
            ],
            "is_language_root": True,
        }

    return {
        "title": title,
        "eyebrow": get_section_label("research", ui_lang),
        "intro": f"Der Forschungsbereich für {title} ist strukturell vorbereitet und folgt bereits dem neuen Route-Schema.",
        "page_kind": "reading",
        "access": "prepared",
        "feature_cards": _research_feature_cards(language_slug, ui_lang),
        "sections": [
            {
                "heading": "Vorbereiteter Stand",
                "paragraphs": [
                    "Die Sprach-Landingpage sowie die Seiten design, speakers, recordings, comparison und phenomena sind als konsistente Platzhalter angelegt.",
                    "Fachinhalte, finale Datenbindung und spätere Restricted-Logik folgen in einem nächsten Ausbauschritt.",
                ],
            }
        ],
        "is_language_root": True,
    }


def build_research_page(ui_lang: str, language_slug: str, page_slug: str) -> dict[str, Any] | None:
    language = get_language(language_slug)
    if language is None:
        return None

    title = get_language_label(language, ui_lang)
    page_title = get_research_page_label(page_slug, ui_lang)

    if language_slug != "spanish":
        return {
            "title": page_title,
            "eyebrow": f"{get_section_label('research', ui_lang)} · {title}",
            "intro": f"Die Seite {page_title} für {title} ist strukturell angelegt, inhaltlich aber noch nicht ausgebaut.",
            "page_kind": "reading" if page_slug == "design" else "workbench",
            "access": "prepared",
            "sections": [
                {
                    "heading": "Vorbereitung statt Endausbau",
                    "paragraphs": [
                        "Die Route existiert bereits mit dem finalen englischen technischen Schlüssel.",
                        "Datenbindung, Freigabestufen und inhaltliche Kuratierung werden später sprachspezifisch ergänzt.",
                    ],
                }
            ],
        }

    pages: dict[str, dict[str, Any]] = {
        "design": {
            "title": "Design",
            "eyebrow": "Forschung · Spanisch",
            "intro": "Dokumentation der sprachspezifischen Anlage des spanischen Korpus.",
            "page_kind": "reading",
            "access": "public",
            "sections": [
                {
                    "heading": "Isolierte Aussprache (Wortliste)",
                    "paragraphs": [
                        "Die Wortliste dokumentiert segmentale und prosodische Zielstellen in klar isolierter Produktion.",
                        "Die technische Aufgabenlogik ist bereits auf den stabilen Task-Key isolated_speech vorbereitet.",
                    ],
                },
                {
                    "heading": "Zusammenhängende Aussprache (Text/Sätze)",
                    "paragraphs": [
                        "Dieser Teil erfasst Aussprache in gelesenen oder eng geführten Satz- und Textpassagen und bereitet den Task-Key connected_speech vor.",
                    ],
                },
                {
                    "heading": "Interview zur Aussprache",
                    "paragraphs": [
                        "Halbgeleitete Gesprächspassagen mit spontaner Aussprache werden als eigener Task-Typ interview geführt.",
                    ],
                },
                {
                    "heading": "Auswahlprinzipien",
                    "paragraphs": [
                        "Items, Sprecher:innenbezug und spätere Vergleichsachsen werden so dokumentiert, dass weitere Sprachkorpora dieselbe Struktur übernehmen können.",
                    ],
                },
            ],
        },
        "speakers": {
            "title": "Sprecher:innen",
            "eyebrow": "Forschung · Spanisch",
            "intro": "Zugang zu Aufnahmen über Personen mit reduzierten Metadaten und vorbereiteten Filtern.",
            "page_kind": "workbench",
            "access": "protected",
            "sections": [
                {
                    "heading": "Geplante Übersicht",
                    "paragraphs": [
                        "Die Oberfläche ist für eine card-basierte Darstellung mit ID, level, L1 und weiteren Kernmetadaten vorbereitet.",
                    ],
                },
                {
                    "heading": "Geplante Filter",
                    "bullets": [
                        "level_code",
                        "l1",
                        "speaker_type",
                        "gender",
                        "standard_variety",
                    ],
                },
                {
                    "heading": "Struktureller Stand",
                    "paragraphs": [
                        "Die Seite markiert den später geschützten Forschungszugang, setzt aber bewusst noch keine halbgare Auth- oder Player-Logik produktiv um.",
                    ],
                },
            ],
        },
        "recordings": {
            "title": "Aufnahmen",
            "eyebrow": "Forschung · Spanisch",
            "intro": "Zugang zu Daten über Aufgabentypen statt über Personen.",
            "page_kind": "workbench",
            "access": "protected",
            "sections": [
                {
                    "heading": "Isolierte Aussprache (Wortliste)",
                    "paragraphs": [
                        "Einzelwörter und kurze isolierte Einheiten für segmentale und prosodische Vergleiche, technisch unter isolated_speech vorbereitet.",
                    ],
                },
                {
                    "heading": "Zusammenhängende Aussprache (Text/Sätze)",
                    "paragraphs": [
                        "Zusammenhängende Aussprache in gelesenen oder eng geführten Satz- und Textpassagen mit dem technischen Task-Key connected_speech.",
                    ],
                },
                {
                    "heading": "Interview zur Aussprache",
                    "paragraphs": [
                        "Halbgeleitete Gesprächssituationen mit spontaner Aussprache unter dem Task-Key interview.",
                    ],
                },
            ],
        },
        "comparison": {
            "title": "Vergleich",
            "eyebrow": "Forschung · Spanisch",
            "intro": "Itembasierter Vergleich über mehrere Sprecher:innen hinweg mit späterem Inline-Audio.",
            "page_kind": "workbench",
            "access": "protected",
            "sections": [
                {
                    "heading": "Geplante Oberfläche",
                    "paragraphs": [
                        "Die Vergleichsseite ist auf eine grid- oder tabellenbasierte Darstellung vorbereitet, in der Zeilen Items und Spalten Sprecher:innen abbilden.",
                    ],
                },
            ],
        },
        "phenomena": {
            "title": "Phänomene",
            "eyebrow": "Forschung · Spanisch",
            "intro": "Linguistisch motivierter Zugang über Kategorien und Phänomene mit späterem Inline-Audio.",
            "page_kind": "workbench",
            "access": "protected",
            "sections": [
                {
                    "heading": "Hinweis zur Zuordnung",
                    "paragraphs": [
                        "Die Zuordnung von Items zu Phänomenen bleibt heuristisch und garantiert keine eindeutige Realisierung.",
                        "Die Seite ist deshalb als vorbereitete Forschungsoberfläche angelegt und noch nicht final datengetrieben ausgebaut.",
                    ],
                },
            ],
        },
    }

    return pages.get(page_slug)


def build_teaching_language_root_page(ui_lang: str, language_slug: str) -> dict[str, Any] | None:
    language = get_language(language_slug)
    if language is None:
        return None

    title = get_language_label(language, ui_lang)
    intro = (
        "Der Unterrichtsbereich führt pro Sprache bewusst nur über eine kompakte Landingpage zu Phänomenen und Materialien."
    )
    if language_slug != "spanish":
        intro = f"Der Unterrichtsbereich für {title} ist strukturell vorbereitet und folgt bereits dem reduzierten PROMAT-Minimalset."

    return {
        "title": title,
        "eyebrow": get_section_label("teaching", ui_lang),
        "intro": intro,
        "page_kind": "material",
        "feature_cards": _teaching_feature_cards(language_slug, ui_lang),
        "sections": [
            {
                "heading": "Aktueller Zuschnitt",
                "paragraphs": [
                    "Der Unterrichtsbereich bleibt absichtlich kleiner als der Forschungsbereich. So kann die spätere öffentliche Medienlogik sauber auf /public aufsetzen.",
                ],
            },
        ],
        "is_language_root": True,
    }


def build_teaching_page(ui_lang: str, language_slug: str, page_slug: str) -> dict[str, Any] | None:
    language = get_language(language_slug)
    if language is None:
        return None

    title = get_language_label(language, ui_lang)
    page_title = get_teaching_page_label(page_slug, ui_lang)

    if language_slug != "spanish":
        return {
            "title": page_title,
            "eyebrow": f"{get_section_label('teaching', ui_lang)} · {title}",
            "intro": f"Die Seite {page_title} für {title} ist als konsistenter Platzhalter vorbereitet.",
            "page_kind": "material",
            "sections": [
                {
                    "heading": "Vorbereiteter Stand",
                    "paragraphs": [
                        "Route, interne Keys und Navigationslogik sind bereits im finalen Schema angelegt.",
                        "Öffentliche Medien, didaktische Inhalte und spätere englische UI-Texte werden in nachfolgenden Ausbauschritten ergänzt.",
                    ],
                },
            ],
        }

    pages: dict[str, dict[str, Any]] = {
        "phenomena": {
            "title": "Phänomene",
            "eyebrow": "Unterricht · Spanisch",
            "intro": "Reduzierte, inhaltlich vorbereitete Seite für didaktisch relevante Aussprachephänomene im Spanischunterricht.",
            "page_kind": "material",
            "sections": [
                {
                    "heading": "Didaktischer Fokus",
                    "meta_cards": [
                        {"title": "Wahrnehmung", "text": "Phänomene, die Lernende sicher hören und unterscheiden sollen."},
                        {"title": "Produktion", "text": "Artikulations- und Prosodiemuster für angeleitete Übungsformate."},
                        {"title": "Variation", "text": "Stellen, an denen mehrere gültige Aussprachestandards sichtbar gemacht werden."},
                    ],
                },
                {
                    "heading": "Struktureller Stand",
                    "paragraphs": [
                        "Die Seite bereitet Inhalte, Labels und spätere öffentliche Medienanbindung vor, ohne bereits komplexe Audio- oder Rechte-Logik einzubauen.",
                    ],
                },
            ],
        },
        "materials": {
            "title": "Materialien",
            "eyebrow": "Unterricht · Spanisch",
            "intro": "Reduzierte, inhaltlich vorbereitete Seite für Materialien und spätere Exporte nach /public.",
            "page_kind": "material",
            "sections": [
                {
                    "heading": "Vorbereitete Formate",
                    "meta_cards": [
                        {"title": "Impulskarten", "text": "Kurze Hör- oder Leseimpulse mit klarer Beobachtungsaufgabe."},
                        {"title": "Arbeitsblätter", "text": "Sequenzen für Einzelarbeit, Partnerarbeit oder gelenktes Nachsprechen."},
                        {"title": "Transfer", "text": "Aufgaben, die Forschungserkenntnisse in Unterrichtssituationen übersetzen."},
                    ],
                },
                {
                    "heading": "Öffentlicher Medienraum",
                    "paragraphs": [
                        "Freigegebene Unterrichtsmedien werden strukturell unter /public vorbereitet und nicht direkt aus /data ausgeliefert.",
                    ],
                },
            ],
        },
    }

    return pages.get(page_slug)


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
        ],
    },
}
