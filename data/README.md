# data

Dieser Ordner ist der vorbereitete geschuetzte Forschungsdatenraum.
Er enthaelt Runtime-Konfiguration, lokale Dev-DB-Ablagen und die session-basierte Forschungsstruktur unter `data/sessions/`.

Verbindliche Audio- und Session-Logik:

- `raw/` enthaelt nur unbearbeitete Original-WAVs aus der Aufnahme.
- `source/` enthaelt bearbeitete Arbeits-WAVs mit standardisierten Pausen, Normalisierung oder vergleichbaren Verarbeitungsschritten.
- `derived/` enthaelt daraus abgeleitete Webformate der Gesamtaufnahme, insbesondere MP3.
- `alignment/` enthaelt TextGrid-Dateien und spaetere reduzierte Alignment-JSONs der Gesamtaufnahme wie `alignment/wordlist.json`.
- `items/{task}/` enthaelt nur gesplittete Einzel-MP3s und keine Alignment-JSON-Dateien.

Fuer die aktuellen spanischen Dev-Beispielsessions gilt:

- die vorhandenen Beispiel-WAVs sind fachlich `source` und liegen deshalb unter `source/wordlist.wav`
- fuer diese Beispielsessions liegen aktuell keine echten `raw`-Dateien vor
- spaetere Splits sollen aus `source/{task}.wav` anhand von `alignment/{task}.json` erzeugt werden
