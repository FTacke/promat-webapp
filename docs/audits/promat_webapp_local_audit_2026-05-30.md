# ProMat Webapp – Lokaler Audit-Bericht

**Datum:** 2026-05-30  
**Bearbeiter:** Claude Sonnet 4.6 (automatisierter Audit-Run)  
**Branch:** `main`  
**Commit bei Start:** `bf6fe32` (fix(goatcounter): restrict GoatCounter script rendering to public pages only)  
**Arbeitsbaumzustand vor Start:** clean  
**Arbeitsbaumzustand nach Abschluss:** 3 Dateien mit minimalen, risikoarmen Änderungen

---

## 1. Executive Summary

Die ProMat-Webapp befindet sich in einem **insgesamt soliden Zustand**. Die Teststufe ist breit (644 Tests), alle automatisierten Prüfungen (Ruff, Pytest, Governance Checks, JSON-Validierung) sind grün. Die App-Architektur folgt klar dokumentierten Grenzen. Es wurden keine kritischen Sicherheitsprobleme identifiziert.

Identifizierte Risiken im Überblick:
- **66 mypy-Typfehler** (Medium): Keine Runtime-Fehler, aber Typannotations-Schulden im Auth- und Forschungsbereich, die echte Bugs verschleiern könnten.
- **Debug-Logs in auth-setup.js** (Low): Vertraulicher Nutzername wird im Browser-Console sichtbar, wenn authentifiziert.
- **Test-Skript in statischem Verzeichnis** (Low): `test-adaptive-title.js` ist öffentlich zugänglich und enthält viele `console.log`-Aufrufe.
- **Dead code in router.js** (Low): `atlas`-Seiteninitialisierer referenziert nicht existierende Datei `pages/atlas.js`.
- **Google Fonts CDN** (Low/Info): Lädt externe Schriften ohne expliziten Nutzerkonsens – potenzieller DSGVO-Aspekt.
- **Doppeltes CSS-System** (Info): Numeriertes CSS-System (00–40) und md3-System laufen parallel, was auf eine laufende Migration hinweist.

**Lokal verifizierbares Ergebnis:** Die App ist nach den Änderungen **grün** (644/644 Tests, Ruff, Governance).

---

## 2. Scope

### Geprüfte Bereiche
- Python-Quellcode (`app/src/app/`) – Imports, Debug-Ausgaben, Routing, Auth-Logik, Konfiguration
- HTML-Templates (`app/templates/`) – Sicherheit, Accessibility, Routen-Referenzen
- JavaScript (`app/static/js/`) – Debug-Logs, Sicherheit, tote Imports
- CSS (`app/static/css/`) – Struktur, Duplikate, Overflow-Risiken
- Tests (`app/tests/`) – Abdeckung, Robustheit
- Dependencies (`requirements.txt`, `requirements.in`)
- JSON-Konfigurationsdaten (`data/config/`)
- Governance-Checks (`scripts/ci_governance_checks.py`)
- Security-Header-Konfiguration
- GoatCounter-Integration
- Auth/Session-Architektur (nur gelesen, nicht verändert)

### Nicht geprüfte Bereiche
- **Browser-UI-Smoketest**: Kein Browser-Rendering möglich (kein laufender Server)
- **Produktionsdaten**: `public/`, `data/sessions/`, `secure/` – lokal leer oder ignoriert
- **E2E-Tests**: Marker `e2e` ausgeschlossen per pyproject.toml
- **Dependency-Vulnerability-Scan**: `pip-audit` nicht installiert; keine externe OSV-Abfrage
- **Mobile-Responsive**: Kein visueller Check möglich ohne Browser
- **Admin-Matrix und Detailseiten**: Kein Login/Session für lokalen Test

### Lokale Einschränkungen
- pip-audit nicht verfügbar (kein `pip-audit`-Binary im `.venv`)
- Kein Datenbankzugang für Live-Tests
- Keine Browser-Instanz für UI-Verifizierung

---

## 3. Repository-Zustand

