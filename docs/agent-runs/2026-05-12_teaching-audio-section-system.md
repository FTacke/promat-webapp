# 2026-05-12 Teaching Audio Section System

## Scope

Fokussierte Vereinheitlichung der Audio-/Hörvergleich-Komponenten im Teaching-Topic `which-pronunciation`.

## Changes

- aligned `audio_contrast` and `audio_examples` to one shared surface family with:
  - `.audio-section`
  - `.audio-section-header`
  - `.audio-section-title`
  - `.audio-section-description`
  - `.audio-grid`
  - `.audio-card`
- moved both audio families from a left-accent rail to a calmer card container with neutral border and top accent
- applied the icon/title/header rhythm consistently to both the contrast and examples sections
- changed the examples title to `Seseo in authentischen Audioausschnitten` / `Seseo in authentic audio excerpts`
- replaced visible backtick-based didactic markup in the affected DE/EN YAML with strong and emphasis markup
- moved transcript token IDs into a quieter lower-right `audio-token` position inside the quote box and prevented automatic uppercase transformation
- kept the existing audio assets and block contents intact

## Files Changed

- `app/templates/partials/_teaching_blocks.html`
- `app/static/css/30_components.css`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
- `app/tests/test_research_sessions.py`
- `docs/spec/platform-data-files.md`

## Validation

- focused route test passed:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k teaching_pilot_topic_renders_canonical_two_column_storytelling`
- focused live browser QA passed:
  - 3 `.audio-section` blocks on the DE route
  - first shared audio section measured `border-top-width: 4px` and `border-left-width: 1px`
  - EN examples title rendered as `Seseo in authentic audio excerpts`
  - no backticks remained in `.audio-section` text
  - token `MEXb80def27c` remained present inside the quote area
  - contrast-card players remained bottom-aligned

## Notes

- this run intentionally changed only the teaching audio surfaces on `which-pronunciation`
- routing, auth, research behavior, and audio assets were left untouched