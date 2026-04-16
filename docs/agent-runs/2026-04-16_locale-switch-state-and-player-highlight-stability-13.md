# Locale Switch State And Player Highlight Stability

Datum: 2026-04-16

## Ziel

Zwei UX-relevante Zustandsfehler systemisch beheben: Der DE/EN-Sprachwechsel darf aktive Research-Workbench-Zustaende nicht mehr zuruecksetzen, und der Text-Player darf an Satzgrenzen niemals kurz das globale letzte Satzitem als aktiv markieren.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `app/templates/partials/_top_app_bar.html`
- `app/static/js/modules/navigation/app-bar.js`
- `app/static/js/pages/research-comparison.js`
- `app/static/js/pages/research-player.js`
- `app/src/app/__init__.py`
- `app/tests/test_research_sessions.py`
- `app/tests/test_research_comparison.py`

## Geaenderte Bereiche

- zentrale Topbar-/Language-Switch-Logik fuer live aus der aktuellen URL berechnete Locale-Zielpfade
- Comparison-Workbench-URL-Synchronisierung fuer stabile Draft-/Filter-/Task-Zustaende
- Player-Highlight-Helfer fuer deterministische Satzitem-Aufloesung ohne globalen Last-Item-Fallback
- fokussierte Python- und Node-Regressionen fuer URL-, Workbench- und Highlight-Helfer
- aktive Spec fuer locale-stabile Workbench-State-Werte und Text-Player-Grenzverhalten

## Wichtige Entscheidungen

- Die Sprachwechsel-Links verlassen sich nicht mehr auf serverseitig initialisierte Hrefs, die nach `history.replaceState(...)` stale sein koennen; sie werden zentral aus der aktuellen Live-URL berechnet und bei URL-Aenderungen automatisch nachgezogen.
- Comparison-Filters bleiben sprachunabhaengig auf stabilen Query-Werten (`search`, `levels`, `l1`, `gender`, `exposure`) und werden per `replaceState` mitgefuehrt, statt nur im fluechtigen In-Memory-Filterzustand zu leben.
- Ein impliziter Comparison-Draft bleibt URL-neutral nur solange er fachlich leer ist; sobald aktive Session-Auswahl oder sonst nicht-defaultiger Workbench-State existiert, wird der stabile `set_id` wieder adressierbar, damit Locale-Wechsel und Rueckkehr dieselbe Auswahl rekonstruieren koennen.
- Die Satzitem-Aufloesung im Text-Player verwendet jetzt denselben robusten Vorgänger-Treffer-Gedanken wie das Token-Mapping: in Gaps bleibt das letzte gueltige Satzitem aktiv, statt global auf das letzte Array-Element zu springen.

## Abweichungen

- Keine Abweichung von der aktiven Spec; die bindenden Regeln wurden in `docs/spec/platform-data-files.md`, `docs/spec/research-access.md` und `docs/spec/research-player.md` nachgezogen.

## Verifikation

- `get_errors` auf den geaenderten Template-, JS-, Test- und Spec-Dateien: keine Fehler
- `Run research sessions tests`: gruen
- `node --test app/tests/js/research_ui_state_helpers.test.mjs`: deckt Locale-URL-Rewrite, Comparison-URL-State und Satzitem-Gap-Mapping ab
- Live-HTML-Pruefung bleibt weiterhin ueber die laufende Dev-Runtime moeglich; die aktuelle Korrektur zielt auf clientseitige Href-/State- und Highlight-Logik, nicht auf neue sichtbare Strukturklassen

## Offene Punkte

- Kein weiterer in-scope Punkt offen. Fuer vollautomatisches Browserklicken waere zusaetzliche Browser-Automation noetig; in diesem Run wurde die Clientlogik stattdessen ueber fokussierte Hilfsmodul-Tests plus bestehende Python-Suites abgesichert.