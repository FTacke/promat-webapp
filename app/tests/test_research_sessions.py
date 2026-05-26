from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

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
from app.research_player_runtime import (
    _build_interview_text_segments,
    _normalize_bundle_tokens,
    _normalize_interview_annotations,
    load_task_ready_sessions,
)
from app.research_views import build_player_page, build_speaker_profile_page, build_speakers_page
from app.routes.auth import blueprint as auth_blueprint
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
    load_task_ready_sessions.cache_clear()


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
    (base_dir / "phenomena_presets.json").write_text(
        json.dumps(
            {
                "language": "spanish",
                "presets": [
                    {
                        "preset_id": "starter_preset",
                        "label": "Starter",
                        "description": "Minimal preset for route tests.",
                        "language": "spanish",
                        "items": [
                            {"task": "wordlist", "item_id": "wl_001"},
                            {"task": "text", "item_id": "d_01"},
                        ],
                    }
                ],
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
        g.user = app.config.get("TEST_AUTH_USER")
        g.user_id = app.config.get("TEST_AUTH_USER_ID")
        g.role = None

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(public_blueprint)
    return app


def _set_test_auth(app: Flask, *, username: str = "alice", user_id: str = "user-1") -> None:
    app.config["TEST_AUTH_USER"] = username
    app.config["TEST_AUTH_USER_ID"] = user_id


def _clear_test_auth(app: Flask) -> None:
    app.config["TEST_AUTH_USER"] = None
    app.config["TEST_AUTH_USER_ID"] = None


def _extract_element_by_id(html: str, tag: str, element_id: str) -> str:
    match = re.search(
        rf'<{tag}[^>]*id="{re.escape(element_id)}".*?</{tag}>',
        html,
        re.DOTALL,
    )
    assert match is not None
    return match.group(0)


def _extract_section_by_labelledby(html: str, labelledby: str) -> str:
    match = re.search(
        rf'<section[^>]*aria-labelledby="{re.escape(labelledby)}".*?</section>',
        html,
        re.DOTALL,
    )
    assert match is not None
    return match.group(0)


def _extract_corpus_card_by_title(html: str, title: str) -> str:
    title_index = html.find(title)
    assert title_index != -1
    anchor_start_index = html.rfind('<a class="pm-card pm-card--corpus', 0, title_index)
    article_start_index = html.rfind('<article class="pm-card pm-card--interactive pm-card--corpus', 0, title_index)
    start_index = max(anchor_start_index, article_start_index)
    assert start_index != -1
    end_anchor_index = html.find('</a>', title_index)
    end_article_index = html.find('</article>', title_index)
    end_index = min(index for index in (end_anchor_index, end_article_index) if index != -1)
    assert end_index != -1
    closing_tag = '</article>' if html[start_index:start_index + 8] == '<article' else '</a>'
    return html[start_index : end_index + len(closing_tag)]


def _assert_muted_locked_nav_item_order(drawer_html: str, label: str) -> None:
    pattern = re.compile(
        rf'<a[^>]*pm-nav__item--muted[^>]*>\s*<span class="promat-panel__item-label">{re.escape(label)}</span>\s*<span class="pm-icon-mask pm-icon-mask--lock promat-panel__item-lock"',
        re.DOTALL,
    )
    assert pattern.search(drawer_html) is not None


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


def _write_text_player_artifacts(
    runtime_root: Path,
    language_slug: str,
    session_id: str,
    person_id: str,
    *,
    include_tokens: bool = False,
    include_spoken_title_item: bool = False,
) -> None:
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
                **({"spoken_title_item": True} if include_spoken_title_item else {}),
                **({
                    "tokens": [
                        {
                            "token_id": "d_01_tok_01",
                            "text": "Hoy",
                            "start_ms": 1200,
                            "end_ms": 1500,
                        },
                        {
                            "token_id": "d_01_tok_02",
                            "text": "miro",
                            "start_ms": 1500,
                            "end_ms": 1900,
                        },
                        {
                            "token_id": "d_01_tok_invalid",
                            "text": "salir",
                            "start_ms": 2700,
                            "end_ms": 2900,
                        },
                    ]
                } if include_tokens else {}),
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


def _write_interview_player_artifacts(runtime_root: Path, language_slug: str, session_id: str, person_id: str) -> None:
    payload = {
        "session_id": session_id,
        "person_id": person_id,
        "task": "interview",
        "audio": {"full_mp3": "derived/interview.mp3"},
        "segments": [
            {
                "segment_id": "seg_001",
                "segment_number": "1",
                "speaker_code": "interviewer",
                "start_ms": 1000,
                "end_ms": 4600,
                "text": "Wie ging es dir mit dem Vorlesen?",
                "tokens": [
                    {"token_id": "seg_001_tok_001", "text": "Wie", "start_ms": 1000, "end_ms": 1360},
                    {"token_id": "seg_001_tok_002", "text": "ging", "start_ms": 1360, "end_ms": 1760},
                    {"token_id": "seg_001_tok_003", "text": "es", "start_ms": 1760, "end_ms": 1960},
                    {"token_id": "seg_001_tok_004", "text": "dir", "start_ms": 1960, "end_ms": 2260},
                    {"token_id": "seg_001_tok_005", "text": "mit", "start_ms": 2260, "end_ms": 2520},
                    {"token_id": "seg_001_tok_006", "text": "dem", "start_ms": 2520, "end_ms": 2780},
                    {"token_id": "seg_001_tok_007", "text": "Vorlesen?", "start_ms": 2780, "end_ms": 4600},
                ],
            },
            {
                "segment_id": "seg_002",
                "segment_number": "2",
                "speaker_code": "participant",
                "start_ms": 5200,
                "end_ms": 9800,
                "text": "Item Nummer 1.",
                "tokens": [
                    {"token_id": "seg_002_tok_001", "text": "Item", "start_ms": 5200, "end_ms": 6100},
                    {"token_id": "seg_002_tok_002", "text": "Nummer", "start_ms": 6100, "end_ms": 7460},
                    {"token_id": "seg_002_tok_003", "text": "1", "suffix": ".", "start_ms": 7460, "end_ms": 9800},
                ],
                "annotations": [
                    {
                        "kind": "material_ref",
                        "item_id": "wl_001",
                        "task": "wordlist",
                        "insert_after_token_id": "seg_002_tok_003",
                        "label": "mesa",
                        "item_number": "1",
                        "canonical_text": "mesa",
                    }
                ],
            },
        ],
    }
    _write_session_file(runtime_root, language_slug, session_id, "alignment/interview.json", json.dumps(payload, indent=2) + "\n")
    _write_session_file(runtime_root, language_slug, session_id, "derived/interview.mp3", _minimal_mp3_bytes())


def _render_interview_text_segments(segments: list[dict[str, object]]) -> str:
    parts: list[str] = []
    for segment in segments:
        kind = segment.get("kind")
        if kind == "token":
            parts.append(str(segment.get("text") or ""))
            suffix = segment.get("suffix")
            if isinstance(suffix, str) and suffix:
                parts.append(suffix)
            continue
        if kind == "material_ref":
            prefix = segment.get("prefix")
            if isinstance(prefix, str) and prefix:
                parts.append(prefix)
            parts.append(f"[{segment.get('label') or ''}]")
            suffix = segment.get("suffix")
            if isinstance(suffix, str) and suffix:
                parts.append(suffix)
            continue
        parts.append(str(segment.get("text") or ""))
    return "".join(parts)


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
                        "spoken_title_item": True,
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
    l1_additional: str | list[str] | None = None,
    person_notes: str | None = None,
    research_consent_signed: str | None = None,
    teaching_consent_signed: str | None = None,
    secure_notes: str | None = None,
) -> dict[str, object]:
    return {
        "person_id": person_id,
        "session_id": session_id,
        "target_language": target_language,
        "speaker_type": "learner",
        "l1": "DE",
        "l1_additional": l1_additional if l1_additional is not None else ["IT", "EN"],
        "mother_l1": "DE",
        "father_l1": "PL",
        "additional_languages": ["English", "French"],
        "gender": "female",
        "birth_year": 1998,
        "current_region": "Berlin, Germany",
        "childhood_region": "Saxony, Germany",
        "person_notes": person_notes,
        "research_consent_signed": research_consent_signed,
        "teaching_consent_signed": teaching_consent_signed,
        "consent_date": "2026-03-14" if research_consent_signed else None,
        "consent_file": "consent_anna.pdf" if research_consent_signed else None,
        "questionnaire_file": "questionnaire_anna.pdf" if research_consent_signed else None,
        "secure_notes": secure_notes,
        "level_code": level_code,
        "level_self": level_code,
        "recording_year": recording_year,
        "recording_date": recording_date,
        "context": context,
        "recorded_by": "Ana Romero",
        "stays_in_target_country": stays_in_target_country,
        "exposure_entries": exposure_entries or [],
        "session_notes": "test learner session",
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
    assert person.l1_additional == ("IT", "EN")
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
            l1_additional="IT; EN",
            exposure_entries=[
                {"country": "France; Israel", "duration_months": 3, "type": "school_exchange", "exposure_notes": "Participated in a one-month school exchange in Provence and stayed for two months with family in Israel."},
            ],
            person_notes="Stable internal biography note.",
            research_consent_signed="yes",
            teaching_consent_signed="unknown",
            secure_notes="Check teaching release before editorial reuse.",
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
    person_rows = {row["label"]: row["value"] for row in page["person_section"]["rows"]}
    assert person_rows["Weitere L1"] == "IT, EN"
    assert person_rows["Zusätzliche Sprachen"] == "English, French"

    person_rows = {row["label"]: row["value"] for row in page["person_section"]["rows"]}
    assert person_rows["Person-Notizen"] == "Stable internal biography note."
    assert person_rows["Research-Einwilligung"] == "Ja"
    assert person_rows["Teaching-Freigabe"] == "Unbekannt · Vor Verwendung prüfen"
    assert person_rows["Interne Notizen"] == "Check teaching release before editorial reuse."

    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Auslands-/Sprachaufenthalte")
    assert exposure_row["entries"] == [
        {
            "text": "3 Monate · France; Israel · Schulaustausch",
            "note": "Participated in a one-month school exchange in Provence and stayed for two months with family in Israel.",
        }
    ]
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
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Auslands-/Sprachaufenthalte")
    assert exposure_row["entries"] == [{"text": "3 Monate · Spain · Studium", "note": ""}]


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
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Auslands-/Sprachaufenthalte")
    assert exposure_row["kind"] == "exposure"
    assert exposure_row["value"] == "Keine"
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
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Auslands-/Sprachaufenthalte")
    assert exposure_row["entries"] == [{"text": "4 Monate · Spain · Arbeit", "note": long_note}]


def test_profile_page_hides_unknown_exposure_type_label(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0007-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0007",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist",),
            exposure_entries=[
                {"country": "France", "duration_months": 0.75, "type": "unknown", "exposure_notes": "Stayed in Strasbourg and Vannes for approximately three weeks."},
            ],
        ),
    )

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", "ES-L-0007", session_id)

    assert page is not None
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Auslands-/Sprachaufenthalte")
    assert exposure_row["entries"] == [{"text": "0,75 Monate · France", "note": "Stayed in Strasbourg and Vannes for approximately three weeks."}]


def test_profile_page_keeps_exposure_note_exact_when_note_contains_place_and_duration(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0012-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0012",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist",),
            exposure_entries=[
                {"country": "Spain", "duration_months": 10, "type": "unknown", "exposure_notes": "Stayed in Valencia for 10 months."},
            ],
        ),
    )

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", "ES-L-0012", session_id)

    assert page is not None
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Auslands-/Sprachaufenthalte")
    assert exposure_row["entries"] == [{"text": "10 Monate · Spain", "note": "Stayed in Valencia for 10 months."}]
    assert exposure_row["entries"][0]["note"] != "Valencia"


def test_profile_page_keeps_complex_exposure_note_unchanged(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0013-2026-S01"
    note = "Completed a voluntary social year in Ontario for 16 months. Participated in a school exchange in France."
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0013",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B2",
            context="baseline",
            task_types=("wordlist",),
            exposure_entries=[
                {"country": "France", "duration_months": 17, "type": "volunteering", "exposure_notes": note},
            ],
        ),
    )

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", "ES-L-0013", session_id)

    assert page is not None
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Auslands-/Sprachaufenthalte")
    assert exposure_row["entries"] == [{"text": "17 Monate · France · Freiwilligendienst", "note": note}]


def test_profile_page_uses_generic_stay_header_when_only_note_exists(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0014-2026-S01"
    note = "Stayed in Paris for approximately three weeks."
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0014",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A2",
            context="baseline",
            task_types=("wordlist",),
            exposure_entries=[
                {"country": None, "duration_months": None, "type": None, "exposure_notes": note},
            ],
        ),
    )

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", "ES-L-0014", session_id)

    assert page is not None
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Auslands-/Sprachaufenthalte")
    assert exposure_row["entries"] == [{"text": "Aufenthalt", "note": note}]


