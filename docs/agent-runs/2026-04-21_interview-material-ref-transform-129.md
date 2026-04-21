# Interview Material Reference Transform 129

Datum: 2026-04-21

## Ziel

Die batch-lokale Interview-Transformation im Working-Tree fachlich vervollständigen: kompakte Materialmarker aus Amberscript korrekt parsen, sichtbare Referenztexte aus den kanonischen Task-Katalogen auflösen, Rohmarker aus Segment- und Tokentext entfernen und ehrliche Fehlerstati für kaputte oder unbekannte Referenzen liefern.

## Consulted Sources

- `AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/intake-workbook.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `scripts/research_data_intake/README.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `docs/plans/PROMAT_ Interview-Pipeline via Amberscript.md`
- `scripts/research_data_intake/intake_batch_common.py`
- `scripts/research_data_intake/alignment_export/import_interview_amberscript.py`
- `scripts/research_data_intake/import/organize_batch_working_tree.py`
- `app/tests/test_research_working_tree_intake.py`
- `data/config/research_player/spanish/task_catalogs/wordlist.json`
- `data/config/research_player/spanish/task_catalogs/text.json`
- `scripts/research_data_intake/import/spanish_batch_20260421/processed/`
- `scripts/research_data_intake/import/spanish_batch_20260421/working/`

## Geänderte Bereiche

- `scripts/research_data_intake/intake_batch_common.py`
- `scripts/research_data_intake/alignment_export/import_interview_amberscript.py`
- `scripts/research_data_intake/import/organize_batch_working_tree.py`
- `app/tests/test_research_working_tree_intake.py`
- `scripts/research_data_intake/README.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `docs/plans/PROMAT_ Interview-Pipeline via Amberscript.md`
- `docs/agent-runs/2026-04-21_interview-material-ref-transform-129.md`

## Wichtige Entscheidungen

- Interview-Materialreferenzen werden im Intake nur noch als kompakte Marker am referenzierenden Token akzeptiert, zum Beispiel `89[wl_089].`, `D5[d_05]` oder `Nummero [wl_087]`.
- Die sichtbaren Referenzdaten werden nicht aus freiem Editortext übernommen, sondern aus den kanonischen Katalogen unter `data/config/research_player/{language}/task_catalogs/wordlist.json` und `text.json` aufgelöst.
- Das Working-JSON hält Rohmarker nicht mehr in `segment.text` oder `tokens[].text`; stattdessen schreibt die Transformation strukturierte `material_ref`-Annotationen mit `item_id`, `task`, `label`, `item_number`, `canonical_text`, `insert_after_token_id` und optional `trailing_punctuation`.
- Die Sprachauflösung für den Kataloglookup wird aus dem kanonischen `person_id` abgeleitet, damit die Transformationslogik nicht spanisch-hartcodiert bleibt.
- Ungültige Markerformen oder unbekannte `item_id`-Werte schlagen nicht mehr den gesamten Batchlauf unkontrolliert ab, sondern werden im Organizer als taskweise Fehlerstati gemeldet.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_working_tree_intake.py -q`
- Ergebnis: `12 passed in 0.28s`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_raw_sync_importer.py -q`
- Ergebnis: `2 passed in 0.84s`
- Reallauf für Interview-only-Rebuild:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421 --force-task interview`
- Reallauf Ergebnis:
  - `interview`: `rebuilt` für `ES-L-0001` bis `ES-L-0007`
  - `interview`: `missing_json` für `ES-L-0008` und `ES-L-0009`
  - `interview`: `missing_wav_and_json` für `ES-N-0001` und `ES-N-0002`
  - `wordlist` und `text`: unverändert `unchanged`
  - `errors=0`
- Reallauf zur Idempotenz:
  `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir spanish_batch_20260421`
- Idempotenz-Ergebnis:
  - `rebuilt=0`
  - alle bereits retransformierten Interview-Tasks danach `unchanged`
- Spotcheck im Working-JSON:
  - `working/ES-L-0001/interview/alignment/interview.json` enthält für das frühere Rohfragment `89[wl_089].` jetzt den Tokentext `89.` plus eine `material_ref`-Annotation mit `label = ahí – allí`, `item_number = 89`, `canonical_text = ahí – allí` und `insert_after_token_id = seg_007_tok_013`.

## Abweichungen

- Keine Abweichung vom Scope: es wurde weder der Player noch der Produktionsimport nach `data/sessions/...` erweitert.
- Die Änderung bleibt vollständig auf den batch-lokalen Working-Tree und seine Interview-Transformation beschränkt.

## Offene Punkte

- Die spätere UI-Renderlogik für `material_ref` muss `insert_after_token_id` und optional `trailing_punctuation` noch auswerten; dieser Run bereitet nur die Working-Daten dafür vor.
- Interview bleibt im produktiven Importpfad nach `data/sessions/...` weiterhin ein getrennter Folgeschritt.
