"""Split overview and editor view-model builders for phenomena."""

from __future__ import annotations

from typing import Any

from flask import g, request, url_for

from .content_navigation import build_content_header
from .research_presets import ResearchConfigError, load_phenomena_preset_map, load_phenomena_presets, load_task_catalogs
from .research_sets import (
    ResearchSetNotFoundError,
    ResearchSetStorageUnavailableError,
    ResearchSetValidationError,
    StoredResearchSet,
    StoredResearchSetItem,
    list_owned_sets,
    load_owned_set,
)
from .routes.public_content import get_language, get_language_label, get_research_page_label, get_section_label


PHENOMENA_TASKS: tuple[str, ...] = ("wordlist", "text")


def _current_owner_user_id() -> str | None:
    candidate = getattr(g, "user_id", None)
    if isinstance(candidate, str) and candidate.strip():
        return candidate.strip()
    return None


def _is_authenticated() -> bool:
    return _current_owner_user_id() is not None


def _editor_status_labels(ui_lang: str) -> dict[str, str]:
    if ui_lang == "de":
        return {
            "curated": "curated",
            "custom": "custom",
            "saved": "gespeichert",
            "unsaved": "ungespeichert",
            "new": "neu",
        }
    return {
        "curated": "curated",
        "custom": "custom",
        "saved": "saved",
        "unsaved": "unsaved",
        "new": "new",
    }


def _catalog_payload(language_slug: str, ui_lang: str) -> tuple[dict[str, list[dict[str, str | None]]], dict[str, str]]:
    catalogs = load_task_catalogs(language_slug)
    task_labels = {
        "wordlist": "Wortliste" if ui_lang == "de" else "Word list",
        "text": catalogs["text"].display_label or ("Satzliste" if ui_lang == "de" else "Sentence list"),
    }
    payload: dict[str, list[dict[str, str | None]]] = {}
    for task_key in PHENOMENA_TASKS:
        catalog = catalogs[task_key]
        payload[task_key] = [
            {
                "task": item.task,
                "item_id": item.item_id,
                "item_number": item.item_number,
                "text": item.text,
                "group_id": item.group_id,
            }
            for item in catalog.items_by_id.values()
        ]
    return payload, task_labels


def _catalog_lookup(catalogs_by_task: dict[str, list[dict[str, str | None]]]) -> dict[tuple[str, str], dict[str, str | None]]:
    lookup: dict[tuple[str, str], dict[str, str | None]] = {}
    for task_key, items in catalogs_by_task.items():
        for item in items:
            item_id = item.get("item_id")
            if isinstance(item_id, str):
                lookup[(task_key, item_id)] = item
    return lookup


def _preview_text(
    references: tuple[StoredResearchSetItem, ...] | tuple[Any, ...],
    *,
    catalogs_by_task: dict[str, list[dict[str, str | None]]],
) -> str:
    reference_list = list(references)
    lookup = _catalog_lookup(catalogs_by_task)
    preview_parts: list[str] = []
    for reference in reference_list[:3]:
        task = getattr(reference, "task", None) or reference.get("task")
        item_id = getattr(reference, "item_id", None) or reference.get("item_id")
        if not isinstance(task, str) or not isinstance(item_id, str):
            continue
        catalog_item = lookup.get((task, item_id))
        if catalog_item is None:
            preview_parts.append(item_id)
            continue
        item_number = catalog_item.get("item_number") or item_id
        text = catalog_item.get("text") or item_id
        preview_parts.append(f"{item_number} {text}")
    if len(reference_list) > 3 and preview_parts:
        preview_parts.append("…")
    return " · ".join(preview_parts)


def _phenomena_intro(ui_lang: str) -> str:
    if ui_lang == "de":
        return "Kuratierte Sets öffnen, bearbeiten oder ein neues Set mit ausgewählten Items aus Wortliste und Text anlegen."
    return "Open curated sets, edit them, or create a new set from selected word-list and sentence-list items."


def _display_set_label(label: str | None, ui_lang: str) -> str:
    normalized = (label or "").strip()
    if normalized:
        return normalized
    return "Ohne Titel" if ui_lang == "de" else "Untitled"


def _editor_intro(ui_lang: str) -> str:
    return "Set bearbeiten" if ui_lang == "de" else "Edit set"


def _base_page(title: str, *, ui_lang: str, language_slug: str) -> dict[str, Any]:
    language = get_language(language_slug)
    language_label = get_language_label(language, ui_lang) if language else language_slug
    return {
        "title": title,
        "page_kind": "workbench",
        "access": "public",
        "content_header": build_content_header(
            page_name="research",
            title=title,
            intro=_phenomena_intro(ui_lang),
            section_label=get_section_label("research", ui_lang),
            section_href=url_for("public.research_home", ui_lang=ui_lang),
            context_mode="language",
            context_title=language_label,
            context_root_href=url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug),
        ),
    }


