# 2026-04-14 - Card divider spacing and nav lock order

## Summary

- introduced a shared card utility that keeps a minimum block-end inset before divider-separated footer or follow-up action areas
- applied that shared inset rule to research corpus cards, speaker cards, player meta cards, and the mirrored sample card
- moved muted sidebar lock icons to render immediately after the link label and aligned the shared sidebar item layout to that order
- updated active platform and research-access specs plus focused regressions for the new spacing and nav ordering rules

## Validation

- focused pytest on research overview, sample page, muted research sidebar, and unaffected admin sidebar navigation