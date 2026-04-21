# Incremental Working-Tree Interview Intake 128

Datum: 2026-04-21

## Ziel

Den batch-lokalen Working-Tree-Organizer auf taskweise Inkrementalität umstellen, Interview über Amberscript-JSON produktiv in den Working-Tree integrieren und dabei den bestehenden `text`-MFA-Pfad unangetastet lassen.

## Consulted Sources

- `AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/intake-workbook.md`
- `docs/spec/research-player.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/research-access.md`
- `scripts/research_data_intake/README.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `docs/plans/PROMAT_ Interview-Pipeline via Amberscript.md`
- `scripts/research_data_intake/intake_batch_common.py`
- `scripts/research_data_intake/import/organize_batch_working_tree.py`
- `scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py`
- `scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py`
- `scripts/research_data_intake/import/spanish_batch_20260421/processed/`
- `scripts/research_data_intake/import/spanish_batch_20260421/raw/`
- `scripts/research_data_intake/import/spanish_batch_20260421/working/`

## Geänderte Bereiche

- `scripts/research_data_intake/intake_batch_common.py`
- `scripts/research_data_intake/alignment_export/__init__.py`
- `scripts/research_data_intake/alignment_export/import_interview_amberscript.py`
- `scripts/research_data_intake/import/organize_batch_working_tree.py`
- `app/tests/test_research_working_tree_intake.py`
- `docs/spec/platform-data-files.md`
- `scripts/research_data_intake/README.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `docs/plans/PROMAT_ Interview-Pipeline via Amberscript.md`
- `docs/agent-runs/2026-04-21_incremental-working-tree-interview-intake-128.md`

## Wichtige Entscheidungen

- Der Organizer führt jetzt batch-lokal `working/.intake_state.json` und entscheidet pro `person_id` und Task auf Basis der relevanten Input-Snapshots `size + mtime_ns`, ob `unchanged` oder `rebuilt` gilt.
- `wordlist` und `text` werden nur noch durch ihre relevanten `processed/`-WAV- und TextGrid-Inputs getriggert; unveränderte Task-Unterbäume bleiben unangetastet.
- Bei Task-Rebuilds wird nur `working/{person_id}/{task}/` ersetzt, nicht der ganze Person- oder Batch-Baum.
- Interview nutzt jetzt batch-lokal Amberscript-JSON als Rohquelle und schreibt `working/{person_id}/interview/alignment/interview.json` statt eines Interview-TextGrids.
- Für Interview gilt eine explizite Fallback-Logik: bevorzugt `*_interview_processed.wav` und `*_interview_processed.json`, sonst `*_interview_raw.wav` beziehungsweise `*_interview_raw.json`; gleichrangige Mehrfachkandidaten sind harte Konflikte.
- Die reale Batch-Situation mit `processed/es_l_0001_interview_raw.json` wurde ausdrücklich unterstützt; JSON-Dateien dürfen deshalb im Organizer nicht pauschal wegen Stage-vs-Folder-Mismatch verworfen werden.
- Der produktive Produktionsimport nach `data/sessions/...` bleibt unverändert getrennt; Interview wird in diesem Run nur bis zur Working-Tree-Stufe integriert.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_working_tree_intake.py app/tests/test_research_raw_sync_importer.py -q`
- Ergebnis: `9 passed in 0.59s`
- Reallauf 1:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421`
- Reallauf 1 Ergebnis:
  - `wordlist`: für alle 11 Personen `unchanged`
  - `text`: für alle 11 Personen `unchanged`
  - `interview`: `rebuilt` für `ES-L-0001` bis `ES-L-0007`
  - `interview`: `missing_json` für `ES-L-0008` und `ES-L-0009`
  - `interview`: `missing_wav_and_json` für `ES-N-0001` und `ES-N-0002`
- Reallauf 2 zur Idempotenz:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421`
- Reallauf 2 Ergebnis:
  - `rebuilt=0`
  - alle bereits gebauten Interview-Tasks danach `unchanged`
- Zusätzliche Batch-Prüfung per Python-Snippet:
  - Vor dem ersten Reallauf existierte kein `working/.intake_state.json`, `working/ES-L-0001/interview/alignment/interview.json` fehlte, und die Mtimes von `wordlist/source/wordlist.wav` und `text/source/text.wav` wurden erfasst.
  - Nach den Realläufen existiert `working/.intake_state.json`, `working/ES-L-0001/interview/alignment/interview.json` wurde erzeugt, und die erfassten `wordlist`-/`text`-Mtimes blieben unverändert.

## Abweichungen

- Keine Abweichung vom aktiven Scope: es wurde bewusst kein Player-Renderer, keine Interview-UI und kein Produktionsimport nach `data/sessions/...` ergänzt.
- Die Interview-Annotationen werden nur technisch für spätere Materialreferenzen vorbereitet; eine fachlich vollständige Anreicherung gegen Kataloge ist nicht Teil dieses Runs.

## Offene Punkte

- Der zentrale Produktionsimport erkennt Interview im Working-Tree weiterhin nur als noch nicht produktiv zu synchronisierenden Task; die spätere Übernahme nach `data/sessions/...` bleibt separat.
- Der Text-MFA-Pfad ist jetzt gegen unnötige Organizer-Rebuilds abgesichert, aber die Entscheidung, wann `prepare_text_mfa_corpus.py` oder `import_text_mfa_alignment.py` automatisch orchestrationseitig erneut laufen sollen, bleibt ein eigener Folgeschritt.
- Für Interview-Materialreferenzen ist die spätere Validierung gegen `wordlist.json` und `text.json` noch offen.