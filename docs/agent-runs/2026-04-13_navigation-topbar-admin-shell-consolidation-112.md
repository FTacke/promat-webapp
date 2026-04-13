# Navigation, Topbar And Admin Shell Consolidation

Datum: 2026-04-13

## Ziel

Die gemeinsame App-Shell für Navigation, Sprachwechsel, Topbar-Utilities und den Admin-Users-Bereich konsistent bereinigen, die Verantwortlichkeiten zwischen Sidebar und User-Menü sauber trennen und das Ergebnis mit fokussierten Regressionen plus Live-Browser-QA in Desktop- und Mobile-Zuständen validieren.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `docs/runbooks/ui-change-workflow.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- Shared App-Factory- und Kontextlogik unter `app/src/app/__init__.py`
- Shared protected-navigation-Helfer unter `app/src/app/protected_navigation.py`
- Shared Topbar- und Drawer-Partials unter `app/templates/partials/`
- Shared Shell-Übersetzungen unter `app/src/app/i18n.py`
- Shared Typografie- und Komponenten-CSS unter `app/static/css/10_typography.css` und `app/static/css/30_components.css`
- Fokus-Regressionen unter `app/tests/test_auth_phase1.py` und `app/tests/test_research_sessions.py`
- Aktive Plattform-Spec unter `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- Sidebars bleiben reine Bereichsnavigation; globale Ziele wie `Mein Konto`, `Admin-Bereich` und `Logout` gehören ausschließlich in die Topbar-Utilities beziehungsweise ins User-Menü.
- Der Sprachwechsel wird als textbasierte Utility `DE | EN` in der Topbar geführt, nicht als Globe- oder Flaggen-Primärkontrolle.
- Der Sprachwechsel muss dieselbe Route erhalten: öffentliche Pfade über den `/{ui_lang}/...`-Prefix, geschützte Auth- und Admin-Flächen über den `ui_lang`-Query-Parameter.
- Der Admin-Bereich verwendet in Sidebar und User-Menü konsistent `Admin-Bereich` beziehungsweise `Admin area`; die Admin-Sidebar enthält nur den nicht klickbaren Bereichstitel sowie `Benutzer` und `Analytics`.
- Der Account-Button bleibt eine ruhige Utility-Aktion; der geöffnete Zustand darf sichtbar sein, aber nicht wie ein permanentes Badge wirken.
- Die Toolbar der Admin-Benutzerverwaltung wird über die gemeinsame Komponentenfamilie ausgerichtet, statt die Filter- und Action-Höhen lokal im Template zu patchen.

## Abweichungen

- Keine fachliche Abweichung von der aktiven Spec.
- Für die Live-QA wurde erneut ein temporärer Dev-Runner auf Port `8010` verwendet, um eine frische Runtime ohne stale HTML aus einem parallelen Listener zu prüfen.

## Verifikation

- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py -q` -> `18 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -q -k "research_overview_topbar_exposes_route_preserving_language_switch or research_sidebar_stays_area_only_when_authenticated or account_page"` -> `3 passed, 138 deselected`
- Headless-Edge-Live-QA gegen `http://127.0.0.1:8010` für Desktop und Mobile in `de` und `en`.
- Verifizierte Zustände: öffentliche Research-Übersicht mit Route-erhaltendem Sprachwechsel, Admin-Users-Desktop inkl. Toolbar und User-Menü, reguläres Konto in `de` und `en`, Research-Mobile-Drawer, Admin-Mobile-Drawer und Admin-Mobile-User-Menü.
- Browser-Artefakte abgelegt unter `tmp/ui-qa/navigation-consolidation/`, inklusive `qa_report.json` und 13 Screenshots der finalen Zustände.

## Offene Punkte

- Kein fachlicher Restpunkt aus diesem Run.
- Der zuvor fehlgeschlagene Mobile-QA-Schritt erwies sich als Sequenzproblem im Prüfskript, nicht als Produktfehler: Vor dem Öffnen des User-Menüs musste der Drawer explizit geschlossen werden.

## Nächste sinnvolle Schritte

- Die temporäre QA-Startlogik auf Port `8010` bei wiederholter Nutzung in ein klar reproduzierbares Runbook überführen, falls weitere UI-Abnahmen auf frischer Runtime nötig sind.
- Bei späteren Shell-Änderungen dieselben fokussierten Auth- und Research-Regressionen plus Screenshot-Pfade wiederverwenden, damit die Verantwortlichkeit zwischen Sidebar und Topbar stabil bleibt.