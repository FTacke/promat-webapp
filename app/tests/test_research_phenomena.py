from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from flask import Flask, g


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

from app import register_context_processors
from app.auth.models import Base, User
from app.extensions import register_extensions
from app.extensions.sqlalchemy_ext import get_engine, get_session, init_engine
from app.research_phenomena_views import (
    build_phenomena_overview_page,
    build_phenomena_preset_editor_page,
    build_phenomena_set_editor_page,
)
from app.research_presets import clear_research_preset_caches
from app.research_sessions import load_language_sessions, load_person_records
from app.research_sets import create_draft_set, update_set_metadata
from app.routes.auth import blueprint as auth_blueprint
from app.routes.research_api import blueprint as research_api_blueprint
from app.routes.public import blueprint as public_blueprint


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


def _session_payload(person_id: str, session_id: str, tasks: tuple[str, ...]) -> dict[str, object]:
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
        "tasks": [_task(task_type) for task_type in tasks],
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
                {"item_id": "d_01", "item_number": "D1", "group_id": "D", "text": "Hoy miro el reloj con calma antes de salir."},
                {"item_id": "qy_01", "item_number": "QY1", "group_id": "QY", "text": "¿El vaso está lleno de vino ahora?"},
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
                    "description": "Minimal preset for phenomena tests.",
                    "language": "spanish",
                    "items": [
                        {"task": "wordlist", "item_id": "wl_001"},
                        {"task": "text", "item_id": "d_01"},
                    ],
                }
            ],
        },
    )

    _write_session(runtime_root, "spanish", "ES-L-0001-2026-S01", _session_payload("ES-L-0001", "ES-L-0001-2026-S01", ("wordlist", "text")))
    _write_session(runtime_root, "spanish", "ES-L-0002-2026-S01", _session_payload("ES-L-0002", "ES-L-0002-2026-S01", ("wordlist",)))


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


@pytest.fixture
def phenomena_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Flask:
    runtime_root = tmp_path / "runtime"
    public_root = tmp_path / "public"
    runtime_root.mkdir(parents=True, exist_ok=True)
    public_root.mkdir(parents=True, exist_ok=True)
    _write_minimal_research_runtime(runtime_root)

    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(runtime_root))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(public_root))

    db_path = tmp_path / "auth.sqlite3"
    app_root = Path(__file__).resolve().parents[1]
    app = Flask(
        __name__,
        template_folder=str(app_root / "templates"),
        static_folder=str(app_root / "static"),
    )
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        SERVER_NAME="promat.test",
        JWT_SECRET_KEY="test-secret",
        JWT_TOKEN_LOCATION=["headers"],
        JWT_COOKIE_CSRF_PROTECT=False,
        AUTH_DATABASE_URL=f"sqlite:///{db_path.as_posix()}",
        RESEARCH_SET_DRAFT_TTL_DAYS=3,
    )

    register_context_processors(app)
    register_extensions(app)
    init_engine(app)
    with app.app_context():
        Base.metadata.create_all(bind=get_engine())
        _insert_user("user-1", "alice")

    @app.before_request
    def _set_test_auth_context() -> None:
        g.user = app.config.get("TEST_AUTH_USER")
        g.user_id = app.config.get("TEST_AUTH_USER_ID")
        g.role = None

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(research_api_blueprint)
    app.register_blueprint(public_blueprint)
    _clear_runtime_caches()
    yield app
    _clear_runtime_caches()


