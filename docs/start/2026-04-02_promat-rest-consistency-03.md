# PROMAT Restkonsistenz aktiver Regeln

Datum: 2026-04-02

## Ziel

Den abgeschlossenen Konsistenz-Umbau mit einem kleinen Schlusslauf sauber abschliessen, ohne neue Doku-Strukturen aufzubauen.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `docs/conventions/README.md`
- `docs/data-intake/README_promat_intake_template_revised.md`
- `scripts/import/session_metadata_xlsx_mapping.md`
- `app/src/app/config/data_conventions.py`

## Geänderte Bereiche

- aktive Spezifikation, Conventions und Governance
- Intake-Workbook-Doku und XLSX-Mapping-Vertrag
- Runtime-Konstanten fuer `standard_variety`

## Wichtige Entscheidungen

- `heritage_speaker` und Marker `H` bleiben ausserhalb historischer Kontexte kein aktiver Standard.
- `Exposure` bleibt im Intake an `person_id` plus `session_ref` gebunden; `session_id` bleibt dort leer.
- Aktive technische Casing-Regeln sind nun explizit ueber Spezifikation, Governance, Intake und Mapping festgezogen.

## Abweichungen

- Keine.

## Verifikation

- gezielte repo-weite Suchlaeufe nach den benannten Altbegriffen in aktiven Bereichen
- fokussierter Testlauf fuer Research-Session-Helfer und Aggregation erfolgreich

## Offene Punkte

- Historische Logs bleiben als Historie erhalten und wurden in diesem Schlusslauf nicht redaktionell bereinigt.

## Nächste sinnvolle Schritte

- die spaetere strukturelle Doku-Reduktion nur noch auf Basis dieses bereinigten aktiven Regelstands durchfuehren