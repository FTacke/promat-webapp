# PROMAT Layout Plan

Stand: Arbeitsgrundlage für den geplanten Neuaufbau des Layouts.  
Ziel ist **kein schrittweises Reparieren der aktuellen Corapan-Übernahme**, sondern ein **sauberer, systematischer Neuaufbau** der PROMAT-Webplattform auf Basis der Zensical-/Buchlogik.

---

## 1. Zielbild

PROMAT soll als ruhige, akademische, eigenständige Projektplattform erscheinen.  
Die Seite ist **research first**, bleibt aber für Unterricht und öffentliche Projektkommunikation offen und verständlich.

Die Plattform vereint drei Bereiche:

1. **Projekt** – öffentliche Informationen zum Gesamtprojekt „Pronunciation Matters“
2. **Forschung** – sprachspezifische, teils geschützte Daten- und Analyseoberflächen
3. **Unterricht** – sprachspezifische, öffentliche Materialien für Lehrkräfte

Die bisherige, aus Corapan übernommene Struktur soll dafür **nicht weiter kosmetisch angepasst**, sondern **ersetzt** werden.

---

## 2. Grundprinzipien

### 2.1 Ein Navigationssystem für alles

Es soll **kein Nebeneinander aus Top-Bar + App-Drawer + separatem TOC + Bereichs-Sonderlogiken** geben.

Stattdessen:

- **globale permanente Top-Bar** für Bereichswechsel
- **ein einheitliches Seitenpanel** für die bereichsinterne Navigation
- auf Mobile erscheint dieses Seitenpanel als **schlichtes Slide-in-Panel**, visuell ähnlich zur Zensical-Mobile-Navigation
- auf Desktop sitzt das Seitenpanel **nicht ganz links außen**, sondern **nah am zentrierten Inhalt**

Das Panel ist begrifflich **kein bloßes TOC im engen Sinn**, sondern eine ruhige, hierarchische Bereichsnavigation.

### 2.2 Unterschiede über Seitentypen, nicht über Navigation

Die Plattform unterscheidet sich primär über **Seitentypen**, nicht über völlig verschiedene Navigationsmuster.

Vorläufige Klassifikation:

- **Reading** – textzentrierte Seiten (Projekt, Methoden, Erklärseiten)
- **Workbench** – daten- und toolorientierte Forschungsseiten
- **Material** – didaktische Karten/Blätter für Unterrichtsmaterialien

Diese Klassifikation wird später separat ausdefiniert; sie ist hier zunächst nur als Strukturprinzip festgehalten.

### 2.3 Zensical als Basis, nicht MD3 als Dogma

PROMAT soll sich erkennbar an der Zensical-/Buchästhetik orientieren:

- ruhige Typografie
- zurückhaltende Navigation
- klare Tokens
- textzentriertes Layout
- CSS-Schriftzug statt PNG-Logo

MD3-Elemente dürfen nur dort erhalten bleiben, wo sie funktional nützlich sind.  
Die neue PROMAT-Oberfläche soll **nicht halb MD3, halb Corapan, halb Buch** wirken.

---

## 3. Design- und Systembasis

### 3.1 Gestalterische Grundlage aus Zensical

Die mitgelieferten Zensical-Dateien dienen als Referenzbasis für den Neuaufbau:

- `00_tokens.css` → zentrale Farb-, Flächen-, Border-, Focus- und Spacing-Tokens fileciteturn0file2
- `10_typography.css` → Typografiesystem mit Source Serif 4 für Lesetext und Inter/UI-Logik fileciteturn0file3
- `20_book.css` → Buchartige Layoutlogik, ruhige linke Navigation, ausgeblendete Sekundär-TOC fileciteturn0file4
- `30_components.css` und `40_custom.css` → gezielte Komponenten- und Projektanpassungen, nicht als ungeordnete Sammelstelle missbrauchen fileciteturn0file0turn0file1

### 3.2 Neue Farbidee für PROMAT

Für PROMAT soll die Palette in diese Richtung neu gesetzt werden:

- **Primärfarbe:** `#2b4460`
- **Sekundärfarbe:** `#a15a95`

Die Palette ist tokenbasiert in Light und Dark sauber zu definieren.  
Der bisherige Dark/Light-Stand gilt als unzureichend und soll beim Neuaufbau grundsätzlich neu geordnet werden.

