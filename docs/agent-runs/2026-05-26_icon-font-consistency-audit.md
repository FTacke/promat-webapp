# Icon + Font Consistency Audit

## 1. Scope

Geprueft wurde eng und read-only:

- produktive Icon-Nutzung in `app/templates`, `app/static/js`, `app/static/css`, `app/src/app`
- vorhandene zentrale Icon-Pfade, Makros, CSS-Klassen und Font-Assets
- visuelle Konsistenz von Library/Familie, Gewicht, Variation, Groesse, Line-Height, Alignment und Accessibility
- verbliebene Altlasten nach der Entfernung von Font Awesome und Bootstrap Icons
- produktive Google-Fonts-Nutzung, geladene Familien/Gewichte und CSP-Auswirkung
- Einordnung: Google Fonts extern belassen vs. lokal hosten

Ausdruecklich nicht geprueft oder umgesetzt:

- keine Fixes
- keine Icon-Migration
- keine CSS- oder Design-System-Migration
- keine Farbnormalisierung
- keine Font-Downloads
- keine P2-Security-Nacharbeit ausser Bewertung als Folgeempfehlung
- keine redaktionellen Content-Aenderungen
- keine Browser- oder Screenshot-Abnahme, weil dieser Run rein read-only und codebasiert blieb

## 2. Kurzfazit

- Ein einzelner globaler Icon-Kanon ist im Repo nicht vollstaendig durchgezogen.
- Produktiv aktiv sind vor allem zwei Wege:
  - `Material Symbols Rounded` als selbstgehosteter Font fuer textnahe Aktions-/Status-Icons
  - `pm-icon-mask` als tokenisiertes SVG-Mask-System fuer Shell-, Player-, Drawer- und Admonition-Icons
- Diese Zweiteilung ist technisch konsistent genug, aber nicht als explizite Konvention dokumentiert.
- Font Awesome und Bootstrap Icons sind produktiv entfernt; produktive Restnutzung wurde in Templates, CSS, JS und Tests nicht belegt.
- Es gibt kleine Altlasten und Sonderpfade:
  - ein isoliertes `material-symbols-outlined`-Snackbar-Modul ohne erkennbare Call-Sites
  - dynamische Inline-SVGs in `research-comparison.js`
  - typografische Pfeile und einzelne Buchstaben als Pseudo-Icons
- Google Fonts werden produktiv benoetigt: `Inter` fuer UI/Display und `Source Serif 4` fuer Lesetext/Karten.
- Fuer dieses Projekt ist lokales Hosting der Google Fonts die elegantere Zielrichtung, aber kein zwingender Sofortblocker, solange die externe Abhaengigkeit bewusst akzeptiert und dokumentiert bleibt.

## 3. Icon-Inventar

| System | Pfade | Nutzung | Status | Empfehlung |
|---|---|---|---|---|
| Material Symbols Rounded | `app/templates/base.html`, `app/static/css/md3/components/material-symbols-fallback.css`, `app/templates/partials/_pm_interactions.html`, Auth-/Account-/Teaching-Templates, `app/static/js/modules/core/snackbar.js`, `app/static/js/md3/alert-utils.js` | lokale Variable-Font fuer Inline-Aktions-, Status- und Formular-Icons | produktiv aktiv | kanonisch fuer inline, textnahe Interaktions- und Status-Icons |
| `pm-icon-mask` auf Basis tokenisierter SVG-Masks | `app/static/css/00_tokens.css`, `app/static/css/30_components.css`, `app/templates/partials/_top_app_bar.html`, `app/templates/partials/_navigation_drawer.html`, `app/templates/pages/research_player.html`, `app/templates/pages/research_comparison.html`, `app/templates/partials/_admonition.html`, `app/static/css/40_cards.css` | Shell-, Drawer-, Player-, Download-, Theme-, Lock- und Admonition-Icons als CSS-Masks | produktiv aktiv | legitim ergaenzend; faktisch kanonisch fuer Shell/Player/Chrome |
| Inline-SVGs aus JS | `app/static/js/pages/research-comparison.js` | geschlossene Menge dynamischer Icons fuer Save, Check, Play, Download, Add, Remove, Close | produktiv aktiv | bewusster Sonderfall; spaeter optional an Hauptweg angleichen |
| Typografische Pfeile/Symbole | `app/templates/partials/_pm_interactions.html`, `app/templates/pages/research_player.html`, `app/templates/pages/research_comparison.html` | `→`, `←`, `i`, `/`, Klammern als UI-Symbole statt Icon-Komponente | produktiv aktiv | kleine Design-Schuld; nur bei gezielter Interaktions-Normalisierung anfassen |
| Material Symbols Outlined | `app/static/js/modules/auth/snackbar.js`, `app/static/css/md3/components/snackbar.css` | isolierter Close-Icon-Pfad in einem Auth-Expired-Snackbar-Modul | unklar, wahrscheinlich inaktiv | Altlast pruefen; falls Modul bleibt, an Rounded angleichen |
| Font Awesome | keine produktive Verwendung; nur negative Tests in `app/tests/test_auth_phase1.py`, historische QA-Snapshots unter `app/tmp/...`, historische Run-Logs | ehemals global geladen, jetzt entfernt | produktiv inaktiv | Altlasten ausserhalb historischer Artefakte nicht mehr prioritaer |
| Bootstrap Icons | keine produktive Verwendung; nur negative Tests in `app/tests/test_auth_phase1.py`, historische QA-Snapshots unter `app/tmp/...`, historische Run-Logs | ehemals global geladen, jetzt entfernt | produktiv inaktiv | Altlasten ausserhalb historischer Artefakte nicht mehr prioritaer |

