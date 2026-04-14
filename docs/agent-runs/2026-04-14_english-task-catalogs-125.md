# 2026-04-14 English task catalogs 125

## Summary

- Added canonical English research-player catalogs under `data/config/research_player/english/task_catalogs/` for `wordlist` and `text`.
- Modeled the English `text` catalog as connected text under the unchanged technical task key `text`, with visible numbering `T1...` and stable item IDs `t_01...`.
- After the first real pipeline run, updated the English `text` catalog so `The Boy who Cried Wolf` is included as spoken item `T1`, because the actual `text.TextGrid` and recorded material contain it as a spoken segment.
- Added minimal English corpus config files so loaders and placeholder corpus surfaces can resolve the same config family as Spanish.
- Removed the remaining Spanish-only catalog assumptions from the reusable wordlist/text production entry points that the central importer delegates to.

## Validation

- JSON for the new English catalog and config files loads through `app.research_presets.load_task_catalog`, `load_player_config`, and `load_phenomena_presets`.
- The repo test suite now asserts that the English `text` catalog resolves as connected text with 56 items and that the English `wordlist` catalog exposes 95 canonical items.
- The reusable wordlist loader now validates sequential `wl_###` catalogs generically instead of hard-requiring the previous Spanish-only item count.

## Validation Results

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_presets.py -q` passed with 13 tests.
- Direct loader smoke test returned `tasks=['text', 'wordlist']`, `text_items=55`, `wordlist_items=95`, `default_render_mode='running_text'`, `preset_count=1`.
- `organize_batch_working_tree.py --batch-dir english_batch --dry-run` completed cleanly and planned `wordlist` plus `text` inputs for `EN-L-0001` without warnings.
- `import_batch_to_production.py --batch-dir english_batch --target-language en --dry-run` completed cleanly and planned one English session create with `raw_sync=2`, `raw_missing=1`, and no conflicts, while correctly reporting missing task-sync inputs before a written working-tree run.