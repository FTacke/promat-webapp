# Architecture

Dieser Bereich beschreibt die aktive PROMAT-Architektur in Repo-Form.

## Kernmodell

- `app/` enthält die versionierte Webapp.
- `data/` enthält geschützte Forschungsdaten und Sessions.
- `public/` enthält explizit freigegebene öffentliche Medien.
- `secure/` bleibt außerhalb der Webapp.
- `scripts/` enthält wiederholbare Verarbeitungs- und Entrypoints.

## Verbindliche Leitlinien

- Die Spezifikation in `../PROMAT_ Plattform-, Daten- und Filestruktur.md` beschreibt die Zielarchitektur.
- Governance-Dateien operationalisieren diese Architektur für Maintainer und Agents.
- Dev und Prod sollen dieselbe Struktur und dieselben Begriffe verwenden.

Siehe zusätzlich `dev-prod-parity.md` für akzeptierte Unterschiede und Abbaurichtung.