from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

from alignment_export.import_interview_amberscript import build_interview_alignment_payload  # noqa: E402
from alignment_export.import_interview_amberscript import InterviewImportError  # noqa: E402
import intake_batch_common  # noqa: E402
from intake_batch_common import working_intake_state_path  # noqa: E402


_ORGANIZER_SPEC = importlib.util.spec_from_file_location(
    "organize_batch_working_tree_module",
    TEST_REPO_ROOT / "scripts" / "research_data_intake" / "import" / "organize_batch_working_tree.py",
)
assert _ORGANIZER_SPEC is not None
assert _ORGANIZER_SPEC.loader is not None
_ORGANIZER_MODULE = importlib.util.module_from_spec(_ORGANIZER_SPEC)
sys.modules[_ORGANIZER_SPEC.name] = _ORGANIZER_MODULE
_ORGANIZER_SPEC.loader.exec_module(_ORGANIZER_MODULE)
organize_batch_working_tree = _ORGANIZER_MODULE.organize_batch_working_tree


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _minimal_interview_payload(
    participant_word: str = "Ja,",
    reference_words: list[str] | None = None,
) -> dict[str, object]:
    participant_words = [
        {"start": 2.50, "end": 2.80, "text": participant_word, "duration": 0.3, "conf": 1, "pristine": True},
    ]
    for index, reference_word in enumerate(reference_words or ["89[wl_089]."], start=1):
        start = 2.80 + ((index - 1) * 0.4)
        end = start + 0.4
        participant_words.append(
            {"start": start, "end": end, "text": reference_word, "duration": 0.4, "conf": 1, "pristine": True}
        )

    return {
        "speakers": [
            {"spkid": "spk1", "name": "Speaker 1"},
            {"spkid": "spk2", "name": "Speaker 2"},
        ],
        "segments": [
            {
                "speaker": "spk1",
                "words": [
                    {"start": 1.71, "end": 1.91, "text": "Ich", "duration": 0.2, "conf": 1, "pristine": True},
                    {"start": 1.91, "end": 2.31, "text": "frage,", "duration": 0.4, "conf": 1, "pristine": True},
                ],
            },
            {
                "speaker": "spk2",
                "words": participant_words,
            },
        ],
    }


def _prepare_incremental_batch(tmp_path: Path, participant_word: str = "Ja,") -> Path:
    batch_dir = tmp_path / "spanish_batch_20260421"
    processed_dir = batch_dir / "processed"
    raw_dir = batch_dir / "raw"
    working_dir = batch_dir / "working"

    _write_bytes(processed_dir / "es_l_0001_wordlist_processed.wav", b"wordlist-processed")
    _write_text(processed_dir / "es_l_0001_wordlist_processed.TextGrid", "wordlist-textgrid")
    _write_bytes(processed_dir / "es_l_0001_text_processed.wav", b"text-processed")
    _write_text(processed_dir / "es_l_0001_text_processed.TextGrid", "text-textgrid")
    _write_json(processed_dir / "es_l_0001_interview_raw.json", _minimal_interview_payload(participant_word=participant_word))
    _write_bytes(raw_dir / "es_l_0001_interview_raw.wav", b"interview-raw")

    (working_dir / "ES-L-0001" / "wordlist" / "source").mkdir(parents=True, exist_ok=True)
    (working_dir / "ES-L-0001" / "wordlist" / "alignment").mkdir(parents=True, exist_ok=True)
    (working_dir / "ES-L-0001" / "text" / "source").mkdir(parents=True, exist_ok=True)
    (working_dir / "ES-L-0001" / "text" / "alignment").mkdir(parents=True, exist_ok=True)
    (working_dir / "ES-L-0001" / "interview" / "source").mkdir(parents=True, exist_ok=True)

    shutil.copy2(processed_dir / "es_l_0001_wordlist_processed.wav", working_dir / "ES-L-0001" / "wordlist" / "source" / "wordlist.wav")
    shutil.copy2(
        processed_dir / "es_l_0001_wordlist_processed.TextGrid",
        working_dir / "ES-L-0001" / "wordlist" / "alignment" / "wordlist.TextGrid",
    )
    shutil.copy2(processed_dir / "es_l_0001_text_processed.wav", working_dir / "ES-L-0001" / "text" / "source" / "text.wav")
    shutil.copy2(
        processed_dir / "es_l_0001_text_processed.TextGrid",
        working_dir / "ES-L-0001" / "text" / "alignment" / "text.TextGrid",
    )
    _write_text(working_dir / "ES-L-0001" / "text" / "mfa_output" / "keep.txt", "keep")
    _write_text(working_dir / "ES-L-0001" / "text" / "mfa_manifest.json", "{}")
    shutil.copy2(raw_dir / "es_l_0001_interview_raw.wav", working_dir / "ES-L-0001" / "interview" / "source" / "interview.wav")
    return batch_dir


