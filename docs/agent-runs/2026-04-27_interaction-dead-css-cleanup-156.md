# 2026-04-27 · Interaction Dead CSS Cleanup · Run 156

## Scope

- Performed a dead-CSS deletion pass for the retired interaction classes `pm-research-button` and `pm-research-inline-action`.
- Verified first that productive templates and productive runtime JS no longer use those classes.
- Removed only shared CSS compatibility selectors that still targeted the retired classes.
- Kept the active semantic control families unchanged: `pm-action-button`, `pm-nav-pill`, `pm-cta-link`, `pm-material-choice`, `pm-player-control-button`, filter chips, tabs, overflow actions, and player-specific controls.

## Repo Grep Before Deletion

Full repo grep for both retired class names showed:

- no productive matches in `app/templates/`
- no productive matches in `app/static/js/`
- no productive matches in `app/src/`
- remaining live code matches only in `app/static/css/30_components.css`
- additional exact-string matches only in historical docs and a few negative-assertion tests

## CSS Removed

Removed the retired compatibility selectors from `app/static/css/30_components.css` in these areas:

- shared inline-flex base grouping for chip/link/button-like controls
- shared bordered paper-surface grouping and matching hover grouping
- retired task-action selector variants `pm-research-inline-action--task`
- retired generic button selectors `pm-research-button` and `pm-research-button--subtle`
- retired inline-action selectors `pm-research-inline-action`, `pm-research-inline-action--compact`, and `pm-research-inline-action--secondary`
- retired table/admin/player compatibility selectors that still targeted the old classes

The cleanup preserved all active selectors and did not change values for active control families.

## Test Adjustments

- Removed exact retired-class negative assertions from `app/tests/test_research_sessions.py` and `app/tests/test_auth_phase1.py` because they would otherwise keep the dead class names alive in repo grep.
- Kept the productive behavior checks that assert the active semantic classes are present in the shipped HTML and JS.

## Validation

- `pytest app/tests/test_research_sessions.py -q` → `178 passed`
- `pytest app/tests/test_auth_phase1.py -q` → `24 passed`
- repo grep for `pm-research-button` after cleanup: historical docs only
- repo grep for `pm-research-inline-action` after cleanup: historical docs only
- direct grep on `app/static/css/30_components.css` after cleanup: no remaining matches for either retired class family

## Remaining References After Cleanup

Only historical documentation still contains the retired names, including earlier run logs and the legacy audit itself. No productive template, productive runtime-JS, active shared CSS selector, or test file still contains exact matches for the retired class names.

## Result

The dead-CSS cleanup is complete for the current repo state:

- productive templates do not use `pm-research-button` or `pm-research-inline-action`
- productive runtime JS does not use `pm-research-button` or `pm-research-inline-action`
- active CSS selectors for both retired class families have been removed
- active semantic interaction families remain unchanged
