# PROMAT Layout Refinement

## Ziel

Diese Verfeinerung reduziert den App-Charakter des öffentlichen Shell-Layouts und zieht Header, Panel und Raumstruktur näher an das Zensical-Buchlayout. Das bestehende `pm-*`-System bleibt erhalten; angepasst wurden nur Layout, Typografie und Positionierung.

## Header

Der Header wurde von einer funktionsorientierten Ein-Zeilen-App-Bar auf ein ruhiges zweizeiliges Muster umgestellt:

- Zeile 1 links: Burger auf Mobile plus einzeilige Wortmarke `Pronunciation Matters`
- Zeile 1 rechts: Theme-Toggle und Login/Konto als reduzierte Meta-Zone
- Zeile 2 linksbuendig darunter: Bereichsnavigation `Projekt / Forschung / Unterricht`

Konkrete Aenderungen:

- die globale Navigation wurde aus der ersten Headerzeile herausgeloest und in eine eigene zweite Zeile verschoben
- die Header-Innenbreite laeuft jetzt ueber gemeinsame Shell-Variablen statt ueber getrennte Top-Bar- und Main-Werte
- Brand, Bereichsnavigation und Panel verwenden dieselbe linke Startkante ueber `--promat-shell-axis-offset`
- Desktop-Burger bleibt ausgeblendet; auf Mobile bleibt die erste Zeile kompakt und die zweite Zeile wird zugunsten des Drawer-Musters unterdrueckt
- Theme-Toggle bleibt ein schlichter Button; Login bzw. Konto sitzt als Icon rechts daneben

Spaetere Korrekturen:

- der Header nutzt jetzt keine Ein-Zeilen-App-Bar-Logik mehr, bei der Navigation und Meta-Zone in dieselbe Reihe gedrueckt werden
- Top-Bar-Hintergrund bleibt tokenbasiert in Light und Dark
- der Header ist jetzt sticky im normalen Shell-Flow verankert und verwendet eine subtile Blur-/Transparenzflaeche mit solidem Fallback fuer Browser ohne `backdrop-filter`
- der Active-State der Global-Nav ist jetzt eine feine Hairline direkt an der unteren Kante der Header-Zeile statt Unterstreichung oder Pill
- die Headerhoehe wurde ueber reduzierte Top-/Bottom-Padding-Werte und geringere Row-Min-Heights kompakter gezogen

Grund: Das Vorbild arbeitet nicht mit einer utility-lastigen App-Leiste, sondern mit klar getrennten, ruhigen Zonen auf einer nahezu papierfarbenen Header-Flaeche.

## Header-Blur und Transparenz

Die Headerflaeche folgt jetzt dem Zensical-Prinzip einer ruhigen, leicht transluzenten Leseschicht:

- `#top-app-bar` ist `position: sticky` und bleibt Teil des normalen Shell-Flows
- `promat-topbar` behaelt die untere Trennlinie bei
- fuer Browser mit `backdrop-filter` wird eine sanfte Blur-Flaeche mit `0.4rem` Blur aktiviert
- fuer Browser ohne Filter bleibt eine deckendere, aber tonal identische Hintergrundfarbe aktiv

Die Transparenz ist in Light und Dark ueber eigene Token abgebildet, damit beim Scrollen Text hinter der Leiste nur weich sichtbar bleibt und der Header nicht wie eine glossy App-Bar wirkt.

## Header-Active-State

Die globale Navigation arbeitet final mit einer ruhigen Hairline-Logik:

- keine Pill und kein Hintergrund pro aktivem Top-Level-Bereich
- stattdessen eine `2px` starke Hairline in `#a15a95`
- die Linie sitzt direkt an der unteren Kante der Global-Nav-Zeile und gehoert visuell zur unteren Header-Border

Dadurch bleibt der Bereichswechsel praezise sichtbar, ohne die editoriale Ruhe des Headers zu stoeren.

## Logo

Die Wortmarke ist jetzt einzeilig gesetzt und bleibt typografisch ruhig, aber praesent:

- `font-size: clamp(1.2rem, 1.08rem + 0.32vw, 1.42rem)`
- `font-weight: 700`
- `letter-spacing: -0.015em`
- `line-height: 1`
- `gap: 0.35rem`
- Akzentfarbe: `#a15a95`

`Matters` behaelt die Akzentfarbe, die Wortmarke bricht nicht um und sitzt in derselben linken Achse wie die Bereichsnavigation und das linke Panel.

## Typografie

Die bisher implizite Schriftlogik wurde in eine formale `pm-*`-Skala überführt. Die wichtigsten Gruppen sind:

- `--pm-type-brand-*` fuer Wortmarke und Brandtitel
- `--pm-type-nav-*` fuer globale Navigation
- `--pm-type-panel-*` fuer Panel-/TOC-Navigation
- `--pm-type-meta-*` fuer Meta- und Steuertexte
- `--pm-type-display-*` fuer die primaere H1-Ebene
- `--pm-type-reading-*` fuer Lesetext, H2, H3 und Eyebrows
- `--pm-type-card-*` fuer Card-Title, Card-Body, Card-Link und Card-Eyebrow

Finale Regel:

- H1 bleibt Sans-Serif
- darunter laufen H2, H3, Intro, Fliesstext, Listen sowie Card-Text in der Book-Serif

Der Lesetext wurde gegenueber dem vorherigen Zustand leicht reduziert und ueber Tokens statt Einzelwerten neu ausbalanciert.

## Content-Header-System

Der öffentliche PROMAT-Bereich verwendet jetzt ein gemeinsames, editoriales Seitenkopfsystem statt verteilter Hero-Varianten. Die feste Reihenfolge lautet:

1. Breadcrumb / Path
2. H1
3. Intro / Lead
4. Content

Dieses Muster wird sowohl für öffentliche Inhaltsseiten als auch für die Login-/Zugangsseiten verwendet. Box-Heroes, Card-Heroes und MD3-Hero-Bühnen am Seitenanfang wurden für diese Seitentypen entfernt.

Technisch wird der Kopf ueber ein gemeinsames Partial und benannte `pm-*`-Klassen getragen:

- `pm-content-header`
- `pm-breadcrumb`
- `pm-breadcrumb__list`
- `pm-breadcrumb__item`
- `pm-breadcrumb__separator`
- `pm-breadcrumb__link`
- `pm-content-header__title`
- `pm-content-header__intro`

Damit entsteht kein Parallelmuster mehr zwischen Projekt-, Forschungs-, Unterrichts- und Zugangsseiten.

## Breadcrumbs

Die Breadcrumbs folgen einer ruhigen Meta-Logik im UI-Font:

- kleine, zurückgenommene Schrift über `--pm-type-breadcrumb-*`
- Linkfarbe standardmaessig ueber `--pm-breadcrumb-text`
- Hover-Farbe ueber `--pm-breadcrumb-link-hover`, also `var(--promat-wordmark-accent)`
- Separatoren sind bewusst leiser ueber `--pm-breadcrumb-separator`
- der aktuelle Eintrag bleibt textnah und wird nicht wie Navigation oder Badge behandelt

Die Breadcrumb-Logik wird in den Public-Routen zentral erzeugt, statt pro Template händisch zusammengestellt zu werden.

## Intro-Layer

Direkt unter dem H1 sitzt nun der einzige zweite Textlayer des Seitenkopfs: ein kurzer Intro- beziehungsweise Lead-Absatz. Die frühere Kontextzeile entfällt vollständig.

Der Introtext ist weiterhin Teil der Reading Column, hebt sich aber typografisch klar vom Fliesstext ab. Dafuer traegt das System eigene Tokens statt Einzelwerte:

- `--pm-type-intro-*` fuer Schriftfamilie, Groesse, Laufweite und Zeilenhoehe
- `--pm-text-intro` fuer die ruhig akzentuierte Textfarbe
- `--pm-content-header-breadcrumb-title-gap` fuer den Abstand zwischen Breadcrumb und H1
- `--pm-content-header-title-intro-gap` fuer den Abstand zwischen H1 und Intro

