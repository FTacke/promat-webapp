# prep_intake.md

# PROMAT Intake, Local Archive, and Server Runtime Publish — Target Plan

## Status

Planning document for the PROMAT repository.

This file defines the intended target model for future production intake, local processing, local archiving, and server publishing of PROMAT research data.

It is not yet a complete implementation runbook. It should guide the implementation of scripts, server preparation, and production procedures.

## Core decision

PROMAT separates three concerns strictly:

```text
Local workspace = intake, processing, validation, and release preparation
Local archive   = complete long-term research archive, including secure and raw/origin data
Prod server     = access-controlled webapp runtime data only
```

The production server must not become a storage place for raw WAVs, origin WAVs, processed WAV work files, MFA working directories, workbook drafts, or secure re-identification data.

The server receives only validated runtime deltas that the webapp needs.

## Naming decision

All new server-side and repo-facing names should use the short project name:

```text
promat
```

Do not introduce new server paths, containers, databases, networks, or service names with `pronunciation-matters`.

Historical preparation paths using `pronunciation-matters` may exist from the earlier storage preparation. They should be normalized to `promat` during the actual production setup.

## Runtime storage decision

PROMAT does not need a separate `media/` runtime tree.

All protected research runtime material belongs under `data/`.

This includes:

```text
metadata.json
alignment/*.json
derived/*.mp3
items/{task}/*.mp3
research-player config JSON
import payloads
manifests
reports
```

The reason is simple: all relevant research audio and alignment material is access-controlled and belongs to the protected research-data space. Public assets, if they ever exist, must be exported explicitly to a separate public path by a separate publication step.

Target server runtime root:

```text
/srv/webapps_storage/promat/data
```

Target app-local host path:

```text
/srv/webapps/promat/data
```

Target container path:

```text
/app/data
```

## Current prepared server state to normalize

The server currently has prepared storage under the earlier long name:

```text
/srv/webapps_storage/pronunciation-matters/data
/srv/webapps_storage/pronunciation-matters/media
```

For production setup, normalize this to:

```text
/srv/webapps_storage/promat/data
```

Do not keep a parallel PROMAT `media` runtime directory unless a later public-media requirement explicitly justifies it.

## Local intake source

The project workbook remains the local intake master.

It may contain all project data across people, sessions, corpora, and future batches. A batch run extracts only the rows relevant for the files and sessions present in that batch.

The workbook is not the runtime data source. It is an intake contract and steering source for producing clean runtime metadata and database import payloads.

Relevant workbook information is split into two groups:

```text
secure / identifying:
  stays local only

runtime-safe research metadata:
  may be exported into cleaned metadata.json and DB import payloads
```

Secure or identifying material must not be uploaded to the production server.

## Local batch workspace

A local batch is a temporary processing workspace.

Recommended local structure:

```text
<local_work_root>/intake_batches/
  es_batch_20260601_pilot01/
    raw/
    origin/
    processed/
    intake_data/
      project_intake.xlsx
      optional_batch_extract.xlsx
    working/
    reports/
```

Rules:

- The batch name should contain `batch`.
- `processed/` is required for a processable batch.
- `raw/` and `origin/` are optional local archive inputs.
- `intake_data/` contains the workbook or batch extract.
- `working/` is temporary and may be regenerated.
- Nothing under this local batch workspace is uploaded wholesale to the server.

## Local processing pipeline

The local pipeline should do the heavy work before anything is uploaded.

Typical sequence:

```text
1. Collect raw/origin WAVs and workbook information locally.
2. Create or verify processed WAVs, TextGrids, and Amberscript JSON.
3. Validate filenames and derive person/task assignments explicitly.
4. Extract only workbook rows relevant to the batch.
5. Separate secure fields from runtime-safe metadata.
6. Organize batch-local working tree.
7. Run alignment/MFA/interview transformation as needed.
8. Generate runtime metadata, alignment JSON, derived MP3, and split MP3.
9. Validate output.
10. Build a small server upload package.
11. Move complete local materials into the long-term local archive.
```

The production server should not run MFA or accumulate working directories.

## Local long-term archive

After a successful local processing run, the local archive becomes the complete research archive.

Recommended archive structure:

