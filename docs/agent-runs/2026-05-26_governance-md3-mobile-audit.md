# Governance + MD3 + Mobile Readiness Audit

## 1. Scope

Geprüft wurden Governance-/Instruction-Dateien, aktive Specs, Runbooks, `.github`-Regeln, produktive Templates, produktive CSS-/JS-Einstiegspunkte, MD3-Reste, Token-/CSS-Konsistenz sowie mobile/responsive Eignung der Webapp anhand statischer Analyse und erlaubter Tests.

Ausdrücklich nicht durchgeführt wurden Fixes, Formatierung, Migrationen, CSS-Bereinigung, MD3-Entfernung, Design-System-Migration, Browser-Aktionen mit Seiteneffekten, Prod-Paketbau oder Serverkontakt. Historische `docs/agent-runs/**` wurden nicht als aktive Governance-Quelle gewertet.

## 2. Kurzfazit

- Governance-Status: im Kern sauber. Root-/Scoped-Instructions, PR-Template, Specs und Runbooks zeigen konsistent auf `docs/spec/` als aktive Source of Truth und verlangen Run-Logs.
- MD3-Reststatus: gemischter Übergangszustand. Die sichtbare Shell nutzt `promat-*`/`pm-*`, aber `base.html` lädt noch viele `css/md3/**`-Dateien global und das globale JS importiert weiterhin das MD3-Navigation-Modul.
- Design-System-/Tokenstatus: `00_tokens.css`, `20_layout.css`, `30_components.css` und `40_cards.css` bilden den produktiven PM/PROMAT-Kanon. MD3-Tokens und einige `!important`-/Utility-Reste umgehen diesen Kanon noch.
- Mobile-/Responsive-Status: statisch überwiegend prod-tauglich für Public/Auth/Research/Teaching, aber visuelle QA für 360-390 px, Player, Comparison, Drawer und Admin-Tabellen bleibt vor Prod sinnvoll.
- Navigation-Status: aktuelle Topbar/Drawer-Struktur ist konsistent und touch-orientiert. Legacy-MD3-Drawer-Selektoren bleiben als JS/CSS-Rest und sollten separat reduziert werden.
- Wichtigste Risiken: Security-Kontakt TODO in `.github/SECURITY.md`, globale MD3-CSS-Last, unklare unreferenzierte MD3-Dateien, MD3-Navigation-JS mit alten Selektoren, fehlende Browser-Viewport-QA.
- Empfohlene Reihenfolge: Governance Cleanup, Responsive Mobile Hardening, MD3 Legacy Reduction, danach CSS Token Consistency Cleanup.

## 3. Governance / Instructions

