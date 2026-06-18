# 2026-06-18 French-Batch-Publish: Live-App-Diskrepanz Diagnose und Fix

## Ausgangssituation

Nach erfolgreich gemeldeten Smoke-Checks des French-Batch-Publish (`french_batch_20260618_runtime`, Release `release_20260618T143628Z_french_batch_20260618_runtime`) zeigte die Live-App weiterhin alte French-Daten (28 Sessions, kein Interview-Task, FR-L-0027/0028/0029 fehlend).

DB-Stand war korrekt (31 FR-Sessions, 31 FR-People, 14 Exposures – per Post-Apply-Dry-Run bestaetigt).

## Diagnose (Read-only)

### Befund 1: Strukturluecke im Publish-Skript

Das Publish-Skript (`publish_prod_release.py`) erstellte korrekt einen Release-Snapshot unter `data/releases/{release_id}/sessions/french/` und aktualisierte den `current`-Symlink atomar. Es fehlte jedoch der Schritt, den flachen App-Leseordner `data/sessions/french/` aus dem Release zu aktualisieren.

`get_sessions_root()` in `runtime_paths.py` ergibt `PROMAT_RUNTIME_ROOT/data/sessions` = `/app/data/sessions` (flat directory). Die App liest niemals ueber `current/`.

### Befund 2: Absoluter `current`-Symlink – im Container nicht aufluesbar

Der `current`-Symlink zeigte auf den absoluten Host-Pfad `/srv/webapps_storage/promat/data/releases/...`. Dieser Pfad ist im Container nicht gemountet (nur `/app/data` = `/srv/webapps/promat/data`), weshalb `current` im Container ein dangling Symlink war.

### Befund 3: `@lru_cache` nicht invalidiert

Kein Container-Neustart nach dem Publish. `load_language_sessions`, `load_task_ready_sessions`, `is_playable_audio_artifact` halten Prozess-Lifetime-Caches – ohne Neustart bleibt der alte Stand aktiv.

### Delta

Flacher `sessions/french/`: 28 Session-Ordner (Stand Mai 2026, ohne Interview-Task bei FR-L-0001 u.a.).
Release `sessions/french/`: 31 Session-Ordner, FR-L-0001 mit allen 3 Tasks (wordlist, text, interview), FR-L-0027/0028/0029 neu.

## Produktionsfix (mit expliziter Freigabe)

1. `rm -rf /srv/webapps_storage/promat/data/sessions/french`
2. `rsync -a --checksum .../release_20260618T143628Z_.../sessions/french/ .../sessions/french/`
   – Ergebnis: 28 → 31 Sessions, FR-L-0001 jetzt mit `alignment/interview.json` + `derived/interview.mp3`
3. `docker restart promat-web-prod` → Container healthy nach 15 Sekunden

## Verifikation nach Fix

- `/health` und `/ready`: `200 OK`
- App-Loader im Container: 31 French Sessions, 20 mit Interview-Task
- DB (read-only): `fr: 31`, `en: 10`; FR-People: 31; FR-Exposures: 14 – unveraendert korrekt

## Strukturelle Korrekturen im Repo

### `publish_prod_release.py`

- Relativer Symlink: `ln -sfn "releases/$RELEASE_ID" "$CURRENT.tmp"` statt absolutem Hostpfad
- Neuer `_sync_sessions_block()`: rsync-Schritt nach `current`-Switch; pro Corpus `rm -rf` + `rsync -a`
- Neuer `_restart_container_block()`: `docker restart "$DB_CONTAINER" && sleep 15` nach Rsync
- Neuer `_restart_skip_block()` fuer `--no-restart-container`
- `RemotePublishOptions.restart_container: bool = True`; CLI-Flag `--no-restart-container`
- Publish-Log erhaelt `sessions_sync_status` und `container_restart_status`

### Tests (`app/tests/test_research_prod_publish.py`)

- Test fuer alten absoluten Symlink auf relativen Pfad korrigiert
- Neue Tests: relativer Symlink, Rsync nach Current-Switch, Container-Restart nach Rsync, `--no-restart-container`-Flag, neue Log-Felder

### `docs/spec/platform-data-files.md`

- Spec-Zeilen zu v0.7-Servermodell korrigiert: `current` ist relativer Symlink fuer Rollback/DB-Upsert-Eingabe, nicht App-Read-Pfad; App liest aus flachem `data/sessions/`; Container-Neustart nach Publish ist Pflicht.

### `docs/runbooks/research-prod-upload-and-publish.md`

- Serverzustand-Abschnitt: App liest aus flachem `sessions/`-Baum, `current` ist relativer Symlink als Rollback-Referenz
- Promote-Abschnitt: drei Schritte dokumentiert (atomarer relativer Symlink-Switch, Rsync-Corpus, Container-Restart)
- Report-Abschnitt: `sessions_sync_status` und `container_restart_status` als Pflichtfelder

### `infra/docker-compose.prod.yml`

Keine Aenderung noetig: `PROMAT_RUNTIME_ROOT:-/app` und das `:ro`-Volume-Mount sind korrekt. Der Rsync-Schritt laeuft Host-seitig vor dem Container-Neustart.

## Keine weiteren offenen Punkte

Alle Korrekturen – Produktionsfix, strukturelle Skript-Aenderung, Tests, Spec, Runbook – sind in diesem Run abgeschlossen. Der naechste Publish-Lauf (beliebiger Corpus) nutzt die korrigierten Publish-Skript-Schritte automatisch.
