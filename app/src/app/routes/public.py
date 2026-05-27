"""Public routes for PROMAT."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import re
import time
from urllib.parse import unquote, urlparse

from flask import Blueprint, abort, current_app, flash, g, jsonify, make_response, redirect, render_template, request, send_file, url_for
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy import event, inspect, text

from ..auth import Role
from ..auth import services as auth_services
from ..content_navigation import build_content_header as build_shared_content_header
from ..extensions import limiter
from ..i18n import PREFERRED_UI_LANGUAGE_COOKIE_NAME, resolve_request_ui_language
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
from ..services.access_request_notifications import deliver_access_request_notification
from ..teaching_content import resolve_teaching_topic_media_artifact, resolve_topic_route_target
from ..extensions.sqlalchemy_ext import get_engine
from .public_content import (
    DEFAULT_UI_LANGUAGE,
    LEGAL_PAGES,
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
from .public_page_content_data import LEGACY_PROJECT_PAGE_REDIRECTS

blueprint = Blueprint("public", __name__)


_ACCESS_REQUEST_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_ACCESS_REQUEST_HONEYPOT_FIELD = "website"
_ACCESS_REQUEST_FORM_TOKEN_FIELD = "access_request_form_token"
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


def _access_request_email_domain(email: str) -> str:
    normalized = auth_services.normalize_email(email)
    return normalized.partition("@")[2] or "unknown"


def _access_request_form_serializer() -> URLSafeSerializer:
    return URLSafeSerializer(current_app.secret_key, salt="auth.access-request.form")


def _build_access_request_form_token(*, next_url: str, ui_lang: str, issued_at: float | None = None) -> str:
    payload = {
        "issued_at": float(issued_at if issued_at is not None else time.time()),
        "next": next_url,
        "ui_lang": ui_lang,
    }
    return _access_request_form_serializer().dumps(payload)


def _resolve_access_request_form_token(raw_token: str | None) -> dict[str, Any] | None:
    if not raw_token:
        return None
    try:
        payload = _access_request_form_serializer().loads(raw_token)
    except BadSignature:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _access_request_submission_is_suspicious(*, ui_lang: str, next_url: str, form_values: dict[str, Any]) -> bool:
    honeypot_value = str(request.form.get(_ACCESS_REQUEST_HONEYPOT_FIELD) or "").strip()
    if honeypot_value:
        current_app.logger.info(
            "Access request blocked by honeypot | ui_lang=%s | email_domain=%s",
            ui_lang,
            _access_request_email_domain(form_values.get("email", "")),
        )
        return True

    token_payload = _resolve_access_request_form_token(request.form.get(_ACCESS_REQUEST_FORM_TOKEN_FIELD))
    if token_payload is None:
        current_app.logger.info("Access request blocked by invalid form token | ui_lang=%s", ui_lang)
        return True
    if token_payload.get("next") != next_url or token_payload.get("ui_lang") != ui_lang:
        current_app.logger.info("Access request blocked by mismatched form token context | ui_lang=%s", ui_lang)
        return True

    issued_at = token_payload.get("issued_at")
    if not isinstance(issued_at, (int, float)):
        current_app.logger.info("Access request blocked by invalid form timing token | ui_lang=%s", ui_lang)
        return True

    token_age_seconds = float(time.time()) - float(issued_at)
    configured_min_submit_seconds = current_app.config.get("AUTH_ACCESS_REQUEST_MIN_SUBMIT_SECONDS")
    configured_max_age_seconds = current_app.config.get("AUTH_ACCESS_REQUEST_FORM_MAX_AGE_SECONDS")
    min_submit_seconds = 0.5 if configured_min_submit_seconds is None else float(configured_min_submit_seconds)
    max_age_seconds = 43200 if configured_max_age_seconds is None else int(configured_max_age_seconds)

    if token_age_seconds < min_submit_seconds:
        current_app.logger.info(
            "Access request blocked by submit timing guard | ui_lang=%s | email_domain=%s",
            ui_lang,
            _access_request_email_domain(form_values.get("email", "")),
        )
        return True
    if token_age_seconds > max_age_seconds:
        current_app.logger.info("Access request blocked by expired form token | ui_lang=%s", ui_lang)
        return True

    return False


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

    for field_name in ("first_name", "last_name", "institution", "role_or_function", "email"):
        field_value = str(values.get(field_name) or "")
        if any(character in field_value for character in {"\r", "\n", "\x00"}):
            errors[field_name] = get_text(ui_lang, "auth.access_request.error.invalid_input")

    if "\x00" in str(values.get("purpose") or ""):
        errors["purpose"] = get_text(ui_lang, "auth.access_request.error.invalid_input")

    if not values.get("consent_confirmed"):
        errors["consent_confirmed"] = get_text(ui_lang, "auth.access_request.error.confirmation_required")

    return errors


def _render_access_request_page(*, next_url: str, form_values: dict[str, Any] | None = None, form_errors: dict[str, str] | None = None, status_code: int = 200):
    ui_lang = _resolve_auth_ui_lang(next_url)
    form_token = _build_access_request_form_token(next_url=next_url, ui_lang=ui_lang)
    response = make_response(
        render_template(
            "auth/access_request.html",
            next=next_url,
            login_href=_build_login_href(ui_lang, next_url),
            access_request_form=_coerce_access_request_form(form_values),
            access_request_errors=form_errors or {},
            access_request_form_token=form_token,
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


def _player_profile_requested() -> bool:
    return request.args.get("_profile") == "1" or request.headers.get("X-Promat-Profile") == "1"


def _player_prewarm_requested() -> bool:
    return request.headers.get("X-Promat-Player-Prewarm") == "1"


def _section_home_href(section_key: str, ui_lang: str) -> str | None:
    if section_key == "project":
        return url_for("public.project_home", ui_lang=ui_lang)
    if section_key == "research":
        return url_for("public.research_home", ui_lang=ui_lang)
    if section_key == "teaching":
        return url_for("public.teaching_home", ui_lang=ui_lang)
    return None


def _build_content_header(
    page: dict[str, Any],
    panel: dict[str, Any],
    page_name: str,
    ui_lang: str,
) -> dict[str, Any]:
    back_link = None
    if panel.get("context_back_href") and panel.get("context_back_label"):
        back_link = {
            "href": panel["context_back_href"],
            "label": panel["context_back_label"],
        }

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
        back_link=back_link,
    )


def _resolve_href_key(href_key: str, ui_lang: str) -> str:
    if href_key == "project_root":
        return url_for("public.project_home", ui_lang=ui_lang)
    if href_key == "research_root":
        return url_for("public.research_home", ui_lang=ui_lang)
    if href_key == "teaching_root":
        return url_for("public.teaching_home", ui_lang=ui_lang)
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
        shell_class = "app-shell--inner"
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


@blueprint.get("/access-request", endpoint="access_request_page")
def access_request_page():
    raw_next = request.args.get("next")
    next_url = _safe_next_value(raw_next) or ""
    ui_lang = _resolve_auth_ui_lang(next_url)
    if getattr(g, "user_id", None):
        return _redirect_authenticated_public_auth(next_url=next_url, ui_lang=ui_lang)
    return _render_access_request_page(next_url=next_url)


@blueprint.post("/access-request", endpoint="access_request_submit")
@limiter.limit("5 per hour")
@limiter.limit("20 per day")
def access_request_submit():
    raw_next = request.form.get("next")
    next_url = _safe_next_value(raw_next) or ""
    ui_lang = _resolve_auth_ui_lang(next_url)
    if getattr(g, "user_id", None):
        return _redirect_authenticated_public_auth(next_url=next_url, ui_lang=ui_lang)

    form_values = _coerce_access_request_form(request.form)
    form_errors = _validate_access_request_form(ui_lang, form_values)
    if form_errors:
        return _render_access_request_page(
            next_url=next_url,
            form_values=form_values,
            form_errors=form_errors,
            status_code=400,
        )

    if _access_request_submission_is_suspicious(ui_lang=ui_lang, next_url=next_url, form_values=form_values):
        flash(get_text(ui_lang, "auth.access_request.success"), "success")
        return redirect(_build_access_request_href(ui_lang, next_url), 303)

    access_request = auth_services.create_access_request(
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
    deliver_access_request_notification(access_request)
    flash(get_text(ui_lang, "auth.access_request.success"), "success")
    return redirect(_build_access_request_href(ui_lang, next_url), 303)


@blueprint.get("/health")
@limiter.exempt
def health_check():
    return jsonify({"status": "healthy", "service": "promat-web"}), 200


def _readiness_check_path(path: Path, *, mode: str) -> dict[str, Any]:
    try:
        if not path.exists():
            return {"ok": False, "error": "missing"}
        if not path.is_dir():
            return {"ok": False, "error": "not_a_directory"}
        if mode == "read":
            try:
                next(path.iterdir(), None)
            except StopIteration:
                pass
            return {"ok": True, "error": None}
        if mode == "write":
            probe = path / ".promat-ready-probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return {"ok": True, "error": None}
        return {"ok": False, "error": f"unknown_mode:{mode}"}
    except OSError as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc.strerror or exc}"}


def _readiness_payload(status: str, checks: dict[str, dict[str, Any]], status_code: int):
    return jsonify({"status": status, "service": "promat-web", "checks": checks}), status_code


@blueprint.get("/ready")
@limiter.exempt
def readiness_check():
    checks: dict[str, dict[str, Any]] = {
        "flask": {"ok": True, "error": None},
        "auth_db": {"ok": False, "error": None},
        "data_root": {"ok": False, "error": None},
        "logs_dir": {"ok": False, "error": None},
        "rate_limit_backend": {"ok": False, "error": None},
    }

    try:
        engine = get_engine()
        if engine is None:
            raise RuntimeError("Auth engine not initialized")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        inspector = inspect(engine)
        if not inspector.has_table("users"):
            raise RuntimeError("required table 'users' is missing")
        checks["auth_db"] = {"ok": True, "error": None}
    except Exception as exc:  # noqa: BLE001
        checks["auth_db"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    checks["data_root"] = _readiness_check_path(Path(current_app.config["DATA_ROOT"]), mode="read")
    checks["logs_dir"] = _readiness_check_path(Path(current_app.config["LOGS_DIR"]), mode="write")

    rate_limit_uri = str(current_app.config.get("RATE_LIMIT_STORAGE_URI") or "")
    if not rate_limit_uri:
        checks["rate_limit_backend"] = {"ok": False, "error": "RATE_LIMIT_STORAGE_URI is not configured"}
    elif rate_limit_uri.lower() == "memory://" and current_app.config.get("FLASK_ENV") not in {"development", "dev", "testing", "test"}:
        checks["rate_limit_backend"] = {"ok": False, "error": "RATE_LIMIT_STORAGE_URI must not be memory:// in production"}
    else:
        checks["rate_limit_backend"] = {"ok": True, "error": None}

    if os.getenv("PROMAT_REQUIRE_RUNTIME_CONFIG", "").lower() in {"1", "true", "yes", "on"}:
        config_root = Path(current_app.config["CONFIG_ROOT"])
        checks["config_root"] = _readiness_check_path(config_root, mode="read")

    if all(check["ok"] for check in checks.values()):
        return _readiness_payload("ready", checks, 200)
    return _readiness_payload("not_ready", checks, 503)


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
    profile_requested = _player_profile_requested()
    prewarm_requested = _player_prewarm_requested()
    route_started_at = time.perf_counter()
    access_started_at = time.perf_counter()
    db_metrics = {"count": 0, "duration_ms": 0.0}
    player_profile: dict[str, float] = {}
    engine = None
    before_cursor_execute = None
    after_cursor_execute = None

    if profile_requested:
        engine = get_engine()

        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            del cursor, statement, parameters, executemany
            context._promat_started_at = time.perf_counter()

        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            del conn, cursor, statement, parameters, executemany
            started_at = getattr(context, "_promat_started_at", None)
            if started_at is None:
                return
            db_metrics["count"] += 1
            db_metrics["duration_ms"] += (time.perf_counter() - started_at) * 1000.0

        event.listen(engine, "before_cursor_execute", before_cursor_execute)
        event.listen(engine, "after_cursor_execute", after_cursor_execute)

    ui_lang = _require_ui_lang(ui_lang)
    canonical_language_slug = get_canonical_language_slug(language_slug)
    if canonical_language_slug is None:
        if profile_requested and engine is not None and before_cursor_execute is not None and after_cursor_execute is not None:
            event.remove(engine, "before_cursor_execute", before_cursor_execute)
            event.remove(engine, "after_cursor_execute", after_cursor_execute)
        abort(404)

    access_response = _require_research_route_access(detail_route="player")
    access_ms = (time.perf_counter() - access_started_at) * 1000.0
    if access_response is not None:
        if profile_requested and engine is not None and before_cursor_execute is not None and after_cursor_execute is not None:
            event.remove(engine, "before_cursor_execute", before_cursor_execute)
            event.remove(engine, "after_cursor_execute", after_cursor_execute)
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
    build_started_at = time.perf_counter()
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
        profile=player_profile if profile_requested else None,
    )
    build_ms = (time.perf_counter() - build_started_at) * 1000.0
    if page is None or language is None:
        if profile_requested and engine is not None and before_cursor_execute is not None and after_cursor_execute is not None:
            event.remove(engine, "before_cursor_execute", before_cursor_execute)
            event.remove(engine, "after_cursor_execute", after_cursor_execute)
        abort(404)

    if prewarm_requested:
        if profile_requested and engine is not None and before_cursor_execute is not None and after_cursor_execute is not None:
            event.remove(engine, "before_cursor_execute", before_cursor_execute)
            event.remove(engine, "after_cursor_execute", after_cursor_execute)
        route_ms = (time.perf_counter() - route_started_at) * 1000.0
        response = make_response("", 204)
        response.headers["X-Promat-Player-Prewarm"] = "1"
        if profile_requested:
            response.headers["X-Promat-Player-Profile"] = json.dumps(
                {
                    "access_ms": round(access_ms, 3),
                    "build_ms": round(build_ms, 3),
                    "render_ms": 0.0,
                    "route_ms": round(route_ms, 3),
                    "db_query_count": db_metrics["count"],
                    "db_duration_ms": round(db_metrics["duration_ms"], 3),
                    **{key: round(value, 3) for key, value in player_profile.items()},
                },
                ensure_ascii=True,
                separators=(",", ":"),
            )
            response.headers["Server-Timing"] = ", ".join(
                [
                    f"access;dur={access_ms:.3f}",
                    f"build;dur={build_ms:.3f}",
                    "render;dur=0.000",
                    f"route;dur={route_ms:.3f}",
                    f"db;dur={db_metrics['duration_ms']:.3f};desc=queries:{db_metrics['count']}",
                    *(f"runtime-{key.removesuffix('_ms')};dur={value:.3f}" for key, value in player_profile.items()),
                ]
            )
        return response

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
    render_started_at = time.perf_counter()
    html = _render_promat_page(page=page, panel=panel, page_name="research", ui_lang=ui_lang)
    render_ms = (time.perf_counter() - render_started_at) * 1000.0

    if profile_requested and engine is not None and before_cursor_execute is not None and after_cursor_execute is not None:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)
        event.remove(engine, "after_cursor_execute", after_cursor_execute)

    if not profile_requested:
        return html

    route_ms = (time.perf_counter() - route_started_at) * 1000.0
    response = make_response(html)
    response.headers["X-Promat-Player-Profile"] = json.dumps(
        {
            "access_ms": round(access_ms, 3),
            "build_ms": round(build_ms, 3),
            "render_ms": round(render_ms, 3),
            "route_ms": round(route_ms, 3),
            "db_query_count": db_metrics["count"],
            "db_duration_ms": round(db_metrics["duration_ms"], 3),
            **{key: round(value, 3) for key, value in player_profile.items()},
        },
        ensure_ascii=True,
        separators=(",", ":"),
    )
    response.headers["Server-Timing"] = ", ".join(
        [
            f"access;dur={access_ms:.3f}",
            f"build;dur={build_ms:.3f}",
            f"render;dur={render_ms:.3f}",
            f"route;dur={route_ms:.3f}",
            f"db;dur={db_metrics['duration_ms']:.3f};desc=queries:{db_metrics['count']}",
            *(f"runtime-{key.removesuffix('_ms')};dur={value:.3f}" for key, value in player_profile.items()),
        ]
    )
    return response


def _player_download_filename(person_id: str, task_key: str, item_id: str, download_label: str) -> str:
    readable_label = re.sub(r"[^\w\s-]", "", download_label.strip().lower(), flags=re.UNICODE)
    readable_label = re.sub(r"[-\s]+", "-", readable_label, flags=re.UNICODE).strip("-_") or item_id
    return f"{person_id}_{task_key}_{item_id}_{readable_label}.mp3"


def _request_wants_download() -> bool:
    value = (request.args.get("download") or "").strip().lower()
    return value not in {"", "0", "false", "no"}


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


@blueprint.get("/teaching-media/<teaching_lang>/<topic_slug>/<media_type>/<path:filename>")
def teaching_topic_media(teaching_lang: str, topic_slug: str, media_type: str, filename: str):
    asset_file = resolve_teaching_topic_media_artifact(teaching_lang, topic_slug, media_type, filename)
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
