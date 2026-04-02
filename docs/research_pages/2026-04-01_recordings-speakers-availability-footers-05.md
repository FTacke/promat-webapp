# Recordings Speakers Availability Footers 05

Datum: 2026-04-01

## Ziel

Den bestehenden Research-Stand für `recordings`, `speakers`, Profil und `Sample` ohne neue Grundarchitektur in Verfügbarkeitslogik, Benennung der Aufzeichnungsbereiche, Speaker-Card-Footern und kleineren Profilkorrekturen konsistent schärfen.

## Schwerpunkt dieses Runs

* Native Speaker bieten keine Interview-Aufzeichnungen mehr an
* Speaker-Cards und Profile verwenden den Bereichstitel `Aufzeichnungen`
* Card-Footer bleiben unten verankert und führen ruhige Textlinks mit kleinem Pfeil
* Profil-Badges erhalten sauberere Abstände
* der Zurück-Link der Profilseite steht ganz am Ende als eigenes Navigationselement
* `recordings` zeigt Task-Panels nur noch für im aktuellen Datenausschnitt tatsächlich verfügbare Aufzeichnungen; die Tabellenaktion wurde in einem späteren Run weiter auf task-spezifische Labels geschärft

## Geänderte Bereiche

* `app/src/app/research_sessions.py`
* `app/src/app/research_views.py`
* `app/templates/pages/research_speakers.html`
* `app/templates/pages/research_speaker_profile.html`
* `app/templates/pages/sample_page.html`
* `app/static/css/30_components.css`
* `app/static/css/40_cards.css`
* `scripts/session_setup/seed_dev_spanish_example_sessions.py`
* `docs/research_pages/promat_recordings_speakers.md`

## Umgesetzt

* die verfügbare Task-Menge wird jetzt pro Session fachlich aus den dokumentierten Task-Typen gelesen; Native Speaker verlieren dabei systematisch `interview`
* `speakers`, Profilseite und Player-Stub verlinken nur noch auf tatsächlich verfügbare Aufzeichnungen
* `recordings` berechnet task-spezifische Counts im jeweils gefilterten Datenausschnitt und blendet nicht verfügbare Task-Panels aus
* Speaker-Cards nutzen `Aufzeichnungen` als Bereichstitel, ruhige Textlinks mit Pfeil und einen stabilen Footer am Kartenende
* Profilseiten nutzen `Aufzeichnungen` als Bereichstitel; der Zurück-Link steht nach dem Aufzeichnungsblock ganz unten
* `Sample` zeigt aktualisierte Learner- und Native-Speaker-Cards sowie Learner-/Native-Varianten des Aufzeichnungsbereichs

## Verifikation

* Fehlerprüfung für die geänderten Python-, Template-, CSS- und Doku-Dateien ohne Befunde
* spanische Dev-Seeds nach der Native-Speaker-Korrektur neu generiert
* Routen erfolgreich geprüft: `/de/research/spanish/recordings`, `/de/research/spanish/speakers`, `/de/research/spanish/speakers/P-0002`, `/de/sample`
* Native-Speaker-Verfügbarkeit geprüft: kein Interview-Link auf Native-Speaker-Card oder Native-Profil, kein Interview-Task-Panel auf `recordings` bei `speaker_type=native_speaker`, Native-Interview-Playerroute liefert `404`

## Offen bewusst nicht umgesetzt

* kein echter Player
* keine neue Datenarchitektur oder parallele DB-Struktur
* keine Rücknahme der bestehenden Feldlogik um `stays_in_target_country`, `origin_country` und `origin_region`

## Offene Restpunkte

* Die dev-seitige Task-Abdeckung bleibt insgesamt weiterhin schmal; außerhalb der hier gezielt geschärften Native-Speaker-Regel bilden die übrigen Sessions nur die aktuell dokumentierten Tasks ab.
* Historische ältere Run-Dokumente wurden nicht sprachlich rückwirkend normalisiert.