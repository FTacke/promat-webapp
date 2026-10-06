"""Publication metadata: one registry, one resource model, generated citations and schema.org JSON-LD.

The bibliographic identity of the platform, of every language corpus and teaching area, and the people behind them
lives in ``content/publication/resources.yaml`` (contract: ``docs/spec/platform-data-files.md, "Publication Metadata"``). Pages never type a
citation or an author list themselves: they ask this module for a *resource* and render what it derives from it.

Hierarchy: ``platform`` > ``research_corpus`` / ``teaching_resource`` > ``research_design`` / ``teaching_topic``.
A resource names its *creators* (the people responsible for it); the platform editor is only ever an editor of the
container, never an implicit author of a single resource.
"""

from __future__ import annotations

from datetime import date
from functools import lru_cache
from html import escape
import json
import os
from pathlib import Path
import re
from typing import Any

import yaml

RESOURCE_TYPES = ("platform", "research_corpus", "teaching_resource", "research_design", "teaching_topic")
LANGUAGE_RESOURCE_KINDS = ("research_corpus", "research_design", "teaching_resource")
RESOURCE_STATUSES = ("published", "in_preparation")
CONTRIBUTOR_ROLES = ("material_design", "data_collection", "coordination")
UI_LANGUAGES = ("de", "en")
#: content language of a corpus / teaching area (BCP 47), keyed by the technical language slug
CONTENT_LANGUAGE_CODES = {"spanish": "es", "french": "fr", "german": "de", "english": "en"}
#: English names of the languages a resource is about (schema.org `about`)
SUBJECT_LANGUAGE_NAMES = {"es": "Spanish", "fr": "French", "de": "German", "en": "English"}
PLACEHOLDER_NAMES = frozenset({"nn", "n.n.", "n. n."})

_RESOURCE_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DATE_PATTERN = re.compile(r"^\d{4}(?:-\d{2}-\d{2})?$")
_DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$")
_ORCID_PATTERN = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")

_SCHEMA_TYPES: dict[str, Any] = {
    "platform": "WebSite",
    "research_corpus": "Dataset",
    "teaching_resource": "Collection",
    "research_design": "ScholarlyArticle",
    "teaching_topic": ["Article", "LearningResource"],
}
_EDITOR_LABELS = {"de": ("Hrsg.", "Hrsg."), "en": ("ed.", "eds.")}
_QUOTES = {"de": ("„", "“"), "en": ("“", "”")}
_DATA_AS_OF_LABELS = {"de": "Datenstand", "en": "data as of"}


class PublicationRegistryError(RuntimeError):
    """The registry file is missing or structurally unusable."""


def _discover_registry_path() -> Path:
    override = os.getenv("PROMAT_PUBLICATION_REGISTRY")
    if override:
        return Path(override).expanduser()
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor / "content" / "publication" / "resources.yaml"
        if candidate.exists():
            return candidate
    raise PublicationRegistryError("content/publication/resources.yaml not found")


@lru_cache(maxsize=1)
def load_registry() -> dict[str, Any]:
    path = _discover_registry_path()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or not isinstance(data.get("platform"), dict):
        raise PublicationRegistryError(f"{path} must define a `platform` mapping")
    data.setdefault("people", {})
    data.setdefault("languages", {})
    return data


def clear_publication_caches() -> None:
    load_registry.cache_clear()


# --- people ---------------------------------------------------------------------------------------------------


def person(person_id: str) -> dict[str, Any] | None:
    """A person of the registry with the derived name forms (`name`, `sort_name`, `display_name`)."""
    raw = load_registry()["people"].get(person_id)
    if not isinstance(raw, dict):
        return None
    given, family = str(raw.get("given") or "").strip(), str(raw.get("family") or "").strip()
    name = f"{given} {family}".strip()
    prefix, suffix = str(raw.get("honorific_prefix") or "").strip(), str(raw.get("honorific_suffix") or "").strip()
    display_name = " ".join(part for part in (prefix, name) if part) + (f", {suffix}" if suffix else "")
    return {
        "id": person_id,
        "given": given,
        "family": family,
        "name": name,
        "sort_name": f"{family}, {given}" if family and given else name,
        "display_name": display_name,
        "affiliation": raw.get("affiliation") or None,
        "orcid": raw.get("orcid") or None,
    }


