# 2026-05-24 Teaching Import Staging Workflow

## Scope

Added a repository-local staging workflow for future Teaching topic imports without changing productive app logic.

## Changes

- added `content/teaching_import/README.md` as the binding instruction set for future agent-driven local Teaching imports
- added `content/teaching_import/.gitkeep` so the staging directory remains present in the repository
- updated `docs/spec/platform-data-files.md` with a short active rule for the local Teaching import workflow

## README rules captured

- import packages live under `content/teaching_import/{import-topic-folder}/`
- target routing still writes only into the existing Teaching model under `content/teaching/{teaching_language}/{topic_slug}/`
- import YAMLs require `teaching_lang`, `topic_slug`, `ui_lang`, `title`, `description`, and `status`
- hub files only control grouping, order, visibility, and status; card copy must remain topic-driven
- topic-local media is normalized into `media/audio`, `media/images`, `media/video`, and `media/downloads`
- agents may perform only light technical corrections and must stop on missing core metadata, ambiguous hub assignment, unsupported `ui_lang`, existing target collisions, or missing media
- no DB, admin UI, research integration, public legacy structure, fallback logic, or repo backups are allowed

## Validation

- `python scripts/validate_teaching_content.py`
- `python -m pytest app/tests/test_teaching_content.py -q`

## Open points

- no import automation was added in this run by design; future work may add at most a small dry-run checker if needed