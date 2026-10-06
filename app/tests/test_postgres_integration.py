"""Tests against a real PostgreSQL server (the production database engine).

Most of the suite runs on SQLite with ``create_all()``, which cannot see CHECK constraints, SQL-migration drift or
Postgres-only behaviour (the ``access_requests`` status constraint was violated by the application for exactly
that reason). These tests apply the real migration chain to a throw-away database and exercise the application
against it.

They need a server and are skipped without one:

    PROMAT_TEST_POSTGRES_URL=postgresql+psycopg2://postgres:<pw>@127.0.0.1:5432/postgres

The role needs ``CREATEDB``; each test module run creates and drops its own database. CI provides a service
container (see ``.github/workflows/ci.yml``).
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import re
import sys
import uuid

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(Path(__file__).resolve().parents[2] / "public"))

pytestmark = pytest.mark.postgres

SERVER_URL = os.environ.get("PROMAT_TEST_POSTGRES_URL", "").strip()
APP_ROOT = Path(__file__).resolve().parents[1]

if not SERVER_URL:
    pytest.skip("PROMAT_TEST_POSTGRES_URL is not set; PostgreSQL integration tests need a server", allow_module_level=True)

psycopg2 = pytest.importorskip("psycopg2")


def _dsn(url: str) -> str:
    return url.replace("postgresql+psycopg2://", "postgresql://").replace("postgresql+psycopg://", "postgresql://")


def _with_database(url: str, database: str) -> str:
    return re.sub(r"/[^/?]*(\?|$)", f"/{database}\\1", url, count=1)


def _load_migration_runner():
    spec = importlib.util.spec_from_file_location("apply_auth_migration_pg", APP_ROOT / "scripts" / "apply_auth_migration.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def migrated_database_url():
    database = f"promat_it_{uuid.uuid4().hex[:12]}"
    admin = psycopg2.connect(_dsn(SERVER_URL))
    admin.autocommit = True
    with admin.cursor() as cursor:
        cursor.execute(f'CREATE DATABASE "{database}"')
    database_url = _with_database(SERVER_URL, database)

    previous = {name: os.environ.get(name) for name in ("AUTH_DATABASE_URL", "PROMAT_ENV", "FLASK_ENV", "APP_ENV")}
    os.environ["AUTH_DATABASE_URL"] = database_url
    try:
        runner = _load_migration_runner()
        runner.apply_postgres_migration()
        yield database_url
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        with admin.cursor() as cursor:
            cursor.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()", (database,))
            cursor.execute(f'DROP DATABASE IF EXISTS "{database}"')
        admin.close()


def _connect(database_url: str):
    connection = psycopg2.connect(_dsn(database_url))
    connection.autocommit = True
    return connection


def test_migration_chain_is_idempotent(migrated_database_url: str) -> None:
    runner = _load_migration_runner()
    os.environ["AUTH_DATABASE_URL"] = migrated_database_url

    runner.apply_postgres_migration()  # a second run over an up-to-date database must not fail
    runner.apply_postgres_migration()

    with _connect(migrated_database_url) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'access_requests'")
        assert cursor.fetchone()[0] == 1


def test_models_and_migrated_schema_agree(migrated_database_url: str) -> None:
    from sqlalchemy import create_engine, inspect

    from app.auth.models import Base

    engine = create_engine(migrated_database_url)
    try:
        inspector = inspect(engine)
        db_tables = set(inspector.get_table_names())
        missing_tables = {table for table in Base.metadata.tables if table not in db_tables}
        assert missing_tables == set(), f"model tables missing from the migrated schema: {missing_tables}"

        for table_name, table in Base.metadata.tables.items():
            db_columns = {column["name"] for column in inspector.get_columns(table_name)}
            model_columns = {column.name for column in table.columns}
            assert model_columns <= db_columns, f"{table_name}: columns {model_columns - db_columns} are not in the migrated schema"
    finally:
        engine.dispose()


def test_access_request_status_constraint_accepts_every_status_the_application_writes(migrated_database_url: str) -> None:
    from app.auth.models import ACCESS_REQUEST_STATUSES

    with _connect(migrated_database_url) as connection, connection.cursor() as cursor:
        for status in ACCESS_REQUEST_STATUSES:
            cursor.execute(
                "INSERT INTO access_requests (id, status, first_name, last_name, institution, role_or_function, email, purpose, consent_confirmed) "
                "VALUES (%s, %s, 'A', 'B', 'I', 'R', 'a@example.org', 'P', TRUE)",
                (f"constraint-{status}", status),
            )
        with pytest.raises(psycopg2.errors.CheckViolation):
            cursor.execute(
                "INSERT INTO access_requests (id, status, first_name, last_name, institution, role_or_function, email, purpose, consent_confirmed) "
                "VALUES ('constraint-bogus', 'bogus', 'A', 'B', 'I', 'R', 'a@example.org', 'P', TRUE)"
            )


PROD_MAIL_ENV = {
    "AUTH_ACCESS_REQUEST_EMAIL": "ops@promat.test",
    "AUTH_ACCESS_REQUEST_FROM_EMAIL": "noreply@promat.test",
    "AUTH_ACCESS_REQUEST_SMTP_HOST": "smtp.promat.test",
}


@pytest.fixture
def pg_app(real_app_factory, migrated_database_url: str):
    flask_app = real_app_factory(env=PROD_MAIL_ENV, database_url=migrated_database_url)
    sent: list[object] = []
    flask_app.config.update(
        AUTH_ACCESS_REQUEST_MAIL_ENABLED=True,
        AUTH_ACCESS_REQUEST_MAIL_SENDER=sent.append,
        AUTH_ACCESS_REQUEST_FORM_MAX_AGE_SECONDS=43200,
        AUTH_ACCESS_REQUEST_MIN_SUBMIT_SECONDS=0,
    )
    flask_app.config["TEST_SENT_MESSAGES"] = sent
    return flask_app


def _submit_access_request(client) -> None:
    form = client.get("/access-request?next=/de/research/spanish")
    token = re.search(r'name="access_request_form_token" value="([^"]*)"', form.get_data(as_text=True)).group(1)
    response = client.post(
        "/access-request",
        data={
            "first_name": "Mara",
            "last_name": "Fischer",
            "institution": "Universität Marburg",
            "role_or_function": "Mitarbeiterin",
            "email": f"mara.{uuid.uuid4().hex[:8]}@uni-marburg.de",
            "purpose": "Zugang für ein Seminar zur Ausspracheforschung.",
            "consent_confirmed": "1",
            "ui_lang": "de",
            "next": "/de/research/spanish",
            "website": "",
            "access_request_form_token": token,
        },
    )
    assert response.status_code == 303, response.get_data(as_text=True)


def _latest_status(database_url: str) -> str:
    with _connect(database_url) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT status FROM access_requests ORDER BY created_at DESC, id DESC LIMIT 1")
        return cursor.fetchone()[0]


def test_access_request_notification_status_is_persisted_in_postgres(pg_app, migrated_database_url: str) -> None:
    _submit_access_request(pg_app.test_client())

    assert len(pg_app.config["TEST_SENT_MESSAGES"]) == 1
    # The status written after a successful send used to violate the CHECK constraint and stay 'submitted'.
    assert _latest_status(migrated_database_url) == "notified"


def test_access_request_notification_failure_is_persisted_in_postgres(pg_app, migrated_database_url: str) -> None:
    def failing_sender(_message) -> None:
        raise RuntimeError("smtp down")

    pg_app.config["AUTH_ACCESS_REQUEST_MAIL_SENDER"] = failing_sender
    _submit_access_request(pg_app.test_client())

    assert _latest_status(migrated_database_url) == "notification_failed"


def test_access_request_with_broken_mail_configuration_is_saved_in_postgres_and_not_a_500(pg_app, migrated_database_url: str) -> None:
    pg_app.config.pop("AUTH_ACCESS_REQUEST_MAIL_SENDER", None)
    pg_app.config["AUTH_ACCESS_REQUEST_EMAIL"] = "__SET_OPERATOR_EMAIL__"
    _submit_access_request(pg_app.test_client())

    assert _latest_status(migrated_database_url) == "notification_failed"


def test_set_api_roundtrip_on_postgres(real_app_factory, migrated_database_url: str, fixture_runtime_root) -> None:
    flask_app = real_app_factory(env=PROD_MAIL_ENV, database_url=migrated_database_url, runtime_root=fixture_runtime_root)
    from datetime import datetime, timezone

    from app.auth import services as auth_services
    from app.auth.models import User
    from app.extensions.sqlalchemy_ext import get_session

    now = datetime.now(timezone.utc)
    email = f"pg{uuid.uuid4().hex[:6]}@example.org"
    with flask_app.app_context(), get_session() as session:
        session.add(
            User(
                id=f"pg-user-{uuid.uuid4().hex[:8]}",
                username=f"pguser{uuid.uuid4().hex[:6]}",
                email=email,
                password_hash=auth_services.hash_password("ValidPass1"),
                role="user",
                is_active=True,
                must_reset_password=False,
                created_at=now,
                updated_at=now,
                first_name="P",
                last_name="G",
                display_name="P G",
            )
        )

    client = flask_app.test_client()
    login = client.post("/auth/login", data={"email": email, "password": "ValidPass1"})
    assert login.status_code == 303

    created = client.post("/api/research/sets", json={"corpus_language": "spanish", "label": "Postgres-Set"})
    assert created.status_code == 201, created.get_data(as_text=True)
    set_id = created.get_json()["set"]["set_id"]
    assert client.put(f"/api/research/sets/{set_id}/items", json={"items": [{"task": "bogus", "item_id": "wl_059"}]}).status_code == 400
    ok = client.put(f"/api/research/sets/{set_id}/items", json={"items": [{"task": "wordlist", "item_id": "wl_059"}]})
    assert ok.status_code == 200
    assert client.get(f"/api/research/sets/{set_id}").get_json()["set"]["items"][0]["item_id"] == "wl_059"
