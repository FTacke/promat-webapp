# ProMat Webapp – Font-Inventar und Migrationsaudit

**Datum:** 2026-05-30  
**Typ:** Read-only Audit – keine Dateiänderungen  
**Zweck:** Grundlage für eine spätere sichere Ablösung von Google Fonts durch lokales Font-Hosting

---

## 1. Executive Summary

Die App lädt zwei externe Text-Fonts über Google Fonts: **Inter** (UI) und **Source Serif 4** (Lesetext). Beide werden als statische Schnitte ohne Italic angefordert. Hinzu kommt ein lokal gehosteter Icon-Font (**Material Symbols Rounded**).

**Kritische Befunde für die Migration:**

1. **Intermediate Weights werden synthetisiert:** Die CSS verwendet `font-weight: 450` und `font-weight: 650`. Google Fonts liefert nur die explizit angeforderten statischen Schnitte (400, 500, 600, 700). Weder für Inter noch für Source Serif 4 existieren Schnitte mit 450 oder 650 – der Browser synthetisiert diese aktuell. Bei lokaler Umstellung muss dieses Verhalten bewusst beibehalten oder durch Variable Fonts ersetzt werden.

2. **Italic wird synthetisiert:** Die Google-Fonts-URL enthält keine Italic-Varianten. Der Browser erzeugt kursiven Text durch CSS-Synthesis. Lokale Dateien müssen dasselbe tun oder echte Italic-Schnitte mitliefern (wäre eine sichtbare Veränderung).

3. **`--book-font-display` nicht definiert:** Die Variable wird neunmal in `30_components.css` referenziert, ist aber nirgends deklariert. Betroffen: Phenomena-Komponenten.

4. **Unicode-Abdeckung:** Für DE/ES/FR benötigte Zeichen (Latin-1 Supplement, General Punctuation) sind in Google-Font-Auslieferungen standardmäßig enthalten, müssen bei lokalem Hosting aber explizit via `unicode-range` sichergestellt werden.

**Umstellung jetzt sinnvoll?** Nein, noch nicht ohne Zusatzarbeit. Eine sichere lokale Umstellung erfordert Variable-Font-Dateien (wegen Weights 450/650), klare Entscheidung zur Italic-Behandlung und einen Browser-Screenshot-Vergleich auf den kritischen Routen.

---

## 2. Aktuelle Font-Einbindung

### Datei: `app/templates/base.html` (Zeilen 18–20)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:wght@400;600;700&display=swap">
```

- Einziger Ort im gesamten Template-Baum mit externem Font-Ladevorgang.
- Kein weiteres Template lädt separat Google Fonts.
- Die `layout.css` wird vor dem Google-Fonts-CSS-Tag gepreloaded (kein render-blocking, da Google Fonts als normales `<link rel="stylesheet">` geladen wird – **nicht preloaded**).
- Google Fonts ist **nicht** hinter einem Consent-Gate.

---

## 3. Google-Fonts-Analyse

### URL-Dekodierung

```
https://fonts.googleapis.com/css2
  ?family=Inter:wght@400;500;600;700
  &family=Source+Serif+4:wght@400;600;700
  &display=swap
