# English Batch Limited Test Import

Datum: 2026-05-25

## Ziel

Den realen Drop-in-Batch `scripts/research_data_intake/import/en_batch_20260525` kontrolliert nur für `EN-L-0001` bis `EN-L-0004` importieren, ohne andere Batch-Personen produktiv in Runtime oder DB zu übernehmen.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `scripts/research_data_intake/README.md`
- `scripts/research_data_intake/import_batch_to_production.py`
- `scripts/research_data_intake/intake_storage.py`
- `scripts/research_data_intake/intake_batch_common.py`
- `scripts/research_data_intake/alignment_export/import_interview_amberscript.py`
- `scripts/research_data_intake/alignment_export/prepare_text_mfa_corpus.py`
- `scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py`

## Geänderte Bereiche

- begrenzter Working-Tree-Aufbau nur für `EN-L-0001` bis `EN-L-0004` unter dem Batch-`working/`
- Runtime-Import nach `data/sessions/english/`
- session-zentriertes Archiv unter `C:/dev/promat_data_archive/sessions/en/`
- Batch-Reports unter `C:/dev/promat_data_archive/batches/en_batch_20260525/`
- kleiner Implementierungsfix in `scripts/research_data_intake/intake_storage.py` und `scripts/research_data_intake/import_batch_to_production.py`, damit Archivmanifeste `skipped_or_missing_artifacts` explizit ausweisen

## Wichtige Entscheidungen

- Der Batch wurde strikt dateinamengetrieben auf vier Zielpersonen begrenzt; alle Dateien von `EN-L-0005` bis `EN-L-0009` blieben außerhalb des produktiven Imports.
- `wordlist` wurde für alle vier Sessions importiert, weil dafür eindeutige WAV/TextGrid-Inputs vorlagen.
- `text` wurde für alle vier Sessions kontrolliert übersprungen, weil lokal keine `mfa`-CLI verfügbar war und daher kein valides `working/text/alignment/text.json` erzeugt werden konnte.
- `interview` wurde für alle vier Sessions kontrolliert übersprungen, weil die Amberscript-JSONs im aktuellen Importer ungültige Marker bzw. nicht unterstützte Speaker-Codes enthielten und nicht heuristisch korrigiert wurden.
- Der Dev-DB-Upsert wurde nicht ausgeführt, weil die aktuelle Dev-DB-Schema-Version nicht zur Importer-ORM passt (`research_people.research_consent_signed` fehlt). Der Lauf wurde deshalb kontrolliert als file-only Import zu Runtime und Archiv abgeschlossen.

## Abweichungen

- Abweichung vom Idealfall: Der Import aktualisierte die Dev-DB nicht.
- Abweichung vom Idealfall: `text` und `interview` wurden nicht in Runtime importiert; die Skip-Gründe stehen pro Session in Warnungen und Archivmanifesten.
- Keine Abweichung bei den Repo-Grenzen: kein Prod-Paket, kein Serverkontakt, keine Änderungen an `content/`, `content/teaching/` oder `public/teaching/`.

## Verifikation

- Batch-Scan plus Workbook-Filter nur für `EN-L-0001` bis `EN-L-0004`
- Dry-Run-Plan mit taskgenauer Entscheidung pro Session
- Laufender Importplan bestätigte nur vier Sessions und nur `wordlist=sync`
- Nachlauf-Checks:
  - `data/sessions/english/EN-L-0001-2026-S01`
  - `data/sessions/english/EN-L-0002-2026-S01`
  - `data/sessions/english/EN-L-0003-2026-S01`
  - `data/sessions/english/EN-L-0004-2026-S01`
  - `validate_runtime_tree(...)` für alle vier Sessions: grün
  - `validate_archive_tree(...)` für alle vier Archiv-Sessions: grün
  - keine verbotenen Runtime-Dateien oder -Ordner (`*.wav`, `*.TextGrid`, `*.xlsx`, `secure/`, `raw/`, `origin/`, `source/`, `alignment_source/`, `working/`, `mfa_*`)
  - `metadata.json`, `alignment/*.json` und `metadata/archive_manifest.json` parsebar
  - `alignment/wordlist.json` verweist auf vorhandenes `derived/wordlist.mp3` sowie vorhandene Item-MP3s
  - Batch-Archivreport `import_payload.json` enthält genau 4 Personen und 4 Sessions
  - `git status --short -- content public/teaching` blieb leer

## Offene Punkte

- Für einen vollständigen EN-Batch-Import muss lokal entweder MFA verfügbar gemacht oder ein alternativer, spezifikationskonformer Text-Ableitungsschritt bereitgestellt werden.
- Die vier Interview-Amberscript-JSONs brauchen eine fachlich saubere Bereinigung oder eine explizite Erweiterung des Importers für die neuen Marker-/Speaker-Code-Varianten.
- Für Dev-DB-Upserts muss die lokale Dev-DB auf das erwartete ORM-Schema migriert werden.

## Nächste sinnvolle Schritte

- Dev-DB-Schema mit dem aktuellen Importer-ORM synchronisieren und den Viererlauf optional mit DB-Upsert wiederholen.
- MFA lokal verfügbar machen und anschließend `text` für dieselben vier Sessions ergänzen.
- Die Interview-JSON-Probleme im Batch oder Importer gezielt beheben und danach `interview` für dieselben vier Sessions nachziehen.
- Erst danach den vollständigen EN-Batch produktiv planen.
