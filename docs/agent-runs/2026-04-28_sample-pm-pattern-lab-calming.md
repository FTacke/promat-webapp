# 2026-04-28 · Sample PM Pattern Lab Calming Pass

## Scope

- calm and systematize the preview-only PM patterns at `/sample`
- no productive migration into Phenomena, error pages, auth/session flows, player logic, or shell files
- keep MD3 islands in place and improve only the sample-first PM reference family plus its focused tests and QA artifacts

## Ausgangsbefund

- the initial sample-first PM pattern lab was directionally correct, but the vertical rhythm still came from several isolated `gap`, `padding`, and action-row values inside each pattern
- the dialog row was overpacked because the standard dialog, danger dialog, and form dialog shared the same three-column desktop row
- the danger dialog already felt calmer than MD3 but still looked slightly compressed, with an object summary that was too dominant for the amount of surrounding content
- the form dialog was the tallest element in the row and inherited a compact dialog rhythm that did not match a form-heavy surface
- the field controls were close to useful, but labels, controls, helper text, error text, and textarea weight were still a bit too bookish and too loosely systematized
- the error surface still looked more playful than calm because the code token and action area carried too much visual weight relative to the message

## Rhythmus-/Density-Modell

- introduced one reusable density system through inherited CSS custom properties on:
  - `pm-surface-density--compact`
  - `pm-surface-density--standard`
  - `pm-surface-density--spacious`
- the model controls shared surface rhythm via inherited variables instead of per-pattern ad hoc values:
  - surface padding
  - vertical stack gap
  - header/body cluster gap
  - form gap
  - field gap
  - action-row gap
  - form-control minimum height and padding
  - textarea minimum height
  - object-summary padding
- the model is consumed by `pm-dialog`, `pm-form`, `pm-error-surface`, `pm-media-surface`, and `pm-workbench-card`
- reused base PM spacing tokens and derived smaller internal steps from them with `calc(...)`; no second parallel density taxonomy was introduced
- added one shared `pm-action-row` and one neutral `pm-object-summary` family so dialog, error, media, and workbench actions use the same calmer row logic

## Layoutänderungen im Pattern Lab

- code inspection before the edit confirmed the previous pattern lab used:
  - one three-column desktop dialog grid in `20_layout.css`
  - separate local spacing in `30_components.css` for dialog, form, error, and media surfaces
  - a separate workbench action-row rhythm in `40_cards.css`
- there were no meaningful existing density helpers for these patterns; only generic PM spacing tokens existed in `00_tokens.css`
- desktop layout now follows the calmer two-column structure:
  - row 1: standard dialog | danger dialog
  - row 2: wide form dialog across both columns
  - row 3: field set | error surface
  - row 4: media surface | workbench card
- mobile remains single-column and tablet stays two-column where useful
- the form dialog is no longer forced into the same narrow rhythm as the confirm/delete dialogs

## Dialoge

- standard dialog now uses `pm-surface-density--compact` and the shared `pm-action-row`
- danger dialog also uses `pm-surface-density--compact`, but its object context is now rendered through the neutral reusable `pm-object-summary` pattern instead of one heavier single block
- the object summary was calmed by reducing fill strength, softening the border, and giving the label/value a quiet UI hierarchy
- the delete button icon was removed so the danger action reads as a calm destructive option rather than a technical warning state
- the danger dialog now stays compact without appearing cramped

## Form Dialog und Form Controls

- form dialog moved to `pm-surface-density--spacious` and spans the full dialog row in the sample grid
- form dialog actions now use the shared action row with right alignment on larger widths and stacked behavior on mobile
- the sample save label was shortened from `Änderungen speichern` / `Save changes` to `Speichern` / `Save`
- the form dialog textarea was reduced to a smaller demo height and now reads as a UI field instead of a larger reading area
- field markup was normalized to the explicit field pattern:
  - label
  - control
  - helper or error text
- added reusable state hooks:
  - `pm-form-field--error`
  - `pm-form-control--error`
  - `pm-form-field--disabled`
- control typography now uses the UI font family and calmer input sizing rather than inherited reading-like text behavior

## Error Surface

- error surface now uses `pm-surface-density--standard`
- `pm-error-surface__code` was reduced from a larger pill-like accent into a compact badge with quieter border and fill treatment
- error actions now use the shared `pm-action-row` and normal PM button proportions
- the leading icons were removed from the sample error actions so the surface can later transfer more directly to real 404/403/500 states without looking playful or oversized
- the message-to-actions distance is shorter and more professional than in the first pattern-lab pass

## Media Surface

