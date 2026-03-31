# PROMAT Scripts Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` für Arbeiten unter `scripts/`.

## Zweck

- Root-Skripte sind wiederholbare Entrypoints und Pipeline-Bausteine.
- Skripte koordinieren Import, Session-Anlage, Audio-Verarbeitung und Export nach `public/`, ohne die Architektur zu unterlaufen.

## Arbeitsregeln

- Skripte müssen idempotent oder klar als nicht-idempotent markiert sein.
- Eingaben, Ausgaben und Zielpfade müssen explizit und nachvollziehbar sein.
- Keine impliziten Pfadannahmen jenseits der kanonischen Runtime-Variablen und dokumentierten Repo-Struktur.
- Keine stillen Seiteneffekte außerhalb des expliziten Zweckes.
- Öffentliche Exporte nach `public/` sind explizite Pipeline-Schritte, keine verdeckten Nebeneffekte.

## Pfad- und Datenregeln

- Keine Script-Logik darf `secure/` an die Webapp oder an öffentliche Exporte durchreichen.
- `raw`, `source`, `alignment`, `derived` und `items` bleiben getrennte Verarbeitungsstufen.
- Skripte dürfen diese Stufen nicht begrifflich oder physisch vermischen.

## Root-Skript-Regeln

- `scripts/dev-start.ps1` und `scripts/dev-setup.ps1` bleiben schlanke Wrapper auf `app/scripts/`.
- Root-Skripte enthalten keine zweite Implementierung derselben Logik.

## No-Go

- Keine stillen Massenumbenennungen oder Pfadverschiebungen ohne Doku.
- Keine impliziten Legacy-Aliasse oder alte Runtime-Variablen.
- Keine direkten öffentlichen Auslieferungen aus `data/`.