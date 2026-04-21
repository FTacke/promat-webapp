from __future__ import annotations

import os
import sys
from pathlib import Path


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

from intake_batch_common import ParsedBatchFile, build_batch_inventory  # noqa: E402
from import_batch_to_production import _build_task_entries, _plan_raw_syncs  # noqa: E402


def _parsed_raw_entry(tmp_path: Path, person_id: str, task: str, relative_source: str) -> ParsedBatchFile:
    source_path = tmp_path / relative_source
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_bytes(b"raw-master")
    return ParsedBatchFile(
        source_path=source_path,
        source_root="raw",
        relative_source=relative_source.replace("\\", "/"),
        person_id=person_id,
        task=task,
        stage="raw",
        file_kind="wav",
    )


def test_plan_raw_syncs_marks_sync_keep_and_missing(tmp_path: Path) -> None:
    target_session_dir = tmp_path / "runtime" / "ES-L-0001-2026-S01"
    raw_dir = target_session_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    existing_wordlist = raw_dir / "wordlist.wav"
    existing_wordlist.write_bytes(b"raw-master")

    inventory = build_batch_inventory(
        [
            _parsed_raw_entry(tmp_path, "ES-L-0001", "wordlist", "raw/es_l_0001_wordlist_raw.wav"),
            _parsed_raw_entry(tmp_path, "ES-L-0001", "interview", "raw/es_l_0001_interview_raw.wav"),
        ]
    )

    warnings: list[str] = []
    conflicts: list[str] = []
    raw_plans = _plan_raw_syncs(
        batch_inventory=inventory,
        person_id="ES-L-0001",
        target_session_dir=target_session_dir,
        warnings=warnings,
        conflicts=conflicts,
    )

    by_task = {plan.task_key: plan for plan in raw_plans}
    assert by_task["wordlist"].action == "keep"
    assert by_task["text"].action == "missing"
    assert by_task["interview"].action == "sync"
    assert conflicts == []
    assert warnings == []


def test_build_task_entries_lists_raw_files_even_without_productive_task(tmp_path: Path) -> None:
    session_dir = tmp_path / "ES-L-0001-2026-S01"
    (session_dir / "raw").mkdir(parents=True, exist_ok=True)
    (session_dir / "source").mkdir(parents=True, exist_ok=True)
    (session_dir / "alignment").mkdir(parents=True, exist_ok=True)
    (session_dir / "raw" / "interview.wav").write_bytes(b"raw-interview")
    (session_dir / "source" / "wordlist.wav").write_bytes(b"processed-wordlist")
    (session_dir / "alignment" / "wordlist.TextGrid").write_text("File type = \"ooTextFile\"", encoding="utf-8")

    tasks, files = _build_task_entries(session_dir)

    assert [task["task_type"] for task in tasks] == ["wordlist"]
    file_map = {entry["path"]: entry for entry in files}
    assert file_map["raw/interview.wav"]["file_role"] == "audio_raw"
    assert file_map["raw/interview.wav"]["status"] == "archived"
    assert file_map["source/wordlist.wav"]["file_role"] == "audio_source"


def test_build_task_entries_uses_json_alignment_for_interview(tmp_path: Path) -> None:
    session_dir = tmp_path / "ES-L-0001-2026-S01"
    (session_dir / "source").mkdir(parents=True, exist_ok=True)
    (session_dir / "alignment").mkdir(parents=True, exist_ok=True)
    (session_dir / "derived").mkdir(parents=True, exist_ok=True)
    (session_dir / "source" / "interview.wav").write_bytes(b"processed-interview")
    (session_dir / "alignment" / "interview.json").write_text("{}\n", encoding="utf-8")
    (session_dir / "derived" / "interview.mp3").write_bytes(b"processed-interview-mp3")

    tasks, files = _build_task_entries(session_dir)

    assert tasks == [
        {
            "task_type": "interview",
            "label": "Interview zur Aussprache",
            "source_file": "source/interview.wav",
            "alignment_file": "alignment/interview.json",
            "derived_file": "derived/interview.mp3",
        }
    ]
    file_map = {entry["path"]: entry for entry in files}
    assert file_map["alignment/interview.json"]["file_role"] == "alignment_json"
    assert file_map["derived/interview.mp3"]["file_role"] == "audio_mp3"