| Datei | Befund | Status | Risiko | Empfehlung |
|---|---|---|---|---|
| `AGENTS.md` | Root-Regeln sind aktuell: aktive Specs zuerst, Run-Log-Pflicht, Runtime-/Archive-Grenzen, Teaching-Trennung und Repo-Hygiene klar. | OK | niedrig | Behalten. |
| `app/AGENTS.md` | Konsistent mit Root: `app/` als einzige Source, Access-Grenzen, UI-Browserpflicht und Teaching-Trennung klar. | OK | niedrig | Behalten. |
| `docs/AGENTS.md` | Klare Trennung Spec/ADR/Runbook/Run-Log; historische Run-Logs nicht normativ. | OK | niedrig | Behalten. |
| `scripts/AGENTS.md` | Intake-/Runtime-Grenzen und kein Teaching-Touch im Intake konsistent. | OK | niedrig | Behalten. |
| `scripts/research_data_intake/AGENTS.md` | Intake-spezifische Regeln passen zum aktuellen Runtime-only-/Archive-Vertrag. | OK | niedrig | Behalten. |
| `.github/instructions/repo.instructions.md` | Deckt aktuelle UI-, Research-, Intake- und Run-Log-Regeln ab. Keine alten Sample-/Icon-Regeln gefunden. | OK | niedrig | Behalten. |
| `.github/pull_request_template.md` | Verlangt Tests, Spec-Prüfung, scoped AGENTS und `docs/agent-runs/`. | OK | niedrig | Behalten. |
| `.github/workflows/ci.yml` | CI läuft `ruff`, `compileall`, Governance-Checks und ausgewählte Pytests. Neue Runtime-/Security-Härtungstests wie `test_runtime_config.py` sind lokal vorhanden, aber nicht sichtbar im CI-Workflow. | unklar | mittel | CI-Scope separat prüfen und sicherheitsnahe Regressionen aufnehmen, ohne redaktionell fragile Checks zu erzwingen. |
| `.github/CODEOWNERS` | Absichtlich comment-only Scaffold mit TODO-Ownern. | Cleanup-Kandidat | mittel vor Review-Enforcement | Vor Required Reviews echte Handles/Teams eintragen oder Datei bewusst als Scaffold dokumentieren. |
| `.github/SECURITY.md` | Enthält `Security contact: TODO before public deployment`. | veraltet | mittel/P2 | Vor öffentlicher Prod-Freigabe echten Meldekanal eintragen. |
| `README.md` | Kurze Orientierung ist konsistent, aber die Binding-Source-Liste nennt nur drei Specs und nicht `research-capabilities.md`. | unklar | niedrig | Bei nächster Governance-Runde Binding-Liste an Root-AGENTS angleichen. |
| `docs/spec/platform-data-files.md` | Aktuell für Access Request, Mailtransport, Google Fonts, Icon-Dualweg, `memory://` nur Dev/Test, mobile Footer-Regel und Intake-Regeln. | OK | niedrig | Behalten. |
| `docs/spec/research-access.md` | Aktuell für Research-Routing, `/access-request` ohne `mailto`, Player/Comparison/Speakers-Regeln. | OK | niedrig | Behalten. |
| `docs/spec/research-capabilities.md` | Als aktive Capability-Quelle eingebunden; keine offensichtliche Drift im Audit-Scope gefunden. | OK | niedrig | Behalten. |
| `docs/spec/intake-workbook.md` | Deprecated-Felder sind als Übergangs-/Kompatibilitätshinweise markiert, nicht als konkurrierende Regel. | OK | niedrig | Behalten. |
| `docs/runbooks/local-dev-start.md` | Aktueller Dev-Start über `scripts/dev-start.ps1`, Port-Fallback und Migrationen dokumentiert. | OK | niedrig | Behalten. |
| `docs/runbooks/ui-change-workflow.md` | Aktuelle Browser-/Screenshot-Pflicht und PM-Referenzflächen dokumentiert. | OK | niedrig | Behalten. |
| `docs/runbooks/research-intake-working-pipeline.md` | Nicht im Detail neu validiert, aber Governance-Rahmen passt zu aktuellen Intake-Regeln. | OK | niedrig | Bei nächstem Intake-Run gegen aktuelle CLI prüfen. |
| `docs/plans/**` | Enthält historische Planungsstände; nicht als aktive Quelle gewertet. | OK | niedrig | Nur bereinigen, wenn konkrete Pläne als aktiv missverstanden werden. |
| `app/src/app/auth/services.py` | `build_access_request_mailto()` existiert noch, wird in produktiven Templates/Routen nicht referenziert. | Cleanup-Kandidat | niedrig bis mittel | Nach Referenztest als Legacy-Helfer entfernen oder als bewusst inaktiv markieren. |

## 4. MD3-Reste

