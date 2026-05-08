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
from app.routes.auth import blueprint as auth_blueprint
from app.extensions import register_extensions
from app.extensions.sqlalchemy_ext import get_engine, get_session, init_engine
from app.research_player_runtime import resolve_player_runtime_state
from app.research_presets import clear_research_preset_caches
from app.research_sessions import get_session as get_research_session, load_language_sessions, load_person_records
from app.research_sets import ResearchSetStorageUnavailableError, create_draft_set, replace_set_items, update_set_metadata
from app.research_views import build_player_page, _is_playable_audio_artifact
from app.routes.public import blueprint as public_blueprint


def _clear_runtime_caches() -> None:
    clear_research_preset_caches()
    load_language_sessions.cache_clear()
    load_person_records.cache_clear()
    _is_playable_audio_artifact.cache_clear()


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_binary(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"ID3\x04\x00\x00\x00\x00\x00\x00\xff\xfb\x90\x64" + (b"\x00" * 256))


def _task(task_type: str) -> dict[str, str]:
    return {
        "task_type": task_type,
        "label": task_type,
        "source_file": f"source/{task_type}.wav",
        "alignment_file": f"alignment/{task_type}.TextGrid",
    }


def _write_session(runtime_root: Path, language_slug: str, session_id: str, payload: dict[str, object]) -> None:
    session_dir = runtime_root / "data" / "sessions" / language_slug / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "metadata.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _session_payload(person_id: str, session_id: str, speaker_type: str = "learner") -> dict[str, object]:
    return {
        "person_id": person_id,
        "session_id": session_id,
        "target_language": "es",
        "speaker_type": speaker_type,
        "l1": "DE" if speaker_type == "learner" else None,
        "gender": "female",
        "birth_year": 1998,
        "level_code": "B1" if speaker_type == "learner" else None,
        "level_self": "B1" if speaker_type == "learner" else None,
        "origin_country": "Spain" if speaker_type != "learner" else None,
        "standard_variety": "es_std" if speaker_type != "learner" else None,
        "recording_year": 2026,
        "recording_date": "2026-03-10",
        "context": "baseline",
        "recorded_by": "Ana Romero",
        "notes": "test session",
        "tasks": [_task("wordlist"), _task("text")],
    }


def _write_wordlist_artifacts(runtime_root: Path, language_slug: str, session_id: str, person_id: str, items: list[dict[str, object]]) -> None:
    session_dir = runtime_root / "data" / "sessions" / language_slug / session_id
    _write_binary(session_dir / "derived" / "wordlist.mp3")
    alignment_items = []
    start_ms = 400
    for item in items:
        item_id = str(item["item_id"])
        split_relative = f"items/wordlist/{item_id}.mp3"
        _write_binary(session_dir / split_relative)
        alignment_items.append(
            {
                "item_id": item_id,
                "item_number": str(item["item_number"]),
                "text": str(item["text"]),
                "start_ms": start_ms,
                "end_ms": start_ms + 700,
                "split_mp3": split_relative,
            }
        )
        start_ms += 900

    _write_json(
        session_dir / "alignment" / "wordlist.json",
        {
            "session_id": session_id,
            "person_id": person_id,
            "task": "wordlist",
            "audio": {"full_mp3": "derived/wordlist.mp3"},
            "items": alignment_items,
        },
    )


