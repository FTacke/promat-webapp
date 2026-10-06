"""Small regressions from the final closure run (TI-14, TI-22, TI-24, TI-32, TI-33, TI-37)."""

from __future__ import annotations

from pathlib import Path

from tests.test_web_hardening import _add_user

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_unknown_login_identifier_still_spends_a_password_verification(real_app_factory, monkeypatch) -> None:
    from app.auth import services

    flask_app = real_app_factory()
    with flask_app.app_context():
        _add_user(user_id="user-1", username="alice")
    calls: list[str] = []
    real = services.spend_password_verification_cost
    monkeypatch.setattr(services, "spend_password_verification_cost", lambda plain: (calls.append(plain), real(plain))[1])
    client = flask_app.test_client()

    unknown = client.post("/auth/login", data={"email": "nobody@example.org", "password": "WrongPass1"})
    known = client.post("/auth/login", data={"email": "alice@example.org", "password": "WrongPass1"})

    assert unknown.status_code == known.status_code == 401
    assert calls == ["WrongPass1"]


def test_dev_entrypoint_and_dev_database_listen_on_loopback_only() -> None:
    main_source = (REPO_ROOT / "app" / "src" / "app" / "main.py").read_text(encoding="utf-8")
    assert "0.0.0.0" not in main_source
    assert 'os.getenv("PROMAT_BIND_HOST", "127.0.0.1")' in main_source
    compose = (REPO_ROOT / "docker-compose.dev-postgres.yml").read_text(encoding="utf-8")
    assert '"127.0.0.1:${PROMAT_DEV_DB_PORT:-54321}:5432"' in compose


def test_access_request_records_the_proxy_fixed_remote_address_not_a_client_header() -> None:
    source = (REPO_ROOT / "app" / "src" / "app" / "routes" / "public.py").read_text(encoding="utf-8")
    assert "ip_address=request.remote_addr," in source
    assert "X-Forwarded-For" not in source


def test_engine_checks_pooled_connections_before_use() -> None:
    source = (REPO_ROOT / "app" / "src" / "app" / "extensions" / "sqlalchemy_ext.py").read_text(encoding="utf-8")
    assert "pool_pre_ping=True" in source


def test_workflow_dispatch_input_does_not_reach_the_shell_unescaped() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "release-candidate-check.yml").read_text(encoding="utf-8")
    assert 'run:' in workflow
    assert "${{ inputs." not in "\n".join(line for line in workflow.splitlines() if "python scripts/qa/responsive_smoke.py" in line)


def test_bcrypt_stays_below_5_while_passlib_is_in_use() -> None:
    requirements = (REPO_ROOT / "app" / "requirements.in").read_text(encoding="utf-8")
    assert any(line.startswith("bcrypt<5") for line in requirements.splitlines())
    lock = (REPO_ROOT / "app" / "requirements.txt").read_text(encoding="utf-8")
    assert "bcrypt==4." in lock


def test_shell_scripts_are_checked_out_with_lf() -> None:
    attributes = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "*.sh text eol=lf" in attributes
