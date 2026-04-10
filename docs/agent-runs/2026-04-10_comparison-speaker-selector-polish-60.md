# Comparison speaker selector polish

- Date: 2026-04-10
- Area: comparison
- Summary: Polished the new three-column comparison speaker selector with a cleaner remove icon, a stronger selected-area panel treatment, and slightly calmer vertical spacing between filter controls and the speaker columns.

## What changed

- Replaced the text-like `×` in the selected-state circle with a dedicated close icon so the remove action sits cleanly centered.
- Removed the weakened selected-column heading treatment and restored `Ausgewählt` to the normal heading hierarchy.
- Shifted the semantic distinction of the right selected column further into the panel surface itself through a calmer differentiated background and subtle inner panel treatment.
- Opened the vertical rhythm slightly between the filter area, result summary, and the three-column speaker lists without re-inflating the whole page.

## Verification

- `pytest app/tests/test_research_comparison.py`
- Static error check on `research_comparison.html`, `research-comparison.js`, `30_components.css`, and `test_research_comparison.py`

## Limits

- Verification remains focused on the rendered HTML contract and regression suite; this run did not add a logged-in browser interaction test for the selected-column remove icon.