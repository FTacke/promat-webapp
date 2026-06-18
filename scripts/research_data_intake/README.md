# Research Data Intake Scripts

## Zweck

Dieser Bereich bündelt die lokale Research-Intake-, Ableitungs-, Archiv- und Upload-Paket-Pipeline für PROMAT.

Teaching gehört nicht zu dieser Pipeline. `content/`, `public/teaching/` und Teaching-Media bleiben bei Research-Intake-Runs unangetastet.

## Zielmodell

- Batch-Eingänge liegen unter `scripts/research_data_intake/import/{batch_name}/`.
- Der Batch ist ein Drop-in-Verzeichnis ohne manuelle Unterordnerpflicht.
- Der Scanner klassifiziert Workbook, WAV, TextGrid und JSON strikt aus Dateinamen.
- Batch-lokales `working/` bleibt eine Zwischenstruktur nur für Vorbereitung und MFA-Schritte.
- `data/sessions/` ist Runtime-only und enthält nur finale JSON/MP3-Artefakte.
- Das lokale Langzeitarchiv liegt außerhalb des Repo-Workspaces unter `PROMAT_LOCAL_ARCHIVE_ROOT`, standardmäßig lokal zum Beispiel `C:\dev\promat_data_archive`.
- Das Archiv ist session-zentriert unter `sessions/{language_code}/{session_id}/...`.
- Prod-Uploads entstehen als explizite Allowlist-Pakete unter `scripts/research_data_intake/exports/{upload_id}/` aus bereits validierten Runtime-Artefakten und optionalem `db/import_payload.json`.
- In Prod-Upload-Paketen liegen Runtime-Sessions immer unter `sessions/{corpus_slug}/{session_id}/` (z. B. `sessions/french/...`), nicht unter Sprachcodes wie `sessions/fr/...`.
- Der lokale Runtime-Pfad bleibt `data/sessions/{corpus_slug}/{session_id}/...`; das Prod-Paket spiegelt denselben Slug unter `sessions/{corpus_slug}/{session_id}/...`.

## Batch-Scan und Klassifizierung

- Batch-Ordnernamen müssen `batch` enthalten.
- Dateien dürfen direkt im Batch oder in optionalen Hilfsunterordnern liegen.
- Es gibt keine Pflicht mehr für `processed/`, `raw/`, `source/` oder `intake_data/`.
- Die Klassifizierung muss aus expliziten Dateinamen kommen: `person_id`, Task, Rolle und Dateityp.
- Mehrdeutigkeit, Konflikte oder nicht erkennbare Dateien werden reportet; die Pipeline rät nicht.

Unterstützte Batch-Rollen:

- `raw`: echte unbearbeitete WAV-Master
- `source`: operative Analyse-/Ableitungs-WAVs, auch aus `*_processed.wav`
- `alignment_source`: TextGrids, Amberscript-JSON, andere alignment-nahe JSON-Quellen
- Workbook: `*.xlsx`

## Working-Tree

Batch-lokale Zielstruktur:

- `working/.intake_state.json`
- `working/{person_id}/wordlist/source/wordlist.wav`
- `working/{person_id}/wordlist/alignment/wordlist.TextGrid`
- `working/{person_id}/text/source/text.wav`
- `working/{person_id}/text/alignment/text.TextGrid`
- `working/{person_id}/text/alignment/text.json`
- `working/{person_id}/text/mfa_corpus/`
- `working/{person_id}/text/mfa_output/`
- `working/{person_id}/text/mfa_manifest.json`
- `working/{person_id}/text/mfa_state.json`
- `working/{person_id}/interview/source/interview.wav`
- `working/{person_id}/interview/alignment/interview.json`

Regeln:

