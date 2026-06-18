# Runbook: Research Prod Upload and Publish

## Zweck

Wiederholbarer Ablauf fuer den sicheren Transfer eines validierten Research-Prod-Pakets nach incoming und den serverseitigen Publish-Pfad mit klaren Gates, optionalem DB-Upsert, Stop-Bedingungen und Report.

## Scope und Nicht-Scope

- Scope: Upload nach `data/incoming/{upload_id}` plus Publish-Gates, Stage, optionaler DB-Upsert, Promote, Health, Smoke, Cleanup, Report.
- Nicht-Scope: lokaler Intake-Reimport, erneute MFA-Ableitung, ungeplanter Direkt-Write in `data/current` oder `data/releases`.

## Serverzustand

- Der aktive Daten-Mount liegt unter `/app/data`.
- Der aktive Daten-Mount liegt unter `/app/data`; `get_sessions_root()` liest aus dem flachen `data/sessions/`-Baum, nicht ueber `current/`.
- Der `data/current`-Marker ist ein relativer Symlink auf den jeweils aktuellen Release und dient als Rollback-Referenz sowie als Eingabepfad fuer den DB-Upsert-Schritt.
- Neue Uploads gehen immer zuerst nach `/srv/webapps_storage/promat/data/incoming/{upload_id}/`.
- Releases liegen unter `/srv/webapps_storage/promat/data/releases/{release_id}/`.
- Nach dem Promote rsync das Publish-Skript jeden Corpus aus dem neuen Release in `data/sessions/{corpus_slug}/` und startet den App-Container neu.
- Direkte Writes in `data/current` oder bestehende Release-Ziele ausserhalb des gesteuerten Publish-Ablaufs sind nicht zulaessig.

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

Der DB-Upsert nutzt `/app/scripts/research_data_intake/apply_prod_db_payload.py` aus dem deployten Webcontainer-Image, wird per `docker exec promat-web-prod python ...` in der Webcontainer-Umgebung ausgefuehrt und betrifft nur:

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

1. Atomarer relativer Symlink-Switch auf neues `data/current` (relativer Pfad `releases/{release_id}`, kein absoluter Host-Pfad).
2. Rsync jedes Corpus aus dem neuen Release in den flachen App-Leseordner `data/sessions/{corpus_slug}/` (altes Corpus-Verzeichnis wird zuerst entfernt).
3. App-Container (`promat-web-prod`) neu starten, damit `@lru_cache`-gebundene Session-Loader den neuen Stand uebernehmen.
4. Keine direkten Hot-Writes in Live-Ziele ausserhalb dieses gesteuerten Ablaufs.

Das Publish-Skript uebernimmt Schritte 1-3 automatisch. Mit `--no-restart-container` kann der Neustart uebersprungen werden, was aber nur fuer Dev-Debugging geeignet ist.

Stop-Bedingungen:

- atomarer Switch nicht garantiert
- Rsync fehlgeschlagen oder Corpus-Verzeichnis nach dem Sync nicht vorhanden
- Container-Neustart fehlgeschlagen und Health-Check rot

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

## Cleanup: Metadata-only Sessions (DB + Runtime)

Sessions, fuer die nur XLSX-Workbook-Zeilen ohne Audio-/Task-Artefakte vorhanden sind, sollen weder in der Runtime noch in der Produktions-DB erscheinen. Falls solche Sessions durch einen frueheren Import in der DB oder im Runtime-Baum vorhanden sind, muessen sie explizit bereinigt werden.

### Schritt 1: Dry-run (immer zuerst)

```bash
ssh vhrz2184 "docker exec -e PROMAT_APP_SRC=/app/src promat-web-prod \
  python /tmp/apply_prod_db_payload_new.py \
  --cleanup-metadata-only \
  --target-language fr \
  --release-dir /app/data"
```

Das Dry-run-Ergebnis benennt `sessions_to_delete`, `persons_to_delete` und `exposures_to_delete`. Nur wenn die Liste plausibel ist und explizit freigegeben wird, weiter.

### Schritt 2: Apply (nur nach bestaetigtem Dry-run)

```bash
ssh vhrz2184 "docker exec -e PROMAT_APP_SRC=/app/src promat-web-prod \
  python /tmp/apply_prod_db_payload_new.py \
  --cleanup-metadata-only \
  --target-language fr \
  --release-dir /app/data \
  --apply-cleanup"
```

### Schritt 3: Runtime-Ordner entfernen

Nur explizit benannte Ordner loeschen – kein Glob-Delete, kein `--delete`:

```bash
ssh vhrz2184 "set -euo pipefail
for s in <SESSION_ID_1> <SESSION_ID_2>; do
  rm -rf \"/srv/webapps_storage/promat/data/sessions/french/\${s}\"
done"
```

### Schritt 4: Container-Restart + Verifikation

```bash
ssh vhrz2184 "docker restart promat-web-prod && sleep 15"
curl -fsS -o /dev/null -w '%{http_code}\n' https://<prod-base-url>/health
curl -fsS -o /dev/null -w '%{http_code}\n' https://<prod-base-url>/ready
```

### Regeln

- Cleanup immer nur fuer explizit angegebenen `--target-language`-Corpus.
- Kein globaler Delete.
- Keine Backups oder Snapshots anlegen.
- Personen nur loeschen, wenn alle ihre Sessions metadata-only sind.
- Loeschen transaktional in einer einzigen DB-Transaktion.
- Andere Sprachen (en, es, de) werden nicht beruehrt.

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
- Sessions-Sync-Status (`sessions_sync_status`)
- Container-Restart-Status (`container_restart_status`)
- Health/Smoke-Ergebnisse
- Cleanup-Entscheidung
- offene Folgepunkte

Der generierte Markdown-Report darf JSON-Blöcke in einem Bash-Heredoc nicht mit Backtick-Fences schreiben, weil unquoted heredocs Backticks als Command Substitution behandeln. Für eingebettete JSON-Ausgaben werden deshalb Tilde-Fences wie `~~~json` verwendet.