```

| Parameter | Wert |
|-----------|------|
| **Font 1** | Inter |
| Inter Weights | 400, 500, 600, 700 (statische Schnitte, NICHT variable) |
| Inter Italic | Nicht angefordert |
| **Font 2** | Source Serif 4 |
| Source Serif 4 Weights | 400, 600, 700 (statische Schnitte, NICHT variable) |
| Source Serif 4 Italic | Nicht angefordert |
| `display` | `swap` → CSS `font-display: swap` |
| Variable Font | Nein (`:wght@` mit Semikolons = statische Instanzen) |
| Subset/Unicode-Range | Nicht explizit angegeben |

### Hinweis zu Unicode-Ranges

Google Fonts liefert ohne expliziten Subset-Parameter automatisch subsets basierend auf dem `Accept-Language`-Header des Browsers aus. In der Praxis enthält die CSS-Antwort von Google für diese Fonts typischerweise:

- `latin` (U+0000–U+00FF, U+0131, U+0152–U+0153, U+02BB–U+02BC, U+02C6, U+02DA, U+02DC, U+2013–U+2014, U+2018–U+201A, U+201C–U+201E, U+2020–U+2022, U+2026, U+2030, U+2039–U+203A, U+2044, U+20AC, U+2122, U+2212, U+FB01–U+FB02)
- `latin-ext` (erweiterter lateinischer Block für europäische Sprachen)

**Diese Unicode-Ranges sind aus dem Repo nicht deduzierbar** – sie werden dynamisch von Google geliefert. Eine lokale Umstellung muss diese Ranges entweder aus dem tatsächlichen Google-Fonts-Response ableiten oder für alle bekannten Zeichenbedarfe (siehe Abschnitt 6) explizit prüfen.

---

## 4. Lokale Fonts

| Datei | Pfad | Größe | Eingebunden in |
|-------|------|-------|----------------|
| `MaterialSymbolsRounded.woff2` | `app/static/fonts/` | 4,9 MB | `css/md3/components/material-symbols-fallback.css` |

Keine weiteren lokal gehosteten Font-Dateien vorhanden. Inter und Source Serif 4 sind **nicht** lokal vorhanden.

### `@font-face`-Regeln (bestehend)

```css
/* app/static/css/md3/components/material-symbols-fallback.css */
@font-face {
  font-family: "Material Symbols Rounded";
  font-style: normal;
  font-weight: 100 700;           /* Variable-Font-Range */
  src: url("/static/fonts/MaterialSymbolsRounded.woff2") format(woff2) tech(variations);
  font-display: block;            /* Verhindert FOUC bei Icon-Font */
}
```

---

## 5. Verwendete Font-Familien, Weights und Stacks

### Font-Variablen-Hierarchie

```
--book-font-ui   → "Inter", system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif
--book-font-body → "Source Serif 4", Georgia, "Times New Roman", "Noto Serif", serif
--book-font-code → "JetBrains Mono", "Cascadia Code", "Fira Code", Consolas, ..., monospace

--promat-font-ui      → var(--book-font-ui)
--promat-font-content → var(--book-font-body)

--pm-type-brand-family   → var(--book-font-ui)   [Seitentitel, Branding]
--pm-type-nav-family     → var(--book-font-ui)   [Navigation]
--pm-type-panel-family   → var(--book-font-ui)   [Panel-Labels]
--pm-type-meta-family    → var(--book-font-ui)   [Metadaten, Breadcrumbs]
--pm-type-display-family → var(--book-font-ui)   [Display-Überschriften]
--pm-type-intro-family   → var(--pm-type-meta-family) → Inter
--pm-type-reading-family → var(--book-font-body) [Fließtext]
--pm-type-card-family    → var(--book-font-body) [Card-Body]
--pm-type-card-link-family → var(--book-font-body)

