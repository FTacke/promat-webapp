from __future__ import annotations

import json
import os
from pathlib import Path
import sys


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

from corpus_inventory import build_inventory, compare_inventories  # noqa: E402


def _session(root: Path, slug: str, session_id: str, *, speaker_type: str = "learner", mp3: bytes = b"ID3a") -> None:
    session_dir = root / slug / session_id
    (session_dir / "derived").mkdir(parents=True)
    (session_dir / "derived" / "text.mp3").write_bytes(mp3)
    (session_dir / "metadata.json").write_text(
        json.dumps(
            {
                "person_id": session_id.rsplit("-20", 1)[0],
                "speaker_type": speaker_type,
                "tasks": [{"task_type": "text", "alignment_file": "alignment/text.json", "derived_file": "derived/text.mp3"}],
            }
        ),
        encoding="utf-8",
    )


def test_inventory_counts_people_sessions_and_tasks_per_corpus(tmp_path: Path) -> None:
    _session(tmp_path, "english", "EN-L-0001-2026-S01")
    _session(tmp_path, "english", "EN-N-0001-2026-S01", speaker_type="native_speaker")
    _session(tmp_path, "french", "FR-L-0001-2026-S01")

    inventory = build_inventory(tmp_path, ["en", "french"])

    english = inventory["corpora"]["english"]
    assert english["person_count"] == 2 and english["learner_count"] == 1 and english["native_speaker_count"] == 1
    assert english["session_count"] == 2 and english["sessions_with_task"]["text"] == 2
    assert inventory["corpora"]["french"]["session_count"] == 1
    assert "german" not in inventory["corpora"]


def test_inventory_compare_detects_added_removed_and_changed_sessions(tmp_path: Path) -> None:
    left_root, right_root = tmp_path / "left", tmp_path / "right"
    for root in (left_root, right_root):
        _session(root, "spanish", "ES-L-0001-2026-S01")
    _session(left_root, "spanish", "ES-L-0002-2026-S01")
    _session(right_root, "spanish", "ES-L-0003-2026-S01")
    (right_root / "spanish" / "ES-L-0001-2026-S01" / "derived" / "text.mp3").write_bytes(b"ID3changed")

    differences = compare_inventories(build_inventory(left_root, ["es"]), build_inventory(right_root, ["es"]))

    assert "spanish: ES-L-0002-2026-S01 only in left" in differences
    assert "spanish: ES-L-0003-2026-S01 only in right" in differences
    assert "spanish: ES-L-0001-2026-S01 content differs" in differences
    assert compare_inventories(build_inventory(left_root, ["es"]), build_inventory(left_root, ["es"])) == []
