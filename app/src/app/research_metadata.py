"""SQLAlchemy models for imported research person/session/exposure metadata."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .auth.models import Base


class ResearchPerson(Base):
    __tablename__ = "research_people"
    __table_args__ = (
        CheckConstraint("speaker_type IN ('learner', 'native_speaker')", name="ck_research_people_speaker_type"),
        CheckConstraint(
            "research_consent_signed IS NULL OR research_consent_signed IN ('yes', 'no', 'unknown')",
            name="ck_research_people_research_consent_signed",
        ),
        CheckConstraint(
            "teaching_consent_signed IS NULL OR teaching_consent_signed IN ('yes', 'no', 'unknown')",
            name="ck_research_people_teaching_consent_signed",
        ),
    )

    person_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    speaker_type: Mapped[str] = mapped_column(String(32), nullable=False)
    l1: Mapped[str | None] = mapped_column(String(32), nullable=True)
    l1_additional: Mapped[str | None] = mapped_column(Text, nullable=True)
    mother_l1: Mapped[str | None] = mapped_column(String(32), nullable=True)
    father_l1: Mapped[str | None] = mapped_column(String(32), nullable=True)
    additional_languages: Mapped[str | None] = mapped_column(Text, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    birth_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_region: Mapped[str | None] = mapped_column(Text, nullable=True)
    childhood_region: Mapped[str | None] = mapped_column(Text, nullable=True)
    origin_country: Mapped[str | None] = mapped_column(Text, nullable=True)
    origin_region: Mapped[str | None] = mapped_column(Text, nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    person_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_consent_signed: Mapped[str | None] = mapped_column(String(16), nullable=True)
    teaching_consent_signed: Mapped[str | None] = mapped_column(String(16), nullable=True)
    consent_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    consent_file: Mapped[str | None] = mapped_column(Text, nullable=True)
    questionnaire_file: Mapped[str | None] = mapped_column(Text, nullable=True)
    secure_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    sessions: Mapped[list["ResearchSession"]] = relationship(
        "ResearchSession",
        back_populates="person",
        cascade="all, delete-orphan",
        order_by="ResearchSession.session_id",
    )


class ResearchSession(Base):
    __tablename__ = "research_sessions"
    __table_args__ = (
        CheckConstraint("target_language IN ('es', 'fr', 'en', 'de')", name="ck_research_sessions_target_language"),
        CheckConstraint(
            "context IS NULL OR context IN ('baseline', 'follow_up')",
            name="ck_research_sessions_context",
        ),
        UniqueConstraint("person_id", "session_ref", name="uq_research_sessions_person_session_ref"),
    )

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    person_id: Mapped[str] = mapped_column(ForeignKey("research_people.person_id", ondelete="CASCADE"), nullable=False, index=True)
    session_ref: Mapped[str] = mapped_column(String(8), nullable=False)
    corpus_language: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    target_language: Mapped[str] = mapped_column(String(8), nullable=False)
    standard_variety: Mapped[str | None] = mapped_column(String(32), nullable=True)
    level_self: Mapped[str | None] = mapped_column(String(32), nullable=True)
    level_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    recording_year: Mapped[int] = mapped_column(Integer, nullable=False)
    recording_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    recorded_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[str | None] = mapped_column(String(32), nullable=True)
    stays_in_target_country: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    session_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    documented_tasks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    person: Mapped[ResearchPerson] = relationship("ResearchPerson", back_populates="sessions")
    exposures: Mapped[list["ResearchSessionExposure"]] = relationship(
        "ResearchSessionExposure",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ResearchSessionExposure.sort_order",
    )


class ResearchSessionExposure(Base):
    __tablename__ = "research_session_exposures"
    __table_args__ = (
        CheckConstraint("sort_order >= 1", name="ck_research_session_exposures_sort_order"),
        UniqueConstraint("session_id", "sort_order", name="uq_research_session_exposures_session_sort"),
    )

    exposure_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("research_sessions.session_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    country: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_months: Mapped[float | None] = mapped_column(Float, nullable=True)
    exposure_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    exposure_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    session: Mapped[ResearchSession] = relationship("ResearchSession", back_populates="exposures")