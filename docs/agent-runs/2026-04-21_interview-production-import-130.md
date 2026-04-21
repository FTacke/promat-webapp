# Interview Production Import 130

Datum: 2026-04-21

## Ziel

Den zentralen Produktionsimport von `working/` nach `data/sessions/` plus Research-Metadatenbank für `interview` vervollständigen, ohne den Player oder neue UI-Flows umzubauen.

## Consulted Sources

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `scripts/AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/intake-workbook.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/research-player.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- `scripts/research_data_intake/import_batch_to_production.py`
- `scripts/research_data_intake/intake_workbook_reader.py`
- `scripts/research_data_intake/produce_wordlist_artifacts.py`
- `scripts/research_data_intake/produce_text_artifacts.py`
- `scripts/research_data_intake/audio_conversion/ffmpeg_audio.py`
- `app/src/app/research_metadata.py`
- `app/src/app/research_sessions.py`
- `app/tests/test_research_raw_sync_importer.py`
- `scripts/research_data_intake/README.md`
- `docs/runbooks/research-intake-working-pipeline.md`

## Geänderte Bereiche

- `scripts/research_data_intake/import_batch_to_production.py`
- `app/tests/test_research_production_importer.py`
- `app/tests/test_research_raw_sync_importer.py`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/spec/research-capabilities.md`
- `scripts/research_data_intake/README.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `docs/agent-runs/2026-04-21_interview-production-import-130.md`

## Wichtige Entscheidungen

- `interview` wird im zentralen Produktionsimport wie ein echter Task behandelt: bei vorhandenem Working-WAV plus Working-JSON ist der Status `ready` und `--sync-tasks` übernimmt die Artefakte produktiv.
- Der Runtime-Import für `interview` schreibt `source/interview.wav`, `alignment/interview.json` und `derived/interview.mp3` in den Session-Baum und setzt dabei die finale `session_id` im Runtime-Alignment-JSON.
- Reale Raw-Master bleiben weiterhin strikt vom Working-`source/` getrennt; fehlende Raw-Master werden nicht aus `source/` synthetisiert.
- Die Runtime-Metadaten bleiben dateisystemwahr: `tasks[]` und `files[]` referenzieren nur tatsächlich vorhandene Artefakte, und `interview` nutzt dort `alignment/interview.json` statt eines erfundenen TextGrid-Pfads.
- `exposure_entries` verwenden im geschriebenen Runtime-Metadata wieder den aktiven Feldnamen `exposure_notes`, damit der Loader die strukturierten Aufenthaltsdaten korrekt liest.
- Player- und Capability-Spezifikation bleiben bewusst getrennt vom Import: produktive Runtime-Artefakte machen `interview` noch nicht zu einem produktiven Player-Modus.

## Abweichungen

- Keine Abweichung vom Scope: der Run erweitert nur den zentralen Produktionsimport, Tests und die dazugehörigen Specs/Dokumente.
- Es wurde kein Interview-Renderer und keine neue UI eingeführt.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_production_importer.py app/tests/test_research_raw_sync_importer.py -q`
- Ergebnis: `7 passed in 0.79s`
- Isolierter Dry-Run gegen den realen Batch mit temporärer Runtime-Root und SQLite-DB:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --person-id ES-L-0001 --sync-tasks --auth-database-url sqlite+pysqlite:///C:/dev/promat/tmp/production-import-check-interview-gpt54.sqlite3 --dry-run`
- Dry-Run-Ergebnis:
  - `create ES-L-0001-2026-S01`
  - `tasks[wordlist=sync/ready, text=sync/ready, interview=sync/ready]`
  - `raw[wordlist=sync/ready, text=sync/ready, interview=sync/ready]`
- Isolierter Schreiblauf gegen denselben Realbatch:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --person-id ES-L-0001 --sync-tasks --auth-database-url sqlite+pysqlite:///C:/dev/promat/tmp/production-import-check-interview-gpt54.sqlite3`
- Re-Run zur Stabilitätsprüfung:
  - `update ES-L-0001-2026-S01`
  - `tasks[wordlist=sync/ready, text=sync/ready, interview=sync/ready]`
  - `raw[wordlist=keep/present, text=keep/present, interview=keep/present]`
- Spotcheck im isolierten Runtime-Baum unter `tmp/production-import-check-interview-gpt54/data/sessions/spanish/ES-L-0001-2026-S01/`:
  - `metadata.json` enthält `interview` in `tasks[]` mit `alignment/interview.json` und `derived/interview.mp3`
  - `alignment/interview.json` trägt die finale `session_id = ES-L-0001-2026-S01`
  - `raw/`, `source/`, `alignment/` und `derived/` enthalten die produktiv importierten Interview-Artefakte
- SQLite-Spotcheck:
  - `research_people`: `1`
  - `research_sessions`: `('ES-L-0001-2026-S01', 'wordlist; text; interview')`

## Offene Punkte

- Der Player rendert `interview` weiterhin bewusst nicht produktiv; die neuen Runtime-Artefakte sind Vorbereitung für spätere Renderer-Arbeit, nicht deren Ersatz.
- Der isolierte Realbatch-Check lief gezielt für `ES-L-0001`; ein größerer Mehr-Personen-Import kann als separater Folgelauf sinnvoll sein.

## Nächste sinnvolle Schritte

- Mehr-Personen-Lauf des zentralen Produktionsimports gegen eine isolierte Runtime-Root und temporäre DB, um Batch-Breite und Konfliktpfade mit mehreren Sessions zu prüfen.
- Bei späterem Interview-Renderer-Start direkt auf die jetzt produktiv geschriebenen `alignment/interview.json`- und `derived/interview.mp3`-Artefakte aufsetzen.