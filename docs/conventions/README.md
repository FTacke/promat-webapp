# Conventions

Dies ist die aktive Kurzform der verbindlichen Repo-Konventionen. Wenn diese Datei und die Spezifikation auseinanderlaufen, ist diese Datei zu korrigieren oder die Abweichung explizit zu dokumentieren.

## Routing

- Öffentliches Routing folgt `/{ui_lang}/{section}/{corpus_language}/{page}`.
- Verbindliche technische Sections sind `project`, `research`, `teaching`, `sample`.
- Verbindliche technische corpus languages sind `spanish`, `french`, `german`, `english`.
- Verbindliche Forschungsseiten sind `design`, `speakers`, `recordings`, `comparison`, `phenomena`.
- Verbindliche Unterrichtsseiten sind `phenomena`, `materials`.

## Sprache und Benennung

- Technische Slugs, Feldnamen und Controlled Vocabularies sind Englisch.
- Sichtbare UI-Labels sind aktuell deutsch und lokalisierbar.
- Alte deutsche Slugs und alte technische Begriffe werden nicht wieder eingeführt.
- Ausdrücke wie `wordlist`, `text` und `reflexion` sind keine technischen Standards mehr.

## IDs und Sessions

- `person_id` identifiziert Personen stabil.
- `session_id` identifiziert konkrete Aufnahmen.
- Sessions liegen unter `data/sessions/{language}/{session_id}/`.
- Session-Unterstruktur: `raw/`, `source/`, `alignment/`, `derived/`, `items/`, `metadata.json`.

## Task- und Dateistandards

- Verbindliche Task-Typen: `isolated_speech`, `connected_speech`, `interview`.
- Verbindliche Verarbeitungsstufen: `raw`, `source`, `alignment`, `derived`, `items`.
- `raw/` enthaelt nur unbearbeitete Original-WAVs.
- `source/` enthaelt bearbeitete Arbeits-WAVs und ist die Basis fuer Annotation, spaetere Alignment-JSON und spaetere Splits.
- `derived/` enthaelt abgeleitete Gesamtdateien fuer die Webapp, z. B. MP3.
- `alignment/` enthaelt TextGrid plus reduzierte JSON-Segmentdaten der Gesamtaufnahme; diese JSON gehoert nicht unter `items/`.
- `items/{task}/` enthaelt nur Split-MP3s.
- Beispiele fuer interne Split-Dateien sind `items/isolated_speech/es_wordlist_001.mp3` und `items/connected_speech/es_text_002.mp3`.
- Interne Split-Dateinamen basieren auf stabiler `item_id`; laengere Namen mit `session_id` und Label sind Sache der spaeteren Download-Logik.
- Die aktuellen spanischen Dev-Beispiel-WAVs sind fachlich `source` und nicht `raw`.
- Fuer die aktuellen spanischen Dev-Beispielsessions liegen keine echten `raw`-Dateien vor.
- Die spaetere Pipeline lautet `TextGrid -> alignment JSON -> item splits`; geschnitten wird aus `source/{task}.wav`, und `silent`-Intervalle gehen nicht in die reduzierte Alignment-JSON ein.
- Keine sensiblen Daten in Dateinamen, Slugs oder öffentlichen Assets.

## Datenräume

- `secure/`: Klardaten, nie Webapp.
- `data/`: geschützte Forschungsdaten.
- `public/`: explizit freigegebene öffentliche Assets.
- Public-Assets werden nur bewusst exportiert, nie direkt aus `data/` bedient.

## Dokumentation

- Jeder substanzielle Run: Eintrag unter `docs/agent-runs/`.
- Bootstrap-, Setup- und Governance-Runs zusätzlich unter `docs/start/`.
- Dauerhafte Architekturentscheidungen unter `docs/decisions/`.