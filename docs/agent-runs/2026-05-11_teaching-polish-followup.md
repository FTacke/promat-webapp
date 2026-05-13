# Teaching polish follow-up after layout-grid refinement

## Scope

- keep the accepted Teaching root, hub, and topic architecture from the previous layout-grid run
- refine only the visual composition of Teaching root rows, hub group alignment, and topic section flow
- keep Sample synchronized with the productive Teaching patterns

## Changes

- reworked the shared Teaching selection-row rendering in `app/templates/partials/_corpus_card.html` and `app/static/css/30_components.css`
- made the root rows more compact and horizontally structured with title, muted status, and right-aligned CTA on desktop while preserving a compact clickable mobile wrap
- kept the root list neutral and single-column with no language-color markers, teaser copy, or banner-card treatment
- aligned Teaching hub group headers with the same left edge as their card grid in `app/templates/pages/teaching_page.html`, `app/templates/pages/sample_page.html`, and `app/static/css/20_layout.css`
- removed the artificial demo regrouping in `content/teaching/spanish/de/index.yaml` so `Weiches Spanisch, hartes Deutsch` returns to `Grundlagen`
- moved the topic follow-up section heading wrapper in `app/templates/partials/_teaching_blocks.html` onto full grid width so `Weitere Themen` reads as one clean section instead of a nested narrow heading
- tuned Teaching block-grid rhythm slightly to reduce the technical demo feel without adding masonry, height logic, or card variants
- updated focused route tests in `app/tests/test_research_sessions.py` to assert the refined root-row structure, corrected Spanish hub grouping, topic-section heading wrapper, and synchronized Sample markup
- updated the active UI contract in `docs/spec/platform-data-files.md`

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_overview_keeps_language_selection_label or teaching_language_root_uses_shared_topbar_and_mobile_drawer or teaching_topic_renders_public_content_blocks or sample_page_reflects_current_landing_and_corpus_cards"` -> 4 passed
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_overview_keeps_language_selection_label or sample_page_reflects_current_landing_and_corpus_cards"` after the root-row CSS repair -> 2 passed
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q` -> 10 passed
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k teaching` -> 14 passed, 183 deselected
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k sample_page_reflects_current_landing_and_corpus_cards` -> 1 passed, 196 deselected
- browser QA completed for `/de/teaching`, `/de/teaching/spanish`, `/de/teaching/english`, `/de/teaching/spanish/final-r`, `/en/teaching`, `/en/teaching/spanish`, `/de/sample`
- final fresh browser artifacts were written to `tmp/ui-qa/2026-05-11-teaching-polish-followup-fresh`

## Notes

- no routing changes
- no Research auth or data-path dependencies introduced
- no visible edition pills were reintroduced in Teaching page bodies
- Sample continues to mirror the productive Teaching root and hub patterns rather than defining them
- the only editor diagnostics after the run were pre-existing `color-mix` compatibility warnings in `app/static/css/30_components.css` and the longstanding macro-local list-item lint warning in `app/templates/partials/_teaching_blocks.html`