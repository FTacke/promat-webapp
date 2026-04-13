# Protected-Area Finalization

Datum: 2026-04-13

## Ziel

Admin- und Kontobereich produktiv finalisieren, den aktiven Rollen- und Navigationsvertrag auf `user` und `admin` reduzieren, die realen Konto- und Adminflächen umsetzen und die Änderungen per Tests plus Live-Browser-QA prüfen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- Auth-Rollen-, Nutzer- und Profillogik unter `app/src/app/auth/`
- Auth- und Admin-Routen unter `app/src/app/routes/`
- Shared protected-navigation-Helfer unter `app/src/app/protected_navigation.py`
- Privacy-safe Analytics unter `app/src/app/analytics.py`
- Konto-, Passwort-, Admin-Users- und Analytics-Templates unter `app/templates/`
- Shared Topbar- und Drawer-Navigation unter `app/templates/partials/`
- Shared Layout- und Komponenten-CSS unter `app/static/css/`
- Admin-Users-Clientlogik unter `app/static/js/auth/admin_users.js`
- Migrationen und Admin-Bootstrap-Skripte unter `app/migrations/` und `app/scripts/`
- Aktive Plattform-Spec unter `docs/spec/platform-data-files.md`
- Fokus-Regressionen unter `app/tests/test_auth_phase1.py`

## Wichtige Entscheidungen

- Produktive Rollen bleiben nur `user` und `admin`; Legacy-`editor` wird serverseitig auf `user` normalisiert statt weiter im UI mitzuschwingen.
- Der geschützte Standardzielpfad nach dem Login ist rollenbasiert: `user -> /auth/account`, `admin -> /admin/users/page`.
- Admin nutzt keine separate Dashboard-Fläche mehr; `/admin` und `/admin/dashboard` leiten direkt auf die Benutzerverwaltung.
- Protected Admin-Seiten reuse-en den gemeinsamen Inner-Shell mit fixer linker Navigation `Benutzer`, `Analytics`, `Mein Konto`, `Logout`.
- Analytics bleiben anonymisiert und aggregiert; gezählt werden nur fachliche PROMAT-Seiten ohne Admin-Routen und ohne personenbezogene Ereignisprotokolle.
- Konto-Seiten ohne Drawer müssen explizit als `app-shell--panel-hidden` gerendert werden, damit der Desktop-Shell-Grid nicht auf die Sidebar-Spalte kollabiert.

## Abweichungen

- Keine fachliche Abweichung von der aktiven Spec.
- Für die Live-QA wurde temporär ein separater Dev-Runner auf Port `8010` verwendet, weil der Listener auf `8000` während des Runs stale HTML mit altem `/auth/konto`-Verhalten auslieferte.

## Verifikation

- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py -q` -> `16 passed`
- Zuvor im Run: fokussierte Public-Shell-Regressionen aus `app/tests/test_research_sessions.py` erfolgreich ausgeführt; breitere Player/Research-Set-Fehler erwiesen sich als separater Altbestand.
- Headless Edge Live-QA gegen `http://127.0.0.1:8010` mit Admin- und User-Login in `de` und `en`.
- Geprüfte Live-Flächen: Admin Users, Create-Dialog, Edit-Dialog, Admin Analytics, Admin Account, Admin Password, User Account, User Password.
- Browser-Artefakte abgelegt unter `tmp/ui-qa/protected-area-final/`, inklusive `qa_report.json` und aktualisierten Screenshots nach dem Drawerless-Account-Fix.

## Offene Punkte

- Der Dev-Listener auf Port `8000` zeigte während der QA stale Runtime-Inhalte und sollte bei Bedarf separat bereinigt werden, bevor weitere Browser-Abnahmen dort stattfinden.
- Die breiteren Fehler in `app/tests/test_research_sessions.py` (`Engine not initialized`, fehlende `ResearchSetStorageUnavailableError`) gehören nicht zu diesem Protected-Area-Run und bleiben separat zu verfolgen.

## Nächste sinnvolle Schritte

- Stalen Dev-Listener auf `8000` bereinigen oder den QA-Runner formal als wiederholbaren Ablauf in ein Runbook überführen, falls das Problem erneut auftritt.
- Die separaten Research-Player- und Research-Set-Regressionsfehler in einem eigenen Run isolieren und beheben.