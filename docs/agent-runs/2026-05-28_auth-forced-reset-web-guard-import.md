# Run Log: Auth Forced-Reset Web Guard Import

Date: 2026-05-28

## Scope
- Import server-prepared hotfix patch into authoritative main
- Validate auth/admin behavior with local tests and static checks
- Push to origin/main and verify workflow start

## Source
- Imported patch: `tmp/promat_auth_guard_fix_b0c0028.patch`
- Source commit in server clone metadata: `b0c0028de0359e4a0fb1caf3edf5b542f3cf4ca2`

## Applied Changes
- `app/src/app/__init__.py`
  - Forced-reset handling now distinguishes web vs JSON flows.
  - HTML and HTMX requests redirect to password reset page.
  - JSON/API requests still return controlled `password_reset_required` JSON with 403.
- `app/src/app/i18n.py`
  - Added localized error key for blocking self-targeted password invitation/reset in admin users flow.
- `app/src/app/routes/admin.py`
  - Added guard to block admin self-target invite/reset actions.
- `app/tests/test_auth_phase1.py`
  - Added regression tests for HTMX redirect, JSON response behavior, and admin self-target guard.

## Local Validation
- `python -m pytest app/tests/test_auth_phase1.py -q` -> pass (107/107)
- `python -m pytest app/tests/test_auth_phase1.py -q -k "admin and (invite or reset)"` -> pass (6 selected)
- `python -m ruff check .` -> pass
- `python scripts/ci_governance_checks.py` -> pass
- `python -m compileall -q app/src app/tests` -> pass

## Git
- Patch applied via `git am` without fallback.
- Resulting commit on main: `bed60a8`.

## CI/Deploy Observation
- Push triggered CI and Deploy production workflows for `bed60a8`.
- Public actions pages showed runs started (CI #125, Deploy production #21) at handoff time.

## Notes
- No environment files were introduced.
- No secrets, tokens, or hashes were added in the imported diff.
- Production smoke execution from this workspace remained blocked by missing production base URL and admin credentials in local environment context.
