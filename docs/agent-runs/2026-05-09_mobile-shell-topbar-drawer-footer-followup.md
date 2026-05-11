# 2026-05-09 Mobile Shell Topbar/Drawer/Footer Follow-up

## Scope

- Simplify the shared mobile topbar to burger, single-line brand, and language switch.
- Turn the mobile drawer into the full mobile navigation surface instead of a local-nav fragment.
- Compress the mobile footer into a calm meta footer.
- Keep earlier Mobile-P0 overflow, grid, and data-surface fixes intact.

## Changes

- Moved mobile-only theme and account or login access out of the visible topbar and into the drawer while keeping desktop topbar behavior intact.
- Reworked the modal drawer so it now renders four labeled blocks: main navigation, current area, account, and appearance.
- Added drawer-specific section labels, block dividers, context title rendering, and a drawer theme toggle that reuses the same theme state as the topbar toggle.
- Tightened the 320-360 px topbar spacing so the mobile bar stays on one calm row with burger, `Pronunciation Matters`, and `DE | EN`.
- Raised drawer navigation rows to the 44 px touch-target floor via the shared nav-item token.
- Reduced the mobile footer to `© 2026 Philipps-Universität Marburg` plus inline `Impressum · Datenschutz`, while hiding larger footer branding, version, and secondary attribution on narrow widths.
- Kept footer legal links typographic instead of treating them as button-like 44 px action blocks.

## Validation

- Started the local app with `./scripts/dev-start.ps1` from the repo root.
- Ran `node ./tmp/mobile_audit.mjs`.
- Ran focused Edge-CDP shell checks for:
  - 320 px topbar and footer on research design, login, and admin users
  - 320 px opened drawer on research design and admin users
  - 1440 px desktop shell on research design, login, and admin users
- Final key artifacts:
  - `tmp/mobile-audit-1778313276253/audit-results.json`
  - `tmp/shell-check-1778313611687/`
  - `tmp/shell-topbar-check-1778313679641/mobile-topbar-320.png`

## Notes

- The landing page remains the existing shell exception and still uses the compact landing language utility instead of the full shared topbar.
- Admin table offscreen findings in the mobile audit remain intentional because those tables stay in explicit horizontal scroll containers.
- The mobile audit continues to report small breadcrumb and compact-card targets on some pages; this run only changed the shared shell, not those separate local control families.