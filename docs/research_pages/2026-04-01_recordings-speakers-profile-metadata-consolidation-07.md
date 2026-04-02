# Recordings Speakers Profile Metadata Consolidation 07

Datum: 2026-04-01

## Ziel

Den bestehenden Research-Stand für `recordings`, `speakers`, Profilseite, `Sample`, spanische Dev-Seeds und die aktive Referenzdokumentation auf einen konsistenten Endstand für Profilsemantik, Sprachbiographie und Session-Metadaten bringen.

## Schwerpunkt dieses Runs

* finale Task-Beschreibungen für `Wortliste`, `Text` und `Interview`
* keine sichtbaren Rohwerte `baseline` oder `follow_up` in Profilen
* `Explorator:in` als sichtbare UI-Fassung von `recorded_by`
* neue Personenfelder `mother_l1`, `father_l1` und `additional_languages`
* detaillierte `Sprachaufenthalte` über strukturierte `exposure_entries`
* `DE` als `l1` für alle fiktionalen Lernenden-Beispielsessions
* harte Bereinigung der aktiven Research-Referenzdoku

## Geänderte Bereiche

* `app/src/app/research_sessions.py`
* `app/src/app/research_views.py`
* `app/templates/pages/research_speaker_profile.html`
* `app/templates/pages/sample_page.html`
* `app/static/css/30_components.css`
* `scripts/session_setup/seed_dev_spanish_example_sessions.py`
* `scripts/session_setup/dev_spanish_example_sessions.json`
* `scripts/import/session_metadata_xlsx_mapping.md`
* `scripts/import/session_metadata_xlsx_mapping.json`
* `data/sessions/spanish/`
* `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
* `docs/research_pages/promat_recordings_speakers.md`

## Umgesetzt

* das Research-Modell liest jetzt Familien-L1, zusätzliche Sprachen und strukturierte Sprachaufenthalte direkt aus `metadata.json`
* Profilseiten zeigen Lernenden-Sprachbiographie mit detaillierten Aufenthalten statt nur einer binären Ja/Nein-Logik
* sichtbare Rohkontexte wurden aus der Profilanzeige entfernt
* alle spanischen Dev-Lernenden wurden auf `DE` als `l1` vereinheitlicht und mit realistischeren Dummy-Feldern ergänzt
* der Seed-Lauf entfernt alte dev-generierte Session-Ordner, wenn sich Session-IDs durch Manifeständerungen verschieben
* XLSX-Mapping und Plattformdoku unterscheiden jetzt explizit Person-, Session- und `exposure_entries`-Ebene
* die Research-Referenzdoku beschreibt nur noch den aktuell gültigen Stand

## Verifikation

* Python-/Template-/CSS-Diagnostik für die geänderten App-Dateien ohne Fehler
* spanische Dev-Seeds neu generiert
* generierter Session-Baum manuell geprüft

## Offen bewusst nicht umgesetzt

* kein echter Player
* keine neue Datenbankarchitektur
* keine Vergleichs- oder Doppel-Player-Logik

## Offene Restpunkte

* Die Importlogik für echte XLSX-Dateien ist weiterhin noch nicht implementiert; die aktualisierten Mapping-Dateien definieren vorerst den verbindlichen Vertrag.
* Historische ältere Run-Dokumente bleiben unverändert und können frühere Zwischenbegriffe enthalten.
