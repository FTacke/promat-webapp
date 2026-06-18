# 2026-06-18 Release-Retention in Publish-Pipeline

## Ausgangsproblem

Releases unter `/srv/webapps_storage/promat/data/releases/` wurden unbegrenzt angesammelt. Vor diesem Run: 4 Releases, 2,1 G belegt, zwei davon 22 Tage alt.

## Umsetzung

### `scripts/research_data_intake/publish_prod_release.py`

Neue Felder in `RemotePublishOptions`:
- `release_retention_days: int = 7`
- `release_retention_previous: int = 1`
- `no_release_retention: bool = False`

Neue Funktionen:
- `_release_retention_inner_block(days, previous)`: Kern-Bash-Logik — scannt `releases/release_*`, behaelt current + max. N vorherige ≤ D Tage, loescht den Rest per `rm -rf`.
- `_release_retention_preview_block(days, previous)`: Gleiche Logik, aber `echo "would_delete:"` statt `rm -rf` (fuer Standalone-Preview).
- `_release_retention_section(days, previous)`: Wraps inner block mit Health/Ready-Gate (`[ "$HEALTH_STATUS" = "200" ] && [ "$READY_STATUS" = "200" ]`).
- `_retention_no_op_block()`: setzt `RETENTION_STATUS="skipped_no_flag"`.
- `build_standalone_retention_script(data_root, days, previous, apply)`: Generiert standalone Bash-Skript fuer manuellen Dry-run oder Apply auf Server.

Neue CLI-Flags: `--release-retention-days`, `--release-retention-previous`, `--no-release-retention`.

Publish-Log erhaelt 6 neue Felder: `release_retention_status`, `current_release`, `previous_release_kept`, `previous_release_age_days`, `deleted_releases`, `retention_policy`.

### Sicherheitsmechanismen

- `RETENTION_CURRENT` wird per `readlink -f` aus `$CURRENT` gelesen; alle Releases, die diesem Pfad entsprechen, werden uebersprungen.
- `case "$_r" in "$DATA_ROOT/releases/release_"*)` prueft, dass der Pfad exakt unter `releases/release_*` liegt — alle anderen werden mit `continue` uebersprungen.
- Retention laeuft nur, wenn Health und Ready 200 zurueckgeben.
- `data/sessions/`, `data/current`, `data/incoming/`, `data/publish_logs/` und DB werden nicht beruehrt.
- Release-Alter wird aus dem Timestamp im Release-Namen (nicht aus mtime) berechnet: `release_YYYYMMDDTHHMMSSz_...`.

### Tests (`app/tests/test_research_prod_publish.py`)

10 neue Tests:
- Current-Release wird nie geloescht
- Vorheriges Release bleibt wenn ≤ 7 Tage
- Vorheriges Release wird geloescht wenn > 7 Tage
- Pfad-Sicherheitscheck verhindert Deletes ausserhalb `releases/release_*`
- Health/Ready-Gate umschliesst den Retention-Block
- `--no-release-retention` setzt `skipped_no_flag`, kein `rm -rf`
- Log enthaelt alle 6 Retention-Felder
- Benutzerdefinierte Tage/Anzahl werden korrekt generiert
- Standalone-Preview-Skript enthaelt `would_delete:` ohne `rm -rf`
- Standalone-Apply-Skript enthaelt `rm -rf`

### Dokumentation

- `docs/spec/platform-data-files.md`: Retention-Regel und Begriffserklaerung hinzugefuegt.
- `docs/runbooks/research-prod-upload-and-publish.md`: Neuer Abschnitt "Release Retention" mit Policy, Log-Feldern und CLI-Optionen.

## Tests und Ruff

67 Tests, alle gruen. Ruff: keine Fehler.

## Commit und Deploy

Commit `00878c8` auf `origin/main` gepusht. GitHub Actions self-hosted Runner hat automatisch deployt; Container neu gebaut und gestartet um `2026-06-18T20:26:51 UTC`, healthy.

## Einmalige Anwendung auf Produktion

### Dry-run-Ergebnis

```
current_release: release_20260618T143628Z_french_batch_20260618_runtime
  keep_as_previous (age=0d): release_20260618T130056Z_english_batch_20260618_runtime
  would_delete: release_20260527T175805Z_promat_upload_20260527T175242Z_english_spanish_runtime
  would_delete: release_20260527T172020Z_french_batch_20260527_initial_fix01
```

### Angewendet

Retention Apply ausgefuehrt mit `build_standalone_retention_script(apply=True)`.

Geloescht:
- `release_20260527T175805Z_promat_upload_20260527T175242Z_english_spanish_runtime` (22 Tage)
- `release_20260527T172020Z_french_batch_20260527_initial_fix01` (22 Tage)

### Nachher

Verbleibende Releases: 2 (current + 1 Rollback-Reserve)
Disk-Nutzung: 2,1 G → 1,3 G (ca. 800 MB frei)
Health/Ready: 200

### Einhaltung der Bedingungen

- `data/current` nicht geloescht.
- Aktuelles Release nicht geloescht.
- Flacher App-Leseordner `data/sessions/` nicht beruehrt.
- `data/incoming/` nicht beruehrt.
- `data/publish_logs/` nicht beruehrt.
- DB nicht beruehrt.
- Kein manuelles Ad-hoc-`rm -rf`; derselbe Retention-Code wie im Publish-Prozess.
- Kein Backup/Snapshot angelegt.