def _editor_page(title: str, *, ui_lang: str, language_slug: str) -> dict[str, Any]:
    language = get_language(language_slug)
    language_label = get_language_label(language, ui_lang) if language else language_slug
    overview_href = url_for(
        "public.research_language_page",
        ui_lang=ui_lang,
        language_slug=language_slug,
        page_slug="phenomena",
    )
    return {
        "title": title,
        "page_kind": "workbench",
        "access": "public",
        "content_header": build_content_header(
            page_name="research",
            title=title,
            intro=_editor_intro(ui_lang),
            section_label=get_section_label("research", ui_lang),
            section_href=url_for("public.research_home", ui_lang=ui_lang),
            context_mode="language",
            context_title=language_label,
            context_root_href=url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug),
            ancestors=[{"label": get_research_page_label("phenomena", ui_lang), "href": overview_href}],
        ),
    }


def _overview_card_from_preset(
    *,
    preset,
    ui_lang: str,
    language_slug: str,
    catalogs_by_task: dict[str, list[dict[str, str | None]]],
) -> dict[str, Any]:
    return {
        "entry_id": f"preset:{preset.preset_id}",
        "kind": "curated",
        "title": preset.label,
        "item_count": len(preset.items),
        "preview": _preview_text(preset.items, catalogs_by_task=catalogs_by_task),
        "status_label": "curated",
        "open_href": url_for(
            "public.research_phenomena_preset_editor",
            ui_lang=ui_lang,
            language_slug=language_slug,
            preset_id=preset.preset_id,
        ),
        "preset_id": preset.preset_id,
    }


def _overview_card_from_set(
    *,
    stored_set: StoredResearchSet,
    ui_lang: str,
    language_slug: str,
    catalogs_by_task: dict[str, list[dict[str, str | None]]],
) -> dict[str, Any]:
    return {
        "entry_id": f"set:{stored_set.set_id}",
        "kind": "custom",
        "title": stored_set.label or ("Ohne Titel" if ui_lang == "de" else "Untitled"),
        "item_count": len(stored_set.items),
        "preview": _preview_text(stored_set.items, catalogs_by_task=catalogs_by_task),
        "status_label": "custom",
        "open_href": url_for(
            "public.research_phenomena_set_editor",
            ui_lang=ui_lang,
            language_slug=language_slug,
            set_id=stored_set.set_id,
        ),
        "set_id": stored_set.set_id,
        "updated_at": stored_set.updated_at.isoformat(),
    }


