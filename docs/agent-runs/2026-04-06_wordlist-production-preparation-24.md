# Wordlist Production Preparation 24

Datum: 2026-04-06

## Ziel

Den Repo-Zustand für den kommenden Implementierungs-Run zur `wordlist`-Produktion vorbereiten, ohne die eigentliche MP3-, Split- oder JSON-Produktionslogik bereits zu bauen.

## Consulted Sources

- `AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/spec/intake-workbook.md`
- `docs/model_mds/speech_text_sync.md`
- `docs/model_mds/PROMAT_ JSON-Aufbau.md`
- `scripts/AGENTS.md`

## Geänderte Bereiche

- `scripts/AGENTS.md`
- `scripts/research_data_intake/README.md`
- `scripts/research_data_intake/AGENTS.md`
- `scripts/research_data_intake/session_setup/seed_dev_spanish_example_sessions.py`
- `scripts/research_data_intake/session_setup/dev_spanish_example_sessions.json`
- `scripts/research_data_intake/audio_conversion/.gitkeep`
- `scripts/research_data_intake/item_split/.gitkeep`
- `scripts/research_data_intake/alignment_export/.gitkeep`
- `scripts/research_data_intake/import/.gitkeep`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/runbooks/dev-spanish-example-seed.md`
- `docs/runbooks/research-wordlist-production.md`
- `docs/agent-runs/2026-04-06_wordlist-production-preparation-24.md`

## Repo-Struktur nach diesem Run

- `scripts/research_data_intake/` ist jetzt die Zielwurzel für Intake- und Ableitungsschritte zu Forschungs-Sessiondaten.
- Der bisherige Dev-Seed unter `session_setup/` wurde in diese neue Wurzel verschoben.
- Leere Zielbereiche für `audio_conversion/`, `item_split/`, `alignment_export/` und `import/` sind angelegt, damit der nächste Run seine Produktionsschritte dort systematisch einsortieren kann.
- Allgemeine Dev-Skripte und `export_to_public/` bleiben bewusst außerhalb dieser Wurzel.

## Vorbereitete verbindliche Regeln für den nächsten `wordlist`-Run

- `wordlist` bleibt der erste reale vertikale Produktionspfad.
- Die Zielartefakte sind `derived/wordlist.mp3`, `items/wordlist/{item_id}.mp3` und `alignment/wordlist.json`.
- Für `wordlist` ist `split_mp3` pro Item als explizite Korrespondenz verbindlich vorbereitet.
- `item_number` wird für die aktuelle Wortliste aus der Reihenfolge der nicht-silence-Intervalle im `wordlist.TextGrid` abgeleitet.
- Silence-Intervalle sind keine Items.
- Kanonische Annotationsgrenzen bleiben von Split-Padding getrennt.
- Die Derivatregeln für konstante Bitrate, Lautheitsstandardisierung auf Full-MP3-Ebene und Split-Erzeugung aus dem standardisierten Full-MP3 sind normativ vorbereitet.

## Abweichungen

- Keine Abweichung von der Docs-Governance.
- Es wurde kein Produktionscode für MP3-, Split- oder JSON-Erzeugung gebaut.

## Verifikation

- Aktive Specs und Modellreferenzen gegengelesen.
- Skriptstruktur unter `scripts/` geprüft und intake-relevante Bereiche in die neue Wurzel eingeordnet.
- Aktive Runbooks und Pfadangaben auf den verschobenen Dev-Seed aktualisiert.
- Normative Wordlist-Regeln auf Konsistenz zwischen Repo-Struktur und Player-Datenvertrag geprüft.
- `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/session_setup/seed_dev_spanish_example_sessions.py --dry-run` erfolgreich ausgeführt.

## Offene Punkte

- Die eigentliche Produktionslogik für `derived/wordlist.mp3`, `items/wordlist/{item_id}.mp3` und `alignment/wordlist.json` ist bewusst noch nicht implementiert.
- Für `text` und `interview` wurden keine künstlichen Vorab-Pipelines vorbereitet, weil belastbare Beispieldaten dafür weiterhin fehlen.
- Die konkrete Werkzeugwahl und CLI-Oberfläche des nächsten Wordlist-Produktionsskripts bleibt bis zum Implementierungs-Run offen.

## Nächste sinnvolle Schritte

1. Die `wordlist`-Produktionslogik unter `scripts/research_data_intake/audio_conversion/`, `item_split/` und `alignment_export/` implementieren.
2. Das kommende Implementierungsskript direkt auf `source/wordlist.wav` und `alignment/wordlist.TextGrid` ausrichten.
3. Danach den resultierenden Artefaktvertrag mit einem kleinen Validierungs- oder Smoke-Test absichern.