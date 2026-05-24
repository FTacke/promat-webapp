from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "content" / "teaching"
MEDIA_FIELDS: dict[str, tuple[tuple[str, str], ...]] = {
    "image": (("src", "images"),),
    "audio_example": (("audio", "audio"),),
    "audio_examples": (("audio", "audio"),),
    "audio_contrast": (("audio", "audio"),),
    "download": (("href", "downloads"), ("file", "downloads"), ("url", "downloads")),
    "video": (("src", "video"),),
}


def _load_yaml_map(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else None


def _as_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_topic_reference(value: Any) -> str:
    if isinstance(value, dict):
        return _as_text(value.get("slug"))
    return _as_text(value)


def _topic_file(teaching_lang: str, topic_slug: str, ui_lang: str) -> Path:
    return CONTENT_ROOT / teaching_lang / topic_slug / f"{ui_lang}.yaml"


def _topic_media_file(teaching_lang: str, topic_slug: str, media_type: str, relative_path: str) -> Path:
    return CONTENT_ROOT / teaching_lang / topic_slug / "media" / media_type / Path(relative_path.replace("\\", "/"))


def _is_relative_media_reference(value: Any) -> bool:
    candidate = _as_text(value).replace("\\", "/")
    if not candidate or candidate.startswith("/"):
        return False
    return not bool(urlparse(candidate).scheme)


def _iter_hub_topic_slugs(hub: dict[str, Any]) -> Iterable[str]:
    if isinstance(hub.get("groups"), list):
        for group in hub["groups"]:
            if not isinstance(group, dict):
                continue
            for entry in group.get("topics", []):
                topic_slug = _normalize_topic_reference(entry)
                if topic_slug:
                    yield topic_slug
        return

    for entry in hub.get("topics", []):
        topic_slug = _normalize_topic_reference(entry)
        if topic_slug:
            yield topic_slug


def _validate_topic_media(
    errors: list[str],
    teaching_lang: str,
    topic_slug: str,
    topic: dict[str, Any],
) -> None:
    for block_index, raw_block in enumerate(topic.get("blocks", []), start=1):
        if not isinstance(raw_block, dict):
            continue
        block_type = _as_text(raw_block.get("type"))
        for field_name, media_type in MEDIA_FIELDS.get(block_type, ()): 
            value = raw_block.get(field_name)
            if _is_relative_media_reference(value):
                media_path = _topic_media_file(teaching_lang, topic_slug, media_type, _as_text(value))
                if not media_path.exists() or not media_path.is_file():
                    errors.append(
                        f"Missing topic-local media for {teaching_lang}/{topic_slug} block {block_index}: {field_name} -> {media_path.relative_to(REPO_ROOT)}"
                    )

        for item in raw_block.get("examples", []):
            if not isinstance(item, dict):
                continue
            if _is_relative_media_reference(item.get("audio")):
                media_path = _topic_media_file(teaching_lang, topic_slug, "audio", _as_text(item.get("audio")))
                if not media_path.exists() or not media_path.is_file():
                    errors.append(
                        f"Missing topic-local media for {teaching_lang}/{topic_slug} example audio -> {media_path.relative_to(REPO_ROOT)}"
                    )


def _validate_topic_equivalents(
    errors: list[str],
    teaching_lang: str,
    ui_lang: str,
    topic_slug: str,
    topic: dict[str, Any],
    available_ui_langs: list[str],
) -> None:
    equivalents = topic.get("equivalents") if isinstance(topic.get("equivalents"), dict) else {}
    for target_ui_lang, target_slug in equivalents.items():
        target_ui_lang_text = _as_text(target_ui_lang)
        target_slug_text = _as_text(target_slug)
        if not target_ui_lang_text or not target_slug_text:
            continue
        if target_ui_lang_text not in available_ui_langs:
            errors.append(
                f"Equivalent target {target_ui_lang_text} for {teaching_lang}/{topic_slug}/{ui_lang} is not in available_ui_langs."
            )
            continue
        if not _topic_file(teaching_lang, target_slug_text, target_ui_lang_text).exists():
            errors.append(
                f"Equivalent topic target missing for {teaching_lang}/{topic_slug}/{ui_lang} -> {target_ui_lang_text}/{target_slug_text}."
            )


def main() -> int:
    errors: list[str] = []
    teaching_languages = sorted(path.name for path in CONTENT_ROOT.iterdir() if path.is_dir()) if CONTENT_ROOT.exists() else []

    for teaching_lang in teaching_languages:
        manifest_path = CONTENT_ROOT / teaching_lang / "teaching.yaml"
        manifest = _load_yaml_map(manifest_path)
        if manifest is None:
            errors.append(f"Missing or invalid manifest: {manifest_path.relative_to(REPO_ROOT)}")
            continue

        available_ui_langs = [
            _as_text(value)
            for value in manifest.get("available_ui_langs", [])
            if _as_text(value)
        ]
        default_ui_lang = _as_text(manifest.get("default_ui_lang"))
        if default_ui_lang and default_ui_lang not in available_ui_langs:
            errors.append(f"Default UI language {default_ui_lang} is not listed in available_ui_langs for {teaching_lang}.")

        for ui_lang in available_ui_langs:
            hub_path = CONTENT_ROOT / teaching_lang / "hubs" / f"{ui_lang}.yaml"
            hub = _load_yaml_map(hub_path)
            if hub is None:
                errors.append(f"Missing or invalid hub file: {hub_path.relative_to(REPO_ROOT)}")
                continue

            for topic_slug in _iter_hub_topic_slugs(hub):
                topic_path = _topic_file(teaching_lang, topic_slug, ui_lang)
                topic = _load_yaml_map(topic_path)
                if topic is None:
                    errors.append(f"Missing topic file for hub reference: {topic_path.relative_to(REPO_ROOT)}")
                    continue
                _validate_topic_media(errors, teaching_lang, topic_slug, topic)
                _validate_topic_equivalents(errors, teaching_lang, ui_lang, topic_slug, topic, available_ui_langs)

    if errors:
        print("Teaching content validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Teaching content validation passed for {len(teaching_languages)} teaching languages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())