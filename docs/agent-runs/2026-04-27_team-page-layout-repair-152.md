# 2026-04-27 · Team Page Layout Repair · Run 152

## Scope

- Repaired the public project team pages on `/de/project/team` and `/en/project/team` so they read as intentional credits surfaces instead of cramped mini-card grids.
- Kept the implementation inside the existing shared public content model and shared card/layout system.
- Restored normal reading-text sections for Language Center and acknowledgements instead of rendering those blocks as extra cards.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/src/app/routes/public_page_content_data.py`
- `app/templates/pages/promat_page.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/20_layout.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`

## Implementation

- Updated `app/src/app/routes/public_page_content_data.py` so the team page now contains exactly two card sections:
  - `Projektleitung und Koordination` / `Project lead and coordination`
  - `Sprachkorpora` / `Language corpora`
- Marked those sections explicitly with `meta_cards_layout` values `team-lead` and `team-corpus` so the shared renderer can apply page-appropriate grid widths without affecting unrelated card groups.
- Converted `Sprachenzentrum` / `Language Center` and `Dank` / `Acknowledgements` back to normal reading sections via `paragraphs_html`, with the acknowledgement names rendered through the existing bullet-list path.
- Updated `app/static/css/20_layout.css` so:
  - the lead section uses one column on small widths and two columns from tablet upward,
  - the corpus section uses one column on small widths, two columns through the normal reading-content widths, and only allows four columns on very wide viewports.
- Updated `app/static/css/40_cards.css` so the team metadata cards keep the shared card padding and calmer internal spacing instead of collapsing to edge-hugging content.
- Updated `app/tests/test_research_sessions.py` to assert the accepted team-page structure: exactly six cards, lead/corpus grid classes present, no info-card fallback, no table, and the normal prose/list content still visible.
- Updated `docs/spec/platform-data-files.md` so the active rule now states explicitly that only the first two team sections use cards while Language Center and acknowledgements remain reading text.

## Key Decisions

- The fix stays shared and data-driven: the renderer still supports explicit card sections, but only sections that opt in via `meta_cards` render as cards.
- The team-specific layout tuning happens through explicit shared grid modifiers (`team-lead`, `team-corpus`) rather than a page-local inline-style or a forced global change to every metadata-card grid.
- Card padding was repaired by returning to the normal shared card container spacing instead of introducing a second custom inner-padding system for the team page.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "team_page_uses_structured_credits_cards_without_legacy_text or sample_page_reflects_current_landing_and_corpus_cards or project_pages_render_new_navigation_without_intro_blocks"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- Opened these live routes in the integrated browser:
  - `http://127.0.0.1:8000/de/project/team`
  - `http://127.0.0.1:8000/en/project/team`
- Live HTML/CSS checks on the running listener confirmed:
  - DE and EN page titles are correct
  - exactly 6 cards render on each route
  - no `pm-meta-card--info` blocks remain
  - `Sprachenzentrum` / `Language Center` is normal text
  - `Dank` / `Acknowledgements` is normal text plus list
  - no intro block and no visible table remain
  - locale switch links to the matching team route in the other language
  - the delivered shared CSS contains the dedicated `team-lead` and `team-corpus` grid rules
  - the old `padding: 0` override for `.pm-meta-card` is no longer present in the delivered card CSS

## Notes

- The current environment allowed opening the real routes in the browser and verifying the delivered live HTML/CSS, but it did not expose screenshot capture or browser DOM inspection back into chat tools. This run therefore documents a concrete live browser check plus server-delivered HTML/CSS validation rather than attached screenshots.
