# Runbook: Research Prod Upload and Publish

## Zweck

Wiederholbarer Ablauf fuer den sicheren Transfer eines validierten Research-Prod-Pakets nach incoming und den serverseitigen Publish-Pfad mit klaren Gates, optionalem DB-Upsert, Stop-Bedingungen und Report.

## Scope und Nicht-Scope

- Scope: Upload nach `data/incoming/{upload_id}` plus Publish-Gates, Stage, optionaler DB-Upsert, Promote, Health, Smoke, Cleanup, Report.
- Nicht-Scope: lokaler Intake-Reimport, erneute MFA-Ableitung, ungeplanter Direkt-Write in `data/current` oder `data/releases`.

## Serverzustand

- Der aktive Daten-Mount liegt unter `/app/data`.
- Der produktive Stand wird ausschliesslich ueber den Marker `data/current` gesteuert.
- Neue Uploads gehen immer zuerst nach `/srv/webapps_storage/promat/data/incoming/{upload_id}/`.
- Releases liegen unter `/srv/webapps_storage/promat/data/releases/{release_id}/`.
- Direkte Writes in `data/current` oder bestehende Release-Ziele sind nicht zulaessig.

## Incoming Transfer

Bevorzugter Upload:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/upload_prod_package.py --package-dir <local_package_dir> --host vhrz2184 --remote-dir /srv/webapps_storage/promat/data/incoming/<upload_id> --method auto`

Skriptregeln:

- erlaubt nur Remote-Ziele unter `/srv/webapps_storage/promat/data/incoming/`
- kein `--delete`
- kein Upload nach `current`, `releases` oder `production`
- `--method auto|rsync|tar-ssh`; `auto` nimmt `rsync` nur wenn lokal und remote verfuegbar
- Root-Sanity, File-Count und Linux-Checksum-Gate nach jedem Upload
- Session-Sprachordner unter `sessions/` muessen Slugs sein; code-aehnliche Ordner wie `fr` oder `en` sind Fehler

## Incoming Gates

1. Allowlist-Gate auf Paketpfade.
2. Forbidden-Scan auf `*.wav`, `*.TextGrid`, `*.xlsx`, `secure/`, `raw/`, `source/`, `alignment_source/`, `working/`, MFA-Artefakte.
3. JSON-Parse-Gate fuer `manifest.json`, Metadaten, Alignments, Config und optionales DB-Payload.
4. Rohes Linux-Checksum-Gate: `cd /srv/webapps_storage/promat/data/incoming/<upload_id>` und `sha256sum -c checksums.sha256`.
5. Session-Pfadvertrag: nur `sessions/{corpus_slug}/{session_id}/...`.
6. Erwartete Root-Dateien/Ordner: `manifest.json`, `checksums.sha256`, `sessions/`, `config/`, `reports/`, optional `db/import_payload.json`.

Stop-Bedingungen:

- irgendein Gate rot
- fehlende Root-Pflichtobjekte
- ungueltige Session-Sprache

## Publish Commands

Runtime-only Publish ohne DB-Write:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/publish_prod_release.py --upload-id <upload_id> --host vhrz2184 --smoke-base-url <prod-base-url>`

Publish mit Produktions-DB-Upsert:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/publish_prod_release.py --upload-id <upload_id> --host vhrz2184 --smoke-base-url <prod-base-url> --apply-db-upsert`

Dry-run der Remote-Shell, ohne Ausfuehrung:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/publish_prod_release.py --upload-id <upload_id> --host vhrz2184 --smoke-base-url <prod-base-url> --apply-db-upsert --dry-run`

## Stage

1. Kein bestehendes `current`: ersten Release unter `data/releases/{release_id}` vorbereiten.
2. Bestehendes `current`: stage aus `current` plus incoming-Delta erstellen.
3. Keine implizite Deletion by omission.
4. Stage isoliert validieren.

Stop-Bedingungen:

- Stage unvollstaendig
- unbeabsichtigte Loeschung
- Pfadverletzung ausserhalb release/current-Vertrag

## DB Schritt

Default: Runtime-only Publish. Ein vorhandenes `db/import_payload.json` wird ausgeliefert, aber nicht angewendet.

Mit `--apply-db-upsert`:

1. `db/import_payload.json` gegen das staged Release validieren.
2. DB-Upsert-Dry-Run ausfuehren und Counts protokollieren.
3. DB-Upsert transaktional anwenden.
4. Post-Upsert-Validierung ausfuehren.
5. Erst danach atomaren `current`-Switch ausfuehren.

Der DB-Upsert nutzt `scripts/research_data_intake/apply_prod_db_payload.py`, wird per `docker exec -i promat-web-prod python - ...` in der Webcontainer-Umgebung ausgefuehrt und betrifft nur:

- `research_people`
- `research_sessions`
- `research_session_exposures`

Nicht im Payload enthaltene Personen oder Sessions werden nicht geloescht. Exposures werden nur fuer Sessions im Payload anhand `(session_id, sort_order)` eingefuegt, aktualisiert oder entfernt.

Stop-Bedingungen:

- DB-Importpfad unklar
- Payload ungueltig oder sicherheitskritisch
- `--apply-db-upsert` gesetzt, aber `db/import_payload.json` fehlt
- Dry-Run oder Post-Upsert-Validierung rot

## Promote

1. Atomic symlink switch auf neues `data/current`.
2. Verifizieren, dass App-Runtime auf dem erwarteten Root liest.
3. Keine direkten Hot-Writes in Live-Ziele ausserhalb Stage/Current-Switch.

Stop-Bedingungen:

- atomarer Switch nicht garantiert
- Runtime-Root unklar

## Health und Smoke

Pflicht:

- `/health`
- `/ready`
- `/{ui_lang}/research/{corpus}`
- `/{ui_lang}/research/{corpus}/design`

Geschuetzte Routen nur mit sicherem Auth-Verfahren testen; keine Tokens loggen.

## Cleanup

1. Neues incoming nur nach erfolgreichem Promote loeschen.
2. Failed incoming erst nach erfolgreichem neuen Promote bewusst loeschen oder in Quarantine verschieben.
3. Cleanup-Schritt im Report dokumentieren.

## Publish Report

Nach erfolgreichem oder abgebrochenem Lauf immer Report schreiben:

`/srv/webapps_storage/promat/data/publish_logs/promat_publish_<upload_id>_<timestamp>.md`

Mindestinhalt:

- Upload-ID und Pfade
- Gate-Ergebnisse
- Stage/Promote-Status
- DB-Payload vorhanden ja/nein
- DB-Upsert uebersprungen, dry-run oder angewendet
- betroffene Tabellen und Insert-/Update-/Unchanged-/Delete-Counts
- Batch-ID und Sprache aus dem Payload
- verwendeter DB-Upsert-Command
- Post-Upsert-Validierung
- Rollback-Hinweis
- Health/Smoke-Ergebnisse
- Cleanup-Entscheidung
- offene Folgepunkte
