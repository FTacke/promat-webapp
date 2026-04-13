# Set-Modell Phase 5

Datum: 2026-04-13

## Ziel

Die nächste Architekturphase nach dem produktiven Phase-4-Split umsetzen: verbliebene Schattenpfade und Kompatibilitätsprojektionen der Set-API entfernen, sodass workbench-spezifischer Zustand im produktiven JSON-Vertrag nur noch unter `workbench_state` geführt wird, ohne `comparison`, `phenomena` oder `player` zu regressieren.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/research-player.md`
- `docs/spec/intake-workbook.md`
- `docs/plans/architecture_plan.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- `app/src/app/research_sets.py`
- `app/src/app/routes/research_api.py`
- `app/static/js/pages/research-comparison.js`
- `app/src/app/research_views.py`
- `app/src/app/research_phenomena_views.py`
- `app/tests/test_research_sets.py`
- `app/tests/test_research_comparison.py`
- `app/tests/test_research_phenomena.py`
- `app/tests/test_research_player_set_context.py`

## Geänderte Bereiche

- `app/src/app/research_sets.py`
- `app/src/app/routes/research_api.py`
- `app/static/js/pages/research-comparison.js`
- `app/tests/test_research_sets.py`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/plans/architecture_plan.md`
- `docs/agent-runs/2026-04-13_set-model-phase5-103.md`
- `tmp/ui-qa/2026-04-13-set-model-phase5-103/capture_set_model_phase5_103.py`
- finale Screenshot-, Text- und Metrik-Artefakte unter `tmp/ui-qa/2026-04-13-set-model-phase5-103/`

## Wichtige Entscheidungen

- Die produktive Set-API liefert workbench-spezifische Zustände nicht mehr parallel als Top-Level-Felder aus; `preferred_task`, `comparison_view_task` und Session-Auswahl bleiben fachlich ausschließlich Teil von `workbench_state`.
- Die Set-API akzeptiert für diese Werte keine Top-Level-Alias-Eingaben mehr. Statt stiller Fallbacks werden alte Alias-Formen jetzt explizit mit klarer Fehlermeldung zurückgewiesen.
- Die dedizierte Route `/api/research/sets/{set_id}/sessions` bleibt als spezialisierter Mutationspfad für die owner-gebundene Session-Auswahl bestehen; sie ersetzt keine kanonische Vollform des Set-JSONs.
- `comparison` liest gespeicherte Sets nicht mehr defensiv aus alten Top-Level-Kompatibilitätsfeldern, sondern normalisiert nur noch `workbench_state`.
- `save-as` kopiert den aktuellen Workbench-State weiterhin vollständig mit, damit produktive Flows stabil bleiben, obwohl die Alias-Projektionen entfernt wurden.

## Abweichungen

- Keine Abweichung von aktiver Spec, Dev/Prod-Parität oder der Phase-5-Zielarchitektur.
- Root- und scoped-`AGENTS.md` sowie `.github`-Instruktionsdateien wurden geprüft, mussten für diese Cleanup-Phase aber nicht geändert werden.
- Im Selenium-Lauf traten nur bekannte Edge-Tracking-Prevention-Warnungen gegen das externe Bootstrap-Icons-CDN auf; es gab keinen produktspezifischen Browserfehler.

## Verifikation

- Statische Fehlerprüfung der geänderten Python-, JS- und Doku-Dateien via VS-Code-Problems: ohne neue Fehler.
- Fokussierte Regressionen:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sets.py app/tests/test_research_comparison.py app/tests/test_research_phenomena.py app/tests/test_research_player_set_context.py -q`
  - Ergebnis: `73 passed`.
- Live-Server neu über den kanonischen Dev-Start aufgesetzt:
  - `scripts/dev-start.ps1`
  - dabei wurde die idempotente PostgreSQL-Migrationskette inklusive `0005_split_research_set_workbench_state.sql` erfolgreich erneut angewendet.
- Reale Browser-QA via Selenium/Edge gegen `127.0.0.1:8000` mit `tmp/ui-qa/2026-04-13-set-model-phase5-103/capture_set_model_phase5_103.py`.
- Final erzeugte Artefakte unter `tmp/ui-qa/2026-04-13-set-model-phase5-103/`, unter anderem:
  - `gate_comparison_de.png`
  - `comparison_de_auth.png`
  - `comparison_en_auth.png`
  - `phenomena_overview_de_auth.png`
  - `phenomena_overview_en_auth.png`
  - `player_de_set_context_auth.png`
  - `player_en_set_context_auth.png`
  - `metrics.json`
- Final verifizierte Browser- und API-Invarianten laut `metrics.json` und Textdumps:
  - Login-Gate auf `comparison` erhält den vollständigen `next`-Pfad mit `set_id` und `task`
  - gespeichertes QA-Set ist in `comparison`, `phenomena` und `player` sichtbar
  - versteckter Draft bleibt in den sichtbaren Set-Listen verborgen
  - rohe `set_id` erscheint nicht als sichtbarer UI-Text im Comparison-Arbeitsbereich
  - der live geladene API-Response für das aktive Set enthält `workbench_state`, aber keine Top-Level-Aliasfelder `preferred_task`, `comparison_view_task` oder `sessions`

## Offene Punkte

- Die Cleanup-Phase entfernt die produktiven Top-Level-Aliasfelder aus Set-Response und Set-Create/Patch-Input. Die dedizierte Sessions-Route bleibt bewusst als spezialisierter Mutationspfad bestehen und könnte später nur dann weiter umgebaut werden, wenn ein klar besserer kanonischer Write-Vertrag benötigt wird.
- Die Live-Browser-QA seedet ihr QA-Set weiterhin gegen das erste reale spanische Preset; spätere Preset-Umbenennungen müssen deshalb das QA-Skript oder seine dynamische Auflösung mitziehen.

## Nächste sinnvolle Schritte

- Phase 6 aus dem Architekturplan nur separat beauftragen und bewusst unabhängig vom jetzt bereinigten Set-Vertrag umsetzen.
- Falls später weitere Research-API-Bereinigungen anstehen, dieselbe Kombination aus expliziter Fehlerprüfung, fokussierten API-Regressionen und Live-Browser-Checks beibehalten.