Damit bleibt die Hierarchie ueber alle oeffentlichen Seiten und die Login-/Zugangsseiten gleich: Pfad, Titel, Einleitung, Inhalt.

## Hero-Muster entfernt

Aus dem öffentlichen PROMAT-Bereich entfernt bzw. ersetzt wurden:

- `promat-page__hero` als öffentlicher Seitenkopf
- getoente/boxed Header fuer Workbench- und Materialseiten
- der `md3-hero md3-hero--card`-Header im Login-Skeleton

Sprachwahlseiten, Textseiten und Login folgen nun derselben Textlogik: Header in der Reading Column, danach entweder Fliesstext oder Feature-Bands.

## Reading-Rhythmus

Der Lesefluss wurde aus den groben Block-Gaps geloest und auf lesbare, systemische Abstandswerte umgestellt:

- `--pm-reading-paragraph-gap` fuer `p + p`
- `--pm-reading-heading-gap-before-h2` und `--pm-reading-heading-gap-after-h2`
- `--pm-reading-heading-gap-before-h3` und `--pm-reading-heading-gap-after-h3`
- `--pm-reading-list-item-gap` fuer Listenrhythmus

Diese Regeln greifen innerhalb der Reading Column generisch auf Textseiten, statt fuer einzelne Seiten Sonderabstaende zu setzen.

## Gemeinsame linke Achse

Die ruhige Zensical-Anmutung entsteht hier ueber gemeinsame Geometrie statt ueber optische Naeherung:

- `--promat-shell-max-width` definiert die gemeinsame Header-/Main-Breite
- `--promat-shell-inline-padding` steuert die aussenliegenden Shell-Innenabstaende
- `--promat-shell-axis-offset` definiert die innere linke Startkante fuer Brand, globale Navigation und Panel-Inhalt

Damit beginnen Logo, Hauptnavigation und Panel-TOC auf Desktop an derselben linken Kante. Zufaellige Einzel-Paddings pro Block wurden entfernt.

## Panel-Positionierung

Das Standard-Panel sitzt jetzt nicht mehr in einer eigenen Viewport-Spalte, sondern innerhalb desselben begrenzten Horizontalraums wie der Inhalt.

Umsetzung:

- `#navigation-drawer` wurde in den Main-Wrapper verschoben
- `md3-content-wrapper` bildet auf Desktop ein zweispaltiges Layout aus Panel- und Content-Spalte
- der Abstand zwischen beiden Spalten laeuft ueber `pm-space`-Werte
- der gesamte Shell-Wrapper wurde in der Breite reduziert und ueber `width + max-width + margin-inline: auto` explizit zentriert

Grund: Im Zensical-Buchlayout entsteht der Eindruck eines gemeinsamen Satzspiegels. Panel und Inhalt sollen denselben Rahmen teilen statt als App-Chrome und Content nebeneinander zu stehen.

## Panel-Typografie und Struktur

Die Panel-Kopfzone wurde gestrafft und auf eine gemeinsame linke Achse gestellt:

- Bereichslabel kleiner und muted
- kompaktere Abstaende in Navigation und Footerblock
- aktive Pills bleiben erhalten, sind aber flacher gepolstert und weniger blob-artig gerundet
- der redundante graue Text `Pronunciation Matters` im Panel wurde entfernt
- `promat-panel__inner` verwendet dieselbe Achsen-Variable wie der Header
- Bereichsheader arbeitet jetzt als gemeinsamer Block aus Icon und Titel statt als lose Einzelzeile
- im Projektbereich entfaellt der Panel-Kopf vollstaendig, damit keine doppelte Bereichsbezeichnung neben dem global aktiven Header mehr erscheint
- die Forschungs- und Unterrichts-Sprachauswahlseiten zeigen keinen separaten Bereichskopf mehr
- auf Sprachseiten wird der Panel-Kopf als kleiner Abschnittstitel gelesen: Back-Icon links, Sprachname rechts daneben, beides als ein kompakter Ruecksprung zur Sprachwahl

Die sprachspezifische Kontextzeile nutzt jetzt eigene Panel-Tokens statt Einzelwerte:

