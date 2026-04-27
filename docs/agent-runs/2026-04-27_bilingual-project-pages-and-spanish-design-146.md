# 2026-04-27 · Bilingual Project Pages and Spanish Design · Run 146

## Scope

- Replaced the visible public project-page structure with the canonical four-page order `about`, `structure`, `data-methods`, `team` in German and English.
- Reworked the public Spanish design page into a localized DE/EN long-form page and added meaningful internal links back into the project area.
- Kept the shared inner shell, shared routing, and shared translation system instead of introducing route-local templates or visible language branching.

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
- `docs/plans/project_pages/project_pages_content_german_english.md`
- `https://hispanistica.com/projects/promat/`

## Implementation

- Added `app/src/app/routes/public_page_content_data.py` as the centralized bilingual content source for the four project pages plus the Spanish design page.
- Stored the project-video embed configuration there as `PROJECT_VIDEO_YOUTUBE_ID = "ucvpPAONGoY"` after verifying the source on the Hispanistica project page.
- Follow-up content adjustments replaced the old `marele.hispanistica.com` references with the requested `https://hispanistica.com/projects/marele/` target and linked visible `MAR.ELE` references directly in the project and Spanish design prose.
- Aligned the project team page title with the existing shared navigation label so the public project area now uses one consistent team label in page titles and cross-links.
- Updated `app/src/app/routes/public_content.py` to localize project pages through shared content data, expose `structure` as the visible second project page, and reuse the same localization path for the public Spanish design page.
- Updated `app/src/app/routes/public.py` so `/project/research-design` is legacy redirect-only and returns a `308` redirect to `/project/structure` in both UI languages.
- Extended `app/templates/pages/promat_page.html` plus shared CSS in `app/static/css/20_layout.css` and `app/static/css/30_components.css` so the existing long-form page renderer can now handle localized rich paragraphs, HTML bullets, tables, and embedded media blocks without page-local hacks.
- Added `app/static/js/modules/core/external-links.js` and registered it from the shared core entry so external HTTP(S) links open in a new tab/window across the app without per-link manual targets.
- Updated `app/src/app/i18n.py` to expose the new project labels while keeping the legacy `project.research-design` label key only for compatibility.
- Added focused route and content regressions in `app/tests/test_research_sessions.py`.
- Extended those regressions so both `/de/project/research-design` and `/en/project/research-design` are covered explicitly, and so the project root verifies that no visible standalone `Forschungsdesign` / `Research Design` project-nav label remains.
- Updated the active platform spec in `docs/spec/platform-data-files.md` so the canonical visible public project order and the legacy-only status of `research-design` are now explicit active rules.

## Key Decisions

- Project pages intentionally omit the old subtitle or intro block and start directly with section content inside the shared reading layout.
- The Spanish design page now follows the same no-intro reading pattern and uses localized internal links to the project pages instead of keeping that context implicit.
- `sample` was not changed in this run because the new behavior is content-rendering capability for real long-form pages, not a mirrored active sample element with a changed accepted layout contract.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "project_about_page_embeds_video_and_hides_intro or spanish_design_page_is_localized_links_to_project_pages_and_has_no_intro"`
- Live HTML validation on the active local listener `http://127.0.0.1:8000` for:
  - `/de/project/about`
  - `/en/project/about`
  - `/de/research/spanish/design`
  - `/en/research/spanish/design`
- The live HTML check confirmed for all four routes:
  - heading present
  - no intro/subtitle block under the content header
  - locale switch points to the same route in the other UI language
  - legacy `/project/research-design` is not visible in navigation
  - expected sidebar navigation labels are present in the requested order
  - the YouTube iframe is present on both project about pages
- The follow-up live HTML check additionally confirmed the new `MAR.ELE` link target on all four routes and the updated `Lehre@Philipp 2025` video caption on both project about pages.
- Additional live checks on `http://127.0.0.1:8000` confirmed:
  - `/de/project/research-design` redirects to `/de/project/structure`
  - `/en/project/research-design` redirects to `/en/project/structure`
  - `/de/project` and `/en/project` do not expose the old standalone project-page labels `Forschungsdesign` / `Research Design` as visible nav entries
- Opened the same four routes in the integrated browser on port `8000` for manual browser validation.

## Notes

- Browser pages could be opened successfully, but no screenshot-capture or browser-content tool was available in this environment for artifact capture beyond the live HTML checks.
- The active local listener for this validation was `127.0.0.1:8000`; port `8010` was not reachable during this run.