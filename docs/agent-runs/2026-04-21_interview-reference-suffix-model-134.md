# Interview Reference Suffix Model 134

Datum: 2026-04-21

## Ziel

Die Interview-Referenzlogik in Intake, Working-JSON, Produktionsimport und produktivem Research-Player so umstellen, dass nachgestellte Interpunktion nicht mehr als `trailing_punctuation` an der Annotation modelliert wird, sondern tokennah als `suffix` am referenzierten Token erhalten bleibt.

## Consulted Sources

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `scripts/research_data_intake/alignment_export/import_interview_amberscript.py`
- `app/src/app/research_player_runtime.py`
- `app/templates/pages/research_player.html`
- `app/tests/test_research_working_tree_intake.py`
- `app/tests/test_research_production_importer.py`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `scripts/research_data_intake/alignment_export/import_interview_amberscript.py`
- `app/src/app/research_player_runtime.py`
- `app/templates/pages/research_player.html`
- `app/tests/test_research_working_tree_intake.py`
- `app/tests/test_research_production_importer.py`
- `app/tests/test_research_sessions.py`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `scripts/research_data_intake/README.md`

## Wichtige Entscheidungen

- Materialreferenz-Marker wie `25[wl_025].`, `D5[d_05],` oder `QY3[qy_03]?` werden im Transformationsschritt lokal in gesprochenen Kern, Referenz und Suffix zerlegt.
- Das Working- und Runtime-JSON tragen Schlussinterpunktion nur noch tokennah in `tokens[].suffix`.
- `annotations[]` behalten nur die strukturierte `material_ref`-Referenz plus `insert_after_token_id`; `trailing_punctuation` wird nicht mehr geschrieben oder ausgewertet.
- Die Runtime konsumiert `suffix` beim Token-Matching gegen `segment.text`, damit die sichtbare Interview-Zeile weiterhin dem Segmenttext entspricht, aber der Renderer die Reihenfolge `token.text` → Referenz → `token.suffix` ausgeben kann.

## Re-Run

- Working-Rebuild:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421 --force-task interview`
- Produktionsimport für die betroffene Person:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import_batch_to_production.py --batch-dir spanish_batch_20260421 --target-language es --person-id ES-L-0002 --sync-tasks --auth-database-url postgresql+psycopg2://promat_auth:promat_auth@127.0.0.1:55432/promat_auth`

## Verifikation

### Tests

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_working_tree_intake.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_production_importer.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`

### Working-JSON

- `scripts/research_data_intake/import/spanish_batch_20260421/working/ES-L-0002/interview/alignment/interview.json` enthält für `seg_009_tok_003` jetzt `"text": "25"` plus `"suffix": "."`.
- Die zugehörige Annotation enthält `item_id = wl_025`, `insert_after_token_id = seg_009_tok_003`, aber kein `trailing_punctuation`.

### Runtime-JSON

- `data/sessions/spanish/ES-L-0002-2026-S01/alignment/interview.json` enthält dieselbe Struktur mit `"text": "25"`, `"suffix": "."` und der referenzierten `material_ref`-Annotation ohne Altfeld.

### Browser

- Headless-Edge-Prüfung gegen den laufenden Dev-Server unter `http://127.0.0.1:8000` mit dem lokalen Dev-Admin aus `app/scripts/dev-start.ps1`.
- Die produktive Interviewzeile für `seg_009` wurde als `Item Nummer 25 [oír].` gerendert.
- Screenshot: `tmp/ui-qa/2026-04-21-interview-suffix-134/de-interview-suffix-es-l-0002.png`