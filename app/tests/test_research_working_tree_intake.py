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
from alignment_export.prepare_text_mfa_corpus import _align_text_items_to_intervals  # noqa: E402
from alignment_export.prepare_text_mfa_corpus import _frame_bounds  # noqa: E402
from alignment_export.prepare_text_mfa_corpus import TextSourceItem  # noqa: E402
from alignment_export.wordlist_alignment import build_timed_items  # noqa: E402
from alignment_export.wordlist_alignment import CatalogItem  # noqa: E402
from alignment_export.wordlist_alignment import parse_textgrid_intervals as parse_wordlist_textgrid_intervals  # noqa: E402
from alignment_export.wordlist_alignment import TextGridInterval as WordlistTextGridInterval  # noqa: E402
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
    _write_bytes(processed_dir / "es_l_0001_interview_processed.wav", b"interview-source")
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
    shutil.copy2(processed_dir / "es_l_0001_interview_processed.wav", working_dir / "ES-L-0001" / "interview" / "source" / "interview.wav")
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
    batch_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(intake_batch_common, "IMPORT_ROOT", import_root)
    monkeypatch.setattr(intake_batch_common, "REPO_ROOT", tmp_path)

    resolved = intake_batch_common.resolve_batch_dir("french_batch_20260501")

    assert resolved == batch_dir.resolve()


