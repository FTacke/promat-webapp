# Research Recordings Speakers Native Comparison Cleanup 08

Datum: 2026-04-02

## Ziel

Den aktuellen Research-Stand für `recordings`, `speakers`, Sprecherprofil, `Sample`, spanische Dev-Seeds und die aktive Doku so korrigieren, dass Native Speaker im PROMAT-UI nur noch als Vergleichsprofile erscheinen und die echte XLSX-Importpipeline weiterhin bewusst offen bleibt.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_views.py`
- `app/templates/pages/sample_page.html`
- `scripts/session_setup/seed_dev_spanish_example_sessions.py`
- `scripts/session_setup/dev_spanish_example_sessions.json`
- `data/sessions/spanish/ES-N-ES_STD-26-001/metadata.json`
- `data/sessions/spanish/ES-N-MX_STD-26-001/metadata.json`
- `docs/research_pages/promat_recordings_speakers.md`
- `scripts/import/session_metadata_xlsx_mapping.md`
- `scripts/import/session_metadata_xlsx_mapping.json`

## Geänderte Bereiche

- Native-Speaker-Rendering in den Research-View-Modellen
- Native-Speaker-Beispiel auf `Sample`
- spanisches Seed-Manifest, Seed-Skript und generierte Native-`metadata.json`
- aktive Referenzdoku, Plattformdoku und Import-/Mapping-Doku
- neue Run-Dokumentation unter `docs/research_pages/` und `docs/agent-runs/`

## Wichtige Entscheidungen

- Native Speaker sind im aktiven PROMAT-UI Vergleichsprofile für Zielsprachenaussprache und keine zweite lernendenartige Sprachbiographie-Gruppe
- Die Felder `l1`, `mother_l1`, `father_l1` und `additional_languages` bleiben im allgemeinen Modell technisch möglich, werden aber für die aktuellen Native-Speaker-Vergleichsprofile nicht sichtbar genutzt und in den spanischen Dev-Native-Seeds nicht gepflegt
- Native-Speaker-Profile zeigen nur noch die für Vergleichsprofile relevanten Angaben zu Herkunft, Varietät und Aufnahme
- Die XLSX-Mapping-Dateien definieren weiterhin nur den Vertrag; die echte XLSX-Importpipeline bleibt bewusst unimplementiert bis zu einer späteren Phase mit realen Daten

## Abweichungen

- Keine neue Grundarchitektur, keine neue Importarchitektur und keine Abweichung von den bestehenden Runtime-Grenzen

## Verifikation

- statische Fehlerprüfung der geänderten Python- und Template-Dateien ohne Befunde
- spanische Dev-Seeds neu generiert
- generierte Native-`metadata.json` geprüft: keine unnötigen Sprachbiographie-Felder mehr vorhanden
- Flask-Testclient-Check erfolgreich für das Native-Speaker-Profil und die `Sample`-Seite

## Offene Punkte

- Die XLSX-Mapping-Dateien sind weiterhin vertragliche Dokumentation und noch keine laufende Importpipeline.
- Historische ältere Run-Logs bleiben unverändert und können frühere Zwischenstände enthalten.

## Nächste sinnvolle Schritte

- Bei real verfügbaren XLSX-Daten eine Importpipeline bauen, die direkt auf dem dokumentierten Vertrag aufsetzt.
- Danach optional automatisierte Tests ergänzen, die Native- und Learner-Profile gegen ihre jeweiligen Sichtbarkeitsregeln absichern.