| Pfad | Rest | Aktiv? | Nutzung | Empfehlung |
|---|---|---:|---:|---|
| `app/templates/base.html` | Globale Links auf `css/md3/tokens.css`, `typography.css`, `layout.css` und viele `css/md3/components/*.css`. | ja | ja | später migrieren |
| `app/templates/base.html` | `md3-content-wrapper` und `md3-footer` als aktive Layout-/Footer-Klassen. | ja | ja | später migrieren |
| `app/static/css/md3/tokens.css` | MD3-/`--md-sys-*` Token-Schicht bleibt global geladen, während PM-Tokens in `00_tokens.css` kanonisch sind. | ja | ja | später migrieren |
| `app/static/css/md3/layout.css` | Bootstrap-artige Utilities mit vielen `!important` und alten max-width-Werten. | ja | unklar/teilweise | später migrieren |
| `app/static/css/md3/components/mobile-responsive.css` | Globale mobile Overrides, Map-Z-Index-Regeln und `!important`-Korrekturen. | ja | unklar/teilweise | nicht anfassen ohne Viewport-QA |
| `app/static/css/md3/components/navbar.css` | Alte `.md3-nav*`/Mobile-Menu-Familien, global geladen. Produktive Topbar nutzt `promat-topbar`. | ja | unklar | später migrieren |
| `app/static/css/md3/components/navigation-drawer.css` | Alte `.md3-navigation-drawer*`-Familie plus aktuelle Dialog-/Drawer-Nähe. | ja | unklar/parallel | nicht anfassen ohne Drawer-QA |
| `app/static/css/md3/components/top-app-bar.css` | Alte `.md3-top-app-bar*`-/Theme-Toggle-Reste, global geladen. Produktive Topbar nutzt `promat-topbar`. | ja | unklar/parallel | später migrieren |
| `app/static/css/md3/components/buttons.css` | MD3-Button-Familie global geladen; produktive PM-Actions in `30_components.css`. | ja | unklar | später migrieren |
| `app/static/css/md3/components/alerts.css` und `snackbar.css` | MD3 Alert/Snackbar noch durch `app/static/js/md3/alert-utils.js` und `modules/core/snackbar.js` genutzt. | ja | ja | behalten bis Ersatz steht |
| `app/static/js/modules/core/entry.js` -> `main.js` -> `modules/navigation/index.js` | Globaler Import des "MD3 Navigation Module". | ja | ja | später migrieren |
| `app/static/js/modules/navigation/drawer.js` | Nutzt aktuelle Dialog-IDs, enthält aber alte `.md3-navigation-drawer__trigger`-Submenu-Selektoren. | ja | teilweise/unklar | später migrieren |
| `app/static/js/modules/navigation/turbo-integration.js` | Alte `.md3-navigation-drawer*`-Aktivierungslogik neben aktueller PM-Shell. | ja | unklar | später migrieren |
| `app/static/js/navigation-drawer-init.js` | Global geladen, enthält nur Kommentar. | ja | nein | sicher entfernbar nach Load-Check |
| `app/static/js/nav_proyecto.js` | Nicht global referenziert, enthält alte `.md3-nav*`, Bottomsheet und Subdrawer-Logik. | nein | unklar/tot wirkend | sicher entfernbar nach Route-Suche |
| `app/static/css/md3/components/auth.css` | Nicht in `base.html` oder Templates referenziert. | nein | nein gefunden | sicher entfernbar nach finalem rg/visual check |
| `app/static/css/md3/components/forms.css` | Nicht referenziert, alte Form-/Filterregeln. | nein | nein gefunden | sicher entfernbar nach finalem rg/visual check |
| `app/static/css/md3/components/chips.css` | Nicht referenziert. | nein | nein gefunden | sicher entfernbar nach finalem rg/visual check |
| `app/static/css/md3/components/index.css` | Nicht referenziert. | nein | nein gefunden | sicher entfernbar nach finalem rg/visual check |
| `app/static/css/md3/components/menu.css` | Nicht referenziert. | nein | nein gefunden | sicher entfernbar nach finalem rg/visual check |
| `app/static/css/md3/components/motion.css` | Nicht referenziert. | nein | nein gefunden | unklar, erst Motion-Abhängigkeiten prüfen |
| `app/static/css/md3/components/player.css` | Nicht referenziert; produktiver Player nutzt `pm-player-*` in `20_layout.css`/`30_components.css`/`40_cards.css`. | nein | nein gefunden | sicher entfernbar nach Player-QA |
| `app/static/css/md3/components/status-banner.css` | Nicht referenziert; nur Kommentar in Topbar-CSS verweist darauf. | nein | nein gefunden | sicher entfernbar nach finalem rg |
| `app/templates/auth/*.html` | Erweitern `_md3_skeletons/auth_login_skeleton.html`, Inhalt selbst nutzt PM-Auth-Familien. | ja | ja | Skeleton später umbenennen, nicht funktional dringend |

