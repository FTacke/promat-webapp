# PROMAT Container System

## Grundlage

Die Container-Schicht fuer PROMAT wurde ausschliesslich aus den Analysen in `docs/zenscial_base/` und den konkreten Zensical-Overrides in `docs/layout/zensical_template/` abgeleitet. Massgeblich waren dabei:

- `container_baseline.md` fuer Geometrie und Typometrie der neutralen Basis
- `spacing_system.md` fuer die formale Skala `12 / 16 / 20 / 24 / 28 / 32 / 48 / 60`
- `admonition_system.md` fuer die Trennung zwischen neutralen Containern und semantischen Admonitions
- `promat_container_proposal.md` fuer die formale `pm-*`-Familie
- `20_book.css` und `30_components.css` fuer Background-, Header- und Logo-Abgleich

## Neue CSS-Strukturen

Die neue Schicht liegt in den bestehenden PROMAT-Dateien, aber mit einer eigenen `pm-*`-Benennung:

- `app/static/css/00_tokens.css`
  - exakte `--book-*`-Bruecke fuer Light/Dark nach Zensical
  - neue Familien `--pm-surface-*`, `--pm-border-*`, `--pm-radius-*`, `--pm-space-*`, `--pm-type-*`
- `app/static/css/20_layout.css`
  - neue Layoutklassen `pm-content`, `pm-stack`, `pm-grid`, `pm-panel`
  - Rhythmus jetzt auf `20 / 24 / 28 / 48 / 60` aus der Analyse ausgerichtet
- `app/static/css/40_cards.css`
  - neue visuelle Basen `pm-container`, `pm-card`, `pm-admonition`
  - Varianten `pm-container--neutral`, `pm-container--tinted`, `pm-container--interactive`
  - Varianten `pm-card--selection`, `pm-card--material`, `pm-card--interactive`

## Ersetzte alte Strukturen

Im öffentlichen Seitenmodell wurden die bisherigen, lose benannten Kartenstrukturen ersetzt:

- `promat-card-grid` wurde im Template auf `pm-grid` umgestellt
- `promat-card` wurde für die öffentlichen Einstiegs- und Metakarten durch `pm-card` ersetzt
- Auswahlkarten fuer Forschung und Unterricht laufen jetzt explizit ueber `pm-card--selection`

Die alten PROMAT-Klassen bleiben in CSS punktuell als Kompatibilitaetsbruecke erhalten, damit keine Nebenwirkung auf vorhandene MD3-/Auth-Flaechen entsteht.

## Baseline-Regeln

Die neutrale Basis folgt der gemessenen `summary`-Geometrie:

- Radius: `8px`
- Border: `1px solid`
- Shadow: `none`
- Padding: `22px 24px 20px 24px`
- Container-Typo: `15.6px / 25.74px`

Die semantische Admonition-Schicht folgt weiterhin der kompakten Wrapper-Basis:

- horizontales Wrapper-Padding: `16px`
- vertikaler Rhythmus: `24.375px`
- Rails nur fuer `expand`, `hoermal`, `weiterlesen`

## Grid.cards

Die Basis-Analyse hat gezeigt, dass geerbte `.grid.cards`-Muster nicht als Primitaerquelle fuer PROMAT-Karten taugen. Deshalb wurde in `app/static/css/20_layout.css` eine scoped Neutralisierung fuer `.pm-content .grid.cards` eingefuehrt:

- kein Shadow
- `8px` Radius
- `1px` Border
- paper-nahe Surface statt Shadow-First-Karte

Damit wurde `.grid.cards` nicht global abgeschaltet, sondern innerhalb der neuen PROMAT-Content-Schicht kontrolliert uebersteuert.

## Header und Hintergrund

Der Shell-Abgleich wurde auf die Zensical-Vorgaben gezogen:

- `body` und Shell-Hintergrund laufen ueber `--book-bg`
- die Top-Bar nutzt denselben Hintergrund und nur die Zensical-Trennlogik `border-bottom: 1px solid var(--book-border)`
- Schatten wurden aus der Top-Bar entfernt

## Logo-Typografie

Die Wortmarke im Top-Bar-Brandblock wurde auf die Werte aus `docs/layout/zensical_template/30_components.css` gesetzt:

- `font-family: var(--book-font-ui)`
- `font-size: 0.8rem`
- `gap: 0.15rem`
- `font-weight: 700`
- `letter-spacing: -0.01em`
- `line-height: 1.1`
- `white-space: nowrap`

Der Akzent folgt wie im Zensical-Vorbild:

- Light: `--book-title-accent-dark`
- Dark: `--book-title-accent`