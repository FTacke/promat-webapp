from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
from flask import Flask, g


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

from app.config.data_conventions import build_person_id, build_session_id, parse_person_id, parse_session_id
from app import register_context_processors
from app.research_presets import clear_research_preset_caches
from app.research_views import build_player_page, build_recordings_page, build_speaker_profile_page, build_speakers_page
from app.routes.public import blueprint as public_blueprint
from app.research_sessions import (
    load_language_sessions,
    load_person_records,
    matching_sessions_for_person,
    resolve_selected_session,
)


def _clear_research_caches() -> None:
    clear_research_preset_caches()
    load_language_sessions.cache_clear()
    load_person_records.cache_clear()


def _write_minimal_research_player_config(runtime_root: Path) -> None:
    base_dir = runtime_root / "data" / "config" / "research_player" / "spanish"
    task_catalog_dir = base_dir / "task_catalogs"
    task_catalog_dir.mkdir(parents=True, exist_ok=True)

    (task_catalog_dir / "wordlist.json").write_text(
        json.dumps(
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
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (task_catalog_dir / "text.json").write_text(
        json.dumps(
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
                    {"item_id": "d_01", "item_number": "D1", "group_id": "D", "text": "Hoy miro el reloj con calma antes de salir."},
                    {"item_id": "qy_01", "item_number": "QY1", "group_id": "QY", "text": "El vaso esta lleno de vino ahora."},
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (base_dir / "player_config.json").write_text(
        json.dumps(
            {
                "language": "spanish",
                "text": {"default_render_mode": "sentence_list", "display_label": "Satzliste"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


@pytest.fixture
def runtime_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "data" / "sessions" / "spanish").mkdir(parents=True, exist_ok=True)
    (tmp_path / "public").mkdir(parents=True, exist_ok=True)
    _write_minimal_research_player_config(tmp_path)

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(tmp_path))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(tmp_path / "public"))

    _clear_research_caches()
    yield tmp_path
    _clear_research_caches()


@pytest.fixture
def url_app() -> Flask:
    app_root = Path(__file__).resolve().parents[1]
    app = Flask(
        __name__,
        template_folder=str(app_root / "templates"),
        static_folder=str(app_root / "static"),
    )
    app.config["SERVER_NAME"] = "promat.test"
    register_context_processors(app)

    @app.before_request
    def _set_test_auth_context() -> None:
        g.user = None
        g.role = None

    app.register_blueprint(public_blueprint)
    return app


def _write_session(runtime_root: Path, language_slug: str, session_id: str, payload: dict[str, object]) -> None:
    session_dir = runtime_root / "data" / "sessions" / language_slug / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "metadata.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_session_file(runtime_root: Path, language_slug: str, session_id: str, relative_path: str, content: bytes | str) -> None:
    file_path = runtime_root / "data" / "sessions" / language_slug / session_id / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        file_path.write_bytes(content)
        return
    file_path.write_text(content, encoding="utf-8")


def _minimal_mp3_bytes() -> bytes:
    return b"ID3\x04\x00\x00\x00\x00\x00\x00\xff\xfb\x90\x64" + (b"\x00" * 256)


def _write_wordlist_player_artifacts(runtime_root: Path, language_slug: str, session_id: str, person_id: str) -> None:
    payload = {
        "session_id": session_id,
        "person_id": person_id,
        "task": "wordlist",
        "audio": {"full_mp3": "derived/wordlist.mp3"},
        "items": [
            {
                "item_id": "wl_001",
                "item_number": "1",
                "text": "mesa",
                "start_ms": 500,
                "end_ms": 1200,
                "split_mp3": "items/wordlist/wl_001.mp3",
            },
            {
                "item_id": "wl_002",
                "item_number": "2",
                "text": "reloj",
                "start_ms": 1500,
                "end_ms": 2400,
                "split_mp3": "items/wordlist/wl_002.mp3",
            },
        ],
    }
    _write_session_file(runtime_root, language_slug, session_id, "alignment/wordlist.json", json.dumps(payload, indent=2) + "\n")
    _write_session_file(runtime_root, language_slug, session_id, "derived/wordlist.mp3", _minimal_mp3_bytes())
    _write_session_file(runtime_root, language_slug, session_id, "items/wordlist/wl_001.mp3", _minimal_mp3_bytes())
    _write_session_file(runtime_root, language_slug, session_id, "items/wordlist/wl_002.mp3", _minimal_mp3_bytes())


def _write_text_player_artifacts(runtime_root: Path, language_slug: str, session_id: str, person_id: str) -> None:
    payload = {
        "session_id": session_id,
        "person_id": person_id,
        "task": "text",
        "audio": {"full_mp3": "derived/text.mp3"},
        "items": [
            {
                "item_id": "d_01",
                "item_number": "D1",
                "text": "Hoy miro el reloj con calma antes de salir.",
                "start_ms": 1200,
                "end_ms": 2600,
                "split_mp3": "items/text/d_01.mp3",
            },
            {
                "item_id": "qy_01",
                "item_number": "QY1",
                "text": "El vaso esta lleno de vino ahora.",
                "start_ms": 2900,
                "end_ms": 4500,
                "split_mp3": "items/text/qy_01.mp3",
            },
        ],
    }
    _write_session_file(runtime_root, language_slug, session_id, "alignment/text.json", json.dumps(payload, indent=2) + "\n")
    _write_session_file(runtime_root, language_slug, session_id, "derived/text.mp3", _minimal_mp3_bytes())
    _write_session_file(runtime_root, language_slug, session_id, "items/text/d_01.mp3", _minimal_mp3_bytes())
    _write_session_file(runtime_root, language_slug, session_id, "items/text/qy_01.mp3", _minimal_mp3_bytes())


def _write_connected_text_catalog(runtime_root: Path) -> None:
    base_dir = runtime_root / "data" / "config" / "research_player" / "spanish"
    (base_dir / "task_catalogs" / "text.json").write_text(
        json.dumps(
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
                        "group_id": "D",
                        "text": "Hoy miro el reloj con calma antes de salir.",
                        "text_container_id": "story_01",
                        "text_order_index": 1,
                        "paragraph_break_before": True,
                        "paragraph_id": "p1",
                    },
                    {
                        "item_id": "qy_01",
                        "item_number": "QY1",
                        "group_id": "QY",
                        "text": "El vaso esta lleno de vino ahora.",
                        "text_container_id": "story_01",
                        "text_order_index": 2,
                        "paragraph_break_before": True,
                        "paragraph_id": "p2",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _task(task_type: str) -> dict[str, str]:
    return {
        "task_type": task_type,
        "label": task_type,
        "source_file": f"source/{task_type}.wav",
        "alignment_file": f"alignment/{task_type}.TextGrid",
    }


def _learner_payload(
    person_id: str,
    session_id: str,
    recording_year: int,
    recording_date: str,
    level_code: str,
    context: str,
    task_types: tuple[str, ...],
    target_language: str = "es",
    exposure_entries: list[dict[str, object]] | None = None,
    stays_in_target_country: bool | None = True,
) -> dict[str, object]:
    return {
        "person_id": person_id,
        "session_id": session_id,
        "target_language": target_language,
        "speaker_type": "learner",
        "l1": "DE",
        "mother_l1": "DE",
        "father_l1": "PL",
        "additional_languages": ["English", "French"],
        "gender": "female",
        "birth_year": 1998,
        "current_region": "Berlin, Germany",
        "childhood_region": "Saxony, Germany",
        "level_code": level_code,
        "level_self": level_code,
        "recording_year": recording_year,
        "recording_date": recording_date,
        "context": context,
        "recorded_by": "Ana Romero",
        "stays_in_target_country": stays_in_target_country,
        "exposure_entries": exposure_entries or [],
        "notes": "test learner session",
        "tasks": [_task(task_type) for task_type in task_types],
    }


def _native_payload(person_id: str, session_id: str, recording_date: str) -> dict[str, object]:
    recording_year = int(recording_date[:4])
    return {
        "person_id": person_id,
        "session_id": session_id,
        "target_language": "es",
        "speaker_type": "native_speaker",
        "gender": "male",
        "birth_year": 1992,
        "origin_region": "Castile and Leon",
        "origin_country": "Spain",
        "standard_variety": "es_std",
        "level_code": None,
        "level_self": None,
        "recording_year": recording_year,
        "recording_date": recording_date,
        "context": "baseline",
        "recorded_by": "Ana Romero",
        "notes": "test native session",
        "tasks": [_task("wordlist"), _task("text")],
    }


def test_person_and_session_id_helpers_round_trip() -> None:
    person_id = build_person_id("es", "learner", 12)
    session_id = build_session_id(person_id, 2027, 2)

    assert person_id == "ES-L-0012"
    assert session_id == "ES-L-0012-2027-S02"
    assert parse_person_id(person_id) is not None
    assert parse_session_id(session_id) is not None
    assert parse_session_id(session_id).person_id == person_id


def test_load_person_records_aggregates_multi_session_person(runtime_env: Path) -> None:
    person_id = "ES-L-0001"
    older_session = "ES-L-0001-2026-S01"
    newer_session = "ES-L-0001-2027-S02"

    _write_session(
        runtime_env,
        "spanish",
        older_session,
        _learner_payload(
            person_id=person_id,
            session_id=older_session,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A1",
            context="baseline",
            task_types=("wordlist",),
        ),
    )
    _write_session(
        runtime_env,
        "spanish",
        newer_session,
        _learner_payload(
            person_id=person_id,
            session_id=newer_session,
            recording_year=2027,
            recording_date="2027-03-12",
            level_code="A2",
            context="follow_up",
            task_types=("wordlist", "text", "interview"),
        ),
    )

    people = load_person_records("spanish")

    assert len(people) == 1
    person = people[0]
    assert person.person_id == person_id
    assert person.session_count == 2
    assert person.latest_session.session_id == newer_session
    assert person.level_codes == ("A1", "A2")
    assert person.recording_years == (2026, 2027)
    assert person.available_task_keys == ("wordlist", "text", "interview")


def test_matching_sessions_and_selected_resolution_are_session_based(runtime_env: Path) -> None:
    person_id = "ES-L-0001"
    baseline_session = "ES-L-0001-2026-S01"
    follow_up_session = "ES-L-0001-2027-S02"

    _write_session(
        runtime_env,
        "spanish",
        baseline_session,
        _learner_payload(
            person_id=person_id,
            session_id=baseline_session,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A1",
            context="baseline",
            task_types=("wordlist",),
        ),
    )
    _write_session(
        runtime_env,
        "spanish",
        follow_up_session,
        _learner_payload(
            person_id=person_id,
            session_id=follow_up_session,
            recording_year=2027,
            recording_date="2027-03-12",
            level_code="A2",
            context="follow_up",
            task_types=("wordlist", "text"),
        ),
    )

    person = load_person_records("spanish")[0]
    matched_sessions = matching_sessions_for_person(person, {"level": "A1"})

    assert [session.session_id for session in matched_sessions] == [baseline_session]
    assert resolve_selected_session(person, preferred_session_ids=[baseline_session]).session_id == baseline_session
    assert resolve_selected_session(person, requested_session_id=follow_up_session).session_id == follow_up_session


def test_native_person_with_multiple_sessions_raises(runtime_env: Path) -> None:
    person_id = "ES-N-0001"
    _write_session(runtime_env, "spanish", "ES-N-0001-2026-S01", _native_payload(person_id, "ES-N-0001-2026-S01", "2026-03-10"))
    _write_session(runtime_env, "spanish", "ES-N-0001-2027-S02", _native_payload(person_id, "ES-N-0001-2027-S02", "2027-03-10"))

    with pytest.raises(ValueError, match="native_speaker person_id must map to exactly one session"):
        load_person_records("spanish")


def test_speakers_cards_use_person_primary_and_no_match_note(runtime_env: Path, url_app: Flask) -> None:
    baseline_session = "ES-L-0001-2026-S01"
    follow_up_session = "ES-L-0001-2027-S02"

    _write_session(
        runtime_env,
        "spanish",
        baseline_session,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=baseline_session,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A1",
            context="baseline",
            task_types=("wordlist",),
        ),
    )
    _write_session(
        runtime_env,
        "spanish",
        follow_up_session,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=follow_up_session,
            recording_year=2027,
            recording_date="2027-03-12",
            level_code="A2",
            context="follow_up",
            task_types=("wordlist", "text", "interview"),
        ),
    )

    with url_app.test_request_context():
        page = build_speakers_page("de", "spanish", {"level": "A1"})

    assert len(page["cards"]) == 1
    card = page["cards"][0]
    assert card["person_id"] == "ES-L-0001"
    assert card["selected_session_id"] == baseline_session
    assert "match_note" not in card
    assert [task["label"] for task in card["task_links"]] == ["Wortliste"]


def test_profile_page_uses_profile_wording_and_structured_exposure(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0001-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text", "interview"),
            exposure_entries=[
                {"country": "Spain", "duration_months": 6, "type": "erasmus", "exposure_notes": "Austauschsemester in Madrid."},
                {"country": "Mexico", "duration_months": 2, "type": "travel", "exposure_notes": ""},
            ],
        ),
    )

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", "ES-L-0001", session_id)

    assert page is not None
    assert page["title"] == "Profil"
    assert page["content_header"]["title"] == "Profil"
    assert page["content_header"]["breadcrumbs"][-1]["label"] == "Profil"
    assert page["person_section"]["title"] == "Profildaten"
    assert page["content_header"]["intro"] == "Profil mit Personendaten und allen zugehörigen Sessions und Aufzeichnungen."
    assert page["profile_header"]["session_count_label"] == "Zugeordnete Sessions"
    assert page["profile_header"]["session_count_value"] == 1

    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Sprachaufenthalte")
    assert [entry["text"] for entry in exposure_row["entries"]] == [
        "Spain · 6 Monate · Erasmus",
        "Mexico · 2 Monate · Reise",
    ]
    assert [entry["note"] for entry in exposure_row["entries"]] == ["Austauschsemester in Madrid.", ""]
    assert [task["key"] for task in page["sessions_section"]["cards"][0]["tasks"]] == ["wordlist", "text", "interview"]
    assert all(not task["is_disabled"] for task in page["sessions_section"]["cards"][0]["tasks"])


def test_profile_page_keeps_selection_and_accent_bound_to_each_session(runtime_env: Path, url_app: Flask) -> None:
    person_id = "ES-L-0010"
    a1_session = "ES-L-0010-2026-S01"
    b2_session = "ES-L-0010-2027-S02"

    _write_session(
        runtime_env,
        "spanish",
        a1_session,
        _learner_payload(
            person_id=person_id,
            session_id=a1_session,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A1",
            context="baseline",
            task_types=("wordlist", "text"),
        ),
    )
    _write_session(
        runtime_env,
        "spanish",
        b2_session,
        _learner_payload(
            person_id=person_id,
            session_id=b2_session,
            recording_year=2027,
            recording_date="2027-03-12",
            level_code="B2",
            context="follow_up",
            task_types=("wordlist", "text"),
        ),
    )

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", person_id, b2_session)

    assert page is not None
    cards = {card["session_id"]: card for card in page["sessions_section"]["cards"]}
    assert cards[a1_session]["accent_modifier"] == "a1"
    assert cards[a1_session]["is_selected"] is False
    assert cards[b2_session]["accent_modifier"] == "b2"
    assert cards[b2_session]["is_selected"] is True
    assert cards[b2_session]["selected_label"] == "Ausgewählt"


def test_profile_page_supports_single_exposure_entry_without_note(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0002-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0002",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A2",
            context="baseline",
            task_types=("wordlist", "text"),
            exposure_entries=[
                {"country": "Spain", "duration_months": 3, "type": "study", "exposure_notes": ""},
            ],
        ),
    )

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", "ES-L-0002", session_id)

    assert page is not None
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Sprachaufenthalte")
    assert exposure_row["entries"] == [{"text": "Spain · 3 Monate · Studium", "note": ""}]


def test_profile_page_uses_compact_exposure_fallback_when_no_entries_exist(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0004-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0004",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A1",
            context="baseline",
            task_types=("wordlist",),
            exposure_entries=[],
            stays_in_target_country=False,
        ),
    )

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", "ES-L-0004", session_id)

    assert page is not None
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Sprachaufenthalte")
    assert exposure_row["kind"] == "exposure"
    assert exposure_row["value"] == "Keine erfassten Sprachaufenthalte"
    assert "entries" not in exposure_row


def test_profile_page_preserves_long_exposure_note_for_wrapping(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0005-2026-S01"
    long_note = "Längerer Freitext zur Reise, der bewusst mehrere Wortgruppen enthält und in schmaleren Layouts sauber umbrechen soll."
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0005",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B2",
            context="baseline",
            task_types=("wordlist", "text"),
            exposure_entries=[
                {"country": "Spain", "duration_months": 4, "type": "work", "exposure_notes": long_note},
            ],
        ),
    )

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", "ES-L-0005", session_id)

    assert page is not None
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Sprachaufenthalte")
    assert exposure_row["entries"] == [{"text": "Spain · 4 Monate · Arbeit", "note": long_note}]


def test_research_profile_renders_exposure_entries_with_grouped_markup(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0006-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0006",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text"),
            exposure_entries=[
                {"country": "Spain", "duration_months": 5, "type": "study", "exposure_notes": "Semester in Salamanca."},
                {"country": "Mexico", "duration_months": 1, "type": "travel", "exposure_notes": ""},
            ],
        ),
    )

    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/speakers/ES-L-0006?session={session_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-profile-metadata__list pm-profile-metadata__list--exposure' in html
    assert html.count('pm-profile-metadata__list-item pm-profile-metadata__list-item--exposure') == 2
    assert 'pm-profile-metadata__entry pm-profile-metadata__entry--exposure' in html
    assert 'pm-profile-metadata__entry-line pm-profile-metadata__entry-summary' in html
    assert 'pm-profile-metadata__note pm-profile-metadata__entry-note' in html
    assert 'Semester in Salamanca.' in html


def test_research_overview_renders_shared_sidebar_header_and_single_header_nav(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/research")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert html.count('class="promat-topbar__nav"') == 1
    assert 'promat-topbar__row--secondary' not in html
    assert 'class="app-shell app-shell--inner"' in html
    assert 'data-page="research"' in html
    assert 'data-context-mode="none"' in html
    assert 'promat-panel__context' in html
    assert 'promat-panel__section-header' in html
    assert 'pm-icon-mask--section' in html
    assert '>Forschung<' in html
    assert 'Korpus wählen' in html
    assert 'class="pm-breadcrumb' not in html


def test_research_overview_renders_corpus_titles_and_data_driven_session_counts(runtime_env: Path, url_app: Flask) -> None:
    spanish_person_id = build_person_id("es", "learner", 1)
    spanish_session_one = build_session_id(spanish_person_id, 2026, 1)
    spanish_session_two = build_session_id(spanish_person_id, 2027, 2)
    english_person_id = build_person_id("en", "learner", 1)
    english_session_one = build_session_id(english_person_id, 2026, 1)

    _write_session(
        runtime_env,
        "spanish",
        spanish_session_one,
        _learner_payload(
            person_id=spanish_person_id,
            session_id=spanish_session_one,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A2",
            context="baseline",
            task_types=("wordlist", "text"),
            target_language="es",
        ),
    )
    _write_session(
        runtime_env,
        "spanish",
        spanish_session_two,
        _learner_payload(
            person_id=spanish_person_id,
            session_id=spanish_session_two,
            recording_year=2027,
            recording_date="2027-03-12",
            level_code="B1",
            context="follow_up",
            task_types=("wordlist", "text", "interview"),
            target_language="es",
        ),
    )
    _write_session(
        runtime_env,
        "english",
        english_session_one,
        _learner_payload(
            person_id=english_person_id,
            session_id=english_session_one,
            recording_year=2026,
            recording_date="2026-04-05",
            level_code="B2",
            context="baseline",
            task_types=("wordlist",),
            target_language="en",
        ),
    )

    client = url_app.test_client()
    response = client.get("/de/research")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Spanisch-Korpus' in html
    assert 'Französisch-Korpus' in html
    assert 'Deutsch-Korpus' in html
    assert 'Englisch-Korpus' in html
    assert 'Kontrolliert angelegtes Korpus zur Lernendenaussprache mit Wortliste, Satzliste und Interview als vergleichbaren Erhebungsformaten.' in html
    assert 'Aktuell 2 erfasste Learner-Sessions im Bestand.' in html
    assert 'Aktuell 1 erfasste Learner-Session im Bestand.' in html
    assert 'Aktuell keine erfassten Learner-Sessions im Bestand.' in html


def test_project_page_uses_inner_shell_with_section_sidebar_header(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/project")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert html.count('class="promat-topbar__nav"') == 1
    assert 'promat-topbar__row--secondary' not in html
    assert 'class="app-shell app-shell--inner"' in html
    assert 'data-page="project"' in html
    assert 'data-context-mode="section"' in html
    assert 'promat-panel__inner--section' in html
    assert 'promat-panel__section-header' in html
    assert 'Projekt' in html
    assert 'class="pm-breadcrumb' not in html


def test_research_language_root_renders_shared_sidebar_header_and_language_context(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/research/spanish")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert html.count('class="promat-topbar__nav"') == 1
    assert 'promat-topbar__row--secondary' not in html
    assert 'class="app-shell app-shell--inner"' in html
    assert 'data-context-mode="language"' in html
    assert 'promat-panel__context' in html
    assert 'promat-panel__inner--language' in html
    assert 'promat-panel__language-header' in html
    assert 'promat-panel__section-header' in html
    assert 'pm-icon-mask--section' in html
    assert 'pm-icon-mask--back' in html
    assert '>Forschung<' in html
    assert 'href="/de/research"' in html
    assert 'aria-label="Zur Korpusauswahl"' in html
    assert 'Spanisch' in html
    assert 'promat-panel__context-line--accent' not in html
    assert 'pm-grid--selection' not in html
    assert 'href="/de/research/spanish/design"' in html
    assert 'href="/de/research/spanish/speakers"' in html
    assert 'href="/de/research/spanish/recordings"' in html
    assert 'Überblick' in html
    assert 'class="pm-breadcrumb pm-breadcrumb--mobile-only"' in html
    assert 'data-depth="2"' in html
    assert 'aria-current="page">Spanisch</span>' in html
    assert 'Vergleich öffnen →' in html
    assert 'Phänomene öffnen →' in html
    assert 'Sprecher:innen erschließt den Bestand personbezogen.' in html


def test_teaching_overview_keeps_language_selection_label(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/teaching")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Sprache wählen' in html
    assert 'Korpus wählen' not in html


def test_teaching_language_root_uses_inner_shell_with_language_sidebar_context(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/teaching/spanish")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert html.count('class="promat-topbar__nav"') == 1
    assert 'promat-topbar__row--secondary' not in html
    assert 'class="app-shell app-shell--inner"' in html
    assert 'data-page="teaching"' in html
    assert 'data-context-mode="language"' in html
    assert 'promat-panel__context' in html
    assert 'promat-panel__inner--language' in html
    assert 'promat-panel__language-header' in html
    assert 'promat-panel__section-header' in html
    assert 'pm-icon-mask--section' in html
    assert 'pm-icon-mask--back' in html
    assert '>Unterricht<' in html
    assert 'href="/de/teaching"' in html
    assert 'aria-label="Zur Sprachwahl"' in html
    assert 'promat-panel__context-line--accent' not in html
    assert 'Spanisch' in html
    assert 'class="pm-breadcrumb pm-breadcrumb--mobile-only"' in html
    assert 'data-depth="2"' in html
    assert 'aria-current="page">Spanisch</span>' in html


def test_sample_page_uses_shared_inner_shell_renderer(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/sample")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert html.count('class="promat-topbar__nav"') == 1
    assert 'promat-topbar__row--secondary' not in html
    assert 'class="app-shell app-shell--inner"' in html
    assert 'data-page="sample"' in html
    assert 'data-context-mode="none"' in html
    assert 'promat-panel__context' in html
    assert 'promat-panel__section-header' in html
    assert 'pm-icon-mask--section' in html
    assert '>Sample<' in html
    assert 'pages/sample_page.html' not in html
    assert 'class="pm-breadcrumb' not in html


def test_project_detail_page_uses_mobile_only_breadcrumb_for_depth_two(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/project/research-design")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'class="pm-breadcrumb pm-breadcrumb--mobile-only"' in html
    assert 'data-depth="2"' in html
    assert 'href="/de/project"' in html
    assert 'aria-current="page">Forschungsdesign</span>' in html


def test_research_detail_page_uses_full_breadcrumb_from_depth_three(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/research/spanish/design")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'class="pm-breadcrumb"' in html
    assert 'pm-breadcrumb--mobile-only' not in html
    assert 'data-depth="3"' in html
    assert 'href="/de/research"' in html
    assert 'href="/de/research/spanish"' in html
    assert 'aria-current="page">Design</span>' in html
    assert '>Zusammenfassung<' not in html


def test_sample_page_reflects_current_landing_and_corpus_cards(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/sample")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Zur Forschung →' in html
    assert 'Zum Unterricht →' in html
    assert 'Spanisch-Korpus' in html
    assert 'Französisch-Korpus' in html
    assert 'Korpus öffnen →' in html
    assert 'Materialien öffnen →' in html
    assert 'Aktuell keine erfassten Learner-Sessions im Bestand.' in html


def test_sample_page_uses_current_research_component_patterns(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/sample")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-speaker-card__footer-section--recordings' in html
    assert 'pm-speaker-card__footer-section--actions' in html
    assert 'pm-research-inline-action--task' in html
    assert 'pm-speaker-task-link' not in html
    assert 'pm-speaker-card__match' not in html
    assert 'pm-speaker-card--a1' in html
    assert 'pm-speaker-card--a2' in html
    assert 'pm-speaker-card--b1' in html
    assert 'pm-speaker-card--b2' in html
    assert 'pm-speaker-card--native' in html
    assert 'Aufzeichnung (Sprecher:in)' in html
    assert 'Chips, Badges und Action-Buttons' in html
    assert 'Task-Aktionen' in html
    assert 'pm-profile-session--a2 is-selected' in html
    assert 'pm-profile-session--native is-selected' in html
    assert 'Zugeordnete Sessions' in html
    assert 'Niveau / Varietät' not in html


def test_recordings_page_combines_session_and_person_in_leading_column(runtime_env: Path, url_app: Flask) -> None:
    learner_session = "ES-L-0001-2026-S01"
    native_session = "ES-N-0001-2026-S01"

    _write_session(
        runtime_env,
        "spanish",
        learner_session,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=learner_session,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A2",
            context="baseline",
            task_types=("wordlist", "text", "interview"),
        ),
    )
    _write_session(runtime_env, "spanish", native_session, _native_payload("ES-N-0001", native_session, "2026-03-11"))

    with url_app.test_request_context():
        page = build_recordings_page("de", "spanish", {"task": "wordlist"})

    assert page["columns"]["recording"] == "Aufzeichnung (Sprecher:in)"
    assert page["columns"]["context"] == "Niveau"
    assert page["columns"]["detail"] == "L1"
    first_row = page["results"][0]
    assert "session_secondary" not in first_row
    assert first_row["person_href"].endswith(f"/de/research/spanish/speakers/{first_row['person_id']}?session={first_row['session_id']}")


def test_recordings_route_uses_shared_task_action_buttons(runtime_env: Path, url_app: Flask) -> None:
    learner_session = "ES-L-0001-2026-S01"
    native_session = "ES-N-0001-2026-S01"

    _write_session(
        runtime_env,
        "spanish",
        learner_session,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=learner_session,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A2",
            context="baseline",
            task_types=("wordlist", "text", "interview"),
        ),
    )
    _write_session(runtime_env, "spanish", native_session, _native_payload("ES-N-0001", native_session, "2026-03-11"))

    client = url_app.test_client()
    response = client.get("/de/research/spanish/recordings?task=wordlist")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-research-inline-action--task' in html
    assert 'pm-speaker-task-link' not in html


def test_profile_header_shows_session_count_and_native_interview_disabled(runtime_env: Path, url_app: Flask) -> None:
    native_session = "ES-N-0001-2026-S01"
    _write_session(runtime_env, "spanish", native_session, _native_payload("ES-N-0001", native_session, "2026-03-11"))

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", "ES-N-0001", native_session)

    assert page is not None
    assert page["profile_header"]["session_count_label"] == "Zugeordnete Sessions"
    assert page["profile_header"]["session_count_value"] == 1
    tasks = page["sessions_section"]["cards"][0]["tasks"]
    assert [task["key"] for task in tasks] == ["wordlist", "text", "interview"]
    assert [task["is_disabled"] for task in tasks] == [False, False, True]
    assert tasks[-1]["state_label"] == "Nicht verfügbar"
    assert page["content_header"]["breadcrumb_mode"] == "all"
    assert [item["label"] for item in page["content_header"]["breadcrumbs"]] == [
        "Forschung",
        "Spanisch",
        "Sprecher:innen",
        "Profil",
    ]


def test_recordings_page_keeps_disabled_interview_panel_and_blank_native_columns(runtime_env: Path, url_app: Flask) -> None:
    native_session = "ES-N-0001-2026-S01"
    _write_session(runtime_env, "spanish", native_session, _native_payload("ES-N-0001", native_session, "2026-03-11"))

    with url_app.test_request_context():
        page = build_recordings_page("de", "spanish", {"task": "wordlist", "speaker_type": "native_speaker"})

    assert [panel["key"] for panel in page["task_panels"]] == ["wordlist", "text", "interview"]
    assert [panel["is_disabled"] for panel in page["task_panels"]] == [False, False, True]
    assert page["task_panels"][-1]["href"] is None
    native_row = page["results"][0]
    assert native_row["context_value"] == ""
    assert native_row["detail_value"] == ""


def test_player_page_builds_real_wordlist_view_and_disables_unimplemented_tasks(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0001-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text", "interview"),
        ),
    )
    _write_wordlist_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001")

    with url_app.test_request_context():
        page = build_player_page("de", "spanish", session_id, "wordlist", "recordings")

    assert page is not None
    assert page["template"] == "pages/research_player.html"
    assert page["player"]["mode"] == "wordlist"
    assert page["player"]["audio_href"].endswith(f"/de/research/spanish/player/{session_id}/wordlist/audio.mp3")
    assert page["player"]["items"][0]["download_href"].endswith(f"/de/research/spanish/player/{session_id}/wordlist/items/wl_001.mp3")
    assert [panel["key"] for panel in page["task_panels"]] == ["wordlist", "text", "interview"]
    assert page["task_panels"][0]["current"] is True
    assert page["task_panels"][1]["href"] is None
    assert page["task_panels"][1]["state_label"] == "Keine verarbeitbaren Player-Artefakte"
    assert page["origin_link"]["href"].endswith("/de/research/spanish/recordings?task=wordlist")
    assert page["summary_cards"][0]["session_id"] == session_id


def test_player_page_exposes_english_labels_for_migrated_wordlist_surface(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0001-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text", "interview"),
        ),
    )
    _write_wordlist_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001")

    with url_app.test_request_context():
        page = build_player_page("en", "spanish", session_id, "wordlist", "recordings")

    assert page is not None
    assert page["title"] == "Player"
    assert page["content_header"]["title"] == "Player"
    assert page["content_header"]["intro"] == "Audio workbench for one documented session and its available task types."
    assert page["player"]["audio_href"].endswith(f"/en/research/spanish/player/{session_id}/wordlist/audio.mp3")
    assert page["task_panels"][1]["state_label"] == "No playable artifacts"
    assert page["origin_link"]["href"].endswith("/en/research/spanish/recordings?task=wordlist")
    assert page["summary_cards"][0]["profile_label"] == "Profile"


def test_player_page_builds_material_bar_and_footer_actions(runtime_env: Path, url_app: Flask) -> None:
    primary_session_id = "ES-L-0001-2026-S01"
    compare_session_id = "ES-N-0001-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        primary_session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=primary_session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text", "interview"),
        ),
    )
    _write_session(runtime_env, "spanish", compare_session_id, _native_payload("ES-N-0001", compare_session_id, "2026-03-11"))
    _write_wordlist_player_artifacts(runtime_env, "spanish", primary_session_id, "ES-L-0001")
    _write_wordlist_player_artifacts(runtime_env, "spanish", compare_session_id, "ES-N-0001")

    with url_app.test_request_context():
        single_page = build_player_page("de", "spanish", primary_session_id, "wordlist", "recordings")
        compare_page = build_player_page(
            "de",
            "spanish",
            primary_session_id,
            "wordlist",
            "recordings",
            compare_session_id=compare_session_id,
        )

    assert single_page is not None
    assert single_page["title"] == "Player"
    assert single_page["content_header"]["title"] == "Player"
    assert [action["action"] for action in single_page["summary_cards"][0]["card_actions"]] == ["profile", "compare-add"]
    assert single_page["summary_cards"][0]["card_actions"][1]["label"] == "Vergleich"
    assert single_page["player"]["set_select"]["options"][0]["label"] == "Alle Items"

    assert compare_page is not None
    assert [action["action"] for action in compare_page["summary_cards"][0]["card_actions"]] == ["profile"]
    assert [action["action"] for action in compare_page["summary_cards"][1]["card_actions"]] == ["profile", "compare-remove"]


def test_player_route_uses_shared_material_choice_family(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0001-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text", "interview"),
        ),
    )
    _write_wordlist_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001")

    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/player/{session_id}/wordlist?source=recordings")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "pm-material-choice" in html
    assert "data-player-set-select" in html


def test_player_page_uses_running_text_for_explicit_connected_text_sources(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0001-2026-S01"
    _write_connected_text_catalog(runtime_env)
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text"),
        ),
    )
    _write_text_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001")

    with url_app.test_request_context():
        page = build_player_page("de", "spanish", session_id, "text", "recordings")

    assert page is not None
    assert page["player"]["mode"] == "text"
    assert page["player"]["source_kind"] == "text"
    assert page["player"]["render_mode"] == "running_text"
    assert page["player"]["primary_audio_mode"] == "full"
    assert page["player"]["render_modes"] is not None
    assert [option["key"] for option in page["player"]["render_modes"]["options"]] == ["sentence_list", "running_text"]
    assert len(page["player"]["text_blocks"]) == 2
    assert page["player"]["render_modes"]["options"][0]["href"].endswith(
        f"/de/research/spanish/player/{session_id}/text?source=recordings&render_mode=sentence_list"
    )


def test_player_page_accepts_explicit_sentence_list_override_for_connected_text_sources(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0001-2026-S01"
    _write_connected_text_catalog(runtime_env)
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text"),
        ),
    )
    _write_text_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001")

    with url_app.test_request_context():
        page = build_player_page("de", "spanish", session_id, "text", "recordings", render_mode="sentence_list")

    assert page is not None
    assert page["player"]["render_mode"] == "sentence_list"
    assert page["player"]["text_blocks"] == []
    assert page["player"]["client_state"]["singleViewHref"].endswith(
        f"/de/research/spanish/player/{session_id}/text?source=recordings&render_mode=sentence_list"
    )


def test_player_page_builds_compare_context_and_mode_switches(runtime_env: Path, url_app: Flask) -> None:
    primary_session_id = "ES-L-0001-2026-S01"
    compare_session_id = "ES-N-0001-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        primary_session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=primary_session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text"),
        ),
    )
    _write_session(runtime_env, "spanish", compare_session_id, _native_payload("ES-N-0001", compare_session_id, "2026-03-11"))
    _write_wordlist_player_artifacts(runtime_env, "spanish", primary_session_id, "ES-L-0001")
    _write_wordlist_player_artifacts(runtime_env, "spanish", compare_session_id, "ES-N-0001")

    with url_app.test_request_context():
        page = build_player_page(
            "de",
            "spanish",
            primary_session_id,
            "wordlist",
            "recordings",
            compare_session_id=compare_session_id,
        )

    assert page is not None
    assert page["player"]["compare"]["is_ready"] is True
    assert page["player"]["compare"]["mode"] == "sequence"
    assert page["player"]["secondary"]["session_id"] == compare_session_id
    assert page["player"]["compare"]["rows"][0]["secondary"]["item_id"] == "wl_001"
    assert page["summary_cards"][1]["session_id"] == compare_session_id
    assert page["summary_cards"][0]["profile_label"] == "Profil"
    assert page["summary_cards"][0]["session_switch"]["current_label"] == primary_session_id
    assert [action["action"] for action in page["summary_cards"][1]["card_actions"]] == ["profile", "compare-remove"]
    assert page["summary_cards"][1]["card_actions"][1]["label"] == "Vergleich entfernen"
    assert page["summary_cards"][1]["card_actions"][1]["href"].endswith(
        f"/de/research/spanish/player/{primary_session_id}/wordlist?source=recordings"
    )
    assert any(row["label"] == "Niveau" for row in page["summary_cards"][0]["rows"])
    assert all(row["label"] != "Explorator:in" for row in page["summary_cards"][0]["rows"])
    assert page["player"]["compare"]["sequence_toggle"]["label"] == "Beide abspielen"
    assert page["player"]["compare"]["sequence_toggle"]["enabled"] is True
    assert any(option["current"] for option in page["player"]["compare"]["switchers"]["compare"]["options"])
    assert page["player"]["client_state"]["compareOpen"] is True
    assert page["player"]["client_state"]["modeHrefs"]["manual"].endswith(
        f"/de/research/spanish/player/{primary_session_id}/wordlist?source=recordings&compare_session={compare_session_id}&compare_mode=manual"
    )
    assert page["player"]["client_state"]["modeHrefs"]["sequence"].endswith(
        f"/de/research/spanish/player/{primary_session_id}/wordlist?source=recordings&compare_session={compare_session_id}"
    )
    assert page["player"]["client_state"]["rateOptions"] == [0.5, 0.75, 1.0, 1.25, 1.5]


