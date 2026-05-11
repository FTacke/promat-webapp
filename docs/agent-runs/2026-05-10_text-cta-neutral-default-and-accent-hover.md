# 2026-05-10 Text CTA Neutral Default And Accent Hover

## Scope

- Unify text-style CTA links so they render in a neutral text color by default, switch to the shared brand accent only on hover and focus, and show underline only on hover and focus.
- Keep navigation, drawer, topbar, footer links, breadcrumbs, and pill or button-style actions out of scope.

## Changes

- Updated the shared CTA tokens in `app/static/css/00_tokens.css` so `.pm-cta-link--primary` and `.pm-cta-link--accent` now resolve to the same neutral default text color and the same shared brand-accent hover color.
- Updated `.pm-inline-text-link` in `app/static/css/30_components.css` to use the same neutral default plus brand-accent hover and focus treatment as shared text CTAs.
- Removed the remaining muted override for `.pm-research-speaker-profile-link` so speaker-profile inline CTAs follow the shared CTA text rule instead of a quieter meta-link color.
- Updated CTA-related research-session tests to match the current CTA implementation: real text-decoration underlines for shared CTA links and inline-text profile links on speaker surfaces.

## Validation

- Browser validation through an Edge CDP probe on real routes:
  - `/de`, `/en`
  - `/de/sample`, `/en/sample`
  - mobile widths `320`, `390`, `430`
  - control checks for landing hero pill, footer links, drawer links, and topbar links
- Verified computed states:
  - landing card CTAs, corpus CTAs, and inline speaker-profile CTAs render `rgb(28, 28, 28)` with `textDecorationLine: none` before interaction
  - the same CTA families switch to `rgb(161, 90, 149)` with `textDecorationLine: underline` on hover
  - drawer and topbar links remain `textDecorationLine: none`
  - the landing hero pill remains separate from the text CTA family
- `get_errors` on the changed CSS files reported no new issues; the only reported items remain the pre-existing Chrome `<111` `color-mix(...)` compatibility warnings elsewhere in `30_components.css`.
- Focused CTA-related assertions in `app/tests/test_research_sessions.py` were updated to the current implementation and revalidated separately.

## Notes

- A full `app/tests/test_research_sessions.py` run still reports one unrelated team-page content assertion failure for the English team page (`Marcela Gualotuña` missing in rendered HTML). That failure is outside the CTA scope of this run.