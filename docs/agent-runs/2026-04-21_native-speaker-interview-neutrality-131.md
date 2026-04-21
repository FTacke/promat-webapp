# Native Speaker Interview Neutrality 131

Datum: 2026-04-21

## Ziel

Die Intake- und Produktionsimportlogik so nachziehen, dass `interview` für Native Speaker kein fehlender oder unvollständiger Task mehr ist, sondern konsistent als fachlich nicht erwartet behandelt wird.

## Consulted Sources

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `scripts/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `scripts/research_data_intake/intake_batch_common.py`
- `scripts/research_data_intake/import/organize_batch_working_tree.py`
- `scripts/research_data_intake/import_batch_to_production.py`
- `app/src/app/research_capabilities.py`
- `app/tests/test_research_working_tree_intake.py`
- `app/tests/test_research_production_importer.py`

## Geänderte Bereiche

- `scripts/research_data_intake/intake_batch_common.py`
- `scripts/research_data_intake/import/organize_batch_working_tree.py`
- `scripts/research_data_intake/import_batch_to_production.py`
- `app/tests/test_research_working_tree_intake.py`
- `app/tests/test_research_production_importer.py`
- `docs/spec/platform-data-files.md`
- `scripts/research_data_intake/README.md`

## Wichtige Entscheidungen

- Der Organizer leitet für `person_id` mit Marker `-N-` den neutralen Status `not_expected_for_native_speaker` für `interview` ab, statt fehlende WAV- oder JSON-Inputs als Warnung zu melden.
- Der zentrale Produktionsimport übernimmt dieselbe Semantik für Task- und Raw-Pläne und behandelt fehlende Native-Speaker-Interviewdateien nicht als Defizit.
- Wenn ein Native-Speaker-Import doch noch alte `interview`-Runtime-Artefakte im Zielverzeichnis vorfindet, räumt der normale Schreibpfad diese vor dem Neuaufbau der Metadaten weg, damit `metadata.json` und `documented_tasks` konsistent bleiben.
- `wordlist` und `text` bleiben für Native Speaker unverändert erwartete Tasks.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_working_tree_intake.py app/tests/test_research_production_importer.py -q`

## Offene Punkte

- Kein zusätzlicher Player-Umbau; die Änderung bleibt bewusst auf Intake-, Import- und Metadaten-Semantik begrenzt.