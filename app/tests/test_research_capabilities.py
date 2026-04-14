from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

from app.research_access import is_public_research_page, requires_research_auth
from app.research_capabilities import (
    comparison_view_task_keys,
    get_research_page_order,
    get_research_page_surface_mode,
    get_research_task_capability,
    get_research_task_label,
    phenomena_task_keys,
    player_compare_task_keys,
    player_productive_task_keys,
    player_visible_task_keys,
    resolve_player_render_capability,
    set_filter_task_keys,
)
from app.research_presets import clear_research_preset_caches
from app.research_sessions import available_task_keys_for_session, load_language_sessions, load_person_records


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_minimal_catalog_config(runtime_root: Path, *, language_slug: str, display_label_de: str) -> None:
    base_dir = runtime_root / "data" / "config" / "research_player" / language_slug
    _write_json(
        base_dir / "task_catalogs" / "wordlist.json",
        {
            "task": "wordlist",
            "language": language_slug,
            "display_label": "Wortliste" if language_slug == "spanish" else "Wordlist",
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
            "items": [{"item_id": "wl_001", "item_number": "1", "text": "mesa" if language_slug == "spanish" else "table"}],
        },
    )
    _write_json(
        base_dir / "task_catalogs" / "text.json",
        {
            "task": "text",
            "language": language_slug,
            "display_label": display_label_de,
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
                    "item_id": "t_01" if language_slug == "english" else "d_01",
                    "item_number": "T1" if language_slug == "english" else "D1",
                    "text": "The Boy who Cried Wolf" if language_slug == "english" else "Hoy miro el reloj con calma.",
                    "text_container_id": "story_01",
                    "text_order_index": 1,
                    "paragraph_break_before": True,
                    "paragraph_id": "p1",
                }
            ],
        },
    )
    _write_json(
        base_dir / "player_config.json",
        {
            "language": language_slug,
            "text": {
                "default_render_mode": "running_text" if language_slug == "english" else "sentence_list",
                "display_label": display_label_de,
            },
        },
    )
    _write_json(
        base_dir / "phenomena_presets.json",
        {
            "language": language_slug,
            "presets": [
                {
                    "preset_id": "starter_preset",
                    "label": "Starter",
                    "description": "Minimal preset for readiness tests.",
                    "language": language_slug,
                    "items": [
                        {"task": "wordlist", "item_id": "wl_001"},
                        {"task": "text", "item_id": "t_01" if language_slug == "english" else "d_01"},
                    ],
                }
            ],
        },
    )


def _write_runtime_session(runtime_root: Path, *, language_slug: str, person_id: str, session_id: str) -> None:
    session_dir = runtime_root / "data" / "sessions" / language_slug / session_id
    (session_dir / "alignment").mkdir(parents=True, exist_ok=True)
    (session_dir / "derived").mkdir(parents=True, exist_ok=True)
    (session_dir / "items" / "wordlist").mkdir(parents=True, exist_ok=True)
    (session_dir / "items" / "text").mkdir(parents=True, exist_ok=True)

    _write_json(
        session_dir / "metadata.json",
        {
            "person_id": person_id,
            "session_id": session_id,
            "target_language": "en",
            "speaker_type": "learner",
            "l1": "DE",
            "l1_additional": [],
            "mother_l1": "DE",
            "father_l1": "DE",
            "additional_languages": [],
            "gender": "female",
            "birth_year": 2002,
            "current_region": "Hessen",
            "childhood_region": "Hessen",
            "origin_country": None,
            "origin_region": None,
            "standard_variety": None,
            "level_code": "B2",
            "level_self": "B2",
            "recording_year": 2026,
            "recording_date": "2026-02-26",
            "context": "baseline",
            "recorded_by": "Marlon Merte",
            "needs_review": False,
            "notes": None,
            "tasks": [
                {"task_type": "wordlist", "label": "Wordlist", "source_file": "source/wordlist.wav", "alignment_file": "alignment/wordlist.TextGrid", "derived_file": "derived/wordlist.mp3"},
                {"task_type": "text", "label": "Text", "source_file": "source/text.wav", "alignment_file": "alignment/text.TextGrid", "derived_file": "derived/text.mp3"},
            ],
        },
    )
    _write_json(
        session_dir / "alignment" / "wordlist.json",
        {
            "session_id": session_id,
            "person_id": person_id,
            "task": "wordlist",
            "audio": {"full_mp3": "derived/wordlist.mp3"},
            "items": [
                {
                    "item_id": "wl_001",
                    "item_number": "1",
                    "text": "table",
                    "start_ms": 0,
                    "end_ms": 1000,
                    "split_mp3": "items/wordlist/wl_001.mp3",
                }
            ],
        },
    )
    _write_json(
        session_dir / "alignment" / "text.json",
        {
            "session_id": session_id,
            "person_id": person_id,
            "task": "text",
            "audio": {"full_mp3": "derived/text.mp3"},
            "items": [
                {
                    "item_id": "t_01",
                    "item_number": "T1",
                    "text": "The Boy who Cried Wolf",
                    "start_ms": 0,
                    "end_ms": 1000,
                    "split_mp3": "items/text/t_01.mp3",
                }
            ],
        },
    )
    (session_dir / "derived" / "wordlist.mp3").write_bytes(b"\xff\xfb\x90\x64")
    (session_dir / "derived" / "text.mp3").write_bytes(b"\xff\xfb\x90\x64")
    (session_dir / "items" / "wordlist" / "wl_001.mp3").write_bytes(b"\xff\xfb\x90\x64")
    (session_dir / "items" / "text" / "t_01.mp3").write_bytes(b"\xff\xfb\x90\x64")


