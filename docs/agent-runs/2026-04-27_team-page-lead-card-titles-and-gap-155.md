# 2026-04-27 · Team Page Lead Card Titles and Gap · Run 155

## Scope

- Adjusted the public team pages on `/de/project/team` and `/en/project/team` in two focused ways:
  - the two upper lead cards now show short role titles first and the contributor names directly beneath,
  - the shared team-card gap is tighter so the two-row card surface reads calmer and more connected.
- Kept the accepted page structure unchanged: 2 upper lead cards, 4 corpus cards in a 2x2 grid, then prose sections for Language Center and acknowledgements.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `app/src/app/routes/public_page_content_data.py`
- `app/static/css/20_layout.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`

## Implementation

- Updated `app/src/app/routes/public_page_content_data.py` so the upper lead cards now use localized short role titles as card headings:
  - DE: `Gesamtprojektleitung`, `Ausführende Koordination`
  - EN: `Project lead`, `Executive coordination`
- Moved the concrete names into the card `text` field so they render directly beneath the heading while keeping the existing metadata rows for `Funktion` / `Schwerpunkte` and `Role` / `Focus areas` unchanged.
- Updated `app/static/css/40_cards.css` so lead-card header spacing is tighter and the name line (`.pm-meta-card--lead .pm-meta-card__text`) renders as a more prominent UI-text line directly below the title.
- Updated `app/static/css/20_layout.css` so both team grids now use the smaller shared gap `clamp(0.85rem, 1.8vw, 1.05rem)` instead of the looser container spacing.
- Updated `app/tests/test_research_sessions.py` so the focused team regression now asserts:
  - the exact DE/EN upper card titles,
  - the title-before-name order in both languages,
  - the smaller delivered team-gap rule.
- Updated `docs/spec/platform-data-files.md` so the active rule now states that the first team section uses short role headings with the contributor name directly beneath.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "team_page_uses_structured_credits_cards_without_legacy_text or team_page_uses_shared_two_column_team_grid_rules"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- Opened the live routes in the integrated browser:
  - `http://127.0.0.1:8000/de/project/team`
  - `http://127.0.0.1:8000/en/project/team`
- Live HTML/CSS checks on the running listener confirmed:
  - DE titles `Gesamtprojektleitung` and `Ausführende Koordination`
  - EN titles `Project lead` and `Executive coordination`
  - in both languages, the role title appears before the contributor name
  - exactly 6 cards still render
  - corpus cards remain in the requested 2x2 order
  - `Sprachenzentrum` / `Language Center` and `Dank` / `Acknowledgements` remain prose sections
  - the delivered CSS contains the tighter team gap rule and still keeps the 2-column grid from tablet upward
  - the delivered lead-card CSS contains the more prominent name-line styling

## Notes

- Browser pages could be opened successfully, but this environment still does not expose screenshot capture or browser DOM tooling back into chat. The visual check is therefore documented through browser opening plus explicit live HTML/CSS validation on the running dev server.
