# Sidebar-Header auf allen Innen-Seiten systemweit vereinheitlicht

Datum: 2026-04-02

## Ziel

Die räumlich beruhigte Innen-Shell beibehalten, aber die Sidebar-Grammatik plattformweit vereinheitlichen: Alle Innen-Seiten außer Landing beginnen in der linken Sidebar wieder mit demselben Bereichsheader aus Icon, Bereichstitel und feiner Trennlinie.

## Ursache der alten Abweichung

- Die frühere Research-Ausnahme war noch im Template-Zweig für `context_mode="none"` verankert.
- Dadurch blieb die Forschungs-Übersicht trotz gemeinsamer Innen-Shell ohne Sidebar-Header.
- Zusätzlich sicherten neue Render-Regressionen und Run-Logs diesen Zwischenstand noch als beabsichtigte Ausnahme ab.

## Geänderte Bereiche

- `app/templates/partials/_navigation_drawer.html`: Bereichsheader wird jetzt zentral für alle Innen-Seiten mit Sidebar gerendert; Sprachkontext kommt darunter als sekundäre Ebene
- `app/static/css/30_components.css`: Panel-Context und Section-Header ohne bereichslokale Sonderabstände vereinheitlicht; Divider läuft über systemische Shell-Tokens
- `app/static/css/10_typography.css` und `app/static/css/00_tokens.css`: Sidebar-Header-Typografie zentral tokenisiert
- `docs/spec/platform-data-files.md`: gemeinsame Innen-Shell und systemweiter Sidebar-Header als aktive Plattformregel ergänzt
- `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/repo.instructions.md`: Guidance auf die aktive Shell-Regel und Spec-Pflicht nachgezogen
- `docs/agent-runs/2026-04-02_research-layout-shell-hierarchy-followup-17.md` und `docs/agent-runs/2026-04-02_app-shell-inner-pages-followup-18.md`: frühere Research-Ausnahme explizit als überholter Zwischenstand markiert
- `app/tests/test_research_sessions.py`: Sidebar-Header-Regel für Projekt, Forschung, Forschung-Subseite, Unterricht und Sample neu abgesichert

## Normative Doku

- `docs/spec/platform-data-files.md` ist jetzt die aktive Source of Truth für die gemeinsame Innen-Shell: Landing bleibt Ausnahme, alle anderen Innen-Seiten beginnen mit Bereichsheader in der Sidebar.

## Verifikation

- `/de/project`
- `/de/research`
- `/de/research/spanish`
- `/de/teaching/spanish`
- `/de/sample`
- vollständiger Testlauf: `pytest tests/test_research_sessions.py`

## Offene Punkte

- Keine neue Bereichsausnahme offen. Unterschiede zwischen Projekt-, Forschungs- und Unterrichtsseiten liegen jetzt nur noch in ihrem sekundären Kontext unterhalb desselben Sidebar-Headers.