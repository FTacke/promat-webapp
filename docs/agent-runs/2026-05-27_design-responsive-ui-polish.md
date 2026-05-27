# Design / Responsive UI Polish

## Scope

Implemented narrow central UI fixes for alert layout, Teaching mobile widths, button sizing consistency, page-header back-link spacing, Datawrapper theme synchronization, Teaching mini-player mobile layout, and mobile drawer focus behavior.

Not changed: Teaching content, editorial copy, Research data, production runtime, deployment config, icon system, Google Fonts, or broad design-system structure.

## Changes

| Area | Root cause | Fix |
|---|---|---|
| Alerts / hints | Auth and legacy MD3 alert content stacked title/text in a body container while the icon was separate, which could make the icon read as a separate row. | Central CSS now lays out alert icon and title in the first grid row and message text below for `pm-auth-message` and `md3-alert` variants. |
| Teaching mobile widths | Mobile Teaching overrides capped content/header/block grids at `18rem`/`21rem`; audio sections also used desktop `85%` width. | Mobile Teaching containers, block grids, breadcrumbs, prompts, and audio sections now use full available inline width, constrained by page padding. Desktop widths stay unchanged. |
| Buttons | Button variants used min-height without fixed block sizing, so icon/line-height differences could affect rendered height. | Shared button families now use box sizing, zero vertical padding, and explicit token-based block sizes for `pm-button`, `pm-action-button`, and `pm-nav-pill`. |
| Back link / page title | Direct back-link-to-title spacing reused the smaller breadcrumb title gap. | Added `--pm-content-header-back-title-gap` and applied it to back-link followed by H1. |
| Datawrapper on mobile Safari | CSS `color-scheme` helped in desktop/devtools, but the iframe could still follow device preference in real mobile Safari. | Datawrapper iframe URLs are now synchronized with the effective PROMAT theme through a safe `dark=false` or `dark=true` query flag, while keeping neutral wrappers and explicit light/dark backgrounds. |
| Teaching mini-player | Mobile progress range was too short to be useful in Teaching cards. | On small viewports only, Teaching mini-player hides the progress range and keeps play/pause plus time visible. Research player classes are untouched. |
| Mobile drawer focus | Drawer open logic focused the first navigation link, causing a visible first-link ring on pointer/touch open. | Drawer now focuses the mobile drawer shell; pointer focus outlines are neutralized only for drawer links with `:focus:not(:focus-visible)`, preserving keyboard focus. |

## Validation

Commands:

- `python -m compileall app` -> passed
- `node --test app/tests/js/*.test.mjs` -> 9 passed
- `.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_research_sessions.py app/tests/test_teaching_content.py -q` -> 311 passed
- `.venv\Scripts\python.exe -m pytest app/tests/test_runtime_config.py -q` -> 5 passed
- `.venv\Scripts\python.exe -m pytest app/tests -q -k "navigation or mobile or drawer or responsive or csp or security_headers or access_request or player or teaching or footer or auth"` -> 291 passed, 196 deselected
- `.venv\Scripts\ruff.exe check .` -> passed
- `mypy .` -> not run; mypy is not installed in the local virtual environment

## Browser QA

Artifacts:

- `tmp/ui-qa/2026-05-27-design-responsive-ui-polish/summary_current.json`
- `tmp/ui-qa/2026-05-27-design-responsive-ui-polish/overflow_results_current.json`
- `tmp/ui-qa/2026-05-27-design-responsive-ui-polish/screenshots-current/`

Checked public/auth/Teaching/Research signed-out routes at `360`, `390`, `768`, and `1440` where applicable. Also checked drawer open at `360` and `390`, invalid login, access-request validation, account-password signed-out redirect, and Teaching Datawrapper/audio page.

Results:

- 24 route/viewport checks
- 2 drawer checks
- 2 invalid-login alert checks
- 2 access-request validation checks
- 0 page-overflow findings
- 0 static 404s
- 0 runtime console errors
- Auth alert metrics: icon/title aligned and message text below at `360`/`390`
- Drawer focus target after open: `.promat-panel__mobile-shell`, not the first link
- Teaching topic block width: `328px` at `360`, `358px` at `390`
- Teaching mini-player mobile: progress track hidden, time visible
- Datawrapper theme sync: `dark=false` in light mode and `dark=true` after dark-mode switch at all checked viewports

## Known Limits

No physical iPhone/Safari device was available in this run. The Datawrapper fix was validated with Chromium viewport QA and by verifying the iframe URL/theme state that should address the Safari-specific device-theme mismatch.

Protected Research player/Admin visual routes were not authenticated in browser QA because no local QA credentials were configured. Existing focused Research/player/auth tests passed.
