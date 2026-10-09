"""CSS regressions of the 2026-10-09 correction run: footer flow, native select theming, meta alignment, no ISO tooltips."""

from __future__ import annotations

from pathlib import Path
import re

STATIC = Path(__file__).resolve().parents[1] / "static"
TEMPLATES = Path(__file__).resolve().parents[1] / "templates"


def _css(name: str) -> str:
    return (STATIC / "css" / name).read_text(encoding="utf-8")


def _rule(css: str, selector: str) -> str:
    match = re.search(r"(?:^|\n)" + re.escape(selector) + r"\s*\{([^}]*)\}", css)
    assert match, f"rule {selector!r} not found"
    return match.group(1)


def test_footer_row_can_never_sit_above_the_content_row() -> None:
    shell = _rule(_css("layout.css"), "body.app-shell")
    assert "grid-template-rows: auto 1fr auto;" in shell
    rows = re.search(r"grid-template-rows:([^;]*);", shell).group(1)
    assert "minmax" not in rows, "a zero minimum lets long content run into the footer row"
    landing = _rule(_css("20_layout.css"), "body.app-shell.page-landing")
    assert "grid-template-rows: 1fr auto;" in landing


def test_matrix_stacking_context_keeps_sticky_cells_below_the_app_bar() -> None:
    wrap = _rule(_css("20_layout.css"), ".pm-comparison-matrix-wrap")
    assert "isolation: isolate;" in wrap


def test_color_scheme_follows_the_effective_theme_and_is_not_forced_on_body() -> None:
    layout = _css("layout.css")
    assert "color-scheme" not in layout, "a color-scheme on html/body overrides the theme-bound value"
    tokens = _css("00_tokens.css")
    light = re.search(r':root,\s*html\[data-theme="light"\],\s*html\[data-theme="auto"\]\[data-system-dark="false"\]\s*\{([^}]*)\}', tokens)
    dark = re.search(r'html\[data-theme="dark"\],\s*html\[data-theme="auto"\]\[data-system-dark="true"\]\s*\{([^}]*)\}', tokens)
    assert light and "color-scheme: light;" in light.group(1)
    assert dark and "color-scheme: dark;" in dark.group(1)


def test_native_select_options_use_theme_tokens() -> None:
    components = _css("30_components.css")
    options = _rule(components, "select option,\nselect optgroup")
    assert "background-color: var(--pm-surface-paper);" in options
    assert "color: var(--book-fg);" in options


def test_metadata_cells_align_their_content_to_the_top() -> None:
    assert "align-content: start;" in _rule(_css("40_cards.css"), ".pm-speaker-card__meta-item")
    assert "align-content: start;" in _rule(_css("30_components.css"), ".pm-profile-metadata__row")


def test_no_iso_code_tooltip_or_inline_info_indicator_is_left_in_the_presentation_layer() -> None:
    forbidden = ("pm-info-tip--inline", "pm-l1", "l1BadgeTitle", "ISO 639")
    for path in [*STATIC.glob("css/*.css"), *STATIC.glob("js/**/*.js"), *TEMPLATES.rglob("*.html")]:
        text = path.read_text(encoding="utf-8")
        for needle in forbidden:
            assert needle not in text, f"{needle!r} still present in {path.relative_to(STATIC.parent)}"
    # The set-select and other substantive info indicators stay.
    assert "pm-info-tip__trigger" in (TEMPLATES / "pages" / "research_player.html").read_text(encoding="utf-8")


def test_page_h1_line_height_comes_from_the_shared_display_token() -> None:
    tokens = _css("00_tokens.css")
    token = re.search(r"--pm-type-display-line:\s*([0-9.]+);", tokens)
    assert token and float(token.group(1)) == 1.12, "multi-line page titles need a little more air than 1.0"
    assert "line-height: var(--pm-type-display-line);" in _rule(_css("10_typography.css"), ".promat-page__title")
    for name in ("20_layout.css", "30_components.css"):
        css = _css(name)
        for rule in re.findall(r"(?:^|\n)([^{}\n]*promat-page__title[^{}\n]*)\{([^}]*)\}", css):
            assert "line-height" not in rule[1], f"page-local H1 line-height override: {rule[0].strip()}"
