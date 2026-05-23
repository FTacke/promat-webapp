# 2026-05-23 · DB-Curated Research Sets

## Scope

- replaced productive file-backed curated research-set usage with the unified PostgreSQL-backed `research_sets` model
- migrated focused backend and UI test fixtures from `starter_preset` to DB-seeded curated sets
- added admin-side curated update or archive or reactivate controls to the phenomena editor
- aligned local bootstrap so initial admin setup also ensures exactly one canonical curated DB test set
- updated active research-player spec to describe DB-curated sets and legacy `preset_id` compatibility

## Implementation

- kept task catalogs file-backed under `data/config/research_player/{language}/task_catalogs/*`, but removed productive dependence on `phenomena_presets.json` for comparison, player, and phenomena set resolution
- updated `app/tests/test_research_comparison.py`, `app/tests/test_research_sets.py`, and `app/tests/test_research_phenomena.py` to seed one DB-curated set per fixture and to route old `preset_id` expectations through the seeded curated row
- fixed `POST /api/research/sets` so an invalid legacy `preset_id` alias returns a controlled client error instead of leaking an uncaught not-found exception
- extended `app/src/app/research_phenomena_views.py`, `app/templates/pages/research_phenomena_editor.html`, `app/static/js/pages/research-phenomena-editor.js`, and `app/src/app/i18n.py` so admins can update curated originals in place and archive or reactivate them, while non-admin curated edits still copy on write into a private set
- updated `app/scripts/create_initial_admin.py` so local admin bootstrap also calls `ensure_curated_test_set(...)`
- updated `docs/spec/research-player.md` so active rules describe the unified DB-backed curated/private set model and the legacy `preset_id` carrier correctly

## Validation

- `python -m pytest app/tests/test_research_player_set_context.py app/tests/test_research_comparison.py app/tests/test_research_phenomena.py app/tests/test_research_sets.py -q`
- `python -m pytest app/tests/test_research_phenomena.py -q`
- `python -m pytest app/tests/test_research_sets.py -q`
- `python -m py_compile app/scripts/create_initial_admin.py app/src/app/routes/research_api.py app/src/app/research_phenomena_views.py app/src/app/i18n.py app/tests/test_research_sets.py app/tests/test_research_phenomena.py app/tests/test_research_comparison.py app/tests/test_research_player_set_context.py`

## Notes

- the workspace task `Run research sessions tests` still reports 6 unrelated failures in teaching, sample, team, and player back-link assertions; none of those failures touch the DB-curated research-set migration slice
