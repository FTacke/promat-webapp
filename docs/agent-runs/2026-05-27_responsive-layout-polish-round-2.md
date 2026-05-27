# Responsive Layout Polish Round 2

## Scope

Implemented the second focused responsive/design polish pass on `main` for Landing, shared content headers, and the Teaching language selection cards.

No server runtime, database, nginx/certbot, Docker runtime, secrets, or production environment changes were made.

## Changes

| Area | Root cause | Fix |
|---|---|---|
| Landing hero top whitespace | The landing shell used a large fixed top clamp, so mobile and short desktop viewports spent too much first-screen space before the language switcher and hero. | Added landing spacing tokens and replaced the hardcoded shell padding/gap with responsive token values. Mobile now uses a compact top-oriented start with safe-area padding; desktop keeps generous but smaller spacing. |
| Back button followed by H1 | The shared header only handled direct sibling spacing. Pages with a mobile-only breadcrumb in the DOM lost the intended desktop Back/H1 gap when that breadcrumb was hidden. | The content header now emits state classes for back link, breadcrumb presence, and mobile-only breadcrumb mode. Central CSS applies the Back/H1 gap for true no-breadcrumb headers and desktop-hidden mobile breadcrumbs. |
| Teaching overview intro on mobile | The overview intro stayed visible on small screens and pushed the language cards down. | The Teaching overview intro is hidden only under the mobile breakpoint, while desktop keeps the full intro. |
| Teaching language cards on mobile | Mobile cards inherited the desktop row structure, so status/meta and CTA were not clearly separated. | Available language cards use a mobile two-column grid: title and meta stacked left, CTA right. Pending cards remain stacked and have no action slot. |
| Teaching language cards on desktop | Title, meta, and CTA used mixed row alignment and spacing values. | Desktop rows now use tokenized columns with centered title/aside/action alignment and consistent aside gaps. |

## Validation

Commands:

- `.venv\Scripts\python.exe scripts/ci_governance_checks.py` -> passed
- `node --test app/tests/js/*.test.mjs` -> 9 passed
- `git diff --check` -> passed
- `cd app; ..\.venv\Scripts\python.exe -m ruff check .` -> passed
- `cd app; ..\.venv\Scripts\python.exe -m compileall .` -> passed
- `cd app; ..\.venv\Scripts\python.exe -m pytest tests/test_research_sessions.py::test_research_language_root_renders_public_landing_with_real_page_links tests/test_research_sessions.py::test_teaching_overview_keeps_language_selection_label tests/test_research_sessions.py::test_teaching_language_root_uses_shared_topbar_and_mobile_drawer -q` -> 10 passed
- `cd app; ..\.venv\Scripts\python.exe -m pytest tests -q` -> 504 passed, 80 warnings

Typecheck:

- `cd app; ..\.venv\Scripts\python.exe -m mypy .` -> failed on existing repo configuration/stub issues before checking this change fully (`psycopg2` stubs and duplicate `app` / `src.app` module resolution).
- `cd app; ..\.venv\Scripts\python.exe -m mypy src/app --explicit-package-bases` -> failed on existing untyped dependency stubs and pre-existing type errors across app modules.

## Browser QA

Artifacts:

- `tmp/ui-qa/2026-05-27-responsive-polish-round-2/focused_results.json`
- `tmp/ui-qa/2026-05-27-responsive-polish-round-2/screenshots/`

Checked with headless Chromium on:

- `390x844`
- `1440x900`
- `1440x650`

Routes:

- `/de`
- `/de/research/spanish`
- `/de/teaching`

Results:

- No horizontal overflow on any checked route/viewport.
- Landing hero top: `104px` at `390`, `162px` at `1440`, `152px` at `1440x650`.
- Research Back/H1 gap: `54px` at `390`, `20px` at desktop widths.
- Teaching overview intro: `display: none` at `390`, `display: grid` at desktop widths.
- Teaching language list top: `237px` at `390`.
- Mobile available card: `Spanisch` and `2 Themenseiten` stacked left, `Öffnen ->` right, no pending action.
- Desktop available card title/meta/action center alignment delta: `3px`.

## Known Limits

No physical iPhone/Safari device was available. Mobile Safari was approximated through safe-area-aware CSS and Chromium viewport QA; a real-device Safari spot check remains useful before treating this as hardware-verified.
