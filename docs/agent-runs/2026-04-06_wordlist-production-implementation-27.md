# Wordlist Production Implementation 27

Datum: 2026-04-06

## Ziel

Die reale `wordlist`-Produktionspipeline unter `scripts/research_data_intake/` implementieren, auf die aktuellen spanischen Dev-Sessions anwenden und die erzeugten Player-Artefakte verifizieren.

## Consulted Sources

- `AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/runbooks/research-wordlist-production.md`
- `docs/agent-runs/2026-04-06_wordlist-production-preparation-24.md`
- `docs/agent-runs/2026-04-06_wordlist-production-rules-finalization-25.md`
- `docs/agent-runs/2026-04-06_task-catalog-foundation-26.md`
- `data/config/research_player/spanish/task_catalogs/wordlist.json`

## Implementierte Dateien

- `scripts/research_data_intake/produce_wordlist_artifacts.py`
- `scripts/research_data_intake/audio_conversion/ffmpeg_audio.py`
- `scripts/research_data_intake/alignment_export/wordlist_alignment.py`
- `scripts/research_data_intake/item_split/wordlist_splits.py`

## Geänderte Doku-Dateien

- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/runbooks/research-wordlist-production.md`
- `scripts/research_data_intake/README.md`
- `docs/agent-runs/2026-04-06_wordlist-production-implementation-27.md`

## Geänderte Session-Dateien und erzeugte Artefakte

Für jede erfolgreich verarbeitete Session wurden geändert oder neu erzeugt:

- `metadata.json`
- `derived/wordlist.mp3`
- `alignment/wordlist.json`
- `items/wordlist/wl_001.mp3` bis `items/wordlist/wl_092.mp3`

Erfolgreich verarbeitet wurden:

- `data/sessions/spanish/ES-L-0001-2026-S01/`
- `data/sessions/spanish/ES-L-0001-2027-S02/`
- `data/sessions/spanish/ES-L-0003-2026-S01/`
- `data/sessions/spanish/ES-L-0003-2027-S02/`
- `data/sessions/spanish/ES-L-0004-2026-S01/`
- `data/sessions/spanish/ES-L-0005-2026-S01/`
- `data/sessions/spanish/ES-L-0006-2026-S01/`
- `data/sessions/spanish/ES-N-0001-2026-S01/`
- `data/sessions/spanish/ES-N-0002-2026-S01/`

Batch-weit übersprungen wurden:

- `data/sessions/spanish/ES-L-0901-2024-S01/` wegen leerem `source/wordlist.wav`
- `data/sessions/spanish/ES-L-0002-2026-S01/` wegen kanonischer `wordlist`-Grenzen außerhalb der verfügbaren Audio-Dauer
- `data/sessions/spanish/ES-L-0002-2027-S02/` wegen kanonischer `wordlist`-Grenzen außerhalb der verfügbaren Audio-Dauer

## Implementiertes CLI

- Einzelsession-Dry-Run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/produce_wordlist_artifacts.py --session-id ES-L-0001-2026-S01 --dry-run`
- Batch-Dry-Run:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/produce_wordlist_artifacts.py --all-suitable-sessions --dry-run`
- Reale Batch-Produktion:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/produce_wordlist_artifacts.py --all-suitable-sessions`

## Umgesetzte Produktionsregeln

- Operative Inhaltsquelle ist `data/config/research_player/spanish/task_catalogs/wordlist.json`.
- `item_id`, `item_number` und `text` kommen ausschließlich aus dem Task-Katalog.
- `alignment/wordlist.TextGrid` liefert nur die Intervallgrenzen und die positionsgleiche Folge der nicht-silence-Intervalle.
- Texte werden nicht normalisiert oder aus TextGrid/PDF/TXT rekonstruiert.
- `start_ms` und `end_ms` werden als ganzzahlige Millisekundenwerte aus auf vier Nachkommastellen gerundeten TextGrid-Sekunden serialisiert.
- `derived/wordlist.mp3` und `items/wordlist/{item_id}.mp3` werden als MP3 in mono mit `160 kbps` CBR erzeugt.
- Lautheitsstandardisierung erfolgt nur auf `derived/wordlist.mp3`.
- Split-MP3s werden aus dem bereits standardisierten Full-MP3 erzeugt und nicht separat pro Item normalisiert.
- Split-Padding beträgt `250 ms` vor und nach dem Item und verändert die kanonischen JSON-Grenzen nicht.

## Verifikation

- Dry-Run für `ES-L-0001-2026-S01` erfolgreich mit `92` gemappten Items.
- Batch-Dry-Run erfolgreich mit `9` verarbeitbaren Sessions und `3` explizit übersprungenen Sessions.
- Reale Batch-Produktion erfolgreich für `9` Sessions.
- Interne Validierung pro verarbeiteter Session geprüft:
  - `derived/wordlist.mp3` vorhanden
  - `alignment/wordlist.json` vorhanden
  - `92` Items im JSON
  - `92` Split-MP3s vorhanden
  - `item_id`-Sequenz `wl_001` bis `wl_092`
  - `split_mp3`-Pfade im JSON stimmen mit den erzeugten Dateien überein
  - `ffprobe` bestätigt mono und `160000` bps für das Full-MP3 sowie stichprobenartig für Split-MP3s

## Offen geblieben

- Für `text` und `interview` wurde bewusst keine Produktionslogik gebaut.
- Zwei learner-Sessions sind aktuell nicht `wordlist`-prozessierbar, weil ihre kanonischen TextGrid-Grenzen über die verfügbare Audio-Dauer hinausreichen.
- Die leere Placeholder-Session `ES-L-0901-2024-S01` bleibt weiterhin nur ein nicht verarbeitbarer Repo-Platzhalter.