# 2026-05-24 Admonition Unification

## Scope

- remove the remaining shared admonition toggle or collapse architecture from templates, JS, CSS, and sample data
- unify admonition headers, titles, icons, and citation actions on one token-based system
- align Teaching audio section titles to the same title standard
- update `sample` so the visible admonition family reflects the current always-visible contract

## Changes

- removed the shared admonition toggle branch from `app/templates/partials/_admonition.html`
- deleted `app/static/js/modules/core/admonitions.js` and removed its initialization from the core entry point
- stopped emitting `collapsible` and `default_open` on Teaching admonition, `audio_examples`, and `further_reading` blocks in `app/src/app/teaching_content.py`
- removed the remaining `<details>/<summary>` rendering paths for `audio_examples` and legacy `further_reading` in `app/templates/partials/_teaching_blocks.html`
- extended Sample admonitions in `app/src/app/routes/public.py` to include visible `overview` and `cite` examples and removed the former collapse flags
- added DE/EN overview labels for Sample in `app/src/app/i18n.py`
- replaced toggle-specific admonition tokens with shared title, icon, action, and audio-title tokens in `app/static/css/00_tokens.css`
- consolidated admonition header and citation geometry in `app/static/css/40_cards.css`
- removed page-local Teaching admonition/citation sizing hacks and dead `pm-teaching-details` CSS in `app/static/css/30_components.css`
- updated the active Teaching spec in `docs/spec/platform-data-files.md` to state that admonitions and `further_reading` remain fully visible

## Validation

- `python -m pytest app/tests/test_teaching_content.py -q`
- `python -m pytest app/tests/test_research_sessions.py -q -k teaching`
- `python scripts/validate_teaching_content.py`
- focused regression during the implementation:
  - `python -m pytest app/tests/test_teaching_content.py app/tests/test_research_sessions.py -q -k "sample_page_places_admonitions_before_pattern_lab_with_visible_titles or keeps_only_valid or preserves_audio_examples_and_contrast_blocks"`
  - `python -m pytest app/tests/test_research_sessions.py -q -k "which_pronunciation or sample_page_places_admonitions_before_pattern_lab_with_visible_titles or sample_page_localizes_admonitions_in_english"`

## Browser QA

- active dev listener during QA: `http://127.0.0.1:8000`
- desktop DOM checks on `/de/sample`, `/de/teaching/spanish/which-pronunciation`, and `/en/teaching/spanish/which-pronunciation`
  - `toggleCount` was `0` on all checked pages
  - DE/EN `which-pronunciation` rendered `audioTitleSize` and `admonitionTitleSize` both at `24.96px`
  - citation action width rendered at `44px` on DE and EN
- regression DOM check on `/de/teaching/spanish/final-r`
  - `toggleCount` was `0`
  - one citation admonition remained present
  - no horizontal overflow occurred
- desktop and mobile screenshots plus metrics were captured with headless Playwright because the browser screenshot tool kept timing out on unstable scroll targets
  - output folder: `tmp/ui-qa/2026-05-24-admonition-unification/`
  - captured files include:
    - `sample-admonition-stack-desktop.png`
    - `which-de-overview-desktop.png`
    - `which-de-audio-header-desktop.png`
    - `which-de-citation-desktop.png`
    - `which-en-further-reading-desktop.png`
    - `which-de-overview-mobile.png`
    - `which-de-further-reading-mobile.png`
    - `which-en-overview-mobile.png`
    - `which-en-further-reading-mobile.png`
- mobile QA used a real `390x844` viewport
  - `window.matchMedia('(max-width: 759px)')` matched on DE and EN
  - `toggleCount` stayed `0`
  - `furtherReadingColumns` resolved to a single column (`254px`)
  - no horizontal overflow occurred

## Notes

- editor diagnostics still report pre-existing warnings in shared CSS about `color-mix(...)` support and pre-existing template lint warnings unrelated to this run
- the browser page attachments in chat still pointed to stale `8010` tabs, but live QA was rerun against the active `8000` listener before closeout