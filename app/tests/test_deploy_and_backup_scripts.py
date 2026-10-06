"""Structural guards for the production deploy script and the PostgreSQL backup/restore tooling.

The behavioural rehearsal (real PostgreSQL, backup, verified restore) runs in CI via
``scripts/ci_backup_restore_smoke.sh``; these tests pin the properties that must not regress silently.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest


SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
DEPLOY = (SCRIPTS / "deploy_prod.sh").read_text(encoding="utf-8")


def _code_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]


def test_deploy_replaces_only_the_web_container() -> None:
    commands = _code_lines(DEPLOY)

    assert "compose up -d --no-deps --force-recreate web" in commands
    assert not any("--force-recreate" in line and "--no-deps" not in line for line in commands)
    assert not any(line.startswith("compose up -d --build") for line in commands)


def test_deploy_validates_configuration_before_migrations_and_before_replacing_web() -> None:
    validate = DEPLOY.index("Validating production configuration")
    migrate = DEPLOY.index("apply_auth_migration.py --engine postgres")
    replace_web = DEPLOY.index("compose up -d --no-deps --force-recreate web")

    assert validate < migrate < replace_web
    assert "load_config(Flask(" in DEPLOY[validate:migrate]


def test_deploy_still_waits_for_health_and_readiness() -> None:
    assert "compose build web" in DEPLOY
    assert "curl -fsS http://127.0.0.1:8000/health" in DEPLOY
    assert "curl -fsS http://127.0.0.1:8000/ready" in DEPLOY


def test_backup_and_restore_scripts_exist_are_executable_and_parse() -> None:
    for name in ("backup_prod_db.sh", "restore_db_dump.sh", "verify_db_restore.sh", "ci_backup_restore_smoke.sh", "deploy_prod.sh"):
        path = SCRIPTS / name
        assert path.is_file(), name
        if name != "deploy_prod.sh":  # the deploy workflow runs it as `bash scripts/deploy_prod.sh`
            assert os.access(path, os.X_OK), f"{name} must be executable"
        result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True, check=False)
        if result.returncode != 0 and "WSL" in result.stderr:
            pytest.skip("`bash` on this machine is the Windows WSL launcher without an installed distribution")
        assert result.returncode == 0, f"{name}: {result.stderr}"


def test_backup_script_never_reads_or_embeds_database_secrets() -> None:
    code = "\n".join(_code_lines((SCRIPTS / "backup_prod_db.sh").read_text(encoding="utf-8")))

    assert "passwords.env" not in code
    assert "PGPASSWORD" not in code
    assert "POSTGRES_PASSWORD" not in code
    assert "--format=custom" in code
    assert "pg_restore --list" in code  # the dump is validated before it is kept
    assert code.index("mv \"${PARTIAL}\" \"${FINAL}\"") > code.index("pg_restore --list")


def test_production_restore_requires_explicit_opt_in() -> None:
    script = (SCRIPTS / "restore_db_dump.sh").read_text(encoding="utf-8")

    assert 'PRODUCTION_CONTAINER="promat-db-prod"' in script
    assert "--allow-production" in script
    assert "Type the database name" in script
    # --clean (data-destroying) is opt-in; the default restore stops at the first conflict.
    assert "--exit-on-error" in script
    assert script.index("--clean --if-exists") > script.index('"${CLEAN}" -eq 1')


def test_deploy_backs_up_the_database_before_any_migration_and_aborts_when_the_backup_fails() -> None:
    validate = DEPLOY.index("Validating production configuration")
    backup = DEPLOY.index("scripts/backup_prod_db.sh")
    migrate = DEPLOY.index("apply_auth_migration.py --engine postgres")
    replace_web = DEPLOY.index("compose up -d --no-deps --force-recreate web")

    assert validate < backup < migrate < replace_web
    backup_command = DEPLOY[backup:migrate]
    assert "|| fail" in backup_command  # a failed or unverifiable backup stops the deploy before the schema changes
    # Only a database without the auth schema (first deployment) may skip the backup.
    assert "to_regclass('public.users')" in DEPLOY[:backup]


def test_migration_reset_is_refused_outside_development(monkeypatch) -> None:
    import importlib.util

    import pytest

    spec = importlib.util.spec_from_file_location("apply_auth_migration_guard", SCRIPTS.parent / "app" / "scripts" / "apply_auth_migration.py")
    assert spec is not None and spec.loader is not None
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)

    for name in ("PROMAT_ENV", "FLASK_ENV", "APP_ENV"):
        monkeypatch.delenv(name, raising=False)
    assert runner._environment_allows_reset() is False  # nothing set means production

    monkeypatch.setenv("FLASK_ENV", "development")
    assert runner._environment_allows_reset() is True
    monkeypatch.setenv("PROMAT_ENV", "production")
    assert runner._environment_allows_reset() is False  # PROMAT_ENV wins over FLASK_ENV
    monkeypatch.setenv("PROMAT_ENV", "staging")
    assert runner._environment_allows_reset() is False

    monkeypatch.setenv("AUTH_DATABASE_URL", "postgresql://never-contacted/db")
    with pytest.raises(SystemExit) as exit_info:
        runner.apply_postgres_migration(reset=True)
    assert exit_info.value.code == 2


def test_gunicorn_access_log_never_contains_query_string_or_referer() -> None:
    config = (SCRIPTS.parent / "app" / "gunicorn.conf.py").read_text(encoding="utf-8")
    dockerfile = (SCRIPTS.parent / "app" / "Dockerfile").read_text(encoding="utf-8")

    assert "gunicorn.conf.py" in dockerfile
    assert "--access-logfile" not in dockerfile  # the log format lives in one place
    log_format = next(line for line in config.splitlines() if line.startswith("access_log_format"))
    assert "%(U)s" in log_format
    for forbidden in ("%(q)s", "%(r)s", "%(f)s", "%(R)s", "%({"):
        assert forbidden not in log_format


def test_gunicorn_config_is_loadable() -> None:
    namespace: dict[str, object] = {}
    exec(compile((SCRIPTS.parent / "app" / "gunicorn.conf.py").read_text(encoding="utf-8"), "gunicorn.conf.py", "exec"), namespace)

    assert namespace["bind"] == "0.0.0.0:5000"
    assert namespace["accesslog"] == "-"
