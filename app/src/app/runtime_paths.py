"""Runtime path getters for canonical PROMAT environments."""

from __future__ import annotations

import logging
import os
from pathlib import Path


logger = logging.getLogger(__name__)


def resolve_environment_name(explicit: str | None = None) -> str:
    """The one environment-name resolution used by config, runtime paths and the entry point.

    Precedence: explicit argument, ``PROMAT_ENV``, ``FLASK_ENV``, ``APP_ENV``. When nothing is set the answer is
    ``production`` (fail-closed): a missing or empty variable never silently selects a debug configuration.
    """
    for candidate in (explicit, os.getenv("PROMAT_ENV"), os.getenv("FLASK_ENV"), os.getenv("APP_ENV")):
        if candidate and candidate.strip():
            return candidate.strip().lower()
    return "production"


def is_dev_environment() -> bool:
    return resolve_environment_name() in ("development", "dev")


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repo_local_runtime_root() -> Path:
    return project_root() / "runtime" / "promat"


def _same_path(left: Path, right: Path) -> bool:
    return left.resolve() == right.resolve()


def get_runtime_root() -> Path:
    runtime_root = os.getenv("PROMAT_RUNTIME_ROOT")
    if not runtime_root or not runtime_root.strip():
        raise RuntimeError(
            "PROMAT_RUNTIME_ROOT environment variable is required.\n"
            "Dev must use the canonical sibling workspace root so data resolves to <workspace>/data.\n"
            "Repo-local runtime/promat is inactive in development."
        )

    resolved = Path(runtime_root).expanduser()
    if is_dev_environment() and _same_path(resolved, repo_local_runtime_root()):
        raise RuntimeError(
            "Repo-local runtime/promat is inactive in development.\n"
            "Use the canonical sibling workspace root that contains data/ and public/."
        )
    return resolved


def get_data_root() -> Path:
    return get_runtime_root() / "data"


def get_sessions_root() -> Path:
    return get_data_root() / "sessions"


def get_public_root() -> Path:
    public_root = os.getenv("PROMAT_PUBLIC_ROOT")
    if not public_root or not public_root.strip():
        raise RuntimeError(
            "PROMAT_PUBLIC_ROOT environment variable is required.\n"
            "Dev must point it to the canonical public path <workspace>/public.\n"
            "No repo-local runtime/promat public fallback is supported."
        )

    resolved = Path(public_root).expanduser()
    repo_local_public_root = repo_local_runtime_root() / "public"
    if is_dev_environment() and _same_path(resolved, repo_local_public_root):
        raise RuntimeError(
            "Repo-local runtime/promat/public is inactive in development.\n"
            "Use the canonical sibling public directory instead."
        )
    return resolved


def get_config_root() -> Path:
    return get_data_root() / "config"


def get_logs_dir() -> Path:
    return get_runtime_root() / "logs"


def log_resolved_paths(log: logging.Logger | None = None) -> None:
    active_logger = log or logger
    runtime_root = get_runtime_root()
    active_logger.info("Resolved runtime paths: RUNTIME_ROOT=%s", runtime_root)
    active_logger.info(
        "Resolved runtime paths: DATA_ROOT=%s SESSIONS_ROOT=%s PUBLIC_ROOT=%s CONFIG_ROOT=%s LOGS_DIR=%s",
        get_data_root(),
        get_sessions_root(),
        get_public_root(),
        get_config_root(),
        get_logs_dir(),
    )


def resolve_runtime_root() -> Path:
    return get_runtime_root()


def resolve_data_root() -> Path:
    return get_data_root()


def resolve_sessions_root() -> Path:
    return get_sessions_root()


def resolve_public_root() -> Path:
    return get_public_root()
