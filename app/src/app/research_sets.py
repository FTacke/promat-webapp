"""DB-backed research set persistence for private and curated PROMAT sets."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping, TypeVar

from flask import current_app, has_app_context
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, or_, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from .auth.models import Base
from .config.data_conventions import get_target_language_for_language_slug
from .extensions.sqlalchemy_ext import get_session
from .research_capabilities import comparison_view_task_keys, set_filter_task_keys
from .research_presets import ResearchConfigError, TaskItemReference, normalize_task_item_reference, validate_task_item_references
from .research_sessions import get_session as get_research_session


SET_VISIBILITIES: tuple[str, ...] = ("private", "curated")
SET_LIFECYCLES: tuple[str, ...] = ("draft", "saved", "archived")
PRIVATE_SET_LIFECYCLES: tuple[str, ...] = ("draft", "saved")
CURATED_SET_LIFECYCLES: tuple[str, ...] = ("saved", "archived")
SET_ITEM_TASKS: tuple[str, ...] = set_filter_task_keys()
COMPARISON_VIEW_TASKS: tuple[str, ...] = comparison_view_task_keys()
RESEARCH_CURATED_TEST_SET_ID = "00000000-0000-0000-0000-000000000601"
UNSET = object()
StorageResult = TypeVar("StorageResult")


def _sql_choice_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


SET_VISIBILITY_SQL = _sql_choice_list(SET_VISIBILITIES)
SET_LIFECYCLE_SQL = _sql_choice_list(SET_LIFECYCLES)
SET_ITEM_TASK_SQL = _sql_choice_list(SET_ITEM_TASKS)
COMPARISON_VIEW_TASK_SQL = _sql_choice_list(COMPARISON_VIEW_TASKS)


def _quoted_task_choices(values: tuple[str, ...]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return f"'{values[0]}'"
    return ", ".join(f"'{value}'" for value in values[:-1]) + f", or '{values[-1]}'"


class ResearchSetError(ValueError):
    """Base error for research set validation and persistence."""


class ResearchSetNotFoundError(ResearchSetError):
    """Raised when a set is missing or not visible to the current user."""


class ResearchSetValidationError(ResearchSetError):
    """Raised when request data is invalid for research sets."""


class ResearchSetStorageUnavailableError(ResearchSetError):
    """Raised when the research-set storage backend is unavailable."""


class ResearchSet(Base):
    __tablename__ = "research_sets"
    __table_args__ = (
        CheckConstraint(f"visibility IN ({SET_VISIBILITY_SQL})", name="ck_research_sets_visibility"),
        CheckConstraint(f"lifecycle IN ({SET_LIFECYCLE_SQL})", name="ck_research_sets_lifecycle"),
        CheckConstraint(
            "lifecycle = 'draft' OR (label IS NOT NULL AND length(trim(label)) > 0)",
            name="ck_research_sets_saved_label",
        ),
        CheckConstraint(
            "(visibility = 'private' AND lifecycle IN ('draft', 'saved')) "
            "OR (visibility = 'curated' AND lifecycle IN ('saved', 'archived'))",
            name="ck_research_sets_visibility_lifecycle",
        ),
        CheckConstraint(
            "(visibility = 'private' AND owner_user_id IS NOT NULL) "
            "OR (visibility = 'curated' AND owner_user_id IS NULL)",
            name="ck_research_sets_owner_scope",
        ),
        CheckConstraint("visibility = 'private' OR expires_at IS NULL", name="ck_research_sets_curated_expiry"),
        CheckConstraint("version >= 1", name="ck_research_sets_version"),
    )

    set_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    corpus_language: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    label: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    visibility: Mapped[str] = mapped_column(String(16), nullable=False, default="private")
    lifecycle: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")
    source_curated_set_id: Mapped[str | None] = mapped_column(
        ForeignKey("research_sets.set_id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list["ResearchSetItem"]] = relationship(
        "ResearchSetItem",
        back_populates="research_set",
        cascade="all, delete-orphan",
        order_by="ResearchSetItem.sort_order",
    )
    workbench_state: Mapped["ResearchSetWorkbenchState"] = relationship(
        "ResearchSetWorkbenchState",
        back_populates="research_set",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ResearchSetWorkbenchState(Base):
    __tablename__ = "research_set_workbench_state"
    __table_args__ = (
        CheckConstraint(
            f"preferred_task IS NULL OR preferred_task IN ({SET_ITEM_TASK_SQL})",
            name="ck_research_set_workbench_state_preferred_task",
        ),
        CheckConstraint(
            f"comparison_view_task IN ({COMPARISON_VIEW_TASK_SQL})",
            name="ck_research_set_workbench_state_comparison_view_task",
        ),
    )

    set_id: Mapped[str] = mapped_column(ForeignKey("research_sets.set_id", ondelete="CASCADE"), primary_key=True)
    preferred_task: Mapped[str | None] = mapped_column(String(16), nullable=True)
    comparison_view_task: Mapped[str] = mapped_column(String(16), nullable=False, default="all")

    research_set: Mapped[ResearchSet] = relationship("ResearchSet", back_populates="workbench_state")
    sessions: Mapped[list["ResearchSetWorkbenchSessionLink"]] = relationship(
        "ResearchSetWorkbenchSessionLink",
        back_populates="workbench_state",
        cascade="all, delete-orphan",
        order_by="ResearchSetWorkbenchSessionLink.sort_order",
    )


class ResearchSetItem(Base):
    __tablename__ = "research_set_items"
    __table_args__ = (
        CheckConstraint(f"task IN ({SET_ITEM_TASK_SQL})", name="ck_research_set_items_task"),
        CheckConstraint("sort_order >= 1", name="ck_research_set_items_sort_order"),
    )

    set_id: Mapped[str] = mapped_column(ForeignKey("research_sets.set_id", ondelete="CASCADE"), primary_key=True)
    task: Mapped[str] = mapped_column(String(16), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    segment_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    research_set: Mapped[ResearchSet] = relationship("ResearchSet", back_populates="items")


class ResearchSetWorkbenchSessionLink(Base):
    __tablename__ = "research_set_workbench_sessions"
    __table_args__ = (CheckConstraint("sort_order >= 1", name="ck_research_set_workbench_sessions_sort_order"),)

    set_id: Mapped[str] = mapped_column(
        ForeignKey("research_set_workbench_state.set_id", ondelete="CASCADE"),
        primary_key=True,
    )
    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    workbench_state: Mapped[ResearchSetWorkbenchState] = relationship(
        "ResearchSetWorkbenchState",
        back_populates="sessions",
    )


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
class StoredResearchSetWorkbenchState:
    preferred_task: str | None
    comparison_view_task: str
    sessions: tuple[StoredResearchSetSession, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "preferred_task": self.preferred_task,
            "comparison_view_task": self.comparison_view_task,
            "sessions": [entry.to_dict() for entry in self.sessions],
        }


@dataclass(frozen=True)
class StoredResearchSet:
    set_id: str
    corpus_language: str
    label: str | None
    note: str | None
    visibility: str
    lifecycle: str
    source_curated_set_id: str | None
    created_by_user_id: str | None
    updated_by_user_id: str | None
    version: int
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None
    archived_at: datetime | None
    last_accessed_at: datetime
    expires_at: datetime | None
    items: tuple[StoredResearchSetItem, ...]
    workbench_state: StoredResearchSetWorkbenchState

    @property
    def state(self) -> str:
        return self.lifecycle

    @property
    def source_preset_id(self) -> str | None:
        return self.source_curated_set_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "set_id": self.set_id,
            "corpus_language": self.corpus_language,
            "label": self.label,
            "note": self.note,
            "suggested_save_label": _suggest_saved_set_label(
                label=self.label,
                source_curated_set_id=self.source_curated_set_id,
                created_at=self.created_at,
            ),
            "visibility": self.visibility,
            "lifecycle": self.lifecycle,
            "state": self.lifecycle,
            "source_curated_set_id": self.source_curated_set_id,
            "source_preset_id": self.source_curated_set_id,
            "created_by_user_id": self.created_by_user_id,
            "updated_by_user_id": self.updated_by_user_id,
            "version": self.version,
            "created_at": _serialize_datetime(self.created_at),
            "updated_at": _serialize_datetime(self.updated_at),
            "published_at": _serialize_datetime(self.published_at),
            "archived_at": _serialize_datetime(self.archived_at),
            "last_accessed_at": _serialize_datetime(self.last_accessed_at),
            "expires_at": _serialize_datetime(self.expires_at),
            "items": [item.to_dict() for item in self.items],
            "workbench_state": self.workbench_state.to_dict(),
        }


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _suggest_saved_set_label(*, label: str | None, source_curated_set_id: str | None, created_at: datetime) -> str:
    if label:
        return label
    if source_curated_set_id:
        return f"{source_curated_set_id}_copy"
    return f"set_{created_at.date().isoformat()}"


def _normalize_owner_user_id(owner_user_id: str) -> str:
    normalized = (owner_user_id or "").strip()
    if not normalized:
        raise ResearchSetValidationError("Missing authenticated owner user id")
    return normalized


def _normalize_optional_owner_user_id(owner_user_id: str | None) -> str | None:
    if owner_user_id is None:
        return None
    normalized = owner_user_id.strip()
    return normalized or None


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


def _normalize_required_label(label: Any, *, field_name: str = "label") -> str:
    normalized = _normalize_optional_label(label)
    if not normalized:
        raise ResearchSetValidationError(f"{field_name} must be a non-empty string")
    return normalized


def _normalize_optional_note(note: Any) -> str | None:
    if note is None:
        return None
    if not isinstance(note, str):
        raise ResearchSetValidationError("note must be a string when provided")
    normalized = note.strip()
    return normalized or None


def _normalize_set_lifecycle(lifecycle: Any, *, visibility: str) -> str:
    if not isinstance(lifecycle, str):
        raise ResearchSetValidationError("lifecycle must be a string when provided")
    normalized = lifecycle.strip().lower()
    allowed = PRIVATE_SET_LIFECYCLES if visibility == "private" else CURATED_SET_LIFECYCLES
    if normalized not in allowed:
        raise ResearchSetValidationError(
            f"lifecycle must be one of {_quoted_task_choices(allowed)} for visibility '{visibility}'"
        )
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
        raise ResearchSetValidationError(
            f"preferred_task must be one of {_quoted_task_choices(SET_ITEM_TASKS)}"
        )
    return normalized


def _normalize_comparison_view_task(task: Any) -> str:
    if task is None:
        return "all"
    if not isinstance(task, str):
        raise ResearchSetValidationError("comparison_view_task must be a string when provided")
    normalized = task.strip() or "all"
    if normalized not in COMPARISON_VIEW_TASKS:
        raise ResearchSetValidationError(
            f"comparison_view_task must be one of {_quoted_task_choices(COMPARISON_VIEW_TASKS)}"
        )
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


def _set_expiration_for_record(record: ResearchSet, *, now: datetime) -> None:
    if record.visibility == "private" and record.lifecycle == "draft":
        record.expires_at = now + _draft_ttl()
    else:
        record.expires_at = None


def _touch_private_access(record: ResearchSet, *, now: datetime) -> None:
    if record.visibility != "private":
        return
    record.last_accessed_at = now
    _set_expiration_for_record(record, now=now)


def _serialize_workbench_state(record: ResearchSet) -> StoredResearchSetWorkbenchState:
    workbench_record = record.workbench_state
    if workbench_record is None:
        return StoredResearchSetWorkbenchState(
            preferred_task=None,
            comparison_view_task="all",
            sessions=tuple(),
        )

    return StoredResearchSetWorkbenchState(
        preferred_task=workbench_record.preferred_task,
        comparison_view_task=workbench_record.comparison_view_task,
        sessions=tuple(
            StoredResearchSetSession(session_id=entry.session_id, sort_order=entry.sort_order)
            for entry in sorted(workbench_record.sessions, key=lambda entry: entry.sort_order)
        ),
    )


def _serialize_set(record: ResearchSet) -> StoredResearchSet:
    return StoredResearchSet(
        set_id=record.set_id,
        corpus_language=record.corpus_language,
        label=record.label,
        note=record.note,
        visibility=record.visibility,
        lifecycle=record.lifecycle,
        source_curated_set_id=record.source_curated_set_id,
        created_by_user_id=record.created_by_user_id,
        updated_by_user_id=record.updated_by_user_id,
        version=record.version,
        created_at=record.created_at,
        updated_at=record.updated_at,
        published_at=record.published_at,
        archived_at=record.archived_at,
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
        workbench_state=_serialize_workbench_state(record),
    )


def _set_query():
    return select(ResearchSet).options(
        selectinload(ResearchSet.items),
        selectinload(ResearchSet.workbench_state).selectinload(ResearchSetWorkbenchState.sessions),
    )


def _get_owned_set_record(session, *, owner_user_id: str, set_id: str) -> ResearchSet:
    stmt = _set_query().where(
        ResearchSet.set_id == set_id,
        ResearchSet.visibility == "private",
        ResearchSet.owner_user_id == owner_user_id,
    )
    record = session.execute(stmt).scalars().first()
    if record is None:
        raise ResearchSetNotFoundError(f"Research set '{set_id}' was not found")
    return record


def _visible_curated_clause(*, include_archived_curated: bool) -> Any:
    allowed_lifecycles = ["saved"]
    if include_archived_curated:
        allowed_lifecycles.append("archived")
    return (ResearchSet.visibility == "curated") & (ResearchSet.lifecycle.in_(tuple(allowed_lifecycles)))


def _get_visible_set_record(
    session,
    *,
    owner_user_id: str | None,
    set_id: str,
    include_archived_curated: bool = False,
) -> ResearchSet:
    clauses = [_visible_curated_clause(include_archived_curated=include_archived_curated)]
    if owner_user_id:
        clauses.append((ResearchSet.visibility == "private") & (ResearchSet.owner_user_id == owner_user_id))
    stmt = _set_query().where(ResearchSet.set_id == set_id, or_(*clauses))
    record = session.execute(stmt).scalars().first()
    if record is None:
        raise ResearchSetNotFoundError(f"Research set '{set_id}' was not found")
    return record


def _existing_owner_labels(session, *, owner_user_id: str, language_slug: str) -> set[str]:
    stmt = select(ResearchSet.label).where(
        ResearchSet.visibility == "private",
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
    source_label: str | None,
) -> str:
    existing_labels = _existing_owner_labels(session, owner_user_id=owner_user_id, language_slug=language_slug)
    if source_label:
        base_label = f"{source_label} (modifiziert)"
        return _next_generated_label(
            existing_labels,
            base_label=base_label,
            suffix_template=f"{source_label} (modifiziert {{index}})",
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


def _references_from_stored_items(items: list[ResearchSetItem]) -> tuple[TaskItemReference, ...]:
    return tuple(
        TaskItemReference(
            task=item.task,
            item_id=item.item_id,
            segment_id=item.segment_id,
            note=item.note,
        )
        for item in sorted(items, key=lambda entry: entry.sort_order)
    )


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


def _ensure_workbench_state(record: ResearchSet) -> ResearchSetWorkbenchState:
    if record.workbench_state is None:
        record.workbench_state = ResearchSetWorkbenchState(
            set_id=record.set_id,
            preferred_task=None,
            comparison_view_task="all",
        )
    return record.workbench_state


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


def _materialize_workbench_sessions(record: ResearchSetWorkbenchState, session_ids: tuple[str, ...]) -> None:
    record.sessions.clear()
    for sort_order, session_id in enumerate(session_ids, start=1):
        record.sessions.append(
            ResearchSetWorkbenchSessionLink(
                set_id=record.set_id,
                session_id=session_id,
                sort_order=sort_order,
            )
        )


def _update_workbench_state(
    record: ResearchSet,
    *,
    preferred_task: object = UNSET,
    comparison_view_task: object = UNSET,
    session_ids: object = UNSET,
) -> None:
    workbench_state = _ensure_workbench_state(record)
    if preferred_task is not UNSET:
        workbench_state.preferred_task = _normalize_preferred_task(preferred_task)
    if comparison_view_task is not UNSET:
        workbench_state.comparison_view_task = _normalize_comparison_view_task(comparison_view_task)
    if session_ids is not UNSET:
        _materialize_workbench_sessions(workbench_state, session_ids)


def _sort_visible_sets(records: tuple[StoredResearchSet, ...]) -> tuple[StoredResearchSet, ...]:
    return tuple(
        sorted(
            records,
            key=lambda record: (
                0 if record.visibility == "curated" else 1,
                -record.updated_at.timestamp(),
                -record.created_at.timestamp(),
            ),
        )
    )


def create_draft_set(
    *,
    owner_user_id: str,
    corpus_language: str,
    source_curated_set_id: str | None = None,
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

    if source_curated_set_id and source_preset_id:
        raise ResearchSetValidationError("Only one of source_curated_set_id or source_preset_id may be provided")
    normalized_source_curated_set_id = (source_curated_set_id or source_preset_id or "").strip() or None

    def operation() -> StoredResearchSet:
        with get_session() as session:
            source_record = None
            source_references: tuple[TaskItemReference, ...] = tuple()
            source_label = None
            if normalized_source_curated_set_id is not None:
                source_record = _get_visible_set_record(
                    session,
                    owner_user_id=owner_id,
                    set_id=normalized_source_curated_set_id,
                )
                if source_record.visibility != "curated" or source_record.lifecycle != "saved":
                    raise ResearchSetValidationError(
                        f"Unknown curated set '{normalized_source_curated_set_id}' for corpus_language '{language_slug}'"
                    )
                if source_record.corpus_language != language_slug:
                    raise ResearchSetValidationError(
                        f"Unknown curated set '{normalized_source_curated_set_id}' for corpus_language '{language_slug}'"
                    )
                source_references = _references_from_stored_items(source_record.items)
                source_label = source_record.label

            effective_label = normalized_label or _default_draft_label(
                session,
                owner_user_id=owner_id,
                language_slug=language_slug,
                source_label=source_label,
            )
            record = ResearchSet(
                set_id=str(uuid.uuid4()),
                owner_user_id=owner_id,
                corpus_language=language_slug,
                label=effective_label,
                note=normalized_note,
                visibility="private",
                lifecycle="draft",
                source_curated_set_id=normalized_source_curated_set_id,
                created_by_user_id=owner_id,
                updated_by_user_id=owner_id,
                version=1,
                created_at=now,
                updated_at=now,
                published_at=None,
                archived_at=None,
                last_accessed_at=now,
                expires_at=now + _draft_ttl(),
            )
            session.add(record)
            _materialize_set_items(record, source_references)
            _update_workbench_state(
                record,
                preferred_task=normalized_preferred_task,
                comparison_view_task=normalized_view_task,
                session_ids=tuple(),
            )
            if source_record is not None:
                source_workbench_state = _serialize_workbench_state(source_record)
                _update_workbench_state(
                    record,
                    preferred_task=source_workbench_state.preferred_task,
                    comparison_view_task=source_workbench_state.comparison_view_task,
                    session_ids=tuple(entry.session_id for entry in source_workbench_state.sessions),
                )
                if normalized_preferred_task is not None:
                    _update_workbench_state(record, preferred_task=normalized_preferred_task)
                if comparison_view_task is not None:
                    _update_workbench_state(record, comparison_view_task=normalized_view_task)
            session.flush()
            return _serialize_set(record)

    return _run_storage_operation(operation)


def create_private_copy_from_curated(
    *,
    owner_user_id: str,
    source_set_id: str,
    label: str | None = None,
    note: str | None = None,
    lifecycle: str = "draft",
) -> StoredResearchSet:
    owner_id = _normalize_owner_user_id(owner_user_id)
    normalized_source_set_id = (source_set_id or "").strip()
    normalized_label = _normalize_optional_label(label)
    normalized_note = _normalize_optional_note(note)
    normalized_lifecycle = _normalize_set_lifecycle(lifecycle, visibility="private")
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            source_record = _get_visible_set_record(session, owner_user_id=owner_id, set_id=normalized_source_set_id)
            effective_label = normalized_label or _default_draft_label(
                session,
                owner_user_id=owner_id,
                language_slug=source_record.corpus_language,
                source_label=source_record.label,
            )
            copied_record = ResearchSet(
                set_id=str(uuid.uuid4()),
                owner_user_id=owner_id,
                corpus_language=source_record.corpus_language,
                label=effective_label,
                note=normalized_note if note is not None else source_record.note,
                visibility="private",
                lifecycle=normalized_lifecycle,
                source_curated_set_id=(
                    source_record.set_id if source_record.visibility == "curated" else source_record.source_curated_set_id
                ),
                created_by_user_id=owner_id,
                updated_by_user_id=owner_id,
                version=1,
                created_at=now,
                updated_at=now,
                published_at=None,
                archived_at=None,
                last_accessed_at=now,
                expires_at=None,
            )
            session.add(copied_record)
            _materialize_set_items(copied_record, _references_from_stored_items(source_record.items))
            source_workbench_state = _serialize_workbench_state(source_record)
            _update_workbench_state(
                copied_record,
                preferred_task=source_workbench_state.preferred_task,
                comparison_view_task=source_workbench_state.comparison_view_task,
                session_ids=tuple(entry.session_id for entry in source_workbench_state.sessions),
            )
            _set_expiration_for_record(copied_record, now=now)
            session.flush()
            return _serialize_set(copied_record)

    return _run_storage_operation(operation)


def create_curated_set(
    *,
    admin_user_id: str,
    corpus_language: str,
    label: str,
    items: list[Any],
    note: str | None = None,
    preferred_task: str | None = None,
    comparison_view_task: str | None = None,
    sessions: list[Any] | None = None,
) -> StoredResearchSet:
    admin_id = _normalize_owner_user_id(admin_user_id)
    language_slug = _normalize_language_slug(corpus_language)
    normalized_label = _normalize_required_label(label)
    normalized_note = _normalize_optional_note(note)
    normalized_preferred_task = _normalize_preferred_task(preferred_task)
    normalized_view_task = _normalize_comparison_view_task(comparison_view_task)
    session_ids = _validated_session_ids(sessions or [], language_slug=language_slug, context="curated set")
    references = _validated_item_references(items, language_slug=language_slug, context="curated set")
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = ResearchSet(
                set_id=str(uuid.uuid4()),
                owner_user_id=None,
                corpus_language=language_slug,
                label=normalized_label,
                note=normalized_note,
                visibility="curated",
                lifecycle="saved",
                source_curated_set_id=None,
                created_by_user_id=admin_id,
                updated_by_user_id=admin_id,
                version=1,
                created_at=now,
                updated_at=now,
                published_at=now,
                archived_at=None,
                last_accessed_at=now,
                expires_at=None,
            )
            session.add(record)
            _materialize_set_items(record, references)
            _update_workbench_state(
                record,
                preferred_task=normalized_preferred_task,
                comparison_view_task=normalized_view_task,
                session_ids=session_ids,
            )
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
                _touch_private_access(record, now=now)
            return _serialize_set(record)

    return _run_storage_operation(operation)


def get_visible_set(
    *,
    owner_user_id: str | None,
    set_id: str,
    include_archived_curated: bool = False,
    touch_access: bool = True,
) -> StoredResearchSet:
    normalized_set_id = (set_id or "").strip()
    if not normalized_set_id:
        raise ResearchSetValidationError("set_id is required")
    normalized_owner_id = _normalize_optional_owner_user_id(owner_user_id)
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = _get_visible_set_record(
                session,
                owner_user_id=normalized_owner_id,
                set_id=normalized_set_id,
                include_archived_curated=include_archived_curated,
            )
            if touch_access:
                _touch_private_access(record, now=now)
            return _serialize_set(record)

    return _run_storage_operation(operation)


def update_set_metadata(
    *,
    owner_user_id: str,
    set_id: str,
    label: object = UNSET,
    note: object = UNSET,
    lifecycle: object = UNSET,
    state: object = UNSET,
) -> StoredResearchSet:
    owner_id = _normalize_owner_user_id(owner_user_id)
    normalized_set_id = (set_id or "").strip()
    if not normalized_set_id:
        raise ResearchSetValidationError("set_id is required")
    if lifecycle is not UNSET and state is not UNSET:
        raise ResearchSetValidationError("Use either lifecycle or state, not both")
    requested_lifecycle = lifecycle if lifecycle is not UNSET else state
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = _get_owned_set_record(session, owner_user_id=owner_id, set_id=normalized_set_id)

            if label is not UNSET:
                record.label = _normalize_optional_label(label)
            if note is not UNSET:
                record.note = _normalize_optional_note(note)
            if requested_lifecycle is not UNSET:
                record.lifecycle = _normalize_set_lifecycle(requested_lifecycle, visibility="private")

            if record.lifecycle == "saved" and not record.label:
                raise ResearchSetValidationError("Saved sets require a non-empty label")

            record.updated_at = now
            record.updated_by_user_id = owner_id
            _touch_private_access(record, now=now)
            session.flush()
            return _serialize_set(record)

    return _run_storage_operation(operation)


def update_curated_set(
    *,
    admin_user_id: str,
    set_id: str,
    label: object = UNSET,
    note: object = UNSET,
    items: object = UNSET,
    preferred_task: object = UNSET,
    comparison_view_task: object = UNSET,
    sessions: object = UNSET,
) -> StoredResearchSet:
    admin_id = _normalize_owner_user_id(admin_user_id)
    normalized_set_id = (set_id or "").strip()
    if not normalized_set_id:
        raise ResearchSetValidationError("set_id is required")
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = _get_visible_set_record(
                session,
                owner_user_id=admin_id,
                set_id=normalized_set_id,
                include_archived_curated=True,
            )
            if record.visibility != "curated":
                raise ResearchSetValidationError(f"Research set '{normalized_set_id}' is not curated")

            if label is not UNSET:
                record.label = _normalize_required_label(label)
            if note is not UNSET:
                record.note = _normalize_optional_note(note)
            if items is not UNSET:
                if not isinstance(items, list):
                    raise ResearchSetValidationError("items must be a JSON array")
                references = _validated_item_references(items, language_slug=record.corpus_language, context=f"set '{normalized_set_id}'")
                _materialize_set_items(record, references)
            if preferred_task is not UNSET or comparison_view_task is not UNSET:
                _update_workbench_state(
                    record,
                    preferred_task=preferred_task,
                    comparison_view_task=comparison_view_task,
                )
            if sessions is not UNSET:
                if not isinstance(sessions, list):
                    raise ResearchSetValidationError("sessions must be a JSON array")
                session_ids = _validated_session_ids(sessions, language_slug=record.corpus_language, context=f"set '{normalized_set_id}'")
                _update_workbench_state(record, session_ids=session_ids)

            if not record.label:
                raise ResearchSetValidationError("Curated sets require a non-empty label")

            record.updated_at = now
            record.updated_by_user_id = admin_id
            record.version += 1
            if record.published_at is None:
                record.published_at = now
            session.flush()
            return _serialize_set(record)

    return _run_storage_operation(operation)


def archive_curated_set(*, admin_user_id: str, set_id: str) -> StoredResearchSet:
    admin_id = _normalize_owner_user_id(admin_user_id)
    normalized_set_id = (set_id or "").strip()
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = _get_visible_set_record(
                session,
                owner_user_id=admin_id,
                set_id=normalized_set_id,
                include_archived_curated=True,
            )
            if record.visibility != "curated":
                raise ResearchSetValidationError(f"Research set '{normalized_set_id}' is not curated")
            record.lifecycle = "archived"
            record.archived_at = now
            record.updated_at = now
            record.updated_by_user_id = admin_id
            record.version += 1
            session.flush()
            return _serialize_set(record)

    return _run_storage_operation(operation)


def reactivate_curated_set(*, admin_user_id: str, set_id: str) -> StoredResearchSet:
    admin_id = _normalize_owner_user_id(admin_user_id)
    normalized_set_id = (set_id or "").strip()
    now = _utcnow()

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = _get_visible_set_record(
                session,
                owner_user_id=admin_id,
                set_id=normalized_set_id,
                include_archived_curated=True,
            )
            if record.visibility != "curated":
                raise ResearchSetValidationError(f"Research set '{normalized_set_id}' is not curated")
            record.lifecycle = "saved"
            record.archived_at = None
            record.updated_at = now
            record.updated_by_user_id = admin_id
            record.version += 1
            if record.published_at is None:
                record.published_at = now
            session.flush()
            return _serialize_set(record)

    return _run_storage_operation(operation)


def update_set_workbench_state(
    *,
    owner_user_id: str,
    set_id: str,
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
            _update_workbench_state(
                record,
                preferred_task=preferred_task,
                comparison_view_task=comparison_view_task,
            )
            record.updated_at = now
            record.updated_by_user_id = owner_id
            _touch_private_access(record, now=now)
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
            stmt = _set_query().where(
                ResearchSet.visibility == "private",
                ResearchSet.owner_user_id == owner_id,
                ResearchSet.corpus_language == language_slug,
            )
            if not include_drafts:
                stmt = stmt.where(ResearchSet.lifecycle == "saved")
            stmt = stmt.order_by(ResearchSet.updated_at.desc(), ResearchSet.created_at.desc())
            records = session.execute(stmt).scalars().all()
            return tuple(_serialize_set(record) for record in records)

    return _run_storage_operation(operation)


def list_visible_sets_for_user(
    *,
    owner_user_id: str | None,
    corpus_language: str,
    include_drafts: bool = False,
    include_archived_curated: bool = False,
) -> tuple[StoredResearchSet, ...]:
    normalized_owner_id = _normalize_optional_owner_user_id(owner_user_id)
    language_slug = _normalize_language_slug(corpus_language)

    def operation() -> tuple[StoredResearchSet, ...]:
        with get_session() as session:
            clauses = [_visible_curated_clause(include_archived_curated=include_archived_curated)]
            if normalized_owner_id:
                clauses.append(
                    (ResearchSet.visibility == "private")
                    & (ResearchSet.owner_user_id == normalized_owner_id)
                    & (ResearchSet.lifecycle.in_(PRIVATE_SET_LIFECYCLES if include_drafts else ("saved",)))
                )
            stmt = _set_query().where(
                ResearchSet.corpus_language == language_slug,
                or_(*clauses),
            )
            records = tuple(_serialize_set(record) for record in session.execute(stmt).scalars().all())
            return _sort_visible_sets(records)

    return _run_storage_operation(operation)


def list_selectable_sets_for_user(
    *,
    owner_user_id: str | None,
    corpus_language: str,
    current_set_id: str | None = None,
) -> tuple[StoredResearchSet, ...]:
    normalized_owner_id = _normalize_optional_owner_user_id(owner_user_id)
    visible_sets = list(
        list_visible_sets_for_user(
            owner_user_id=normalized_owner_id,
            corpus_language=corpus_language,
            include_drafts=False,
            include_archived_curated=False,
        )
    )
    normalized_current_set_id = (current_set_id or "").strip()
    if not normalized_current_set_id or normalized_owner_id is None:
        return tuple(visible_sets)

    if any(record.set_id == normalized_current_set_id for record in visible_sets):
        return tuple(visible_sets)

    try:
        current_record = load_owned_set(owner_user_id=normalized_owner_id, set_id=normalized_current_set_id, touch_access=False)
    except (ResearchSetNotFoundError, ResearchSetStorageUnavailableError, ResearchSetValidationError):
        return tuple(visible_sets)

    if current_record.corpus_language != _normalize_language_slug(corpus_language):
        return tuple(visible_sets)

    return (current_record, *visible_sets)


def list_selectable_owned_sets(
    *,
    owner_user_id: str,
    corpus_language: str,
    current_set_id: str | None = None,
) -> tuple[StoredResearchSet, ...]:
    return list_selectable_sets_for_user(
        owner_user_id=owner_user_id,
        corpus_language=corpus_language,
        current_set_id=current_set_id,
    )


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
            record.updated_by_user_id = owner_id
            _touch_private_access(record, now=now)
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
            _update_workbench_state(record, session_ids=session_ids)
            record.updated_at = now
            record.updated_by_user_id = owner_id
            _touch_private_access(record, now=now)
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
            _touch_private_access(source_record, now=now)
            source_workbench_state = _serialize_workbench_state(source_record)

            saved_record = ResearchSet(
                set_id=str(uuid.uuid4()),
                owner_user_id=owner_id,
                corpus_language=source_record.corpus_language,
                label=normalized_label,
                note=source_record.note,
                visibility="private",
                lifecycle="saved",
                source_curated_set_id=source_record.source_curated_set_id,
                created_by_user_id=owner_id,
                updated_by_user_id=owner_id,
                version=1,
                created_at=now,
                updated_at=now,
                published_at=None,
                archived_at=None,
                last_accessed_at=now,
                expires_at=None,
            )
            session.add(saved_record)
            _materialize_set_items(saved_record, _references_from_stored_items(source_record.items))
            _update_workbench_state(
                saved_record,
                preferred_task=source_workbench_state.preferred_task,
                comparison_view_task=source_workbench_state.comparison_view_task,
                session_ids=tuple(entry.session_id for entry in source_workbench_state.sessions),
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
            stmt = _set_query().where(
                ResearchSet.visibility == "private",
                ResearchSet.lifecycle == "draft",
                ResearchSet.expires_at.is_not(None),
                ResearchSet.expires_at <= effective_now,
            )
            expired_records = list(session.execute(stmt).scalars().all())
            for record in expired_records:
                session.delete(record)
            return len(expired_records)

    return _run_storage_operation(operation)


def ensure_curated_test_set(*, admin_user_id: str | None = None) -> StoredResearchSet:
    normalized_admin_id = _normalize_optional_owner_user_id(admin_user_id)
    language_slug = "spanish"
    now = _utcnow()
    references = _validated_item_references(
        [
            {"task": "wordlist", "item_id": "wl_001"},
            {"task": "wordlist", "item_id": "wl_002"},
            {"task": "text", "item_id": "d_01"},
            {"task": "text", "item_id": "d_02"},
        ],
        language_slug=language_slug,
        context="curated test set",
    )

    def operation() -> StoredResearchSet:
        with get_session() as session:
            record = session.get(ResearchSet, RESEARCH_CURATED_TEST_SET_ID)
            if record is None:
                record = ResearchSet(
                    set_id=RESEARCH_CURATED_TEST_SET_ID,
                    owner_user_id=None,
                    corpus_language=language_slug,
                    label="PROMAT Testset",
                    note="DB-seeded curated baseline set.",
                    visibility="curated",
                    lifecycle="saved",
                    source_curated_set_id=None,
                    created_by_user_id=normalized_admin_id,
                    updated_by_user_id=normalized_admin_id,
                    version=1,
                    created_at=now,
                    updated_at=now,
                    published_at=now,
                    archived_at=None,
                    last_accessed_at=now,
                    expires_at=None,
                )
                session.add(record)
                _materialize_set_items(record, references)
                _update_workbench_state(
                    record,
                    preferred_task="wordlist",
                    comparison_view_task="wordlist",
                    session_ids=tuple(),
                )
            else:
                if record.visibility != "curated":
                    raise ResearchSetValidationError(
                        f"Existing set '{RESEARCH_CURATED_TEST_SET_ID}' is not curated and cannot be reused"
                    )
                if normalized_admin_id is not None and record.created_by_user_id is None:
                    record.created_by_user_id = normalized_admin_id
                if normalized_admin_id is not None:
                    record.updated_by_user_id = normalized_admin_id
            session.flush()
            return _serialize_set(record)

    return _run_storage_operation(operation)