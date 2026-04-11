# Phenomena Selected Items Drag Fix 83

## Ziel

Den Reorder-Fehler unter `Ausgewählte Items` beheben und den horizontalen Abstand zwischen Positionskreis und Zeileninhalt sichtbar sauber herstellen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/runbooks/ui-change-workflow.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`

## Geänderte Bereiche

- Drag-and-drop-Logik der Selected-Items-Liste
- horizontales Grid-Gap der Selected-Items-Zeile
- Drop-Target-Visualisierung für before/after-Einfügepunkte

## Wichtige Entscheidungen

- Während eines laufenden Drags wird die Selected-Items-Liste nicht mehr per `renderSelectedList()` neu aufgebaut; Drop-Zustände werden direkt am bestehenden DOM markiert, damit der Drag-Kontext stabil bleibt.
- Der Drop-Zielpunkt unterscheidet jetzt zwischen `before` und `after`, abhängig von der Cursorlage innerhalb der Zielzeile; damit folgt die Einfügelogik der sichtbaren Drop-Markierung statt implizit immer denselben Index zu verwenden.
- Der Abstand zwischen Kreis und Inhalt wird als echtes Spalten-Gap im Grid modelliert statt über isolierte Margins einzelner Kindelemente.

## Abweichungen

- Keine.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sets.py tests/test_research_phenomena.py`
  - Ergebnis: `26 passed`
- Browser-QA auf isolierter lokaler Testinstanz mit Headless Edge/Selenium
  - DOM-Prüfung des Reorders:
    - vorher: `mesa`, `quería`, `reír`, `Hoy miro el reloj con calma antes de salir.`, ...
    - nach Drop hinter den Zielblock: `quería`, `reír`, `Hoy miro el reloj con calma antes de salir.`, `mesa`, ...
- Sichtprüfung des aktualisierten Selected-Items-Layouts und des zusätzlichen Horizontalabstands

## Screenshots

- `tmp/ui-qa/phenomena-drag-fix-83/selected-items-spacing-and-order.png`

## Offene Punkte

- Keine zusätzlichen offenen Punkte aus diesem Nachfix.

## Nächste sinnvolle Schritte

- Falls gewünscht, einen zweiten Browser-Check mit manueller Mausinteraktion auf der realen Dev-Instanz nachziehen, zusätzlich zur isolierten Selenium-Prüfung.