# PROMAT Shell Reading Refinement 02

Run-Zeitpunkt: 2026-03-26

## Ziel

Dieser Run hat die nach dem ersten Layout-Overhaul verbliebenen Shell- und Leseraum-Probleme gezielt nachbearbeitet. CORAPAN wurde dabei nur selektiv als technische Referenz fuer robuste Shell-, Drawer-, Top-Bar- und Footer-Strukturen genutzt. Das PROMAT-Designsystem blieb die visuelle Grundlage.

## Vergleichsbasis

Verglichen wurden vor allem diese Bereiche:

- Footer-Struktur und Footer-Rhythmus
- Shell-Grundlayout mit `body.app-shell`, `main`, `footer` und Drawer-Spalte
- Drawer- und Top-App-Bar-Schichtung
- User-Menu-/Dropdown-Verhalten
- Content-Container-Logik fuer Textseiten

Die wesentliche Ableitung aus CORAPAN war nicht die Optik, sondern die Struktur:

- klare `z-index`-Hierarchie
- `overflow: visible` fuer den Main-Bereich
- ruhiger, gestapelter Footer statt stark umgebautem Desktop-Footer
- Textseiten nicht als grosse Card-Box, sondern als offene Leseflaeche

## Hauptprobleme vor dem Run

- Textseiten lagen weiterhin in sichtbar gerahmten, hellen Boxen und wirkten dadurch zu app-/panelartig.
- Der PROMAT-Override setzte der Top-Bar eine abweichende niedrige Schichtung, was die Shell-Robustheit schwaechen konnte.
- Drawer und User-Menu hatten keine explizit zusammengezogene PROMAT-Schichtlogik.
- Der Footer war strukturell zu stark in ein Desktop-Mehrspaltenmuster umgebogen und verlor die ruhig-funktionale CORAPAN-Anmutung.
- Landing-Hero und Landing-Cards wirkten weiterhin zu stark wie generische Web-App-Panels.
- Das User-Menu nutzte `hidden`, `data-open` und `aria-expanded` nicht durchgaengig konsistent.

## Umgesetzte Aenderungen

### 1. Shell / Schichtung

- In `app/static/css/20_layout.css` eine explizite Schicht-Hierarchie eingefuehrt:
  - `--z-index-top-app-bar`
  - `--z-index-dropdown`
  - `--z-index-drawer-modal`
  - `--z-index-dialog`
  - `--z-index-snackbar`
- `body.app-shell` mit `isolation: isolate` abgesichert.
- `#top-app-bar` und `.md3-top-app-bar` auf die kanonische hohe Schicht gezogen.
- `#main-content`, `main.site-main` und `.site-main` auf `background: transparent` und `overflow: visible` gesetzt.

### 2. Textseiten / Leseraum

- `app/templates/_md3_skeletons/page_text_skeleton.html` von der Card-Logik geloest.
- Der Hero-Bereich nutzt jetzt `promat-reading-hero` statt einer sichtbaren Hero-Card.
- Der Haupttext nutzt `promat-reading-space` statt einer editorial Card-Flaeche.
- In `app/static/css/20_layout.css` eine echte Lesebreite definiert:
  - `--promat-reading-width`
  - `--promat-reading-hero-width`
- In `app/static/css/40_cards.css` wurde fuer `.md3-text-page .md3-text-content` und `.promat-reading-space` die Box-Flaeche entfernt:
  - kein Border
  - kein Background-Panel
  - kein Shadow
  - nur offener, vertikal gefuehrter Text-Raum

### 3. Footer

- In `app/static/css/30_components.css` den Footer wieder auf eine ruhigere, gestapelte Struktur zurückgeführt.
- Die fruehere PROMAT-Desktop-Mehrspaltenlogik fuer den Footer entfernt.
- `max-width` des Footer-Contents wieder auf die ruhigere CORAPAN-nahe Breite reduziert.
- Logo-Marker und vertikaler Abstand beruhigt.

### 4. Cards / Landing

- Landing-Hero in `app/templates/pages/index.html` von der sichtbaren Card-Flaeche geloest.
- Landing-Cards in `app/static/css/40_cards.css` ruhiger gemacht:
  - keine Hover-Schatten
  - weichere Border-Logik
  - sanfter Verlauf statt technischem Panel-Eindruck
  - Footer-/Action-Zone ohne harte Trennerlinie
- Card-Padding vergroessert und Radien leicht angehoben.

### 5. Navigation / User Menu

- In `app/static/js/modules/navigation/app-bar.js` den User-Menu-State vereinheitlicht.
- `openUserMenu` und `closeUserMenu` setzen jetzt konsistent:
  - `hidden`
  - `data-open`
  - `aria-expanded`
- Das reduziert Inkonsistenzen zwischen CSS-Open-State und DOM-Open-State.

## Betroffene Dateien

- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/templates/_md3_skeletons/page_text_skeleton.html`
- `app/templates/pages/index.html`
- `app/static/js/modules/navigation/app-bar.js`

## Verifikation

Geprueft wurde lokal gegen `http://127.0.0.1:8000`.

Verifizierte Marker im gerenderten HTML:

- Landing-Hero vorhanden
- Landing-Cards vorhanden
- Text-Hero `promat-reading-hero` vorhanden
- Textbereich `promat-reading-space` vorhanden
- keine `promat-card promat-card--editorial`-Box mehr im Text-Hauptbereich
- Footer-Struktur vorhanden
- Drawer-Logo `img/promat.png` vorhanden

Die verifizierte Textseiten-URL im lokalen Lauf war:

- `/projekt/uebersicht`

## Ergebnis

Der Shell-Unterbau ist jetzt naeher an der robusten CORAPAN-Struktur, ohne PROMAT visuell zu verwischen. Die Textseiten wirken nicht mehr wie in ein grosses UI-Panel gesetzt, sondern wie ein editorieller Leseraum. Footer und Landing-Cards sind ruhiger, waehrend Drawer, Top-Bar und User-Menu technisch sauberer geschichtet sind.

## Nicht Teil dieses Runs

- keine neuen Features
- keine inhaltliche Ueberarbeitung der Projekttexte
- kein Umbau von Atlas-, Admin- oder Auth-Logik ueber die benoetigte Shell-/Card-Anpassung hinaus
- keine Rueckkehr zu CORAPAN-Optik

## AGENTS / .github

- Keine Aenderungen an `AGENTS.md` oder `.github/` in diesem Run.
