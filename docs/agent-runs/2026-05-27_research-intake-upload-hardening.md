# 2026-05-27 Research Intake Upload Hardening

## Ausgangslage

- Erstes Paket `french_batch_20260527_initial` scheiterte im serverseitigen Publish-Gate.
- Korrigiertes Paket `french_batch_20260527_initial_fix01` wurde lokal gebaut und validiert.
- Upload nach incoming unter neuer ID wurde abgeschlossen; alter fehlgeschlagener incoming-Baum blieb unveraendert.

## Erster failed server publish

Gesicherte Gate-Fehler:

1. `checksums.sha256` mit CRLF, dadurch Linux-`sha256sum -c` Fehler.
2. Sessionpfade als `sessions/fr/...` statt `sessions/french/...`.
3. Fehlendes `db/import_payload.json` im ersten Paket.

## Fix-Run Status

- Upload-ID: `french_batch_20260527_initial_fix01`
- Lokaler Package-Validator: gruen
- Remote incoming: `/srv/webapps_storage/promat/data/incoming/french_batch_20260527_initial_fix01/`
- Remote file count: `4416`
- Remote root: `manifest.json`, `checksums.sha256`, `sessions/`, `config/`, `db/`, `reports/`
- Remote session dirs: `english`, `french`, `spanish`
- Remote `db/import_payload.json`: vorhanden
- Remote Linux checksum gate: `sha256sum -c checksums.sha256` mit `rc:0`

## Ursachenanalyse Text-Import

### Gesichert durch Log/State/Git-Diff

1. Vorherige gruene Teillaeufe fuer FR-L-0001..0003 basierten auf Reuse eines bereits vorhandenen, gueltigen Text-MFA-Working-States.
2. Der Haker im French-Textlauf trat auf, als Signaturvergleich fuer denselben Dateiinhalt an Windows-Pfadschreibweisen (`C:\...` vs `c:\...`) scheiterte.
3. Ohne passendes `alignment/text.json` wurde `text` als unvollstaendig/prepare-notwendig behandelt, waehrend `wordlist` weiter synchronisiert werden konnte.
4. Der Importpfad wurde gehaertet durch:
- path-case-insensitive Signaturnormalisierung
- Fallback von strict import (`fail_on_missing_output=True`) auf warnenden Import (`False`) bei fehlenden Einzel-TextGrids
5. `silent1` wurde als non-spoken Label in TextGrid-Parsing explizit behandelt.
6. French Katalogkorrektur bei `t_42` reduzierte Katalog-vs-Spoken-Inkonsistenzen fuer den Textpfad.
7. Docker-MFA war relevant als expliziter Fallback, wenn Host-`mfa` nicht verfuegbar war.

### Plausible Zusatzfaktoren

1. Fruehere "vollautomatisch gruen"-Wahrnehmung entstand teilweise durch gueltige Vorzustands-Artefakte im Working-Tree, nicht zwingend durch einen komplett frischen End-to-End-Lauf.
2. Einzelne fehlende MFA-TextGrid-Outputs fuer bestimmte Items konnten vorher den strikten Import abbrechen und wurden erst mit Fallback robust abgefangen.

### Offen oder nicht belegbar

1. Exakte Reihenfolge aller manuellen Zwischenkommandos ausserhalb der protokollierten Runs ist nicht vollstaendig rekonstruiert.
2. Ob jeder fruehere Lauf auf identischer Toolchain/Host-Konfiguration lief, ist nicht lueckenlos belegt.

### Kurzdiagnose

- Vorherige gruene Laeufe waren gruen, weil ein gueltiger Working-/MFA-State bereits vorhanden und wiederverwendbar war.
- Dieser Lauf hakte, weil stale Signaturabgleich unter Windows-Pfadvarianten und itemweise fehlende MFA-Outputs den Textpfad blockieren konnten.
- Wiederholung wird verhindert durch Signaturnormalisierung, task-lokale stale-Erkennung, Docker-Fallback und warnenden Import-Fallback.

## Dokumentationsaenderungen

- Spec gehaertet: `docs/spec/platform-data-files.md`
- Intake-Runbook erweitert: `docs/runbooks/research-intake-working-pipeline.md`
- Neues Upload/Publish-Runbook: `docs/runbooks/research-prod-upload-and-publish.md`
- Intake README erweitert: `scripts/research_data_intake/README.md`

## Tests

Ausgefuehrt:

- `pytest app/tests/test_research_intake_storage.py -q`
- `pytest app/tests/test_research_production_importer.py -q`
- `pytest app/tests/test_research_presets.py -q`

Ergaenzt:

- stale-state Guard fuer Text-Preparation
- Windows-Path-Normalisierung fuer Signaturvergleich
- cached strict->warning Import-Fallback
- MFA-Subprocess-Encoding (`utf-8`, `errors=replace`)

## Transferpfad

- Primaer dokumentiert: rsync
- Gepruefter Fallback dokumentiert: binary-safe tar-over-SSH
- Wiederholbares Script bereitgestellt: `scripts/research_data_intake/upload_prod_package.py`

## Server-Publish Folgepunkt

Siehe Runbook `docs/runbooks/research-prod-upload-and-publish.md`.

Offen:

1. serverseitiger Publish fuer `french_batch_20260527_initial_fix01`
2. altes failed incoming nach erfolgreichem neuem Promote bewusst bereinigen oder quarantainen
