# 2026-05-09 Mobile Drawer Mini-Tabbar

## Scope

- Replace the mobile drawer's vertical primary navigation list with a compact mini-tabbar.
- Keep the mobile topbar, footer, animation behavior, and existing mobile overflow fixes intact.
- Simplify the mobile drawer hierarchy to brand, top-level tabs, local context navigation, and secondary utilities.

## Changes

- Updated the mobile drawer partial so the brand is followed directly by a horizontal `Projekt / Forschung / Unterricht` tab row.
- Removed the mobile `Hauptnavigation` and `Aktueller Bereich` labels from the modal drawer and rendered the current context as a compact title line.
- Grouped lower drawer utilities into quieter `Konto` and `Darstellung` sections and changed the theme control to an icon-plus-text row instead of a floating icon button.
- Tightened the mobile drawer CSS for top padding, larger wordmark sizing, tab spacing, active-state treatment, local-nav density, and bottom utility grouping.
- Added a focused regression test that asserts the modal drawer renders the new tabbar hierarchy and grouped utilities on a real research page.
- Updated the active shell spec to define the mobile mini-tabbar and the simplified current-area block as the binding drawer contract.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k research_design_modal_drawer_uses_primary_tabs_and_grouped_utilities`
- Additional browser validation and broad mobile audit were run after the implementation on the live dev server.

## Notes

- The desktop shell and standard sidebar drawer markup remain untouched.
- Existing `color-mix(...)` compatibility warnings in `30_components.css` predate this run and were not expanded by this change.
