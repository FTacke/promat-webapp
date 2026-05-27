# Runbook: Research Prod Upload and Publish

## Zweck

Wiederholbarer Ablauf für den sicheren Transfer eines validierten Research-Prod-Pakets nach incoming und den serverseitigen Publish-Pfad mit klaren Gates, Stop-Bedingungen und Report.

## Scope und Nicht-Scope

- Scope: Upload nach `data/incoming/{upload_id}` plus Publish-Gates, Stage, Promote, Health, Smoke, Cleanup, Report.
- Nicht-Scope: lokaler Intake-Reimport, erneute MFA-Ableitung, ungeplanter Direkt-Write in `data/current` oder `data/releases`.

## Verifizierter Serverzustand (Stand nach French Promote)

- Der aktive Daten-Mount liegt unter `/app/data`.
- Der produktive Stand wird ausschließlich über den Marker `data/current` gesteuert.
- Neue Uploads gehen immer zuerst nach `/srv/webapps_storage/promat/data/incoming/{upload_id}/`.
- Direkte Writes in `data/current` oder `data/releases` sind nicht zulässig.

## Preflight

1. Paketlokation und Upload-ID bestimmen.
2. Serverpfade prüfen:
- incoming root: `/srv/webapps_storage/promat/data/incoming/`
- releases root: `/srv/webapps_storage/promat/data/releases/`
- current link: `/srv/webapps_storage/promat/data/current`
3. Laufzeitziel prüfen (Container/App): nutzt Runtime aus `/app/data` mit `current`-Marker.
4. Health-Endpoints für spätere Verifikation notieren.
5. Stop-Bedingung: Wenn Pfade unklar sind oder `current`-Ziel nicht eindeutig ist, nicht promoten.

## Incoming Transfer

Primärweg (wenn lokal und remote `rsync` verfügbar):

`rsync -avh --progress <package>/ <ssh_user>@vhrz2184:/srv/webapps_storage/promat/data/incoming/<upload_id>/`

Geprüfter Fallback (wenn lokal oder remote kein `rsync` verfügbar und serverseitig scp/SFTP nicht verfügbar):

1. Lokales Paket als binaeren tar-Stream ueber SSH uebertragen.
2. Remote-Zielverzeichnis vorher anlegen.
3. Remote entpacken mit `tar -xf -`.
4. Danach remote Root-Sanity und Datei-Anzahl pruefen.
5. Danach roh unter Linux pruefen: `sha256sum -c checksums.sha256`.

Wiederholbarer Skriptweg (bevorzugt):

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/upload_prod_package.py --package-dir <local_package_dir> --host vhrz2184 --remote-dir /srv/webapps_storage/promat/data/incoming/<upload_id> --method auto`

Skriptregeln:

- erlaubt nur Remote-Ziele unter `/srv/webapps_storage/promat/data/incoming/`
- kein `--delete`
- kein Upload nach `current`, `releases` oder `production`
- `--method auto|rsync|tar-ssh`; `auto` nimmt `rsync` nur wenn lokal und remote verfügbar
- Root-Sanity, File-Count und Linux-Checksum-Gate nach jedem Upload (kein optionaler Skip)
- Session-Sprachordner unter `sessions/` müssen Slugs sein; code-ähnliche Ordner wie `fr`/`en` werden als Fehler behandelt

## Incoming Gates (vor Stage)

1. Allowlist-Gate auf Paketpfade.
2. Forbidden-Scan auf verbotene Artefaktfamilien (`*.wav`, `*.TextGrid`, `*.xlsx`, `secure/`, `raw/`, `source/`, `alignment_source/`, `working/`, MFA-Artefakte).
3. JSON-Parse-Gate für `manifest.json`, Metadaten, Alignments, Config und optionales DB-Payload.
4. Rohes Linux-Checksum-Gate:
- `cd /srv/webapps_storage/promat/data/incoming/<upload_id>`
- `sha256sum -c checksums.sha256`
5. Session-Pfadvertrag:
- nur `sessions/{corpus_slug}/{session_id}/...`
- explizit kein `sessions/fr/...` oder andere Code-Segmente
6. Erwartete Root-Dateien/Ordner:
- `manifest.json`, `checksums.sha256`, `sessions/`, `config/`, `reports/`
- optional `db/import_payload.json`

Stop-Bedingungen:

- irgendein Gate rot
- fehlende Root-Pflichtobjekte
- ungueltige Session-Sprache

## Stage

1. Kein bestehendes `current`:
- ersten Release unter `data/releases/{release_id}` vorbereiten.
2. Bestehendes `current`:
- stage aus `current` plus incoming-Delta erstellen.
- keine implizite Deletion by omission.
3. Stage isoliert validieren (Dateibaum und erwartete Targets).

Stop-Bedingungen:

- stage unvollstaendig
- unbeabsichtigte Loeschung
- Pfadverletzung ausserhalb release/current-Vertrag

## DB Schritt

1. `db/import_payload.json` vorhanden:
- Import nur ueber freigegebenen, dokumentierten Importpfad/Tool.
2. `db/import_payload.json` fehlt:
- File-Publish darf fortgesetzt werden, wenn alle Dateigates grün sind.
- DB-Upsert ist dann ein separater dokumentierter Folgeprozess.
3. Kein Dummy-Payload und keine secure/PII-Leaks in Logs.

Stop-Bedingungen:

- DB-Importpfad unklar
- Payload ungueltig oder sicherheitskritisch

## Promote

1. Atomic symlink switch auf neues `data/current`.
2. Verifizieren, dass App-Runtime auf dem erwarteten Root liest (`/app/data` vs `/app/data/current`).
3. Keine direkten Hot-Writes in Live-Ziele ausserhalb Stage/Current-Switch.

Stop-Bedingungen:

- atomarer Switch nicht garantiert
- Runtime-Root unklar

## Health und Smoke

1. Health/Ready pruefen.
2. French Smoke pruefen:
- `/de/research/french`
- `/de/research/french/design`
3. Geschuetzte Routen nur mit sicherem Auth-Verfahren testen; keine Tokens loggen.

Stop-Bedingungen:

- Health nicht gruen
- Kernrouten regressiv

## Cleanup

1. Neues incoming nur nach erfolgreichem Promote loeschen.
2. Altes failed incoming erst nach erfolgreichem neuen Promote bewusst loeschen oder in Quarantine verschieben.
3. Cleanup-Schritt im Report dokumentieren.

## Publish Report

Nach erfolgreichem oder abgebrochenem Lauf immer Report schreiben:

`/srv/webapps_storage/promat/data/publish_logs/promat_publish_<upload_id>_<timestamp>.md`

Mindestinhalt:

- Upload-ID und Pfade
- Gate-Ergebnisse
- Stage/Promote-Status
- DB-Import-Status
- Health/Smoke-Ergebnisse
- Cleanup-Entscheidung
- offene Folgepunkte

## Referenzlauf French Promote

- Upload-ID: `french_batch_20260527_initial_fix01`
- Incoming-Pfad: `/srv/webapps_storage/promat/data/incoming/french_batch_20260527_initial_fix01/`
- Linux-Checksum-Gate: `sha256sum -c checksums.sha256` erfolgreich
- Release-Promote: durchgeführt; `current` zeigt auf den neuen Release-Stand
- DB-Payload: vorhanden, aber DB-Workflow bleibt weiterhin eigener kontrollierter Schritt
