# 2026-05-24 Overview Hero Refinement

## Scope

- refine the shared `overview` admonition variant so it reads as a distinct hero-like quick-scan card instead of a normal tinted admonition
- keep the existing shared admonition structure intact and avoid new one-off overview markup

## Changes

- added dedicated overview hero tokens in `app/static/css/00_tokens.css`
  - background and gradient surface
  - accent, title, body, and bullet colors
  - larger badge and icon sizes
  - overview radius, shadow, divider, and decorative mark tokens
- updated `app/static/css/40_cards.css`
  - removed visible overview border treatment
  - promoted the overview title to a larger hero scale
  - turned the icon into a badge surface
  - added a subtle divider under the header
  - added a faint decorative compass mark on the right that hides on mobile
- updated `app/static/css/30_components.css`
  - tuned the overview body rhythm and bullet-list spacing
  - kept the overview bullets on the shared wordmark-accent family

## Validation

- `python -m pytest app/tests/test_research_sessions.py -q -k "which_pronunciation or sample_page_places_admonitions_before_pattern_lab_with_visible_titles"`

## Browser QA

- live QA used `http://127.0.0.1:8000`
- desktop checks on `/de/teaching/spanish/which-pronunciation`
  - overview title rendered at `28.58px`
  - overview badge rendered at `43.61px`
  - overview border width rendered at `0px`
  - decorative mark rendered on desktop and the divider line was present
- desktop checks on `/de/sample`
  - sample overview used the same hero styling
  - normal `tip` admonitions stayed on the standard `24.96px` title scale with `1px` border and no shadow
- mobile checks on DE and EN `which-pronunciation`
  - breakpoint matched at `390px`
  - decorative mark was hidden
  - no horizontal overflow occurred

## QA Artifacts

- screenshots saved under `tmp/ui-qa/2026-05-24-overview-hero-refinement/`
  - `sample-overview-desktop.png`
  - `which-de-overview-desktop.png`
  - `which-en-overview-desktop.png`
  - `which-de-overview-mobile.png`
  - `which-en-overview-mobile.png`