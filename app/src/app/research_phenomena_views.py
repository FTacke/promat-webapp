"""Split overview and editor view-model builders for phenomena."""

from __future__ import annotations

from typing import Any

from flask import g, request, url_for

from .content_navigation import build_content_header
from .i18n import translate, translate_many
from .research_capabilities import get_research_task_label, phenomena_task_keys
from .research_presets import load_task_catalogs
from .research_sessions import load_language_sessions
from .research_sets import (
    ResearchSetNotFoundError,
    ResearchSetStorageUnavailableError,
    ResearchSetValidationError,
    StoredResearchSet,
    StoredResearchSetItem,
    get_visible_set,
    list_visible_sets_for_user,
)
from .routes.public_content import get_language, get_research_corpus_title, get_research_page_label, get_section_label


PHENOMENA_TASKS: tuple[str, ...] = phenomena_task_keys()


def _t(ui_lang: str, key: str, **kwargs: object) -> str:
    return translate(ui_lang, key, **kwargs)


def _current_owner_user_id() -> str | None:
    candidate = getattr(g, "user_id", None)
    if isinstance(candidate, str) and candidate.strip():
        return candidate.strip()
    return None


def _is_authenticated() -> bool:
    return _current_owner_user_id() is not None


def _is_admin() -> bool:
    return getattr(g, "role", None) == "admin"


def _editor_status_labels(ui_lang: str) -> dict[str, str]:
    return translate_many(
        ui_lang,
        {
            "curated": "common.status.curated",
            "custom": "common.status.custom",
            "archived": "common.status.archived",
            "saved": "common.status.saved",
            "unsaved": "common.status.unsaved",
            "new": "common.status.new",
        },
    )


def _catalog_payload(language_slug: str, ui_lang: str) -> tuple[dict[str, list[dict[str, str | None]]], dict[str, str]]:
    catalogs = load_task_catalogs(language_slug)
    task_labels = {
        task_key: get_research_task_label(task_key, ui_lang, variant="material", language_slug=language_slug)
        for task_key in PHENOMENA_TASKS
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
    return _t(ui_lang, "research.phenomena.intro")


def _display_set_label(label: str | None, ui_lang: str) -> str:
    normalized = (label or "").strip()
    if normalized:
        return normalized
    return _t(ui_lang, "common.untitled")


def _editor_intro(ui_lang: str) -> str:
    return _t(ui_lang, "research.phenomena.editor_intro")


def _base_page(title: str, *, ui_lang: str, language_slug: str) -> dict[str, Any]:
    language = get_language(language_slug)
    corpus_title = get_research_corpus_title(language, ui_lang) if language else language_slug
    return {
        "title": title,
        "page_kind": "workbench",
        "access": "protected",
        "content_header": build_content_header(
            page_name="research",
            title=title,
            intro=_phenomena_intro(ui_lang),
            section_label=get_section_label("research", ui_lang),
            section_href=url_for("public.research_home", ui_lang=ui_lang),
            context_mode="language",
            context_title=corpus_title,
            context_root_href=url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug),
        ),
    }


def _editor_page(title: str, *, ui_lang: str, language_slug: str) -> dict[str, Any]:
    language = get_language(language_slug)
    corpus_title = get_research_corpus_title(language, ui_lang) if language else language_slug
    overview_href = url_for(
        "public.research_language_page",
        ui_lang=ui_lang,
        language_slug=language_slug,
        page_slug="phenomena",
    )
    return {
        "title": title,
        "page_kind": "workbench",
        "access": "protected",
        "content_header": build_content_header(
            page_name="research",
            title=title,
            intro=_editor_intro(ui_lang),
            section_label=get_section_label("research", ui_lang),
            section_href=url_for("public.research_home", ui_lang=ui_lang),
            context_mode="language",
            context_title=corpus_title,
            context_root_href=url_for("public.research_language_root", ui_lang=ui_lang, language_slug=language_slug),
            ancestors=[{"label": get_research_page_label("phenomena", ui_lang), "href": overview_href}],
            back_link={"label": get_research_page_label("phenomena", ui_lang), "href": overview_href},
        ),
    }


