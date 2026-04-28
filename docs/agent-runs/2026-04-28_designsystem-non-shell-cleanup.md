# Designsystem Non-Shell Cleanup

## Scope

- Step 3a only: reduce non-shell design-system debt after the shell recovery without reopening any shared-shell migration
- limit productive edits to isolated non-shell action families and dead legacy assets that could be proven unreferenced
- keep auth/session stabilization, shared i18n consolidation, and the recovered shared shell intact

## Harte Shell-Schutzregel

- no edits to `app/templates/base.html`, `app/templates/partials/_top_app_bar.html`, `app/templates/partials/_navigation_drawer.html`, `app/templates/partials/footer.html`, or `app/static/css/layout.css`
- no new `pm-shell-*`, `pm-topbar*`, `pm-panel*`, or `pm-footer*` shell migration work in 3a
- the preexisting unstaged diff in `_top_app_bar.html` was left untouched
- existing unrelated non-shell diffs in `20_layout.css` and `30_components.css` were left untouched

## Ausgangsbefund

- after the shell-regression recovery, productive non-shell surfaces still mixed `pm-*`, `promat-*`, and `md3-*`
- the safest remaining slice was not a broad template rewrite but isolated action rows already adjacent to proven PM button usage
- `research_phenomena_overview.html` and `research_phenomena_editor.html` still used MD3 dialog structures, but only the dialog action buttons remained obvious low-risk migration candidates
- the error pages still depended structurally on `css/md3/components/errors.css`, but their action rows were generic enough to migrate separately from the MD3 error layout
- `app/templates/pages/admin_dashboard.html` existed as a legacy remainder, but the productive admin routes already redirected to `/admin/users/page`

## Inventur: Shell vs. Nicht-Shell

- shell-owned surfaces remained the base wrapper, topbar, drawer, footer, and shell CSS; they were guarded and not edited
- non-shell productive slices addressed in this run were:
  - Phenomena dialog action rows in overview/editor
  - error-page action rows in 400/401/403/404/500
  - the unreferenced legacy `admin_dashboard.html` template
- shell-class inventory showed expected productive matches in the guarded shell files plus legitimate non-shell content-panel usage in `sample_page.html` and `promat_page.html`
- narrow `md3-|promat-` inventory showed:
  - error templates remain MD3-structured via `md3-error-*`
  - Phenomena dialogs remain MD3-structured via `md3-dialog*`, `md3-form`, and `md3-outlined-textfield*`
  - `promat-page`/`promat-content-*` remain active reading/workbench/content families in `promat_page.html`, `sample_page.html`, `research_player_stub.html`, and the Phenomena pages

## Geänderte Dateien

- `app/templates/pages/research_phenomena_overview.html`
- `app/templates/pages/research_phenomena_editor.html`
- `app/static/css/md3/components/dialog.css`
- `app/templates/errors/400.html`
- `app/templates/errors/401.html`
- `app/templates/errors/403.html`
- `app/templates/errors/404.html`
- `app/templates/errors/500.html`
- `app/tests/test_research_phenomena.py`
- `app/tests/test_auth_phase1.py`
- deleted: `app/templates/pages/admin_dashboard.html`

## Migrierte nicht-shellbezogene Templates

- `research_phenomena_overview.html`: rename and delete dialog action buttons migrated from MD3 buttons to `pm-action-button`
- `research_phenomena_editor.html`: confirm dialog action buttons migrated from MD3 buttons to `pm-action-button`
- `400.html`, `401.html`, `403.html`, `404.html`, `500.html`: error-page action buttons migrated from MD3 button classes to `pm-action-button`

## Migrierte oder klassifizierte Card-Familien

- no card family was migrated in this run
- `pm-panel` usage in `sample_page.html` and `promat_page.html` was classified as active non-shell content-panel usage, not shell drift
- no productive `md3-card` migration was attempted in 3a because the safe edit slices were isolated action rows rather than full surface rebuilds

## Migrierte oder klassifizierte Button-/Action-Familien

- migrated to PM:
  - Phenomena dialog cancel/save/delete/confirm actions
  - error-page primary and secondary actions across 400/401/403/404/500
- consciously classified as legacy for later work:
  - MD3 dialog/form/textfield internals in Phenomena
  - MD3 error-page layout containers and typography in `errors.css`
- no `pm-research-button` or `pm-research-inline-action` matches remained under the checked app paths

## Research-Phenomena / Dialoge / Forms

- the migration stayed intentionally narrow: only dialog action buttons changed
- `md3-dialog`, `md3-dialog__*`, `md3-form`, `md3-outlined-textfield*`, and surrounding dialog content stayed in place to avoid half-migrating dialog behavior or field styling
- `app/static/css/md3/components/dialog.css` gained mobile stacked-action support for `.pm-action-button` inside `.md3-dialog__actions` so the PM buttons keep the same full-width/centered mobile behavior as the previous MD3 buttons
- focused Phenomena regressions were expanded to assert PM buttons are present while `md3-button` is absent

## Error-Seiten

- 400/401/403/404/500 now use `pm-action-button` for their visible primary/secondary actions
- the surrounding error-page structure remains MD3-bound through `md3-error-page`, `md3-error-container`, `md3-error-icon`, `md3-error-title`, and `md3-error-actions`
- `css/md3/components/errors.css` was left untouched and classified as an explicit later migration boundary
- live 404 HTML on `http://127.0.0.1:8000/en/missing-page` confirmed `md3-error-page` plus PM primary/secondary action buttons, and no `md3-button` marker

