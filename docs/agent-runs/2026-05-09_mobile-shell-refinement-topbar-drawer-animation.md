# 2026-05-09 Mobile Shell Refinement Topbar Drawer Animation

## Scope

- Refine the compact mobile language switch in the topbar.
- Pull the drawer brand higher and make it use the wordmark treatment.
- Push account and appearance utilities to the lower utility zone.
- Add a calm left-to-right drawer animation with matching close behavior and reduced-motion handling.

## Changes

- Reduced the visual weight of the visible mobile `DE | EN` control by removing the heavy pill treatment on mobile while keeping the compact switch visible in the topbar.
- Tightened the 320-360 px topbar spacing and removed the mobile accent-span ellipsis so the one-line `Pronunciation Matters` wordmark remains visible without a second row.
- Reworked the modal drawer structure into a top wordmark, a main navigation block, a current-area block, and a bottom utility zone.
- Moved account/login utilities into a compact inline utility row at the bottom of the drawer.
- Simplified the drawer theme control to an icon-sized secondary utility button rather than a full-width action row.
- Added modal-drawer open and close state classes, transform-based slide-in or slide-out motion, matching backdrop fade, focus return to the burger button, and reduced-motion-aware timing.
- Changed initial drawer focus from the brand link to the first main navigation entry.

## Validation

- Started the local app with `./scripts/dev-start.ps1`.
- Ran `node ./tmp/mobile_audit.mjs` after the refinement pass.
- Ran focused Edge-CDP checks for:
  - 320 px topbar on research design and login
  - 320 px open or close drawer behavior on research design
  - 320 px reduced-motion drawer open or close behavior
  - desktop design topbar state
- Ran focused pytest checks:
  - `python -m pytest app/tests/test_research_sessions.py -q -k research_language_root_shows_muted_locked_entries_for_signed_out_users`
  - `python -m pytest app/tests/test_auth_phase1.py -q`

## Notes

- The focused auth pytest run still ends with the existing unrelated English landing-copy failure.
- Admin offscreen findings remain intentional because admin tables keep their explicit horizontal scroll containers.