# Agent Run: EN-L-0001 Intake Pipeline Completion

**Date:** 2026-05-25  
**Scope:** EN-L-0001 nur, aus `en_batch_20260525`

---

## Ausgangslage

Der Pipeline-Command für EN-L-0001 war halb durchgeführt. MFA hatte bereits gelaufen (text.json in working vorhanden), aber drei Probleme verhinderten einen sauberen Abschluss:

1. **Staler Working-State für Interview**: `organize_batch_working_tree` detektierte interview als "unchanged", obwohl `interview/alignment/interview.json` fehlte. Ursache: Der `_should_rebuild`-Check prüfte nur die historisch im State gespeicherten Outputs (nur WAV), nicht ob alle aktuell erwarteten Outputs vorhanden sind.
2. **`.mfa_cache`-Verzeichnis nicht gefiltert**: Das MFA-Arbeitsverzeichnis wurde vom Batch-Scanner erfasst; auf Windows konnten Kaldi-`.ark`-Dateien nicht per `stat()` gelesen werden (`WinError 1920`).
3. **`rglob`-Traversal betritt ignorierte Verzeichnisse**: Selbst nach Hinzufügen des Namens zu `IGNORED_BATCH_DIR_NAMES` versuchte der Iterator zuerst in das Verzeichnis zu descenden und dann zu filtern – zu spät für Windows-Dateizugriffsfehler.

---

## Behobene Probleme

### 1. `_should_rebuild` – aktuelle Expected Outputs prüfen
**Datei:** `scripts/research_data_intake/import/organize_batch_working_tree.py`

Im Early-Return-Branch wird jetzt zusätzlich geprüft, ob alle aktuell erwarteten Outputs (`_expected_outputs(...)`) auf Disk vorhanden sind. Wenn ein erwarteter Output fehlt (z.B. `interview.json`), wird kein Early-Return gemacht und der Task wird rebuilt.

```python
# Vorher:
if _state_inputs_match(...) and _state_outputs_exist(...):
    return False, None

# Nachher:
if _state_inputs_match(...) and _state_outputs_exist(...):
    current_outputs_missing = any(
        not path.exists() and not path.is_symlink()
        for path in _expected_outputs(batch_dir, person_id, task)
    )
    if not current_outputs_missing:
        return False, None
```

**Neuer Regressionstest:** `test_organize_batch_working_tree_rebuilds_interview_when_json_missing_despite_stale_state` in `app/tests/test_research_working_tree_intake.py`.

### 2. `.mfa_cache` zu `IGNORED_BATCH_DIR_NAMES` hinzugefügt
**Datei:** `scripts/research_data_intake/intake_batch_common.py`

```python
IGNORED_BATCH_DIR_NAMES = {"working", "reports", "exports", "__pycache__", ".mfa_cache"}
```

### 3. `_iter_batch_files` – manueller Directory Walk statt `rglob`
**Datei:** `scripts/research_data_intake/intake_batch_common.py`

`rglob("*")` betritt Verzeichnisse bevor der Filter greift. Ersetzt durch `_collect_batch_files`, das Verzeichnisse aus `IGNORED_BATCH_DIR_NAMES` überspringt, bevor es in sie einsteigt. Zusätzlich werden OSError beim Lesen einzelner Dateien ignoriert.

---

## Finaler Pipeline-Command

```
python scripts/research_data_intake/import_batch_to_production.py ^
  --batch en_batch_20260525 ^
  --person-id EN-L-0001 ^
  --target-language en ^
  --archive-root C:\dev\promat_data_archive ^
  --run-working ^
  --sync-tasks ^
  --cleanup-working-on-success
```

Hinweis: `--run-mfa` wurde nicht übergeben, da MFA bereits gelaufen war und `text.json` im Working vorhanden war. `--target-language en` ist zwingend (Default ist `es`).

---

## Ergebnisse

### Working Tree
- Vom Organizer rebuilt: wordlist (unchanged → rebuilt nach cleanup), text (unchanged → rebuilt nach cleanup), **interview** (rebuilt via Fix, Amberscript-JSON produziert)
- Nach erfolgreichem Import gelöscht (cleanup): `working/` nicht mehr vorhanden ✓

