# 2026-05-24 Admonition Typography Final Consolidation

## Scope

- consolidate the shared admonition typography so `overview`, citation, tip/info/summary, sample admonitions, and the teaching `further_reading` header all use the same title and icon scale
- remove the remaining `overview` hero-card exceptions that made it louder than the rest of the shared admonition family
- keep admonition bodies on sans-serif UI typography instead of drifting back to the reading serif family

## Changes

- updated `app/static/css/00_tokens.css`
  - follow-up correction: changed `--pm-admonition-title-size` from the previous responsive clamp to the new central type-scale token `--pm-type-ui-title-size`
  - added `--pm-type-ui-title-size: 1.5rem` so the shared admonition family lands at an exact `24px` title size at the standard root size
  - follow-up correction: changed `--pm-admonition-title-line-height` from `1.18` to `1` because the DevTools overlay height was tracking the element line box, not the font size itself
  - changed `--pm-admonition-body-font` from the reading family to the shared UI family
  - added optional shared admonition header-divider tokens:
    - `--pm-admonition-header-divider-width`
    - `--pm-admonition-header-divider-color`
    - `--pm-admonition-header-divider-space-after`
    - `--pm-admonition-header-divider-space-before`
  - simplified the overview token family to the calm surface-focused values that remain in use:
    - `--pm-overview-bg`
    - `--pm-overview-accent`
    - `--pm-overview-title-color`
    - `--pm-overview-body-color`
    - `--pm-overview-divider-color`
    - `--pm-overview-bullet-color`
  - removed the overview-only hero tokens that existed only for the louder special treatment:
    - `--pm-overview-bg-gradient`
    - `--pm-overview-icon-badge-bg`
    - `--pm-overview-icon-badge-color`
    - `--pm-overview-icon-badge-size`
    - `--pm-overview-icon-size`
    - `--pm-overview-radius`
    - `--pm-overview-shadow`
    - `--pm-overview-divider-width`
    - `--pm-overview-header-gap`
    - `--pm-overview-header-padding-end`
    - `--pm-overview-header-padding-bottom`
    - `--pm-overview-body-gap`
    - `--pm-overview-body-size`
    - `--pm-overview-body-line-height`
    - `--pm-overview-decoration-size`
    - `--pm-overview-decoration-color`
  - added `--pm-teaching-further-reading-divider-color`
- updated `app/static/css/40_cards.css`
  - the shared admonition header now supports an optional token-based divider, but it is off by default
  - `overview` now uses the shared admonition title token and shared 24px icon token again
  - `overview` keeps its differentiated surface through tint and borderless area treatment, not through oversized typography or decorative chrome
  - removed the `overview` hero exceptions:
    - larger title scale override
    - larger icon box and glyph override
    - shadow/glow styling
    - right-side decorative pseudo-element
    - custom badge background treatment
- updated `app/static/css/30_components.css`
  - removed the last overview shadow override and kept the body/list treatment calm and token-based
  - aligned `further_reading` to the shared admonition title token, shared 24px icon size, and shared header gap
  - added a subtle divider under `further_reading` using the new tokenized divider color

## Divider Decision

- I tested the divider concept as a shared optional pattern instead of forcing it globally.
- The divider support now exists in the shared admonition header tokens, but it is only enabled for `overview`.
- `further_reading` uses the same visual idea through its own header rule so it aligns with the shared admonition rhythm.
- Citation, tip, info, and summary were intentionally left without the divider because they read cleaner and lighter without an extra line.

## Validation

- `python -m pytest app/tests/test_research_sessions.py -q -k "sample_page_localizes_admonitions_in_english or sample_page_places_admonitions_before_pattern_lab_with_visible_titles or teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_topic_renders_public_content_blocks"`

## Browser QA

- live QA used `http://127.0.0.1:8000`
- checked pages
  - `/de/sample`
  - `/en/sample`
  - `/de/teaching/spanish/which-pronunciation`
  - `/en/teaching/spanish/which-pronunciation`
  - `/de/teaching/spanish/final-r`
- computed desktop checks
  - initial consolidation pass rendered `--pm-admonition-title-size` at `24.96px`
  - follow-up correction changed the resolved value to `24px`
  - `overview`, citation, tip, summary, cite, and `further_reading` header titles now render at `24px`
  - the actual title element box height also now renders at `24px`; previously the old `1.18` line-height produced a `28.3125px` box height despite the correct `24px` font size
  - all checked admonition icons rendered at `24px × 24px`
  - `overview` no longer rendered a box shadow and no longer exposed a right-side decoration pseudo-element
  - `overview` kept a subtle divider under the header, while citation/tip/summary stayed divider-free
- computed mobile checks at `390px`
  - the earlier responsive clamp no longer applies after the correction to the fixed `1.5rem` token
  - all checked icons still rendered at `24px × 24px`
  - no horizontal overflow occurred on the checked teaching pages
- toggle/collapse verification
  - no admonition toggle or collapse controls were present
  - the only `aria-expanded` element found during broad page scans was the shared topbar menu button

## QA Artifacts

- screenshots saved under `tmp/ui-qa/2026-05-24-admonition-typography-final/`
  - `sample-de-admonition-stack-desktop.png`
  - `sample-en-admonition-stack-desktop.png`
  - `which-de-overview-desktop.png`
  - `which-de-further-reading-desktop.png`
  - `which-en-overview-desktop.png`
  - `which-en-further-reading-desktop.png`
  - `final-r-de-citation-desktop.png`
  - `final-r-de-tip-desktop.png`
  - `which-de-overview-mobile.png`
  - `which-de-further-reading-mobile.png`
  - `which-en-overview-mobile.png`
  - `which-en-further-reading-mobile.png`
  - `final-r-de-citation-mobile.png`

## Notes

- `further_reading` is not currently represented on the sample page, so its final state was validated on the productive DE and EN `which-pronunciation` routes instead.