# 2026-05-11 Teaching Public Rawbau

## Scope

- Implement the public Teaching rawbau from `docs/plans/teaching_section_raw.md` as a file-based, fully public surface.
- Keep Research access, player routing, and auth behavior unchanged.
- Deliver a working edition hub plus topic pages for Spanish, including localized routing, edition switching, placeholder media handling, and production-path wiring for repo-root Teaching content.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/plans/teaching_section_raw.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Changes

- Added a new Teaching content layer in `app/src/app/teaching_content.py` that reads YAML from `content/teaching`, resolves edition fallback, maps topic equivalents, builds hub/topic page payloads, and keeps Teaching-specific language switching separate from Research logic.
- Wired the public Teaching routes in `app/src/app/routes/public_content.py`, `app/src/app/routes/public.py`, and `app/src/app/__init__.py` to use the new hub/topic model, the Teaching-specific template, and route-aware locale switching.
- Added the Teaching templates and styling in `app/templates/pages/teaching_page.html`, `app/templates/partials/_teaching_blocks.html`, `app/templates/partials/_top_app_bar.html`, `app/static/css/20_layout.css`, and `app/static/css/30_components.css`.
- Added the new Teaching UI strings in `app/src/app/i18n.py`.
- Added initial public Teaching content and placeholder media/export files under `content/teaching/spanish/...` and `public/teaching/spanish/...`.
- Updated `app/tests/test_research_sessions.py` to assert the drawer-free Teaching shell, topic rendering, and edition fallback behavior.
- Hardened shared analytics in `app/src/app/analytics.py` with a retry around the daily aggregate write path after the live browser pass exposed a duplicate-key failure on repeated Teaching requests.
- Updated production wiring in `app/Dockerfile` and `app/infra/docker-compose.prod.yml` so repo-root Teaching content is copied into the image and addressed through `PROMAT_TEACHING_CONTENT_ROOT`.
- Updated `docs/spec/platform-data-files.md` to make the new Teaching route model and content-path rules active, and marked `docs/plans/teaching_section_raw.md` as superseded by the active spec and implementation.

## Decisions

- Teaching remains a fully public, file-based surface and does not reuse Research auth, Research player routes, or protected data paths.
- Teaching edition hubs and topic pages use the shared topbar but intentionally disable the permanent drawer/sidebar shell.
- The canonical Teaching content source is versioned repository content under `content/teaching/...`; public media stays under `public/teaching/...`.
- Locale switching on Teaching routes is route-aware: keep the current edition when possible, switch to an equivalent topic when available, otherwise fall back to the target edition hub.
- Production image wiring now treats Teaching content as an explicit runtime input via `PROMAT_TEACHING_CONTENT_ROOT` instead of relying on implicit relative paths.

## Deviations

- No admin authoring surface was added.
- The content seed is intentionally minimal and centered on Spanish plus one minimal English topic edition; other teaching languages remain structurally prepared but unfilled.

## Validation

- `get_errors` on the touched Python, Jinja, Docker, and YAML-adjacent integration files.
- `python -m pytest app/tests/test_research_sessions.py -q -k teaching`
- Live browser validation via headless Edge screenshots on:
  - `/de/teaching/spanish`
  - `/en/teaching/spanish/final-r`
  - regression check on `/de/project/about`

## Results

- The new public Teaching routes render as a dedicated card-based hub and block-based topic surface without the permanent left drawer.
- The global DE/EN switch keeps Teaching context instead of falling back to naive prefix swapping.
- The first live browser pass exposed an unrelated shared analytics duplicate-key defect that produced a 500 on repeated Teaching requests; the run fixed that defect and confirmed clean rendering afterward.
- Research remained protected and unchanged in the implementation slice touched here.

## Open Points

- Additional Teaching languages and richer public media assets still need editorial content work.
- The current visual treatment is intentionally rohbau-level and should receive a later design pass only after the content model settles.
- No production image build was executed in this run; the Docker and compose wiring was updated but not built end-to-end here.

## Next Steps

- Extend `content/teaching/...` with further editions and topic sets for the remaining teaching languages.
- Add focused coverage for the new analytics retry path if a stable integration seam is introduced for that shared write flow.
- When the Teaching IA stabilizes, do a dedicated visual polish pass for spacing, typography, and mobile density across the new Teaching components.
