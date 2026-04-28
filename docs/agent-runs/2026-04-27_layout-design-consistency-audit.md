# PROMAT Layout and Design Consistency Audit

Datum: 2026-04-27
Scope: globale Shell, Templates, CSS-Architektur, Design-Tokens, wiederverwendete Komponentenfamilien, bilinguale UI-Konsistenz
Artefakttyp: nicht-normativer Auditbericht

## Executive Summary

Die UI ist visuell nicht ungeordnet, aber systemisch noch nicht konsolidiert. PROMAT betreibt aktuell zwei uebereinanderliegende Designsprachen:

- ein juengeres PROMAT-System mit `pm-*`-Klassen und Tokenfiles `00_tokens.css`, `10_typography.css`, `20_layout.css`, `30_components.css`, `40_cards.css`
- ein parallel weiter mitgefuhrtes `md3`-System mit eigenem Komponenten- und Layoutstapel

Das Ergebnis ist eine App, die an vielen Stellen bereits bewusst gestaltet wirkt, deren Designsystem aber noch nicht eindeutig kanonisiert ist. Fuer Nutzende ist das oft noch akzeptabel. Fuer Wartung, UI-Konsistenz und spaetere Produktreife ist es ein klares Risiko.

Gesamturteil: visuell brauchbar bis stellenweise stark, systemisch aber nur mittel konsistent.

## Positive Befunde

### 1. Starkes Token-Fundament im PROMAT-Layer

`app/static/css/00_tokens.css` zeigt klare Systemarbeit:

- definierte Surface-, Status- und Spacing-Tokens
- lernerspezifische Level-Farbskala
- eigener nativer Accent fuer Native-Speaker-Kontexte
- sinnvolle Trennung zwischen UI-Font, Lesetypografie und Komponentenwerten

Das ist deutlich reifer als ein rein seitenlokal gewachsenes CSS.

### 2. Forschungsspezifische Komponentenfamilien sind bereits eigenstaendig

Im `pm-*`-Layer sind Research-spezifische Familien wie Speaker Cards, Player-, Comparison- und Phenomena-Komponenten klar erkennbar. Das ist ein gutes Zeichen, weil die App dadurch nicht nur generische CRUD-Oberflaechen reproduziert.

### 3. Viele neuere produktive Auth-Seiten nutzen bereits die zentrale Uebersetzungsschicht

Zum Beispiel `app/templates/auth/login.html` und `app/templates/auth/access_request.html` binden sichtbare Texte ueber `t(...)` ein. Das zeigt, dass die gewuenschte Richtung fuer neue oder modernisierte Seiten bereits funktioniert.

## Kritische Findings

### D1. Zwei aktive Designsysteme erzeugen dauerhafte Konsistenzschulden

Prioritaet: P1

Aktuell laufen `pm-*`, `md3-*` und teilweise `promat-*` gleichzeitig produktiv. Das betrifft nicht nur historische Restklassen, sondern auch aktiv geladene CSS-Dateien in `app/templates/base.html`.

Folgen:

- Karten, Buttons, Layout- und Dialogfamilien existieren parallel
- visuelle Entscheidungen koennen ueber Source-Order statt ueber klare Systemzustaendigkeit entschieden werden
- Entwickler muessen haeufig erst rekonstruieren, welche Familie fuer eine Seite kanonisch ist

Das ist der groesste Designsystem-Risikofaktor der App.

Empfehlung:

1. kanonische Familien pro UI-DomAene explizit festlegen
2. `md3` als Foundation oder als Altlast entscheiden, aber nicht dauerhaft als gleichrangiges Zweitsystem weitertragen
3. gemischte Komponentenverwendung systematisch reduzieren

### D2. Karten- und Interaktionsfamilien kollidieren

Prioritaet: P1

`app/static/css/40_cards.css` fuehrt `.md3-card`, `.pm-card` und `.promat-card` sichtbar gemeinsam. Aehnlich existieren bei Buttons und Aktionsmustern parallele Familien.

Folgen:

- unklare Ownership pro Komponente
- Cascade-/Specificity-Risiko
- erschwerte visuelle Regressionstests

Empfehlung:

- eine aktive Kartenfamilie definieren und die anderen auf Migrations- oder Kompatibilitaetsstatus reduzieren

### D3. Fertige bilinguale UI ist nicht konsistent umgesetzt

Prioritaet: P1

Trotz klarer Governance-Regeln enthalten mehrere produktive Templates sichtbare hartcodierte deutsche Texte, etwa:

- Error-Seiten unter `app/templates/errors/`
- Footer in `app/templates/partials/footer.html`
- weitere produktive Templates mit direkt geschriebenen Labeln

Zusaetzlich existieren in Python-Buildern lokale `if ui_lang == "de" else ...`-Strings fuer UI-Copy.

Das ist nicht nur ein i18n-Thema, sondern ein Designsystem-Thema: Copy, Labeling und UI-Konsistenz sind Teil der Oberflaechenarchitektur.

