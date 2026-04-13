# Research Root Muted Links Only 109

Datum: 2026-04-13

## Ziel

Die sichtbare Nachkorrektur an der öffentlichen Research-Korpus-Landingpage umsetzen: Bei geschützten Zielen sollen nur die Aktionslinks gedimmt bleiben, nicht die erklärenden Titel- und Beschreibungstexte der Einträge.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/runbooks/ui-change-workflow.md`
- Produktive Dateien: `app/templates/pages/research_language_root.html`, `app/templates/pages/sample_page.html`, `app/static/css/30_components.css`, `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `app/templates/pages/research_language_root.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`

## Wichtige Entscheidungen

- Die Dimmung bleibt ausschließlich an der geschützten Aktion selbst, damit die Landingpage weiterhin informativ lesen darf, auch wenn ein Ziel noch login-geschützt ist.
- Der Sample-Mirror wurde im selben Run mitgezogen, damit die dargestellte aktive Layoutfamilie konsistent bleibt.

## Abweichungen

- Keine Abweichung von den aktiven Specs.
- Keine funktionale Access-Logik geändert; nur die sichtbare Gewichtung der Landingpage-Einträge wurde angepasst.

## Verifikation

- Fokussierte Regression ausgeführt:
  - `pytest app/tests/test_research_sessions.py -q -k research_language_root_shows_muted_locked_entries_for_signed_out_users`
  - Ergebnis: `1 passed, 138 deselected`
- Zusätzlich Testassertion ergänzt, dass der gesamte Root-Eintrag nicht mehr die Klasse `is-muted` trägt.

## Offene Punkte

- Keine im Scope dieses Korrekturlaufs.

## Nächste sinnvolle Schritte

- Bei weiteren kleinen UI-Korrekturen an der Research-Root dieselbe Regel beibehalten: Zugangssignal auf der Aktion, Information im Textkörper normal lesbar.