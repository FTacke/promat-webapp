# 2026-05-25 Spanish Batch Full Test

## Scope

- Workspace: `C:\dev\promat`
- Batch: `scripts\research_data_intake\import\es_batch_20260525`
- Archive root: `C:\dev\promat_data_archive`
- No prod package was built.
- No PROMAT server/upload contact was performed. One failed MFA retry exposed an external GitHub model-download attempt before the cache guard was added; the final successful run used cached MFA models.
- `content/`, `content/teaching/`, and `public/teaching/` were not touched.
- No original research source data was patched.

## Commands

Dry-run:

```powershell
.venv\Scripts\python.exe scripts\research_data_intake\import_batch_to_production.py --batch es_batch_20260525 --target-language es --archive-root C:\dev\promat_data_archive --run-working --run-mfa --mfa-executable docker --sync-tasks --cleanup-working-on-success --dry-run
```

Write:

```powershell
.venv\Scripts\python.exe scripts\research_data_intake\import_batch_to_production.py --batch es_batch_20260525 --target-language es --archive-root C:\dev\promat_data_archive --run-working --run-mfa --mfa-executable docker --sync-tasks --cleanup-working-on-success
```

Auxiliary checks:

```powershell
.venv\Scripts\python.exe -m py_compile scripts\research_data_intake\alignment_export\run_text_mfa.py
.venv\Scripts\python.exe -m pytest app/tests/test_research_working_tree_intake.py app/tests/test_research_production_importer.py app/tests/test_research_intake_storage.py app/tests/test_research_raw_sync_importer.py
```

Detailed command logs are under `tmp/intake-runs/2026-05-25-spanish-batch-full-test/`.

## Pipeline Fixes During This ES Test

- `import_batch_to_production._run_text_pipeline` now skips missing working text inputs in write mode instead of trying MFA for workbook-only rows without batch files. This keeps ES-L-0010 through ES-L-0016 metadata-only instead of hard-failing on missing `working\...\text\source\text.wav`.
- `run_text_mfa.py` now emits combined stdout/stderr for MFA failures and, for Docker MFA, checks cached model files before running `mfa model download`. This avoided the GitHub API rate-limit failure once cached Spanish MFA models were present.
- Regression coverage was added for both behaviors.

## Dry-Run Result

Dry-run exit code: `0`.

Summary:

- `sessions=19`
- `create=8`
- `update=11`
- `skip=0`
- `conflict=0`
- `task_sync=0`

Dry-run working orchestration reported ES-L-0001 through ES-L-0009 and ES-N-0001 through ES-N-0003 as rebuildable, with native-speaker interviews marked `not_expected_for_native_speaker`. Because dry-run does not materialize the working tree for the later import-plan phase, task rows appeared as `skip/missing:working task directory missing` in the dry-run plan. No unresolved conflict was reported, so the write run was allowed.

Warnings:

- Openpyxl warning: conditional-formatting extension unsupported and removed in the in-memory workbook load.
- `.bak` files were ignored as unsupported intake files:
  - `es_l_0001_interview_processed.json.bak`
  - `es_l_0002_interview_processed.json.bak`
  - `es_l_0003_interview_processed.json.bak`
  - `es_l_0004_interview_processed.json.bak`
  - `es_l_0005_interview_processed.json.bak`
  - `es_l_0007_interview_processed.json.bak`
  - `es_l_0008_interview_processed.json.bak`
  - `es_l_0009_interview_processed.json.bak`
  - `promat_intake_spanish.xlsx.bak`

## Write Result

Write exit code: `0`.

Summary:

- `sessions=19`
- `create=8`
- `update=11`
- `skip=0`
- `conflict=0`
- `task_sync=33`

Session result:

- ES-L-0001 through ES-L-0009: `update`, tasks `wordlist=sync/ready`, `text=sync/ready`, `interview=sync/ready`, `archive_inputs=9`.
- ES-L-0010 through ES-L-0016: `create`, tasks skipped as missing because no working task inputs exist, `archive_inputs=0`.
- ES-N-0001 and ES-N-0002: `update`, tasks `wordlist=sync/ready`, `text=sync/ready`, `interview=skip/not_expected_for_native_speaker`, `archive_inputs=6`.
- ES-N-0003: `create`, tasks `wordlist=sync/ready`, `text=sync/ready`, `interview=skip/not_expected_for_native_speaker`, `archive_inputs=6`.

Speaker groups:

- Learners: ES-L-0001 through ES-L-0016.
- Native speakers: ES-N-0001, ES-N-0002, ES-N-0003.
- Native-speaker interview remained `not_expected`; no unexpected native-speaker interview task was imported.

## MFA Status

- Wordlist: no MFA, all successful task imports used TextGrid/runtime artifact generation.
- Text: MFA ran successfully for ES-L-0001 through ES-L-0009 and ES-N-0001 through ES-N-0003.
- Text for ES-L-0010 through ES-L-0016: skipped because no text working inputs exist in the batch.
- Interview: no MFA.

