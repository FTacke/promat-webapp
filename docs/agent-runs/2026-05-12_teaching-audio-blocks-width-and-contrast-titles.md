# 2026-05-12 Teaching Audio Blocks Width And Contrast Titles

## Scope

Fokussierter UI-/Content-Fix fuer die Audio-Bloecke im Teaching-Topic `which-pronunciation`.

## Changes

- updated the two `audio_contrast` titles in DE/EN to the requested didactic wording
- changed the shared contrast transcript presentation from a standalone pill to a labeled sequence row with localized `Wortfolge` / `Word sequence`
- added localized transcript-row labels in the shared teaching label payload and i18n catalog
- widened `span: 2` audio material blocks so `audio_contrast` and `audio_examples` explicitly stretch to the full available topic content width instead of relying on default panel behavior
- strengthened `audio_contrast` title styling so it reads as a real material block title instead of a small label
- aligned comparison-card players to the bottom of their cards
- softened the inner contrast cards by removing the stronger inner accent rail and using a calmer border/background treatment
- kept the shared `audio_examples` material block wide, with the existing 2x2 desktop grid and one-column mobile stacking preserved

## Files Changed

- `app/templates/partials/_teaching_blocks.html`
- `app/templates/pages/teaching_page.html`
- `app/src/app/i18n.py`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`
- `docs/spec/platform-data-files.md`

## Validation

- focused route test passed:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k teaching_pilot_topic_renders_canonical_two_column_storytelling`
- focused browser QA passed on the live app:
  - DE and EN contrast blocks measured `1056px`
  - DE and EN audio-examples block measured `1056px`
  - both matched their parent teaching block width
  - DE shows `Wortfolge` twice; EN shows `Word sequence` twice
  - first contrast-card players were aligned with a measured top delta of `0.0px`
  - the audio-examples block still renders four items in a 2x2 desktop grid
  - mobile DE keeps the examples stacked in one column

## Notes

- no routing, auth, research, or collapsible behavior was changed
- the rest of the lower page sections were intentionally left untouched in this run