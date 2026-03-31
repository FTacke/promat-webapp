# Container Baseline

## Measurement Setup

- Runtime source: live build on `http://localhost:8000/`
- Scheme: `default` (light mode)
- Viewport: `1440 x 2200`
- Pages sampled:
  - `/admonitions/`
  - `/aussprache/`
  - `/variation/variation_morphosyntax/`
  - `/variation/variation_plurizentrik/`

## Structural Note

Inside `.md-typeset`, the prose pages do **not** use semantic `section` wrappers for the main flow. The article content is a flat sequence of direct children (`h1`, `h2`, `h3`, `p`, `div.admonition`, `details`, `hr`, etc.).

For baseline purposes, the relevant normal content containers are therefore:

- `article.md-content__inner.md-typeset`
- `.md-typeset > p`
- direct block containers such as `.admonition` and `details`

## Content Flow Baseline

| Element | Background | Border | Radius | Shadow | Padding | Margin top / bottom | Font size | Line height |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `article.md-content__inner.md-typeset` | `rgba(0, 0, 0, 0)` | `0px none` on all sides | `0px` | `none` | `14px 40px 0px 44px` | `0px / 24px` | `20px` | `35px` |
| `.md-typeset > p` | `rgba(0, 0, 0, 0)` | `0px none` | `0px` | `none` | `0px` | `20px / 20px` | `20px` | `35px` |
| `.md-typeset > h1` | `rgba(0, 0, 0, 0)` | `0px none` | `0px` | `none` | `0px` | `0px / 55px` | `44px` | `44px` |
| `.md-typeset > h2` | `rgba(0, 0, 0, 0)` | `border-bottom: 1px solid rgb(213, 210, 204)` | `0px` | `none` | `0px 0px 9px 0px` | `48px / 19.2px` | `30px` | `42px` |

## Shared Open Admonition Baseline

These live wrappers share the same geometry and differ only in tint or accent edge treatment:

- `.admonition.context`
- `.admonition.regel`
- `.admonition.tip`
- `.admonition.praxis`
- `.admonition.oton`
- `.admonition.expand`
- `.admonition.hoermal`

### Shared Geometry

| Property | Value |
| --- | --- |
| Display | `flow-root` |
| Border top/right/bottom | `1px solid rgba(0, 0, 0, 0.06)` |
| Border radius | `8px` |
| Box shadow | `none` |
| Padding | `0px 16px 0px 16px` |
| Margin top / bottom | `24.375px / 24.375px` |
| Font size | `15.6px` |
| Line height | `25.74px` |
| Text color | `rgba(0, 0, 0, 0.87)` |

### Variant Surfaces And Edge Changes

| Element | Background | Border-left |
| --- | --- | --- |
| `.admonition.context` | `color(srgb 0.912627 0.923255 0.919176)` | `1px solid rgba(0, 0, 0, 0.06)` |
| `.admonition.regel` | `color(srgb 0.913451 0.924627 0.903804)` | `1px solid rgba(0, 0, 0, 0.06)` |
| `.admonition.tip` | `color(srgb 0.909059 0.930667 0.907647)` | `1px solid rgba(0, 0, 0, 0.06)` |
| `.admonition.praxis` | `color(srgb 0.934314 0.918588 0.892824)` | `1px solid rgba(0, 0, 0, 0.06)` |
| `.admonition.oton` | `color(srgb 0.934314 0.909804 0.908745)` | `1px solid rgba(0, 0, 0, 0.06)` |
| `.admonition.expand` | `color(srgb 0.918118 0.926275 0.917529)` | `4px solid rgb(63, 106, 114)` |
| `.admonition.hoermal` | `color(srgb 0.92251 0.926549 0.923569)` | `4px solid rgb(79, 107, 136)` |

## Closed Details Baseline

`details.context` inherits the same wrapper geometry as the open admonitions.

| Element | Background | Border | Radius | Shadow | Padding | Margin top / bottom | Font size | Line height |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `details.context` | `color(srgb 0.912627 0.923255 0.919176)` | `1px solid rgba(0, 0, 0, 0.06)` on all sides | `8px` | `none` | `0px 16px 0px 16px` | `24.375px / 24.375px` | `15.6px` | `25.74px` |
| `details.context > summary` | `rgba(0, 0, 0, 0)` | `0px none` | `2px` | `none` | `0px 32px 0px 32px` | `12px / 12px` | `15.6px` | `25.74px` |