def _task_status(report_payload: dict[str, object], person_id: str, task: str) -> str:
    tasks = report_payload["tasks"]
    assert isinstance(tasks, list)
    for task_entry in tasks:
        assert isinstance(task_entry, dict)
        if task_entry["person_id"] == person_id and task_entry["task"] == task:
            return str(task_entry["status"])
    raise AssertionError(f"Task report missing for {person_id}/{task}")


def _task_entry(report_payload: dict[str, object], person_id: str, task: str) -> dict[str, object]:
    tasks = report_payload["tasks"]
    assert isinstance(tasks, list)
    for task_entry in tasks:
        assert isinstance(task_entry, dict)
        if task_entry["person_id"] == person_id and task_entry["task"] == task:
            return task_entry
    raise AssertionError(f"Task report missing for {person_id}/{task}")


def test_resolve_batch_dir_accepts_generic_batch_names(tmp_path: Path, monkeypatch) -> None:
    import_root = tmp_path / "import-root"
    batch_dir = import_root / "french_batch_20260501"
    (batch_dir / "processed").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(intake_batch_common, "IMPORT_ROOT", import_root)
    monkeypatch.setattr(intake_batch_common, "REPO_ROOT", tmp_path)

    resolved = intake_batch_common.resolve_batch_dir("french_batch_20260501")

    assert resolved == batch_dir.resolve()


def test_build_interview_alignment_payload_maps_segments_and_annotations(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload())

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="es-l-0001", session_id=None)

    assert payload["person_id"] == "ES-L-0001"
    assert payload["task"] == "interview"
    assert payload["audio"] == {"full_mp3": "derived/interview.mp3"}
    segments = payload["segments"]
    assert isinstance(segments, list)
    assert segments[0]["speaker_code"] == "interviewer"
    assert segments[0]["start_ms"] == 1710
    assert segments[1]["speaker_code"] == "participant"
    assert segments[1]["tokens"][0]["text"] == "Ja,"
    assert segments[1]["tokens"][1]["text"] == "89."
    assert segments[1]["text"] == "Ja, 89."
    assert segments[1]["annotations"][0]["item_id"] == "wl_089"
    assert segments[1]["annotations"][0]["task"] == "wordlist"
    assert segments[1]["annotations"][0]["label"] == "ahí – allí"
    assert segments[1]["annotations"][0]["item_number"] == "89"
    assert segments[1]["annotations"][0]["canonical_text"] == "ahí – allí"
    assert segments[1]["annotations"][0]["insert_after_token_id"] == "seg_002_tok_002"
    assert segments[1]["annotations"][0]["trailing_punctuation"] == "."


