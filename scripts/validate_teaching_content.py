"""Validate the public editorial content: Teaching manifests, hubs, topics, and the publication registry.

    python scripts/validate_teaching_content.py

Checks the structure (manifest, hubs, media, equivalents) and, for every topic that is public, its publication
front matter: stable ``resource_id``, structured creators, publication date, real DE/EN equivalents, and no typed
citation. The publication registry (``content/publication/resources.yaml``) is validated in the same run.
Topic media that no source file references is reported: a file is an error unless it is listed with a reason in
``content/teaching/media-exceptions.yaml``, in which case it is only a warning (and a stale entry is an error).
Contract: ``docs/spec/platform-data-files.md, "Publication Metadata"``.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
import importlib.util
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlparse

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "content" / "teaching"
UNFINISHED_STATUS_VALUES = {"draft", "private", "pending", "planned", "scaffold"}
PLACEHOLDER_AUTHORS = {"nn", "n.n.", "n. n."}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DOI_PATTERN = re.compile(r"^10[.][0-9]{4,9}/[^ ]+$")
MEDIA_EXCEPTIONS_FILE = CONTENT_ROOT / "media-exceptions.yaml"
MEDIA_EXCEPTION_STATUSES = {"content_decision_required", "retained"}


def load_publication_module():
    """The app's publication module, loaded by path: it has no Flask or configuration dependency."""
    spec = importlib.util.spec_from_file_location("promat_publication", REPO_ROOT / "app" / "src" / "app" / "publication.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
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


def _metadata(topic: dict[str, Any]) -> dict[str, Any]:
    metadata = topic.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_as_text(item) for item in value if _as_text(item)]
    return [_as_text(value)] if _as_text(value) else []


def topic_is_public(topic: dict[str, Any]) -> bool:
    """Same rule as ``app.teaching_content.topic_is_public``, evaluated on the YAML alone."""
    for key in ("is_available", "is_public", "published"):
        value = topic.get(key)
        if value is False or _as_text(value).lower() in {"false", "no", "0", "draft", "private", "pending", "planned"}:
            return False
    hub = topic.get("hub") if isinstance(topic.get("hub"), dict) else {}
    if any(_as_text(value).lower() in UNFINISHED_STATUS_VALUES for value in (topic.get("status"), hub.get("status"))):
        return False
    metadata = _metadata(topic)
    names = _string_list(metadata.get("authors"))
    if names and not _string_list(metadata.get("creators")) and all(name.lower() in PLACEHOLDER_AUTHORS for name in names):
        return False
    return True


def _as_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(_as_text(value))
    except ValueError:
        return None


def validate_publication_front_matter(
    errors: list[str],
    publication: Any,
    teaching_lang: str,
    available_ui_langs: list[str],
    seen_resource_ids: dict[str, str],
) -> None:
    """Front matter of every public topic edition of one teaching language."""
    language_dir = CONTENT_ROOT / teaching_lang
    topic_slugs = sorted(path.name for path in language_dir.iterdir() if path.is_dir() and path.name != "hubs")
    known_people = set(publication.load_registry().get("people") or {})
    for topic_slug in topic_slugs:
        if not SLUG_PATTERN.match(topic_slug):
            errors.append(f"{teaching_lang}/{topic_slug}: topic slug must be lower-case ASCII words joined by hyphens")
        editions = {ui_lang: _load_yaml_map(_topic_file(teaching_lang, topic_slug, ui_lang)) for ui_lang in available_ui_langs}
        public = {ui_lang: topic for ui_lang, topic in editions.items() if topic is not None and topic_is_public(topic)}
        resource_ids = {_as_text(topic.get("resource_id")) for topic in public.values()}
        if len(resource_ids) > 1:
            errors.append(f"{teaching_lang}/{topic_slug}: the language editions must share one resource_id, found {sorted(resource_ids)}")
        for ui_lang, topic in public.items():
            where = f"{teaching_lang}/{topic_slug}/{ui_lang}"
            owner = f"{teaching_lang}/{topic_slug}"
            resource_id = _as_text(topic.get("resource_id"))
            if not SLUG_PATTERN.match(resource_id):
                errors.append(f"{where}: a public topic needs a resource_id (lower-case ASCII words joined by hyphens)")
            elif seen_resource_ids.get(resource_id, owner) != owner:
                errors.append(f"{where}: resource_id {resource_id!r} is already used by {seen_resource_ids[resource_id]}")
            else:
                seen_resource_ids[resource_id] = owner
            if not _as_text(topic.get("title")):
                errors.append(f"{where}: title is required")
            if not _as_text(topic.get("summary")) and not _as_text(topic.get("description")):
                errors.append(f"{where}: summary or description is required (used as the page description)")
            metadata = _metadata(topic)
            creators = _string_list(metadata.get("creators"))
            if not creators:
                errors.append(f"{where}: metadata.creators must list at least one person id of content/publication/resources.yaml")
            for person_id in creators:
                if person_id not in known_people:
                    errors.append(f"{where}: unknown creator {person_id!r}")
            if _string_list(metadata.get("authors")) or isinstance(topic.get("credits"), dict):
                errors.append(f"{where}: a public topic names its authors only through metadata.creators (remove authors/credits)")
            created, updated = _as_date(metadata.get("created")), _as_date(metadata.get("updated"))
            if created is None:
                errors.append(f"{where}: metadata.created must be an ISO date (publication date)")
            if metadata.get("updated") is not None and updated is None:
                errors.append(f"{where}: metadata.updated must be an ISO date")
            if created and updated and updated < created:
                errors.append(f"{where}: metadata.updated is earlier than metadata.created")
            citation = topic.get("citation")
            if isinstance(citation, dict) and any(key in citation for key in ("text", "copy_text", "url")):
                errors.append(f"{where}: remove the typed citation; it is generated from the publication metadata")
            doi = topic.get("doi")
            if doi is not None and not DOI_PATTERN.match(_as_text(doi)):
                errors.append(f"{where}: doi {doi!r} is not a DOI (expected 10.xxxx/...)")
            for alias in _string_list(topic.get("aliases")):
                if not SLUG_PATTERN.match(alias):
                    errors.append(f"{where}: alias {alias!r} must be a slug")
                elif alias in topic_slugs:
                    errors.append(f"{where}: alias {alias!r} collides with an existing topic")
            # Finished surfaces are bilingual: every other UI edition must exist, be public and point back.
            equivalents = topic.get("equivalents") if isinstance(topic.get("equivalents"), dict) else {}
            for other_ui_lang in available_ui_langs:
                if other_ui_lang == ui_lang:
                    continue
                other_slug = _as_text(equivalents.get(other_ui_lang))
                other = _load_yaml_map(_topic_file(teaching_lang, other_slug, other_ui_lang)) if other_slug else None
                if other is None or not topic_is_public(other):
                    errors.append(f"{where}: no public {other_ui_lang} equivalent (equivalents.{other_ui_lang})")
                    continue
                back = other.get("equivalents") if isinstance(other.get("equivalents"), dict) else {}
                if _as_text(back.get(ui_lang)) != topic_slug:
                    errors.append(f"{where}: equivalent {other_ui_lang}/{other_slug} does not point back to {topic_slug}")


