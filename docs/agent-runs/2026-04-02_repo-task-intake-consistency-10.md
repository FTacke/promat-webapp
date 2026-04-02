# PROMAT Repo-Consistency Sweep fuer Task-Keys und Intake

Datum: 2026-04-02

## Ziel

Den aktiven Repo-Stand systematisch auf die zuletzt akzeptierten PROMAT-Entscheidungen ziehen: personbasierter Research-Zugang, kanonische `person_id`/`session_id`, aktive Task-Keys `wordlist`/`text`/`interview`, Native-Speaker-Sonderfall und Intake-Workbook-Endstand.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `scripts/session_setup/seed_dev_spanish_example_sessions.py`
- `scripts/import/session_metadata_xlsx_mapping.md`
- `scripts/import/session_metadata_xlsx_mapping.json`
- `docs/README_promat_intake_template_revised.md`

## Geänderte Bereiche

- zentrale Research-Vokabulare und Task-Definitionen unter `app/src/app/`
- spanischer Dev-Seed und Research-Tests
- aktive Governance unter `.github/`, `AGENTS.md` und `docs/conventions/`
- aktive Spezifikation und Referenzdoku fuer Tasks, Session-Dateinamen und Intake-Mapping
- Session-Metadaten und Dateibenennung unter `data/sessions/spanish/`

## Wichtige Entscheidungen

- Aktive technische Task-Keys sind repo-weit `wordlist`, `text`, `interview`; `isolated_speech` und `connected_speech` bleiben nur noch als historische Altbegriffe zulaessig.
- Der aktive `speaker_type`-Standard fuer den aktuellen Intake- und Runtime-Stand ist auf `learner` und `native_speaker` begrenzt; `heritage_speaker` bleibt kein aktiver Projektwert ohne echte Nutzung.
- Der XLSX-/Intake-Vertrag folgt verbindlich dem Workbook-Endstand: `speaker_type` in `Research_Person`, `session_ref` als Intake-Verknuepfung, leere `session_id` im Intake und breites `Vocabularies`-Blatt.
- Der veraltete Repo-Platzhalterordner mit legacy Session-Pfad wurde aus `data/sessions/spanish/` entfernt; der kanonische Platzhalter bleibt `ES-L-0901-2024-S01`.

## Abweichungen

- Keine.

## Verifikation

- repo-weite Suchlaeufe nach `isolated_speech`, `connected_speech`, `heritage_speaker` und alten Placeholder-Pfaden in aktiven Bereichen ausgefuehrt
- spanischer Dev-Seed mit aktualisierten Task-Namen neu geschrieben
- Session-Dateien und Task-Unterordner unter `data/sessions/spanish/` auf `wordlist` und `text` umbenannt
- fokussierte Research-Tests nach der Umstellung ausgefuehrt

## Offene Punkte

- Historische Run-Logs und Start-Logs enthalten weiterhin fruehere Task-Namen und alte Platzhalterpfade als Historie.
- Kein kompletter Browser-E2E-Lauf gegen einen neu gestarteten Dev-Server in diesem Run.

## Nächste sinnvolle Schritte

- alte historische Dokumente bei Bedarf spaeter explizit als Legacy-/Historienreferenz sammeln oder querschriftlich markieren
- eine spaetere echte Intake-Importpipeline direkt auf das jetzt festgezogene Workbook-Modell aufsetzen
