"""Protected-area navigation helpers for account and admin surfaces."""

from __future__ import annotations

from flask import url_for

from .content_navigation import build_content_header


def build_admin_panel(ui_lang: str, *, active_slug: str, translate):
    section_label = translate(ui_lang, "shell.admin.section")
    return {
        "section_key": "admin",
        "section_label": section_label,
        "context_mode": "none",
        "context_title": None,
        "active_primary_label": section_label,
        "mobile_context_title": section_label,
        "show_mobile_context_title": False,
        "active_slug": active_slug,
        "show_section_icon": True,
        "items": [
            {
                "label": translate(ui_lang, "shell.admin.users"),
                "href": url_for("admin.users_page", ui_lang=ui_lang),
                "page_slug": "users",
            },
            {
                "label": translate(ui_lang, "shell.admin.analytics"),
                "href": url_for("admin.analytics_page", ui_lang=ui_lang),
                "page_slug": "analytics",
            },
        ],
    }


def build_protected_content_header(
    *,
    page_name: str,
    title: str,
    intro: str | None,
    ui_lang: str,
    translate,
    section_label: str | None = None,
    section_href: str | None = None,
    current_href: str | None = None,
    back_link: dict[str, str] | None = None,
):
    return build_content_header(
        page_name=page_name,
        title=title,
        intro=intro,
        section_label=section_label,
        section_href=section_href,
        context_mode="none",
        context_title=None,
        context_root_href=None,
        current_href=current_href,
        back_link=back_link,
    )