### Summary Row Findings

- `summary` is the real interactive header primitive.
- It uses a `32px` icon/chevron gutter on both sides in the collapsed details pattern.
- It carries pointer affordance via `cursor: pointer`.
- No custom background or hover fill is applied in the project layer.

## Neutral Chapter-End Containers

### `div.admonition.summary`

| Property | Value |
| --- | --- |
| Background | `rgba(0, 0, 0, 0)` |
| Border | `1px solid rgba(0, 0, 0, 0.06)` on all sides |
| Border radius | `8px` |
| Box shadow | `none` |
| Padding | `22px 24px 20px 24px` |
| Margin top / bottom | `48px / 48px` |
| Font size | `15.6px` |
| Line height | `25.74px` |

Title row inside `.admonition.summary`:

| Property | Value |
| --- | --- |
| Background | `rgba(0, 0, 0, 0)` |
| Border | `0px none` |
| Padding | `0px` |
| Margin top / bottom | `0px / 10px` |
| Font size | `15.6px` |
| Line height | `25.74px` |

### `details.weiterlesen`

| Property | Value |
| --- | --- |
| Background | `color(srgb 0.970196 0.966274 0.954902)` |
| Border top/right/bottom | `1px solid rgba(0, 0, 0, 0.06)` |
| Border left | `3px solid rgb(28, 26, 32)` |
| Border radius | `8px` |
| Box shadow | `none` |
| Padding | `0px 16px 0px 16px` |
| Margin top / bottom | `24.375px / 24.375px` |
| Font size | `15.6px` |
| Line height | `25.74px` |

Summary row inside `details.weiterlesen`:

| Property | Value |
| --- | --- |
| Padding | `0px 32px 0px 32px` |
| Margin top / bottom | `12px / 12px` |
| Font size | `15.6px` |
| Line height | `25.74px` |
| Cursor | `pointer` |

### `div.admonition.cite`

| Property | Value |
| --- | --- |
| Background | `color(srgb 0.994118 0.995059 0.995294)` |
| Border | `1px solid rgba(0, 0, 0, 0.06)` on all sides |
| Border radius | `8px` |
| Box shadow | `none` |
| Padding | `0px 16px 0px 16px` |
| Margin top / bottom | `60px / 24.375px` |
| Font size | `15.6px` |
| Line height | `25.74px` |

Title row inside `.admonition.cite`:

| Property | Value |
| --- | --- |
| Padding | `0px 48px 0px 32px` |
| Margin top / bottom | `12px / 15.6px` |
| Font size | `15.6px` |
| Line height | `25.74px` |

## Existing Grid-Like Structures

### `.audio-grid`

| Property | Value |
| --- | --- |
| Display | `grid` |
| Columns | `325.5px 325.5px` |
| Gap | `22px 28px` |
| Margin top / bottom | `18px / 0px` |
| Font size | `15.6px` |
| Line height | `25.74px` |

### `.audio-grid > .audio-block`

| Property | Value |
| --- | --- |
| Display | `flex` |
| Border | `0px none` |
| Padding | `0px 0px 28px 0px` |
| Margin top / bottom | `0px / 0px` |
| Font size | `15.6px` |
| Line height | `25.74px` |

### `.audio-grid .example`

| Property | Value |
| --- | --- |
| Background | `color(srgb 0.957961 0.953412 0.940706)` |
| Border | `1px solid color(srgb 0.835294 0.823529 0.8 / 0.7)` |
| Border radius | `7px` |
| Box shadow | `none` |
| Padding | `9px 12px 30px 12px` |
| Margin top / bottom | `0px / 11px` |
| Font size | `14.352px` |
| Line height | `21.528px` |

### `.map-image-row`

| Property | Value |
| --- | --- |
| Display | `grid` |
| Columns | `336px 336px` |
| Gap | `10px` |
| Width | `682px` |

This is a local media row, not a generic prose container.

## Practical Baseline Summary

There are two real baseline geometries in the project:

1. **Compact admonition wrapper baseline**
   - `8px` radius
   - `1px` border
   - `16px` horizontal wrapper padding
   - `24.375px` vertical margins
   - `15.6px / 25.74px` inner text scale

2. **Neutral summary container baseline**
   - `8px` radius
   - `1px` border
   - explicit box padding `22px 24px 20px 24px`
   - `48px` top and bottom separation
   - no tint, no icon, no accent rail

For a future generic container system, the second pattern is the cleaner neutral primitive.