## 4. Icon-Konsistenz

### Library/Familie

- `Material Symbols Rounded` ist der einzige belegte produktive Icon-Font mit lokaler Auslieferung.
- `pm-icon-mask` bildet eine zweite, ebenfalls klar zentralisierte Icon-Familie ueber SVG-Data-URIs und CSS-Masken.
- Es gibt damit keine wilde Mischung vieler Libraries, sondern zwei klar wiederkehrende aktive Familien plus einen kleinen Inline-SVG-Sonderfall.

### Style

- Material Symbols laufen produktiv ueberwiegend in der `Rounded`-Variante.
- Die Mask-Icons sind mehrheitlich einheitliche stroked SVG-Silhouetten mit `stroke-width="2"` in `app/static/css/00_tokens.css`; nur `play` und `pause` sind bewusst als gefuellte Formen definiert.
- Die Inline-SVGs in `app/static/js/pages/research-comparison.js` liegen stilistisch nahe an den Mask-Icons, aber nicht exakt gleich: `stroke-width` wechselt dort zwischen `1.8`, `1.9` und `2`, und `play` ist ebenfalls gefuellt.

### Weight, Grade, Optical Size

- Basis fuer `Material Symbols Rounded` in `app/static/css/md3/components/material-symbols-fallback.css`:
  - `FILL 0`
  - `wght 300`
  - `GRAD 0`
  - `opsz 24`
- Diese Basis ist innerhalb der klassischen PROMAT-Interaktionskomponenten konsistent.
- Es existieren einzelne Override-Pfade in alten MD3-CSS-Dateien, etwa fuer `md3-theme-toggle` und `md3-badge` in `app/static/css/md3/components/top-app-bar.css`, mit `FILL 1` und hoeherem Gewicht. In den produktiven Templates dieses Runs wurden dafuer aber keine Nutzungen gefunden. Das wirkt eher wie alter oder parallel liegender CSS-Bestand als wie aktiver Oberweg.

### Groesse, Line-Height, Alignment

- Material Symbols haben global `font-size: 24px`, `line-height: 1` und `vertical-align: middle`.
- Die produktiven PROMAT-Interaktionskomponenten uebersteuern die Groesse zentral ueber Tokens:
  - `--pm-action-button-icon-size-medium: 0.96rem`
  - `--pm-action-button-icon-size-small: 0.84rem`
  - `--pm-nav-pill-icon-size-medium: 0.82rem`
  - `--pm-nav-pill-icon-size-small: 0.76rem`
- `app/static/css/30_components.css` setzt fuer `pm-interaction__icon` und `pm-button__icon` durchgaengig `line-height: 1` bzw. icon-size-gebundene `font-size`.
- `pm-icon-mask` ist ebenfalls tokenisiert und nutzt die gemeinsamen Groessen `--pm-icon-size-sm/md/lg`, was Shell- und Player-Icons innerhalb ihrer Familie konsistent haelt.

### Accessibility

- Dekorative Icons sind in den inspizierten Templates ueberwiegend sauber mit `aria-hidden="true"` markiert.
- Icon-only Buttons im Player tragen konsistent `aria-label` und meist auch `title`, z. B. Download-/Play-Toggles in `app/templates/pages/research_player.html`.
- Die Shell-Buttons im Topbar-/Account-Bereich haben `aria-label` oder `sr-only`-Text.
- Admonition-Actions in `app/templates/partials/_admonition.html` sind mit `aria-label`, `title` und Live-Status-Element versehen.
- In diesem engen Audit wurden keine offensichtlich klickbaren, rein ikonischen Controls ohne Accessible Name belegt.

