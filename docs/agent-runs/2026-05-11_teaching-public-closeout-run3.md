# Teaching Public Closeout Run 3

## Goal

Close the public Teaching rawbau after Run 1 and Run 2 with a narrow focus on the last known mobile topbar bug, one real public Teaching asset probe, final QA/regression, and a final spec/governance consistency check.

## Changed Files

- `content/teaching/spanish/de/topics/final-r.yaml`
- `content/teaching/spanish/en/topics/final-r.yaml`
- `public/teaching/spanish/downloads/asset-smoke.txt`
- `app/tests/test_research_sessions.py`

## What Changed

### Mobile topbar bug

- No additional app CSS change was needed in Run 3.
- The remaining Run-2 clipping report was re-checked with exact browser-engine DOM inspection instead of the earlier coarse `--window-size` screenshot approach.
- A CDP-based 390 px viewport inspection showed the current Teaching topbar already reflows correctly on real `390px` CSS width:
  - `document.documentElement.clientWidth = 390`
  - `scrollWidth = 390`
  - the Teaching topbar primary row resolves to a single-column grid on `page-teaching`
  - the `DE | EN` switch sits on its own visible row and is not clipped
- The earlier clipped screenshots were caused by an inexact headless capture setup that did not represent a true `390px` CSS viewport.

### Real public asset probe

- Added one committed public smoke asset:
  - `public/teaching/spanish/downloads/asset-smoke.txt`
- Rewired the existing German and English `final-r` download blocks to that real file.
- Updated the Teaching route regression so the rendered topic page now asserts the live `/teaching/spanish/downloads/asset-smoke.txt` link instead of the old placeholder filename.

## Screenshot / Browser Smoke At 390 px

Exact `390px` viewport screenshots were captured via Edge DevTools emulation for:

- `/de/teaching`
- `/de/teaching/spanish`
- `/de/teaching/spanish/final-r`
- `/en/teaching/spanish/final-r`
- `/de/project/about`

Result:

- Teaching pages remain drawer-free.
- The topbar wordmark remains readable.
- The global `DE | EN` switch is fully visible and reachable on Teaching at exact `390px` CSS width.
- No horizontal overflow remained in the exact-viewport DOM measurements (`scrollWidth == clientWidth == 390`).
- The public project regression remained visually stable on the same narrow-width pass.

## Asset Route Result

Live HTTP checks on the refreshed server state:

- `/teaching/spanish/downloads/asset-smoke.txt` -> `200 OK`
- `/teaching/../secure/secret.txt` -> `404 NOT FOUND`
- `/de/research/spanish/comparison` -> `302 FOUND` to `/login?next=/de/research/spanish/comparison`

Live HTML checks on the served topic pages confirmed:

- German `final-r` page renders `Arbeitsblatt herunterladen` linking to `/teaching/spanish/downloads/asset-smoke.txt`
- English `final-r` page renders `Download worksheet` linking to `/teaching/spanish/downloads/asset-smoke.txt`

## Tests / Checks

- `get_errors` on changed repo files -> no errors
- `pytest app/tests/test_teaching_content.py -q` -> `7 passed`
- `pytest app/tests/test_research_sessions.py -q -k teaching` -> `10 passed, 183 deselected`
- `pytest app/tests/test_analytics.py -q` -> `3 passed`

Coverage already present or confirmed in the final run includes:

- `/de/teaching`
- `/de/teaching/spanish`
- `/de/teaching/spanish/final-r`
- `/en/teaching/spanish`
- `/en/teaching/spanish/final-r`
- missing topic redirect
- missing target edition redirect to hub
- Teaching language switch on hub and topic routes
- `next_topics` filtering without broken links
- empty credits suppressed
- unknown block types ignored without crash
- public Teaching asset route
- asset traversal rejection
- Research remains protected

## Spec / Governance Check

- Re-read `docs/spec/platform-data-files.md`, `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`, and `.github/instructions/repo.instructions.md`.
- The active rules are now already consistent for the in-scope Teaching contract:
  - Teaching is fully public
  - Teaching is separate from Research
  - no Research auth on Teaching
  - no Research player on Teaching
  - Teaching content under `content/teaching`
  - Teaching media under `public/teaching`
  - public Teaching assets served only from `public/teaching`
  - `ui_lang` and `teaching_lang` remain separate axes
  - editions are not forced 1:1 translations
  - Teaching language switch stays context-sensitive
  - extra Teaching-only UI languages stay local to Teaching
  - no admin editor for Teaching content
- Run 3 did not need further spec or governance edits.

## Production / Build Sanity

- Run 3 did not change Docker files, runtime-path code, or path architecture.
- Therefore no full Docker rebuild was repeated here.
- Run 2 remains the authoritative production sanity pass for:
  - `docker compose -f app/infra/docker-compose.prod.yml config`
  - image build from `app/Dockerfile`
  - container verification of `content/teaching`
  - container verification of Teaching content-root resolution

## Open Points

- No blocking open point remains for the public Teaching rawbau scope defined across Run 1 to Run 3.
- Future work, if any, is content/editorial expansion or later visual polish, not architecture completion.

## Recommendation

The public Teaching rawbau can now be treated as complete for the current scope.

Reasons:

- the last known mobile topbar issue is closed by exact 390 px browser-engine validation
- Teaching remains drawer-free and public
- the public asset route is now proven with one real committed asset
- traversal and Research-access regressions stay clean
- focused Teaching and analytics regressions are green
- no new architecture or design-system phase was introduced