def build_phenomena_overview_page(ui_lang: str, language_slug: str) -> dict[str, Any] | None:
    language = get_language(language_slug)
    if language is None:
        return None

    catalogs_by_task, task_labels = _catalog_payload(language_slug, ui_lang)
    curated_entries = [
        _overview_card_from_preset(
            preset=preset,
            ui_lang=ui_lang,
            language_slug=language_slug,
            catalogs_by_task=catalogs_by_task,
        )
        for preset in load_phenomena_presets(language_slug)
    ]

    custom_entries: list[dict[str, Any]] = []
    if _is_authenticated():
        try:
            custom_entries = [
                _overview_card_from_set(
                    stored_set=stored_set,
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    catalogs_by_task=catalogs_by_task,
                )
                for stored_set in list_owned_sets(
                    owner_user_id=_current_owner_user_id() or "",
                    corpus_language=language_slug,
                )
            ]
        except (ResearchSetStorageUnavailableError, ResearchSetValidationError):
            custom_entries = []

    page = _base_page(get_research_page_label("phenomena", ui_lang), ui_lang=ui_lang, language_slug=language_slug)
    page.update(
        {
            "template": "pages/research_phenomena_overview.html",
            "heading": "1 Set wählen" if ui_lang == "de" else "1 Choose a set",
            "search_placeholder": "Set suchen" if ui_lang == "de" else "Search sets",
            "new_set_label": "Neues Set" if ui_lang == "de" else "New set",
            "entries": curated_entries + custom_entries,
            "empty_title": "Keine Sets gefunden." if ui_lang == "de" else "No sets found.",
            "empty_text": "Passen Sie die Suche an oder legen Sie ein neues Set an." if ui_lang == "de" else "Adjust the search or create a new set.",
            "is_authenticated": _is_authenticated(),
            "client_state": {
                "uiLang": ui_lang,
                "languageSlug": language_slug,
                "isAuthenticated": _is_authenticated(),
                "entries": curated_entries + custom_entries,
                "createSetUrl": url_for("research_api.create_set"),
                "patchSetUrlTemplate": url_for("research_api.patch_set", set_id="__SET_ID__"),
                "deleteSetUrlTemplate": url_for("research_api.delete_set", set_id="__SET_ID__"),
                "setEditorHrefTemplate": url_for(
                    "public.research_phenomena_set_editor",
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    set_id="__SET_ID__",
                ),
                "loginHref": url_for("public.login", next=request.full_path or request.path),
                "labels": {
                    "newSet": "Neues Set" if ui_lang == "de" else "New set",
                    "renameTitle": "Set umbenennen" if ui_lang == "de" else "Rename set",
                    "renameConfirm": "Speichern" if ui_lang == "de" else "Save",
                    "renameCancel": "Abbrechen" if ui_lang == "de" else "Cancel",
                    "deleteTitle": "Eigenes Set löschen?" if ui_lang == "de" else "Delete custom set?",
                    "deleteConfirm": "Löschen" if ui_lang == "de" else "Delete",
                    "deleteCancel": "Abbrechen" if ui_lang == "de" else "Cancel",
                    "deleteMessage": "„{label}“ wird dauerhaft entfernt." if ui_lang == "de" else '"{label}" will be permanently removed.',
                    "view": "Ansehen" if ui_lang == "de" else "View",
                    "edit": "Bearbeiten" if ui_lang == "de" else "Edit",
                    "modify": "Modifizieren" if ui_lang == "de" else "Modify",
                    "rename": "Umbenennen" if ui_lang == "de" else "Rename",
                    "delete": "Löschen" if ui_lang == "de" else "Delete",
                    "createError": "Set konnte nicht erstellt werden." if ui_lang == "de" else "Could not create set.",
                    "renameSuccess": "Set wurde umbenannt." if ui_lang == "de" else "Set renamed.",
                    "deleteSuccess": "Set wurde gelöscht." if ui_lang == "de" else "Set deleted.",
                    "itemsLabel": "Items" if ui_lang == "de" else "Items",
                    "emptyTitle": "Keine Sets gefunden." if ui_lang == "de" else "No sets found.",
                    "emptyText": "Passen Sie die Suche an oder legen Sie ein neues Set an." if ui_lang == "de" else "Adjust the search or create a new set.",
                },
                "taskLabels": task_labels,
            },
        }
    )
    return page


def _editor_record_from_preset(language_slug: str, preset_id: str) -> dict[str, Any] | None:
    try:
        preset = load_phenomena_preset_map(language_slug)[preset_id]
    except (KeyError, ResearchConfigError):
        return None

    return {
        "set_id": None,
        "corpus_language": language_slug,
        "label": preset.label,
        "note": None,
        "state": "curated",
        "source_preset_id": preset.preset_id,
        "preferred_task": None,
        "comparison_view_task": "all",
        "created_at": None,
        "updated_at": None,
        "last_accessed_at": None,
        "expires_at": None,
        "items": [
            {
                "task": reference.task,
                "item_id": reference.item_id,
                "sort_order": index,
                "segment_id": reference.segment_id,
                "note": reference.note,
            }
            for index, reference in enumerate(preset.items, start=1)
        ],
        "sessions": [],
    }