def test_build_phenomena_overview_page_merges_curated_and_custom_entries(phenomena_app: Flask) -> None:
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        update_set_metadata(owner_user_id="user-1", set_id=draft.set_id, label="Mein Fokusset", state="saved")
        hidden_draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        update_set_metadata(owner_user_id="user-1", set_id=hidden_draft.set_id, label="Nur Draft")

    with phenomena_app.test_request_context("/de/research/spanish/phenomena"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_phenomena_overview_page("de", "spanish")

    assert page is not None
    assert page["template"] == "pages/research_phenomena_overview.html"
    assert page["heading"] == "1 Set wählen"
    assert [item["label"] for item in page["content_header"]["breadcrumbs"]][:2] == ["Forschung", "Spanisch-Korpus"]
    assert page["content_header"]["intro"] == "Kuratierte Sets öffnen, bearbeiten oder ein neues Set mit ausgewählten Items aus Wortliste und Text anlegen."
    assert [entry["kind"] for entry in page["entries"]] == ["curated", "custom"]
    assert page["entries"][1]["title"] == "Mein Fokusset"
    assert page["client_state"]["labels"]["view"] == "Ansehen"
    assert page["client_state"]["labels"]["edit"] == "Bearbeiten"
    assert page["client_state"]["labels"]["modify"] == "Modifizieren"
    assert page["search_placeholder"] == "Set suchen"
    assert page["entries"][0]["preview"]
    assert all(entry["title"] != "Nur Draft" for entry in page["entries"])


def test_build_phenomena_preset_editor_page_exposes_curated_initial_record(phenomena_app: Flask) -> None:
    with phenomena_app.test_request_context("/de/research/spanish/phenomena/presets/starter_preset"):
        g.user = None
        g.user_id = None
        g.role = None
        page = build_phenomena_preset_editor_page("de", "spanish", "starter_preset")

    assert page is not None
    assert page["template"] == "pages/research_phenomena_editor.html"
    assert page["title"] == "Starter"
    assert page["content_header"]["title"] == "Starter"
    assert [item["label"] for item in page["content_header"]["breadcrumbs"]][:2] == ["Forschung", "Spanisch-Korpus"]
    assert page["content_header"]["intro"] == "Set bearbeiten"
    assert [item["label"] for item in page["content_header"]["breadcrumbs"]][-2:] == ["Phänomene", "Starter"]
    assert page["client_state"]["editorMode"] == "preset"
    assert page["client_state"]["initialRecord"]["state"] == "curated"
    assert page["client_state"]["initialRecord"]["label"] == "Starter"
    assert page["client_state"]["labels"]["selectedItems"] == "Ausgewählte Items"
    assert page["client_state"]["labels"]["curatedHint"] == "Änderungen an diesem kuratierten Set werden als neues eigenes Set gespeichert."
    assert page["client_state"]["labels"]["typeWordlist"] == "Wortliste"
    assert page["client_state"]["labels"]["unsavedStateText"] == "Änderungen noch nicht gespeichert."


def test_build_phenomena_set_editor_page_loads_owned_set(phenomena_app: Flask) -> None:
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish", source_preset_id="starter_preset")
        update_set_metadata(owner_user_id="user-1", set_id=draft.set_id, label="Mein Set", note="Merken", state="saved")

    with phenomena_app.test_request_context(f"/de/research/spanish/phenomena/sets/{draft.set_id}"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_phenomena_set_editor_page("de", "spanish", draft.set_id)

    assert page is not None
    assert page["title"] == "Mein Set"
    assert page["content_header"]["title"] == "Mein Set"
    assert [item["label"] for item in page["content_header"]["breadcrumbs"]][:2] == ["Forschung", "Spanisch-Korpus"]
    assert page["client_state"]["editorMode"] == "set"
    assert page["client_state"]["initialRecord"]["set_id"] == draft.set_id
    assert page["client_state"]["initialRecord"]["note"] == "Merken"


def test_phenomena_pages_expose_english_labels_for_migrated_surfaces(phenomena_app: Flask) -> None:
    with phenomena_app.test_request_context("/en/research/spanish/phenomena"):
        g.user = None
        g.user_id = None
        g.role = None
        overview_page = build_phenomena_overview_page("en", "spanish")

    with phenomena_app.test_request_context("/en/research/spanish/phenomena/presets/starter_preset"):
        g.user = None
        g.user_id = None
        g.role = None
        editor_page = build_phenomena_preset_editor_page("en", "spanish", "starter_preset")

    assert overview_page is not None
    assert overview_page["heading"] == "1 Choose a set"
    assert [item["label"] for item in overview_page["content_header"]["breadcrumbs"]][:2] == ["Research", "Spanish corpus"]
    assert overview_page["content_header"]["intro"] == "Open curated sets, edit them, or create a new set from selected word-list and sentence-list items."
    assert overview_page["search_placeholder"] == "Search sets"
    assert overview_page["client_state"]["labels"]["requestFailed"] == "Request failed."
    assert overview_page["client_state"]["labels"]["view"] == "View"

    assert editor_page is not None
    assert [item["label"] for item in editor_page["content_header"]["breadcrumbs"]][:2] == ["Research", "Spanish corpus"]
    assert editor_page["content_header"]["intro"] == "Edit set"
    assert editor_page["client_state"]["labels"]["selectedItems"] == "Selected items"
    assert editor_page["client_state"]["labels"]["curatedHint"] == "Changes to this curated set are saved as a new custom set."
    assert editor_page["client_state"]["labels"]["untitled"] == "Untitled"


def test_public_phenomena_overview_route_redirects_to_login_without_auth(phenomena_app: Flask) -> None:
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login?next=/de/research/spanish/phenomena"


def test_public_phenomena_overview_route_renders_split_overview(phenomena_app: Flask) -> None:
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Set wählen" in html
    assert "Spanisch-Korpus" in html
    assert "Set suchen" in html
    assert "Neues Set" in html
    assert "Ansehen" in html
    assert "Öffnen" not in html
    assert "pm-phenomena-overview-card__preview" not in html
    assert "research-phenomena-overview.js" in html
    assert "Material-Presets" not in html


def test_public_phenomena_overview_route_renders_edit_action_for_owned_custom_sets(phenomena_app: Flask) -> None:
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        update_set_metadata(owner_user_id="user-1", set_id=draft.set_id, label="Mein Set", state="saved")

    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Bearbeiten" in html
    assert "Modifizieren" in html
    assert "Öffnen" not in html


def test_public_preset_editor_route_redirects_to_login_without_auth(phenomena_app: Flask) -> None:
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena/presets/starter_preset")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login?next=/de/research/spanish/phenomena/presets/starter_preset"


def test_public_preset_editor_route_renders_editor_page(phenomena_app: Flask) -> None:
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena/presets/starter_preset")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "research-phenomena-editor.js" in html
    assert "Spanisch-Korpus" in html
    assert "Ausgewählte Items" in html
    assert "Zum Speichern bitte anmelden" not in html
    assert "data-phenomena-state-badge" in html
    assert "data-phenomena-editor-root" in html


def test_public_set_editor_route_redirects_to_login_without_auth(phenomena_app: Flask) -> None:
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")

    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/sets/{draft.set_id}")

    assert response.status_code == 302
    assert response.headers["Location"] == f"/login?next=/de/research/spanish/phenomena/sets/{draft.set_id}"


def test_public_set_editor_route_renders_for_authenticated_owner(phenomena_app: Flask) -> None:
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")

    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/sets/{draft.set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "data-phenomena-editor-root" in html
    assert "Spanisch-Korpus" in html
    assert "pm-phenomena-editor-state" in html