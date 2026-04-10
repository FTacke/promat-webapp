# Lokale Research-Set-Basis stabilisiert

Datum: 2026-04-09

## Ziel

Die lokale Research-Set-Grundlage diagnostizieren und stabilisieren: fehlende `research_sets`-Tabellen sauber nachziehen, den Dev-Startpfad robust machen, rohe 500er bei fehlendem Set-Schema vermeiden und den lokalen Ablauf dokumentieren.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `scripts/AGENTS.md`
- `app/scripts/dev-start.ps1`
- `app/scripts/dev-setup.ps1`
- `app/scripts/apply_auth_migration.py`
- `app/migrations/0003_create_research_sets.sql`
- `app/src/app/research_sets.py`
- `app/src/app/routes/research_api.py`
- `app/src/app/research_views.py`
- `docker-compose.dev-postgres.yml`

## Root Cause

- Die lokale Dev-PostgreSQL-Instanz lief auf einem persistierten Volume, in dem nur die frueheren Tabellen `users`, `refresh_tokens`, `reset_tokens` und `analytics_daily` existierten.
- `app/scripts/apply_auth_migration.py` kann `0003_create_research_sets.sql` korrekt anwenden, aber `scripts/dev-start.ps1` hat die lokale Datenbank bislang nicht selbst gebootstrappt oder migriert.
- Dadurch konnte ein alter lokaler Datenstand ohne `research_sets` bestehen bleiben und spaeter bei `POST /api/research/sets` als rohe SQL-Exception explodieren.

## Geaenderte Bereiche

- `app/scripts/dev-start.ps1`
- `app/scripts/dev-setup.ps1`
- `app/src/app/research_sets.py`
- `app/src/app/routes/research_api.py`
- `app/src/app/research_views.py`
- `app/tests/test_research_sets.py`
- `app/tests/test_research_player_set_context.py`
- `docs/spec/platform-data-files.md`
- `docs/runbooks/local-dev-start.md`

## Wichtige Entscheidungen

- `scripts/dev-start.ps1` bootstrappt fuer die kanonische lokale Dev-PostgreSQL-URL jetzt selbst die lokale DB-Service-Readiness und die idempotente Migrationskette, statt auf einen einmalig frischen Volume-Zustand zu vertrauen.
- `app/scripts/dev-setup.ps1` wartet ebenfalls explizit auf PostgreSQL-Readiness und uebergibt danach an `dev-start` ohne doppelten Bootstrap.
- Datenbanknahe Set-Fehler werden in der Set-Schicht als kontrollierte `ResearchSetStorageUnavailableError` behandelt und in der API als `503 Service Unavailable` ausgegeben.
- Der Player degradiert bei fehlender Set-Storage-Basis auf die regulaere Session-Ansicht mit ehrlichem Hinweis, statt mit einem unkontrollierten Fehler zu scheitern.

## Verifikation

- Lokale Dev-DB per Docker Compose geprueft; initial waren `research_sets`, `research_set_items` und `research_set_sessions` nicht vorhanden.
- `app/scripts/apply_auth_migration.py --engine postgres` gegen die lokale Dev-DB erfolgreich ausgefuehrt; die Research-Set-Tabellen wurden nachgezogen.
- Regressionstests fuer kontrollierte 503-API-Antwort und saubere Player-Degradation ergaenzt.

## Offene Punkte

- Die inhaltliche Vereinfachung der `comparison`- und `phenomena`-UIs bleibt bewusst nachgeordnet und sollte erst auf dieser stabilisierten Basis erfolgen.

## Naechste sinnvolle Schritte

- Den lokal produktiven `comparison`-/`phenomena`-Umfang auf einen kleineren ersten Arbeitsmodus reduzieren, jetzt wo die Set-Basis reproduzierbar startet.