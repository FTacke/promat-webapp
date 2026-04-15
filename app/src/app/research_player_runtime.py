"""Runtime resolvers and normalized contracts for the unified research player."""

from __future__ import annotations

import functools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from flask import url_for

from .i18n import translate
from .research_capabilities import (
    PLAYER_RENDER_MODES,
    get_research_task_label,
    resolve_player_render_capability,
    task_supports_player_compare,
    task_supports_set_filtering,
)
from .research_presets import ResearchConfigError, load_phenomena_preset_map, load_task_catalogs
from .research_sets import (
    ResearchSetNotFoundError,
    ResearchSetStorageUnavailableError,
    ResearchSetValidationError,
    load_owned_set,
)
from .research_sessions import SessionRecord, get_session, load_language_sessions, session_has_task, sort_sessions_by_recency


@dataclass(frozen=True)
class NormalizedPlayerSource:
    task_key: str
    source_kind: str
    items_title: str
    default_render_mode: str | None
    render_mode: str | None
    allowed_render_modes: tuple[str, ...]
    primary_audio_mode: str
    supports_item_audio: bool
    supports_full_audio: bool
    supports_text_view: bool
    is_set_excerpt: bool


@dataclass(frozen=True)
class ResolvedPlayerRuntimeState:
    set_context: dict[str, Any] | None
    effective_set_id: str | None
    effective_preset_id: str | None
    active_selector_preset_id: str | None
    task_bundle: dict[str, Any] | None
    ready_sessions: list[SessionRecord]
    ready_bundles: dict[str, dict[str, Any]]
    compare_session: SessionRecord | None
    compare_bundle: dict[str, Any] | None
    compare_requested_unavailable: bool
    effective_compare_mode: str
    player_source: NormalizedPlayerSource | None
    active_render_mode_query: str | None
    filtered_task_items: list[dict[str, Any]] | None
    filtered_task_empty: bool
    primary_items: list[dict[str, Any]]
    secondary_items: list[dict[str, Any]]
    compare_rows: list[dict[str, Any]]
    visible_focus_item_id: str | None


def _t(ui_lang: str, key: str, **kwargs: object) -> str:
    return translate(ui_lang, key, **kwargs)


def _normalize_text(value: str | None) -> str | None:
    normalized = (value or "").strip()
    return normalized or None


def _player_task_display_label(language_slug: str, task_key: str, ui_lang: str) -> str:
    return get_research_task_label(task_key, ui_lang, variant="material", language_slug=language_slug)


def _session_root(session: SessionRecord) -> Path:
    return session.metadata_path.parent


def _resolve_session_relative_path(session_root: Path, relative_path: str | None) -> Path | None:
    normalized = (relative_path or "").strip()
    if not normalized:
        return None

    candidate = (session_root / normalized).resolve()
    root = session_root.resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


@functools.lru_cache(maxsize=4096)
def is_playable_audio_artifact(path: Path | None) -> bool:
    if path is None or not path.is_file():
        return False

    try:
        file_size = path.stat().st_size
    except OSError:
        return False

    if file_size < 4:
        return False

    try:
        with path.open("rb") as handle:
            probe = handle.read(min(file_size, 65536))
    except OSError:
        return False

    if len(probe) < 4:
        return False

    start_offset = 0
    if probe.startswith(b"ID3"):
        if len(probe) < 10:
            return False
        start_offset = 10 + ((probe[6] & 0x7F) << 21) + ((probe[7] & 0x7F) << 14) + ((probe[8] & 0x7F) << 7) + (probe[9] & 0x7F)

    if start_offset >= len(probe) - 1:
        return False

    for index in range(start_offset, len(probe) - 1):
        if probe[index] != 0xFF:
            continue
        next_byte = probe[index + 1]
        if next_byte & 0xE0 == 0xE0 and next_byte & 0x18 != 0x08:
            return True
    return False


