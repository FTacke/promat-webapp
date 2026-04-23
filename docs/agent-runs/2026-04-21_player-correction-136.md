# Research Player Correction Pass

## Summary

- corrected the shared research-player surfaces without adding a new architecture, route family, or second player zone
- restored the lower interview material title while keeping the redundant interview count line removed
- tightened the interview transcript spacing, alignment, active-turn treatment, and reference-popover header layout
- added a data-driven `spoken_title_item` contract so connected-text `running_text` can render a spoken title line while list mode keeps the same item as a normal first row
- marked the productive English text title item in both the task catalog and the session alignment data

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/research-player.md`
- `app/src/app/research_presets.py`
- `app/src/app/research_player_runtime.py`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-player.js`
- `app/tests/test_research_sessions.py`
- `data/config/research_player/english/task_catalogs/text.json`
- `data/sessions/english/EN-L-0001-2026-S01/alignment/text.json`

## Spec Updates

- updated `docs/spec/research-player.md` so normalized text items may carry `spoken_title_item`
- clarified in `docs/spec/research-player.md` that interview keeps the lower material title but omits the duplicate count line
- clarified in `docs/spec/research-player.md` that the interview reference popover keeps the quiet number pill directly beside the reference label

## Implementation Notes

### Runtime and data

- extended `TaskCatalogItem` in `app/src/app/research_presets.py` with `spoken_title_item`
- propagated `spoken_title_item` through set-context filtering, bundle loading, normalized player rows, and running-text block construction in `app/src/app/research_player_runtime.py`
- marked `t_01` as `spoken_title_item = true` in the productive English task catalog and in `data/sessions/english/EN-L-0001-2026-S01/alignment/text.json`

### Template and styling

- updated `app/templates/pages/research_player.html` so the interview content panel always shows the material title and suppresses only the redundant count line
- moved the interview popover number pill into the same header row as the reference label
- added a dedicated running-text spoken-title renderer path in the shared template
- widened the interview meta-to-text column gap in `app/static/css/20_layout.css`
- softened and aligned the interview transcript rows and added spoken-title text styling in `app/static/css/30_components.css`

### Regression coverage

- updated `app/tests/test_research_sessions.py` for the restored interview title, the missing count line, the popover title row, and the running-text spoken-title behavior

## Verification

- VS Code problems check for `research_presets.py`, `research_player_runtime.py`, `research_player.html`, `20_layout.css`, `30_components.css`, and `test_research_sessions.py` reported no errors
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- headless Edge or Selenium pass against `http://127.0.0.1:8000` validated:
  - desktop `de` interview route with shared `Wiedergabe` title, visible lower `Interview` title, no `22 Segmente` line, compact popover, and working download utility
  - desktop `en` interview route with shared `Playback` title, visible lower `Interview` title, and correct popover layout
  - mobile `de` and `en` interview routes with role badge plus time on one line and unclipped bottom-sheet popover
  - desktop `de` and `en` English text routes with the spoken title rendered as its own running-text line
  - desktop `en` English sentence-list route with no spoken-title block leakage
  - unaffected `de` wordlist route as a regression check for the shared metadata-card family
- screenshot and QA artifacts:
  - `tmp/ui-qa/2026-04-21-player-correction-136/de-interview.png`
  - `tmp/ui-qa/2026-04-21-player-correction-136/de-interview-popover.png`
  - `tmp/ui-qa/2026-04-21-player-correction-136/en-interview.png`
  - `tmp/ui-qa/2026-04-21-player-correction-136/en-interview-popover.png`
  - `tmp/ui-qa/2026-04-21-player-correction-136/de-interview-mobile-popover.png`
  - `tmp/ui-qa/2026-04-21-player-correction-136/en-interview-mobile-popover.png`
  - `tmp/ui-qa/2026-04-21-player-correction-136/de-english-text.png`
  - `tmp/ui-qa/2026-04-21-player-correction-136/en-english-text.png`
  - `tmp/ui-qa/2026-04-21-player-correction-136/de-wordlist-regression.png`
  - `tmp/ui-qa/2026-04-21-player-correction-136/qa-results.json`

## Notes

- `app/templates/pages/sample_page.html` was not changed because this run did not modify a mirrored sample element there