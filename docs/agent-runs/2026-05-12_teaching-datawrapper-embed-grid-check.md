# 2026-05-12 Teaching Datawrapper Embed Grid Check

## Scope

Schneller Debug-/Fix-Run fuer die Teaching-Pilotseite `/de/teaching/spanish/which-pronunciation` mit Fokus auf die Frage, warum die beiden Datawrapper-Embeds im realen Browser untereinander standen.

## Ursache

- Die YAML-Quelle fuer beide Datawrapper-Karten setzt korrekt `layout.span: 1`.
- Der Teaching-Normalizer in `app/src/app/teaching_content.py` gibt fuer `embed` bei explizitem `span: 1` ebenfalls `1` zurueck.
- Der eigentliche Fehler lag im Template: Der `embed`-Zweig in `app/templates/partials/_teaching_blocks.html` schloss das umgebende `<section>` nicht, sodass der zweite Embed im gerenderten DOM innerhalb des ersten Embed-Blocks verschachtelt wurde.
- Durch diese Verschachtelung war der zweite Embed kein direkter Grid-Item mehr und konnte nicht in der zweiten Spalte stehen.

## Fix

- `app/templates/partials/_teaching_blocks.html`
  - fehlendes `</section>` nach dem Datawrapper-`figure` im `embed`-Zweig ergänzt
- `app/tests/test_research_sessions.py`
  - fokussierte HTML-Regressionsprüfung ergänzt, die zwei sibling Embed-Sections verlangt

## Validierung

### Pytest

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "which_pronunciation or teaching_pilot or datawrapper or teaching"`

### Browser-QA

Geprüft auf dem laufenden Server:

- `/de/teaching/spanish/which-pronunciation`

Ergebnis der DOM-/CSS-Prüfung:

- beide Embed-Blöcke sind direkte Kinder von `.pm-teaching-block-grid--topic`
- beide haben `pm-teaching-block pm-teaching-block--span-1 pm-teaching-block--embed`
- der Grid-Container ist zweispaltig (`514px 514px`)
- kein Ancestor erzwingt Full-Width oder falsches Nesting
- Screenshot bestätigt die nebeneinander stehende Anordnung

## Ergebnis

- Desktop: die beiden Datawrapper-Embeds stehen nebeneinander.
- Mobile: das bestehende 1-Spalten-Topic-Grid bleibt erhalten.
- Die Ursache war kein CSS-Grid-Zwang, sondern ein fehlendes schliessendes `</section>` im `embed`-Templatezweig.
