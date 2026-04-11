from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from flask import Flask
from flask_jwt_extended import create_access_token


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

from app.auth.models import Base, User  # noqa: E402
from app.extensions import register_extensions  # noqa: E402
from app.extensions.sqlalchemy_ext import get_engine, init_engine, get_session  # noqa: E402
from app.research_presets import clear_research_preset_caches  # noqa: E402
from app.research_sessions import load_language_sessions, load_person_records  # noqa: E402
from app.research_sets import (  # noqa: E402
    ResearchSet,
    ResearchSetStorageUnavailableError,
    ResearchSetValidationError,
    create_draft_set,
    delete_owned_set,
    delete_expired_drafts,
    list_owned_sets,
    load_owned_set,
    update_set_metadata,
)
from app.routes.research_api import blueprint as research_api_blueprint  # noqa: E402


def _clear_runtime_caches() -> None:
    clear_research_preset_caches()
    load_language_sessions.cache_clear()
    load_person_records.cache_clear()


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_session(runtime_root: Path, language_slug: str, session_id: str, payload: dict[str, object]) -> None:
    session_dir = runtime_root / "data" / "sessions" / language_slug / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "metadata.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _task(task_type: str) -> dict[str, str]:
    return {
        "task_type": task_type,
        "label": task_type,
        "source_file": f"source/{task_type}.wav",
        "alignment_file": f"alignment/{task_type}.TextGrid",
    }


def _session_payload(person_id: str, session_id: str) -> dict[str, object]:
    return {
        "person_id": person_id,
        "session_id": session_id,
        "target_language": "es",
        "speaker_type": "learner",
        "l1": "DE",
        "gender": "female",
        "birth_year": 1998,
        "level_code": "B1",
        "level_self": "B1",
        "recording_year": 2026,
        "recording_date": "2026-03-10",
        "context": "baseline",
        "recorded_by": "Ana Romero",
        "notes": "test learner session",
        "tasks": [_task("wordlist"), _task("text")],
    }


def _write_minimal_research_runtime(runtime_root: Path) -> None:
    base_dir = runtime_root / "data" / "config" / "research_player" / "spanish"
    _write_json(
        base_dir / "task_catalogs" / "wordlist.json",
        {
            "task": "wordlist",
            "language": "spanish",
            "items": [
                {"item_id": "wl_001", "item_number": "1", "text": "mesa"},
                {"item_id": "wl_002", "item_number": "2", "text": "reloj"},
            ],
        },
    )
    _write_json(
        base_dir / "task_catalogs" / "text.json",
        {
            "task": "text",
            "language": "spanish",
            "display_label": "Satzliste",
            "items": [
                {"item_id": "d_01", "item_number": "D1", "text": "Hoy miro el reloj con calma antes de salir."},
                {"item_id": "qy_01", "item_number": "QY1", "text": "¿El vaso está lleno de vino ahora?"},
            ],
        },
    )
    _write_json(
        base_dir / "player_config.json",
        {
            "language": "spanish",
            "text": {"default_render_mode": "sentence_list", "display_label": "Satzliste"},
        },
    )
    _write_json(
        base_dir / "phenomena_presets.json",
        {
            "language": "spanish",
            "presets": [
                {
                    "preset_id": "starter_preset",
                    "label": "Starter",
                    "description": "Minimal preset for tests.",
                    "language": "spanish",
                    "items": [
                        {"task": "wordlist", "item_id": "wl_001"},
                        {"task": "text", "item_id": "d_01", "segment_id": "rise", "note": "focus"},
                    ],
                }
            ],
        },
    )

    _write_session(runtime_root, "spanish", "ES-L-0001-2026-S01", _session_payload("ES-L-0001", "ES-L-0001-2026-S01"))
    _write_session(runtime_root, "spanish", "ES-L-0002-2026-S01", _session_payload("ES-L-0002", "ES-L-0002-2026-S01"))


