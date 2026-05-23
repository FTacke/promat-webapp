# Dev Start Migration Idempotency Fix

## Ziel

- `./scripts/dev-start.ps1` lief lokal nicht mehr an.
- Ursache prüfen und den echten Startpfad wiederherstellen.

## Befund

- Der Root-Wrapper unter `scripts/dev-start.ps1` war nicht die Ursache.
- Der Fehler lag in `app/scripts/dev-start.ps1` beim wiederholten Lauf von `scripts/apply_auth_migration.py --engine postgres`.
- Die PostgreSQL-Migrationskette sollte auf dem bestehenden Dev-Postgres idempotent erneut laufen, brach aber in `0003_create_research_sets.sql` mit `column "state" does not exist` ab.
- Hintergrund: `0006_unify_research_sets_for_curated_db_model.sql` benennt `research_sets.state` nach `lifecycle` um, während `0003` beim späteren Rerun weiter blind den Legacy-Index `idx_research_sets_owner_state` anlegen wollte.
- Zusätzlich war `0006_unify_research_sets_for_curated_db_model.sql` selbst nicht vollständig rerun-idempotent, weil mehrere `ADD CONSTRAINT`-Anweisungen ihre bereits existierenden Constraints nicht vorher entfernten.

## Umsetzung

- `app/migrations/0003_create_research_sets.sql`
  - Legacy-Index auf `(owner_user_id, state)` nur noch anlegen, wenn die Spalte `state` tatsächlich noch existiert.
- `app/migrations/0006_unify_research_sets_for_curated_db_model.sql`
  - alle von der Migration selbst angelegten Constraints vor dem erneuten `ADD CONSTRAINT` per `DROP CONSTRAINT IF EXISTS` abgesichert.

## Validierung

- erneuter direkter Lauf von:
  - `python scripts/apply_auth_migration.py --engine postgres`
- erneuter Root-Start von:
  - `./scripts/dev-start.ps1`
- Health-Check auf:
  - `http://127.0.0.1:8000/health`

## Ergebnis

- Die komplette PostgreSQL-Migrationskette läuft wieder auf einem bestehenden Dev-Postgres durch.
- `./scripts/dev-start.ps1` startet wieder bis zum laufenden Dev-Server auf Port `8000`.
- `/health` antwortet wieder mit `status: healthy`.