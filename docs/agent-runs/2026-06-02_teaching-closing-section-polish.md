# Teaching Closing Section Polish — 2026-06-02

## Scope

Polished the lower closing area of teaching topic pages: Impulse, Vertiefung, Zitieren-Box.

## Changes

### `app/static/css/30_components.css`

**Unified `didactic_close` block styles** — replaced two separate layers of styling (one generic, one `which-pronunciation`-slug-specific with rosé pill badges) with a single generic rule set that applies to all topics:

- **Outer block**: rosé background (`7% wordmark-accent`), `--pm-teaching-further-reading-border` border, `12px` radius, no left-accent border, uniform padding via `clamp()`.
- **Width**: `min(85%, 56rem)` — matches `further-reading` and `citation`. Needs `justify-self: center` + selector specificity `(0-3-0)` (via `.pm-teaching-block-grid`) to beat the `.pm-teaching-block-grid > .pm-teaching-block.pm-reading { width: 100% }` rule in `20_layout.css`.
- **Number markers**: `position: absolute` circle at `inset-inline-start: 0`. Using absolute positioning (not flex) because CSS flexbox blockifies inline children (`<strong>`, `<em>`, `<br>`) into separate flex items, fragmenting the text. With `li { position: relative; padding-inline-start: calc(2.15rem + 0.68rem) }`, inline content flows normally as a block. Circle size `2.15rem × 2.15rem` — neutral border/bg, UI font, same visual family as `.pm-comparison-item__number` but slightly larger.
- **List layout**: `ul { display: grid; gap: 0.62rem; counter-reset: impulse-list }` — uses gap instead of border-top between items.
- Removed all `[data-topic-slug="which-pronunciation"]` overrides for `didactic_close` (approx. 80+ lines across two wave locations).
- **Citation section**: generalized `gap: 0.9rem` and `margin-top: 3.6rem` from slug-specific to all topics. Removed `row-gap: 0` override (was hiding the gap between further-reading and citation blocks).
- **Mobile** (`≤759px`): added `width: 100%; max-width: none` for `didactic_close` alongside the existing `further-reading` and new `citation` mobile overrides.

**Citation block width** — changed from `min(100%, 72ch + 48px)` to `min(85%, 56rem)` + `max-width: 100%`. All three closing blocks (impulse, further-reading, citation) now resolve to the same `896px` on a 1280px viewport.

### `app/static/css/30_components.css` — unchanged

- `.pm-comparison-item__number` and `.pm-phenomena-item__number` not touched.

## Browser acceptance

- DE `/de/teaching/spanish/which-pronunciation`: impulse `01/02/03` circles left-aligned, title bold, description wraps cleanly; rosé outer block; same width as Vertiefung and Zitieren-Box below.
- EN `/en/teaching/spanish/which-pronunciation`: "Classroom prompts" / "Listen first / Make variation visible / Clarify norms" — correct.
- Mobile 390px: circle + text stacks cleanly, no overflow.
- Width alignment verified numerically: all three blocks `896px` at `l=192`.
- No regression on comparison/research pages (number marker CSS not touched).
