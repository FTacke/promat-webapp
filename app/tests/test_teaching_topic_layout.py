"""Regressions for the shared vertical Teaching topic layout: one centered axis, two functional widths.

Contract: ``docs/spec/platform-data-files.md`` (Teaching topic pages) and ``content/teaching_import/README.md``.
"""

from __future__ import annotations

from pathlib import Path
import re

import yaml

APP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = APP_ROOT.parent
CSS = APP_ROOT / "static" / "css"
PARTIAL = APP_ROOT / "templates" / "partials" / "_teaching_blocks.html"


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


def test_two_content_widths_are_shared_layout_tokens_in_the_design_range() -> None:
    tokens = _css("00_tokens.css")
    editorial = re.search(r"--pm-layout-editorial-width:\s*([^;]+);", tokens)
    component = re.search(r"--pm-layout-component-width:\s*([^;]+);", tokens)
    assert editorial and component, "the two shared width tokens are missing"
    assert 700 <= _rem(editorial.group(1)) * 16 <= 760, "editorial width stays around 700-760 px"
    assert 900 <= _rem(component.group(1)) * 16 <= 960, "component width stays around 900-960 px"
    assert tokens.count("--pm-layout-editorial-width:") == 1 and tokens.count("--pm-layout-component-width:") == 1
    everything = tokens + _css("20_layout.css") + _css("30_components.css")
    for retired in ("--pm-teaching-topic-content-width", "--pm-teaching-topic-block-gap", "--pm-teaching-topic-section-gap"):
        assert retired not in everything, f"{retired} duplicates an existing layout/spacing token"


def test_widths_come_from_one_grid_and_never_from_literal_values() -> None:
    layout = _css("20_layout.css")
    sections = _rule(layout, ".pm-teaching-topic-sections,\n.pm-teaching-block-stack")
    assert "width: min(100%, var(--pm-layout-component-width));" in sections
    assert "margin-inline: auto;" in sections
    grid = _rule(layout, ".pm-teaching-topic-section,\n.pm-teaching-block-stack")
    assert "min(var(--pm-layout-editorial-width), 100%)" in grid
    assert "[editorial-start]" in grid and "[component-start]" in grid
    default = _rule(layout, ".pm-teaching-topic-section > *,\n.pm-teaching-block-stack > .pm-teaching-block")
    assert "grid-column: editorial;" in default
    wide = _rule(
        layout,
        '.pm-teaching-topic-section > .pm-teaching-block-stack,\n.pm-teaching-block-stack > .pm-teaching-block[data-teaching-width="wide"]',
    )
    assert "grid-column: component;" in wide
    rules = (sections, grid, default, wide, _rule(layout, ".pm-teaching-topic-section"), _rule(layout, ".pm-teaching-block-stack"))
    for rule in rules:
        assert not re.search(r"\d(?:rem|px|ch|vw)\b", rule), f"literal length in {rule!r}"
    for selector in (".pm-teaching-topic-header", ".pm-teaching-topic-metadata"):
        assert "var(--pm-layout-" in _rule(layout, selector)
    assert "56rem" not in layout, "no leftover literal topic width"


def test_topic_header_to_content_gap_is_the_shared_section_gap_for_every_topic_page() -> None:
    components = _css("30_components.css")
    assert "gap: var(--pm-layout-section-gap);" in _rule(components, ".pm-teaching-page--topic")
    assert re.search(r"--pm-layout-section-gap:\s*var\(--pm-space-xl\);", _css("00_tokens.css")), "48 px"
    assert "margin-bottom" not in _rule(_css("20_layout.css"), ".pm-teaching-topic-header")
    assert "pm-teaching-topic-header {\n    margin-bottom" not in components, "no second, competing header spacing rule"
    assert "topic-citation" not in components, "the citation section uses the standard section gap"


