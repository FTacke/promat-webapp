# Runbook: Research Prod DB Payload Upsert

## Zweck

Kontrollierter Ablauf für den optionalen DB-Upsert aus `db/import_payload.json` nach einem bereits erfolgreichen Datei-Publish.

## Grundsatz

- Datei-Publish und DB-Upsert sind getrennte Schritte.
- Ein fehlendes `db/import_payload.json` blockiert den Datei-Publish nicht.
- Ein vorhandenes `db/import_payload.json` wird nur über den freigegebenen Importpfad verarbeitet.

## Inputs

- Upload-ID und Release-Kontext aus dem Publish-Report
- Paketpfad unter `/srv/webapps_storage/promat/data/incoming/{upload_id}/`
- Optional: `db/import_payload.json`

## Gates

1. Verifizieren, dass der Dateipublish erfolgreich war und `current` auf den erwarteten Release zeigt.
2. Prüfen, ob `db/import_payload.json` vorhanden und JSON-valid ist.
3. Sicherstellen, dass keine Secrets oder secure-Inhalte in Logs ausgegeben werden.

## Ablauf

1. Payload aus incoming-Paket lesen.
2. Import ausschließlich mit dem freigegebenen Produktions-Importer ausführen.
3. Import-Ergebnis protokollieren: Anzahl Inserts/Updates, Warnungen, Fehler.
4. Bei Fehlern keine verdeckten Retry-Schleifen; stattdessen klaren Abbruch und Incident-Notiz.

## Stop-Bedingungen

- Importpfad oder Ziel-DB unklar
- Payload ungültig oder schema-inkonsistent
- Sicherheitsverletzung (PII/Secrets im Log)

## Report

`/srv/webapps_storage/promat/data/publish_logs/promat_db_upsert_<upload_id>_<timestamp>.md`

Mindestinhalt:

- Upload-ID
- Payload-Status (vorhanden/fehlend)
- Import-Werkzeug und Zielumgebung
- Ergebnis (insert/update/skip)
- Fehler/Warnungen
- Offene Folgepunkte
