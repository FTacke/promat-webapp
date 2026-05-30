# MD3-Entfernungsplan — ProMat Webapp

**Erstellt:** 2026-05-30  
**Branch:** `main`  
**Commit:** `1e260127359e99c941dfa30a03d7eff1d635b1e6`  
**Git-Status:** Clean — keine uncommitted Änderungen  
**Typ:** Read-only Analyse und Migrationsplan  

---

## 1. Executive Summary

Die App hat zwei parallele CSS-Welten: 23 MD3-CSS-Dateien und das genuine App-CSS-System (`promat-*` / `pm-*`). Die Templates wurden bereits **zu nahezu 100 % vom MD3-System migriert** — nur eine einzige MD3-CSS-Klasse verbleibt in den Templates (`md3-status-live`, ein no-op pointer-events-Marker ohne visuelle Wirkung).

**Zentrale Erkenntnis:** Die MD3-CSS-Dateien werden noch global über `base.html` eingebunden und erzeugen toten CSS-Overhead, aber sie werden kaum noch auf tatsächliche DOM-Elemente angewandt. Lediglich zwei JavaScript-Module erzeugen noch aktiv MD3-Klassen: `alert-utils.js` und `snackbar.js`. Vier weitere JS-Dateien haben stale Selektoren auf MD3-Klassen, die inzwischen keinen Match mehr finden.

**Empfehlung: Phasenweise Migration jetzt starten.** Eine direkte sofortige Entfernung von `app/static/css/md3/` ist **nicht möglich** — aber Phase 1 (Fontdateien herauslösen) und Phase 2 (Navigation/Utility-Leichen entfernen) sind risikoarm und sofort durchführbar.

---

## 2. Aktueller MD3-Umfang

### 23 MD3-CSS-Dateien

