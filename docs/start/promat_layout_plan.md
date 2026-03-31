# PROMAT Layout & Design System Plan

## Ziel

Aufbau eines ruhigen, hochwertigen, editorial geprägten UI-Systems für die Pronunciation Matters Webapp auf Basis von:

- Material Design 3 (technisches System)
- bestehendem Zensical-Buchprojekt (visuelle Referenz)
- reduzierter, semantischer Farbstrategie
- klarer Trennung von UI und Content

---

# 1. Grundprinzipien

## 1.1 Editorial statt „App-Look"

- Fokus auf Lesbarkeit und Inhalt
- keine flächige Markenfärbung
- ruhige, warme Neutrals dominieren
- Akzentfarben nur funktional einsetzen

## 1.2 System statt Einzelentscheidungen

- alle Farben = Rollen (Tokens)
- keine ad-hoc Farben
- klare Hierarchie über Surface, nicht Shadow

## 1.3 Typografische Trennung

- UI = funktional
- Content = leserlich / editorial

---

# 2. Farbstrategie

## 2.1 Rollen

### Primary (Marke)

Mauve (aus Logo abgeleitet):

- Hauptfarbe für Interaktion
- nicht für Flächen

Einsatz:
- aktive Navigation
- Links
- Buttons
- Fokuszustände

---

### Secondary (Gegenpol)

Gedämpftes Blau:

Einsatz:
- sekundäre Aktionen
- visuelle Differenzierung
- alternative States

---

### Neutrals (dominant)

Die wichtigste Ebene des Systems.

Rollen:

- App Background (outer)
- Content Surface ("Papier")
- Elevated Surface (Top Bar, Dialoge)
- Borders / Outline

Prinzip:

- warm, leicht getönt
- kein hartes Weiß als Standardfläche
- minimale Kontraste statt starker Farbwechsel

---

## 2.2 Konkrete Token-Richtung

- Background: sehr hell, warm
- Content: leicht wärmer (Papier-Effekt)
- Text: dunkel, klar
- Border: subtil

---

## 2.3 Wichtige Regeln

Nicht tun:

- große Flächen in Primary einfärben
- mehrere Akzentfarben gleichzeitig dominant nutzen
- graue, kontrastarme Texte

---

# 3. Surface-System (MD3 korrekt genutzt)

## Rollen

- Surface → App-Hintergrund
- Surface Container → Contentbereich
- Surface Bright → Top Bar / Overlays
- Surface Variant → Sidebar / leichte Trennung

## Prinzip

Tiefe entsteht durch:

- Tonwertunterschiede
- Abstand
- Typografie

Nicht durch:

- starke Shadows

---

# 4. Layout-Struktur

## 4.1 Grundlayout

- links: Navigation (Nav Drawer)
- rechts: Content

## 4.2 Sidebar

- neutral gehalten
- aktive Items über Farbe + Gewicht
- keine flächige Hervorhebung

## 4.3 Content-Bereich

- "Papier"-Fläche
- begrenzte Breite (Lesespalte)
- viel Weißraum

## 4.4 Top Bar (optional)

- weiß oder sehr hell
- nur feine Trennlinie

---

# 5. Typografie

## 5.1 Fonts

- UI: Inter
- Content: Source Serif 4

## 5.2 Verteilung

### UI (Inter)

- Navigation
- Buttons
- Labels
- Meta-Informationen
- Formulare

### Content (Source Serif 4)

- Fließtext
- längere Inhalte
- Beispiele

---

## 5.3 Headings

- H1 zunächst Inter (bewusst systemisch)
- später optional Serif möglich

---

## 5.4 Lesetypografie

- line-height: 1.6–1.75
- max-width: 65–75ch
- klare Abstände

---

# 6. Übertragung des Zensical-Systems

## 6.1 Was übernommen wird

Aus den bestehenden CSS-Dateien:

