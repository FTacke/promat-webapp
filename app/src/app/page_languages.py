"""Per-page UI-language availability (docs/spec/platform-data-files.md, "Single-language pages").

Every public page under ``/{ui_lang}/...`` exists in all supported UI languages unless it is declared here. A declared
page exists only in the listed languages: a request in any other language is redirected to the first listed one, the
language switch shows the missing language as unavailable, hreflang names only the existing editions, and navigation
links point straight to an existing edition.

Teaching keeps its own edition model (``content/teaching``); this registry covers the other public pages.
"""

from __future__ import annotations

from .i18n import SUPPORTED_UI_LANGUAGES

#: Pages that exist in fewer than all UI languages: path below the ``/{ui_lang}`` prefix -> available UI languages,
#: the first one being the redirect target. Keys are exact paths (no trailing slash, no query string).
PAGE_UI_LANGUAGES: dict[str, tuple[str, ...]] = {
    # The design article of the English corpus is published in English only (author: content/publication/resources.yaml).
    "research/english/design": ("en",),
}


def _split_ui_lang_path(path: str) -> tuple[str | None, str]:
    """``/en/research/x`` -> (``en``, ``research/x``); paths without a UI-language prefix -> (None, path)."""
    stripped = (path or "").strip("/")
    head, _, rest = stripped.partition("/")
    if head in SUPPORTED_UI_LANGUAGES:
        return head, rest
    return None, stripped


def page_ui_languages(path: str) -> tuple[str, ...]:
    """UI languages in which the page at ``path`` exists (all supported languages unless declared otherwise)."""
    ui_lang, page_path = _split_ui_lang_path(path)
    if ui_lang is None:
        return tuple(SUPPORTED_UI_LANGUAGES)
    return PAGE_UI_LANGUAGES.get(page_path, tuple(SUPPORTED_UI_LANGUAGES))


def unavailable_ui_language_target(path: str) -> str | None:
    """Path of the existing edition when ``path`` asks for a UI language the page does not have, else ``None``."""
    ui_lang, page_path = _split_ui_lang_path(path)
    if ui_lang is None:
        return None
    available = page_ui_languages(path)
    if ui_lang in available:
        return None
    return f"/{available[0]}/{page_path}"


def available_page_path(path: str) -> str:
    """``path`` itself, or the path of its existing edition; used for navigation links so they need no redirect."""
    return unavailable_ui_language_target(path) or path
