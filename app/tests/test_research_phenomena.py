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
from app.extensions.sqlalchemy_ext import get_engine, init_engine, get_session
from app.research_presets import clear_research_preset_caches
from app.research_sessions import load_language_sessions, load_person_records
from app.research_sets import create_draft_set
from app.research_views import build_phenomena_page
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
        g.role = None

    app.register_blueprint(public_blueprint)
    _clear_runtime_caches()
    yield app
    _clear_runtime_caches()


def test_build_phenomena_page_exposes_file_backed_presets_and_catalogs(phenomena_app: Flask) -> None:
    with phenomena_app.test_request_context("/de/research/spanish/phenomena"):
        g.user = None
        g.role = None
        page = build_phenomena_page("de", "spanish", {})

    assert page is not None
    assert page["template"] == "pages/research_phenomena.html"
    assert page["preset_cards"][0]["preset_id"] == "starter_preset"
    assert page["client_state"]["taskLabels"]["text"] == "Satzliste"
    assert page["client_state"]["catalogsByTask"]["wordlist"][0]["item_id"] == "wl_001"
    assert page["client_state"]["sessionsByTask"]["text"][0]["session_id"] == "ES-L-0001-2026-S01"


def test_build_phenomena_page_marks_requested_preset_for_authenticated_flow(phenomena_app: Flask) -> None:
    with phenomena_app.test_request_context("/de/research/spanish/phenomena?preset_id=starter_preset"):
        g.user = "alice"
        g.role = None
        page = build_phenomena_page("de", "spanish", {"preset_id": "starter_preset"})

    assert page is not None
    assert page["is_authenticated"] is True
    assert page["workspace"]["mode"] == "open-preset"
    assert page["workspace"]["save_label"] == "Als neues Set speichern"
    assert page["client_state"]["requestedPresetId"] == "starter_preset"
    assert page["client_state"]["labels"]["saveAsLabel"] == "Als neues Set speichern"
    assert page["client_state"]["labels"]["stateDraft"] == "Draft"
    assert page["client_state"]["labels"]["stateSaved"] == "Gespeichert"


def test_build_phenomena_page_exposes_requested_set_id_for_client_loading(phenomena_app: Flask) -> None:
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish", source_preset_id="starter_preset")

    with phenomena_app.test_request_context(f"/de/research/spanish/phenomena?set_id={draft.set_id}"):
        g.user = "alice"
        g.role = None
        page = build_phenomena_page("de", "spanish", {"set_id": draft.set_id})

    assert page is not None
    assert page["workspace"]["mode"] == "load-set"
    assert page["client_state"]["requestedSetId"] == draft.set_id


def test_public_phenomena_route_renders_dedicated_workspace(phenomena_app: Flask) -> None:
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena?preset_id=starter_preset")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Material-Presets" in html
    assert "pm-phenomena-state" in html
    assert "data-phenomena-save-dialog" in html
    assert "data-phenomena-status-meta" in html
    assert "heuristisch" not in html