# Runbook: Backup und Restore

## Zugehörige Spezifikation

- `docs/spec/platform-data-files.md` (Abschnitte „Release Gate and Deployment“, `data/`, „Local Archive Filesystem“)

## Zweck

Ein verifiziertes PostgreSQL-Backup, ein Restore mit Gegenprobe und die Festlegung, welche Dateibestände gesichert werden müssen. Das ist bewusst nur das Fundament; die Aufbewahrungs- und Langzeitarchivierungspolitik gehört in den späteren „Storage & Preservation“-Lauf (siehe unten).

## Was gesichert werden muss

| Bestand | Ort | Ersetzbar? | Sicherung |
|---|---|---|---|
| PostgreSQL (Konten, Zugangsanfragen, Research-Sets, `research_*`-Metadaten, Analytics-Aggregate) | Docker-Volume `promat_postgres_prod` | nein | `scripts/backup_prod_db.sh` (dieses Runbook) |
| Operatoreigene Research-Konfiguration | Server: `/srv/webapps_storage/promat/data/config/research_player/`; lokal: `data/config/research_player/` | nein (Katalog-/Player-Inhalt, nicht im Git) | Dateikopie beider Orte; nach jeder Änderung |
| Geheimnisse | `/srv/webapps/promat/config/passwords.env` | nein | getrennt und verschlüsselt ablegen, **nie** zusammen mit DB-Dumps |
| Lokales Quellarchiv | `PROMAT_LOCAL_ARCHIVE_ROOT` (Beispiel `C:\dev\promat_data_archive`): `sessions/{code}/{session_id}/{secure,raw,source,alignment_source,runtime,metadata,reports}` und `batches/{batch}/` | **nein** (Original-WAVs, Einwilligungs-PDFs) | komplette Archivwurzel kopieren, mindestens eine Kopie außerhalb der Arbeitsmaschine; verifizierte institutionelle Kopie siehe `archive-preservation.md` |
| Intake-Workbooks und Batch-Eingänge | `scripts/research_data_intake/import/{batch}/` (XLSX, TextGrids, Amberscript-JSON) | teilweise (Originale liegen im Archiv, Workbook-Stand nicht) | Workbooks sichern, solange sie nicht im Archiv liegen |
| Abgeleitete Runtime-Dateien | Server `data/sessions/`, `data/releases/`, `data/current` | ja (aus Archiv und Katalogen via Intake) | kein eigenes Backup nötig; der Server hält einen Vorrelease (siehe Publish-Runbook) |
| Redis (Rate-Limit-Zähler) | Volume `promat_redis_prod` | ja | nicht sichern |

Nicht in dieses Backup gehören: `working/`, `.mfa_cache/`, `exports/`, lokale Dev-Datenbank.

## Voraussetzungen

- Ausführung auf dem Produktionsserver im Deploy-Checkout (`/srv/webapps/promat/app`) durch einen Benutzer mit Docker-Zugriff
- Der Datenbank-Container `promat-db-prod` läuft
- Zielordner mit ausreichend Platz; Standard `/srv/webapps_storage/promat/backups/postgres` (anderer Ort über `PROMAT_BACKUP_DIR` oder `--output-dir`)
- Das Skript liest kein Passwort und keine `passwords.env`: `pg_dump` läuft im Container

## Schritte: Backup erstellen

1. `cd /srv/webapps/promat/app && scripts/backup_prod_db.sh`
2. Optionen: `--output-dir DIR`, `--container NAME`, `--keep N` (Standard 14; `0` schaltet das Aufräumen ab)
3. Ergebnis im Zielordner (Modus 600, Ordner 700): `promat_db_<UTC>.dump`, `.sha256` (Prüfsumme) und `.counts.tsv` (exakte Zeilenzahl je Tabelle direkt nach dem Dump)
4. Das Skript beendet sich nur bei Erfolg mit `OK`; jeder Fehler gibt einen Exit-Code ungleich 0 aus und hinterlässt keine halbe Datei unter dem Endnamen

Zeitplan (Beispiel, vom Operator einzurichten; Fehlermeldungen gehen per `MAILTO` an den Operator):

