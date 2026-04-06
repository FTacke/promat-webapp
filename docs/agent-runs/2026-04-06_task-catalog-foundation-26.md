# Task Catalog Foundation 26

Datum: 2026-04-06

## Ziel

Die kanonische corpus-spezifische Task-Katalog-Struktur als Inhalts-Source-of-Truth für Research-Player-Inhalte und spätere Produktionspipelines einführen, ohne bereits MP3- oder JSON-Produktionscode zu bauen.

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

## Geänderte und neue Dateien

- `data/config/research_player/README.md`
- `data/config/research_player/spanish/task_catalogs/wordlist.json`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/runbooks/research-wordlist-production.md`
- `scripts/research_data_intake/README.md`
- `docs/agent-runs/2026-04-06_task-catalog-foundation-26.md`

## Ergebnis

- `data/config/research_player/{language}/task_catalogs/` ist jetzt als kanonische Struktur für corpus-spezifische Task-Kataloge eingeführt.
- `data/config/research_player/spanish/task_catalogs/wordlist.json` ist jetzt der kanonische spanische `wordlist`-Katalog.
- Dieser Katalog trägt für die spanische Wortliste die inhaltliche Source of Truth für Reihenfolge, `item_id`, `item_number` und exakte `text`-Werte.
- Die Specs regeln jetzt ausdrücklich, dass session-spezifische `alignment/{task}.json`-Artefakte aus Task-Katalog plus session-spezifischen Alignment- und Audiodaten abgeleitet werden.
- Dieselbe Struktur ist normativ bereits für einen späteren `text`-Katalog vorbereitet.
- Task-Kataloge sind außerdem als spätere Grundlage für rohe Materialansichten in der Webapp vorbereitet, ohne dadurch automatisch Public-Freigaben auszulösen oder eine zweite Materialquelle aufzubauen.

## Bewusst nicht umgesetzt

- Keine MP3-Produktionslogik.
- Keine Split-MP3-Produktionslogik.
- Keine Erzeugung von session-spezifischem `alignment/wordlist.json`.
- Kein künstlich erfundener `text`-Katalog ohne belastbare Eingangsgrundlage.

## Verifikation

- Der spanische `wordlist`-Katalog wurde aus der 92-zeiligen kanonischen Wortliste strukturiert aufgebaut.
- Die Specs und das Runbook wurden auf Katalog-basierte Ableitungslogik umgestellt.
- Die Trennung zwischen Kataloginhalt, session-spezifischen Zeitgrenzen, Split-Exportgrenzen und späterer Download-Benennung wurde konsistent gehalten.