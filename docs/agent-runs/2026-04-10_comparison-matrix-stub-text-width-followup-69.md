# Comparison Matrix Stub Text Width Follow-up

Datum: 2026-04-10

## Ziel

Die linke Item-Stub-Spalte der `comparison`-Matrix für kurze Wortlisten und spätere Satz-/Text-Items robust machen, ohne Audio-, Filter-, Material- oder Sprecherlogik anzufassen.

## Consulted Sources

- `docs/spec/research-access.md`
- `app/static/css/30_components.css`
- `app/static/css/20_layout.css`
- `app/static/js/pages/research-comparison.js`
- `docs/agent-runs/_template.md`

## Geänderte Bereiche

- `app/static/css/30_components.css`
- `app/static/css/20_layout.css`
- `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Die bestehende Matrix-Stub-Markup-Struktur blieb unverändert; die gewünschte Robustheit ließ sich CSS-first erreichen.
- Die linke Stub-Spalte wurde auf einen stabileren Desktop-Korridor angehoben, damit Wort- und Satzitems dieselbe Geometrie behalten.
- Item-Text unterstützt jetzt bis zu zwei sichtbare Zeilen mit linker Ausrichtung, während Nummern- und Play-Kreis oben an der ersten Textzeile ausgerichtet bleiben.
- Der rechte Matrixrand bekam nur einen subtilen Fortsetzungs-Hinweis über einen Fade statt einer stärkeren dekorativen Kante.

## Abweichungen

- Keine Abweichung von der aktiven Spezifikation; die Spezifikation wurde im selben Run auf das präzisierte Stub-Verhalten nachgezogen.

## Verifikation

- CSS-Diagnostik über die geänderten Dateien mit `get_errors`: keine Fehler.
- Fokussierter Testlauf `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_comparison.py`: `6 passed`.
- Keine pixelgenaue Browser-Screenshot- oder Click-through-Verifikation in diesem Run.

## Offene Punkte

- Die neue Zwei-Zeilen-Stubdarstellung ist per CSS und Regressionstest abgesichert, aber noch nicht live mit zukünftigen echten längeren `text`-/`Satzliste`-Datensätzen visuell gegengeprüft.

## Nächste sinnvolle Schritte

- Die Matrix bei Gelegenheit mit realen längeren Satzitems im Browser gegenprüfen.
- Falls dabei nötig, nur das vertikale Spacing der Stub-Zeile feinjustieren, ohne die Geometrie erneut umzubauen.