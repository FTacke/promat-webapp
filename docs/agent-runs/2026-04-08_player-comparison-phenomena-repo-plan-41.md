# Player / Comparison / Phenomena Repo-Plan

Datum: 2026-04-08

## Ziel

Den neuen Arbeitsbeschluss zu `player`, `comparison`, `phenomena` sowie Presets/Sets gegen die bindenden Specs und den aktuellen Repo-Stand pruefen und daraus einen repo-konkreten Umsetzungsplan fuer die naechsten Implementierungsruns ableiten.

## Consulted Sources

- `docs/plans/player_comparison_phenomena.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/spec/intake-workbook.md`
- Root `AGENTS.md`
- `docs/AGENTS.md`
- `app/AGENTS.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- `app/src/app/routes/public.py`
- `app/src/app/routes/public_content.py`
- `app/src/app/research_views.py`
- `app/src/app/research_sessions.py`
- `app/src/app/auth/models.py`
- `app/src/app/auth/services.py`
- `app/src/app/extensions/sqlalchemy_ext.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/tests/test_research_sessions.py`
- `data/config/research_player/README.md`
- `data/config/research_player/spanish/task_catalogs/wordlist.json`
- `data/config/research_player/spanish/task_catalogs/text.json`

## Geaenderte Bereiche

- `docs/plans/`
- `docs/spec/`
- `docs/agent-runs/`

## Wichtige Entscheidungen

- Der Repo-konkrete Folgeplan wurde als eigenes Planungsdokument unter `docs/plans/` abgelegt, damit der fachliche Arbeitsbeschluss und die technische Umsetzungsplanung getrennt bleiben.
- `research-access.md` und `research-player.md` wurden so angepasst, dass `comparison` und `phenomena` nicht mehr stillschweigend auf Player-Untermodes reduziert werden.
- `platform-data-files.md` wurde nur minimal geklaert: keine `mixed`-Player-Route, keine Umdeutung von `comparison`/`phenomena` zu alternativen Player-Pfaden.

## Abweichungen

- Keine Implementierung an App-Code, Datenbank oder UI vorgenommen.
- Der Audit hat eine bestehende Repo-Luecke bestaetigt: Research-Seiten sind aktuell fachlich als protected markiert, werden aber auf Route-Ebene noch nicht per JWT erzwungen.

## Verifikation

- Bindende Specs und Governance-Dateien gelesen.
- Routing-, Player-, Template-, JS-, Auth- und Migrationsdateien gelesen.
- Vorhandene Task-Kataloge und Tests gesichtet.
- Workspace-Suche nach `preset_id`, `set_id`, `phenomena_presets`, `player_config`, `comparison`, `phenomena` und API-Pfaden durchgefuehrt.

## Offene Punkte

- Die eigentliche Implementierungsreihenfolge zwischen Config-Foundation und Set-Backend muss im naechsten Run entschieden werden; beide Varianten sind im Plan begruendet.
- Die Frage, ob Research-HTML-Routen insgesamt auth-enforced werden oder ob zunaechst nur Set-API und set-gestuetzte Seiten Auth erzwingen, bleibt fuer den Implementierungsrun zu konkretisieren.

## Naechste sinnvolle Schritte

- `player_config.json` und `phenomena_presets.json` fuer Spanisch einfuehren.
- Danach das Postgres-Set-Schema samt API und Ownership-Checks aufbauen.
- Anschliessend `phenomena` und `comparison` als echte datengetriebene Seiten implementieren.
