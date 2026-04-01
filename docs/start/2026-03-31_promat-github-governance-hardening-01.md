# PROMAT GitHub Governance Hardening 01

Datum: 2026-03-31

## Ziel

Die frueh sichtbaren Repo-Instruktionen unter `.github` gegen Architektur-Drift bei Datenbank-, Dateisystem- und Importentscheidungen absichern.

## Umgesetzter Stand

- `.github/copilot-instructions.md` um explizite Forschungsdaten-, PostgreSQL- und Dev/Prod-Regeln erweitert.
- `.github/instructions/repo.instructions.md` um knappe normative Verbote gegen SQLite-Behelfe, Parallelstrukturen und temporaere Nebenwege erweitert.
- Verbindlich festgehalten, dass neue DB-, Dateisystem- und Importpfadentscheidungen unter `.github` im selben Run dokumentiert werden muessen.

## Verifikation

- Neue `.github`-Regeln gegen die aktive Repo-Governance und die vorhandene PostgreSQL-/Runtime-Struktur geprueft.
- Dopplungen zur Projektspezifikation bewusst knapp gehalten; `.github` enthaelt nur die frueh wirksamen Repo-Regeln.