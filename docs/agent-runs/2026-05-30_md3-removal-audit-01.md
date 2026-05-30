# MD3-Removal Audit — Read-only Analyse

**Datum:** 2026-05-30  
**Branch:** main  
**Commit:** 1e260127359e99c941dfa30a03d7eff1d635b1e6  
**Typ:** Read-only Analyse, kein Code geändert  

## Ziel

Systematische Kartierung aller MD3-CSS-Abhängigkeiten in der App mit dem Ziel, einen konkreten Migrationsplan für die vollständige Entfernung von `app/static/css/md3/` zu erstellen.

## Ergebnisse

**Kernbefund:** Die Templates wurden bereits zu nahezu 100 % vom MD3-HTML-System migriert. Nur eine einzige MD3-CSS-Klasse verbleibt in Templates (`md3-status-live`, pointer-events: none Marker). Die 23 MD3-CSS-Dateien werden noch global geladen, stylen aber fast keine DOM-Elemente mehr.

**Aktiv genutztes MD3-CSS:**
- `alerts.css` und `snackbar.css` — JavaScript erzeugt noch `md3-alert` / `md3-snackbar` Klassen dynamisch
- `material-symbols-fallback.css` — Font und `.material-symbols-rounded` werden noch benötigt
- `typefaces.css` — Inter und Source Serif 4 Font-Faces

**Totes MD3-CSS (16 von 23 Dateien):**
Navigation (top-app-bar, navigation-drawer, navbar), Buttons, Cards, Dialog, Textfields, Login, Hero, Text-Pages, Page-Navigation, Typography-Classes, Layout-Helpers, Como-Citar

**JS-Status:**
- 4 JS-Dateien mit stalen MD3-Selektoren (drawer.js, turbo-integration.js, material-symbols-loader.js, logout.js) — finden keine DOM-Elemente mehr
- 4 JS-Dateien erzeugen noch aktiv MD3-Klassen (alert-utils.js, snackbar.js, login.js, password_reset.js)

**Token-Bridge:** `00_tokens.css` überschreibt alle `--md-sys-*`, `--space-*`, `--radius-*`, `--elev-*` Tokens mit promat-Werten.

## Ausgabe

Vollständiger Migrationsplan in: `docs/audits/promat_md3_removal_plan_2026-05-30.md`

6 Phasen: Fonts herauslösen → totes Nav-CSS entfernen → tote Utilities entfernen → Alerts/Snackbar migrieren → Rest aufräumen → md3/ löschen.

**Phase 1 sofort empfohlen** (risikoarm): typefaces.css und material-symbols.css aus md3/ in App-CSS-Wurzel verschieben.