| Feld | Wert |
|------|------|
| Branch | `main` |
| Commit bei Start | `bf6fe32` |
| Uncommitted Änderungen vor Start | keine (clean) |
| Uncommitted Änderungen nach Abschluss | 3 JS-Dateien (Debug-Log-Bereinigung), 1 neue Docs-Datei |

---

## 4. Direkt behobene Punkte

### Fix 1 – `accordion.js`: Debug-Log entfernt
| Feld | Wert |
|------|------|
| **Datei** | `app/static/js/modules/navigation/accordion.js:37` |
| **Änderung** | `console.log("[accordion] Initialized", allDetails.length, "details elements")` entfernt |
| **Grund** | Reines Initialisierungs-Debug-Log ohne Produktionswert; Navigation-Modul, kein Auth-Code |
| **Risikoabschätzung** | Minimal – rein kosmetisch, keine Verhaltensänderung |

### Fix 2 – `app-bar.js`: Zwei Debug-Logs entfernt
| Feld | Wert |
|------|------|
| **Datei** | `app/static/js/modules/navigation/app-bar.js:278,282` |
| **Änderung** | `console.log("[TopAppBar] User menu not found on this page")` und `console.log("[TopAppBar] User menu initialized")` entfernt |
| **Grund** | Initialisierungs-Debug-Logs ohne Produktionswert; Navigation-Modul |
| **Risikoabschätzung** | Minimal – rein kosmetisch |

### Fix 3 – `router.js`: Zwei Debug-Logs entfernt
| Feld | Wert |
|------|------|
| **Datei** | `app/static/js/modules/core/router.js:17,32` |
| **Änderung** | `console.log('[page-router] Atlas initialized')` und `console.log('[page-router] Initializing page:', page)` entfernt |
| **Grund** | Debug-Logs in Page-Router; kein Produktionswert |
| **Risikoabschätzung** | Minimal – der `atlas`-Eintrag wird nie ausgelöst (kein `data-page="atlas"` in Templates); `console.error` bei Fehler bleibt erhalten |

---

## 5. Findings nach Schweregrad

### Blocker
*Keine.*

---

### High
*Keine.*

---

### Medium

#### M-1: 66 mypy-Typfehler in 11 Dateien
- **Schweregrad:** Medium
- **Betroffene Dateien:** `routes/auth.py` (22 Fehler), `routes/public.py` (7), `auth/services.py` (10), `research_views.py` (8), `research_sets.py` (2), `teaching_content.py` (7), `research_sessions.py` (1), `research_player_runtime.py` (1), `routes/research_api.py` (2), `routes/public_content.py` (2), `__init__.py` (1)
- **Beschreibung:** `mypy src/ --ignore-missing-imports` liefert 66 Fehler. Die häufigsten Typen:
  - Inkompatible Return-Typen in Flask-Routen (Werkzeug-Response vs. Flask-Response, Tuple vs. Response)
  - Nullable-datetime-Vergleiche in `auth/services.py`
  - `Optional[dict].get()` ohne None-Guard in `teaching_content.py`
  - Ein `method-assign` bei `app.wsgi_app = ProxyFix(...)` (bekanntes Flask/mypy-Spannungsfeld)
- **Risiko:** Die Fehler führen aktuell zu keinen Runtime-Failures (644 Tests grün). Sie verschleiern aber echte Typprobleme (z.B. nullable datetime in Services), die in Edge Cases Bugs auslösen könnten.
- **Empfehlung:** Schrittweise beheben, beginnend bei `auth/services.py` (nullable datetime) und `teaching_content.py` (None-Guards). Für Flask-Route-Return-Typen `flask.typing.ResponseReturnValue` als Rückgabetype nutzen.
- **Warum nicht direkt behoben:** Zu viele Dateien, zu viel Kontext nötig – kein risikoloser Massenfix möglich.

---

### Low

