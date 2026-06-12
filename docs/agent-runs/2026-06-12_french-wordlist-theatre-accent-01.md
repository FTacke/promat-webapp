# 2026-06-12 French Wordlist Theatre Accent

## Summary

- Corrected the French wordlist item `wl_014` from `théatre` to `théâtre` in the runtime catalog.
- Applied the same correction to existing French session alignment JSON artifacts.
- Updated the research preset regression expectation.

## Validation

- `rg -n --hidden --no-ignore "théatre" app data public secure` returned no matches.
- `.venv\Scripts\python.exe -m pytest app/tests/test_research_presets.py` passed: 15 tests.
