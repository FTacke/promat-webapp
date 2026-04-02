---
tags: promat, research, recordings, speakers
---

# PROMAT Research Pages: Recordings und Speakers

## Zweck

Dieses Dokument beschreibt den aktuell gültigen Stand der PROMAT-Forschungsseiten `recordings`, `speakers`, Profilseite und Player-Stub für den spanischen Dev-Stand. Es ersetzt ältere, widersprüchliche Zwischenstände.

## Aktive Datenquelle

- Die Research-Webapp liest Sessions direkt aus `data/sessions/spanish/{session_id}/metadata.json`.
- Es gibt aktuell keine separate Research-Metadatentabelle als zweite Laufzeitquelle.
- Mehrere Sessions derselben Person werden über `person_id` zusammengeführt.
- Kanonische IDs sind `person_id = {CORPUS_CODE}-{SPEAKER_MARKER}-{NNNN}` und `session_id = {person_id}-{YYYY}-S{NN}`.

## Recordings

- `recordings` ist der task-basierte Zugang.
- Jede Zeile referenziert explizit Person, Session und Task.
- Die sichtbaren kurzen Task-Namen sind `Wortliste`, `Text` und `Interview`.
- Die längeren Beschreibungstexte sind fest eingefroren:

| Task | Beschreibung |
| --- | --- |
| Wortliste | Isolierte Aussprache über das Vorlesen einer Wortliste. |
| Text | Zusammenhängende Aussprache über das Vorlesen eines Textes oder einer Satzliste. |
| Interview | Halbgeleitete Gesprächssituation mit spontaner Aussprache. |

- Die Ergebnissicht bleibt tabellarisch, kompakt, ruhig und sans-orientiert.
- Die Aktionsspalte ist task-abhängig und benennt direkt die aktuell gewählte Aufzeichnung.
- Verfügbarkeit wird aus den dokumentierten `tasks` der Session abgeleitet.
- Native-Speaker-Sessions bieten keinen Interview-Zugang.
- Profil-Links aus `recordings` fokussieren dieselbe Personenseite optional über `?session={session_id}`.

## Speakers und Profilseite

- `speakers` ist der person-basierte Zugang.
- Es gibt genau eine Karte pro `person_id`, auch wenn diese Person mehrere Sessions hat.
- Filter treffen eine Person dann, wenn mindestens eine ihrer Sessions alle aktiven Filter erfüllt.
- Karten bleiben kompakt und führen entweder ins Profil oder direkt in verfügbare Aufzeichnungen der ausgewählten bzw. gematchten Session.
- Der Footer-Bereich der Karten heißt `Aufzeichnungen`.

### Profilsemantik

- Oben steht ein stabiler Personbereich; darunter folgen alle Sessions dieser Person als eigene Container.
- Jede Session zeigt ihre eigenen Metadaten, Hinweise und direkt darunter ihre verfügbaren Aufzeichnungen.
- Die ausgewählte Session heißt `Ausgewählte Session` und bleibt zusätzlich markiert, ohne andere Sessions auszublenden.
- Das technische Feld `context` bleibt intern, wird aber nicht sichtbar als `baseline` oder `follow_up` ausgegeben.
- `recorded_by` wird sichtbar als `Explorator:in` gezeigt.

### Sprachbiographie für Lernende

Die Lernenden-Profile zeigen in `Sprachbiographie`:

- `Level (Selbsteinschätzung)`
- `L1`
- `L1 der Mutter`
- `L1 des Vaters`
- `Zusätzliche Sprachen`
- `Geschlecht`
- `Geburtsjahr`
- `Aktuelle Region`
- `Region Kindheit`
- `Sprachaufenthalte`

`Sprachaufenthalte` priorisiert detaillierte `exposure_entries`. Sichtbar sind dort pro Eintrag `country`, Dauer, Typ und optionale Notiz. Wenn keine Detaildaten vorliegen, bleibt `stays_in_target_country` die kompakte Fallback-Information.

### Sprachbiographie für Native Speaker

Native-Speaker-Profile zeigen:

- `Person-ID`
- `Ausgewählte Session`
- `Sprechergruppe`
- `Geschlecht`
- `Geburtsjahr`
- `Aufnahmedatum`
- `Aufnahmejahr`
- `Explorator:in`
- `Herkunftsland`
- `Herkunftsregion`
- `Standardvarietät`

Sie zeigen bewusst nicht:

- `L1`
- `L1 der Mutter`
- `L1 des Vaters`
- `Zusätzliche Sprachen`
- `Sprachaufenthalte`
- `Level (Selbsteinschätzung)`

Native Speaker dienen im aktiven UI als Vergleichsprofile für Zielsprachenaussprache und nicht als zweite sprachbiographische Untersuchungsgruppe neben den Lernenden.
Für aktive Vergleichsprofile gilt zusätzlich: genau eine Session pro nativer `person_id`.

## Aktiver Metadatenvertrag

### Person-Ebene

- `person_id`
- `l1`
- `mother_l1`
- `father_l1`
- `additional_languages`
- `gender`
- `birth_year`
- `current_region`
- `childhood_region`
- `origin_country`
- `origin_region`

Das allgemeine Modell kann personbezogene sprachbiographische Felder tragen. In den aktiven Native-Speaker-Vergleichsprofilen und den aktuellen spanischen Dev-Native-Seeds bleiben `l1`, `mother_l1`, `father_l1` und `additional_languages` jedoch ungenutzt.

### Session-Ebene

- `session_id`
- `target_language`
- `speaker_type`
- `level_code`
- `level_self`
- `recording_year`
- `recording_date`
- `context`
- `recorded_by`
- `stays_in_target_country`
- `standard_variety`
- `notes`
- `tasks`
- `files`

### Detaillierte Sprachaufenthalte

- `exposure_entries` ist die strukturierte Session-Liste für Sprachaufenthalte.
- Jeder Eintrag enthält `country`, `duration_months`, `type` und optional `exposure_notes`.
- `stays_in_target_country` bleibt zusätzlich das kompakte Filter- und Summenfeld.

## Sample

- `Sample` bleibt die Proof-Surface für sichtbare Forschungssemantik.
- Änderungen an Task-Texten, Profilbezeichnungen, `Explorator:in`, `Sprachaufenthalte` und der Person-/Session-Struktur müssen dort parallel aktualisiert werden.
- Native-Speaker-Beispiele in `Sample` folgen derselben schlanken Vergleichslogik wie die aktiven Profile und zeigen keine lernendenzentrierte Sprachbiographie.

## Bewusst nicht umgesetzt

- kein echter Player
- kein Doppel-Player
- keine Vergleichslogik
- keine zweite Datenquelle neben den dateibasierten Session-Metadaten
- keine echte XLSX-Importpipeline; die Mapping-Dateien definieren derzeit nur den Vertrag für eine spätere Implementierung mit realen Daten
