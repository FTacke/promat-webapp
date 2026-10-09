# 2026-10-09 German corpus citation box and H1 line height

## German corpus citation

- The citation box on `/{de,en}/research/{corpus}` is rendered by the shared `citation_block` for every corpus whose registry entry is `citable` (published, creators, publication date). German was `status: in_preparation` without `date_published`, so no box appeared.
- Change: `content/publication/resources.yaml`, `languages.german.research_corpus`: `status: published`, `date_published: "2026"`. Creator stays the existing registry entry `kathrin-siebold` (project lead, with the corpus contributors Theresa Fischer for material design and data collection); no authorship was added. Component, position (below the access buttons), icons, copy button and the English variant follow from the existing template; nothing was duplicated.
- Result: `Siebold, Kathrin (2026–). Pronunciation Matters: German Learner Pronunciation Corpus. In: Felix Tacke (Hrsg.), Pronunciation Matters: A Multilingual Platform for Learner Pronunciation Research and Teaching. Philipps-Universität Marburg. https://pronunciation-matters.de/de/research/german` (EN: `(ed.)`, `/en/research/german`). The author is the registry's corpus creator and follows the French pattern (project lead as first author); please confirm Prof. Dr. Siebold as the intended first author.
- Tests: new `test_german_corpus_offers_the_same_citation_box_as_the_french_one`; the former "German corpus is not citable" assertions were updated (`/de/teaching/german` remains uncited).
- Browser: DE and EN, light/dark, 1440/390 px: box geometry identical to the French page (725 px, same position), copy button puts the exact text into the clipboard, no overflow.
- Note: the running dev server caches the registry; a `.py` touch (reload) was needed to see the change locally.

## H1 line height

- Shared token `--pm-type-display-line` (used by `.promat-page__title`, the H1 of every page type) changed from `1` to `1.12`; no page-local override. Teaching topic, hub and overview titles keep their own existing line heights.
- Measured: single-line titles keep their glyphs and gain about 5 px of box height (39.2 → 43.9 px line box); the two-line title of `/de/research/spanish/design` is 88 px (was 78) on desktop, the four-line mobile title 158 px (was 141). No overflow.
- Test: `test_page_h1_line_height_comes_from_the_shared_display_token`.