def test_speakers_page_card_shows_compact_stays_summary(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0008-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0008",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist",),
            exposure_entries=[
                {"country": "Morocco", "duration_months": 3.5, "type": "study", "exposure_notes": "Completed a semester abroad for approximately 3.5 months."},
            ],
        ),
    )

    with url_app.test_request_context():
        page = build_speakers_page("de", "spanish", {})

    card = next(entry for entry in page["cards"] if entry["person_id"] == "ES-L-0008")
    stays_row = next(row for row in card["meta_rows"] if row["label"] == "Aufenthalte")
    assert stays_row["value"] == "Ja · 3,5 Monate"
    assert card["table_stays"] == "Ja · 3,5 Monate"


def test_speakers_page_card_shows_none_without_exposure(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0009-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0009",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A2",
            context="baseline",
            task_types=("wordlist",),
            exposure_entries=[],
            stays_in_target_country=False,
        ),
    )

    with url_app.test_request_context():
        page = build_speakers_page("de", "spanish", {})

    card = next(entry for entry in page["cards"] if entry["person_id"] == "ES-L-0009")
    stays_row = next(row for row in card["meta_rows"] if row["label"] == "Aufenthalte")
    assert stays_row["value"] == "Keine"


def test_english_profile_localizes_exposure_labels(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0011-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0011",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B2",
            context="baseline",
            task_types=("wordlist",),
            exposure_entries=[
                {"country": "France; Israel", "duration_months": 3, "type": "school_exchange", "exposure_notes": "Full note kept."},
            ],
        ),
    )

    with url_app.test_request_context():
        page = build_speaker_profile_page("en", "spanish", "ES-L-0011", session_id)

    assert page is not None
    exposure_row = next(row for row in page["sessions_section"]["cards"][0]["rows"] if row["label"] == "Stays abroad / language stays")
    assert exposure_row["entries"] == [{"text": "3 months · France; Israel · School exchange", "note": "Full note kept."}]


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

    _set_test_auth(url_app)
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