## Public-/Sample-/Stub-Klassifizierung

- `sample_page.html` was not edited; its `pm-panel` usage remains an active sample mirror of existing productive content-panel families
- `promat_page.html` was not edited; `promat-page` and `promat-content-*` remain active reading/content families, not legacy shell debt
- `research_player_stub.html` was not edited; it remains a classified stub with active `promat-page` workbench structure and later cleanup potential outside this run
- no public/sample/stub surface was used as an upstream design source for 3a changes

## Tote Assets / Legacy-Skeletons

- deleted `app/templates/pages/admin_dashboard.html`
- admin route inspection showed `/admin` and `/admin/dashboard` already redirect to `/admin/users/page`
- reference check across `app/**` returned no remaining `admin_dashboard.html` matches
- decision: delete instead of migrate an unreferenced legacy template

## CSS-Hygiene

- changed only `app/static/css/md3/components/dialog.css` for PM button compatibility inside existing MD3 mobile dialog actions
- did not touch `layout.css`, `20_layout.css`, or `30_components.css` in this run to avoid shell drift
- left `app/static/css/md3/components/errors.css` untouched and explicitly classified as still owning the MD3 error layout
- no new shared alias layer or fallback shell selector family was introduced

## Tests

- focused Phenomena slice: `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q` -> `11 passed`
- focused error-page slice: `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_auth_phase1.py -q -k "generic_html_401_renders_error_page or generic_html_403_renders_error_page or error_pages_render_english_shared_copy"` -> `6 passed`
- full auth regression: `Run auth phase tests` -> `37 passed`
- full research regression: `Run research sessions tests` -> `182 passed`
- full Phenomena regression rerun: `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q` -> `11 passed`

## Grep-/Regressionsergebnisse

- no matches for `/auth/refresh|initAuthRefresh|token-refresh` under `app/static`, `app/src`, `app/templates`, and `app/tests`
- no matches for `pm-research-button|pm-research-inline-action` under `app/templates`, `app/static`, `app/src`, and `app/tests`
- shell inventory for `pm-shell-|pm-topbar|pm-panel|pm-footer` showed expected shell hits in guarded shell CSS/files and expected non-shell content-panel usage in `sample_page.html` and `promat_page.html`
- `admin_dashboard.html` reference search across `app/**` returned `NO_MATCHES`
- narrow legacy inventory showed remaining `md3-*` hits only where deliberately classified:
  - error-page layout structure
  - Phenomena dialog/form/textfield structure
- narrow legacy inventory showed remaining `promat-*` hits on active content/workbench families, not on the guarded shell migration path

## Browser-/Screenshot-Abnahme

- real browser pages were opened on:
  - `http://127.0.0.1:8000/de/project`
  - `http://127.0.0.1:8000/en/missing-page`
- live server HTML checks on `http://127.0.0.1:8000` confirmed:
  - `/de/project` -> `200`, `md3-content-wrapper`, `promat-main-column`, `md3-footer`
  - `/de/project/team` -> `200`, `md3-content-wrapper`, `promat-main-column`, `md3-footer`
  - `/de/sample` -> `200`, `md3-content-wrapper`, `promat-main-column`, `md3-footer`, `pm-panel`
  - `/de/research/spanish/design` -> `200`, `md3-content-wrapper`, `promat-main-column`, `md3-footer`
  - `/login?next=/de/project` -> `200`, `pm-auth-surface`, `pm-auth-secondary`, `pm-action-button`
  - `/en/missing-page` -> `404`, live HTML includes `md3-error-page` and PM primary/secondary action buttons
- protected Phenomena browser acceptance against the live `:8000` runtime could not be completed in this session because the documented local seed credentials (`felix.tacke@uni-marburg.de` / `change-me`) returned `401` on the running listener
- no screenshot artifacts were generated under `tmp/ui-qa/` in this session because the available browser tooling could open pages but did not expose screenshot capture or browser content inspection back into chat

## Verbleibende bewusst klassifizierte Legacy-Treffer

- `app/templates/errors/*.html`: `md3-error-*` layout and typography remain active until a dedicated error-surface migration exists
- `app/static/css/md3/components/errors.css`: remains the owning error-layout stylesheet
- `app/templates/pages/research_phenomena_overview.html` and `app/templates/pages/research_phenomena_editor.html`: `md3-dialog*`, `md3-form`, and `md3-outlined-textfield*` remain by design in 3a
- `app/templates/pages/research_player_stub.html`: classified stub still carrying active `promat-page` workbench structure and visible local branches for later cleanup
- `app/templates/pages/promat_page.html` and `app/templates/pages/sample_page.html`: `promat-*` content families remain active and intentionally not part of the shell-only rollback boundary

## Offene Folgepunkte für 3b/4 oder 4/4

- decide whether error pages deserve a full surface migration away from `md3/components/errors.css` or should remain a deliberately isolated MD3 legacy island
- decide whether Phenomena dialogs should move beyond PM action rows toward a full PM dialog/form family, and keep that work isolated from shell changes
- classify or clean up `research_player_stub.html` and any remaining visible inline language branches on stub/public surfaces
- if protected-route browser QA is required in the next slice, first establish reliable live credentials or a dedicated authenticated QA path before claiming screenshot coverage
- keep shell migration work separate from further non-shell cleanup so visual regressions remain attributable and browser-verifiable