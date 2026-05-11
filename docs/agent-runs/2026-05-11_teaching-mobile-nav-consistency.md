# Teaching Mobile Navigation Consistency

## Goal

Restore full shared mobile navigation consistency for public Teaching so Teaching uses the same global topbar and the same mobile app drawer as Projekt, Forschung, and Sample, while still keeping Teaching pages free of a permanent desktop content sidebar.

## Cause Of The Inconsistency

The mismatch came from two separate Teaching-specific deviations in the shared shell path:

- In `app/src/app/routes/public.py`, `layout == "teaching"` set `render_navigation_drawer = False` and `app-shell--panel-hidden`, which removed the shared drawer include completely. That suppressed both the mobile drawer dialog and the burger button, not only the permanent desktop panel.
- In `app/static/css/30_components.css`, multiple `page-teaching` overrides rewired the shared mobile topbar grid and brand layout. Those overrides removed the normal burger/wordmark column logic and stacked the Teaching header differently from the rest of the app.

Together, those two choices misinterpreted `drawer-free` as `no shared drawer at all` instead of the correct rule `no permanent left content/sidebar navigation on desktop`.

## Changed Files

- `app/src/app/routes/public.py`
- `app/static/css/layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`
- `docs/agent-runs/2026-05-11_teaching-mobile-nav-consistency.md`

## What Changed

### Shared topbar and drawer path restored

- Teaching no longer disables `render_navigation_drawer` in `_render_promat_page(...)`.
- Teaching no longer uses `app-shell--panel-hidden` for its shared inner shell.
- As a result, Teaching now renders the same shared burger button and the same shared drawer markup as the other inner app areas.

### Permanent desktop sidebar still suppressed for Teaching

- Added a desktop-only layout rule in `app/static/css/layout.css` for `body.app-shell.page-teaching`.
- On desktop widths, `#navigation-drawer` is hidden for Teaching and the content wrapper collapses to the single main-content column.
- This keeps the correct Teaching rule: no permanent left content/sidebar navigation on hub and topic pages.

### Teaching-specific topbar divergence removed

- Removed the `page-teaching` topbar overrides from `app/static/css/30_components.css` that changed:
  - mobile brand grid columns
  - brand gap/scale behavior
  - small-width topbar row stacking
  - Teaching-only language-switch compression
- Teaching now falls back to the same shared mobile topbar rules as Projekt, Forschung, and Sample.

### Focused route expectations updated

- Updated the Teaching shell regression in `app/tests/test_research_sessions.py`.
- Correct expectation now is:
  - Teaching uses the shared topbar and mobile drawer
  - Teaching does not use `app-shell--panel-hidden`
  - Teaching still does not render a redundant mobile context block for empty local drawer nav

## How The Shared Global Navigation Was Preserved

- The same `_top_app_bar.html` path is used unchanged for Teaching.
- The same `_navigation_drawer.html` path is used unchanged for Teaching.
- The same shared mobile topbar layout rules now apply to Teaching again.
- The same drawer controller logic and the same top-level drawer tabs (`Projekt`, `Forschung`, `Unterricht`) now apply on Teaching.

## How Teaching Still Avoids A Permanent Left Content Sidebar

- The Teaching routes still render with `body_class = "page-teaching"`.
- Desktop-only CSS hides the standard drawer column for `page-teaching` and centers the main column layout.
- This keeps Teaching hub/topic pages free of the permanent left shell panel while allowing the shared mobile drawer to exist normally on compact widths.

## Screenshot / Browser Smoke

Exact `390px` browser-engine inspection and screenshots were run for:

- `/de/project/about`
- `/de/research/spanish/design`
- `/de/teaching`
- `/de/teaching/spanish`
- `/de/teaching/spanish/final-r`
- `/en/teaching/spanish/final-r`

### Measured shell parity at 390 px

For all six routes, the exact DOM metrics matched on the shared shell slice:

- `innerWidth = 390`
- `clientWidth = 390`
- `scrollWidth = 390`
- `bodyScrollWidth = 390`
- burger present: `hasMenu = true`
- topbar grid: `306.938px 61.0156px`
- burger rect: `44 x 44`
- visible language switch width: `61.015625`
- no horizontal overflow

For Teaching routes specifically:

- `standardDrawerDisplay = none` at the mobile viewport, matching the shared compact-shell behavior
- the topbar geometry matches Projekt and Forschung exactly
- the wordmark remains on one line beside the burger
- the language switch stays on the same visible row as on the other app areas

### Teaching drawer interaction smoke

On `/de/teaching/spanish/final-r`:

- burger click opened the shared drawer successfully: `open = true`
- active top-level drawer tab was `Unterricht`
- drawer top tabs were `Projekt`, `Forschung`, `Unterricht`
- utility entries remained `Login` and `Hell / Dunkel`
- closing the drawer worked: `openAfterClose = false`
- no redundant local mobile context title was rendered for Teaching: `contextTitles = []`

### Visual result

- Projekt, Forschung, and Teaching now show the same mobile topbar structure: burger left, one-line wordmark center-left, compact language switch right.
- Teaching no longer renders the old special stacked header with wordmark and language switch on separate rows.
- Teaching root, hub, and topic screenshots remain clean and overflow-free.

## Tests / Checks

- `get_errors` on changed code files -> no relevant new errors
- `pytest app/tests/test_research_sessions.py -q -k teaching` -> `10 passed, 183 deselected`
- `pytest app/tests/test_teaching_content.py -q` -> `7 passed`
- exact 390 px browser-engine mobile smoke completed on the six in-scope routes

## Spec / Governance Alignment

- No active spec change was required.
- The implementation was corrected to match the existing platform rule in `docs/spec/platform-data-files.md`:
  - Teaching keeps the shared topbar
  - shared mobile topbar stays burger + one-line wordmark + `DE | EN`
  - Teaching does not use the permanent left sidebar navigation
  - mobile drawer remains the shared global drawer, not a Teaching-specific variant

## Open Points

- No blocking open point remains in the navigation-consistency slice.
- The earlier Run-3 conclusion that Teaching was simply `drawer-free` needs to be read with the corrected meaning: no permanent desktop content/sidebar panel, but shared mobile global drawer still present.