"""Date-based public Teaching content for PROMAT."""

from __future__ import annotations

from datetime import date
from html import escape
from html.parser import HTMLParser
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

_TOPIC_MEDIA_TYPES = frozenset({"audio", "downloads", "images", "video"})
_DATAWRAPPER_EMBED_HOST = "datawrapper.dwcdn.net"


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


def render_markdown_block(value: Any) -> str:
    text = _as_text(value)
    if not text:
        return ""
    return _MARKDOWN_RENDERER.render(text).strip()


def render_markdown_blocks(value: Any) -> list[str]:
    return [
        render_markdown_block(block)
        for block in _split_paragraphs(value)
        if block.strip()
    ]


def render_markdown_inline(value: Any) -> str:
    text = _as_text(value)
    if not text:
        return ""
    return _MARKDOWN_RENDERER.renderInline(text).strip()


class _MarkdownPlainTextParser(HTMLParser):
    _BLOCK_TAGS = {"p", "div", "ul", "ol", "li", "blockquote", "pre", "br"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def _append_newline(self) -> None:
        if not self.parts or self.parts[-1].endswith("\n"):
            return
        self.parts.append("\n")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "li":
            self._append_newline()
            self.parts.append("- ")
            return
        if tag == "br":
            self._append_newline()
            return
        if tag in self._BLOCK_TAGS:
            self._append_newline()

    def handle_endtag(self, tag: str) -> None:
        if tag in self._BLOCK_TAGS:
            self._append_newline()

    def handle_data(self, data: str) -> None:
        if data:
            self.parts.append(data)

    def text_content(self) -> str:
        normalized_lines: list[str] = []
        previous_blank = False
        for raw_line in "".join(self.parts).replace("\xa0", " ").splitlines():
            line = " ".join(raw_line.split())
            if line:
                normalized_lines.append(line)
                previous_blank = False
                continue
            if normalized_lines and not previous_blank:
                normalized_lines.append("")
                previous_blank = True
        return "\n".join(normalized_lines).strip()


def render_markdown_plain_text(value: Any) -> str:
    rendered = render_markdown_block(value)
    if not rendered:
        return ""
    parser = _MarkdownPlainTextParser()
    parser.feed(rendered)
    parser.close()
    return parser.text_content()


def _markdown_blocks(value: Any) -> list[str]:
    return render_markdown_blocks(value)


def _markdown_inline(value: Any) -> str:
    return render_markdown_inline(value)


def _set_inline_markdown_fields(payload: dict[str, Any], *fields: str) -> dict[str, Any]:
    for field in fields:
        text = _as_text(payload.get(field))
        payload[field] = text
        payload[f"{field}_html"] = render_markdown_inline(text)
    return payload


def _text_entries(values: Any) -> list[str]:
    entries: list[str] = []
    if not isinstance(values, list):
        return entries
    for item in values:
        if isinstance(item, dict):
            text = _as_text(item.get("name") or item.get("label") or item.get("text"))
        else:
            text = _as_text(item)
        if text and text not in entries:
            entries.append(text)
    return entries


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
    load_teaching_media_manifest.cache_clear()


def _manifest_path(teaching_lang: str) -> Path:
    return TEACHING_CONTENT_ROOT / teaching_lang / "teaching.yaml"


def _hub_path(teaching_lang: str, ui_lang: str) -> Path:
    return TEACHING_CONTENT_ROOT / teaching_lang / "hubs" / f"{ui_lang}.yaml"


def _index_path(teaching_lang: str, ui_lang: str) -> Path:
    return _hub_path(teaching_lang, ui_lang)


def _topic_dir(teaching_lang: str, topic_slug: str) -> Path:
    return TEACHING_CONTENT_ROOT / teaching_lang / topic_slug


def _topic_locale_path(teaching_lang: str, ui_lang: str, topic_slug: str) -> Path:
    return _topic_dir(teaching_lang, topic_slug) / f"{ui_lang}.yaml"


def _topic_path(teaching_lang: str, ui_lang: str, topic_slug: str) -> Path:
    return _topic_locale_path(teaching_lang, ui_lang, topic_slug)


def _media_manifest_path(teaching_lang: str, topic_slug: str) -> Path:
    return _topic_dir(teaching_lang, topic_slug) / "media.yaml"


def _topic_media_root(teaching_lang: str, topic_slug: str) -> Path:
    return _topic_dir(teaching_lang, topic_slug) / "media"


def _normalize_ui_langs(values: Any) -> list[str]:
    normalized: list[str] = []
    if not isinstance(values, list):
        return normalized
    for value in values:
        candidate = _as_text(value).lower()
        if candidate and candidate not in normalized:
            normalized.append(candidate)
    return normalized


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


def _hub_overview_intro(index: dict[str, Any]) -> str:
    return _as_text(index.get("overview_intro") or index.get("hub_intro") or index.get("orientation"))


def _normalize_topic_reference(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        slug = _as_text(value.get("slug"))
        if not slug:
            return None
        return {**value, "slug": slug}

    slug = _as_text(value)
    if not slug:
        return None
    return {"slug": slug}


def _hub_group_entries(index: dict[str, Any]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []

    if isinstance(index.get("groups"), list):
        for raw_group in index["groups"]:
            if not isinstance(raw_group, dict):
                continue
            topic_refs = [
                reference
                for raw_topic in raw_group.get("topics", [])
                for reference in [_normalize_topic_reference(raw_topic)]
                if reference is not None
            ]
            groups.append(
                {
                    "title": _as_text(raw_group.get("title")),
                    "description": _as_text(raw_group.get("description") or raw_group.get("intro")),
                    "topics": topic_refs,
                }
            )

    if groups:
        return groups

    flat_topics = [
        reference
        for raw_topic in index.get("topics", [])
        for reference in [_normalize_topic_reference(raw_topic)]
        if reference is not None
    ]
    if not flat_topics:
        return []
    return [{"title": "", "description": "", "topics": flat_topics}]


def _hub_topic_entries(index: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for group in _hub_group_entries(index):
        for entry in group["topics"]:
            topic_slug = _as_text(entry.get("slug"))
            if not topic_slug or topic_slug in seen:
                continue
            entries.append(entry)
            seen.add(topic_slug)
    return entries


def _explicit_public_availability(entry: dict[str, Any] | None) -> bool | None:
    if not isinstance(entry, dict):
        return None
    for key in ("is_available", "is_public", "published"):
        if key not in entry:
            continue
        value = entry.get(key)
        if isinstance(value, bool):
            return value
        normalized = _as_text(value).lower()
        if normalized in {"true", "yes", "1", "published", "public", "ready"}:
            return True
        if normalized in {"false", "no", "0", "draft", "private", "pending", "planned"}:
            return False
    return None


def _topic_author_names(raw_topic: dict[str, Any]) -> list[str]:
    authors = _text_entries(_topic_metadata_source(raw_topic).get("authors"))
    if authors:
        return authors

    credits = raw_topic.get("credits") if isinstance(raw_topic.get("credits"), dict) else {}
    return [person["name"] for person in _person_entries(credits.get("authors"))]


def _topic_card_byline(ui_lang: str, raw_topic: dict[str, Any]) -> str:
    authors = _topic_author_names(raw_topic)
    if not authors:
        return ""
    return translate(ui_lang, "teaching.topic.byline", authors=", ".join(authors))


def topic_is_public(
    teaching_lang: str,
    ui_lang: str,
    topic_slug: str,
    entry: dict[str, Any] | None = None,
    raw_topic: dict[str, Any] | None = None,
) -> bool:
    explicit_values = [
        _explicit_public_availability(source)
        for source in (entry, raw_topic)
        if isinstance(source, dict)
    ]
    if any(value is False for value in explicit_values):
        return False
    exists = raw_topic is not None if raw_topic is not None else topic_exists(teaching_lang, ui_lang, topic_slug)
    if any(value is True for value in explicit_values):
        return exists
    return exists


def resolve_teaching_topic_media_artifact(
    teaching_lang: str,
    topic_slug: str,
    media_type: str,
    filename: str,
) -> Path | None:
    if media_type not in _TOPIC_MEDIA_TYPES:
        return None

    normalized_filename = _as_text(filename).replace("\\", "/")
    if not normalized_filename:
        return None

    parsed = urlparse(normalized_filename)
    if parsed.scheme or normalized_filename.startswith("/"):
        return None

    relative_path = Path(normalized_filename)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return None

    media_root = (_topic_media_root(teaching_lang, topic_slug) / media_type).resolve()
    candidate = (media_root / relative_path).resolve()
    try:
        candidate.relative_to(media_root)
    except ValueError:
        return None

    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate


def _resolve_topic_media_url(teaching_lang: str, topic_slug: str, media_type: str, value: Any) -> str:
    candidate = _as_text(value).replace("\\", "/")
    if not candidate:
        return ""

    parsed = urlparse(candidate)
    if parsed.scheme in {"http", "https"} or candidate.startswith("/"):
        return candidate

    artifact = resolve_teaching_topic_media_artifact(teaching_lang, topic_slug, media_type, candidate)
    if artifact is None:
        return ""

    return url_for(
        "public.teaching_topic_media",
        teaching_lang=teaching_lang,
        topic_slug=topic_slug,
        media_type=media_type,
        filename=candidate,
    )


def _topic_media_is_available(teaching_lang: str, topic_slug: str, media_type: str, value: Any) -> bool:
    candidate = _as_text(value).replace("\\", "/")
    if not candidate:
        return False
    parsed = urlparse(candidate)
    if parsed.scheme in {"http", "https"} or candidate.startswith("/"):
        return True
    return resolve_teaching_topic_media_artifact(teaching_lang, topic_slug, media_type, candidate) is not None


def _hub_topic_card(
    teaching_lang: str,
    ui_lang: str,
    topic_slug: str,
    raw_entry: dict[str, Any] | None,
    *,
    include_unavailable: bool = False,
) -> dict[str, Any] | None:
    if not topic_slug:
        return None

    raw_topic = load_teaching_topic(teaching_lang, ui_lang, topic_slug)
    if raw_topic is None:
        return None

    is_available = topic_is_public(teaching_lang, ui_lang, topic_slug, raw_entry, raw_topic)
    if not is_available and not include_unavailable:
        return None

    return _set_inline_markdown_fields({
        "slug": topic_slug,
        "title": _as_text(raw_topic.get("title")) or topic_slug,
        "summary": _as_text(raw_topic.get("summary") or raw_topic.get("description")),
        "byline": _topic_card_byline(ui_lang, raw_topic),
        "metadata": _topic_card_metadata(raw_topic),
        "href": url_for(
            "public.teaching_language_page",
            ui_lang=ui_lang,
            language_slug=teaching_lang,
            page_slug=topic_slug,
        ) if is_available else "",
        "is_available": is_available,
    }, "title", "summary", "byline")


def _audio_example_payload(
    teaching_lang: str,
    topic_slug: str,
    raw_item: dict[str, Any],
    *,
    inherited_transcript: str = "",
) -> dict[str, Any]:
    audio_url = _resolve_topic_media_url(teaching_lang, topic_slug, "audio", raw_item.get("audio"))
    is_available = _topic_media_is_available(teaching_lang, topic_slug, "audio", raw_item.get("audio"))
    transcript = _as_text(raw_item.get("transcript")) or inherited_transcript
    note = _as_text(raw_item.get("note"))
    return _set_inline_markdown_fields({
        "label": _as_text(raw_item.get("label")) or _as_text(raw_item.get("title")),
        "title": _as_text(raw_item.get("title")),
        "subtitle": _as_text(raw_item.get("subtitle")),
        "audio": audio_url if is_available else "",
        "transcript": transcript,
        "transcript_html": _markdown_inline(transcript),
        "note": note,
        "note_html": _markdown_inline(note),
        "source": _audio_source_payload(raw_item.get("source")),
        "speaker_id": _as_text(raw_item.get("speaker_id")),
        "token_id": _as_text(raw_item.get("token_id") or raw_item.get("speaker_id")),
        "segments": [
            {"text": _as_text(segment.get("text"))}
            for segment in raw_item.get("segments", [])
            if isinstance(segment, dict) and _as_text(segment.get("text"))
        ],
        "is_available": is_available,
        "teaching_lang": teaching_lang,
        "topic_slug": topic_slug,
    }, "label", "title", "subtitle")


def _audio_source_payload(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        label = _as_text(value.get("label") or value.get("title") or value.get("name") or value.get("url"))
        url = _as_text(value.get("url"))
        return _set_inline_markdown_fields({
            "label": label,
            "url": url,
        }, "label")

    label = _as_text(value)
    return _set_inline_markdown_fields({
        "label": label,
        "url": "",
    }, "label")


def _download_payload(teaching_lang: str, topic_slug: str, raw_block: dict[str, Any]) -> dict[str, Any]:
    raw_href = _as_text(raw_block.get("href") or raw_block.get("url") or raw_block.get("file"))
    href = _resolve_topic_media_url(teaching_lang, topic_slug, "downloads", raw_href)
    return _set_inline_markdown_fields({
        "title": _as_text(raw_block.get("title")),
        "label": _as_text(raw_block.get("label")) or raw_href.rsplit("/", 1)[-1],
        "href": href,
        "description": _as_text(raw_block.get("description")),
        "is_available": _topic_media_is_available(teaching_lang, topic_slug, "downloads", raw_href),
    }, "title", "label", "description")


def _embed_height(value: Any, *, default: int = 540) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value if value > 0 else default
    raw_value = _as_text(value)
    if raw_value.isdigit():
        parsed = int(raw_value)
        return parsed if parsed > 0 else default
    return default


def _normalize_datawrapper_src(value: Any) -> str | None:
    raw_value = _as_text(value)
    if not raw_value:
        return None

    parsed = urlparse(raw_value)
    if parsed.scheme != "https":
        return None
    if parsed.hostname != _DATAWRAPPER_EMBED_HOST:
        return None
    if parsed.port is not None or parsed.username or parsed.password:
        return None
    if parsed.query or parsed.fragment or parsed.params:
        return None

    segments = [segment for segment in parsed.path.split("/") if segment]
    if len(segments) < 2 or any(segment in {".", ".."} for segment in segments):
        return None

    normalized_path = "/" + "/".join(segments) + "/"
    return f"https://{_DATAWRAPPER_EMBED_HOST}{normalized_path}"


def _embed_payload(raw_block: dict[str, Any]) -> dict[str, Any] | None:
    provider = _as_text(raw_block.get("provider")).lower()
    src = _normalize_datawrapper_src(raw_block.get("src"))
    if provider != "datawrapper" or not src:
        return None
    payload = _set_inline_markdown_fields({
        "provider": provider,
        "src": src,
        "height": _embed_height(raw_block.get("height")),
        "title": _as_text(raw_block.get("title")),
        "caption": _as_text(raw_block.get("caption")),
    }, "title", "caption")
    payload["title_plain"] = render_markdown_plain_text(payload["title"]) or payload["title"]
    return payload


_BLOCK_LAYOUT_SPAN_DEFAULTS: dict[str, int] = {
    "hero": 2,
    "section_heading": 2,
    "text": 2,
    "rich_text": 2,
    "image": 1,
    "topic_meta": 2,
    "overview": 1,
    "info_box": 1,
    "tip_box": 1,
    "warning_box": 1,
    "audio_example": 1,
    "audio_examples": 2,
    "audio_contrast": 2,
    "download": 1,
    "embed": 2,
    "video": 2,
    "further_reading": 2,
    "credits": 2,
    "next_topics": 2,
    "topic_grid": 2,
    "citation": 2,
}


def _block_layout_span(block_type: str, raw_block: dict[str, Any]) -> int:
    default_span = _BLOCK_LAYOUT_SPAN_DEFAULTS.get(block_type, 2)
    raw_layout = raw_block.get("layout")
    if not isinstance(raw_layout, dict):
        return default_span

    raw_span = raw_layout.get("span")
    if isinstance(raw_span, bool):
        return default_span
    if isinstance(raw_span, int):
        if raw_span in {1, 2}:
            return raw_span
        if raw_span == 3:
            return 2
        return default_span

    raw_span_text = _as_text(raw_span)
    if raw_span_text in {"1", "2"}:
        return int(raw_span_text)
    if raw_span_text == "3":
        return 2
    return default_span


def _block_layout_payload(block_type: str, raw_block: dict[str, Any]) -> dict[str, int]:
    return {"span": _block_layout_span(block_type, raw_block)}


def _parse_iso_date(value: Any) -> date | None:
    raw_value = _as_text(value)
    if not raw_value:
        return None
    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        logger.warning("Ignoring invalid teaching topic date value '%s'.", raw_value)
        return None


def _format_topic_date(ui_lang: str, value: Any) -> str:
    parsed = _parse_iso_date(value)
    if parsed is None:
        return ""
    if ui_lang == "de":
        return parsed.strftime("%d.%m.%Y")
    return parsed.isoformat()


def _topic_metadata_source(raw_topic: dict[str, Any]) -> dict[str, Any]:
    metadata = raw_topic.get("metadata")
    if isinstance(metadata, dict):
        return metadata
    return raw_topic


def _topic_metadata(ui_lang: str, raw_topic: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {"authors": None, "details": []}
    metadata_source = _topic_metadata_source(raw_topic)
    authors = _text_entries(metadata_source.get("authors"))
    if not authors:
        credits = raw_topic.get("credits") if isinstance(raw_topic.get("credits"), dict) else {}
        authors = [person["name"] for person in _person_entries(credits.get("authors"))]
    if authors:
        metadata["authors"] = {
            "key": "authors",
            "label": translate(ui_lang, "teaching.topic.authors"),
            "value": ", ".join(authors),
        }

    peer_review = _text_entries(metadata_source.get("peer_review"))
    if peer_review:
        metadata["details"].append(
            {
                "key": "peer_review",
                "label": translate(ui_lang, "teaching.topic.peer_review"),
                "value": ", ".join(peer_review),
            }
        )

    created = _format_topic_date(ui_lang, metadata_source.get("created"))
    if created:
        metadata["details"].append(
            {
                "key": "created",
                "label": translate(ui_lang, "teaching.topic.created"),
                "value": created,
            }
        )

    updated = _format_topic_date(ui_lang, metadata_source.get("updated"))
    if updated:
        metadata["details"].append(
            {
                "key": "updated",
                "label": translate(ui_lang, "teaching.topic.updated"),
                "value": updated,
            }
        )

    return metadata


def _has_topic_metadata(metadata: dict[str, Any]) -> bool:
    return bool(metadata.get("authors") or metadata.get("details"))


def _link_entries(values: Any) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    if not isinstance(values, list):
        return entries
    for item in values:
        if not isinstance(item, dict):
            continue
        label = _as_text(item.get("label"))
        href = _as_text(item.get("href"))
        if label and href:
            entries.append(_set_inline_markdown_fields({"label": label, "href": href}, "label"))
    return entries


def _overview_item_entries(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [item_text for item in values if (item_text := _as_text(item))]


def _markdown_list_block(items: list[str]) -> str | None:
    if not items:
        return None
    return render_markdown_block("\n".join(f"- {item}" for item in items))


def _further_reading_item_entries(values: Any) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    if not isinstance(values, list):
        return entries
    for item in values:
        if not isinstance(item, dict):
            continue
        title = _as_text(item.get("title"))
        text = _as_text(item.get("text"))
        cta = _as_text(item.get("cta"))
        href = _as_text(item.get("href"))
        if title and text and cta and href:
            entries.append(_set_inline_markdown_fields({"title": title, "text": text, "cta": cta, "href": href}, "title", "text", "cta"))
    return entries


def _citation_payload(ui_lang: str, value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    text = _as_text(value.get("text"))
    doi = _as_text(value.get("doi"))
    url = _as_text(value.get("url"))
    if not any((text, doi, url)):
        return None
    body_html_blocks = render_markdown_blocks(text)
    copy_text = _as_text(value.get("copy_text"))
    if not copy_text:
        copy_parts: list[str] = []
        plain_text = render_markdown_plain_text(text)
        if plain_text:
            copy_parts.append(plain_text)
        if doi and doi not in plain_text:
            copy_parts.append(doi)
        if url and url not in plain_text:
            copy_parts.append(url)
        copy_text = "\n".join(copy_parts)
    meta_rows: list[str] = []
    if doi:
        meta_rows.append(
            "".join(
                (
                    '<div class="pm-teaching-citation__meta-item">',
                    f'<dt class="pm-teaching-citation__label">{escape(translate(ui_lang, "teaching.citation.doi"))}</dt>',
                    f'<dd class="pm-teaching-citation__value">{escape(doi)}</dd>',
                    "</div>",
                )
            )
        )
    if url:
        safe_url = escape(url, quote=True)
        meta_rows.append(
            "".join(
                (
                    '<div class="pm-teaching-citation__meta-item">',
                    f'<dt class="pm-teaching-citation__label">{escape(translate(ui_lang, "teaching.citation.url"))}</dt>',
                    '<dd class="pm-teaching-citation__value">',
                    f'<a href="{safe_url}" class="pm-teaching-inline-link">{safe_url}</a>',
                    "</dd>",
                    "</div>",
                )
            )
        )
    if meta_rows:
        body_html_blocks.append(f'<dl class="pm-teaching-citation__meta">{"".join(meta_rows)}</dl>')
    payload = _set_inline_markdown_fields({
        "title": _as_text(value.get("title")) or translate(ui_lang, "teaching.citation.heading"),
        "text": text,
        "doi": doi,
        "url": url,
        "copy_text": copy_text,
        "body_html_blocks": body_html_blocks,
    }, "title")
    return payload


def _decorate_content_header_markdown(content_header: dict[str, Any], *, title: str, intro: str) -> dict[str, Any]:
    content_header["title_html"] = render_markdown_inline(title)
    content_header["intro_html"] = render_markdown_inline(intro)
    return content_header


def _topic_page_intro(raw_topic: dict[str, Any]) -> str:
    for raw_block in raw_topic.get("blocks", []):
        if not isinstance(raw_block, dict) or _as_text(raw_block.get("type")) != "hero":
            continue
        hero_lead = _as_text(raw_block.get("lead"))
        if hero_lead:
            return hero_lead
        break
    return _as_text(raw_topic.get("description"))


def _build_topic_grid_cards(teaching_lang: str, ui_lang: str, topic_slugs: list[str]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for topic_slug in topic_slugs:
        raw_topic = load_teaching_topic(teaching_lang, ui_lang, topic_slug)
        if raw_topic is None or not topic_is_public(teaching_lang, ui_lang, topic_slug, raw_topic=raw_topic):
            continue
        cards.append(
            _set_inline_markdown_fields({
                "slug": topic_slug,
                "title": _as_text(raw_topic.get("title")) or topic_slug,
                "summary": _as_text(raw_topic.get("summary") or raw_topic.get("description")),
                "byline": _topic_card_byline(ui_lang, raw_topic),
                "metadata": _topic_card_metadata(raw_topic),
                "href": url_for(
                    "public.teaching_language_page",
                    ui_lang=ui_lang,
                    language_slug=teaching_lang,
                    page_slug=topic_slug,
                ),
                "is_available": True,
            }, "title", "summary", "byline")
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


def _topic_blocks(
    teaching_lang: str,
    ui_lang: str,
    topic_slug: str,
    raw_topic: dict[str, Any],
    topic_metadata: dict[str, Any],
) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    top_level_citation = _citation_payload(ui_lang, raw_topic.get("citation"))
    for index, raw_block in enumerate(raw_topic.get("blocks", [])):
        if not isinstance(raw_block, dict):
            continue
        block_type = _as_text(raw_block.get("type"))
        block_id = f"{topic_slug}-block-{index + 1}"
        if block_type == "hero":
            continue
        if block_type == "section_heading":
            title = _as_text(raw_block.get("title"))
            if title:
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "section_heading",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": title,
                        "lead": _as_text(raw_block.get("lead")),
                    }, "title", "lead")
                )
            continue

        if block_type == "overview":
            list_block = _markdown_list_block(_overview_item_entries(raw_block.get("items")))
            if list_block:
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "overview",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": _as_text(raw_block.get("title")),
                        "body_html_blocks": [list_block],
                    }, "title")
                )
            continue


        if block_type == "text":
            body_html_blocks = _markdown_blocks(raw_block.get("body"))
            if body_html_blocks:
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "text",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": _as_text(raw_block.get("title")),
                        "body_html_blocks": body_html_blocks,
                    }, "title")
                )
            continue
        if block_type == "rich_text":
            body = _as_text(raw_block.get("body"))
            if body:
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "rich_text",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": _as_text(raw_block.get("title")),
                        "variant": _as_text(raw_block.get("variant")),
                        "body_html": render_markdown_block(body),
                    }, "title")
                )
            continue
        if block_type == "image":
            src = _resolve_topic_media_url(teaching_lang, topic_slug, "images", raw_block.get("src"))
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
                    _set_inline_markdown_fields({
                        "type": "image",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "src": src,
                        "alt": alt,
                        "caption": _as_text(raw_block.get("caption")),
                    }, "caption")
                )
            continue
        if block_type == "embed":
            payload = _embed_payload(raw_block)
            if payload is not None:
                blocks.append(
                    {
                        "type": "embed",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "provider": payload["provider"],
                        "src": payload["src"],
                        "height": payload["height"],
                        "title": payload["title"],
                        "title_html": payload["title_html"],
                        "title_plain": payload["title_plain"],
                        "caption": payload["caption"],
                        "caption_html": payload["caption_html"],
                    }
                )
            elif _as_text(raw_block.get("provider")):
                raw_provider = _as_text(raw_block.get("provider")).lower()
                if raw_provider == "datawrapper" and _as_text(raw_block.get("src")):
                    logger.warning(
                        "Ignoring invalid teaching datawrapper src '%s' in %s/%s/%s.",
                        _as_text(raw_block.get("src")),
                        teaching_lang,
                        ui_lang,
                        topic_slug,
                    )
                else:
                    logger.warning(
                        "Ignoring unsupported teaching embed provider '%s' in %s/%s/%s.",
                        _as_text(raw_block.get("provider")),
                        teaching_lang,
                        ui_lang,
                        topic_slug,
                    )
            continue
        if block_type in {"info_box", "tip_box", "warning_box"}:
            variant_map = {
                "info_box": "context",
                "tip_box": "tip",
                "warning_box": "regel",
            }
            body = _split_paragraphs(raw_block.get("body"))
            body_html_blocks = _markdown_blocks(raw_block.get("body"))
            if body or body_html_blocks:
                blocks.append(
                    {
                        "type": "admonition",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "item": _set_inline_markdown_fields({
                            "id": block_id,
                            "variant": variant_map[block_type],
                            "title": _as_text(raw_block.get("title")),
                            "default_title": _as_text(raw_block.get("title")),
                            "body_paragraphs": body,
                            "body_html_blocks": body_html_blocks,
                        }, "title", "default_title"),
                    }
                )
            continue
        if block_type == "topic_meta":
            if _has_topic_metadata(topic_metadata):
                continue
            continue
        if block_type == "audio_example":
            example = _audio_example_payload(
                teaching_lang,
                topic_slug,
                raw_block,
                inherited_transcript=_as_text(raw_block.get("transcript")),
            )
            block_source = _audio_source_payload(raw_block.get("source"))
            if any((example["label"], example["title"], example["audio"], example["transcript"], example["note"], example["token_id"], example["segments"])):
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "audio_examples",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": _as_text(raw_block.get("title")),
                        "lead": _as_text(raw_block.get("lead")),
                        "lead_html": _markdown_inline(raw_block.get("lead")),
                        "source": block_source,
                        "examples": [example],
                    }, "title", "lead")
                )
            continue
        if block_type == "audio_examples":
            inherited_transcript = _as_text(raw_block.get("transcript"))
            block_source = _audio_source_payload(raw_block.get("source"))
            examples = [
                _audio_example_payload(
                    teaching_lang,
                    topic_slug,
                    item,
                    inherited_transcript=inherited_transcript,
                )
                for item in raw_block.get("examples", [])
                if isinstance(item, dict)
            ]
            examples = [
                example
                for example in examples
                if any((example["label"], example["title"], example["audio"], example["transcript"], example["note"], example["token_id"], example["segments"]))
            ]
            if examples:
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "audio_examples",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": _as_text(raw_block.get("title")),
                        "lead": _as_text(raw_block.get("lead")),
                        "lead_html": _markdown_inline(raw_block.get("lead")),
                        "source": block_source,
                        "examples": examples,
                    }, "title", "lead")
                )
            continue
        if block_type == "audio_contrast":
            inherited_transcript = _as_text(raw_block.get("transcript"))
            examples = [
                _audio_example_payload(
                    teaching_lang,
                    topic_slug,
                    item,
                    inherited_transcript=inherited_transcript,
                )
                for item in raw_block.get("examples", [])
                if isinstance(item, dict)
            ]
            if examples:
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "audio_contrast",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": _as_text(raw_block.get("title")),
                        "lead": _as_text(raw_block.get("lead")),
                        "lead_html": _markdown_inline(raw_block.get("lead")),
                        "transcript": inherited_transcript,
                        "transcript_html": _markdown_inline(inherited_transcript),
                        "examples": examples,
                    }, "title", "lead")
                )
            continue
        if block_type == "download":
            payload = _download_payload(teaching_lang, topic_slug, raw_block)
            if payload["href"]:
                blocks.append(
                    {
                        "type": "download",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "download": payload,
                    }
                )
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
                        "layout": _block_layout_payload(block_type, raw_block),
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
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "next_topics",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": _as_text(raw_block.get("title")),
                        "cards": cards,
                    }, "title")
                )
            continue
        if block_type == "topic_grid":
            topic_slugs = [_as_text(value) for value in raw_block.get("topics", []) if _as_text(value)]
            cards = _build_topic_grid_cards(teaching_lang, ui_lang, topic_slugs)
            if cards:
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "topic_grid",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": _as_text(raw_block.get("title")),
                        "cards": cards,
                    }, "title")
                )
            continue
        if block_type == "video":
            raw_src = _as_text(raw_block.get("src"))
            src = _resolve_topic_media_url(teaching_lang, topic_slug, "video", raw_src)
            embed_url = _as_text(raw_block.get("embed_url"))
            if src or embed_url:
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "video",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": _as_text(raw_block.get("title")),
                        "title_plain": render_markdown_plain_text(raw_block.get("title")) or _as_text(raw_block.get("title")),
                        "src": src,
                        "embed_url": embed_url,
                        "caption": _as_text(raw_block.get("caption")),
                        "is_available": _topic_media_is_available(teaching_lang, topic_slug, "video", raw_src) if src else True,
                    }, "title", "caption")
                )
            continue
        if block_type == "further_reading":
            items = _further_reading_item_entries(raw_block.get("items"))
            links = _link_entries(raw_block.get("links"))
            body_html_blocks = _markdown_blocks(raw_block.get("body"))
            if body_html_blocks or links or items:
                blocks.append(
                    _set_inline_markdown_fields({
                        "type": "further_reading",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "title": _as_text(raw_block.get("title")),
                        "description": _as_text(raw_block.get("description")),
                        "description_html": _markdown_inline(raw_block.get("description")),
                        "body_html_blocks": body_html_blocks,
                        "items": items,
                        "links": links,
                    }, "title")
                )
            continue
        if block_type == "citation":
            if top_level_citation is not None:
                if os.getenv("FLASK_ENV") == "development":
                    logger.warning(
                        "Ignoring explicit teaching citation block '%s' in %s/%s/%s because top-level citation metadata is present.",
                        block_id,
                        teaching_lang,
                        ui_lang,
                        topic_slug,
                    )
                continue
            citation = _citation_payload(ui_lang, raw_block)
            if citation is not None:
                blocks.append(
                    {
                        "type": "citation",
                        "id": block_id,
                        "layout": _block_layout_payload(block_type, raw_block),
                        "citation": citation,
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

    if top_level_citation is not None:
        blocks.append(
            {
                "type": "citation",
                "id": f"{topic_slug}-block-citation",
                "layout": {"span": _BLOCK_LAYOUT_SPAN_DEFAULTS["citation"]},
                "citation": top_level_citation,
            }
        )
    return blocks


def _topic_sections(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current_section: dict[str, Any] | None = None

    def _append_current_section() -> None:
        nonlocal current_section
        if current_section is None:
            return
        if current_section.get("heading") or current_section.get("blocks"):
            sections.append(current_section)
        current_section = None

    for block in blocks:
        block_type = _as_text(block.get("type"))
        if block_type == "section_heading":
            _append_current_section()
            current_section = {
                "kind": "section",
                "heading": block,
                "blocks": [],
            }
            continue

        if block_type in {"next_topics", "topic_grid", "further_reading", "citation"}:
            _append_current_section()
            sections.append(
                {
                    "kind": block_type,
                    "heading": None,
                    "blocks": [block],
                }
            )
            continue

        if current_section is None:
            current_section = {
                "kind": "intro",
                "heading": None,
                "blocks": [],
            }
        current_section["blocks"].append(block)

    _append_current_section()
    return sections


def _hub_topic_cards(teaching_lang: str, ui_lang: str, *, include_unavailable: bool = False) -> list[dict[str, Any]]:
    index = load_teaching_index(teaching_lang, ui_lang) or {}
    cards: list[dict[str, Any]] = []
    for entry in _hub_topic_entries(index):
        topic_slug = _as_text(entry.get("slug"))
        card = _hub_topic_card(
            teaching_lang,
            ui_lang,
            topic_slug,
            entry,
            include_unavailable=include_unavailable,
        )
        if card is not None:
            cards.append(card)
    return cards


def _hub_topic_groups(teaching_lang: str, ui_lang: str) -> list[dict[str, Any]]:
    index = load_teaching_index(teaching_lang, ui_lang) or {}
    groups: list[dict[str, Any]] = []

    for raw_group in _hub_group_entries(index):
        cards: list[dict[str, Any]] = []
        for raw_topic in raw_group["topics"]:
            topic_slug = _as_text(raw_topic.get("slug"))
            card = _hub_topic_card(
                teaching_lang,
                ui_lang,
                topic_slug,
                raw_topic,
                include_unavailable=True,
            )
            if card is not None:
                cards.append(card)
        if cards:
            groups.append(
                _set_inline_markdown_fields({
                    "title": raw_group["title"],
                    "description": raw_group["description"],
                    "cards": cards,
                }, "title", "description")
            )

    if groups:
        return groups

    flat_cards = _hub_topic_cards(teaching_lang, ui_lang, include_unavailable=True)
    if not flat_cards:
        return []
    return [_set_inline_markdown_fields({"title": "", "description": "", "cards": flat_cards}, "title", "description")]


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
    return [
        ui_lang
        for ui_lang in manifest["available_ui_langs"]
        if _index_path(teaching_lang, ui_lang).exists()
    ]


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


@lru_cache(maxsize=None)
def load_teaching_media_manifest(teaching_lang: str, topic_slug: str) -> dict[str, Any] | None:
    return _safe_yaml_map(_media_manifest_path(teaching_lang, topic_slug))


def topic_exists(teaching_lang: str, ui_lang: str, topic_slug: str) -> bool:
    return load_teaching_topic(teaching_lang, ui_lang, topic_slug) is not None


def count_teaching_topics(teaching_lang: str, ui_lang: str) -> int:
    return len(_hub_topic_cards(teaching_lang, ui_lang))


def resolve_topic_slug_for_ui_lang(teaching_lang: str, current_ui_lang: str, topic_slug: str, target_ui_lang: str) -> str | None:
    if not edition_exists(teaching_lang, target_ui_lang):
        return None

    current_topic = load_teaching_topic(teaching_lang, current_ui_lang, topic_slug)
    if current_topic is not None:
        equivalents = current_topic.get("equivalents") if isinstance(current_topic.get("equivalents"), dict) else {}
        equivalent_slug = _as_text(equivalents.get(target_ui_lang))
        equivalent_topic = load_teaching_topic(teaching_lang, target_ui_lang, equivalent_slug) if equivalent_slug else None
        if equivalent_slug and equivalent_topic is not None and topic_is_public(
            teaching_lang,
            target_ui_lang,
            equivalent_slug,
            raw_topic=equivalent_topic,
        ):
            return equivalent_slug

    target_topic = load_teaching_topic(teaching_lang, target_ui_lang, topic_slug)
    if target_topic is not None and topic_is_public(teaching_lang, target_ui_lang, topic_slug, raw_topic=target_topic):
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
    page_title = render_markdown_plain_text(title) or title
    lead = _as_text(index.get("lead"))
    overview_intro = _hub_overview_intro(index)
    topic_groups = _hub_topic_groups(teaching_lang, effective_ui_lang)
    topic_count = sum(len(group["cards"]) for group in topic_groups)
    content_header = _decorate_content_header_markdown(
        build_content_header(
            page_name="teaching",
            title=page_title,
            intro=lead,
            section_label=translate(effective_ui_lang, "section.teaching"),
            section_href=url_for("public.teaching_home", ui_lang=effective_ui_lang),
            context_mode="section",
            context_title=None,
            context_root_href=None,
            current_label=page_title,
            back_link={
                "label": translate(effective_ui_lang, "teaching.action.back_to_selection"),
                "href": url_for("public.teaching_home", ui_lang=effective_ui_lang),
            },
        ),
        title=title,
        intro=lead,
    )
    return {
        "title": title,
        "page_title": page_title,
        "intro": lead,
        "overview_intro": overview_intro,
        "page_kind": "material",
        "layout": "teaching",
        "template": "pages/teaching_page.html",
        "teaching_view": "hub",
        "resolved_ui_lang": effective_ui_lang,
        "teaching_lang": teaching_lang,
        "topic_groups": topic_groups,
        "empty_state": None
        if topic_count
        else {
            "title": translate(effective_ui_lang, "teaching.hub.empty.title"),
            "text": translate(effective_ui_lang, "teaching.hub.empty.text"),
        },
        "back_link": {
            "label": translate(effective_ui_lang, "teaching.action.back_to_selection"),
            "href": url_for("public.teaching_home", ui_lang=effective_ui_lang),
        },
        "teaching_switch_items": _teaching_switch_items(effective_ui_lang, teaching_lang),
        "content_header": content_header,
    }


def resolve_topic_route_target(teaching_lang: str, requested_ui_lang: str, topic_slug: str) -> dict[str, Any]:
    effective_ui_lang = resolve_teaching_edition_ui_lang(teaching_lang, requested_ui_lang)
    if effective_ui_lang is None:
        return {"status": "missing-language"}

    if effective_ui_lang != requested_ui_lang:
        effective_topic = load_teaching_topic(teaching_lang, effective_ui_lang, topic_slug)
        if effective_topic is not None and topic_is_public(
            teaching_lang,
            effective_ui_lang,
            topic_slug,
            raw_topic=effective_topic,
        ):
            return {"status": "redirect-topic", "ui_lang": effective_ui_lang, "topic_slug": topic_slug}
        return {"status": "redirect-hub", "ui_lang": effective_ui_lang}

    effective_topic = load_teaching_topic(teaching_lang, effective_ui_lang, topic_slug)
    if effective_topic is None or not topic_is_public(
        teaching_lang,
        effective_ui_lang,
        topic_slug,
        raw_topic=effective_topic,
    ):
        return {"status": "redirect-hub", "ui_lang": effective_ui_lang}

    return {"status": "ok", "ui_lang": effective_ui_lang, "topic_slug": topic_slug}


def build_teaching_topic_page(ui_lang: str, teaching_lang: str, topic_slug: str) -> dict[str, Any] | None:
    raw_topic = load_teaching_topic(teaching_lang, ui_lang, topic_slug)
    index = load_teaching_index(teaching_lang, ui_lang)
    if raw_topic is None or index is None or not topic_is_public(teaching_lang, ui_lang, topic_slug, raw_topic=raw_topic):
        return None

    title = _as_text(raw_topic.get("title")) or topic_slug.replace("-", " ").title()
    page_title = render_markdown_plain_text(title) or title
    page_intro = _topic_page_intro(raw_topic)
    hub_title = _as_text(index.get("title")) or teaching_lang.replace("-", " ").title()
    hub_title_plain = render_markdown_plain_text(hub_title) or hub_title
    topic_metadata = _topic_metadata(ui_lang, raw_topic)
    blocks = _topic_blocks(teaching_lang, ui_lang, topic_slug, raw_topic, topic_metadata)
    topic_sections = _topic_sections(blocks)
    content_header = _decorate_content_header_markdown(
        build_content_header(
            page_name="teaching",
            title=page_title,
            intro=page_intro,
            section_label=translate(ui_lang, "section.teaching"),
            section_href=url_for("public.teaching_home", ui_lang=ui_lang),
            context_mode="section",
            context_title=None,
            context_root_href=None,
            current_label=page_title,
            back_link={
                "label": translate(ui_lang, "teaching.action.back_to_language_hub", hub_title=hub_title_plain),
                "href": url_for("public.teaching_language_root", ui_lang=ui_lang, language_slug=teaching_lang),
            },
        ),
        title=title,
        intro=page_intro,
    )
    return {
        "title": title,
        "page_title": page_title,
        "intro": page_intro,
        "page_kind": "material",
        "layout": "teaching",
        "template": "pages/teaching_page.html",
        "teaching_view": "topic",
        "resolved_ui_lang": ui_lang,
        "teaching_lang": teaching_lang,
        "topic_slug": topic_slug,
        "hub_title": hub_title_plain,
        "hub_href": url_for("public.teaching_language_root", ui_lang=ui_lang, language_slug=teaching_lang),
        "back_link": {
            "label": translate(ui_lang, "teaching.action.back_to_language_hub", hub_title=hub_title_plain),
            "href": url_for("public.teaching_language_root", ui_lang=ui_lang, language_slug=teaching_lang),
        },
        "topic_metadata": topic_metadata,
        "teaching_switch_items": _teaching_switch_items(ui_lang, teaching_lang, topic_slug=topic_slug),
        "blocks": blocks,
        "topic_sections": topic_sections,
        "content_header": content_header,
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