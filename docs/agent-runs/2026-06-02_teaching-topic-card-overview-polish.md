# Teaching Topic Card Overview Polish

## Scope

Polished public Teaching language-hub topic cards, especially `/de/teaching/spanish` and `/en/teaching/spanish`.

## Changes

- Removed the rendered author byline from Teaching topic overview cards while leaving topic-page metadata and citation paths intact.
- Added central Teaching topic-card tokens based on the existing overview/admonition accent family.
- Gave available topic cards a warm tinted surface, stronger accent border, clearer CTA color, and subtle hover movement/shadow.
- Gave pending cards the same structure with muted tint, low-contrast accent, default cursor, no CTA, and bottom-aligned status.
- Updated focused hub render regressions to assert that card bylines are absent in German and English.

## Verification

- Passed focused tests:
  - `.\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py::test_teaching_language_root_uses_shared_topbar_and_mobile_drawer app/tests/test_research_sessions.py::test_teaching_english_hub_stays_within_english_edition_topics app/tests/test_teaching_content.py::test_build_teaching_hub_page_groups_topics_and_sets_back_link app/tests/test_teaching_content.py::test_build_teaching_hub_page_keeps_unpublished_topics_as_unavailable_cards -q`
- Broader check `.\.venv\Scripts\python.exe -m pytest app/tests/test_teaching_content.py app/tests/test_research_sessions.py -q` still has three pre-existing/orthogonal failures around peer-review metadata and an English research workbench intro; the four in-scope tests pass.
- Browser QA on local dev server:
  - `/de/teaching/spanish` desktop and mobile
  - `/en/teaching/spanish` desktop and mobile
  - `/de/teaching` desktop regression for the unchanged language-selection card family
- Screenshot artifacts:
  - `tmp/ui-qa/2026-06-02-teaching-topic-cards/de-desktop.png`
  - `tmp/ui-qa/2026-06-02-teaching-topic-cards/de-mobile.png`
  - `tmp/ui-qa/2026-06-02-teaching-topic-cards/en-desktop.png`
  - `tmp/ui-qa/2026-06-02-teaching-topic-cards/en-mobile.png`
  - `tmp/ui-qa/2026-06-02-teaching-topic-cards/de-teaching-overview-regression.png`
