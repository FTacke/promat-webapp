# Research Player Interview Turn Layout Pass

## Summary

- reworked the existing shared interview turn rows so the left metadata column is a vertical stack again, with the role badge above the turn timing
- aligned the timing line to the badge text inset instead of the outer pill edge
- tightened the interview row geometry so the metadata column and the reading block feel more balanced without changing the shared player architecture, route family, or reference behavior

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/research-player.md`
- `app/templates/pages/research_player.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`

## Spec Updates

- updated `docs/spec/research-player.md` so the active interview transcript contract now explicitly requires a stacked badge-plus-timing metadata column, timing aligned to the badge text inset, and compact content-led turn rows

## Implementation Notes

### Interview metadata column

- wrapped the timing line in `app/templates/pages/research_player.html` with a dedicated `pm-player-transcript__time-wrap` element so the visual inset can be controlled separately from the badge pill
- changed `.pm-player-transcript__meta` in `app/static/css/30_components.css` from a flat flex row to a compact grid stack with the badge above the timing
- kept the existing badge weighting: participant stays stronger than interviewer, with no new role semantics or color system

### Row height and alignment

- tightened `.pm-player-transcript__row` vertical padding in `app/static/css/30_components.css`
- reduced the transcript trigger top and bottom padding so turn height follows the actual content more closely
- narrowed the left transcript metadata track slightly in `app/static/css/20_layout.css` while preserving the larger column gap to the text block
- kept the bounded interview text measure and moderate line-height for the right reading column

### Regression coverage

- updated the focused interview route regression in `app/tests/test_research_sessions.py` so it asserts the stacked metadata markup in both `de` and `en`

## Verification

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k test_player_route_renders_interview_transcript_and_reference_dialog_in_both_languages`
- browser verification on the live dev server at `http://127.0.0.1:8000` after login with the local dev admin:
  - `de`: `http://127.0.0.1:8000/de/research/spanish/player/ES-L-0009-2026-S01/interview?source=recordings&focus_segment=seg_009`
  - `en`: `http://127.0.0.1:8000/en/research/spanish/player/ES-L-0009-2026-S01/interview?source=recordings&focus_segment=seg_009`
- captured screenshots and layout metrics under:
  - `tmp/ui-qa/2026-04-21-player-interview-layout-139/de-interview.png`
  - `tmp/ui-qa/2026-04-21-player-interview-layout-139/en-interview.png`
  - `tmp/ui-qa/2026-04-21-player-interview-layout-139/qa-results.json`
- measured browser metrics for both languages confirmed:
  - `metaDisplay = grid`
  - `timeTop > speakerTop`
  - `timeLeft = speakerLeft + 9px`
  - compact trigger padding of roughly `2.56px` top and `3.84px` bottom on the active desktop render

## Notes

- the live browser validation used the already running local dev server; no route, data, popover, or playback behavior was changed in this pass