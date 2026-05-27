# Account Password Change + Admin Recovery Fix

## 1. Scope

This run fixed two repository-side issues:

- the authenticated account password-change path did not have a proven atomic persistence path;
- `app/scripts/create_initial_admin.py` coupled admin recovery to optional curated research test-set setup.

No server runtime, secrets, Docker runtime, nginx, certbot, monitoring, production database, runner, mounts, or Teaching/content files were touched.

## 2. Root Cause

### Account Password Change

The password reset/invitation path already persisted password changes correctly through the shared password-update helper. The authenticated account password-change route verified the current password on a loaded user object and then called the lower-level password-update helper separately. That path had no regression test proving that logout plus old-password failure plus new-password login worked.

The fix adds an authenticated password-change service that verifies the current password and writes the new official password hash in one database session, then routes both HTML and JSON password-change posts through that service.

### Admin Recovery Script

`create_initial_admin.py` successfully created or updated the admin user, but then always attempted to create the curated research test set. In production recovery this could fail after admin success when optional research-player task catalog directories were not present, causing a non-zero script exit.

The curated test-set step is now opt-in through `--ensure-curated-test-set`; normal admin recovery does not depend on research-player catalog resources.

## 3. Changed Files

| File | Change |
|---|---|
| `app/src/app/auth/services.py` | Added `change_user_password()` to verify current password and persist the new hash atomically; added explicit flush in password update helper. |
| `app/src/app/routes/auth.py` | Routed authenticated HTML and JSON password-change flows through `change_user_password()`. |
| `app/scripts/create_initial_admin.py` | Made curated test-set creation explicit opt-in via `--ensure-curated-test-set`; removed unconditional import/call. |
| `app/tests/test_auth_phase1.py` | Added regression coverage for successful account password change, old-password rejection, new-password login, wrong-current-password rejection, confirmation mismatch rejection, status-guard preservation, admin-role preservation, and script opt-in guard. |

## 4. Tests

Commands run:

```powershell
.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py -q -k "account_password_change or create_initial_admin_curated or login_status_guards or password_reset_updates"
```

Result: `6 passed, 64 deselected`.

```powershell
.venv\Scripts\python.exe -m ruff check app/src/app/auth/services.py app/src/app/routes/auth.py app/scripts/create_initial_admin.py app/tests/test_auth_phase1.py
```

Result: `All checks passed!`

```powershell
python -m compileall app
```

Result: passed.

```powershell
.venv\Scripts\python.exe app/scripts/create_initial_admin.py --help
```

Result: passed; help output includes `--ensure-curated-test-set`.

```powershell
.venv\Scripts\python.exe -m pytest app/tests -q
```

Result: `483 passed, 80 warnings`.

```powershell
git diff --check
```

Result: no whitespace errors; Git reported existing CRLF normalization warnings only.

## 5. Production Recovery Status

`create_initial_admin.py` is now safe for production admin recovery by default. Running it to create or update the admin user no longer requires `data/config/research_player/spanish/task_catalogs` or any other curated research test-set resources.

The optional curated test-set behavior remains available for dev/test use:

```powershell
python app/scripts/create_initial_admin.py --ensure-curated-test-set ...
```

Do not use that flag for emergency admin recovery unless the curated research-player resources are intentionally present.

## 6. Deployment Notes

- No database migration is required.
- No secrets were added or printed.
- No production data access was performed.
- After deploying this code, the authenticated account password-change page should allow an admin or normal user to change their password, log out, fail login with the old password, and log in with the new password.

## 7. No-Go Confirmation

- no server changes
- no SSH
- no production database access
- no secrets
- no auth weakening
- no global CSRF changes
- no password/hash logging
- no UI redesign
- no Teaching/content changes
