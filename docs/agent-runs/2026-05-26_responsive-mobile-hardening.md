# Responsive Mobile Hardening

## 1. Scope

Geprüft wurden Public/Auth/Research/Teaching, Navigation/Topbar/Drawer, Research Player, Comparison, Teaching Audio/Datawrapper und Admin Users in echten Chromium-Viewports.

Umgesetzt wurde nur ein belegter risikoarmer Hardening-Fix: globale Navigation-Initialisierung bleibt auf Seiten ohne App-Bar oder Drawer jetzt stiller No-op statt Console-Error/Warnung.

Ausdrücklich nicht umgesetzt wurden Design-System-Migration, MD3-Bereinigung, breite CSS-Bereinigung, Google-Fonts-Arbeit, Icon-Migration, Content-Änderungen, Teaching-Inhaltsänderungen, P0/P1-Refactors und Admin-/Workbench-Mobile-Neugestaltung.

## 2. Kurzfazit

- Public/Auth mobile Status: OK. Login und Access Request sind bei 360/375/390 px nutzbar, Fehlermeldungen sind sichtbar, kein horizontaler Page-Overflow.
- Research mobile Status: OK mit Workbench-Hinweis. Speakers, Profile, Player wordlist/text/interview und Comparison rendern ohne Page-Overflow. Dichte Workbench-Flächen bleiben horizontal/vertikal scroll-orientiert.
- Teaching mobile Status: OK. Topic mit Audio-Blöcken und Datawrapper rendert ohne Page-Overflow; Audio-Controls bleiben bedienbar.
- Navigation/Drawer Status: OK. Topbar passt bei 360/375/390 px, Drawer öffnet, sperrt Scroll, schließt per ESC und nach Link-Klick.
- Admin/Workbench Status: desktop-first akzeptiert. Admin Users zeigt eine mobile Scrollstrategie und einen Hinweis, Tabelle sprengt nicht die Seite.
- Mobile-seitig kein Prod-Blocker gefunden.
- Wichtigster Restpunkt: spätere visuelle QA kann nach MD3 Legacy Reduction erneut stichprobenartig laufen, weil globale MD3-CSS weiterhin aktiv ist.

## 3. Viewport-QA-Matrix

Screenshot-/QA-Artefakte:

- `tmp/ui-qa/2026-05-26-responsive-mobile-hardening/mobile-qa-results.json`
- `tmp/ui-qa/2026-05-26-responsive-mobile-hardening/mobile-qa-overflow-summary.json`
- `tmp/ui-qa/2026-05-26-responsive-mobile-hardening/focused-section-results.json`
- `tmp/ui-qa/2026-05-26-responsive-mobile-hardening/screenshots/`

Insgesamt wurden 96 Route/Viewport-Kombinationen plus fokussierte Abschnitts-Screenshots erfasst. `mobile-qa-overflow-summary.json` ist leer.

| Route/Flow | 360 | 375/390 | 768 | 1024 | 1440 | Ergebnis |
|---|---|---|---|---|---|---|
| Public Home `/de` | OK | OK | OK | OK | OK | 200, kein Page-Overflow |
| Projektseite `/de/project/about` | OK | OK | OK | OK | OK | 200, kein Page-Overflow |
| Research Root signed-out | OK | OK | OK | OK | OK | 200, locked routes sichtbar ohne Body-Overflow |
| Login | OK | OK | OK | OK | OK | Form nutzbar, Topbar stabil |
| Access Request | OK | OK | OK | OK | OK | Form nutzbar, Validation sichtbar |
| Access Request Validation | OK | OK | nicht separat | nicht separat | nicht separat | 7 Feldfehler + Summary sichtbar |
| Research Root signed-in | OK | OK | OK | OK | OK | 200, Navigation stabil |
| Speakers Card View | OK | OK | OK | OK | OK | Filter und Cards lesbar |
| Speakers Table View | OK | OK | OK | OK | OK | Scroll-/Tabellenstrategie ohne Page-Overflow |
| Speaker Detail | OK | OK | OK | OK | OK | Detailkarten lesbar |
| Player Wordlist | OK | OK | OK | OK | OK | Controls/Liste separat geprüft |
| Player Text | OK | OK | OK | OK | OK | Controls stabil |
| Player Interview | OK | OK | OK | OK | OK | Transcript/Popover separat geprüft |
| Player Controls/List | OK | OK | OK | nicht separat | nicht separat | Timeline, Volume, Speed und Liste bedienbar |
| Comparison | OK | OK | OK | OK | OK | Workbench scrollt/stackt ohne Page-Overflow |
| Comparison Matrix/Toolbar | OK | OK | OK | nicht separat | nicht separat | Matrix-Panel und Toolbar sichtbar; 0-Items-State sauber |
| Teaching Root | OK | OK | OK | OK | OK | Topic Cards lesbar |
| Teaching Topic Audio/Datawrapper | OK | OK | OK | OK | OK | Audio und Datawrapper separat geprüft |
| Admin Users | OK | OK | OK | OK | OK | Desktop-first, Tabelle mit Scrollstrategie |
| Mobile Drawer signed-out | OK | OK | nicht nötig | nicht nötig | nicht nötig | Open, Scroll-Lock, ESC, Link-Klick OK |
| Mobile Drawer signed-in/admin | nicht separat | OK | nicht separat | nicht nötig | nicht nötig | Konto/Admin-Links im Drawer erreichbar |

