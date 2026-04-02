# Recordings Speakers Native Comparison Cleanup 08

Datum: 2026-04-02

## Ziel

Den bestehenden PROMAT-Stand für `speakers`, `recordings`, Profilseite, `Sample`, spanische Dev-Seeds und die aktive Doku gezielt so bereinigen, dass Native Speaker fachlich nur noch als Vergleichsprofile für Zielsprachenaussprache erscheinen und nicht mehr mit lernendenzentrierter Sprachbiographie überfrachtet werden.

## Schwerpunkt dieses Runs

* Native-Speaker-Profile sichtbar verschlanken
* Native-Speaker-Seeds und `metadata.json` von nicht benötigten Sprachbiographie-Feldern bereinigen
* `Sample` für Native-Speaker-Vergleichsprofile nachziehen
* aktive Referenz-, Plattform- und Mapping-Doku korrigieren
* ausdrücklich festhalten, dass die XLSX-Importpipeline weiterhin bewusst offen bleibt

## Geänderte Bereiche

* `app/src/app/research_views.py`
* `app/templates/pages/sample_page.html`
* `scripts/session_setup/seed_dev_spanish_example_sessions.py`
* `scripts/session_setup/dev_spanish_example_sessions.json`
* `data/sessions/spanish/ES-N-ES_STD-26-001/metadata.json`
* `data/sessions/spanish/ES-N-MX_STD-26-001/metadata.json`
* `docs/research_pages/promat_recordings_speakers.md`
* `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
* `scripts/import/session_metadata_xlsx_mapping.md`
* `scripts/import/session_metadata_xlsx_mapping.json`

## Umgesetzt

* Native-Speaker-Profile zeigen jetzt nur noch Vergleichsangaben: `Person-ID`, `Ausgewählte Session`, `Sprechergruppe`, `Geschlecht`, `Geburtsjahr`, `Aufnahmedatum`, `Aufnahmejahr`, `Explorator:in`, `Herkunftsland`, `Herkunftsregion`, `Standardvarietät` und die verfügbaren Aufzeichnungen `Wortliste` und `Text`
* sichtbare lernendenzentrierte Felder wurden aus Native-Speaker-Profilen entfernt: `L1`, `L1 der Mutter`, `L1 des Vaters`, `Zusätzliche Sprachen`, `Sprachaufenthalte`, `Level (Selbsteinschätzung)`
* die spanischen Native-Speaker-Dev-Seeds führen diese Felder nicht mehr und schreiben entsprechend bereinigte `metadata.json`
* `Sample` enthält jetzt ein eigenes schlankes Native-Speaker-Vergleichsprofil statt einer impliziten Lernendenlogik
* Plattform- und Referenzdoku unterscheiden jetzt klar zwischen allgemeinem Modellvertrag und aktivem Native-Speaker-Vergleichsprofil
* die Mapping-Doku hält ausdrücklich fest, dass die XLSX-Dateien derzeit nur den Vertrag definieren und die echte Importpipeline später mit realen Daten gebaut wird

## Verifikation

* Editor-Diagnostik für die geänderten Python- und Template-Dateien ohne Fehler
* spanische Dev-Seeds erfolgreich neu generiert
* generierte Native-`metadata.json` geprüft: keine `l1`-, `mother_l1`-, `father_l1`- oder `additional_languages`-Felder mehr vorhanden
* Flask-Testclient geprüft: `/de/research/spanish/speakers/P-0002` liefert `200`, zeigt Herkunfts- und Varietätsangaben und blendet Native-Sprachbiographie-Felder aus
* `Sample` geprüft: Native-Speaker-Beispiel zeigt das neue `Vergleichsprofil · Native Speaker`

## Offen bewusst nicht umgesetzt

* keine echte XLSX-Importpipeline
* kein echter Player
* kein Doppel-Player
* keine Vergleichslogik
* keine neue Grundarchitektur

## Offene Restpunkte

* Die XLSX-Mapping-Dateien sind weiterhin nur ein Vertrag; produktiver Importcode für reale XLSX-Daten ist bewusst nicht Teil dieses Runs.
* Das allgemeine Datenmodell kann sprachbiographische Personenfelder technisch weiterhin tragen; im aktiven Native-Speaker-Vergleichsprofil werden sie jedoch nicht verwendet.
