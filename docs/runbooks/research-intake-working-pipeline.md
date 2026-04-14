# Runbook: Research Intake Working Pipeline

## Zweck

Wiederholbarer Ablauf für den generischen Batch-zu-Working-Pfad unter `scripts/research_data_intake/`, einschließlich des aktuellen `text`-MFA-Zwischenwegs bis `working/{person_id}/text/alignment/text.json`.

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

## Ergebnis dieses Runbooks

- Ziel ist ein batch-lokaler `working/`-Baum pro `person_id` und `task`.
- Für `text` endet der aktuelle Pfad bei `working/{person_id}/text/alignment/text.json`.
- Dieses JSON ist ein Zwischenartefakt im Working-Tree, nicht der finale Produktionsimport.

## Bewusst nicht Teil dieses Runbooks

- finaler Transfer nach `data/`
- finale `session_id`-Setzung
- vollständige Session-/Metadata-/XLSX-Integration
- Produktions-`derived/text.mp3`
- endgültige Interview-Integration