# Comparison speaker selector to three-column structure

- Date: 2026-04-10
- Area: comparison
- Summary: Reworked the comparison speaker selector from a two-column mixed list into a three-column structure with separate learner and native source lists plus a semantically distinct selected area.

## What changed

- Replaced the previous `Verfügbar` / `Ausgewählt` structure with `Lernende`, `Native Speaker`, and `Ausgewählt`.
- Removed native speakers from the mixed source list and rendered them only in the dedicated middle column.
- Removed the visible `Native` filter chip and kept the level chips at `A1`, `A2`, `B1`, and `B2`.
- Tightened the speaker rows slightly so the three-column desktop layout stays dense and calm without returning to bulky cards.
- Styled the right selected column as a quieter composition area rather than a third identical source list.
- Replaced the selected-state checkmark with a real remove action in the circle and kept selected ordering as learners first, native speakers second.

## Verification

- `pytest app/tests/test_research_comparison.py`
- Static error check on `research_comparison.html`, `research-comparison.js`, and `30_components.css`

## Limits

- The focused regression suite verifies the server-rendered comparison structure and preserved contracts, but it does not simulate a logged-in browser click flow through all three columns.