Empfehlung:

1. Shared Partials und Error-Seiten zuerst bereinigen
2. sichtbare UI-Copy als systemische Design-Ressource behandeln, nicht als lokale Builder-Beilage

### D4. CSS-Load-Order ist fragil

Prioritaet: P1

`app/templates/base.html` laedt gleichzeitig kritisches Inline-CSS, MD3-Foundation, MD3-Komponenten und danach PROMAT-Overrides. Das funktioniert aktuell offenbar hauptsaechlich, weil spaetere Regeln fruehere ueberschreiben.

Folgen:

- Erfolg basiert teilweise auf Reihenfolge statt auf klarer Abstraktion
- Shared-Refactorings werden riskanter
- tote oder halbgenutzte Assets bleiben leichter unsichtbar aktiv

### D5. Fokusdarstellung wird waehrend Hydration unterdrueckt

Prioritaet: P1

In `app/templates/base.html` werden `:focus` und `:focus-visible` waehrend des Hydration-Zustands unterdrueckt.

Risiko:

- wenn der Zustand haengenbleibt oder JS nicht korrekt raeumt, verlieren Keyboard-Nutzende sichtbare Orientierung

Das ist ein Accessibility- und Konsistenzproblem fuer die gesamte App-Shell.

## Weitere relevante Findings

### D6. Breakpoints und Responsivitaetslogik sind nicht zentral genug

Prioritaet: P2

Im CSS tauchen mehrere unterschiedliche Breakpoint-Familien auf, etwa um 979 px, 899 px, 719 px und 599 px. Das ist nicht automatisch falsch, aber ohne klare zentrale Regel werden Layoutwechsel schwerer nachvollziehbar.

### D7. Harte Farbwerte leben noch ausserhalb des Token-Layers

Prioritaet: P2

Insbesondere Kartenakzente und einzelne Mischfarben liegen noch direkt im Komponenten-CSS. Damit wird ein Teil der semantischen Farbe wieder aus dem Token-System herausgezogen.

### D8. Legacy- oder Beispieloberflaechen sind sprachlich gemischt

Prioritaet: P2

Unter `_md3_skeletons` existieren Beispiel-/Skelett-Templates mit spanischen, deutschen und englischen Texten. Solange diese nicht produktiv sind, ist das weniger kritisch. Sie tragen aber zur gestalterischen Unklarheit bei und koennen bei Wiederverwendung falsche Muster weitergeben.

### D9. Einige produktive Auth-/Account-Seiten sind noch MD3-lastig und textlich hartcodiert

Prioritaet: P2

Teile des Account-Bereichs zeigen noch den aelteren Stil aus MD3-Komponenten plus direkter Copy. Dadurch wirkt der Auth-Bereich nicht vollstaendig aus einem Guss.

## Gestalterisches Gesamtbild

PROMAT hat bereits eine erkennbare eigene Sprache in den juengeren Research- und Promat-Komponenten:

- ruhigere, inhaltlich orientierte Cards
- stringente Research-Metadatenrhythmen
- gute Spezialisierung fuer Speaker-/Player-/Comparison-Kontexte

Diese Staerken werden jedoch systemisch abgeschwaecht durch:

- parallele Alt-Familien
- unklare Shared-Komponenten-Ownership
- inkonsistente Copy- und i18n-Disziplin
- fragile globale CSS-Reihenfolge

## Priorisierte Empfehlungen

### Phase 1: Shared Designsystem klarziehen

1. Definieren, welche Komponentenfamilien kanonisch sind.
2. Karten-, Button- und Dialogfamilien auf aktive und Legacy-Pfade reduzieren.
3. `base.html`-Load-Order und Asset-Ownership dokumentieren und bereinigen.

### Phase 2: Bilinguale und Shared UI konsolidieren

4. Footer, Error-Seiten und weitere Shared Partials auf zentrale Uebersetzung ziehen.
5. sichtbare Hardcodings in produktiven Templates systematisch abbauen.

### Phase 3: Token- und Responsive-System haerten

6. harte Farbwerte in Tokens ueberfuehren.
7. Breakpoint-Strategie explizit zentralisieren.
8. Hydration-Focus-Suppression sicherheitshalber neu pruefen.

## Audit-Fazit

Die App hat bereits ein deutlich besseres UI-Fundament als ein beliebiges zusammenkopiertes Admin-Frontend. Der eigentliche Nachholbedarf liegt nicht im visuellen Geschmack, sondern in der disziplinierten Systemfuehrung. Solange `pm-*` und `md3-*` gleichrangig nebeneinanderleben und produktive Copy nicht zentralisiert ist, bleibt die Designkonsistenz nur teilweise abgesichert.

Mit einer klaren Systementscheidung und konsequenter Shared-UI-Bereinigung kann PROMAT jedoch relativ effizient in einen deutlich reiferen Zustand ueberfuehrt werden.