def people(person_ids: Any) -> list[dict[str, Any]]:
    return [entry for entry in (person(str(person_id)) for person_id in (person_ids or [])) if entry is not None]


def display_names(person_ids: Any) -> list[str]:
    """Names with academic titles, for visible lists such as corpus cards and the team page."""
    return [entry["display_name"] for entry in people(person_ids)]


# --- registry access ------------------------------------------------------------------------------------------


def platform_entry() -> dict[str, Any]:
    return load_registry()["platform"]


def canonical_base_url() -> str:
    return str(platform_entry()["canonical_base_url"]).rstrip("/")


def canonical_url(path: str) -> str:
    """The one public URL of a path: https, registry host, no query string, no trailing slash."""
    clean = "/" + str(path or "").split("?", 1)[0].split("#", 1)[0].strip("/")
    return canonical_base_url() + ("" if clean == "/" else clean)


def language_entry(kind: str, language_slug: str) -> dict[str, Any] | None:
    entry = (load_registry()["languages"].get(language_slug) or {}).get(kind)
    return entry if isinstance(entry, dict) else None


def contributor_ids(language_slug: str, role: str, kind: str = "research_corpus") -> list[str]:
    entry = language_entry(kind, language_slug) or {}
    return [str(item["person"]) for item in entry.get("contributors") or [] if isinstance(item, dict) and item.get("role") == role]


def _year(value: Any) -> str:
    text = str(value or "").strip()
    return text[:4] if _DATE_PATTERN.match(text) else ""


def _iso(value: Any) -> str | None:
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    return text if _DATE_PATTERN.match(text) else None


# --- resource model -------------------------------------------------------------------------------------------


def _resource(
    resource_type: str,
    *,
    resource_id: str,
    title: str,
    ui_lang: str,
    path: str,
    entry: dict[str, Any],
    language: str | None,
    is_part_of: dict[str, Any] | None,
    creators: list[dict[str, Any]] | None = None,
    date_published: Any = None,
    date_modified: Any = None,
    continuing: bool | None = None,
    status: str | None = None,
    description: str | None = None,
    subject_language: str | None = None,
) -> dict[str, Any]:
    platform = platform_entry()
    resolved_creators = creators if creators is not None else people(entry.get("creators"))
    resolved_status = status or str(entry.get("status") or "published")
    published = _iso(date_published if date_published is not None else entry.get("date_published"))
    resource = {
        "resource_id": resource_id,
        "resource_type": resource_type,
        "title": title,
        "description": description,
        "creators": resolved_creators,
        "contributors": [
            {"person": contributor, "role": item.get("role")}
            for item in entry.get("contributors") or []
            if isinstance(item, dict) and (contributor := person(str(item.get("person")))) is not None
        ],
        "editors": people(platform.get("editors")),
        "publisher": dict(platform.get("publisher") or {}),
        "date_published": published,
        "date_modified": _iso(date_modified if date_modified is not None else entry.get("date_modified")),
        "continuing": bool(entry.get("continuing")) if continuing is None else continuing,
        "version": entry.get("version") or None,
        "data_as_of": _iso(entry.get("data_as_of")),
        "language": language,
        "subject_language": subject_language,
        "ui_lang": ui_lang,
        "license": entry.get("license") or None,
        "doi": entry.get("doi") or None,
        "canonical_url": canonical_url(path),
        "is_part_of": is_part_of,
        "related_identifiers": list(entry.get("related_identifiers") or []),
        "status": resolved_status,
    }
    # Citable = a published scholarly unit with real responsible people and a publication date.
    resource["citable"] = bool(
        resolved_status == "published"
        and published
        and (resource["creators"] or resource_type == "platform")
        and all(creator["name"].lower() not in PLACEHOLDER_NAMES for creator in resource["creators"])
    )
    return resource


