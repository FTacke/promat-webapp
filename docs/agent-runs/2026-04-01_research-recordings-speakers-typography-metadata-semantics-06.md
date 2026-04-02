# Research Recordings Speakers Typography Metadata Semantics 06

Datum: 2026-04-01

## Ziel

Bestehende Research-Seiten, die Profilansicht, `Sample` und die spanischen Dev-Session-Metadaten für präzisere sichtbare Benennungen, ehrlichere Profilsemantik und ein erweitertes Session-Metadatenmodell nachschärfen.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_sessions.py`
- `app/src/app/research_views.py`
- `app/src/app/routes/public_content.py`
- `app/templates/pages/research_recordings.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/30_components.css`
- `scripts/session_setup/seed_dev_spanish_example_sessions.py`
- `scripts/session_setup/dev_spanish_example_sessions.json`
- `scripts/import/session_metadata_xlsx_mapping.md`
- `scripts/import/session_metadata_xlsx_mapping.json`
- `data/sessions/spanish/ES-L-DE-B2-24-001/metadata.json`
- `docs/research_pages/promat_recordings_speakers.md`

## Geänderte Bereiche

- Session-Reader, View-Modelle und sichtbare Research-Texte in der Flask-App
- `recordings`-Template, `Sample`-Proof-Surface und bestehendes Komponenten-CSS
- spanische Dev-Seeds und versionierte Beispiel-Metadaten
- XLSX-Mapping, Plattform-/Datenstruktur-Doku und Research-Referenzdoku
- neue Run-Dokumentation unter `docs/research_pages/`

## Wichtige Entscheidungen

- `recorded_by` wird als neues sessionbezogenes Metadatenfeld eingeführt und bleibt technisch englisch benannt
- die sichtbare deutsche UI bezeichnet `recorded_by` als `Explorator:in`
- die Profilseite zeigt für Lernende `Level (Selbsteinschätzung)` statt einer getrennten Anzeige von `Level` und `Selbsteinschätzung`
- die sichtbare Session-Bezeichnung auf Profilseiten lautet `Ausgewählte Session`
- die Ergebnistabelle von `recordings` nutzt task-spezifische Linktexte statt einer generischen Aktion `Aufnahme`

## Abweichungen

- Keine neue Grundarchitektur, keine neue DB-Struktur und keine Abweichung von den bestehenden Runtime-Grenzen

## Verifikation

- statische Fehlerprüfung der geänderten Python-, Template-, CSS- und Doku-Dateien
- spanische Dev-Sessions nach der Einführung von `recorded_by` neu generiert
- Routenvalidierung für `recordings`, Profilseite und `Sample`

## Offene Punkte

- Historische frühere Run-Logs bleiben als Historie unverändert und verwenden teilweise noch ältere Formulierungen.
- Der fiktionale Dev-Datensatz bleibt bewusst klein und dient weiterhin nur als strukturtreue Entwicklungsbasis.