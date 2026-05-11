# 2026-05-10 CTA Link Underline Normalization

## Scope

- Diagnose and normalize the underline behavior for text-style CTA links such as `Zur Forschung` / `Go to research` and comparable CTA/action links with arrow suffixes.
- Remove artificial underline mechanisms from `.pm-cta-link` without regressing drawer, topbar, button, or footer link families.

## Root Cause

- The deep CTA underline was not produced by `text-decoration`. It came from `.pm-cta-link::after` in `app/static/css/30_components.css`.
- That pseudo-element underline was combined with `min-height: var(--pm-touch-target-min)` and block padding on `.pm-cta-link`, which pushed the line toward the bottom edge of the CTA block instead of keeping it close to the text.
- Landing-card CTAs such as `Zur Forschung` / `Go to research` are rendered through `render_cta_link_visual(...)` as visible `.pm-cta-link` text inside a clickable card link, so they needed the same normalization triggered from card hover and focus states rather than only from direct anchor hover.

## Changes

- Removed the CTA-specific pseudo underline mechanism from `.pm-cta-link` in `app/static/css/30_components.css`.
- Removed touch-target geometry from text-style `.pm-cta-link` by dropping the CTA `min-height` and block padding that were dragging the underline downward.
- Switched `.pm-cta-link` to real `text-decoration` underline behavior with a normal text underline offset, thickness from font, and skip-ink.
- Added underline inheritance for `.pm-cta-link__label` and `.pm-cta-link .pm-interaction__arrow` so the visible CTA text and arrow are underlined together.
- Added the same real underline treatment for visual CTA spans inside clickable cards via `a.pm-card:hover .pm-cta-link` and corresponding focus/active selectors.
- Restored the shared text underline offset token in `app/static/css/00_tokens.css` to a normal typographic value and removed the CTA-specific pseudo-underline offset token.
- Added underline inheritance for `.pm-inline-text-link` arrow spans so inline text links with arrow suffixes underline as one visible text unit.
- Kept drawer and topbar link families on `text-decoration: none`.

## Validation

- CSS validation with `get_errors` on:
  - `app/static/css/00_tokens.css`
  - `app/static/css/30_components.css`
- Browser validation through Edge CDP on real routes:
  - Landing desktop: `/de`, `/en`
  - Landing mobile: `/de`, `/en` at `320`, `390`, `430`
  - Sample CTA anchor: `/de/sample`, `/en/sample`, plus mobile `390` on `/en/sample`
  - Sample footer links: `/de/sample`, `/en/sample`, plus mobile `390` on `/en/sample`
  - Sample inline text links: `/de/sample`, `/en/sample`, plus mobile `390` on `/en/sample`
  - Drawer/topbar regression check: `/de/research`, `/en/research` at mobile `390`

## Results

- Landing card CTAs report `textDecorationLine: underline`, `borderBottomWidth: 0px`, `backgroundImage: none`, `boxShadow: none`, and `afterContent: none` in desktop and all requested mobile widths.
- Sample real CTA anchors report the same normalized underline behavior, with the arrow span also reporting `textDecorationLine: underline`.
- Sample inline text links now report underline on both label and arrow span.
- Footer links remain normal text-decoration underlines.
- Drawer and topbar links remain `textDecorationLine: none`.
- Remaining reported issues are only the pre-existing Chrome `<111` `color-mix(...)` compatibility warnings elsewhere in `30_components.css`.