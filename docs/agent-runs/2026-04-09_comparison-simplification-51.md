# Comparison vereinfacht, Phänomene geschärft

Datum: 2026-04-09

## Ziel

`comparison` radikal auf den ersten produktiven Arbeitsmodus reduzieren: kurze Materialfläche, kompakte Sessionauswahl und dominante Vergleichsmatrix. Gleichzeitig `phenomena` klar als Material-Konfiguration schärfen und die Umlaut-Regel in den `.github`-Instruktionen absichern.

## Consulted Sources

- `docs/plans/player_comparison_phenomena.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/spec/platform-data-files.md`
- `docs/runbooks/local-dev-start.md`
- `docs/agent-runs/2026-04-09_research-comparison-workbench-45.md`
- `docs/agent-runs/2026-04-09_research-player-set-context-46.md`
- `docs/agent-runs/2026-04-09_research-player-text-renderer-47.md`
- `docs/agent-runs/2026-04-09_research-player-text-compare-48.md`
- `docs/agent-runs/2026-04-09_research-set-save-workflow-49.md`
- `docs/agent-runs/2026-04-09_local-research-set-bootstrap-50.md`

## Geänderte Bereiche

- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/src/app/research_views.py`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/research-access.md`
- `app/tests/test_research_comparison.py`
- `app/tests/test_research_phenomena.py`

## Wichtige Entscheidungen

- `comparison` startet für angemeldete Owner ohne sichtbaren Set-Auswahlschritt in einen internen Standard-Draft mit `wordlist` als Default-Material.
- Die Vergleichsseite zeigt keinen separaten Launcher- oder Fokusblock mehr; Player-Handoffs bleiben in der Matrix pro Zelle dezent erreichbar.
- Die Sessionauswahl bleibt bewusst kompakt und zeigt nur `session_id`, `person_id`, Sprechergruppe, Niveau und `L1`.
- `phenomena` bleibt die Materialseite; `comparison` ist die Session-Vergleichsseite.
- Die `.github`-Instruktionen nennen nun explizit die Regel, dass sichtbare deutsche UI-Texte und gepflegte deutsche Überschriften/Labels echte Umlaute und `ß` verwenden müssen, während technische Werte ASCII/English bleiben.

## Verifikation

- Gezielte Research-Tests für `comparison` und `phenomena` angepasst und erneut ausgeführt.
- HTML-Regression prüft jetzt zusätzlich, dass der alte `comparison`-Launcher-Block nicht mehr gerendert wird.

## Nächster sinnvoller Schritt

- `phenomena` im nächsten Run noch stärker auf Material-Kuration verdichten, etwa durch kompaktere Preset-Einstiege und weniger generische Workspace-Sprache.