### Auffaellige Inkonsistenzen

| Pfad | Icon-Art | Inkonsistenz | Risiko | Empfehlung |
|---|---|---|---|---|
| `app/static/js/modules/auth/snackbar.js` + `app/static/css/md3/components/snackbar.css` | `material-symbols-outlined` | isolierte Outlined-Variante, waehrend sonst Rounded dominiert; ausserdem keine weitere Call-Site gefunden | Altlast / kleine Inkonsistenz | spaeter pruefen, ob Modul ueberhaupt noch gebraucht wird; falls ja, auf Rounded oder bestehenden Core-Snackbar-Pfad angleichen |
| `app/static/js/pages/research-comparison.js` | Inline-SVG | eigener dynamischer Sonderpfad mit leicht variierenden Stroke-Widths und gefuelltem `play` | Design-Schuld | nur bei gezielter Comparison-Normalisierung anfassen; kein Sofortproblem |
| `app/templates/partials/_pm_interactions.html` | typografische Pfeile | `→`/`←` statt Material- oder Mask-Icons | kleine Inkonsistenz | als bewusste Typografie lassen oder spaeter konsistent definieren; keine dringende Migration |
| `app/templates/pages/research_player.html`, `app/templates/pages/research_comparison.html` | typografisches `i` | einzelne Pseudo-Info-Icons als Buchstabe statt Icon-Komponente | kleine Inkonsistenz | nur bei gezielter Player/Comparison-Politur normalisieren |
| `app/static/css/md3/components/top-app-bar.css` | Material-Symbol-Overrides | FILL-/Weight-Overrides fuer MD3-Klassen ohne belegte Template-Nutzung in diesem Audit | Altlast / unklar | spaeter als toten oder parallelen CSS-Bestand verifizieren |

## 5. Icon-Altlasten

### Font-Awesome-Reste

- In produktiven Templates, produktivem CSS und produktivem JS wurde keine aktive `Font Awesome`-Nutzung belegt.
- `app/tests/test_auth_phase1.py` enthaelt nur die negative Regression, dass die alte CDN-Einbindung nicht mehr gerendert wird.
- Historische Erwahnungen existieren weiterhin in alten Run-Logs unter `docs/agent-runs/` und in QA-Artefakten unter `app/tmp/`, sind aber nicht produktiv relevant.

### Bootstrap-Icon-Reste

- In produktiven Templates, produktivem CSS und produktivem JS wurde keine aktive `Bootstrap Icons`-Nutzung belegt.
- Auch hier belegt `app/tests/test_auth_phase1.py` nur, dass die alte CDN-Einbindung nicht mehr gerendert wird.
- Verbleibende Erwaehnungen sitzen in historischen Run-Logs und QA-Artefakten, nicht in der aktiven App.

### Sonstige alte Icon-Pfade

- `material-symbols-outlined` im Auth-Snackbar-Modul ist die auffaelligste kleine Restinkonsistenz.
- Alte MD3-CSS-Pfade fuer Material-Symbol-Varianten wirken teilweise parallel oder ungenutzt, weil die aktuellen produktiven Templates ueberwiegend `promat-*`, `pm-*` und `material-symbols-rounded` verwenden.

## 6. Inline-SVGs und Sonderfälle

### CSS-gestuetzte SVG-Masks

- `app/static/css/00_tokens.css` definiert zahlreiche SVGs als `data:image/svg+xml`-Tokens.
- Diese werden ueber `pm-icon-mask` oder Admonition-Masken in `app/static/css/30_components.css` und `app/static/css/40_cards.css` gerendert.
- Das ist kein Wildwuchs, sondern ein zentralisierter Sonderweg.
- Bewertung: bewusstes Sonder-Icon-System, behalten.

### JS-generierte Inline-SVGs in Research Comparison

- `app/static/js/pages/research-comparison.js` erzeugt eine geschlossene, statische Menge an Icon-SVGs in `iconSvg(kind)`.
- Die SVG-Strings sind hartkodiert und nicht aus untrusted Daten zusammengesetzt; das ist im hier betrachteten Kontext technisch kontrolliert.
- Sie versorgen dynamisch erzeugte Buttons/Indikatoren in der Comparison-UI.
- Bewertung: bewusstes Sonder-Icon, spaeter optional in den kanonischen Weg ueberfuehren.

### Typografische Symbole

- `→`, `←` und einzelne `i`-Marker sind in mehreren UIs als visuelle Affordanzen vorhanden.
- Diese sind nicht automatisch problematisch, bilden aber keinen expliziten Teil einer dokumentierten Icon-Konvention.
- Bewertung: unkritische Design-Schuld, kein Sicherheits- oder Funktionsproblem.