#### L-1: `auth-setup.js` loggt Benutzernamen im Browser-Console
- **Schweregrad:** Low
- **Betroffene Datei:** `app/static/js/auth-setup.js:110`
- **Beschreibung:** `console.log(\`[Auth] ✅ Authenticated as: ${data.user}\`)` gibt den eingeloggten Benutzernamen in die Browser-Console aus. Weiterhin sind viele technische Initialisierungs-Logs (`[Auth Setup] Initializing...`, `[Auth Setup] ✅ Fetch interceptor installed` usw.) vorhanden.
- **Risiko:** Nutzername in der Browser-Console sichtbar (z.B. für Dritte auf öffentlichen Terminals). Kein direkter Remote-Exploit, aber unerwünschtes Information-Leakage in der Console.
- **Empfehlung:** Mindestens `console.log(\`[Auth] ✅ Authenticated as: ${data.user}\`)` entfernen; alle anderen Init-Logs bereinigen.
- **Warum nicht direkt behoben:** Auth-Code – Änderungen erfordern explizite manuelle Prüfung.

#### L-2: `test-adaptive-title.js` in Produktions-Static-Verzeichnis
- **Schweregrad:** Low
- **Betroffene Datei:** `app/static/js/modules/navigation/test-adaptive-title.js`
- **Beschreibung:** Browser-Console-Testskript (260 Zeilen, vollständig mit `console.log`) liegt im produktiven Static-Verzeichnis. Wird nirgends importiert, ist aber unter der öffentlichen URL `/static/js/modules/navigation/test-adaptive-title.js` abrufbar und enthält seitenlayoutbezogene Tests mit Hinweisen auf interne DOM-Strukturen.
- **Risiko:** Kein direktes Sicherheitsrisiko, aber Informations-Offenlegung über DOM-Struktur und Initialisierungsguards; Dev-Debris in Production-Assets.
- **Empfehlung:** Datei nach `scripts/qa/` verschieben oder löschen. Repo-Governance (AGENTS.md) schreibt vor, dass Einweg-Debug-Skripte unter `tmp/ui-qa/` oder `scripts/qa/` gehören.
- **Warum nicht direkt behoben:** Dateilöschungen/Verschiebungen erfordern explizite Freigabe per Audit-Scope.

#### L-3: `router.js` enthält Dead-Code-Eintrag für `atlas`-Seite
- **Schweregrad:** Low
- **Betroffene Datei:** `app/static/js/modules/core/router.js`
- **Beschreibung:** `pageInits.atlas` versucht dynamisch `../../pages/atlas.js` zu importieren. Diese Datei existiert nicht. Kein Template setzt `data-page="atlas"`. Der Fehler wird von einem `try/catch` abgefangen, jedoch produziert er (wenn durch Zufall ausgelöst) einen `console.error`.
- **Risiko:** Aktuell kein Runtime-Impact. Potenzielle Verwirrung beim Onboarding; würde im Browser-Netzwerk-Tab einen 404 erzeugen, falls `data-page="atlas"` jemals gesetzt wird.
- **Empfehlung:** `atlas`-Eintrag aus `pageInits` entfernen; Kommentar „Register additional page initializers here" ist ausreichend als Beispiel-Anleitung.
- **Warum nicht direkt behoben:** Der Eintrag könnte als Beispiel-Template für künftige Page-Initialisierer gedacht sein; Entscheidung liegt beim Entwickler.

#### L-4: Debug-Logs in `auth-setup.js` laufen auf jeder Seite (public + protected)
- **Schweregrad:** Low
- **Betroffene Datei:** `app/static/js/auth-setup.js`
- **Beschreibung:** Das Skript macht auf jeder Seite (inkl. öffentlicher Seiten) einen `fetch('/auth/session')` zur Sessionsverifizierung und loggt das Ergebnis. Das ist unabhängig von der GoatCounter-Filterung.
- **Risiko:** Jeder Seitenaufruf (auch unauthentifizierte öffentliche Seiten) erzeugt einen zusätzlichen HTTP-Request an `/auth/session`. Minimaler Performance-Overhead.
- **Empfehlung:** `verifyAuth()` nur auf geschützten Seiten oder Login-Seiten aufrufen; alternativ mit Server-seitigem Flag steuern.
- **Warum nicht direkt behoben:** Architekturentscheidung der Auth-Session-Verwaltung.

