# Shell/Auth/Footer MD3 Cleanup

## 1. Scope

Geprüft wurden kleine aktive MD3-Altbezeichnungen im Shell-/Auth-/Footer-Bereich:

- Kommentar-/Doku-Reste zu bereits entfernten MD3-Dateien
- `_md3_skeletons/auth_login_skeleton.html`
- `md3-content-wrapper`
- `md3-footer`
- global geladene aktive MD3-Schichten als Kartierung, nicht als Entfernungskandidaten

Geändert wurden nur Kommentartext, Template-Extends, Shell-Klassennamen und rein additive CSS-Alias-Selektoren. Keine Layoutwerte, Breakpoints, Inhalte, Farben, Fonts, Icons oder funktionales Verhalten wurden geändert.

## 2. Kurzfazit

- Kommentarrest auf `status-banner.css` in `top-app-bar.css` wurde entfernt.
- `_md3_skeletons/auth_login_skeleton.html` wurde nach `_pm_skeletons/auth_login_skeleton.html` migriert; die vier Auth-Templates extenden jetzt den PM-Pfad.
- `md3-content-wrapper` wurde in `base.html` durch `pm-content-wrapper` ersetzt. CSS führt `pm-content-wrapper` aliasbasiert mit identischem Styling; `md3-content-wrapper` bleibt nur als Kompatibilitätsalias.
- `md3-footer` wurde in `base.html` durch `pm-footer-shell` ersetzt. `footer.css` führt `pm-footer-shell` aliasbasiert mit identischem Styling; `md3-footer` bleibt als Kompatibilitätsalias.
- Aktive globale MD3-Schichten bleiben bewusst erhalten.
- Chromium-Smoke-QA stabil: 27 Route/Viewport-Checks, 2 Drawer-Checks, 2 Access-Request-Validation-Checks, 0 Overflow, 0 Static 404, 0 Runtime-Console-Errors.
- Tests sind grün.

## 3. Referenzsuche

| Kandidat | Referenzen | Entscheidung |
|---|---|---|
| `status-banner.css` / entfernte MD3-Dateinamen | Nur noch ein Kommentar in `top-app-bar.css`; nach Cleanup keine Treffer mehr in aktiven Pfaden. | Kommentar entfernt. |
| `_md3_skeletons/auth_login_skeleton.html` | Vier Template-Extends: Login, Access Request, Password Forgot, Password Reset. Keine Python-/Test-/Spec-Referenzen. | Datei nach `_pm_skeletons/auth_login_skeleton.html` verschoben, Extends aktualisiert. |
| `md3-content-wrapper` | `base.html`, `layout.css`, `20_layout.css`, `mobile-responsive.css`. | `base.html` auf `pm-content-wrapper` migriert; CSS-Alias ergänzt, keine Werte geändert. |
| `md3-footer` | `base.html`, `md3/components/footer.css`. Footer-Inhalt selbst nutzt bereits `promat-footer`. | `base.html` auf `pm-footer-shell` migriert; CSS-Alias ergänzt, keine Werte geändert. |
| `md3-footer__*` | Nur in alter Footer-CSS-Komponente, nicht im produktiven Footer-Partial. | Nicht migriert; spätere globale MD3-Footer-CSS-Prüfung. |

Nachkontrolle:

- `rg "status-banner|status-banner.css|auth.css|forms.css|chips.css|index.css|menu.css|player.css|navigation-drawer-init.js|nav_proyecto.js" ...` liefert keine Treffer mehr.
- `_md3_skeletons` liefert keine Treffer mehr in aktiven Pfaden.
- `md3-content-wrapper` und `md3-footer` verbleiben nur als CSS-Aliasse bzw. in alten Footer-CSS-Subselektoren.

## 4. Änderungen

