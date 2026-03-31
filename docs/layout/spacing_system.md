# Spacing System

## Measurement Setup

- Runtime sample: live build, light mode
- Main rhythm page: `/admonitions/`
- Chapter-end rhythm page: `/aussprache/`
- Shell spacing page: `/admonitions/`
- Viewport: desktop `1440px` wide

## Measured Vertical Rhythm

### Core Flow Rhythm

| Transition | Measured gap |
| --- | --- |
| `h1 -> first paragraph` | `55px` |
| `h2 -> paragraph` | `20px` |
| `h3 -> paragraph` | `20px` |
| `paragraph -> paragraph` | `20px` |
| `paragraph -> open admonition` | `24.38px` |
| `paragraph -> closed details` | `24.38px` |

### Real Container-To-Container Rhythm

Measured on `/aussprache/`, where containers actually follow each other directly:

| Transition | Measured gap |
| --- | --- |
| `.admonition.regel -> details.expand` | `24.38px` |
| `.admonition.summary -> details.weiterlesen` | `48px` |

Interpretation:

- `24.38px` is the standard prose-to-container and container-to-container rhythm.
- `48px` is the enlarged chapter-end separation used by `summary`.

## Shell And Content Width Spacing

Measured on `/admonitions/`:

| Relation | Measured value |
| --- | --- |
| Primary sidebar width | `260px` |
| Content column width | `960px` |
| Article width inside content | `800px` |
| Sidebar edge -> content box gap | `0px` |
| Sidebar edge -> article box gap | `24px` |
| Article/content inner padding left | `44px` |
| Article/content inner padding right | `40px` |
| Article top padding | `14px` |
| Article bottom margin | `24px` |

Important consequence: the readable text column is not separated from the sidebar by an outer content gutter first; the readable column emerges from the `.md-content__inner` margin and padding system.

## Grid And Media Spacing

### Audio Grid

| Property | Value |
| --- | --- |
| Grid columns | `325.5px 325.5px` |
| Grid gap | `22px 28px` |
| Grid margin-top | `18px` |
| Block bottom padding | `28px` |
| Example box bottom padding | `30px` |
| Example box bottom margin | `11px` |

### Map Preview Row

| Property | Value |
| --- | --- |
| Grid columns | `336px 336px` |
| Gap | `10px` |

These grids are component-local and do not form a general card rhythm.

## Observed Spacing Values In The Live System

The runtime system uses these values repeatedly:

- `10px`
- `12px`
- `14px`
- `16px`
- `18px`
- `20px`
- `22px`
- `24px` / `24.375px`
- `28px`
- `30px`
- `32px`
- `40px`
- `44px`
- `48px`
- `55px`
- `60px`

This is broader than the token scale in `00_tokens.css`.

## Existing Token Scale Versus Real Runtime

Current token scale in `00_tokens.css`:

| Token | Value |
| --- | --- |
| `--s-1` | `0.25rem` |
| `--s-2` | `0.5rem` |
| `--s-3` | `1rem` |
| `--s-4` | `1.5rem` |
| `--s-5` | `2.5rem` |

Observed issue:

- The live container system is not actually governed by those five tokens.
- Most decisive container values are hard-coded in px or rem elsewhere.
- The token scale does not encode the real chapter-end separation (`48px`), content rhythm (`20px`), summary padding (`22/24/20`), or cite offset (`60px`).

## Recommended Formalized Scale

To describe the existing system coherently without changing CSS, the smallest stable scale is:

| Recommended semantic step | Runtime value it best represents |
| --- | --- |
| `space-xs` | `12px` |
| `space-sm` | `16px` |
| `space-text` | `20px` |
| `space-container` | `24px` |
| `space-grid` | `28px` |
| `space-lg` | `32px` |
| `space-xl` | `48px` |
| `space-xxl` | `60px` |

### How The Runtime Maps To This Scale

- text flow uses `20px`
- default container separation uses `24px`
- summary chapter-end containers use `48px`
- cite blocks begin with `60px` top offset
- component grids use `22/28px`, so `28px` is the stronger reusable grid step

## Practical Recommendation

For future container work, treat the live rhythm as two concentric systems:

1. **Flow rhythm**
   - `20px` between prose blocks and headings-to-text
   - `24px` when prose transitions into containers

2. **Section / chapter-end rhythm**
   - `48px` before and after summary-like closing containers
   - `60px` reserved for citation/endmatter offsets only

This description matches the current site more closely than the existing token file.
