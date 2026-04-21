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
- Für `en` sind die kanonischen Katalogquellen `data/config/research_player/english/task_catalogs/wordlist.json` und `data/config/research_player/english/task_catalogs/text.json`; der englische `text`-Katalog bleibt unter dem Task-Key `text`, ist aber als connected text modelliert.

## Schritt 1: Working-Tree organisieren

- Dry run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421 --dry-run`
- Schreiben:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421`
- Optional kann `--move` oder `--symlink` statt `--copy` gewählt werden.

Regeln:

- Dieser Schritt arbeitet inkrementell pro `person_id` und Task, führt den batch-lokalen Zustand in `working/.intake_state.json` und ersetzt nur Task-Unterbäume mit geänderten oder neu vollständigen Inputs.
- Für `wordlist` und `text` zählen nur die relevanten `processed/`-WAVs und `processed/`-TextGrids als Trigger für einen Rebuild des jeweiligen Task-Unterbaums.
- Für `interview` bevorzugt derselbe Schritt `*_interview_processed.wav` plus `*_interview_processed.json` und fällt getrennt auf `*_interview_raw.wav` beziehungsweise `*_interview_raw.json` zurück.
- Wenn bei Interview mehrere gleichrangige WAV- oder JSON-Kandidaten existieren, meldet der Organizer einen harten Konflikt statt zu raten.
- Wenn ein Interview-Input fehlt, bleiben andere Tasks derselben Person unangetastet und der Report nennt den taskweisen Status wie `missing_json` oder `missing_wav`.
- Interview-Referenzen werden in der Amberscript-Quelle als kompakte Marker am referenzierenden Token gepflegt, zum Beispiel `89[wl_089].`, `D5[d_05]` oder `Nummero [wl_087]`.
- Beim Transformieren verschwinden diese Rohmarker aus `segment.text` und `tokens[].text`; stattdessen schreibt das Working-JSON strukturierte `annotations[]` mit Katalogdaten aus `wordlist.json` oder `text.json`.
- Ungültige Markerformen oder unbekannte `item_id`-Werte werden nicht stillschweigend übernommen, sondern als taskweiser Fehler wie `error_invalid_material_ref_marker` oder `error_unknown_material_ref_item_id` gemeldet.

## Schritt 2: Text-MFA-Zwischenkorpus vorbereiten

- Dry run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py --batch-dir spanish_batch_20260421 --language es --text-source-json data/config/research_player/spanish/task_catalogs/text.json --dry-run`
- Schreiben:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py --batch-dir spanish_batch_20260421 --language es --text-source-json data/config/research_player/spanish/task_catalogs/text.json`
- Für einen späteren englischen Working-Lauf wird derselbe Schritt generisch mit `--language en --text-source-json data/config/research_player/english/task_catalogs/text.json` ausgeführt.
- Unveränderte `text`-Tasks müssen nach dem inkrementellen Organizer nicht erneut vorbereitet werden; nur geänderte `text`-Unterbäume sind für den MFA-Zwischenschritt erneut relevant.

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
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py --batch-dir spanish_batch_20260421 --language es --dry-run`
- Schreiben:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py --batch-dir spanish_batch_20260421 --language es`

## Schritt 5a: Interview-Amberscript-JSON in Working-JSON transformieren

- Der Organizer erledigt diesen Schritt im Normalfall bereits taskweise zusammen mit Schritt 1.
- Für einen isolierten Einzelfall kann derselbe Transformationsschritt explizit ausgeführt werden:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/import_interview_amberscript.py --batch-dir spanish_batch_20260421 --person-id ES-L-0001 --source-json scripts/research_data_intake/import/spanish_batch_20260421/processed/es_l_0001_interview_raw.json --replace-existing`
- Das Ziel bleibt dabei immer der batch-lokale Working-Pfad `working/{person_id}/interview/alignment/interview.json`; es wird noch nichts nach `data/sessions/` geschrieben.
- Wenn nur die Interview-Transformation nach einer Marker- oder Katalogkorrektur erneut laufen soll, ist der sichere Batch-Weg:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421 --force-task interview`
- Das resultierende Working-JSON hält sichtbare Referenztexte nicht als freie Editorannotation, sondern als strukturierte `material_ref`-Annotation mit `label`, `item_number`, `canonical_text` und `insert_after_token_id`; nachgestellte Markerinterpunktion bleibt stattdessen tokennah in `tokens[].suffix`.

