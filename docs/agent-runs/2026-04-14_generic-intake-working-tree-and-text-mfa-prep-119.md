# Generic Intake Working Tree And Text MFA Prep 119

Datum: 2026-04-14

## Ziel

Zwei generische, vorproduktive Intake-Schritte unter `scripts/research_data_intake/` ergänzen: Batch-Organisation in eine kanonische `working/`-Struktur und Vorbereitung eines personbezogenen MFA-Zwischenkorpus für `text`.

## Consulted Sources

- `AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/intake-workbook.md`
- `docs/spec/research-player.md`
- `scripts/research_data_intake/README.md`
- `scripts/research_data_intake/produce_wordlist_artifacts.py`
- `scripts/research_data_intake/alignment_export/wordlist_alignment.py`
- `scripts/research_data_intake/audio_conversion/ffmpeg_audio.py`

## Geänderte Bereiche

- `scripts/research_data_intake/intake_batch_common.py`
- `scripts/research_data_intake/textgrid_support.py`
- `scripts/research_data_intake/import/organize_batch_working_tree.py`
- `scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py`
- `scripts/research_data_intake/README.md`
- `docs/spec/platform-data-files.md`
- `docs/agent-runs/2026-04-14_generic-intake-working-tree-and-text-mfa-prep-119.md`

## Wichtige Entscheidungen

- Die neue Batch-Organisation bleibt batch-lokal unter `scripts/research_data_intake/import/{batch}/working/` und schreibt bewusst nicht nach `data/`.
- `processed/` ist die primäre Quelle für kanonische `working/`-WAVs und TextGrids; `raw/` dient nur als optionaler WAV-Fallback oder Zusatzquelle.
- Der neue `text`-MFA-Schritt akzeptiert eine explizite JSON-Solltextquelle und behandelt das TextGrid nur als Segmentgrenzenquelle.
- Das Manifest für den MFA-Zwischenschritt liegt pro Person unter `working/{person_id}/text/mfa_manifest.json`, damit die spätere Rückübertragung vom MFA-Output eindeutig bleibt.
- Die bestehende `wordlist`-Produktionspipeline blieb unberührt.

## Abweichungen

- Keine Abweichung von den aktiven Spec- und Governance-Regeln.
- MFA wird bewusst noch nicht ausgeführt; der neue Schritt endet beim vorbereiteten Zwischenkorpus und Manifest.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m py_compile scripts/research_data_intake/intake_batch_common.py scripts/research_data_intake/textgrid_support.py scripts/research_data_intake/import/organize_batch_working_tree.py scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py`
- `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/import/organize_batch_working_tree.py --batch-dir scripts/research_data_intake/import/spanisch_batch --dry-run`
- Temporären Batch unter `scripts/research_data_intake/import/_validation_batch` aus dem Beispielmaterial aufgebaut, Organizer im Schreibmodus ausgeführt und anschließend entfernt.
- `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py --batch-dir _validation_batch --text-source-json data/config/research_player/spanish/task_catalogs/text.json --dry-run`
- Ergebnis der Dry-Run-Validierung: 11 Personen erkannt, Organizer plante 53 Transfers, MFA-Prep validierte 50 Textsegmente pro Person ohne Fehler.

## Offene Punkte

- Für andere Korpora oder Textaufgaben muss die passende explizite Solltextquelle noch bereitgestellt werden.
- Finale `alignment/text.json`-Ableitung, MFA-Ausführung und Endimport in `data/` sind weiterhin nachgelagerte Schritte.

## Nächste sinnvolle Schritte

1. Ein kleines Mapping- oder Katalogformat für weitere Textaufgaben standardisieren, damit `--text-source-json` corpusübergreifend konsistent befüllt werden kann.
2. Den späteren MFA-Ausführungsschritt und die Rückübertragung des MFA-Outputs getrennt von dieser Vorstufe implementieren.
3. Falls weitere reale Batch-Namensschemata dazukommen, die Dateinamen-Parserregeln bewusst und explizit erweitern statt freie Heuristiken einzubauen.