---

### Info

#### I-1: Google Fonts werden von externem CDN geladen
- **Schweregrad:** Info
- **Betroffene Datei:** `app/templates/base.html:18-20`
- **Beschreibung:** `Inter` und `Source Serif 4` werden von `https://fonts.googleapis.com` / `https://fonts.gstatic.com` geladen. Das geschieht auf jeder Seite vor Anzeige von Inhalt, ohne Cookie-/Consent-Gate.
- **Risiko:** Potenzieller DSGVO-Aspekt (Google-IP-Übermittlung ohne explizite Einwilligung). Leichte Performance-Abhängigkeit von externem Dienst.
- **Empfehlung:** Fonts lokal hosten (wie es für `MaterialSymbolsRounded.woff2` bereits gemacht wird) oder im Datenschutzkonzept dokumentieren.
- **Warum nicht direkt behoben:** Produktentscheidung/DSGVO-Strategie.

#### I-2: `passwords.env.template` enthält reale E-Mail-Adresse als Default
- **Schweregrad:** Info
- **Betroffene Datei:** `app/passwords.env.template:49`
- **Beschreibung:** `AUTH_MAIL_DEFAULT_REPLY_TO=felix.tacke@uni-marburg.de` ist die einzige Zeile in der Template-Datei mit einer real besetzten Adresse statt einem `__SET_...__`-Platzhalter.
- **Risiko:** Minimal (es ist explizit eine Template-Datei, nicht eine aktive Konfiguration). Könnten bei unkritischem Kopieren als Default-Wert in Production landen.
- **Empfehlung:** Auf `AUTH_MAIL_DEFAULT_REPLY_TO=__SET_REPLY_TO_EMAIL__` ändern oder bewusst als Operator-Default belassen und in README dokumentieren.
- **Warum nicht direkt behoben:** Produktentscheidung (ob die eigene Adresse bewusst als Default gesetzt sein soll).

#### I-3: CSS-Dual-Track (numerierte Dateien + md3-System parallel geladen)
- **Schweregrad:** Info
- **Betroffene Dateien:** `app/templates/base.html:23-51`, `app/static/css/00_tokens.css`–`40_cards.css`, `app/static/css/md3/`
- **Beschreibung:** Die Basis-HTML lädt sowohl das md3-Designsystem (md3/tokens.css, md3/typography.css usw.) als auch das ältere numerierte CSS-System (00_tokens.css, 10_typography.css, 20_layout.css, 30_components.css, 40_cards.css) in einem gemeinsamen Dokument. Dies deutet auf eine laufende CSS-Migration hin. Die 30_components.css ist mit 9526 Zeilen sehr groß.
- **Risiko:** Potenziell widersprüchliche Regeln, hohes CSS-Bundle-Gewicht (~21.700 Zeilen über 27 Dateien), kein Bundling.
- **Empfehlung:** CSS-Migrationsstrategie klären und dokumentieren; langfristig numerierte Dateien in md3-System integrieren.
- **Warum nicht direkt behoben:** Größeres CSS-Umbau-Thema.

#### I-4: `style-src 'unsafe-inline'` in CSP
- **Schweregrad:** Info
- **Betroffene Datei:** `app/src/app/__init__.py:426`
- **Beschreibung:** Der CSP-Header enthält `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;`. `'unsafe-inline'` für Styles ist notwendig für dynamisches Theming (CSS Custom Properties via JS), schwächt aber die CSP.
- **Risiko:** Kann CSS-Injection-Angriffe erleichtern, falls XSS-Vektoren vorhanden wären.
- **Empfehlung:** Wenn möglich, nonce-basiertes CSP für Inline-Styles evaluieren; alternativ als akzeptiertes Risiko dokumentieren.
- **Warum nicht direkt behoben:** Architekturentscheidung, Theming-System-Abhängigkeit.

