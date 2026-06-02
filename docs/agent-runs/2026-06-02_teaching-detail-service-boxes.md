# 2026-06-02 Teaching Detail Service Boxes

## Scope

- Polished the existing Teaching detail-page citation, tip, and download/material components.
- Kept the citation box neutral and functional with the existing copy action.
- Restyled `tip_box` as a muted hint box without the former left callout accent.
- Restyled the Teaching download card as a compact material/service box with the existing download mask icon.

## Changes

- `app/templates/partials/_teaching_blocks.html`
  - Added a compact download-card header with the existing `pm-icon-mask--download` icon.
- `app/static/css/00_tokens.css`
  - Tuned `tip` admonition tokens to a slightly stronger, muted green tint.
- `app/static/css/40_cards.css`
  - Added structured tip-box divider and neutral one-pixel border.
  - Reduced citation heading, icon, copy-icon, padding, and body-text scale.
- `app/static/css/30_components.css`
  - Applied consistent Teaching topic sizing to tip and citation text.
  - Added compact material-card background, header, icon, text, CTA, and unavailable-state styles.
- `app/tests/test_research_sessions.py`
  - Added assertions for the download-card header/icon and the updated CSS component families.
  - Adjusted the `final-r` peer-review assertion to match the current empty content field.

## Verification

- `.\.venv\Scripts\pytest.exe app/tests/test_research_sessions.py -k "teaching_topic_renders_public_content_blocks or teaching_topic_box_css_uses_eye_overview_and_structured_context_box or teaching_english_topic_uses_natural_hub_backlink or teaching_english_which_pronunciation_renders_single_markdown_citation"`
  - Result: 4 passed.
- `.\.venv\Scripts\pytest.exe app/tests/test_teaching_content.py -q`
  - Result: 36 passed.
- `.\.venv\Scripts\pytest.exe app/tests/test_research_sessions.py app/tests/test_teaching_content.py -q`
  - Result after Teaching metadata expectation update: 237 passed, 1 failed.
  - Remaining non-scope failure: `test_research_workbench_builders_expose_english_shared_labels`, where `speakers_page["content_header"]["intro"]` is empty.
- Browser QA on local dev server `http://127.0.0.1:8000`
  - Routes: `/de/teaching/spanish/final-r`, `/en/teaching/spanish/final-r`, `/de/teaching/spanish/which-pronunciation`, `/en/teaching/spanish/which-pronunciation`.
  - Viewports: desktop `1440x1050`, mobile `390x844`.
  - Result: no horizontal overflow; target boxes rendered with expected muted/neutral surfaces and compact dimensions.
  - Artifacts: `tmp/ui-qa/2026-06-02-teaching-detail-service-boxes/`.
