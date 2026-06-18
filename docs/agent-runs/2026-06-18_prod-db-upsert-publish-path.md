# 2026-06-18 Prod DB Upsert Publish Path

## Ziel

Den Research-Prod-Publish so erweitern, dass ein vorbereitetes `db/import_payload.json` optional, explizit und transaktional in die Produktionsdatenbank upserted werden kann.

## Ergebnis

- Neues Tool `scripts/research_data_intake/apply_prod_db_payload.py` validiert ein staged Release und plant oder schreibt den DB-Upsert.
- Neuer Publish-Wrapper `scripts/research_data_intake/publish_prod_release.py` haelt Runtime-only als Default und aktiviert den DB-Upsert nur mit `--apply-db-upsert`.
- Der DB-Upsert betrifft `research_people`, `research_sessions` und `research_session_exposures`.
- Dry-Run und Apply liefern JSON-Reports mit Insert-/Update-/Unchanged-/Delete-Counts, Batch, Sprache, Post-Upsert-Validierung und Rollback-Hinweis.
- Docs aktualisiert in Spec, Runbooks und README.

## Validierung

- `python -m pytest app/tests/test_research_prod_db_payload.py app/tests/test_research_prod_publish.py`
- Weitere Repo-Tests und Ruff werden im Abschlusslauf ausgefuehrt.