def test_player_page_supports_manual_compare_override(runtime_env: Path, url_app: Flask) -> None:
    primary_session_id = "ES-L-0001-2026-S01"
    compare_session_id = "ES-N-0001-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        primary_session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=primary_session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text"),
        ),
    )
    _write_session(runtime_env, "spanish", compare_session_id, _native_payload("ES-N-0001", compare_session_id, "2026-03-11"))
    _write_wordlist_player_artifacts(runtime_env, "spanish", primary_session_id, "ES-L-0001")
    _write_wordlist_player_artifacts(runtime_env, "spanish", compare_session_id, "ES-N-0001")

    with url_app.test_request_context():
        page = build_player_page(
            "de",
            "spanish",
            primary_session_id,
            "wordlist",
            "recordings",
            compare_session_id=compare_session_id,
            compare_mode="manual",
        )

    assert page is not None
    assert page["player"]["compare"]["mode"] == "manual"
    assert page["player"]["compare"]["sequence_toggle"]["enabled"] is False


def test_player_route_renders_wordlist_runtime_and_profile_back_link(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-N-0001-2026-S01"
    _write_session(runtime_env, "spanish", session_id, _native_payload("ES-N-0001", session_id, "2026-03-11"))
    _write_wordlist_player_artifacts(runtime_env, "spanish", session_id, "ES-N-0001")

    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/player/{session_id}/wordlist?source=profile")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-player-root' in html
    assert f'/de/research/spanish/player/{session_id}/wordlist/audio.mp3' in html
    assert f'/de/research/spanish/player/{session_id}/wordlist/items/wl_001.mp3' in html
    assert '>Zurück<' in html
    assert '>Profil<' in html
    assert 'Zurück zum Profil' not in html
    assert 'Explorator:in' not in html
    assert 'pm-player-panel--control-bar' in html
    assert 'pm-player-list pm-player-list--single' in html


def test_player_route_keeps_compare_optional_until_explicit_activation(runtime_env: Path, url_app: Flask) -> None:
    primary_session_id = "ES-L-0001-2026-S01"
    compare_session_id = "ES-N-0001-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        primary_session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=primary_session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text"),
        ),
    )
    _write_session(runtime_env, "spanish", compare_session_id, _native_payload("ES-N-0001", compare_session_id, "2026-03-11"))
    _write_wordlist_player_artifacts(runtime_env, "spanish", primary_session_id, "ES-L-0001")
    _write_wordlist_player_artifacts(runtime_env, "spanish", compare_session_id, "ES-N-0001")

    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/player/{primary_session_id}/wordlist?source=recordings")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-player-compare-open="false"' in html
    assert 'data-player-session-menu="primary"' in html
    assert 'data-player-session-menu="secondary"' in html
    assert '>Vergleich<' in html
    assert 'Vergleichssession wählen' in html
    assert 'data-player-speaker-card="secondary" hidden' in html
    assert 'data-player-nav-select' not in html
    assert 'data-player-sequence-toggle' not in html
    assert 'pm-player-panel--compare' not in html
    assert 'pm-player-material-strip__set-inline-label' in html
    assert 'pm-player-task-switch-title' not in html
    assert 'pm-comparison-set-select-block__label-row' not in html


