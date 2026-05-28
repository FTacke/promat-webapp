# 2026-05-28 Layout UX Token Pass

## Scope

- Tightened the admin user table layout with tokenized column widths, compact cell rhythm, dynamic scroll-edge hints, email ellipsis/title access, and responsive icon-only edit actions.
- Reworked admin status and role badges through shared semantic tokens.
- Changed research corpus cards to count distinct `native_speaker` person IDs and updated singular/plural reference-speaker copy.
- Added mobile corpus-root link pills that reuse the shared panel item/auth metadata and preserve locked states.
- Updated landing card copy/CTA text and made the mobile hero/card layout more compact through shared landing/card tokens.

## Verification

- Browser QA via Playwright:
  - `tmp/ui-qa/2026-05-28-layout-ux/landing-desktop-de.png`
  - `tmp/ui-qa/2026-05-28-layout-ux/landing-mobile-de.png`
  - `tmp/ui-qa/2026-05-28-layout-ux/research-spanish-desktop-signedout.png`
  - `tmp/ui-qa/2026-05-28-layout-ux/research-spanish-mobile-signedout.png`
  - `tmp/ui-qa/2026-05-28-layout-ux/admin-users-desktop-de.png`
  - `tmp/ui-qa/2026-05-28-layout-ux/admin-users-mobile-de.png`
- `python -m pytest`
- `python -m ruff check .`
- `python scripts/ci_governance_checks.py`
- `python -m compileall -q src`

## Notes

- No repository-level `package.json` exists outside the virtual environment, so there is no separate frontend build command for this repo state.
- The capability test for default surface modes now isolates its runtime root so local imported corpus data cannot make a default-placeholder assertion depend on the developer machine state.