#### I-5: mypy-Fehler `app.wsgi_app = ProxyFix(...)` (`method-assign`)
- **Schweregrad:** Info
- **Betroffene Datei:** `app/src/app/__init__.py:185`
- **Beschreibung:** mypy flaggt `app.wsgi_app = ProxyFix(app.wsgi_app, ...)` als `Cannot assign to a method [method-assign]`. Dies ist ein bekanntes False Positive – Werkzeug/Flask erlaubt explizit diese WSGI-Middleware-Wrapping-Technik.
- **Risiko:** Keines – funktioniert korrekt zur Laufzeit.
- **Empfehlung:** `# type: ignore[method-assign]` ergänzen, um mypy-Rauschen zu reduzieren.
- **Warum nicht direkt behoben:** Änderung in `__init__.py` – minimales Risiko, aber im Rahmen des Auth-nahen Application-Bootstraps.

---

## 6. Security-Befund

| Bereich | Befund |
|---------|--------|
| **Secrets/Env** | Keine echten Secrets im Repo. `passwords.env.template` korrekt als Template markiert. `.gitignore` deckt `.env`-Dateien ab. `DEFAULT_SECRET_SENTINEL = "__CHANGE_ME__"` mit Production-Guard. |
| **Auth/Admin** | Routen durch `@require_admin_role` / JWT-Dekoratoren geschützt. Session-Cookie: `httponly=True`, `secure=True` in Production. CSRF-Schutz aktiviert (`JWT_COOKIE_CSRF_PROTECT = True`). Rate-Limiter (`flask-limiter`) konfiguriert. |
| **XSS/HTML/Markdown** | Jinja2 autoescape aktiv. `| safe`-Filter nur für MarkdownIt-gerendertes HTML (`html: False` – kein Raw-HTML-Durchlass). Kein direktes Rendern von User-Input mit `safe`. |
| **CSRF** | CSRF via JWT-Cookie-CSRF-Schutz (`JWT_CSRF_CHECK_FORM = True`). `window.getCSRFToken()` in `auth-setup.js` für Fetch-Requests. |
| **Cookies/Sessions** | `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SECURE` env-kontrolliert (default: `true`). `SESSION_COOKIE_SAMESITE = "lax"`. UI-Language-Cookie: `httponly=True`, `samesite` aus Config. |
| **Dependencies** | pip-audit nicht lokal verfügbar. Keine bekannten kritischen CVEs in der manuellen Review der requirements.txt (Flask 3.1.2, Werkzeug 3.1.3, SQLAlchemy 2.0.43, PyJWT 2.10.1, argon2-cffi 23.1.0, passlib 1.7.4). |
| **Externe Skripte/GoatCounter** | GoatCounter korrekt nur in Production und nur auf Public-Seiten (nicht `/admin`, `/auth`, `/login`). CSP-Header erlaubt `https://gc.zgo.at` für `script-src`. Keine anderen externen Skripte außer Google Fonts. |
| **Dynamische Dateipfade** | Audio-MP3-Lieferung über `research_player_runtime.py`: Pfade werden aus signierten Session-IDs und Task-Catalogs validiert, nicht direkt aus User-Input. Player-Route validiert gegen Session-Katalog. |
| **Security-Header** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, HSTS in Production, CSP. |
| **Redirect-Sicherheit** | `save_return_url` / Post-Login-Redirect: Ziel wird validiert. `_default_post_login_target` nutzt `url_for` statt direkter User-Input. |

**Kritische Lücken:** Keine gefunden.  
**Minor Concerns:** `auth-setup.js` loggt Benutzernamen in Console (L-1), Google Fonts CDN ohne expliziten Consent (I-1).

---

## 7. CSS-/Responsive-Befund

