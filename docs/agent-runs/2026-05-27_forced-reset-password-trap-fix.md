# Forced Reset Password Trap Fix

## 1. Scope

This run fixed the repository-side forced-reset password trap reported from production.

No server runtime, SSH, production database, nginx, certbot, monitoring, mounts, Docker runtime, secrets, or other applications were touched. The temporary server-side operator workaround was not executed from this local repo session.

## 2. Root Cause

Production uses cookie-based JWT auth with `JWT_COOKIE_CSRF_PROTECT=True`.

The forced-reset account password page rendered a normal HTML form that posted to `/auth/account/password`, but the form did not include the JWT double-submit CSRF value. In production, that means the POST can be rejected before the password-change service runs, leaving `must_reset_password=True`.

A second trap remained after a successful password change: the database flag could be cleared, but the browser still held the old access JWT whose claims contained `must_reset_password=true`. The global redirect guard reads that token claim, so a stale token could keep redirecting the user back to `/auth/account/password?mustReset=1`.

## 3. Fix

Implemented:

- enabled JWT CSRF form-field support through `JWT_CSRF_CHECK_FORM=True`;
- rendered the JWT access CSRF value as a hidden field on the protected account password HTML form;
- rendered the same hidden field on the protected account details HTML form, which uses the same cookie-JWT POST boundary;
- preserved the originally requested protected target when the forced-reset guard redirects to the password page;
- after successful account password change, refreshed the access JWT cookie from the updated user record so `must_reset_password=false` is reflected immediately;
- kept JSON/API behavior intact and continued to reject missing or invalid JWT CSRF.

No CSRF protection was disabled or weakened.

## 4. Changed Files

| File | Change |
|---|---|
| `app/src/app/config/__init__.py` | Enabled JWT form CSRF checking. |
| `app/src/app/__init__.py` | Forced-reset redirect now preserves the originally requested protected target as `next`. |
| `app/src/app/routes/auth.py` | Added JWT CSRF hidden-field context and refreshed access cookies after successful password changes. |
| `app/templates/auth/account_password.html` | Added JWT CSRF hidden input and preserved `next` hidden input. |
| `app/templates/pages/account.html` | Added JWT CSRF hidden input for the protected account-details POST form. |
| `app/tests/test_auth_phase1.py` | Added production-like cookie-JWT-CSRF regression tests for forced reset and normal account password changes. |

## 5. Tests

Commands run:

```powershell
.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py -q -k "forced_reset or account_password_change"
```

Result: `7 passed, 67 deselected`.

```powershell
.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py -q -k "forced_reset or account_password_change or account_page_renders_real_account_surface"
```

Result: `8 passed, 66 deselected`.

```powershell
.venv\Scripts\python.exe -m ruff check app/src/app/config/__init__.py app/src/app/__init__.py app/src/app/routes/auth.py app/tests/test_auth_phase1.py
```

Result: `All checks passed!`

```powershell
.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q
```

Result: `79 passed`.

```powershell
python -m compileall app
```

Result: passed.

```powershell
.venv\Scripts\python.exe -m pytest app/tests -q
```

Result: `487 passed, 80 warnings`.

```powershell
git diff --check
```

Result: no whitespace errors; Git reported existing CRLF normalization warnings only.

## 6. Regression Coverage

New coverage proves:

- a user with `must_reset_password=True` can log in and is redirected to the forced-reset page;
- the forced-reset form includes `csrf_token`;
- the forced-reset form omits the current-password field;
- the forced-reset POST succeeds with a valid JWT CSRF form value;
- the database flag becomes `must_reset_password=False`;
- the response refreshes the access JWT cookie;
- the next request to `/admin/users/page` is not trapped back on the password page;
- the old password fails after logout;
- the new password works after logout/login;
- normal account password change still works with cookie-JWT-CSRF enabled;
- missing or invalid JWT CSRF does not update the password.

## 7. Deployment Note

After this change is deployed to production, verify:

1. create or mark a test account with `must_reset_password=True`;
2. log in through the browser;
3. confirm the forced-reset form submits successfully;
4. confirm the user lands on the intended protected page or account page;
5. confirm a reload does not redirect back to `/auth/account/password?mustReset=1`;
6. confirm old-password login fails and new-password login succeeds.

Users who were already trapped with stale cookies should reopen the browser or clear cookies for `pronunciation-matters.de` before retesting.

## 8. No-Go Confirmation

- no SSH
- no server runtime changes
- no production DB access
- no secrets
- no nginx/certbot/monitoring/mount changes
- no Docker runtime changes
- no auth weakening
- no global CSRF disabling
- no password/hash logging
- no Teaching/content changes
