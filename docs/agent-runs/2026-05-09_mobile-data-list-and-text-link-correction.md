# 2026-05-09 Mobile Data List And Text Link Correction

## Scope

- Restore compact mobile list and table behavior for structured data surfaces after the earlier mobile P0 pass.
- Keep the useful shared shell, touch-target, root-grid, footer, overlay, and explicit table-scroll fixes from the previous run.
- Correct the player wordlist row layout, generic table cardization, over-tall speaker cards on narrow mobile widths, and text-like profile-link styling.

## Changes

- Restored the mobile wordlist player row to a compact list structure instead of collapsing the number badge above a full-width block.
- Kept player item text wrappable inside the row while leaving the download action in the same compact row structure.
- Removed the generic mobile `pm-research-table` block/card decomposition so admin, analytics, speaker, and comparable structured tables stay tables inside local scroll containers.
- Added a dedicated inline text-link component for compact profile and meta links so they no longer inherit CTA min-height or pseudo-underline geometry.
- Switched productive speaker profile links and their mirrored sample links onto that inline text-link family.
- Densified speaker cards on small widths by keeping metadata in a tighter two-column rhythm and reducing excess internal spacing.
- Kept the earlier explicit admin table scroll hints and scroll containers intact.

## Validation

- `node .\tmp\mobile_audit.mjs`
  - Final artifact: `tmp/mobile-audit-1778312596699`
- Final 320 px metric checks from `tmp/mobile-audit-1778312596699/audit-results.json`
  - `research-player`: `off=0`, `small=3`
  - `admin-users`: `off=20`, `small=0` because the table stays intentionally horizontally scrollable
  - `admin-analytics`: `off=20`, `small=0` because the tables stay intentionally horizontally scrollable
  - `research-speakers`: `off=0`, `small=20`
  - `research-root`: `off=0`, `small=0`
  - `teaching-root`: `off=0`, `small=0`
  - `login`: `off=0`, `small=1`
  - `access-request`: `off=0`, `small=1`
  - `research-comparison`: `off=0`, `small=2`
  - `research-phenomena`: `off=0`, `small=2`
- `pytest app/tests/test_research_sessions.py -q -k research_language_root_shows_muted_locked_entries_for_signed_out_users`
  - Passed.
- `pytest app/tests/test_auth_phase1.py -q`
  - 44 passed, 1 failed.
  - Failing test: existing English landing-copy assertion unrelated to this mobile list/text-link correction.

## Notes

- The admin pages still report offscreen elements in the audit because the tables are intentionally wider than the viewport and now remain inside explicit local scroll containers instead of degrading into per-row cards.
- The remaining `small` hits on `research-player`, `login`, `access-request`, `research-comparison`, and `research-phenomena` are breadcrumb-sized inline links rather than broken primary controls.
- The remaining `small` hits on `research-speakers` come from intentionally compact segmented controls, profile text links, and task pills inside the card view; the page is visually denser and more scanable than the previous oversized mobile card state, but a later run could still decide whether the default mobile speaker view should shift further toward table/list behavior.