def platform_resource(ui_lang: str) -> dict[str, Any]:
    entry = platform_entry()
    description = (entry.get("description") or {}).get(ui_lang)
    return _resource(
        "platform",
        resource_id=str(entry["resource_id"]),
        title=str(entry["title"]),
        ui_lang=ui_lang,
        path=f"/{ui_lang}",
        entry=entry,
        language=None,
        is_part_of=None,
        creators=[],
        description=description,
    )


def platform_description(ui_lang: str) -> str:
    descriptions = platform_entry().get("description") or {}
    return str(descriptions.get(ui_lang) or descriptions.get("en") or "")


def corpus_resource(language_slug: str, ui_lang: str) -> dict[str, Any] | None:
    entry = language_entry("research_corpus", language_slug)
    if entry is None:
        return None
    return _resource(
        "research_corpus",
        resource_id=str(entry["resource_id"]),
        title=str(entry["title"]),
        ui_lang=ui_lang,
        path=f"/{ui_lang}/research/{language_slug}",
        entry=entry,
        language=CONTENT_LANGUAGE_CODES.get(language_slug),
        is_part_of=platform_resource(ui_lang),
    )


def teaching_area_resource(language_slug: str, ui_lang: str, *, has_public_topics: bool = True) -> dict[str, Any] | None:
    entry = language_entry("teaching_resource", language_slug)
    if entry is None:
        return None
    resource = _resource(
        "teaching_resource",
        resource_id=str(entry["resource_id"]),
        title=str(entry["title"]),
        ui_lang=ui_lang,
        path=f"/{ui_lang}/teaching/{language_slug}",
        entry=entry,
        language=ui_lang,
        subject_language=CONTENT_LANGUAGE_CODES.get(language_slug),
        is_part_of=platform_resource(ui_lang),
    )
    resource["citable"] = resource["citable"] and has_public_topics
    return resource


def design_resource(language_slug: str, ui_lang: str, title: str) -> dict[str, Any] | None:
    entry = language_entry("research_design", language_slug)
    if entry is None:
        return None
    return _resource(
        "research_design",
        resource_id=str(entry["resource_id"]),
        title=title,
        ui_lang=ui_lang,
        path=f"/{ui_lang}/research/{language_slug}/design",
        entry=entry,
        language=ui_lang,
        subject_language=CONTENT_LANGUAGE_CODES.get(language_slug),
        is_part_of=corpus_resource(language_slug, ui_lang),
        continuing=False,
    )


def topic_resource(
    language_slug: str,
    ui_lang: str,
    topic_slug: str,
    *,
    resource_id: str,
    title: str,
    creator_ids: Any,
    date_published: Any,
    date_modified: Any,
    description: str | None = None,
    doi: str | None = None,
    license_value: str | None = None,
    published: bool = True,
) -> dict[str, Any]:
    return _resource(
        "teaching_topic",
        resource_id=resource_id,
        title=title,
        ui_lang=ui_lang,
        path=f"/{ui_lang}/teaching/{language_slug}/{topic_slug}",
        entry={"doi": doi, "license": license_value},
        language=ui_lang,
        is_part_of=teaching_area_resource(language_slug, ui_lang),
        creators=people(creator_ids),
        date_published=date_published,
        date_modified=date_modified,
        continuing=False,
        status="published" if published else "in_preparation",
        description=description,
        subject_language=CONTENT_LANGUAGE_CODES.get(language_slug),
    )


# --- citation -------------------------------------------------------------------------------------------------


def _join_names(names: list[str]) -> str:
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " & " + names[-1]


def citation_year(resource: dict[str, Any]) -> str:
    """`2026–` for continuously maintained resources, the publication year for single published pages."""
    year = _year(resource.get("date_published"))
    return f"{year}–" if year and resource.get("continuing") else year


def resource_locator(resource: dict[str, Any]) -> str:
    """Where the resource is found: the DOI resolver once a DOI exists, otherwise the canonical URL."""
    return f"https://doi.org/{resource['doi']}" if resource.get("doi") else str(resource["canonical_url"])


