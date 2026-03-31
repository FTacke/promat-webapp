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