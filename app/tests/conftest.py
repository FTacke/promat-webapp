"""Shared pytest wiring for the PROMAT test suite.

The canonical research-player configuration (task catalogs, player configs) is operator-owned runtime
configuration under ``<PROMAT_RUNTIME_ROOT>/data/config/research_player`` and is deliberately not part of the
repository. Tests that need *some* catalog content use the tracked, minimal fixture runtime root below
instead of depending on a developer machine or on production data. Tests that validate the content of the
real catalogs are marked ``data`` (see ``docs/runbooks/test-and-ci.md``).
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


TESTS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = TESTS_ROOT.parents[1]
FIXTURE_RUNTIME_ROOT = TESTS_ROOT / "fixtures" / "runtime"


def _clear_catalog_caches() -> None:
    scripts_root = str(REPO_ROOT / "scripts" / "research_data_intake")
    if scripts_root not in sys.path:
        sys.path.insert(0, scripts_root)
    src_root = str(REPO_ROOT / "app" / "src")
    if src_root not in sys.path:
        sys.path.insert(0, src_root)

    from app.research_presets import clear_research_preset_caches
    from intake_batch_common import load_task_catalog_item_index

    clear_research_preset_caches()
    load_task_catalog_item_index.cache_clear()


@pytest.fixture
def fixture_runtime_root(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the runtime root at the tracked minimal catalog fixtures and reset catalog caches."""
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(FIXTURE_RUNTIME_ROOT))
    _clear_catalog_caches()
    yield FIXTURE_RUNTIME_ROOT
    monkeypatch.undo()
    _clear_catalog_caches()


@pytest.fixture
def real_app_factory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Build the application through the real ``create_app`` composition (blueprints, headers, error handlers).

    Most tests assemble a Flask app by hand; this factory exists for invariants that only hold in the composed
    app (security headers, cache rules, analytics, error handling). The auth database is a private SQLite file
    with the model schema, and every setting the factory needs is passed through the environment so that the
    configuration module is re-read exactly as it is in a real start.
    """
    import importlib

    src_root = str(REPO_ROOT / "app" / "src")
    if src_root not in sys.path:
        sys.path.insert(0, src_root)

    created: list[object] = []

    def build(
        *,
        env_name: str = "testing",
        env: dict[str, str] | None = None,
        runtime_root: Path | None = None,
        database_url: str | None = None,
    ):
        runtime_root = runtime_root or tmp_path / "runtime"
        public_root = tmp_path / "public"
        for directory in (runtime_root / "data" / "sessions", runtime_root / "data" / "config", runtime_root / "logs"):
            if runtime_root != FIXTURE_RUNTIME_ROOT:
                directory.mkdir(parents=True, exist_ok=True)
        public_root.mkdir(parents=True, exist_ok=True)
        # With an explicit database_url (PostgreSQL integration tests) the schema comes from the real migrations.
        db_url = database_url or f"sqlite:///{(tmp_path / 'real-app.sqlite3').as_posix()}"

        for name in ("PROMAT_ENV", "RATE_LIMIT_STORAGE_URI", "RATELIMIT_STORAGE_URI", "VITE_GOATCOUNTER_URL", "MAX_CONTENT_LENGTH"):
            monkeypatch.delenv(name, raising=False)
        monkeypatch.setenv("APP_ENV", env_name)
        monkeypatch.setenv("FLASK_ENV", env_name)
        monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(runtime_root))
        monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(public_root))
        monkeypatch.setenv("AUTH_DATABASE_URL", db_url)
        monkeypatch.setenv("FLASK_SECRET_KEY", "real-app-flask-secret-key-0123456789abcdef")
        monkeypatch.setenv("JWT_SECRET_KEY", "real-app-jwt-secret-key-fedcba9876543210")
        monkeypatch.setenv("PROMAT_PUBLIC_BASE_URL", "https://promat.test")
        for key, value in (env or {}).items():
            monkeypatch.setenv(key, value)

        import app.config as config_module

        importlib.reload(config_module)

        if database_url is None:
            from sqlalchemy import create_engine

            from app.auth.models import Base

            engine = create_engine(db_url)
            Base.metadata.create_all(engine)
            engine.dispose()

        from app import create_app
        from app.extensions import limiter

        # The limiter is a process-wide singleton; an earlier debug app may have switched it off.
        limiter.enabled = True
        flask_app = create_app(env_name)
        created.append(flask_app)
        return flask_app

    yield build
    # A production-like app starts a storage health monitor thread; do not let its outage flag leak into other tests.
    from app.extensions import stop_rate_limit_health_monitors

    stop_rate_limit_health_monitors()