Repräsentative Screenshots:

- `screenshots/360_login.jpg`
- `screenshots/360_drawer-open.jpg`
- `screenshots/390_drawer-open-signed-in-admin.jpg`
- `screenshots/360_access-request-validation.jpg`
- `screenshots/360_player-controls-360.jpg`
- `screenshots/390_player-interview-popover.jpg`
- `screenshots/360_comparison-matrix-360.jpg`
- `screenshots/360_teaching-audio-360.jpg`
- `screenshots/360_teaching-datawrapper-360.jpg`
- `screenshots/360_admin-table-360.jpg`

## 4. Gefundene Probleme

### RMH-1

- Route/Flow: Seiten ohne vollständige Shell/App-Bar, insbesondere Landing/Public-Varianten.
- Viewport: alle geprüften Viewports.
- Evidenz/Screenshot: `mobile-qa-results.json` vor Fix enthielt Console-Meldungen `Navigation drawers not found` und `[TopAppBar] App Bar not found`.
- Ursache: Das globale Navigation-Modul initialisierte Drawer/App-Bar auch auf Seiten, die diese Elemente bewusst nicht rendern.
- Fix: `app/static/js/modules/navigation/drawer.js` und `app/static/js/modules/navigation/app-bar.js` geben bei fehlenden Shell-Elementen still zurück.
- Restrestrisiko: niedrig. Keine sichtbare Layoutänderung; vorhandene Drawer-Interaktion wurde nach dem Fix erneut geprüft.

Keine weiteren belegten Mobile-Bugs mit Layoutwirkung gefunden. Bekannte Restmeldungen aus der QA:

- Datawrapper/Browser-Warnung `Unrecognized feature: 'web-share'`, externes iframe-feature-Noise, keine Layoutwirkung.
- Erwartbare 400-Response beim absichtlich leeren Access-Request-Validation-Submit, Fehlermeldungen sichtbar.

## 5. Änderungen

| Datei | Kurzgrund |
|---|---|
| `app/static/js/modules/navigation/drawer.js` | Fehlender Drawer ist auf shell-losen Seiten ein legitimer Zustand; kein Console-Error mehr. |
| `app/static/js/modules/navigation/app-bar.js` | Fehlende App-Bar ist auf passenden Seiten ein legitimer Zustand; keine Console-Warnung mehr. |
| `tmp/ui-qa/2026-05-26-responsive-mobile-hardening/mobile_qa.py` | QA-Hilfsskript für Viewport-Matrix und Drawer/Form/Popover-Checks. |
| `tmp/ui-qa/2026-05-26-responsive-mobile-hardening/focused_sections.py` | QA-Hilfsskript für tiefer liegende Player/Comparison/Teaching/Admin-Abschnitte. |
| `tmp/ui-qa/2026-05-26-responsive-mobile-hardening/screenshots/` | Screenshot-Belege. |

## 6. Navigation/Drawer

- Topbar: Brand passt bei 360/375/390 px; Drawer-Button bleibt 44 px groß; Sprachwechsel bleibt erreichbar.
- Drawer: öffnet per Button, setzt `body`/`html` overflow auf `hidden`, schließt per ESC und nach Link-Klick.
- Sprachwechsel: kompakte `DE | EN`-Darstellung bleibt ohne Überlappung sichtbar.
- Account/Admin: Desktop-Account-Menü ist auf Mobile bewusst nicht in der Topbar sichtbar; Konto/Admin/Logout sind im mobilen Drawer erreichbar. Screenshot: `390_drawer-open-signed-in-admin.jpg`.
- Backlinks/CTAs: Login, Player, Teaching und Research-Backlinks bleiben sichtbar und bedienbar.
- Touch-Ziele: Topbar, Drawer-Links, Auth-Buttons, Player-Controls und Admin-Actions sind in den Screenshots touch-tauglich.

## 7. Research Player/Comparison

