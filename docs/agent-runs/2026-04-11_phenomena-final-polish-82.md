# Phenomena Final Polish 82

## Ziel

Die verbleibenden Detailfehler der split `phenomena`-Overview und des Editors schließen: Preview-Zeile aus der Overview entfernen, Set-Zeilen rhythmisch luftiger machen, `gespeichert`/`ungespeichert` als echte sichtbare Zustände ausweisen, selected-vs-muted in den Materiallisten stärker trennen, Selected-Items räumlich beruhigen und das Drag-Feedback als ganze Zeile lesbar machen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/runbooks/ui-change-workflow.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/src/app/research_phenomena_views.py`
- `app/templates/pages/research_phenomena_overview.html`
- `app/templates/pages/research_phenomena_editor.html`
- `app/static/css/00_tokens.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/tests/test_research_phenomena.py`

## Geänderte Bereiche

- Phenomena-Overview-Markup und Zeilenrhythmus
- Phenomena-Editor-Statuszeile und Zustandslogik
- Materiallisten- und Selected-Items-Styling
- Drag-Visualisierung im Selected-Items-Bereich
- aktive Research-Spec für `phenomena`-Terminologie und Aktionslogik
- fokussierte Render-/Route-Regressionen für `phenomena`

## Wichtige Entscheidungen

- Typstatus und Speicherstatus bleiben getrennte sichtbare Konzepte: `curated`/`custom` als ein Badge, `neu`/`gespeichert`/`ungespeichert` als separates Badge plus kurze Statuszeile.
- Für selected-vs-muted wurde nicht noch ein lokaler Phenomena-Farbmix eingeführt; stattdessen wurden die vorhandenen semantischen Zustands-Tokens in `00_tokens.css` nachgeschärft und in den Listenzeilen konsequenter verwendet.
- Das Drag-Feedback wurde als ganze Zeile modelliert: Row-Ghost plus Drop-Target-Streifen statt einer nur am Handle lesbaren Bewegung.

## Abweichungen

- Keine Abweichung an aktiven Specs.
- Die isolierte Comparison-Regressionsinstanz lief mit Test-Auth-Kontext für das Page-Rendering, aber ohne echte owner-bound API-Session; dadurch zeigt die Vergleichsseite im Screenshot einen `UNAUTHORIZED`-Hinweis im Set-Bereich, die Shared-CSS-Regression blieb dennoch prüfbar.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sets.py tests/test_research_phenomena.py`
  - Ergebnis: `26 passed`
- Browser-QA auf isolierter lokaler Testinstanz mit minimalem `phenomena`-Runtime-Setup und Headless Edge/Selenium
- Sichtprüfung der Screenshots auf:
  - korrekte Terminologie (`Phänomene`, `1 Set wählen`, Introtext)
  - entfernte Overview-Preview-Zeile
  - sichtbare Saved/Unsaved-Zustände
  - stärkere selected-vs-muted-Differenz
  - nicht-pillige Selected-Fläche in Materialzeilen
  - ruhigere Selected-Items-Zeilen und ganzzeiliges Drag-Feedback
  - Shared-CSS-Regression auf `comparison`

## Screenshots

- `tmp/ui-qa/phenomena-final-polish-82/overview-default.png`
- `tmp/ui-qa/phenomena-final-polish-82/overview-auth-hover-custom-actions.png`
- `tmp/ui-qa/phenomena-final-polish-82/editor-saved-state.png`
- `tmp/ui-qa/phenomena-final-polish-82/editor-unsaved-state.png`
- `tmp/ui-qa/phenomena-final-polish-82/editor-wordlist-selected-muted.png`
- `tmp/ui-qa/phenomena-final-polish-82/editor-selected-items-drag-state.png`
- `tmp/ui-qa/phenomena-final-polish-82/comparison-regression.png`

## Offene Punkte

- Die Badges nutzen aktuell bewusst die bestehenden technischen Kurzlabels `curated` und `custom`; falls dort später deutschsprachige, produktive Sichtlabels gewünscht sind, sollte das als gesonderte Copy-Entscheidung einmalig über den zentralen Status-Label-Pfad erfolgen.

## Nächste sinnvolle Schritte

- Falls gewünscht, die Statusbadge-Copy (`curated`/`custom`) als letzten separaten Copy-Pass auf sichtbare deutsche Arbeitsbegriffe umstellen.