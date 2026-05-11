# 2026-05-09 Mobile Drawer Offset, Context, and Density Refinement

## Scope

- Refine the existing mobile drawer without changing the overall shell structure.
- Remove the remaining topbar-height-based mobile drawer offset.
- Tighten the local context block, local-link rhythm, and bottom utility density.

## Changes

- Removed the remaining mobile `padding-top` override that pushed the drawer body down by `--promat-topbar-height`.
- Kept the drawer as a true overlay and switched the mobile shell top inset to a compact safe-area-aware offset using the drawer token instead of the topbar height.
- Updated the drawer brand markup so the `Pronunciation Matters` wordmark keeps a visible separation between both words while staying one line and underline-free.
- Reduced the mobile local context title from `Forschung · Spanisch-Korpus` to `Spanisch-Korpus` when the active top-level tab already provides the section context.
- Tightened the local navigation spacing, reduced excess indentation, and kept the local active page as a restrained tint state without left-rail markers.
- Compressed the lower utility groups by reducing vertical section spacing and slightly tightening the utility text rhythm while keeping 44 px touch targets.
- Updated the focused modal-drawer regression to assert the non-redundant context title and visible word separation in the drawer brand.
- Updated the binding shell spec to forbid topbar-height-derived overlay offsets for the mobile drawer and to require local-context-only titles beneath the mini-tabbar.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k research_design_modal_drawer_uses_primary_tabs_and_grouped_utilities`
- `node .\tmp\mobile_audit.mjs`
- `node .\tmp\drawer_mini_tabbar_check.mjs`
- Broad audit artifact: `tmp/mobile-audit-1778334124757/audit-results.json`
- Drawer QA artifact: `tmp/drawer-mini-tabbar-check-1778334232162/summary.json`

## Notes

- The refined drawer now opens with the brand around 16 px from the top of the overlay in the QA summary, down from the previous topbar-height-driven offset.
- The broad page audit remained overflow-clean outside the intentional admin table horizontal-scroll cases.
- Existing unrelated pytest failures outside the mobile drawer slice were not addressed in this run.
