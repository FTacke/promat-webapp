"""Date-based public Teaching content for PROMAT."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from flask import url_for
from markdown_it import MarkdownIt

from .content_navigation import build_content_header
from .i18n import SUPPORTED_UI_LANGUAGES, translate
from .runtime_paths import get_public_root


logger = logging.getLogger(__name__)


def _discover_default_teaching_content_root(module_path: Path | None = None) -> Path:
    resolved_module_path = (module_path or Path(__file__)).resolve()
    for ancestor in resolved_module_path.parents:
        candidate = ancestor / "content" / "teaching"
        if candidate.exists():
            return candidate

    fallback_parent_index = 3 if len(resolved_module_path.parents) > 3 else len(resolved_module_path.parents) - 1
    return resolved_module_path.parents[fallback_parent_index] / "content" / "teaching"


DEFAULT_TEACHING_CONTENT_ROOT = _discover_default_teaching_content_root()
TEACHING_CONTENT_ROOT = Path(
    os.getenv("PROMAT_TEACHING_CONTENT_ROOT", str(DEFAULT_TEACHING_CONTENT_ROOT))
).expanduser()
_MARKDOWN_RENDERER = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": False})


def _as_text(value: Any) -> str:
    return str(value or "").strip()


def _split_paragraphs(value: Any) -> list[str]:
    body = _as_text(value)
    if not body:
        return []
    return [paragraph.strip() for paragraph in body.split("\n\n") if paragraph.strip()]


def _safe_yaml_map(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        logger.warning("Teaching content file %s did not contain a mapping root.", path)
        return None
    return loaded


def clear_teaching_content_caches() -> None:
    load_teaching_manifest.cache_clear()
    load_teaching_index.cache_clear()
    load_teaching_topic.cache_clear()


def _manifest_path(teaching_lang: str) -> Path:
    return TEACHING_CONTENT_ROOT / teaching_lang / "teaching.yaml"


def _index_path(teaching_lang: str, ui_lang: str) -> Path:
    return TEACHING_CONTENT_ROOT / teaching_lang / ui_lang / "index.yaml"


def _topic_path(teaching_lang: str, ui_lang: str, topic_slug: str) -> Path:
    return TEACHING_CONTENT_ROOT / teaching_lang / ui_lang / "topics" / f"{topic_slug}.yaml"


def _normalize_ui_langs(values: Any) -> list[str]:
    normalized: list[str] = []
    if not isinstance(values, list):
        return normalized
    for value in values:
        candidate = _as_text(value).lower()
        if candidate and candidate not in normalized:
            normalized.append(candidate)
    return normalized


def _public_asset_path(asset_url: str | None) -> Path | None:
    candidate = _as_text(asset_url)
    if not candidate or not candidate.startswith("/"):
        return None
    parsed = urlparse(candidate)
    relative_path = parsed.path.lstrip("/")
    if not relative_path:
        return None
    return get_public_root() / relative_path


def _public_asset_exists(asset_url: str | None) -> bool:
    asset_path = _public_asset_path(asset_url)
    return bool(asset_path and asset_path.exists() and asset_path.is_file())


def _person_entries(values: Any) -> list[dict[str, str]]:
    people: list[dict[str, str]] = []
    if not isinstance(values, list):
        return people
    for item in values:
        if not isinstance(item, dict):
            continue
        name = _as_text(item.get("name"))
        if not name:
            continue
        people.append(
            {
                "name": name,
                "affiliation": _as_text(item.get("affiliation")),
                "role": _as_text(item.get("role")),
                "url": _as_text(item.get("url")),
                "orcid": _as_text(item.get("orcid")),
            }
        )
    return people


def _topic_card_metadata(entry: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    level = _as_text(entry.get("level"))
    category = _as_text(entry.get("category"))
    if level:
        rows.append({"label": "level", "value": level})
    if category:
        rows.append({"label": "category", "value": category})
    return rows


def _audio_example_payload(teaching_lang: str, raw_item: dict[str, Any]) -> dict[str, Any]:
    audio_url = _as_text(raw_item.get("audio"))
    return {
        "label": _as_text(raw_item.get("label")) or _as_text(raw_item.get("title")),
        "title": _as_text(raw_item.get("title")),
        "audio": audio_url,
        "transcript": _as_text(raw_item.get("transcript")),
        "segments": [
            {"text": _as_text(segment.get("text"))}
            for segment in raw_item.get("segments", [])
            if isinstance(segment, dict) and _as_text(segment.get("text"))
        ],
        "is_available": _public_asset_exists(audio_url),
        "teaching_lang": teaching_lang,
    }


def _download_payload(raw_block: dict[str, Any]) -> dict[str, Any]:
    href = _as_text(raw_block.get("href") or raw_block.get("url") or raw_block.get("file"))
    return {
        "title": _as_text(raw_block.get("title")),
        "label": _as_text(raw_block.get("label")) or href.rsplit("/", 1)[-1],
        "href": href,
        "description": _as_text(raw_block.get("description")),
        "is_available": _public_asset_exists(href) if href.startswith("/") else bool(href),
    }


def _build_topic_grid_cards(teaching_lang: str, ui_lang: str, topic_slugs: list[str]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    index = load_teaching_index(teaching_lang, ui_lang) or {}
    listed_topics = {
        _as_text(item.get("slug")): item
        for item in index.get("topics", [])
        if isinstance(item, dict) and _as_text(item.get("slug"))
    }
    for topic_slug in topic_slugs:
        entry = listed_topics.get(topic_slug)
        if not entry or not topic_exists(teaching_lang, ui_lang, topic_slug):
            continue
        cards.append(
            {
                "slug": topic_slug,
                "title": _as_text(entry.get("title")) or topic_slug,
                "summary": _as_text(entry.get("summary")),
                "metadata": _topic_card_metadata(entry),
                "href": url_for(
                    "public.teaching_language_page",
                    ui_lang=ui_lang,
                    language_slug=teaching_lang,
                    page_slug=topic_slug,
                ),
            }
        )
    return cards


def _teaching_switch_items(current_ui_lang: str, teaching_lang: str, *, topic_slug: str | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    available_ui_langs = set(list_existing_ui_editions(teaching_lang))
    for target_ui_lang in SUPPORTED_UI_LANGUAGES:
        href = None
        fallback_to_hub = False
        disabled = target_ui_lang not in available_ui_langs
        if not disabled:
            if topic_slug:
                target_topic_slug = resolve_topic_slug_for_ui_lang(teaching_lang, current_ui_lang, topic_slug, target_ui_lang)
                if target_topic_slug:
                    href = url_for(
                        "public.teaching_language_page",
                        ui_lang=target_ui_lang,
                        language_slug=teaching_lang,
                        page_slug=target_topic_slug,
                    )
                else:
                    href = url_for(
                        "public.teaching_language_root",
                        ui_lang=target_ui_lang,
                        language_slug=teaching_lang,
                    )
                    fallback_to_hub = True
            else:
                href = url_for(
                    "public.teaching_language_root",
                    ui_lang=target_ui_lang,
                    language_slug=teaching_lang,
                )
        items.append(
            {
                "ui_lang": target_ui_lang,
                "label": translate(current_ui_lang, f"shell.topbar.language_{target_ui_lang}"),
                "href": href,
                "is_current": target_ui_lang == current_ui_lang,
                "is_disabled": disabled,
                "fallback_to_hub": fallback_to_hub,
            }
        )
    return items


def _topic_blocks(teaching_lang: str, ui_lang: str, topic_slug: str, raw_topic: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for index, raw_block in enumerate(raw_topic.get("blocks", [])):
        if not isinstance(raw_block, dict):
            continue
        block_type = _as_text(raw_block.get("type"))
        block_id = f"{topic_slug}-block-{index + 1}"
        if block_type == "hero":
            blocks.append(
                {
                    "type": "hero",
                    "id": block_id,
                    "eyebrow": _as_text(raw_block.get("eyebrow")),
                    "title": _as_text(raw_block.get("title")) or _as_text(raw_topic.get("title")),
                    "lead": _as_text(raw_block.get("lead")),
                }
            )
            continue
        if block_type == "text":
            paragraphs = _split_paragraphs(raw_block.get("body"))
            if paragraphs:
                blocks.append({"type": "text", "id": block_id, "title": _as_text(raw_block.get("title")), "paragraphs": paragraphs})
            continue
        if block_type == "rich_text":
            body = _as_text(raw_block.get("body"))
            if body:
                blocks.append(
                    {
                        "type": "rich_text",
                        "id": block_id,
                        "title": _as_text(raw_block.get("title")),
                        "body_html": _MARKDOWN_RENDERER.render(body),
                    }
                )
            continue
        if block_type == "image":
            src = _as_text(raw_block.get("src"))
            alt = _as_text(raw_block.get("alt"))
            if src:
                if not alt:
                    logger.warning(
                        "Teaching image block '%s' in %s/%s/%s is missing alt text.",
                        block_id,
                        teaching_lang,
                        ui_lang,
                        topic_slug,
                    )
                blocks.append(
                    {
                        "type": "image",
                        "id": block_id,
                        "src": src,
                        "alt": alt,
                        "caption": _as_text(raw_block.get("caption")),
                    }
                )
            continue
        if block_type in {"info_box", "tip_box", "warning_box"}:
            variant_map = {
                "info_box": "context",
                "tip_box": "tip",
                "warning_box": "regel",
            }
            body = _split_paragraphs(raw_block.get("body"))
            if body:
                blocks.append(
                    {
                        "type": "admonition",
                        "id": block_id,
                        "item": {
                            "id": block_id,
                            "variant": variant_map[block_type],
                            "title": _as_text(raw_block.get("title")),
                            "default_title": _as_text(raw_block.get("title")),
                            "body_paragraphs": body,
                            "collapsible": False,
                        },
                    }
                )
            continue
        if block_type == "audio_example":
            example = _audio_example_payload(teaching_lang, raw_block)
            if example["audio"] or example["transcript"]:
                blocks.append(
                    {
                        "type": "audio_example",
                        "id": block_id,
                        "title": _as_text(raw_block.get("title")),
                        "example": example,
                    }
                )
            continue
        if block_type == "audio_contrast":
            examples = [
                _audio_example_payload(teaching_lang, item)
                for item in raw_block.get("examples", [])
                if isinstance(item, dict)
            ]
            if examples:
                blocks.append(
                    {
                        "type": "audio_contrast",
                        "id": block_id,
                        "title": _as_text(raw_block.get("title")),
                        "examples": examples,
                    }
                )
            continue
        if block_type == "download":
            payload = _download_payload(raw_block)
            if payload["href"]:
                blocks.append({"type": "download", "id": block_id, "download": payload})
            continue
        if block_type == "credits":
            credits = raw_topic.get("credits") if isinstance(raw_topic.get("credits"), dict) else {}
            coordinator = _person_entries(credits.get("coordinator"))
            authors = _person_entries(credits.get("authors"))
            if coordinator or authors:
                blocks.append(
                    {
                        "type": "credits",
                        "id": block_id,
                        "groups": [
                            {"key": "coordinator", "title": translate(ui_lang, "teaching.credits.coordinator"), "people": coordinator},
                            {"key": "authors", "title": translate(ui_lang, "teaching.credits.authors"), "people": authors},
                        ],
                    }
                )
            continue
        if block_type == "next_topics":
            topic_slugs = [_as_text(value) for value in raw_block.get("topics", []) if _as_text(value)]
            cards = _build_topic_grid_cards(teaching_lang, ui_lang, topic_slugs)
            if cards:
                blocks.append({"type": "next_topics", "id": block_id, "title": _as_text(raw_block.get("title")), "cards": cards})
            continue
        if block_type == "topic_grid":
            topic_slugs = [_as_text(value) for value in raw_block.get("topics", []) if _as_text(value)]
            cards = _build_topic_grid_cards(teaching_lang, ui_lang, topic_slugs)
            if cards:
                blocks.append({"type": "topic_grid", "id": block_id, "title": _as_text(raw_block.get("title")), "cards": cards})
            continue
        if block_type == "video":
            src = _as_text(raw_block.get("src"))
            embed_url = _as_text(raw_block.get("embed_url"))
            if src or embed_url:
                blocks.append(
                    {
                        "type": "video",
                        "id": block_id,
                        "title": _as_text(raw_block.get("title")),
                        "src": src,
                        "embed_url": embed_url,
                        "caption": _as_text(raw_block.get("caption")),
                        "is_available": _public_asset_exists(src) if src else True,
                    }
                )
            continue

        logger.warning(
            "Ignoring unknown teaching block type '%s' in %s/%s/%s.",
            block_type,
            teaching_lang,
            ui_lang,
            topic_slug,
        )
    return blocks


def _hub_topic_cards(teaching_lang: str, ui_lang: str) -> list[dict[str, Any]]:
    index = load_teaching_index(teaching_lang, ui_lang) or {}
    cards: list[dict[str, Any]] = []
    for raw_topic in index.get("topics", []):
        if not isinstance(raw_topic, dict):
            continue
        topic_slug = _as_text(raw_topic.get("slug"))
        if not topic_slug or not topic_exists(teaching_lang, ui_lang, topic_slug):
            continue
        cards.append(
            {
                "slug": topic_slug,
                "title": _as_text(raw_topic.get("title")) or topic_slug,
                "summary": _as_text(raw_topic.get("summary")),
                "metadata": _topic_card_metadata(raw_topic),
                "href": url_for(
                    "public.teaching_language_page",
                    ui_lang=ui_lang,
                    language_slug=teaching_lang,
                    page_slug=topic_slug,
                ),
            }
        )
    return cards


@lru_cache(maxsize=None)
def load_teaching_manifest(teaching_lang: str) -> dict[str, Any] | None:
    data = _safe_yaml_map(_manifest_path(teaching_lang))
    if data is None:
        return None
    available_ui_langs = _normalize_ui_langs(data.get("available_ui_langs"))
    default_ui_lang = _as_text(data.get("default_ui_lang")).lower()
    return {
        **data,
        "teaching_lang": _as_text(data.get("teaching_lang")) or teaching_lang,
        "default_ui_lang": default_ui_lang,
        "available_ui_langs": available_ui_langs,
    }


def list_teaching_languages() -> list[str]:
    if not TEACHING_CONTENT_ROOT.exists():
        return []
    languages: list[str] = []
    for entry in sorted(TEACHING_CONTENT_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if load_teaching_manifest(entry.name) is not None:
            languages.append(entry.name)
    return languages


def list_existing_ui_editions(teaching_lang: str) -> list[str]:
    manifest = load_teaching_manifest(teaching_lang)
    if manifest is None:
        return []
    return [ui_lang for ui_lang in manifest["available_ui_langs"] if _index_path(teaching_lang, ui_lang).exists()]


def edition_exists(teaching_lang: str, ui_lang: str) -> bool:
    return ui_lang in list_existing_ui_editions(teaching_lang)


def resolve_teaching_edition_ui_lang(teaching_lang: str, requested_ui_lang: str) -> str | None:
    if edition_exists(teaching_lang, requested_ui_lang):
        return requested_ui_lang

    manifest = load_teaching_manifest(teaching_lang)
    if manifest is None:
        return None

    default_ui_lang = _as_text(manifest.get("default_ui_lang")).lower()
    if default_ui_lang and edition_exists(teaching_lang, default_ui_lang):
        return default_ui_lang

    editions = list_existing_ui_editions(teaching_lang)
    if editions:
        return editions[0]
    return None


@lru_cache(maxsize=None)
def load_teaching_index(teaching_lang: str, ui_lang: str) -> dict[str, Any] | None:
    return _safe_yaml_map(_index_path(teaching_lang, ui_lang))


@lru_cache(maxsize=None)
def load_teaching_topic(teaching_lang: str, ui_lang: str, topic_slug: str) -> dict[str, Any] | None:
    return _safe_yaml_map(_topic_path(teaching_lang, ui_lang, topic_slug))


def topic_exists(teaching_lang: str, ui_lang: str, topic_slug: str) -> bool:
    return load_teaching_topic(teaching_lang, ui_lang, topic_slug) is not None


def resolve_topic_slug_for_ui_lang(teaching_lang: str, current_ui_lang: str, topic_slug: str, target_ui_lang: str) -> str | None:
    if not edition_exists(teaching_lang, target_ui_lang):
        return None

    current_topic = load_teaching_topic(teaching_lang, current_ui_lang, topic_slug)
    if current_topic is not None:
        equivalents = current_topic.get("equivalents") if isinstance(current_topic.get("equivalents"), dict) else {}
        equivalent_slug = _as_text(equivalents.get(target_ui_lang))
        if equivalent_slug and topic_exists(teaching_lang, target_ui_lang, equivalent_slug):
            return equivalent_slug

    if topic_exists(teaching_lang, target_ui_lang, topic_slug):
        return topic_slug
    return None


def build_teaching_hub_page(ui_lang: str, teaching_lang: str) -> dict[str, Any] | None:
    effective_ui_lang = resolve_teaching_edition_ui_lang(teaching_lang, ui_lang)
    if effective_ui_lang is None:
        return None

    index = load_teaching_index(teaching_lang, effective_ui_lang)
    if index is None:
        return None

    title = _as_text(index.get("title")) or teaching_lang.replace("-", " ").title()
    lead = _as_text(index.get("lead"))
    topic_cards = _hub_topic_cards(teaching_lang, effective_ui_lang)
    return {
        "title": title,
        "intro": lead,
        "page_kind": "material",
        "layout": "teaching",
        "template": "pages/teaching_page.html",
        "teaching_view": "hub",
        "resolved_ui_lang": effective_ui_lang,
        "teaching_lang": teaching_lang,
        "topic_cards": topic_cards,
        "teaching_switch_items": _teaching_switch_items(effective_ui_lang, teaching_lang),
        "content_header": build_content_header(
            page_name="teaching",
            title=title,
            intro=lead,
            section_label=translate(effective_ui_lang, "section.teaching"),
            section_href=url_for("public.teaching_home", ui_lang=effective_ui_lang),
            context_mode="section",
            context_title=None,
            context_root_href=None,
            current_label=title,
        ),
        "feature_cards": [
            {
                "title": card["title"],
                "text": card["summary"],
                "href": card["href"],
                "link_label": translate(effective_ui_lang, "teaching.action.open_topic"),
                "variant": "selection",
            }
            for card in topic_cards
        ],
    }


def resolve_topic_route_target(teaching_lang: str, requested_ui_lang: str, topic_slug: str) -> dict[str, Any]:
    effective_ui_lang = resolve_teaching_edition_ui_lang(teaching_lang, requested_ui_lang)
    if effective_ui_lang is None:
        return {"status": "missing-language"}

    if effective_ui_lang != requested_ui_lang:
        if topic_exists(teaching_lang, effective_ui_lang, topic_slug):
            return {"status": "redirect-topic", "ui_lang": effective_ui_lang, "topic_slug": topic_slug}
        return {"status": "redirect-hub", "ui_lang": effective_ui_lang}

    if not topic_exists(teaching_lang, effective_ui_lang, topic_slug):
        return {"status": "redirect-hub", "ui_lang": effective_ui_lang}

    return {"status": "ok", "ui_lang": effective_ui_lang, "topic_slug": topic_slug}


def build_teaching_topic_page(ui_lang: str, teaching_lang: str, topic_slug: str) -> dict[str, Any] | None:
    raw_topic = load_teaching_topic(teaching_lang, ui_lang, topic_slug)
    index = load_teaching_index(teaching_lang, ui_lang)
    if raw_topic is None or index is None:
        return None

    title = _as_text(raw_topic.get("title")) or topic_slug.replace("-", " ").title()
    description = _as_text(raw_topic.get("description"))
    hub_title = _as_text(index.get("title")) or teaching_lang.replace("-", " ").title()
    return {
        "title": title,
        "intro": description,
        "page_kind": "material",
        "layout": "teaching",
        "template": "pages/teaching_page.html",
        "teaching_view": "topic",
        "resolved_ui_lang": ui_lang,
        "teaching_lang": teaching_lang,
        "topic_slug": topic_slug,
        "hub_title": hub_title,
        "hub_href": url_for("public.teaching_language_root", ui_lang=ui_lang, language_slug=teaching_lang),
        "back_link": {
            "label": translate(ui_lang, "teaching.action.back_to_hub"),
            "href": url_for("public.teaching_language_root", ui_lang=ui_lang, language_slug=teaching_lang),
        },
        "teaching_switch_items": _teaching_switch_items(ui_lang, teaching_lang, topic_slug=topic_slug),
        "blocks": _topic_blocks(teaching_lang, ui_lang, topic_slug, raw_topic),
        "content_header": build_content_header(
            page_name="teaching",
            title=title,
            intro=description,
            section_label=translate(ui_lang, "section.teaching"),
            section_href=url_for("public.teaching_home", ui_lang=ui_lang),
            context_mode="section",
            context_title=None,
            context_root_href=None,
            ancestors=[{"label": hub_title, "href": url_for("public.teaching_language_root", ui_lang=ui_lang, language_slug=teaching_lang)}],
            current_label=title,
        ),
    }


def resolve_teaching_switch_path(current_path: str, target_ui_lang: str) -> str | None:
    parts = [segment for segment in current_path.strip("/").split("/") if segment]
    if len(parts) < 2 or parts[1] != "teaching":
        return None

    if len(parts) == 2:
        return f"/{target_ui_lang}/teaching"

    teaching_lang = parts[2]
    if not edition_exists(teaching_lang, target_ui_lang):
        return None

    if len(parts) == 3:
        return f"/{target_ui_lang}/teaching/{teaching_lang}"

    topic_slug = parts[3]
    target_topic_slug = resolve_topic_slug_for_ui_lang(teaching_lang, parts[0], topic_slug, target_ui_lang)
    if target_topic_slug:
        return f"/{target_ui_lang}/teaching/{teaching_lang}/{target_topic_slug}"
    return f"/{target_ui_lang}/teaching/{teaching_lang}"