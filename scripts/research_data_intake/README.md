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
- `processed/` bleibt auch für den inkrementellen Working-Tree der primäre Intake-Eingang; `raw/` bleibt optional und darf nicht als Ersatz für den operativen `source/`-Layer umgedeutet werden.
- Wenn `raw/` echte unveränderte Original-WAV-Master enthält, ist dieser Bereich die Archivquelle für den produktiven Session-Baum unter `data/sessions/{language}/{session_id}/raw/`.
- `raw/` und `processed` beziehungsweise später `source/` dürfen dabei nicht vermischt werden.
- `working/` innerhalb eines Batch-Ordners ist eine vorbereitende person- und task-zentrierte Arbeitsstruktur, keine Produktionsablage.

## Working-Tree-Zielstruktur

- `working/.intake_state.json`
- `working/{person_id}/wordlist/source/wordlist.wav`
- `working/{person_id}/wordlist/alignment/wordlist.TextGrid`
- `working/{person_id}/text/source/text.wav`
- `working/{person_id}/text/alignment/text.TextGrid`
- `working/{person_id}/text/alignment/text.json`
- `working/{person_id}/text/mfa_corpus/`
- `working/{person_id}/text/mfa_output/`
- `working/{person_id}/text/mfa_manifest.json`
- `working/{person_id}/interview/source/interview.wav`
- `working/{person_id}/interview/alignment/interview.json`

## Aktuell implementierte Working-Pipeline

- `import/organize_batch_working_tree.py` organisiert einen gewählten Batch inkrementell pro `person_id` und Task in die kanonische `working/`-Struktur, führt den batch-lokalen Zustand in `working/.intake_state.json` und ersetzt nur die tatsächlich geänderten Task-Unterbäume.
- Für `wordlist` und `text` vergleicht dieser Organizer nur die relevanten `processed/`-Inputs je Task, lässt unveränderte Tasks unangetastet und räumt bei Änderungen nur `working/{person_id}/{task}/` gezielt neu auf.
- Für `interview` organisiert derselbe Schritt `working/{person_id}/interview/source/interview.wav` plus `working/{person_id}/interview/alignment/interview.json`; das JSON wird aus dem ausgewählten Amberscript-Export transformiert, nicht als Rohdatei weitergereicht.
- Für Native Speaker mit `person_id`-Marker `-N-` ist `interview` in diesem Pfad fachlich nicht erwartet; fehlende Interview-WAVs oder -JSONs werden deshalb neutral als `not_expected_for_native_speaker` statt als fehlend gemeldet.
- Interview-Materialreferenzen werden in Amberscript nur noch als kompakte Marker direkt am referenzierenden Token gepflegt, zum Beispiel `89[wl_089].`, `D5[d_05]` oder `Nummero [wl_087]`.
- Diese Marker bleiben im Working-JSON nicht roh stehen: `segment.text` bildet weiterhin die sichtbare Segmentoberfläche, `tokens[].text` enthält den gesprochenen Kern, optionale nachgestellte Markerinterpunktion bleibt tokennah in `tokens[].suffix`, und `annotations[]` tragen nur die strukturierte `material_ref`-Referenz mit `item_id`, `task`, `label`, `item_number`, `canonical_text` und `insert_after_token_id`.
- Sichtbare Referenzlabels werden dabei nicht frei aus dem Editor übernommen, sondern ausschließlich aus den kanonischen Katalogen unter `data/config/research_player/{language}/task_catalogs/wordlist.json` und `text.json` aufgelöst.
- `alignment_export/import_interview_amberscript.py` ist der wiederverwendbare Transformationsschritt für Amberscript-JSON nach `working/{person_id}/interview/alignment/interview.json`.
- `alignment_export/prepare_text_mfa_corpus.py` erzeugt aus `working/{person_id}/text/` den MFA-Zwischenstand aus segmentierten `.wav`-Dateien, `.lab`-Dateien, `mfa_output/` und `mfa_manifest.json`.
- `alignment_export/import_text_mfa_alignment.py` importiert die MFA-Ergebnisse aus `working/{person_id}/text/mfa_output/` zurück in `working/{person_id}/text/alignment/text.json`.
- Dieses `alignment/text.json` ist ein bewusst batch-lokales Zwischenartefakt im Working-Tree und noch kein finaler Transfer nach `data/`.
- `import_batch_to_production.py` ist der zentrale orchestrierende Produktionsimport: Workbook lesen, Session-ID ableiten, PostgreSQL-Metadaten schreiben, Runtime-Session-Verzeichnisse erzeugen, echte Raw-Master archivieren und produktive `wordlist`-/`text`-Artefakte delegieren sowie `interview` aus dem Working-Tree in den Runtime-Baum übernehmen.
- Der aktuelle `text`-Workflow arbeitet mit kanonischen Zieltexten aus einer expliziten Textquelle und benutzt das vorhandene `text.TextGrid` nur als Segmentgrenzenquelle.
- MFA-Warnungen zu OOVs, Dysfluencies und Selbstreparaturen sind Qualitätssignale, aber im aktuellen Working-Pfad nicht automatisch Abbruchgründe.
- Für `text` wird bewusst auf kanonische Zielwörter aligned; Dysfluency-Elemente müssen in diesem Schritt nicht vollständig als eigene Zielstruktur modelliert werden.
- Für `interview` bevorzugt der Organizer `*_interview_processed.wav` und `*_interview_processed.json`; wenn diese fehlen, fallen WAV und JSON separat auf `*_interview_raw.wav` beziehungsweise `*_interview_raw.json` zurück. Mehrere gleichrangige Kandidaten sind harte Konflikte.

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
- `import/organize_batch_working_tree.py` meldet taskweise ehrliche Stati wie `unchanged`, `rebuilt`, `missing_json` oder Konflikte und überschreibt ohne nachweisbare Vorzustandslogik keine fremd oder unklar entstandenen Task-Unterbäume stillschweigend.
- Interview-Transformationen melden bei kaputten Markerformen oder unbekannten `item_id`-Werten ebenfalls ehrliche Fehlerstati wie `error_invalid_material_ref_marker` oder `error_unknown_material_ref_item_id`, statt halbsyntaktische Rohmarker in das Working-JSON durchzureichen.
- `import/organize_batch_working_tree.py` unterstützt optional `--force-task {wordlist,text,interview}` für gezielte Task-Rebuilds und `--report-json <path>` für maschinenlesbare Run-Reports.
- Bestehende reale Ergebnisse im `working/`-Baum werden ohne taskbezogene Änderungsursache oder explizites `--replace-existing` nicht pauschal überschrieben.

