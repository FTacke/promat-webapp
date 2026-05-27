from __future__ import annotations

import importlib
import os
from pathlib import Path
import sys

from flask import Flask
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

TEST_REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(TEST_REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(TEST_REPO_ROOT / "public"))

import app.config as config_module


def _reload_config_module(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    env_name: str,
    rate_limit_storage_uri: str | None,
):
    runtime_root = tmp_path / "runtime"
    public_root = tmp_path / "public"
    runtime_root.mkdir(parents=True, exist_ok=True)
    public_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.delenv("PROMAT_ENV", raising=False)
    monkeypatch.setenv("APP_ENV", env_name)
    monkeypatch.setenv("FLASK_ENV", env_name)
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(runtime_root))
    monkeypatch.setenv("PROMAT_PUBLIC_ROOT", str(public_root))
    monkeypatch.setenv("AUTH_DATABASE_URL", f"sqlite:///{(tmp_path / 'auth.sqlite3').as_posix()}")
    monkeypatch.setenv("FLASK_SECRET_KEY", "test-secret")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.delenv("RATE_LIMIT_STORAGE_URI", raising=False)
    monkeypatch.delenv("RATELIMIT_STORAGE_URI", raising=False)
    monkeypatch.delenv("VITE_APP_VERSION", raising=False)
    monkeypatch.delenv("VITE_GOATCOUNTER_URL", raising=False)
    monkeypatch.delenv("APP_RELEASE_TAG", raising=False)
    monkeypatch.delenv("APP_RELEASE_URL", raising=False)
    if rate_limit_storage_uri is not None:
        monkeypatch.setenv("RATE_LIMIT_STORAGE_URI", rate_limit_storage_uri)

    return importlib.reload(config_module)


def test_testing_load_config_defaults_to_memory_rate_limit_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reloaded = _reload_config_module(
        tmp_path,
        monkeypatch,
        env_name="testing",
        rate_limit_storage_uri=None,
    )
    app = Flask(__name__)

    reloaded.load_config(app, "testing")

    assert app.config["RATE_LIMIT_STORAGE_URI"] == "memory://"
    assert app.config["RATELIMIT_STORAGE_URI"] == "memory://"


def test_production_load_config_requires_rate_limit_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reloaded = _reload_config_module(
        tmp_path,
        monkeypatch,
        env_name="production",
        rate_limit_storage_uri=None,
    )
    app = Flask(__name__)

    with pytest.raises(RuntimeError, match="RATE_LIMIT_STORAGE_URI must be configured"):
        reloaded.load_config(app, "production")


def test_production_load_config_rejects_memory_rate_limit_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reloaded = _reload_config_module(
        tmp_path,
        monkeypatch,
        env_name="production",
        rate_limit_storage_uri="memory://",
    )
    app = Flask(__name__)

    with pytest.raises(RuntimeError, match="must not use memory://"):
        reloaded.load_config(app, "production")


def test_production_load_config_accepts_redis_rate_limit_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reloaded = _reload_config_module(
        tmp_path,
        monkeypatch,
        env_name="production",
        rate_limit_storage_uri="redis://rate_limit:6379/0",
    )
    app = Flask(__name__)

    reloaded.load_config(app, "production")

    assert app.config["RATE_LIMIT_STORAGE_URI"] == "redis://rate_limit:6379/0"
    assert app.config["RATELIMIT_STORAGE_URI"] == "redis://rate_limit:6379/0"


def test_promat_env_selects_production_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROMAT_ENV", "production")
    reloaded = _reload_config_module(
        tmp_path,
        monkeypatch,
        env_name="development",
        rate_limit_storage_uri="redis://rate_limit:6379/0",
    )
    monkeypatch.setenv("PROMAT_ENV", "production")
    reloaded = importlib.reload(config_module)
    app = Flask(__name__)

    reloaded.load_config(app)

    assert app.config["FLASK_ENV"] == "production"
    assert app.config["PROMAT_ENV"] == "production"


def test_release_tag_defaults_to_dev_without_deploy_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reloaded = _reload_config_module(
        tmp_path,
        monkeypatch,
        env_name="testing",
        rate_limit_storage_uri=None,
    )
    app = Flask(__name__)

    reloaded.load_config(app, "testing")

    assert app.config["APP_VERSION"] == "dev"
    assert app.config["APP_RELEASE_TAG"] == "dev"


def test_release_tag_uses_public_deploy_version_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reloaded = _reload_config_module(
        tmp_path,
        monkeypatch,
        env_name="testing",
        rate_limit_storage_uri=None,
    )
    monkeypatch.setenv("VITE_APP_VERSION", "v0.7")
    reloaded = importlib.reload(config_module)
    app = Flask(__name__)

    reloaded.load_config(app, "testing")

    assert app.config["APP_VERSION"] == "v0.7"
    assert app.config["APP_RELEASE_TAG"] == "v0.7"
    assert app.config["APP_RELEASE_URL"].endswith("/releases/tag/v0.7")


def test_goatcounter_url_is_production_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    endpoint = "https://pronunciation-matters.goatcounter.com/count"
    reloaded = _reload_config_module(
        tmp_path,
        monkeypatch,
        env_name="testing",
        rate_limit_storage_uri=None,
    )
    monkeypatch.setenv("VITE_GOATCOUNTER_URL", endpoint)
    reloaded = importlib.reload(config_module)
    app = Flask(__name__)

    reloaded.load_config(app, "testing")

    assert app.config["VITE_GOATCOUNTER_URL"] == endpoint
    assert app.config["GOATCOUNTER_URL"] == ""

    reloaded = _reload_config_module(
        tmp_path,
        monkeypatch,
        env_name="production",
        rate_limit_storage_uri="redis://rate_limit:6379/0",
    )
    monkeypatch.setenv("VITE_GOATCOUNTER_URL", endpoint)
    reloaded = importlib.reload(config_module)
    prod_app = Flask(__name__)

    reloaded.load_config(prod_app, "production")

    assert prod_app.config["GOATCOUNTER_URL"] == endpoint


def test_goatcounter_url_does_not_accept_other_sites(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reloaded = _reload_config_module(
        tmp_path,
        monkeypatch,
        env_name="production",
        rate_limit_storage_uri="redis://rate_limit:6379/0",
    )
    monkeypatch.setenv("VITE_GOATCOUNTER_URL", "https://example.goatcounter.com/count")
    reloaded = importlib.reload(config_module)
    app = Flask(__name__)

    reloaded.load_config(app, "production")

    assert app.config["VITE_GOATCOUNTER_URL"] == "https://example.goatcounter.com/count"
    assert app.config["GOATCOUNTER_URL"] == ""
