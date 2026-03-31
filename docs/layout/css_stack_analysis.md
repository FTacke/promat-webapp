# CSS Stack Analysis

## Scope

- Runtime sample: `http://localhost:8000/admonitions/`
- Scheme: `default` (light mode)
- Viewport: `1440 x 2200`
- Source of truth: generated HTML head plus shipped CSS bundles in `site/` and `docs/assets/styles/`

## Actual Runtime Load Order

| Order | Runtime stylesheet | Primary layer | Functional role | Container relevance |
| --- | --- | --- | --- | --- |
| 0 | `assets/stylesheets/modern/main.28978c9b.min.css` | Base Stack | Core Zensical/Material shell, reset, typography baseline, nav, buttons, admonition mechanics, `details/summary`, generic `.grid` / `.grid.cards` | Defines the original admonition box model and the built-in card/grid system |
| 1 | `assets/stylesheets/modern/palette.dfe2e883.min.css` | Theme | Color-scheme and accent variable layer for default/slate modes | Supplies the theme color variables used by base components |
| 2 | `https://fonts.googleapis.com/...` | Theme dependency | Loads `Inter` and `JetBrains Mono` declared by the theme | Affects UI/code typography unless locally overridden |
| 3 | `assets/styles/00_tokens.css` | Zensical Tokens | Project design tokens: surfaces, accents, borders, admonition tint variables, spacing seeds | Rebinds the theme to the book palette |
| 4 | `assets/styles/10_typography.css` | Zensical Overrides | Local font-face definitions plus content typography override for `.md-typeset` | Replaces the base content scale with the editorial text system |
| 5 | `assets/styles/20_book.css` | Zensical Layout | Content width, content padding, nav chrome, link underline tuning, base admonition geometry bridge | Establishes the practical container baseline used by most admonitions/details |
| 6 | `assets/styles/25_cover.css` | Zensical Overrides | Isolated start-page cover component | Special-case container; not part of the reusable content baseline |
| 7 | `assets/styles/30_components.css` | Zensical Overrides | Header branding, doc meta block, search/header adjustments, component-level layout | Indirectly relevant; defines chapter meta grid and shell component spacing |
| 8 | `assets/vendor/leaflet/leaflet.css` | Theme/vendor extension | Third-party map UI styles | Not part of the prose container system; relevant only inside map components |
| 9 | `assets/styles/40_custom.css` | Zensical Overrides | Project-specific admonitions, audio layouts, `summary`, `cite`, `weiterlesen`, `impuls` | Defines the project-specific container families |
| 10 | `assets/styles/50_map.css` | Zensical Overrides | Map-specific media/layout inside `tip` admonitions and `.book-map` | Adds local grid/media rules, but not a generic card family |

## Inline Runtime Style Injection

The head also injects an inline style block:

```css
:root { --md-text-font: "Inter"; --md-code-font: "JetBrains Mono" }
```

This sits between the theme bundles and the project overrides. `10_typography.css` then replaces content typography for `.md-typeset`, but UI regions still inherit the theme font contract.

## Layer Responsibilities

### 1. Base Stack

The base bundle in `main.*.min.css` contributes the structural defaults that all later layers build on:

- Base content scale: `.md-typeset { font-size: .75rem; line-height: 1.8; }`
- Base headings, paragraphs, lists, tables, buttons, nav, sidebars
- Base admonition container: `display: flow-root`, `margin: 1.5625em 0`, `padding: 0 .8rem`, `border-radius: .4rem`
- Base admonition title / summary row: icon gutter, chevron logic, `summary` interactivity
- Built-in generic grid/card system:
  - `.md-typeset .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr)); grid-gap: .4rem; }`
  - `.md-typeset .grid.cards > ... { border: .05rem solid var(--md-default-fg-color--lightest); border-radius: .4rem; padding: .8rem; }`

This means the project already ships a generic card/grid primitive at the base-theme level, even though the repository content currently does not instantiate it.

### 2. Theme

`palette.*.min.css` is the theme-level variable switchboard. It does not create the component geometry itself; it feeds the base stack with scheme-specific colors, accent colors and shadow values.

Key consequence: hover/focus and default card/admonition behaviors from the base stack still point at theme variables unless later files override them.

### 3. Zensical Tokens

`00_tokens.css` rebases the visual system onto the book palette.

Primary token groups:

- surfaces: `--book-bg`, `--book-surface-1`, `--book-surface-2`
- text and border colors: `--book-fg`, `--book-muted`, `--book-border`, `--hairline-color`
- accent and link colors: `--book-accent`, `--book-link`, `--book-link-hover`
- admonition hues: `--book-adm-context`, `--book-adm-regel`, `--book-adm-tip`, `--book-adm-praxis`, `--book-adm-hoermal`, `--book-adm-expand`, `--book-adm-oton`, `--book-adm-cite`, `--book-adm-weiterlesen`
- token seeds: `--book-radius`, `--book-radius-sm`, `--book-shadow`, `--book-shadow-md`, `--book-focus`, `--s-1 ... --s-5`

Important finding: the token file contains only a partial spacing/radius system; many live values are still hard-coded later.

### 4. Zensical Layout

`20_book.css` is the decisive bridge from theme defaults to the book layout.

Container-relevant effects:

- content width and side spacing
- hidden secondary sidebar
- nav coloring and subnav guide line
- header border normalization
- global link underline treatment
- base admonition/details geometry rewrite:
  - `font-size: 0.78rem`
  - `line-height: 1.65`
  - `background: var(--book-surface-1)`
  - `border: 1px solid var(--book-border)`
  - `box-shadow: none`

This file defines the neutral geometry that project-specific admonitions later inherit.

### 5. Zensical Overrides

The remaining project files refine component families:

- `10_typography.css`: content type scale, local body font, H1/H2 treatment
- `25_cover.css`: isolated cover container
- `30_components.css`: doc meta grid, header, drawer branding
- `40_custom.css`: actual custom admonition families and supporting component layouts
- `50_map.css`: map preview/media composition inside tip admonitions

## Container-Relevant Cascade Result

The effective container system is not defined by one file, but by this sequence:

1. `main.*.min.css` supplies the admonition/details/card shell.
2. `palette.*.min.css` colors that shell.
3. `00_tokens.css` maps the shell to the book variables.
4. `20_book.css` rewrites the neutral admonition geometry.
5. `40_custom.css` specializes the variants (`summary`, `cite`, `weiterlesen`, `context`, `regel`, `tip`, `praxis`, `expand`, `hoermal`, `oton`).

That is the real stack to treat as the container foundation for future work.

## Immediate Consequences For Future Cards

- There is already a base-theme `.grid.cards` system in the loaded stack.
- The current project does not use it in source Markdown.
- The current Zensical override language prefers `8px` radius, `1px` borders, `box-shadow: none`, and calm surfaces.
- Any future card family that reuses `.grid.cards` unchanged would inherit hover shadow and border semantics from the base stack, not the book-specific container language.
