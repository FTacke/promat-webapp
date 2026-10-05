# Lokales Storage-Audit und kontrolliertes Aufräumen

Datum: 2026-10-05

## Ziel

Inventar des lokalen PROMAT-Speichers (Repo, Intake, Archiv, Exports, Worktrees), Aufräumen unstrittiger Reproduzierbarer, Read-only-Inventarwerkzeug und Handoff-Fakten für spätere Cloud-Läufe.

## Consulted Sources

- `docs/spec/platform-data-files.md`, `docs/spec/intake-workbook.md`
- `scripts/research_data_intake/intake_storage.py`, `run_text_mfa.py`, `intake_batch_common.py`
- `docs/runbooks/research-intake-working-pipeline.md`

## Geänderte Bereiche

- `scripts/storage_inventory.py` (neu, read-only)
- `docs/spec/platform-data-files.md` (Abschnitt „Local Storage Roles And Preservation Root“)
- `docs/runbooks/local-storage-hygiene.md` (neu)
- `docs/reports/2026-10-05_local-storage-audit.md` (Report inkl. Cloud-Handoff)
- Lokal gelöscht (nicht im Repo): `tmp/` QA-Captures und Edge-Profile, Tool-Caches; 1,70 GB frei geworden

## Wichtige Entscheidungen

- Keine Forschungsdaten, Workbooks, Kataloge oder DB-Volumes gelöscht; Archiv liegt nur lokal und gilt bis zur verifizierten Preservation als einzige Kopie.
- Batch-lokales `.mfa_cache` (3,1 GB) bewusst nicht gelöscht: der Legacy-Migrationspfad in `run_text_mfa.py` nutzt es, `shared/en` fehlt.
- Organizer-Äquivalenz nicht festgestellt; committete Rekonstruktion nicht verändert.

## Abweichungen

- Keine Abweichung von der Spezifikation.
- `K:\Pronunciation_Matters` existiert nicht; auf `K:` wurde nichts angelegt oder geschrieben.

## Verifikation

- SHA-256-Vergleich Drop-in/`working/` gegen Archiv, Katalog-Vergleich gegen Upload-Pakete.
- `test_research_working_tree_intake.py` 37/37 mit beiden Organizer-Versionen (Wegwerf-Worktree, entfernt).
- `scripts/storage_inventory.py` lauffähig, ruff sauber.
