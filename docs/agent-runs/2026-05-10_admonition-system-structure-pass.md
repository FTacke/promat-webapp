# 2026-05-10 Admonition System Structure Pass

## Scope

- Removed the extra panel indent from the shared admonition shell.
- Increased admonition title and body typography to a larger reading size.
- Made admonition icons more prominent by enlarging the shared icon token sizes and icon box.

## Changes

- Updated the shared admonition token block in `app/static/css/00_tokens.css` so title and body text now use a larger scale, and icon sizing is based on a larger shared box/token pair.
- Removed `padding-inline-start: var(--pm-admonition-panel-indent);` from the shared admonition panel rule in `app/static/css/40_cards.css` and dropped the now-unused indent token.
- Left the admonition DOM and variant model layout-free; the visible change stays in shared tokens and shared shell geometry only.

## Validation

- Focused regression test: `pytest app/tests/test_research_sessions.py -q -k sample_page` -> `10 passed`
- Browser validation through a local Selenium/Edge probe on real routes:
  - `/de/sample`
  - `/en/sample`
  - `/en/research`
- Verified computed states in the browser probe:
  - title font token remains the UI font
  - body font token remains the reading font
  - title size token resolves to a larger clamp around 1.1rem
  - body size token resolves to 1.08rem
  - icon box resolves to 32px and the icon mask remains data-token driven
  - panel inline-start padding resolves to `0px`
  - collapsible `weiterlesen` toggles `aria-expanded` and `hidden` correctly
- Screenshot artifacts were written to `tmp/ui-qa/admonition-system-pass/` for the German sample, English sample, and English research route.

## Notes

- `get_errors` still reports pre-existing CSS compatibility warnings elsewhere in `app/static/css/40_cards.css` and `app/static/css/10_typography.css`; no new warning was introduced by this pass.
