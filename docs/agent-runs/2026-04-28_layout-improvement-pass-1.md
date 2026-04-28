# Layout Improvement Pass 1

- Date: 2026-04-28
- Scope: Shared card hover, team-card calming, player/comparison material-choice consolidation, H2 spacing, literature list styling, admin settings icon

## Changes

- consolidated shared `pm-card` hover behavior in `app/static/css/40_cards.css` so link-card titles keep their normal color and hover feedback stays on the card shell without layout movement
- lightened `pm-meta-card` for the project team surface with transparent card backgrounds, tighter grid width and quieter lead-name typography
- removed the player-only `pm-material-choice` styling fork so the player now uses the same shared material-choice base as comparison
- raised shared H2 follow-text spacing through the reading token layer instead of page-local margins
- added shared `pm-literature` and `pm-literature-abbreviations` list styles in the reading layout system and wired the Spanish design references section to `pm-literature`
- replaced the admin user-menu home-like icon with a shared settings icon and aligned menu item icon/text layout

## Validation

- focused pytest slice for touched layout regressions in `app/tests/test_research_sessions.py` and `app/tests/test_auth_phase1.py`
- full `Run research sessions tests` task: 182 passed
- full `Run auth phase tests` task: 39 passed
- browser QA on `127.0.0.1:8000` with screenshots saved under `tmp/ui-qa/layout-pass-2026-04-28/`
- hover stability check on the landing card reported zero rectangle deltas for `x`, `y`, `width`, and `height`
- bilingual screenshots captured for public team, research root, and design routes plus authenticated comparison, player, and admin routes

## Notes

- no live page currently renders `pm-literature-abbreviations`; the class was added and covered structurally in CSS/tests for upcoming bibliography-abbreviation sections