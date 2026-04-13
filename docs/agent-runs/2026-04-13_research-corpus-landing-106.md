# Research Corpus Landing 106

Datum: 2026-04-13

## Ziel

Die Research-Korpuswurzeln unter `/{ui_lang}/research/{corpus}` von einem direkten Redirect auf `design` zu einer eigenen öffentlichen Orientierungsliste umbauen, ohne die bestehende Access-Architektur aufzuweichen. Dazu gehörten echte Ziel-Links, muted/locked Darstellung geschützter Bereiche für unangemeldete Nutzer:innen, dieselbe Semantik in der Research-Seitennavigation, vollständige `de`/`en`-Texte, fokussierte Regressionen sowie reale Browser-QA mit Screenshots.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- `docs/runbooks/ui-change-workflow.md`
- `docs/plans/auth_login_plan.md`
- `/memories/repo/promat-research-ui-notes.md`
- `/memories/repo/promat-doc-system-notes.md`
- Unverändert geprüft, aber nicht geändert: `.github/copilot-instructions.md`, `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`

## Geänderte Bereiche

- Research-Routing und Shell-Panels in `app/src/app/routes/public.py`
- Öffentlicher Research-Content-Builder in `app/src/app/routes/public_content.py`
- Shared Translation Layer in `app/src/app/i18n.py`
- Shared Navigation Drawer in `app/templates/partials/_navigation_drawer.html`
- Neue dedizierte Research-Landing-Templatefläche in `app/templates/pages/research_language_root.html`
- Sample-Mirror in `app/templates/pages/sample_page.html`
- Shared Tokens und Komponenten-CSS in `app/static/css/00_tokens.css` und `app/static/css/30_components.css`
- Fokussierte Render-/Access-Regressionen in `app/tests/test_research_sessions.py`
- Aktive Specs in `docs/spec/platform-data-files.md`, `docs/spec/research-access.md`, `docs/spec/research-capabilities.md`
- QA-Hilfsartefakte nur unter `tmp/ui-qa/2026-04-13-research-corpus-landing-106/`

## Wichtige Entscheidungen

- Die Korpuswurzel bleibt öffentlich, aber nur als Orientierungsebene; die einzige öffentliche corpus-scoped Research-Seite mit eigenem Seiten-Slug bleibt weiterhin `design`.
- Für die neue Root-Seite wurde bewusst kein Karten-Grid weiterverwendet, sondern eine ruhige lineare Liste auf Basis bestehender `pm-panel`- und `pm-research-button`-Familien.
- Geschützte Ziele bleiben als echte Links sichtbar, werden für unangemeldete Nutzer:innen jedoch ausschließlich über muted/lock-Zustände signalisiert, ohne wiederholte Inline-Login-Hinweise.
- Da die laufende Dev-Instanz auf `127.0.0.1:8000` noch den alten Redirect-Stand renderte, wurde die finale Browser-Abnahme auf einer isolierten aktuellen Workspace-Instanz auf `127.0.0.1:8001` durchgeführt.

## Abweichungen

- Keine Abweichung von der aktiven Access- oder Routing-Spec nach dem Update; die Änderung wurde parallel in die bindenden Spec-Dateien eingetragen.
- Dev-Runtime-Abweichung festgestellt: `127.0.0.1:8000` war stale und renderte noch `/de/research/spanish/design` statt der neuen Korpus-Landingpage. Die finale visuelle Abnahme wurde deshalb auf `127.0.0.1:8001` wiederholt.
- Die QA-Helfer unter `tmp/ui-qa/2026-04-13-research-corpus-landing-106/` sind rein temporäre Run-Artefakte und nicht normativ.

## Verifikation

- Editor-Fehlerprüfung auf den geänderten Python-, Template- und Testdateien: ohne neue Fehler.
- Breiter Pytest-Lauf gegen `tests/test_research_sessions.py` und `tests/test_research_capabilities.py` gestartet; dabei traten bereits bestehende, für diesen Run unveränderte Player-Harness-Fehler wegen nicht initialisierter SQLAlchemy-Engine in einzelnen auth-abhängigen Player-Tests auf.
- Relevanter fokussierter Pytest-Lauf grün:
  - `tests/test_research_sessions.py`
  - `tests/test_research_capabilities.py`
  - Filter: Root-Landing, Public-Design, Workbench-Gates, Detail-Route-Gates, authentifizierte Protected-Workbenches, Sample-Mirror und Capability-Layer
  - Ergebnis: `102 passed, 49 deselected`
- Health-Check auf isolierter Instanz erfolgreich: `http://127.0.0.1:8001/health`
- Browser-QA per headless Edge/Selenium gegen `127.0.0.1:8001` erfolgreich für:
  - `/de/research/spanish`
  - `/en/research/spanish`
  - `/de/research/french`
  - `/de/research/spanish/design`
  - Klick auf den gelockten Link `Sprecher:innen` von `/de/research/spanish` mit Redirect auf `/login?next=/de/research/spanish/speakers`
  - anschließender Login und Weiterleitung auf `/de/research/spanish/speakers`
- Zusätzliche Live-HTML-Prüfung bestätigt den stale Zustand von `127.0.0.1:8000` und den korrekten neuen Zustand auf `127.0.0.1:8001`.

## Screenshots

- `tmp/ui-qa/2026-04-13-research-corpus-landing-106/root_spanish_de.png`
- `tmp/ui-qa/2026-04-13-research-corpus-landing-106/root_spanish_en.png`
- `tmp/ui-qa/2026-04-13-research-corpus-landing-106/root_french_de.png`
- `tmp/ui-qa/2026-04-13-research-corpus-landing-106/design_spanish_de_locked_sidebar.png`
- `tmp/ui-qa/2026-04-13-research-corpus-landing-106/gate_spanish_speakers_de.png`
- `tmp/ui-qa/2026-04-13-research-corpus-landing-106/speakers_spanish_de_auth.png`
- `tmp/ui-qa/2026-04-13-research-corpus-landing-106/metrics.json`

## Offene Punkte

- Die Ursache für den stale Dev-Server auf `127.0.0.1:8000` wurde in diesem Run nicht dauerhaft beseitigt; maßgeblich abgeschlossen wurde die isolierte aktuelle Instanz auf `127.0.0.1:8001`.
- Der breitere Player-Testblock benötigt weiterhin eine vollständig initialisierte SQLAlchemy-/Set-Engine-Harness, wenn künftig der gesamte File-Umfang statt fokussierter Access-/IA-Regressionen grün laufen soll.

## Nächste sinnvolle Schritte

- Die Standard-Dev-Instanz auf `127.0.0.1:8000` so bereinigen, dass sie denselben aktuellen Workspace-Stand wie die isolierte QA-Instanz rendert.
- Den kleinen Selenium-Capture unter `tmp/ui-qa/2026-04-13-research-corpus-landing-106/` bei weiteren Research-IA-Änderungen fortschreiben, statt neue manuelle Screenshotpfade aufzubauen.