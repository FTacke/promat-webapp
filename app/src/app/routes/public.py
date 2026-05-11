"""Public routes for PROMAT."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import re
from urllib.parse import unquote, urlparse

from flask import Blueprint, abort, flash, g, jsonify, make_response, redirect, render_template, request, send_file, url_for
from sqlalchemy import text

from ..auth import Role
from ..auth import services as auth_services
from ..content_navigation import build_content_header as build_shared_content_header
from ..i18n import PREFERRED_UI_LANGUAGE_COOKIE_NAME, resolve_request_ui_language, resolve_ui_language
from ..research_capabilities import get_research_page_surface_mode
from ..research_access import requires_research_auth
from ..research_phenomena_views import (
    build_phenomena_overview_page,
    build_phenomena_preset_editor_page,
    build_phenomena_set_editor_page,
)
from ..research_views import (
    build_comparison_page,
    build_player_page,
    build_speaker_profile_page,
    build_speakers_page,
    resolve_player_audio_artifact,
    resolve_player_item_download,
)
from ..runtime_paths import get_public_root
from ..teaching_content import resolve_teaching_switch_path, resolve_topic_route_target
from .public_content import (
    DEFAULT_UI_LANGUAGE,
    LEGAL_PAGES,
    LEGACY_PROJECT_PAGE_REDIRECTS,
    PROJECT_PAGE_ORDER,
    RESEARCH_PAGE_ORDER,
    build_project_page,
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
    get_language,
    get_language_label,
    get_research_corpus_title,
    get_project_page_label,
    get_research_page_label,
    get_section_label,
    get_supported_ui_language,
    get_text,
    get_top_navigation,
)

blueprint = Blueprint("public", __name__)


_ACCESS_REQUEST_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_ACCESS_REQUEST_MAX_LENGTHS = {
    "first_name": 160,
    "last_name": 160,
    "institution": 255,
    "role_or_function": 255,
    "email": 255,
    "purpose": 4000,
}


def _redirect(location: str):
    return make_response("", 302, {"Location": location})


def _no_store_response(response, *, status_code: int = 200):
    response.status_code = status_code
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Vary"] = "Cookie"
    return response


def _request_next_value() -> str:
    next_value = request.full_path or request.path
    if next_value.endswith("?"):
        return next_value[:-1]
    return next_value


def _safe_next_value(raw: str | None) -> str | None:
    if not raw:
        return None
    parsed = urlparse(unquote(raw))
    if parsed.netloc and parsed.netloc != request.host:
        return None
    if parsed.path.startswith(("/auth/login", "/auth/logout", "/login", "/access-request")):
        return None
    safe = parsed.path or ""
    if parsed.query:
        safe += f"?{parsed.query}"
    return safe or None


def _research_login_redirect():
    return _redirect(url_for("public.login", next=_request_next_value()))


def _default_public_auth_target(ui_lang: str) -> str:
    if getattr(g, "role", None) == Role.ADMIN:
        return url_for("admin.users_page", ui_lang=ui_lang)
    return url_for("auth.account_page", ui_lang=ui_lang)


def _redirect_authenticated_public_auth(*, next_url: str, ui_lang: str):
    return redirect(next_url or _default_public_auth_target(ui_lang), 303)


def _build_access_request_href(ui_lang: str, next_url: str | None = None) -> str:
    if next_url:
        return url_for("public.access_request_page", next=next_url)
    return url_for("public.access_request_page", ui_lang=ui_lang)


def _build_login_href(ui_lang: str, next_url: str | None = None) -> str:
    if next_url:
        return url_for("public.login", next=next_url)
    return url_for("public.login", ui_lang=ui_lang)


def _empty_access_request_form() -> dict[str, Any]:
    return {
        "first_name": "",
        "last_name": "",
        "institution": "",
        "role_or_function": "",
        "email": "",
        "purpose": "",
        "consent_confirmed": False,
    }


def _coerce_access_request_form(form_data) -> dict[str, Any]:
    values = _empty_access_request_form()
    if not form_data:
        return values
    values.update(
        {
            "first_name": str(form_data.get("first_name") or "").strip(),
            "last_name": str(form_data.get("last_name") or "").strip(),
            "institution": str(form_data.get("institution") or "").strip(),
            "role_or_function": str(form_data.get("role_or_function") or "").strip(),
            "email": auth_services.normalize_email(str(form_data.get("email") or "")),
            "purpose": str(form_data.get("purpose") or "").strip(),
            "consent_confirmed": str(form_data.get("consent_confirmed") or "") in {"1", "true", "on", "yes"},
        }
    )
    return values


def _validate_access_request_form(ui_lang: str, values: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    required_keys = {
        "first_name": "auth.access_request.error.first_name_required",
        "last_name": "auth.access_request.error.last_name_required",
        "institution": "auth.access_request.error.institution_required",
        "role_or_function": "auth.access_request.error.role_required",
        "email": "auth.access_request.error.email_required",
        "purpose": "auth.access_request.error.purpose_required",
    }
    for field_name, key in required_keys.items():
        if not values.get(field_name):
            errors[field_name] = get_text(ui_lang, key)

    email = str(values.get("email") or "")
    if email and not _ACCESS_REQUEST_EMAIL_PATTERN.match(email):
        errors["email"] = get_text(ui_lang, "auth.access_request.error.email_invalid")

    for field_name, max_length in _ACCESS_REQUEST_MAX_LENGTHS.items():
        field_value = str(values.get(field_name) or "")
        if len(field_value) > max_length:
            errors[field_name] = get_text(ui_lang, "auth.access_request.error.too_long")

    if not values.get("consent_confirmed"):
        errors["consent_confirmed"] = get_text(ui_lang, "auth.access_request.error.confirmation_required")

    return errors


def _render_access_request_page(*, next_url: str, form_values: dict[str, Any] | None = None, form_errors: dict[str, str] | None = None, status_code: int = 200):
    ui_lang = _resolve_auth_ui_lang(next_url)
    response = make_response(
        render_template(
            "auth/access_request.html",
            next=next_url,
            login_href=_build_login_href(ui_lang, next_url),
            access_request_form=_coerce_access_request_form(form_values),
            access_request_errors=form_errors or {},
            auth_ui_lang=ui_lang,
            page_name="access-request",
            shell_class="app-shell--panel-hidden",
            ui_lang=ui_lang,
        )
    )
    return _no_store_response(response, status_code=status_code)


def _resolve_auth_ui_lang(next_value: str | None = None) -> str:
    return resolve_request_ui_language(
        explicit_ui_lang=request.values.get("lang") or request.values.get("ui_lang"),
        stored_ui_lang=request.cookies.get(PREFERRED_UI_LANGUAGE_COOKIE_NAME),
        next_candidates=(next_value, request.referrer, request.path),
        accept_language=request.headers.get("Accept-Language"),
    )


def _require_research_route_access(*, page_slug: str | None = None, detail_route: str | None = None):
    if not requires_research_auth(page_slug=page_slug, detail_route=detail_route):
        return None
    if getattr(g, "user_id", None):
        return None
    return _research_login_redirect()


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
        return url_for("public.login", next=_request_next_value())
    if href_key == "access_request":
        return url_for("public.access_request_page", next=_request_next_value())

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
        is_authenticated = getattr(g, "user_id", None) is not None
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
                "is_protected": requires_research_auth(page_slug=page_slug),
                "is_muted": requires_research_auth(page_slug=page_slug) and not is_authenticated,
                "show_lock": requires_research_auth(page_slug=page_slug) and not is_authenticated,
            }
            for page_slug, _ in RESEARCH_PAGE_ORDER
        ]

    return []


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
    resolved_context_title = context_title or language_label or section_label
    mobile_context_title = resolved_context_title if context_mode == "language" and resolved_context_title else section_label
    active_primary_label = section_label
    show_mobile_context_title = bool(
        mobile_context_title
        and active_primary_label
        and mobile_context_title.strip() != active_primary_label.strip()
    )
    return {
        "section_key": section_key,
        "section_label": section_label,
        "language_label": language_label,
        "context_mode": context_mode,
        "context_title": resolved_context_title,
        "active_primary_label": active_primary_label,
        "mobile_context_title": mobile_context_title,
        "show_mobile_context_title": show_mobile_context_title,
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
    page_context["action_links"] = _linkify(page_context.get("action_links", []), ui_lang)
    page_context["research_entries"] = _linkify(page_context.get("research_entries", []), ui_lang)
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
    elif layout == "teaching":
        render_navigation_drawer = False
        shell_class = "app-shell--inner app-shell--panel-hidden"
        body_class = "page-teaching"

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


def _sample_action_button(
    label: str,
    *,
    variant: str = "secondary",
    size: str = "medium",
    href: str | None = None,
    leading_icon: str | None = None,
    trailing_icon: str | None = None,
    trailing_arrow: bool = False,
    disabled: bool = False,
    full_width: bool = False,
) -> dict[str, Any]:
    return {
        "component": "action_button",
        "label": label,
        "variant": variant,
        "size": size,
        "href": href,
        "leading_icon": leading_icon,
        "trailing_icon": trailing_icon,
        "trailing_arrow": trailing_arrow,
        "disabled": disabled,
        "full_width": full_width,
    }


def _sample_nav_pill(label: str, *, size: str = "medium", href: str | None = None, disabled: bool = False) -> dict[str, Any]:
    return {
        "component": "nav_pill",
        "label": label,
        "size": size,
        "href": href,
        "disabled": disabled,
    }


def _sample_cta_link(label: str, *, tone: str = "primary", href: str | None = None, disabled: bool = False) -> dict[str, Any]:
    return {
        "component": "cta_link",
        "label": label,
        "tone": tone,
        "href": href,
        "disabled": disabled,
    }


def _sample_chip(label: str, *, active: bool = False) -> dict[str, Any]:
    return {
        "component": "chip",
        "label": label,
        "active": active,
    }


_SAMPLE_ADMONITION_VARIANTS: dict[str, dict[str, str]] = {
    "hoermal": {"title_key": "sample.admonitions.item.hoermal.title"},
    "regel": {"title_key": "sample.admonitions.item.regel.title"},
    "tip": {"title_key": "sample.admonitions.item.tip.title"},
    "praxis": {"title_key": "sample.admonitions.item.praxis.title"},
    "context": {"title_key": "sample.admonitions.item.context.title"},
    "cite": {"title_key": "sample.admonitions.item.cite.title"},
    "summary": {"title_key": "sample.admonitions.item.summary.title"},
    "weiterlesen": {"title_key": "sample.admonitions.item.weiterlesen.title"},
}


def _sample_admonition(
    ui_lang: str,
    variant: str,
    *body_keys: str,
    item_id: str | None = None,
    title_key: str | None = None,
    collapsible: bool = False,
    default_open: bool = False,
    footer_key: str | None = None,
    tag: str = "aside",
) -> dict[str, Any]:
    variant_config = _SAMPLE_ADMONITION_VARIANTS[variant]
    return {
        "id": item_id or f"sample-admonition-{variant}",
        "tag": tag,
        "variant": variant,
        "title": get_text(ui_lang, title_key) if title_key else None,
        "default_title": get_text(ui_lang, variant_config["title_key"]),
        "collapsible": collapsible,
        "default_open": default_open,
        "body_paragraphs": [get_text(ui_lang, key) for key in body_keys],
        "footer": get_text(ui_lang, footer_key) if footer_key else None,
    }


def _sample_admonitions(ui_lang: str) -> list[dict[str, Any]]:
    return [
        _sample_admonition(
            ui_lang,
            "hoermal",
            "sample.admonitions.item.hoermal.body",
            footer_key="sample.admonitions.item.hoermal.footer",
            collapsible=True,
            default_open=True,
        ),
        _sample_admonition(ui_lang, "regel", "sample.admonitions.item.regel.body"),
        _sample_admonition(ui_lang, "tip", "sample.admonitions.item.tip.body"),
        _sample_admonition(ui_lang, "praxis", "sample.admonitions.item.praxis.body"),
        _sample_admonition(ui_lang, "context", "sample.admonitions.item.context.body"),
        _sample_admonition(ui_lang, "cite", "sample.admonitions.item.cite.body"),
        _sample_admonition(ui_lang, "summary", "sample.admonitions.item.summary.body"),
        _sample_admonition(
            ui_lang,
            "weiterlesen",
            "sample.admonitions.item.weiterlesen.body",
            collapsible=True,
            default_open=False,
        ),
    ]


def _sample_interaction_preview(ui_lang: str) -> dict[str, Any]:
    login_href = url_for("public.login", ui_lang=ui_lang)
    access_request_href = url_for("public.access_request_page", ui_lang=ui_lang)
    profile_href = "#sample-research-profile-title"
    task_href = "#sample-research-task-panels-title"
    corpus_href = url_for("public.research_language_root", ui_lang=ui_lang, language_slug="spanish")
    materials_href = url_for("public.teaching_language_root", ui_lang=ui_lang, language_slug="spanish")

    return {
        "title": get_text(ui_lang, "sample.interaction_preview.title"),
        "intro": get_text(ui_lang, "sample.interaction_preview.intro"),
        "groups": [
            {
                "id": "sample-interaction-preview-actions",
                "title": get_text(ui_lang, "sample.interaction_preview.groups.actions.title"),
                "note": get_text(ui_lang, "sample.interaction_preview.groups.actions.note"),
                "rows": [
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.large"),
                        "class_name": "pm-interaction-row pm-interaction-row--wrap",
                        "items": [
                            _sample_action_button(get_text(ui_lang, "auth.login.submit"), variant="primary", size="large", leading_icon="login"),
                        ],
                    },
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.medium"),
                        "class_name": "pm-interaction-row pm-interaction-row--wrap",
                        "items": [
                            _sample_action_button(get_text(ui_lang, "auth.login.submit"), variant="primary", size="medium", leading_icon="login"),
                            _sample_action_button(get_text(ui_lang, "auth.login.forgot_password"), variant="secondary", size="medium"),
                            _sample_action_button(get_text(ui_lang, "sample.button_preview.label.apply_filters"), variant="primary", size="medium"),
                            _sample_action_button(get_text(ui_lang, "sample.button_preview.label.reset_filters"), variant="secondary", size="medium"),
                            _sample_action_button(get_text(ui_lang, "auth.admin_users.refresh"), variant="secondary", size="medium", leading_icon="refresh"),
                            _sample_action_button(get_text(ui_lang, "auth.admin_users.create_button"), variant="primary", size="medium", leading_icon="add"),
                            _sample_action_button(get_text(ui_lang, "sample.interaction_preview.label.compare"), variant="secondary", size="medium", leading_icon="add"),
                            _sample_action_button(get_text(ui_lang, "sample.interaction_preview.label.modify"), variant="secondary", size="medium"),
                        ],
                    },
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.small"),
                        "class_name": "pm-interaction-row pm-interaction-row--wrap",
                        "items": [
                            _sample_action_button(get_text(ui_lang, "sample.interaction_preview.label.compare"), variant="secondary", size="small", leading_icon="add"),
                            _sample_action_button(get_text(ui_lang, "sample.interaction_preview.label.modify"), variant="secondary", size="small"),
                            _sample_action_button(get_text(ui_lang, "auth.login.forgot_password"), variant="tertiary", size="small"),
                        ],
                    },
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.disabled"),
                        "class_name": "pm-interaction-row pm-interaction-row--wrap",
                        "items": [
                            _sample_action_button(get_text(ui_lang, "auth.login.submit"), variant="primary", size="medium", leading_icon="login", disabled=True),
                            _sample_action_button(get_text(ui_lang, "auth.admin_users.refresh"), variant="secondary", size="medium", leading_icon="refresh", disabled=True),
                            _sample_action_button(get_text(ui_lang, "sample.interaction_preview.label.modify"), variant="tertiary", size="small", disabled=True),
                        ],
                    },
                ],
            },
            {
                "id": "sample-interaction-preview-navigation",
                "title": get_text(ui_lang, "sample.interaction_preview.groups.navigation.title"),
                "note": get_text(ui_lang, "sample.interaction_preview.groups.navigation.note"),
                "rows": [
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.medium"),
                        "class_name": "pm-interaction-row pm-interaction-row--wrap",
                        "items": [
                            _sample_nav_pill(get_text(ui_lang, "sample.button_preview.label.go_to_login"), size="medium", href=login_href),
                            _sample_nav_pill(get_text(ui_lang, "sample.interaction_preview.label.to_request_form"), size="medium", href=access_request_href),
                            _sample_nav_pill(get_text(ui_lang, "sample.interaction_preview.label.learn_more"), size="medium", href="#sample-entry-cards-title"),
                        ],
                    },
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.small"),
                        "class_name": "pm-interaction-row pm-interaction-row--card",
                        "items": [
                            _sample_nav_pill(get_text(ui_lang, "sample.interaction_preview.label.open_corpus"), size="small", href=corpus_href),
                            _sample_nav_pill(get_text(ui_lang, "sample.button_preview.label.profile"), size="small", href=profile_href),
                            _sample_nav_pill(get_text(ui_lang, "sample.button_preview.label.wordlist"), size="small", href=task_href),
                            _sample_nav_pill(get_text(ui_lang, "sample.button_preview.label.text"), size="small", href=task_href),
                            _sample_nav_pill("Interview", size="small", href=task_href),
                        ],
                    },
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.disabled"),
                        "class_name": "pm-interaction-row pm-interaction-row--wrap",
                        "items": [
                            _sample_nav_pill(get_text(ui_lang, "sample.button_preview.label.go_to_login"), size="medium", disabled=True),
                            _sample_nav_pill(get_text(ui_lang, "sample.interaction_preview.label.open_corpus"), size="small", disabled=True),
                        ],
                    },
                ],
            },
            {
                "id": "sample-interaction-preview-cta",
                "title": get_text(ui_lang, "sample.interaction_preview.groups.cta.title"),
                "note": get_text(ui_lang, "sample.interaction_preview.groups.cta.note"),
                "rows": [
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.standard"),
                        "class_name": "pm-cta-link-row",
                        "items": [
                            _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.to_research"), tone="primary", href="#sample-entry-cards-title"),
                            _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.open_corpus"), tone="primary", href=corpus_href),
                            _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.open_materials"), tone="primary", href=materials_href),
                        ],
                    },
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.accent"),
                        "class_name": "pm-cta-link-row",
                        "items": [
                            _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.to_teaching"), tone="accent", href="#sample-entry-cards-title"),
                        ],
                    },
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.disabled"),
                        "class_name": "pm-cta-link-row",
                        "items": [
                            _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.open_corpus"), tone="primary", disabled=True),
                        ],
                    },
                ],
            },
            {
                "id": "sample-interaction-preview-chips",
                "title": get_text(ui_lang, "sample.interaction_preview.groups.chips.title"),
                "note": get_text(ui_lang, "sample.interaction_preview.groups.chips.note"),
                "rows": [
                    {
                        "label": get_text(ui_lang, "sample.interaction_preview.row.selection"),
                        "class_name": "pm-interaction-row pm-interaction-row--wrap",
                        "items": [
                            _sample_chip(get_text(ui_lang, "sample.interaction_preview.label.all"), active=True),
                            _sample_chip(get_text(ui_lang, "sample.interaction_preview.label.learners")),
                            _sample_chip(get_text(ui_lang, "sample.interaction_preview.label.native_speakers")),
                            _sample_chip("B2"),
                            _sample_chip("L1 DE"),
                        ],
                    },
                ],
            },
        ],
        "contexts": {
            "title": get_text(ui_lang, "sample.interaction_preview.contexts.title"),
            "note": get_text(ui_lang, "sample.interaction_preview.contexts.note"),
            "rows": [
                {
                    "label": get_text(ui_lang, "sample.interaction_preview.row.form"),
                    "class_name": "pm-interaction-row--form",
                    "items": [
                        _sample_action_button(get_text(ui_lang, "auth.login.submit"), variant="primary", size="medium", leading_icon="login"),
                        _sample_action_button(get_text(ui_lang, "auth.login.forgot_password"), variant="secondary", size="medium"),
                    ],
                },
                {
                    "label": get_text(ui_lang, "sample.interaction_preview.row.hero"),
                    "class_name": "pm-interaction-row pm-interaction-row--wrap",
                    "items": [
                        _sample_nav_pill(get_text(ui_lang, "sample.interaction_preview.label.learn_more"), size="medium", href="#sample-entry-cards-title"),
                    ],
                },
                {
                    "label": get_text(ui_lang, "sample.interaction_preview.row.main_cards"),
                    "class_name": "pm-cta-link-row",
                    "items": [
                        _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.to_research"), tone="primary", href="#sample-entry-cards-title"),
                        _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.to_teaching"), tone="accent", href="#sample-entry-cards-title"),
                    ],
                },
                {
                    "label": get_text(ui_lang, "sample.interaction_preview.row.section_cards"),
                    "class_name": "pm-cta-link-row",
                    "items": [
                        _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.open_corpus"), tone="primary", href=corpus_href),
                        _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.open_materials"), tone="primary", href=materials_href),
                    ],
                },
                {
                    "label": get_text(ui_lang, "sample.interaction_preview.row.app_card"),
                    "class_name": "pm-interaction-row--card",
                    "items": [
                        _sample_nav_pill(get_text(ui_lang, "sample.button_preview.label.profile"), size="small", href=profile_href),
                        _sample_action_button(get_text(ui_lang, "sample.interaction_preview.label.compare"), variant="secondary", size="small", leading_icon="add"),
                    ],
                },
                {
                    "label": get_text(ui_lang, "sample.interaction_preview.row.toolbar"),
                    "class_name": "pm-interaction-row--toolbar",
                    "items": [
                        _sample_action_button(get_text(ui_lang, "auth.admin_users.refresh"), variant="secondary", size="medium", leading_icon="refresh"),
                        _sample_action_button(get_text(ui_lang, "auth.admin_users.create_button"), variant="primary", size="medium", leading_icon="add"),
                    ],
                },
                {
                    "label": get_text(ui_lang, "sample.interaction_preview.row.compare"),
                    "class_name": "pm-interaction-row pm-interaction-row--wrap",
                    "items": [
                        _sample_action_button(get_text(ui_lang, "sample.interaction_preview.label.compare"), variant="secondary", size="medium", leading_icon="add"),
                    ],
                },
            ],
        },
        "mock_cards": [
            {
                "eyebrow": get_text(ui_lang, "sample.interaction_preview.mock.main.eyebrow"),
                "title": get_text(ui_lang, "sample.interaction_preview.mock.main.research_title"),
                "text": get_text(ui_lang, "sample.interaction_preview.mock.main.research_text"),
                "footer_class_name": "pm-cta-link-row pm-interaction-preview__mock-footer",
                "items": [
                    _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.to_research"), tone="primary", href="#sample-entry-cards-title"),
                ],
            },
            {
                "eyebrow": get_text(ui_lang, "sample.interaction_preview.mock.main.eyebrow"),
                "title": get_text(ui_lang, "sample.interaction_preview.mock.main.teaching_title"),
                "text": get_text(ui_lang, "sample.interaction_preview.mock.main.teaching_text"),
                "footer_class_name": "pm-cta-link-row pm-interaction-preview__mock-footer",
                "items": [
                    _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.to_teaching"), tone="accent", href="#sample-entry-cards-title"),
                ],
            },
            {
                "eyebrow": get_text(ui_lang, "sample.interaction_preview.mock.research.eyebrow"),
                "title": get_text(ui_lang, "sample.interaction_preview.mock.research.title"),
                "text": get_text(ui_lang, "sample.interaction_preview.mock.research.text"),
                "meta_rows": [
                    {"label": get_text(ui_lang, "research.overview.card.project_lead"), "value": "Prof. Dr. Felix Tacke"},
                    {"label": get_text(ui_lang, "research.overview.card.material_conception"), "value": "Felix Tacke, Ana Goás Pérez"},
                    {"label": get_text(ui_lang, "research.overview.card.conducted_by"), "value": "Marlon Merte"},
                    {"label": get_text(ui_lang, "research.overview.card.learner_recordings.other", count=12), "value": ""},
                ],
                "footer_class_name": "pm-cta-link-row pm-interaction-preview__mock-footer",
                "items": [
                    _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.open_corpus"), tone="primary", href=corpus_href),
                ],
            },
            {
                "eyebrow": get_text(ui_lang, "sample.interaction_preview.mock.teaching.eyebrow"),
                "title": get_text(ui_lang, "sample.interaction_preview.mock.teaching.title"),
                "text": get_text(ui_lang, "sample.interaction_preview.mock.teaching.text"),
                "footer_class_name": "pm-cta-link-row pm-interaction-preview__mock-footer",
                "items": [
                    _sample_cta_link(get_text(ui_lang, "sample.interaction_preview.label.open_materials"), tone="primary", href=materials_href),
                ],
            },
            {
                "eyebrow": get_text(ui_lang, "sample.interaction_preview.mock.app.eyebrow"),
                "title": get_text(ui_lang, "sample.interaction_preview.mock.app.title"),
                "text": get_text(ui_lang, "sample.interaction_preview.mock.app.text"),
                "chips": [
                    _sample_chip("B2", active=True),
                    _sample_chip("L1 DE"),
                ],
                "footer_class_name": "pm-interaction-row--card pm-interaction-preview__mock-footer",
                "items": [
                    _sample_nav_pill(get_text(ui_lang, "sample.button_preview.label.profile"), size="small", href=profile_href),
                    _sample_action_button(get_text(ui_lang, "sample.interaction_preview.label.compare"), variant="secondary", size="small", leading_icon="add"),
                ],
            },
        ],
    }


def _sample_speaker_cards(ui_lang: str) -> list[dict[str, Any]]:
    profile_label = "Profil" if ui_lang == "de" else "Profile"
    recordings_label = "Aufzeichnungen" if ui_lang == "de" else "Recordings"
    recording_links_aria_label = "Direktlinks zu Aufzeichnungen" if ui_lang == "de" else "Direct links to recordings"
    learner_eyebrow = "Lernende" if ui_lang == "de" else "Learner"
    native_eyebrow = "Native Speaker" if ui_lang == "de" else "Native speaker"
    selected_session_label = "Ausgewählte Session" if ui_lang == "de" else "Selected session"

    return [
        {
            "person_id": "ES-L-0101",
            "eyebrow": learner_eyebrow,
            "selected_session_label": selected_session_label,
            "selected_session_id": "ES-L-0101-2026-S01",
            "meta_rows": [
                {
                    "label": "Niveau" if ui_lang == "de" else "Level",
                    "value": "A1",
                    "badges": [{"label": "A1", "modifiers": ["level", "a1"]}],
                },
                {"label": "L1", "value": "DE"},
                {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": "weiblich" if ui_lang == "de" else "female"},
                {"label": "Sprachaufenthalte" if ui_lang == "de" else "Stays", "value": "Nein" if ui_lang == "de" else "No"},
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
            "accent_modifier": "learner",
        },
        {
            "person_id": "ES-L-0102",
            "eyebrow": learner_eyebrow,
            "selected_session_label": selected_session_label,
            "selected_session_id": "ES-L-0102-2027-S02",
            "meta_rows": [
                {
                    "label": "Niveau" if ui_lang == "de" else "Level",
                    "value": "A2",
                    "badges": [{"label": "A2", "modifiers": ["level", "a2"]}],
                },
                {"label": "L1", "value": "DE"},
                {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": "weiblich" if ui_lang == "de" else "female"},
                {"label": "Sprachaufenthalte" if ui_lang == "de" else "Stays", "value": "Teilweise" if ui_lang == "de" else "Partial"},
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
            "accent_modifier": "learner",
        },
        {
            "person_id": "ES-L-0103",
            "eyebrow": learner_eyebrow,
            "selected_session_label": selected_session_label,
            "selected_session_id": "ES-L-0103-2026-S01",
            "meta_rows": [
                {
                    "label": "Niveau" if ui_lang == "de" else "Level",
                    "value": "B1",
                    "badges": [{"label": "B1", "modifiers": ["level", "b1"]}],
                },
                {"label": "L1", "value": "EN"},
                {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": "männlich" if ui_lang == "de" else "male"},
                {"label": "Sprachaufenthalte" if ui_lang == "de" else "Stays", "value": "Ja" if ui_lang == "de" else "Yes"},
            ],
            "profile_href": "#sample-research-profile-title",
            "profile_label": profile_label,
            "recordings_label": recordings_label,
            "recording_links_aria_label": recording_links_aria_label,
            "task_links": [
                {"label": "Wortliste" if ui_lang == "de" else "Wordlist", "href": "#sample-research-task-panels-title"},
                {"label": "Text", "href": "#sample-research-task-panels-title"},
            ],
            "accent_modifier": "learner",
        },
        {
            "person_id": "ES-L-0104",
            "eyebrow": learner_eyebrow,
            "selected_session_label": selected_session_label,
            "selected_session_id": "ES-L-0104-2026-S01",
            "meta_rows": [
                {
                    "label": "Niveau" if ui_lang == "de" else "Level",
                    "value": "B2",
                    "badges": [{"label": "B2", "modifiers": ["level", "b2"]}],
                },
                {"label": "L1", "value": "FR"},
                {"label": "Geschlecht" if ui_lang == "de" else "Gender", "value": "männlich" if ui_lang == "de" else "male"},
                {"label": "Sprachaufenthalte" if ui_lang == "de" else "Stays", "value": "Ja" if ui_lang == "de" else "Yes"},
            ],
            "profile_href": "#sample-research-profile-title",
            "profile_label": profile_label,
            "recordings_label": recordings_label,
            "recording_links_aria_label": recording_links_aria_label,
            "task_links": [
                {"label": "Wortliste" if ui_lang == "de" else "Wordlist", "href": "#sample-research-task-panels-title"},
                {"label": "Text", "href": "#sample-research-task-panels-title"},
            ],
            "accent_modifier": "learner",
        },
        {
            "person_id": "ES-N-0001",
            "eyebrow": native_eyebrow,
            "selected_session_label": selected_session_label,
            "selected_session_id": "ES-N-0001-2026-S01",
            "meta_rows": [
                {
                    "label": "Standardvarietät" if ui_lang == "de" else "Standard variety",
                    "value": "Spanien" if ui_lang == "de" else "Spain",
                    "badges": [
                        {
                            "label": "Spanien" if ui_lang == "de" else "Spain",
                            "modifiers": ["native-detail"],
                        }
                    ],
                },
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
    ui_lang = resolve_request_ui_language(
        explicit_ui_lang=request.values.get("lang") or request.values.get("ui_lang"),
        stored_ui_lang=request.cookies.get(PREFERRED_UI_LANGUAGE_COOKIE_NAME),
        next_candidates=(request.referrer, request.path),
        accept_language=request.headers.get("Accept-Language"),
    )
    return _redirect(url_for("public.localized_landing_page", ui_lang=ui_lang))


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
    research_feature_page = build_research_language_root_page(ui_lang, "french", is_authenticated=False) or {}
    teaching_feature_page = build_teaching_language_root_page(ui_lang, "spanish") or {}
    page = {
        "title": "Sample",
        "template": "pages/sample_page.html",
        "intro": (
            "Visueller Prüfstand für die aktuell produktiv genutzten Layout-Elemente. Sample folgt "
            "den realen Seiten und dient nicht als eigenständiges Vorbild."
        ),
        "is_section_root": True,
        "sample_admonitions": _sample_admonitions(ui_lang),
        "interaction_preview": _sample_interaction_preview(ui_lang),
        "sample_landing_cards": _linkify(landing_page.get("landing_cards", []), ui_lang),
        "sample_research_cards": _linkify(research_select_page.get("corpus_cards", []), ui_lang),
        "sample_teaching_cards": _linkify(teaching_select_page.get("corpus_cards", []), ui_lang),
        "sample_research_root_page": {
            "title": research_feature_page.get("title"),
            "intro": research_feature_page.get("intro"),
            "body_paragraphs": research_feature_page.get("body_paragraphs", []),
            "action_links": _linkify(research_feature_page.get("action_links", []), ui_lang),
        },
        "sample_teaching_feature_cards": _linkify(teaching_feature_page.get("feature_cards", []), ui_lang),
        "sample_speaker_cards": _sample_speaker_cards(ui_lang),
        "sample_composition_admonition": _sample_admonition(
            ui_lang,
            "context",
            "sample.admonitions.composition.context.body",
            item_id="sample-composition-context",
        ),
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
    next_url = _safe_next_value(request.args.get("next")) or ""
    ui_lang = _resolve_auth_ui_lang(next_url)
    if getattr(g, "user_id", None):
        return _redirect_authenticated_public_auth(next_url=next_url, ui_lang=ui_lang)
    response = make_response(
        render_template(
            "auth/login.html",
            next=next_url,
            auth_ui_lang=ui_lang,
            access_request_href=_build_access_request_href(ui_lang, next_url),
            page_name="login",
            shell_class="app-shell--panel-hidden",
            ui_lang=ui_lang,
        )
    )
    return _no_store_response(response)


@blueprint.route("/access-request", methods=["GET", "POST"], endpoint="access_request_page")
def access_request_page():
    raw_next = request.form.get("next") if request.method == "POST" else request.args.get("next")
    next_url = _safe_next_value(raw_next) or ""
    ui_lang = _resolve_auth_ui_lang(next_url)
    if getattr(g, "user_id", None):
        return _redirect_authenticated_public_auth(next_url=next_url, ui_lang=ui_lang)
    if request.method == "GET":
        return _render_access_request_page(next_url=next_url)

    form_values = _coerce_access_request_form(request.form)
    form_errors = _validate_access_request_form(ui_lang, form_values)
    if form_errors:
        return _render_access_request_page(
            next_url=next_url,
            form_values=form_values,
            form_errors=form_errors,
            status_code=400,
        )

    auth_services.create_access_request(
        first_name=form_values["first_name"],
        last_name=form_values["last_name"],
        institution=form_values["institution"],
        role_or_function=form_values["role_or_function"],
        email=form_values["email"],
        purpose=form_values["purpose"],
        consent_confirmed=bool(form_values["consent_confirmed"]),
        ui_lang=ui_lang,
        requested_path=next_url or None,
        user_agent=request.user_agent.string if request.user_agent else None,
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
    )
    flash(get_text(ui_lang, "auth.access_request.success"), "success")
    return redirect(_build_access_request_href(ui_lang, next_url), 303)


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
    page = build_project_page(ui_lang, first_page_slug)
    if page is None:
        abort(404)
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
    redirect_target = LEGACY_PROJECT_PAGE_REDIRECTS.get(page_slug)
    if redirect_target is not None:
        return redirect(url_for("public.project_page", ui_lang=ui_lang, page_slug=redirect_target), 308)

    canonical_page_slug = get_canonical_project_page_slug(page_slug)
    if canonical_page_slug is None:
        abort(404)

    page = build_project_page(ui_lang, canonical_page_slug)
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
    page = build_research_language_root_page(
        ui_lang,
        canonical_language_slug,
        is_authenticated=getattr(g, "user_id", None) is not None,
    )
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    corpus_title = get_research_corpus_title(language, ui_lang)
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug="language-root",
        language_label=language_label,
        context_mode="language",
        context_title=corpus_title,
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

    access_response = _require_research_route_access(page_slug=canonical_page_slug)
    if access_response is not None:
        return access_response

    language = get_language(canonical_language_slug)
    surface_mode = get_research_page_surface_mode(canonical_language_slug, canonical_page_slug)
    if surface_mode == "productive" and canonical_page_slug == "speakers":
        page = build_speakers_page(ui_lang, canonical_language_slug, request.args)
    elif surface_mode == "productive" and canonical_page_slug == "comparison":
        page = build_comparison_page(ui_lang, canonical_language_slug, request.args)
    elif surface_mode == "productive" and canonical_page_slug == "phenomena":
        page = build_phenomena_overview_page(ui_lang, canonical_language_slug)
    else:
        page = build_research_page(ui_lang, canonical_language_slug, canonical_page_slug)
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    corpus_title = get_research_corpus_title(language, ui_lang)
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug=canonical_page_slug,
        language_label=language_label,
        context_mode="language",
        context_title=corpus_title,
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


@blueprint.get("/<ui_lang>/research/<language_slug>/phenomena/presets/<preset_id>")
def research_phenomena_preset_editor(ui_lang: str, language_slug: str, preset_id: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    access_response = _require_research_route_access(detail_route="phenomena-preset-editor")
    if access_response is not None:
        return access_response

    language = get_language(canonical_language_slug)
    page = build_phenomena_preset_editor_page(ui_lang, canonical_language_slug, preset_id)
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    corpus_title = get_research_corpus_title(language, ui_lang)
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug="phenomena",
        language_label=language_label,
        context_mode="language",
        context_title=corpus_title,
        context_root_href=url_for(
            "public.research_language_root",
            ui_lang=ui_lang,
            language_slug=canonical_language_slug,
        ),
        context_back_href=url_for(
            "public.research_language_page",
            ui_lang=ui_lang,
            language_slug=canonical_language_slug,
            page_slug="phenomena",
        ),
        context_back_label=get_research_page_label("phenomena", ui_lang),
        items=_panel_items_for_language("research", canonical_language_slug, ui_lang),
    )
    return _render_promat_page(page=page, panel=panel, page_name="research", ui_lang=ui_lang)


@blueprint.get("/<ui_lang>/research/<language_slug>/phenomena/sets/<set_id>")
def research_phenomena_set_editor(ui_lang: str, language_slug: str, set_id: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    access_response = _require_research_route_access(detail_route="phenomena-set-editor")
    if access_response is not None:
        return access_response

    language = get_language(canonical_language_slug)
    page = build_phenomena_set_editor_page(ui_lang, canonical_language_slug, set_id)
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    corpus_title = get_research_corpus_title(language, ui_lang)
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug="phenomena",
        language_label=language_label,
        context_mode="language",
        context_title=corpus_title,
        context_root_href=url_for(
            "public.research_language_root",
            ui_lang=ui_lang,
            language_slug=canonical_language_slug,
        ),
        context_back_href=url_for(
            "public.research_language_page",
            ui_lang=ui_lang,
            language_slug=canonical_language_slug,
            page_slug="phenomena",
        ),
        context_back_label=get_research_page_label("phenomena", ui_lang),
        items=_panel_items_for_language("research", canonical_language_slug, ui_lang),
    )
    return _render_promat_page(page=page, panel=panel, page_name="research", ui_lang=ui_lang)


@blueprint.get("/<ui_lang>/research/<language_slug>/speakers/<person_id>")
def research_speaker_profile(ui_lang: str, language_slug: str, person_id: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    access_response = _require_research_route_access(detail_route="speaker-profile")
    if access_response is not None:
        return access_response

    language = get_language(canonical_language_slug)
    page = build_speaker_profile_page(ui_lang, canonical_language_slug, person_id, request.args.get("session"))
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    corpus_title = get_research_corpus_title(language, ui_lang)
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug="speakers",
        language_label=language_label,
        context_mode="language",
        context_title=corpus_title,
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
def research_player(ui_lang: str, language_slug: str, session_id: str, task: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    access_response = _require_research_route_access(detail_route="player")
    if access_response is not None:
        return access_response

    language = get_language(canonical_language_slug)
    source = request.args.get("source")
    compare_session = request.args.get("compare_session")
    compare_mode = request.args.get("compare_mode")
    set_id = request.args.get("set_id")
    preset_id = request.args.get("preset_id")
    focus_item = request.args.get("focus_item")
    focus_segment = request.args.get("focus_segment")
    render_mode = request.args.get("render_mode")
    page = build_player_page(
        ui_lang,
        canonical_language_slug,
        session_id,
        task,
        source,
        compare_session,
        compare_mode,
        set_id,
        preset_id,
        focus_item,
        focus_segment,
        render_mode,
    )
    if page is None or language is None:
        abort(404)

    language_label = get_language_label(language, ui_lang)
    corpus_title = get_research_corpus_title(language, ui_lang)
    active_slug = (
        "speakers"
        if source in {"recordings", "speakers", "profile"}
        else "comparison"
        if source == "comparison"
        else "phenomena"
        if source == "phenomena"
        else ""
    )
    panel = _panel_config(
        section_key="research",
        section_label=get_section_label("research", ui_lang),
        active_slug=active_slug,
        language_label=language_label,
        context_mode="language",
        context_title=corpus_title,
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


def _player_download_filename(person_id: str, task_key: str, item_id: str, download_label: str) -> str:
    readable_label = re.sub(r"[^\w\s-]", "", download_label.strip().lower(), flags=re.UNICODE)
    readable_label = re.sub(r"[-\s]+", "-", readable_label, flags=re.UNICODE).strip("-_") or item_id
    return f"{person_id}_{task_key}_{item_id}_{readable_label}.mp3"


def _request_wants_download() -> bool:
    value = (request.args.get("download") or "").strip().lower()
    return value not in {"", "0", "false", "no"}


def _resolve_public_teaching_asset(asset_path: str) -> Path | None:
    relative_path = Path(asset_path)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return None

    asset_root = get_public_root() / "teaching"
    candidate = (asset_root / relative_path).resolve()
    try:
        candidate.relative_to(asset_root.resolve())
    except ValueError:
        return None

    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate


@blueprint.get("/<ui_lang>/research/<language_slug>/player/<session_id>/<task>/audio.mp3")
def research_player_audio(ui_lang: str, language_slug: str, session_id: str, task: str):
    _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    access_response = _require_research_route_access(detail_route="player-audio")
    if access_response is not None:
        return access_response

    artifact_path = resolve_player_audio_artifact(canonical_language_slug, session_id, task)
    if artifact_path is None:
        abort(404)

    return send_file(artifact_path, mimetype="audio/mpeg", conditional=True, etag=False)


@blueprint.get("/<ui_lang>/research/<language_slug>/player/<session_id>/<task>/items/<item_id>.mp3")
def research_player_item_download(ui_lang: str, language_slug: str, session_id: str, task: str, item_id: str):
    _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    access_response = _require_research_route_access(detail_route="player-item-audio")
    if access_response is not None:
        return access_response

    artifact = resolve_player_item_download(canonical_language_slug, session_id, task, item_id)
    if artifact is None:
        abort(404)

    download_name = _player_download_filename(
        artifact["person_id"],
        artifact["task_key"],
        artifact["item_id"],
        artifact["download_label"],
    )

    return send_file(
        artifact["path"],
        mimetype="audio/mpeg",
        as_attachment=_request_wants_download(),
        download_name=download_name,
        conditional=True,
        etag=False,
    )


@blueprint.get("/<ui_lang>/teaching")
def teaching_home(ui_lang: str):
    ui_lang = _require_ui_lang(ui_lang)
    panel = _panel_config(section_key="teaching", section_label=get_section_label("teaching", ui_lang), active_slug="", context_mode="none", items=[])
    return _render_promat_page(
        page=build_teaching_select_page(ui_lang),
        panel=panel,
        page_name="teaching",
        ui_lang=ui_lang,
    )


@blueprint.get("/teaching/<path:asset_path>")
def teaching_public_asset(asset_path: str):
    asset_file = _resolve_public_teaching_asset(asset_path)
    if asset_file is None:
        abort(404)

    return send_file(asset_file, conditional=True, etag=False)


@blueprint.get("/<ui_lang>/teaching/<language_slug>")
def teaching_language_root(ui_lang: str, language_slug: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    page = build_teaching_language_root_page(ui_lang, canonical_language_slug)
    if page is None:
        abort(404)
    resolved_ui_lang = page.get("resolved_ui_lang", ui_lang)
    if resolved_ui_lang != ui_lang:
        return redirect(
            url_for(
                "public.teaching_language_root",
                ui_lang=resolved_ui_lang,
                language_slug=canonical_language_slug,
            ),
            302,
        )

    panel = _panel_config(section_key="teaching", section_label=get_section_label("teaching", resolved_ui_lang), active_slug="", context_mode="none", items=[])
    return _render_promat_page(page=page, panel=panel, page_name="teaching", ui_lang=resolved_ui_lang)


@blueprint.get("/<ui_lang>/teaching/<language_slug>/<page_slug>")
def teaching_language_page(ui_lang: str, language_slug: str, page_slug: str):
    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        abort(404)

    resolution = resolve_topic_route_target(canonical_language_slug, ui_lang, page_slug)
    if resolution["status"] == "missing-language":
        abort(404)
    if resolution["status"] == "redirect-hub":
        return redirect(
            url_for(
                "public.teaching_language_root",
                ui_lang=resolution["ui_lang"],
                language_slug=canonical_language_slug,
            ),
            302,
        )
    if resolution["status"] == "redirect-topic":
        return redirect(
            url_for(
                "public.teaching_language_page",
                ui_lang=resolution["ui_lang"],
                language_slug=canonical_language_slug,
                page_slug=resolution["topic_slug"],
            ),
            302,
        )
    if resolution["status"] != "ok":
        abort(404)

    resolved_ui_lang = resolution["ui_lang"]
    page = build_teaching_page(resolved_ui_lang, canonical_language_slug, resolution["topic_slug"])
    if page is None:
        abort(404)

    panel = _panel_config(section_key="teaching", section_label=get_section_label("teaching", resolved_ui_lang), active_slug="", context_mode="none", items=[])
    return _render_promat_page(page=page, panel=panel, page_name="teaching", ui_lang=resolved_ui_lang)


@blueprint.get("/impressum")
def impressum_page():
    return _render_legal_page("impressum")


@blueprint.get("/datenschutz")
@blueprint.get("/privacy")
def privacy_page():
    return _render_legal_page("privacy")
