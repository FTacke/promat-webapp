# Teaching: R am Silbenende + Impulse Restructure — 2026-06-02

## Scope

Cleanup and structural improvements across the teaching topic system:

1. Remove `status_box` from the system (was only used on `r-am-silbenende`; replaced by status badge in topic_meta).
2. Add `teaching_impulses` as a proper block type with structured `items`.
3. Restructure impulse sections on `which-pronunciation` (DE/EN) from `rich_text--didactic_close span:2` to `text span:1` + `teaching_impulses span:1`.
4. Rewrite `r-am-silbenende` (DE/EN) YAML: remove `status_box`, fix block structure, reduce 3 `audio_examples` to 1, add Material section.
5. Further-reading CTA: change from separate CTA paragraph to inline link in the text paragraph. CTA text changed from `Hier mehr erfahren` → `Mehr erfahren` (DE) / `Learn more` (EN).
6. Status badge: `In Vorbereitung` / `In preparation` now shows as a small pill badge in the topic_meta detail row.

## Changes

### `content/teaching/spanish/r-am-silbenende/de.yaml`

Full rewrite:
- Removed `status_box` block.
- Removed `variant: plain` from `text` blocks.
- Reduced from 3 `audio_examples` blocks to 1 (title `Hörvergleich`).
- Impulse section: `rich_text--didactic_close span:2` → `text span:1` + `teaching_impulses span:1`.
- Added `section_heading` + `text span:1` before the existing `download span:1` (Material section).

### `content/teaching/spanish/r-am-silbenende/en.yaml`

Same structural changes in English. Section heading `Teaching classification` updated to `Teaching context`.

### `content/teaching/spanish/which-pronunciation/de.yaml`

- Impulse section: `text span:2` → `text span:1`; `rich_text--didactic_close span:2` → `teaching_impulses span:1`.
- `further_reading` first item title: `` `ll` und `y` `` → `Aussprache von ll und y`.
- Both `further_reading` CTAs: `Hier mehr erfahren` → `Mehr erfahren`.

### `content/teaching/spanish/which-pronunciation/en.yaml`

- Same impulse restructuring in English.
- First `further_reading` item title: `` `ll` and `y` `` → `Pronunciation of ll and y`.
- Both CTAs: `Learn more here` → `Learn more`.

### `app/src/app/teaching_content.py`

- Removed `status_box` block handler from `_topic_blocks()`.
- Added `"teaching_impulses": 1` to `_BLOCK_LAYOUT_SPAN_DEFAULTS`.
- Added `_teaching_impulse_item_entries()` helper.
- Added `teaching_impulses` handler in `_topic_blocks()`.

### `app/templates/partials/_teaching_blocks.html`

- Removed `status_box` rendering from `render_block`.
- Added `teaching_impulses` rendering: `<ol class="pm-teaching-impulses">` with `<li>` items containing `<strong>` title + `<p>` body; number markers via `::before` CSS counter.
- Modified `render_topic_metadata_rows`: added `data-key="{{ item.key }}"` to the `.pm-teaching-topic-meta__detail` span.
- Modified `render_further_reading_item`: CTA is now an inline link appended to the text paragraph; separate action `<p>` removed.

### `app/static/css/30_components.css`

- Updated `:has()` selector to cover both `pm-teaching-rich-text--didactic_close` and new `pm-teaching-block--teaching-impulses`.
- Added `.pm-teaching-block--teaching-impulses`: rosé background, `--pm-teaching-further-reading-border`, same radius/padding pattern as `didactic_close`.
- Added `.pm-teaching-impulses`, `.pm-teaching-impulses__item`, `::before` (numbered circle marker, same token values as `didactic_close`), `.pm-teaching-impulses__item-title`, `.pm-teaching-impulses__item-body`.
- Added `.pm-teaching-topic-meta__detail[data-key="status"] .pm-teaching-topic-meta__value`: pill badge using `--pm-teaching-status-*` tokens (same as `status_box`).

### `app/tests/test_teaching_content.py`

- Replaced `test_build_teaching_topic_page_parses_preparation_status_box_and_plain_sections` with `test_build_teaching_topic_page_parses_teaching_impulses`.

## Not changed

- `status_box` CSS (`.pm-teaching-status-box`) kept for now; can be removed once the template reference is gone and there is no YAML usage.
- `rich_text--didactic_close` CSS kept; still valid for any future use.
- Comparison player numbers and word-list numbers not touched.
