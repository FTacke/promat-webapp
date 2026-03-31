# Admonition System

## Scope

This document combines:

- the live CSS stack
- computed values from the running site
- the existing project documentation in `docs/assets/documentation/admonitions_digital_book.md`

## Inventory

## Base-theme admonitions available in the stack

These are supplied by the base bundle and lightly tinted in `20_book.css`:

- `note`
- `info`
- `success`
- `warning`
- `danger`

They are available, but they are not the main project language.

## Project-specific admonition/container types

- `cover`
- `context`
- `expand`
- `regel`
- `tip`
- `praxis`
- `hoermal`
- `oton`
- `summary`
- `cite`
- `weiterlesen`

## Shared Formal Base

Most project admonitions inherit a common compact base:

- wrapper display: `flow-root`
- wrapper border: `1px solid rgba(0, 0, 0, 0.06)`
- wrapper radius: `8px`
- wrapper horizontal padding: `16px`
- wrapper vertical margins: `24.375px`
- body text scale: `15.6px / 25.74px`
- title/summary row built on the base theme admonition header mechanic

This compact base is used by:

- `context`
- `regel`
- `tip`
- `praxis`
- `oton`
- `expand`
- `hoermal`
- `weiterlesen`
- `cite`

`summary` deliberately breaks from this compact wrapper and behaves like a neutral section container.

## Type Matrix

| Type | Formal delta vs compact base | Visual character | Typical use |
| --- | --- | --- | --- |
| `context` | no geometry delta; tint only | calm informational tint, no left rail | contextualization, terminology, precision |
| `regel` | no geometry delta; tint only | concise rule container, didactic emphasis | explicit rule, merksatz |
| `tip` | no geometry delta; tint only | positive hint container | learning aid, shortcut, strategy |
| `praxis` | no geometry delta; tint only | applied/didactic container | transfer, classroom application |
| `oton` | no geometry delta; tint only | quote/perspective container | voice, testimony, perspective |
| `expand` | left rail becomes `4px solid rgb(63, 106, 114)` | expository, visibly expandable | excursion, deepening, contextual expansion |
| `hoermal` | left rail becomes `4px solid rgb(79, 107, 136)`; audio layout rules inside | media-enhanced, audio-led | listening examples, pronunciation analysis |
| `weiterlesen` | left rail becomes `3px solid rgb(28, 26, 32)`; paper-like background | academic/endmatter tone | further reading, literature pointers |
| `cite` | neutral paper surface, no left rail, `margin-top: 60px`, copy-button title affordance | reference box | chapter/book citation blocks |
| `summary` | transparent background, no icon, explicit padding `22px 24px 20px 24px`, `48px` outer margin | neutral closing section | chapter synthesis / recap |
| `cover` | fully isolated fixed-size component in `25_cover.css` | landing-page cover object | homepage only |

## Detailed Type Notes

### `context`

- Best representative of the normal tinted informational admonition family.
- No accent rail; only surface tint and icon color carry semantics.
- Suitable as the baseline for a **semantic admonition**, but not for a neutral generic card.

### `expand`

- Uses the same wrapper geometry as `context`, but introduces a strong `4px` left rail.
- Standard expandable/deepening variant.
- Formally closer to a semantic callout than to a neutral container.

### `regel`

- Same compact wrapper geometry.
- Strong didactic use case: visible, concise, not normally collapsed by default.

### `tip`

- Same compact wrapper geometry.
- Positive/supportive tone; visually still part of the same family.

### `praxis`

- Same compact wrapper geometry.
- Distinguished by didactic scenario rather than by structural geometry.

### `hoermal`

- Same compact wrapper geometry, but with `4px` semantic rail and several nested layout primitives:
  - `.audio-comparison`
  - `.audio-grid`
  - `.audio-block`
  - `.example`
- This is already a container-within-container system.

### `oton`

- Same compact wrapper geometry.
- Functionally discursive and perspective-oriented, not structurally distinct.

### `weiterlesen`

- Keeps the compact admonition shell, but changes the tone to academic endmatter.
- The `3px` left rail is weaker than `expand` / `hoermal`, but still semantic.

### `cite`

- Keeps the compact shell, but neutralizes the semantic accenting.
- The copy button and title padding make it a **specialized reference container**, not a general base.

### `summary`

- Removes the icon and the compact admonition header rhythm.
- Uses explicit whole-box padding instead of the compact admonition wrapper + header interplay.
- Keeps the same border/radius/shadow language, but strips semantic tint and semantic iconography.
- This is the cleanest neutral container in the project.

## Best Baseline Candidate For A Generic Container

## Recommendation: `summary`

`summary` is formally the best baseline for a future generic container system.

### Why `summary` wins

- no icon slot
- no semantic tint
- no semantic accent rail
- explicit whole-box padding instead of admonition-header coupling
- same border language as the rest of the project (`1px`, `8px`, `box-shadow: none`)
- already behaves like a neutral section-level closing container rather than an alert/callout

### Why `cite` is not the best baseline

- still tied to the admonition-title mechanic
- title row reserves extra space for the copy control
- top margin (`60px`) is endmatter-specific
- semantically bound to citation UX

### Why `context` is not the best baseline

- it is the best baseline for a **semantic informational admonition**
- but it still depends on a tinted surface and icon-bearing admonition header

## Formal Family Split

The live system already suggests three subfamilies:

### 1. Neutral containers

- `summary`
- `cite`

### 2. Compact semantic admonitions

- `context`
- `regel`
- `tip`
- `praxis`
- `oton`

### 3. Compact semantic admonitions with rail emphasis

- `expand`
- `hoermal`
- `weiterlesen`

`cover` remains an isolated outlier.

## Design-Language Summary

Across all project-specific admonitions, the actual design type is consistent:

- low-elevation
- quiet borders
- rounded but not pill-like containers
- semantic meaning carried by tint or rail, not shadow
- calm UI font titles over editorial body text

This is the design language a future card family should inherit.
