# Direct Mail Sendmail Backend

## Scope

Implemented repo-only mail delivery changes for ProMat access-request notifications and admin invitation/reset emails. No server runtime, secrets, Docker runtime, nginx, certbot, monitoring, databases, mounts, Teaching content, or production data were touched.

## Root Cause / Need

The existing access-request notification path was SMTP-only. Production host checks showed local mail tooling (`sendmail`/Exim) is available, while no local SMTP listener was confirmed. Admin invitation/reset handling prepared copyable link, subject, and body but had no direct send action.

## Changes

- Added `app/src/app/services/mail_delivery.py` with a shared mail abstraction:
  - backends: `disabled`, `smtp`, `sendmail`
  - safe RFC 5322 text/plain UTF-8 message generation
  - header injection rejection
  - conservative recipient validation
  - `subprocess.run([...], input=..., timeout=...)` sendmail execution without `shell=True`
- Routed access-request notifications through the shared mail service while preserving the existing test/manual sender hook.
- Added explicit admin invitation/reset send endpoint: `POST /admin/users/<user_id>/send-invite`.
- Added a primary `E-Mail senden` / `Send email` action to the existing admin prepared-mail dialog.
- Kept manual copy fallback for link, subject, and body on both success and failure paths.
- Updated invitation/reset preview copy so the contact line uses the authenticated triggering admin email.
- Added common mail config keys and kept legacy access-request SMTP keys.
- Updated active platform spec and production prep notes for sendmail, SMTP, disabled mode, and Reply-To rules.

## Behavior

- Access request:
  - direct mail respects `AUTH_ACCESS_REQUEST_MAIL_ENABLED`
  - recipient is `AUTH_ACCESS_REQUEST_EMAIL`
  - sender is `AUTH_MAIL_FROM_NAME` + `AUTH_MAIL_FROM_EMAIL`
  - `Reply-To` is the requester email after form validation
- Admin invitation/reset:
  - direct send only happens through an explicit authenticated admin POST
  - CSRF protection follows the existing JWT-cookie admin fetch pattern
  - sender is `AUTH_MAIL_FROM_NAME` + `AUTH_MAIL_FROM_EMAIL`
  - `Reply-To` is the authenticated admin email
  - if direct send fails or backend is disabled, the prepared manual copy remains visible
- Logs remain metadata-only:
  - no invitation/reset token
  - no full invitation link
  - no full email body
  - no SMTP credentials or sendmail output

## Env Keys

Recommended production sendmail configuration:

```text
AUTH_MAIL_BACKEND=sendmail
AUTH_MAIL_FROM_EMAIL=<server-allowed-sender-address>
AUTH_MAIL_FROM_NAME=Pronunciation Matters Administrator
AUTH_MAIL_DEFAULT_REPLY_TO=felix.tacke@uni-marburg.de
AUTH_MAIL_SENDMAIL_PATH=/usr/sbin/sendmail
AUTH_MAIL_TIMEOUT_SECONDS=10
```

Existing SMTP keys remain supported for `AUTH_MAIL_BACKEND=smtp`.

## Tests

- `python -m pytest app/tests/test_auth_phase1.py -q` -> 83 passed
- `python -m pytest app/tests -q -k "access_request or admin or mail or auth"` -> 169 passed, 327 deselected
- `python -m pytest app/tests -q` -> 496 passed
- `python -m compileall app` -> passed
- `ruff check app/src/app/services/mail_delivery.py app/src/app/services/access_request_notifications.py app/src/app/routes/admin.py app/tests/test_auth_phase1.py` -> passed
- `ruff check .` -> passed
- `node --test app/tests/js/*.test.mjs` -> 9 passed
- `git diff --check` -> passed

## Notes

Direct invitation send and access-request send are ready for production configuration once the server env file provides a server-allowed sender address and sendmail path. SMTP remains available for a future provider-backed setup.