## 7. Google Fonts

### Produktive Einbindung

- `app/templates/base.html` bindet exakt eine externe Google-Fonts-Stylesheet-URL ein:
  - `Inter:wght@400;500;600;700`
  - `Source Serif 4:wght@400;600;700`
- Zusaetzlich gibt es Preconnects zu `fonts.googleapis.com` und `fonts.gstatic.com`.

### Produktive Nutzung

- `app/static/css/00_tokens.css` setzt:
  - `--book-font-ui: "Inter", system-ui, ...`
  - `--book-font-body: "Source Serif 4", Georgia, ...`
- `app/static/css/10_typography.css` und weitere CSS-Dateien leiten daraus die produktive Typografie ab.
- `Inter` wird fuer UI, Display, Navigation, Meta, Labels und viele MD3-/Shell-Elemente verwendet.
- `Source Serif 4` wird fuer Lesetext, Content-Blocks, Karten- und Reading-Bereiche verwendet.

### Lokale Alternativen im Repo

- Unter `app/static/fonts` liegt nur `MaterialSymbolsRounded.woff2`.
- Es wurden keine lokalen `Inter`- oder `Source Serif 4`-Dateien und keine zugehoerigen `@font-face`-Definitionen belegt.

### Geladene vs. genutzte Gewichte

| Font | Quelle | Geladene Gewichte | Genutzte Gewichte | Nutzung | Empfehlung |
|---|---|---:|---:|---|---|
| Inter | extern ueber `app/templates/base.html` | 400, 500, 600, 700 | 400, 500, 600, 700; zusaetzlich ein Token `450` fuer Intro-Typografie | UI, Display, Navigation, Meta, Labels, Brand | produktiv noetig; mittelfristig lokal hosten, wenn Datenschutz/CSP gestrafft werden sollen |
| Source Serif 4 | extern ueber `app/templates/base.html` | 400, 600, 700 | klar belegt: 400 und 600; 700 wurde in diesem engen Audit nicht eindeutig belegt | Lesetext, Karten, Reading-Zonen | produktiv noetig; bei Lokalisierung wahrscheinlich Gewichte pruefen und 700 ggf. trimmen |
| Material Symbols Rounded | lokal ueber `app/static/css/md3/components/material-symbols-fallback.css` und `app/static/fonts/MaterialSymbolsRounded.woff2` | variable Font 100 bis 700 | Basis `wght 300`, `FILL 0`, `GRAD 0`, `opsz 24`; einzelne alte MD3-Overrides vorhanden | Icon-Font | bereits lokal und etablierter Standard fuer Font-Icons |

### CSP-Auswirkung

- `fonts.googleapis.com` bleibt im aktuellen CSP nur fuer die externe CSS-Einbindung von `Inter` und `Source Serif 4` noetig.
- `fonts.gstatic.com` bleibt im aktuellen CSP nur fuer die ausgelieferten Font-Dateien noetig.
- Bei lokaler Auslieferung koennten beide Hosts aus der Font-/Style-Allowlist entfallen.

## 8. Empfehlung

### Icons

Empfohlene Konvention fuer dieses Projekt:

- `Material Symbols Rounded` als Standard fuer inline, textnahe Aktions-, Formular- und Status-Icons
- `pm-icon-mask` als Standard fuer Shell-, Drawer-, Player-, Lock-, Theme- und sonstige Chrome-/Utility-Icons
- Inline-SVGs nur dort, wo UI dynamisch in JS gebaut wird und ein eigener Klassen-/Token-Weg unverhaeltnismaessig waere

Das bedeutet praktisch:

- kein harter Zwang zur Ein-Familien-Migration
- aber eine explizite repoweite Konvention waere sinnvoll, damit der bestehende Dualweg nicht als Zufall weiterwaechst
- die beiden kleinen Restpfade (`material-symbols-outlined`-Snackbar, typografische Pseudo-Icons) koennen spaeter separat bewertet werden

### Fonts

Bewertung fuer dieses Projekt:

- eleganter: `Inter` und `Source Serif 4` lokal hosten
- pragmatisch heute: extern lassen ist funktional vertretbar, solange es bewusst akzeptiert und dokumentiert bleibt
- fuer eine DSGVO-sensible Bildungs-/Forschungsplattform ist lokales Hosting die sauberere Zielrichtung

Konkrete Empfehlung:

