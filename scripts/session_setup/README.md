# session_setup

Hilfen zur Anlage neuer Sessions, Ordner und Metadatenvorlagen.

- `seed_dev_spanish_example_sessions.py` legt den lokalen Dev-Beispieldatensatz fuer 11 spanische Sessions aus `data/example_data/` in der kanonischen Session-Struktur unter `data/sessions/spanish/` an.
- Die aktuellen Beispiel-WAVs aus `data/example_data/` werden als bearbeitete Arbeitsfassungen nach `source/isolated_speech.wav` uebernommen; `raw/` bleibt fuer diese Seed-Daten leer.
- Fuer diese Seed-Daten liegen aktuell keine echten unbearbeiteten `raw`-Masterdateien vor.
- Spaetere Alignment-JSONs gehoeren unter `alignment/{task}.json`; `items/{task}/` bleibt fuer Split-MP3s reserviert.
- `dev_spanish_example_sessions.json` ist das deterministische Seed-Manifest fuer Person-, Session- und Quelldatei-Mapping.
