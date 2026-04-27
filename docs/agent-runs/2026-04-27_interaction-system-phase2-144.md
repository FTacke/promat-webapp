# 2026-04-27 · Interaction-System Phase 2 · Run 144

## Scope

- Continued the productive migration from legacy `pm-research-button` and `pm-research-inline-action` usage toward semantic action buttons, navigation pills, CTA links, and unchanged chip or selection families.
- Migrated shared research surfaces already touched in phase 2 through to green tests, then extended the migration into the productive player/profile slice and the auth, account, and admin surfaces.
- Kept selection-style controls such as chips and player task selectors separate from the button hierarchy instead of flattening them into generic buttons.
- Updated `sample` wherever the changed productive layout elements are mirrored.

## Implementation

- Kept the active interaction-system rule in `docs/spec/platform-data-files.md` aligned with the productive semantic families.
- Extended `app/templates/partials/_pm_interactions.html` and shared component CSS so navigation pills can carry an explicit primary or secondary variant while CTA links still remain distinct from pill chrome.
- Migrated productive landing, corpus-card, research-root, speaker-card, filter, recordings, profile, and player entry actions to the semantic interaction families.
- Migrated auth login, access request, password-forgot, password-reset, account, and account-password surfaces so submit flows use action buttons and cross-links use navigation pills.
- Migrated admin-users toolbar and dialog actions to semantic action buttons while leaving the inactive filter as a chip-style toggle.
- Migrated the remaining comparison clear-filter action, the phenomena overview/editor controls, and the old player-stub navigation so the legacy generic action families no longer remain on productive template surfaces.
- Updated focused regressions in `app/tests/test_research_sessions.py` and `app/tests/test_auth_phase1.py` so they assert the new visible control families and ordering.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_auth_phase1.py -q`
- Started a fresh local listener on `http://127.0.0.1:8010` with `AUTH_DATABASE_URL=postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:55432/promat_auth`.
- Opened `http://127.0.0.1:8010/login?ui_lang=de` in the integrated browser.
- Fetched live HTML for `http://127.0.0.1:8010/login?ui_lang=de`, `http://127.0.0.1:8010/login?ui_lang=en`, `http://127.0.0.1:8010/access-request?ui_lang=de`, and `http://127.0.0.1:8010/en/sample` to verify the migrated controls on the active listener.

## Notes

- Protected account and admin routes were validated through the focused auth pytest coverage in this run; no browser login automation or screenshot capture tool was available in the current environment.
- The remaining legacy interaction usage is now tracked explicitly in `docs/agent-runs/2026-04-27_interaction-system-phase2-legacy-audit-145.md` instead of being left implicit.
- The live listener on port `8010` used the same PostgreSQL override to port `55432` that was already required earlier in this workspace.
- A final template grep showed only one remaining legacy class usage: the player transport toggle on `app/templates/pages/research_player.html`, which remains a workbench-specific media control rather than a generic semantic action.