def _overview_card_from_curated_set(
    *,
    stored_set: StoredResearchSet,
    own_copy_set: StoredResearchSet | None,
    is_admin: bool,
    ui_lang: str,
    language_slug: str,
    catalogs_by_task: dict[str, list[dict[str, str | None]]],
) -> dict[str, Any]:
    editor_href = url_for(
        "public.research_phenomena_preset_editor",
        ui_lang=ui_lang,
        language_slug=language_slug,
        preset_id=stored_set.set_id,
    )
    return {
        "entry_id": f"set:{stored_set.set_id}",
        "kind": "curated",
        "title": _display_set_label(stored_set.label, ui_lang),
        "item_count": len(stored_set.items),
        "preview": _preview_text(stored_set.items, catalogs_by_task=catalogs_by_task),
        "status_label": _t(
            ui_lang,
            "common.status.archived" if stored_set.lifecycle == "archived" else "common.status.curated",
        ),
        "open_href": editor_href,
        "view_href": editor_href,
        "edit_curated_href": editor_href if is_admin else None,
        "edit_as_own_href": (
            url_for(
                "public.research_phenomena_set_editor",
                ui_lang=ui_lang,
                language_slug=language_slug,
                set_id=own_copy_set.set_id,
            )
            if own_copy_set is not None
            else None
        ),
        "copy_source_set_id": stored_set.set_id,
        "preset_id": stored_set.set_id,
        "set_id": stored_set.set_id,
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
        "title": _display_set_label(stored_set.label, ui_lang),
        "item_count": len(stored_set.items),
        "preview": _preview_text(stored_set.items, catalogs_by_task=catalogs_by_task),
        "status_label": _t(ui_lang, "common.status.custom"),
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
    has_runtime_data = bool(load_language_sessions(language_slug))
    curated_entries: list[dict[str, Any]] = []
    custom_entries: list[dict[str, Any]] = []
    private_copy_targets: dict[str, StoredResearchSet] = {}
    owner_user_id = _current_owner_user_id()
    if has_runtime_data:
        try:
            visible_sets = list_visible_sets_for_user(
                owner_user_id=owner_user_id,
                corpus_language=language_slug,
                include_drafts=False,
                include_archived_curated=_is_admin(),
            )
        except (ResearchSetStorageUnavailableError, ResearchSetValidationError, RuntimeError):
            visible_sets = tuple()

        if owner_user_id is not None:
            try:
                private_copy_candidates = list_visible_sets_for_user(
                    owner_user_id=owner_user_id,
                    corpus_language=language_slug,
                    include_drafts=True,
                    include_archived_curated=_is_admin(),
                )
            except (ResearchSetStorageUnavailableError, ResearchSetValidationError, RuntimeError):
                private_copy_candidates = tuple()
            for candidate in private_copy_candidates:
                if candidate.visibility != "private" or not candidate.source_curated_set_id:
                    continue
                private_copy_targets.setdefault(candidate.source_curated_set_id, candidate)

        for stored_set in visible_sets:
            if stored_set.visibility == "curated":
                curated_entries.append(
                    _overview_card_from_curated_set(
                        stored_set=stored_set,
                        own_copy_set=private_copy_targets.get(stored_set.set_id),
                        is_admin=_is_admin(),
                        ui_lang=ui_lang,
                        language_slug=language_slug,
                        catalogs_by_task=catalogs_by_task,
                    )
                )
                continue
            custom_entries.append(
                _overview_card_from_set(
                    stored_set=stored_set,
                    ui_lang=ui_lang,
                    language_slug=language_slug,
                    catalogs_by_task=catalogs_by_task,
                )
            )

    page = _base_page(get_research_page_label("phenomena", ui_lang), ui_lang=ui_lang, language_slug=language_slug)
    page.update(
        {
            "template": "pages/research_phenomena_overview.html",
            "heading": _t(ui_lang, "research.phenomena.overview.heading"),
            "search_placeholder": _t(ui_lang, "research.phenomena.overview.search_placeholder"),
            "new_set_label": _t(ui_lang, "research.phenomena.overview.new_set"),
            "entries": curated_entries + custom_entries,
            "empty_title": _t(ui_lang, "research.phenomena.overview.no_data_title") if not has_runtime_data else _t(ui_lang, "research.phenomena.overview.empty_title"),
            "empty_text": "" if not has_runtime_data else _t(ui_lang, "research.phenomena.overview.empty_text"),
            "is_authenticated": _is_authenticated(),
            "client_state": {
                "uiLang": ui_lang,
                "languageSlug": language_slug,
                "isAuthenticated": _is_authenticated(),
                "hasRuntimeData": has_runtime_data,
                "entries": curated_entries + custom_entries,
                "createSetUrl": url_for("research_api.create_set"),
                "privateCopySetUrlTemplate": url_for("research_api.private_copy_set", set_id="__SET_ID__"),
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
                    **translate_many(
                        ui_lang,
                        {
                            "newSet": "research.phenomena.overview.new_set",
                            "renameTitle": "research.phenomena.overview.rename_title",
                            "renameConfirm": "common.actions.save",
                            "renameCancel": "common.actions.cancel",
                            "deleteTitle": "research.phenomena.overview.delete_title",
                            "deleteConfirm": "common.actions.delete",
                            "deleteCancel": "common.actions.cancel",
                            "view": "common.actions.view",
                            "edit": "common.actions.edit",
                            "editCurated": "common.actions.edit_curated",
                            "editAsOwnSet": "common.actions.edit_as_own_set",
                            "rename": "common.actions.rename",
                            "delete": "common.actions.delete",
                            "createError": "research.phenomena.overview.create_error",
                            "renameSuccess": "research.phenomena.overview.rename_success",
                            "deleteSuccess": "research.phenomena.overview.delete_success",
                            "itemsLabel": "common.labels.items_count",
                            "emptyTitle": "research.phenomena.overview.empty_title",
                            "emptyText": "research.phenomena.overview.empty_text",
                            "noDataTitle": "research.phenomena.overview.no_data_title",
                            "requestFailed": "common.errors.request_failed",
                            "moreActions": "common.actions.more",
                        },
                    ),
                    "deleteMessage": _t(ui_lang, "research.phenomena.overview.delete_message", label="{label}"),
                    "untitled": _t(ui_lang, "common.untitled"),
                },
                "taskLabels": task_labels,
            },
        }
    )
    return page