- warme Neutralpalette
- klare Typografie-Trennung
- ruhige Header/Navigation
- begrenzte Contentbreite
- feine Borders statt Schatten

## 6.2 Was angepasst wird

- bisheriger Primary (Blau) → wird Secondary
- neuer Primary = Mauve
- stärkere semantische Trennung von UI vs Content

---

# 7. Admonitions → Card-System

Die bestehenden Admonitions dienen als direkte Vorlage.

## 7.1 Eigenschaften der Admonitions

- sanfte Hintergrundtönung (kein Vollfarbblock)
- feine Border
- geringe visuelle Lautstärke
- konsistente Struktur
- semantische Differenzierung über Farbe + Icon

---

## 7.2 Übertragung auf MD3 Cards

### Grundprinzip

Cards = systematisierte Admonitions

---

## 7.3 Card-Typen

### 1. Standard Card

- neutraler Hintergrund
- feine Border
- kein oder minimaler Shadow

Verwendung:
- Container
- UI-Elemente

---

### 2. Soft Semantic Card

- leichte Tönung
- optional Icon oder Marker

Verwendung:
- Hinweise
- Kontext
- didaktische Elemente

---

### 3. Editorial Card

- sehr ruhig
- fast neutral

Verwendung:
- längere Inhalte
- Meta-Information

---

### 4. Highlight Card

- minimal stärkerer Akzent
- aber keine Vollfläche

Verwendung:
- wichtige Hinweise
- Key Content

---

## 7.4 Farbprinzip für Cards

- Tönung über Mischung mit Neutral
- keine reinen Akzentflächen
- Akzent eher in:
  - Icon
  - Border
  - Marker

---

## 7.5 Shadow-Regel

- Standard: kein Shadow
- Hover: minimal
- Tiefe über Surface + Spacing

---

# 8. Semantik statt Farbe

Farben sind unterstützend, nicht führend.

Semantik entsteht durch:

- Struktur
- Typografie
- Layout
- Labels

---

# 9. Gesamtstrategie

## Kombination

- MD3 = technisches Fundament
- Zensical = visuelle Referenz
- Admonitions = Komponentenlogik

## Ergebnis

- ruhige, hochwertige UI
- klare Hierarchie
- starke Lesbarkeit
- skalierbares System

---

# 10. Leitlinien für Umsetzung

- immer zuerst Neutral denken
- Akzent nur gezielt einsetzen
- Typografie bewusst trennen
- Cards wie Admonitions behandeln
- keine unnötige visuelle Komplexität

---

# 11. Konkretes Token-System für die PROMAT-Webapp

Dieses Token-System ist als Startpunkt für die spätere Umsetzung in einer aus dem CORAPAN-Template geklonten PROMAT-Webapp gedacht.

## 11.1 Design-Tokens (semantisch)

### Brand / Accent

```css
:root {
  --promat-primary: #8b4a78;
  --promat-on-primary: #ffffff;
  --promat-primary-container: #f2d9e8;
  --promat-on-primary-container: #3a102f;

  --promat-secondary: #4d648a;
  --promat-on-secondary: #ffffff;
  --promat-secondary-container: #dde5f3;
  --promat-on-secondary-container: #1d2d45;

  --promat-tertiary: #c8a7b6;
  --promat-on-tertiary: #2f1f27;
}
```

### Neutrals / Surfaces

```css
:root {
  --promat-bg: #f7f4f2;
  --promat-surface: #f7f4f2;
  --promat-surface-1: #f3efea;
  --promat-surface-2: #ece7e2;
  --promat-surface-bright: #ffffff;
  --promat-surface-variant: #ebe6e2;

  --promat-fg: #1f1b18;
  --promat-fg-soft: #5e5753;
  --promat-outline: #c9c1bc;
  --promat-outline-soft: rgba(31, 27, 24, 0.08);
}
```

### Utility / States

