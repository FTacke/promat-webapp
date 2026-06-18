# English Batch Prod Export

Datum: 2026-06-18

## Ziel

Den frisch importierten `english_batch_20260618` als Prod-Upload-Paket exportieren, nach `vhrz2184` uebertragen und in der Live-App ueber den `data/current`-Release-Pfad sichtbar machen.

## Consulted Sources

- `docs/runbooks/research-prod-upload-and-publish.md`
- `docs/runbooks/research-prod-db-payload-upsert.md`
- `scripts/research_data_intake/README.md`
- `scripts/research_data_intake/build_prod_upload_package.py`
- `scripts/research_data_intake/upload_prod_package.py`

## Geaenderte Bereiche

- Lokales Paket: `scripts/research_data_intake/exports/english_batch_20260618_runtime/`
- Remote incoming: `/srv/webapps_storage/promat/data/incoming/english_batch_20260618_runtime/`
- Remote release: `/srv/webapps_storage/promat/data/releases/release_20260618T130056Z_english_batch_20260618_runtime/`
- Remote current symlink: `/srv/webapps_storage/promat/data/current`

## Wichtige Entscheidungen

- Paket enthaelt die englischen Runtime-Sessions `EN-L-0001-2026-S01` bis `EN-L-0010-2026-S01`, Research-Player-Config und den DB-Payload aus `C:/dev/promat_data_archive/batches/english_batch_20260618/import_payload.json`.
- Stage/Promote folgte dem letzten erfolgreichen Prod-Run: `current` in einen neuen Release kopieren, incoming ohne Delete darueberlegen, dann atomarer `current`-Switch.
- DB-Upsert wurde wie im letzten Publish-Run bewusst nicht ausgefuehrt, weil kein freigegebener Produktions-DB-Importer-Entrypoint im Publish-Scope vorliegt.

## Abweichungen

- Keine Abweichung vom Datei-Publish-Vertrag. Upload erfolgte nur nach `incoming`, Live-Schaltung nur ueber neuen Release und `current`-Switch.

## Verifikation

- Lokales Paket gebaut mit `build_prod_upload_package.py`.
- Lokaler Package-Validator: `[ok] validation passed`.
- Remote Upload mit `upload_prod_package.py --method auto`; tatsaechliche Strategie `tar-over-ssh`.
- Remote file count: 1438.
- Remote checksum gate: ok.
- Remote forbidden scan: passed.
- Remote JSON parse gate: 51 JSON-Dateien parsed.
- Remote session path contract: `sessions/english`.
- Host health/ready: 200/200.
- Public health/ready: 200/200.
- Public smoke `/de/research/english`: 200.
- Public smoke `/de/research/english/design`: 200.
- Remote Publish-Log: `/srv/webapps_storage/promat/data/publish_logs/promat_publish_english_batch_20260618_runtime_20260618T130056Z.md`.

## Offene Punkte

- `db/import_payload.json` ist im Release vorhanden, aber der Produktions-DB-Upsert wurde nicht ausgefuehrt.

## Naechste sinnvolle Schritte

- Falls die produktiven PostgreSQL-Metadaten aktualisiert werden sollen, den separaten freigegebenen DB-Upsert-Pfad nachziehen.
