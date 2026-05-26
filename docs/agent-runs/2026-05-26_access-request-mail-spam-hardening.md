# 2026-05-26 Access Request Mail And Spam Hardening

## Scope

- Implement the re-audit findings limited to the public access-request flow plus the remaining small P0/P1 auth or runtime gaps.
- Keep scope out of teaching, broader UI refactors, content work, and unrelated production cleanup.

## Changes

- Added configurable server-side access-request notification delivery in `app/src/app/services/access_request_notifications.py` using plain-text operator mail, a fixed configured sender, and applicant email only as validated `Reply-To`.
- Extended auth runtime config in `app/src/app/config/__init__.py` with access-request mail settings, anti-bot timing and token settings, and TLS/SSL validation for the SMTP transport.
- Split the public access-request route in `app/src/app/routes/public.py` into GET and POST handlers, added route-specific submit limits, a honeypot, a signed form-age token, suspicious-submit no-op handling, metadata-only logging, and a fix so an explicit `AUTH_ACCESS_REQUEST_MIN_SUBMIT_SECONDS=0` remains valid in tests.
- Updated `app/src/app/auth/services.py` to log only request metadata when persisting access requests.
- Updated `app/templates/auth/access_request.html` and `app/src/app/i18n.py` for the hidden anti-bot fields and the invalid-input error copy.
- Wired the production environment in `app/infra/docker-compose.prod.yml` and `app/passwords.env.template` for access-request mail settings and switched the web healthcheck to a Python `urllib` probe that exists in the image.
- Expanded `app/tests/test_auth_phase1.py` with token-aware access-request helpers plus focused regressions for notification delivery, notification failure, honeypot and timing guards, route throttling, invalid input rejection, privacy-safe logging, admin reset logging secrecy, and admin PATCH or reset rate limits.
- Kept the active runtime spec aligned in `docs/spec/platform-data-files.md` with the new operator-mail and abuse-guard contract for `/access-request`.

## Validation

- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q` -> `64 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -q` -> `201 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m compileall app` completed successfully
- `docker compose -f app/infra/docker-compose.prod.yml config` rendered successfully with placeholder required environment values for interpolation

## Notes

- The first focused test rerun exposed a local defect where the access-request timing guard used `or 0.5`; this run corrected that slice to treat explicit zero values as intentional configuration instead of falling back to the default.
- The compose validation needed placeholder values for the required secrets because the production file intentionally uses fail-fast `${VAR:?}` interpolation.