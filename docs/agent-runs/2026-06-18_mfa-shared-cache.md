# MFA Shared Cache

Datum: 2026-06-18

## Ziel

Docker-backed Text-MFA soll MFA-Modelle sprachspezifisch gemeinsam wiederverwenden, statt pro Person oder Manifest-Hash dieselben Acoustic- und Dictionary-Modelle erneut herunterzuladen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `scripts/research_data_intake/README.md`
- `scripts/research_data_intake/language_config.py`
- `scripts/research_data_intake/alignment_export/run_text_mfa.py`

## Geaenderte Bereiche

- `scripts/research_data_intake/alignment_export/run_text_mfa.py`
- `app/tests/test_research_text_mfa_runner.py`
- `docs/spec/platform-data-files.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `scripts/research_data_intake/README.md`

## Wichtige Entscheidungen

- Der Docker-MFA-Modellcache liegt global im Intake-Bereich unter `scripts/research_data_intake/.mfa_cache/shared/{language_code}/`.
- Das personenspezifische `working/{person_id}/text/mfa_corpus/` und `working/{person_id}/text/mfa_output/` bleibt unveraendert.
- Der Runner trennt Modell-Ensure und Alignment: `mfa model download` wird nur fuer fehlende Modelle geplant, `mfa align` bleibt ein eigener Befehl.
- Alte batchlokale Person-Caches koennen als vorsichtige Migrationsquelle fuer fehlende Shared-Cache-Modelle dienen.

## Abweichungen

- Keine Abweichung von Runtime- oder Archivgrenzen. Der Shared Cache bleibt Intake-intern und wird nicht nach Runtime, Archiv oder Prod-Paketen exportiert.

## Verifikation

- `python -m pytest app/tests/test_research_text_mfa_runner.py`
- `python -m pytest app/tests/test_research_text_mfa_runner.py app/tests/test_research_working_tree_intake.py app/tests/test_research_production_importer.py`
- `python -m ruff check .`
- Dry-Run gegen `english_batch_20260618` fuer `EN-L-0009` zeigte `model_cache_dir=.../.mfa_cache/shared/en`, geplante Legacy-Migration und getrennten `align_command`.

## Offene Punkte

- Der Shared Cache wird erst beim naechsten echten Docker-MFA-Lauf physisch aus Legacy-Caches befuellt oder bei fehlenden Modellen heruntergeladen.

## Naechste sinnvolle Schritte

- Bei einem kuenftigen frischen Batch einmal den Docker-MFA-Dry-Run je Sprache pruefen, bevor der volle `--run-mfa`-Import gestartet wird.
