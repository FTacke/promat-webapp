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
from app.extensions.sqlalchemy_ext import get_engine, init_engine, get_session
from app.research_presets import clear_research_preset_caches
from app.research_sessions import load_language_sessions, load_person_records
from app.research_sets import create_draft_set, replace_set_sessions, update_set_metadata
from app.research_views import build_comparison_page, _is_playable_audio_artifact
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


def _session_payload(
    person_id: str,
    session_id: str,
    tasks: tuple[str, ...],
    *,
    speaker_type: str = "learner",
    l1: str | None = "DE",
    l1_additional: str | None = "IT; EN",
    gender: str = "female",
    level_code: str | None = "B1",
    standard_variety: str | None = None,
    origin_country: str | None = None,
) -> dict[str, object]:
    return {
        "person_id": person_id,
        "session_id": session_id,
        "target_language": "es",
        "speaker_type": speaker_type,
        "l1": l1,
        "l1_additional": l1_additional,
        "gender": gender,
        "birth_year": 1998,
        "level_code": level_code,
        "level_self": level_code,
        "recording_year": 2026,
        "recording_date": "2026-03-10",
        "context": "baseline",
        "recorded_by": "Ana Romero",
        "notes": "test learner session",
        "standard_variety": standard_variety,
        "origin_country": origin_country,
        "tasks": [_task(task_type) for task_type in tasks],
    }


