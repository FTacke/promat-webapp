"""Guards for the tracked minimal research-player fixtures and the config validator.

The real catalogs are operator-owned runtime configuration (not in git). These tests prove that the fixtures the
canonical suite relies on are valid for the app's own loaders, that connected-text semantics (the structural part of
the former repo-data assertions) are exercised without production content, and that the operator validator
detects broken configuration.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

from app.research_presets import load_task_catalog  # noqa: E402


VALIDATOR = TEST_REPO_ROOT / "scripts" / "research_data_intake" / "validate_research_config.py"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "runtime"


def _run_validator(runtime_root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if key != "PROMAT_RUNTIME_ROOT"}
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--runtime-root", str(runtime_root), *extra],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


@pytest.mark.parametrize(
    ("language", "task"),
    [
        ("spanish", "wordlist"),
        ("spanish", "text"),
        ("english", "wordlist"),
        ("english", "text"),
        ("french", "wordlist"),
        ("french", "text"),
    ],
)
def test_fixture_catalogs_load_through_app_loader(fixture_runtime_root: Path, language: str, task: str) -> None:
    catalog = load_task_catalog(language, task)

    assert catalog.language == language
    assert catalog.task == task
    assert catalog.items_by_id


@pytest.mark.parametrize("language", ["english", "french"])
def test_connected_text_catalog_semantics(fixture_runtime_root: Path, language: str) -> None:
    catalog = load_task_catalog(language, "text")

    assert catalog.display_label == "Text"
    assert catalog.player_source.source_kind == "text"
    assert catalog.player_source.content_mode == "connected_text"
    assert catalog.player_source.default_view == "text"
    assert catalog.player_source.allowed_views == ("text", "list")
    assert all(item.text_container_id == f"{language}:text" for item in catalog.items_by_id.values())


def test_english_text_fixture_marks_unspoken_title_item(fixture_runtime_root: Path) -> None:
    catalog = load_task_catalog("english", "text")

    assert catalog.items_by_id["t_01"].spoken_title_item is True
    assert catalog.items_by_id["t_18"].spoken_title_item is False


def test_french_wordlist_fixture_uses_canonical_theatre_spelling(fixture_runtime_root: Path) -> None:
    assert load_task_catalog("french", "wordlist").items_by_id["wl_014"].text == "théâtre"


def test_validator_accepts_fixture_runtime_root() -> None:
    result = _run_validator(FIXTURE_ROOT)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[ok] spanish/wordlist" in result.stdout
    assert "[ok] french/text" in result.stdout


def test_validator_require_complete_flags_missing_player_config() -> None:
    result = _run_validator(FIXTURE_ROOT, "--require-complete")

    assert result.returncode == 1
    assert "player_config.json not present" in result.stdout


def test_validator_rejects_broken_catalog(tmp_path: Path) -> None:
    catalog_path = tmp_path / "data" / "config" / "research_player" / "german" / "task_catalogs" / "wordlist.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps({"task": "wordlist", "language": "german", "items": []}), encoding="utf-8")

    result = _run_validator(tmp_path)

    assert result.returncode == 1
    assert "german/wordlist" in result.stdout


def test_validator_fails_when_no_configuration_exists(tmp_path: Path) -> None:
    (tmp_path / "data" / "config").mkdir(parents=True)

    result = _run_validator(tmp_path)

    assert result.returncode == 1
    assert "no research-player configuration found" in result.stderr
