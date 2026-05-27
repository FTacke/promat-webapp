# 2026-05-27 Invite mail error hardening finalization

## Scope

- Work on `main` only.
- No SMTP host hunting and no server mail configuration changes.
- Harden invite mail error handling in repository code only.
- Keep successful mail-send behavior unchanged.

## Repo hardening implemented

Updated `app/src/app/services/mail_delivery.py`:

- Added controlled wrapping in `_send_smtp(...)` for raw delivery failures:
  - `ConnectionRefusedError`
  - `TimeoutError`
  - `socket.timeout`
  - `socket.gaierror`
  - `OSError` (connect/send path)
  - `smtplib.SMTPException`
- Wrapped exceptions are re-raised as `MailDeliveryError("smtp delivery failed")`.
- No sensitive SMTP details are propagated into API responses.

Admin invite endpoint behavior:

- Existing `MailDeliveryError` handling in `POST /admin/users/<user_id>/send-invite` remains active.
- Mail delivery failures return controlled `503` JSON with manual fallback, not an unhandled `500`.
- Success path and reply-to behavior remain unchanged.

## Tests changed

Updated `app/tests/test_auth_phase1.py`:

- Added SMTP/network wrapping regression:
  - `test_smtp_backend_wraps_raw_network_errors_in_mail_delivery_error`
- Added invite endpoint regressions:
  - `test_admin_invitation_send_connection_refused_returns_controlled_error`
  - `test_admin_invitation_send_smtp_or_os_error_returns_controlled_error`
- Existing success test remains in place and green:
  - `test_admin_invitation_send_uses_admin_reply_to_and_keeps_secret_logging`

## Local test results

- Command: `python -m pytest app/tests/test_auth_phase1.py -q`
- Result: `99 passed`

## Git and CI/Deploy

- Commit: `eeffe43`
- Message: `auth: harden invite mail error handling`
- Push target: `origin main`

GitHub Actions for commit `eeffe43`:

- CI: success
  - `https://github.com/FTacke/promat-webapp/actions/runs/26533226584`
- Deploy production: success
  - `https://github.com/FTacke/promat-webapp/actions/runs/26533226581`

## Production smoke evidence

- Container log evidence for invite endpoint:
  - `POST /admin/users/<id>/send-invite?ui_lang=de` returned `200`
  - app log includes `Admin invitation email sent`
- Server mail delivery path was not altered in this run.

## Monitoring final check

Timers:

- `webapp-healthcheck-alert.timer`: enabled + active
- `webapp-healthcheck-monthly.timer`: enabled + active

Timer cadence (server output at run time):

- alert timer: last run same day, next run scheduled next morning
- monthly timer: next monthly slot scheduled

Latest monitoring log checked:

- `/srv/server_monitoring/logs/webapp_healthcheck_check_20260527_211924.log`
- Contains ProMat checks with `ProMat: OK` in app summary.
- ProMat local/public health endpoints OK in the same report.

Alert-mail status:

- Latest scheduled alert run log:
  - `/srv/server_monitoring/logs/webapp_healthcheck_alert_20260527_082422.log`
- Result line: `No FAILs on first pass; no alert mail sent.`
- No ProMat-triggered alert-mail evidence.

Additional note:

- A manual monitoring check was executed in this run to provide current confirmation independent of timer cadence.
