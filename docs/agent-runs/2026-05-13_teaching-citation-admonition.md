# Teaching Citation Admonition

## Scope

- moved the Teaching `citation` block from a dedicated template branch onto the shared admonition system as the new `citation` variant
- added the shared header action slot needed for the copy button without introducing a second citation-box component
- mirrored the new variant in the public Sample admonition overview and documented the active contract in the platform spec

## Implementation

- extended `app/templates/partials/_admonition.html` with an optional header action area and live-status slot
- added token-based `citation` styling in `app/static/css/00_tokens.css` and `app/static/css/40_cards.css`
- rewired Teaching citation rendering in `app/templates/partials/_teaching_blocks.html` to `render_admonition(...)`
- normalized citation payloads in `app/src/app/teaching_content.py` to provide rendered citation body blocks and copy-only citation text
- added bilingual copy labels in `app/src/app/i18n.py`
- added shared core JS clipboard handling in `app/static/js/modules/core/teaching-citation-copy.js`
- updated Sample admonition data in `app/src/app/routes/public.py` to expose the new `citation` variant with its copy action
- updated `docs/spec/platform-data-files.md` with the active Teaching citation-admonition rule

## Validation

### Pytest

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q -k citation`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_topic_uses_natural_hub_backlink or sample_page_places_admonitions_before_pattern_lab_with_visible_titles or sample_page_localizes_admonitions_in_english"`

### Browser QA

Artifacts: `tmp/ui-qa/2026-05-13-teaching-citation-admonition/`

- `capture_citation_qa.py` captured desktop and mobile screenshots for:
  - `/de/teaching/spanish/which-pronunciation`
  - `/en/teaching/spanish/which-pronunciation`
  - `/de/sample`
- `summary.json` confirmed localized titles and copy-button labels on all captured surfaces
- `verify_citation_copy.py` confirmed `data-copy-state="done"`, localized success labels, and clipboard contents for DE topic, EN topic, and DE Sample

## Notes

- the current DE `which-pronunciation` source file contained an invalid top-level citation quote; the run fixed that YAML syntax so the productive route could render again
- the broad storytelling regression for `which-pronunciation` was refreshed to the current editorial content where peer review is optional and several older text assertions no longer matched the live YAML
