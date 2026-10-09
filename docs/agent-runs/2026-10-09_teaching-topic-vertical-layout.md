# 2026-10-09 Teaching topic pages: shared vertical layout

## Scope

Replaced the two-column page layout of the Teaching topic pages by one shared vertical layout. The pilot page `/{ui_lang}/teaching/spanish/which-pronunciation` is the reference; the layout is owned by the shared topic template and CSS, so every current and future topic of every Teaching language gets it.

## Architecture

- Removed the per-block `layout.span` model: `_BLOCK_LAYOUT_SPAN_DEFAULTS`, `_block_layout_span`, `_block_layout_payload` and every `layout` payload entry in `app/src/app/teaching_content.py`; removed `pm-teaching-block--span-*` classes from `_teaching_blocks.html`.
- Stripped all `layout: span:` keys from the 10 topic files (Spanish, French; de/en). `scripts/validate_teaching_content.py` now rejects a `layout` key, so it cannot return unnoticed.
- `teaching_page.html`: sections keep their wrapper; the block container is now `pm-teaching-topic-section__stack pm-teaching-block-stack` (single-column grid) instead of the two-column `pm-teaching-block-grid`.
- CSS: new tokens `--pm-teaching-topic-content-width` (56 rem), `--pm-teaching-topic-block-gap`, `--pm-teaching-topic-section-gap`; `.pm-teaching-topic-sections` is the centered column; the two-column grid, the span rules and the narrowed inline widths of `further_reading`, citation and didactic box were removed. Running text keeps `--pm-layout-reading-width` (72 ch); `.audio-section` no longer inherits the 72 ch cap from `.pm-reading` and uses the full column. Section headings fit their text (`justify-self: start`) so the accent underline no longer spans the column.
- Internal component columns are unchanged: two recordings per `audio_contrast` card and the 2×2 `audio_examples` grid from 760 px, one column below.

## Page structure (pilot, DE/EN)

Header (title, intro, metadata) → intro text → "Auf einen Blick" box → Hörvergleich (text, two contrast cards) → Seseo und distinción (text, Spain map, blue box, Hispanoamérica map) → Hörbeispiele Hispanoamerika (text, 2×2 audio grid) → Impulse für den Unterricht (text, impulses box) → Vertiefung → Zitierhinweis → back link.

## Docs

- `docs/spec/platform-data-files.md`: topic page rule rewritten (shared vertical layout, tokens, retired `layout.span`); hub/topic width sentence corrected.
- `content/teaching_import/README.md`: new section "Seitenlayout neuer Themenseiten".

## Tests

- Updated `test_teaching_content.py` (span test replaced by "retired layout key is inert") and `test_research_sessions.py` (class names).
- New: `test_research_sessions.py::test_teaching_topic_page_keeps_one_vertical_content_order` (DE/EN, exact DOM order of all blocks, component grids, citation before back link), `::test_every_teaching_topic_edition_uses_the_shared_vertical_layout` (all languages and UI languages), `tests/test_teaching_topic_layout.py` (width token range, single-column stack, reading measure, component columns and 760 px switch, token-only rhythm/colors, no `layout` keys in content, validator rejects them).

## Verification

- `ruff check .`, `compileall`, `ci_governance_checks.py`, `validate_teaching_content.py`: green.
- `pytest app/tests`: 1329 passed, 2 skipped, 11 deselected; `node --test app/tests/js/*.test.mjs`: 64 passed.
- Browser (Playwright, local dev server, `tmp/ui-qa/2026-10-09-vertical-layout/`): DE and EN, light and dark, 1440/820/390 px: no horizontal overflow; column 896 px on desktop, text 643 px; audio cards two columns at 820 px and up, one column at 390 px; maps render at full column width. Teaching overview, hub (DE/EN) and landing re-checked as unaffected shared-CSS pages.

## Limits

- Audio playback was not exercised in a real audio device; the player markup and scripts are unchanged and covered by the existing tests.
- The French and `r-am-silbenende` topics are drafts and not publicly routable; they were checked via the released-content test fixture only.