## 5. Token-/CSS-Konsistenz

| Pfad | Befund | Token-/CSS-Risiko | Empfehlung | Priorität |
|---|---|---|---|---|
| `app/static/css/00_tokens.css` | PM/PROMAT-Tokens für Layout, Touch Targets, Icons, Topbar, Drawer, Research und Teaching sind kanonisch und breit genutzt. | niedrig | Behalten und als Zielsystem nutzen. | P3 |
| `app/static/css/md3/tokens.css` | Globale MD3-Tokenlage existiert parallel; Kommentar nennt `--md-sys-*` noch kanonisch, während Projekt-Spec inzwischen PM/PROMAT-Konventionen priorisiert. | mittel | Token-Rollen später entflechten und aktive PM-Tokens dokumentiert bevorzugen. | P3 |
| `app/static/css/md3/layout.css` | Viele Utility-Klassen mit `!important` (`.m-*`, `.d-flex`, `.w-100`) können PM-Komponenten unerwartet übersteuern. | mittel | Usage suchen, dann ungenutzte Utilities entfernen oder auf PM-Utilities begrenzen. | P3 |
| `app/static/css/md3/components/mobile-responsive.css` | Breite mobile Overrides mit `!important` und globalen Klassen können echte Overflow-Probleme maskieren. | mittel | Erst visuelle QA, dann gezielte Reduktion. | P2 |
| `app/static/css/30_components.css` | Produktive PM-Komponenten sind tokenisiert, aber Datei ist sehr groß und bündelt Shell, Auth, Research, Teaching, Admin. | mittel | Nicht umbauen vor Prod; später nach Komponentenfamilien schneiden. | später |
| `app/static/css/30_components.css` | Einige harte Werte und Spezialbreakpoints neben Tokens, z. B. Admin/Comparison/Player-Mindestbreiten. | mittel | Nur problematische mobile Stellen gezielt tokenisieren. | P3 |
| `app/static/css/30_components.css` | Touch-Ziel-Regel wird positiv umgesetzt: viele Controls nutzen `--pm-touch-target-min`. | niedrig | Behalten. | P3 |
| `app/templates` und `app/src/app` | `rg "style="` in produktiven Templates/App-Code ohne Treffer. | niedrig | Behalten. | P3 |
| `app/static/css/md3/components/top-app-bar.css` | Alte Topbar-Regeln parallel zur aktuellen `promat-topbar`-Familie. | mittel | Erst Load-/Visual-Abhängigkeit klären, dann reduzieren. | P3 |
| `app/static/css/md3/components/navigation-drawer.css` | Alte Drawer-Regeln parallel zur aktuellen `promat-panel`-Familie. | mittel | Nur zusammen mit Drawer-Viewport-QA anfassen. | P2 |

## 6. Mobile / Responsive

