"""Provenance helpers for research intake archive writes.

Everything here is additive metadata: nothing in this module changes how intake classifies, converts or
publishes files. All lookups degrade to the literal string ``"unknown"`` (or ``"unavailable"`` for tools)
instead of failing an intake run.
"""

from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

from fixity import sha256_file


UNKNOWN = "unknown"
UNAVAILABLE = "unavailable"
PROVENANCE_SCHEMA_VERSION = 2
REPO_ROOT = Path(__file__).resolve().parents[2]

_REVISION_PATTERN = re.compile(r"^[0-9a-fA-F]{7,40}$")
_cache: dict[str, Any] = {}


def _run(command: list[str], *, cwd: Path | None = None, timeout: float = 10.0) -> str | None:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return (completed.stdout or completed.stderr or "").strip() or None


def current_git_revision(repo_root: Path | None = None) -> str:
    """Return the git revision of the running code, ``<sha>`` or ``<sha>-dirty``, else ``"unknown"``.

    ``PROMAT_GIT_REVISION`` may pin a value (for example when the code is run from an export without ``.git``).
    """
    override = (os.getenv("PROMAT_GIT_REVISION") or "").strip()
    if override:
        return override
    root = repo_root or REPO_ROOT
    cache_key = f"git:{root}"
    if cache_key in _cache:
        return _cache[cache_key]
    revision = _run(["git", "rev-parse", "HEAD"], cwd=root)
    if not revision or not _REVISION_PATTERN.match(revision):
        value = UNKNOWN
    else:
        status = _run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=root)
        value = f"{revision}-dirty" if status else revision
    _cache[cache_key] = value
    return value


def importer_version(tool_name: str, repo_root: Path | None = None) -> str:
    """``<tool>@<git revision>``; replaces the former constant importer label."""
    return f"{tool_name}@{current_git_revision(repo_root)}"


def _first_line(text: str | None) -> str:
    return (text or "").splitlines()[0].strip() if text else UNAVAILABLE


def tool_versions() -> dict[str, str]:
    """Best-effort ffmpeg and Montreal Forced Aligner versions (cached per process)."""
    if "tools" in _cache:
        return dict(_cache["tools"])
    ffmpeg = _first_line(_run(["ffmpeg", "-version"], timeout=10.0))
    mfa_executable = (os.getenv("PROMAT_MFA_EXECUTABLE") or "mfa").strip() or "mfa"
    mfa = _first_line(_run([mfa_executable, "version"], timeout=30.0))
    versions = {"ffmpeg": ffmpeg, "mfa": mfa}
    _cache["tools"] = versions
    return dict(versions)


def clear_provenance_cache() -> None:
    _cache.clear()


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def normalized_relative_source(value: str) -> str:
    """Keep only a relative POSIX-style path; never record drive letters or absolute prefixes."""
    text = (value or "").replace("\\", "/")
    if re.match(r"^[A-Za-z]:", text):
        text = text[2:]
    return text.lstrip("/")


def workbook_provenance(workbook_path: Path) -> dict[str, Any]:
    return {
        "original_filename": workbook_path.name,
        "role": "intake_workbook",
        "storage_class": "secure",
        "size": workbook_path.stat().st_size,
        "sha256": sha256_file(workbook_path),
    }


def catalog_provenance(catalog_path: Path) -> dict[str, Any]:
    """Describe a task catalog without interpreting it beyond a few best-effort header fields."""
    record: dict[str, Any] = {
        "original_filename": catalog_path.name,
        "role": "task_catalog",
        "size": catalog_path.stat().st_size,
        "sha256": sha256_file(catalog_path),
        "language": UNKNOWN,
        "catalog_type": UNKNOWN,
        "item_count": None,
        "schema_version": UNKNOWN,
    }
    try:
        payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return record
    if isinstance(payload, dict):
        for source_key, target_key in (
            ("language", "language"),
            ("language_code", "language"),
            ("task_type", "catalog_type"),
            ("type", "catalog_type"),
            ("schema_version", "schema_version"),
            ("schema", "schema_version"),
        ):
            value = payload.get(source_key)
            if isinstance(value, (str, int)) and record[target_key] == UNKNOWN:
                record[target_key] = str(value)
        items = payload.get("items")
        if isinstance(items, list):
            record["item_count"] = len(items)
    elif isinstance(payload, list):
        record["item_count"] = len(payload)
    return record
