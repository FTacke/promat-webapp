# Session Storage Logic Alignment 01

Datum: 2026-04-01

## Ziel

Die verbindliche Logik fuer `raw`, `source`, `derived`, `alignment`, `items`, spaetere Alignment-JSONs und interne Item-Dateinamen repo-weit konsistent festziehen und die bestehenden spanischen Dev-Beispieldaten fachlich korrigieren.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `docs/conventions/README.md`
- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/config/data_conventions.py`
- `scripts/session_setup/seed_dev_spanish_example_sessions.py`
- `scripts/session_setup/README.md`
- bestehende Session-Dateien unter `data/sessions/spanish/`

## Geaenderte Bereiche

- kanonische Spezifikation in `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- aktive Kurzkonventionen in `docs/conventions/README.md`
- Repo- und Agent-Instruktionen unter `.github/`
- Seed-Logik unter `scripts/session_setup/`
- kanonische File-Role-Vokabulare in `app/src/app/config/data_conventions.py`
- bestehende spanische Dev-Sessions unter `data/sessions/spanish/`

## Wichtige Entscheidungen

- Die vorhandenen spanischen Beispiel-WAVs sind fachlich `source`-Audio und keine `raw`-Masteraufnahmen.
- Fuer diese spanischen Dev-Beispielsessions liegen aktuell keine echten `raw`-Masterdateien vor.
- `alignment/{task}.json` ist spaeter Teil der Alignment-Ebene der Gesamtaufnahme, nicht der Items-Ebene.
- `items/{task}/` enthaelt nur Split-MP3s.
- Interne Split-Dateien werden spaeter nach stabiler `item_id` benannt; laengere Namen mit `session_id` und Label sind nur fuer Download-Logik vorgesehen.
- Die spaetere Pipeline lautet `TextGrid -> alignment JSON -> item splits`, geschnitten aus `source/{task}.wav`; `silent`-Intervalle werden nicht in die reduzierte Alignment-JSON uebernommen.

## Nachgeschaerfte Sichtbarkeit

- `data/README.md` nennt die Audio-Ebenen nun ebenfalls normativ direkt am geschuetzten Datenraum.
- Seed-README und Session-Metadaten nennen nun explizit, dass die aktuellen Dev-Beispiel-WAVs `source` sind und keine echten `raw`-Master vorliegen.

## Abweichungen

- Keine Architekturabweichung eingefuehrt.

## Verifikation

- Seed-Skript und Metadatenlogik wurden auf `source/isolated_speech.wav` umgestellt.
- Bestehende falsch einsortierte Dev-WAVs wurden aus `raw/` in `source/` korrigiert.
- Der Repo-Platzhalter unter `data/sessions/spanish/ES-L-DE-B2-24-001/` wurde auf die neue interne Item-Namenslogik angepasst.
- Die aktiven `.github`-Instruktionen und die Projektspezifikation wurden konsistent nachgezogen.

## Offene Punkte

- Alignment-JSON wird in diesem Schritt bewusst noch nicht erzeugt.
- MP3-Konvertierung und spaetere Item-Splits sind weiterhin offene Folgeschritte.

## Naechste sinnvolle Schritte

- Script fuer `TextGrid -> alignment/isolated_speech.json` auf Basis der `source/`-Aufnahme bauen.
- Danach MP3-Konvertierung der Gesamtaufnahme unter `derived/` und anschliessend Item-Splitting aus `source/` anhand der Alignment-JSON ergaenzen.