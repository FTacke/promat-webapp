# 2026-06-23 Selbsteinordnung UI – App-wide Consolidation (Session 3)

## Summary

Completed app-wide migration from the old large-button `pm-comparison-inline-help` pattern to the new compact `pm-info-tip` component. Fixed mobile comparison filter layout and stabilised desktop speaker meta badge row.

## Old info patterns found and migrated

| Location | Old pattern | Migrated |
|---|---|---|
| `research_comparison.html` — Set-selector label row | `pm-comparison-inline-help` | → `pm-info-tip` |
| `research_player.html` — Material strip set-select | `pm-comparison-inline-help pm-player-material-strip__set-help` | → `pm-info-tip pm-player-material-strip__set-help` |
| `research_filters.html` — Level filter label | migrated in Session 2 | done |
| `research_speaker_profile.html` — Session rows | migrated in Session 2 | done |
| `research_comparison.html` — Level filter zone | migrated in Session 2 | done |

All `pm-comparison-inline-help` references are now gone from all HTML templates. The CSS block for `pm-comparison-inline-help` is retained temporarily for the responsive overrides (now updated to also cover `pm-info-tip__body`).

## Mobile comparison filter layout fix

**Problem:** The secondary filter zone (`[L1 wählen] [Selbsteinordnung ⓘ] [Weitere Filter]`) was rendered as a single flex row on mobile, squeezing the "Selbsteinordnung wählen" select so its placeholder showed as "Selbs...".

**Fix:**
- Made `pm-comparison-filter-zone--secondary` `flex-wrap: wrap` on mobile (≤699px).
- Gave `pm-comparison-filter-field--select` and `pm-comparison-filter-level-wrap` `flex: 1 1 auto` so L1 and Selbsteinordnung share the row and wrap naturally.
- Made `pm-comparison-more-filters` full width (`flex: 1 1 100%`) so it sits on its own row.
- Shortened the placeholder `<option>` text in the level `<select>` from the long `levelFilterLabel` ("Selbsteinordnung wählen") to `t('common.labels.level')` ("Selbsteinordnung" / "Self-placement"). The `aria-label` retains the descriptive long form for accessibility.

Mobile result:
```
[Sprecher-ID suchen                 ]
[L1 wählen        ] [Selbsteinordnung ⓘ]
[Weitere Filter                     ]
```

## Desktop speaker meta badge fix

**Problem:** `.pm-comparison-speaker-row__meta` used `flex-wrap: wrap`, causing "Selbsteinordnung: B2" and "L1: DE" badges to appear on separate lines within speaker cards.

**Fix:**
- Changed `.pm-comparison-speaker-row__meta` to `flex-wrap: nowrap; min-width: 0; overflow: hidden`.
- Added `flex-shrink: 0; white-space: nowrap` to `.pm-comparison-speaker-badge`.
- Added `flex-wrap: wrap` override for `.pm-comparison-speaker-row__meta` in the ≤699px mobile media query so badges stack on small screens.

## Responsive pm-info-tip__body positioning

Updated both existing responsive overrides (≤699px and ≤979px) to include `pm-info-tip__body` alongside `pm-comparison-inline-help__body`, ensuring info popovers near the right edge right-anchor their body panel and don't overflow the viewport.

## Files changed

| File | Change |
|---|---|
| `app/templates/pages/research_comparison.html` | Set-selector → `pm-info-tip`; level select placeholder shortened |
| `app/templates/pages/research_player.html` | Material strip set-help → `pm-info-tip` |
| `app/static/css/30_components.css` | Speaker meta nowrap; badge white-space; mobile secondary zone wrapping; `pm-info-tip__body` in responsive overrides |

## Test result

217 passed, 16 deselected (pre-existing unrelated failures). No regressions introduced.
