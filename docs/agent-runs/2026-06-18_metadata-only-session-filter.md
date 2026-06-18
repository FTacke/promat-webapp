# 2026-06-18 Metadata-Only-Session-Filter: Pipeline-Fix und French-Cleanup

## Ausgangsproblem

Alle im XLSX-Workbook vorhandenen Personen/Sessions wurden automatisch in Runtime, `db/import_payload.json` und Produktions-DB uebernommen, auch wenn fuer diese Personen keine Audio-/Task-Artefakte im Batch vorhanden waren. Die French-Batch-Ausgangslage nach dem vorherigen Run: 31 Sessions in DB und Runtime, davon 10 metadata-only (nur `metadata.json`, keine `alignment/*.json` oder `derived/*.mp3`).

## Loesung: Zentraler Publishability-Filter

Eine Session gilt als publizierbar, wenn mindestens ein Task (wordlist, text, interview) im Batch arbeitsbereit ist (`action in {"sync", "available"}`) oder im bestehenden Runtime-Dir bereits Artefakte vorhanden sind.

## Geaenderte Dateien

### `scripts/research_data_intake/import_batch_to_production.py`

- `SessionImportPlan` erhaelt neues Feld `has_delivered_task_data: bool`
- Neue Funktion `_session_has_delivered_task_data()`: prueft initial task_plans (vor Skip-Override) und bestehende Runtime-Artefakte
- `_build_import_plans()`: berechnet `has_delivered_task_data` vor dem Skip-Override
- `_print_plan()`: metadata-only create/update-Plans werden als `skip reason=no_delivered_task_data` angezeigt und gezaehlt
- `main()`: ueberspringt `_apply_plan` wenn `not plan.has_delivered_task_data`

### `scripts/research_data_intake/apply_prod_db_payload.py`

- `validate_payload_against_release()`: lehnt Sessions mit leeren `documented_tasks` ab
- Neue Funktion `_session_dir_has_task_artifacts()`: prueft alignment/derived auf Taskartefakte
- Neue Funktion `run_cleanup_metadata_only()`: findet und loescht optional metadata-only Sessions fuer eine bestimmte Sprache transaktional; Person-Zeilen nur wenn alle ihre Sessions metadata-only sind
- Neue CLI-Args: `--cleanup-metadata-only`, `--target-language`, `--apply-cleanup`
- Startup-Pfaderkennung robuster: `parents[2]` mit IndexError-Schutz, `PROMAT_APP_SRC`-Env-Override

### `scripts/research_data_intake/build_prod_upload_package.py`

- `_discover_all_runtime_sessions()`: filtert Sessions ohne Task-Artefakte (metadata-only) aus dem `--all-runtime-sessions`-Modus

### `app/tests/test_research_production_importer.py`

7 neue Tests:
- `test_import_plan_has_no_delivered_task_data_when_no_working_files`
- `test_import_plan_has_delivered_task_data_when_wordlist_ready`
- `test_import_plan_has_delivered_task_data_when_existing_runtime_artifacts`
- `test_import_plan_native_speaker_with_only_non_expected_interview_has_no_delivered_task_data`
- `test_main_skips_metadata_only_sessions_in_db_and_runtime`
- `test_import_db_payload_excludes_metadata_only_sessions`

### `app/tests/test_research_prod_db_payload.py`

6 neue Tests:
- `test_db_payload_with_empty_documented_tasks_fails_validation`
- `test_cleanup_metadata_only_dry_run_finds_sessions_without_task_artifacts`
- `test_cleanup_metadata_only_apply_removes_sessions_and_persons`
- `test_cleanup_metadata_only_does_not_touch_other_languages`
- `test_cleanup_metadata_only_person_with_publishable_session_not_deleted`
- `test_cleanup_metadata_only_is_idempotent`

### `docs/spec/platform-data-files.md`

Neue Regeln: Publishability-Bedingung (mindestens ein Task mit realen Artefakten), Ablehnung leerer `documented_tasks` in der Payload-Validierung, Cleanup-Verfahren fuer metadata-only Sessions.

### `docs/runbooks/research-prod-upload-and-publish.md`

Neuer Abschnitt "Cleanup: Metadata-only Sessions (DB + Runtime)" mit Schritt-fuer-Schritt-Anleitung, Regeln und Randbedingungen.

## Testergebnis

57 Tests, alle gruen. Ruff: keine Fehler.

## Produktions-Cleanup French (Einmaliger Fix)

### Script-Stand

Lokaler Working-Tree-Stand (vor Commit), auf Basis von `f03aff4` plus aktuelle Aenderungen. Script temporaer nach `/tmp` auf dem Server kopiert und per `docker cp` in den Container gebracht. Kein Deploy oder Commit-Artefakt – einmaliger Produktionsfix.

### Ausgangslage

31 French Sessions in Runtime und DB. Davon 10 metadata-only (keine Task-Artefakte):
`FR-L-0008`, `FR-L-0022`–`FR-L-0029`, `FR-N-0002` (jeweils `-2026-S01`).

### Ausgefuehrte Schritte

1. Script nach `/tmp` auf Server kopiert und per `docker cp` in Container gebracht.
2. **Dry-run**: `--cleanup-metadata-only --target-language fr --release-dir /app/data`
   - Ergebnis: 10 Sessions, 10 Persons, 6 Exposures, mode=dry_run – stimmt exakt mit der Erwartung ueberein.
3. **Apply** (nach expliziter Freigabe): gleicher Befehl mit `--apply-cleanup`
   - Ergebnis: `"applied": true`, 10 Sessions + 10 Persons + 6 Exposures transaktional geloescht.
4. **Runtime-Dirs**: genau die 10 Ordner unter `/srv/webapps_storage/promat/data/sessions/french/` geloescht.
5. **Container-Restart**: `docker restart promat-web-prod`, healthy nach 15 s.
6. **Verifikation**:
   - `/health` 200, `/ready` 200
   - DB: `fr: 21`, `en: 10`; FR-People: 21; FR-Sessions: 21; FR-Exposures: 8; EN/ES unveraendert
   - Runtime: 21 French-Session-Ordner (alle mit Task-Artefakten)
   - App-Loader: 21 FR Sessions
   - Anker vorhanden: `FR-L-0001-2026-S01`, `FR-L-0021-2026-S01`, `FR-N-0001-2026-S01`
   - Metadata-only entfernt: `FR-L-0008-2026-S01`, `FR-L-0022-2026-S01`, `FR-N-0002-2026-S01` (exemplarisch geprueft)

## Einhaltung der Bedingungen

- Kein Backup/Snapshot angelegt.
- Keine anderen Sprachen beruehrt (en, es unveraendert).
- Kein globaler Delete.
- Loeschung ausschliesslich unter `/srv/webapps_storage/promat/data/sessions/french/`.
- DB-Cleanup nur `--target-language fr`.
- Dry-run zuerst ausgefuehrt und bestaetigt.
- Apply nur nach expliziter Freigabe.
- Loeschung transaktional.
- Personen nur geloescht, wenn alle Sessions metadata-only waren.

## Offene Punkte

- Aenderungen noch nicht committed. Commit und regulaerer Deploy ausstehend, damit der neue Publishability-Filter und die Cleanup-Funktion dauerhaft im Image verankert sind.
- Der temporaere Script-Stand in `/tmp` auf dem Server und im Container kann nach dem naechsten regulaeren Deploy entfernt werden.
