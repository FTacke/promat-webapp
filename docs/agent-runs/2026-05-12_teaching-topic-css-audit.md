# Teaching Topic CSS Audit

## Scope

- Ran a systematic CSS/template audit for Teaching topic pages with focus on the shared audio-section migration and remaining legacy cascade overlap.
- Kept content, routing, public assets, and topic-grid structure unchanged.

## Files Changed

- `app/static/css/00_tokens.css`
- `app/templates/partials/_teaching_blocks.html`
- `app/static/css/30_components.css`
- `app/static/css/20_layout.css`
- `app/tests/test_research_sessions.py`

## Removed Legacy Classes And Paths

- Removed the unused legacy `render_audio_example(...)` macro and its old `pm-teaching-audio-card*` surface family.
- Removed legacy shared-layer classes from the audio-section header markup:
  - `pm-teaching-audio-examples__header`
  - `pm-teaching-audio-examples__title-row`
  - `pm-teaching-audio-examples__lead`
  - `pm-teaching-audio-examples__icon`
  - `pm-teaching-audio-contrast__header`
  - `pm-teaching-audio-contrast__title-row`
  - `pm-teaching-audio-contrast__title`
  - `pm-teaching-audio-contrast__icon`
- Removed the unused layout leftover `.pm-teaching-audio-grid` from `20_layout.css`.

## Kept Specific Classes Intentionally

- Kept `pm-teaching-audio-example__*` only for inner example-card structure such as label, quote text, token, note, and player wrap.
- Kept `pm-teaching-audio-contrast__*` only for contrast-specific internals such as transcript row, transcript pill, example subtitle, note, and player wrap.
- Kept `pm-teaching-mini-player__*` for the interactive player internals while moving the shell contract to the shared `audio-player-shell` class.

## Shared Rules Consolidated

- Shared audio-section container, header, title, icon, description, grid, card, player-wrap, player-shell, quote, source line, note rhythm, and token placement now resolve through the shared `audio-*` classes.
- Introduced clean shared modifiers where variant behavior is real:
  - `audio-section--examples`
  - `audio-section--contrast`
  - `audio-grid--examples`
  - `audio-grid--contrast`
- Moved the player shell contract to the shared `audio-player-shell` instead of leaving it anchored in the legacy outer player class.
- Removed broad legacy page-scope overrides that were still targeting shared audio-section header/lead/title elements.

## Token Audit Follow-Up

- Located the active token system in `app/static/css/00_tokens.css`, including existing color, border, surface, radius, and spacing variables plus light/dark theme roots.
- Reused exact existing tokens where the rendered values already matched the current audio-section UI:
  - `--book-muted`
  - `--book-fg`
  - `--book-shadow`
  - `--pm-space-sm`
  - `--pm-space-container`
- Added new semantic teaching-audio tokens only where no exact existing token preserved the live values without visual drift:
  - `--pm-teaching-audio-surface: #fff`
  - `--pm-teaching-audio-card-surface: #fcfcfc`
  - `--pm-teaching-audio-section-border: #e5e5e5`
  - `--pm-teaching-audio-card-border: #e8e8e8`
  - `--pm-teaching-audio-quote-border: #e6e6e6`
  - `--pm-teaching-audio-section-accent: #c7d7e8`
  - `--pm-teaching-audio-icon-color: #2f5f8f`
  - `--pm-teaching-audio-token-color: #777`
  - `--pm-teaching-audio-subtitle-color: #666`
  - `--pm-teaching-audio-section-radius: 12px`
  - `--pm-teaching-audio-card-radius: 10px`
- Switched the shared audio-section component rules in `30_components.css` from local hardcoded color values to those central tokens.
- Removed the remaining audio-token color cascade conflict so the shared `.audio-token` class, not the legacy internal example token class, controls the rendered token color.
- Deliberately did not tokenize non-repeated local values like `gap: 0.65rem`, `padding: 1.25rem 1.25rem 2rem`, `bottom: 0.65rem`, and `transform: translateY(1px)` because the project token system does not currently model those as shared design tokens and introducing one-off tokens there would add maintenance noise without improving consistency.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k teaching_pilot_topic_renders_canonical_two_column_storytelling`
  - Passed.
- Browser QA with screenshots and JSON reports under `tmp/ui-qa/2026-05-12-teaching-audio-audit/`
  - Audited `de` and `en` topic pages on desktop and mobile.
  - Root token values resolved in the browser to the expected unchanged audio values.
  - Shared audio-section icons measured `20px` size with the same blue color in examples and contrast.
  - Shared descriptions measured `16px` font size and `23.2px` line height.
  - `audio-section-header` margin-bottom measured `24px`; `audio-grid` margin-top measured `0px`.
  - Examples grid measured two columns on desktop and one column on mobile.
  - `audio-example-note` and `audio-quote` each measured `16px` top margin.
  - Audio token remained letter-true with `text-transform: none`, `letter-spacing: normal`, and restored computed token color `#777`.
  - Shared section, card, and quote surfaces and borders still computed to the same pre-tokenized values: `#fff`, `#fcfcfc`, `#e5e5e5`, `#e8e8e8`, `#e6e6e6`, `#c7d7e8`, `#2f5f8f`, and `#666` where expected.
  - No literal backticks or `**` were visible inside `.audio-section`.
  - No removed legacy header/title/icon classes remained on shared audio-section elements.
  - No new hardcoded hex colors remained in the audio-section slice of `30_components.css`.

## Remaining Technical Debt

- Existing repo-wide lint warnings remain for older inline iframe styles and HTML structure warnings in unrelated teaching template areas.
- Existing `color-mix(...)` compatibility warnings in shared CSS remain unchanged and were not part of this audit.
- The legacy negative assertion for `pm-teaching-audio-card` remains in the focused test as a regression guard against reintroducing the retired markup family.

## Notes

- No spec update was needed because this run cleaned internal component hierarchy and removed legacy overlap without changing the accepted public Teaching contract.