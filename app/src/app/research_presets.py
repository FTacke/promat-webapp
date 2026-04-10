"""File-backed research-player config and preset loading for PROMAT."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from .config.data_conventions import TASK_TYPES, get_target_language_for_language_slug
from .runtime_paths import get_config_root


TEXT_RENDER_MODES: tuple[str, ...] = ("sentence_list", "running_text")


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


@dataclass(frozen=True)
class TaskCatalog:
    language: str
    task: str
    display_label: str | None
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


def _optional_string(payload: Mapping[str, Any], field_name: str, *, context: str) -> str | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ResearchConfigError(f"Invalid optional string field '{field_name}' in {context}")
    normalized = value.strip()
    return normalized or None


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
        items_by_id[item_id] = TaskCatalogItem(
            task=normalized_task,
            item_id=item_id,
            item_number=_require_string(raw_item, "item_number", context=context),
            text=_require_string(raw_item, "text", context=context),
            group_id=_optional_string(raw_item, "group_id", context=context),
        )

    display_label = _optional_string(payload, "display_label", context=str(path))
    return TaskCatalog(
        language=normalized_language,
        task=normalized_task,
        display_label=display_label,
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