--md-sys-typescale-base-font-family → var(--book-font-ui)  [MD3-Basis]
--md-sys-typescale-body-large-font-family → var(--book-font-body)
--md-sys-typescale-body-medium-font-family → var(--book-font-body)
```

### Undefined Variable: `--book-font-display`

**Achtung:** `--book-font-display` wird in `30_components.css` an 9 Stellen als `font-family` gesetzt, ist aber in **keiner CSS-Datei** definiert. Der Browser erbt daher die Schrift aus dem DOM-Eltern-Kontext (in der Regel `--book-font-ui` = Inter via `.app-shell`).

Betroffene Selektoren (30_components.css):
- `.pm-phenomena-section-intro__title`
- `.pm-phenomena-status-card__title`
- `.pm-phenomena-panel-header__title`
- `.pm-phenomena-preset-card__title`
- Weitere (~5 weitere Phenomena-/Research-Komponenten)

### Benötigte Font-Weights

**Explizit in CSS (numerisch):**

| Weight | Häufigkeit | Font-Familie |
|--------|-----------|-------------|
| 400 | 9× explizit + viele via `--pm-type-reading-weight` | Inter + Source Serif 4 |
| 500 | 24× explizit + viele via Token | Inter |
| 600 | 58× explizit + viele via Token | Inter + Source Serif 4 |
| 700 | 18× explizit | Inter + Source Serif 4 |
| **450** | 1× via Token (`--pm-type-intro-weight`) | Inter (Intro-Text) |
| **650** | 4× explizit | Inter (UI-Labels, Auth-Titel) + Source Serif 4 (Card-Titel) |
| 100 | 1× | Material Symbols only (in `@font-face` range) |

**Kritisch:** 450 und 650 sind **nicht** in der Google-Fonts-URL angefordert und existieren nicht als statische Schnitte. Sie werden momentan durch Browser-Font-Synthesis interpoliert.

### Font-Styles

- `font-style: normal` — überall explizit als Standard
- `font-style: italic` — 4 Stellen:
  1. `30_components.css:6311` — `.pm-player-inline-ref__label` (Research Player, erbt Source Serif 4)
  2. `page-navigation.css:114` — `.md3-page-navigation__title` (erbt Inter via app-shell)
  3. `text-pages.css:251` — `.md3-text-citation em` (erbt Source Serif 4 über body-large)
  4. `text-pages.css:544` — `.md3-blockquote p` (erbt Source Serif 4 über body-large)

**Italic nicht in Google-Fonts-URL angefordert.** Browser synthetisiert Italic aus den normalen Schnitten.

### Font-Display

| Kontext | `font-display` |
|---------|---------------|
| Google Fonts (Inter + Source Serif 4) | `swap` (via URL-Parameter `display=swap`) |
| Material Symbols Rounded (lokal) | `block` |

---

## 6. Unicode-/Glyph-Bedarf

### Nachgewiesener Bedarf (aus Repo-Dateien)

**Aus `i18n.py` (UI-Strings DE/EN):**

| Code | Zeichen | Name | Block |
|------|---------|------|-------|
| U+00C4 | Ä | LATIN CAPITAL LETTER A WITH DIAERESIS | Latin-1 Supplement |
| U+00D6 | Ö | LATIN CAPITAL LETTER O WITH DIAERESIS | Latin-1 Supplement |
| U+00DC | Ü | LATIN CAPITAL LETTER U WITH DIAERESIS | Latin-1 Supplement |
| U+00E4 | ä | LATIN SMALL LETTER A WITH DIAERESIS | Latin-1 Supplement |
| U+00F6 | ö | LATIN SMALL LETTER O WITH DIAERESIS | Latin-1 Supplement |
| U+00FC | ü | LATIN SMALL LETTER U WITH DIAERESIS | Latin-1 Supplement |
| U+00DF | ß | LATIN SMALL LETTER SHARP S | Latin-1 Supplement |
| U+00ED | í | LATIN SMALL LETTER I WITH ACUTE | Latin-1 Supplement |
| U+00B7 | · | MIDDLE DOT | Latin-1 Supplement |
| U+2013 | – | EN DASH | General Punctuation |
| U+201C | " | LEFT DOUBLE QUOTATION MARK | General Punctuation |
| U+201D | " | RIGHT DOUBLE QUOTATION MARK | General Punctuation |
| U+201E | „ | DOUBLE LOW-9 QUOTATION MARK | General Punctuation |

**Aus Forschungsdaten (Spanisch/Französisch task catalogs + Content YAML):**

| Code | Zeichen | Name | Block |
|------|---------|------|-------|
| U+00E1 | á | LATIN SMALL LETTER A WITH ACUTE | Latin-1 Supplement |
| U+00E9 | é | LATIN SMALL LETTER E WITH ACUTE | Latin-1 Supplement |
| U+00ED | í | LATIN SMALL LETTER I WITH ACUTE | Latin-1 Supplement |
| U+00F3 | ó | LATIN SMALL LETTER O WITH ACUTE | Latin-1 Supplement |
| U+00FA | ú | LATIN SMALL LETTER U WITH ACUTE | Latin-1 Supplement |
| U+00F1 | ñ | LATIN SMALL LETTER N WITH TILDE | Latin-1 Supplement |
| U+00BF | ¿ | INVERTED QUESTION MARK | Latin-1 Supplement |
| U+00E7 | ç | LATIN SMALL LETTER C WITH CEDILLA | Latin-1 Supplement |
| U+00E0 | à | LATIN SMALL LETTER A WITH GRAVE | Latin-1 Supplement |
| U+00E2 | â | LATIN SMALL LETTER A WITH CIRCUMFLEX | Latin-1 Supplement |
| U+00E8 | è | LATIN SMALL LETTER E WITH GRAVE | Latin-1 Supplement |
| U+00EA | ê | LATIN SMALL LETTER E WITH CIRCUMFLEX | Latin-1 Supplement |
| U+00EE | î | LATIN SMALL LETTER I WITH CIRCUMFLEX | Latin-1 Supplement |
| U+00F4 | ô | LATIN SMALL LETTER O WITH CIRCUMFLEX | Latin-1 Supplement |
| U+00C9 | É | LATIN CAPITAL LETTER E WITH ACUTE | Latin-1 Supplement |
| U+00AB | « | LEFT-POINTING DOUBLE ANGLE QUOTATION MARK | Latin-1 Supplement |
| U+00BB | » | RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK | Latin-1 Supplement |
| U+2019 | ' | RIGHT SINGLE QUOTATION MARK | General Punctuation |

### Potenziell benötigte, nicht nachgewiesen

- U+0153 **œ** (LATIN SMALL LETTER OE) — Französisch (z.B. „cœur", „sœur") → Latin Extended-A
- U+00E6 **æ** (LATIN SMALL LETTER AE) — Dänisch/ältere Lehnwörter
- U+00F8 **ø** — Dänisch/Norwegisch
- IPA-Symbole (ɛ ɔ ə ʁ ʃ ʒ etc.) — Nicht in aktuellen Dateien gefunden, aber phonetisches Lehrprojekt; könnten in künftigen Inhalten auftauchen

### Fazit Unicode

Alle bisher nachgewiesenen Zeichen liegen im **Latin-1 Supplement (U+00A0–U+00FF)** und im **General Punctuation Block (U+2000–U+206F)**. Inter und Source Serif 4 decken diese Bereiche vollständig ab. Kritisch wird es, wenn IPA-Symbole oder erweiterte Zeichen (U+0100+) in Corpus-Daten oder UI-Labels hinzukommen — das muss vor der Migration geprüft werden.

---

## 7. Visuelle Paritätsrisiken

### Risiko 1 — Fehlende Intermediate Weights (HOCH)
- **Betrifft:** `font-weight: 450` (Inter, Intro-Text), `font-weight: 650` (Inter + Source Serif 4, Card-Titel, Auth-Titel, Lehrmaterial-Labels, Phenomena-Editor)
- **Aktueller Zustand:** Google Fonts liefert statische Schnitte 400/500/600/700. Der Browser **synthetisiert** 450 und 650 bereits jetzt.
- **Risiko bei statischen lokalen Dateien:** Identische Synthesis wie heute → **kein sichtbarer Unterschied** solange dieselben statischen Schnitte genutzt werden.
- **Risiko bei Variable Fonts lokal:** Echte Interpolation statt Synthesis → Card-Titel und Auth-Titel würden exakt auf dem definierten Weight-Punkt gerendert. Das wäre **visuell besser**, aber eine messbare Abweichung gegenüber heute.
- **Empfehlung:** Variable Fonts bevorzugen; aber einen Screenshot-Vergleich durchführen.

### Risiko 2 — Fehlende Italic-Schnitte (MITTEL)
- **Betrifft:** Research Player (`.pm-player-inline-ref__label`), Seiten-Navigation (`.md3-page-navigation__title`), Zitat-Blöcke, Blockquotes
- **Aktueller Zustand:** Italic wird durch CSS-Synthesis generiert (da nicht in Google-Fonts-URL angefordert).
- **Risiko bei lokalen Dateien ohne Italic:** Identisches Verhalten, Synthesis läuft weiter. Kein Unterschied.
- **Risiko bei lokalen Dateien MIT Italic-Schnitten:** Echter kursiver Schnitt statt Synthesis → sichtbare Änderung in Strichführung und Neigungswinkel, besonders bei Source Serif 4 (Antiqua mit klarer Kursivform).
- **Empfehlung:** Für Phase 1 der Umstellung KEINE Italic-Schnitte mitliefern → Synthesis-Parität beibehalten. Italic-Umstellung als separates, visuell verifizierbares Folge-Issue behandeln.

### Risiko 3 — `font-display`-Wechsel (NIEDRIG)
- **Aktueller Zustand:** `font-display: swap` via Google Fonts.
- **Risiko:** Falls lokal `font-display: block` oder `optional` gesetzt wird → sichtbares Layout-Shift-Verhalten ändert sich.
- **Empfehlung:** Lokal explizit `font-display: swap` setzen, identisch zu heute.

### Risiko 4 — Unterschiedliche Fallback-Kaskade (MITTEL)
- **Inter-Fallback-Stack:** `system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif`
- **Source-Serif-4-Fallback:** `Georgia, "Times New Roman", "Noto Serif", serif`
- Beide Fallbacks sind breit und sinnvoll gewählt. Solange Inter und Source Serif 4 korrekt geladen werden, ist kein sichtbarer Unterschied zu erwarten.
- Risiko besteht nur, wenn der Font in bestimmten Browsern nicht lädt → dann würde der Fallback greifen, was heute mit Google Fonts identisch wäre.

### Risiko 5 — Font-Metriken-Differenz (MITTEL, schlecht quantifizierbar)
- Selbst gleiche Fonts können bei unterschiedlicher WOFF2-Kodierung (z.B. hinting-Unterschiede, Subsetting) leicht andere `ascent`, `descent`, `cap-height`-Werte haben.
- Dies könnte zu unterschiedlichen Zeilenhöhen bei identischem `line-height` führen.
- **Nicht vorhersagbar ohne tatsächliche Font-Dateien und Browser-Vergleich.**
- Betrifft besonders: Button-Höhen, Card-Höhen, Input-Felder mit `line-height`-abhängiger Höhe.

### Risiko 6 — `--book-font-display` undefiniert (NIEDRIG)
- 9 Stellen in `30_components.css` referenzieren diese Variable, die nirgends definiert ist.
- Aktuell erben diese Elemente `Inter` aus dem Kontext. Bei der Migration könnte `--book-font-display` versehentlich mit einem anderen Wert definiert werden.
- **Empfehlung:** Vor der Migration entscheiden, ob `--book-font-display` auf `--book-font-body` (Source Serif 4) oder `--book-font-ui` (Inter) gesetzt werden soll.

### Risiko 7 — Blockierende Ladestrategie (NIEDRIG)
- Die Google-Fonts-CSS wird als reguläres `<link rel="stylesheet">` geladen, nicht als `preload`.
- Bei lokalem Hosting könnte `<link rel="preload" as="font" crossorigin>` ergänzt werden, was die Lade-Performance verbessert.
- Dies ist keine visuelle Parität-Frage, aber relevant für FOUC (Flash of Unstyled Content).

---

## 8. Konkreter Migrationsplan

> **Noch nicht umsetzen.** Dies ist ein Planungsdokument.

### Schritt 1 — Font-Dateien beschaffen

**Benötigte Dateien:**

| Datei | Format | Zweck |
|-------|--------|-------|
| `Inter[wght].woff2` | Variable WOFF2 | Inter UI-Font, alle Weights in einer Datei |
| `SourceSerif4[wght].woff2` | Variable WOFF2 | Source Serif 4 Body-Font |

**Warum Variable Fonts:**
- Decken Weights 450 und 650 korrekt ab (statt Synthesis)
- Eine Datei statt 4 statischer Schnitte pro Familie
- Kleinere Gesamtgröße bei breitem Weight-Spektrum
- Inter Variable: ca. 200–400 KB (wght-Achse 100–900)
- Source Serif 4 Variable: ca. 200–350 KB (wght-Achse 200–900)

**Bezugsquellen:**
- Inter Variable: [github.com/rsms/inter](https://github.com/rsms/inter) → `Inter.woff2` (Variable)
- Source Serif 4 Variable: Google Fonts → Download als Variable Font

**Ablage:** `app/static/fonts/Inter[wght].woff2` und `app/static/fonts/SourceSerif4[wght].woff2`

### Schritt 2 — `@font-face`-Regeln schreiben

Neue Datei: `app/static/css/md3/components/typefaces.css`

```css
/* Inter – Variable Font (UI-Schrift) */
@font-face {
  font-family: "Inter";
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  src: url("/static/fonts/Inter[wght].woff2") format("woff2") tech("variations"),
       url("/static/fonts/Inter[wght].woff2") format("woff2-variations");
  unicode-range:
    U+0000-00FF,    /* Latin Basic + Latin-1 Supplement */
    U+0100-024F,    /* Latin Extended-A + B */
    U+2013-2014,    /* EN DASH, EM DASH */
    U+2018-201E,    /* Typografische Anführungszeichen */
    U+20AC;         /* Euro */
}

