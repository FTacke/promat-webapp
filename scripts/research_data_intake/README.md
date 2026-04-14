# Research Data Intake Scripts

## Zweck

Dieser Bereich bündelt die Intake- und Ableitungspipeline für forschungsbezogene Session-Daten.

Wenn für einen Task ein kanonischer Katalog unter `data/config/research_player/{language}/task_catalogs/` existiert, verwenden Ableitungsschritte diesen Katalog als Inhaltsbasis und ergänzen nur session-spezifische Zeit-, Split- und Audio-Daten.

## Gehört hierher

- Session-Setup und Seed-Skripte für Forschungsdaten
- Audio-Ableitung für Research-Player-Artefakte
- Item-Splitting für task-spezifische Derivate
- Alignment- oder JSON-Export für Player-fähige Strukturdaten
- intake-nahe Batch- und Vorverarbeitungsschritte für Forschungsdaten

## Gehört nicht hierher

- allgemeine Dev-Start- oder Setup-Skripte
- allgemeine Maintenance-Skripte ohne direkten Intake- oder Ableitungsbezug
- Public-Export-Schritte, die ausschließlich freigegebene Inhalte nach `public/` schreiben

## Struktur

- `session_setup/`: sessionbezogene Seeds und Setup-Schritte
- `audio_conversion/`: Ableitung von Full-MP3-Webartefakten
- `item_split/`: Ableitung von Split-MP3-Artefakten
- `alignment_export/`: Export playerfähiger Alignment- oder JSON-Artefakte sowie vorbereitende Alignment-Schritte wie MFA-Zwischenkorpora und Working-Tree-Rückimporte
- `import/`: generische Batch-Eingänge, intake-nahe Importschritte und zugehörige Hilfsartefakte

## Generische Batch-Ordner

- `scripts/research_data_intake/import/` ist der generische Intake-Eingangsbereich für konkrete Roh- oder Vorverarbeitungsbatches.
- Ein verarbeitbarer Batch ist ein Ordner unter diesem Import-Root, dessen Name `batch` enthält und der mindestens `processed/` enthält.
- `raw/` und `intake_data/` sind optionale begleitende Eingangsbereiche.
- Batch-Ordner dürfen nicht auf feste Namen wie `spanish_batch` oder `spanisch_batch` verdrahtet sein; die Resolver-Logik arbeitet auf beliebigen passenden Batch-Namen.
- `processed/` ist der zentrale Eingang für die aktuelle Weiterverarbeitung von task-bezogenen WAVs und TextGrids.
- Wenn `raw/` echte unveränderte Original-WAV-Master enthält, ist dieser Bereich die Archivquelle für den produktiven Session-Baum unter `data/sessions/{language}/{session_id}/raw/`.
- `raw/` und `processed` beziehungsweise später `source/` dürfen dabei nicht vermischt werden.
- `working/` innerhalb eines Batch-Ordners ist eine vorbereitende person- und task-zentrierte Arbeitsstruktur, keine Produktionsablage.

## Working-Tree-Zielstruktur

- `working/{person_id}/wordlist/source/wordlist.wav`
- `working/{person_id}/wordlist/alignment/wordlist.TextGrid`
- `working/{person_id}/text/source/text.wav`
- `working/{person_id}/text/alignment/text.TextGrid`
- `working/{person_id}/text/alignment/text.json`
- `working/{person_id}/text/mfa_corpus/`
- `working/{person_id}/text/mfa_output/`
- `working/{person_id}/text/mfa_manifest.json`
- `working/{person_id}/interview/source/interview.wav`
- `working/{person_id}/interview/alignment/interview.TextGrid`

## Aktuell implementierte Working-Pipeline

