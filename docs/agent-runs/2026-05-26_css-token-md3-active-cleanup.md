# CSS Token + Active MD3 Cleanup

## 1. Scope

Geprüft wurden die produktiven CSS- und aktiven MD3-Schichten:

- `app/static/css/00_tokens.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/static/css/layout.css`
- `app/static/css/md3/**/*.css`

Geändert wurde nur, was ohne Layoutänderung hart belegbar war:

- alte, unreferenzierte MD3-Footer-Unterklassen aus `footer.css` entfernt
- `footer.css` auf eine kleine Footer-Shell-Kompatibilitätsschicht reduziert
- wiederverwendbarer Responsive-Smoke-Runner unter `scripts/qa/responsive_smoke.py` ergänzt

Ausdrücklich nicht umgesetzt wurden Redesign, Design-System-Migration, globale MD3-Entfernung, Font-/Google-Fonts-Arbeit, Icon-Migration, Content-Änderungen, Teaching-Inhaltsänderungen, Mobile-Neugestaltung oder riskante Foundation-Token-Entfernung.

## 2. Kurzfazit

- Token-Konsistenz verbessert: keine breite Token-Migration; stattdessen alte harte Footer-Komponentenwerte entfernt und die verbleibende Footer-Shell bleibt tokenbasiert.
- MD3-Schicht reduziert: `app/static/css/md3/components/footer.css` wurde von einer alten vollständigen MD3-Footer-Komponente auf eine kleine Shell-Alias-Schicht reduziert.
- Aktive MD3-Schichten bewusst behalten: Buttons, Alerts, Snackbar, Navigation Drawer, Top App Bar, Mobile Responsive, Foundation Tokens/Layout/Typography.
- Smoke-QA stabil: 30 Route/Viewport-Checks, 2 Drawer-Checks, 2 Validation-Checks, 0 Overflow, 0 Static 404, 0 Runtime-Console-Errors.
- Prod-Risiko verbleibend: niedrig für diesen Cleanup; mittelfristig bleiben aktive MD3-Foundation- und JS-gekoppelte Alert/Snackbar-Schichten.

## 3. Phasenbericht

### Phase 1: Inventar und sichere Token-Kandidaten

Ziel: harte CSS-Werte, `!important`, Tokens und aktive MD3-Dateien klassifizieren.

Befunde:

- Viele harte Werte liegen in sensiblen typografischen, Research-, Teaching-, Player- oder responsive-spezifischen Regeln.
- `00_tokens.css` enthält bereits PM/PROMAT-Token für Shell, Footer, Topbar, Drawer, Radius, Shadow, Touch Targets und Research/Teaching.
- Direkte risikoarme Token-Ersetzungen waren in dieser Runde nicht überzeugend, weil viele harte Werte Teil bestehender visueller Kalibrierung sind.
- Sicherer Befund: alte `md3-footer__*`-Regeln enthalten viele harte Werte, werden aber produktiv nicht referenziert.

Änderungen: keine direkte Token-Ersetzung in Phase 1.

Tests/Smoke: Phase 1 war read-only; Validierung erfolgte nach der anschließenden sicheren Reduktion.

Entscheidung: riskante harte Werte dokumentieren, nicht pauschal tokenisieren.

### Phase 2: `!important` und alte Utilities

Ziel: offensichtlich überflüssige `!important`-Regeln und alte Utilities reduzieren.

Befunde:

- Mobile-Responsive- und Navigation-`!important`-Regeln schützen sichtbare Shell-/Overflow-/Motion-Zustände.
- `md3/layout.css` enthält Bootstrap-artige Utilities mit `!important`; Referenzsuche in produktiven App-Pfaden fand keine klare Nutzung, aber die Utility-Schicht ist global und generisch.
- Alerts/Buttons/Snackbar enthalten `!important` in aktiven oder JS-gekoppelten Pfaden.

Änderungen: keine `!important`-Entfernung.

Tests/Smoke: keine CSS-Änderung in Phase 2.

Entscheidung: behalten und später separat mit größerer Utility-Audit-Sorgfalt prüfen.