- Player wordlist/text/interview: alle drei Routen 200 und ohne Page-Overflow bei 360/375/390/768/1024/1440.
- Timeline/Controls: `360_player-controls-360.jpg` zeigt Play, Timeline, Volume und Speed gestapelt und bedienbar.
- Listen/Transcript: `360_player-list-360.jpg` und `360_player-interview-transcript-360.jpg` bleiben lesbar.
- Popover/Dialoge: `390_player-interview-popover.jpg` zeigt keine Viewport-Sprengung.
- Comparison: Session-Auswahl stackt mobil; Material- und Matrix-Bereiche bleiben ohne Page-Overflow.
- Matrix/Toolbar: `360_comparison-matrix-360.jpg` zeigt die dichte Workbench als mobile Scroll-/Stack-Strategie. Bei der QA-Auswahl ergab sich ein sauberer 0-Items-State, kein kaputter Zustand.

## 8. Teaching Audio/Datawrapper

- Audio-Blöcke: `360_teaching-audio-360.jpg` zeigt gestapelte Audio-Cards mit bedienbaren Mini-Playern.
- Mini-Player: Controls bleiben sichtbar; keine horizontale Sprengung.
- Datawrapper: `360_teaching-datawrapper-360.jpg` zeigt iframe/Embed in der Content-Spalte ohne Page-Overflow.
- Lange Labels: Topic-Titel und Audio-Karten brechen sauber.

## 9. Admin/Workbench

- Admin Users ist weiterhin desktop-first, aber mobil nicht kaputt.
- Die Toolbar stackt bei 360 px, Suchfeld und Hauptaktionen bleiben bedienbar.
- Die Tabelle zeigt einen mobilen Hinweis und bleibt horizontal/innerhalb des Tabellenbereichs scroll-orientiert.
- Keine Mobile-Neugestaltung der Admin-Tabelle vorgenommen.

## 10. Tests und Checks

Ausgeführt:

```text
.venv\Scripts\python.exe tmp\ui-qa\2026-05-26-responsive-mobile-hardening\mobile_qa.py
```

Ergebnis: 96 Route/Viewport-Checks, 0 Overflow-Findings.

```text
.venv\Scripts\python.exe tmp\ui-qa\2026-05-26-responsive-mobile-hardening\focused_sections.py
```

Ergebnis: fokussierte Abschnitts-Screenshots für Player, Comparison, Teaching und Admin bei 360/390/768; alle gemessenen Abschnitte `pageOverflow: 0`.

```text
.venv\Scripts\python.exe -m compileall app -q
```

Ergebnis: bestanden.

```text
.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q
```

Ergebnis: 66 passed.

```text
.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -q
```

Ergebnis: 201 passed.

```text
.venv\Scripts\python.exe -m pytest app/tests -q -k "navigation or mobile or drawer or responsive or csp or security_headers or access_request or player"
```

Ergebnis: 121 passed, 353 deselected. Es gab 28 bekannte Testmodus-Warnungen von Flask-Limiter zur In-Memory-Storage-Nutzung.

```text
node --test app/tests/js/*.test.mjs
```

Ergebnis: 7 passed.

Optional geprüft:

```text
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe .
```

Ergebnis: `ruff` und `mypy` sind in der lokalen `.venv` nicht verfügbar. Ein erster direkter PowerShell-Aufruf ohne `.\` wurde vom Shell-Resolver nicht ausgeführt; anschließend wurde die Verfügbarkeit sauber geprüft.

## 11. Nicht umgesetzt

- keine Design-System-Migration
- keine MD3-Bereinigung
- keine Content-Änderungen
- keine Teaching-Inhaltsänderungen
- keine Google-Fonts-Arbeit
- keine Icon-Migration
- keine Farbangleichung
- keine Admin/Workbench-Mobile-Neugestaltung
- keine breite CSS-Datei-Neustruktur
- keine echte externe Mailzustellung
- kein Prod-Paket
- kein Serverkontakt

## 12. Verbleibende nächste Schritte

- MD3 Legacy Reduction ist nach diesem Pass sicherer, sollte aber nach jedem Entfernen global geladener MD3-Dateien erneut Topbar/Drawer/Auth/Player/Teaching stichprobenartig visuell prüfen.
- CSS Token Consistency Cleanup bleibt sinnvoll, aber nicht als Prod-Blocker aus Mobile-Sicht.
- Falls Admin Users für kleine Smartphones produktiv intensiv genutzt werden soll, könnte später eine eigene Admin-Table-UX geplant werden; aktuell ist desktop-first mit Scrollstrategie ausreichend.
- Vor finalem Prod-Schnitt empfiehlt sich ein kurzer Smoke derselben Screenshot-Auswahl nach dem nächsten größeren CSS- oder MD3-Reduktionslauf.
