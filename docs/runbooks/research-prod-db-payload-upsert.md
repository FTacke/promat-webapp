# Runbook: Research Prod DB Payload Upsert

## Zweck

Kontrollierter Ablauf fuer den optionalen Produktions-DB-Upsert aus `db/import_payload.json`.

## Grundsatz

- Runtime-only Publish bleibt der sichere Default.
- Ein vorhandenes `db/import_payload.json` wird nur geschrieben, wenn der Publish mit `--apply-db-upsert` gestartet wird.
- Ohne Flag wird das Payload mit ausgeliefert, aber nicht angewendet.
- Der Upsert betrifft nur `research_people`, `research_sessions` und `research_session_exposures`.
- Der Upsert ist idempotent: stabile Schluessel sind `person_id`, `session_id` und `(session_id, sort_order)` fuer Exposures.
- Nicht im Payload enthaltene Personen oder Sessions werden nicht geloescht. Exposure-Reihen werden nur fuer Sessions im Payload auf die Payload-Reihenfolge gebracht.

## Tool

Dry-run gegen einen bereits gestagten Release aus der Webcontainer-Umgebung:

`docker exec promat-web-prod python /app/scripts/research_data_intake/apply_prod_db_payload.py --release-dir /app/data/releases/<release_id> --payload /app/data/releases/<release_id>/db/import_payload.json`

Transaktional anwenden:

`docker exec promat-web-prod python /app/scripts/research_data_intake/apply_prod_db_payload.py --release-dir /app/data/releases/<release_id> --payload /app/data/releases/<release_id>/db/import_payload.json --apply`

Im Publish-Ablauf ist das direkte Tool normalerweise nicht noetig; bevorzugt wird:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/publish_prod_release.py --upload-id <upload_id> --host vhrz2184 --smoke-base-url <prod-base-url> --apply-db-upsert`

## Server-Gates

Das Upsert-Tool bricht vor jedem Write ab, wenn:

- `db/import_payload.json` fehlt oder kein valides JSON ist.
- Das Payload-Schema nicht zu `persons`, `sessions` und `exposures` passt.
- `batch_name` fehlt oder nicht als Batch erkennbar ist.
- Personen- oder Session-Schluessel doppelt sind.
- Sessions unbekannte Personen referenzieren.
- Exposures unbekannte Sessions referenzieren.
- `target_language` nicht in der Intake-Sprachkonfiguration aufloesbar ist.
- Lokale Windows-Pfade wie `C:\...` oder UNC-Pfade enthalten sind.
- Referenzierte Runtime-Dateien im staged Release fehlen: `metadata.json`, `alignment/{task}.json`, `derived/{task}.mp3`.
- Das Payload keine Personen oder keine Sessions enthaelt.

## Dry-Run

Der Dry-Run schreibt nicht. Er gibt JSON aus mit:

- Modus `dry_run`
- Batch-ID und Sprachen
- Payload-Counts fuer Personen, Sessions, Exposures und dokumentierte Tasks
- pro Tabelle Counts fuer `insert`, `update`, `unchanged`, `delete`
- vorhandene Tabellen-Counts vor dem Write
- Rollback-Hinweis

Der Publish mit `--apply-db-upsert` fuehrt den Dry-Run vor dem echten Write aus und schreibt dessen Ausgabe ins Publish-Log.

## Write, Transaction und Rollback

Der echte Upsert laeuft in einer einzelnen SQLAlchemy-Transaktion. Bei Fehlern wird automatisch gerollt und der Publish bricht vor dem `current`-Switch ab.

Rollback nach einem erfolgreichen Write:

1. Wenn Runtime bereits promoted wurde: `data/current` auf den vorherigen Release zurueckzeigen lassen.
2. DB ueber den vorhandenen Produktions-DB-Backup- oder Snapshot-Weg wiederherstellen.
3. Alternativ nur die im Upsert-Report gelisteten betroffenen Personen, Sessions und Exposures anhand der Pre-Counts und Payload-Schluessel pruefen und gezielt korrigieren.

## Erfolg erkennen

- Dry-Run und Apply geben JSON ohne Fehler aus.
- `post_upsert_validation.status` ist `ok`.
- Publish-Log enthaelt `db_upsert_status: applied`.
- Health/Ready und Research-Smoke-Routen sind nach dem Promote gruen.

## Pflicht-Smoke

Nach einem Publish mit DB-Upsert:

- `/health`
- `/ready`
- `/{ui_lang}/research/{corpus}`
- `/{ui_lang}/research/{corpus}/design`
- ein geschuetzter Player-/Detailpfad nur mit sicherem Auth-Verfahren, ohne Tokens in Logs
