# Comparison matrix player visual alignment

- Date: 2026-04-10
- Area: comparison
- Summary: Harmonized the comparison matrix visually with the research player by reusing the player control language for volume and speed, turning matrix speaker headers into compact speaker-style cards, removing the visible stop button, and calming the matrix empty-state and selected-area panel treatment.

## What changed

- Replaced the comparison matrix volume and speed controls with the same player-style range-field pattern and live value labels used in the player control bar.
- Removed the visible `Stoppen` button from the matrix toolbar so the control area stays visually closer to the player and less CTA-heavy.
- Reworked matrix speaker headers into compact card-like headers with the same badge and accent family as the speaker selector.
- Changed the matrix empty-state surface from a dashed placeholder look to a calmer informational note, and suppressed the empty container entirely when no message is present.
- Strengthened the right `Ausgewählt` column further through panel treatment and slightly more open spacing between summary, filters, and the three speaker columns.

## Verification

- `pytest app/tests/test_research_comparison.py`
- Static error check on `research_comparison.html`, `research-comparison.js`, `30_components.css`, `test_research_comparison.py`, and `research-access.md`

## Limits

- This run was intentionally visual-only. It did not change comparison data flow, set behavior, or investigate audio playback issues in the matrix.