def _write_text_artifacts(
    runtime_root: Path,
    language_slug: str,
    session_id: str,
    person_id: str,
    items: list[dict[str, object]],
    *,
    split_item_ids: set[str] | None = None,
) -> None:
    session_dir = runtime_root / "data" / "sessions" / language_slug / session_id
    _write_binary(session_dir / "derived" / "text.mp3")
    alignment_items = []
    start_ms = 1200
    effective_split_item_ids = split_item_ids if split_item_ids is not None else {str(item["item_id"]) for item in items}
    for item in items:
        item_id = str(item["item_id"])
        split_relative = f"items/text/{item_id}.mp3"
        alignment_item = {
            "item_id": item_id,
            "item_number": str(item["item_number"]),
            "text": str(item["text"]),
            "start_ms": start_ms,
            "end_ms": start_ms + 1200,
        }
        if item_id in effective_split_item_ids:
            _write_binary(session_dir / split_relative)
            alignment_item["split_mp3"] = split_relative
        alignment_items.append(alignment_item)
        start_ms += 1500

    _write_json(
        session_dir / "alignment" / "text.json",
        {
            "session_id": session_id,
            "person_id": person_id,
            "task": "text",
            "audio": {"full_mp3": "derived/text.mp3"},
            "items": alignment_items,
        },
    )


def _write_minimal_runtime(runtime_root: Path) -> None:
    config_dir = runtime_root / "data" / "config" / "research_player" / "spanish"
    _write_json(
        config_dir / "task_catalogs" / "wordlist.json",
        {
            "task": "wordlist",
            "language": "spanish",
            "player_source": {
                "source_kind": "wordlist",
                "content_mode": "wordlist",
                "default_view": "list",
                "allowed_views": ["list"],
                "primary_audio_mode": "item",
                "supports_item_audio": True,
                "supports_full_audio": True,
                "supports_text_view": False,
                "paragraph_model": "none",
            },
            "items": [
                {"item_id": "wl_001", "item_number": "1", "text": "mesa"},
                {"item_id": "wl_002", "item_number": "2", "text": "reloj"},
            ],
        },
    )
    _write_json(
        config_dir / "task_catalogs" / "text.json",
        {
            "task": "text",
            "language": "spanish",
            "display_label": "Satzliste",
            "player_source": {
                "source_kind": "sentence_list",
                "content_mode": "sentence_list",
                "default_view": "list",
                "allowed_views": ["list"],
                "primary_audio_mode": "item",
                "supports_item_audio": True,
                "supports_full_audio": True,
                "supports_text_view": False,
                "paragraph_model": "none",
            },
            "items": [
                {"item_id": "d_01", "item_number": "D1", "text": "Hoy miro el reloj con calma antes de salir."},
                {"item_id": "d_02", "item_number": "D2", "text": "Mañana vuelvo a casa después del trabajo."},
            ],
        },
    )
    _write_json(
        config_dir / "player_config.json",
        {
            "language": "spanish",
            "text": {"default_render_mode": "sentence_list", "display_label": "Satzliste"},
        },
    )
    _write_json(
        config_dir / "phenomena_presets.json",
        {
            "language": "spanish",
            "presets": [
                {
                    "preset_id": "starter_preset",
                    "label": "Starter",
                    "description": "Minimal preset for player set-context tests.",
                    "language": "spanish",
                    "items": [
                        {"task": "wordlist", "item_id": "wl_001"},
                        {"task": "text", "item_id": "d_01"},
                    ],
                }
            ],
        },
    )

    primary_session = "ES-L-0001-2026-S01"
    compare_session = "ES-N-0001-2026-S01"
    _write_session(runtime_root, "spanish", primary_session, _session_payload("ES-L-0001", primary_session))
    _write_session(runtime_root, "spanish", compare_session, _session_payload("ES-N-0001", compare_session, speaker_type="native_speaker"))
    wordlist_items = [
        {"item_id": "wl_001", "item_number": "1", "text": "mesa"},
        {"item_id": "wl_002", "item_number": "2", "text": "reloj"},
    ]
    text_items = [
        {"item_id": "d_01", "item_number": "D1", "text": "Hoy miro el reloj con calma antes de salir."},
        {"item_id": "d_02", "item_number": "D2", "text": "Mañana vuelvo a casa después del trabajo."},
    ]
    _write_wordlist_artifacts(runtime_root, "spanish", primary_session, "ES-L-0001", wordlist_items)
    _write_wordlist_artifacts(runtime_root, "spanish", compare_session, "ES-N-0001", wordlist_items)
    _write_text_artifacts(runtime_root, "spanish", primary_session, "ES-L-0001", text_items)
    _write_text_artifacts(runtime_root, "spanish", compare_session, "ES-N-0001", text_items)