```css
:root {
  --promat-link: var(--promat-primary);
  --promat-link-hover: #6f365f;
  --promat-focus: var(--promat-primary);
  --promat-selection: rgba(139, 74, 120, 0.14);
  --promat-shadow-soft: 0 1px 2px rgba(31, 27, 24, 0.06);
}
```

---

## 11.2 Mapping auf MD3-Rollen

Wenn die App intern MD3-Tokens verwendet, sollte das semantisch ungefähr so gemappt werden:

```css
:root {
  --md-sys-color-primary: var(--promat-primary);
  --md-sys-color-on-primary: var(--promat-on-primary);
  --md-sys-color-primary-container: var(--promat-primary-container);
  --md-sys-color-on-primary-container: var(--promat-on-primary-container);

  --md-sys-color-secondary: var(--promat-secondary);
  --md-sys-color-on-secondary: var(--promat-on-secondary);
  --md-sys-color-secondary-container: var(--promat-secondary-container);
  --md-sys-color-on-secondary-container: var(--promat-on-secondary-container);

  --md-sys-color-surface: var(--promat-surface);
  --md-sys-color-surface-container: var(--promat-surface-1);
  --md-sys-color-surface-container-high: var(--promat-surface-2);
  --md-sys-color-surface-bright: var(--promat-surface-bright);
  --md-sys-color-surface-variant: var(--promat-surface-variant);

  --md-sys-color-on-surface: var(--promat-fg);
  --md-sys-color-on-surface-variant: var(--promat-fg-soft);
  --md-sys-color-outline: var(--promat-outline);
}
```

Hinweis:
- MD3 bleibt das technische Fundament.
- Die PROMAT-Tokens definieren die visuelle Ausprägung.

---

# 12. Typografie-Tokens

Die Typografie orientiert sich klar am Buchprojekt.

## 12.1 Font Families

```css
:root {
  --promat-font-ui: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --promat-font-content: "Source Serif 4", Georgia, serif;
}
```

## 12.2 Font Usage

```css
:root {
  --promat-font-body: var(--promat-font-content);
  --promat-font-heading: var(--promat-font-ui);
  --promat-font-nav: var(--promat-font-ui);
  --promat-font-label: var(--promat-font-ui);
  --promat-font-meta: var(--promat-font-ui);
}
```

## 12.3 Type Scale (Startwerte)

```css
:root {
  --promat-text-xs: 0.8125rem;
  --promat-text-sm: 0.9375rem;
  --promat-text-md: 1rem;
  --promat-text-lg: 1.125rem;
  --promat-text-xl: 1.375rem;
  --promat-text-2xl: 1.75rem;
  --promat-text-3xl: 2.25rem;

  --promat-leading-ui: 1.4;
  --promat-leading-content: 1.7;
  --promat-leading-tight: 1.2;

  --promat-measure-content: 72ch;
}
```

## 12.4 Typografische Regeln

### UI

- Inter
- 400 / 500 / 600
- eher kompakt

### Content

- Source Serif 4
- 400 / 600
- großzügige Zeilenhöhe

### H1

- zunächst Inter
- systemisch, klar, ruhig

---

# 13. Layout-Tokens

```css
:root {
  --promat-radius-sm: 0.4rem;
  --promat-radius-md: 0.65rem;
  --promat-radius-lg: 0.9rem;

  --promat-space-1: 0.25rem;
  --promat-space-2: 0.5rem;
  --promat-space-3: 0.75rem;
  --promat-space-4: 1rem;
  --promat-space-5: 1.5rem;
  --promat-space-6: 2rem;
  --promat-space-7: 3rem;

  --promat-content-max: 80ch;
  --promat-sidebar-width: 18rem;
  --promat-border-width: 1px;
}
```

---

# 14. Konkretes Card-System für PROMAT

Die Card-Logik soll direkt von der formalen Ruhe der Admonitions inspiriert sein.

## 14.1 Grundprinzipien

