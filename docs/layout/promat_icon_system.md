# PROMAT Icon System

## Ziel

Die PROMAT-Shell verwendet fuer Navigation, Panel und Meta-Aktionen jetzt eine einheitliche Outline-Iconfamilie. Die Loesung bleibt nah an den Erkenntnissen aus der Zensical-Analyse, setzt fuer die Shell aber bewusst auf einen robusten, lokalen Mechanismus.

## Strategische Entscheidung

Zensical arbeitet hybrid:

- Theme-seitig tauchen Lucide-orientierte Outline-Icons auf
- projektintern ist der stabile Mechanismus lokal eingebettetes SVG via `data:image/svg+xml` und `mask-image`

Fuer PROMAT gilt deshalb in der Shell:

- zentrale Icon-Tokens in CSS
- lokales SVG pro Icon als `data:image/svg+xml`
- Ausgabe per `mask-image` und `currentColor`

Das vermeidet uneinheitliche Iconquellen, haelt Light/Dark und State-Farben einfach steuerbar und passt stilistisch zur editoriellen, nicht-appigen Shell.

## Token-Logik

Die Shell-Icons liegen als Variablen in der Token-Schicht:

- `--pm-icon-project`
- `--pm-icon-research`
- `--pm-icon-teaching`
- `--pm-icon-menu`
- `--pm-icon-theme-light`
- `--pm-icon-theme-dark`
- `--pm-icon-login`
- `--pm-icon-account`

## Bereichsicons

- Projekt: sachliche Projektmappe
- Forschung: Mikroskop
- Unterricht: offenes Buch

Zusaetzlich existieren neutrale Shell-Icons fuer Start und Rechtliches, damit auch diese Panel-Koepfe nicht aus der Familienlogik herausfallen.

## State-Kopplung

Da die Icons per `currentColor` gerendert werden, folgen sie automatisch denselben Farbregeln wie Text und States:

- neutrales Grau im Ruhezustand
- etwas dunkler bei Hover
- Akzentton bei aktiver Navigation

Dadurch bleiben Panel-Hierarchie, Hover und Active-State visuell gekoppelt, ohne dass Icons extra eingefaerbt oder als Badges behandelt werden.