def _write_connected_text_catalog(runtime_root: Path) -> None:
    config_dir = runtime_root / "data" / "config" / "research_player" / "spanish"
    _write_json(
        config_dir / "task_catalogs" / "text.json",
        {
            "task": "text",
            "language": "spanish",
            "display_label": "Text",
            "player_source": {
                "source_kind": "text",
                "content_mode": "connected_text",
                "default_view": "text",
                "allowed_views": ["text", "list"],
                "primary_audio_mode": "full",
                "supports_item_audio": True,
                "supports_full_audio": True,
                "supports_text_view": True,
                "paragraph_model": "explicit",
            },
            "items": [
                {
                    "item_id": "d_01",
                    "item_number": "D1",
                    "text": "Hoy miro el reloj con calma antes de salir.",
                    "text_container_id": "story_01",
                    "text_order_index": 1,
                    "paragraph_break_before": True,
                    "paragraph_id": "p1",
                },
                {
                    "item_id": "d_02",
                    "item_number": "D2",
                    "text": "Mañana vuelvo a casa después del trabajo.",
                    "text_container_id": "story_01",
                    "text_order_index": 2,
                    "paragraph_break_before": True,
                    "paragraph_id": "p2",
                },
            ],
        },
    )


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
def player_set_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Flask:
    runtime_root = tmp_path / "runtime"
    public_root = tmp_path / "public"
    runtime_root.mkdir(parents=True, exist_ok=True)
    public_root.mkdir(parents=True, exist_ok=True)
    _write_minimal_runtime(runtime_root)

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
        _insert_user("user-2", "bob")

    @app.before_request
    def _set_test_auth_context() -> None:
        g.user = app.config.get("TEST_AUTH_USER")
        g.user_id = app.config.get("TEST_AUTH_USER_ID")
        g.role = None

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(public_blueprint)
    _clear_runtime_caches()
    yield app
    _clear_runtime_caches()


def _create_set(*, owner_user_id: str, items: list[dict[str, str]]) -> str:
    record = create_draft_set(owner_user_id=owner_user_id, corpus_language="spanish")
    updated = replace_set_items(owner_user_id=owner_user_id, set_id=record.set_id, items=items)
    return updated.set_id


def test_player_runtime_resolves_connected_text_set_excerpt_to_list_only_state(player_set_app: Flask) -> None:
    runtime_root = Path(os.environ["PROMAT_RUNTIME_ROOT"])
    _write_connected_text_catalog(runtime_root)

    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "text", "item_id": "d_02"}])
        _clear_runtime_caches()

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        session = get_research_session("spanish", "ES-L-0001-2026-S01")
        assert session is not None
        state = resolve_player_runtime_state(
            "de",
            "spanish",
            session,
            "text",
            source="speakers",
            owner_user_id="user-1",
            compare_session_id=None,
            compare_mode=None,
            set_id=set_id,
            preset_id=None,
            focus_item="d_02",
            focus_segment=None,
            render_mode="running_text",
        )

    assert state.set_context is not None
    assert state.set_context["status"] == "loaded"
    assert state.player_source is not None
    assert state.player_source.source_kind == "set"
    assert state.player_source.render_mode == "sentence_list"
    assert state.player_source.allowed_render_modes == ("sentence_list",)
    assert state.active_render_mode_query is None
    assert [item["item_id"] for item in state.primary_items] == ["d_02"]
    assert state.visible_focus_item_id == "d_02"
    assert state.filtered_task_empty is False


