# 2026-04-27 · Button-System Phase 1 Preview · Run 142

## Scope

- Introduced a preview-only, token-based `pm-button` family for future shared-button migration.
- Kept all existing productive button families untouched.
- Added a temporary button-system preview zone at the top of `/{ui_lang}/sample`.
- Added focused sample-page tests and aligned the active platform spec with the preview-only rollout rule.

## Implementation

- Added button tokens in `app/static/css/00_tokens.css` for size, spacing, color, focus, disabled, and grouping behavior.
- Added namespaced `pm-button` styles and group helpers in `app/static/css/30_components.css`.
- Added a central Jinja macro in `app/templates/partials/_pm_button.html`.
- Wired localized sample preview data in `app/src/app/routes/public.py` and rendered it in `app/templates/pages/sample_page.html`.
- Added DE/EN translation keys for the preview section in `app/src/app/i18n.py`.
- Added focused sample-page regressions in `app/tests/test_research_sessions.py`.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "button_system_preview or sample_page_exposes_button_system_preview_without_global_button_migration or sample_page_localizes_button_system_preview_in_english"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "sample_page"`
- Started the canonical dev server with `./scripts/dev-start.ps1`.
- Opened `http://127.0.0.1:8000/de/sample` and `http://127.0.0.1:8000/en/sample` in the integrated browser.
- Fetched the live HTML for both routes and verified the new preview section plus localized preview labels.

## Notes

- No headless browser binary was available on this host, so screenshot generation could not be automated in this run.
- The new preview section is localized in DE/EN. Outside that preview zone, the existing sample page still contains older mixed-language content that predates this run.