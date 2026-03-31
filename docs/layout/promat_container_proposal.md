# PROMAT Container Proposal

## Purpose

This proposal does **not** change CSS. It formalizes the existing live Zensical container language so that:

- current admonitions stay structurally readable
- future PROMAT cards can belong to the same design family
- the future system is defined by measured values instead of taste

## A. Foundation Tokens

## Existing token strengths

Already present and reusable:

- book surfaces: `--book-bg`, `--book-surface-1`, `--book-surface-2`
- border hues: `--book-border`, `--book-border-strong`, `--hairline-color`
- semantic hues: `--book-adm-*`
- interaction color: `--book-link-hover`

## Missing or insufficient tokenization

The current token layer is incomplete for a formal container system.

### Missing or inconsistent areas

1. **Container radius scale is incomplete**
   - Tokens define `14px` and `8px`.
   - Live containers actually use `8px`.
   - Nested example boxes use `7px`.
   - Buttons use `24px`.
   - Result: the token layer does not yet describe the live radius hierarchy.

2. **Spacing scale is not authoritative**
   - Token scale: `0.25rem`, `0.5rem`, `1rem`, `1.5rem`, `2.5rem`
   - Live container values: `12`, `16`, `20`, `24.38`, `28`, `32`, `48`, `60` px and more
   - Result: current spacing tokens do not govern the real container geometry.

3. **Typography scale for containers is implicit**
   - Prose body: `20px / 35px`
   - Container body: `15.6px / 25.74px`
   - Neutral container title: `15.6px / 25.74px`
   - Result: no dedicated container typography tokens currently exist.

4. **Interactive tokens are present but not wired consistently**
   - `--book-focus` exists
   - Live focus-visible is still the base-theme `outline: auto` pattern
   - Result: future card focus behavior should be tokenized explicitly

## Recommended token set for a formal container system

### Surface tokens

- `container-surface-neutral`: neutral container surface
- `container-surface-paper`: citation / reading / material surface
- `container-surface-tint-*`: semantic family tints derived from `--book-adm-*`
- `container-surface-hover`: interactive card hover surface

### Border tokens

- `container-border-default`: default `1px` container border
- `container-border-strong`: stronger border where needed
- `container-rail-*`: semantic left-rail colors

### Radius tokens

- `container-radius-sm = 7px` only for nested example boxes
- `container-radius = 8px` for all real containers
- `control-radius-pill = 24px` for buttons/chips only

### Spacing tokens

- `space-xs = 12px`
- `space-sm = 16px`
- `space-text = 20px`
- `space-container = 24px`
- `space-grid = 28px`
- `space-lg = 32px`
- `space-xl = 48px`
- `space-xxl = 60px`

### Typography tokens

- `type-flow = 20px / 35px`
- `type-container = 15.6px / 25.74px`
- `type-container-title = 15.6px / 25.74px`, UI font, `600`

## B. Base Container

## Proposed neutral base container

This should be derived from the live `summary` container, because `summary` is the cleanest neutral primitive already present.

### Formal definition

- background: transparent or neutral surface token
- border: `1px solid container-border-default`
- border-radius: `8px`
- box-shadow: `none`
- padding: `22px 24px 20px 24px`
- outer rhythm: `48px` only when used as chapter-end or major section box; otherwise use `24px`
- body text: `15.6px / 25.74px`
- title text: `15.6px / 25.74px`, UI font, `600`
- no icon gutter by default
- no semantic left rail by default

### Formal rule

If a container is meant to be reusable across content types, it must start from this neutral base, not from a semantically tinted admonition.

## C. Family Split

## 1. Admonition Family

This family already exists. It should be formalized, not redesigned.

### Shared rules

- wrapper radius stays `8px`
- wrapper border stays `1px`
- wrapper shadow stays `none`
- body text stays `15.6px / 25.74px`
- compact wrapper padding stays `0 16px`
- title/header keeps icon/chevron gutter behavior

### Subfamilies

#### A. Tinted semantic admonitions

- `context`
- `regel`
- `tip`
- `praxis`
- `oton`

Rule:

- semantic meaning is carried by surface tint and icon
- no semantic rail unless the variant explicitly requires one

#### B. Rail-emphasis admonitions

- `expand`
- `hoermal`
- `weiterlesen`

Rule:

- semantic meaning is carried by both surface and left rail
- rail is reserved for emphasis or media-specific variants

#### C. Neutral admonition-like endmatter

- `cite`

Rule:

- keep compact admonition shell only when the component still needs admonition-title behavior or controls

## 2. Card Family

This family is conceptual only at this stage, but it should speak the same design language.

### Card family root rule

Future cards should inherit the **neutral base container**, not the base-theme `.grid.cards` appearance directly.

Reason:

- base-theme cards use hover shadow as a primary signal
- the live book language uses border + tint + quiet surfaces, not elevation

### Card subtypes

#### A. Selection card

Use case:

- choosing between options, modules, exercises, or routes

Formal rules:

- base: neutral container geometry
- full-surface link allowed
- hover: border tint and/or subtle surface shift, no heavy elevation
- focus-visible: explicit container focus ring token, not browser-default only

#### B. Material card

Use case:

- structured references, assets, examples, compact learning materials

Formal rules:

- base: neutral or paper-like surface
- no semantic rail by default
- internal meta rows may use compact spacing, but outer geometry stays neutral

#### C. Interactive card

Use case:

- clickable cards with active/selected states

Formal rules:

- hover changes surface and border, not shadow-first
- selected state should use border/accent tokens, not ad hoc background colors
- nested inline links must remain visually distinct from the card-level click target

## D. Clear Rules

1. Container radius for all real prose containers is `8px`.
2. Default container border is `1px`; thicker left rails are semantic exceptions.
3. Default container shadow is `none`.
4. Default container body type is `15.6px / 25.74px`.
5. Prose-to-container and standard container-to-container rhythm is `24px`.
6. `48px` spacing is reserved for summary-like chapter-end containers.
7. `60px` top offset is an endmatter exception, not a generic card rule.
8. Neutral reusable containers must not depend on icon gutters.
9. Rail accents are reserved for semantic or media-driven variants only.
10. Future PROMAT cards should not adopt base-theme `.grid.cards` hover shadow unchanged.

## E. Practical Recommendation For PROMAT

If PROMAT needs a formal container family, the safest path is:

1. Treat `summary` as the neutral base container.
2. Treat compact tinted admonitions as the semantic companion family.
3. Build future cards as neutral containers with explicit interactive states.
4. Reuse the same border/radius/type/rhythm language before introducing any new ornament.

This keeps admonitions and future cards inside one coherent design type instead of creating a second parallel system.
