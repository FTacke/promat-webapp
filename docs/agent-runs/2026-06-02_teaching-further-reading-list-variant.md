# 2026-06-02 Teaching Further Reading List Variant

## Scope

- Reworked the existing Teaching detail-page `further_reading` component to variant B.
- Removed the large inner card/grid treatment.
- Rendered structured further-reading items as a compact material/link list inside the warm outer container.
- Shortened the `ll/y` and `/s/` item texts in German and English.

## Changes

- `app/templates/partials/_teaching_blocks.html`
  - Changed structured further-reading items from nested `pm-card` articles to `ul`/`li` list entries.
  - Kept the CTA directly after each item text.
- `app/static/css/00_tokens.css`
  - Warmed the outer further-reading surface and restored a subtle divider token.
- `app/static/css/30_components.css`
  - Replaced `.pm-teaching-further-reading-card*` rules with compact list, item, text, and action rules.
- `content/teaching/spanish/which-pronunciation/de.yaml`
  - Shortened `ll und y` and `/s/-Abschwächung`.
- `content/teaching/spanish/which-pronunciation/en.yaml`
  - Kept the English edition aligned with the shorter material-list style.
- `app/tests/test_research_sessions.py`
  - Added assertions that the further-reading section renders as a list, has no card classes, and keeps two direct CTAs.

## Verification

- `.\.venv\Scripts\pytest.exe app/tests/test_research_sessions.py -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation or teaching_topic_box_css_uses_eye_overview_and_structured_context_box" -q`
  - Result: 3 passed.
- `.\.venv\Scripts\pytest.exe app/tests/test_teaching_content.py -q`
  - Result: 36 passed.
- Browser QA on local QA server `http://127.0.0.1:8011`
  - Routes: `/de/teaching/spanish/which-pronunciation`, `/en/teaching/spanish/which-pronunciation`.
  - Viewports: desktop `1440x1000`, mobile `390x844`.
  - Result: no horizontal overflow, `cardCount: 0`, list entries stacked with subtle dividers, CTA directly after short text.
  - Artifacts: `tmp/ui-qa/2026-06-02-teaching-further-reading-list/`.
