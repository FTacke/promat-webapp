from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

from import_batch_to_production import _build_task_entries, parse_args  # noqa: E402


def test_build_task_entries_lists_runtime_only_files(tmp_path: Path) -> None:
    session_dir = tmp_path / "ES-L-0001-2026-S01"
    (session_dir / "alignment").mkdir(parents=True, exist_ok=True)
    (session_dir / "derived").mkdir(parents=True, exist_ok=True)
    (session_dir / "items" / "wordlist").mkdir(parents=True, exist_ok=True)
    (session_dir / "alignment" / "wordlist.json").write_text("{}\n", encoding="utf-8")
    (session_dir / "derived" / "wordlist.mp3").write_bytes(b"wordlist-mp3")
    (session_dir / "items" / "wordlist" / "wl_001.mp3").write_bytes(b"item-mp3")

    tasks, files = _build_task_entries(session_dir)

    assert [task["task_type"] for task in tasks] == ["wordlist"]
    assert all("source_file" not in task for task in tasks)
    assert {entry["path"] for entry in files} == {
        "metadata.json",
        "alignment/wordlist.json",
        "derived/wordlist.mp3",
        "items/wordlist/wl_001.mp3",
    }
    assert all(not entry["path"].startswith("raw/") for entry in files)
    assert all(not entry["path"].startswith("source/") for entry in files)


def test_build_task_entries_skips_native_speaker_interview(tmp_path: Path) -> None:
    session_dir = tmp_path / "ES-N-0001-2026-S01"
    (session_dir / "alignment").mkdir(parents=True, exist_ok=True)
    (session_dir / "derived").mkdir(parents=True, exist_ok=True)
    (session_dir / "alignment" / "interview.json").write_text("{}\n", encoding="utf-8")
    (session_dir / "derived" / "interview.mp3").write_bytes(b"interview-mp3")

    tasks, files = _build_task_entries(
        session_dir,
        person_id="ES-N-0001",
        speaker_type="native_speaker",
    )

    assert tasks == []
    assert files == [{"path": "metadata.json", "file_role": "metadata", "format": "json", "status": "processed"}]


def test_parse_args_hides_obsolete_sync_raw_only_from_help(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["import_batch_to_production.py", "--help"])

    with pytest.raises(SystemExit):
        parse_args()

    captured = capsys.readouterr()
    assert "--sync-raw-only" not in captured.out
    assert "recursive workbook discovery" in captured.out
    assert "--run-working" in captured.out
    assert "--run-mfa" in captured.out
    assert "--cleanup-working-on-success" in captured.out