/* Source Serif 4 – Variable Font (Lesetext) */
@font-face {
  font-family: "Source Serif 4";
  font-style: normal;
  font-weight: 200 900;
  font-display: swap;
  src: url("/static/fonts/SourceSerif4[wght].woff2") format("woff2") tech("variations"),
       url("/static/fonts/SourceSerif4[wght].woff2") format("woff2-variations");
  unicode-range:
    U+0000-00FF,
    U+0100-024F,
    U+2013-2014,
    U+2018-201E,
    U+20AC;
}
```

**Hinweis:** `unicode-range` für Cyrillisch, Griechisch und IPA weglassen, solange diese nicht nachgewiesen sind.

### Schritt 3 — `base.html` anpassen

Entfernen:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:wght@400;600;700&display=swap">
```

Ersetzen durch:
```html
<link rel="preload" href="{{ url_for('static', filename='fonts/Inter[wght].woff2') }}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{{ url_for('static', filename='fonts/SourceSerif4[wght].woff2') }}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{{ url_for('static', filename='css/md3/components/typefaces.css') }}">
```

### Schritt 4 — `--book-font-display` klären

Vor oder gleichzeitig mit der Font-Migration in `00_tokens.css` definieren:
```css
--book-font-display: var(--book-font-body);  /* oder var(--book-font-ui) – Entscheidung erforderlich */
```

