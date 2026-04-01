# PROMAT Session Storage Logic Alignment 02

Datum: 2026-04-01

## Ziel

Noch fehlende explizite Hinweise zur Audio-, Alignment- und Item-Logik in Datenraum-, Seed- und Metadaten-Doku nachziehen.

## Umgesetzter Stand

- `data/README.md` nennt `raw`, `source`, `derived`, `alignment` und `items` jetzt direkt und normativ.
- Seed-Doku und Seed-Metadaten nennen jetzt explizit, dass die spanischen Beispiel-WAVs `source` sind und keine echten `raw`-Master vorliegen.
- Die Projektspezifikation nennt jetzt die `alignment/*.json`-Beispiele und die Pipeline-Logik noch expliziter, inklusive Ausschluss von `silent` aus der reduzierten Alignment-JSON.
- `.github` wurde in diesem Nachschaerfungslauf nicht erneut geaendert, weil die noetigen Architekturregeln dort bereits aus dem vorherigen Governance-Lauf bestehen.

## Verifikation

- Spanische Dev-Session-Metadaten erneut aus dem Seed aktualisiert.
- Relevante Doku-Dateien gegen die verlangten Strukturentscheidungen abgeglichen.