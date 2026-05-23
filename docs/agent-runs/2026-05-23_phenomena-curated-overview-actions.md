# 2026-05-23 · Phenomena Curated Overview Actions

## Scope

- replaced the unclear curated overview action `Modifizieren` with explicit curated-original vs private-copy actions
- aligned the phenomena overview action matrix for normal users and admins
- kept private-set actions on the existing edit / rename / delete path
- added an explicit confirmation step before admins save global changes to curated originals in the editor

## Implementation

- updated `app/src/app/research_phenomena_views.py` so curated overview entries now carry:
  - `Ansehen` / `View`
  - admin-only `Kuratiertes Set bearbeiten` / `Edit curated set`
  - `Als eigenes Set bearbeiten` / `Edit as own set`
- added private-copy target resolution so `Als eigenes Set bearbeiten` opens an existing private copy when one already exists for the same curated source, otherwise it creates a new private draft from the curated set
- updated `app/templates/pages/research_phenomena_overview.html` to render the new curated action order with the existing navigation-pill and action-button families and without new page-local styles
- updated `app/static/js/pages/research-phenomena-overview.js` so curated private-copy actions now use the explicit `/api/research/sets/<set_id>/private-copy` flow instead of the old create-via-legacy-preset path
- updated `app/static/js/pages/research-phenomena-editor.js` so admin saves of curated originals require an explicit confirmation dialog before the global update request is sent
- added the new bilingual labels in `app/src/app/i18n.py`
- updated `app/tests/test_research_phenomena.py` to assert the exact visible action matrix for normal users and admins plus the private-copy/open-existing-copy behavior

## Validation

- `python -m pytest app/tests/test_research_phenomena.py -q`
- `python -m pytest app/tests/test_research_player_set_context.py app/tests/test_research_comparison.py app/tests/test_research_phenomena.py app/tests/test_research_sets.py -q`

## Notes

- no page-local CSS was introduced; the change stays on existing PM navigation-pill, button, overflow, and dialog families
- the visible curated-original action for admins is a direct editor link, while the private-copy action remains copy-on-write and never points at the curated original editor route
