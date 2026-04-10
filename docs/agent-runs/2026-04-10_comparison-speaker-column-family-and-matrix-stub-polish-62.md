# Comparison speaker column family and matrix stub polish

- Date: 2026-04-10
- Area: comparison
- Summary: Unified the three-column speaker-selection surface into one calmer container family, reduced the special-case look of the selected column, and tightened the left matrix item stub so it follows the compact player item hierarchy more closely.

## What changed

- Moved all three speaker columns onto the same base container pattern with the same padding, header zone, divider logic, and general surface treatment.
- Reduced the right `Ausgewählt` column from a visually separate UI system to a subtle active variant of the same column family through a lighter tint and quieter inset treatment.
- Kept the selected speaker cards on the same base card pattern as the source cards and reduced the active-state difference to a calmer selected-state tint plus the existing remove indicator.
- Added the same neutral indicator circle shell to all speaker cards so the remove circle reads as part of the same card system instead of as a separate selected-only object.
- Tightened the matrix stub item presentation by making the item number a compact player-like pill and aligning the item text beside it in a denser, quieter layout while keeping the row play action intact.
- Reduced the sticky left matrix stub width slightly so the item column feels less coarse and more like a compact matrix adaptation of the player list.

## Verification

- Static error check on `app/static/css/30_components.css` and `app/templates/pages/research_comparison.html`
- `pytest app/tests/test_research_comparison.py`

## Limits

- This run was visual-only. It did not change selection logic, ordering, filters, audio handling, matrix behavior, or the column structure.
