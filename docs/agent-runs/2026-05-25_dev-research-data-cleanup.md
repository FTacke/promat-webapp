# Dev Research Data Cleanup

Datum: 2026-05-25

## Ziel

Kontrolliertes Entfernen vorlaeufiger lokaler Dev-Research-Runtime-Daten unter `data/`, ohne Eingriffe in `content/`, `public/teaching`, produktive Serverpfade oder das externe Archiv `C:\dev\promat_data_archive`.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `data/config/research_player/README.md`

## Geaenderte Bereiche

- geloescht: `data/sessions/english/EN-L-0001-2026-S01/`
- geloescht: `data/sessions/spanish/ES-L-0001-2026-S01/`
- geloescht: `data/sessions/spanish/ES-L-0002-2026-S01/`
- geloescht: `data/sessions/spanish/ES-L-0003-2026-S01/`
- geloescht: `data/sessions/spanish/ES-L-0004-2026-S01/`
- geloescht: `data/sessions/spanish/ES-L-0005-2026-S01/`
- geloescht: `data/sessions/spanish/ES-L-0006-2026-S01/`
- geloescht: `data/sessions/spanish/ES-L-0007-2026-S01/`
- geloescht: `data/sessions/spanish/ES-L-0008-2026-S01/`
- geloescht: `data/sessions/spanish/ES-L-0009-2026-S01/`
- geloescht: `data/sessions/spanish/ES-N-0001-2026-S01/`
- geloescht: `data/sessions/spanish/ES-N-0002-2026-S01/`
- angelegt: leere Sprachordner `data/sessions/de/`, `data/sessions/en/`, `data/sessions/es/`, `data/sessions/fr/`

## Wichtige Entscheidungen

- `data/config/research_player/` wurde vollstaendig behalten, weil README, Skript-Doku und Code diese Dateien als kanonische corpus-spezifische Konfigurations- und Katalogquelle definieren.
- `data/db/postgres_dev/` blieb unangetastet, weil der Prompt keinen Dev-Postgres-Reset beauftragt und DB-Aktionen explizit ausgeschlossen waren.
- Nicht vorhandene Import-/Report-Pfade `data/incoming`, `data/production`, `data/quarantine`, `data/publish_logs`, `data/manifests` und `data/reports` wurden nicht erzeugt und nicht veraendert.
- Vorhandene Platzhalterdateien `data/.gitkeep`, `data/sessions/.gitkeep` und `data/sessions/spanish/.gitkeep` blieben erhalten.

## Abweichungen

- Keine Abweichung vom beauftragten Scope.

## Verifikation

- Session-Ordner vor dem Cleanup enumeriert und als Loeschmenge festgehalten.
- `data/config/research_player/README.md` sowie Codeverweise auf `player_config.json`, `phenomena_presets.json` und `task_catalogs/` geprueft.
- Vor dem Cleanup bestaetigt, dass `data/incoming`, `data/production`, `data/quarantine`, `data/publish_logs`, `data/manifests` und `data/reports` lokal nicht existieren.
- Nach dem Cleanup validiert: unter `data/sessions` bleiben nur `data/sessions/.gitkeep` und `data/sessions/spanish/.gitkeep` als Dateien bestehen.
- Nach dem Cleanup validiert: `*.mp3`, `*.json`, `*.TextGrid` und `*.wav` unter `data/sessions` jeweils `0` Treffer.
- `git status --short -- data content public/teaching` blieb ohne Ausgabe.
- Externes Archiv `C:\dev\promat_data_archive` nur per `Test-Path` auf Existenz geprueft, nicht veraendert.

## Offene Punkte

- `data/db/postgres_dev/` enthaelt weiterhin den lokalen Dev-Postgres-Dateibaum; falls ein separater DB-Cleanup gewuenscht ist, braucht das einen eigenen, expliziten Schritt ausserhalb dieses Runs.

## Naechste sinnvolle Schritte

- Optional getrennt entscheiden, ob der lokale Dev-Postgres-Bestand ebenfalls kontrolliert zurueckgesetzt werden soll.