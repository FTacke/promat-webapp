# Teaching Title Inline Markdown

## Scope

- fixed the remaining Teaching topic title paths that still rendered raw inline Markdown markers instead of the normalized `title_html` values
- covered section headings on topic pages plus audio block title paths that bypassed the existing shared Markdown normalization
- added focused regressions so title fields keep inline Markdown semantics without introducing block markup inside headings

## Implementation

- updated `app/templates/pages/teaching_page.html` so topic-section headings render `section.heading.title_html` before falling back to plain text
- updated `app/templates/partials/_teaching_blocks.html` so collapsible audio-example summaries and audio-contrast headers render `block.title_html` before falling back to plain text
- left technical fields and non-editorial machine values unchanged

## Validation

### Pytest

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation"`

### Browser QA

Artifacts: `tmp/ui-qa/2026-05-13-title-inline-markdown/`

- captured `which-pronunciation-de-headings.png` from the live DE topic route
- confirmed live heading innerHTML for the affected title paths contains inline markup instead of raw markers:
  - section heading: `<em>Seseo</em> ...`
  - contrast title: `Mit und ohne Unterscheidung: <em>casa</em> vs. <em>caza</em>`
  - admonition title: `Noch ein Aussprachemerkmal: <code>ll</code> und <code>y</code>`
- confirmed no paragraph wrapper was introduced inside those heading surfaces

## Notes

- the integrated `open_browser_page` tool remained unavailable in this session, so browser QA again used Playwright from the workspace Python environment
- the VS Code static analyzer still reports pre-existing test-environment typing/import warnings in `app/tests/test_teaching_content.py`; this run did not change or worsen those warnings
