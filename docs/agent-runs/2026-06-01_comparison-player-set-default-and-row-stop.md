# 2026-06-01 Comparison Player Set Default and Row Stop

## Scope

- Kept the comparison workbench's internal all-items draft from becoming a visible concrete set during normal speaker and filter work.
- Added hard stop behavior for comparison matrix row playback.

## Changes

- Updated `app/static/js/pages/research-comparison.js`.
  - Tracks whether material/set selection is explicit.
  - Materializes the internal default draft with all catalog items while keeping the visible selector on the default option.
  - Adds row playback state, active row tracking, cancellation, audio reset, and cleanup on page exit.
  - Switches the active row button to the localized stop label and stop icon while the row sequence is running.
- Updated `app/static/js/modules/research/comparison-url-state.js`.
  - Keeps non-explicit all-items drafts out of `set_id` URL state.
- Updated `app/tests/js/research_ui_state_helpers.test.mjs`.
  - Regresses that normal all-items draft selection does not expose `set_id`, while explicit sets still can.

## Checks

- `node --check app/static/js/pages/research-comparison.js`
- `node --test app/tests/js/research_ui_state_helpers.test.mjs`
- Focused Python checks:
  - `.\.venv\Scripts\python.exe -m pytest app/tests/test_research_comparison.py::test_build_comparison_page_exposes_session_catalog_and_filter_state app/tests/test_research_comparison.py::test_build_comparison_page_marks_requested_set_for_client_loading app/tests/test_research_comparison.py::test_public_comparison_route_renders_dedicated_workspace app/tests/test_research_player_set_context.py::test_player_set_select_uses_saved_workbench_list_and_only_keeps_current_draft app/tests/test_research_player_set_context.py::test_player_set_select_marks_curated_preset_as_active_context`
- Broader Python check attempted:
  - `.\.venv\Scripts\python.exe -m pytest app/tests/test_research_comparison.py app/tests/test_research_player_set_context.py`
  - Result: 39 passed, 1 existing unrelated failure in `test_build_comparison_page_exposes_english_labels_for_migrated_workspace` because `research.comparison.intro` currently resolves to an empty string.
