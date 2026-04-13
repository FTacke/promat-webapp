# Set-Modell Phase 4

Datum: 2026-04-13

## Ziel

Die nächste Architekturphase nach der bereits produktiven Player-Runtime-Konsolidierung umsetzen: den kanonischen owner-gebundenen Set-Kern von workbench-spezifischem Zustands- und Präferenzverhalten trennen, ohne die produktiven Flows in `phenomena`, `comparison` und `player` zu regressieren.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/spec/research-capabilities.md`
- `docs/plans/architecture_plan.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_sets.py`
- `app/src/app/routes/research_api.py`
- `app/src/app/research_views.py`
- `app/src/app/research_phenomena_views.py`
- `app/static/js/pages/research-comparison.js`
- `app/migrations/0003_create_research_sets.sql`
- `app/migrations/0004_extend_research_sets_for_phenomena_editor.sql`
- `app/scripts/apply_auth_migration.py`
- `app/tests/test_research_sets.py`
- `app/tests/test_research_comparison.py`
- `app/tests/test_research_phenomena.py`
- `app/tests/test_research_player_set_context.py`

## Geänderte Bereiche

- `app/src/app/research_sets.py`
- `app/src/app/routes/research_api.py`
- `app/src/app/research_views.py`
- `app/src/app/research_phenomena_views.py`
- `app/static/js/pages/research-comparison.js`
- `app/migrations/0005_split_research_set_workbench_state.sql`
- `app/scripts/apply_auth_migration.py`
- `app/tests/test_research_sets.py`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/plans/architecture_plan.md`
- `tmp/ui-qa/2026-04-13-set-model-phase4-102/capture_set_model_phase4_102.py`
- `tmp/ui-qa/2026-04-13-set-model-phase4-102/metrics.json`
- finale Screenshot- und Textartefakte unter `tmp/ui-qa/2026-04-13-set-model-phase4-102/`

## Wichtige Entscheidungen

- Der kanonische Set-Kern bleibt in `research_sets`, enthält aber nur noch durable Set-Semantik: Identität, Owner, Lifecycle, Label oder Note, Preset-Provenienz und explizite Item-Referenzen.
- Workbench-spezifische Zustände liegen jetzt serverseitig in einem separaten owner-gebundenen Submodell `workbench_state`; aktuell umfasst es `preferred_task`, `comparison_view_task` und die Comparison-Session-Auswahl.
- Die bestehende API-Routefamilie bleibt erhalten, aber `workbench_state` ist jetzt die kanonische Request- und Response-Struktur. Top-Level-Felder bleiben nur noch als Kompatibilitätsprojektion erhalten.
- `save-as` kopiert weiterhin den aktuellen Workbench-Zustand mit, damit produktive Flows stabil bleiben, obwohl diese Daten nicht mehr Teil des Set-Kerns sind.
- Die Postgres-Migration `0005_split_research_set_workbench_state.sql` ist idempotent aufgebaut, weil `app/scripts/apply_auth_migration.py` die komplette SQL-Kette bei jedem Dev-Start erneut ausführt.

## Abweichungen

- Keine Abweichung von der aktiven Spec oder Dev/Prod-Parität im Zielmodell.
- Es waren keine zusätzlichen Änderungen an Root- oder scoped-`AGENTS.md` bzw. den `.github`-Instruktionsdateien nötig, weil die geänderte aktive Regel vollständig in `docs/spec/` verankert ist und dort aktualisiert wurde.
- Im ersten Selenium-Lauf trat einmalig ein Edge-Netzwerkfehler beim Laden von `static/css/10_typography.css` auf; ein vollständiger Wiederholungslauf war danach sauber. Die finalen Artefakte stammen aus dem sauberen Wiederholungslauf.

## Verifikation

- Statische Fehlerprüfung der geänderten Python- und JS-Dateien via VS-Code-Problems: ohne neue Fehler.
- Fokussierte Regressionen:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sets.py app/tests/test_research_comparison.py app/tests/test_research_phenomena.py app/tests/test_research_player_set_context.py`
  - Ergebnis: `69 passed`.
- Live-Server neu über den kanonischen Dev-Start aufgesetzt:
  - `scripts/dev-start.ps1`
  - dabei wurde die neue `0005_split_research_set_workbench_state.sql` erfolgreich angewendet.
- Health-Check erfolgreich auf `http://127.0.0.1:8000/health`.
- Reale Browser-QA via Selenium/Edge gegen `127.0.0.1:8000` mit dem Skript `tmp/ui-qa/2026-04-13-set-model-phase4-102/capture_set_model_phase4_102.py`.
- Final erzeugte Artefakte unter `tmp/ui-qa/2026-04-13-set-model-phase4-102/`, unter anderem:
  - `gate_comparison_de.png`
  - `comparison_de_auth.png`
  - `comparison_en_auth.png`
  - `phenomena_overview_de_auth.png`
  - `phenomena_overview_en_auth.png`
  - `phenomena_set_editor_de_auth.png`
  - `player_de_set_context_auth.png`
  - `player_en_set_context_auth.png`
  - `metrics.json`
- Final verifizierte Browser-Invarianten laut `metrics.json` und Textdumps:
  - gespeichertes QA-Set ist in `comparison`, `phenomena` und `player` sichtbar
  - versteckter Draft bleibt in den sichtbaren Set-Listen verborgen
  - rohe `set_id` wird im Comparison-Arbeitsbereich nicht als sichtbarer Text ausgegeben
  - Login-Gate auf `comparison` erhält den vollständigen `next`-Pfad mit `set_id` und `task`
  - keine produktspezifischen Browserfehler im finalen Wiederholungslauf; nur bekannte Edge-Tracking-Prevention-Warnungen gegen das externe Bootstrap-Icons-CDN

## Offene Punkte

- Die API liefert die alten Top-Level-Felder `preferred_task`, `comparison_view_task` und `sessions` noch als Kompatibilitätsprojektion neben `workbench_state`; fachlich ist `workbench_state` bereits kanonisch, aber die Alias-Projektion kann in einer späteren Bereinigungsphase entfernt werden.
- Die Live-Spanisch-Konfiguration nutzt derzeit kein Testfixture-Preset wie `starter_preset`; Browser-QA-Skripte müssen deshalb weiterhin das erste reale verfügbare Preset dynamisch auflösen.

## Nächste sinnvolle Schritte

- Die verbliebenen Architekturphasen aus `docs/plans/architecture_plan.md` in derselben Spec-first-Reihenfolge fortführen.
- In einer späteren Cleanup-Phase die verbliebenen Top-Level-Kompatibilitätsfelder aus der Set-API entfernen, sobald keine internen Consumer mehr davon abhängen.
