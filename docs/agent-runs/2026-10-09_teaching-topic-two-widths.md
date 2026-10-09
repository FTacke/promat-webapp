# 2026-10-09 Teaching topic pages: two functional content widths and header gap

## Scope

Follow-up to `2026-10-09_teaching-topic-vertical-layout.md`: the single 56 rem column became one centered axis with two functional widths, and the oversized gap between page header and introduction was removed. Typography, colors, accents and component designs are unchanged.

## Tokens

- Reused: `--pm-layout-reading-width` (72 ch text measure), `--pm-layout-section-gap` (= `--pm-space-xl`, 48 px) for header-to-content, section and back-link distance, `--pm-space-container` (24 px) for block gaps, `--pm-overview-*`, `--book-title-accent-dark`, `--promat-wordmark-accent` and the audio/further-reading tokens for all accents (untouched).
- New (layout section of `00_tokens.css`, next to `--pm-layout-reading-width`): `--pm-layout-editorial-width` (46 rem, about 736 px) and `--pm-layout-component-width` (58 rem, about 928 px). No existing token expressed these two widths.
- Removed again: the three tokens of the previous run (`--pm-teaching-topic-content-width`, `-block-gap`, `-section-gap`); they duplicated existing layout/spacing tokens.

## Implementation

- `20_layout.css`: `.pm-teaching-topic-sections` and `.pm-teaching-block-stack` are centered at the component width and are one grid `[component-start] 1fr [editorial-start] min(editorial, 100%) [editorial-end] 1fr [component-end]`. Section headings and blocks default to `grid-column: editorial`; blocks with `data-teaching-width="wide"` (and the block stack inside a section) span `component`. Both widths therefore share one axis, content stays left-aligned, and both shrink fluidly to the viewport (no new breakpoints). Topic header, breadcrumb, title, intro and metadata now use the same tokens instead of 56/68 rem literals.
- `_teaching_blocks.html`: the width variant is assigned centrally by block type (`teaching_wide_block_types`: `audio_example(s)`, `audio_contrast`, `embed`, `video`, `image`, `next_topics`, `topic_grid`) and emitted as `data-teaching-width`; everything else, including `info_box`, `overview`, `teaching_impulses`, `further_reading`, `citation`, is editorial. Content files carry no width information.
- `30_components.css`: header-to-content distance is the shared section gap (`.pm-teaching-page--topic { gap }`, replacing the competing `clamp()` rule, the `margin-bottom` clamp in `20_layout.css` and the mobile `2rem` override); the 3.6 rem citation margin and its section gap were dropped in favor of the standard section gap; the unused `rich_text` variant `didactic_close` styles (retired in the spec) were deleted. Measured gap between metadata and first text: 95 px before, 48 px now (1440, 820, 390 px).

## Docs

- `docs/spec/platform-data-files.md`: topic page rule, header proportions, `teaching_impulses`, `info_box` and `topic_grid` sentences updated to the two-width model.
- `content/teaching_import/README.md`: section "Seitenlayout neuer Themenseiten" now states the rule (editorial by default, wide only for interactive or complex visual components) and where the mapping lives.

## Tests

- `tests/test_teaching_topic_layout.py` rewritten: token presence and ranges, no duplicate/retired tokens, one-grid width mechanism without literal lengths, header gap via the shared token, no retired mechanisms or per-topic CSS, reading measure, component columns and 760 px switch, central width mapping in the partial, content/validator `layout` checks.
- `test_research_sessions.py::test_teaching_topic_blocks_use_editorial_or_component_width_by_function` asserts the exact block order with its width variant (DE and EN).

## Verification

- `ruff`, `compileall`, governance checks, Teaching validator: green; `pytest app/tests`: 1333 passed, 2 skipped, 11 deselected; `node --test`: 64 passed.
- Browser (Playwright, `tmp/ui-qa/2026-10-09-vertical-layout/`, DE/EN, light/dark, 1440/820/390 px): no horizontal overflow; editorial 736 px and component 928 px on desktop, 736/788 px on tablet, 358 px both on mobile; all block centers equal the axis center; header gap 48 px everywhere. Maps, audio cards, hub, overview, landing and design page re-checked (no overflow, hub/overview unchanged).

## Limits

- Both maps use the component width as a block type; an individual map cannot be narrowed without a new semantic variant (not needed: both charts use the extra width).
- Top and bottom back-link pills keep their existing position at the left edge of the page container.