- `import/organize_batch_working_tree.py` organisiert einen gewählten Batch aus `processed/` und optional `raw/` in die kanonische `working/`-Struktur pro `person_id` und `task`.
- `alignment_export/prepare_text_mfa_corpus.py` erzeugt aus `working/{person_id}/text/` den MFA-Zwischenstand aus segmentierten `.wav`-Dateien, `.lab`-Dateien, `mfa_output/` und `mfa_manifest.json`.
- `alignment_export/import_text_mfa_alignment.py` importiert die MFA-Ergebnisse aus `working/{person_id}/text/mfa_output/` zurück in `working/{person_id}/text/alignment/text.json`.
- Dieses `alignment/text.json` ist ein bewusst batch-lokales Zwischenartefakt im Working-Tree und noch kein finaler Transfer nach `data/`.
- `import_batch_to_production.py` ist der zentrale orchestrierende Produktionsimport: Workbook lesen, Session-ID ableiten, PostgreSQL-Metadaten schreiben, Runtime-Session-Verzeichnisse erzeugen, echte Raw-Master archivieren und produktive `wordlist`-/`text`-Artefakte delegieren.
- Der aktuelle `text`-Workflow arbeitet mit kanonischen Zieltexten aus einer expliziten Textquelle und benutzt das vorhandene `text.TextGrid` nur als Segmentgrenzenquelle.
- MFA-Warnungen zu OOVs, Dysfluencies und Selbstreparaturen sind Qualitätssignale, aber im aktuellen Working-Pfad nicht automatisch Abbruchgründe.
- Für `text` wird bewusst auf kanonische Zielwörter aligned; Dysfluency-Elemente müssen in diesem Schritt nicht vollständig als eigene Zielstruktur modelliert werden.

## Sprachkonfiguration

- `produce_wordlist_artifacts.py` und `produce_text_artifacts.py` akzeptieren ebenfalls `--language`, damit Katalogauflösung und Runtime-Session-Auswahl nicht implizit nur auf Spanisch festliegen.
- Im aktuellen Repo ist `data/config/research_player/english/task_catalogs/` jetzt die kanonische Inhaltsquelle für den späteren generischen `english_batch`-Working- und Produktionspfad; der englische `text`-Katalog bleibt item-zentriert, obwohl er als connected text modelliert ist.

## Optionaler MFA-Modell-Preload

- `alignment_export/preload_mfa_models.py` prüft die konfigurierte MFA-CLI und zeigt die zugehörigen Modelle für konfigurierte Intake-Sprachen an.
- Standardmodus ist rein lesend und lädt nichts herunter.
- Mit `--download-models` werden die konfigurierten Acoustic- und Dictionary-Modelle explizit geladen.
- Wenn die MFA-CLI lokal nicht verfügbar ist, bricht dieses Skript sauber mit einer ehrlichen Fehlermeldung ab.
- Beispiel nur prüfen:
	`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/preload_mfa_models.py --language es`
- Beispiel mit explizitem Download in einer MFA-fähigen Shell:
	`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/preload_mfa_models.py --language es --download-models`

## CLI-Realität

- Alle neuen Working-Tree-Schritte erwarten weiterhin explizit `--batch-dir`; verarbeitet wird genau der Batch, den die Resolver-Logik unter `scripts/research_data_intake/import/` auflöst.
- Batch-Läufe nennen in ihrer Ausgabe immer den tatsächlich verarbeiteten Batch-Pfad.
- Bestehende reale Ergebnisse im `working/`-Baum werden ohne `--replace-existing` nicht stillschweigend überschrieben.

## Aktueller Produktionsstand

- Der finale Import aus Batch/Working nach `data/` läuft über `import_batch_to_production.py`.
- Die finale `session_id`-Setzung ist Teil dieses zentralen Imports.
- Reale Batch-`raw/`-Master werden dort archivisch korrekt nach `data/sessions/{language}/{session_id}/raw/` übernommen; fehlende Raw-Master bleiben sichtbar fehlend.
- Produktions-`derived/*.mp3` für `wordlist` und `text` werden dort über die wiederverwendbaren Task-Prozessoren erzeugt.
- `interview` bleibt über den aktuellen Strukturplatzhalter hinaus noch unproduktiv.
- Produktive MFA-Ausführung bleibt weiterhin ein vorgelagerter externer oder manueller Schritt vor dem finalen Import.

## Einstiegspunkte

- Die bestehende `wordlist`-Produktionspipeline bleibt in `scripts/research_data_intake/produce_wordlist_artifacts.py` separat bestehen.
- Die `text`-Produktionspipeline steht wiederverwendbar in `scripts/research_data_intake/produce_text_artifacts.py` bereit.
- Der zentrale Workbook-plus-Working-Import steht in `scripts/research_data_intake/import_batch_to_production.py`.
- Für reine Nacharchivierung bereits importierter Sessions unterstützt derselbe zentrale Importer den Modus `--sync-raw-only`.
- Der wiederholbare Ablauf für den generischen Batch- und Working-Pfad steht ergänzend in `docs/runbooks/research-intake-working-pipeline.md`.