def test_player_runtime_marks_invalid_compare_session_without_breaking_primary_state(player_set_app: Flask) -> None:
    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        session = get_research_session("spanish", "ES-L-0001-2026-S01")
        assert session is not None
        state = resolve_player_runtime_state(
            "de",
            "spanish",
            session,
            "text",
            source="speakers",
            owner_user_id="user-1",
            compare_session_id="missing-session",
            compare_mode="manual",
            set_id=None,
            preset_id=None,
            focus_item=None,
            focus_segment=None,
            render_mode=None,
        )

    assert state.compare_requested_unavailable is True
    assert state.compare_session is None
    assert state.compare_bundle is None
    assert state.effective_compare_mode == "single"
    assert [item["item_id"] for item in state.primary_items] == ["d_01", "d_02"]
    assert state.compare_rows == []


def test_player_filters_wordlist_to_active_set_excerpt(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "wordlist", "item_id": "wl_002"}])

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page("de", "spanish", "ES-L-0001-2026-S01", "wordlist", "comparison", set_id=set_id)

    assert page is not None
    assert page["player"]["mode"] == "wordlist"
    assert [item["item_id"] for item in page["player"]["items"]] == ["wl_002"]
    assert page["player"]["set_notice"] is None


def test_player_renders_explicit_empty_state_when_task_excerpt_is_empty(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "text", "item_id": "d_01"}])

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page("de", "spanish", "ES-L-0001-2026-S01", "wordlist", "comparison", set_id=set_id)

    assert page is not None
    assert page["player"]["mode"] == "wordlist"
    assert "keine sichtbaren Items" in page["player"]["empty_state"]["message"]
    assert page["player"]["set_notice"] is None
    assert [action["action"] for action in page["summary_cards"][0]["card_actions"]] == ["profile", "compare-add"]
    assert page["player"]["set_select"]["options"][0]["label"] == "Alle Items"
    assert any(option["current"] for option in page["player"]["set_select"]["options"][1:])


def test_player_focus_item_marks_visible_set_excerpt(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(
            owner_user_id="user-1",
            items=[
                {"task": "wordlist", "item_id": "wl_001"},
                {"task": "wordlist", "item_id": "wl_002"},
            ],
        )

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "wordlist",
            "comparison",
            set_id=set_id,
            focus_item="wl_002",
        )

    assert page is not None
    assert page["player"]["client_state"]["focusedItemId"] == "wl_002"
    assert page["player"]["set_notice"] is None


def test_player_set_select_uses_saved_workbench_list_and_only_keeps_current_draft(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        saved_set_id = _create_set(owner_user_id="user-1", items=[{"task": "wordlist", "item_id": "wl_001"}])
        update_set_metadata(owner_user_id="user-1", set_id=saved_set_id, label="Gespeichertes Set", state="saved")
        current_draft_id = _create_set(owner_user_id="user-1", items=[{"task": "wordlist", "item_id": "wl_002"}])
        update_set_metadata(owner_user_id="user-1", set_id=current_draft_id, label="Aktiver Draft")
        hidden_draft_id = _create_set(owner_user_id="user-1", items=[{"task": "text", "item_id": "d_01"}])
        update_set_metadata(owner_user_id="user-1", set_id=hidden_draft_id, label="Versteckter Draft")

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        base_page = build_player_page("de", "spanish", "ES-L-0001-2026-S01", "wordlist", "comparison")
        current_draft_page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "wordlist",
            "comparison",
            set_id=current_draft_id,
        )

    assert base_page is not None
    assert [option["label"] for option in base_page["player"]["set_select"]["options"]] == ["Alle Items", "Starter", "Gespeichertes Set"]

    assert current_draft_page is not None
    assert [option["label"] for option in current_draft_page["player"]["set_select"]["options"]] == [
        "Alle Items",
        "Starter",
        "Aktiver Draft",
        "Gespeichertes Set",
    ]
    assert current_draft_page["player"]["set_select"]["options"][2]["current"] is True


