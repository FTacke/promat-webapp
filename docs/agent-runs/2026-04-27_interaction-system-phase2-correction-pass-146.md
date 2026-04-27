## Summary

- Corrected the post-migration interaction-system details on shared macros, shared CSS, and the affected auth, player, profile, landing, and sample surfaces.
- Removed hardcoded arrow characters from localized labels and landing-card content so CTA links and forward navigation pills render exactly one arrow through the shared component layer.
- Added an explicit back-direction navigation-pill variant with a leading left arrow and no trailing forward arrow.
- Restored compact intrinsic-width behavior for login-side actions, card CTAs, speaker-profile pills, account security navigation, and the player back action.
- Added leading add/remove icons to player comparison actions so comparison stays in the action-button family without navigation-arrow semantics.

## Files Changed

- app/templates/partials/_pm_interactions.html
- app/static/css/30_components.css
- app/static/css/40_cards.css
- app/templates/auth/login.html
- app/templates/auth/password_forgot.html
- app/templates/auth/password_reset.html
- app/templates/auth/account_password.html
- app/templates/pages/research_player.html
- app/templates/pages/research_player_stub.html
- app/templates/pages/research_speaker_profile.html
- app/templates/pages/sample_page.html
- app/src/app/i18n.py
- app/src/app/routes/public_content.py
- app/tests/test_auth_phase1.py
- app/tests/test_research_sessions.py
- docs/spec/platform-data-files.md

## Validation

- `pytest app/tests/test_auth_phase1.py -q` -> 22 passed.
- `pytest app/tests/test_research_sessions.py -q` -> 173 passed.
- Live runtime validation on `http://127.0.0.1:8000` after restart via `scripts/dev-start.ps1`.
- Verified live HTML for the affected pages:
  - login uses `pm-auth-action-link` plus `pm-action-button--tertiary` for `Passwort vergessen?`
  - sample contains the back-pill variant class `pm-nav-pill--back`
  - sample no longer contains the broken `Seite öffnen → →` pattern
  - research root no longer contains duplicated CTA label-arrow strings

## Notes

- The local dev startup again fell back from PostgreSQL host port `54321` to `55432`; the existing dev-start fallback handled that automatically.
- The available tools allowed live runtime HTML checks, but not browser screenshots inside this run.