def test_build_interview_alignment_payload_resolves_text_catalog_refs(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["D5[d_05]", "QY3[qy_03]", "QW4[qw_04]"]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="ES-L-0001", session_id=None)

    annotations = payload["segments"][1]["annotations"]
    assert [annotation["item_id"] for annotation in annotations] == ["d_05", "qy_03", "qw_04"]
    assert all(annotation["task"] == "text" for annotation in annotations)
    assert [annotation["item_number"] for annotation in annotations] == ["D5", "QY3", "QW4"]
    assert annotations[0]["canonical_text"] == "Cuidar un perro exige tiempo y atención diaria."
    assert annotations[1]["insert_after_token_id"] == "seg_002_tok_003"
    assert annotations[2]["insert_after_token_id"] == "seg_002_tok_004"


def test_build_interview_alignment_payload_handles_spaced_marker_anchor(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["Nummero [wl_087]"]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="ES-L-0001", session_id=None)

    segment = payload["segments"][1]
    assert segment["tokens"][1]["text"] == "Nummero"
    assert segment["text"] == "Ja, Nummero"
    assert segment["annotations"][0]["item_id"] == "wl_087"
    assert segment["annotations"][0]["insert_after_token_id"] == "seg_002_tok_002"


def test_build_interview_alignment_payload_rejects_unknown_material_ref_item_id(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["89[wl_999]."]))

    try:
        build_interview_alignment_payload(source_json_path=source_json, person_id="ES-L-0001", session_id=None)
    except InterviewImportError as exc:
        assert exc.status_code == "error_unknown_material_ref_item_id"
        assert "wl_999" in str(exc)
    else:
        raise AssertionError("Expected InterviewImportError for unknown material reference item_id")


def test_build_interview_alignment_payload_rejects_invalid_material_ref_marker(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["89[foo_089]."]))

    try:
        build_interview_alignment_payload(source_json_path=source_json, person_id="ES-L-0001", session_id=None)
    except InterviewImportError as exc:
        assert exc.status_code == "error_invalid_material_ref_marker"
        assert "foo_089" in str(exc)
    else:
        raise AssertionError("Expected InterviewImportError for invalid material reference marker")


def test_organize_batch_working_tree_bootstraps_and_only_builds_interview(tmp_path: Path) -> None:
    batch_dir = _prepare_incremental_batch(tmp_path)

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=False,
        force_tasks=set(),
    )

    assert _task_status(report_payload, "ES-L-0001", "wordlist") == "unchanged"
    assert _task_status(report_payload, "ES-L-0001", "text") == "unchanged"
    assert _task_status(report_payload, "ES-L-0001", "interview") == "rebuilt"
    assert (batch_dir / "working" / "ES-L-0001" / "text" / "mfa_output" / "keep.txt").exists()
    assert (batch_dir / "working" / "ES-L-0001" / "interview" / "alignment" / "interview.json").exists()
    assert working_intake_state_path(batch_dir).exists()


def test_organize_batch_working_tree_second_run_is_idempotent(tmp_path: Path) -> None:
    batch_dir = _prepare_incremental_batch(tmp_path)
    organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=False,
        force_tasks=set(),
    )
    interview_json = batch_dir / "working" / "ES-L-0001" / "interview" / "alignment" / "interview.json"
    first_mtime = interview_json.stat().st_mtime_ns

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=False,
        force_tasks=set(),
    )

    assert _task_status(report_payload, "ES-L-0001", "wordlist") == "unchanged"
    assert _task_status(report_payload, "ES-L-0001", "text") == "unchanged"
    assert _task_status(report_payload, "ES-L-0001", "interview") == "unchanged"
    assert interview_json.stat().st_mtime_ns == first_mtime


