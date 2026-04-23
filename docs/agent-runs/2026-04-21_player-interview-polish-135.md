# Research Player Interview Polish

## Summary

- tightened the existing shared research-player shell without adding a new player architecture, route family, or second upper player zone
- unified the productive playback heading to `Wiedergabe` or `Playback` across `wordlist`, `text`, and `interview`
- expanded the shared player metadata cards to include `Geschlecht` or `Gender`, `Sprachaufenthalte` or `Stays in target-language country`, and `Explorator:in` or `Recorded by`
- removed the extra interview content-summary header above the transcript and kept the interview body inside the existing shared player panel
- refined the interview transcript rows and reference popover so reference clicks stay separate from turn playback and the popover remains compact, collision-aware, and download-capable

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/research-player.md`
- `docs/runbooks/ui-change-workflow.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/static/js/pages/research-player.js`
- `app/tests/test_research_sessions.py`

## Spec Updates

- updated `docs/spec/research-player.md` so the shared productive metadata-card contract now includes `gender`, `target_country_stays`, and `recorded_by`
- updated `docs/spec/research-player.md` so interview explicitly keeps the shared playback title, omits a duplicate interview summary header, and treats the material-reference popover plus non-bubbling reference interaction as part of the active player contract

## Implementation Notes

### Shared player builder

- changed the productive control-bar title to always use the shared playback label instead of task-specific `items_title`
- expanded player summary-card facts in `app/src/app/research_views.py` for all productive player tasks

### Interview template and styling

- removed the extra interview content header from `app/templates/pages/research_player.html`
- kept the interview left meta column to role badge plus timing only
- added a compact split-download icon to the reference mini-player
- refined transcript and popover styling in `app/static/css/30_components.css` so the active turn is softer, the transcript text width is bounded, the badge plus time stay on one line, and the popover stays compact on desktop and as a small sheet on mobile

### Interaction behavior

- blocked pointer, touch, and keyboard propagation from inline reference triggers so they do not trigger turn playback
- replaced the old fixed-below reference-dialog placement with flip and shift positioning plus viewport padding in `app/static/js/pages/research-player.js`
- added live repositioning on resize and scroll for the open reference popover

## Verification

- VS Code problems check for `research_views.py`, `research_player.html`, `30_components.css`, `research-player.js`, `test_research_sessions.py`, and `research-player.md` reported no errors
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- headless Edge or Selenium pass against `http://127.0.0.1:8000` with the local dev admin validated:
  - desktop `de` interview route with compact reference popover and no viewport clipping
  - desktop `en` interview route with shared `Playback` title and correct popover CTA
  - mobile `de` and `en` interview routes with role badge plus time on one line and the popover rendered as a compact bottom sheet
  - unaffected `de` wordlist player route as a regression check for the shared metadata-card and control-bar family
- screenshot and QA artifacts:
  - `tmp/ui-qa/2026-04-21-player-interview-polish-135/de-interview.png`
  - `tmp/ui-qa/2026-04-21-player-interview-polish-135/de-interview-popover.png`
  - `tmp/ui-qa/2026-04-21-player-interview-polish-135/en-interview.png`
  - `tmp/ui-qa/2026-04-21-player-interview-polish-135/en-interview-popover.png`
  - `tmp/ui-qa/2026-04-21-player-interview-polish-135/de-interview-mobile-popover.png`
  - `tmp/ui-qa/2026-04-21-player-interview-polish-135/en-interview-mobile-popover.png`
  - `tmp/ui-qa/2026-04-21-player-interview-polish-135/de-wordlist-regression.png`
  - `tmp/ui-qa/2026-04-21-player-interview-polish-135/qa-results.json`

## Notes

- `app/templates/pages/sample_page.html` was not changed in this run because it does not currently mirror the shared player or interview-popover surface that was refined here
