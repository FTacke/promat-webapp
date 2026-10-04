"""Structural guards for the CI release gate and the CI-gated production deployment.

These cannot prove the GitHub behaviour end to end, but they make it impossible to quietly reintroduce the
original defect: a `push`-triggered deploy that runs in parallel with (and independent of) CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"


def _load(name: str) -> dict[str, Any]:
    payload = yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _triggers(workflow: dict[str, Any]) -> dict[str, Any]:
    # PyYAML (YAML 1.1) parses the bare key `on` as the boolean True.
    triggers = workflow.get("on", workflow.get(True))
    assert isinstance(triggers, dict)
    return triggers


def _all_run_text(workflow: dict[str, Any]) -> str:
    chunks: list[str] = []
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            chunks.append(str(step.get("run", "")))
    return "\n".join(chunks)


def test_deploy_is_triggered_only_by_completed_ci_or_manual_dispatch() -> None:
    triggers = _triggers(_load("deploy.yml"))

    assert "push" not in triggers
    assert "pull_request" not in triggers
    assert set(triggers) == {"workflow_run", "workflow_dispatch"}
    assert triggers["workflow_run"]["workflows"] == ["CI"]
    assert triggers["workflow_run"]["types"] == ["completed"]
    assert triggers["workflow_run"]["branches"] == ["main"]


def test_deploy_job_requires_successful_ci_push_run_on_main() -> None:
    condition = " ".join(str(_load("deploy.yml")["jobs"]["deploy"]["if"]).split())

    assert "github.event.workflow_run.conclusion == 'success'" in condition
    assert "github.event.workflow_run.event == 'push'" in condition
    assert "github.event.workflow_run.head_branch == 'main'" in condition


def test_deploy_uses_the_tested_commit_and_not_the_branch_tip() -> None:
    workflow = _load("deploy.yml")
    run_text = _all_run_text(workflow)

    assert "github.event.workflow_run.head_sha" in (WORKFLOWS / "deploy.yml").read_text(encoding="utf-8")
    assert 'git checkout --force "${DEPLOY_SHA}"' in run_text
    assert 'git reset --hard "${DEPLOY_SHA}"' in run_text
    assert "$GITHUB_SHA" not in run_text
    assert "bash scripts/deploy_prod.sh" in run_text


def test_deploy_verifies_ci_success_for_the_exact_commit_and_serializes_runs() -> None:
    workflow = _load("deploy.yml")
    run_text = _all_run_text(workflow)

    assert "actions/workflows/ci.yml/runs?head_sha=${deploy_sha}&status=success" in run_text
    assert workflow["concurrency"] == {"group": "production-deploy", "cancel-in-progress": False}
    assert workflow["jobs"]["deploy"]["runs-on"] == ["self-hosted", "promat-prod"]


def test_ci_is_the_full_release_gate() -> None:
    workflow = _load("ci.yml")
    triggers = _triggers(workflow)
    run_text = _all_run_text(workflow)

    assert {"push", "pull_request", "workflow_call"} <= set(triggers)
    assert "python -m ruff check ." in run_text
    assert "python -m compileall" in run_text
    assert "python scripts/ci_governance_checks.py" in run_text
    assert "python -m pytest tests -q" in run_text
    assert "node --test app/tests/js/*.test.mjs" in run_text
    assert "docker build -f app/Dockerfile" in run_text
    assert "docker compose --env-file app/passwords.env.template -f infra/docker-compose.prod.yml config" in run_text
    assert "scripts/ci_image_smoke.py" in run_text


def test_ci_pytest_step_runs_the_whole_suite_without_selecting_a_subset() -> None:
    pytest_steps = [
        step["run"]
        for job in _load("ci.yml")["jobs"].values()
        for step in job.get("steps", [])
        if "pytest" in str(step.get("run", ""))
    ]

    assert pytest_steps == ["python -m pytest tests -q"]
    assert all("::" not in command and " -k " not in command and "--deselect" not in command for command in pytest_steps)


def test_release_gate_job_depends_on_every_other_ci_job() -> None:
    jobs = _load("ci.yml")["jobs"]
    gate = jobs["release-gate"]

    assert gate["if"] == "${{ always() }}"
    assert set(gate["needs"]) == set(jobs) - {"release-gate"}


def test_full_suite_is_not_a_separate_manual_only_workflow() -> None:
    assert not (WORKFLOWS / "full-test.yml").exists()
    release_candidate = _load("release-candidate-check.yml")
    assert release_candidate["jobs"]["release-gate"]["uses"] == "./.github/workflows/ci.yml"
