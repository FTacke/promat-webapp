# 2026-04-27 · Interaction Legacy Cleanup · Run 154

## Scope

- Removed the remaining productive legacy interaction-class usage from the player template and the active runtime-JS render paths.
- Kept the player transport toggle as a player-specific control instead of forcing it into the generic semantic action-button family.
- Updated the existing legacy audit so it no longer claims an outdated single remaining template case.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/agent-runs/2026-04-27_interaction-system-phase2-legacy-audit-145.md`
- `app/templates/pages/research_player.html`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-comparison.js`
- `app/static/js/auth/admin_users.js`
- `app/tests/test_research_sessions.py`
- `app/tests/test_auth_phase1.py`

## Implementation

- Updated `app/templates/pages/research_player.html` so the transport toggle no longer uses `pm-research-button`; it now uses the dedicated player-specific class `pm-player-control-button` together with the existing icon-button styling.
- Updated `app/static/css/30_components.css` with the minimal button-reset behavior for `pm-player-control-button` (`appearance: none`, pointer cursor, inherited font) so the player transport control is no longer coupled to the retired generic button family.
- Updated `app/static/js/pages/research-comparison.js` so:
  - fallback status actions render with semantic secondary action-button classes,
  - material/task selector buttons render as plain `pm-material-choice` controls instead of inheriting retired inline-action classes.
- Updated `app/static/js/auth/admin_users.js` so the runtime-rendered toast close action and per-row edit action now use semantic secondary action-button classes instead of retired inline-action classes.
- Updated `app/tests/test_research_sessions.py` and `app/tests/test_auth_phase1.py` with focused regressions for the cleaned player, comparison-JS, and admin-JS paths.
- Updated `docs/agent-runs/2026-04-27_interaction-system-phase2-legacy-audit-145.md` so it now reflects that no productive template or runtime-JS usage of `pm-research-button` / `pm-research-inline-action` remains.

## Key Decisions

- The player transport toggle stays a specialized media control. The cleanup removed the legacy class dependency but did not relabel it as a generic semantic action button, which would blur the distinction between workbench media controls and ordinary actions.
- The comparison material selector continues to use the dedicated `pm-material-choice` family as the correct selection control rather than migrating into the button hierarchy.
- The retired legacy class rules may remain temporarily in shared CSS as a compatibility layer until a later deletion pass removes dead styling safely.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py app/tests/test_auth_phase1.py -q -k "player_route_renders_wordlist_runtime_and_profile_back_link or research_comparison_static_js_uses_non_legacy_control_classes or admin_users_static_js_uses_semantic_action_button_classes"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_auth_phase1.py -q`
- Repo grep after the change found no remaining `pm-research-button` or `pm-research-inline-action` usage in productive templates under `app/templates/` or productive runtime JS under `app/static/js/`.

## Notes

- This run cleaned productive usage and audit accuracy, not the shared compatibility CSS layer itself.
- If a later deletion pass removes the retired CSS rules, it should repeat the same grep step first and then validate any non-productive or fallback paths that may still rely on them.
