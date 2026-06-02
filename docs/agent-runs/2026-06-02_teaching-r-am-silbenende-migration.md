# 2026-06-02 - Teaching r-am-silbenende migration

## Scope

- Replaced the interim `final-r` preparation page with the new YAML-backed Spanish Teaching topic `r-am-silbenende` in `de` and `en`.
- Removed the preview-only placeholder block renderer and its dashed placeholder styling from the Teaching block system.
- Updated the Spanish Teaching hubs and local topic cross-links to the new slug.

## Content changes

- Added `content/teaching/spanish/r-am-silbenende/de.yaml` from the supplied German structure, with technically necessary adaptation to the active Teaching model:
  - `tip_box` instead of a custom preview-only teaching-perspective box
  - `audio_examples` with an empty state instead of a fake player module
  - `download` with status text instead of a fake download CTA
  - plain text sections via `section_heading` plus `text` blocks in the normal topic flow
- Added `content/teaching/spanish/r-am-silbenende/en.yaml` as the aligned English edition.
- Removed the old `content/teaching/spanish/final-r/*.yaml` topic files.

## Renderer cleanup

- Removed the Teaching `placeholder` block branch from `app/src/app/teaching_content.py`.
- Removed the corresponding Jinja block in `app/templates/partials/_teaching_blocks.html`.
- Removed the dashed placeholder token/style definitions from `app/static/css/00_tokens.css` and `app/static/css/30_components.css`.

## Link and hub updates

- Updated `content/teaching/spanish/hubs/de.yaml` and `content/teaching/spanish/hubs/en.yaml` from `final-r` to `r-am-silbenende`.
- Updated internal Spanish Teaching topic references in `content/teaching/spanish/r/de.yaml` and `content/teaching/spanish/soft-spanish-hard-german/de.yaml`.
- Updated QA helper routes in `scripts/qa/capture_qa.py` and `scripts/qa/capture_qa.ps1`.

## Validation

- `python scripts/validate_teaching_content.py`
- `python -m pytest app/tests/test_teaching_content.py -q`
- Focused route regressions in `app/tests/test_research_sessions.py` for the Spanish hub and the new detail route
- Browser QA on:
  - `/de/teaching/spanish`
  - `/en/teaching/spanish`
  - `/de/teaching/spanish/r-am-silbenende`
  - `/en/teaching/spanish/r-am-silbenende`
- Mobile QA confirmed no horizontal overflow on the German detail page and English hub, with the audio empty state and material status rendered as quiet non-interactive states.