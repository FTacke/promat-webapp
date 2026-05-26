from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import wave
from pathlib import Path


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

from alignment_export.import_interview_amberscript import build_interview_alignment_payload  # noqa: E402
from alignment_export.import_interview_amberscript import InterviewImportError  # noqa: E402
from alignment_export.import_text_mfa_alignment import import_text_mfa_alignment_for_person  # noqa: E402
from alignment_export.prepare_text_mfa_corpus import prepare_text_mfa_for_person  # noqa: E402
from alignment_export.run_text_mfa import run_text_mfa_for_person  # noqa: E402
import intake_batch_common  # noqa: E402
import produce_text_artifacts as produce_text_artifacts_module  # noqa: E402
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


def _write_silent_wav(path: Path, *, sample_rate: int, frame_count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(b"\x00\x00" * frame_count)


def _write_textgrid_intervals(path: Path, labels: list[str]) -> None:
    lines: list[str] = []
    for index, label in enumerate(labels, start=1):
        lines.extend(
            [
                f"intervals [{index}]:",
                f"    xmin = {index - 1}",
                f"    xmax = {index}",
                f'    text = "{label}"',
            ]
        )
    _write_text(path, "\n".join(lines) + "\n")


def _write_mfa_words_textgrid(path: Path, label: str = "word") -> None:
    _write_text(
        path,
        "\n".join(
            [
                'File type = "ooTextFile"',
                'Object class = "TextGrid"',
                "xmin = 0",
                "xmax = 1",
                "tiers? <exists>",
                "size = 1",
                "item [1]:",
                '    class = "IntervalTier"',
                '    name = "words"',
                "    xmin = 0",
                "    xmax = 1",
                "    intervals: size = 1",
                "    intervals [1]:",
                "        xmin = 0",
                "        xmax = 0.5",
                f'        text = "{label}"',
            ]
        )
        + "\n",
    )


def _english_text_items(*, count: int = 56, spoken_title_item: bool = True) -> list[dict[str, object]]:
    items: list[dict[str, object]] = [
        {
            "item_id": "t_01",
            "item_number": "T1",
            "text": "The Boy who Cried Wolf",
            **({"spoken_title_item": True} if spoken_title_item else {}),
        }
    ]
    for index in range(2, count + 1):
        items.append({"item_id": f"t_{index:02d}", "item_number": f"T{index}", "text": f"Item {index:02d}"})
    return items


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


def test_build_interview_alignment_payload_keeps_ipa_brackets_as_transcript_annotations(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["[θ]", "[x]", "nicht"]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="ES-L-0001", session_id=None)

    segment = payload["segments"][1]
    assert [token["text"] for token in segment["tokens"][1:]] == ["[θ]", "[x]", "nicht"]
    assert segment.get("annotations") is None
    import_warnings = payload.get("_import_warnings", [])
    assert any("[θ]" in warning and "without material_ref" in warning for warning in import_warnings)
    assert any("[x]" in warning and "without material_ref" in warning for warning in import_warnings)


def test_build_interview_alignment_payload_keeps_u_marker_without_material_ref(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    _write_json(source_json, _minimal_interview_payload(reference_words=["[u]", "weiter"]))

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    segment = payload["segments"][1]
    assert [token["text"] for token in segment["tokens"][1:]] == ["[u]", "weiter"]
    assert segment.get("annotations") is None
    assert any("[u]" in warning and "without material_ref" in warning for warning in payload.get("_import_warnings", []))


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
        {"start": 3.0, "end": 3.0, "text": "Ja", "duration": 0.0, "conf": 1, "pristine": True}
    ]
    _write_json(source_json, payload_data)

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    segment = payload["segments"][1]
    assert segment["start_ms"] == 3000
    assert segment["end_ms"] == 3001
    import_warnings = payload.get("_import_warnings", [])
    assert any("segment 2 has zero duration" in w for w in import_warnings)
    assert any("'Ja'" in w and "zero duration" in w for w in import_warnings)


def test_build_interview_alignment_payload_maps_uuid_speaker_when_speakers_list_is_unambiguous(tmp_path: Path) -> None:
    source_json = tmp_path / "input.json"
    payload_data = _minimal_interview_payload()
    uuid = "d39f1341-f0dd-4917-8eba-831abe7577d3"
    payload_data["speakers"][1]["spkid"] = uuid
    for segment in payload_data["segments"]:
        if segment["speaker"] == "spk2":
            segment["speaker"] = uuid
    _write_json(source_json, payload_data)

    payload = build_interview_alignment_payload(source_json_path=source_json, person_id="EN-L-0001", session_id=None)

    assert payload["segments"][1]["speaker_code"] == "participant"
    assert any(uuid in warning and "mapped to spk2" in warning for warning in payload.get("_import_warnings", []))


def test_read_json_file_accepts_utf8_bom(tmp_path: Path) -> None:
    source_json = tmp_path / "bom.json"
    source_json.write_text("\ufeff{\"segments\": []}\n", encoding="utf-8")

    payload = intake_batch_common.read_json_file(source_json)

    assert payload == {"segments": []}


def test_working_intake_state_accepts_utf8_bom(tmp_path: Path) -> None:
    state_path = tmp_path / ".intake_state.json"
    state_path.write_text('\ufeff{"version": 1, "persons": {}}\n', encoding="utf-8")

    payload = _ORGANIZER_MODULE._load_state(state_path)

    assert payload == {"version": 1, "persons": {}}


def test_prepare_text_mfa_clamps_tiny_textgrid_audio_overrun_with_warning(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    person_id = "EN-L-0001"
    _write_silent_wav(batch_dir / "working" / person_id / "text" / "source" / "text.wav", sample_rate=10000, frame_count=10000)
    _write_text(
        batch_dir / "working" / person_id / "text" / "alignment" / "text.TextGrid",
        'intervals [1]:\n    xmin = 0\n    xmax = 1.0004\n    text = "spoken"\n',
    )
    text_source_json = tmp_path / "text.json"
    _write_json(
        text_source_json,
        {
            "task": "text",
            "language": "en",
            "items": [{"item_id": "t_01", "item_number": "T1", "text": "spoken"}],
        },
    )

    result = prepare_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id=person_id,
        text_source_json=text_source_json,
        cli_language="en",
        dry_run=False,
        replace_existing=True,
    )

    manifest = json.loads((batch_dir / "working" / person_id / "text" / "mfa_manifest.json").read_text(encoding="utf-8"))
    assert result["segments"] == 1
    assert any("clamped to source duration" in warning for warning in result["warnings"])
    assert manifest["warnings"] == result["warnings"]
    assert (batch_dir / "working" / person_id / "text" / "mfa_corpus" / "text_001_t_01.wav").exists()


def test_prepare_text_mfa_omits_unspoken_title_when_shifted_catalog_matches(tmp_path: Path, monkeypatch) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    person_id = "EN-L-0008"
    text_root = batch_dir / "working" / person_id / "text"
    _write_silent_wav(text_root / "source" / "text.wav", sample_rate=1000, frame_count=60000)
    _write_textgrid_intervals(text_root / "alignment" / "text.TextGrid", [f"Item {index:02d}" for index in range(2, 57)])
    text_source_json = tmp_path / "text.json"
    _write_json(text_source_json, {"task": "text", "language": "en", "items": _english_text_items()})

    result = prepare_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id=person_id,
        text_source_json=text_source_json,
        cli_language="en",
        dry_run=False,
        replace_existing=True,
    )
    manifest_path = text_root / "mfa_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result["segments"] == 55
    assert manifest["items"][0]["item_id"] == "t_02"
    assert manifest["items"][-1]["item_id"] == "t_56"
    assert manifest["omitted_items"] == [
        {
            "item_id": "t_01",
            "item_number": "T1",
            "text": "The Boy who Cried Wolf",
            "omitted": True,
            "omit_reason": "unspoken_title",
        }
    ]
    assert any("omitted t_01" in warning for warning in manifest["warnings"])

    for item in manifest["items"]:
        _write_mfa_words_textgrid(text_root / "mfa_output" / f"{item['utterance_basename']}.TextGrid")

    import_result = import_text_mfa_alignment_for_person(
        batch_dir=batch_dir,
        person_id=person_id,
        cli_language="en",
        dry_run=False,
        fail_on_missing_output=True,
        replace_existing=True,
    )
    alignment_path = text_root / "alignment" / "text.json"
    alignment = json.loads(alignment_path.read_text(encoding="utf-8"))

    assert import_result.item_count == 55
    assert [item["item_id"] for item in alignment["items"][:2]] == ["t_02", "t_03"]
    assert alignment["items"][-1]["item_id"] == "t_56"
    assert alignment["omitted_items"][0]["item_id"] == "t_01"
    assert "start_ms" not in alignment["omitted_items"][0]
    assert "end_ms" not in alignment["omitted_items"][0]
    assert "split_mp3" not in alignment["omitted_items"][0]

    created_splits: list[str] = []
    session_dir = tmp_path / "runtime" / "EN-L-0008-2026-S01"
    (session_dir / "alignment").mkdir(parents=True)
    (session_dir / "derived").mkdir()
    (session_dir / "items").mkdir()
    _write_silent_wav(tmp_path / "source.wav", sample_rate=1000, frame_count=60000)
    monkeypatch.setattr(
        produce_text_artifacts_module,
        "probe_audio_profile",
        lambda path: {
            "duration": 60.0,
            "channels": produce_text_artifacts_module.TARGET_CHANNELS,
            "bit_rate": produce_text_artifacts_module.TARGET_BITRATE_BPS,
        },
    )
    monkeypatch.setattr(produce_text_artifacts_module, "probe_duration_seconds", lambda path: 60.0)
    monkeypatch.setattr(
        produce_text_artifacts_module,
        "create_full_task_mp3",
        lambda source, target: (_write_bytes(target, b"mp3")),
    )

    def fake_split(source: Path, target: Path, start_seconds: float, end_seconds: float) -> None:
        created_splits.append(target.stem)
        _write_bytes(target, b"split")

    monkeypatch.setattr(produce_text_artifacts_module, "create_split_mp3", fake_split)

    produce_text_artifacts_module.produce_text_artifacts(
        session_dir=session_dir,
        session_id="EN-L-0008-2026-S01",
        person_id=person_id,
        source_wav=tmp_path / "source.wav",
        working_alignment_json=alignment_path,
        dry_run=False,
    )

    runtime_alignment = json.loads((session_dir / "alignment" / "text.json").read_text(encoding="utf-8"))
    assert "t_01" not in created_splits
    assert "t_02" in created_splits
    assert runtime_alignment["omitted_items"][0]["omit_reason"] == "unspoken_title"
    assert "split_mp3" not in runtime_alignment["omitted_items"][0]
    assert all("session_id remains unresolved" not in warning for warning in runtime_alignment["_import_warnings"])


