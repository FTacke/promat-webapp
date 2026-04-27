# 2026-04-27 · Team Page Credits Cards and CTA Underline · Run 151

## Scope

- Reworked the public project team page on `/de/project/team` and `/en/project/team` into a scan-friendly credits and contributors surface built from shared card families.
- Kept the existing public content system and shared long-form page renderer instead of introducing a route-local page template.
- Moved CTA underline behavior to the shared interaction system so the underline spans label text and trailing arrow as one continuous unit.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Implementation

- Repaired and replaced `app/src/app/routes/public_page_content_data.py` after the file had become structurally invalid during the initial content conversion.
- Kept the canonical four public project pages and restored the Spanish design content source with localized links back into the project area.
- Converted the `team` page content to structured `meta_cards` for project lead and coordination, language corpora, Language Center context, and acknowledgements.
- Removed the old visible student-participant section from the `team` page content model.
- Extended `app/templates/pages/promat_page.html` so shared project pages can render richer metadata-card bodies, metadata rows, and contributor lists without empty body wrappers.
- Added shared `pm-meta-card` styles in `app/static/css/40_cards.css` for the new credits-card presentation.
- Updated the shared CTA-link styling in `app/static/css/30_components.css` to use a container pseudo-element underline instead of split text-decoration behavior.
- Added and updated focused regressions in `app/tests/test_research_sessions.py`.
- Updated `docs/spec/platform-data-files.md` with the accepted team-page and CTA-link UI rules.

## Key Decisions

- The team-page redesign stays inside the existing centralized content model and shared reading renderer so DE and EN remain data-driven rather than template-forked.
- The team page uses the shared metadata-card family to stay aligned with the established card system instead of adding a team-page-only component family.
- The CTA underline fix was treated as a shared interaction-system rule because the arrow is part of the CTA component, not page-local decoration.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "project_pages_render_new_navigation_without_intro_blocks or spanish_design_page_is_localized_links_to_project_pages_and_has_no_intro or team_page_uses_structured_credits_cards_without_legacy_text or shared_cta_links_use_container_underline_rule"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- Live HTML checks on `http://127.0.0.1:8000` for `/de/project/team` and `/en/project/team` confirmed:
  - localized team titles
  - lead or coordination section headings
  - corpus cards
  - acknowledgement content
- Live CSS check on `http://127.0.0.1:8000/static/css/30_components.css` confirmed the shared `.pm-cta-link::after` underline rules are present.
- Opened `/de/project/team` and `/en/project/team` in the integrated browser during the run.

## Notes

- The integrated browser could be opened successfully, but this environment did not expose browser chat tools or screenshot capture for direct DOM inspection or screenshot artifacts.
- The canonical dev start script had to fall back from local PostgreSQL port `54321` to `55432` on this Windows host because `54321` was reserved; the app still ran successfully on `127.0.0.1:8000`.