| Bereich | Status | Evidenz | Empfehlung |
|---|---|---|---|
| Public Home/Projektseiten | OK | `base.html`, `promat_page.html`, PM content containers und mobile shell tokens vorhanden; keine aktiven Sample-Links gefunden. | Visuelle Smoke-QA bei 375/390/768 vor Prod. |
| Auth/Login/Access Request | OK | Auth-Templates nutzen `pm-auth-*`, responsive Form-Grid und PM-Buttons; keine `mailto`-Journey in Templates. | Browser-QA für Login, Fehlerzustand und Access-Request-Erfolg ergänzen. |
| Research Root | OK | Access-Spec und PM-Shell trennen public root und protected Workbench; drawer/sidebar generisch. | Viewport-QA für signed-out und signed-in Zustand. |
| Research Speaker/List/Card-Seiten | Warnung | Cards und Table-View haben responsive Strategien (`pm-research-mobile-filters`, Table-Wrap, Card Grid). Table-View bleibt dichter. | 375/390 px Table- und Card-View prüfen. |
| Research Player | Warnung | Player nutzt mobile Layout-Regeln, Touch-Targets und `mobileMinWidth: 900`; Comparison-Panel wird mobil ausgeblendet. | Visuelle QA für wordlist/text/interview Player, Timeline und Popover. |
| Research Comparison | Warnung | Matrix/Toolbar haben Scroll-/Min-width-Strategien, aber dreispaltige Auswahl und Matrix sind dicht. | Vor Prod explizite mobile/tablet QA; falls nötig horizontales Scroll-Verhalten dokumentieren. |
| Teaching Root | OK | Teaching-Overview und Topic-Grids haben responsive PM-Regeln; Mini-Player und Audio-Blocks sind tokenisiert. | Smoke-QA für Topic mit Audio und Datawrapper. |
| Teaching Topic Pages | OK | Audio-Example/Contrast-Blöcke stacken mobil laut Spec/CSS; keine Content-Änderungen im Audit. | Mobile QA mit langen Labels und Datawrapper. |
| Navigation Header / Top App Bar | Warnung | Aktuelle `promat-topbar` hat mobile Breakpoints 979/767/430/360 und 44px-Ziele; Desktop-Nav wird mobil versteckt. | 360/375 px visuell prüfen, besonders Brand + Drawer-Button + Sprachwechsel. |
| Navigation Drawer / Mobile Menu | Warnung | Dialog-basierter Drawer mit `showModal()`, inert, Scroll-Lock und Swipe-Gestures; JS enthält aber alte MD3-Submenu-Selektoren. | Drawer-QA mit Öffnen/Schließen, Fokus, ESC, Link-Klick, Swipe. |
| Footer | OK | Spec dokumentiert kompakten mobilen Footer; `md3-footer` noch aktiv, Footer-CSS global geladen. | Mobile Footer visuell prüfen, MD3-Klasse später migrieren. |
| Admin-Login und einfache Admin-Übersichten | desktop-only akzeptiert | Admin-Tabelle hat Scroll-Hint und mobile Desktop-Spalten-Ausblendung; Admin ist Spezialfläche. | Desktop-first zulassen, aber Mindestbreiten/Scroll-Hinweis im Browser prüfen. |
| Workbench-/Admin-Spezialflächen | desktop-only akzeptiert | Research `comparison`/`phenomena` sind dichte Workbenches; mobile Regeln existieren, aber Funktionsdichte bleibt hoch. | Keine Blockade, aber explizit als Workbench-QA-Scope behandeln. |
| Modals/Dialogs | unklar, visuelle QA nötig | Dialog-CSS hat `max-width`/mobile Regeln; Drawer und Player Reference Popover nutzen Dialoge. | Dialoge bei 375/390 px prüfen. |
| Tabellen allgemein | Warnung | Research/Admin-Tabellen nutzen Wraps, horizontales Scrollen oder mobile Spaltenstrategie. | Keine pauschale Umstellung; pro Tabelle visuell validieren. |

## 7. Navigation

- Desktop: `partials/_top_app_bar.html` rendert Hauptbereiche Projekt, Research, Teaching; `partials/_navigation_drawer.html` rendert Kontextnavigation. Pfade sind lokalisiert und aus `url_for()` gebaut.
- Mobile: Topbar versteckt Desktop-Navigation und Standard-Panel unter 980 px; Drawer-Button öffnet `navigation-drawer-modal`.
- Drawer: Dialog-basierter Drawer mit `aria-controls`, `aria-expanded`, `showModal()`, inert auf `main`, Scroll-Lock und Fokus auf initialen Link. Risiko: alte `.md3-navigation-drawer__*`-Submenu-Logik im gleichen Modul ist aktuell parallel/unklar.
- Sprachwechsel: `_ui_lang_switch.html` ist in Topbar eingebunden; mobile CSS reduziert Breiten bei 430/360 px. Visuelle QA nötig wegen langer Kombination aus Brand und Sprachwechsel.
- Account/Admin: Account-Menü ist in Topbar und Drawer erreichbar; Admin-Link wird rollenbasiert gerendert.
- Backlinks/CTAs: Shared PM-Interaction- und Nav-Pill-Familien werden verwendet; keine aktiven `sample`-Links gefunden.
- Tote/Legacy-Links: `rg "sample"` in produktiven App-Pfaden ohne Treffer. `nav_proyecto.js` wirkt nicht referenziert und ist ein Legacy-Kandidat.
- Icons/Labels: Aktiver Dualweg entspricht Spec: `pm-icon-mask` für Shell/Player/Utility, `material-symbols-rounded` für inline/textnahe Aktionen. Keine Font-Awesome- oder Bootstrap-Icon-Nutzung in produktiven App-Pfaden gefunden.
- Ohne Hover: Drawer, Topbar-Buttons, Nav-Pills und Account-Menü sind button-/link-basiert; Touch-Ziel-Tokens sind vorhanden.

