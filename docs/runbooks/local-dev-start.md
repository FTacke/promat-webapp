# Local Dev Start

## Zweck

Wiederholbarer Start- und Reparaturablauf fuer die lokale PROMAT-Entwicklungsumgebung mit der kanonischen Workspace-PostgreSQL-Instanz auf `127.0.0.1:54321`.
Wenn dieser Default-Port auf dem lokalen Host nicht veroeffentlicht werden kann, weichen `./scripts/dev-start.ps1` und `./app/scripts/dev-setup.ps1` automatisch auf einen freien lokalen Fallback-Port aus und halten `AUTH_DATABASE_URL` sowie `PROMAT_DEV_DB_PORT` im gestarteten Prozess konsistent.

## Voraussetzungen

- Workspace-Root: `c:\dev\promat`
- bevorzugte Python-Umgebung: `c:\dev\promat\.venv`
- Docker Desktop oder kompatibles Docker-Setup fuer die lokale Dev-PostgreSQL-Instanz

## Standardstart

1. Im Workspace-Root `./scripts/dev-start.ps1` ausfuehren.
2. Das Script startet bei der kanonischen lokalen `AUTH_DATABASE_URL` automatisch `promat_auth_db`, wartet auf Readiness und fuehrt die idempotente Auth-/Research-Set-Migrationskette aus.
3. Wenn `127.0.0.1:54321` lokal nicht bindbar ist, waehlt das Script einen freien Fallback-Port, setzt `PROMAT_DEV_DB_PORT` und richtet `AUTH_DATABASE_URL` fuer diesen Start darauf aus.
4. Im selben lokalen Dev-Fall setzt das Script den Standard-Admin `admin_dev` idempotent zurueck und setzt dessen Passwort auf `Admin0000!`.
5. Vor dem Webstart beendet das Script alle noch laufenden PROMAT-Dev-Prozesse aus demselben Workspace, damit auf Port `8000` kein stale Listener altes HTML weiter ausliefert.
6. Danach startet die Flask-App ueber `python -m src.app.main` in Development-Reload-Modus auf `127.0.0.1:8000`, sodass Python-, Template- und sonstige Flask-Dev-Aenderungen im Browser ohne manuelle Prozesssuche sichtbar werden.

## Erstinitialisierung oder Admin-Reset

1. Im Workspace-Root `./app/scripts/dev-setup.ps1` ausfuehren.
2. Optional `-ResetAuth` verwenden, wenn die lokale Dev-Datenbank bewusst neu aufgebaut werden soll.
3. Das Script startet die lokale PostgreSQL-Instanz, waehlt bei Bedarf denselben Fallback-Port-Mechanismus wie `dev-start`, fuehrt dieselbe Migrationskette aus und legt anschliessend den initialen Admin an.
4. Fuer den Standardstart und fuer wiederholte lokale Resets ist `admin_dev / Admin0000!` damit der kanonische Dev-Login.

## Standard-Dev-Admin

1. Benutzername: `admin_dev`
2. Passwort: `Admin0000!`
3. `./scripts/dev-start.ps1` stellt diesen Account auf der kanonischen lokalen Dev-DB bei jedem Start idempotent wieder her.
4. Der Rueckfall gilt fuer lokale Development-Starts gegen die kanonische Dev-PostgreSQL-URL und folgt demselben Host-Port wie `PROMAT_DEV_DB_PORT` im jeweiligen Startprozess.

## Port-Fallback oder feste Portwahl

1. Default bleibt `127.0.0.1:54321`.
2. Wenn Windows oder ein anderer lokaler Dienst diesen Port nicht fuer Docker freigibt, waehlt das Startscript automatisch einen freien Fallback-Port wie `55432`.
3. Fuer einen festen lokalen Port kann vor dem Start `PROMAT_DEV_DB_PORT` gesetzt werden.
4. Wenn `AUTH_DATABASE_URL` ausserhalb des Startscripts dauerhaft konfiguriert wird, muss ihr Port mit `PROMAT_DEV_DB_PORT` uebereinstimmen.

## Wenn `research_sets` lokal fehlt

1. Sicherstellen, dass `AUTH_DATABASE_URL` auf die aktuell verwendete lokale Dev-DB zeigt. Standard ist `postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:54321/promat_auth`; nach einem Port-Fallback muss derselbe Fallback-Port verwendet werden.
2. `./scripts/dev-start.ps1` erneut ausfuehren.
3. Das Script zieht die fehlende Migration `app/migrations/0003_create_research_sets.sql` idempotent nach.
4. Zur Kontrolle in Postgres pruefen, ob `research_sets`, `research_set_items` und `research_set_sessions` existieren.

## Erwartetes Ergebnis

- Die lokale Dev-Datenbank enthaelt mindestens:
  - `users`
  - `refresh_tokens`
  - `reset_tokens`
  - `analytics_daily`
  - `research_sets`
  - `research_set_items`
  - `research_set_sessions`
- `POST /api/research/sets` antwortet im lokal gebootstrappten Zustand nicht mehr mit `relation "research_sets" does not exist`.
- `http://127.0.0.1:8000/health` antwortet aus genau einem aktiven PROMAT-Dev-Listener.
- Wiederholtes Ausfuehren von `./scripts/dev-start.ps1` ersetzt den alten PROMAT-Listener auf `8000`, statt ihn parallel weiterlaufen zu lassen.

## Wenn der Browser alte HTML-Staende zeigt

1. `./scripts/dev-start.ps1` erneut im Workspace-Root ausfuehren.
2. Das Script beendet jetzt stale PROMAT-Prozesse aus `c:\dev\promat` automatisch, bevor es den neuen Dev-Server startet.
3. Wenn Port `8000` danach immer noch blockiert ist, meldet das Script den fremden Prozess explizit, statt still einen alten Zustand weiter zu verwenden.