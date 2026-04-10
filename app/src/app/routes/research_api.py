"""Owner-bound JSON API for research sets."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..research_sets import (
    ResearchSetNotFoundError,
    ResearchSetStorageUnavailableError,
    ResearchSetValidationError,
    UNSET,
    create_draft_set,
    load_owned_set,
    replace_set_items,
    replace_set_sessions,
    save_set_as_new,
    update_set_metadata,
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


def _set_response_payload(record) -> dict[str, Any]:
    return {"set": record.to_dict()}


@blueprint.post("/sets")
@jwt_required()
def create_set() -> tuple[Response, int]:
    try:
        payload = _json_object_payload()
        record = create_draft_set(
            owner_user_id=_current_owner_user_id(),
            corpus_language=payload.get("corpus_language", ""),
            source_preset_id=payload.get("preset_id"),
            preferred_task=payload.get("preferred_task"),
            label=payload.get("label"),
            comparison_view_task=payload.get("comparison_view_task"),
        )
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.CREATED.value


@blueprint.get("/sets/<set_id>")
@jwt_required()
def get_set(set_id: str) -> tuple[Response, int]:
    try:
        record = load_owned_set(owner_user_id=_current_owner_user_id(), set_id=set_id)
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
        record = update_set_metadata(
            owner_user_id=_current_owner_user_id(),
            set_id=set_id,
            label=payload["label"] if "label" in payload else UNSET,
            preferred_task=payload["preferred_task"] if "preferred_task" in payload else UNSET,
            comparison_view_task=payload["comparison_view_task"] if "comparison_view_task" in payload else UNSET,
        )
    except ResearchSetValidationError as exc:
        return _json_error(str(exc), HTTPStatus.BAD_REQUEST)
    except ResearchSetNotFoundError as exc:
        return _json_error(str(exc), HTTPStatus.NOT_FOUND)
    except ResearchSetStorageUnavailableError as exc:
        return _json_error(str(exc), HTTPStatus.SERVICE_UNAVAILABLE)
    return jsonify(_set_response_payload(record)), HTTPStatus.OK.value


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