def test_player_set_select_marks_curated_preset_as_active_context(player_set_app: Flask) -> None:
    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "wordlist",
            "phenomena",
            preset_id="starter_preset",
        )

    assert page is not None
    assert [option["label"] for option in page["player"]["set_select"]["options"][:2]] == ["Alle Items", "Starter"]
    assert page["player"]["set_select"]["options"][1]["current"] is True
    assert [item["item_id"] for item in page["player"]["items"]] == ["wl_001"]


def test_player_task_switches_keep_set_and_focus_context(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "wordlist", "item_id": "wl_001"}])

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "wordlist",
            "phenomena",
            set_id=set_id,
            preset_id="starter_preset",
            focus_item="wl_001",
        )

    assert page is not None
    text_panel = next(panel for panel in page["task_panels"] if panel["key"] == "text")
    assert text_panel["href"] is not None
    assert text_panel["href"].endswith(
        f"/de/research/spanish/player/ES-L-0001-2026-S01/text?source=phenomena&set_id={set_id}&preset_id=starter_preset&focus_item=wl_001"
    )
    assert page["player"]["client_state"]["singleViewHref"].endswith(
        f"/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=phenomena&set_id={set_id}&focus_item=wl_001"
    )


def test_player_compare_rows_are_filtered_by_same_set_excerpt(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "wordlist", "item_id": "wl_001"}])

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "wordlist",
            "comparison",
            compare_session_id="ES-N-0001-2026-S01",
            set_id=set_id,
        )

    assert page is not None
    assert page["player"]["compare"]["is_ready"] is True
    assert [row["item_id"] for row in page["player"]["compare"]["rows"]] == ["wl_001"]
    assert page["player"]["client_state"]["modeHrefs"]["sequence"].endswith(
        f"/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=comparison&compare_session=ES-N-0001-2026-S01&set_id={set_id}"
    )


def test_player_degrades_without_leaking_set_data_when_owner_context_is_missing(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "wordlist", "item_id": "wl_002"}])

    with player_set_app.test_request_context():
        g.user = None
        g.user_id = None
        g.role = None
        page = build_player_page("de", "spanish", "ES-L-0001-2026-S01", "wordlist", "comparison", set_id=set_id)

    assert page is not None
    assert [item["item_id"] for item in page["player"]["items"]] == ["wl_001", "wl_002"]
    assert page["player"]["set_notice"]["status"] == "requires-auth"


def test_player_degrades_cleanly_when_set_storage_is_unavailable(
    player_set_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_storage_error(*, owner_user_id: str, set_id: str, touch_access: bool = True):
        del owner_user_id, set_id, touch_access
        raise ResearchSetStorageUnavailableError("Research-set storage is unavailable.")

    monkeypatch.setattr("app.research_views.load_owned_set", raise_storage_error)

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page("de", "spanish", "ES-L-0001-2026-S01", "wordlist", "comparison", set_id="set-missing")

    assert page is not None
    assert [item["item_id"] for item in page["player"]["items"]] == ["wl_001", "wl_002"]
    assert page["player"]["set_notice"]["status"] == "storage-unavailable"


def test_player_route_renders_filtered_handoff_from_comparison(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "wordlist", "item_id": "wl_002"}])

    player_set_app.config["TEST_AUTH_USER"] = "alice"
    player_set_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = player_set_app.test_client()
    response = client.get(
        f"/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=comparison&set_id={set_id}&focus_item=wl_002"
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-player-set-context' not in html
    assert 'data-player-set-notice' not in html
    assert 'data-player-focus-item="wl_002"' in html
    assert 'data-player-focus-item="wl_001"' not in html


def test_text_player_builds_productive_sentence_list_with_set_context(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(
            owner_user_id="user-1",
            items=[
                {"task": "text", "item_id": "d_01"},
                {"task": "text", "item_id": "d_02"},
            ],
        )

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page("de", "spanish", "ES-L-0001-2026-S01", "text", "comparison", set_id=set_id, focus_item="d_01")

    assert page is not None
    assert page["player"]["mode"] == "text"
    assert page["player"]["render_mode"] == "sentence_list"
    assert page["player"]["source_kind"] == "set"
    assert page["player"]["set_notice"] is None
    assert [item["item_id"] for item in page["player"]["items"]] == ["d_01", "d_02"]
    assert page["player"]["client_state"]["focusedItemId"] == "d_01"


def test_connected_text_source_falls_back_to_list_view_inside_set_excerpt(player_set_app: Flask) -> None:
    runtime_root = Path(os.environ["PROMAT_RUNTIME_ROOT"])
    _write_connected_text_catalog(runtime_root)

    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "text", "item_id": "d_01"}])

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "text",
            "phenomena",
            set_id=set_id,
            focus_item="d_01",
            render_mode="running_text",
        )

    assert page is not None
    assert page["player"]["mode"] == "text"
    assert page["player"]["source_kind"] == "set"
    assert page["player"]["render_mode"] == "sentence_list"
    assert page["player"]["render_modes"] is None
    assert page["player"]["text_blocks"] == []
    assert [item["item_id"] for item in page["player"]["items"]] == ["d_01"]


