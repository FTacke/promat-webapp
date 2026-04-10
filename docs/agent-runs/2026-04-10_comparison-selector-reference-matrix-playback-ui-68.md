# Comparison selector reference, matrix alignment, and playback UI

Datum: 2026-04-10

## Ziel

Die `comparison`-Oberfläche ab dem Stand der dreispaltigen Sprecher:innen-Auswahl in der richtigen Richtung weiterziehen: die oberen Sprecherkarten bleiben die visuelle Referenz, die Matrix-Sprecherköpfe werden zur kompakten Adaption derselben Kartenfamilie, die linke Item-Spalte wird als stabile sticky Drei-Zonen-Zelle gefestigt, und die sichtbare Playback-Reaktion wandert ohne externe Statuszeile direkt in die aktive Matrixzelle.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/templates/pages/research_comparison.html`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_comparison.py`

## Geänderte Bereiche

- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-comparison.js`
- `app/static/css/30_components.css`
- `app/static/css/20_layout.css`
- `app/tests/test_research_comparison.py`
- `docs/spec/research-access.md`
- `docs/agent-runs/`

## Wichtige Entscheidungen

- Die oberen Sprecherkarten bleiben ausdrücklich das Referenzmuster; die Matrix-Spaltenköpfe verwenden nun dieselbe Kartenfamilie nur in dichterer, schmalerer Form statt einer zweiten Matrix-eigenen Kopfkarte.
- Das redundante sichtbare `Lernende`-Label wurde aus den Sprecherkarten und Matrix-Köpfen entfernt; Lernende lesen nun über `person_id`, Niveau und `L1`, Native über `person_id`, `Native` und die übersetzte Standardvarietät.
- Die drei Spalten `Lernende`, `Native Speaker` und `Ausgewählt` bleiben auf demselben Containermuster; `Ausgewählt` ist nur noch eine subtile aktive Variante derselben UI-Familie.
- Die Matrix bleibt ein echter horizontaler Arbeitsbereich: stabile sticky Kopfzeile, stabile sticky Stub-Spalte links, breitere Arbeitsbreite und kein erneutes Zusammendrücken der Stub-Zelle zugunsten zusätzlicher Sprecher-Spalten.
- Die sichtbare Playback-UI wurde beruhigt, ohne die Audio-Transportlogik anzufassen: keine externe Statuszeile mehr über der Matrix, stattdessen direkte aktive Zellmarkierung in derselben ruhigen Zustandslogik wie im Player.

## Abweichungen

- Keine Abweichung von Routing, Player-Familie, Set-/Phenomena-Modell, Filterlogik oder Audio-Header-/Response-Transportlogik.
- In diesem Run wurde keine stabile browsergesteuerte Klick- oder Screenshot-Automation für die neue Matrix-Aktivmarkierung durchgeführt.

## Verifikation

- VS-Code-Fehlerprüfung auf den geänderten Template-, JS-, CSS-, Test- und Spec-Dateien: ohne neue Fehler.
- Fokussierter Regressionstest:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_comparison.py`
  - Ergebnis: `6 passed`.
- Laufzeitnahe Roh-HTML-Prüfung gegen die lokale Route `http://127.0.0.1:8000/de/research/spanish/comparison`:
  - `HasPlaybackStatus: False`
  - `HasMatrixWrap: True`
  - `HasSpeakerStage: True`
  - `HasSelectedHeaderModifier: False`

## Offene Punkte

- Die Kartenfamilie oben/unten und die ruhige Matrixstruktur sind über Markup, CSS und Regression abgesichert, aber nicht per Screenshot-Diff oder pixelgenauer Browserprüfung belegt.
- Die aktive Matrixzell-Markierung wurde code- und zustandsseitig umgesetzt, aber nicht in einem stabilen browserautomatisierten Play-Flow mit echter Audioausführung nachgewiesen.

## Nächste sinnvolle Schritte

- Einen browsergesteuerten Owner-Flow für `comparison` ergänzen: Sprecher:in auswählen, Matrix-Playback starten, aktive Zelle beobachten.
- Falls der nächste visuelle Feinschliff nötig ist, nur noch die Dichte der Matrix-Karten und Stub-Spalte nachziehen, nicht erneut die Referenzrichtung zwischen oberer Auswahl und Matrix umdrehen.