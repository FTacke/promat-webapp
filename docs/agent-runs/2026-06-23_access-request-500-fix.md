# 2026-06-23 Access Request 500 Fix

## Context

After the PRG fix in `bc5ffd2` (2026-06-22), a live submission at 2026-06-23T10:07:46Z still produced a 500 error despite the mail being delivered successfully and the DB record being created (Request ID: b3d8d624-c25c-4061-a478-d93b1dffe235).

## Root cause

In `deliver_access_request_notification`, the call to `_update_request_status(message.request_id, "notified")` was placed **outside** the `try/except` block. If the DB status update failed (e.g. transient connection error) after mail delivery had already succeeded, the exception would propagate uncaught through `access_request_submit` and Flask would return a 500. The user saw a 500 error but the mail was already sent.

```python
# Before (bug): status update outside try block
try:
    _deliver_with_configured_backend(message)
except Exception:
    _update_request_status(..., "notification_failed")
    return False

_update_request_status(..., "notified")  # ← propagated if DB fails → 500
```

## Fix

Moved both the "notified" update and its log call **inside** the try block. The `except` block now wraps its own status update in a nested `try/except` so a DB failure during failure-marking cannot mask the outer exception.

```python
# After (fixed):
try:
    _deliver_with_configured_backend(message)
    _update_request_status(..., "notified")   # inside try
    return True
except Exception as exc:
    try:
        _update_request_status(..., "notification_failed")
    except Exception:
        pass
    ...
    return False
```

## Confirmation text update

The user also specified updated confirmation page copy (title and body), matching the wording from their specification:

| Key | DE (before) | DE (after) |
|-----|-------------|------------|
| `submitted_heading` | "Anfrage übermittelt" | "Anfrage eingegangen" |
| `submitted_body` | "Wir prüfen den Antrag und senden Ihnen ..." | "Sofern der Antrag als legitim eingestuft wird, erhalten Sie innerhalb von 72 Stunden ..." |
| `submitted_spam_hint` | *(new key)* | "Bitte prüfen Sie auch Ihren Spam-Ordner." |

| Key | EN (before) | EN (after) |
|-----|-------------|------------|
| `submitted_heading` | "Request Submitted" | "Request received" |
| `submitted_body` | "We will review it and send access credentials ..." | "If the request is considered legitimate, you will receive access credentials or further information by email within 72 hours." |
| `submitted_spam_hint` | *(new key)* | "Please also check your spam folder." |

The template (`auth/access_request.html`) was updated to render the new `submitted_spam_hint` paragraph below the main body text.

## Tests added / updated

- `test_access_request_submit_persists_request_and_shows_success` — updated assertions to match new heading/spam hint
- `test_access_request_submitted_page_shows_de_confirmation` — updated assertions
- `test_access_request_submitted_page_shows_en_confirmation` — updated assertions + added "spam folder" check
- **new** `test_access_request_submit_en_shows_english_confirmation` — full POST→303→GET flow for English UI
- **new** `test_access_request_submit_does_not_500_when_status_update_fails` — monkeypatches `_update_request_status` to raise on "notified"; asserts 303 (not 500) and confirmation page still renders

## Files changed

| File | Change |
|------|--------|
| `app/src/app/services/access_request_notifications.py` | Status update moved inside try block; nested try around failure-path update |
| `app/src/app/i18n.py` | Updated `submitted_heading` and `submitted_body` (DE + EN); added `submitted_spam_hint` (DE + EN) |
| `app/templates/auth/access_request.html` | Renders `submitted_spam_hint` as additional paragraph |
| `app/tests/test_auth_phase1.py` | Updated 3 existing tests; added 2 new tests |

## Test result

759 passed, 15 failed (all pre-existing: corpus_root, Spanish design, comparison labels, teaching). No regressions.
