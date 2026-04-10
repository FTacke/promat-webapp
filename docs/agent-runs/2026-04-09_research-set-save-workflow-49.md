# Research Set Save Workflow

Datum: 2026-04-09

## Ziel

Die sichtbare Draft-zu-Saved-Set-UX in `phenomena` und `comparison` schliessen, ohne neue Persistenzmodelle, neue Routefamilien oder neue DB-Strukturen einzuführen.

## Consulted Sources

- `docs/spec/research-player.md`
- `docs/spec/research-access.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/plans/player_comparison_phenomena.md`
- `docs/plans/player_comparison_phenomena_repo_implementation_plan.md`
- `app/src/app/research_sets.py`
- `app/src/app/routes/research_api.py`
- `app/src/app/research_views.py`

## Geänderte Bereiche

- `app/src/app/research_sets.py`
- `app/src/app/research_views.py`
- `app/templates/pages/research_phenomena.html`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-phenomena.js`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/30_components.css`
- `app/tests/test_research_sets.py`
- `app/tests/test_research_phenomena.py`
- `app/tests/test_research_comparison.py`
- `docs/spec/research-player.md`
- `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Die produktive Speicheraktion bleibt auf genau einen sichtbaren CTA `Als neues Set speichern` pro Workbench begrenzt.
- Beide Workbenches nutzen unverändert den bestehenden `save-as`-Pfad `/api/research/sets/{set_id}/save-as`.
- Nach erfolgreichem Speichern wechselt die aktive Client-Session unmittelbar auf das neu zurückgegebene Saved-Set, damit alle weiteren Handoffs konsistent auf dem neuen `set_id` laufen.
- Draft/Saved-Orientierung bleibt bewusst zurückhaltend: Status-Meta plus Feedback-Zeile statt zusätzlicher Toolbar oder Set-Management-Oberfläche.

## Abweichungen

- Keine Abweichung von der aktiven Set-Architektur, den Runtime-Grenzen oder der bestehenden Routefamilie.

## Verifikation

- Strukturelle Fehlerprüfung für geänderte Python-, JS- und Template-Dateien über die Problems-/Errors-Schnittstelle.
- Ergänzte API- und Seiten-Regressionstests für Save-Labels, Save-Dialog-Präsenz und Label-Verdrahtung.
- Geplanter gezielter Pytest-Lauf für die geänderten Research-Set-, Phenomena- und Comparison-Tests.

## Offene Punkte

- Es gibt noch keine separate Oberfläche zum Laden oder Verwalten bestehender Saved-Sets; dieser Run deckt bewusst nur den Draft-zu-Saved-Fluss ab.
- Die Save-UX ist strukturell und per Fehlerprüfung abgesichert; browserseitige End-to-End-Interaktion bleibt ein sinnvoller späterer Zusatztest.

## Nächste sinnvolle Schritte

- Einen gezielten Pytest-Lauf für die geänderten Research-Set-, Phenomena- und Comparison-Tests ausführen.
- Optional eine kleine Saved-Set-Auswahl prüfen, falls sie ohne zweite Set-Management-Architektur in die bestehenden Statuskarten passt.
