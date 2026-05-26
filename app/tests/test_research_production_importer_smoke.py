from __future__ import annotations

from pathlib import Path

import pytest

from test_research_production_importer import (
    test_run_text_pipeline_dry_run_does_not_require_written_manifest as _dry_run_does_not_require_written_manifest,
)
from test_research_production_importer import (
    test_run_text_pipeline_skips_missing_working_text_inputs_in_write_mode as _skips_missing_working_text_inputs,
)


def test_importer_smoke_dry_run_does_not_require_written_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _dry_run_does_not_require_written_manifest(tmp_path, monkeypatch)


def test_importer_smoke_skips_missing_working_text_inputs_in_write_mode(tmp_path: Path) -> None:
    _skips_missing_working_text_inputs(tmp_path)