## Aktueller Produktionsstand

- Der finale Import aus Batch/Working nach `data/` läuft über `import_batch_to_production.py`.
- Die finale `session_id`-Setzung ist Teil dieses zentralen Imports.
- Reale Batch-`raw/`-Master werden dort archivisch korrekt nach `data/sessions/{language}/{session_id}/raw/` übernommen; fehlende Raw-Master bleiben sichtbar fehlend.
- Produktions-`derived/*.mp3` für `wordlist` und `text` werden dort über die wiederverwendbaren Task-Prozessoren erzeugt.
- `interview` wird dort jetzt ebenfalls produktiv übernommen: `source/interview.wav`, `alignment/interview.json` und `derived/interview.mp3` landen im Runtime-Session-Baum, und die Runtime-`metadata.json` referenziert die tatsächlich erzeugten Interview-Artefakte.
- Für Native Speaker bleibt `interview` auch im Produktionsimport ein neutral nicht erwarteter Task: fehlende Working- oder Raw-Interview-Dateien zählen dort nicht als Defizit und erzeugen keine Runtime-Interview-Artefakte.
- Produktive MFA-Ausführung bleibt weiterhin ein vorgelagerter externer oder manueller Schritt vor dem finalen Import.

## Einstiegspunkte

- Die bestehende `wordlist`-Produktionspipeline bleibt in `scripts/research_data_intake/produce_wordlist_artifacts.py` separat bestehen.
- Die `text`-Produktionspipeline steht wiederverwendbar in `scripts/research_data_intake/produce_text_artifacts.py` bereit.
- Der zentrale Workbook-plus-Working-Import steht in `scripts/research_data_intake/import_batch_to_production.py`.
- Für reine Nacharchivierung bereits importierter Sessions unterstützt derselbe zentrale Importer den Modus `--sync-raw-only`.
- Der wiederholbare Ablauf für den generischen Batch- und Working-Pfad steht ergänzend in `docs/runbooks/research-intake-working-pipeline.md`.