def test_text_set_select_preserves_render_mode_query_for_saved_sets(player_set_app: Flask) -> None:
    runtime_root = Path(os.environ["PROMAT_RUNTIME_ROOT"])
    _write_connected_text_catalog(runtime_root)

    with player_set_app.app_context():
        saved_set_id = _create_set(owner_user_id="user-1", items=[{"task": "text", "item_id": "d_01"}])
        update_set_metadata(owner_user_id="user-1", set_id=saved_set_id, label="Gespeichertes Set", state="saved")

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "text",
            "speakers",
            render_mode="sentence_list",
        )

    assert page is not None
    assert page["player"]["render_mode"] == "sentence_list"
    saved_option = next(
        option for option in page["player"]["set_select"]["options"] if option["label"] == "Gespeichertes Set"
    )
    assert saved_option["href"].endswith(
        f"/de/research/spanish/player/ES-L-0001-2026-S01/text?source=speakers&set_id={saved_set_id}&render_mode=sentence_list"
    )


def test_text_player_filters_to_set_excerpt(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "text", "item_id": "d_02"}])

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page("de", "spanish", "ES-L-0001-2026-S01", "text", "phenomena", set_id=set_id, focus_item="d_02")

    assert page is not None
    assert page["player"]["mode"] == "text"
    assert [item["item_id"] for item in page["player"]["items"]] == ["d_02"]
    assert page["player"]["client_state"]["focusedItemId"] == "d_02"


def test_text_player_renders_explicit_empty_state_when_text_excerpt_is_empty(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "wordlist", "item_id": "wl_001"}])

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page("de", "spanish", "ES-L-0001-2026-S01", "text", "comparison", set_id=set_id)

    assert page is not None
    assert page["player"]["mode"] == "text"
    assert "keine sichtbaren Items" in page["player"]["empty_state"]["message"]
    assert page["player"]["set_select"]["options"][0]["label"] == "Alle Items"


def test_text_task_switch_keeps_set_context_and_becomes_available(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(
            owner_user_id="user-1",
            items=[
                {"task": "wordlist", "item_id": "wl_001"},
                {"task": "text", "item_id": "d_02"},
            ],
        )

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page("de", "spanish", "ES-L-0001-2026-S01", "wordlist", "phenomena", set_id=set_id, focus_item="wl_001")

    assert page is not None
    text_panel = next(panel for panel in page["task_panels"] if panel["key"] == "text")
    assert text_panel["href"] is not None
    assert text_panel["href"].endswith(
        f"/de/research/spanish/player/ES-L-0001-2026-S01/text?source=phenomena&set_id={set_id}&focus_item=wl_001"
    )


def test_text_focus_item_degrades_cleanly_when_not_in_excerpt(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "text", "item_id": "d_01"}])

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page("de", "spanish", "ES-L-0001-2026-S01", "text", "comparison", set_id=set_id, focus_item="d_02")

    assert page is not None
    assert page["player"]["mode"] == "text"
    assert page["player"]["client_state"]["focusedItemId"] is None
    assert page["player"]["set_notice"]["status"] == "focus-missed"


