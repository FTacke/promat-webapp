# PROMAT Governance Bootstrap 03

Datum: 2026-03-31

## Ziel

Ein schlankes, repo-spezifisches Governance-System für Agents und Maintainer aufsetzen, das die bestehende PROMAT-Spezifikation in operative Regeln, Templates und Doku-Pfade übersetzt.

## Umgesetzter Stand

- Root-`AGENTS.md` zu einer verbindlichen Repo-Governance ausgebaut.
- Scoped `AGENTS.md` für `app/`, `docs/` und `scripts/` ergänzt.
- `.github/copilot-instructions.md` mit dem aktuellen Architekturstand synchronisiert.
- PR- und Issue-Templates unter `.github/` eingeführt.
- Aktive Doku-Struktur unter `docs/architecture/`, `docs/conventions/`, `docs/runbooks/`, `docs/decisions/` und `docs/agent-runs/` angelegt.
- Templates für Run-Logs, ADRs und Runbooks angelegt.

## Repo-spezifische Leitentscheidungen

- Die Spezifikation bleibt die bindende Source of Truth.
- `docs/agent-runs/` ist die Standardstelle für substanzielle Run-Dokumentation.
- `docs/start/` bleibt als zusätzliche historische Bootstrap-Chronik erhalten.
- `CODEOWNERS` wurde nicht eingeführt, weil kein autoritativer Owner-Stand im Repo vorliegt.

## Verbleibende Grenzen

- Historische `docs/start/`-Einträge bleiben in ihrer ursprünglichen Sprache und Begriffswahl bestehen.
- Die Governance verhindert Drift, ersetzt aber keine spätere fachliche ADR-Arbeit bei größeren Architekturentscheidungen.