### Phase 3: Aktive MD3-Schichten

Ziel: aktive globale MD3-Dateien dateiweise prüfen.

Befunde:

- `buttons.css`: global geladen. Produktive Templates sollen keine `md3-button` mehr rendern; Tests sichern das teilweise ab. JS verwendet aber noch `md3-button--loading`, und `material-symbols-loader.js` kennt `.md3-icon-button`. Nicht entfernt.
- `alerts.css` / `snackbar.css`: aktiv über `app/static/js/md3/alert-utils.js`, `app/static/js/modules/core/snackbar.js` und Auth-Login-JS. Nicht entfernt.
- `layout.css`: enthält aktive/unklare alte Layout-, Form-, Table- und Utility-Schichten. Nicht entfernt.
- `typography.css`: Foundation-Typografie für alte MD3-Klassen; keine Font-/Typografieänderung in diesem Run.
- `tokens.css`: Foundation für aktive MD3- und PM-Brücken. Keine Entfernung.
- `navigation-drawer.css`, `top-app-bar.css`, `mobile-responsive.css`: Shell-/Mobile-riskant und aktiv geladen. Nicht entfernt.

Änderungen: keine in Phase 3.

Tests/Smoke: keine CSS-Änderung in Phase 3.

Entscheidung: nur kartieren; spätere file-by-file Prompts.

### Phase 4: Footer- und Alias-Stabilisierung

Ziel: `md3-footer__*`, `md3-footer`, `md3-content-wrapper`, `pm-footer-shell`, `pm-content-wrapper` prüfen.

Befunde:

- `md3-footer__*` und `md3-legal-micro` waren nur in `app/static/css/md3/components/footer.css` vorhanden.
- Produktives Footer-Partial nutzt `promat-footer__*`; Shell nutzt `pm-footer-shell`.
- `md3-footer` und `md3-content-wrapper` bleiben als Kompatibilitätsaliase sinnvoll.

Änderungen:

- `app/static/css/md3/components/footer.css` auf Shell-Alias reduziert.
- Entfernt wurden unreferenzierte `md3-footer__*`-Regeln und `md3-legal-micro`.
- `md3-footer`-Alias bleibt.
- `md3-content-wrapper`-Alias bleibt.

Tests:

```text
.\.venv\Scripts\python.exe -m compileall app -q
.\.venv\Scripts\python.exe -m pytest app/tests -q -k "navigation or drawer or responsive or csp or security_headers or access_request or player or teaching or footer or auth"
```

Ergebnis: Compile bestanden; 279 passed, 195 deselected, 33 bekannte Flask-Limiter-Testmodus-Warnungen.

Smoke:

```text
.\.venv\Scripts\python.exe scripts\qa\responsive_smoke.py --run-id 2026-05-26-css-token-md3-active-cleanup
```

Ergebnis: 30 Route/Viewport-Checks, 2 Drawer-Checks, 2 Validation-Checks, 0 Overflow, 0 Static 404, 0 Runtime-Console-Errors.

Entscheidung: Reduktion stabil, Aliasse behalten.

### Phase 5: Wiederverwendbarer Smoke-QA-Runner

Ziel: ähnliche `tmp/ui-qa/...`-Skripte in einem wiederverwendbaren QA-Hilfsskript konsolidieren.

Änderung:

- `scripts/qa/responsive_smoke.py` ergänzt.

Funktionen:

- Viewports 360, 390, 768, 1440
- Kernrouten für Projekt, Auth, Research, Player, Teaching, Admin
- Drawer-Open-Check
- Access-Request-Validation-Check
- Overflow-Check
- Static-404-Check
- Runtime-Console-Error-Check
- Screenshot-Ausgabe in `tmp/ui-qa/<run-id>/`

Entscheidung: umgesetzt und in diesem Run verwendet.

## 4. Token-/CSS-Änderungen

