# Text MFA Working Import 120

Datum: 2026-04-14

## Ziel

Einen batch-lokalen Rückimport der vorhandenen MFA-Ergebnisse in `working/{person_id}/text/alignment/text.json` implementieren, ohne Produktionsdaten unter `data/` zu berühren.

## Consulted Sources

- `AGENTS.md`
- `scripts/AGENTS.md`
- `scripts/research_data_intake/AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `scripts/research_data_intake/README.md`
- `scripts/research_data_intake/textgrid_support.py`
- `scripts/research_data_intake/alignment_export/wordlist_alignment.py`
- `scripts/research_data_intake/import/spanisch_batch/working/ES-L-0001/text/mfa_manifest.json`
- `scripts/research_data_intake/import/spanisch_batch/working/ES-L-0001/text/mfa_output/text_001_d_01.TextGrid`

## Geänderte Bereiche

- `scripts/research_data_intake/textgrid_support.py`
- `scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py`
- `scripts/research_data_intake/README.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`
- `docs/agent-runs/2026-04-14_text-mfa-working-import-120.md`

## Wichtige Entscheidungen

- Der Rückimport bleibt vollständig im Working-Tree und schreibt nur nach `working/{person_id}/text/alignment/text.json`.
- Manifest-Einträge bleiben die führenden `items`; MFA-Wortintervalle werden als `tokens` innerhalb dieser Items importiert.
- Tokenzeiten werden über den Manifest-Offset auf die globale Zeitachse des Ursprungsaudios zurückgerechnet und danach in ms serialisiert.
- Da die End-Metadatenintegration noch nicht erfolgt ist, bleibt `session_id` im Working-Tree-JSON vorläufig `null`.
- `audio.full_mp3` wird bereits auf die spätere kanonische relative Zielstruktur `derived/text.mp3` gesetzt, ohne das MP3 in diesem Schritt zu erzeugen.

## Abweichungen

- Keine Abweichung von der aktiven Governance.
- Die erzeugten `text.json`-Dateien sind batch-lokale Working-Artefakte und noch keine produktiv nach `data/` übertragenen Session-Artefakte.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m py_compile scripts/research_data_intake/textgrid_support.py scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py`
- `c:/dev/promat/.venv/Scripts/python.exe scripts/research_data_intake/alignment_export/import_text_mfa_alignment.py --batch-dir spanisch_batch --dry-run`
- Dry-Run-Ergebnis: 11 Personen gefunden, 11 importierbar, 0 strukturell übersprungen, nur die erwartete Warnung zu noch nicht integrierten `session_id`-Werten.

## Offene Punkte

- Die spätere Endintegration muss `session_id` aus Intake-/Produktionsmetadaten auflösen.
- Der spätere Transfer nach `data/` und die Bereitstellung des finalen `derived/text.mp3` bleiben separate Pipeline-Schritte.
- OOV-Qualitätsthemen aus dem MFA-Lauf bleiben in den MFA-Logs und sind nicht Gegenstand dieses JSON-Rückimports.

## Nächste sinnvolle Schritte

1. Den nun batch-lokal erzeugten `alignment/text.json`-Vertrag in einen späteren, separaten Transfer nach `data/sessions/...` überführen.
2. In diesem späteren Endimport `session_id` aus der eigentlichen Intake-/Session-Metadatenintegration auflösen.
3. Danach die produktive Nutzung im Player gegen die erzeugten `tokens` und Satzgrenzen testen.