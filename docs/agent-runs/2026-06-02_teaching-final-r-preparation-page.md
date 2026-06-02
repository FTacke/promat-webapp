# 2026-06-02 - Teaching final-r preparation page

## Scope

- Reworked the Spanish Teaching topic `final-r` into a public preparation page titled `R am Silbenende`.
- Kept the existing English technical slug `final-r` to follow repo rules against new German technical slugs.
- Removed fake citation, credits, download, audio, and next-topic production blocks from the page content.
- Added compact `status_box` and `placeholder` Teaching block types for honest preparation-state modules.
- Added status metadata rendering via the shared Teaching metadata row.

## Validation

- `.venv\Scripts\python.exe -m pytest app\tests\test_teaching_content.py -q` passed.
- Focused Teaching route tests in `app\tests\test_research_sessions.py` passed.
- Full run of `app\tests\test_teaching_content.py app\tests\test_research_sessions.py -q` passed for 238 tests and retained one unrelated Research failure:
  `test_research_workbench_builders_expose_english_shared_labels`.
- Browser QA via Playwright covered:
  `/de/teaching/spanish/final-r`, `/en/teaching/spanish/final-r`, `/de/teaching/spanish`, `/en/teaching/spanish`
  on desktop and mobile.
- Screenshots and QA helper scripts are under `tmp/ui-qa/2026-06-02-teaching-final-r-prep/`.