```text
<local_archive_root>/promat/
  es/
    20260601_pilot01/
      secure/
        secure_person_intake_export.json
        consent_refs/
        questionnaire_refs/

      raw/
        original_wavs/

      origin/
        origin_wavs/

      processed/
        processed_wavs/
        textgrids/
        amberscript_json/

      derived/
        sessions/
        mp3/
        alignment_json/

      metadata/
        batch_metadata_clean.json
        workbook_extract_clean.json
        manifest.json
        checksums.sha256

      reports/
        intake_report.md
        validation_report.md
        server_upload_report.md
```

The workbook has served its intake purpose at this point. The long-term archive keeps a structured, auditable state independent of ad hoc workbook history.

## What must not go to the production server

Do not upload:

```text
raw/
origin/
processed/
working/
mfa_corpus/
mfa_output/
secure/
*.xlsx
*.wav
consent files
questionnaire files
full workbook drafts
temporary split or trial outputs
```

Especially:

- no raw WAVs
- no origin WAVs
- no processed WAVs unless a later runtime requirement explicitly changes this
- no secure workbook sheet content
- no clear-text names or e-mail addresses
- no MFA intermediate directories
- no local working tree

## Server upload package

A server upload package is a runtime delta.

It may contain new sessions, corrected session files, corrected metadata, corrected alignment JSON, regenerated MP3 files, or updated research-player config.

Recommended structure:

```text
promat_upload_20260610_fix01/
  sessions/
    es/
      ES-L-0001-2026-S01/
        metadata.json
        alignment/
          text.json
        derived/
          text.mp3
        items/
          text/
            d_01.mp3
            d_02.mp3

  config/
    research_player/
      spanish/
        player_config.json
        phenomena_presets.json
        task_catalogs/
          wordlist.json
          text.json

  db/
    import_payload.json

  manifest.json
  checksums.sha256

  reports/
    upload_report.md
```

A package may be small. It does not need to contain a full corpus or a full batch if only one session or one task changed.

## Upload to server

Upload packages go to `incoming/`.

Example target:

```text
/srv/webapps_storage/promat/data/incoming/<upload_id>/
```

Recommended transfer mechanism:

```bash
rsync -avh --progress <local_upload_package>/ user@vhrz2184:/srv/webapps_storage/promat/data/incoming/<upload_id>/
```

Normal uploads must not use `rsync --delete`.

## Server production tree

The server keeps one active production tree.

Recommended target:

```text
/srv/webapps_storage/promat/data/
  incoming/
  production/
    sessions/
      es/
      fr/
      en/
      de/
    config/
      research_player/
    manifests/
    reports/
  quarantine/
  publish_logs/
```

The webapp reads from:

```text
/srv/webapps/promat/data
```

which should expose the production tree to the container as:

```text
/app/data
```

## Server publish model

Publishing is a controlled merge into the production tree.

It is not a full `current` symlink switch and not a batch registry model.

Rules:

```text
incoming/<upload_id>
  -> validate manifest and checksums
  -> reject forbidden paths and file types
  -> preview overwrite list
  -> merge allowed files into production/
  -> overwrite existing files with the same relative path
  -> keep files that are not present in the upload
  -> run DB upsert if import payload exists
  -> run health/readiness checks
  -> delete incoming/<upload_id> after success
```

This means:

- new batches add new session files
- correction uploads overwrite existing session files
- omitted files are left untouched
- no file is deleted by omission
- the server stores only active runtime data

## Incoming cleanup rule

After a successful publish, delete:

```text
/srv/webapps_storage/promat/data/incoming/<upload_id>
```

The upload already exists locally and in the local archive. Keeping incoming copies on the server would create an online data graveyard.

On failure, move the upload to:

```text
/srv/webapps_storage/promat/data/quarantine/<upload_id>
```

or leave it in `incoming/` only long enough for diagnosis. Quarantine needs a retention rule and should not grow without review.

## Correction model

Corrections are local-first.

Never edit production server runtime files manually.

### Metadata correction

```text
1. Correct workbook or local structured metadata source.
2. Rebuild cleaned metadata and db/import_payload.json locally.
3. Build a small upload package containing only changed metadata files and DB payload.
4. Upload to incoming/.
5. Publish merge overwrites affected metadata.json and upserts DB rows.
6. Delete incoming/ after success.
```

### Alignment correction

```text
1. Correct local annotation/alignment source.
2. Regenerate affected alignment JSON.
3. If needed, regenerate affected MP3 splits.
4. Build a small upload package for the affected session/task.
5. Publish merge overwrites the affected files.
```

