from __future__ import annotations

import json
import sys
from pathlib import Path


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

from intake_batch_common import ParsedBatchFile  # noqa: E402
from intake_storage import (  # noqa: E402
    ARCHIVE_SESSION_SUBDIRS,
    build_prod_upload_package,
    validate_prod_package,
    validate_runtime_tree,
    write_secure_person_export,
    write_session_archive,
)


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _minimal_runtime_session(tmp_path: Path, session_id: str = "ES-L-0001-2026-S01") -> Path:
    session_dir = tmp_path / "data" / "sessions" / "spanish" / session_id
    _write_text(session_dir / "metadata.json", "{}\n")
    _write_text(session_dir / "alignment" / "wordlist.json", '{"items": []}\n')
    _write_bytes(session_dir / "derived" / "wordlist.mp3", b"ID3\x04\x00\x00\x00\x00\x00\x00")
    _write_bytes(session_dir / "items" / "wordlist" / "wl_001.mp3", b"ID3\x04\x00\x00\x00\x00\x00\x00")
    return session_dir


def test_validate_runtime_tree_rejects_runtime_source_wav(tmp_path: Path) -> None:
    session_dir = _minimal_runtime_session(tmp_path)
    _write_bytes(session_dir / "source" / "wordlist.wav", b"RIFF")

    errors = validate_runtime_tree(session_dir)

    assert any("forbidden runtime path part 'source'" in error for error in errors)


def test_build_prod_upload_package_copies_only_allowed_runtime_artifacts(tmp_path: Path) -> None:
    session_dir = _minimal_runtime_session(tmp_path)
    output_dir = tmp_path / "exports" / "promat_upload_test"

    result = build_prod_upload_package(
        output_dir=output_dir,
        session_roots=[("es", session_dir)],
        db_payload={"sessions": [{"session_id": session_dir.name}]},
        upload_id="promat_upload_test",
    )

    assert (output_dir / "sessions" / "es" / session_dir.name / "metadata.json").exists()
    assert (output_dir / "sessions" / "es" / session_dir.name / "alignment" / "wordlist.json").exists()
    assert (output_dir / "sessions" / "es" / session_dir.name / "derived" / "wordlist.mp3").exists()
    assert (output_dir / "db" / "import_payload.json").exists()
    assert result.manifest_path.exists()
    assert result.checksums_path.exists()
    assert result.report_path.exists()


def test_validate_prod_package_blocks_forbidden_wav_and_source_paths(tmp_path: Path) -> None:
    package_dir = tmp_path / "package"
    _write_text(package_dir / "manifest.json", "{}\n")
    _write_text(package_dir / "reports" / "upload_report.md", "# report\n")
    _write_text(package_dir / "db" / "import_payload.json", "{}\n")
    _write_bytes(package_dir / "sessions" / "es" / "ES-L-0001-2026-S01" / "source" / "wordlist.wav", b"RIFF")

    errors = validate_prod_package(package_dir)

    assert any("forbidden prod package path part 'source'" in error for error in errors)
    assert any("forbidden prod package file type .wav" in error for error in errors)


def test_write_session_archive_marks_raw_wav_as_derivation_source_in_manifest(tmp_path: Path) -> None:
    session_dir = _minimal_runtime_session(tmp_path)
    batch_dir = tmp_path / "en_batch_20260525"
    raw_wav_path = batch_dir / "en_l_0001_wordlist_raw.wav"
    textgrid_path = batch_dir / "en_l_0001_wordlist_processed.TextGrid"
    _write_bytes(raw_wav_path, b"RIFF-raw-wav")
    _write_text(textgrid_path, "TextGrid content")

    raw_wav_entry = ParsedBatchFile(
        source_path=raw_wav_path,
        source_root="batch_root",
        relative_source="en_l_0001_wordlist_raw.wav",
        person_id="EN-L-0001",
        task="wordlist",
        stage="raw",
        file_kind="wav",
        file_role="raw",
    )
    textgrid_entry = ParsedBatchFile(
        source_path=textgrid_path,
        source_root="batch_root",
        relative_source="en_l_0001_wordlist_processed.TextGrid",
        person_id="EN-L-0001",
        task="wordlist",
        stage="processed",
        file_kind="textgrid",
        file_role="alignment_source",
    )

    result = write_session_archive(
        session_dir=session_dir,
        language_code="en",
        session_id=session_dir.name,
        person_id="EN-L-0001",
        source_batch="en_batch_20260525",
        input_files=[raw_wav_entry, textgrid_entry],
        warnings=[],
        importer_version="test",
        archive_root=tmp_path / "archive",
    )

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    raw_entry = next(
        entry for entry in manifest["input_files"] if entry["role"] == "raw" and entry["path"].endswith(".wav")
    )
    assert raw_entry["source_file_used_for_derivation"] is True
    assert raw_entry["source_file_role"] == "raw"
    textgrid_entry_in_manifest = next(
        entry for entry in manifest["input_files"] if entry["path"].endswith(".TextGrid")
    )
    assert "source_file_used_for_derivation" not in textgrid_entry_in_manifest


