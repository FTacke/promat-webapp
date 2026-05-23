# Migration Hygiene Audit

## Ziel

- gesamte SQL-Migrationskette kurz auf Rerun-Idempotenz pruefen
- Dev-Start-Fehlerpfad nach dem vorherigen Fix weiter absichern
- lokale Dev-Start-Doku um den Rerun-Anspruch ergaenzen

## Gepruefte Migrationen

- `0001_create_auth_schema_postgres.sql`
- `0001_create_auth_schema_sqlite.sql`
- `0002_create_analytics_tables.sql`
- `0003_create_research_sets.sql`
- `0004_extend_research_sets_for_phenomena_editor.sql`
- `0005_split_research_set_workbench_state.sql`
- `0006_finalize_protected_area.sql`
- `0006_unify_research_sets_for_curated_db_model.sql`
- `0007_create_research_metadata_tables.sql`
- `0008_create_access_requests.sql`
- `0008_create_access_requests_sqlite.sql`

## Ergebnis

- keine weitere breite Rerun-Failure-Kette gefunden
- bestaetigt problematisch waren die bereits gefixten Legacy-Uebergaenge zwischen `0003` und `0006`
- fuer den Python-Migrationsrunner wurden klarere Fehlertexte ergaenzt
- das lokale Dev-Runbook dokumentiert jetzt ausdruecklich den Root-Startpfad, die erneute Migration auf bestehendem Dev-Postgres und die lokale Validierung

## Behobene Punkte

- `app/scripts/apply_auth_migration.py`
  - Fehlerausgabe nennt jetzt Engine und betroffene Migration
- `app/scripts/dev-start.ps1`
  - verweist bei Migrationsfehlern explizit auf die vorherige Runner-Fehlermeldung
- `docs/runbooks/local-dev-start.md`
  - dokumentiert Root-Wrapper versus Implementierungspfad
  - dokumentiert den rerun-idempotenten Anspruch der Dev-Migrationen
  - dokumentiert lokale Validierung ueber Migration, Dev-Start und `/health`
- `app/tests/test_research_sets.py`
  - statische Regression fuer den guard auf den Legacy-`state`-Index und die Constraint-Drops in `0006`

## Bewusst offen gelassen

- `0006_finalize_protected_area.sql` enthaelt weiter die Datenmigration `UPDATE users SET role = 'user' WHERE lower(role) = 'editor'`.
- Das ist kein Rerun-Crash, sondern eine fachliche Legacy-Normalisierung. Fuer diesen Lauf wurde kein groesserer Umbau dieser historischen Datenmigration vorgenommen.

## Checks

- `python scripts/apply_auth_migration.py --engine postgres`
- `pytest tests/test_research_sets.py -q -k "research_set_migration_declares_expected_tables or apply_auth_migration_discovers_full_postgres_chain"`
- `./scripts/dev-start.ps1`
- `http://127.0.0.1:8000/health`