def test_player_route_renders_compare_controls_and_secondary_audio(runtime_env: Path, url_app: Flask) -> None:
    primary_session_id = "ES-L-0001-2026-S01"
    compare_session_id = "ES-N-0001-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        primary_session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=primary_session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text"),
        ),
    )
    _write_session(runtime_env, "spanish", compare_session_id, _native_payload("ES-N-0001", compare_session_id, "2026-03-11"))
    _write_wordlist_player_artifacts(runtime_env, "spanish", primary_session_id, "ES-L-0001")
    _write_wordlist_player_artifacts(runtime_env, "spanish", compare_session_id, "ES-N-0001")

    client = url_app.test_client()
    response = client.get(
        f"/de/research/spanish/player/{primary_session_id}/wordlist?source=recordings&compare_session={compare_session_id}"
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-player-mode="sequence"' in html
    assert 'data-player-compare-open="true"' in html
    assert 'data-player-session-menu="primary"' in html
    assert 'data-player-session-menu="secondary"' in html
    assert 'data-player-volume' in html
    assert 'data-player-rate-slider' in html
    assert 'data-player-sequence-toggle' in html
    assert 'data-player-sequence-toggle checked' in html
    assert 'data-player-compare-panel' in html
    assert html.index('data-player-compare-panel') < html.index('data-player-sequence-toggle')
    assert f'/de/research/spanish/player/{compare_session_id}/wordlist/audio.mp3' in html
    assert 'Beide abspielen' in html
    assert html.count('Profil →') == 2
    assert 'Vergleich entfernen' in html
    assert f'href="/de/research/spanish/player/{primary_session_id}/wordlist?source=recordings"' in html
    assert 'Vergleich erscheint nur auf Desktop-Breiten' not in html
    assert 'data-player-activate-speaker' not in html
    assert 'pm-player-panel--control-bar' in html
    assert 'pm-player-summary-cards is-compare-ready' in html
    assert 'pm-player-control-bar__block--transport' in html
    assert 'pm-player-control-bar__block--settings' in html
    assert 'pm-player-transport-main' in html
    assert 'pm-player-list pm-player-list--compare' in html
    assert 'pm-player-list__header' in html
    assert 'pm-player-icon-button' in html
    assert 'data-player-rate-value' in html
    assert 'data-player-mode-hint' not in html
    assert 'Zwei ausgerichtete Wortlisten mit gemeinsamer Nummerierung und getrennten Downloads.' not in html
    assert '1.75×' not in html
    assert '2.00×' not in html


def test_player_route_uses_unavailable_fallback_when_wordlist_artifacts_are_missing(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0002-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0002",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-11",
            level_code="A2",
            context="baseline",
            task_types=("wordlist", "text", "interview"),
        ),
    )

    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/player/{session_id}/wordlist")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'keine verarbeitbaren wortlisten-artefakte'.lower() in html.lower()
    assert 'data-player-root' not in html


