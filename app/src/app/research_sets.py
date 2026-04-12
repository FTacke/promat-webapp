"""Owner-bound research set persistence and validation for PROMAT."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping, TypeVar

from flask import current_app, has_app_context
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from .auth.models import Base
from .config.data_conventions import get_target_language_for_language_slug
from .extensions.sqlalchemy_ext import get_session
from .research_presets import (
    ResearchConfigError,
    TaskItemReference,
    load_phenomena_preset_map,
    normalize_task_item_reference,
    validate_task_item_references,
)
from .research_sessions import get_session as get_research_session


SET_STATES: tuple[str, ...] = ("draft", "saved")
SET_ITEM_TASKS: tuple[str, ...] = ("wordlist", "text")
COMPARISON_VIEW_TASKS: tuple[str, ...] = ("all", "wordlist", "text")
UNSET = object()
StorageResult = TypeVar("StorageResult")


class ResearchSetError(ValueError):
    """Base error for research set validation and persistence."""


class ResearchSetNotFoundError(ResearchSetError):
    """Raised when a set is missing or not owned by the current user."""


class ResearchSetValidationError(ResearchSetError):
    """Raised when request data is invalid for research sets."""


class ResearchSetStorageUnavailableError(ResearchSetError):
    """Raised when the research-set storage backend is unavailable."""


class ResearchSet(Base):
    __tablename__ = "research_sets"
    __table_args__ = (
        CheckConstraint("state IN ('draft', 'saved')", name="ck_research_sets_state"),
        CheckConstraint(
            "preferred_task IS NULL OR preferred_task IN ('wordlist', 'text')",
            name="ck_research_sets_preferred_task",
        ),
        CheckConstraint(
            "comparison_view_task IN ('all', 'wordlist', 'text')",
            name="ck_research_sets_comparison_view_task",
        ),
        CheckConstraint(
            "state = 'draft' OR (label IS NOT NULL AND length(trim(label)) > 0)",
            name="ck_research_sets_saved_label",
        ),
    )

    set_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    corpus_language: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    label: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str] = mapped_column(String(16), nullable=False)
    source_preset_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_task: Mapped[str | None] = mapped_column(String(16), nullable=True)
    comparison_view_task: Mapped[str] = mapped_column(String(16), nullable=False, default="all")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list["ResearchSetItem"]] = relationship(
        "ResearchSetItem",
        back_populates="research_set",
        cascade="all, delete-orphan",
        order_by="ResearchSetItem.sort_order",
    )
    sessions: Mapped[list["ResearchSetSessionLink"]] = relationship(
        "ResearchSetSessionLink",
        back_populates="research_set",
        cascade="all, delete-orphan",
        order_by="ResearchSetSessionLink.sort_order",
    )


class ResearchSetItem(Base):
    __tablename__ = "research_set_items"
    __table_args__ = (
        CheckConstraint("task IN ('wordlist', 'text')", name="ck_research_set_items_task"),
        CheckConstraint("sort_order >= 1", name="ck_research_set_items_sort_order"),
    )

    set_id: Mapped[str] = mapped_column(ForeignKey("research_sets.set_id", ondelete="CASCADE"), primary_key=True)
    task: Mapped[str] = mapped_column(String(16), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    segment_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    research_set: Mapped[ResearchSet] = relationship("ResearchSet", back_populates="items")


class ResearchSetSessionLink(Base):
    __tablename__ = "research_set_sessions"
    __table_args__ = (CheckConstraint("sort_order >= 1", name="ck_research_set_sessions_sort_order"),)

    set_id: Mapped[str] = mapped_column(ForeignKey("research_sets.set_id", ondelete="CASCADE"), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    research_set: Mapped[ResearchSet] = relationship("ResearchSet", back_populates="sessions")


@dataclass(frozen=True)
class StoredResearchSetItem:
    task: str
    item_id: str
    sort_order: int
    segment_id: str | None
    note: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "item_id": self.item_id,
            "sort_order": self.sort_order,
            "segment_id": self.segment_id,
            "note": self.note,
        }


@dataclass(frozen=True)
class StoredResearchSetSession:
    session_id: str
    sort_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "sort_order": self.sort_order,
        }


@dataclass(frozen=True)
class StoredResearchSet:
    set_id: str
    corpus_language: str
    label: str | None
    note: str | None
    state: str
    source_preset_id: str | None
    preferred_task: str | None
    comparison_view_task: str
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    expires_at: datetime | None
    items: tuple[StoredResearchSetItem, ...]
    sessions: tuple[StoredResearchSetSession, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "set_id": self.set_id,
            "corpus_language": self.corpus_language,
            "label": self.label,
            "note": self.note,
            "suggested_save_label": _suggest_saved_set_label(
                label=self.label,
                state=self.state,
                source_preset_id=self.source_preset_id,
                created_at=self.created_at,
            ),
            "state": self.state,
            "source_preset_id": self.source_preset_id,
            "preferred_task": self.preferred_task,
            "comparison_view_task": self.comparison_view_task,
            "created_at": _serialize_datetime(self.created_at),
            "updated_at": _serialize_datetime(self.updated_at),
            "last_accessed_at": _serialize_datetime(self.last_accessed_at),
            "expires_at": _serialize_datetime(self.expires_at),
            "items": [item.to_dict() for item in self.items],
            "sessions": [entry.to_dict() for entry in self.sessions],
        }


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _suggest_saved_set_label(*, label: str | None, state: str, source_preset_id: str | None, created_at: datetime) -> str:
    if label:
        return label
    if source_preset_id:
        return f"{source_preset_id}_modified"
    return f"set_{created_at.date().isoformat()}"


def _normalize_owner_user_id(owner_user_id: str) -> str:
    normalized = (owner_user_id or "").strip()
    if not normalized:
        raise ResearchSetValidationError("Missing authenticated owner user id")
    return normalized


def _normalize_language_slug(language_slug: str) -> str:
    normalized = (language_slug or "").strip().lower()
    if get_target_language_for_language_slug(normalized) is None:
        raise ResearchSetValidationError(f"Unsupported corpus_language '{language_slug}'")
    return normalized


def _normalize_optional_label(label: Any) -> str | None:
    if label is None:
        return None
    if not isinstance(label, str):
        raise ResearchSetValidationError("label must be a string when provided")
    normalized = label.strip()
    return normalized or None


def _normalize_optional_note(note: Any) -> str | None:
    if note is None:
        return None
    if not isinstance(note, str):
        raise ResearchSetValidationError("note must be a string when provided")
    normalized = note.strip()
    return normalized or None


def _normalize_set_state(state: Any) -> str:
    if not isinstance(state, str):
        raise ResearchSetValidationError("state must be a string when provided")
    normalized = state.strip().lower()
    if normalized not in SET_STATES:
        raise ResearchSetValidationError("state must be one of 'draft' or 'saved'")
    return normalized


def _normalize_preferred_task(task: Any) -> str | None:
    if task is None:
        return None
    if not isinstance(task, str):
        raise ResearchSetValidationError("preferred_task must be a string when provided")
    normalized = task.strip()
    if not normalized:
        return None
    if normalized not in SET_ITEM_TASKS:
        raise ResearchSetValidationError("preferred_task must be one of 'wordlist' or 'text'")
    return normalized


def _normalize_comparison_view_task(task: Any) -> str:
    if task is None:
        return "all"
    if not isinstance(task, str):
        raise ResearchSetValidationError("comparison_view_task must be a string when provided")
    normalized = task.strip() or "all"
    if normalized not in COMPARISON_VIEW_TASKS:
        raise ResearchSetValidationError("comparison_view_task must be one of 'all', 'wordlist', or 'text'")
    return normalized


def _draft_ttl() -> timedelta:
    ttl_days = int(current_app.config.get("RESEARCH_SET_DRAFT_TTL_DAYS", 14))
    return timedelta(days=max(ttl_days, 1))


def _storage_unavailable_message() -> str:
    return (
        "Research-set storage is unavailable. Run scripts/dev-start.ps1 or "
        "app/scripts/dev-setup.ps1 to apply the auth and research-set migrations."
    )


def _raise_storage_unavailable(exc: DBAPIError) -> None:
    logger = current_app.logger if has_app_context() else logging.getLogger(__name__)
    logger.exception("Research-set storage is unavailable: %s", exc)
    raise ResearchSetStorageUnavailableError(_storage_unavailable_message()) from exc


def _run_storage_operation(operation: Callable[[], StorageResult]) -> StorageResult:
    try:
        return operation()
    except DBAPIError as exc:
        _raise_storage_unavailable(exc)


def _set_expiration_for_draft(record: ResearchSet, *, now: datetime) -> None:
    if record.state == "draft":
        record.expires_at = now + _draft_ttl()
    else:
        record.expires_at = None


def _touch_access(record: ResearchSet, *, now: datetime) -> None:
    record.last_accessed_at = now
    _set_expiration_for_draft(record, now=now)


def _serialize_set(record: ResearchSet) -> StoredResearchSet:
    return StoredResearchSet(
        set_id=record.set_id,
        corpus_language=record.corpus_language,
        label=record.label,
        note=record.note,
        state=record.state,
        source_preset_id=record.source_preset_id,
        preferred_task=record.preferred_task,
        comparison_view_task=record.comparison_view_task,
        created_at=record.created_at,
        updated_at=record.updated_at,
        last_accessed_at=record.last_accessed_at,
        expires_at=record.expires_at,
        items=tuple(
            StoredResearchSetItem(
                task=item.task,
                item_id=item.item_id,
                sort_order=item.sort_order,
                segment_id=item.segment_id,
                note=item.note,
            )
            for item in sorted(record.items, key=lambda entry: entry.sort_order)
        ),
        sessions=tuple(
            StoredResearchSetSession(session_id=entry.session_id, sort_order=entry.sort_order)
            for entry in sorted(record.sessions, key=lambda entry: entry.sort_order)
        ),
    )


def _get_owned_set_record(session, *, owner_user_id: str, set_id: str) -> ResearchSet:
    stmt = (
        select(ResearchSet)
        .options(selectinload(ResearchSet.items), selectinload(ResearchSet.sessions))
        .where(ResearchSet.set_id == set_id, ResearchSet.owner_user_id == owner_user_id)
    )
    record = session.execute(stmt).scalars().first()
    if record is None:
        raise ResearchSetNotFoundError(f"Research set '{set_id}' was not found")
    return record


def _existing_owner_labels(session, *, owner_user_id: str, language_slug: str) -> set[str]:
    stmt = select(ResearchSet.label).where(
        ResearchSet.owner_user_id == owner_user_id,
        ResearchSet.corpus_language == language_slug,
        ResearchSet.label.is_not(None),
    )
    return {value.strip() for value in session.execute(stmt).scalars().all() if isinstance(value, str) and value.strip()}


def _next_generated_label(existing_labels: set[str], *, base_label: str, suffix_template: str) -> str:
    if base_label not in existing_labels:
        return base_label

    index = 2
    while True:
        candidate = suffix_template.format(index=index)
        if candidate not in existing_labels:
            return candidate
        index += 1


def _default_draft_label(
    session,
    *,
    owner_user_id: str,
    language_slug: str,
    preset_label: str | None,
) -> str:
    existing_labels = _existing_owner_labels(session, owner_user_id=owner_user_id, language_slug=language_slug)
    if preset_label:
        base_label = f"{preset_label} (modifiziert)"
        return _next_generated_label(
            existing_labels,
            base_label=base_label,
            suffix_template=f"{preset_label} (modifiziert {{index}})",
        )

    index = 1
    while True:
        candidate = f"Neues Set {index}"
        if candidate not in existing_labels:
            return candidate
        index += 1


def _validated_item_references(raw_items: list[Any], *, language_slug: str, context: str) -> tuple[TaskItemReference, ...]:
    references: list[TaskItemReference] = []
    for index, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, Mapping):
            raise ResearchSetValidationError(f"Invalid item payload at position {index} in {context}")
        reference = normalize_task_item_reference(raw_item, context=f"{context} item #{index}")
        if reference.task not in SET_ITEM_TASKS:
            raise ResearchSetValidationError(
                f"Unsupported set item task '{reference.task}' in {context}; only 'wordlist' and 'text' are allowed"
            )
        references.append(reference)

    try:
        validate_task_item_references(tuple(references), language_slug=language_slug, context=context)
    except ResearchConfigError as exc:
        raise ResearchSetValidationError(str(exc)) from exc
    return tuple(references)


def _materialize_set_items(record: ResearchSet, references: tuple[TaskItemReference, ...]) -> None:
    record.items.clear()
    for sort_order, reference in enumerate(references, start=1):
        record.items.append(
            ResearchSetItem(
                set_id=record.set_id,
                task=reference.task,
                item_id=reference.item_id,
                sort_order=sort_order,
                segment_id=reference.segment_id,
                note=reference.note,
            )
        )


def _validated_session_ids(raw_sessions: list[Any], *, language_slug: str, context: str) -> tuple[str, ...]:
    normalized_sessions: list[str] = []
    seen: set[str] = set()
    for index, raw_entry in enumerate(raw_sessions, start=1):
        if isinstance(raw_entry, str):
            session_id = raw_entry.strip()
        elif isinstance(raw_entry, Mapping):
            value = raw_entry.get("session_id")
            if not isinstance(value, str):
                raise ResearchSetValidationError(f"Invalid session payload at position {index} in {context}")
            session_id = value.strip()
        else:
            raise ResearchSetValidationError(f"Invalid session payload at position {index} in {context}")

        if not session_id:
            raise ResearchSetValidationError(f"Empty session_id at position {index} in {context}")
        if session_id in seen:
            raise ResearchSetValidationError(f"Duplicate session_id '{session_id}' in {context}")
        if get_research_session(language_slug, session_id) is None:
            raise ResearchSetValidationError(
                f"Unknown session_id '{session_id}' for corpus_language '{language_slug}' in {context}"
            )
        seen.add(session_id)
        normalized_sessions.append(session_id)
    return tuple(normalized_sessions)


def _materialize_set_sessions(record: ResearchSet, session_ids: tuple[str, ...]) -> None:
    record.sessions.clear()
    for sort_order, session_id in enumerate(session_ids, start=1):
        record.sessions.append(
            ResearchSetSessionLink(
                set_id=record.set_id,
                session_id=session_id,
                sort_order=sort_order,
            )
        )


def create_draft_set(
    *,
    owner_user_id: str,
    corpus_language: str,
    source_preset_id: str | None = None,
    preferred_task: str | None = None,
    label: str | None = None,
    note: str | None = None,
    comparison_view_task: str | None = None,
) -> StoredResearchSet:
    owner_id = _normalize_owner_user_id(owner_user_id)
    language_slug = _normalize_language_slug(corpus_language)
    normalized_label = _normalize_optional_label(label)
    normalized_note = _normalize_optional_note(note)
    normalized_preferred_task = _normalize_preferred_task(preferred_task)
    normalized_view_task = _normalize_comparison_view_task(comparison_view_task)
    now = _utcnow()

    preset_items: tuple[TaskItemReference, ...] = tuple()
    normalized_source_preset_id = None
    preset_label: str | None = None
    if source_preset_id is not None:
        if not isinstance(source_preset_id, str) or not source_preset_id.strip():
            raise ResearchSetValidationError("source_preset_id must be a non-empty string when provided")
        normalized_source_preset_id = source_preset_id.strip()
        try:
            preset = load_phenomena_preset_map(language_slug)[normalized_source_preset_id]
        except ResearchConfigError as exc:
            raise ResearchSetValidationError(str(exc)) from exc
        except KeyError as exc:
            raise ResearchSetValidationError(
                f"Unknown preset_id '{normalized_source_preset_id}' for corpus_language '{language_slug}'"
            ) from exc
        preset_items = preset.items
        preset_label = preset.label

    def operation() -> StoredResearchSet:
        with get_session() as session:
            effective_label = normalized_label or _default_draft_label(
                session,
                owner_user_id=owner_id,
                language_slug=language_slug,
                preset_label=preset_label,
            )
            record = ResearchSet(
                set_id=str(uuid.uuid4()),
                owner_user_id=owner_id,
                corpus_language=language_slug,
                label=effective_label,
                note=normalized_note,
                state="draft",
                source_preset_id=normalized_source_preset_id,
                preferred_task=normalized_preferred_task,
                comparison_view_task=normalized_view_task,
                created_at=now,
                updated_at=now,
                last_accessed_at=now,
                expires_at=now + _draft_ttl(),
            )
            session.add(record)
            _materialize_set_items(record, preset_items)
            session.flush()
            return _serialize_set(record)

    return _run_storage_operation(operation)


def load_owned_set(*, owner_user_id: str, set_id: str, touch_access: bool = True) -> StoredResearchSet:
    owner_id = _normalize_owner_user_id(owner_user_id)
    normalized_set_id = (set_id or "").strip()
    if not normalized_set_id:
        raise ResearchSetValidationError("set_id is required")
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = _get_owned_set_record(session, owner_user_id=owner_id, set_id=normalized_set_id)
            if touch_access:
                _touch_access(record, now=now)
            return _serialize_set(record)

    return _run_storage_operation(operation)


def update_set_metadata(
    *,
    owner_user_id: str,
    set_id: str,
    label: object = UNSET,
    note: object = UNSET,
    state: object = UNSET,
    preferred_task: object = UNSET,
    comparison_view_task: object = UNSET,
) -> StoredResearchSet:
    owner_id = _normalize_owner_user_id(owner_user_id)
    normalized_set_id = (set_id or "").strip()
    if not normalized_set_id:
        raise ResearchSetValidationError("set_id is required")
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = _get_owned_set_record(session, owner_user_id=owner_id, set_id=normalized_set_id)

            if label is not UNSET:
                record.label = _normalize_optional_label(label)
            if note is not UNSET:
                record.note = _normalize_optional_note(note)
            if state is not UNSET:
                record.state = _normalize_set_state(state)
            if preferred_task is not UNSET:
                record.preferred_task = _normalize_preferred_task(preferred_task)
            if comparison_view_task is not UNSET:
                record.comparison_view_task = _normalize_comparison_view_task(comparison_view_task)

            if record.state == "saved" and not record.label:
                raise ResearchSetValidationError("Saved sets require a non-empty label")

            record.updated_at = now
            _touch_access(record, now=now)
            session.flush()
            return _serialize_set(record)

    return _run_storage_operation(operation)


def list_owned_sets(
    *,
    owner_user_id: str,
    corpus_language: str,
    include_drafts: bool = False,
) -> tuple[StoredResearchSet, ...]:
    owner_id = _normalize_owner_user_id(owner_user_id)
    language_slug = _normalize_language_slug(corpus_language)

    def operation() -> tuple[StoredResearchSet, ...]:
        with get_session() as session:
            stmt = (
                select(ResearchSet)
                .options(selectinload(ResearchSet.items), selectinload(ResearchSet.sessions))
                .where(
                    ResearchSet.owner_user_id == owner_id,
                    ResearchSet.corpus_language == language_slug,
                )
                .order_by(ResearchSet.updated_at.desc(), ResearchSet.created_at.desc())
            )
            if not include_drafts:
                stmt = stmt.where(ResearchSet.state == "saved")
            records = session.execute(stmt).scalars().all()
            return tuple(_serialize_set(record) for record in records)

    return _run_storage_operation(operation)


def list_selectable_owned_sets(
    *,
    owner_user_id: str,
    corpus_language: str,
    current_set_id: str | None = None,
) -> tuple[StoredResearchSet, ...]:
    owner_id = _normalize_owner_user_id(owner_user_id)
    language_slug = _normalize_language_slug(corpus_language)
    visible_sets = list(list_owned_sets(owner_user_id=owner_id, corpus_language=language_slug, include_drafts=False))
    normalized_current_set_id = (current_set_id or "").strip()
    if not normalized_current_set_id:
        return tuple(visible_sets)

    if any(record.set_id == normalized_current_set_id for record in visible_sets):
        return tuple(visible_sets)

    try:
        current_record = load_owned_set(owner_user_id=owner_id, set_id=normalized_current_set_id, touch_access=False)
    except (ResearchSetNotFoundError, ResearchSetStorageUnavailableError, ResearchSetValidationError):
        return tuple(visible_sets)

    if current_record.corpus_language != language_slug:
        return tuple(visible_sets)

    return (current_record, *visible_sets)


def replace_set_items(*, owner_user_id: str, set_id: str, items: list[Any]) -> StoredResearchSet:
    owner_id = _normalize_owner_user_id(owner_user_id)
    normalized_set_id = (set_id or "").strip()
    if not isinstance(items, list):
        raise ResearchSetValidationError("items must be a JSON array")
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = _get_owned_set_record(session, owner_user_id=owner_id, set_id=normalized_set_id)
            references = _validated_item_references(items, language_slug=record.corpus_language, context=f"set '{normalized_set_id}'")
            _materialize_set_items(record, references)
            record.updated_at = now
            _touch_access(record, now=now)
            session.flush()
            return _serialize_set(record)

    return _run_storage_operation(operation)


def replace_set_sessions(*, owner_user_id: str, set_id: str, sessions: list[Any]) -> StoredResearchSet:
    owner_id = _normalize_owner_user_id(owner_user_id)
    normalized_set_id = (set_id or "").strip()
    if not isinstance(sessions, list):
        raise ResearchSetValidationError("sessions must be a JSON array")
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = _get_owned_set_record(session, owner_user_id=owner_id, set_id=normalized_set_id)
            session_ids = _validated_session_ids(sessions, language_slug=record.corpus_language, context=f"set '{normalized_set_id}'")
            _materialize_set_sessions(record, session_ids)
            record.updated_at = now
            _touch_access(record, now=now)
            session.flush()
            return _serialize_set(record)

    return _run_storage_operation(operation)


def save_set_as_new(*, owner_user_id: str, source_set_id: str, label: str) -> StoredResearchSet:
    owner_id = _normalize_owner_user_id(owner_user_id)
    normalized_source_set_id = (source_set_id or "").strip()
    normalized_label = _normalize_optional_label(label)
    if not normalized_label:
        raise ResearchSetValidationError("Saved sets require a non-empty label")
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            source_record = _get_owned_set_record(session, owner_user_id=owner_id, set_id=normalized_source_set_id)
            _touch_access(source_record, now=now)

            saved_record = ResearchSet(
                set_id=str(uuid.uuid4()),
                owner_user_id=owner_id,
                corpus_language=source_record.corpus_language,
                label=normalized_label,
                note=source_record.note,
                state="saved",
                source_preset_id=source_record.source_preset_id,
                preferred_task=source_record.preferred_task,
                comparison_view_task=source_record.comparison_view_task,
                created_at=now,
                updated_at=now,
                last_accessed_at=now,
                expires_at=None,
            )
            session.add(saved_record)
            _materialize_set_items(
                saved_record,
                tuple(
                    TaskItemReference(
                        task=item.task,
                        item_id=item.item_id,
                        segment_id=item.segment_id,
                        note=item.note,
                    )
                    for item in sorted(source_record.items, key=lambda entry: entry.sort_order)
                ),
            )
            _materialize_set_sessions(
                saved_record,
                tuple(entry.session_id for entry in sorted(source_record.sessions, key=lambda entry: entry.sort_order)),
            )
            session.flush()
            return _serialize_set(saved_record)

    return _run_storage_operation(operation)


def delete_owned_set(*, owner_user_id: str, set_id: str) -> None:
    owner_id = _normalize_owner_user_id(owner_user_id)
    normalized_set_id = (set_id or "").strip()
    if not normalized_set_id:
        raise ResearchSetValidationError("set_id is required")

    def operation() -> None:
        with get_session() as session:
            record = _get_owned_set_record(session, owner_user_id=owner_id, set_id=normalized_set_id)
            session.delete(record)

    _run_storage_operation(operation)


def delete_expired_drafts(*, now: datetime | None = None) -> int:
    effective_now = now or _utcnow()

    def operation() -> int:
        with get_session() as session:
            stmt = select(ResearchSet).where(
                ResearchSet.state == "draft",
                ResearchSet.expires_at.is_not(None),
                ResearchSet.expires_at <= effective_now,
            )
            expired_records = list(session.execute(stmt).scalars().all())
            for record in expired_records:
                session.delete(record)
            return len(expired_records)

    return _run_storage_operation(operation)