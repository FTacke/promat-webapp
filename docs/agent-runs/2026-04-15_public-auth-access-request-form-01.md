# 2026-04-15 Public Auth Access Request Form 01

## Summary

- Replaced the public mailto-based access-request flow with a persisted `/access-request` form backed by the auth/core database.
- Unified public research corpus-root naming so the sidebar language header matches the visible corpus title such as `Spanisch-Korpus` / `Spanish corpus`.
- Suppressed anonymous corpus-root CTAs for authenticated users while preserving the signed-out request-access-first, login-second order.
- Restyled the login and password-adjacent access-request hint as the same quieter shared secondary card family.

## Implementation

- Added `access_requests` persistence in `app/src/app/auth/models.py` plus `app/migrations/0008_create_access_requests.sql` and `app/migrations/0008_create_access_requests_sqlite.sql`.
- Added server-side request creation, validation, success messaging, and authenticated redirects in `app/src/app/routes/public.py`.
- Reused shared auth form/message/button families in `app/templates/auth/login.html`, `app/templates/auth/access_request.html`, `app/templates/auth/password_forgot.html`, `app/templates/auth/password_reset.html`, and `app/static/css/30_components.css`.
- Added focused regressions in `app/tests/test_auth_phase1.py` and `app/tests/test_research_sessions.py`.

## Verification

- `Run auth phase tests`
- `Run research sessions tests`
- Opened the real routes in the integrated browser for `de` and `en` on:
  - `/de/research/spanish`
  - `/login?ui_lang=de`
  - `/access-request?ui_lang=de`
  - `/en/research/spanish`
  - `/login?ui_lang=en`
  - `/access-request?ui_lang=en`

## Notes

- The browser tooling in this run could open the routes but did not expose page contents or screenshots because `workbench.browser.enableChatTools` was not available.