# Local Dev Start

## Zweck

Wiederholbarer Start- und Reparaturablauf fuer die lokale PROMAT-Entwicklungsumgebung mit der kanonischen Workspace-PostgreSQL-Instanz auf `127.0.0.1:54321`.

## Voraussetzungen

- Workspace-Root: `c:\dev\promat`
- bevorzugte Python-Umgebung: `c:\dev\promat\.venv`
- Docker Desktop oder kompatibles Docker-Setup fuer die lokale Dev-PostgreSQL-Instanz

## Standardstart

1. Im Workspace-Root `./scripts/dev-start.ps1` ausfuehren.
2. Das Script startet bei der kanonischen lokalen `AUTH_DATABASE_URL` automatisch `promat_auth_db`, wartet auf Readiness und fuehrt die idempotente Auth-/Research-Set-Migrationskette aus.
3. Im selben lokalen Dev-Fall setzt das Script den Standard-Admin `admin_dev` idempotent zurueck und setzt dessen Passwort auf `Admin0000!`.
4. Danach startet die Flask-App ueber `python -m src.app.main`.

## Erstinitialisierung oder Admin-Reset

1. Im Workspace-Root `./app/scripts/dev-setup.ps1` ausfuehren.
2. Optional `-ResetAuth` verwenden, wenn die lokale Dev-Datenbank bewusst neu aufgebaut werden soll.
3. Das Script startet die lokale PostgreSQL-Instanz, wartet auf Readiness, fuehrt dieselbe Migrationskette aus und legt anschliessend den initialen Admin an.
4. Fuer den Standardstart und fuer wiederholte lokale Resets ist `admin_dev / Admin0000!` damit der kanonische Dev-Login.

## Standard-Dev-Admin

1. Benutzername: `admin_dev`
2. Passwort: `Admin0000!`
3. `./scripts/dev-start.ps1` stellt diesen Account auf der kanonischen lokalen Dev-DB bei jedem Start idempotent wieder her.
4. Der Rueckfall gilt nur fuer lokale Development-Starts gegen die kanonische Dev-PostgreSQL-URL auf `127.0.0.1:54321`.

## Wenn `research_sets` lokal fehlt

1. Sicherstellen, dass `AUTH_DATABASE_URL` auf die kanonische lokale Dev-DB zeigt: `postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:54321/promat_auth`.
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