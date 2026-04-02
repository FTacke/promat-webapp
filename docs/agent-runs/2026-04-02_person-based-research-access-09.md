# Personbasierter Research-Zugang und kanonische IDs

Datum: 2026-04-02

## Ziel

Den spanischen PROMAT-Research-Zugang repo-weit auf ein stabiles personbasiertes Modell umstellen: kanonische `person_id`/`session_id`, `speakers` pro Person, `recordings` pro Session/Task, genau eine Personenseite pro Person und ein nativer Sonderfall mit genau einer Session.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- `app/migrations/`
- `app/scripts/dev-setup.ps1`
- aktive Seed- und Import-Entrypoints unter `scripts/`

## Geänderte Bereiche

- Research-Runtime und Aggregationslogik unter `app/src/app/`
- öffentliche Research-Routen und Templates unter `app/templates/pages/`
- Research-bezogene CSS-Layer unter `app/static/css/`
- spanischer Dev-Seed unter `scripts/session_setup/` und `data/sessions/spanish/`
- fokussierte Tests unter `app/tests/`
- aktive Doku und Governance unter `README.md`, `.github/`, `AGENTS.md`, `docs/`, `scripts/`

## Wichtige Entscheidungen

- `person_id` und `session_id` werden verbindlich als `{CORPUS_CODE}-{SPEAKER_MARKER}-{NNNN}` bzw. `{person_id}-{YYYY}-S{NN}` geführt.
- `speakers` aggregiert per `person_id`; Filter matchen existential über Sessions.
- Personenseiten zeigen alle Sessions derselben Person; eine Session kann nur zusätzlich fokussiert, nicht exklusiv isoliert werden.
- Native-Speaker-Vergleichsprofile bleiben personbasiert, aber strikt ein-Sessionig.
- Die dateibasierte Session-Metadatenstruktur bleibt die einzige aktive Laufzeitquelle für Research-Seiten.

## Abweichungen

- Keine bewusste Abweichung von der Spezifikation oder der Dev/Prod-Parität.

## Verifikation

- `scripts/session_setup/seed_dev_spanish_example_sessions.py` ausgeführt; 11 Sessions erfolgreich mit kanonischen IDs neu geschrieben.
- Fokussierter Testlauf: `python -m pytest tests/test_research_sessions.py` mit 4 bestandenen Tests.
- Loader-Snippet gegen reale Workspace-Daten ausgeführt: `sessions=12`, `people=9`, Mehrfach-Sessions für `ES-L-0001`, `ES-L-0002`, `ES-L-0003` bestätigt.
- Editor-Diagnostik für die geänderten Python-, Template- und JSON-Dateien ohne Fehler.

## Offene Punkte

- Kein echter HTTP- oder Browser-Smoke-Test über laufenden Flask-Server in diesem Run.
- Historische Run-Logs und historische Forschungsnotizen behalten alte IDs als Historie; aktive Referenzdokumente wurden dagegen aktualisiert.

## Nächste sinnvolle Schritte

- Person-/Session-Modell in künftigen Import- und Exportpipelines explizit weiterverwenden.
- Bei späterem Player-Ausbau Session-Fokus aus `recordings`/`speakers` konsistent bis in den echten Player durchreichen.