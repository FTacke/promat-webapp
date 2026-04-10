# Run Log: Comparison set select no default reset

- Date: 2026-04-10
- Area: comparison
- Summary: Corrected the compact `Set wählen` control so preset selections no longer remain flagged as the implicit default draft and therefore no longer snap back to `Alle Items` after item updates.

## What changed

- Restricted the implicit-draft treatment to the real default full-item selection only.
- Kept preset-selected comparison sets as explicit active draft state so the chosen dropdown option remains visible after `PUT /items` updates.

## Verification

- `pytest app/tests/test_research_comparison.py`