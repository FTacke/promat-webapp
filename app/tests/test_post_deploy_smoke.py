"""The post-deploy smoke and the image smoke run the same page list; keep both honest against the real app."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app" / "src"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

CANONICAL_ORIGIN = "https://pronunciation-matters.de"


def _load_smoke():
    spec = importlib.util.spec_from_file_location("post_deploy_smoke", REPO_ROOT / "scripts" / "post_deploy_smoke.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _client_fetch(client):
    def fetch(path: str):
        response = client.get(path)
        return response.status_code, {key.lower(): value for key, value in response.headers.items()}, response.get_data(as_text=True)

    return fetch


def test_post_deploy_smoke_passes_against_the_composed_application(real_app_factory) -> None:
    smoke = _load_smoke()

    failures = smoke.run_checks(_client_fetch(real_app_factory().test_client()), canonical_origin=CANONICAL_ORIGIN)

    assert failures == []


def test_post_deploy_smoke_reports_a_broken_legal_page_and_a_public_draft(real_app_factory) -> None:
    smoke = _load_smoke()
    client = real_app_factory().test_client()
    base_fetch = _client_fetch(client)
    drafts = smoke.draft_topic_paths()
    assert drafts, "the content tree is expected to contain at least one draft topic"

    def broken_fetch(path: str):
        if path == "/de/privacy":
            return 500, {}, "Internal Server Error"
        if path == drafts[0]:
            return 200, {}, "<title>Draft</title>"
        if path == "/de/research/spanish/speakers":
            return 200, {}, "<title>Speakers</title>"
        return base_fetch(path)

    failures = smoke.run_checks(broken_fetch, canonical_origin=CANONICAL_ORIGIN)

    assert any("/de/privacy" in failure and "500" in failure for failure in failures)
    assert any(drafts[0] in failure and "publicly served" in failure for failure in failures)
    assert any("/de/research/spanish/speakers" in failure and "/login" in failure for failure in failures)


def test_post_deploy_smoke_reports_a_citation_that_points_at_the_domain_root(real_app_factory) -> None:
    smoke = _load_smoke()
    base_fetch = _client_fetch(real_app_factory().test_client())

    def wrong_citation(path: str):
        status, headers, body = base_fetch(path)
        if path == "/de/teaching/spanish/which-pronunciation":
            body = body.replace("https://pronunciation-matters.de/de/teaching/spanish/which-pronunciation", "https://www.pronunciation-matters.de")
        return status, headers, body

    failures = smoke.run_checks(wrong_citation, canonical_origin=CANONICAL_ORIGIN)

    assert any("citation URL" in failure for failure in failures)


def test_deploy_workflow_runs_the_post_deploy_smoke_after_the_deploy_script() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")

    assert workflow.index("bash scripts/deploy_prod.sh") < workflow.index("scripts/post_deploy_smoke.py")
    assert "scripts/post_deploy_smoke.py --base-url https://pronunciation-matters.de" in workflow
