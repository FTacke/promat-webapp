# Auth Login Polish

Datum: 2026-04-13

## Ziel

Gezielter Korrektur- und Qualitätslauf für die bereits umgesetzte Auth-/Login-Phase: sichtbare Copy und Branding schärfen, die vorkonfigurierte Zugangsanfrage vervollständigen, den lokalen Dev-Admin zuverlässig nutzbar machen, die Admin-Benutzeroberfläche funktional und CSP-sauber machen und den Stand mit echten Browser-Artefakten abnahmefähig verifizieren.

## Consulted Sources

- `docs/plans/auth_login_plan.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- Root `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `docs/runbooks/ui-change-workflow.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- Bestehende Auth-/Admin-Implementierung unter `app/src/app/routes/`, `app/src/app/auth/`, `app/templates/auth/` und `app/static/js/auth/`

## Geänderte Bereiche

- Zentrale Access-Request- und Auth-Helfer unter `app/src/app/auth/services.py`
- Public-, Auth- und Admin-Routen unter `app/src/app/routes/public.py`, `app/src/app/routes/auth.py` und `app/src/app/routes/admin.py`
- Kontext-/Template-Helfer unter `app/src/app/__init__.py`
- Dev-Bootstrap unter `app/scripts/create_initial_admin.py`, `app/scripts/dev-start.ps1` und `app/scripts/dev-setup.ps1`
- Bilinguale Copy unter `app/src/app/i18n.py`
- Auth-/Admin-Templates unter `app/templates/auth/`
- Admin-Clientlogik unter `app/static/js/auth/admin_users.js`
- Fokussierte Regressionen unter `app/tests/test_auth_phase1.py`
- Aktive Plattformregeln unter `docs/spec/platform-data-files.md`
- Browser-QA-Artefakte unter `tmp/ui-qa/2026-04-13-auth-login-polish-105/`

## Wichtige Entscheidungen

- Die sichtbare Produktbezeichnung auf Auth-/Admin-Oberflächen ist `Pronunciation Matters`; `PROMAT` bleibt interne Kurzform.
- Die Zugangsanfrage bleibt eine zentral konfigurierte `mailto`-Strecke ohne öffentliche Registrierung und mit vollständig vorbefülltem Inhalt.
- Admin-Invite- und Reset-Mails werden weiterhin nur vorbereitet, angezeigt und geloggt; ein echter SMTP-Versand wurde bewusst nicht in diesen Run gezogen.
- Für die Admin-Benutzerseite wurden die JS-Konfiguration und das Asset-Laden so umgestellt, dass keine blockierten Inline-Skripte mehr nötig sind und geänderte JS-Dateien nicht an altem Browser-Cache hängen bleiben.
- Die kanonische lokale Dev-Startstrecke seeded bzw. aktualisiert den nutzbaren Admin-Zugang über `felix.tacke@uni-marburg.de`.

## Abweichungen

- Keine Abweichung von den konsultierten aktiven Specs für Research-Access, Routenstruktur oder Runtime-Grenzen.
- Kein produktiver Mailversand in diesem Run; die Admin-Oberfläche bleibt bei ehrlicher manueller Versandvorbereitung.
- Der finale Browser-Log enthält nur noch Edge-Tracking-Prevention-Warnungen zur externen Bootstrap-Icons-CDN-Einbindung auf der Login-Seite; kein app-eigener CSP- oder JS-Fehler blieb bestehen.

## Verifikation

- Editor-Fehlerprüfung der geänderten Python-, Template- und JS-Dateien ohne verbleibende Probleme.
- Regressionstestlauf mit Workspace-Python:
  - `pytest app/tests/test_auth_phase1.py app/tests/test_research_capabilities.py app/tests/test_research_comparison.py -q`
  - Ergebnis: `33 passed`
- Reale Browser-QA gegen den laufenden Dev-Stack auf `http://127.0.0.1:8000` mit Selenium/Edge und frischem Profil pro Lauf.
- Erzeugte Artefakte unter `tmp/ui-qa/2026-04-13-auth-login-polish-105/`, darunter:
  - `login_de.png`, `login_en.png`
  - `forgot_de.png`, `forgot_en.png`, `forgot_en_success.png`
  - `gate_comparison_de.png`, `gate_comparison_en.png`
  - `comparison_de_auth.png`, `comparison_en_auth.png`
  - `admin_users_de.png`, `admin_users_en.png`, `admin_invite_en.png`
  - `reset_setup_de.png`, `reset_setup_en.png`
  - `metrics.json`
- Verifiziert in `metrics.json`:
  - vollständige `mailto`-Vorkonfiguration in `de` und `en`
  - intakte `next`-/Redirect-Logik für geschützte Research-Routen
  - englischer Admin-Invite-Betreff und englischer Reset-Link mit `ui_lang=en`
  - lokaler Dev-Admin `felix.tacke@uni-marburg.de` aktiv und nutzbar

## Offene Punkte

- Die Login-Seite lädt `bootstrap-icons` weiter über CDN; Edge meldet dafür im Headless-Log Tracking-Prevention-Warnungen. Das ist kein funktionaler Auth-Fehler, kann aber bei Bedarf später auf lokales Asset-Hosting umgestellt werden.
- Der QA-Run hat zusätzliche Testnutzer in der lokalen Dev-Datenbank angelegt; das ist für die lokale Prüfumgebung akzeptiert, aber kein Produktionspfad.

## Nächste sinnvolle Schritte

- Falls die externen CDN-Warnungen verschwinden sollen, Bootstrap Icons lokal ausliefern oder auf die bereits vorhandenen Material Symbols konsolidieren.
- Falls gewünscht, im nächsten separaten Run einen echten Versandkanal auf die jetzt bereinigten Invite-/Reset-Previews aufsetzen.