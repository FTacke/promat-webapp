# Runbook: Research Intake Working Pipeline

## Zweck

Wiederholbarer Ablauf für den Drop-in-Batch-Pfad unter `scripts/research_data_intake/` bis zum kontrollierten lokalen Import nach Runtime, Dev-DB und externem Archiv sowie zum separaten Prod-Upload-Paket.

Teaching ist nicht Teil dieses Runbooks. `content/`, `public/teaching/` und Teaching-Media bleiben unangetastet.

## Batch-Definition

- Der Batch liegt unter `scripts/research_data_intake/import/`.
- Der Batch-Ordnername enthält `batch`.
- Der Batch ist ein Drop-in-Verzeichnis ohne Pflicht für `processed/`, `raw/`, `source/` oder `intake_data/`.
- Workbook, WAV, TextGrid und JSON dürfen direkt im Batch oder in optionalen Hilfsunterordnern liegen.
- Klassifikation erfolgt strikt über Dateinamen und bekannte Rollen, nicht über freie Workbook-Prosa oder heuristische Pfadannahmen.

## Unterstützte Sprachkonfiguration

- Zentrale Konfiguration: `scripts/research_data_intake/language_config.py`
- Aktuell vorbereitete Codes: `es`, `de`, `fr`, `en`
- Die Sprachkonfiguration hält die geplanten MFA-Akustik- und Dictionary-Modelle pro Sprache zusammen.
- Für `en` bleiben die kanonischen Katalogquellen `data/config/research_player/english/task_catalogs/wordlist.json` und `data/config/research_player/english/task_catalogs/text.json`.

## Schritt 1: Drop-in-Batch scannen

- Menschlich lesbarer Report:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/scan_import_batch.py --batch-dir spanish_batch_20260421`
- JSON-Report:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/scan_import_batch.py --batch-dir spanish_batch_20260421 --json`

Regeln:

- Der Scanner klassifiziert Dateien nach `person_id`, Task, Rolle und Dateityp.
- Mehrdeutige oder konkurrierende Kandidaten bleiben sichtbar im Report und werden nicht automatisch aufgelöst.
- Das Workbook wird aus dem Batch rekursiv gefunden; es ist nicht mehr an `intake_data/*.xlsx` gebunden.

## Schritt 2: Working-Tree organisieren

- Dry run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421 --dry-run`
- Schreiben:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421`

Regeln:

- Dieser Schritt arbeitet inkrementell pro `person_id` und Task, führt den batch-lokalen Zustand in `working/.intake_state.json` und ersetzt nur Task-Unterbäume mit geänderten oder neu vollständigen Inputs.
- Für `wordlist` und `text` zählen nur klassifizierte `source`-WAVs und alignment-source TextGrids als operative Working-Eingänge.
- Für `interview` sind nur klassifizierte `source`-WAV plus klassifizierte alignment-source JSON-Datei operative Eingänge.
- `raw` allein ist kein zulässiger Fallback für die operative Interview-Ableitung.
- Wenn bei Interview mehrere gleichrangige WAV- oder JSON-Kandidaten existieren, meldet der Organizer einen harten Konflikt statt zu raten.
- Wenn ein Interview-Input fehlt, bleiben andere Tasks derselben Person unangetastet und der Report nennt den taskweisen Status.
- Native Speaker mit `speaker_type = native_speaker` oder `-N-` bleiben für `interview` neutral `not_expected_for_native_speaker`.

## Schritt 3: Text-MFA-Zwischenkorpus vorbereiten

- Dry run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py --batch-dir spanish_batch_20260421 --language es --text-source-json data/config/research_player/spanish/task_catalogs/text.json --dry-run`
- Schreiben:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py --batch-dir spanish_batch_20260421 --language es --text-source-json data/config/research_player/spanish/task_catalogs/text.json`

Regeln:

- Nur geänderte `text`-Tasks müssen nach einem inkrementellen Organizer-Lauf erneut vorbereitet werden.
- Der MFA-Zwischenschritt bleibt batch-lokal und schreibt nicht nach `data/sessions/`.
- Kleinste TextGrid-Grenzüberschreitungen gegenüber der WAV-Dauer durch Rundung werden auf die WAV-Dauer geklemmt und im Manifest reportet; echte Zähl- oder Timingkonflikte bleiben Blocker.

## Schritt 4: Optionale MFA-Modellprüfung oder Downloads

- Nur prüfen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/preload_mfa_models.py --language es`
- Explizit herunterladen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/preload_mfa_models.py --language es --download-models`

## Schritt 5: Externer MFA-Lauf

- Die eigentliche MFA-Ausführung bleibt außerhalb dieses Repo-Skripts und schreibt in `working/{person_id}/text/mfa_output/`.
- OOVs, Dysfluencies und Selbstreparaturen sind Qualitätswarnungen, aber im Working-Pfad nicht automatisch Abbruchgründe.

## Schritt 6: MFA in Working-JSON zurückimportieren

