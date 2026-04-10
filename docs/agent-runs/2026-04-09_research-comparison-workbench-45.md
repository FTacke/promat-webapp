# Vergleichs-Workbench als echte Set-Seite

Datum: 2026-04-09

## Ziel

Die bestehende Research-Seite `comparison` von Platzhalterinhalt auf eine echte set-basierte Mehrfach-Workbench heben, ohne den Player in eine zweite Comparison-App umzubauen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/plans/player_comparison_phenomena.md`
- `docs/plans/player_comparison_phenomena_repo_implementation_plan.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/src/app/routes/public.py`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`

## Wichtige Entscheidungen

- `comparison` bleibt als HTML-Seite öffentlich renderbar, aber `set_id`-Laden, Draft-Erzeugung, Session-Mutationen und View-Filter-Persistenz laufen owner-gebunden über `/api/research/sets`.
- Item-Kuration bleibt in `phenomena`; `comparison` zeigt und verwendet das aktive Set, wird aber kein zweiter Item-Editor.
- Reduzierte Comparison-Wiedergabe basiert auf Split-Clips über die bestehende Player-Item-Routefamilie statt auf einem zweiten Audio-API-System.
- Die geschützte Artifact-Auflösung wurde minimal von `wordlist` auf task-basierte `wordlist`-/`text`-Bundles erweitert, ohne den produktiven Player-Renderer für `text` vorwegzunehmen.
- Player-Handoffs tragen nun optional `set_id`, `preset_id` und `focus_item`, aber die tiefe set-basierte Player-Interpretation bleibt bewusst außerhalb dieses Runs.

## Abweichungen

- Keine Abweichung von den aktiven Specs; die Specs wurden im selben Run auf den jetzt produktiven `comparison`-Stand nachgezogen.

## Verifikation

- Statische Fehlerprüfung der geänderten Python-, JS-, CSS- und Template-Dateien über den VS-Code-Fehlerdienst.
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_comparison.py tests/test_research_phenomena.py tests/test_research_sets.py tests/test_research_sessions.py`
- Ergebnis: `52 passed`

## Offene Punkte

- Der session-zentrierte Player rendert weiterhin nur `wordlist` produktiv; `text`-Handoffs aus `comparison` landen bewusst noch im bestehenden ehrlichen Player-Fallback.
- `comparison` kann leere Drafts und Session-Konfigurationen starten, aber die Item-Kuration erfolgt weiterhin über `phenomena`.
- Es gibt noch keine sichtbare "save as new set"-Aktion in der `comparison`-UI.

## Nächste sinnvolle Schritte

- `set_id` im Player taskbezogen wirklich als sichtbaren Item-Filter interpretieren.
- Für `text` eine echte Player-Renderer-Stufe ergänzen, damit `comparison`-Handoffs dort nicht mehr nur in den Fallback laufen.
- Optional eine sichtbare "Als neues Set speichern"-Aktion auf `comparison` ergänzen.