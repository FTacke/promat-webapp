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

from app.research_presets import (  # noqa: E402
    ResearchConfigError,
    clear_research_preset_caches,
    load_phenomena_preset_map,
    load_phenomena_presets,
    load_player_config,
    load_task_catalog,
    normalize_task_item_reference,
)


@pytest.fixture
def runtime_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "data" / "config" / "research_player").mkdir(parents=True, exist_ok=True)
    (tmp_path / "public").mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(tmp_path))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(tmp_path / "public"))

    clear_research_preset_caches()
    yield tmp_path
    clear_research_preset_caches()


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _minimal_catalog(task: str, language: str = "spanish") -> dict[str, object]:
    if task == "wordlist":
        return {
            "task": "wordlist",
            "language": language,
            "items": [
                {"item_id": "wl_001", "item_number": "1", "text": "mesa"},
                {"item_id": "wl_002", "item_number": "2", "text": "reloj"},
            ],
        }
    if task == "text":
        return {
            "task": "text",
            "language": language,
            "display_label": "Satzliste",
            "items": [
                {"item_id": "d_01", "item_number": "D1", "text": "Hoy miro el reloj con calma antes de salir."},
                {"item_id": "qy_01", "item_number": "QY1", "text": "¿El vaso está lleno de vino ahora?"},
            ],
        }
    raise AssertionError(f"Unsupported test task: {task}")


def _write_minimal_language_config(runtime_root: Path, *, presets: list[dict[str, object]]) -> None:
    base_dir = runtime_root / "data" / "config" / "research_player" / "spanish"
    _write_json(base_dir / "task_catalogs" / "wordlist.json", _minimal_catalog("wordlist"))
    _write_json(base_dir / "task_catalogs" / "text.json", _minimal_catalog("text"))
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
    _write_json(base_dir / "phenomena_presets.json", {"language": "spanish", "presets": presets})


def test_load_player_config_reads_spanish_defaults_from_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))
    clear_research_preset_caches()

    config = load_player_config("spanish")

    assert config.language == "spanish"
    assert config.text.default_render_mode == "sentence_list"
    assert config.text.display_label == "Satzliste"


def test_load_phenomena_presets_reads_mixed_spanish_presets_from_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))
    clear_research_preset_caches()

    presets = load_phenomena_presets("spanish")

    assert len(presets) >= 4
    preset_map = load_phenomena_preset_map("spanish")
    assert "question_prosody_paths" in preset_map
    assert any(reference.task == "wordlist" for reference in preset_map["question_prosody_paths"].items)
    assert any(reference.task == "text" for reference in preset_map["question_prosody_paths"].items)


def test_load_task_catalog_reads_existing_text_display_label_from_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))
    clear_research_preset_caches()

    catalog = load_task_catalog("spanish", "text")

    assert catalog.display_label == "Satzliste"
    assert "d_01" in catalog.items_by_id
    assert "qw_10" in catalog.items_by_id


def test_normalize_task_item_reference_keeps_optional_fields() -> None:
    reference = normalize_task_item_reference(
        {
            "task": "text",
            "item_id": "d_01",
            "segment_id": "rise",
            "note": "focus on phrase-final movement",
            "sort_key": "010",
        },
        context="unit test",
    )

    assert reference.task == "text"
    assert reference.item_id == "d_01"
    assert reference.segment_id == "rise"
    assert reference.note == "focus on phrase-final movement"
    assert reference.sort_key == "010"


def test_load_phenomena_presets_rejects_unknown_item_reference(runtime_env: Path) -> None:
    _write_minimal_language_config(
        runtime_env,
        presets=[
            {
                "preset_id": "bad_reference",
                "label": "Bad",
                "description": "Contains an unknown wordlist item.",
                "language": "spanish",
                "items": [
                    {"task": "wordlist", "item_id": "wl_999"},
                ],
            }
        ],
    )

    with pytest.raises(ResearchConfigError, match="Unknown item_id 'wl_999'"):
        load_phenomena_presets("spanish")


def test_load_phenomena_presets_rejects_unknown_task_catalog(runtime_env: Path) -> None:
    _write_minimal_language_config(
        runtime_env,
        presets=[
            {
                "preset_id": "interview_reference",
                "label": "Interview",
                "description": "Uses a task without a configured task catalog.",
                "language": "spanish",
                "items": [
                    {"task": "interview", "item_id": "seg_001"},
                ],
            }
        ],
    )

    with pytest.raises(ResearchConfigError, match="No task catalog configured for task 'interview'"):
        load_phenomena_presets("spanish")


def test_load_phenomena_presets_rejects_duplicate_item_references(runtime_env: Path) -> None:
    _write_minimal_language_config(
        runtime_env,
        presets=[
            {
                "preset_id": "duplicate_items",
                "label": "Duplicate",
                "description": "Contains the same item twice.",
                "language": "spanish",
                "items": [
                    {"task": "wordlist", "item_id": "wl_001"},
                    {"task": "wordlist", "item_id": "wl_001"},
                ],
            }
        ],
    )

    with pytest.raises(ResearchConfigError, match="Duplicate preset item reference 'wordlist:wl_001'"):
        load_phenomena_presets("spanish")


def test_load_phenomena_presets_rejects_language_mismatch(runtime_env: Path) -> None:
    _write_minimal_language_config(
        runtime_env,
        presets=[
            {
                "preset_id": "wrong_language",
                "label": "Wrong language",
                "description": "Preset language mismatches the file and request.",
                "language": "german",
                "items": [
                    {"task": "wordlist", "item_id": "wl_001"},
                ],
            }
        ],
    )

    with pytest.raises(ResearchConfigError, match="language mismatch"):
        load_phenomena_presets("spanish")


def test_load_phenomena_presets_accepts_mixed_wordlist_and_text(runtime_env: Path) -> None:
    _write_minimal_language_config(
        runtime_env,
        presets=[
            {
                "preset_id": "mixed_ok",
                "label": "Mixed ok",
                "description": "Contains both wordlist and text references.",
                "language": "spanish",
                "items": [
                    {"task": "wordlist", "item_id": "wl_001"},
                    {"task": "text", "item_id": "d_01"},
                    {"task": "text", "item_id": "qy_01"},
                ],
            }
        ],
    )

    presets = load_phenomena_presets("spanish")

    assert len(presets) == 1
    assert [reference.task for reference in presets[0].items] == ["wordlist", "text", "text"]
