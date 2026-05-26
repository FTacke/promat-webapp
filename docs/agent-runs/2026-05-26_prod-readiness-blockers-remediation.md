# 2026-05-26 Prod Readiness Blockers Remediation

## Scope

- Fix the P0/P1 prod-readiness blockers from the 2026-05-26 audit without widening scope into unrelated UI, teaching, or content-system work.
- Keep the implementation limited to four areas: auth-message logging secrecy, production WSGI startup, multi-instance-safe rate-limit storage, and the required focused auth/research test baselines.

## Changes

- Sanitized auth and admin mail-preview logging in `app/src/app/routes/auth.py` and `app/src/app/routes/admin.py` so server logs no longer include password-reset or invite bodies, subjects, or links; the logs now keep only non-secret delivery metadata.
- Moved rate-limit storage selection into config in `app/src/app/config/__init__.py`, removed the hard-coded in-memory limiter backend from `app/src/app/extensions/__init__.py`, and added production guardrails that reject missing or `memory://` storage outside dev/testing.
- Added explicit runtime coverage in `app/tests/test_runtime_config.py` for testing defaults, production misconfiguration rejection, and valid Redis-backed production config.
- Added focused auth regressions in `app/tests/test_auth_phase1.py` to prove secret-bearing reset or invite payloads are not logged and that the affected auth/admin mutation routes remain rate-limited.
- Switched the production image in `app/Dockerfile` from the Werkzeug/dev-style app startup path to Gunicorn, and wired the production limiter backend through Redis in `app/infra/docker-compose.prod.yml` plus `app/passwords.env.template`.
- Added the Redis client dependency in `app/requirements.in` and `app/requirements.txt`.
- Updated `docs/spec/platform-data-files.md` so the active runtime contract now explicitly requires a production-grade WSGI server and a non-memory rate-limit storage backend outside dev/testing.
- Repaired the remaining focused research baseline in `app/src/app/i18n.py`, `app/src/app/research_views.py`, and `app/tests/test_research_sessions.py` by restoring spec-aligned stays labels and removing stale assertions around historical team content, DOM-synced player payload duplication, and helper-style back-link wording.

## Validation

- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q` -> `54 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -q` -> `201 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m compileall app` completed successfully

## Notes

- The research-session closeout intentionally treated `Marcela Gualotuña`, DOM-derived player sync items, and visible `Zurück` helper text as stale test assumptions rather than active implementation targets, because the current repo state and active specs do not support those older expectations.
- No broader research-routing, teaching-content, browser-QA, or UI-family work was included in this run.
