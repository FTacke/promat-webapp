"""Public routes for PROMAT."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, abort, jsonify, make_response, render_template, request, url_for
from sqlalchemy import text

from ..content_navigation import build_content_header as build_shared_content_header
from ..research_views import (
    build_player_stub_page,
    build_recordings_page,
    build_speaker_profile_page,
    build_speakers_page,
)
from .public_content import (
    DEFAULT_UI_LANGUAGE,
    LEGAL_PAGES,
    PROJECT_PAGE_ORDER,
    PROJECT_PAGES,
    RESEARCH_PAGE_ORDER,
    TEACHING_PAGE_ORDER,
    build_research_language_root_page,
    build_research_page,
    build_research_select_page,
    build_start_page,
    build_teaching_language_root_page,
    build_teaching_page,
    build_teaching_select_page,
    get_canonical_language_slug,
    get_canonical_project_page_slug,
    get_canonical_research_page_slug,
    get_canonical_teaching_page_slug,
    get_language,
    get_language_label,
    get_project_page_label,
    get_research_page_label,
    get_section_label,
    get_supported_ui_language,
    get_teaching_page_label,
    get_text,
    get_top_navigation,
)

blueprint = Blueprint("public", __name__)


def _redirect(location: str):
    return make_response("", 302, {"Location": location})


def _require_ui_lang(ui_lang: str) -> str:
    resolved = get_supported_ui_language(ui_lang)
    if resolved is None:
        abort(404)
    return resolved


def _section_home_href(section_key: str, ui_lang: str) -> str | None:
    if section_key == "project":
        return url_for("public.project_home", ui_lang=ui_lang)
    if section_key == "research":
        return url_for("public.research_home", ui_lang=ui_lang)
    if section_key == "teaching":
        return url_for("public.teaching_home", ui_lang=ui_lang)
    if section_key == "sample":
        return url_for("public.sample_page", ui_lang=ui_lang)
    return None


def _build_content_header(
    page: dict[str, Any],
    panel: dict[str, Any],
    page_name: str,
    ui_lang: str,
) -> dict[str, Any]:
    return build_shared_content_header(
        page_name=page_name,
        title=page["title"],
        intro=page.get("intro"),
        section_label=panel["section_label"],
        section_href=_section_home_href(panel["section_key"], ui_lang),
        context_mode=panel["context_mode"],
        context_title=panel.get("context_title"),
        context_root_href=panel.get("context_root_href"),
        is_section_root=bool(page.get("is_section_root")),
        is_language_root=bool(page.get("is_language_root")),
        ancestors=page.get("nav_ancestors", []),
        current_label=page.get("nav_current_label"),
    )


def _resolve_href_key(href_key: str, ui_lang: str) -> str:
    if href_key == "project_root":
        return url_for("public.project_home", ui_lang=ui_lang)
    if href_key == "research_root":
        return url_for("public.research_home", ui_lang=ui_lang)
    if href_key == "teaching_root":
        return url_for("public.teaching_home", ui_lang=ui_lang)
    if href_key == "sample_root":
        return url_for("public.sample_page", ui_lang=ui_lang)
    if href_key == "login":
        return url_for("public.login", next=request.full_path or request.path)

    if ":" not in href_key:
        return href_key

    parts = href_key.split(":", 2)
    if len(parts) == 2:
        section_key, value = parts
        if section_key == "project":
            return url_for("public.project_page", ui_lang=ui_lang, page_slug=value)
        if section_key == "research":
            return url_for("public.research_language_root", ui_lang=ui_lang, language_slug=value)
        if section_key == "teaching":
            return url_for("public.teaching_language_root", ui_lang=ui_lang, language_slug=value)
        return href_key

    section_key, language_slug, page_slug = parts
    if section_key == "research":
        return url_for(
            "public.research_language_page",
            ui_lang=ui_lang,
            language_slug=language_slug,
            page_slug=page_slug,
        )
    if section_key == "teaching":
        return url_for(
            "public.teaching_language_page",
            ui_lang=ui_lang,
            language_slug=language_slug,
            page_slug=page_slug,
        )
    return href_key


def _linkify(items: list[dict[str, Any]], ui_lang: str) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    for item in items:
        enriched = dict(item)
        href_key = enriched.pop("href_key", None)
        if href_key:
            enriched["href"] = _resolve_href_key(href_key, ui_lang)
        resolved.append(enriched)
    return resolved


def _top_nav(ui_lang: str) -> list[dict[str, Any]]:
    return _linkify(get_top_navigation(ui_lang), ui_lang)


def _panel_items_for_project(ui_lang: str) -> list[dict[str, str]]:
    return [
        {
            "label": get_project_page_label(page_slug, ui_lang),
            "href": url_for("public.project_page", ui_lang=ui_lang, page_slug=page_slug),
            "page_slug": page_slug,
        }
        for page_slug, _ in PROJECT_PAGE_ORDER
    ]


def _panel_items_for_language(section_key: str, language_slug: str, ui_lang: str) -> list[dict[str, str]]:
    if section_key == "research":
        return [
            {
                "label": get_research_page_label(page_slug, ui_lang),
                "href": url_for(
                    "public.research_language_page",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    page_slug=page_slug,
                ),
                "page_slug": page_slug,
            }
            for page_slug, _ in RESEARCH_PAGE_ORDER
        ]

    return [
        {
            "label": get_teaching_page_label(page_slug, ui_lang),
            "href": url_for(
                "public.teaching_language_page",
                ui_lang=ui_lang,
                language_slug=language_slug,
                page_slug=page_slug,
            ),
            "page_slug": page_slug,
        }
        for page_slug, _ in TEACHING_PAGE_ORDER
    ]


def _panel_config(
    *,
    section_key: str,
    section_label: str,
    active_slug: str,
    language_label: str | None = None,
    context_mode: str = "section",
    context_title: str | None = None,
    context_root_href: str | None = None,
    context_back_href: str | None = None,
    context_back_label: str | None = None,
    items: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "section_key": section_key,
        "section_label": section_label,
        "language_label": language_label,
        "context_mode": context_mode,
        "context_title": context_title or language_label or section_label,
        "context_root_href": context_root_href,
        "context_back_href": context_back_href,
        "context_back_label": context_back_label,
        "active_slug": active_slug,
        "items": items,
    }


def _render_promat_page(
    *,
    page: dict[str, Any],
    panel: dict[str, Any],
    page_name: str,
    ui_lang: str,
) -> str:
    page_context = dict(page)
    layout = page_context.get("layout", "reading")
    page_context["content_header"] = page_context.get("content_header") or _build_content_header(page_context, panel, page_name, ui_lang)
    page_context["hero_links"] = _linkify(page_context.get("hero_links", []), ui_lang)
    page_context["feature_cards"] = _linkify(page_context.get("feature_cards", []), ui_lang)
    page_context["corpus_cards"] = _linkify(page_context.get("corpus_cards", []), ui_lang)
    page_context["landing_cards"] = _linkify(page_context.get("landing_cards", []), ui_lang)
    if page_context.get("more_link"):
        page_context["more_link"] = _linkify([page_context["more_link"]], ui_lang)[0]

    template_name = page_context.get("template") or "pages/promat_page.html"
    render_top_app_bar = True
    render_navigation_drawer = True
    shell_class = "app-shell--inner"
    body_class = None

    if layout == "landing":
        template_name = "pages/landing.html"
        render_top_app_bar = False
        render_navigation_drawer = False
        shell_class = "app-shell--panel-hidden app-shell--landing"
        body_class = "page-landing"

    return render_template(
        template_name,
        promat_page=page_context,
        promat_panel=panel,
        promat_top_nav_items=_top_nav(ui_lang),
        page_name=page_name,
        render_top_app_bar=render_top_app_bar,
        render_navigation_drawer=render_navigation_drawer,
        shell_class=shell_class,
        body_class=body_class,
        ui_lang=ui_lang,
    )


def _render_legal_page(page_key: str) -> str:
    ui_lang = DEFAULT_UI_LANGUAGE
    page = LEGAL_PAGES[page_key]
    panel = _panel_config(
        section_key="legal",
        section_label=get_section_label("legal", ui_lang),
        active_slug=page_key,
        items=[
            {"label": "Impressum", "href": url_for("public.impressum_page"), "page_slug": "impressum"},
            {"label": "Datenschutz", "href": url_for("public.privacy_page"), "page_slug": "privacy"},
        ],
    )
    return _render_promat_page(page=page, panel=panel, page_name="legal", ui_lang=ui_lang)


def _sample_speaker_cards(ui_lang: str) -> list[dict[str, Any]]:
    profile_label = "Profil öffnen" if ui_lang == "de" else "Open profile"
    recordings_label = "Aufzeichnungen" if ui_lang == "de" else "Recordings"
    recording_links_aria_label = "Direktlinks zu Aufzeichnungen" if ui_lang == "de" else "Direct links to recordings"
    learner_eyebrow = "Lernende" if ui_lang == "de" else "Learner"
    native_eyebrow = "Native Speaker" if ui_lang == "de" else "Native speaker"
    selected_session_label = "Ausgewählte Session" if ui_lang == "de" else "Selected session"

    return [
        {
            "person_id": "ES-L-0001",
            "eyebrow": learner_eyebrow,
            "selected_session_label": selected_session_label,
            "selected_session_id": "ES-L-0001-2027-S02",
            "meta_rows": [
                {"label": "Sessions" if ui_lang == "de" else "Sessions", "value": "2"},
                {"label": "Niveaus" if ui_lang == "de" else "Levels", "value": "A1, A2"},
                {"label": "L1", "value": "DE"},
                {"label": "Sprachaufenthalte" if ui_lang == "de" else "Stays", "value": "Teilweise" if ui_lang == "de" else "Partial"},
                {"label": "Aufnahmejahre" if ui_lang == "de" else "Recording years", "value": "2026–2027"},
            ],
            "profile_href": "#sample-research-profile-title",
            "profile_label": profile_label,
            "recordings_label": recordings_label,
            "recording_links_aria_label": recording_links_aria_label,
            "task_links": [
                {"label": "Wortliste" if ui_lang == "de" else "Wordlist", "href": "#sample-research-task-panels-title"},
                {"label": "Text", "href": "#sample-research-task-panels-title"},
                {"label": "Interview", "href": "#sample-research-task-panels-title"},
            ],
            "accent_modifier": "b1",
        },
        {
            "person_id": "ES-N-0001",
            "eyebrow": native_eyebrow,
            "selected_session_label": selected_session_label,
            "selected_session_id": "ES-N-0001-2026-S01",
            "meta_rows": [
                {"label": "Standardvarietät" if ui_lang == "de" else "Standard variety", "value": "ES_STD"},
                {"label": "Herkunftsland" if ui_lang == "de" else "Origin country", "value": "Spain"},
                {"label": "Herkunftsregion" if ui_lang == "de" else "Origin region", "value": "Andalusia"},
                {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": "männlich" if ui_lang == "de" else "male"},
                {"label": "Aufnahmejahr" if ui_lang == "de" else "Recording year", "value": "2026"},
            ],
            "profile_href": "#sample-research-profile-title",
            "profile_label": profile_label,
            "recordings_label": recordings_label,
            "recording_links_aria_label": recording_links_aria_label,
            "task_links": [
                {"label": "Wortliste" if ui_lang == "de" else "Wordlist", "href": "#sample-research-task-panels-title"},
                {"label": "Text", "href": "#sample-research-task-panels-title"},
            ],
            "accent_modifier": "native",
        },
    ]


@blueprint.get("/")
def landing_page():
    return _redirect(url_for("public.localized_landing_page", ui_lang=DEFAULT_UI_LANGUAGE))


@blueprint.get("/<ui_lang>")
def localized_landing_page(ui_lang: str):
    ui_lang = _require_ui_lang(ui_lang)
    panel = _panel_config(
        section_key="project",
        section_label=get_section_label("project", ui_lang),
        active_slug="start",
        context_mode="none",
        items=[],
    )
    return _render_promat_page(page=build_start_page(ui_lang), panel=panel, page_name="start", ui_lang=ui_lang)


@blueprint.get("/<ui_lang>/sample")
def sample_page(ui_lang: str):
    ui_lang = _require_ui_lang(ui_lang)
    landing_page = build_start_page(ui_lang)
    research_select_page = build_research_select_page(ui_lang)
    teaching_select_page = build_teaching_select_page(ui_lang)
    research_feature_page = build_research_language_root_page(ui_lang, "french") or {}
    teaching_feature_page = build_teaching_language_root_page(ui_lang, "spanish") or {}
    page = {
        "title": "Sample",
        "template": "pages/sample_page.html",
        "intro": (
            "Visueller Prüfstand für die aktuell produktiv genutzten Layout-Elemente. Sample folgt "
            "den realen Seiten und dient nicht als eigenständiges Vorbild."
        ),
        "is_section_root": True,
        "sample_landing_cards": _linkify(landing_page.get("landing_cards", []), ui_lang),
        "sample_research_cards": _linkify(research_select_page.get("corpus_cards", []), ui_lang),
        "sample_teaching_cards": _linkify(teaching_select_page.get("corpus_cards", []), ui_lang),
        "sample_research_feature_cards": _linkify(research_feature_page.get("feature_cards", []), ui_lang),
        "sample_teaching_feature_cards": _linkify(teaching_feature_page.get("feature_cards", []), ui_lang),
        "sample_speaker_cards": _sample_speaker_cards(ui_lang),
    }
    panel = _panel_config(
        section_key="sample",
        section_label=get_section_label("sample", ui_lang),
        active_slug="sample",
        context_mode="none",
        items=[
            {
                "label": get_section_label("sample", ui_lang),
                "href": url_for("public.sample_page", ui_lang=ui_lang),
                "page_slug": "sample",
            }
        ],
    )
    page["content_header"] = _build_content_header(page, panel, "sample", ui_lang)
    return _render_promat_page(page=page, panel=panel, page_name="sample", ui_lang=ui_lang)


@blueprint.get("/login", endpoint="login")
def login_page():
    next_url = request.args.get("next") or ""
    response = make_response(
        render_template(
            "auth/login.html",
            next=next_url,
            page_name="login",
            shell_class="app-shell--panel-hidden",
            ui_lang=DEFAULT_UI_LANGUAGE,
        )
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Vary"] = "Cookie"
    return response, 200


@blueprint.get("/health")
def health_check():
    from ..extensions.sqlalchemy_ext import get_engine

    checks = {"flask": {"ok": True}, "auth_db": {"ok": False, "error": None}}
    try:
        engine = get_engine()
        if engine is None:
            raise RuntimeError("Auth engine not initialized")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["auth_db"] = {"ok": True, "error": None}
        return jsonify({"status": "healthy", "service": "promat-web", "checks": checks}), 200
    except Exception as exc:  # noqa: BLE001
        checks["auth_db"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        return jsonify({"status": "unhealthy", "service": "promat-web", "checks": checks}), 503


@blueprint.get("/<ui_lang>/project")
def project_home(ui_lang: str):
    ui_lang = _require_ui_lang(ui_lang)
    first_page_slug = PROJECT_PAGE_ORDER[0][0]
    page = dict(PROJECT_PAGES[first_page_slug])
    page["is_section_root"] = True
    panel = _panel_config(
        section_key="project",
        section_label=get_section_label("project", ui_lang),
        active_slug=first_page_slug,
        context_mode="section",
        items=_panel_items_for_project(ui_lang),
    )
    return _render_promat_page(page=page, panel=panel, page_name="project", ui_lang=ui_lang)


@blueprint.get("/<ui_lang>/project/<page_slug>")
def project_page(ui_lang: str, page_slug: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_page_slug = get_canonical_project_page_slug(page_slug)
    if canonical_page_slug is None:
        abort(404)

    page = PROJECT_PAGES.get(canonical_page_slug)
    if page is None:
        abort(404)
    panel = _panel_config(
        section_key="project",
        section_label=get_section_label("project", ui_lang),
        active_slug=canonical_page_slug,
        context_mode="section",
        items=_panel_items_for_project(ui_lang),
    )
    return _render_promat_page(page=page, panel=panel, page_name="project", ui_lang=ui_lang)


@blueprint.get("/<ui_lang>/research")
def research_home(ui_lang: str):
    ui_lang = _require_ui_lang(ui_lang)
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug="language-selection",
        context_mode="none",
        items=[
            {
                "label": get_text(ui_lang, "nav.choose_corpus"),
                "href": url_for("public.research_home", ui_lang=ui_lang),
                "page_slug": "language-selection",
            }
        ],
    )
    return _render_promat_page(
        page=build_research_select_page(ui_lang),
        panel=panel,
        page_name="research",
        ui_lang=ui_lang,
    )


@blueprint.get("/<ui_lang>/research/<language_slug>")
def research_language_root(ui_lang: str, language_slug: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    language = get_language(canonical_language_slug)
    page = build_research_language_root_page(ui_lang, canonical_language_slug)
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug="",
        language_label=language_label,
        context_mode="language",
        context_title=language_label,
        context_root_href=url_for(
            "public.research_language_root",
            ui_lang=ui_lang,
            language_slug=canonical_language_slug,
        ),
        context_back_href=url_for("public.research_home", ui_lang=ui_lang),
        context_back_label=get_text(ui_lang, "nav.back_to_corpus_selection"),
        items=_panel_items_for_language("research", canonical_language_slug, ui_lang),
    )
    return _render_promat_page(page=page, panel=panel, page_name="research", ui_lang=ui_lang)


@blueprint.get("/<ui_lang>/research/<language_slug>/<page_slug>")
def research_language_page(ui_lang: str, language_slug: str, page_slug: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    canonical_page_slug = get_canonical_research_page_slug(page_slug)
    if canonical_language_slug is None or canonical_page_slug is None:
        abort(404)

    language = get_language(canonical_language_slug)
    if canonical_language_slug == "spanish" and canonical_page_slug == "recordings":
        page = build_recordings_page(ui_lang, canonical_language_slug, request.args)
    elif canonical_language_slug == "spanish" and canonical_page_slug == "speakers":
        page = build_speakers_page(ui_lang, canonical_language_slug, request.args)
    else:
        page = build_research_page(ui_lang, canonical_language_slug, canonical_page_slug)
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug=canonical_page_slug,
        language_label=language_label,
        context_mode="language",
        context_title=language_label,
        context_root_href=url_for(
            "public.research_language_root",
            ui_lang=ui_lang,
            language_slug=canonical_language_slug,
        ),
        context_back_href=url_for("public.research_home", ui_lang=ui_lang),
        context_back_label=get_text(ui_lang, "nav.back_to_corpus_selection"),
        items=_panel_items_for_language("research", canonical_language_slug, ui_lang),
    )
    return _render_promat_page(page=page, panel=panel, page_name="research", ui_lang=ui_lang)


@blueprint.get("/<ui_lang>/research/<language_slug>/speakers/<person_id>")
def research_speaker_profile(ui_lang: str, language_slug: str, person_id: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    language = get_language(canonical_language_slug)
    page = build_speaker_profile_page(ui_lang, canonical_language_slug, person_id, request.args.get("session"))
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug="speakers",
        language_label=language_label,
        context_mode="language",
        context_title=language_label,
        context_root_href=url_for(
            "public.research_language_root",
            ui_lang=ui_lang,
            language_slug=canonical_language_slug,
        ),
        context_back_href=url_for("public.research_home", ui_lang=ui_lang),
        context_back_label=get_text(ui_lang, "nav.back_to_corpus_selection"),
        items=_panel_items_for_language("research", canonical_language_slug, ui_lang),
    )
    return _render_promat_page(page=page, panel=panel, page_name="research", ui_lang=ui_lang)


@blueprint.get("/<ui_lang>/research/<language_slug>/player/<session_id>/<task>")
def research_player_stub(ui_lang: str, language_slug: str, session_id: str, task: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    language = get_language(canonical_language_slug)
    source = request.args.get("source")
    page = build_player_stub_page(ui_lang, canonical_language_slug, session_id, task, source)
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    active_slug = "recordings" if source == "recordings" else "speakers" if source in {"speakers", "profile"} else ""
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug=active_slug,
        language_label=language_label,
        context_mode="language",
        context_title=language_label,
        context_root_href=url_for(
            "public.research_language_root",
            ui_lang=ui_lang,
            language_slug=canonical_language_slug,
        ),
        context_back_href=url_for("public.research_home", ui_lang=ui_lang),
        context_back_label=get_text(ui_lang, "nav.back_to_corpus_selection"),
        items=_panel_items_for_language("research", canonical_language_slug, ui_lang),
    )
    return _render_promat_page(page=page, panel=panel, page_name="research", ui_lang=ui_lang)


@blueprint.get("/<ui_lang>/teaching")
def teaching_home(ui_lang: str):
    ui_lang = _require_ui_lang(ui_lang)
    panel = _panel_config(
        section_key="teaching",
        section_label=get_section_label("teaching", ui_lang),
        active_slug="language-selection",
        context_mode="section",
        items=[
            {
                "label": get_text(ui_lang, "nav.choose_language"),
                "href": url_for("public.teaching_home", ui_lang=ui_lang),
                "page_slug": "language-selection",
            }
        ],
    )
    return _render_promat_page(
        page=build_teaching_select_page(ui_lang),
        panel=panel,
        page_name="teaching",
        ui_lang=ui_lang,
    )


@blueprint.get("/<ui_lang>/teaching/<language_slug>")
def teaching_language_root(ui_lang: str, language_slug: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    language = get_language(canonical_language_slug)
    page = build_teaching_language_root_page(ui_lang, canonical_language_slug)
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    panel = _panel_config(
        section_key="teaching",
        section_label=get_section_label("teaching", ui_lang),
        active_slug="",
        language_label=language_label,
        context_mode="language",
        context_title=language_label,
        context_root_href=url_for(
            "public.teaching_language_root",
            ui_lang=ui_lang,
            language_slug=canonical_language_slug,
        ),
        context_back_href=url_for("public.teaching_home", ui_lang=ui_lang),
        context_back_label=get_text(ui_lang, "nav.back_to_language_selection"),
        items=_panel_items_for_language("teaching", canonical_language_slug, ui_lang),
    )
    return _render_promat_page(page=page, panel=panel, page_name="teaching", ui_lang=ui_lang)


@blueprint.get("/<ui_lang>/teaching/<language_slug>/<page_slug>")
def teaching_language_page(ui_lang: str, language_slug: str, page_slug: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    canonical_page_slug = get_canonical_teaching_page_slug(page_slug)
    if canonical_language_slug is None or canonical_page_slug is None:
        abort(404)

    language = get_language(canonical_language_slug)
    page = build_teaching_page(ui_lang, canonical_language_slug, canonical_page_slug)
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    panel = _panel_config(
        section_key="teaching",
        section_label=get_section_label("teaching", ui_lang),
        active_slug=canonical_page_slug,
        language_label=language_label,
        context_mode="language",
        context_title=language_label,
        context_root_href=url_for(
            "public.teaching_language_root",
            ui_lang=ui_lang,
            language_slug=canonical_language_slug,
        ),
        context_back_href=url_for("public.teaching_home", ui_lang=ui_lang),
        context_back_label=get_text(ui_lang, "nav.back_to_language_selection"),
        items=_panel_items_for_language("teaching", canonical_language_slug, ui_lang),
    )
    return _render_promat_page(page=page, panel=panel, page_name="teaching", ui_lang=ui_lang)


@blueprint.get("/impressum")
def impressum_page():
    return _render_legal_page("impressum")


@blueprint.get("/datenschutz")
@blueprint.get("/privacy")
def privacy_page():
    return _render_legal_page("privacy")
