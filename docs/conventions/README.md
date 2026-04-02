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
- Ausdrücke wie `isolated_speech`, `connected_speech` und `reflexion` sind keine aktiven technischen Standards mehr.

## Kontrollvokabulare

- Aktive `speaker_type`-Werte sind nur `learner` und `native_speaker`; `heritage_speaker` ist kein aktiver Soll-Stand.
- Aktive Speaker-Marker in IDs sind nur `L` und `N`.
- `target_language` bleibt technisch lowercase: `es`, `fr`, `en`, `de`.
- `standard_variety` bleibt lowercase snake_case; aktive Schweizer Werte sind `fr_ch_std` und `de_ch_std`, nicht `ch_std`.
- `unknown` ist die kanonische aktive Kleinform; `l1_code` bleibt dagegen uppercase.
- Das aktive Intake-Workbook nutzt nur das breite Blatt `Vocabularies`; eine normalisierte Feld-Wert-Alternative ist kein aktiver Standard.
- Im Intake verknüpft `Exposure` Zeilen nur über `person_id` plus `session_ref`; `session_id` bleibt dort leer.

## IDs und Sessions

- `person_id` identifiziert Personen stabil.
- `session_id` identifiziert konkrete Aufnahmen.
- Kanonische Formate sind `person_id = {CORPUS_CODE}-{SPEAKER_MARKER}-{NNNN}` und `session_id = {person_id}-{YYYY}-S{NN}`.
- `session_id` trägt nur Personbezug, Aufnahmejahr und Session-Nummer; Level, L1 und Standardvarietät bleiben Metadaten.
- Sessions liegen unter `data/sessions/{language}/{session_id}/`.
- Session-Unterstruktur: `raw/`, `source/`, `alignment/`, `derived/`, `items/`, `metadata.json`.
- `speakers` aggregiert pro `person_id`; `recordings` bleibt session- und taskbasiert.
- Native-Speaker-Vergleichsprofile haben genau eine Session pro nativer `person_id`.

## Task- und Dateistandards

- Verbindliche Task-Typen: `wordlist`, `text`, `interview`.
- Verbindliche Verarbeitungsstufen: `raw`, `source`, `alignment`, `derived`, `items`.
- `raw/` enthält nur unbearbeitete Original-WAVs.
- `source/` enthält bearbeitete Arbeits-WAVs und ist die Basis für Annotation, spätere Alignment-JSON und spätere Splits.
- `derived/` enthält abgeleitete Gesamtdateien für die Webapp, z. B. MP3.
- `alignment/` enthält TextGrid plus reduzierte JSON-Segmentdaten der Gesamtaufnahme; diese JSON gehört nicht unter `items/`.
- `items/{task}/` enthält nur Split-MP3s.
- Beispiele fuer interne Split-Dateien sind `items/wordlist/es_wordlist_001.mp3` und `items/text/es_text_002.mp3`.
- Interne Split-Dateinamen basieren auf stabiler `item_id`; längere Namen mit `session_id` und Label sind Sache der späteren Download-Logik.
- Die aktuellen spanischen Dev-Beispiel-WAVs sind fachlich `source` und nicht `raw`.
- Für die aktuellen spanischen Dev-Beispielsessions liegen keine echten `raw`-Dateien vor.
- Die spätere Pipeline lautet `TextGrid -> alignment JSON -> item splits`; geschnitten wird aus `source/{task}.wav`, und `silent`-Intervalle gehen nicht in die reduzierte Alignment-JSON ein.
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