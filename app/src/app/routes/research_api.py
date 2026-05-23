"""JSON API for private and curated research sets."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from flask import Blueprint, Response, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..auth import Role
from ..research_sets import (
    ResearchSetNotFoundError,
    ResearchSetStorageUnavailableError,
    ResearchSetValidationError,
    UNSET,
    archive_curated_set,
    create_curated_set,
    create_draft_set,
    create_private_copy_from_curated,
    delete_owned_set,
    get_visible_set,
    list_visible_sets_for_user,
    replace_set_items,
    replace_set_sessions,
    save_set_as_new,
    update_curated_set,
    update_set_metadata,
    update_set_workbench_state,
    reactivate_curated_set,
)

blueprint = Blueprint("research_api", __name__, url_prefix="/api/research")


def _json_error(message: str, status: HTTPStatus) -> tuple[Response, int]:
    return jsonify({"error": message}), status.value


def _json_object_payload() -> dict[str, Any]:
    payload = request.get_json(silent=True)
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ResearchSetValidationError("Request body must be a JSON object")
    return payload


def _current_owner_user_id() -> str:
    identity = get_jwt_identity()
    if not isinstance(identity, str) or not identity.strip():
        raise ResearchSetValidationError("Authenticated user id is missing")
    return identity.strip()


def _is_admin_request() -> bool:
    return getattr(g, "role", None) == Role.ADMIN


def _require_admin() -> str:
    owner_user_id = _current_owner_user_id()
    if not _is_admin_request():
        raise PermissionError("Admin role required")
    return owner_user_id


def _workbench_state_object(payload: dict[str, Any], *, required: bool = False) -> dict[str, Any]:
    raw_workbench_state = payload.get("workbench_state", UNSET)
    if raw_workbench_state is UNSET:
        if required:
            raise ResearchSetValidationError("workbench_state must be a JSON object when provided")
        return {}
    if not isinstance(raw_workbench_state, dict):
        raise ResearchSetValidationError("workbench_state must be a JSON object when provided")
    return raw_workbench_state


def _validate_no_top_level_workbench_aliases(payload: dict[str, Any]) -> None:
    for field_name in ("preferred_task", "comparison_view_task", "sessions"):
        if field_name in payload:
            raise ResearchSetValidationError(
                f"Top-level '{field_name}' is no longer supported; use 'workbench_state.{field_name}' or the dedicated /sessions route"
            )


def _workbench_patch_values(payload: dict[str, Any], *, allow_sessions: bool = False) -> dict[str, Any]:
    values: dict[str, Any] = {}
    workbench_state = _workbench_state_object(payload)
    for field_name in ("preferred_task", "comparison_view_task"):
        if field_name in workbench_state:
            values[field_name] = workbench_state[field_name]
    if "sessions" in workbench_state:
        if not allow_sessions:
            raise ResearchSetValidationError(
                "workbench_state.sessions is not supported on PATCH; use the dedicated /api/research/sets/{set_id}/sessions route"
            )
        values["sessions"] = workbench_state["sessions"]
    return values


def _set_response_payload(record) -> dict[str, Any]:
    return {"set": record.to_dict()}


@blueprint.post("/sets")
@jwt_required()
def create_set() -> tuple[Response, int]:
    payload: dict[str, Any] = {}
    try:
        payload = _json_object_payload()
        _validate_no_top_level_workbench_aliases(payload)
        workbench_state = _workbench_state_object(payload)
        if "sessions" in workbench_state:
            raise ResearchSetValidationError(
                "workbench_state.sessions is not supported on create; use the dedicated /api/research/sets/{set_id}/sessions route after draft creation"
            )
        record = create_draft_set(
            owner_user_id=_current_owner_user_id(),
            corpus_language=payload.get("corpus_language", ""),
            source_curated_set_id=payload.get("source_curated_set_id"),
            source_preset_id=payload.get("preset_id"),
            preferred_task=workbench_state.get("preferred_task"),
            label=payload.get("label"),
            note=payload.get("note"),
            comparison_view_task=workbench_state.get("comparison_view_task"),
        )
    except ResearchSetNotFoundError as exc:
        if payload.get("preset_id"):
            return _json_error(f"Unknown preset_id '{payload['preset_id']}'", HTTPStatus.BAD_REQUEST)
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.CREATED.value


@blueprint.get("/sets")
@jwt_required()
def list_sets() -> tuple[Response, int]:
    try:
        include_drafts = request.args.get("include_drafts", "").strip().lower() in {"1", "true", "yes"}
        include_archived_curated = request.args.get("include_archived_curated", "").strip().lower() in {"1", "true", "yes"}
        if include_archived_curated and not _is_admin_request():
            return _json_error("Admin role required", HTTPStatus.FORBIDDEN)
        records = list_visible_sets_for_user(
            owner_user_id=_current_owner_user_id(),
            corpus_language=request.args.get("corpus_language", ""),
            include_drafts=include_drafts,
            include_archived_curated=include_archived_curated,
        )
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify({"sets": [record.to_dict() for record in records]}), HTTPStatus.OK.value


@blueprint.get("/sets/<set_id>")
@jwt_required()
def get_set(set_id: str) -> tuple[Response, int]:
    try:
        record = get_visible_set(
            owner_user_id=_current_owner_user_id(),
            set_id=set_id,
            include_archived_curated=_is_admin_request(),
        )
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.OK.value


@blueprint.patch("/sets/<set_id>")
@jwt_required()
def patch_set(set_id: str) -> tuple[Response, int]:
    try:
        payload = _json_object_payload()
        _validate_no_top_level_workbench_aliases(payload)
        owner_user_id = _current_owner_user_id()
        record = None
        if any(field_name in payload for field_name in ("label", "note", "lifecycle", "state")):
            record = update_set_metadata(
                owner_user_id=owner_user_id,
                set_id=set_id,
                label=payload["label"] if "label" in payload else UNSET,
                note=payload["note"] if "note" in payload else UNSET,
                lifecycle=payload["lifecycle"] if "lifecycle" in payload else UNSET,
                state=payload["state"] if "state" in payload else UNSET,
            )

        workbench_values = _workbench_patch_values(payload)
        if workbench_values:
            record = update_set_workbench_state(
                owner_user_id=owner_user_id,
                set_id=set_id,
                preferred_task=workbench_values.get("preferred_task", UNSET),
                comparison_view_task=workbench_values.get("comparison_view_task", UNSET),
            )

        if record is None:
            record = get_visible_set(owner_user_id=owner_user_id, set_id=set_id, include_archived_curated=_is_admin_request())
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.OK.value


@blueprint.delete("/sets/<set_id>")
@jwt_required()
def delete_set(set_id: str) -> tuple[Response, int]:
    try:
        delete_owned_set(owner_user_id=_current_owner_user_id(), set_id=set_id)
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify({"deleted": True, "set_id": set_id}), HTTPStatus.OK.value


@blueprint.put("/sets/<set_id>/items")
@jwt_required()
def put_set_items(set_id: str) -> tuple[Response, int]:
    try:
        payload = _json_object_payload()
        record = replace_set_items(
            owner_user_id=_current_owner_user_id(),
            set_id=set_id,
            items=payload.get("items", []),
        )
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.OK.value


@blueprint.put("/sets/<set_id>/sessions")
@jwt_required()
def put_set_sessions(set_id: str) -> tuple[Response, int]:
    try:
        payload = _json_object_payload()
        record = replace_set_sessions(
            owner_user_id=_current_owner_user_id(),
            set_id=set_id,
            sessions=payload.get("sessions", []),
        )
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.OK.value


@blueprint.post("/sets/<set_id>/save-as")
@jwt_required()
def save_as_new_set(set_id: str) -> tuple[Response, int]:
    try:
        payload = _json_object_payload()
        record = save_set_as_new(
            owner_user_id=_current_owner_user_id(),
            source_set_id=set_id,
            label=payload.get("label"),
        )
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.CREATED.value


@blueprint.post("/sets/<set_id>/private-copy")
@jwt_required()
def private_copy_set(set_id: str) -> tuple[Response, int]:
    try:
        payload = _json_object_payload()
        record = create_private_copy_from_curated(
            owner_user_id=_current_owner_user_id(),
            source_set_id=set_id,
            label=payload.get("label"),
            note=payload.get("note"),
            lifecycle=payload.get("lifecycle", "draft"),
        )
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.CREATED.value


@blueprint.post("/admin/curated-sets")
@jwt_required()
def create_admin_curated_set() -> tuple[Response, int]:
    try:
        admin_user_id = _require_admin()
        payload = _json_object_payload()
        workbench_state = _workbench_state_object(payload)
        record = create_curated_set(
            admin_user_id=admin_user_id,
            corpus_language=payload.get("corpus_language", ""),
            label=payload.get("label"),
            note=payload.get("note"),
            items=payload.get("items", []),
            preferred_task=workbench_state.get("preferred_task"),
            comparison_view_task=workbench_state.get("comparison_view_task"),
            sessions=workbench_state.get("sessions", []),
        )
    except PermissionError as exc:
        return _json_error(str(exc), HTTPStatus.FORBIDDEN)
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.CREATED.value


@blueprint.put("/admin/curated-sets/<set_id>")
@jwt_required()
def update_admin_curated_set(set_id: str) -> tuple[Response, int]:
    try:
        admin_user_id = _require_admin()
        payload = _json_object_payload()
        workbench_values = _workbench_patch_values(payload, allow_sessions=True)
        record = update_curated_set(
            admin_user_id=admin_user_id,
            set_id=set_id,
            label=payload["label"] if "label" in payload else UNSET,
            note=payload["note"] if "note" in payload else UNSET,
            items=payload["items"] if "items" in payload else UNSET,
            preferred_task=workbench_values.get("preferred_task", UNSET),
            comparison_view_task=workbench_values.get("comparison_view_task", UNSET),
            sessions=workbench_values.get("sessions", UNSET),
        )
    except PermissionError as exc:
        return _json_error(str(exc), HTTPStatus.FORBIDDEN)
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.OK.value


@blueprint.post("/admin/curated-sets/<set_id>/archive")
@jwt_required()
def archive_admin_curated_set(set_id: str) -> tuple[Response, int]:
    try:
        record = archive_curated_set(admin_user_id=_require_admin(), set_id=set_id)
    except PermissionError as exc:
        return _json_error(str(exc), HTTPStatus.FORBIDDEN)
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.OK.value


@blueprint.post("/admin/curated-sets/<set_id>/reactivate")
@jwt_required()
def reactivate_admin_curated_set(set_id: str) -> tuple[Response, int]:
    try:
        record = reactivate_curated_set(admin_user_id=_require_admin(), set_id=set_id)
    except PermissionError as exc:
        return _json_error(str(exc), HTTPStatus.FORBIDDEN)
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.OK.value