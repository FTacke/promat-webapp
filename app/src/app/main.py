"""Entry point for running the application via python -m src.app.main."""

from __future__ import annotations

import os

from . import create_app
from .runtime_paths import resolve_environment_name
from werkzeug.serving import run_simple

# Fail-closed: without PROMAT_ENV / FLASK_ENV / APP_ENV this is production. Local development sets
# FLASK_ENV=development explicitly (scripts/dev-start.ps1).
app = create_app(resolve_environment_name())


def _resolve_debug() -> bool:
    explicit_debug = os.getenv("FLASK_DEBUG")
    if explicit_debug and explicit_debug.strip():
        return explicit_debug.lower() in ("1", "true", "yes")
    return bool(app.config.get("DEBUG"))


if __name__ == "__main__":
    debug_enabled = _resolve_debug()
    app.debug = debug_enabled
    app.config["TEMPLATES_AUTO_RELOAD"] = debug_enabled

    run_simple(
        "0.0.0.0",
        8000,
        app,
        threaded=True,
        use_debugger=debug_enabled,
        use_reloader=debug_enabled,
        reloader_interval=1,
    )
