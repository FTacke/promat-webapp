# 2026-05-26 sample-page-removal

- Removed the obsolete public `sample` surface completely from the runtime: route, navigation wiring, template, translation keys, sample-only builders, sample-only CSS, and QA route lists.
- Kept the removal strict: no redirect, no compatibility alias, no placeholder page, and no legacy `sample` section entry in runtime routing.
- Updated the active governance and spec files so `sample` is no longer described as an active surface or mirror contract in `docs/spec/platform-data-files.md`, root/scoped `AGENTS.md`, repo instructions, the UI workflow runbook, and the PR checklist.
- Added a focused regression in `app/tests/test_research_sessions.py` that asserts `/{ui_lang}/sample` returns 404 and that the top navigation on `/{ui_lang}/project` no longer exposes a sample link.
- Validation:
  - `pytest app/tests/test_research_sessions.py -q -k sample_route_is_removed_and_top_navigation_omits_sample` passed (`2 passed`).
  - Full `pytest app/tests/test_research_sessions.py -q` ran and still shows 9 unrelated existing failures in team/speakers/player assertions; the new sample-removal regression passed inside that run.
  - Grep checks found no remaining `sample` references in `app/src/`, `app/templates/`, `app/static/`, `docs/spec/`, active AGENTS files, `.github/`, or `scripts/qa/`.
  - Browser validation on `http://127.0.0.1:8000/de/project` confirmed the top navigation now shows only `Projekt`, `Forschung`, and `Unterricht`.
  - Browser validation on `http://127.0.0.1:8000/de/sample` confirmed the route now renders the normal 404 page.
- `npm run lint`, `npm run typecheck`, and `npm run build` were not run because the repository has no `package.json`, so those commands do not exist in this workspace.