Cards sind:
- ruhig
- strukturiert
- semantisch lesbar
- kaum schattenbasiert

Nicht gewünscht:
- laute Vollflächen
- starke Box-Effekte
- übertriebene Material-Elevation

---

## 14.2 Basisklasse

```css
.promat-card {
  background: var(--promat-surface-1);
  color: var(--promat-fg);
  border: 1px solid var(--promat-outline-soft);
  border-radius: var(--promat-radius-md);
  box-shadow: none;
  padding: var(--promat-space-4) var(--promat-space-5);
}

.promat-card__title {
  font-family: var(--promat-font-ui);
  font-size: var(--promat-text-lg);
  font-weight: 600;
  line-height: var(--promat-leading-tight);
  margin: 0 0 var(--promat-space-3);
}

.promat-card__body {
  font-family: var(--promat-font-content);
  font-size: var(--promat-text-md);
  line-height: var(--promat-leading-content);
}
```

Diese Basisklasse ist die neutrale Standard-Card.

---

## 14.3 Card-Typen

### A. Standard Card

Verwendung:
- normale Inhaltscontainer
- Panels
- einfache Informationseinheiten

Stil:
- neutral
- keine zusätzliche Tönung

```css
.promat-card--standard {
  background: var(--promat-surface-1);
}
```

---

### B. Editorial Card

Vorbild:
- `summary` / `cite`-artige Ruhe aus dem Buchprojekt

Verwendung:
- längere Texteinheiten
- Meta-Information
- begleitende Erklärungen

```css
.promat-card--editorial {
  background: color-mix(in srgb, var(--promat-surface-1) 88%, white 12%);
  border-color: rgba(31, 27, 24, 0.06);
}
```

---

### C. Primary Semantic Card

Vorbild:
- ruhige, leicht getönte Admonition

Verwendung:
- wichtige Hinweise
- Kerninformationen
- didaktische Leitpunkte

```css
.promat-card--primary {
  background: color-mix(in srgb, var(--promat-primary) 8%, var(--promat-surface-1));
  border-color: color-mix(in srgb, var(--promat-primary) 22%, var(--promat-outline));
}
```

---

### D. Secondary Semantic Card

Verwendung:
- Kontext
- Sekundärinfos
- analytische Hilfsinformationen

```css
.promat-card--secondary {
  background: color-mix(in srgb, var(--promat-secondary) 8%, var(--promat-surface-1));
  border-color: color-mix(in srgb, var(--promat-secondary) 22%, var(--promat-outline));
}
```

---

### E. Meta Card

Verwendung:
- Zitation
- technische Hinweise
- Randinformationen

```css
.promat-card--meta {
  background: color-mix(in srgb, var(--promat-surface) 94%, white 6%);
  border-color: var(--promat-outline);
}
```

---

# 15. Admonition-inspirierte Semantik für die App

Die Zensical-Admonitions sind eine wertvolle formale Vorlage und dürfen in künftigen Planungs- oder Prompt-Kontexten ausdrücklich referenziert werden.

## 15.1 Übertragbare Eigenschaften

Aus den Zensical-Dateien zu übernehmen:

- sehr sanfte Tönungen
- Border statt Shadow
- konsistente Grundstruktur
- Semantik über kleine Differenzen, nicht über massive Farbflächen
- typografisch ruhige Titelzonen

---

## 15.2 Semantische Rollen für PROMAT

Vorschlag für App-interne semantische Card-Typen:

### `info`
Allgemeine Hinweise, Orientierung, erklärende Zusatzinfos

- leicht primary-getönt
- ruhig

### `context`
sprachlicher oder fachlicher Kontext

- leicht secondary-getönt

### `practice`
Übungen, Aufgaben, konkrete Anwendungsimpulse

- warm-neutral mit sehr leichter Tertiary-Nuance

### `rule`
Regeln, Kernprinzipien, normierende Aussagen

- neutral mit klarer Border
- typografisch stark, farblich zurückhaltend