### Schritt 5 — Browser-Screenshot-Vergleich (zwingend)

Vor dem Merge müssen Vor/Nach-Screenshots auf folgenden Routen erstellt werden:

| Route | Grund |
|-------|-------|
| `/de` (Landing Page) | Hauptschrift Inter, Seitentitel, Hero |
| `/de/project/projekt` | Source Serif 4 Fließtext (Lesbarkeit) |
| `/de/research` | Card-Titel mit weight 650 (Source Serif 4) |
| `/de/research/spanish/player/*` | Player mit Inline-Referenz (Italic Source Serif 4) |
| `/de/teaching/spanish/r` | Lehrmaterial mit audio-example__label (Inter 650) |
| `/de/research/spanish/phenomena/overview` | Phenomena-Komponenten (`--book-font-display`) |
| `/admin/users` | Auth-Titel (Inter 650) |

**Viewports:**
- 320px (kleinster Mobile)
- 768px (Tablet)
- 1280px (Desktop)
- 1920px (Wide)

### Schritt 6 — CSP aktualisieren

Die aktuelle CSP in `app/src/app/__init__.py` erlaubt:
```python
"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
"font-src 'self' https://fonts.gstatic.com; "
```

Nach Migration ändern zu:
```python
"style-src 'self' 'unsafe-inline'; "
"font-src 'self'; "
```

