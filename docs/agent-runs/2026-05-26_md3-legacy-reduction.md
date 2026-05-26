# MD3 Legacy Reduction

## 1. Scope

Geprüft und entfernt wurden nur die im Auftrag genannten, sicher belegbaren MD3-Legacy-Kandidaten:

- nicht global geladene MD3-Komponenten-CSS-Dateien
- tote JS-Altpfade `navigation-drawer-init.js` und `nav_proyecto.js`
- der einzige globale Link auf den leeren Drawer-Init-Altpfad

Ausdrücklich nicht umgesetzt wurden Design-System-Migration, globale MD3-Entfernung, Mobile-Neugestaltung, Content-Änderungen, Teaching-Inhaltsänderungen, Google-Fonts-Arbeit, Icon-Migration oder eine breite CSS-Bereinigung.

Als visuelle Baseline wurde der abgeschlossene Responsive-Run `tmp/ui-qa/2026-05-26-responsive-mobile-hardening/` herangezogen. Nach jeder Entfernungseinheit und final wurde eine neue Chromium-Smoke-QA erzeugt.

## 2. Kurzfazit

- Entfernt wurden 7 ungebundene MD3-Komponenten-CSS-Dateien und 2 tote JS-Altpfade.
- `base.html` lädt den leeren `navigation-drawer-init.js`-Altpfad nicht mehr.
- Global aktive oder unklare MD3-Schichten bleiben unangetastet.
- Visuelle Smoke-QA war nach Einheit 1, nach Einheit 2 und final stabil: jeweils 30 Route/Viewport-Checks, 2 Drawer-Checks, 0 Overflow-Findings, keine statischen 404s, keine Console-Errors.
- Tests sind grün.
- Kein Mobile-/Navigation-/Player-/Teaching-Prod-Blocker aus dieser Reduktion sichtbar.

## 3. Referenzsuche

| Kandidat | Referenzbefund | Entscheidung |
|---|---|---|
| `app/static/css/md3/components/auth.css` | Kein produktiver Link/Import auf die Datei. Ähnliche Klassen existieren weiterhin in aktiven Dateien wie `30_components.css`, `md3/layout.css`, `md3/components/login.css` und `md3/components/cards.css`. | Datei entfernt; aktive Klassen in anderen Dateien nicht angefasst. |
| `app/static/css/md3/components/forms.css` | Kein produktiver Link/Import auf die Datei. Form-/Textfield-Klassen werden weiterhin über aktive MD3-Dateien bedient. | Datei entfernt; aktive Formsysteme nicht angefasst. |
| `app/static/css/md3/components/chips.css` | Treffer nur in der Datei selbst. | Datei entfernt. |
| `app/static/css/md3/components/index.css` | Treffer nur in der Datei selbst bzw. in anderen aktiven MD3-Dateien für generische alte Page-Klassen; kein Link/Import auf `index.css`. | Datei entfernt. |
| `app/static/css/md3/components/menu.css` | Treffer nur in der Datei selbst. | Datei entfernt. |
| `app/static/css/md3/components/player.css` | Treffer nur in der Datei selbst; produktiver Research Player nutzt andere PM/PROMAT-Strukturen. | Datei entfernt. |
| `app/static/css/md3/components/status-banner.css` | Kein produktiver Link/Import. Ein Kommentar in `top-app-bar.css` verweist noch auf den alten Pfad; keine Runtime-Referenz. | Datei entfernt; `top-app-bar.css` gemäß No-Go nicht geändert. |
| `app/static/js/navigation-drawer-init.js` | Einziger produktiver Treffer war der globale Script-Link in `base.html`; Datei enthielt nur Kommentar. | Script-Link entfernt und Datei gelöscht. |
| `app/static/js/nav_proyecto.js` | Treffer nur in der Datei selbst. | Datei entfernt. |

Referenzsuchlauf nach Entfernung:

- Für entfernte CSS/JS-Kandidaten bleibt nur ein Kommentar-Treffer in `app/static/css/md3/components/top-app-bar.css` zu `status-banner.css`.
- Kein produktiver Template-/JS-/Spec-/Runbook-Link lädt entfernte Assets.

## 4. Entfernte Dateien / Links / Imports

Entfernte Dateien:

- `app/static/css/md3/components/auth.css`
- `app/static/css/md3/components/forms.css`
- `app/static/css/md3/components/chips.css`
- `app/static/css/md3/components/index.css`
- `app/static/css/md3/components/menu.css`
- `app/static/css/md3/components/player.css`
- `app/static/css/md3/components/status-banner.css`
- `app/static/js/navigation-drawer-init.js`
- `app/static/js/nav_proyecto.js`