| Datei | Kurzgrund |
|---|---|
| `app/static/css/md3/components/top-app-bar.css` | Toten Kommentar auf entfernte `status-banner.css` gelöscht. |
| `app/templates/_pm_skeletons/auth_login_skeleton.html` | Auth-Skeleton unter PM-konformem Pfad. Inhalt unverändert. |
| `app/templates/auth/login.html` | Extends-Pfad auf `_pm_skeletons/...` aktualisiert. |
| `app/templates/auth/access_request.html` | Extends-Pfad auf `_pm_skeletons/...` aktualisiert. |
| `app/templates/auth/password_forgot.html` | Extends-Pfad auf `_pm_skeletons/...` aktualisiert. |
| `app/templates/auth/password_reset.html` | Extends-Pfad auf `_pm_skeletons/...` aktualisiert. |
| `app/templates/base.html` | Shell-Wrapper auf `pm-content-wrapper`, Footer-Shell auf `pm-footer-shell`. |
| `app/static/css/layout.css` | `pm-content-wrapper` als identischer Alias zu `md3-content-wrapper`. |
| `app/static/css/20_layout.css` | `pm-content-wrapper` als identischer Alias zu `md3-content-wrapper`. |
| `app/static/css/md3/components/mobile-responsive.css` | `pm-content-wrapper` in bestehende Overflow-Schutzregel aufgenommen. |
| `app/static/css/md3/components/footer.css` | `pm-footer-shell` als identischer Alias zu `md3-footer`. |
| `tmp/ui-qa/2026-05-26-shell-auth-footer-md3-cleanup/shell_auth_footer_smoke.py` | Fokussiertes Smoke-QA-Skript für diesen Run. |

Hinweis: Die vorherigen MD3-Legacy-Deletions aus `2026-05-26_md3-legacy-reduction.md` waren bereits uncommitted im Working Tree und sind nicht Teil dieser Namensmigration.

## 5. Beibehaltene aktive MD3-Schichten

| Datei | Aktiv geladen? | Sichtbare Abhängigkeit? | Grund fürs Behalten |
|---|---:|---:|---|
| `app/static/css/md3/components/navigation-drawer.css` | ja | ja | Drawer ist produktive Shell-Navigation; nicht in diesem Run anfassen. |
| `app/static/css/md3/components/top-app-bar.css` | ja | ja | Topbar ist produktiv sichtbar; nur toter Kommentar wurde entfernt. |
| `app/static/css/md3/components/mobile-responsive.css` | ja | ja | Mobile-Overflow-Schutz aktiv; nur additiver Wrapper-Alias ergänzt. |
| `app/static/css/md3/components/buttons.css` | ja | unklar/teilweise | Globale Button-Schicht, separate Prüfung nötig. |
| `app/static/css/md3/components/alerts.css` | ja | ja | Auth-/Flash-/Alert-Pfade können davon abhängen. |
| `app/static/css/md3/components/snackbar.css` | ja | ja | Snackbar/Core-Pfad weiterhin aktiv. |
| `app/static/css/md3/tokens.css` | ja | ja | Globale MD3/Token-Foundation; nicht sicher entfernbar. |
| `app/static/css/md3/layout.css` | ja | ja | Enthält aktive Altklassen/Form-/Layout-Regeln. |
| `app/static/css/md3/typography.css` | ja | ja | Globale Typography-Schicht; separate Token-/CSS-Arbeit nötig. |

## 6. Visuelle Smoke-QA

Artefakte:

- Screenshot-Ordner: `tmp/ui-qa/2026-05-26-shell-auth-footer-md3-cleanup/screenshots/`
- Ergebnis: `tmp/ui-qa/2026-05-26-shell-auth-footer-md3-cleanup/smoke_results.json`
- Overflow: `tmp/ui-qa/2026-05-26-shell-auth-footer-md3-cleanup/overflow_results.json`
- Summary: `tmp/ui-qa/2026-05-26-shell-auth-footer-md3-cleanup/summary.json`

Summary:

- Route/Viewport-Checks: 27
- Drawer-Checks: 2
- Access-Request-Validation-Checks: 2
- Overflow-Findings: 0
- Static 404: 0
- Runtime-Console-Errors: 0
- Erwartbare Validation-Resource-Meldungen: 2 mal `400 (BAD REQUEST)` beim absichtlich leeren Access-Request-Submit

