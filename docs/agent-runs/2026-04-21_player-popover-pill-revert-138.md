# Research Player Popover Pill Revert

## Summary

- moved the interview reference popover item-number pill back into the upper eyebrow row beside the task badge
- removed the extra title-row wrapper that had placed the number beside the title label instead
- updated the active player spec and focused HTML regression to match the restored arrangement

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/research-player.md`
- `app/templates/pages/research_player.html`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`

## Spec Updates

- updated `docs/spec/research-player.md` so the interview reference popover now explicitly keeps the number pill in the upper eyebrow row with the task badge

## Implementation Notes

- restored the popover header markup in `app/templates/pages/research_player.html` to `eyebrow` plus title, with the number pill back in the eyebrow row
- removed the unused `.pm-player-reference-popover__title-row` layout rule from `app/static/css/30_components.css`
- changed the focused interview route regression in `app/tests/test_research_sessions.py` so it checks for the eyebrow structure instead of the removed title-row wrapper

## Verification

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`

## Notes

- this was a targeted visual rollback of the popover header arrangement only; no runtime data or route behavior changed