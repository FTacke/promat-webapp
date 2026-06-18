# English Batch Intake

Datum: 2026-06-18

## Ziel

Vollstaendiger lokaler Intake von `scripts/research_data_intake/import/english_batch_20260618`, inklusive Ueberschreiben der bereits integrierten englischen Runtime- und Archivdaten.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `scripts/research_data_intake/README.md`

## Geaenderte Bereiche

- `scripts/research_data_intake/alignment_export/import_interview_amberscript.py`
- `scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py`
- `scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py`
- `scripts/research_data_intake/alignment_export/run_text_mfa.py`
- `app/tests/test_research_working_tree_intake.py`
- lokale Runtime unter `data/sessions/english/`
- lokales Archiv unter `C:/dev/promat_data_archive/sessions/en/`
- Dev-PostgreSQL Research-Metadaten

## Wichtige Entscheidungen

- Keine neue Intake-Regel eingefuehrt; die bestehenden Spezifikationsfaelle wurden umgesetzt: eindeutige Amberscript-Speaker-Zuordnung aus `speakers[]`, nicht-materiale Interview-Klammerliterale wie `[u].`, kleine TextGrid/WAV-Endgrenzen-Clamps, und dokumentiertes Auslassen eines ungesprochenen Titel-Items.
- Docker-MFA nutzt vorhandene lokale Modell-Dateien, wenn sie im Cache liegen, damit ein GitHub-API-Rate-Limit den Lauf nicht blockiert.

## Abweichungen

- Keine Abweichung von Runtime-/Archivgrenzen. Runtime enthaelt nur `metadata.json`, Alignment-JSON, Derived-MP3 und Item-MP3.
- Workbook-Warnung zu einem OpenPyXL-kompatibel normalisierten Data-Validation-Range wurde gemeldet; die originale Workbook-Datei wurde nicht geaendert.

## Verifikation

- `scan_import_batch.py --batch-dir english_batch_20260618`
- `organize_batch_working_tree.py --batch-dir english_batch_20260618 --replace-existing`
- `import_batch_to_production.py --batch-dir english_batch_20260618 --target-language en --run-working --run-mfa --sync-tasks --archive-root C:/dev/promat_data_archive`
- `pytest app/tests/test_research_working_tree_intake.py`
- Runtime-Validator fuer alle 10 englischen Sessions
- Archiv-Validator fuer alle 10 englischen Sessions
- Stichprobe: EN-L-0008 `alignment/text.json` enthaelt 55 Items plus `omitted_items[]` fuer `t_01`.

## Offene Punkte

- EN-L-0010 wurde aus dem Workbook als Metadaten-Session ohne Batch-Medien angelegt.
- Kein Prod-Upload-Paket wurde in diesem Run gebaut.

## Naechste sinnvolle Schritte

- Bei Bedarf ein explizites Prod-Upload-Paket aus den validierten englischen Runtime-Artefakten bauen und validieren.
