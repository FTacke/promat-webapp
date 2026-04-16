# Local Dev Start Live Reload And Listener Cleanup

Datum: 2026-04-16

## Ziel

Den lokalen PROMAT-Dev-Start so haerten, dass Browser-Pruefungen nicht mehr an stale Port-8000-Prozessen oder einem nicht reload-faehigen Flask-Start haengen. Zukuenftige Code- und Template-Aenderungen sollen ueber den kanonischen Root-Entrypoint sichtbar werden, ohne manuelle Prozessjagd.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `scripts/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `app/src/app/main.py`
- `app/scripts/dev-start.ps1`
- `app/scripts/dev-setup.ps1`
- `app/scripts/dev-postgres.ps1`
- `docs/runbooks/local-dev-start.md`
- repo memory `/memories/repo/promat-dev-setup-notes.md`

## Geaenderte Bereiche

- Flask-Entrypoint `app/src/app/main.py`
- kanonischer Root- und App-Dev-Start ueber `app/scripts/dev-start.ps1`
- aktive Runtime-Spec in `docs/spec/platform-data-files.md`
- wiederholbares Dev-Start-Runbook in `docs/runbooks/local-dev-start.md`

## Wichtige Entscheidungen

- Der Dev-Server laeuft nicht mehr ueber einen starren `make_server`, sondern ueber Werkzeugs Reload-Loop, damit Python- und Template-Aenderungen im lokalen Browser ohne manuellen Neustart sichtbar werden.
- `app/scripts/dev-start.ps1` setzt in `development` standardmaessig `FLASK_DEBUG=1`, falls die Variable nicht explizit vorgegeben ist.
- Vor jedem Webstart beendet `app/scripts/dev-start.ps1` alle laufenden PROMAT-Dev-Prozesse aus derselben Arbeitsumgebung, einschliesslich des Windows-Falls, in dem der Child-Prozess nur als `python.exe -m src.app.main` erscheint.
- Wenn Port `8000` durch einen nicht zu PROMAT gehoerenden Prozess blockiert ist, bricht das Script mit einer klaren Fehlermeldung ab, statt weiter einen veralteten Serverzustand zu kaschieren.

## Abweichungen

- Keine fachliche Abweichung von der aktiven Spec. Die Runtime-Regel fuer `scripts/dev-start.ps1` wurde in `docs/spec/platform-data-files.md` und der wiederholbare Ablauf in `docs/runbooks/local-dev-start.md` im selben Run aktualisiert.

## Verifikation

- `get_errors` auf `app/src/app/main.py`, `app/scripts/dev-start.ps1`, `docs/spec/platform-data-files.md` und `docs/runbooks/local-dev-start.md`: keine Fehler
- realer Root-Start ueber `./scripts/dev-start.ps1`:
  - lokaler Dev-Postgres-Fallback von `54321` auf `55432` erfolgreich
  - bestehende stale PROMAT-Prozesse auf Port `8000` wurden vor dem Start automatisch beendet
  - neuer Dev-Server startete auf `http://127.0.0.1:8000`
  - Werkzeug-Reloader aktiv, sichtbar an `Restarting with stat`
- HTTP-Pruefung gegen den laufenden Server:
  - `/health` antwortet `healthy`
  - `/de/sample` liefert den aktuellen HTML-Stand mit `Profil →` und `Spanien`, also nicht den alten stale Zustand
- Port-Pruefung: genau ein aktiver Listener auf `0.0.0.0:8000`

## Offene Punkte

- Kein weiterer in-scope Punkt offen. Der laufende Dev-Server wurde nach der Verifikation bewusst aktiv gelassen, damit die aktuelle Browser-Session direkt weitergenutzt werden kann.