| Datei | Kategorie | Zweck | Schlüsselklassen | Status |
|---|---|---|---|---|
| `md3/tokens.css` | Tokens | Farb-, Typografie-, Spacing-, Motion-Tokens | `--md-sys-color-*`, `--space-*`, `--radius-*`, `--elev-*`, `--md-motion-*` | Aktiv, aber durch `00_tokens.css` überschrieben |
| `md3/typography.css` | Typography | Typografieklassen | `.md3-display-*`, `.md3-headline-*`, `.md3-title-*`, `.md3-body-*`, `.md3-label-*` | **Tote CSS** — keine Template-Nutzung |
| `md3/layout.css` | Layout | Seitenlayout, Tabellen, Utilities | `.md3-page`, `.md3-container`, `.md3-stack--*`, `.md3-table`, `.md3-empty-state`, `.m-*`, `.mt-*` | **Tote CSS** — keine Template-Nutzung |
| `components/typefaces.css` | Fonts | **Nicht MD3-spezifisch** — Inter und Source Serif 4 | `@font-face` für Inter, Source Serif 4 | **Muss raus aus md3/** |
| `components/material-symbols-fallback.css` | Icons | Material Symbols Rounded Font | `.material-symbols-rounded` | **Muss raus aus md3/**, Font wird weiterhin benötigt |
| `components/top-app-bar.css` | Navigation | Top App Bar, User Menu, Account Chip, Badges | `.md3-top-app-bar`, `.md3-user-menu`, `.md3-badge`, `.md3-theme-toggle` | **Tote CSS** — Template nutzt `promat-topbar` |
| `components/navigation-drawer.css` | Navigation | Modal + Standard Drawer, Accordion | `.md3-navigation-drawer`, `.drawer` | **Tote CSS** — Template nutzt `promat-panel` |
| `components/navbar.css` | Navigation | Alternatives Navbar-Bauteil | `.md3-nav`, `.md3-mobile-menu` | **Tote CSS** — nicht in aktuellen Templates |
| `components/buttons.css` | Buttons | Button-Varianten | `.md3-button--filled`, `.md3-button--tonal`, `.md3-button--outlined`, `.md3-button--text`, `.md3-button--danger` | **Tote CSS** — keine Template-Nutzung |
| `components/cards.css` | Cards | Card-Varianten | `.md3-card`, `.card-elevated`, `.card-outlined`, `.card-tonal` | Tote CSS — aber `.md3-card` ist Selektor in `40_cards.css` |
| `components/dialog.css` | Overlays | Dialog-Bauteil | `.md3-dialog`, `.md3-dialog__*`, `.md3-snippet` | **Tote CSS** — keine Template-Nutzung |
| `components/textfields.css` | Forms | Outlined Textfield | `.md3-outlined-textfield`, `.md3-outlined-textfield__*` | **Tote CSS** — keine Template-Nutzung |
| `components/alerts.css` | Feedback | Alert-Banner | `.md3-alert`, `.md3-alert--error`, `.md3-field-error` | **AKTIV** — JS erzeugt diese Klassen |
| `components/snackbar.css` | Feedback | Toast-Notifications | `.md3-snackbar`, `.md3-snackbar--*` | **AKTIV** — JS erzeugt diese Klassen |
| `components/login.css` | Auth | Login-Seite / Login-Sheet | `.md3-login-page`, `.md3-login-card`, `.md3-login-sheet`, `.md3-sheet` | **Tote CSS** — Templates nutzen promat-Klassen |
| `components/hero.css` | Content | Page Heroes, Back Links | `.md3-hero`, `.md3-hero--*`, `.md3-back-link` | **Tote CSS** — keine Template-Nutzung |
| `components/text-pages.css` | Content | Text-/Projektseitenlayout | `.md3-text-page`, `.md3-text-content`, `.md3-code-block`, `.citation-block` | **Tote CSS** — keine Template-Nutzung |
| `components/page-navigation.css` | Navigation | Prev/Next Seiten-Navigation | `.md3-page-navigation` | **Tote CSS** — keine Template-Nutzung |
| `components/footer.css` | Shell | Footer-Kompatibilitätsschicht | `.md3-footer`, `.pm-footer-shell` | Teils aktiv über `.pm-footer-shell`-Alias |
| `components/mobile-responsive.css` | Responsive | Mobile Overrides, Z-Index-Hierarchie, Atlas-Map | HTML/Body-Regeln, `#panel-resultados`, `--z-index-*` | **Noch aktiv** — enthält globale mobile Overrides |
| `components/motion.css` | Motion | Transitions, State Layers, Keyframes | `.md3-interactive`, `@keyframes`, `:focus-visible` | **Teils aktiv** — globaler `:focus-visible` override |
| `components/layout-helpers.css` | Utilities | Spacing-Utilities | `.md3-row`, `.md3-stack`, `.md3-mt-*`, `.md3-mb-*` | **Tote CSS** — keine Template-Nutzung |
| `components/como-citar.css` | Content | Zitier-Seiten-Grid | `.doi-resource-grid`, `.doi-resource-card` | Unklar — kein Template-Match gefunden |

**Lade-Reihenfolge in `base.html`:**
1. `layout.css` (preload + load) — genuines App-CSS
2. `md3/components/typefaces.css`
3. `md3/tokens.css`
4. `00_tokens.css` → **überschreibt alle MD3-Tokens**
5. `md3/typography.css`
6. `md3/layout.css`
7. Alle `md3/components/*.css` (Navigation, Buttons, Cards, Dialog, Forms, Alerts, Snackbar, Login, Helpers, Mobile, Motion, Layout-Helpers, Como-Citar)
8. `10_typography.css`, `20_layout.css`, `30_components.css`, `40_cards.css`

---

## 3. Aktive Template-Abhängigkeiten

### Übersicht: MD3-Klassen in Templates

| Bereich | Template(s) | MD3-Klassen | Kritikalität | Migrationsrisiko |
|---|---|---|---|---|
| App Shell / Base | `base.html` | Keine md3-Klassen im HTML — nur CSS-`<link>`-Tags | — | Niedrig: nur Link-Entfernung nötig |
| Navigation Drawer | `_navigation_drawer.html` | **Keine** — nutzt `promat-panel-dialog`, `promat-panel--modal/standard` | — | Keins — bereits migriert |
| Top App Bar | `_top_app_bar.html` | **Keine** — nutzt `promat-topbar__*`, `promat-user-menu__*`, `pm-icon-mask` | — | Keins — bereits migriert |
| Admonitions | `_admonition.html` | `md3-status-live` (pointer-events: none Marker, kein visueller Effekt) | Low | Trivial |
| Landing / Public | `landing.html` | Keine | — | Keins |
| Textseiten (Proyecto etc.) | `promat_page.html` | Keine | — | Keins |
| Research | `research_*.html` | Keine | — | Keins |
| Research Player | `research_player.html` | Keine | — | Keins |
| Teaching | `teaching_page.html` | Keine | — | Keins |
| Admin | `admin_analytics.html`, `admin_users.html` | Keine | — | Keins |
| Auth/Login | `login.html`, `account.html`, `password_*.html` | Keine | — | Keins |
| Fehlerseiten | `errors/*.html` | Keine | — | Keins |
| Footer | `partials/footer.html` | Keine | — | Keins |

**Fazit:** Nahezu alle Templates sind vollständig vom MD3-HTML-System migriert. Nur das no-op `md3-status-live` verblieben.

---

## 4. Aktive CSS-Klassen-Abhängigkeiten

### MD3-Klassen, die noch aktiv auf DOM-Elemente angewendet werden

| MD3-Klasse | Erzeugt durch | Aktuelle MD3-CSS-Datei | Beschreibung | Migration |
|---|---|---|---|---|
| `md3-alert`, `md3-alert--error`, `md3-alert--warning`, `md3-alert--info`, `md3-alert--success`, `md3-alert__icon`, `md3-alert__content`, `md3-alert__title`, `md3-alert__text` | `alert-utils.js` (JS, dynamisch) | `alerts.css` | Alert-Banner | `pm-alert--*` CSS fehlt noch in App-CSS |
| `md3-alert--inline`, `md3-alert--banner` | `alert-utils.js` | `alerts.css` | Alert-Layout-Varianten | — |
| `md3-field-error`, `md3-field-support`, `md3-error-text` | `alerts.css` direkt | `alerts.css` | Formularfeld-Fehlermeldungen | — |
| `md3-snackbar`, `md3-snackbar--success`, `md3-snackbar--error`, `md3-snackbar--info`, `md3-snackbar--warning` | `snackbar.js` (JS, dynamisch) | `snackbar.css` | Toast-Notifications | `pm-snackbar--*` CSS fehlt noch in App-CSS |
| `md3-snackbar__icon`, `md3-snackbar__message`, `md3-snackbar__action` | `snackbar.js`, `login.js` | `snackbar.css` | Snackbar-Inneres | — |
| `md3-form-error` | `login.js` | `alerts.css` (adjacent) | Formfehler-Container | — |
| `md3-status-live` | `_admonition.html` | `layout.css` | Pointer-events-Marker (no-op) | Trivial: Klasse entfernen oder behalten |
| `.pm-footer-shell` (+ `.md3-footer` Alias) | `base.html` | `footer.css` | Footer-Shell | Alias entfernen, `.pm-footer-shell` zu App-CSS |
| `.md3-card` (in `40_cards.css` Selektor) | `40_cards.css` | `cards.css` (indirekt) | `.md3-card` im App-CSS-Selektor | `.md3-card` aus `40_cards.css` Selektor entfernen |

### MD3-Klassen, die ausschließlich in totem CSS definiert sind

Alle `.md3-button--*`, `.md3-card--*` (varianten), `.md3-dialog__*`, `.md3-outlined-textfield__*`, `.md3-navigation-drawer__*`, `.md3-top-app-bar__*`, `.md3-user-menu__*`, `.md3-badge`, `.md3-nav__*`, `.md3-hero__*`, `.md3-text-page`, `.md3-page-navigation`, `.md3-display-*`, `.md3-headline-*`, `.md3-title-*`, `.md3-body-*`, `.md3-label-*` usw. — **kein Template produziert diese Klassen**.

---

## 5. Aktive CSS-Variablen-Abhängigkeiten

### Token-Bridge in `00_tokens.css`

`00_tokens.css` definiert einen vollständigen Mapping-Layer, der alle MD3-Tokens auf promat-Werte überschreibt:

| MD3-Variable (in md3/tokens.css) | Brücke in 00_tokens.css | Promat-Ziel | Empfehlung |
|---|---|---|---|
| `--md-sys-color-primary` | `var(--promat-primary)` | `var(--book-accent)` | Kann nach Phase 5 als direkter promat-Alias bleiben |
| `--md-sys-color-surface` | `var(--promat-surface)` | Abgeleitet von `--book-bg` | Kann bleiben |
| `--md-sys-color-*` (alle anderen) | Alle gemappt | Promat-Aquivalente | Abhängig von alerts/snackbar Migration |
| `--space-1..12` | `var(--promat-space-1..9)` | Promat-Spacing | Können nach Migration ersetzt werden |
| `--radius-sm/md/lg` | `var(--promat-radius-*)` | Promat-Radius | Können nach Migration ersetzt werden |
| `--elev-1..5` | `var(--promat-shadow-soft/panel)` | Promat-Shadows | Können nach Migration ersetzt werden |
| `--md-motion-*`, `--md-state-*` | Nicht gemappt | — | Nicht im App-CSS genutzt → nach Migration obsolet |
| `--md-sys-typescale-*` | Nicht gemappt | — | Referenziert nur in md3/ CSS → nach Migration obsolet |

### Variablen außerhalb von md3/ genutzt

| Variable | Genutzt in | Quelle | Wichtigkeit |
|---|---|---|---|
| `--md-sys-color-on-background` | `layout.css` Z.7 | `00_tokens.css` Bridge | Muss als promat-Token ersetzt werden |
| `--app-background` | `layout.css`, mehrere md3-Komponenten | `00_tokens.css` (`var(--book-bg)`) | Bleibt; in App-CSS bereits definiert |
| `--app-textfield-label-bg` | `md3/components/textfields.css` | Nicht in App-CSS | Nur in toter textfield CSS → mit Migration obsolet |
| `--md-sys-color-*` (in alerts/snackbar CSS) | `alerts.css`, `snackbar.css` | `00_tokens.css` Bridge | Muss bestehen bleiben bis PM-Alerts/Snackbars migriert |

---

## 6. JS-Abhängigkeiten

| JS-Datei | MD3-Abhängigkeit | Funktion | Status | Risiko bei Migration |
|---|---|---|---|---|
| `modules/navigation/drawer.js` | `.md3-navigation-drawer__submenu`, `.md3-navigation-drawer__trigger` | Inert-State-Init, Collapsible-Accordion | **Stale** — template hat `promat-panel-*`; Queries finden nichts | Niedrig: removeAttibute aufrufe auf null-Elementen laufen ins Leere |
| `modules/navigation/turbo-integration.js` | 11 verschiedene `.md3-navigation-drawer__*` Klassen | Active-Link-State, Submenu-Restore | **Stale** — alles tote Selektoren | Mittel: active-link-highlighting funktioniert nicht → aber visuell schon über `aria-current` |
| `modules/navigation/material-symbols-loader.js` | `.md3-navigation-drawer__item, .md3-icon-button` | Font-Fallback: Elemente ausblenden falls Font nicht lädt | **Stale** — Elemente nicht im DOM | Niedrig: Fallback wirkt nicht, aber Font-Check arbeitet weiter |
| `logout.js` | `.md3-user-menu__item--logout` (Fallback-Selektor) | Logout-Click-Handler | **Stale** — primärer `[data-logout="fetch"]` Selektor funktioniert | Trivial |
| `md3/alert-utils.js` | Erzeugt `md3-alert md3-alert--*` Klassen | Alert-HTML-Generator | **Aktiv** | Hoch: Styling bricht, wenn `alerts.css` entfernt wird |
| `modules/core/snackbar.js` | Erzeugt `md3-snackbar md3-snackbar--*` Klassen | Snackbar/Toast-System | **Aktiv** | Hoch: Styling bricht, wenn `snackbar.css` entfernt wird |
| `modules/auth/login.js` | Erzeugt `md3-snackbar md3-snackbar--error` | Login-Fehler-Anzeige | **Aktiv** | Hoch |
| `auth/password_reset.js` | Importiert `alert-utils.js` | Passwort-Formular-Fehler | **Aktiv** | Hoch |

### Ergebnis

- 4 JS-Dateien mit **stale** MD3-Selektoren → können parallel zu CSS-Cleanup bereinigt werden
- 4 JS-Dateien (**alert-utils.js**, **snackbar.js**, **login.js**, **password_reset.js**) erzeugen **aktiv** MD3-DOM-Klassen → `alerts.css` und `snackbar.css` können erst entfernt werden, wenn die JS-Seite migriert ist

---

## 7. Test-Abhängigkeiten

| Test-Datei | MD3-Abhängigkeit | Art | Empfehlung |
|---|---|---|---|
| `test_auth_phase1.py` | `assert "md3-card" not in html`, `assert "md3-button" not in html`, `assert "md3-outlined-textfield" not in html`, `assert "md3-error-page" not in html`, `assert "md3-error-container" not in html`, `assert "md3-snackbar--auth-expired" not in css` | **Regressionschutz** — stellt sicher, dass keine MD3-Klassen in HTML zurückkommen | Behalten und erweitern |
| `test_research_phenomena.py` | `assert 'md3-dialog' not in ...`, `assert "md3-button" not in html` | **Regressionschutz** | Behalten |
| `test_research_sessions.py` | `navigation` (nicht direkt md3) | Unspezifisch | Prüfen ob `promat-panel` Tests vorhanden |

**Fazit Tests:**
- Vorhanden: Negative Regressionstests (keine md3-Klassen in HTML)
- Fehlend: Positive Tests für `promat-panel`, `promat-topbar`, `promat-user-menu` — sollten nach Migration ergänzt werden

---

## 8. Material-Symbols-Plan

**Aktueller Status:**
- `MaterialSymbolsRounded.woff2` liegt in `app/static/fonts/`
- Einbindung über `md3/components/material-symbols-fallback.css` (`@font-face` + `.material-symbols-rounded` Basisstil)
- Dynamisches Laden via `material-symbols-loader.js` (Font-Loading-API-basiert)
- Aktive Nutzung: `alert-utils.js` und `snackbar.js` erzeugen HTML mit `.material-symbols-rounded`

**MD3-Entfernung ≠ Material-Symbols-Entfernung.** Die Schrift muss weiterhin eingebunden bleiben.

**Plan:**
1. `md3/components/material-symbols-fallback.css` → verschieben nach `app/static/css/material-symbols.css`
2. `base.html`-Link entsprechend anpassen
3. Material Symbols Font und CSS-Klasse weiterhin intakt lassen
4. `material-symbols-loader.js` bereinigen (stale `.md3-navigation-drawer__item` Selektor entfernen)

---

## 9. Font/Typefaces-Plan

**Aktueller Zustand:**
- `md3/components/typefaces.css` enthält `@font-face`-Deklarationen für Inter (Variable, Italic) und Source Serif 4 (Variable, Italic)
- Diese Datei ist **nicht MD3-spezifisch** und gehört fachlich nicht zum MD3-System
- Fonts liegen in `app/static/fonts/`

**Zielpfad:**
```
app/static/css/typefaces.css
```
oder
```
app/static/css/01_typefaces.css
```

**Anpassungsbedarf:**
- `base.html`: Link von `md3/components/typefaces.css` auf `css/typefaces.css` ändern
- Tests: CSP-Tests (`test_auth_phase1.py` Z.2502) prüfen CSS-Klassen, nicht Pfade — unverändert
- `00_tokens.css`: Referenziert `--book-font-ui: "Inter"` und `--book-font-body: "Source Serif 4"` → Fonts müssen weiterhin geladen sein

---

## 10. Mapping MD3 → App-CSS

### Token-Mapping (bereits vorhanden in `00_tokens.css`)

| MD3-Token | App-Token | Status |
|---|---|---|
| `--md-sys-color-primary` | `--book-accent` / `--promat-primary` | ✅ Gemappt |
| `--md-sys-color-surface` | `--promat-surface` | ✅ Gemappt |
| `--md-sys-color-on-surface` | `--promat-fg` | ✅ Gemappt |
| `--md-sys-color-error` | `#b75548` (direkt) | ✅ Gemappt |
| `--space-4` | `--promat-space-4` | ✅ Gemappt |
| `--radius-md` | `--promat-radius-md` | ✅ Gemappt |
| `--elev-2` | `--promat-shadow-soft` | ✅ Gemappt |

### Klassen-Mapping für verbleibende aktive Komponenten

| MD3-Klasse | Aktion | Ziel App-CSS |
|---|---|---|
| `.md3-alert`, `.md3-alert--*` | JS auf `pm-alert--*` umstellen + CSS in `30_components.css` migrieren | `pm-alert`, `pm-alert--error` etc. |
| `.md3-snackbar`, `.md3-snackbar--*` | JS auf `pm-snackbar--*` umstellen + CSS in `30_components.css` migrieren | `pm-snackbar`, `pm-snackbar--error` etc. |
| `.material-symbols-rounded` | CSS-Datei verschieben, keine Klassenänderung | `material-symbols.css` |
| `.md3-footer` (Alias in `footer.css`) | Alias entfernen, `.pm-footer-shell` bleibt | Bereits in `30_components.css` |
| `.md3-card` (in `40_cards.css`) | Aus Selektor in `40_cards.css` Z.7 entfernen | `40_cards.css` bereinigen |
| `.md3-content-wrapper` (in `layout.css`) | Referenz prüfen; `layout.css` nutzt `.md3-content-wrapper` als Alias | `.pm-content-wrapper` allein genügt |
| `--md-sys-color-on-background` in `layout.css` | Durch `--promat-fg` oder `--book-fg` ersetzen | `layout.css` bereinigen |

---

## 11. Empfohlene Zielstruktur App-CSS

Zielzustand nach vollständiger Migration:

```
app/static/css/
  layout.css                  (Bestand, --md-sys-* Referenz bereinigen)
  typefaces.css               (Neu: aus md3/components/typefaces.css)
  material-symbols.css        (Neu: aus md3/components/material-symbols-fallback.css)
  00_tokens.css               (Bestand; --space-*, --radius-*, --elev-*, --md-sys-* Bridge entfernen nach Phase 5)
  10_typography.css           (Bestand)
  20_layout.css               (Bestand)
  30_components.css           (Bestand; pm-alert, pm-snackbar hinzufügen)
  40_cards.css                (Bestand; .md3-card aus Selektoren entfernen)
  50_navigation.css           (Optional: promat-panel CSS aus 30_components.css auslagern)
```

**Nicht empfohlen:** Eine neue parallele Dateistruktur erzeugen, die die Situation nicht verbessert. Priorität hat das Entfernen toter CSS-Last.

---

## 12. Phasenplan zur Migration

### Phase 0 — Schutznetz (0-2h, sofort möglich)

**Ziel:** Baseline dokumentieren, Regressionsnetz aufspannen

- Aktuelle visuelle Screenshots erfassen: `/de`, `/de/project/projekt`, `/de/research`, `/de/teaching`, `/account`, `/admin/users`, Login-Dialog, Research Player
- Viewports: 390px, 768px, 1280px
- Sicherstellen dass Tests `test_auth_phase1.py` und `test_research_phenomena.py` grün laufen
- Commit-Stand als Tag setzen (optional)

**Risiken:** Keine  
**Rollback:** N/A (read-only Phase)

---

### Phase 1 — Nicht-MD3-Dateien aus md3/ herauslösen (1-2h, risikoarm)

**Ziel:** `typefaces.css` und `material-symbols-fallback.css` korrekt verorten

**Dateien:**
1. `app/static/css/md3/components/typefaces.css` → `app/static/css/typefaces.css`
2. `app/static/css/md3/components/material-symbols-fallback.css` → `app/static/css/material-symbols.css`

**Änderungen in `base.html`:**
```html
<!-- Alt: -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/md3/components/typefaces.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/md3/components/material-symbols-fallback.css') }}">
<!-- Neu: -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/typefaces.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/material-symbols.css') }}">
```

**Tests:** CSP-Test in `test_auth_phase1.py` prüft keine Pfade, nur Klassen → unverändert  
**Visuelle Prüfrouten:** `/de` (Fonts), alle Seiten mit Icons  
**Rollback:** Links in `base.html` zurückändern

---

### Phase 2 — Totes Navigation-CSS entfernen (2-4h, risikoarm)

**Ziel:** CSS-Links für tote Navigationkomponenten aus `base.html` entfernen

**Dateien (Entfernung aus base.html):**
- `md3/components/top-app-bar.css` — Template nutzt `promat-topbar`
- `md3/components/navigation-drawer.css` — Template nutzt `promat-panel`
- `md3/components/navbar.css` — nicht in aktuellen Templates

**Gleichzeitig:** JS bereinigen
- `drawer.js`: Stale-Selektoren `.md3-navigation-drawer__submenu`, `.md3-navigation-drawer__trigger` entfernen oder durch `promat-panel__*`-Äquivalente ersetzen
- `turbo-integration.js`: Stale `.md3-navigation-drawer__*` Selektoren durch neue `promat-panel__*` Selektoren ersetzen oder nicht mehr benötigte Funktionen entfernen
- `material-symbols-loader.js`: `.md3-navigation-drawer__item` aus Selektor entfernen
- `logout.js`: `.md3-user-menu__item--logout` Fallback-Selektor entfernen

**Risiken:** Mittel — Drawer-Accordion und Active-Link-Highlighting könnten betroffen sein  
**Tests:** Browser-Check Navigation, Accordion-Verhalten, Active-Link-State  
**Visuelle Prüfrouten:** Alle Seiten mit Navigation, Mobile Drawer, Desktop Drawer  
**Rollback:** Links in `base.html` wiederherstellen

---

### Phase 3 — Totes Utility-CSS entfernen (2-3h, mittel)

**Ziel:** CSS-Links für tote Utility-Komponenten aus `base.html` entfernen

**Dateien (Entfernung aus base.html):**
- `md3/typography.css` — keine Template-Nutzung
- `md3/components/buttons.css` — keine Template-Nutzung
- `md3/components/cards.css` — keine Template-Nutzung (aber `.md3-card` in `40_cards.css` vorher entfernen!)
- `md3/components/dialog.css` — keine Template-Nutzung
- `md3/components/textfields.css` — keine Template-Nutzung
- `md3/components/login.css` — Template nutzt promat-Klassen
- `md3/components/hero.css` — Template nutzt promat-Klassen
- `md3/components/text-pages.css` — Template nutzt promat-Klassen
- `md3/components/page-navigation.css` — keine Template-Nutzung
- `md3/components/layout-helpers.css` — keine Template-Nutzung
- `md3/components/como-citar.css` — Template-Nutzung unklar (muss vor Entfernung verifiziert werden)

**Gleichzeitig:**
- `40_cards.css`: `.md3-card` aus Selektor in Z.7 entfernen
- `layout.css`: `--md-sys-color-on-background` durch `--book-fg` ersetzen

**Risiken:** Mittel — falls eine Seite doch noch md3-Klassen nutzt, wird sie stillos  
**Tests:** Alle Templates Browser-Check, besonders Auth- und Admin-Seiten  
**Rollback:** Links in `base.html` wiederherstellen

---

### Phase 4 — Aktive MD3-Komponenten migrieren (4-8h, Hauptarbeit)

**Ziel:** `alerts.css` und `snackbar.css` ersetzen durch App-CSS

**Vorgehensweise:**
1. `pm-alert--*` CSS in `30_components.css` erstellen (semantisch equivalent zu `md3-alert--*`)
2. `pm-snackbar--*` CSS in `30_components.css` erstellen (semantisch equivalent zu `md3-snackbar--*`)
3. `alert-utils.js`: Doppelklassen (`pm-alert md3-alert`) auf reine `pm-alert` reduzieren
4. `snackbar.js`: Doppelklassen auf reine `pm-snackbar` reduzieren
5. `login.js`: Doppelklassen auf reine `pm-*` reduzieren
6. Dann `md3/components/alerts.css` und `md3/components/snackbar.css` aus base.html entfernen

**Risiken:** Hoch — Alerts und Snackbars sind sichtbare Nutzerfeedback-Elemente  
**Tests:** Auth-Flows (Login-Fehler, Passwort-Reset, Logout), Research-Phänomene  
**Visuelle Prüfrouten:** Login mit falschem Passwort, Passwort-Änderung, Phänomene-Aktionen  
**Rollback:** Doppelklassen behalten; CSS-Links wiederherstellen

---

### Phase 5 — Restliche MD3-Dateien entfernen (1-2h)

**Ziel:** Verbleibende MD3-Dateien aus `base.html` entfernen

**Dateien:**
- `md3/layout.css` — prüfen ob `.md3-stack--*`, `.m-*` noch in Templates
- `md3/components/footer.css` — `.pm-footer-shell` nach `30_components.css` übernehmen, `.md3-footer`-Alias entfernen
- `md3/components/mobile-responsive.css` — globale mobile Overrides nach `layout.css` / `30_components.css` überführen
- `md3/components/motion.css` — globale `:focus-visible` Regel prüfen (`30_components.css` hat eigene)

**Gleichzeitig:**
- `md3/tokens.css` aus `base.html` entfernen (sobald `alerts.css` und `snackbar.css` migriert)
- Token-Bridge in `00_tokens.css` bereinigen (--md-sys-* Aliases können entfernt werden wenn alerts/snackbar migriert)

**Risiken:** Mittel — globale Regeln aus mobile-responsive.css und motion.css müssen sicher überführt werden  
**Tests:** Mobile-Rendering, Focus-States  
**Rollback:** Links wiederherstellen

---

### Phase 6 — md3/-Ordner entfernen (30min)

**Vorbedingung:** Keine aktiven Referenzen auf `md3/` in `base.html`, JS oder Templates

**Aktion:**
```bash
git rm -r app/static/css/md3/
```

**Tests:** Kompletter Regression-Pass aller Test-Suiten  
**Visuelle Prüfrouten:** Alle kritischen Seiten in allen Viewports  
**Rollback:** `git revert`

---

## 13. Visuelle Prüfrouten und Viewports

### Kritische Prüfrouten

| Route | Prüffokus |
|---|---|
| `/de` | Landing: Wordmark, Cards, Navigation, Icons, Fonts |
| `/de/project/projekt` | Textseite: Prose, Hero, Page-Navigation |
| `/de/research` | Research-Startseite: Navigation, Panel |
| `/de/teaching/spanish/r` | Teaching: Promat-Panel, Sidebar, Audio-Player |
| `/de/research/spanish/phenomena/overview` | Phenomena: Buttons, Dialoge, Admin-Aktionen (wenn Admin) |
| `/account` | Auth: Formular, Buttons, Error-States |
| `/admin/users` | Admin: Tabelle, Dialoge, Badges |
| Login-Flow | Login-Dialog, Fehler-Alerts, Snackbar bei Erfolg |
| Passwort-Reset | Alert-Anzeige, Form-Errors |

### Viewports

| Viewport | Typ |
|---|---|
| 390px | Mobile small (iPhone 14) |
| 768px | Tablet |
| 1280px | Desktop Standard |
| 1920px | Desktop Wide |

### Prüffokus je Viewport

- Navigation: Hamburger (mobile), Drawer (desktop)
- Top App Bar: Transparent (desktop), opak (mobile)
- User-Menü: Avatar/Chip (alle Viewports)
- Material Icons: Snackbar-Icons, Alert-Icons
- Cards, Buttons, Badges, Forms
- Overflow-Menüs, Dialoge
- Keine horizontalen Scrollbars
- Mobile: Touch-Targets ≥ 44px

---

## 14. Risikoanalyse

| Risiko | Kategorie | Beschreibung | Einstufung |
|---|---|---|---|
| Alerts und Snackbars verlieren Styling | **Blocker** | JS erzeugt `md3-alert` / `md3-snackbar` Klassen; CSS muss vor JS-Migration bestehen bleiben | Blocker |
| Drawer-JS findet keine Elemente | High | `drawer.js`, `turbo-integration.js` haben stale MD3-Selektoren → Accordion und Active-Link-Highlighting funktionieren ggf. nicht korrekt | High — aber schon jetzt defekt da Templates migriert sind |
| Material Symbols brechen | High | Font und `.material-symbols-rounded` CSS müssen sicher aus `md3/` herausgelöst werden | High; Risiko beherrschbar durch Phase 1 |
| Token-Bridge-Abriss | High | `--md-sys-color-*` Tokens werden in alerts/snackbar CSS referenziert; Bridge in `00_tokens.css` muss bis Phase 5 bestehen bleiben | High; klar kontrollierbar |
| Mobile-Responsive-Regeln verloren | Medium | `mobile-responsive.css` enthält globale Regeln (html overflow-x, z-index vars, Atlas-Map-Fixes) die nicht einfach wegfallen dürfen | Medium |
| `.focus-visible` überschrieben | Medium | `motion.css` hat globalen `:focus-visible` Override; `30_components.css` hat eigenen — Reihenfolge prüfen | Medium |
| `40_cards.css` Selektor `.md3-card` | Medium | `.md3-card` in `40_cards.css` Zeile 7 — wenn `cards.css` entfernt wird bevor dieser Selektor bereinigt ist, verliert `.md3-card` seinen Stil | Medium; vor Phase 3 bereinigen |
| footer.css `.pm-footer-shell` Alias | Medium | Alias in `footer.css` — wenn `footer.css` entfernt, verliert `.pm-footer-shell` seine Stile wenn sie nicht vorher nach `30_components.css` übernommen wurden | Medium |
| stale `--md-sys-color-on-background` in layout.css | Low | `layout.css` Z.7 nutzt `--md-sys-color-on-background` mit `CanvasText` Fallback; Bridge-Entfernung in Phase 5 würde den Fallback aktivieren | Low |
| CSS-Spezifitätskonflikte | Low | Wenn md3-CSS entfernt wird, könnten promat-CSS-Regeln durch fehlende md3-Überschreibungen sichtbar werden | Low |
| Template-Regression durch md3-Klasse | Low | Falls ein Template versehentlich neue md3-Klassen erhält — Tests fangen das ab | Low — Schutznetz vorhanden |
| JS Logout-Fallback-Selektor | Info | `logout.js` hat `.md3-user-menu__item--logout` als Fallback — primärer `[data-logout="fetch"]` funktioniert | Info |

---

## 15. Offene Fragen

1. **`como-citar.css`**: Kein Template-Match für `.doi-resource-grid`, `.doi-resource-card` gefunden. Werden diese Klassen vielleicht dynamisch durch Python-Builder erzeugt? Vor Phase 3 prüfen.

2. **`drawer.js` / `turbo-integration.js`**: Sind `initCollapsibles()` und Active-Link-Restore schon heute defekt, weil das Template die `promat-panel` Struktur nutzt? Wenn ja, muss das **vor** Phase 2 gefixt werden — nicht danach. Klarheit über die neue `promat-panel__*` Collapsible-Struktur erforderlich.

3. **`pm-alert` / `pm-snackbar` CSS**: Wo genau soll es landen — in `30_components.css` oder in neuen Dateien `50_alerts.css` und `51_snackbar.css`? Entscheidung vor Phase 4 nötig.

4. **`mobile-responsive.css` Atlas-Map-Fixes**: Die Leaflet/Atlas-Map Z-Index-Korrekturen in `mobile-responsive.css` müssen vor Phase 5 sicher in ein geeignetes App-CSS-File überführt werden.

5. **`motion.css` Reduced-Motion-Regeln**: `@media (prefers-reduced-motion: reduce)` mit `* { transition-duration: 0.01ms !important }` — ist das noch in allen Viewports korrekt? Clash mit promat-transition-Regeln?

6. **`--app-textfield-label-bg`**: Wird ausschließlich in `textfields.css` definiert und genutzt. Nach Phase 3 (Entfernung textfields.css) obsolet. Prüfen ob `30_components.css` promat-Textfelder hat.

7. **`typefaces.css` CSP-Prüfung**: Nach Phase 1 prüfen ob der neue Pfad `css/typefaces.css` nicht durch CSP-Tests oder Header-Konfiguration blockiert wird.

---

## 16. Empfehlung: Jetzt migrieren ja/nein?

**Ja — Phase 1 und Phase 2 sofort möglich und empfohlen.**

Begründung:
- Die Templates sind bereits vollständig migriert
- Die CSS-Dateien für Navigation, Buttons, Cards, Dialoge, Textfelder sind bereits **dead CSS**
- Jede geladene MD3-Datei kostet Ladezeit und erhöht die Angriffsfläche für Spezifitätskonflikte
- Phase 1 (typefaces, material-symbols) ist komplett risikolos
- Phase 2 (Navigations-CSS + JS-Cleanup) ist mit Browser-Check sicher durchführbar

**Warnung:** Phases 4 und 5 sind aufwendiger und haben höhere Risiken — dort ist sorgfältige Vorbereitung und Testing nötig.

---

## 17. Konkreter erster Umsetzungs-Prompt für Phase 1

```
Arbeite auf dem aktuellen Branch `main`.

Phase 1 der MD3-Migration: Nicht-MD3-Dateien aus md3/ herauslösen.

1. Kopiere `app/static/css/md3/components/typefaces.css` nach 
   `app/static/css/typefaces.css` (Inhalt unverändert).

2. Kopiere `app/static/css/md3/components/material-symbols-fallback.css` nach
   `app/static/css/material-symbols.css` (Inhalt unverändert).

3. Passe `app/templates/base.html` an:
   - Ersetze den Link auf `css/md3/components/typefaces.css` durch `css/typefaces.css`
   - Ersetze den Link auf `css/md3/components/material-symbols-fallback.css` durch `css/material-symbols.css`
   - Entferne die Link-Tags für diese beiden Dateien aus dem md3/-Block

4. Lösche die Originaldateien aus md3/components/:
   - `app/static/css/md3/components/typefaces.css`
   - `app/static/css/md3/components/material-symbols-fallback.css`

5. Starte den Dev-Server und prüfe visual im Browser:
   - `/de` auf 390px und 1280px: Fonts Inter und Source Serif 4 korrekt?
   - Navigation Icons sichtbar?
   - Material Symbols in Alerts/Snackbars sichtbar?

6. Führe Tests aus: `pytest app/tests/test_auth_phase1.py -x`

7. Berichte Ergebnis — Änderungen nur committen wenn explizit gebeten.
```

---

## Phase 1–2 Follow-up 2026-05-30

**Commit zum Zeitpunkt der Ausführung:** `8bc98b562e29c5d301ff4a612625d5d0c2d48a6d`  
**Arbeitsbaum vorher:** sauber (keine uncommitted Änderungen)  
**Änderungen nicht committet** — Arbeitsbaum mit Änderungen hinterlassen für lokale Sichtprüfung.

### Umgesetzt

**Phase 1 — Nicht-MD3-Dateien herauslösen:**
- `app/static/css/md3/components/typefaces.css` → `app/static/css/typefaces.css` (via `git mv`)
- `app/static/css/md3/components/material-symbols-fallback.css` → `app/static/css/material-symbols.css` (via `git mv`)
- `app/templates/base.html` angepasst: neue Pfade für beide Dateien eingebunden
- Lade-Reihenfolge beibehalten: `typefaces.css` früh, `material-symbols.css` vor App-Komponenten

**Phase 2 — Alerts/Snackbars nach App-CSS migrieren:**
- `app/static/css/50_feedback.css` neu erstellt: 1:1-Migration aller Selektoren von `md3-*` auf `pm-*`
- `app/templates/base.html`: `50_feedback.css` nach `40_cards.css` eingebunden
- `app/templates/base.html`: Links auf `md3/components/alerts.css` und `md3/components/snackbar.css` entfernt
- `app/static/js/md3/alert-utils.js`: Generierte Klassen von `pm-alert md3-alert ...` auf reine `pm-alert ...` umgestellt; `window.md3AlertUtils` → `window.pmAlertUtils`
- `app/static/js/modules/core/snackbar.js`: Generierte Klassen von `pm-snackbar md3-snackbar ...` auf reine `pm-snackbar ...` umgestellt; Dismiss-Button-Selektor bereinigt; `window.MD3Snackbar` → `window.PMSnackbar`
- `app/static/js/modules/auth/login.js`: Selektor und generierte Klassen auf reine `pm-*` umgestellt

### Geänderte Dateien

| Datei | Art der Änderung |
|---|---|
| `app/static/css/md3/components/typefaces.css` | Verschoben nach `app/static/css/typefaces.css` |
| `app/static/css/md3/components/material-symbols-fallback.css` | Verschoben nach `app/static/css/material-symbols.css` |
| `app/static/css/50_feedback.css` | Neu angelegt (migrated from alerts.css + snackbar.css) |
| `app/templates/base.html` | 2× Pfad aktualisiert, 1× neuer Link, 2× Links entfernt |
| `app/static/js/md3/alert-utils.js` | md3-* Klassen aus generiertem HTML entfernt |
| `app/static/js/modules/core/snackbar.js` | md3-* Klassen aus generiertem HTML entfernt |
| `app/static/js/modules/auth/login.js` | md3-* Klassen aus Selektor und generiertem HTML entfernt |
| `app/tests/test_auth_phase1.py` | Test-Pfadassertionen auf neue CSS-Pfade aktualisiert |

### Klassenmigration (vollständig)

Alert: `md3-alert` → `pm-alert`, inkl. alle Varianten (`--error`, `--warning`, `--info`, `--success`, `--inline`, `--banner`, `--field`, `--above`, `--below`, `--dismissible`) und alle BEM-Elemente (`__icon`, `__content`, `__title`, `__text`, `__message`, `__close`).

Weitere Alert-nahe Klassen: `md3-field-support` → `pm-field-support`, `md3-field-error` → `pm-field-error`, `md3-error-text` → `pm-error-text`, `md3-form-status` → `pm-form-status`, `md3-sr-status` → `pm-sr-status`.

Snackbar: `md3-snackbar` → `pm-snackbar`, inkl. alle Varianten (`--success`, `--error`, `--info`, `--warning`) und alle BEM-Elemente (`__icon`, `__message`, `__action`).

`.material-symbols-rounded` in beiden Komponenten: **unverändert**.

### Referenzprüfung

- Aktive md3-alert/md3-snackbar Referenzen in Templates, JS, App-CSS: **keine mehr**
- Verbleibende md3-snackbar Referenzen: nur noch in den noch-auf-Disk-liegenden MD3-Quelldateien (`alerts.css`, `snackbar.css`) sowie in `motion.css:296` und `mobile-responsive.css:335` (beide noch geladen, Phase 5 Scope; betreffen aber keine aktiv erzeugten DOM-Elemente mehr)
- CSS-Links für alle 4 migrierten Dateien auf neue Pfade aktualisiert
- pm-* Zielklassen korrekt in JS und CSS vorhanden

### Testergebnisse

```
667 passed, 0 failed, 120 warnings — 78s
```

Ruff: `All checks passed!`  
CI Governance: `All governance checks passed.`

### UI-Prüfung

Lokale Browserprüfung steht aus — Änderungen im Arbeitsbaum hinterlassen für manuelle Sichtprüfung durch den Entwickler. Zu prüfen: Alerts, Snackbars, Login-Fehler, Material Symbols Icons, keine 404-Fehler für CSS/Fonts.

### Bewusst nicht umgesetzt

- **Phase 3**: Entfernung weiterer toter MD3-Dateien — nicht in diesem Run
- **`app/static/js/auth/password_reset.js`**: Erzeugt keine Alert-Klassen direkt (nutzt `showError`/`showSuccess` aus `alert-utils.js`); verbleibende Referenz `.md3-outlined-textfield__icon--trailing` ist ein Textfield-Concern (Phase 5)
- **`md3/tokens.css`**: Nicht entfernt — noch nicht sicher, ob alle Abhängigkeiten vollständig durch `00_tokens.css` abgedeckt
- **`md3/components/motion.css`**, **`md3/components/mobile-responsive.css`**: Noch global geladen — globale Regeln aktiv (Phase 5)
- **`md3/components/footer.css`**: Hat aktive `.pm-footer-shell` Regel — Phase 5
- **Dateiumzug von `alert-utils.js`**: Datei verbleibt unter `app/static/js/md3/alert-utils.js` — Import-Pfade in Phase 4/5 bereinigen

### Offene Risiken

- `motion.css:296` und `mobile-responsive.css:335` referenzieren `.md3-snackbar` — inaktive Selektoren, kein DOM-Match mehr, aber technisch totes CSS in noch-geladenen Dateien
- `window.pmAlertUtils` und `window.PMSnackbar` sind neue globale Namen — falls externe Skripte `window.md3AlertUtils` oder `window.MD3Snackbar` nutzen, brechen diese. In der Codebase nicht gefunden.

---

## Abschluss

| Metrik | Wert |
|---|---|
| MD3-CSS-Dateien gesamt | 23 |
| MD3-Klassen in Templates | 1 (`md3-status-live`, no-op) |
| JS-Dateien mit stalen MD3-Selektoren | 4 (drawer.js, turbo-integration.js, material-symbols-loader.js, logout.js) |
| JS-Dateien die aktiv MD3-Klassen erzeugen | 4 (alert-utils.js, snackbar.js, login.js, password_reset.js) |
| Tote MD3-CSS-Dateien (keine Template-Nutzung) | 16 von 23 |
| Größte Risikobereiche | Alerts/Snackbar-Migration (Phase 4), Mobile-Responsive-Überführung (Phase 5) |
| Empfohlene erste Phase | Phase 1: typefaces.css + material-symbols.css herauslösen |
| Direkte Entfernung von `app/static/css/md3/` möglich? | **Nein** — Migration nur phasenweise |