## 8. Priorisierte Befunde

### P2: vor Prod sinnvoll

- `.github/SECURITY.md`: echten Security-Kontakt statt TODO eintragen.
- Mobile visuelle QA für 360/375/390/768 px auf Topbar, Drawer, Auth, Research Speakers, Player, Comparison, Teaching Topic, Admin Users.
- `app/static/css/md3/components/mobile-responsive.css` und `navigation-drawer.css` nicht löschen, aber als Risikoquellen im Mobile-QA-Pass beobachten.
- CI prüfen: sicherheitsnahe Runtime-/Config-Tests wie `test_runtime_config.py` und relevante CSP/Access-Request-Tests sollten in CI sichtbar sein, wenn die Dateien final im Tree bleiben.

### P3: Wartbarkeit

- `.github/CODEOWNERS` vor Review-Enforcement mit echten Ownern füllen.
- `README.md` Binding-Source-Liste an Root-AGENTS angleichen.
- Dead-looking `build_access_request_mailto()` entfernen oder als inaktive Legacy-Kompatibilität klären.
- Nicht referenzierte MD3-Dateien nach finalem rg und Browser-QA entfernen.
- MD3-Navigation-Modul schrittweise auf `promat-*`/`pm-*` umbenennen.
- `!important`-Utilities in MD3-Layout und mobilen Overrides gezielt reduzieren.

### später: Design-Politur

- `30_components.css` nach Komponentenfamilien schneiden.
- MD3-Token- und PM-Token-Schichten entflechten.
- `md3-content-wrapper` und `md3-footer` auf PM/PROMAT-Namen migrieren.
- Auth-Skeleton-Dateiname `_md3_skeletons/auth_login_skeleton.html` umbenennen, nachdem Referenzen und Screenshots stabil sind.

## 9. Folgeprompts

### Governance Cleanup

Führe einen engen Governance-Cleanup durch. Scope: `.github/SECURITY.md`, `.github/CODEOWNERS`, `README.md`, `.github/workflows/ci.yml` und aktive Instruction-Dateien. Keine Produktcode-Änderungen außer CI/Testlisten, keine UI-Änderungen. Sichere Befunde umsetzen: echten Security-Kontakt eintragen, CODEOWNERS-Status klären, README-Binding-Quelle an Root-AGENTS angleichen, CI-Scope für bestehende sicherheitsnahe Tests prüfen. Unklare Befunde separat reporten. Tests: relevante Governance-Checks, `pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q`. Abschlussbericht unter `docs/agent-runs/YYYY-MM-DD_governance-cleanup.md`.

### MD3 Legacy Reduction

Reduziere nur sicher unreferenzierte MD3-Reste. Vor jedem Delete `rg` gegen `app/templates`, `app/static/js`, `app/src/app`, `.github`, `docs/spec`, `docs/runbooks` ausführen. Keine optischen Redesigns, keine globale Shell-Migration. Sichere Kandidaten prüfen: nicht geladene `css/md3/components/auth.css`, `forms.css`, `chips.css`, `index.css`, `menu.css`, `player.css`, `status-banner.css`, `navigation-drawer-init.js`, ggf. `nav_proyecto.js`. Unklare aktive CSS/JS wie `navigation-drawer.css`, `top-app-bar.css`, `mobile-responsive.css`, Snackbar/Alert behalten. Tests und Browser-QA für Auth, Topbar/Drawer, Player. Abschlussbericht unter `docs/agent-runs/YYYY-MM-DD_md3-legacy-reduction.md`.

