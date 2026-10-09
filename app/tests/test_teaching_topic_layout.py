"""Regressions for the shared vertical Teaching topic layout (2026-10-09): one centered column, flexible components.

Contract: ``docs/spec/platform-data-files.md`` (Teaching topic pages) and ``content/teaching_import/README.md``.
"""

from __future__ import annotations

from pathlib import Path
import re

import yaml

APP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = APP_ROOT.parent
CSS = APP_ROOT / "static" / "css"


def _css(name: str) -> str:
    return (CSS / name).read_text(encoding="utf-8")


def _rule(css: str, selector: str) -> str:
    match = re.search(r"(?:^|\n)" + re.escape(selector) + r"\s*\{([^}]*)\}", css)
    assert match, f"rule {selector!r} not found"
    return match.group(1)


def _rem(value: str) -> float:
    match = re.fullmatch(r"\s*([0-9.]+)rem\s*", value)
    assert match, value
    return float(match.group(1))


def test_content_column_width_is_a_single_shared_token_in_the_design_range() -> None:
    tokens = _css("00_tokens.css")
    width = re.search(r"--pm-teaching-topic-content-width:\s*([^;]+);", tokens)
    assert width, "the shared content-width token is missing"
    assert 50 <= _rem(width.group(1)) * 16 <= 56 * 16 + 1, "column width must stay around 800-900 px"
    sections = _rule(_css("20_layout.css"), ".pm-teaching-page--topic .pm-teaching-topic-sections")
    assert "var(--pm-teaching-topic-content-width)" in sections
    assert "margin-inline: auto;" in sections


def test_block_stack_is_a_single_column_on_every_viewport() -> None:
    layout = _css("20_layout.css")
    stack = _rule(layout, ".pm-teaching-block-stack")
    assert "grid-template-columns: minmax(0, 1fr);" in stack
    for name in ("20_layout.css", "30_components.css"):
        css = _css(name)
        assert "pm-teaching-block-grid" not in css, "the two-column page grid is retired"
        assert "pm-teaching-block--span-" not in css, "block span modifiers are retired"
        assert "pm-teaching-further-reading-inline-width" not in css, "no narrowed inline widths for page-level blocks"


def test_page_level_blocks_use_the_full_column_but_running_text_keeps_a_reading_measure() -> None:
    components = _css("30_components.css")
    text = _rule(
        components,
        ".pm-teaching-block--text > .promat-content-block__text,\n.pm-teaching-block--rich-text .pm-teaching-rich-text__body",
    )
    assert "var(--pm-layout-reading-width)" in text
    reading = re.search(r"--pm-layout-reading-width:\s*(\d+)ch;", _css("00_tokens.css"))
    assert reading and 65 <= int(reading.group(1)) <= 75
    assert "max-width: none;" in _rule(components, ".pm-teaching-page--topic .pm-teaching-block--citation")
    audio = _rule(components, ".audio-section")
    assert "width: 100%;" in audio and "max-width: none;" in audio


def test_components_keep_their_internal_columns_and_collapse_on_narrow_viewports() -> None:
    components = _css("30_components.css")
    assert "grid-template-columns: 1fr;" in _rule(components, ".audio-grid")
    assert re.search(
        r"@media \(min-width: 760px\)\s*\{\s*\.audio-grid\s*\{\s*grid-template-columns: repeat\(2, minmax\(0, 1fr\)\);",
        components,
    ), "audio comparison cards and the 2x2 example grid switch to two columns from 760 px"


def test_section_rhythm_and_dark_mode_use_shared_tokens_only() -> None:
    tokens = _css("00_tokens.css")
    for token in ("--pm-teaching-topic-block-gap", "--pm-teaching-topic-section-gap"):
        assert token in tokens
    components = _css("30_components.css")
    section = _rule(components, ".pm-teaching-page--topic .pm-teaching-topic-section")
    assert "var(--pm-teaching-topic-block-gap)" in section
    spacing = _rule(components, ".pm-teaching-page--topic .pm-teaching-topic-section + .pm-teaching-topic-section")
    assert "var(--pm-teaching-topic-section-gap)" in spacing
    topic_css = "\n".join(
        _rule(components, selector)
        for selector in (".pm-teaching-page--topic .pm-teaching-topic-section", ".pm-teaching-block-stack .pm-teaching-download-card")
    )
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", topic_css), "layout rules must not hardcode colors (light/dark come from tokens)"


def test_topic_content_files_carry_no_per_block_layout_keys() -> None:
    files = [path for path in sorted((REPO_ROOT / "content" / "teaching").glob("*/*/??.yaml")) if path.parent.name != "hubs"]
    assert files
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for index, block in enumerate(data.get("blocks") or [], start=1):
            assert "layout" not in block, f"{path.relative_to(REPO_ROOT)} block {index} still sets the retired layout key"


def test_validator_rejects_the_retired_layout_key() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("validate_teaching_content", REPO_ROOT / "scripts" / "validate_teaching_content.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors: list[str] = []
    module._validate_topic_layout(errors, "spanish", "demo", {"blocks": [{"type": "text"}, {"type": "text", "layout": {"span": 1}}]})
    assert len(errors) == 1 and "block 2" in errors[0]