def _write_task_artifacts(
    runtime_root: Path,
    language_slug: str,
    session_id: str,
    person_id: str,
    task_key: str,
    items: list[dict[str, object]],
) -> None:
    session_dir = runtime_root / "data" / "sessions" / language_slug / session_id
    _write_binary(session_dir / "derived" / f"{task_key}.mp3")
    alignment_items: list[dict[str, object]] = []
    start_ms = 0
    for item in items:
      item_id = str(item["item_id"])
      item_number = str(item["item_number"])
      text = str(item["text"])
      split_relative = f"items/{task_key}/{item_id}.mp3"
      _write_binary(session_dir / split_relative)
      alignment_items.append(
          {
              "item_id": item_id,
              "item_number": item_number,
              "text": text,
              "start_ms": start_ms,
              "end_ms": start_ms + 900,
              "split_mp3": split_relative,
          }
      )
      start_ms += 1000

    _write_json(
        session_dir / "alignment" / f"{task_key}.json",
        {
            "session_id": session_id,
            "person_id": person_id,
            "task": task_key,
            "audio": {"full_mp3": f"derived/{task_key}.mp3"},
            "items": alignment_items,
        },
    )


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
                {"item_id": "qy_01", "item_number": "QY1", "group_id": "QY", "text": "El vaso esta lleno de vino ahora."},
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
                    "description": "Minimal preset for comparison tests.",
                    "language": "spanish",
                    "items": [
                        {"task": "wordlist", "item_id": "wl_001"},
                        {"task": "text", "item_id": "d_01"},
                    ],
                }
            ],
        },
    )

    session_one = "ES-L-0001-2026-S01"
    session_two = "ES-L-0002-2026-S01"
    session_native = "ES-N-0001-2026-S01"
    person_one = "ES-L-0001"
    person_two = "ES-L-0002"
    person_native = "ES-N-0001"
    _write_session(runtime_root, "spanish", session_one, _session_payload(person_one, session_one, ("wordlist", "text")))
    _write_session(runtime_root, "spanish", session_two, _session_payload(person_two, session_two, ("wordlist",)))
    _write_session(
        runtime_root,
        "spanish",
        session_native,
        _session_payload(
            person_native,
            session_native,
            ("wordlist",),
            speaker_type="native_speaker",
            l1=None,
            l1_additional=None,
            gender="male",
            level_code=None,
            standard_variety="castellano",
            origin_country="Spain",
        ),
    )

    _write_task_artifacts(
        runtime_root,
        "spanish",
        session_one,
        person_one,
        "wordlist",
        [{"item_id": "wl_001", "item_number": "1", "text": "mesa"}],
    )
    _write_task_artifacts(
        runtime_root,
        "spanish",
        session_one,
        person_one,
        "text",
        [{"item_id": "d_01", "item_number": "D1", "text": "Hoy miro el reloj con calma antes de salir."}],
    )
    _write_task_artifacts(
        runtime_root,
        "spanish",
        session_two,
        person_two,
        "wordlist",
        [{"item_id": "wl_001", "item_number": "1", "text": "mesa"}],
    )
    _write_task_artifacts(
        runtime_root,
        "spanish",
        session_native,
        person_native,
        "wordlist",
        [{"item_id": "wl_001", "item_number": "1", "text": "mesa"}],
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
def comparison_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Flask:
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
    app.config["TEST_RUNTIME_ROOT"] = runtime_root

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
    app.register_blueprint(public_blueprint)
    _clear_runtime_caches()
    yield app
    _clear_runtime_caches()


def test_build_comparison_page_exposes_session_catalog_and_filter_state(comparison_app: Flask) -> None:
    with comparison_app.test_request_context("/de/research/spanish/comparison?task=text"):
        g.user = None
        g.role = None
        page = build_comparison_page("de", "spanish", {"task": "text"})

    assert page is not None
    assert page["template"] == "pages/research_comparison.html"
    assert page["access"] == "protected"
    assert page["client_state"]["defaultViewTask"] == "text"
    assert page["client_state"]["sessionCatalog"][0]["availableItemIdsByTask"]["text"] == ["d_01"]
    assert page["client_state"]["sessionCatalog"][0]["genderKey"] == "female"
    assert page["client_state"]["sessionCatalog"][0]["targetCountryStayKey"] == "unknown"
    assert page["client_state"]["labels"]["materialPrompt"] == "Items auswählen"
    assert page["client_state"]["labels"]["moreFiltersLabel"] == "Weitere Filter"
    assert page["client_state"]["labels"]["speakerPluralLabel"] == "Sprecher:innen"
    assert page["client_state"]["labels"]["setSelectLabel"] == "Set wählen"
    assert page["client_state"]["labels"]["setSelectInfoText"] == "Sets lassen sich unter „Phänomene“ individuell erstellen und anpassen."
    assert page["client_state"]["labels"]["l1FilterLabel"] == "L1 wählen"
    assert page["client_state"]["labels"]["fullListLabel"] == "Alle Items"
    assert page["client_state"]["labels"]["fullTextLabel"] == "Ganzer Text"
    assert page["client_state"]["labels"]["downloadClip"] == "MP3 laden"
    assert page["client_state"]["materialPresets"][0]["presetId"] == "starter_preset"
    assert page["client_state"]["materialPresets"][0]["items"] == [
        {"task": "wordlist", "item_id": "wl_001"},
        {"task": "text", "item_id": "d_01"},
    ]

    learner_session = next(entry for entry in page["client_state"]["sessionCatalog"] if entry["sessionId"] == "ES-L-0001-2026-S01")
    native_session = next(entry for entry in page["client_state"]["sessionCatalog"] if entry["sessionId"] == "ES-N-0001-2026-S01")
    assert learner_session["l1BadgeLabel"] == "L1: DE"
    assert learner_session["l1AdditionalValues"] == ["IT", "EN"]
    assert learner_session["l1AdditionalValue"] == "IT, EN"
    assert native_session["speakerTypeLabel"] == "Native"
    assert native_session["standardVarietyValue"] == "Kastilisches Spanisch"
    assert native_session["detailValue"] == "Spanien"


def test_build_comparison_page_marks_requested_set_for_client_loading(comparison_app: Flask) -> None:
    with comparison_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish", source_preset_id="starter_preset")
        draft = replace_set_sessions(
            owner_user_id="user-1",
            set_id=draft.set_id,
            sessions=[{"session_id": "ES-L-0001-2026-S01"}, {"session_id": "ES-L-0002-2026-S01"}],
        )

    with comparison_app.test_request_context(f"/de/research/spanish/comparison?set_id={draft.set_id}"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_comparison_page("de", "spanish", {"set_id": draft.set_id})

    assert page is not None
    assert page["workspace"]["mode"] == "load-set"
    assert page["client_state"]["requestedSetId"] == draft.set_id
    assert page["client_state"]["labels"]["stateDraft"] == "Draft"
    assert page["client_state"]["labels"]["stateSaved"] == "Gespeichert"


def test_build_comparison_page_exposes_english_labels_for_migrated_workspace(comparison_app: Flask) -> None:
    with comparison_app.test_request_context("/en/research/spanish/comparison?task=text"):
        g.user = None
        g.role = None
        page = build_comparison_page("en", "spanish", {"task": "text"})

    assert page is not None
    assert page["content_header"]["intro"] == "Item-centered comparison workbench for speakers, sets, and directly usable split clips."
    assert page["client_state"]["labels"]["materialPrompt"] == "Select items"
    assert page["client_state"]["labels"]["setSelectLabel"] == "Choose set"
    assert page["client_state"]["labels"]["fullTextLabel"] == "Full text"
    assert page["client_state"]["labels"]["requestFailed"] == "Request failed."
    assert page["client_state"]["labels"]["nativeShort"] == "Native"


def test_build_comparison_page_includes_saved_custom_sets_in_material_options(comparison_app: Flask) -> None:
    with comparison_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish", source_preset_id="starter_preset")
        update_set_metadata(owner_user_id="user-1", set_id=draft.set_id, label="Mein Fokusset", state="saved")
        hidden_draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish")
        update_set_metadata(owner_user_id="user-1", set_id=hidden_draft.set_id, label="Nur Draft")

    with comparison_app.test_request_context("/de/research/spanish/comparison"):
        g.user = "alice"
        g.user_id = "user-1"
        g.role = None
        page = build_comparison_page("de", "spanish", {})

    assert page is not None
    option_labels = [entry["optionLabel"] for entry in page["client_state"]["materialPresets"]]
    assert "Starter · curated" in option_labels
    assert "Mein Fokusset · custom" in option_labels
    assert "Nur Draft · custom" not in option_labels


def test_comparison_route_redirects_to_login_without_auth(comparison_app: Flask) -> None:
    client = comparison_app.test_client()
    response = client.get("/de/research/spanish/comparison?task=wordlist")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login?next=/de/research/spanish/comparison?task%3Dwordlist"


def test_public_comparison_route_renders_dedicated_workspace(comparison_app: Flask) -> None:
    comparison_app.config["TEST_AUTH_USER"] = "alice"
    comparison_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = comparison_app.test_client()
    response = client.get("/de/research/spanish/comparison?task=wordlist")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "pm-comparison-state" in html
    assert "Items auswählen" in html
    assert "1 · Material wählen" not in html
    assert "2 · Sprecher:innen auswählen" not in html
    assert "Sprecher:innen auswählen" in html
    assert "Matrix" in html
    assert "Set wählen" in html
    assert "Sets lassen sich unter „Phänomene“ individuell erstellen und anpassen." in html
    assert "Phänomene wählen" not in html
    assert "data-comparison-material-controls" in html
    assert "data-comparison-material-preset-select" in html
    assert "data-comparison-filter-search" in html
    assert "data-comparison-level-filters" in html
    assert "data-comparison-filter-l1" in html
    assert "data-comparison-filter-gender" in html
    assert "data-comparison-filter-exposure" in html
    assert "Lernende" in html
    assert "Native Speaker" in html
    assert "Ausgewählt" in html
    assert "Verfügbar" not in html
    assert "data-comparison-learner-sessions" in html
    assert "data-comparison-native-sessions" in html
    assert "pm-comparison-session-group__title--selected" not in html
    assert "In Phänomene anpassen" not in html
    assert "Zum Vergleichen anmelden." not in html
    assert "data-comparison-set-summary" not in html
    assert "data-comparison-stop" not in html
    assert "data-comparison-playback-status" not in html
    assert "data-comparison-volume-value" in html


def test_comparison_topbar_language_switch_preserves_requested_set_and_task_query(comparison_app: Flask) -> None:
    with comparison_app.app_context():
        draft = create_draft_set(owner_user_id="user-1", corpus_language="spanish", source_preset_id="starter_preset")

    comparison_app.config["TEST_AUTH_USER"] = "alice"
    comparison_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = comparison_app.test_client()
    response = client.get(f"/de/research/spanish/comparison?set_id={draft.set_id}&task=text")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert f'href="/en/research/spanish/comparison?set_id={draft.set_id}&amp;task=text"' in html
    assert "data-comparison-rate-value" in html
    assert "data-comparison-status-actions" not in html
    assert "data-comparison-launcher" not in html
    assert "Geplante Oberfläche" not in html


def test_text_item_route_separates_playback_from_download(comparison_app: Flask) -> None:
    comparison_app.config["TEST_AUTH_USER"] = "alice"
    comparison_app.config["TEST_AUTH_USER_ID"] = "user-1"
    client = comparison_app.test_client()
    playback_response = client.get("/de/research/spanish/player/ES-L-0001-2026-S01/text/items/d_01.mp3")
    download_response = client.get("/de/research/spanish/player/ES-L-0001-2026-S01/text/items/d_01.mp3?download=1")

    assert playback_response.status_code == 200
    assert playback_response.mimetype == "audio/mpeg"
    assert "attachment;" not in (playback_response.headers.get("Content-Disposition") or "")

    assert download_response.status_code == 200
    assert download_response.mimetype == "audio/mpeg"
    assert "attachment;" in (download_response.headers.get("Content-Disposition") or "")


def test_zero_byte_split_clip_is_not_exposed_as_playable(comparison_app: Flask) -> None:
    runtime_root = Path(comparison_app.config["TEST_RUNTIME_ROOT"])
    zero_clip = runtime_root / "data" / "sessions" / "spanish" / "ES-L-0001-2026-S01" / "items" / "wordlist" / "wl_001.mp3"
    zero_clip.write_bytes(b"")
    _clear_runtime_caches()

    try:
        with comparison_app.test_request_context("/de/research/spanish/comparison"):
            g.user = None
            g.role = None
            page = build_comparison_page("de", "spanish", {})

        assert page is not None
        session = next(entry for entry in page["client_state"]["sessionCatalog"] if entry["sessionId"] == "ES-L-0001-2026-S01")
        assert "wl_001" not in session["availableItemIdsByTask"]["wordlist"]

        comparison_app.config["TEST_AUTH_USER"] = "alice"
        comparison_app.config["TEST_AUTH_USER_ID"] = "user-1"
        client = comparison_app.test_client()
        response = client.get("/de/research/spanish/player/ES-L-0001-2026-S01/wordlist/items/wl_001.mp3")
        assert response.status_code == 404
    finally:
        _write_binary(zero_clip)
        _clear_runtime_caches()


def test_non_mp3_split_clip_is_not_exposed_as_playable(comparison_app: Flask) -> None:
    runtime_root = Path(comparison_app.config["TEST_RUNTIME_ROOT"])
    invalid_clip = runtime_root / "data" / "sessions" / "spanish" / "ES-L-0001-2026-S01" / "items" / "wordlist" / "wl_001.mp3"
    invalid_clip.write_bytes(b"<html>not audio</html>")
    _clear_runtime_caches()

    try:
        with comparison_app.test_request_context("/de/research/spanish/comparison"):
            g.user = None
            g.role = None
            page = build_comparison_page("de", "spanish", {})

        assert page is not None
        session = next(entry for entry in page["client_state"]["sessionCatalog"] if entry["sessionId"] == "ES-L-0001-2026-S01")
        assert "wl_001" not in session["availableItemIdsByTask"]["wordlist"]

        comparison_app.config["TEST_AUTH_USER"] = "alice"
        comparison_app.config["TEST_AUTH_USER_ID"] = "user-1"
        client = comparison_app.test_client()
        response = client.get("/de/research/spanish/player/ES-L-0001-2026-S01/wordlist/items/wl_001.mp3")
        assert response.status_code == 404
    finally:
        _write_binary(invalid_clip)
        _clear_runtime_caches()