# 2026-04-29 · Phenomena Dialog Stability Fix

## Scope

- stabilize the productive Phenomena delete and confirm dialogs after the PM dialog transfer
- keep the productive PM delete/confirm dialogs in place if the issues can be fixed locally and robustly
- keep the rename/form dialog on the existing MD3 shell and field stack
- do not touch shell, auth/session behavior, error pages, or any broader form/textfield migration

## Problembeobachtung

- after the productive PM dialog transfer, the real UI exposed regressions that were not visible in the sample-only pattern lab:
  - delete/confirm dialogs could remain open across navigation changes or re-entry scenarios
  - the confirm action button could render as a narrow pill without a stable PM label structure
  - the rename dialog had to be checked for accidental collateral damage from the new native-dialog CSS and lifecycle changes
  - the native `<dialog>` behavior in the real protected workbench differed from the earlier temporary harness expectations

## Ursachenanalyse

- the productive PM transfer had four concrete robustness gaps:
  - `showModal()` was called without an `open` guard in overview and editor dialog openers
  - there was no page-level dialog cleanup on `pagehide` / `beforeunload`, so native dialog state could survive into navigation/back-forward scenarios
  - the editor confirm submit button no longer used the normal PM button-label substructure; its text was written directly onto the button node, which made the live button rendering less stable than the rest of the PM button family
  - confirm dialog state cleanup depended on click handlers only, not on a central dialog `close` reset path
- browser QA also clarified one important point that is not itself a bug:
  - a native modal dialog correctly intercepts background clicks while open, so navigation-away behavior had to be tested through a real location change rather than by trying to click a background breadcrumb through the modal
- the rename/form dialog did not need rollback:
  - live screenshot QA showed the MD3 rename dialog still renders as an MD3 form shell with intact label/input relationship
  - the earlier broken screenshot state could not be reproduced after the dialog lifecycle and button-markup stabilization

## Entscheidung: Fix oder Rollback

- decision: fix, no rollback
- reason:
  - the regressions were local to the productive native-dialog lifecycle and confirm-button markup, not evidence that the productive PM delete/confirm transfer is fundamentally unworkable
  - the rename/form dialog remained isolated and stable on the MD3 stack
  - browser QA plus a state report showed that a small focused fix resolves the hanging/open-state issue without reopening broader migration scope

## Geänderte Dateien

- `app/templates/pages/research_phenomena_editor.html`
- `app/static/js/pages/research-phenomena-overview.js`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/static/css/30_components.css`
- `app/tests/test_research_phenomena.py`
- `docs/agent-runs/2026-04-29_phenomena-dialog-stability-fix.md`
- `tmp/ui-qa/phenomena-dialog-stability-fix-2026-04-29/capture_phenomena_dialog_stability_fix.py`

## Delete Dialog

- kept on the productive PM dialog shell
- stabilized by:
  - guarded `showModal()` usage
  - guarded `close()` usage
  - central close/reset handling for delete target and object summary content
  - pagehide/beforeunload cleanup
- live browser checks confirmed:
  - open
  - cancel
  - reopen
  - navigate away while open
  - return via back navigation
  - mobile open and cancel
- screenshots show the action row with visible labels and correct mobile stacking; the earlier narrow unlabeled action pill is no longer reproducible

## Confirm Dialog

- kept on the productive PM dialog shell
- stabilized by:
  - guarded `showModal()` usage
  - central `close` reset for danger/primary button classes, title/message content, and confirm action state
  - restored PM button label markup through `pm-action-button__label`
  - pagehide cleanup for open confirm dialogs
- live browser checks confirmed:
  - open
  - cancel
  - reopen through discard/delete flow
  - submit/delete back to overview
  - mobile open

## Rename/Form Dialog

- intentionally remains MD3
- no productive migration to PM form controls was attempted in this run
- live screenshot QA on the real overview route showed:
  - MD3 shell still active
  - label and input no longer overlap
  - PM native-dialog fixes do not override the MD3 rename shell

## JS-Stabilisierung

- overview:
  - added guarded `showDialog(...)` / `closeDialog(...)`
  - added dialog close resets for rename/delete state
  - added pagehide/beforeunload cleanup
  - added link-navigation cleanup before leaving the page
- editor:
  - added guarded `showDialog(...)` / `closeDialog(...)`
  - moved confirm reset behavior into a dialog `close` handler
  - added pagehide cleanup
  - kept danger-vs-standard confirm variants, but ensured they are reset on close

## CSS-Stabilisierung

- kept the productive PM dialog family in `30_components.css`
- tightened native `<dialog>` reset behavior for `dialog.pm-dialog`:
  - `box-sizing`
  - `inset`
  - `overflow`
  - stable open-state display
  - backdrop prefix for Safari
- hardened action-row behavior so PM action buttons keep their label width and do not collapse into a narrow pill on desktop
- retained mobile stacking only under the shared small-viewport rule

## Tests

- focused Phenomena regression:
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
  - `pm-shell-|pm-topbar|pm-footer` returned only expected existing shell token references in shared CSS; no shell migration markup was introduced in templates or tests
- productive Phenomena inventory after the fix:
  - rename/form dialog still contains `md3-dialog`, `md3-form`, and `md3-outlined-textfield*`
  - overview delete dialog remains PM-based with `pm-dialog` and `pm-object-summary`
  - editor confirm dialog remains PM-based with `pm-dialog`

## Browser-/Screenshot-Abnahme

- screenshot directory:
  - `tmp/ui-qa/phenomena-dialog-stability-fix-2026-04-29/`
- supporting QA report:
  - `tmp/ui-qa/phenomena-dialog-stability-fix-2026-04-29/qa_report.json`
- productive live route used:
  - `http://127.0.0.1:8000`
- authenticated QA used the local dev admin created by `app/scripts/dev-start.ps1`
- captured key artifacts:
  - `de-phenomena-delete-open.png`
  - `de-after-open-delete-navigation.png`
  - `de-after-back-to-overview.png`
  - `de-phenomena-rename-open.png`
  - `de-phenomena-confirm-open.png`
  - `de-after-confirm-delete.png`
  - `en-phenomena-overview.png`
  - `de-phenomena-delete-open-mobile.png`
  - `de-phenomena-confirm-open-mobile.png`
  - `de-design-regression.png`
  - `de-sample-regression.png`
- verified outcomes:
  - delete dialog opens, closes, reopens, and is not left open after navigation away/back
  - confirm dialog opens, closes, and routes back cleanly after destructive confirmation
  - rename dialog remains visually intact on its MD3 shell
  - the earlier blank blue action-pill regression is no longer present
  - mobile screenshots show full-width stacked actions with visible labels
  - unaffected regression surfaces `/de/sample` and `/de/research/spanish/design` remain visually stable

## Offene Folgepunkte

- the productive PM dialog family is stable enough for these two Phenomena dialog surfaces, but broader productive PM form/textfield migration should still stay separate
- if future work touches native PM dialogs outside Phenomena, reuse the same guarded open/close lifecycle and pagehide cleanup instead of copying the earlier, more optimistic transfer pattern