### `quote` / `evidence`
Belegstellen, Zitate, Datenausschnitte

- editorial / meta-artig
- fast neutral

---

## 15.3 Beispiel-API für Klassen

```css
.promat-card--info {}
.promat-card--context {}
.promat-card--practice {}
.promat-card--rule {}
.promat-card--evidence {}
```

Diese Klassen sollten immer auf derselben strukturellen Basisklasse aufbauen.

---

# 16. Beispiel-CSS für semantische Ausprägungen

```css
.promat-card--info {
  background: color-mix(in srgb, var(--promat-primary) 7%, var(--promat-surface-1));
  border-color: color-mix(in srgb, var(--promat-primary) 20%, var(--promat-outline));
}

.promat-card--context {
  background: color-mix(in srgb, var(--promat-secondary) 7%, var(--promat-surface-1));
  border-color: color-mix(in srgb, var(--promat-secondary) 20%, var(--promat-outline));
}

.promat-card--practice {
  background: color-mix(in srgb, var(--promat-tertiary) 8%, var(--promat-surface-1));
  border-color: color-mix(in srgb, var(--promat-tertiary) 22%, var(--promat-outline));
}

.promat-card--rule {
  background: color-mix(in srgb, var(--promat-surface-1) 90%, white 10%);
  border-color: var(--promat-outline);
}

.promat-card--evidence {
  background: color-mix(in srgb, var(--promat-surface) 96%, white 4%);
  border-color: rgba(31, 27, 24, 0.1);
}
```

---

# 17. Komponentenregeln für die spätere Implementierung

## 17.1 Navigation / Drawer

- Hintergrund neutral
- aktive Items in Primary
- kein bunter Vollflächen-Drawer
- Inter für Labels

## 17.2 Buttons

- Primary Buttons in Mauve
- Secondary Buttons neutral oder blau-akzentuiert
- Ghost / Text Buttons sehr reduziert

## 17.3 Links

- standardmäßig Primary
- Hover dunkler
- Underline zurückhaltend aber klar

## 17.4 Dialoge / Overlays

- hell, fast weiß
- Border oder sehr weicher Shadow
- keine starke Tönung

## 17.5 Tabellen / Result-Listen

- neutral
- Header UI-orientiert
- ggf. Serif nur in längeren textlichen Zellen, nicht global

---

# 18. Umsetzungshinweise für die aus CORAPAN geklonte PROMAT-Webapp

## 18.1 Was früh angelegt werden sollte

- zentrale Token-Datei
- getrennte Typografie-Datei
- Komponenten-Datei für Cards / Panels / Notices
- semantische Utility-Klassen

## 18.2 Was nicht verteilt werden sollte

Nicht sinnvoll:
- Farblogik quer über viele Komponenten streuen
- gleiche Semantik an mehreren Stellen anders definieren
- schnelle Einzelstyles ohne Token-Anbindung

## 18.3 Zielarchitektur

Empfohlene Struktur:

- `00_tokens.css` → Farben, Spacing, Radius, Typography Tokens
- `10_typography.css` → UI-/Content-Regeln
- `20_layout.css` → App Shell, Drawer, Contentzonen
- `30_components.css` → Buttons, Inputs, allgemeine Komponenten
- `40_cards.css` → semantisches Card-System, Admonition-Äquivalente

---

# 19. Fazit

Das PROMAT-System soll nicht „bunt“ wirken, sondern hochwertig, ruhig und semantisch kontrolliert.

Die Basis dafür ist:

- warme neutrale Flächen
- Inter für UI
- Source Serif 4 für Content
- Mauve als Primary
- Blau als Secondary
- Admonition-inspirierte, sehr ruhige Cards
- MD3 als technisches Fundament im Hintergrund

So kann aus dem CORAPAN-Template zügig eine eigenständige PROMAT-Webapp mit vollständigem, konsistentem Tokensystem entstehen.

