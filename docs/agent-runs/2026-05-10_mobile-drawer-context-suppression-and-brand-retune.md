# 2026-05-10 Mobile Drawer Context Suppression and Brand Retune

## Scope

- Suppress redundant root-level mobile context titles below the existing mini-tabbar.
- Retune the shared mobile topbar and drawer wordmark so the brand reads as primary branding again without reintroducing drawer-only sizing.
- Revalidate the requested project, research root, research corpus, and teaching root routes on `320`, `390`, and `430` in `de` and `en`.

## Changes

- Extended the shared panel model in `app/src/app/routes/public.py` with `active_primary_label` and `show_mobile_context_title` so mobile context-title visibility is derived centrally rather than through template-local comparisons.
- Aligned the protected admin panel payload in `app/src/app/protected_navigation.py` with the same mobile panel fields.
- Updated `app/templates/partials/_navigation_drawer.html` so the mobile context title only renders when `show_mobile_context_title` is true.
- Retuned the shared mobile brand tokens in `app/static/css/00_tokens.css` to a visibly larger range, with the narrowest breakpoint still holding a one-line brand at `320` px.
- Removed the remaining topbar-only narrow-breakpoint brand downsizing in `app/static/css/30_components.css` so both topbar and drawer stay on the same shared mobile brand tokens.
- Made the mobile topbar and drawer wordmark spans inherit the same mobile font metrics and aligned their markup to the same two-span structure so font size, line height, gap, transform, and accent treatment match in computed output.
- Restored the mobile wordmark weight to the desktop brand weight and increased the vertical air between the wordmark, mini-tabbar, and current-area block so the drawer no longer feels compressed after the redundant root-title removal.
- Aligned the mobile mini-tabbar active marker with the desktop topbar navigation underline rhythm by reusing the desktop offset token and hanging the active indicator just below the label instead of leaving a looser bottom gap.
- Updated the focused drawer regression in `app/tests/test_research_sessions.py` so root-level project, research, and teaching pages assert no redundant mobile context title while corpus pages still assert the specific corpus title.
- Tightened the focused Edge QA script in `tmp/ui-qa/mobile_drawer_systematic_check.mjs` to check context-title suppression, brand prominence, single-line behavior, compact local-nav spacing, and horizontal overflow safety.
- Updated the binding shell rule in `docs/spec/platform-data-files.md` to suppress repeated main-area labels below the mini-tabbar and to keep the shared mobile wordmark visibly primary at `320` px.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "modal_drawer_context_title_only_renders_for_specific_local_context or research_design_modal_drawer_uses_primary_tabs_and_grouped_utilities"`
- `node .\tmp\ui-qa\mobile_drawer_systematic_check.mjs`
- `node .\tmp\ui-qa\mobile_drawer_systematic_check.mjs` after the final brand-weight and spacing adjustment
- QA artifact summary: `tmp/ui-qa/mobile-drawer-systematic-1778397438961/summary.json`
- QA screenshots: `tmp/ui-qa/mobile-drawer-systematic-1778397438961/`

## Notes

- The live QA showed no repeated `Projekt` / `Forschung` / `Unterricht` context titles below the mini-tabbar on the root pages, while `Spanisch-Korpus` / `Spanish corpus` remained visible on the corpus page.
- The live QA reported matching computed topbar and drawer brand font size, line height, gap, transform, and accent color across all requested routes and viewports.
- The live QA also reported matching brand font weight across topbar and drawer, with the brand staying one-line and visibly prominent on `320` px.
- The measured drawer brand top offset remained `24px`, the brand stayed single-line, and the focused QA reported no horizontal overflow regressions.
- The mobile mini-tabbar active indicator now follows the desktop underline rhythm instead of using a looser drawer-only bottom gap.
