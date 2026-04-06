# Research-Player Wordlist MVP

Datum: 2026-04-06

## Ziel

Den ersten echten Research-Player-MVP für den bereits produktionsreifen `wordlist`-Pfad direkt in der App implementieren, inklusive echter Session-Artefaktladung, Playback, Item-Sync, Split-Download und ehrlicher Fallback-Zustände.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/src/app/routes/public.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`

## Wichtige Entscheidungen

- Der erste produktive Player bleibt auf der kanonischen Route `/{ui_lang}/research/{corpus_language}/player/{session_id}/{task}` und nutzt keine zweite task-spezifische Player-Familie.
- Geschützte Session-Audioauslieferung bleibt unter derselben Player-Familie und läuft über App-Routen für `audio.mp3` sowie `items/{item_id}.mp3`, statt `data/` statisch zu veröffentlichen.
- `wordlist` ist im aktuellen MVP produktiv; `text` und `interview` bleiben im gemeinsamen Task-Switch sichtbar, aber bewusst als ehrliche Unavailable-States ohne Fake-Renderer.
- Nicht verarbeitbare oder unvollständige `wordlist`-Sessions liefern keinen Fehler-Page, sondern einen expliziten Fallback-Zustand auf derselben Player-Oberfläche.

## Abweichungen

- Keine Abweichung von den aktiven Routing-, Runtime- oder Datenraumregeln.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py` → `28 passed`
- Repo-realistischer Flask-Testclient-Smoketest gegen echte spanische Dev-Daten:
  - `recordings` enthält Player-Links mit `source=recordings`
  - `speakers` enthält Player-Links mit `source=speakers`
  - `profile` enthält Player-Links mit `source=profile`
  - reale verarbeitbare Session `ES-L-0001-2026-S01` rendert den interaktiven `wordlist`-Player
  - reale nicht verarbeitbare Session `ES-L-0002-2026-S01` rendert den expliziten Fallback-Zustand

## Offene Punkte

- `text` und `interview` besitzen im gemeinsamen Player noch keine produktiven Renderer.
- Für spätere echte Zugangskontrolle muss geprüft werden, wie geschützte Audioauslieferung im produktiven Auth-Kontext abgesichert wird.
- Vergleichsmodus, Presets und `focus_item`/`focus_segment`-Query-Kontext sind in diesem MVP noch nicht umgesetzt.

## Nächste sinnvolle Schritte

- `text` als nächsten produktiven Task-Modus in denselben Player integrieren.
- Auth- und Berechtigungsregeln für Player-Media-Routen explizit an den produktiven Forschungszugang anbinden.
- Vergleichsmodus für kompatible `wordlist`-Sessions auf Basis der jetzt vorhandenen gemeinsamen Player-Struktur ergänzen.