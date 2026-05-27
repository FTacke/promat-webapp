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
