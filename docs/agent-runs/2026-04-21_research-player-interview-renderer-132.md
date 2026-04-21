# Research Player Interview Renderer

## Summary

- implemented the productive `interview` renderer inside the existing unified research-player architecture
- kept `interview` inside the shared player shell and route family
- did not add compare support, set-filter logic, a task-specific player route, or a second upper player zone
- wired the renderer to productive runtime artifacts `alignment/interview.json` and `derived/interview.mp3`
- added segment focus, transcript rendering, material-reference overlay behavior, and focused regressions

## Spec Updates

- updated `docs/spec/research-capabilities.md` so `interview` is productive in player while still remaining non-compare and non-set-filter capable
- updated `docs/spec/research-player.md` so the interview renderer is defined as a segment-oriented content branch inside the shared player shell

## Implementation Notes

### Capability and runtime

- separated productive-player checks from set-filter capability checks
- enabled full-audio resolution for `interview` through the existing protected player-media route family
- normalized interview segments, speaker roles, token timing, `focus_segment`, and inline material references in `app/src/app/research_player_runtime.py`

### View and route

- threaded `focus_segment` through the public player route and shared player page builder
- kept task switching inside the same player architecture and suppressed compare/set UI automatically for `interview`
- reused the existing summary-band, material-strip, and control-bar payloads

### Template and client

- added an interview transcript branch below the existing player-control zone in `app/templates/pages/research_player.html`
- added a small contextual reference dialog for interview material references with an optional mini-player for referenced clips and a deep link back into the relevant task context
- extended `app/static/js/pages/research-player.js` for segment focus and reference-dialog behavior without forking the player controller
- extended shared player CSS in `app/static/css/20_layout.css` and `app/static/css/30_components.css` for the transcript and dialog surface

## Verification

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_capabilities.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- live authenticated HTTP check against `http://127.0.0.1:8000` confirmed German and English interview pages render transcript markup and the reference dialog labels
- local dev server started via `./scripts/dev-start.ps1`; this host fell back from PostgreSQL port `54321` to `55432` as expected

## Open Points

- the live validation confirmed transcript and dialog HTML presence in `de` and `en`, but no screenshot artifact was captured in this run
- the contextual reference dialog currently uses the existing MD3 dialog family as the calmest reusable surface; if later UX requires a different mobile presentation, that should stay within the same player architecture rather than introducing a separate interview shell
