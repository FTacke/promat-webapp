# Runbook: Research Intake Working Pipeline

## Zweck

Wiederholbarer Ablauf für den generischen Batch-zu-Working-Pfad unter `scripts/research_data_intake/` plus den anschließenden zentralen Produktionsimport nach `data/sessions/` und PostgreSQL.

## Batch-Definition

- Der Batch liegt unter `scripts/research_data_intake/import/`.
- Der Batch-Ordnername enthält `batch`.
- Verarbeitbar ist ein Batch nur mit mindestens vorhandenem `processed/`.
- `raw/` und `intake_data/` sind optional.

## Unterstützte Sprachkonfiguration

- Zentrale Konfiguration: `scripts/research_data_intake/language_config.py`
- Aktuell vorbereitete Codes: `es`, `de`, `fr`, `en`
- Die Sprachkonfiguration hält die geplanten MFA-Akustik- und Dictionary-Modelle pro Sprache zusammen.

## Schritt 1: Working-Tree organisieren

- Dry run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanisch_batch --dry-run`
- Schreiben:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanisch_batch`
- Optional kann `--move` oder `--symlink` statt `--copy` gewählt werden.

## Schritt 2: Text-MFA-Zwischenkorpus vorbereiten

- Dry run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py --batch-dir spanisch_batch --language es --text-source-json data/config/research_player/spanish/task_catalogs/text.json --dry-run`
- Schreiben:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py --batch-dir spanisch_batch --language es --text-source-json data/config/research_player/spanish/task_catalogs/text.json`

## Schritt 3: Optionale MFA-Modellprüfung oder Downloads

- Nur prüfen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/preload_mfa_models.py --language es`
- Explizit herunterladen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/preload_mfa_models.py --language es --download-models`
- Dieses CLI lädt nie stillschweigend Modelle; ohne `--download-models` bleibt es im Check-Modus.

## Schritt 4: Externer MFA-Lauf

- Die eigentliche MFA-Ausführung bleibt außerhalb dieses Repo-Skripts und schreibt in `working/{person_id}/text/mfa_output/`.
- OOVs, Dysfluencies und Selbstreparaturen sind Warnsignale für die Qualität, aber im aktuellen Working-Pfad nicht automatisch Abbruchgründe.

## Schritt 5: MFA in Working-JSON zurückimportieren

- Dry run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py --batch-dir spanisch_batch --language es --dry-run`
- Schreiben:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py --batch-dir spanisch_batch --language es`

## Schritt 6: Produktionsimport planen oder ausführen

- Voller Dry-Run für einen Batch mit Metadaten-Update und Task-Sync-Plan:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanisch_batch --target-language es --sync-tasks --dry-run`
- Kontrollierter Ein-Personen-Run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanisch_batch --target-language es --person-id ES-L-0001 --sync-tasks`
- Reiner Metadata-Reimport gegen bestehende Sessions ohne erneute Task-Produktion:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanisch_batch --target-language es --update-metadata`
- Nur fehlende Sessions anlegen, bestehende aber exakt überspringen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanisch_batch --target-language es --create-missing-only --dry-run`

Regeln:

- Der Import liest Workbook-Steuerdaten aus `intake_data/*.xlsx` und technische Inputs aus `working/{person_id}/{task}/`.
- Er schreibt person-, session- und exposure-bezogene Metadaten nach PostgreSQL und projiziert die Laufzeitstruktur nach `data/sessions/{language}/{session_id}/`.
- `--sync-tasks` delegiert produktive Artefakt-Erzeugung an die wiederverwendbaren `wordlist`- und `text`-Prozessoren.
- Sessions ohne vollständige Task-Verfügbarkeit bleiben importierbar; nur die tatsächlich vorbereiteten Tasks werden synchronisiert.
- Ein abgeleiteter `session_id`-Wechsel für ein bestehendes `(person_id, session_ref)`-Slot ist ohne explizites `--allow-session-id-change` ein harter Konflikt.
- Interview bleibt aktuell nur als Strukturslot ohne produktiven Artefakt-Import.

## Ergebnis dieses Runbooks

- Ziel ist ein batch-lokaler `working/`-Baum pro `person_id` und `task` plus ein kontrollierter Produktionsimport nach `data/sessions/` und PostgreSQL.
- Für `text` bleibt `working/{person_id}/text/alignment/text.json` das Zwischenartefakt vor dem Produktionsimport.
- Der finale Produktionsimport kann daraus `derived/text.mp3`, `items/text/{item_id}.mp3`, `alignment/text.json` und `metadata.json` im Laufzeitbaum erzeugen.

## Bewusst nicht Teil dieses Runbooks

- endgültige Interview-Integration
- produktive Interview-Artefaktableitung