"""File-backed research-player config and preset loading for PROMAT."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from .config.data_conventions import get_target_language_for_language_slug
from .research_capabilities import PLAYER_RENDER_MODES as TEXT_RENDER_MODES, RESEARCH_TASK_KEYS as TASK_TYPES
from .runtime_paths import get_config_root

PLAYER_SOURCE_KINDS: tuple[str, ...] = ("wordlist", "sentence_list", "text")
PLAYER_CONTENT_MODES: tuple[str, ...] = ("wordlist", "sentence_list", "connected_text")
PLAYER_VIEWS: tuple[str, ...] = ("list", "text")
PLAYER_AUDIO_MODES: tuple[str, ...] = ("item", "full")
PLAYER_PARAGRAPH_MODELS: tuple[str, ...] = ("none", "explicit")


class ResearchConfigError(ValueError):
    """Raised when research-player config files are missing or invalid."""


@dataclass(frozen=True)
class TaskItemReference:
    task: str
    item_id: str
    segment_id: str | None = None
    note: str | None = None
    sort_key: str | None = None

    @property
    def key(self) -> tuple[str, str]:
        return (self.task, self.item_id)


@dataclass(frozen=True)
class TaskCatalogItem:
    task: str
    item_id: str
    item_number: str
    text: str
    group_id: str | None = None
    text_container_id: str | None = None
    text_order_index: int | None = None
    paragraph_break_before: bool = False
    paragraph_id: str | None = None
    spoken_title_item: bool = False


@dataclass(frozen=True)
class TaskCatalogPlayerSource:
    source_kind: str
    content_mode: str
    default_view: str
    allowed_views: tuple[str, ...]
    primary_audio_mode: str
    supports_item_audio: bool
    supports_full_audio: bool
    supports_text_view: bool
    paragraph_model: str
    title: str | None = None
    subtitle: str | None = None


@dataclass(frozen=True)
class TaskCatalog:
    language: str
    task: str
    display_label: str | None
    player_source: TaskCatalogPlayerSource
    items_by_id: dict[str, TaskCatalogItem]


@dataclass(frozen=True)
class PlayerTextConfig:
    default_render_mode: str
    display_label: str


@dataclass(frozen=True)
class PlayerConfig:
    language: str
    text: PlayerTextConfig


@dataclass(frozen=True)
class PhenomenaPreset:
    preset_id: str
    label: str
    description: str
    language: str
    items: tuple[TaskItemReference, ...]


def _require_language_slug(language_slug: str) -> str:
    normalized = (language_slug or "").strip().lower()
    if get_target_language_for_language_slug(normalized) is None:
        raise ResearchConfigError(f"Unsupported language slug: {language_slug}")
    return normalized


def _research_player_language_dir(language_slug: str) -> Path:
    normalized = _require_language_slug(language_slug)
    return get_config_root() / "research_player" / normalized


def _require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise ResearchConfigError(f"Missing {label}: {path}")
    return path


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    _require_file(path, label)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ResearchConfigError(f"Invalid JSON in {label}: {path}: {exc}") from exc
    except OSError as exc:
        raise ResearchConfigError(f"Unable to read {label}: {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise ResearchConfigError(f"{label} must contain a top-level JSON object: {path}")
    return payload


def _require_string(payload: Mapping[str, Any], field_name: str, *, context: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ResearchConfigError(f"Missing or invalid string field '{field_name}' in {context}")
    return value.strip()


def _require_nonblank_string(payload: Mapping[str, Any], field_name: str, *, context: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ResearchConfigError(f"Missing or invalid string field '{field_name}' in {context}")
    return value


def _optional_string(payload: Mapping[str, Any], field_name: str, *, context: str) -> str | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ResearchConfigError(f"Invalid optional string field '{field_name}' in {context}")
    normalized = value.strip()
    return normalized or None


def _optional_int(payload: Mapping[str, Any], field_name: str, *, context: str) -> int | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResearchConfigError(f"Invalid optional integer field '{field_name}' in {context}")
    return value


def _optional_bool(payload: Mapping[str, Any], field_name: str, *, context: str) -> bool | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResearchConfigError(f"Invalid optional boolean field '{field_name}' in {context}")
    return value


def _require_string_list(
    payload: Mapping[str, Any],
    field_name: str,
    *,
    context: str,
    allowed_values: tuple[str, ...],
) -> tuple[str, ...]:
    raw_values = payload.get(field_name)
    if not isinstance(raw_values, list) or not raw_values:
        raise ResearchConfigError(f"Missing or invalid list field '{field_name}' in {context}")

    normalized_values: list[str] = []
    seen: set[str] = set()
    for index, raw_value in enumerate(raw_values, start=1):
        if not isinstance(raw_value, str) or not raw_value.strip():
            raise ResearchConfigError(f"Invalid entry #{index} in '{field_name}' for {context}")
        normalized_value = raw_value.strip()
        if normalized_value not in allowed_values:
            raise ResearchConfigError(
                f"Unsupported value '{normalized_value}' in '{field_name}' for {context}; expected one of {allowed_values}"
            )
        if normalized_value in seen:
            continue
        seen.add(normalized_value)
        normalized_values.append(normalized_value)

    return tuple(normalized_values)


def _default_player_source(task_key: str) -> TaskCatalogPlayerSource:
    if task_key == "wordlist":
        return TaskCatalogPlayerSource(
            source_kind="wordlist",
            content_mode="wordlist",
            default_view="list",
            allowed_views=("list",),
            primary_audio_mode="item",
            supports_item_audio=True,
            supports_full_audio=True,
            supports_text_view=False,
            paragraph_model="none",
        )
    return TaskCatalogPlayerSource(
        source_kind="sentence_list",
        content_mode="sentence_list",
        default_view="list",
        allowed_views=("list",),
        primary_audio_mode="item",
        supports_item_audio=True,
        supports_full_audio=True,
        supports_text_view=False,
        paragraph_model="none",
    )


def _load_task_catalog_player_source(payload: Mapping[str, Any], *, task_key: str, context: str) -> TaskCatalogPlayerSource:
    raw_player_source = payload.get("player_source")
    if raw_player_source is None:
        return _default_player_source(task_key)
    if not isinstance(raw_player_source, dict):
        raise ResearchConfigError(f"Invalid 'player_source' object in {context}")

    source_kind = _require_string(raw_player_source, "source_kind", context=f"{context} player_source")
    if source_kind not in PLAYER_SOURCE_KINDS:
        raise ResearchConfigError(
            f"Unsupported player_source.source_kind '{source_kind}' in {context}; expected one of {PLAYER_SOURCE_KINDS}"
        )

    content_mode = _require_string(raw_player_source, "content_mode", context=f"{context} player_source")
    if content_mode not in PLAYER_CONTENT_MODES:
        raise ResearchConfigError(
            f"Unsupported player_source.content_mode '{content_mode}' in {context}; expected one of {PLAYER_CONTENT_MODES}"
        )

    default_view = _require_string(raw_player_source, "default_view", context=f"{context} player_source")
    if default_view not in PLAYER_VIEWS:
        raise ResearchConfigError(
            f"Unsupported player_source.default_view '{default_view}' in {context}; expected one of {PLAYER_VIEWS}"
        )

    allowed_views = _require_string_list(
        raw_player_source,
        "allowed_views",
        context=f"{context} player_source",
        allowed_values=PLAYER_VIEWS,
    )
    if default_view not in allowed_views:
        raise ResearchConfigError(
            f"player_source.default_view '{default_view}' must be listed in allowed_views for {context}"
        )

    primary_audio_mode = _require_string(raw_player_source, "primary_audio_mode", context=f"{context} player_source")
    if primary_audio_mode not in PLAYER_AUDIO_MODES:
        raise ResearchConfigError(
            f"Unsupported player_source.primary_audio_mode '{primary_audio_mode}' in {context}; expected one of {PLAYER_AUDIO_MODES}"
        )

    supports_item_audio = raw_player_source.get("supports_item_audio")
    supports_full_audio = raw_player_source.get("supports_full_audio")
    supports_text_view = raw_player_source.get("supports_text_view")
    if not isinstance(supports_item_audio, bool):
        raise ResearchConfigError(f"Missing or invalid boolean field 'supports_item_audio' in {context} player_source")
    if not isinstance(supports_full_audio, bool):
        raise ResearchConfigError(f"Missing or invalid boolean field 'supports_full_audio' in {context} player_source")
    if not isinstance(supports_text_view, bool):
        raise ResearchConfigError(f"Missing or invalid boolean field 'supports_text_view' in {context} player_source")

    paragraph_model = _require_string(raw_player_source, "paragraph_model", context=f"{context} player_source")
    if paragraph_model not in PLAYER_PARAGRAPH_MODELS:
        raise ResearchConfigError(
            f"Unsupported player_source.paragraph_model '{paragraph_model}' in {context}; expected one of {PLAYER_PARAGRAPH_MODELS}"
        )

    if supports_text_view and source_kind != "text":
        raise ResearchConfigError(
            f"player_source.supports_text_view may only be true for source_kind 'text' in {context}"
        )
    if supports_text_view and content_mode != "connected_text":
        raise ResearchConfigError(
            f"player_source.supports_text_view requires content_mode 'connected_text' in {context}"
        )
    if "text" in allowed_views and not supports_text_view:
        raise ResearchConfigError(
            f"player_source.allowed_views must not contain 'text' when supports_text_view is false in {context}"
        )
    if not supports_text_view and default_view == "text":
        raise ResearchConfigError(
            f"player_source.default_view 'text' requires supports_text_view=true in {context}"
        )

    return TaskCatalogPlayerSource(
        source_kind=source_kind,
        content_mode=content_mode,
        default_view=default_view,
        allowed_views=allowed_views,
        primary_audio_mode=primary_audio_mode,
        supports_item_audio=supports_item_audio,
        supports_full_audio=supports_full_audio,
        supports_text_view=supports_text_view,
        paragraph_model=paragraph_model,
        title=_optional_string(raw_player_source, "title", context=f"{context} player_source"),
        subtitle=_optional_string(raw_player_source, "subtitle", context=f"{context} player_source"),
    )


def normalize_task_item_reference(payload: Mapping[str, Any], *, context: str) -> TaskItemReference:
    task = _require_string(payload, "task", context=context)
    item_id = _require_string(payload, "item_id", context=context)
    if task not in TASK_TYPES:
        raise ResearchConfigError(f"Unknown task '{task}' in {context}")

    return TaskItemReference(
        task=task,
        item_id=item_id,
        segment_id=_optional_string(payload, "segment_id", context=context),
        note=_optional_string(payload, "note", context=context),
        sort_key=_optional_string(payload, "sort_key", context=context),
    )


def _task_catalog_dir(language_slug: str) -> Path:
    return _research_player_language_dir(language_slug) / "task_catalogs"


def _task_catalog_path(language_slug: str, task_key: str) -> Path:
    return _task_catalog_dir(language_slug) / f"{task_key}.json"


@lru_cache(maxsize=None)
def load_task_catalog(language_slug: str, task_key: str) -> TaskCatalog:
    normalized_language = _require_language_slug(language_slug)
    normalized_task = (task_key or "").strip()
    if normalized_task not in TASK_TYPES:
        raise ResearchConfigError(f"Unknown task catalog requested: {task_key}")

    path = _task_catalog_path(normalized_language, normalized_task)
    payload = _load_json_object(path, f"task catalog '{normalized_task}'")

    language_value = _require_string(payload, "language", context=str(path))
    if language_value != normalized_language:
        raise ResearchConfigError(
            f"Task catalog language mismatch in {path}: expected '{normalized_language}', got '{language_value}'"
        )

    task_value = _require_string(payload, "task", context=str(path))
    if task_value != normalized_task:
        raise ResearchConfigError(
            f"Task catalog task mismatch in {path}: expected '{normalized_task}', got '{task_value}'"
        )

    player_source = _load_task_catalog_player_source(payload, task_key=normalized_task, context=str(path))

    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ResearchConfigError(f"Task catalog '{normalized_task}' must contain a non-empty 'items' list: {path}")

    items_by_id: dict[str, TaskCatalogItem] = {}
    for index, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, dict):
            raise ResearchConfigError(f"Invalid item entry #{index} in task catalog '{normalized_task}': {path}")
        context = f"{path} item #{index}"
        item_id = _require_string(raw_item, "item_id", context=context)
        if item_id in items_by_id:
            raise ResearchConfigError(f"Duplicate item_id '{item_id}' in task catalog '{normalized_task}': {path}")
        text_container_id = _optional_string(raw_item, "text_container_id", context=context)
        text_order_index = _optional_int(raw_item, "text_order_index", context=context)
        paragraph_break_before = _optional_bool(raw_item, "paragraph_break_before", context=context)
        spoken_title_item = _optional_bool(raw_item, "spoken_title_item", context=context)
        items_by_id[item_id] = TaskCatalogItem(
            task=normalized_task,
            item_id=item_id,
            item_number=_require_string(raw_item, "item_number", context=context),
            text=_require_nonblank_string(raw_item, "text", context=context),
            group_id=_optional_string(raw_item, "group_id", context=context),
            text_container_id=text_container_id or (f"{normalized_language}:{normalized_task}" if player_source.source_kind == "text" else None),
            text_order_index=text_order_index if text_order_index is not None else (index if player_source.source_kind == "text" else None),
            paragraph_break_before=bool(paragraph_break_before),
            paragraph_id=_optional_string(raw_item, "paragraph_id", context=context),
            spoken_title_item=bool(spoken_title_item),
        )

    display_label = _optional_string(payload, "display_label", context=str(path))
    return TaskCatalog(
        language=normalized_language,
        task=normalized_task,
        display_label=display_label,
        player_source=player_source,
        items_by_id=items_by_id,
    )


@lru_cache(maxsize=None)
def load_task_catalogs(language_slug: str) -> dict[str, TaskCatalog]:
    normalized_language = _require_language_slug(language_slug)
    catalog_dir = _task_catalog_dir(normalized_language)
    if not catalog_dir.is_dir():
        raise ResearchConfigError(f"Missing task catalog directory: {catalog_dir}")

    catalogs: dict[str, TaskCatalog] = {}
    for path in sorted(catalog_dir.glob("*.json")):
        task_key = path.stem
        catalogs[task_key] = load_task_catalog(normalized_language, task_key)
    if not catalogs:
        raise ResearchConfigError(f"No task catalogs found in {catalog_dir}")
    return catalogs


def validate_task_item_references(
    references: tuple[TaskItemReference, ...],
    *,
    language_slug: str,
    context: str,
) -> None:
    catalogs = load_task_catalogs(language_slug)
    seen: set[tuple[str, str]] = set()
    for reference in references:
        if reference.key in seen:
            raise ResearchConfigError(
                f"Duplicate preset item reference '{reference.task}:{reference.item_id}' in {context}"
            )
        seen.add(reference.key)

        catalog = catalogs.get(reference.task)
        if catalog is None:
            raise ResearchConfigError(
                f"No task catalog configured for task '{reference.task}' in language '{language_slug}' ({context})"
            )
        if reference.item_id not in catalog.items_by_id:
            raise ResearchConfigError(
                f"Unknown item_id '{reference.item_id}' for task '{reference.task}' in {context}"
            )


@lru_cache(maxsize=None)
def load_player_config(language_slug: str) -> PlayerConfig:
    normalized_language = _require_language_slug(language_slug)
    path = _research_player_language_dir(normalized_language) / "player_config.json"
    payload = _load_json_object(path, "player config")

    language_value = _require_string(payload, "language", context=str(path))
    if language_value != normalized_language:
        raise ResearchConfigError(
            f"Player config language mismatch in {path}: expected '{normalized_language}', got '{language_value}'"
        )

    text_payload = payload.get("text")
    if not isinstance(text_payload, dict):
        raise ResearchConfigError(f"Player config must contain a 'text' object: {path}")

    default_render_mode = _require_string(text_payload, "default_render_mode", context=f"{path} text")
    if default_render_mode not in TEXT_RENDER_MODES:
        raise ResearchConfigError(
            f"Unsupported text.default_render_mode '{default_render_mode}' in {path}; expected one of {TEXT_RENDER_MODES}"
        )

    display_label = _require_string(text_payload, "display_label", context=f"{path} text")
    return PlayerConfig(
        language=normalized_language,
        text=PlayerTextConfig(default_render_mode=default_render_mode, display_label=display_label),
    )


@lru_cache(maxsize=None)
def load_phenomena_presets(language_slug: str) -> tuple[PhenomenaPreset, ...]:
    normalized_language = _require_language_slug(language_slug)
    path = _research_player_language_dir(normalized_language) / "phenomena_presets.json"
    payload = _load_json_object(path, "phenomena presets")

    language_value = _require_string(payload, "language", context=str(path))
    if language_value != normalized_language:
        raise ResearchConfigError(
            f"Phenomena preset file language mismatch in {path}: expected '{normalized_language}', got '{language_value}'"
        )

    raw_presets = payload.get("presets")
    if not isinstance(raw_presets, list) or not raw_presets:
        raise ResearchConfigError(f"Phenomena preset file must contain a non-empty 'presets' list: {path}")

    presets: list[PhenomenaPreset] = []
    preset_ids: set[str] = set()
    for index, raw_preset in enumerate(raw_presets, start=1):
        if not isinstance(raw_preset, dict):
            raise ResearchConfigError(f"Invalid preset entry #{index} in {path}")
        context = f"{path} preset #{index}"
        preset_id = _require_string(raw_preset, "preset_id", context=context)
        if preset_id in preset_ids:
            raise ResearchConfigError(f"Duplicate preset_id '{preset_id}' in {path}")
        preset_ids.add(preset_id)

        preset_language = _require_string(raw_preset, "language", context=context)
        if preset_language != normalized_language:
            raise ResearchConfigError(
                f"Preset '{preset_id}' language mismatch in {path}: expected '{normalized_language}', got '{preset_language}'"
            )

        raw_items = raw_preset.get("items")
        if not isinstance(raw_items, list) or not raw_items:
            raise ResearchConfigError(f"Preset '{preset_id}' must contain a non-empty 'items' list in {path}")

        items = tuple(
            normalize_task_item_reference(raw_item, context=f"{context} item #{item_index}")
            for item_index, raw_item in enumerate(raw_items, start=1)
            if isinstance(raw_item, dict)
        )
        if len(items) != len(raw_items):
            raise ResearchConfigError(f"Preset '{preset_id}' contains non-object item entries in {path}")

        validate_task_item_references(items, language_slug=normalized_language, context=f"preset '{preset_id}'")

        presets.append(
            PhenomenaPreset(
                preset_id=preset_id,
                label=_require_string(raw_preset, "label", context=context),
                description=_require_string(raw_preset, "description", context=context),
                language=preset_language,
                items=items,
            )
        )

    return tuple(presets)


@lru_cache(maxsize=None)
def load_phenomena_preset_map(language_slug: str) -> dict[str, PhenomenaPreset]:
    return {preset.preset_id: preset for preset in load_phenomena_presets(language_slug)}


def clear_research_preset_caches() -> None:
    load_task_catalog.cache_clear()
    load_task_catalogs.cache_clear()
    load_player_config.cache_clear()
    load_phenomena_presets.cache_clear()
    load_phenomena_preset_map.cache_clear()