def _load_alignment_payload(session: SessionRecord, task_key: str) -> dict[str, Any] | None:
    session_root = _session_root(session)
    alignment_path = _resolve_session_relative_path(session_root, f"alignment/{task_key}.json")
    if alignment_path is None or not alignment_path.is_file():
        return None

    try:
        payload = json.loads(alignment_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None
    if payload.get("session_id") != session.session_id or payload.get("person_id") != session.person_id or payload.get("task") != task_key:
        return None
    return payload


def _coerce_milliseconds(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _normalize_bundle_tokens(
    item_id: str,
    raw_tokens: Any,
    *,
    item_start_ms: int,
    item_end_ms: int,
) -> list[dict[str, Any]]:
    if not isinstance(raw_tokens, list) or not raw_tokens:
        return []

    tokens: list[dict[str, Any]] = []
    for index, raw_token in enumerate(raw_tokens):
        if not isinstance(raw_token, dict):
            continue

        token_text = raw_token.get("text")
        token_start_ms = _coerce_milliseconds(raw_token.get("start_ms"))
        token_end_ms = _coerce_milliseconds(raw_token.get("end_ms"))
        if not isinstance(token_text, str) or not token_text.strip():
            continue
        if token_start_ms is None or token_end_ms is None or token_end_ms < token_start_ms:
            continue
        if token_start_ms < item_start_ms or token_end_ms > item_end_ms:
            continue

        raw_token_id = raw_token.get("token_id")
        tokens.append(
            {
                "token_id": raw_token_id if isinstance(raw_token_id, str) and raw_token_id else f"{item_id}_token_{index}",
                "text": token_text,
                "start_ms": token_start_ms,
                "end_ms": token_end_ms,
            }
        )

    return tokens


def _build_text_segments(item_id: str, text_value: str, tokens: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not text_value:
        return ([], [])
    if not tokens:
        return ([{"kind": "text", "text": text_value}], [])

    normalized_text = text_value.casefold()
    cursor = 0
    segments: list[dict[str, Any]] = []
    renderable_tokens: list[dict[str, Any]] = []

    for token in tokens:
        token_text = token.get("text")
        token_id = token.get("token_id")
        token_start_ms = token.get("start_ms")
        token_end_ms = token.get("end_ms")
        if not isinstance(token_text, str) or not token_text:
            continue
        if not isinstance(token_id, str) or not token_id:
            continue
        if not isinstance(token_start_ms, int) or not isinstance(token_end_ms, int):
            continue

        match_start = normalized_text.find(token_text.casefold(), cursor)
        if match_start < 0:
            continue

        if match_start > cursor:
            segments.append({"kind": "text", "text": text_value[cursor:match_start]})

        match_end = match_start + len(token_text)
        token_index = len(renderable_tokens)
        renderable_token = {
            "token_id": token_id or f"{item_id}_token_{token_index}",
            "token_index": token_index,
            "text": text_value[match_start:match_end],
            "start_ms": token_start_ms,
            "end_ms": token_end_ms,
        }
        renderable_tokens.append(renderable_token)
        segments.append(
            {
                "kind": "token",
                "token_id": renderable_token["token_id"],
                "token_index": token_index,
                "text": renderable_token["text"],
            }
        )
        cursor = match_end

    if not renderable_tokens:
        return ([{"kind": "text", "text": text_value}], [])

    if cursor < len(text_value):
        segments.append({"kind": "text", "text": text_value[cursor:]})

    return (segments, renderable_tokens)


def load_task_bundle(session: SessionRecord, task_key: str) -> dict[str, Any] | None:
    if not task_supports_set_filtering(task_key):
        return None

    payload = _load_alignment_payload(session, task_key)
    if payload is None:
        return None

    session_root = _session_root(session)
    audio = payload.get("audio")
    if not isinstance(audio, dict):
        return None

    full_mp3 = audio.get("full_mp3")
    if not isinstance(full_mp3, str):
        return None

    full_audio_path = _resolve_session_relative_path(session_root, full_mp3)
    if not is_playable_audio_artifact(full_audio_path):
        return None

    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        return None

    items: list[dict[str, Any]] = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            return None

        item_id = raw_item.get("item_id")
        item_number = raw_item.get("item_number")
        text_value = raw_item.get("text")
        start_ms = _coerce_milliseconds(raw_item.get("start_ms"))
        end_ms = _coerce_milliseconds(raw_item.get("end_ms"))
        if not isinstance(item_id, str) or not isinstance(item_number, str) or not isinstance(text_value, str):
            return None
        if start_ms is None or end_ms is None or end_ms < start_ms:
            return None

        split_mp3 = raw_item.get("split_mp3")
        split_audio_path = _resolve_session_relative_path(session_root, split_mp3) if isinstance(split_mp3, str) else None
        items.append(
            {
                "item_id": item_id,
                "item_number": item_number,
                "text": text_value,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "tokens": _normalize_bundle_tokens(
                    item_id,
                    raw_item.get("tokens"),
                    item_start_ms=start_ms,
                    item_end_ms=end_ms,
                ),
                "split_audio_path": split_audio_path if is_playable_audio_artifact(split_audio_path) else None,
            }
        )

    return {"full_audio_path": full_audio_path, "items": items}


def load_task_ready_sessions(language_slug: str, task_key: str) -> tuple[list[SessionRecord], dict[str, dict[str, Any]]]:
    ready_sessions: list[SessionRecord] = []
    bundles: dict[str, dict[str, Any]] = {}
    for candidate in sort_sessions_by_recency(load_language_sessions(language_slug)):
        if not session_has_task(candidate, task_key):
            continue
        bundle = load_task_bundle(candidate, task_key)
        if bundle is None:
            continue
        ready_sessions.append(candidate)
        bundles[candidate.session_id] = bundle
    return ready_sessions, bundles


def resolve_player_set_context(
    language_slug: str,
    task_key: str,
    requested_set_id: str | None,
    requested_preset_id: str | None,
    requested_focus_item: str | None,
    *,
    owner_user_id: str | None,
    load_owned_set_fn=load_owned_set,
) -> dict[str, Any] | None:
    normalized_set_id = _normalize_text(requested_set_id)
    normalized_preset_id = _normalize_text(requested_preset_id)

    if normalized_set_id:
        if owner_user_id is None:
            return {
                "status": "requires-auth",
                "requested_set_id": normalized_set_id,
                "task_items": [],
                "task_counts": {task_name: 0 for task_name in ("wordlist", "text")},
                "focused_item_id": None,
                "requested_focus_item": requested_focus_item,
                "effective_preset_id": None,
            }

        try:
            stored_set = load_owned_set_fn(owner_user_id=owner_user_id, set_id=normalized_set_id)
        except (ResearchSetNotFoundError, ResearchSetValidationError, RuntimeError):
            return {
                "status": "unavailable",
                "requested_set_id": normalized_set_id,
                "task_items": [],
                "task_counts": {task_name: 0 for task_name in ("wordlist", "text")},
                "focused_item_id": None,
                "requested_focus_item": requested_focus_item,
                "effective_preset_id": None,
            }
        except ResearchSetStorageUnavailableError:
            return {
                "status": "storage-unavailable",
                "requested_set_id": normalized_set_id,
                "task_items": [],
                "task_counts": {task_name: 0 for task_name in ("wordlist", "text")},
                "focused_item_id": None,
                "requested_focus_item": requested_focus_item,
                "effective_preset_id": None,
            }

        if stored_set.corpus_language != language_slug:
            return {
                "status": "unavailable",
                "requested_set_id": normalized_set_id,
                "task_items": [],
                "task_counts": {task_name: 0 for task_name in ("wordlist", "text")},
                "focused_item_id": None,
                "requested_focus_item": requested_focus_item,
                "effective_preset_id": None,
            }

        task_counts = {task_name: 0 for task_name in ("wordlist", "text")}
        for item in stored_set.items:
            if item.task in task_counts:
                task_counts[item.task] += 1

        task_items: list[dict[str, Any]] = []
        catalogs = load_task_catalogs(language_slug)
        catalog = catalogs.get(task_key) if task_supports_set_filtering(task_key) else None
        if catalog is not None:
            for stored_item in stored_set.items:
                if stored_item.task != task_key:
                    continue
                catalog_item = catalog.items_by_id.get(stored_item.item_id)
                if catalog_item is None:
                    continue
                task_items.append(
                    {
                        "task": stored_item.task,
                        "item_id": stored_item.item_id,
                        "item_number": catalog_item.item_number,
                        "text": catalog_item.text,
                        "group_id": catalog_item.group_id,
                        "text_container_id": catalog_item.text_container_id,
                        "text_order_index": catalog_item.text_order_index,
                        "paragraph_break_before": catalog_item.paragraph_break_before,
                        "paragraph_id": catalog_item.paragraph_id,
                        "segment_id": stored_item.segment_id,
                        "note": stored_item.note,
                    }
                )

        focused_item_id = None
        if isinstance(requested_focus_item, str) and requested_focus_item:
            if any(item["item_id"] == requested_focus_item for item in task_items):
                focused_item_id = requested_focus_item

        return {
            "status": "loaded",
            "requested_set_id": normalized_set_id,
            "stored_set": stored_set,
            "task_items": task_items,
            "task_counts": task_counts,
            "focused_item_id": focused_item_id,
            "requested_focus_item": requested_focus_item,
            "effective_preset_id": stored_set.source_preset_id,
        }

    if not normalized_preset_id:
        return None

    try:
        preset = load_phenomena_preset_map(language_slug)[normalized_preset_id]
    except (KeyError, ResearchConfigError):
        return {
            "status": "unavailable",
            "requested_set_id": None,
            "task_items": [],
            "task_counts": {task_name: 0 for task_name in ("wordlist", "text")},
            "focused_item_id": None,
            "requested_focus_item": requested_focus_item,
            "effective_preset_id": normalized_preset_id,
        }

    task_counts = {task_name: 0 for task_name in ("wordlist", "text")}
    for reference in preset.items:
        if reference.task in task_counts:
            task_counts[reference.task] += 1

    task_items: list[dict[str, Any]] = []
    catalogs = load_task_catalogs(language_slug)
    catalog = catalogs.get(task_key) if task_supports_set_filtering(task_key) else None
    if catalog is not None:
        for reference in preset.items:
            if reference.task != task_key:
                continue
            catalog_item = catalog.items_by_id.get(reference.item_id)
            if catalog_item is None:
                continue
            task_items.append(
                {
                    "task": reference.task,
                    "item_id": reference.item_id,
                    "item_number": catalog_item.item_number,
                    "text": catalog_item.text,
                    "group_id": catalog_item.group_id,
                    "text_container_id": catalog_item.text_container_id,
                    "text_order_index": catalog_item.text_order_index,
                    "paragraph_break_before": catalog_item.paragraph_break_before,
                    "paragraph_id": catalog_item.paragraph_id,
                    "segment_id": reference.segment_id,
                    "note": reference.note,
                }
            )

    focused_item_id = None
    if isinstance(requested_focus_item, str) and requested_focus_item:
        if any(item["item_id"] == requested_focus_item for item in task_items):
            focused_item_id = requested_focus_item

    return {
        "status": "loaded",
        "requested_set_id": None,
        "stored_set": None,
        "task_items": task_items,
        "task_counts": task_counts,
        "focused_item_id": focused_item_id,
        "requested_focus_item": requested_focus_item,
        "effective_preset_id": preset.preset_id,
    }


def build_player_set_notice(
    ui_lang: str,
    language_slug: str,
    task_key: str,
    set_context: dict[str, Any] | None,
    resolved_focus_item_id: str | None,
) -> dict[str, Any] | None:
    del language_slug
    if set_context is None:
        return None

    status = set_context["status"]
    if status == "requires-auth":
        return {"status": status, "text": _t(ui_lang, "research.player.set_banner.requires_auth_text")}
    if status == "storage-unavailable":
        return {"status": status, "text": _t(ui_lang, "research.player.set_banner.storage_unavailable_text")}
    if status != "loaded":
        return {"status": status, "text": _t(ui_lang, "research.player.set_banner.unavailable_text")}

    if task_supports_set_filtering(task_key) and set_context.get("requested_focus_item") and not resolved_focus_item_id:
        return {"status": "focus-missed", "text": _t(ui_lang, "research.player.set_banner.focus_missed")}
    return None


def _format_player_clock(milliseconds: int) -> str:
    total_seconds = max(0, milliseconds // 1000)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def normalize_compare_mode(raw_value: str | None, *, compare_selected: bool) -> str:
    normalized = (raw_value or "").strip().lower()
    if not compare_selected:
        return "single"
    if normalized == "manual":
        return "manual"
    return "sequence"


def normalize_render_mode(raw_value: str | None) -> str | None:
    normalized = (raw_value or "").strip().lower()
    if normalized in PLAYER_RENDER_MODES:
        return normalized
    return None


def normalized_render_mode_query(player_source: NormalizedPlayerSource) -> str | None:
    if player_source.task_key != "text":
        return None
    if player_source.render_mode and player_source.render_mode != player_source.default_render_mode:
        return player_source.render_mode
    return None


def build_normalized_player_source(
    ui_lang: str,
    language_slug: str,
    task_key: str,
    *,
    bundle: Mapping[str, Any] | None,
    compare_selected: bool,
    requested_render_mode: str | None,
    set_context: dict[str, Any] | None,
) -> NormalizedPlayerSource:
    task_label = _player_task_display_label(language_slug, task_key, ui_lang)
    if task_key == "wordlist":
        return NormalizedPlayerSource(
            task_key=task_key,
            source_kind="set" if set_context is not None and set_context.get("status") == "loaded" else "wordlist",
            items_title=task_label,
            default_render_mode=None,
            render_mode=None,
            allowed_render_modes=(),
            primary_audio_mode="item",
            supports_item_audio=True,
            supports_full_audio=bundle is not None and bundle.get("full_audio_path") is not None,
            supports_text_view=False,
            is_set_excerpt=set_context is not None and set_context.get("status") == "loaded",
        )

    catalog = load_task_catalogs(language_slug)[task_key]
    catalog_source = catalog.player_source
    is_set_excerpt = set_context is not None and set_context.get("status") == "loaded"
    source_kind = "set" if is_set_excerpt else catalog_source.source_kind
    render_capability = resolve_player_render_capability(
        task_key,
        source_allowed_views=catalog_source.allowed_views,
        source_default_view=catalog_source.default_view,
        compare_selected=compare_selected,
        is_set_excerpt=is_set_excerpt,
    )
    supports_text_view = (
        render_capability.supports_text_view
        and catalog_source.source_kind == "text"
        and catalog_source.content_mode == "connected_text"
        and catalog_source.supports_text_view
    )
    allowed_render_modes = render_capability.allowed_render_modes or (("sentence_list",) if task_key == "text" else ())
    default_render_mode = render_capability.default_render_mode
    render_mode = normalize_render_mode(requested_render_mode)
    if render_mode not in allowed_render_modes:
        render_mode = default_render_mode

    return NormalizedPlayerSource(
        task_key=task_key,
        source_kind=source_kind,
        items_title=catalog.display_label or task_label,
        default_render_mode=default_render_mode,
        render_mode=render_mode,
        allowed_render_modes=allowed_render_modes,
        primary_audio_mode="item" if is_set_excerpt else catalog_source.primary_audio_mode,
        supports_item_audio=catalog_source.supports_item_audio,
        supports_full_audio=(
            False
            if is_set_excerpt
            else catalog_source.supports_full_audio and bundle is not None and bundle.get("full_audio_path") is not None
        ),
        supports_text_view=supports_text_view,
        is_set_excerpt=is_set_excerpt,
    )


def build_player_items(
    ui_lang: str,
    language_slug: str,
    session: SessionRecord,
    task_key: str,
    bundle: Mapping[str, Any],
    *,
    item_filter: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    catalog = load_task_catalogs(language_slug)[task_key]
    bundle_items = {item["item_id"]: item for item in bundle["items"]}
    if item_filter is not None:
        visible_items = item_filter
    else:
        visible_items = []
        for bundle_item in bundle["items"]:
            catalog_item = catalog.items_by_id.get(bundle_item["item_id"])
            visible_items.append(
                {
                    "item_id": bundle_item["item_id"],
                    "item_number": catalog_item.item_number if catalog_item is not None else bundle_item["item_number"],
                    "text": catalog_item.text if catalog_item is not None else bundle_item["text"],
                    "group_id": catalog_item.group_id if catalog_item is not None else None,
                    "text_container_id": catalog_item.text_container_id if catalog_item is not None else None,
                    "text_order_index": catalog_item.text_order_index if catalog_item is not None else None,
                    "paragraph_break_before": catalog_item.paragraph_break_before if catalog_item is not None else False,
                    "paragraph_id": catalog_item.paragraph_id if catalog_item is not None else None,
                    "segment_id": None,
                    "note": None,
                }
            )

    rows: list[dict[str, Any]] = []
    for visible_item in visible_items:
        bundle_item = bundle_items.get(visible_item["item_id"])
        row_text = visible_item.get("text") or ""
        if bundle_item is None:
            rows.append(
                {
                    "item_id": visible_item["item_id"],
                    "item_number": visible_item["item_number"],
                    "text": row_text,
                    "group_id": visible_item.get("group_id"),
                    "text_container_id": visible_item.get("text_container_id"),
                    "text_order_index": visible_item.get("text_order_index"),
                    "paragraph_break_before": bool(visible_item.get("paragraph_break_before")),
                    "paragraph_id": visible_item.get("paragraph_id"),
                    "segment_id": visible_item.get("segment_id"),
                    "note": visible_item.get("note"),
                    "tokens": [],
                    "text_segments": [{"kind": "text", "text": row_text}] if row_text else [],
                    "start_label": "",
                    "end_label": "",
                    "download_href": None,
                    "start_ms": None,
                    "end_ms": None,
                    "is_available": False,
                    "missing_label": _t(ui_lang, "research.player.no_clip_in_session"),
                }
            )
            continue

        row_text = visible_item.get("text") or bundle_item["text"]
        text_segments, renderable_tokens = _build_text_segments(
            bundle_item["item_id"],
            row_text,
            bundle_item.get("tokens", []),
        )

        rows.append(
            {
                "item_id": bundle_item["item_id"],
                "item_number": visible_item.get("item_number") or bundle_item["item_number"],
                "text": row_text,
                "group_id": visible_item.get("group_id"),
                "text_container_id": visible_item.get("text_container_id"),
                "text_order_index": visible_item.get("text_order_index"),
                "paragraph_break_before": bool(visible_item.get("paragraph_break_before")),
                "paragraph_id": visible_item.get("paragraph_id"),
                "segment_id": visible_item.get("segment_id"),
                "note": visible_item.get("note"),
                "tokens": renderable_tokens,
                "text_segments": text_segments,
                "start_label": _format_player_clock(bundle_item["start_ms"]),
                "end_label": _format_player_clock(bundle_item["end_ms"]),
                "download_href": url_for(
                    "public.research_player_item_download",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    session_id=session.session_id,
                    task=task_key,
                    item_id=bundle_item["item_id"],
                    download="1",
                ) if bundle_item["split_audio_path"] else None,
                "start_ms": bundle_item["start_ms"],
                "end_ms": bundle_item["end_ms"],
                "is_available": True,
                "missing_label": None,
            }
        )
    return rows


def build_running_text_blocks(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not items:
        return []

    blocks: list[dict[str, Any]] = []
    current_items: list[dict[str, Any]] = []
    block_index = 1
    for item in items:
        if current_items and item.get("paragraph_break_before"):
            blocks.append({"block_id": f"paragraph-{block_index}", "items": current_items})
            block_index += 1
            current_items = []
        current_items.append(item)

    if current_items:
        blocks.append({"block_id": f"paragraph-{block_index}", "items": current_items})
    return blocks


def build_player_compare_rows(
    primary_items: list[dict[str, Any]],
    secondary_items: list[dict[str, Any]],
    ui_lang: str,
) -> list[dict[str, Any]]:
    secondary_by_item = {item["item_id"]: item for item in secondary_items}
    rows: list[dict[str, Any]] = []
    for primary in primary_items:
        secondary = secondary_by_item.get(primary["item_id"])
        rows.append(
            {
                "item_id": primary["item_id"],
                "primary": primary,
                "secondary": secondary or {
                    "item_id": primary["item_id"],
                    "item_number": primary["item_number"],
                    "text": _t(ui_lang, "research.player.unavailable"),
                    "group_id": primary.get("group_id"),
                    "text_container_id": primary.get("text_container_id"),
                    "text_order_index": primary.get("text_order_index"),
                    "paragraph_break_before": primary.get("paragraph_break_before"),
                    "paragraph_id": primary.get("paragraph_id"),
                    "segment_id": primary.get("segment_id"),
                    "note": None,
                    "tokens": [],
                    "text_segments": [{"kind": "text", "text": _t(ui_lang, "research.player.unavailable")}],
                    "start_label": "",
                    "end_label": "",
                    "download_href": None,
                    "start_ms": None,
                    "end_ms": None,
                    "is_available": False,
                    "missing_label": _t(ui_lang, "research.player.no_clip_in_session"),
                },
            }
        )
    return rows


def resolve_player_runtime_state(
    ui_lang: str,
    language_slug: str,
    session: SessionRecord,
    task_key: str,
    *,
    owner_user_id: str | None,
    compare_session_id: str | None,
    compare_mode: str | None,
    set_id: str | None,
    preset_id: str | None,
    focus_item: str | None,
    render_mode: str | None,
    load_owned_set_fn=load_owned_set,
) -> ResolvedPlayerRuntimeState:
    set_context = resolve_player_set_context(
        language_slug,
        task_key,
        set_id,
        preset_id,
        focus_item,
        owner_user_id=owner_user_id,
        load_owned_set_fn=load_owned_set_fn,
    )
    effective_set_id = set_context["requested_set_id"] if set_context is not None else set_id
    effective_preset_id = set_context["effective_preset_id"] if set_context is not None else preset_id
    active_selector_preset_id = effective_preset_id if effective_set_id is None else None

    task_bundle = load_task_bundle(session, task_key) if task_supports_set_filtering(task_key) else None
    ready_sessions, ready_bundles = load_task_ready_sessions(language_slug, task_key) if task_supports_set_filtering(task_key) else ([], {})

    compare_session = None
    compare_bundle = None
    compare_requested_unavailable = False
    if task_supports_player_compare(task_key) and compare_session_id and compare_session_id != session.session_id:
        compare_session = next((candidate for candidate in ready_sessions if candidate.session_id == compare_session_id), None)
        compare_bundle = ready_bundles.get(compare_session_id)
        if compare_session is None or compare_bundle is None:
            compare_session = None
            compare_bundle = None
            compare_requested_unavailable = True

    effective_compare_mode = normalize_compare_mode(compare_mode, compare_selected=compare_session is not None)
    player_source = build_normalized_player_source(
        ui_lang,
        language_slug,
        task_key,
        bundle=task_bundle,
        compare_selected=compare_session is not None,
        requested_render_mode=render_mode,
        set_context=set_context if task_supports_set_filtering(task_key) else None,
    ) if task_supports_set_filtering(task_key) else None
    active_render_mode_query = normalized_render_mode_query(player_source) if player_source is not None else None
    filtered_task_items = set_context["task_items"] if set_context is not None and set_context["status"] == "loaded" else None
    filtered_task_empty = bool(
        set_context is not None
        and set_context["status"] == "loaded"
        and task_supports_set_filtering(task_key)
        and not set_context["task_items"]
    )

    primary_items: list[dict[str, Any]] = []
    secondary_items: list[dict[str, Any]] = []
    compare_rows: list[dict[str, Any]] = []
    visible_focus_item_id = None
    if task_supports_set_filtering(task_key) and task_bundle is not None and player_source is not None:
        primary_items = build_player_items(
            ui_lang,
            language_slug,
            session,
            task_key,
            task_bundle,
            item_filter=filtered_task_items,
        )
        if compare_session is not None and compare_bundle is not None:
            secondary_items = build_player_items(
                ui_lang,
                language_slug,
                compare_session,
                task_key,
                compare_bundle,
                item_filter=filtered_task_items,
            )
            compare_rows = build_player_compare_rows(primary_items, secondary_items, ui_lang)
        if isinstance(focus_item, str) and focus_item and any(item["item_id"] == focus_item for item in primary_items):
            visible_focus_item_id = focus_item

    return ResolvedPlayerRuntimeState(
        set_context=set_context,
        effective_set_id=effective_set_id,
        effective_preset_id=effective_preset_id,
        active_selector_preset_id=active_selector_preset_id,
        task_bundle=task_bundle,
        ready_sessions=ready_sessions,
        ready_bundles=ready_bundles,
        compare_session=compare_session,
        compare_bundle=compare_bundle,
        compare_requested_unavailable=compare_requested_unavailable,
        effective_compare_mode=effective_compare_mode,
        player_source=player_source,
        active_render_mode_query=active_render_mode_query,
        filtered_task_items=filtered_task_items,
        filtered_task_empty=filtered_task_empty,
        primary_items=primary_items,
        secondary_items=secondary_items,
        compare_rows=compare_rows,
        visible_focus_item_id=visible_focus_item_id,
    )


def resolve_player_audio_artifact(language_slug: str, session_id: str, task_key: str) -> Path | None:
    session = get_session(language_slug, session_id)
    if session is None or not task_supports_set_filtering(task_key) or not session_has_task(session, task_key):
        return None
    bundle = load_task_bundle(session, task_key)
    if bundle is None:
        return None
    return bundle["full_audio_path"]


def resolve_player_item_download(language_slug: str, session_id: str, task_key: str, item_id: str) -> dict[str, Any] | None:
    session = get_session(language_slug, session_id)
    if session is None or not task_supports_set_filtering(task_key) or not session_has_task(session, task_key):
        return None

    bundle = load_task_bundle(session, task_key)
    if bundle is None:
        return None

    for item in bundle["items"]:
        if item["item_id"] != item_id or item["split_audio_path"] is None:
            continue
        return {
            "path": item["split_audio_path"],
            "person_id": session.person_id,
            "task_key": task_key,
            "item_id": item["item_id"],
            "download_label": item["text"],
        }
    return None