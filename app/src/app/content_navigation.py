"""Shared breadcrumb and content-header helpers for public PROMAT pages."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def _normalize_path_item(item: Mapping[str, Any]) -> dict[str, Any] | None:
    label = str(item.get("label") or "").strip()
    if not label:
        return None
    return {"label": label, "href": item.get("href"), "current": False}


def _finalize_path(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        normalized_item = _normalize_path_item(item)
        if normalized_item is not None:
            normalized.append(normalized_item)

    if not normalized:
        return []

    normalized[-1]["href"] = None
    normalized[-1]["current"] = True
    return normalized


def build_navigation_path(
    *,
    page_name: str,
    section_label: str | None,
    section_href: str | None,
    context_mode: str,
    context_title: str | None,
    context_root_href: str | None,
    title: str,
    is_section_root: bool = False,
    is_language_root: bool = False,
    ancestors: Sequence[Mapping[str, Any]] | None = None,
    current_label: str | None = None,
    current_href: str | None = None,
) -> list[dict[str, Any]]:
    if page_name == "start":
        return []

    path_items: list[dict[str, Any]] = []

    if section_label:
        path_items.append({"label": section_label, "href": None if is_section_root else section_href})

    if context_mode == "language" and context_title:
        path_items.append({"label": context_title, "href": None if is_language_root else context_root_href})

    if ancestors:
        path_items.extend(dict(item) for item in ancestors)

    include_current = not is_section_root and not (context_mode == "language" and is_language_root)
    resolved_current_label = (current_label or title).strip()
    if include_current and resolved_current_label:
        last_label = str(path_items[-1]["label"]).strip() if path_items else ""
        if last_label != resolved_current_label:
            path_items.append({"label": resolved_current_label, "href": current_href})

    return _finalize_path(path_items)


def build_content_header(
    *,
    page_name: str,
    title: str,
    intro: str | None,
    section_label: str | None,
    section_href: str | None,
    context_mode: str,
    context_title: str | None,
    context_root_href: str | None,
    is_section_root: bool = False,
    is_language_root: bool = False,
    ancestors: Sequence[Mapping[str, Any]] | None = None,
    current_label: str | None = None,
    current_href: str | None = None,
    back_link: Mapping[str, Any] | None = None,
    title_id: str = "promat-page-title",
) -> dict[str, Any]:
    path = build_navigation_path(
        page_name=page_name,
        section_label=section_label,
        section_href=section_href,
        context_mode=context_mode,
        context_title=context_title,
        context_root_href=context_root_href,
        title=title,
        is_section_root=is_section_root,
        is_language_root=is_language_root,
        ancestors=ancestors,
        current_label=current_label,
        current_href=current_href,
    )
    depth = len(path)
    show_mobile = depth >= 2
    show_desktop = depth >= 3

    return {
        "back_link": dict(back_link) if back_link else None,
        "breadcrumbs": path if show_mobile else [],
        "breadcrumb_depth": depth,
        "breadcrumb_mode": "all" if show_desktop else "mobile-only" if show_mobile else "hidden",
        "title": title,
        "intro": intro,
        "title_id": title_id,
    }