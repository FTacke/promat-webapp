from __future__ import annotations

import sys
from pathlib import Path

import pytest


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

import import_batch_to_production as production_importer  # noqa: E402


def test_importer_smoke_skips_missing_working_text_inputs_in_write_mode(tmp_path: Path) -> None:
    batch_dir = tmp_path / "spanish_batch_20260525"
    batch_dir.mkdir()

    notes = production_importer._run_text_pipeline(
        batch_dir=batch_dir,
        person_id="ES-L-0010",
        target_language="es",
        mfa_executable="docker",
        dry_run=False,
    )

    assert notes == [
        "Skipped text MFA for ES-L-0010: working text inputs are not present; task will remain missing unless existing runtime artifacts are available."
    ]


def test_importer_smoke_dry_run_does_not_require_written_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    person_id = "EN-L-0008"
    (batch_dir / "working" / person_id / "text" / "source").mkdir(parents=True)
    (batch_dir / "working" / person_id / "text" / "alignment").mkdir()
    (batch_dir / "working" / person_id / "text" / "source" / "text.wav").write_bytes(b"wav")
    (batch_dir / "working" / person_id / "text" / "alignment" / "text.TextGrid").write_text(
        "textgrid", encoding="utf-8"
    )
    text_catalog_path = tmp_path / "text.json"
    text_catalog_path.write_text('{"task": "text", "language": "en", "items": []}\n', encoding="utf-8")

    monkeypatch.setattr(production_importer, "_text_task_catalog_path", lambda target_language: text_catalog_path)
    monkeypatch.setattr(
        production_importer,
        "prepare_text_mfa_for_person",
        lambda **kwargs: {
            "segments": 55,
            "warnings": ["EN-L-0008 text: omitted t_01 because the spoken title was not recorded"],
        },
    )

    def fail_run_text_mfa_for_person(**kwargs):
        raise AssertionError("dry-run must not require a written mfa_manifest.json")

    monkeypatch.setattr(production_importer, "run_text_mfa_for_person", fail_run_text_mfa_for_person)

    notes = production_importer._run_text_pipeline(
        batch_dir=batch_dir,
        person_id=person_id,
        target_language="en",
        mfa_executable="docker",
        dry_run=True,
    )

    assert notes == [
        "Prepared text MFA corpus for EN-L-0008: segments=55",
        "Text MFA prep warning for EN-L-0008: EN-L-0008 text: omitted t_01 because the spoken title was not recorded",
        "Planned MFA for EN-L-0008: executable=docker",
        "Planned working text alignment import for EN-L-0008 after MFA outputs are available.",
    ]