- `--pm-panel-stack-gap-compact` fuer den engeren Rhythmus zwischen Kontextblock und Navigation
- `--pm-panel-context-padding-bottom-compact` fuer den reduzierten Abstand zur Trennlinie
- `--pm-panel-context-rule-color` fuer eine leisere Teilung als im Standard-Panel
- `--pm-panel-context-title-gap` und `--pm-panel-context-title-min-height` fuer die Header-Geometrie

Dadurch bleibt der Sprachheader klar als Kontext lesbar, ohne sich wie ein Nav-Item oder Badge zu verhalten.

Zusaetzlich wurden `Impressum` und `Datenschutz` aus dem Panel entfernt, weil diese Links im Footer semantisch sauberer aufgehoben sind.
Im selben Schritt wurde auch der separate Login-Bereich aus dem Panel-Footer entfernt.

## Panel-Navigation und States

Die TOC-Navigation im linken Panel folgt jetzt einem einheitlichen State-System:

- alle Eintraege verwenden dieselbe Boxgeometrie fuer Normal-, Hover- und Active-State
- Hoehe, Padding, Radius und Einzug sind identisch; Unterschiede entstehen nur ueber Farbe, Border und Textton
- Hover nutzt jetzt `--pm-surface-accent-hover`
- Active nutzt `--pm-surface-accent-soft` und `--pm-text-accent`
- Outline, Border-Betonung und inset-Linie entfallen im Active-State komplett
- kompakte Hover-Flaechen fuer Sprachkontext und Panel-Footer laufen ueber gemeinsame `--pm-shell-inline-hover-*`-Tokens, damit links und rechts dieselbe Luft bleibt

Fuer den Sprachkontext selbst gilt bewusst eine andere Logik:

- keine Badge- oder Pill-Flaeche
- Icon und Titel laufen in normaler Textfarbe
- der Ruecksprung wirkt wie ein kleiner Abschnittstitel, nicht wie ein Label

Damit verschwinden springende Pill-Geometrien, und die Navigation bleibt auch in dauerhaft sichtbarem Zustand ruhig lesbar.

## Footer

Der Footer folgt jetzt einem institutionellen Zwei-Zeilen-Modell ohne Zusatzebenen:

- Zeile 1: links `Pronunciation Matters`, rechts die Release-Verlinkung `v0.0`
- Zeile 2: links Copyright- und Institutionszeile mit externer Verlinkung `Hispanistica @ Marburg`, rechts `Impressum` und `Datenschutz`

Systemisch getragen wird das ueber eigene Footer-Tokens:

- `--pm-surface-footer` fuer die ruhige Absetzung vom Content
- `--pm-footer-margin-top`, `--pm-footer-padding-y`, `--pm-footer-row-gap`, `--pm-footer-column-gap`, `--pm-footer-nav-gap` fuer den vertikalen und horizontalen Rhythmus
- `--pm-type-footer-title-*`, `--pm-type-footer-meta-*` und `--pm-type-footer-version-*` fuer eine klare Meta-Hierarchie ohne Sonderstyling pro Einzeltext

Die Struktur bleibt damit textuell, ruhig und systemisch: keine Logos, keine Icons, keine dritte Informationsebene, keine ad-hoc Footer-Navigation.

## Finale Navigationshierarchie

Die sichtbare Hierarchie ist jetzt klar getrennt:

1. Header-Hairline markiert den aktiven Hauptbereich
2. Sprachkontext im Panel markiert auf Forschungs- und Unterrichtsseiten die gewählte Sprache und führt per Klick zur Sprachwahl zurück
3. Panel-Items navigieren innerhalb dieses Kontextes die Inhaltsseiten

Im Projektbereich entfällt der Panel-Kopf, weil der Kontext bereits durch den Header eindeutig ist.

## Shell-Icons

PROMAT folgt fuer Shell-Icons jetzt einer konsistenten, Zensical-nahen Strategie:

- keine gemischten Einzelquellen pro Komponente
- lokale, zentral definierte Outline-SVGs als `data:image/svg+xml`-Tokens
- Ausgabe ueber `mask-image` / `-webkit-mask-image` und `currentColor`