def format_citation(resource: dict[str, Any], ui_lang: str) -> dict[str, str] | None:
    """Citation of a citable resource as plain text and as HTML; ``None`` when the resource is not citable."""
    if not resource.get("citable"):
        return None
    platform = platform_entry()
    resource_type = resource["resource_type"]
    authors = resource["editors"] if resource_type == "platform" else resource["creators"]
    author_text = _join_names([author["sort_name"] for author in authors])
    head = f"{author_text} ({citation_year(resource)})."
    publisher = str((resource.get("publisher") or {}).get("name") or "")
    locator = resource_locator(resource)
    title = str(resource["title"])
    open_quote, close_quote = _QUOTES.get(ui_lang, _QUOTES["en"])

    suffix_parts: list[str] = []
    if resource.get("version"):
        suffix_parts.append(f"Version {resource['version']}")
    if resource.get("data_as_of"):
        suffix_parts.append(f"{_DATA_AS_OF_LABELS.get(ui_lang, _DATA_AS_OF_LABELS['en'])}: {resource['data_as_of']}")
    title_suffix = f" ({'; '.join(suffix_parts)})" if suffix_parts else ""

    if resource_type in ("teaching_topic", "research_design"):
        title_text = f"{open_quote}{title}{close_quote}{title_suffix}."
        title_html = f"{open_quote}{escape(title)}{close_quote}{escape(title_suffix)}."
    else:
        title_text = f"{title}{title_suffix}."
        title_html = f"<em>{escape(title)}</em>{escape(title_suffix)}."

    container_text = container_html = ""
    if resource_type != "platform":
        editors = resource["editors"]
        singular, plural = _EDITOR_LABELS.get(ui_lang, _EDITOR_LABELS["en"])
        editor_text = f"{_join_names([editor['name'] for editor in editors])} ({plural if len(editors) > 1 else singular})"
        container_text = f" In: {editor_text}, {platform['title']}."
        container_html = f" In: {escape(editor_text)}, <em>{escape(str(platform['title']))}</em>."

    tail = f" {publisher}." if publisher else ""
    text = f"{head} {title_text}{container_text}{tail} {locator}"
    html = (
        f"{escape(head)} {title_html}{container_html}{escape(tail)} "
        f'<a href="{escape(locator, quote=True)}">{escape(locator)}</a>'
    )
    return {"text": text, "html": html}


# --- schema.org JSON-LD and reference-manager tags ------------------------------------------------------------


def _schema_person(entry: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {"@type": "Person", "name": entry["name"], "givenName": entry["given"], "familyName": entry["family"]}
    if entry.get("affiliation"):
        payload["affiliation"] = {"@type": "Organization", "name": entry["affiliation"]}
    if entry.get("orcid"):
        payload["sameAs"] = f"https://orcid.org/{entry['orcid']}"
    return payload


def _schema_publisher(resource: dict[str, Any]) -> dict[str, Any] | None:
    publisher = resource.get("publisher") or {}
    if not publisher.get("name"):
        return None
    payload = {"@type": "Organization", "name": publisher["name"]}
    if publisher.get("url"):
        payload["url"] = publisher["url"]
    return payload


def json_ld(resource: dict[str, Any]) -> dict[str, Any]:
    """schema.org description of a resource; only values that exist in the model are emitted."""
    payload: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": _SCHEMA_TYPES[resource["resource_type"]],
        "@id": resource["canonical_url"],
        "identifier": resource["resource_id"],
        "name": resource["title"],
        "url": resource["canonical_url"],
    }
    if resource["resource_type"] == "platform":
        short_title = platform_entry().get("short_title")
        if short_title:
            payload["alternateName"] = short_title
        payload["inLanguage"] = list(UI_LANGUAGES)
    if resource.get("description"):
        payload["description"] = resource["description"]
    if resource["creators"]:
        key = "creator" if resource["resource_type"] in ("research_corpus", "teaching_resource") else "author"
        payload[key] = [_schema_person(creator) for creator in resource["creators"]]
    if resource["resource_type"] == "platform" and resource["editors"]:
        payload["editor"] = [_schema_person(editor) for editor in resource["editors"]]
    contributors = {item["person"]["id"]: item["person"] for item in resource["contributors"]}
    creator_ids = {creator["id"] for creator in resource["creators"]}
    extra = [_schema_person(entry) for person_id, entry in contributors.items() if person_id not in creator_ids]
    if extra:
        payload["contributor"] = extra
    publisher = _schema_publisher(resource)
    if publisher:
        payload["publisher"] = publisher
    if resource.get("date_published"):
        payload["datePublished"] = resource["date_published"]
    modified = resource.get("date_modified") or resource.get("data_as_of")
    if modified:
        payload["dateModified"] = modified
    if resource.get("version"):
        payload["version"] = str(resource["version"])
    if resource.get("language") and "inLanguage" not in payload:
        payload["inLanguage"] = resource["language"]
    subject = resource.get("subject_language")
    if subject in SUBJECT_LANGUAGE_NAMES:
        payload["about"] = {"@type": "Language", "name": SUBJECT_LANGUAGE_NAMES[subject], "alternateName": subject}
    if resource.get("license"):
        payload["license"] = resource["license"]
    if resource.get("doi"):
        payload["sameAs"] = f"https://doi.org/{resource['doi']}"
    parent = resource.get("is_part_of")
    if parent:
        payload["isPartOf"] = {
            "@type": _SCHEMA_TYPES[parent["resource_type"]],
            "@id": parent["canonical_url"],
            "identifier": parent["resource_id"],
            "name": parent["title"],
        }
    return payload