def test_research_profile_html_does_not_replace_exposure_note_with_extracted_place(runtime_env: Path, url_app: Flask) -> None:
    session_id = "ES-L-0015-2026-S01"
    _write_session(
        runtime_env,
        "spanish",
        session_id,
        _learner_payload(
            person_id="ES-L-0015",
            session_id=session_id,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="B1",
            context="baseline",
            task_types=("wordlist",),
            exposure_entries=[
                {"country": "Spain", "duration_months": 10, "type": "unknown", "exposure_notes": "Stayed in Valencia for 10 months."},
            ],
        ),
    )

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/speakers/ES-L-0015?session={session_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '10 Monate · Spain' in html
    assert 'Stayed in Valencia for 10 months.' in html
    assert 'pm-profile-metadata__entry-summary">Valencia<' not in html


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


def test_research_overview_topbar_exposes_route_preserving_language_switch(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/research")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "promat-topbar__language-switch" in html
    assert 'href="/de/research?lang=de"' in html
    assert 'href="/en/research?lang=en"' in html
    assert "pm-icon-mask--language" not in html
    assert html.index("promat-topbar__language-switch") < html.index('id="themeToggle"') < html.index("pm-icon-mask--login")


def test_research_design_modal_drawer_uses_primary_tabs_and_grouped_utilities(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/research/spanish/design")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    drawer_html = _extract_element_by_id(html, "dialog", "navigation-drawer-modal")

    assert "Hauptnavigation" not in drawer_html
    assert "Aktueller Bereich" not in drawer_html
    assert "promat-panel__nav--mobile-primary" not in drawer_html
    assert 'class="promat-panel__primary-tabs"' in drawer_html
    assert re.search(r'promat-panel__brand-prefix[^>]*>Pronunciation</span><span class="promat-site-title__line promat-site-title__line--accent">Matters</span>', drawer_html, re.S) is not None
    assert re.search(r'promat-panel__brand-wordmark.*?promat-panel__primary-tabs.*?promat-panel__mobile-context-title">Spanisch-Korpus<', drawer_html, re.S) is not None
    assert 'Forschung · Spanisch-Korpus' not in drawer_html
    assert re.search(r'class="promat-panel__primary-tab is-active"[^>]*aria-current="page"[^>]*>\s*<span class="promat-panel__primary-tab-label">Forschung</span>', drawer_html, re.S) is not None
    assert drawer_html.count("promat-panel__primary-tab-label") == 3
    assert re.search(r'promat-panel__section-label promat-panel__section-label--utility">Konto<', drawer_html) is not None
    assert re.search(r'promat-panel__section-label promat-panel__section-label--utility">Darstellung<', drawer_html) is not None
    assert 'class="promat-panel__theme-toggle"' in drawer_html
    assert 'class="promat-panel__theme-toggle-label">Hell / Dunkel<' in drawer_html



@pytest.mark.parametrize(
    ("path", "expected_context", "show_context_title", "has_drawer"),
    [
        ("/de/project/about", "Projekt", False, True),
        ("/de/research", "Forschung", False, True),
        ("/de/research/spanish/design", "Spanisch-Korpus", True, True),
        ("/de/teaching", "Unterricht", False, True),
    ],
)
def test_modal_drawer_context_title_only_renders_for_specific_local_context(
    url_app: Flask,
    path: str,
    expected_context: str,
    show_context_title: bool,
    has_drawer: bool,
) -> None:
    client = url_app.test_client()

    response = client.get(path)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    if not has_drawer:
        assert 'id="navigation-drawer-modal"' not in html
        return

    drawer_html = _extract_element_by_id(html, "dialog", "navigation-drawer-modal")

    if show_context_title:
        assert f'class="promat-panel__mobile-context-title">{expected_context}<' in drawer_html
    else:
        assert expected_context not in re.findall(r'promat-panel__mobile-context-title">([^<]+)<', drawer_html)
        assert 'class="promat-panel__mobile-context-title"' not in drawer_html


def test_player_topbar_language_switch_preserves_compare_and_render_query(url_app: Flask, runtime_env: Path) -> None:
    primary_session_id = "ES-L-0001-2026-S01"
    compare_session_id = "ES-N-0001-2026-S01"
    _write_connected_text_catalog(runtime_env)
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
    _write_text_player_artifacts(runtime_env, "spanish", primary_session_id, "ES-L-0001")
    _write_text_player_artifacts(runtime_env, "spanish", compare_session_id, "ES-N-0001")

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get(
        f"/de/research/spanish/player/{primary_session_id}/text?source=speakers&compare_session={compare_session_id}&render_mode=sentence_list"
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert (
        f'href="/en/research/spanish/player/{primary_session_id}/text?source=speakers&amp;compare_session={compare_session_id}&amp;render_mode=sentence_list&amp;lang=en"'
        in html
    )


def test_research_sidebar_stays_area_only_when_authenticated(url_app: Flask) -> None:
    _set_test_auth(url_app)
    client = url_app.test_client()

    response = client.get("/de/research")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    drawer_html = _extract_element_by_id(html, "aside", "navigation-drawer-standard")

    assert "Mein Konto" not in drawer_html
    assert "Admin-Bereich" not in drawer_html
    assert "Logout" not in drawer_html


def test_research_overview_renders_structured_corpus_metadata_and_dynamic_counts(runtime_env: Path, url_app: Flask) -> None:
    spanish_person_id = build_person_id("es", "learner", 1)
    spanish_session_one = build_session_id(spanish_person_id, 2026, 1)
    spanish_session_two = build_session_id(spanish_person_id, 2027, 2)
    english_person_id = build_person_id("en", "learner", 1)
    english_session_one = build_session_id(english_person_id, 2026, 1)
    spanish_native_one = build_person_id("es", "native_speaker", 1)
    spanish_native_session_one = build_session_id(spanish_native_one, 2026, 1)
    spanish_native_two = build_person_id("es", "native_speaker", 2)
    spanish_native_session_two = build_session_id(spanish_native_two, 2026, 1)
    english_native_one = build_person_id("en", "native_speaker", 1)
    english_native_session_one = build_session_id(english_native_one, 2026, 1)

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
    _write_session(
        runtime_env,
        "spanish",
        spanish_native_session_one,
        _native_payload(spanish_native_one, spanish_native_session_one, "2026-03-10"),
    )
    _write_session(
        runtime_env,
        "spanish",
        spanish_native_session_two,
        {
            **_native_payload(spanish_native_two, spanish_native_session_two, "2026-03-11"),
            "standard_variety": "rioplatense",
            "origin_country": "Argentina",
            "origin_region": "Buenos Aires",
        },
    )
    _write_session(
        runtime_env,
        "english",
        english_native_session_one,
        {
            **_native_payload(english_native_one, english_native_session_one, "2026-04-08"),
            "target_language": "en",
            "standard_variety": "rp",
            "origin_country": "United Kingdom",
            "origin_region": "England",
        },
    )

    client = url_app.test_client()
    response = client.get("/de/research")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Vier Sprachkorpora zur Lernendenaussprache.' not in html
    assert 'einheitlicher Route-Struktur' not in html
    assert 'Spanisch-Korpus' in html
    assert 'Französisch-Korpus' in html
    assert 'Deutsch-Korpus' in html
    assert 'Englisch-Korpus' in html

    spanish_card = _extract_corpus_card_by_title(html, 'Spanisch-Korpus')
    assert 'Projektleitung' in spanish_card
    assert 'Prof. Dr. Felix Tacke' in spanish_card
    assert 'Materialkonzeption' in spanish_card
    assert 'Felix Tacke, Ana Goás Pérez' in spanish_card
    assert 'Durchführung' in spanish_card
    assert 'Marlon Merte' in spanish_card
    assert spanish_card.index('Projektleitung') < spanish_card.index('Materialkonzeption') < spanish_card.index('Durchführung')
    assert 'pm-corpus-overview-card__section--primary' in spanish_card
    assert 'pm-corpus-overview-card__section--secondary pm-card__divider-buffer' in spanish_card
    assert 'pm-speaker-card__footer pm-corpus-overview-card__footer' in spanish_card
    assert 'pm-speaker-card__footer-section pm-corpus-overview-card__footer-section' in spanish_card
    assert 'pm-corpus-overview-card--shared-accent' in spanish_card
    assert 'pm-cta-link pm-cta-link--primary pm-corpus-overview-card__action' in spanish_card
    assert 'Aufnahmen von 1 Lernenden' in spanish_card
    assert 'Referenzaufnahmen zu 2 Standardvarietäten' in spanish_card
    assert spanish_card.index('Aufnahmen von 1 Lernenden') < spanish_card.index('Referenzaufnahmen zu 2 Standardvarietäten')

    french_card = _extract_corpus_card_by_title(html, 'Französisch-Korpus')
    assert 'Prof. Dr. Janina Reinhardt' in french_card
    assert 'Amelie Spieß' in french_card
    assert 'Materialkonzeption' in french_card
    assert 'Janina Reinhardt' in french_card
    assert 'Korpus im Aufbau' in french_card
    assert 'Referenzaufnahmen' not in french_card

    german_card = _extract_corpus_card_by_title(html, 'Deutsch-Korpus')
    assert 'Prof. Dr. Kathrin Siebold' in german_card
    assert 'Theresa Fischer' in german_card
    assert 'Kathrin Siebold' in german_card
    assert 'Korpus im Aufbau' in german_card
    assert 'Referenzaufnahmen' not in german_card

    english_card = _extract_corpus_card_by_title(html, 'Englisch-Korpus')
    assert 'Prof. Dr. Rolf Kreyer' in english_card
    assert 'Marlon Merte' in english_card
    assert 'Rolf Kreyer' in english_card
    assert 'Aufnahmen von 1 Lernenden' in english_card
    assert 'Referenzaufnahmen' not in english_card

    assert 'Learner-Sessions' not in html
    assert 'Kontrolliert angelegtes Korpus' not in html


def test_research_overview_localizes_structured_corpus_cards_in_english(runtime_env: Path, url_app: Flask) -> None:
    spanish_person_id = build_person_id("es", "learner", 1)
    spanish_session = build_session_id(spanish_person_id, 2026, 1)
    spanish_native_one = build_person_id("es", "native_speaker", 1)
    spanish_native_session_one = build_session_id(spanish_native_one, 2026, 1)
    spanish_native_two = build_person_id("es", "native_speaker", 2)
    spanish_native_session_two = build_session_id(spanish_native_two, 2026, 1)

    _write_session(
        runtime_env,
        "spanish",
        spanish_session,
        _learner_payload(
            person_id=spanish_person_id,
            session_id=spanish_session,
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A2",
            context="baseline",
            task_types=("wordlist",),
        ),
    )
    _write_session(
        runtime_env,
        "spanish",
        spanish_native_session_one,
        _native_payload(spanish_native_one, spanish_native_session_one, "2026-03-10"),
    )
    _write_session(
        runtime_env,
        "spanish",
        spanish_native_session_two,
        {
            **_native_payload(spanish_native_two, spanish_native_session_two, "2026-03-11"),
            "standard_variety": "rioplatense",
            "origin_country": "Argentina",
            "origin_region": "Buenos Aires",
        },
    )

    client = url_app.test_client()
    response = client.get("/en/research")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Four learner-pronunciation corpora.' not in html
    assert 'bilingual UI' not in html

    spanish_card = _extract_corpus_card_by_title(html, 'Spanish corpus')
    assert 'Project lead' in spanish_card
    assert 'Material design' in spanish_card
    assert 'Conducted by' in spanish_card
    assert 'pm-corpus-overview-card__section--primary' in spanish_card
    assert 'pm-corpus-overview-card__section--secondary' in spanish_card
    assert 'pm-corpus-overview-card--shared-accent' in spanish_card
    assert 'Recordings from 1 learner' in spanish_card
    assert 'Reference recordings for 2 standard varieties' in spanish_card
    assert spanish_card.index('Project lead') < spanish_card.index('Material design') < spanish_card.index('Conducted by')
    assert spanish_card.index('Recordings from 1 learner') < spanish_card.index('Reference recordings for 2 standard varieties')

    french_card = _extract_corpus_card_by_title(html, 'French corpus')
    assert 'Corpus in progress' in french_card


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


@pytest.mark.parametrize(
    ("ui_lang", "language_slug", "expected_title", "expected_subtitle", "expected_body"),
    [
        (
            "de",
            "spanish",
            "Spanisch-Korpus",
            "Forschungsbereich zur spanischen Lernendenaussprache.",
            "Das Spanisch-Korpus bündelt öffentliche Informationen zum Forschungsdesign sowie geschützte Arbeitsbereiche mit pseudonymisierten Forschungsdaten. Über die Navigation links sind Aufbau, Materialien und – je nach Zugriffsrecht – Sprecher:innen, Vergleich und Phänomene erreichbar.",
        ),
        (
            "de",
            "french",
            "Französisch-Korpus",
            "Forschungsbereich zur französischen Lernendenaussprache.",
            "Das Französisch-Korpus bündelt öffentliche Informationen zum Forschungsdesign sowie geschützte Arbeitsbereiche mit pseudonymisierten Forschungsdaten. Über die Navigation links sind Aufbau, Materialien und – je nach Zugriffsrecht – Sprecher:innen, Vergleich und Phänomene erreichbar.",
        ),
        (
            "de",
            "german",
            "Deutsch-Korpus",
            "Forschungsbereich zur deutschen Lernendenaussprache.",
            "Das Deutsch-Korpus bündelt öffentliche Informationen zum Forschungsdesign sowie geschützte Arbeitsbereiche mit pseudonymisierten Forschungsdaten. Über die Navigation links sind Aufbau, Materialien und – je nach Zugriffsrecht – Sprecher:innen, Vergleich und Phänomene erreichbar.",
        ),
        (
            "de",
            "english",
            "Englisch-Korpus",
            "Forschungsbereich zur englischen Lernendenaussprache.",
            "Das Englisch-Korpus bündelt öffentliche Informationen zum Forschungsdesign sowie geschützte Arbeitsbereiche mit pseudonymisierten Forschungsdaten. Über die Navigation links sind Aufbau, Materialien und – je nach Zugriffsrecht – Sprecher:innen, Vergleich und Phänomene erreichbar.",
        ),
        (
            "en",
            "spanish",
            "Spanish corpus",
            "Research area for Spanish learner pronunciation.",
            "The Spanish corpus brings together public information on the research design as well as protected work areas with pseudonymized research data. The navigation on the left leads to corpus structure, materials and, depending on access rights, speakers, comparison, and phenomena.",
        ),
        (
            "en",
            "french",
            "French corpus",
            "Research area for French learner pronunciation.",
            "The French corpus brings together public information on the research design as well as protected work areas with pseudonymized research data. The navigation on the left leads to corpus structure, materials and, depending on access rights, speakers, comparison, and phenomena.",
        ),
        (
            "en",
            "german",
            "German corpus",
            "Research area for German learner pronunciation.",
            "The German corpus brings together public information on the research design as well as protected work areas with pseudonymized research data. The navigation on the left leads to corpus structure, materials and, depending on access rights, speakers, comparison, and phenomena.",
        ),
        (
            "en",
            "english",
            "English corpus",
            "Research area for English learner pronunciation.",
            "The English corpus brings together public information on the research design as well as protected work areas with pseudonymized research data. The navigation on the left leads to corpus structure, materials and, depending on access rights, speakers, comparison, and phenomena.",
        ),
    ],
)
def test_research_language_root_renders_public_landing_with_real_page_links(
    url_app: Flask,
    ui_lang: str,
    language_slug: str,
    expected_title: str,
    expected_subtitle: str,
    expected_body: str,
) -> None:
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/research/{language_slug}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert f'href="/{ui_lang}/research/{language_slug}/design"' in html
    assert f'href="/{ui_lang}/research/{language_slug}/speakers"' in html
    assert f'href="/{ui_lang}/research/{language_slug}/recordings"' not in html
    assert f'href="/{ui_lang}/research/{language_slug}/comparison"' in html
    assert f'href="/{ui_lang}/research/{language_slug}/phenomena"' in html
    assert expected_title in html
    assert f'promat-panel__language-title">{expected_title}<' in html
    assert expected_subtitle in html
    assert expected_body in html
    assert 'pm-research-language-root__list' not in html
    assert 'pm-research-language-root__item' not in html
    path = f"/{ui_lang}/research/{language_slug}"
    if ui_lang == "de":
        assert "Zum Schutz personenbezogener und forschungsbezogener Daten sind nicht alle Bereiche öffentlich zugänglich." in html
        assert "Als legitime Nutzer:innen gelten Angehörige von Forschungs- und Bildungseinrichtungen." in html
        assert f'href="/access-request?next={quote(path, safe="/?")}"' in html
        assert f'href="/login?next={quote(path, safe="/?")}"' in html
        assert re.search(r'pm-nav-pill__label">Zugang beantragen</span>\s*<span class="pm-interaction__arrow"', html, re.S) is not None
        assert re.search(r'pm-nav-pill__label">Zum Login</span>\s*<span class="pm-interaction__arrow"', html, re.S) is not None
    else:
        assert "To protect personal and research-related data, not every area is publicly accessible." in html
        assert "Legitimate users are members of research and educational institutions." in html
        assert f'href="/access-request?next={quote(path, safe="/?")}"' in html
        assert f'href="/login?next={quote(path, safe="/?")}"' in html
        assert re.search(r'pm-nav-pill__label">Request access</span>\s*<span class="pm-interaction__arrow"', html, re.S) is not None
        assert re.search(r'pm-nav-pill__label">Go to login</span>\s*<span class="pm-interaction__arrow"', html, re.S) is not None


def test_research_language_root_shows_muted_locked_entries_for_signed_out_users(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/research/spanish")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    drawer_html = _extract_element_by_id(html, "aside", "navigation-drawer-standard")
    assert "pm-research-language-root__action is-muted" not in html
    assert 'pm-research-language-root__item is-muted' not in html
    assert "pm-nav__item--muted" in html
    assert "pm-icon-mask--lock" in html
    assert "Login erforderlich" not in html
    assert f'href="/access-request?next={quote("/de/research/spanish", safe="/?")}"' in html
    assert f'href="/login?next={quote("/de/research/spanish", safe="/?")}"' in html
    _assert_muted_locked_nav_item_order(drawer_html, "Sprecher:innen")
    _assert_muted_locked_nav_item_order(drawer_html, "Vergleich")
    _assert_muted_locked_nav_item_order(drawer_html, "Phänomene")
    assert '/de/research/spanish/recordings' not in drawer_html


def test_research_language_root_hides_anonymous_actions_for_authenticated_users(url_app: Flask) -> None:
    _set_test_auth(url_app)
    client = url_app.test_client()

    response = client.get("/de/research/spanish")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'href="/access-request?next=/de/research/spanish"' not in html
    assert 'href="/login?next=/de/research/spanish"' not in html
    assert "Zugang beantragen →" not in html
    assert "Zum Login →" not in html
    assert "pm-research-language-root__actions" not in html
    assert 'promat-panel__language-title">Spanisch-Korpus<' in html


def test_research_design_page_shows_muted_locked_sidebar_entries_for_signed_out_users(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/research/spanish/design")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "pm-nav__item--muted" in html
    assert "pm-icon-mask--lock" in html


def test_research_design_page_keeps_sidebar_entries_unmuted_for_authenticated_users(url_app: Flask) -> None:
    _set_test_auth(url_app)
    client = url_app.test_client()

    response = client.get("/de/research/spanish/design")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "pm-nav__item--muted" not in html


def test_teaching_overview_keeps_language_selection_label(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/teaching")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-teaching-page--overview' in html
    assert 'Aussprache unterrichten' not in html
    assert 'class="promat-page__intro pm-content-header__intro">Themenseiten zur Aussprachevermittlung im Fremdsprachenunterricht.</p>' not in html
    assert 'Wählen Sie eine Sprache, um Themenseiten zur Aussprachevermittlung zu öffnen.' in html
    assert 'id="teaching-selection-title"' not in html
    assert 'pm-teaching-overview__prompt' not in html
    assert 'Welche Sprache unterrichten Sie?' in html
    assert 'pm-teaching-language-list' in html
    assert html.count('pm-teaching-language-row--available') == 1
    assert html.count('pm-teaching-language-row--pending') == 3
    assert html.count('pm-teaching-language-row__secondary') == 0
    assert html.count('pm-teaching-language-row__body--available') == 1
    assert html.count('pm-teaching-language-row__body--pending') == 3
    assert html.count('pm-teaching-language-row__aside--available') == 1
    assert html.count('pm-teaching-language-row__aside--pending') == 3
    assert html.count('pm-teaching-language-row__status') == 4
    assert html.count('pm-teaching-language-row__action') == 1
    assert 'pm-teaching-language-row__primary' not in html
    assert 'href="/de/teaching/spanish"' in html
    assert 'href="/de/teaching/english"' not in html
    assert 'href="/de/teaching/french"' not in html
    assert 'href="/de/teaching/german"' not in html
    assert html.count('aria-disabled="true"') == 3
    assert '2 Themenseiten' in html
    assert html.count('In Vorbereitung') == 3
    assert html.index('>Spanisch<') < html.index('>Englisch<') < html.index('>Französisch<') < html.index('>Deutsch<')
    assert 'Korpus wählen' not in html
    assert 'Aussprachebewusstsein für plurizentrisches Spanisch im Unterricht.' not in html
    assert 'pm-card--lang-es' not in html


def test_teaching_language_root_uses_shared_topbar_and_mobile_drawer(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/teaching/spanish")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert html.count('class="promat-topbar__nav"') == 1
    assert 'promat-topbar__row--secondary' not in html
    assert 'app-shell--inner' in html
    assert 'app-shell--panel-hidden' not in html
    assert 'data-page="teaching"' in html
    assert 'data-action="open-drawer"' in html
    assert 'id="navigation-drawer-modal"' in html
    assert 'class="promat-panel__primary-tab is-active"' in html
    assert 'promat-panel__mobile-section--context' not in html
    assert 'pm-teaching-page--hub' in html
    assert 'Spanisch: Themenseiten' in html
    assert 'Spanisch: Aussprache unterrichten' not in html
    assert 'Themenseiten zur spanischen Aussprache im Fremdsprachenunterricht.' not in html
    assert 'Die Themenseiten bieten Orientierung zur Vermittlung der Aussprache des Spanischen' in html
    assert 'class="pm-back-link pm-content-header__back"' in html
    assert 'pm-nav-pill__label">Sprachauswahl</span>' in html
    assert 'class="pm-teaching-topic-group pm-teaching-content-wide"' in html
    assert 'pm-card-grid pm-teaching-topic-grid' in html
    assert html.count('pm-teaching-topic-grid--compact') >= 2
    assert 'Grundlagen' in html
    assert 'Orientierung zu Varianten, Normen und didaktischen Entscheidungen im Unterricht.' in html
    assert 'Laute und Artikulation' in html
    assert 'Konkrete Aussprachethemen mit Beispielen und Unterrichtsimpulsen.' in html
    assert 'Welche Aussprache unterrichten?' in html
    assert 'Orientierung zu Aussprachmodellen und Variation im Spanischunterricht: Warum <em>seseo</em> und <em>distinción</em> gleichberechtigte Aussprachenormen sind und was das für den Unterricht bedeutet.' in html
    assert 'Von Felix Tacke' in html
    assert 'Finales r' in html
    assert html.count('pm-teaching-topic-card--available') == 2
    assert html.count('pm-teaching-topic-card--pending') == 2
    assert html.count('pm-teaching-topic-card--compact') == 4
    assert 'href="/de/teaching/spanish/which-pronunciation"' in html
    assert 'href="/de/teaching/spanish/soft-spanish-hard-german"' not in html
    assert 'href="/de/teaching/spanish/r"' not in html
    assert 'href="/de/teaching/spanish/final-r"' in html
    assert html.count('In Vorbereitung') >= 2
    assert 'pm-teaching-topic-card__meta' not in html
    assert 'pm-teaching-topic-card__pill' not in html
    assert 'Themenmetadaten' not in html
    assert 'Finales r wird im Unterricht besser über Hörziele' in html
    first_group_html = _extract_section_by_labelledby(html, 'teaching-group-1')
    assert 'Welche Aussprache unterrichten?' in first_group_html
    assert 'Weiches Spanisch, hartes Deutsch' in first_group_html
    assert 'Beschreibung folgt.' in first_group_html
    assert 'Das spanische r' not in first_group_html
    assert 'Finales r' not in first_group_html
    second_group_html = _extract_section_by_labelledby(html, 'teaching-group-2')
    assert 'Das spanische r' in second_group_html
    assert 'Finales r' in second_group_html
    assert 'Überblick über die wichtigsten Realisierungen des spanischen r' in second_group_html
    assert 'Finales r wird im Unterricht besser über Hörziele' in second_group_html
    assert 'Weiches Spanisch, hartes Deutsch' not in second_group_html
    assert 'Editionen' not in html
    assert 'pm-teaching-locale-switch' not in html
    assert 'pm-teaching-topic-header' not in html
    assert 'pm-teaching-block-grid--topic' not in html


def test_teaching_english_hub_stays_within_english_edition_topics(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/en/teaching/spanish")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Spanish: Topic pages' in html
    assert 'Teaching Spanish pronunciation' not in html
    assert 'Topic pages for Spanish pronunciation in foreign language teaching.' not in html
    assert 'pm-nav-pill__label">Language selection</span>' in html
    assert 'Orientation to pronunciation models, variation, and classroom pragmatics.' in html
    assert 'Which pronunciation should you teach?' in html
    assert 'By Felix Tacke' in html
    assert 'Soft Spanish, hard German' in html
    assert 'Spanish r' in html
    assert 'Concrete pronunciation topics with examples and classroom prompts.' in html
    assert 'Final r' in html
    assert html.count('pm-teaching-topic-card--available') == 2
    assert html.count('pm-teaching-topic-card--pending') == 2
    assert 'In preparation' in html
    assert 'href="/en/teaching/spanish/soft-spanish-hard-german"' not in html
    assert 'href="/en/teaching/spanish/r"' not in html
    assert 'href="/en/teaching/spanish/final-r"' in html
    assert 'Which pronunciation counts?' not in html
    assert 'Weiches Spanisch, hartes Deutsch' not in html


@pytest.mark.parametrize("language_slug", ["english", "french", "german"])
def test_teaching_empty_hubs_render_public_empty_state(url_app: Flask, language_slug: str) -> None:
    client = url_app.test_client()

    response = client.get(f"/de/teaching/{language_slug}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert ': Aussprache unterrichten' in html
    assert 'Themenseiten im Aufbau' in html
    assert 'Für diese Sprache sind noch keine öffentlichen Themenseiten hinterlegt.' in html
    assert 'Editionen' not in html


def test_teaching_missing_topic_redirects_cleanly_to_hub(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/teaching/spanish/does-not-exist")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/de/teaching/spanish")


def test_teaching_topic_media_route_serves_released_media(url_app: Flask) -> None:
    client = url_app.test_client()
    response = client.get("/teaching-media/spanish/final-r/downloads/final-r-handout.txt")

    assert response.status_code == 200
    assert response.data == b"PROMAT Teaching placeholder export for the public final-r worksheet.\r\n"


def test_teaching_topic_media_route_blocks_parent_traversal(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/teaching-media/spanish/final-r/downloads/../secret.txt")

    assert response.status_code == 404


def test_teaching_topic_missing_target_edition_redirects_to_hub(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/en/teaching/spanish/r")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/en/teaching/spanish")


def test_teaching_topic_renders_public_content_blocks(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/de/teaching/spanish/final-r")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-teaching-page--topic' in html
    assert 'pm-teaching-block-grid' in html
    assert 'pm-teaching-block--span-3' not in html
    assert 'pm-teaching-block--span-2' in html
    assert 'pm-teaching-block--span-1' in html
    assert 'Finales r' in html
    assert html.count('class="pm-back-link') == 2
    assert html.count('pm-back-link__pill') == 2
    assert 'class="pm-teaching-topic-metadata"' in html
    assert 'class="pm-teaching-topic-meta__authors"' in html
    assert 'class="pm-teaching-topic-meta__details"' in html
    assert 'Autor:innen:' in html
    assert 'Peer Review:' in html
    assert 'pm-teaching-block--topic-meta' not in html
    assert 'Diese Themenseite zitieren' in html
    assert 'pm-teaching-block--citation' in html
    assert 'pm-admonition pm-admonition--citation' in html
    assert 'aria-label="Zitat kopieren"' in html
    assert 'pm-teaching-hero__title' not in html
    assert 'pm-teaching-block__section-heading' in html
    assert 'Weiter im Hub' in html
    assert 'Arbeitsblatt herunterladen' in html
    assert html.count('pm-teaching-topic-card--available') == 1
    assert 'href="/en/teaching/spanish/final-r?lang=en"' in html
    assert 'href="/teaching-media/spanish/final-r/downloads/final-r-handout.txt"' in html


def test_teaching_pilot_topic_renders_canonical_two_column_storytelling(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get('/de/teaching/spanish/which-pronunciation')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Welche Aussprache unterrichten?' in html
    assert html.count('<h1 ') == 1
    assert 'class="pm-teaching-topic-header"' in html
    assert 'class="pm-teaching-topic-sections"' in html
    assert 'class="pm-teaching-topic-section pm-teaching-topic-section--intro"' in html
    assert html.count('class="pm-teaching-topic-section pm-teaching-topic-section--section"') == 4
    assert html.count('class="pm-teaching-topic-section pm-teaching-topic-section--further_reading"') == 1
    assert 'class="pm-teaching-topic-section pm-teaching-topic-section--citation pm-teaching-topic-section--topic-citation"' in html
    assert 'data-admonition-variant="citation"' in html
    assert html.count('data-admonition-variant="citation"') == 1
    assert html.count('class="pm-teaching-section-heading__title"') == 4
    assert html.count('class="pm-back-link') == 2
    assert html.count('pm-back-link__pill') == 2
    assert 'class="pm-back-link pm-back-link--bottom pm-teaching-topic-bottom-nav"' in html
    assert 'class="pm-teaching-topic-section pm-teaching-topic-section--citation pm-teaching-topic-section--topic-citation"' in html
    assert 'pm-teaching-topic-section__grid pm-teaching-block-grid pm-teaching-block-grid--topic pm-teaching-topic-section__grid--citation' in html
    assert '<em>Seseo</em> und <em>distinción</em>' in html
    assert 'Impulse für den Unterricht' in html
    assert 'class="pm-teaching-block pm-teaching-block--span-2 pm-teaching-block--rich-text pm-panel pm-reading pm-teaching-rich-text pm-teaching-rich-text--didactic_close" data-block-variant="didactic_close"' in html
    assert 'Aus den Vergleichen ergeben sich konkrete Entscheidungen für den Unterricht:' in html
    assert '>Vertiefung im Lehrbuch<' not in html
    assert 'Wer mehr wissen will' not in html
    assert 'data-admonition-variant="overview"' in html
    assert html.count('data-admonition-variant="overview"') == 1
    assert html.count('data-admonition-variant="context"') == 1
    assert 'class="pm-teaching-block pm-teaching-block--span-1 pm-teaching-block--overview"' in html
    assert 'class="pm-admonition pm-admonition--overview"' in html
    assert 'Variation hörbar machen' in html
    assert 'Normen transparent machen' in html
    assert '<h3 class="promat-content-block__title pm-panel__title">Mit und ohne Unterscheidung: <em>casa</em> vs. <em>caza</em></h3>' in html
    assert '<code>ll</code> und <code>y</code>' in html
    assert 'class="pm-teaching-further-reading__title">Vertiefung</h2>' in html
    assert 'Hörbeispiele zur Vertiefung öffnen' in html
    assert html.count('Hörbeispiele zur Vertiefung öffnen') == 2
    assert 'Ausblick: Weitere Aussprachemerkmale' not in html
    assert 'class="pm-teaching-section-heading__title"><p>' not in html
    assert '<h3 class="promat-content-block__title pm-panel__title"><p>' not in html
    assert '<h3 class="pm-admonition__title"><p>' not in html
    assert 'pm-teaching-block-grid' in html
    assert 'pm-teaching-block--span-3' not in html
    assert 'pm-teaching-block--topic-meta' not in html
    assert 'class="pm-teaching-topic-metadata"' in html
    intro_index = html.index('Gibt es die eine richtige Aussprache im Spanischen? Und was heißt das für den Unterricht?')
    author_index = html.index('Autor:innen:')
    first_body_index = html.index('Sorgfältige Aussprache gibt es in allen spanischsprachigen Ländern')
    assert intro_index < author_index < first_body_index
    if 'Peer Review:' in html:
        assert author_index < html.index('Peer Review:') < first_body_index
    assert 'pm-teaching-topic-meta__authors' in html
    assert 'pm-teaching-topic-meta__details' in html
    assert 'pm-teaching-section-heading__lead' not in html
    assert 'pm-teaching-block--section-heading' not in html
    assert 'Weiter im Hub' not in html
    assert html.index('Hörvergleich') < html.index('Mit und ohne Unterscheidung:')
    assert html.index('Mit und ohne Unterscheidung:') < html.index('/teaching-media/spanish/which-pronunciation/audio/variation/distincion-casa-caza.mp3')
    assert html.index('/teaching-media/spanish/which-pronunciation/audio/variation/distincion-casa-caza.mp3') < html.index('Anders, aber genauso korrekt')
    assert html.index('gracias – ciudad – paz – ración') < html.index('/teaching-media/spanish/which-pronunciation/audio/variation/distincion-word-series.mp3')
    assert html.index('Der Unterschied, den die Aufnahmen zeigen, betrifft nicht einzelne Wörter') < html.index('src="https://datawrapper.dwcdn.net/poSnB/9/"')
    assert html.index('src="https://datawrapper.dwcdn.net/poSnB/9/"') < html.index('Merksatz: Wer ')
    assert html.index('Merksatz: Wer ') < html.index('src="https://datawrapper.dwcdn.net/Uza2n/5/"')
    assert html.index('/teaching-media/spanish/which-pronunciation/audio/variation/distincion-word-series.mp3') < html.index('Kurze Ausschnitte aus Radiosendungen zeigen, dass der ')
    assert html.index('Kurze Ausschnitte aus Radiosendungen zeigen, dass der ') < html.index('/teaching-media/spanish/which-pronunciation/audio/corapan/MEXb80def27c.mp3')
    assert '<em>casa</em>' in html
    assert '<em>caza</em>' in html
    assert '<code>ll</code>' in html
    assert '<code>y</code>' in html
    assert '<em>yeísmo</em>' in html
    assert '<code>c</code>' in html
    assert '<code>z</code>' in html
    assert '<code>ci</code>' in html
    assert 'werden hier wie' in html
    assert 'href="https://www.pronunciation-matters.de"' in html
    assert '>pronunciation-matters.de<' in html
    assert 'audio-section--contrast' in html
    assert 'audio-section--examples' in html
    assert '<code>z/c</code>' in html
    assert '<code>s</code>' in html
    assert '**z/c**' not in html
    assert '**s**' not in html
    assert '*Seseo* und *distinción*' not in html
    assert 'Mit und ohne Unterscheidung: *casa* vs. *caza*' not in html
    assert 'Noch ein Aussprachemerkmal: `ll` und `y`' not in html
    assert html.count('class="pm-panel pm-reading audio-section audio-section--contrast"') == 2
    assert html.count('class="pm-panel pm-reading audio-section audio-section--examples"') == 1
    assert 'class="audio-grid audio-grid--contrast"' in html
    assert 'class="audio-grid audio-grid--examples"' in html
    assert 'class="pm-teaching-audio-contrast__lead audio-section-description"' not in html
    assert 'pm-teaching-audio-examples__header' not in html
    assert 'pm-teaching-audio-examples__title-row' not in html
    assert 'pm-teaching-audio-examples__lead' not in html
    assert 'pm-teaching-audio-examples__source' not in html
    assert 'pm-teaching-audio-contrast__header' not in html
    assert 'pm-teaching-audio-contrast__title-row' not in html
    assert 'pm-teaching-audio-contrast__title' not in html
    assert 'pm-teaching-audio-examples__icon' not in html
    assert 'pm-teaching-audio-contrast__icon' not in html
    assert html.count('class="material-symbols-rounded audio-section-icon"') == 3
    assert html.count('class="pm-teaching-audio-example audio-card audio-example-card"') == 4
    assert html.count('class="pm-teaching-audio-example__note audio-example-note"') == 4
    assert html.count('class="pm-teaching-audio-example__player audio-player-wrap"') == 4
    assert html.count('class="pm-teaching-audio-contrast__player audio-player-wrap"') == 4
    assert html.count('class="pm-teaching-audio-example__transcript audio-quote" data-audio-state="idle" id="') == 4
    assert html.count('class="audio-section-source"') == 1
    assert html.count('CO.RA.PAN') == 1
    assert 'MEXb80def27c' in html
    assert 'CHL8b78ac16b' in html
    assert 'ARGCBAeca46a987' in html
    assert 'CRI61d9dc2dc' in html
    assert '/teaching-media/spanish/which-pronunciation/audio/corapan/MEXb80def27c.mp3' in html
    assert '/teaching-media/spanish/which-pronunciation/audio/corapan/CHL8b78ac16b.mp3' in html
    assert '/teaching-media/spanish/which-pronunciation/audio/corapan/ARGCBAeca46a987.mp3' in html
    assert '/teaching-media/spanish/which-pronunciation/audio/corapan/CRI61d9dc2dc.mp3' in html
    assert 'pm-card pm-card--material pm-teaching-audio-card' not in html
    assert 'src="https://datawrapper.dwcdn.net/Uza2n/5/"' in html
    assert 'src="https://datawrapper.dwcdn.net/poSnB/9/"' in html
    assert html.count('class="pm-embed-block pm-embed-block--datawrapper pm-teaching-embed-card" data-provider="datawrapper"') == 2
    assert html.count('data-provider="datawrapper"') >= 2
    assert html.count('data-external="1"') >= 2
    assert html.count('pm-teaching-block--span-1 pm-teaching-block--embed') == 2
    assert html.count('pm-teaching-embed-card') >= 2
    assert 'pm-teaching-embed-card__title' not in html
    assert 'class="pm-embed-block__caption"' not in html
    assert 'In den spanischsprachigen Ländern Amerikas ist seseo die übliche Aussprache.' not in html
    assert 'Schematische Darstellung. Lokale und soziale Variation ist vereinfacht.' not in html
    assert 'window.addEventListener("message"' not in html
    assert 'datawrapper-height' not in html
    assert 'pm-teaching-details__summary' not in html
    assert 'data-admonition-toggle' not in html
    assert 'pm-admonition__chevron' not in html
    assert html.count('class="pm-teaching-audio-contrast__example audio-card"') == 4
    assert html.count('class="pm-teaching-audio-contrast__transcript" data-audio-state="idle" id="') == 2
    assert html.count('class="pm-teaching-audio-contrast__transcript-row audio-sequence-row"') == 2
    assert 'data-teaching-mini-player' in html
    assert html.count('class="pm-teaching-mini-player audio-player-shell" data-teaching-mini-player') == 8
    assert html.count('data-audio-feedback-target="') == 8
    assert html.count('data-audio-state="idle"') >= 14
    assert '/teaching-media/spanish/which-pronunciation/audio/variation/distincion-casa-caza.mp3' in html
    assert '/teaching-media/spanish/which-pronunciation/audio/variation/seseo-casa-caza.mp3' in html
    assert '/teaching-media/spanish/which-pronunciation/audio/variation/distincion-word-series.mp3' in html
    assert '/teaching-media/spanish/which-pronunciation/audio/variation/seseo-word-series.mp3' in html
    assert '>Audios aus<' in html
    assert html.count('>Wortfolge<') == 2
    assert '<em>caza</em>' in html
    assert '<code>z/c</code>' in html
    assert '<code>c</code>' in html
    assert '<code>s</code>' in html
    assert '<em>cerca</em>' in html
    assert '<em>cena</em>' in html
    assert 'text-transform: uppercase' not in html
    assert 'Diese Themenseite zitieren' in html
    assert html.index('Impulse für den Unterricht') < html.index('Vertiefung') < html.index('Diese Themenseite zitieren') < html.rindex('pm-nav-pill__label">Spanisch: Themenseiten</span>')
    assert '*Pronunciation Matters*' not in html
    assert '[pronunciation-matters.de]' not in html
    assert 'Noch ein Aussprachemerkmal: `ll` und `y`' not in html
    assert '`c`, `z` und `ci` werden hier wie `s` ausgesprochen.' not in html
    assert '>Transkript<' not in html
    assert '>Hinweis<' not in html
    assert '>Quelle<' not in html
    assert '>Speaker-ID<' not in html
    assert 'Audio-Datei wird ergänzt.' not in html
    assert 'pm-teaching-hero__title' not in html
    assert 'Editionen' not in html


def test_teaching_english_topic_uses_natural_hub_backlink(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/en/teaching/spanish/final-r")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-nav-pill__label">Spanish: Topic pages</span>' in html
    assert 'Editionen' not in html


def test_teaching_english_which_pronunciation_renders_single_markdown_citation(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get('/en/teaching/spanish/which-pronunciation')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert html.count('data-admonition-variant="citation"') == 1
    assert 'Cite this topic page' in html
    assert 'class="pm-teaching-topic-section pm-teaching-topic-section--citation pm-teaching-topic-section--topic-citation"' in html
    assert 'class="pm-back-link pm-back-link--bottom pm-teaching-topic-bottom-nav"' in html
    assert 'Classroom prompts' in html
    assert 'class="pm-teaching-block pm-teaching-block--span-2 pm-teaching-block--rich-text pm-panel pm-reading pm-teaching-rich-text pm-teaching-rich-text--didactic_close" data-block-variant="didactic_close"' in html
    assert 'At a glance' in html
    assert 'data-admonition-variant="overview"' in html
    assert 'Further exploration' in html
    assert 'Open audio examples for further exploration' in html
    assert 'Outlook: More pronunciation features' not in html
    assert 'For those who want to know more' not in html
    assert 'Continue in this hub' not in html
    assert '<em>Pronunciation Matters</em>' in html
    assert 'href="https://www.pronunciation-matters.de"' in html
    assert 'aria-label="Copy citation"' in html
    assert 'data-admonition-toggle' not in html
    assert 'pm-admonition__chevron' not in html
    assert '*Pronunciation Matters*' not in html
    assert '[pronunciation-matters.de]' not in html


@pytest.mark.parametrize("ui_lang", ["de", "en"])
def test_sample_route_is_removed_and_top_navigation_omits_sample(url_app: Flask, ui_lang: str) -> None:
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/sample")

    assert response.status_code == 404

    response = client.get(f"/{ui_lang}/project")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert html.count('class="promat-topbar__nav"') == 1
    assert f'href="/{ui_lang}/sample"' not in html


@pytest.mark.parametrize(
    ("ui_lang", "expected_target", "expected_title"),
    [
        ("de", "/de/project/structure", "Projektaufbau"),
        ("en", "/en/project/structure", "Project structure"),
    ],
)
def test_legacy_project_research_design_redirects_to_structure_and_keeps_depth_two_breadcrumb(
    url_app: Flask,
    ui_lang: str,
    expected_target: str,
    expected_title: str,
) -> None:
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/project/research-design")

    assert response.status_code == 308
    assert response.headers["Location"].endswith(expected_target)

    response = client.get(f"/{ui_lang}/project/research-design", follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'class="pm-breadcrumb pm-breadcrumb--mobile-only"' in html
    assert 'data-depth="2"' in html
    assert f'href="/{ui_lang}/project"' in html
    assert f'aria-current="page">{expected_title}</span>' in html


@pytest.mark.parametrize(
    ("ui_lang", "page_slug", "expected_title", "legacy_label"),
    [
        ("de", "about", "Worum es geht", "Forschungsdesign"),
        ("de", "structure", "Projektaufbau", "Forschungsdesign"),
        ("de", "data-methods", "Daten & Methodik", "Forschungsdesign"),
        ("de", "team", "Team & Mitwirkende", "Forschungsdesign"),
        ("en", "about", "What this project is about", "Research Design"),
        ("en", "structure", "Project structure", "Research Design"),
        ("en", "data-methods", "Data & methods", "Research Design"),
        ("en", "team", "Team & contributors", "Research Design"),
    ],
)
def test_project_pages_render_new_navigation_without_intro_blocks(
    url_app: Flask,
    ui_lang: str,
    page_slug: str,
    expected_title: str,
    legacy_label: str,
) -> None:
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/project/{page_slug}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    expected_title_html = expected_title.replace("&", "&amp;")
    assert f'aria-current="page">{expected_title_html}</span>' in html
    assert 'class="promat-page__intro pm-content-header__intro"' not in html
    assert f'href="/{ui_lang}/project/about"' in html
    assert f'href="/{ui_lang}/project/structure"' in html
    assert f'href="/{ui_lang}/project/data-methods"' in html
    assert f'href="/{ui_lang}/project/team"' in html
    assert f'href="/{"en" if ui_lang == "de" else "de"}/project/{page_slug}?lang={"en" if ui_lang == "de" else "de"}"' in html
    assert f'href="/{ui_lang}/project/research-design"' not in html
    assert f'>{legacy_label}<' not in html


@pytest.mark.parametrize(
    ("ui_lang", "expected_title", "legacy_label"),
    [
        ("de", "Worum es geht", "Forschungsdesign"),
        ("en", "What this project is about", "Research Design"),
    ],
)
def test_project_root_uses_about_page_and_hides_legacy_project_navigation(
    url_app: Flask,
    ui_lang: str,
    expected_title: str,
    legacy_label: str,
) -> None:
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/project")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert f'<h1 id="promat-page-title" class="promat-page__title pm-content-header__title">{expected_title}</h1>' in html
    assert f'href="/{ui_lang}/project/research-design"' not in html
    assert f'>{legacy_label}<' not in html


@pytest.mark.parametrize(
    ("ui_lang", "expected_title", "expected_caption_html"),
    [
        (
            "de",
            "Worum es geht",
            "Lehre@Philipp 2025: <em>Pronunciation Matters</em> – Fremdsprachen digital erforschen und lehren",
        ),
        (
            "en",
            "What this project is about",
            "Lehre@Philipp 2025: <em>Pronunciation Matters</em> – Researching and teaching foreign languages digitally",
        ),
    ],
)
def test_project_about_page_embeds_video_and_hides_intro(
    url_app: Flask,
    ui_lang: str,
    expected_title: str,
    expected_caption_html: str,
) -> None:
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/project/about")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert f'aria-current="page">{expected_title}</span>' in html
    assert 'class="promat-page__intro pm-content-header__intro"' not in html
    assert 'src="https://www.youtube.com/embed/ucvpPAONGoY"' in html
    assert 'class="pm-embed-block__caption"' in html
    assert expected_caption_html in html
    assert 'href="https://hispanistica.com/projects/marele/"' in html


@pytest.mark.parametrize(
    ("ui_lang", "expected_phrase", "expected_about_label", "expected_structure_label", "expected_data_label", "expected_team_label"),
    [
        (
            "de",
            "Die spanischen Aufgaben dieses Korpus wurden entwickelt",
            "Worum es geht",
            "Projektaufbau",
            "Daten & Methodik",
            "Team & Mitwirkende",
        ),
        (
            "en",
            "The Spanish tasks in this corpus were developed",
            "What this project is about",
            "Project structure",
            "Data & methods",
            "Team & contributors",
        ),
    ],
)
def test_spanish_design_page_is_localized_links_to_project_pages_and_has_no_intro(
    url_app: Flask,
    ui_lang: str,
    expected_phrase: str,
    expected_about_label: str,
    expected_structure_label: str,
    expected_data_label: str,
    expected_team_label: str,
) -> None:
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/research/spanish/design")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    expected_data_label_html = expected_data_label.replace("&", "&amp;")
    expected_team_label_html = expected_team_label.replace("&", "&amp;")
    assert expected_phrase in html
    assert 'class="promat-page__intro pm-content-header__intro"' not in html
    assert f'>{expected_about_label}<' in html
    assert f'>{expected_structure_label}<' in html
    assert f'>{expected_data_label_html}<' in html
    assert f'>{expected_team_label_html}<' in html
    assert f'href="/{ui_lang}/project/about"' in html
    assert f'href="/{ui_lang}/project/structure"' in html
    assert f'href="/{ui_lang}/project/data-methods"' in html
    assert f'href="/{ui_lang}/project/team"' in html


def test_spanish_design_page_uses_dedicated_literature_list_class(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get('/de/research/spanish/design')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '<h2 class="promat-content-block__title pm-panel__title">Literatur</h2>' in html
    assert '<ul class="promat-content-block__list pm-literature">' in html

    css_response = client.get('/static/css/20_layout.css')

    assert css_response.status_code == 200
    css = css_response.get_data(as_text=True)
    assert '.pm-literature,' in css
    assert '.pm-literature li {' in css
    assert 'text-indent: calc(-1 * var(--pm-literature-indent));' in css
    assert '.pm-literature-abbreviations li {' in css
    assert 'href="https://hispanistica.com/projects/marele/"' in html


@pytest.mark.parametrize(
    (
        "ui_lang",
        "expected_title",
        "expected_role_label",
        "expected_focus_label",
        "expected_corpus_label",
        "unexpected_legacy_section",
    ),
    [
        (
            "de",
            "Team & Mitwirkende",
            "Funktion",
            "Schwerpunkte",
            "Korpusverantwortung",
            "Studierende als Beteiligte",
        ),
        (
            "en",
            "Team & contributors",
            "Role",
            "Focus areas",
            "Corpus responsibility",
            "Students as participants in the project",
        ),
    ],
)
def test_team_page_uses_structured_credits_cards_without_legacy_text(
    url_app: Flask,
    ui_lang: str,
    expected_title: str,
    expected_role_label: str,
    expected_focus_label: str,
    expected_corpus_label: str,
    unexpected_legacy_section: str,
) -> None:
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/project/team")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    expected_title_html = expected_title.replace("&", "&amp;")
    assert f'aria-current="page">{expected_title_html}</span>' in html
    assert 'class="promat-page__intro pm-content-header__intro"' not in html
    assert '<table' not in html
    assert 'pm-grid--team-lead' in html
    assert 'pm-grid--team-corpus' in html
    assert html.count('pm-card pm-card--material pm-meta-card') == 6
    assert html.count('pm-meta-card--lead') == 2
    assert 'pm-meta-card--info' not in html
    if ui_lang == 'de':
        assert 'Gesamtprojektleitung' in html
        assert 'Ausführende Koordination' in html
        assert html.index('Gesamtprojektleitung') < html.index('Prof. Dr. Felix Tacke')
        assert html.index('Ausführende Koordination') < html.index('Marlon Merte')
    else:
        assert 'Project lead' in html
        assert 'Executive coordination' in html
        assert html.index('Project lead') < html.index('Prof. Dr. Felix Tacke')
        assert html.index('Executive coordination') < html.index('Marlon Merte')
    assert html.index('Prof. Dr. Felix Tacke') < html.index('Marlon Merte')
    if ui_lang == 'de':
        assert html.index('Spanisch-Korpus') < html.index('Französisch-Korpus') < html.index('Deutsch-Korpus') < html.index('Englisch-Korpus')
    else:
        assert html.index('Spanish corpus') < html.index('French corpus') < html.index('German corpus') < html.index('English corpus')
    assert unexpected_legacy_section not in html
    assert 'support for recording processes' not in html
    assert 'übergreifende Konzeption' not in html
    assert '<em>Pronunciation Matters</em>' in html
    assert 'Prof. Dr. Felix Tacke' in html
    assert 'Marlon Merte' in html
    assert 'Prof. Dr. Janina Reinhardt' in html
    assert 'Prof. Dr. Kathrin Siebold' in html
    assert 'Prof. Dr. Rolf Kreyer' in html
    assert 'Theresa Fischer, M.A.' in html
    assert 'Dr. Edmund Voges' in html
    assert 'Ariane Wenz' in html
    assert 'Dr. Pedro Alonso' in html
    assert 'Ana Goás Pérez' in html
    assert 'Marcela Gualotuña' in html
    assert 'Aoife Holmes-Rein, M.A.' in html
    assert 'Sprachenzentrum' in html or 'Language Center' in html
    assert 'Dank' in html or 'Acknowledgements' in html
    assert expected_role_label in html
    assert expected_focus_label in html
    assert expected_corpus_label in html


def test_team_page_uses_shared_two_column_team_grid_rules(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get('/static/css/20_layout.css')

    assert response.status_code == 200
    css = response.get_data(as_text=True)
    assert '.pm-grid--team-lead,' in css
    assert '.pm-grid--team-corpus {' in css
    assert '.pm-feature-band > .pm-grid--team-lead,' in css
    assert '.pm-feature-band > .pm-grid--team-corpus {' in css
    assert 'gap: clamp(0.78rem, 1.55vw, 0.98rem);' in css
    assert 'width: min(100%, 46rem);' in css
    assert 'max-width: 46rem;' in css
    assert 'margin-inline: auto;' in css
    assert '@media (min-width: 760px) {' in css
    assert 'repeat(2, minmax(0, 1fr));' in css
    assert 'repeat(4, minmax(0, 1fr));' not in css


def test_shared_card_hover_rules_keep_titles_neutral_and_stable(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get('/static/css/40_cards.css')

    assert response.status_code == 200
    css = response.get_data(as_text=True)
    assert 'a.pm-card:hover,' in css
    assert 'a.pm-card:active,' in css
    assert '.pm-card--interactive:hover {' in css
    assert 'box-shadow: var(--pm-card-hover-shadow);' in css
    assert 'color: var(--book-fg);' in css
    assert 'a.pm-card:hover .pm-card__title,' in css
    assert 'a.pm-card:active .pm-card__title,' in css
    assert 'color: inherit;' in css


def test_shared_cta_links_use_container_underline_rule(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get("/static/css/30_components.css")

    assert response.status_code == 200
    css = response.get_data(as_text=True)
    hover_block = re.search(
        r"a\.pm-cta-link:hover,\s*a\.pm-cta-link:focus-visible,\s*a\.pm-cta-link:active,(?P<selectors>.*?)\{(?P<body>.*?)\}",
        css,
        re.S,
    )
    assert '.pm-cta-link::after' not in css
    assert hover_block is not None
    assert 'text-decoration' not in hover_block.group('body')


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


@pytest.mark.parametrize("ui_lang", ["de", "en"])
@pytest.mark.parametrize("language_slug", ["spanish", "french", "german", "english"])
def test_research_design_page_stays_public(url_app: Flask, ui_lang: str, language_slug: str) -> None:
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/research/{language_slug}/design")

    assert response.status_code == 200


@pytest.mark.parametrize("ui_lang", ["de", "en"])
@pytest.mark.parametrize("language_slug", ["spanish", "french", "german", "english"])
@pytest.mark.parametrize("page_slug", ["speakers", "comparison", "phenomena"])
def test_research_workbench_pages_require_auth_with_preserved_target(
    url_app: Flask,
    ui_lang: str,
    language_slug: str,
    page_slug: str,
) -> None:
    _clear_test_auth(url_app)
    client = url_app.test_client()
    path = f"/{ui_lang}/research/{language_slug}/{page_slug}"

    response = client.get(path)

    assert response.status_code == 302
    assert response.headers["Location"] == f"/login?next={quote(path, safe='/?')}"


@pytest.mark.parametrize("ui_lang", ["de", "en"])
@pytest.mark.parametrize("language_slug", ["spanish", "french", "german", "english"])
@pytest.mark.parametrize(
    "path_template",
    [
        "/{ui_lang}/research/{language_slug}/speakers/ES-L-0001",
        "/{ui_lang}/research/{language_slug}/phenomena/presets/starter_preset",
        "/{ui_lang}/research/{language_slug}/phenomena/sets/demo-set",
        "/{ui_lang}/research/{language_slug}/player/ES-L-0001-2026-S01/wordlist",
        "/{ui_lang}/research/{language_slug}/player/ES-L-0001-2026-S01/wordlist/audio.mp3",
        "/{ui_lang}/research/{language_slug}/player/ES-L-0001-2026-S01/wordlist/items/wl_001.mp3?download=1",
    ],
)
def test_research_detail_routes_require_auth_before_lookup(
    url_app: Flask,
    ui_lang: str,
    language_slug: str,
    path_template: str,
) -> None:
    _clear_test_auth(url_app)
    client = url_app.test_client()
    path = path_template.format(ui_lang=ui_lang, language_slug=language_slug)

    response = client.get(path)

    assert response.status_code == 302
    assert response.headers["Location"] == f"/login?next={quote(path, safe='/?')}"


@pytest.mark.parametrize(
    ("ui_lang", "language_slug", "page_slug"),
    [("de", "spanish", "speakers"), ("en", "english", "comparison")],
)
def test_authenticated_research_workbench_pages_render_after_access_gate(
    url_app: Flask,
    ui_lang: str,
    language_slug: str,
    page_slug: str,
) -> None:
    _set_test_auth(url_app)
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/research/{language_slug}/{page_slug}")

    assert response.status_code == 200


def test_research_player_prewarm_request_warms_route_without_rendering_body(url_app: Flask) -> None:
    _set_test_auth(url_app)
    client = url_app.test_client()

    response = client.get(
        "/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=speakers",
        headers={"X-Promat-Player-Prewarm": "1"},
    )

    assert response.status_code == 204
    assert response.headers["X-Promat-Player-Prewarm"] == "1"
    assert response.get_data(as_text=True) == ""


@pytest.mark.parametrize("ui_lang", ["de", "en"])
def test_removed_recordings_route_falls_through_to_not_found(url_app: Flask, ui_lang: str) -> None:
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/research/spanish/recordings")

    assert response.status_code == 404


def test_speakers_page_uses_neutral_learner_cards_with_level_badges(runtime_env: Path, url_app: Flask) -> None:
    _write_session(
        runtime_env,
        "spanish",
        "ES-L-0001-2026-S01",
        _learner_payload(
            person_id="ES-L-0001",
            session_id="ES-L-0001-2026-S01",
            recording_year=2026,
            recording_date="2026-03-10",
            level_code="A2",
            context="baseline",
            task_types=("wordlist", "text"),
        ),
    )
    _write_session(runtime_env, "spanish", "ES-N-0001-2026-S01", _native_payload("ES-N-0001", "ES-N-0001-2026-S01", "2026-03-11"))

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get("/de/research/spanish/speakers")
    with url_app.test_request_context():
        page = build_speakers_page("de", "spanish", {})

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-speaker-card pm-speaker-card--learner' in html
    assert 'pm-speaker-card pm-speaker-card--native' in html
    assert 'pm-speaker-card--a2' not in html
    assert 'pm-research-meta-badge pm-research-meta-badge--level pm-research-meta-badge--a2' in html
    assert 'pm-research-meta-badge pm-research-meta-badge--native-detail">Spanien<' in html
    assert 'Profil öffnen' not in html
    assert 'pm-speaker-card__footer-section--actions' not in html
    assert re.search(r'pm-inline-text-link pm-speaker-card__profile-link pm-research-speaker-profile-link" href="/de/research/spanish/speakers/ES-L-0001\?session=ES-L-0001-2026-S01">\s*<span class="pm-inline-text-link__label">Profil</span>\s*<span class="pm-interaction__arrow"', html, re.S) is not None
    assert html.index('pm-speaker-card__session-id') < html.index('pm-speaker-card__profile-link') < html.index('pm-speaker-card__meta')
    learner_card = next(card for card in page["cards"] if card["person_id"] == "ES-L-0001")
    native_card = next(card for card in page["cards"] if card["person_id"] == "ES-N-0001")
    assert [row["label"] for row in learner_card["meta_rows"]] == ["Niveau", "L1", "Geschlecht", "Sprachaufenthalte"]
    assert learner_card["meta_rows"][0]["badges"][0]["modifiers"] == ["level", "a2"]
    assert learner_card["profile_label"] == "Profil"
    assert [row["label"] for row in native_card["meta_rows"]] == ["Standardvarietät", "Herkunftsregion", "Geschlecht", "Aufnahmejahr"]
    assert native_card["meta_rows"][0]["value"] == "Spanien"
    assert native_card["meta_rows"][0]["badges"][0] == {"label": "Spanien", "modifiers": ["native-detail"]}


def test_speakers_page_supports_shared_cards_and_table_views(runtime_env: Path, url_app: Flask) -> None:
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
        cards_page = build_speakers_page("de", "spanish", {})
        table_page = build_speakers_page("de", "spanish", {"view": "table"})
        fallback_page = build_speakers_page("de", "spanish", {"view": "grid"})

    assert cards_page["view"] == "cards"
    assert table_page["view"] == "table"
    assert fallback_page["view"] == "cards"
    assert cards_page["cards"] is cards_page["results"]
    assert len(cards_page["results"]) == len(table_page["results"]) == 2

    learner_row = next(row for row in table_page["results"] if row["person_id"] == "ES-L-0001")
    native_row = next(row for row in table_page["results"] if row["person_id"] == "ES-N-0001")

    assert learner_row["session_id"] == learner_session
    assert learner_row["table_level"] == "A2"
    assert learner_row["table_detail"] == "DE"
    assert learner_row["table_stays"] == "Ja"
    assert learner_row["profile_label"] == "Profil"
    assert learner_row["profile_href"].endswith(f"/de/research/spanish/speakers/ES-L-0001?session={learner_session}")
    assert [action["label"] for action in learner_row["table_actions"]] == ["Wortliste", "Text", "Interview"]
    assert [action["label"] for action in native_row["table_actions"]] == ["Wortliste", "Text"]
    assert learner_row["table_actions"][0]["href"].endswith(f"/de/research/spanish/player/{learner_session}/wordlist?source=speakers")
    assert learner_row["table_actions"][1]["href"].endswith(f"/de/research/spanish/player/{learner_session}/text?source=speakers")
    assert learner_row["table_actions"][2]["href"].endswith(f"/de/research/spanish/player/{learner_session}/interview?source=speakers")
    assert native_row["table_level"] == "–"
    assert native_row["table_stays"] == "–"
    assert native_row["table_detail"] == "Spanien"


def test_speakers_card_route_localizes_quiet_profile_link_in_english(runtime_env: Path, url_app: Flask) -> None:
    learner_session = "ES-L-0001-2026-S01"
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

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get("/en/research/spanish/speakers")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-inline-text-link__label">Profile</span>' in html
    assert 'pm-speaker-card__footer-section--actions' not in html
    assert 'pm-nav-pill__label">Wordlist</span>' in html
    assert html.index('pm-speaker-card__session-id') < html.index('pm-speaker-card__profile-link') < html.index('pm-speaker-card__meta')


def test_speakers_route_renders_table_view_and_preserves_query_state(runtime_env: Path, url_app: Flask) -> None:
    learner_session = "ES-L-0001-2026-S01"
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

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get("/de/research/spanish/speakers?gender=female&view=table")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '>Ansicht:<' in html
    assert '>Karten<' in html
    assert '>Tabelle<' in html
    assert '>Sprecher:in<' in html
    assert '>L1 / Varietät<' in html
    assert '>Aufenthalt<' in html
    assert '>Aufzeichnungen<' in html
    assert 'href="/de/research/spanish/speakers?gender=female&amp;view=cards"' in html
    assert 'href="/en/research/spanish/speakers?gender=female&amp;view=table&amp;lang=en"' in html
    assert 'pm-research-speaker-cell__profile' in html
    assert 'pm-inline-text-link__label">Profil</span>' in html
    assert 'pm-nav-pill__label">Profil</span>' not in html
    assert 'href="/de/research/spanish/speakers/ES-L-0001?session=ES-L-0001-2026-S01"' in html
    assert 'pm-research-speaker-cell__session' not in html
    assert 'pm-nav-pill__label">Wortliste</span>' in html
    assert 'href="/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=speakers"' in html
    assert 'href="/de/research/spanish/player/ES-L-0001-2026-S01/text?source=speakers"' in html
    assert 'href="/de/research/spanish/player/ES-L-0001-2026-S01/interview?source=speakers"' in html


def test_speakers_table_route_localizes_labels_in_english(runtime_env: Path, url_app: Flask) -> None:
    learner_session = "ES-L-0001-2026-S01"
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

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get("/en/research/spanish/speakers?view=table")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '>View:<' in html
    assert '>Cards<' in html
    assert '>Table<' in html
    assert '>Speaker<' in html
    assert '>Speaker group<' in html
    assert '>Stays<' in html
    assert '>L1 / Variety<' in html
    assert '>Recordings<' in html
    assert 'pm-inline-text-link__label">Profile</span>' in html
    assert 'pm-nav-pill__label">Profile</span>' not in html
    assert 'pm-nav-pill__label">Wordlist</span>' in html
    assert 'pm-nav-pill__label">Text</span>' in html
    assert 'pm-nav-pill__label">Interview</span>' in html
    assert 'pm-research-speaker-cell__session' not in html


@pytest.mark.parametrize(
    ("ui_lang", "expected_message"),
    [
        ("de", "Keine Sprecherdaten vorhanden."),
        ("en", "No speaker data available."),
    ],
)
def test_speakers_route_renders_plain_empty_state_without_runtime_sessions(
    runtime_env: Path,
    url_app: Flask,
    ui_lang: str,
    expected_message: str,
) -> None:
    _set_test_auth(url_app)
    client = url_app.test_client()

    response = client.get(f"/{ui_lang}/research/spanish/speakers")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert expected_message in html
    assert "Keine passenden Personen gefunden." not in html
    assert "No matching people found." not in html
    assert "Geplante Übersicht" not in html
    assert "Geplante Filter" not in html
    assert "Struktureller Stand" not in html
    assert 'class="pm-research-empty__text">' in html


def test_research_workbench_builders_expose_english_shared_labels(runtime_env: Path, url_app: Flask) -> None:
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
        speakers_page = build_speakers_page("en", "spanish", {})
        profile_page = build_speaker_profile_page("en", "spanish", "ES-L-0001", learner_session)

    assert speakers_page["content_header"]["intro"] == "Person-based access to the Spanish corpus. A person appears exactly once and matches as soon as at least one of their sessions satisfies all active filters."
    assert speakers_page["status"]["result_label"] == "people"
    assert speakers_page["cards"][0]["selected_session_label"] == "Selected session"
    assert speakers_page["cards"][0]["recordings_label"] == "Recordings"
    assert profile_page is not None
    assert profile_page["title"] == "Profile"
    assert profile_page["person_section"]["title"] == "Profile data"
    assert profile_page["sessions_section"]["title"] == "Session and recordings"


def test_research_workbench_routes_render_english_shared_aria_and_actions(runtime_env: Path, url_app: Flask) -> None:
    learner_session = "ES-L-0001-2026-S01"
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

    _set_test_auth(url_app)
    client = url_app.test_client()

    speakers_response = client.get("/en/research/spanish/speakers?gender=female")
    assert speakers_response.status_code == 200
    speakers_html = speakers_response.get_data(as_text=True)
    assert 'aria-label="Quick filters"' in speakers_html
    assert 'aria-label="Speaker groups"' in speakers_html
    assert 'aria-label="Speakers"' in speakers_html
    assert 'aria-label="Active filters"' in speakers_html

    profile_response = client.get(f"/en/research/spanish/speakers/ES-L-0001?session={learner_session}")
    assert profile_response.status_code == 200
    profile_html = profile_response.get_data(as_text=True)
    assert '>Note<' in profile_html
    assert 'aria-label="Navigation"' in profile_html
    assert 'class="pm-back-link pm-back-link--bottom pm-profile-navigation"' in profile_html
    assert re.search(r'pm-nav-pill__label">Speakers</span>', profile_html) is not None


def test_profile_header_shows_session_count_and_native_interview_disabled(runtime_env: Path, url_app: Flask) -> None:
    native_session = "ES-N-0001-2026-S01"
    _write_session(runtime_env, "spanish", native_session, _native_payload("ES-N-0001", native_session, "2026-03-11"))

    with url_app.test_request_context():
        page = build_speaker_profile_page("de", "spanish", "ES-N-0001", native_session)

    assert page is not None
    assert page["profile_header"]["session_count_label"] == "Zugeordnete Sessions"
    assert page["profile_header"]["session_count_value"] == 1
    assert [badge["label"] for badge in page["profile_header"]["badges"]] == ["Native Speaker", "Spanien"]
    person_rows = {row["label"]: row["value"] for row in page["person_section"]["rows"]}
    assert person_rows["Herkunftsland"] == "Spanien"
    assert "Standardvarietät" not in person_rows
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


def test_player_page_maps_legacy_recordings_source_back_to_speakers_table(runtime_env: Path, url_app: Flask) -> None:
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
    assert page["player"]["items"][0]["download_href"].endswith(f"/de/research/spanish/player/{session_id}/wordlist/items/wl_001.mp3?download=1")
    assert [panel["key"] for panel in page["task_panels"]] == ["wordlist", "text", "interview"]
    assert page["task_panels"][0]["current"] is True
    assert page["task_panels"][1]["href"] is None
    assert page["task_panels"][1]["state_label"] == "Keine verarbeitbaren Player-Artefakte"
    assert page["origin_link"]["href"].endswith("/de/research/spanish/speakers?view=table")
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
        page = build_player_page("en", "spanish", session_id, "wordlist", "speakers")

    assert page is not None
    assert page["title"] == "Player"
    assert page["content_header"]["title"] == "Player"
    assert page["content_header"]["intro"] == "Audio workbench for one documented session and its available task types."
    assert page["player"]["audio_href"].endswith(f"/en/research/spanish/player/{session_id}/wordlist/audio.mp3")
    assert page["player"]["controls_title"] == "Playback"
    assert page["task_panels"][1]["state_label"] == "No playable artifacts"
    assert page["summary_cards"][0]["profile_label"] == "Profile"
    assert [row["label"] for row in page["summary_cards"][0]["rows"]] == [
        "Person-ID",
        "Recording date",
        "Gender",
        "Stays in target-language country",
        "Recorded by",
    ]


def test_player_page_builds_productive_interview_view_inside_shared_player(runtime_env: Path, url_app: Flask) -> None:
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
    _write_interview_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001")

    with url_app.test_request_context():
        page = build_player_page("de", "spanish", session_id, "interview", "speakers", focus_segment="seg_002")

    assert page is not None
    assert page["player"]["mode"] == "interview"
    assert page["player"]["primary_audio_mode"] == "full"
    assert page["player"]["controls_title"] == "Wiedergabe"
    assert page["player"]["compare"]["has_candidates"] is False
    assert page["player"]["set_select"] is None
    assert page["player"]["client_state"]["focusedSegmentId"] == "seg_002"
    assert [item["speaker_label"] for item in page["player"]["primary"]["items"]] == ["Explorator:in", "Sprecher:in"]
    material_ref = next(
        segment
        for segment in page["player"]["primary"]["items"][1]["text_segments"]
        if segment["kind"] == "material_ref"
    )
    assert material_ref["suffix"] == "."
    assert "trailing_punctuation" not in material_ref
    assert material_ref["reference"]["task_label"] == "Wortliste"
    assert "focus_item=wl_001" in material_ref["reference"]["open_href"]
    assert material_ref["reference"]["clip_href"].endswith(f"/de/research/spanish/player/{session_id}/wordlist/items/wl_001.mp3")


def test_build_interview_text_segments_keeps_material_ref_before_suffix_for_suffix_and_legacy_token_models() -> None:
    cases = [
        {
            "segment_id": "seg_025",
            "text": "Item Nummer 25.",
            "tokens": [
                {"token_id": "seg_025_tok_001", "text": "Item", "start_ms": 0, "end_ms": 200},
                {"token_id": "seg_025_tok_002", "text": "Nummer", "start_ms": 200, "end_ms": 500},
                {"token_id": "seg_025_tok_003", "text": "25", "suffix": ".", "start_ms": 500, "end_ms": 900},
            ],
            "annotations": [
                {
                    "kind": "material_ref",
                    "item_id": "wl_025",
                    "task": "wordlist",
                    "insert_after_token_id": "seg_025_tok_003",
                    "label": "oír",
                    "item_number": "25",
                    "canonical_text": "oír",
                }
            ],
            "expected": "Item Nummer 25 [oír].",
        },
        {
            "segment_id": "seg_080",
            "text": "Item Nummer 80.",
            "tokens": [
                {"token_id": "seg_080_tok_001", "text": "Item", "start_ms": 0, "end_ms": 200},
                {"token_id": "seg_080_tok_002", "text": "Nummer", "start_ms": 200, "end_ms": 500},
                {"token_id": "seg_080_tok_003", "text": "80.", "start_ms": 500, "end_ms": 900},
            ],
            "annotations": [
                {
                    "kind": "material_ref",
                    "item_id": "wl_080",
                    "task": "wordlist",
                    "insert_after_token_id": "seg_080_tok_003",
                    "label": "Europa",
                    "item_number": "80",
                    "canonical_text": "Europa",
                }
            ],
            "expected": "Item Nummer 80 [Europa].",
        },
    ]

    for case in cases:
        tokens = _normalize_bundle_tokens(
            case["segment_id"],
            case["tokens"],
            item_start_ms=0,
            item_end_ms=1000,
        )
        annotations = _normalize_interview_annotations(case["segment_id"], case["annotations"])
        text_segments, renderable_tokens, _ = _build_interview_text_segments(
            case["segment_id"],
            case["text"],
            tokens,
            annotations,
        )

        material_ref = next(segment for segment in text_segments if segment["kind"] == "material_ref")
        anchored_token = next(segment for segment in text_segments if segment["kind"] == "token" and segment["token_id"].endswith("003"))
        renderable_token = next(token for token in renderable_tokens if token["token_id"].endswith("003"))

        assert _render_interview_text_segments(text_segments) == case["expected"]
        assert anchored_token["text"] in {"25", "80"}
        assert "suffix" not in anchored_token
        assert material_ref["suffix"] == "."
        assert renderable_token["text"] in {"25", "80"}
        assert renderable_token["suffix"] == "."


def test_player_route_renders_interview_transcript_and_reference_dialog_in_both_languages(runtime_env: Path, url_app: Flask) -> None:
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
    _write_interview_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001")

    _set_test_auth(url_app)
    client = url_app.test_client()

    response_de = client.get(f"/de/research/spanish/player/{session_id}/interview?source=speakers&focus_segment=seg_002")
    response_en = client.get(f"/en/research/spanish/player/{session_id}/interview?source=speakers&focus_segment=seg_002")

    assert response_de.status_code == 200
    assert response_en.status_code == 200

    html_de = response_de.get_data(as_text=True)
    html_en = response_en.get_data(as_text=True)

    assert "pm-player-transcript" in html_de
    assert "data-player-reference-dialog" in html_de
    assert '<h2 class="pm-player-panel__title">Wiedergabe</h2>' in html_de
    assert html_de.count('<h2 class="pm-player-panel__title">Interview</h2>') == 1
    assert "Explorator:in" in html_de
    assert "Im Kontext öffnen" in html_de
    assert "pm-player-transcript__segment" not in html_de
    assert "Segment 1" not in html_de
    assert '>2 Segmente<' not in html_de
    assert "data-player-reference-close" not in html_de
    assert "data-player-reference-download" in html_de
    assert "pm-player-inline-ref__label" in html_de
    assert 'class="pm-player-transcript__meta">' in html_de
    assert 'class="pm-player-transcript__speaker pm-player-transcript__speaker--interviewer">Explorator:in</span>' in html_de
    assert 'class="pm-player-transcript__time-wrap"' in html_de
    assert '>0:01' in html_de
    assert '0:04</span>' in html_de
    assert html_de.index('pm-player-transcript__speaker pm-player-transcript__speaker--interviewer') < html_de.index('pm-player-transcript__time-wrap')
    assert '<div class="pm-player-reference-popover__eyebrow">' in html_de
    assert 'data-player-reference-task' in html_de
    assert 'data-player-reference-item-number' in html_de
    assert '</button><span class="pm-player-inline-ref__punctuation">.</span>' in html_de
    assert 'target="_blank"' in html_de
    assert "data-player-compare-add" not in html_de
    assert "data-player-set-select" not in html_de

    assert "pm-player-transcript" in html_en
    assert '<h2 class="pm-player-panel__title">Playback</h2>' in html_en
    assert html_en.count('<h2 class="pm-player-panel__title">Interview</h2>') == 1
    assert "Interviewer" in html_en
    assert "Open in context" in html_en
    assert "data-player-reference-dialog" in html_en
    assert 'class="pm-player-transcript__speaker pm-player-transcript__speaker--interviewer">Interviewer</span>' in html_en
    assert 'class="pm-player-transcript__time-wrap"' in html_en
    assert '>0:01' in html_en
    assert '0:04</span>' in html_en
    assert html_en.index('pm-player-transcript__speaker pm-player-transcript__speaker--interviewer') < html_en.index('pm-player-transcript__time-wrap')
    assert "pm-player-transcript__segment" not in html_en
    assert "Segment 1" not in html_en
    assert '>2 segments<' not in html_en
    assert "data-player-reference-close" not in html_en
    assert "data-player-reference-download" in html_en
    assert '</button><span class="pm-player-inline-ref__punctuation">.</span>' in html_en


def test_player_audio_route_serves_interview_full_audio(runtime_env: Path, url_app: Flask) -> None:
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
            task_types=("interview",),
        ),
    )
    _write_interview_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001")

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/player/{session_id}/interview/audio.mp3")

    assert response.status_code == 200
    assert response.mimetype == "audio/mpeg"


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
        single_page = build_player_page("de", "spanish", primary_session_id, "wordlist", "speakers")
        compare_page = build_player_page(
            "de",
            "spanish",
            primary_session_id,
            "wordlist",
            "speakers",
            compare_session_id=compare_session_id,
        )

    assert single_page is not None
    assert single_page["title"] == "Player"
    assert single_page["content_header"]["title"] == "Player"
    assert single_page["summary_cards"][0]["accent_modifier"] == "neutral"
    assert single_page["player"]["controls_title"] == "Wiedergabe"
    assert [row["label"] for row in single_page["summary_cards"][0]["rows"]] == [
        "Person-ID",
        "Aufnahmedatum",
        "Geschlecht",
        "Sprachaufenthalte",
        "Explorator:in",
    ]
    assert [badge["label"] for badge in single_page["summary_cards"][0]["badges"]] == ["Lernende", "B1", "L1 DE"]
    assert single_page["summary_cards"][0]["badges"][1]["modifiers"] == ["level", "b1"]
    assert [action["action"] for action in single_page["summary_cards"][0]["card_actions"]] == ["profile", "compare-add"]
    assert single_page["summary_cards"][0]["card_actions"][1]["label"] == "Vergleich"
    assert single_page["player"]["set_select"]["options"][0]["label"] == "Alle Items"

    assert compare_page is not None
    assert compare_page["summary_cards"][0]["accent_modifier"] == "neutral"
    assert compare_page["summary_cards"][1]["accent_modifier"] == "neutral"
    assert compare_page["summary_cards"][1]["role_badge"]["label"] == "Vergleich"
    assert [badge["label"] for badge in compare_page["summary_cards"][1]["badges"]] == ["Native Speaker", "Spanien"]
    assert [row["label"] for row in compare_page["summary_cards"][1]["rows"]] == [
        "Standardvarietät",
        "Herkunftsregion",
        "Geschlecht",
        "Aufnahmejahr",
    ]
    assert [row["value"] for row in compare_page["summary_cards"][1]["rows"]] == [
        "Spanien",
        "Castile and Leon",
        "männlich",
        "2026",
    ]
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

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/player/{session_id}/wordlist?source=speakers")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "pm-material-choice" in html
    assert "data-player-set-select" in html

    css_response = client.get('/static/css/30_components.css')

    assert css_response.status_code == 200
    css = css_response.get_data(as_text=True)
    assert '.pm-material-choice {' in css
    assert 'border: 1px solid var(--pm-border-subtle);' in css
    assert '.pm-player-material-strip .pm-material-choice {' not in css


def test_player_route_uses_neutral_meta_cards_and_shared_badges(runtime_env: Path, url_app: Flask) -> None:
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

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get(
        f"/de/research/spanish/player/{primary_session_id}/wordlist?source=speakers&compare_session={compare_session_id}"
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert html.count('pm-speaker-card--neutral pm-player-meta-card') == 2
    assert 'pm-speaker-card--b1 pm-player-meta-card' not in html
    assert 'pm-speaker-card--native pm-player-meta-card' not in html
    assert 'pm-research-meta-badge pm-research-meta-badge--detail">Native Speaker<' in html
    assert 'pm-research-meta-badge pm-research-meta-badge--native-detail">Spanien<' in html
    assert 'pm-research-meta-badge pm-player-meta-card__role pm-research-meta-badge--role pm-research-meta-badge--detail' in html
    assert 'pm-research-meta-badge pm-research-meta-badge--level pm-research-meta-badge--b1' in html


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
        page = build_player_page("de", "spanish", session_id, "text", "speakers")

    assert page is not None
    assert page["player"]["mode"] == "text"
    assert page["player"]["source_kind"] == "text"
    assert page["player"]["render_mode"] == "running_text"
    assert page["player"]["primary_audio_mode"] == "full"
    assert page["player"]["render_modes"] is not None
    assert [option["key"] for option in page["player"]["render_modes"]["options"]] == ["sentence_list", "running_text"]
    assert len(page["player"]["text_blocks"]) == 2
    assert [block["kind"] for block in page["player"]["text_blocks"]] == ["spoken_title", "paragraph"]
    assert page["player"]["text_blocks"][0]["item"]["item_id"] == "d_01"
    assert page["player"]["render_modes"]["options"][0]["href"].endswith(
        f"/de/research/spanish/player/{session_id}/text?source=speakers&render_mode=sentence_list"
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
        page = build_player_page("de", "spanish", session_id, "text", "speakers", render_mode="sentence_list")

    assert page is not None
    assert page["player"]["render_mode"] == "sentence_list"
    assert page["player"]["text_blocks"] == []
    assert page["player"]["client_state"]["singleViewHref"].endswith(
        f"/de/research/spanish/player/{session_id}/text?source=speakers&render_mode=sentence_list"
    )


def test_player_page_preserves_renderable_text_tokens_in_existing_client_state(runtime_env: Path, url_app: Flask) -> None:
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
    _write_text_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001", include_tokens=True)

    with url_app.test_request_context():
        page = build_player_page("de", "spanish", session_id, "text", "speakers")

    assert page is not None
    first_item = page["player"]["items"][0]
    assert first_item["item_id"] == "d_01"
    assert [token["token_id"] for token in first_item["tokens"]] == ["d_01_tok_01", "d_01_tok_02"]
    assert [segment["kind"] for segment in first_item["text_segments"]] == ["token", "text", "token", "text"]
    speaker_item = page["player"]["client_state"]["speakers"][0]["items"][0]
    assert speaker_item["itemId"] == "d_01"
    assert [token["tokenId"] for token in speaker_item["tokens"]] == ["d_01_tok_01", "d_01_tok_02"]


def test_player_route_renders_text_token_spans_when_alignment_tokens_exist(runtime_env: Path, url_app: Flask) -> None:
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
    _write_text_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001", include_tokens=True)

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/player/{session_id}/text?source=speakers&render_mode=sentence_list")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-player-token-id="d_01_tok_01"' in html
    assert 'data-player-token-id="d_01_tok_02"' in html
    assert 'data-player-token-id="d_01_tok_invalid"' not in html
    assert 'pm-player-token' in html
    assert 'class="pm-player-list__meta-inline">d_01<' not in html


def test_player_route_renders_spoken_title_item_as_separate_running_text_block(runtime_env: Path, url_app: Flask) -> None:
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
    _write_text_player_artifacts(runtime_env, "spanish", session_id, "ES-L-0001", include_spoken_title_item=True)

    _set_test_auth(url_app)
    client = url_app.test_client()

    running_text_response = client.get(f"/de/research/spanish/player/{session_id}/text?source=speakers")
    sentence_list_response = client.get(
        f"/de/research/spanish/player/{session_id}/text?source=speakers&render_mode=sentence_list"
    )

    assert running_text_response.status_code == 200
    assert sentence_list_response.status_code == 200

    running_text_html = running_text_response.get_data(as_text=True)
    sentence_list_html = sentence_list_response.get_data(as_text=True)

    assert 'pm-player-text-flow__spoken-title' in running_text_html
    assert 'pm-player-text-flow__text--title' in running_text_html
    assert 'Hoy miro el reloj con calma antes de salir.' in running_text_html
    assert 'pm-player-text-flow__spoken-title' not in sentence_list_html
    assert 'class="pm-player-list__meta-inline">D<' not in sentence_list_html
    assert 'class="pm-player-list__meta-time">' in sentence_list_html


def test_player_route_keeps_sentence_only_text_markup_when_no_tokens_exist(runtime_env: Path, url_app: Flask) -> None:
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

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/player/{session_id}/text?source=speakers")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-player-token' not in html
    assert 'data-player-token-id=' not in html


def test_player_route_integrates_text_view_switch_into_content_header(runtime_env: Path, url_app: Flask) -> None:
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

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/player/{session_id}/text?source=speakers")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'pm-player-view-bar' not in html
    assert '>Ansicht<' not in html
    assert 'promat-panel__language-title">Spanisch-Korpus<' in html
    assert 'class="pm-player-view-switch"' in html
    assert '>Liste<' in html
    assert '>Text<' in html
    assert '>2 Items<' in html
    assert '?download=1' in html
    assert 'download aria-label=' in html


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
            "speakers",
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
        f"/de/research/spanish/player/{primary_session_id}/wordlist?source=speakers"
    )
    assert [row["label"] for row in page["summary_cards"][0]["rows"]] == [
        "Person-ID",
        "Aufnahmedatum",
        "Geschlecht",
        "Sprachaufenthalte",
        "Explorator:in",
    ]
    assert any(badge["label"] == "B1" for badge in page["summary_cards"][0]["badges"])
    assert page["player"]["compare"]["sequence_toggle"]["label"] == "Beide abspielen"
    assert page["player"]["compare"]["sequence_toggle"]["enabled"] is True
    assert any(option["current"] for option in page["player"]["compare"]["switchers"]["compare"]["options"])
    assert page["player"]["client_state"]["compareOpen"] is True
    assert page["player"]["client_state"]["modeHrefs"]["manual"].endswith(
        f"/de/research/spanish/player/{primary_session_id}/wordlist?source=speakers&compare_session={compare_session_id}&compare_mode=manual"
    )
    assert page["player"]["client_state"]["modeHrefs"]["sequence"].endswith(
        f"/de/research/spanish/player/{primary_session_id}/wordlist?source=speakers&compare_session={compare_session_id}"
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
            "speakers",
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

    _set_test_auth(url_app)
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
    assert 'Aufnahmejahr' in html
    assert 'Explorator:in' not in html
    assert 'pm-nav-pill pm-nav-pill--secondary pm-nav-pill--medium' in html
    assert 'pm-nav-pill pm-nav-pill--secondary pm-nav-pill--small pm-player-meta-card__action pm-player-meta-card__action--profile pm-player-meta-card__profile-link' in html
    assert 'pm-player-control-button pm-player-toolbar__toggle pm-player-icon-button' in html
    assert 'pm-player-panel--control-bar' in html
    assert 'pm-player-list pm-player-list--single' in html


def test_research_comparison_static_js_uses_non_legacy_control_classes(url_app: Flask) -> None:
    client = url_app.test_client()

    response = client.get('/static/js/pages/research-comparison.js')

    assert response.status_code == 200
    js = response.get_data(as_text=True)
    assert 'pm-action-button pm-action-button--secondary pm-action-button--medium' in js
    assert 'class="pm-material-choice${isCurrent ? " is-current" : ""}${isDisabled ? " is-disabled" : ""}"' in js


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

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get(f"/de/research/spanish/player/{primary_session_id}/wordlist?source=speakers")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'data-player-compare-open="false"' in html
    assert 'data-player-session-menu="primary"' in html
    assert 'data-player-session-menu="secondary"' in html
    assert re.search(r'data-player-compare-add>\s*<span class="material-symbols-rounded pm-interaction__icon pm-interaction__icon--leading" aria-hidden="true">add</span>\s*<span class="pm-action-button__label">Vergleich</span>', html, re.S) is not None
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

    _set_test_auth(url_app)
    client = url_app.test_client()
    response = client.get(
        f"/de/research/spanish/player/{primary_session_id}/wordlist?source=speakers&compare_session={compare_session_id}"
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
    assert html.count('pm-player-meta-card__action--profile') == 2
    assert html.count('<span class="pm-nav-pill__label">Profil</span>') == 2
    assert 'Vergleich entfernen' in html
    assert re.search(r'pm-player-meta-card__action pm-player-meta-card__action--compare-remove" href="[^"]+" data-player-compare-remove>\s*<span class="material-symbols-rounded pm-interaction__icon pm-interaction__icon--leading" aria-hidden="true">remove</span>\s*<span class="pm-action-button__label">Vergleich entfernen</span>', html, re.S) is not None
    assert f'href="/de/research/spanish/player/{primary_session_id}/wordlist?source=speakers"' in html
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

    _set_test_auth(url_app)
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

    _set_test_auth(url_app)
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