# Auth Admin Research UI Tuning 108

Datum: 2026-04-13

## Ziel

Reiner Layout- und UI-Nachjustierungsrun für die bereits modernisierten Auth-Flächen, die Admin-Benutzerverwaltung und die neue öffentliche Research-Korpus-Landingpage: globale Navbar- und Sidebar-Abstände reparieren, verbliebene sichtbare MD3-Reste aus der Admin-Oberfläche entfernen, die öffentliche Auth-Nebenstrecke ruhiger und klarer machen, die Research-Korpus-Landingpage von doppelter Intro-Copy bereinigen und das Ergebnis mit fokussierten Tests plus realer Browser-QA auf `127.0.0.1:8000` abnehmen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/runbooks/ui-change-workflow.md`
- Runtime-Wiring geprüft: `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `docker-compose.dev-postgres.yml`, `app/infra/docker-compose.prod.yml`
- Repo-Memory geprüft: `/memories/repo/promat-dev-setup-notes.md`, `/memories/repo/promat-doc-system-notes.md`, `/memories/repo/promat-research-ui-notes.md`, `/memories/repo/promat-shell-notes.md`
- Produktive Referenzflächen geprüft: `app/templates/pages/research_comparison.html`, `app/templates/pages/research_player.html`, `app/templates/pages/research_recordings.html`, `app/templates/partials/_top_app_bar.html`, `app/templates/partials/_navigation_drawer.html`, `app/static/css/20_layout.css`, `app/static/css/30_components.css`, `app/static/css/40_cards.css`

## Geänderte Bereiche

- Shared Shell- und Komponenten-CSS in `app/static/css/30_components.css`
- Öffentliche Auth-Templates in `app/templates/auth/login.html`, `app/templates/auth/password_forgot.html` und `app/templates/auth/password_reset.html`
- Admin-Benutzerverwaltung in `app/templates/auth/admin_users.html` und `app/static/js/auth/admin_users.js`
- Auth-Rendering und bilinguale Copy in `app/src/app/routes/auth.py` und `app/src/app/i18n.py`
- Öffentliche Research-Korpus-Landingpage in `app/templates/pages/research_language_root.html`
- Fokussierte Regressionen in `app/tests/test_auth_phase1.py` und `app/tests/test_research_sessions.py`

## Wichtige Entscheidungen

- Die globalen Navbar- und Sidebar-Abstände wurden als Shared-CSS-Problem behandelt und nicht seitenlokal gepatcht.
- Die Admin-Benutzerverwaltung wurde sichtbar vollständig in die aktuelle PROMAT-Komponentenfamilie überführt, ohne Rollenmodell, Menüarchitektur oder Invite-/Reset-Logik funktional umzubauen.
- Für die öffentlichen Auth-Flächen blieb die Zugangsanfrage eine sekundäre, ruhigere Support-Sektion unterhalb des Primärflows; keine öffentliche Registrierung und kein funktionaler Access-Rebuild wurden eingeführt.
- Eine breite Änderung der authentifizierten `auth_profile_skeleton`-Familie wurde bewusst vermieden, um die außerhalb des Scopes liegenden `account_*`-Seiten nicht mitzuziehen.
- Der Run wurde erst nach echter Browserprüfung geschlossen; ein im Screenshot sichtbarer doppelter Admin-Header wurde nach grünen Tests noch entfernt und erneut verifiziert.

## Abweichungen

- Keine Abweichung von den konsultierten aktiven Specs; für diesen Run waren keine zusätzlichen Spec-Änderungen nötig.
- Vor der Live-QA bestand eine lokale Runtime-Abweichung: stale globale `python.exe -m src.app.main`-Listener belegten `127.0.0.1:8000` und lieferten veraltetes HTML aus. Die Prozesse wurden beendet und die kanonische Startstrecke `scripts/dev-start.ps1` wurde erneut verwendet.
- Im QA-Ordner liegt zusätzlich ein vorläufiges `smoke.png` aus dem initialen Browser-Smoke-Test. Es ist kein eigener Abnahmescreenshot, bleibt aber als Hilfsartefakt dokumentiert erhalten.

## Verifikation

- Editor-Fehlerprüfung der geänderten Template-, CSS-, JS- und Python-Dateien ohne verbleibende relevante Fehler.
- Fokussierter Pytest-Lauf:
  - `pytest app/tests/test_auth_phase1.py app/tests/test_research_sessions.py -q`
  - Ergebnis: `151 passed`
- Laufzeitprüfung nach Runtime-Bereinigung:
  - `http://127.0.0.1:8000/health` antwortete mit `200`
- Reale Browser-QA mit Headless Edge gegen `http://127.0.0.1:8000` für:
  - `/login?ui_lang=de`
  - `/login?ui_lang=en`
  - `/auth/password/forgot?ui_lang=de`
  - `/auth/password/forgot?ui_lang=en`
  - `/auth/password/reset?token=...&ui_lang=de`
  - `/auth/password/reset?token=...&ui_lang=en`
  - `/de/research/spanish`
  - `/en/research/spanish`
  - `/de/research/spanish/design`
  - `/admin/users/page?ui_lang=de`
  - `/admin/users/page?ui_lang=en`
  - Admin-Dialoge für Create, Invite und Edit in `de` und `en`
- Shared-CSS-Regressionscheck explizit auch auf einer unbetroffenen Research-Seite mit Sidebar/Lock-Zustand (`design_locked_sidebar_de.png`) durchgeführt.
- Nach dem ersten Screenshot-Review wurde der doppelte innere Titel-/Intro-Block in der Admin-Tabelle entfernt und die betroffenen Admin-Screenshots erneut erzeugt.

## Screenshots

- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/login_de.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/login_en.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/forgot_de.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/forgot_en.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/reset_set_password_de.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/reset_set_password_en.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/research_spanish_de.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/research_spanish_en.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/design_locked_sidebar_de.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/admin_users_de.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/admin_users_en.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/admin_create_dialog_de.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/admin_create_dialog_en.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/admin_invite_dialog_de.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/admin_invite_dialog_en.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/admin_edit_dialog_de.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/admin_edit_dialog_en.png`
- `tmp/ui-qa/2026-04-13-auth-admin-research-ui-tuning-108/metrics.json`

## Offene Punkte

- Die authentifizierten `account_*`-Seiten außerhalb dieses Scopes verwenden weiterhin ältere Strukturen und wurden bewusst nicht in denselben globalen Umbau hineingezogen.
- Für künftige Browser-QA auf `127.0.0.1:8000` bleibt stale Runtime-Hygiene ein reales Risiko; vor visueller Abnahme sollte weiter zuerst geprüft werden, welcher Listener tatsächlich HTML ausliefert.

## Nächste sinnvolle Schritte

- Falls die verbleibenden authentifizierten Account-Seiten ebenfalls in die aktuelle PROMAT-Familie überführt werden sollen, diesen Ausbau in einem separaten gezielten Run angehen.
- Falls weitere Shared-Shell-Anpassungen nötig werden, dieselbe Kombination aus fokussierten Tests, Live-HTML-Prüfung und Screenshot-Rerun beibehalten, damit Runtime-Drift nicht wieder visuelle Fehlurteile erzeugt.