def json_ld_script_text(resource: dict[str, Any]) -> str:
    """JSON for a ``<script type="application/ld+json">`` data block (cannot close the element early)."""
    return json.dumps(json_ld(resource), ensure_ascii=False, indent=None, separators=(",", ":")).replace("</", "<\\/")


def reference_manager_tags(resource: dict[str, Any]) -> list[tuple[str, str]]:
    """Highwire-style ``citation_*`` tags derived from the same model; browser reference managers read these."""
    if not resource.get("citable"):
        return []
    authors = resource["editors"] if resource["resource_type"] == "platform" else resource["creators"]
    tags: list[tuple[str, str]] = [("citation_title", str(resource["title"]))]
    tags += [("citation_author", author["sort_name"]) for author in authors]
    if resource.get("date_published"):
        tags.append(("citation_publication_date", str(resource["date_published"]).replace("-", "/")))
    if resource["resource_type"] != "platform":
        tags.append(("citation_inbook_title", str(platform_entry()["title"])))
    publisher = (resource.get("publisher") or {}).get("name")
    if publisher:
        tags.append(("citation_publisher", str(publisher)))
    if resource.get("language"):
        tags.append(("citation_language", str(resource["language"])))
    if resource.get("doi"):
        tags.append(("citation_doi", str(resource["doi"])))
    tags.append(("citation_public_url", str(resource["canonical_url"])))
    return tags


def author_names(resource: dict[str, Any]) -> list[str]:
    authors = resource["editors"] if resource["resource_type"] == "platform" else resource["creators"]
    return [author["name"] for author in authors]


# --- validation -----------------------------------------------------------------------------------------------


def _check_common(errors: list[str], where: str, entry: dict[str, Any], known_people: set[str]) -> None:
    resource_id = str(entry.get("resource_id") or "")
    if not _RESOURCE_ID_PATTERN.match(resource_id):
        errors.append(f"{where}: resource_id {resource_id!r} must be lower-case ASCII words joined by hyphens")
    for field in ("date_published", "date_modified", "data_as_of"):
        value = entry.get(field)
        if value is not None and not _DATE_PATTERN.match(str(value)):
            errors.append(f"{where}: {field} {value!r} must be YYYY or YYYY-MM-DD")
    doi = entry.get("doi")
    if doi is not None and not _DOI_PATTERN.match(str(doi)):
        errors.append(f"{where}: doi {doi!r} is not a DOI (expected 10.xxxx/...)")
    for person_id in list(entry.get("creators") or []) + list(entry.get("editors") or []):
        if person_id not in known_people:
            errors.append(f"{where}: unknown person {person_id!r}")
    for item in entry.get("contributors") or []:
        if not isinstance(item, dict) or item.get("person") not in known_people:
            errors.append(f"{where}: contributor {item!r} must reference a known person")
        elif item.get("role") not in CONTRIBUTOR_ROLES:
            errors.append(f"{where}: contributor role {item.get('role')!r} is not one of {CONTRIBUTOR_ROLES}")