| Datei | Änderung | Token/Grund | Risiko | Validierung |
|---|---|---|---|---|
| `app/static/css/md3/components/footer.css` | Alte MD3-Footer-Komponente auf Shell-Alias reduziert. | Produktives Partial nutzt `promat-footer`; alte harte `md3-footer__*`-Werte waren unreferenziert. | niedrig | Tests + responsive smoke |
| `app/static/css/md3/components/footer.css` | `border-top: 0px solid ...` zu `border-top: 0`. | Gleiche sichtbare Wirkung, kleinere Kompatibilitätsschicht. | niedrig | Footer-Smoke |
| `scripts/qa/responsive_smoke.py` | Wiederverwendbares QA-Skript ergänzt. | Keine Produkt-CSS-Änderung; reduziert wiederholte tmp-Skripte. | niedrig | Skriptlauf erfolgreich |

## 5. MD3-Schichten

| Datei | Befund | Änderung | Behalten/Entfernt | Grund |
|---|---|---|---|---|
| `md3/components/footer.css` | Shell-Alias aktiv, alte Footer-Unterklassen tot. | `md3-footer__*` und `md3-legal-micro` entfernt. | reduziert | Produktiver Footer nutzt `promat-footer`. |
| `md3/components/buttons.css` | Keine produktiven Template-Refs auf `md3-button`, aber JS kennt `md3-button--loading`/`.md3-icon-button`. | keine | behalten | Nicht hart genug für globale Entfernung. |
| `md3/components/alerts.css` | Aktiv via `alert-utils.js`. | keine | behalten | Notification/Auth-Pfad. |
| `md3/components/snackbar.css` | Aktiv via `modules/core/snackbar.js` und Auth-Login-JS. | keine | behalten | Runtime-Nachrichten. |
| `md3/layout.css` | Alte Utilities/Form/Table/Layout gemischt; teils unklar. | keine | behalten | Zu global für sicheren Schnitt. |
| `md3/typography.css` | Foundation für alte Typografieklassen. | keine | behalten | Keine Typografieänderung im Scope. |
| `md3/tokens.css` | Foundation für aktive MD3-Schichten. | keine | behalten | Breite Token-Entfernung riskant. |
| `md3/components/navigation-drawer.css` | Sichtbare Drawer-Abhängigkeit. | keine | behalten | Shell-riskant. |
| `md3/components/top-app-bar.css` | Sichtbare Topbar-Abhängigkeit. | keine | behalten | Shell-riskant. |
| `md3/components/mobile-responsive.css` | Mobile-Overflow-/Responsive-Schutz. | keine | behalten | Mobile-riskant. |

## 6. Footer/Aliasse

- `md3-footer__*`: entfernt; keine aktiven Referenzen mehr.
- `md3-legal-micro`: entfernt; keine aktiven Referenzen.
- `md3-footer`: bleibt als temporärer Shell-Alias in `footer.css`.
- `md3-content-wrapper`: bleibt als temporärer Wrapper-Alias in `layout.css`, `20_layout.css`, `mobile-responsive.css`.
- `pm-footer-shell`: produktive Shell-Klasse in `base.html`.
- `pm-content-wrapper`: produktive Wrapper-Klasse in `base.html`.

Spätere Entfernungsmöglichkeit: `md3-footer` und `md3-content-wrapper` können nach einer Stabilitätsphase und erneuter Referenzsuche entfernt werden, wenn keine alten Templates oder externen Overrides mehr darauf angewiesen sind.

## 7. QA-Smoke

Command:

```text
.\.venv\Scripts\python.exe scripts\qa\responsive_smoke.py --run-id 2026-05-26-css-token-md3-active-cleanup
```

Artefakte:

- Screenshot-Ordner: `tmp/ui-qa/2026-05-26-css-token-md3-active-cleanup/screenshots/`
- `tmp/ui-qa/2026-05-26-css-token-md3-active-cleanup/smoke_results.json`
- `tmp/ui-qa/2026-05-26-css-token-md3-active-cleanup/overflow_results.json`
- `tmp/ui-qa/2026-05-26-css-token-md3-active-cleanup/summary.json`

Summary:

- Route/Viewport-Checks: 30
- Drawer-Checks: 2
- Validation-Checks: 2
- Overflow-Findings: 0
- Static 404: 0
- Runtime Console Errors: 0
- Erwartbare Validation-Resource-Meldungen: 2 mal `400 (BAD REQUEST)` beim absichtlich leeren Access-Request-Submit

| Route/Flow | 360 | 390 | 768 | 1440 | Status |
|---|---|---|---|---|---|
| Projektseite/Footer | OK | OK | OK | OK | stabil |
| Login/Auth | OK | OK | OK | OK | stabil |
| Access Request | OK | OK | nicht separat | nicht separat | stabil |
| Access Request Validation | OK | OK | nicht separat | nicht separat | erwartete Fehler sichtbar |
| Mobile Drawer offen | OK | OK | nicht nötig | nicht nötig | stabil |
| Research Root | OK | OK | OK | OK | stabil |
| Speakers Card | OK | OK | OK | nicht separat | stabil |
| Player Wordlist | nicht separat | OK | OK | nicht separat | stabil |
| Player Interview | nicht separat | OK | OK | nicht separat | stabil |
| Teaching Root | OK | OK | OK | OK | stabil |
| Teaching Audio/Datawrapper | OK | OK | OK | nicht separat | stabil |
| Admin Users | OK | nicht separat | OK | nicht separat | stabil |

## 8. Tests und Checks

Nach CSS-/Footer-Reduktion:

```text
.\.venv\Scripts\python.exe -m compileall app -q
```

Ergebnis: bestanden.

```text
.\.venv\Scripts\python.exe -m pytest app/tests -q -k "navigation or drawer or responsive or csp or security_headers or access_request or player or teaching or footer or auth"
```

Ergebnis: 279 passed, 195 deselected, 33 bekannte Flask-Limiter-Testmodus-Warnungen.

Final:

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
.\.venv\Scripts\python.exe -m pytest app/tests -q -k "navigation or mobile or drawer or responsive or csp or security_headers or access_request or player or teaching or footer or auth"
```

Ergebnis: 279 passed, 195 deselected, 33 bekannte Flask-Limiter-Testmodus-Warnungen.

```text
node --test app/tests/js/*.test.mjs
```

Ergebnis: 7 passed.

Optional geprüft:

```text
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe .
```

Ergebnis: `ruff` und `mypy` sind in der lokalen `.venv` nicht verfügbar.

Repo-Grenzen:

```text
git status --short -- content content\teaching public\teaching
```

Ergebnis: leer.

## 9. Nicht umgesetzt

- keine Design-System-Migration
- keine globale MD3-Entfernung
- keine Layout-Neugestaltung
- keine Mobile-Neugestaltung
- keine Content-Änderungen
- keine Teaching-Inhaltsänderungen
- keine Google-Fonts-Arbeit
- keine Icon-Migration
- keine Entfernung der Wrapper/Footer-Aliasse
- keine Entfernung riskanter Foundation-Tokens
- keine Entfernung riskanter Navigation-/Topbar-/Mobile-Responsive-Regeln
- keine Entfernung aktiver Alert-/Snackbar-Pfade
- keine Änderung an `style-src 'unsafe-inline'`

## 10. Verbleibende nächste Schritte

- Aktive MD3-Reste: `buttons.css`, `alerts.css`, `snackbar.css`, `layout.css`, `typography.css`, `tokens.css`, `navigation-drawer.css`, `top-app-bar.css`, `mobile-responsive.css`.
- Nach Stabilitätsphase können `md3-footer` und `md3-content-wrapper`-Aliasse mit erneuter Referenzsuche und Smoke-QA entfernt werden.
- `md3-button--loading` in `app/static/js/modules/auth/login.js` und Alert/Snackbar-MD3-Namen sind gute Kandidaten für einen eigenen JS/CSS-Namensmigrationsprompt.
- Ein Final Prod Smoke ist als nächster Schritt sinnvoll, weil Mobile-/Shell-/Auth-/Research-/Teaching-Smoke nach diesem Cleanup stabil war.
