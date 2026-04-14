# 2026-04-14 - Reduced corpus landing pages

## Summary

- removed the redundant main-column research-area list from corpus landing pages and reduced the surface to title, subtitle, two prose paragraphs, and two actions
- kept the left sidebar as the only area navigation for `design`, `speakers`, `recordings`, `comparison`, and `phenomena`
- added a dedicated public access-request page and linked corpus-root login actions through the existing `next` return-target flow so successful login returns to the same corpus landing page
- updated the sample mirror, active specs, and focused regressions for the reduced landing-page pattern across all four corpora

## Validation

- focused pytest for research landing pages, access-request/login flow, and one unaffected admin sidebar regression