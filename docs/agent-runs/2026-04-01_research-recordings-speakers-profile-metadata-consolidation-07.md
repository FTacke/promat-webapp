# Research Recordings Speakers Profile Metadata Consolidation 07

Datum: 2026-04-01

## Ziel

Bestehende Research-Seiten, `Sample`, spanische Dev-Session-Metadaten und die aktive Referenzdokumentation für den finalen Stand von Profilsemantik, Sprachbiographie und Session-Metadaten konsolidieren.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_sessions.py`
- `app/src/app/research_views.py`
- `app/templates/pages/research_speaker_profile.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/30_components.css`
- `scripts/session_setup/seed_dev_spanish_example_sessions.py`
- `scripts/session_setup/dev_spanish_example_sessions.json`
- `scripts/import/session_metadata_xlsx_mapping.md`
- `scripts/import/session_metadata_xlsx_mapping.json`
- `data/sessions/spanish/`
- `docs/research_pages/promat_recordings_speakers.md`

## Geänderte Bereiche

- Research-Sessionreader, View-Modelle, Profiltemplate, Sample und Component-CSS
- spanische Dev-Seeds, Seed-Manifest und generierte `metadata.json`
- XLSX-Mapping und Plattform-/Research-Dokumentation
- neue Run-Dokumentation unter `docs/research_pages/` und `docs/agent-runs/`

## Wichtige Entscheidungen

- `recorded_by` bleibt das technische Session-Feld; die sichtbare deutsche UI zeigt `Explorator:in`
- Lernenden-Profile priorisieren detaillierte `exposure_entries`; `stays_in_target_country` bleibt das kompakte Summen- und Filterfeld
- `mother_l1`, `father_l1` und `additional_languages` sind aktive Personenfelder und gehören in Seeds, `metadata.json`, Mapping und Profilanzeige zusammengeführt
- der aktive XLSX-Vertrag wird in `sessions`- und `exposure_entries`-Ebene getrennt beschrieben, statt alle Informationen in eine flache einzige Tabelle zu drücken

## Abweichungen

- Keine neue Grundarchitektur, keine neue Research-DB und keine Abweichung von den bestehenden Runtime-Grenzen

## Verifikation

- statische Fehlerprüfung der geänderten Python-, Template- und CSS-Dateien
- Seed-Lauf mit dem aktualisierten Manifest erfolgreich ausgeführt
- manueller Check des resultierenden Session-Baums und exemplarischer `metadata.json`-Dateien

## Offene Punkte

- Die aktualisierten XLSX-Mapping-Dateien definieren den Vertrag für eine spätere echte Importimplementierung, sind aber selbst noch keine Importpipeline.
- Historische frühere Run-Logs bleiben als Historie unverändert.

## Nächste sinnvolle Schritte

- Test- oder Importcode ergänzen, der den neuen `sessions`-/`exposure_entries`-Vertrag automatisiert validiert.
- Nach einer UI-Abnahme optional echte Route-Checks gegen die laufende Dev-App ergänzen.