| Route | Viewport | Status | Artefakt |
|---|---:|---|---|
| Projektseite | 360 | OK | `screenshots/360_project.jpg` |
| Projektseite/Footer | 1440 | OK | `screenshots/1440_project.jpg` |
| Login/Auth-Skeleton | 360 | OK | `screenshots/360_login.jpg` |
| Login/Auth-Skeleton | 390 | OK | `screenshots/390_login.jpg` |
| Access Request | 360 | OK | `screenshots/360_access-request.jpg` |
| Access Request Validation | 360 | OK | `screenshots/360_access-request-validation.jpg` |
| Access Request Validation | 390 | OK | `screenshots/390_access-request-validation.jpg` |
| Mobile Drawer offen | 360 | OK | `screenshots/360_drawer-open.jpg` |
| Mobile Drawer offen | 390 | OK | `screenshots/390_drawer-open.jpg` |
| Research Root | 390 | OK | `screenshots/390_research-root.jpg` |
| Player Wordlist | 390 | OK | `screenshots/390_player-wordlist.jpg` |
| Player Interview | 390 | OK | `screenshots/390_player-interview.jpg` |
| Teaching Root | 360 | OK | `screenshots/360_teaching-root.jpg` |
| Teaching Audio/Datawrapper | 360 | OK | `screenshots/360_teaching-audio-datawrapper.jpg` |
| Admin Users | 360 | OK | `screenshots/360_admin-users.jpg` |

Auth/Footer/Wrapper/Drawer/Topbar blieben in der Smoke-QA stabil. Die Messung bestätigt `pm-content-wrapper` und `pm-footer-shell` im DOM.

## 7. Tests und Checks

```text
.\.venv\Scripts\python.exe tmp\ui-qa\2026-05-26-shell-auth-footer-md3-cleanup\shell_auth_footer_smoke.py
```

Ergebnis: 27 Route/Viewport-Checks, 2 Drawer-Checks, 2 Validation-Checks, 0 Overflow, 0 Static 404, 0 Runtime-Console-Errors.

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

Zusätzlich wegen Skeleton-Migration:

```text
.\.venv\Scripts\python.exe -m pytest app/tests -q -k "auth or login or access_request"
```

Ergebnis: 145 passed, 329 deselected, 5 bekannte Flask-Limiter-Testmodus-Warnungen.

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
- keine CSS-Token-Migration
- keine Mobile-Neugestaltung
- keine Content-Änderungen
- keine Teaching-Inhaltsänderungen
- keine Google-Fonts-Arbeit
- keine Icon-Migration
- keine Farbangleichung
- keine Admin-/Workbench-Mobile-Neugestaltung
- keine Änderung an funktionalem Auth-/Drawer-/Topbar-/Footer-/Player-/Teaching-Verhalten

## 9. Verbleibende nächste Schritte

- CSS Token Consistency Cleanup ist jetzt sinnvoller, weil Shell-Wrapper und Footer-Shell PM-Namen haben, sollte aber getrennt und mit Screenshot-Smoke laufen.
- Globale MD3-Schichten können später einzeln geprüft werden: `buttons.css`, `alerts.css`, `snackbar.css`, `layout.css`, `typography.css`, `tokens.css`.
- `md3-footer__*` bleibt in der alten Footer-CSS-Komponente, wird aber vom produktiven `promat-footer`-Partial nicht genutzt; später sicher als Teil einer Footer-CSS-Audit-Einheit prüfen.
- `md3-content-wrapper` und `md3-footer` können nach einer längeren Stabilitätsphase aus den Alias-Selektoren entfernt werden, wenn keine externen/alten Templates mehr darauf angewiesen sind.
- Nach jeder weiteren Änderung an globalen Shell-CSS-Dateien bleibt ein kurzer Mobile-/Drawer-/Auth-/Footer-Smoke sinnvoll.
