# Comparison Sticky Corner And L1 Badge Fix

Datum: 2026-04-10

## Ziel

Zwei verbleibende visuelle Restfehler in der `comparison`-Matrix korrigieren: den sticky Kopf-/Eckbereich wirklich opak machen und `L1: ...` als klar neutrales graues Badge mit einfacher Kontur führen.

## Consulted Sources

- `app/templates/pages/research_comparison.html`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-comparison.js`
- `docs/agent-runs/_template.md`

## Geänderte Bereiche

- `app/static/css/30_components.css`

## Wichtige Entscheidungen

- Der sticky Kopf- und Stubbereich bekam eine zusätzliche opake Hintergrundebene per Pseudoelement, statt Matrix-Markup oder Scroll-Logik zu verändern.
- Das `L1`-Badge wurde von einer zu flachen Neutralfläche auf eine schlichte weiße Fläche mit grauer Kontur umgestellt, damit es an Auswahl und Matrix zuverlässig als Badge lesbar bleibt.

## Abweichungen

- Keine Abweichung von aktiven Regeln; rein visueller Korrekturlauf im bestehenden Comparison-System.

## Verifikation

- CSS-Diagnostik auf der geänderten Datei: ohne Fehler.
- Fokussierter Vergleichstestlauf `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_comparison.py`: `6 passed`.

## Offene Punkte

- Keine Screenshot- oder Live-Scroll-Prüfung in diesem Run.

## Nächste sinnvolle Schritte

- Die obere linke Matrixecke und das `L1`-Badge bei Gelegenheit kurz im Browser gegenprüfen.
