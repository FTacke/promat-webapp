# Teaching Mobile Drawer Navigation

Date: 2026-06-03

Summary:
- Reused the shared PROMAT panel data path for Teaching mobile drawer context navigation.
- Added Teaching drawer states for language selection, language hubs, and topic pages without enabling a desktop Teaching sidebar.
- Updated the active platform spec and focused route regressions for the exact visible Drawer labels and exclusions.

Verification:
- `.\.venv\Scripts\python.exe -m pytest app\tests\test_research_sessions.py -k "teaching_overview or teaching_language_root or teaching_french_hub or teaching_english_hub or teaching_empty_hubs or teaching_topic_renders_public_content_blocks or modal_drawer_context"`
- Browser QA with Playwright against `http://127.0.0.1:8077` for `/de/teaching`, `/de/teaching/spanish`, `/de/teaching/spanish/r-am-silbenende`, `/de/teaching/french`, and `/en/teaching/spanish`; artifacts in `tmp/ui-qa/2026-06-03-teaching-mobile-drawer/`.

Residual:
- Full `app\tests\test_teaching_content.py` still has one pre-existing builder expectation mismatch around `section_heading` retention in `test_build_teaching_topic_page_parses_teaching_impulses`; unrelated to the drawer route/config change.
