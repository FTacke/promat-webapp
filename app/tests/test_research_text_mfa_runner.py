from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest


TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(TEST_REPO_ROOT / "scripts" / "research_data_intake"))

from alignment_export import run_text_mfa  # noqa: E402
from language_config import LANGUAGE_CONFIGS  # noqa: E402


def _prepare_text_mfa_inputs(batch_dir: Path, person_id: str) -> None:
    text_root = batch_dir / "working" / person_id / "text"
    mfa_corpus = text_root / "mfa_corpus"
    mfa_corpus.mkdir(parents=True)
    (mfa_corpus / "text_001_t_01.wav").write_bytes(b"wav")
    (mfa_corpus / "text_001_t_01.lab").write_text("hello\n", encoding="utf-8")
    (text_root / "mfa_manifest.json").write_text(
        '{"person_id": "' + person_id + '", "task": "text", "items": [{"item_id": "t_01"}]}\n',
        encoding="utf-8",
    )


def test_run_command_uses_utf8_and_replace_error_mode(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(command, **kwargs):
        calls.append({"command": command, **kwargs})
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(run_text_mfa.subprocess, "run", fake_run)

    result = run_text_mfa._run_command(["docker", "--version"])

    assert result.returncode == 0
    assert len(calls) == 1
    assert calls[0]["command"] == ["docker", "--version"]
    assert calls[0]["capture_output"] is True
    assert calls[0]["text"] is True
    assert calls[0]["encoding"] == "utf-8"
    assert calls[0]["errors"] == "replace"
    assert calls[0]["check"] is False


def test_resolve_mfa_executable_prefers_cli_over_env(monkeypatch) -> None:
    monkeypatch.setenv("PROMAT_MFA_EXECUTABLE", "docker")

    assert run_text_mfa.resolve_mfa_executable("mfa") == "mfa"


def test_resolve_mfa_executable_uses_env_when_cli_missing(monkeypatch) -> None:
    monkeypatch.setenv("PROMAT_MFA_EXECUTABLE", "mfa")

    assert run_text_mfa.resolve_mfa_executable(None) == "mfa"


def test_resolve_mfa_executable_defaults_to_docker(monkeypatch) -> None:
    monkeypatch.delenv("PROMAT_MFA_EXECUTABLE", raising=False)

    assert run_text_mfa.resolve_mfa_executable(None) == "docker"


def test_check_mfa_available_docker_error_message(monkeypatch) -> None:
    monkeypatch.setattr(
        run_text_mfa,
        "_run_command",
        lambda command: SimpleNamespace(returncode=1, stdout="", stderr="docker unavailable"),
    )

    with pytest.raises(RuntimeError) as exc_info:
        run_text_mfa.check_mfa_available("docker")

    assert "Docker-MFA requested but docker is not available/running" in str(exc_info.value)


def test_language_config_contains_supported_mfa_model_mapping() -> None:
    assert LANGUAGE_CONFIGS["en"].mfa_acoustic_model == "english_mfa"
    assert LANGUAGE_CONFIGS["en"].mfa_dictionary_model == "english_mfa"
    assert LANGUAGE_CONFIGS["fr"].mfa_acoustic_model == "french_mfa"
    assert LANGUAGE_CONFIGS["fr"].mfa_dictionary_model == "french_mfa"
    assert LANGUAGE_CONFIGS["es"].mfa_acoustic_model == "spanish_mfa"
    assert LANGUAGE_CONFIGS["es"].mfa_dictionary_model == "spanish_mfa"
    assert LANGUAGE_CONFIGS["de"].mfa_acoustic_model == "german_mfa"
    assert LANGUAGE_CONFIGS["de"].mfa_dictionary_model == "german_mfa"


def test_docker_mfa_uses_shared_language_cache_for_multiple_people(tmp_path: Path, monkeypatch) -> None:
    script_root = tmp_path / "scripts" / "research_data_intake"
    monkeypatch.setattr(run_text_mfa, "SCRIPT_ROOT", script_root)
    monkeypatch.setattr(run_text_mfa, "check_mfa_available", lambda mfa_executable="docker": "docker-version")
    batch_dir = tmp_path / "english_batch_20260618"
    _prepare_text_mfa_inputs(batch_dir, "EN-L-0001")
    _prepare_text_mfa_inputs(batch_dir, "EN-L-0002")

    first = run_text_mfa.run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id="EN-L-0001",
        language="en",
        mfa_executable="docker",
        dry_run=True,
    )
    second = run_text_mfa.run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id="EN-L-0002",
        language="en",
        mfa_executable="docker",
        dry_run=True,
    )

    expected_cache = script_root / ".mfa_cache" / "shared" / "en"
    assert first["model_cache_dir"] == str(expected_cache)
    assert second["model_cache_dir"] == str(expected_cache)
    first_mfa_volume = next(part for part in first["align_command"] if str(expected_cache) in part)
    second_mfa_volume = next(part for part in second["align_command"] if str(expected_cache) in part)
    assert first_mfa_volume == second_mfa_volume
    assert "EN-L-0001" not in first_mfa_volume
    assert "EN-L-0002" not in second_mfa_volume


