# 2026-05-25 Intake Consent And Exposure Alignment

## Scope

- Updated the active intake workbook contract for secure consent fields, expanded standard varieties, and revised exposure parsing semantics.
- Implemented the matching parser, importer, runtime metadata, DB model, and protected research UI stay rendering changes.
- Added focused pytest coverage for workbook parsing, importer mapping, and protected research stay presentation.

## Notes

- `consent_signed` remains accepted only as a deprecated fallback for `research_consent_signed` with an explicit warning.
- `unspecified` exposure type now normalizes to `unknown` with a warning and is hidden as a visible UI label.
- Runtime metadata now carries protected internal fields such as consent flags and internal notes for research-only contexts.