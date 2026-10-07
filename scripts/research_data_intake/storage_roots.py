"""Operator configuration of the machine-dependent storage roots (stdlib only; no intake imports).

Three roots, three roles, never interchangeable (docs/spec/platform-data-files.md, "Storage Roots"):

* ``PROMAT_LOCAL_ARCHIVE_ROOT``  local working archive; the only root intake writes to.
* ``PROMAT_PRESERVATION_ROOT``   institutional preservation copy; written by the preservation tooling only.
* ``PROMAT_BACKUP_ROOT``         physically separate backup copy; written by the backup commands only.

A value comes from the process environment or, when the variable is unset there, from the git-ignored ``.env``
file at the repository root. The process environment always wins, the file is never written, and only the
variables named here are read from it. Nothing has a default: an unset root is an error for whoever needs it.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"

LOCAL_ARCHIVE_ROOT_ENV = "PROMAT_LOCAL_ARCHIVE_ROOT"
PRESERVATION_ROOT_ENV = "PROMAT_PRESERVATION_ROOT"
BACKUP_ROOT_ENV = "PROMAT_BACKUP_ROOT"
STORAGE_ROOT_VARIABLES = (LOCAL_ARCHIVE_ROOT_ENV, PRESERVATION_ROOT_ENV, BACKUP_ROOT_ENV)


class StorageRootNotConfigured(RuntimeError):
    pass


def read_env_file(path: Path | None = None) -> dict[str, str]:
    """Storage-root assignments of the local ``.env`` file; other keys in that file are ignored."""
    env_file = ENV_FILE if path is None else path
    try:
        text = env_file.read_text(encoding="utf-8-sig")
    except OSError:
        return {}
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key in STORAGE_ROOT_VARIABLES and value:
            values[key] = value
    return values


def configured_value(name: str) -> str | None:
    """The configured value of one storage-root variable, or ``None``. The process environment wins."""
    if name not in STORAGE_ROOT_VARIABLES:
        raise ValueError(f"not a storage root variable: {name}")
    value = (os.getenv(name) or "").strip() or read_env_file().get(name)
    return value or None


def configured_source(name: str) -> str | None:
    """Where the value comes from: ``environment``, ``.env`` or ``None`` when the root is not configured."""
    if (os.getenv(name) or "").strip():
        return "environment"
    return ".env" if read_env_file().get(name) else None


def configured_root(name: str) -> Path | None:
    """The configured root as an absolute path, or ``None`` when unset. A relative value is refused."""
    value = configured_value(name)
    if value is None:
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise StorageRootNotConfigured(
            f"{name} must be an absolute path (got {value!r}); a relative root would depend on the working directory."
        )
    return path


def require_root(name: str, *, cli_option: str) -> Path:
    path = configured_root(name)
    if path is None:
        raise StorageRootNotConfigured(
            f"{name} is not configured. Set it in the environment or in {ENV_FILE.name} at the repository root "
            f"(see .env.example), or pass {cli_option}. There is deliberately no default location."
        )
    return path
