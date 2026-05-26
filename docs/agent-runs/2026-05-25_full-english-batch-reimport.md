# 2026-05-25 Full English Batch Reimport

## Scope

- Workspace: `C:\dev\promat`
- Batch: `scripts\research_data_intake\import\en_batch_20260525`
- Archive root: `C:\dev\promat_data_archive`
- No prod package was built.
- No PROMAT server/upload contact was performed. Docker MFA used the batch-local cached English MFA models.
- `content/`, `content/teaching/`, and `public/teaching/` were not touched.
- No original research source data was patched.

## Implemented EN-L-0008 Rule

The EN-L-0008 text conflict was resolved in the pipeline, not by editing the TextGrid or catalog.

The new rule applies only when:

- the first catalog item is `t_01` and has `spoken_title_item: true`;
- the catalog has exactly one more item than the spoken TextGrid intervals;
- the first spoken interval matches `t_02`;
- every later spoken interval matches `t_03` through `t_56` in order;
- no later mismatch exists.

When those checks pass, the MFA manifest maps the 55 spoken intervals to `t_02` through `t_56` and records:

```json
{
  "item_id": "t_01",
  "item_number": "T1",
  "text": "The Boy who Cried Wolf",
  "omitted": true,
  "omit_reason": "unspoken_title"
}
```

The omitted item has no `start_ms`, no `end_ms`, and no `split_mp3`. Runtime `alignment/text.json`, archive runtime copy, archive manifest warnings, and import report warnings document `EN-L-0008 text: omitted t_01 because the spoken title was not recorded`.

## Other Pipeline Fixes In This Run

- Batch working state JSON is now read with `utf-8-sig`, because the EN dry-run exposed a direct `.intake_state.json` BOM path outside the central JSON reader.
- `--run-mfa --dry-run` no longer requires a written per-person MFA manifest. It now prepares/validates the plan and prints run notes without expecting dry-run files to exist.
- Runtime text export removes the working-only warning `session_id remains unresolved...` after the production session ID has been resolved.
- Dry-run output now prints `[run-notes]`, making MFA prep warnings such as the EN-L-0008 title omission visible in the regular command output.
- The active spec was updated in `docs/spec/platform-data-files.md` for the constrained `spoken_title_item` omission contract.

## Tests

Final relevant Intake test command:

```powershell
.venv\Scripts\python.exe -m pytest app/tests/test_research_working_tree_intake.py app/tests/test_research_production_importer.py app/tests/test_research_intake_storage.py app/tests/test_research_raw_sync_importer.py
```

Result:

```text
72 passed
```

New coverage includes:

- positive EN title omission: 56 catalog items, 55 intervals, `t_01` omitted, intervals mapped to `t_02` through `t_56`;
- negative no title marker;
- negative wrong interval count;
- negative later mismatch;
- no split/audio expectation for omitted `t_01`;
- BOM-tolerant working state load;
- dry-run text MFA planning without requiring a written manifest.

## Dry-Run Summary

Command log: `tmp/intake-runs/2026-05-25-full-english-batch-reimport/dry-run.txt`

Summary:

- `sessions=9`
- `create=7`
- `update=2`
- `skip=0`
- `conflict=0`
- `task_sync=2`

The dry-run did not write the full working tree, so most task rows appeared as missing in the import-plan phase. The run notes documented that a write run with `--run-working` would create those working inputs. EN-L-0008 was explicitly validated in dry-run notes:

- `Prepared text MFA corpus for EN-L-0008: segments=55`
- `EN-L-0008 text: omitted t_01 because the spoken title was not recorded`

Warnings:

- `.bak` files ignored: `en_l_0004_interview_processed.json.bak`, `en_l_0008_interview_processed.json.bak`.

## Write Result

Final write log: `tmp/intake-runs/2026-05-25-full-english-batch-reimport/write-final.txt`

Summary:

- `sessions=9`
- `create=0`
- `update=9`
- `skip=0`
- `conflict=0`
- `task_sync=27`

Task result per session:

