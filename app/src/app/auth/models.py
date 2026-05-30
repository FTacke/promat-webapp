"""SQLAlchemy ORM models for the new auth schema.

This file defines declarative models for User, RefreshToken and ResetToken.
These are intentionally independent from existing sqlite helpers; they can be
imported by migration/seed scripts or by application services when integrating
SQLAlchemy into the app.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    # Use platform-specific UUID type when possible (Postgres), otherwise store as text
    # Use text-based UUID representation for cross-database compatibility
    id: Mapped[Optional[str]] = mapped_column("user_id", String(36), primary_key=True)

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="user")

    # Status & controls
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    must_reset_password: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    access_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    display_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.user_id"), nullable=True
    )

    login_failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deletion_requested_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Account kind: 'personal' (default) or 'group'
    account_kind: Mapped[str] = mapped_column(String(16), nullable=False, default="personal")
    responsible_admin_user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True
    )

    # relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    reset_tokens: Mapped[list["ResetToken"]] = relationship(
        "ResetToken", back_populates="user", cascade="all, delete-orphan"
    )
    created_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side="User.id",
        foreign_keys=[created_by_user_id],
    )
    responsible_admin: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side="User.id",
        foreign_keys=[responsible_admin_user_id],
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_id: Mapped[Optional[str]] = mapped_column(
        "token_id", String(36), primary_key=True
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.user_id"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    replaced_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")


class ResetToken(Base):
    __tablename__ = "reset_tokens"

    id: Mapped[Optional[str]] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.user_id"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped[User] = relationship("User", back_populates="reset_tokens")


class AnalyticsDaily(Base):
    __tablename__ = "analytics_daily"

    activity_date: Mapped[date] = mapped_column("date", Date, primary_key=True)
    unique_visitors: Mapped[int] = mapped_column("visitors", Integer, nullable=False, default=0)
    page_views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AnalyticsLanguageAreaDaily(Base):
    __tablename__ = "analytics_language_area_daily"

    activity_date: Mapped[date] = mapped_column("date", Date, primary_key=True)
    section: Mapped[str] = mapped_column(String(32), primary_key=True)
    corpus_language: Mapped[str] = mapped_column(String(32), primary_key=True)
    unique_visitors: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    page_views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AccessRequest(Base):
    __tablename__ = "access_requests"

    id: Mapped[Optional[str]] = mapped_column(String(36), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="submitted")
    first_name: Mapped[str] = mapped_column(String(160), nullable=False)
    last_name: Mapped[str] = mapped_column(String(160), nullable=False)
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    role_or_function: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    consent_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ui_lang: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    requested_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
