# Comparison Step Order Reordering

Datum: 2026-04-10

## Ziel

Die drei bestehenden Hauptschritte der `comparison`-Seite ausschließlich in ihrer Reihenfolge umstellen, sodass der sichtbare Flow als `1 Sprecher:innen auswählen`, `2 Items auswählen`, `3 Matrix` gelesen wird.

## Consulted Sources

- `app/templates/pages/research_comparison.html`
- `docs/spec/research-access.md`
- `docs/agent-runs/_template.md`

## Geänderte Bereiche

- `app/templates/pages/research_comparison.html`
- `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Der Run blieb rein strukturell: Es wurden nur die bestehenden Container umgehängt und die Schrittziffern angepasst.
- Weder Filter-, Material-, Matrix-, Audio- noch Auswahlverhalten wurden verändert.
- Die aktive Spec wurde im selben Run nur auf die neue sichtbare Schrittfolge nachgezogen.

## Abweichungen

- Keine Abweichung von der aktiven Spezifikation; die Spezifikation wurde parallel zur Template-Änderung aktualisiert.

## Verifikation

- Template- und Spec-Diagnostik: keine Fehler.
- Fokussierter Testlauf `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_comparison.py`: `6 passed`.
- Gerenderter HTML-Probeaufruf der lokalen Seite bestätigt die Reihenfolge `session -> material -> matrix`.

## Offene Punkte

- Keine zusätzliche visuelle Browserprüfung in diesem Run.

## Nächste sinnvolle Schritte

- Bei Gelegenheit die Seite im Browser kurz öffnen und nur die sichtbare Schrittfolge gegenprüfen.
