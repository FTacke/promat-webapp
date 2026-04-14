# Research Data Intake Scripts

## Zweck

Dieser Bereich bündelt die Intake- und Ableitungspipeline für forschungsbezogene Session-Daten.

Wenn für einen Task ein kanonischer Katalog unter `data/config/research_player/{language}/task_catalogs/` existiert, verwenden Ableitungsschritte diesen Katalog als Inhaltsbasis und ergänzen nur session-spezifische Zeit-, Split- und Audio-Daten.

## Gehört hierher

- Session-Setup und Seed-Skripte für Forschungsdaten
- Audio-Ableitung für Research-Player-Artefakte
- Item-Splitting für task-spezifische Derivate
- Alignment- oder JSON-Export für Player-fähige Strukturdaten
- intake-nahe Importschritte für Forschungs-Sessiondaten

## Gehört nicht hierher

- allgemeine Dev-Start- oder Setup-Skripte
- allgemeine Maintenance-Skripte ohne direkten Intake- oder Ableitungsbezug
- Public-Export-Schritte, die ausschließlich freigegebene Inhalte nach `public/` schreiben

## Struktur

- `session_setup/`: sessionbezogene Seeds und Setup-Schritte
- `audio_conversion/`: Ableitung von Full-MP3-Webartefakten
- `item_split/`: Ableitung von Split-MP3-Artefakten
- `alignment_export/`: Export playerfähiger Alignment- oder JSON-Artefakte sowie vorbereitende Alignment-Schritte wie MFA-Zwischenkorpora
- `import/`: generische Batch-Eingänge, intake-nahe Importschritte und zugehörige Hilfsartefakte

## Intake-Batches

- `import/` ist der Intake-/Batch-Eingangsbereich für konkrete Roh- oder Vorverarbeitungsbatches.
- Batch-Ordner unter `scripts/research_data_intake/import/` sind generisch und nicht auf `spanisch_batch` oder eine bestimmte Sprache fest verdrahtet.
- Ein Batch kann mindestens `processed/` enthalten und optional `raw/` sowie `intake_data/`.
- `working/` innerhalb eines Batch-Ordners ist eine vorbereitende person- und task-zentrierte Arbeitsstruktur, keine Produktionsablage.
- Diese vorbereitenden Schritte schreiben bewusst noch nicht nach `data/` und erzeugen noch keine finalen Produktions-Metadaten oder finalen `alignment/text.json`-Artefakte.

## Vorbereitende Batch-Schritte

- `scripts/research_data_intake/import/organize_batch_working_tree.py` überführt einen konkreten Batch generisch aus `processed/` und optional `raw/` in die kanonische `working/`-Struktur pro `person_id` und `task`.
- Das Skript erwartet `--batch-dir`, unterstützt `--dry-run` und verwendet standardmäßig die sichere Transferstrategie `--copy`; alternativ stehen `--move` und `--symlink` bereit.
- Die Zielbenennung in `working/` ist kanonisch auf Task-Rollen ausgerichtet, etwa `working/{person_id}/text/source/text.wav` und `working/{person_id}/text/alignment/text.TextGrid`.
- `scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py` arbeitet auf dieser `working/`-Struktur und bereitet daraus pro Person einen MFA-Zwischenkorpus für `text` vor.
- Das Skript erwartet `--batch-dir` und eine explizite Solltextquelle per `--text-source-json`; optional kann `--person-id` auf eine Person einschränken.
- Der vorbereitende `text`-Schritt erzeugt nur segmentierte `.wav`-Dateien, zugehörige `.lab`-Dateien, `mfa_output/`-Zielordner und ein Manifest `working/{person_id}/text/mfa_manifest.json`.
- Das vorhandene `TextGrid` dient in diesem Schritt nur als Segmentquelle; der kanonische Solltext muss explizit von außen geliefert werden und wird nicht aus Labels erraten.

## Bewusst noch nicht implementiert

- MFA-Ausführung selbst
- Import von MFA-Outputs in finale `alignment/text.json`
- finaler Transfer in die Produktionsumgebung unter `data/`
- vollständige XLSX-/Metadatenintegration für den Endimport

## Aktueller Einstiegspunkt

- `scripts/research_data_intake/produce_wordlist_artifacts.py` implementiert die aktuelle reale `wordlist`-Produktionspipeline.
- Das CLI unterstützt `--session-id`, `--all-suitable-sessions`, `--dry-run` und `--validate-labels {off,warn,fail}`.
- Batch-Verarbeitung schreibt nur für Sessions mit nicht-leerem `source/wordlist.wav`, nicht-leerem `alignment/wordlist.TextGrid` und kanonischen Grenzen innerhalb der verfügbaren Audio-Dauer.