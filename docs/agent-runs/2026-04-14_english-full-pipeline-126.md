# English Full Pipeline 126

## Summary

Ran the full generic `english_batch` intake pipeline through working-tree organization, English text MFA preparation, real English MFA alignment, MFA import back into `working/`, and the real central production import for `target_language = en`.

## Scope

- `scripts/research_data_intake/textgrid_support.py`
- `data/config/research_player/english/task_catalogs/text.json`
- `app/tests/test_research_presets.py`
- `data/config/research_player/README.md`
- `docs/spec/platform-data-files.md`
- `docs/agent-runs/2026-04-14_english-task-catalogs-125.md`

## What changed

- Fixed the shared TextGrid interval parser so Praat-style doubled quotes inside interval text are parsed correctly instead of truncating spoken segments.
- Updated the English connected-text catalog so `The Boy who Cried Wolf` is included as spoken item `T1` because the real working `text.TextGrid` and recorded material contain it as an actual spoken segment.
- Updated the focused English catalog test to expect 56 text items.
- Updated active documentation and the earlier English-catalog run log to reflect the corrected title treatment.

## Pipeline execution

1. Revalidated the focused English loader/config tests:
   - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_presets.py -q`
   - Result: `13 passed`
2. Rechecked the working English `text.TextGrid` with the fixed parser:
   - Result: `spoken_count = 56`, first item `The Boy who Cried Wolf`, last item `And so the wolf had a feast.`
3. Re-ran generic English text MFA preparation:
   - Dry run succeeded with `planned_segments=56`
   - Write run succeeded with `written_segments=56`
4. Checked MFA model availability in the established `promat-mfa` conda environment:
   - `mfa 3.3.9`
   - English acoustic and dictionary models configured as `english_mfa`
5. Downloaded the missing English MFA models via the existing preload CLI.
6. Ran isolated English MFA validation:
   - Validation reached successful corpus loading and first-pass alignment for all 56 utterances
   - MFA still ended the validate command with a Windows-side cleanup/rename error (`WinError 1314`) in the temporary alignment area after `Aligned 56, errors on 0`
   - This did not indicate a corpus-content failure
7. Ran the real English MFA alignment with isolated `-t` and `-p` paths:
   - Result: success
   - Exported per-item TextGrids into `working/EN-L-0001/text/mfa_output/`
8. Ran generic MFA import back into the working tree:
   - Dry run and write run both succeeded
   - `working/EN-L-0001/text/alignment/text.json` written with `56` items and `364` tokens
9. Ran the central production importer:
   - Dry run succeeded
   - Real run succeeded
   - Planned and created `EN-L-0001-2026-S01`
   - Synced `wordlist` and `text`
   - Archived raw masters for `wordlist` and `text`
   - Left `interview` absent as expected because no working inputs exist for that task

## Verification

Runtime tree verification for `data/sessions/english/EN-L-0001-2026-S01`:

- Session directory exists with `alignment/`, `derived/`, `items/`, `metadata.json`, `raw/`, and `source/`
- `metadata.json` lists both `wordlist` and `text` tasks
- `raw/` contains `wordlist.wav` and `text.wav`
- `source/` contains `wordlist.wav` and `text.wav`
- `alignment/text.json` contains `56` items and `364` tokens
- `alignment/wordlist.json` contains `95` items

PostgreSQL verification against the local development database:

- `research_people` contains `EN-L-0001` with learner metadata
- `research_sessions` contains `EN-L-0001-2026-S01`
- Stored session values include `corpus_language = english`, `target_language = en`, `session_ref = S01`, `recording_year = 2026`, `context = baseline`, `documented_tasks = wordlist; text`
- `research_session_exposures` currently has `0` rows for this session

## Notes

- The MFA validate command on Windows required the correct CLI form (`--acoustic_model_path english_mfa`) and isolated `-t`/`-p` paths to get past global-state issues.
- Even with isolated paths, MFA validate still hit a Windows rename/privilege cleanup issue after successfully aligning all utterances. The real `mfa align` run was not affected and produced the required per-item outputs.
