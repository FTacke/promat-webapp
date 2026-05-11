# 2026-05-10 Mobile Drawer Brand and Context Systematic Pass

## Scope

- Align the mobile drawer brand with the mobile topbar brand instead of keeping a drawer-specific larger wordmark treatment.
- Replace template-local mobile context-title branching with a central panel-field derivation.
- Revalidate the requested public routes on mobile widths `320`, `390`, and `430` in `de` and `en`.

## Changes

- Added shared mobile brand tokens in `app/static/css/00_tokens.css` for font size, gap, line height, and horizontal compression, and reused them for both the topbar wordmark and the drawer wordmark.
- Increased the drawer mobile top inset token to `1.5rem`, keeping the overlay independent from `--promat-topbar-height` while restoring a moderate top offset.
- Removed drawer-only brand sizing overrides in `app/static/css/30_components.css`, including the narrow-screen enlargement that made the drawer wordmark larger than the topbar.
- Added a central `mobile_context_title` field in `app/src/app/routes/public.py` and aligned protected admin panel data with the same field in `app/src/app/protected_navigation.py`.
- Updated the mobile drawer template to render `mobile_context_title` directly instead of branching on `context_mode` inside the template.
- Added a focused regression in `app/tests/test_research_sessions.py` to assert the drawer context title across project, research root, research corpus, and teaching root routes.
- Updated the binding shell spec in `docs/spec/platform-data-files.md` to require shared mobile brand treatment, moderate safe-area top inset, and hierarchy-driven mobile context titles.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k context_title_follows_section_or_local_context`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "modal_drawer_context_title or research_design_modal_drawer_uses_primary_tabs"`
- `node .\tmp\ui-qa\mobile_drawer_systematic_check.mjs`
- QA artifact summary: `tmp/ui-qa/mobile-drawer-systematic-1778391735414/summary.json`
- QA screenshots: `tmp/ui-qa/mobile-drawer-systematic-1778391735414/`

## Notes

- The live mobile QA reported matching topbar and drawer brand font size, line height, gap, transform, and accent color on all requested routes and viewports.
- The measured drawer brand top offset was `24px` in the live checks, matching the requested moderate top spacing.
- Context titles resolved as requested: `Projekt` / `Project`, `Forschung` / `Research`, `Spanisch-Korpus` / `Spanish corpus`, and `Unterricht` / `Teaching`.
