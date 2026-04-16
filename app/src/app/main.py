"""Entry point for running the application via python -m src.app.main."""

from __future__ import annotations

import os

from . import create_app
from werkzeug.serving import run_simple


def _resolve_env() -> str:
    env_name = os.getenv("FLASK_ENV")
    if env_name:
        return env_name
    env_name = "development"
    os.environ["FLASK_ENV"] = env_name
    return env_name


app = create_app(_resolve_env())


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
