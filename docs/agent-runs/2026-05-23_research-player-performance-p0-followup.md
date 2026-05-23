# Research Player Performance P0 Follow-up

## Ziel

- P0-Maßnahmen aus der Research-Player-Diagnose umsetzen
- doppelte Player-Timingdaten reduzieren
- Comparison-Boot ohne frühe Set-API-Kette starten
- Audio-Preload für den Player entschärfen, ohne Item-Playback zu brechen

## Umsetzung

- `app/static/js/pages/research-comparison.js`
  - impliziten Default-Workspace clientseitig aufgebaut
  - initialen Preset-Reload entfernt
- `app/src/app/research_player_runtime.py`
  - Token-Segmente um Timingwerte für das DOM ergänzt
- `app/templates/pages/research_player.html`
  - Token-Timings als `data-*`-Attribute gerendert
  - Hauptaudio auf `preload="none"` umgestellt
- `app/src/app/research_views.py`
  - Player-Client-State für `text`/`wordlist` auf DOM-Sync umgestellt
- `app/static/js/pages/research-player.js`
  - Sync-Items aus dem DOM aufgebaut
  - Metadaten bei Item-Seeks bei Bedarf nachgeladen
- `app/tests/test_research_player_set_context.py`
  - kompakteren Player-State und `preload="none"` abgesichert

## Checks

- `pytest app/tests/test_research_player_set_context.py -q`
- `pytest app/tests/test_research_comparison.py -q`
- Live-Playwright-Smoke-Run gegen `http://127.0.0.1:8010`
- `get_errors` auf den geänderten JS-, Template- und Python-Dateien

## Ergebnis

- Player-`text`-State von `72.2 KB` auf `632 Bytes` reduziert
- Player-HTML auf der gemessenen Route von `223.8 KB` auf ca. `176.5 KB` reduziert
- frühe Player-Audio-Requests auf `0` gesenkt
- authentifizierter Comparison-Load ohne `set_id` macht beim ersten Aufbau `0` Requests auf `/api/research/sets`