def test_prepare_text_mfa_rejects_unspoken_title_offset_without_title_marker(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    person_id = "EN-L-0008"
    text_root = batch_dir / "working" / person_id / "text"
    _write_silent_wav(text_root / "source" / "text.wav", sample_rate=1000, frame_count=60000)
    _write_textgrid_intervals(text_root / "alignment" / "text.TextGrid", [f"Item {index:02d}" for index in range(2, 57)])
    text_source_json = tmp_path / "text.json"
    _write_json(text_source_json, {"task": "text", "language": "en", "items": _english_text_items(spoken_title_item=False)})

    try:
        prepare_text_mfa_for_person(
            batch_dir=batch_dir,
            person_id=person_id,
            text_source_json=text_source_json,
            cli_language="en",
            dry_run=True,
            replace_existing=True,
        )
    except ValueError as exc:
        assert "first item is not the marked spoken title item t_01" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unmarked omitted title item")


def test_prepare_text_mfa_rejects_unspoken_title_offset_with_wrong_count(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    person_id = "EN-L-0008"
    text_root = batch_dir / "working" / person_id / "text"
    _write_silent_wav(text_root / "source" / "text.wav", sample_rate=1000, frame_count=60000)
    _write_textgrid_intervals(text_root / "alignment" / "text.TextGrid", [f"Item {index:02d}" for index in range(2, 56)])
    text_source_json = tmp_path / "text.json"
    _write_json(text_source_json, {"task": "text", "language": "en", "items": _english_text_items()})

    try:
        prepare_text_mfa_for_person(
            batch_dir=batch_dir,
            person_id=person_id,
            text_source_json=text_source_json,
            cli_language="en",
            dry_run=True,
            replace_existing=True,
        )
    except ValueError as exc:
        assert "does not match spoken TextGrid interval count (54)" in str(exc)
    else:
        raise AssertionError("Expected ValueError for wrong omitted-title interval count")


def test_prepare_text_mfa_rejects_unspoken_title_offset_with_later_mismatch(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260525"
    person_id = "EN-L-0008"
    text_root = batch_dir / "working" / person_id / "text"
    _write_silent_wav(text_root / "source" / "text.wav", sample_rate=1000, frame_count=60000)
    labels = [f"Item {index:02d}" for index in range(2, 57)]
    labels[12] = "unexpected words"
    _write_textgrid_intervals(text_root / "alignment" / "text.TextGrid", labels)
    text_source_json = tmp_path / "text.json"
    _write_json(text_source_json, {"task": "text", "language": "en", "items": _english_text_items()})

    try:
        prepare_text_mfa_for_person(
            batch_dir=batch_dir,
            person_id=person_id,
            text_source_json=text_source_json,
            cli_language="en",
            dry_run=True,
            replace_existing=True,
        )
    except ValueError as exc:
        assert "Refusing unspoken-title offset" in str(exc)
        assert "t_14" in str(exc)
    else:
        raise AssertionError("Expected ValueError for shifted catalog mismatch")


def test_run_text_mfa_docker_command_uses_cached_models_before_download(tmp_path: Path, monkeypatch) -> None:
    batch_dir = tmp_path / "spanish_batch_20260525"
    person_id = "ES-L-0001"
    text_root = batch_dir / "working" / person_id / "text"
    _write_json(text_root / "mfa_manifest.json", {"person_id": person_id})
    _write_text(text_root / "mfa_corpus" / "text_001_d_01.lab", "texto")
    monkeypatch.setattr("alignment_export.run_text_mfa.check_mfa_available", lambda _: "Docker test")

    result = run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id=person_id,
        language="es",
        mfa_executable="docker",
        dry_run=True,
    )

    shell_command = result["command"][-1]
    assert "if [ ! -f /mfa/pretrained_models/acoustic/spanish_mfa.zip ]" in shell_command
    assert "if [ ! -f /mfa/pretrained_models/dictionary/spanish_mfa.dict ]" in shell_command
    assert "mfa align --clean --single_speaker" in shell_command


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
