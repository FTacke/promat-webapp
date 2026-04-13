# Research Capabilities Phase 2

Datum: 2026-04-13

## Ziel

Phase 2 aus `docs/plans/architecture_plan.md` umsetzen: eine zentrale, kanonische Research-Capability-Schicht für Tasks, Seiten, Access, Compare, Set-Filter, Render-Modi und corpus-spezifische Surface-Modes einführen, bestehende verteilte Capability-Literale auf diese Schicht routen und dabei Phase-1-Access-Regeln sowie produktive Player-, Comparison- und Phenomena-Flows stabil halten.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/spec/intake-workbook.md`
- `docs/plans/architecture_plan.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `docs/runbooks/ui-change-workflow.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- neues kanonisches Capability-Modul in `app/src/app/research_capabilities.py`
- Capability-Wiring in `app/src/app/research_access.py`, `app/src/app/research_sessions.py`, `app/src/app/research_presets.py`, `app/src/app/research_sets.py`, `app/src/app/research_views.py`, `app/src/app/research_phenomena_views.py`, `app/src/app/routes/public.py`, `app/src/app/routes/public_content.py`, und `app/src/app/config/data_conventions.py`
- fokussierte Capability-Regressionen in `app/tests/test_research_capabilities.py` sowie betroffene Research-Suites unter `app/tests/`
- aktive Spezifikation in `docs/spec/research-capabilities.md`, `docs/spec/platform-data-files.md`, `docs/spec/research-access.md`, `docs/spec/research-player.md`
- Governance und Instructions in `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/repo.instructions.md`, `docs/runbooks/ui-change-workflow.md`
- Planstatus in `docs/plans/architecture_plan.md`
- Browser-QA-Skript und Artefakte in `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/`

## Wichtige Entscheidungen

- Die aktive Capability-Source-of-Truth liegt jetzt normativ in `docs/spec/research-capabilities.md` und im kanonischen Implementierungsspiegel `app/src/app/research_capabilities.py`.
- Research-Access bleibt corpus-generic; Surface-Modes beschreiben nur productive versus placeholder readiness und schwächen die Auth-Grenze nie ab.
- Der Router leitet productive-vs-placeholder-Verhalten über Capability-Metadaten statt über spanischspezifische Sonderzweige ab.
- `interview` bleibt ein expliziter begrenzter Sonderfall: sichtbar im Capability-Vertrag, aber nicht compare- oder set-filter-fähig und nicht in den aktuellen produktiven unified Player hineingezwungen.
- Für Materiallabels darf die corpus-spezifische Catalog-`display_label` nur die deutsche Workbench-Beschriftung übersteuern; englische Labels bleiben aus dem zentralen bilingualen Capability-Vertrag ableitbar.
- Die geschützten Placeholder-Seiten für nicht-spanische Korpora wurden bei der Browser-QA als bilinguale reale Surface behandelt; dabei entdeckte deutsche Placeholder-Hardcodings in der englischen Route wurden im selben Run auf die Translation-Layer umgestellt.

## Abweichungen

- Keine beabsichtigte Abweichung von der aktiven Spezifikation.
- Im Selenium-Lauf meldete Edge nur bekannte Tracking-Prevention-Warnungen gegen das externe Bootstrap-Icons-CDN; es trat kein produktspezifischer Browserfehler auf.

## Verifikation

- fokussierte Tests: `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_capabilities.py app/tests/test_research_presets.py app/tests/test_research_sessions.py app/tests/test_research_comparison.py app/tests/test_research_phenomena.py app/tests/test_research_player_set_context.py`
- Ergebnis: `204 passed`
- Live-Listener auf `127.0.0.1:8000` geprüft; stale globale und Workspace-`src.app.main`-Prozesse wurden vor dem finalen QA-Lauf beendet und der kanonische Dev-Server über `scripts/dev-start.ps1` frisch gestartet.
- Browser-QA via Selenium/Edge gegen reale Routen mit `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/capture_research_capabilities_phase2_101.py`
- Final erzeugte Screenshot-Artefakte unter anderem:
  - `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/gate_spanish_comparison_de.png`
  - `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/comparison_spanish_de_auth.png`
  - `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/comparison_spanish_en_auth.png`
  - `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/phenomena_spanish_de_auth.png`
  - `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/phenomena_spanish_en_auth.png`
  - `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/player_spanish_de_auth.png`
  - `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/player_spanish_en_auth.png`
  - `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/comparison_english_en_placeholder_auth.png`
- `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/metrics.json` bestätigt:
  - Login-Gate mit erhaltenem `next` auf einer geschützten spanischen Comparison-Route
  - produktive Player-, Comparison- und Phenomena-Routen für `spanish` in `de` und `en`
  - geschützte Placeholder-Comparison für den zweiten Korpus `english` nach Login ohne productive Comparison-Controls

## Offene Punkte

- Phase 3 aus dem Architekturplan, also der tiefere interne Player-Umbau, ist weiterhin offen und bewusst nicht Teil dieses Runs.
- Nicht-spanische Research-Workbenches bleiben protected placeholders; ihre spätere productive Ausgestaltung muss weiterhin zuerst im Capability-Vertrag und dann in den betroffenen Specs und Consumern ausgerollt werden.

## Nächste sinnvolle Schritte

- Phase 3 nur separat beauftragen und dabei konsequent auf der jetzt vorhandenen Capability-Schicht aufsetzen.
- Bei weiteren Research-Workbench-Änderungen denselben Selenium-QA-Pfad unter `tmp/ui-qa/2026-04-13-research-capabilities-phase2-101/` fortschreiben statt neue Einmalskripte zu bauen.