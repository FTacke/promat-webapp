"""Drift guard: the Spanish design article quotes the task catalogs verbatim.

The article keeps its own item lists (it is a citable publication and must render without the
operator-owned runtime catalogs, e.g. in CI and the image smoke). This test, which needs the real
catalogs under ``data/config`` (marker ``data``), fails when the two copies diverge.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app" / "src"))
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("PROMAT_RUNTIME_ROOT", str(REPO_ROOT))
os.environ.setdefault("PROMAT_PUBLIC_ROOT", str(REPO_ROOT / "public"))

from app.routes.public_page_content_data import SPANISH_DESIGN_PAGE_CONTENT  # noqa: E402

CATALOG_DIR = REPO_ROOT / "data" / "config" / "research_player" / "spanish" / "task_catalogs"
# Article content element id -> canonical catalog file.
ARTICLE_LISTS = {
    "spanish-final-wordlist": "wordlist.json",
    "spanish-final-sentence-list": "text.json",
}


def _article_items(element_id: str) -> list[tuple[str, str]]:
    for section in SPANISH_DESIGN_PAGE_CONTENT["sections"]:
        for element in section.get("content_elements", []):
            if element.get("id") == element_id:
                return [(item["label"], item["text"]) for item in element["items"]]
    raise AssertionError(f"design article has no content element {element_id!r}")


def _catalog_items(file_name: str) -> list[tuple[str, str]]:
    payload = json.loads((CATALOG_DIR / file_name).read_text(encoding="utf-8"))
    return [(str(item["item_number"]), item["text"]) for item in payload["items"]]


@pytest.mark.data
@pytest.mark.parametrize(("element_id", "file_name"), sorted(ARTICLE_LISTS.items()))
def test_design_article_items_match_the_canonical_task_catalogs(element_id: str, file_name: str) -> None:
    if not (CATALOG_DIR / file_name).is_file():
        pytest.skip(f"{file_name} is operator-owned runtime config and not present here")

    article = _article_items(element_id)
    catalog = _catalog_items(file_name)

    catalog_by_number = dict(catalog)
    differences = [
        f"{number}: article {text!r} != catalog {catalog_by_number.get(number)!r}"
        for number, text in article
        if number in catalog_by_number and catalog_by_number[number] != text
    ]
    missing = [number for number, _ in article if number not in catalog_by_number]
    assert not differences, differences
    assert not missing, f"article items without catalog counterpart: {missing}"
    assert len(article) == len(catalog), f"article lists {len(article)} items, catalog {len(catalog)}"
