# session_setup

Hilfen zur Anlage neuer Sessions, Ordner und Metadatenvorlagen.

- `seed_dev_spanish_example_sessions.py` legt den lokalen Dev-Beispieldatensatz für 11 spanische Sessions aus `data/example_data/` in der kanonischen Session-Struktur unter `data/sessions/spanish/` an.
- Das Manifest verwendet kanonische IDs: `person_id = {CORPUS_CODE}-{SPEAKER_MARKER}-{NNNN}` und `session_id = {person_id}-{YYYY}-S{NN}`.
- Der aktuelle spanische Dev-Seed enthält echte Mehrfach-Sessions für einige Lernenden-Personen, damit personbasierte Aggregation im UI und in Skripten überprüfbar bleibt.
- Lernenden-Seeds schreiben drei dokumentierte Tasks (`wordlist`, `text`, `interview`); Native-Speaker-Seeds schreiben nur `wordlist` und `text`.
- Die aktuellen Beispiel-WAVs aus `data/example_data/` werden als bearbeitete Arbeitsfassungen nach `source/{task}.wav` übernommen; `raw/` bleibt für diese Seed-Daten leer.
- Für diese Seed-Daten liegen aktuell keine echten unbearbeiteten `raw`-Masterdateien vor.
- Spätere Alignment-JSONs gehören unter `alignment/{task}.json`; `items/{task}/` bleibt für Split-MP3s reserviert.
- `dev_spanish_example_sessions.json` ist das deterministische Seed-Manifest für Person-, Session- und Quelldatei-Mapping.
- Lernenden-Seeds schreiben `current_region`, `childhood_region` und `stays_in_target_country`.
- Native-Speaker-Seeds schreiben `standard_variety`, `origin_country` und `origin_region` statt lernendentypischer Regionalfelder.
