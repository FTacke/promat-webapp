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
- `alignment_export/`: Export playerfähiger Alignment- oder JSON-Artefakte
- `import/`: intake-nahe Importschritte und zugehörige Hilfsartefakte

## Aktueller Einstiegspunkt

- `scripts/research_data_intake/produce_wordlist_artifacts.py` implementiert die aktuelle reale `wordlist`-Produktionspipeline.
- Das CLI unterstützt `--session-id`, `--all-suitable-sessions`, `--dry-run` und `--validate-labels {off,warn,fail}`.
- Batch-Verarbeitung schreibt nur für Sessions mit nicht-leerem `source/wordlist.wav`, nicht-leerem `alignment/wordlist.TextGrid` und kanonischen Grenzen innerhalb der verfügbaren Audio-Dauer.