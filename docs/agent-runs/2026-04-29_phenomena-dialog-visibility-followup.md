# 2026-04-29 · Phenomena Dialog Visibility Follow-up

## Scope

- fix the follow-up regression where productive Phenomena dialogs rendered visibly without user interaction
- confirm whether the local dev runtime was stale or serving the current broken CSS
- keep the earlier dialog lifecycle stabilization intact

## Problembeobachtung

- the current screenshots showed three symptoms at once:
  - delete dialog visible on load without backdrop interaction
  - rename dialog shell visibly parked in the page flow
  - editor confirm row showing only `Abbrechen` plus an empty blue pill
- those symptoms pointed to closed native `<dialog>` elements being rendered as normal layout boxes before any JS opened them

## Ursachenanalyse

- the shared PM dialog CSS applied `display: grid` directly to `.pm-dialog`
- on native `<dialog class="pm-dialog">` elements this overrode the browser's hidden-by-default behavior for closed dialogs
- because the confirm dialog title/message/submit label are populated only when JS opens the dialog, a closed-but-rendered dialog naturally appeared as a partial shell with an empty confirm button
- the active dev server on `:8000` was not stale:
  - the served `30_components.css` already reflected the current code state
  - the served HTML did not contain accidental `open` attributes on the Phenomena dialogs

## Fix

- kept the existing PM dialog structure and JS lifecycle work unchanged
- added an explicit native-dialog guard in `app/static/css/30_components.css`:
  - `dialog.pm-dialog:not([open]) { display: none; }`
- this restores the expected closed-state invisibility while keeping open-state PM dialog layout intact

## Validation

- served asset check on `http://127.0.0.1:8000/static/css/30_components.css` confirmed the live dev server now serves the hidden-by-default rule
- served HTML checks on the Phenomena routes confirmed no `open` attribute is emitted for rename, delete, or confirm dialogs
- focused regression:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q` -> `11 passed`

## Geänderte Dateien

- `app/static/css/30_components.css`
- `docs/agent-runs/2026-04-29_phenomena-dialog-visibility-followup.md`