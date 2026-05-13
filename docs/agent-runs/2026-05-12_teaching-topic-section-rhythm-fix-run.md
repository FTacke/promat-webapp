# 2026-05-12 Teaching Topic Section Rhythm Fix Run

## Scope

Kleiner CSS-Fix fuer den Teaching-Topic-Section-Rhythmus auf der Pilotseite `which-pronunciation`.

Ziel war, den Abstand zwischen echten Sections klar vom internen Abstand innerhalb einer Section zu trennen und dabei insbesondere zu verhindern, dass die Intro-Section einen zusaetzlichen 3rem-Abstand unter dem Header bekommt.

## Umsetzung

- `app/static/css/30_components.css`
  - Ursache war die kombinierte Regel auf `.pm-teaching-topic-sections` mit `gap: 3rem` plus `margin-top: 3rem`
  - der Container nutzt jetzt `gap: 0`, damit kein pauschaler Extra-Abstand vor der ersten Intro-Section entsteht
  - jede `.pm-teaching-topic-section` behaelt intern `gap: 1.5rem`
  - der Aussenabstand wird jetzt nur noch ueber `.pm-teaching-topic-section + .pm-teaching-topic-section { margin-top: 3rem; }` gesetzt
  - die Intro-Section wird explizit auf `margin-top: 0` und `padding-top: 0` gehalten
  - die Topic-Section-Grids bleiben intern bei `row-gap: 1.5rem`

## Validierung

Geprueft auf:

- `/de/teaching/spanish/which-pronunciation`

Gepruefte Punkte:

- Header -> Intro-Section ohne zusaetzlichen 3rem-Section-Offset
- Intro -> Seseo-Section mit ca. 3rem Abstand
- innerhalb der Seseo-Section ca. 1.5rem Rhythmus zwischen Titel, Text und Karten
- Seseo -> Hoervergleich mit ca. 3rem Abstand
- Mobile bleibt sauber gestapelt