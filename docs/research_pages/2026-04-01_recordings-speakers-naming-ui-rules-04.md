# Recordings Speakers Naming UI Rules 04

Datum: 2026-04-01

## Ziel

Den bestehenden Research-Stand für `recordings`, `speakers`, Profil und `Sample` ohne neue Grundarchitektur in Benennung, Layout-Hierarchie, UI-Systemregeln und sichtbaren deutschen Texten konsistent einfrieren.

## Kernentscheidungen dieses Runs

* feste kurze Task-Namen: `Wortliste`, `Text`, `Interview`
* feste längere Erläuterungen: `Isolierte Aussprache (Wortliste)`, `Zusammenhängende Aussprache (Text/Sätze)`, `Interview zur Aussprache`
* sichtbare deutsche UI-Texte verwenden echte Umlaute und `ß`
* Filter-Chips und Badges folgen jetzt getrennten, globalen UI-Regeln
* Profilkopf ohne redundante Meta-Zeile
* Zurück-Link als eigene Navigation außerhalb des Aufgabencontainers
* Desktop-Filterlayout in zwei bis drei Spalten

## Geänderte Bereiche

* `app/src/app/research_sessions.py`
* `app/src/app/research_views.py`
* `app/templates/pages/research_speakers.html`
* `app/templates/pages/research_recordings.html`
* `app/templates/pages/research_speaker_profile.html`
* `app/templates/pages/sample_page.html`
* `app/static/css/00_tokens.css`
* `app/static/css/20_layout.css`
* `app/static/css/30_components.css`
* `AGENTS.md`
* `app/AGENTS.md`
* `docs/AGENTS.md`
* `.github/instructions/repo.instructions.md`
* `.github/copilot-instructions.md`
* `docs/research_pages/promat_recordings_speakers.md`

## Umgesetzt

* die zentrale Task-Definition liefert jetzt konsistent `Wortliste / Text / Interview`
* `recordings` zeigt kurze Paneltitel mit längerer Erläuterung darunter
* Speaker-Cards und Profilaufgaben verwenden dieselben kurzen Tasktitel
* Profilkopf und Profilnavigation wurden getrennt; der Zurück-Link steht nicht mehr im Aufgabencontainer
* Filter-Chips sind kleiner, getönt und klar von Buttons getrennt
* Badges folgen eigener Größen-, Abstands- und Tönungslogik
* die Filterformulare nutzen auf Desktop ein mehrspaltiges Grid
* sichtbare deutsche Texte in den betroffenen Research-Komponenten und Sample-Dummys wurden auf echte Umlaute umgestellt

## Offene Restpunkte

* ältere historische Run-Dokumente bleiben als Historie bestehen und wurden nicht rückwirkend sprachlich komplett normalisiert
* task-spezifische Counts bleiben weiterhin an die aktuelle gefilterte Ergebnismenge gebunden, solange keine feinere Task-Datenbasis vorliegt
