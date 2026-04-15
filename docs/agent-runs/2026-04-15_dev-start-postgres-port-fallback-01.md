# PROMAT Dev-Start PostgreSQL-Port-Fallback

Datum: 2026-04-15

## Ziel

Den lokalen Startfehler beheben, bei dem `./scripts/dev-start.ps1` die Auth-/Research-Set-Migration gegen `127.0.0.1:54321` startet, obwohl Docker den Host-Port auf diesem Windows-Host nicht veroeffentlichen kann.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/runbooks/local-dev-start.md`
- `docker-compose.dev-postgres.yml`
- `app/scripts/dev-start.ps1`
- `app/scripts/dev-setup.ps1`

## Geänderte Bereiche

- gemeinsamer lokaler PostgreSQL-Bootstrap unter `app/scripts/`
- Dev-Start und Dev-Setup fuer lokale PostgreSQL-Port-Fallbacks
- lokales Docker-Compose-Port-Mapping fuer konfigurierbare Host-Ports
- aktive Runtime-Spec und lokales Dev-Runbook

## Wichtige Entscheidungen

- Der kanonische Dev-Default bleibt `127.0.0.1:54321`.
- Wenn dieser Host-Port lokal nicht bindbar ist, duerfen `dev-start` und `dev-setup` fuer den jeweiligen Prozesslauf auf einen freien Fallback-Port wechseln.
- Der Fallback ist nur zulaessig, wenn die Startskripte gleichzeitig `PROMAT_DEV_DB_PORT` und `AUTH_DATABASE_URL` auf denselben tatsaechlich veroeffentlichten Host-Port ausrichten.

## Abweichungen

- Auf dem betroffenen Windows-Host konnte Docker `0.0.0.0:54321` nicht binden und lieferte `bind: An attempt was made to access a socket in a way forbidden by its access permissions`.

## Verifikation

- `docker ps`, `docker inspect`, `docker compose ps`, `docker port promat_auth_db` und `Test-NetConnection 127.0.0.1 -Port 54321` gegengeprueft
- bestaetigt, dass der Container intern gesund war, aber kein erreichbarer Windows-Listener auf `54321` existierte
- Windows-Portdiagnose mit `netsh interface ipv4 show excludedportrange protocol=tcp`, `netsh interface ipv6 show excludedportrange protocol=tcp` und `netstat -aon | findstr 54321` ausgefuehrt
- `./app/scripts/dev-setup.ps1 -SkipInstall -SkipDevServer` erfolgreich gegen den Fallback-Port `55432` durchlaufen lassen
- `./scripts/dev-start.ps1` aus sauberer Shell neu gestartet; Flask lief auf `http://127.0.0.1:8000`, `docker port promat_auth_db` zeigte `55432`, und `/health` antwortete wieder mit `status=healthy`

## Offene Punkte

- Keine.

## Nächste sinnvolle Schritte

- `./scripts/dev-start.ps1` lokal erneut starten und den von Docker veroeffentlichten Host-Port aus der Konsole uebernehmen, falls `54321` wieder abgefangen wird