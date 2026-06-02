# Teaching Detail Box Polish

Date: 2026-06-02

## Scope

- Refined Teaching topic detail page boxes for Spanish `which-pronunciation`.
- Replaced the overview admonition compass with an eye icon through the existing CSS mask icon system.
- Tuned overview and context/info box title scale, body rhythm, mobile metadata, and context box styling.

## Changes

- `Auf einen Blick` now uses a calmer title/body scale and an eye icon.
- `context`/`info_box` admonitions now share a structured box language with a light blue tint, header divider, and no pronounced left-callout treatment.
- Mobile topic metadata is smaller and more secondary.

## Verification

- Ran focused tests:
  - `.\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py::test_teaching_pilot_topic_renders_canonical_two_column_storytelling app/tests/test_research_sessions.py::test_teaching_english_which_pronunciation_renders_single_markdown_citation app/tests/test_research_sessions.py::test_teaching_topic_box_css_uses_eye_overview_and_structured_context_box -q`
- Result: `3 passed`.

## Browser QA

Captured and inspected:

- `tmp/ui-qa/2026-06-02-teaching-detail-boxes/de-desktop.png`
- `tmp/ui-qa/2026-06-02-teaching-detail-boxes/de-mobile.png`
- `tmp/ui-qa/2026-06-02-teaching-detail-boxes/en-desktop.png`
- `tmp/ui-qa/2026-06-02-teaching-detail-boxes/en-mobile.png`

Notes:

- Desktop and mobile layouts remain readable in German and English.
- Overview and context boxes keep a calm hierarchy and do not overpower the main text.
- External Datawrapper embed placeholders were visible during local QA and are unrelated to this styling change.