def test_write_session_archive_does_not_mark_raw_wav_when_processed_wav_present(tmp_path: Path) -> None:
    session_dir = _minimal_runtime_session(tmp_path)
    batch_dir = tmp_path / "en_batch_20260525"
    processed_wav_path = batch_dir / "en_l_0001_wordlist_processed.wav"
    raw_wav_path = batch_dir / "en_l_0001_wordlist_raw.wav"
    textgrid_path = batch_dir / "en_l_0001_wordlist_processed.TextGrid"
    _write_bytes(processed_wav_path, b"RIFF-processed")
    _write_bytes(raw_wav_path, b"RIFF-raw")
    _write_text(textgrid_path, "TextGrid content")

    processed_wav_entry = ParsedBatchFile(
        source_path=processed_wav_path,
        source_root="batch_root",
        relative_source="en_l_0001_wordlist_processed.wav",
        person_id="EN-L-0001",
        task="wordlist",
        stage="processed",
        file_kind="wav",
        file_role="source",
    )
    raw_wav_entry = ParsedBatchFile(
        source_path=raw_wav_path,
        source_root="batch_root",
        relative_source="en_l_0001_wordlist_raw.wav",
        person_id="EN-L-0001",
        task="wordlist",
        stage="raw",
        file_kind="wav",
        file_role="raw",
    )
    textgrid_entry = ParsedBatchFile(
        source_path=textgrid_path,
        source_root="batch_root",
        relative_source="en_l_0001_wordlist_processed.TextGrid",
        person_id="EN-L-0001",
        task="wordlist",
        stage="processed",
        file_kind="textgrid",
        file_role="alignment_source",
    )

    result = write_session_archive(
        session_dir=session_dir,
        language_code="en",
        session_id=session_dir.name,
        person_id="EN-L-0001",
        source_batch="en_batch_20260525",
        input_files=[processed_wav_entry, raw_wav_entry, textgrid_entry],
        warnings=[],
        importer_version="test",
        archive_root=tmp_path / "archive",
    )

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    for entry in manifest["input_files"]:
        assert "source_file_used_for_derivation" not in entry


def test_archive_session_subdirs_does_not_include_origin() -> None:
    assert "origin" not in ARCHIVE_SESSION_SUBDIRS


def test_write_session_archive_creates_source_copy_for_raw_wav_fallback(tmp_path: Path) -> None:
    session_dir = _minimal_runtime_session(tmp_path)
    batch_dir = tmp_path / "en_batch_20260525"
    raw_wav_path = batch_dir / "en_l_0001_wordlist_raw.wav"
    _write_bytes(raw_wav_path, b"RIFF-raw-wav")

    raw_wav_entry = ParsedBatchFile(
        source_path=raw_wav_path,
        source_root="batch_root",
        relative_source="en_l_0001_wordlist_raw.wav",
        person_id="EN-L-0001",
        task="wordlist",
        stage="raw",
        file_kind="wav",
        file_role="raw",
    )

    result = write_session_archive(
        session_dir=session_dir,
        language_code="en",
        session_id=session_dir.name,
        person_id="EN-L-0001",
        source_batch="en_batch_20260525",
        input_files=[raw_wav_entry],
        warnings=[],
        importer_version="test",
        archive_root=tmp_path / "archive",
    )

    archive_dir = result.archive_session_dir
    assert (archive_dir / "raw" / "wordlist.wav").exists()
    assert (archive_dir / "source" / "wordlist.wav").exists()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["task_audio_roles"]["wordlist"]["source_audio_role"] == "raw"
    assert manifest["task_audio_roles"]["wordlist"]["source_file_path"] == "raw/wordlist.wav"


def test_write_secure_person_export_writes_json_to_archive(tmp_path: Path) -> None:
    archive_session_dir = tmp_path / "archive" / "sessions" / "en" / "EN-L-0001-2026-S01"
    archive_session_dir.mkdir(parents=True, exist_ok=True)

    write_secure_person_export(
        archive_session_dir=archive_session_dir,
        person_id="EN-L-0001",
        secure_data={
            "last_name": "Mustermann",
            "first_name": "Anna",
            "email": "anna@example.test",
            "research_consent_signed": "yes",
            "needs_review": False,
        },
    )

    secure_json = archive_session_dir / "secure" / "secure_person_intake.json"
    assert secure_json.exists()
    payload = json.loads(secure_json.read_text(encoding="utf-8"))
    assert payload["person_id"] == "EN-L-0001"
    assert payload["last_name"] == "Mustermann"
    assert payload["email"] == "anna@example.test"