### Responsive Mobile Hardening

Führe eine visuelle mobile QA und nur gezielte Hardening-Fixes aus. Viewports: 360, 375, 390, 768, 1024, 1440. Routen: Home/Projekt, Login, Access Request, Research Root, Speakers Card/Table, Player wordlist/text/interview, Comparison, Teaching Root, Teaching Topic mit Audio/Datawrapper, Admin Users. Keine Redesigns, keine MD3-Bereinigung. Sichere mobile Bugs fixen, desktop-first Admin/Workbench nur mit sauberem Hinweis/Scrollstrategie behandeln. Tests: Navigation/Player/Auth/Research-Sessions plus Screenshot-Dokumentation. Abschlussbericht unter `docs/agent-runs/YYYY-MM-DD_responsive-mobile-hardening.md`.

### CSS Token Consistency Cleanup

Führe einen kleinen CSS-Token-Cleanup ohne visuelles Redesign aus. Scope: harte Werte und `!important` nur dort reduzieren, wo ein bestehender PM-Token direkt passt und Browser-Parität leicht belegbar ist. Keine MD3-Großmigration, keine Datei-Neustruktur. Sichere Befunde und unklare Befunde getrennt behandeln. Tests: relevante UI-/Research-/Auth-Regressionen plus Browser-Screenshots auf betroffenen und mindestens einer unbetroffenen Route. Abschlussbericht unter `docs/agent-runs/YYYY-MM-DD_css-token-consistency-cleanup.md`.

## 10. Tests/Checks

Ausgeführt:

- `git status --short`
- `git diff --stat`
- `git status --short -- content content\teaching public\teaching`
- `rg "sample|Font Awesome|font-awesome|Bootstrap Icons|bootstrap-icons|Werkzeug|memory://|mailto|md3|md3-|material-symbols-outlined|style=|!important" ...`
- `rg "drawer|navigation|top-app-bar|mobile|responsive|breakpoint|overflow|media query|@media|min-width|max-width" app/templates app/static app/src/app`
- `rg "css/md3|js/md3|md3/|md3-" app/templates app/static/js app/src/app -n`
- `rg "style=" app/templates app/src/app -n`
- `rg "!important" app/static/css -n`
- `rg "sample" app/templates app/static app/src/app docs/spec docs/runbooks .github -n`
- `.venv\Scripts\python.exe -m compileall app -q` -> bestanden.
- `.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q` -> 66 passed.
- `.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -q` -> 201 passed.
- `.venv\Scripts\python.exe -m pytest app/tests -q -k "navigation or mobile or drawer or responsive or csp or security_headers or access_request or player"` -> 121 passed, 353 deselected, 28 Testmodus-Warnungen zum In-Memory-Rate-Limiter.

Nicht ausgeführt:

- Browser-/Screenshot-QA: nicht gestartet, weil der Auftrag read-only war und keine Dev-Server-/Browser-Aktionen mit potenziellen Seiteneffekten erzwungen werden sollten. Statische QA benennt konkrete spätere Viewport-Routen.
- Vollständiger `pytest app/tests -q`: nicht erforderlich laut Auftrag; der erlaubte gefilterte Lauf wurde ausgeführt.
- Auto-Fix, Formatter, Migrationen, Seeds, Font-Downloads, externe Mailtests, Deploys: ausdrücklich nicht ausgeführt.

## 11. No-Go

- Keine Produktcode-, Template-, CSS- oder JS-Fixes angewendet.
- Keine Design-System-Migration durchgeführt.
- Keine MD3-Entfernung durchgeführt.
- Keine Mobile-Fixes durchgeführt.
- Kein Prod-Paket gebaut.
- Kein Serverkontakt durchgeführt.
- `content/`, `content/teaching/` und `public/teaching/` blieben laut `git status --short -- content content\teaching public\teaching` unangetastet.
- Der Workspace war bereits vor diesem Audit dirty; dieser Run hat nur den geforderten Auditbericht angelegt.