def test_organize_batch_working_tree_rebuilds_only_interview_when_json_changes(tmp_path: Path) -> None:
    batch_dir = _prepare_incremental_batch(tmp_path)
    organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=False,
        force_tasks=set(),
    )

    interview_json = batch_dir / "working" / "ES-L-0001" / "interview" / "alignment" / "interview.json"
    wordlist_wav = batch_dir / "working" / "ES-L-0001" / "wordlist" / "source" / "wordlist.wav"
    first_interview_mtime = interview_json.stat().st_mtime_ns
    first_wordlist_mtime = wordlist_wav.stat().st_mtime_ns

    source_json_path = batch_dir / "processed" / "es_l_0001_interview_raw.json"
    _write_json(source_json_path, _minimal_interview_payload(participant_word="Nein,"))

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=False,
        force_tasks=set(),
    )

    assert _task_status(report_payload, "ES-L-0001", "wordlist") == "unchanged"
    assert _task_status(report_payload, "ES-L-0001", "text") == "unchanged"
    assert _task_status(report_payload, "ES-L-0001", "interview") == "rebuilt"
    assert interview_json.stat().st_mtime_ns >= first_interview_mtime
    assert wordlist_wav.stat().st_mtime_ns == first_wordlist_mtime
    rebuilt_payload = json.loads(interview_json.read_text(encoding="utf-8"))
    assert rebuilt_payload["segments"][1]["tokens"][0]["text"] == "Nein,"


def test_organize_batch_working_tree_reports_material_ref_errors_without_aborting_batch(tmp_path: Path) -> None:
    batch_dir = _prepare_incremental_batch(tmp_path)
    source_json_path = batch_dir / "processed" / "es_l_0001_interview_raw.json"
    _write_json(source_json_path, _minimal_interview_payload(reference_words=["89[wl_999]."]))

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=False,
        force_tasks={"interview"},
    )

    assert _task_status(report_payload, "ES-L-0001", "wordlist") == "unchanged"
    assert _task_status(report_payload, "ES-L-0001", "text") == "unchanged"
    assert _task_status(report_payload, "ES-L-0001", "interview") == "error_unknown_material_ref_item_id"
    assert report_payload["summary"]["errors"] == 1


def test_organize_batch_working_tree_reports_multiple_interview_json_candidates(tmp_path: Path) -> None:
    batch_dir = tmp_path / "spanish_batch_20260421"
    processed_dir = batch_dir / "processed"
    raw_dir = batch_dir / "raw"
    _write_json(processed_dir / "es_l_0001_interview_raw.json", _minimal_interview_payload())
    _write_json(raw_dir / "es_l_0001_interview_raw.json", _minimal_interview_payload(participant_word="Nein,"))
    _write_bytes(raw_dir / "es_l_0001_interview_raw.wav", b"interview-raw")

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=False,
        force_tasks=set(),
    )

    assert _task_status(report_payload, "ES-L-0001", "interview") == "conflict_multiple_json_candidates"


def test_organize_batch_working_tree_reports_missing_interview_json(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260615"
    raw_dir = batch_dir / "raw"
    processed_dir = batch_dir / "processed"
    _write_bytes(raw_dir / "en_l_0001_interview_raw.wav", b"interview-raw")
    _write_bytes(processed_dir / "en_l_0001_wordlist_processed.wav", b"wordlist-processed")
    _write_text(processed_dir / "en_l_0001_wordlist_processed.TextGrid", "wordlist-textgrid")

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=False,
        force_tasks=set(),
    )

    assert _task_status(report_payload, "EN-L-0001", "interview") == "missing_json"


def test_organize_batch_working_tree_marks_native_speaker_interview_not_expected(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260615"
    processed_dir = batch_dir / "processed"
    _write_bytes(processed_dir / "en_n_0001_wordlist_processed.wav", b"wordlist-processed")
    _write_text(processed_dir / "en_n_0001_wordlist_processed.TextGrid", "wordlist-textgrid")
    _write_bytes(processed_dir / "en_n_0001_text_processed.wav", b"text-processed")
    _write_text(processed_dir / "en_n_0001_text_processed.TextGrid", "text-textgrid")

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=False,
        force_tasks=set(),
    )

    interview_entry = _task_entry(report_payload, "EN-N-0001", "interview")
    assert interview_entry["status"] == "not_expected_for_native_speaker"
    assert interview_entry["message"] == "interview is not expected for native_speaker"
    assert report_payload["warnings"] == []