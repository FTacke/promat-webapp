# PROMAT Layout Overhaul 01

Run-Zeitpunkt: 2026-03-26

## 1. Ziel des Runs

Ziel dieses Runs war ein kontrollierter Layout-Overhaul des vorhandenen PROMAT-Bootstraps. Die bestehende Übergangsoberfläche sollte auf das definierte PROMAT-Designsystem umgestellt werden: semantische Tokens, ruhiges Surface-System, klare Typografie-Trennung, systematische Cards und konsistentes UI-Chrome.

## 2. Bezug auf `promat_layout_plan.md`

Der Run wurde explizit gegen `docs/start/promat_layout_plan.md` umgesetzt. Leitend waren insbesondere:

- Mauve als Primary und Blau als Secondary
- warme neutrale Surface-Palette statt kalt-blauem MD3-Restbild
- klare Trennung von UI-Font und Content-Font
- Paper-/Surface-System fuer Contentbereiche
- Card-System mit subtiler Toenung, Border vor Shadow
- ruhige Sidebar und reduziertes UI-Chrome

## 3. Identifizierte Probleme im alten Layout

- Das bisherige MD3-Token-Set nutzte eine blaue Primary-Farbe und kuehle Surface-Tones, was dem PROMAT-Plan widersprach.
- Ein explizites PROMAT-Token-System mit `--promat-*` Rollen fehlte.
- `app/static/css/app-tokens.css` war nur ein kleiner Zwischenlayer und kein tragfaehiges Designsystem.
- Typografie lief weiterhin technisch auf Roboto-/System-Basis; Inter und Source Serif 4 waren nicht sauber getrennt.
- Contentbereiche nutzten keine konsequente Paper-Flaeche mit begrenzter Lesespalte.
- Cards waren technisch vorhanden, aber nicht als systematisches PROMAT-Card-System organisiert.
- Startseiten-Cards wirkten zu stark als technische MD3-Karten statt als editoriale, ruhige Einstiegselemente.
- Die Sidebar nutzte noch flaechenhafte Aktiv-Hinterlegungen statt eine leisere Markierung ueber Farbe und Gewicht.
- Im Footer und Drawer war die gewuenschte Logo-/Badge-Nutzung noch nicht auf die angeforderten Dateien gezogen.
- In `app/templates/auth/admin_users.html` wurde noch eine nicht vorhandene `search-ui.css` referenziert.

## 4. Konkret implementierte Aenderungen

### Tokens

- Neues zentrales Token-File `app/static/css/00_tokens.css` angelegt.
- PROMAT-Farbtokens (`--promat-primary`, `--promat-secondary`, Surface- und Outline-Tokens) eingefuehrt.
- MD3-Rollen auf das PROMAT-System gemappt.
- Spacing-, Radius-, Width- und Utility-Tokens vereinheitlicht.
- App-weite Variablen wie `--app-background`, `--app-theme-color`, `--drawer-width` und `--text-page-max-width` in den neuen Token-Layer überführt.
- Veraltete Einbindung von `app/static/css/app-tokens.css` entfernt; Datei geloescht.

### Typografie

- Neues zentrales Typografie-File `app/static/css/10_typography.css` angelegt.
- Inter und Source Serif 4 in `base.html` eingebunden.
- UI-Zonen auf Inter gezogen: Top Bar, Drawer, Buttons, Labels, Footer, Form-UI.
- Content-Zonen auf Source Serif 4 gezogen: Fliesstext, Textseiten, Intro-/Lead-Texte, Card-Fliesstext.
- Heading-Hierarchie mit Inter und engerem Tracking neu gesetzt.
- Lesebreite und Content-Line-Height fuer Textbereiche vereinheitlicht.

### Layout

- Neues Layout-Override `app/static/css/20_layout.css` angelegt.
- Outer Background und Main Surface auf das neue neutrale Surface-System umgestellt.
- Content-Wrapper neu gerahmt und vertikal ruhiger ausgerichtet.
- Textseiten nutzen jetzt konsequent eine Paper-artige editoriale Flaeche.
- Startseite erhielt eine echte Hero-/Intro-Struktur statt eines zufaellig zentrierten Logos.
- Der Drawer trennt sich auf Desktop ueber Border und Surface-Variant sauber vom Content.

### Komponenten und Cards

- Neues Komponenten-Override `app/static/css/30_components.css` angelegt.
- Neue Card-System-Datei `app/static/css/40_cards.css` angelegt.
- Basisklasse `.promat-card` eingefuehrt und auf bestehende `md3-card`-Strukturen abgebildet.
- Varianten fuer `standard`, `editorial`, `primary`, `secondary`, `meta` sowie semantische Varianten `info`, `context`, `practice`, `rule`, `evidence` angelegt.
- Cards arbeiten jetzt mit sehr subtiler Toenung und Border-Akzent statt mit starken Shadows.
- Buttons neu auf PROMAT-Primary/Secondary-Logik gezogen.
- Sidebar-Active-State auf Farbe, Gewicht und einen schmalen linken Akzent reduziert.
- Footer-Chrome auf die gewuenschten Bildassets gezogen.

