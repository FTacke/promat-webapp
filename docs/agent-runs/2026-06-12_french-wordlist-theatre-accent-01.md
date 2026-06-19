# 2026-06-12 French Wordlist Theatre Accent

## Summary

- Corrected the former French wordlist misspelling for `wl_014` to `théâtre` in the runtime catalog.
- Applied the same correction to existing French session alignment JSON artifacts.
- Updated the research preset regression expectation.

## Validation

- A repository-wide search for the former misspelling returned no matches in app, runtime, public, or secure data.
- `.venv\Scripts\python.exe -m pytest app/tests/test_research_presets.py` passed: 15 tests.
