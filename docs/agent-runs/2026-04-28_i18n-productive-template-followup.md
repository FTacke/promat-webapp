# 2026-04-28 · I18n Productive Template Follow-up

## Scope

Remediation-Schritt 2b/4 mit bewusst enger Slice vor der Designsystem-Migration:

- verbleibende sichtbare i18n-Schulden in produktionsnahen Account-/Auth-Surfaces prüfen
- `app/templates/auth/account_profile.html` und `app/templates/auth/account_delete.html` bereinigen
- sichtbare Account-Statusmeldungen in den zugehörigen produktionsnahen JS-Dateien zentralisieren
- übrige Auth-Templates und angrenzende Public-/Stub-Surfaces klassifizieren, aber nicht breit umbauen
- fokussierte Regressionen und Grep-Nachweise ergänzen

Nicht Teil dieses Schritts:

- neue Routing- oder Auth-Architektur
- Reaktivierung eines `/auth/refresh`-Flows
- Designsystem-Migration oder größere Public-/Sample-Umbauten
- neue aktive Produktregeln in `docs/spec/`

## Ausgangsbefund aus Schritt 2/4

Nach Schritt 2/4 blieben zwei klar sichtbare Account-/Auth-Restflächen übrig:

- `app/templates/auth/account_profile.html`
- `app/templates/auth/account_delete.html`

Beide Templates enthielten direkte sichtbare UI-Copy für Seitentitel, Überschriften, Formularlabels, Gefahrenzonen- und Löschdialog-Texte.

Der kleine Folgecheck zeigte zusätzlich:

- `app/static/js/auth/account_profile.js` und `app/static/js/auth/account_delete.js` trugen noch sichtbare Status- und Fehlermeldungen als Hardcodings
- die übrigen produktiven Auth-Templates in `app/templates/auth/` waren bereits weitgehend auf die zentrale Übersetzungsschicht gezogen

## Geänderte Dateien

- `app/src/app/i18n.py`
- `app/templates/auth/account_profile.html`
- `app/templates/auth/account_delete.html`
- `app/static/js/auth/account_profile.js`
- `app/static/js/auth/account_delete.js`
- `app/tests/test_auth_phase1.py`
- `docs/agent-runs/2026-04-28_i18n-productive-template-followup.md`

## Neue oder geänderte i18n-Keys

Neu ergänzt in `app/src/app/i18n.py`:

- `auth.account_profile.*` für Titel, Heading, Intro, Feldlabels, Gefahrenzonen-Texte und Profile-JS-Meldungen
- `auth.account_delete.*` für Löschseite, Löschdialog, Button-Labels und Delete-JS-Meldungen
- `auth.account_password.error.submit`
- `auth.account_password.error.network`

Die neuen Keys folgen der bestehenden `auth.account*`-Familie und eröffnen keine parallele Namenslogik.

## Bereinigte Account-/Auth-Templates

Bereinigt:

- `app/templates/auth/account_profile.html`
  - sichtbare Überschriften, Labels, Buttons und Dialogtexte auf `t(...)` umgestellt
  - JS-Statusmeldungen über ein serverseitig lokalisiertes JSON-Config-Template an `account_profile.js` übergeben
  - Passwort-Link auf `ui_lang`-bewahrenden `url_for(...)` vereinheitlicht

- `app/templates/auth/account_delete.html`
  - sichtbare Überschriften, Warntexte, Passwortlabel und Actions auf `t(...)` umgestellt
  - JS-Statusmeldungen über ein serverseitig lokalisiertes JSON-Config-Template an `account_delete.js` übergeben
  - Rücklink auf `auth_ui_lang` vereinheitlicht

Zusätzlich bereinigt:

- `app/static/js/auth/account_profile.js`
  - sichtbare Save-/Delete-Statusmeldungen lesen jetzt lokalisiertes Template-Config statt harter Strings

- `app/static/js/auth/account_delete.js`
  - sichtbare Erfolgs-/Fehlermeldungen lesen jetzt lokalisiertes Template-Config statt harter Strings

Bereits sauber bzw. nicht erneut angefasst:

- `app/templates/auth/login.html`
- `app/templates/auth/access_request.html`
- `app/templates/auth/password_forgot.html`
- `app/templates/auth/password_reset.html`
- `app/templates/auth/account_password.html`
- `app/templates/auth/admin_users.html`

Produktiver Referenzanker bleibt weiterhin `app/templates/pages/account.html`; dieser Schritt hat die alte MD3-Account-Familie bereinigt, ohne den kanonischen produktiven Account-Flow umzubauen.

