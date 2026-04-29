# 2026-04-28 · Phenomena PM Dialog Transfer

## Scope

- transfer only the previewed PM dialog shells to productive Phenomena delete and confirm dialogs
- keep the rename/form dialog on the existing MD3 form/textfield stack
- leave productive error pages, shell files, auth/session flows, and public/sample structure untouched

## Ausgangsbefund

- Phenomena overview still used two MD3 dialog shells:
  - rename dialog with `md3-form` and `md3-outlined-textfield*`
  - delete dialog with `md3-dialog*` around already-migrated PM action buttons
- Phenomena editor still used one MD3 confirm dialog shell around PM action buttons
- the sample pattern lab already had a stable preview-only PM dialog family with:
  - `pm-dialog`
  - `pm-dialog--danger`
  - `pm-surface-density--compact`
  - `pm-action-row`
  - `pm-object-summary`
  - `pm-action-button--danger`
- JS inspection confirmed both productive dialog flows were bound through `data-*` hooks and native `showModal()/close()` calls, not through `md3-dialog` selectors

## Übertragene Sample-Muster

- transferred directly from the sample PM family into productive Phenomena dialogs:
  - `pm-dialog`
  - `pm-dialog--danger`
  - `pm-surface-density--compact`
  - `pm-action-row`
  - `pm-object-summary`
  - `pm-action-button--danger`
- added minimal neutral support so `pm-dialog` works as a native `<dialog>` outside `/sample`:
  - `dialog.pm-dialog`
  - `dialog.pm-dialog[open]`
  - `dialog.pm-dialog::backdrop`

## Delete Dialog

- productive overview delete dialog now uses the PM danger shell instead of `md3-dialog*`
- new structure:
  - `pm-dialog pm-dialog--danger pm-surface-density--compact`
  - `pm-dialog__header`
  - `pm-dialog__body`
  - `pm-object-summary`
  - `pm-dialog__actions pm-action-row`
- destructive action now uses `pm-action-button--danger` instead of the previous primary styling
- the dynamic set label is now rendered into `data-phenomena-delete-object`
- static copy uses the shared i18n layer for:
  - delete body text
  - selected-set summary label
- no MD3 button class remains in the delete dialog slice

## Confirm Dialog

- productive editor confirm dialog now uses the PM dialog shell instead of `md3-dialog*`
- new structure:
  - `pm-dialog pm-surface-density--compact`
  - `pm-dialog__header`
  - `pm-dialog__body`
  - `pm-dialog__actions pm-action-row`
- existing `data-*` hooks remain intact for title, message, cancel, and submit
- JS now toggles the confirm dialog between standard and danger visual state depending on the action:
  - discard confirmation stays standard with primary confirm button
  - saved-set deletion switches to `pm-dialog--danger` and `pm-action-button--danger`

## Bewusst nicht migrierter Rename/Form Dialog

- the overview rename dialog remains MD3 on purpose
- unchanged legacy pieces:
  - `md3-dialog`
  - `md3-form`
  - `md3-outlined-textfield*`
- reason:
  - no half-migration of dialog shell plus legacy form controls in the same run
  - productive form/textfield migration remains a later isolated slice

## CSS-Änderungen

- no shell CSS was changed
- no `layout.css` edit
- no `md3/components/errors.css` edit
- only neutral PM dialog support was added in `30_components.css` so the same PM dialog family used on `/sample` can render as a real native dialog productively

## JS-Hooks

- overview delete dialog hooks preserved:
  - `data-phenomena-delete-dialog`
  - `data-phenomena-delete-object`
  - `data-phenomena-delete-cancel`
  - `data-phenomena-delete-confirm`
- editor confirm dialog hooks preserved:
  - `data-phenomena-editor-confirm`
  - `data-phenomena-editor-confirm-title`
  - `data-phenomena-editor-confirm-message`
  - `data-phenomena-editor-confirm-cancel`
  - `data-phenomena-editor-confirm-submit`
- no JS logic depends on MD3 visual classes after this transfer

## Geänderte Dateien

- `app/templates/pages/research_phenomena_overview.html`
- `app/templates/pages/research_phenomena_editor.html`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-phenomena-overview.js`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/src/app/i18n.py`
- `app/tests/test_research_phenomena.py`
- `docs/agent-runs/2026-04-28_phenomena-pm-dialog-transfer.md`

## Tests

- focused dialog-transfer slice:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q -k "public_phenomena_overview_route_renders_split_overview or public_preset_editor_route_renders_editor_page or public_set_editor_route_renders_for_authenticated_owner"` -> `3 passed`
- full Phenomena regression:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q` -> `11 passed`
- full auth regression:
  - `Run auth phase tests` -> `37 passed`
- full research sessions regression:
  - `Run research sessions tests` -> `185 passed`
- governance:
  - `c:/dev/promat/.venv/Scripts/python.exe scripts/ci_governance_checks.py` -> `PASS`

## Grep-/Regressionsergebnisse

- forbidden auth refresh frontend paths:
  - `/auth/refresh|initAuthRefresh|token-refresh` -> `NO_MATCHES`
- forbidden legacy research interaction classes:
  - `pm-research-button|pm-research-inline-action` -> `NO_MATCHES`
- shell grep:
  - `pm-shell-|pm-topbar|pm-footer` returned only expected existing shell token references in `layout.css` and `30_components.css`; no shell migration markup was introduced
- Phenomena MD3 inventory after transfer:
  - rename/form dialog in `research_phenomena_overview.html` still contains `md3-dialog`, `md3-form`, and `md3-outlined-textfield*`
  - overview delete dialog no longer contains `md3-dialog` or `md3-button`
  - editor confirm dialog no longer contains `md3-dialog` or `md3-button`

## Browser-/Screenshot-Abnahme

- screenshot directory:
  - `tmp/ui-qa/phenomena-pm-dialog-transfer-2026-04-28/`
- captured files:
  - `de-phenomena-overview-delete-dialog.png`
  - `de-phenomena-editor-confirm-dialog.png`
  - `de-phenomena-overview-delete-dialog-mobile.png`
  - `de-project.png`
  - `de-research-spanish-design.png`
  - `de-sample.png`
- live auth note:
  - the real dev server on `:8000` correctly redirects `/de/research/spanish/phenomena` to `/login?next=/de/research/spanish/phenomena`
  - because productive Phenomena is auth-gated, dialog-open screenshots were captured through a temporary local QA harness on `:8011` that rendered the same productive templates with test data and auto-auth, while guard pages were checked on the real `:8000` server
- verified outcomes:
  - overview delete dialog visually matches the calmer PM danger language from the sample pattern lab
  - object summary is present and quieter than the previous MD3-bound dialog treatment
  - delete action is visibly destructive but not alarmistic
  - editor confirm dialog reads as a compact PM confirm surface and fits the surrounding workbench layout
  - mobile overview delete screenshot shows correct stacked actions and readable object summary
  - `/de/project`, `/de/research/spanish/design`, and `/de/sample` show no shell or sample regressions from this run
- limitation:
  - cancel/delete clicks were not manually exercised in a live authenticated browser session on `:8000`; visual QA used the temporary harness, while behavior continuity is covered by preserved `data-*` hooks and the passing Phenomena regression suite

## Offene Folgepunkte

- rename/form dialog remains the next isolated migration candidate if the productive PM field/control family is accepted
- HTML error surface remains a separate future slice and should not be combined with the form-dialog transfer