def test_retired_page_level_width_mechanisms_stay_gone() -> None:
    for name in ("20_layout.css", "30_components.css"):
        css = _css(name)
        assert "pm-teaching-block-grid" not in css, "the two-column page grid is retired"
        assert "pm-teaching-block--span-" not in css, "block span modifiers are retired"
        assert "pm-teaching-further-reading-inline-width" not in css, "no narrowed inline widths for page-level blocks"
        assert "didactic_close" not in css, "the retired rich_text variant has no styles left"
    assert "data-topic-slug" not in _css("30_components.css"), "no per-topic CSS exceptions"


def test_editorial_elements_share_the_column_width_without_a_character_measure_cap() -> None:
    layout = _css("20_layout.css")
    neutralizer = _rule(layout, ".pm-teaching-block-stack > .pm-teaching-block.pm-reading")
    assert "width: 100%;" in neutralizer and "max-width: none;" in neutralizer
    components = _css("30_components.css")
    # no ch-based cap is left on any editorial teaching text or box inside the topic layout
    for selector in (
        ".pm-teaching-further-reading__description",
        ".pm-teaching-further-reading__item-text",
        ".pm-teaching-block--text-plain .promat-content-block__text",
        ".pm-teaching-block--text > .promat-content-block__text,\n.pm-teaching-block--rich-text .pm-teaching-rich-text__body",
        ".pm-teaching-block--citation .pm-admonition__text,\n.pm-teaching-block--citation .pm-teaching-citation__meta",
    ):
        match = re.search(r"(?:^|\n)" + re.escape(selector) + r"\s*\{([^}]*)\}", components)
        assert not match or "max-width" not in match.group(1), selector
    for selector, body in re.findall(r"(?:^|\n)([^{}\n][^{}]*)\{([^{}]*)\}", components + _css("20_layout.css")):
        if "teaching" in selector or "audio-" in selector:
            assert "--pm-layout-reading-width" not in body, f"reading-width cap inside the topic layout: {selector.strip()}"
    # the token itself stays available for other page types
    assert re.search(r"--pm-layout-reading-width:\s*72ch;", _css("00_tokens.css"))
    assert "width: min(100%, var(--pm-layout-reading-width));" in _rule(layout, ".pm-reading")
    # the component-internal lead of audio sections keeps its own measure (component unchanged)
    assert "max-width: 72ch;" in _rule(components, ".audio-section-description")
    audio = _rule(components, ".audio-section")
    assert "width: 100%;" in audio and "max-width: none;" in audio


def test_components_keep_their_internal_columns_and_collapse_on_narrow_viewports() -> None:
    components = _css("30_components.css")
    assert "grid-template-columns: 1fr;" in _rule(components, ".audio-grid")
    assert re.search(
        r"@media \(min-width: 760px\)\s*\{\s*\.audio-grid\s*\{\s*grid-template-columns: repeat\(2, minmax\(0, 1fr\)\);",
        components,
    ), "audio comparison cards and the 2x2 example grid switch to two columns from 760 px"


def test_topic_layout_rules_do_not_hardcode_colors() -> None:
    layout = _css("20_layout.css")
    for selector in (".pm-teaching-topic-section", ".pm-teaching-block-stack"):
        assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgb\(", _rule(layout, selector))


def test_width_variant_is_assigned_centrally_by_block_type_in_the_shared_partial() -> None:
    partial = PARTIAL.read_text(encoding="utf-8")
    wide = re.search(r"teaching_wide_block_types = \[([^\]]*)\]", partial)
    assert wide
    assert set(re.findall(r"'([a-z_]+)'", wide.group(1))) == {
        "audio_example",
        "audio_examples",
        "audio_contrast",
        "video",
        "image",
        "next_topics",
        "topic_grid",
    }
    assert "embed" not in wide.group(1), "maps and other embeds use the editorial width"
    blocks = re.findall(r'<(?:section|figure) id="\{\{ block\.id \}\}"([^>]*)>', partial)
    assert blocks and all('data-teaching-width="{{ block_width }}"' in attrs for attrs in blocks), "every block carries its width variant"


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
