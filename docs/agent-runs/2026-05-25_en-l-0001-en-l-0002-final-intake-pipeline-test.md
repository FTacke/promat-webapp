# Agent Run: EN-L-0001 + EN-L-0002 Final Intake Pipeline Test

**Date:** 2026-05-25  
**Scope:** EN-L-0001 und EN-L-0002 aus `en_batch_20260525` — vollständiger End-to-End-Test mit überarbeiteter Archiv-/WAV-Rollenlogik

---

## Umgesetzte Änderungen

### A. `origin/` aus Archivstruktur entfernt

- `ARCHIVE_SESSION_SUBDIRS` in `intake_storage.py`: `"origin"` entfernt
- `FORBIDDEN_RUNTIME_PARTS`: `"origin"` bleibt (Runtime-Schutz unverändert)
- `validate_archive_tree`: prüft weiterhin gegen `ARCHIVE_SESSION_SUBDIRS` ohne `origin/`
- Alle referenzierenden Dateien aktualisiert: `AGENTS.md`, `scripts/AGENTS.md`, `scripts/research_data_intake/README.md`, `.github/copilot-instructions.md`, `.github/instructions/repo.instructions.md`, `docs/spec/platform-data-files.md`, `docs/runbooks/research-intake-working-pipeline.md`

### B. WAV-Rollenlogik verfeinert

**Archiv:**
- `source/` enthält immer die operative Ableitungs-WAV (processed bevorzugt, raw als Fallback)
- Wenn raw WAV als Fallback genutzt wird: Datei wird ZUSÄTZLICH nach `source/{task}.wav` kopiert (bleibt auch unter `raw/`)
- `archive_manifest.json` enthält jetzt `task_audio_roles`: pro Task `raw_available`, `processed_available`, `source_audio_role` (`raw`|`processed`), `source_file_path`
- Einzel-Datei-Manifest-Einträge für raw-WAVs-als-Quelle: `source_file_role: "raw"`, `source_file_used_for_derivation: true`

**Organizer:**
- `raw_wav_used_as_source: bool` in `TaskSelection` und `TaskReport` (aus vorheriger Session)
- Kein `origin`-Fallback mehr; Konflikt bei mehreren Raw-WAVs ohne processed WAV

### C. Secure Export implementiert

- `write_secure_person_export()` in `intake_storage.py` schreibt `secure/secure_person_intake.json` per Session
- Alle 16 Felder aus `Secure_Person_Intake`-Sheet werden exportiert
- `SecurePersonIntakeRow` in `intake_workbook_reader.py` um 9 fehlende Felder erweitert: `last_name`, `first_name`, `email`, `paper_original_location`, `intake_date`, `intake_by`, `needs_review`, `verified_by`, `verified_date`
- `_normalize_secure_person_row` liest alle Felder
- `IntakeWorkbookData` enthält jetzt `secure_persons: dict[str, SecurePersonIntakeRow]`
- `SessionImportPlan` enthält `secure_person: SecurePersonIntakeRow | None`
- `_apply_plan` ruft `write_secure_person_export` nach `write_session_archive`
- **Nie in data/sessions, nie in Prod-Paketen, nie in Git**

### D. Multi `--person-id` CLI-Support

- `--person-id` in `parse_args` jetzt `action="append"` mit `dest="person_ids"`
- `load_intake_workbook` akzeptiert `person_id_filter: str | set[str] | None`
- `_run_working_pipeline` akzeptiert `person_ids: set[str] | None`
- Aufruf aus `main()` konvertiert `args.person_ids` (Liste) in Set

### E. Bugfixes am Interview-Amberscript-Parser

**Fix 1 – Dash als Suffix nach Materialreferenz:**  
`[t_30]-` und `[wl_093]-` wurden bisher als ungültige Marker abgelehnt. Suffix-Pattern erweitert auf `[.,!?;:\-]+`.

**Fix 2 – Zero-Duration-Words:**  
`//ich//` (overlapping speech) und `((lacht))` (paralinguistic) hatten `start == end`. Der Parser bricht nicht mehr ab, sondern klemmt `end_ms` auf `start_ms + 1` und schreibt eine Warning in `_import_warnings` des Payloads.

---

## Pipeline-Command

```
.venv\Scripts\python.exe scripts\research_data_intake\import_batch_to_production.py ^
  --batch en_batch_20260525 ^
  --person-id EN-L-0001 ^
  --person-id EN-L-0002 ^
  --target-language en ^
  --archive-root C:\dev\promat_data_archive ^
  --run-working ^
  --run-mfa ^
  --mfa-executable docker ^
  --sync-tasks ^
  --cleanup-working-on-success
```

---

## Ergebnisse

### Import-Plan (vor Ausführung)

```
update   EN-L-0001-2026-S01 (EN-L-0001/S01) tasks[wordlist=sync/ready, text=sync/ready, interview=sync/ready] archive_inputs=9
create   EN-L-0002-2026-S01 (EN-L-0002/S01) tasks[wordlist=sync/ready, text=sync/ready, interview=sync/ready] archive_inputs=9
sessions=2 create=1 update=1 skip=0 conflict=0 task_sync=6
```

### Working Tree

