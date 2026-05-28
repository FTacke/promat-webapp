# 2026-05-28 Auth-Mail-Flows

## Bestand

- Admin-Einladungs- und Passwortlinks wurden bereits in `app/src/app/routes/admin.py` erzeugt. Die Zustellung lief ueber `app.services.mail_delivery.send_mail(MailMessage(...))`; dieses gehaertete Modul blieb der zentrale Versandweg.
- Admin-Mailtexte wurden bisher in der Admin-Route aufgebaut. Die oeffentliche Passwort-zuruecksetzen-Seite hatte eine HTML-Route unter `/auth/password/forgot` und einen API-Pfad `/auth/reset-password/request`, versendete aber keine Mail.
- Die Zielroute zum Setzen eines Passworts existierte bereits unter `/auth/password/reset?token=...`.
- Technisch existiert ein gemeinsamer `ResetToken`-Flow fuer Account-Aktivierung/Ersteinrichtung und Passwort-Reset. `create_reset_token_for_user` invalidiert alte unbenutzte Tokens fuer denselben User; die Gueltigkeit bleibt 14 Tage, sofern die Umgebung `AUTH_RESET_TOKEN_EXP_DAYS` nicht anders setzt.
- Links nutzten bereits `ui_lang` auf der Passwort-Setzen-Route.
- Bestehende Tests fuer Mailversand, Fehlerhaertung, Rate-Limits, Login/Auth und Admin-User-Flows liegen vor allem in `app/tests/test_auth_phase1.py`.

## Aenderungen

- Mail-Subjects und Bodies fuer Einladung und Passwortlink sind jetzt zentral in `app/src/app/services/auth_mail_messages.py` strukturiert.
- Relevante Mails nutzen personalisierte Anreden:
  - Deutsch: `Hallo Vorname Nachname,`
  - Englisch: `Hello Firstname Lastname,`
  - mit Teilnamen-Fallback und generischer Anrede bei fehlendem Namen.
- Einladungsmails beschreiben jetzt fachlich den angelegten Nutzeraccount und optional die persoenliche Notiz.
- Passwortmails beschreiben neutral den Link zum Festlegen eines neuen Passworts.
- Admin-Formulare bieten eine Mail-Sprache `de`/`en`; ungueltige Werte fallen serverseitig auf `de` zurueck. Die Sprache steuert Betreff, Body und `ui_lang` im Link.
- Bestehende User koennen im Bearbeiten-Dialog jetzt getrennt eine Einladung vorbereiten oder eine Passwort-Mail vorbereiten.
- Die oeffentliche Reset-Seite sendet per JavaScript an `/auth/password/reset/request`; HTML-Fallback ueber `/auth/password/forgot` bleibt erhalten.
- `docs/spec/platform-data-files.md` dokumentiert den neuen Reset-Request-Endpunkt und die Mail-/Token-Regeln.

## Mailtemplates

- Einladung DE: `Ihr Nutzeraccount fuer Pronunciation Matters`
- Einladung EN: `Your Pronunciation Matters user account`
- Passwort DE: `Neues Passwort fuer Pronunciation Matters festlegen`
- Passwort EN: `Set a new password for Pronunciation Matters`

Platzhalter werden zentral fuer Anzeigename, Link, persoenliche Notiz, Kontaktadresse und Gueltigkeit gefuellt. Die persoenliche Notiz erscheint nur, wenn sie vorhanden ist.

## Sicherheit

- Account-Enumeration: oeffentliche Reset-Requests antworten fuer vorhandene und nicht vorhandene Adressen gleich neutral.
- Token-Logging: Tokens, komplette Links, Mailbody und volle E-Mail-Adressen werden nicht routinemaessig geloggt.
- Token-Gueltigkeit: 14 Tage per bestehender Konfiguration.
- Token-Invalidierung: neue Reset-/Setup-Tokens invalidieren alte unbenutzte Tokens fuer denselben User.
- Rate-Limiting: bestehende Flask-Limiter-Regeln bleiben aktiv (`5/min` fuer oeffentliche Forgot/Reset-Requests, `10/min` fuer Admin-Mailvorbereitung).
- Mailfehler: oeffentliche Requests geben keine technischen Details aus; Admin-Versand nutzt weiter die vorhandene kontrollierte Fehlerbehandlung.

## Lokale Dev-Pruefung

- App lokal mit vorhandener App-Fabrik und sendmail-kompatiblem QA-Stub gestartet. Wegen eines verwaisten lokalen Listeners auf Port 8000 lief die Browser-QA auf `127.0.0.1:8001`; die App-Konfiguration und das Mailmodul waren unveraendert.
- Geprueft:
  - Admin: neuen User anlegen und DE-Einladung senden.
  - Admin: bestehendem User EN-Einladung senden.
  - Admin: bestehendem User DE-Passwortmail senden.
  - Oeffentlich: vorhandene Adresse DE.
  - Oeffentlich: nicht vorhandene Adresse EN.
  - Oeffentlich: vorhandene Adresse EN.
- Ergebnis: 5 Mails wurden im lokalen Stub-Outbox-Verzeichnis erfasst; die nicht vorhandene Adresse erzeugte keine Mail und dieselbe neutrale Erfolgsmeldung. Screenshots liegen als temporaere QA-Artefakte unter `tmp/ui-qa/2026-05-28-auth-mail-flows/`.

## Tests

- `python -m pytest tests/test_auth_phase1.py -q`
- `python -m ruff check src/app/routes/auth.py src/app/routes/admin.py src/app/services/auth_mail_messages.py tests/test_auth_phase1.py`

Weitere Projektchecks wurden im Abschlusslauf ausgefuehrt und im finalen Handoff zusammengefasst.

## Deployment / Server-To-dos

- Keine DB-Migration.
- Keine neuen Env-Variablen.
- Keine neuen Dependencies.
- Keine neue Server-Mailkonfiguration noetig. Der bestehende funktionierende Admin-Mailversand verwendet weiterhin dasselbe `mail_delivery`-Modul.
- Server-To-do: nur den App-Code deployen. SMTP-/sendmail-Konfiguration muss nicht angepasst werden.
