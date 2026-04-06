# Wordlist Production Rules Finalization 25

Datum: 2026-04-06

## Ziel

Die letzten offenen Detailregeln für den kommenden `wordlist`-Implementierungs-Run verbindlich festziehen, ohne bereits MP3-, Split- oder JSON-Produktionscode zu bauen.

## Consulted Sources

- `AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/runbooks/research-wordlist-production.md`
- `docs/agent-runs/2026-04-06_wordlist-production-preparation-24.md`
- `docs/model_mds/PROMAT_ JSON-Aufbau.md`
- `docs/model_mds/01_Spanisch_Wortliste.pdf`
- `docs/model_mds/spanish_wordlist.txt`

## Geänderte Dateien

- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/runbooks/research-wordlist-production.md`
- `docs/agent-runs/2026-04-06_wordlist-production-rules-finalization-25.md`

## Festgezogene Regeln

- Das `wordlist`-`item_id`-Schema ist jetzt für den aktuellen spanischen Produktionspfad verbindlich als `wl_001` bis `wl_092` festgelegt.
- `item_number` ist die fachlich sichtbare Nummer `1` bis `92`; `item_id` ist die stabile technische ID, deterministisch aus dieser Nummer abgeleitet.
- Die PDF ist als Referenz für Reihenfolge und Nummerierung festgehalten.
- Die TXT ist als autoritative Zeichenkettenquelle für die exakten Item-Texte festgehalten.
- `alignment/wordlist.TextGrid` liefert Zeitgrenzen und nicht-silence-Reihenfolge, überschreibt aber nicht die kanonischen Texte.
- Nicht exakt `92` nicht-silence-Intervalle sind jetzt ausdrücklich ein Fehlerfall.
- Interne Split-Pfade und spätere Download-Dateinamen sind sauber getrennt dokumentiert.
- Der vorbereitete Download-Dateivertrag enthält mindestens `person_id`, `task`, `item_id` und die lesbare Textkomponente.

## Bewusst nicht umgesetzt

- Keine Implementierung der MP3-Erzeugung.
- Keine Implementierung der Split-MP3-Erzeugung.
- Keine Implementierung des JSON-Exports.
- Keine Einführung künstlicher Vorab-Pipelines für `text` oder `interview`.

## Verifikation

- Pflichtquellen und Arbeitsquellen gegengelesen.
- Die Rohwortliste als aktuelle 92-zeilige kanonische Textquelle geprüft.
- Die Specs und das Runbook auf Konsistenz zwischen interner Speicherlogik, Download-Benennung und `wordlist`-Vertrag abgeglichen.