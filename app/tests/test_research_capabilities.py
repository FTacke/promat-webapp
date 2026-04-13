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
from app.research_sessions import available_task_keys_for_session


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


@pytest.fixture
def runtime_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "data" / "config" / "research_player").mkdir(parents=True, exist_ok=True)
    (tmp_path / "public").mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(tmp_path))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(tmp_path / "public"))

    base_dir = tmp_path / "data" / "config" / "research_player" / "spanish"
    _write_json(
        base_dir / "task_catalogs" / "wordlist.json",
        {
            "task": "wordlist",
            "language": "spanish",
            "display_label": "Wortliste",
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
            "items": [{"item_id": "wl_001", "item_number": "1", "text": "mesa"}],
        },
    )
    _write_json(
        base_dir / "task_catalogs" / "text.json",
        {
            "task": "text",
            "language": "spanish",
            "display_label": "Satzliste",
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
                    "text": "Hoy miro el reloj con calma.",
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
            "language": "spanish",
            "text": {
                "default_render_mode": "sentence_list",
                "display_label": "Satzliste",
            },
        },
    )
    _write_json(base_dir / "phenomena_presets.json", {"language": "spanish", "presets": []})

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
    assert get_research_page_surface_mode("spanish", "comparison") == "productive"
    assert get_research_page_surface_mode("french", "comparison") == "placeholder"


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