- EN-L-0001 through EN-L-0009: `wordlist=sync/ready`, `text=sync/ready`, `interview=sync/ready`.
- EN-L-0001 and EN-L-0002 remained single existing DB/runtime sessions and were updated, not duplicated.

MFA status:

- wordlist: no MFA.
- text: MFA ran for all EN text tasks.
- interview: no MFA.

## Interview Status

All nine corrected EN interview JSONs were rebuilt and imported through the regular working pipeline. The remaining warnings are controlled transcript/timing warnings, not blockers:

- EN-L-0004 UUID speaker id was mapped to `spk2` from an unambiguous `speakers[]` entry.
- IPA/transcript bracket annotations remain token text without `material_ref`.
- Zero-duration words were clamped to 1 ms with warnings where present.

## EN-L-0008 Runtime Mapping

Runtime `data/sessions/english/EN-L-0008-2026-S01/alignment/text.json`:

- `items`: 55 entries.
- first item: `t_02`.
- last item: `t_56`.
- `omitted_items[0]`: `t_01`, `omit_reason="unspoken_title"`.
- no `start_ms`, `end_ms`, or `split_mp3` on omitted `t_01`.
- no `items/text/t_01.mp3`.
- `items/text/t_02.mp3` through `items/text/t_56.mp3` exist.

## Runtime Validation

Runtime root: `data/sessions/english`.

- 9 English session directories exist.
- Every `metadata.json` is parseable.
- `alignment/wordlist.json`, `alignment/text.json`, and `alignment/interview.json` are parseable for every EN session.
- `derived/*.mp3` exists for every successful task.
- `items/wordlist/*.mp3` and `items/text/*.mp3` exist for every EN session.
- No forbidden runtime files or folders were found: `*.wav`, `*.TextGrid`, `*.xlsx`, `secure/`, `raw/`, `source/`, `origin/`, `alignment_source/`, `working/`, `mfa_corpus/`, `mfa_output/`.

## Archive Validation

Archive root: `C:\dev\promat_data_archive\sessions\en`.

- 9 English archive session directories exist.
- `secure/secure_person_intake.json` exists and is parseable for every session.
- `raw/`, `source/`, `alignment_source/`, `runtime/`, `metadata/`, and `reports/` exist for every session.
- No `origin/` directory exists.
- Every `metadata/archive_manifest.json` is parseable.
- `task_audio_roles` are present for `wordlist`, `text`, and `interview`.
- `input_files` and `generated_runtime_files` include checksums and sizes.
- `skipped_or_missing_artifacts` is empty for all EN sessions.
- EN-L-0008 manifest/report warnings document the omitted title item.

Batch archive reports were generated under `C:\dev\promat_data_archive\batches\en_batch_20260525`.

## DB Validation

Database: default dev PostgreSQL `postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:54321/promat_auth`.

- English sessions: 9.
- English people: 9.
- Exposure rows for English sessions: 1.
- Duplicate `(person_id, session_ref)` slots: none.
- Every EN session has documented tasks `wordlist; text; interview`.

## Working Cleanup

`scripts\research_data_intake\import\en_batch_20260525\working` is absent after the successful write.

## Git Status

`git status --short -- content content\teaching public\teaching data\sessions\english` was clean. English runtime session directories are present locally under ignored runtime paths.

The full worktree remains dirty from ongoing intake/platform work and pre-existing unrelated changes. In-scope changed files for this run include:

- `scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py`
- `scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py`
- `scripts/research_data_intake/produce_text_artifacts.py`
- `scripts/research_data_intake/import_batch_to_production.py`
- `scripts/research_data_intake/import/organize_batch_working_tree.py`
- `app/tests/test_research_working_tree_intake.py`
- `app/tests/test_research_production_importer.py`
- `docs/spec/platform-data-files.md`
- this report

## Open Points Before Prod Package

- Prod package build remains intentionally not performed.
- No EN source-data blockers remain from this run.
- Full EN+ES package validation can proceed in a separate explicit prod-package step when requested.
