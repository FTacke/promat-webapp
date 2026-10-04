"""Shared pytest wiring for the PROMAT test suite.

The canonical research-player configuration (task catalogs, player configs) is operator-owned runtime
configuration under ``<PROMAT_RUNTIME_ROOT>/data/config/research_player`` and is deliberately not part of the
repository. Tests that need *some* catalog content use the tracked, minimal fixture runtime root below
instead of depending on a developer machine or on production data. Tests that validate the content of the
real catalogs are marked ``data`` (see ``docs/runbooks/test-and-ci.md``).
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


TESTS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = TESTS_ROOT.parents[1]
FIXTURE_RUNTIME_ROOT = TESTS_ROOT / "fixtures" / "runtime"


def _clear_catalog_caches() -> None:
    scripts_root = str(REPO_ROOT / "scripts" / "research_data_intake")
    if scripts_root not in sys.path:
        sys.path.insert(0, scripts_root)
    src_root = str(REPO_ROOT / "app" / "src")
    if src_root not in sys.path:
        sys.path.insert(0, src_root)

    from app.research_presets import clear_research_preset_caches
    from intake_batch_common import load_task_catalog_item_index

    clear_research_preset_caches()
    load_task_catalog_item_index.cache_clear()


@pytest.fixture
def fixture_runtime_root(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the runtime root at the tracked minimal catalog fixtures and reset catalog caches."""
    monkeypatch.setenv("PROMAT_RUNTIME_ROOT", str(FIXTURE_RUNTIME_ROOT))
    _clear_catalog_caches()
    yield FIXTURE_RUNTIME_ROOT
    monkeypatch.undo()
    _clear_catalog_caches()
