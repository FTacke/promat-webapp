# 2026-04-27 · Interaction-System Phase 1 Refinement · Run 143

## Scope

- Reworked the preview-only phase-1 sample surface from a generic button family into a broader interaction-system preview.
- Kept productive pages and existing shared families untouched; no global migration was performed.
- Split the preview semantics into action buttons, navigation pills, CTA links, and existing chips/tabs.
- Added mock cards and context rows on `/{ui_lang}/sample` to show where each interaction type belongs.

## Implementation

- Updated the active platform spec note so the preview-only migration target is now the interaction family split on `sample`.
- Added DE/EN translation keys for the new interaction preview copy in `app/src/app/i18n.py`.
- Added quieter interaction tokens plus new action-button, nav-pill, and CTA-link component styles in `app/static/css/00_tokens.css` and `app/static/css/30_components.css`.
- Updated preview typography and layout helpers in `app/static/css/10_typography.css` and `app/static/css/20_layout.css`.
- Added `app/templates/partials/_pm_interactions.html` with separate render macros for action buttons, navigation pills, CTA links, and chip previews.
- Replaced the old sample preview payload with semantic interaction preview data in `app/src/app/routes/public.py`.
- Rebuilt the top sample preview section in `app/templates/pages/sample_page.html`.
- Updated focused preview regressions in `app/tests/test_research_sessions.py`.

## Validation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "interaction_preview or sample_page_exposes_semantic_interaction_preview_without_global_migration or sample_page_localizes_interaction_preview_in_english or login_page_does_not_render_sample_interaction_preview_components"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "sample_page or login_page_does_not_render_sample_interaction_preview_components"`
- Fetched `http://127.0.0.1:8000/de/sample` and `http://127.0.0.1:8000/en/sample`; that listener still served the stale pre-refinement preview.
- Started a fresh local listener on `http://127.0.0.1:8010` with `AUTH_DATABASE_URL=postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:55432/promat_auth` and validated the current DE/EN sample HTML there.
- Opened `http://127.0.0.1:8010/de/sample` and `http://127.0.0.1:8010/en/sample` in the integrated browser.

## Notes

- `tmp/run_app_8010.py` still defaults to PostgreSQL port `54321`; on this host the active dev database was reachable on `55432`, so the validation run overrode `AUTH_DATABASE_URL` explicitly.
- The old listener on port `8000` was stale during this run and should not be treated as evidence about the current implementation state.
- No automated screenshot capture was available in this environment.