def _editor_record_from_preset(language_slug: str, preset_id: str) -> dict[str, Any] | None:
    try:
        stored_set = get_visible_set(
            owner_user_id=_current_owner_user_id(),
            set_id=preset_id,
            include_archived_curated=_is_admin(),
            touch_access=False,
        )
    except (ResearchSetNotFoundError, ResearchSetValidationError, ResearchSetStorageUnavailableError, RuntimeError):
        return None
    if stored_set.corpus_language != language_slug or stored_set.visibility != "curated":
        return None
    return stored_set.to_dict()


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
        "isAdmin": _is_admin(),
        "initialRecord": record,
        "catalogsByTask": catalogs_by_task,
        "taskLabels": task_labels,
        "statusLabels": _editor_status_labels(ui_lang),
        "createSetUrl": url_for("research_api.create_set"),
        "adminUpdateCuratedSetUrlTemplate": url_for("research_api.update_admin_curated_set", set_id="__SET_ID__"),
        "adminDeleteCuratedSetUrlTemplate": url_for("research_api.delete_admin_curated_set", set_id="__SET_ID__"),
        "adminCreateCuratedFromCustomUrl": url_for("research_api.create_admin_curated_set_from_custom"),
        "adminArchiveCuratedSetUrlTemplate": url_for("research_api.archive_admin_curated_set", set_id="__SET_ID__"),
        "adminReactivateCuratedSetUrlTemplate": url_for("research_api.reactivate_admin_curated_set", set_id="__SET_ID__"),
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
        "presetEditorHrefTemplate": url_for(
            "public.research_phenomena_preset_editor",
            ui_lang=ui_lang,
            language_slug=language_slug,
            preset_id="__SET_ID__",
        ),
        "loginHref": url_for("public.login", next=request.full_path or request.path),
        "labels": {
            **translate_many(
                ui_lang,
                {
                    "save": "common.actions.save",
                    "discard": "research.phenomena.editor.discard",
                    "delete": "research.phenomena.editor.delete",
                    "note": "common.note",
                    "searchWordlist": "research.phenomena.editor.search_wordlist",
                    "searchText": "research.phenomena.editor.search_text",
                    "selectAll": "common.actions.select_all",
                    "clearAll": "common.actions.clear_all",
                    "selectedItems": "research.phenomena.editor.selected_items",
                    "selectedEmpty": "research.phenomena.editor.selected_empty",
                    "remove": "common.actions.remove",
                    "dragHandle": "research.phenomena.editor.drag_handle",
                    "curatedHint": "research.phenomena.editor.curated_hint",
                    "curatedAdminHint": "research.phenomena.editor.curated_admin_hint",
                    "discardChanges": "research.phenomena.editor.discard_changes",
                    "curatedCopyHint": "research.phenomena.editor.curated_copy_hint",
                    "saveSuccess": "research.phenomena.editor.save_success",
                    "saveError": "research.phenomena.editor.save_error",
                    "updateCurated": "research.phenomena.editor.update_curated",
                    "updateCuratedTitle": "research.phenomena.editor.update_curated_title",
                    "updateCuratedMessage": "research.phenomena.editor.update_curated_message",
                    "deleteCurated": "research.phenomena.editor.delete_curated",
                    "deleteCuratedTitle": "research.phenomena.editor.delete_curated_title",
                    "deleteCuratedSuccess": "research.phenomena.editor.delete_curated_success",
                    "saveAsCurated": "research.phenomena.editor.save_as_curated",
                    "saveAsCuratedTitle": "research.phenomena.editor.save_as_curated_title",
                    "saveAsCuratedMessage": "research.phenomena.editor.save_as_curated_message",
                    "saveAsCuratedSuccess": "research.phenomena.editor.save_as_curated_success",
                    "saveCopyTitle": "research.phenomena.editor.save_copy_title",
                    "saveCopyMessage": "research.phenomena.editor.save_copy_message",
                    "saveAsCustom": "research.phenomena.editor.save_as_custom",
                    "saveAsCustomTitle": "research.phenomena.editor.save_as_custom_title",
                    "saveAsCustomMessage": "research.phenomena.editor.save_as_custom_message",
                    "saveAsCustomSuccess": "research.phenomena.editor.save_as_custom_success",
                    "archiveCurated": "research.phenomena.editor.archive_curated",
                    "reactivateCurated": "research.phenomena.editor.reactivate_curated",
                    "archiveCuratedTitle": "research.phenomena.editor.archive_curated_title",
                    "archiveCuratedMessage": "research.phenomena.editor.archive_curated_message",
                    "reactivateCuratedTitle": "research.phenomena.editor.reactivate_curated_title",
                    "reactivateCuratedMessage": "research.phenomena.editor.reactivate_curated_message",
                    "archiveSuccess": "research.phenomena.editor.archive_success",
                    "reactivateSuccess": "research.phenomena.editor.reactivate_success",
                    "archivedStateText": "research.phenomena.editor.archived_state_text",
                    "requestFailed": "common.errors.request_failed",
                    "deleteTitle": "research.phenomena.editor.delete_title",
                    "discardTitle": "research.phenomena.editor.discard_title",
                    "discardMessage": "research.phenomena.editor.discard_message",
                    "confirmDelete": "common.actions.delete",
                    "confirmDiscard": "common.actions.discard",
                    "cancel": "common.actions.cancel",
                    "savedStateText": "research.phenomena.editor.saved_state_text",
                    "unsavedStateText": "research.phenomena.editor.unsaved_state_text",
                    "unsavedLeave": "research.phenomena.editor.unsaved_leave",
                    "title": "common.title",
                    "editName": "research.phenomena.editor.edit_name",
                    "notePlaceholder": "research.phenomena.editor.note_placeholder",
                    "untitled": "common.untitled",
                },
            ),
            "wordlist": task_labels["wordlist"],
            "text": task_labels["text"],
            "deleteMessage": _t(ui_lang, "research.phenomena.editor.delete_message", label="{label}"),
            "deleteCuratedMessage": _t(ui_lang, "research.phenomena.editor.delete_curated_message", label="{label}"),
            "typeWordlist": task_labels["wordlist"],
            "typeText": task_labels["text"],
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
            "editor_hint": _t(ui_lang, "research.phenomena.editor.hint_curated"),
            "is_admin": _is_admin(),
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
        stored_set = get_visible_set(
            owner_user_id=owner_user_id,
            set_id=set_id,
            include_archived_curated=_is_admin(),
            touch_access=True,
        )
    except (ResearchSetNotFoundError, ResearchSetValidationError, ResearchSetStorageUnavailableError, RuntimeError):
        return None

    record = stored_set.to_dict()
    page = _editor_page(_display_set_label(record.get("label"), ui_lang), ui_lang=ui_lang, language_slug=language_slug)
    page.update(
        {
            "template": "pages/research_phenomena_editor.html",
            "editor_hint": _t(
                ui_lang,
                "research.phenomena.editor.hint_curated" if stored_set.visibility == "curated" else "research.phenomena.editor.hint_custom",
            ),
            "is_admin": _is_admin(),
            "client_state": _editor_state(
                ui_lang=ui_lang,
                language_slug=language_slug,
                record=record,
                editor_mode="preset" if stored_set.visibility == "curated" else "set",
            ),
        }
    )
    return page