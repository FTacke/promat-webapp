"""The French sentence list: one complete sentence per line, in the order of the catalog (operator-side checks).

``french_text.txt`` is the human-readable source of the sentence catalog (``provided_txt:french_text.txt``). It lives in the
gitignored import area, so these checks skip when the file is absent (CI); the catalog check runs with ``pytest -m data``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG = REPO_ROOT / "data" / "config" / "research_player" / "french" / "task_catalogs" / "text.json"
BATCH_SOURCE = REPO_ROOT / "scripts" / "research_data_intake" / "import" / "french_batch_complete_20261008" / "french_text.txt"
SENTENCE_COUNT = 67


def _source_lines() -> list[str]:
    return BATCH_SOURCE.read_text(encoding="utf-8").splitlines()


@pytest.mark.data
@pytest.mark.skipif(not BATCH_SOURCE.is_file(), reason="french_text.txt is not part of this checkout")
def test_french_text_source_has_one_sentence_per_line() -> None:
    lines = _source_lines()
    assert len(lines) == SENTENCE_COUNT
    assert all(line.strip() for line in lines), "empty line in the sentence list"
    assert not any(a.rstrip().endswith(",") and b[:1].islower() for a, b in zip(lines, lines[1:])), "a sentence continues on the next line"


@pytest.mark.data
@pytest.mark.skipif(not (BATCH_SOURCE.is_file() and CATALOG.is_file()), reason="needs the batch source and the runtime catalog")
def test_french_text_source_matches_the_catalog_in_order_and_wording() -> None:
    items = json.loads(CATALOG.read_text(encoding="utf-8"))["items"]
    assert len(items) == SENTENCE_COUNT
    assert [item["item_id"] for item in items] == [f"t_{index:02d}" for index in range(1, SENTENCE_COUNT + 1)]
    assert [line.strip() for line in _source_lines()] == [item["text"].strip() for item in items]
