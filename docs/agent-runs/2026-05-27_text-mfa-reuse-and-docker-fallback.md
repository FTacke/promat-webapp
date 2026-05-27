# 2026-05-27 Text MFA Reuse and Docker Fallback

## Summary

Hardened the research-intake text pipeline so unchanged working inputs can reuse current text alignment outputs, cached MFA outputs can be imported without rerunning MFA, and the central importer falls back to Docker-backed MFA when the host `mfa` CLI is unavailable.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_production_importer.py -q -k "text_pipeline or detect_working_text_requires_preparation_when_alignment_json_missing"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_production_importer.py -q`
