# 2026-04-27 · Team Page Two-Column Grid · Run 153

## Scope

- Tightened the public team-page layout on `/de/project/team` and `/en/project/team` to one calmer shared two-column card grid.
- Kept the existing content model: only the lead/coordination and language-corpora sections remain card-based.
- Preserved `Sprachenzentrum` / `Language Center` and `Dank` / `Acknowledgements` as normal reading text rather than cards.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/static/css/20_layout.css`
- `app/templates/pages/promat_page.html`
- `app/templates/pages/sample_page.html`
- `app/src/app/routes/public_page_content_data.py`
- `app/tests/test_research_sessions.py`

## Implementation

- Updated `app/static/css/20_layout.css` so `pm-grid--team-lead` and `pm-grid--team-corpus` now share the same layout rule:
  - one column by default,
  - two equal-width columns from `760px` upward,
  - no wider breakpoint that turns the corpus section into a four-column row.
- Reduced the team-grid spacing to `var(--pm-space-container)` so the cards sit closer together than the generic metadata grid.
- Updated `app/tests/test_research_sessions.py` so the focused team regression now also asserts:
  - the requested lead-card order,
  - the requested corpus-card order `Spanish/French/German/English` in DE and EN,
  - the delivered CSS rule for the shared two-column team grid,
  - the absence of any `repeat(4, minmax(0, 1fr))` team layout.
- Updated `docs/spec/platform-data-files.md` so the accepted team-page rule explicitly records the shared calm two-column desktop/tablet grid with single-column mobile fallback.

## Key Decisions

- The layout fix stays entirely in shared CSS via the existing `team-lead` and `team-corpus` modifiers; no route-local template variant or inline style was introduced.
- Equal card width is achieved by making both team sections use the same two-column grid width, not by forcing special card widths per section.
- The mobile requirement is satisfied through the base single-column rule rather than a separate mobile-only override.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "team_page_uses_structured_credits_cards_without_legacy_text or team_page_uses_shared_two_column_team_grid_rules"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- Opened the live routes in the integrated browser:
  - `http://127.0.0.1:8000/de/project/team`
  - `http://127.0.0.1:8000/en/project/team`
- Live HTML/CSS checks against the running listener confirmed:
  - DE and EN titles are correct,
  - exactly 6 cards render,
  - lead cards remain `Felix Tacke` then `Marlon Merte`,
  - corpus cards remain ordered `Spanish`, `French`, `German`, `English`,
  - `Sprachenzentrum` / `Language Center` and `Dank` / `Acknowledgements` remain normal text,
  - delivered CSS contains the base single-column team rule,
  - delivered CSS contains the two-column rule from `760px`,
  - delivered CSS contains the tighter team gap,
  - delivered CSS no longer contains any four-column team-grid rule.

## Notes

- Browser pages could be opened successfully, but this environment still did not expose screenshot capture or browser DOM tooling back into chat. The visual pass is therefore documented through browser opening plus concrete live HTML/CSS validation on the running dev server.