def test_text_player_route_renders_productive_runtime(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "text", "item_id": "d_01"}])

    player_set_app.config["TEST_AUTH_USER"] = "alice"
    player_set_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = player_set_app.test_client()
    response = client.get(
        f"/de/research/spanish/player/ES-L-0001-2026-S01/text?source=comparison&set_id={set_id}&focus_item=d_01"
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-player-root' in html
    assert 'Satzliste' in html
    assert 'data-player-focus-item="d_01"' in html
    assert 'data-player-focus-item="d_02"' not in html
    assert '/de/research/spanish/player/ES-L-0001-2026-S01/text/audio.mp3' in html


def test_text_compare_builds_productive_compare_view_model(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(
            owner_user_id="user-1",
            items=[
                {"task": "text", "item_id": "d_01"},
                {"task": "text", "item_id": "d_02"},
            ],
        )

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "text",
            "comparison",
            compare_session_id="ES-N-0001-2026-S01",
            set_id=set_id,
            focus_item="d_02",
        )

    assert page is not None
    assert page["player"]["mode"] == "text"
    assert page["player"]["compare"]["is_ready"] is True
    assert page["player"]["compare"]["mode"] == "sequence"
    assert [row["item_id"] for row in page["player"]["compare"]["rows"]] == ["d_01", "d_02"]
    assert page["player"]["client_state"]["compareReady"] is True
    assert page["player"]["client_state"]["focusedItemId"] == "d_02"
    assert page["player"]["secondary"]["session_id"] == "ES-N-0001-2026-S01"


def test_text_compare_matches_rows_by_stable_item_id_not_bundle_order(player_set_app: Flask) -> None:
    runtime_root = Path(os.environ["PROMAT_RUNTIME_ROOT"])
    _write_text_artifacts(
        runtime_root,
        "spanish",
        "ES-N-0001-2026-S01",
        "ES-N-0001",
        [
            {"item_id": "d_02", "item_number": "D2", "text": "Mañana vuelvo a casa después del trabajo."},
            {"item_id": "d_01", "item_number": "D1", "text": "Hoy miro el reloj con calma antes de salir."},
        ],
    )

    with player_set_app.app_context():
        set_id = _create_set(
            owner_user_id="user-1",
            items=[
                {"task": "text", "item_id": "d_01"},
                {"task": "text", "item_id": "d_02"},
            ],
        )

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "text",
            "comparison",
            compare_session_id="ES-N-0001-2026-S01",
            set_id=set_id,
        )

    assert page is not None
    rows = page["player"]["compare"]["rows"]
    assert [row["item_id"] for row in rows] == ["d_01", "d_02"]
    assert rows[0]["secondary"]["start_ms"] == 2700
    assert rows[1]["secondary"]["start_ms"] == 1200


def test_text_compare_filters_rows_to_active_set_excerpt(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "text", "item_id": "d_02"}])

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "text",
            "comparison",
            compare_session_id="ES-N-0001-2026-S01",
            set_id=set_id,
            focus_item="d_02",
        )

    assert page is not None
    assert [row["item_id"] for row in page["player"]["compare"]["rows"]] == ["d_02"]
    assert page["player"]["client_state"]["focusedItemId"] == "d_02"


