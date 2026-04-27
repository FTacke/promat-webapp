# 2026-04-27 · Auth Controls and Sidebar Pill Rollback · Run 149

## Scope

- Reverted the last sidebar menu-pill shape and padding change that made the left navigation pills read worse.
- Made the account-page input fields stretch to the card width.
- Reduced the height of the shared medium nav pill and the admin inactive-filter chip so controls like `Passwort ändern` and `Inaktive anzeigen` no longer feel oversized.

## Implementation

- Updated `app/static/css/00_tokens.css` so the shared sidebar menu-item tokens return to the previous `min-height` and vertical padding values.
- Updated the shared nav-pill and chip tokens in `app/static/css/00_tokens.css` to reduce the overall control height slightly.
- Updated `app/static/css/30_components.css` so the sidebar menu items return to full-width drawer pills instead of the recent content-width variant.
- Updated `app/static/css/30_components.css` so account-form grid items stretch and their `.pm-phenomena-field__input` fields fill the available card width.
- Reduced the admin-toolbar override that had pushed the inactive filter chip to an overly tall `2.75rem` control height.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_auth_phase1.py -q`
- Live CSS delivery check on `http://127.0.0.1:8000/static/css/00_tokens.css` and `http://127.0.0.1:8000/static/css/30_components.css` confirmed the reverted sidebar pill values plus the reduced nav-pill/chip heights and the account-grid stretch rules.

## Notes

- No active spec update was needed because this run reverted a recent visual detour and tightened existing control sizing without changing routes, labels, hierarchy, or accepted component families.
- `sample` did not need markup changes in this run because the affected behavior came from shared CSS tokens and shared component rules rather than from changed mirrored structure.
