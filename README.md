# PROMAT Webapp

PROMAT ist die Webplattform für Pronunciation Matters. Das Repo bündelt die Flask-Anwendung, die geschützte Forschungsdatenstruktur und die Skript-Entrypoints für Setup, Import und Verarbeitung.

## Orientierung

- `app/` enthält den versionierten Anwendungskern.
- `data/` enthält geschützte Forschungsdaten und lokale Dev-Runtime-Daten.
- `public/` ist der explizit freigegebene Medienraum.
- `secure/` ist für Klardaten reserviert.
- `scripts/` enthält wiederholbare Entrypoints und Pipeline-Bausteine.

## Verbindliche Spezifikation

Die aktive Source of Truth liegt ausschließlich unter `docs/spec/`:

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`

Für Änderungen an Architektur, Routing, Datenpfaden, Governance oder Repo-Struktur gelten zusätzlich die jeweils relevanten scoped `AGENTS.md` sowie das Runtime-Wiring in `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `docker-compose.dev-postgres.yml` und `infra/docker-compose.prod.yml`.

## Weitere Doku-Bereiche

- `docs/decisions/` enthält ADRs und erklärt das Warum.
- `docs/runbooks/` enthält wiederholbare Arbeitsabläufe.
- `docs/agent-runs/` enthält nicht-normative Arbeitsjournale.

## Governance

- `AGENTS.md` im Repo-Root und die scoped `AGENTS.md` unter `app/`, `docs/` und `scripts/` enthalten nur Arbeitsregeln und verweisen auf `docs/spec/`.
- `.github/` enthält die dazugehörigen Repo- und Review-Regeln.