def _insert_user(user_id: str, username: str) -> None:
    now = datetime.now(timezone.utc)
    with get_session() as session:
        session.add(
            User(
                id=user_id,
                username=username,
                email=f"{username}@example.org",
                password_hash="not-used-in-tests",
                role="user",
                is_active=True,
                must_reset_password=False,
                created_at=now,
                updated_at=now,
            )
        )


def _auth_header(app: Flask, user_id: str, username: str) -> dict[str, str]:
    with app.app_context():
        token = create_access_token(
            identity=user_id,
            additional_claims={"username": username, "role": "user", "must_reset_password": False},
        )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def set_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Flask:
    runtime_root = tmp_path / "runtime"
    public_root = tmp_path / "public"
    runtime_root.mkdir(parents=True, exist_ok=True)
    public_root.mkdir(parents=True, exist_ok=True)
    _write_minimal_research_runtime(runtime_root)

    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(runtime_root))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(public_root))

    db_path = tmp_path / "auth.sqlite3"
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        JWT_SECRET_KEY="test-secret",
        JWT_TOKEN_LOCATION=["headers"],
        JWT_COOKIE_CSRF_PROTECT=False,
        AUTH_DATABASE_URL=f"sqlite:///{db_path.as_posix()}",
        RESEARCH_SET_DRAFT_TTL_DAYS=3,
    )

    register_extensions(app)
    init_engine(app)
    with app.app_context():
        Base.metadata.create_all(bind=get_engine())
        _insert_user("user-1", "alice")
        _insert_user("user-2", "bob")

    app.register_blueprint(research_api_blueprint)
    _clear_runtime_caches()
    yield app
    _clear_runtime_caches()


def test_research_set_migration_declares_expected_tables() -> None:
    migration_path = TEST_REPO_ROOT / "app" / "migrations" / "0003_create_research_sets.sql"
    content = migration_path.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS research_sets" in content
    assert "CREATE TABLE IF NOT EXISTS research_set_items" in content
    assert "CREATE TABLE IF NOT EXISTS research_set_sessions" in content
    assert "REFERENCES users(user_id) ON DELETE CASCADE" in content
    assert "state IN ('draft', 'saved')" in content

    extension_migration = (TEST_REPO_ROOT / "app" / "migrations" / "0004_extend_research_sets_for_phenomena_editor.sql").read_text(
        encoding="utf-8"
    )
    assert "ADD COLUMN IF NOT EXISTS note TEXT NULL" in extension_migration