`https://fonts.googleapis.com` und `https://fonts.gstatic.com` aus der CSP entfernen.

---

## 9. Offene Fragen

1. **Echte Unicode-Ranges von Google Fonts:** Was liefert Google konkret für die aktuelle URL? → Prüfung mit Browser-DevTools (Network → Response der Fonts-CSS) nötig. Nicht aus Repo ableitbar.

2. **Inter Variable vs. statische Schnitte:** Soll die bessere Darstellung von weights 450/650 als Verbesserung in Kauf genommen werden, oder soll die Synthesis-Parität bewusst erhalten bleiben?

3. **Italic in Phase 1:** Synthesis beibehalten (Parität) oder echte Italic-Schnitte (`Inter-Italic[wght].woff2`, `SourceSerif4-Italic[wght].woff2`) mitliefern (Verbesserung, aber sichtbare Änderung)?

4. **`--book-font-display`:** Auf `--book-font-body` (Source Serif 4) oder `--book-font-ui` (Inter) setzen? Die Phenomena-Komponenten sind Design-seitig zu bewerten.

5. **Subsetting:** Soll das WOFF2 für lateinische Sprachen nur `latin` + `latin-ext` enthalten, oder soll das vollständige Variable-Font-File ohne Subsetting genutzt werden?

6. **IPA/phonetische Zeichen:** Werden in zukünftigen Inhalten IPA-Symbole (ɛ ɔ ə ʁ etc.) als Fließtext in Inter oder Source Serif 4 angezeigt? Falls ja, müssen die Font-Dateien die IPA Extensions (U+0250–U+02AF, U+1D00–U+1D7F) abdecken.