@pytest.fixture
def runtime_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "data" / "config" / "research_player").mkdir(parents=True, exist_ok=True)
    (tmp_path / "public").mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(tmp_path))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(tmp_path / "public"))

    _write_minimal_catalog_config(tmp_path, language_slug="spanish", display_label_de="Satzliste")

    clear_research_preset_caches()
    yield tmp_path
    clear_research_preset_caches()


def test_research_capability_layer_defines_canonical_page_order_access_and_surface_modes() -> None:
    assert get_research_page_order() == (
        ("design", "research.design"),
        ("speakers", "research.speakers"),
        ("recordings", "research.recordings"),
        ("comparison", "research.comparison"),
        ("phenomena", "research.phenomena"),
    )
    assert is_public_research_page("design") is True
    assert requires_research_auth(page_slug="comparison") is True
    assert requires_research_auth(detail_route="player") is True
    assert get_research_page_surface_mode("french", "comparison") == "placeholder"


def test_surface_modes_become_productive_when_runtime_and_config_are_present(runtime_env: Path) -> None:
    _write_minimal_catalog_config(runtime_env, language_slug="english", display_label_de="Text")
    _write_runtime_session(
        runtime_env,
        language_slug="english",
        person_id="EN-L-0001",
        session_id="EN-L-0001-2026-S01",
    )
    clear_research_preset_caches()
    load_language_sessions.cache_clear()
    load_person_records.cache_clear()

    assert get_research_page_surface_mode("english", "design") == "content"
    assert get_research_page_surface_mode("english", "speakers") == "productive"
    assert get_research_page_surface_mode("english", "recordings") == "productive"
    assert get_research_page_surface_mode("english", "comparison") == "productive"
    assert get_research_page_surface_mode("english", "phenomena") == "productive"
    assert get_research_page_surface_mode("german", "speakers") == "placeholder"


@pytest.mark.parametrize(
    ("task_key", "productive", "compare", "set_filter", "phenomena", "native_ok"),
    [
        ("wordlist", True, True, True, True, True),
        ("text", True, True, True, True, True),
        ("interview", False, False, False, False, False),
    ],
)
def test_research_task_capabilities_cover_core_workbench_rules(
    task_key: str,
    productive: bool,
    compare: bool,
    set_filter: bool,
    phenomena: bool,
    native_ok: bool,
) -> None:
    capability = get_research_task_capability(task_key)

    assert capability is not None
    assert capability.productive_in_player is productive
    assert capability.supports_player_compare is compare
    assert capability.supports_set_filtering is set_filter
    assert capability.visible_in_phenomena is phenomena
    assert capability.available_for_native_speakers is native_ok


def test_research_capability_layer_exposes_canonical_task_subsets() -> None:
    assert player_visible_task_keys() == ("wordlist", "text", "interview")
    assert player_productive_task_keys() == ("wordlist", "text")
    assert player_compare_task_keys() == ("wordlist", "text")
    assert set_filter_task_keys() == ("wordlist", "text")
    assert phenomena_task_keys() == ("wordlist", "text")
    assert comparison_view_task_keys() == ("all", "wordlist", "text")


def test_available_task_keys_for_session_uses_capabilities_for_native_interview_exclusion() -> None:
    documented = ("wordlist", "text", "interview")

    assert available_task_keys_for_session(type("Session", (), {"documented_task_types": documented, "speaker_type": "learner"})()) == (
        "wordlist",
        "text",
        "interview",
    )
    assert available_task_keys_for_session(type("Session", (), {"documented_task_types": documented, "speaker_type": "native_speaker"})()) == (
        "wordlist",
        "text",
    )


@pytest.mark.parametrize(
    ("task_key", "allowed_views", "default_view", "compare_selected", "is_set_excerpt", "expected_modes", "expected_default", "supports_text_view"),
    [
        ("wordlist", ("list",), "list", False, False, (), None, False),
        ("text", ("text", "list"), "text", False, False, ("sentence_list", "running_text"), "running_text", True),
        ("text", ("text", "list"), "text", True, False, ("sentence_list",), "sentence_list", False),
        ("text", ("text", "list"), "text", False, True, ("sentence_list",), "sentence_list", False),
        ("interview", None, None, False, False, (), None, False),
    ],
)
def test_resolve_player_render_capability_applies_task_and_context_rules(
    task_key: str,
    allowed_views: tuple[str, ...] | None,
    default_view: str | None,
    compare_selected: bool,
    is_set_excerpt: bool,
    expected_modes: tuple[str, ...],
    expected_default: str | None,
    supports_text_view: bool,
) -> None:
    capability = resolve_player_render_capability(
        task_key,
        source_allowed_views=allowed_views,
        source_default_view=default_view,
        compare_selected=compare_selected,
        is_set_excerpt=is_set_excerpt,
    )

    assert capability.allowed_render_modes == expected_modes
    assert capability.default_render_mode == expected_default
    assert capability.supports_text_view is supports_text_view


def test_get_research_task_label_uses_catalog_display_label_when_available(runtime_env: Path) -> None:
    assert get_research_task_label("text", "de", variant="material", language_slug="spanish") == "Satzliste"
    assert get_research_task_label("wordlist", "en", variant="material", language_slug="spanish") == "Wordlist"
    assert get_research_task_label("interview", "de", variant="material", language_slug="spanish") == "Interview"