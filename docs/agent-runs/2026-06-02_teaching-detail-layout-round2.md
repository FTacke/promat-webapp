# Teaching Detail Layout Round 2

Date: 2026-06-02

## Scope

- Refined existing Teaching topic detail page sections for Spanish `which-pronunciation`.
- Covered `Impulse für den Unterricht`, context/info box width, audio section headings/icons, and the `Vertiefung` block.
- Did not introduce new Teaching box types or a generic future box system.

## Changes

- Kept the rose didactic outer block and replaced the inner callout-like cards with quiet tinted cards.
- Converted impulse numbers into small badges and removed the left border/bar treatment.
- Removed the artificial 82% width rule for one-column context/info admonitions.
- Reduced audio heading scale and aligned the audio icon size with the other topic-page box icons.
- Restyled `Vertiefung` with a warm neutral surface, no header divider, more compact inner cards, and natural CTA placement.
- Shortened the real `which-pronunciation` further-reading CTAs:
  - `Hörbeispiele öffnen`
  - `Open listening examples`

## Verification

- Ran focused tests:
  - `.\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py::test_teaching_pilot_topic_renders_canonical_two_column_storytelling app/tests/test_research_sessions.py::test_teaching_english_which_pronunciation_renders_single_markdown_citation app/tests/test_research_sessions.py::test_teaching_topic_box_css_uses_eye_overview_and_structured_context_box -q`
- Result: `3 passed`.

## Browser QA

Captured and inspected:

- `tmp/ui-qa/2026-06-02-teaching-detail-layout-round2/de-desktop.png`
- `tmp/ui-qa/2026-06-02-teaching-detail-layout-round2/de-mobile.png`
- `tmp/ui-qa/2026-06-02-teaching-detail-layout-round2/en-desktop.png`
- `tmp/ui-qa/2026-06-02-teaching-detail-layout-round2/en-mobile.png`
- `tmp/ui-qa/2026-06-02-teaching-detail-layout-round2/computed-styles.json`
- Regression route using the same Teaching detail family:
  - `tmp/ui-qa/2026-06-02-teaching-detail-layout-round2/final-r-desktop.png`
  - `tmp/ui-qa/2026-06-02-teaching-detail-layout-round2/final-r-mobile.png`

Notes:

- Context/info box width matches its one-column grid container on desktop and mobile.
- Audio titles are smaller and no longer dominate the box hierarchy.
- `Vertiefung` has no divider and CTA padding computes to `0px`.
- The unaffected `final-r` Teaching topic detail page remains visually clean.
- External Datawrapper frames remained blank in local QA; this is unrelated to the CSS changes.
