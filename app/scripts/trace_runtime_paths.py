"""Trace runtime data paths without secrets.

Usage:
  python scripts/trace_runtime_paths.py

The script prints resolved runtime paths based on the canonical environment
variables. It does not print credentials.
"""

from __future__ import annotations

import os
from pathlib import Path


def _env(name: str) -> str | None:
    value = os.getenv(name)
    return value if value else None


def _resolve_runtime_root() -> Path | None:
    runtime_root = _env("PROMAT_RUNTIME_ROOT")
    if runtime_root:
        return Path(runtime_root)
    return None


def _print_path(label: str, path: Path | None, public: bool | None = None) -> None:
    if path is None:
        print(f"- {label}: <missing>")
        return
    flag = ""
    if public is True:
        flag = " (public)"
    elif public is False:
        flag = " (restricted)"
    exists = "OK" if path.exists() else "MISSING"
    print(f"- {label}:{flag} {path} [{exists}]")


def main() -> None:
    print("Runtime path trace (no secrets)")
    print(
        f"- FLASK_ENV/APP_ENV: {os.getenv('FLASK_ENV') or os.getenv('APP_ENV') or 'production'}"
    )

    runtime_root = _resolve_runtime_root()
    public_root = _env("PROMAT_PUBLIC_ROOT")

    if not runtime_root:
        print("- NOTE: repo-local runtime/promat is inactive in dev; PROMAT_RUNTIME_ROOT must be set explicitly")

    _print_path("PROMAT_RUNTIME_ROOT", runtime_root)
    _print_path(
        "PROMAT_PUBLIC_ROOT", Path(public_root) if public_root else None, public=True
    )

    if runtime_root:
        data_root = runtime_root / "data"
        _print_path("DATA_ROOT", data_root)
        _print_path("SESSIONS_ROOT", data_root / "sessions", public=False)
        _print_path("AUTH_DB_DIR", data_root / "db", public=False)
        _print_path(
            "POSTGRES_DEV_DATA_DIR",
            Path(_env("POSTGRES_DEV_DATA_DIR"))
            if _env("POSTGRES_DEV_DATA_DIR")
            else data_root / "db" / "postgres_dev",
            public=False,
        )

    if public_root:
        public_root_path = Path(public_root)
        _print_path("PUBLIC_ROOT", public_root_path, public=True)

    print(
        "- AUTH_DATABASE_URL: <redacted>"
        if _env("AUTH_DATABASE_URL")
        else "- AUTH_DATABASE_URL: <missing>"
    )


if __name__ == "__main__":
    main()