### Audio correction

```text
1. Correct local source/processing state.
2. Regenerate derived MP3 and split MP3 locally.
3. Upload only runtime MP3 and related metadata/alignment updates.
4. Publish merge overwrites same relative paths.
```

### Session addition

```text
1. Process new batch locally.
2. Build upload package with new sessions and metadata DB payload.
3. Publish merge adds new files.
4. Existing sessions remain untouched.
```

## Deletion model

Deletion is not part of normal upload or correction.

Uploads must never delete existing production files by omission.

If deletion becomes necessary, use a separate explicit mechanism:

```text
delete_manifest.json
```

Rules for future delete support:

- separate command
- explicit approval
- dry-run first
- exact paths listed
- no globbing
- no recursive delete without hard-coded safeguards
- report and backup or quarantine before removal

Until such a mechanism exists, deletes should be handled manually only with explicit approval and full report.

## Allowed server upload paths

A server publish script should accept only these top-level paths:

```text
sessions/
config/research_player/
db/import_payload.json
manifest.json
checksums.sha256
reports/
```

It should reject:

```text
raw/
origin/
processed/
working/
secure/
mfa_corpus/
mfa_output/
*.xlsx
*.wav
```

Allowed runtime file types should be narrow:

```text
.json
.mp3
.md
.txt
.sha256
```

## Database handling

The database import payload should contain only runtime-safe research metadata.

Prod database writes should be explicit and reportable:

```text
1. validate import_payload.json
2. dry-run DB upsert
3. execute DB upsert only after validation
4. write import report
```

PROMAT should use its own production PostgreSQL container/database, not CO.RA.PAN, Games, HedgeDoc, or host PostgreSQL unless a future approved architecture says otherwise.

## Curated sets are not an intake concern

Curated sets should not be managed through JSON upload packages in the standard intake pipeline.

The reason: users can already create sets through the app UI, and the same authoring surface is more maintainable than hand-written or generated JSON intake.

Target model:

```text
Normal user:
  open curated set
  modify it
  -> app creates a private user-owned copy

Admin:
  open curated set
  modify it
  -> app offers explicit admin-only action to update the curated original
```

Implementation target:

- curated sets live in the application set model/database
- normal users cannot mutate curated originals
- normal user edits remain copy-on-write
- admins can update a curated original only through an explicit admin-only action
- admin updates require confirmation because they affect all users
- curated set changes should record `updated_by`, `updated_at`, and ideally a simple `version`
- JSON/CLI import for curated sets may exist later only as an exceptional migration/admin fallback, not as the standard workflow

The intake pipeline remains responsible for:

```text
sessions
audio runtime artifacts
alignment JSON
metadata.json
research-player config
database import payloads for people/sessions/exposures
```

It is not responsible for ordinary curated-set authoring.

## Health and verification after publish

After every server publish:

```text
1. verify files and checksums
2. run DB import verification if applicable
3. run app /health
4. run app /ready
5. run relevant protected route smoke tests if possible
6. run server-wide monitoring check when configured
7. write publish report
8. delete incoming/<upload_id> after success
```

The server-wide monitoring command should use check mode only:

```bash
/srv/server_monitoring/webapp_healthcheck.sh check
```

No alert or monthly mode should be triggered by a normal publish.

## Implementation tasks still needed

### Local tooling

- batch validator
- secure/runtime metadata splitter
- local archive writer
- upload package builder
- manifest and checksum writer
- forbidden-path scanner

### Server tooling

- incoming validator
- publish merge script
- overwrite preview
- DB dry-run and upsert integration
- forbidden-path and file-type rejection
- incoming cleanup
- quarantine handling
- publish report writer
- healthcheck integration

### App / database

- production DB model and migrations for PROMAT research metadata
- stable `/health` and `/ready`
- runtime data root configuration via `PROMAT_RUNTIME_ROOT`
- admin-only curated-set update action
- copy-on-write behavior for non-admin curated-set edits
- curated-set audit fields such as `updated_by`, `updated_at`, `version`

## Non-goals

- no server-side raw WAV archive
- no server-side origin WAV archive
- no server-side intake workbook archive
- no server-side MFA workbench
- no server-side manual editing of production runtime files
- no curated-set JSON intake as standard workflow
- no automatic deletion of production files by omission
- no reuse of CO.RA.PAN/Games/HedgeDoc databases