- EN-L-0001: `wordlist=unchanged`, `text=unchanged`, `interview=rebuilt` (Amberscript-JSON existierte)
- EN-L-0002: `wordlist=unchanged`, `text=unchanged`, `interview=rebuilt` (nach Parser-Fixes)
- Nach Erfolg gelöscht via `--cleanup-working-on-success` ✓

### Runtime `data/sessions/english/`

| Session | Status |
|---|---|
| `EN-L-0001-2026-S01/metadata.json` | ✓ |
| `EN-L-0001-2026-S01/alignment/*.json` | ✓ wordlist, text, interview |
| `EN-L-0001-2026-S01/derived/*.mp3` | ✓ wordlist, text, interview |
| `EN-L-0001-2026-S01/items/wordlist/*.mp3` | ✓ 95 Items |
| `EN-L-0001-2026-S01/items/text/*.mp3` | ✓ |
| `EN-L-0001-2026-S01/items/interview/` | n/a (interview = full MP3 only) |
| `EN-L-0002-2026-S01` | ✓ identische Struktur |
| Runtime-Validierung | **OK** (beide Sessions) |
| Verbotene Dateien | keine |

Dateianzahl: 158 pro Session.

### Archive `C:\dev\promat_data_archive\sessions\en\`

| Subdir | EN-L-0001 | EN-L-0002 |
|---|---|---|
| `secure/secure_person_intake.json` | ✓ | ✓ |
| `raw/` (wordlist, text, interview) | ✓ | ✓ |
| `source/` (wordlist, text, interview) | ✓ | ✓ |
| `alignment_source/` | ✓ | ✓ |
| `runtime/` | ✓ | ✓ |
| `metadata/archive_manifest.json` | ✓ | ✓ |
| `reports/import_report.json` | ✓ | ✓ |
| `origin/` | **nicht vorhanden** ✓ | **nicht vorhanden** ✓ |

**`task_audio_roles` in `archive_manifest.json`:**  
Alle Tasks: `source_audio_role=processed`, `raw_available=True`, `processed_available=True` (beide Personen haben vollständige processed+raw WAVs).

**Archiv-Validierung:** OK (beide Sessions)

**Secure Export:**
- EN-L-0001: `person_id=EN-L-0001`, `last_name=Bender`, consent=yes
- EN-L-0002: `person_id=EN-L-0002`, `last_name=Hansen`, consent=yes

### DB (PostgreSQL)

| Person | Session | documented_tasks | speaker_type | l1 | consent |
|---|---|---|---|---|---|
| EN-L-0001 | EN-L-0001-2026-S01 | wordlist; text; interview | learner | DE | yes |
| EN-L-0002 | EN-L-0002-2026-S01 | wordlist; text; interview | learner | DE | yes |

---

## Test-Status

57 Intake-Tests grün nach allen Änderungen:

- `test_research_intake_storage.py` (8) — inkl. 3 neue Tests (no-origin, source-copy-for-raw-fallback, secure-export)
- `test_research_production_importer.py` (21) — inkl. 2 neue Tests (secure_persons, set-filter)
- `test_research_working_tree_intake.py` (25) — inkl. 2 neue Tests (dash-suffix, zero-duration clamp)
- `test_research_raw_sync_importer.py` (3)

---

## Geänderte Dateien

| Datei | Änderungstyp |
|---|---|
| `scripts/research_data_intake/intake_storage.py` | Feature: kein origin/, source/-Copy für raw-Fallback, task_audio_roles in Manifest, write_secure_person_export |
| `scripts/research_data_intake/intake_workbook_reader.py` | Feature: SecurePersonIntakeRow +9 Felder, secure_persons in IntakeWorkbookData, set-basierter person_id_filter |
| `scripts/research_data_intake/import_batch_to_production.py` | Feature: --person-id multi-value, secure_person in SessionImportPlan, secure export in _apply_plan, _run_working_pipeline multi-IDs |
| `scripts/research_data_intake/alignment_export/import_interview_amberscript.py` | Fix: Dash-Suffix erlaubt, Zero-Duration clamp mit Warning |
| `app/tests/test_research_intake_storage.py` | Neue Tests |
| `app/tests/test_research_production_importer.py` | Neue Tests |
| `app/tests/test_research_working_tree_intake.py` | Neue Tests |
| `AGENTS.md` | origin/ entfernt |
| `scripts/AGENTS.md` | origin/ entfernt |
| `scripts/research_data_intake/README.md` | origin/ entfernt, raw-Fallback-Semantik |
| `.github/copilot-instructions.md` | origin/ entfernt |
| `.github/instructions/repo.instructions.md` | origin/ entfernt |
| `docs/spec/platform-data-files.md` | origin/ entfernt, source/-Semantik, secure/-Semantik |
| `docs/runbooks/research-intake-working-pipeline.md` | origin/ entfernt |

---

## Offene Punkte

1. **EN-L-0003 bis EN-L-0009** – ausstehend bis Quelldaten geprüft und Amberscript-JSONs bereit
2. **Prod-Paket** – noch nicht gebaut; kein Server-Kontakt in diesem Run
3. **Webapp-URLs** – nicht getestet in diesem Run (kein laufender Dev-Server)
