# 2026-06-02 Teaching Impulse And Further Reading Calm Pass

## Scope

- Targeted follow-up for two existing Teaching topic-detail components only:
  - `Impulse für den Unterricht` / `Classroom prompts`
  - `Vertiefung` / `Further exploration`

## Changes

- `content/teaching/spanish/which-pronunciation/de.yaml`
  - Reduced the didactic-close impulse list from four items to three short classroom actions.
  - Removed the former own-pronunciation-decision impulse.
  - Changed further-reading CTA labels to `Hier mehr erfahren`.
- `content/teaching/spanish/which-pronunciation/en.yaml`
  - Kept the English edition aligned with the new three-prompt structure.
  - Changed further-reading CTA labels to `Learn more here`.
- `app/static/css/30_components.css`
  - Kept the rose didactic-close outer block.
  - Removed the 2-column impulse layout and inner-card treatment.
  - Rendered impulse entries as compact one-column flow items with small number badges above titles.
  - Removed hard inner borders and border-left styling from the impulse entries.
  - Calmed the further-reading list: no divider after intro, only a very subtle divider between entries, quieter titles, smaller/lighter CTA links.
- `app/tests/test_research_sessions.py`
  - Added regression assertions for the three new impulse texts, removed legacy prompt assertions, and asserted the quieter further-reading CTA labels and CSS rules.

## Verification

- `.\.venv\Scripts\pytest.exe app/tests/test_research_sessions.py -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_which_pronunciation_renders_single_markdown_citation or teaching_topic_box_css_uses_eye_overview_and_structured_context_box" -q`
  - Result: 3 passed.
- `.\.venv\Scripts\pytest.exe app/tests/test_teaching_content.py -q`
  - Result: 36 passed.
- Browser QA on local QA server `http://127.0.0.1:8012`
  - Routes: `/de/teaching/spanish/which-pronunciation`, `/en/teaching/spanish/which-pronunciation`.
  - Viewports: desktop `1440x1000`, mobile `390x844`.
  - Result: no horizontal overflow; impulse list is one-column with three entries; no inner impulse borders; further-reading `cardCount: 0`; CTA links are lighter and smaller.
  - Artifacts: `tmp/ui-qa/2026-06-02-teaching-impulse-further-reading-calm/`.
