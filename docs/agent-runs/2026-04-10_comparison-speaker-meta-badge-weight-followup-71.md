# Comparison Speaker Meta Badge Weight Follow-up

Datum: 2026-04-10

## Ziel

Die Vergleichs-Sprecherinfos in Auswahl und Matrix visuell angleichen: Level- und L1-Badges nicht fett darstellen und `L1: ...` an beiden Stellen als neutralen grauen Badge führen.

## Consulted Sources

- `app/static/css/30_components.css`
- `app/static/js/pages/research-comparison.js`
- `app/templates/pages/sample_page.html`
- `docs/agent-runs/_template.md`

## Geänderte Bereiche

- `app/static/css/30_components.css`

## Wichtige Entscheidungen

- Die Angleichung blieb rein im Comparison-CSS; das bestehende Speaker-Card-Markup in Auswahl und Matrix war bereits gemeinsam genug.
- Die Meta-Zeile und ihre Badges wurden explizit auf nicht-fette Gewichtung gesetzt, damit Level- und L1-Angaben nicht je nach Kontext stärker wirken.
- Das L1-Badge nutzt jetzt dieselbe neutrale graue Oberflächenlogik in beiden Comparison-Kontexten.

## Abweichungen

- Keine Abweichung von aktiven Regeln; nur visuelle Konsistenz im bestehenden Comparison-Sprecherkarten-System.

## Verifikation

- CSS-Diagnostik für die geänderte Datei.
- Kein Markup- oder Logikumbau erforderlich.

## Offene Punkte

- Keine browserseitige Screenshot-Prüfung in diesem Run.

## Nächste sinnvolle Schritte

- Bei Gelegenheit die Auswahl und Matrix im Browser nebeneinander gegenprüfen, ob Level- und L1-Badges nun identisch ruhig wirken.