### Runtime `data/sessions/english/EN-L-0001-2026-S01`
| Artifact | Status |
|---|---|
| `metadata.json` | ✓ vorhanden, parsierbar |
| `alignment/wordlist.json` | ✓ |
| `alignment/text.json` | ✓ (aus MFA-Output) |
| `alignment/interview.json` | ✓ (aus Amberscript-Konvertierung) |
| `derived/wordlist.mp3` | ✓ |
| `derived/text.mp3` | ✓ |
| `derived/interview.mp3` | ✓ |
| `items/wordlist/wl_001…wl_095.mp3` | ✓ 95 Items |
| `items/text/t_01…t_56.mp3` | ✓ 56 Items |
| Verbotene Dateien (WAV, TextGrid, XLSX) | ✗ keine |

Runtime-Validierung: **OK**

### Archiv `C:\dev\promat_data_archive\sessions\en\EN-L-0001-2026-S01`
- Alle erwarteten Subdirs vorhanden (`alignment_source`, `raw`, `source`, `metadata`, `runtime`, `reports`, `secure`, `origin`)
- `metadata/archive_manifest.json`: `session_id=EN-L-0001-2026-S01`, `input_files=9`, `generated_runtime_files=158`, `warnings=[]`

Archiv-Validierung: **OK**

### DB-Upsert (PostgreSQL)
- Migration 0009 korrekt angewandt
- `research_people`: `EN-L-0001 speaker_type=learner l1=DE research_consent_signed=yes` ✓
- `research_sessions`: `EN-L-0001-2026-S01 documented_tasks=wordlist; text; interview lang=en corpus=english` ✓

### MFA
- War bereits gelaufen (text.json in working vorhanden)
- Im finalen Lauf **nicht** erneut ausgeführt (kein `--run-mfa`)

### Interview
- Amberscript-Parser hatte bereits Fixes für `[t_18],` und intra-word Brackets
- Conversion erfolgreich (Segmente, Tokens, Annotations produziert)

---

## Test-Status

45 Intake-Tests grün nach allen Änderungen:
- `test_research_working_tree_intake.py` (20)
- `test_research_production_importer.py` (19)
- `test_research_raw_sync_importer.py` (3)
- `test_research_intake_storage.py` (3)

Pre-existierender Fehler in `test_research_sessions.py::test_team_page_uses_structured_credits_cards_without_legacy_text` (encoding-Problem bei Sonderzeichen im Team-Page-Test) – nicht durch diesen Run verursacht.

---

## Offene Punkte vor vollständigem EN-Batch

1. **WAV-Rollenlogik: raw-als-source-Fallback** – Regel wurde definiert (siehe separate Aufgabe): Wenn kein processed WAV vorhanden ist, soll raw WAV als Derivationsbasis genutzt werden. Noch nicht implementiert.
2. **EN-L-0002 bis EN-L-0009** – erst importieren, wenn alle Artefakte geprüft und Regel aus Punkt 1 implementiert ist.
3. **`--run-mfa` für Folge-Personen** – wenn text.json nicht vorhanden ist, muss MFA erneut laufen. Docker-Pfad ist implementiert (`--mfa-executable docker`). Für EN-L-0002+ MFA-Status prüfen.
4. **Idempotenz-Test nach Cleanup** – nach `--cleanup-working-on-success` muss ein Folgelauf mit vorhandener Runtime als Update funktionieren (text=skip ist unkritisch wenn Artefakte bereits in Runtime vorhanden, aber ein erneutes `--run-mfa` wäre nötig wenn text.json nicht im Working vorhanden).

---

## Geänderte Dateien

| Datei | Änderungstyp |
|---|---|
| `scripts/research_data_intake/import/organize_batch_working_tree.py` | Fix: `_should_rebuild` prüft aktuelle Expected Outputs |
| `scripts/research_data_intake/intake_batch_common.py` | Fix: `.mfa_cache` zu IGNORED_BATCH_DIR_NAMES; `_iter_batch_files` → `_collect_batch_files` |
| `app/tests/test_research_working_tree_intake.py` | Neu: Regressionstest für Stale-State-Rebuild |