## Klassifizierte Public-/Stub-Surfaces

Im angefragten Klassifizierungs-Check bestätigt:

- `app/templates/pages/research_player_stub.html`
  - Stub-Surface mit sichtbaren `if ui_lang == 'de'`-Branches
  - bewusst nicht in 2b/4 mitgezogen

- `app/src/app/routes/public.py`
  - größere öffentliche/sample-nahe Builder-Bestände mit direkten DE/EN-Branches
  - nicht kleine lokale Auth-Schuld, sondern eigener Public-/Sample-Folgeblock

- `app/src/app/routes/public_content.py`
  - öffentliche Inhalts-/Langtext-Schicht mit Sprachverzweigung
  - keine Account-/Auth-Template-Schuld

- `app/src/app/research_capabilities.py`
  - verbleibende `ui_lang`-Verzweigungen liegen im kanonischen Capability-Modell mit getrennten DE/EN-Feldern
  - für 2b/4 bewusst nicht angetastet

Zusätzliche Legacy-Klassifizierung:

- `app/static/js/auth/account_password.js`
  - Datei existiert weiter, ist aber derzeit ungebunden: keine Template-Referenzen im Repo
  - zudem erwartet sie DOM-IDs, die nicht zur produktiven Passwortseite passen
  - deshalb für 2b/4 als Legacy-/Dead-Asset klassifiziert statt mit neuer produktiver Bindung aufgezogen

## Bewusst nicht geänderte Bereiche

- keine Änderungen an `app/src/app/__init__.py`, Auth-Routing oder Session-Architektur
- keine Spezifikationsänderung unter `docs/spec/`, weil keine aktive Produktregel geändert wurde
- keine Bereinigung der größeren Public-/Sample-/Stub-Flächen mit `if ui_lang == ...`-Branches
- keine Reaktivierung oder Neuverkabelung von Legacy-Assets wie `account_password.js`
- keine Browser-/Screenshot-Abnahme, weil hier keine substantial UI-Umgestaltung oder produktive Layout-Änderung vorlag, sondern Copy-Zentralisierung und Legacy-Klassifizierung

## Tests

Ergänzt in `app/tests/test_auth_phase1.py`:

- direkte Template-Regression für `auth/account_profile.html` in Englisch
- direkte Template-Regression für `auth/account_delete.html` in Englisch
- beide Regressionen prüfen sichtbare Copy und die lokalisierten JS-Meldungen im serverseitigen Config-Payload

Ausgeführt:

- `python -m pytest app/tests/test_auth_phase1.py -q`
- `python -m pytest app/tests/test_research_sessions.py -q`

Ergebnis:

- `39 passed`
- `180 passed`

## Grep-/Regressionsergebnisse

Gezielte Nachkontrollen nach der Änderung:

- keine Treffer für die bereinigten Rohstrings wie `Dein Profil`, `Grunddaten`, `Gefahrenzone`, `Konto löschen?`, `Bestätigung erforderlich` oder rohe `Abbrechen`-/`Löschen`-Buttons mehr unter `app/templates/auth/**/*.html`
- keine `if ui_lang == 'de'`-Branches unter `app/templates/auth/**/*.html`
- `account_profile.html` und `account_delete.html` werden außerhalb der neuen Regressionen nicht produktiv referenziert; der Suchtrefferbestand besteht nur aus den beiden neuen Tests
- `account_password.js` hat keine Referenzen im Repo und bleibt deshalb als ungebundene Legacy-Datei klassifiziert
- gezielte Suchen in `app/templates/**`, `app/static/**` und `app/src/app/routes/**` ergaben keine Frontend-/Route-Treffer für `/auth/refresh`, `initAuthRefresh`, `token-refresh` oder `refreshToken`
- breite App-Suche auf `refreshToken` trifft nur noch Backend-Modelle und Service-Code rund um `RefreshToken`, nicht mehr produktive Frontend-Bootstraps

## Offene Folgepunkte für Schritt 3/4

- Public-/Sample-/Stub-Flächen mit direkten `ui_lang`-Branches gesammelt in Schritt 3/4 oder einem separaten Public-i18n-Block entscheiden
- Legacy-MD3-Account-Surfaces mittelfristig entweder endgültig entfernen oder sauber in die produktive Navigations-/Template-Landschaft einordnen
- ungebundene Legacy-Assets wie `app/static/js/auth/account_password.js` im Zuge der Designsystem-/Template-Konsolidierung bereinigen oder löschen