Diese Entscheidung passt zur Zensical-Analyse, weil dort ebenfalls hybride Theme-Icons vorkommen, der projektinterne robuste Mechanismus aber ueber lokal eingebettete SVG-Masken laeuft. Fuer PROMAT ist diese mask-basierte Variante in der Shell die konsistentere Wahl, weil sie farblich sauber an States, Hover und Darkmode gekoppelt werden kann.

Bereichsicons im Panel:

- Projekt: sachliche Ordner-/Projektmappe
- Forschung: Mikroskop als Forschungswerkzeug
- Unterricht: offenes Buch

Die gleichen Shell-Tokens decken auch Burger, Theme-Wechsel, Login und Konto ab.

## Meta-Zone rechts

Die rechte Headerseite ist jetzt bewusst reduziert:

- Theme-Wechsel als schlichter, kleiner Toggle-Button mit Icon und kurzem Statuslabel
- Login für öffentliche Nutzer als Icon-Link
- Konto fuer angemeldete Nutzer als Icon-Trigger fuer das bestehende Menue

Dadurch bleibt die obere Zeile institutionell und ruhig, ohne zweite Utility-Navigation oder doppelte Bereichslinks.

## Reading Column und Feature Band

Textseiten unterscheiden jetzt systemisch zwischen zwei Inhaltszonen:

- `.pm-reading` fuer Kicker, H1, H2/H3, Fliesstext und Listen
- `.pm-feature-band` fuer Kartenreihen, Auswahlmodule, Materialteaser und andere breitere Strukturbausteine

Die Reading Column bleibt schmal und konstant. Feature-Bands duerfen auf die volle Contentbreite gehen, bleiben aber mittig und symmetrisch im Satzspiegel. Dadurch koennen Kartenblöcke breiter sein, ohne dass der Lesefluss selbst aufgeweitet wird.

Neu ist dabei die konsequente Zuordnung des Content-Headers selbst zur Reading Column; Headertexte und Intros werden nicht mehr in Containerboxen eingeschlossen.

## Projekt-Navigation

Die Projekt-Primärnavigation wurde auf vier Eintraege reduziert:

- `Worum es geht`
- `Forschungsdesign`
- `Daten & Methodik`
- `Team`

Dabei wurde `Ueber das Projekt` in `Worum es geht` überführt. Die bisherigen Seiten `Materialien`, `Publikationen` und `Kontakt / Mitwirken` wurden aus der öffentlichen Projekt-Primärnavigation entfernt; alte Slugs leiten auf reduzierte Zielseiten um.

## Spacing

Die kritischen Shell-Abstaende wurden auf `pm-space`-Tokens gezogen:

- Logo zu Navigation
- Navigation zu rechter Meta-Zone
- Panel zu Content
- Footer-Innenabstaende

Neu hinzugekommen sind dabei komponentenspezifische Shell-Tokens fuer Panel-Kontext und Footer. Die Anpassungen wurden bewusst nicht als Einzel-Margins oder Pixelkorrekturen umgesetzt, sondern ueber benannte `pm-*`-Tokens in Surface-, Border-, Type- und Spacing-Familien.

Das staerkt die innere Konsistenz des neuen `pm-*`-Systems auch auf Shell-Ebene.

## Gepruefte Seitentypen

Die Anpassungen wurden gegen vier öffentliche Seitentypen geprüft:

- Startseite `/`
- Projekt-Textseite `/projekt/worum-es-geht`
- Unterrichtsseite mit Sprachkarten `/unterricht`
- Forschungsseite zur Sprachwahl `/forschung`

## Geaenderte Dateien

- `app/templates/base.html`
- `app/templates/partials/_top_app_bar.html`
- `app/templates/partials/_navigation_drawer.html`
- `app/static/css/00_tokens.css`
- `app/static/css/layout.css`
- `app/static/css/10_typography.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/js/theme-toggle.js`
- `app/templates/pages/promat_page.html`
- `docs/layout/promat_typography_system.md`
- `docs/layout/promat_icon_system.md`
