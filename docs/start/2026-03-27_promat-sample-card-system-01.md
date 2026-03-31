# PROMAT Sample Card System 01

## Anlass

Die Sample-Seite wurde von einer reinen Testsammlung zu einer konsolidierten Referenzseite fuer das PROMAT-Layout-System ueberarbeitet.

## Aktueller Zustand

- `/sample` bleibt die zentrale Pruefseite fuer Layout, Surface-Logik und Komponententrennung
- die Seite zeigt jetzt in fester Reihenfolge:
  - Landing Entry Cards
  - Corpus Cards fuer Forschung
  - Corpus Cards fuer Lehre
  - ruhige Info-Panels
  - bestehende Admonitions
  - einen kombinierten Beispielbereich

## Kartentypen

- `pm-card--entry`
  - kuratierte Einstiegskarten fuer Projekt, Forschung und Unterricht
  - Standard-Layout: flacher Bildstreifen oben, Titel darunter, ein kurzer Teasersatz, CTA
  - eigene Landing-Geometrie fuer 2er- oder 3er-Gruppen unter einem zentralen Logo
  - reale Bildbeispiele fuer Projekt, Forschung und Unterricht sind auf `/sample` eingebunden
  - Bilder werden als flache, kontrollierte Bildstreifen mit ruhigem Crop integriert
  - jede gezeigte Entry-Card fuehrt den CTA `Oeffnen ->` konsistent am unteren Kartenrand
  - CTA-Farblogik ist jetzt systematisch organisiert: Projekt und Forschung nutzen `var(--promat-primary)`, Unterricht nutzt `var(--promat-wordmark-accent)`
  - die Varianten sind auf `/sample` explizit als Variante A bis D benannt und direkt vergleichbar gemacht
  - keine linken Bildspalten mehr; Labels dienen nur der Sample-Praesentation und nicht als Kartenbestandteil
  - Overlay-Titel bleibt ausschliesslich eine kontrollierte Projekt-Sondervariante mit Scrim und ist sichtbar als Testfall markiert
- `pm-card--corpus pm-card--corpus-research`
  - neutral, ruhig, textnah, leicht raised
  - keine Sprachfarbe, keine Hintergrundtoenung
- `pm-card--corpus pm-card--lang-*`
  - gleiche Grundflaeche wie Forschung
  - sprachliche Differenzierung nur ueber gedaempften Top-Akzent und CTA-Farbe

## Abgrenzung der Systeme

- Cards bleiben Navigations- und Einstiegselemente mit CTA am unteren Rand
- `pm-panel--info` bleibt eine ruhigere Informationsflaeche ohne CTA-Optik, Marker oder Bildzone
- Admonitions bleiben didaktische Inhaltskomponenten und wurden nicht neu gestaltet
- Unterschiede werden ueber Surface, Rhythmus und semantische Rolle lesbar gemacht, nicht ueber lautere Effekte

## Formale Entscheidungen

- Cards, Panels und Admonitions bleiben klar getrennte Systeme innerhalb einer gemeinsamen Designfamilie
- Forschung und Lehre teilen dieselbe Raised-Surface; Lehre fuegt nur einen kontrollierten Sprachakzent hinzu
- Entry-Cards sind ein eigener horizontaler Landing-Typ mit reduzierten Inhalten: Titel, ein Teasersatz, CTA
- Entry-Cards unterscheiden sich von Corpus Cards ueber Geometrie, Top-Image-Layout und CTA-Farblogik, nicht ueber lautere Flaechen
- Hover bleibt ruhig: keine Lifts, keine staerkeren Schatten, keine Sonderfaelle pro Karte

## Betroffene Dateien

- `app/templates/pages/sample_page.html`
- `app/static/css/20_layout.css`
- `app/static/css/10_typography.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`