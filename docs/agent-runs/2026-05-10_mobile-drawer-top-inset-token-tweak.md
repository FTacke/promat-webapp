# 2026-05-10 Mobile Drawer Top Inset Token Tweak

## Scope

- Increase the shared mobile drawer top inset token slightly so the drawer body sits a bit lower without changing the overlay rule.

## Changes

- Raised `--pm-drawer-mobile-padding-top` in `app/static/css/00_tokens.css` from `1.5rem` to `1.75rem`.
- Kept the safe-area-aware `max(...)` padding rule in `app/static/css/30_components.css` unchanged.

## Validation

- `get_errors` on `app/static/css/00_tokens.css`

## Notes

- The change increases the drawer top inset by about 4px while preserving the existing safe-area behavior.