```cron
MAILTO=<operator-mail>
15 2 * * * cd /srv/webapps/promat/app && scripts/backup_prod_db.sh >> /srv/webapps/promat/logs/backup.log 2>&1
```

Vor einem Deployment mit neuen SQL-Migrationen zusätzlich ein manuelles Backup erstellen. Ein Backup, das nur auf dem Produktionsserver liegt, schützt nicht vor Verlust des Servers: Dump, `.sha256` und `.counts.tsv` zusätzlich an einen vom Operator gewählten Ort außerhalb des Servers kopieren (zulässig nur für Speicher, der personenbezogene Daten aufnehmen darf).

## Schritte: Restore üben und prüfen (ungefährlich)

1. `scripts/verify_db_restore.sh --dump /srv/webapps_storage/promat/backups/postgres/promat_db_<UTC>.dump`
2. Das Skript startet einen Wegwerf-Container (`postgres:15`, kein veröffentlichter Port, Zufallspasswort, Daten im RAM), prüft die Prüfsumme, stellt wieder her, vergleicht die Tabellenzeilen mit `.counts.tsv` und entfernt den Container.
3. Exit-Codes: `0` verifiziert; `3` Restore funktioniert, aber Zeilenzahlen weichen ab (zwischen Dump und Zählung können Schreibvorgänge liegen; erneut sichern und prüfen); `1` Fehler.
4. Dieselbe Rehearsal läuft in CI gegen echte Migrationen (`scripts/ci_backup_restore_smoke.sh`). Auf dem Server mindestens monatlich ein echtes Backup so prüfen.

## Schritte: Restore in Produktion (DESTRUKTIV)

Nur bei Datenverlust oder fehlerhafter Migration. `--clean` löscht vorhandene Daten der wiederhergestellten Tabellen.

1. Entscheiden, welches Backup gilt; Prüfsumme und Wegwerf-Restore (`verify_db_restore.sh`) vorher durchführen.
2. **Frisches Backup des jetzigen Zustands erstellen** (auch wenn er defekt ist).
3. Web stoppen: `docker stop promat-web-prod`
4. `scripts/restore_db_dump.sh --dump <dump> --container promat-db-prod --allow-production --clean` und den Datenbanknamen als Bestätigung eintippen
5. Zeilenzahlen gegen `.counts.tsv` prüfen (zum Beispiel mit `scripts/verify_db_restore.sh`-Ausgabe oder `psql`-Zählung)
6. Web starten: `docker start promat-web-prod`; dann `curl -fsS http://127.0.0.1:8000/health` und `/ready`
7. Anmelden und eine geschützte Research-Seite öffnen

Ohne `--clean` bricht der Restore beim ersten bereits vorhandenen Objekt ab (`--exit-on-error`); das ist der sichere Standard für Wegwerf-Datenbanken.

## Verifikation

- Backup: `OK`, Dump und Sidecars vorhanden, `sha256sum -c promat_db_<UTC>.dump.sha256` im Zielordner grün
- Restore-Probe: `RESTORE VERIFIED`
- Nach Produktionsrestore: `/health` und `/ready` liefern 200, Login funktioniert

## Risiken und Rückbau

- Dumps enthalten Konten, Passwort-Hashes und Zugangsanfragen: Ordner 700, Dateien 600, nur auf Speicher ablegen, der das darf.
- Ein Restore ersetzt Daten, die nach dem Backup entstanden sind (neue Konten, Sets, Zugangsanfragen).
- Der Dump ist ein logisches Backup derselben Postgres-Hauptversion (15). Bei einem Major-Upgrade Restore auf der Zielversion neu üben.

## Offen für den späteren „Storage & Preservation“-Lauf

- Aufbewahrungsfristen und Rotation außerhalb des Servers, Verschlüsselung, Ort der Zweitkopie
- Prüfsummen-Nachprüfung (Fixity) des Quellarchivs nach Zeitplan
- Trennung Original/kanonisch/abgeleitet, versionierte wissenschaftliche Releases, DOI-Exporte
- Versionierung der Research-Kataloge (heute nur Dateikopien)
- Regelmäßige Restore-Übungen und Zuständigkeit
