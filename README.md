# PROMAT Webapp

PROMAT ist die Webplattform für Pronunciation Matters. Die aktuelle Codebasis ist ein strukturierter Bootstrap-Stand, der Routing, Runtime-Grenzen und Datenablage auf den in `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md` definierten Zielzustand vorbereitet.

## Aktuelle Struktur

- `app/` enthält den versionierten Flask-Anwendungskern.
- `data/` ist der vorbereitete geschützte Forschungsdatenraum, inklusive `data/sessions/` und Dev-Runtime-Unterordnern.
- `public/` ist der vorbereitete öffentliche Medienraum für Unterricht und Sample.
- `secure/` ist als geschützter Klardatenbereich reserviert und wird nicht von der Webapp verwendet.
- `scripts/` bündelt Root-Entrypoints und die vorbereitete Verarbeitungspipeline.

## Governance und Doku

- `AGENTS.md` im Repo-Root definiert die verbindlichen Arbeitsregeln für Maintainer und Repo-Agents.
- Scoped `AGENTS.md` unter `app/`, `docs/` und `scripts/` ergänzen bereichsspezifische Regeln.
- `docs/architecture/`, `docs/conventions/`, `docs/runbooks/`, `docs/decisions/` und `docs/agent-runs/` bilden die aktive technische Dokumentation.
- `docs/start/` bleibt die historische Bootstrap- und Strukturchronik.

## Routing

Die primären öffentlichen Routen folgen jetzt dem ui-lang-prefixed Schema.

- `/de/project`
- `/de/project/about`
- `/de/project/research-design`
- `/de/project/data-methods`
- `/de/project/team`
- `/de/research`
- `/de/research/spanish`
- `/de/research/spanish/design`
- `/de/research/spanish/speakers`
- `/de/research/spanish/recordings`
- `/de/research/spanish/comparison`
- `/de/research/spanish/phenomena`
- `/de/research/french`
- `/de/research/german`
- `/de/research/english`
- `/de/teaching`
- `/de/teaching/spanish`
- `/de/teaching/spanish/phenomena`
- `/de/teaching/spanish/materials`
- `/de/teaching/french`
- `/de/teaching/german`
- `/de/teaching/english`
- `/de/sample`

Frühere deutsche Altpfade wie `/forschung/...`, `/unterricht/...`, `/projekt/...`, `/sample` und `/sprachen` sind aus dem öffentlichen Routing entfernt.

## Runtime-Grenzen

- `PROMAT_RUNTIME_ROOT` muss auf das Workspace-Root zeigen, das `data/`, `logs/`, `secure/` und `public/` enthält.
- `PROMAT_PUBLIC_ROOT` ist die einzige gültige Variable für den öffentlichen Medienraum und soll auf `<workspace>/public` zeigen.
- `AUTH_DATABASE_URL` bleibt die einzige gültige Variable für Auth- und Core-Daten.
- Die lokale Dev-Postgres-Ablage liegt unter `data/db/postgres_dev`.

## Aktueller Ausbaugrad

- Die UI ist weiterhin auf Deutsch ausgerichtet, aber Labels und technische Slugs sind entkoppelt.
- `/en/...` ist strukturell vorbereitet, aber noch nicht als vollständige UI aktiviert.
- Forschungsseiten mit späterem Restricted-Zugriff sind strukturell vorbereitet, aber bewusst noch nicht final abgesichert.
- Die Export-Pipeline nach `public/` ist nur als Ordner- und Skriptstruktur angelegt.