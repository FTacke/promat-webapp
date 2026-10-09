# 2026-10-09 Teaching topic pages: running text uses the full editorial width

## Scope

The 72ch cap on running text and on text inside boxes is removed inside the shared Teaching topic layout, so every editorial element ends at the same right edge as the boxes (`--pm-layout-editorial-width`, 46 rem). `--pm-layout-reading-width` is untouched and still drives `.pm-reading`, footnotes and other page types. Component width (58 rem) for audio comparisons and the multi-column audio examples is unchanged.

## CSS changes (no new token, no literal)

- `30_components.css`, removed: the `.pm-teaching-block--text` / `--rich-text` reading-width rule; the redundant `width:100%`/`max-width:none` rules of `.pm-teaching-block--citation` and its `.pm-admonition`; the `65ch` cap on citation text; the `reading-width` cap of `.pm-teaching-block--text-plain`; the `68ch` and `70ch` caps of `.pm-teaching-further-reading__description` and `__item-text`.
- `20_layout.css`: one comment on the existing `.pm-teaching-block-stack > .pm-teaching-block.pm-reading` rule, which is the single place that neutralizes the global `.pm-reading` cap inside the topic layout. No new selector, no added specificity.
- Left as is on purpose: `.audio-section-description` (72ch lead inside the wide audio card, a component detail), header subtitle width, heading underline geometry (headings keep fitting their text so the accent underline does not span the column; same left edge).

## Measured (DE/EN, light/dark, 1440/820/390 px)

Editorial blocks (text paragraphs, "Auf einen Blick", info box, both maps, impulses, further reading, citation): left/width 352/736 px (desktop), 42/736 (tablet), 16/358 (mobile); inner text of further reading and citation fills the box padding (705/699 px). Audio sections 928 px (desktop), 788 (tablet), 358 (mobile). Headings start at the same left edge. No horizontal overflow in any combination. Typography, colors, spacing (48 px under the header) unchanged.

## Tests and docs

- `test_teaching_topic_layout.py`: the old "reading measure" test became `test_editorial_elements_share_the_column_width_without_a_character_measure_cap` (no ch caps on topic text/boxes, no `--pm-layout-reading-width` in any teaching or audio rule, token and `.pm-reading` still defined, audio lead and audio-section width unchanged).
- Spec: the sentence about an additional 72-character limit was replaced by the shared-outer-width rule.
