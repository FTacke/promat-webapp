from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))
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
from build_prod_upload_package import _discover_all_runtime_sessions  # noqa: E402


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

    assert (output_dir / "sessions" / "spanish" / session_dir.name / "metadata.json").exists()
    assert (output_dir / "sessions" / "spanish" / session_dir.name / "alignment" / "wordlist.json").exists()
    assert (output_dir / "sessions" / "spanish" / session_dir.name / "derived" / "wordlist.mp3").exists()
    assert not (output_dir / "sessions" / "es").exists()
    assert (output_dir / "db" / "import_payload.json").exists()
    assert result.manifest_path.exists()
    assert result.checksums_path.exists()
    assert result.report_path.exists()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert "manifest.json" in manifest["files"]
    assert "checksums.sha256" in manifest["files"]
    assert "reports/upload_report.md" in manifest["files"]


def test_build_prod_upload_package_copies_research_player_config(tmp_path: Path) -> None:
    session_dir = _minimal_runtime_session(tmp_path)
    config_root = tmp_path / "data" / "config" / "research_player"
    _write_text(config_root / "english" / "player_config.json", '{"language": "english"}\n')
    _write_text(config_root / "english" / "phenomena_presets.json", '{"language": "english", "presets": []}\n')
    output_dir = tmp_path / "exports" / "promat_upload_test"

    build_prod_upload_package(
        output_dir=output_dir,
        session_roots=[("es", session_dir)],
        config_roots=[config_root],
        upload_id="promat_upload_test",
    )

    assert (output_dir / "config" / "research_player" / "english" / "player_config.json").exists()
    assert (output_dir / "config" / "research_player" / "english" / "phenomena_presets.json").exists()
    assert validate_prod_package(output_dir) == []


def test_discover_all_runtime_sessions_uses_canonical_language_codes(tmp_path: Path, monkeypatch) -> None:
    session_dir = _minimal_runtime_session(tmp_path, session_id="ES-L-0002-2026-S01")
    english_dir = tmp_path / "data" / "sessions" / "english" / "EN-L-0001-2026-S01"
    _write_text(english_dir / "metadata.json", "{}\n")
    _write_text(english_dir / "alignment" / "text.json", "{}\n")
    _write_bytes(english_dir / "derived" / "text.mp3", b"mp3")
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(tmp_path))

    discovered = _discover_all_runtime_sessions()

    assert ("en", english_dir) in discovered
    assert ("es", session_dir) in discovered


def test_validate_prod_package_blocks_forbidden_wav_and_source_paths(tmp_path: Path) -> None:
    package_dir = tmp_path / "package"
    _write_text(package_dir / "manifest.json", "{}\n")
    _write_text(package_dir / "reports" / "upload_report.md", "# report\n")
    _write_text(package_dir / "db" / "import_payload.json", "{}\n")
    _write_bytes(package_dir / "sessions" / "spanish" / "ES-L-0001-2026-S01" / "source" / "wordlist.wav", b"RIFF")

    errors = validate_prod_package(package_dir)

    assert any("forbidden prod package path part 'source'" in error for error in errors)
    assert any("forbidden prod package file type .wav" in error for error in errors)


def test_validate_prod_package_rejects_language_code_session_directory(tmp_path: Path) -> None:
    package_dir = tmp_path / "package"
    _write_text(package_dir / "sessions" / "fr" / "FR-L-0001-2026-S01" / "metadata.json", "{}\n")
    _write_text(package_dir / "manifest.json", json.dumps({"files": ["manifest.json", "checksums.sha256", "sessions/fr/FR-L-0001-2026-S01/metadata.json"]}) + "\n")
    _write_text(
        package_dir / "checksums.sha256",
        "\n".join(
            [
                f"{hashlib.sha256((package_dir / 'manifest.json').read_bytes()).hexdigest()}  manifest.json",
                f"{hashlib.sha256((package_dir / 'sessions' / 'fr' / 'FR-L-0001-2026-S01' / 'metadata.json').read_bytes()).hexdigest()}  sessions/fr/FR-L-0001-2026-S01/metadata.json",
            ]
        )
        + "\n",
    )

    errors = validate_prod_package(package_dir)

    assert any("must use corpus slug 'french', got 'fr'" in error for error in errors)


def test_build_prod_upload_package_writes_lf_checksums_and_linux_sha256_format(tmp_path: Path) -> None:
    session_dir = _minimal_runtime_session(tmp_path)
    output_dir = tmp_path / "exports" / "promat_upload_test"

    build_prod_upload_package(
        output_dir=output_dir,
        session_roots=[("fr", session_dir)],
        upload_id="promat_upload_test",
    )

    checksums_path = output_dir / "checksums.sha256"
    payload = checksums_path.read_bytes()
    assert b"\r" not in payload
    text_payload = payload.decode("utf-8")
    assert text_payload.endswith("\n")
    for line in text_payload.splitlines(keepends=True):
        assert line.endswith("\n")
        digest, relative_path = line[:-1].split("  ", 1)
        assert len(digest) == 64
        assert all(char in "0123456789abcdef" for char in digest)
        assert "\\" not in relative_path
        assert not relative_path.startswith("/")


def test_validate_prod_package_detects_crlf_checksums(tmp_path: Path) -> None:
    package_dir = tmp_path / "package"
    _write_text(package_dir / "sessions" / "french" / "FR-L-0001-2026-S01" / "metadata.json", "{}\n")
    _write_text(
        package_dir / "manifest.json",
        json.dumps(
            {
                "files": [
                    "checksums.sha256",
                    "manifest.json",
                    "sessions/french/FR-L-0001-2026-S01/metadata.json",
                ]
            }
        )
        + "\n",
    )
    manifest_digest = hashlib.sha256((package_dir / "manifest.json").read_bytes()).hexdigest()
    metadata_digest = hashlib.sha256(
        (package_dir / "sessions" / "french" / "FR-L-0001-2026-S01" / "metadata.json").read_bytes()
    ).hexdigest()
    (package_dir / "checksums.sha256").write_bytes(
        (f"{manifest_digest}  manifest.json\r\n{metadata_digest}  sessions/french/FR-L-0001-2026-S01/metadata.json\r\n").encode(
            "utf-8"
        )
    )

    errors = validate_prod_package(package_dir)

    assert any("contains CR characters" in error for error in errors)


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