def _string_leaves(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value.replace("\\", "/")
    elif isinstance(value, dict):
        for item in value.values():
            yield from _string_leaves(item)
    elif isinstance(value, list):
        for item in value:
            yield from _string_leaves(item)


def _source_strings(teaching_lang: str) -> list[str]:
    """Every string in the YAML sources of one teaching language (topics, hubs, manifest).

    Matching on any string (not only the known media fields) keeps references that the block model does not
    name explicitly, such as media mentioned from hubs or nested block fields, from being reported as orphans.
    """
    strings: list[str] = []
    for source in sorted((CONTENT_ROOT / teaching_lang).rglob("*.yaml")):
        loaded = _load_yaml_map(source)
        if loaded is not None:
            strings.extend(_string_leaves(loaded))
    return strings


def _load_media_exceptions(errors: list[str]) -> dict[str, dict[str, Any]]:
    if not MEDIA_EXCEPTIONS_FILE.exists():
        return {}
    loaded = _load_yaml_map(MEDIA_EXCEPTIONS_FILE)
    if loaded is None:
        errors.append(f"Missing or invalid media exceptions file: {MEDIA_EXCEPTIONS_FILE.relative_to(REPO_ROOT)}")
        return {}
    exceptions: dict[str, dict[str, Any]] = {}
    for entry in loaded.get("unreferenced_media") or []:
        path = _as_text(entry.get("path")) if isinstance(entry, dict) else ""
        status = _as_text(entry.get("status")) if isinstance(entry, dict) else ""
        reason = _as_text(entry.get("reason")) if isinstance(entry, dict) else ""
        if not path or status not in MEDIA_EXCEPTION_STATUSES or not reason:
            errors.append(f"media exceptions: every entry needs path, reason and status in {sorted(MEDIA_EXCEPTION_STATUSES)}: {entry!r}")
            continue
        exceptions[path] = {"status": status, "reason": reason}
    return exceptions


def validate_unreferenced_media(errors: list[str], warnings: list[str], teaching_languages: list[str]) -> None:
    """Report topic media files that no YAML source of their teaching language references."""
    exceptions = _load_media_exceptions(errors)
    orphans: set[str] = set()
    for teaching_lang in teaching_languages:
        strings = _source_strings(teaching_lang)
        for media_file in sorted((CONTENT_ROOT / teaching_lang).glob("*/media/**/*")):
            if not media_file.is_file():
                continue
            relative_to_media = media_file.relative_to(media_file.parents[len(media_file.relative_to(CONTENT_ROOT / teaching_lang).parts) - 3])
            # {media_type}/{path inside the type}; references may name the path with or without the type folder.
            parts = relative_to_media.parts
            inner = "/".join(parts[1:])
            if any(inner in text or "/".join(parts) in text for text in strings):
                continue
            key = media_file.relative_to(CONTENT_ROOT).as_posix()
            orphans.add(key)
            if key in exceptions:
                warnings.append(f"unreferenced media kept by exception ({exceptions[key]['status']}): content/teaching/{key}")
            else:
                errors.append(
                    f"Unreferenced topic media: content/teaching/{key} (reference it, remove it, or list it with a reason in "
                    f"{MEDIA_EXCEPTIONS_FILE.relative_to(REPO_ROOT).as_posix()})"
                )
    for key in sorted(set(exceptions) - orphans):
        errors.append(f"media exceptions: {key} is no longer an unreferenced file; remove the stale entry")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    publication = load_publication_module()
    errors.extend(f"publication registry: {error}" for error in publication.validate_registry())
    seen_resource_ids: dict[str, str] = dict(publication.registry_resource_ids())
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

        validate_publication_front_matter(errors, publication, teaching_lang, available_ui_langs, seen_resource_ids)

    validate_unreferenced_media(errors, warnings, teaching_languages)

    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        print("Teaching content validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Teaching content validation passed for {len(teaching_languages)} teaching languages; publication registry valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())