# Run Log: Comparison set dropdown in-place material update

- Date: 2026-04-10
- Area: comparison
- Summary: Corrected the compact `Set wählen` dropdown so defined example presets update the active comparison draft in place instead of creating a fresh draft set on each selection.

## What changed

- Extended the comparison preset payload to include concrete item references for each example set.
- Rewired the comparison client so a set selection updates the current draft via `PUT /items` and only patches metadata when the visible comparison task must change.
- Kept the compact step-1 UI intact and aligned the active spec with the corrected dropdown behavior.

## Verification

- `pytest app/tests/test_research_comparison.py`