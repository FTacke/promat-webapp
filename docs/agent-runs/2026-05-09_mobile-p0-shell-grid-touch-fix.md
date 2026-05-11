# 2026-05-09 Mobile P0 Shell Grid Touch Fix

## Scope

- Shared mobile shell stabilization in `layout.css`, `00_tokens.css`, and `30_components.css`
- Mobile-safe research and teaching root card grids in `20_layout.css`
- Controlled admin table scrolling plus visible hints in `admin_users.html` and `admin_analytics.html`
- Bilingual hint strings in `app/src/app/i18n.py`
- Spec update for shared mobile shell, touch targets, root-card grids, footer behavior, and explicit table scrolling

## Changes

- Added shared mobile tokens for touch targets, topbar action sizing, mobile page padding, section spacing, grid gap, overlay width, form-control minimum block size, and footer link minimum block size.
- Removed body-level `overflow-x: clip` from the shared app shell so responsive defects are no longer masked globally.
- Switched the shared corpus-card grid to a mobile-safe single-column collapse for small widths.
- Reflowed the mobile topbar so utilities can wrap below the brand while keeping the canonical order language, theme, then account/login.
- Raised shared topbar controls, buttons, chips, nav pills, CTA links, form fields, footer links, and auth checkbox controls to the mobile touch-target floor where they are primary controls.
- Constrained shared overlays and popovers with a mobile-safe max inline size.
- Added explicit admin table scroll wrappers, gradient edge affordance, and bilingual visible scroll hints on small screens.
- Let player control groups wrap instead of forcing narrow offscreen clusters.
- Raised dense workbench mini-controls such as material choices, comparison filter chips, inline-help triggers, session pickers, and player icon buttons to the shared mobile touch floor, and removed closed overflow bodies from layout participation.

## Validation

- `pytest app/tests/test_research_sessions.py -q -k research_language_root_shows_muted_locked_entries_for_signed_out_users`
  - Passed.
- `pytest app/tests/test_auth_phase1.py -q`
  - 44 passed, 1 failed.
  - Failing test: English landing-copy assertion unrelated to this mobile shell run.
- Repeated Edge-CDP mobile audits with `node .\tmp\mobile_audit.mjs`
  - Final artifact: `tmp/mobile-audit-1778310401772`
  - Earlier comparison artifacts kept separately under `tmp/mobile-audit-1778309082813`, `tmp/mobile-audit-1778309437745`, `tmp/mobile-audit-1778309613695`, `tmp/mobile-audit-1778309762436`, and `tmp/mobile-audit-1778310213464`
- Final 320 px metric checks from `tmp/mobile-audit-1778310401772/audit-results.json`
  - `research-root`: `off=0`, `small=0`
  - `teaching-root`: `off=0`, `small=0`
  - `login`: `off=0`, remaining `small=1` from breadcrumb link only
  - `access-request`: `off=0`, remaining `small=1` from breadcrumb link only
  - `admin-users`: `off=20`, `small=0` because the table stays intentionally horizontally scrollable
  - `admin-analytics`: `off=20`, `small=0` because the tables stay intentionally horizontally scrollable
  - `research-comparison`: `off=0`, remaining `small=2` from breadcrumb links only
  - `research-phenomena`: `off=0`, remaining `small=2` from breadcrumb links only
  - `research-player`: `off=0`, remaining `small=4` from breadcrumb links plus one near-threshold `43x44` player toggle

## Notes

- The admin pages still report offscreen elements in the audit because the tables are wider than the viewport by design and now live inside explicit scroll containers instead of being hidden by global clipping.
- The remaining small-target hits after the final pass are breadcrumb text links plus one near-threshold player toggle button; no remaining audited workbench page at 320 px reports offscreen overflow.