# PROMAT Typography System

## Ziel

Die öffentliche PROMAT-Shell trennt Typografie jetzt formal in UI-, Display- und Reading-Ebenen. Damit entstehen Grössenverhältnisse und Schriftwechsel nicht mehr implizit aus Einzelregeln, sondern aus einer festen `pm-*`-Tokenfamilie.

## Token-Gruppen

- `--pm-type-brand-*`: Wortmarke und Brandtitel
- `--pm-type-nav-*`: obere Bereichsnavigation
- `--pm-type-panel-*`: linkes Panel und TOC-Links
- `--pm-type-meta-*`: Meta-Texte, Toggle-Beschriftungen, kleine Status- und Kontexttexte
- `--pm-type-display-*`: primaere H1-Ebene
- `--pm-type-reading-*`: Intro, Body, H2, H3 und textnahe Eyebrows
- `--pm-type-card-*`: Card-Eyebrow, Card-Title, Card-Body und Card-Link

## Regel

- Sans-Serif bleibt auf Brand, Navigation, Panel-Chrome und H1 beschraenkt
- unterhalb der H1 laeuft die textnahe Hierarchie in der Book-Serif

Konkret bedeutet das:

- H1: Sans-Serif
- H2: Book-Serif
- H3: Book-Serif
- Body: Book-Serif
- Listen: Book-Serif
- Card-Title: Book-Serif
- Card-Body: Book-Serif
- Card-Link: Book-Serif
- Page- und Card-Eyebrows: Book-Serif

## Layout-Kopplung

Die Typo-Skala ist an zwei Layoutzonen gekoppelt:

- `.pm-reading` fuer den ruhigen Lesesatzspiegel
- `.pm-feature-band` fuer breitere, zentrierte Karten- und Strukturbausteine

Damit kann die Reading-Typografie konstant bleiben, waehrend Feature-Bands mehr Breite erhalten, ohne die textliche Ruhe zu verlieren.