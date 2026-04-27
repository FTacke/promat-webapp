# 2026-04-27 · Team Page Compact Centered Grid · Run 157

## Scope

- Corrected the visual spacing of the public team-page card layout on `/de/project/team` and `/en/project/team`.
- Kept the accepted content structure unchanged:
  - 2 lead cards with short role titles and names directly underneath,
  - 4 language-corpus cards in a 2 x 2 grid,
  - prose-only `Sprachenzentrum` / `Language Center`,
  - prose-plus-list `Dank` / `Acknowledgements`.

## Cause

- The team grids already used the correct 1-column mobile / 2-column tablet-and-up grid logic.
- The remaining visual problem came from the wrapper width, not the column count: both team grids still lived inside the normal `pm-feature-band` width, which is broader than the calmer compact block the page needs.
- Because the inner grid had no team-specific max-width, the two equal-width columns spread across too much horizontal space, which made the cards feel too far apart even though the gap token itself was already reduced.

## Implementation

- Updated `app/static/css/20_layout.css` so the team-grid variants keep their existing shared gap and 2-column breakpoint, but now also use a centered compact inner wrapper:
  - `.pm-feature-band > .pm-grid--team-lead`
  - `.pm-feature-band > .pm-grid--team-corpus`
- The new wrapper rule sets:
  - `width: min(100%, 50rem);`
  - `max-width: 50rem;`
  - `margin-inline: auto;`
- This keeps the cards as one compact, centered 2-column block without changing card styling, hierarchy, copy, or the accepted card order.
- Updated `app/tests/test_research_sessions.py` so the focused team-grid regression now asserts the centered team-wrapper rule in the delivered shared layout CSS.
- Updated `docs/spec/platform-data-files.md` so the active team-page rule now states that the card grids stay inside a narrower centered max-width instead of spreading across the full feature width.

## Validation

- Focused team-page regression slice:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "team_page_uses_structured_credits_cards_without_legacy_text or team_page_uses_shared_two_column_team_grid_rules"`
- Full research-session suite:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- Live route/browser validation opened:
  - `http://127.0.0.1:8000/de/project/team`
  - `http://127.0.0.1:8000/en/project/team`
  - `http://127.0.0.1:8000/de/sample`
- Live HTML/CSS checks on the running dev server confirm:
  - both team grids still render 2 columns from tablet upward and 1 column below,
  - both team grids now ship the centered `50rem` max-width wrapper,
  - the six cards remain in the accepted 2 + 4 order,
  - the prose sections remain prose-only,
  - the shared sample route still loads after the shared layout CSS change.

## Notes

- This was a cleanup of layout containment only, not a redesign: no colors, card chrome, typography hierarchy, or CTA semantics were changed.
- Screenshot capture is still unavailable from this environment, so browser validation is documented through real-route browser opening plus live HTML/CSS checks against the running listener.
