# Final Controlled Cleanup + Prod Smoke

## 1. Scope

Geprüft wurden die letzten sicheren MD3-/CSS-/JS-Namensreste und die aktuelle Prod-Smoke-Fähigkeit nach den vorherigen Cleanup-Runs.

Geändert wurde nur klein und aliasbasiert:

- `md3-button--loading` im Auth-Login-JS auf `pm-action-button--loading` migriert.
- Alert/Snackbar-JS rendert jetzt zusätzlich PM-konforme Klassen (`pm-alert`, `pm-snackbar`, `pm-form-error`), behält aber MD3-Klassen als Styling-Brücke.

Ausdrücklich nicht geändert wurden Layout, Mobile-Verhalten, Typografie, Farben, Google Fonts, Icons, Content, Teaching-Inhalte, Auth-/Security-Grenzen, CSP und globale MD3-Dateien.

## 2. Kurzfazit

- Phase 1 umgesetzt: `md3-button--loading` entfernt.
- Phase 2 umgesetzt: PM-Aliasse für Alert/Snackbar/Form-Error ergänzt, MD3-Styling-Klassen behalten.
- Phase 3 umgesetzt als Prüfung: `pm-content-wrapper` und `pm-footer-shell` sind produktiv; `md3-content-wrapper` und `md3-footer` bleiben bewusst als kurze Stabilitätsaliasse.
- Phase 4 umgesetzt als Kartierung: globale aktive MD3-Schichten bleiben vor Prod vertretbar.
- Phase 5 Final Prod Smoke: stabil.
- Prod-Readiness-Entscheidung: `prod-ready with documented operational prerequisites`.

## 3. Phasenbericht

### Phase 1: `md3-button--loading`

Referenzsuche:

- Treffer nur in `app/static/js/modules/auth/login.js`.
- Keine CSS-Regel für `md3-button--loading`; der State war ein JS-only Marker.

Änderung:

- `md3-button--loading` zu `pm-action-button--loading` migriert.

Validierung:

- `compileall`: bestanden.
- Fokussierte Tests: 279 passed.
- Responsive Smoke `2026-05-26-final-controlled-cleanup-phase1`: 30 Route/Viewport-Checks, 0 Overflow, 0 Static 404, 0 Runtime-Console-Errors.

### Phase 2: Alert/Snackbar-Namen

Referenzsuche:

- `alert-utils.js` rendert `md3-alert*`.
- `modules/core/snackbar.js` rendert `md3-snackbar*`.
- `modules/auth/login.js` erzeugt im AJAX-Fallback `md3-form-error md3-snackbar`.
- CSS bleibt in `alerts.css` und `snackbar.css` aktiv.

Änderung:

- Alert-Markup rendert jetzt zusätzlich `pm-alert*`.
- Snackbar-Markup rendert jetzt zusätzlich `pm-snackbar*`.
- Login-Form-Error rendert jetzt zusätzlich `pm-form-error` und `pm-snackbar*`.
- MD3-Klassen bleiben für Styling-Kompatibilität erhalten.

Validierung:

- `compileall`: bestanden.
- Fokussierte Tests: 279 passed.
- Node JS tests: 7 passed.
- Responsive Smoke `2026-05-26-final-controlled-cleanup-phase2`: 30 Route/Viewport-Checks, 0 Overflow, 0 Static 404, 0 Runtime-Console-Errors.

### Phase 3: Wrapper/Footer-Aliasse

Referenzsuche:

- Produktive Templates nutzen `pm-content-wrapper` und `pm-footer-shell`.
- `md3-content-wrapper` existiert nur noch als CSS-Alias in `layout.css`, `20_layout.css` und `mobile-responsive.css`.
- `md3-footer` existiert nur noch als CSS-Alias in `footer.css`.

Entscheidung:

- Aliasse bleiben. Die Stabilitätsphase ist noch kurz, und die Aliasse sind layoutneutral.
- Spätere Entfernung erst nach erneutem Referenzcheck und Smoke.

### Phase 4: Aktive globale MD3-Dateien

