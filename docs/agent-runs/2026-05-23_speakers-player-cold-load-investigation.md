# Speakers -> Player Cold-Load Investigation

## Ziel

- kalten Klick von Speakers auf Player gezielt zerlegen
- Serverzeit, DB-Anteil, Template-Rendern und Browser-Anteil trennen
- nur kleine sichere Maßnahmen umsetzen, wenn der Hotspot klar ist

## Befund

- Player-Links auf Speakers sind normale Anchors; kein clientseitiges Router-Blocking.
- Audio war nicht das Problem: vor Interaktion blieben Audio-Requests bei `0`.
- Auf dem kalten ersten Player-Request nach Reload dominierte `load_task_ready_sessions(...)` den Serverpfad deutlich.
- DB war kein Haupttreiber: stabil `8` Queries, warm nur wenige Millisekunden, auch kalt klar kleiner als der Runtime-Dateipfad.

## Umsetzung

- opt-in Profiling für die Player-Route ergänzt
  - Route, Build, Render, DB und Runtime-Teilschritte als Header messbar gemacht
- `load_task_ready_sessions(...)` pro Sprache/Task gecacht
- internen `X-Promat-Player-Prewarm`-Pfad für die Player-Route ergänzt
  - baut Runtime-Warm-up, rendert aber kein HTML und antwortet mit `204`
- kleines Speakers-Page-Modul ergänzt
  - startet Prewarm bei Hover, Fokus und Touch auf Player-Links
- fokussierten Regressionstest für den Prewarm-HTTP-Pfad ergänzt

## Checks

- Live-Playwright-Messung des echten Speakers -> Player-Klickpfads gegen `http://127.0.0.1:8000`
- Profiling-Headers auf kaltem und warmem Player-Request geprüft
- Hover-Prewarm plus nachfolgender echter Klick live gemessen
- `pytest tests/test_research_sessions.py -q -k player_prewarm_request_warms_route_without_rendering_body`
- `pytest tests/test_research_player_set_context.py -q`

## Ergebnis

- kalter erster Player-Request nach Reload: `route ~= 6359 ms`, davon `ready_sessions ~= 5341 ms`
- zweiter Request im selben Prozess: `route ~= 50 ms`
- Speakers-Hover-Prewarm: `204` nach `~261 ms`
- anschließender echter Klick: `route ~= 92 ms`, `responseStart ~= 86.5 ms`, `ready_sessions ~= 0 ms`

## Restgrenze

- Nach dem Server-Fix bleibt die volle Shell-Basis des Vollseiten-Reloads sichtbar: viele Stylesheets plus Player-JS werden weiterhin auf der Zielseite geladen.
- Wenn dieser Rest noch adressiert werden soll, ist das ein separater globaler Shell-/Asset-Track und kein Player-spezifischer Datenbank- oder Query-Fix.