### 3.3 Textlogo

Der Markenauftritt soll nicht über ein Bildlogo laufen, sondern über einen **CSS-Schriftzug** in der Top-Bar.

Vorgabe:

- zweizeilig
- linksbündig
- `Pronunciation` in Zeile 1
- `Matters` in Zeile 2
- `Matters` in Sekundärfarbe
- Schriftgewicht eher **semibold** als bold
- Ausgestaltung orientiert sich an der Zensical-Definition von `.md-header .site-title`

---

## 4. Globale Navigation (Top-Bar)

Die Top-Bar bleibt **permanent sichtbar** und enthält nur globale Bereichswechsel und Systemaktionen.

### 4.1 Reihenfolge

```text
Pronunciation Matters | Projekt | Forschung | Unterricht                    Dark/Light   Login
```

### 4.2 Regeln

- links steht das Textlogo
- danach folgen **schlichte globale Textlinks**, keine lauten Primärbuttons
- die Top-Bar dient **nur dem Wechsel zwischen Hauptbereichen**
- kein Sprachwechsel in der Top-Bar
- rechts sitzen:
  - Light/Dark-Toggle
  - Login-Button

### 4.3 Funktion der Hauptpunkte

- **Pronunciation Matters** → Startseite / globale Einstiegsseite
- **Projekt** → öffentlicher Projektbereich
- **Forschung** → Einstieg in den Forschungsbereich
- **Unterricht** → Einstieg in den Unterrichtsbereich
- **Login** → Zugang zu geschützten Bereichen bzw. Nutzerkontext

---

## 5. Seitenpanel (einheitliches Navigationssystem)

### 5.1 Grundidee

Neben der globalen Top-Bar gibt es **ein einziges Seitenpanel**, das in allen Bereichen nach demselben Prinzip funktioniert.

Es ist:

- auf Desktop sichtbar und fest positioniert
- auf Mobile ein Slide-in-Panel, ähnlich zur schlichten Zensical-Mobile-Navigation
- visuell ruhig und typografisch zurückhaltend
- bereichsbezogen, nicht global überladen

### 5.2 Position auf Desktop

Das Panel soll **nicht weit links am Rand kleben**, sondern näher am eigentlichen Inhaltsbereich stehen.

Ziel:

- kürzere Blickwege
- mehr Buchnähe
- keine Dashboard-Wirkung
- trotzdem genug Abstand, damit Forschungsseiten nicht gequetscht wirken

Es wird daher **eine feste Mittelposition** gewählt, die für alle Bereiche gleich bleibt.

### 5.3 Aufbau des Panels

Das Seitenpanel zeigt immer:

1. Kontextkopf
2. aktuellen Hauptbereich
3. Sprache, falls relevant
4. die bereichsinterne Navigation der aktuellen Ebene

Es gibt **vorerst keine zusätzliche Ebene 2** im Sinn einer weiteren TOC-Schachtelung.  
Das System bleibt zunächst bewusst flach.

---

## 6. Informationsarchitektur des Seitenpanels

### 6.1 Projekt

Kontext im Panelkopf:

```text
Pronunciation Matters
Projekt
```

Navigationspunkte:

- Über das Projekt
- Forschungsdesign
- Daten & Methodik
- Materialien (Metaebene)
- Team
- Publikationen
- Kontakt / Mitwirken

### 6.2 Forschung

Kontext im Panelkopf:

```text
Pronunciation Matters
Forschung
[Sprache]
```

Navigationspunkte:

- Sprache wählen
- Informanten
- Vergleich
- Phänomene
- Suche
- Korpus & Annotation
- Hinweise zum Zugang

Hinweis:

- „Sprache wählen“ kann als erste Seite oder Kontexteinstieg fungieren
- nach Sprachwahl bleibt die Sprache als Kontext im Panelkopf sichtbar
- Forschung ist research-first und darf entsprechend prominent als Hauptbereich erscheinen

### 6.3 Unterricht

Kontext im Panelkopf:

```text
Pronunciation Matters
Unterricht
[Sprache]
```

Navigationspunkte:

- Sprache wählen
- Einstieg Unterricht
- Phänomene
- Materialien
- Hinweise für Lehrkräfte
- Hintergrund & Einsatz im Unterricht