def test_apply_auth_migration_discovers_full_postgres_chain() -> None:
    script_path = TEST_REPO_ROOT / "app" / "scripts" / "apply_auth_migration.py"
    spec = importlib.util.spec_from_file_location("apply_auth_migration", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    migration_names = [path.name for path in module._postgres_migration_files()]

    assert migration_names == sorted(migration_names)
    assert migration_names[0] == "0001_create_auth_schema_postgres.sql"
    assert "0001_create_auth_schema_sqlite.sql" not in migration_names
    assert "0004_extend_research_sets_for_phenomena_editor.sql" in migration_names


def test_create_empty_draft_set_service(set_app: Flask) -> None:
    with set_app.app_context():
        record = create_draft_set(owner_user_id="user-1", corpus_language="spanish")

    assert record.state == "draft"
    assert record.corpus_language == "spanish"
    assert record.label == "Neues Set 1"
    assert record.items == tuple()
    assert record.sessions == tuple()
    assert record.expires_at is not None


def test_create_draft_from_valid_preset_materializes_items(set_app: Flask) -> None:
    client = set_app.test_client()
    response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish", "preset_id": "starter_preset", "preferred_task": "text"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["set"]["source_preset_id"] == "starter_preset"
    assert payload["set"]["preferred_task"] == "text"
    assert payload["set"]["label"] == "Starter (modifiziert)"
    assert [item["task"] for item in payload["set"]["items"]] == ["wordlist", "text"]
    assert payload["set"]["items"][1]["segment_id"] == "rise"


def test_create_draft_rejects_invalid_preset_id(set_app: Flask) -> None:
    client = set_app.test_client()
    response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish", "preset_id": "missing_preset"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert response.status_code == 400
    assert "Unknown preset_id" in response.get_json()["error"]


def test_replace_items_rejects_invalid_task_item(set_app: Flask) -> None:
    client = set_app.test_client()
    create_response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )
    set_id = create_response.get_json()["set"]["set_id"]

    response = client.put(
        f"/api/research/sets/{set_id}/items",
        json={"items": [{"task": "wordlist", "item_id": "wl_999"}]},
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert response.status_code == 400
    assert "Unknown item_id 'wl_999'" in response.get_json()["error"]


def test_replace_sessions_rejects_invalid_session_id(set_app: Flask) -> None:
    client = set_app.test_client()
    create_response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )
    set_id = create_response.get_json()["set"]["set_id"]

    response = client.put(
        f"/api/research/sets/{set_id}/sessions",
        json={"sessions": [{"session_id": "ES-L-9999-2026-S01"}]},
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert response.status_code == 400
    assert "Unknown session_id 'ES-L-9999-2026-S01'" in response.get_json()["error"]


def test_save_as_new_set_creates_saved_copy(set_app: Flask) -> None:
    client = set_app.test_client()
    create_response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish", "preset_id": "starter_preset"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )
    draft_payload = create_response.get_json()["set"]
    draft_id = draft_payload["set_id"]

    save_response = client.post(
        f"/api/research/sets/{draft_id}/save-as",
        json={"label": "Mein Set"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert save_response.status_code == 201
    saved_payload = save_response.get_json()["set"]
    assert saved_payload["set_id"] != draft_id
    assert saved_payload["state"] == "saved"
    assert saved_payload["label"] == "Mein Set"
    assert saved_payload["suggested_save_label"] == "Mein Set"
    assert saved_payload["expires_at"] is None
    assert saved_payload["items"] == draft_payload["items"]


def test_preset_derived_draft_exposes_suggested_save_label(set_app: Flask) -> None:
    client = set_app.test_client()
    create_response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish", "preset_id": "starter_preset"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert create_response.status_code == 201
    payload = create_response.get_json()["set"]
    assert payload["state"] == "draft"
    assert payload["suggested_save_label"] == "Starter (modifiziert)"


def test_patch_set_can_store_note_and_promote_to_saved(set_app: Flask) -> None:
    client = set_app.test_client()
    create_response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish", "note": "Arbeitsnotiz"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )
    set_id = create_response.get_json()["set"]["set_id"]

    patch_response = client.patch(
        f"/api/research/sets/{set_id}",
        json={"label": "Mein Fokusset", "note": "Gespeichert", "state": "saved"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert patch_response.status_code == 200
    payload = patch_response.get_json()["set"]
    assert payload["state"] == "saved"
    assert payload["label"] == "Mein Fokusset"
    assert payload["note"] == "Gespeichert"
    assert payload["expires_at"] is None


def test_list_sets_endpoint_returns_only_saved_sets_by_default(set_app: Flask) -> None:
    with set_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        update_set_metadata(owner_user_id="user-1", set_id=draft.set_id, state="saved", label="Freies Set")
        create_draft_set(owner_user_id="user-1", corpus_language="spanish", label="Nur Draft")

    client = set_app.test_client()
    response = client.get(
        "/api/research/sets?corpus_language=spanish",
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert [entry["label"] for entry in payload["sets"]] == ["Freies Set"]


def test_delete_set_endpoint_removes_owned_set(set_app: Flask) -> None:
    client = set_app.test_client()
    create_response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish", "label": "Löschbar"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )
    set_id = create_response.get_json()["set"]["set_id"]

    delete_response = client.delete(
        f"/api/research/sets/{set_id}",
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert delete_response.status_code == 200
    follow_up = client.get(
        f"/api/research/sets/{set_id}",
        headers=_auth_header(set_app, "user-1", "alice"),
    )
    assert follow_up.status_code == 404


def test_save_as_new_set_rejects_empty_label(set_app: Flask) -> None:
    client = set_app.test_client()
    create_response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish", "preset_id": "starter_preset"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )
    draft_id = create_response.get_json()["set"]["set_id"]

    save_response = client.post(
        f"/api/research/sets/{draft_id}/save-as",
        json={"label": "   "},
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert save_response.status_code == 400
    assert "non-empty label" in save_response.get_json()["error"]


def test_create_set_returns_controlled_503_when_storage_is_unavailable(
    set_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_storage_error(**_kwargs):
        raise ResearchSetStorageUnavailableError("Research-set storage is unavailable.")

    monkeypatch.setattr("app.routes.research_api.create_draft_set", raise_storage_error)

    client = set_app.test_client()
    response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )

    assert response.status_code == 503
    assert "Research-set storage is unavailable" in response.get_json()["error"]


def test_foreign_owned_set_is_not_readable_or_mutable(set_app: Flask) -> None:
    client = set_app.test_client()
    create_response = client.post(
        "/api/research/sets",
        json={"corpus_language": "spanish", "preset_id": "starter_preset"},
        headers=_auth_header(set_app, "user-1", "alice"),
    )
    set_id = create_response.get_json()["set"]["set_id"]

    get_response = client.get(f"/api/research/sets/{set_id}", headers=_auth_header(set_app, "user-2", "bob"))
    patch_response = client.patch(
        f"/api/research/sets/{set_id}",
        json={"label": "Fremdes Set"},
        headers=_auth_header(set_app, "user-2", "bob"),
    )

    assert get_response.status_code == 404
    assert patch_response.status_code == 404


def test_loading_set_updates_access_and_extends_draft_expiry(set_app: Flask) -> None:
    with set_app.app_context():
        record = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        first_access = record.last_accessed_at
        first_expiry = record.expires_at

        with get_session() as session:
            db_record = session.get(ResearchSet, record.set_id)
            db_record.last_accessed_at = first_access - timedelta(days=1)
            db_record.expires_at = first_expiry - timedelta(days=1)

        loaded = load_owned_set(owner_user_id="user-1", set_id=record.set_id, touch_access=True)

    assert loaded.last_accessed_at > first_access - timedelta(hours=12)
    assert loaded.expires_at > first_expiry - timedelta(hours=12)


def test_cleanup_removes_expired_drafts(set_app: Flask) -> None:
    with set_app.app_context():
        record = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        with get_session() as session:
            db_record = session.get(ResearchSet, record.set_id)
            db_record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)

        deleted = delete_expired_drafts()

        assert deleted == 1
        with pytest.raises(ResearchSetValidationError, match="set_id"):
            load_owned_set(owner_user_id="user-1", set_id="")

        client = set_app.test_client()
        response = client.get(f"/api/research/sets/{record.set_id}", headers=_auth_header(set_app, "user-1", "alice"))
        assert response.status_code == 404


def test_list_and_delete_helpers_work_for_owned_sets(set_app: Flask) -> None:
    with set_app.app_context():
        first = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        second = create_draft_set(owner_user_id="user-1", corpus_language="spanish", source_preset_id="starter_preset")
        update_set_metadata(owner_user_id="user-1", set_id=first.set_id, state="saved", label="A")
        update_set_metadata(owner_user_id="user-1", set_id=second.set_id, state="saved", label="B")

        listed = list_owned_sets(owner_user_id="user-1", corpus_language="spanish")
        assert {entry.label for entry in listed} == {"A", "B"}

        delete_owned_set(owner_user_id="user-1", set_id=first.set_id)
        listed_after_delete = list_owned_sets(owner_user_id="user-1", corpus_language="spanish")
        assert [entry.label for entry in listed_after_delete] == ["B"]