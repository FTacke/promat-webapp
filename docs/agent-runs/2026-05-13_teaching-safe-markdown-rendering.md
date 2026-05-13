# Teaching Safe Markdown Rendering

## Scope

- centralized safe Markdown rendering for visible Teaching YAML prose on hub and topic pages
- kept technical machine-value fields such as token IDs, raw URLs, and public audio paths out of the Markdown pass
- aligned top-level Teaching citation metadata with the shared admonition-based citation surface and plain-text copy behavior

## Implementation

- extended `app/src/app/teaching_content.py` with centralized helpers for inline, block, multi-block, and plain-text Markdown rendering
- normalized visible Teaching payload fields to companion `*_html` or plain-text values instead of rendering raw Markdown in templates
- updated shared Teaching templates and the shared admonition/content-header partials to prefer normalized HTML fields where present
- made top-level `citation` metadata the canonical Teaching citation source, with plain-text `copy_text` support and duplicate legacy citation-block suppression
- migrated the English `which-pronunciation` topic content to the top-level citation contract
- documented the active Markdown contract in `docs/spec/platform-data-files.md`

## Validation

### Pytest

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation or teaching_english_topic_uses_natural_hub_backlink or sample_page_places_admonitions_before_pattern_lab_with_visible_titles or sample_page_localizes_admonitions_in_english"`

### Browser QA

Artifacts: `tmp/ui-qa/2026-05-13-teaching-markdown/`

- captured desktop screenshots for `/de/teaching/spanish/which-pronunciation` and `/en/teaching/spanish/which-pronunciation`
- verified both live routes on the running local server at `127.0.0.1:8000`
- confirmed rendered `<em>` and `<code>` markup, one citation admonition per route, clickable citation link output, and absence of raw citation/topic Markdown markers in live HTML

## Notes

- the integrated `open_browser_page` tool remained broken in this session (`browserContext.newPage: Cannot read properties of undefined (reading '_page')`), so browser QA used Playwright directly from the workspace Python environment instead
- route regressions now assert real rendered Markdown signals for `which-pronunciation` in addition to the existing storytelling and Sample checks