During the first write attempt, ES-L-0010 exposed the missing-working-input hard failure. During the second attempt, ES-L-0009 exposed an MFA model-download GitHub rate-limit failure. Both were fixed in the pipeline; a targeted ES-L-0009 MFA rerun then completed successfully before the final full write.

## ES Warnings

Source-data/runtime warnings retained in alignment payloads:

- 40 interview import warnings total.
- Zero-duration word clamps were recorded for ES-L-0001, ES-L-0002, ES-L-0003, ES-L-0004, ES-L-0006, ES-L-0007, ES-L-0008, and ES-L-0009.
- IPA/transcript bracket annotations in ES-L-0006 were kept as token text without `material_ref`, including examples such as `mucha[t͡ʃ]o`, `mucha[x]o`, `é[ks]ito`, `é[x]ito`, and `Mé[x]ico`.

No true ES source-data conflict remains from this run. The workbook-only learners ES-L-0010 through ES-L-0016 are imported as metadata-only sessions with skipped task artifacts.

## Runtime Validation

Runtime root: `data/sessions/spanish`.

- 19 Spanish session directories exist.
- Every `metadata.json` is parseable.
- Alignment JSON files are parseable for all successful tasks.
- `derived/*.mp3` exists for all successful tasks.
- `items/wordlist/*.mp3` and `items/text/*.mp3` exist for all successful wordlist/text tasks.
- No forbidden runtime files or folders were found: `*.wav`, `*.TextGrid`, `*.xlsx`, `secure/`, `raw/`, `source/`, `origin/`, `alignment_source/`, `working/`, `mfa_corpus/`, `mfa_output/`.

Runtime task coverage:

- ES-L-0001 through ES-L-0009: `wordlist`, `text`, `interview`.
- ES-L-0010 through ES-L-0016: metadata-only, no documented tasks.
- ES-N-0001 through ES-N-0003: `wordlist`, `text`.

## Archive Validation

Archive root: `C:\dev\promat_data_archive\sessions\es`.

- 19 Spanish archive session directories exist.
- `secure/secure_person_intake.json` exists and is parseable for every session.
- `raw/`, `source/`, `alignment_source/`, `runtime/`, `metadata/`, and `reports/` exist for every session.
- No `origin/` directory exists.
- Every `metadata/archive_manifest.json` is parseable.
- `task_audio_roles` are present for all successful task artifacts and use `processed` or `raw` source roles.
- `input_files` and `generated_runtime_files` include checksums and sizes.
- `skipped_or_missing_artifacts` correctly records:
  - 0 skipped artifacts for ES-L-0001 through ES-L-0009.
  - 3 skipped missing task artifacts for each ES-L-0010 through ES-L-0016.
  - 1 skipped native-speaker interview for each ES-N-0001 through ES-N-0003.

Batch archive reports were generated under `C:\dev\promat_data_archive\batches\es_batch_20260525`.

## DB Validation

Database: default dev PostgreSQL `postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:54321/promat_auth`.

- Spanish sessions: 19.
- Spanish people: 19.
- Learners: 16.
- Native speakers: 3.
- Exposure rows for Spanish sessions: 6.
- No native-speaker session has an unexpected `interview` documented task.

## Working Cleanup

`scripts\research_data_intake\import\es_batch_20260525\working` is absent after the successful write. Only cache/log artifacts remain outside the working tree.

## Webapp Check

The dev server was not available on `127.0.0.1:5000` or `127.0.0.1:8000`, so route checks for `/de/research/spanish/speakers` and player routes were not executed.

## Tests

Result:

```text
66 passed
```

Test command:

```powershell
.venv\Scripts\python.exe -m pytest app/tests/test_research_working_tree_intake.py app/tests/test_research_production_importer.py app/tests/test_research_intake_storage.py app/tests/test_research_raw_sync_importer.py
```

Covered ES-related regressions include workbook whole-column `sqref`, UTF-8 BOM JSON, IPA brackets, `[u]`, zero-duration word/segment clamp, missing text working inputs, and cached MFA model use.

## Git Status

`git status --short -- content content\teaching public\teaching` was clean.

The full worktree remains dirty from ongoing intake/platform work, including pipeline/test/doc changes and pre-existing unrelated tracked/untracked changes. Spanish runtime session directories are present locally under `data/sessions/spanish` and are ignored by Git; the tracked `.gitkeep` marker was restored after the import cleanup. No Teaching/content files were changed by this run.

## Open Points Before Full EN+ES Import Or Prod Package

- EN-L-0008 text remains a separate open source-data/corpus mismatch: 55 spoken TextGrid intervals versus 56 English text catalog items.
- ES-L-0010 through ES-L-0016 are metadata-only unless task source files are later provided.
- Dev web routes still need a browser/server pass once the dev server is running.
- Prod package build remains intentionally not performed in this run.