def _editor_state(
    *,
    ui_lang: str,
    language_slug: str,
    record: dict[str, Any],
    editor_mode: str,
) -> dict[str, Any]:
    catalogs_by_task, task_labels = _catalog_payload(language_slug, ui_lang)
    return {
        "uiLang": ui_lang,
        "languageSlug": language_slug,
        "editorMode": editor_mode,
        "isAuthenticated": _is_authenticated(),
        "initialRecord": record,
        "catalogsByTask": catalogs_by_task,
        "taskLabels": task_labels,
        "statusLabels": _editor_status_labels(ui_lang),
        "createSetUrl": url_for("research_api.create_set"),
        "patchSetUrlTemplate": url_for("research_api.patch_set", set_id="__SET_ID__"),
        "putItemsUrlTemplate": url_for("research_api.put_set_items", set_id="__SET_ID__"),
        "deleteSetUrlTemplate": url_for("research_api.delete_set", set_id="__SET_ID__"),
        "overviewHref": url_for(
            "public.research_language_page",
            ui_lang=ui_lang,
            language_slug=language_slug,
            page_slug="phenomena",
        ),
        "setEditorHrefTemplate": url_for(
            "public.research_phenomena_set_editor",
            ui_lang=ui_lang,
            language_slug=language_slug,
            set_id="__SET_ID__",
        ),
        "loginHref": url_for("public.login", next=request.full_path or request.path),
        "labels": {
            "save": "Speichern" if ui_lang == "de" else "Save",
            "discard": "Entwurf verwerfen" if ui_lang == "de" else "Discard draft",
            "delete": "Set löschen" if ui_lang == "de" else "Delete set",
            "note": "Notiz" if ui_lang == "de" else "Note",
            "wordlist": task_labels["wordlist"],
            "text": task_labels["text"],
            "searchWordlist": "Wortliste durchsuchen" if ui_lang == "de" else "Search word list",
            "searchText": "Satzliste durchsuchen" if ui_lang == "de" else "Search sentence list",
            "selectAll": "Alle auswählen" if ui_lang == "de" else "Select all",
            "clearAll": "Alle abwählen" if ui_lang == "de" else "Clear all",
            "selectedItems": "Ausgewählte Items" if ui_lang == "de" else "Selected items",
            "selectedEmpty": "Noch keine Items ausgewählt." if ui_lang == "de" else "No items selected yet.",
            "remove": "Entfernen" if ui_lang == "de" else "Remove",
            "dragHandle": "Reihenfolge ändern" if ui_lang == "de" else "Change order",
            "curatedHint": "Änderungen an diesem kuratierten Set werden als neues eigenes Set gespeichert." if ui_lang == "de" else "Changes to this curated set are saved as a new custom set.",
            "saveSuccess": "Set wurde gespeichert." if ui_lang == "de" else "Set saved.",
            "saveError": "Set konnte nicht gespeichert werden." if ui_lang == "de" else "Could not save set.",
            "deleteTitle": "Eigenes Set löschen?" if ui_lang == "de" else "Delete custom set?",
            "deleteMessage": "„{label}“ wird dauerhaft entfernt." if ui_lang == "de" else '"{label}" will be permanently removed.',
            "discardTitle": "Ungespeicherte Änderungen verwerfen?" if ui_lang == "de" else "Discard unsaved changes?",
            "discardMessage": "Änderungen gehen verloren." if ui_lang == "de" else "Changes will be lost.",
            "confirmDelete": "Löschen" if ui_lang == "de" else "Delete",
            "confirmDiscard": "Verwerfen" if ui_lang == "de" else "Discard",
            "cancel": "Abbrechen" if ui_lang == "de" else "Cancel",
            "typeWordlist": "Wortliste" if ui_lang == "de" else "Word list",
            "typeText": task_labels["text"],
            "savedStateText": "Stand gespeichert." if ui_lang == "de" else "Set saved.",
            "unsavedStateText": "Änderungen noch nicht gespeichert." if ui_lang == "de" else "Changes not saved yet.",
            "unsavedLeave": "Ungespeicherte Änderungen verwerfen?" if ui_lang == "de" else "Discard unsaved changes?",
        },
    }


def build_phenomena_preset_editor_page(ui_lang: str, language_slug: str, preset_id: str) -> dict[str, Any] | None:
    language = get_language(language_slug)
    if language is None:
        return None
    record = _editor_record_from_preset(language_slug, preset_id)
    if record is None:
        return None

    page = _editor_page(_display_set_label(record.get("label"), ui_lang), ui_lang=ui_lang, language_slug=language_slug)
    page.update(
        {
            "template": "pages/research_phenomena_editor.html",
            "editor_hint": "Kuratiertes Set" if ui_lang == "de" else "Curated set",
            "client_state": _editor_state(ui_lang=ui_lang, language_slug=language_slug, record=record, editor_mode="preset"),
        }
    )
    return page


def build_phenomena_set_editor_page(ui_lang: str, language_slug: str, set_id: str) -> dict[str, Any] | None:
    language = get_language(language_slug)
    if language is None:
        return None
    owner_user_id = _current_owner_user_id()
    if owner_user_id is None:
        return None

    try:
        stored_set = load_owned_set(owner_user_id=owner_user_id, set_id=set_id, touch_access=True)
    except (ResearchSetNotFoundError, ResearchSetValidationError, ResearchSetStorageUnavailableError):
        return None

    record = stored_set.to_dict()
    page = _editor_page(_display_set_label(record.get("label"), ui_lang), ui_lang=ui_lang, language_slug=language_slug)
    page.update(
        {
            "template": "pages/research_phenomena_editor.html",
            "editor_hint": "Eigenes Set" if ui_lang == "de" else "Custom set",
            "client_state": _editor_state(ui_lang=ui_lang, language_slug=language_slug, record=record, editor_mode="set"),
        }
    )
    return page