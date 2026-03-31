"""Lightweight SQLAlchemy integration for PROMAT."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_engine = None
_session_local: sessionmaker | None = None


def init_engine(app) -> None:
    """Initialize the SQLAlchemy engine from app config."""
    global _engine, _session_local
    db_url = app.config.get("AUTH_DATABASE_URL")
    if not db_url:
        raise RuntimeError("AUTH_DATABASE_URL is not configured")

    _engine = create_engine(db_url, future=True)
    _session_local = sessionmaker(bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_engine():
    return _engine


@contextmanager
def get_session() -> Iterator[Session]:
    """Yield a SQLAlchemy session and manage commit/rollback."""
    if _session_local is None:
        raise RuntimeError("Engine not initialized — call init_engine(app) first")
    session = _session_local()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()