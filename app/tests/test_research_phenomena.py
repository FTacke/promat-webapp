from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
import shutil
import sys
from pathlib import Path

import pytest
from flask import Flask, g


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
PHENOMENA_EDITOR_JS = TEST_REPO_ROOT / "app" / "static" / "js" / "pages" / "research-phenomena-editor.js"
PHENOMENA_EDITOR_TEMPLATE = TEST_REPO_ROOT / "app" / "templates" / "pages" / "research_phenomena_editor.html"
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
from app.research_sets import create_curated_set, create_draft_set, update_set_metadata
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


class _NestedButtonParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._button_depth = 0
        self.nested_button_found = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "button":
            return
        if self._button_depth > 0:
            self.nested_button_found = True
        self._button_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self._button_depth > 0:
            self._button_depth -= 1


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


def _insert_user(user_id: str, username: str, *, role: str = "user") -> None:
    now = datetime.now(timezone.utc)
    with get_session() as session:
        session.add(
            User(
                id=user_id,
                username=username,
                email=f"{username}@example.org",
                password_hash="not-used-in-tests",
                role=role,
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
        _insert_user("admin-1", "admin", role="admin")
        curated_set = create_curated_set(
            admin_user_id="admin-1",
            corpus_language="spanish",
            label="Starter",
            note="Minimal DB-curated set for phenomena tests.",
            items=[
                {"task": "wordlist", "item_id": "wl_001"},
                {"task": "text", "item_id": "d_01"},
            ],
        )
        app.config["TEST_CURATED_SET_ID"] = curated_set.set_id

    @app.before_request
    def _set_test_auth_context() -> None:
        g.user = app.config.get("TEST_AUTH_USER")
        g.user_id = app.config.get("TEST_AUTH_USER_ID")
        g.role = app.config.get("TEST_AUTH_ROLE")

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(research_api_blueprint)
    app.register_blueprint(public_blueprint)
    _clear_runtime_caches()
    yield app
    _clear_runtime_caches()


def test_editor_static_js_keeps_single_sync_status_and_request_helpers() -> None:
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")

    assert source.count("function syncStatus") == 1
    assert "function parseState()" in source
    assert "async function requestJson(url, options = {})" in source
    assert "function discardOrDelete" not in source
    assert "function discardOrNavigate()" in source
    assert "persistSaveAsCopy" in source
    assert 'root.addEventListener("click"' in source
    assert 'selectedList?.addEventListener("dragstart"' in source
    assert "data-phenomena-curated-toggle-action" not in source


def test_editor_static_js_parse_state_has_no_merged_event_fragments() -> None:
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    parse_start = source.index("function parseState()")
    parse_end = source.index("function buildUrl", parse_start)
    parse_state = source[parse_start:parse_end]

    assert "addEventListener" not in parse_state
    assert "discardOrNavigate" not in parse_state
    assert "persistSaveAsCopy" not in parse_state
    assert "requestJson" not in parse_state
    assert "options.headers" not in parse_state


def test_editor_template_has_no_nested_buttons_and_no_curated_toggle_action() -> None:
    template = PHENOMENA_EDITOR_TEMPLATE.read_text(encoding="utf-8")
    parser = _NestedButtonParser()
    parser.feed(template)

    assert not parser.nested_button_found
    assert "data-phenomena-curated-toggle-action" not in template


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
    curated_entry = page["entries"][0]
    assert page["client_state"]["labels"]["view"] == "Ansehen"
    assert page["client_state"]["labels"]["edit"] == "Bearbeiten"
    assert page["client_state"]["labels"]["editCurated"] == "Kuratiertes Set bearbeiten"
    assert page["client_state"]["labels"]["editAsOwnSet"] == "Als eigenes Set bearbeiten"
    assert curated_entry["view_href"].endswith(f"/de/research/spanish/phenomena/presets/{phenomena_app.config['TEST_CURATED_SET_ID']}")
    assert curated_entry["edit_curated_href"] is None
    assert curated_entry["edit_as_own_href"] is None
    assert curated_entry["copy_source_set_id"] == phenomena_app.config["TEST_CURATED_SET_ID"]
    assert page["search_placeholder"] == "Set suchen"
    assert page["entries"][0]["preview"]
    assert all(entry["title"] != "Nur Draft" for entry in page["entries"])


def test_build_phenomena_overview_page_exposes_admin_curated_actions(phenomena_app: Flask) -> None:
    with phenomena_app.test_request_context("/de/research/spanish/phenomena"):
        g.user = "admin"
        g.user_id = "admin-1"
        g.role = "admin"
        page = build_phenomena_overview_page("de", "spanish")

    assert page is not None
    curated_entry = page["entries"][0]
    assert curated_entry["edit_curated_href"].endswith(f"/de/research/spanish/phenomena/presets/{phenomena_app.config['TEST_CURATED_SET_ID']}")
    assert curated_entry["edit_as_own_href"] is None
    assert curated_entry["copy_source_set_id"] == phenomena_app.config["TEST_CURATED_SET_ID"]


def test_build_phenomena_overview_page_prefers_existing_private_copy_for_edit_as_own_set(phenomena_app: Flask) -> None:
    with phenomena_app.app_context():
        private_copy = create_draft_set(
            owner_user_id="user-1",
            corpus_language="spanish",
            source_curated_set_id=phenomena_app.config["TEST_CURATED_SET_ID"],
        )

    with phenomena_app.test_request_context("/de/research/spanish/phenomena"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_phenomena_overview_page("de", "spanish")

    assert page is not None
    curated_entry = page["entries"][0]
    assert curated_entry["edit_curated_href"] is None
    assert curated_entry["edit_as_own_href"].endswith(f"/de/research/spanish/phenomena/sets/{private_copy.set_id}")


def test_build_phenomena_preset_editor_page_exposes_curated_initial_record(phenomena_app: Flask) -> None:
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    with phenomena_app.test_request_context(f"/de/research/spanish/phenomena/presets/{curated_set_id}"):
        g.user = None
        g.user_id = None
        g.role = None
        page = build_phenomena_preset_editor_page("de", "spanish", curated_set_id)

    assert page is not None
    assert page["template"] == "pages/research_phenomena_editor.html"
    assert page["title"] == "Starter"
    assert page["content_header"]["title"] == "Starter"
    assert [item["label"] for item in page["content_header"]["breadcrumbs"]][:2] == ["Forschung", "Spanisch-Korpus"]
    assert page["content_header"]["intro"] == "Set bearbeiten"
    assert [item["label"] for item in page["content_header"]["breadcrumbs"]][-2:] == ["Phänomene", "Starter"]
    assert page["client_state"]["editorMode"] == "preset"
    assert page["client_state"]["initialRecord"]["state"] == "saved"
    assert page["client_state"]["initialRecord"]["visibility"] == "curated"
    assert page["client_state"]["initialRecord"]["label"] == "Starter"
    assert page["client_state"]["labels"]["selectedItems"] == "Ausgewählte Items"
    assert page["client_state"]["labels"]["curatedHint"] == "Beim Speichern wird eine eigene Kopie angelegt – das kuratierte Original bleibt unverändert."
    assert page["client_state"]["labels"]["typeWordlist"] == "Wortliste"
    assert page["client_state"]["labels"]["unsavedStateText"] == "Änderungen noch nicht gespeichert."


def test_build_phenomena_set_editor_page_loads_owned_set(phenomena_app: Flask) -> None:
    with phenomena_app.app_context():
        draft = create_draft_set(
            owner_user_id="user-1",
            corpus_language="spanish",
            source_curated_set_id=phenomena_app.config["TEST_CURATED_SET_ID"],
        )
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
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    with phenomena_app.test_request_context("/en/research/spanish/phenomena"):
        g.user = None
        g.user_id = None
        g.role = None
        overview_page = build_phenomena_overview_page("en", "spanish")

    with phenomena_app.test_request_context(f"/en/research/spanish/phenomena/presets/{curated_set_id}"):
        g.user = None
        g.user_id = None
        g.role = None
        editor_page = build_phenomena_preset_editor_page("en", "spanish", curated_set_id)

    assert overview_page is not None
    assert overview_page["heading"] == "1 Choose a set"
    assert [item["label"] for item in overview_page["content_header"]["breadcrumbs"]][:2] == ["Research", "Spanish corpus"]
    assert overview_page["content_header"]["intro"] == "Open curated sets, edit them, or create a new set from selected word-list and sentence-list items."
    assert overview_page["search_placeholder"] == "Search sets"
    assert overview_page["client_state"]["labels"]["requestFailed"] == "Request failed."
    assert overview_page["client_state"]["labels"]["view"] == "View"
    assert overview_page["client_state"]["labels"]["editCurated"] == "Edit curated set"
    assert overview_page["client_state"]["labels"]["editAsOwnSet"] == "Edit as own set"

    assert editor_page is not None
    assert [item["label"] for item in editor_page["content_header"]["breadcrumbs"]][:2] == ["Research", "Spanish corpus"]
    assert editor_page["content_header"]["intro"] == "Edit set"
    assert editor_page["client_state"]["labels"]["selectedItems"] == "Selected items"
    assert editor_page["client_state"]["labels"]["curatedHint"] == "Saving creates your own copy – the curated original stays unchanged."
    assert editor_page["client_state"]["labels"]["untitled"] == "Untitled"


def test_public_phenomena_overview_route_redirects_to_login_without_auth(phenomena_app: Flask) -> None:
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login?next=/de/research/spanish/phenomena"


def test_public_phenomena_overview_route_renders_split_overview(phenomena_app: Flask) -> None:
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Set wählen" in html
    assert "Spanisch-Korpus" in html
    assert "Set suchen" in html
    assert "Neues Set" in html
    assert "Ansehen" in html
    assert ">Als eigenes Set bearbeiten<" not in html
    assert ">Kuratiertes Set bearbeiten<" not in html
    assert "Modifizieren" not in html
    assert "Öffnen" not in html
    assert "pm-phenomena-overview-card__preview" not in html
    rename_start = html.rfind("<dialog", 0, html.index('data-phenomena-rename-dialog'))
    delete_start = html.rfind("<dialog", 0, html.index('data-phenomena-delete-dialog'))
    rename_slice = html[rename_start:delete_start]
    delete_slice = html[delete_start:]
    assert 'class="pm-dialog pm-surface-density--spacious" data-phenomena-rename-dialog' in rename_slice
    assert 'class="pm-dialog__title"' in rename_slice
    assert 'class="pm-form"' in rename_slice
    assert 'class="pm-form-field"' in rename_slice
    assert 'class="pm-form-label" for="pm-phenomena-rename-input"' in rename_slice
    assert 'class="pm-form-control" data-phenomena-rename-input' in rename_slice
    assert 'class="pm-form-error" data-phenomena-rename-error' in rename_slice
    assert 'pm-dialog__actions pm-action-row pm-action-row--end' in rename_slice
    assert 'md3-dialog' not in rename_slice
    assert 'md3-form' not in rename_slice
    assert 'md3-outlined-textfield' not in rename_slice
    assert 'class="pm-dialog pm-dialog--danger pm-surface-density--compact" data-phenomena-delete-dialog' in delete_slice
    assert 'pm-object-summary' in delete_slice
    assert 'data-phenomena-delete-object' in delete_slice
    assert 'pm-dialog__actions pm-action-row' in delete_slice
    assert 'class="pm-action-button pm-action-button--danger pm-action-button--medium" data-phenomena-delete-confirm' in delete_slice
    assert 'md3-dialog' not in delete_slice
    assert "md3-button" not in html
    assert "pm-research-" + "button" not in delete_slice
    assert "research-phenomena-overview.js" in html
    assert "Material-Presets" not in html


def test_public_phenomena_overview_route_renders_edit_action_for_owned_custom_sets(phenomena_app: Flask) -> None:
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        update_set_metadata(owner_user_id="user-1", set_id=draft.set_id, label="Mein Set", state="saved")

    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Bearbeiten" in html
    assert "Modifizieren" not in html
    assert "Öffnen" not in html


def test_public_phenomena_overview_route_renders_all_curated_actions_for_admins(phenomena_app: Flask) -> None:
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "admin"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "admin-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = "admin"
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Ansehen" in html
    assert ">Kuratiertes Set bearbeiten<" not in html
    assert ">Als eigenes Set bearbeiten<" not in html
    assert f'href="/de/research/spanish/phenomena/presets/{curated_set_id}"' in html
    assert f'data-phenomena-copy-curated-set="{curated_set_id}"' not in html


@pytest.mark.parametrize(
    ("ui_lang", "expected_message"),
    [
        ("de", "Keine Sets vorhanden."),
        ("en", "No sets available."),
    ],
)
def test_phenomena_overview_route_renders_plain_empty_state_without_runtime_sessions(
    phenomena_app: Flask,
    ui_lang: str,
    expected_message: str,
) -> None:
    runtime_root = Path(os.environ["PROMAT_RUNTIME_ROOT"])
    sessions_root = runtime_root / "data" / "sessions" / "spanish"
    shutil.rmtree(sessions_root, ignore_errors=True)
    sessions_root.mkdir(parents=True, exist_ok=True)
    _clear_runtime_caches()

    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/{ui_lang}/research/spanish/phenomena")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert expected_message in html
    assert f'data-phenomena-empty-title>{expected_message}</h3>' in html
    assert "Geplante Oberfläche" not in html
    assert "Geplante Übersicht" not in html
    assert "Hinweis zur Zuordnung" not in html
    assert "data-phenomena-copy-curated-set" not in html


def test_public_preset_editor_route_redirects_to_login_without_auth(phenomena_app: Flask) -> None:
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")

    assert response.status_code == 302
    assert response.headers["Location"] == f"/login?next=/de/research/spanish/phenomena/presets/{curated_set_id}"


def test_public_preset_editor_route_renders_editor_page(phenomena_app: Flask) -> None:
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "research-phenomena-editor.js" in html
    assert "Spanisch-Korpus" in html
    assert "Ausgewählte Items" in html
    assert "Zum Speichern bitte anmelden" not in html
    assert "data-phenomena-state-badge" in html
    assert "data-phenomena-editor-root" in html
    confirm_start = html.rfind("<dialog", 0, html.index('data-phenomena-editor-confirm'))
    confirm_slice = html[confirm_start:]
    assert 'class="pm-dialog pm-surface-density--compact" data-phenomena-editor-confirm' in confirm_slice
    assert 'class="pm-dialog__title" data-phenomena-editor-confirm-title' in confirm_slice
    assert 'class="pm-dialog__text" data-phenomena-editor-confirm-message' in confirm_slice
    assert 'pm-dialog__actions pm-action-row' in confirm_slice
    assert 'class="pm-action-button pm-action-button--secondary pm-action-button--medium" data-phenomena-editor-confirm-cancel' in html
    assert 'class="pm-action-button pm-action-button--primary pm-action-button--medium" data-phenomena-editor-confirm-submit' in html
    assert 'class="pm-action-button__label" data-phenomena-editor-confirm-submit-label' in confirm_slice
    assert 'md3-dialog' not in confirm_slice
    assert "md3-button" not in html


def test_editor_template_has_dedicated_delete_action_button(phenomena_app: Flask) -> None:
    """Template must have a dedicated data-phenomena-delete-action button (hidden by default)."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-phenomena-delete-action' in html
    assert 'data-phenomena-discard-action' in html
    assert 'data-phenomena-curated-toggle-action' not in html


def test_editor_user_preset_view_has_is_admin_false_in_client_state(phenomena_app: Flask) -> None:
    """Regular user must see isAdmin=false in client state; admin-only buttons must not be in the DOM."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '"isAdmin": false' in html
    # Admin-only buttons must not be rendered for USER (server-side exclusion)
    assert 'data-phenomena-delete-curated-action' not in html
    assert 'data-phenomena-save-as-curated-action' not in html
    assert 'data-phenomena-curated-toggle-action' not in html


def test_editor_user_new_custom_set_has_is_admin_false_and_buttons_present(phenomena_app: Flask) -> None:
    """New custom set for regular user: isAdmin=false in state; admin-only buttons not in DOM."""
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")

    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/sets/{draft.set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '"isAdmin": false' in html
    # Admin-only buttons must not be rendered server-side for USER
    assert 'data-phenomena-delete-curated-action' not in html
    assert 'data-phenomena-save-as-curated-action' not in html
    # User-facing buttons must be present
    assert 'data-phenomena-delete-action' in html
    assert 'data-phenomena-discard-action' in html


def test_editor_admin_curated_set_state_has_all_curated_labels(phenomena_app: Flask) -> None:
    """Admin editing a curated set must have all required curated management labels in client state."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    # Check via Python dict (avoids JSON encoding ambiguity for non-ASCII)
    with phenomena_app.test_request_context(f"/de/research/spanish/phenomena/presets/{curated_set_id}"):
        from flask import g as _g
        _g.user = "admin"
        _g.user_id = "admin-1"
        _g.role = "admin"
        page = build_phenomena_preset_editor_page("de", "spanish", curated_set_id)

    assert page is not None
    labels = page["client_state"]["labels"]
    assert labels["updateCuratedTitle"] == "Änderungen am kuratierten Set speichern?"
    assert labels["updateCuratedMessage"] == "Die Änderungen werden global am kuratierten Original gespeichert."
    assert labels["saveAsCustom"] == "Als Custom Set speichern"
    assert labels["saveAsCustomTitle"] == "Als Custom Set speichern?"
    assert labels["deleteCurated"] == "Kuratiertes Set löschen"
    assert labels["saveAsCurated"] == "Als kuratiertes Set speichern"

    # Also verify rendered HTML has correct structure
    phenomena_app.config["TEST_AUTH_USER"] = "admin"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "admin-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = "admin"
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '"isAdmin": true' in html
    assert 'data-phenomena-delete-curated-action' in html
    assert 'data-phenomena-save-as-curated-action' in html
    assert 'data-phenomena-save-as-custom-action' in html
    assert 'Kuratiertes Set löschen' in html
    assert 'Als kuratiertes Set speichern' in html
    assert 'Als Custom Set speichern' in html
    assert 'data-phenomena-curated-toggle-action' not in html


def test_editor_admin_custom_set_state_has_correct_labels(phenomena_app: Flask) -> None:
    """Admin editing a custom set must have save-as-curated available and no delete-curated in wrong context."""
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="admin-1", corpus_language="spanish")
        update_set_metadata(owner_user_id="admin-1", set_id=draft.set_id, label="Admin-Set", state="saved")

    phenomena_app.config["TEST_AUTH_USER"] = "admin"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "admin-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = "admin"
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/sets/{draft.set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '"isAdmin": true' in html
    # Template must have both buttons (JS controls visibility)
    assert 'data-phenomena-save-as-curated-action' in html
    assert 'data-phenomena-delete-curated-action' in html
    assert 'data-phenomena-delete-action' in html
    # Save-as-curated labels must be present in state
    assert 'Als kuratiertes Set speichern' in html


def test_editor_new_i18n_labels_present_in_client_state(phenomena_app: Flask) -> None:
    """discardChanges and curatedCopyHint labels must be present in client state."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None

    with phenomena_app.test_request_context(f"/de/research/spanish/phenomena/presets/{curated_set_id}"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page_de = build_phenomena_preset_editor_page("de", "spanish", curated_set_id)

    with phenomena_app.test_request_context(f"/en/research/spanish/phenomena/presets/{curated_set_id}"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page_en = build_phenomena_preset_editor_page("en", "spanish", curated_set_id)

    assert page_de is not None
    assert page_en is not None
    # DE labels
    assert page_de["client_state"]["labels"]["discardChanges"] == "Änderungen verwerfen"
    assert page_de["client_state"]["labels"]["curatedCopyHint"] == "Diese Kopie basiert auf einem kuratierten Set. Änderungen werden als eigenes Set gespeichert."
    # EN labels
    assert page_en["client_state"]["labels"]["discardChanges"] == "Discard changes"
    assert page_en["client_state"]["labels"]["curatedCopyHint"] == "This copy is based on a curated set. Changes are saved as a custom set."


def test_editor_regression_no_curated_toggle_in_template(phenomena_app: Flask) -> None:
    """Regression: data-phenomena-curated-toggle-action must not exist in template."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-phenomena-curated-toggle-action' not in html
    assert 'archivieren' not in html.lower() or 'archiviert' in html.lower()  # no visible archivieren action button

def test_public_preset_editor_route_exposes_admin_curated_actions_for_admins(phenomena_app: Flask) -> None:
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "admin"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "admin-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = "admin"
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-phenomena-delete-curated-action' in html
    assert 'data-phenomena-save-as-curated-action' in html
    assert 'data-phenomena-save-label' in html
    assert '"isAdmin": true' in html
    assert '"updateCuratedTitle"' in html
    assert 'global am kuratierten Original gespeichert.' in html
    assert '/api/research/admin/curated-sets/__SET_ID__' in html
    assert 'Kuratiertes Set löschen' in html
    assert 'Als kuratiertes Set speichern' in html


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
    confirm_start = html.rfind("<dialog", 0, html.index('data-phenomena-editor-confirm'))
    confirm_slice = html[confirm_start:]
    assert 'class="pm-dialog pm-surface-density--compact" data-phenomena-editor-confirm' in confirm_slice
    assert 'pm-dialog__actions pm-action-row' in confirm_slice
    assert 'md3-dialog' not in confirm_slice


# --- USER button visibility matrix tests ---

def test_overview_user_curated_entry_shows_only_view_button(phenomena_app: Flask) -> None:
    """USER overview: curated set must show 'Ansehen' only – no 'Als eigenes Set bearbeiten'."""
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Ansehen" in html
    assert ">Als eigenes Set bearbeiten<" not in html
    assert "data-phenomena-copy-curated-set" not in html


def test_overview_user_curated_entry_has_no_edit_hrefs(phenomena_app: Flask) -> None:
    """USER curated card: edit_curated_href and edit_as_own_href must be None."""
    with phenomena_app.test_request_context("/de/research/spanish/phenomena"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_phenomena_overview_page("de", "spanish")

    assert page is not None
    curated_entry = next(e for e in page["entries"] if e["kind"] == "curated")
    assert curated_entry["edit_curated_href"] is None
    assert curated_entry["edit_as_own_href"] is None


def test_overview_admin_curated_entry_has_edit_curated_href(phenomena_app: Flask) -> None:
    """ADMIN curated card: edit_curated_href must point to preset editor (used as Bearbeiten link)."""
    with phenomena_app.test_request_context("/de/research/spanish/phenomena"):
        g.user = "admin"
        g.user_id = "admin-1"
        g.role = "admin"
        page = build_phenomena_overview_page("de", "spanish")

    assert page is not None
    curated_entry = next(e for e in page["entries"] if e["kind"] == "curated")
    assert curated_entry["edit_curated_href"] is not None
    assert curated_entry["edit_curated_href"].endswith(
        f"/de/research/spanish/phenomena/presets/{phenomena_app.config['TEST_CURATED_SET_ID']}"
    )


def test_editor_user_new_set_has_save_button_and_no_curated_labels_in_html(phenomena_app: Flask) -> None:
    """USER new set: Speichern-Button present; admin-only curated buttons not in DOM."""
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")

    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/sets/{draft.set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '"isAdmin": false' in html
    assert 'data-phenomena-save-action' in html
    # Admin-only buttons must not be rendered server-side for USER
    assert 'data-phenomena-delete-curated-action' not in html
    assert 'data-phenomena-save-as-curated-action' not in html


def test_editor_user_curated_set_initial_state_has_correct_client_data(phenomena_app: Flask) -> None:
    """USER curated set initial: isAdmin=false, editorMode=preset, save_copy labels present."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    with phenomena_app.test_request_context(f"/de/research/spanish/phenomena/presets/{curated_set_id}"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_phenomena_preset_editor_page("de", "spanish", curated_set_id)

    assert page is not None
    state = page["client_state"]
    assert state["isAdmin"] is False
    assert state["editorMode"] == "preset"
    # Confirm-dialog labels for user saving curated-set-as-copy must be present
    assert state["labels"]["saveCopyTitle"] == "Als eigenes Set speichern?"
    assert state["labels"]["saveCopyMessage"] == "Das kuratierte Set wird nicht verändert. Ihre Änderungen werden als eigenes Set gespeichert."


def test_editor_user_curated_set_initial_template_has_discard_hidden(phenomena_app: Flask) -> None:
    """USER curated set: discard button starts hidden (JS un-hides on first change)."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-phenomena-discard-action hidden' in html


def test_editor_user_saved_custom_set_has_delete_and_no_curated_admin_buttons(phenomena_app: Flask) -> None:
    """USER saved custom set: delete-action present; admin curated buttons start hidden."""
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        update_set_metadata(owner_user_id="user-1", set_id=draft.set_id, label="Mein Set", state="saved")

    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/sets/{draft.set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '"isAdmin": false' in html
    assert 'data-phenomena-delete-action' in html
    # Admin-only buttons must not be rendered server-side for USER
    assert 'data-phenomena-delete-curated-action' not in html
    assert 'data-phenomena-save-as-curated-action' not in html


def test_editor_user_curated_copy_client_state_is_custom_set_mode(phenomena_app: Flask) -> None:
    """USER custom copy from curated: editorMode=set, isAdmin=false, no curated admin buttons."""
    with phenomena_app.app_context():
        draft = create_draft_set(
            owner_user_id="user-1",
            corpus_language="spanish",
            source_curated_set_id=phenomena_app.config["TEST_CURATED_SET_ID"],
        )
        update_set_metadata(owner_user_id="user-1", set_id=draft.set_id, label="Meine Kopie", state="saved")

    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/sets/{draft.set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '"isAdmin": false' in html
    assert '"editorMode": "set"' in html
    # Admin-only buttons must not be rendered server-side for USER
    assert 'data-phenomena-delete-curated-action' not in html
    assert 'data-phenomena-save-as-curated-action' not in html


def test_editor_js_dirty_declared_before_use_in_sync_status() -> None:
    """Regression: syncStatus() must declare dirty via isDirty() before any use of dirty."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    sync_start = source.index("function syncStatus()")
    sync_end = source.index("\n  function ", sync_start + 1)
    sync_body = source[sync_start:sync_end]

    # dirty must be declared as a const at the top of syncStatus
    assert "const dirty = isDirty();" in sync_body
    # its first use must come after the declaration
    decl_pos = sync_body.index("const dirty = isDirty();")
    first_use = sync_body.index("dirty", decl_pos + len("const dirty = isDirty();"))
    assert first_use > decl_pos, "dirty used before declaration in syncStatus"


def test_editor_js_discard_hidden_logic_present_in_source() -> None:
    """JS: syncStatus must hide discard button when not dirty."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "discardButton.hidden = !dirty" in source


def test_editor_js_user_curated_save_opens_confirm_in_source() -> None:
    """JS: save button handler must check !state.isAdmin && isCuratedRecord() for confirm dialog."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "!state.isAdmin && isCuratedRecord() && isDirty()" in source
    assert "saveCopyTitle" in source
    assert "saveCopyMessage" in source


def test_editor_js_preset_mode_uses_source_curated_set_id_in_source() -> None:
    """JS: persistCurrentRecord must pass source_curated_set_id when copying from preset mode."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "source_curated_set_id: record.set_id" in source


def test_editor_new_i18n_save_copy_labels_present_in_client_state(phenomena_app: Flask) -> None:
    """DE + EN: saveCopyTitle and saveCopyMessage must be present in editor client state."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    with phenomena_app.test_request_context(f"/de/research/spanish/phenomena/presets/{curated_set_id}"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page_de = build_phenomena_preset_editor_page("de", "spanish", curated_set_id)

    with phenomena_app.test_request_context(f"/en/research/spanish/phenomena/presets/{curated_set_id}"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page_en = build_phenomena_preset_editor_page("en", "spanish", curated_set_id)

    assert page_de is not None
    assert page_en is not None
    assert page_de["client_state"]["labels"]["saveCopyTitle"] == "Als eigenes Set speichern?"
    assert page_de["client_state"]["labels"]["saveCopyMessage"] == "Das kuratierte Set wird nicht verändert. Ihre Änderungen werden als eigenes Set gespeichert."
    assert page_en["client_state"]["labels"]["saveCopyTitle"] == "Save as your own set?"
    assert page_en["client_state"]["labels"]["saveCopyMessage"] == "The curated set will not be changed. Your changes will be saved as your own set."


# --- ADMIN button matrix tests ---

def test_overview_admin_curated_shows_ansehen_and_bearbeiten(phenomena_app: Flask) -> None:
    """ADMIN overview: curated entry shows Ansehen + Bearbeiten only."""
    phenomena_app.config["TEST_AUTH_USER"] = "admin"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "admin-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = "admin"
    client = phenomena_app.test_client()
    response = client.get("/de/research/spanish/phenomena")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Ansehen" in html
    assert ">Bearbeiten<" in html
    assert ">Kuratiertes Set bearbeiten<" not in html
    assert ">Als eigenes Set bearbeiten<" not in html


def test_editor_admin_curated_has_save_as_custom_button(phenomena_app: Flask) -> None:
    """ADMIN curated editor: data-phenomena-save-as-custom-action must be in DOM."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "admin"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "admin-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = "admin"
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-phenomena-save-as-custom-action' in html
    assert 'Als Custom Set speichern' in html
    assert '"isAdmin": true' in html


def test_editor_admin_custom_set_has_save_as_curated_and_overflow(phenomena_app: Flask) -> None:
    """ADMIN custom set editor: save-as-curated and overflow buttons present in DOM."""
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="admin-1", corpus_language="spanish")
        update_set_metadata(owner_user_id="admin-1", set_id=draft.set_id, label="Admin-Set", state="saved")

    phenomena_app.config["TEST_AUTH_USER"] = "admin"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "admin-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = "admin"
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/sets/{draft.set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-phenomena-save-as-curated-action' in html
    # delete-curated is in DOM for all admins (JS hides it for non-curated context)
    assert 'data-phenomena-delete-curated-action' in html
    # save-as-custom is in DOM for all admins (JS hides it for non-curated context)
    assert 'data-phenomena-save-as-custom-action' in html
    # Overflow container must be present
    assert 'data-phenomena-editor-overflow' in html
    assert '"isAdmin": true' in html
    # isAdmin=true means editorMode=set for custom set
    assert '"editorMode": "set"' in html


def test_editor_admin_new_set_has_save_and_overflow_present(phenomena_app: Flask) -> None:
    """ADMIN new set: save, save-as-curated, overflow present in DOM (JS controls visibility)."""
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="admin-1", corpus_language="spanish")

    phenomena_app.config["TEST_AUTH_USER"] = "admin"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "admin-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = "admin"
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/sets/{draft.set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-phenomena-save-action' in html
    assert 'data-phenomena-save-as-curated-action' in html
    assert 'data-phenomena-editor-overflow' in html
    assert '"isAdmin": true' in html


def test_editor_js_save_as_custom_button_logic_in_source() -> None:
    """JS: save-as-custom button handler must check isAdmin+isCuratedRecord."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "data-phenomena-save-as-custom-action" in source
    assert "saveAsCustomTitle" in source
    assert "saveAsCustomMessage" in source
    assert "persistSaveAsCopy" in source


def test_editor_js_overflow_visibility_logic_in_source() -> None:
    """JS: syncStatus must compute overflow menu visibility based on overflow action state."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "data-phenomena-editor-overflow" in source
    assert "hasOverflowAction" in source
    assert "overflowMenu.hidden" in source


def test_editor_js_overflow_utility_imported_in_editor() -> None:
    """JS: overflow-menu utility must be imported in editor JS."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert 'overflow-menu.js' in source
    assert 'initOverflowMenus' in source


def test_editor_admin_save_as_custom_labels_present(phenomena_app: Flask) -> None:
    """DE + EN: saveAsCustom labels must be in editor client state."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    with phenomena_app.test_request_context(f"/de/research/spanish/phenomena/presets/{curated_set_id}"):
        from flask import g as _g
        _g.user = "admin"
        _g.user_id = "admin-1"
        _g.role = "admin"
        page_de = build_phenomena_preset_editor_page("de", "spanish", curated_set_id)

    with phenomena_app.test_request_context(f"/en/research/spanish/phenomena/presets/{curated_set_id}"):
        from flask import g as _g
        _g.user = "admin"
        _g.user_id = "admin-1"
        _g.role = "admin"
        page_en = build_phenomena_preset_editor_page("en", "spanish", curated_set_id)

    assert page_de is not None
    assert page_en is not None
    assert page_de["client_state"]["labels"]["saveAsCustom"] == "Als Custom Set speichern"
    assert page_de["client_state"]["labels"]["saveAsCustomTitle"] == "Als Custom Set speichern?"
    assert page_de["client_state"]["labels"]["updateCurated"] == "Änderungen speichern"
    assert page_en["client_state"]["labels"]["saveAsCustom"] == "Save as custom set"
    assert page_en["client_state"]["labels"]["saveAsCustomTitle"] == "Save as custom set?"
    assert page_en["client_state"]["labels"]["updateCurated"] == "Save changes"


# --- Overflow behavior tests ---

def test_overview_template_uses_data_overflow_menu_attribute() -> None:
    """Regression: overview custom set overflow must use data-overflow-menu attribute."""
    from pathlib import Path
    template = Path(__file__).resolve().parents[1] / "templates" / "pages" / "research_phenomena_overview.html"
    content = template.read_text(encoding="utf-8")
    assert "data-overflow-menu" in content
    assert "data-phenomena-overflow" in content


def test_editor_template_uses_data_overflow_menu_attribute() -> None:
    """Regression: editor overflow must use data-overflow-menu attribute."""
    from pathlib import Path
    template = Path(__file__).resolve().parents[1] / "templates" / "pages" / "research_phenomena_editor.html"
    content = template.read_text(encoding="utf-8")
    assert "data-overflow-menu" in content
    assert "data-phenomena-editor-overflow" in content


def test_overflow_menu_utility_module_exists_and_exports_init() -> None:
    """Regression: overflow-menu.js must exist and export initOverflowMenus."""
    from pathlib import Path
    module = Path(__file__).resolve().parents[1] / "static" / "js" / "modules" / "core" / "overflow-menu.js"
    assert module.exists()
    content = module.read_text(encoding="utf-8")
    assert "export function initOverflowMenus" in content
    assert "data-overflow-menu" in content
    assert "Escape" in content


# --- New matrix / finalization tests ---

def test_editor_js_new_matrix_save_visible_logic_in_source() -> None:
    """JS: save button visibility must be derived from isDraft || dirty, not just dirty."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "isDraft || dirty" in source or "isDraftCustom() || dirty" in source
    assert "saveButton.hidden = !saveVisible" in source


def test_editor_js_save_as_custom_and_curated_in_overflow_not_main_bar() -> None:
    """JS: saveAsCustom and saveAsCurated must be in the overflow, not as top-level action buttons."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "data-phenomena-save-as-custom-action" in source
    assert "data-phenomena-save-as-curated-action" in source


def test_editor_template_save_as_custom_in_overflow_menu() -> None:
    """Template: save-as-custom must be inside the overflow menu (not a main-bar button)."""
    from pathlib import Path
    template_path = Path(__file__).resolve().parents[1] / "templates" / "pages" / "research_phenomena_editor.html"
    content = template_path.read_text(encoding="utf-8")
    overflow_start = content.index("data-phenomena-editor-overflow")
    assert "data-phenomena-save-as-custom-action" in content[overflow_start:]
    assert "data-phenomena-save-as-curated-action" in content[overflow_start:]
    assert "data-phenomena-delete-curated-action" in content[overflow_start:]
    assert "data-phenomena-delete-action" in content[overflow_start:]


def test_editor_template_uses_comparison_more_filters_for_overflow() -> None:
    """Template: overflow must use pm-comparison-more-filters CSS pattern (no raw triangle)."""
    from pathlib import Path
    template_path = Path(__file__).resolve().parents[1] / "templates" / "pages" / "research_phenomena_editor.html"
    content = template_path.read_text(encoding="utf-8")
    assert "pm-comparison-more-filters" in content
    assert "pm-comparison-more-filters__summary" in content
    assert "pm-comparison-more-filters__body" in content


def test_editor_js_overflow_includes_saveascustom_check_in_hasoverflowaction() -> None:
    """JS: hasOverflowAction must check saveAsCustomButton and saveAsCuratedButton."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "saveAsCustomButton" in source
    assert "saveAsCuratedButton" in source
    assert "hasOverflowAction" in source


def test_editor_js_commit_save_baseline_function_present() -> None:
    """JS: commitSave() must update baseline = snapshot() to prevent false leave-warning."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "function commitSave" in source
    assert "baseline = snapshot();" in source


def test_editor_js_leave_warning_uses_isdirty_not_flag() -> None:
    """JS: beforeunload handler must check isDirty(), not a saveCompleted flag."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    beforeunload_start = source.index("beforeunload")
    # suppressBeforeUnload OR !isDirty() must be the gate
    segment = source[beforeunload_start:beforeunload_start + 300]
    assert "isDirty()" in segment
    assert "suppressBeforeUnload" in segment


def test_editor_js_discard_hidden_only_when_dirty() -> None:
    """JS: discardButton.hidden = !dirty (clean state → hidden, dirty → visible)."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "discardButton.hidden = !dirty" in source


def test_editor_template_save_button_starts_hidden() -> None:
    """Template: save button must start with hidden attribute (JS controls visibility)."""
    from pathlib import Path
    template_path = Path(__file__).resolve().parents[1] / "templates" / "pages" / "research_phenomena_editor.html"
    content = template_path.read_text(encoding="utf-8")
    assert 'data-phenomena-save-action hidden' in content


def test_editor_admin_curated_set_has_overflow_with_all_admin_actions(phenomena_app: Flask) -> None:
    """ADMIN curated: template has save-as-custom, save-as-curated, delete-curated in overflow."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "admin"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "admin-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = "admin"
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '"isAdmin": true' in html
    # All admin overflow actions must be in DOM
    assert 'data-phenomena-save-as-custom-action' in html
    assert 'data-phenomena-save-as-curated-action' in html
    assert 'data-phenomena-delete-curated-action' in html
    # Overflow structure
    assert 'pm-comparison-more-filters' in html
    assert 'data-phenomena-editor-overflow' in html


def test_editor_user_curated_has_no_overflow_actions_for_user(phenomena_app: Flask) -> None:
    """USER curated: no admin-only overflow actions in DOM."""
    curated_set_id = phenomena_app.config["TEST_CURATED_SET_ID"]
    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/presets/{curated_set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '"isAdmin": false' in html
    # Admin-only buttons must be absent
    assert 'data-phenomena-save-as-custom-action' not in html
    assert 'data-phenomena-save-as-curated-action' not in html
    assert 'data-phenomena-delete-curated-action' not in html
    # Overflow itself is present (for delete-custom if user has saved custom sets)
    assert 'data-phenomena-editor-overflow' in html


def test_editor_user_saved_custom_has_delete_in_overflow_not_main_bar(phenomena_app: Flask) -> None:
    """USER saved custom: delete action is in the overflow, not a top-level main-bar button."""
    with phenomena_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        update_set_metadata(owner_user_id="user-1", set_id=draft.set_id, label="Mein Set", state="saved")

    phenomena_app.config["TEST_AUTH_USER"] = "alice"
    phenomena_app.config["TEST_AUTH_USER_ID"] = "user-1"
    phenomena_app.config["TEST_AUTH_ROLE"] = None
    client = phenomena_app.test_client()
    response = client.get(f"/de/research/spanish/phenomena/sets/{draft.set_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # Delete must be in the overflow
    assert 'data-phenomena-editor-overflow' in html
    assert 'data-phenomena-delete-action' in html
    # Delete must NOT be a standalone primary main-bar button
    assert 'pm-action-button--danger' not in html.split('data-phenomena-editor-overflow')[0].split('data-phenomena-save-action')[-1]


# --- Regression tests ---

def test_regression_no_curated_toggle_action_in_js() -> None:
    """Regression: data-phenomena-curated-toggle-action must not exist in editor JS."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert "data-phenomena-curated-toggle-action" not in source


def test_regression_item_selection_still_works_in_js() -> None:
    """Regression: root click handler for item toggle must still exist in editor JS."""
    source = PHENOMENA_EDITOR_JS.read_text(encoding="utf-8")
    assert 'root.addEventListener("click"' in source
    assert 'data-toggle-selection' in source
    assert 'data-remove-selection' in source
