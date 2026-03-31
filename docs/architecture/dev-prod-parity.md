# Dev/Prod Parity

PROMAT behandelt Dev und Prod als dieselbe Architektur mit minimalen, dokumentierten Infrastrukturunterschieden.

## Verbindliche Paritätsregeln

- Routing, Slugs, technische Keys und Datenkonzepte sind in Dev und Prod identisch.
- `AUTH_DATABASE_URL`, `PROMAT_RUNTIME_ROOT` und `PROMAT_PUBLIC_ROOT` sind in beiden Umgebungen die kanonischen Variablen.
- `data/`, `public/` und `secure/` behalten in Dev und Prod dieselbe semantische Rolle.
- Öffentliche Medienlogik, Zugriffsgrenzen und Dateistruktur dürfen nicht umgebungsspezifisch auseinanderlaufen.

## Aktuell akzeptierte Unterschiede

- Dev nutzt `docker-compose.dev-postgres.yml` mit Host-Bind-Mount nach `data/db/postgres_dev`.
- Prod nutzt `app/infra/docker-compose.prod.yml` mit produktionsnahem Container-Setup und persistentem Docker-Volume für PostgreSQL.
- Dev setzt das Runtime-Root auf das Workspace-Root, Prod auf `/app` im Container. Die semantischen Unterpfade bleiben gleich.

## Aktuelle Produktreife-Grenzen

- Die UI ist technisch auf weitere UI-Sprachen vorbereitet, produktiv aber derzeit deutsch.
- Forschungsnahe Detailseiten mit späterem Restricted-Zugriff sind strukturell vorbereitet, aber nicht final ausgebaut.

## Regeln für neue Abweichungen

- Neue Dev/Prod-Abweichungen sind nur zulässig, wenn sie klein, infrastrukturell und dokumentiert sind.
- Jede neue Abweichung muss im zugehörigen Run-Log und hier benannt werden.
- Dev-only Workarounds ohne dokumentierten Rückbaupfad sind nicht zulässig.