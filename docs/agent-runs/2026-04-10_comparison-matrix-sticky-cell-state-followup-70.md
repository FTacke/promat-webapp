# Comparison Matrix Sticky And Cell State Follow-up

Datum: 2026-04-10

## Ziel

Den letzten sichtbaren Feinschliff der `comparison`-Matrix umsetzen: opaker Sticky-Kopf- und Eckbereich, stärkere Binnenhierarchie in der linken Item-Spalte, kontrolliertere Ein-/Zweizeiligkeit und ein ruhiger aktiver Zellzustand für Audio.

## Consulted Sources

- `docs/spec/research-access.md`
- `app/static/css/30_components.css`
- `app/static/css/20_layout.css`
- `app/static/js/pages/research-comparison.js`
- `docs/agent-runs/_template.md`

## Geänderte Bereiche

- `app/static/css/30_components.css`
- `docs/spec/research-access.md`

## Wichtige Entscheidungen

- Der Feinschliff blieb CSS-first; weder Matrix-Struktur noch Audio- oder Auswahl-Logik wurden verändert.
- Der Sticky-Kopf- und Eckbereich wurde über feste Hintergrundflächen und eine klarere `z-index`-Staffelung als echte opake Matrixschicht stabilisiert.
- Die linke Stub-Zelle priorisiert jetzt den Text deutlicher gegenüber Nummern- und Play-Kreis; beide Kreise wurden kompakter und an der ersten Textzeile verankert.
- Der aktive Audiozustand wird als ruhige Zellfläche mit zentrierter Aktionsgruppe gelesen statt als kleine hinterlegte Button-Insel.

## Abweichungen

- Keine Abweichung von der aktiven Spezifikation; die Matrix-Regeln in `docs/spec/research-access.md` wurden im selben Run präzisiert.

## Verifikation

- CSS-Diagnostik für die geänderten Stylesheets mit `get_errors`: keine Fehler nach der Kompatibilitätsbereinigung.
- Fokussierter Testlauf `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_comparison.py`: `6 passed`.
- Keine Browser-Screenshot- oder Scroll-/Playback-Sichtprüfung in diesem Run.

## Offene Punkte

- Die opake Sticky-Wirkung und der flächigere aktive Zellzustand sind per Codeprüfung und Testlauf abgesichert, aber noch nicht live im Browser mit echtem Scrollen und aktiver Wiedergabe visuell gegengeprüft.

## Nächste sinnvolle Schritte

- Die Matrix einmal im laufenden Browser horizontal und vertikal scrollen und die obere linke Ecke gegen Durchscheinen prüfen.
- Einen echten aktiven Zellzustand im Browser anklicken und die Zentrierung der Icons in der markierten Fläche gegenprüfen.