---

## 7. Sitemap (erste Arbeitsfassung)

Die Sitemap dient als Grundlage für das Anlegen neuer Seiten mit Dummytexten und korrekten Überschriften.

```text
/
├── Start
│
├── Projekt
│   ├── Über das Projekt
│   ├── Forschungsdesign
│   ├── Daten & Methodik
│   ├── Materialien (Meta)
│   ├── Team
│   ├── Publikationen
│   └── Kontakt / Mitwirken
│
├── Forschung
│   ├── Sprache wählen
│   ├── Französisch
│   │   ├── Informanten
│   │   ├── Vergleich
│   │   ├── Phänomene
│   │   ├── Suche
│   │   ├── Korpus & Annotation
│   │   └── Hinweise zum Zugang
│   ├── Spanisch
│   │   ├── Informanten
│   │   ├── Vergleich
│   │   ├── Phänomene
│   │   ├── Suche
│   │   ├── Korpus & Annotation
│   │   └── Hinweise zum Zugang
│   ├── Deutsch als Fremdsprache
│   │   ├── Informanten
│   │   ├── Vergleich
│   │   ├── Phänomene
│   │   ├── Suche
│   │   ├── Korpus & Annotation
│   │   └── Hinweise zum Zugang
│   └── Englisch
│       ├── Informanten
│       ├── Vergleich
│       ├── Phänomene
│       ├── Suche
│       ├── Korpus & Annotation
│       └── Hinweise zum Zugang
│
└── Unterricht
    ├── Sprache wählen
    ├── Französisch
    │   ├── Einstieg Unterricht
    │   ├── Phänomene
    │   ├── Materialien
    │   ├── Hinweise für Lehrkräfte
    │   └── Hintergrund & Einsatz im Unterricht
    ├── Spanisch
    │   ├── Einstieg Unterricht
    │   ├── Phänomene
    │   ├── Materialien
    │   ├── Hinweise für Lehrkräfte
    │   └── Hintergrund & Einsatz im Unterricht
    ├── Deutsch als Fremdsprache
    │   ├── Einstieg Unterricht
    │   ├── Phänomene
    │   ├── Materialien
    │   ├── Hinweise für Lehrkräfte
    │   └── Hintergrund & Einsatz im Unterricht
    └── Englisch
        ├── Einstieg Unterricht
        ├── Phänomene
        ├── Materialien
        ├── Hinweise für Lehrkräfte
        └── Hintergrund & Einsatz im Unterricht
```

---

## Sprachauswahl (Einstiegsseite)

Nach Auswahl eines Bereichs („Forschung“ oder „Unterricht“) erfolgt keine direkte Navigation in Inhalte, sondern zunächst eine **Sprachauswahl-Seite**.

### Ziel
- bewusste Auswahl eines Sprachprojekts
- Kontextualisierung (kein technischer Filter)

---

### Aufbau

Grid aus ruhigen Cards (ähnlich Admonitions / Buchstil):

**Pro Card:**
- Sprachname (z. B. „Französisch“)
- Kurzbeschreibung (1–2 Sätze)
- Projektleitung (Name)
- optional: kleines visuelles Element (zur Unterscheidung)

→ Klick öffnet den jeweiligen Bereich in dieser Sprache

---

### Verhalten

- Sprache wird als **Kontext gesetzt**, nicht als permanente Navigation
- danach erscheint die Sprache im Seitenpanel (Header-Kontext)
- Wechsel der Sprache erfolgt nicht primär über Navigation, sondern über Rückkehr zur Sprachauswahl

---

### Hinweis

Die Sprachauswahl ist eine **eigene Seite**, kein Dropdown und kein reines Navigationselement.

---

## 8. Seiten, die jetzt neu angelegt werden sollen

Bestehende Corapan-Template-Seiten sollen für diesen Neuaufbau **nicht maßgeblich weiterverwendet** werden.  
Stattdessen sollen neue Seiten mit deutscher Platzhalterprosa angelegt werden.

### 8.1 Allgemeine Regeln für Dummyseiten

Jede neue Seite soll zunächst enthalten:

- eine **korrekte Hauptüberschrift**
- zwei bis drei kurze deutsche Absätze Dummytext
- sinnvolle Zwischenüberschriften, wo nötig
- keine lorem-ipsum-artigen Fülltexte
- eher ruhige, sachliche Platzhaltertexte, die den späteren Zweck der Seite andeuten

### 8.2 Priorität beim Anlegen

Zuerst anlegen:

1. Start
2. alle Projektseiten
3. Forschung → Sprache wählen
4. Unterricht → Sprache wählen
5. danach je Sprache die Hauptseiten in Forschung und Unterricht

---

## 9. Inhaltliche Vorgaben für zentrale Seiten

### 9.1 Startseite

Die Startseite ist keine bloße Projektbeschreibung, sondern eine klare Einstiegsseite.

Sie soll knapp in die drei Bereiche führen:

- Projekt
- Forschung
- Unterricht

Der Ton darf akademisch sein, aber die Orientierung muss sofort klar sein.

### 9.2 Projektbereich

Die Projektseiten sollen eher reading-orientiert sein:

- textzentriert
- ruhig
- seriös
- nah an der Buchlogik

### 9.3 Forschungsbereich

Auch wenn die Navigation schlicht bleibt, sind diese Seiten funktional angelegt.  
Später werden hier toolartige Flächen, Filter, Listen, Player und Vergleichsansichten ergänzt.

In der ersten Ausbaustufe reichen Dummytexte, aber die Seitenüberschriften und die Navigationsstruktur müssen schon die spätere Arbeitslogik vorbereiten.

### 9.4 Unterrichtsbereich

Der Unterrichtsbereich bleibt öffentlich und richtet sich an Lehrkräfte.

Später soll hier insbesondere ein eigener Seitentyp für Materialien entstehen:  
didaktische, DINA4-nahe Karten/Blätter mit kompakten Texten, visuellen Elementen, Links und Audiobeispielen.

Für den jetzigen Schritt reicht es, diese Materiallogik strukturell vorzusehen, aber gestalterisch noch nicht vollständig auszuarbeiten.

---

## 10. Layout-Implikationen für die Umsetzung

### 10.1 Keine Detailreparatur des aktuellen Pfuschs

Die neue Umsetzung soll als **systematischer Rebuild** verstanden werden.

Das bedeutet:

- bestehende unruhige oder inkonsistente Corapan-Strukturen nicht nur nachschärfen
- keine weitere Flickarbeit an heterogenen Layoutresten
- klare Neuordnung von Tokens, Header, Navigation, Flächen und Seitengerüsten

### 10.2 Tokenbasierte Light/Dark-Logik

Light und Dark müssen neu und sauber über Tokens organisiert werden.

Zu vermeiden:

- verstreute Farbregeln
- komponentenspezifische Ad-hoc-Überschreibungen
- uneinheitliche Zustände zwischen Bereichen

### 10.3 Dokumentation nach jedem Run

Nach jedem Umbauschritt ist Dokumentation in `docs/layout/` zu aktualisieren bzw. neu zu ergänzen.

Ziel:

- nachvollziehbarer Umbau
- keine stillen Strukturänderungen ohne schriftliche Spur
- klare Projektbasis für spätere Iteration

---

## 11. Konkrete Umsetzungsrichtung für den nächsten Build-Schritt

Der nächste Umbau soll mindestens Folgendes leisten:

1. neue Top-Bar gemäß diesem Plan
2. neues einheitliches Seitenpanel gemäß diesem Plan
3. neue Farbtokens für PROMAT
4. saubere Light/Dark-Definition
5. neues Textlogo auf CSS-Basis
6. neue Seitenstruktur mit deutschen Dummytexten
7. Ablösung der bisherigen Corapan-Seiten als primäre Layoutgrundlage
8. begleitende Dokumentation in `docs/layout/`

---

## 12. Kurzfassung der Architekturentscheidung

PROMAT erhält:

- **eine permanente globale Top-Bar**
- **ein einziges bereichsinternes Seitenpanel**
- **keine zusätzliche Panel-Ebene vorerst**
- **eine ruhige Zensical-nahe Formensprache**
- **einen strukturellen Neuaufbau statt weiterer Reparaturarbeit**

Die spätere Differenzierung erfolgt über Seitentypen, nicht über konkurrierende Navigationssysteme.
