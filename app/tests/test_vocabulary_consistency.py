"""Drift guard for the parallel corpus, language and task vocabularies.

The app, the intake tooling and the database each need their own projection of "which corpora exist"
(display data, analytics, intake profiles, DB constraints, bibliographic registry). They are intentionally
not merged into one registry; this test fails as soon as one projection gains or loses a member.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app" / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "research_data_intake"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app import analytics, publication  # noqa: E402
from app.config import data_conventions  # noqa: E402
from app.research_capabilities import ACTIVE_RESEARCH_CORPORA, RESEARCH_TASK_KEYS  # noqa: E402
from app.research_metadata import ResearchSession  # noqa: E402
from app.routes.public_content import LANGUAGES  # noqa: E402
from app.teaching_content import list_teaching_languages  # noqa: E402
import build_prod_upload_package  # noqa: E402
import intake_batch_common  # noqa: E402
from language_config import LANGUAGE_CONFIGS  # noqa: E402

CORPORA = set(ACTIVE_RESEARCH_CORPORA)
CODE_BY_SLUG = {"spanish": "es", "french": "fr", "german": "de", "english": "en"}


def _module_literal(path: str, name: str) -> object:
    """Read a module-level literal without importing the module (intake scripts have side effects)."""
    tree = ast.parse((REPO_ROOT / path).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{path} defines no literal {name}")


def _db_target_languages() -> set[str]:
    for constraint in ResearchSession.__table__.constraints:
        if getattr(constraint, "name", None) == "ck_research_sessions_target_language":
            return set(re.findall(r"'([a-z]{2})'", str(constraint.sqltext)))
    raise AssertionError("ck_research_sessions_target_language is missing")


def test_the_corpus_set_is_the_four_documented_corpora() -> None:
    assert CORPORA == set(CODE_BY_SLUG)
    assert len(ACTIVE_RESEARCH_CORPORA) == len(CORPORA)


def test_every_corpus_registry_lists_the_same_corpora() -> None:
    registry = publication.load_registry()
    projections = {
        "public LANGUAGES": {language["slug"] for language in LANGUAGES},
        "analytics TRACKED_CORPORA": set(analytics.TRACKED_CORPORA),
        "data_conventions slug map": set(data_conventions.LANGUAGE_SLUG_TO_TARGET_LANGUAGE),
        "publication registry languages": set(registry["languages"]),
        "publication CONTENT_LANGUAGE_CODES": set(publication.CONTENT_LANGUAGE_CODES),
        "intake LANGUAGE_CONFIGS": {config.corpus_slug for config in LANGUAGE_CONFIGS.values()},
    }
    for name, members in projections.items():
        assert members == CORPORA, f"{name} differs from ACTIVE_RESEARCH_CORPORA: {sorted(members ^ CORPORA)}"


def test_every_language_code_projection_agrees() -> None:
    projections = {
        "data_conventions slug map": dict(data_conventions.LANGUAGE_SLUG_TO_TARGET_LANGUAGE),
        "publication CONTENT_LANGUAGE_CODES": dict(publication.CONTENT_LANGUAGE_CODES),
        "intake LANGUAGE_CONFIGS": {config.corpus_slug: config.code for config in LANGUAGE_CONFIGS.values()},
    }
    for name, mapping in projections.items():
        assert mapping == CODE_BY_SLUG, f"{name} maps slugs to different language codes"

    codes = set(CODE_BY_SLUG.values())
    code_sets = {
        "data_conventions TARGET_LANGUAGES": set(data_conventions.TARGET_LANGUAGES),
        "data_conventions STANDARD_VARIETIES": set(data_conventions.STANDARD_VARIETIES),
        "data_conventions TARGET_LANGUAGE_TO_CORPUS_CODE": set(data_conventions.TARGET_LANGUAGE_TO_CORPUS_CODE),
        "DB ck_research_sessions_target_language": _db_target_languages(),
    }
    for name, members in code_sets.items():
        assert members == codes, f"{name} differs from the language codes: {sorted(members ^ codes)}"


def test_the_prod_payload_fallback_resolver_knows_the_same_corpora() -> None:
    """``apply_prod_db_payload`` carries a fallback alias table for when the intake package is absent."""
    source = (REPO_ROOT / "scripts" / "research_data_intake" / "apply_prod_db_payload.py").read_text(encoding="utf-8")
    fallback_slugs = set(re.findall(r'_LanguageConfig\("[a-z]{2}", "([a-z]+)"\)', source))
    assert fallback_slugs == CORPORA


def test_every_task_vocabulary_lists_the_same_tasks() -> None:
    tasks = tuple(RESEARCH_TASK_KEYS)
    assert tuple(data_conventions.TASK_TYPES) == tasks
    assert tuple(intake_batch_common.SUPPORTED_TASKS) == tasks
    assert tuple(build_prod_upload_package._TASK_KEYS) == tasks
    assert set(_module_literal("scripts/research_data_intake/apply_prod_db_payload.py", "SUPPORTED_TASKS")) == set(tasks)


def test_teaching_languages_are_a_subset_of_the_corpora() -> None:
    assert set(list_teaching_languages()) <= CORPORA


def test_the_admin_analytics_table_walks_the_canonical_corpus_order() -> None:
    source = (REPO_ROOT / "app" / "src" / "app" / "routes" / "admin.py").read_text(encoding="utf-8")
    assert "for slug in ACTIVE_RESEARCH_CORPORA:" in source
    assert '("spanish", "french", "german", "english")' not in source