def test_text_compare_marks_missing_secondary_items_without_breaking_view(player_set_app: Flask) -> None:
    runtime_root = Path(os.environ["PROMAT_RUNTIME_ROOT"])
    _write_text_artifacts(
        runtime_root,
        "spanish",
        "ES-N-0001-2026-S01",
        "ES-N-0001",
        [{"item_id": "d_01", "item_number": "D1", "text": "Hoy miro el reloj con calma antes de salir."}],
    )

    with player_set_app.app_context():
        set_id = _create_set(
            owner_user_id="user-1",
            items=[
                {"task": "text", "item_id": "d_01"},
                {"task": "text", "item_id": "d_02"},
            ],
        )

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "text",
            "comparison",
            compare_session_id="ES-N-0001-2026-S01",
            set_id=set_id,
        )

    assert page is not None
    assert page["player"]["compare"]["is_ready"] is True
    rows = page["player"]["compare"]["rows"]
    assert rows[1]["item_id"] == "d_02"
    assert rows[1]["secondary"]["is_available"] is False
    assert rows[1]["secondary"]["missing_label"] == "Kein Clip in dieser Session"
    assert page["player"]["controls_hint"] is not None


def test_text_compare_keeps_available_side_when_secondary_split_download_is_missing(player_set_app: Flask) -> None:
    runtime_root = Path(os.environ["PROMAT_RUNTIME_ROOT"])
    _write_text_artifacts(
        runtime_root,
        "spanish",
        "ES-N-0001-2026-S01",
        "ES-N-0001",
        [
            {"item_id": "d_01", "item_number": "D1", "text": "Hoy miro el reloj con calma antes de salir."},
            {"item_id": "d_02", "item_number": "D2", "text": "Mañana vuelvo a casa después del trabajo."},
        ],
        split_item_ids={"d_01"},
    )

    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "text",
            "comparison",
            compare_session_id="ES-N-0001-2026-S01",
        )

    assert page is not None
    rows = page["player"]["compare"]["rows"]
    assert rows[0]["secondary"]["download_href"] is not None
    assert rows[1]["secondary"]["is_available"] is True
    assert rows[1]["secondary"]["download_href"] is None


def test_text_compare_degrades_cleanly_for_invalid_compare_session(player_set_app: Flask) -> None:
    with player_set_app.test_request_context():
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_player_page(
            "de",
            "spanish",
            "ES-L-0001-2026-S01",
            "text",
            "comparison",
            compare_session_id="ES-UNKNOWN-2026-S01",
            focus_item="d_01",
        )

    assert page is not None
    assert page["player"]["mode"] == "text"
    assert page["player"]["compare"]["is_ready"] is False
    assert page["player"]["controls_hint"] is not None
    assert page["player"]["client_state"]["focusedItemId"] == "d_01"


def test_text_compare_route_renders_handoff_from_comparison(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(
            owner_user_id="user-1",
            items=[
                {"task": "text", "item_id": "d_01"},
                {"task": "text", "item_id": "d_02"},
            ],
        )

    player_set_app.config["TEST_AUTH_USER"] = "alice"
    player_set_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = player_set_app.test_client()
    response = client.get(
        f"/de/research/spanish/player/ES-L-0001-2026-S01/text?source=comparison&set_id={set_id}&compare_session=ES-N-0001-2026-S01&focus_item=d_02"
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-player-compare-ready="true"' in html
    assert 'ES-N-0001-2026-S01' in html
    assert 'data-player-focus-item="d_02"' in html


def test_text_compare_route_from_phenomena_stays_single_without_compare_session(player_set_app: Flask) -> None:
    with player_set_app.app_context():
        set_id = _create_set(owner_user_id="user-1", items=[{"task": "text", "item_id": "d_01"}])

    player_set_app.config["TEST_AUTH_USER"] = "alice"
    player_set_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = player_set_app.test_client()
    response = client.get(
        f"/de/research/spanish/player/ES-L-0001-2026-S01/text?source=phenomena&set_id={set_id}&focus_item=d_01"
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-player-compare-ready="false"' in html
    assert 'data-player-focus-item="d_01"' in html
