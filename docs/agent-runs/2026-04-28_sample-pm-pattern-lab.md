# 2026-04-28 · Sample PM Pattern Lab

## Scope

- build a sample-first PM pattern lab at the top of `sample` without migrating any productive legacy surface
- add new PM component patterns only where they are rendered inside the sample page
- keep productive Phenomena dialogs/forms, productive error pages, productive auth/session flows, player runtime logic, and the frozen shell unchanged

## Ausgangsbefund

- productive legacy and MD3 islands still exist in three relevant groups:
  - Phenomena dialogs and dialog-bound form fields in `research_phenomena_overview.html` and `research_phenomena_editor.html`
  - HTML error pages plus `app/static/css/md3/components/errors.css`
  - active `promat-page` and `promat-content-*` workbench/content surfaces on productive reading and research pages
- repo-wide PM inventory still lacked a productive shared `pm-dialog`, `pm-form`, `pm-textfield`, or `pm-error` family; only action/button and adjacent field patterns existed
- `sample` already uses the shared translation layer and current productive layout families, so it is the right safe place for visual comparison patterns before any productive transfer

## Referenz: Interview-/Player-Surface

- the visual reference for calm compact surfaces was the current player reference popover and adjacent player panel geometry in `app/templates/pages/research_player.html` and `app/static/css/30_components.css`
- reused characteristics:
  - bright paper-like surface
  - soft border and restrained shadow
  - compact header/body/action rhythm
  - rounded, quiet controls
  - mobile-friendly stacking without oversized modal weight
- no player-specific JS or runtime behavior was transferred into the sample patterns

## Inventur der verbleibenden Legacy-/MD3-Inseln

1. Phenomena Dialoge:
   - productive `md3-dialog*` remain in `research_phenomena_overview.html` and `research_phenomena_editor.html`
2. Formfelder / Textfields / Textareas:
   - productive `md3-form` and `md3-outlined-textfield*` remain in the Phenomena rename flow
3. Error-Surface:
   - productive `md3-error-*` remains in `app/templates/errors/*.html` with `css/md3/components/errors.css`
4. Confirm-/Delete-Dialoge:
   - productive confirm/delete dialog shells remain MD3-bound in Phenomena
5. Standard-Dialoge:
   - remaining dialog skeletons exist under `app/templates/_md3_skeletons/`
6. Workbench-/Content-Surfaces:
   - `promat-page` and `promat-content-*` remain active workbench/reading families, not migration debt to remove in this step
7. Player-/Interview-Dialog als visuelle Referenz:
   - `pm-player-reference-popover*` remains the best current compact PM-like dialog/surface reference
8. bewusst nicht berührte Shell:
   - no edits to `base.html`, top app bar, navigation drawer, footer structure, or shell layout rules

## Neue Sample-Muster

- added a new top-of-page section in `sample_page.html` titled `PM Komponentenmuster` / `PM component patterns`
- the new section appears before the existing interaction preview and is explicitly framed as a QA surface rather than productive content
- rendered patterns:
  - PM standard dialog
  - PM danger / delete dialog
  - PM form dialog
  - PM field set / form controls
  - PM error surface
  - PM compact media / player-inspired surface
  - PM workbench card / action row
- all user-facing copy for the new area ships in `de` and `en` through `app/src/app/i18n.py`

## Neue oder geänderte PM-Klassen

- in `app/static/css/30_components.css`:
  - `pm-action-button--danger`
  - `pm-dialog*`
  - `pm-form*`
  - `pm-error-surface*`
  - `pm-media-surface*`
- in `app/static/css/40_cards.css`:
  - `pm-workbench-card*`
- in `app/static/css/20_layout.css`:
  - `pm-pattern-lab*` layout/grid helpers for the sample-only arrangement

## Nicht geänderte produktive Bereiche

- no productive Phenomena template or JS logic was changed
- no productive error page or `errors.css` migration was attempted
- no auth/session page or flow was changed
- no player runtime logic, route logic, or research access logic was changed
- no MD3 asset was deleted
- no shell structure or shell CSS was changed

## Geänderte Dateien

- `app/templates/pages/sample_page.html`
- `app/src/app/i18n.py`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`
- `docs/agent-runs/2026-04-28_sample-pm-pattern-lab.md`

## Tests

- focused sample slice:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "pattern_lab or sample_page_localizes_pm_pattern_lab_in_english"` -> `2 passed`
  - rerun after CSS integration -> `2 passed`
- full auth regression:
  - `Run auth phase tests` -> `37 passed`
- full research regression:
  - `Run research sessions tests` -> `184 passed`
- full Phenomena regression:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q` -> `11 passed`
- governance checks:
  - `c:/dev/promat/.venv/Scripts/python.exe c:/dev/promat/scripts/ci_governance_checks.py` -> `PASS`

## Grep-/Regressionsergebnisse

- required regression greps:
  - `/auth/refresh|initAuthRefresh|token-refresh` under productive app paths -> `NO_MATCHES`
  - `pm-research-button|pm-research-inline-action` under productive app paths -> `NO_MATCHES`
- raw shell grep for `pm-shell-|pm-topbar|pm-footer` returned only accepted existing token references in shell CSS; no new shell template migration hits were introduced
- legacy inventory grep confirmed active productive MD3 remnants remain where expected:
  - Phenomena dialogs/forms
  - HTML error pages
  - `_md3_skeletons/`
- PM pattern grep confirmed the new sample-first family is present only in:
  - `sample_page.html`
  - `20_layout.css`
  - `30_components.css`
  - `40_cards.css`
  - focused sample tests

## Browser-/Screenshot-Abnahme

- screenshot directory:
  - `tmp/ui-qa/pm-pattern-lab-2026-04-28/`
- captured pages:
  - `de-sample.png`
  - `en-sample.png`
  - `de-sample-tablet.png`
  - `de-sample-mobile.png`
  - `de-project.png`
  - `de-research-spanish-design.png`
- verified outcomes:
  - the pattern lab renders above the existing interaction preview on `/de/sample` and `/en/sample`
  - the standard and danger dialogs read as noticeably calmer and more compact than the current MD3 productive delete-dialog baseline
  - the form dialog and field set no longer look MD3-shaped; controls use the quieter PM surface language
  - the error surface fits the PM card/surface language and stays readable in both languages
  - the media surface picks up the player/reference-popover calmness without pretending to be a live player
  - the workbench card shows a stable action row without falling back to MD3 or older legacy button patterns
  - `/de/project` and `/de/research/spanish/design` show no visible shell drift from this run
  - mobile screenshot shows correct stacking for dialog actions and readable field widths
- residual note:
  - the mobile topbar remains dense on narrow widths, but that is a preexisting shell concern and was intentionally left out of scope

## Bewertung der Muster

- visually ready:
  - PM standard dialog
  - PM danger / delete dialog
  - PM form dialog
  - PM field set / form controls
  - PM error surface
  - PM media surface
  - PM workbench card
- likely needs minor calibration only when transferred productively:
  - exact spacing around danger-object chips against real Phenomena copy lengths
  - exact primary/secondary action emphasis inside a real error-page layout
  - exact control density if a productive form needs validation/help/error states with live data

## Empfohlene nächste produktive Übertragung

- first candidate: the Phenomena delete dialog
- reason:
  - smallest high-value productive transfer
  - already close to the new compact danger dialog semantics
  - no need to migrate a full field system at the same time
- after that, likely order:
  1. Phenomena confirm/delete dialogs
  2. Phenomena rename/form dialog
  3. HTML error surface