- media surface now uses `pm-surface-density--compact`
- the title no longer carries the more content-heavy `pm-item-content-text` styling and now reads as a calmer UI surface heading
- controls were slightly reduced in size and the progress/control cluster was tightened
- the footer now uses the shared action-row rhythm, and the CTA remains a quiet secondary action rather than a full-width callout

## Workbench Card

- workbench card now uses `pm-surface-density--standard`
- body gap, header gap, and action-row gap are aligned with the same inherited rhythm model used by the other sample patterns
- the card status continues to use the existing `pm-research-meta-badge` logic; the badge remains neutral but is now explicitly treated as the card status element
- title, body, and count now use UI sans rather than reading-oriented typography because this card is meant as a workbench surface, not long-form content
- action buttons were stripped of icons so the row reads more like a production-adjacent workbench card than a demo control cluster

## Geänderte Dateien

- `app/templates/pages/sample_page.html`
- `app/src/app/i18n.py`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`
- `docs/agent-runs/2026-04-28_sample-pm-pattern-lab-calming.md`

## Tests

- focused sample validation:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "sample_page_exposes_pm_pattern_lab_before_interaction_preview or sample_page_pattern_lab_uses_density_layout_and_quiet_error_actions or sample_page_localizes_pm_pattern_lab_in_english"` -> `3 passed`
- full auth regression:
  - `Run auth phase tests` -> `37 passed`
- full research sessions regression:
  - `Run research sessions tests` -> `185 passed`
- full Phenomena regression:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q` -> `11 passed`
- governance:
  - `c:/dev/promat/.venv/Scripts/python.exe scripts/ci_governance_checks.py` -> `PASS`

## Grep-/Regressionsergebnisse

- current pattern-lab inventory grep showed the PM family lives in:
  - `sample_page.html`
  - `20_layout.css`
  - `30_components.css`
  - `40_cards.css`
  - focused sample tests
- forbidden auth refresh frontend paths:
  - `/auth/refresh|initAuthRefresh|token-refresh` -> `NO_MATCHES`
- forbidden legacy research interaction classes:
  - `pm-research-button|pm-research-inline-action` -> `NO_MATCHES`
- shell grep:
  - `pm-shell-|pm-topbar|pm-footer` returned only expected existing shell token references in `layout.css` and `30_components.css`; no new shell migration markup or sample-induced shell drift was introduced
- no new `md3-dialog`, `md3-error`, or `md3-button` markers appear inside the pattern-lab HTML slice

## Browser-/Screenshot-Abnahme

- screenshot directory:
  - `tmp/ui-qa/pm-pattern-lab-calming-2026-04-28/`
- captured files:
  - `de-sample.png`
  - `en-sample.png`
  - `de-sample-tablet.png`
  - `de-sample-mobile.png`
  - `de-project.png`
  - `de-research-spanish-design.png`
- verified outcomes:
  - desktop and tablet sample now show the form dialog in its own broad row instead of inside a cramped three-card row
  - standard and danger dialogs now read as a compact pair with balanced heights and calmer action rows
  - danger dialog object summary is visibly quieter and no longer dominates the surface
  - form dialog actions are no longer visually pressed into the bottom edge
  - field controls have a clearer label/control/help rhythm and the UI typography is more control-like than book-like
  - error surface shows a compact 404 badge and normal-sized buttons instead of a more playful oversized action treatment
  - media surface keeps the player-adjacent calmness without feeling like a full player widget
  - workbench card remains production-adjacent and calmer, with sans typography and a clearer meta/action split
  - `/de/project` remains unchanged visually, so the shared CSS edits did not leak into shell or long-form content rhythm
  - `/de/research/spanish/design` remains unchanged visually, so the shared CSS edits did not disturb the research reading surface
- residual note:
  - on mobile, all pattern-lab action rows stack full-width by design; this is visually consistent and readable, though still intentionally stronger than desktop because touch targets stay the priority

## Bewertung nach Calming Pass

- the pattern lab is now materially more systematic because the core rhythm is controlled by one density model instead of several isolated spacing islands
- the clearest gain is structural: compact dialogs are now truly compact while the form dialog has a compatible but different spacious density
- danger, error, and workbench actions now feel less alarmist and less demo-like
- the control family is close enough to serve as the current preview reference for a later real PM form transfer
- the current preview set is visually stable enough to use as the next decision base for a narrow productive migration

## Empfohlene produktive Übertragung

- first productive candidate remains the Phenomena delete dialog
- reason:
  - its compact destructive pattern now has the clearest and most convincing preview form
  - it exercises the new calm danger-dialog rhythm without requiring the full form-control stack to migrate at the same time
  - it is the smallest productive slice that would prove whether the sample-first dialog family transfers cleanly into a real workbench surface