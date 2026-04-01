# GitHub Governance Hardening 01

Datum: 2026-03-31

## Ziel

Die aktiven `.github`-Instruktionen so schaerfen, dass kuenftige Repo-Arbeit keine SQLite-, Fallback- oder Dev-Sonderarchitektur fuer Forschungsdaten einfuehrt.

## Consulted Sources

- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- `app/migrations/0001_create_auth_schema_postgres.sql`
- `app/migrations/0002_create_analytics_tables.sql`
- `app/scripts/dev-setup.ps1`

## Geaenderte Bereiche

- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `docs/agent-runs/`
- `docs/start/`

## Wichtige Entscheidungen

- Die verbindliche Repo-Governance unter `.github` nennt nun explizit PostgreSQL als verbindliche Datenbankstrategie fuer Forschungsdaten.
- Dev und Prod werden fuer Forschungsdaten normativ als moeglichst gleiche Architektur festgeschrieben; Dev-only Fallbacks, SQLite-Behelfe und Parallelstrukturen sind ohne explizite Entscheidung unzulaessig.
- Vor Aenderungen an DB, Seeds, Importpfaden oder Dev-Setup muss die bestehende PostgreSQL-, Compose-, Env- und Migrationsstruktur geprueft werden.
- Akzeptierte Architekturentscheidungen zu DB-, Dateisystem- und Importpfaden muessen kuenftig im selben Run unter `.github` festgehalten werden.

## Abweichungen

- Keine Architekturabweichung eingefuehrt.

## Verifikation

- Bestehende `.github`-Instruktionen wurden gegen die aktive Repo-Governance und Runtime-/DB-Dateien abgeglichen.
- Die neuen Regeln duplizieren die Projektspezifikation nicht vollstaendig, sondern verlinken auf die verbindlichen aktiven Quellen und ergaenzen nur die frueh sichtbaren Repo-Verbote.

## Offene Punkte

- Die aktive Webapp liest Forschungs-Sessions derzeit noch nicht aus `data/sessions/`; sobald dieser Reader gebaut wird, sollte seine Datenquelle und Listing-Logik ebenfalls knapp in `.github` normiert werden.
- Falls spaeter eigene Forschungsdaten-Tabellen oder -Schemas in PostgreSQL eingefuehrt werden, sollte `.github` um einen knappen Hinweis auf das kanonische Schema-Entry-Point erweitert werden.

## Naechste sinnvolle Schritte

- Beim naechsten Ausbau des Forschungsdaten-Readers die zugelassene Lade- und Listing-Logik unter `.github` knapp nachziehen.
- Bei Einfuehrung einer echten Forschungsdaten-DB die kanonischen Migrations- und Seed-Entry-Points unter `.github` explizit benennen.