# Generic Intake Docs And Language Hardening 121

Datum: 2026-04-14

## Ziel

Die dokumentierte und implementierte Realität der generischen Batch-/Working-Pipeline unter `scripts/research_data_intake/` auf den tatsächlich erreichten Stand bringen, mit Fokus auf Generalisierung, Robustheit, Sprachkonfiguration und optionalem MFA-Modell-Preload.

## Consulted Sources

- `AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/intake-workbook.md`
- `docs/spec/research-player.md`
- `scripts/research_data_intake/README.md`
- `scripts/research_data_intake/intake_batch_common.py`
- `scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py`
- `scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py`

## Geänderte Bereiche

- `scripts/research_data_intake/intake_batch_common.py`
- `scripts/research_data_intake/language_config.py`
- `scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py`
- `scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py`
- `scripts/research_data_intake/alignment_export/preload_mfa_models.py`
- `scripts/research_data_intake/README.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/runbooks/research-intake-working-pipeline.md`
- `docs/agent-runs/2026-04-14_generic-intake-docs-language-hardening-121.md`

## Wichtige Entscheidungen

- Batch-Erkennung bleibt generisch unter `scripts/research_data_intake/import/`, verlangt aber jetzt explizit `batch` im Ordnernamen und mindestens ein vorhandenes `processed/`.
- Die gemeinsame Sprachkonfiguration für `es`, `de`, `fr` und `en` hält MFA-Modellnamen und einfache Workflow-Metadaten zentral zusammen.
- `prepare_text_mfa_corpus.py` und `import_text_mfa_alignment.py` akzeptieren optional `--language` zur validierten Kopplung an die Sprachkonfiguration.
- Das opt-in CLI `preload_mfa_models.py` prüft MFA explizit und lädt Modelle nur mit `--download-models`.
- `working/{person_id}/text/alignment/text.json` bleibt explizit ein Working-Tree-Zwischenartefakt und keine Produktionssession unter `data/`.

## Verifikation

- Python-Compile-Check der geänderten Intake-Skripte
- CLI-Help- oder Dry-Run-Prüfung der neuen Batch-/Sprachlogik
- Konsistenzprüfung von README, Spec und neuem Runbook gegen die tatsächliche Working-Pipeline

## Offene Punkte

- finaler Transfer aus Batch/Working nach `data/`
- vollständige Session-/Metadata-/XLSX-Integration
- finale `session_id`-Setzung
- Produktions-`derived/text.mp3`
- finale Interview-Integration