def test_scan_import_batch_accepts_drop_in_files_without_stage_subfolders(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260615"
    _write_bytes(batch_dir / "en_l_0001_wordlist_processed.wav", b"wordlist-source")
    _write_text(batch_dir / "en_l_0001_wordlist_processed.TextGrid", "wordlist-grid")
    _write_bytes(batch_dir / "en_l_0001_interview_source.wav", b"interview-source")
    _write_json(batch_dir / "en_l_0001_interview_amberscript.json", _minimal_interview_payload())
    _write_bytes(batch_dir / "notes.txt", b"ignored")

    scan_report = intake_batch_common.scan_import_batch(batch_dir)

    assert {entry.relative_source for entry in scan_report.parsed_files} == {
        "en_l_0001_wordlist_processed.wav",
        "en_l_0001_wordlist_processed.TextGrid",
        "en_l_0001_interview_source.wav",
        "en_l_0001_interview_amberscript.json",
    }
    assert "unsupported intake file type skipped: notes.txt" in scan_report.warnings


def test_scan_import_batch_treats_bearbeitet_like_processed(tmp_path: Path) -> None:
    batch_dir = tmp_path / "french_batch_20260618"
    _write_bytes(batch_dir / "fr_l_0021_wordlist_bearbeitet.wav", b"wordlist-source")

    scan_report = intake_batch_common.scan_import_batch(batch_dir)

    assert scan_report.warnings == ()
    assert len(scan_report.parsed_files) == 1
    entry = scan_report.parsed_files[0]
    assert entry.person_id == "FR-L-0021"
    assert entry.task == "wordlist"
    assert entry.stage == "processed"
    assert entry.file_role == "source"


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
    assert segments[1]["tokens"][1]["text"] == "89"
    assert segments[1]["tokens"][1]["suffix"] == "."
    assert segments[1]["text"] == "Ja, 89."
    assert segments[1]["annotations"][0]["item_id"] == "wl_089"
    assert segments[1]["annotations"][0]["task"] == "wordlist"
    assert segments[1]["annotations"][0]["label"] == "ahí – allí"
    assert segments[1]["annotations"][0]["item_number"] == "89"
    assert segments[1]["annotations"][0]["canonical_text"] == "ahí – allí"
    assert segments[1]["annotations"][0]["insert_after_token_id"] == "seg_002_tok_002"


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


def test_build_interview_alignment_payload_keeps_marker_punctuation_as_token_suffix(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["QY3[qy_03]?", "D5[d_05],", "17 [d_05]."]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="ES-L-0001", session_id=None)

    segment = payload["segments"][1]
    assert [token["text"] for token in segment["tokens"][1:]] == ["QY3", "D5", "17"]
    assert [token.get("suffix") for token in segment["tokens"][1:]] == ["?", ",", "."]
    assert segment["text"] == "Ja, QY3? D5, 17."
    assert all("trailing_punctuation" not in annotation for annotation in segment["annotations"])


def test_build_interview_alignment_payload_anchors_standalone_marker_to_previous_token(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["Zeile", "18", "[t_18],", "sorry."]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    segment = payload["segments"][1]
    assert [token["text"] for token in segment["tokens"][1:]] == ["Zeile", "18", "sorry."]
    assert segment["tokens"][2]["suffix"] == ","
    assert segment["text"] == "Ja, Zeile 18, sorry."
    assert segment["annotations"][0]["item_id"] == "t_18"
    assert segment["annotations"][0]["insert_after_token_id"] == "seg_002_tok_003"


def test_build_interview_alignment_payload_keeps_intraword_brackets_as_literal_text(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=['"thr[i]ten"', "nicht"]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    segment = payload["segments"][1]
    assert [token["text"] for token in segment["tokens"][1:]] == ['"thr[i]ten"', "nicht"]
    assert segment.get("annotations") is None
    assert segment["text"] == 'Ja, "thr[i]ten" nicht'


def test_build_interview_alignment_payload_keeps_non_material_bracket_literals(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["[u].", "[x]", "[theta]"]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    segment = payload["segments"][1]
    assert [token["text"] for token in segment["tokens"][1:]] == ["[u].", "[x]", "[theta]"]
    assert segment.get("annotations") is None
    assert segment["text"] == "Ja, [u]. [x] [theta]"


def test_build_interview_alignment_payload_keeps_empty_phonetic_omission_brackets(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=['"va[]nilla".', "weiter"]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="ES-L-0015", session_id=None)

    segment = payload["segments"][1]
    assert [token["text"] for token in segment["tokens"][1:]] == ['"va[]nilla".', "weiter"]
    assert segment.get("annotations") is None
    assert segment["text"] == 'Ja, "va[]nilla". weiter'


def test_build_interview_alignment_payload_keeps_quoted_word_final_brackets_as_literal(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(
        source_json,
        _minimal_interview_payload(
            reference_words=['"blan[k]"', '"aspe[kt]"', "all[e", 'ɛ]lles"', "[ʒ]-Sound", '"[ʒ]eler"-']
        ),
    )

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    segment = payload["segments"][1]
    assert [token["text"] for token in segment["tokens"][1:]] == [
        '"blan[k]"',
        '"aspe[kt]"',
        "all[e",
        'ɛ]lles"',
        "[ʒ]-Sound",
        '"[ʒ]eler"-',
    ]
    assert segment.get("annotations") is None


def test_build_interview_alignment_payload_maps_uuid_speaker_ids_from_speakers_table(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    payload_data = _minimal_interview_payload()
    payload_data["speakers"] = [
        {"spkid": "spk1", "name": "Speaker 1"},
        {"spkid": "d39f1341-f0dd-4917-8eba-831abe7577d3", "name": "Speaker 2"},
    ]
    payload_data["segments"][1]["speaker"] = "d39f1341-f0dd-4917-8eba-831abe7577d3"
    _write_json(source_json, payload_data)

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    assert payload["segments"][0]["speaker_code"] == "interviewer"
    assert payload["segments"][1]["speaker_code"] == "participant"


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


def test_build_interview_alignment_payload_accepts_dash_suffix_on_material_ref(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["[wl_059]-", "weiter"]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    segment = payload["segments"][1]
    ref_token = next(t for t in segment["tokens"] if t.get("suffix") == "-")
    assert ref_token is not None
    assert segment.get("annotations")


def test_build_interview_alignment_payload_zero_pads_known_material_ref_ids(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["[t_8]."]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="FR-L-0001", session_id=None)

    annotations = payload["segments"][1]["annotations"]
    assert annotations[0]["item_id"] == "t_08"
    assert annotations[0]["item_number"] == "T8"


def test_build_interview_alignment_payload_clamps_zero_duration_word_with_warning(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    zero_dur_word = {"start": 3.0, "end": 3.0, "text": "//ich//", "duration": 0.0, "conf": 1, "pristine": True}
    payload_data = _minimal_interview_payload()
    payload_data["segments"][1]["words"].append(zero_dur_word)
    _write_json(source_json, payload_data)

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    assert "//ich//" in " ".join(t["text"] for t in payload["segments"][1]["tokens"])
    import_warnings = payload.get("_import_warnings", [])
    assert any("//ich//" in w and "zero duration" in w for w in import_warnings)


def test_build_interview_alignment_payload_clamps_zero_duration_segment_with_warning(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    payload_data = _minimal_interview_payload()
    payload_data["segments"][1]["words"] = [
        {"start": 3.0, "end": 3.0, "text": "oui", "duration": 0.0, "conf": 1, "pristine": True}
    ]
    _write_json(source_json, payload_data)

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    segment = payload["segments"][1]
    assert segment["end_ms"] == segment["start_ms"] + 1
    import_warnings = payload.get("_import_warnings", [])
    assert any("segment 2 has zero duration" in w for w in import_warnings)


def test_text_mfa_frame_bounds_clamps_tiny_end_overrun() -> None:
    start_frame, end_frame, warning = _frame_bounds(0.0, 1.0006, 1000, 1000)

    assert start_frame == 0
    assert end_frame == 1000
    assert warning is not None
    assert "clamped TextGrid end boundary" in warning


def test_wordlist_alignment_treats_silent_dash_as_silence() -> None:
    items = [
        CatalogItem(item_id="wl_001", item_number="1", text="un"),
        CatalogItem(item_id="wl_002", item_number="2", text="deux"),
    ]
    intervals = [
        WordlistTextGridInterval(start_seconds=0.0, end_seconds=0.1, text="un"),
        WordlistTextGridInterval(start_seconds=0.1, end_seconds=0.2, text="silent-"),
        WordlistTextGridInterval(start_seconds=0.2, end_seconds=0.3, text="deux"),
    ]

    timed_items, warnings = build_timed_items(items, intervals, validate_labels="fail")

    assert [item.text for item in timed_items] == ["un", "deux"]
    assert warnings == []


def test_french_wordlist_alignment_canonicalizes_theatre_before_validation() -> None:
    items = [CatalogItem(item_id="wl_014", item_number="14", text="théâtre")]
    intervals = [WordlistTextGridInterval(start_seconds=0.0, end_seconds=0.5, text="théatre")]

    timed_items, warnings = build_timed_items(
        items,
        intervals,
        validate_labels="fail",
        language_slug="french",
    )

    assert timed_items[0].text == "théâtre"
    assert any("canonical_item_correction" in warning for warning in warnings)
    assert not any("label mismatch" in warning for warning in warnings)


def test_wordlist_alignment_accepts_utf8_textgrid(tmp_path: Path) -> None:
    textgrid_path = tmp_path / "wordlist.TextGrid"
    textgrid_path.write_text(
        '''
File type = "ooTextFile"
Object class = "TextGrid"

item [1]:
    class = "IntervalTier"
    name = "words"
    xmin = 0
    xmax = 1
    intervals: size = 1
    intervals [1]:
        xmin = 0
        xmax = 0.5
        text = "vainilla"
'''.lstrip(),
        encoding="utf-8",
    )

    intervals = parse_wordlist_textgrid_intervals(textgrid_path)

    assert len(intervals) == 1
    assert intervals[0].text == "vainilla"
    assert intervals[0].end_seconds == 0.5


def test_text_mfa_allows_omitted_spoken_title_item() -> None:
    class Interval:
        def __init__(self, text: str) -> None:
            self.text = text

    text_items = [
        TextSourceItem("t_01", "T1", "The Boy who Cried Wolf", spoken_title_item=True),
        TextSourceItem("t_02", "T2", "There was once a poor shepherd boy, "),
        TextSourceItem("t_03", "T3", "\u2014 a child more than a man \u2014 "),
    ]
    intervals = [
        Interval("There was once a poor shepherd boy,"),
        Interval("-a child more than a man-"),
    ]

    aligned_items, omitted_items = _align_text_items_to_intervals(text_items, intervals, "EN-L-0008")

    assert [item.item_id for item in aligned_items] == ["t_02", "t_03"]
    assert len(omitted_items) == 1
    assert omitted_items[0].item_id == "t_01"
    assert omitted_items[0].omit_reason == "unspoken_title"


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


def test_organize_batch_working_tree_accepts_drop_in_batch_without_processed_dir(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    _write_bytes(batch_dir / "en_l_0001_wordlist_processed.wav", b"wordlist-processed")
    _write_text(batch_dir / "en_l_0001_wordlist_processed.TextGrid", "wordlist-textgrid")
    _write_bytes(batch_dir / "en_l_0001_text_processed.wav", b"text-processed")
    _write_text(batch_dir / "en_l_0001_text_processed.TextGrid", "text-textgrid")
    _write_bytes(batch_dir / "en_l_0001_interview_processed.wav", b"interview-source")
    _write_json(batch_dir / "en_l_0001_interview_processed.json", _minimal_interview_payload(reference_words=["Zeile", "18", "[t_18],"]))

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=True,
        force_tasks=set(),
        person_ids={"EN-L-0001"},
    )

    assert report_payload["person_ids"] == ["EN-L-0001"]
    assert _task_status(report_payload, "EN-L-0001", "wordlist") == "rebuilt"
    assert _task_status(report_payload, "EN-L-0001", "text") == "rebuilt"
    assert _task_status(report_payload, "EN-L-0001", "interview") == "rebuilt"
    assert (batch_dir / "working" / "EN-L-0001" / "interview" / "alignment" / "interview.json").exists()


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


def test_organize_batch_working_tree_uses_raw_wav_as_source_for_interview_when_no_processed_wav(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260615"
    raw_dir = batch_dir / "raw"
    processed_dir = batch_dir / "processed"
    _write_bytes(raw_dir / "en_l_0001_interview_raw.wav", b"interview-raw")
    _write_json(processed_dir / "en_l_0001_interview_processed.json", _minimal_interview_payload())

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=True,
        force_tasks=set(),
    )

    interview_entry = _task_entry(report_payload, "EN-L-0001", "interview")
    assert interview_entry["status"] == "rebuilt"
    assert interview_entry["raw_wav_used_as_source"] is True
    assert interview_entry["selected_inputs"]["source_wav"]["stage"] == "raw"
    assert (batch_dir / "working" / "EN-L-0001" / "interview" / "source" / "interview.wav").read_bytes() == b"interview-raw"
    assert (batch_dir / "working" / "EN-L-0001" / "interview" / "alignment" / "interview.json").exists()


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


def test_organize_batch_working_tree_rebuilds_interview_when_json_missing_despite_stale_state(tmp_path: Path) -> None:
    """Regression: state records only WAV as output (from before JSON was tracked), JSON missing — must rebuild."""
    batch_dir = tmp_path / "english_batch_20260525"
    interview_wav_src = batch_dir / "en_l_0001_interview_processed.wav"
    interview_json_src = batch_dir / "en_l_0001_interview_processed.json"
    _write_bytes(interview_wav_src, b"interview-source-bytes")
    _write_json(interview_json_src, _minimal_interview_payload(reference_words=["Zeile", "18", "[t_18],"]))
    _write_bytes(batch_dir / "en_l_0001_wordlist_processed.wav", b"wordlist-processed")
    _write_text(batch_dir / "en_l_0001_wordlist_processed.TextGrid", "wordlist-textgrid")
    _write_bytes(batch_dir / "en_l_0001_text_processed.wav", b"text-processed")
    _write_text(batch_dir / "en_l_0001_text_processed.TextGrid", "text-textgrid")

    # Simulate partial working tree: WAV copied, JSON not yet produced
    working_wav = batch_dir / "working" / "EN-L-0001" / "interview" / "source" / "interview.wav"
    working_wav.parent.mkdir(parents=True, exist_ok=True)
    working_wav.write_bytes(b"interview-source-bytes")
    (batch_dir / "working" / "EN-L-0001" / "interview" / "alignment").mkdir(parents=True, exist_ok=True)

    # Write stale state that only records WAV output (JSON not yet tracked)
    wav_stat = interview_wav_src.stat()
    json_stat = interview_json_src.stat()
    stale_state = {
        "version": 1,
        "batch": batch_dir.as_posix(),
        "updated_at": "2026-05-25T10:00:00+00:00",
        "persons": {
            "EN-L-0001": {
                "interview": {
                    "selected_inputs": {
                        "source_wav": {
                            "path": "en_l_0001_interview_processed.wav",
                            "size": wav_stat.st_size,
                            "mtime_ns": wav_stat.st_mtime_ns,
                            "hash": None,
                            "source_root": "batch_root",
                            "stage": "processed",
                            "file_kind": "wav",
                        },
                        "source_json": {
                            "path": "en_l_0001_interview_processed.json",
                            "size": json_stat.st_size,
                            "mtime_ns": json_stat.st_mtime_ns,
                            "hash": None,
                            "source_root": "batch_root",
                            "stage": "processed",
                            "file_kind": "json",
                        },
                    },
                    "recognized_sources": {},
                    "last_build_status": "unchanged",
                    "last_build_time": None,
                    "last_evaluated_at": "2026-05-25T10:00:00+00:00",
                    "outputs": ["working/EN-L-0001/interview/source/interview.wav"],
                },
                "wordlist": {},
                "text": {},
            }
        },
    }
    _write_json(working_intake_state_path(batch_dir), stale_state)

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=False,
        force_tasks=set(),
        person_ids={"EN-L-0001"},
    )

    assert _task_status(report_payload, "EN-L-0001", "interview") == "rebuilt"
    assert (batch_dir / "working" / "EN-L-0001" / "interview" / "alignment" / "interview.json").exists()


def test_organize_batch_working_tree_uses_raw_wav_when_no_processed_wav_for_wordlist(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    _write_bytes(batch_dir / "en_l_0001_wordlist_raw.wav", b"wordlist-raw")
    _write_text(batch_dir / "en_l_0001_wordlist_processed.TextGrid", "wordlist-textgrid")

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=True,
        force_tasks=set(),
        person_ids={"EN-L-0001"},
    )

    entry = _task_entry(report_payload, "EN-L-0001", "wordlist")
    assert entry["status"] == "rebuilt"
    assert entry["raw_wav_used_as_source"] is True
    assert entry["selected_inputs"]["source_wav"]["stage"] == "raw"
    working_wav = batch_dir / "working" / "EN-L-0001" / "wordlist" / "source" / "wordlist.wav"
    assert working_wav.read_bytes() == b"wordlist-raw"


def test_organize_batch_working_tree_prefers_processed_wav_over_raw_for_wordlist(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    _write_bytes(batch_dir / "en_l_0001_wordlist_processed.wav", b"wordlist-processed")
    _write_bytes(batch_dir / "en_l_0001_wordlist_raw.wav", b"wordlist-raw")
    _write_text(batch_dir / "en_l_0001_wordlist_processed.TextGrid", "wordlist-textgrid")

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=True,
        force_tasks=set(),
        person_ids={"EN-L-0001"},
    )

    entry = _task_entry(report_payload, "EN-L-0001", "wordlist")
    assert entry["status"] == "rebuilt"
    assert entry["raw_wav_used_as_source"] is False
    assert entry["selected_inputs"]["source_wav"]["stage"] == "processed"
    working_wav = batch_dir / "working" / "EN-L-0001" / "wordlist" / "source" / "wordlist.wav"
    assert working_wav.read_bytes() == b"wordlist-processed"


def test_organize_batch_working_tree_conflicts_on_multiple_raw_wavs_when_no_processed_wav(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    _write_bytes(batch_dir / "src1" / "en_l_0001_wordlist_raw.wav", b"raw-v1")
    _write_bytes(batch_dir / "src2" / "en_l_0001_wordlist_raw.wav", b"raw-v2")
    _write_text(batch_dir / "en_l_0001_wordlist_processed.TextGrid", "wordlist-textgrid")

    report_payload = organize_batch_working_tree(
        batch_dir=batch_dir,
        transfer_mode="copy",
        dry_run=False,
        replace_existing=True,
        force_tasks=set(),
        person_ids={"EN-L-0001"},
    )

    assert _task_status(report_payload, "EN-L-0001", "wordlist") == "conflict_multiple_raw_wav_candidates"