- `working/` ist nur Vorbereitung und nie Runtime oder Prod-Ziel.
- Der Organizer arbeitet inkrementell pro `person_id` und Task.
- Für `wordlist` und `text` braucht der Organizer klassifizierte `source`-WAVs plus alignment source TextGrid.
- Für `interview` braucht der Organizer eine klassifizierte `source`-WAV plus eine klassifizierte alignment-source JSON-Datei.
- Die Text-MFA schreibt zusätzlich eine task-lokale `mfa_state.json`, damit unveränderte Inputs die aktuelle Textausgabe wiederverwenden können, statt MFA erneut auszuführen.
- MFA-Executable-Auflösung folgt überall demselben Vertrag: CLI `--mfa-executable` > `PROMAT_MFA_EXECUTABLE` > `docker`.
- Docker-backed Text-MFA mountet `MFA_ROOT_DIR=/mfa` aus einem gemeinsamen Sprachcache unter `scripts/research_data_intake/.mfa_cache/shared/{language_code}/`, zum Beispiel `shared/en/`, `shared/fr/`, `shared/es/` oder `shared/de/`.
- Die MFA-Modell-Downloads sind von `mfa align` getrennt: vorhandene `pretrained_models/acoustic/*.zip` und `pretrained_models/dictionary/*.dict` werden wiederverwendet, fehlende Modelle werden einmalig in den Shared Cache geladen.
- `raw` kann als Fallback genutzt werden wenn kein `source`-WAV vorhanden ist; das Archiv dokumentiert dies in `task_audio_roles`.
- Native Speaker mit `-N-` bleiben für `interview` neutral `not_expected_for_native_speaker`.

## Runtime-Vertrag

`data/sessions/{language}/{session_id}/` darf nur enthalten:

- `metadata.json`
- `alignment/{task}.json`
- `derived/{task}.mp3`
- `items/{task}/{item_id}.mp3`

Nie in Runtime:

- `*.wav`
- `*.TextGrid`
- `*.xlsx`
- `secure/`
- `raw/`
- `source/`
- `alignment_source/`
- `working/`
- `mfa_corpus/`
- `mfa_output/`

## Lokales Archiv

Session-zentrierte Struktur außerhalb des Repo-Workspaces:

```text
PROMAT_LOCAL_ARCHIVE_ROOT/
  sessions/
    es/
      ES-L-0001-2026-S01/
        secure/
        raw/
        source/
        alignment_source/
        runtime/
        metadata/archive_manifest.json
        reports/
```

Regeln:

- `secure/` ist lokal-only und nie Runtime oder Prod.
- `runtime/` spiegelt die final erzeugten Runtime-Artefakte.
- `archive_manifest.json` enthält Session-ID, Person-ID, Sprache, Source-Batch, Zeitstempel, Importer-Version, Input-/Output-Dateien mit Checksums, Warnungen und fehlende oder optionale Artefakte.
- Das Archiv darf im normalen Importlauf beschrieben werden, aber nicht implizit durch Dev-Reset gelöscht werden.

## Prod-Upload-Paket

Beispielstruktur:

```text
scripts/research_data_intake/exports/{upload_id}/
  sessions/
  db/import_payload.json
  config/research_player/
  manifest.json
  checksums.sha256
  reports/
```

Erlaubt:

- `sessions/.../metadata.json`
- `sessions/.../alignment/*.json`
- `sessions/.../derived/*.mp3`
- `sessions/.../items/**/*.mp3`
- `sessions/{corpus_slug}/...` verwendet denselben Corpus-Slug wie die Runtime (`spanish`, `german`, `french`, `english`).
- `db/import_payload.json`
- `config/research_player/**/*.json` nur wenn explizit runtime-relevant
- `manifest.json`
- `checksums.sha256`
- `reports/*.md|*.txt|*.json`

Checksum-Vertrag:

- Datei-Encoding: UTF-8
- Zeilenenden: LF-only
- Zeilenformat: `<sha256><two spaces><relative-posix-path>`
- Linux-Gate: `sha256sum -c checksums.sha256`

DB-Payload-Regel:

- Wenn ein reales Import-Payload verfuegbar ist, wird es als `db/import_payload.json` ins Paket aufgenommen.
- Ohne explizites Publish-Flag wird `db/import_payload.json` nur ausgeliefert, aber nicht in die Produktionsdatenbank geschrieben.
- Der Produktions-DB-Upsert laeuft nur mit `--apply-db-upsert`, validiert vorher das staged Release, fuehrt einen Dry-Run aus und schreibt danach transaktional.
- Der Upsert betrifft `research_people`, `research_sessions` und `research_session_exposures`; nicht im Payload enthaltene Personen oder Sessions werden nicht geloescht.
- Kein Dummy-Payload.
- Keine Secure- oder direkt personenbezogenen Felder in Upload-Payloads.

Validator-Regel:

- `validate_research_intake.py prod-package` nimmt die Server-Gates lokal vorweg: Allowlist, Manifest-Dateiliste, Slug-Sessionpfade, Checksum-Format, LF-only, UTF-8 und Dateihashes.

Verboten:

- `*.wav`
- `*.TextGrid`
- `*.xlsx`
- `secure/`
- `raw/`
- `source/`
- `alignment_source/`
- `working/`
- `mfa_corpus/`
- `mfa_output/`
- Consent-/Questionnaire-PDFs
- temporäre Dateien

## Commands

Drop-in-Batch scannen:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/scan_import_batch.py --batch-dir spanish_batch_20260421`

JSON-Dry-Run-Report für den Scan:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/scan_import_batch.py --batch-dir spanish_batch_20260421 --json`

Batch in den Working-Tree organisieren:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421`

Zentralen lokalen Import nach Runtime, Dev-DB und Archiv dry-run planen:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --sync-tasks --dry-run`

Kontrollierten lokalen Import ausführen:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --sync-tasks`

Einzelnen Docker-MFA-Personenlauf testen:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/run_text_mfa.py --batch-dir english_batch_20260618 --person-id EN-L-0001 --language en --mfa-executable docker --dry-run`

Shared MFA-Modellcache bei Bedarf manuell leeren:

`Remove-Item -Recurse -Force scripts/research_data_intake/.mfa_cache/shared/en`

Runtime-Session validieren:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/validate_research_intake.py runtime-tree --session-dir C:/dev/promat/data/sessions/spanish/ES-L-0001-2026-S01`

Archiv-Session validieren:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/validate_research_intake.py archive-tree --archive-session-dir C:/dev/promat_data_archive/sessions/es/ES-L-0001-2026-S01`

Prod-Upload-Paket bauen:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/build_prod_upload_package.py --language spanish --session-id ES-L-0001-2026-S01 --db-payload C:/dev/promat_data_archive/batches/spanish_batch_20260421/import_payload.json`

Initiales Prod-Upload-Paket fuer alle vorhandenen Runtime-Sessions plus Research-Player-Config bauen:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/build_prod_upload_package.py --all-runtime-sessions --include-research-player-config --db-payload C:/dev/promat_data_archive/batches/french_batch_20260527/import_payload.json --upload-id promat_upload_YYYYMMDDTHHMMSSZ_initial_runtime`

Prod-Upload-Paket validieren:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/validate_research_intake.py prod-package --package-dir C:/dev/promat/scripts/research_data_intake/exports/promat_upload_20260525T120000Z`

Prod-Upload-Paket nach incoming übertragen (`auto`: rsync nur wenn lokal und remote verfügbar, sonst tar-over-SSH):

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/upload_prod_package.py --package-dir C:/dev/promat/scripts/research_data_intake/exports/french_batch_20260527_initial_fix01 --host vhrz2184 --remote-dir /srv/webapps_storage/promat/data/incoming/french_batch_20260527_initial_fix01 --method auto`

Runtime-only Publish ohne DB-Write:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/publish_prod_release.py --upload-id french_batch_20260527_initial_fix01 --host vhrz2184 --smoke-base-url <prod-base-url>`

Publish mit Produktions-DB-Upsert aus `db/import_payload.json`:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/publish_prod_release.py --upload-id french_batch_20260527_initial_fix01 --host vhrz2184 --smoke-base-url <prod-base-url> --apply-db-upsert`

Serverseitigen DB-Payload-Upsert gegen ein staged Release nur pruefen:

`docker exec -i promat-web-prod python - --release-dir /app/data/releases/<release_id> --payload /app/data/releases/<release_id>/db/import_payload.json < /srv/webapps/promat/app/scripts/research_data_intake/apply_prod_db_payload.py`

Expliziten Dev-Research-File-Reset nur dry-run anzeigen:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/reset_dev_research_runtime.py`

Expliziten Dev-Research-File-Reset ausführen:

`c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/reset_dev_research_runtime.py --yes`

## Wichtige Trennungen

- Research Intake ist nicht Teaching Import.
- `content/` bleibt bei Research-Intake unangetastet.
- `public/teaching/` und Teaching-Media bleiben unangetastet.
- `data/config/research_player/` ist kanonische Runtime-Konfiguration und keine wegzuwerfende Batch-Altlast.
- Der File-Cleanup-Stand vom 2026-05-25 bleibt gültig; ein Dev-Postgres-Reset ist ein separater expliziter Schritt und kein Nebeneffekt des Imports.
- Prod wird nicht direkt aus `data/sessions` per rsync befüllt, sondern nur über explizite Upload-Pakete.