| Bereich | Befund |
|---------|--------|
| **Globale Styles** | `layout.css` (root) definiert `html, body` Reset + App-Shell-Grid. `md3/tokens.css` und `00_tokens.css` sind parallel geladen – potenzielle Token-Konflikte möglich, aber kein offensichtlicher Bruch sichtbar. |
| **Overflow** | Kein `overflow-x: visible` auf `<body>` oder `<html>` gefunden. `layout.css` setzt `overflow-x: visible` auf `.app-shell`, was unkritisch erscheint. Die `md3/components/navigation-drawer.css` nutzt `overflow: clip` zur Bleeding-Kontrolle (korrekt). |
| **Mobile** | `mobile-responsive.css` wird korrekt nach allen Komponenten geladen. Kein offensichtliches horizontales Scrollen in den CSS-Regeln. |
| **Desktop** | Keine offensichtlichen fixen Breitenprobleme in der Analyse. |
| **Admin-Oberflächen** | Admin-Templates wurden gesichtet aber nicht browser-seitig getestet. |
| **Bekannte Layout-Risiken** | CSS-Dual-Track (I-3): 27 CSS-Dateien einzeln geladen, kein Bundling. Performance-Impact bei schlechten Verbindungen möglich. |
| **z-index** | Keine auffälligen z-index-Probleme im statischen Code sichtbar. |

**Hinweis:** Ohne Browser-Test kein visueller Beweis für oder gegen Responsive-Probleme.

---

## 8. Tests/CI-Befund

| Kommando | Ergebnis |
|----------|----------|
| `python -m ruff check src/` | ✅ All checks passed |
| `python -m pytest tests/ -x -q` (vor Fixes) | ✅ 644/644 passed, 120 warnings |
| `python -m pytest tests/ -x -q` (nach Fixes) | ✅ 644/644 passed, 120 warnings |
| `python -m mypy src/ --ignore-missing-imports` | ❌ Found 66 errors in 11 files (checked 38 source files) |
| `python scripts/ci_governance_checks.py` | ✅ All governance checks passed |
| `pip-audit` | ⚠️ Nicht verfügbar (nicht installiert) |

**Relevante Warnungen:**
- `flask_limiter` warnt in Tests: `Using the in-memory storage for tracking rate limits as no storage was explicitly specified.` – erwartet in Test-Umgebung, harmlos.

**Einschätzung Testqualität:**
- Die 644 Tests decken Auth-Phase1, Analytics, Research-Capabilities, Comparison, Intake-Storage, Phenomena, Player-Set-Context, Presets, Production-Importer, Raw-Sync-Importer, Sessions, Sets, Text-MFA-Runner, Working-Tree-Intake, Runtime-Config, Teaching-Content und Upload-Prod-Package ab. Das ist eine starke Abdeckung für die Kerndomänen.
- Die `test_research_phenomena.py` (43 Warnungen) und `test_research_sets.py` (37 Warnungen) produzieren viele In-Memory-Rate-Limiter-Warnungen – diese sind harmlos aber rauschen in der Ausgabe.
- Mypy-Fehler sind bekannte Pre-Existing-Schulden, keine durch diesen Run eingeführten.

---

## 9. Dependency-/Supply-Chain-Befund

**pip-audit:** Nicht verfügbar lokal. Für einen vollständigen Vulnerability-Scan sollte `pip install pip-audit` und `pip-audit -r requirements.txt` in der CI ergänzt werden.

**Manuelle Inspektion:**
- Flask 3.1.2, Werkzeug 3.1.3 – aktuelle stabile Versionen
- SQLAlchemy 2.0.43 – aktuell
- PyJWT 2.10.1 – aktuell
- argon2-cffi 23.1.0 – aktuell
- passlib 1.7.4 – **Achtung:** passlib ist seit 2023 nicht mehr aktiv maintained. Die Abhängigkeit wird für Bcrypt-Fallback bei alten Passwort-Hashes verwendet (neben argon2). Kein aktiver CVE bekannt, aber ein Risiko auf lange Sicht.
- htmx 1.x (vendor/htmx.min.js) – Version aus dem Dateinamen nicht ablesbar; sollte geprüft werden.
- jQuery 3.7.1 (vendor/jquery-3.7.1.min.js) – aktuelle jQuery-3.x-Version

