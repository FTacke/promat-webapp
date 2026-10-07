"""storage_inventory.py stays read-only and consumes the preservation model without requiring K: or production."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))
INTAKE_DIR = TEST_REPO_ROOT / "scripts" / "research_data_intake"
sys.path.insert(0, str(INTAKE_DIR))

import fixity  # noqa: E402
import preservation as pres  # noqa: E402
from test_archive_preservation import UNIT, _archive_session  # noqa: E402

_spec = importlib.util.spec_from_file_location("storage_inventory", TEST_REPO_ROOT / "scripts" / "storage_inventory.py")
inventory = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inventory)


def _args(**overrides) -> argparse.Namespace:
    values = {"preservation_root": None, "measure_preservation": False, "cleanup_report": None, "json": True}
    values.update(overrides)
    return argparse.Namespace(**values)


@pytest.fixture
def archive(tmp_path: Path, monkeypatch) -> Path:
    root = tmp_path / "archive"
    _archive_session(tmp_path, root)
    monkeypatch.setenv("PROMAT_LOCAL_ARCHIVE_ROOT", str(root))
    monkeypatch.delenv(pres.PRESERVATION_ROOT_ENV, raising=False)
    return root


def test_inventory_without_preservation_root_reports_unconfigured_and_pending(archive: Path) -> None:
    section = inventory.preservation_section(_args())
    assert section["configured"] is False and section["reachable"] is False
    assert section["unit_states"][pres.STATE_PENDING] == 1
    assert section["unit_states"][pres.STATE_PRESERVED] == 0


def test_inventory_reads_env_root_and_never_creates_it(archive: Path, tmp_path: Path, monkeypatch) -> None:
    missing = tmp_path / "unmounted_volume" / "root"
    monkeypatch.setenv(pres.PRESERVATION_ROOT_ENV, str(missing))
    section = inventory.preservation_section(_args())
    assert section["source"] == "PROMAT_PRESERVATION_ROOT" and section["reachable"] is False
    assert not missing.exists() and not missing.parent.exists()


def test_inventory_reports_quick_states_and_is_read_only(archive: Path, tmp_path: Path) -> None:
    root = pres.open_preservation_root(tmp_path / "inst", archive_root=archive, initialize=True)
    pres.copy_unit(archive, UNIT, root, execute=True)
    before = (fixity.compute_manifest(archive), fixity.compute_manifest(tmp_path / "inst"))
    section = inventory.preservation_section(_args(preservation_root=str(tmp_path / "inst")))
    assert section["root_id"] == root.root_id
    # The quick check never claims cleanup eligibility.
    assert section["unit_states"][pres.STATE_PRESERVED] == 1
    assert section["unit_states"][pres.STATE_CLEANUP_ELIGIBLE] == 0
    assert before == (fixity.compute_manifest(archive), fixity.compute_manifest(tmp_path / "inst"))


def test_inventory_consumes_cleanup_report_json_without_recomputing(archive: Path, tmp_path: Path) -> None:
    root = pres.open_preservation_root(tmp_path / "inst", archive_root=archive, initialize=True)
    pres.copy_unit(archive, UNIT, root, execute=True)
    report = pres.cleanup_eligibility_report(archive, root)
    path = tmp_path / "cleanup.json"
    path.write_text(json.dumps({"cleanup": {k: v for k, v in report.items() if k != "units"}}), encoding="utf-8")
    section = inventory.preservation_section(_args(preservation_root=str(tmp_path / "inst"), cleanup_report=str(path)))
    assert section["cleanup_report"]["counts"][pres.STATE_CLEANUP_ELIGIBLE] == 1
    assert "snapshot" in section["cleanup_report"]["snapshot_warning"]


def test_inventory_rejects_foreign_or_deleting_cleanup_json(archive: Path, tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"schema": "other", "deletes_anything": True}), encoding="utf-8")
    assert "error" in inventory.preservation_section(_args(cleanup_report=str(bad)))["cleanup_report"]
    assert "error" in inventory.preservation_section(_args(cleanup_report=str(tmp_path / "missing.json")))["cleanup_report"]


def test_inventory_lists_archive_root_entries_outside_the_unit_copy(archive: Path) -> None:
    (archive / "praat_pipeline").mkdir()
    (archive / "informanten_intake_20260525").mkdir()
    section = inventory.preservation_section(_args())
    assert section["archive_root_entries_not_covered_by_unit_copy"] == ["informanten_intake_20260525", "praat_pipeline"]


def test_inventory_text_output_runs_without_k_drive(archive: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(inventory, "measured_locations", lambda: [])
    monkeypatch.setattr(inventory, "worktrees", lambda: [])
    assert inventory.main([]) == 0
    out = capsys.readouterr().out
    assert "Preservation status" in out and "PRESERVATION_PENDING=1" in out


def test_inventory_source_contains_no_deletion() -> None:
    text = (TEST_REPO_ROOT / "scripts" / "storage_inventory.py").read_text(encoding="utf-8")
    assert not any(token in text for token in ("rmtree", "os.remove", ".unlink(", "os.rmdir"))


def test_intake_never_reads_the_preservation_root() -> None:
    """Setting PROMAT_PRESERVATION_ROOT must not redirect intake writes: only the preservation tools read it."""
    # storage_roots.py only names the variables; it never resolves one root from another.
    allowed = {"preservation.py", "archive_preservation.py", "storage_roots.py"}
    for path in INTAKE_DIR.glob("*.py"):
        if path.name in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        assert "PRESERVATION_ROOT" not in text and "import preservation" not in text, path.name
    from intake_storage import IntakeStorageError, get_local_archive_root

    os.environ["PROMAT_PRESERVATION_ROOT"] = "/somewhere/else"
    try:
        # With only the preservation root set, intake has no archive root at all: it fails instead of borrowing it.
        with pytest.raises(IntakeStorageError):
            get_local_archive_root()
    finally:
        del os.environ["PROMAT_PRESERVATION_ROOT"]