### Templates und Branding

- `base.html` auf die neue CSS-Staffel 00/10/20/30/40 umgestellt.
- Startseite `app/templates/pages/index.html` mit neuem Hero-Bereich und ruhigem Card-Grid neu strukturiert.
- Textseiten-Skelett `app/templates/_md3_skeletons/page_text_skeleton.html` auf `promat-card`-basierte Hero- und Content-Container gezogen.
- Drawer-Template auf `promat.png` umgestellt.
- Footer-Template explizit auf `corapan_basic.png` und `hispanistica_badge.png` verdrahtet.
- `app/src/app/branding.py` fuer das neue Branding-/Asset-Set bereinigt.
- Broken Include `css/md3/components/search-ui.css` aus `app/templates/auth/admin_users.html` entfernt.

### Verifikation / Laufumgebung

- `app/scripts/dev-start.ps1` so angepasst, dass das Workspace-`\.venv` bevorzugt verwendet wird.
- Lokaler Lauf gegen `http://127.0.0.1:8000/` erfolgreich verifiziert.
- HTML-Pruefung bestaetigte neue Landing-Hero-Struktur, editoriale Textseiten-Container sowie die gewuenschten Drawer-/Footer-Bildassets.

## 5. Betroffene Dateien

- `app/static/css/00_tokens.css`
- `app/static/css/10_typography.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/static/css/md3/tokens.css`
- `app/templates/base.html`
- `app/templates/pages/index.html`
- `app/templates/_md3_skeletons/page_text_skeleton.html`
- `app/templates/partials/_navigation_drawer.html`
- `app/templates/partials/footer.html`
- `app/templates/auth/admin_users.html`
- `app/src/app/branding.py`
- `app/scripts/dev-start.ps1`
- `app/static/js/drawer-logo.js`
- `app/static/js/theme.js`

## 6. Was bewusst noch NICHT umgesetzt wurde

- Keine neuen Produktfeatures, kein Player, kein Search, kein BlackLab, kein Editor, kein Analytics-Ausbau, kein Admin-Ausbau.
- Keine inhaltliche redaktionelle Bereinigung der uebernommenen spanischen Projekt-/Korpus-Texte.
- Kein eigenstaendig ausgearbeitetes separates Dark-Theme auf PROMAT-Niveau; der Run fokussierte das verbindliche Light-/Surface-System.
- Keine systematische Entfernung aller historischen CORAPAN-Bezuege in nicht direkt betroffenen Altdateien.

## 7. Visuelles Ergebnis

- Die Oberfläche wirkt jetzt deutlich ruhiger und wärmer.
- Die Sidebar ist neutraler und weniger flaechig, aktive Eintraege werden ueber Farbe und Gewicht signalisiert.
- Der Hauptbereich liest sich staerker als editoriale Papierflaeche statt als technische App-Flaeche.
- Die Startseite hat einen klaren Einstieg mit Hero, Logo und geordnetem Card-Grid.
- Buttons, Links, Footer und Karten folgen jetzt derselben zurückhaltenden Gestaltungslogik.

## 8. Verbleibende Probleme

- Mehrere uebernommene Inhaltsseiten enthalten weiterhin spanische Texte und CORAPAN-Bezuege; das ist inhaltlich, nicht strukturell.
- Alte CORAPAN-Kommentare und Namespace-Reste existieren weiterhin in einigen nicht fokussierten JS-/Python-Dateien.
- Die CSS-Basis enthaelt weiterhin den umfangreichen MD3-Unterbau; der neue PROMAT-Layer ueberschreibt ihn gezielt, hat ihn aber noch nicht komplett ausgeduennt.
- Nicht alle Legacy-Komponenten wurden visuell einzeln auditiert; der Run konzentrierte sich auf Shell, Textseiten, Startseite und UI-Chrome.

## 9. Empfohlene naechsten Schritte

- Verbliebene sichtbare CORAPAN-/spanische Inhalte auf Projekt- und Korpusseiten redaktionell auf PROMAT umstellen.
- Den neuen Card-Layer schrittweise auch auf Auth-, Fehler- und Admin-Seiten semantisch feinjustieren.
- Nicht mehr genutzte Legacy-CSS- und JS-Reste gezielt abbauen, sobald die neue PROMAT-Basis stabil bestaetigt ist.
- Optional ein eigenes, planbasiertes Dark-Theme definieren, falls der Theme-Toggle langfristig erhalten bleiben soll.

## AGENTS / .github

- Keine Aenderungen an `AGENTS.md` oder `.github/` in diesem Run.