"""Blueprint registration for PROMAT."""

from __future__ import annotations

from flask import Flask

from . import admin, auth, public

BLUEPRINTS = [public.blueprint, auth.blueprint, admin.blueprint]


def register_blueprints(app: Flask) -> None:
    """Register all active blueprints."""
    from .. import register_context_processors

    register_context_processors(app)
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)