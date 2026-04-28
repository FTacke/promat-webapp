# 2026-04-28 · Auth Session and App Factory Remediation

## Scope

Remediation-Schritt 1/4 mit Fokus auf:

- produktive Auth-/Session-Architektur
- Entfernung aktiver Frontend-Refresh-Drift
- Konsolidierung der App-Fabrik in `app/src/app/__init__.py`
- kanonische 401/403-/Logout-Regressionen

Nicht Teil dieses Schritts:

- groessere i18n-Bereinigung ausserhalb unmittelbarer Error-/Auth-Pfade
- Designsystem-/Layout-Konsolidierung
- CI-/GitHub-Haertung

## Ausgangsbefund

Der produktive JS-Bootstrap initialisierte einen aktiven Auth-Refresh-Loop ueber `app/static/js/main.js`.

Produktiv beteiligt waren:

- `app/static/js/main.js`
- `app/static/js/modules/auth/refresh.js`
- `app/static/js/modules/auth/token-refresh.js`
- `app/static/js/pages/research-comparison.js`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/static/js/pages/research-phenomena-overview.js`

Diese Pfade erwarteten einen `/auth/refresh`-Endpoint, der im aktuellen Backend-Routing nicht vorhanden ist.

Zusatzbefund in `app/src/app/__init__.py`:

- doppelte `setup_logging(...)`-Definitionen
- konkurrierende `@app.errorhandler(...)`-Bloecke
- Legacy-Produktname `CO.RA.PAN`
- uneinheitliche Fehlerbehandlung zwischen dem fruehen und spaeteren Handler-Block

## Architekturentscheidung

Fuer den aktuellen PROMAT-Stand gilt jetzt explizit:

- kein produktiver clientseitiger Refresh-Loop
- kein produktiver Aufruf von `/auth/refresh`
- servergetriebener Cookie-/JWT-Flow ohne implizite JS-Sessionerneuerung
- JWT-Fehler fuer geschuetzte HTML-/API-Routen bleiben zentral im Extension-Layer geregelt
- generische 400/401/403/404/500-Fehler laufen ueber genau einen Handler-Registrierungspfad in `app/src/app/__init__.py`
- Logging laeuft ueber genau einen aktiven Dateihandler-Pfad ohne Legacy-Namen

## Geänderte Dateien

- `app/static/js/main.js`
- `app/static/js/pages/research-comparison.js`
- `app/static/js/pages/research-phenomena-editor.js`
- `app/static/js/pages/research-phenomena-overview.js`
- `app/static/js/modules/auth/fetch.js`
- `app/src/app/__init__.py`
- `app/tests/test_auth_phase1.py`

Entfernt:

- `app/static/js/modules/auth/refresh.js`
- `app/static/js/modules/auth/token-refresh.js`

## Entfernte oder deaktivierte Refresh-Pfade

- `initAuthRefresh()` aus dem produktiven Bootstrap entfernt
- produktive Imports von `modules/auth/refresh.js` entfernt
- tote Refresh-Module geloescht
- Workbench-Seiten auf einen neutralen `fetchWithAuth(...)`-Wrapper ohne Refresh-Logik umgestellt

## Kanonisches Session-/Auth-Verhalten

- Login setzt weiterhin Access-Cookies serverseitig ueber `set_access_cookies(...)`
- Logout entfernt JWT-Cookies ueber `unset_jwt_cookies(...)`
- `/auth/session` liefert den aktuellen Auth-Status fuer denselben Cookie-Flow
- geschuetzte HTML-Routen ohne Auth werden ueber den JWT-Layer zum Login umgeleitet
- geschuetzte API-Routen ohne Auth liefern JSON-401-Antworten
- generische 401- und 403-Pfade bleiben getrennt und fuer HTML bzw. API konsistent

## Bereinigtes Error-/Logging-Modell

`app/src/app/__init__.py` enthaelt jetzt:

- genau einen aktiven `setup_logging(...)`-Pfad
- genau einen aktiven `register_error_handlers(...)`-Pfad
- eine gemeinsame Entscheidungshilfe fuer JSON- versus HTML-Fehlerantworten
- keinen konkurrierenden spaeteren Handler-Block mehr
- keinen Legacy-Logdateinamen `corapan.log` und keinen Startup-String `CO.RA.PAN`

Zusaetzlich wurde `setup_logging(...)` in `create_app(...)` nach `load_config(...)` vor die spaetere App-Initialisierung gezogen, damit fruehe Runtime-/DB-Logs im produktiven Betrieb denselben Handler verwenden.

## Tests

Fokussiert ergaenzt oder abgesichert in `app/tests/test_auth_phase1.py`:

- Logout entfernt Auth-Zustand und leert Access-Cookie
- geschuetzte HTML-Route ohne Auth fuehrt zum Login-Redirect
- geschuetzte API-Route ohne Auth liefert JSON-401
- generische HTML-401 rendert die 401-Seite
- generische API-401 liefert JSON-Fehler
- generische HTML-403 rendert die 403-Seite
- generische API-403 liefert JSON-Fehler

Ausgefuehrte Tests:

- `python -m pytest app/tests/test_auth_phase1.py -q`
- `python -m pytest app/tests/test_research_sessions.py -q`

Ergebnis:

- `31 passed`
- `178 passed`

## Grep-/Regressionsergebnisse

Nach der Bereinigung ergaben gezielte Produktiv-Suchen:

- keine Treffer fuer `/auth/refresh` unter `app/static`, `app/src`, `app/templates`, `app/tests`
- keine Treffer fuer `initAuthRefresh` oder `token-refresh` in produktiven Codepfaden
- keine Treffer fuer `CO.RA.PAN` unter `app/src` und `app/templates`

## Offene Folgepunkte für Schritt 2/4, 3/4 oder 4/4

### Fuer Schritt 2/4

- Error-Seiten und Footer bleiben sichtbar hartcodiert und sollten in die zentrale Uebersetzungsschicht ueberfuehrt werden
- mehrere produktive Templates und Builder enthalten weiterhin lokale UI-Copy statt zentraler i18n-Nutzung

### Fuer Schritt 3/4

- Auth-/Error-Seiten verwenden weiterhin den vorhandenen visuellen Mix aus Shared-PM- und MD3-orientierten Strukturen
- das ist bewusst in diesem Schritt unberuehrt geblieben

### Fuer Schritt 4/4

- CI prueft diese neue Slice derzeit nicht automatisch ausser ueber manuelle Testausfuehrung
- Security-/Governance-Artefakte in `.github/` bleiben separat zu haerten