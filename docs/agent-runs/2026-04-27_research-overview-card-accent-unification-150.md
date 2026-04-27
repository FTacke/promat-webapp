# 2026-04-27 · Research Overview Card Accent Unification · Run 150

## Scope

- Unified the top accent bar of the corpus cards on the public research overview page.
- Kept the change scoped to the research overview corpus-card group only.
- Preserved corpus- or language-specific accent colors on other card surfaces.

## Implementation

- Updated `app/src/app/routes/public_content.py` so research overview corpus cards receive a dedicated modifier class in addition to their existing language class.
- Updated `app/static/css/40_cards.css` so only corpus cards with that dedicated research-overview modifier override their top border color to the shared primary-blue token `var(--promat-primary)`.
- Updated `app/tests/test_research_sessions.py` so the real research overview and the mirrored sample surface both assert the shared-accent modifier.
- Updated `docs/spec/platform-data-files.md` so the accepted rule for research overview corpus-card accents is explicit in the active UI spec.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "research_overview_renders_structured_corpus_metadata_and_dynamic_counts or research_overview_localizes_structured_corpus_cards_in_english or sample_page_reflects_current_landing_and_corpus_cards"`
- Live runtime checks on:
  - `http://127.0.0.1:8000/de/research`
  - `http://127.0.0.1:8000/en/research`
  - `http://127.0.0.1:8000/static/css/40_cards.css`
  confirmed the shared-accent class is present in both languages and the delivered CSS override points to `var(--promat-primary)`.
- Opened `/de/research` and `/en/research` in the integrated browser for runtime inspection.

## Notes

- `sample` needed no template update in this run because the mirrored research corpus cards already come from the live research overview builder; the mirror changed automatically once the productive builder class changed.
- The current environment allowed opening the real pages in the browser, but did not expose screenshot capture or browser DOM inspection back into chat tools, so runtime verification combined live delivered HTML/CSS checks with browser opening.