def validate_registry() -> list[str]:
    """Structural and bibliographic checks of the registry; an empty list means valid."""
    registry = load_registry()
    errors: list[str] = []
    platform = registry["platform"]
    people_map = registry.get("people") or {}
    known_people = set(people_map)

    for field in ("resource_id", "title", "short_title", "canonical_base_url", "date_published"):
        if not str(platform.get(field) or "").strip():
            errors.append(f"platform: {field} is required")
    base_url = str(platform.get("canonical_base_url") or "")
    if not base_url.startswith("https://") or "://www." in base_url or base_url.endswith("/") or "?" in base_url:
        errors.append("platform: canonical_base_url must be an https origin without www, trailing slash or query")
    if not platform.get("editors"):
        errors.append("platform: at least one editor is required")
    if not (platform.get("publisher") or {}).get("name"):
        errors.append("platform: publisher.name is required")
    for ui_lang in UI_LANGUAGES:
        if not str((platform.get("description") or {}).get(ui_lang) or "").strip():
            errors.append(f"platform: description.{ui_lang} is required")
    _check_common(errors, "platform", platform, known_people)

    for person_id, raw in people_map.items():
        if not _RESOURCE_ID_PATTERN.match(str(person_id)):
            errors.append(f"people: id {person_id!r} must be lower-case ASCII words joined by hyphens")
        if not isinstance(raw, dict) or not str(raw.get("given") or "").strip() or not str(raw.get("family") or "").strip():
            errors.append(f"people.{person_id}: given and family name are required")
            continue
        if f"{raw['given']} {raw['family']}".strip().lower() in PLACEHOLDER_NAMES or str(raw["family"]).strip().lower() in PLACEHOLDER_NAMES:
            errors.append(f"people.{person_id}: placeholder names are not allowed")
        if raw.get("orcid") is not None and not _ORCID_PATTERN.match(str(raw["orcid"])):
            errors.append(f"people.{person_id}: orcid {raw['orcid']!r} must look like 0000-0000-0000-0000")

    seen_ids: dict[str, str] = {str(platform.get("resource_id")): "platform"}
    for language_slug, kinds in (registry.get("languages") or {}).items():
        if language_slug not in CONTENT_LANGUAGE_CODES:
            errors.append(f"languages.{language_slug}: unknown language slug")
        for kind, entry in (kinds or {}).items():
            where = f"languages.{language_slug}.{kind}"
            if kind not in LANGUAGE_RESOURCE_KINDS or not isinstance(entry, dict):
                errors.append(f"{where}: unknown resource kind")
                continue
            _check_common(errors, where, entry, known_people)
            resource_id = str(entry.get("resource_id") or "")
            if resource_id in seen_ids:
                errors.append(f"{where}: resource_id {resource_id!r} is already used by {seen_ids[resource_id]}")
            seen_ids[resource_id] = where
            status = entry.get("status")
            if status not in RESOURCE_STATUSES:
                errors.append(f"{where}: status {status!r} must be one of {RESOURCE_STATUSES}")
            if kind != "research_design" and not str(entry.get("title") or "").strip():
                errors.append(f"{where}: title is required")
            if status == "published":
                if not entry.get("creators"):
                    errors.append(f"{where}: a published resource needs at least one creator")
                if not entry.get("date_published"):
                    errors.append(f"{where}: a published resource needs date_published")
    return errors


def registry_resource_ids() -> dict[str, str]:
    """All resource ids of the registry mapped to where they are defined (for duplicate checks across content)."""
    registry = load_registry()
    ids = {str(registry["platform"].get("resource_id")): "platform"}
    for language_slug, kinds in (registry.get("languages") or {}).items():
        for kind, entry in (kinds or {}).items():
            if isinstance(entry, dict) and entry.get("resource_id"):
                ids[str(entry["resource_id"])] = f"languages.{language_slug}.{kind}"
    return ids
