"""Orphan detection of the Teaching content validator (``scripts/validate_teaching_content.py``)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def validator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("validate_teaching_content_orphans", REPO_ROOT / "scripts" / "validate_teaching_content.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    content = tmp_path / "content" / "teaching"
    topic = content / "spanish" / "topic-one"
    (topic / "media" / "audio" / "variation").mkdir(parents=True)
    (content / "spanish" / "teaching.yaml").write_text("available_ui_langs: [de]\n", encoding="utf-8")
    (topic / "de.yaml").write_text("blocks:\n  - type: audio_example\n    audio: variation/used.mp3\n", encoding="utf-8")
    (topic / "media" / "audio" / "variation" / "used.mp3").write_bytes(b"x")
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "CONTENT_ROOT", content)
    monkeypatch.setattr(module, "MEDIA_EXCEPTIONS_FILE", content / "media-exceptions.yaml")
    return module


def _run(module) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    module.validate_unreferenced_media(errors, warnings, ["spanish"])
    return errors, warnings


def _add_orphan(validator) -> Path:
    orphan = validator.CONTENT_ROOT / "spanish" / "topic-one" / "media" / "audio" / "variation" / "orphan.mp3"
    orphan.write_bytes(b"y")
    return orphan


def test_referenced_media_is_not_reported(validator) -> None:
    assert _run(validator) == ([], [])


def test_unknown_orphan_fails_validation(validator) -> None:
    _add_orphan(validator)
    errors, warnings = _run(validator)
    assert len(errors) == 1 and "spanish/topic-one/media/audio/variation/orphan.mp3" in errors[0]
    assert warnings == []


def test_documented_exception_only_warns(validator) -> None:
    _add_orphan(validator)
    validator.MEDIA_EXCEPTIONS_FILE.write_text(
        "unreferenced_media:\n  - path: spanish/topic-one/media/audio/variation/orphan.mp3\n    status: content_decision_required\n    reason: test\n",
        encoding="utf-8",
    )
    errors, warnings = _run(validator)
    assert errors == []
    assert len(warnings) == 1 and "content_decision_required" in warnings[0]


def test_stale_exception_fails_validation(validator) -> None:
    validator.MEDIA_EXCEPTIONS_FILE.write_text(
        "unreferenced_media:\n  - path: spanish/topic-one/media/audio/variation/used.mp3\n    status: retained\n    reason: test\n",
        encoding="utf-8",
    )
    errors, _ = _run(validator)
    assert any("no longer an unreferenced file" in error for error in errors)


def test_exception_without_reason_is_rejected(validator) -> None:
    _add_orphan(validator)
    validator.MEDIA_EXCEPTIONS_FILE.write_text(
        "unreferenced_media:\n  - path: spanish/topic-one/media/audio/variation/orphan.mp3\n    status: retained\n",
        encoding="utf-8",
    )
    errors, _ = _run(validator)
    assert any("needs path, reason and status" in error for error in errors)


def test_reference_from_a_hub_counts(validator) -> None:
    orphan = _add_orphan(validator)
    hubs = validator.CONTENT_ROOT / "spanish" / "hubs"
    hubs.mkdir()
    (hubs / "de.yaml").write_text(f"cards:\n  - image: variation/{orphan.name}\n", encoding="utf-8")
    assert _run(validator) == ([], [])


def test_the_real_content_tree_has_no_undocumented_orphans() -> None:
    spec = importlib.util.spec_from_file_location("validate_teaching_content_real", REPO_ROOT / "scripts" / "validate_teaching_content.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors: list[str] = []
    module.validate_unreferenced_media(errors, [], sorted(p.name for p in module.CONTENT_ROOT.iterdir() if p.is_dir()))
    assert errors == []
