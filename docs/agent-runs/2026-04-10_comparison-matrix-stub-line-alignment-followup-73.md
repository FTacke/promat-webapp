# Comparison Matrix Stub Line Alignment Follow-up

Datum: 2026-04-10

## Ziel

Die Vertikallogik der linken Item-Stub-Zelle in der `comparison`-Matrix sauber zwischen Einzeilern und Zweizeilern trennen, ohne Matrixlogik, Audio, Filter oder Sprecherdarstellung zu verändern.

## Consulted Sources

- `app/static/js/pages/research-comparison.js`
- `app/static/css/30_components.css`
- `docs/agent-runs/_template.md`

## Geänderte Bereiche

- `app/static/js/pages/research-comparison.js`
- `app/static/css/30_components.css`

## Wichtige Entscheidungen

- Die Unterscheidung zwischen Einzeiler und Zweizeiler erfolgt messbasiert nach dem tatsächlichen gerenderten Textblock statt über Zeichenlänge oder starre Heuristiken.
- Einzeilige Stub-Zellen verwenden jetzt die mittige Achse als Standardzustand.
- Nur tatsächlich mehrzeilige Stub-Zellen schalten gezielt auf die bestehende obere Verankerung an Zeile 1 um.
- Die Messung wird nach dem Matrix-Render und bei Fenstergrößenänderungen erneut synchronisiert, damit das Verhalten bei Wortlisten und späteren Satzitems reproduzierbar bleibt.

## Abweichungen

- Keine Abweichung von aktiven Regeln; die bestehende Zweizeilen-Regel wurde nur technisch sauberer umgesetzt.

## Verifikation

- Diagnostik für `app/static/js/pages/research-comparison.js` und `app/static/css/30_components.css`: keine Fehler.
- Fokussierter Testlauf `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_comparison.py`: `6 passed`.

## Offene Punkte

- Keine visuelle Browserprüfung mit echten Ein- und Zweizeiler-Beispielen in diesem Run.

## Nächste sinnvolle Schritte

- Im Browser kurz einen Einzeiler und einen Zweizeiler in der linken Stub-Spalte gegeneinander prüfen.