## Schritt 6: Produktionsimport planen oder ausführen

- Voller Dry-Run für einen Batch mit Metadaten-, Raw- und Task-Sync-Plan:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --sync-tasks --dry-run`
- Kontrollierter Ein-Personen-Run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --person-id ES-L-0001 --sync-tasks`
- Reiner Metadata-Reimport gegen bestehende Sessions ohne erneute Task-Produktion:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --update-metadata`
- Reiner Raw-Backfill gegen bereits importierte Sessions:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --sync-raw-only --dry-run`
- Nur fehlende Sessions anlegen, bestehende aber exakt überspringen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --create-missing-only --dry-run`

Regeln:

- Der Import liest Workbook-Steuerdaten aus `intake_data/*.xlsx` und technische Inputs aus `working/{person_id}/{task}/`.
- Er schreibt person-, session- und exposure-bezogene Metadaten nach PostgreSQL und projiziert die Laufzeitstruktur nach `data/sessions/{language}/{session_id}/`.
- Wenn der Batch für eine Person und einen Task einen echten unveränderten Raw-Master unter `raw/` enthält, archiviert derselbe Import ihn zusätzlich unter `data/sessions/{language}/{session_id}/raw/{task}.wav`.
- Fehlt ein echter Raw-Master, bleibt das transparent; der Import darf `source/`-Dateien niemals als Ersatz nach `raw/` kopieren.
- `--sync-tasks` delegiert produktive Artefakt-Erzeugung an die wiederverwendbaren `wordlist`- und `text`-Prozessoren und übernimmt `interview` aus dem Working-Tree in den Runtime-Baum.
- `--sync-raw-only` ist der Nachholmodus für bereits importierte Sessions und ergänzt nur die Archivschicht `raw/` plus die zugehörigen `metadata.json`-Dateieinträge.
- Sessions ohne vollständige Task-Verfügbarkeit bleiben importierbar; nur die tatsächlich vorbereiteten Tasks werden synchronisiert.
- Ein abgeleiteter `session_id`-Wechsel für ein bestehendes `(person_id, session_ref)`-Slot ist ohne explizites `--allow-session-id-change` ein harter Konflikt.
- Für `interview` schreibt derselbe Produktionsimport `source/interview.wav`, `alignment/interview.json` und `derived/interview.mp3` nach `data/sessions/{language}/{session_id}/`, setzt dort die finale `session_id` im Alignment-JSON und ergänzt die Runtime-Metadaten nur um tatsächlich vorhandene Interview-Artefakte.

## Ergebnis dieses Runbooks

- Ziel ist ein batch-lokaler `working/`-Baum pro `person_id` und `task` plus ein kontrollierter Produktionsimport nach `data/sessions/` und PostgreSQL.
- Für `text` bleibt `working/{person_id}/text/alignment/text.json` das Zwischenartefakt vor dem Produktionsimport.
- Für `interview` ist `working/{person_id}/interview/alignment/interview.json` jetzt das batch-lokale Zielartefakt aus Amberscript-JSON.
- Der finale Produktionsimport kann daraus `raw/{task}.wav`, `source/interview.wav`, `alignment/interview.json`, `derived/interview.mp3`, `derived/text.mp3`, `items/text/{item_id}.mp3`, `alignment/text.json` und `metadata.json` im Laufzeitbaum erzeugen.

## Bewusst nicht Teil dieses Runbooks

- produktive Interview-Renderer oder Player-Artefaktableitung