def test_player_item_download_route_uses_delivery_filename(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0001-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0001",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist", "text"),
        ),
    )
    _write_wordlist_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001")

    client = url_app.test_client()
    audio_response = client.get(f"/de/research/spanish/player/{session_id}/wordlist/audio.mp3")
    item_response = client.get(f"/de/research/spanish/player/{session_id}/wordlist/items/wl_001.mp3")
    item_download_response = client.get(f"/de/research/spanish/player/{session_id}/wordlist/items/wl_001.mp3?download=1")
    item_range_response = client.get(
        f"/de/research/spanish/player/{session_id}/wordlist/items/wl_001.mp3",
        headers={"Range": "bytes=0-15"},
    )

    assert audio_response.status_code == 200
    assert audio_response.mimetype == "audio/mpeg"
    assert item_response.status_code == 200
    assert item_response.mimetype == "audio/mpeg"
    disposition = item_response.headers["Content-Disposition"]
    assert "attachment;" not in disposition
    assert item_download_response.status_code == 200
    assert item_download_response.mimetype == "audio/mpeg"
    download_disposition = item_download_response.headers["Content-Disposition"]
    assert "attachment;" in download_disposition
    assert "ES-L-0001_wordlist_wl_001_mesa.mp3" in download_disposition
    assert item_range_response.status_code == 206
    assert item_range_response.mimetype == "audio/mpeg"
    assert "attachment;" not in (item_range_response.headers.get("Content-Disposition") or "")
    assert item_range_response.headers["Content-Range"].startswith("bytes 0-15/")