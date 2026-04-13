"""Structured content, labels, and route metadata for PROMAT public pages."""

from __future__ import annotations

from typing import Any

from ..i18n import DEFAULT_UI_LANGUAGE, SUPPORTED_UI_LANGUAGES, translate
from ..research_capabilities import get_research_page_capability, get_research_page_order
from ..research_sessions import load_language_sessions


LANGUAGES: tuple[dict[str, Any], ...] = (
    {
        "slug": "spanish",
        "lang_code": "es",
        "labels": {"de": "Spanisch", "en": "Spanish"},
        "corpus_lead": "Prof. Dr. Felix Tacke",
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
        "corpus_lead": "Prof. Dr. Janina Reinhardt",
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
        "corpus_lead": "Prof. Dr. Kathrin Siebold",
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
        "corpus_lead": "Prof. Dr. Rolf Kreyer",
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

RESEARCH_PAGE_ORDER: tuple[tuple[str, str], ...] = get_research_page_order()

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


def get_text(ui_lang: str, key: str, **kwargs: object) -> str:
    return translate(ui_lang, key, **kwargs)


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


def _research_learner_session_count(language_slug: str) -> int:
    return sum(1 for session in load_language_sessions(language_slug) if session.speaker_type == "learner")


def _research_learner_session_count_copy(count: int, ui_lang: str) -> str:
    if ui_lang == "de":
        if count == 0:
            return "Aktuell keine erfassten Learner-Sessions im Bestand."
        if count == 1:
            return "Aktuell 1 erfasste Learner-Session im Bestand."
        return f"Aktuell {count} erfasste Learner-Sessions im Bestand."

    if count == 0:
        return "Currently no learner sessions are available."
    if count == 1:
        return "Currently 1 learner session is available."
    return f"Currently {count} learner sessions are available."


def _research_corpus_card_copy(language_slug: str, ui_lang: str) -> str:
    base_copy = {
        "de": "Kontrolliert angelegtes Korpus zur Lernendenaussprache mit Wortliste, Satzliste und Interview als vergleichbaren Erhebungsformaten.",
        "en": "Structured learner-pronunciation corpus with wordlist, sentence-list, and interview tasks as comparable elicitation formats.",
    }
    count_copy = _research_learner_session_count_copy(_research_learner_session_count(language_slug), ui_lang)
    return f"{base_copy.get(ui_lang, base_copy['de'])} {count_copy}"


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


def _build_research_language_root_entries(
    ui_lang: str,
    language_slug: str,
    *,
    is_authenticated: bool,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for page_slug, _ in RESEARCH_PAGE_ORDER:
        capability = get_research_page_capability(page_slug)
        if capability is None:
            continue
        is_protected = capability.access == "protected"
        is_muted = is_protected and not is_authenticated
        entries.append(
            {
                "title": get_research_page_label(page_slug, ui_lang),
                "text": get_text(ui_lang, f"research.root.{page_slug}.text"),
                "href_key": f"research:{language_slug}:{page_slug}",
                "button_label": get_research_page_label(page_slug, ui_lang),
                "is_protected": is_protected,
                "is_muted": is_muted,
                "show_lock": is_muted,
            }
        )
    return entries


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
                "title": _research_corpus_card_title(language, ui_lang),
                "modifier": "pm-card--corpus-research",
                "meta": (
                    f"Projekt-Leitung: {language['corpus_lead']}"
                    if ui_lang == "de"
                    else f"Project lead: {language['corpus_lead']}"
                ),
                "text": _research_corpus_card_copy(language["slug"], ui_lang),
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
            "vorbereiteter Zugriffslogik und zweisprachiger UI."
            if ui_lang == "de"
            else "Four learner-pronunciation corpora with a shared route structure, prepared access logic, and a bilingual UI."
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
        "intro": get_text(ui_lang, "research.root.intro", corpus_title=title),
        "access_note": get_text(ui_lang, "research.root.access_note"),
        "page_kind": "reading",
        "access": "public",
        "research_entries": _build_research_language_root_entries(
            ui_lang,
            language_slug,
            is_authenticated=is_authenticated,
        ),
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

    pages: dict[str, dict[str, Any]] = {
        "design": {
            "title": "Design",
            "eyebrow": "Forschung · Spanisch",
            "intro": "Das spanische Forschungsdesign verbindet kontrollierte Elizitation, Vergleichbarkeit und lernendengerechte Materialgestaltung für die Untersuchung von Lernendenaussprache.",
            "page_kind": "reading",
            "access": "public",
            "sections": [
                {
                    "heading": "Ausgangspunkt",
                    "paragraphs": [
                        "Die spanischen Aufgaben dieses Korpus wurden entwickelt, um ein Forschungsdesign für Lernendenaussprache bereitzustellen, das systematisch, vergleichbar und zugleich für Lernende gut bearbeitbar ist.",
                        "Ausgangspunkt war die Beobachtung, dass bestehende Modelle zwar wichtige Vorarbeiten bieten, für die gezielte Untersuchung der spanischen Aussprache von Lernenden aber nur teilweise direkt übernommen werden können. Das betrifft vor allem Wortschatzschwierigkeit, inhaltliche Ablenkungen durch Lesetexte und die Frage, welche lautlichen Phänomene für Lernendenaussprache tatsächlich mehrfach und kontrolliert erhoben werden müssen. Leitend sind daher nicht Nativitätsnähe oder bloße Tradition, sondern Intelligibilität, kontrollierte Elizitation und eine für Lernende sinnvolle Materialgestaltung.",
                    ],
                },
                {
                    "heading": "Vorarbeiten und empirische Ausgangslage",
                    "paragraphs": [
                        "Ein wichtiger Zwischenschritt war das frühere Projekt MAR.ELE – Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg. In diesem kleineren Vorprojekt wurden 22 Aufnahmen mit Studierenden der Universität Marburg erstellt. MAR.ELE diente dazu, spanische Lernendenaussprache als Korpusmaterial zugänglich und empirisch auswertbar zu machen. In der praktischen Arbeit mit diesem Korpus wurden jedoch auch die Grenzen eines stark übernommenen Designs sichtbar. Gerade diese Erfahrungen waren entscheidend für die weitergehende Überarbeitung im vorliegenden Projekt.",
                        "Für MAR.ELE wurde die Wortliste des Projekts I(F)EC vollständig übernommen, um die Anschlussfähigkeit an ein etabliertes korpusphonologisches Design des Spanischen zu sichern. Das war methodisch sinnvoll, zeigte in der Arbeit mit Lernenden aber auch deutliche Probleme: Einige Items erwiesen sich als unnötige lexikalische Stolperstellen, andere Phänomene, die für Lernendenaussprache besonders aufschlussreich sind, waren nicht optimal verteilt oder nicht stark genug vertreten. Die jetzige Konzeption reagiert daher nicht aus bloßer Präferenz auf frühere Modelle, sondern auf konkrete Erfahrungen aus ihrer Anwendung.",
                    ],
                },
                {
                    "heading": "Anschluss an bestehende Forschungsdesigns",
                    "paragraphs": [
                        "Bei der Erstellung der Materialien wurde zunächst geprüft, inwiefern und wie weit sich an Forschungsdesigns empirisch arbeitender Phonologieprojekte anknüpfen lässt. Besonders wichtig war hier I(F)EC, dessen Grundprotokoll eine Wortliste, einen Lesetext, einen Discourse-Completion-Task und ein Interview umfasst. Die I(F)EC-Wortliste ist bewusst breit angelegt und zielt auf eine umfassende Erfassung regionaler Variation, phonologischer Prozesse, Wortakzentuierung und orthographischer Einflüsse. Dieses Modell war für die Entwicklung der spanischen Materialien ein zentraler Referenzpunkt, wurde aber nicht unverändert übernommen.",
                        "Die Orientierung an I(F)EC war damit wichtig, aber nicht bindend. Ziel war nicht, ein bestehendes Materialpaket zu reproduzieren, sondern ein Design zu entwickeln, das die Aussprache von Lernenden möglichst kontrolliert erhebt, ohne sie durch unnötig schwierigen Wortschatz oder unpassende Inhalte zusätzlich zu belasten. Daraus ergab sich die Grundentscheidung, bestehende Vorbilder nur dort zu übernehmen, wo sie für die vorliegende Fragestellung tatsächlich tragfähig sind.",
                    ],
                },
                {
                    "heading": "Wortliste",
                    "paragraphs": [
                        "Die spanische Wortliste orientiert sich zunächst grob an I(F)EC, wurde dann aber konsequent auf ein lernendenorientiertes Forschungsdesign hin überarbeitet. Maßgeblich waren dabei mehrere Prinzipien: lexikalische Vertrautheit vor bloßer Tradition, mehrfache Belege pro relevantem Phänomen, keine sichtbare Gruppierung nach Phänomenbereichen im Hauptteil und ein eigener Schlussblock mit Minimal- oder Pseudominimalpaaren. Damit soll die Liste einerseits systematische Analyse ermöglichen, andererseits aber für Lernende lesbar und bearbeitbar bleiben.",
                        "Die Überarbeitung reagiert auch auf ein praktisches Problem früherer Designs: Die direkte Übernahme bestehender Listen erhöht zwar oft die Vergleichbarkeit, kann aber für Lernende unnötige Stolperstellen erzeugen. Für das vorliegende Projekt wurde deshalb eine Liste zusammengestellt, die zentrale segmentale und prosodisch relevante Zielstellen mehrfach abbildet, ohne sich unnötig an lexikalisch randständige oder didaktisch wenig geeignete Items zu binden. Auf diese Weise soll nicht nur Variation dokumentiert, sondern Lernendenaussprache unter möglichst stabilen Bedingungen erhoben werden.",
                    ],
                },
                {
                    "heading": "Vom Lesetext zur Satzliste",
                    "paragraphs": [
                        "Auch bei der zweiten kontrollierten Leseaufgabe wurde geprüft, welche bestehenden Lösungen übernehmbar sind. In anderen Projekten wurden dafür traditionelle Lesetexte verwendet, etwa der vielfach eingesetzte Text El viento del norte y el sol. Solche Texte sind forschungsgeschichtlich etabliert, für Lernende aber nur begrenzt geeignet: Ihr Inhalt ist oft künstlich oder ungewöhnlich, der Wortschatz nicht durchgehend einfach, und die lautlichen Zielstellen lassen sich nur begrenzt kontrollieren. Dadurch steigt die Gefahr, dass nicht die Aussprache selbst, sondern vor allem Verstehens- und Leseschwierigkeiten das Ergebnis beeinflussen.",
                        "Bereits im Vorprojekt MAR.ELE wurde statt eines neutralen Standardtexts ein modifizierter und erweiterter Ausschnitt aus Der kleine Prinz verwendet. Dieser Text war seinerseits in bearbeiteter Form von Andrea Pešková übernommen worden, deren Forschung insbesondere im Bereich der Intonation des Spanischen wichtige Anknüpfungspunkte bietet. Gerade die Arbeit mit einem literarischen Text machte jedoch sichtbar, dass literarische Prägung, stilistische Dichte und eingeschränkte Kontrollierbarkeit der Lautkontexte für Lernende neue Probleme erzeugen. Das war ein wesentlicher Grund, im vorliegenden Projekt bewusst auf eine eigene Satzliste umzusteigen.",
                        "Die Satzliste des vorliegenden Projekts ist daher kein Ersatztext im traditionellen Sinn, sondern ein kontrolliertes Elizitationsinstrument. Sie rekombiniert die Items der Wortliste in einfachen, gut lesbaren Sätzen, ohne neue aussprachebezogene Zielphänomene einzuführen. Ziel ist es, die in der Wortliste erhobenen Muster in Lautkontexten und unter satzprosodischen Bedingungen erneut zu prüfen. Die Satzliste ist damit funktional eng an die Wortliste gebunden, aber kognitiv deutlich kontrollierbarer als ein übernommener Fließtext.",
                    ],
                },
                {
                    "heading": "Interview",
                    "paragraphs": [
                        "Das Interview ist schließlich eine projektweite Erweiterung des Designs. Es ergänzt die kontrollierten Leseaufgaben um eine reflexive Komponente: Lernende werden nicht nur aufgenommen, sondern auch zu ihrer eigenen Aussprache, zu wahrgenommenen Schwierigkeiten und zu auffälligen Phänomenen befragt, die im Verlauf der Erhebung beobachtet wurden. Damit fließt neben der Außenbeobachtung auch die Perspektive der Lernenden selbst in das Korpus ein. Für die Untersuchung von Lernendenaussprache ist das besonders wichtig, weil so nicht nur Realisierungen dokumentiert, sondern auch metasprachliche Einschätzungen und subjektive Problemwahrnehmungen sichtbar werden.",
                    ],
                },
                {
                    "heading": "Literatur",
                    "bullets": [
                        "I(F)EC: (Inter-)Fonología del Español Contemporáneo.",
                        "MAR.ELE: Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg.",
                        "Bárkányi, Zsuzsanna / Galindo Merino, M. Mar / Pérez-Bernabeu, Aarón (Hg.) (2024): La integración de la pronunciación en el aula de ELE / Integrating pronunciation in the Spanish language classroom. Amsterdam / Philadelphia: John Benjamins.",
                        "Pešková, Andrea: Archivo de los acentos en el ELE. Online: https://andrea-peskova.com/archivo-de-los-acentos-l2/",
                        "Pustka, Elissa / Gabriel, Christoph / Meisenburg, Trudel / Burkard, Monja / Dziallas, Kristina (2018): (Inter-)Fonología del Español Contemporáneo (I)FEC: Metodología de un programa de investigación para la fonología de corpus. Loquens 5(1), e046. DOI: https://doi.org/10.3989/loquens.2018.046",
                        "Tacke, Felix (2023–2024): MAR.ELE – Corpus sobre la pronunciación del español por aprendientes de ELE en Marburg. Marburg: Philipps-Universität Marburg. Online: https://marele.hispanistica.com",
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
                    "heading": "Wortliste",
                    "paragraphs": [
                        "Einzelwörter und kurze isolierte Einheiten für segmentale und prosodische Vergleiche, technisch unter wordlist vorbereitet.",
                    ],
                },
                {
                    "heading": "Text",
                    "paragraphs": [
                        "Zusammenhängende Aussprache in gelesenen oder eng geführten Satz- und Textpassagen mit dem technischen Task-Key text.",
                    ],
                },
                {
                    "heading": "Interview zur Aussprache",
                    "paragraphs": [
                        "Interview mit den Sprecher:innen zur Reflexion der Aussprache bzw. Aufzeichnung.",
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
