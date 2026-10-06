"""The German corpus has no runtime sessions yet; its protected pages must say so plainly.

Contract: ``docs/spec/research-capabilities.md`` (Corpus-Specific Surface Modes): no planning placeholders or dummy
cards for an empty runtime, and the public ``design`` page is an honest "in preparation" state.
"""

from __future__ import annotations

import pytest

from tests.test_web_hardening import _logged_in_client

FORBIDDEN_PLANNING_COPY = (
    "Geplante Übersicht",
    "Geplante Filter",
    "Struktureller Stand",
    "Geplante Oberfläche",
    "Planned overview",
    "Planned filters",
    "Structural status",
    "Planned interface",
    "strukturell angelegt",
    "technischen Schlüssel",
    "structurally prepared",
    "final technical slug",
)


@pytest.fixture
def german_client(real_app_factory, fixture_runtime_root):
    return _logged_in_client(real_app_factory(runtime_root=fixture_runtime_root))


@pytest.mark.parametrize("ui_lang", ["de", "en"])
@pytest.mark.parametrize("page", ["speakers", "comparison", "phenomena"])
def test_german_protected_pages_render_final_empty_states_without_planning_copy(german_client, ui_lang: str, page: str) -> None:
    response = german_client.get(f"/{ui_lang}/research/german/{page}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for copy in FORBIDDEN_PLANNING_COPY:
        assert copy not in html, f"{page}/{ui_lang} still shows planning copy {copy!r}"


@pytest.mark.parametrize("ui_lang", ["de", "en"])
def test_german_design_page_is_an_honest_in_preparation_state(german_client, ui_lang: str) -> None:
    html = german_client.get(f"/{ui_lang}/research/german/design").get_data(as_text=True)

    assert 'name="robots" content="noindex' in html
    for copy in FORBIDDEN_PLANNING_COPY:
        assert copy not in html
