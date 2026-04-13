# Research Access Phase 1

Datum: 2026-04-13

## Ziel

Phase 1 aus `docs/plans/architecture_plan.md` umsetzen: unter `/{ui_lang}/research/{corpus}` nur `design` öffentlich lassen, alle anderen Research-Seiten sowie Detail- und Medienrouten vor dem Rendern authentifizieren, dabei den Login-Rücksprung erhalten und die Player-Set-Sichtbarkeit für kuratierte Presets, gespeicherte Sets und den bereits aktiven Draft absichern.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `docs/spec/research-player.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- zentrales Research-Access-Modul in `app/src/app/research_access.py`
- corpus-scoped Research-Routing in `app/src/app/routes/public.py`
- öffentliche Placeholder-Page-Daten in `app/src/app/routes/public_content.py`
- Research-Workbench-Builder in `app/src/app/research_views.py` und `app/src/app/research_phenomena_views.py`
- fokussierte Research-Regressionen in `app/tests/`
- aktive Spezifikation und Governance in `docs/spec/`, Root- und Scoped-`AGENTS.md` sowie `.github/instructions/`
- Browser-QA-Artefakte in `tmp/ui-qa/2026-04-13-research-access-phase1-100/`

## Wichtige Entscheidungen

- Research-Zugriff wird corpus-generic zentralisiert: `design` bleibt die einzige öffentliche corpus-scoped Research-Seite.
- `/{ui_lang}/research/{corpus}` leitet auf `design` um, statt einen zweiten öffentlichen Research-Hub zu rendern.
- Geschützte Research-Seiten, Detailrouten und Player-Medienrouten prüfen Authentifizierung an der Route-Grenze und rendern die Workbench nicht vorab.
- Die Player-Set-Auswahl zeigt kuratierte Presets, gespeicherte Custom-Sets und nur den bereits aktiven Draft-Kontext; andere Drafts bleiben verborgen.

## Abweichungen

- Keine beabsichtigte Abweichung von der aktiven Spezifikation.
- Die Live-Browser-QA musste nach Bereinigung stale `src.app.main`-Prozesse erneut gegen den kanonischen Dev-Start ausgeführt werden; das war ein Runtime-Thema, keine Soll-Abweichung.

## Verifikation

- fokussierte Tests: `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sessions.py tests/test_research_comparison.py tests/test_research_phenomena.py tests/test_research_player_set_context.py`
- Ergebnis: `182 passed`
- Live-Listener geprüft auf `127.0.0.1:8000`, geschützte Route per HTTP gegen Login-Redirect verifiziert
- Browser-QA mit `tmp/ui-qa/2026-04-13-research-access-phase1-100/capture_research_access_phase1_100.py`
- erzeugte Screenshots u. a.:
  - `design_spanish_de_public.png`
  - `design_english_en_public.png`
  - `gate_spanish_comparison_de.png`
  - `comparison_spanish_de_auth.png`
  - `gate_english_speakers_en.png`
  - `speakers_english_en_auth.png`
  - `player_set_sources_de.png`
  - `player_set_sources_en.png`
  - `player_active_draft_de.png`
- QA-Metriken in `tmp/ui-qa/2026-04-13-research-access-phase1-100/metrics.json` bestätigen:
  - `design` öffentlich in `de` und `en`
  - Login-Gate mit erhaltenem `next`
  - Post-Login-Render der geschützten Routen
  - kuratierte Presets plus gespeicherte Sets im Player
  - aktiver Draft nur im aktiven Kontext sichtbar

## Offene Punkte

- Kein offener Funktionsblocker in Phase 1.
- Die Browser-QA stützt sich auf den aktuellen Spanish-Preset-Bestand aus `phenomena_presets.json`; spätere Preset-Umbenennungen sollten die QA-Datei oder ihre Live-Config-Ableitung mitziehen.

## Nächste sinnvolle Schritte

- Phase 2 aus dem Architekturplan nur nach separater Beauftragung umsetzen.
- Falls weitere Access-Änderungen folgen, denselben Live-Listener-Check als festen QA-Schritt beibehalten.