# PROMAT Restkonsistenz aktiver Regeln

Datum: 2026-04-02

## Ziel

Nur die verbliebenen aktiven Restwidersprueche nach dem Konsistenz-Umbau beseitigen: `heritage_speaker`/`H`, XLSX-Exposure-Verknuepfung, aktive Vokabular-Casings und die breite `Vocabularies`-Logik.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `docs/conventions/README.md`
- `docs/data-intake/README_promat_intake_template_revised.md`
- `docs/research_pages/promat_recordings_speakers.md`
- `scripts/import/session_metadata_xlsx_mapping.md`
- `scripts/import/session_metadata_xlsx_mapping.json`
- `app/src/app/config/data_conventions.py`

## Geänderte Bereiche

- aktive Hauptspezifikation und aktive Kurzkonventionen unter `docs/`
- aktive Repo-, Docs-, App- und Scripts-Governance unter `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`, `scripts/AGENTS.md`
- aktive Workspace-Instruktionen unter `.github/`
- Intake-Workbook- und XLSX-Mapping-Vertrag unter `docs/data-intake/` und `scripts/import/`
- Runtime-Vokabular fuer `standard_variety` unter `app/src/app/config/`

## Wichtige Entscheidungen

- Aktive `speaker_type`-Werte bleiben nur `learner` und `native_speaker`; aktive ID-Marker bleiben nur `L` und `N`.
- Der Intake-Vertrag fuer `Exposure` bleibt verbindlich person- plus session-ref-basiert: `person_id` + `session_ref`, nie `session_id`.
- Aktive technische Casing-Regeln sind verbindlich: `target_language` lowercase, `standard_variety` lowercase snake_case, `unknown` lowercase, `l1_code` uppercase.
- Schweizer Standardvarietaeten werden aktiv nur noch als `fr_ch_std` und `de_ch_std` gefuehrt; `ch_std` ist kein aktiver Standard mehr.
- Das aktive Intake-Modell bleibt das breite Blatt `Vocabularies`; eine normalisierte Feld-Wert-Alternative ist kein aktiver Soll-Stand.

## Abweichungen

- Keine.

## Verifikation

- repo-weite Suchlaeufe nach `heritage_speaker`, `FR-H-`, `H`, `ch_std`, `UNKNOWN`, alten Exposure-`session_id`-Aussagen und Feld-Wert-Resten in aktiven Bereichen ausgefuehrt
- aktive Intake-Beispiele, Mapping-Dateien und Governance-Dateien gegeneinander abgeglichen
- fokussierter Pytest-Lauf `app/tests/test_research_sessions.py` erfolgreich

## Offene Punkte

- Historische Run-Logs enthalten weiterhin fruehere Zwischenstaende, beanspruchen aber keine normative Autoritaet.
- Fuer die neu disambiguierten Werte `fr_ch_std` und `de_ch_std` existieren aktuell noch keine aktiven Dev-Beispieldaten, nur die Runtime- und Doku-Standards.

## Nächste sinnvolle Schritte

- beim spaeteren Doku-Abbau nur noch die jetzt vereinheitlichten aktiven Referenzstellen konsolidieren
- kuenftige Intake- oder Seed-Erweiterungen direkt auf die festgezurrten Vokabular- und `session_ref`-Regeln aufsetzen