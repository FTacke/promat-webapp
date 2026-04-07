# Research-Player Wordlist Compare Extension

Datum: 2026-04-06

## Ziel

Den bestehenden produktiven `wordlist`-Research-Player innerhalb derselben Route-Familie gezielt erweitern: Speaker-Wechsel im Player, desktop-only Compare, die Modi `single`, `manual` und `sequence`, gemeinsame Lautstärke- und Geschwindigkeitssteuerung sowie kompaktere, farbkonsistente Session-Karten.

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
- `app/static/css/00_tokens.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`

## Wichtige Entscheidungen

- Compare bleibt eine begrenzte Erweiterung derselben kanonischen Player-Route und nutzt nur Query-Kontext über `compare_session` und `compare_mode`, statt eine zweite Player-Familie einzuführen.
- Produktiv erweitert wird weiterhin nur `wordlist`; `text` und `interview` bleiben im gemeinsamen Task-Switch sichtbar, aber ohne Fake-Playback.
- `manual` Compare verwendet genau einen aktiven Speaker-Fokus und pausiert die jeweils andere Session, damit kein paralleles Dual-Audio als Default entsteht.
- `sequence` Compare spielt pro Item zuerst den Primärclip und danach den passenden Vergleichsclip derselben `item_id`.
- Compare bleibt desktop-only; kleinere Viewports degradieren auf dieselbe Primäransicht, ohne Route oder Player-State zu brechen.

## Abweichungen

- Keine Abweichung von aktiven Routing-, Runtime- oder Datenraumregeln.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py` → `30 passed`
- VS-Code-Problems-/Syntax-Prüfung für die geänderten Python-, Template-, JS- und CSS-Dateien ohne gemeldete Fehler
- Expliziter Regression-Fix nach erstem Testlauf: Jinja-Dict-Zugriff auf `primary['items']` statt `.items`

## Offene Punkte

- Browserseitiges Verhalten für echte Compare-Wiedergabe ist derzeit über Server-Tests und strukturelles HTML validiert, aber nicht über einen dedizierten Frontend-Test-Runner automatisiert.
- `text` besitzt weiterhin noch keinen produktiven Compare- oder Playback-Renderer.
- Für spätere Forschungszugänge muss die geschützte Media-Auslieferung weiterhin mit produktiven Auth-Regeln zusammengedacht werden.

## Nächste sinnvolle Schritte

- Produktiven `text`-Renderer auf derselben Player-Basis aufsetzen und erst dann die Compare-Regeln für `text` real aktivieren.
- Falls benötigt, einen kleinen Browser-basierten Smoke-Test für `manual` und `sequence` Compare ergänzen.
- Compare aus `recordings` und später `comparison` mit kuratierten Vorbelegungen derselben Query-Kontexte starten.