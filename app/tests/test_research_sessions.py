from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
from flask import Flask


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

from app.config.data_conventions import build_person_id, build_session_id, parse_person_id, parse_session_id
from app.research_views import build_recordings_page, build_speaker_profile_page, build_speakers_page
from app.routes.public import blueprint as public_blueprint
from app.research_sessions import (
    load_language_sessions,
    load_person_records,
    matching_sessions_for_person,
    resolve_selected_session,
)


def _clear_research_caches() -> None:
    load_language_sessions.cache_clear()
    load_person_records.cache_clear()


@pytest.fixture
def runtime_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "data" / "sessions" / "spanish").mkdir(parents=True, exist_ok=True)
    (tmp_path / "public").mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(tmp_path))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(tmp_path / "public"))

    _clear_research_caches()
    yield tmp_path
    _clear_research_caches()


@pytest.fixture
def url_app() -> Flask:
    app = Flask(__name__)
    app.config["SERVER_NAME"] = "promat.test"
    app.register_blueprint(public_blueprint)
    return app


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


def _learner_payload(
    person_id: str,
    session_id: str,
    recording_year: int,
    recording_date: str,
    level_code: str,
    context: str,
    task_types: tuple[str, ...],
    exposure_entries: list[dict[str, object]] | None = None,
    stays_in_target_country: bool | None = True,
) -> dict[str, object]:
    return {
        "person_id": person_id,
        "session_id": session_id,
        "target_language": "es",
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