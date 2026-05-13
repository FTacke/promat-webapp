# 2026-05-12 Teaching Topic Section Heading Marker

## Scope

Mini-CSS-Run fuer Teaching-Topic-Seiten: echte Topic-Section-H2s sollen visuell etwas staerker als narrative Abschnittsmarker wirken, ohne Hub-Gruppen, Card-Titel, Box-Titel oder H1 zu beruehren.

## Umsetzung

- `app/static/css/30_components.css`
  - Topic-Section-Heading-H2s erhalten nur auf Topic-Seiten einen dezenten Secondary-Accent-Marker per `::after`
  - der Marker ist auf die echte Topic-Section-H2-Klasse `pm-teaching-section-heading__title` beschraenkt
  - Hub-Seiten, Card-Titel, Box-Titel und H1 bleiben unveraendert

## Validierung

### Browser-QA

Geprueft auf:

- `/de/teaching/spanish/which-pronunciation`

Ergebnis:

- Topic-Section-H2s zeigen einen subtilen Marker
- Hub-/Card-/Box-Titel bleiben unveraendert
- Marker wirkt auf Desktop und Mobile dezent

Screenshot-Artefakt:

- `C:\dev\promat\desktop_screenshot.png`
