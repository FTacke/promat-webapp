# 2026-05-25 Full EN/ES Batch Import Blocker Fixes

## Scope

- Target batches: `en_batch_20260525`, `es_batch_20260525`.
- No prod package was built.
- No server contact was made.
- `content/` and `public/teaching/` were not touched.

## Pipeline fixes implemented

- `intake_batch_common.read_json_file` now reads JSON with `utf-8-sig`, so a UTF-8 BOM in Amberscript JSON does not block intake.
- `intake_workbook_reader.py` now normalizes whole-column workbook data-validation `sqref` values such as `H:H` in a temporary XLSX copy for `openpyxl`; the source workbook is not overwritten and the normalization is reported as a warning.
- `import_interview_amberscript.py` now keeps non-material bracket annotations such as `[θ]`, `[x]`, and `[u]` as token text without creating `material_ref`.
- Material references remain limited to controlled PROMAT item IDs such as `wl_059`, `t_18`, `d_01`, `qy_01`, and `qw_01`; unknown material-ref-like prefixes still fail explicitly.
- Amberscript zero-duration words and segments are clamped to 1 ms with `_import_warnings`.
- Amberscript alternate speaker IDs are mapped only when `speakers[]` unambiguously maps the ID to `Speaker 1` or `Speaker 2`; otherwise the interview task reports a speaker-mapping error.
- Text MFA prep now clamps tiny TextGrid/WAV end-boundary rounding overruns to the source WAV duration with a manifest warning; larger timing mismatches remain hard errors.
- `--run-mfa --dry-run` no longer requires MFA outputs that a dry-run does not write.
- Docker/MFA subprocess output is decoded as UTF-8 with replacement to avoid Windows codepage reader-thread failures.

## Data patches

- No original research input file was patched by this run.
- EN-L-0004 was checked separately: the current JSON already contains `spk2`. The adjacent `.bak` shows UUID `d39f1341-f0dd-4917-8eba-831abe7577d3` as the second `speakers[]` entry (`Speaker 2`) and all corresponding participant segments. The implemented fix is a generic, documented speaker-alias rule rather than another source-data patch.

## Tests

- `python -m pytest app/tests/test_research_working_tree_intake.py app/tests/test_research_production_importer.py`: 52 passed.
- `python -m pytest app/tests/test_research_intake_storage.py app/tests/test_research_production_importer.py app/tests/test_research_working_tree_intake.py app/tests/test_research_raw_sync_importer.py`: 63 passed before the TextGrid/WAV rounding fix.
- After the TextGrid/WAV rounding regression was added: `python -m pytest app/tests/test_research_working_tree_intake.py app/tests/test_research_production_importer.py app/tests/test_research_intake_storage.py app/tests/test_research_raw_sync_importer.py`: 64 passed.
- `py_compile` passed for the touched intake modules.

## Dry-run plans

### English

Command used:

```text
.venv\Scripts\python.exe scripts\research_data_intake\import_batch_to_production.py --batch en_batch_20260525 --target-language en --archive-root C:\dev\promat_data_archive --run-working --run-mfa --mfa-executable docker --sync-tasks --cleanup-working-on-success --dry-run
```

- Working dry-run: EN-L-0001 through EN-L-0009 planned `rebuilt` for `wordlist`, `text`, and `interview`.
- Import plan summary: `sessions=9 create=7 update=2 skip=0 conflict=0 task_sync=0`.
- EN-L-0001 and EN-L-0002 showed `update` because existing runtime/DB sessions are present.
- `task_sync=0` in the import plan is expected for this dry-run because `--run-working --dry-run` validates but does not create `working/`.
- Warnings: unsupported `.bak` files for EN-L-0004 and EN-L-0008.

### Spanish

Command used:

```text
.venv\Scripts\python.exe scripts\research_data_intake\import_batch_to_production.py --batch es_batch_20260525 --target-language es --archive-root C:\dev\promat_data_archive --run-working --run-mfa --mfa-executable docker --sync-tasks --cleanup-working-on-success --dry-run
```

- Working dry-run: ES-L-0001 through ES-L-0009 planned `rebuilt` for `wordlist`, `text`, and `interview`.
- Native speakers ES-N-0001 through ES-N-0003 planned `rebuilt` for `wordlist` and `text`; `interview` was `not_expected_for_native_speaker`.
- Import plan summary: `sessions=19 create=8 update=11 skip=0 conflict=0 task_sync=0`.
- Warnings: unsupported `.bak` files, including Amberscript JSON backups and `promat_intake_spanish.xlsx.bak`.

## Write attempt and blocker

- English write was attempted after dry-runs showed no unresolved conflicts.
- First run stopped during text MFA prep on a tiny TextGrid/WAV end-boundary overrun; this is now handled by the rounding-clamp fix and covered by a regression test.
- Second run stopped before Runtime/DB/Archive import on EN-L-0008 `text`: canonical English text catalog has 56 items, while EN-L-0008 TextGrid has 55 spoken intervals.
- EN-L-0008 appears to start at catalog item `t_02`; the title item `t_01` (`The Boy who Cried Wolf`) is not present as a spoken TextGrid interval. This is a real data/catalog alignment conflict, not a safe pipeline normalization.
- No Spanish write was started after this unresolved English blocker remained.

## Task outcome

- Robust blockers solved: workbook `sqref H:H`, JSON BOM, IPA brackets, `[u]`, zero-duration Amberscript words/segments, and unambiguous UUID speaker aliasing.
- EN-L-0004 interview is no longer blocked by UUID speaker IDs when the `speakers[]` table proves the mapping.
- EN-L-0008 interview is no longer blocked by `[u]`.
- ES interview sources are no longer blocked by BOM, IPA bracket annotations, or zero-duration Amberscript segments.
- Open blocker: EN-L-0008 `text` cannot be imported until the catalog/TextGrid item-count mismatch is resolved explicitly.

## Runtime, archive, DB, working

- Runtime after the failed English write still contains only existing English sessions EN-L-0001 and EN-L-0002.
- Archive after the failed English write still contains only existing English archive sessions EN-L-0001 and EN-L-0002.
- No DB upsert result was produced for the full English/Spanish import because the write stopped before import-plan application.
- Generated English `working/` was cleaned down to the affected EN-L-0008 context plus `.intake_state.json`.
- No prod upload package was created.
- Root hygiene check found pre-existing `inspect_dw.py`, `inspect_styles.py`, and `start.txt`; they were not created or moved in this run.

## Open points before prod package build

- Resolve EN-L-0008 `text` explicitly: either provide/restore a TextGrid interval for `t_01`, adjust the source TextGrid with documented provenance, or mark EN-L-0008 `text` task as skipped with a clear `mapping_required`/count-mismatch report.
- Re-run full EN dry-run and write after EN-L-0008 is resolved.
- Run Spanish write only after the full-batch policy is satisfied again.
- Consider moving or deleting batch `.bak` files if they should not remain scan warnings.
