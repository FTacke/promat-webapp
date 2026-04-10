# Research Sets Backend

Datum: 2026-04-08

## Ziel

Die serverseitige Backend-Grundlage fuer Research-Sets einfuehren: gemeinsames Draft/Saved-Modell in PostgreSQL, owner-gebundene JSON-API, strenge Validierung gegen Presets, Task-Kataloge und Session-Bestand sowie eine reale Cleanup-Grundlage fuer ablaufende Drafts.

## Consulted Sources

- `docs/plans/player_comparison_phenomena.md`
- `docs/plans/player_comparison_phenomena_repo_implementation_plan.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `app/src/app/auth/models.py`
- `app/src/app/auth/services.py`
- `app/src/app/extensions/sqlalchemy_ext.py`
- `app/src/app/research_presets.py`
- `app/src/app/research_sessions.py`
- `app/src/app/routes/auth.py`
- `app/src/app/routes/public.py`
- `app/migrations/0001_create_auth_schema_postgres.sql`
- `app/migrations/0002_create_analytics_tables.sql`

## Geaenderte Bereiche

- `app/migrations/`
- `app/src/app/`
- `app/src/app/routes/`
- `app/tests/`
- `docs/spec/`
- `docs/agent-runs/`

## Eingefuehrte DB-Objekte

- `research_sets`
- `research_set_items`
- `research_set_sessions`

## Eingefuehrte API-Endpunkte

- `POST /api/research/sets`
- `GET /api/research/sets/<set_id>`
- `PATCH /api/research/sets/<set_id>`
- `PUT /api/research/sets/<set_id>/items`
- `PUT /api/research/sets/<set_id>/sessions`
- `POST /api/research/sets/<set_id>/save-as`

## Wichtige Entscheidungen

- Drafts und Saved Sets laufen ueber exakt dasselbe technische Modell; der Lifecycle wird nur ueber `state` plus `expires_at` unterschieden.
- Ownership wird ausschliesslich aus dem authentifizierten JWT-User abgeleitet; kein Endpunkt akzeptiert `owner_user_id` aus dem Request.
- Set-Items bleiben auf `wordlist` und `text` beschraenkt und werden ueber die bestehende file-backed Preset-/Task-Katalog-Logik validiert.
- Session-Referenzen werden weiterhin gegen den dateibasierten Research-Session-Bestand validiert, nicht gegen ein neues DB-Schattenmodell.
- `save-as` erzeugt ein neues `saved`-Set mit expliziter kopierter Item- und Sessionliste statt das Draft still umzuwandeln.

## Bewusst nicht in diesem Run integriert

- Keine vollwertige `phenomena`-UI
- Keine vollwertige `comparison`-Workbench
- Keine grosse `player`-Integration von `set_id`
- Keine allgemeine JWT-Erzwingung fuer alle Research-HTML-Routen

## Offene Punkte

- Die neue Set-API ist sauber auth-gebunden; die allgemeine Frage nach JWT-Schutz fuer alle Research-HTML-Routen bleibt bewusst ein Folgepunkt.
- Die naechste UI-Phase soll `phenomena` ueber `preset_id` und `set_id` an dieses Backend anschliessen.

## Naechster sinnvoller Schritt

- `phenomena` als echte editierbare Preset-Seite bauen, die Presets in Draft-Sets materialisiert und danach nach `comparison` oder `player` weiterleitet.