def test_docker_mfa_uses_distinct_shared_cache_per_language(tmp_path: Path, monkeypatch) -> None:
    script_root = tmp_path / "scripts" / "research_data_intake"
    monkeypatch.setattr(run_text_mfa, "SCRIPT_ROOT", script_root)
    monkeypatch.setattr(run_text_mfa, "check_mfa_available", lambda mfa_executable="docker": "docker-version")
    batch_dir = tmp_path / "mixed_batch_20260618"
    _prepare_text_mfa_inputs(batch_dir, "EN-L-0001")
    _prepare_text_mfa_inputs(batch_dir, "FR-L-0001")

    english = run_text_mfa.run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id="EN-L-0001",
        language="en",
        mfa_executable="docker",
        dry_run=True,
    )
    french = run_text_mfa.run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id="FR-L-0001",
        language="fr",
        mfa_executable="docker",
        dry_run=True,
    )

    assert english["model_cache_dir"] == str(script_root / ".mfa_cache" / "shared" / "en")
    assert french["model_cache_dir"] == str(script_root / ".mfa_cache" / "shared" / "fr")
    assert english["model_cache_dir"] != french["model_cache_dir"]


def test_docker_mfa_dry_run_separates_model_ensure_from_alignment(tmp_path: Path, monkeypatch) -> None:
    script_root = tmp_path / "scripts" / "research_data_intake"
    monkeypatch.setattr(run_text_mfa, "SCRIPT_ROOT", script_root)
    monkeypatch.setattr(run_text_mfa, "check_mfa_available", lambda mfa_executable="docker": "docker-version")
    batch_dir = tmp_path / "english_batch_20260618"
    _prepare_text_mfa_inputs(batch_dir, "EN-L-0001")

    result = run_text_mfa.run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id="EN-L-0001",
        language="en",
        mfa_executable="docker",
        dry_run=True,
    )

    ensure_shell = result["ensure_command"][-1]
    align_shell = result["align_command"][-1]
    assert "mfa model download acoustic english_mfa" in ensure_shell
    assert "mfa model download dictionary english_mfa" in ensure_shell
    assert align_shell.startswith("mfa align --clean --single_speaker --num_jobs 1")
    assert "mfa model download" not in align_shell


def test_docker_mfa_skips_ensure_command_when_shared_models_exist(tmp_path: Path, monkeypatch) -> None:
    script_root = tmp_path / "scripts" / "research_data_intake"
    monkeypatch.setattr(run_text_mfa, "SCRIPT_ROOT", script_root)
    monkeypatch.setattr(run_text_mfa, "check_mfa_available", lambda mfa_executable="docker": "docker-version")
    batch_dir = tmp_path / "english_batch_20260618"
    cache_dir = script_root / ".mfa_cache" / "shared" / "en"
    (cache_dir / "pretrained_models" / "acoustic").mkdir(parents=True)
    (cache_dir / "pretrained_models" / "dictionary").mkdir(parents=True)
    (cache_dir / "pretrained_models" / "acoustic" / "english_mfa.zip").write_bytes(b"model")
    (cache_dir / "pretrained_models" / "dictionary" / "english_mfa.dict").write_text("word W ER D\n", encoding="utf-8")
    _prepare_text_mfa_inputs(batch_dir, "EN-L-0001")

    result = run_text_mfa.run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id="EN-L-0001",
        language="en",
        mfa_executable="docker",
        dry_run=True,
    )

    assert result["missing_models"] == []
    assert result["ensure_command"] is None


def test_docker_mfa_migrates_legacy_person_cache_to_shared(tmp_path: Path) -> None:
    batch_dir = tmp_path / "english_batch_20260618"
    shared_cache = tmp_path / "shared" / "en"
    legacy_cache = batch_dir / ".mfa_cache" / "EN-L-0001" / "abc123" / "pretrained_models"
    (legacy_cache / "acoustic").mkdir(parents=True)
    (legacy_cache / "dictionary").mkdir(parents=True)
    (legacy_cache / "acoustic" / "english_mfa.zip").write_bytes(b"acoustic")
    (legacy_cache / "dictionary" / "english_mfa.dict").write_text("word W ER D\n", encoding="utf-8")

    migrated = run_text_mfa.migrate_legacy_mfa_models_to_shared(
        batch_dir=batch_dir,
        cache_dir=shared_cache,
        acoustic_model="english_mfa",
        dictionary_model="english_mfa",
    )

    assert len(migrated) == 2
    assert (shared_cache / "pretrained_models" / "acoustic" / "english_mfa.zip").read_bytes() == b"acoustic"
    assert (shared_cache / "pretrained_models" / "dictionary" / "english_mfa.dict").exists()


def test_docker_mfa_dry_run_plans_legacy_cache_migration_without_download(tmp_path: Path, monkeypatch) -> None:
    script_root = tmp_path / "scripts" / "research_data_intake"
    monkeypatch.setattr(run_text_mfa, "SCRIPT_ROOT", script_root)
    monkeypatch.setattr(run_text_mfa, "check_mfa_available", lambda mfa_executable="docker": "docker-version")
    batch_dir = tmp_path / "english_batch_20260618"
    legacy_cache = batch_dir / ".mfa_cache" / "EN-L-0001" / "abc123" / "pretrained_models"
    (legacy_cache / "acoustic").mkdir(parents=True)
    (legacy_cache / "dictionary").mkdir(parents=True)
    (legacy_cache / "acoustic" / "english_mfa.zip").write_bytes(b"acoustic")
    (legacy_cache / "dictionary" / "english_mfa.dict").write_text("word W ER D\n", encoding="utf-8")
    _prepare_text_mfa_inputs(batch_dir, "EN-L-0002")

    result = run_text_mfa.run_text_mfa_for_person(
        batch_dir=batch_dir,
        person_id="EN-L-0002",
        language="en",
        mfa_executable="docker",
        dry_run=True,
    )

    assert set(result["planned_model_migrations"]) == {"acoustic", "dictionary"}
    assert result["missing_models"] == []
    assert result["ensure_command"] is None
