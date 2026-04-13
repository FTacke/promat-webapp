# Auth Login Phase 1

Datum: 2026-04-13

## Ziel

Die erste Umsetzungsphase aus `docs/plans/auth_login_plan.md` produktiv in PROMAT verankern: E-Mail-only-Login, admin-erzeugte Konten, 14-Tage-Einladungs-/Reset-Links, `mailto`-Zugangsanfrage, aktive/inaktive/abgelaufene Konten, bilinguale Auth-Oberflächen und systemische Regressionen.

## Consulted Sources

- `docs/plans/auth_login_plan.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- Root `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- Bestand in `app/src/app/routes/auth.py`, `app/src/app/routes/admin.py`, `app/src/app/routes/public.py`, `app/src/app/auth/models.py`, `app/src/app/auth/services.py`, `app/src/app/i18n.py`
- Bestehende Auth-Templates und das Admin-JS unter `app/templates/auth/` und `app/static/js/auth/`

## Geänderte Bereiche

- Auth-Konfiguration und Service-Layer unter `app/src/app/config/` und `app/src/app/auth/`
- Auth-, Public- und Admin-Routen unter `app/src/app/routes/`
- Bilinguale Auth- und Admin-Oberflächen unter `app/templates/auth/` und `app/static/js/auth/`
- Übersetzungskatalog unter `app/src/app/i18n.py`
- Fokussierte Auth-Regressionen unter `app/tests/test_auth_phase1.py`
- Aktive Plattform-Spezifikation unter `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- Das bestehende SQLAlchemy-/JWT-Auth-Grundgerüst wurde ausgebaut statt ersetzt.
- `username` bleibt als interne Altlast im Datenmodell bestehen, ist aber kein öffentlicher Login-Identifier mehr; die produktive Oberfläche und die Lookup-Logik sind E-Mail-only.
- Einladungs- und Reset-Nachrichten werden real erzeugt und serverseitig geloggt; die Admin-Oberfläche zeigt Link, Betreff und Nachrichtentext zum manuellen Versand an, statt einen fiktiven Mailversand zu behaupten.
- Die aktive Spezifikation wurde in `docs/spec/platform-data-files.md` verdichtet statt eine neue konkurrierende Auth-Spec einzuführen.

## Abweichungen

- Keine Abweichung von den konsultierten aktiven Specs bei Routing, Runtime-Grenzen oder Research-Access.
- Kein SMTP-/Outbox-Dispatcher wurde in dieser Phase eingeführt; stattdessen wird der erzeugte Mailinhalt transparent angezeigt und geloggt.

## Verifikation

- Statische Fehlerprüfung der geänderten Python-, Template- und JS-Dateien mit dem VS-Code-Problemcheck.
- Neue fokussierte Regressionen in `app/tests/test_auth_phase1.py` für E-Mail-only-Login, Reset-/Setup-Token, Account-Expiry und Admin-Einladung.
- Geplante Browser-Abnahme auf `127.0.0.1:8000` nach lokalem Testlauf.

## Offene Punkte

- Die bestehende Account-Self-Service-Strecke außerhalb des explizit umgesetzten Phase-1-Kerns bleibt nur teilweise modernisiert.
- Für produktiven Mailversand ist weiterhin ein expliziter Versandkanal nötig; diese Phase erzeugt und dokumentiert die Inhalte, versendet sie aber nicht automatisch.

## Nächste sinnvolle Schritte

- Die neue Auth-Testsuite lokal ausführen und verbleibende Integrationsfehler bereinigen.
- Browser-QA für `/login`, `/auth/password/forgot`, `/auth/password/reset` und `/admin/users/page` in `de` und `en` gegen die laufende App durchführen.
- Falls produktiver Versand gewünscht ist, eine klar spezifizierte SMTP-/Mailer-Stufe auf den jetzt vorhandenen Nachrichtengeneratoren aufsetzen.