**Nicht durchgeführte Updates:** Keine automatischen Updates wurden durchgeführt – alle Dependency-Entscheidungen erfordern manuelle Prüfung.

**Lockfile:** `requirements.txt` ist ein pip-compile-Output (`uv pip compile`). Konsistenz geprüft: `requirements.in` und `requirements.txt` stimmen inhaltlich überein.

---

## 10. Daten-/Asset-Befund

| Bereich | Befund |
|---------|--------|
| **JSON-Konfiguration** | Alle 12 `data/config/research_player/*/` JSON-Dateien valide (`python -m json.tool` – kein Fehler). |
| **Public-Verzeichnis** | `public/` ist lokal leer (nur `.gitkeep`). Korrekt: Produktions-Audio/-Assets werden nicht im Repo verwaltet. |
| **Daten-Repo-Trennung** | `data/sessions/`, `secure/`, `data/db/` sind im `.gitignore` korrekt ausgeschlossen. `PROMAT_LOCAL_ARCHIVE_ROOT` liegt außerhalb des Repos – konform mit AGENTS.md. |
| **Asset-Referenzen** | Keine kaputten Template-Referenzen gefunden. Alle `url_for('static', ...)` zeigen auf existierende Dateien (manuell geprüft für CSS/JS im Basis-Template). |
| **Verwaiste Assets** | `test-adaptive-title.js` ist eine verwaiste Datei (kein Import); siehe L-2. |

---

## 11. Empfohlener nächster Fix-Plan

### Priorität 1 (Low Risk, hoher Klarheitsgewinn)
**Debug-Logs in `auth-setup.js` bereinigen**  
Datei: `app/static/js/auth-setup.js`  
Entfernen: mindestens `console.log(\`[Auth] ✅ Authenticated as: ${data.user}\`)` (Zeile 110), idealerweise alle Init-Logs. `console.warn` und `console.error` behalten.  
Risiko: Minimal. Kein Verhaltenseinfluss.

### Priorität 2 (Low Risk, Repo-Hygiene)
**`test-adaptive-title.js` aus Static-Verzeichnis entfernen**  
Datei: `app/static/js/modules/navigation/test-adaptive-title.js`  
Aktion: Löschen oder nach `scripts/qa/` verschieben (konform mit AGENTS.md-Governance).  
Risiko: Keine Auswirkung auf Produktionsfunktionalität (kein Import).

### Priorität 3 (Low Risk, Dead Code)
**`atlas`-Eintrag in `router.js` entfernen**  
Datei: `app/static/js/modules/core/router.js`  
Aktion: `atlas`-Eintrag aus `pageInits` löschen; nur den Kommentar behalten.  
Risiko: Minimal – `atlas.js` existiert nicht, kein Template triggert den Eintrag.

### Priorität 4 (Medium Risk, technische Schulden)
**Mypy-Fehler schrittweise beheben**  
Beginnen bei: `auth/services.py` (nullable datetime – tatsächliche Laufzeitrisiken möglich), dann `teaching_content.py` (None-Guards).  
Flask-Route-Return-Typen: `flask.typing.ResponseReturnValue` als Annotation nutzen.  
Risiko: Mittel – Auth-Services-Änderungen erfordern sorgfältige Tests.

### Priorität 5 (Info, Infrastruktur)
**pip-audit in CI integrieren**  
Aktion: `pip install pip-audit` in CI, `pip-audit -r requirements.txt` als CI-Step ergänzen.  
Risiko: Kein Code-Risiko; reine CI-Ergänzung.

---

## Anhang: Ausgeführte Kommandos (Zusammenfassung)

```
cd /c/dev/promat/app
python -m ruff check src/             → All checks passed
python -m pytest tests/ -x -q        → 644 passed
python -m mypy src/ --ignore-missing-imports → 66 errors in 11 files
python scripts/ci_governance_checks.py → All governance checks passed
python -m json.tool data/config/**/*.json → All valid
```