Geänderter Link:

- `app/templates/base.html`: globaler `<script>` für `js/navigation-drawer-init.js` entfernt.

## 5. Bewusst beibehaltene MD3-Reste

- `app/static/css/md3/components/navigation-drawer.css`: global geladen und sichtbare Drawer-Abhängigkeit.
- `app/static/css/md3/components/top-app-bar.css`: global geladen und sichtbare Topbar-Abhängigkeit.
- `app/static/css/md3/components/mobile-responsive.css`: global geladen; mobile QA nutzt weiterhin diese Schicht.
- `app/static/css/md3/components/buttons.css`, `alerts.css`, `snackbar.css`: global geladen bzw. aktive Form/Auth/Message-Abhängigkeiten.
- `app/static/css/md3/tokens.css`, `layout.css`, `typography.css`: globale Foundation-Schicht.
- `app/static/js/modules/navigation/**`: produktiver Shell-/Drawer-/Topbar-Pfad.
- `app/static/js/md3/alert-utils.js`: aktiver Import aus Auth-Passwort-JS.
- `app/static/js/modules/core/snackbar.js`: globaler Core-Pfad, nicht in diesem Run bewertet.
- `_md3_skeletons/auth_login_skeleton.html`: aktive Auth-Templates extenden dieses Skeleton.
- `md3-content-wrapper`, `md3-footer`: aktiv in `base.html` und globalen Layout-/Footer-CSS-Dateien.

Späterer sicherer Pfad: erst aktive Shell-/Auth-/Snackbar-/Footer-Nutzung separat kartieren, dann einzelne globale MD3-Schichten nur mit Vorher/Nachher-Screenshots und fokussierten Regressionstests reduzieren.

## 6. Visuelle Smoke-QA

Screenshot-Ordner:

- `tmp/ui-qa/2026-05-26-md3-legacy-reduction/screenshots/`

Ergebnisdateien:

- `tmp/ui-qa/2026-05-26-md3-legacy-reduction/unit1-css_results.json`
- `tmp/ui-qa/2026-05-26-md3-legacy-reduction/unit1-css_overflow.json`
- `tmp/ui-qa/2026-05-26-md3-legacy-reduction/unit2-js_results.json`
- `tmp/ui-qa/2026-05-26-md3-legacy-reduction/unit2-js_overflow.json`
- `tmp/ui-qa/2026-05-26-md3-legacy-reduction/final_results.json`
- `tmp/ui-qa/2026-05-26-md3-legacy-reduction/final_overflow.json`

| Einheit | Route | Viewport | Status | Screenshot/Artefakt |
|---|---|---:|---|---|
| Unit 1 CSS | Login | 360 | OK | `screenshots/unit1-css_360_login.jpg` |
| Unit 1 CSS | Drawer offen | 360 | OK | `screenshots/unit1-css_360_drawer-open.jpg` |
| Unit 1 CSS | Player Wordlist | 390 | OK | `screenshots/unit1-css_390_player-wordlist.jpg` |
| Unit 1 CSS | Player Interview | 390 | OK | `screenshots/unit1-css_390_player-interview.jpg` |
| Unit 1 CSS | Teaching Audio/Datawrapper | 360 | OK | `screenshots/unit1-css_360_teaching-audio-datawrapper.jpg` |
| Unit 1 CSS | Admin Users | 360 | OK | `screenshots/unit1-css_360_admin-users.jpg` |
| Unit 1 CSS | Projektseite | 1440 | OK | `screenshots/unit1-css_1440_project.jpg` |
| Unit 2 JS | Login | 360 | OK | `screenshots/unit2-js_360_login.jpg` |
| Unit 2 JS | Drawer offen | 360 | OK | `screenshots/unit2-js_360_drawer-open.jpg` |
| Unit 2 JS | Player Wordlist | 390 | OK | `screenshots/unit2-js_390_player-wordlist.jpg` |
| Unit 2 JS | Teaching Audio/Datawrapper | 360 | OK | `screenshots/unit2-js_360_teaching-audio-datawrapper.jpg` |
| Unit 2 JS | Admin Users | 360 | OK | `screenshots/unit2-js_360_admin-users.jpg` |
| Final | Login | 360 | OK | `screenshots/final_360_login.jpg` |
| Final | Drawer offen | 360 | OK | `screenshots/final_360_drawer-open.jpg` |
| Final | Player Wordlist | 390 | OK | `screenshots/final_390_player-wordlist.jpg` |
| Final | Player Interview | 390 | OK | `screenshots/final_390_player-interview.jpg` |
| Final | Teaching Audio/Datawrapper | 360 | OK | `screenshots/final_360_teaching-audio-datawrapper.jpg` |
| Final | Admin Users | 360 | OK | `screenshots/final_360_admin-users.jpg` |
| Final | Projektseite | 1440 | OK | `screenshots/final_1440_project.jpg` |