- Dry run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py --batch-dir spanish_batch_20260421 --language es --dry-run`
- Schreiben:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py --batch-dir spanish_batch_20260421 --language es`

## Schritt 7: Batch nach Runtime, Dev-DB und Archiv importieren

- Voller Dry-Run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --sync-tasks --dry-run`
- Kontrollierter Ein-Personen-Run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --person-id ES-L-0001 --sync-tasks`
- Reiner Metadata-Reimport gegen bestehende Sessions ohne erneute Task-Produktion:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --update-metadata`

Regeln:

- Der Import liest Workbook-Steuerdaten aus dem rekursiv gefundenen Batch-Workbook und technische Inputs aus `working/{person_id}/{task}/`.
- `--run-mfa --dry-run` plant die MFA-Schritte ohne MFA-Outputs zu verlangen, weil ein Dry-run keine batch-lokalen MFA-Dateien schreibt.
- Er schreibt person-, session- und exposure-bezogene Metadaten nach PostgreSQL und projiziert den Runtime-Baum nach `data/sessions/{language}/{session_id}/`.
- Runtime bleibt strikt JSON/MP3-only: kein `raw/`, kein `source/`, keine TextGrids, keine XLSX.
- Der Import schreibt die Langzeitablage separat unter `PROMAT_LOCAL_ARCHIVE_ROOT/sessions/{language_code}/{session_id}/`.
- Archiveingänge und Runtime-Ziele werden validiert; Konflikte oder Mehrdeutigkeiten bleiben explizite Fehler statt impliziter Überschreibungen.
- Sessions ohne vollständige Task-Verfügbarkeit bleiben importierbar; nur tatsächlich vorbereitete Tasks werden synchronisiert.
- Workbook-Zeilen ohne neue Dateien können dennoch DB- oder Runtime-Metadaten aktualisieren; sie erzeugen aber keine erfundenen Audioartefakte.
- `--sync-raw-only` ist obsolet und kein aktiver Pfad mehr.

## Schritt 8: Runtime, Archiv und Paket validieren

- Runtime-Tree prüfen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/validate_research_intake.py runtime-tree --session-dir C:/dev/promat/data/sessions/spanish/ES-L-0001-2026-S01`
- Archiv-Tree prüfen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/validate_research_intake.py archive-tree --archive-session-dir C:/dev/promat_data_archive/sessions/es/ES-L-0001-2026-S01`

Regeln:

- Runtime-Validierung blockiert WAV, TextGrid, XLSX, `secure/`, `raw/`, `source/`, `alignment_source/`, `working/` und andere Intake-Reste.
- Archiv-Validierung prüft die Session-zentrierte Struktur und den Archiv-Manifest-Vertrag.
- Paket-Validierung blockiert dieselben verbotenen Artefaktfamilien zusätzlich für Upload-Pakete.

## Schritt 9: Explizites Prod-Upload-Paket bauen

- Paket bauen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/build_prod_upload_package.py --language spanish --session-id ES-L-0001-2026-S01 --db-payload C:/dev/promat_data_archive/batches/spanish_batch_20260421/import_payload.json`
- Paket validieren:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/validate_research_intake.py prod-package --package-dir C:/dev/promat/scripts/research_data_intake/exports/promat_upload_20260525T120000Z`

Regeln:

- Das Upload-Paket ist eine explizite Allowlist-Auswahl aus validierten Runtime-Artefakten plus optionalem `db/import_payload.json`.
- Das Paket ist kein zweiter Importer und liest keine Batch-Rohdateien neu als Wahrheit ein.
- Auslassung im Paket löscht niemals implizit bestehende Prod-Dateien.

## Schritt 10: Expliziter Dev-Research-File-Reset

- Nur anzeigen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/reset_dev_research_runtime.py`
- Wirklich ausführen:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/reset_dev_research_runtime.py --yes`

Regeln:

- Dieser Reset betrifft nur lokale Dev-Research-Runtime-Dateien unter `data/sessions/`.
- Das externe Archiv unter `PROMAT_LOCAL_ARCHIVE_ROOT` bleibt unberührt.
- Teaching, `content/`, `public/teaching/` und andere Produktivflächen bleiben unberührt.
- Ein Dev-DB-Reset ist ein separater expliziter Schritt und kein Nebeneffekt dieses Runbooks.

## Ergebnis dieses Runbooks

- Ziel ist ein batch-lokaler `working/`-Baum pro `person_id` und Task plus ein kontrollierter Import nach Runtime, Dev-DB und externem Archiv.
- Runtime enthält nur finale JSON/MP3-Artefakte.
- Das lokale Archiv trägt die vollständige nachvollziehbare Session-Historie.
- Prod-Uploads entstehen separat und allowlist-basiert.

## Bewusst nicht Teil dieses Runbooks

- produktive Interview-Renderer oder Player-Artefaktableitung jenseits des Runtime-Vertrags
- direkte Server-Merge-Implementierung
- Teaching-Import oder Teaching-Publikationspfade