- nicht als Sofortblocker dieses Audits behandeln
- aber als eigenen, kleinen Follow-up-Run vor strenger Prod-Abnahme bevorzugen
- falls kurzfristig extern geblieben wird, sollte die Entscheidung bewusst dokumentiert sein, weil die aktuellen CSP-Hosts sonst allein wegen Google Fonts offen bleiben

### Was vor Prod sinnvoll ist

- eine kleine, explizite Icon-Konvention dokumentieren
- entscheiden, ob die Google-Fonts-Abhaengigkeit fuer die Zielumgebung akzeptiert ist
- bei hohem Datenschutzanspruch: Fonts vor oeffentlicher Auslieferung lokal hosten

### Was spaeter reicht

- den kleinen `material-symbols-outlined`-Altpfad bereinigen
- dynamische Comparison-Inline-SVGs optional normalisieren
- typografische Pseudo-Icons nur dann anfassen, wenn ein gezielter UI-Normalisierungslauf ohnehin ansteht

## 9. Folgeprompts

### 1. Normalize Icon System

Read-only vorbereiten und dann eng implementieren:

- dokumentiere zuerst die produktive Dual-Konvention `Material Symbols Rounded` vs. `pm-icon-mask`
- pruefe nur die kleinen Abweichungen: `material-symbols-outlined`-Snackbar, typografische Pseudo-Icons, Inline-SVGs in `research-comparison.js`
- behandle bewusst notwendige Sonderfaelle anders als tote Altlasten
- keine Design-System-Migration
- keine Farbangleichung
- nur kleine, klar belegte Normalisierungen
- fuehre mindestens gezielte Template-/JS-Tests und `python -m compileall app` aus
- schreibe einen Abschlussbericht nach `docs/agent-runs/YYYY-MM-DD_normalize-icon-system.md`

### 2. Localize Google Fonts

Enger Umsetzungs-Run ohne Re-Design:

- lokalisiere nur die heute produktiv benoetigten Familien `Inter` und `Source Serif 4`
- pruefe vorab, welche Gewichte wirklich gebraucht werden, und unterscheide belegte Nutzung von totem Ladegewicht
- passe nur Font-Einbindung und CSP-relevante Folgen an
- keine Typografie-Neugestaltung
- keine Design-System-Migration
- fuehre mindestens `python -m compileall app`, `pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q` und einen gezielten Render-/HTML-Check fuer die Font-Einbindung aus
- schreibe einen Abschlussbericht nach `docs/agent-runs/YYYY-MM-DD_localize-google-fonts.md`

### 3. Clean Up Icon Legacy Rests

Kleiner Bereinigungs-Run fuer sichere Altlasten:

- pruefe nur tote oder wahrscheinlich tote Reste wie das isolierte `material-symbols-outlined`-Snackbar-Modul und ungenutzte MD3-Icon-CSS-Zweige
- historische QA-Artefakte und `docs/agent-runs` nur dokumentieren, nicht migrieren
- keine Icon-Migration produktiver Bereiche erzwingen
- keine Farb- oder Layoutaenderungen
- sichere Altlasten von bewusstem Sonderfall trennen
- fuehre mindestens gezielte JS-/Template-Checks und `python -m compileall app` aus
- schreibe einen Abschlussbericht nach `docs/agent-runs/YYYY-MM-DD_clean-up-icon-legacy-rests.md`

## 10. Tests/Checks

Ausgefuehrt:

- Workspace-Suche nach Icon-Signalen in `app/templates`, `app/static`, `app/src/app`
- Workspace-Suche nach Font-Signalen in `app/templates`, `app/static/css`, `app/tests`
- Workspace-Suche nach verbliebenen `Font Awesome`-/`Bootstrap Icons`-Resten in produktiven App-Pfaden
- `c:\dev\promat\.venv\Scripts\python.exe -m compileall app`
  - erfolgreich
- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q`
  - `65 passed`
- `c:\dev\promat\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -q`
  - `201 passed`

Nicht ausgefuehrt oder ersetzt:

- Terminal-`rg` laut vorgeschlagenem Check
  - auf diesem Windows-Setup im genutzten Terminal nicht verfuegbar; fuer den Audit durch die Workspace-Suchtools ersetzt
- Browser-/Screenshot-QA
  - nicht noetig fuer einen read-only Code-Audit ohne sichtbare UI-Aenderungen

## 11. No-Go

- keine App-, CSS-, JS-, Template-, Test- oder Asset-Dateien geaendert
- keine Fonts heruntergeladen
- keine Icon-Migration umgesetzt
- keine Design-System-Migration
- keine P2-Security-Arbeit umgesetzt
- nur dieser angeforderte Audit-Bericht unter `docs/agent-runs/` wurde neu angelegt