7. **Performance-Target:** Aktuell laden zwei externe Font-Requests (Preconnect + CSS). Wie ist der Performance-Zielwert für lokal?

---

## 10. Empfehlung

**Umstellung jetzt sinnvoll: Nein**

Begründung:
- Die Zwischengewichte 450 und 650 erfordern eine Entscheidung: Synthesis beibehalten (statische Dateien) oder Variable Fonts einsetzen (sichtbare Verbesserung). Diese Entscheidung muss bewusst getroffen werden.
- Italic-Behandlung (Synthesis vs. echte Schnitte) ist ungeklärt.
- `--book-font-display` ist undefiniert – das sollte vor oder mit der Migration geklärt werden.
- Ein Browser-Screenshot-Vergleich auf sieben definierten Routen und vier Viewports ist zwingend erforderlich.

**Voraussetzungen für eine sichere Umstellung:**
1. Klärung der offenen Fragen 1–4
2. Bereitstellung der Variable-Font-Dateien (Inter + Source Serif 4) in `app/static/fonts/`
3. `@font-face`-Regeln gemäß Plan verfassen
4. Vor-Screenshot auf allen Zielrouten
5. Umstellung durchführen
6. Nach-Screenshot und Diff-Vergleich
7. CSS-Anpassung: `--book-font-display` definieren

---

## Anhang: Dateien und Stellen im Überblick

| Datei | Relevanz |
|-------|---------|
| `app/templates/base.html:18-20` | Google Fonts Einbindung (preconnect + stylesheet) |
| `app/static/css/00_tokens.css:19-21` | Kanonische Font-Stack-Definitionen (`--book-font-*`) |
| `app/static/css/00_tokens.css:341` | `--pm-type-intro-weight: 450` |
| `app/static/css/10_typography.css:301` | `font-weight: 650` (card-title, Source Serif 4) |
| `app/static/css/30_components.css:2118,3157,4746` | `font-weight: 650` (Inter UI-Elemente) |
| `app/static/css/30_components.css:3335,3505,3517,3701,4537,5564,7064,8140,8468` | `--book-font-display` (undefinierte Variable) |
| `app/static/css/md3/components/material-symbols-fallback.css` | Bestehende `@font-face` Vorlage (lokal) |
| `app/static/fonts/MaterialSymbolsRounded.woff2` | Einziger lokal gehosteter Font (4,9 MB) |
| `app/src/app/__init__.py:426-436` | CSP-Header (muss nach Migration angepasst werden) |