| Datei | Warum noch aktiv? | Kann vor Prod bleiben? | Risiko | Späterer Pfad |
|---|---|---:|---|---|
| `buttons.css` | Global geladen; JS kennt noch `.md3-icon-button`; Tests sichern keine Template-MD3-Buttons. | ja | niedrig/mittel | Button-JS/CSS-State separat migrieren. |
| `alerts.css` | Styling für `alert-utils.js`; PM-Klassen wurden nur additiv ergänzt. | ja | niedrig | CSS auf PM-Selektoren aliasieren, dann MD3 entfernen. |
| `snackbar.css` | Styling für Core Snackbar und Flash-Messages. | ja | niedrig | PM-Selektoren im CSS ergänzen, MD3 nach Stabilität entfernen. |
| `layout.css` | Foundation für alte Layout/Form/Table-Utilities. | ja | mittel | Utility-Audit separat. |
| `typography.css` | Foundation für alte MD3-Typografieklassen. | ja | niedrig | Nur mit Visual Regression migrieren. |
| `tokens.css` | MD3/PM-Brücken-Foundation. | ja | mittel | Token-Foundation langfristig vereinheitlichen. |
| `navigation-drawer.css` | Sichtbarer Drawer. | ja | mittel | Separate Shell-Migration. |
| `top-app-bar.css` | Sichtbare Topbar. | ja | mittel | Separate Shell-Migration. |
| `mobile-responsive.css` | Mobile Overflow-/Responsive-Schutz. | ja | mittel | Nur nach weiterer Mobile-QA reduzieren. |

## 4. Änderungen

| Datei | Kurzgrund |
|---|---|
| `app/static/js/modules/auth/login.js` | `pm-action-button--loading`, `pm-form-error`, `pm-snackbar` eingeführt; MD3-Kompatibilitätsklassen für Error-Snackbar bleiben. |
| `app/static/js/md3/alert-utils.js` | Alert-Markup rendert zusätzlich PM-Klassen. |
| `app/static/js/modules/core/snackbar.js` | Snackbar-Markup rendert zusätzlich PM-Klassen; Dismiss-Query akzeptiert PM/MD3. |
| `docs/agent-runs/2026-05-26_final-controlled-cleanup-prod-smoke.md` | Abschlussbericht. |

Hinweis: Die bereits uncommitted CSS-/Template-Änderungen aus den vorherigen MD3-Cleanup-Runs bleiben Teil des Working Tree, wurden hier nicht zurückgerollt.

## 5. Beibehaltene Legacy-/MD3-Reste

- `md3-alert*`, `md3-snackbar*`, `md3-form-error`: bleiben als Styling-Brücke, jetzt mit PM-Pendants im Markup.
- `md3-footer`: bleibt als Footer-Shell-Alias.
- `md3-content-wrapper`: bleibt als Wrapper-Alias.
- `buttons.css`, `alerts.css`, `snackbar.css`, `layout.css`, `typography.css`, `tokens.css`, `navigation-drawer.css`, `top-app-bar.css`, `mobile-responsive.css`: bleiben aktiv geladen, weil sie Shell-, Foundation-, Alert/Snackbar- oder Mobile-Schutzfunktionen haben.

Vor Prod vertretbar, weil Tests und Smoke stabil sind und die Reste keine falsche Runtime-Grenze, kein Security-Problem und keinen sichtbaren Mobile-/Layout-Blocker darstellen.

## 6. Final Prod Smoke

### Tests

```text
.\.venv\Scripts\python.exe -m compileall app -q
```

Ergebnis: bestanden.

```text
.\.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q
```

Ergebnis: 66 passed.

```text
.\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -q
```

Ergebnis: 201 passed.

```text
.\.venv\Scripts\python.exe -m pytest app/tests/test_teaching_content.py -q
```

Ergebnis: 36 passed.

```text
.\.venv\Scripts\python.exe -m pytest app/tests/test_research_phenomena.py -q
```

Ergebnis: 17 passed, 17 bekannte Flask-Limiter-Testmodus-Warnungen.

```text
.\.venv\Scripts\python.exe -m pytest app/tests -q -k "navigation or mobile or drawer or responsive or csp or security_headers or access_request or player or teaching or footer or auth or runtime_config"
```

Ergebnis: 283 passed, 191 deselected, 33 bekannte Flask-Limiter-Testmodus-Warnungen.

```text
node --test app/tests/js/*.test.mjs
```

Ergebnis: 7 passed.

Optional:

```text
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe .
```

Ergebnis: `ruff` und `mypy` sind lokal nicht in `.venv` verfügbar.

### Responsive Smoke

```text
.\.venv\Scripts\python.exe scripts\qa\responsive_smoke.py --run-id final-prod-smoke
```

Artefakte:

- `tmp/ui-qa/final-prod-smoke/summary.json`
- `tmp/ui-qa/final-prod-smoke/smoke_results.json`
- `tmp/ui-qa/final-prod-smoke/overflow_results.json`
- `tmp/ui-qa/final-prod-smoke/screenshots/`

Ergebnis:

- 30 Route/Viewport-Checks
- 2 Drawer-Checks
- 2 Access-Request-Validation-Checks
- 0 Overflow
- 0 Static 404
- 0 Runtime Console Errors
- 2 erwartbare `400 (BAD REQUEST)`-Console-Meldungen beim absichtlich leeren Access-Request-Submit

### Docker/Compose

Erster Check ohne vollständige Pflichtvariablen stoppte erwartbar bei fehlendem `POSTGRES_PASSWORD`.

Mit Platzhalter-Secrets:

```text
docker compose -f app/infra/docker-compose.prod.yml config
```

Ergebnis: bestanden. Rendered config enthält Redis-Rate-Limiter `redis://rate_limit:6379/0`, SMTP-/Access-Request-Variablen und Pflicht-Secrets.

### Security/Access Request/Runtime

- Keine `/sample`-Route in Navigation/produktiven App-Pfaden gefunden.
- Keine produktive Font-Awesome-/Bootstrap-Icon-Nutzung gefunden; Treffer nur in der Spec als No-Go-Regel.
- Google Fonts sind in `base.html`, CSP und Spec bewusst extern dokumentiert.
- Material Symbols Rounded ist self-hosted via `material-symbols-fallback.css`.
- Access Request Mailtransport ist über Prod-Env konfigurierbar.
- Access Request Spam-Schutz ist aktiv: Honeypot, Form-Token, Max-Age, Minimum-Submit-Zeit, Tests.
- Prod Rate Limiter ist nicht `memory://`; non-development config erzwingt eine nicht-memory URI.
- `SECURITY.md` ist bewusst Pre-Publication-Scaffold ohne erfundenen öffentlichen Kontakt.
- `CODEOWNERS` ist comment-only Scaffold und nicht für Required Reviews aktiv.
- `git status --short -- content content\teaching public\teaching`: leer.

## 7. Operational Prerequisites

- Echte `POSTGRES_PASSWORD`, `FLASK_SECRET_KEY`, `JWT_SECRET_KEY` setzen.
- `RATE_LIMIT_STORAGE_URI` auf Redis/Shared Store setzen, nicht `memory://`.
- SMTP-/Provider-Werte setzen: `AUTH_ACCESS_REQUEST_EMAIL`, `AUTH_ACCESS_REQUEST_FROM_EMAIL`, `AUTH_ACCESS_REQUEST_SMTP_HOST`, optional Username/Password.
- Produktive Runtime-/Public-/Teaching-Volumes unter `/srv/webapps/promat/...` bereitstellen.
- Öffentlichen Security-Meldekanal klären, bevor öffentliches Vulnerability Intake aktiviert wird.
- Echte CODEOWNERS-Handles/Teams eintragen, bevor Required Reviews aktiviert werden.

## 8. Nicht umgesetzt

- keine globale MD3-Entfernung
- keine Design-System-Migration
- keine Google-Fonts-Lokalisierung
- keine Icon-Migration
- keine Content-Änderungen
- keine Teaching-Inhaltsänderungen
- keine Admin/Workbench-Mobile-Neugestaltung
- keine Entfernung bewusst aktiver Brückenschichten
- keine Entfernung von `md3-footer` oder `md3-content-wrapper`
- keine CSP-Änderung

## 9. Verbleibende spätere Aufgaben

- Aktive MD3-Brückenschichten langfristig migrieren: Buttons, Alerts, Snackbar, Layout/Typography/Tokens, Drawer/Topbar/Mobile.
- `md3-footer` und `md3-content-wrapper` nach Stabilitätsphase entfernen.
- Research-Comparison-Inline-SVGs optional normalisieren, falls später gewünscht.
- Google-Fonts-Lokalisierung nur mit Visual Regression, falls die Policy sich ändert.

## 10. Prod-Readiness-Entscheidung

`prod-ready with documented operational prerequisites`

Begründung: Tests, responsive Smoke, Docker-Compose-Rendering und Runtime-/Security-Basics sind stabil. Die verbleibenden Punkte sind operative Konfigurationen oder dokumentierte Wartbarkeits-/Designsystem-Reste, keine aktuellen Prod-Blocker.