Smoke-QA-Zusammenfassung je Phase:

| Phase | Route/Viewport-Checks | Drawer-Checks | Overflow | Static 404 | Console Errors |
|---|---:|---:|---:|---:|---:|
| `unit1-css` | 30 | 2 | 0 | 0 | 0 |
| `unit2-js` | 30 | 2 | 0 | 0 | 0 |
| `final` | 30 | 2 | 0 | 0 | 0 |

Geprüfte Flächen: Projektseite, Login, Access Request, Research Root, Speakers Card View, Player Wordlist, Player Interview, Teaching Root, Teaching Topic mit Audio/Datawrapper, Mobile Drawer offen, Admin Users.

## 7. Tests und Checks

Nach Einheit 1:

```text
.\.venv\Scripts\python.exe -m compileall app -q
```

Ergebnis: bestanden.

```text
.\.venv\Scripts\python.exe -m pytest app/tests -q -k "navigation or drawer or responsive or csp or security_headers or access_request or player or teaching"
```

Ergebnis: 171 passed, 303 deselected, 28 bekannte Flask-Limiter-Testmodus-Warnungen.

```text
.\.venv\Scripts\python.exe tmp\ui-qa\2026-05-26-md3-legacy-reduction\md3_smoke_qa.py unit1-css
```

Ergebnis: 30 Route/Viewport-Checks, 2 Drawer-Checks, 0 Overflow, 0 Static 404, 0 Console Errors.

Nach Einheit 2:

```text
.\.venv\Scripts\python.exe -m compileall app -q
```

Ergebnis: bestanden.

```text
.\.venv\Scripts\python.exe -m pytest app/tests -q -k "navigation or drawer or responsive or csp or security_headers or access_request or player or teaching"
```

Ergebnis: 171 passed, 303 deselected, 28 bekannte Flask-Limiter-Testmodus-Warnungen.

```text
.\.venv\Scripts\python.exe tmp\ui-qa\2026-05-26-md3-legacy-reduction\md3_smoke_qa.py unit2-js
```

Ergebnis: 30 Route/Viewport-Checks, 2 Drawer-Checks, 0 Overflow, 0 Static 404, 0 Console Errors.

Final:

```text
.\.venv\Scripts\python.exe tmp\ui-qa\2026-05-26-md3-legacy-reduction\md3_smoke_qa.py final
```

Ergebnis: 30 Route/Viewport-Checks, 2 Drawer-Checks, 0 Overflow, 0 Static 404, 0 Console Errors.

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
.\.venv\Scripts\python.exe -m pytest app/tests -q -k "navigation or mobile or drawer or responsive or csp or security_headers or access_request or player or teaching"
```

Ergebnis: 171 passed, 303 deselected, 28 bekannte Flask-Limiter-Testmodus-Warnungen.

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

## 8. Nicht umgesetzt

- keine Design-System-Migration
- keine globale MD3-Entfernung
- keine Änderung an `navigation-drawer.css`, `top-app-bar.css`, `mobile-responsive.css`, Alert/Snackbar oder global geladenen MD3-Basisdateien
- keine Mobile-Neugestaltung
- keine Content-Änderungen
- keine Teaching-Inhaltsänderungen
- keine Google-Fonts-Arbeit
- keine Icon-Migration
- keine Admin-/Workbench-Mobile-Neugestaltung
- keine pauschale Entfernung historischer Reports

## 9. Verbleibende nächste Schritte

- `top-app-bar.css` enthält noch einen Kommentar auf den entfernten `status-banner.css`-Pfad. Das ist keine Runtime-Referenz, kann aber in einem späteren Kommentar-/Doku-Cleanup bereinigt werden.
- Aktive globale MD3-Schichten separat prüfen: `navigation-drawer.css`, `top-app-bar.css`, `mobile-responsive.css`, `buttons.css`, `alerts.css`, `snackbar.css`, Foundation-Dateien.
- `_md3_skeletons/auth_login_skeleton.html`, `md3-content-wrapper` und `md3-footer` bleiben aktive Altbezeichnungen und sollten nur im Rahmen eines eigenen Shell/Auth/Footer-Migrationsprompts angefasst werden.
- CSS Token Consistency Cleanup ist nach dieser Reduktion sinnvoller, aber weiterhin getrennt von einer MD3-Entfernung zu planen.
- Ein weiterer kurzer Mobile-Smoke ist nach jeder späteren globalen MD3-Schichtänderung empfohlen.
