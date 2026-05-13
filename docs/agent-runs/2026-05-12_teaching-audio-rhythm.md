# Teaching Audio Rhythm

## Scope

- Corrected the vertical rhythm of the shared Teaching `audio-section` surfaces on the public `which-pronunciation` topic page.
- Kept assets, routing, content payloads, and grid column structure unchanged.

## Files Changed

- `app/static/css/30_components.css`

## What Changed

- Increased `audio-section` inner padding to restore calmer top and side spacing.
- Made the header the single spacing source before the card grid by setting `audio-grid` top margin to `0`.
- Converted the audio cards to stable flex columns and removed large artificial inter-zone gaps.
- Increased shared audio-card padding to `1.5rem` for the requested calmer rhythm.
- Moved the player wraps to consistent bottom alignment with explicit top padding on the player zone.
- Reduced the mini-player shell height/padding to a denser, lower player area.
- Removed the previous artificial note min-height in contrast cards.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k teaching_pilot_topic_renders_canonical_two_column_storytelling`
  - Passed.
- Browser QA on `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`
  - `audio-section` padding measured `28px 32px 28px 32px`.
  - `audio-section-header` bottom margin measured `28px`.
  - `audio-grid` top margin measured `0px`.
  - `audio-card` padding measured `24px`.
  - Player bottom offsets in the first two cards of both audio sections measured `0px` delta.
- Browser QA on `http://127.0.0.1:8000/en/teaching/spanish/which-pronunciation`
  - Same spacing metrics confirmed.

## Notes

- No spec update was needed for this run because the change only tightened the presentational rhythm inside the existing shared audio-section contract.