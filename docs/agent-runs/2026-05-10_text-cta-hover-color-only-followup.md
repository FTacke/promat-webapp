# 2026-05-10 Text CTA Hover Color Only Followup

## Scope

- Follow up on the shared text CTA normalization so hover and focus keep the neutral-to-accent color change but no longer add an underline.
- Keep navigation, drawer, footer, breadcrumbs, body links, and pill or button CTAs outside the change scope.

## Changes

- Removed the hover and focus underline from `.pm-inline-text-link` in `app/static/css/30_components.css` so inline CTA-style links now use color-only interaction.
- Removed the hover and focus underline from the shared `.pm-cta-link` hover block, including card-triggered hover states for visual CTAs inside clickable cards.
- Updated the shared CTA CSS regression in `app/tests/test_research_sessions.py` so it now asserts that the hover block contains no text-decoration rule.
- Removed an unrelated empty `a:hover {}` rule at the top of `app/static/css/30_components.css` to clear the local CSS error reported by `get_errors`.

## Validation

- Focused pytest run:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "shared_cta_links_use_container_underline_rule or sample_page_uses_current_research_component_patterns or speakers_page_uses_neutral_learner_cards_with_level_badges or speakers_card_route_localizes_quiet_profile_link_in_english or speakers_route_renders_table_view_and_preserves_query_state or speakers_table_route_localizes_labels_in_english"`
- Browser validation through an Edge CDP probe on real routes:
  - `/de`
  - `/en`
  - `/en/sample`
  - `/en/research`
  - desktop plus mobile `390` and `430`

## Results

- Landing card CTAs, corpus CTAs, and inline speaker-profile CTAs stay `textDecorationLine: none` before and after hover while changing from `rgb(28, 28, 28)` to `rgb(161, 90, 149)`.
- The landing hero pill remains unchanged and outside the text CTA family.
- Footer links remain normally underlined.
- Drawer and topbar links remain un-underlined.
- `get_errors` reports no new issues beyond the pre-existing Chrome `<111` `color-mix(...)` compatibility warnings elsewhere in `30_components.css`.