# Research Player Interview Re-Import Robustness Pass

## Summary

- hardened the shared interview runtime so material references still render in the order `token [reference].` when older runtime data still keeps trailing punctuation inside the anchor token text
- added focused regression coverage for the exact interview reference forms `Item Nummer 25 [oír].` and `Item Nummer 80 [Europa].`
- rebuilt the batch-local interview working JSON for `spanish_batch_20260421` and re-imported the batch into the productive runtime sessions

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/research-player.md`
- `docs/spec/intake-workbook.md`
- `scripts/research_data_intake/README.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `app/src/app/research_player_runtime.py`
- `app/tests/test_research_sessions.py`
- `app/tests/test_research_production_importer.py`
- `app/tests/test_research_working_tree_intake.py`
- `scripts/research_data_intake/import/organize_batch_working_tree.py`
- `scripts/research_data_intake/import_batch_to_production.py`
- `scripts/research_data_intake/import/spanish_batch_20260421/working/ES-L-0002/interview/alignment/interview.json`
- `scripts/research_data_intake/import/spanish_batch_20260421/working/ES-L-0009/interview/alignment/interview.json`

## Spec Updates

- no spec text changed in this run because the active interview reference rule in `docs/spec/research-player.md` already required `token core -> inline reference -> token-local suffix`

## Implementation Notes

### Runtime robustness

- updated `app/src/app/research_player_runtime.py` so anchored interview references detach trailing punctuation not only from explicit `segment.suffix`, but also from older token texts like `80.` when such data still appears in runtime alignment JSON
- the same normalization now updates the renderable token payload so the transcript token and the suffix-carrying reference stay internally consistent

### Regression coverage

- added a focused unit-style regression in `app/tests/test_research_sessions.py` that exercises both the current suffix model and the legacy punctuation-in-token fallback for the exact `oír` and `Europa` cases

### Batch rebuild and re-import

- reran `scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421 --force-task interview`, which rebuilt all learner interview working trees in the batch and kept the native-speaker interview tasks correctly marked as not expected
- reran the central production importer for `spanish_batch_20260421` with `--sync-tasks`
- because local port `54321` was blocked on this Windows machine, the development PostgreSQL container was started on fallback port `55433` and the importer was pointed to `postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:55433/promat_auth`

## Verification

- VS Code problems check for `app/src/app/research_player_runtime.py` and `app/tests/test_research_sessions.py` reported no errors
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_production_importer.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_working_tree_intake.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421 --force-task interview`
- `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --sync-tasks --auth-database-url postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:55433/promat_auth --dry-run`
- `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --sync-tasks --auth-database-url postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:55433/promat_auth`
- direct runtime validation against `data/sessions/spanish/ES-L-0002-2026-S01/alignment/interview.json` and `data/sessions/spanish/ES-L-0009-2026-S01/alignment/interview.json` confirmed:
  - `Item Nummer 25 [oír].`
  - `Item Nummer 80 [Europa].`

## Notes

- no browser screenshot pass was added in this run because the visible UI structure was unchanged; the correction was limited to runtime transcript assembly and productive data refresh