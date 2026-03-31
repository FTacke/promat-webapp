# PROMAT Layout Rebuild

Stand: 2026-03-26

## Ziel des Rebuilds

Der Neuaufbau ersetzt die geerbte Corapan-Struktur nicht kosmetisch, sondern systematisch. Grundlage waren:

- `docs/layout/layout_plan.md`
- `docs/layout/zensical_template/`

Ziel war eine ruhige, textzentrierte PROMAT-Oberfläche mit klarer Top-Bar, einem einzigen Seitenpanel und einer sauberen Trennung zwischen `Projekt`, `Forschung` und `Unterricht`.

## Entfernte Legacy-Bausteine

Folgende Altstrukturen wurden aus dem öffentlichen Bereich entfernt oder entkoppelt:

- die IA `Projekt / Korpus / Atlas`
- die alten Corapan-Seiten `proyecto_*`, `corpus_*`, `atlas_placeholder`
- die lineare Vor-/Zurück-Navigation über `partials/page_navigation.html`
- bildgestützte Drawer-Branding-Logik im öffentlichen Shell-Markup
- die öffentlichen Impressum-/Datenschutz-Templates auf Basis der alten Textseitenskeletons

MD3 bleibt nur dort aktiv, wo es funktional weiterhilft, vor allem in Auth- und Formularbereichen.

## Neue Layout-Bausteine

Der Rebuild fuehrt vier zentrale Bausteine ein:

1. `pages/promat_page.html`
   Generische Seitenschablone fuer Reading-, Workbench- und Material-Seiten.

2. Neue Top-Bar in `partials/_top_app_bar.html`
   Permanente globale Navigation mit CSS-Schriftzug `Pronunciation / Matters`, Bereichslinks, Theme-Toggle und Login/Konto.

3. Neues einheitliches Seitenpanel in `partials/_navigation_drawer.html`
   Dasselbe Navigationsprinzip fuer Desktop und Mobile, ohne zweite TOC-Ebene.

4. Datengetriebene Inhalts- und Routenlogik in `app/src/app/routes/public_content.py`
   Inhalte, Sprachbereiche und Panelnavigation werden aus einer konsistenten Struktur erzeugt statt aus vielen Einzeltemplates.

## Neue Informationsarchitektur

### Start

- `/`

Die Startseite fuehrt in die drei Hauptbereiche ein und erklaert die gemeinsame Arbeitslogik der Plattform.

### Projekt

- `/projekt`
- `/projekt/ueber-das-projekt`
- `/projekt/forschungsdesign`
- `/projekt/daten-methodik`
- `/projekt/materialien`
- `/projekt/team`
- `/projekt/publikationen`
- `/projekt/kontakt-mitwirken`

### Forschung

- `/forschung`
- `/forschung/<sprache>/informanten`
- `/forschung/<sprache>/vergleich`
- `/forschung/<sprache>/phaenomene`
- `/forschung/<sprache>/suche`
- `/forschung/<sprache>/korpus-annotation`
- `/forschung/<sprache>/hinweise-zum-zugang`

Sprachen:

- `spanisch`
- `franzoesisch`
- `deutsch-als-fremdsprache`
- `englisch`

### Unterricht

- `/unterricht`
- `/unterricht/<sprache>/einstieg-unterricht`
- `/unterricht/<sprache>/phaenomene`
- `/unterricht/<sprache>/materialien`
- `/unterricht/<sprache>/hinweise-fuer-lehrkraefte`
- `/unterricht/<sprache>/hintergrund-einsatz`

Sprachen:

- `spanisch`
- `franzoesisch`
- `deutsch-als-fremdsprache`
- `englisch`

### Rechtliches

- `/impressum`
- `/datenschutz`

## Theme- und Oberflächenlogik

Die alte Farblogik wurde durch ein neues Token-System ersetzt.

- Primaerfarbe: `#2b4460`
- Sekundaerfarbe: `#a15a95`
- Light- und Dark-Mode auf derselben Variablenbasis
- Serif fuer Lesetext, Inter fuer UI und Navigation

Die Shell arbeitet jetzt mit:

- einer fixierten, ruhigen Top-Bar
- einem nah am Inhalt sitzenden Desktop-Panel
- einem mobilen Slide-in-Panel
- Seitentyp-spezifischen Hero-Flaechen fuer `reading`, `workbench`, `material`

## Offene Anschlussstellen

Der Rebuild bereitet weitere Arbeit vor, ohne sie vorwegzunehmen:

- echte Forschungswerkzeuge statt der aktuellen Dummytexte
- sprachspezifische Such- und Vergleichskomponenten
- didaktische Materialobjekte mit Download- und Filterlogik
- gestufte Freigabe für geschützte Forschungsansichten

## Ergebnis

PROMAT hat jetzt eine eigenständige Shell mit neuer Hauptnavigation, einheitlichem Panel, neuer Projekt-/Forschungs-/Unterrichtslogik und komplett neuen deutschen Dummy-Inhalten. Die öffentliche Oberfläche hängt nicht mehr an der geerbten Corapan-IA.