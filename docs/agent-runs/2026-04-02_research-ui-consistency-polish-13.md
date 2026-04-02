# Research-UI konsistenter und ruhiger gemacht

Datum: 2026-04-02

## Ziel

Die spanische Research-UI für `speakers`, `profile` und `recordings` nach dem person_id-/session_id-Umbau visuell und semantisch konsistenter machen, ohne neue Nebenbaustellen zu eröffnen.

## Consulted Sources

- `docs/spec/research-access.md`
- `docs/spec/platform-data-files.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_speakers.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/templates/pages/research_recordings.html`

## Geänderte Bereiche

- `app/src/app/research_views.py`: Profilkopf von ausgewählter Session auf Session-Anzahl umgestellt, native Tabellenwerte für `Niveau`/`L1` geleert, deaktivierte Task-Zustände für Profil und recordings modelliert
- `app/templates/pages/research_speaker_profile.html`: Profilkopf-Sekundärzeile auf `Zugeordnete Sessions` umgestellt, deaktivierte Task-Kacheln ergänzt
- `app/templates/pages/research_recordings.html`: deaktivierte Task-Panels ergänzt, Tabellenstruktur per `colgroup` und expliziten Spaltenklassen präzisiert
- `app/templates/pages/research_speakers.html`: unverändert in der Struktur, aber weiterverwendet mit kompakteren Task-Chips und angeglichenem Divider-Rhythmus
- `app/static/css/30_components.css`: Exposure-Liste entchromt, Task-Panels/Task-Kacheln um Disabled-Stile ergänzt, Tabellenlayout und Header-Wrapping stabilisiert, Speaker-Task-Chips weiter verdichtet
- `app/static/css/40_cards.css`: Divider-Abstände in Speaker-Cards über gemeinsames Spacing-Token angeglichen
- `app/static/css/00_tokens.css`: wiederverwendbares Divider-Spacing-Token ergänzt
- `app/tests/test_research_sessions.py`: Regressionstests für Session-Anzahl im Profilkopf, deaktiviertes Native-Interview und leere Native-Spalten in recordings ergänzt
- `docs/spec/research-access.md`: aktive Regeln zu Profilkopf, Exposure-Liste, deaktivierten Tasks und recordings-Spalten präzisiert

## Verifikation

- fokussierte Tests für Session-Logik und Research-View-Model
- Learner-Profil mit mehreren Sessions und Session-Fokus geprüft
- Native-Speaker-Profil mit genau einer Session geprüft
- Exposure-Fälle geprüft für 0 Einträge, 1 Eintrag mit Notiz, 1 Eintrag ohne Notiz und mehrere Einträge mit teils leerer Notiz
- recordings-Tabelle mit gemischten Learner-/Native-Zeilen und mittleren Breiten geprüft
- deaktiviertes `Interview` in Profil und recordings-Task-Panels geprüft
- Speaker-Cards für Learner und Native Speaker mit vereinheitlichten Dividern und kompakteren Task-Chips geprüft

## Offene Punkte

- Nach diesem Folge-Run keine weiteren offenen UI-Restpunkte in den angefassten Bereichen gesehen.