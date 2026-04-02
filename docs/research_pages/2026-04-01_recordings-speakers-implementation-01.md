# PROMAT Research Pages Run 01

Datum: 2026-04-01

## Ziel des Runs

Das verbindliche PROMAT-Konzept für die spanischen Forschungsseiten `recordings` und `speakers` in einen bereits kohärent klickbaren Webapp-Stand überführen, inklusive Sprecherprofilseite und vorbereiteter Player-Zielroute, aber ohne den eigentlichen Player fachlich zu implementieren.

## Referenzdokument

Das aktive Referenzdokument liegt unter:

`docs/research_pages/promat_recordings_speakers.md`

Dieses Dokument ist bei künftigen Konzeptänderungen ausdrücklich mitzupflegen.

## Umgesetzte Punkte

* `recordings` als task-first-Arbeitsseite mit Tabs, Task-Beschreibung, Statuszeile, Filterpanel, Filter-Chips, Nullzustand und kompakter Tabellenansicht umgesetzt
* `speakers` als person-first-Arbeitsseite mit segmentiertem Schnellfilter, zusätzlichen Filtern, Statuszeile, Filter-Chips, kompakten Speaker-Cards und Task-Direktlinks umgesetzt
* Sprecherprofilseite unter Route über `person_id` angelegt
* Player-Zielroute als austauschbare Stub-Seite angelegt
* direkte Verlinkungen von `recordings`, `speakers` und Profil zur Player-Zielroute umgesetzt
* Rücksprunglogik im Player-Stub über Ursprungskontext vorbereitet
* Mobile-Filter als einklappbarer Bereich oberhalb der Ergebnisse umgesetzt
* Nulltreffer-Zustände für `recordings` und `speakers` umgesetzt

## Geänderte Dateien

* `app/src/app/research_sessions.py`
* `app/src/app/research_views.py`
* `app/src/app/routes/public.py`
* `app/templates/partials/_research_filters.html`
* `app/templates/pages/research_recordings.html`
* `app/templates/pages/research_speakers.html`
* `app/templates/pages/research_speaker_profile.html`
* `app/templates/pages/research_player_stub.html`
* `app/static/css/00_tokens.css`
* `app/static/css/20_layout.css`
* `app/static/css/30_components.css`
* `app/static/css/40_cards.css`
* `docs/research_pages/promat_recordings_speakers.md`

## Angelegte Routen und Komponenten

### Routen

* `/{ui_lang}/research/{language}/recordings`
  * bestehende generische Route für Spanisch auf spezialisierte Workbench-Ansicht umgelegt
* `/{ui_lang}/research/{language}/speakers`
  * bestehende generische Route für Spanisch auf spezialisierte Workbench-Ansicht umgelegt
* `/{ui_lang}/research/{language}/speakers/[person_id]`
  * neu als echte Profilseite
* `/{ui_lang}/research/{language}/player/[session_id]/[task]`
  * neu als Player-Stub

### Neue Komponenten / Vorlagen

* gemeinsames Filter-Partial für Desktop- und Mobile-Filter
* spezialisierte Template-Dateien für `recordings`, `speakers`, Sprecherprofil und Player-Stub
* dateibasierter Session-Reader für `data/sessions/{language}/{session_id}/metadata.json`
* View-Builder für Filterzustand, Chips, Tabellenzeilen, Speaker-Cards und Navigationslinks

## Daten- und Typing-Annahmen

* spanische Forschungsdaten werden derzeit dateibasiert aus `data/sessions/spanish/*/metadata.json` gelesen
* `person_id` und `session_id` bleiben getrennt; `speakers` gruppiert Sessions über `person_id`
* wenn für eine Person mehrere Sessions vorhanden sind, verwendet die Profilseite derzeit eine primäre Session und kann weitere Sessions zusätzlich aufführen
* die UI routet bereits auf alle drei kanonischen Tasks `isolated_speech`, `connected_speech`, `interview`
* aktuelle Dev-Beispielmetadaten dokumentieren diese Task-Abdeckung noch nicht überall vollständig; die Routing-Vorbereitung folgt daher dem Konzept, nicht nur dem momentanen Seed-Minimalstand
* strukturierte Exposure-Felder fehlen im aktuellen spanischen Dev-Datensatz; die UI zeigt in diesem Fall `Nicht erfasst` und erfindet keinen Ersatzwert

## Designentscheidungen

* `recordings` bleibt klar tabellarisch und vermeidet Card-Grid-Logik
* `speakers` nutzt kompakte Karten mit subtiler Top-Border für die Level-/Native-Codierung
* die Farbstufen für Lernenden-Level bewegen sich zwischen `--promat-wordmark-accent` und `--book-accent`
* Filter, Statuszeile und Chips wurden als ruhige Arbeitsoberfläche statt als Showcase-Komponenten umgesetzt
* Mobile verwendet ein `details`-basiertes Filter-Accordion statt dauerhafter Sidebar

## Offene Punkte

* der Player selbst ist weiterhin nur Stub und rendert noch keine Audios, Transkripte oder Vergleichsfunktionen
* die Exposure-Filter werden erst vollständig aussagekräftig, wenn strukturierte Exposure-Metadaten im Session-Bestand vorliegen
* andere Sprachbereiche verwenden weiterhin die generischen Platzhalterseiten
* die aktuelle spanische Dev-Datenlage enthält eine Mischung aus Seed-Sessions und älterer Platzhalter-Session; Mehrfach-Sessions pro Person sind deshalb schon sichtbar, aber noch nicht fachlich ausgebaut

## Bewusst noch nicht umgesetzte Teile

* kein echter Player
* kein Doppel-Player
* keine Vergleichslogik
* kein Wort-/Item-Filter auf `recordings`
* keine Inline-Audio-Elemente auf Übersichtsseiten
* keine Heritage-Speaker-Schnellfilter-UI
* keine ausgebauten Rückkehr-Parameter für vollständige Listen-Zustände im Player

## Technische Einschränkungen und Designannahmen

* der dateibasierte Reader setzt voraus, dass `metadata.json` pro Session vorhanden und parsebar ist
* der aktuelle Dev-Server läuft ohne Reloader; Template-/CSS-Verifikation erfordert deshalb einen expliziten Neustart oder einen Test-Client-Lauf
* weil die bestehenden Dev-Beispielsessions nicht überall dieselbe Task-Vollständigkeit dokumentieren, trennt die aktuelle Umsetzung bewusst zwischen Routing-Scaffolding und späterer medienbezogener Player-Prüfung

## Nächste sinnvolle Schritte

* Player-Fachansicht mit Audio, Transkript und sauberer Rücknavigation implementieren
* strukturierte Exposure-Felder in den spanischen Dev-Metadaten ergänzen
* das gleiche Workbench-Muster nach Bedarf auf weitere Sprachen übertragen