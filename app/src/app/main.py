"""Entry point for running the application via python -m src.app.main."""

from __future__ import annotations

import os

from . import create_app
from werkzeug.serving import make_server


def _resolve_env() -> str:
    env_name = os.getenv("FLASK_ENV")
    if env_name:
        return env_name
    env_name = "development"
    os.environ["FLASK_ENV"] = env_name
    return env_name


app = create_app(_resolve_env())


if __name__ == "__main__":
    explicit_debug = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    app.debug = explicit_debug
    app.config["TEMPLATES_AUTO_RELOAD"] = explicit_debug

    server = make_server("0.0.0.0", 8000, app, threaded=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
