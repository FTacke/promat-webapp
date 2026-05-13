# Teaching Audio Section Migration Cleanup

## Scope

- Cleaned the shared Teaching audio-section migration so common description, spacing, and player layout no longer inherit legacy contrast-only styling.
- Kept content, routing, assets, and grid column structure unchanged.

## Files Changed

- `app/templates/partials/_teaching_blocks.html`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`

## What Changed

- Removed the legacy `pm-teaching-audio-contrast__lead` class from the shared contrast description paragraph so the outer audio-section description only resolves through `audio-section-description`.
- Added neutral shared hooks for the migrated system: `audio-example-card` on example cards and `audio-player-wrap` on both example and contrast player wrappers.
- Reduced the legacy contrast CSS so it no longer overrides the shared audio-section typography and spacing.
- Moved the shared description contract to:
  - `margin: 0.45rem 0 0`
  - `max-width: 72ch`
  - `font-size: 1rem`
  - `line-height: 1.45`
  - `color: var(--book-muted)`
- Set the shared header/grid spacing contract to:
  - `audio-section-header { margin-bottom: 1.5rem; }`
  - `audio-grid { margin-top: 0; }`
- Kept contrast-specific classes only for internal contrast layout such as the transcript pill, example gap, and note spacing.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k teaching_pilot_topic_renders_canonical_two_column_storytelling`
  - Passed.
- Live DOM QA on `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`
  - Contrast descriptions no longer had class `pm-teaching-audio-contrast__lead`.
  - Description computed styles measured `font-size: 16px`, `line-height: 23.2px`, `margin-top: 7.2px`, `color: rgb(90, 88, 85)`.
  - `audio-section-header` computed `margin-bottom` measured `24px`.
  - `audio-grid` computed `margin-top` measured `0px`.
  - All 8 example/contrast player wrappers carried `audio-player-wrap`.

## Notes

- No spec update was needed because this run removed migration overlap inside the existing shared audio-section contract rather than changing the contract itself.